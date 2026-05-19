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
#      cadence-aligned slot was consumed by user-directed work — the trigger
#      sat dormant for nearly 2x the configured cadence in that case. At
#      S-0041, the logic was replaced with overdue-catchup:
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
#      At S-0196 per Issue #133, the surface split into two output lanes:
#      action-needed (categories firing >=3/5 without a documented
#      annotation) and annotated-baselines (categories firing >=3/5 that
#      carry an annotation in tools-validate-interpretation.md's
#      "Persistent-warn annotation" section, surfaced as a single-line
#      count). The split makes new threshold-crossings visible without
#      competing against documented-expected baselines.
#
#   3. Shared-state health probe — per ADR 0045. Runs
#      `validate.py --health-probe-only` (sub-second) which executes
#      probe_repo.py and probe_session_dir.py to catch parent .git/config
#      misset to bare and macOS Finder / iCloud-sync duplicate files in
#      engine/session/ before the AI tries to run parent-side git
#      operations. Hard-broken findings emit a LOUD stderr surface so the
#      AI sees them at boot and addresses them before substantive work;
#      the hook still exits 0 so the session can start (otherwise the AI
#      cannot even diagnose). engine_memory's SQLite + FTS5 substrate has
#      its own connect-time healthcheck() per ADR 0091 — no boot-time
#      subprocess surface needed here.
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

# ---------------------------------------------------------------------------
# Per-worktree liveness marker (per ADR 0076 amendment, S-0157 / Issue #120)
# ---------------------------------------------------------------------------
#
# Write a `session-live` marker into this worktree's PRIVATE git dir
# (.git/worktrees/<name>/ for a linked worktree, .git/ for the main repo).
# The boot-time bulk sweep (sweep_worktrees.sh) and the per-worktree tool
# (routine_worktree_sweep.py) read this marker's mtime and preserve any
# worktree whose marker is within a 24h freshness window.
#
# Why this exists: a session in plan/exploration mode has not run the
# eager-claim ritual, so register_state.json `current_status` is still
# `closed` and check_session_conflict.py reports no conflict. A sibling
# session booting in that window opens the sweep gate and reaps the
# plan-mode worktree (claude/* + clean + merged — it has made no commits
# yet). The marker is the liveness signal that lands at session boot,
# BEFORE eager-claim, closing the window. The marker sits in the private
# git dir — outside the working tree — so it never shows in `git status`
# and cannot make a worktree look dirty.
#
# Best-effort: any failure is logged and boot proceeds. The marker is a
# preserve hint, never a blocker.

WORKTREE_GIT_DIR="$(git rev-parse --absolute-git-dir 2>/dev/null)"
if [ -n "$WORKTREE_GIT_DIR" ] && [ -d "$WORKTREE_GIT_DIR" ]; then
    if echo "$TIMESTAMP" >"$WORKTREE_GIT_DIR/session-live" 2>/dev/null; then
        log_ok "liveness-marker-written $WORKTREE_GIT_DIR/session-live"
    else
        log_fail "liveness-marker-write-failed"
    fi
else
    log_fail "liveness-marker-git-dir-unresolved"
fi

# ---------------------------------------------------------------------------
# Version telemetry (per ADR 0080 engine, S-0147)
# ---------------------------------------------------------------------------
#
# Surfaces the active venv's Python version + the resolved venv prefix
# so the AI sees at boot which Python it's actually running. Closes the
# visibility gap that drove the S-0144→S-0146 cold-start confusion arc.
# Per ADR 0091 the chromadb + mempalace dependencies retired; the probe
# now reports only python + venv label.
#
# Verifies scrub_env.sh's PATH-prepend (per ADR 0050) actually won: when
# sys.prefix matches neither the worktree-local nor main-repo .venv/,
# emits a LOUD warning that system Python is resolving (and the AI
# should investigate before substantive work).
#
# Best-effort: probe failure (no python3, no venv, no git) emits a stderr
# log and proceeds. Always exits 0; the surface is informational.

VERSION_PROBE="$REPO_ROOT/engine/tools/probe_versions.py"
if [ -x "$(command -v python3)" ] && [ -f "$VERSION_PROBE" ]; then
    if ! python3 "$VERSION_PROBE" --repo "$REPO_ROOT" 2>/dev/null; then
        log_fail "version-probe-nonzero"
    fi
else
    log_fail "version-probe-prereq-missing"
fi

# jq is required for JSON parsing.
if ! command -v jq >/dev/null 2>&1; then
    log_fail "jq-not-installed"
    exit 0
fi

# ---------------------------------------------------------------------------
# Worktree-staleness check (per Issue #10 / S-0051)
# ---------------------------------------------------------------------------
#
# Surfaces when the working tree's HEAD is behind origin/main, which means
# shared-state files (register_state.json, current.json, auto_target.json)
# on disk reflect pre-update state. Symptom that motivated this check:
# S-0051 boot in worktree great-wright-9dd19b saw register_state.json
# showing S-0050 in_progress; S-0050 had actually closed and pushed to
# origin/main, but this worktree was created at pre-shutdown HEAD and
# never fast-forwarded. The AI spent ~30 min investigating "why didn't
# routine shut down" before discovering the state was stale.
#
# Runs early (before cadence trigger reads register_state.json) so the
# warning surfaces before any stale-data-derived counts. Best-effort: a
# git fetch failure (no network, etc.) emits a stderr note and proceeds.
# Hook always exits 0; the check is informational, never blocking.

STALE_CHECK_STATUS="not-run"
if command -v git >/dev/null 2>&1 && [ -d "$REPO_ROOT/.git" -o -f "$REPO_ROOT/.git" ]; then
    if git -C "$REPO_ROOT" fetch --no-tags --quiet origin main 2>/dev/null; then
        if git -C "$REPO_ROOT" merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
            STALE_CHECK_STATUS="up-to-date"
        else
            LOCAL_HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null)"
            REMOTE_MAIN="$(git -C "$REPO_ROOT" rev-parse origin/main 2>/dev/null)"
            BEHIND_COUNT="$(git -C "$REPO_ROOT" rev-list --count HEAD..origin/main 2>/dev/null)"
            BEHIND_COUNT="${BEHIND_COUNT:-?}"
            {
                echo ""
                echo "============================================================"
                echo "[session-start] STALE WORKTREE: HEAD is behind origin/main by $BEHIND_COUNT commit(s)"
                echo "============================================================"
                echo "  HEAD:        ${LOCAL_HEAD:0:7}"
                echo "  origin/main: ${REMOTE_MAIN:0:7}"
                echo ""
                echo "  Shared-state files on disk (register_state.json,"
                echo "  current.json, auto_target.json) may reflect pre-update"
                echo "  state. Boot-surface counts below may be wrong."
                echo ""
                echo "  Recover before substantive work:"
                echo "    git fetch && git merge --ff-only origin/main"
                echo "============================================================"
                echo ""
            } >&2
            STALE_CHECK_STATUS="behind-$BEHIND_COUNT"
        fi
    else
        log_fail "git-fetch-failed-or-offline"
        STALE_CHECK_STATUS="fetch-failed"
    fi
else
    STALE_CHECK_STATUS="not-a-git-repo"
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
# .env onboarding pointer (per Issue #7 / S-0048; parent-repo fallback per
# Issue #50 / S-0099)
# ---------------------------------------------------------------------------
#
# When auto_target.json is present (routine-mode is configured) AND .env is
# missing SUPABASE_DB_URL, emit a LOUD pointer at boot so the user knows to
# run `python3 engine/tools/setup_env.py` once. The pointer is informational
# only — the hook always exits 0. Without SUPABASE_DB_URL, every Phase 5
# routine fire bails cleanly per its own checks; the pointer just makes the
# remediation discoverable.
#
# Worktree-aware resolution (Issue #50): inside a worktree, REPO_ROOT
# resolves to the worktree path (per `git rev-parse --show-toplevel` at
# line 58), but `.env` is gitignored so it does not propagate to worktrees.
# When the worktree's .env is absent or lacks SUPABASE_DB_URL, fall back to
# the parent main repo's .env. Resolution: `git rev-parse --git-common-dir`
# returns the parent's .git directory (e.g., `/parent/.git`) from inside a
# worktree; `dirname` of that gives the parent repo path. From a non-
# worktree session, `--git-common-dir` returns `$REPO_ROOT/.git` so the
# fallback path equals REPO_ROOT — same path, no behavior change. The LOUD
# pointer fires only when NEITHER location carries the URL, preserving the
# original Issue #7 / S-0048 contract.
#
# This is one-time-onboarding scaffolding. After the user runs setup_env.py
# once, .env carries the URL forever (gitignored) and this pointer goes
# silent for all future boots.

ENV_FILE="$REPO_ROOT/.env"
AUTO_TARGET_FILE="$REPO_ROOT/engine/session/auto_target.json"
ENV_POINTER_STATUS="not-checked"
if [ -f "$AUTO_TARGET_FILE" ]; then
    DB_URL_PRESENT=0
    if [ -f "$ENV_FILE" ] && grep -q '^SUPABASE_DB_URL=.\+' "$ENV_FILE" 2>/dev/null; then
        DB_URL_PRESENT=1
    else
        # Parent-repo fallback (worktree case). git rev-parse --git-common-dir
        # returns /<parent>/.git from inside a worktree; dirname → parent.
        # From a non-worktree session it returns $REPO_ROOT/.git → same path.
        PARENT_GIT_DIR="$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null)"
        if [ -n "$PARENT_GIT_DIR" ]; then
            case "$PARENT_GIT_DIR" in
                /*) PARENT_REPO="$(dirname "$PARENT_GIT_DIR")" ;;
                *)  PARENT_REPO="$(cd "$REPO_ROOT" 2>/dev/null && cd "$(dirname "$PARENT_GIT_DIR")" 2>/dev/null && pwd)" ;;
            esac
            if [ -n "$PARENT_REPO" ] && [ "$PARENT_REPO" != "$REPO_ROOT" ]; then
                PARENT_ENV="$PARENT_REPO/.env"
                if [ -f "$PARENT_ENV" ] && grep -q '^SUPABASE_DB_URL=.\+' "$PARENT_ENV" 2>/dev/null; then
                    DB_URL_PRESENT=1
                fi
            fi
        fi
    fi
    if [ "$DB_URL_PRESENT" -eq 0 ]; then
        {
            echo ""
            echo "============================================================"
            echo "[session-start] .env onboarding pointer"
            echo "============================================================"
            echo "  SUPABASE_DB_URL is missing from .env. Without it, every"
            echo "  Phase 5 routine fire will bail at the migration_applied /"
            echo "  validate_passes criteria (Issue #7)."
            echo ""
            echo "  One-time setup (gitignored .env persists forever after):"
            echo "    python3 engine/tools/setup_env.py"
            echo ""
            echo "  Prompts for SUPABASE_DB_URL only, validates with a real"
            echo "  psycopg.connect(), writes .env on success. Re-runnable;"
            echo "  idempotent. Skip if you're not running Phase 5 routines"
            echo "  in this session."
            echo "============================================================"
            echo ""
        } >&2
        ENV_POINTER_STATUS="missing-supabase-db-url"
    else
        ENV_POINTER_STATUS="ok"
    fi
fi

# ---------------------------------------------------------------------------
# Concurrent-session collision check (per Issue #3 / S-0048)
# ---------------------------------------------------------------------------
#
# Surfaces when register_state.json says current_status: in_progress at boot.
# Hook is informational and never blocks; the slash command's boot procedure
# (`.claude/commands/start-engine.md` step 4b) is what actually refuses to
# claim. Three exit codes:
#
#   0 — no conflict (current_status closed/absent or current.json absent)
#   1 — recent collision (<1h) or ambiguous mid-window
#   2 — stale (>24h) — likely dead session, recovery candidate
#
# The hook surfaces all three to stderr (so the AI sees them at boot) and
# logs the disposition. The session can still start; the AI is responsible
# for honoring the surface before claiming.

CONFLICT_TOOL="$REPO_ROOT/engine/tools/check_session_conflict.py"
CONFLICT_STATUS="not-run"
if [ -x "$(command -v python3)" ] && [ -f "$CONFLICT_TOOL" ]; then
    CONFLICT_TMP_OUT="$(mktemp 2>/dev/null || echo "/tmp/session-start-conflict.$$")"
    CONFLICT_TMP_ERR="$(mktemp 2>/dev/null || echo "/tmp/session-start-conflict-err.$$")"
    python3 "$CONFLICT_TOOL" --repo-root "$REPO_ROOT" \
        >"$CONFLICT_TMP_OUT" 2>"$CONFLICT_TMP_ERR"
    CONFLICT_EXIT=$?
    case "$CONFLICT_EXIT" in
        0)
            CONFLICT_STATUS="no-conflict"
            ;;
        1)
            cat "$CONFLICT_TMP_ERR" >&2 2>/dev/null
            CONFLICT_STATUS="recent-or-ambiguous"
            ;;
        2)
            cat "$CONFLICT_TMP_ERR" >&2 2>/dev/null
            CONFLICT_STATUS="stale"
            ;;
        *)
            CONFLICT_STATUS="exit-$CONFLICT_EXIT"
            log_fail "session-conflict-exit-$CONFLICT_EXIT"
            ;;
    esac
    rm -f "$CONFLICT_TMP_OUT" "$CONFLICT_TMP_ERR" 2>/dev/null
else
    log_fail "session-conflict-prereq-missing"
    CONFLICT_STATUS="prereq-missing"
fi

# ---------------------------------------------------------------------------
# Boot-time worktree bulk sweep (per ADR 0076 Amendment v2 / S-0143)
# ---------------------------------------------------------------------------
#
# After every session boot, run sweep_worktrees.sh --apply --quiet to
# collect previously-closed sessions' worktrees that survived their own
# close (per ADR 0076 Amendment v2's skip-caller defense in both
# routine_worktree_sweep.py and sweep_worktrees.sh). The bulk utility
# unconditionally preserves:
#   - The caller's enclosing worktree (in-flight session — this one).
#   - Worktrees with branches not matching claude/*.
#   - Worktrees with uncommitted changes or untracked files.
#   - Worktrees whose branch has unmerged commits ahead of main.
#
# Gated on CONFLICT_STATUS == "no-conflict" — if another session is in
# flight, defer the sweep to avoid the race where a concurrent session's
# transiently-clean worktree could be reaped between their eager-claim
# push and their next dirty edit (the skip-caller check protects against
# self-sweep but not against sibling sessions).
#
# Best-effort: any failure emits a stderr line and the boot proceeds.

SWEEP_SCRIPT="$REPO_ROOT/engine/tools/sweep_worktrees.sh"
SWEEP_STATUS="not-run"
if [ "$CONFLICT_STATUS" = "no-conflict" ] && [ -x "$SWEEP_SCRIPT" ]; then
    SWEEP_TMP="$(mktemp 2>/dev/null || echo "/tmp/session-start-sweep.$$")"
    if bash "$SWEEP_SCRIPT" --apply --quiet >"$SWEEP_TMP" 2>&1; then
        SWEEP_STATUS="ok"
    else
        SWEEP_STATUS="exit-nonzero"
        log_fail "boot-sweep-exit-nonzero"
    fi
    # Emit the tool's per-line output to stderr so the AI + user see what
    # was removed and what was preserved. In --quiet mode the tool emits
    # one line per preserved worktree (path + short reason) plus a final
    # `[sweep] removed N, preserved K` summary.
    if [ -s "$SWEEP_TMP" ]; then
        cat "$SWEEP_TMP" >&2 2>/dev/null
    fi
    rm -f "$SWEEP_TMP" 2>/dev/null
elif [ ! -x "$SWEEP_SCRIPT" ]; then
    log_fail "boot-sweep-script-missing"
    SWEEP_STATUS="script-missing"
else
    SWEEP_STATUS="deferred-concurrent-session"
fi

# ---------------------------------------------------------------------------
# Shared-state health probe (per ADR 0045)
# ---------------------------------------------------------------------------
#
# Runs `validate.py --health-probe-only` which wraps probe_repo.py and
# probe_session_dir.py. Sub-second on a healthy state. Output is captured
# and surfaced based on the validator's exit code:
#
#   0 — healthy, single OK line.
#   1 — soft-warn (probe-reported issue, e.g. repo_config_health); pass-through stderr.
#   2 — hard-broken (parent core.bare=true, session_dir duplicate-file corruption);
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
                echo "  for repo_config_health / session_dir_strays categories."
            } >&2
            PROBE_STATUS="soft-warn"
            ;;
        2)
            {
                echo ""
                echo "============================================================"
                echo "[session-start] Shared-state health: HARD-BROKEN — boot proceeds"
                echo "  but parent-side git operations may fail. Diagnose and"
                echo "  fix BEFORE substantive work."
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
# CI-red on main surface (per ADR 0065 — S-0131)
# ---------------------------------------------------------------------------
#
# Reads the most recent GitHub Actions run on main and emits a LOUD block
# when it concluded `failure`. The cleanup-session signal for routine-mode
# lifecycle pushes that bypass synchronous CI wait per ADR 0054 +
# routine_lifecycle_push.py.
#
# Silent when:
#   - status is success (the healthy case)
#   - status is null / empty / "in_progress" (no completed runs to judge)
#   - `gh` binary is missing OR network unavailable (legitimate offline-boot;
#     surfacing in this case would be noise, not signal)
#
# Exits 0 regardless (per the project's hook contract — boot must proceed).

if command -v gh >/dev/null 2>&1; then
    CI_STATUS=$(gh run list --branch main --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "")
    if [ "$CI_STATUS" = "failure" ]; then
        {
            echo ""
            echo "============================================================"
            echo "[session-start] CI RED on main"
            echo "============================================================"
            echo "  The most recent CI run on main concluded FAILURE."
            echo "  Inspect:  gh run list --branch main --limit 5"
            echo "            gh run view <run-id> --log-failed"
            echo ""
            echo "  Red on main after a routine_lifecycle_push.py push is the"
            echo "  expected cleanup-session signal per ADR 0065 (CI mirror)."
            echo "  Either fix-in-context if scope-compatible, or open a"
            echo "  cleanup-session issue via gh issue create."
            echo "============================================================"
            echo ""
        } >&2
    fi
fi


# ---------------------------------------------------------------------------
# Issues backlog visibility (per ADR 0048)
# ---------------------------------------------------------------------------
#
# Calls scan_issue_backlog.py which wraps `gh issue list` and emits
# either a single-line FYI ("Issues backlog: N bugs, ...") or a
# multi-line LOUD attention block when any issue carries
# `priority:urgent`. Best-effort: a gh failure (no auth, no network,
# repo not on GitHub) emits a stderr note; the boot proceeds.
#
# Surfaces the backlog count at every boot so the user can see the
# trend across sessions and dedicate cleanup-batch sessions when the
# count crosses a threshold worth addressing.

BACKLOG_TOOL="$REPO_ROOT/engine/tools/scan_issue_backlog.py"
BACKLOG_STATUS="not-run"
if [ -x "$(command -v python3)" ] && [ -f "$BACKLOG_TOOL" ]; then
    if python3 "$BACKLOG_TOOL" 2>/dev/null; then
        BACKLOG_STATUS="ok"
    else
        # Non-zero exit is reserved by the tool but currently unused.
        # Treat as soft failure: log and proceed.
        BACKLOG_STATUS="exit-nonzero"
        log_fail "backlog-scan-nonzero"
    fi
else
    log_fail "backlog-prereq-missing"
    BACKLOG_STATUS="prereq-missing"
fi

# ---------------------------------------------------------------------------
# Dependabot PR visibility (per ADR 0080 engine, S-0147)
# ---------------------------------------------------------------------------
#
# Sibling to scan_issue_backlog.py. Closes the gap that allowed ADR 0069's
# Dependabot PRs to sit invisible — the boot surface previously counted
# Issues, never queried gh pr list. Emits quiet (0 PRs), single-line FYI
# (1–4 fresh), or multi-line LOUD (≥5 OR any ≥7d) attention block.
# Best-effort: gh failure emits stderr note and proceeds.

DEPABOT_TOOL="$REPO_ROOT/engine/tools/scan_dependabot_prs.py"
DEPABOT_STATUS="not-run"
if [ -x "$(command -v python3)" ] && [ -f "$DEPABOT_TOOL" ]; then
    if python3 "$DEPABOT_TOOL" 2>/dev/null; then
        DEPABOT_STATUS="ok"
    else
        DEPABOT_STATUS="exit-nonzero"
        log_fail "dependabot-scan-nonzero"
    fi
else
    log_fail "dependabot-scan-prereq-missing"
    DEPABOT_STATUS="prereq-missing"
fi

# ---------------------------------------------------------------------------
# Persistent-warn surface (last 5 archives, 3-of-5 threshold)
# ---------------------------------------------------------------------------

if [ ! -d "$ARCHIVE_DIR" ]; then
    echo "[session-start] Persistent warns: archive directory absent."
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=no-archive boot_sweep=$SWEEP_STATUS"
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
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=no-archives boot_sweep=$SWEEP_STATUS"
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
    log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=calibration-window structured=$STRUCTURED_COUNT boot_sweep=$SWEEP_STATUS"
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

# Load the annotated-category list once via the helper. The helper parses
# the "Persistent-warn annotation" H2 section of
# engine/operations/tools-validate-interpretation.md (Issue #133 / S-0196
# per ADR 0042). Failure modes (helper absent, parse error, exit != 0):
# leave ANNOTATED_LIST empty so all categories surface as action-needed —
# graceful degradation preserves visibility on parser break.
ANNOTATED_HELPER="$REPO_ROOT/engine/tools/scan_persistent_warn_annotations.py"
ANNOTATED_LIST=""
if [ -f "$ANNOTATED_HELPER" ]; then
    ANNOTATED_LIST="$(python3 "$ANNOTATED_HELPER" 2>/dev/null)"
fi

# Returns success (0) if $1 is a category name carried in ANNOTATED_LIST,
# failure (1) otherwise. Bash 3.2-safe: newline-anchored grep against
# the captured list.
_is_annotated() {
    local target="$1"
    if [ -z "$ANNOTATED_LIST" ]; then
        return 1
    fi
    printf '%s\n' "$ANNOTATED_LIST" | grep -qx -- "$target"
}

# Pass 1 — action-needed lane (categories firing >=3/5 without an
# annotation). Header + per-line surface + the existing tail hint.
PERSISTENT_FOUND=0
for ((i=0; i<${#CATEGORY_NAMES[@]}; i++)); do
    cat="${CATEGORY_NAMES[$i]}"
    firings=${CATEGORY_FIRINGS[$i]}
    if [ "$firings" -ge 3 ] && ! _is_annotated "$cat"; then
        if [ "$PERSISTENT_FOUND" -eq 0 ]; then
            echo "[session-start] Persistent warns (action-needed):" >&2
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
fi

# Pass 2 — annotated-baselines lane (categories firing >=3/5 that carry
# a documented annotation). Single-line summary count + pointer.
# Categories continue to fire per-commit; this lane is the periodic
# reminder that the bucket exists, without competing with action-needed
# alerts. Per Issue #133 / S-0196.
ANNOTATED_FOUND=0
for ((i=0; i<${#CATEGORY_NAMES[@]}; i++)); do
    cat="${CATEGORY_NAMES[$i]}"
    firings=${CATEGORY_FIRINGS[$i]}
    if [ "$firings" -ge 3 ] && _is_annotated "$cat"; then
        ANNOTATED_FOUND=$((ANNOTATED_FOUND + 1))
    fi
done

if [ "$ANNOTATED_FOUND" -ge 1 ]; then
    {
        if [ "$ANNOTATED_FOUND" -eq 1 ]; then
            label="category"
        else
            label="categories"
        fi
        echo "[session-start] Persistent warns (annotated baselines): $ANNOTATED_FOUND $label carrying annotated-baseline status; see engine/operations/tools-validate-interpretation.md \"Persistent-warn annotation\". These continue to fire per-commit but do not surface as action-needed."
    } >&2
fi

if [ "$PERSISTENT_FOUND" -eq 0 ] && [ "$ANNOTATED_FOUND" -eq 0 ]; then
    echo "[session-start] Persistent warns: none above the 3-of-5 threshold."
fi

# ---------------------------------------------------------------------------
# Multi-session scope-erosion signal (per ADR 0049)
# ---------------------------------------------------------------------------
#
# Walks the same RECENT_ARCHIVES window. Counts how many archives carry
# scope_delivery.delivered = false. Surface fires at >= 3 of 5.
#
# Same surface treatment as the persistent-warn pattern. Best-effort:
# archives that pre-date the field don't count toward the threshold.

SCOPE_NON_YES=0
for archive in "${RECENT_ARCHIVES[@]}"; do
    if jq -e '.scope_delivery.delivered == false' "$archive" >/dev/null 2>&1; then
        SCOPE_NON_YES=$((SCOPE_NON_YES + 1))
    fi
done

if [ "$SCOPE_NON_YES" -ge 3 ]; then
    {
        echo "[session-start] Scope-delivery non-yes in $SCOPE_NON_YES of last ${#RECENT_ARCHIVES[@]} sessions."
        echo "  Per ADR 0049, this signals scope-discipline drift across sessions."
        echo "  Review the recent scope_delivery answers in engine/session/archive/*.json"
        echo "  and consider tighter declared_scope at boot or smaller chunks."
    } >&2
fi

# ---------------------------------------------------------------------------
# Hook-bypass audit-log surface (.engine_reports/hook-bypass.log)
# ---------------------------------------------------------------------------
#
# Per ADR 0100. The SKIP_ENGINE_HOOKS=1 audited bypass logs each use to
# .engine_reports/hook-bypass.log (per-clone, gitignored). At every
# session boot we surface unread entries as a LOUD attention block so
# every bypass is visible to a subsequent session even if the using
# session never named it. The "unread" boundary is the most recent
# closed session's started_at — anything newer surfaces.
#
# Best-effort: if jq is missing or the log is unreadable, log fail and
# continue. The surveillance is informational at boot — never blocking.

HOOK_BYPASS_LOG="$REPO_ROOT/.engine_reports/hook-bypass.log"
BYPASS_FOUND=0

if [ -s "$HOOK_BYPASS_LOG" ]; then
    # Find the most recent closed session's started_at to use as the
    # "unread" boundary. Falls back to "show everything" if no archives.
    LATEST_ARCHIVE="$(ls -t "$REPO_ROOT/engine/session/archive/"S-*.json 2>/dev/null | head -1)"
    BOUNDARY_TIMESTAMP=""
    if [ -n "$LATEST_ARCHIVE" ] && [ -x "$(command -v jq)" ]; then
        BOUNDARY_TIMESTAMP="$(jq -r '.started_at // empty' "$LATEST_ARCHIVE" 2>/dev/null)"
    fi

    # Each line shape: [ISO-8601] pre-commit bypass: branch=... user=... subject=...
    # Filter to lines newer than BOUNDARY_TIMESTAMP. Lexicographic compare
    # works because ISO-8601 is lex-ordered.
    if [ -n "$BOUNDARY_TIMESTAMP" ]; then
        UNREAD_ENTRIES="$(awk -v boundary="$BOUNDARY_TIMESTAMP" '
            match($0, /^\[([^\]]+)\]/, m) {
                if (m[1] > boundary) print
            }
        ' "$HOOK_BYPASS_LOG" 2>/dev/null)"
    else
        # No boundary → show everything (max 5 most-recent entries).
        UNREAD_ENTRIES="$(tail -5 "$HOOK_BYPASS_LOG" 2>/dev/null)"
    fi

    if [ -n "$UNREAD_ENTRIES" ]; then
        UNREAD_COUNT="$(echo "$UNREAD_ENTRIES" | wc -l | tr -d ' ')"
        {
            echo ""
            echo "============================================================"
            echo "[session-start] HOOK-BYPASS audit: $UNREAD_COUNT unread entry(ies)"
            echo "  in $HOOK_BYPASS_LOG since last closed session."
            echo ""
            echo "$UNREAD_ENTRIES" | sed 's/^/  /'
            echo ""
            echo "  Each entry is a SKIP_ENGINE_HOOKS=1 use bypassing pre-commit."
            echo "  Per ADR 0100, bypass is intended for rare close-friction"
            echo "  cases only. Review whether each use was legitimate and"
            echo "  whether the underlying issue should be fixed (Issue / ADR)."
            echo "============================================================"
            echo ""
        } >&2
        BYPASS_FOUND=1
    fi
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

log_ok "cadence-fires=$CADENCE_FIRES cadence-mode=$CADENCE_TRIGGER_REASON slots-since=${SLOTS_SINCE:-NA} persistent-warns=$PERSISTENT_FOUND persistent-warns-annotated=$ANNOTATED_FOUND scheduled=$SCHEDULED_FOUND probe=$PROBE_STATUS backlog=$BACKLOG_STATUS scope_non_yes=$SCOPE_NON_YES conflict=$CONFLICT_STATUS env_pointer=$ENV_POINTER_STATUS stale_check=$STALE_CHECK_STATUS boot_sweep=$SWEEP_STATUS hook_bypass=$BYPASS_FOUND"
exit 0
