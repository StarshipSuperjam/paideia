"""Scan open Issues for keyword/path overlap with this session's scope.

Layer 1 contract per ADR 0048 + ADR 0049 + S-0143 Issue #110 refinement.

Purpose
-------
Catch the case where a session is about to touch files or topics that
an open Issue has flagged as broken. Soft-warn so the user/AI can
decide: fix the colliding issue first, work on it in parallel, or
proceed (the existing scope is independent).

Strategy
--------
1. Read ``declared_scope`` from ``engine/session/current.json``.
   Extract keywords (whitespace-tokenized, lowercase, drop stopwords).
2. Collect file paths from ``git diff --cached --name-only`` (the
   first-commit's staged files).
3. Query open Issues via ``gh issue list`` (with labels).
4. **Filter out structurally-non-actionable Issues** (per S-0143 / Issue
   #110): Issues carrying the ``upstream`` label (not in-project
   actionable per ADR 0048's cleanup-batch discipline) and Issues whose
   titles match the trigger-gate marker pattern ``[TRIGGER: ...]`` (the
   work is gated on a future external condition that hasn't fired yet).
5. For each remaining Issue, soft-warn if the body or title contains
   either an extracted keyword OR a touched file path.

Exit codes
----------
- ``0`` — no collisions detected, OR ``gh`` failed (silent skip).
- ``1`` — at least one collision; ``validate.py`` translates this into
  the ``issue_collision`` soft-warn category per
  ``engine/operations/tools-validate-interpretation.md``.

Wired from ``validate.py`` on first-commit-after-eager-claim. Standalone
invocation also supported for ad-hoc runs.

CLI
---
- ``scan_issue_collisions.py`` — default; auto-detect repo, current.json,
  staged files.
- ``scan_issue_collisions.py --json`` — emit machine-readable findings.
- ``scan_issue_collisions.py --repo-root PATH`` — override repo root.
- ``scan_issue_collisions.py --gh-repo OWNER/NAME`` — pass-through to
  gh -R.

Out of scope
------------
- No issue creation, editing, or closing.
- Stopword list expanded at S-0195 per Issue #141 after the T3-C
  noisy-warn gate fired (10+ collision warns in 10 consecutive sessions
  S-0184 through S-0193). The set below adds Paideia-specific
  infrastructure terms that pervade every session's commit messages
  ("engine", "operations", "tools", "session", "commit", "audit", ...)
  without being load-bearing match anchors. Confidence-tier split (the
  shape-A complement) waits on Issue #133 landing the general
  persistent-warn bucket framework.
- No matching against Issues in closed state.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]
CURRENT_JSON = "engine/session/current.json"

# Stopword list. Two strata:
#   * Generic English function words (small core unchanged since
#     authoring).
#   * Paideia-infrastructure terms added at S-0195 per Issue #141.
#     The T3-C noisy-warn gate fired with 10+ collisions/session across
#     S-0184–S-0193 dominated by generic infra words that appear in
#     every commit message ("engine", "operations", "tools", ...).
#     These words are not load-bearing match anchors — a collision
#     surfaces meaningfully only when a substantive identifier (file
#     path, named symbol, domain term) overlaps with an Issue body.
_STOPWORDS = frozenset(
    {
        # Generic English function words
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
        # Pre-S-0195 Paideia anchors
        "phase",
        "session",
        "scope",
        # S-0195 expansion per Issue #141 — words named in the Issue
        # body that pervade every session's commit-message scope.
        "tool",
        "tools",
        "docs",
        "commit",
        "audit",
        "engine",
        "operations",
        "close",
        "closing",
        "add",
        "update",
        "extend",
        "file",
        "call",
        "verify",
        "verification",
        "status",
        "step",
        "against",
        "archive",
        # S-0195 expansion — additional infra terms observed in the
        # S-0193/S-0194/S-0195 collision-warn surfaces that match the
        # same "generic infrastructure" shape (high frequency, no
        # discriminating power in a collision context).
        "github",
        "issues",
        "each",
        "claude",
        "work",
        "pass",
        "state",
        "json",
        "since",
        "either",
        "follow-up",
        "rewrite",
        "tuning",
        "touch",
        "landing",
        "plus",
        "requires",
        "consequences",
        "amendment",
    }
)

# Words we consider too short to be meaningful match anchors.
_MIN_KEYWORD_LEN = 4

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]+")

# Trigger-gate marker pattern (per S-0143 / Issue #110). Issues whose
# titles carry "[TRIGGER: <condition>]" are gated on a future external
# condition and are not in-project actionable until the condition fires.
# Pre-S-0143 these collided constantly with sessions that touched
# adjacent scope without intending to act on the gated work; the filter
# reduces noise without losing signal (when the gate fires, the title
# is rewritten to drop the marker, restoring matchability).
_TRIGGER_TITLE_RE = re.compile(r"\[TRIGGER:\s")

# Labels that signal "not in-project actionable now" (per ADR 0048).
# `upstream` is the bug-is-elsewhere lane the cleanup-batch discipline
# explicitly says NOT to pick up; matching against it produces noise
# without producing acted-on signal. Extend this set if new
# not-actionable-now labels emerge (e.g., a future `blocked` /
# `external-dependency` lane).
_NON_ACTIONABLE_LABELS = frozenset({"upstream"})


@dataclass(frozen=True)
class Collision:
    """One open issue colliding with this session's scope."""

    issue_number: int
    issue_title: str
    matches: tuple[str, ...]  # The matched keywords / paths.


def read_declared_scope(repo_root: Path) -> str:
    """Return the scope prose for collision-matching, or empty.

    Prefers ``declared_scope`` (added by ADR 0049). Falls back to
    ``working_on`` for sessions that pre-date ADR 0049 or that haven't
    written the new field yet. Empty when neither is present or the file
    is missing.
    """
    path = repo_root / CURRENT_JSON
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return ""
    scope = data.get("declared_scope")
    if isinstance(scope, str) and scope:
        return scope
    fallback = data.get("working_on")
    return fallback if isinstance(fallback, str) else ""


def extract_keywords(scope: str) -> set[str]:
    """Tokenize, lowercase, drop stopwords + short tokens.

    Returns a set so duplicate hits in different parts of the scope
    don't double-count.
    """
    tokens = _WORD_RE.findall(scope.lower())
    keywords: set[str] = set()
    for tok in tokens:
        if tok in _STOPWORDS:
            continue
        if len(tok) < _MIN_KEYWORD_LEN:
            continue
        keywords.add(tok)
    return keywords


def staged_files(repo_root: Path) -> list[str]:
    """Return repo-relative paths of files staged for the next commit."""
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def fetch_open_issues(gh_repo: str | None = None) -> list[dict[str, Any]] | None:
    """Return open issues as a list of dicts, or None on gh failure.

    Includes the `labels` field (per S-0143 / Issue #110) so downstream
    filtering can skip Issues marked `upstream` etc. without an extra
    round-trip.
    """
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        "open",
        "--limit",
        "1000",
        "--json",
        "number,title,body,labels",
    ]
    if gh_repo:
        cmd.extend(["-R", gh_repo])
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if proc.returncode != 0:
        return None
    try:
        return cast(list[dict[str, Any]], json.loads(proc.stdout))
    except json.JSONDecodeError:
        return None


def is_actionable_now(issue: dict[str, Any]) -> bool:
    """True when the Issue is in-project actionable AND not trigger-gated.

    Skip criteria (per S-0143 / Issue #110):
      - Carries any label in ``_NON_ACTIONABLE_LABELS`` (e.g., `upstream`).
      - Title matches ``_TRIGGER_TITLE_RE`` (carries `[TRIGGER: ...]`).

    Returns False for skip candidates; True otherwise. Issues missing
    `labels` (legacy gh response shape) default to actionable.
    """
    title = issue.get("title") or ""
    if _TRIGGER_TITLE_RE.search(title):
        return False

    labels = issue.get("labels") or []
    if isinstance(labels, list):
        label_names = {
            entry.get("name", "").lower() for entry in labels if isinstance(entry, dict)
        }
        if label_names & _NON_ACTIONABLE_LABELS:
            return False

    return True


def find_collisions(
    issues: list[dict[str, Any]],
    keywords: set[str],
    paths: list[str],
) -> list[Collision]:
    """Match each issue's body/title against keywords + paths.

    Path matching is exact substring; keyword matching is case-insensitive
    word boundary (the keyword surrounded by non-word characters or
    line edges).
    """
    collisions: list[Collision] = []
    for issue in issues:
        body = (issue.get("body") or "").lower()
        title = (issue.get("title") or "").lower()
        haystack = f"{title}\n{body}"

        matches: list[str] = []

        # Path matches: exact substring.
        for path in paths:
            if path.lower() in haystack:
                matches.append(path)

        # Keyword matches: word-boundary regex, deduplicated against paths.
        for keyword in keywords:
            # Skip if the keyword is part of an already-matched path
            # (avoids double-reporting the same collision).
            if any(keyword in p.lower() for p in matches):
                continue
            pattern = re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)")
            if pattern.search(haystack):
                matches.append(keyword)

        if matches:
            collisions.append(
                Collision(
                    issue_number=int(issue.get("number", 0)),
                    issue_title=issue.get("title", "(no title)"),
                    matches=tuple(matches),
                )
            )
    return collisions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan open GitHub Issues for keyword/path overlap with this "
            "session's declared_scope and staged-files. Per ADR 0048 + 0049."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable findings.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (defaults to script's repo).",
    )
    parser.add_argument(
        "--gh-repo",
        help="Pass-through to gh -R (defaults to current-repo auto-detect).",
    )
    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root

    scope = read_declared_scope(repo_root)
    keywords = extract_keywords(scope)
    paths = staged_files(repo_root)

    if not keywords and not paths:
        # Nothing to match against; clean exit. (Common when the field
        # hasn't been written yet or the diff is empty.)
        return 0

    issues = fetch_open_issues(args.gh_repo)
    if issues is None:
        print(
            "[scan-issue-collisions] gh issue list failed; collision check "
            "skipped this commit.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    # Filter out structurally-non-actionable Issues (per S-0143 / Issue #110):
    # `upstream`-labeled (cleanup-batch discipline says skip per ADR 0048)
    # and trigger-gated (`[TRIGGER: ...]` title prefix; gated work whose
    # external condition hasn't fired yet).
    actionable_issues = [i for i in issues if is_actionable_now(i)]

    collisions = find_collisions(actionable_issues, keywords, paths)

    if args.json:
        json.dump(
            {
                "scope_keywords": sorted(keywords),
                "staged_paths": paths,
                "collisions": [
                    {
                        "number": c.issue_number,
                        "title": c.issue_title,
                        "matches": list(c.matches),
                    }
                    for c in collisions
                ],
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 1 if collisions else 0

    if not collisions:
        return 0

    for c in collisions:
        match_str = ", ".join(c.matches)
        print(
            f"[scan-issue-collisions] Open issue #{c.issue_number} "
            f'"{c.issue_title}" appears to touch this session\'s scope: '
            f"{match_str}.",
            file=sys.stderr,
            flush=True,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
