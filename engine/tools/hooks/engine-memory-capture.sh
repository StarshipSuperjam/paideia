#!/bin/bash
#
# Engine-memory transcript capture hook.
#
# Per ADR 0091, this hook captures conversation transcripts into the
# engine_memory SQLite substrate's room='work', preserving the
# auto-capture affordance that mempalace previously delivered.
# Parallel-write per ADR 0078 — runs alongside mempalace-hook-wrapper.sh
# during the S-0190 → S-0192 cutover window; mempalace path retires at
# S-0193.
#
# Wired in .claude/settings.json as a second entry in the Stop and
# PreCompact hook arrays.
#
# Invocation: engine-memory-capture.sh {stop|precompact}
# Stdin: harness JSON event payload (transcript_path, session_id,
#        stop_hook_active) — pass-through to python -m engine.memory.capture.
#
# Always exits 0 — capture failures log to
# .claude/logs/engine-memory-hook.log and do NOT block the harness.
#
# Log path is per-worktree (parity with mempalace-hook-wrapper.sh; per
# Issue #136 the cross-worktree log fragmentation will be addressed at
# the substrate level once the cutover settles).
#
# ---------------------------------------------------------------------------
# Resolve repo root + scrub GIT_* env (per ADR 0045/0050)
# ---------------------------------------------------------------------------

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
LOG_FILE="$LOG_DIR/engine-memory-hook.log"
mkdir -p "$LOG_DIR" 2>/dev/null

HOOK_KIND="${1:-stop}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ---------------------------------------------------------------------------
# Resolve python; invoke the capture entrypoint
# ---------------------------------------------------------------------------

# The scrub_env.sh PATH-prepend should put the venv's python ahead of
# the system python (per ADR 0050). Fall back to bare python3 if it's
# missing — system python is acceptable for the simple stdlib-only
# capture path.
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "$TIMESTAMP FAIL reason=python_not_found hook_kind=$HOOK_KIND" \
        >> "$LOG_FILE" 2>/dev/null
    exit 0
fi

cd "$REPO_ROOT" || { echo "$TIMESTAMP FAIL reason=cwd_failed hook_kind=$HOOK_KIND" \
    >> "$LOG_FILE" 2>/dev/null; exit 0; }

# Capture stderr for the failure log; stdin flows through untouched.
STDERR_FILE="$(mktemp 2>/dev/null || echo "/tmp/engine-memory-hook-stderr.$$")"
"$PYTHON_BIN" -m engine.memory.capture "$HOOK_KIND" 2>"$STDERR_FILE"
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "$TIMESTAMP OK hook_kind=$HOOK_KIND exit=0" >> "$LOG_FILE" 2>/dev/null
else
    STDERR_SNIPPET="$(tr '\n' ' ' <"$STDERR_FILE" 2>/dev/null | head -c 500)"
    echo "$TIMESTAMP FAIL hook_kind=$HOOK_KIND exit=$EXIT_CODE stderr=$STDERR_SNIPPET" \
        >> "$LOG_FILE" 2>/dev/null
fi

rm -f "$STDERR_FILE" 2>/dev/null

# Always exit 0 — capture is best-effort; never block the harness.
exit 0
