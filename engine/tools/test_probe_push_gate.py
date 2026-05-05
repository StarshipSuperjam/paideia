"""Tests for probe_push_gate.py — Phase 0 of S-0060."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_push_gate import (  # noqa: E402
    main,
    make_empty_commit,
    push,
    _utc_timestamp,
)


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin_with_clone(tmp_path: Path) -> tuple[Path, Path]:
    """Bare origin + clone with one commit on main. Mirrors the fixture used
    elsewhere in engine/tools/test_*.py."""
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
    _git(["add", "README"], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["branch", "-M", "main"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    return origin, clone


def test_utc_timestamp_format() -> None:
    """Timestamp must be UTC, branch-name-safe."""
    ts = _utc_timestamp()
    assert len(ts) == 16  # YYYYMMDDTHHMMSSZ
    assert ts[8] == "T"
    assert ts.endswith("Z")
    # No characters that would break a git refname:
    for ch in ts:
        assert ch.isalnum(), f"{ch!r} not refname-safe"


def test_dry_run_prints_command_does_not_commit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Default mode: print command, no commit created."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()

    rc = main(["--repo-root", str(clone)])
    assert rc == 0

    head_after = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_before == head_after, "dry-run created a commit"

    captured = capsys.readouterr()
    assert "dry-run" in captured.out
    assert "would push" in captured.out


def test_dry_run_with_target_main_indicates_load_bearing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--target-main without --actually-push still describes the load-bearing test."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    rc = main(["--repo-root", str(clone), "--target-main"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "main" in captured.out
    assert "load-bearing" in captured.out.lower() or "TARGETING MAIN" in captured.out


def test_make_empty_commit_creates_commit(tmp_path: Path) -> None:
    """Empty commit creation succeeds and returns the new HEAD SHA."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()

    ok, sha = make_empty_commit(clone, "20260505T000000Z")
    assert ok
    assert sha != head_before
    assert len(sha) == 40

    # The commit's message contains the timestamp
    msg = _git(["log", "--format=%s", "-n1", sha], clone).stdout.strip()
    assert "20260505T000000Z" in msg
    assert "probe_push_gate" in msg


def test_push_to_throwaway_branch_succeeds(tmp_path: Path) -> None:
    """Subprocess push to a non-main branch succeeds against bare origin."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    make_empty_commit(clone, "20260505T000000Z")

    ok, _stdout, stderr = push(clone, "HEAD:claude/probe-throwaway", dry_run=False)
    assert ok, f"push failed: stderr={stderr!r}"

    # Verify the branch landed on the bare origin
    refs = subprocess.run(
        ["git", "-C", str(_origin), "for-each-ref", "--format=%(refname)"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "refs/heads/claude/probe-throwaway" in refs


def test_push_to_main_via_subprocess_succeeds_against_local_origin(
    tmp_path: Path,
) -> None:
    """Subprocess push to main against a local bare origin succeeds.

    This is NOT the load-bearing test (no harness in fixture), but it
    exercises the actual code path. The empirical hypothesis test
    (subprocess vs harness gate) requires a real Claude Code session
    invoking the script — see Phase 0 Run 2/3 in the build_readiness
    note.
    """
    _origin, clone = _make_origin_with_clone(tmp_path)
    make_empty_commit(clone, "20260505T000000Z")

    ok, _stdout, stderr = push(clone, "HEAD:main", dry_run=False)
    assert ok, f"push to main failed: stderr={stderr!r}"


def test_actually_push_throwaway_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--actually-push to throwaway branch: commit + push, exit 0."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()

    rc = main(["--repo-root", str(clone), "--actually-push"])
    assert rc == 0

    head_after = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_after != head_before, "no commit created"

    captured = capsys.readouterr()
    assert "empty commit created" in captured.out
    assert "push succeeded" in captured.out


def test_actually_push_target_main_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--actually-push --target-main: full path against local bare origin."""
    _origin, clone = _make_origin_with_clone(tmp_path)

    rc = main(["--repo-root", str(clone), "--actually-push", "--target-main"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "LOAD-BEARING TEST" in captured.out
    assert "push succeeded" in captured.out

    # Verify the empty commit landed on origin/main
    head = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    msg = subprocess.run(
        ["git", "-C", str(_origin), "log", "--format=%s", "-n1", head],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert "probe_push_gate" in msg
