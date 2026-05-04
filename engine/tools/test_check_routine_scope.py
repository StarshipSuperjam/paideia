"""Tests for engine/tools/check_routine_scope.py.

Covers path matching, mode detection, plan parsing, and the three
checks (plan, staged, master-plan integrity), plus main() exit codes.

Test isolation strategy
-----------------------
- Pure-function units (path_matches, parse_plan, _allowed_patterns_for,
  check_plan, check_staged, check_master_plan_integrity) test against
  hand-crafted dicts and strings — no filesystem or git involvement.
- Filesystem units (detect_mode) use tmp_path with hand-written files.
- Git-touching units (get_staged_files, get_target_diff) build a real
  tmp_path git repo with hand-staged content via subprocess; the
  conftest.py autouse _scrub_git_env fixture protects against parent
  GIT_* leakage.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_routine_scope import (  # noqa: E402
    OPERATIONAL_ALLOWLIST,
    PlanContents,
    _allowed_patterns_for,
    check_master_plan_integrity,
    check_plan,
    check_staged,
    detect_mode,
    main,
    matches_any,
    parse_plan,
    path_matches,
)


# ---------------------------------------------------------------------------
# path_matches
# ---------------------------------------------------------------------------


def test_path_matches_literal() -> None:
    assert path_matches("HANDOFF.md", "HANDOFF.md") is True
    assert path_matches("HANDOFF.md", "OTHER.md") is False


def test_path_matches_single_star_within_segment() -> None:
    assert (
        path_matches("engine/migrations/0042_x.sql", "engine/migrations/0042_*") is True
    )
    assert (
        path_matches("engine/migrations/0043_x.sql", "engine/migrations/0042_*")
        is False
    )


def test_path_matches_single_star_does_not_cross_slash() -> None:
    # With segment-aware matching, * within a segment does NOT cross /
    assert (
        path_matches("engine/migrations/sub/x.sql", "engine/migrations/0042_*") is False
    )


def test_path_matches_double_star() -> None:
    assert path_matches("a/b/c/d.md", "a/**/d.md") is True
    assert path_matches("a/d.md", "a/**/d.md") is True  # ** matches zero segments
    assert path_matches("a/x/d.md", "a/**/d.md") is True
    assert path_matches("a/b/c/e.md", "a/**/d.md") is False


def test_path_matches_double_star_at_end() -> None:
    assert path_matches("a/b/c", "a/**") is True
    assert path_matches("a", "a/**") is True


def test_path_matches_session_archive_pattern() -> None:
    assert (
        path_matches(
            "engine/session/archive/S-0044.json", "engine/session/archive/S-*.json"
        )
        is True
    )
    assert (
        path_matches(
            "engine/session/archive/S-0044/x.json", "engine/session/archive/S-*.json"
        )
        is False
    )


def test_matches_any() -> None:
    patterns = ["a.md", "engine/migrations/*"]
    assert matches_any("a.md", patterns) is True
    assert matches_any("engine/migrations/x.sql", patterns) is True
    assert matches_any("engine/foo/x.sql", patterns) is False


# ---------------------------------------------------------------------------
# detect_mode
# ---------------------------------------------------------------------------


def _write_target(repo_root: Path, body: dict[str, Any]) -> Path:
    target_dir = repo_root / "engine" / "session"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "auto_target.json"
    target_path.write_text(json.dumps(body))
    return target_path


def _write_plan(
    repo_root: Path, body: str = "paths_to_modify: []\ncriteria_addressed: []\n"
) -> Path:
    plan_dir = repo_root / "engine" / "session"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plan_dir / "current_plan.md"
    plan_path.write_text(body)
    return plan_path


def test_detect_mode_no_target(tmp_path: Path) -> None:
    ctx = detect_mode(tmp_path)
    assert ctx.in_routine_mode is False
    assert "absent" in ctx.reason_not_routine


def test_detect_mode_no_plan(tmp_path: Path) -> None:
    _write_target(tmp_path, {"tasks": [{"id": "T1", "status": "in_progress"}]})
    ctx = detect_mode(tmp_path)
    assert ctx.in_routine_mode is False
    assert "current_plan.md absent" in ctx.reason_not_routine


def test_detect_mode_no_in_progress_task(tmp_path: Path) -> None:
    _write_target(tmp_path, {"tasks": [{"id": "T1", "status": "complete"}]})
    _write_plan(tmp_path)
    ctx = detect_mode(tmp_path)
    assert ctx.in_routine_mode is False
    assert "no in_progress task" in ctx.reason_not_routine


def test_detect_mode_active(tmp_path: Path) -> None:
    _write_target(
        tmp_path,
        {
            "tasks": [
                {"id": "T1", "status": "complete"},
                {"id": "T2", "status": "in_progress"},
            ]
        },
    )
    _write_plan(tmp_path)
    ctx = detect_mode(tmp_path)
    assert ctx.in_routine_mode is True
    assert ctx.active_task is not None
    assert ctx.active_task["id"] == "T2"


def test_detect_mode_malformed_target(tmp_path: Path) -> None:
    target_dir = tmp_path / "engine" / "session"
    target_dir.mkdir(parents=True)
    (target_dir / "auto_target.json").write_text("{not json")
    _write_plan(tmp_path)
    ctx = detect_mode(tmp_path)
    assert ctx.in_routine_mode is False
    assert "malformed" in ctx.reason_not_routine


# ---------------------------------------------------------------------------
# parse_plan
# ---------------------------------------------------------------------------


def test_parse_plan_basic() -> None:
    text = """# Plan
paths_to_modify: ["engine/migrations/0042_x.sql", "build_plan/foo.md"]
criteria_addressed: [0, 1]
Some prose rationale.
"""
    parsed = parse_plan(text)
    assert parsed.paths_to_modify == [
        "engine/migrations/0042_x.sql",
        "build_plan/foo.md",
    ]
    assert parsed.criteria_addressed == ["0", "1"]


def test_parse_plan_empty_lists() -> None:
    text = "paths_to_modify: []\ncriteria_addressed: []\n"
    parsed = parse_plan(text)
    assert parsed.paths_to_modify == []
    assert parsed.criteria_addressed == []


def test_parse_plan_missing_fields() -> None:
    parsed = parse_plan("just rationale\n")
    assert parsed.paths_to_modify == []
    assert parsed.criteria_addressed == []


def test_parse_plan_single_quoted() -> None:
    parsed = parse_plan("paths_to_modify: ['a.md']\ncriteria_addressed: ['0']\n")
    assert parsed.paths_to_modify == ["a.md"]
    assert parsed.criteria_addressed == ["0"]


# ---------------------------------------------------------------------------
# check_plan
# ---------------------------------------------------------------------------


def test_check_plan_pass() -> None:
    task = {"scope_lock": {"allowed_paths": ["engine/migrations/0042_*"]}}
    plan = PlanContents(
        paths_to_modify=[
            "engine/migrations/0042_x.sql",
            "HANDOFF.md",
        ],  # second is operational
        criteria_addressed=["0"],
    )
    violations = check_plan(plan, task)
    assert violations == []


def test_check_plan_out_of_scope_path() -> None:
    task = {"scope_lock": {"allowed_paths": ["engine/migrations/0042_*"]}}
    plan = PlanContents(
        paths_to_modify=["engine/adr/9999-rogue.md"], criteria_addressed=["0"]
    )
    violations = check_plan(plan, task)
    assert len(violations) == 1
    assert violations[0].kind == "out_of_scope"
    assert "9999-rogue" in violations[0].detail


def test_check_plan_no_criteria_addressed() -> None:
    task = {"scope_lock": {"allowed_paths": ["*.md"]}}
    plan = PlanContents(paths_to_modify=["x.md"], criteria_addressed=[])
    violations = check_plan(plan, task)
    assert any(v.kind == "no_criteria_addressed" for v in violations)


def test_check_plan_operational_paths_always_allowed() -> None:
    task: dict[str, Any] = {
        "scope_lock": {"allowed_paths": []}
    }  # nothing in scope_lock
    plan = PlanContents(
        paths_to_modify=list(OPERATIONAL_ALLOWLIST[:3]), criteria_addressed=["0"]
    )
    # Adjust the glob pattern in OPERATIONAL_ALLOWLIST that has * so it matches a concrete path
    # (e.g., "engine/session/archive/S-*.json" — substitute for a concrete instance).
    plan.paths_to_modify = [
        "engine/session/current.json",
        "engine/session/auto_target.json",
        "HANDOFF.md",
    ]
    violations = check_plan(plan, task)
    assert violations == []


# ---------------------------------------------------------------------------
# check_staged
# ---------------------------------------------------------------------------


def test_check_staged_pass() -> None:
    task = {"scope_lock": {"allowed_paths": ["engine/migrations/0042_*"]}}
    staged = ["engine/migrations/0042_x.sql", "engine/session/auto_target.json"]
    violations = check_staged(staged, task)
    assert violations == []


def test_check_staged_rejects_out_of_scope() -> None:
    task = {"scope_lock": {"allowed_paths": ["engine/migrations/0042_*"]}}
    staged = ["engine/adr/9999-rogue.md"]
    violations = check_staged(staged, task)
    assert len(violations) == 1
    assert violations[0].kind == "out_of_scope"


# ---------------------------------------------------------------------------
# _allowed_patterns_for
# ---------------------------------------------------------------------------


def test_allowed_patterns_unions_scope_and_operational() -> None:
    task = {"scope_lock": {"allowed_paths": ["foo/*"]}}
    patterns = _allowed_patterns_for(task)
    assert "foo/*" in patterns
    for op in OPERATIONAL_ALLOWLIST:
        assert op in patterns


def test_allowed_patterns_handles_missing_scope_lock() -> None:
    task: dict[str, Any] = {}
    patterns = _allowed_patterns_for(task)
    # Just the operational allowlist
    assert set(patterns) == set(OPERATIONAL_ALLOWLIST)


# ---------------------------------------------------------------------------
# check_master_plan_integrity
# ---------------------------------------------------------------------------


def _target_with(tasks: list[dict[str, Any]], **top_fields: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "target_id": "T",
        "goal": "g",
        "paused": False,
        "max_sessions": 10,
        "tasks": tasks,
    }
    body.update(top_fields)
    return body


def test_master_plan_integrity_status_only_pass() -> None:
    head = _target_with(
        [{"id": "T1", "status": "pending", "name": "n", "criteria": []}]
    )
    staged = _target_with(
        [{"id": "T1", "status": "in_progress", "name": "n", "criteria": []}]
    )
    assert check_master_plan_integrity(head, staged) == []


def test_master_plan_integrity_blocked_reason_added_pass() -> None:
    head = _target_with(
        [{"id": "T1", "status": "in_progress", "name": "n", "criteria": []}]
    )
    staged = _target_with(
        [
            {
                "id": "T1",
                "status": "blocked",
                "blocked_reason": "x",
                "name": "n",
                "criteria": [],
            }
        ]
    )
    assert check_master_plan_integrity(head, staged) == []


def test_master_plan_integrity_top_level_change_fails() -> None:
    head = _target_with(
        [{"id": "T1", "status": "pending", "name": "n", "criteria": []}], goal="g"
    )
    staged = _target_with(
        [{"id": "T1", "status": "in_progress", "name": "n", "criteria": []}],
        goal="GOAL_CHANGED",
    )
    violations = check_master_plan_integrity(head, staged)
    assert len(violations) == 1
    assert "goal" in violations[0].detail


def test_master_plan_integrity_task_field_change_fails() -> None:
    head = _target_with(
        [{"id": "T1", "status": "pending", "name": "old", "criteria": []}]
    )
    staged = _target_with(
        [{"id": "T1", "status": "in_progress", "name": "NEW", "criteria": []}]
    )
    violations = check_master_plan_integrity(head, staged)
    assert len(violations) == 1
    assert "name" in violations[0].detail


def test_master_plan_integrity_task_added_fails() -> None:
    head = _target_with([{"id": "T1", "status": "pending"}])
    staged = _target_with(
        [{"id": "T1", "status": "pending"}, {"id": "T2", "status": "pending"}]
    )
    violations = check_master_plan_integrity(head, staged)
    assert len(violations) == 1
    assert "task id set changed" in violations[0].detail


def test_master_plan_integrity_first_introduction_blocked() -> None:
    staged = _target_with([{"id": "T1", "status": "pending"}])
    violations = check_master_plan_integrity(None, staged)
    assert len(violations) == 1
    assert "newly added" in violations[0].detail


def test_master_plan_integrity_no_diff_no_violations() -> None:
    # No staged target → no violations to emit
    assert check_master_plan_integrity({"tasks": []}, None) == []


# ---------------------------------------------------------------------------
# main() — uses real git repos in tmp_path
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo_with_target(tmp_path: Path, tasks: list[dict[str, Any]]) -> Path:
    """Create a git repo with auto_target.json + current_plan.md committed at HEAD."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "test@test"], repo)
    _git(["config", "user.name", "test"], repo)
    _git(["config", "commit.gpgsign", "false"], repo)

    target_dir = repo / "engine" / "session"
    target_dir.mkdir(parents=True)
    target_body = {
        "target_id": "T",
        "goal": "g",
        "paused": False,
        "max_sessions": 10,
        "tasks": tasks,
    }
    (target_dir / "auto_target.json").write_text(json.dumps(target_body))
    (target_dir / "current_plan.md").write_text(
        "paths_to_modify: []\ncriteria_addressed: []\n"
    )
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "initial"], repo)
    return repo


def test_main_not_in_routine_mode(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--staged", "--repo-root", str(tmp_path)])
    assert rc == 0
    assert "not in routine mode" in capsys.readouterr().err


def test_main_plan_pass(tmp_path: Path) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["src/*.py"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    plan = repo / "plan.md"
    plan.write_text('paths_to_modify: ["src/foo.py"]\ncriteria_addressed: [0]\n')
    rc = main(["--plan", str(plan), "--repo-root", str(repo)])
    assert rc == 0


def test_main_plan_out_of_scope(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["src/*.py"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    plan = repo / "plan.md"
    plan.write_text('paths_to_modify: ["other/rogue.md"]\ncriteria_addressed: [0]\n')
    rc = main(["--plan", str(plan), "--repo-root", str(repo)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "out_of_scope" in err


def test_main_staged_pass(tmp_path: Path) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["src/*.py"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    src = repo / "src"
    src.mkdir()
    (src / "foo.py").write_text("# in-scope\n")
    _git(["add", "src/foo.py"], repo)
    rc = main(["--staged", "--repo-root", str(repo)])
    assert rc == 0


def test_main_staged_out_of_scope_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["src/*.py"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    rogue = repo / "rogue.md"
    rogue.write_text("nope\n")
    _git(["add", "rogue.md"], repo)
    rc = main(["--staged", "--repo-root", str(repo)])
    assert rc == 1
    assert "out_of_scope" in capsys.readouterr().err


def test_main_staged_master_plan_integrity_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["*"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    # Modify a non-status field of auto_target.json
    target_path = repo / "engine" / "session" / "auto_target.json"
    body = json.loads(target_path.read_text())
    body["goal"] = "CHANGED"
    target_path.write_text(json.dumps(body))
    _git(["add", "engine/session/auto_target.json"], repo)
    rc = main(["--staged", "--repo-root", str(repo)])
    assert rc == 1
    assert "master_plan_non_status" in capsys.readouterr().err


def test_main_staged_master_plan_status_only_passes(tmp_path: Path) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["*"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    # Status-only change is permitted
    target_path = repo / "engine" / "session" / "auto_target.json"
    body = json.loads(target_path.read_text())
    body["tasks"][0]["status"] = "complete"
    target_path.write_text(json.dumps(body))
    _git(["add", "engine/session/auto_target.json"], repo)
    rc = main(["--staged", "--repo-root", str(repo)])
    assert rc == 0


def test_main_plan_file_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["*"]},
                "criteria": [{"type": "x"}],
            }
        ],
    )
    rc = main(["--plan", str(repo / "nonexistent.md"), "--repo-root", str(repo)])
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_main_task_id_override(tmp_path: Path) -> None:
    repo = _init_repo_with_target(
        tmp_path,
        [
            {
                "id": "T1",
                "status": "complete",
                "scope_lock": {"allowed_paths": ["a/*"]},
                "criteria": [{"type": "x"}],
            },
            {
                "id": "T2",
                "status": "in_progress",
                "scope_lock": {"allowed_paths": ["b/*"]},
                "criteria": [{"type": "x"}],
            },
        ],
    )
    plan = repo / "plan.md"
    plan.write_text('paths_to_modify: ["a/foo.md"]\ncriteria_addressed: [0]\n')
    # Without override → uses T2 (in_progress); a/foo.md is out of scope
    rc = main(["--plan", str(plan), "--repo-root", str(repo)])
    assert rc == 1
    # With override → uses T1; a/foo.md is in scope
    rc = main(["--plan", str(plan), "--task-id", "T1", "--repo-root", str(repo)])
    assert rc == 0
