"""Mechanically-verified loser recovery for the routine eager-claim race.

Layer 1 contract per ADR 0082 (Issue #15 residual defense).

Purpose
-------
The routine boot's eager-claim push can be rejected if a peer
session pushed first. The freshness gate
(:mod:`routine_boot_freshness`) eliminates the staleness vector
that produced the S-0054 failure; the lockfile
(:mod:`routine_lock`) eliminates the in-process concurrent-fire
case. This tool covers the residual: if both layers somehow slip
(e.g. the lockfile machinery itself fails, or two cadence fires
race past the lock check before either acquires), the loser
auto-cleans rather than leaving an orphan branch + worktree pair.

Mechanism
---------
On push rejection, the routine boot procedure
(``.claude/skills/routine-mode-lifecycle/SKILL.md`` step 8 push-
rejection branch) runs this tool. The tool:

1. Verifies the rejection has the eager-claim-race shape:
   - HEAD has exactly one commit ahead of origin/main
   - That commit's subject matches the eager-claim convention:
     ``chore(session): eager-claim S-NNNN — ...``
   - origin/main HEAD also has an eager-claim commit for the
     same slot (the winner's claim that just landed).
   The shape verification is mechanical, not heuristic. If it
   fails, the tool exits 2 (refuse to recover ambiguous state).

2. On verified race: ``git reset --hard origin/main`` on the
   worktree branch. Bounded — moves HEAD to origin tip; nothing
   on the loser's branch is salvageable (the eager-claim is
   obsolete by definition).

3. Exit 0. The routine session then exits cleanly without re-
   claiming. The next cadence fire claims fresh.

Whitelisted as a narrow exception to the routine-mode destructive-
action posture (per CLAUDE.md). The bounded reset is verified
mechanically; outside the verified shape the destructive-action
refusal stands.

Exit codes
----------
- ``0`` — verified race detected and recovered (HEAD reset).
- ``2`` — ambiguous state; recovery refused. Routine session
  must escalate (write HANDOFF and exit).

CLI
---
- ``routine_eager_claim_recovery.py`` — defaults to the script's
  repo root.
- ``routine_eager_claim_recovery.py --repo-root PATH`` — override
  for tests.
- ``routine_eager_claim_recovery.py --dry-run`` — verify the race
  shape and report findings without performing the reset.

Out of scope
------------
- Multi-commit-ahead recovery. If the loser has more than one
  commit ahead of origin/main, the shape doesn't match an eager-
  claim race (substantive work was committed before the push) and
  the tool refuses. That's a manual cleanup case.
- Cross-worktree cleanup. If the orphan exists in a different
  worktree (the typical S-0054 case), this tool only handles the
  local recovery; the orphan branch on the remote and the orphan
  worktree directory are user-adjudicated cleanup.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EAGER_CLAIM_SUBJECT = re.compile(r"^chore\(session\): eager-claim (S-\d{4})\b")


def _run_git(
    args: list[str], repo: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Wrap subprocess.run for git invocations."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def get_local_ahead_subjects(repo: Path) -> list[str] | None:
    """Subjects of commits HEAD has that origin/main does not. None on git error."""
    try:
        result = _run_git(
            ["log", "--format=%s", "HEAD", "--not", "origin/main"], repo, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.splitlines()


def get_origin_main_subject(repo: Path) -> str | None:
    """Subject of origin/main HEAD. None on git error."""
    try:
        result = _run_git(
            ["log", "--format=%s", "-n", "1", "origin/main"], repo, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip()


def verify_race_shape(repo: Path) -> tuple[bool, str]:
    """Return (is_race, reason). reason is human-readable for stderr."""
    ahead_subjects = get_local_ahead_subjects(repo)
    if ahead_subjects is None:
        return False, "git log failed; cannot determine local-ahead commits"
    if len(ahead_subjects) == 0:
        return (
            False,
            "HEAD has no commits ahead of origin/main; not a race recovery case",
        )
    if len(ahead_subjects) > 1:
        return (
            False,
            f"HEAD has {len(ahead_subjects)} commits ahead of origin/main; "
            "expected exactly 1 (the eager-claim). Substantive work appears "
            "committed before push — manual review needed.",
        )

    local_subject = ahead_subjects[0]
    local_match = EAGER_CLAIM_SUBJECT.match(local_subject)
    if not local_match:
        return (
            False,
            f"local-ahead commit subject does not match eager-claim pattern: "
            f"{local_subject!r}",
        )
    local_slot = local_match.group(1)

    origin_subject = get_origin_main_subject(repo)
    if origin_subject is None:
        return False, "git log of origin/main failed"
    origin_match = EAGER_CLAIM_SUBJECT.match(origin_subject)
    if not origin_match:
        return (
            False,
            f"origin/main HEAD subject does not match eager-claim pattern: "
            f"{origin_subject!r}",
        )
    origin_slot = origin_match.group(1)

    if local_slot != origin_slot:
        return (
            False,
            f"local-ahead claim is for {local_slot} but origin/main HEAD is "
            f"for {origin_slot} — slots differ; not the symmetric race shape",
        )

    return True, f"verified race for slot {local_slot}; both sides claim same slot"


def perform_reset(repo: Path) -> bool:
    """`git reset --hard origin/main`. Returns True on success."""
    try:
        _run_git(["reset", "--hard", "origin/main"], repo, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for exit-code semantics."""
    parser = argparse.ArgumentParser(
        description=(
            "Mechanically-verified loser recovery for the routine eager-claim "
            "race. Per ADR 0082; whitelisted exception to the routine-mode "
            "destructive-action posture."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root for git invocations (default: script's repo).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify race shape and report; do not perform the reset.",
    )
    args = parser.parse_args(argv)
    repo: Path = args.repo_root

    is_race, reason = verify_race_shape(repo)
    if not is_race:
        print(
            f"[routine-eager-claim-recovery] HARD-FAIL: {reason}",
            file=sys.stderr,
        )
        print(
            "Refusing to perform reset on ambiguous state. Inspect manually "
            "and adjudicate.",
            file=sys.stderr,
        )
        return 2

    print(f"[routine-eager-claim-recovery] {reason}", file=sys.stderr)

    if args.dry_run:
        print(
            "[routine-eager-claim-recovery] dry-run: would `git reset "
            "--hard origin/main` on this worktree branch.",
            file=sys.stderr,
        )
        return 0

    if not perform_reset(repo):
        print(
            "[routine-eager-claim-recovery] HARD-FAIL: git reset failed",
            file=sys.stderr,
        )
        return 2

    print(
        "[routine-eager-claim-recovery] reset complete; worktree branch is "
        "now at origin/main. Routine session should exit cleanly without "
        "re-claiming.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
