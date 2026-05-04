"""Tests for validate_routine_mode (per ADR 0051).

The function emits two soft-warns specific to routine-mode sessions:

- ``routine_no_target_reference`` when current_plan.md exists but
  doesn't mention the active task's id or name.
- ``routine_issue_spam`` when more than 3 GitHub issues were created
  since started_at (best-effort; silent on gh-tool failure).

Tests use monkeypatch to redirect ``validate.REPO_ROOT`` to a
synthetic tmp_path repo. Issue-spam tests stub ``subprocess.run`` to
avoid real network calls; the unit under test is the count threshold
and the silent-on-failure path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402


def _make_routine_repo(
    tmp_path: Path,
    *,
    plan_text: str = "paths_to_modify: []\ncriteria_addressed: [0]\n",
    target_tasks: list[dict[str, Any]] | None = None,
    started_at: str = "2026-05-04T00:00:00Z",
    omit_target: bool = False,
    omit_plan: bool = False,
    omit_current: bool = False,
) -> Path:
    """Build a synthetic routine-mode repo under tmp_path."""
    sess_dir = tmp_path / "engine" / "session"
    sess_dir.mkdir(parents=True)

    if not omit_target:
        target = {
            "target_id": "T",
            "goal": "g",
            "paused": False,
            "max_sessions": 10,
            "tasks": target_tasks
            or [
                {
                    "id": "T1",
                    "name": "first task",
                    "status": "in_progress",
                    "criteria": [],
                }
            ],
        }
        (sess_dir / "auto_target.json").write_text(json.dumps(target))

    if not omit_plan:
        (sess_dir / "current_plan.md").write_text(plan_text)

    if not omit_current:
        (sess_dir / "current.json").write_text(
            json.dumps(
                {"id": "S-0044", "started_at": started_at, "status": "in_progress"}
            )
        )

    return tmp_path


@pytest.fixture
def stub_no_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub subprocess.run so gh issue list returns zero issues."""

    def _fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="[]", stderr=""
        )

    monkeypatch.setattr("validate.subprocess.run", _fake_run)


@pytest.fixture
def stub_many_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub subprocess.run to return 4 issues all created after a fixed boundary."""

    def _fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        issues = [
            {"number": 100, "createdAt": "2026-05-04T01:00:00Z"},
            {"number": 101, "createdAt": "2026-05-04T02:00:00Z"},
            {"number": 102, "createdAt": "2026-05-04T03:00:00Z"},
            {"number": 103, "createdAt": "2026-05-04T04:00:00Z"},
        ]
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(issues), stderr=""
        )

    monkeypatch.setattr("validate.subprocess.run", _fake_run)


@pytest.fixture
def stub_gh_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub subprocess.run to raise FileNotFoundError (gh missing)."""

    def _fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("gh not on PATH")

    monkeypatch.setattr("validate.subprocess.run", _fake_run)


# ---------------------------------------------------------------------------
# Not-in-routine-mode → no-op
# ---------------------------------------------------------------------------


def test_no_target_file_is_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_no_target_reference" in r.checks_run
    assert r.soft_warns == {}


def test_no_plan_file_is_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(tmp_path, omit_plan=True)
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert r.soft_warns == {}


def test_no_in_progress_task_is_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        target_tasks=[{"id": "T1", "name": "n", "status": "complete", "criteria": []}],
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert r.soft_warns == {}


# ---------------------------------------------------------------------------
# routine_no_target_reference
# ---------------------------------------------------------------------------


def test_plan_references_task_id_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_no_target_reference" not in r.soft_warns


def test_plan_references_task_name_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="working on first task\npaths_to_modify: []\ncriteria_addressed: [0]\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_no_target_reference" not in r.soft_warns


def test_plan_no_reference_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="paths_to_modify: []\ncriteria_addressed: [0]\nrandom rationale\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_no_target_reference" in r.soft_warns
    assert any("'T1'" in m for m in r.soft_warns["routine_no_target_reference"])


# ---------------------------------------------------------------------------
# routine_issue_spam
# ---------------------------------------------------------------------------


def test_issue_count_under_threshold_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_no_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_issue_spam" not in r.soft_warns


def test_issue_count_over_threshold_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_many_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
        started_at="2026-05-04T00:00:00Z",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert "routine_issue_spam" in r.soft_warns
    msg = r.soft_warns["routine_issue_spam"][0]
    assert "4" in msg


def test_gh_unavailable_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_gh_unavailable: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    # gh failure should not crash and should not produce spam warn
    assert "routine_issue_spam" not in r.soft_warns


def test_issue_count_excludes_pre_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Issues created before started_at should not count, even if the
    date-prefix search would otherwise pull them in."""

    def _fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        # Issues all on the same day but earlier than started_at
        issues = [
            {
                "number": 100,
                "createdAt": "2026-05-04T00:00:00Z",
            },  # at started_at — included
            {"number": 101, "createdAt": "2026-05-04T01:00:00Z"},  # after — included
            {"number": 102, "createdAt": "2026-05-03T23:00:00Z"},  # before — excluded
            {"number": 103, "createdAt": "2026-05-03T22:00:00Z"},  # before — excluded
            {"number": 104, "createdAt": "2026-05-03T21:00:00Z"},  # before — excluded
        ]
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(issues), stderr=""
        )

    monkeypatch.setattr("validate.subprocess.run", _fake_run)
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
        started_at="2026-05-04T00:00:00Z",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    # Only 2 issues counted; under threshold of 3
    assert "routine_issue_spam" not in r.soft_warns


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------


def test_malformed_target_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sess_dir = tmp_path / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "auto_target.json").write_text("{not json")
    (sess_dir / "current_plan.md").write_text("anything")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    assert r.soft_warns == {}


def test_empty_started_at_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stub_many_issues: None
) -> None:
    _make_routine_repo(
        tmp_path,
        plan_text="addressing T1\npaths_to_modify: []\ncriteria_addressed: [0]\n",
        started_at="",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_routine_mode()
    # Empty started_at → check 2 skipped silently
    assert "routine_issue_spam" not in r.soft_warns
