#!/bin/bash
#
# Paideia PostToolUse hook for ADR writes — two-layer recording reminder.
#
# Per ADR 0043 (engine). Wired in .claude/settings.json as a PostToolUse hook
# matched against Edit/Write tool calls touching (engine|product)/adr/*.md.
#
# Posture this mechanizes (per CLAUDE.md "Two-layer decision recording"):
# every settled decision lands in BOTH an ADR (the contract) AND a MemPalace
# `decision`-tagged drawer (the story). The S-0030 audit measured 1 decision
# drawer for 42 ADRs — discipline carried in name only. This hook surfaces
# the gap at authoring time.
#
# Behavior: parses the ADR file path from the harness's tool-call payload
# (read from stdin as JSON), extracts the ADR id and title, queries the
# MemPalace daemon for a `decision`-tagged drawer matching the title slug
# or ADR id, and emits a stderr reminder when no match is found. Always
# exits 0; the reminder is informational, not blocking.
#
# Failure modes:
#   - jq absent → log fail line, exit 0 (no reminder; reminder defers).
#   - mempalace daemon down → log fail line, exit 0 (no false-positive
#     reminder when MemPalace is unreachable).
#   - tool payload malformed → log fail line, exit 0.
#   - All other failures → log, exit 0.
#
# Log path: .claude/logs/post-adr-write.log (gitignored under .claude/*).

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
LOG_FILE="$LOG_DIR/post-adr-write.log"
mkdir -p "$LOG_DIR" 2>/dev/null

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log_fail() {
    echo "$TIMESTAMP FAIL reason=$1" >>"$LOG_FILE" 2>/dev/null
}

log_ok() {
    echo "$TIMESTAMP OK $1" >>"$LOG_FILE" 2>/dev/null
}

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

# Extract the file path from the tool call. The harness's PostToolUse payload
# names the path under tool_input.file_path for both Edit and Write.
FILE_PATH="$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
if [ -z "$FILE_PATH" ]; then
    log_fail "no-file-path"
    exit 0
fi

# Make the path relative to the repo root for the regex match. The harness
# passes absolute paths typically.
REL_PATH="${FILE_PATH#$REPO_ROOT/}"

# Filter: only ADR files under engine/adr/ or product/adr/ matching the
# NNNN-kebab-title.md naming convention.
if ! echo "$REL_PATH" | grep -qE '^(engine|product)/adr/[0-9]{4}-[a-z0-9-]+\.md$'; then
    # Not an ADR write; nothing to do.
    log_ok "skip path=$REL_PATH"
    exit 0
fi

# Parse the ADR id (4-digit number) from the filename.
ADR_ID="$(basename "$REL_PATH" | grep -oE '^[0-9]{4}')"
if [ -z "$ADR_ID" ]; then
    log_fail "id-parse path=$REL_PATH"
    exit 0
fi

ADR_BASENAME="$(basename "$REL_PATH")"

# Read the ADR's title from the first H1 line. Best-effort; if the file is
# unreadable (deleted between Edit and hook fire), skip.
ADR_TITLE=""
if [ -f "$FILE_PATH" ]; then
    ADR_TITLE="$(head -5 "$FILE_PATH" 2>/dev/null | grep -m1 -E '^# ADR' | sed -E 's/^# ADR [0-9]+ — //' | head -c 200)"
fi

# ---------------------------------------------------------------------------
# ADR-README index consistency check (per ADR 0099 Fix D / Issue #153).
#
# Every accepted ADR must have a row in its partition's README index per
# ADR 0037. The validator already enforces this as the `adr_index_inconsistent`
# soft-warn at commit time; this hook surfaces the same predicate at *write*
# time so the AI catches the gap in the same authoring cycle.
#
# Predicate: look for either `[NNNN](NNNN-title.md)` or `[ADR NNNN](NNNN-title.md)`
# in the partition's README.md (engine/adr/README.md for engine ADRs,
# product/adr/README.md for product ADRs). Markdown link syntax preserves
# the basename verbatim so the lookup is a simple grep.
#
# Non-blocking exit-0 posture per ADR 0043. Reminder fires only on miss;
# silent on hit.
# ---------------------------------------------------------------------------

# Resolve the partition's README path from the ADR path's prefix.
ADR_PARTITION="$(echo "$REL_PATH" | cut -d'/' -f1)"  # engine or product
INDEX_PATH="$REPO_ROOT/$ADR_PARTITION/adr/README.md"

if [ -f "$INDEX_PATH" ]; then
    # Match either [NNNN](NNNN-title.md) or [ADR NNNN](NNNN-title.md).
    # The fixed-string fragment matches the basename verbatim; the leading
    # bracket-pair regex permits both index conventions across engine + product.
    INDEX_LINE_PATTERN="\[(ADR )?${ADR_ID}\]\(${ADR_BASENAME}\)"
    if ! grep -qE "$INDEX_LINE_PATTERN" "$INDEX_PATH" 2>/dev/null; then
        {
            echo "[adr-index-consistency] ADR $ADR_ID '$ADR_TITLE' written;"
            echo "  no matching index entry found in $ADR_PARTITION/adr/README.md."
            echo "  Add a row to the index table in the same commit per the"
            echo "  'Adding a new ADR' section at the bottom of the README."
            echo "  validate.py's \`adr_index_inconsistent\` soft-warn will fire at"
            echo "  commit time otherwise."
        } >&2
        log_ok "index-reminder-emitted adr=$ADR_ID partition=$ADR_PARTITION"
    else
        log_ok "index-present adr=$ADR_ID partition=$ADR_PARTITION"
    fi
else
    log_fail "index-missing partition=$ADR_PARTITION"
fi

# Query MemPalace via the CLI. The daemon may be down; treat any non-zero
# exit as "could not verify" rather than "drawer absent."
SEARCH_TERMS="ADR $ADR_ID"
if [ -n "$ADR_TITLE" ]; then
    SEARCH_TERMS="$SEARCH_TERMS $ADR_TITLE"
fi

# Resolve mempalace binary. STATE.md notes the user-scope install at
# ~/Library/Python/3.9/bin/. The harness's PATH may not include it; fall
# back to the literal path before giving up.
MEMPALACE_BIN=""
if command -v mempalace >/dev/null 2>&1; then
    MEMPALACE_BIN="mempalace"
elif [ -x "$HOME/Library/Python/3.9/bin/mempalace" ]; then
    MEMPALACE_BIN="$HOME/Library/Python/3.9/bin/mempalace"
fi

if [ -z "$MEMPALACE_BIN" ]; then
    log_fail "mempalace-cli-missing adr=$ADR_ID"
    exit 0
fi

# Run the search; capture output. The CLI flags are --wing and --results
# (not --tag/--limit). Tag filtering is done by grep over the result body
# since the CLI does not expose a --tag flag in its search subcommand.
SEARCH_OUTPUT="$("$MEMPALACE_BIN" search "$SEARCH_TERMS" --wing paideia --results 5 2>/dev/null || true)"
if [ -z "$SEARCH_OUTPUT" ]; then
    log_fail "search-empty-or-failed adr=$ADR_ID"
    exit 0
fi

# Heuristic for "decision drawer for this ADR exists": at least one result
# whose body carries both a `**Tags:**` line containing `decision` AND a
# mention of the ADR id (e.g., "ADR 0043"). The CLI output prints the full
# drawer body so both checks can run via grep.
HAS_TAG_AND_ID=0
if echo "$SEARCH_OUTPUT" | grep -qE '^\s*\*\*Tags:\*\*[^$]*decision' \
   && echo "$SEARCH_OUTPUT" | grep -q "ADR $ADR_ID"; then
    HAS_TAG_AND_ID=1
fi

# Room-targeting check (added at S-0032 per the MemPalace audit plan,
# Improvement B + Cleanup 3). Per engine/operations/mempalace-tagging-conventions.md
# "Room-targeting conventions", ADR companion drawers belong in the
# `decisions` room. Pre-S-0032, the legacy filing pattern placed them in
# `general`. The hook now distinguishes the two cases:
#   - Tag+id match AND a result line names "paideia / decisions": correct, log OK.
#   - Tag+id match AND only "paideia / general" lines present: legacy pattern,
#     emit migration reminder (drawer exists but should move to decisions).
#   - No tag+id match at all: drawer absent, emit existing two-layer reminder.
HAS_DECISIONS_ROOM=0
HAS_GENERAL_ROOM=0
if echo "$SEARCH_OUTPUT" | grep -qE '^\s*\[[0-9]+\][[:space:]]+paideia[[:space:]]*/[[:space:]]*decisions'; then
    HAS_DECISIONS_ROOM=1
fi
if echo "$SEARCH_OUTPUT" | grep -qE '^\s*\[[0-9]+\][[:space:]]+paideia[[:space:]]*/[[:space:]]*general'; then
    HAS_GENERAL_ROOM=1
fi

if [ "$HAS_TAG_AND_ID" = "1" ] && [ "$HAS_DECISIONS_ROOM" = "1" ]; then
    log_ok "drawer-present adr=$ADR_ID room=decisions"
    exit 0
fi

if [ "$HAS_TAG_AND_ID" = "1" ] && [ "$HAS_GENERAL_ROOM" = "1" ]; then
    # Legacy filing pattern: drawer exists but in the wrong room.
    {
        echo "[two-layer-recording / room-targeting] ADR $ADR_ID '$ADR_TITLE' written;"
        echo "  matching \`decision\`-tagged drawer found in MemPalace, but appears"
        echo "  to be filed in the legacy \`general\` room (no result in \`decisions\` room)."
        echo "  Per engine/operations/mempalace-tagging-conventions.md \"Room-targeting"
        echo "  conventions\" (added at S-0032), ADR companions belong in the \`decisions\`"
        echo "  room. Migrate via mempalace_get_drawer (read content) + mempalace_add_drawer"
        echo "  (refile to room=decisions) — and remove or supersede the legacy drawer."
    } >&2
    log_ok "drawer-wrong-room adr=$ADR_ID"
    exit 0
fi

# No matching drawer — emit existing two-layer reminder.
{
    echo "[two-layer-recording] ADR $ADR_ID '$ADR_TITLE' written;"
    echo "  no matching \`decision\`-tagged MemPalace drawer found in wing 'paideia'."
    echo "  Per CLAUDE.md two-layer recording, the conversation that produced this"
    echo "  decision should be filed to MemPalace alongside the ADR."
    echo "  See engine/operations/mempalace-tagging-conventions.md for tag conventions"
    echo "  and the \"Room-targeting conventions\" section for room placement."
} >&2

log_ok "reminder-emitted adr=$ADR_ID"

# Always exit 0 — non-blocking by design.
exit 0
