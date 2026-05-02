#!/bin/bash
#
# Paideia stale-worktree sweep utility.
#
# Removes claude/* worktrees whose branch is fully merged into main and whose
# working tree is clean. Run on demand (typically after a build session
# closes successfully and main has been fast-forwarded).
#
# Conservative: skips worktrees with uncommitted changes, untracked files,
# branches not matching the claude/* pattern, or branches not yet merged.
#
# Usage:
#   tools/sweep_worktrees.sh           # dry run (default)
#   tools/sweep_worktrees.sh --apply   # actually remove

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

DRY_RUN=true
if [ "$1" = "--apply" ]; then
    DRY_RUN=false
fi

REMOVED=0
SKIPPED=0

# Iterate worktrees (skip the current/main one)
git worktree list --porcelain | awk '/^worktree / {print $2}' | tail -n +2 | while read -r WT_PATH; do
    if [ ! -d "$WT_PATH" ]; then
        echo "[sweep] worktree path missing: $WT_PATH (skipping)" >&2
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    BRANCH=$(git -C "$WT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    # Only sweep claude/* branches
    if [[ "$BRANCH" != claude/* ]]; then
        echo "[sweep] skip $WT_PATH (branch $BRANCH not claude/*)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip if uncommitted changes or untracked files
    STATUS=$(git -C "$WT_PATH" status --porcelain 2>/dev/null)
    if [ -n "$STATUS" ]; then
        echo "[sweep] skip $WT_PATH (working tree dirty on $BRANCH)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip if branch not merged into main
    if ! git merge-base --is-ancestor "$BRANCH" main 2>/dev/null; then
        echo "[sweep] skip $WT_PATH (branch $BRANCH not merged into main)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    if [ "$DRY_RUN" = true ]; then
        echo "[sweep] would remove $WT_PATH (branch $BRANCH)"
    else
        echo "[sweep] removing $WT_PATH (branch $BRANCH)"
        git worktree remove "$WT_PATH"
        # Delete the branch separately (per macOS/Windows handle-release timing)
        git branch -d "$BRANCH" 2>/dev/null || true
        REMOVED=$((REMOVED + 1))
    fi
done

if [ "$DRY_RUN" = true ]; then
    echo "[sweep] dry run complete. Re-run with --apply to actually remove."
else
    echo "[sweep] removed $REMOVED, skipped $SKIPPED"
fi
