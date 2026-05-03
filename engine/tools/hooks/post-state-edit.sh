#!/bin/bash
#
# Paideia PostToolUse hook for engine/STATE.md edits — required-fields verifier.
#
# Per ADR 0043 (engine). Wired in .claude/settings.json as a PostToolUse hook
# matched against Edit/Write tool calls touching engine/STATE.md.
#
# Posture this mechanizes: STATE.md is the single source of truth that every
# session reads first. An edit that empties or placeholders the "Last build
# session" or "Next session work item" rows degrades the next session's boot
# silently. This hook surfaces such regressions at edit time.
#
# Behavior: reads the post-edit file; verifies that the `## Current` table's
# "Last build session" row is non-empty and not a placeholder, and that the
# `## Next session work item` block is non-empty. Emits stderr reminders for
# any violation. Always exits 0; reminders are informational, not blocking.
#
# Failure modes:
#   - jq absent → not used here; pure shell.
#   - tool payload malformed → log fail, exit 0.
#   - STATE.md absent post-edit (deletion) → log fail, exit 0.
#
# Log path: .claude/logs/post-state-edit.log (gitignored under .claude/*).

# Resolve repo root. Scrub GIT_* env first per ADR 0045 — defense-in-depth
# against a leaked GIT_DIR from any future Skill or sub-agent context that
# could redirect this hook's git rev-parse to a foreign repo. Source-only
# helper at engine/tools/scrub_env.sh; gracefully degrades if absent.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
SCRUB_HELPER="$SCRIPT_DIR/../scrub_env.sh"
if [ -f "$SCRUB_HELPER" ]; then
    # shellcheck source=../scrub_env.sh
    source "$SCRUB_HELPER"
    scrub_git_env
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." 2>/dev/null && pwd)"
fi

LOG_DIR="$REPO_ROOT/.claude/logs"
LOG_FILE="$LOG_DIR/post-state-edit.log"
mkdir -p "$LOG_DIR" 2>/dev/null

STATE_FILE="$REPO_ROOT/engine/STATE.md"

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log_fail() {
    echo "$TIMESTAMP FAIL reason=$1" >>"$LOG_FILE" 2>/dev/null
}

log_ok() {
    echo "$TIMESTAMP OK $1" >>"$LOG_FILE" 2>/dev/null
}

# Read the harness's tool-call payload from stdin (best-effort — only used
# to confirm the edit targeted engine/STATE.md, which the matcher already
# enforces).
PAYLOAD="$(cat 2>/dev/null || echo '')"

if [ ! -f "$STATE_FILE" ]; then
    log_fail "state-md-absent"
    exit 0
fi

# ---------------------------------------------------------------------------
# Check 1: "Last build session" row
# ---------------------------------------------------------------------------

# Match the row in the `## Current` table. The expected shape is:
#   | **Last build session** | S-NNNN (date) — summary |
LAST_SESSION_LINE="$(grep -m1 -E '^\| \*\*Last build session\*\* \|' "$STATE_FILE" 2>/dev/null)"

ISSUES=0

if [ -z "$LAST_SESSION_LINE" ]; then
    {
        echo "[post-state-edit] Reminder: STATE.md has no 'Last build session' row in the ## Current table."
        echo "  Expected shape: | **Last build session** | S-NNNN (YYYY-MM-DD) — summary |"
    } >&2
    ISSUES=$((ISSUES + 1))
else
    # Extract the value cell (between the second and third pipe).
    LAST_SESSION_VALUE="$(echo "$LAST_SESSION_LINE" | awk -F'\\|' '{print $3}' | sed 's/^ *//;s/ *$//')"
    # Empty, or contains a placeholder substring like <fill>, TBD, or just S-NNNN literal.
    if [ -z "$LAST_SESSION_VALUE" ] \
        || echo "$LAST_SESSION_VALUE" | grep -qE '<.*>|^TBD|^\(see |^S-NNNN|placeholder' ; then
        {
            echo "[post-state-edit] Reminder: STATE.md 'Last build session' row appears empty or placeholder."
            echo "  Current value: '$LAST_SESSION_VALUE'"
            echo "  Boot procedure depends on a populated value."
        } >&2
        ISSUES=$((ISSUES + 1))
    fi
fi

# ---------------------------------------------------------------------------
# Check 2: "Next session work item" section
# ---------------------------------------------------------------------------

# Locate the section header and read until the next `## ` header.
NEXT_SECTION="$(awk '
    /^## Next session work item/ { in_section = 1; next }
    /^## / && in_section { exit }
    in_section { print }
' "$STATE_FILE" 2>/dev/null)"

# Strip leading/trailing whitespace and check for substantive content
# (more than 50 non-whitespace characters).
NEXT_TRIMMED="$(echo "$NEXT_SECTION" | tr -d '[:space:]')"
NEXT_LEN=${#NEXT_TRIMMED}

if [ "$NEXT_LEN" -lt 50 ]; then
    {
        echo "[post-state-edit] Reminder: STATE.md '## Next session work item' section appears empty or stub."
        echo "  Section content length (whitespace stripped): $NEXT_LEN chars; expect >= 50."
        echo "  The next session reads this cold; it should be sufficient to bootstrap."
    } >&2
    ISSUES=$((ISSUES + 1))
fi

# Check for placeholder markers in the next-session block.
if echo "$NEXT_SECTION" | grep -qE '<TBD>|<placeholder>|<fill ' ; then
    {
        echo "[post-state-edit] Reminder: STATE.md '## Next session work item' contains placeholder tokens."
        echo "  Search for <TBD>, <placeholder>, or <fill ...> and replace before close."
    } >&2
    ISSUES=$((ISSUES + 1))
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

if [ "$ISSUES" -eq 0 ]; then
    log_ok "all-checks-pass"
else
    log_ok "reminders-emitted issues=$ISSUES"
fi

# Always exit 0 — non-blocking by design.
exit 0
