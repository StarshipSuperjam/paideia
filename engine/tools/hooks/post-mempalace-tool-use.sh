#!/bin/bash
#
# Paideia PostToolUse hook for MemPalace MCP tool calls — per-session telemetry.
#
# Per ADR 0056 (engine; this session). Wired in .claude/settings.json as a
# PostToolUse hook matched against mcp__mempalace__.* tool calls.
#
# Posture this mechanizes: build-mode and routine-mode sessions are expected
# to query MemPalace at boot (mempalace_search), read the diary at boot
# (mempalace_diary_read), and write a diary entry at shutdown
# (mempalace_diary_write). Posture-only enforcement slipped silently across
# Phase 5 (12/16 routine sessions skipped diary write per Issue #27). This
# hook captures every MCP call to a per-session JSONL log; validate.py reads
# it at shutdown to soft-warn (boot query, diary read) or hard-fail (diary
# write, with acknowledgement-token escape hatch) when the expected calls
# are absent.
#
# Behavior: parses tool_name from the harness's PostToolUse payload (read
# from stdin as JSON); appends one JSONL line to
# engine/session/current_mempalace.jsonl with shape:
#   {"ts":"<iso>","tool":"<tool_name>","args_summary":"<truncated 200 chars>"}
# Always exits 0; never blocks the harness.
#
# Failure modes:
#   - jq absent → log fail line, exit 0 (telemetry deferred until jq lands).
#   - tool payload malformed → log fail line, exit 0.
#   - file write fails → log fail line, exit 0.
#
# Log paths:
#   - .claude/logs/post-mempalace-tool-use.log (gitignored; hook diagnostics)
#   - engine/session/current_mempalace.jsonl   (gitignored; per-session telemetry,
#                                              cleared at boot, rolled up at archive)

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
LOG_FILE="$LOG_DIR/post-mempalace-tool-use.log"
TELEMETRY_FILE="$REPO_ROOT/engine/session/current_mempalace.jsonl"
mkdir -p "$LOG_DIR" 2>/dev/null
mkdir -p "$(dirname "$TELEMETRY_FILE")" 2>/dev/null

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log_fail() {
    echo "$TIMESTAMP FAIL reason=$1" >>"$LOG_FILE" 2>/dev/null
}

log_ok() {
    echo "$TIMESTAMP OK $1" >>"$LOG_FILE" 2>/dev/null
}

PAYLOAD="$(cat 2>/dev/null || echo '')"
if [ -z "$PAYLOAD" ]; then
    log_fail "empty-stdin"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    log_fail "jq-not-installed"
    exit 0
fi

# Extract tool_name from the PostToolUse payload. The matcher already filtered
# to mcp__mempalace__.*, but we record the specific tool to distinguish
# search / diary_read / diary_write / add_drawer / status / etc.
TOOL_NAME="$(echo "$PAYLOAD" | jq -r '.tool_name // empty' 2>/dev/null)"
if [ -z "$TOOL_NAME" ]; then
    log_fail "no-tool-name"
    exit 0
fi

# Defensive double-check on the matcher — only log MemPalace MCP calls. If a
# misconfigured settings.json routed a non-MemPalace tool here, skip cleanly.
case "$TOOL_NAME" in
    mcp__mempalace__*) ;;
    *)
        log_ok "skip non-mempalace tool=$TOOL_NAME"
        exit 0
        ;;
esac

# Capture a truncated args summary for forensics. Compact JSON; truncated to
# 200 chars to keep the log file small over a long session.
ARGS_SUMMARY="$(echo "$PAYLOAD" | jq -c '.tool_input // {}' 2>/dev/null | head -c 200)"

# Build the JSONL line via jq for proper escaping.
LINE="$(jq -nc \
    --arg ts "$TIMESTAMP" \
    --arg tool "$TOOL_NAME" \
    --arg args "$ARGS_SUMMARY" \
    '{ts: $ts, tool: $tool, args_summary: $args}' 2>/dev/null)"

if [ -z "$LINE" ]; then
    log_fail "jq-build-failed tool=$TOOL_NAME"
    exit 0
fi

if ! echo "$LINE" >>"$TELEMETRY_FILE" 2>/dev/null; then
    log_fail "telemetry-write-failed tool=$TOOL_NAME"
    exit 0
fi

log_ok "logged tool=$TOOL_NAME"

# Always exit 0 — non-blocking by design.
exit 0
