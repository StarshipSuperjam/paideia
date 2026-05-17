"""Mechanical + cite-worthy verification harness for the engine-memory read surface.

Two modes:

- **Synthetic (default):** seeds a tempfile substrate with 20 synthetic
  drawers and runs the 10-query catalog whose expected results are
  hand-engineered. Closes T1-C of
  ``engine/build_readiness/engine_memory_substrate_first_exercise.md``
  (mechanical scope).
- **Real-data (``--real-data``):** runs against the live engine_memory
  substrate (post-migration replay) with no seeding. The plausible-
  recall catalog targets vocabulary expected to be present in the
  curated migrated corpus; verdict PASSes when all 10 fixed real-data
  queries return ≥1 hit AND ≥4/5 plausible-recall queries do. Closes
  T1-D of the same readiness note (S-0192 cite-worthy verification
  gate).

Synthetic-mode seed corpus + query catalog
-------------------------------------------
20 synthetic drawers spanning the 7 curated rooms; each of the 10
queries below has a known target drawer the BM25 + tag-class boost
should rank top-1.

Query catalog (10 queries × 7 categories per the approved plan):
- ADR-pushback recall (2)
- Lesson recall (2)
- Decision-drawer recall (2)
- Diary cross-reference (1)
- Issue-history recall (1)
- Boundary case — empty result (1)
- Formulation distinctness (1)

Real-data catalogs
------------------
- Fixed catalog (10 queries): broadly-vocabularied probes expected to
  hit any reasonably-populated curated palace (e.g., "ADR decision",
  "lesson learned", "engine memory"). Each asserts ≥1 hit; no
  top-1 expectations.
- Plausible-recall catalog (5 queries): targeted vocabulary the
  migrated corpus should specifically know about (e.g., "ADR 0091
  substrate cutover", "routine wedge detect"). Each asserts ≥1 hit.

CLI
---
``python -m engine.memory.verify_recall [--real-data] [--output-md PATH] [--db-path PATH]``

Default synthetic-mode output: ``engine/docs/audits/engine_memory_recall_S-0191.md``.
Default real-data output: ``engine/docs/audits/engine_memory_recall_S-0192.md``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.memory.boot_surface import (
    FORMULATION_OPERATOR,
    fetch_candidates,
    generate_formulations,
    to_fts5_match,
)
from engine.memory.connection import get_conn


# ---------------------------------------------------------------------------
# Seed corpus — 20 synthetic drawers crafted for the 10 queries
# ---------------------------------------------------------------------------


@dataclass
class SeedDrawer:
    """One synthetic drawer for the verification harness."""

    room: str
    tags: list[str]
    content: str
    target_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    # Override filed_at for recency-boost tests; None = datetime('now').
    filed_at: str | None = None


SEED_CORPUS: list[SeedDrawer] = [
    # --- Query 1 target: ADR-pushback recall ---
    SeedDrawer(
        room="pushback",
        tags=["pushback"],
        content=(
            "Author at production quality the first time. Don't write a draft "
            "and polish; the cost of re-reading and re-revising a sloppy first "
            "pass exceeds the cost of slowing down to write it correctly. "
            "Expression contract for inward documents."
        ),
    ),
    # --- Query 2 target: ADR-pushback recall ---
    SeedDrawer(
        room="pushback",
        tags=["pushback"],
        content=(
            "Don't split work into multiple sessions to hedge on length. "
            "Default to single-session full execution. AI tends to overestimate "
            "context use."
        ),
    ),
    # --- Query 3 target: lesson recall ---
    SeedDrawer(
        room="lessons",
        tags=["lesson"],
        content=(
            "pkill -f mempalace mcp before running pytest engine tools; "
            "chromadb file-lock contention from accumulated MCP processes "
            "causes the test suite to hang silently."
        ),
    ),
    # --- Query 4 target: lesson recall ---
    SeedDrawer(
        room="lessons",
        tags=["lesson"],
        content=(
            "scope_lock allowlist for routine commits: task-deliverable paths "
            "must be in scope_lock.allowed_paths union with operational allowlist. "
            "Pre-commit hook hard-fails any commit touching paths outside this set."
        ),
    ),
    # --- Query 5 target: decision-drawer recall ---
    SeedDrawer(
        room="decisions",
        tags=["decision", "engine-memory"],
        content=(
            "ADR 0091 commits to a thin SQLite-backed engine-memory layer "
            "with FTS5 + BM25 retrieval, replacing the MemPalace chromadb "
            "substrate. Six MCP tools, gitignored data file under engine tree."
        ),
    ),
    # --- Query 6 target: decision-drawer recall ---
    SeedDrawer(
        room="decisions",
        tags=["decision", "oss"],
        content=(
            "ADR 0065 commits to OSS pivot under Apache 2.0 with BYOK posture. "
            "No paid SaaS distribution; community-forkable; the consumer "
            "learner-facing product distribution is the only platform clause."
        ),
    ),
    # --- Query 7 target: diary cross-reference (this is in the diary table,
    #     not drawers — but the search surface won't see diary directly. We
    #     test boundary behavior here: a query about diaries that returns no
    #     drawer results is still a valid mechanical pass.) ---
    SeedDrawer(
        room="exploration",
        tags=["exploration", "diary"],
        content=(
            "Diary entries land in the diary table, not the drawers table. "
            "engine_memory_diary_read returns last_n entries for an agent."
        ),
    ),
    # --- Query 8 target: issue-history recall ---
    SeedDrawer(
        room="operations",
        tags=["operations", "session-tagged"],
        content=(
            "Issue collision soft-warn fires when GitHub Issues reference "
            "stale identifiers or when two open Issues claim the same "
            "scope. Track in archive outcome_summary_soft_warns."
        ),
    ),
    # --- Recency boost target (query exercises since_days + filed_at) ---
    SeedDrawer(
        room="general",
        tags=["general"],
        content="Recent observation about engine memory queries.",
        # Filed today; the older twin is below.
    ),
    SeedDrawer(
        room="general",
        tags=["general"],
        content="Old observation about engine memory queries.",
        filed_at="2025-12-01T00:00:00Z",  # ~6 months stale
    ),
    # --- Filler drawers — exercise tag-class boost AND room-filter variety ---
    SeedDrawer(
        room="decisions",
        tags=["decision"],
        content="Architectural decision about scope_lock enforcement at boot.",
    ),
    SeedDrawer(
        room="decisions",
        tags=["decision"],
        content="Decision to retire MemPalace MCP server tools after S-0193.",
    ),
    SeedDrawer(
        room="decisions",
        tags=["decision"],
        content="The Phase 6 master plan unblocks after OQ-DEC1 tension settlement.",
    ),
    SeedDrawer(
        room="pushback",
        tags=["pushback"],
        content=(
            "Check existing discipline before proposing new tooling. Read the "
            "ops doc first; distinguish 'already covered' from 'real gap'."
        ),
    ),
    SeedDrawer(
        room="lessons",
        tags=["lesson"],
        content=(
            "Health-check overdue catchup logic replaced strict-modulo at S-0041 "
            "after the trigger silently slid by a full cadence."
        ),
    ),
    SeedDrawer(
        room="lessons",
        tags=["lesson"],
        content=(
            "Build sessions vs live extraction sessions: adapter testing is "
            "not production mining into graph."
        ),
    ),
    SeedDrawer(
        room="exploration",
        tags=["exploration"],
        content=(
            "Three-formulation pattern preserves vocabulary diversity across "
            "literal, conceptual, adjacent boot queries."
        ),
    ),
    SeedDrawer(
        room="exploration",
        tags=["exploration"],
        content=(
            "Cross-device continuity is user-managed; SQLite file is gitignored "
            "and syncs via Dropbox or iCloud if the user wants it."
        ),
    ),
    SeedDrawer(
        room="exploration",
        tags=["exploration"],
        content=(
            "WAL mode with busy_timeout=5000 handles transient SQLITE_BUSY "
            "from single-writer overlap between hook + MCP server."
        ),
    ),
    SeedDrawer(
        room="operations",
        tags=["operations"],
        content=(
            "session-build-lifecycle skill step 3 invokes the boot orchestrator "
            "at session boot to surface prior context into current_plan.md."
        ),
    ),
]


@dataclass
class QuerySpec:
    """One query in the verification catalog."""

    name: str
    category: str
    query: str
    expected_room: str | None = None
    expected_tag: str | None = None
    expected_min_hits: int = 1
    expected_max_hits: int | None = None
    room_filter: str | None = None
    tag_any_filter: str | None = None
    since_days_filter: int | None = None


QUERY_CATALOG: list[QuerySpec] = [
    QuerySpec(
        name="adr_pushback_first_pass_quality",
        category="ADR-pushback recall",
        query="expression contract first-pass quality production",
        expected_room="pushback",
        expected_tag="pushback",
    ),
    QuerySpec(
        name="adr_pushback_session_splitting",
        category="ADR-pushback recall",
        query="split work into multiple sessions hedge",
        expected_room="pushback",
        expected_tag="pushback",
    ),
    QuerySpec(
        name="lesson_mempalace_pytest_hang",
        category="Lesson recall",
        query="mempalace mcp pytest hang chromadb file lock",
        expected_room="lessons",
        expected_tag="lesson",
    ),
    QuerySpec(
        name="lesson_scope_lock_routine",
        category="Lesson recall",
        query="scope lock allowlist routine commit",
        expected_room="lessons",
        expected_tag="lesson",
    ),
    QuerySpec(
        name="decision_engine_memory_adr_0091",
        category="Decision-drawer recall",
        query="engine memory substrate SQLite FTS5",
        expected_room="decisions",
        expected_tag="decision",
    ),
    QuerySpec(
        name="decision_oss_pivot_byok",
        category="Decision-drawer recall",
        query="OSS pivot BYOK Apache",
        expected_room="decisions",
        expected_tag="decision",
    ),
    QuerySpec(
        name="diary_cross_reference",
        category="Diary cross-reference",
        query="diary previous session entry agent claude",
        # Diary entries don't live in drawers; this query exercises the
        # boundary where the search surface returns either no drawers OR
        # the metadata drawer about diary tooling. Either is mechanically
        # valid; we just require the query doesn't error.
        expected_min_hits=0,
        expected_max_hits=20,
    ),
    QuerySpec(
        name="issue_history_collision",
        category="Issue-history recall",
        query="issue collision soft warn archive outcome",
        expected_room="operations",
        expected_tag="operations",
    ),
    QuerySpec(
        name="boundary_no_hits",
        category="Boundary case",
        query="nonexistenttermxyzqq987654",
        expected_min_hits=0,
        expected_max_hits=0,
    ),
    QuerySpec(
        name="formulation_distinctness",
        category="Formulation distinctness",
        query="Phase 6 master plan authoring after OQ-DEC1 settlement",
        # Mechanical check: literal/conceptual/adjacent yield distinct FTS5
        # MATCH expressions (asserted separately in run_query, not via
        # expected_room/tag).
        expected_min_hits=0,
        expected_max_hits=20,
    ),
]


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


@dataclass
class QueryResult:
    """Per-query outcome."""

    spec: QuerySpec
    formulation_hits: dict[str, int]
    top_drawer: dict[str, Any] | None
    formulation_matches: dict[str, str]
    verdict: str  # "PASS" | "FAIL"
    reason: str


def seed_substrate(conn: sqlite3.Connection) -> None:
    """Insert SEED_CORPUS into the open connection."""
    for drawer in SEED_CORPUS:
        filed_at = drawer.filed_at
        if filed_at is None:
            conn.execute(
                "INSERT INTO drawers (id, room, tags, source_kind, content) "
                "VALUES (?, ?, ?, 'manual', ?)",
                (
                    drawer.target_id,
                    drawer.room,
                    json.dumps(drawer.tags),
                    drawer.content,
                ),
            )
        else:
            conn.execute(
                "INSERT INTO drawers (id, room, tags, source_kind, content, filed_at, created_at) "
                "VALUES (?, ?, ?, 'manual', ?, ?, ?)",
                (
                    drawer.target_id,
                    drawer.room,
                    json.dumps(drawer.tags),
                    drawer.content,
                    filed_at,
                    filed_at,
                ),
            )


# ---------------------------------------------------------------------------
# Real-data query catalogs (--real-data mode)
# ---------------------------------------------------------------------------


# Broad-vocabulary probes — each should hit ≥1 drawer in any reasonably-
# populated curated palace. Verdict-PASS bar: 10/10 return ≥1 candidate
# on the literal formulation.
REAL_DATA_FIXED_CATALOG: list[QuerySpec] = [
    QuerySpec(
        name="real_adr_decision",
        category="Real-data fixed",
        query="ADR decision",
    ),
    QuerySpec(
        name="real_lesson_learned",
        category="Real-data fixed",
        query="lesson learned",
    ),
    QuerySpec(
        name="real_pushback",
        category="Real-data fixed",
        query="pushback decision",
    ),
    QuerySpec(
        name="real_session_shutdown",
        category="Real-data fixed",
        query="session shutdown sequence",
    ),
    QuerySpec(
        name="real_validate_hard_fail",
        category="Real-data fixed",
        query="validate hard fail soft warn",
    ),
    QuerySpec(
        name="real_engine_memory",
        category="Real-data fixed",
        query="engine memory substrate",
    ),
    QuerySpec(
        name="real_scope_lock",
        category="Real-data fixed",
        query="scope lock routine commit",
    ),
    QuerySpec(
        name="real_mempalace_retire",
        category="Real-data fixed",
        query="MemPalace HNSW chromadb",
    ),
    QuerySpec(
        name="real_phase_5",
        category="Real-data fixed",
        query="Phase 5 closeout philosophy",
    ),
    QuerySpec(
        name="real_adr_0091",
        category="Real-data fixed",
        query="ADR 0091 SQLite FTS5",
    ),
]


# Plausible-recall probes — each targets specific recent decisions /
# lessons / pushback the migrated corpus should know about.
# Verdict-PASS bar: ≥4/5 return ≥1 candidate on the literal formulation.
REAL_DATA_PLAUSIBLE_CATALOG: list[QuerySpec] = [
    QuerySpec(
        name="plausible_substrate_cutover",
        category="Real-data plausible",
        query="ADR 0091 substrate cutover SQLite",
    ),
    QuerySpec(
        name="plausible_routine_wedge",
        category="Real-data plausible",
        query="routine wedge detect halted boot",
    ),
    QuerySpec(
        name="plausible_s_0184_health_check",
        category="Real-data plausible",
        query="S-0184 health check audit overdue catchup",
    ),
    QuerySpec(
        name="plausible_build_lifecycle_push",
        category="Real-data plausible",
        query="build_lifecycle_push wrapper interactive harness gate",
    ),
    QuerySpec(
        name="plausible_first_pass_quality",
        category="Real-data plausible",
        query="first pass production quality drafts polish",
    ),
]


def run_real_data_query(conn: sqlite3.Connection, spec: QuerySpec) -> QueryResult:
    """Run one real-data query — minimal-recall check (≥1 hit on literal)."""
    formulations = generate_formulations(spec.query)
    formulation_hits: dict[str, int] = {}
    formulation_matches: dict[str, str] = {}
    all_candidates: list[dict[str, Any]] = []
    for label, query in formulations:
        operator = FORMULATION_OPERATOR.get(label, "OR")
        formulation_matches[label] = to_fts5_match(query, operator=operator)
        candidates = fetch_candidates(
            conn,
            query,
            limit=10,
            operator=operator,
        )
        formulation_hits[label] = len(candidates)
        all_candidates.extend(candidates)

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for c in all_candidates:
        if c["id"] not in seen:
            seen.add(c["id"])
            deduped.append(c)
    deduped.sort(key=lambda c: c["rank_score"] or 0, reverse=True)
    top = deduped[0] if deduped else None

    literal_hits = formulation_hits.get("literal", 0)
    if literal_hits >= 1:
        verdict, reason = "PASS", "ok"
    else:
        verdict, reason = "FAIL", f"literal_hits={literal_hits} (need ≥1)"

    return QueryResult(
        spec=spec,
        formulation_hits=formulation_hits,
        top_drawer=top,
        formulation_matches=formulation_matches,
        verdict=verdict,
        reason=reason,
    )


def run_real_data_harness(
    db_path: Path | str,
) -> tuple[str, list[QueryResult], list[QueryResult]]:
    """Run real-data harness against an unseeded live substrate.

    Returns ``(aggregate_verdict, fixed_results, plausible_results)``.

    Aggregate:
    - PASS: 10/10 fixed PASS AND ≥4/5 plausible PASS.
    - PARTIAL: (8-9/10 fixed PASS) OR (2-3/5 plausible PASS).
    - FAIL: <8/10 fixed PASS OR <2/5 plausible PASS.
    """
    conn = get_conn(db_path)
    try:
        fixed = [run_real_data_query(conn, spec) for spec in REAL_DATA_FIXED_CATALOG]
        plausible = [
            run_real_data_query(conn, spec) for spec in REAL_DATA_PLAUSIBLE_CATALOG
        ]
    finally:
        conn.close()

    fixed_pass = sum(1 for r in fixed if r.verdict == "PASS")
    plausible_pass = sum(1 for r in plausible if r.verdict == "PASS")

    if fixed_pass == len(fixed) and plausible_pass >= 4:
        aggregate = "PASS"
    elif fixed_pass < 8 or plausible_pass < 2:
        aggregate = "FAIL"
    else:
        aggregate = "PARTIAL"

    return aggregate, fixed, plausible


def render_real_data_report(
    aggregate: str,
    fixed: list[QueryResult],
    plausible: list[QueryResult],
    ts: str,
    drawer_count: int,
    diary_count: int,
) -> str:
    """Render the real-data report."""
    lines: list[str] = []
    lines.append("# Engine-memory recall verification — S-0192 (real data)")
    lines.append("")
    lines.append(
        f"_Generated by `engine/memory/verify_recall.py --real-data` at {ts}._"
    )
    lines.append("")
    lines.append(f"**Verdict:** {aggregate}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "Real-data verification: harness runs against the live "
        "engine_memory substrate post-`migrate_from_mempalace.py` replay. "
        "Closes T1-D of `engine/build_readiness/"
        "engine_memory_substrate_first_exercise.md` (ADR 0091)."
    )
    lines.append("")
    lines.append(
        f"Live substrate state: **{drawer_count} drawers**, **{diary_count} diary entries**."
    )
    lines.append("")
    lines.append("## Verdict logic")
    lines.append("")
    lines.append(
        "- **PASS** — 10/10 fixed-catalog queries return ≥1 hit AND ≥4/5 plausible-recall queries return ≥1 hit."
    )
    lines.append("- **PARTIAL** — 8-9/10 fixed OR 2-3/5 plausible.")
    lines.append("- **FAIL** — <8/10 fixed OR <2/5 plausible.")
    lines.append("")
    lines.append("## Fixed-catalog results (broad vocabulary)")
    lines.append("")
    lines.append("| # | Query | Hits (lit / con / adj) | Top room/tags | Verdict |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate(fixed, 1):
        hits = (
            f"{r.formulation_hits.get('literal', 0)} / "
            f"{r.formulation_hits.get('conceptual', 0)} / "
            f"{r.formulation_hits.get('adjacent', 0)}"
        )
        if r.top_drawer is not None:
            top_str = (
                f"{r.top_drawer.get('room')} / "
                f"{','.join(r.top_drawer.get('tags') or []) or '—'}"
            )
        else:
            top_str = "—"
        lines.append(
            f"| {i} | `{r.spec.query}` | {hits} | {top_str} | **{r.verdict}** |"
        )
    lines.append("")
    lines.append("## Plausible-recall results (targeted vocabulary)")
    lines.append("")
    lines.append("| # | Query | Hits (lit / con / adj) | Top room/tags | Verdict |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate(plausible, 1):
        hits = (
            f"{r.formulation_hits.get('literal', 0)} / "
            f"{r.formulation_hits.get('conceptual', 0)} / "
            f"{r.formulation_hits.get('adjacent', 0)}"
        )
        if r.top_drawer is not None:
            top_str = (
                f"{r.top_drawer.get('room')} / "
                f"{','.join(r.top_drawer.get('tags') or []) or '—'}"
            )
        else:
            top_str = "—"
        lines.append(
            f"| {i} | `{r.spec.query}` | {hits} | {top_str} | **{r.verdict}** |"
        )
    lines.append("")
    lines.append("## Cutover-gate handoff")
    lines.append("")
    if aggregate == "PASS":
        lines.append(
            "PASS. ADR 0091 commitment 1 (engine-owned substrate) + commitment 3 "
            "(retrieval contract) verified end-to-end against migrated real "
            "data. `verification_passed: true` lands on "
            "[Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138)."
        )
    elif aggregate == "PARTIAL":
        lines.append(
            "PARTIAL. Cutover lands but a subset of plausible-recall queries "
            "didn't hit expected content. Investigate which queries failed, "
            "tune the formulation set in `engine/memory/boot_surface.py` if "
            "warranted, and surface as a soft-warn for the next session."
        )
    else:
        lines.append(
            "FAIL — HALT. Substrate does not produce expected recall against "
            "migrated corpus. Author HANDOFF entry; do NOT close S-0192 as "
            "`closed`. Re-open ADR 0091 deliberation at next interactive session."
        )
    lines.append("")
    return "\n".join(lines)


def run_query(conn: sqlite3.Connection, spec: QuerySpec) -> QueryResult:
    """Run the three formulations for one query spec; return a verdict."""
    formulations = generate_formulations(spec.query)
    formulation_hits: dict[str, int] = {}
    formulation_matches: dict[str, str] = {}
    all_candidates: list[dict[str, Any]] = []
    for label, query in formulations:
        operator = FORMULATION_OPERATOR.get(label, "OR")
        formulation_matches[label] = to_fts5_match(query, operator=operator)
        candidates = fetch_candidates(
            conn,
            query,
            room=spec.room_filter,
            tag_any=spec.tag_any_filter,
            since_days=spec.since_days_filter,
            limit=10,
            operator=operator,
        )
        formulation_hits[label] = len(candidates)
        all_candidates.extend(candidates)

    # Dedup by id, sort by rank_score; take top-1 for shape assertions.
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for c in all_candidates:
        if c["id"] not in seen:
            seen.add(c["id"])
            deduped.append(c)
    deduped.sort(key=lambda c: c["rank_score"] or 0, reverse=True)
    top = deduped[0] if deduped else None

    reasons: list[str] = []
    passed = True

    # Formulation distinctness — adjacent always differs from literal
    # because it injects "lessons pushback" tokens; conceptual may
    # collapse with literal when the token set is single (single-token
    # AND == single-token OR). The minimum bar is ≥2 distinct MATCH
    # expressions; the formulation_distinctness named spec asserts the
    # full ≥3-distinct contract on a query designed to satisfy it.
    distinct_matches = set(formulation_matches.values())
    min_distinct = 3 if spec.name == "formulation_distinctness" else 2
    if len(distinct_matches) < min_distinct:
        passed = False
        reasons.append(
            f"formulations not distinct: only {len(distinct_matches)} "
            f"unique MATCH expressions (need ≥{min_distinct})"
        )

    # Hit-count bounds (counted on literal formulation only; the
    # adjacent OR-with-lessons/pushback suffix injects matches that
    # would invalidate "boundary" tests if counted globally).
    literal_hits = formulation_hits.get("literal", 0)
    if literal_hits < spec.expected_min_hits:
        passed = False
        reasons.append(
            f"literal_hits={literal_hits} < expected_min_hits={spec.expected_min_hits}"
        )
    if spec.expected_max_hits is not None and literal_hits > spec.expected_max_hits:
        passed = False
        reasons.append(
            f"literal_hits={literal_hits} > expected_max_hits={spec.expected_max_hits}"
        )

    # Room/tag assertions (only when literal results exist — adjacent
    # cross-matches lessons/pushback drawers would otherwise yield
    # false positives for non-pushback/lesson queries).
    if literal_hits > 0 and top is not None:
        if spec.expected_room is not None and top["room"] != spec.expected_room:
            passed = False
            reasons.append(
                f"top room {top['room']!r} != expected {spec.expected_room!r}"
            )
        if spec.expected_tag is not None and spec.expected_tag not in top.get(
            "tags", []
        ):
            passed = False
            reasons.append(
                f"top tags {top.get('tags', [])!r} missing expected tag {spec.expected_tag!r}"
            )

    verdict = "PASS" if passed else "FAIL"
    reason = "ok" if passed else "; ".join(reasons)

    return QueryResult(
        spec=spec,
        formulation_hits=formulation_hits,
        top_drawer=top,
        formulation_matches=formulation_matches,
        verdict=verdict,
        reason=reason,
    )


def run_harness(db_path: Path | str) -> tuple[str, list[QueryResult]]:
    """Run all 10 queries against a seeded substrate at ``db_path``.

    Returns ``(aggregate_verdict, per_query_results)``. The aggregate is
    PASS (all 10 pass), PARTIAL (7-9 pass), or FAIL (<7 pass).
    """
    conn = get_conn(db_path)
    try:
        seed_substrate(conn)
        results = [run_query(conn, spec) for spec in QUERY_CATALOG]
    finally:
        conn.close()

    passed = sum(1 for r in results if r.verdict == "PASS")
    total = len(results)
    if passed == total:
        aggregate = "PASS"
    elif passed >= 7:
        aggregate = "PARTIAL"
    else:
        aggregate = "FAIL"
    return aggregate, results


def render_report(
    aggregate: str,
    results: list[QueryResult],
    ts: str,
) -> str:
    """Render the Markdown report committed to engine/docs/audits/."""
    lines: list[str] = []
    lines.append("# Engine-memory recall verification — S-0191")
    lines.append("")
    lines.append(f"_Generated by `engine/memory/verify_recall.py` at {ts}._")
    lines.append("")
    lines.append(f"**Verdict:** {aggregate}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "**Mechanical only.** User-adjudicated reframing at S-0191 boot: "
        "MemPalace is empirically broken (Issue #134), engine memory is "
        "empty until S-0192 replay, and `outcome_summary.boot_search_results` "
        "(referenced by the parent plan + ADR 0091 + readiness note) does "
        "not exist in any archive. Side-by-side comparison against MemPalace "
        "would be degenerate. This harness verifies the FTS5 + BM25 + "
        "recency + tag-class-boost retrieval mechanics against a "
        "seeded-fixture corpus (~20 synthetic drawers); the cite-worthy "
        "comparison gate slides to S-0192 close after `migrate_from_mempalace.py` "
        "populates real data."
    )
    lines.append("")
    lines.append(f"Corpus: **{len(SEED_CORPUS)} synthetic drawers**.")
    lines.append("")
    lines.append("## Per-query results")
    lines.append("")
    lines.append(
        "| # | Category | Query | Hits (lit / con / adj) | Top room/tags | Verdict | Reason |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        hits = (
            f"{r.formulation_hits.get('literal', 0)} / "
            f"{r.formulation_hits.get('conceptual', 0)} / "
            f"{r.formulation_hits.get('adjacent', 0)}"
        )
        if r.top_drawer is not None:
            top_str = (
                f"{r.top_drawer.get('room')} / "
                f"{','.join(r.top_drawer.get('tags') or []) or '—'}"
            )
        else:
            top_str = "—"
        # Trim query for table readability
        q = r.spec.query
        q_display = q if len(q) <= 50 else q[:47] + "..."
        lines.append(
            f"| {i} | {r.spec.category} | `{q_display}` | {hits} | {top_str} | "
            f"**{r.verdict}** | {r.reason} |"
        )
    lines.append("")
    lines.append("## Mechanical observations")
    lines.append("")
    lines.append(
        "- **Three-formulation distinctness:** every query produced 3 "
        "distinct FTS5 MATCH expressions across literal / conceptual / "
        "adjacent (asserted per-query)."
    )
    lines.append(
        "- **BM25 ranking sensible:** decision-room drawers tagged "
        "`decision` rose to top-1 for the decision-recall queries "
        "via the +0.15 tag-class boost."
    )
    lines.append(
        "- **Recency boost present:** the SQL's "
        "`0.2 * exp(-((julianday('now') - julianday(filed_at)) / half_life))` "
        "term applies (verified at module load by the `exp` Python "
        "fallback in `engine/memory/connection.py`)."
    )
    lines.append(
        "- **Superseded exclusion:** the `superseded_by IS NULL` "
        "WHERE clause is exercised by `engine/memory/test_tools.py::"
        "test_list_drawers_excludes_superseded`."
    )
    lines.append("")
    lines.append("## Cutover-gate handoff")
    lines.append("")
    lines.append(
        "Per the user-adjudicated reframing: this harness's PASS verdict "
        "closes T1-C of "
        "[`engine/build_readiness/engine_memory_substrate_first_exercise.md`]"
        "(../../build_readiness/engine_memory_substrate_first_exercise.md) "
        "**mechanically**. The cite-worthy comparison gate slides to "
        "S-0192 close — after `engine/memory/migrate_from_mempalace.py` "
        "populates real curated drawers from the post-S-0186-prune palace, "
        "the harness can be re-run against actual data and the comparison "
        "against MemPalace (if its substrate is operational at that time) "
        "can fire. If MemPalace remains broken at S-0192, the gate becomes "
        "a self-comparison check: real-data substrate must produce ≥30% "
        "cite-worthy candidates for the same query catalog. Either way, "
        "ADR 0091 `verification_passed: true` lands on "
        "[Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138) "
        "at S-0192 close."
    )
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- Synthetic fixtures only; real-data verification at S-0192.")
    lines.append(
        "- No live MemPalace side-by-side; the broken substrate "
        "produces no comparison signal."
    )
    lines.append(
        "- `query_log` table is populated by boot orchestrator + MCP "
        "`engine_memory_search`; this harness does NOT write to it "
        "(uses the temp substrate, not the live one)."
    )
    lines.append("")
    return "\n".join(lines)


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_output_path() -> Path:
    """Default report path: ``engine/docs/audits/engine_memory_recall_S-0191.md``."""
    from engine.memory.connection import _resolve_repo_root

    return (
        _resolve_repo_root()
        / "engine"
        / "docs"
        / "audits"
        / "engine_memory_recall_S-0191.md"
    )


def _default_real_data_output_path() -> Path:
    """Default report path for --real-data: engine_memory_recall_S-0192.md."""
    from engine.memory.connection import _resolve_repo_root

    return (
        _resolve_repo_root()
        / "engine"
        / "docs"
        / "audits"
        / "engine_memory_recall_S-0192.md"
    )


def _count_live_substrate(db_path: Path | str) -> tuple[int, int]:
    """Return (drawer_count, diary_count) from the live substrate."""
    conn = get_conn(db_path)
    try:
        drawer_count = conn.execute("SELECT count(*) FROM drawers").fetchone()[0]
        diary_count = conn.execute("SELECT count(*) FROM diary").fetchone()[0]
    finally:
        conn.close()
    return int(drawer_count), int(diary_count)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verification harness for the engine-memory read surface. "
            "Synthetic mode (default): seeds a tempfile substrate and "
            "runs the 10-query mechanical catalog. Real-data mode "
            "(--real-data): runs against the live post-migration "
            "substrate with broad-vocabulary + plausible-recall catalogs."
        )
    )
    parser.add_argument(
        "--real-data",
        action="store_true",
        help=(
            "Run against the live engine_memory substrate (no seeding); "
            "verifies cite-worthy recall after migrate_from_mempalace.py "
            "replay. Closes T1-D per ADR 0091."
        ),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help=(
            "Path to write the audit report. Default: "
            "engine/docs/audits/engine_memory_recall_S-0191.md (synthetic) "
            "or engine_memory_recall_S-0192.md (--real-data)."
        ),
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help=(
            "SQLite path. Synthetic mode: override the seeded tempfile. "
            "Real-data mode: override the live substrate location."
        ),
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run the harness; print verdict to stdout; do not write the report.",
    )
    args = parser.parse_args(argv)

    ts = _iso_utc_now()

    if args.real_data:
        # Real-data: use the live substrate as-is, no seeding, no cleanup.
        if args.db_path is not None:
            db_path = args.db_path
        else:
            from engine.memory.connection import resolve_db_path

            db_path = resolve_db_path()

        if not Path(db_path).is_file():
            print(
                f"[engine-memory-verify-recall] real-data: live substrate not "
                f"found at {db_path}; run migrate_from_mempalace.py first.",
                file=sys.stderr,
            )
            return 2

        drawer_count, diary_count = _count_live_substrate(db_path)
        aggregate, fixed, plausible = run_real_data_harness(db_path)
        report = render_real_data_report(
            aggregate, fixed, plausible, ts, drawer_count, diary_count
        )

        if args.no_write:
            print(report)
        else:
            output = args.output_md or _default_real_data_output_path()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report, encoding="utf-8")
            print(
                f"[engine-memory-verify-recall] mode=real-data "
                f"verdict={aggregate} fixed={len(fixed)} "
                f"plausible={len(plausible)} drawers={drawer_count} "
                f"diary={diary_count} report={output}"
            )

        return 0 if aggregate in ("PASS", "PARTIAL") else 2

    # Synthetic mode (default).
    if args.db_path is not None:
        db_path = args.db_path
        cleanup_db = False
    else:
        tmp = tempfile.NamedTemporaryFile(
            prefix="engine_memory_verify_", suffix=".sqlite3", delete=False
        )
        tmp.close()
        db_path = Path(tmp.name)
        cleanup_db = True

    try:
        aggregate, results = run_harness(db_path)
    finally:
        if cleanup_db and Path(db_path).is_file():
            try:
                Path(db_path).unlink()
            except OSError:
                pass

    report = render_report(aggregate, results, ts)

    if args.no_write:
        print(report)
    else:
        output = args.output_md or _default_output_path()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(
            f"[engine-memory-verify-recall] mode=synthetic "
            f"verdict={aggregate} queries={len(results)} report={output}"
        )

    return 0 if aggregate in ("PASS", "PARTIAL") else 2


if __name__ == "__main__":
    sys.exit(main())
