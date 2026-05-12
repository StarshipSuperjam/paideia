"""Tests for build_lifecycle_push.py per ADR 0076.

Coverage targets:
- Per-mode well-formed accept (3 tests)
- Build-mode deliverable verifier rejects (4 tests covering each predicate)
- Build-mode deliverable accepts WITHOUT task_id (the key delta from routine)
- Eager-claim + close verifiers behave identically to routine (smoke tests
  via direct import — the imported functions are tested exhaustively in
  test_routine_lifecycle_push.py; this file does not re-prove them, only
  confirms the build wrapper invokes them correctly)
- Push-failure path (1 test — exit-code mapping)
- Edge case: dry-run (1 test)

Total: ~12 tests against tmp-dir bare-repo + clone fixtures.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lifecycle_push import (  # noqa: E402
    main,
    verify_deliverable_shape,
)


# ---------------------------------------------------------------------------
# Fixtures — mirror test_routine_lifecycle_push.py shape, but build-mode
# current.json has NO task_id and no auto_target.json read is required.
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin_with_clone(tmp_path: Path) -> tuple[Path, Path]:
    """Bare origin + clone with initial commit + register_state.json on main."""
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(origin)],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "clone", str(origin), str(clone)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)

    sess_dir = clone / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "register_state.json").write_text(
        json.dumps(
            {
                "next_id": "0138",
                "last_claimed": "S-0137",
                "current_status": "closed",
            }
        )
        + "\n"
    )
    (clone / "README").write_text("init\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "initial"], clone)
    _git(["branch", "-M", "main"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    return origin, clone


def _make_build_eager_claim_commit(clone: Path, slot: str = "S-0138") -> str:
    """Author a well-formed build-mode eager-claim commit (NO task_id)."""
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0139"
    state["last_claimed"] = slot
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    # Build-mode current.json — NO task_id field (key contrast with routine)
    (sess_dir / "current.json").write_text(
        json.dumps({"id": slot, "status": "in_progress", "working_on": "test"}) + "\n"
    )
    _git(["add", "."], clone)
    _git(["commit", "-m", f"chore(session): eager-claim {slot} — test"], clone)
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


def _make_build_deliverable_commit(
    clone: Path, path: str = "engine/some/file.md"
) -> str:
    """Author a well-formed build-mode deliverable commit."""
    full = clone / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("deliverable content\n")
    _git(["add", path], clone)
    _git(["commit", "-m", "feat(engine): land the build-mode deliverable"], clone)
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


def _make_build_close_commit(clone: Path, slot: str = "S-0138") -> str:
    """Author a well-formed build-mode close commit."""
    sess_dir = clone / "engine" / "session"
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive = archive_dir / f"{slot}.json"
    archive.write_text(
        json.dumps({"id": slot, "status": "closed", "outcome_summary": "done"}) + "\n"
    )
    (sess_dir / "current.json").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", f"chore(session): close {slot} — test close"], clone)
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


# ---------------------------------------------------------------------------
# Per-mode well-formed accepts
# ---------------------------------------------------------------------------


def test_eager_claim_well_formed_accepts_and_pushes(tmp_path: Path) -> None:
    """Smoke test: imported routine verifier accepts build-mode eager-claim shape."""
    origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    rc = main(
        [
            "eager-claim",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 0
    head_origin = subprocess.run(
        ["git", "-C", str(origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    head_clone = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_origin == head_clone


def test_deliverable_well_formed_accepts_and_pushes(tmp_path: Path) -> None:
    """Build-mode deliverable accepts WITHOUT task_id (key delta vs routine)."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    _make_build_deliverable_commit(clone)
    rc = main(
        [
            "deliverable",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 0


def test_close_well_formed_accepts_and_pushes(tmp_path: Path) -> None:
    """Smoke test: imported routine verifier accepts build-mode close shape."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    _make_build_close_commit(clone)
    rc = main(
        [
            "close",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 0


# ---------------------------------------------------------------------------
# Deliverable verifier — build-mode specific behavior
# ---------------------------------------------------------------------------


def test_deliverable_does_not_require_task_id(tmp_path: Path) -> None:
    """The key build-mode property: deliverable verification does NOT read
    current.json's task_id. Verify by authoring an eager-claim with
    current.json that explicitly carries NO task_id, then verifying
    deliverable shape against a follow-on commit."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)  # explicitly no task_id
    _git(["push"], clone)
    _make_build_deliverable_commit(clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert ok, reason
    assert "verified" in reason


def test_deliverable_rejects_lifecycle_prefix(tmp_path: Path) -> None:
    """A commit using 'chore(session):' prefix must be refused — reserved
    for eager-claim and close only."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    (clone / "extra.md").write_text("body\n")
    _git(["add", "extra.md"], clone)
    _git(["commit", "-m", "chore(session): not-a-deliverable"], clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "chore(session):" in reason


def test_deliverable_rejects_non_conventional_subject(tmp_path: Path) -> None:
    """A commit with a free-form subject (no conventional-commits prefix)
    must be refused."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    (clone / "extra.md").write_text("body\n")
    _git(["add", "extra.md"], clone)
    _git(["commit", "-m", "just landed some stuff"], clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "conventional-commits" in reason


def test_deliverable_rejects_two_commits_ahead(tmp_path: Path) -> None:
    """HEAD must be exactly 1 commit ahead of remote/target."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    _make_build_deliverable_commit(clone)
    # Second deliverable on top — now 2 ahead
    (clone / "second.md").write_text("body\n")
    _git(["add", "second.md"], clone)
    _git(["commit", "-m", "feat(engine): second one"], clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "2 commits ahead" in reason


def test_deliverable_rejects_dirty_working_tree(tmp_path: Path) -> None:
    """Working tree with uncommitted changes must be refused."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    _make_build_deliverable_commit(clone)
    # Leave an uncommitted change
    (clone / "dirty.md").write_text("uncommitted\n")
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "working tree is not clean" in reason


# ---------------------------------------------------------------------------
# Eager-claim + close shape verifiers — imported from routine_lifecycle_push.
# Exhaustive coverage lives in test_routine_lifecycle_push.py. These tests
# confirm the build wrapper rejects malformed shapes correctly via the
# imported verifiers.
# ---------------------------------------------------------------------------


def test_eager_claim_rejects_wrong_subject(tmp_path: Path) -> None:
    """A commit with a non-eager-claim subject is refused."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0139"
    state["last_claimed"] = "S-0138"
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(json.dumps({"id": "S-0138"}) + "\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "feat: not-an-eager-claim"], clone)
    rc = main(
        [
            "eager-claim",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 2


def test_close_rejects_wrong_subject(tmp_path: Path) -> None:
    """A commit with a non-close subject is refused at close mode."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_build_eager_claim_commit(clone)
    _git(["push"], clone)
    # Author a fake-close: archive + current.json removal + register flip,
    # but with WRONG subject
    sess_dir = clone / "engine" / "session"
    (sess_dir / "archive").mkdir(exist_ok=True)
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "archive" / "S-0138.json").write_text(
        json.dumps({"id": "S-0138"}) + "\n"
    )
    (sess_dir / "current.json").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "feat: pretending to close"], clone)
    rc = main(
        [
            "close",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_dry_run_does_not_push(tmp_path: Path) -> None:
    """--dry-run verifies shape and reports, but does not push."""
    origin, clone = _make_origin_with_clone(tmp_path)
    head_before_origin = subprocess.run(
        ["git", "-C", str(origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _make_build_eager_claim_commit(clone)
    rc = main(
        [
            "eager-claim",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
            "--dry-run",
        ]
    )
    assert rc == 0
    head_after_origin = subprocess.run(
        ["git", "-C", str(origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert head_before_origin == head_after_origin


def test_push_rejected_non_fast_forward_returns_3(tmp_path: Path) -> None:
    """When origin has a commit the clone doesn't, the push is rejected
    with exit code 3 (non-fast-forward)."""
    origin, clone = _make_origin_with_clone(tmp_path)
    # Make a second clone, commit + push to origin so origin is ahead
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", str(origin), str(other)], capture_output=True, check=True
    )
    _git(["config", "user.email", "other@example.com"], other)
    _git(["config", "user.name", "Other"], other)
    (other / "from_other.md").write_text("from other clone\n")
    _git(["add", "from_other.md"], other)
    _git(["commit", "-m", "feat: from other clone"], other)
    _git(["push"], other)
    # Now the first clone's eager-claim will be rejected — origin has a
    # commit clone doesn't.
    _make_build_eager_claim_commit(clone)
    rc = main(
        [
            "eager-claim",
            "--repo-root",
            str(clone),
            "--remote",
            "origin",
            "--target-branch",
            "main",
        ]
    )
    assert rc == 3
