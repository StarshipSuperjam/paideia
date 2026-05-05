"""Routine-mode post-close worktree sweep.

Layer 1 contract per ADR 0054 amendment (S-0072 / Issue #16 follow-on).

Purpose
-------
At routine close, after the close push and parent-side FF have succeeded,
remove the current session's worktree and its ``claude/<name>`` feature
branch. Routine sessions create a fresh worktree per fire (the Worktree
checkbox in Claude Code Routines) and the close push lifecycle did not
sweep them. By S-0072 the project had accumulated 14+ active worktrees
plus orphan branches (Issue #16). This tool closes that gap so a clean
routine close leaves no detritus.

Companion to ``routine_lifecycle_push.py`` (post-push parent FF) — both
extend the routine close lifecycle to match the interactive close's
"leave-no-mess" posture.

Sequence
--------
1. Resolve current worktree path (CLI ``--worktree`` or ``os.getcwd()``).
2. Resolve parent repo path via ``git rev-parse --git-common-dir`` (the
   shared ``.git`` directory's parent). Same helper as
   ``routine_lifecycle_push.py``.
3. Refuse if running directly in the parent (not a linked worktree).
4. Chdir to parent so subsequent operations don't carry the about-to-be-
   removed worktree as CWD (forks would fail).
5. Pre-flight checks:
   - working tree must be clean (no uncommitted changes / untracked files);
   - branch must match ``claude/*`` (the routine convention);
   - branch must be fully merged into ``main`` (otherwise sweep would
     orphan the work; close push not yet propagated).
6. ``git -C <parent> worktree remove <worktree-path>``.
7. ``git -C <parent> branch -d <worktree-branch>``.

The pre-flight checks mirror ``engine/tools/sweep_worktrees.sh`` exactly
(claude/* branch, working tree clean, branch merged) — this tool is the
single-worktree, called-at-routine-close form of that bulk utility.

Exit codes
----------
- ``0`` — sweep succeeded (worktree directory removed, branch deleted).
- ``2`` — refused with explicit reason (working tree dirty, branch not
  ``claude/*``, branch not merged, running in parent). Caller logs and
  continues — the close has already succeeded; sweep is best-effort.
- ``5`` — generic git error during remove/branch-delete. Caller logs and
  continues; the worktree may need manual cleanup later.

CLI
---
- ``routine_worktree_sweep.py`` — sweeps the current worktree (uses
  ``os.getcwd()``).
- ``routine_worktree_sweep.py --worktree PATH`` — sweep a specific
  worktree (test fixtures, manual recovery).
- ``--dry-run`` — run pre-flight checks, report what would happen, do
  not remove anything.

Out of scope
------------
- Bulk cleanup of stale sibling worktrees. ``sweep_worktrees.sh --apply``
  remains the right tool for that; this sweep is single-worktree only.
- Interactive close. Interactive sessions don't always use worktrees and
  the closer-loops-back affordance is well-served by manual cleanup.
- Hard-fail propagation. Sweep is best-effort by design — the close has
  already landed by the time we run.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_git(
    args: list[str], repo: Path, check: bool = False
) -> subprocess.CompletedProcess[str]:
    """Wrap subprocess.run for git invocations."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def get_parent_repo_path(repo: Path) -> Path | None:
    """Resolve the parent repo path for a linked worktree.

    Same shape as ``routine_lifecycle_push.get_parent_repo_path``: returns
    the directory containing the shared ``.git``. Returns the same path
    as ``repo`` when ``repo`` IS the parent (not a linked worktree).
    Returns ``None`` on git error or unexpected layout.
    """
    result = _run_git(["rev-parse", "--git-common-dir"], repo)
    if result.returncode != 0:
        return None
    common_dir = Path(result.stdout.strip())
    if not common_dir.is_absolute():
        common_dir = (repo / common_dir).resolve()
    else:
        common_dir = common_dir.resolve()
    if common_dir.name != ".git":
        return None
    return common_dir.parent


def get_current_branch(repo: Path) -> str | None:
    """Return repo's current branch name. None on git error or detached HEAD."""
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo)
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    if not branch or branch == "HEAD":
        return None
    return branch


def working_tree_clean(repo: Path) -> bool:
    """True if working tree has no uncommitted changes or untracked files."""
    result = _run_git(["status", "--porcelain"], repo)
    if result.returncode != 0:
        return False
    return result.stdout.strip() == ""


def branch_merged_into_main(parent: Path, branch: str) -> bool:
    """True if `branch`'s tip is an ancestor of `main` in the parent repo."""
    result = _run_git(
        ["merge-base", "--is-ancestor", branch, "main"], parent, check=False
    )
    return result.returncode == 0


def preflight(worktree: Path, parent: Path) -> tuple[bool, str, str | None]:
    """Run pre-flight checks before sweep. Returns (ok, reason, branch_name).

    The third element is the branch name resolved from the worktree, or
    None if a check failed before resolution.
    """
    if parent == worktree:
        return False, "running in parent repo, not a linked worktree", None

    branch = get_current_branch(worktree)
    if branch is None:
        return False, "could not determine worktree branch (detached HEAD?)", None

    if not branch.startswith("claude/"):
        return False, f"branch {branch!r} is not claude/*; refusing sweep", branch

    if not working_tree_clean(worktree):
        return False, f"working tree dirty on {branch}; refusing sweep", branch

    if not branch_merged_into_main(parent, branch):
        return (
            False,
            f"branch {branch} not merged into main; refusing sweep "
            "(close push may not have propagated)",
            branch,
        )

    return True, f"preflight ok on {branch}", branch


def sweep(parent: Path, worktree: Path, branch: str) -> tuple[bool, str]:
    """Run the actual sweep. Returns (ok, reason)."""
    remove_result = _run_git(["worktree", "remove", str(worktree)], parent, check=False)
    if remove_result.returncode != 0:
        msg = (
            remove_result.stderr.strip()
            or remove_result.stdout.strip()
            or "unknown error"
        )
        return False, f"worktree remove failed: {msg.splitlines()[0]}"

    branch_result = _run_git(["branch", "-d", branch], parent, check=False)
    if branch_result.returncode != 0:
        msg = (
            branch_result.stderr.strip()
            or branch_result.stdout.strip()
            or "unknown error"
        )
        # Branch delete failed but worktree was removed — partial success;
        # surface the reason but exit 0 because the worktree is gone (the
        # primary deliverable). The branch becomes an orphan that
        # sweep_worktrees.sh or manual cleanup can address.
        return True, (
            f"worktree removed; branch {branch} delete failed "
            f"(orphan branch, will need manual cleanup): {msg.splitlines()[0]}"
        )

    return True, f"swept worktree and deleted branch {branch}"


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for exit-code semantics."""
    parser = argparse.ArgumentParser(
        description=(
            "Routine-mode post-close worktree sweep. Removes the current "
            "session's worktree and its claude/<name> feature branch after "
            "close has propagated to origin/main."
        ),
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=None,
        help="Worktree path to sweep (default: current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pre-flight checks and report what would happen; do not remove.",
    )
    args = parser.parse_args(argv)

    worktree: Path = (args.worktree or Path(os.getcwd())).resolve()

    parent = get_parent_repo_path(worktree)
    if parent is None:
        print(
            "[routine-worktree-sweep] could not resolve parent repo path; refusing.",
            file=sys.stderr,
        )
        return 5

    ok, reason, branch = preflight(worktree, parent)
    if not ok:
        print(
            f"[routine-worktree-sweep] REFUSED: {reason}",
            file=sys.stderr,
        )
        return 2

    print(f"[routine-worktree-sweep] {reason}", file=sys.stderr)

    if args.dry_run:
        print(
            f"[routine-worktree-sweep] dry-run: would remove worktree "
            f"{worktree} and branch {branch}.",
            file=sys.stderr,
        )
        return 0

    # Chdir to parent BEFORE running the sweep — once the worktree directory
    # is unlinked, child-process forks from this process inheriting the
    # about-to-be-removed CWD would fail on macOS.
    try:
        os.chdir(parent)
    except OSError as exc:
        print(
            f"[routine-worktree-sweep] chdir to parent failed: {exc}",
            file=sys.stderr,
        )
        return 5

    assert branch is not None  # preflight guarantees on ok=True
    sweep_ok, sweep_reason = sweep(parent, worktree, branch)
    if sweep_ok:
        print(f"[routine-worktree-sweep] {sweep_reason}", file=sys.stderr)
        return 0

    print(
        f"[routine-worktree-sweep] sweep failed: {sweep_reason}",
        file=sys.stderr,
    )
    return 5


if __name__ == "__main__":
    sys.exit(main())
