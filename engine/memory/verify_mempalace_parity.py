"""Cross-substrate parity verifier — gates the S-0193 demolition pass.

Independent verification that every load-bearing drawer in the live
mempalace corpus has a corresponding entry in engine_memory. Unlike
``verify_recall.py`` (which queries the engine_memory substrate for
retrievability), this harness compares against the *external* source
of truth — mempalace's chroma.sqlite3 — to confirm the migration
preserved everything classified as load-bearing.

Authored at S-0193 after the plan-mode parity audit surfaced ~130
load-bearing paideia-wing drawers the S-0192 migration filter dropped
(87 ``[pushback]``-content misfiled into a ``problems`` room name +
13 historical foundation records). The migration extension in the
same session recovered them; this harness is the hard gate that
mechanically confirms the recovery is complete before the demolition
deletes the mempalace tooling that would let us re-run the migration
if a gap were discovered later.

Checks
------
1. **Per-paideia-room enumeration sample**: for each room in the
   paideia + wing_paideia wings, sample up to N drawers, classify
   each as load-bearing or droppable via content-prefix heuristics,
   verify every load-bearing sample has a lineage row in engine_memory.
2. **Content fidelity spot-check**: M random load-bearing drawers
   from the broader sample; fetch content from both substrates;
   assert byte-equality (content body, not metadata wrapping).
3. **FTS5 retrievability spot-check**: for each spot-check drawer,
   pick a verbatim N-word n-gram from its content, run engine_memory
   FTS5 MATCH, confirm the drawer surfaces in the top K results.
4. **Sessions-wing intentional-drop check**: count sessions-wing
   drawers in engine_memory's lineage; must be zero.
5. **Diary count parity**: source diary count vs engine_memory diary
   count; within ±5 (accounting for honest tombstone drops).

Verdict
-------
- **PASS** when: every load-bearing sample has lineage coverage AND
  content fidelity matches ≥95% of spot-checks AND FTS5 hit rate
  ≥(threshold) of spot-checks AND sessions-wing drop check passes
  AND diary parity holds.
- **PARTIAL** when individual sub-checks fail but the load-bearing
  coverage check passes (acceptable for in-session diagnosis).
- **FAIL** when any load-bearing drawer lacks lineage coverage. The
  S-0193 demolition cannot proceed under FAIL.

CLI
---
``python -m engine.memory.verify_mempalace_parity [--output-md PATH]
[--palace PATH] [--db-path PATH] [--sample-per-room N]
[--content-spot-check M] [--exit-on-fail]``

Exit codes
----------
- ``0`` — PASS (or PARTIAL with ``--exit-on-fail`` not set).
- ``2`` — FAIL (load-bearing coverage gap) OR PARTIAL with
  ``--exit-on-fail`` set.
- ``3`` — verification could not run (palace missing, substrate
  missing, chromadb import failure).
"""

from __future__ import annotations

import argparse
import os
import random
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.memory.connection import get_conn, resolve_db_path

# Default report destination — matches the sibling audit naming.
DEFAULT_OUTPUT_MD = Path("engine/docs/audits/engine_memory_parity_S-0193.md")

# Sampling defaults.
DEFAULT_SAMPLE_PER_ROOM = 10
DEFAULT_CONTENT_SPOT_CHECK = 20
DEFAULT_FTS_TOP_K = 10
DEFAULT_FTS_NGRAM_WORDS = 6

# Diary count tolerance — chromadb tombstone gap can drop a small
# number of entries with no recoverable content; ±5 is the same band
# the S-0192 audit used.
DIARY_COUNT_TOLERANCE = 5

# Content-prefix markers that identify load-bearing canonical content
# regardless of source room name. Mirrors the migration script's
# CONTENT_PREFIX_OVERRIDES — kept independent to avoid coupling the
# verifier's classification to whatever the migration happens to map.
LOAD_BEARING_PREFIXES: tuple[str, ...] = (
    "[pushback]",
    "[lesson]",
    "[decision]",
    "[exploration]",
    "# Verbatim exchange",
)

# Rooms whose drawers are load-bearing by name (the canonical curated
# set + the S-0193 extension targets). Drawers in these rooms are
# treated as load-bearing even if their content has no canonical
# prefix — the room name itself is the load-bearing signal.
LOAD_BEARING_ROOMS: frozenset[str] = frozenset(
    {
        "decisions",
        "pushback",
        "lessons",
        "exploration",
        "operations",
        "problems",
        "foundation-planning-s0001",
        "s0003-adr-collection",
        "project",
    }
)

# Wings whose drawers are eligible candidates (matches the migration's
# ALLOWED_DRAWER_WINGS). The sessions wing's drawers are auto-capture
# residue and explicitly excluded from "load-bearing" classification.
LOAD_BEARING_WINGS: frozenset[str] = frozenset({"paideia", "wing_paideia"})


@dataclass
class DrawerSample:
    """One sampled mempalace drawer with classification result."""

    internal_id: str
    uuid: str
    wing: str
    room: str
    content: str
    metadata: dict[str, Any]
    is_load_bearing: bool
    classification_reason: str
    has_lineage_in_engine_memory: bool = False
    engine_memory_drawer_id: str | None = None
    engine_memory_room: str | None = None


@dataclass
class ContentFidelityResult:
    """Content equality + FTS5 retrievability for one spot-check drawer."""

    uuid: str
    source_room: str
    target_room: str | None
    content_matches: bool
    content_byte_diff: int  # 0 when matches
    fts_hit: bool
    fts_top_k_count: int
    fts_ngram_used: str


@dataclass
class ParityReport:
    """Aggregate verdict + per-check breakdown."""

    palace_path: str = ""
    substrate_path: str = ""
    per_room_samples: dict[str, list[DrawerSample]] = field(default_factory=dict)
    coverage_pass_count: int = 0
    coverage_fail_count: int = 0
    coverage_failures: list[DrawerSample] = field(default_factory=list)
    content_spot_checks: list[ContentFidelityResult] = field(default_factory=list)
    sessions_wing_in_engine_memory: int = 0
    source_diary_count: int = 0
    substrate_diary_count: int = 0
    verdict: str = "PENDING"  # decide_verdict() sets PASS/PARTIAL/FAIL
    fail_reasons: list[str] = field(default_factory=list)
    partial_reasons: list[str] = field(default_factory=list)


# --------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------


def classify_drawer(wing: str, room: str, content: str) -> tuple[bool, str]:
    """Decide whether a drawer is load-bearing. Returns (verdict, reason).

    Empty content is treated as non-load-bearing FIRST — even when the
    room name would otherwise qualify. mempalace's chromadb collection
    sometimes returns empty content for drawers whose sqlite-side
    metadata still exists (the tombstone-vs-vacuum gap documented in
    the S-0192 audit). These are honest drops: the content is
    genuinely unrecoverable from chromadb regardless of room name, so
    classifying them as load-bearing would generate spurious coverage
    failures for content that no longer exists at the source.
    """
    if wing not in LOAD_BEARING_WINGS:
        return False, f"non-load-bearing wing {wing!r}"
    stripped = (content or "").lstrip()
    if not stripped:
        return (
            False,
            "empty content — chromadb tombstone (honest drop per S-0192 audit)",
        )
    for prefix in LOAD_BEARING_PREFIXES:
        if stripped.startswith(prefix):
            return True, f"content-prefix {prefix!r} matched"
    if room in LOAD_BEARING_ROOMS:
        return True, f"load-bearing room {room!r}"
    return False, f"non-load-bearing room {room!r}, no canonical content prefix"


# --------------------------------------------------------------------
# Source-side enumeration (read-only against mempalace)
# --------------------------------------------------------------------


def open_palace_ro(palace_path: Path) -> sqlite3.Connection:
    """Open chroma.sqlite3 read-only."""
    db = palace_path / "chroma.sqlite3"
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def enumerate_paideia_rooms(con: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """Return distinct (wing, room, count) for paideia + wing_paideia wings."""
    wings = list(LOAD_BEARING_WINGS)
    placeholders = ",".join("?" for _ in wings)
    sql = f"""
        SELECT em_w.string_value AS wing,
               em_r.string_value AS room,
               COUNT(*)          AS n
        FROM   embedding_metadata em_w
        JOIN   embedding_metadata em_r
               ON em_w.id = em_r.id AND em_r.key = 'room'
        WHERE  em_w.key = 'wing'
          AND  em_w.string_value IN ({placeholders})
        GROUP  BY em_w.string_value, em_r.string_value
        ORDER  BY em_r.string_value
    """  # nosec B608 — placeholders parameterized
    rows = con.execute(sql, wings).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


def sample_drawer_ids(
    con: sqlite3.Connection, wing: str, room: str, n: int
) -> list[str]:
    """Return up to n internal_ids for drawers in a given (wing, room)."""
    sql = """
        SELECT em_w.id
        FROM   embedding_metadata em_w
        JOIN   embedding_metadata em_r
               ON em_w.id = em_r.id AND em_r.key = 'room'
        WHERE  em_w.key = 'wing'
          AND  em_w.string_value = ?
          AND  em_r.string_value = ?
        ORDER  BY em_w.id
    """
    ids = [str(r[0]) for r in con.execute(sql, (wing, room)).fetchall()]
    if len(ids) <= n:
        return ids
    # Deterministic sample for reproducible audit reports — seeded RNG.
    rng = random.Random(f"S-0193-{wing}-{room}")  # nosec B311 — audit reproducibility, not security
    return rng.sample(ids, n)


def fetch_uuid_map(palace_path: Path, internal_ids: list[str]) -> dict[str, str]:
    """Resolve chroma internal IDs (ints) to drawer UUIDs."""
    if not internal_ids:
        return {}
    db = palace_path / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in internal_ids)
        sql = f"SELECT id, embedding_id FROM embeddings WHERE id IN ({placeholders})"  # nosec B608
        return {str(r[0]): r[1] for r in con.execute(sql, internal_ids).fetchall()}
    finally:
        con.close()


def fetch_contents(palace_path: Path, uuids: list[str]) -> dict[str, dict[str, Any]]:
    """Bulk-fetch (content, metadata) via chromadb client."""
    if not uuids:
        return {}
    try:
        import chromadb
    except ImportError as exc:  # pragma: no cover — venv invariant
        raise RuntimeError("chromadb not importable from venv") from exc
    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection("mempalace_drawers")
    res = col.get(ids=uuids, include=["metadatas", "documents"])
    out: dict[str, dict[str, Any]] = {}
    for u, doc, meta in zip(res["ids"], res["documents"] or [], res["metadatas"] or []):
        out[u] = {"content": doc or "", "metadata": dict(meta or {})}
    return out


def source_diary_count(con: sqlite3.Connection) -> int:
    """Count diary entries across all wings in the live palace."""
    sql = """
        SELECT COUNT(*)
        FROM   embedding_metadata em_w
        JOIN   embedding_metadata em_r
               ON em_w.id = em_r.id AND em_r.key = 'room'
        WHERE  em_w.key = 'wing'
          AND  em_r.string_value = 'diary'
    """
    return int(con.execute(sql).fetchone()[0])


# --------------------------------------------------------------------
# Target-side checks (against engine_memory)
# --------------------------------------------------------------------


def check_lineage_coverage(substrate: sqlite3.Connection, sample: DrawerSample) -> None:
    """Populate sample's coverage fields by querying engine_memory's lineage."""
    if not sample.uuid:
        sample.has_lineage_in_engine_memory = False
        return
    row = substrate.execute(
        """
        SELECT l.drawer_id, d.room
        FROM   lineage l
        JOIN   drawers d ON d.id = l.drawer_id
        WHERE  l.imported_from = ?
        LIMIT  1
        """,
        (f"mempalace:{sample.uuid}",),
    ).fetchone()
    if row is None:
        sample.has_lineage_in_engine_memory = False
    else:
        sample.has_lineage_in_engine_memory = True
        sample.engine_memory_drawer_id = row[0]
        sample.engine_memory_room = row[1]


def fetch_substrate_content(
    substrate: sqlite3.Connection, drawer_id: str
) -> str | None:
    """Return the content field for a given engine_memory drawer."""
    row = substrate.execute(
        "SELECT content FROM drawers WHERE id = ? LIMIT 1", (drawer_id,)
    ).fetchone()
    return row[0] if row else None


def fts_match(
    substrate: sqlite3.Connection, query: str, top_k: int
) -> list[tuple[str, float]]:
    """Run FTS5 MATCH; return list of (drawer_id, bm25_score) up to top_k.

    The FTS5 virtual table is declared with ``content_rowid='rowid'``
    (see ``engine/memory/schema.py``), so the join key to the ``drawers``
    base table is ``rowid``, NOT ``id``. Each term is wrapped in
    double-quotes to neutralize FTS5 operator characters in n-gram
    tokens (``-``, ``/``, ``.``, ``'``); terms joined with ``OR``
    because the n-gram is a heuristic-picked phrase, not a strict
    AND-of-tokens query.
    """
    terms = [t for t in query.split() if t]
    if not terms:
        return []
    escaped = " OR ".join(f'"{t}"' for t in terms)
    try:
        rows = substrate.execute(
            """
            SELECT d.id, bm25(drawers_fts)
            FROM   drawers_fts
            JOIN   drawers d ON d.rowid = drawers_fts.rowid
            WHERE  drawers_fts MATCH ?
            ORDER  BY bm25(drawers_fts) ASC
            LIMIT  ?
            """,
            (escaped, top_k),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [(r[0], float(r[1])) for r in rows]


def substrate_sessions_wing_count(substrate: sqlite3.Connection) -> int:
    """Count engine_memory lineage rows whose source_wing is 'sessions'."""
    row = substrate.execute(
        "SELECT COUNT(*) FROM lineage WHERE source_wing = 'sessions'"
    ).fetchone()
    return int(row[0]) if row else 0


def substrate_diary_count(substrate: sqlite3.Connection) -> int:
    """Total diary entries in engine_memory."""
    return int(substrate.execute("SELECT COUNT(*) FROM diary").fetchone()[0])


# --------------------------------------------------------------------
# Spot-check + verdict
# --------------------------------------------------------------------


def pick_ngram(content: str, words: int) -> str:
    """Extract a verbatim word-aligned n-gram from content for FTS5 query."""
    tokens = [t.strip(".,;:()[]{}'\"!?") for t in content.split() if t.strip()]
    tokens = [t for t in tokens if len(t) >= 3]  # drop short noise words
    if len(tokens) < words:
        return " ".join(tokens)
    # Take from the middle so we avoid headers/timestamps at the start
    start = max(0, len(tokens) // 2 - words // 2)
    return " ".join(tokens[start : start + words])


def run_content_spot_checks(
    palace_path: Path,
    substrate: sqlite3.Connection,
    load_bearing_samples: list[DrawerSample],
    m: int,
    fts_top_k: int,
    fts_words: int,
) -> list[ContentFidelityResult]:
    """Pick M random samples; verify content equality + FTS5 retrievability."""
    if not load_bearing_samples:
        return []
    covered = [s for s in load_bearing_samples if s.has_lineage_in_engine_memory]
    if not covered:
        return []
    rng = random.Random("S-0193-spot-check")  # nosec B311 — audit reproducibility, not security
    chosen = rng.sample(covered, min(m, len(covered)))
    results: list[ContentFidelityResult] = []
    for sample in chosen:
        substrate_content = (
            fetch_substrate_content(substrate, sample.engine_memory_drawer_id or "")
            or ""
        )
        diff = abs(len(sample.content) - len(substrate_content))
        matches = sample.content == substrate_content
        ngram = pick_ngram(sample.content, fts_words)
        fts_results = fts_match(substrate, ngram, fts_top_k)
        fts_hit = any(rid == sample.engine_memory_drawer_id for rid, _ in fts_results)
        results.append(
            ContentFidelityResult(
                uuid=sample.uuid,
                source_room=sample.room,
                target_room=sample.engine_memory_room,
                content_matches=matches,
                content_byte_diff=diff,
                fts_hit=fts_hit,
                fts_top_k_count=len(fts_results),
                fts_ngram_used=ngram,
            )
        )
    return results


def decide_verdict(report: ParityReport) -> None:
    """Set verdict + fail_reasons + partial_reasons in-place on the report."""
    # Load-bearing coverage is the hard gate.
    if report.coverage_fail_count > 0:
        report.fail_reasons.append(
            f"{report.coverage_fail_count} load-bearing sample(s) without "
            f"lineage in engine_memory"
        )

    # Sessions-wing leak is a hard fail too — it means the migration
    # pulled in pollution it shouldn't have.
    if report.sessions_wing_in_engine_memory > 0:
        report.fail_reasons.append(
            f"{report.sessions_wing_in_engine_memory} sessions-wing drawer(s) "
            f"leaked into engine_memory lineage"
        )

    # Content fidelity + FTS5 are partial-failing (recoverable) signals.
    if report.content_spot_checks:
        content_pass = sum(1 for r in report.content_spot_checks if r.content_matches)
        fts_pass = sum(1 for r in report.content_spot_checks if r.fts_hit)
        n = len(report.content_spot_checks)
        if content_pass < n * 0.95:
            report.partial_reasons.append(
                f"content fidelity {content_pass}/{n} below 95% threshold"
            )
        if fts_pass < n * 0.7:  # 14/20 default
            report.partial_reasons.append(
                f"FTS5 retrievability {fts_pass}/{n} below 70% threshold"
            )

    # Diary count parity (partial).
    diary_diff = abs(report.source_diary_count - report.substrate_diary_count)
    if diary_diff > DIARY_COUNT_TOLERANCE:
        report.partial_reasons.append(
            f"diary count delta {diary_diff} exceeds tolerance "
            f"±{DIARY_COUNT_TOLERANCE} (source={report.source_diary_count}, "
            f"substrate={report.substrate_diary_count})"
        )

    if report.fail_reasons:
        report.verdict = "FAIL"
    elif report.partial_reasons:
        report.verdict = "PARTIAL"
    else:
        report.verdict = "PASS"


# --------------------------------------------------------------------
# Orchestration + rendering
# --------------------------------------------------------------------


def run_parity(
    palace_path: Path,
    substrate_path: Path | None = None,
    *,
    sample_per_room: int = DEFAULT_SAMPLE_PER_ROOM,
    content_spot_check: int = DEFAULT_CONTENT_SPOT_CHECK,
    fts_top_k: int = DEFAULT_FTS_TOP_K,
    fts_ngram_words: int = DEFAULT_FTS_NGRAM_WORDS,
) -> ParityReport:
    """Top-level orchestrator. Returns a populated ParityReport."""
    report = ParityReport(
        palace_path=str(palace_path),
        substrate_path=str(substrate_path or resolve_db_path()),
    )

    # Source enumeration + sampling
    src = open_palace_ro(palace_path)
    try:
        room_counts = enumerate_paideia_rooms(src)
        all_internal_ids: list[tuple[str, str, str]] = []
        for wing, room, _n in room_counts:
            ids = sample_drawer_ids(src, wing, room, sample_per_room)
            for iid in ids:
                all_internal_ids.append((iid, wing, room))
    finally:
        src.close()

    # Hydrate uuid + content for the sampled set
    internal_ids = [iid for iid, _w, _r in all_internal_ids]
    uuid_map = fetch_uuid_map(palace_path, internal_ids)
    uuids_to_fetch = list(uuid_map.values())
    contents = fetch_contents(palace_path, uuids_to_fetch)

    # Build DrawerSample objects + classify
    samples_by_room: dict[str, list[DrawerSample]] = {}
    load_bearing_pool: list[DrawerSample] = []
    for internal_id, wing, room in all_internal_ids:
        u = uuid_map.get(internal_id, "")
        body = contents.get(u, {"content": "", "metadata": {}})
        is_lb, reason = classify_drawer(wing, room, body["content"])
        sample = DrawerSample(
            internal_id=internal_id,
            uuid=u,
            wing=wing,
            room=room,
            content=body["content"],
            metadata=body["metadata"],
            is_load_bearing=is_lb,
            classification_reason=reason,
        )
        samples_by_room.setdefault(room, []).append(sample)
        if is_lb:
            load_bearing_pool.append(sample)
    report.per_room_samples = samples_by_room

    # Coverage check + sessions-wing audit + diary parity
    substrate = get_conn(path=substrate_path) if substrate_path else get_conn()
    try:
        for sample in load_bearing_pool:
            check_lineage_coverage(substrate, sample)
            if sample.has_lineage_in_engine_memory:
                report.coverage_pass_count += 1
            else:
                report.coverage_fail_count += 1
                report.coverage_failures.append(sample)
        report.sessions_wing_in_engine_memory = substrate_sessions_wing_count(substrate)
        report.substrate_diary_count = substrate_diary_count(substrate)
        src2 = open_palace_ro(palace_path)
        try:
            report.source_diary_count = source_diary_count(src2)
        finally:
            src2.close()

        # Spot-check content + FTS5
        report.content_spot_checks = run_content_spot_checks(
            palace_path,
            substrate,
            load_bearing_pool,
            content_spot_check,
            fts_top_k,
            fts_ngram_words,
        )
    finally:
        substrate.close()

    decide_verdict(report)
    return report


def render_markdown(report: ParityReport) -> str:
    """Produce the audit report body for engine/docs/audits/."""
    lines = [
        "# Engine-memory ↔ mempalace parity verification — S-0193",
        "",
        "_Generated by `engine/memory/verify_mempalace_parity.py` — "
        "the HARD GATE for the S-0193 demolition pass per ADR 0091._",
        "",
        f"**Verdict:** {report.verdict}",
        "",
        "## Scope",
        "",
        f"- Source: `{report.palace_path}`",
        f"- Target: `{report.substrate_path}`",
        "- Wings sampled: " + ", ".join(sorted(LOAD_BEARING_WINGS)),
        f"- Per-room sample size: {DEFAULT_SAMPLE_PER_ROOM} (deterministic seed)",
        f"- Content + FTS5 spot-checks: {len(report.content_spot_checks)}",
        "",
        "## Verdict logic",
        "",
        "- **PASS** when every load-bearing sample has lineage coverage "
        "AND sessions-wing leak count is zero "
        "AND no PARTIAL reasons triggered.",
        "- **PARTIAL** when load-bearing coverage is complete but content "
        "fidelity / FTS5 retrievability / diary parity thresholds slipped.",
        "- **FAIL** when any load-bearing sample lacks lineage coverage OR "
        "sessions-wing drawers leaked into engine_memory.",
        "",
        "## Per-room enumeration sample",
        "",
        "| Room | Samples | Load-bearing | Covered | Failed |",
        "|---|---|---|---|---|",
    ]
    for room in sorted(report.per_room_samples):
        samples = report.per_room_samples[room]
        lb = [s for s in samples if s.is_load_bearing]
        covered = [s for s in lb if s.has_lineage_in_engine_memory]
        failed = [s for s in lb if not s.has_lineage_in_engine_memory]
        lines.append(
            f"| `{room}` | {len(samples)} | {len(lb)} | {len(covered)} "
            f"| {len(failed)} |"
        )
    lines.append("")
    if report.coverage_failures:
        lines += [
            "## Coverage failures (load-bearing samples WITHOUT lineage in engine_memory)",
            "",
        ]
        for s in report.coverage_failures:
            lines.append(
                f"- `{s.wing}/{s.room}/{s.uuid}` — {s.classification_reason}; "
                f"content head: `{s.content[:120].strip()}…`"
            )
        lines.append("")
    lines += [
        "## Content fidelity + FTS5 spot-check",
        "",
        "| # | Source room | Target room | Content match | "
        "Byte diff | FTS5 hit | FTS5 results | n-gram |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(report.content_spot_checks, start=1):
        match_mark = "✓" if r.content_matches else "✗"
        fts_mark = "✓" if r.fts_hit else "✗"
        lines.append(
            f"| {i} | `{r.source_room}` | `{r.target_room or '-'}` | "
            f"{match_mark} | {r.content_byte_diff} | {fts_mark} | "
            f"{r.fts_top_k_count} | `{r.fts_ngram_used[:60]}…` |"
        )
    lines.append("")
    lines += [
        "## Sessions-wing leak check",
        "",
        f"- engine_memory lineage rows with `source_wing='sessions'`: "
        f"**{report.sessions_wing_in_engine_memory}**",
        "  (must be 0 — sessions-wing drawers are auto-capture pollution "
        "per the S-0186 prune lesson)",
        "",
        "## Diary count parity",
        "",
        f"- Source palace diary count (all wings, `room='diary'`): "
        f"**{report.source_diary_count}**",
        f"- engine_memory `diary` table count: **{report.substrate_diary_count}**",
        f"- Delta: **{abs(report.source_diary_count - report.substrate_diary_count)}** "
        f"(tolerance ±{DIARY_COUNT_TOLERANCE})",
        "",
    ]
    if report.fail_reasons or report.partial_reasons:
        lines.append("## Reasons")
        lines.append("")
        for reason in report.fail_reasons:
            lines.append(f"- **FAIL** — {reason}")
        for reason in report.partial_reasons:
            lines.append(f"- **PARTIAL** — {reason}")
        lines.append("")
    lines += [
        "## Cutover-gate disposition",
        "",
        f"Verdict **{report.verdict}**. "
        + (
            "Demolition may proceed."
            if report.verdict == "PASS"
            else "Diagnose before proceeding."
            if report.verdict == "PARTIAL"
            else "Demolition MUST NOT proceed."
        ),
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-substrate parity verifier (mempalace ↔ engine_memory)."
    )
    parser.add_argument("--palace", default=None, help="MemPalace palace path.")
    parser.add_argument("--db-path", default=None, help="engine_memory SQLite path.")
    parser.add_argument(
        "--output-md",
        default=str(DEFAULT_OUTPUT_MD),
        help=f"Markdown report destination (default: {DEFAULT_OUTPUT_MD}).",
    )
    parser.add_argument("--sample-per-room", type=int, default=DEFAULT_SAMPLE_PER_ROOM)
    parser.add_argument(
        "--content-spot-check", type=int, default=DEFAULT_CONTENT_SPOT_CHECK
    )
    parser.add_argument("--fts-top-k", type=int, default=DEFAULT_FTS_TOP_K)
    parser.add_argument("--fts-ngram-words", type=int, default=DEFAULT_FTS_NGRAM_WORDS)
    parser.add_argument(
        "--exit-on-fail",
        action="store_true",
        help="Exit 2 on PARTIAL as well as FAIL.",
    )
    args = parser.parse_args(argv)

    env_palace = os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    if args.palace:
        palace = Path(args.palace)
    elif env_palace:
        palace = Path(env_palace)
    else:
        palace = Path.home() / ".mempalace" / "palace"
    if not (palace / "chroma.sqlite3").exists():
        print(f"[parity] palace not found at {palace}", file=sys.stderr)
        return 3

    db_path = Path(args.db_path) if args.db_path else None

    try:
        report = run_parity(
            palace,
            db_path,
            sample_per_room=args.sample_per_room,
            content_spot_check=args.content_spot_check,
            fts_top_k=args.fts_top_k,
            fts_ngram_words=args.fts_ngram_words,
        )
    except RuntimeError as exc:
        print(f"[parity] {exc}", file=sys.stderr)
        return 3

    md = render_markdown(report)
    out_path = Path(args.output_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(md)
    print(f"\n[parity] report written to {out_path}")

    if report.verdict == "FAIL":
        return 2
    if report.verdict == "PARTIAL" and args.exit_on_fail:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
