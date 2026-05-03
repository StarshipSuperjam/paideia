#!/bin/bash
#
# Paideia SessionStart hook — cadence trigger + persistent-warn surface
# + shared-state health probe.
#
# Per ADR 0043 (engine; cadence + persistent-warn) and ADR 0045 (engine;
# shared-state health probes). Wired in .claude/settings.json as a
# SessionStart hook. Fires once at every session boot regardless of
# whether /start-engine or `Start Engine` is invoked.
#
# Three posture rules this mechanizes:
#
#   1. Health-check cadence trigger — per ADR 0022. Two prior bugs are
#      relevant context. First, the original logic `last_claimed mod cadence
#      == 0` fired the trigger one session AFTER the cadence-numbered slot
#      (off-by-one against ROADMAP/ADR 0022 prose), corrected at S-0031 to
#      `next_id mod cadence == 0`. Second, the corrected strict-modulo logic
#      silently slid the trigger forward by a full cadence whenever the
#      cadence-aligned slot was consumed by user-directed work — S-0040's
#      slot was taken by the deferred MemPalace wing-filter fix, leaving
#      the next firing at S-0050 (a 19-session gap, nearly 2x the configured
#      cadence). At S-0041, the logic was replaced with overdue-catchup:
#      `(next_id - last_audit_session) >= cadence`, where last_audit_session
#      is tracked in register_state.json and bumped by health_check.py after
#      writing the report. The hook surfaces "due" at the natural-cadence
#      slot and "overdue" at every slot beyond. If `last_audit_session` is
#      absent (legacy register_state.json, pre-S-0041), the hook falls back
#      to strict-modulo with a log line so the regression is visible.
#
#   2. Persistent-warn surface — per ADR 0042. Reads the last 5
#      engine/session/archive/S-NNNN.json files, parses the
#      `outcome_summary_soft_warns` structured field, and surfaces any
#      soft-warn category that fired in 3-or-more of those 5 archives.
#      The calibration window per soft-warn-lifecycle.md is in effect until
#      5 structured-field archives accumulate (≈ S-0033); during the window,
#      the surface emits "calibration window in effect" instead.
#
#   3. Shared-state health probe — per ADR 0045. Runs
#      `validate.py --health-probe-only` (sub-second on a 130 MB
#      palace) which executes probe_palace.py and probe_repo.py to
#      catch corruption (chromadb HNSW segment, parent .git/config
#      misset to bare) before the AI tries to query mempalace or
#      run parent-side git operations. Hard-broken findings emit a
#      LOUD stderr surface so the AI sees them at boot and addresses
#      them before substantive work; the hook still exits 0 so the
#      session can start (otherwise the AI cannot even diagnose).
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

# Source the env scrubber. Must precede any subprocess that hits git or
# git-aware tools so a leaked GIT_DIR / GIT_WORK_TREE from the parent
# context (the S-0033 vector) is dropped before we shell out.
SCRUB_HELPER="$REPO_ROOT/engine/tools/scrub_env.sh"
if [ -f "$SCRUB_HELPER" ]; then
    # shellcheck source=../scrub_env.sh
    source "$SCRUB_HELPER"
    scrub_git_env
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
# field, defaulting to 10 per the project default at S-0032 (was 30 pre-S-0033;
# tightened because the S-0032 MemPalace audit surfaced enough silent failures
# that 30-session intervals were too sparse — raise back when the project
# performs more consistently). Override via register_state.json.
CADENCE="$(jq -r '.health_check_cadence // 10' "$REGISTER_FILE" 2>/dev/null)"
if ! echo "$CADENCE" | grep -qE '^[0-9]+$' || [ "$CADENCE" -lt 1 ]; then
    CADENCE=10
fi

# Overdue-catchup logic (per ADR 0022 Consequences amendment at S-0041):
# the trigger fires when the slot about to be claimed is at-or-past one
# cadence beyond the most recent completed audit. last_audit_session is the
# canonical "audit happened" pointer; health_check.py bumps it after writing
# the report. A "due" surface fires when slots_since == cadence (the natural
# fire); an "overdue" surface fires when slots_since > cadence (the audit
# was due in a prior slot that got consumed by other work).
#
# Fallback: if last_audit_session is absent (legacy register_state.json
# pre-S-0041), the hook reverts to strict-modulo (next_id mod cadence == 0)
# with a log line so the regression to the silent-slide failure mode is
# visible. After S-0041 this fallback path should not trigger in practice.

LAST_AUDIT="$(jq -r '.last_audit_session // empty' "$REGISTER_FILE" 2>/dev/null)"

CADENCE_TRIGGER_REASON="strict-modulo-fallback"  # for log_ok telemetry
CADENCE_FIRES=0
SLOTS_SINCE=""

echo "[session-start] register: next_id=$NEXT_ID last_claimed=$LAST_CLAIMED cadence=$CADENCE last_audit=${LAST_AUDIT:-<absent>}"

if [ -n "$LAST_AUDIT" ] && echo "$LAST_AUDIT" | grep -qE '^S-[0-9]{4}$'; then
    LAST_AUDIT_INT=$((10#${LAST_AUDIT#S-}))
    SLOTS_SINCE=$((NEXT_INT - LAST_AUDIT_INT))
    CADENCE_TRIGGER_REASON="overdue-catchup"
    if [ "$SLOTS_SINCE" -ge "$CADENCE" ]; then
        CADENCE_FIRES=1
        if [ "$SLOTS_SINCE" -eq "$CADENCE" ]; then
            {
                echo "[session-start] Cadence: trigger fires for the cadence-aligned session about to be claimed (S-$NEXT_ID; $SLOTS_SINCE slots since last audit $LAST_AUDIT, cadence $CADENCE)."
                echo "  Per ADR 0022 + engine/operations/health-check.md, propose a project health check."
                echo "  Run engine/tools/health_check.py --session S-$NEXT_ID to produce the audit report,"
                echo "  or defer with the reason captured in outcome_summary."
            } >&2
        else
            OVERDUE=$((SLOTS_SINCE - CADENCE))
            {
                echo "[session-start] Cadence: trigger fires; audit is OVERDUE by $OVERDUE session(s) (S-$NEXT_ID is $SLOTS_SINCE slots since last audit $LAST_AUDIT; cadence $CADENCE)."
                echo "  The cadence-aligned slot was consumed by user-directed work without the audit firing."
                echo "  Per ADR 0022 + engine/operations/health-check.md, run the audit now or document explicit deferral."
                echo "  Run engine/tools/health_check.py --session S-$NEXT_ID to produce the catch-up report."
            } >&2
        fi
    else
        SLOTS_REMAINING=$((CADENCE - SLOTS_SINCE))
        echo "[session-start] Cadence: no trigger this session ($SLOTS_SINCE/$CADENCE slots since last audit $LAST_AUDIT; $SLOTS_REMAINING slot(s) until next due)."
    fi
else
    # Legacy fallback. Should not trigger in practice after S-0041.
    log_fail "last-audit-absent-falling-back-to-strict-modulo"
    CADENCE_REMAINDER=$((NEXT_INT % CADENCE))
    if [ "$CADENCE_REMAINDER" -eq 0 ]; then
        CADENCE_FIRES=1
        {
            echo "[session-start] Cadence: trigger fires (strict-modulo fallback; last_audit_session absent from register_state.json)."
            echo "  Per ADR 0022 + engine/operations/health-check.md, propose a project health check."
            echo "  Run engine/tools/health_check.py --session S-$NEXT_ID to produce the audit report."
            echo "  Restore last_audit_session in register_state.json to re-enable overdue-catchup logic."
        } >&2
    else
        echo "[session-start] Cadence: no trigger this session (strict-modulo fallback; next_id $NEXT_ID mod $CADENCE = $CADENCE_REMAINDER)."
    fi
fi

# ---------------------------------------------------------------------------
# Shared-state health probe (per ADR 0045)
# ---------------------------------------------------------------------------
#
# Runs `validate.py --health-probe-only` which wraps probe_palace.py
# and probe_repo.py. Sub-second on a healthy state. Output is captured
# and surfaced based on the validator's exit code:
#
#   0 — healthy, single OK line.
#   1 — soft-warn (palace empty, etc.); pass-through stderr.
#   2 — hard-broken (chromadb segfault, parent core.bare=true);
#       emit a LOUD attention surface so the AI sees it at boot and
#       fixes before substantive work. Hook still exits 0 so the
#       session can start to receive the fix.
#
# Best-effort: if python3 or validate.py is missing, log fail and
# continue. The probe is informational at boot — never blocking.

PROBE_FOUND=0
PROBE_STATUS=""
VALIDATE_PY="$REPO_ROOT/engine/tools/validate.py"
if [ -x "$(command -v python3)" ] && [ -f "$VALIDATE_PY" ]; then
    PROBE_TMP="$(mktemp 2>/dev/null || echo "/tmp/session-start-probe.$$")"
    PROBE_TMP_ERR="$(mktemp 2>/dev/null || echo "/tmp/session-start-probe-err.$$")"
    python3 "$VALIDATE_PY" --health-probe-only \
        >"$PROBE_TMP" 2>"$PROBE_TMP_ERR"
    PROBE_EXIT=$?
    PROBE_FOUND=1
    case "$PROBE_EXIT" in
        0)
            echo "[session-start] Shared-state health: probes clean."
            PROBE_STATUS="clean"
            ;;
        1)
            {
                echo "[session-start] Shared-state health: SOFT-WARN findings:"
                cat "$PROBE_TMP_ERR" 2>/dev/null | sed 's/^/  /'
                echo "  See engine/operations/tools-validate-interpretation.md"
                echo "  for chromadb_palace_health / repo_config_health categories."
            } >&2
            PROBE_STATUS="soft-warn"
            ;;
        2)
            {
                echo ""
                echo "============================================================"
                echo "[session-start] Shared-state health: HARD-BROKEN — boot proceeds"
                echo "  but mempalace queries and parent-side git operations may"
                echo "  fail. Diagnose and fix BEFORE substantive work."
                echo "============================================================"
                cat "$PROBE_TMP_ERR" 2>/dev/null | sed 's/^/  /'
                echo "------------------------------------------------------------"
                echo "  See ADR 0045 (engine/adr/0045-shared-state-integrity-discipline.md)"
                echo "  for diagnostic commands and recovery procedures."
                echo "============================================================"
                echo ""
            } >&2
            PROBE_STATUS="hard-broken"
            ;;
        *)
            {
                echo "[session-start] Shared-state health: probe exited $PROBE_EXIT (unexpected)" >&2
                cat "$PROBE_TMP_ERR" 2>/dev/null | sed 's/^/  /' >&2
            }
            PROBE_STATUS="exit-$PROBE_EXIT"
            ;;
    esac
    rm -f "$PROBE_TMP" "$PROBE_TMP_ERR" 2>/dev/null
else
    log_fail "probe-prereq-missing"
    PROBE_STATUS="prereq-missing"
fi

# ---------------------------------------------------------------------------
# Persistent-warn surface (last 5 archives, 3-of-5 threshold)
# ---------------------------------------------------------------------------

if [ ! -d "$ARCHIVE_DIR" ]; then
    echo "[session-start] Persistent warns: archive directory absent."
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=no-archive"
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
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=no-archives"
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
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=calibration-window structured=$STRUCTURED_COUNT"
    exit 0
fi

# Aggregate per-category counts across the 5 most-recent archives. A category
# "fires in" an archive iff its count is >0.
#
# Bash 3.2 compatibility (per HANDOFF.md S-0035 entry, fixed at S-0036):
# associative arrays (declare -A) and ${!arr[@]} key iteration are bash 4+
# only. macOS ships /bin/bash 3.2; the shebang resolves to that. To stay
# portable, use parallel indexed arrays — CATEGORY_NAMES[i] holds the
# category name and CATEGORY_FIRINGS[i] holds the count of archives in
# which that category fires.
CATEGORY_NAMES=()
CATEGORY_FIRINGS=()

# Find the index of $1 in CATEGORY_NAMES; print -1 if absent. Local function
# scope in bash 3.2 is `local`-keyword; we explicitly mark loop vars local.
_find_category_index() {
    local target="$1"
    local i
    for ((i=0; i<${#CATEGORY_NAMES[@]}; i++)); do
        if [ "${CATEGORY_NAMES[$i]}" = "$target" ]; then
            echo "$i"
            return
        fi
    done
    echo "-1"
}

for archive in "${RECENT_ARCHIVES[@]}"; do
    while IFS=$'\t' read -r cat count; do
        if [ -n "$cat" ] && [ -n "$count" ] && [ "$count" -gt 0 ] 2>/dev/null; then
            idx="$(_find_category_index "$cat")"
            if [ "$idx" = "-1" ]; then
                CATEGORY_NAMES+=("$cat")
                CATEGORY_FIRINGS+=(1)
            else
                CATEGORY_FIRINGS[$idx]=$((${CATEGORY_FIRINGS[$idx]} + 1))
            fi
        fi
    done < <(jq -r '.outcome_summary_soft_warns // {} | to_entries[] | "\(.key)\t\(.value)"' "$archive" 2>/dev/null)
done

PERSISTENT_FOUND=0
for ((i=0; i<${#CATEGORY_NAMES[@]}; i++)); do
    cat="${CATEGORY_NAMES[$i]}"
    firings=${CATEGORY_FIRINGS[$i]}
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

# ---------------------------------------------------------------------------
# Scheduled-audit surface (engine/scheduled_audits.json)
# ---------------------------------------------------------------------------
#
# Added at S-0032 per the MemPalace audit plan. Distinct from the cadence-30
# health-check trigger above: that fires for broad project audits at
# regular intervals; this surfaces one-time adoption-checks tied to
# specific session-numbered triggers added by prior decisions.

SCHEDULED_AUDITS_FILE="$REPO_ROOT/engine/scheduled_audits.json"
SCHEDULED_FOUND=0

if [ -f "$SCHEDULED_AUDITS_FILE" ]; then
    # Match entries whose trigger_session equals "S-$NEXT_ID" (exact) or
    # whose trigger_session is in the past (a deferred audit that hasn't
    # landed yet). The numeric comparison uses the same 10# base-10 forcing
    # as the cadence calculation above.
    SCHEDULED_ENTRIES="$(jq -r --arg next "S-$NEXT_ID" '
        (.audits // [])
        | map(select(
            .trigger_session == $next
            or (
                (.trigger_session // "" | sub("^S-0*"; "") | tonumber? // -1)
                <= ($next | sub("^S-0*"; "") | tonumber? // -1)
            )
        ))
        | .[]
        | "  - \(.trigger_session): \(.description)"
    ' "$SCHEDULED_AUDITS_FILE" 2>/dev/null)"

    if [ -n "$SCHEDULED_ENTRIES" ]; then
        {
            echo "[session-start] Scheduled audits due (engine/scheduled_audits.json):"
            echo "$SCHEDULED_ENTRIES"
            echo "  Run the audit this session, or document the deferral in outcome_summary."
        } >&2
        SCHEDULED_FOUND=1
    fi
fi

log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=$PERSISTENT_FOUND scheduled=$SCHEDULED_FOUND probe=$PROBE_STATUS"
exit 0
