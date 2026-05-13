"""Mechanical boot-freshness gate for routine-mode sessions.

Layer 1 contract per ADR 0082 (Issue #15 corrected diagnosis).

Purpose
-------
Routine sessions read shared-state files (``register_state.json``,
``current.json``, ``auto_target.json``) at boot to make claim-and-route
decisions. When the worktree's local HEAD is behind ``origin/main``,
those files reflect pre-update state and the AI can re-claim a slot
that's already been taken upstream, write a duplicate eager-claim,
and produce an orphan branch + worktree pair on push rejection.

Issue #15 case study: the S-0054 winner-session closed cleanly,
pushed three commits to ``origin/main``, and exited. A subsequent
routine fired in a worktree whose local HEAD was at the precursor
of the winner's eager-claim. The routine read stale
``register_state.json`` showing ``next_id=0054``, claimed S-0054
again, and got rejected at FF-merge time. The S-0051 fix to Issue
#10 added an *informational* staleness warning at the harness side
(:file:`engine/tools/hooks/session-start.sh`); the warning is not
mechanically acted on by the routine boot procedure.

This tool is the mechanical gate. The routine boot procedure
(``.claude/skills/routine-mode-lifecycle/SKILL.md`` step 0a) runs it
*before* reading any shared-state file. Fast-forward is bounded —
``git merge --ff-only`` moves HEAD forward without merging or
discarding anything — and is safe to mechanize. Diverged HEAD
(impossible to ff) refuses the boot; that's a real anomaly that
needs human adjudication and routine sessions cannot resolve it.

Sequence
--------
1. ``git fetch --no-tags --quiet origin main`` — best-effort. A
   network failure emits a stderr note and exits 0 (the routine then
   proceeds against possibly-stale state and the existing
   informational warning at session-start.sh surfaces).
2. Compare HEAD to ``origin/main`` via
   ``git merge-base --is-ancestor origin/main HEAD``:
   - HEAD is at-or-ahead-of origin/main → no-op, exit 0.
   - HEAD is strictly behind origin/main (FF possible) →
     ``git merge --ff-only origin/main``, log to stderr the count of
     commits fast-forwarded, exit 0.
   - HEAD is diverged from origin/main → exit 2 with a clear stderr
     message. Routine boot must NOT proceed.

Exit codes
----------
- ``0`` — clean (already-fresh, fetch-failed-with-note, or
  successfully-fast-forwarded).
- ``2`` — diverged HEAD; cannot ff. Boot refused.

CLI
---
- ``routine_boot_freshness.py`` — defaults to the script's repo root.
- ``routine_boot_freshness.py --repo-root PATH`` — override for tests.

Out of scope
------------
- Concurrency control. ADR 0082 covers serialization
  (``routine_lock.py``) and loser recovery
  (``routine_eager_claim_recovery.py``) as separate layers.
- Interactive ``/start-engine`` boot. The informational-warning
  model at session-start.sh remains for interactive sessions where
  the AI is in the loop and can read+act.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_git(
    args: list[str], repo: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Wrap subprocess.run for git invocations with consistent flags."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def fetch_main(repo: Path) -> bool:
    """Best-effort `git fetch --no-tags --quiet origin main`. Returns True on success."""
    try:
        _run_git(["fetch", "--no-tags", "--quiet", "origin", "main"], repo, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        # git not installed — extremely unlikely in the routine-mode environment
        return False


def is_ancestor(ancestor: str, descendant: str, repo: Path) -> bool | None:
    """Return True if `ancestor` is an ancestor of `descendant`. None on git error."""
    try:
        result = _run_git(
            ["merge-base", "--is-ancestor", ancestor, descendant], repo, check=False
        )
    except FileNotFoundError:
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def count_commits_behind(repo: Path) -> int:
    """Count commits HEAD is behind origin/main. 0 if already ahead/at."""
    try:
        result = _run_git(
            ["rev-list", "--count", "HEAD..origin/main"], repo, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def fast_forward_main(repo: Path) -> bool:
    """`git merge --ff-only origin/main`. Returns True on success."""
    try:
        _run_git(["merge", "--ff-only", "origin/main"], repo, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for exit-code semantics."""
    parser = argparse.ArgumentParser(
        description=(
            "Mechanical boot-freshness gate for routine-mode sessions. "
            "Fast-forwards the worktree to origin/main before any shared-state "
            "read; refuses to proceed if HEAD is diverged."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root for git invocations (default: script's repo).",
    )
    args = parser.parse_args(argv)
    repo: Path = args.repo_root

    if not fetch_main(repo):
        print(
            "[routine-boot-freshness] git fetch failed — proceeding against "
            "possibly-stale state. Existing session-start.sh staleness warning "
            "(if any) will surface separately.",
            file=sys.stderr,
        )
        return 0

    head_ahead_of_origin = is_ancestor("origin/main", "HEAD", repo)
    origin_ahead_of_head = is_ancestor("HEAD", "origin/main", repo)

    if head_ahead_of_origin is None or origin_ahead_of_head is None:
        # git error somewhere; treat as best-effort and continue
        print(
            "[routine-boot-freshness] git ancestry check failed — proceeding "
            "against possibly-stale state.",
            file=sys.stderr,
        )
        return 0

    if head_ahead_of_origin and origin_ahead_of_head:
        # Same commit — clean.
        return 0

    if head_ahead_of_origin and not origin_ahead_of_head:
        # HEAD is strictly ahead. Fine — local commits not yet pushed.
        return 0

    if origin_ahead_of_head and not head_ahead_of_origin:
        # HEAD is strictly behind origin/main — fast-forward possible.
        n = count_commits_behind(repo)
        if not fast_forward_main(repo):
            print(
                "[routine-boot-freshness] fast-forward failed despite "
                "ancestor relationship; refusing boot.",
                file=sys.stderr,
            )
            return 2
        print(
            f"[routine-boot-freshness] fast-forwarded {n} commit(s) "
            "to origin/main before reading shared-state.",
            file=sys.stderr,
        )
        return 0

    # Neither is ancestor of the other — diverged.
    print(
        "[routine-boot-freshness] HARD-FAIL: HEAD has diverged from "
        "origin/main (each side has commits the other does not).",
        file=sys.stderr,
    )
    print(
        "Routine boot refused. This is a real anomaly that needs human "
        "adjudication — a routine session cannot resolve it. Inspect with:\n"
        "    git log HEAD --not origin/main      # local-only commits\n"
        "    git log origin/main --not HEAD      # upstream-only commits",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
