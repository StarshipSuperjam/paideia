"""Tests for routine_lifecycle_push.py — Phase 1 of S-0060.

Coverage targets per ADR 0054 / S-0060 plan:
- Per-mode well-formed accept (3 tests)
- Per-mode shape-verification rejects (4+ predicates per mode = 12+ tests)
- Push-failure paths (3 tests)
- Edge cases (2 tests)

Total: 20 tests, all running against tmp-dir bare-repo + clone fixtures.
The user's S-0060 directive: "test, test, test."
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_lifecycle_push import (  # noqa: E402
    CLOSE_ALLOWED_GLOBS,
    get_parent_repo_path,
    main,
    parent_ff,
    push,
    verify_close_shape,
    verify_deliverable_shape,
    verify_eager_claim_shape,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_origin_with_clone(tmp_path: Path) -> tuple[Path, Path]:
    """Bare origin + clone with one commit on main, plus an initial
    register_state.json + auto_target.json so subsequent commits can diff
    register_state cleanly. Same fixture pattern as test_routine_eager_claim_recovery.py.
    """
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    # --initial-branch=main on `git init --bare` ensures the bare repo's
    # HEAD points at refs/heads/main regardless of the host's
    # init.defaultBranch config; without it, GitHub Actions runners
    # (where the default is master) leave HEAD pointing to a nonexistent
    # master ref after the clone pushes main, which silently breaks
    # non-fast-forward push tests and HEAD~1 reset tests (S-0131 CI
    # surfacing). Requires git ≥ 2.28; CI ships 2.53.
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

    # Initial state files matching the project shape
    sess_dir = clone / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "register_state.json").write_text(
        json.dumps(
            {
                "next_id": "0060",
                "last_claimed": "S-0059",
                "current_status": "closed",
            }
        )
        + "\n"
    )
    (sess_dir / "auto_target.json").write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "id": "P5-05",
                        "name": "Political philosophy seed",
                        "status": "pending",
                        "scope_lock": {
                            "allowed_paths": [
                                "product/seed-graph/migrations/0100_*.sql",
                                "product/seed-graph/migrations/ROUTING.md",
                            ]
                        },
                    },
                ],
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


def _make_eager_claim_commit(clone: Path, slot: str = "S-0060") -> str:
    """Author a well-formed eager-claim commit. Returns SHA."""
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0061"
    state["last_claimed"] = slot
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(
        json.dumps({"id": slot, "status": "in_progress", "task_id": "P5-05"}) + "\n"
    )
    (sess_dir / "current_plan.md").write_text(
        'paths_to_modify: ["product/seed-graph/migrations/0100_*.sql"]\n'
        "criteria_addressed: [0]\n\nplan body\n"
    )
    target = json.loads((sess_dir / "auto_target.json").read_text())
    target["tasks"][0]["status"] = "in_progress"
    (sess_dir / "auto_target.json").write_text(json.dumps(target) + "\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", f"chore(session): eager-claim {slot} — test"], clone)
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


def _make_deliverable_commit(
    clone: Path, path: str = "product/seed-graph/migrations/0100_test.sql"
) -> str:
    """Author a well-formed deliverable commit. Returns SHA."""
    full = clone / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("-- deliverable\n")
    _git(["add", path], clone)
    _git(["commit", "-m", "feat(seed): add political philosophy nodes"], clone)
    return _git(["rev-parse", "HEAD"], clone).stdout.strip()


def _make_close_commit(clone: Path, slot: str = "S-0060") -> str:
    """Author a well-formed close commit. Returns SHA."""
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
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
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
    # Confirm the bare origin received the commit
    head_origin = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    head_clone = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_origin == head_clone


def test_deliverable_well_formed_accepts_and_pushes(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)  # sync the eager-claim so deliverable is 1 ahead
    _make_deliverable_commit(clone)
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
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)  # eager-claim synced
    _make_close_commit(clone)
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
# Eager-claim shape rejects
# ---------------------------------------------------------------------------


def test_eager_claim_rejects_when_two_commits_ahead(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    # Add a second commit on top
    (clone / "extra").write_text("extra\n")
    _git(["add", "extra"], clone)
    _git(["commit", "-m", "feat: extra"], clone)
    ok, reason = verify_eager_claim_shape(clone, "origin", "main")
    assert not ok
    assert "2 commits ahead" in reason


def test_eager_claim_rejects_when_subject_pattern_wrong(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    # Build a commit with wrong subject but eager-claim diff shape
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0061"
    state["last_claimed"] = "S-0060"
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "feat: not an eager-claim subject"], clone)
    ok, reason = verify_eager_claim_shape(clone, "origin", "main")
    assert not ok
    assert "eager-claim pattern" in reason


def test_eager_claim_rejects_when_diff_touches_outside_set(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    # Stage an out-of-scope path alongside the legit eager-claim shape
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0061"
    state["last_claimed"] = "S-0060"
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    (clone / "engine" / "TAINTED.md").write_text("not allowed\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "chore(session): eager-claim S-0060 — tainted"], clone)
    ok, reason = verify_eager_claim_shape(clone, "origin", "main")
    assert not ok
    assert "TAINTED.md" in reason


def test_eager_claim_rejects_when_register_state_doesnt_bump_one(
    tmp_path: Path,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0062"  # bump by 2 instead of 1
    state["last_claimed"] = "S-0061"
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(json.dumps({"id": "S-0061"}) + "\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "chore(session): eager-claim S-0061 — bad bump"], clone)
    ok, reason = verify_eager_claim_shape(clone, "origin", "main")
    assert not ok
    assert "bump by exactly 1" in reason


def test_eager_claim_rejects_when_current_json_already_existed(
    tmp_path: Path,
) -> None:
    """current.json must be newly created (status 'A'); modification ('M') refused."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess_dir = clone / "engine" / "session"
    # Pre-create current.json on main so the eager-claim modifies rather than creates
    (sess_dir / "current.json").write_text(json.dumps({"id": "stale"}) + "\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "chore: pre-existing current.json"], clone)
    _git(["push"], clone)

    # Now eager-claim modifies (not creates)
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["next_id"] = "0061"
    state["last_claimed"] = "S-0060"
    state["current_status"] = "in_progress"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").write_text(
        json.dumps({"id": "S-0060", "status": "in_progress"}) + "\n"
    )
    _git(["add", "."], clone)
    _git(
        ["commit", "-m", "chore(session): eager-claim S-0060 — modifies stale"],
        clone,
    )
    ok, reason = verify_eager_claim_shape(clone, "origin", "main")
    assert not ok
    assert "NEWLY CREATED" in reason


# ---------------------------------------------------------------------------
# Deliverable shape rejects
# ---------------------------------------------------------------------------


def test_deliverable_rejects_when_subject_uses_chore_session_prefix(
    tmp_path: Path,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    full = clone / "product/seed-graph/migrations/0100_test.sql"
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("-- d\n")
    _git(["add", "."], clone)
    _git(
        ["commit", "-m", "chore(session): would-be lifecycle subject"],
        clone,
    )
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "chore(session):" in reason
    assert "reserved" in reason.lower()


def test_deliverable_rejects_when_subject_not_conventional_commits(
    tmp_path: Path,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    full = clone / "product/seed-graph/migrations/0100_test.sql"
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("-- d\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "WIP whatever"], clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "conventional-commits" in reason


def test_deliverable_rejects_when_path_outside_scope_lock(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    # Path outside scope_lock and outside operational allowlist
    full = clone / "product/seed-graph/migrations/9999_outside.sql"
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("-- nope\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "feat(seed): out of scope"], clone)
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "outside scope_lock" in reason
    assert "9999_outside.sql" in reason


def test_deliverable_rejects_when_working_tree_dirty(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    _make_deliverable_commit(clone)
    # Dirty the working tree
    (clone / "product/seed-graph/migrations/0100_test.sql").write_text(
        "-- modified after commit\n"
    )
    ok, reason = verify_deliverable_shape(clone, "origin", "main")
    assert not ok
    assert "working tree is not clean" in reason


# ---------------------------------------------------------------------------
# Close shape rejects
# ---------------------------------------------------------------------------


def test_close_rejects_when_archive_file_not_created(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    (sess_dir / "current.json").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — missing archive"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert not ok
    assert "CREATE engine/session/archive" in reason


def test_close_rejects_when_current_json_not_deleted(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    # Do NOT delete current.json
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — current.json kept"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert not ok
    assert "DELETE engine/session/current.json" in reason


def test_close_rejects_when_register_state_doesnt_flip_to_closed(
    tmp_path: Path,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    sess_dir = clone / "engine" / "session"
    # Don't flip register state
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    (sess_dir / "current.json").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — state not flipped"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert not ok
    assert "in_progress" in reason
    assert "closed" in reason


def test_close_rejects_when_diff_touches_arbitrary_paths(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)
    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    (sess_dir / "current.json").unlink()
    # Touch an arbitrary unrelated path
    (clone / "engine" / "RANDOM.md").write_text("hi\n")
    _git(["add", "-A"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — touched random"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert not ok
    assert "RANDOM.md" in reason


# ---------------------------------------------------------------------------
# Issue #17 regressions — close-mode allowlist must match documented operational allowlist
# ---------------------------------------------------------------------------


def test_close_accepts_with_current_plan_md_deletion(tmp_path: Path) -> None:
    """Issue #17 literal repro: close commit deletes current_plan.md alongside
    current.json; mode must accept. Pre-fix this case REFUSED with exit 2 in the
    routine session for S-0061; post-fix it accepts because current_plan.md is
    in check_routine_scope.OPERATIONAL_ALLOWLIST."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)

    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    (sess_dir / "current.json").unlink()
    # The literal Issue #17 trigger: close also deletes current_plan.md
    (sess_dir / "current_plan.md").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — current_plan deleted"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert ok, (
        f"Issue #17 regression: close shape with current_plan.md deletion rejected: {reason}"
    )


def test_close_accepts_with_archive_creation_and_current_plan_deletion(
    tmp_path: Path,
) -> None:
    """Full close shape including BOTH archive creation AND current_plan.md
    deletion (the realistic post-S-0062 close shape). Verifies both globs
    resolve through the canonical OPERATIONAL_ALLOWLIST glob match."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)

    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(
        json.dumps({"id": "S-0060", "outcome_summary": "x"}) + "\n"
    )
    (sess_dir / "current.json").unlink()
    (sess_dir / "current_plan.md").unlink()
    # Also touch STATE.md and ENGINE_LOG.md (operational close-time edits)
    (clone / "engine" / "STATE.md").write_text("# State\n\nupdated\n")
    (clone / "engine" / "ENGINE_LOG.md").write_text("# Log\n\nupdated\n")
    _git(["add", "-A"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — full close shape"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert ok, f"full close shape rejected: {reason}"


def test_close_rejects_when_archive_path_format_wrong(tmp_path: Path) -> None:
    """Archive file at wrong-format path (5 digits instead of 4) is refused.
    Confirms the strict archive_strict_re still enforces canonical S-NNNN.json."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)

    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    # Wrong: 5-digit suffix instead of 4
    (archive_dir / "S-12345.json").write_text(json.dumps({"id": "S-12345"}) + "\n")
    (sess_dir / "current.json").unlink()
    _git(["add", "-A", "engine/session"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — bad archive name"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert not ok
    assert "must CREATE engine/session/archive/S-NNNN.json" in reason


def test_close_allowed_globs_derived_from_canonical_operational_allowlist() -> None:
    """Structural test: CLOSE_ALLOWED_GLOBS must contain every entry of
    check_routine_scope.OPERATIONAL_ALLOWLIST plus engine/STATE.md plus
    engine/build_readiness/*.md (per Issue #139). Locks in the canonical-
    source alignment so a future drift (constant added to one list but not
    the other) is caught at test time."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_routine_scope  # noqa: PLC0415

    canonical = set(check_routine_scope.OPERATIONAL_ALLOWLIST)
    close_set = set(CLOSE_ALLOWED_GLOBS)
    missing = canonical - close_set
    assert not missing, f"CLOSE_ALLOWED_GLOBS is missing canonical entries: {missing}"
    assert "engine/STATE.md" in close_set, (
        "CLOSE_ALLOWED_GLOBS must include engine/STATE.md "
        "(close commits update STATE.md per session-shutdown-sequence)"
    )
    assert "engine/build_readiness/*.md" in close_set, (
        "CLOSE_ALLOWED_GLOBS must include engine/build_readiness/*.md "
        "(Issue #139: first-exercise readiness notes carry session-tied "
        "empirical records appended at close per ADR 0053)"
    )


def test_close_accepts_build_readiness_md_edit(tmp_path: Path) -> None:
    """Issue #139: A close commit that touches engine/build_readiness/*.md
    must be accepted, not refused as out-of-allowlist."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)

    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "S-0060.json").write_text(json.dumps({"id": "S-0060"}) + "\n")
    (sess_dir / "current.json").unlink()
    (sess_dir / "current_plan.md").unlink()
    # Touch a build_readiness readiness note as part of close (the Issue
    # #139 pattern — first-exercise readiness empirical record).
    readiness_dir = clone / "engine" / "build_readiness"
    readiness_dir.mkdir(parents=True, exist_ok=True)
    (readiness_dir / "fake_mechanism_first_exercise.md").write_text(
        "# Fake mechanism\n\n## Empirical record\n\n- S-0060: T1-A closed.\n"
    )
    _git(["add", "-A"], clone)
    _git(
        ["commit", "-m", "chore(session): close S-0060 — with readiness-note edit"],
        clone,
    )
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert ok, f"close-with-readiness-note rejected: {reason}"


def test_close_detects_rename_as_add_plus_delete(tmp_path: Path) -> None:
    """Rename-detection fix: `git mv current.json archive/S-NNNN.json` must
    be reported by get_changed_paths_since as separate D + A statuses, not
    as a single R-status rename. The verifier requires both."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _make_eager_claim_commit(clone)
    _git(["push"], clone)

    sess_dir = clone / "engine" / "session"
    state = json.loads((sess_dir / "register_state.json").read_text())
    state["current_status"] = "closed"
    (sess_dir / "register_state.json").write_text(json.dumps(state) + "\n")
    archive_dir = sess_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    # Use `git mv` (the discipline session-shutdown-sequence step 13 prescribes).
    # Before --no-renames flag, this surfaced as R098 and the close verifier
    # missed both required statuses.
    _git(
        ["mv", "engine/session/current.json", "engine/session/archive/S-0060.json"],
        clone,
    )
    # Modify the archive file slightly to mimic close-time field changes
    archive_data = json.loads((archive_dir / "S-0060.json").read_text())
    archive_data["status"] = "closed"
    (archive_dir / "S-0060.json").write_text(json.dumps(archive_data) + "\n")
    (sess_dir / "current_plan.md").unlink()
    _git(["add", "-A"], clone)
    _git(["commit", "-m", "chore(session): close S-0060 — via git mv"], clone)
    ok, reason = verify_close_shape(clone, "origin", "main")
    assert ok, f"git-mv close rejected (rename-detection bug): {reason}"


# ---------------------------------------------------------------------------
# Push-failure paths
# ---------------------------------------------------------------------------


def test_push_failure_non_fast_forward_returns_3(tmp_path: Path) -> None:
    """Bare origin gets a commit beyond local; push from clone is rejected non-FF."""
    _origin, clone = _make_origin_with_clone(tmp_path)

    # Second clone advances origin/main without telling the first
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", str(_origin), str(other)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], other)
    _git(["config", "user.name", "Test"], other)
    (other / "ahead").write_text("ahead\n")
    _git(["add", "."], other)
    _git(["commit", "-m", "feat: ahead"], other)
    _git(["push"], other)

    # First clone makes a local commit and tries to push
    (clone / "local").write_text("local\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "feat: local"], clone)

    code, _stdout, stderr = push(clone, "origin", "main")
    assert code == 3
    assert "rejected" in stderr.lower() or "non-fast-forward" in stderr.lower()


def test_push_failure_unreachable_remote_returns_4(tmp_path: Path) -> None:
    """Pointing remote at unreachable URL returns exit 4."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _git(
        [
            "remote",
            "set-url",
            "origin",
            "https://nonexistent.invalid.example/repo.git",
        ],
        clone,
    )
    code, _stdout, stderr = push(clone, "origin", "main")
    assert code in (4, 5)  # network failure or generic git error
    if code == 4:
        assert (
            "could not resolve" in stderr.lower()
            or "connection" in stderr.lower()
            or "network" in stderr.lower()
            or "timed out" in stderr.lower()
        )


def test_push_failure_missing_remote_returns_5(tmp_path: Path) -> None:
    """Removing origin entirely returns exit 5 (generic git error)."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _git(["remote", "remove", "origin"], clone)
    code, _stdout, _stderr = push(clone, "origin", "main")
    assert code == 5


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_main_refuses_with_exit_2_on_verification_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End-to-end: main() returns 2 and does NOT push when shape verification fails."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    # Make HEAD not match eager-claim shape (no commit at all beyond initial)
    rc = main(["eager-claim", "--repo-root", str(clone)])
    assert rc == 2
    captured = capsys.readouterr()
    assert "REFUSED" in captured.err
    # Bare origin should NOT have moved
    head_origin = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    head_clone_initial = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert head_origin == head_clone_initial


def test_dry_run_verifies_but_does_not_push(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--dry-run on a well-formed eager-claim verifies and reports without pushing."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    head_before_origin = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _make_eager_claim_commit(clone)
    rc = main(["eager-claim", "--repo-root", str(clone), "--dry-run"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "dry-run" in captured.err
    assert "verified" in captured.err
    # Origin must not have moved
    head_after_origin = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert head_before_origin == head_after_origin


# ---------------------------------------------------------------------------
# Parent-side FF post-push (the gap closed by this session)
# ---------------------------------------------------------------------------


def _make_clone_with_worktree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Returns (origin, clone, worktree). Clone is on main with the standard
    initial state; worktree is a linked worktree on feature branch
    `claude/test-worktree`, sharing the clone's `.git` directory."""
    origin, clone = _make_origin_with_clone(tmp_path)
    worktree = tmp_path / "worktree"
    _git(
        ["worktree", "add", "-b", "claude/test-worktree", str(worktree)],
        clone,
    )
    _git(["config", "user.email", "test@example.com"], worktree)
    _git(["config", "user.name", "Test"], worktree)
    return origin, clone, worktree


def test_get_parent_repo_path_resolves_for_linked_worktree(tmp_path: Path) -> None:
    """From a linked worktree, get_parent_repo_path returns the clone's path."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)
    parent = get_parent_repo_path(worktree)
    assert parent is not None
    assert parent.resolve() == clone.resolve()


def test_get_parent_repo_path_returns_self_for_parent(tmp_path: Path) -> None:
    """From the parent (clone), get_parent_repo_path returns the same path."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    parent = get_parent_repo_path(clone)
    assert parent is not None
    assert parent.resolve() == clone.resolve()


def test_parent_ff_advances_parent_main_after_push(tmp_path: Path) -> None:
    """After pushing from worktree, parent_ff advances parent's local main."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()

    # Make a commit on the worktree's branch and push to main
    (worktree / "wt-file").write_text("hi\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: from worktree"], worktree)
    _git(["push", "origin", "HEAD:main"], worktree)

    # Parent main is still at the prior commit (push advanced origin/main only)
    parent_head_after_push = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after_push == parent_head_before

    # parent_ff brings parent's main current
    ok, reason = parent_ff(worktree, "main")
    assert ok, f"expected success, got: {reason}"
    assert "parent main FF'd to" in reason

    parent_head_after_ff = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after_ff != parent_head_before
    worktree_head = _git(["rev-parse", "HEAD"], worktree).stdout.strip()
    assert parent_head_after_ff == worktree_head


def test_parent_ff_noop_when_called_from_parent(tmp_path: Path) -> None:
    """parent_ff returns success no-op when called against the parent itself."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    ok, reason = parent_ff(clone, "main")
    assert ok
    assert "no-op" in reason


def test_parent_ff_refuses_when_parent_on_different_branch(tmp_path: Path) -> None:
    """parent_ff refuses if the parent is checked out on a non-target branch."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    # Switch parent to a different branch (not main)
    _git(["checkout", "-b", "experiment"], clone)

    # Make a commit on the worktree and push to main
    (worktree / "wt-file").write_text("hi\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: from worktree"], worktree)
    _git(["push", "origin", "HEAD:main"], worktree)

    parent_head_before = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    ok, reason = parent_ff(worktree, "main")
    assert not ok
    assert "experiment" in reason
    # Parent's HEAD must not have moved
    parent_head_after = _git(["rev-parse", "HEAD"], clone).stdout.strip()
    assert parent_head_after == parent_head_before


def test_main_invokes_parent_ff_after_successful_eager_claim_push(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End-to-end: main(eager-claim) push success advances parent's local main."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()
    _make_eager_claim_commit(worktree)

    rc = main(["eager-claim", "--repo-root", str(worktree)])
    assert rc == 0

    captured = capsys.readouterr()
    assert "parent main FF'd to" in captured.err

    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after != parent_head_before
    worktree_head = _git(["rev-parse", "HEAD"], worktree).stdout.strip()
    assert parent_head_after == worktree_head


def test_main_returns_zero_when_parent_ff_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """parent_ff failure does NOT propagate to main()'s exit code — best-effort."""
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    # Force parent_ff to refuse: switch parent off main
    _git(["checkout", "-b", "experiment"], clone)

    _make_eager_claim_commit(worktree)
    rc = main(["eager-claim", "--repo-root", str(worktree)])
    assert rc == 0  # push succeeded; parent_ff failure is non-fatal

    captured = capsys.readouterr()
    assert "parent FF best-effort failed" in captured.err
    # Origin/main DID advance (push succeeded)
    origin_head = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    worktree_head = _git(["rev-parse", "HEAD"], worktree).stdout.strip()
    assert origin_head == worktree_head


# ---------------------------------------------------------------------------
# parent_ff identical-content auto-recovery (Issue #107, S-0150)
# ---------------------------------------------------------------------------


def _setup_overwrite_refusal_scenario(
    tmp_path: Path,
    parent_working_tree_contents: dict[str, str],
) -> tuple[Path, Path, Path, str]:
    """Set up the canonical 'would be overwritten by merge' scenario.

    Steps:
    1. Initialize origin + clone + worktree, all at the same starting commit.
    2. Create files in the clone (= parent) and commit + push: these are
       the files whose content will diverge in the working tree.
    3. From the worktree, modify those files with NEW content
       (``v2_<name>``), commit, and push to origin/main. Now origin/main
       is one commit ahead of the parent's main, and the FF target carries
       the v2 content.
    4. Write ``parent_working_tree_contents`` into the parent's working
       tree as uncommitted modifications. Whether these match origin/main
       (= auto-recoverable) or diverge (= bail) is the test parameter.

    Returns ``(origin, clone, worktree, ref_v2_path)`` where ref_v2_path
    is one of the file paths whose ``origin/main`` content is ``v2_<name>``.
    """
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    # Pre-create the files in the clone at v1 (initial committed state).
    file_paths = list(parent_working_tree_contents.keys())
    for f in file_paths:
        target_path = clone / f
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(f"v1_{f}\n")
    _git(["add", *file_paths], clone)
    _git(["commit", "-m", "feat: seed initial files at v1"], clone)
    _git(["push", "origin", "main"], clone)

    # Pull the v1 commit into the worktree, modify each file to v2, push.
    _git(["pull", "origin", "main"], worktree)
    for f in file_paths:
        wt_target = worktree / f
        wt_target.parent.mkdir(parents=True, exist_ok=True)
        wt_target.write_text(f"v2_{f}\n")
    _git(["add", *file_paths], worktree)
    _git(["commit", "-m", "feat: bump files to v2"], worktree)
    _git(["push", "origin", "HEAD:main"], worktree)

    # Now write the test's chosen working-tree contents into the parent.
    # Clone's HEAD is still at v1; FF target (origin/main) is at v2.
    for f, content in parent_working_tree_contents.items():
        (clone / f).write_text(content)

    return _origin, clone, worktree, file_paths[0]


def test_parent_ff_auto_recovers_identical_content_single_file(
    tmp_path: Path,
) -> None:
    """Single-file overwrite refusal with identical content → auto-recovery succeeds."""
    _origin, clone, worktree, _f = _setup_overwrite_refusal_scenario(
        tmp_path,
        {"settings.json": "v2_settings.json\n"},
    )

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()
    origin_head = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert parent_head_before != origin_head, "fixture must put parent behind origin"

    ok, reason = parent_ff(worktree, "main")
    assert ok, f"expected auto-recovery success, got: {reason}"
    assert (
        "auto-recovered from identical-content overwrite refusal on 1 file(s)" in reason
    )

    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after == origin_head, "FF must have advanced parent's main"


def test_parent_ff_auto_recovers_identical_content_multi_file(
    tmp_path: Path,
) -> None:
    """Multi-file overwrite refusal, all identical → auto-recovery handles batch."""
    _origin, clone, worktree, _f = _setup_overwrite_refusal_scenario(
        tmp_path,
        {
            "a.txt": "v2_a.txt\n",
            "b.txt": "v2_b.txt\n",
            "nested/c.txt": "v2_nested/c.txt\n",
        },
    )

    origin_head = subprocess.run(
        ["git", "-C", str(_origin), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    ok, reason = parent_ff(worktree, "main")
    assert ok, f"expected auto-recovery success, got: {reason}"
    assert (
        "auto-recovered from identical-content overwrite refusal on 3 file(s)" in reason
    )

    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after == origin_head


def test_parent_ff_bails_on_diverged_content_single_file(tmp_path: Path) -> None:
    """Overwrite refusal with diverged working-tree content → bail; state unchanged."""
    _origin, clone, worktree, _f = _setup_overwrite_refusal_scenario(
        tmp_path,
        {"settings.json": "v3_diverged\n"},  # Different from v2 (origin/main) AND v1
    )

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()
    wt_content_before = (clone / "settings.json").read_text()

    ok, reason = parent_ff(worktree, "main")
    assert not ok, f"expected bail, got success: {reason}"
    assert "working-tree diverges from origin/main" in reason
    assert "settings.json" in reason
    assert "manual recovery required" in reason

    # Parent HEAD must NOT have moved (no state mutation on bail)
    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after == parent_head_before
    # Working-tree file must NOT have been touched
    wt_content_after = (clone / "settings.json").read_text()
    assert wt_content_after == wt_content_before


def test_parent_ff_bails_when_one_of_many_files_diverges(tmp_path: Path) -> None:
    """Multi-file refusal where ONE file diverges → bail; report the diverged file."""
    _origin, clone, worktree, _f = _setup_overwrite_refusal_scenario(
        tmp_path,
        {
            "a.txt": "v2_a.txt\n",  # identical to origin/main
            "b.txt": "v3_b_diverged\n",  # diverged
            "c.txt": "v2_c.txt\n",  # identical to origin/main
        },
    )

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()
    wt_a_before = (clone / "a.txt").read_text()

    ok, reason = parent_ff(worktree, "main")
    assert not ok
    assert "working-tree diverges from origin/main" in reason
    assert "b.txt" in reason
    # a.txt and c.txt should NOT appear in the diverged list
    assert "'a.txt'" not in reason
    assert "'c.txt'" not in reason

    # No state mutation
    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after == parent_head_before
    # All working-tree files preserved (no partial checkout)
    assert (clone / "a.txt").read_text() == wt_a_before


def test_parent_ff_passes_through_non_overwrite_refusal(tmp_path: Path) -> None:
    """Non-overwrite refusal (e.g., non-fast-forward) → 'refused: ...' unchanged.

    Regression guard: the auto-recovery path must NOT fire on refusal classes
    other than the 'would be overwritten by merge' signature.
    """
    _origin, clone, worktree = _make_clone_with_worktree(tmp_path)

    # Create divergent history: commit on parent's main AND push a different commit
    # from the worktree, so origin/main has a commit the parent doesn't, AND the
    # parent has a commit origin doesn't — merge --ff-only will fail with
    # "Not possible to fast-forward", which does NOT match the overwrite signature.
    (clone / "parent-only.txt").write_text("parent\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "feat: parent-only commit"], clone)

    (worktree / "wt-only.txt").write_text("wt\n")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "feat: worktree-only commit"], worktree)
    _git(["push", "origin", "HEAD:main"], worktree)

    parent_head_before = _git(["rev-parse", "main"], clone).stdout.strip()

    ok, reason = parent_ff(worktree, "main")
    assert not ok
    assert reason.startswith("refused: ")
    # The new auto-recovery path's signature strings must NOT appear in the reason
    assert "auto-recovered" not in reason
    assert "working-tree diverges" not in reason

    # State unchanged
    parent_head_after = _git(["rev-parse", "main"], clone).stdout.strip()
    assert parent_head_after == parent_head_before
