"""Tests for ``engine/memory/tools.py`` — registry shape + handler behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.memory.connection import get_conn
from engine.memory.tools import (
    ALLOWED_ROOMS,
    ALLOWED_SOURCE_KINDS,
    REGISTRY,
    _tool_add_drawer,
    _tool_diary_write,
)


# --- REGISTRY shape --------------------------------------------------------


def test_registry_contains_exactly_two_tools_at_s0190() -> None:
    assert set(REGISTRY) == {"engine_memory_add_drawer", "engine_memory_diary_write"}


def test_registry_entries_have_required_fields() -> None:
    for name, spec in REGISTRY.items():
        assert "description" in spec and spec["description"]
        assert "input_schema" in spec and isinstance(spec["input_schema"], dict)
        assert "handler" in spec and callable(spec["handler"])


def test_registry_input_schemas_declare_required_fields() -> None:
    add = REGISTRY["engine_memory_add_drawer"]["input_schema"]
    assert add.get("required") == ["content", "room"]
    diary = REGISTRY["engine_memory_diary_write"]["input_schema"]
    assert diary.get("required") == ["entry"]


# --- _tool_add_drawer ------------------------------------------------------


def test_add_drawer_inserts_with_uuid_id(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_add_drawer(
        "decision content", "decisions", session_id="S-test", db_path=db
    )
    assert len(result["id"]) == 32
    assert result["filed_at"]

    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT room, source_kind, content, session_id FROM drawers WHERE id = ?",
            (result["id"],),
        ).fetchone()
    finally:
        conn.close()
    assert row == ("decisions", "manual", "decision content", "S-test")


def test_add_drawer_writes_lineage_when_source_provided(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_add_drawer(
        "a decision with provenance",
        "decisions",
        session_id="S-X",
        commit_sha="abc123",
        source_adr_id="0091",
        db_path=db,
    )

    conn = get_conn(db)
    try:
        rows = conn.execute(
            "SELECT source, session_id, commit_sha, source_adr_id "
            "FROM lineage WHERE drawer_id = ?",
            (result["id"],),
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 1
    assert rows[0] == ("manual_author", "S-X", "abc123", "0091")


def test_add_drawer_no_lineage_when_no_source(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_add_drawer("plain decision", "decisions", db_path=db)

    conn = get_conn(db)
    try:
        rows = conn.execute(
            "SELECT count(*) FROM lineage WHERE drawer_id = ?", (result["id"],)
        ).fetchone()
    finally:
        conn.close()
    assert rows == (0,)


def test_add_drawer_rejects_invalid_room(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="invalid room"):
        _tool_add_drawer("content", "bogus_room", db_path=db)


def test_add_drawer_rejects_invalid_source_kind(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="invalid source_kind"):
        _tool_add_drawer("content", "general", source_kind="bogus_kind", db_path=db)


def test_add_drawer_rejects_empty_content(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="non-empty"):
        _tool_add_drawer("", "general", db_path=db)
    with pytest.raises(ValueError, match="non-empty"):
        _tool_add_drawer("   ", "general", db_path=db)


def test_add_drawer_serializes_tags_and_metadata(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_add_drawer(
        "x",
        "decisions",
        tags=["decision", "phase-6"],
        metadata={"foo": "bar"},
        db_path=db,
    )

    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT tags, metadata FROM drawers WHERE id = ?", (result["id"],)
        ).fetchone()
    finally:
        conn.close()
    assert json.loads(row[0]) == ["decision", "phase-6"]
    assert json.loads(row[1]) == {"foo": "bar"}


def test_add_drawer_accepts_all_seven_rooms(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    for room in sorted(ALLOWED_ROOMS):
        _tool_add_drawer(f"content for {room}", room, db_path=db)
    conn = get_conn(db)
    try:
        count = conn.execute("SELECT count(*) FROM drawers").fetchone()
    finally:
        conn.close()
    assert count == (len(ALLOWED_ROOMS),)


# --- _tool_diary_write -----------------------------------------------------


def test_diary_write_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_diary_write(
        "reflection content", topic="boot", session_id="S-test", db_path=db
    )
    assert len(result["id"]) == 32
    assert result["created_at"]

    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT agent_name, session_id, topic, content FROM diary WHERE id = ?",
            (result["id"],),
        ).fetchone()
    finally:
        conn.close()
    assert row == ("claude", "S-test", "boot", "reflection content")


def test_diary_write_respects_agent_name(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    result = _tool_diary_write("x", agent_name="other_agent", db_path=db)
    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT agent_name FROM diary WHERE id = ?", (result["id"],)
        ).fetchone()
    finally:
        conn.close()
    assert row == ("other_agent",)


# --- Registry dispatch via mcp_server ---------------------------------------


def test_registry_handlers_callable_via_kwargs(tmp_path: Path) -> None:
    """Both handlers accept kwargs as the JSON-RPC `arguments` dict provides them."""
    db = tmp_path / "test.sqlite3"
    args = {"content": "via kwargs", "room": "general", "db_path": str(db)}
    result = REGISTRY["engine_memory_add_drawer"]["handler"](**args)
    assert "id" in result

    diary_args = {"entry": "via kwargs", "db_path": str(db)}
    diary_result = REGISTRY["engine_memory_diary_write"]["handler"](**diary_args)
    assert "id" in diary_result


def test_allowlists_have_expected_membership() -> None:
    # Defensive: keep these in sync with the SQL CHECK constraints.
    assert ALLOWED_ROOMS == {
        "decisions",
        "pushback",
        "lessons",
        "exploration",
        "operations",
        "work",
        "general",
    }
    assert ALLOWED_SOURCE_KINDS == {
        "manual",
        "hook_stop",
        "hook_precompact",
        "export_replay",
        "migration_seed",
    }
