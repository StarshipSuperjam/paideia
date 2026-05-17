"""Migration replay: MemPalace → engine_memory SQLite substrate.

One-time export of curated drawers + diary entries from the live
chromadb palace into the engine-memory SQLite substrate. Closes T1-D
per ``engine/build_readiness/engine_memory_substrate_first_exercise.md``
(ADR 0091).

Layer 1 contract
----------------
Source: ``~/.mempalace/palace`` (read-only sqlite for enumeration +
chromadb client for content fetch — same dual-access pattern as
``engine/tools/prune_mempalace.py``). Curated drawers from rooms in
``CURATED_ROOMS`` are imported across every wing the palace contains;
diary entries (``room='diary'``) are imported separately into the new
substrate's ``diary`` table.

Lineage discipline: every imported drawer gets a fresh ``uuid4`` ID
plus a ``lineage`` row with ``source='mempalace_replay_S-0192'`` and
``imported_from='mempalace:<old_uuid>'``. The pre-flight lookup
``SELECT drawer_id FROM lineage WHERE imported_from=?`` makes rerun
idempotent without relying on ``INSERT OR IGNORE`` to recover from
mid-rerun half-state. Diary entries use deterministic ``uuid5`` IDs
derived from the mempalace UUID — the diary table has no lineage row
of its own.

Filter rules
------------
- Keep drawers where ``room IN ('decisions', 'pushback', 'lessons',
  'exploration', 'operations')``.
- Drop ``room='work'`` (transcript auto-capture residue), ``room='general'``
  (legacy fallback noise).
- Drop drawers in any non-canonical wing (orphan ``wing_<6-hex>``,
  historical ``-Users-...``) — these were drained at S-0086 / S-0088 /
  S-0092 but the classifier here is defensive against any post-prune
  drift.
- Diary entries are taken from ``room='diary'`` across every wing
  (canonical wing is ``wing_claude`` but per-project wings have
  historically captured diary writes too).

Content shape
-------------
- ``drawers.content``: raw chromadb document body (plaintext as written
  by mempalace; no decompression required — diary content is stored
  uncompressed by upstream ``tool_diary_write``).
- ``drawers.metadata``: JSON-encoded original chromadb metadata
  (``filed_at``, ``added_by``, ``source_file``, etc. preserved in full
  for forensic auditing).
- ``drawers.tags``: empty JSON array unless original metadata carried a
  ``tags`` field already in JSON form.

Exit codes
----------
- ``0`` — migration completed (or dry-run completed); all assertions
  passed.
- ``2`` — palace open failed.
- ``3`` — verification assertion failed (something migrated but not
  what was expected).
- ``4`` — chromadb import failed (package missing from venv).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.memory.connection import get_conn, resolve_db_path

# Curated rooms preserved in the migration. ``work`` and ``general``
# are explicitly dropped per the S-0186 prune lesson.
CURATED_ROOMS: tuple[str, ...] = (
    "decisions",
    "pushback",
    "lessons",
    "exploration",
    "operations",
)

# Diary entries live in their own ``diary`` table — fetched from any
# wing where ``room='diary'``.
DIARY_ROOM = "diary"

# Lineage source tag — identifies every drawer migrated by this script.
MIGRATION_SOURCE = "mempalace_replay_S-0192"

# Stable namespace for diary UUID5 derivation. The diary table has no
# lineage relationship; deterministic IDs are how we hold idempotency.
DIARY_UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000192")


@dataclass
class DrawerCandidate:
    """One curated drawer queued for migration."""

    internal_id: str
    wing: str
    room: str
    filed_at: str | None
    uuid: str = ""
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiaryCandidate:
    """One diary entry queued for migration."""

    internal_id: str
    wing: str
    filed_at: str | None
    uuid: str = ""
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationReport:
    """Outcome of a migration run (drawers + diary combined)."""

    drawer_candidates: int = 0
    drawer_inserted: int = 0
    drawer_skipped_already_imported: int = 0
    drawer_skipped_missing_content: int = 0
    drawer_per_room: dict[str, int] = field(default_factory=dict)
    diary_candidates: int = 0
    diary_inserted: int = 0
    diary_skipped_already_imported: int = 0
    diary_skipped_missing_content: int = 0
    fts_count_after: int = 0
    drawers_count_after: int = 0
    diary_count_after: int = 0
    assertion_failures: list[str] = field(default_factory=list)


# --------------------------------------------------------------------
# Source-side enumeration (read-only sqlite against chroma.sqlite3)
# --------------------------------------------------------------------


def resolve_palace_path(arg_palace: str | None) -> Path:
    """Resolve the source palace path (mirrors prune_mempalace.py)."""
    import os

    env = os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    if env:
        return Path(env)
    if arg_palace:
        return Path(arg_palace)
    return Path.home() / ".mempalace" / "palace"


def open_palace_ro(palace_path: Path) -> sqlite3.Connection:
    """Open chroma.sqlite3 read-only for fast enumeration."""
    db = palace_path / "chroma.sqlite3"
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def enumerate_drawers(con: sqlite3.Connection) -> list[DrawerCandidate]:
    """Enumerate curated drawers (any wing, rooms in CURATED_ROOMS)."""
    placeholders = ",".join("?" for _ in CURATED_ROOMS)
    sql = f"""
        SELECT em_w.id, em_w.string_value, em_r.string_value, em_f.string_value
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id AND em_r.key='room'
        LEFT JOIN embedding_metadata em_f
            ON em_w.id = em_f.id AND em_f.key='filed_at'
        WHERE em_w.key='wing'
          AND em_r.string_value IN ({placeholders})
        """  # nosec B608  # placeholder construction, values parameterized
    rows = con.execute(sql, CURATED_ROOMS).fetchall()
    return [
        DrawerCandidate(
            internal_id=str(r[0]),
            wing=r[1] or "",
            room=r[2] or "",
            filed_at=r[3],
        )
        for r in rows
    ]


def enumerate_diary(con: sqlite3.Connection) -> list[DiaryCandidate]:
    """Enumerate diary entries (any wing, room='diary')."""
    sql = """
        SELECT em_w.id, em_w.string_value, em_f.string_value
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id AND em_r.key='room'
        LEFT JOIN embedding_metadata em_f
            ON em_w.id = em_f.id AND em_f.key='filed_at'
        WHERE em_w.key='wing'
          AND em_r.string_value = ?
        """
    rows = con.execute(sql, (DIARY_ROOM,)).fetchall()
    return [
        DiaryCandidate(
            internal_id=str(r[0]),
            wing=r[1] or "",
            filed_at=r[2],
        )
        for r in rows
    ]


def map_internal_ids_to_uuids(
    palace_path: Path, internal_ids: list[str]
) -> dict[str, str]:
    """Map chromadb internal-IDs (integers) to drawer UUIDs."""
    if not internal_ids:
        return {}
    db = palace_path / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in internal_ids)
        sql = f"SELECT id, embedding_id FROM embeddings WHERE id IN ({placeholders})"  # nosec B608
        rows = con.execute(sql, internal_ids).fetchall()
    finally:
        con.close()
    return {str(r[0]): r[1] for r in rows}


def fetch_content_batch(
    palace_path: Path, uuids: list[str]
) -> dict[str, dict[str, Any]]:
    """Bulk-fetch (content, metadata) for a list of drawer UUIDs."""
    if not uuids:
        return {}
    try:
        import chromadb
    except ImportError as exc:  # pragma: no cover - venv invariant
        raise RuntimeError(
            "chromadb not importable from the venv; migration cannot fetch content"
        ) from exc
    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection("mempalace_drawers")
    res = col.get(ids=uuids, include=["metadatas", "documents"])
    out: dict[str, dict[str, Any]] = {}
    for u, doc, meta in zip(res["ids"], res["documents"] or [], res["metadatas"] or []):
        out[u] = {"content": doc or "", "metadata": dict(meta or {})}
    return out


def hydrate_candidates(
    palace_path: Path,
    drawers: list[DrawerCandidate],
    diary: list[DiaryCandidate],
) -> None:
    """Fill ``uuid``, ``content``, ``metadata`` on each candidate in place."""
    all_internal = [d.internal_id for d in drawers] + [d.internal_id for d in diary]
    uuid_by_internal = map_internal_ids_to_uuids(palace_path, all_internal)
    all_uuids = list(uuid_by_internal.values())
    contents = fetch_content_batch(palace_path, all_uuids)
    for cand in drawers:
        cand.uuid = uuid_by_internal.get(cand.internal_id, "")
        if cand.uuid and cand.uuid in contents:
            cand.content = contents[cand.uuid]["content"]
            cand.metadata = contents[cand.uuid]["metadata"]
    for entry in diary:
        entry.uuid = uuid_by_internal.get(entry.internal_id, "")
        if entry.uuid and entry.uuid in contents:
            entry.content = contents[entry.uuid]["content"]
            entry.metadata = contents[entry.uuid]["metadata"]


# --------------------------------------------------------------------
# Target-side INSERT (engine_memory substrate)
# --------------------------------------------------------------------


def _encode_tags(meta: dict[str, Any]) -> str:
    """Coerce whatever ``tags`` shape into the substrate's JSON array."""
    raw = meta.get("tags")
    if raw is None:
        return "[]"
    if isinstance(raw, str):
        # Could already be a JSON string or a comma-separated string
        stripped = raw.strip()
        if stripped.startswith("["):
            try:
                json.loads(stripped)
                return stripped
            except json.JSONDecodeError:
                pass
        parts = [p.strip() for p in stripped.split(",") if p.strip()]
        return json.dumps(parts)
    if isinstance(raw, list):
        return json.dumps([str(t) for t in raw])
    return "[]"


def _filed_at_or_now(filed_at: str | None) -> str:
    """Fall back to current UTC if the source metadata had no filed_at."""
    if filed_at:
        return filed_at
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def insert_drawers(
    target: sqlite3.Connection, candidates: list[DrawerCandidate]
) -> tuple[int, int, int, dict[str, int]]:
    """INSERT all candidates idempotently. Return counts + per-room tally."""
    inserted = 0
    skipped_already = 0
    skipped_missing = 0
    per_room: dict[str, int] = {}
    cur = target.cursor()
    for cand in candidates:
        per_room[cand.room] = per_room.get(cand.room, 0)
        if not cand.uuid or not cand.content:
            skipped_missing += 1
            continue
        imported_from = f"mempalace:{cand.uuid}"
        existing = cur.execute(
            "SELECT drawer_id FROM lineage WHERE imported_from=? AND source=? LIMIT 1",
            (imported_from, MIGRATION_SOURCE),
        ).fetchone()
        if existing:
            skipped_already += 1
            per_room[cand.room] = per_room.get(cand.room, 0) + 1
            continue
        new_id = str(uuid.uuid4())
        filed_at = _filed_at_or_now(cand.filed_at)
        tags = _encode_tags(cand.metadata)
        # Preserve original metadata wholesale; embed old uuid for traceability.
        meta_payload = dict(cand.metadata)
        meta_payload["original_uuid"] = cand.uuid
        meta_payload["original_wing"] = cand.wing
        cur.execute(
            """
            INSERT INTO drawers
                (id, room, tags, source_kind, agent, session_id,
                 filed_at, content, metadata)
            VALUES (?, ?, ?, 'export_replay', 'claude', NULL, ?, ?, ?)
            """,
            (
                new_id,
                cand.room,
                tags,
                filed_at,
                cand.content,
                json.dumps(meta_payload, ensure_ascii=False),
            ),
        )
        cur.execute(
            """
            INSERT OR IGNORE INTO lineage
                (drawer_id, source, imported_from, source_wing,
                 source_filed_at, imported_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                new_id,
                MIGRATION_SOURCE,
                imported_from,
                cand.wing,
                cand.filed_at,
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        inserted += 1
        per_room[cand.room] = per_room.get(cand.room, 0) + 1
    target.commit()
    return inserted, skipped_already, skipped_missing, per_room


def insert_diary(
    target: sqlite3.Connection, entries: list[DiaryCandidate]
) -> tuple[int, int, int]:
    """INSERT diary entries with deterministic UUID5 IDs. Idempotent."""
    inserted = 0
    skipped_already = 0
    skipped_missing = 0
    cur = target.cursor()
    for entry in entries:
        if not entry.uuid or not entry.content:
            skipped_missing += 1
            continue
        deterministic_id = str(
            uuid.uuid5(DIARY_UUID_NAMESPACE, f"mempalace-diary:{entry.uuid}")
        )
        existing = cur.execute(
            "SELECT id FROM diary WHERE id=? LIMIT 1",
            (deterministic_id,),
        ).fetchone()
        if existing:
            skipped_already += 1
            continue
        topic = entry.metadata.get("topic") or None
        session_id = entry.metadata.get("session_id") or None
        created_at = _filed_at_or_now(entry.filed_at)
        cur.execute(
            """
            INSERT INTO diary (id, agent_name, session_id, created_at, content, topic)
            VALUES (?, 'claude', ?, ?, ?, ?)
            """,
            (deterministic_id, session_id, created_at, entry.content, topic),
        )
        inserted += 1
    target.commit()
    return inserted, skipped_already, skipped_missing


# --------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------


def verify_migration(
    target: sqlite3.Connection,
    expected_drawers_lineage: int,
    expected_per_room: dict[str, int],
) -> tuple[list[str], int, int, int]:
    """Assert post-migration invariants. Return (failures, fts_count, drawers_count, diary_count)."""
    failures: list[str] = []
    cur = target.cursor()

    actual_lineage = cur.execute(
        "SELECT count(*) FROM lineage WHERE source=?",
        (MIGRATION_SOURCE,),
    ).fetchone()[0]
    if actual_lineage != expected_drawers_lineage:
        failures.append(
            f"lineage count mismatch: expected {expected_drawers_lineage}, "
            f"observed {actual_lineage}"
        )

    for room, expected_n in expected_per_room.items():
        actual = cur.execute(
            """
            SELECT count(*) FROM drawers d
            JOIN lineage l ON l.drawer_id = d.id
            WHERE l.source=? AND d.room=?
            """,
            (MIGRATION_SOURCE, room),
        ).fetchone()[0]
        if actual != expected_n:
            failures.append(
                f"per-room mismatch for {room!r}: expected {expected_n}, "
                f"observed {actual}"
            )

    fts_count = cur.execute("SELECT count(*) FROM drawers_fts").fetchone()[0]
    drawers_count = cur.execute("SELECT count(*) FROM drawers").fetchone()[0]
    if fts_count != drawers_count:
        failures.append(
            f"FTS5 count out of sync: drawers={drawers_count}, fts={fts_count}"
        )

    diary_count = cur.execute("SELECT count(*) FROM diary").fetchone()[0]

    # Spot-check: 5 most-recent migrated decision drawers must round-trip
    # cleanly (content non-empty + retrievable by imported_from).
    spot = cur.execute(
        """
        SELECT d.id, d.content, l.imported_from
        FROM drawers d
        JOIN lineage l ON l.drawer_id = d.id
        WHERE l.source=? AND d.room='decisions'
        ORDER BY d.filed_at DESC
        LIMIT 5
        """,
        (MIGRATION_SOURCE,),
    ).fetchall()
    for row in spot:
        if not row[1] or not row[1].strip():
            failures.append(f"spot-check: empty content for drawer {row[0]} ({row[2]})")

    return failures, fts_count, drawers_count, diary_count


# --------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------


def run_migration(
    palace_path: Path,
    target_db_path: Path | None = None,
    *,
    dry_run: bool = False,
) -> MigrationReport:
    """Top-level orchestrator. Returns a MigrationReport."""
    ro = open_palace_ro(palace_path)
    try:
        drawer_cands = enumerate_drawers(ro)
        diary_cands = enumerate_diary(ro)
    finally:
        ro.close()

    hydrate_candidates(palace_path, drawer_cands, diary_cands)

    # Expected counts (built from hydrated candidates before INSERT)
    expected_per_room: dict[str, int] = {}
    for cand in drawer_cands:
        if cand.uuid and cand.content:
            expected_per_room[cand.room] = expected_per_room.get(cand.room, 0) + 1
    expected_lineage = sum(expected_per_room.values())

    report = MigrationReport(
        drawer_candidates=len(drawer_cands),
        diary_candidates=len(diary_cands),
        drawer_per_room=dict(expected_per_room),
    )

    if dry_run:
        return report

    db_path = target_db_path or resolve_db_path()
    target = get_conn(path=db_path)
    try:
        ins, skip_a, skip_m, per_room = insert_drawers(target, drawer_cands)
        report.drawer_inserted = ins
        report.drawer_skipped_already_imported = skip_a
        report.drawer_skipped_missing_content = skip_m
        report.drawer_per_room = per_room
        d_ins, d_skip_a, d_skip_m = insert_diary(target, diary_cands)
        report.diary_inserted = d_ins
        report.diary_skipped_already_imported = d_skip_a
        report.diary_skipped_missing_content = d_skip_m
        failures, fts, drawers, diary = verify_migration(
            target, expected_lineage, expected_per_room
        )
        report.assertion_failures = failures
        report.fts_count_after = fts
        report.drawers_count_after = drawers
        report.diary_count_after = diary
    finally:
        target.close()
    return report


def render_console(report: MigrationReport) -> str:
    """Render a brief human-readable summary for stdout."""
    lines = [
        "engine-memory migration replay (mempalace → SQLite)",
        f"  source candidates: {report.drawer_candidates} drawers + "
        f"{report.diary_candidates} diary entries",
        f"  drawers inserted: {report.drawer_inserted} "
        f"(already-imported skipped: {report.drawer_skipped_already_imported}, "
        f"missing-content skipped: {report.drawer_skipped_missing_content})",
        f"  diary inserted: {report.diary_inserted} "
        f"(already-imported skipped: {report.diary_skipped_already_imported}, "
        f"missing-content skipped: {report.diary_skipped_missing_content})",
        "  per-room:",
    ]
    for room in sorted(report.drawer_per_room):
        lines.append(f"    {room}: {report.drawer_per_room[room]}")
    lines.append(
        f"  post-state: drawers={report.drawers_count_after}, "
        f"fts={report.fts_count_after}, diary={report.diary_count_after}"
    )
    if report.assertion_failures:
        lines.append("  assertion failures:")
        for f in report.assertion_failures:
            lines.append(f"    - {f}")
    else:
        lines.append("  assertions: PASS")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Replay curated MemPalace drawers + diary into engine_memory.",
    )
    parser.add_argument(
        "--palace",
        default=None,
        help="MemPalace path (default: ~/.mempalace/palace; env override: MEMPALACE_PROBE_PALACE_PATH)",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Target engine_memory SQLite path (default: resolved via engine.memory.connection)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enumerate + hydrate only; no INSERTs against the target substrate.",
    )
    args = parser.parse_args(argv)

    palace_path = resolve_palace_path(args.palace)
    if not (palace_path / "chroma.sqlite3").exists():
        print(
            f"[migrate] palace not found at {palace_path}",
            file=sys.stderr,
        )
        return 2

    target_db = Path(args.db_path) if args.db_path else None
    try:
        report = run_migration(palace_path, target_db, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"[migrate] {exc}", file=sys.stderr)
        return 4

    print(render_console(report))
    if report.assertion_failures:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
