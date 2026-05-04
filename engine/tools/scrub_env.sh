#!/bin/bash
#
# Subprocess environment scrubber + project-venv PATH wiring —
# bash-sourceable helper.
#
# Two responsibilities, both invoked at source time by hook scripts:
#
# 1) `scrub_git_env` (function): unsets every GIT_* variable in the
#    current shell. Hook scripts source this helper and call
#    `scrub_git_env` before any subprocess that touches git or
#    git-aware tools (mempalace, mypy --strict, etc.).
#
# 2) Project-venv PATH prepend (sourcing-time side effect): prepends
#    the project's `.venv/bin/` directory to PATH so that bare
#    `python3`, `ruff`, `mypy`, `pytest`, `mempalace`, etc. resolve
#    to the venv install rather than system Python. Worktree-local
#    `.venv/` takes precedence over the main repo's `.venv/`; if
#    neither exists, no-op (system Python continues to be used).
#
# Per ADR 0045 (subprocess env scrubbing) and ADR 0050 (project
# venv and hook PATH wiring). Mirrors the production-side Python
# helper in engine/tools/scrub_env.py and the pytest autouse fixture
# in engine/tools/conftest.py.
#
# Source-only — never executed directly. Hook scripts must use:
#     source "$REPO_ROOT/engine/tools/scrub_env.sh"
#     scrub_git_env
# The PATH prepend fires automatically at source time; no function
# call is required for it. Idempotent — re-sourcing the file does
# not duplicate PATH entries.
#
# Motivating failures:
#  - S-0033: pytest subprocess wrote core.bare=true to parent
#    .git/config because GIT_DIR / GIT_WORK_TREE leaked from the
#    pre-commit context. `scrub_git_env` stops the leak.
#  - S-0043: system Python 3.9 carried mempalace 3.3.3 with
#    upstream wing-naming and wing-filter bugs (Issues #1, #2),
#    plus chromadb at whatever the user's site-packages happened
#    to hold. `python3 -m {ruff,mypy,pytest}` and probe_palace's
#    `import chromadb` resolved unpredictably across machines.
#    The venv at `.venv/` pins the project's Python stack; this
#    PATH prepend is what makes hook subprocesses see it.

scrub_git_env() {
    local key
    # Use sed to extract just the variable name from `env`'s KEY=value
    # output. Portable across bash 3.2 (macOS /bin/bash) and bash 4+.
    for key in $(env | sed -n 's/^\(GIT_[^=]*\)=.*/\1/p'); do
        unset "$key"
    done
}

# Project-venv PATH prepend (sourcing-time).
#
# Runs once when this file is sourced. Resolves the worktree root
# and the main repo root (same path when not in a worktree), prefers
# a worktree-local .venv/, falls back to the main repo's .venv/.
# Silent no-op when neither exists or when not inside a git repo
# (hook scripts may be invoked from contexts without git, e.g.
# manual debugging — failing to wire is correct behavior there).
__scrub_env_wire_project_venv() {
    local worktree_root main_root candidate

    # Suppress stderr — `git rev-parse` complains when not in a repo;
    # that's a valid case for this helper to no-op silently.
    worktree_root=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
    main_root=$(git rev-parse --git-common-dir 2>/dev/null) || return 0

    # `--git-common-dir` may return a relative path (e.g. ".git").
    # `realpath` normalizes; if `realpath` fails, bail rather than
    # prepending a broken path.
    main_root=$(realpath "$main_root/.." 2>/dev/null) || return 0

    # Worktree-local first, then main fallback.
    for candidate in "$worktree_root/.venv/bin" "$main_root/.venv/bin"; do
        if [[ -d "$candidate" ]]; then
            # Idempotency: skip if the directory is already prepended.
            case ":$PATH:" in
                *":$candidate:"*) ;;
                *) export PATH="$candidate:$PATH" ;;
            esac
            return 0
        fi
    done
}

__scrub_env_wire_project_venv
unset -f __scrub_env_wire_project_venv
