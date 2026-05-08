"""Shutdown-time MemPalace citation scanner — drawer-citation telemetry.

Layer 1 contract per ADR 0056 (S-0093 amendment, Issue #39).

Purpose
-------
ADR 0056 (S-0078) captures per-session call counts (``search_calls``,
``diary_read_calls``, ``diary_write_calls``, ``add_drawer_calls``). It
does not capture whether returned drawers actually fed the session's
authoring — i.e., whether retrieval altered what the session did.

Without that signal, "MemPalace is being used" is observable but
"MemPalace is being useful" is not. A session can pass S-0078's adoption
checks while drawing zero behavioral value from MemPalace.

This tool runs at shutdown after the diary write and after
``outcome_summary`` is filled. It scans three sources for citation
patterns and writes a nested ``mempalace_citations`` block under the
existing ``mempalace_activity`` field in ``current.json``. The new
soft-warn ``mempalace_zero_citations_after_search`` (in ``validate.py
--final-check``) fires when ``search_calls > 0`` AND
``mempalace_citations.total == 0`` — retrieval happened but produced no
observable behavior change.

Sources scanned
---------------
1. ``outcome_summary`` text in ``engine/session/current.json``.
2. The session's diary entry, retrieved via
   ``mempalace.mcp_server.tool_diary_read(agent_name="claude", last_n=1)``
   and matched on today's date. Best-effort; substrate-unreachable yields
   empty.
3. Commit messages from ``git log <eager-claim-sha>..HEAD --format=%B``
   (eager-claim SHA detected by the same regex
   ``audit_archive_structured_fields.py`` uses).

Pattern matching
----------------
- ``DRAWER_ID_PATTERN``: matches ``drawer_paideia_<hash>``,
  ``drawer_wing_paideia_<hash>``, etc. — chromadb-internal drawer IDs
  whenever they surface in authored text.
- ``SESSION_ARCHIVE_PATTERN``: matches ``per S-NNNN``, ``from S-NNNN``,
  ``at S-NNNN``, and ``S-NNNN's <noun>`` forms.
- ``TAG_NAMED_PATTERN``: matches ``per pushback drawer``, ``per lesson
  drawer``, ``per decision drawer``.

Counts (overlapping matches not double-counted within a single source).

Field shape
-----------

::

    "mempalace_citations": {
        "drawer_id_refs": int,
        "session_archive_refs": int,
        "tag_named_refs": int,
        "total": int
    }

Nested under ``mempalace_activity``; the existing
``REQUIRED_ARCHIVE_FIELDS`` row in
``audit_archive_structured_fields.py`` covers it without code change.

Idempotent — re-running overwrites the nested block.

Exit codes
----------
- ``0`` — citations scanned (or dry-run printed).
- The non-zero path is reserved.

Out of scope
------------
- Retroactive backfill of pre-S-0093 archives. Citation telemetry begins
  S-0093 forward.
- Counting which specific drawer IDs are cited (only counts, not surface).
- Deduplication across sources (a drawer ID appearing in both
  outcome_summary and diary counts twice — different consumption paths).

Cross-references
----------------
- ADR 0056 (S-0078; S-0093 amendment) — the contract.
- ADR 0042 — the soft-warn lifecycle the new
  ``mempalace_zero_citations_after_search`` category participates in.
- ADR 0049 — per-session ``scope_delivery`` audit pattern this scanner
  follows.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"

DRAWER_ID_PATTERN = re.compile(r"\bdrawer_[a-z][a-z0-9_]*_[a-f0-9]{16,}\b")
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
    """Return today's diary entry content for `agent_name`, or empty string.

    Imports ``mempalace.mcp_server.tool_diary_read`` lazily; substrate-
    unreachable (ImportError or runtime exception) yields empty.
    """
    try:
        from mempalace.mcp_server import tool_diary_read
    except ImportError:
        return ""
    try:
        result = tool_diary_read(agent_name=agent_name, last_n=3)
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"[scan-mempalace-citations] tool_diary_read raised "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return ""
    if not isinstance(result, dict):
        return ""
    # NOT routed through timestamps.today() per ADR 0058 — MemPalace diary
    # entries carry palace-naive local-date semantics (palace storage is
    # naive local time per audit_mempalace_attribution.py:_parse_palace_dt).
    # Matching against UTC date would silently miss entries written at
    # local times near the UTC date boundary. The file is allowlisted in
    # validate.py's _TIMESTAMP_HELPER_BYPASS_ALLOWLIST for this reason.
    today_str = _dt.date.today().isoformat()
    entries = result.get("entries")
    if not isinstance(entries, list):
        return ""
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("date") == today_str:
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
    """Update current.json's mempalace_activity with the nested citations block."""
    if not current_path.is_file():
        raise FileNotFoundError(f"current.json not found at {current_path}")
    data: dict[str, Any] = json.loads(current_path.read_text(encoding="utf-8"))
    activity = data.get("mempalace_activity")
    if not isinstance(activity, dict):
        activity = {}
    activity["mempalace_citations"] = citations
    data["mempalace_activity"] = activity
    current_path.write_text(json.dumps(data, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan session-authored artifacts (outcome_summary + diary + "
            "commit messages) for MemPalace drawer citations; write the "
            "nested mempalace_citations block under mempalace_activity. "
            "Per ADR 0056 S-0093 amendment (Issue #39)."
        )
    )
    parser.add_argument("--current-path", type=Path, default=DEFAULT_CURRENT_PATH)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--agent-name", type=str, default="claude")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.current_path.is_file():
        print(
            f"[scan-mempalace-citations] {args.current_path} not found; "
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
        f"[scan-mempalace-citations] drawer_id_refs={citations['drawer_id_refs']} "
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
