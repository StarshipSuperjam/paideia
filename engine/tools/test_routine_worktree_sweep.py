"""Tests for routine_worktree_sweep.py — S-0072 Issue #16 follow-on.

Coverage:
- Successful sweep (worktree + branch removed).
- Dry-run reports without modifying state.
- Refusals: parent invocation, dirty working tree, non-claude/* branch,
  unmerged branch, detached HEAD.
- main() exit codes (0 success, 2 refused, 5 git error).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_worktree_sweep import (  # noqa: E402
    branch_merged_into_main,
    get_current_branch,
    get_parent_repo_path,
    main,
    preflight,
    working_tree_clean,
)


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin_with_clone(tmp_path: Path) -> tuple[Path, Path]:
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "init", "--bare", str(origin)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "clone", str(origin), str(clone)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)
    (clone / "README").write_text("init\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["branch", "-M", "main"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    return origin, clone


def _make_clone_with_worktree(
    tmp_path: Path, branch: str = "claude/test-worktree"
) -> tuple[Path, Path, Path]:
    """Origin + clone + linked worktree on `branch`."""
    origin, clone = _make_origin_with_clone(tmp_path)
    worktree = tmp_path / "worktree"
    _git(["worktree", "add", "-b", branch, str(worktree)], clone)
    _git(["config", "user.email", "test@example.com"], worktree)
    _git(["config", "user.name", "Test"], worktree)
    return origin, clone, worktree


def _merge_worktree_branch_into_main(clone: Path, branch: str) -> None:
    """FF main to the worktree's branch tip (simulates post-close-push state)."""
    _git(["merge", "--ff-only", branch], clone)


# ---------------------------------------------------------------------------
# Helper-function unit tests
# ---------------------------------------------------------------------------


def test_get_parent_repo_path_resolves_for_worktree(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    parent = get_parent_repo_path(worktree)
    assert parent is not None
    assert parent.resolve() == clone.resolve()


def test_get_current_branch_returns_branch(tmp_path: Path) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    assert get_current_branch(worktree) == "claude/test-worktree"


def test_get_current_branch_none_on_detached_head(tmp_path: Path) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    head_sha = _git(["rev-parse", "HEAD"], worktree).stdout.strip()
    _git(["checkout", "--detach", head_sha], worktree)
    assert get_current_branch(worktree) is None


def test_working_tree_clean_true_when_clean(tmp_path: Path) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    assert working_tree_clean(worktree) is True


def test_working_tree_clean_false_with_untracked_file(tmp_path: Path) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "scratch").write_text("x")
    assert working_tree_clean(worktree) is False


def test_branch_merged_into_main_true_when_merged(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    # Worktree's branch was created from main and hasn't diverged → ancestor.
    assert branch_merged_into_main(clone, "claude/test-worktree") is True


def test_branch_merged_into_main_false_when_diverged(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "feature").write_text("ahead\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: ahead"], worktree)
    # Worktree branch has a commit not in main → not ancestor.
    assert branch_merged_into_main(clone, "claude/test-worktree") is False


# ---------------------------------------------------------------------------
# Pre-flight tests
# ---------------------------------------------------------------------------


def test_preflight_ok_on_clean_merged_claude_branch(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    ok, reason, branch = preflight(worktree, clone)
    assert ok, reason
    assert branch == "claude/test-worktree"
    assert "preflight ok" in reason


def test_preflight_refuses_when_parent_equals_worktree(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    ok, reason, branch = preflight(clone, clone)
    assert not ok
    assert "parent repo" in reason
    assert branch is None


def test_preflight_refuses_on_non_claude_branch(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(
        tmp_path, branch="experiment/my-branch"
    )
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "not claude/*" in reason


def test_preflight_refuses_on_dirty_working_tree(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "scratch").write_text("x")
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "working tree dirty" in reason


def test_preflight_refuses_on_unmerged_branch(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "ahead").write_text("ahead\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: ahead"], worktree)
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "not merged into main" in reason


# ---------------------------------------------------------------------------
# main() end-to-end
# ---------------------------------------------------------------------------


def test_main_succeeds_and_removes_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    rc = main(["--worktree", str(worktree)])
    assert rc == 0

    captured = capsys.readouterr()
    assert "swept worktree" in captured.err

    # Worktree directory removed
    assert not worktree.exists()
    # Branch deleted
    branches = _git(["branch", "--list", "claude/test-worktree"], clone).stdout.strip()
    assert branches == ""


def test_main_dry_run_reports_without_removing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    rc = main(["--worktree", str(worktree), "--dry-run"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "dry-run" in captured.err
    assert "would remove" in captured.err
    # Worktree still present
    assert worktree.exists()


def test_main_returns_2_on_refusal_dirty_tree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "scratch").write_text("x")
    rc = main(["--worktree", str(worktree)])
    assert rc == 2

    captured = capsys.readouterr()
    assert "REFUSED" in captured.err
    assert "working tree dirty" in captured.err
    # Worktree still present
    assert worktree.exists()


def test_main_returns_2_when_called_in_parent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    rc = main(["--worktree", str(clone)])
    assert rc == 2

    captured = capsys.readouterr()
    assert "REFUSED" in captured.err
    assert "parent repo" in captured.err
    # Clone still present
    assert clone.exists()


def test_main_uses_cwd_when_worktree_not_specified(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main([])
    assert rc == 0

    captured = capsys.readouterr()
    assert "swept worktree" in captured.err
    assert not worktree.exists()


def test_main_chdirs_to_parent_before_sweep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After main() succeeds, CWD must be the parent — confirms the chdir
    happened, which is what makes the sweep safe (forks from the process
    after worktree removal would fail otherwise)."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main([])
    assert rc == 0
    # CWD should now be the parent (clone), not the removed worktree
    assert Path(os.getcwd()).resolve() == clone.resolve()
