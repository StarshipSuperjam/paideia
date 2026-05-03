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
    validate_adr_back_reference_orphan,
    validate_adr_consequences_deliverable_audit,
    validate_code_gates,
    validate_graph,
    validate_repo_structure,
    validate_sql_gates,
    validate_superseded_adr_currency,
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
# validate_graph (Phase 4 implementation per ADR 0016 + gate phase_4_graph_validation.md)
# ---------------------------------------------------------------------------


def _node(
    nid: str,
    *,
    label: str | None = None,
    domain: list[str] | None = None,
    teaching_notes: str | None = None,
    rigor_score_computed: float = 0.5,
    confidence_level: str = "INTERPRETED",
    status: str = "active",
) -> dict[str, Any]:
    """Build a node row dict with the columns validate_graph reads."""
    return {
        "id": nid,
        "label": label if label is not None else nid.replace("_", " ").title(),
        "domain": domain or ["epistemology"],
        "summary": "Summary text.",
        "teaching_notes": teaching_notes,
        "rigor_score_computed": rigor_score_computed,
        "confidence_level": confidence_level,
        "status": status,
    }


def _edge(
    source: str, target: str, *, edge_type: str = "pedagogical_prerequisite"
) -> dict[str, Any]:
    """Build an edge row dict with the columns validate_graph reads."""
    return {"source_id": source, "target_id": target, "edge_type": edge_type}


def test_validate_graph_env_unset_returns_skipped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When neither argument nor env var is set, the audit skips clean."""
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    r = validate_graph()
    assert r.hard_fails == []
    assert r.soft_warns == {}
    assert "graph_audit_skipped" in r.checks_run


class TestDetectDuplicateNodeIds:
    """_detect_duplicate_node_ids: structural duplicate-id check."""

    def test_no_duplicates_returns_empty(self) -> None:
        nodes = [_node("a"), _node("b"), _node("c")]
        assert validate._detect_duplicate_node_ids(nodes) == []

    def test_single_duplicate_pair_returns_id(self) -> None:
        nodes = [_node("a"), _node("b"), _node("a")]
        assert validate._detect_duplicate_node_ids(nodes) == ["a"]

    def test_multiple_duplicates_returns_sorted(self) -> None:
        nodes = [_node("z"), _node("a"), _node("z"), _node("a"), _node("m")]
        assert validate._detect_duplicate_node_ids(nodes) == ["a", "z"]

    def test_none_id_skipped(self) -> None:
        nodes = [{"id": None}, _node("a"), {"id": None}]
        assert validate._detect_duplicate_node_ids(nodes) == []


class TestDetectDanglingEdges:
    """_detect_dangling_edges: source-or-target-not-in-nodes detection."""

    def test_clean_graph_returns_empty(self) -> None:
        nodes = [_node("a"), _node("b")]
        edges = [_edge("a", "b")]
        assert validate._detect_dangling_edges(nodes, edges) == []

    def test_missing_source_returns_source_marker(self) -> None:
        nodes = [_node("b")]
        edges = [_edge("ghost", "b")]
        result = validate._detect_dangling_edges(nodes, edges)
        assert result == [("ghost", "b", "source")]

    def test_missing_target_returns_target_marker(self) -> None:
        nodes = [_node("a")]
        edges = [_edge("a", "ghost")]
        result = validate._detect_dangling_edges(nodes, edges)
        assert result == [("a", "ghost", "target")]


class TestDetectPrerequisiteCycles:
    """_detect_prerequisite_cycles: Kosaraju SCC on the prereq subgraph."""

    def test_empty_returns_empty(self) -> None:
        assert validate._detect_prerequisite_cycles([]) == []

    def test_acyclic_chain_returns_empty(self) -> None:
        edges = [_edge("a", "b"), _edge("b", "c"), _edge("c", "d")]
        assert validate._detect_prerequisite_cycles(edges) == []

    def test_simple_two_node_cycle_detected(self) -> None:
        edges = [_edge("a", "b"), _edge("b", "a")]
        cycles = validate._detect_prerequisite_cycles(edges)
        assert cycles == [["a", "b"]]

    def test_three_node_cycle_detected(self) -> None:
        edges = [_edge("a", "b"), _edge("b", "c"), _edge("c", "a")]
        cycles = validate._detect_prerequisite_cycles(edges)
        assert cycles == [["a", "b", "c"]]

    def test_self_loop_detected(self) -> None:
        edges = [_edge("a", "a")]
        assert validate._detect_prerequisite_cycles(edges) == [["a"]]

    def test_non_prereq_cycle_ignored(self) -> None:
        """historical_influence cycles are legitimate and must not fire."""
        edges = [
            _edge("a", "b", edge_type="historical_influence"),
            _edge("b", "a", edge_type="historical_influence"),
        ]
        assert validate._detect_prerequisite_cycles(edges) == []

    def test_mixed_cycle_only_prereq_counts(self) -> None:
        """An a→b→a cycle that uses one prereq and one non-prereq edge does
        not constitute a prerequisite-subgraph cycle."""
        edges = [
            _edge("a", "b"),
            _edge("b", "a", edge_type="historical_influence"),
        ]
        assert validate._detect_prerequisite_cycles(edges) == []

    def test_disjoint_cycles_both_detected(self) -> None:
        edges = [
            _edge("a", "b"),
            _edge("b", "a"),
            _edge("c", "d"),
            _edge("d", "c"),
        ]
        cycles = validate._detect_prerequisite_cycles(edges)
        assert cycles == [["a", "b"], ["c", "d"]]


class TestDetectUndeclaredPredicates:
    """_detect_undeclared_predicates: edge_type not in manifest."""

    def test_all_declared_returns_empty(self) -> None:
        edges = [_edge("a", "b"), _edge("a", "c")]
        declared = {"pedagogical_prerequisite"}
        assert validate._detect_undeclared_predicates(edges, declared) == {}

    def test_undeclared_counted(self) -> None:
        edges = [
            _edge("a", "b", edge_type="enables"),
            _edge("c", "d", edge_type="enables"),
            _edge("e", "f", edge_type="informed_by"),
        ]
        declared = {"pedagogical_prerequisite"}
        result = validate._detect_undeclared_predicates(edges, declared)
        assert result == {"enables": 2, "informed_by": 1}


class TestDetectAttributeShapeInconsistency:
    """_detect_attribute_shape_inconsistency: teaching_notes mix per domain."""

    def test_all_populated_does_not_fire(self) -> None:
        nodes = [
            _node("a", domain=["ethics"], teaching_notes="x"),
            _node("b", domain=["ethics"], teaching_notes="y"),
        ]
        assert validate._detect_attribute_shape_inconsistency(nodes) == []

    def test_all_null_does_not_fire(self) -> None:
        nodes = [
            _node("a", domain=["ethics"], teaching_notes=None),
            _node("b", domain=["ethics"], teaching_notes=None),
        ]
        assert validate._detect_attribute_shape_inconsistency(nodes) == []

    def test_even_mix_fires(self) -> None:
        nodes = [
            _node("a", domain=["ethics"], teaching_notes="x"),
            _node("b", domain=["ethics"], teaching_notes=None),
            _node("c", domain=["ethics"], teaching_notes="y"),
            _node("d", domain=["ethics"], teaching_notes=None),
        ]
        result = validate._detect_attribute_shape_inconsistency(nodes)
        assert ("ethics", 2, 2) in result

    def test_lopsided_does_not_fire(self) -> None:
        """9-of-10 populated is a 90/10 split — below the 30% minority floor."""
        nodes = [
            _node(f"n{i}", domain=["ethics"], teaching_notes=("x" if i < 9 else None))
            for i in range(10)
        ]
        assert validate._detect_attribute_shape_inconsistency(nodes) == []


class TestDetectMissingRigorScore:
    """_detect_missing_rigor_score: prereq inbound + default rigor."""

    def test_default_with_inbound_prereq_fires(self) -> None:
        nodes = [_node("a"), _node("b", rigor_score_computed=0.5)]
        edges = [_edge("a", "b")]
        assert validate._detect_missing_rigor_score(nodes, edges) == ["b"]

    def test_non_default_does_not_fire(self) -> None:
        nodes = [_node("a"), _node("b", rigor_score_computed=0.7)]
        edges = [_edge("a", "b")]
        assert validate._detect_missing_rigor_score(nodes, edges) == []

    def test_no_inbound_prereq_does_not_fire(self) -> None:
        """A node with no inbound prereq is excluded — formula has no inputs."""
        nodes = [_node("a", rigor_score_computed=0.5)]
        assert validate._detect_missing_rigor_score(nodes, []) == []


class TestDetectRenderReadinessViolations:
    """_detect_render_readiness_violations: scaffolding tokens in label."""

    def test_clean_label_does_not_fire(self) -> None:
        nodes = [_node("a", label="Transcendental Idealism")]
        assert validate._detect_render_readiness_violations(nodes) == []

    def test_scaffolding_token_fires(self) -> None:
        nodes = [_node("svc_logic", label="logic primitive [service_node]")]
        result = validate._detect_render_readiness_violations(nodes)
        assert result == [
            ("svc_logic", "logic primitive [service_node]", "service_node")
        ]

    def test_case_insensitive(self) -> None:
        nodes = [_node("a", label="STUB concept")]
        result = validate._detect_render_readiness_violations(nodes)
        assert result and result[0][2] == "stub"


class TestDetectSyntheticReviewQueue:
    """_detect_synthetic_review_queue: confidence_level filter."""

    def test_no_synthetic_returns_empty(self) -> None:
        nodes = [_node("a"), _node("b", confidence_level="EXTRACTED")]
        assert validate._detect_synthetic_review_queue(nodes) == []

    def test_synthetic_returned_sorted(self) -> None:
        nodes = [
            _node("z", confidence_level="SYNTHETIC"),
            _node("a", confidence_level="SYNTHETIC"),
            _node("b"),
        ]
        assert validate._detect_synthetic_review_queue(nodes) == ["a", "z"]


class TestDetectOrphanLeaves:
    """_detect_orphan_leaves: zero in/out prereq edges."""

    def test_connected_node_does_not_fire(self) -> None:
        nodes = [_node("a"), _node("b")]
        edges = [_edge("a", "b")]
        assert validate._detect_orphan_leaves(nodes, edges) == []

    def test_isolated_node_fires(self) -> None:
        nodes = [_node("a"), _node("b"), _node("alone")]
        edges = [_edge("a", "b")]
        assert validate._detect_orphan_leaves(nodes, edges) == ["alone"]

    def test_only_non_prereq_edge_still_orphan(self) -> None:
        """A node connected only by historical_influence is orphan-leaf."""
        nodes = [_node("a"), _node("b")]
        edges = [_edge("a", "b", edge_type="historical_influence")]
        assert validate._detect_orphan_leaves(nodes, edges) == ["a", "b"]


class TestDetectSuspiciousCrossDomainRatio:
    """_detect_suspicious_cross_domain_ratio: per-domain inbound mix."""

    def test_within_domain_only_does_not_fire(self) -> None:
        nodes = [
            _node("a", domain=["ethics"]),
            _node("b", domain=["ethics"]),
        ]
        edges = [_edge("a", "b")]
        assert validate._detect_suspicious_cross_domain_ratio(nodes, edges) == []

    def test_majority_cross_domain_fires(self) -> None:
        nodes = [
            _node("p1", domain=["epistemology"]),
            _node("p2", domain=["epistemology"]),
            _node("p3", domain=["epistemology"]),
            _node("e1", domain=["ethics"]),
            _node("target", domain=["ethics"]),
        ]
        edges = [
            _edge("p1", "target"),
            _edge("p2", "target"),
            _edge("p3", "target"),
            _edge("e1", "target"),
        ]
        result = validate._detect_suspicious_cross_domain_ratio(nodes, edges)
        assert ("ethics", 4, 3) in result

    def test_below_threshold_does_not_fire(self) -> None:
        """40% threshold is exclusive (>40%); equal does not fire."""
        nodes = [
            _node("p1", domain=["epistemology"]),
            _node("p2", domain=["epistemology"]),
            _node("e1", domain=["ethics"]),
            _node("e2", domain=["ethics"]),
            _node("e3", domain=["ethics"]),
            _node("target", domain=["ethics"]),
        ]
        # 2 cross-domain (p1, p2) + 3 within-domain (e1, e2, e3) = 2/5 = 40%
        edges = [_edge(s, "target") for s in ("p1", "p2", "e1", "e2", "e3")]
        result = validate._detect_suspicious_cross_domain_ratio(nodes, edges)
        assert result == []


class TestReadPredicateManifest:
    """_read_predicate_manifest: markdown registry parser."""

    def test_absent_file_returns_empty(self, tmp_path: Path) -> None:
        assert validate._read_predicate_manifest(tmp_path / "missing.md") == set()

    def test_placeholder_returns_empty(self, tmp_path: Path) -> None:
        path = tmp_path / "manifest.md"
        path.write_text(
            "## Predicate registry\n\n"
            "| Predicate | Domain | Range |\n"
            "|---|---|---|\n"
            "| *(none yet)* | | |\n"
        )
        assert validate._read_predicate_manifest(path) == set()

    def test_populated_registry_parsed(self, tmp_path: Path) -> None:
        path = tmp_path / "manifest.md"
        path.write_text(
            "# Title\n\n"
            "## Predicate registry\n\n"
            "| Predicate | Domain | Range | Cardinality | Description |\n"
            "|---|---|---|---|---|\n"
            "| `pedagogical_prerequisite` | `nodes` | `nodes` | many-to-many | A. |\n"
            "| `historical_influence` | `nodes` | `nodes` | many-to-many | B. |\n\n"
            "## Reserved-but-unused\n\n"
            "| Predicate | Source ADR | Status |\n"
            "|---|---|---|\n"
            "| `enables` | ADR 0016 | reserved |\n"
        )
        result = validate._read_predicate_manifest(path)
        assert result == {"pedagogical_prerequisite", "historical_influence"}


class TestValidateGraphIntegration:
    """validate_graph end-to-end with a monkey-patched DB reader."""

    def _patch_db(
        self,
        monkeypatch: pytest.MonkeyPatch,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> None:
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        monkeypatch.setattr(validate, "_read_graph_from_db", lambda _: (nodes, edges))

    def test_clean_graph_runs_all_categories(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """All seven soft-warn categories register in checks_run, even clean."""
        self._patch_db(monkeypatch, [], [])
        r = validate_graph()
        assert r.hard_fails == []
        for cat in validate.GRAPH_SOFT_WARN_CATEGORIES:
            assert cat in r.checks_run, cat
        assert "graph_audit" in r.checks_run

    def test_duplicate_node_id_hard_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_db(monkeypatch, [_node("a"), _node("a")], [])
        r = validate_graph()
        assert any("duplicate_node_id" in m for m in r.hard_fails)

    def test_dangling_edge_hard_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_db(monkeypatch, [_node("a")], [_edge("a", "ghost")])
        r = validate_graph()
        assert any("dangling_edge" in m for m in r.hard_fails)

    def test_prereq_cycle_hard_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_db(
            monkeypatch,
            [_node("a"), _node("b")],
            [_edge("a", "b"), _edge("b", "a")],
        )
        r = validate_graph()
        assert any("prerequisite_cycle" in m for m in r.hard_fails)

    def test_undeclared_predicate_soft_warns(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "PREDICATE_MANIFEST.md"
        manifest.write_text(
            "## Predicate registry\n\n"
            "| Predicate |\n|---|\n| `pedagogical_prerequisite` |\n"
        )
        monkeypatch.setattr(validate, "PREDICATE_MANIFEST_PATH", manifest)
        self._patch_db(
            monkeypatch,
            [_node("a"), _node("b")],
            [_edge("a", "b", edge_type="not_declared")],
        )
        r = validate_graph()
        assert "undeclared_predicate" in r.soft_warns

    def test_synthetic_node_soft_warns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_db(
            monkeypatch,
            [_node("a", confidence_level="SYNTHETIC")],
            [],
        )
        r = validate_graph()
        assert "synthetic_review_queue" in r.soft_warns

    def test_orphan_leaf_soft_warns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_db(monkeypatch, [_node("alone")], [])
        r = validate_graph()
        assert "orphan_leaf" in r.soft_warns

    def test_db_failure_hard_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

        def boom(_: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            raise RuntimeError("connection refused")

        monkeypatch.setattr(validate, "_read_graph_from_db", boom)
        r = validate_graph()
        assert any("DB connection or query failed" in m for m in r.hard_fails)


class TestValidateGraphSnapshot:
    """validate_graph --export-snapshot mode."""

    def test_snapshot_writes_json(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        nodes = [_node("a")]
        edges = [_edge("a", "a")]  # self-cycle would fail in audit mode
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        monkeypatch.setattr(validate, "_read_graph_from_db", lambda _: (nodes, edges))
        snapshot = tmp_path / "snapshot.json"
        r = validate_graph(export_snapshot=snapshot)
        assert "graph_export_snapshot" in r.checks_run
        assert r.hard_fails == []  # snapshot mode skips checks
        payload = json.loads(snapshot.read_text())
        assert payload["nodes"][0]["id"] == "a"
        assert payload["edges"][0]["edge_type"] == "pedagogical_prerequisite"


class TestMainExportSnapshotMode:
    """main(): --export-snapshot dispatch."""

    def test_export_snapshot_writes_and_exits_clean(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        monkeypatch.setattr(
            validate,
            "_read_graph_from_db",
            lambda _: ([_node("a")], []),
        )
        path = tmp_path / "snap.json"
        rc = main(["--export-snapshot", str(path)])
        assert rc == 0
        assert path.is_file()


# ---------------------------------------------------------------------------
# Cascade-analysis checks (per ADR 0041)
# ---------------------------------------------------------------------------


def _write_adr(
    repo: Path, *, engine: bool, num: str, status: str, body: str = ""
) -> Path:
    """Helper: write an ADR file under the appropriate subtree."""
    adr_dir = repo / ("engine" if engine else "product") / "adr"
    path = adr_dir / f"{num}-test-{num}.md"
    path.write_text(
        f"# ADR {num} — Test\n\n- **Status:** {status}\n- **Date:** 2026-05-01\n\n"
        f"## Context\n\nTest.\n\n## Decision\n\nTest.\n\n## Consequences\n\n{body}\n"
    )
    return path


class TestSupersededAdrCurrency:
    """validate_superseded_adr_currency: stale-citation detection."""

    def test_no_superseded_adrs_returns_empty(self, synthetic_repo: Path) -> None:
        """No superseded ADRs in the repo means no checks fire."""
        r = validate_superseded_adr_currency()
        assert r.soft_warns == {}
        assert "cascade_superseded_adr_currency" in r.checks_run

    def test_unmarked_citation_warns(self, synthetic_repo: Path) -> None:
        """Doc citing a superseded ADR without historical marker warns."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        _write_adr(synthetic_repo, engine=True, num="0051", status="Accepted")
        # Doc that cites 0050 without "superseded" or "0051" nearby.
        (synthetic_repo / "product" / "docs" / "stale.md").write_text(
            "Per ADR 0050, the cake is a lie.\n"
        )
        r = validate_superseded_adr_currency()
        assert "superseded_adr_currency" in r.soft_warns

    def test_historical_marker_suppresses_warn(self, synthetic_repo: Path) -> None:
        """Citation with 'superseded' nearby does not warn."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        _write_adr(synthetic_repo, engine=True, num="0051", status="Accepted")
        (synthetic_repo / "product" / "docs" / "history.md").write_text(
            "Per ADR 0050 (superseded by ADR 0051), the original framing was X.\n"
        )
        r = validate_superseded_adr_currency()
        assert "superseded_adr_currency" not in r.soft_warns

    def test_new_adr_id_in_window_suppresses_warn(self, synthetic_repo: Path) -> None:
        """Citation with the new ADR id nearby does not warn."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        _write_adr(synthetic_repo, engine=True, num="0051", status="Accepted")
        (synthetic_repo / "product" / "docs" / "ok.md").write_text(
            "ADR 0050 — see also ADR 0051 for the current framing.\n"
        )
        r = validate_superseded_adr_currency()
        assert "superseded_adr_currency" not in r.soft_warns

    def test_adr_files_excluded_from_grep(self, synthetic_repo: Path) -> None:
        """Citations inside */adr/* files are not flagged (their job is narration)."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        _write_adr(synthetic_repo, engine=True, num="0051", status="Accepted")
        # Another ADR file that mentions 0050 without marker — should not warn.
        _write_adr(
            synthetic_repo,
            engine=True,
            num="0052",
            status="Accepted",
            body="ADR 0050 framing carries forward.",
        )
        r = validate_superseded_adr_currency()
        assert "superseded_adr_currency" not in r.soft_warns

    def test_engine_log_excluded(self, synthetic_repo: Path) -> None:
        """ENGINE_LOG.md is excluded — its job is historical narration."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        _write_adr(synthetic_repo, engine=True, num="0051", status="Accepted")
        (synthetic_repo / "engine" / "ENGINE_LOG.md").write_text(
            "## [Unreleased]\n\n### Changed\n\n- ADR 0050 status flipped.\n"
        )
        r = validate_superseded_adr_currency()
        assert "superseded_adr_currency" not in r.soft_warns


class TestAdrBackReferenceOrphan:
    """validate_adr_back_reference_orphan: zero-inbound-citation detection."""

    def test_cited_adr_does_not_warn(self, synthetic_repo: Path) -> None:
        """An Accepted ADR cited from a non-ADR doc is not orphaned."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
        (synthetic_repo / "product" / "docs" / "uses.md").write_text(
            "See ADR 0050 for the contract.\n"
        )
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" not in r.soft_warns

    def test_uncited_accepted_adr_warns(self, synthetic_repo: Path) -> None:
        """An Accepted ADR with no inbound non-ADR citation warns."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" in r.soft_warns

    def test_orphan_ok_annotation_suppresses(self, synthetic_repo: Path) -> None:
        """Orphan-OK annotation suppresses the warn."""
        adr_dir = synthetic_repo / "engine" / "adr"
        path = adr_dir / "0050-orphan-ok.md"
        path.write_text(
            "# ADR 0050 — Test\n\n"
            "- **Status:** Accepted\n"
            "- **Orphan-OK:** load-bearing for Phase 7; revisit at S-0050\n"
            "- **Date:** 2026-05-01\n\n"
            "## Context\n\nTest.\n\n## Decision\n\nTest.\n\n## Consequences\n\n"
        )
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" not in r.soft_warns

    def test_superseded_adr_not_checked(self, synthetic_repo: Path) -> None:
        """Superseded ADRs are not subject to the orphan check (only Accepted)."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" not in r.soft_warns


class TestAdrConsequencesDeliverableAudit:
    """validate_adr_consequences_deliverable_audit: promised-but-absent detection."""

    def test_no_archive_dir_returns_empty(
        self, synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without an archive dir, the audit cannot check session closure."""
        # Synthetic_repo doesn't create archive/; this is the natural state.
        r = validate_adr_consequences_deliverable_audit()
        assert r.soft_warns == {}

    def test_promise_for_unclosed_session_no_warn(self, synthetic_repo: Path) -> None:
        """A promise for a session that hasn't closed yet is not flagged."""
        archive_dir = synthetic_repo / "engine" / "session" / "archive"
        archive_dir.mkdir()
        # No archives — target session not closed.
        _write_adr(
            synthetic_repo,
            engine=True,
            num="0050",
            status="Accepted",
            body="`tools/foo.py` lands around S-0099.",
        )
        r = validate_adr_consequences_deliverable_audit()
        assert "adr_consequences_deliverable_audit" not in r.soft_warns

    def test_promise_for_closed_session_with_missing_path_warns(
        self, synthetic_repo: Path
    ) -> None:
        """A promise for a closed session with an absent path warns."""
        archive_dir = synthetic_repo / "engine" / "session" / "archive"
        archive_dir.mkdir()
        (archive_dir / "S-0005.json").write_text("{}")
        _write_adr(
            synthetic_repo,
            engine=True,
            num="0050",
            status="Accepted",
            body="`tools/missing.py` lands around S-0005.",
        )
        r = validate_adr_consequences_deliverable_audit()
        assert "adr_consequences_deliverable_audit" in r.soft_warns

    def test_promise_for_closed_session_with_present_path_no_warn(
        self, synthetic_repo: Path
    ) -> None:
        """A promise for a closed session with the path present does not warn."""
        archive_dir = synthetic_repo / "engine" / "session" / "archive"
        archive_dir.mkdir()
        (archive_dir / "S-0005.json").write_text("{}")
        (synthetic_repo / "tools").mkdir()
        (synthetic_repo / "tools" / "delivered.py").write_text("# delivered")
        _write_adr(
            synthetic_repo,
            engine=True,
            num="0051",
            status="Accepted",
            body="`tools/delivered.py` lands around S-0005.",
        )
        r = validate_adr_consequences_deliverable_audit()
        assert "adr_consequences_deliverable_audit" not in r.soft_warns


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
