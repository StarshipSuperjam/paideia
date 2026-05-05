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
    _migration_name_from_file,
    apply_migration_body,
    check_already_applied,
    main,
    record_in_schema_migrations,
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
    migration_path.write_text(
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
