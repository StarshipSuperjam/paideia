"""Pytest config — autouse fixtures applied to every test in this directory.

Hoisted from ``test_audit_side_discoveries.py`` per ADR 0045 (engine) so
the GIT_* env scrub applies to every test in the engine/tools/ suite,
not just the side-discovery audit tests. Without this hoist, any new
test file that subprocesses git could silently inherit GIT_* from a
parent pre-commit invocation and write to the parent's .git/config —
the S-0033 vector.

The :func:`_scrub_git_env` fixture remains in
``test_audit_side_discoveries.py`` as well so removing this conftest
does not silently regress that file's protection. Both fixtures are
no-ops when GIT_* is not set; running both has no side effect.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _scrub_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove GIT_* env vars from each test's process.

    Necessary so test subprocesses do not inherit GIT_DIR /
    GIT_WORK_TREE / GIT_INDEX_FILE from a parent invocation
    (e.g., when pytest runs inside a pre-commit hook), which would
    point git operations at the parent repo instead of the per-test
    tmp_path repo.
    """
    for key in list(os.environ.keys()):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)
