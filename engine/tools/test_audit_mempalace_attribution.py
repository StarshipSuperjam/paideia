"""Tests for audit_mempalace_attribution.py — ADR 0056 Part B / S-0079.

Covers the helper-function correctness (added_by parsing, topic parsing,
window matching, categorization) and an end-to-end pass against an in-memory
chromadb-shaped fixture plus stub archive directory.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_mempalace_attribution import (  # noqa: E402
    SessionAudit,
    categorize,
    collect_audits,
    in_window,
    parse_iso_window,
    session_id_from_added_by,
    session_id_from_topic,
    session_str,
)


def test_session_id_from_added_by_canonical() -> None:
    assert session_id_from_added_by("S-0050") == 50
    assert session_id_from_added_by("S-0078") == 78
    assert session_id_from_added_by("S-0001") == 1


def test_session_id_from_added_by_variants() -> None:
    assert session_id_from_added_by("claude-S-0026") == 26
    assert session_id_from_added_by("claude-s0001") == 1
    assert session_id_from_added_by("claude-s0042") == 42
    assert session_id_from_added_by("claude-opus-4-7-S-0009") == 9
    assert session_id_from_added_by("claude-opus-4.7-S-0017") == 17
    assert session_id_from_added_by("mcp:S-0005") == 5
    assert session_id_from_added_by("S-0003-continuation") == 3


def test_session_id_from_added_by_rejects_bare() -> None:
    assert session_id_from_added_by("mempalace") is None
    assert session_id_from_added_by("claude") is None
    assert session_id_from_added_by("mcp") is None
    assert session_id_from_added_by("") is None
    assert session_id_from_added_by(None) is None
    assert session_id_from_added_by("session-hook") is None


def test_session_id_from_topic() -> None:
    assert session_id_from_topic("S-0042 close") == 42
    assert session_id_from_topic("paideia-S-0038") == 38
    assert session_id_from_topic("paideia-S-0040") == 40
    assert session_id_from_topic("s0035-engine-hardening") == 35
    assert session_id_from_topic("paideia-s0078-mempalace-mechanization") == 78
    assert session_id_from_topic("phase-5-routine") is None
    assert session_id_from_topic("general") is None
    assert session_id_from_topic(None) is None


def test_session_str() -> None:
    assert session_str(1) == "S-0001"
    assert session_str(78) == "S-0078"
    assert session_str(9999) == "S-9999"


def test_parse_iso_window_explicit_close() -> None:
    from datetime import timezone as _tz

    s, e = parse_iso_window("2026-05-06T04:46:14Z", "2026-05-06T05:30:00Z")
    assert s is not None
    assert s.hour == 4 and s.minute == 46 and s.tzinfo == _tz.utc
    assert e is not None
    assert e.hour == 5 and e.minute == 30 and e.tzinfo == _tz.utc


def test_parse_iso_window_open_session_widens_to_eod() -> None:
    s, e = parse_iso_window("2026-05-06T04:46:14Z", None)
    assert s is not None
    assert e is not None
    assert e.hour == 23 and e.minute == 59


def test_in_window_with_local_naive_filed_at() -> None:
    # filed_at is local-naive; the helper attaches the process-local tz.
    # We pick a window that should obviously contain "now" regardless of TZ.
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td

    now = _dt.now()
    naive_iso = now.isoformat(timespec="microseconds")
    now_utc = now.astimezone(_tz.utc)
    start = now_utc - _td(minutes=1)
    end = now_utc + _td(minutes=1)
    assert in_window(naive_iso, start, end) is True
    assert in_window(naive_iso, start - _td(hours=2), start - _td(hours=1)) is False
    assert in_window(None, start, end) is False
    assert in_window(naive_iso, None, end) is False


def test_categorize_complete() -> None:
    a = SessionAudit(
        session_id=78,
        mode="interactive",
        started_at=None,
        closed_at=None,
        diary_present=True,
        decision_drawer_count=1,
        adrs_added=["0056-x.md"],
    )
    assert categorize(a) == "complete"


def test_categorize_diary_only_missing() -> None:
    a = SessionAudit(
        session_id=50,
        mode="routine",
        started_at=None,
        closed_at=None,
        diary_present=False,
        decision_drawer_count=0,
        adrs_added=[],
    )
    assert categorize(a) == "no_signal"


def test_categorize_decisions_missing() -> None:
    a = SessionAudit(
        session_id=42,
        mode="interactive",
        started_at=None,
        closed_at=None,
        diary_present=True,
        decision_drawer_count=0,
        adrs_added=["0050-x.md"],
    )
    assert categorize(a) == "decisions_missing"


def test_categorize_both_missing() -> None:
    a = SessionAudit(
        session_id=42,
        mode="interactive",
        started_at=None,
        closed_at=None,
        diary_present=False,
        decision_drawer_count=0,
        adrs_added=["0050-x.md"],
    )
    assert categorize(a) == "both_missing"


def test_categorize_diary_only_when_routine_lacks_adrs() -> None:
    a = SessionAudit(
        session_id=50,
        mode="routine",
        started_at=None,
        closed_at=None,
        diary_present=False,
        decision_drawer_count=0,
        adrs_added=[],
    )
    assert categorize(a) == "no_signal"
    a2 = SessionAudit(
        session_id=50,
        mode="routine",
        started_at=None,
        closed_at=None,
        diary_present=False,
        decision_drawer_count=1,
        adrs_added=[],
    )
    assert categorize(a2) == "diary_only_missing"


def _build_palace(path: Path) -> None:
    """Build a palace-shaped sqlite stub matching the production schema."""
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE embedding_metadata (id INTEGER, key TEXT, string_value TEXT, "
        "PRIMARY KEY (id, key))"
    )
    rows: list[tuple[int, str, str]] = []
    rows.extend(
        [
            (1, "agent", "claude"),
            (1, "type", "diary_entry"),
            (1, "topic", "S-0078 close"),
            (1, "filed_at", "2026-05-06T04:20:00.000000"),
            (1, "room", "diary"),
        ]
    )
    rows.extend(
        [
            (2, "added_by", "S-0078"),
            (2, "room", "decisions"),
            (2, "chroma:document", "[decision] ADR 0056 — body"),
            (2, "filed_at", "2026-05-06T04:18:00.000000"),
        ]
    )
    rows.extend(
        [
            (3, "added_by", "S-0078"),
            (3, "room", "lessons"),
            (3, "chroma:document", "[lesson] json.dumps default ensure_ascii"),
            (3, "filed_at", "2026-05-06T04:18:30.000000"),
        ]
    )
    rows.extend(
        [
            (4, "added_by", "S-0050"),
            (4, "room", "general"),
            (4, "chroma:document", "Some routine content"),
            (4, "filed_at", "2026-05-04T12:00:00.000000"),
        ]
    )
    rows.extend(
        [
            (5, "added_by", "S-0042"),
            (5, "room", "decisions"),
            (5, "chroma:document", "[decision] body"),
            (5, "filed_at", "2026-05-03T18:00:00.000000"),
        ]
    )
    rows.extend(
        [
            (6, "agent", "session-hook"),
            (6, "type", "diary_entry"),
            (6, "topic", "checkpoint"),
            (6, "filed_at", "2026-05-04T12:30:00.000000"),
            (6, "room", "diary"),
        ]
    )
    conn.executemany("INSERT INTO embedding_metadata VALUES (?, ?, ?)", rows)
    conn.commit()
    conn.close()


def _write_archive(
    path: Path, sid: int, mode: str | None, started: str, closed: str
) -> None:
    payload: dict[str, object] = {
        "id": session_str(sid),
        "started_at": started,
        "closed_at": closed,
        "status": "closed",
        "commits": [],
    }
    if mode is not None:
        payload["mode"] = mode
    path.write_text(json.dumps(payload))


def test_collect_audits_end_to_end(tmp_path: Path) -> None:
    palace = tmp_path / "chroma.sqlite3"
    _build_palace(palace)
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    _write_archive(
        archive_dir / "S-0042.json",
        42,
        "interactive",
        "2026-05-03T17:00:00Z",
        "2026-05-03T18:30:00Z",
    )
    _write_archive(
        archive_dir / "S-0050.json",
        50,
        "routine",
        "2026-05-04T11:00:00Z",
        "2026-05-04T13:00:00Z",
    )
    _write_archive(
        archive_dir / "S-0078.json",
        78,
        "interactive",
        "2026-05-06T03:37:00Z",
        "2026-05-06T04:25:00Z",
    )
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    audits = collect_audits(archive_dir, palace, repo_root, max_session_id=99)
    by_session = {a.session_id: a for a in audits}
    assert set(by_session.keys()) == {42, 50, 78}
    a78 = by_session[78]
    assert a78.diary_present is True
    assert a78.diary_match_method == "topic"
    assert a78.decision_drawer_count == 1
    assert a78.lesson_drawer_count == 1
    assert a78.auto_captures_present is True
    a42 = by_session[42]
    assert a42.diary_present is False
    assert a42.decision_drawer_count == 1
    a50 = by_session[50]
    assert a50.diary_present is False
    assert a50.decision_drawer_count == 0


def test_collect_audits_respects_max_session(tmp_path: Path) -> None:
    palace = tmp_path / "chroma.sqlite3"
    _build_palace(palace)
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    _write_archive(
        archive_dir / "S-0042.json",
        42,
        "interactive",
        "2026-05-03T17:00:00Z",
        "2026-05-03T18:30:00Z",
    )
    _write_archive(
        archive_dir / "S-0078.json",
        78,
        "interactive",
        "2026-05-06T03:37:00Z",
        "2026-05-06T04:25:00Z",
    )
    audits = collect_audits(archive_dir, palace, tmp_path, max_session_id=50)
    assert {a.session_id for a in audits} == {42}
