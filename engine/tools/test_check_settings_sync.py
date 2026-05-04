"""Tests for engine/tools/check_settings_sync.py.

Two layers of coverage:

1. Pure-function units (``files_differ``) tested against ``tmp_path`` files
   with no git involvement.
2. ``main()`` integration via ``monkeypatch`` of the git-touching helpers
   (``detect_worktree`` + ``is_staged``) so we exercise the full disposition
   logic without building real worktrees.
3. Real-git integration for ``detect_worktree`` and ``is_staged`` so the
   ``git rev-parse`` resolution path is covered end-to-end (the conftest.py
   autouse ``_scrub_git_env`` fixture protects against parent GIT_*
   leakage).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_settings_sync import (  # noqa: E402
    detect_worktree,
    files_differ,
    is_staged,
    main,
)


def _git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


# ---------------------------------------------------------------------------
# files_differ
# ---------------------------------------------------------------------------


def test_files_differ_byte_equal(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_bytes(b'{"x": 1}\n')
    b.write_bytes(b'{"x": 1}\n')
    assert files_differ(a, b) is False


def test_files_differ_byte_different(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_bytes(b'{"x": 1}\n')
    b.write_bytes(b'{"x": 2}\n')
    assert files_differ(a, b) is True


def test_files_differ_one_missing(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    a.write_bytes(b'{"x": 1}\n')
    b = tmp_path / "missing.json"
    assert files_differ(a, b) is True


# ---------------------------------------------------------------------------
# main() — monkeypatched helpers
# ---------------------------------------------------------------------------


def _stub_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    main_content: bytes | None,
    worktree_content: bytes | None,
    staged: bool,
) -> tuple[Path, Path]:
    """Build main + worktree dirs each with optional .claude/settings.json,
    monkeypatch the git-touching helpers, return the two settings paths."""
    main_root = tmp_path / "main"
    worktree_root = tmp_path / "worktree"
    (main_root / ".claude").mkdir(parents=True)
    (worktree_root / ".claude").mkdir(parents=True)
    main_settings = main_root / ".claude" / "settings.json"
    worktree_settings = worktree_root / ".claude" / "settings.json"
    if main_content is not None:
        main_settings.write_bytes(main_content)
    if worktree_content is not None:
        worktree_settings.write_bytes(worktree_content)

    import check_settings_sync

    monkeypatch.setattr(
        check_settings_sync,
        "detect_worktree",
        lambda: (worktree_root, main_root),
    )
    monkeypatch.setattr(check_settings_sync, "is_staged", lambda _path: staged)
    return main_settings, worktree_settings


def test_main_not_in_worktree_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    import check_settings_sync

    monkeypatch.setattr(check_settings_sync, "detect_worktree", lambda: None)
    assert main() == 0


def test_main_in_sync_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 1}\n',
        staged=False,
    )
    assert main() == 0


def test_main_divergent_not_staged_hard_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 0}\n',
        staged=False,
    )
    assert main() == 1
    captured = capsys.readouterr()
    assert "desync detected" in captured.err
    assert "cp " in captured.err
    assert "git add .claude/settings.json" in captured.err


def test_main_divergent_but_staged_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 0}\n',
        staged=True,
    )
    assert main() == 0


def test_main_worktree_missing_file_treated_as_divergent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing worktree settings.json counts as divergent; should hard-fail
    when not staged. Covers the "fresh clone never had the file synced" case.
    """
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=None,
        staged=False,
    )
    assert main() == 1


# ---------------------------------------------------------------------------
# Real-git integration
# ---------------------------------------------------------------------------


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q", "-b", "main"], cwd=repo)
    _git(["config", "user.email", "t@t"], cwd=repo)
    _git(["config", "user.name", "T"], cwd=repo)
    (repo / "x.txt").write_text("x\n")
    _git(["add", "."], cwd=repo)
    _git(["commit", "-q", "-m", "init"], cwd=repo)


def test_detect_worktree_in_main_repo_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    monkeypatch.chdir(repo)
    assert detect_worktree() is None


def test_detect_worktree_in_worktree_returns_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    wt = tmp_path / "wt"
    _git(["worktree", "add", "-q", "-b", "feature", str(wt)], cwd=repo)
    monkeypatch.chdir(wt)
    detected = detect_worktree()
    assert detected is not None
    worktree_root, main_root = detected
    assert worktree_root.resolve() == wt.resolve()
    assert main_root.resolve() == repo.resolve()


def test_is_staged_detects_staged_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "x.txt").write_text("y\n")
    _git(["add", "x.txt"], cwd=repo)
    monkeypatch.chdir(repo)
    assert is_staged("x.txt") is True
    assert is_staged("nonexistent.txt") is False


def test_main_real_worktree_divergent_not_staged_hard_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: real git repo + real worktree + divergent files."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".claude").mkdir()
    (repo / ".claude" / "settings.json").write_text('{"x": 1}\n')
    _git(["add", ".claude/settings.json"], cwd=repo)
    _git(["commit", "-q", "-m", "add settings"], cwd=repo)

    wt = tmp_path / "wt"
    _git(["worktree", "add", "-q", "-b", "feature", str(wt)], cwd=repo)

    # Diverge: edit main's copy, leave worktree's stale (mirrors the bug)
    (repo / ".claude" / "settings.json").write_text('{"x": 99}\n')

    monkeypatch.chdir(wt)
    assert main() == 1
