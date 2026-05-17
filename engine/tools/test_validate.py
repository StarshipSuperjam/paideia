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
import subprocess
import sys
import threading
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
    validate_duplicate_adr_number,
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

    def test_health_check_overdue_soft_warns_when_past_cadence(
        self, synthetic_repo: Path
    ) -> None:
        """Overdue audit soft-warns when next_id - last_audit_session > cadence.

        Per ADR 0022 Consequences amendment at S-0041: the SessionStart hook
        surfaces overdue at boot; this validator check is defense-in-depth
        in case the hook silently fails.
        """
        (synthetic_repo / "engine" / "session" / "register_state.json").write_text(
            json.dumps(
                {
                    "next_id": "0042",
                    "last_claimed": "S-0041",
                    "current_status": "in_progress",
                    "health_check_cadence": 10,
                    "last_audit_session": "S-0030",
                }
            )
        )
        r = validate_repo_structure()
        assert "health_check_overdue" in r.soft_warns
        msg = r.soft_warns["health_check_overdue"][0]
        assert "S-0042" in msg
        assert "S-0030" in msg
        assert "overdue by 2" in msg

    def test_health_check_overdue_silent_at_natural_cadence_slot(
        self, synthetic_repo: Path
    ) -> None:
        """No soft-warn at the natural cadence slot (slots_since == cadence).

        The hook surfaces "due"; the validator stays silent because nothing
        is overdue yet — the audit can fire in this very session.
        """
        (synthetic_repo / "engine" / "session" / "register_state.json").write_text(
            json.dumps(
                {
                    "next_id": "0040",
                    "last_claimed": "S-0039",
                    "current_status": "in_progress",
                    "health_check_cadence": 10,
                    "last_audit_session": "S-0030",
                }
            )
        )
        r = validate_repo_structure()
        assert "health_check_overdue" not in r.soft_warns

    def test_health_check_overdue_silent_when_field_absent(
        self, synthetic_repo: Path
    ) -> None:
        """Legacy register_state.json without last_audit_session triggers no soft-warn.

        The hook's strict-modulo fallback covers the legacy case at the
        surface; the validator skips because the contract anchor is absent.
        """
        # synthetic_repo's default register has no last_audit_session field.
        r = validate_repo_structure()
        assert "health_check_overdue" not in r.soft_warns
        assert "health_check_overdue" in r.checks_run

    def test_health_check_overdue_silent_when_under_cadence(
        self, synthetic_repo: Path
    ) -> None:
        """No soft-warn when slots_since is below the cadence."""
        (synthetic_repo / "engine" / "session" / "register_state.json").write_text(
            json.dumps(
                {
                    "next_id": "0035",
                    "last_claimed": "S-0034",
                    "current_status": "in_progress",
                    "health_check_cadence": 10,
                    "last_audit_session": "S-0030",
                }
            )
        )
        r = validate_repo_structure()
        assert "health_check_overdue" not in r.soft_warns


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


class TestDetectEdgeEvidenceEmpty:
    """_detect_edge_evidence_empty: cross-domain prereq edges missing
    pedagogical-warrant evidence prose (Issue #62 Proposal 1)."""

    def test_cross_domain_with_null_evidence_fires(self) -> None:
        nodes = [
            _node("p", domain=["epistemology"]),
            _node("t", domain=["ethics"]),
        ]
        edges = [
            {
                "id": "e1",
                "source_id": "p",
                "target_id": "t",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            },
        ]
        assert validate._detect_edge_evidence_empty(nodes, edges) == [("e1", "p", "t")]

    def test_cross_domain_with_empty_string_evidence_fires(self) -> None:
        nodes = [
            _node("p", domain=["epistemology"]),
            _node("t", domain=["ethics"]),
        ]
        edges = [
            {
                "id": "e1",
                "source_id": "p",
                "target_id": "t",
                "edge_type": "pedagogical_prerequisite",
                "evidence": "   ",
            },
        ]
        assert validate._detect_edge_evidence_empty(nodes, edges) == [("e1", "p", "t")]

    def test_within_domain_with_null_evidence_does_not_fire(self) -> None:
        nodes = [
            _node("p", domain=["ethics"]),
            _node("t", domain=["ethics"]),
        ]
        edges = [
            {
                "id": "e1",
                "source_id": "p",
                "target_id": "t",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            },
        ]
        assert validate._detect_edge_evidence_empty(nodes, edges) == []

    def test_cross_domain_with_populated_evidence_does_not_fire(self) -> None:
        nodes = [
            _node("p", domain=["epistemology"]),
            _node("t", domain=["ethics"]),
        ]
        edges = [
            {
                "id": "e1",
                "source_id": "p",
                "target_id": "t",
                "edge_type": "pedagogical_prerequisite",
                "evidence": "p grounds the normative warrant for t.",
            },
        ]
        assert validate._detect_edge_evidence_empty(nodes, edges) == []

    def test_non_prereq_edge_skipped(self) -> None:
        nodes = [
            _node("p", domain=["epistemology"]),
            _node("t", domain=["ethics"]),
        ]
        edges = [
            {
                "id": "e1",
                "source_id": "p",
                "target_id": "t",
                "edge_type": "historical_influence",
                "evidence": None,
            },
        ]
        assert validate._detect_edge_evidence_empty(nodes, edges) == []


class TestDetectTopLevelDisciplineLabelAsPrereqSource:
    """_detect_top_level_discipline_label_as_prereq_source: umbrella-as-
    prereq-source pattern detection (Issue #62 Proposal 2b)."""

    def test_top_level_label_with_3_targets_2_domains_fires(self) -> None:
        nodes = [
            _node(
                "philosophy_of_science",
                label="philosophy_of_science",
                domain=["philosophy_of_science"],
            ),
            _node("scientific_method", domain=["philosophy_of_science"]),
            _node("paradigm", domain=["philosophy_of_science", "metaphysics"]),
            _node("induction", domain=["epistemology"]),
        ]
        edges = [
            _edge("philosophy_of_science", "scientific_method"),
            _edge("philosophy_of_science", "paradigm"),
            _edge("philosophy_of_science", "induction"),
        ]
        result = validate._detect_top_level_discipline_label_as_prereq_source(
            nodes, edges
        )
        assert (
            "philosophy_of_science",
            "philosophy_of_science",
            3,
            3,
        ) in result

    def test_top_level_label_with_below_min_prereqs_does_not_fire(self) -> None:
        nodes = [
            _node(
                "philosophy_of_science",
                label="philosophy_of_science",
                domain=["philosophy_of_science"],
            ),
            _node("scientific_method", domain=["philosophy_of_science"]),
            _node("paradigm", domain=["metaphysics"]),
        ]
        edges = [
            _edge("philosophy_of_science", "scientific_method"),
            _edge("philosophy_of_science", "paradigm"),
        ]
        assert (
            validate._detect_top_level_discipline_label_as_prereq_source(nodes, edges)
            == []
        )

    def test_top_level_label_with_single_target_domain_does_not_fire(
        self,
    ) -> None:
        nodes = [
            _node(
                "philosophy_of_science",
                label="philosophy_of_science",
                domain=["philosophy_of_science"],
            ),
            _node("scientific_method", domain=["philosophy_of_science"]),
            _node("paradigm", domain=["philosophy_of_science"]),
            _node("induction", domain=["philosophy_of_science"]),
        ]
        edges = [
            _edge("philosophy_of_science", "scientific_method"),
            _edge("philosophy_of_science", "paradigm"),
            _edge("philosophy_of_science", "induction"),
        ]
        assert (
            validate._detect_top_level_discipline_label_as_prereq_source(nodes, edges)
            == []
        )

    def test_non_canonical_label_does_not_fire(self) -> None:
        nodes = [
            _node(
                "scientific_method",
                label="scientific_method",
                domain=["philosophy_of_science"],
            ),
            _node("hypothesis", domain=["philosophy_of_science"]),
            _node("induction", domain=["epistemology"]),
            _node("falsification", domain=["philosophy_of_science"]),
        ]
        edges = [
            _edge("scientific_method", "hypothesis"),
            _edge("scientific_method", "induction"),
            _edge("scientific_method", "falsification"),
        ]
        assert (
            validate._detect_top_level_discipline_label_as_prereq_source(nodes, edges)
            == []
        )


class TestDetectPrereqDirectionSummaryInconsistency:
    """_detect_prereq_direction_summary_inconsistency: phrase-pattern
    detection of authoring direction reversals (Issue #62 Proposal 3+5
    merged). Cases anchored on the audit's documented reversals."""

    def test_proposition_attitude_reversal_fires(self) -> None:
        # CB-E-63: edge runs propositional_attitude -> proposition,
        # but proposition.summary names propositions as the contents
        # supplied to PA — PA depends on proposition, edge is reversed.
        target = _node("proposition", domain=["philosophy_of_language"])
        target["summary"] = (
            "Propositions are the contents of propositional attitudes "
            "such as belief and desire."
        )
        source = _node("propositional_attitude", domain=["philosophy_of_mind"])
        nodes = [source, target]
        edges = [
            {
                "id": "e63",
                "source_id": "propositional_attitude",
                "target_id": "proposition",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            }
        ]
        result = validate._detect_prereq_direction_summary_inconsistency(nodes, edges)
        assert any(f[0] == "e63" and "the contents of" in f[3] for f in result)

    def test_justice_morality_reversal_fires(self) -> None:
        # CB-E-70: edge runs justice -> morality, but morality.summary
        # names morality as the broader framework — justice depends on
        # morality (broader).
        target = _node("morality", domain=["metaethics"])
        target["summary"] = (
            "Morality is the broader normative framework within which "
            "specific theories of justice operate."
        )
        source = _node("justice", domain=["political_philosophy"])
        nodes = [source, target]
        edges = [
            {
                "id": "e70",
                "source_id": "justice",
                "target_id": "morality",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            }
        ]
        result = validate._detect_prereq_direction_summary_inconsistency(nodes, edges)
        assert any(f[0] == "e70" and "the broader" in f[3] for f in result)

    def test_cross_domain_with_no_reversal_phrase_does_not_fire(self) -> None:
        target = _node("scientific_realism", domain=["philosophy_of_science"])
        target["summary"] = (
            "Scientific realism holds that successful theories give us "
            "reason to believe in their unobservable entities."
        )
        source = _node("truth", domain=["epistemology"])
        nodes = [source, target]
        edges = [
            {
                "id": "e1",
                "source_id": "truth",
                "target_id": "scientific_realism",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            }
        ]
        assert (
            validate._detect_prereq_direction_summary_inconsistency(nodes, edges) == []
        )

    def test_within_domain_skipped_even_if_pattern_present(self) -> None:
        # Same-domain edge: pattern present in summary, but cross-domain
        # filter excludes within-subdomain pairs (less defect-prone).
        target = _node("proposition", domain=["philosophy_of_language"])
        target["summary"] = "Propositions are the contents of propositional attitudes."
        source = _node("propositional_attitude", domain=["philosophy_of_language"])
        nodes = [source, target]
        edges = [
            {
                "id": "e1",
                "source_id": "propositional_attitude",
                "target_id": "proposition",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            }
        ]
        assert (
            validate._detect_prereq_direction_summary_inconsistency(nodes, edges) == []
        )

    def test_summary_naming_only_target_does_not_fire(self) -> None:
        # Pattern requires both labels to appear with connecting phrase
        # between them. Target naming itself but not source -> no fire.
        target = _node("proposition", domain=["philosophy_of_language"])
        target["summary"] = "Propositions are the bearers of truth values."
        source = _node("propositional_attitude", domain=["philosophy_of_mind"])
        nodes = [source, target]
        edges = [
            {
                "id": "e1",
                "source_id": "propositional_attitude",
                "target_id": "proposition",
                "edge_type": "pedagogical_prerequisite",
                "evidence": None,
            }
        ]
        assert (
            validate._detect_prereq_direction_summary_inconsistency(nodes, edges) == []
        )


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


class TestReadGraphFromDbTimeouts:
    """_read_graph_from_db: bounded-wait connect + statement-level timeout.

    S-0186 surfaced a recurring hang (S-0184 boot, S-0185 close, S-0186
    close) where validate.py's graph-audit step blocked indefinitely on
    paused / unreachable Supabase. ``psycopg.connect()`` without an
    explicit ``connect_timeout`` waits forever for the server response.
    These tests assert the two caps actually wire through to psycopg.
    """

    def test_connect_called_with_connect_timeout_and_statement_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Ensure both bounded-wait parameters are passed to psycopg.connect()."""
        captured: dict[str, Any] = {}

        class _StubCursor:
            def __enter__(self) -> "_StubCursor":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def execute(self, _sql: str) -> None:
                pass

            def fetchall(self) -> list[dict[str, Any]]:
                return []

        class _StubConn:
            def __enter__(self) -> "_StubConn":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def cursor(self, **_kwargs: Any) -> _StubCursor:
                return _StubCursor()

        def stub_connect(connection_string: str, **kwargs: Any) -> _StubConn:
            captured["connection_string"] = connection_string
            captured["kwargs"] = kwargs
            return _StubConn()

        import sys as _sys

        psycopg_stub = type(_sys)("psycopg")
        psycopg_stub.connect = stub_connect  # type: ignore[attr-defined]
        rows_stub = type(_sys)("psycopg.rows")

        def _dict_row(_cursor: object) -> object:
            return None

        rows_stub.dict_row = _dict_row  # type: ignore[attr-defined]
        monkeypatch.setitem(_sys.modules, "psycopg", psycopg_stub)
        monkeypatch.setitem(_sys.modules, "psycopg.rows", rows_stub)

        validate._read_graph_from_db("postgresql://user:pw@host/db")

        assert captured["connection_string"] == "postgresql://user:pw@host/db"
        assert captured["kwargs"].get("connect_timeout") == 10, (
            "connect_timeout must be set to a finite value; absent value caused "
            "the S-0184/0185/0186 indefinite hang against paused Supabase"
        )
        assert "statement_timeout=30000" in captured["kwargs"].get("options", ""), (
            "statement_timeout option must be set so server-side query waits are "
            "also bounded; protects against in-flight query stalls distinct from "
            "the initial connect"
        )

    def test_watchdog_cancels_in_flight_query_when_wall_clock_cap_exceeded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """S-0187: client-side wall-clock cap fires conn.cancel() on hang.

        S-0186 added ``options="-c statement_timeout=30000"`` to bound
        server-side query waits. Supabase's pgbouncer transaction-pool
        URL (the project's SUPABASE_DB_URL) silently strips the
        ``options=-c`` parameter from the startup packet — the server
        cap is inert there. S-0187's wall-clock watchdog calls
        ``conn.cancel()`` after the cap; psycopg surfaces a
        QueryCanceled exception that the caller routes to graph_audit
        hard-fail. This test stubs a cursor whose ``execute()`` blocks
        until a Cancel event and verifies the cancellation reaches
        the cursor within ~2× the watchdog cap.
        """
        cancel_called = threading.Event()
        cursor_unblocked = threading.Event()

        class _BlockingCursor:
            def __enter__(self) -> "_BlockingCursor":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def execute(self, _sql: str) -> None:
                # Block until conn.cancel() fires the unblock event,
                # OR fail the test if we sit here way past the cap.
                if not cursor_unblocked.wait(timeout=10.0):
                    raise AssertionError(
                        "execute() blocked past 10s without watchdog cancel"
                    )
                # Simulate psycopg's behavior on PQcancel — raise a
                # QueryCanceled-shaped exception to the caller. The
                # specific subclass doesn't matter for this test;
                # any Exception bubbles up through the finally and
                # the caller's except-Exception handler.
                raise RuntimeError("query cancelled by watchdog (simulated)")

            def fetchall(self) -> list[dict[str, Any]]:  # pragma: no cover
                return []

        class _StubConn:
            def __enter__(self) -> "_StubConn":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def cursor(self, **_kwargs: Any) -> _BlockingCursor:
                return _BlockingCursor()

            def cancel(self) -> None:
                # Watchdog fires this; simulate PQcancel by unblocking
                # the cursor's execute() so it can raise.
                cancel_called.set()
                cursor_unblocked.set()

        def stub_connect(_connection_string: str, **_kwargs: Any) -> _StubConn:
            return _StubConn()

        import sys as _sys

        psycopg_stub = type(_sys)("psycopg")
        psycopg_stub.connect = stub_connect  # type: ignore[attr-defined]
        rows_stub = type(_sys)("psycopg.rows")

        def _dict_row(_cursor: object) -> object:
            return None

        rows_stub.dict_row = _dict_row  # type: ignore[attr-defined]
        monkeypatch.setitem(_sys.modules, "psycopg", psycopg_stub)
        monkeypatch.setitem(_sys.modules, "psycopg.rows", rows_stub)

        # Use a 0.5s cap so the test completes quickly. The watchdog
        # should fire within ~0.5s, conn.cancel() unblocks execute(),
        # and the RuntimeError bubbles out.
        with pytest.raises(RuntimeError, match="query cancelled by watchdog"):
            validate._read_graph_from_db(
                "postgresql://user:pw@host/db", wall_clock_timeout_s=0.5
            )

        assert cancel_called.is_set(), (
            "Watchdog must call conn.cancel() when the wall-clock cap is "
            "exceeded; otherwise hung Supabase reads block validate.py "
            "indefinitely (the S-0187 regression of the S-0186 fix)"
        )

    def test_watchdog_does_not_fire_when_query_completes_within_cap(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Happy path: queries complete fast; ``done.set()`` prevents
        ``conn.cancel()`` from firing.

        Regression guard against an overly-aggressive watchdog that
        cancels healthy in-flight queries. The watchdog must observe
        ``done`` being set before the cap elapses and exit cleanly.
        """
        cancel_called = threading.Event()

        class _FastCursor:
            def __enter__(self) -> "_FastCursor":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def execute(self, _sql: str) -> None:
                pass

            def fetchall(self) -> list[dict[str, Any]]:
                return []

        class _StubConn:
            def __enter__(self) -> "_StubConn":
                return self

            def __exit__(self, *_: Any) -> None:
                pass

            def cursor(self, **_kwargs: Any) -> _FastCursor:
                return _FastCursor()

            def cancel(self) -> None:
                cancel_called.set()

        def stub_connect(_connection_string: str, **_kwargs: Any) -> _StubConn:
            return _StubConn()

        import sys as _sys

        psycopg_stub = type(_sys)("psycopg")
        psycopg_stub.connect = stub_connect  # type: ignore[attr-defined]
        rows_stub = type(_sys)("psycopg.rows")

        def _dict_row(_cursor: object) -> object:
            return None

        rows_stub.dict_row = _dict_row  # type: ignore[attr-defined]
        monkeypatch.setitem(_sys.modules, "psycopg", psycopg_stub)
        monkeypatch.setitem(_sys.modules, "psycopg.rows", rows_stub)

        nodes, edges = validate._read_graph_from_db(
            "postgresql://user:pw@host/db", wall_clock_timeout_s=2.0
        )
        assert nodes == []
        assert edges == []
        # Allow the watchdog's daemon thread a small moment to observe
        # ``done`` and exit. If it had spuriously fired, cancel_called
        # would be set.
        import time as _t

        _t.sleep(0.05)
        assert not cancel_called.is_set(), (
            "Watchdog must NOT call conn.cancel() when queries complete "
            "within the cap — spurious cancellations would corrupt healthy "
            "in-flight reads"
        )


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
        """Superseded ADRs are not subject to the orphan check (Accepted or Deprecated only)."""
        _write_adr(
            synthetic_repo, engine=True, num="0050", status="Superseded by ADR 0051"
        )
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" not in r.soft_warns

    def test_uncited_deprecated_adr_warns(self, synthetic_repo: Path) -> None:
        """A Deprecated ADR with no inbound non-ADR citation warns (per ADR 0077)."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Deprecated")
        r = validate_adr_back_reference_orphan()
        assert "adr_back_reference_orphan" in r.soft_warns

    def test_cited_deprecated_adr_does_not_warn(self, synthetic_repo: Path) -> None:
        """A Deprecated ADR cited from a non-ADR doc is not orphaned."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Deprecated")
        (synthetic_repo / "product" / "docs" / "lessons.md").write_text(
            "ADR 0050 was abandoned; see the discussion below.\n"
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


class TestDuplicateAdrNumber:
    """validate_duplicate_adr_number: cross-partition collision detection.

    Defense-in-depth landed at S-0149 alongside the engine ADR 0052 → 0082
    renumber (Issue #91). Catches author-time mistakes in either partition
    at structural-phase validate time rather than via post-hoc audit.
    """

    def test_disjoint_partitions_does_not_warn(self, synthetic_repo: Path) -> None:
        """Engine 0050 + product 0060 (no collision) does not warn."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
        _write_adr(synthetic_repo, engine=False, num="0060", status="Accepted")
        r = validate_duplicate_adr_number()
        assert "duplicate_adr_number" not in r.soft_warns

    def test_cross_partition_collision_warns(self, synthetic_repo: Path) -> None:
        """Engine 0050 + product 0050 (collision) warns once for that number."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
        _write_adr(synthetic_repo, engine=False, num="0050", status="Accepted")
        r = validate_duplicate_adr_number()
        assert "duplicate_adr_number" in r.soft_warns
        assert len(r.soft_warns["duplicate_adr_number"]) == 1
        msg = r.soft_warns["duplicate_adr_number"][0]
        assert "0050" in msg
        assert "engine/adr/0050" in msg
        assert "product/adr/0050" in msg

    def test_engine_only_does_not_warn(self, synthetic_repo: Path) -> None:
        """Engine ADR with no matching product ADR does not warn."""
        _write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
        r = validate_duplicate_adr_number()
        assert "duplicate_adr_number" not in r.soft_warns


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


# ---------------------------------------------------------------------------
# Wing-count threshold extraction (S-0088 per Issue #46)
# ---------------------------------------------------------------------------


class TestValidateRuntimePhaseRegression:
    """Regression detection across the last N entries of validate-history.jsonl.

    Per ADR 0063: fires on sustained 1.5x target breach across the rolling
    window. Current run's tentative entry participates in the window when
    supplied. Four-phase model since S-0127 (Issue #90 fold): structural,
    health_probe, graph_audit, total.
    """

    def _write_history(self, path: Path, entries: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(e, separators=(",", ":")) for e in entries]
        path.write_text("\n".join(lines) + ("\n" if lines else ""))

    def _clean_entry(self) -> dict[str, Any]:
        return {
            "duration_structural_ms": 100.0,
            "duration_health_probe_ms": 3000.0,
            "duration_graph_audit_ms": 3000.0,
            "duration_total_ms": 6200.0,
        }

    def _breaching_entry(self) -> dict[str, Any]:
        # All four phases strictly exceed 1.5x their tiered target.
        return {
            "duration_structural_ms": 800.0,  # > 750 (1.5 * 500)
            "duration_health_probe_ms": 8000.0,  # > 7500 (1.5 * 5000)
            "duration_graph_audit_ms": 8000.0,  # > 7500 (1.5 * 5000)
            "duration_total_ms": 17000.0,  # > 16500 (1.5 * 11000)
        }

    def test_phase_targets_dict_has_four_phases(self) -> None:
        """The four-phase model from S-0127 must include health_probe."""
        assert set(validate.VALIDATOR_PHASE_TARGETS_MS.keys()) == {
            "duration_structural_ms",
            "duration_health_probe_ms",
            "duration_graph_audit_ms",
            "duration_total_ms",
        }

    def test_absent_history_returns_clean(self, tmp_path: Path) -> None:
        r = validate.validate_runtime_phase_regression(
            history_path=tmp_path / "missing.jsonl"
        )
        assert r.soft_warns == {}
        assert "validator_runtime_phase_regression" in r.checks_run

    def test_fewer_than_window_entries_returns_clean(self, tmp_path: Path) -> None:
        history = tmp_path / "h.jsonl"
        self._write_history(history, [self._breaching_entry()])
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert r.soft_warns == {}

    def test_all_phases_breach_fires_warn_per_phase(self, tmp_path: Path) -> None:
        history = tmp_path / "h.jsonl"
        self._write_history(history, [self._breaching_entry()] * 3)
        r = validate.validate_runtime_phase_regression(history_path=history)
        # All four phases breach → four soft-warns under the same category.
        assert "validator_runtime_phase_regression" in r.soft_warns
        msgs = r.soft_warns["validator_runtime_phase_regression"]
        assert len(msgs) == 4
        assert any("duration_structural_ms" in m for m in msgs)
        assert any("duration_health_probe_ms" in m for m in msgs)
        assert any("duration_graph_audit_ms" in m for m in msgs)
        assert any("duration_total_ms" in m for m in msgs)

    def test_two_breaches_plus_one_clean_does_not_fire(self, tmp_path: Path) -> None:
        history = tmp_path / "h.jsonl"
        self._write_history(
            history,
            [self._breaching_entry(), self._breaching_entry(), self._clean_entry()],
        )
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert r.soft_warns == {}

    def test_only_structural_phase_breaches_fires_single_warn(
        self, tmp_path: Path
    ) -> None:
        history = tmp_path / "h.jsonl"
        # Only structural phase breaches; others stay clean.
        entry = {
            "duration_structural_ms": 1000.0,  # > 1.5 * 500
            "duration_health_probe_ms": 3000.0,
            "duration_graph_audit_ms": 3000.0,
            "duration_total_ms": 7100.0,
        }
        self._write_history(history, [entry] * 3)
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert "validator_runtime_phase_regression" in r.soft_warns
        msgs = r.soft_warns["validator_runtime_phase_regression"]
        assert len(msgs) == 1
        assert "duration_structural_ms" in msgs[0]

    def test_only_health_probe_phase_breaches_fires_single_warn(
        self, tmp_path: Path
    ) -> None:
        """Health-probe phase regression detected independently of others.

        Specifically guards the S-0127 split: a slow probe must surface as a
        health_probe warn, not a structural-phase false-positive.
        """
        history = tmp_path / "h.jsonl"
        entry = {
            "duration_structural_ms": 100.0,
            "duration_health_probe_ms": 8000.0,  # > 1.5 * 5000
            "duration_graph_audit_ms": 3000.0,
            "duration_total_ms": 11200.0,
        }
        self._write_history(history, [entry] * 3)
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert "validator_runtime_phase_regression" in r.soft_warns
        msgs = r.soft_warns["validator_runtime_phase_regression"]
        assert len(msgs) == 1
        assert "duration_health_probe_ms" in msgs[0]

    def test_tentative_entry_completes_window(self, tmp_path: Path) -> None:
        """Two breaches in history + a breaching tentative current run → fires."""
        history = tmp_path / "h.jsonl"
        self._write_history(history, [self._breaching_entry()] * 2)
        r = validate.validate_runtime_phase_regression(
            history_path=history,
            tentative_entry=self._breaching_entry(),
        )
        assert "validator_runtime_phase_regression" in r.soft_warns
        assert len(r.soft_warns["validator_runtime_phase_regression"]) == 4

    def test_tentative_clean_breaks_the_streak(self, tmp_path: Path) -> None:
        """Two breaches in history + a clean tentative current run → no fire."""
        history = tmp_path / "h.jsonl"
        self._write_history(history, [self._breaching_entry()] * 2)
        r = validate.validate_runtime_phase_regression(
            history_path=history,
            tentative_entry=self._clean_entry(),
        )
        assert r.soft_warns == {}

    def test_legacy_duration_ms_entries_skipped(self, tmp_path: Path) -> None:
        """Pre-S-0126 entries (only duration_ms) are not counted toward the
        rolling window — they lack the per-phase fields the regression check
        evaluates.
        """
        history = tmp_path / "h.jsonl"
        legacy_entry: dict[str, Any] = {"duration_ms": 9000.0}
        self._write_history(history, [legacy_entry] * 3)
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert r.soft_warns == {}

    def test_pre_split_three_phase_entries_skipped(self, tmp_path: Path) -> None:
        """Pre-S-0127 entries (only the three S-0126 phase fields) are not
        counted — they lack ``duration_health_probe_ms`` introduced at the
        Issue #90 fold.
        """
        history = tmp_path / "h.jsonl"
        pre_split_entry: dict[str, Any] = {
            "duration_structural_ms": 800.0,
            "duration_graph_audit_ms": 8000.0,
            "duration_total_ms": 9500.0,
        }
        self._write_history(history, [pre_split_entry] * 3)
        r = validate.validate_runtime_phase_regression(history_path=history)
        assert r.soft_warns == {}

    def test_malformed_jsonl_lines_skipped(self, tmp_path: Path) -> None:
        history = tmp_path / "h.jsonl"
        history.parent.mkdir(parents=True, exist_ok=True)
        history.write_text(
            "not valid json\n"
            + json.dumps(self._breaching_entry())
            + "\n"
            + "[]\n"
            + json.dumps(self._breaching_entry())
            + "\n"
            + json.dumps(self._breaching_entry())
            + "\n"
        )
        r = validate.validate_runtime_phase_regression(history_path=history)
        # Three well-formed breaching entries → all phases warn.
        assert "validator_runtime_phase_regression" in r.soft_warns


# ---------------------------------------------------------------------------
# Governed-doc soft-warns per ADR 0062 (S-0126; Issue #87 part b)
# ---------------------------------------------------------------------------


class TestValidateStateMdRowCount:
    """STATE.md row-count threshold gate."""

    def test_absent_state_md_returns_clean(self, tmp_path: Path) -> None:
        # No engine/STATE.md created.
        r = validate.validate_state_md_row_count(repo_root=tmp_path)
        assert r.soft_warns == {}
        assert "state_md_row_count" in r.checks_run

    def test_under_threshold_clean(self, tmp_path: Path) -> None:
        state_dir = tmp_path / "engine"
        state_dir.mkdir(parents=True)
        # 100 lines, under the 180 threshold.
        (state_dir / "STATE.md").write_text("\n".join(["row"] * 100) + "\n")
        r = validate.validate_state_md_row_count(repo_root=tmp_path)
        assert r.soft_warns == {}

    def test_over_threshold_fires(self, tmp_path: Path) -> None:
        state_dir = tmp_path / "engine"
        state_dir.mkdir(parents=True)
        # 200 lines, over the 180 threshold.
        (state_dir / "STATE.md").write_text("\n".join(["row"] * 200) + "\n")
        r = validate.validate_state_md_row_count(repo_root=tmp_path)
        assert "state_md_row_count" in r.soft_warns
        assert len(r.soft_warns["state_md_row_count"]) == 1
        assert "200 rows" in r.soft_warns["state_md_row_count"][0]


class TestValidateAdrConsequencesAmendmentHeaders:
    """Zero-tolerance gate against re-introduction of ADR inline-amendment pattern."""

    def _setup_repo(self, tmp_path: Path) -> None:
        (tmp_path / "engine" / "adr").mkdir(parents=True)
        (tmp_path / "product" / "adr").mkdir(parents=True)

    def test_clean_adr_corpus_no_warn(self, tmp_path: Path) -> None:
        self._setup_repo(tmp_path)
        (tmp_path / "engine" / "adr" / "0001-test.md").write_text(
            "# ADR 0001\n\n## Decision\n\nBody.\n\n## Consequences\n\nBody.\n"
        )
        r = validate.validate_adr_consequences_amendment_headers(repo_root=tmp_path)
        assert r.soft_warns == {}

    def test_amendment_header_in_engine_adr_fires(self, tmp_path: Path) -> None:
        self._setup_repo(tmp_path)
        (tmp_path / "engine" / "adr" / "0001-test.md").write_text(
            "# ADR 0001\n\n## Consequences\n\n### Amendment (S-0042) — retrofit\n\nProse.\n"
        )
        r = validate.validate_adr_consequences_amendment_headers(repo_root=tmp_path)
        assert "adr_consequences_amendment_header" in r.soft_warns
        msg = r.soft_warns["adr_consequences_amendment_header"][0]
        assert "engine/adr/0001-test.md" in msg
        assert "line 5" in msg

    def test_amendment_header_in_product_adr_fires(self, tmp_path: Path) -> None:
        self._setup_repo(tmp_path)
        (tmp_path / "product" / "adr" / "0042-x.md").write_text(
            "# ADR 0042\n\n## Consequences\n\n### Amendment (S-0099)\n\nProse.\n"
        )
        r = validate.validate_adr_consequences_amendment_headers(repo_root=tmp_path)
        assert "adr_consequences_amendment_header" in r.soft_warns
        assert (
            "product/adr/0042-x.md"
            in r.soft_warns["adr_consequences_amendment_header"][0]
        )

    def test_multiple_amendments_each_fire(self, tmp_path: Path) -> None:
        self._setup_repo(tmp_path)
        (tmp_path / "engine" / "adr" / "0056-multi.md").write_text(
            "# ADR 0056\n\n## Consequences\n\n"
            "### Amendment (S-0087)\n\nProse.\n\n"
            "### Amendment (S-0089)\n\nProse.\n\n"
            "### Amendment (S-0091)\n\nProse.\n"
        )
        r = validate.validate_adr_consequences_amendment_headers(repo_root=tmp_path)
        assert len(r.soft_warns["adr_consequences_amendment_header"]) == 3

    def test_no_adr_dir_returns_clean(self, tmp_path: Path) -> None:
        # tmp_path has no engine/adr or product/adr directories.
        r = validate.validate_adr_consequences_amendment_headers(repo_root=tmp_path)
        assert r.soft_warns == {}


class TestValidateHandoffLongResolvedSections:
    """HANDOFF.md prune-on-resolve discipline gate."""

    def test_absent_handoff_returns_clean(self, tmp_path: Path) -> None:
        r = validate.validate_handoff_long_resolved_sections(repo_root=tmp_path)
        assert r.soft_warns == {}
        assert "handoff_long_resolved_sections" in r.checks_run

    def test_few_resolved_sections_clean(self, tmp_path: Path) -> None:
        (tmp_path / "HANDOFF.md").write_text(
            "# Handoff Log\n\n"
            "## Item 1\n\n**Resolved:** S-0010 — landed in commit abc.\n\n"
            "## Item 2\n\n**Resolved:** S-0012 — landed in commit def.\n"
        )
        r = validate.validate_handoff_long_resolved_sections(
            repo_root=tmp_path, current_session_id="S-0015"
        )
        # 2 sections, under threshold 5; 5-session age, under threshold 10.
        assert r.soft_warns == {}

    def test_too_many_resolved_sections_fires_count_warn(self, tmp_path: Path) -> None:
        sections = "\n\n".join(
            [f"## Item {i}\n\n**Resolved:** S-0090 — landed." for i in range(8)]
        )
        (tmp_path / "HANDOFF.md").write_text(f"# Handoff Log\n\n{sections}\n")
        r = validate.validate_handoff_long_resolved_sections(
            repo_root=tmp_path, current_session_id="S-0095"
        )
        msgs = r.soft_warns.get("handoff_long_resolved_sections", [])
        # One count-warn at minimum (count=8 > 5).
        assert any("8 resolved sections" in m for m in msgs)

    def test_old_resolved_section_fires_age_warn(self, tmp_path: Path) -> None:
        (tmp_path / "HANDOFF.md").write_text(
            "# Handoff Log\n\n"
            "## Old Item\n\n**Resolved:** S-0010 — landed long ago.\n\n"
            "## Recent Item\n\n**Resolved:** S-0120 — landed recently.\n"
        )
        r = validate.validate_handoff_long_resolved_sections(
            repo_root=tmp_path, current_session_id="S-0126"
        )
        msgs = r.soft_warns.get("handoff_long_resolved_sections", [])
        # S-0010 is 116 sessions old (> 10); S-0120 is 6 sessions old (< 10).
        old_warns = [m for m in msgs if "S-0010" in m and "sessions old" in m]
        assert len(old_warns) == 1
        recent_warns = [m for m in msgs if "S-0120" in m]
        assert len(recent_warns) == 0

    def test_no_current_session_skips_age_check(self, tmp_path: Path) -> None:
        (tmp_path / "HANDOFF.md").write_text(
            "# Handoff Log\n\n## Old Item\n\n**Resolved:** S-0010 — landed.\n"
        )
        r = validate.validate_handoff_long_resolved_sections(
            repo_root=tmp_path, current_session_id=None
        )
        # No age check without current session id; count is 1 (under threshold).
        assert r.soft_warns == {}

    def test_preamble_resolved_prose_not_matched(self, tmp_path: Path) -> None:
        """The HANDOFF.md preamble uses 'Resolved' in prose without bold + S-NNNN;
        the regex only matches actual section-marker shape."""
        (tmp_path / "HANDOFF.md").write_text(
            "# Handoff Log\n\n"
            "> Per the preamble, Resolved entries leave under prune-on-resolve.\n"
            "> Past sections marked **Resolved:** are pruned in interactive sessions.\n"
            "\n## Item\n\n**Resolved:** S-0050 — landed.\n"
        )
        r = validate.validate_handoff_long_resolved_sections(
            repo_root=tmp_path, current_session_id="S-0055"
        )
        # Only 1 actual section-marker should match; preamble prose does not.
        assert r.soft_warns == {}  # count under threshold, age under threshold


# ---------------------------------------------------------------------------
# validate_uv_lock_freshness (ADR 0064, Issue #65)
# ---------------------------------------------------------------------------


class TestValidateUvLockFreshness:
    """`uv lock --check` staleness gate per ADR 0064.

    Verified shapes:
    - missing pyproject.toml → no-op (project hasn't adopted)
    - missing uv.lock → no-op (project hasn't adopted)
    - missing uv binary on PATH → no-op (clone hasn't installed prereqs)
    - both files present + uv available + clean → no soft-warn
    - both files present + uv available + stale → uv_lock_out_of_date soft-warn
    """

    def test_absent_pyproject_returns_clean(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # Neither pyproject nor uv.lock exists.
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert r.soft_warns == {}
        assert "uv_lock_out_of_date" in r.checks_run

    def test_absent_lockfile_returns_clean(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n'
        )
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert r.soft_warns == {}

    def test_uv_binary_missing_returns_clean(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n'
        )
        (tmp_path / "uv.lock").write_text("# placeholder lock\n")
        # shutil.which returns None for any binary lookup.
        monkeypatch.setattr("shutil.which", lambda _name: None)
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert r.soft_warns == {}

    def test_clean_lock_no_warn(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n'
        )
        (tmp_path / "uv.lock").write_text("# placeholder lock\n")
        # Stub uv binary present + uv lock --check returning 0.
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/uv" if name == "uv" else None
        )
        completed = subprocess.CompletedProcess(
            args=["uv", "lock", "--check"], returncode=0, stdout="", stderr=""
        )
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: completed)
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert r.soft_warns == {}

    def test_stale_lock_fires_soft_warn(self, tmp_path: Path, monkeypatch: Any) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n'
        )
        (tmp_path / "uv.lock").write_text("# stale lock\n")
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/uv" if name == "uv" else None
        )
        completed = subprocess.CompletedProcess(
            args=["uv", "lock", "--check"],
            returncode=1,
            stdout="",
            stderr="lockfile out of date",
        )
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: completed)
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert "uv_lock_out_of_date" in r.soft_warns
        assert len(r.soft_warns["uv_lock_out_of_date"]) == 1
        assert "uv lock" in r.soft_warns["uv_lock_out_of_date"][0]

    def test_subprocess_timeout_returns_clean(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        """Timeout is treated as a no-op (returns clean) rather than a warn —
        the gate cannot distinguish 'lockfile stale' from 'uv hung,' and
        falsely flagging on transient subprocess failure would erode trust
        in the warn category."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n'
        )
        (tmp_path / "uv.lock").write_text("# placeholder lock\n")
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/uv" if name == "uv" else None
        )

        def _raise_timeout(*args: Any, **kwargs: Any) -> Any:
            raise subprocess.TimeoutExpired(cmd="uv lock --check", timeout=30)

        monkeypatch.setattr(subprocess, "run", _raise_timeout)
        r = validate.validate_uv_lock_freshness(repo_root=tmp_path)
        assert r.soft_warns == {}


# ---------------------------------------------------------------------------
# validate_dependabot_pr_stale (ADR 0080 engine, S-0147)
# ---------------------------------------------------------------------------


class TestValidateDependabotPrStale:
    """Per-PR soft-warn for Dependabot PRs aged ≥ 7 days.

    Verified shapes:
    - gh binary missing → no-op
    - gh fails (returns None) → no-op
    - no open PRs → no-op
    - all PRs fresh → no soft-warn
    - one stale PR → one soft-warn
    - multiple stale PRs → multiple soft-warns
    - threshold boundary (exactly 7d) → fires
    """

    def _make_scanner_stub(self, prs: list[dict[str, Any]]) -> object:
        """Return an object that quacks like the scan_dependabot_prs module."""
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        class _Stub:
            @staticmethod
            def fetch_open_prs(repo: Any = None) -> list[dict[str, Any]]:
                return prs

            @staticmethod
            def age_days(created_at: str, now: Any = None) -> int:
                now = now or _dt.now(_tz.utc)
                created = _dt.fromisoformat(created_at.replace("Z", "+00:00"))
                return int((now - created).days)

            @staticmethod
            def next_action_hint(pr: dict[str, Any]) -> str:
                return "test-hint"

        return _Stub()

    def _pr(self, num: int, days_old: int, title: str = "test") -> dict[str, Any]:
        from datetime import datetime as _dt
        from datetime import timedelta, timezone as _tz

        created = (
            (_dt.now(_tz.utc) - timedelta(days=days_old))
            .isoformat()
            .replace("+00:00", "Z")
        )
        return {
            "number": num,
            "title": title,
            "createdAt": created,
            "mergeable": "MERGEABLE",
            "headRefName": "dependabot/pip/foo",
        }

    def test_gh_missing_returns_clean(self, monkeypatch: Any) -> None:
        monkeypatch.setattr("shutil.which", lambda _name: None)
        r = validate.validate_dependabot_pr_stale()
        assert r.soft_warns == {}
        assert "dependabot_pr_stale" in r.checks_run

    def test_no_open_prs_returns_clean(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )
        stub = self._make_scanner_stub([])
        r = validate.validate_dependabot_pr_stale(_scanner_module=stub)
        assert r.soft_warns == {}

    def test_gh_fetch_failure_returns_clean(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )

        class _StubNone:
            @staticmethod
            def fetch_open_prs(repo: Any = None) -> Any:
                return None

        r = validate.validate_dependabot_pr_stale(_scanner_module=_StubNone())
        assert r.soft_warns == {}

    def test_fresh_prs_no_warn(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )
        stub = self._make_scanner_stub([self._pr(1, 1), self._pr(2, 3)])
        r = validate.validate_dependabot_pr_stale(_scanner_module=stub)
        assert r.soft_warns == {}

    def test_one_stale_pr_fires_one_warn(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )
        stub = self._make_scanner_stub(
            [self._pr(1, 1), self._pr(99, 10, title="stale")]
        )
        r = validate.validate_dependabot_pr_stale(_scanner_module=stub)
        assert "dependabot_pr_stale" in r.soft_warns
        assert len(r.soft_warns["dependabot_pr_stale"]) == 1
        assert "#99" in r.soft_warns["dependabot_pr_stale"][0]
        assert "10 days" in r.soft_warns["dependabot_pr_stale"][0]

    def test_multiple_stale_prs_fire_multiple_warns(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )
        stub = self._make_scanner_stub(
            [self._pr(1, 10), self._pr(2, 8), self._pr(3, 15)]
        )
        r = validate.validate_dependabot_pr_stale(_scanner_module=stub)
        assert "dependabot_pr_stale" in r.soft_warns
        assert len(r.soft_warns["dependabot_pr_stale"]) == 3

    def test_threshold_boundary_exactly_7d_fires(self, monkeypatch: Any) -> None:
        """7d is the threshold; >= fires (not strict >)."""
        monkeypatch.setattr(
            "shutil.which", lambda name: "/usr/bin/gh" if name == "gh" else None
        )
        stub = self._make_scanner_stub([self._pr(1, 7), self._pr(2, 6)])
        r = validate.validate_dependabot_pr_stale(_scanner_module=stub)
        assert "dependabot_pr_stale" in r.soft_warns
        assert len(r.soft_warns["dependabot_pr_stale"]) == 1
        assert "#1" in r.soft_warns["dependabot_pr_stale"][0]
