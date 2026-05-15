"""Prune MemPalace noise floor: mined ops-doc drawers + orphaned per-worktree wings + historical full-encoded-path wings.

Layer 1 contract per Issues #40 + #41. Issue #40 parts A
(mined ops-doc drawers) and B (orphaned per-worktree wings) closed at
S-0088. Issue #40 part C / Issue #41 (historical full-encoded-path
wings) closes at S-0092 — the apply path is wired here, gated by the
S-0092 signal probe (engine/docs/audits/historical-wings-signal-probe-
S-0092.md) which verified zero preservation candidates across the
37,634-drawer population.

Four modes
----------
- ``--audit-mined-ops-docs`` — list/delete drawers in the ``paideia``
  wing's ``general`` and ``operations`` rooms whose ``added_by``
  metadata equals exactly ``claude-s0002`` (the S-0002 mining
  session). Excludes ``claude-s0002-manual`` (curated content from
  the same era; ``[decision]``-prefixed bodies that landed in the
  wrong room) and any drawer added by a post-S-0002 session
  (``claude-opus-4-7-S-NNNN``, ``claude``).
- ``--audit-orphan-wings`` — list/delete drawers in wings matching
  ``wing_<6-hex>`` (the upstream wing-naming bug's per-worktree
  output). Explicitly excludes ``wing_paideia`` (main-session
  captures), ``wing_claude`` (canonical AI diary), and ``sessions``
  (auto-captured session content).
- ``--audit-historical-paths`` — list/delete drawers in
  ``-Users-...`` and ``--claude-worktrees-`` historical full-encoded-
  path wings. Apply path landed at S-0092 (Issue #41). The
  S-0092 signal probe verified zero preservation candidates in the
  population (no ``decision``/``pushback``/``lesson`` markers; all
  ``added_by=mempalace``; all ``room=general``); the apply path is
  delete-only and does not wire ``--preserve-ids``. If a future
  similar wing surfaces signal candidates, extend
  ``audit_historical_paths()`` at that point.
- ``--audit-sessions-pollution`` — list/delete drawers in the
  ``sessions`` wing's noise rooms (``technical``, ``planning``,
  ``architecture``, ``general``, ``problems``). Per ADR 0090
  commitment 2b. Upstream ``mempalace/hooks_cli.py:649-650`` hardcodes
  ``--wing sessions`` on the transcript-mining subprocess; this audit
  drains the resulting pollution while preserving curated rooms
  (``decisions``, ``lessons``, ``pushback``, ``diary``,
  ``operations``) in the same wing. Retire when upstream PR #1511
  (``MEMPALACE_WING`` env-var override) lands and the hook wrapper
  wires the override.

Common flags
------------
- ``--palace <path>`` (also ``MEMPALACE_PROBE_PALACE_PATH`` env): test
  override; defaults to ``~/.mempalace/palace``.
- ``--apply`` to mutate. Default is dry-run (counts + sample only).
- ``--backup-dir <path>``: ``cp -a`` backup BEFORE any mutation.
  Required when ``--apply`` is set; refuses with non-zero exit if
  backup creation fails. Mirrors the ``mempalace_rebuild_hnsw.py``
  Phase 0 pre-mutation backup discipline (S-0084 precedent).

Exit codes
----------
- ``0`` — clean run.
- ``2`` — backup creation failed when ``--apply`` was requested; nothing
  mutated.
- ``3`` — chromadb open failed; nothing mutated.

Out of scope
------------
- Does NOT preserve-via-re-capture. Orphan-wing drawers (S-0088
  verification) and historical-path drawers (S-0092 verification) are
  uniformly auto-capture residue with no curated markers; bulk delete
  is consistent with both audits' "Recommend retire" verdicts.
- Mined-ops-docs and orphan-wings modes do NOT modify
  ``mempalace_closets`` — neither classifier matched closet rows in
  the live data at S-0088 audit time, and the deleted drawers had no
  closets pointing at them. The historical-paths mode DOES touch
  ``mempalace_closets`` because closets carry the same ``-Users-...``
  wing tag as the drawers they group, and the S-0092 first apply
  surfaced 67 surviving closet rows after the drawer pass; the apply
  now fans deletes out by collection (``fetch_uuids_by_collection``).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Pattern matching orphan per-worktree wings: ``wing_`` + 6 hex chars.
# The upstream wing-naming bug derives these from ``rsplit("-", 1)[-1]``
# of the encoded transcript path; the suffix is always 6 chars in the
# observed dataset. ``wing_paideia`` and ``wing_claude`` are explicit
# canonical exclusions; the regex naturally excludes longer names.
_ORPHAN_WING_RE = re.compile(r"^wing_[0-9a-f]{6}$")

# Classifier exclusions for orphan-wing audit. Even if a future variant
# matches the regex, these are preserved by name.
_CANONICAL_NON_ORPHAN_WINGS = frozenset(
    {"paideia", "wing_paideia", "wing_claude", "sessions"}
)

# Pattern matching historical full-encoded-path wings. Two shapes
# observed: leading ``-Users-`` (worktree-derived absolute path) and
# embedded ``-claude-worktrees-`` (subdirectory marker).
_HISTORICAL_FULL_PATH_RE = re.compile(r"(^-Users-|--claude-worktrees-)")

# Classifier signal for mined ops-doc drawers: exact ``added_by`` match.
# The ``-manual`` suffix is excluded (curated content from S-0002 era
# that landed in the operations room with ``[decision]`` body prefix —
# these are real drawers, not mined chunks).
_MINED_ADDED_BY = "claude-s0002"

# Rooms in the ``paideia`` wing where mined ops-doc drawers landed.
_MINED_ROOMS = ("general", "operations")

# S-0186 sessions-wing pollution classifier per ADR 0090 commitment 2b.
# Upstream ``mempalace/hooks_cli.py:649-650`` hardcodes
# ``--wing sessions`` on ``_ingest_transcript`` subprocess; every Stop
# / PreCompact hook fire mines the active transcript into the
# ``sessions`` wing across these high-volume noise rooms. At S-0186
# audit time the live palace had 22,676 drawers, of which 21,893 (97%)
# were transcript-mining pollution distributed across these five rooms
# in the ``sessions`` wing alone. The classifier is wing+room-exact —
# room='decisions' (105 curated drawers), 'lessons', 'pushback',
# 'diary', 'operations' are explicitly preserved even when wing-mis'd.
# Retire when upstream PR #1511 (MEMPALACE_WING env-var override)
# lands and the hook wrapper wires the override.
_SESSIONS_POLLUTION_WING = "sessions"
_SESSIONS_POLLUTION_ROOMS = (
    "technical",
    "planning",
    "architecture",
    "general",
    "problems",
)


@dataclass
class AuditReport:
    """Structured report from a single prune mode.

    Returned from each ``audit_*`` function so ``main`` can format
    consistently across modes. Counts always populated; sample is up
    to 5 representative entries to make dry-run review actionable.
    """

    mode: str
    candidates: list[dict[str, Any]] = field(default_factory=list)
    sample: list[dict[str, Any]] = field(default_factory=list)
    deleted: int = 0
    preserved: int = 0
    notes: list[str] = field(default_factory=list)


def resolve_palace_path(arg_palace: str | None) -> Path:
    """Resolve the palace path with env-var > CLI > default precedence."""
    env = os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    if env:
        return Path(env)
    if arg_palace:
        return Path(arg_palace)
    return Path.home() / ".mempalace" / "palace"


def open_sqlite_ro(palace_path: Path) -> sqlite3.Connection:
    """Open chroma.sqlite3 read-only via SQLite URI mode.

    Used for fast metadata enumeration; does not contend with chromadb's
    own write locks.
    """
    db = palace_path / "chroma.sqlite3"
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def enumerate_mined_ids(con: sqlite3.Connection) -> list[str]:
    """Return chromadb internal IDs of mined ops-doc drawers.

    The query joins ``embedding_metadata`` against itself thrice to
    select drawers in ``paideia/<general|operations>`` whose
    ``added_by`` metadata matches the ``claude-s0002`` mining session
    exactly. Returns the SQLite-internal integer IDs as strings (the
    form chromadb's ``embeddings`` table uses) — caller maps to drawer
    UUIDs via ``get(...)`` if needed for chromadb deletion.
    """
    placeholders = ",".join("?" for _ in _MINED_ROOMS)
    sql = f"""
        SELECT DISTINCT em_w.id
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id
        JOIN embedding_metadata em_a ON em_w.id = em_a.id
        WHERE em_w.key='wing' AND em_w.string_value='paideia'
          AND em_r.key='room' AND em_r.string_value IN ({placeholders})
          AND em_a.key='added_by' AND em_a.string_value=?
        """  # nosec B608  # placeholder string construction; values parameterized via execute()
    rows = con.execute(sql, (*_MINED_ROOMS, _MINED_ADDED_BY)).fetchall()
    return [str(r[0]) for r in rows]


def enumerate_orphan_wing_drawers(
    con: sqlite3.Connection,
) -> list[tuple[str, str]]:
    """Return ``(wing_name, internal_id)`` pairs for orphan-wing drawers."""
    rows = con.execute(
        "SELECT id, string_value FROM embedding_metadata WHERE key='wing'"
    ).fetchall()
    out: list[tuple[str, str]] = []
    for internal_id, wing in rows:
        if wing in _CANONICAL_NON_ORPHAN_WINGS:
            continue
        if _ORPHAN_WING_RE.match(wing):
            out.append((wing, str(internal_id)))
    return out


def enumerate_sessions_pollution_ids(con: sqlite3.Connection) -> list[str]:
    """Return chromadb internal IDs of sessions-wing transcript-pollution drawers.

    Joins ``embedding_metadata`` against itself to select drawers in
    ``sessions/<polluted-room>`` per the S-0186 audit classifier.
    Curated rooms in the same wing (``decisions``, ``lessons``,
    ``pushback``, ``diary``, ``operations``) are excluded by the room
    whitelist — they remain in the sessions wing if the user does not
    consolidate them into ``paideia``.
    """
    placeholders = ",".join("?" for _ in _SESSIONS_POLLUTION_ROOMS)
    sql = f"""
        SELECT DISTINCT em_w.id
        FROM embedding_metadata em_w
        JOIN embedding_metadata em_r ON em_w.id = em_r.id
        WHERE em_w.key='wing' AND em_w.string_value=?
          AND em_r.key='room' AND em_r.string_value IN ({placeholders})
        """  # nosec B608  # placeholder string construction; values parameterized via execute()
    rows = con.execute(
        sql, (_SESSIONS_POLLUTION_WING, *_SESSIONS_POLLUTION_ROOMS)
    ).fetchall()
    return [str(r[0]) for r in rows]


def enumerate_historical_paths(con: sqlite3.Connection) -> list[tuple[str, int]]:
    """Return (wing_name, drawer_count) for historical full-encoded-path wings."""
    rows = con.execute(
        """
        SELECT string_value, COUNT(DISTINCT id)
        FROM embedding_metadata WHERE key='wing'
        GROUP BY string_value
        """
    ).fetchall()
    out: list[tuple[str, int]] = []
    for wing, n in rows:
        if _HISTORICAL_FULL_PATH_RE.search(wing):
            out.append((wing, int(n)))
    return sorted(out, key=lambda t: -t[1])


def enumerate_historical_path_drawer_internal_ids(
    con: sqlite3.Connection,
) -> list[tuple[str, str]]:
    """Return ``(wing_name, internal_id)`` pairs for every embedding row tagged with a historical full-encoded-path wing.

    Sibling to ``enumerate_orphan_wing_drawers`` — same single-pass
    metadata scan, different classifier. The result includes BOTH
    drawer and closet rows because ``embedding_metadata`` stores
    them together; the classifier filters on the ``wing`` tag only.
    Caller maps internal ids to collection-grouped UUIDs via
    ``fetch_uuids_by_collection`` for the actual chromadb delete
    batch.
    """
    rows = con.execute(
        "SELECT id, string_value FROM embedding_metadata WHERE key='wing'"
    ).fetchall()
    out: list[tuple[str, str]] = []
    for internal_id, wing in rows:
        if _HISTORICAL_FULL_PATH_RE.search(wing):
            out.append((wing, str(internal_id)))
    return out


def fetch_drawer_uuids(palace_path: Path, internal_ids: list[str]) -> list[str]:
    """Map chromadb internal-IDs to drawer UUIDs via the embeddings table.

    The collection.delete() API accepts drawer UUIDs (the ``ids``
    column on embedded rows); ``embedding_metadata.id`` is the
    SQLite-internal integer. This helper queries ``embeddings`` for
    the UUIDs corresponding to the provided internal-ids.

    Returns UUIDs without their collection origin — suitable when the
    caller already knows every internal-id belongs to a single
    collection (e.g., orphan-wings + mined-ops-docs which only ever
    have ``mempalace_drawers`` rows). For mixed-collection sets (e.g.,
    historical-paths, where closets and drawers both carry the
    ``-Users-...`` wing tag) use ``fetch_uuids_by_collection`` instead.
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


def fetch_uuids_by_collection(
    palace_path: Path, internal_ids: list[str]
) -> dict[str, list[str]]:
    """Group UUIDs by their owning chromadb collection.

    Joins ``embeddings`` -> ``segments`` -> ``collections`` so each
    UUID is bucketed under the collection name it lives in. Used by
    the historical-paths apply path because the ``-Users-...`` wing
    tag appears on BOTH ``mempalace_drawers`` rows and
    ``mempalace_closets`` rows, and ``collection.delete`` is
    collection-scoped — calling it on the wrong collection is a
    silent no-op (which is what the S-0092 first apply discovered:
    37,567 drawers deleted, 67 closets surviving).
    """
    if not internal_ids:
        return {}
    db = palace_path / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in internal_ids)
        sql = f"""
            SELECT e.embedding_id, c.name
            FROM embeddings e
            LEFT JOIN segments s ON e.segment_id = s.id
            LEFT JOIN collections c ON s.collection = c.id
            WHERE e.id IN ({placeholders})
            """  # nosec B608  # placeholder string construction; values parameterized via execute()
        rows = con.execute(sql, internal_ids).fetchall()
    finally:
        con.close()
    out: dict[str, list[str]] = {}
    for uuid, collection in rows:
        out.setdefault(collection or "<unknown>", []).append(uuid)
    return out


def sample_drawers(
    palace_path: Path, internal_ids: list[str], n: int = 5
) -> list[dict[str, Any]]:
    """Fetch up to n drawers' (uuid, doc_preview, metadata) for dry-run review."""
    if not internal_ids:
        return []
    sample_ids = internal_ids[:n]
    uuids = fetch_drawer_uuids(palace_path, sample_ids)
    if not uuids:
        return []
    try:
        import chromadb
    except ImportError:
        return []
    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection("mempalace_drawers")
    res = col.get(ids=uuids, include=["metadatas", "documents"])
    out: list[dict[str, Any]] = []
    docs = res["documents"] or []
    metas = res["metadatas"] or []
    for uuid, doc, meta in zip(res["ids"], docs, metas):
        out.append(
            {
                "uuid": uuid,
                "doc_preview": (doc or "")[:200],
                "wing": (meta or {}).get("wing"),
                "room": (meta or {}).get("room"),
                "added_by": (meta or {}).get("added_by"),
                "source_file": (meta or {}).get("source_file"),
            }
        )
    return out


def delete_drawers_by_uuid(
    palace_path: Path,
    uuids: list[str],
    *,
    collection: str = "mempalace_drawers",
) -> int:
    """Delete a batch of drawers from a chromadb collection.

    Returns the count requested (chromadb's delete is silent on
    success). Does not check post-state; caller may verify via a
    follow-up query. ``collection`` defaults to ``mempalace_drawers``
    to preserve the pre-S-0092 contract for the orphan-wings and
    mined-ops-docs callers; the historical-paths caller passes
    ``mempalace_closets`` explicitly for the closet-deletion pass.
    """
    if not uuids:
        return 0
    import chromadb

    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection(collection)
    col.delete(ids=uuids)
    return len(uuids)


def backup_palace(palace_path: Path, backup_dir: Path) -> None:
    """``cp -a`` the palace dir to backup_dir; raises on failure.

    Mirrors the ``mempalace_rebuild_hnsw.py`` Phase 0 precedent. The
    backup target must NOT already exist — collisions are caller-
    responsibility (timestamp the path). Uses ``shutil.copytree`` with
    ``copy2`` to preserve metadata, the closest stdlib equivalent of
    ``cp -a`` on macOS / Linux.
    """
    if backup_dir.exists():
        raise FileExistsError(
            f"backup target already exists: {backup_dir}; "
            f"choose a unique path or remove the existing backup first"
        )
    if not palace_path.is_dir():
        raise FileNotFoundError(f"palace not found: {palace_path}")
    shutil.copytree(palace_path, backup_dir, copy_function=shutil.copy2)


def audit_mined_ops_docs(palace_path: Path, *, apply: bool) -> AuditReport:
    """Audit + optionally delete mined ops-doc drawers."""
    report = AuditReport(mode="mined-ops-docs")
    con = open_sqlite_ro(palace_path)
    try:
        internal_ids = enumerate_mined_ids(con)
    finally:
        con.close()

    report.candidates = [{"internal_id": iid} for iid in internal_ids]
    report.sample = sample_drawers(palace_path, internal_ids, n=5)
    report.notes.append(
        f"Classifier: wing=paideia, room IN {_MINED_ROOMS}, "
        f"added_by={_MINED_ADDED_BY!r} exact match. "
        f"Excludes claude-s0002-manual (curated content from S-0002 "
        f"era; preserved)."
    )

    if apply and internal_ids:
        uuids = fetch_drawer_uuids(palace_path, internal_ids)
        report.deleted = delete_drawers_by_uuid(palace_path, uuids)
    return report


def audit_orphan_wings(palace_path: Path, *, apply: bool) -> AuditReport:
    """Audit + optionally delete orphan-wing drawers."""
    report = AuditReport(mode="orphan-wings")
    con = open_sqlite_ro(palace_path)
    try:
        pairs = enumerate_orphan_wing_drawers(con)
    finally:
        con.close()

    # Group by wing for the report so the operator sees per-wing counts.
    by_wing: dict[str, list[str]] = {}
    for wing, iid in pairs:
        by_wing.setdefault(wing, []).append(iid)
    report.candidates = [
        {"wing": wing, "drawer_count": len(ids)}
        for wing, ids in sorted(by_wing.items())
    ]
    flat_ids = [iid for _, iid in pairs]
    report.sample = sample_drawers(palace_path, flat_ids, n=5)
    report.notes.append(
        f"Classifier: wing matches {_ORPHAN_WING_RE.pattern!r}; "
        f"excludes {sorted(_CANONICAL_NON_ORPHAN_WINGS)}. "
        f"All drawers in matching wings are deleted (S-0088 plan-time "
        f"verification: 79 drawers across 50+ wings, all "
        f"type=diary_entry, no decision/pushback/lesson markers — "
        f"audit's 'Recommend retire' verdict)."
    )
    report.notes.append(f"Wings affected: {len(by_wing)}; drawers: {len(flat_ids)}.")

    if apply and flat_ids:
        uuids = fetch_drawer_uuids(palace_path, flat_ids)
        report.deleted = delete_drawers_by_uuid(palace_path, uuids)
    return report


def audit_sessions_pollution(palace_path: Path, *, apply: bool) -> AuditReport:
    """Audit + optionally delete sessions-wing transcript-pollution drawers.

    Per ADR 0090 commitment 2b (S-0186 deliverable). The upstream
    ``_ingest_transcript`` hardcodes ``--wing sessions`` on the
    transcript-mining subprocess, so every Stop / PreCompact hook fire
    appends terminal-output capture into ``sessions/<noise-room>``.
    The S-0184 freshness probe found ``mempalace_search`` returning
    these polluted drawers as BM25-fallback top hits, displacing
    curated decision / lesson / pushback content. This audit drains
    that pollution while preserving curated rooms in the same wing.

    The pre-flight ``--backup-dir`` gate is enforced by ``main()``
    before this function is called when ``apply=True``.
    """
    report = AuditReport(mode="sessions-pollution")
    con = open_sqlite_ro(palace_path)
    try:
        internal_ids = enumerate_sessions_pollution_ids(con)
    finally:
        con.close()

    report.candidates = [{"internal_id": iid} for iid in internal_ids]
    report.sample = sample_drawers(palace_path, internal_ids, n=5)
    report.notes.append(
        f"Classifier: wing={_SESSIONS_POLLUTION_WING!r}, "
        f"room IN {_SESSIONS_POLLUTION_ROOMS}. Curated rooms in the same "
        f"wing (decisions/lessons/pushback/diary/operations) are "
        f"preserved by room-whitelist exclusion."
    )
    report.notes.append(
        "Upstream source: mempalace/hooks_cli.py:649-650 hardcodes "
        "--wing sessions on _ingest_transcript. Retire this mode when "
        "upstream PR #1511 (MEMPALACE_WING env-var override) lands and "
        "the hook wrapper wires the override."
    )

    if apply and internal_ids:
        uuids = fetch_drawer_uuids(palace_path, internal_ids)
        report.deleted = delete_drawers_by_uuid(palace_path, uuids)
    return report


def audit_historical_paths(palace_path: Path, *, apply: bool) -> AuditReport:
    """Audit + optionally delete historical full-encoded-path wing drawers.

    When ``apply=False`` (default), report-only enumeration: the
    operator sees per-wing drawer counts and the upstream-bug notice.
    When ``apply=True``, fetches every drawer UUID across all matched
    wings and bulk-deletes via ``collection.delete``. Per the S-0092
    signal probe (engine/docs/audits/historical-wings-signal-probe-
    S-0092.md) the population is uniformly auto-capture residue —
    delete-only; no preservation branch.

    The pre-flight ``--backup-dir`` gate is enforced by ``main()``
    before this function is called when ``apply=True``.
    """
    report = AuditReport(mode="historical-paths")
    con = open_sqlite_ro(palace_path)
    try:
        wings = enumerate_historical_paths(con)
        pairs = enumerate_historical_path_drawer_internal_ids(con)
    finally:
        con.close()
    report.candidates = [{"wing": w, "drawer_count": n} for w, n in wings]
    total = sum(n for _, n in wings)
    flat_ids = [iid for _, iid in pairs]
    if apply:
        report.notes.append(
            f"APPLY MODE: deleting {total} drawer(s) across {len(wings)} "
            f"historical full-encoded-path wing(s). Per the S-0092 signal "
            f"probe at engine/docs/audits/historical-wings-signal-probe-"
            f"S-0092.md, zero preservation candidates in the population."
        )
    else:
        report.notes.append(
            f"Found {len(wings)} historical full-encoded-path wing(s) "
            f"({total} drawer(s) total). Inaccessible to wing-filtered "
            f"queries due to upstream 'wing contains invalid characters' "
            f"validation. Pass --apply with --backup-dir to bulk-delete "
            f"(Issue #41 / S-0092 scope; signal probe verifies zero "
            f"preservation candidates)."
        )
    if apply and flat_ids:
        # Closets and drawers BOTH carry the ``-Users-...`` wing tag, so
        # fan deletes out by collection. ``mempalace_drawers`` accounts
        # for the bulk; ``mempalace_closets`` is the residue cleanup
        # the S-0092 first apply discovered. Any other collection
        # surfaces in the report sheet but is not auto-deleted —
        # operator surfaces it explicitly.
        by_collection = fetch_uuids_by_collection(palace_path, flat_ids)
        for coll_name, coll_uuids in by_collection.items():
            if coll_name in ("mempalace_drawers", "mempalace_closets"):
                report.deleted += delete_drawers_by_uuid(
                    palace_path, coll_uuids, collection=coll_name
                )
            else:
                report.notes.append(
                    f"WARN: {len(coll_uuids)} drawer(s) in unexpected "
                    f"collection {coll_name!r} were NOT deleted; "
                    f"investigate before re-running."
                )
    return report


def format_report(report: AuditReport, *, apply: bool) -> str:
    """Render an AuditReport for human reading on stdout."""
    lines: list[str] = []
    lines.append(f"=== prune_mempalace [{report.mode}] ===")
    if not apply:
        lines.append("MODE: dry-run (no mutations; pass --apply to execute)")
    else:
        lines.append("MODE: apply (mutations performed)")
    lines.append("")
    lines.append(f"candidates: {len(report.candidates)}")
    if report.deleted:
        lines.append(f"deleted: {report.deleted}")
    if report.preserved:
        lines.append(f"preserved: {report.preserved}")

    for note in report.notes:
        lines.append(f"  note: {note}")

    if report.sample:
        lines.append("")
        lines.append(
            f"sample (up to {len(report.sample)} of {len(report.candidates)}):"
        )
        for entry in report.sample:
            lines.append(f"  uuid: {entry['uuid']}")
            lines.append(
                f"    wing={entry.get('wing')} "
                f"room={entry.get('room')} "
                f"added_by={entry.get('added_by')}"
            )
            sf = entry.get("source_file")
            if sf:
                lines.append(f"    source_file: {sf}")
            lines.append(f"    doc[:200]: {entry['doc_preview']!r}")
    elif report.candidates:
        # Per-wing summary for orphan-wings / historical-paths modes.
        lines.append("")
        lines.append("breakdown:")
        for entry in report.candidates[:30]:
            if "wing" in entry and "drawer_count" in entry:
                lines.append(f"  {entry['wing']:60} {entry['drawer_count']:>5} drawers")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prune MemPalace noise floor (mined ops-doc drawers + "
            "orphaned per-worktree wings). Defaults to dry-run; pass "
            "--apply to mutate. Always run --apply with --backup-dir."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--audit-mined-ops-docs",
        action="store_true",
        help="Audit/delete mined ops-doc drawers in paideia/general + paideia/operations.",
    )
    mode.add_argument(
        "--audit-orphan-wings",
        action="store_true",
        help="Audit/delete orphan per-worktree wings (wing_<6-hex>).",
    )
    mode.add_argument(
        "--audit-historical-paths",
        action="store_true",
        help="Audit/delete historical full-encoded-path wing drawers (Issue #41).",
    )
    mode.add_argument(
        "--audit-sessions-pollution",
        action="store_true",
        help=(
            "Audit/delete sessions-wing transcript-mining pollution in noise "
            "rooms (technical/planning/architecture/general/problems). ADR 0090 "
            "commitment 2b. Preserves curated rooms in the same wing."
        ),
    )
    parser.add_argument(
        "--palace",
        help="Palace path override (also MEMPALACE_PROBE_PALACE_PATH env).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute deletions. Default is dry-run.",
    )
    parser.add_argument(
        "--backup-dir",
        help="cp -a backup target. Required when --apply is set.",
    )
    args = parser.parse_args(argv)

    palace_path = resolve_palace_path(args.palace)
    if not palace_path.is_dir():
        print(
            f"[prune_mempalace] palace not found at {palace_path}",
            file=sys.stderr,
        )
        return 3

    is_mutating_mode = (
        args.audit_mined_ops_docs
        or args.audit_orphan_wings
        or args.audit_historical_paths
        or args.audit_sessions_pollution
    )
    if args.apply and is_mutating_mode:
        if not args.backup_dir:
            print(
                "[prune_mempalace] --apply requires --backup-dir for safety; "
                "see ADR 0045 backup discipline.",
                file=sys.stderr,
            )
            return 2
        try:
            backup_palace(palace_path, Path(args.backup_dir))
        except (FileExistsError, FileNotFoundError, OSError) as exc:
            print(
                f"[prune_mempalace] backup failed: {exc}",
                file=sys.stderr,
            )
            return 2
        print(
            f"[prune_mempalace] backup written: {args.backup_dir}",
            file=sys.stderr,
        )

    if args.audit_mined_ops_docs:
        report = audit_mined_ops_docs(palace_path, apply=args.apply)
    elif args.audit_orphan_wings:
        report = audit_orphan_wings(palace_path, apply=args.apply)
    elif args.audit_sessions_pollution:
        report = audit_sessions_pollution(palace_path, apply=args.apply)
    else:
        report = audit_historical_paths(palace_path, apply=args.apply)

    print(format_report(report, apply=args.apply))
    return 0


if __name__ == "__main__":
    sys.exit(main())
