"""Pytest config for ``engine/memory/`` — mirrors ``engine/tools/conftest.py``.

The autouse ``_scrub_git_env`` fixture removes ``GIT_*`` env vars from
each test's process. ``engine.memory.connection._resolve_repo_root``
shells out to ``git rev-parse --show-toplevel`` for default path
resolution; without the scrub, tests run inside a pre-commit hook
context could inherit ``GIT_DIR`` / ``GIT_WORK_TREE`` and write to the
wrong repo (the S-0033 vector that ADR 0045 closes).

Cheap insurance even though most tests pass an explicit ``tmp_path /
'test.sqlite3'`` and never exercise the git-rev-parse fallback.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _scrub_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove GIT_* env vars from each test's process."""
    for key in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(key, raising=False)
