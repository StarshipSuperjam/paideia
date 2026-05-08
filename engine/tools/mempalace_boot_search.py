"""Boot-time MemPalace orchestrator — three formulations + similarity filter + current_plan.md write.

Layer 1 contract per ADR 0056 (S-0093 amendment, Issue #38).

Purpose
-------
ADR 0056 (S-0078) mechanized boot-search FREQUENCY: the PostToolUse hook +
``scan_mempalace_activity.py`` + ``validate.py --final-check`` ensure
``mempalace_search`` runs at least once per session. It does not address
EFFECTIVENESS — phrasing, reformulation, and forwarding-of-results into
planning all remained AI judgment. A session that boot-searches the
literal phrase from ``engine/STATE.md``'s next-session work item, gets
nothing relevant (because vocabulary doesn't overlap with prior drawers),
and proceeds passes the ``mempalace_boot_query_skipped`` soft-warn but
realizes none of the value the boot search was meant to deliver.

This tool runs three formulations of the work-item phrase through
``mempalace.mcp_server.tool_search``, filters by similarity threshold,
and writes a ``## Prior context (MemPalace boot search)`` section into
``engine/session/current_plan.md``. The write is idempotent — re-running
replaces the section. Telemetry shim writes one JSONL line per
formulation into ``engine/session/current_mempalace.jsonl`` so the
existing audit's ``search_calls`` counter increments correctly.

Formulation set
---------------
- **literal**: work-item phrase normalized (lowercased, punctuation
  stripped, ≤250 chars per mempalace_search's max query length).
- **conceptual**: top-N substantive keywords from the phrase joined with
  spaces. Drops connectives so the vector embedding lands at a different
  point in semantic space — useful when the literal sentence-shape
  produces weak retrieval.
- **adjacent**: literal phrase suffixed with ``lessons pushback`` —
  orients the search toward past-failure-recovery drawers
  (``lesson``-tagged + ``pushback``-tagged content).

Similarity filter (default ≥0.6 per Issue #38) is applied via
``tool_search``'s native ``min_similarity`` parameter. Tunable via
``--similarity-threshold`` flag.

Mode resolution
---------------
- Reads ``engine/session/current.json``'s ``working_on`` (eager-claim seed)
  first.
- Falls back to parsing the "Next session work item" block from
  ``engine/STATE.md`` for sessions not yet claimed.
- Routine mode: reads the active task's ``name`` from
  ``engine/session/auto_target.json`` (eligibility match per
  routine-mode-lifecycle skill step 5).

Exit codes
----------
- ``0`` — boot search ran (or dry-run printed). Section written even when
  every formulation returns empty results above threshold (the section
  carries an "_no drawers above threshold_" notice).
- ``1`` — work-item phrase could not be resolved.
- ``2`` — mempalace library import failed. Best-effort: emits stderr
  line + writes a "substrate unreachable" section + skips telemetry shim.

Out of scope
------------
- LLM-driven paraphrase. The conceptual formulation is deterministic
  keyword extraction, not true paraphrase.
- Multi-wing / multi-room filtering — defaults to all wings/rooms.
- Persistence across sessions — section is per-session (rewritten each
  boot); JSONL telemetry truncates at shutdown step 0.

Cross-references
----------------
- ADR 0056 (S-0078; S-0093 amendment) — the contract.
- engine/operations/mempalace-operations.md "Mechanical adoption checks".
- session-build-lifecycle SKILL step 3 / routine-mode-lifecycle SKILL
  step 5.5 — the invocation sites.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import emit  # noqa: E402  # ADR 0058

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"
DEFAULT_STATE_PATH = REPO_ROOT / "engine" / "STATE.md"
DEFAULT_AUTO_TARGET_PATH = REPO_ROOT / "engine" / "session" / "auto_target.json"
DEFAULT_PLAN_PATH = REPO_ROOT / "engine" / "session" / "current_plan.md"
DEFAULT_JSONL_PATH = REPO_ROOT / "engine" / "session" / "current_mempalace.jsonl"

DEFAULT_SIMILARITY_THRESHOLD = 0.6
DEFAULT_MAX_RESULTS = 5
MAX_QUERY_CHARS = 250
DEFAULT_KEYWORD_COUNT = 6

SECTION_HEADING = "## Prior context (MemPalace boot search)"
SECTION_END_PATTERN = re.compile(r"^## ", re.MULTILINE)

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

WORK_ITEM_HEADING_PATTERN = re.compile(
    r"^##\s+Next session work item\s*$", re.MULTILINE | re.IGNORECASE
)


def _normalize_query(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace, truncate."""
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:MAX_QUERY_CHARS]


def _extract_keywords(text: str, max_n: int = DEFAULT_KEYWORD_COUNT) -> list[str]:
    """Return up to max_n substantive tokens (≥3 chars, stopwords dropped, dedup-preserve-order)."""
    normalized = _normalize_query(text)
    seen: set[str] = set()
    keywords: list[str] = []
    for token in normalized.split():
        token = token.strip("-")
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
    """Return [(label, query), ...] — three formulations.

    Deterministic; identical inputs always yield identical outputs (so
    tests can pin shape and tuning is one-line).
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


def fetch_drawers(
    query: str, min_similarity: float, limit: int
) -> list[dict[str, Any]] | None:
    """Call mempalace.mcp_server.tool_search; return results list or None on import failure.

    Returning None signals substrate-unreachable to the caller — distinct
    from an empty list (substrate alive, no hits above threshold).
    """
    try:
        from mempalace.mcp_server import tool_search
    except ImportError:
        return None
    try:
        result = tool_search(query=query, limit=limit, min_similarity=min_similarity)
    except Exception as exc:  # pragma: no cover - defensive; MCP runtime failures
        print(
            f"[mempalace-boot-search] tool_search raised {type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return None
    drawers = result.get("results")
    return drawers if isinstance(drawers, list) else []


def _format_drawer_line(drawer: dict[str, Any]) -> str:
    """One Markdown bullet per drawer."""
    wing = drawer.get("wing") or "?"
    room = drawer.get("room") or "?"
    similarity = drawer.get("similarity")
    sim_str = f"{similarity:.2f}" if isinstance(similarity, (int, float)) else "?"
    source = drawer.get("source_file") or "?"
    text = drawer.get("text") or ""
    excerpt = re.sub(r"\s+", " ", text).strip()
    if len(excerpt) > 180:
        excerpt = excerpt[:177] + "..."
    return f"- **{wing}/{room}** (source: `{source}`; sim: {sim_str}) — {excerpt}"


def render_section(
    formulations_results: list[tuple[str, str, list[dict[str, Any]]]],
    ts: str,
    threshold: float,
    substrate_unreachable: bool,
) -> str:
    """Render the Markdown section body (heading included)."""
    lines: list[str] = [SECTION_HEADING, ""]
    if substrate_unreachable:
        lines.append(f"_Generated by `engine/tools/mempalace_boot_search.py` at {ts}._")
        lines.append("")
        lines.append(
            "_MemPalace substrate unreachable at boot — no formulations executed. "
            "The boot-search soft-warn at shutdown will surface the gap unless other "
            "MemPalace MCP calls landed during the session._"
        )
        lines.append("")
        return "\n".join(lines)

    total = sum(len(d) for _, _, d in formulations_results)
    lines.append(
        f"_Generated by `engine/tools/mempalace_boot_search.py` at {ts}. "
        f"Three formulations × similarity ≥{threshold:.2f} = {total} drawers._"
    )
    lines.append("")

    for label, query, drawers in formulations_results:
        lines.append(f"### {label.capitalize()} — `{query}`")
        if not drawers:
            lines.append("- _no drawers above threshold_")
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
    if plan_path.is_file():
        existing = plan_path.read_text(encoding="utf-8")
    else:
        existing = ""

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


def append_telemetry(
    jsonl_path: Path, formulations: list[tuple[str, str]], ts: str
) -> None:
    """Append one JSONL line per formulation, mimicking the PostToolUse hook shape.

    Keeps ``search_calls`` increment consistent with the existing audit
    (PostToolUse hook only fires on ``mcp__mempalace__*`` MCP tool calls;
    library-import path doesn't trigger it). The args_summary prefix
    ``boot-search:<label>:`` makes orchestrator-emitted lines distinguishable
    from AI-emitted MCP calls if forensics ever needs the distinction.
    """
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        for label, query in formulations:
            entry = {
                "ts": ts,
                "tool": "mcp__mempalace__mempalace_search",
                "args_summary": f"boot-search:{label}:{query[:160]}",
            }
            f.write(json.dumps(entry) + "\n")


def resolve_work_item(
    current_path: Path,
    state_path: Path,
    auto_target_path: Path,
) -> str | None:
    """Return the work-item phrase for this session, or None if unresolvable.

    Resolution order:
    1. ``current.json``'s ``working_on`` (eager-claim seed; preferred).
    2. ``auto_target.json``'s first pending task ``name`` (routine mode pre-claim).
    3. ``STATE.md``'s "Next session work item" block (interactive pre-claim).
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
            "Boot-time MemPalace orchestrator — three formulations + similarity "
            "filter + current_plan.md write. Per ADR 0056 S-0093 amendment "
            "(Issue #38)."
        )
    )
    parser.add_argument("--work-item", type=str, default=None)
    parser.add_argument(
        "--similarity-threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD
    )
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    parser.add_argument("--plan-path", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--current-path", type=Path, default=DEFAULT_CURRENT_PATH)
    parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument(
        "--auto-target-path", type=Path, default=DEFAULT_AUTO_TARGET_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    work_item = args.work_item
    if work_item is None:
        work_item = resolve_work_item(
            args.current_path, args.state_path, args.auto_target_path
        )
    if work_item is None:
        print(
            "[mempalace-boot-search] could not resolve work-item phrase "
            "(no current.json working_on, no auto_target pending task, no "
            "STATE.md 'Next session work item' block). Pass --work-item "
            "explicitly.",
            file=sys.stderr,
        )
        return 1

    formulations = generate_formulations(work_item)
    ts = emit()  # ADR 0058 canonical

    formulations_results: list[tuple[str, str, list[dict[str, Any]]]] = []
    substrate_unreachable = False
    for label, query in formulations:
        drawers = fetch_drawers(
            query=query,
            min_similarity=args.similarity_threshold,
            limit=args.max_results,
        )
        if drawers is None:
            substrate_unreachable = True
            formulations_results.append((label, query, []))
        else:
            formulations_results.append((label, query, drawers))

    section_body = render_section(
        formulations_results, ts, args.similarity_threshold, substrate_unreachable
    )

    if args.dry_run:
        print(section_body)
        return 2 if substrate_unreachable else 0

    write_section(args.plan_path, section_body)
    if not substrate_unreachable:
        append_telemetry(args.jsonl_path, formulations, ts)

    total = sum(len(d) for _, _, d in formulations_results)
    print(
        f"[mempalace-boot-search] formulations=3 threshold={args.similarity_threshold:.2f} "
        f"drawers={total} substrate={'down' if substrate_unreachable else 'up'} "
        f"plan={args.plan_path}",
        flush=True,
    )

    return 2 if substrate_unreachable else 0


if __name__ == "__main__":
    sys.exit(main())
