"""Tests for routine_worktree_sweep.py.

Coverage:
- Successful sweep (worktree + branch removed).
- Dry-run reports without modifying state.
- Refusals: parent invocation, dirty working tree, non-claude/* branch,
  unmerged branch, detached HEAD, caller's-own-worktree default
  (ADR 0076 Amendment v2).
- main() exit codes (0 success, 2 refused, 5 git error).
- collect_preserve_info / format_preserve_report — structured report shape
  per ADR 0076 Amendment v2.
- --allow-caller-self opt-in restores legacy self-sweep semantics.
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
    collect_preserve_info,
    format_preserve_report,
    get_current_branch,
    get_parent_repo_path,
    is_caller_self,
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
    assert branch_merged_into_main(clone, "claude/test-worktree") is True


def test_branch_merged_into_main_false_when_diverged(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "feature").write_text("ahead\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: ahead"], worktree)
    assert branch_merged_into_main(clone, "claude/test-worktree") is False


def test_is_caller_self_true_when_cwd_equals_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    assert is_caller_self(worktree) is True


def test_is_caller_self_false_when_cwd_differs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    assert is_caller_self(worktree) is False


# ---------------------------------------------------------------------------
# Pre-flight tests
# ---------------------------------------------------------------------------


def test_preflight_ok_on_clean_merged_claude_branch_from_other_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)  # caller NOT in worktree
    ok, reason, branch = preflight(worktree, clone)
    assert ok, reason
    assert branch == "claude/test-worktree"
    assert "preflight ok" in reason


def test_preflight_refuses_caller_self_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    ok, reason, branch = preflight(worktree, clone)
    assert not ok
    assert "caller's own worktree" in reason
    assert branch is None


def test_preflight_allows_caller_self_with_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    ok, reason, branch = preflight(worktree, clone, allow_caller_self=True)
    assert ok, reason
    assert branch == "claude/test-worktree"


def test_preflight_refuses_when_parent_equals_worktree(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    ok, reason, branch = preflight(clone, clone)
    assert not ok
    assert "parent repo" in reason
    assert branch is None


def test_preflight_refuses_on_non_claude_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(
        tmp_path, branch="experiment/my-branch"
    )
    monkeypatch.chdir(clone)
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "not claude/*" in reason


def test_preflight_refuses_on_dirty_working_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    (worktree / "scratch").write_text("x")
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "working tree dirty" in reason


def test_preflight_refuses_on_unmerged_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    (worktree / "ahead").write_text("ahead\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: ahead"], worktree)
    ok, reason, _branch = preflight(worktree, clone)
    assert not ok
    assert "not merged into main" in reason


# ---------------------------------------------------------------------------
# collect_preserve_info / format_preserve_report
# ---------------------------------------------------------------------------


def test_collect_preserve_info_clean_merged_worktree(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    assert info["path"] == str(worktree)
    assert info["branch"] == "claude/test-worktree"
    assert info["merged"] == "yes"
    assert info["ahead_main"] == "0"
    assert info["behind_main"] == "0"
    assert info["dirty_files"] == "(clean)"
    assert "initial" in info["last_commit"] or "|" in info["last_commit"]


def test_collect_preserve_info_dirty_worktree_lists_files(tmp_path: Path) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "scratch").write_text("x")
    (worktree / "another").write_text("y")
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    assert info["dirty_files"] != "(clean)"
    assert "scratch" in info["dirty_files"]
    assert "another" in info["dirty_files"]


def test_collect_preserve_info_dirty_worktree_truncates_after_5(
    tmp_path: Path,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    for i in range(8):
        (worktree / f"file_{i}").write_text("x")
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    assert "more)" in info["dirty_files"]
    assert "+3 more" in info["dirty_files"]


def test_format_preserve_report_caller_self_carries_followup_guidance(
    tmp_path: Path,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    report = format_preserve_report(
        info, "caller's own worktree", is_caller_self_refusal=True
    )
    assert "PRESERVED" in report
    assert "caller's own worktree preserved for follow-up" in report
    assert "boot-time bulk sweep" in report


def test_format_preserve_report_dirty_tree_carries_checkout_guidance(
    tmp_path: Path,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "scratch").write_text("x")
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    report = format_preserve_report(info, "working tree dirty")
    assert "review files" in report
    assert "checkout ." in report
    assert "git worktree remove" in report


def test_format_preserve_report_unmerged_branch_carries_investigate_guidance(
    tmp_path: Path,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    (worktree / "ahead").write_text("ahead\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: ahead"], worktree)
    info = collect_preserve_info(clone, worktree, "claude/test-worktree")
    report = format_preserve_report(info, "branch not merged")
    assert "unmerged commit" in report
    assert "investigate" in report


# ---------------------------------------------------------------------------
# main() end-to-end
# ---------------------------------------------------------------------------


def test_main_succeeds_from_outside_worktree(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default behavior: invoke from outside the target worktree → succeeds."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    rc = main(["--worktree", str(worktree)])
    assert rc == 0

    captured = capsys.readouterr()
    assert "swept worktree" in captured.err

    assert not worktree.exists()
    branches = _git(["branch", "--list", "claude/test-worktree"], clone).stdout.strip()
    assert branches == ""


def test_main_dry_run_reports_without_removing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    rc = main(["--worktree", str(worktree), "--dry-run"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "dry-run" in captured.err
    assert "would remove" in captured.err
    assert worktree.exists()


def test_main_returns_2_on_caller_self_default(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ADR 0076 Amendment v2: caller's own worktree refused by default."""
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main([])
    assert rc == 2

    captured = capsys.readouterr()
    assert "PRESERVED" in captured.err
    assert "caller's own worktree" in captured.err
    assert worktree.exists()


def test_main_allows_caller_self_with_opt_in(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main(["--allow-caller-self"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "swept worktree" in captured.err
    assert not worktree.exists()


def test_main_returns_2_on_refusal_dirty_tree_emits_preserve_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(clone)
    (worktree / "scratch").write_text("x")
    rc = main(["--worktree", str(worktree)])
    assert rc == 2

    captured = capsys.readouterr()
    assert "PRESERVED" in captured.err
    assert "working tree dirty" in captured.err
    assert "guidance:" in captured.err
    assert worktree.exists()


def test_main_returns_2_when_called_in_parent(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    monkeypatch.chdir(clone)
    rc = main(["--worktree", str(clone)])
    assert rc == 2

    captured = capsys.readouterr()
    # In-parent refusal uses the concise REFUSED form (no preserve-report).
    assert "REFUSED" in captured.err
    assert "parent repo" in captured.err
    assert clone.exists()


def test_main_default_cwd_refuses_self_sweep(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default invocation from inside a worktree (no --worktree, no flag)
    refuses with the preserve-report — the post-S-0143 default behavior."""
    _origin, _clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main([])
    assert rc == 2

    captured = capsys.readouterr()
    assert "PRESERVED" in captured.err
    assert "caller's own worktree" in captured.err
    assert worktree.exists()


def test_main_with_opt_in_chdirs_to_parent_before_sweep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The --allow-caller-self path still chdir's to parent so post-removal
    forks don't fail (the legacy semantic that originally motivated the
    chdir-to-parent step at S-0072)."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    monkeypatch.chdir(worktree)
    rc = main(["--allow-caller-self"])
    assert rc == 0
    assert Path(os.getcwd()).resolve() == clone.resolve()
