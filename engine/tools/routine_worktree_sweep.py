"""Per-worktree post-close sweep — sibling to the bulk ``sweep_worktrees.sh``.

Layer 1 contract per ADR 0054 amendment (S-0072 / Issue #16 follow-on) plus
ADR 0076 Amendment v2 (S-0143 / skip-caller defense + enriched preserve-report).

Purpose
-------
Remove a previously-closed session's worktree and its ``claude/<name>``
feature branch when the close push has already propagated to ``origin/main``.

**The tool defaults to refusing self-sweep.** When the resolved target
worktree path equals the caller's current working directory, the tool emits
a structured preserve-report and exits 2. This protects the in-flight
session's working folder from being silently removed mid-session — the
defect S-0142 surfaced at its own close, where the routine post-close
sweep wiping the closing worktree erased the user's follow-up surface.

Sweep of the caller's own worktree is opt-in via ``--allow-caller-self``;
this is reserved for test fixtures (pytest creates the worktree, chdir's
into it, then invokes the tool in-process) and manual recovery scenarios.
Production close ceremonies should never set this flag — the boot-time
bulk sweep in ``engine/tools/hooks/session-start.sh`` cleans accumulated
prior-session worktrees at the next session's start.

Sequence
--------
1. Resolve target worktree path (CLI ``--worktree`` or ``os.getcwd()``).
2. Resolve parent repo path via ``git rev-parse --git-common-dir``.
3. Refuse if running directly in the parent (not a linked worktree).
4. Refuse if target is the caller's own CWD AND ``--allow-caller-self``
   is NOT set. Emit the structured preserve-report on refusal.
5. Pre-flight checks (mirrored from ``sweep_worktrees.sh``):
   - branch matches ``claude/*``;
   - working tree clean (no uncommitted changes / untracked files);
   - branch fully merged into ``main``.
   Failures emit the structured preserve-report.
6. Chdir to parent so subsequent operations don't carry the about-to-be-
   removed worktree as CWD.
7. ``git -C <parent> worktree remove <worktree-path>``.
8. ``git -C <parent> branch -d <worktree-branch>``.

Exit codes
----------
- ``0`` — sweep succeeded (worktree directory removed, branch deleted).
- ``2`` — refused with explicit reason (caller's-own-worktree default,
  working tree dirty, branch not ``claude/*``, branch not merged, running
  in parent). Caller logs and continues — the close has already succeeded;
  sweep is best-effort.
- ``5`` — generic git error during remove/branch-delete.

CLI
---
- ``routine_worktree_sweep.py`` — refuses (caller's own worktree default).
- ``routine_worktree_sweep.py --worktree PATH`` — sweep a specific worktree
  (resolved path must differ from caller's CWD, OR ``--allow-caller-self``
  must be set).
- ``--allow-caller-self`` — opt-in to legacy self-sweep behavior for tests
  and manual recovery.
- ``--dry-run`` — run pre-flight checks, emit preserve-report on refusal
  OR the would-be-removed line on accept; do not remove anything.

Out of scope
------------
- Bulk cleanup of stale sibling worktrees. ``sweep_worktrees.sh --apply``
  remains the right tool for that (invoked at session boot per the
  ADR 0076 Amendment v2 boot-time-sweep wiring).
- Hard-fail propagation. Sweep is best-effort by design.
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

    Returns the directory containing the shared ``.git``. Returns the same
    path as ``repo`` when ``repo`` IS the parent (not a linked worktree).
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


def is_caller_self(target: Path) -> bool:
    """True when the target worktree equals the caller's current CWD.

    Resolves both paths to avoid symlink-mismatch false negatives. Returns
    False on OSError (e.g., CWD does not exist).
    """
    try:
        return Path(os.getcwd()).resolve() == target.resolve()
    except OSError:
        return False


def collect_preserve_info(
    parent: Path, worktree: Path, branch: str | None
) -> dict[str, str]:
    """Gather structured info for a preserved worktree.

    Returns a dict with keys: path, branch, merged, ahead_main, behind_main,
    dirty_files, last_commit. Used by both the per-worktree refusal path
    and the bulk utility's --dry-run preserve-report.
    """
    info: dict[str, str] = {"path": str(worktree)}

    if branch is None:
        result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], worktree)
        branch = result.stdout.strip() if result.returncode == 0 else ""
    info["branch"] = branch or "<unknown>"

    if branch:
        info["merged"] = "yes" if branch_merged_into_main(parent, branch) else "no"
        ahead = _run_git(["rev-list", "--count", f"main..{branch}"], parent)
        info["ahead_main"] = ahead.stdout.strip() if ahead.returncode == 0 else "?"
        behind = _run_git(["rev-list", "--count", f"{branch}..main"], parent)
        info["behind_main"] = behind.stdout.strip() if behind.returncode == 0 else "?"
    else:
        info["merged"] = "?"
        info["ahead_main"] = "?"
        info["behind_main"] = "?"

    status = _run_git(["status", "--porcelain"], worktree)
    if status.returncode == 0 and status.stdout.strip():
        files = [line[3:] for line in status.stdout.strip().splitlines()[:5]]
        total = len(status.stdout.strip().splitlines())
        suffix = f" (+{total - len(files)} more)" if total > len(files) else ""
        info["dirty_files"] = ", ".join(files) + suffix
    else:
        info["dirty_files"] = "(clean)"

    last = _run_git(["log", "-1", "--format=%s | %ci", "HEAD"], worktree)
    info["last_commit"] = last.stdout.strip() if last.returncode == 0 else "<unknown>"

    return info


def format_preserve_report(
    info: dict[str, str], reason: str, *, is_caller_self_refusal: bool = False
) -> str:
    """Format collected info as a multi-line stderr block with guidance.

    The guidance line differs by refusal class: caller-self gets the
    "preserve for follow-up" note; dirty trees get the
    `git checkout . && git worktree remove` recipe; merged-but-not-claude
    or unmerged branches get an investigate-first note.
    """
    lines = [
        f"[routine-worktree-sweep] PRESERVED {info['path']}",
        f"  reason: {reason}",
        (
            f"  branch: {info['branch']} (merged={info['merged']}, "
            f"ahead={info['ahead_main']}, behind={info['behind_main']})"
        ),
        f"  dirty files: {info['dirty_files']}",
        f"  last commit: {info['last_commit']}",
    ]

    if is_caller_self_refusal:
        lines.append(
            "  guidance: caller's own worktree preserved for follow-up; "
            "the next session's boot-time bulk sweep will collect it once "
            "it is no longer the caller (per session-start.sh + ADR 0076 "
            "Amendment v2)."
        )
    elif info["dirty_files"] != "(clean)":
        lines.append(
            f"  guidance: review files; if no work to preserve, "
            f"`git -C {info['path']} checkout . && "
            f"git worktree remove {info['path']}`"
        )
    elif info["merged"] == "yes" and info["branch"].startswith("claude/"):
        lines.append(
            f"  guidance: clean + merged; safe to remove via "
            f"`git worktree remove {info['path']}` (would normally be "
            "swept automatically — investigate why it was retained)."
        )
    elif info["merged"] == "no":
        lines.append(
            f"  guidance: branch carries {info['ahead_main']} unmerged "
            "commit(s); investigate before discarding (merge or rebase as "
            "appropriate, then remove)."
        )
    else:
        lines.append(
            f"  guidance: branch {info['branch']!r} does not match "
            "claude/* convention; manual review required."
        )

    return "\n".join(lines)


def preflight(
    worktree: Path, parent: Path, *, allow_caller_self: bool = False
) -> tuple[bool, str, str | None]:
    """Run pre-flight checks before sweep. Returns (ok, reason, branch_name).

    Refuses self-sweep by default (per ADR 0076 Amendment v2). The
    ``allow_caller_self`` opt-in is reserved for tests and manual recovery;
    production close ceremonies must not set it.
    """
    if parent == worktree:
        return False, "running in parent repo, not a linked worktree", None

    if not allow_caller_self and is_caller_self(worktree):
        return (
            False,
            "caller's own worktree; preserve for follow-up "
            "(boot-time sweep will collect at next session start)",
            None,
        )

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
        return True, (
            f"worktree removed; branch {branch} delete failed "
            f"(orphan branch, will need manual cleanup): {msg.splitlines()[0]}"
        )

    return True, f"swept worktree and deleted branch {branch}"


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for exit-code semantics."""
    parser = argparse.ArgumentParser(
        description=(
            "Per-worktree post-close sweep. Refuses self-sweep by default "
            "(caller's own worktree preserved for follow-up); the boot-time "
            "bulk sweep in session-start.sh collects accumulated prior-"
            "session worktrees at next session boot."
        ),
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=None,
        help="Worktree path to sweep (default: current working directory).",
    )
    parser.add_argument(
        "--allow-caller-self",
        action="store_true",
        help=(
            "Permit sweeping the caller's own worktree. Default refuses "
            "to preserve user follow-up access (per ADR 0076 Amendment "
            "v2). Reserved for test fixtures and manual recovery."
        ),
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

    ok, reason, branch = preflight(
        worktree, parent, allow_caller_self=args.allow_caller_self
    )
    if not ok:
        is_self_refusal = "caller's own worktree" in reason
        is_in_parent = reason.startswith("running in parent repo")

        if is_in_parent:
            print(
                f"[routine-worktree-sweep] REFUSED: {reason}",
                file=sys.stderr,
            )
        else:
            info = collect_preserve_info(parent, worktree, branch)
            print(
                format_preserve_report(
                    info, reason, is_caller_self_refusal=is_self_refusal
                ),
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
