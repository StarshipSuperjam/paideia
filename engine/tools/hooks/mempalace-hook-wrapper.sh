#!/bin/bash
#
# Paideia MemPalace capture-hook wrapper.
#
# Wraps `mempalace hook run` so capture failures (binary missing, daemon down,
# capture errored, or post-mine corruption) surface to a session-visible log
# instead of failing silently. Always exits 0 to the harness regardless of
# mempalace's actual exit code — the log carries the truth. The next session's
# boot procedure reads the log and surfaces unacknowledged failure entries.
#
# Wired in .claude/settings.json as the Stop and PreCompact hook command.
# Pass-through args: --hook <stop|precompact> --harness <name>.
# Pass-through stdin: the harness's JSON event payload.
#
# Log path: .claude/logs/mempalace-hook.log (gitignored under .claude/* — the
# log is per-clone state, not project state).
#
# === Atomic-write discipline (per ADR 0045) ===
#
# S-0034 surfaced a corrupt chromadb HNSW segment for the
# `mempalace_drawers` collection that crashed every subsequent session
# at the first query. Cause: the rust binding writes segment files
# in-place; a mid-write kill or env-leak corruption produces a corrupt
# segment that's only detected on the next read.
#
# Mitigation: this wrapper takes a `cp -a` snapshot of ~/.mempalace/palace
# (and the knowledge_graph.sqlite3* files) BEFORE invoking mempalace,
# runs probe_palace.py AFTER, and rolls back from the snapshot on probe
# failure. One last-good snapshot is retained at palace.last-good for
# debugging; the in-progress snapshot at palace.pre-mine exists only
# during a hook run and is rotated on success or consumed on failure.
#
# Snapshot semantics: cp -a is byte-level, not transactional. If the
# long-running mempalace MCP server has the chromadb sqlite open mid-WAL
# write, the snapshot may be slightly inconsistent at the byte level.
# The trade is accepted because (a) chromadb uses WAL mode so reads
# don't block writes; (b) the snapshot is a recovery point, not a
# perfect transactional baseline; (c) the cost of post-mine HNSW
# corruption (multi-session crash loop) dwarfs the cost of an
# imperfect rollback target.

# ---------------------------------------------------------------------------
# Resolve repo root and source the env scrubber
# ---------------------------------------------------------------------------

# Scrub GIT_* env first per ADR 0045. The `mempalace` subprocess shells
# out internally and inherits this hook's environment; a leaked GIT_DIR
# would point internal git operations at the wrong repo. Defense-in-depth
# against the S-0033 vector pattern.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
SCRUB_HELPER="$SCRIPT_DIR/../scrub_env.sh"
if [ -f "$SCRUB_HELPER" ]; then
    # shellcheck source=../scrub_env.sh
    source "$SCRUB_HELPER"
    scrub_git_env
fi

# Resolve repo root. Prefer git's view; fall back to the wrapper's own location
# (the script lives at <repo>/engine/tools/hooks/mempalace-hook-wrapper.sh
# post-S-0024 partition migration per ADR 0037).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." 2>/dev/null && pwd)"
fi

LOG_DIR="$REPO_ROOT/.claude/logs"
LOG_FILE="$LOG_DIR/mempalace-hook.log"

# Best-effort log-dir creation. Failures here are themselves silent — the
# alternative (failing the harness) is worse.
mkdir -p "$LOG_DIR" 2>/dev/null

# Capture stderr to a temp file so the failure log line can include a snippet.
STDERR_FILE="$(mktemp 2>/dev/null || echo "/tmp/mempalace-hook-stderr.$$")"

# Capture the wrapper start timestamp BEFORE invoking mempalace. Used
# by the defensive post-hook sessions-wing pollution prune (per ADR
# 0090 commitment 2b) — the prune deletes only drawers added with
# created_at > $HOOK_START_TS, leaving prior hook fires' content
# alone. Retire when upstream MemPalace PR #1511 lands (MEMPALACE_WING
# env-var override) and the source pollution stops.
HOOK_START_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# ---------------------------------------------------------------------------
# Resolve mempalace binary
# ---------------------------------------------------------------------------

# STATE.md notes the user-scope install at ~/Library/Python/3.9/bin/. The
# harness's PATH may not include it; fall back to the literal user-scope
# path before giving up. Mirrors the resolution pattern in post-adr-write.sh
# per ADR 0043. Without this fallback the wrapper writes FAIL exit=127 on
# every Stop / PreCompact event when invoked from a Claude Code subshell —
# the actual cause of the silent auto-capture breakage diagnosed at S-0032.
MEMPALACE_BIN=""
if command -v mempalace >/dev/null 2>&1; then
    MEMPALACE_BIN="mempalace"
elif [ -x "$HOME/Library/Python/3.9/bin/mempalace" ]; then
    MEMPALACE_BIN="$HOME/Library/Python/3.9/bin/mempalace"
fi

# ---------------------------------------------------------------------------
# Pre-mine snapshot (per ADR 0045)
# ---------------------------------------------------------------------------

PALACE_DIR="$HOME/.mempalace/palace"
PALACE_PRE_MINE="$HOME/.mempalace/palace.pre-mine"
PALACE_LAST_GOOD="$HOME/.mempalace/palace.last-good"
KG_GLOB_DIR="$HOME/.mempalace"
KG_SNAPSHOT_DIR="$HOME/.mempalace/kg.pre-mine"

# Clear any leftover in-progress snapshot from a previous interrupted run.
rm -rf "$PALACE_PRE_MINE" 2>/dev/null
rm -rf "$KG_SNAPSHOT_DIR" 2>/dev/null

SNAPSHOT_TAKEN=0
if [ -d "$PALACE_DIR" ]; then
    if cp -a "$PALACE_DIR" "$PALACE_PRE_MINE" 2>>"$LOG_FILE"; then
        SNAPSHOT_TAKEN=1
    fi
fi

if [ "$SNAPSHOT_TAKEN" -eq 1 ]; then
    mkdir -p "$KG_SNAPSHOT_DIR" 2>/dev/null
    # SQLite WAL discipline: copy main db, -shm, and -wal together so a
    # rollback restores all three to a consistent point.
    for kg_file in "$KG_GLOB_DIR"/knowledge_graph.sqlite3 \
                   "$KG_GLOB_DIR"/knowledge_graph.sqlite3-shm \
                   "$KG_GLOB_DIR"/knowledge_graph.sqlite3-wal; do
        [ -f "$kg_file" ] && cp -a "$kg_file" "$KG_SNAPSHOT_DIR/" 2>/dev/null
    done
fi

# ---------------------------------------------------------------------------
# Invoke mempalace hook run
# ---------------------------------------------------------------------------

# Manual sentinel for the manual-failure test: if
# PAIDEIA_MEMPALACE_HOOK_FORCE_FAIL=1, skip the real binary and synthesize
# a failure — used during S-0020 verification per the approved plan, never
# set in production.
if [ "$PAIDEIA_MEMPALACE_HOOK_FORCE_FAIL" = "1" ]; then
    echo "forced failure (PAIDEIA_MEMPALACE_HOOK_FORCE_FAIL=1)" >"$STDERR_FILE"
    EXIT_CODE=99
elif [ -z "$MEMPALACE_BIN" ]; then
    echo "mempalace binary not found in PATH or at ~/Library/Python/3.9/bin/mempalace" >"$STDERR_FILE"
    EXIT_CODE=127
else
    "$MEMPALACE_BIN" hook run "$@" 2>"$STDERR_FILE"
    EXIT_CODE=$?
fi

# ---------------------------------------------------------------------------
# Post-mine probe and disposition
# ---------------------------------------------------------------------------
#
# Probe verdicts:
#   healthy        — probe_palace.py exit 0; mining produced a usable palace.
#   suspect-1      — probe exit 1; soft-warn condition (e.g., empty palace).
#                    Treated as success (no rollback) because soft-warn isn't
#                    corruption.
#   broken-2       — probe exit 2; hard-broken. Roll back.
#   broken-139     — probe segfaulted; treat as hard-broken. Roll back.
#                    This is the S-0034 chromadb-rust-binding signature.
#   probe-skipped  — no snapshot to roll back to (first mine on empty
#                    palace). Trust mempalace's exit code.
#   probe-missing  — probe_palace.py absent or python3 missing. Trust
#                    mempalace's exit code; log the gap.

PROBE_VERDICT="probe-skipped"
PROBE_EXIT="-"

if [ "$SNAPSHOT_TAKEN" -eq 1 ]; then
    PROBE_PY="$REPO_ROOT/engine/tools/probe_palace.py"
    if [ -f "$PROBE_PY" ] && command -v python3 >/dev/null 2>&1; then
        # Capture probe stderr separately so palace findings don't pollute
        # the mempalace stderr file.
        PROBE_ERR="$(mktemp 2>/dev/null || echo "/tmp/mempalace-probe-err.$$")"
        python3 "$PROBE_PY" >/dev/null 2>"$PROBE_ERR"
        PROBE_EXIT=$?
        case "$PROBE_EXIT" in
            0) PROBE_VERDICT="healthy" ;;
            1) PROBE_VERDICT="suspect-1" ;;
            2) PROBE_VERDICT="broken-2" ;;
            139) PROBE_VERDICT="broken-139" ;;
            *) PROBE_VERDICT="broken-$PROBE_EXIT" ;;
        esac
        # If probe broken, append its stderr to the mempalace stderr file
        # so the eventual log line carries both surfaces.
        case "$PROBE_VERDICT" in
            broken-*) cat "$PROBE_ERR" >>"$STDERR_FILE" 2>/dev/null ;;
        esac
        rm -f "$PROBE_ERR" 2>/dev/null
    else
        PROBE_VERDICT="probe-missing"
    fi
fi

ROLLBACK_DONE=0
POST_PRUNE_DELETED="-"
case "$PROBE_VERDICT" in
    broken-*)
        # Roll back palace from snapshot; restore KG.
        rm -rf "$PALACE_DIR" 2>/dev/null
        if mv "$PALACE_PRE_MINE" "$PALACE_DIR" 2>>"$LOG_FILE"; then
            ROLLBACK_DONE=1
            for kg_base in knowledge_graph.sqlite3 knowledge_graph.sqlite3-shm \
                           knowledge_graph.sqlite3-wal; do
                if [ -f "$KG_SNAPSHOT_DIR/$kg_base" ]; then
                    cp -a "$KG_SNAPSHOT_DIR/$kg_base" "$KG_GLOB_DIR/$kg_base" 2>/dev/null
                fi
            done
        fi
        # Treat post-rollback as failure for the eventual log line so the
        # next-session boot surface picks it up.
        if [ "$EXIT_CODE" -eq 0 ]; then
            EXIT_CODE=1
        fi
        ;;
    *)
        # Successful (or trusted-without-probe) mine: rotate snapshot to
        # last-good for debugging. One snapshot retained between hook fires.
        if [ "$SNAPSHOT_TAKEN" -eq 1 ]; then
            rm -rf "$PALACE_LAST_GOOD" 2>/dev/null
            mv "$PALACE_PRE_MINE" "$PALACE_LAST_GOOD" 2>/dev/null
        fi

        # Defensive post-hook sessions-wing pollution prune. Per ADR
        # 0090 commitment 2b. Deletes drawers added by THIS hook fire
        # into ``sessions/<noise-room>`` while preserving curated rooms
        # (decisions/lessons/pushback/diary) in the same wing. Runs
        # only on probe-healthy paths so a rolled-back state is not
        # mutated further. Failures are logged but do NOT block the
        # hook — the prune is advisory recurrence-prevention, not a
        # capture-integrity gate.
        POST_PRUNE_PY="$REPO_ROOT/engine/tools/mempalace_post_hook_prune.py"
        if [ -f "$POST_PRUNE_PY" ] && command -v python3 >/dev/null 2>&1; then
            POST_PRUNE_OUT="$(python3 "$POST_PRUNE_PY" --since "$HOOK_START_TS" 2>&1)"
            POST_PRUNE_EXIT=$?
            if [ "$POST_PRUNE_EXIT" -eq 0 ]; then
                # Parse the count from the stderr message; default to 0 on no-op.
                POST_PRUNE_DELETED="$(echo "$POST_PRUNE_OUT" | sed -n 's/.*deleted \([0-9]*\) sessions-wing.*/\1/p')"
                [ -z "$POST_PRUNE_DELETED" ] && POST_PRUNE_DELETED=0
            else
                POST_PRUNE_DELETED="err-$POST_PRUNE_EXIT"
            fi
        fi
        ;;
esac

# Always clean up the KG snapshot dir; its contents have been restored
# (rollback case) or are no longer needed (success case).
rm -rf "$KG_SNAPSHOT_DIR" 2>/dev/null

# ---------------------------------------------------------------------------
# Log line
# ---------------------------------------------------------------------------

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "$TIMESTAMP OK args=$* exit=0 probe=$PROBE_VERDICT post_prune_deleted=$POST_PRUNE_DELETED" >>"$LOG_FILE" 2>/dev/null
else
    # Single-line stderr snippet (newlines collapsed, capped at 500 chars).
    STDERR_SNIPPET="$(tr '\n' ' ' <"$STDERR_FILE" 2>/dev/null | head -c 500)"
    echo "$TIMESTAMP FAIL args=$* exit=$EXIT_CODE probe=$PROBE_VERDICT rollback=$ROLLBACK_DONE post_prune_deleted=$POST_PRUNE_DELETED stderr=$STDERR_SNIPPET" >>"$LOG_FILE" 2>/dev/null
fi

rm -f "$STDERR_FILE" 2>/dev/null

# Always exit 0 — never block the harness on capture issues.
exit 0
