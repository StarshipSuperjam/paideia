"""Hard-fail commits where the worktree's .claude/settings.json desyncs from main's.

When a Claude Code session running in a git worktree edits
``.claude/settings.json`` via the Write tool, the harness redirects the
write to the main repo's copy (where the harness reads from), not the
worktree's local copy (where git tracks for the worktree's branch).
Result: the worktree's tracked copy stays stale, ``git status`` from the
worktree sees no change, and the close commit silently ships without the
deliverable looking complete.

This tool runs in the pre-commit hook. It hard-fails the commit when:

- The current working tree is a git worktree (not the main repo itself).
- The main repo's ``.claude/settings.json`` differs from the worktree's
  tracked copy.
- The worktree's ``.claude/settings.json`` is NOT staged for the current
  commit (i.e., the user has not already ``cp``'d main's copy into the
  worktree's copy and staged it).

When all three conditions hold, the user gets a clear hint pointing at
the cp procedure documented in
``engine/operations/routine-mode-operations.md`` "Editing settings.json
from a worktree".

Exit codes:

- ``0`` — synced, or not in a worktree, or the divergence is staged
- ``1`` — divergent + worktree copy not staged (hard-fail)
- ``2`` — tool error (e.g., ``git rev-parse`` failed unexpectedly)

Per Issue #5 (S-0048).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SETTINGS_PATH = ".claude/settings.json"


def _run_git(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    """Run ``git <args>``; return (returncode, stripped stdout)."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def detect_worktree() -> tuple[Path, Path] | None:
    """Resolve worktree root and main repo root.

    Returns ``(worktree_root, main_repo_root)`` when running inside a
    git worktree (i.e., the worktree lives outside the main repo).
    Returns ``None`` when running from the main repo itself, or when
    ``git rev-parse`` fails (not a git repo).
    """
    rc, toplevel = _run_git(["rev-parse", "--show-toplevel"])
    if rc != 0 or not toplevel:
        return None
    worktree_root = Path(toplevel).resolve()

    rc, common_dir = _run_git(["rev-parse", "--git-common-dir"])
    if rc != 0 or not common_dir:
        return None
    common_dir_path = Path(common_dir)
    if not common_dir_path.is_absolute():
        common_dir_path = (worktree_root / common_dir_path).resolve()
    main_repo_root = common_dir_path.parent.resolve()

    if main_repo_root == worktree_root:
        return None
    return worktree_root, main_repo_root


def is_staged(path: str) -> bool:
    """Return True if ``path`` appears in the staged-for-commit name list."""
    rc, out = _run_git(["diff", "--cached", "--name-only", "--", path])
    return rc == 0 and bool(out)


def files_differ(a: Path, b: Path) -> bool:
    """Return True if file bytes differ, or either file is missing."""
    if not a.exists() or not b.exists():
        return True
    return a.read_bytes() != b.read_bytes()


def main(argv: list[str] | None = None) -> int:
    detected = detect_worktree()
    if detected is None:
        return 0

    worktree_root, main_root = detected
    worktree_settings = worktree_root / SETTINGS_PATH
    main_settings = main_root / SETTINGS_PATH

    if not files_differ(main_settings, worktree_settings):
        return 0

    if is_staged(SETTINGS_PATH):
        return 0

    print(
        "[check_settings_sync] worktree settings.json desync detected\n\n"
        "The Claude Code harness redirects worktree Writes to the main\n"
        "repo's .claude/settings.json, but git tracks the worktree's\n"
        "local copy. Right now those two files differ AND the worktree's\n"
        "copy is not staged for this commit, which means the close commit\n"
        "would silently ship without your settings.json change.\n\n"
        f"  main:     {main_settings}\n"
        f"  worktree: {worktree_settings}\n\n"
        "To resolve, run from the worktree root:\n\n"
        f"  cp '{main_settings}' .claude/settings.json\n"
        "  git add .claude/settings.json\n\n"
        "Then retry the commit. See engine/operations/routine-mode-operations.md\n"
        "'Editing settings.json from a worktree' for the full procedure.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
