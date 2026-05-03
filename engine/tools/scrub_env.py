"""Subprocess environment scrubber.

Removes ``GIT_*`` variables from an env dict so child processes cannot
inherit a parent's git context. Per ADR 0045 (engine), this is the
production-side counterpart to the ``_scrub_git_env`` autouse fixture
hoisted into ``engine/tools/conftest.py``.

Motivating failure
------------------
S-0033 wrote ``core.bare=true`` to the parent ``.git/config`` from
inside a pytest subprocess invoked by the pre-commit hook. Root cause:
``GIT_DIR`` / ``GIT_WORK_TREE`` leaked from the pre-commit context into
test subprocesses, which then ran ``git config`` against the wrong
repository. The autouse fixture stops that vector for tests; this
helper stops it for any production subprocess that shells out (the
ruff/mypy/pytest gates in :mod:`validate`, the post-state-edit hook's
``git rev-parse``, etc.).

Usage
-----

    >>> from scrub_env import scrubbed_env
    >>> import subprocess
    >>> proc = subprocess.run(
    ...     ["git", "status"],
    ...     env=scrubbed_env(),
    ...     capture_output=True, text=True, check=True,
    ... )

Pass ``base`` only if you need to start from something other than the
current process environment (rarely).
"""

from __future__ import annotations

import os

# Variable-name prefix that identifies a leaked git-context variable.
# Includes GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_AUTHOR_*,
# GIT_COMMITTER_*, GIT_CONFIG, GIT_OBJECT_DIRECTORY, etc. — every
# documented git env var starts with this prefix.
_GIT_ENV_PREFIX = "GIT_"


def scrubbed_env(base: dict[str, str] | None = None) -> dict[str, str]:
    """Return a copy of ``base`` (or ``os.environ``) with GIT_* keys removed.

    Parameters
    ----------
    base
        Source dict. ``None`` (the default) snapshots ``os.environ``.

    Returns
    -------
    A new dict; the source is not mutated.
    """
    source = dict(os.environ if base is None else base)
    return {k: v for k, v in source.items() if not k.startswith(_GIT_ENV_PREFIX)}


def scrub_in_place(env: dict[str, str]) -> dict[str, str]:
    """Mutate ``env`` to remove every GIT_* key; return ``env`` for chaining.

    Used when the caller already holds an env dict it wants to alter
    (e.g., a copy.deepcopy of os.environ that's about to be augmented
    with caller-specific overrides). Prefer :func:`scrubbed_env` for the
    common case.
    """
    for k in [k for k in env if k.startswith(_GIT_ENV_PREFIX)]:
        del env[k]
    return env
