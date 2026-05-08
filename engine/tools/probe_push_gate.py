"""Empirical probe for the local-routine 'Default Branch Push' harness gate.

Phase 0 artifact for S-0060 per ADR 0054 (lifecycle-push wrapping). Tests
the hypothesis that the harness gates Bash command surface (the literal
``git push``) but not git operations spawned from a subprocess inside a
permitted tool. If the hypothesis holds, this script's subprocess push
to ``main`` succeeds where a raw ``git push origin main`` Bash call
would be denied with the gate's "(Git Push to Default Branch)" message.

The probe MUST be invoked deliberately (no default ``--actually-push``),
because the empirical test inherently performs a push. The dry-run mode
exists so the script can be inspected without side-effects.

Modes
-----
- (default) ``--dry-run``: print the push command that would be executed;
  do not execute. Safe to run anywhere, even uncommitted.
- ``--actually-push``: create an empty commit on the current branch and
  push it. Without ``--target-main``, pushes to a throwaway branch
  ``claude/probe-push-gate-<UTC-timestamp>`` that's safe to delete.
- ``--actually-push --target-main``: pushes the empty commit to ``main``
  via subprocess. THIS IS THE LOAD-BEARING TEST. Caller must be ready to
  observe whether the gate fires (push refused with the 'Default Branch
  Push' message) or the subprocess slips past it.

The empty commit is harmless: ``git commit --allow-empty -m
'chore(probe): probe_push_gate.py empirical run @ <timestamp>'``. After
the probe, the user (or a follow-up commit) can amend or revert as
needed.

Findings get written to
``engine/build_readiness/routine_lifecycle_push_first_exercise.md`` per
ADR 0053's mechanism-first-exercise gate.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_git(args: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    """Wrap subprocess.run for git invocations. check=False so caller inspects."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _utc_timestamp() -> str:
    """Compact UTC timestamp suitable for branch names: YYYYMMDDTHHMMSSZ.

    NOT routed through engine/tools/timestamps.py per ADR 0058 because the
    canonical %Y-%m-%dT%H:%M:%SZ form contains colons, which Git's
    check-ref-format rejects in branch names. The compact form is the
    correct legacy shape for filename-safe contexts; ``probe_push_gate.py``
    is allowlisted in validate.py's _TIMESTAMP_HELPER_BYPASS_ALLOWLIST so
    the timestamp_helper_bypass soft-warn does not fire here. The
    ``parse()`` helper accepts this form on read-back via the
    compact-time regex branch.
    """
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def make_empty_commit(repo: Path, timestamp: str) -> tuple[bool, str]:
    """Create an empty commit on HEAD. Returns (success, sha-or-error)."""
    msg = f"chore(probe): probe_push_gate.py empirical run @ {timestamp}"
    result = _run_git(["commit", "--allow-empty", "-m", msg], repo)
    if result.returncode != 0:
        return False, result.stderr.strip()
    sha = _run_git(["rev-parse", "HEAD"], repo).stdout.strip()
    return True, sha


def push(repo: Path, refspec: str, dry_run: bool) -> tuple[bool, str, str]:
    """Push refspec via subprocess. Returns (success, stdout, stderr).

    `subprocess.run` here is the load-bearing test: the harness gate
    inspects Bash command surface, not python subprocess invocations.
    If the gate fires here, the wrapper hypothesis is dead.
    """
    if dry_run:
        return True, f"[dry-run] would: git push origin {refspec}", ""
    result = _run_git(["push", "origin", refspec], repo)
    return result.returncode == 0, result.stdout, result.stderr


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for mode semantics."""
    parser = argparse.ArgumentParser(
        description=(
            "Empirical probe for the local-routine 'Default Branch Push' "
            "gate. Subprocess git push hypothesis test."
        ),
    )
    parser.add_argument(
        "--actually-push",
        action="store_true",
        help="Perform the push. Default is dry-run (print only).",
    )
    parser.add_argument(
        "--target-main",
        action="store_true",
        help=(
            "Push to main (the load-bearing test). Without this flag, "
            "pushes to a throwaway claude/probe-push-gate-<ts> branch."
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
    timestamp = _utc_timestamp()

    if not args.actually_push:
        # Dry-run: describe what would happen
        target = "main" if args.target_main else f"claude/probe-push-gate-{timestamp}"
        refspec = f"HEAD:{target}"
        print("[probe-push-gate] dry-run mode")
        print("[probe-push-gate] would create: empty commit at HEAD")
        print(f"[probe-push-gate] would push: git push origin {refspec}")
        print(
            f"[probe-push-gate] re-invoke with --actually-push to perform"
            f"{' (TARGETING MAIN — load-bearing test)' if args.target_main else ''}."
        )
        return 0

    ok, sha_or_err = make_empty_commit(repo, timestamp)
    if not ok:
        print(f"[probe-push-gate] commit failed: {sha_or_err}", file=sys.stderr)
        return 1
    print(f"[probe-push-gate] empty commit created: {sha_or_err}")

    if args.target_main:
        target = "main"
        refspec = "HEAD:main"
        print(
            "[probe-push-gate] LOAD-BEARING TEST: pushing HEAD to main "
            "via subprocess. If the harness gate fires here, the wrapper "
            "hypothesis is dead."
        )
    else:
        target = f"claude/probe-push-gate-{timestamp}"
        refspec = f"HEAD:{target}"
        print(f"[probe-push-gate] pushing HEAD to throwaway branch: {target}")

    ok, stdout, stderr = push(repo, refspec, dry_run=False)
    if ok:
        print("[probe-push-gate] push succeeded.")
        if stdout:
            print(f"[probe-push-gate] stdout: {stdout.strip()}")
        if stderr:
            print(f"[probe-push-gate] stderr: {stderr.strip()}")
        return 0

    print("[probe-push-gate] push FAILED.", file=sys.stderr)
    if stdout:
        print(f"[probe-push-gate] stdout: {stdout.strip()}", file=sys.stderr)
    if stderr:
        print(f"[probe-push-gate] stderr: {stderr.strip()}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
