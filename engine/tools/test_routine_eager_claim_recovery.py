"""Tests for routine_eager_claim_recovery.py — Issue #15 (S-0055)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_eager_claim_recovery import main, verify_race_shape  # noqa: E402


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin_with_clone(tmp_path: Path) -> tuple[Path, Path]:
    """Create bare origin + clone with one commit on main.

    ``--initial-branch=main`` is passed to both ``git init --bare`` and
    ``git clone`` so the fixture works on any runner regardless of the
    host's ``init.defaultBranch`` config. Without this, GitHub Actions
    runners (where the default is ``master``) end up with the bare
    origin's HEAD pointing at a nonexistent ``master`` ref after the
    clone pushes ``main``, which breaks subsequent ``git reset --hard
    HEAD~1`` and non-fast-forward push tests (S-0131 CI surfacing).
    Requires git ≥ 2.28; CI runners ship 2.53 and the local venv is
    well past 2.28.
    """
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(origin)],
        capture_output=True,
        check=True,
    )
    # No --branch=main on clone: the bare repo is empty, so main has no
    # commits yet — git refuses --branch=<X> when X doesn't exist as a
    # ref. The bare's HEAD (set via --initial-branch=main on init) is
    # inherited by the clone's HEAD, so the first commit lands on main.
    subprocess.run(
        ["git", "clone", str(origin), str(clone)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)
    (clone / "README").write_text("init\n")
    _git(["add", "README"], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    return origin, clone


def _make_eager_claim_commit(
    clone: Path, slot: str, content_file: str = "claim"
) -> str:
    """Write the canonical eager-claim commit. Returns the commit SHA."""
    (clone / content_file).write_text(f"claim {slot}\n")
    _git(["add", content_file], clone)
    _git(
        ["commit", "-m", f"chore(session): eager-claim {slot} — test claim"],
        clone,
    )
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


def test_verifies_race_shape_when_both_sides_claim_same_slot(tmp_path: Path) -> None:
    """Loser has eager-claim S-0055; origin/main also has eager-claim S-0055 (winner)."""
    _origin, winner_clone = _make_origin_with_clone(tmp_path)
    # Winner: claim and push S-0055
    _make_eager_claim_commit(winner_clone, "S-0055", content_file="winner_claim")
    _git(["push"], winner_clone)

    # Loser: clone the origin into a separate dir, then add a local claim for the same slot
    loser_clone = tmp_path / "loser"
    subprocess.run(
        ["git", "clone", str(_origin), str(loser_clone)],
        capture_output=True,
        check=True,
    )
    _git(["config", "user.email", "test@example.com"], loser_clone)
    _git(["config", "user.name", "Test"], loser_clone)
    # Move loser back to before the winner's claim
    _git(["reset", "--hard", "HEAD~1"], loser_clone)
    # Loser writes its own eager-claim for S-0055 (the duplicate-slot bug)
    _make_eager_claim_commit(loser_clone, "S-0055", content_file="loser_claim")
    _git(["fetch", "origin", "main"], loser_clone)

    is_race, reason = verify_race_shape(loser_clone)
    assert is_race
    assert "S-0055" in reason


def test_refuses_when_no_local_ahead_commits(tmp_path: Path) -> None:
    """HEAD == origin/main → not a race; refuse."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    is_race, reason = verify_race_shape(clone)
    assert not is_race
    assert "no commits ahead" in reason


def test_refuses_when_multiple_commits_ahead(tmp_path: Path) -> None:
    """HEAD has 2 commits ahead → substantive work; refuse."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone, "S-0055", content_file="claim")
    (clone / "extra").write_text("extra\n")
    _git(["add", "extra"], clone)
    _git(["commit", "-m", "feat: extra work"], clone)

    is_race, reason = verify_race_shape(clone)
    assert not is_race
    assert "2 commits ahead" in reason or "manual review" in reason


def test_refuses_when_local_subject_not_eager_claim(tmp_path: Path) -> None:
    """Local-ahead commit with non-eager-claim subject → refuse."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    (clone / "unrelated").write_text("x\n")
    _git(["add", "unrelated"], clone)
    _git(["commit", "-m", "feat: unrelated work"], clone)

    is_race, reason = verify_race_shape(clone)
    assert not is_race
    assert "does not match eager-claim pattern" in reason


def test_refuses_when_origin_main_not_eager_claim(tmp_path: Path) -> None:
    """origin/main HEAD with non-eager-claim subject → refuse (no symmetric shape)."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    # Push a non-claim commit to origin
    (clone / "feature").write_text("feature\n")
    _git(["add", "feature"], clone)
    _git(["commit", "-m", "feat: feature"], clone)
    _git(["push"], clone)

    # Now make a local-only eager-claim
    _make_eager_claim_commit(clone, "S-0055", content_file="local_claim")

    is_race, reason = verify_race_shape(clone)
    assert not is_race
    assert "origin/main HEAD" in reason


def test_refuses_when_slots_differ(tmp_path: Path) -> None:
    """Local claim S-0055 vs origin claim S-0056 → not the same-slot shape."""
    _origin, winner_clone = _make_origin_with_clone(tmp_path)
    # Winner pushes S-0056
    _make_eager_claim_commit(winner_clone, "S-0056", content_file="winner_claim")
    _git(["push"], winner_clone)

    # Loser: clone fresh, reset to before winner's claim, claim S-0055 instead
    loser = tmp_path / "loser"
    subprocess.run(
        ["git", "clone", str(_origin), str(loser)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], loser)
    _git(["config", "user.name", "Test"], loser)
    _git(["reset", "--hard", "HEAD~1"], loser)
    _make_eager_claim_commit(loser, "S-0055", content_file="loser_claim")
    _git(["fetch", "origin", "main"], loser)

    is_race, reason = verify_race_shape(loser)
    assert not is_race
    assert "slots differ" in reason


def test_main_dry_run_verifies_without_resetting(tmp_path: Path) -> None:
    """--dry-run reports the verified shape and does not perform the reset."""
    _origin, winner = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(winner, "S-0055", content_file="winner_claim")
    _git(["push"], winner)
    loser = tmp_path / "loser"
    subprocess.run(
        ["git", "clone", str(_origin), str(loser)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], loser)
    _git(["config", "user.name", "Test"], loser)
    _git(["reset", "--hard", "HEAD~1"], loser)
    _make_eager_claim_commit(loser, "S-0055", content_file="loser_claim")
    _git(["fetch", "origin", "main"], loser)

    head_before = _git(["rev-parse", "HEAD"], loser).stdout.strip()
    rc = main(["--repo-root", str(loser), "--dry-run"])
    assert rc == 0
    head_after = _git(["rev-parse", "HEAD"], loser).stdout.strip()
    assert head_before == head_after  # not reset


def test_main_performs_reset_when_verified(tmp_path: Path) -> None:
    """Without --dry-run, the reset moves HEAD to origin/main."""
    _origin, winner = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(winner, "S-0055", content_file="winner_claim")
    _git(["push"], winner)
    origin_head = _git(["rev-parse", "origin/main"], winner).stdout.strip()

    loser = tmp_path / "loser"
    subprocess.run(
        ["git", "clone", str(_origin), str(loser)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], loser)
    _git(["config", "user.name", "Test"], loser)
    _git(["reset", "--hard", "HEAD~1"], loser)
    _make_eager_claim_commit(loser, "S-0055", content_file="loser_claim")
    _git(["fetch", "origin", "main"], loser)

    rc = main(["--repo-root", str(loser)])
    assert rc == 0
    head_after = _git(["rev-parse", "HEAD"], loser).stdout.strip()
    expected_head_after = _git(["rev-parse", "origin/main"], loser).stdout.strip()
    assert head_after == expected_head_after
    assert head_after == origin_head


def test_main_refuses_ambiguous_with_exit_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Multi-commit-ahead → exit 2, no reset."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone, "S-0055", content_file="claim")
    (clone / "extra").write_text("extra\n")
    _git(["add", "extra"], clone)
    _git(["commit", "-m", "feat: extra"], clone)

    head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    rc = main(["--repo-root", str(clone)])
    assert rc == 2
    head_after = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_before == head_after
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
