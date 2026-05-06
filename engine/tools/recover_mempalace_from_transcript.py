"""Recovery helper: locate transcripts and emit analytical-voice prompts for user-driven MemPalace recovery.

Plan
----
Implements Part B step B3 of the approved plan at
``~/.claude/plans/use-of-mempalace-by-velvety-pebble.md`` (S-0079
execution plan at ``~/.claude/plans/to-continue-to-keen-lemur.md``),
revised at S-0079 after a content-integrity concern surfaced. The
revised guidance lives at
``engine/docs/audits/mempalace-recovery-guide-user-driven.md``.

Direction (revised at S-0079)
------------------------------
Recovery sessions run in **default Claude Code mode** (no
``/start-engine``, no eager-claim, no slot consumption). The user
opens a fresh chat, pastes the prompt this tool emits, the recovering
session reads the transcript and writes drawers/diary in **its own
analytical voice** — NOT impersonating the original session — then
ends naturally. The session counter stays clean.

The ``S-NNNN-recovery-S-XXXX`` attribution shape from the original
plan was rejected because it labels who *wrote* the drawer but not
what the drawer *claims to be*. A future reader could miss the tag
and treat synthetic first-person reflection as authentic primary
signal. The revised prompts use ``added_by: "recovery-observer"`` and
require ``Source: <TARGET> transcript (analytical recovery)`` headers
in drawer bodies.

CLI
---
1. ``--worklist`` / ``--worklist --pending`` — print the prioritized
   list of pending sessions plus their resolved transcript paths (or
   ``unrecoverable: <reason>``).
2. ``--resolve S-NNNN`` — print the resolved transcript path or
   unrecoverable reason for one session (for ad-hoc inspection).
3. ``--prompt S-NNNN`` / ``--prompt S-NNNN --dry-run`` — emit the
   analytical-voice recovery prompt for the user to paste into a
   fresh default-mode session.
4. ``--mark-completed S-NNNN --summary "<short>"`` /
   ``--mark-unrecoverable S-NNNN --reason "<why>"`` — record progress
   at ``engine/docs/audits/mempalace-recovery-progress.md`` (optional;
   the progress file is convenience-tracking, not a hard contract).

Path resolution
---------------
For each archive at ``engine/session/archive/S-NNNN.json``:

- Read the ``worktree`` field. If absent (pre-S-0048 sessions), assume
  the main-repo path.
- Map the worktree path to its Claude Code projects directory under
  ``~/.claude/projects/`` via two strategies:

  1. **Suffix match** (preferred) — find a directory whose name ends
     with the worktree path's last component. This is reliable for
     worktrees because each carries a unique random suffix.
  2. **Full-path encode** (fallback) — replace ``/``, ``.`` and ``_``
     with ``-`` to derive the encoded directory name; check existence.

- Within the matched directory, list ``*.jsonl`` files. Pick the file
  whose ``mtime`` falls within ``[started_at - 30min, closed_at + 30min]``;
  if multiple, pick the one closest to ``closed_at``. If none in
  window, pick the single file (if exactly one) or the largest.

If no directory or no transcript matches → ``unrecoverable``.

Out of scope
------------
- Auto-dispatching subagents to write drawers (rejected at S-0079 for
  the impersonation reason). The wrapper emits prompts; the user
  pastes them into a fresh default-mode session.
- Touching auto-captured drawers (``agent='session-hook'``) — recovery
  targets the deliberate-content gap, not the auto-capture layer.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ARCHIVE_DIR = DEFAULT_REPO_ROOT / "engine" / "session" / "archive"
DEFAULT_PROJECTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_PROGRESS_PATH = (
    DEFAULT_REPO_ROOT / "engine" / "docs" / "audits" / "mempalace-recovery-progress.md"
)
DEFAULT_AUDIT_TOOL = (
    DEFAULT_REPO_ROOT / "engine" / "tools" / "audit_mempalace_attribution.py"
)
CURRENT_SESSION_DEFAULT = "S-0079"

_SID_RE = re.compile(r"^S-(\d{1,4})$")


def parse_sid(label: str) -> int:
    m = _SID_RE.match(label)
    if not m:
        raise ValueError(f"invalid session id {label!r}; expected S-NNNN")
    return int(m.group(1))


def session_str(n: int) -> str:
    return f"S-{n:04d}"


def encode_worktree_path(path: str) -> str:
    """Replace ``/``, ``.``, ``_`` with ``-`` to match Claude Code's
    transcripts-directory naming. Empirically validated against
    actual paths in ``~/.claude/projects/``."""
    return re.sub(r"[/._]", "-", path)


@dataclass
class TranscriptResolution:
    session_id: int
    transcript_path: Path | None
    project_dir: Path | None
    reason: str | None  # if unresolved
    candidates: list[Path]


def find_project_dir(
    worktree_path: str | None, projects_dir: Path
) -> tuple[Path | None, str | None]:
    """Find the ~/.claude/projects/<encoded>/ directory for a worktree path.

    Returns ``(dir, reason_or_None)``. Reason populated if not found.
    """
    if not worktree_path:
        return None, "worktree_field_absent"
    if not projects_dir.is_dir():
        return None, "projects_dir_missing"
    encoded = encode_worktree_path(worktree_path)
    candidate = projects_dir / encoded
    if candidate.is_dir():
        return candidate, None
    last_component = Path(worktree_path).name
    matches = [
        p
        for p in projects_dir.iterdir()
        if p.is_dir() and p.name.endswith(last_component)
    ]
    if len(matches) == 1:
        return matches[0], None
    if len(matches) > 1:
        return None, f"ambiguous_suffix_match:{len(matches)}"
    return None, "no_matching_project_dir"


def pick_transcript(
    project_dir: Path,
    started_at: datetime | None,
    closed_at: datetime | None,
) -> tuple[Path | None, list[Path], str | None]:
    """Pick the most plausible transcript ``.jsonl`` for the session window.

    Strategy:
    1. List all ``*.jsonl`` files in the project dir (non-recursive).
    2. If exactly one, return it.
    3. Otherwise prefer files whose ``mtime`` falls in
       ``[started_at - 30min, closed_at + 30min]``. Among those pick
       the one with mtime closest to ``closed_at``.
    4. Fall back to the largest file.
    """
    candidates = sorted(project_dir.glob("*.jsonl"))
    if not candidates:
        return None, [], "no_transcripts_in_project_dir"
    if len(candidates) == 1:
        return candidates[0], candidates, None
    in_window: list[tuple[float, Path]] = []
    if started_at is not None and closed_at is not None:
        lo = started_at - timedelta(minutes=30)
        hi = closed_at + timedelta(minutes=30)
        for c in candidates:
            try:
                mtime = datetime.fromtimestamp(c.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if lo <= mtime <= hi:
                distance = abs((mtime - closed_at).total_seconds())
                in_window.append((distance, c))
    if in_window:
        in_window.sort()
        return in_window[0][1], candidates, None
    largest = max(candidates, key=lambda p: p.stat().st_size)
    return largest, candidates, "fallback_largest_no_window_match"


def resolve_transcript(archive_path: Path, projects_dir: Path) -> TranscriptResolution:
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    sid_match = re.match(r"S-(\d{4})\.json$", archive_path.name)
    if not sid_match:
        return TranscriptResolution(
            session_id=0,
            transcript_path=None,
            project_dir=None,
            reason="bad_archive_filename",
            candidates=[],
        )
    sid = int(sid_match.group(1))
    worktree = archive.get("worktree")
    if not worktree:
        worktree = str(DEFAULT_REPO_ROOT)
    project_dir, reason = find_project_dir(worktree, projects_dir)
    if project_dir is None:
        return TranscriptResolution(
            session_id=sid,
            transcript_path=None,
            project_dir=None,
            reason=reason,
            candidates=[],
        )
    started_at = _parse_iso_utc(archive.get("started_at"))
    closed_at = _parse_iso_utc(archive.get("closed_at"))
    transcript, candidates, pick_reason = pick_transcript(
        project_dir, started_at, closed_at
    )
    return TranscriptResolution(
        session_id=sid,
        transcript_path=transcript,
        project_dir=project_dir,
        reason=pick_reason,
        candidates=candidates,
    )


def _parse_iso_utc(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_audit_worklist(audit_tool: Path) -> list[dict[str, Any]]:
    """Run the B1 audit in --json mode and return its list[dict] output."""
    result = subprocess.run(
        ["python3", str(audit_tool), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, list):
        raise ValueError("audit --json did not return a list")
    return payload


def build_recovery_prompt(
    archive_path: Path,
    transcript_path: Path,
    current_session: str,
    dry_run: bool,
) -> str:
    """Emit the analytical-voice recovery prompt for the user to paste into
    a fresh default-mode Claude Code session.

    The prompt instructs the recovering session to write drawers in its OWN
    analytical voice — NOT impersonating the target session. See
    ``engine/docs/audits/mempalace-recovery-guide-user-driven.md`` for the
    rationale (the impersonation-shape original direction was rejected
    after S-0079 surfaced a content-integrity concern).

    The ``current_session`` parameter is unused in the new direction
    (recovery sessions don't claim slots). It's retained for backwards
    compatibility of the CLI surface.
    """
    target_sid = re.match(r"S-(\d{4})\.json$", archive_path.name)
    if not target_sid:
        raise ValueError(f"bad archive name {archive_path.name}")
    sid_label = f"S-{target_sid.group(1)}"
    mode = "DRY-RUN" if dry_run else "WRITE"
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    started_at = archive.get("started_at") or "(unknown)"
    closed_at = archive.get("closed_at") or "(unknown)"
    archive_working_on = archive.get("working_on") or "(unknown)"
    _ = current_session  # retained for backwards compatibility
    if dry_run:
        dry_run_parts: list[str] = [
            "**This is a DRY-RUN.** Do NOT call ``mempalace_add_drawer`` or ",
            "``mempalace_diary_write``. Instead, return all observations as a ",
            "single JSON object with shape:\n\n",
            "```json\n",
            "{\n",
            '  "observation_diary": "<analytical reflection on what you ',
            "learned by reading the transcript, in YOUR voice — not ",
            f'first-person-from-{sid_label}>",\n',
            '  "pushback":  [{"first_line": "[pushback] Pattern observed in ',
            f'{sid_label}: ...", "body": "..."}}],\n',
            '  "lesson":    [{"first_line": "[lesson] Pattern observed in ',
            f'{sid_label}: ...", "body": "..."}}],\n',
            '  "decision":  [{"first_line": "[decision] ADR XXXX (landed in ',
            f'{sid_label}): ...", "body": "..."}}],\n',
            '  "summary":   "observation_diary 1, pushback N, lesson L, decision D"\n',
            "}\n",
            "```\n\n",
            "Return ONLY the JSON. The user reviews quality before scaling.",
        ]
        write_clause = "".join(dry_run_parts)
    else:
        write_clause = (
            "**Mode of authorship.** Write drawers in YOUR analytical voice "
            f"— NOT first-person-from-{sid_label}. Frame as observations of "
            f"the transcript: ``Pattern observed in {sid_label}: ...`` rather "
            "than ``I observed ...`` (which would impersonate that session).\n\n"
            "Each drawer body must include a header line ``Source: "
            f"{sid_label} transcript (analytical recovery)`` so any future "
            "reader sees the relationship immediately.\n\n"
            "Write each observation via ``mempalace_add_drawer`` with:\n\n"
            "- ``wing``: ``paideia``\n"
            "- ``room``: pushback → ``problems``; lesson → ``lessons``; "
            "decision → ``decisions``\n"
            "- ``added_by``: ``recovery-observer`` (do NOT use any S-NNNN "
            "form — this is exploration mode, not a slot-claimed session)\n"
            "- Drawer body begins with the tag bracket then the analytical "
            f"framing: ``[pushback] Pattern observed in {sid_label}: ...``\n\n"
            "OPTIONALLY, write a single MemPalace diary entry summarizing what "
            "you LEARNED BY READING the transcript (your reflection, in your "
            'voice). Use ``mempalace_diary_write agent_name="claude" '
            f'topic="{sid_label}-observed"`` and prefix the entry body with '
            f"``[recovery-observer reading {sid_label}]``.\n\n"
            "Return a one-line summary in the form "
            "``observation_diary 1|0, pushback N, lesson L, decision D``."
        )
    return f"""You are a MemPalace recovery exploration session. We are in DEFAULT mode \
— do NOT invoke /start-engine, do NOT eager-claim a slot, do NOT commit to \
tracked files. Your only outputs are MemPalace MCP tool calls.

Read another session's transcript and write MemPalace entries that capture \
what you LEARN from it, IN YOUR OWN ANALYTICAL VOICE — NOT impersonating \
that session.

## Inputs

- Target session: **{sid_label}** (a past, completed session)
- Session window: ``{started_at}`` → ``{closed_at}`` (UTC)
- Session intent: {archive_working_on}
- Transcript (Claude Code JSONL): ``{transcript_path}``
- Session archive: ``{archive_path}``

The transcript may be 50K-2MB and may span MULTIPLE sessions in the same \
worktree (Claude Code stores all sessions for a worktree in one JSONL). \
**Filter to {sid_label}'s segment by**:

- Looking for the eager-claim commit message ``chore(session): eager-claim \
  {sid_label}`` — this marks the start.
- Looking for the close commit message ``chore(session): close {sid_label}`` \
  — this marks the end.
- Cross-checking against the session window timestamps above.

Within {sid_label}'s segment, identify any of these that you'd want a \
future session to know about (in YOUR analytical voice as an observer, \
not as {sid_label}):

1. **Pushback moments** — risks named, pushback against user framing, \
   self-critiques. → ``[pushback]`` drawer in ``room=problems``.
2. **Lesson moments** — concrete tool gotchas, workflow lessons, debugging \
   discoveries. → ``[lesson]`` drawer in ``room=lessons``.
3. **Decision moments** — ADRs landed in the session, especially their \
   motivation. → ``[decision]`` drawer in ``room=decisions``.

## Output

Mode: **{mode}**.

{write_clause}

## Quality bar

- **Skip if the transcript yields nothing meaningful.** Procedural session \
  with no reflection-worthy content → respond ``unrecoverable: \
  empty_extraction`` and do not call any write tools. This is a feature.
- **Cite concrete content** — function name, file path, specific bug, ADR \
  number. Avoid platitudes.
- **Skip duplicates.** If ``mempalace_search`` shows the original session \
  already wrote a particular drawer, don't re-author it.
- **Use unfiltered ``mempalace_search``** because the wing-name landscape is \
  messy (per ``engine/operations/mempalace-operations.md``).

Begin.
"""


def progress_load(path: Path) -> dict[str, dict[str, Any]]:
    """Return dict keyed by session id (str like 'S-0067') -> entry dict.

    Entry shape: {"status": "completed"|"unrecoverable"|"pending",
                  "summary"?: str, "reason"?: str, "ts": iso}
    """
    if not path.is_file():
        return {}
    out: dict[str, dict[str, Any]] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Session") or line.startswith("|---"):
            in_table = True
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 4:
                sid, status, ts, detail = cols[0], cols[1], cols[2], cols[3]
                key = "summary" if status == "completed" else "reason"
                out[sid] = {"status": status, "ts": ts, key: detail}
        elif in_table and not line.strip():
            in_table = False
    return out


def progress_render(entries: dict[str, dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# MemPalace recovery progress (Part B per ADR 0056)")
    lines.append("")
    lines.append(
        "> Tracked by [`engine/tools/recover_mempalace_from_transcript.py`](../../tools/recover_mempalace_from_transcript.py)."
    )
    lines.append("")
    lines.append("Status legend:")
    lines.append("- `completed` — subagent extracted and wrote drawers / diary.")
    lines.append("- `unrecoverable` — transcript not located or extraction empty.")
    lines.append("- `pending` — recorded but not yet processed (rare; intermediate).")
    lines.append("")
    lines.append("| Session | Status | Timestamp | Detail |")
    lines.append("|---|---|---|---|")
    for sid in sorted(entries):
        e = entries[sid]
        detail = e.get("summary") or e.get("reason") or ""
        lines.append(
            f"| {sid} | {e.get('status', '')} | {e.get('ts', '')} | {detail} |"
        )
    lines.append("")
    completed = sum(1 for e in entries.values() if e.get("status") == "completed")
    unrec = sum(1 for e in entries.values() if e.get("status") == "unrecoverable")
    lines.append(
        f"_Totals: completed={completed} unrecoverable={unrec} total={len(entries)}_"
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def progress_write_entry(
    progress_path: Path,
    sid_label: str,
    status: str,
    summary: str | None = None,
    reason: str | None = None,
) -> None:
    entries = progress_load(progress_path)
    detail_key = "summary" if status == "completed" else "reason"
    detail_value = summary if status == "completed" else reason
    entries[sid_label] = {
        "status": status,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        detail_key: detail_value or "",
    }
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(progress_render(entries), encoding="utf-8")


def cmd_worklist(
    archive_dir: Path,
    projects_dir: Path,
    audit_tool: Path,
    progress_path: Path,
    pending_only: bool,
) -> int:
    audit = get_audit_worklist(audit_tool)
    progress = progress_load(progress_path)
    high_signal = [
        r for r in audit if not r.get("low_signal") and not r.get("diary_present")
    ]
    low_signal = [
        r for r in audit if r.get("low_signal") and not r.get("diary_present")
    ]

    def _print(rows: list[dict[str, Any]], header: str) -> None:
        print(header)
        for r in rows:
            sid = r["session"]
            if pending_only and sid in progress:
                continue
            archive_path = archive_dir / f"{sid}.json"
            if not archive_path.exists():
                print(f"  {sid} — archive_missing")
                continue
            res = resolve_transcript(archive_path, projects_dir)
            if res.transcript_path is None:
                print(f"  {sid} — unrecoverable:{res.reason}")
                continue
            status = progress.get(sid, {}).get("status", "pending")
            print(
                f"  {sid} ({r.get('mode') or 'unmoded'}) [{status}] — {res.transcript_path}"
            )

    _print(high_signal, "## high-signal")
    print()
    _print(low_signal, "## low-signal")
    return 0


def cmd_resolve(archive_dir: Path, projects_dir: Path, sid_label: str) -> int:
    archive_path = archive_dir / f"{sid_label}.json"
    if not archive_path.exists():
        print(f"archive_missing: {archive_path}", file=sys.stderr)
        return 2
    res = resolve_transcript(archive_path, projects_dir)
    if res.transcript_path is None:
        print(f"unrecoverable:{res.reason}")
        return 2
    print(str(res.transcript_path))
    return 0


def cmd_prompt(
    archive_dir: Path,
    projects_dir: Path,
    sid_label: str,
    current_session: str,
    dry_run: bool,
) -> int:
    archive_path = archive_dir / f"{sid_label}.json"
    if not archive_path.exists():
        print(f"archive_missing: {archive_path}", file=sys.stderr)
        return 2
    res = resolve_transcript(archive_path, projects_dir)
    if res.transcript_path is None:
        print(f"unrecoverable:{res.reason}", file=sys.stderr)
        return 2
    print(
        build_recovery_prompt(
            archive_path, res.transcript_path, current_session, dry_run
        )
    )
    return 0


def cmd_mark(
    progress_path: Path,
    sid_label: str,
    status: str,
    summary: str | None,
    reason: str | None,
) -> int:
    if status == "completed" and not summary:
        print("--summary required for --mark-completed", file=sys.stderr)
        return 2
    if status == "unrecoverable" and not reason:
        print("--reason required for --mark-unrecoverable", file=sys.stderr)
        return 2
    progress_write_entry(
        progress_path, sid_label, status, summary=summary, reason=reason
    )
    print(f"recorded: {sid_label} {status}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n", 1)[0] if __doc__ else None
    )
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR)
    parser.add_argument("--projects-dir", type=Path, default=DEFAULT_PROJECTS_DIR)
    parser.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS_PATH)
    parser.add_argument("--audit-tool", type=Path, default=DEFAULT_AUDIT_TOOL)
    parser.add_argument("--current-session", default=CURRENT_SESSION_DEFAULT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--worklist", action="store_true")
    group.add_argument("--resolve", metavar="S-NNNN")
    group.add_argument("--prompt", metavar="S-NNNN")
    group.add_argument("--mark-completed", metavar="S-NNNN")
    group.add_argument("--mark-unrecoverable", metavar="S-NNNN")
    parser.add_argument(
        "--pending",
        action="store_true",
        help="With --worklist, suppress already-recorded sessions.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --prompt, emit the dry-run variant.",
    )
    parser.add_argument(
        "--summary", help="With --mark-completed, the recovery summary string."
    )
    parser.add_argument(
        "--reason", help="With --mark-unrecoverable, the reason string."
    )
    args = parser.parse_args(argv)

    if args.worklist:
        return cmd_worklist(
            args.archive_dir,
            args.projects_dir,
            args.audit_tool,
            args.progress,
            args.pending,
        )
    if args.resolve:
        return cmd_resolve(args.archive_dir, args.projects_dir, args.resolve)
    if args.prompt:
        return cmd_prompt(
            args.archive_dir,
            args.projects_dir,
            args.prompt,
            args.current_session,
            args.dry_run,
        )
    if args.mark_completed:
        return cmd_mark(
            args.progress,
            args.mark_completed,
            "completed",
            summary=args.summary,
            reason=None,
        )
    if args.mark_unrecoverable:
        return cmd_mark(
            args.progress,
            args.mark_unrecoverable,
            "unrecoverable",
            summary=None,
            reason=args.reason,
        )
    parser.error("no subcommand")
    return 2


if __name__ == "__main__":
    sys.exit(main())
