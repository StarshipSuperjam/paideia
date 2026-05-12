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

# Capture the caller's enclosing worktree (whatever ``git rev-parse
# --show-toplevel`` resolves from INITIAL_PWD); skip that path during sweep.
# The caller is presumably mid-session there. Without this, a build session
# whose branch has been merged into main via the eager-claim lifecycle push
# (per ADR 0076) would have its own worktree swept out from under it because
# the merged-into-main + clean-tree + claude/* preconditions all pass.
# Added at S-0142 per user pushback "what is the point in HAVING to clean
# this up at all?" — the bulk sweep should be safe to run unattended without
# removing the caller's working tree.
CALLER_WT=$(git rev-parse --path-format=absolute --show-toplevel 2>/dev/null || echo "")

# Resolve the main repo (the parent of .git/) rather than the caller's
# linked-worktree path. ``--git-common-dir`` gives the shared .git directory;
# its parent is the main repo regardless of which worktree we were invoked
# from.
COMMON_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
REPO_ROOT=$(cd "$COMMON_DIR/.." 2>/dev/null && pwd -P)
cd "$REPO_ROOT"

DRY_RUN=true
if [ "$1" = "--apply" ]; then
    DRY_RUN=false
fi

REMOVED=0
SKIPPED=0

# Iterate worktrees (skip the current/main one).
#
# Process substitution (`< <(...)`) instead of pipe-to-while so the loop body
# runs in the parent shell, not a subshell — REMOVED/SKIPPED counters
# survive the loop. The pipe form silently zeroed both counters at end-of-
# loop (the per-iteration increments lived in the subshell that the pipe
# spawned), surfaced at S-0041 catch-up worktree sweep where the final
# "[sweep] removed N, skipped K" line read "removed 0, skipped 0" despite
# 37 actual removals. Fixed inline at S-0041 per the audit's "Default to
# fix-in-context" discipline.
while IFS= read -r WT_PATH; do
    if [ ! -d "$WT_PATH" ]; then
        echo "[sweep] worktree path missing: $WT_PATH (skipping)" >&2
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip the caller's enclosing worktree (in-flight session).
    if [ -n "$CALLER_WT" ]; then
        WT_PATH_REAL=$(cd "$WT_PATH" 2>/dev/null && pwd -P || echo "$WT_PATH")
        CALLER_WT_REAL=$(cd "$CALLER_WT" 2>/dev/null && pwd -P || echo "$CALLER_WT")
        if [ "$WT_PATH_REAL" = "$CALLER_WT_REAL" ]; then
            echo "[sweep] skip $WT_PATH (caller's current worktree; in-flight session)"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
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
done < <(git worktree list --porcelain | awk '/^worktree / {print $2}' | tail -n +2)

if [ "$DRY_RUN" = true ]; then
    echo "[sweep] dry run complete. Re-run with --apply to actually remove."
else
    echo "[sweep] removed $REMOVED, skipped $SKIPPED"
fi
