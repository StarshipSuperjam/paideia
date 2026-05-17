"""Migration replay: MemPalace → engine_memory SQLite substrate.

One-time export of curated drawers + diary entries from the live
chromadb palace into the engine-memory SQLite substrate. Initial
S-0192 run closed T1-D; S-0193 extension landed the recovery of
~130 load-bearing drawers the original filter dropped (closes T1-E
per ``engine/build_readiness/engine_memory_substrate_first_exercise.md``).

Layer 1 contract
----------------
Source: ``~/.mempalace/palace`` (read-only sqlite for enumeration +
chromadb client for content fetch — same dual-access pattern as
``engine/tools/prune_mempalace.py``). Curated drawers from the
canonical rooms (``CURATED_ROOMS``) + the S-0193 extended rooms
(``EXTENDED_ROOM_MAPPING``) + the mixed ``general`` room are enumerated
across the paideia + wing_paideia wings; the sessions wing (1142
auto-capture drawers) is filtered at SQL level. Diary entries
(``room='diary'``) are imported separately into the new substrate's
``diary`` table from any wing.

Lineage discipline: every imported drawer gets a fresh ``uuid4`` ID
plus a ``lineage`` row tagged with the current ``MIGRATION_SOURCE``
(S-0192's ``mempalace_replay_S-0192`` for the original 383 drawers;
S-0193's ``mempalace_replay_S-0193_extension`` for the 102 recovered
drawers) and ``imported_from='mempalace:<old_uuid>'``. The pre-flight
lookup ``SELECT drawer_id FROM lineage WHERE imported_from=?`` is
source-agnostic, so re-running with a new source tag correctly skips
drawers imported under any prior tag — idempotency holds across both
the S-0192 and S-0193 runs.

Diary entries use deterministic ``uuid5`` IDs derived from the
mempalace UUID — the diary table has no lineage row of its own.

Classification rules (S-0193 extension)
---------------------------------------
``_resolve_target_room(source_room, content)`` decides each drawer's
target room. Priority:

1. Content-prefix override (defense-in-depth): drawers whose content
   begins with ``[pushback]`` / ``[lesson]`` / ``[decision]`` /
   ``[exploration]`` / ``# Verbatim exchange`` route to the matching
   canonical room regardless of source-room name. Rescues misfiling.
2. Source room in ``CURATED_ROOMS``: pass through unchanged.
3. Source room in ``EXTENDED_ROOM_MAPPING``: apply the mapping
   (``problems``→``pushback``, etc.).
4. Otherwise: skip (logged as ``skipped-no-mapping``).

The S-0192 original migration's hardcoded ``CURATED_ROOMS`` filter
dropped 87 ``[pushback]``-content drawers misfiled into a ``problems``
room name + 13 foundation/historical records. S-0193 plan-mode spot-
check surfaced the gap; this script's classifier closes it.

Wing filter
-----------
``ALLOWED_DRAWER_WINGS = ('paideia', 'wing_paideia')``. The sessions
wing's 1142 drawers (technical/architecture/problems rooms,
``added_by=mempalace``) are auto-capture transcript residue, not
curated content; excluding them at the SQL ``WHERE em_w.string_value
IN (...)`` level prevents them from ever reaching the classifier.
Diary entries (separate enumerator) still scan all wings since
``wing_claude``/``wing_paideia``/orphan ``wing_<6-hex>`` all carry
legitimate diary content.

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

# Curated rooms — the original S-0192 default. ``work`` is auto-capture;
# ``general`` is legacy fallback. Both deliberately omitted from this
# canonical set per the S-0186 prune lesson.
CURATED_ROOMS: tuple[str, ...] = (
    "decisions",
    "pushback",
    "lessons",
    "exploration",
    "operations",
)

# S-0193 extension: rooms in the ``paideia`` / ``wing_paideia`` wings
# that carry load-bearing content despite their non-canonical names.
# Each entry maps source-room -> target-room in the engine_memory
# substrate. Discovered during the S-0193 plan-mode parity audit:
#
# - ``problems`` (87 drawers) — every spot-check entry was
#   ``[pushback]``-prefixed pushback content misfiled by an upstream
#   auto-classifier into a ``problems`` room name (S-0075 cross-bridge
#   curation, S-0010 ADR-warranted judgment, S-0061 amend-discipline,
#   S-0155 self-pushback, etc.).
# - ``foundation-planning-s0001`` (10) — verbatim S-0001 founding-
#   decision exchanges that became ADRs (bimodal session model,
#   eager-claim load-bearing, health-check cadence → ADR 0022).
# - ``s0003-adr-collection`` (2) — Phase 0 ADR-collection decision
#   narrative.
# - ``project`` (1) — PDG papers extraction state snapshot.
#
# ``general`` (28, mixed) is handled by the content-prefix classifier
# below rather than blanket-mapped — some drawers are pushback content,
# others are exploration framings, others are legacy noise.
EXTENDED_ROOM_MAPPING: dict[str, str] = {
    "problems": "pushback",
    "foundation-planning-s0001": "decisions",
    "s0003-adr-collection": "decisions",
    "project": "operations",
}

# Wings whose curated-room content is eligible for migration. The
# ``sessions`` wing is the largest source of auto-capture pollution
# (1142 drawers across technical/architecture/problems rooms at
# S-0193 spot-check); excluding it at the SQL level is the
# defense-in-depth that ensures sessions-wing technical/architecture/
# problems content never reaches the in-process classifier.
ALLOWED_DRAWER_WINGS: tuple[str, ...] = ("paideia", "wing_paideia")

# Content-prefix classifier — defense-in-depth that overrides the
# source-room mapping when a drawer's content begins with a known
# canonical-content marker. Catches misfiling: a ``decisions`` drawer
# whose content starts with ``[pushback]`` routes to ``pushback`` (not
# ``decisions``); a ``general`` drawer whose content starts with
# ``[lesson]`` is rescued from the legacy-fallback bucket. Lookup is
# longest-prefix-first to handle overlaps.
CONTENT_PREFIX_OVERRIDES: tuple[tuple[str, str], ...] = (
    ("# Verbatim exchange", "decisions"),
    ("[pushback]", "pushback"),
    ("[lesson]", "lessons"),
    ("[decision]", "decisions"),
    ("[exploration]", "exploration"),
)

# Diary entries live in their own ``diary`` table — fetched from any
# wing where ``room='diary'``.
DIARY_ROOM = "diary"

# Lineage source tag — identifies every drawer migrated by this script.
# Default is the S-0193 extension tag (newly-imported drawers carry it);
# the S-0192 original-migration tag is preserved on the 383 drawers it
# inserted, and the existing-import lookup is source-agnostic so
# re-running with the new tag does NOT duplicate those rows.
MIGRATION_SOURCE = "mempalace_replay_S-0193_extension"

# Stable namespace for diary UUID5 derivation. The diary table has no
# lineage relationship; deterministic IDs are how we hold idempotency
# across both the S-0192 original migration and the S-0193 extension —
# the same mempalace UUID maps to the same engine_memory diary ID
# regardless of which run inserts it.
DIARY_UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000192")


def _resolve_target_room(source_room: str, content: str) -> str | None:
    """Map a (source_room, content) pair to a target engine_memory room.

    Returns the target room name (one of CURATED_ROOMS) or ``None`` if
    the drawer should be skipped (no recognized mapping AND no canonical
    content prefix). Priority order:

    1. **Content-prefix override** wins over source-room mapping —
       defense-in-depth against misfiling. A drawer whose content begins
       with ``[pushback]`` always routes to ``pushback`` regardless of
       whether its source room was ``decisions`` / ``general`` /
       ``problems``.
    2. **Source-room in CURATED_ROOMS** — pass through unchanged.
    3. **Source-room in EXTENDED_ROOM_MAPPING** — apply the mapping.
    4. **Otherwise** — return ``None`` (skip; logged as
       ``skipped-no-mapping``).

    Empty / whitespace-only content also returns ``None`` (the existing
    ``insert_drawers`` skipped-missing-content path handles it).
    """
    if not content or not content.strip():
        return None
    stripped = content.lstrip()
    for prefix, target in CONTENT_PREFIX_OVERRIDES:
        if stripped.startswith(prefix):
            return target
    if source_room in CURATED_ROOMS:
        return source_room
    if source_room in EXTENDED_ROOM_MAPPING:
        return EXTENDED_ROOM_MAPPING[source_room]
    return None


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
    drawer_skipped_no_mapping: int = 0
    drawer_per_room: dict[str, int] = field(default_factory=dict)
    # S-0193 extension: per-source-room and source→target mapping
    # accounting. ``drawer_per_source_room`` shows the enumeration
    # breakdown (every distinct source-room hit, regardless of whether
    # the drawer survived classification). ``drawer_source_target_pairs``
    # records the (source_room, target_room) tuples actually inserted,
    # so an audit can see *where* recovered content went.
    drawer_per_source_room: dict[str, int] = field(default_factory=dict)
    drawer_source_target_pairs: dict[str, int] = field(default_factory=dict)
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
    """Enumerate paideia-wing drawers across all curated + extended rooms.

    Source rooms enumerated: ``CURATED_ROOMS`` (the canonical S-0192 set)
    + the keys of ``EXTENDED_ROOM_MAPPING`` (the S-0193 extension that
    rescues misfiled load-bearing content) + ``general`` (handled by the
    content-prefix classifier).

    Wing filter: restricted to ``ALLOWED_DRAWER_WINGS`` (paideia +
    wing_paideia) to exclude the sessions-wing auto-capture pollution.
    Sessions-wing drawers in rooms named ``problems`` / ``technical`` /
    ``architecture`` are transcript-mining residue, not curated content,
    and must not enter the classifier.

    The in-process ``_resolve_target_room`` helper then decides whether
    each enumerated drawer maps to a target engine_memory room or is
    skipped (``None``); the per-source-room enumeration count is logged
    in the MigrationReport regardless of classification outcome.
    """
    enumerable_rooms = (
        tuple(CURATED_ROOMS) + tuple(EXTENDED_ROOM_MAPPING) + ("general",)
    )
    room_placeholders = ",".join("?" for _ in enumerable_rooms)
    wing_placeholders = ",".join("?" for _ in ALLOWED_DRAWER_WINGS)
    sql = f"""
        SELECT em_w.id, em_w.string_value, em_r.string_value, em_f.string_value
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id AND em_r.key='room'
        LEFT JOIN embedding_metadata em_f
            ON em_w.id = em_f.id AND em_f.key='filed_at'
        WHERE em_w.key='wing'
          AND em_w.string_value IN ({wing_placeholders})
          AND em_r.string_value IN ({room_placeholders})
        """  # nosec B608  # placeholder construction, values parameterized
    rows = con.execute(sql, tuple(ALLOWED_DRAWER_WINGS) + enumerable_rooms).fetchall()
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
) -> tuple[
    int,
    int,
    int,
    int,
    dict[str, int],
    dict[str, int],
    dict[str, int],
]:
    """INSERT all candidates idempotently. Return counts + room tallies.

    Tuple: ``(inserted, skipped_already, skipped_missing, skipped_no_mapping,
    per_target_room, per_source_room, source_target_pairs)``.

    Each candidate runs through ``_resolve_target_room`` to determine
    its target engine_memory room (which may differ from the source
    room — defense-in-depth against misfiling, and the path that
    rescues the S-0193 paideia/problems pushback corpus). Candidates
    with no recognized mapping (non-curated room AND no canonical
    content prefix) skip with ``skipped_no_mapping``.

    The pre-flight lineage lookup is source-agnostic (no
    ``AND source=?`` filter): a drawer imported under any prior
    source tag — including S-0192's ``mempalace_replay_S-0192`` — is
    treated as already-imported and skipped. This is what makes
    re-running the script with the S-0193 extension tag safe against
    the existing 383-drawer S-0192 corpus.
    """
    inserted = 0
    skipped_already = 0
    skipped_missing = 0
    skipped_no_mapping = 0
    per_target_room: dict[str, int] = {}
    per_source_room: dict[str, int] = {}
    source_target_pairs: dict[str, int] = {}
    cur = target.cursor()
    for cand in candidates:
        per_source_room[cand.room] = per_source_room.get(cand.room, 0) + 1
        if not cand.uuid or not cand.content:
            skipped_missing += 1
            continue
        target_room = _resolve_target_room(cand.room, cand.content)
        if target_room is None:
            skipped_no_mapping += 1
            continue
        pair_key = f"{cand.room}->{target_room}"
        imported_from = f"mempalace:{cand.uuid}"
        existing = cur.execute(
            "SELECT drawer_id FROM lineage WHERE imported_from=? LIMIT 1",
            (imported_from,),
        ).fetchone()
        if existing:
            skipped_already += 1
            per_target_room[target_room] = per_target_room.get(target_room, 0) + 1
            continue
        new_id = str(uuid.uuid4())
        filed_at = _filed_at_or_now(cand.filed_at)
        tags = _encode_tags(cand.metadata)
        # Preserve original metadata wholesale; embed old uuid + wing
        # + source room for traceability through the migration history.
        meta_payload = dict(cand.metadata)
        meta_payload["original_uuid"] = cand.uuid
        meta_payload["original_wing"] = cand.wing
        if cand.room != target_room:
            meta_payload["original_room"] = cand.room
            meta_payload["target_room_rationale"] = (
                "S-0193 extension: room remapped per "
                "EXTENDED_ROOM_MAPPING or CONTENT_PREFIX_OVERRIDES"
            )
        cur.execute(
            """
            INSERT INTO drawers
                (id, room, tags, source_kind, agent, session_id,
                 filed_at, content, metadata)
            VALUES (?, ?, ?, 'export_replay', 'claude', NULL, ?, ?, ?)
            """,
            (
                new_id,
                target_room,
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
        per_target_room[target_room] = per_target_room.get(target_room, 0) + 1
        source_target_pairs[pair_key] = source_target_pairs.get(pair_key, 0) + 1
    target.commit()
    return (
        inserted,
        skipped_already,
        skipped_missing,
        skipped_no_mapping,
        per_target_room,
        per_source_room,
        source_target_pairs,
    )


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
    expected_new_inserts: int,
    expected_per_target_room: dict[str, int],
) -> tuple[list[str], int, int, int]:
    """Assert post-migration invariants. Return (failures, fts_count, drawers_count, diary_count).

    Verifies the rows newly inserted under the current ``MIGRATION_SOURCE``
    tag (the S-0193 extension tag by default). Prior-session inserts
    (S-0192's ``mempalace_replay_S-0192`` tag) are NOT counted in
    ``expected_new_inserts`` — they're the already-imported drawers
    the source-agnostic lineage lookup correctly skips. The verifier's
    invariant is "this run inserted exactly the new drawers it
    enumerated minus skipped-already, all in the expected target rooms."
    """
    failures: list[str] = []
    cur = target.cursor()

    actual_lineage = cur.execute(
        "SELECT count(*) FROM lineage WHERE source=?",
        (MIGRATION_SOURCE,),
    ).fetchone()[0]
    if actual_lineage != expected_new_inserts:
        failures.append(
            f"lineage count mismatch under {MIGRATION_SOURCE!r}: "
            f"expected {expected_new_inserts}, observed {actual_lineage}"
        )

    for room, expected_n in expected_per_target_room.items():
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
                f"per-target-room mismatch for {room!r}: expected {expected_n}, "
                f"observed {actual}"
            )

    fts_count = cur.execute("SELECT count(*) FROM drawers_fts").fetchone()[0]
    drawers_count = cur.execute("SELECT count(*) FROM drawers").fetchone()[0]
    if fts_count != drawers_count:
        failures.append(
            f"FTS5 count out of sync: drawers={drawers_count}, fts={fts_count}"
        )

    diary_count = cur.execute("SELECT count(*) FROM diary").fetchone()[0]

    # Spot-check: 5 most-recent drawers under the current MIGRATION_SOURCE
    # tag must round-trip cleanly (content non-empty + retrievable by
    # imported_from). For an S-0193 extension run that newly inserts
    # pushback drawers, the spot-check exercises the pushback room; for
    # the original S-0192 tag it would have exercised decisions. Falling
    # back to the most-recent drawer regardless of room is the
    # source-agnostic check.
    spot = cur.execute(
        """
        SELECT d.id, d.content, l.imported_from
        FROM drawers d
        JOIN lineage l ON l.drawer_id = d.id
        WHERE l.source=?
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
    """Top-level orchestrator. Returns a MigrationReport.

    The S-0193 extension enumerates a wider source-room set + restricts
    to ``ALLOWED_DRAWER_WINGS``; ``_resolve_target_room`` (called from
    ``insert_drawers``) decides each drawer's target room or skips it.
    Verification runs against ONLY the rows newly inserted under
    ``MIGRATION_SOURCE`` (the source-agnostic lineage lookup means
    already-imported S-0192 drawers are correctly counted as skipped
    and don't appear in the expected-new-insert counts).
    """
    ro = open_palace_ro(palace_path)
    try:
        drawer_cands = enumerate_drawers(ro)
        diary_cands = enumerate_diary(ro)
    finally:
        ro.close()

    hydrate_candidates(palace_path, drawer_cands, diary_cands)

    report = MigrationReport(
        drawer_candidates=len(drawer_cands),
        diary_candidates=len(diary_cands),
    )

    if dry_run:
        # Pre-classification enumeration tally (target rooms resolved
        # in-process; skip categories not reflected without a target run).
        per_source: dict[str, int] = {}
        for cand in drawer_cands:
            per_source[cand.room] = per_source.get(cand.room, 0) + 1
        report.drawer_per_source_room = per_source
        return report

    db_path = target_db_path or resolve_db_path()
    target = get_conn(path=db_path)
    try:
        (
            ins,
            skip_a,
            skip_m,
            skip_n,
            per_target_room,
            per_source_room,
            source_target_pairs,
        ) = insert_drawers(target, drawer_cands)
        report.drawer_inserted = ins
        report.drawer_skipped_already_imported = skip_a
        report.drawer_skipped_missing_content = skip_m
        report.drawer_skipped_no_mapping = skip_n
        report.drawer_per_room = per_target_room
        report.drawer_per_source_room = per_source_room
        report.drawer_source_target_pairs = source_target_pairs
        d_ins, d_skip_a, d_skip_m = insert_diary(target, diary_cands)
        report.diary_inserted = d_ins
        report.diary_skipped_already_imported = d_skip_a
        report.diary_skipped_missing_content = d_skip_m
        # Expected new inserts under the current MIGRATION_SOURCE tag
        # equals the count we actually inserted in this run (the lineage
        # row created per insert carries this tag). Per-target-room
        # expectation is the same dict.
        expected_new_inserts = ins
        expected_per_target_room = {
            room: count for room, count in per_target_room.items() if count > 0
        }
        # Subtract already-skipped per-target-room counts: those rows
        # exist under a *prior* source tag (S-0192's
        # mempalace_replay_S-0192), not the current tag. The current-tag
        # per-target-room query won't see them.
        # Quick approach: rebuild expected_per_target_room from
        # source-target pairs (which only count NEW inserts, not skips).
        rebuilt: dict[str, int] = {}
        for pair_key, n in source_target_pairs.items():
            target_room = pair_key.split("->", 1)[1]
            rebuilt[target_room] = rebuilt.get(target_room, 0) + n
        expected_per_target_room = rebuilt
        failures, fts, drawers, diary = verify_migration(
            target, expected_new_inserts, expected_per_target_room
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
        f"engine-memory migration replay (mempalace → SQLite) [source={MIGRATION_SOURCE}]",
        f"  source candidates: {report.drawer_candidates} drawers + "
        f"{report.diary_candidates} diary entries",
        f"  drawers inserted: {report.drawer_inserted} "
        f"(already-imported: {report.drawer_skipped_already_imported}, "
        f"missing-content: {report.drawer_skipped_missing_content}, "
        f"no-mapping: {report.drawer_skipped_no_mapping})",
        f"  diary inserted: {report.diary_inserted} "
        f"(already-imported: {report.diary_skipped_already_imported}, "
        f"missing-content: {report.diary_skipped_missing_content})",
    ]
    if report.drawer_per_source_room:
        lines.append("  per-source-room (enumeration):")
        for room in sorted(report.drawer_per_source_room):
            lines.append(f"    {room}: {report.drawer_per_source_room[room]}")
    if report.drawer_source_target_pairs:
        lines.append("  source→target pairs (this run's inserts):")
        for pair in sorted(report.drawer_source_target_pairs):
            lines.append(f"    {pair}: {report.drawer_source_target_pairs[pair]}")
    if report.drawer_per_room:
        lines.append("  per-target-room (this run + already-imported):")
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
