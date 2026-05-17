#!/bin/bash
#
# Paideia PostToolUse hook for engine_memory MCP tool calls — per-session telemetry.
#
# Per ADR 0091 (engine-memory substrate). Sibling of
# engine/tools/hooks/post-mempalace-tool-use.sh wired in
# .claude/settings.json as a PostToolUse hook matched against
# mcp__engine_memory__.* tool calls.
#
# Captures every engine_memory MCP call to a per-session JSONL log;
# scan_engine_memory_activity.py rolls the JSONL up into the
# engine_memory_activity field on current.json at shutdown step 2;
# validate.py --final-check reads that field to soft-warn (boot query,
# diary read) or hard-fail (diary write, with escape-hatch token
# engine_memory_unavailable_acknowledged) when expected calls are
# absent.
#
# Behavior: parses tool_name from harness's PostToolUse payload (stdin
# JSON); appends one JSONL line to
# engine/session/current_engine_memory.jsonl with shape:
#   {"ts":"<iso>","tool":"<tool_name>","args_summary":"<truncated 200 chars>"}
# Always exits 0; never blocks the harness.
#
# Log paths:
#   - .claude/logs/post-engine-memory-tool-use.log (hook diagnostics)
#   - engine/session/current_engine_memory.jsonl   (per-session telemetry,
#                                                   cleared at boot, rolled up at archive)

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
LOG_FILE="$LOG_DIR/post-engine-memory-tool-use.log"
TELEMETRY_FILE="$REPO_ROOT/engine/session/current_engine_memory.jsonl"
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

TOOL_NAME="$(echo "$PAYLOAD" | jq -r '.tool_name // empty' 2>/dev/null)"
if [ -z "$TOOL_NAME" ]; then
    log_fail "no-tool-name"
    exit 0
fi

case "$TOOL_NAME" in
    mcp__engine_memory__*) ;;
    *)
        log_ok "skip non-engine_memory tool=$TOOL_NAME"
        exit 0
        ;;
esac

ARGS_SUMMARY="$(echo "$PAYLOAD" | jq -c '.tool_input // {}' 2>/dev/null | head -c 200)"

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

exit 0
