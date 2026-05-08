"""Tests for validate.validate_outcome_summary_unhandled_defer — ADR 0049 Decision 6 / Issue #54."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402


def _write_current(
    tmp_path: Path,
    outcome_summary: str | None = None,
    next_session_handle: object = "__OMIT__",
    session_id: str = "S-0100",
) -> Path:
    """Write a current.json fixture under tmp_path/engine/session/.

    `next_session_handle="__OMIT__"` (default) means the key is absent from
    the JSON entirely — the "you forgot to declare" case. Pass `None`
    explicitly for the load-bearing "explicit no defer" semantic, or pass
    a string for verification-path tests.
    """
    payload: dict[str, object] = {"id": session_id, "mode": "interactive"}
    if outcome_summary is not None:
        payload["outcome_summary"] = outcome_summary
    if next_session_handle != "__OMIT__":
        payload["next_session_handle"] = next_session_handle
    session_dir = tmp_path / "engine" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    p = session_dir / "current.json"
    p.write_text(json.dumps(payload))
    return p


def _write_register(tmp_path: Path, next_id: str = "0101") -> Path:
    p = tmp_path / "engine" / "session" / "register_state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"next_id": next_id, "last_claimed": "S-0100"}))
    return p


def _patch_repo_root_to(tmp_path: Path) -> "mock._patch[Path]":
    return mock.patch.object(validate, "REPO_ROOT", tmp_path)


# ----- absent-current.json safety --------------------------------------------


def test_no_current_returns_clean(tmp_path: Path) -> None:
    """Default-mode (no current.json) → no checks fire, no warnings."""
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "validate_outcome_summary_unhandled_defer" in result.checks_run
    assert len(result.hard_fails) == 0
    assert len(result.soft_warns) == 0


def test_malformed_json_returns_clean(tmp_path: Path) -> None:
    """Bad JSON in current.json → graceful no-op (other audits catch shape)."""
    p = tmp_path / "engine" / "session" / "current.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{ not valid json")
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


# ----- mid-session safety (outcome_summary null) -----------------------------


def test_outcome_summary_null_returns_clean(tmp_path: Path) -> None:
    """Mid-session pre-commit invocations (outcome_summary still null) → no-op."""
    _write_current(tmp_path, outcome_summary=None, next_session_handle=None)
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_outcome_summary_empty_string_returns_clean(tmp_path: Path) -> None:
    """Empty / whitespace-only outcome_summary → no hedge match possible."""
    _write_current(tmp_path, outcome_summary="   ", next_session_handle=None)
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


# ----- no hedge match --------------------------------------------------------


def test_no_hedge_no_warn(tmp_path: Path) -> None:
    """Plain delivery prose with no hedge phrasing → no warn."""
    _write_current(
        tmp_path,
        outcome_summary="Phase 3 SQL landed cleanly. All 47 tests pass.",
        next_session_handle=None,
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


# ----- hedge + missing handle (the primary positive case) --------------------


def test_hedge_with_handle_absent_warns(tmp_path: Path) -> None:
    """Hedge prose + `next_session_handle` key absent → primary soft-warn fires."""
    _write_current(
        tmp_path,
        outcome_summary=(
            "Schema work landed. The font-tuning fix is correctable in any "
            "future session via a JSON edit."
        ),
        next_session_handle="__OMIT__",
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "outcome_summary_unhandled_defer" in result.soft_warns
    assert len(result.soft_warns["outcome_summary_unhandled_defer"]) == 1
    msg = result.soft_warns["outcome_summary_unhandled_defer"][0]
    assert "future" in msg.lower()
    assert "ADR 0049" in msg or "Decision 6" in msg


def test_hedge_with_handle_explicit_null_no_warn(tmp_path: Path) -> None:
    """Hedge prose + explicit null → no warn ("intentional forward-pointer")."""
    _write_current(
        tmp_path,
        outcome_summary=(
            "Routine fired and exited cleanly; the next session will resume from "
            "the same target."
        ),
        next_session_handle=None,
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


# ----- hedge + Issue handle verification -------------------------------------


def test_hedge_with_issue_handle_verified_exists_no_warn(tmp_path: Path) -> None:
    """Hedge + `#NN` + gh reports exit-0 → no warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; the next session will pick this up.",
        next_session_handle="#54",
    )
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")
    with (
        _patch_repo_root_to(tmp_path),
        mock.patch("validate.subprocess.run", return_value=fake),
    ):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_hedge_with_issue_handle_not_found_warns(tmp_path: Path) -> None:
    """Hedge + `#NN` + gh reports 'Could not resolve' → unknown-issue warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely until the next session can pick this up.",
        next_session_handle="#9999",
    )
    fake = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="GraphQL error: Could not resolve to an Issue",
    )
    with (
        _patch_repo_root_to(tmp_path),
        mock.patch("validate.subprocess.run", return_value=fake),
    ):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "next_session_handle_unknown_issue" in result.soft_warns


def test_hedge_with_issue_handle_gh_unavailable_no_warn(tmp_path: Path) -> None:
    """Hedge + `#NN` + gh not installed → suppress (offline-graceful)."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; the next session will pick this up.",
        next_session_handle="#54",
    )
    with (
        _patch_repo_root_to(tmp_path),
        mock.patch(
            "validate.subprocess.run",
            side_effect=FileNotFoundError("gh not installed"),
        ),
    ):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_hedge_with_issue_handle_gh_timeout_no_warn(tmp_path: Path) -> None:
    """Hedge + `#NN` + gh times out → suppress (offline-graceful)."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; the next session will pick this up.",
        next_session_handle="#54",
    )
    with (
        _patch_repo_root_to(tmp_path),
        mock.patch(
            "validate.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=5.0),
        ),
    ):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_hedge_with_issue_handle_auth_error_no_warn(tmp_path: Path) -> None:
    """Hedge + `#NN` + gh auth failure → suppress (no false positive)."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; next session will resolve.",
        next_session_handle="#54",
    )
    fake = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="error: not authenticated. Run `gh auth login`.",
    )
    with (
        _patch_repo_root_to(tmp_path),
        mock.patch("validate.subprocess.run", return_value=fake),
    ):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


# ----- hedge + Session handle verification -----------------------------------


def test_hedge_with_session_handle_archive_exists_no_warn(tmp_path: Path) -> None:
    """Hedge + `S-NNNN` + archive file exists → no warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; revisit when the next session boots.",
        next_session_handle="S-0099",
    )
    archive = tmp_path / "engine" / "session" / "archive" / "S-0099.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text(json.dumps({"id": "S-0099"}))
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_hedge_with_session_handle_matches_next_id_no_warn(tmp_path: Path) -> None:
    """Hedge + `S-NNNN` matching register_state.json next_id → no warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; the next session will pick up the rest.",
        next_session_handle="S-0101",
    )
    _write_register(tmp_path, next_id="0101")
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert len(result.soft_warns) == 0


def test_hedge_with_session_handle_unknown_warns(tmp_path: Path) -> None:
    """Hedge + `S-NNNN` matching neither archive nor next_id → unknown-session warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; revisit when next session fires.",
        next_session_handle="S-9999",
    )
    _write_register(tmp_path, next_id="0101")
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "next_session_handle_unknown_session" in result.soft_warns


# ----- hedge + malformed handle ---------------------------------------------


def test_hedge_with_malformed_string_handle_warns(tmp_path: Path) -> None:
    """Hedge + handle string not matching #NN or S-NNNN → malformed warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; future session will resolve.",
        next_session_handle="see-the-other-doc",
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "next_session_handle_malformed" in result.soft_warns


def test_hedge_with_non_string_handle_warns(tmp_path: Path) -> None:
    """Hedge + handle that's an int (or other non-str non-null) → malformed warn."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; the next session will resolve.",
        next_session_handle=42,
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "next_session_handle_malformed" in result.soft_warns


def test_hedge_with_session_handle_wrong_digit_count_warns(
    tmp_path: Path,
) -> None:
    """`S-99` (not 4-digit) doesn't match the canonical pattern → malformed."""
    _write_current(
        tmp_path,
        outcome_summary="Defer indefinitely; future session will resolve.",
        next_session_handle="S-99",
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "next_session_handle_malformed" in result.soft_warns


# ----- hedge regex coverage --------------------------------------------------


@pytest.mark.parametrize(
    "phrase",
    [
        "future session",
        "next session will",
        "correctable in any",
        "preserved for manual review",
        "picked up by",
        "defer indefinitely",
        "revisit when",
    ],
)
def test_each_hedge_pattern_fires(tmp_path: Path, phrase: str) -> None:
    """Each canonical hedge phrase fires the warn when handle is absent."""
    _write_current(
        tmp_path,
        outcome_summary=f"Work landed; the {phrase} the rest will need separate work.",
        next_session_handle="__OMIT__",
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "outcome_summary_unhandled_defer" in result.soft_warns


def test_hedge_pattern_case_insensitive(tmp_path: Path) -> None:
    """Patterns match regardless of case."""
    _write_current(
        tmp_path,
        outcome_summary="Work landed; FUTURE SESSION will resolve the open thread.",
        next_session_handle="__OMIT__",
    )
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_outcome_summary_unhandled_defer()
    assert "outcome_summary_unhandled_defer" in result.soft_warns
