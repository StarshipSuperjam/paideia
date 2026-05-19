"""Tests for engine/tools/check_settings_sync.py.

Three layers of coverage:

1. Pure-function units (``compare``) tested against ``tmp_path`` files
   with no git involvement, covering each of the six direction signals:
   in_sync, worktree_canonical, main_canonical, concurrent,
   missing_main, missing_worktree.
2. ``main()`` integration via ``monkeypatch`` of the git-touching helpers
   (``detect_worktree`` + ``is_staged``) so we exercise the full
   disposition logic without building real worktrees.
3. Real-git integration for ``detect_worktree`` and ``is_staged`` so the
   ``git rev-parse`` resolution path is covered end-to-end (the conftest.py
   autouse ``_scrub_git_env`` fixture protects against parent GIT_*
   leakage).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_settings_sync import (  # noqa: E402
    CONCURRENT_TOLERANCE_SECONDS,
    compare,
    detect_worktree,
    is_staged,
    main,
)


def _git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _set_mtime(path: Path, seconds: float) -> None:
    """Set both atime and mtime of ``path``."""
    os.utime(path, (seconds, seconds))


# ---------------------------------------------------------------------------
# compare() — pure-function direction detection
# ---------------------------------------------------------------------------


def test_compare_byte_equal_returns_in_sync(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_bytes(b'{"x": 1}\n')
    b.write_bytes(b'{"x": 1}\n')
    assert compare(a, b) == "in_sync"


def test_compare_both_missing_returns_in_sync(tmp_path: Path) -> None:
    a = tmp_path / "missing_a.json"
    b = tmp_path / "missing_b.json"
    assert compare(a, b) == "in_sync"


def test_compare_main_missing(tmp_path: Path) -> None:
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    worktree_file.write_bytes(b'{"x": 1}\n')
    assert compare(main_file, worktree_file) == "missing_main"


def test_compare_worktree_missing(tmp_path: Path) -> None:
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    main_file.write_bytes(b'{"x": 1}\n')
    assert compare(main_file, worktree_file) == "missing_worktree"


def test_compare_worktree_newer(tmp_path: Path) -> None:
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    main_file.write_bytes(b'{"x": 1}\n')
    worktree_file.write_bytes(b'{"x": 2}\n')
    now = time.time()
    _set_mtime(main_file, now - 100)
    _set_mtime(worktree_file, now)
    assert compare(main_file, worktree_file) == "worktree_canonical"


def test_compare_main_newer(tmp_path: Path) -> None:
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    main_file.write_bytes(b'{"x": 1}\n')
    worktree_file.write_bytes(b'{"x": 2}\n')
    now = time.time()
    _set_mtime(main_file, now)
    _set_mtime(worktree_file, now - 100)
    assert compare(main_file, worktree_file) == "main_canonical"


def test_compare_concurrent_within_tolerance(tmp_path: Path) -> None:
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    main_file.write_bytes(b'{"x": 1}\n')
    worktree_file.write_bytes(b'{"x": 2}\n')
    now = time.time()
    _set_mtime(main_file, now)
    # Within the 1-second tolerance band.
    _set_mtime(worktree_file, now + CONCURRENT_TOLERANCE_SECONDS / 2)
    assert compare(main_file, worktree_file) == "concurrent"


def test_compare_just_outside_tolerance_returns_direction(tmp_path: Path) -> None:
    """Verify the tolerance boundary: just outside it, direction must surface."""
    main_file = tmp_path / "main.json"
    worktree_file = tmp_path / "wt.json"
    main_file.write_bytes(b'{"x": 1}\n')
    worktree_file.write_bytes(b'{"x": 2}\n')
    now = time.time()
    _set_mtime(main_file, now)
    # 0.5s outside tolerance → direction must be detected
    _set_mtime(worktree_file, now + CONCURRENT_TOLERANCE_SECONDS + 0.5)
    assert compare(main_file, worktree_file) == "worktree_canonical"


# ---------------------------------------------------------------------------
# main() — monkeypatched helpers (direction-aware)
# ---------------------------------------------------------------------------


def _stub_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    main_content: bytes | None,
    worktree_content: bytes | None,
    staged: bool,
    worktree_newer: bool | None = None,
) -> tuple[Path, Path]:
    """Build main + worktree dirs with optional content; monkeypatch helpers.

    ``worktree_newer``: if True, set worktree mtime > main mtime by 100s.
    If False, the inverse. If None, leave mtimes as-written (used for
    in_sync + concurrent cases).
    """
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

    if worktree_newer is not None and main_content is not None and worktree_content is not None:
        now = time.time()
        if worktree_newer:
            _set_mtime(main_settings, now - 100)
            _set_mtime(worktree_settings, now)
        else:
            _set_mtime(main_settings, now)
            _set_mtime(worktree_settings, now - 100)

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


def test_main_main_canonical_not_staged_hard_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Main is newer (original case); guidance should say 'cp main → worktree'."""
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 99}\n',
        worktree_content=b'{"x": 1}\n',
        staged=False,
        worktree_newer=False,
    )
    assert main() == 1
    captured = capsys.readouterr()
    assert "main (canonical)" in captured.err
    assert "worktree (stale)" in captured.err
    assert "cp " in captured.err
    assert "git add .claude/settings.json" in captured.err


def test_main_worktree_canonical_not_staged_hard_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Worktree is newer (Issue #154 case); guidance should NOT say 'cp main → worktree'.

    This is the direction the pre-S-0210 tool got wrong — when worktree
    is canonical, copying main's content into the worktree would destroy
    the canonical content.
    """
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 99}\n',
        staged=False,
        worktree_newer=True,
    )
    assert main() == 1
    captured = capsys.readouterr()
    assert "worktree settings.json is NEWER" in captured.err
    assert "worktree (canonical)" in captured.err
    assert "main (stale)" in captured.err
    # Critical: the guidance must NOT direct the user to `cp main → worktree`
    # (which would destroy the canonical content). The acceptable cp shape
    # is "cp '<main_path>' .claude/settings.json" — that's the bug.
    assert "git add .claude/settings.json" in captured.err
    # The worktree-canonical guidance does not include `cp ` at all — it
    # only says "stage the worktree's copy."
    assert "cp " not in captured.err


def test_main_concurrent_edit_halts_with_diff_hint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Both edited within tolerance → halt-and-confirm, emit diff command."""
    main_root = tmp_path / "main"
    worktree_root = tmp_path / "worktree"
    (main_root / ".claude").mkdir(parents=True)
    (worktree_root / ".claude").mkdir(parents=True)
    main_settings = main_root / ".claude" / "settings.json"
    worktree_settings = worktree_root / ".claude" / "settings.json"
    main_settings.write_bytes(b'{"x": 1}\n')
    worktree_settings.write_bytes(b'{"x": 99}\n')
    now = time.time()
    _set_mtime(main_settings, now)
    _set_mtime(worktree_settings, now + CONCURRENT_TOLERANCE_SECONDS / 4)

    import check_settings_sync

    monkeypatch.setattr(
        check_settings_sync,
        "detect_worktree",
        lambda: (worktree_root, main_root),
    )
    monkeypatch.setattr(check_settings_sync, "is_staged", lambda _path: False)
    assert main() == 1
    captured = capsys.readouterr()
    assert "bidirectional edit detected" in captured.err
    assert "diff " in captured.err
    assert "If main is canonical" in captured.err
    assert "If worktree is canonical" in captured.err


def test_main_divergent_but_staged_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Once user has staged the worktree's copy, no direction-detection runs."""
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 0}\n',
        staged=True,
        worktree_newer=False,  # Even if main were newer
    )
    assert main() == 0


def test_main_staged_short_circuits_worktree_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Worktree-newer + staged → still pass (user did the right thing)."""
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=b'{"x": 99}\n',
        staged=True,
        worktree_newer=True,
    )
    assert main() == 0


def test_main_worktree_missing_file_hard_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing worktree settings.json → hard-fail with restore guidance."""
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=b'{"x": 1}\n',
        worktree_content=None,
        staged=False,
    )
    assert main() == 1
    captured = capsys.readouterr()
    assert "worktree's .claude/settings.json is missing" in captured.err
    assert "cp " in captured.err


def test_main_main_missing_file_hard_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing main settings.json is unusual — surface but hard-fail."""
    _stub_paths(
        tmp_path,
        monkeypatch,
        main_content=None,
        worktree_content=b'{"x": 1}\n',
        staged=False,
    )
    assert main() == 1
    captured = capsys.readouterr()
    assert "main repo's .claude/settings.json is missing" in captured.err


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


def test_main_real_worktree_main_canonical_hard_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: real git repo + real worktree + main is canonical."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".claude").mkdir()
    (repo / ".claude" / "settings.json").write_text('{"x": 1}\n')
    _git(["add", ".claude/settings.json"], cwd=repo)
    _git(["commit", "-q", "-m", "add settings"], cwd=repo)

    wt = tmp_path / "wt"
    _git(["worktree", "add", "-q", "-b", "feature", str(wt)], cwd=repo)

    # Force main's settings to be NEWER (the original case) + diverged
    (repo / ".claude" / "settings.json").write_text('{"x": 99}\n')
    now = time.time()
    _set_mtime(repo / ".claude" / "settings.json", now)
    _set_mtime(wt / ".claude" / "settings.json", now - 100)

    monkeypatch.chdir(wt)
    assert main() == 1


def test_main_real_worktree_worktree_canonical_hard_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: Issue #154 scenario — worktree is canonical."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".claude").mkdir()
    (repo / ".claude" / "settings.json").write_text('{"x": 1}\n')
    _git(["add", ".claude/settings.json"], cwd=repo)
    _git(["commit", "-q", "-m", "add settings"], cwd=repo)

    wt = tmp_path / "wt"
    _git(["worktree", "add", "-q", "-b", "feature", str(wt)], cwd=repo)

    # The harness wrote to the WORKTREE's copy (Issue #154 case)
    (wt / ".claude" / "settings.json").write_text('{"x": 99}\n')
    now = time.time()
    _set_mtime(repo / ".claude" / "settings.json", now - 100)
    _set_mtime(wt / ".claude" / "settings.json", now)

    monkeypatch.chdir(wt)
    # We expect hard-fail (worktree's content is the right content but it's
    # not staged for the current commit yet). The guidance now correctly
    # directs the user to stage the worktree's copy (not destroy it).
    assert main() == 1
