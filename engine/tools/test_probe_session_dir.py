"""Tests for engine/tools/probe_session_dir.py — Issue #57 regression.

Covers the probe's three exit conditions (healthy / soft-warn / no-parent)
against synthetic git repos under ``tmp_path``. Mirrors the test
isolation pattern of ``test_probe_repo.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROBE_PATH = Path(__file__).resolve().parent / "probe_session_dir.py"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo_with_session_dir(tmp_path: Path) -> Path:
    """Init a non-bare repo with an empty engine/session/ directory."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    sess = repo / "engine" / "session"
    sess.mkdir(parents=True)
    (sess / "register_state.json").write_text(
        '{"next_id": "0001", "last_claimed": null}\n'
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "initial")
    return repo


def _run_probe(cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    for key in list(env.keys()):
        if key.startswith("GIT_"):
            del env[key]
    return subprocess.run(
        [sys.executable, str(PROBE_PATH)],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )


def test_healthy_clean_session_dir(tmp_path: Path) -> None:
    """No stray files → exit 0 with healthy stdout."""
    repo = _init_repo_with_session_dir(tmp_path)
    result = _run_probe(repo)
    assert result.returncode == 0, (
        f"expected exit 0; got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "healthy" in result.stdout.lower()


def test_stray_current_2_json_triggers_soft_warn(tmp_path: Path) -> None:
    """The canonical macOS Finder duplicate pattern is detected → exit 1.

    Creates ``engine/session/current 2.json`` (literal space, digit,
    extension) — the exact pattern that blocked S-0116 boot.
    """
    repo = _init_repo_with_session_dir(tmp_path)
    stray = repo / "engine" / "session" / "current 2.json"
    stray.write_text('{"id": "S-0001"}\n')
    result = _run_probe(repo)
    assert result.returncode == 1, (
        f"expected exit 1 (soft-warn); got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    # The stray path appears in stderr so the LOUD attention surface
    # in session-start.sh names it.
    assert str(stray) in result.stderr
    # Recovery move surfaces in the same block.
    assert "mv " in result.stderr
    assert "/tmp/" in result.stderr
    assert "Issue #57" in result.stderr


def test_multiple_strays_listed_deterministically(tmp_path: Path) -> None:
    """If multiple matches exist, all are listed in sorted order → exit 1."""
    repo = _init_repo_with_session_dir(tmp_path)
    sess = repo / "engine" / "session"
    (sess / "current 3.json").write_text("{}\n")
    (sess / "current 2.json").write_text("{}\n")
    result = _run_probe(repo)
    assert result.returncode == 1
    # Both paths appear and `current 2.json` precedes `current 3.json`
    # in the output (sort order).
    idx_2 = result.stderr.find("current 2.json")
    idx_3 = result.stderr.find("current 3.json")
    assert idx_2 != -1 and idx_3 != -1
    assert idx_2 < idx_3


def test_archive_subdir_files_not_scanned(tmp_path: Path) -> None:
    """Files in archive/ matching the pattern are NOT flagged.

    The iCloud conflict targets the live ``current.json`` slot, not
    archive files. A literal `archive/current 2.json` would be a
    different bug; the probe stays focused on its scope.
    """
    repo = _init_repo_with_session_dir(tmp_path)
    archive = repo / "engine" / "session" / "archive"
    archive.mkdir(parents=True)
    (archive / "current 2.json").write_text("{}\n")  # NOT a real concern
    result = _run_probe(repo)
    assert result.returncode == 0, (
        f"expected exit 0 — archive/ files should not flag; "
        f"got {result.returncode}; stderr={result.stderr!r}"
    )


def test_unrelated_filename_not_flagged(tmp_path: Path) -> None:
    """Non-matching filenames don't trigger the probe → exit 0.

    Verifies the regex isn't over-broad. Files like ``current.json``
    (no space-digit suffix), ``current_2.json`` (underscore), and
    ``foo 2.json`` (different stem) all stay silent.
    """
    repo = _init_repo_with_session_dir(tmp_path)
    sess = repo / "engine" / "session"
    (sess / "current.json").write_text("{}\n")
    (sess / "current_2.json").write_text("{}\n")
    (sess / "foo 2.json").write_text("{}\n")
    result = _run_probe(repo)
    assert result.returncode == 0


def test_not_in_a_repo_treated_as_healthy(tmp_path: Path) -> None:
    """No git repo at cwd → no parent session dir resolvable → exit 0.

    Best-effort: the probe doesn't fail loudly when it can't even find
    a repo to scan. The session-start hook surfaces repo-level health
    on its own; this probe stays narrow.
    """
    bare_dir = tmp_path / "not-a-repo"
    bare_dir.mkdir()
    result = _run_probe(bare_dir)
    assert result.returncode == 0
    assert "healthy" in result.stdout.lower()


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
