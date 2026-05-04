"""Tests for engine/tools/check_session_conflict.py.

Cover the disposition logic by writing register_state.json + current.json
fixtures into ``tmp_path`` and calling ``check()`` with a fixed ``now``
to make time deltas deterministic.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_session_conflict import (  # noqa: E402
    check,
    main,
    parse_started_at,
)


# ---------------------------------------------------------------------------
# parse_started_at
# ---------------------------------------------------------------------------


def test_parse_started_at_z_suffix() -> None:
    dt = parse_started_at("2026-05-04T17:30:03Z")
    assert dt is not None
    assert dt.year == 2026
    assert dt.tzinfo is not None


def test_parse_started_at_offset() -> None:
    dt = parse_started_at("2026-05-04T17:30:03+00:00")
    assert dt is not None
    assert dt.tzinfo is not None


def test_parse_started_at_malformed_returns_none() -> None:
    assert parse_started_at("not a timestamp") is None
    assert parse_started_at("") is None


# ---------------------------------------------------------------------------
# check() helpers
# ---------------------------------------------------------------------------


def _write_state(
    tmp_path: Path,
    register: dict[str, Any] | None,
    current: dict[str, Any] | None,
) -> Path:
    """Build engine/session/{register_state,current}.json under ``tmp_path``."""
    session_dir = tmp_path / "engine" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    if register is not None:
        (session_dir / "register_state.json").write_text(json.dumps(register))
    if current is not None:
        (session_dir / "current.json").write_text(json.dumps(current))
    return tmp_path


# ---------------------------------------------------------------------------
# check() dispositions
# ---------------------------------------------------------------------------


def test_check_no_register_returns_zero(tmp_path: Path) -> None:
    repo = _write_state(tmp_path, register=None, current=None)
    code, msg = check(repo)
    assert code == 0
    assert "no register_state.json" in msg


def test_check_status_closed_returns_zero(tmp_path: Path) -> None:
    repo = _write_state(
        tmp_path,
        register={"current_status": "closed", "next_id": "0042"},
        current=None,
    )
    code, msg = check(repo)
    assert code == 0
    assert "no conflict" in msg


def test_check_in_progress_no_current_json_returns_zero(tmp_path: Path) -> None:
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current=None,
    )
    code, msg = check(repo)
    assert code == 0
    assert "anomalous state" in msg


def test_check_in_progress_unparseable_started_at_returns_zero(
    tmp_path: Path,
) -> None:
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": "garbage"},
    )
    code, msg = check(repo)
    assert code == 0
    assert "could not be parsed" in msg


def test_check_in_progress_recent_returns_one(tmp_path: Path) -> None:
    """Started 30 minutes ago → recent collision → exit 1."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started = now - timedelta(minutes=30)
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started.isoformat()},
    )
    code, msg = check(repo, now=now)
    assert code == 1
    assert "RECENT" in msg
    assert "S-0041" in msg
    assert "30 minute" in msg


def test_check_in_progress_ambiguous_returns_one(tmp_path: Path) -> None:
    """Started 5 hours ago → mid-window ambiguous → exit 1."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started = now - timedelta(hours=5)
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started.isoformat()},
    )
    code, msg = check(repo, now=now)
    assert code == 1
    assert "AMBIGUOUS" in msg
    assert "5h ago" in msg


def test_check_in_progress_stale_returns_two(tmp_path: Path) -> None:
    """Started 48 hours ago → stale → exit 2."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started = now - timedelta(hours=48)
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started.isoformat()},
    )
    code, msg = check(repo, now=now)
    assert code == 2
    assert "STALE" in msg
    assert "2 day" in msg


def test_check_future_started_at_treated_as_recent(tmp_path: Path) -> None:
    """Clock skew producing a future started_at clamps to recent collision."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started = now + timedelta(hours=1)  # future
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started.isoformat()},
    )
    code, _msg = check(repo, now=now)
    assert code == 1


def test_check_z_suffix_started_at(tmp_path: Path) -> None:
    """The eager-claim writes ``...Z`` form; ensure parsing covers it."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started_str = "2026-05-04T17:30:00Z"
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started_str},
    )
    code, _msg = check(repo, now=now)
    assert code == 1  # 30 min ago → recent


def test_check_custom_windows(tmp_path: Path) -> None:
    """Override windows; an event 90 min ago is "recent" under a 2h window."""
    now = datetime(2026, 5, 4, 18, 0, 0, tzinfo=timezone.utc)
    started = now - timedelta(minutes=90)
    repo = _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started.isoformat()},
    )
    code_default, _ = check(repo, now=now)
    assert code_default == 1  # ambiguous under default 1h recent / 24h stale
    code_extended, msg_extended = check(
        repo, now=now, recent_window=7200, stale_window=86400
    )
    assert code_extended == 1
    assert "RECENT" in msg_extended


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def test_main_no_conflict_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_state(
        tmp_path,
        register={"current_status": "closed", "next_id": "0042"},
        current=None,
    )
    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "no conflict" in captured.out


def test_main_recent_collision_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    started = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
    _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started},
    )
    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 1
    captured = capsys.readouterr()
    assert "RECENT" in captured.err


def test_main_quiet_suppresses_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    started = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
    _write_state(
        tmp_path,
        register={"current_status": "in_progress", "next_id": "0042"},
        current={"id": "S-0041", "started_at": started},
    )
    rc = main(["--repo-root", str(tmp_path), "--quiet"])
    assert rc == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
