"""Tests for ``engine/memory/diary.py`` — write + read round-trip, ordering, filters."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.memory.diary import read_entries, write_entry


def test_write_entry_returns_id_and_timestamp(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    result = write_entry("test entry", db_path=db)
    assert "id" in result
    assert "created_at" in result
    assert isinstance(result["id"], str)
    assert len(result["id"]) == 32  # UUID4 hex
    assert result["created_at"]  # non-empty timestamp


def test_write_entry_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    write_entry("first reflection", session_id="S-test", topic="boot", db_path=db)
    entries = read_entries(db_path=db)
    assert len(entries) == 1
    e = entries[0]
    assert e["content"] == "first reflection"
    assert e["session_id"] == "S-test"
    assert e["topic"] == "boot"
    assert e["agent_name"] == "claude"


def test_write_entry_rejects_empty_content(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    with pytest.raises(ValueError):
        write_entry("", db_path=db)
    with pytest.raises(ValueError):
        write_entry("   \n  ", db_path=db)


def test_read_entries_orders_most_recent_first(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    write_entry("entry one", db_path=db)
    # SQLite datetime('now') has 1-second resolution; sleep to ensure
    # ordering is unambiguous via created_at. The id-DESC tiebreak
    # handles same-second writes for the round-trip ordering test below.
    time.sleep(1.1)
    write_entry("entry two", db_path=db)
    time.sleep(1.1)
    write_entry("entry three", db_path=db)

    entries = read_entries(db_path=db)
    assert [e["content"] for e in entries] == ["entry three", "entry two", "entry one"]


def test_read_entries_respects_last_n(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    for i in range(5):
        write_entry(f"entry {i}", db_path=db)
        time.sleep(1.1)

    entries = read_entries(last_n=2, db_path=db)
    assert len(entries) == 2
    assert entries[0]["content"] == "entry 4"
    assert entries[1]["content"] == "entry 3"


def test_read_entries_filters_by_agent_name(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    write_entry("claude reflection", agent_name="claude", db_path=db)
    write_entry("other reflection", agent_name="other", db_path=db)

    claude_entries = read_entries(agent_name="claude", db_path=db)
    other_entries = read_entries(agent_name="other", db_path=db)

    assert len(claude_entries) == 1
    assert claude_entries[0]["content"] == "claude reflection"
    assert len(other_entries) == 1
    assert other_entries[0]["content"] == "other reflection"


def test_read_entries_empty_substrate_returns_empty_list(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    assert read_entries(db_path=db) == []


def test_read_entries_zero_last_n_returns_empty(tmp_path: Path) -> None:
    db = tmp_path / "diary.sqlite3"
    write_entry("one", db_path=db)
    assert read_entries(last_n=0, db_path=db) == []
    assert read_entries(last_n=-1, db_path=db) == []


def test_diary_persists_across_connections(tmp_path: Path) -> None:
    """A diary entry written via one connection is readable via the next."""
    db = tmp_path / "diary.sqlite3"
    write_entry("persistent entry", db_path=db)
    # read_entries opens a fresh connection; if the write didn't commit,
    # this returns []. Tests autocommit + isolation_level=None contract.
    entries = read_entries(db_path=db)
    assert len(entries) == 1
    assert entries[0]["content"] == "persistent entry"
