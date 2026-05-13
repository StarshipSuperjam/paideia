"""Tests for engine/tools/update_settings.py — Issue #107 (S-0150).

Two layers of coverage:
1. main() integration via monkeypatch of detect_worktree (the only git-
   touching helper update_settings calls directly) so we exercise the
   sync-vs-noop-vs-error dispositions without building real worktrees.
2. Real-git integration: a single end-to-end test against a tmp-dir bare
   origin + clone + linked worktree, exercising the
   detect_worktree -> cp -> git add path.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_settings_sync  # noqa: E402
from update_settings import SETTINGS_PATH, main  # noqa: E402


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _stub_detect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    main_content: bytes | None,
    worktree_content: bytes | None,
) -> tuple[Path, Path]:
    """Build main + worktree dirs each with optional .claude/settings.json,
    monkeypatch detect_worktree to return them. Returns the two roots."""
    main_root = tmp_path / "main"
    worktree_root = tmp_path / "worktree"
    (main_root / ".claude").mkdir(parents=True)
    (worktree_root / ".claude").mkdir(parents=True)
    if main_content is not None:
        (main_root / SETTINGS_PATH).write_bytes(main_content)
    if worktree_content is not None:
        (worktree_root / SETTINGS_PATH).write_bytes(worktree_content)

    monkeypatch.setattr(
        check_settings_sync,
        "detect_worktree",
        lambda: (worktree_root, main_root),
    )
    return main_root, worktree_root


# ---------------------------------------------------------------------------
# main() — monkeypatched dispositions
# ---------------------------------------------------------------------------


def test_main_returns_zero_no_op_when_not_in_worktree(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """detect_worktree() returns None → exit 0 + informational stderr + reminder."""
    monkeypatch.setattr(check_settings_sync, "detect_worktree", lambda: None)
    rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "not in a linked worktree" in captured.err
    assert "parent_ff() auto-recovers" in captured.err


def test_main_returns_zero_when_files_already_in_sync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Worktree's copy already matches parent's → no copy/add; exit 0 + reminder."""
    same = b'{"hooks": {}}\n'
    main_root, worktree_root = _stub_detect(tmp_path, monkeypatch, same, same)
    rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "already in sync" in captured.err
    assert "parent_ff() auto-recovers" in captured.err
    # The worktree's file must NOT have been re-written (mtime preserved is
    # the natural side-effect of taking the no-op branch — we assert via
    # content equality and absence of staging which is impossible here as
    # the dir isn't a git repo).
    assert (worktree_root / SETTINGS_PATH).read_bytes() == same


def test_main_copies_and_stages_when_files_differ(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Parent and worktree differ → cp + git add; verify content + staging."""
    main_content = b'{"hooks": {"new": "harness-edit"}}\n'
    worktree_stale = b'{"hooks": {}}\n'
    main_root, worktree_root = _stub_detect(
        tmp_path, monkeypatch, main_content, worktree_stale
    )
    # The worktree needs to be a real git repo for `git add` to work
    _git(["init"], worktree_root)
    _git(["config", "user.email", "test@example.com"], worktree_root)
    _git(["config", "user.name", "Test"], worktree_root)
    # Commit the initial stale content so we have a HEAD
    _git(["add", SETTINGS_PATH], worktree_root)
    _git(["commit", "-m", "initial stale"], worktree_root)

    rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "synced and staged" in captured.err
    assert "parent_ff() auto-recovers" in captured.err

    # Worktree's copy now matches parent's
    assert (worktree_root / SETTINGS_PATH).read_bytes() == main_content
    # And it's staged (cached diff shows the change)
    cached = subprocess.run(
        ["git", "-C", str(worktree_root), "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert SETTINGS_PATH in cached


def test_main_returns_two_when_git_add_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """git add failure → exit 2 + stderr names the failure."""
    main_content = b'{"hooks": {"new": "x"}}\n'
    worktree_stale = b'{"hooks": {}}\n'
    main_root, worktree_root = _stub_detect(
        tmp_path, monkeypatch, main_content, worktree_stale
    )
    # Do NOT init the worktree as a git repo — git add will fail because
    # the directory isn't tracked by git.
    rc = main()
    assert rc == 2
    captured = capsys.readouterr()
    assert "git add failed" in captured.err


def test_main_returns_two_when_copy_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Copy failure (parent's settings missing) → exit 2."""
    main_root = tmp_path / "main"
    worktree_root = tmp_path / "worktree"
    (main_root / ".claude").mkdir(parents=True)
    (worktree_root / ".claude").mkdir(parents=True)
    # Parent's settings missing entirely; worktree has stale content.
    (worktree_root / SETTINGS_PATH).write_bytes(b'{"hooks": {}}\n')

    monkeypatch.setattr(
        check_settings_sync,
        "detect_worktree",
        lambda: (worktree_root, main_root),
    )
    rc = main()
    assert rc == 2
    captured = capsys.readouterr()
    assert "failed to copy" in captured.err


# ---------------------------------------------------------------------------
# Real-git integration
# ---------------------------------------------------------------------------


def test_main_real_worktree_end_to_end(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end with real linked worktree: detect → cp → git add → exit 0."""
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    worktree = tmp_path / "worktree"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(origin)],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "clone", str(origin), str(clone)],
        capture_output=True,
        check=True,
    )
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)
    (clone / ".claude").mkdir()
    (clone / SETTINGS_PATH).write_bytes(b'{"hooks": {}}\n')
    _git(["add", "."], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    _git(
        ["worktree", "add", "-b", "claude/test-worktree", str(worktree)],
        clone,
    )
    _git(["config", "user.email", "test@example.com"], worktree)
    _git(["config", "user.name", "Test"], worktree)

    # Simulate the harness redirect: edit the parent's settings, leaving the
    # worktree's copy stale.
    (clone / SETTINGS_PATH).write_bytes(b'{"hooks": {"new": "harness-edit"}}\n')

    # Invoke update_settings from inside the worktree (chdir).
    monkeypatch.chdir(worktree)
    rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "synced and staged" in captured.err

    # Worktree's copy now matches parent
    assert (
        worktree / SETTINGS_PATH
    ).read_bytes() == b'{"hooks": {"new": "harness-edit"}}\n'
    # And it's staged in the worktree
    cached = _git(["diff", "--cached", "--name-only"], worktree).stdout.strip()
    assert SETTINGS_PATH in cached
