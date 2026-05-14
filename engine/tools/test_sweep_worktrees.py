"""Tests for sweep_worktrees.sh — the boot-time bulk worktree-sweep utility.

`sweep_worktrees.sh` is a bash script with no Python entry point; these
tests shell out to it against tmp-dir bare-repo + linked-worktree fixtures.
Focused coverage on the liveness-marker path added at S-0157 (ADR 0076
amendment / Issue #120) — the bug where a sibling session's boot-time sweep
reaped a pre-eager-claim plan/exploration worktree. The pre-existing
caller-self + reap-criteria behavior is exercised by the routine
per-worktree tool's own suite (test_routine_worktree_sweep.py); the one
caller-self case here is a regression guard on the bash script specifically.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sweep_worktrees.sh"


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_clone_with_worktree(
    tmp_path: Path, branch: str = "claude/test-worktree"
) -> tuple[Path, Path]:
    """Bare origin + clone + one linked worktree on `branch`, branch merged
    into main (the post-close-push state that makes a worktree reap-eligible).
    Returns (clone, worktree)."""
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

    worktree = tmp_path / "worktree"
    _git(["worktree", "add", "-b", branch, str(worktree)], clone)
    _git(["config", "user.email", "test@example.com"], worktree)
    _git(["config", "user.name", "Test"], worktree)
    # branch is at main's tip → already merged → reap-eligible absent a marker.
    return clone, worktree


def _write_marker(worktree: Path, age_seconds: float = 0.0) -> Path:
    """Write a `session-live` marker into the worktree's private git dir,
    optionally backdating its mtime to exercise the stale path."""
    git_dir = _git(["rev-parse", "--absolute-git-dir"], worktree).stdout.strip()
    marker = Path(git_dir) / "session-live"
    marker.write_text("2026-05-14T00:00:00Z\n")
    if age_seconds:
        past = time.time() - age_seconds
        os.utime(marker, (past, past))
    return marker


def _run_sweep(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def test_fresh_marker_preserves_clean_merged_worktree(tmp_path: Path) -> None:
    """The core Issue #120 fix: a clean + merged + claude/* worktree that
    would otherwise be reaped is preserved when it carries a fresh marker."""
    clone, worktree = _make_clone_with_worktree(tmp_path)
    _write_marker(worktree)
    result = _run_sweep(clone, "--apply")
    assert result.returncode == 0, result.stderr
    assert worktree.exists()
    assert "PRESERVED" in result.stdout
    assert "live session marker" in result.stdout
    assert "removed 0, preserved 1" in result.stdout


def test_stale_marker_does_not_block_reap(tmp_path: Path) -> None:
    """A marker older than the 24h window does not protect the worktree —
    a genuinely abandoned worktree becomes reapable again."""
    clone, worktree = _make_clone_with_worktree(tmp_path)
    _write_marker(worktree, age_seconds=25 * 3600)
    result = _run_sweep(clone, "--apply")
    assert result.returncode == 0, result.stderr
    assert not worktree.exists()
    assert "removed 1" in result.stdout


def test_no_marker_reaped_regression_baseline(tmp_path: Path) -> None:
    """Regression baseline: a clean + merged + claude/* worktree with no
    marker is still reaped — the marker check is additive, not a behavior
    change for the no-marker case."""
    clone, worktree = _make_clone_with_worktree(tmp_path)
    result = _run_sweep(clone, "--apply")
    assert result.returncode == 0, result.stderr
    assert not worktree.exists()
    assert "removed 1" in result.stdout


def test_caller_self_still_preserved(tmp_path: Path) -> None:
    """Regression guard on the bash script: the caller's own worktree is
    preserved even with no marker (the S-0142 safety check)."""
    clone, worktree = _make_clone_with_worktree(tmp_path)
    result = _run_sweep(worktree, "--apply")
    assert result.returncode == 0, result.stderr
    assert worktree.exists()
    assert "PRESERVED" in result.stdout
    assert "caller's current worktree" in result.stdout


def test_fresh_marker_preserved_in_dry_run(tmp_path: Path) -> None:
    """Dry-run (default) also honors the marker — emits the structured
    preserve-report with the live-session guidance line."""
    clone, worktree = _make_clone_with_worktree(tmp_path)
    _write_marker(worktree)
    result = _run_sweep(clone)
    assert result.returncode == 0, result.stderr
    assert worktree.exists()
    assert "PRESERVED" in result.stdout
    assert "live session marker" in result.stdout
    assert "a live session" in result.stdout
    assert "would remove" not in result.stdout
