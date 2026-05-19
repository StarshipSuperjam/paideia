"""Hard-fail commits where the worktree's .claude/settings.json desyncs from main's.

When a Claude Code session running in a git worktree edits
``.claude/settings.json``, the harness's redirection rule depends on
which path the harness reads from. Pre-S-0048 this was always assumed
to be main's copy (Issue #5), so the original implementation hard-coded
the cp direction as ``main → worktree``. But Issue #154 (filed mid-S-0209)
surfaced the inverse case: the harness wrote to the *worktree's* copy,
making the worktree canonical and main stale. The original tool's
unconditional ``cp main → worktree`` guidance would silently destroy the
worktree's canonical content.

This refactor (per ADR 0100 Item 2) makes the tool **direction-aware**:

1. Compare SHA-256 content hashes. If equal, exit 0 (no divergence).
2. If different, mtime is the discriminator:
   - **worktree mtime > main mtime + tolerance** → worktree is canonical.
     The fix is to STAGE the worktree's copy so the commit ships it.
     (No cp needed; the harness already wrote canonical content to the
     worktree.)
   - **main mtime > worktree mtime + tolerance** → main is canonical
     (the original case). The fix is to ``cp main's copy → worktree``
     and stage.
   - **|mtime diff| ≤ tolerance** (1 second) → bidirectional concurrent
     edit; the tool cannot autonomously decide. **Halt-and-confirm**:
     emit both file paths + a hint to diff them manually, exit 1 so the
     commit blocks and the user adjudicates.
3. If the worktree's copy is staged for this commit, exit 0 regardless
   of direction (the user has already done the right thing).

Exit codes:

- ``0`` — synced, or not in a worktree, or the divergence is staged
- ``1`` — divergent + worktree copy not staged (hard-fail); guidance
  emitted to stderr
- ``2`` — tool error (e.g., ``git rev-parse`` failed unexpectedly,
  or hash/mtime read failed)

Per Issue #5 (S-0048) for the original tool; Issue #154 (S-0209/S-0210)
for the direction-fix.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

SETTINGS_PATH = ".claude/settings.json"

# Tolerance band (seconds) for declaring two mtimes "essentially
# concurrent." Anything within this window cannot be reliably
# discriminated — halts and asks the user to adjudicate.
CONCURRENT_TOLERANCE_SECONDS = 1.0


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


def _sha256(path: Path) -> str | None:
    """Return SHA-256 hex digest of ``path``, or None if unreadable/missing."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _mtime(path: Path) -> float | None:
    """Return mtime in seconds since epoch, or None if unreadable/missing."""
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def compare(main_settings: Path, worktree_settings: Path) -> str:
    """Diagnose the divergence direction.

    Returns one of:
      - ``"in_sync"`` — hashes match (or both missing)
      - ``"worktree_canonical"`` — worktree mtime is newer beyond tolerance
      - ``"main_canonical"`` — main mtime is newer beyond tolerance
      - ``"concurrent"`` — mtimes within tolerance; cannot discriminate
      - ``"missing_main"`` — main file absent, worktree present
      - ``"missing_worktree"`` — worktree file absent, main present
    """
    main_hash = _sha256(main_settings)
    worktree_hash = _sha256(worktree_settings)

    if main_hash is None and worktree_hash is None:
        return "in_sync"
    if main_hash is None:
        return "missing_main"
    if worktree_hash is None:
        return "missing_worktree"
    if main_hash == worktree_hash:
        return "in_sync"

    main_mtime = _mtime(main_settings)
    worktree_mtime = _mtime(worktree_settings)
    if main_mtime is None or worktree_mtime is None:
        # Hash mismatch confirmed but mtime unreadable — treat as
        # concurrent so the user adjudicates rather than guessing.
        return "concurrent"

    diff = worktree_mtime - main_mtime
    if abs(diff) <= CONCURRENT_TOLERANCE_SECONDS:
        return "concurrent"
    if diff > 0:
        return "worktree_canonical"
    return "main_canonical"


def main(argv: list[str] | None = None) -> int:
    detected = detect_worktree()
    if detected is None:
        return 0

    worktree_root, main_root = detected
    worktree_settings = worktree_root / SETTINGS_PATH
    main_settings = main_root / SETTINGS_PATH

    direction = compare(main_settings, worktree_settings)

    if direction == "in_sync":
        return 0

    # If the worktree's copy is staged, the user has already done the
    # right thing (regardless of direction) — the commit will ship the
    # current worktree content, which after FF to main becomes main's
    # canonical content.
    if is_staged(SETTINGS_PATH):
        return 0

    if direction == "worktree_canonical":
        print(
            "[check_settings_sync] worktree settings.json is NEWER than main's\n\n"
            "The harness wrote canonical content to the worktree's copy; main's\n"
            "copy is stale. Stage the worktree's copy so the commit ships the\n"
            "intended content:\n\n"
            f"  worktree (canonical): {worktree_settings}\n"
            f"  main (stale):         {main_settings}\n\n"
            "Run from the worktree root:\n\n"
            "  git add .claude/settings.json\n\n"
            "Then retry the commit. After the commit lands and main FFs,\n"
            "the main repo's working tree picks up the new content.\n\n"
            "See engine/operations/routine-mode-operations.md 'Editing\n"
            "settings.json from a worktree' for the full procedure.",
            file=sys.stderr,
        )
        return 1

    if direction == "main_canonical":
        print(
            "[check_settings_sync] worktree settings.json desync detected\n\n"
            "The Claude Code harness wrote to the main repo's .claude/settings.json,\n"
            "but git tracks the worktree's local copy. Right now main's copy is\n"
            "newer (the harness wrote there); the worktree's copy is stale AND\n"
            "is not staged for this commit, which means the close commit would\n"
            "silently ship without the settings.json change.\n\n"
            f"  main (canonical): {main_settings}\n"
            f"  worktree (stale): {worktree_settings}\n\n"
            "To resolve, run from the worktree root:\n\n"
            f"  cp '{main_settings}' .claude/settings.json\n"
            "  git add .claude/settings.json\n\n"
            "Then retry the commit. See engine/operations/routine-mode-operations.md\n"
            "'Editing settings.json from a worktree' for the full procedure.",
            file=sys.stderr,
        )
        return 1

    if direction == "concurrent":
        print(
            "[check_settings_sync] settings.json bidirectional edit detected\n\n"
            "Both main's and worktree's copies of .claude/settings.json have\n"
            f"been modified within {CONCURRENT_TOLERANCE_SECONDS}s of each other; the tool cannot\n"
            "autonomously decide which is canonical. Human adjudication needed.\n\n"
            f"  main:     {main_settings}\n"
            f"  worktree: {worktree_settings}\n\n"
            "Inspect both files and pick the canonical one:\n\n"
            f"  diff '{main_settings}' '{worktree_settings}'\n\n"
            "If main is canonical:\n"
            f"  cp '{main_settings}' .claude/settings.json && git add .claude/settings.json\n\n"
            "If worktree is canonical:\n"
            "  git add .claude/settings.json\n\n"
            "Either way, stage the chosen content and retry the commit.",
            file=sys.stderr,
        )
        return 1

    if direction == "missing_main":
        print(
            "[check_settings_sync] main repo's .claude/settings.json is missing\n\n"
            f"  expected at: {main_settings}\n"
            f"  worktree:    {worktree_settings}\n\n"
            "This is unusual — main's copy should always exist for an active\n"
            "Claude Code project. Investigate before forcing a sync.",
            file=sys.stderr,
        )
        return 1

    if direction == "missing_worktree":
        print(
            "[check_settings_sync] worktree's .claude/settings.json is missing\n\n"
            f"  main:                {main_settings}\n"
            f"  worktree (missing):  {worktree_settings}\n\n"
            "Copy main's copy into the worktree to restore:\n\n"
            f"  cp '{main_settings}' .claude/settings.json\n"
            "  git add .claude/settings.json",
            file=sys.stderr,
        )
        return 1

    # Defensive — unreachable under the current compare() return set.
    print(
        f"[check_settings_sync] unrecognized direction signal: {direction!r}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
