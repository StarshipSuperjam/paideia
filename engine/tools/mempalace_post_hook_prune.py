"""Defensive post-hook prune of sessions-wing transcript-mining pollution.

Per ADR 0090 commitment 2b. The upstream
``mempalace/hooks_cli.py:649-650`` hardcodes ``--wing sessions`` on
the ``_ingest_transcript`` subprocess, so every Stop / PreCompact
hook fire appends terminal-output capture into ``sessions/<noise-
room>``. The S-0186 one-shot prune via
``prune_mempalace.py --audit-sessions-pollution --apply`` clears
historical pollution, but the source itself keeps refilling. This
helper runs immediately after the hook completes and removes any
newly-added pollution drawers from the just-fired hook invocation.

Bounded scope (defensive — narrower than the audit-mode classifier):

- Wing exact match: ``sessions``.
- Room IN the same noise-room set as ``audit_sessions_pollution`` in
  ``prune_mempalace.py``.
- ``created_at`` (drawer metadata) strictly greater than ``--since``.

The ``--since`` parameter is the hook-wrapper's captured start
timestamp (ISO-8601 UTC). Drawers older than that window are NOT
touched even if they match the wing+room classifier — they belong to
an earlier hook fire and the one-shot audit prune is the right tool
for them.

Idempotent: re-running with the same ``--since`` is a no-op once the
matching drawers are gone (no candidates to delete).

Exit codes
----------
- ``0`` — clean run (drawers deleted OR no candidates found).
- ``2`` — palace path missing or unreadable (palace not yet
  initialized at first session boot). Logged but does NOT block the
  hook; caller treats as advisory.
- ``3`` — chromadb open or delete raised. Logged but does NOT block
  the hook.

Retirement criterion
--------------------
Retire when upstream PR
``https://github.com/MemPalace/mempalace/pull/1511`` (``MEMPALACE_WING``
env-var override) lands and ``mempalace-hook-wrapper.sh`` wires the
override to direct transcript ingest into ``wing_paideia`` (or
equivalent) at source. At that point the pollution stops being
generated and the defensive prune has no candidates to find.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

# Mirrors the classifier in ``prune_mempalace.py`` so the two stay in
# lock-step. Any change here must be paired with the audit-mode
# constant.
_SESSIONS_POLLUTION_WING = "sessions"
_SESSIONS_POLLUTION_ROOMS = (
    "technical",
    "planning",
    "architecture",
    "general",
    "problems",
)


def resolve_palace_path(arg_palace: str | None) -> Path:
    """Resolve palace path with env > CLI > default precedence."""
    env = os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    if env:
        return Path(env)
    if arg_palace:
        return Path(arg_palace)
    return Path.home() / ".mempalace" / "palace"


def enumerate_recent_pollution_internal_ids(
    palace_path: Path, since_iso: str
) -> list[str]:
    """Return chromadb internal IDs of recent sessions-wing pollution.

    The created_at metadata is an ISO-8601 timestamp string captured
    by mempalace at drawer-add time. Lexical comparison (``>``)
    works correctly for ISO-8601 strings — the format is sort-stable.
    """
    db = palace_path / "chroma.sqlite3"
    if not db.is_file():
        raise FileNotFoundError(db)
    placeholders = ",".join("?" for _ in _SESSIONS_POLLUTION_ROOMS)
    sql = f"""
        SELECT DISTINCT em_w.id
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id
        JOIN embedding_metadata em_t ON em_w.id = em_t.id
        WHERE em_w.key='wing' AND em_w.string_value=?
          AND em_r.key='room' AND em_r.string_value IN ({placeholders})
          AND em_t.key='created_at' AND em_t.string_value > ?
        """  # nosec B608  # placeholder string construction; values parameterized via execute()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            sql,
            (_SESSIONS_POLLUTION_WING, *_SESSIONS_POLLUTION_ROOMS, since_iso),
        ).fetchall()
    finally:
        con.close()
    return [str(r[0]) for r in rows]


def fetch_uuids_for_internal_ids(
    palace_path: Path, internal_ids: list[str]
) -> list[str]:
    """Map chromadb internal-IDs to drawer UUIDs.

    Sibling to ``prune_mempalace.fetch_drawer_uuids`` — kept local to
    avoid a cross-module import at hook-run time (the hook wrapper
    runs in a constrained PATH; one-file tool with stdlib + chromadb
    keeps the import surface narrow).
    """
    if not internal_ids:
        return []
    db = palace_path / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in internal_ids)
        sql = f"SELECT embedding_id FROM embeddings WHERE id IN ({placeholders})"  # nosec B608  # placeholder string construction; values parameterized via execute()
        rows = con.execute(sql, internal_ids).fetchall()
    finally:
        con.close()
    return [r[0] for r in rows]


def delete_drawers(palace_path: Path, uuids: list[str]) -> int:
    """Delete a batch of drawers from ``mempalace_drawers``.

    Returns the count requested. chromadb's delete is silent on
    success.
    """
    if not uuids:
        return 0
    import chromadb

    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection("mempalace_drawers")
    col.delete(ids=uuids)
    return len(uuids)


def run(palace_path: Path, since_iso: str) -> tuple[int, int]:
    """Run the prune. Returns (exit_code, deleted_count)."""
    try:
        internal_ids = enumerate_recent_pollution_internal_ids(palace_path, since_iso)
    except FileNotFoundError as exc:
        print(
            f"[mempalace-post-hook-prune] palace not found: {exc}",
            file=sys.stderr,
        )
        return 2, 0
    except sqlite3.Error as exc:
        print(
            f"[mempalace-post-hook-prune] sqlite error: {exc}",
            file=sys.stderr,
        )
        return 3, 0

    if not internal_ids:
        return 0, 0

    uuids = fetch_uuids_for_internal_ids(palace_path, internal_ids)
    try:
        deleted = delete_drawers(palace_path, uuids)
    except Exception as exc:  # noqa: BLE001  # bounded to chromadb open / delete; broad catch is intentional for hook safety
        print(
            f"[mempalace-post-hook-prune] delete error: {exc}",
            file=sys.stderr,
        )
        return 3, 0
    return 0, deleted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Defensive post-hook prune of newly-added sessions-wing "
            "transcript-mining pollution drawers. Idempotent. Always "
            "logs to stderr; exit code is advisory (the hook wrapper "
            "does not block on non-zero)."
        ),
    )
    parser.add_argument(
        "--palace",
        help="Palace path override (also MEMPALACE_PROBE_PALACE_PATH env).",
    )
    parser.add_argument(
        "--since",
        required=True,
        help=(
            "ISO-8601 UTC timestamp (e.g. 2026-05-15T19:56:32Z). Drawers "
            "with created_at <= this value are NOT touched. Pass the "
            "hook-wrapper's captured start timestamp."
        ),
    )
    args = parser.parse_args(argv)

    palace_path = resolve_palace_path(args.palace)
    exit_code, deleted = run(palace_path, args.since)
    if deleted:
        print(
            f"[mempalace-post-hook-prune] deleted {deleted} sessions-wing "
            f"pollution drawer(s) added since {args.since}",
            file=sys.stderr,
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
