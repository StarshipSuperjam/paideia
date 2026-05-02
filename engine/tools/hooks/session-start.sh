#!/bin/bash
#
# Paideia SessionStart hook — cadence trigger + persistent-warn surface.
#
# Per ADR 0043 (engine). Wired in .claude/settings.json as a SessionStart
# hook. Fires once at every session boot regardless of whether /start-engine
# or `Start Engine` is invoked.
#
# Two posture rules this mechanizes:
#
#   1. Health-check cadence trigger — per ADR 0022. The strict logic
#      `last_claimed mod cadence == 0` was off-by-one against ROADMAP/ADR 0022
#      prose intent (the trigger should fire AT the cadence-numbered session,
#      not the session AFTER). The corrected logic is `next_id mod cadence == 0`
#      — fires when the slot ABOUT TO BE CLAIMED matches the cadence number.
#
#   2. Persistent-warn surface — per ADR 0042. Reads the last 5
#      engine/session/archive/S-NNNN.json files, parses the
#      `outcome_summary_soft_warns` structured field, and surfaces any
#      soft-warn category that fired in 3-or-more of those 5 archives.
#      The calibration window per soft-warn-lifecycle.md is in effect until
#      5 structured-field archives accumulate (≈ S-0033); during the window,
#      the surface emits "calibration window in effect" instead.
#
# Behavior: emits informational stdout/stderr; never blocks. Always exits 0.
#
# Failure modes:
#   - jq absent → log fail, exit 0 (no surface; reminder defers).
#   - register_state.json missing or malformed → log fail, exit 0.
#   - archive directory absent or empty → emit "no archive data yet", exit 0.
#
# Log path: .claude/logs/session-start.log (gitignored under .claude/*).

# Resolve repo root.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
    REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." 2>/dev/null && pwd)"
fi

LOG_DIR="$REPO_ROOT/.claude/logs"
LOG_FILE="$LOG_DIR/session-start.log"
mkdir -p "$LOG_DIR" 2>/dev/null

REGISTER_FILE="$REPO_ROOT/engine/session/register_state.json"
ARCHIVE_DIR="$REPO_ROOT/engine/session/archive"

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log_fail() {
    echo "$TIMESTAMP FAIL reason=$1" >>"$LOG_FILE" 2>/dev/null
}

log_ok() {
    echo "$TIMESTAMP OK $1" >>"$LOG_FILE" 2>/dev/null
}

# jq is required for JSON parsing.
if ! command -v jq >/dev/null 2>&1; then
    log_fail "jq-not-installed"
    exit 0
fi

# ---------------------------------------------------------------------------
# Cadence trigger surface
# ---------------------------------------------------------------------------

if [ ! -f "$REGISTER_FILE" ]; then
    log_fail "register-missing"
    exit 0
fi

NEXT_ID="$(jq -r '.next_id // empty' "$REGISTER_FILE" 2>/dev/null)"
LAST_CLAIMED="$(jq -r '.last_claimed // empty' "$REGISTER_FILE" 2>/dev/null)"

if [ -z "$NEXT_ID" ]; then
    log_fail "next-id-empty"
    exit 0
fi

# Strip any leading zeros for arithmetic (bash interprets 0NNN as octal).
# 10# prefix forces base-10 interpretation.
NEXT_INT=$((10#$NEXT_ID))

# Cadence read from register_state.json's optional `health_check_cadence`
# field, defaulting to 30 per the project default.
CADENCE="$(jq -r '.health_check_cadence // 30' "$REGISTER_FILE" 2>/dev/null)"
if ! echo "$CADENCE" | grep -qE '^[0-9]+$' || [ "$CADENCE" -lt 1 ]; then
    CADENCE=30
fi

CADENCE_REMAINDER=$((NEXT_INT % CADENCE))

echo "[session-start] register: next_id=$NEXT_ID last_claimed=$LAST_CLAIMED cadence=$CADENCE"

if [ "$CADENCE_REMAINDER" -eq 0 ]; then
    {
        echo "[session-start] Cadence: trigger fires for the session about to be claimed (S-$NEXT_ID)."
        echo "  Per ADR 0022 + engine/operations/health-check.md, propose a project health check."
        echo "  Run engine/tools/health_check.py --session S-$NEXT_ID to produce the audit report,"
        echo "  or defer with the reason captured in outcome_summary."
    } >&2
else
    echo "[session-start] Cadence: no trigger this session (next_id $NEXT_ID mod $CADENCE = $CADENCE_REMAINDER)."
fi

# ---------------------------------------------------------------------------
# Persistent-warn surface (last 5 archives, 3-of-5 threshold)
# ---------------------------------------------------------------------------

if [ ! -d "$ARCHIVE_DIR" ]; then
    echo "[session-start] Persistent warns: archive directory absent."
    log_ok "cadence=$CADENCE_REMAINDER persistent-warns=no-archive"
    exit 0
fi

# Collect the last 5 archive files by sorted name (S-NNNN.json sorts
# lexicographically and chronologically because the counter is zero-padded).
RECENT_ARCHIVES=()
while IFS= read -r f; do
    RECENT_ARCHIVES+=("$f")
done < <(find "$ARCHIVE_DIR" -maxdepth 1 -name 'S-[0-9][0-9][0-9][0-9].json' -type f 2>/dev/null \
    | sort \
    | tail -5)

ARCHIVE_COUNT=${#RECENT_ARCHIVES[@]}

if [ "$ARCHIVE_COUNT" -eq 0 ]; then
    echo "[session-start] Persistent warns: no archive files yet."
    log_ok "cadence=$CADENCE_REMAINDER persistent-warns=no-archives"
    exit 0
fi

# Count how many of the recent archives carry the structured field.
STRUCTURED_COUNT=0
for archive in "${RECENT_ARCHIVES[@]}"; do
    if jq -e '.outcome_summary_soft_warns // empty | type == "object"' "$archive" >/dev/null 2>&1; then
        STRUCTURED_COUNT=$((STRUCTURED_COUNT + 1))
    fi
done

# Calibration window per soft-warn-lifecycle.md: defer surface until 5
# structured-field archives accumulate.
if [ "$STRUCTURED_COUNT" -lt 5 ]; then
    echo "[session-start] Persistent warns: calibration window in effect ($STRUCTURED_COUNT/5 structured archives; surface defers until 5)."
    log_ok "cadence=$CADENCE_REMAINDER persistent-warns=calibration-window structured=$STRUCTURED_COUNT"
    exit 0
fi

# Aggregate per-category counts across the 5 most-recent archives. A category
# "fires in" an archive iff its count is >0.
declare -A CATEGORY_FIRINGS
for archive in "${RECENT_ARCHIVES[@]}"; do
    while IFS=$'\t' read -r cat count; do
        if [ -n "$cat" ] && [ -n "$count" ] && [ "$count" -gt 0 ] 2>/dev/null; then
            CATEGORY_FIRINGS[$cat]=$((${CATEGORY_FIRINGS[$cat]:-0} + 1))
        fi
    done < <(jq -r '.outcome_summary_soft_warns // {} | to_entries[] | "\(.key)\t\(.value)"' "$archive" 2>/dev/null)
done

PERSISTENT_FOUND=0
for cat in "${!CATEGORY_FIRINGS[@]}"; do
    firings=${CATEGORY_FIRINGS[$cat]}
    if [ "$firings" -ge 3 ]; then
        if [ "$PERSISTENT_FOUND" -eq 0 ]; then
            echo "[session-start] Persistent warns:" >&2
            PERSISTENT_FOUND=1
        fi
        echo "  - $cat fired in $firings of the last 5 sessions." >&2
    fi
done

if [ "$PERSISTENT_FOUND" -eq 1 ]; then
    {
        echo "  Per engine/operations/soft-warn-lifecycle.md, consider addressing inline,"
        echo "  promoting to hard-fail, or accepting via tools-validate-interpretation.md."
    } >&2
else
    echo "[session-start] Persistent warns: none above the 3-of-5 threshold."
fi

log_ok "cadence=$CADENCE_REMAINDER persistent-warns=$PERSISTENT_FOUND"
exit 0
