"""Tests for validate.validate_engine_memory_adoption — ADR 0091 cutover (S-0191)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # type: ignore[import-not-found]  # noqa: E402


def _write_current(
    tmp_path: Path,
    activity: dict[str, Any] | None,
    *,
    mode: str = "interactive",
    outcome_summary: str | None = None,
) -> Path:
    """Write a fake current.json under tmp_path/engine/session/."""
    session_dir = tmp_path / "engine" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    current: dict[str, Any] = {
        "id": "S-0192",
        "started_at": "2026-05-17T00:00:00Z",
        "status": "in_progress",
        "mode": mode,
        "working_on": "engine memory cutover",
    }
    if activity is not None:
        current["engine_memory_activity"] = activity
    if outcome_summary is not None:
        current["outcome_summary"] = outcome_summary
    path = session_dir / "current.json"
    path.write_text(json.dumps(current))
    return path


def test_returns_clean_when_current_json_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert r.hard_fails == []
    assert r.soft_warns == {}
    assert "validate_engine_memory_adoption" in r.checks_run


def test_returns_clean_when_engine_memory_activity_field_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Through S-0191, the field is absent — graceful skip per ADR 0091 plan."""
    _write_current(tmp_path, activity=None)
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert r.hard_fails == []
    assert r.soft_warns == {}


def test_returns_clean_when_search_calls_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No search → no soft-warn (the boot-step-skipped check is separate)."""
    _write_current(
        tmp_path,
        activity={
            "search_calls": 0,
            "engine_memory_citations": {"total": 0},
        },
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_zero_citations_after_search" not in r.soft_warns


def test_returns_clean_when_search_calls_and_citations_both_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 3,
            "engine_memory_citations": {"total": 2},
        },
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_zero_citations_after_search" not in r.soft_warns


def test_fires_soft_warn_on_search_with_zero_citations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 5,
            "engine_memory_citations": {"total": 0},
        },
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_zero_citations_after_search" in r.soft_warns
    bodies = r.soft_warns["engine_memory_zero_citations_after_search"]
    assert len(bodies) == 1
    assert "search_calls=5" in bodies[0]
    assert "boot_surface.py" in bodies[0]


def test_fires_when_citations_field_missing_entirely(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing citations dict treated as zero — defensive default."""
    _write_current(
        tmp_path,
        activity={"search_calls": 2},
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_zero_citations_after_search" in r.soft_warns


def test_returns_clean_on_malformed_current_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_dir = tmp_path / "engine" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "current.json").write_text("not valid json {{{")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    # Malformed JSON is caught by validate_repo_structure; this adoption
    # check returns clean and lets the structural validator hard-fail.
    assert r.hard_fails == []


# --------------------------------------------------------------------
# S-0192: new categories activated (3 soft-warns + 1 hard-fail with
# escape-hatch token)
# --------------------------------------------------------------------


def test_fires_boot_query_skipped_when_search_calls_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 0,
            "diary_read_calls": 1,
            "diary_write_calls": 1,
        },
        outcome_summary="ok",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_boot_query_skipped" in r.soft_warns


def test_fires_diary_read_skipped_when_diary_read_calls_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 1,
            "diary_read_calls": 0,
            "diary_write_calls": 1,
        },
        outcome_summary="ok",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert "engine_memory_diary_read_skipped" in r.soft_warns


def test_hard_fails_when_engine_interactive_session_skips_diary_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 1,
            "diary_read_calls": 1,
            "diary_write_calls": 0,
        },
        outcome_summary="all done; nothing notable",
        mode="interactive",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert any("engine_memory_diary_write_skipped" in msg for msg in r.hard_fails)


def test_escape_hatch_token_downgrades_diary_write_hard_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 1,
            "diary_read_calls": 1,
            "diary_write_calls": 0,
        },
        outcome_summary=("engine_memory_unavailable_acknowledged: early-exit session"),
        mode="interactive",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert r.hard_fails == []
    assert "engine_memory_diary_write_acknowledged_skip" in r.soft_warns


def test_routine_mode_emits_soft_warn_not_hard_fail_on_diary_write_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 1,
            "diary_read_calls": 1,
            "diary_write_calls": 0,
        },
        outcome_summary="routine session — substrate dropped mid-run",
        mode="routine",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert r.hard_fails == []
    assert "engine_memory_diary_write_skipped_routine" in r.soft_warns


def test_clean_session_with_all_three_calls_fires_no_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_current(
        tmp_path,
        activity={
            "search_calls": 3,
            "diary_read_calls": 1,
            "diary_write_calls": 1,
            "engine_memory_citations": {"total": 2},
        },
        outcome_summary="ok",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_engine_memory_adoption()
    assert r.hard_fails == []
    assert r.soft_warns == {}
