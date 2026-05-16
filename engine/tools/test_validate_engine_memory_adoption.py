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
) -> Path:
    """Write a fake current.json under tmp_path/engine/session/."""
    session_dir = tmp_path / "engine" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    current: dict[str, Any] = {
        "id": "S-0191",
        "started_at": "2026-05-16T20:00:00Z",
        "status": "in_progress",
        "mode": "interactive",
        "working_on": "engine memory cutover",
    }
    if activity is not None:
        current["engine_memory_activity"] = activity
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
