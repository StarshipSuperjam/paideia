"""Tests for apply_migration.py — Phase 1 of S-0064 (Issue #18 fix).

Coverage targets per ADR 0055 / S-0064 plan:
- Per-predicate shape rejects (filename, location, contract header, BEGIN, COMMIT, scope_lock)
- Well-formed accept (dry-run path)
- check_already_applied (true / false / connection failure)
- apply_migration_body (success / SQL error / connection failure)
- record_in_schema_migrations (success / DB error)
- main() integration: success path; dry-run; refuse on shape; refuse on already-applied; --force reapply; partial-failure exit 7

Total: ~22 tests. Uses psycopg stub injected via monkeypatch (same pattern
as test_check_target.py test_migration_applied_queries_name_column).

The user's S-0060 directive applies: "test, test, test."
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_migration import (  # noqa: E402
    PostconditionAssertionParseError,
    _migration_name_from_file,
    apply_migration_body,
    check_already_applied,
    main,
    parse_postcondition_assertions,
    record_in_schema_migrations,
    verify_postconditions,
    verify_shape,
)


# ---------------------------------------------------------------------------
# psycopg stub fixtures
#
# Module-level Error classes so multiple _make_psycopg_stub calls in a single
# test all share the same exception types. (Pre-defining outside the helper
# means an exception raised by stub-call-1 is still caught by the wrapper code
# importing the stub at call time.)
# ---------------------------------------------------------------------------


class _StubError(Exception):
    pass


class _StubOperationalError(_StubError):
    pass


def _make_psycopg_stub(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fetchone_return: Any = None,
    execute_raises: Exception | None = None,
    connect_raises: Exception | None = None,
) -> list[tuple[str, tuple[Any, ...]]]:
    """Inject a psycopg stub. Returns the list that captures (sql, params) executes."""
    captured: list[tuple[str, tuple[Any, ...]]] = []

    class _Cur:
        def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> None:
            captured.append((sql, params or ()))
            if execute_raises is not None:
                raise execute_raises

        def fetchone(self) -> Any:
            return fetchone_return

        def __enter__(self) -> _Cur:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    class _Conn:
        def cursor(self) -> _Cur:
            return _Cur()

        def __enter__(self) -> _Conn:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    import importlib.machinery  # noqa: PLC0415

    psycopg_stub = type(sys)("psycopg")
    # __spec__ matters for downstream find_spec() calls (e.g., from
    # _venv_reexec.ensure_venv_python invoked transitively via setup_env's
    # module-level when load_env is lazy-imported by tools that wrap psycopg).
    # Without a spec, find_spec raises ValueError("psycopg.__spec__ is None").
    psycopg_stub.__spec__ = importlib.machinery.ModuleSpec("psycopg", loader=None)
    psycopg_stub.Error = _StubError  # type: ignore[attr-defined]
    psycopg_stub.OperationalError = _StubOperationalError  # type: ignore[attr-defined]
    if connect_raises is not None:

        def _connect(*_: Any, **__: Any) -> _Conn:
            raise connect_raises

        psycopg_stub.connect = _connect  # type: ignore[attr-defined]
    else:
        psycopg_stub.connect = lambda *_args, **_kwargs: _Conn()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "psycopg", psycopg_stub)
    return captured


def _make_well_formed_migration(
    repo: Path, name: str = "0042_seed_test_part1.sql"
) -> Path:
    """Create a well-formed migration file in the canonical directory."""
    migrations_dir = repo / "product" / "seed-graph" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    migration_path = migrations_dir / name
    migration_path.write_text(  # nosec B608  # writing test fixture SQL file content, not building a SQL query
        f"-- Migration: {name.removesuffix('.sql')}\n"
        f"-- Purpose: test\n"
        f"\n"
        f"BEGIN;\n"
        f"\n"
        f"UPDATE settings SET graph_version = 99 WHERE id = 1;\n"
        f"\n"
        f"COMMIT;\n"
    )
    return migration_path


def _make_routine_session_state(
    repo: Path, task_id: str = "P5-06", allowed_paths: list[str] | None = None
) -> None:
    """Create routine-session state files (current.json + auto_target.json)
    so verify_shape's scope-lock branch fires."""
    sess = repo / "engine" / "session"
    sess.mkdir(parents=True, exist_ok=True)
    (sess / "current.json").write_text(
        json.dumps({"id": "S-0064", "task_id": task_id, "status": "in_progress"})
    )
    target_doc = {
        "tasks": [
            {
                "id": task_id,
                "name": "Test task",
                "status": "in_progress",
                "scope_lock": {
                    "allowed_paths": allowed_paths
                    or ["product/seed-graph/migrations/0042_*.sql"]
                },
            }
        ]
    }
    (sess / "auto_target.json").write_text(json.dumps(target_doc))


# ---------------------------------------------------------------------------
# Shape verification
# ---------------------------------------------------------------------------


def test_verify_shape_well_formed_accepts(tmp_path: Path) -> None:
    migration = _make_well_formed_migration(tmp_path)
    ok, reason = verify_shape(migration, tmp_path)
    assert ok, reason
    assert "shape verified" in reason


def test_verify_shape_rejects_when_file_missing(tmp_path: Path) -> None:
    ok, reason = verify_shape(tmp_path / "nonexistent.sql", tmp_path)
    assert not ok
    assert "not found" in reason


def test_verify_shape_rejects_when_filename_pattern_wrong(tmp_path: Path) -> None:
    migration = _make_well_formed_migration(tmp_path, name="bad_name.sql")
    ok, reason = verify_shape(migration, tmp_path)
    assert not ok
    assert "filename does not match" in reason


def test_verify_shape_rejects_when_outside_canonical_dir(tmp_path: Path) -> None:
    bad_path = tmp_path / "0042_seed_test_part1.sql"
    bad_path.write_text("-- Migration: x\nBEGIN;\nCOMMIT;\n")
    ok, reason = verify_shape(bad_path, tmp_path)
    assert not ok
    assert "not under" in reason


def test_verify_shape_rejects_when_no_contract_header(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "product" / "seed-graph" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    migration = migrations_dir / "0042_seed_test_part1.sql"
    migration.write_text("BEGIN;\nCOMMIT;\n")
    ok, reason = verify_shape(migration, tmp_path)
    assert not ok
    assert "contract header" in reason


def test_verify_shape_rejects_when_no_begin(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "product" / "seed-graph" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    migration = migrations_dir / "0042_seed_test_part1.sql"
    migration.write_text("-- Migration: x\nCOMMIT;\n")
    ok, reason = verify_shape(migration, tmp_path)
    assert not ok
    assert "BEGIN" in reason


def test_verify_shape_rejects_when_no_commit(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "product" / "seed-graph" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    migration = migrations_dir / "0042_seed_test_part1.sql"
    migration.write_text("-- Migration: x\nBEGIN;\n")
    ok, reason = verify_shape(migration, tmp_path)
    assert not ok
    assert "COMMIT" in reason


def test_verify_shape_rejects_when_outside_scope_lock(tmp_path: Path) -> None:
    migration = _make_well_formed_migration(tmp_path, name="0099_seed_other_part1.sql")
    _make_routine_session_state(
        tmp_path,
        task_id="P5-06",
        allowed_paths=["product/seed-graph/migrations/0042_*.sql"],
    )
    ok, reason = verify_shape(migration, tmp_path)
    assert not ok
    assert "outside active task" in reason
    assert "P5-06" in reason


def test_verify_shape_accepts_within_scope_lock(tmp_path: Path) -> None:
    migration = _make_well_formed_migration(tmp_path)
    _make_routine_session_state(
        tmp_path,
        task_id="P5-06",
        allowed_paths=["product/seed-graph/migrations/0042_*.sql"],
    )
    ok, reason = verify_shape(migration, tmp_path)
    assert ok, reason


def test_verify_shape_skips_scope_check_when_no_current_json(tmp_path: Path) -> None:
    """Interactive use (no routine session active) skips the scope check."""
    migration = _make_well_formed_migration(tmp_path)
    # No engine/session/current.json → interactive mode
    ok, reason = verify_shape(migration, tmp_path)
    assert ok, reason


# ---------------------------------------------------------------------------
# check_already_applied
# ---------------------------------------------------------------------------


def test_check_already_applied_true_when_row_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_psycopg_stub(monkeypatch, fetchone_return=(1,))
    applied, detail = check_already_applied("postgresql://stub", "0042_test")
    assert applied is True
    assert "already" in detail
    assert len(captured) == 1
    sql, params = captured[0]
    assert "name = %s" in sql
    assert params == ("0042_test",)


def test_check_already_applied_false_when_no_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub(monkeypatch, fetchone_return=None)
    applied, detail = check_already_applied("postgresql://stub", "0042_test")
    assert applied is False
    assert "not yet" in detail


def test_check_already_applied_returns_none_on_connection_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub(
        monkeypatch,
        connect_raises=_StubOperationalError("could not connect"),
    )
    applied, detail = check_already_applied("postgresql://stub", "0042_test")
    assert applied is None
    assert "connection failed" in detail


# ---------------------------------------------------------------------------
# apply_migration_body
# ---------------------------------------------------------------------------


def test_apply_migration_body_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _make_psycopg_stub(monkeypatch)
    ok, reason = apply_migration_body(
        "postgresql://stub", "BEGIN; INSERT INTO x VALUES (1); COMMIT;"
    )
    assert ok, reason
    assert len(captured) == 1
    assert "INSERT INTO x VALUES (1)" in captured[0][0]


def test_apply_migration_body_sql_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _make_psycopg_stub(
        monkeypatch,
        execute_raises=_StubError("syntax error at or near"),
    )
    ok, reason = apply_migration_body("postgresql://stub", "BAD SQL;")
    assert not ok
    assert "DB error during apply" in reason


def test_apply_migration_body_connection_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub(
        monkeypatch,
        connect_raises=_StubOperationalError("network unreachable"),
    )
    ok, reason = apply_migration_body("postgresql://stub", "BEGIN; COMMIT;")
    assert not ok
    assert "connection failed" in reason


# ---------------------------------------------------------------------------
# record_in_schema_migrations
# ---------------------------------------------------------------------------


def test_record_in_schema_migrations_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_psycopg_stub(monkeypatch)
    ok, reason = record_in_schema_migrations(
        "postgresql://stub", "0042_test", "BEGIN; ... COMMIT;"
    )
    assert ok, reason
    assert "version=" in reason
    assert len(captured) == 1
    sql, params = captured[0]
    assert "INSERT INTO supabase_migrations.schema_migrations" in sql
    assert params[1] == "0042_test"  # name
    assert isinstance(params[0], str) and len(params[0]) == 14  # version YYYYMMDDHHMMSS
    assert params[2] == ["BEGIN; ... COMMIT;"]  # statements as list


def test_record_in_schema_migrations_db_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub(
        monkeypatch,
        execute_raises=_StubError("unique violation"),
    )
    ok, reason = record_in_schema_migrations(
        "postgresql://stub", "0042_test", "BEGIN; ... COMMIT;"
    )
    assert not ok
    assert "INSERT failed" in reason


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def test_main_dry_run_verifies_but_does_not_connect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    migration = _make_well_formed_migration(tmp_path)
    rc = main(
        ["--migration-file", str(migration), "--repo-root", str(tmp_path), "--dry-run"]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert "dry-run" in captured.err
    assert "shape verified" in captured.err


def test_main_returns_2_on_shape_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad_path = tmp_path / "bad.sql"
    bad_path.write_text("not a migration\n")
    rc = main(
        ["--migration-file", str(bad_path), "--repo-root", str(tmp_path), "--dry-run"]
    )
    assert rc == 2
    captured = capsys.readouterr()
    assert "REFUSED" in captured.err


def test_main_returns_4_when_db_url_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """When _resolve_db_url returns None (env var unset and no .env), main exits 4."""
    migration = _make_well_formed_migration(tmp_path)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import apply_migration  # noqa: PLC0415

    monkeypatch.setattr(apply_migration, "_resolve_db_url", lambda _repo: None)
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 4
    captured = capsys.readouterr()
    assert "SUPABASE_DB_URL" in captured.err


def test_main_returns_6_when_already_applied_and_no_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    migration = _make_well_formed_migration(tmp_path)
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    _make_psycopg_stub(monkeypatch, fetchone_return=(1,))
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 6
    captured = capsys.readouterr()
    assert "already" in captured.err
    assert "--force" in captured.err


def test_main_full_success_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifies shape, sees no prior application, applies body, records, exits 0."""
    migration = _make_well_formed_migration(tmp_path)
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    captured_sql = _make_psycopg_stub(monkeypatch, fetchone_return=None)
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr()
    assert "applied" in out.err
    assert "cleanly" in out.err
    # 3 SQL statements: SELECT (already-applied check), the migration body, the schema_migrations INSERT.
    assert len(captured_sql) == 3
    # First is the already-applied check
    assert "schema_migrations" in captured_sql[0][0]
    assert "name = %s" in captured_sql[0][0]
    # Last is the schema_migrations INSERT
    assert "INSERT INTO supabase_migrations.schema_migrations" in captured_sql[2][0]


def test_migration_name_from_file_strips_extension() -> None:
    p = Path("/x/y/0042_seed_test_part1.sql")
    assert _migration_name_from_file(p) == "0042_seed_test_part1"


# ---------------------------------------------------------------------------
# Layer 2.5 — Postcondition assertion parser + verifier (S-0094 / Issue #23)
# ---------------------------------------------------------------------------


def _make_psycopg_stub_with_fetchone_seq(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fetchone_returns: list[Any],
    execute_raises_on_index: dict[int, Exception] | None = None,
) -> list[tuple[str, tuple[Any, ...]]]:
    """Stub variant where fetchone returns a different value per call.

    Each cur.execute() advances the index; cur.fetchone() returns the
    next item from `fetchone_returns`. If the index runs past the list,
    fetchone returns None. Optional per-index execute_raises injects an
    exception on the Nth execute() (0-based), useful for SQL-error tests.
    """
    captured: list[tuple[str, tuple[Any, ...]]] = []
    state = {"idx": 0}
    raises = execute_raises_on_index or {}

    class _Cur:
        def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> None:
            captured.append((sql, params or ()))
            current = state["idx"]
            if current in raises:
                state["idx"] = current + 1
                raise raises[current]
            state["idx"] = current + 1

        def fetchone(self) -> Any:
            # fetchone() reads the value associated with the most-recent
            # execute(). state["idx"] has already advanced, so look back one.
            i = state["idx"] - 1
            if 0 <= i < len(fetchone_returns):
                return fetchone_returns[i]
            return None

        def __enter__(self) -> _Cur:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    class _Conn:
        def cursor(self) -> _Cur:
            return _Cur()

        def __enter__(self) -> _Conn:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    import importlib.machinery  # noqa: PLC0415

    psycopg_stub = type(sys)("psycopg")
    psycopg_stub.__spec__ = importlib.machinery.ModuleSpec("psycopg", loader=None)
    psycopg_stub.Error = _StubError  # type: ignore[attr-defined]
    psycopg_stub.OperationalError = _StubOperationalError  # type: ignore[attr-defined]
    psycopg_stub.connect = lambda *_args, **_kwargs: _Conn()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "psycopg", psycopg_stub)
    return captured


def _make_well_formed_migration_with_assertions(
    repo: Path,
    name: str = "0042_seed_test_part1.sql",
    assertion_lines: list[str] | None = None,
) -> Path:
    """Create a well-formed migration with a Postcondition-Assertions block."""
    migrations_dir = repo / "product" / "seed-graph" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    migration_path = migrations_dir / name
    if assertion_lines is None:
        assertion_lines = ["SELECT 1 :: 1", "SELECT 2 :: 2"]
    block = "\n".join(f"--   {line}" for line in assertion_lines)
    migration_path.write_text(  # nosec B608  # writing test fixture SQL file content, not building a SQL query
        f"-- Migration: {name.removesuffix('.sql')}\n"
        f"-- Purpose: test\n"
        f"-- Postconditions:\n"
        f"--   * graph_version = 99 after apply.\n"
        f"-- Postcondition-Assertions:\n"
        f"{block}\n"
        f"\n"
        f"BEGIN;\n"
        f"\n"
        f"UPDATE settings SET graph_version = 99 WHERE id = 1;\n"
        f"\n"
        f"COMMIT;\n"
    )
    return migration_path


# ---- parser tests --------------------------------------------------------


def test_parse_assertions_returns_none_when_header_absent() -> None:
    sql = (
        "-- Migration: foo\n"
        "-- Postconditions:\n"
        "--   * graph_version = 99\n"
        "BEGIN;\n"
        "UPDATE settings SET graph_version = 99 WHERE id = 1;\n"
        "COMMIT;\n"
    )
    assert parse_postcondition_assertions(sql) is None


def test_parse_assertions_returns_empty_list_when_block_has_no_double_colon() -> None:
    sql = (
        "-- Migration: foo\n"
        "-- Postcondition-Assertions:\n"
        "--   (no assertions yet)\n"
        "BEGIN;\nCOMMIT;\n"
    )
    assert parse_postcondition_assertions(sql) == []


def test_parse_assertions_well_formed_returns_tuples() -> None:
    sql = (
        "-- Postcondition-Assertions:\n"
        "--   SELECT count(*) FROM nodes WHERE graph_version_added=2 :: 28\n"
        "--   SELECT count(*) FROM edges WHERE graph_version_added=2 :: 34\n"
        "--   SELECT graph_version FROM settings :: 2\n"
        "BEGIN;\nCOMMIT;\n"
    )
    result = parse_postcondition_assertions(sql)
    assert result == [
        ("SELECT count(*) FROM nodes WHERE graph_version_added=2", 28),
        ("SELECT count(*) FROM edges WHERE graph_version_added=2", 34),
        ("SELECT graph_version FROM settings", 2),
    ]


def test_parse_assertions_skips_prose_lines_inside_block() -> None:
    sql = (
        "-- Postcondition-Assertions:\n"
        "--   (the next assertion checks the node count)\n"
        "--   SELECT count(*) FROM nodes :: 28\n"
        "--   (and the next checks edges)\n"
        "--   SELECT count(*) FROM edges :: 34\n"
        "BEGIN;\nCOMMIT;\n"
    )
    result = parse_postcondition_assertions(sql)
    assert result == [
        ("SELECT count(*) FROM nodes", 28),
        ("SELECT count(*) FROM edges", 34),
    ]


def test_parse_assertions_block_terminates_at_first_non_dash_line() -> None:
    sql = (
        "-- Postcondition-Assertions:\n"
        "--   SELECT 1 :: 1\n"
        "\n"
        "BEGIN;\n"
        "--   SELECT 999 :: 999\n"
        "COMMIT;\n"
    )
    result = parse_postcondition_assertions(sql)
    # Empty line continues per impl; the BEGIN; (non-dash) terminates.
    # The line below BEGIN; is inside the body and not parsed as an assertion.
    assert result == [("SELECT 1", 1)]


def test_parse_assertions_block_terminates_at_next_section_header() -> None:
    """Real-world contract blocks have multiple `-- <Header>:` sections.
    The parser must stop at the next section to avoid consuming `::`
    that appears in subsequent prose (e.g., PostgreSQL casts in
    Invariants/Rollback sections like `'15'::jsonb`)."""
    sql = (
        "-- Postcondition-Assertions:\n"
        "--   SELECT count(*) FROM nodes :: 28\n"
        "-- Invariants:\n"
        "--   * graph_version = '15'::jsonb after the legacy COMMIT\n"
        "--   * SELECT 999 :: 999  (this is prose, not an assertion)\n"
        "-- Rollback:\n"
        "--   UPDATE settings SET graph_version = '15'::jsonb;\n"
        "BEGIN;\nCOMMIT;\n"
    )
    result = parse_postcondition_assertions(sql)
    assert result == [("SELECT count(*) FROM nodes", 28)]


def test_parse_assertions_rejects_non_integer_expected_value() -> None:
    sql = (
        "-- Postcondition-Assertions:\n"
        "--   SELECT 'foo' :: not_an_integer\n"
        "BEGIN;\nCOMMIT;\n"
    )
    with pytest.raises(PostconditionAssertionParseError, match="not an integer"):
        parse_postcondition_assertions(sql)


def test_parse_assertions_rejects_empty_select_before_separator() -> None:
    sql = "-- Postcondition-Assertions:\n--   :: 28\nBEGIN;\nCOMMIT;\n"
    with pytest.raises(PostconditionAssertionParseError, match="empty SELECT"):
        parse_postcondition_assertions(sql)


# ---- verifier tests ------------------------------------------------------


def test_verify_postconditions_empty_list_returns_true_no_db() -> None:
    # Empty assertions skips the DB connect entirely.
    ok, failures = verify_postconditions("postgresql://stub", [])
    assert ok is True
    assert failures == []


def test_verify_postconditions_all_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[(28,), (34,), (2,)]
    )
    assertions = [
        ("SELECT count(*) FROM nodes", 28),
        ("SELECT count(*) FROM edges", 34),
        ("SELECT graph_version FROM settings", 2),
    ]
    ok, failures = verify_postconditions("postgresql://stub", assertions)
    assert ok is True
    assert failures == []


def test_verify_postconditions_one_fails_returns_failure_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[(28,), (33,), (2,)]
    )
    assertions = [
        ("SELECT count(*) FROM nodes", 28),
        ("SELECT count(*) FROM edges", 34),
        ("SELECT graph_version FROM settings", 2),
    ]
    ok, failures = verify_postconditions("postgresql://stub", assertions)
    assert ok is False
    assert len(failures) == 1
    assert "actual=33" in failures[0]
    assert "expected=34" in failures[0]


def test_verify_postconditions_multiple_failures_all_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[(27,), (33,), (1,)]
    )
    assertions = [
        ("SELECT count(*) FROM nodes", 28),
        ("SELECT count(*) FROM edges", 34),
        ("SELECT graph_version FROM settings", 2),
    ]
    ok, failures = verify_postconditions("postgresql://stub", assertions)
    assert ok is False
    assert len(failures) == 3
    assert any("actual=27" in f for f in failures)
    assert any("actual=33" in f for f in failures)
    assert any("actual=1" in f for f in failures)


def test_verify_postconditions_zero_rows_treated_as_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(monkeypatch, fetchone_returns=[None])
    ok, failures = verify_postconditions(
        "postgresql://stub", [("SELECT count(*) FROM empty_table", 5)]
    )
    assert ok is False
    assert "zero rows" in failures[0]


def test_verify_postconditions_non_integer_value_treated_as_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[("not_an_int",)]
    )
    ok, failures = verify_postconditions(
        "postgresql://stub", [("SELECT label FROM nodes WHERE id='x'", 5)]
    )
    assert ok is False
    assert "non-integer" in failures[0]


def test_verify_postconditions_sql_error_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch,
        fetchone_returns=[],
        execute_raises_on_index={0: _StubError("syntax error at 'SELEC'")},
    )
    with pytest.raises(_StubError, match="syntax error"):
        verify_postconditions(
            "postgresql://stub",
            [("SELEC count(*) FROM nodes", 28)],  # typo
        )


def test_verify_postconditions_connection_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _make_psycopg_stub(
        monkeypatch, connect_raises=_StubOperationalError("connection refused")
    )
    with pytest.raises(_StubOperationalError, match="connection refused"):
        verify_postconditions("postgresql://stub", [("SELECT count(*) FROM nodes", 28)])


# ---- main() integration tests -------------------------------------------


def test_main_warns_when_no_assertions_block_and_returns_0(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Migration without -- Postcondition-Assertions: header → soft-warn + exit 0."""
    migration = _make_well_formed_migration(tmp_path)  # no assertions block
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    _make_psycopg_stub(monkeypatch, fetchone_return=None)
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "no '-- Postcondition-Assertions:' block" in captured.err
    assert "applied" in captured.err
    assert "cleanly" in captured.err


def test_main_assertions_pass_full_success_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Full success: shape OK → not yet applied → body apply → record →
    Layer 2.5 verify (passes) → exit 0."""
    migration = _make_well_formed_migration_with_assertions(
        tmp_path,
        assertion_lines=[
            "SELECT count(*) FROM nodes :: 28",
            "SELECT graph_version FROM settings :: 2",
        ],
    )
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    # SQL call sequence:
    #   0: SELECT 1 FROM schema_migrations (already-applied check) → None
    #   1: migration body (no fetchone needed)
    #   2: INSERT INTO schema_migrations (no fetchone needed)
    #   3: assertion 1 → (28,)
    #   4: assertion 2 → (2,)
    captured_sql = _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[None, None, None, (28,), (2,)]
    )
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr()
    assert "postconditions verified" in out.err
    assert "2 assertion(s) passed" in out.err
    assert "applied" in out.err
    assert "cleanly" in out.err
    # 5 SQL calls: already-applied check + body + INSERT + 2 assertions.
    assert len(captured_sql) == 5
    assert "INSERT INTO supabase_migrations.schema_migrations" in captured_sql[2][0]
    assert "FROM nodes" in captured_sql[3][0]
    assert "FROM settings" in captured_sql[4][0]


def test_main_assertions_fail_returns_8_and_records_in_schema_migrations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One assertion fails → schema_migrations IS recorded, exit 8."""
    migration = _make_well_formed_migration_with_assertions(
        tmp_path,
        assertion_lines=[
            "SELECT count(*) FROM nodes :: 28",
            "SELECT graph_version FROM settings :: 2",
        ],
    )
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    # Same call sequence as the pass test, but assertion 1 returns 27 (off by 1).
    captured_sql = _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[None, None, None, (27,), (2,)]
    )
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 8
    out = capsys.readouterr()
    assert "POSTCONDITION FAILURE" in out.err
    assert "actual=27" in out.err
    assert "expected=28" in out.err
    assert "MANUAL ADJUDICATION" in out.err
    # Critical: schema_migrations was still recorded (call index 2).
    assert "INSERT INTO supabase_migrations.schema_migrations" in captured_sql[2][0]


def test_main_multiple_assertion_failures_all_listed_in_stderr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    migration = _make_well_formed_migration_with_assertions(
        tmp_path,
        assertion_lines=[
            "SELECT count(*) FROM nodes :: 28",
            "SELECT count(*) FROM edges :: 34",
            "SELECT graph_version FROM settings :: 2",
        ],
    )
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch, fetchone_returns=[None, None, None, (27,), (33,), (1,)]
    )
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 8
    out = capsys.readouterr()
    assert "actual=27" in out.err
    assert "actual=33" in out.err
    assert "actual=1" in out.err
    assert "3 assertion(s) failed" in out.err


def test_main_returns_3_when_assertion_query_raises_sql_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Malformed SELECT in the assertions block → exit 3 (author error)."""
    migration = _make_well_formed_migration_with_assertions(
        tmp_path,
        assertion_lines=["SELEC count(*) FROM nodes :: 28"],  # typo
    )
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    # Indices 0/1/2 = check, body, INSERT (succeed); index 3 = assertion
    # (raises). The body and INSERT succeed first; the error fires on the
    # 4th execute() call (index 3) — the assertion query.
    _make_psycopg_stub_with_fetchone_seq(
        monkeypatch,
        fetchone_returns=[None, None, None, None],
        execute_raises_on_index={3: _StubError("syntax error at 'SELEC'")},
    )
    rc = main(["--migration-file", str(migration), "--repo-root", str(tmp_path)])
    assert rc == 3
    out = capsys.readouterr()
    assert "POSTCONDITION VERIFICATION ERROR" in out.err
    assert "_StubError" in out.err


def test_main_rejects_malformed_assertions_block_at_shape_time(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Non-integer expected value is caught at verify_shape (exit 2)."""
    migration = _make_well_formed_migration_with_assertions(
        tmp_path, assertion_lines=["SELECT 1 :: not_a_number"]
    )
    rc = main(
        ["--migration-file", str(migration), "--repo-root", str(tmp_path), "--dry-run"]
    )
    assert rc == 2
    captured = capsys.readouterr()
    assert "REFUSED" in captured.err
    assert "not an integer" in captured.err


def test_main_assertions_block_under_routine_scope_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Confirms scope_lock unaffected by assertions block — the migration
    file still falls under the active task's allowed_paths regardless of
    assertion content (assertions live in the same file as the body)."""
    migration = _make_well_formed_migration_with_assertions(tmp_path)
    _make_routine_session_state(
        tmp_path, allowed_paths=["product/seed-graph/migrations/0042_*.sql"]
    )
    rc = main(
        ["--migration-file", str(migration), "--repo-root", str(tmp_path), "--dry-run"]
    )
    assert rc == 0
    out = capsys.readouterr()
    assert "shape verified" in out.err


# ---------------------------------------------------------------------------
# TCP keepalive kwargs (S-0208, Issue #151 re-scope)
# ---------------------------------------------------------------------------
#
# Server-side Supabase logs were clean across the #151 wedge window; the
# symptom is consistent with a client-side stale socket between
# cur.execute() returning and cur.fetchall() completing on a connection
# the server silently dropped. The fix is TCP keepalive on every
# psycopg.connect call so the kernel surfaces dead-socket errors within
# ~60s instead of blocking poll() forever. These tests verify every
# connect site in this module passes the four kwargs.


def _make_keepalive_capturing_stub(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fetchone_return: Any = None,
) -> list[dict[str, Any]]:
    """Inject a psycopg stub that captures connect() kwargs for assertion."""
    captured_kwargs: list[dict[str, Any]] = []

    class _Cur:
        def execute(self, _sql: str, _params: tuple[Any, ...] | None = None) -> None:
            pass

        def fetchone(self) -> Any:
            return fetchone_return

        def __enter__(self) -> _Cur:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    class _Conn:
        def cursor(self) -> _Cur:
            return _Cur()

        def __enter__(self) -> _Conn:
            return self

        def __exit__(self, *_: Any) -> None:
            pass

    import importlib.machinery  # noqa: PLC0415

    psycopg_stub = type(sys)("psycopg")
    psycopg_stub.__spec__ = importlib.machinery.ModuleSpec("psycopg", loader=None)
    psycopg_stub.Error = _StubError  # type: ignore[attr-defined]
    psycopg_stub.OperationalError = _StubOperationalError  # type: ignore[attr-defined]

    def _connect(*_args: Any, **kwargs: Any) -> _Conn:
        captured_kwargs.append(kwargs)
        return _Conn()

    psycopg_stub.connect = _connect  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "psycopg", psycopg_stub)
    return captured_kwargs


def _assert_keepalive_kwargs_present(kwargs: dict[str, Any]) -> None:
    """All four TCP keepalive params must be set on every psycopg.connect."""
    assert kwargs.get("keepalives") == 1, (
        "keepalives=1 must be set; without it the OS does not probe idle "
        "connections and a silent server-side drop wedges Python"
    )
    assert kwargs.get("keepalives_idle") == 30
    assert kwargs.get("keepalives_interval") == 10
    assert kwargs.get("keepalives_count") == 3


def test_check_already_applied_passes_keepalive_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_keepalive_capturing_stub(monkeypatch, fetchone_return=None)
    check_already_applied("postgresql://stub", "0042_test")
    assert len(captured) == 1
    _assert_keepalive_kwargs_present(captured[0])


def test_apply_migration_body_passes_keepalive_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_keepalive_capturing_stub(monkeypatch)
    apply_migration_body("postgresql://stub", "BEGIN; COMMIT;")
    assert len(captured) == 1
    _assert_keepalive_kwargs_present(captured[0])


def test_record_in_schema_migrations_passes_keepalive_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_keepalive_capturing_stub(monkeypatch)
    record_in_schema_migrations("postgresql://stub", "0042_test", "BEGIN; COMMIT;")
    assert len(captured) == 1
    _assert_keepalive_kwargs_present(captured[0])


def test_verify_postconditions_passes_keepalive_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _make_keepalive_capturing_stub(monkeypatch, fetchone_return=(0,))
    verify_postconditions("postgresql://stub", [("SELECT 0", 0)])
    assert len(captured) == 1
    _assert_keepalive_kwargs_present(captured[0])
