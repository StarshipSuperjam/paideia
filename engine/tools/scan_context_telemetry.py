"""Capture per-session context-window usage at shutdown.

Layer 1 contract per ADR 0049's cross-cutting telemetry addition.

Purpose
-------
The Claude Code harness does not expose context usage to running code.
The transcript JSONL stored at
``~/.claude/projects/<encoded-project-path>/<session-id>.jsonl`` is
the only proxy available. This tool reads that file at shutdown,
tokenizes the content for an upper-bound estimate, and writes three
fields into the session's current.json:

- ``transcript_token_estimate`` (int) — total tokens.
- ``transcript_token_pct`` (float) — estimate / 1_000_000 (the 1M
  Opus 4.7 window).
- ``tokenizer_used`` (str) — ``"tiktoken-o200k_base"`` when tiktoken
  is installed; ``"chars-div-4-fallback"`` otherwise.

The estimate is upper-bound (the harness manages context via
compaction and caching; on-disk transcript represents the full
conversation, not the actual prompt size at any moment). Sufficient
for the cross-session "running too long / too short / high variance"
judgment in the health-check session-load trend section.

The fields are NOT suitable for in-session "do I have budget"
decisions. ``transcript_token_pct`` can exceed 1.0 in long sessions
because cached+compacted content compounds the cumulative count past
the 1M live-window size — a value above 1.0 is a tell that the
metric is cumulative, not live. See Issue #11 (closed at S-0052) for
the false-pressure-misread incident the audit's window-wide telemetry
turned into a structural finding.

Run from session-shutdown-sequence step 7b (after scope-delivery
audit, before outcome_summary fill, before archive).

Exit codes
----------
- ``0`` — telemetry captured (or transcript unfindable; logged note).
- The non-zero path is reserved.

CLI
---
- ``scan_context_telemetry.py`` — auto-detect transcript, write to
  current.json.
- ``scan_context_telemetry.py --transcript PATH`` — explicit
  transcript path.
- ``scan_context_telemetry.py --repo-root PATH`` — override repo root.
- ``scan_context_telemetry.py --dry-run`` — compute and print, do not
  write.

Out of scope
------------
- No backfill of historical archives. Telemetry begins from S-0042
  forward; older archives carry no fields. The health-check trend
  section handles missing fields gracefully.
- No precise context measurement. Upper-bound proxy only.
- No token cost estimation. Cost telemetry is a separate concern.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_WINDOW_TOKENS = 1_000_000  # Opus 4.7 1M context.

# Encoded project-path form Claude Code uses for the transcript directory.
# Each non-alphanumeric character (slash, dot, underscore) is replaced
# with a dash. The leading `/` of an absolute path becomes a leading `-`.
# Verified against ~/.claude/projects/ directory listing for known paths.
import re as _re  # noqa: E402

_ENCODE_RE = _re.compile(r"[^A-Za-z0-9-]")


def _encoded_project_dir(project_path: Path) -> str:
    return _ENCODE_RE.sub("-", str(project_path))


def find_transcript_for_repo(repo_root: Path) -> Path | None:
    """Locate the most-recently-modified .jsonl transcript for repo_root.

    Claude Code stores transcripts at
    ``~/.claude/projects/<encoded-project-path>/<session-id>.jsonl``.
    The encoded path uses ``/`` → ``-`` and ``.`` → ``-`` replacement;
    the leading absolute-path slash becomes a leading dash.

    Returns the most recently modified file in that directory, or
    None if no project directory exists or no transcripts are present.
    """
    encoded = _encoded_project_dir(repo_root)
    project_dir = Path.home() / ".claude" / "projects" / encoded
    if not project_dir.is_dir():
        return None
    candidates = sorted(
        project_dir.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def read_transcript_text(transcript: Path) -> str:
    """Return the concatenated string content of every transcript line.

    Each JSONL line is a structured record (user/assistant message,
    tool call, tool result). For an upper-bound token estimate, the
    raw concatenation of every line's serialized form is the
    appropriate input — the tokenizer sees something at-or-larger
    than what was actually prompted to the model.
    """
    try:
        return transcript.read_text()
    except OSError as exc:
        raise RuntimeError(f"Could not read transcript {transcript}: {exc}") from exc


def tokenize(text: str) -> tuple[int, str]:
    """Return (estimated_token_count, tokenizer_label).

    Tries tiktoken with o200k_base first (best Claude proxy publicly
    available — same family GPT-4o uses). Falls back to a coarse
    char-count / 4 estimate when tiktoken is not importable.
    """
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("o200k_base")
        return len(encoding.encode(text)), "tiktoken-o200k_base"
    except ImportError:
        return len(text) // 4, "chars-div-4-fallback"


def write_telemetry_to_current(
    repo_root: Path, token_estimate: int, tokenizer_label: str
) -> None:
    """Update engine/session/current.json with the telemetry fields.

    Idempotent: re-running overwrites the prior values. Raises if
    current.json is absent (caller decides whether to surface).
    """
    current = repo_root / "engine" / "session" / "current.json"
    if not current.is_file():
        raise FileNotFoundError(f"current.json not found at {current}")
    data: dict[str, Any] = json.loads(current.read_text())
    data["transcript_token_estimate"] = token_estimate
    data["transcript_token_pct"] = round(token_estimate / CONTEXT_WINDOW_TOKENS, 4)
    data["tokenizer_used"] = tokenizer_label
    current.write_text(json.dumps(data, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture per-session transcript-token estimate at shutdown. "
            "Per ADR 0049's cross-cutting telemetry addition."
        ),
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        default=None,
        help="Explicit transcript JSONL path (overrides auto-detect).",
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
        help="Compute and print the estimate; do not write to current.json.",
    )
    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root

    transcript = args.transcript or find_transcript_for_repo(repo_root)
    if transcript is None:
        print(
            f"[scan-context-telemetry] no transcript found at "
            f"~/.claude/projects/{_encoded_project_dir(repo_root)}/. "
            f"Telemetry capture skipped this session.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    if not transcript.is_file():
        print(
            f"[scan-context-telemetry] transcript path not a file: {transcript}",
            file=sys.stderr,
            flush=True,
        )
        return 0

    text = read_transcript_text(transcript)
    token_estimate, tokenizer_label = tokenize(text)

    print(
        f"[scan-context-telemetry] transcript={transcript.name} "
        f"session_total_tokens~{token_estimate:,} "
        f"(upper-bound; cached+compacted included; not live prompt pressure) "
        f"via {tokenizer_label}",
        flush=True,
    )

    if args.dry_run:
        return 0

    try:
        write_telemetry_to_current(repo_root, token_estimate, tokenizer_label)
    except FileNotFoundError as exc:
        print(
            f"[scan-context-telemetry] {exc}; cannot write telemetry.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
