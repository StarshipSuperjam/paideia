"""Sync a harness-redirected .claude/settings.json edit into the worktree.

Companion to ``engine/tools/check_settings_sync.py`` for Issue #107.

Why this exists
---------------
When a Claude Code session running in a git worktree edits
``.claude/settings.json`` via the harness Write/Edit tools, the edit
lands on the PARENT repo's tracked copy (the harness reads settings
from the parent path). The worktree's tracked copy stays stale, so
the close commit silently ships without the deliverable looking
complete. ``check_settings_sync.py`` already hard-fails the commit
when this state is detected at pre-commit time, with a stderr hint
pointing at the manual ``cp <parent>/.claude/settings.json
.claude/settings.json && git add .claude/settings.json`` flow.

This tool mechanizes that remediation: one command that
(1) resolves the worktree + parent, (2) copies the parent's copy
into the worktree, and (3) stages the worktree's copy for the next
commit. After invocation, the pre-commit hook's
``check_settings_sync`` check passes.

Behavior
--------
- Resolves the worktree + parent via the same logic as
  ``check_settings_sync.detect_worktree()``. When running from the
  parent repo (not a linked worktree), exits 0 with a no-op message —
  the tool is a convenience for the worktree → parent sync flow; from
  the parent the harness writes the only tracked copy directly.
- When running from a worktree:
  - If the worktree's copy already matches the parent's copy, exits 0
    no-op (nothing to sync).
  - Otherwise, copies the parent's bytes into the worktree's copy and
    runs ``git -C <worktree> add .claude/settings.json``.
- Always emits the post-push reminder: parent_ff()'s auto-recovery
  (per Issue #107 / ADR 0054 amendment) handles identical-content
  overwrite refusals automatically; manual ``git -C <parent> checkout
  .claude/settings.json`` + ``git -C <parent> merge --ff-only
  origin/main`` is the residual fallback when content diverges.

Exit codes
----------
- ``0`` — synced + staged, OR no-op (not in a worktree, OR already
  in sync). The reminder line is always emitted to stderr so the
  invoker sees it regardless of whether a sync was needed.
- ``2`` — subprocess error (git add failed, or path resolution
  failed unexpectedly).

CLI
---
- ``update_settings.py`` — zero-arg invocation. Reads CWD to resolve.

Per Issue #107 (S-0150). Companion to
``engine/tools/check_settings_sync.py``.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_settings_sync  # noqa: E402

SETTINGS_PATH = check_settings_sync.SETTINGS_PATH

_POST_PUSH_REMINDER = (
    "[update_settings] reminder: after push, the parent's "
    f"{SETTINGS_PATH} working-tree copy may surface as a parent-FF "
    "refusal in build_lifecycle_push.py / routine_lifecycle_push.py. "
    "parent_ff() auto-recovers when the working-tree copy matches "
    "origin/main byte-identically (per ADR 0054 amendment landed at "
    "S-0150). Manual fallback if content diverges:\n"
    "  git -C <parent> diff HEAD origin/main -- .claude/settings.json\n"
    "  git -C <parent> checkout .claude/settings.json\n"
    "  git -C <parent> merge --ff-only origin/main"
)


def _print_reminder() -> None:
    print(_POST_PUSH_REMINDER, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Sync the parent's .claude/settings.json into the worktree + stage.

    See module docstring for the full behavior contract.
    """
    detected = check_settings_sync.detect_worktree()
    if detected is None:
        # Running from the parent repo (or git rev-parse failed). The harness
        # writes the only tracked copy directly; nothing to sync.
        print(
            "[update_settings] not in a linked worktree — no sync needed.\n"
            f"The harness writes {SETTINGS_PATH} directly when invoked from "
            "the parent repo. Commit normally from here.",
            file=sys.stderr,
        )
        _print_reminder()
        return 0

    worktree_root, main_root = detected
    worktree_settings = worktree_root / SETTINGS_PATH
    main_settings = main_root / SETTINGS_PATH

    if not check_settings_sync.files_differ(main_settings, worktree_settings):
        print(
            f"[update_settings] {SETTINGS_PATH} already in sync — nothing to do.",
            file=sys.stderr,
        )
        _print_reminder()
        return 0

    try:
        worktree_settings.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(main_settings, worktree_settings)
    except OSError as exc:
        print(
            f"[update_settings] failed to copy {main_settings} -> "
            f"{worktree_settings}: {exc}",
            file=sys.stderr,
        )
        return 2

    add_result = subprocess.run(
        ["git", "-C", str(worktree_root), "add", SETTINGS_PATH],
        capture_output=True,
        text=True,
        check=False,
    )
    if add_result.returncode != 0:
        err = add_result.stderr.strip() or add_result.stdout.strip() or "unknown error"
        print(
            f"[update_settings] git add failed: {err}",
            file=sys.stderr,
        )
        return 2

    print(
        f"[update_settings] synced and staged {SETTINGS_PATH} from "
        f"{main_root} into {worktree_root}.",
        file=sys.stderr,
    )
    _print_reminder()
    return 0


if __name__ == "__main__":
    sys.exit(main())
