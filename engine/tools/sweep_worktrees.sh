#!/bin/bash
#
# Paideia stale-worktree sweep utility.
#
# Removes claude/* worktrees whose branch is fully merged into main and whose
# working tree is clean. Run on demand OR at session boot (per ADR 0076
# Amendment v2; the session-start.sh hook invokes this script with --apply
# --quiet after the stale-worktree check so accumulated prior-session
# worktrees are collected at next-session boot, replacing the post-close
# self-sweep ADR 0076's first version performed).
#
# Conservative: skips worktrees with uncommitted changes, untracked files,
# branches not matching the claude/* pattern, or branches not yet merged.
# Skips the caller's enclosing worktree (in-flight session) unconditionally
# (S-0142 safety check; the caller is presumably mid-session there).
#
# Usage:
#   tools/sweep_worktrees.sh                 # dry run (default) — full preserve-report per skipped
#   tools/sweep_worktrees.sh --apply         # actually remove
#   tools/sweep_worktrees.sh --apply --quiet # apply, suppress per-preserved detail (boot use)

set -e

# Capture the caller's enclosing worktree (whatever ``git rev-parse
# --show-toplevel`` resolves from INITIAL_PWD); skip that path during sweep.
# Without this, a build session whose branch has been merged into main via
# the eager-claim lifecycle push (per ADR 0076) would have its own worktree
# swept out from under it because the merged-into-main + clean-tree +
# claude/* preconditions all pass. Added at S-0142.
CALLER_WT=$(git rev-parse --path-format=absolute --show-toplevel 2>/dev/null || echo "")

# Resolve the main repo (the parent of .git/) rather than the caller's
# linked-worktree path.
COMMON_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
REPO_ROOT=$(cd "$COMMON_DIR/.." 2>/dev/null && pwd -P)
cd "$REPO_ROOT"

DRY_RUN=true
QUIET=false
for arg in "$@"; do
    case "$arg" in
        --apply) DRY_RUN=false ;;
        --quiet) QUIET=true ;;
    esac
done

REMOVED=0
SKIPPED=0

# emit_preserve_report — multi-line structured report per preserved worktree.
# Args: $1=path  $2=branch  $3=reason  $4=is_caller (yes|no)
# Reads dirty-files, merged state, ahead/behind, last-commit inline via git.
# Quiet mode (boot use) emits only the path + reason line.
emit_preserve_report() {
    local wt_path="$1"
    local branch="$2"
    local reason="$3"
    local is_caller="$4"

    if [ "$QUIET" = true ]; then
        echo "[sweep] PRESERVED $wt_path: $reason"
        return
    fi

    # Resolve branch state. Best-effort — any failure falls back to "?".
    local merged="?"
    local ahead="?"
    local behind="?"
    local last_commit="<unknown>"
    local dirty_files="(clean)"

    if [ -n "$branch" ] && [ "$branch" != "<unknown>" ]; then
        if git -C "$REPO_ROOT" merge-base --is-ancestor "$branch" main 2>/dev/null; then
            merged="yes"
        else
            merged="no"
        fi
        ahead=$(git -C "$REPO_ROOT" rev-list --count "main..$branch" 2>/dev/null || echo "?")
        behind=$(git -C "$REPO_ROOT" rev-list --count "$branch..main" 2>/dev/null || echo "?")
    fi

    if [ -d "$wt_path" ]; then
        last_commit=$(git -C "$wt_path" log -1 --format='%s | %ci' HEAD 2>/dev/null || echo "<unknown>")
        local status
        status=$(git -C "$wt_path" status --porcelain 2>/dev/null)
        if [ -n "$status" ]; then
            # First 5 files, newline-joined → comma-joined; tail count if more.
            local total
            total=$(printf '%s\n' "$status" | wc -l | tr -d ' ')
            local first5
            first5=$(printf '%s\n' "$status" | head -5 | awk '{ s = substr($0, 4); printf "%s%s", (NR>1?", ":""), s }')
            if [ "$total" -gt 5 ]; then
                dirty_files="$first5 (+$((total - 5)) more)"
            else
                dirty_files="$first5"
            fi
        fi
    fi

    echo "[sweep] PRESERVED $wt_path"
    echo "  reason: $reason"
    echo "  branch: $branch (merged=$merged, ahead=$ahead, behind=$behind)"
    echo "  dirty files: $dirty_files"
    echo "  last commit: $last_commit"

    if [ "$is_caller" = "yes" ]; then
        echo "  guidance: caller's own worktree preserved for follow-up; the"
        echo "           next session's boot-time bulk sweep collects it once"
        echo "           it is no longer the caller (ADR 0076 Amendment v2)."
    elif [ "$dirty_files" != "(clean)" ]; then
        echo "  guidance: review files; if no work to preserve, run"
        echo "           \`git -C $wt_path checkout . && git worktree remove $wt_path\`"
    elif [ "$merged" = "yes" ] && [[ "$branch" == claude/* ]]; then
        echo "  guidance: clean + merged; safe to remove via"
        echo "           \`git worktree remove $wt_path\` (would normally be swept"
        echo "           automatically — investigate why it was retained)."
    elif [ "$merged" = "no" ]; then
        echo "  guidance: branch carries $ahead unmerged commit(s); investigate"
        echo "           before discarding (merge or rebase as appropriate)."
    else
        echo "  guidance: branch \`$branch\` does not match claude/* convention;"
        echo "           manual review required."
    fi
}

# Process substitution (`< <(...)`) instead of pipe-to-while so the loop body
# runs in the parent shell, not a subshell — REMOVED/SKIPPED counters
# survive the loop.
while IFS= read -r WT_PATH; do
    if [ ! -d "$WT_PATH" ]; then
        echo "[sweep] worktree path missing: $WT_PATH (skipping)" >&2
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip the caller's enclosing worktree (in-flight session).
    IS_CALLER="no"
    if [ -n "$CALLER_WT" ]; then
        WT_PATH_REAL=$(cd "$WT_PATH" 2>/dev/null && pwd -P || echo "$WT_PATH")
        CALLER_WT_REAL=$(cd "$CALLER_WT" 2>/dev/null && pwd -P || echo "$CALLER_WT")
        if [ "$WT_PATH_REAL" = "$CALLER_WT_REAL" ]; then
            BRANCH_CALLER=$(git -C "$WT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "<unknown>")
            emit_preserve_report "$WT_PATH" "$BRANCH_CALLER" "caller's current worktree (in-flight session)" "yes"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
    fi

    BRANCH=$(git -C "$WT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    # Only sweep claude/* branches
    if [[ "$BRANCH" != claude/* ]]; then
        emit_preserve_report "$WT_PATH" "${BRANCH:-<unknown>}" "branch not claude/*" "no"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip if uncommitted changes or untracked files
    STATUS=$(git -C "$WT_PATH" status --porcelain 2>/dev/null)
    if [ -n "$STATUS" ]; then
        emit_preserve_report "$WT_PATH" "$BRANCH" "working tree dirty" "no"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip if branch not merged into main
    if ! git merge-base --is-ancestor "$BRANCH" main 2>/dev/null; then
        emit_preserve_report "$WT_PATH" "$BRANCH" "branch not merged into main" "no"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    if [ "$DRY_RUN" = true ]; then
        echo "[sweep] would remove $WT_PATH (branch $BRANCH)"
    else
        if [ "$QUIET" = false ]; then
            echo "[sweep] removing $WT_PATH (branch $BRANCH)"
        fi
        git worktree remove "$WT_PATH"
        # Delete the branch separately (per macOS/Windows handle-release timing)
        git branch -d "$BRANCH" 2>/dev/null || true
        REMOVED=$((REMOVED + 1))
    fi
done < <(git worktree list --porcelain | awk '/^worktree / {print $2}' | tail -n +2)

if [ "$DRY_RUN" = true ]; then
    echo "[sweep] dry run complete ($SKIPPED preserved). Re-run with --apply to actually remove."
else
    echo "[sweep] removed $REMOVED, preserved $SKIPPED"
fi
