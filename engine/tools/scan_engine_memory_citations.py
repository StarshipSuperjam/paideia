"""Shutdown-time engine_memory citation scanner — drawer-citation telemetry.

Layer 1 contract per ADR 0091 (S-0193 demolition) — sibling of the
retiring ``scan_mempalace_citations.py``. Same pattern-matching shape,
re-pointed at the engine_memory substrate.

Purpose
-------
ADR 0091's ``engine_memory_activity`` rollup captures per-session call
counts (``search_calls``, ``diary_read_calls``, ``add_drawer_calls``,
etc.) but does NOT capture whether returned drawers actually fed the
session's authoring. Without that signal, "engine_memory is being used"
is observable but "engine_memory is being useful" is not.

This tool runs at shutdown after the diary write and after
``outcome_summary`` is filled. It scans three sources for citation
patterns and writes a nested ``engine_memory_citations`` block under the
existing ``engine_memory_activity`` field in ``current.json``. The
soft-warn ``engine_memory_zero_citations_after_search`` (in ``validate.py
--final-check``) fires when ``search_calls > 0`` AND
``engine_memory_citations.total == 0`` — retrieval happened but produced
no observable behavior change.

Sources scanned
---------------
1. ``outcome_summary`` text in ``engine/session/current.json``.
2. The session's diary entry, retrieved via ``engine.memory.diary.read_recent``
   (the direct-Python entrypoint that ``engine_memory_diary_read`` MCP tool
   wraps). Substrate-unreachable yields empty.
3. Commit messages from ``git log <eager-claim-sha>..HEAD --format=%B``
   (eager-claim SHA detected by the same regex the parent
   ``scan_mempalace_citations.py`` used).

Pattern matching
----------------
- ``DRAWER_ID_PATTERN``: matches engine_memory's uuid4-style hex drawer
  IDs (32-char lowercase hex, optionally surrounded by punctuation),
  AND the legacy chromadb-internal ``drawer_paideia_<hash>`` forms in
  citations of historical content. The dual pattern preserves
  citation-counting continuity for migrated drawers whose
  ``lineage.imported_from`` still carries the old ID.
- ``SESSION_ARCHIVE_PATTERN``: matches ``per S-NNNN``, ``from S-NNNN``,
  ``at S-NNNN``, ``in S-NNNN``, ``see S-NNNN``, ``S-NNNN's <noun>``.
- ``TAG_NAMED_PATTERN``: matches ``per pushback drawer``, ``per lesson
  drawer``, ``per decision drawer``.

Counts dedupe within a single source (overlapping matches in the same
text count once); summed across sources.

Field shape
-----------

::

    "engine_memory_citations": {
        "drawer_id_refs": int,
        "session_archive_refs": int,
        "tag_named_refs": int,
        "total": int
    }

Nested under ``engine_memory_activity``; ``audit_archive_structured_fields.py``
already declares ``engine_memory_activity`` as a required structured
field.

Idempotent — re-running overwrites the nested block.

Exit codes
----------
- ``0`` — citations scanned (or dry-run printed).
- Non-zero reserved for future use.

Out of scope
------------
- Retroactive backfill of pre-S-0193 archives. Citation telemetry under
  ``engine_memory_citations`` begins S-0193 forward; pre-S-0193 archives
  carry the equivalent under ``mempalace_citations``.
- Counting which specific drawer IDs are cited (only counts, not
  surface).
- Deduplication across sources (a drawer ID appearing in both
  outcome_summary and diary counts twice — different consumption paths).

Cross-references
----------------
- ADR 0091 (S-0188; S-0193 demolition) — the engine-memory substrate.
- ADR 0042 — the soft-warn lifecycle the
  ``engine_memory_zero_citations_after_search`` category participates in.
- ADR 0049 — per-session ``scope_delivery`` audit pattern this scanner
  follows.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"

# Matches both modern engine_memory uuid4 hex IDs (32-char lowercase
# hex) AND legacy chromadb drawer_ prefixed IDs — the former is what
# engine_memory_add_drawer writes; the latter still appears in
# citations of historical content via lineage.imported_from.
DRAWER_ID_PATTERN = re.compile(
    r"\b(?:[a-f0-9]{32}|drawer_[a-z][a-z0-9_]*_[a-f0-9]{16,})\b"
)
SESSION_ARCHIVE_PATTERN = re.compile(
    r"(?:\b(?:per|from|at|in|see)\s+S-(\d{4})\b|\bS-(\d{4})'s\b)",
    re.IGNORECASE,
)
TAG_NAMED_PATTERN = re.compile(
    r"\bper\s+(pushback|lesson|decision)\s+drawer\b", re.IGNORECASE
)
EAGER_CLAIM_PATTERN = re.compile(
    r"^chore\(session\): eager-claim S-\d{4}\b", re.MULTILINE
)


def _count_unique_matches(text: str, pattern: re.Pattern[str]) -> int:
    """Count distinct matches (deduped per-source) returned by `pattern`."""
    matches = pattern.findall(text)
    if not matches:
        return 0
    flat: list[str] = []
    for m in matches:
        if isinstance(m, tuple):
            flat.append(next((p for p in m if p), ""))
        else:
            flat.append(m)
    return len({m.lower() for m in flat if m})


def scan_text(text: str) -> dict[str, int]:
    """Return per-pattern counts for a single source string."""
    return {
        "drawer_id_refs": _count_unique_matches(text, DRAWER_ID_PATTERN),
        "session_archive_refs": _count_unique_matches(text, SESSION_ARCHIVE_PATTERN),
        "tag_named_refs": _count_unique_matches(text, TAG_NAMED_PATTERN),
    }


def _sum_counts(counts_list: list[dict[str, int]]) -> dict[str, int]:
    """Sum per-pattern counts across sources; compute total."""
    summed: dict[str, int] = {
        "drawer_id_refs": 0,
        "session_archive_refs": 0,
        "tag_named_refs": 0,
    }
    for c in counts_list:
        for k in summed:
            summed[k] += int(c.get(k, 0))
    summed["total"] = (
        summed["drawer_id_refs"]
        + summed["session_archive_refs"]
        + summed["tag_named_refs"]
    )
    return summed


def fetch_today_diary(agent_name: str = "claude") -> str:
    """Return today's diary content for `agent_name` from engine_memory.

    Direct-Python read via ``engine.memory.diary.read_entries``; the
    engine_memory_diary_read MCP tool wraps the same function.
    Substrate-unreachable (ImportError or runtime exception) yields
    empty.
    """
    try:
        from engine.memory.diary import read_entries
    except ImportError:
        return ""
    try:
        entries = read_entries(agent_name=agent_name, last_n=3)
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"[scan-engine-memory-citations] diary.read_entries raised "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return ""
    if not isinstance(entries, list):
        return ""
    # Today's date in UTC (engine_memory diary uses datetime('now')
    # which is UTC by default in SQLite, per engine/memory/schema.py).
    today_str = datetime.now(timezone.utc).date().isoformat()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        created = entry.get("created_at", "")
        if isinstance(created, str) and created.startswith(today_str):
            content = entry.get("content")
            if isinstance(content, str):
                return content
    return ""


def fetch_session_commit_messages(repo_root: Path) -> str:
    """Return commit messages from eager-claim..HEAD as a single string.

    Walks ``git log -n 50 --format=%H<TAB>%s%n%b`` to find the eager-claim
    commit; concatenates every commit's full message between that SHA
    and HEAD. Returns empty string when no eager-claim is in recent
    history (typical pre-claim or non-session contexts).
    """
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "log",
                "--format=%H%n%s%n%b%n--END--",
                "-n",
                "50",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

    commits: list[tuple[str, str]] = []
    for block in result.stdout.split("--END--"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n", 1)
        sha = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if sha:
            commits.append((sha, body))

    eager_idx: int | None = None
    for i, (_sha, body) in enumerate(commits):
        if EAGER_CLAIM_PATTERN.search(body):
            eager_idx = i
            break
    if eager_idx is None:
        return ""

    return "\n\n".join(body for _sha, body in commits[:eager_idx])


def write_citations_to_current(current_path: Path, citations: dict[str, int]) -> None:
    """Update current.json's engine_memory_activity with the citations block."""
    if not current_path.is_file():
        raise FileNotFoundError(f"current.json not found at {current_path}")
    data: dict[str, Any] = json.loads(current_path.read_text(encoding="utf-8"))
    activity = data.get("engine_memory_activity")
    if not isinstance(activity, dict):
        activity = {}
    activity["engine_memory_citations"] = citations
    data["engine_memory_activity"] = activity
    current_path.write_text(json.dumps(data, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan session-authored artifacts (outcome_summary + diary + "
            "commit messages) for engine_memory drawer citations; write "
            "the nested engine_memory_citations block under "
            "engine_memory_activity. Per ADR 0091 (S-0193 demolition)."
        )
    )
    parser.add_argument("--current-path", type=Path, default=DEFAULT_CURRENT_PATH)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--agent-name", type=str, default="claude")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.current_path.is_file():
        print(
            f"[scan-engine-memory-citations] {args.current_path} not found; "
            "no in-flight session — nothing to scan.",
            flush=True,
        )
        return 0

    current = json.loads(args.current_path.read_text(encoding="utf-8"))
    outcome_summary = current.get("outcome_summary") or ""
    if not isinstance(outcome_summary, str):
        outcome_summary = ""

    diary_text = fetch_today_diary(agent_name=args.agent_name)
    git_text = fetch_session_commit_messages(args.repo_root)

    per_source = [
        scan_text(outcome_summary),
        scan_text(diary_text),
        scan_text(git_text),
    ]
    citations = _sum_counts(per_source)

    print(
        f"[scan-engine-memory-citations] "
        f"drawer_id_refs={citations['drawer_id_refs']} "
        f"session_archive_refs={citations['session_archive_refs']} "
        f"tag_named_refs={citations['tag_named_refs']} "
        f"total={citations['total']} "
        f"sources={'outcome' if outcome_summary else '-'},"
        f"{'diary' if diary_text else '-'},"
        f"{'git' if git_text else '-'}",
        flush=True,
    )

    if args.dry_run:
        return 0

    write_citations_to_current(args.current_path, citations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
