"""Scan the GitHub Issues backlog for boot-time visibility.

Layer 1 contract per ADR 0048.

Purpose
-------
Surface the open Issues backlog at session boot so the user can see
backlog growth across sessions and dedicate cleanup-batch sessions
when the count crosses a threshold worth addressing.

Two surfaces:

- Default FYI line, always shown:
  ``[session-start] Issues backlog: N bugs, N tech-debt, N cleanup,
  N enhancement, N health-check, N docs, N question
  (M urgent; K upstream-blocked).`` Updated at S-0051: emits 7 type
  categories instead of the original 4 (`health-check-finding`,
  `documentation`, `question` added). Bugs that are also tagged
  `upstream` are subtracted from the bug count and surfaced
  separately as `upstream-blocked` in the parenthetical, so the
  reader sees in-project actionable bugs rather than a noise-padded
  total. See ADR 0048 Consequences amendment at S-0051.
- Urgent LOUD block, only when ``priority:urgent`` count > 0:
  multi-line attention block listing each urgent issue's number,
  title, and non-priority labels. Same surface treatment as ADR 0045's
  hard-broken probe findings.

Exit codes
----------
- ``0`` — backlog scanned cleanly OR ``gh`` failed and the failure was
  surfaced to stderr (best-effort visibility).

The non-zero path is reserved; the scanner is intentionally
non-blocking.

CLI
---
- ``scan_issue_backlog.py`` — default; emit FYI + optional LOUD to stdout.
- ``scan_issue_backlog.py --json`` — emit raw JSON of label counts +
  urgent issues (test fixture support; production hook uses default).
- ``scan_issue_backlog.py --repo PATH`` — pass-through to ``gh -R``;
  defaults to current-repo auto-detection.

Out of scope
------------
- No issue creation, editing, or closing.
- No filtering beyond the standard label set; surfacing of arbitrary
  labels is not promised.
- No retry on ``gh`` failure; one shot, surface and proceed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


# Label taxonomy per ADR 0048 + issue-discipline.md. Keys are the
# canonical label names; values are the human-readable forms used in
# the FYI line. Extended at S-0051 (issue-discipline.md taxonomy
# additions): documentation, question.
TYPE_LABELS: dict[str, str] = {
    "bug": "bugs",
    "tech-debt": "tech-debt",
    "cleanup": "cleanup",
    "enhancement": "enhancement",
    "health-check-finding": "health-check",
    "upstream": "upstream",
    "documentation": "docs",
    "question": "question",
}
PRIORITY_LABEL = "priority:urgent"
UPSTREAM_LABEL = "upstream"
HEALTH_CHECK_FINDING_LABEL = "health-check-finding"

# Regex matching audit-report cross-references inside an issue body.
# Both forms covered: full GitHub URL
# (`https://github.com/<org>/<repo>/blob/<ref>/engine/docs/audits/<file>.md`)
# and bare relative path (`engine/docs/audits/<file>.md`). Captures the
# filename only — distinct filenames form the count of "active audits"
# in the surface line. Non-greedy and bounded to `.md` to avoid greedy
# trailing punctuation.
_AUDIT_REF_RE = re.compile(r"engine/docs/audits/([\w\-]+\.md)")


def fetch_open_issues(repo: str | None = None) -> list[dict[str, Any]] | None:
    """Return a list of open issues, or None on gh failure.

    Each issue dict carries ``number``, ``title``, ``labels``, ``body``.
    ``labels`` is a list of dicts with at least a ``name`` key
    (matching gh's JSON shape).
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
        "number,title,labels,body",
    ]
    if repo:
        cmd.extend(["-R", repo])
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


def label_names(issue: dict[str, Any]) -> list[str]:
    """Return the list of label names on an issue (handling missing fields)."""
    labels = issue.get("labels", [])
    return [lbl.get("name", "") for lbl in labels if isinstance(lbl, dict)]


def count_by_label(issues: list[dict[str, Any]]) -> dict[str, int]:
    """Return per-label counts for the canonical type-label set."""
    counts: dict[str, int] = {label: 0 for label in TYPE_LABELS}
    for issue in issues:
        names = label_names(issue)
        for label in TYPE_LABELS:
            if label in names:
                counts[label] += 1
    return counts


def count_upstream_bugs(issues: list[dict[str, Any]]) -> int:
    """Return count of issues tagged BOTH ``bug`` AND ``upstream``.

    Used to subtract upstream-blocked bugs from the actionable bug
    count in the FYI line, so a reader sees the in-project bug
    backlog rather than a noise-padded total. Pure on the input
    issue list.
    """
    return sum(
        1
        for issue in issues
        if "bug" in label_names(issue) and UPSTREAM_LABEL in label_names(issue)
    )


def collect_urgent(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return issues carrying the ``priority:urgent`` label."""
    return [issue for issue in issues if PRIORITY_LABEL in label_names(issue)]


def collect_audit_lineage(
    issues: list[dict[str, Any]],
) -> tuple[list[str], int]:
    """Return distinct audit-report filenames + count of health-check-finding issues.

    Filters issues by the ``health-check-finding`` label, then extracts
    audit-report cross-references from each issue's body via the
    ``engine/docs/audits/<file>.md`` pattern (matches both GitHub URL
    and bare relative-path forms). Returns (sorted distinct audit
    filenames, total count of filtered issues).

    An issue without a detectable audit cross-reference still counts
    toward the recommendation tally — it's a recommendation even if
    its lineage isn't machine-recoverable. The line surface clarifies
    the relationship: ``N audits, M recommendations`` may have ``M >=
    N`` (typical) or ``M > 0, N == 0`` (issues exist but their bodies
    don't cite an audit report).

    Per Issue #47 (S-0088). The audit lineage gives the boot surface
    a structural anchor: future audits at the cadence cycle spawn new
    `health-check-finding`-labeled Issues; this surface preserves the
    audit → recommendation lineage so the user sees which audits are
    still open without having to dig into the undifferentiated backlog
    count.
    """
    relevant = [
        issue for issue in issues if HEALTH_CHECK_FINDING_LABEL in label_names(issue)
    ]
    audits: set[str] = set()
    for issue in relevant:
        body = issue.get("body") or ""
        audits.update(_AUDIT_REF_RE.findall(body))
    return sorted(audits), len(relevant)


def format_fyi_line(
    counts: dict[str, int], urgent_count: int, upstream_bug_count: int = 0
) -> str:
    """Build the single-line FYI surface.

    Updated at S-0051: emits 7 type categories instead of 4. ``upstream``
    is no longer in the type list (it's a modifier, not a type) and
    instead surfaces in the parenthetical alongside ``urgent``. Bugs
    that are also tagged ``upstream`` are subtracted from the bug
    count via ``upstream_bug_count`` so the surface shows in-project
    actionable bugs, not the noise-padded total.
    """
    in_project_bugs = max(0, counts.get("bug", 0) - upstream_bug_count)
    parts = [
        f"{in_project_bugs} bugs",
        f"{counts['tech-debt']} tech-debt",
        f"{counts['cleanup']} cleanup",
        f"{counts['enhancement']} enhancement",
        f"{counts['health-check-finding']} health-check",
        f"{counts['documentation']} docs",
        f"{counts['question']} question",
    ]
    base = ", ".join(parts)
    upstream_total = counts.get("upstream", 0)
    return (
        f"[session-start] Issues backlog: {base} "
        f"({urgent_count} urgent; {upstream_total} upstream-blocked)."
    )


def format_audit_trail_line(
    audits: list[str], recommendation_count: int
) -> list[str] | None:
    """Build the audit-trail surface; return None when no findings present.

    When `health-check-finding`-labeled Issues exist, emits:
    ``[session-start] Active health-check audits: N (M open recommendations).``
    plus one indented line per audit report path so the AI can `Read`
    the audit context if the next-session work intersects.

    Returns ``None`` when ``recommendation_count == 0`` so the call
    site can suppress the line entirely on a clean backlog. Keeps the
    boot surface noise-free until findings actually exist.
    """
    if recommendation_count == 0:
        return None
    lines = [
        f"[session-start] Active health-check audits: {len(audits)} "
        f"({recommendation_count} open recommendations)."
    ]
    for filename in audits:
        lines.append(f"  engine/docs/audits/{filename}")
    return lines


def format_loud_block(urgent_issues: list[dict[str, Any]]) -> list[str]:
    """Build the multi-line LOUD attention block for urgent issues."""
    lines: list[str] = []
    lines.append("")
    lines.append("=" * 72)
    lines.append(
        f"[session-start] URGENT: {len(urgent_issues)} open issue(s) "
        f"flagged priority:urgent. Review before substantive work:"
    )
    for issue in urgent_issues:
        num = issue.get("number", "?")
        title = issue.get("title", "(no title)")
        non_priority = [n for n in label_names(issue) if n != PRIORITY_LABEL]
        label_str = f" [{', '.join(non_priority)}]" if non_priority else ""
        lines.append(f"  #{num}: {title}{label_str}")
    lines.append("=" * 72)
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan GitHub Issues backlog for boot-time visibility per ADR 0048."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON of counts + urgent issues (test fixture support).",
    )
    parser.add_argument(
        "--repo",
        help="Pass-through to gh -R (defaults to current-repo auto-detect).",
    )
    args = parser.parse_args(argv)

    issues = fetch_open_issues(args.repo)
    if issues is None:
        # gh failed — best-effort visibility, surface a stderr note,
        # exit 0 so the boot proceeds.
        print(
            "[scan-issue-backlog] gh issue list failed; backlog visibility "
            "skipped this boot. Check `gh auth status` and network.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    counts = count_by_label(issues)
    urgent = collect_urgent(issues)
    upstream_bug_count = count_upstream_bugs(issues)
    audits, recommendation_count = collect_audit_lineage(issues)

    if args.json:
        json.dump(
            {
                "counts": counts,
                "urgent_count": len(urgent),
                "upstream_bug_count": upstream_bug_count,
                "urgent": [
                    {
                        "number": i.get("number"),
                        "title": i.get("title"),
                        "labels": label_names(i),
                    }
                    for i in urgent
                ],
                "audits": audits,
                "recommendation_count": recommendation_count,
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 0

    print(format_fyi_line(counts, len(urgent), upstream_bug_count), flush=True)
    audit_lines = format_audit_trail_line(audits, recommendation_count)
    if audit_lines is not None:
        for line in audit_lines:
            print(line, flush=True)
    if urgent:
        for line in format_loud_block(urgent):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
