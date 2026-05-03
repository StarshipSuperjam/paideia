"""Session-shutdown audit for undispositioned side-discoveries.

Layer 1 contract per ADR 0038 + ADR 0039.

Purpose
-------
Catch undispositioned side-discoveries before session close. Fires from
the shutdown sequence as a gate; exits non-zero when any discovered
marker lacks a recorded disposition. The pattern this addresses:
side-discoveries the AI flags during a session land in commit messages
or end-of-session prose ("flagged for follow-up") and vanish without a
mechanical surface that triggers future action. Naming an explicit
disposition for each match forces the AI to either route the discovery
to the right surface (engine/scheduled_audits.json,
product/docs/tensions.md, HANDOFF.md, an inline fix-commit) or
explicitly accept it as a no-op with stated reasoning.

Inputs
------
This session's commit messages: range derived from
engine/session/current.json. The eager-claim commit is identified by
its ``chore(session): eager-claim S-NNNN`` subject and excluded from
scanning (its body is template, not session content).

Dispositions: read from engine/session/current.json's
``side_discoveries`` field (list; default empty).

Markers scanned (case-insensitive whole-word):
``flagged``, ``follow-up``, ``follow up``, ``TODO``, ``FIXME``,
``deferred``, ``noted for``, ``future session``, ``next session``,
``pending``, ``out of scope``.

Negation filter: a marker preceded within ~12 chars by ``no`` /
``not`` / ``nothing`` / ``no longer`` is skipped. Marker-as-noun usage
(``the TODO comment was removed``) is not filtered by the scanner;
those false positives use ``acceptable_no_action`` dispositions.

Disposition shape
-----------------
Each entry in ``current.json``'s ``side_discoveries`` list:

.. code-block:: json

    {
      "commit": "<7-char SHA prefix>",
      "marker": "<phrase that matched, lowercased>",
      "disposition_type": "scheduled_audit | tension_oq | handoff_section | addressed_inline | acceptable_no_action",
      "disposition_ref": "<id, OQ name, section heading, fix-commit SHA, or empty>",
      "reasoning": "<optional; required for acceptable_no_action>"
    }

Match key: ``(commit-SHA-7-prefix, marker-text-lower)``. Multiple
identical markers in one commit are covered by a single disposition.
Multiple distinct markers in one commit get separate dispositions.

Exit codes
----------
- ``0`` if no markers found OR every marker is dispositioned.
- ``2`` if any marker is undispositioned. The script prints per-marker
  ``commit / marker / surrounding-context`` to stderr plus a hint
  pointing at the disposition shape.

CLI
---
- ``audit_side_discoveries.py`` — default; range from current.json,
  dispositions from current.json.
- ``audit_side_discoveries.py --range A..B`` — override git range.
- ``audit_side_discoveries.py --dispositions PATH`` — override
  dispositions file (must contain a top-level ``side_discoveries`` list).
- ``audit_side_discoveries.py --list`` — dry-run; prints discovered
  markers (one per line) and exits 0; useful while authoring
  dispositions.

Out of scope
------------
- No staged-diff scanning — markers must appear in commit messages, not
  in the diff body.
- No GitHub / Linear / external-tracker integration.
- No auto-creation of dispositions; entries are hand-authored.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_JSON = REPO_ROOT / "engine" / "session" / "current.json"

EAGER_CLAIM_RE = re.compile(r"^chore\(session\): eager-claim S-\d{4}")

_MARKER_PATTERNS: list[str] = [
    r"\bflagged\b",
    r"\bfollow-up\b",
    r"\bfollow up\b",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bdeferred\b",
    r"\bnoted for\b",
    r"\bfuture session\b",
    r"\bnext session\b",
    r"\bpending\b",
    r"\bout of scope\b",
]
MARKER_RE = re.compile("|".join(_MARKER_PATTERNS), re.IGNORECASE)
NEGATION_RE = re.compile(r"\b(no|not|nothing|no\s+longer)\s+$", re.IGNORECASE)

_RECORD_SEP = "\x1e"


@dataclass(frozen=True)
class Marker:
    """One marker hit in a commit message."""

    commit: str  # 7-char SHA prefix, lowercase
    marker: str  # matched phrase, lowercased, internal whitespace collapsed
    context: str  # ~60 chars surrounding the match, with newlines stripped


@dataclass(frozen=True)
class Disposition:
    """One entry from current.json's side_discoveries list."""

    commit: str
    marker: str
    disposition_type: str
    disposition_ref: str
    reasoning: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Disposition:
        commit_raw = str(data["commit"])
        return cls(
            commit=commit_raw[:7].lower(),
            marker=re.sub(r"\s+", " ", str(data["marker"]).strip().lower()),
            disposition_type=str(data["disposition_type"]),
            disposition_ref=str(data.get("disposition_ref", "")),
            reasoning=str(data.get("reasoning", "")),
        )


def find_eager_claim_sha(repo_root: Path) -> str | None:
    """Return the most recent eager-claim commit SHA, or None."""
    proc = subprocess.run(
        ["git", "log", "--format=%H %s", "-50"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        sha, _, subject = line.partition(" ")
        if EAGER_CLAIM_RE.match(subject):
            return sha
    return None


def session_range(repo_root: Path) -> str:
    """Return ``<eager-claim-SHA>..HEAD`` for the current session.

    Raises ``RuntimeError`` if no eager-claim commit is visible in the
    last 50 commits.
    """
    sha = find_eager_claim_sha(repo_root)
    if sha is None:
        raise RuntimeError(
            "No eager-claim commit found in the last 50 commits. Either "
            "this is not a build session or the eager-claim subject "
            "pattern has drifted. Use --range to override."
        )
    return f"{sha}..HEAD"


def commits_in_range(repo_root: Path, git_range: str) -> list[tuple[str, str]]:
    """Return ``[(sha, full-message-text)]`` for the range."""
    fmt = f"%H%n%B{_RECORD_SEP}"
    proc = subprocess.run(
        ["git", "log", f"--format={fmt}", git_range],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    records = [r.strip() for r in proc.stdout.split(_RECORD_SEP) if r.strip()]
    out: list[tuple[str, str]] = []
    for record in records:
        sha, _, message = record.partition("\n")
        out.append((sha, message))
    return out


def is_negated(text: str, match_start: int) -> bool:
    """True if the match is preceded within ~12 chars by no/not/nothing/no longer."""
    prefix = text[max(0, match_start - 12) : match_start]
    return bool(NEGATION_RE.search(prefix))


def scan_markers(commits: list[tuple[str, str]]) -> list[Marker]:
    """Return every undeniable marker hit across the given commits."""
    found: list[Marker] = []
    for sha, message in commits:
        for match in MARKER_RE.finditer(message):
            if is_negated(message, match.start()):
                continue
            phrase = re.sub(r"\s+", " ", match.group(0).strip().lower())
            ctx_start = max(0, match.start() - 30)
            ctx_end = min(len(message), match.end() + 30)
            ctx = re.sub(r"\s+", " ", message[ctx_start:ctx_end]).strip()
            found.append(Marker(commit=sha[:7].lower(), marker=phrase, context=ctx))
    return found


def load_dispositions(path: Path) -> list[Disposition]:
    """Load dispositions from a JSON file's ``side_discoveries`` field.

    Returns an empty list if the file does not exist or does not contain
    the field. Raises ``json.JSONDecodeError`` on malformed JSON;
    ``KeyError`` on entries missing required fields.
    """
    if not path.exists():
        return []
    with path.open() as f:
        data = json.load(f)
    raw = data.get("side_discoveries", [])
    if not isinstance(raw, list):
        raise ValueError(
            f"{path}: 'side_discoveries' must be a list (got {type(raw).__name__})"
        )
    return [Disposition.from_dict(d) for d in raw]


def match_dispositions(
    markers: list[Marker], dispositions: list[Disposition]
) -> list[Marker]:
    """Return the markers that have no matching disposition."""
    keys = {(d.commit, d.marker) for d in dispositions}
    return [m for m in markers if (m.commit, m.marker) not in keys]


def _print_undispositioned(undisp: list[Marker]) -> None:
    print(
        f"[audit-side-discoveries] {len(undisp)} undispositioned marker(s):",
        file=sys.stderr,
    )
    for m in undisp:
        print(
            f"  commit={m.commit} marker={m.marker!r}\n    context: ...{m.context}...",
            file=sys.stderr,
        )
    print(
        "\nDisposition each in engine/session/current.json's `side_discoveries` list:\n"
        "  {\n"
        '    "commit": "<7-char SHA prefix>",\n'
        '    "marker": "<phrase that matched, lowercased>",\n'
        '    "disposition_type": "scheduled_audit | tension_oq | handoff_section | addressed_inline | acceptable_no_action",\n'
        '    "disposition_ref": "<id, OQ name, section heading, fix-commit SHA, or empty>",\n'
        '    "reasoning": "<optional; required for acceptable_no_action>"\n'
        "  }",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit_side_discoveries.py",
        description=(
            "Audit this session's commit messages for undispositioned "
            "side-discoveries (per S-0033 HANDOFF.md Item 2)."
        ),
    )
    parser.add_argument(
        "--range",
        dest="git_range",
        default=None,
        help="Override git range (default: <eager-claim-SHA>..HEAD).",
    )
    parser.add_argument(
        "--dispositions",
        type=Path,
        default=None,
        help=f"Override dispositions file (default: {DEFAULT_CURRENT_JSON}).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print discovered markers without enforcing dispositions; exits 0.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    git_range: str = args.git_range or session_range(args.repo_root)
    commits = commits_in_range(args.repo_root, git_range)
    markers = scan_markers(commits)

    if args.list:
        for m in markers:
            print(f"{m.commit} {m.marker} :: {m.context}")
        return 0

    disp_path: Path = args.dispositions or DEFAULT_CURRENT_JSON
    dispositions = load_dispositions(disp_path)
    undisp = match_dispositions(markers, dispositions)

    if not undisp:
        print(
            f"[audit-side-discoveries] {len(markers)} marker(s) found, "
            "all dispositioned."
        )
        return 0

    _print_undispositioned(undisp)
    return 2


if __name__ == "__main__":
    sys.exit(main())
