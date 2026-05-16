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
    _tool_diary_read,
    _tool_diary_write,
    _tool_get_drawer,
    _tool_list_drawers,
    _tool_search,
)


# --- REGISTRY shape --------------------------------------------------------


def test_registry_contains_all_six_tools_at_s0191() -> None:
    assert set(REGISTRY) == {
        "engine_memory_add_drawer",
        "engine_memory_diary_write",
        "engine_memory_search",
        "engine_memory_get_drawer",
        "engine_memory_list_drawers",
        "engine_memory_diary_read",
    }


def test_registry_size_matches_adr_0091_ceiling() -> None:
    # ADR 0091 Decision commitment 5 pre-commits to a six-tool surface.
    # Any addition past six requires a new superseding ADR.
    assert len(REGISTRY) == 6


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


# --- _tool_search ----------------------------------------------------------


def test_search_returns_candidates_dict(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_add_drawer(
        "engine memory substrate is SQLite + FTS5",
        "decisions",
        tags=["decision"],
        db_path=db,
    )
    result = _tool_search("engine memory", db_path=db)
    assert "candidates" in result
    assert isinstance(result["candidates"], list)
    assert len(result["candidates"]) >= 1
    assert result["candidates"][0]["room"] == "decisions"


def test_search_logs_query(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_search("anything", db_path=db)
    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT formulation, query_text, result_count FROM query_log "
            "ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == "mcp_call"
    assert row[1] == "anything"
    assert row[2] == 0


def test_search_rejects_empty_query(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="non-empty"):
        _tool_search("", db_path=db)
    with pytest.raises(ValueError, match="non-empty"):
        _tool_search("   ", db_path=db)


def test_search_rejects_invalid_room(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="invalid room"):
        _tool_search("x", room="bogus", db_path=db)


def test_search_rejects_invalid_limit(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="limit must be >= 1"):
        _tool_search("x", limit=0, db_path=db)


# --- _tool_get_drawer ------------------------------------------------------


def test_get_drawer_returns_drawer_and_lineage(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    add_result = _tool_add_drawer(
        "decision with lineage",
        "decisions",
        tags=["decision"],
        session_id="S-test",
        commit_sha="abc123",
        source_adr_id="0091",
        db_path=db,
    )
    drawer_id = add_result["id"]

    out = _tool_get_drawer(drawer_id, db_path=db)
    assert out["drawer"]["id"] == drawer_id
    assert out["drawer"]["room"] == "decisions"
    assert out["drawer"]["tags"] == ["decision"]
    assert len(out["lineage"]) == 1
    assert out["lineage"][0]["source"] == "manual_author"
    assert out["lineage"][0]["commit_sha"] == "abc123"


def test_get_drawer_returns_drawer_with_empty_lineage(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    add_result = _tool_add_drawer("plain", "general", db_path=db)
    out = _tool_get_drawer(add_result["id"], db_path=db)
    assert out["lineage"] == []


def test_get_drawer_raises_on_unknown_id(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(LookupError, match="drawer not found"):
        _tool_get_drawer("unknown-id-xxx", db_path=db)


def test_get_drawer_rejects_empty_id(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="non-empty"):
        _tool_get_drawer("", db_path=db)


# --- _tool_list_drawers ----------------------------------------------------


def test_list_drawers_returns_recent_first(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    a = _tool_add_drawer("a", "general", db_path=db)
    b = _tool_add_drawer("b", "general", db_path=db)
    c = _tool_add_drawer("c", "general", db_path=db)
    out = _tool_list_drawers(db_path=db)
    ids = [d["id"] for d in out["drawers"]]
    # All three drawers were inserted at the same datetime('now') second;
    # the secondary "id DESC" sort gives deterministic order. We just
    # assert all three appear.
    assert set(ids) == {a["id"], b["id"], c["id"]}


def test_list_drawers_filters_by_room(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_add_drawer("a", "decisions", db_path=db)
    _tool_add_drawer("b", "pushback", db_path=db)
    out = _tool_list_drawers(room="decisions", db_path=db)
    assert all(d["room"] == "decisions" for d in out["drawers"])
    assert len(out["drawers"]) == 1


def test_list_drawers_filters_by_tag_any(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_add_drawer("a", "general", tags=["foo"], db_path=db)
    _tool_add_drawer("b", "general", tags=["bar"], db_path=db)
    out = _tool_list_drawers(tag_any="foo", db_path=db)
    assert len(out["drawers"]) == 1
    assert out["drawers"][0]["tags"] == ["foo"]


def test_list_drawers_excludes_superseded(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    add = _tool_add_drawer("old", "decisions", db_path=db)
    # Mark superseded via direct SQL (no public API yet).
    conn = get_conn(db)
    try:
        conn.execute(
            "UPDATE drawers SET superseded_by = ?, superseded_at = '2026-01-01' "
            "WHERE id = ?",
            (add["id"], add["id"]),
        )
    finally:
        conn.close()
    out = _tool_list_drawers(db_path=db)
    assert out["drawers"] == []


def test_list_drawers_rejects_invalid_room(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="invalid room"):
        _tool_list_drawers(room="bogus", db_path=db)


def test_list_drawers_rejects_out_of_range_limit(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match=r"limit must be in \[1, 1000\]"):
        _tool_list_drawers(limit=0, db_path=db)
    with pytest.raises(ValueError, match=r"limit must be in \[1, 1000\]"):
        _tool_list_drawers(limit=1001, db_path=db)


def test_list_drawers_rejects_negative_offset(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    with pytest.raises(ValueError, match="offset"):
        _tool_list_drawers(offset=-1, db_path=db)


# --- _tool_diary_read ------------------------------------------------------


def test_diary_read_returns_recent_entries(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_diary_write("entry one", session_id="S-a", db_path=db)
    _tool_diary_write("entry two", session_id="S-b", db_path=db)
    out = _tool_diary_read(last_n=5, db_path=db)
    assert len(out["entries"]) == 2
    # Sorted by created_at DESC; both inserted same second, secondary
    # sort is id DESC — we just assert both present.
    contents = {e["content"] for e in out["entries"]}
    assert contents == {"entry one", "entry two"}


def test_diary_read_respects_agent_name(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_diary_write("for claude", agent_name="claude", db_path=db)
    _tool_diary_write("for other", agent_name="other", db_path=db)
    out = _tool_diary_read(agent_name="other", db_path=db)
    assert len(out["entries"]) == 1
    assert out["entries"][0]["agent_name"] == "other"


def test_diary_read_empty_when_no_entries(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    out = _tool_diary_read(db_path=db)
    assert out["entries"] == []


def test_diary_read_zero_limit_returns_empty(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    _tool_diary_write("x", db_path=db)
    out = _tool_diary_read(last_n=0, db_path=db)
    assert out["entries"] == []
