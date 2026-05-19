#!/bin/bash
#
# Paideia PostToolUse hook for per-session changelog entry writes —
# summary-length catch-early reminder.
#
# Per ADR 0099 Fix D (Issue #153) + ADR 0043 (hook architecture). Wired in
# .claude/settings.json as a PostToolUse hook matched against Edit/Write tool
# calls touching engine/changelog/<YYYY>/S-NNNN-*.md.
#
# Posture this mechanizes: the per-session changelog entry schema (per ADR
# 0092) caps the `summary:` frontmatter field at 200 chars. validate.py's
# `changelog_entry_schema_violation` hard-fail enforces this at commit time.
# Issue #153 quantified the friction: a too-long summary discovered at the
# close commit triggers the same recovery-required-via-classifier-blocked-
# operations cascade as other late-discovered hard-fails. This hook surfaces
# the same predicate at WRITE time so the AI catches the limit in the same
# authoring cycle.
#
# Behavior: reads the post-edit file; parses YAML frontmatter; extracts
# `summary:`; emits stderr reminder if length > 200 chars. Always exits 0;
# the reminder is informational, not blocking per ADR 0043.
#
# Failure modes:
#   - tool payload malformed → log fail, exit 0.
#   - changelog file unreadable post-edit → log fail, exit 0.
#   - frontmatter missing → log fail, exit 0 (validator catches at commit).
#   - All other failures → log, exit 0.
#
# Log path: .claude/logs/post-changelog-write.log (gitignored under .claude/*).

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
LOG_FILE="$LOG_DIR/post-changelog-write.log"
mkdir -p "$LOG_DIR" 2>/dev/null

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log_fail() {
    echo "$TIMESTAMP FAIL reason=$1" >>"$LOG_FILE" 2>/dev/null
}

log_ok() {
    echo "$TIMESTAMP OK $1" >>"$LOG_FILE" 2>/dev/null
}

# Per ADR 0092 the summary cap is 200 chars. Update both if the schema changes.
SUMMARY_LIMIT=200

# Read the harness's tool-call payload from stdin.
PAYLOAD="$(cat 2>/dev/null || echo '')"
if [ -z "$PAYLOAD" ]; then
    log_fail "empty-stdin"
    exit 0
fi

# Need jq to parse the JSON payload. If absent, log and exit; the reminder
# will defer until jq is installed.
if ! command -v jq >/dev/null 2>&1; then
    log_fail "jq-not-installed"
    exit 0
fi

# Extract the file path from the tool call. PostToolUse payload names it
# under tool_input.file_path for both Edit and Write.
FILE_PATH="$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
if [ -z "$FILE_PATH" ]; then
    log_fail "no-file-path"
    exit 0
fi

REL_PATH="${FILE_PATH#$REPO_ROOT/}"

# Filter: only per-session changelog entry files under engine/changelog/<YYYY>/
# matching the S-NNNN-<topic>.md naming convention per ADR 0092.
if ! echo "$REL_PATH" | grep -qE '^engine/changelog/[0-9]{4}/S-[0-9]{4}-[a-z0-9-]+\.md$'; then
    log_ok "skip path=$REL_PATH"
    exit 0
fi

if [ ! -f "$FILE_PATH" ]; then
    log_fail "file-absent path=$REL_PATH"
    exit 0
fi

# Parse YAML frontmatter between the first two `---` lines. Extract `summary:`
# value (single-line scalar; ADR 0092 implies single-line shape).
# Use awk to locate the frontmatter block, then grep+sed for the summary line.
FRONTMATTER="$(awk '
    /^---$/ { count++; if (count == 1) next; if (count == 2) exit }
    count == 1 { print }
' "$FILE_PATH" 2>/dev/null)"

if [ -z "$FRONTMATTER" ]; then
    log_fail "frontmatter-empty path=$REL_PATH"
    exit 0
fi

SUMMARY_VALUE="$(echo "$FRONTMATTER" | grep -m1 -E '^summary:' | sed -E 's/^summary:[[:space:]]*//' | sed -E 's/^"(.*)"$/\1/' | sed -E "s/^'(.*)'\$/\1/")"

if [ -z "$SUMMARY_VALUE" ]; then
    log_ok "summary-absent path=$REL_PATH"
    exit 0
fi

SUMMARY_LEN=${#SUMMARY_VALUE}
SESSION_ID="$(basename "$REL_PATH" | grep -oE '^S-[0-9]{4}')"

if [ "$SUMMARY_LEN" -gt "$SUMMARY_LIMIT" ]; then
    OVER=$((SUMMARY_LEN - SUMMARY_LIMIT))
    {
        echo "[changelog-entry-schema] $SESSION_ID entry's 'summary:' field is $SUMMARY_LEN chars"
        echo "  (over the $SUMMARY_LIMIT-char cap by $OVER chars; per ADR 0092)."
        echo "  validate.py's \`changelog_entry_schema_violation\` hard-fail will fire"
        echo "  at commit time. Trim now while the session is still in_progress."
    } >&2
    log_ok "summary-over-cap session=$SESSION_ID length=$SUMMARY_LEN limit=$SUMMARY_LIMIT"
else
    log_ok "summary-within-cap session=$SESSION_ID length=$SUMMARY_LEN limit=$SUMMARY_LIMIT"
fi

# Always exit 0 — non-blocking by design.
exit 0
