"""Tests for engine/tools/validate.py.

Test contract — what this suite covers and does not cover.

The suite covers each public surface of validate.py with at least one test
per public function and one test per logical branch within each function.
Coverage targets the hard-fail and soft-warn paths explicitly named in
validate_repo_structure's category list, plus all gate paths in
validate_code_gates, plus the helpers (session_id_from_current,
append_history) and the CLI entry point (main).

Test isolation strategy:

- Filesystem isolation via pytest's tmp_path and monkeypatch fixtures.
  Tests that exercise file-reading branches construct synthetic repo
  trees in a tmp_path and patch validate.REPO_ROOT (and derived path
  constants) to point there. The patches restore via monkeypatch's
  automatic teardown.
- Subprocess isolation for validate_code_gates: tests use real
  subprocess calls against minimal Python files in tmp_path. The tools
  themselves (ruff, mypy, pytest) are exercised; subprocess.run is not
  mocked because the gate-tool integration is part of what the contract
  guarantees.

Non-responsibilities:

- Does not test ruff, mypy, or pytest themselves. Each gate's behavior
  is bounded by what the upstream tool produces; the suite verifies the
  gate function's wiring (subprocess invoked, output captured, exit code
  mapped to hard_fail).
- Does not test the JSONL telemetry format beyond round-trip writability.
  ADR 0022 health-check tests own format-stability concerns when authored.
- Does not test the pre-commit hook integration. That layer is shell-side
  and tested by manual invocation in development.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add the engine/tools/ directory to sys.path so we can import validate
# as a module. Tests run via `pytest engine/tools/test_validate.py` from
# the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402
from validate import (  # noqa: E402
    ValidationResult,
    append_history,
    main,
    session_id_from_current,
    validate_code_gates,
    validate_graph,
    validate_repo_structure,
    validate_sql_gates,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal valid synthetic repo tree and patch validate's paths.

    Returns the synthetic repo's root path. Has the bare structure needed
    for validate_repo_structure to run with no hard-fails: top-level files,
    engine/ subtree with STATE.md, ENGINE_LOG.md, session/register_state.json,
    plus engine/adr/, engine/operations/, product/docs/, product/adr/. Tests
    can override individual files to exercise specific failure paths.

    The fixture patches validate.REPO_ROOT and the four derived path
    constants (HISTORY_FILE, ENGINE_ADR_DIR, PRODUCT_ADR_DIR) to point at
    tmp_path.
    """
    for name in validate.REQUIRED_TOP_LEVEL:
        (tmp_path / name).write_text(f"# {name}\n")

    (tmp_path / "engine").mkdir()
    (tmp_path / "engine" / "STATE.md").write_text(
        "# Project State\n\n## Current\n\n| Current phase | Phase 0 |\n"
    )
    (tmp_path / "engine" / "ENGINE_LOG.md").write_text(
        "# ENGINE_LOG\n\n## [Unreleased]\n"
    )

    (tmp_path / "engine" / "session").mkdir()
    (tmp_path / "engine" / "session" / "register_state.json").write_text(
        json.dumps(
            {
                "next_id": "0001",
                "last_claimed": "S-0000",
                "current_status": "closed",
            }
        )
    )

    (tmp_path / "engine" / "adr").mkdir()
    (tmp_path / "engine" / "adr" / "README.md").write_text(
        "# Engine ADRs\n\n## Index\n\n| ADR | Title | Status |\n|---|---|---|\n"
    )

    (tmp_path / "engine" / "operations").mkdir()
    (tmp_path / "engine" / "operations" / "README.md").write_text(
        "# engine/operations/\n"
    )

    (tmp_path / "product").mkdir()
    (tmp_path / "product" / "docs").mkdir()
    (tmp_path / "product" / "docs" / "MISSION.md").write_text("# Mission\n")
    (tmp_path / "product" / "docs" / "CROSS_REFERENCES.md").write_text(
        "# Cross-references\n"
    )
    (tmp_path / "product" / "adr").mkdir()
    (tmp_path / "product" / "adr" / "README.md").write_text(
        "# Product ADRs\n\n## Index\n\n| ADR | Title | Status |\n|---|---|---|\n"
    )

    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(validate, "ENGINE_ADR_DIR", tmp_path / "engine" / "adr")
    monkeypatch.setattr(validate, "PRODUCT_ADR_DIR", tmp_path / "product" / "adr")
    monkeypatch.setattr(
        validate,
        "HISTORY_FILE",
        tmp_path / "engine" / "tools" / "validate-history.jsonl",
    )

    return tmp_path


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


class TestValidationResult:
    """ValidationResult accumulator: per-method behavior and merge semantics."""

    def test_empty_init(self) -> None:
        """Default fields are empty containers."""
        r = ValidationResult()
        assert r.checks_run == []
        assert r.hard_fails == []
        assert r.soft_warns == {}

    def test_add_check_appends_in_order_with_duplicates(self) -> None:
        """add_check is append-only and records duplicates per contract."""
        r = ValidationResult()
        r.add_check("a")
        r.add_check("b")
        r.add_check("a")
        assert r.checks_run == ["a", "b", "a"]

    def test_hard_fail_appends(self) -> None:
        """hard_fail accumulates messages for single-pass blocker reporting."""
        r = ValidationResult()
        r.hard_fail("first")
        r.hard_fail("second")
        assert r.hard_fails == ["first", "second"]

    def test_soft_warn_categorizes_and_groups(self) -> None:
        """soft_warn groups by category preserving message order."""
        r = ValidationResult()
        r.soft_warn("cat1", "msg1")
        r.soft_warn("cat2", "msg2")
        r.soft_warn("cat1", "msg3")
        assert r.soft_warns == {
            "cat1": ["msg1", "msg3"],
            "cat2": ["msg2"],
        }

    def test_merge_combines_all_fields_without_mutating_other(self) -> None:
        """merge concatenates checks/fails and extends soft-warn categories."""
        r1 = ValidationResult()
        r1.add_check("a")
        r1.hard_fail("h1")
        r1.soft_warn("c1", "s1")
        r2 = ValidationResult()
        r2.add_check("b")
        r2.hard_fail("h2")
        r2.soft_warn("c1", "s2")
        r2.soft_warn("c2", "s3")

        r1.merge(r2)
        assert r1.checks_run == ["a", "b"]
        assert r1.hard_fails == ["h1", "h2"]
        assert r1.soft_warns == {"c1": ["s1", "s2"], "c2": ["s3"]}
        assert r2.checks_run == ["b"]
        assert r2.hard_fails == ["h2"]
        assert r2.soft_warns == {"c1": ["s2"], "c2": ["s3"]}


# ---------------------------------------------------------------------------
# validate_repo_structure
# ---------------------------------------------------------------------------


class TestValidateRepoStructure:
    """validate_repo_structure: each check category, hard- and soft-warn paths."""

    def test_clean_synthetic_repo_no_hard_fails(self, synthetic_repo: Path) -> None:
        """A minimal valid synthetic repo produces no hard-fails."""
        r = validate_repo_structure()
        assert r.hard_fails == [], f"unexpected hard-fails: {r.hard_fails}"

    def test_missing_top_level_hard_fails(self, synthetic_repo: Path) -> None:
        """Removing a required top-level file produces a top_level_required fail."""
        (synthetic_repo / "README.md").unlink()
        r = validate_repo_structure()
        assert any("README.md" in m for m in r.hard_fails)

    def test_missing_engine_required_hard_fails(self, synthetic_repo: Path) -> None:
        """Removing an engine-required file produces an engine_required fail."""
        (synthetic_repo / "engine" / "STATE.md").unlink()
        r = validate_repo_structure()
        assert any("engine/STATE.md" in m for m in r.hard_fails)

    def test_missing_register_hard_fails(self, synthetic_repo: Path) -> None:
        """Missing register_state.json hard-fails."""
        (synthetic_repo / "engine" / "session" / "register_state.json").unlink()
        r = validate_repo_structure()
        assert any("register_state.json" in m for m in r.hard_fails)

    def test_register_missing_key_hard_fails(self, synthetic_repo: Path) -> None:
        """register_state.json missing a required key hard-fails."""
        (synthetic_repo / "engine" / "session" / "register_state.json").write_text(
            json.dumps({"next_id": "0001"})
        )
        r = validate_repo_structure()
        assert any("missing key" in m for m in r.hard_fails)

    def test_register_invalid_json_hard_fails(self, synthetic_repo: Path) -> None:
        """register_state.json with invalid JSON hard-fails."""
        (synthetic_repo / "engine" / "session" / "register_state.json").write_text(
            "{not valid json"
        )
        r = validate_repo_structure()
        assert any("not valid JSON" in m for m in r.hard_fails)

    def test_current_invalid_id_hard_fails(self, synthetic_repo: Path) -> None:
        """current.json with non-S-NNNN id hard-fails."""
        (synthetic_repo / "engine" / "session" / "current.json").write_text(
            json.dumps(
                {
                    "id": "session-1",
                    "started_at": "2026-05-02T00:00:00Z",
                    "status": "in_progress",
                    "working_on": "test",
                }
            )
        )
        r = validate_repo_structure()
        assert any("S-NNNN" in m for m in r.hard_fails)

    def test_current_missing_key_hard_fails(self, synthetic_repo: Path) -> None:
        """current.json missing a required key hard-fails."""
        (synthetic_repo / "engine" / "session" / "current.json").write_text(
            json.dumps({"id": "S-0001"})
        )
        r = validate_repo_structure()
        assert any("missing key" in m for m in r.hard_fails)

    def test_engine_log_missing_unreleased_soft_warns(
        self, synthetic_repo: Path
    ) -> None:
        """ENGINE_LOG without an [Unreleased] section header soft-warns."""
        (synthetic_repo / "engine" / "ENGINE_LOG.md").write_text(
            "# ENGINE_LOG\n\nno header here\n"
        )
        r = validate_repo_structure()
        assert "engine_log_format" in r.soft_warns

    def test_state_missing_current_phase_soft_warns(self, synthetic_repo: Path) -> None:
        """STATE.md without 'Current phase' soft-warns."""
        (synthetic_repo / "engine" / "STATE.md").write_text(
            "# Project State\n\nno phase here\n"
        )
        r = validate_repo_structure()
        assert "state_format" in r.soft_warns

    def test_adr_missing_status_soft_warns(self, synthetic_repo: Path) -> None:
        """An ADR file without a Status field soft-warns."""
        (synthetic_repo / "engine" / "adr" / "0001-test.md").write_text(
            "# ADR 0001\n\nNo status field.\n"
        )
        r = validate_repo_structure()
        assert "adr_missing_status" in r.soft_warns

    def test_adr_index_missing_row_soft_warns(self, synthetic_repo: Path) -> None:
        """An ADR file present but not indexed soft-warns adr_index_inconsistent."""
        (synthetic_repo / "engine" / "adr" / "0001-test.md").write_text(
            "# ADR 0001\n\n- **Status:** Accepted\n"
        )
        r = validate_repo_structure()
        assert "adr_index_inconsistent" in r.soft_warns

    def test_adr_index_status_mismatch_soft_warns(self, synthetic_repo: Path) -> None:
        """An ADR file Status differing from its index status soft-warns."""
        (synthetic_repo / "engine" / "adr" / "0001-test.md").write_text(
            "# ADR 0001\n\n- **Status:** Superseded by 0002\n"
        )
        (synthetic_repo / "engine" / "adr" / "README.md").write_text(
            "# Engine ADRs\n\n## Index\n\n"
            "| ADR | Title | Status |\n|---|---|---|\n"
            "| [0001](0001-test.md) | Test | Accepted |\n"
        )
        r = validate_repo_structure()
        assert "adr_index_inconsistent" in r.soft_warns

    def test_cross_reference_broken_soft_warns(self, synthetic_repo: Path) -> None:
        """A broken markdown link in CROSS_REFERENCES.md soft-warns."""
        (synthetic_repo / "product" / "docs" / "CROSS_REFERENCES.md").write_text(
            "# Cross-references\n\nSee [missing](missing.md).\n"
        )
        r = validate_repo_structure()
        assert "cross_reference_broken" in r.soft_warns

    def test_future_files_missing_soft_warns(self, synthetic_repo: Path) -> None:
        """A file in EXPECTED_FROM_S0002 absent soft-warns expected_future_file_missing."""
        (synthetic_repo / "product" / "docs" / "MISSION.md").unlink()
        r = validate_repo_structure()
        assert "expected_future_file_missing" in r.soft_warns


# ---------------------------------------------------------------------------
# validate_code_gates
# ---------------------------------------------------------------------------


def _write_clean_module(path: Path) -> None:
    """Write a small Python module that passes lint, format, and mypy strict."""
    path.write_text(
        '"""Clean module — minimal contract.\n\n'
        "This module exists for testing the gate stack. It exposes one\n"
        "pure function that adds two integers.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n\n"
        "def add(a: int, b: int) -> int:\n"
        '    """Return ``a + b``."""\n'
        "    return a + b\n"
    )


def _write_clean_test(path: Path, module_dir: Path) -> None:
    """Write a passing pytest test for the clean module."""
    path.write_text(
        '"""Tests for module.py."""\n\n'
        "from __future__ import annotations\n\n"
        "import sys\n"
        f"sys.path.insert(0, {str(module_dir)!r})\n\n"
        "from module import add  # noqa: E402\n\n\n"
        "def test_add() -> None:\n"
        '    """add returns the sum of its arguments."""\n'
        "    assert add(2, 3) == 5\n"
    )


class TestValidateCodeGates:
    """validate_code_gates: subprocess invocation, gate-failure surfacing."""

    def test_empty_files_runs_sentinel_check(self) -> None:
        """An empty file list runs the empty-check sentinel and no gate checks."""
        r = validate_code_gates([])
        assert r.hard_fails == []
        assert "code_gates_empty" in r.checks_run
        for gate in (
            "code_gates_ruff_check",
            "code_gates_ruff_format",
            "code_gates_mypy",
            "code_gates_test_presence",
            "code_gates_pytest",
        ):
            assert gate not in r.checks_run

    def test_clean_file_with_test_passes_all_gates(self, tmp_path: Path) -> None:
        """A clean module with a passing sibling test passes all gates."""
        src = tmp_path / "module.py"
        _write_clean_module(src)
        test = tmp_path / "test_module.py"
        _write_clean_test(test, tmp_path)
        r = validate_code_gates([src])
        assert r.hard_fails == [], f"unexpected fails: {r.hard_fails}"
        for gate in (
            "code_gates_ruff_check",
            "code_gates_ruff_format",
            "code_gates_mypy",
            "code_gates_test_presence",
            "code_gates_pytest",
        ):
            assert gate in r.checks_run

    def test_lint_violation_hard_fails(self, tmp_path: Path) -> None:
        """An unused import (F401) hard-fails ruff_check."""
        src = tmp_path / "module.py"
        src.write_text(
            '"""Module with unused import."""\n\n'
            "from __future__ import annotations\n\n"
            "import json  # unused\n"
        )
        # Provide a sibling test so test_presence does not also fail
        test = tmp_path / "test_module.py"
        test.write_text(
            '"""Tests."""\n\n\n'
            "def test_smoke() -> None:\n"
            '    """Sanity."""\n'
            "    assert True\n"
        )
        r = validate_code_gates([src])
        assert any("ruff check" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_mypy_violation_hard_fails(self, tmp_path: Path) -> None:
        """A type error hard-fails mypy."""
        src = tmp_path / "module.py"
        src.write_text(
            '"""Module with a type error."""\n\n'
            "from __future__ import annotations\n\n\n"
            "def foo() -> int:\n"
            '    """Claims int but returns str."""\n'
            '    return "not an int"\n'
        )
        test = tmp_path / "test_module.py"
        test.write_text(
            '"""Tests."""\n\n\n'
            "def test_smoke() -> None:\n"
            '    """Sanity."""\n'
            "    assert True\n"
        )
        r = validate_code_gates([src])
        assert any("mypy" in f for f in r.hard_fails), f"hard_fails: {r.hard_fails}"

    def test_missing_test_hard_fails(self, tmp_path: Path) -> None:
        """A source file without a sibling/nested test_<name>.py hard-fails."""
        src = tmp_path / "module.py"
        _write_clean_module(src)
        r = validate_code_gates([src])
        assert any("no test file" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_test_file_skips_test_presence(self, tmp_path: Path) -> None:
        """A file named test_X.py is exempt from the test_presence requirement."""
        test = tmp_path / "test_x.py"
        test.write_text(
            '"""Test module."""\n\n'
            "from __future__ import annotations\n\n\n"
            "def test_smoke() -> None:\n"
            '    """Sanity."""\n'
            "    assert True\n"
        )
        r = validate_code_gates([test])
        assert not any("no test file" in f for f in r.hard_fails), (
            f"unexpected hard_fails: {r.hard_fails}"
        )

    def test_nested_test_dir_satisfies_presence(self, tmp_path: Path) -> None:
        """A test under <dir>/tests/test_<name>.py satisfies test_presence."""
        src_dir = tmp_path / "pkg"
        src_dir.mkdir()
        src = src_dir / "module.py"
        _write_clean_module(src)
        tests_dir = src_dir / "tests"
        tests_dir.mkdir()
        test = tests_dir / "test_module.py"
        _write_clean_test(test, src_dir)
        r = validate_code_gates([src])
        assert not any("no test file" in f for f in r.hard_fails), (
            f"unexpected hard_fails: {r.hard_fails}"
        )


# ---------------------------------------------------------------------------
# validate_sql_gates
# ---------------------------------------------------------------------------


# A clean migration that satisfies all four SQL gates: transaction wrap,
# CASCADE on FK to users(id), RLS-enable on the public.* table, and CHECK
# constraint on every enum-modeled column declared.
_CLEAN_MIGRATION = """\
-- Migration: 0001_test
-- Purpose: synthetic clean migration for the gate suite.
BEGIN;

CREATE TABLE public.events (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  CHECK (status IN ('open', 'closed'))
);

ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

COMMIT;
"""


def _write_sql(path: Path, body: str) -> None:
    """Write a synthetic SQL migration file at ``path``."""
    path.write_text(body)


class TestValidateSqlGates:
    """validate_sql_gates: each gate path, plus aggregate behavior."""

    def test_empty_files_runs_sentinel_check(self) -> None:
        """An empty file list runs the empty-check sentinel and no gate checks."""
        r = validate_sql_gates([])
        assert r.hard_fails == []
        assert "sql_gates_empty" in r.checks_run
        for gate in (
            "sql_gates_transaction_wrap",
            "sql_gates_cascade_present",
            "sql_gates_rls_enabled",
            "sql_gates_enum_checks",
        ):
            assert gate not in r.checks_run

    def test_clean_migration_passes_all_gates(self, tmp_path: Path) -> None:
        """A clean migration produces no hard-fails and runs all four gates."""
        path = tmp_path / "0001_test.sql"
        _write_sql(path, _CLEAN_MIGRATION)
        r = validate_sql_gates([path])
        assert r.hard_fails == [], f"unexpected fails: {r.hard_fails}"
        for gate in (
            "sql_gates_transaction_wrap",
            "sql_gates_cascade_present",
            "sql_gates_rls_enabled",
            "sql_gates_enum_checks",
        ):
            assert gate in r.checks_run

    def test_missing_begin_hard_fails(self, tmp_path: Path) -> None:
        """A migration without BEGIN at the start hard-fails the wrap gate."""
        body = _CLEAN_MIGRATION.replace("BEGIN;\n", "", 1)
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("does not start with BEGIN" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_missing_commit_hard_fails(self, tmp_path: Path) -> None:
        """A migration without COMMIT/END at the end hard-fails the wrap gate."""
        body = _CLEAN_MIGRATION.replace("COMMIT;\n", "", 1)
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("does not end with COMMIT" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_end_keyword_satisfies_wrap(self, tmp_path: Path) -> None:
        """A migration ending in END (instead of COMMIT) satisfies the gate."""
        body = _CLEAN_MIGRATION.replace("COMMIT;\n", "END;\n")
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert not any("does not end with COMMIT" in f for f in r.hard_fails), (
            f"unexpected fails: {r.hard_fails}"
        )

    def test_missing_cascade_hard_fails(self, tmp_path: Path) -> None:
        """An FK to users(id) without ON DELETE CASCADE hard-fails."""
        body = _CLEAN_MIGRATION.replace(
            "REFERENCES public.users(id) ON DELETE CASCADE",
            "REFERENCES public.users(id)",
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("without ON DELETE CASCADE" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_cascade_in_unqualified_users_reference(self, tmp_path: Path) -> None:
        """The CASCADE gate matches REFERENCES users(id) without public. prefix."""
        body = _CLEAN_MIGRATION.replace(
            "REFERENCES public.users(id) ON DELETE CASCADE",
            "REFERENCES users(id)",
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("without ON DELETE CASCADE" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_cascade_check_ignores_comments(self, tmp_path: Path) -> None:
        """A REFERENCES users(id) inside a -- comment does not trigger the gate."""
        # The comment-stripping helper removes line comments before checks
        # run, so a comment naming the FK pattern should not produce a fail.
        body = (
            "-- Notes: REFERENCES users(id) is the standard FK shape.\n"
            + _CLEAN_MIGRATION
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert r.hard_fails == [], f"unexpected fails: {r.hard_fails}"

    def test_missing_rls_enable_hard_fails(self, tmp_path: Path) -> None:
        """A public.* CREATE TABLE without ENABLE ROW LEVEL SECURITY hard-fails."""
        body = _CLEAN_MIGRATION.replace(
            "ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;\n", ""
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("ENABLE ROW LEVEL SECURITY" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_unqualified_alter_table_satisfies_rls(self, tmp_path: Path) -> None:
        """ALTER TABLE events (no public. prefix) satisfies the RLS gate."""
        body = _CLEAN_MIGRATION.replace(
            "ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE events ENABLE ROW LEVEL SECURITY;",
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert not any("ENABLE ROW LEVEL SECURITY" in f for f in r.hard_fails), (
            f"unexpected fails: {r.hard_fails}"
        )

    def test_missing_enum_check_hard_fails(self, tmp_path: Path) -> None:
        """A status TEXT column without CHECK constraint hard-fails."""
        body = _CLEAN_MIGRATION.replace(
            "  CHECK (status IN ('open', 'closed'))\n",
            "",
        ).replace(
            "  status TEXT NOT NULL,\n",
            "  status TEXT NOT NULL\n",
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("no CHECK" in f and "status" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_confidence_level_check_required(self, tmp_path: Path) -> None:
        """A confidence_level column requires a CHECK (... IN ...) constraint."""
        body = """\
-- Migration: 0002_nodes
BEGIN;
CREATE TABLE public.nodes (
  id UUID PRIMARY KEY,
  confidence_level TEXT NOT NULL DEFAULT 'INTERPRETED'
);
ALTER TABLE public.nodes ENABLE ROW LEVEL SECURITY;
COMMIT;
"""
        path = tmp_path / "0002_nodes.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert any("confidence_level" in f and "no CHECK" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_confidence_level_with_check_passes(self, tmp_path: Path) -> None:
        """A confidence_level column with a CHECK constraint passes."""
        body = """\
-- Migration: 0002_nodes
BEGIN;
CREATE TABLE public.nodes (
  id UUID PRIMARY KEY,
  confidence_level TEXT NOT NULL DEFAULT 'INTERPRETED'
    CHECK (confidence_level IN ('EXTRACTED', 'INTERPRETED', 'SYNTHETIC'))
);
ALTER TABLE public.nodes ENABLE ROW LEVEL SECURITY;
COMMIT;
"""
        path = tmp_path / "0002_nodes.sql"
        _write_sql(path, body)
        r = validate_sql_gates([path])
        assert r.hard_fails == [], f"unexpected fails: {r.hard_fails}"

    def test_unreadable_file_hard_fails(self, tmp_path: Path) -> None:
        """A path that does not exist hard-fails with read-failure message."""
        bogus = tmp_path / "missing.sql"
        r = validate_sql_gates([bogus])
        assert any("failed to read file" in f for f in r.hard_fails), (
            f"hard_fails: {r.hard_fails}"
        )

    def test_aggregates_across_multiple_files(self, tmp_path: Path) -> None:
        """Per-file failures all surface in a single ValidationResult."""
        # File 1: missing CASCADE
        body1 = _CLEAN_MIGRATION.replace(
            "REFERENCES public.users(id) ON DELETE CASCADE",
            "REFERENCES public.users(id)",
        )
        path1 = tmp_path / "0001_a.sql"
        _write_sql(path1, body1)
        # File 2: missing RLS enable
        body2 = _CLEAN_MIGRATION.replace(
            "ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;\n", ""
        )
        path2 = tmp_path / "0002_b.sql"
        _write_sql(path2, body2)
        r = validate_sql_gates([path1, path2])
        # Both failures surface in one run
        assert any("CASCADE" in f and "0001_a.sql" in f for f in r.hard_fails)
        assert any(
            "ENABLE ROW LEVEL SECURITY" in f and "0002_b.sql" in f for f in r.hard_fails
        )


class TestMainSqlGatesMode:
    """main(): --sql-gates dispatch."""

    def test_sql_gates_clean_returns_zero(self, tmp_path: Path) -> None:
        """--sql-gates against a clean migration exits 0."""
        path = tmp_path / "0001_test.sql"
        _write_sql(path, _CLEAN_MIGRATION)
        rc = main(["--sql-gates", "--files", str(path)])
        assert rc == 0

    def test_sql_gates_no_files_returns_zero(self) -> None:
        """--sql-gates with no --files exits 0 via the empty-check sentinel."""
        rc = main(["--sql-gates"])
        assert rc == 0

    def test_sql_gates_dirty_returns_two(self, tmp_path: Path) -> None:
        """--sql-gates against a migration with hard-fails exits 2."""
        body = _CLEAN_MIGRATION.replace(
            "REFERENCES public.users(id) ON DELETE CASCADE",
            "REFERENCES public.users(id)",
        )
        path = tmp_path / "0001_test.sql"
        _write_sql(path, body)
        rc = main(["--sql-gates", "--files", str(path)])
        assert rc == 2


# ---------------------------------------------------------------------------
# validate_graph (Phase 4 stub)
# ---------------------------------------------------------------------------


def test_validate_graph_returns_stub_result() -> None:
    """validate_graph is a Phase 4 stub: empty result with the stub check name."""
    r = validate_graph()
    assert r.hard_fails == []
    assert r.soft_warns == {}
    assert "graph_audit_stub" in r.checks_run


# ---------------------------------------------------------------------------
# session_id_from_current
# ---------------------------------------------------------------------------


class TestSessionIdFromCurrent:
    """session_id_from_current: sentinel and parsed-id paths."""

    def test_no_current_returns_outside_sentinel(self, synthetic_repo: Path) -> None:
        """No current.json means outside-session."""
        assert session_id_from_current() == "outside-session"

    def test_valid_current_returns_id(self, synthetic_repo: Path) -> None:
        """current.json with id returns the id string."""
        (synthetic_repo / "engine" / "session" / "current.json").write_text(
            json.dumps(
                {
                    "id": "S-0042",
                    "started_at": "x",
                    "status": "x",
                    "working_on": "x",
                }
            )
        )
        assert session_id_from_current() == "S-0042"

    def test_malformed_current_returns_outside(self, synthetic_repo: Path) -> None:
        """Malformed current.json returns the outside-session sentinel."""
        (synthetic_repo / "engine" / "session" / "current.json").write_text("{not json")
        assert session_id_from_current() == "outside-session"


# ---------------------------------------------------------------------------
# append_history
# ---------------------------------------------------------------------------


class TestAppendHistory:
    """append_history: best-effort JSONL writes; never raises."""

    def test_writes_record_as_jsonl(self, synthetic_repo: Path) -> None:
        """Record appears in HISTORY_FILE as a single JSON line."""
        record: dict[str, Any] = {"k": "v", "n": 1}
        append_history(record)
        history_path = synthetic_repo / "engine" / "tools" / "validate-history.jsonl"
        assert history_path.is_file()
        lines = history_path.read_text().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0]) == record

    def test_appends_not_overwrites(self, synthetic_repo: Path) -> None:
        """Two append_history calls produce two lines."""
        append_history({"first": True})
        append_history({"second": True})
        history_path = synthetic_repo / "engine" / "tools" / "validate-history.jsonl"
        assert len(history_path.read_text().splitlines()) == 2

    def test_oserror_swallowed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """OSError during write is swallowed; the function returns cleanly."""
        bogus = tmp_path / "bogus" / "history.jsonl"
        monkeypatch.setattr(validate, "HISTORY_FILE", bogus)

        def boom(*args: Any, **kwargs: Any) -> None:
            raise OSError("simulated failure")

        monkeypatch.setattr(Path, "mkdir", boom)
        # Must not raise
        append_history({"k": "v"})


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    """main(): exit-code mapping and dispatch between the two modes."""

    def test_default_mode_clean_returns_non_two(self, synthetic_repo: Path) -> None:
        """Clean repo, default mode: exit code 0 or 1 (no hard-fails)."""
        rc = main([])
        assert rc != 2

    def test_default_mode_hard_fail_returns_two(self, synthetic_repo: Path) -> None:
        """Removing a required file forces exit 2."""
        (synthetic_repo / "README.md").unlink()
        rc = main([])
        assert rc == 2

    def test_code_gates_mode_clean_returns_zero(self, tmp_path: Path) -> None:
        """--code-gates against a clean file with a passing test exits 0."""
        src = tmp_path / "module.py"
        _write_clean_module(src)
        test = tmp_path / "test_module.py"
        _write_clean_test(test, tmp_path)
        rc = main(["--code-gates", "--files", str(src)])
        assert rc == 0

    def test_code_gates_mode_no_files_returns_zero(self) -> None:
        """--code-gates with no --files exits 0 via the empty-check sentinel."""
        rc = main(["--code-gates"])
        assert rc == 0
