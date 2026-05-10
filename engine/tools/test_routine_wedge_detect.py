"""Tests for routine_wedge_detect.py — Issue #58 systemic fix.

Coverage targets per ADR 0060:
- Per-conjunct mechanical predicate (clean / wedge / ambiguous).
- Idempotent HANDOFF authoring (second invocation does NOT duplicate).
- ``--dry-run`` does not mutate state.
- ``--skip-gh`` proceeds with HANDOFF-only when gh is unavailable.

Tests run against tmp-dir bare-repo + clone fixtures, mirroring the
pattern used by ``test_routine_lifecycle_push.py``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_wedge_detect import (  # noqa: E402
    HANDOFF_HEADING_TEMPLATE,
    archive_exists_at_head,
    detect_wedge,
    handoff_section_exists,
    main,
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

    sess_dir = clone / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "register_state.json").write_text(
        json.dumps(
            {
                "next_id": "0001",
                "last_claimed": None,
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
                        "id": "T-DEMO",
                        "name": "Demo task",
                        "status": "pending",
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


def _stage_wedge_state(clone: Path, slot: str = "S-0117") -> None:
    """Mutate the clone into the wedge shape: register in_progress, current.json
    in_progress, auto_target.task in_progress, no archive."""
    sess = clone / "engine" / "session"
    register = json.loads((sess / "register_state.json").read_text())
    register["next_id"] = "0118"
    register["last_claimed"] = slot
    register["current_status"] = "in_progress"
    (sess / "register_state.json").write_text(json.dumps(register) + "\n")

    (sess / "current.json").write_text(
        json.dumps(
            {
                "id": slot,
                "mode": "routine",
                "task_id": "T-DEMO",
                "status": "in_progress",
            }
        )
        + "\n"
    )

    target = json.loads((sess / "auto_target.json").read_text())
    target["tasks"][0]["status"] = "in_progress"
    (sess / "auto_target.json").write_text(json.dumps(target) + "\n")

    _git(["add", "engine/session"], clone)
    _git(
        ["commit", "-m", "chore(session): eager-claim S-0117 — routine task T-DEMO"],
        clone,
    )
    _git(["push", "-u", "origin", "main"], clone)


# ---------------------------------------------------------------------------
# detect_wedge predicate
# ---------------------------------------------------------------------------


def test_clean_state_returns_clean(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    disposition, reason, payload = detect_wedge(clone)
    assert disposition == "clean"
    assert payload is None


def test_full_wedge_shape_returns_wedge(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    disposition, reason, payload = detect_wedge(clone)
    assert disposition == "wedge", f"reason={reason!r}"
    assert payload is not None
    assert payload["session_id"] == "S-0117"
    assert payload["task_id"] == "T-DEMO"


def test_archive_exists_at_head_clears_wedge(tmp_path: Path) -> None:
    """Archive existing at HEAD means close happened — ambiguous, not wedge."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    # Now author an archive WITHOUT clearing register/current — simulates
    # half-applied close.
    archive = clone / "engine" / "session" / "archive"
    archive.mkdir()
    (archive / "S-0117.json").write_text('{"id": "S-0117", "status": "closed"}\n')
    _git(["add", "engine/session/archive"], clone)
    _git(["commit", "-m", "test: stage half-applied close"], clone)
    _git(["push"], clone)
    disposition, reason, _payload = detect_wedge(clone)
    assert disposition == "ambiguous"
    assert reason is not None and "archive" in reason.lower()


def test_register_closed_returns_clean(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    # No staging; register_state.json starts at current_status: closed
    disposition, reason, _payload = detect_wedge(clone)
    assert disposition == "clean"
    assert reason is not None and "current_status" in reason


def test_no_task_id_returns_clean(tmp_path: Path) -> None:
    """Interactive sessions don't carry task_id — not a routine wedge."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess = clone / "engine" / "session"
    register = json.loads((sess / "register_state.json").read_text())
    register["current_status"] = "in_progress"
    (sess / "register_state.json").write_text(json.dumps(register) + "\n")
    (sess / "current.json").write_text(
        json.dumps({"id": "S-0099", "mode": "build", "status": "in_progress"}) + "\n"
    )
    _git(["add", "engine/session"], clone)
    _git(["commit", "-m", "interactive eager-claim"], clone)
    _git(["push"], clone)
    disposition, reason, _payload = detect_wedge(clone)
    assert disposition == "clean"
    assert reason is not None and "task_id" in reason.lower()


def test_register_says_in_progress_but_current_missing_is_ambiguous(
    tmp_path: Path,
) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess = clone / "engine" / "session"
    register = json.loads((sess / "register_state.json").read_text())
    register["current_status"] = "in_progress"
    (sess / "register_state.json").write_text(json.dumps(register) + "\n")
    _git(["add", "engine/session/register_state.json"], clone)
    _git(["commit", "-m", "anomaly: register says in_progress but no current"], clone)
    _git(["push"], clone)
    disposition, reason, _payload = detect_wedge(clone)
    assert disposition == "ambiguous"


def test_head_ahead_of_origin_is_ambiguous(tmp_path: Path) -> None:
    """HEAD ahead of origin/main means routine may still be running."""
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    # Now make a new local commit that hasn't been pushed.
    (clone / "extra.txt").write_text("not yet pushed\n")
    _git(["add", "extra.txt"], clone)
    _git(["commit", "-m", "in-flight work"], clone)
    disposition, reason, _payload = detect_wedge(clone)
    assert disposition == "ambiguous"
    assert reason is not None and "ahead" in reason.lower()


# ---------------------------------------------------------------------------
# CLI / idempotency
# ---------------------------------------------------------------------------


def test_main_clean_returns_0(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    rc = main(["--repo-root", str(clone), "--skip-gh", "--skip-push"])
    assert rc == 0


def test_main_dry_run_on_wedge_returns_2_no_mutation(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    handoff = clone / "HANDOFF.md"
    assert not handoff.exists()
    rc = main(["--repo-root", str(clone), "--skip-gh", "--dry-run"])
    assert rc == 2
    assert not handoff.exists(), "dry-run must not mutate state"


def test_main_wedge_authors_handoff_and_returns_2(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    handoff = clone / "HANDOFF.md"
    rc = main(["--repo-root", str(clone), "--skip-gh", "--skip-push"])
    assert rc == 2
    assert handoff.exists()
    body = handoff.read_text()
    assert HANDOFF_HEADING_TEMPLATE.format(session_id="S-0117") in body
    assert "T-DEMO" in body
    # Disposition must be present so the audit-handoff-dispositions
    # gate accepts the section.
    assert "**Disposition:**" in body
    # The wedge-detect commit landed.
    log = _git(["log", "--format=%s", "-n", "1", "HEAD"], clone).stdout.strip()
    assert log.startswith("chore(session): wedge-detect-and-pause for S-0117")


def test_main_idempotent_no_double_author(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    _stage_wedge_state(clone)
    rc1 = main(["--repo-root", str(clone), "--skip-gh", "--skip-push"])
    assert rc1 == 2
    handoff = clone / "HANDOFF.md"
    body_first = handoff.read_text()
    occurrences_first = body_first.count(
        HANDOFF_HEADING_TEMPLATE.format(session_id="S-0117")
    )
    assert occurrences_first == 1

    # Re-run the tool against the same wedged state.
    rc2 = main(["--repo-root", str(clone), "--skip-gh", "--skip-push"])
    assert rc2 == 2  # still wedge
    body_second = handoff.read_text()
    occurrences_second = body_second.count(
        HANDOFF_HEADING_TEMPLATE.format(session_id="S-0117")
    )
    assert occurrences_second == 1, (
        f"second invocation should not duplicate the section; "
        f"found {occurrences_second}"
    )


def test_main_ambiguous_returns_3(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    sess = clone / "engine" / "session"
    register = json.loads((sess / "register_state.json").read_text())
    register["current_status"] = "in_progress"
    (sess / "register_state.json").write_text(json.dumps(register) + "\n")
    _git(["add", "engine/session/register_state.json"], clone)
    _git(["commit", "-m", "anomaly"], clone)
    _git(["push"], clone)
    rc = main(["--repo-root", str(clone), "--skip-gh", "--skip-push"])
    assert rc == 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_archive_exists_at_head_helper(tmp_path: Path) -> None:
    _origin, clone = _make_origin_with_clone(tmp_path)
    assert archive_exists_at_head(clone, "S-0001") is False
    archive = clone / "engine" / "session" / "archive"
    archive.mkdir()
    (archive / "S-0001.json").write_text("{}\n")
    _git(["add", "."], clone)
    _git(["commit", "-m", "add archive"], clone)
    assert archive_exists_at_head(clone, "S-0001") is True
    assert archive_exists_at_head(clone, "S-9999") is False


def test_handoff_section_exists_helper(tmp_path: Path) -> None:
    handoff = tmp_path / "HANDOFF.md"
    assert handoff_section_exists(handoff, "S-0001") is False
    handoff.write_text("# HANDOFF\n\n### Routine wedge detected (S-0001)\n\nbody\n")
    assert handoff_section_exists(handoff, "S-0001") is True
    assert handoff_section_exists(handoff, "S-9999") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
