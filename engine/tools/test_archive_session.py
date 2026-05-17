"""Tests for archive_session.py (S-0194)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_session import (  # noqa: E402
    _validate_inflight,
    _validate_register,
    main,
)


def make_inflight(session_id: str = "S-0194", **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": session_id,
        "started_at": "2026-05-17T04:41:02Z",
        "status": "in_progress",
        "mode": "interactive",
        "working_on": "test fixture",
        "outcome_summary": "completed test work",
        "approved_plan": "fixture/test-plan.md",
        "branch": "claude/test-branch",
        "worktree": "fixture/test-worktree",
    }
    payload.update(overrides)
    return payload


def make_register(session_id: str = "S-0194", **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "next_id": "0195",
        "last_claimed": session_id,
        "current_status": "in_progress",
        "health_check_cadence": 20,
        "last_audit_session": "S-0184",
    }
    payload.update(overrides)
    return payload


def write_fixtures(
    tmp_path: Path,
    inflight: dict[str, object] | None = None,
    register: dict[str, object] | None = None,
) -> tuple[Path, Path, Path]:
    """Create current.json + register_state.json + archive dir; return their paths."""
    session_dir = tmp_path / "engine" / "session"
    archive_dir = session_dir / "archive"
    archive_dir.mkdir(parents=True)
    current_path = session_dir / "current.json"
    register_path = session_dir / "register_state.json"
    current_path.write_text(json.dumps(inflight or make_inflight(), indent=2) + "\n")
    register_path.write_text(json.dumps(register or make_register(), indent=2) + "\n")
    return current_path, archive_dir, register_path


def run_main(
    current_path: Path,
    archive_dir: Path,
    register_path: Path,
    *,
    partial: bool = False,
) -> int:
    argv = [
        "--current-path",
        str(current_path),
        "--archive-dir",
        str(archive_dir),
        "--register-path",
        str(register_path),
    ]
    if partial:
        argv.append("--partial")
    return main(argv)


# ----- validation helpers -----------------------------------------------------


def test_validate_inflight_canonical_passes() -> None:
    ok, reason = _validate_inflight(make_inflight())
    assert ok, reason


def test_validate_inflight_rejects_malformed_id() -> None:
    ok, reason = _validate_inflight(make_inflight(id="S-19"))
    assert not ok
    assert "S-NNNN" in reason


def test_validate_inflight_rejects_missing_id() -> None:
    payload = make_inflight()
    del payload["id"]
    ok, reason = _validate_inflight(payload)
    assert not ok


def test_validate_inflight_rejects_status_closed() -> None:
    """If current.json is already in closed state, that's a prior-run residue."""
    ok, reason = _validate_inflight(make_inflight(status="closed"))
    assert not ok
    assert "in_progress" in reason


def test_validate_inflight_rejects_missing_started_at() -> None:
    payload = make_inflight()
    del payload["started_at"]
    ok, reason = _validate_inflight(payload)
    assert not ok


def test_validate_register_canonical_passes() -> None:
    ok, reason = _validate_register(make_register(), "S-0194")
    assert ok, reason


def test_validate_register_rejects_session_mismatch() -> None:
    ok, reason = _validate_register(make_register(last_claimed="S-0193"), "S-0194")
    assert not ok
    assert "mismatch" in reason


# ----- happy paths ------------------------------------------------------------


def test_happy_path_closed(tmp_path: Path) -> None:
    """Default close: archive created with both fields; current.json deleted;
    register flipped."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    rc = run_main(cur, archive_dir, reg)
    assert rc == 0
    assert not cur.exists()
    archive_path = archive_dir / "S-0194.json"
    assert archive_path.exists()
    archived = json.loads(archive_path.read_text())
    assert archived["status"] == "closed"
    assert isinstance(archived["closed_at"], str)
    assert archived["closed_at"].endswith("Z")
    # Original fields preserved
    assert archived["id"] == "S-0194"
    assert archived["started_at"] == "2026-05-17T04:41:02Z"
    assert archived["mode"] == "interactive"
    # Register flipped
    register = json.loads(reg.read_text())
    assert register["current_status"] == "closed"


def test_happy_path_closed_partial(tmp_path: Path) -> None:
    """--partial flag sets status=closed_partial (budget-cap-reached close)."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    rc = run_main(cur, archive_dir, reg, partial=True)
    assert rc == 0
    archived = json.loads((archive_dir / "S-0194.json").read_text())
    assert archived["status"] == "closed_partial"


def test_archived_output_passes_the_audit(tmp_path: Path) -> None:
    """End-to-end: the JSON we write satisfies audit_archive_structured_fields
    in --from-stdin mode, which is what the closing pre-commit hook runs."""
    import subprocess

    cur, archive_dir, reg = write_fixtures(
        tmp_path,
        inflight=make_inflight(
            session_id="S-0194",
            outcome_summary_soft_warns={},
            engine_memory_activity={
                "search_calls": 0,
                "diary_read_calls": 0,
                "diary_write_calls": 0,
                "add_drawer_calls": 0,
                "get_drawer_calls": 0,
                "list_drawers_calls": 0,
                "other_calls": 0,
                "total_calls": 0,
                "first_call_ts": None,
                "last_call_ts": None,
            },
            next_session_handle=None,
        ),
    )
    rc = run_main(cur, archive_dir, reg)
    assert rc == 0
    audit_input = (archive_dir / "S-0194.json").read_text()
    audit_tool = Path(__file__).resolve().parent / "audit_archive_structured_fields.py"
    r = subprocess.run(
        ["python3", str(audit_tool), "--from-stdin"],
        input=audit_input,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"audit hard-failed:\n{r.stderr}"


# ----- idempotency ------------------------------------------------------------


def test_idempotent_rerun_is_safe(tmp_path: Path) -> None:
    """Running twice produces the same archive content and exit 0."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    rc = run_main(cur, archive_dir, reg)
    assert rc == 0
    archive_path = archive_dir / "S-0194.json"
    first_content = archive_path.read_text()
    # The first run deleted current.json. Re-create it for the rerun
    # idempotency check (simulates the AI accidentally re-running the
    # archive tool — common shell-up-arrow pattern).
    cur.write_text(json.dumps(make_inflight(), indent=2) + "\n")
    rc = run_main(cur, archive_dir, reg)
    assert rc == 0
    # Archive content unchanged from the first run
    assert archive_path.read_text() == first_content
    # current.json removed by the idempotent path too
    assert not cur.exists()


def test_archive_already_exists_with_wrong_id_refuses(tmp_path: Path) -> None:
    """If S-0194.json exists but contains a different session id, refuse."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    pre_existing = {
        "id": "S-9999",
        "started_at": "x",
        "status": "closed",
        "closed_at": "2020-01-01T00:00:00Z",
    }
    (archive_dir / "S-0194.json").write_text(json.dumps(pre_existing, indent=2))
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


def test_archive_already_exists_status_in_progress_refuses(tmp_path: Path) -> None:
    """Partial prior run that wrote archive but didn't flip status → refuse."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    (archive_dir / "S-0194.json").write_text(
        json.dumps(
            {
                "id": "S-0194",
                "started_at": "x",
                "status": "in_progress",
                "closed_at": None,
            },
            indent=2,
        )
    )
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


# ----- refusal cases ----------------------------------------------------------


def test_missing_current_refuses(tmp_path: Path) -> None:
    cur, archive_dir, reg = write_fixtures(tmp_path)
    cur.unlink()
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


def test_malformed_current_json_refuses(tmp_path: Path) -> None:
    cur, archive_dir, reg = write_fixtures(tmp_path)
    cur.write_text("{ not valid json")
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


def test_register_session_mismatch_refuses(tmp_path: Path) -> None:
    cur, archive_dir, reg = write_fixtures(
        tmp_path, register=make_register(last_claimed="S-0193")
    )
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2
    # current.json must not be deleted on refusal — recoverable
    assert cur.exists()


def test_register_missing_refuses(tmp_path: Path) -> None:
    cur, archive_dir, reg = write_fixtures(tmp_path)
    reg.unlink()
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


def test_inflight_status_already_closed_refuses(tmp_path: Path) -> None:
    """A current.json with status='closed' is a prior-run residue."""
    cur, archive_dir, reg = write_fixtures(
        tmp_path, inflight=make_inflight(status="closed")
    )
    rc = run_main(cur, archive_dir, reg)
    assert rc == 2


# ----- timestamp emission discipline -----------------------------------------


def test_closed_at_uses_canonical_timestamp_helper(tmp_path: Path) -> None:
    """closed_at must route through engine.tools.timestamps.emit() to
    avoid the timestamp_helper_bypass soft-warn per ADR 0058."""
    cur, archive_dir, reg = write_fixtures(tmp_path)
    with mock.patch(
        "archive_session.emit_timestamp", return_value="2026-09-09T09:09:09Z"
    ) as m:
        rc = run_main(cur, archive_dir, reg)
        assert rc == 0
        m.assert_called_once()
    archived = json.loads((archive_dir / "S-0194.json").read_text())
    assert archived["closed_at"] == "2026-09-09T09:09:09Z"


# ----- CLI integration --------------------------------------------------------


def test_cli_help_does_not_crash(capsys: pytest.CaptureFixture[str]) -> None:
    """``--help`` exits cleanly without raising."""
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "step-13" in out.lower()
