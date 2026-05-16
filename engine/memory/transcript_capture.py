"""Stop/PreCompact transcript-capture handler for the engine-memory substrate.

Per ADR 0091, this module preserves MemPalace's load-bearing affordance:
auto-capture of conversation transcripts so future sessions can recall
"what was said" without re-deriving from cold. Mempalace's
``hooks_cli.py`` is the reference; this is the simplified vendored
replacement (~200 LOC).

Invocation contract:

* Triggered from ``engine/tools/hooks/engine-memory-capture.sh`` via
  ``python -m engine.memory.capture {stop,precompact}``.
* Reads a JSON payload from stdin: ``{"session_id": str,
  "stop_hook_active": bool, "transcript_path": str}``. The harness
  (Claude Code) pipes this on every Stop and PreCompact event.
* Opens the transcript JSONL at ``transcript_path``; iterates records.
* Counts user messages; compares to ``capture_state.message_count_since_save``
  for this ``session_id``; computes the delta.
* Extracts content for the delta range, strips noise (length-gated;
  long blocks summarized to head+tail), chunks if > 50KB, INSERTs one
  drawer per chunk into ``room='work'`` with ``source_kind='hook_stop'``
  or ``'hook_precompact'``, ``tags=['transcript']``.
* Updates ``capture_state`` to the new count for idempotency.
* Always exits 0 — capture failures log to
  ``.claude/logs/engine-memory-hook.log``, never block the harness.

Per-session watermark (``message_count_since_save``) gives mempalace-
parity idempotency: re-firing the same Stop event over the same JSONL
produces zero new drawers. JSONL growth between fires produces only the
delta.

Per ADR 0091's out-of-scope pre-commits:

* Auto-capture always routes to ``room='work'`` (the S-0186 pollution
  defense). Curated rooms remain Claude-authored only.
* No lineage row at S-0190 for hook-driven writes — the migration
  replay at S-0192 is the lineage-heavy path. Provenance lives in the
  ``metadata`` JSON (transcript basename, hook_kind, chunk_index).
* No deny-list redaction at S-0190 — transcript content sensitivity is
  ADR 0091 risk #10, deferred indefinitely until triggered.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Literal

from engine.memory.connection import get_conn

logger = logging.getLogger("engine_memory.transcript_capture")

# Tuning constants — chosen per ADR 0091 risk register + the approved plan.
# Adjust here if empirical evidence post-cutover shifts the calculus.
MAX_BLOCK_CHARS = 10_000  # blocks larger than this get head+tail-summarized
MAX_DRAWER_CHARS = 50_000  # content larger than this splits across drawers
HEAD_TAIL_CHARS = 500  # bytes preserved at each end of a noise-stripped block


def read_hook_event(stream: Any | None = None) -> dict[str, Any]:
    """Parse the harness's stdin JSON payload.

    Returns an empty dict on parse failure — the caller treats that as
    "no transcript path available; no-op". ``stream`` defaults to
    ``sys.stdin`` but is overridable for tests.
    """
    if stream is None:
        stream = sys.stdin
    try:
        data = json.load(stream)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError, OSError):
        pass
    return {}


def validate_transcript_path(path: str) -> Path | None:
    """Return a resolved Path if safe + existent, else None.

    Rejects ``..`` traversal segments; requires ``.jsonl`` or ``.json``
    extension; requires the file to exist. Per mempalace's
    ``_validate_transcript_path`` pattern (S-0033 defense in depth).
    """
    if not path:
        return None
    expanded = os.path.expanduser(path)
    # Reject any path that contains a parent-directory traversal segment
    # BEFORE resolving — resolution would normalize them away.
    if ".." in Path(expanded).parts:
        return None
    resolved = Path(expanded).resolve()
    if resolved.suffix not in (".jsonl", ".json"):
        return None
    if not resolved.is_file():
        return None
    return resolved


def _record_is_user_message(record: dict[str, Any]) -> bool:
    """True for a Claude Code user-message record, skipping command-messages.

    Claude Code transcript JSONL shape:
        {"message": {"role": "user", "content": ...}, ...}

    Command-messages (the harness wraps slash-command surfaces as user
    messages with ``<command-message>`` prefix) are skipped — per
    mempalace's pattern, they're harness-internal noise that distorts
    the high-water mark.
    """
    msg = record.get("message")
    if not isinstance(msg, dict):
        return False
    if msg.get("role") != "user":
        return False
    content = msg.get("content")
    text = _extract_text_from_content(content)
    if text.lstrip().startswith("<command-message>"):
        return False
    return True


def _extract_text_from_content(content: Any) -> str:
    """Flatten Claude Code message content to plain text.

    ``content`` may be a string OR a list of blocks like
    ``[{"type": "text", "text": "..."}, {"type": "tool_use", ...}]``.
    Returns the concatenation of the text fields; non-text blocks are
    serialized as a short marker (``[tool_use: <name>]``,
    ``[tool_result: <len> chars]``, etc.) so the captured content
    reflects shape, not just text.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type", "")
        if btype == "text":
            text = block.get("text", "")
            if isinstance(text, str):
                parts.append(text)
        elif btype == "tool_use":
            name = block.get("name", "?")
            parts.append(f"[tool_use: {name}]")
        elif btype == "tool_result":
            result = block.get("content", "")
            if isinstance(result, list):
                result_text = "".join(
                    b.get("text", "") for b in result if isinstance(b, dict)
                )
            else:
                result_text = str(result) if result else ""
            parts.append(f"[tool_result: {len(result_text)} chars]\n{result_text}")
        else:
            parts.append(f"[{btype}]")
    return "\n".join(parts)


def read_jsonl_records(path: Path) -> list[dict[str, Any]]:
    """Parse a JSONL file into a list of dicts. Malformed lines are skipped."""
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if isinstance(rec, dict):
                    records.append(rec)
    except OSError:
        pass
    return records


def count_user_messages(records: list[dict[str, Any]]) -> int:
    """Count records that pass :func:`_record_is_user_message`."""
    return sum(1 for r in records if _record_is_user_message(r))


def strip_noise(text: str, max_block_chars: int = MAX_BLOCK_CHARS) -> str:
    """Length-gate a block: if too large, replace middle with truncation marker.

    Pure heuristic — doesn't introspect content type. Works for any
    verbose content (tool results, file reads, long pastes). The
    head + tail format preserves recognizable context at each end so
    future searches can still match against the first or last passage.
    """
    if len(text) <= max_block_chars:
        return text
    head = text[:HEAD_TAIL_CHARS]
    tail = text[-HEAD_TAIL_CHARS:]
    truncated = len(text) - 2 * HEAD_TAIL_CHARS
    return f"{head}\n...[{truncated} bytes truncated]...\n{tail}"


def extract_content_for_chunk(
    records: list[dict[str, Any]], start_user_index: int
) -> str:
    """Build the content string for records FROM the start_user_index-th user message.

    ``start_user_index`` is 0-based among user messages. All records
    after (and including) the start user message are concatenated, with
    each record's content extracted and noise-stripped.
    """
    if start_user_index < 0:
        start_user_index = 0

    user_seen = 0
    capture_index = None
    for i, rec in enumerate(records):
        if _record_is_user_message(rec):
            if user_seen == start_user_index:
                capture_index = i
                break
            user_seen += 1

    if capture_index is None:
        return ""

    parts: list[str] = []
    for rec in records[capture_index:]:
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "?")
        text = _extract_text_from_content(msg.get("content"))
        if not text:
            continue
        text = strip_noise(text)
        parts.append(f"--- {role} ---\n{text}")

    return "\n\n".join(parts)


def chunk_content(content: str, max_drawer_chars: int = MAX_DRAWER_CHARS) -> list[str]:
    """Split content into ≤max_drawer_chars chunks on paragraph boundary."""
    if len(content) <= max_drawer_chars:
        return [content] if content else []

    chunks: list[str] = []
    remaining = content
    while len(remaining) > max_drawer_chars:
        # Find the last paragraph boundary within the cap, preferring
        # double-newline over single-newline over hard-cut.
        cut = remaining.rfind("\n\n", 0, max_drawer_chars)
        if cut <= max_drawer_chars // 4:
            cut = remaining.rfind("\n", 0, max_drawer_chars)
        if cut <= max_drawer_chars // 4:
            cut = max_drawer_chars
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _resolve_log_path() -> Path | None:
    """Resolve <repo-root>/.claude/logs/engine-memory-hook.log if possible."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())
    except (subprocess.SubprocessError, OSError):
        return None
    return repo_root / ".claude" / "logs" / "engine-memory-hook.log"


def log_failure(reason: str, **details: Any) -> None:
    """Append a single-line failure record to .claude/logs/engine-memory-hook.log.

    Best-effort — failures here are silent (log dir may not exist; the
    alternative of raising would block the harness, which is worse).
    Mirrors the mempalace wrapper's logging discipline.
    """
    log_path = _resolve_log_path()
    if log_path is None:
        return
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        detail_str = " ".join(f"{k}={v}" for k, v in details.items())
        with log_path.open("a", encoding="utf-8") as fh:
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            fh.write(f"{ts} FAIL reason={reason} {detail_str}\n")
    except OSError:
        pass


def capture(
    hook_kind: Literal["stop", "precompact"],
    *,
    stdin: Any | None = None,
    db_path: Path | str | None = None,
) -> int:
    """Orchestrate one capture run. Returns exit code (always 0 in production).

    Test code may pass ``stdin`` (a StringIO) and ``db_path`` (an isolated
    SQLite file) to exercise the full path without side effects. The
    bash hook always passes neither — defaults are sys.stdin + the
    project's engine_memory.sqlite3.
    """
    if hook_kind not in ("stop", "precompact"):
        log_failure("invalid_hook_kind", got=hook_kind)
        return 0

    event = read_hook_event(stdin)
    transcript_path_str = event.get("transcript_path", "")
    session_id = event.get("session_id") or "unknown"

    transcript_path = validate_transcript_path(str(transcript_path_str))
    if transcript_path is None:
        # No transcript path resolved — this is the Risk #9 fallback
        # path. Soft-warn naming reserved for S-0193's validate.py
        # wiring; here we just log + exit 0.
        log_failure(
            "transcript_path_missing_or_invalid",
            session_id=session_id,
            hook_kind=hook_kind,
            raw_path=str(transcript_path_str)[:200],
        )
        return 0

    records = read_jsonl_records(transcript_path)
    current_count = count_user_messages(records)

    conn = get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT message_count_since_save FROM capture_state WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        stored_count = row[0] if row else 0

        if current_count <= stored_count:
            # Idempotent no-op: re-fire over identical or shrunken transcript.
            return 0

        content = extract_content_for_chunk(records, start_user_index=stored_count)
        if not content.strip():
            # Delta exists in count but contains no extractable text
            # (e.g., entirely tool-result blocks of zero length).
            # Update the watermark so we don't re-attempt, then no-op.
            _upsert_capture_state(conn, session_id, current_count)
            return 0

        chunks = chunk_content(content)
        source_kind = f"hook_{hook_kind}"
        transcript_basename = transcript_path.name

        for i, chunk in enumerate(chunks):
            metadata = json.dumps(
                {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "transcript_path": transcript_basename,
                    "hook_kind": hook_kind,
                    "delta_user_messages": current_count - stored_count,
                }
            )
            conn.execute(
                "INSERT INTO drawers "
                "(id, room, tags, source_kind, agent, session_id, content, metadata) "
                "VALUES (?, 'work', '[\"transcript\"]', ?, 'claude', ?, ?, ?)",
                (uuid.uuid4().hex, source_kind, session_id, chunk, metadata),
            )

        _upsert_capture_state(conn, session_id, current_count)
    except Exception as exc:  # noqa: BLE001
        # Any unexpected failure is logged + swallowed. The hook never
        # blocks the harness; failures surface via the log file +
        # eventually validate.py's engine_memory_capture_failure
        # soft-warn (wired at S-0193).
        logger.exception("capture failed")
        log_failure(
            "exception",
            session_id=session_id,
            hook_kind=hook_kind,
            exc=type(exc).__name__,
        )
    finally:
        conn.close()

    return 0


def _upsert_capture_state(conn: Any, session_id: str, new_count: int) -> None:
    """UPSERT capture_state with the new high-water mark + timestamp."""
    conn.execute(
        "INSERT INTO capture_state (session_id, last_stop_save_at, message_count_since_save) "
        "VALUES (?, datetime('now'), ?) "
        "ON CONFLICT(session_id) DO UPDATE SET "
        "last_stop_save_at = datetime('now'), "
        "message_count_since_save = excluded.message_count_since_save",
        (session_id, new_count),
    )
