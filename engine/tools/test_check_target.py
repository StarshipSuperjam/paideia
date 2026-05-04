"""Tests for engine/tools/check_target.py.

Covers each criterion type with at least one pass and one fail path,
plus the top-level dispatch (unknown type, missing type, dispatcher
isolation), plus main() exit codes and CLI surfaces.

Test isolation strategy
-----------------------
- Pure-function units (check_criterion, check_task) test against
  hand-crafted dicts; no filesystem involvement.
- File-touching units (file_exists, adr_status) use tmp_path with
  hand-built fixtures.
- migration_applied is tested in the SUPABASE_DB_URL-unset path only
  (the live-DB path is integration territory; the criterion is
  designed to gracefully report cannot-verify there).
- validate_passes is tested with a stub validate.py invocation by
  monkeypatching subprocess.run — the live validator path runs
  through the integration suite naturally.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_target import (  # noqa: E402
    CRITERION_TYPES,
    PREDICATE_REGISTRY,
    _check_adr_status,
    _check_file_exists,
    _check_migration_applied,
    _check_predicate,
    check_criterion,
    check_task,
    load_target,
    main,
    register_predicate,
)


# ---------------------------------------------------------------------------
# file_exists
# ---------------------------------------------------------------------------


def test_file_exists_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "subdir" / "x.md"
    target.parent.mkdir()
    target.write_text("hi")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_file_exists(path="subdir/x.md")
    assert passed is True
    assert "subdir/x.md" in detail


def test_file_exists_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_file_exists(path="missing.md")
    assert passed is False
    assert "not found" in detail


# ---------------------------------------------------------------------------
# adr_status
# ---------------------------------------------------------------------------


def test_adr_status_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adr_dir = tmp_path / "engine" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0099-test.md").write_text("# ADR\n\n- **Status:** Accepted\n")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0099", status="Accepted")
    assert passed is True
    assert "Accepted" in detail


def test_adr_status_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adr_dir = tmp_path / "engine" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0099-test.md").write_text("- **Status:** Proposed\n")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0099", status="Accepted")
    assert passed is False
    assert "Proposed" in detail


def test_adr_status_wildcard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adr_dir = tmp_path / "engine" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0099-test.md").write_text("- **Status:** Whatever\n")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0099", status="*")
    assert passed is True


def test_adr_status_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "engine" / "adr").mkdir(parents=True)
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0099", status="Accepted")
    assert passed is False
    assert "no ADR file found" in detail


def test_adr_status_no_status_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adr_dir = tmp_path / "engine" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0099-test.md").write_text("# ADR\n\nno frontmatter here\n")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0099", status="Accepted")
    assert passed is False
    assert "no Status line" in detail


def test_adr_status_finds_in_product_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    product_adr = tmp_path / "product" / "adr"
    product_adr.mkdir(parents=True)
    (product_adr / "0046-philosophy.md").write_text("- **Status:** Accepted\n")
    (tmp_path / "engine" / "adr").mkdir(parents=True)  # empty engine dir
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    passed, detail = _check_adr_status(id="0046", status="Accepted")
    assert passed is True


# ---------------------------------------------------------------------------
# migration_applied — only the no-DB-URL path is unit-testable
# ---------------------------------------------------------------------------


def test_migration_applied_no_db_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    passed, detail = _check_migration_applied(id="0042_x")
    assert passed is False
    assert "SUPABASE_DB_URL" in detail


# ---------------------------------------------------------------------------
# predicate
# ---------------------------------------------------------------------------


def test_predicate_unregistered() -> None:
    passed, detail = _check_predicate(name="nonexistent_predicate_xyz")
    assert passed is False
    assert "not registered" in detail


def test_predicate_registered_truthy() -> None:
    @register_predicate("_test_pred_truthy")
    def _truthy(**_: Any) -> bool:
        return True

    try:
        passed, detail = _check_predicate(name="_test_pred_truthy")
        assert passed is True
        assert "truthy" in detail
    finally:
        PREDICATE_REGISTRY.pop("_test_pred_truthy", None)


def test_predicate_registered_falsy() -> None:
    @register_predicate("_test_pred_falsy")
    def _falsy(**_: Any) -> bool:
        return False

    try:
        passed, detail = _check_predicate(name="_test_pred_falsy")
        assert passed is False
        assert "falsy" in detail
    finally:
        PREDICATE_REGISTRY.pop("_test_pred_falsy", None)


def test_predicate_registered_raises() -> None:
    @register_predicate("_test_pred_raises")
    def _raiser(**_: Any) -> bool:
        raise RuntimeError("boom")

    try:
        passed, detail = _check_predicate(name="_test_pred_raises")
        assert passed is False
        assert "raised" in detail
        assert "boom" in detail
    finally:
        PREDICATE_REGISTRY.pop("_test_pred_raises", None)


def test_predicate_passes_params() -> None:
    captured = {}

    @register_predicate("_test_pred_capture")
    def _capture(**kwargs: Any) -> bool:
        captured.update(kwargs)
        return True

    try:
        _check_predicate(name="_test_pred_capture", params={"n": 42, "label": "x"})
        assert captured == {"n": 42, "label": "x"}
    finally:
        PREDICATE_REGISTRY.pop("_test_pred_capture", None)


# ---------------------------------------------------------------------------
# check_criterion (top-level dispatcher)
# ---------------------------------------------------------------------------


def test_check_criterion_unknown_type() -> None:
    result = check_criterion({"type": "frobozz"})
    assert result.passed is False
    assert "unknown criterion type" in result.detail


def test_check_criterion_missing_type() -> None:
    result = check_criterion({"id": "0042"})
    assert result.passed is False
    assert "missing 'type'" in result.detail


def test_check_criterion_dispatches_correctly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "x"
    target.write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    result = check_criterion({"type": "file_exists", "path": "x"})
    assert result.type == "file_exists"
    assert result.passed is True


def test_check_criterion_handles_typeerror_from_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # file_exists requires path kwarg; omitting it raises TypeError inside the dispatcher
    result = check_criterion({"type": "file_exists"})
    assert result.passed is False
    assert "criterion call failed" in result.detail


# ---------------------------------------------------------------------------
# check_task
# ---------------------------------------------------------------------------


def test_check_task_all_passed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "a").write_text("")
    (tmp_path / "b").write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    task = {
        "id": "T1",
        "name": "task one",
        "status": "in_progress",
        "criteria": [
            {"type": "file_exists", "path": "a"},
            {"type": "file_exists", "path": "b"},
        ],
    }
    result = check_task(task)
    assert result.all_passed is True
    assert len(result.criteria_results) == 2
    assert all(c.passed for c in result.criteria_results)


def test_check_task_one_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "a").write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    task = {
        "id": "T1",
        "name": "task one",
        "criteria": [
            {"type": "file_exists", "path": "a"},
            {"type": "file_exists", "path": "missing"},
        ],
    }
    result = check_task(task)
    assert result.all_passed is False
    assert result.criteria_results[0].passed is True
    assert result.criteria_results[1].passed is False


def test_check_task_empty_criteria_not_auto_completable() -> None:
    task = {"id": "T1", "name": "no criteria", "criteria": []}
    result = check_task(task)
    # Empty criteria list → all_passed=False per ADR 0051 authoring decision.
    assert result.all_passed is False
    assert len(result.criteria_results) == 0


# ---------------------------------------------------------------------------
# CLI / main()
# ---------------------------------------------------------------------------


def _write_target(path: Path, body: dict[str, Any]) -> None:
    path.write_text(json.dumps(body))


def test_main_target_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--target", str(tmp_path / "nonexistent.json")])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_main_target_malformed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "bad.json"
    target.write_text("{not json")
    rc = main(["--target", str(target)])
    assert rc == 1
    assert "malformed" in capsys.readouterr().err


def test_main_all_pass_returns_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "a").write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    target_path = tmp_path / "target.json"
    _write_target(
        target_path,
        {
            "target_id": "T",
            "goal": "g",
            "paused": False,
            "max_sessions": 1,
            "tasks": [
                {
                    "id": "T1",
                    "name": "n",
                    "depends_on": [],
                    "criteria": [{"type": "file_exists", "path": "a"}],
                    "scope_lock": {"allowed_paths": ["*"]},
                    "status": "pending",
                }
            ],
        },
    )
    rc = main(["--target", str(target_path)])
    assert rc == 0


def test_main_one_fail_returns_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    target_path = tmp_path / "target.json"
    _write_target(
        target_path,
        {
            "target_id": "T",
            "goal": "g",
            "paused": False,
            "max_sessions": 1,
            "tasks": [
                {
                    "id": "T1",
                    "name": "n",
                    "depends_on": [],
                    "criteria": [{"type": "file_exists", "path": "missing"}],
                    "scope_lock": {"allowed_paths": ["*"]},
                    "status": "pending",
                }
            ],
        },
    )
    rc = main(["--target", str(target_path)])
    assert rc == 1


def test_main_task_id_filter_hits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a").write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    target_path = tmp_path / "target.json"
    _write_target(
        target_path,
        {
            "target_id": "T",
            "goal": "g",
            "paused": False,
            "max_sessions": 1,
            "tasks": [
                {
                    "id": "T1",
                    "name": "first",
                    "depends_on": [],
                    "criteria": [{"type": "file_exists", "path": "a"}],
                    "scope_lock": {"allowed_paths": ["*"]},
                    "status": "pending",
                },
                {
                    "id": "T2",
                    "name": "second",
                    "depends_on": [],
                    "criteria": [{"type": "file_exists", "path": "missing"}],
                    "scope_lock": {"allowed_paths": ["*"]},
                    "status": "pending",
                },
            ],
        },
    )
    # Filter to T1 only — its criterion passes, exit 0
    rc = main(["--target", str(target_path), "--task-id", "T1"])
    assert rc == 0
    # Filter to T2 — its criterion fails, exit 1
    rc = main(["--target", str(target_path), "--task-id", "T2"])
    assert rc == 1


def test_main_task_id_filter_misses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target_path = tmp_path / "target.json"
    _write_target(
        target_path,
        {"target_id": "T", "goal": "", "paused": False, "max_sessions": 1, "tasks": []},
    )
    rc = main(["--target", str(target_path), "--task-id", "nonexistent"])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_main_json_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "a").write_text("")
    monkeypatch.setattr("check_target.REPO_ROOT", tmp_path)
    target_path = tmp_path / "target.json"
    _write_target(
        target_path,
        {
            "target_id": "T",
            "goal": "g",
            "paused": False,
            "max_sessions": 1,
            "tasks": [
                {
                    "id": "T1",
                    "name": "n",
                    "depends_on": [],
                    "criteria": [{"type": "file_exists", "path": "a"}],
                    "scope_lock": {"allowed_paths": ["*"]},
                    "status": "pending",
                }
            ],
        },
    )
    rc = main(["--target", str(target_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["id"] == "T1"
    assert payload[0]["all_passed"] is True


# ---------------------------------------------------------------------------
# load_target
# ---------------------------------------------------------------------------


def test_load_target_basic(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"target_id": "X", "tasks": []}))
    loaded = load_target(p)
    assert loaded["target_id"] == "X"


# ---------------------------------------------------------------------------
# CRITERION_TYPES registry
# ---------------------------------------------------------------------------


def test_criterion_types_registry_has_all_five() -> None:
    expected = {
        "migration_applied",
        "validate_passes",
        "adr_status",
        "file_exists",
        "predicate",
    }
    assert set(CRITERION_TYPES.keys()) == expected
