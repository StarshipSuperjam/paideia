"""Diary read/write surface for the engine-memory substrate.

Plain-text storage in the ``diary`` SQLite table — per ADR 0091, no
AAAK compression. SQLite holds the column type ``TEXT`` directly; the
size cost of uncompressed prose at one-entry-per-session is negligible
(~1KB per row × hundreds of sessions = sub-MB).

Two operations:

* :func:`write_entry` — author one diary row per session at close (the
  mempalace_diary_write equivalent; the closing skill calls this at
  step 1 once the S-0192 cutover lands).
* :func:`read_entries` — read the last N entries for an agent. Used by
  the boot orchestrator (wired at S-0191) to surface prior-session
  reflection into ``current_plan.md``.

Both wrap :func:`engine.memory.connection.get_conn` per call — open +
operate + close. Matches the existing test pattern in
``test_connection.py`` / ``test_schema.py``. The MCP layer (wired in
``engine/memory/tools.py``) re-exports these as ``engine_memory_diary_write``
and ``engine_memory_diary_read``.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from engine.memory.connection import get_conn


def write_entry(
    content: str,
    *,
    agent_name: str = "claude",
    session_id: str | None = None,
    topic: str | None = None,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Write a diary entry. Returns ``{id, created_at}``.

    ``content`` must be non-empty (the table accepts NOT NULL but no
    length CHECK; the Python layer enforces a minimum so a misfire that
    passes ``""`` is caught here rather than producing a useless row).
    """
    if not content or not content.strip():
        raise ValueError("diary entry content must be non-empty")

    entry_id = uuid.uuid4().hex
    conn = get_conn(db_path)
    try:
        conn.execute(
            "INSERT INTO diary (id, agent_name, session_id, content, topic) "
            "VALUES (?, ?, ?, ?, ?)",
            (entry_id, agent_name, session_id, content, topic),
        )
        row = conn.execute(
            "SELECT created_at FROM diary WHERE id = ?", (entry_id,)
        ).fetchone()
    finally:
        conn.close()

    return {"id": entry_id, "created_at": row[0]}


def read_entries(
    *,
    agent_name: str = "claude",
    last_n: int = 3,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Return up to ``last_n`` most-recent diary entries for ``agent_name``.

    Ordered by ``created_at DESC``. Returns ``[]`` if no entries exist
    for the agent (e.g., fresh substrate or first session for that
    agent_name).
    """
    if last_n < 1:
        return []

    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT id, agent_name, session_id, created_at, topic, content "
            "FROM diary WHERE agent_name = ? "
            "ORDER BY created_at DESC, id DESC LIMIT ?",
            (agent_name, last_n),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "id": r[0],
            "agent_name": r[1],
            "session_id": r[2],
            "created_at": r[3],
            "topic": r[4],
            "content": r[5],
        }
        for r in rows
    ]
