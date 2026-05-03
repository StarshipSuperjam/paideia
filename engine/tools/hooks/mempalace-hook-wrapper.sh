#!/bin/bash
#
# Paideia MemPalace capture-hook wrapper.
#
# Wraps `mempalace hook run` so capture failures (binary missing, daemon down,
# capture errored) surface to a session-visible log instead of failing silently.
# Always exits 0 to the harness regardless of mempalace's actual exit code —
# the log carries the truth. The next session's boot procedure reads the log
# and surfaces unacknowledged failure entries.
#
# Wired in .claude/settings.json as the Stop and PreCompact hook command.
# Pass-through args: --hook <stop|precompact> --harness <name>.
# Pass-through stdin: the harness's JSON event payload.
#
# Log path: .claude/logs/mempalace-hook.log (gitignored under .claude/* — the
# log is per-clone state, not project state).

# Resolve repo root. Prefer git's view; fall back to the wrapper's own location
# (the script lives at <repo>/engine/tools/hooks/mempalace-hook-wrapper.sh
# post-S-0024 partition migration per ADR 0037).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
    REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." 2>/dev/null && pwd)"
fi

LOG_DIR="$REPO_ROOT/.claude/logs"
LOG_FILE="$LOG_DIR/mempalace-hook.log"

# Best-effort log-dir creation. Failures here are themselves silent — the
# alternative (failing the harness) is worse.
mkdir -p "$LOG_DIR" 2>/dev/null

# Capture stderr to a temp file so the failure log line can include a snippet.
STDERR_FILE="$(mktemp 2>/dev/null || echo "/tmp/mempalace-hook-stderr.$$")"

# Resolve mempalace binary. STATE.md notes the user-scope install at
# ~/Library/Python/3.9/bin/. The harness's PATH may not include it; fall
# back to the literal user-scope path before giving up. Mirrors the
# resolution pattern in post-adr-write.sh per ADR 0043. Without this
# fallback the wrapper writes FAIL exit=127 on every Stop / PreCompact
# event when invoked from a Claude Code subshell — the actual cause of
# the silent auto-capture breakage diagnosed at S-0032.
MEMPALACE_BIN=""
if command -v mempalace >/dev/null 2>&1; then
    MEMPALACE_BIN="mempalace"
elif [ -x "$HOME/Library/Python/3.9/bin/mempalace" ]; then
    MEMPALACE_BIN="$HOME/Library/Python/3.9/bin/mempalace"
fi

# Invoke the real hook. Pass through stdin and all args. Manual sentinel for
# the manual-failure test: if PAIDEIA_MEMPALACE_HOOK_FORCE_FAIL=1, skip the
# real binary and synthesize a failure — used during S-0020 verification per
# the approved plan, never set in production.
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

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "$TIMESTAMP OK args=$* exit=0" >>"$LOG_FILE" 2>/dev/null
else
    # Single-line stderr snippet (newlines collapsed, capped at 500 chars).
    STDERR_SNIPPET="$(tr '\n' ' ' <"$STDERR_FILE" 2>/dev/null | head -c 500)"
    echo "$TIMESTAMP FAIL args=$* exit=$EXIT_CODE stderr=$STDERR_SNIPPET" >>"$LOG_FILE" 2>/dev/null
fi

rm -f "$STDERR_FILE" 2>/dev/null

# Always exit 0 — never block the harness on capture issues.
exit 0
