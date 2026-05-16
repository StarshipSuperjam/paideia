"""MCP tool registry for the engine-memory substrate.

Per ADR 0091 Decision commitment 5, the substrate exposes **exactly six
MCP tools** as the pre-committed surface ceiling. Adding a seventh
requires a new ADR superseding or amending ADR 0091.

S-0190 wires 2 of the 6:

* ``engine_memory_add_drawer`` — author a curated drawer
  (decisions / pushback / lessons / exploration / operations / general).
  Hook-driven transcript capture uses ``room='work'`` and goes through
  ``transcript_capture.capture`` directly (no MCP round-trip); this
  tool is the human/Claude-authored curated-content path.
* ``engine_memory_diary_write`` — write a session-close diary entry.
  Mechanically enforced via the
  ``engine_memory_diary_write_skipped`` soft-warn at S-0193.

The remaining 4 (``engine_memory_search``, ``engine_memory_get_drawer``,
``engine_memory_list_drawers``, ``engine_memory_diary_read``) land at
S-0191. Adding rows to ``REGISTRY`` is the only change S-0191 needs to
make in this file.

Handlers raise on validation failures; ``mcp_server.handle_request``
catches and returns the JSON-RPC ``-32000`` error code. The Python-side
validation (room / source_kind allowlists) produces clear error messages
ahead of the SQL CHECK constraints firing.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from engine.memory.connection import get_conn
from engine.memory.diary import write_entry as _diary_write_entry

ALLOWED_ROOMS = {
    "decisions",
    "pushback",
    "lessons",
    "exploration",
    "operations",
    "work",
    "general",
}
ALLOWED_SOURCE_KINDS = {
    "manual",
    "hook_stop",
    "hook_precompact",
    "export_replay",
    "migration_seed",
}


def _tool_add_drawer(
    content: str,
    room: str,
    *,
    tags: list[str] | None = None,
    session_id: str | None = None,
    source_kind: str = "manual",
    commit_sha: str | None = None,
    source_path: str | None = None,
    source_adr_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Insert a curated drawer + optional lineage row.

    A lineage row is written iff at least one of ``commit_sha``,
    ``source_path``, ``source_adr_id`` is provided. Returns
    ``{id, filed_at}``.
    """
    if not content or not str(content).strip():
        raise ValueError("drawer content must be non-empty")
    if room not in ALLOWED_ROOMS:
        raise ValueError(f"invalid room {room!r}; allowed: {sorted(ALLOWED_ROOMS)}")
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(
            f"invalid source_kind {source_kind!r}; allowed: {sorted(ALLOWED_SOURCE_KINDS)}"
        )

    drawer_id = uuid.uuid4().hex
    tags_json = json.dumps(tags if tags else [])
    metadata_json = json.dumps(metadata if metadata else {})

    conn = get_conn(db_path)
    try:
        conn.execute(
            "INSERT INTO drawers "
            "(id, room, tags, source_kind, session_id, content, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                drawer_id,
                room,
                tags_json,
                source_kind,
                session_id,
                content,
                metadata_json,
            ),
        )
        # Optional lineage row when authoring against a known source.
        if any((commit_sha, source_path, source_adr_id)):
            conn.execute(
                "INSERT INTO lineage "
                "(drawer_id, source, session_id, commit_sha, source_path, source_adr_id) "
                "VALUES (?, 'manual_author', ?, ?, ?, ?)",
                (
                    drawer_id,
                    session_id,
                    commit_sha,
                    source_path,
                    source_adr_id,
                ),
            )
        row = conn.execute(
            "SELECT filed_at FROM drawers WHERE id = ?", (drawer_id,)
        ).fetchone()
    finally:
        conn.close()

    return {"id": drawer_id, "filed_at": row[0]}


def _tool_diary_write(
    entry: str,
    *,
    topic: str | None = None,
    session_id: str | None = None,
    agent_name: str = "claude",
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Write a diary entry. Delegates to :func:`engine.memory.diary.write_entry`."""
    return _diary_write_entry(
        entry,
        agent_name=agent_name,
        session_id=session_id,
        topic=topic,
        db_path=db_path,
    )


REGISTRY: dict[str, dict[str, Any]] = {
    "engine_memory_add_drawer": {
        "description": (
            "Author a curated drawer (decisions, pushback, lessons, "
            "exploration, operations, general). Per ADR 0091, transcript "
            "auto-capture is hook-driven and uses room='work' — this tool "
            "is for deliberate Claude/human-authored content."
        ),
        "input_schema": {
            "type": "object",
            "required": ["content", "room"],
            "properties": {
                "content": {"type": "string", "description": "Drawer body content."},
                "room": {
                    "type": "string",
                    "enum": sorted(ALLOWED_ROOMS),
                    "description": "Routing key. Curated rooms = decisions/pushback/lessons/exploration/operations/general; 'work' reserved for hook-driven auto-capture.",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Free-form tags for retrieval routing (e.g. 'decision','pushback','lesson').",
                },
                "session_id": {"type": "string"},
                "source_kind": {
                    "type": "string",
                    "enum": sorted(ALLOWED_SOURCE_KINDS),
                    "default": "manual",
                },
                "commit_sha": {"type": "string"},
                "source_path": {"type": "string"},
                "source_adr_id": {"type": "string"},
                "metadata": {"type": "object"},
            },
        },
        "handler": _tool_add_drawer,
    },
    "engine_memory_diary_write": {
        "description": (
            "Write a session-close diary entry (the AI's first-person "
            "reflection on the session). Distinct from outcome_summary "
            "and ENGINE_LOG per the project's two-layer decision-recording "
            "convention. Mechanically enforced via the "
            "engine_memory_diary_write_skipped soft-warn (wired at S-0193)."
        ),
        "input_schema": {
            "type": "object",
            "required": ["entry"],
            "properties": {
                "entry": {
                    "type": "string",
                    "description": "150-400 word first-person reflection.",
                },
                "topic": {
                    "type": "string",
                    "description": "Optional one-line topic tag.",
                },
                "session_id": {
                    "type": "string",
                    "description": "The closing session's S-NNNN ID.",
                },
                "agent_name": {
                    "type": "string",
                    "default": "claude",
                    "description": "Per project convention, defaults to 'claude'.",
                },
            },
        },
        "handler": _tool_diary_write,
    },
}
