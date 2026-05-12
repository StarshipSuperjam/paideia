"""One-shot audit: which sessions S-0001..S-NNNN have missing deliberate MemPalace content.

Plan
----
Implements Part B step B1 of the approved plan at
``~/.claude/plans/use-of-mempalace-by-velvety-pebble.md`` (S-0079 execution
plan at ``~/.claude/plans/to-continue-to-keen-lemur.md``).

Purpose
-------
The pre-S-0078 mechanism for surfacing missing MemPalace usage was
posture-only. Issue #27 confirmed routine-mode silent diary-skip across
12/16 Phase 5 routine sessions; the same gap probably affects interactive
sessions where no detection mechanism existed at all. ADR 0056 (S-0078)
mechanizes future sessions. Recovery of historical content for sessions
S-0032 → S-0077 is the unfinished work; this audit produces the
authoritative per-session worklist that B3
(``recover_mempalace_from_transcript.py``) consumes.

Detection
---------
For every ``engine/session/archive/S-NNNN.json`` ≤ S-0077:

1. **Diary entry**: any drawer in ``room=diary`` with ``agent='claude'``
   AND (``topic`` references the session id OR ``filed_at`` falls within
   ``[started_at, closed_at]`` window). Auto-captured drawers
   (``agent='session-hook'``) are excluded — they aren't the deliberate
   reflection layer the recovery targets.

2. **Decision drawers**: drawers in ``room=decisions`` whose
   ``added_by`` resolves to this session id (via
   ``session_id_from_added_by``). Variants: ``S-NNNN``,
   ``claude-S-NNNN``, ``claude-s00NN``, ``claude-opus-4-7-S-NNNN``,
   ``claude-opus-4.7-S-NNNN``, ``mcp:S-NNNN``, ``S-NNNN-continuation``.

3. **Pushback drawers**: drawers whose ``chroma:document`` first line
   starts with ``[pushback`` AND ``added_by`` resolves to this session id.
   These typically land in ``general`` or ``problems`` room, not a
   ``pushback`` room.

4. **Lesson drawers**: drawers in ``room=lessons`` whose ``added_by``
   resolves to this session id, OR drawers in any room whose document
   first line starts with ``[lesson``.

5. **ADR cross-reference**: count ADRs added in the session's commit
   range (``commits[]`` in archive, filtered to ADR file additions). If
   ADRs > decision drawers, the unmatched ADRs flag the session as
   ``decision_drawer_missing`` (per the two-layer recording rule —
   every ADR should have a companion decision drawer).

Categorization
--------------
Each session is categorized:

- ``complete`` — diary present AND ADR-count ≤ decision-drawer-count AND
  zero pushback/lesson drawers expected (no marker of need; this is the
  weakest category since absence of pushback isn't necessarily a miss).
- ``diary_only_missing`` — no diary entry; decisions match.
- ``decisions_missing`` — diary present but ADRs > decisions.
- ``both_missing`` — diary missing AND ADRs > decisions.
- ``no_signal`` — no diary AND no ADRs in window (weak sessions, hard to
  reflect on; recovery may yield empty extracts).

Note: pushback and lesson absence is NOT a categorization driver because
not every session produces them. The recovery executor still scans for
them; the audit just doesn't flag absence as ``missing``.

Output
------
- Markdown report at
  ``engine/docs/audits/mempalace-attribution-S0001-to-S0077.md``
  with per-mode tables (matching Issue #27's format) and a per-session
  worklist for B3.
- ``--json`` flag emits a machine-readable rollup to stdout.

CLI
---
- ``audit_mempalace_attribution.py`` — produce Markdown report.
- ``audit_mempalace_attribution.py --json`` — machine-readable to stdout.
- ``audit_mempalace_attribution.py --max-session S-NNNN`` — cap (default S-0077).
- ``audit_mempalace_attribution.py --palace PATH`` — override chromadb path.
- ``audit_mempalace_attribution.py --archive-dir PATH`` — override archive dir.
- ``audit_mempalace_attribution.py --repo-root PATH`` — override repo root.

Out of scope
------------
- Knowledge graph / tunnels (project doesn't use them).
- Wing-naming bug investigation (Issues #1, #2 — upstream).
- HNSW vector-index repair (separate ``mempalace repair`` workflow).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import parse  # noqa: E402  # ADR 0058

DEFAULT_PALACE = Path.home() / ".mempalace" / "palace" / "chroma.sqlite3"
DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ARCHIVE_DIR = DEFAULT_REPO_ROOT / "engine" / "session" / "archive"
DEFAULT_REPORT_PATH = (
    DEFAULT_REPO_ROOT
    / "engine"
    / "docs"
    / "audits"
    / "mempalace-attribution-S0001-to-S0077.md"
)
DEFAULT_MAX_SESSION = "S-0077"

_SESSION_PATTERNS = [
    re.compile(r"^S-?(\d{1,4})\b", re.IGNORECASE),
    re.compile(r"^claude-?S-?(\d{1,4})\b", re.IGNORECASE),
    re.compile(r"^claude-s(\d{4})\b", re.IGNORECASE),
    re.compile(r"^claude-opus-?4[-.]?7-?S-?(\d{1,4})\b", re.IGNORECASE),
    re.compile(r"^mcp:S-?(\d{1,4})\b", re.IGNORECASE),
]


def session_id_from_added_by(added_by: str | None) -> int | None:
    """Extract canonical session number (1..9999) from any ``added_by`` variant.

    Returns ``None`` for ``mempalace``, ``claude`` (bare), ``mcp`` (bare),
    or any pattern not recognized.
    """
    if not added_by:
        return None
    s = added_by.strip()
    for pat in _SESSION_PATTERNS:
        m = pat.match(s)
        if m:
            return int(m.group(1))
    return None


_TOPIC_SESSION_PAT = re.compile(r"\b[Ss]-?(\d{4})\b")


def session_id_from_topic(topic: str | None) -> int | None:
    """Extract session number from a diary entry's ``topic`` field."""
    if not topic:
        return None
    m = _TOPIC_SESSION_PAT.search(topic)
    if m:
        return int(m.group(1))
    return None


def session_str(n: int) -> str:
    return f"S-{n:04d}"


@dataclass
class SessionAudit:
    session_id: int
    mode: str | None
    started_at: str | None
    closed_at: str | None
    diary_present: bool = False
    diary_match_method: str | None = None  # "topic" | "window" | None
    decision_drawer_count: int = 0
    pushback_drawer_count: int = 0
    lesson_drawer_count: int = 0
    adrs_added: list[str] = field(default_factory=list)
    auto_captures_present: bool = False
    transcript_unresolved: bool = False
    category: str = "no_signal"
    commit_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "session": session_str(self.session_id),
            "mode": self.mode,
            "diary_present": self.diary_present,
            "diary_match_method": self.diary_match_method,
            "decision_drawer_count": self.decision_drawer_count,
            "pushback_drawer_count": self.pushback_drawer_count,
            "lesson_drawer_count": self.lesson_drawer_count,
            "adrs_added": self.adrs_added,
            "adr_count": len(self.adrs_added),
            "auto_captures_present": self.auto_captures_present,
            "category": self.category,
            "commit_count": self.commit_count,
            "low_signal": self.is_low_signal(),
        }

    def is_low_signal(self) -> bool:
        """Heuristic: session likely had little reflective content to recover.

        True when diary was already present, OR session had ≤ 1 commit and no
        ADRs and no decisions. Recovery executor will still scan but the
        subagent's skip-if-empty rule applies more often.
        """
        if self.diary_present:
            return True
        if (
            self.commit_count <= 1
            and not self.adrs_added
            and self.decision_drawer_count == 0
        ):
            return True
        return False


def categorize(audit: SessionAudit) -> str:
    adr_count = len(audit.adrs_added)
    decisions_short = adr_count > audit.decision_drawer_count
    diary_missing = not audit.diary_present
    if diary_missing and decisions_short:
        return "both_missing"
    if diary_missing and adr_count == 0 and audit.decision_drawer_count == 0:
        return "no_signal"
    if diary_missing:
        return "diary_only_missing"
    if decisions_short:
        return "decisions_missing"
    return "complete"


def parse_iso_window(
    started_at: str | None, closed_at: str | None
) -> tuple[datetime | None, datetime | None]:
    """Return ``(start, end)`` as timezone-aware UTC datetimes.

    Archive timestamps are UTC (``Z`` suffix or explicit ``+00:00``). When
    ``closed_at`` is missing, widen to end-of-day in UTC.
    """
    if not started_at:
        return None, None
    start = _parse_archive_dt(started_at)
    if start is None:
        return None, None
    if closed_at:
        end = _parse_archive_dt(closed_at)
        if end is None:
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def diary_window_for(
    start: datetime | None, end: datetime | None
) -> tuple[datetime | None, datetime | None]:
    """Return a diary-tuned window — narrowed for runaway windows, padded forward.

    The diary write happens near session shutdown. Two known-pathology shapes
    informed by S-0058 and S-0070 in the live data:

    - **Runaway start** (S-0058: ``started_at=2026-05-04T00:00:00Z`` against
      ``closed_at=2026-05-05T02:33:07Z`` — 26h apparent window): cap the
      backward extension at 3h before close so the diary-detect doesn't sweep
      in unrelated entries from earlier in the day.

    - **Late diary** (S-0070: claude diary filed ~9 minutes after the
      recorded ``closed_at``): pad 30 minutes forward so a diary that
      landed during the shutdown ritual (between ``closed_at`` recording
      and the actual close-commit hash) is still attributed.
    """
    from datetime import timedelta as _td

    if start is None or end is None:
        return start, end
    earliest = end - _td(hours=3)
    if start < earliest:
        start = earliest
    return start, end + _td(minutes=30)


def _parse_archive_dt(s: str) -> datetime | None:
    """Parse an archive timestamp (UTC). Returns timezone-aware datetime."""
    if not s:
        return None
    try:
        dt = parse(s)  # ADR 0058 — tolerant of Z and +00:00 archive shapes
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_palace_dt(filed_at: str) -> datetime | None:
    """Parse a mempalace ``filed_at`` (naive local time per palace storage).

    The palace stores naive ISO strings without timezone marker, written
    against the user's local clock. Convert to UTC by attaching the
    process-local timezone (which matches the original write context: the
    same user, same machine).

    NOT routed through ``timestamps.parse()`` per ADR 0058 — that helper's
    contract is for canonical UTC-emitted strings (Z-suffix, +00:00, or
    compact-time). Palace-storage strings are NAIVE local time, a
    different concern. ``audit_mempalace_attribution.py`` is allowlisted
    in validate.py's _TIMESTAMP_HELPER_BYPASS_ALLOWLIST so the
    timestamp_helper_bypass soft-warn does not fire on this site (the
    cost of allowlisting the whole file is that line 282's helper
    routing is also silenced — but line 282 IS routed through parse()
    above for cleanliness).
    """
    if not filed_at:
        return None
    try:
        dt = datetime.fromisoformat(filed_at)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc)


def in_window(
    filed_at: str | None, start: datetime | None, end: datetime | None
) -> bool:
    """Return True if ``filed_at`` (palace-naive ISO) falls within ``[start, end]`` UTC."""
    if not filed_at or start is None or end is None:
        return False
    dt = _parse_palace_dt(filed_at)
    if dt is None:
        return False
    return start <= dt <= end


def open_palace_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_drawer_metadata_bulk(
    conn: sqlite3.Connection,
) -> dict[int, dict[str, str | None]]:
    """Return dict id -> {key: value} of every drawer's metadata.

    One pass over ``embedding_metadata``. We carry only the keys the audit
    needs (room, agent, topic, added_by, filed_at, type) plus the document
    text. Memory cost ~30-40MB for 41K drawers; acceptable for a one-shot.
    """
    keys = (
        "room",
        "agent",
        "topic",
        "added_by",
        "filed_at",
        "type",
        "chroma:document",
        "wing",
        "date",
    )
    placeholders = ",".join("?" for _ in keys)
    sql = (
        f"SELECT id, key, string_value FROM embedding_metadata "
        f"WHERE key IN ({placeholders})"
    )  # nosec B608  # placeholder string construction; values parameterized via execute(sql, keys)
    cur = conn.execute(sql, keys)
    out: dict[int, dict[str, str | None]] = {}
    for row in cur:
        out.setdefault(row["id"], {})[row["key"]] = row["string_value"]
    return out


def attribute_diary_entries(
    drawers: dict[int, dict[str, str | None]],
    sessions: list[tuple[int, datetime | None, datetime | None]],
) -> dict[int, tuple[int, str]]:
    """Map session_id -> (drawer_id, method) for the canonical diary attribution.

    Each claude-agent diary entry is attributed to AT MOST ONE session:

    1. **Topic match** — if ``topic`` parses to a session id, attribute there.
    2. **Closest by close** — among sessions whose ``[closed_at-3h, closed_at+30min]``
       diary window contains the entry, pick the one whose ``closed_at`` is
       closest to ``filed_at``.

    Returns a dict keyed by session_id with the matching drawer id and method.
    Sessions absent from the dict had no diary attribution.
    """
    from datetime import timedelta as _td

    session_by_id = {sid: (start, end) for sid, start, end in sessions}
    out: dict[int, tuple[int, str]] = {}
    for did, md in drawers.items():
        if md.get("agent") != "claude":
            continue
        if md.get("type") != "diary_entry" and md.get("room") != "diary":
            continue
        topic = md.get("topic")
        topic_sid = session_id_from_topic(topic) if topic else None
        if topic_sid is not None and topic_sid in session_by_id:
            if topic_sid not in out:
                out[topic_sid] = (did, "topic")
            continue
        filed_at = _parse_palace_dt(md.get("filed_at") or "")
        if filed_at is None:
            continue
        candidates: list[tuple[float, int]] = []
        for sid, (s, e) in session_by_id.items():
            if s is None or e is None:
                continue
            diary_start = max(s, e - _td(hours=3))
            diary_end = e + _td(minutes=30)
            if diary_start <= filed_at <= diary_end:
                distance = abs((filed_at - e).total_seconds())
                candidates.append((distance, sid))
        if not candidates:
            continue
        candidates.sort()
        winner_sid = candidates[0][1]
        if winner_sid not in out:
            out[winner_sid] = (did, "window")
    return out


def discover_session_drawers(
    drawers: dict[int, dict[str, str | None]],
    target_session: int,
) -> tuple[int, int, int, bool]:
    """Return (decision_count, pushback_count, lesson_count, auto_captures_present)."""
    decision = 0
    pushback = 0
    lesson = 0
    auto_captures = False
    for md in drawers.values():
        added_by = md.get("added_by")
        sid = session_id_from_added_by(added_by)
        if sid != target_session:
            if added_by and added_by.startswith("session-hook"):
                pass
            continue
        room = md.get("room") or ""
        doc = md.get("chroma:document") or ""
        first_line = doc.split("\n", 1)[0] if doc else ""
        if room == "decisions" or first_line.startswith("[decision"):
            decision += 1
        elif room == "lessons" or first_line.startswith("[lesson"):
            lesson += 1
        elif first_line.startswith("[pushback"):
            pushback += 1
    for md in drawers.values():
        if md.get("agent") == "session-hook":
            auto_captures = True
            break
    return decision, pushback, lesson, auto_captures


def adrs_added_in_commits(repo_root: Path, commit_shas: Iterable[str]) -> list[str]:
    """Return sorted list of ADR-file basenames added in any of the given commits."""
    adrs: set[str] = set()
    for sha in commit_shas:
        try:
            out = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "show",
                    "--name-only",
                    "--diff-filter=A",
                    "--pretty=format:",
                    sha,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            continue
        for line in out.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if (
                line.startswith("engine/adr/") or line.startswith("product/adr/")
            ) and line.endswith(".md"):
                if "README" in Path(line).name:
                    continue
                adrs.add(Path(line).name)
    return sorted(adrs)


def load_archive(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"archive {path} is not a JSON object")
    return payload


def session_id_from_archive_name(p: Path) -> int | None:
    m = re.match(r"S-(\d{4})\.json$", p.name)
    return int(m.group(1)) if m else None


def collect_audits(
    archive_dir: Path,
    palace_path: Path,
    repo_root: Path,
    max_session_id: int,
) -> list[SessionAudit]:
    archives = sorted(
        p
        for p in archive_dir.glob("S-*.json")
        if (sid := session_id_from_archive_name(p)) is not None
        and sid <= max_session_id
    )
    conn = open_palace_readonly(palace_path)
    try:
        drawers = fetch_drawer_metadata_bulk(conn)
    finally:
        conn.close()
    session_windows: list[tuple[int, datetime | None, datetime | None]] = []
    archive_data: dict[int, dict[str, Any]] = {}
    for path in archives:
        archive = load_archive(path)
        sid = session_id_from_archive_name(path)
        if sid is None:
            continue
        archive_data[sid] = archive
        start, end = parse_iso_window(
            archive.get("started_at"), archive.get("closed_at")
        )
        session_windows.append((sid, start, end))
    diary_attribution = attribute_diary_entries(drawers, session_windows)
    audits: list[SessionAudit] = []
    for sid, _, _ in session_windows:
        archive = archive_data[sid]
        commit_shas = [c.get("sha") for c in archive.get("commits", []) if c.get("sha")]
        adrs = adrs_added_in_commits(repo_root, commit_shas) if commit_shas else []
        decision_count, pushback_count, lesson_count, auto_captures = (
            discover_session_drawers(drawers, sid)
        )
        diary_pair = diary_attribution.get(sid)
        audit = SessionAudit(
            session_id=sid,
            mode=archive.get("mode"),
            started_at=archive.get("started_at"),
            closed_at=archive.get("closed_at"),
            diary_present=diary_pair is not None,
            diary_match_method=diary_pair[1] if diary_pair else None,
            decision_drawer_count=decision_count,
            pushback_drawer_count=pushback_count,
            lesson_drawer_count=lesson_count,
            adrs_added=adrs,
            auto_captures_present=auto_captures,
            commit_count=len(archive.get("commits", [])),
        )
        audit.category = categorize(audit)
        audits.append(audit)
    return audits


def render_markdown_report(audits: list[SessionAudit], max_session: str) -> str:
    interactive = [a for a in audits if a.mode == "interactive"]
    routine = [a for a in audits if a.mode == "routine"]
    unmoded = [a for a in audits if a.mode not in ("interactive", "routine")]
    by_cat: dict[str, list[SessionAudit]] = {}
    for a in audits:
        by_cat.setdefault(a.category, []).append(a)
    cat_order = [
        "complete",
        "diary_only_missing",
        "decisions_missing",
        "both_missing",
        "no_signal",
    ]
    lines: list[str] = []
    lines.append("# MemPalace attribution audit — S-0001 to " + max_session)
    lines.append("")
    lines.append(
        "> One-shot audit produced by [`engine/tools/audit_mempalace_attribution.py`](../../tools/audit_mempalace_attribution.py)."
    )
    lines.append(
        "> Per [ADR 0056](../../adr/0056-mempalace-mechanical-adoption-checks.md) and the approved plan at `~/.claude/plans/use-of-mempalace-by-velvety-pebble.md` (Part B). Surfaces the per-session worklist that `recover_mempalace_from_transcript.py` consumes."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Sessions audited: **{len(audits)}** (S-0001 → {max_session}).")
    lines.append(
        f"- Mode breakdown: interactive={len(interactive)}, routine={len(routine)}, unmoded={len(unmoded)}."
    )
    lines.append("- Categories:")
    for cat in cat_order:
        n = len(by_cat.get(cat, []))
        lines.append(f"  - **{cat}**: {n}")
    lines.append("")
    lines.append("Field semantics:")
    lines.append("")
    lines.append(
        "- `diary` — `✅` if a `room=diary, agent=claude` drawer matches by topic-id or filed_at-window. `❌` if neither."
    )
    lines.append(
        "- `dec` — count of `room=decisions` drawers attributed to the session via `added_by`."
    )
    lines.append("- `adr` — count of ADR files added in the session's commit range.")
    lines.append(
        "- `pb` / `les` — pushback / lesson drawer counts attributed to the session."
    )
    lines.append("- `cat` — categorization (see below).")
    lines.append("")
    lines.append("Category meaning:")
    lines.append("")
    lines.append("- `complete` — diary present AND adr count ≤ decision drawer count.")
    lines.append("- `diary_only_missing` — no diary; decisions/ADRs match.")
    lines.append("- `decisions_missing` — diary present but ADRs > decisions.")
    lines.append("- `both_missing` — diary absent AND ADRs > decisions.")
    lines.append(
        "- `no_signal` — no diary AND no ADRs in window. Recovery may yield little."
    )
    lines.append("")
    if interactive:
        lines.append("## Interactive sessions")
        lines.append("")
        lines.extend(_render_session_table(interactive))
        lines.append("")
    if routine:
        lines.append("## Routine sessions")
        lines.append("")
        lines.extend(_render_session_table(routine))
        lines.append("")
    if unmoded:
        lines.append("## Sessions without `mode` field (pre-S-0048)")
        lines.append("")
        lines.extend(_render_session_table(unmoded))
        lines.append("")
    lines.append("## Recovery worklist")
    lines.append("")
    lines.append(
        "All sessions where the diary write is missing — input to `recover_mempalace_from_transcript.py`. Sessions marked `(low signal)` had ≤ 1 commit and no ADRs/decisions; the executor will still scan but the subagent's skip-if-empty rule may apply."
    )
    lines.append("")
    high = [a for a in audits if not a.diary_present and not a.is_low_signal()]
    low = [a for a in audits if not a.diary_present and a.is_low_signal()]
    if not high and not low:
        lines.append("_(empty — no sessions flagged.)_")
    else:
        if high:
            lines.append("### High-signal (recovery prioritized)")
            lines.append("")
            for a in high:
                tag = a.category
                adr_part = f" ADRs={','.join(a.adrs_added)}" if a.adrs_added else ""
                lines.append(
                    f"- {session_str(a.session_id)} ({a.mode or 'unmoded'}) — {tag} — dec={a.decision_drawer_count} commits={a.commit_count}{adr_part}"
                )
            lines.append("")
        if low:
            lines.append("### Low-signal (recovery may yield little)")
            lines.append("")
            for a in low:
                lines.append(
                    f"- {session_str(a.session_id)} ({a.mode or 'unmoded'}) — {a.category} — commits={a.commit_count}"
                )
            lines.append("")
    lines.append("## Sessions with diary already present (no recovery needed)")
    lines.append("")
    have_diary = [a for a in audits if a.diary_present]
    if not have_diary:
        lines.append("_(empty.)_")
    else:
        for a in have_diary:
            lines.append(
                f"- {session_str(a.session_id)} ({a.mode or 'unmoded'}) — diary by {a.diary_match_method}"
            )
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_session_table(audits: list[SessionAudit]) -> list[str]:
    lines: list[str] = []
    lines.append("| Session | diary | dec | adr | pb | les | category |")
    lines.append("|---|---|---|---|---|---|---|")
    for a in audits:
        diary = "✅" if a.diary_present else "❌"
        if a.diary_present and a.diary_match_method == "window":
            diary = "✅(w)"
        lines.append(
            f"| {session_str(a.session_id)} | {diary} | "
            f"{a.decision_drawer_count} | {len(a.adrs_added)} | "
            f"{a.pushback_drawer_count} | {a.lesson_drawer_count} | "
            f"{a.category} |"
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n", 1)[0] if __doc__ else None
    )
    parser.add_argument("--palace", type=Path, default=DEFAULT_PALACE)
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument(
        "--max-session",
        default=DEFAULT_MAX_SESSION,
        help="Highest session id to include, e.g. S-0077.",
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON to stdout instead of writing the Markdown report.",
    )
    args = parser.parse_args(argv)
    if not args.palace.exists():
        print(
            f"[audit_mempalace_attribution] palace not found: {args.palace}",
            file=sys.stderr,
        )
        return 2
    if not args.archive_dir.is_dir():
        print(
            f"[audit_mempalace_attribution] archive dir not found: {args.archive_dir}",
            file=sys.stderr,
        )
        return 2
    m = re.match(r"S-(\d{1,4})$", args.max_session)
    if not m:
        print(
            f"[audit_mempalace_attribution] invalid --max-session: {args.max_session}",
            file=sys.stderr,
        )
        return 2
    max_id = int(m.group(1))
    audits = collect_audits(args.archive_dir, args.palace, args.repo_root, max_id)
    if args.json:
        json.dump([a.to_dict() for a in audits], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    report = render_markdown_report(audits, args.max_session)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"[audit_mempalace_attribution] wrote {args.report}", file=sys.stderr)
    by_cat: dict[str, int] = {}
    for a in audits:
        by_cat[a.category] = by_cat.get(a.category, 0) + 1
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat}: {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
