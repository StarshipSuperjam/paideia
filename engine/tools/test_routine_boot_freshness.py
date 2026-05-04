"""Tests for routine_boot_freshness.py — Issue #15 (S-0055)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_boot_freshness import main  # noqa: E402


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command in cwd; raise on non-zero."""
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin(tmp_path: Path) -> tuple[Path, Path]:
    """Create a bare 'origin' repo and a clone, return (origin_path, clone_path).

    The clone has one commit on main matching origin/main. Returns the bare
    origin path and the clone path.
    """
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"

    subprocess.run(
        ["git", "init", "--bare", str(origin)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "clone", str(origin), str(clone)], capture_output=True, check=True
    )

    # Set up identity locally so commits succeed
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)

    # Create initial commit
    (clone / "README").write_text("init\n")
    _git(["add", "README"], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["branch", "-M", "main"], clone)
    _git(["push", "-u", "origin", "main"], clone)

    return origin, clone


def test_clean_tree_noops(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """HEAD == origin/main → no-op exit 0, no fast-forward log."""
    _origin, clone = _make_origin(tmp_path)
    rc = main(["--repo-root", str(clone)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "fast-forwarded" not in err


def test_behind_tree_fast_forwards(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """HEAD strictly behind origin/main → ff and log the count."""
    _origin, clone = _make_origin(tmp_path)

    # Add a second commit, push it, then reset clone back so we're "behind"
    (clone / "second").write_text("second\n")
    _git(["add", "second"], clone)
    _git(["commit", "-m", "second"], clone)
    _git(["push"], clone)
    head_after = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    _git(["reset", "--hard", "HEAD~1"], clone)
    head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_before != head_after

    rc = main(["--repo-root", str(clone)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "fast-forwarded 1 commit" in err
    head_now = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_now == head_after


def test_ahead_tree_noops(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """HEAD strictly ahead of origin/main → no-op exit 0 (local-only commits ok)."""
    _origin, clone = _make_origin(tmp_path)

    # Make a local-only commit (don't push)
    (clone / "local").write_text("local\n")
    _git(["add", "local"], clone)
    _git(["commit", "-m", "local"], clone)

    rc = main(["--repo-root", str(clone)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "fast-forwarded" not in err


def test_diverged_tree_refuses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """HEAD diverged → exit 2 with HARD-FAIL message."""
    _origin, clone = _make_origin(tmp_path)

    # Push an upstream commit, then diverge locally by resetting and committing different content
    (clone / "upstream").write_text("upstream\n")
    _git(["add", "upstream"], clone)
    _git(["commit", "-m", "upstream"], clone)
    _git(["push"], clone)
    _git(["reset", "--hard", "HEAD~1"], clone)
    (clone / "local").write_text("local\n")
    _git(["add", "local"], clone)
    _git(["commit", "-m", "local"], clone)
    # Now: clone HEAD has 'local' commit, origin/main has 'upstream' commit, diverged.

    rc = main(["--repo-root", str(clone)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "diverged" in err.lower()


def test_fetch_failure_continues(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fetch failure (broken remote) → stderr note + exit 0 (best-effort)."""
    _origin, clone = _make_origin(tmp_path)
    # Break the remote URL so fetch fails
    _git(["remote", "set-url", "origin", "/nonexistent/path/to/missing.git"], clone)

    rc = main(["--repo-root", str(clone)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "fetch failed" in err.lower()
