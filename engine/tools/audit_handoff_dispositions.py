"""Session-shutdown audit for undispositioned HANDOFF.md additions.

Layer 1 contract per ADR 0038 + ADR 0039.

Purpose
-------
Catch the deferral pattern. A new section added to HANDOFF.md during
a session represents work routed to a future session. The pattern
this addresses: the AI finds a bug whose fix is in context, writes
prose in HANDOFF.md describing the bug + the proposed fix for a
future session, and never applies the fix in the current session.
The deferral overhead — prose authoring now plus future re-derivation
of the same details from cold — exceeds the inline-fix cost in
nearly every case. (See CLAUDE.md "Default to fix-in-context.")

Forcing every new HANDOFF.md section to carry an explicit
``**Disposition:**`` line surfaces the choice at authoring time. Five
forms accepted:

- ``fixed-in-session @ <SHA>`` — the bug was fixed in this session;
  the SHA points at the resolving commit (or any commit in this
  session's range — the audit takes the SHA at face value).
- ``deferred-with-user-confirmation`` — user explicitly confirmed
  deferral via a prior chat turn. The session's working_on or diary
  ideally name when.
- ``out-of-scope`` — the entry documents a pattern, anti-pattern, or
  finding that's structurally not a fix-this-now item (e.g., a
  recovery procedure that other sessions might need).
- ``not-actionable`` — informational; no fix exists or no fix is
  warranted given current state.
- ``tracked-as-issue #<num>`` — the work is cross-session deferral
  routed to GitHub Issues per ADR 0048; ``<num>`` is the issue
  number. Used when a HANDOFF section was authored before realizing
  the work belonged in an Issue (or when an existing HANDOFF entry
  is being closed by routing to a fresh Issue).

Inputs
------
This session's HANDOFF.md diff. Range derived from the eager-claim
commit (``chore(session): eager-claim S-NNNN`` subject in recent
git log); diff range is ``<eager-claim-SHA>^..HEAD`` so the diff
covers everything from the commit before the eager-claim through
HEAD. Override via ``--range A..B``.

Detection
---------
The diff is parsed for added section headers (``+## `` at the start
of a diff line). For each new header, the contiguous run of added
``+`` body lines until the next added header or end-of-diff is the
section body. The body is searched for a ``**Disposition:**`` line;
the captured value is validated against the four accepted forms.

Exit codes
----------
- ``0`` — no new HANDOFF.md sections, OR every new section has a
  valid disposition.
- ``2`` — at least one new section is missing or has a malformed
  disposition. Per-section detail goes to stderr; a hint pointing at
  the accepted forms follows.

CLI
---
- ``audit_handoff_dispositions.py`` — default; auto-detect range.
- ``audit_handoff_dispositions.py --range A..B`` — explicit range.
- ``audit_handoff_dispositions.py --list`` — dry-run inspection;
  prints discovered new sections + their dispositions and exits 0.
- ``audit_handoff_dispositions.py --repo-root PATH`` — override the
  repo root for git invocations (test fixture support; production
  defaults to the script's own repo).

Out of scope
------------
- No correctness verification. ``fixed-in-session @ <SHA>`` is taken
  at face value; the audit does not assert the SHA exists, points at
  a commit in this session's range, or that the commit's diff
  actually addresses the named entry.
- No detection on edits to *existing* sections — only newly-added
  section headers are audited. The retrofit cost on existing
  sections (which predate the convention) would be prohibitive.
- No moved-section detection. A section that's deleted from one
  position and re-added at another within the same diff is counted
  as a new section. Cosmetic false positive; acceptable.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EAGER_CLAIM_RE = re.compile(r"^chore\(session\): eager-claim S-\d{4}")

# Match `**Disposition:**` followed by the value on the same line. Captures
# leading/trailing whitespace tolerantly so prose-style entries don't
# accidentally fail the audit.
DISPOSITION_RE = re.compile(
    r"\*\*Disposition:\*\*\s*(\S.*?)\s*$",
    re.MULTILINE,
)

# Five accepted disposition forms — see module docstring.
_VALID_DISPOSITION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^fixed-in-session\s+@\s+\S+$"),
    re.compile(r"^deferred-with-user-confirmation$"),
    re.compile(r"^out-of-scope$"),
    re.compile(r"^not-actionable$"),
    re.compile(r"^tracked-as-issue\s+#\d+$"),
]


@dataclass(frozen=True)
class HandoffSection:
    """One newly-added HANDOFF.md section parsed from a unified diff."""

    header: str
    body: str
    disposition: str | None


def find_eager_claim_sha(repo: Path = REPO_ROOT) -> str | None:
    """Return the SHA of this session's eager-claim commit, or None.

    Scans the most recent 50 commits for a ``chore(session): eager-claim
    S-NNNN`` subject. Mirrors the helper in audit_side_discoveries.py;
    duplicated rather than imported because each audit's session range
    is independently determined and the two files should not couple.
    """
    proc = subprocess.run(
        ["git", "log", "--format=%H %s", "-50"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        sha, _, subject = line.partition(" ")
        if EAGER_CLAIM_RE.match(subject):
            return sha
    return None


def session_diff_range(repo: Path = REPO_ROOT) -> str | None:
    """Return the diff range covering this session's HANDOFF.md changes.

    The range is ``<eager-claim-SHA>^..HEAD`` so it includes everything
    written between the moment the slot was claimed and now. Returns
    None when no eager-claim commit is found in the recent history.
    """
    eager_sha = find_eager_claim_sha(repo)
    if eager_sha is None:
        return None
    return f"{eager_sha}^..HEAD"


def get_handoff_diff(diff_range: str, repo: Path = REPO_ROOT) -> str:
    """Return the unified diff of HANDOFF.md across the range.

    Empty string on git failure (treated downstream as "no diff to
    audit"); the caller decides whether that's pass or fail.
    """
    proc = subprocess.run(
        ["git", "diff", diff_range, "--", "HANDOFF.md"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def parse_added_sections(diff_text: str) -> list[HandoffSection]:
    """Parse newly-added HANDOFF.md sections from a unified diff.

    A "new section" is an added line (``+`` prefix in the unified diff)
    whose content starts with ``## ``. The body is the contiguous run
    of subsequent added lines until the next added section header, or
    until a non-added line breaks the run, or until end of diff.
    """
    sections: list[HandoffSection] = []
    current_header: str | None = None
    current_body_lines: list[str] = []

    for line in diff_text.splitlines():
        # Diff metadata lines: skip without disturbing in-progress section.
        if line.startswith(("+++", "---", "@@", "diff ", "index ")):
            continue
        if line.startswith("+"):
            content = line[1:]
            if content.startswith("## "):
                if current_header is not None:
                    sections.append(_build_section(current_header, current_body_lines))
                current_header = content
                current_body_lines = []
                continue
            if current_header is not None:
                current_body_lines.append(content)
            continue
        # Non-added line ends the in-progress section's body. (Removed
        # lines, context lines, blank-in-diff lines all break continuity.)
        if current_header is not None:
            sections.append(_build_section(current_header, current_body_lines))
            current_header = None
            current_body_lines = []

    if current_header is not None:
        sections.append(_build_section(current_header, current_body_lines))

    return sections


def _build_section(header: str, body_lines: list[str]) -> HandoffSection:
    body = "\n".join(body_lines)
    disposition = _extract_disposition(body)
    return HandoffSection(header=header, body=body, disposition=disposition)


def _extract_disposition(body: str) -> str | None:
    """Return the value following ``**Disposition:**`` in ``body``, or None."""
    match = DISPOSITION_RE.search(body)
    if match is None:
        return None
    return match.group(1).strip()


def is_valid_disposition(value: str) -> bool:
    """Return True when ``value`` matches one of the four accepted forms."""
    return any(pat.match(value) for pat in _VALID_DISPOSITION_PATTERNS)


def find_undispositioned_sections(
    sections: list[HandoffSection],
) -> list[HandoffSection]:
    """Return sections whose disposition is missing or malformed."""
    bad: list[HandoffSection] = []
    for s in sections:
        if s.disposition is None or not is_valid_disposition(s.disposition):
            bad.append(s)
    return bad


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 on clean, 2 on undispositioned sections."""
    parser = argparse.ArgumentParser(
        description=(
            "Audit this session's HANDOFF.md additions for explicit "
            "**Disposition:** lines per CLAUDE.md 'Default to fix-in-context'."
        ),
    )
    parser.add_argument(
        "--range",
        help="Git range to diff (default: auto-detect from eager-claim).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "List discovered new sections + their dispositions and exit 0. "
            "Useful while authoring HANDOFF entries."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help=(
            "Repo root for git invocations. Defaults to the script's own "
            "repo; overridable for test fixtures."
        ),
    )
    args = parser.parse_args(argv)

    repo: Path = args.repo_root

    diff_range = args.range or session_diff_range(repo)
    if diff_range is None:
        print(
            "[audit-handoff-dispositions] no eager-claim found in recent "
            "history; nothing to audit.",
            flush=True,
        )
        return 0

    diff_text = get_handoff_diff(diff_range, repo)
    sections = parse_added_sections(diff_text)

    if args.list:
        if not sections:
            print(
                f"[audit-handoff-dispositions] no new HANDOFF.md sections "
                f"in {diff_range}."
            )
            return 0
        for s in sections:
            disp = s.disposition if s.disposition is not None else "(missing)"
            print(f"  {s.header}")
            print(f"    Disposition: {disp}")
        return 0

    bad = find_undispositioned_sections(sections)

    if not bad:
        n = len(sections)
        if n == 0:
            print(
                "[audit-handoff-dispositions] no new HANDOFF.md sections; "
                "nothing to audit."
            )
        else:
            print(
                f"[audit-handoff-dispositions] {n} new section(s) found, "
                "all with valid dispositions."
            )
        return 0

    print(
        f"[audit-handoff-dispositions] {len(bad)} new HANDOFF.md "
        f"section(s) missing a valid **Disposition:** line:",
        file=sys.stderr,
    )
    for s in bad:
        print(f"  - {s.header}", file=sys.stderr)
        if s.disposition is None:
            print("      no disposition found in section body", file=sys.stderr)
        else:
            print(
                f"      unrecognized disposition: {s.disposition!r}",
                file=sys.stderr,
            )
    print("", file=sys.stderr)
    print(
        "Per CLAUDE.md 'Default to fix-in-context', every new HANDOFF.md",
        file=sys.stderr,
    )
    print("section must carry one of these disposition lines:", file=sys.stderr)
    print("  - **Disposition:** fixed-in-session @ <SHA>", file=sys.stderr)
    print(
        "  - **Disposition:** deferred-with-user-confirmation",
        file=sys.stderr,
    )
    print("  - **Disposition:** out-of-scope", file=sys.stderr)
    print("  - **Disposition:** not-actionable", file=sys.stderr)
    print("  - **Disposition:** tracked-as-issue #<num>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
