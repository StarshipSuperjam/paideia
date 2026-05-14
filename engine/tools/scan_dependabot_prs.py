"""Scan open Dependabot PRs for boot-time visibility.

Per ADR 0080 (engine), S-0147. Sibling to ``scan_issue_backlog.py``.
Closes the gap that allowed Dependabot PRs to sit invisible after
ADR 0069 adoption: the boot surface counts Issues, never queries
``gh pr list``, so the "user merges" posture had no escalation path.

Purpose
-------
Surface the open-Dependabot-PR count + age at every session boot. Two
modes:

- Quiet (0 PRs): no output line.
- FYI (1–4 PRs, all <7d): single-line FYI naming the count + oldest age.
- LOUD (≥5 PRs OR any ≥7d): multi-line attention block listing each PR
  with age, mergeable status, and a one-line next-action hint.

Threshold rationale (7 days): one full Dependabot weekly cadence per
``.github/dependabot.yml``. A PR uncrossed across one Monday refresh is
stale by definition; the per-PR next-action hint points the AI toward
the procedure in ``engine/operations/dependency-discipline.md``.

Exit codes
----------
- ``0`` — scan succeeded OR gh failed gracefully (stderr note emitted).

The non-zero path is reserved; the scanner is intentionally
non-blocking — mirrors ``scan_issue_backlog.py`` discipline.

CLI
---
- ``scan_dependabot_prs.py`` — default; emit FYI / LOUD / quiet to
  stdout.
- ``scan_dependabot_prs.py --json`` — emit JSON of PR list + thresholds
  (test fixture support; production hook uses default).
- ``scan_dependabot_prs.py --repo PATH`` — pass-through to ``gh -R``;
  defaults to current-repo auto-detection.
- ``scan_dependabot_prs.py --simulate-age N`` — for testing: override
  PR ages to ``N`` days each. Production hook never sets.

Out of scope
------------
- No PR closing, merging, or commenting.
- No filtering by PR title content; all open Dependabot-authored PRs
  surface.
- No retry on gh failure; one shot.
- Not a substitute for ``validate_dependabot_pr_stale`` in
  ``validate.py`` — the validator soft-warn records to
  ``outcome_summary`` for cross-session persistent-warn tracking; this
  scanner is boot-time visibility.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


# 7 days = one full Dependabot weekly cadence per .github/dependabot.yml.
# A PR open across one Monday refresh is stale.
STALE_AGE_DAYS = 7

# ≥5 open PRs trips LOUD even if all are fresh; signals batch attention.
LOUD_COUNT_THRESHOLD = 5

# The Dependabot author login. GitHub shows it as "dependabot[bot]" in
# the UI but the API returns "app/dependabot".
DEPENDABOT_AUTHOR = "app/dependabot"


def fetch_open_prs(repo: str | None = None) -> list[dict[str, Any]] | None:
    """Return list of open Dependabot PRs, or None on gh failure.

    Each PR dict carries ``number``, ``title``, ``createdAt``,
    ``mergeable``, ``headRefName``.
    """
    cmd = [
        "gh",
        "pr",
        "list",
        "--author",
        DEPENDABOT_AUTHOR,
        "--state",
        "open",
        "--limit",
        "100",
        "--json",
        "number,title,createdAt,mergeable,headRefName",
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


def age_days(created_at: str, now: datetime | None = None) -> int:
    """Return integer days between created_at (ISO-8601 UTC) and now.

    Pure function — `now` defaults to current UTC for production but is
    injectable for tests.
    """
    now = now or datetime.now(timezone.utc)
    # gh emits "2026-05-12T16:03:27Z" — replace trailing Z for fromisoformat.
    # Allowlisted in validate.py's _TIMESTAMP_HELPER_BYPASS_ALLOWLIST per
    # ADR 0058: this parses gh's external wire format, not an engine-canonical
    # stored timestamp, so timestamps.parse() (which knows engine shapes) does
    # not apply.
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (now - created).days


def next_action_hint(pr: dict[str, Any]) -> str:
    """Return a one-line next-action hint based on the PR title shape.

    Categories: github-actions bump, pip major-version bump, pip
    minor-or-patch bump. The hint points to the procedure in
    ``engine/operations/dependency-discipline.md``.
    """
    title = pr.get("title", "")
    head_ref = pr.get("headRefName", "")
    if head_ref.startswith("dependabot/github_actions/"):
        return "verify action release notes; merge"
    if "minor" in title.lower() or "patch" in title.lower():
        return "regenerate uv.lock and merge"
    # Default: major bump (pip ecosystem)
    return "major bump — verify ADR 0069 contract; regenerate uv.lock"


def classify(prs: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any]:
    """Return a dict describing the scan outcome.

    Keys:
      - ``count``: total open PR count
      - ``oldest_age``: integer days of the oldest open PR (-1 when count=0)
      - ``stale_prs``: list of PRs (sorted oldest-first) with age ≥
        STALE_AGE_DAYS
      - ``mode``: ``quiet`` | ``fyi`` | ``loud``
    """
    count = len(prs)
    if count == 0:
        return {"count": 0, "oldest_age": -1, "stale_prs": [], "mode": "quiet"}

    ages = [(pr, age_days(pr["createdAt"], now)) for pr in prs]
    ages.sort(key=lambda pa: pa[1], reverse=True)
    oldest_age = ages[0][1]
    stale = [pr for pr, a in ages if a >= STALE_AGE_DAYS]

    if count >= LOUD_COUNT_THRESHOLD or stale:
        mode = "loud"
    else:
        mode = "fyi"

    return {
        "count": count,
        "oldest_age": oldest_age,
        "stale_prs": stale,
        "mode": mode,
    }


def format_fyi(scan: dict[str, Any]) -> str:
    """Single-line FYI for count 1–4 with no stale PRs."""
    return (
        f"[session-start] Dependabot PRs: {scan['count']} open "
        f"(oldest {scan['oldest_age']} day(s); review at convenience)."
    )


def format_loud(
    prs: list[dict[str, Any]], scan: dict[str, Any], now: datetime | None = None
) -> list[str]:
    """Multi-line LOUD attention block."""
    lines: list[str] = []
    lines.append("")
    lines.append("=" * 72)
    lines.append(
        f"[session-start] Dependabot PRs: {scan['count']} open "
        f"(oldest {scan['oldest_age']} day(s); {len(scan['stale_prs'])} stale ≥"
        f"{STALE_AGE_DAYS}d). Review per engine/operations/dependency-discipline.md."
    )
    # Sort all PRs oldest-first for the listing.
    aged = [(pr, age_days(pr["createdAt"], now)) for pr in prs]
    aged.sort(key=lambda pa: pa[1], reverse=True)
    for pr, days in aged:
        num = pr.get("number", "?")
        title = pr.get("title", "(no title)")
        mergeable = pr.get("mergeable", "UNKNOWN")
        stale_marker = " STALE" if days >= STALE_AGE_DAYS else ""
        action = next_action_hint(pr)
        lines.append(f"  #{num} [{days}d{stale_marker}] [{mergeable}]: {title}")
        lines.append(f"      → {action}")
    lines.append("=" * 72)
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan open Dependabot PRs for boot-time visibility per ADR 0080 (engine)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON of PR list + classification (test fixture support).",
    )
    parser.add_argument(
        "--repo",
        help="Pass-through to gh -R (defaults to current-repo auto-detect).",
    )
    parser.add_argument(
        "--simulate-age",
        type=int,
        default=None,
        help=(
            "TEST/DIAGNOSTIC: override every PR's age to N days. "
            "Production hook never sets."
        ),
    )
    args = parser.parse_args(argv)

    prs = fetch_open_prs(args.repo)
    if prs is None:
        print(
            "[scan-dependabot-prs] gh pr list failed; Dependabot PR "
            "visibility skipped this boot. Check `gh auth status` and network.",
            file=sys.stderr,
            flush=True,
        )
        return 0

    # --simulate-age overrides createdAt to (now - N days) so downstream
    # age_days computation produces N. Pure for tests.
    if args.simulate_age is not None:
        from datetime import timedelta

        # Emits gh's external wire format ("...Z"), not an engine-canonical
        # timestamp — must round-trip through age_days' fromisoformat parse
        # above. Allowlisted in validate.py's _TIMESTAMP_HELPER_BYPASS_ALLOWLIST
        # per ADR 0058 for the same reason as the age_days parse site.
        simulated_created = (
            (datetime.now(timezone.utc) - timedelta(days=args.simulate_age))
            .isoformat()
            .replace("+00:00", "Z")
        )
        for pr in prs:
            pr["createdAt"] = simulated_created

    scan = classify(prs)

    if args.json:
        json.dump(
            {
                "count": scan["count"],
                "oldest_age": scan["oldest_age"],
                "stale_prs_count": len(scan["stale_prs"]),
                "mode": scan["mode"],
                "prs": [
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "createdAt": pr.get("createdAt"),
                        "mergeable": pr.get("mergeable"),
                        "headRefName": pr.get("headRefName"),
                        "age_days": age_days(pr["createdAt"]),
                    }
                    for pr in prs
                ],
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 0

    if scan["mode"] == "quiet":
        return 0
    if scan["mode"] == "fyi":
        print(format_fyi(scan), flush=True)
        return 0
    for line in format_loud(prs, scan):
        print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
