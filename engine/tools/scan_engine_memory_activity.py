"""Roll per-session engine_memory MCP-call telemetry into current.json at shutdown.

Layer 1 contract per ADR 0091 (engine-memory substrate). Sibling of
``scan_mempalace_activity.py`` per ADR 0091 Decision 5 (the 6-tool MCP
surface ceiling).

Purpose
-------
The PostToolUse hook at
``engine/tools/hooks/post-engine-memory-tool-use.sh`` writes one JSONL
line per ``mcp__engine_memory__*`` invocation to
``engine/session/current_engine_memory.jsonl`` over the session's
lifetime. This tool reads that file at shutdown, counts calls per
tool, and writes a structured ``engine_memory_activity`` field into
``engine/session/current.json`` so the archive carries the telemetry
forward into the canonical record.

Runs at session-shutdown step 2 (after the diary write at step 1,
before the audit pass at step 3). Mirrors the shutdown ordering of
``scan_mempalace_activity.py``.

Field shape
-----------
::

    "engine_memory_activity": {
        "search_calls": int,
        "add_drawer_calls": int,
        "get_drawer_calls": int,
        "list_drawers_calls": int,
        "diary_read_calls": int,
        "diary_write_calls": int,
        "other_calls": int,
        "total_calls": int,
        "first_call_ts": str | null,
        "last_call_ts": str | null,
        "search_first_ts": str | null,
        "diary_read_first_ts": str | null
    }

Six named buckets correspond exactly to the ADR 0091 Decision 5
ceiling. Any tool falling outside the six-tool ceiling lands in
``other_calls`` (defense-in-depth — should never fire under the
ceiling, but catches drift if a future ADR amends or supersedes).

Per-tool first-timestamps follow the Issue #124 (S-0160) precedent:
the boot-search and diary-read MCP calls run *before* the eager-claim
ritual stamps ``started_at`` on ``current.json``; a first-call ts that
postdates ``started_at`` signals a boot step that ran late. Tracked
explicitly here so ``validate.py --final-check`` can emit the
``engine_memory_boot_query_late`` / ``engine_memory_diary_read_late``
soft-warns sibling to their mempalace_ predecessors.

Downstream
----------
- ``validate.py --final-check`` reads ``engine_memory_activity`` and
  applies the 3-soft-warn + 1-hard-fail adoption-check categories
  (see ``validate_engine_memory_adoption`` in
  ``engine/tools/validate.py``).
- ``audit_archive_structured_fields.py`` declares
  ``engine_memory_activity`` in ``REQUIRED_ARCHIVE_FIELDS`` since
  S-0192; the closing-commit hook hard-fails any archive that lacks
  it after this session.

Cleanup
-------
After successfully writing the rollup into ``current.json``, this
tool truncates ``current_engine_memory.jsonl`` to zero bytes so the
next session's PostToolUse hook starts from a clean baseline.
Mirrors the ``scan_mempalace_activity.py`` per-session-truncation
contract (Issue #37 / S-0083).

Per S-0089 merge-don't-replace fix carried over: if
``engine_memory_activity`` already exists in ``current.json``, the
new rollup is merged (counts summed; first/last ts spanned) rather
than replacing — supports multiple scan invocations within a single
session without losing earlier counts.

Exit codes
----------
- ``0`` — telemetry rolled up (or JSONL absent — wrote zero-counts).

CLI
---
- ``scan_engine_memory_activity.py`` — auto-detect, write to
  current.json, truncate JSONL.
- ``scan_engine_memory_activity.py --dry-run`` — compute and print,
  no write, no truncation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL_PATH = REPO_ROOT / "engine" / "session" / "current_engine_memory.jsonl"
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"

# Mapping of engine_memory MCP tool names to rollup-field keys. Six
# tools total, matching the ADR 0091 Decision 5 ceiling. Anything else
# falls into ``other_calls``.
TOOL_KEY_MAP: dict[str, str] = {
    "mcp__engine_memory__engine_memory_search": "search_calls",
    "mcp__engine_memory__engine_memory_add_drawer": "add_drawer_calls",
    "mcp__engine_memory__engine_memory_get_drawer": "get_drawer_calls",
    "mcp__engine_memory__engine_memory_list_drawers": "list_drawers_calls",
    "mcp__engine_memory__engine_memory_diary_read": "diary_read_calls",
    "mcp__engine_memory__engine_memory_diary_write": "diary_write_calls",
}

EMPTY_ROLLUP: dict[str, Any] = {
    "search_calls": 0,
    "add_drawer_calls": 0,
    "get_drawer_calls": 0,
    "list_drawers_calls": 0,
    "diary_read_calls": 0,
    "diary_write_calls": 0,
    "other_calls": 0,
    "total_calls": 0,
    "first_call_ts": None,
    "last_call_ts": None,
    "search_first_ts": None,
    "diary_read_first_ts": None,
}

# Per-tool first-call timestamps — sibling to PER_TOOL_FIRST_TS_MAP in
# scan_mempalace_activity.py. Used by validate.py to detect late boot
# calls.
PER_TOOL_FIRST_TS_MAP: dict[str, str] = {
    "search_first_ts": "mcp__engine_memory__engine_memory_search",
    "diary_read_first_ts": "mcp__engine_memory__engine_memory_diary_read",
}


def rollup_jsonl(jsonl_path: Path) -> dict[str, Any]:
    """Read JSONL telemetry and return the structured rollup dict."""
    rollup: dict[str, Any] = dict(EMPTY_ROLLUP)
    if not jsonl_path.is_file():
        return rollup

    first_ts: str | None = None
    last_ts: str | None = None
    per_tool_first: dict[str, str] = {}

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue

            tool = entry.get("tool")
            ts = entry.get("ts")

            if isinstance(tool, str):
                key = TOOL_KEY_MAP.get(tool, "other_calls")
                rollup[key] = int(rollup.get(key, 0)) + 1
                rollup["total_calls"] = int(rollup["total_calls"]) + 1

            if isinstance(ts, str) and ts:
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts
                if isinstance(tool, str):
                    existing = per_tool_first.get(tool)
                    if existing is None or ts < existing:
                        per_tool_first[tool] = ts

    rollup["first_call_ts"] = first_ts
    rollup["last_call_ts"] = last_ts
    for rollup_key, tool_name in PER_TOOL_FIRST_TS_MAP.items():
        rollup[rollup_key] = per_tool_first.get(tool_name)
    return rollup


def _merge_rollups(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Merge new rollup into existing — sum counts, span timestamps.

    Mirrors scan_mempalace_activity._merge_rollups per S-0089 fix.
    """
    if not isinstance(existing, dict):
        return new

    merged: dict[str, Any] = dict(existing)
    for key, value in new.items():
        if (key.endswith("_calls") or key == "total_calls") and isinstance(value, int):
            existing_value = existing.get(key, 0)
            if isinstance(existing_value, int):
                merged[key] = existing_value + value
            else:
                merged[key] = value
        elif key == "first_call_ts":
            existing_ts = existing.get("first_call_ts")
            if value is None:
                merged[key] = existing_ts
            elif existing_ts is None:
                merged[key] = value
            else:
                merged[key] = existing_ts if existing_ts < value else value
        elif key == "last_call_ts":
            existing_ts = existing.get("last_call_ts")
            if value is None:
                merged[key] = existing_ts
            elif existing_ts is None:
                merged[key] = value
            else:
                merged[key] = existing_ts if existing_ts > value else value
        elif key.endswith("_first_ts"):
            existing_ts = existing.get(key)
            if value is None:
                merged[key] = existing_ts
            elif existing_ts is None:
                merged[key] = value
            else:
                merged[key] = existing_ts if existing_ts < value else value
        else:
            merged[key] = value
    return merged


def write_rollup_to_current(current_path: Path, rollup: dict[str, Any]) -> None:
    """Update current.json with the rollup in ``engine_memory_activity``."""
    if not current_path.is_file():
        raise FileNotFoundError(f"current.json not found at {current_path}")
    data: dict[str, Any] = json.loads(current_path.read_text())
    existing = data.get("engine_memory_activity")
    merged = _merge_rollups(existing, rollup) if isinstance(existing, dict) else rollup
    data["engine_memory_activity"] = merged
    current_path.write_text(json.dumps(data, indent=2) + "\n")


def truncate_jsonl(jsonl_path: Path) -> None:
    """Truncate the JSONL telemetry file to zero bytes."""
    if jsonl_path.is_file():
        jsonl_path.write_text("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Roll engine/session/current_engine_memory.jsonl into the "
            "engine_memory_activity field of engine/session/current.json. "
            "Per ADR 0091 (engine-memory substrate)."
        ),
    )
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=DEFAULT_JSONL_PATH,
        help=(
            "JSONL telemetry path (default: "
            "engine/session/current_engine_memory.jsonl)."
        ),
    )
    parser.add_argument(
        "--current-path",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="current.json path (default: engine/session/current.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print the rollup; do not write to current.json.",
    )
    args = parser.parse_args(argv)

    jsonl_path: Path = args.jsonl
    current_path: Path = args.current_path

    rollup = rollup_jsonl(jsonl_path)

    print(
        f"[scan-engine-memory-activity] total_calls={rollup['total_calls']} "
        f"search={rollup['search_calls']} "
        f"diary_read={rollup['diary_read_calls']} "
        f"diary_write={rollup['diary_write_calls']} "
        f"add_drawer={rollup['add_drawer_calls']} "
        f"first={rollup['first_call_ts']} last={rollup['last_call_ts']} "
        f"search_first={rollup['search_first_ts']} "
        f"diary_read_first={rollup['diary_read_first_ts']}",
        flush=True,
    )

    if args.dry_run:
        return 0

    try:
        write_rollup_to_current(current_path, rollup)
    except FileNotFoundError as exc:
        print(
            f"[scan-engine-memory-activity] {exc}; cannot write rollup.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    truncate_jsonl(jsonl_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
