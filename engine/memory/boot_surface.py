"""Boot-time engine-memory orchestrator — three formulations + FTS5 + section write.

Successor to ``engine/tools/mempalace_boot_search.py``. Ported with the
three-formulation pattern preserved (literal / conceptual / adjacent —
deterministic, identical inputs always produce identical outputs) but
the retrieval substrate swapped from chromadb vector similarity to
SQLite FTS5 with the BM25 + recency + tag-class-boost SQL from the
parent plan ``~/.claude/plans/mempalace-overhead-is-dragging-twinkly-harp.md``
(lines 252-282) per ADR 0091.

Semantic shift vs the mempalace predecessor
-------------------------------------------
mempalace_boot_search.py used vector similarity with a
``min_similarity`` floor; SQLite FTS5 produces BM25 rank scores (lower
is more relevant per FTS5 convention) which we flip to higher-is-better
and combine with recency + tag-class + tag-match boosts. There is no
similarity threshold — ranking + LIMIT is the only filter. The CLI
flag from the predecessor (``--similarity-threshold``) is dropped.

Module shape
------------
- :func:`generate_formulations` — same three-form deterministic
  shape as the predecessor (literal / conceptual / adjacent). The
  STOPWORDS set and tokenization rules are ported byte-faithful so the
  formulation surface is comparable across substrates during the
  cutover window.
- :func:`fetch_candidates` — runs the parent-plan SQL against the
  ``drawers_fts`` virtual table joined to ``drawers``. Returns rows as
  dicts with a synthetic ``rank_score`` column.
- :func:`render_section` — emits a Markdown ``## Prior context (engine
  memory)`` block with per-formulation subsections.
- :func:`write_section` — idempotent rewrite of the section in
  ``engine/session/current_plan.md`` (same H2-bounded pattern as the
  predecessor).
- :func:`append_query_log` — INSERTs one ``query_log`` row per
  formulation (SQLite-side telemetry replacing the predecessor's
  ``current_mempalace.jsonl`` shim).
- :func:`resolve_work_item` — same three-source precedence:
  ``current.json``'s ``working_on`` (eager-claim seed) → first pending
  task in ``auto_target.json`` (routine mode pre-claim) → first
  paragraph after STATE.md's "Next session work item" heading
  (interactive pre-claim).

Module-import surface stays inside ``engine/memory/`` per the
engine/product wall (ADR 0037) — no dependency on ``engine/tools/``.

Cross-references
----------------
- ADR 0091 — the substrate decision.
- Parent plan section "S-0191" — this module's scope.
- session-build-lifecycle SKILL step 3 — wires this CLI into the boot
  flow at S-0192 (NOT this session; the S-0191 deliverable is the
  module + tests only).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.memory.connection import get_conn


# Path defaults resolve from the repo root via the substrate's
# connection.py git-rev-parse machinery; CLI flags can override.
def _repo_root() -> Path:
    from engine.memory.connection import _resolve_repo_root  # local import

    return _resolve_repo_root()


DEFAULT_TOP_N = 8
DEFAULT_LIMIT = 30
MAX_QUERY_CHARS = 250
DEFAULT_KEYWORD_COUNT = 6
DEFAULT_RECENCY_HALF_LIFE_DAYS = 30.0

SECTION_HEADING = "## Prior context (engine memory)"
SECTION_END_PATTERN = re.compile(r"^## ", re.MULTILINE)

WORK_ITEM_HEADING_PATTERN = re.compile(
    r"^##\s+Next session work item\s*$", re.MULTILINE | re.IGNORECASE
)

# Ported byte-faithful from mempalace_boot_search.py so formulation
# surface stays comparable across substrates during the cutover window.
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "being",
        "but",
        "by",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "per",
        "so",
        "such",
        "that",
        "the",
        "their",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "to",
        "vs",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "you",
        "your",
        "via",
        "etc",
        "issue",
        "session",
        "phase",
        "step",
        "close",
        "closes",
        "campaign",
        "task",
        "plan",
        "work",
    }
)


def _iso_utc_now() -> str:
    """Return current UTC time as ISO 8601 with Z suffix.

    Inlined to avoid depending on ``engine/tools/timestamps.py`` — the
    engine/memory package stays inside its own subtree per ADR 0037.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_query(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace, truncate."""
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:MAX_QUERY_CHARS]


def _extract_keywords(text: str, max_n: int = DEFAULT_KEYWORD_COUNT) -> list[str]:
    """Return up to ``max_n`` substantive tokens (≥3 chars, stopwords dropped, dedup-preserve-order)."""
    normalized = _normalize_query(text)
    seen: set[str] = set()
    keywords: list[str] = []
    for raw in normalized.split():
        token = raw.strip("-")
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        keywords.append(token)
        if len(keywords) >= max_n:
            break
    return keywords


def generate_formulations(work_item: str) -> list[tuple[str, str]]:
    """Return [(label, normalized_query), ...] — three formulations.

    Deterministic; identical inputs always yield identical outputs (so
    tests can pin shape and tuning is one-line). Labels: literal,
    conceptual, adjacent.
    """
    literal = _normalize_query(work_item)
    keywords = _extract_keywords(work_item)
    conceptual = " ".join(keywords) if keywords else literal
    adjacent_base = literal[: MAX_QUERY_CHARS - len(" lessons pushback")]
    adjacent = f"{adjacent_base} lessons pushback"
    return [
        ("literal", literal),
        ("conceptual", conceptual),
        ("adjacent", adjacent),
    ]


def to_fts5_match(query: str, operator: str = "OR") -> str:
    """Convert a normalized query string to an FTS5 MATCH expression.

    Each token is wrapped in double quotes so FTS5 reserved characters
    (``AND``, ``OR``, ``NOT``, ``NEAR``, ``*``, ``"``, ``(``, ``)``,
    ``:``, ``.``) cannot be parsed as operators. Tokens shorter than 3
    chars and stopwords are dropped (same filter as keyword extraction)
    to avoid noisy OR-of-everything matches that swamp BM25.

    ``operator`` is ``"OR"`` (default — broad recall) or ``"AND"``
    (strict precision). The three boot formulations map as: literal →
    OR, conceptual → AND, adjacent → OR (see :data:`FORMULATION_OPERATOR`).
    This is the FTS5-substrate equivalent of mempalace's vector-embedding
    diversity — for FTS5, distinct logical operators produce distinct
    result sets even when the token list is identical.

    Empty query (all tokens filtered) returns ``"~_~~_no_query_~_~~"``
    — a deliberately unmatchable phrase. The caller decides whether to
    treat that as "substrate alive, zero results" or skip the formulation.
    """
    if operator not in ("OR", "AND"):
        raise ValueError(f"operator must be 'OR' or 'AND', got {operator!r}")
    if not query.strip():
        return '"~_~~_no_query_~_~~"'

    tokens: list[str] = []
    seen: set[str] = set()
    for raw in query.lower().split():
        token = raw.strip("-")
        # Strip embedded quotes — they would terminate the wrapping
        # quoted-string and let downstream chars escape as operators.
        token = token.replace('"', "")
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        tokens.append(f'"{token}"')

    if not tokens:
        return '"~_~~_no_query_~_~~"'
    return f" {operator} ".join(tokens)


# Maps boot-formulation label → FTS5 operator. Literal and adjacent run
# broad-OR; conceptual runs strict-AND so it surfaces drawers whose
# content carries *all* of the substantive keywords (high-precision
# complement to the broad-recall siblings). Distinct operators also
# guarantee the three formulations produce distinct MATCH expressions
# for short queries where token sets collapse after stopword filtering.
FORMULATION_OPERATOR: dict[str, str] = {
    "literal": "OR",
    "conceptual": "AND",
    "adjacent": "OR",
}


_FETCH_SQL = """
WITH ranked AS (
  SELECT
    d.id, d.room, d.tags, d.agent, d.session_id,
    d.created_at, d.filed_at, d.content, d.metadata,
    bm25(drawers_fts) AS bm25_score
  FROM drawers_fts
  JOIN drawers d ON d.rowid = drawers_fts.rowid
  WHERE drawers_fts MATCH :query
    AND d.superseded_by IS NULL
    AND (:room IS NULL OR d.room = :room)
    AND (
      :since_days IS NULL
      OR julianday(d.filed_at) >= julianday('now') - CAST(:since_days AS REAL)
    )
)
SELECT
  id, room, tags, agent, session_id, created_at, filed_at, content,
  metadata, bm25_score,
  (
    (-bm25_score)
    + 0.2 * exp(-((julianday('now') - julianday(filed_at)) / :half_life))
    + CASE WHEN :room IS NOT NULL AND room = :room THEN 0.3 ELSE 0 END
    + CASE
        WHEN :tag_any IS NOT NULL
             AND EXISTS (SELECT 1 FROM json_each(tags) WHERE value = :tag_any)
        THEN 0.25 ELSE 0
      END
    + CASE
        WHEN EXISTS (SELECT 1 FROM json_each(tags) WHERE value = 'decision') THEN 0.15
        WHEN EXISTS (SELECT 1 FROM json_each(tags) WHERE value = 'pushback') THEN 0.12
        WHEN EXISTS (SELECT 1 FROM json_each(tags) WHERE value = 'lesson')   THEN 0.10
        ELSE 0
      END
  ) AS rank_score
FROM ranked
ORDER BY rank_score DESC
LIMIT :limit
"""


def fetch_candidates(
    conn: sqlite3.Connection,
    query: str,
    *,
    room: str | None = None,
    tag_any: str | None = None,
    since_days: int | None = None,
    limit: int = DEFAULT_LIMIT,
    half_life: float = DEFAULT_RECENCY_HALF_LIFE_DAYS,
    operator: str = "OR",
) -> list[dict[str, Any]]:
    """Run the FTS5 + BM25 + recency + tag-class-boost retrieval.

    ``query`` is a normalized literal/conceptual/adjacent string;
    converted to an FTS5 MATCH expression via :func:`to_fts5_match`
    inside this function. ``operator`` (default ``"OR"``) selects broad
    recall vs strict precision. Caller stays substrate-agnostic.

    Returns ``list[dict]`` of candidate rows with ``id``, ``room``,
    ``tags`` (parsed from JSON), ``agent``, ``session_id``,
    ``created_at``, ``filed_at``, ``content``, ``metadata`` (parsed
    from JSON), ``bm25_score`` (FTS5 raw — lower is better), and
    ``rank_score`` (synthetic — higher is better; the ORDER BY column).
    """
    match_expr = to_fts5_match(query, operator=operator)
    rows = conn.execute(
        _FETCH_SQL,
        {
            "query": match_expr,
            "room": room,
            "tag_any": tag_any,
            "since_days": since_days,
            "half_life": half_life,
            "limit": limit,
        },
    ).fetchall()

    candidates: list[dict[str, Any]] = []
    for row in rows:
        (
            id_,
            room_,
            tags_raw,
            agent,
            session_id,
            created_at,
            filed_at,
            content,
            metadata_raw,
            bm25_score,
            rank_score,
        ) = row
        try:
            tags = json.loads(tags_raw) if tags_raw else []
        except json.JSONDecodeError:
            tags = []
        try:
            metadata = json.loads(metadata_raw) if metadata_raw else {}
        except json.JSONDecodeError:
            metadata = {}
        candidates.append(
            {
                "id": id_,
                "room": room_,
                "tags": tags,
                "agent": agent,
                "session_id": session_id,
                "created_at": created_at,
                "filed_at": filed_at,
                "content": content,
                "metadata": metadata,
                "bm25_score": bm25_score,
                "rank_score": rank_score,
            }
        )
    return candidates


def _format_drawer_line(drawer: dict[str, Any]) -> str:
    """One Markdown bullet per drawer — includes room, tags, filed_at, excerpt."""
    room = drawer.get("room") or "?"
    tags = drawer.get("tags") or []
    tags_str = ",".join(tags) if tags else "—"
    session_id = drawer.get("session_id") or "?"
    filed_at = (drawer.get("filed_at") or "?")[:10]  # YYYY-MM-DD slice
    rank = drawer.get("rank_score")
    rank_str = f"{rank:.3f}" if isinstance(rank, (int, float)) else "?"
    drawer_id = drawer.get("id", "?")
    short_id = drawer_id[:8] if drawer_id else "?"
    content = drawer.get("content") or ""
    excerpt = re.sub(r"\s+", " ", content).strip()
    if len(excerpt) > 180:
        excerpt = excerpt[:177] + "..."
    return (
        f"- **{room}** [{tags_str}] (sess `{session_id}`, "
        f"filed {filed_at}, id `{short_id}`, rank {rank_str}) — {excerpt}"
    )


def render_section(
    formulations_results: list[tuple[str, str, list[dict[str, Any]]]],
    ts: str,
    top_n: int = DEFAULT_TOP_N,
    substrate_unreachable: bool = False,
) -> str:
    """Render the Markdown section body. Caller writes via :func:`write_section`."""
    lines: list[str] = [SECTION_HEADING, ""]
    if substrate_unreachable:
        lines.append(f"_Generated by `engine/memory/boot_surface.py` at {ts}._")
        lines.append("")
        lines.append(
            "_Engine-memory substrate unreachable at boot — no formulations "
            'executed. Verify via `python -c "from engine.memory.connection '
            'import healthcheck; healthcheck()"` and re-run boot search._'
        )
        lines.append("")
        return "\n".join(lines)

    # Union + dedup across formulations, preserving first-seen order
    # within each formulation; then take top_n by rank_score across the
    # whole union. This produces the "surfaced inline" set the SKILL
    # body asks Claude to read.
    union: dict[str, dict[str, Any]] = {}
    for _, _, drawers in formulations_results:
        for drawer in drawers:
            drawer_id = drawer.get("id")
            if drawer_id is None or drawer_id in union:
                continue
            union[drawer_id] = drawer
    ranked_union = sorted(
        union.values(),
        key=lambda d: d.get("rank_score") or 0,
        reverse=True,
    )[:top_n]

    total = sum(len(d) for _, _, d in formulations_results)
    lines.append(
        f"_Generated by `engine/memory/boot_surface.py` at {ts}. "
        f"Three formulations × FTS5 BM25 + recency + tag-class boost; "
        f"{total} candidates union to {len(ranked_union)} surfaced._"
    )
    lines.append("")

    if ranked_union:
        lines.append(f"### Top {len(ranked_union)} surfaced inline")
        for drawer in ranked_union:
            lines.append(_format_drawer_line(drawer))
        lines.append("")

    for label, query, drawers in formulations_results:
        lines.append(f"### {label.capitalize()} — `{query}`")
        if not drawers:
            lines.append("- _no candidates_")
        else:
            for drawer in drawers:
                lines.append(_format_drawer_line(drawer))
        lines.append("")

    return "\n".join(lines)


def write_section(plan_path: Path, section_body: str) -> None:
    """Idempotently write/replace SECTION_HEADING block in current_plan.md.

    Section bounds: from SECTION_HEADING to the next H2 (``## ``) or EOF.
    """
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    existing = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""

    if SECTION_HEADING in existing:
        idx = existing.index(SECTION_HEADING)
        rest = existing[idx + len(SECTION_HEADING) :]
        next_h2 = SECTION_END_PATTERN.search(rest)
        if next_h2 is not None:
            new = (
                existing[:idx]
                + section_body.rstrip()
                + "\n\n"
                + rest[next_h2.start() :]
            )
        else:
            new = existing[:idx] + section_body.rstrip() + "\n"
    else:
        sep = "\n\n" if existing and not existing.endswith("\n\n") else ""
        new = (
            (existing + sep + section_body.rstrip() + "\n")
            if existing
            else (section_body.rstrip() + "\n")
        )

    plan_path.write_text(new, encoding="utf-8")


def append_query_log(
    conn: sqlite3.Connection,
    formulations: list[tuple[str, str, int]],
    session_id: str | None,
) -> None:
    """INSERT one ``query_log`` row per formulation.

    ``formulations`` is ``[(label, query, result_count), ...]``. The
    ``queried_at`` column defaults to ``datetime('now')`` SQL-side so
    we don't need to pass a timestamp.
    """
    for label, query, result_count in formulations:
        conn.execute(
            "INSERT INTO query_log "
            "(session_id, formulation, query_text, result_count) "
            "VALUES (?, ?, ?, ?)",
            (session_id, label, query, result_count),
        )


def resolve_work_item(
    current_path: Path,
    state_path: Path,
    auto_target_path: Path,
) -> str | None:
    """Return the work-item phrase for this session, or None if unresolvable.

    Resolution order:
    1. ``current.json``'s ``working_on`` (eager-claim seed; preferred).
    2. ``auto_target.json``'s first pending task ``name`` (routine pre-claim).
    3. ``STATE.md``'s "Next session work item" first paragraph (interactive
       pre-claim).
    """
    if current_path.is_file():
        try:
            current = json.loads(current_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            current = {}
        working_on = current.get("working_on") if isinstance(current, dict) else None
        if isinstance(working_on, str) and working_on.strip():
            return working_on.strip()

    if auto_target_path.is_file():
        try:
            target = json.loads(auto_target_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            target = {}
        if isinstance(target, dict) and target.get("paused") is not True:
            tasks_raw = target.get("tasks")
            tasks: list[Any] = tasks_raw if isinstance(tasks_raw, list) else []
            for task in tasks:
                if not isinstance(task, dict):
                    continue
                if task.get("status") == "pending":
                    name = task.get("name")
                    if isinstance(name, str) and name.strip():
                        return name.strip()

    if state_path.is_file():
        text = state_path.read_text(encoding="utf-8")
        match = WORK_ITEM_HEADING_PATTERN.search(text)
        if match is not None:
            after = text[match.end() :]
            next_h2 = SECTION_END_PATTERN.search(after)
            block = after[: next_h2.start()] if next_h2 else after
            block = block.strip()
            if block:
                first_para = block.split("\n\n", 1)[0]
                first_para = re.sub(r"\s+", " ", first_para).strip()
                if first_para.startswith("**"):
                    first_para = first_para.lstrip("*").strip()
                if first_para:
                    return first_para[:500]

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Boot-time engine-memory orchestrator. Three formulations × "
            "FTS5 + BM25 + recency + tag-class-boost retrieval; idempotent "
            "Markdown section write into current_plan.md."
        )
    )
    parser.add_argument("--work-item", type=str, default=None)
    parser.add_argument("--max-results", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument(
        "--half-life",
        type=float,
        default=DEFAULT_RECENCY_HALF_LIFE_DAYS,
        help="Recency boost half-life in days (default 30).",
    )
    parser.add_argument("--plan-path", type=Path, default=None)
    parser.add_argument("--current-path", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--auto-target-path", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    plan_path = args.plan_path or repo_root / "engine" / "session" / "current_plan.md"
    current_path = (
        args.current_path or repo_root / "engine" / "session" / "current.json"
    )
    state_path = args.state_path or repo_root / "engine" / "STATE.md"
    auto_target_path = (
        args.auto_target_path or repo_root / "engine" / "session" / "auto_target.json"
    )

    work_item = args.work_item
    if work_item is None:
        work_item = resolve_work_item(current_path, state_path, auto_target_path)
    if work_item is None:
        print(
            "[engine-memory-boot-surface] could not resolve work-item phrase "
            "(no current.json working_on, no auto_target pending task, no "
            "STATE.md 'Next session work item' block). Pass --work-item "
            "explicitly.",
            file=sys.stderr,
        )
        return 1

    formulations = generate_formulations(work_item)
    ts = _iso_utc_now()

    # Try to open the substrate; if connection fails surface
    # substrate-unreachable section and exit 2 — same shape as the
    # predecessor's substrate-down path.
    try:
        conn = get_conn()
    except (sqlite3.Error, OSError, RuntimeError) as exc:
        print(
            f"[engine-memory-boot-surface] substrate unreachable: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        section_body = render_section(
            [(label, query, []) for label, query in formulations],
            ts,
            top_n=args.top_n,
            substrate_unreachable=True,
        )
        if not args.dry_run:
            write_section(plan_path, section_body)
        else:
            print(section_body)
        return 2

    try:
        # Resolve session_id from current.json for query_log attribution.
        session_id: str | None = None
        if current_path.is_file():
            try:
                current = json.loads(current_path.read_text(encoding="utf-8"))
                if isinstance(current, dict):
                    raw_id = current.get("id")
                    if isinstance(raw_id, str) and raw_id.strip():
                        session_id = raw_id.strip()
            except json.JSONDecodeError:
                pass

        formulations_results: list[tuple[str, str, list[dict[str, Any]]]] = []
        log_rows: list[tuple[str, str, int]] = []
        for label, query in formulations:
            candidates = fetch_candidates(
                conn,
                query,
                limit=args.max_results,
                half_life=args.half_life,
                operator=FORMULATION_OPERATOR.get(label, "OR"),
            )
            formulations_results.append((label, query, candidates))
            log_rows.append((label, query, len(candidates)))

        section_body = render_section(
            formulations_results,
            ts,
            top_n=args.top_n,
            substrate_unreachable=False,
        )

        if args.dry_run:
            print(section_body)
        else:
            write_section(plan_path, section_body)
            append_query_log(conn, log_rows, session_id)

        total = sum(len(d) for _, _, d in formulations_results)
        print(
            f"[engine-memory-boot-surface] formulations=3 "
            f"candidates={total} plan={plan_path}",
            flush=True,
        )
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
