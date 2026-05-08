"""Detect mid-session collision before claiming a new slot.

When a routine-mode session is in flight and a user starts an interactive
``/start-engine`` session, the interactive session would otherwise overwrite
the routine's ``current.json`` and ``register_state.json`` and corrupt the
routine's archive. This tool inspects the in-flight state and emits an
informative surface so the boot procedure can refuse (interactive) or
surface the warning (the SessionStart hook).

Intended call sites:

- ``engine/tools/hooks/session-start.sh`` — informational surface; the hook
  always exits 0 per its "never blocks" design, so the exit code is logged
  but doesn't stop boot.
- ``.claude/commands/start-engine.md`` boot procedure step 4b — the AI runs
  the tool before the eager-claim ritual; on exit 1 (recent collision /
  ambiguous mid-window) the AI refuses to claim and asks the user to
  coordinate; on exit 2 (stale session) the AI offers auto-recovery.

Disposition windows (configurable via CLI flags):

- **No conflict**: ``current_status != "in_progress"``, or ``current.json``
  is absent, or the timestamp cannot be parsed. Exit 0.
- **Recent collision**: ``in_progress`` and the in-flight session was
  claimed less than ``--recent-window-seconds`` ago (default 3600s).
  Exit 1. Surface: refuse + cite the cooperation procedure.
- **Mid-window ambiguity**: ``in_progress`` between recent and stale.
  Exit 1. Surface: ambiguous, prompt the user.
- **Stale**: ``in_progress`` for longer than ``--stale-window-seconds``
  (default 86400s = 24h). Exit 2. Surface: offer auto-recovery.

Per Issue #3 (S-0048).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import parse  # noqa: E402  # ADR 0058

DEFAULT_RECENT_WINDOW_SECONDS = 3600
DEFAULT_STALE_WINDOW_SECONDS = 86400

REGISTER_PATH = "engine/session/register_state.json"
CURRENT_PATH = "engine/session/current.json"


def parse_started_at(s: str) -> datetime | None:
    """Parse ISO-8601 UTC timestamps written by the eager-claim ritual.

    Accepts both ``2026-05-04T17:30:03Z`` and ``...+00:00`` forms. Returns
    ``None`` on malformed input — the caller treats that as "no conflict
    signal" rather than crashing the hook.
    """
    if not s:
        return None
    s = s.strip()
    try:
        return parse(s)  # ADR 0058 — tolerant of Z and +00:00 shapes
    except (ValueError, TypeError):
        return None


def check(
    repo_root: Path,
    *,
    now: datetime | None = None,
    recent_window: int = DEFAULT_RECENT_WINDOW_SECONDS,
    stale_window: int = DEFAULT_STALE_WINDOW_SECONDS,
) -> tuple[int, str]:
    """Inspect register_state.json + current.json; return ``(exit_code, message)``."""
    register_file = repo_root / REGISTER_PATH
    current_file = repo_root / CURRENT_PATH

    if not register_file.is_file():
        return 0, "no register_state.json — nothing to check"

    try:
        register = json.loads(register_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return 0, f"register_state.json read error: {exc}; not blocking"

    if register.get("current_status") != "in_progress":
        return 0, "current_status: closed (or absent) — no conflict"

    if not current_file.is_file():
        return 0, (
            "register says in_progress but engine/session/current.json is "
            "absent — anomalous state; consider clearing "
            "register_state.json's current_status manually"
        )

    try:
        current = json.loads(current_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return 0, f"current.json read error: {exc}; not blocking"

    rival_id = current.get("id", "<unknown>")
    started_at_raw = current.get("started_at", "")
    started_at = parse_started_at(started_at_raw)
    if started_at is None:
        return 0, (
            f"current.json's started_at could not be parsed "
            f"('{started_at_raw}'); treat {rival_id} as ambiguous"
        )

    if now is None:
        now = datetime.now(timezone.utc)
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    delta_seconds = int((now - started_at).total_seconds())
    if delta_seconds < 0:
        delta_seconds = 0

    if delta_seconds < recent_window:
        minutes = delta_seconds // 60
        msg = (
            "============================================================\n"
            f"[check_session_conflict] RECENT collision: {rival_id} in_progress\n"
            "============================================================\n"
            f"Session {rival_id} started {started_at_raw} "
            f"({minutes} minute(s) ago).\n"
            "Concurrent sessions corrupt shared state. Do NOT claim a "
            "new slot.\n"
            "\n"
            "Options:\n"
            "  1. Wait for the in-flight session to close (check "
            "engine/session/archive\n"
            "     for the rival's archive entry, then retry).\n"
            "  2. Pause the routine: edit engine/session/auto_target.json, "
            "set\n"
            "     `paused: true`, commit, and the routine won't fire again.\n"
            "  3. See engine/operations/routine-mode-operations.md\n"
            "     'Mixing interactive and routine sessions' for the\n"
            "     cooperation procedure.\n"
            "============================================================"
        )
        return 1, msg

    if delta_seconds < stale_window:
        hours = delta_seconds // 3600
        msg = (
            "============================================================\n"
            f"[check_session_conflict] AMBIGUOUS in_progress: {rival_id} "
            f"({hours}h ago)\n"
            "============================================================\n"
            f"Session {rival_id} started {started_at_raw} — between the "
            "recent (<1h)\n"
            "and stale (>24h) windows.\n"
            "\n"
            "If the rival is still actively running, do NOT claim a new "
            "slot —\n"
            "concurrent sessions corrupt shared state. If the rival is dead\n"
            "(force-killed, machine rebooted, etc.), manually edit\n"
            "engine/session/register_state.json to set current_status: "
            "'closed'\n"
            "and re-run the boot procedure.\n"
            "============================================================"
        )
        return 1, msg

    days = delta_seconds // 86400
    msg = (
        "============================================================\n"
        f"[check_session_conflict] STALE in_progress: {rival_id} "
        f"({days}d ago)\n"
        "============================================================\n"
        f"Session {rival_id} started {started_at_raw} ({days} day(s) ago) "
        "and never\n"
        "closed. Almost certainly a dead session (force-killed, machine "
        "rebooted,\n"
        "etc.) rather than an actively-running rival.\n"
        "\n"
        "Recovery: manually edit engine/session/register_state.json to set\n"
        "current_status: 'closed', archive engine/session/current.json to\n"
        f"engine/session/archive/{rival_id}.json with closed_partial status\n"
        "and a note in outcome_summary, then re-run the boot procedure.\n"
        "============================================================"
    )
    return 2, msg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Detect mid-session collision before claiming a new slot."),
    )
    parser.add_argument(
        "--repo-root",
        default=os.environ.get("REPO_ROOT", "."),
        help="Repo root (default: REPO_ROOT env var or .)",
    )
    parser.add_argument(
        "--recent-window-seconds",
        type=int,
        default=DEFAULT_RECENT_WINDOW_SECONDS,
        help=(
            "Recent-collision window in seconds "
            f"(default {DEFAULT_RECENT_WINDOW_SECONDS})"
        ),
    )
    parser.add_argument(
        "--stale-window-seconds",
        type=int,
        default=DEFAULT_STALE_WINDOW_SECONDS,
        help=(
            f"Stale-session window in seconds (default {DEFAULT_STALE_WINDOW_SECONDS})"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational surface; return exit code only",
    )
    args = parser.parse_args(argv)

    exit_code, message = check(
        Path(args.repo_root),
        recent_window=args.recent_window_seconds,
        stale_window=args.stale_window_seconds,
    )
    if not args.quiet:
        if exit_code == 0:
            print(f"[check_session_conflict] {message}")
        else:
            print(message, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
