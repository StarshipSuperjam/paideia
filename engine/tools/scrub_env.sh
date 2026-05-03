#!/bin/bash
#
# Subprocess environment scrubber — bash-sourceable helper.
#
# Defines `scrub_git_env`: a function that unsets every GIT_* variable
# in the current shell. Hook scripts source this helper and call
# `scrub_git_env` before any subprocess that touches git or git-aware
# tools (mempalace, mypy --strict, etc.).
#
# Per ADR 0045 (engine). Mirrors the production-side Python helper in
# engine/tools/scrub_env.py and the pytest autouse fixture in
# engine/tools/conftest.py.
#
# Source-only — never executed directly. Hook scripts must use:
#     source "$REPO_ROOT/engine/tools/scrub_env.sh"
#     scrub_git_env
#
# Motivating failure: S-0033 wrote core.bare=true to the parent
# .git/config from inside a pytest subprocess invoked by the pre-commit
# hook. Root cause: GIT_DIR / GIT_WORK_TREE leaked from the pre-commit
# context into test subprocesses. This helper stops the leak vector for
# bash-side hook subprocess calls; the Python helper covers
# Python-side; the conftest fixture covers pytest-side.

scrub_git_env() {
    local key
    # Use sed to extract just the variable name from `env`'s KEY=value
    # output. Portable across bash 3.2 (macOS /bin/bash) and bash 4+.
    for key in $(env | sed -n 's/^\(GIT_[^=]*\)=.*/\1/p'); do
        unset "$key"
    done
}
