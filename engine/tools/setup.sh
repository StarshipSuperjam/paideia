#!/bin/bash
#
# Paideia first-time setup script.
#
# Run once after `git clone` to wire local clone-specific tooling that isn't
# tracked in the repo (git hooks live in .git/hooks/, which is per-clone).
#
# Idempotent: safe to re-run.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# pre-commit hook
# ---------------------------------------------------------------------------

HOOK_SOURCE="$REPO_ROOT/engine/tools/hooks/pre-commit"
HOOK_TARGET="$(git rev-parse --git-path hooks)/pre-commit"

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "[setup] error: engine/tools/hooks/pre-commit not found" >&2
    exit 1
fi

# Make sure the hook source is executable
chmod +x "$HOOK_SOURCE"

# Symlink (force-replace any existing hook)
mkdir -p "$(dirname "$HOOK_TARGET")"
ln -sf "$HOOK_SOURCE" "$HOOK_TARGET"

echo "[setup] pre-commit hook installed → $HOOK_TARGET"

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo "[setup] warning: python3 not on PATH; engine/tools/validate.py will not run" >&2
fi

echo "[setup] done."
