"""Tests for ``_resolve_canonical_history_path()`` in ``validate.py``.

Covers the S-0205 fix for Issue #150: HISTORY_FILE must resolve to the
canonical main-repo path regardless of which worktree's validate.py is
invoking the function, with a defensive fallback to the per-clone path
when ``git rev-parse`` cannot resolve a git common dir.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# validate.py lives in the same engine/tools/ directory as this test file
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_main_repo_with_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """Create a main repo + linked worktree fixture.

    Returns (main_repo, worktree). Both paths are absolute. The main repo
    has one empty commit on ``main``; the worktree is checked out to a
    branch named ``worktree-branch``.
    """
    main = tmp_path / "main_repo"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    _git(main, "config", "user.email", "test@example.com")
    _git(main, "config", "user.name", "Test")
    _git(main, "commit", "--allow-empty", "-q", "-m", "initial")
    worktree = tmp_path / "worktree"
    _git(main, "worktree", "add", "-q", "-b", "worktree-branch", str(worktree))
    return main, worktree


def test_canonical_path_resolves_to_main_repo_from_worktree(tmp_path: Path) -> None:
    """From inside a linked worktree, HISTORY_FILE must point at the main repo."""
    main, worktree = _init_main_repo_with_worktree(tmp_path)
    expected = main / "engine" / "tools" / "validate-history.jsonl"

    result = validate._resolve_canonical_history_path(cwd=worktree)

    assert result == expected, (
        f"Expected main-repo path {expected}, got {result}. "
        f"This means the worktree resolved its own per-clone path "
        f"instead of the canonical main-repo path — the Issue #150 "
        f"regression has returned."
    )


def test_canonical_path_resolves_correctly_from_main_repo(tmp_path: Path) -> None:
    """From inside the main repo, HISTORY_FILE must also resolve to itself."""
    main, _ = _init_main_repo_with_worktree(tmp_path)
    expected = main / "engine" / "tools" / "validate-history.jsonl"

    result = validate._resolve_canonical_history_path(cwd=main)

    assert result == expected


def test_falls_back_to_per_clone_outside_git_repo(tmp_path: Path) -> None:
    """Outside any git repo, fall back to the passed cwd-relative path.

    Defensive behavior: telemetry writes should never raise. When git
    rev-parse fails (no .git anywhere up the tree), the function returns
    the cwd-relative per-clone path so ``append_history()`` still has a
    target.
    """
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()
    expected_fallback = not_a_repo / "engine" / "tools" / "validate-history.jsonl"

    result = validate._resolve_canonical_history_path(cwd=not_a_repo)

    assert result == expected_fallback
