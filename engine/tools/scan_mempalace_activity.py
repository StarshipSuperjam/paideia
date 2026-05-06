"""Roll per-session MemPalace MCP-call telemetry into current.json at shutdown.

Layer 1 contract per ADR 0056 (engine; this session — MemPalace mechanical
adoption checks).

Purpose
-------
The PostToolUse hook at engine/tools/hooks/post-mempalace-tool-use.sh writes
one JSONL line per ``mcp__mempalace__*`` invocation to
``engine/session/current_mempalace.jsonl`` over the session's lifetime. This
tool reads that file at shutdown, counts calls per tool, and writes a
structured ``mempalace_activity`` field into engine/session/current.json so
the archive carries the telemetry forward into the canonical record.

Symmetric in shape to ``scan_context_telemetry.py`` — that tool writes
transcript-token telemetry; this tool writes MemPalace-call telemetry. Both
run at session-shutdown step 7b before validate.py's final-check audit and
before the archive ritual.

The field shape:

::

    "mempalace_activity": {
        "search_calls": int,
        "diary_read_calls": int,
        "diary_write_calls": int,
        "add_drawer_calls": int,
        "status_calls": int,
        "list_drawers_calls": int,
        "other_calls": int,
        "total_calls": int,
        "first_call_ts": str | null,
        "last_call_ts": str | null
    }

Downstream:

- ``validate.py --final-check`` reads ``mempalace_activity`` and applies
  the three adoption-check categories (boot query, diary read, diary write
  — see the ADR for severity).
- ``audit_archive_structured_fields.py`` declares ``mempalace_activity``
  in ``REQUIRED_ARCHIVE_FIELDS`` since S-0078; the closing-commit hook
  hard-fails any archive that lacks it.

Cleanup
-------
After successfully writing the rollup into ``current.json``, this tool
truncates ``current_mempalace.jsonl`` to zero bytes so the next session's
PostToolUse hook starts from a clean baseline. The truncation only fires
on the success path — if the rollup write fails (e.g., ``current.json``
absent), the JSONL stays intact for recovery. Per Issue #37 (S-0083): the
JSONL was previously appended-to indefinitely across sessions, inflating
each archive's ``mempalace_activity`` field with prior-session calls.
Per-session truncation closes that defect.

Re-running this tool is idempotent in shape — it overwrites
``mempalace_activity`` with the current rollup. After the first run
within a session, the JSONL is empty, so a second run produces the empty
rollup and writes that into ``current.json``. The shutdown sequence's
single invocation is the intended call site; manual re-runs (rare) reset
``mempalace_activity`` to zero counts.

If the JSONL file is absent (no MemPalace MCP calls fired this session),
write the field with all zero counts and null timestamps. No truncation
is necessary in that path. The validate audit interprets zero-counts
according to the ADR's severity rules.

Exit codes
----------
- ``0`` — telemetry rolled up (or JSONL absent — wrote zero-counts).
- The non-zero path is reserved.

CLI
---
- ``scan_mempalace_activity.py`` — auto-detect, write to current.json.
- ``scan_mempalace_activity.py --jsonl PATH`` — explicit JSONL path.
- ``scan_mempalace_activity.py --repo-root PATH`` — override repo root.
- ``scan_mempalace_activity.py --dry-run`` — compute and print, no write.

Out of scope
------------
- No backfill of historical archives. Telemetry begins from S-0078 forward.
- No per-call retention. Only counts + first/last timestamps survive past
  the JSONL deletion at archive time.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL_PATH = REPO_ROOT / "engine" / "session" / "current_mempalace.jsonl"
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"

# Mapping of mempalace MCP tool names to the rollup-field key used in
# mempalace_activity. Tools not in this map fall into "other_calls" so the
# rollup remains exhaustive even if a future MemPalace release adds tools
# the project doesn't yet name explicitly.
TOOL_KEY_MAP: dict[str, str] = {
    "mcp__mempalace__mempalace_search": "search_calls",
    "mcp__mempalace__mempalace_diary_read": "diary_read_calls",
    "mcp__mempalace__mempalace_diary_write": "diary_write_calls",
    "mcp__mempalace__mempalace_add_drawer": "add_drawer_calls",
    "mcp__mempalace__mempalace_status": "status_calls",
    "mcp__mempalace__mempalace_list_drawers": "list_drawers_calls",
}

# Empty-rollup template — every count starts at 0; timestamps null.
EMPTY_ROLLUP: dict[str, Any] = {
    "search_calls": 0,
    "diary_read_calls": 0,
    "diary_write_calls": 0,
    "add_drawer_calls": 0,
    "status_calls": 0,
    "list_drawers_calls": 0,
    "other_calls": 0,
    "total_calls": 0,
    "first_call_ts": None,
    "last_call_ts": None,
}


def rollup_jsonl(jsonl_path: Path) -> dict[str, Any]:
    """Read JSONL telemetry and return the structured rollup dict.

    Tolerates malformed lines (skipped silently — the hook may have
    written a partial line during a crash). Returns the empty rollup
    when the file is absent.
    """
    rollup: dict[str, Any] = dict(EMPTY_ROLLUP)
    if not jsonl_path.is_file():
        return rollup

    first_ts: str | None = None
    last_ts: str | None = None

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

    rollup["first_call_ts"] = first_ts
    rollup["last_call_ts"] = last_ts
    return rollup


def write_rollup_to_current(current_path: Path, rollup: dict[str, Any]) -> None:
    """Update current.json with the rollup in the ``mempalace_activity`` field."""
    if not current_path.is_file():
        raise FileNotFoundError(f"current.json not found at {current_path}")
    data: dict[str, Any] = json.loads(current_path.read_text())
    data["mempalace_activity"] = rollup
    current_path.write_text(json.dumps(data, indent=2) + "\n")


def truncate_jsonl(jsonl_path: Path) -> None:
    """Truncate the JSONL telemetry file to zero bytes.

    Called from ``main`` only after ``write_rollup_to_current`` succeeds, so
    the rollup data is already preserved in ``current.json`` before the
    JSONL evidence is cleared. Per Issue #37 (S-0083) — the JSONL had been
    accumulating across sessions, inflating each archive's per-session
    rollup with prior-session calls; this truncation closes that defect.

    Idempotent: absent file is a no-op (the next session's hook will create
    it on first MCP call).
    """
    if jsonl_path.is_file():
        jsonl_path.write_text("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Roll engine/session/current_mempalace.jsonl into the "
            "mempalace_activity field of engine/session/current.json. Per "
            "ADR 0056 (this session)."
        ),
    )
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=DEFAULT_JSONL_PATH,
        help=(
            "JSONL telemetry path (default: engine/session/current_mempalace.jsonl)."
        ),
    )
    parser.add_argument(
        "--current-path",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="current.json path (default: engine/session/current.json).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (defaults to script's repo).",
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
        f"[scan-mempalace-activity] total_calls={rollup['total_calls']} "
        f"search={rollup['search_calls']} "
        f"diary_read={rollup['diary_read_calls']} "
        f"diary_write={rollup['diary_write_calls']} "
        f"add_drawer={rollup['add_drawer_calls']} "
        f"first={rollup['first_call_ts']} last={rollup['last_call_ts']}",
        flush=True,
    )

    if args.dry_run:
        return 0

    try:
        write_rollup_to_current(current_path, rollup)
    except FileNotFoundError as exc:
        print(
            f"[scan-mempalace-activity] {exc}; cannot write rollup.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    truncate_jsonl(jsonl_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
