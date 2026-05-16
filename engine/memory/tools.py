"""MCP tool registry for the engine-memory substrate.

Per ADR 0091 Decision commitment 5, the substrate exposes **exactly six
MCP tools** as the pre-committed surface ceiling. Adding a seventh
requires a new ADR superseding or amending ADR 0091.

After S-0191 all six tools are wired:

* ``engine_memory_add_drawer`` (S-0190) — author a curated drawer.
* ``engine_memory_diary_write`` (S-0190) — write a session-close diary entry.
* ``engine_memory_search`` (S-0191) — FTS5 + BM25 + recency + tag-class
  retrieval (via :mod:`engine.memory.boot_surface`).
* ``engine_memory_get_drawer`` (S-0191) — drawer + lineage rows by id.
* ``engine_memory_list_drawers`` (S-0191) — paginated drawer list with
  optional room / tag filter, excludes superseded drawers.
* ``engine_memory_diary_read`` (S-0191) — read recent diary entries
  for an agent (delegates to :func:`engine.memory.diary.read_entries`).

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
from engine.memory.diary import read_entries as _diary_read_entries
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


def _tool_search(
    query: str,
    *,
    room: str | None = None,
    tag_any: str | None = None,
    since_days: int | None = None,
    limit: int = 30,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """FTS5 + BM25 + recency + tag-class retrieval.

    Delegates to :func:`engine.memory.boot_surface.fetch_candidates` so
    the boot orchestrator and runtime MCP queries share one SQL path.
    Also INSERTs a ``query_log`` row with ``formulation='mcp_call'`` so
    the citation-counting telemetry (wired at S-0192) can distinguish
    runtime calls from boot-orchestrator calls.
    """
    if not query or not str(query).strip():
        raise ValueError("query must be non-empty")
    if room is not None and room not in ALLOWED_ROOMS:
        raise ValueError(f"invalid room {room!r}; allowed: {sorted(ALLOWED_ROOMS)}")
    if limit < 1:
        raise ValueError("limit must be >= 1")

    # Local import to avoid a top-level cycle (boot_surface itself
    # imports from connection.py; tools.py is imported by mcp_server.py
    # at module-load time).
    from engine.memory.boot_surface import fetch_candidates

    conn = get_conn(db_path)
    try:
        candidates = fetch_candidates(
            conn,
            query,
            room=room,
            tag_any=tag_any,
            since_days=since_days,
            limit=limit,
        )
        conn.execute(
            "INSERT INTO query_log "
            "(session_id, formulation, query_text, result_count) "
            "VALUES (?, 'mcp_call', ?, ?)",
            (None, query, len(candidates)),
        )
    finally:
        conn.close()

    return {"candidates": candidates}


def _tool_get_drawer(
    id: str,  # noqa: A002 — JSON-RPC arg name
    *,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Return one drawer + its lineage rows.

    Raises if the id is unknown — the caller surfaces a JSON-RPC error.
    """
    if not id or not str(id).strip():
        raise ValueError("drawer id must be non-empty")

    conn = get_conn(db_path)
    try:
        drawer_row = conn.execute(
            "SELECT id, room, tags, source_kind, agent, session_id, "
            "created_at, filed_at, content, metadata, "
            "superseded_by, superseded_at "
            "FROM drawers WHERE id = ?",
            (id,),
        ).fetchone()
        if drawer_row is None:
            raise LookupError(f"drawer not found: {id!r}")

        lineage_rows = conn.execute(
            "SELECT source, session_id, commit_sha, source_path, "
            "source_adr_id, imported_from, source_wing, source_filed_at, "
            "imported_at "
            "FROM lineage WHERE drawer_id = ? ORDER BY source",
            (id,),
        ).fetchall()
    finally:
        conn.close()

    try:
        tags = json.loads(drawer_row[2]) if drawer_row[2] else []
    except json.JSONDecodeError:
        tags = []
    try:
        metadata = json.loads(drawer_row[9]) if drawer_row[9] else {}
    except json.JSONDecodeError:
        metadata = {}

    drawer = {
        "id": drawer_row[0],
        "room": drawer_row[1],
        "tags": tags,
        "source_kind": drawer_row[3],
        "agent": drawer_row[4],
        "session_id": drawer_row[5],
        "created_at": drawer_row[6],
        "filed_at": drawer_row[7],
        "content": drawer_row[8],
        "metadata": metadata,
        "superseded_by": drawer_row[10],
        "superseded_at": drawer_row[11],
    }
    lineage = [
        {
            "source": r[0],
            "session_id": r[1],
            "commit_sha": r[2],
            "source_path": r[3],
            "source_adr_id": r[4],
            "imported_from": r[5],
            "source_wing": r[6],
            "source_filed_at": r[7],
            "imported_at": r[8],
        }
        for r in lineage_rows
    ]
    return {"drawer": drawer, "lineage": lineage}


def _tool_list_drawers(
    *,
    room: str | None = None,
    tag_any: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Paginated list of drawers ordered by ``filed_at DESC``.

    Excludes superseded drawers (``superseded_by IS NULL``) by default.
    Optional ``room`` and ``tag_any`` filters narrow the list.
    """
    if room is not None and room not in ALLOWED_ROOMS:
        raise ValueError(f"invalid room {room!r}; allowed: {sorted(ALLOWED_ROOMS)}")
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be in [1, 1000]")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    sql_parts = [
        "SELECT id, room, tags, source_kind, agent, session_id, ",
        "created_at, filed_at, content, metadata ",
        "FROM drawers WHERE superseded_by IS NULL ",
    ]
    params: list[Any] = []
    if room is not None:
        sql_parts.append("AND room = ? ")
        params.append(room)
    if tag_any is not None:
        sql_parts.append("AND EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?) ")
        params.append(tag_any)
    sql_parts.append("ORDER BY filed_at DESC, id DESC LIMIT ? OFFSET ?")
    params.extend([limit, offset])

    conn = get_conn(db_path)
    try:
        rows = conn.execute("".join(sql_parts), params).fetchall()
    finally:
        conn.close()

    drawers: list[dict[str, Any]] = []
    for r in rows:
        try:
            tags = json.loads(r[2]) if r[2] else []
        except json.JSONDecodeError:
            tags = []
        try:
            metadata = json.loads(r[9]) if r[9] else {}
        except json.JSONDecodeError:
            metadata = {}
        drawers.append(
            {
                "id": r[0],
                "room": r[1],
                "tags": tags,
                "source_kind": r[3],
                "agent": r[4],
                "session_id": r[5],
                "created_at": r[6],
                "filed_at": r[7],
                "content": r[8],
                "metadata": metadata,
            }
        )
    return {"drawers": drawers}


def _tool_diary_read(
    *,
    agent_name: str = "claude",
    last_n: int = 3,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Read recent diary entries. Delegates to diary.read_entries."""
    entries = _diary_read_entries(agent_name=agent_name, last_n=last_n, db_path=db_path)
    return {"entries": entries}


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
    "engine_memory_search": {
        "description": (
            "FTS5 + BM25 + recency + tag-class-boost retrieval. "
            "Returns up to `limit` candidate drawers ordered by composite "
            "rank score (higher is better). Optional filters: `room` "
            "narrows to one of decisions/pushback/lessons/exploration/"
            "operations/work/general; `tag_any` boosts drawers whose "
            "tags array contains the given value; `since_days` excludes "
            "drawers older than N days."
        ),
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text search query (any whitespace-separated tokens).",
                },
                "room": {
                    "type": "string",
                    "enum": sorted(ALLOWED_ROOMS),
                    "description": "Filter to a single room.",
                },
                "tag_any": {
                    "type": "string",
                    "description": "Boost drawers whose tags array contains this value.",
                },
                "since_days": {
                    "type": "integer",
                    "description": "Exclude drawers older than N days.",
                },
                "limit": {
                    "type": "integer",
                    "default": 30,
                    "description": "Max candidates returned (1-1000).",
                },
            },
        },
        "handler": _tool_search,
    },
    "engine_memory_get_drawer": {
        "description": (
            "Fetch one drawer by id, joined with its lineage rows. "
            "Raises if id is unknown."
        ),
        "input_schema": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string", "description": "Drawer UUID."},
            },
        },
        "handler": _tool_get_drawer,
    },
    "engine_memory_list_drawers": {
        "description": (
            "Paginated drawer list ordered by filed_at DESC. Excludes "
            "superseded drawers. Optional room/tag_any filters narrow."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "room": {
                    "type": "string",
                    "enum": sorted(ALLOWED_ROOMS),
                    "description": "Filter to a single room.",
                },
                "tag_any": {
                    "type": "string",
                    "description": "Filter to drawers whose tags array contains this value.",
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Max drawers returned (1-1000).",
                },
                "offset": {
                    "type": "integer",
                    "default": 0,
                    "description": "Skip this many before returning.",
                },
            },
        },
        "handler": _tool_list_drawers,
    },
    "engine_memory_diary_read": {
        "description": (
            "Read the last N diary entries for an agent. Ordered by "
            "created_at DESC. Returns empty list if no entries exist "
            "for the agent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "default": "claude",
                    "description": "Defaults to 'claude' per project convention.",
                },
                "last_n": {
                    "type": "integer",
                    "default": 3,
                    "description": "Max entries returned.",
                },
            },
        },
        "handler": _tool_diary_read,
    },
}
