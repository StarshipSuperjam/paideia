"""Tests for engine/tools/scrub_env.py.

Covers each public function with at least one test per behavior branch.

Test isolation strategy
-----------------------
- ``monkeypatch.setenv`` / ``monkeypatch.delenv`` to set up controlled
  GIT_* state per test. The autouse ``_scrub_git_env`` fixture in
  conftest.py runs first, so each test starts with no GIT_* in its
  process env; tests that need GIT_* set must do so explicitly via
  monkeypatch.

Non-responsibilities
--------------------
- Does not test that subprocess.run honors ``env=`` correctly — that's
  a stdlib invariant, not this module's responsibility.
- Does not exercise the bash-side ``scrub_env.sh`` helper. That's
  covered by integration smoke-tests in the verification suite.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scrub_env import _GIT_ENV_PREFIX, scrub_in_place, scrubbed_env  # noqa: E402


# ---------------------------------------------------------------------------
# scrubbed_env
# ---------------------------------------------------------------------------


def test_scrubbed_env_drops_all_git_prefixed_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every GIT_* key disappears from the returned dict."""
    monkeypatch.setenv("GIT_DIR", "/foo/bar")
    monkeypatch.setenv("GIT_WORK_TREE", "/foo/baz")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "test")
    monkeypatch.setenv("GIT_INDEX_FILE", "/foo/index")

    result = scrubbed_env()

    git_keys = [k for k in result if k.startswith(_GIT_ENV_PREFIX)]
    assert git_keys == []


def test_scrubbed_env_preserves_non_git_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Non-GIT keys present in the source dict survive."""
    monkeypatch.setenv("GIT_DIR", "/foo/bar")
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    monkeypatch.setenv("HOME", "/home/test")
    monkeypatch.setenv("MEMPALACE_BIN", "/usr/local/bin/mempalace")

    result = scrubbed_env()

    assert result["PATH"] == "/usr/bin:/bin"
    assert result["HOME"] == "/home/test"
    assert result["MEMPALACE_BIN"] == "/usr/local/bin/mempalace"


def test_scrubbed_env_does_not_mutate_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Calling scrubbed_env leaves os.environ unchanged."""
    monkeypatch.setenv("GIT_DIR", "/foo/bar")

    _ = scrubbed_env()

    assert os.environ.get("GIT_DIR") == "/foo/bar"


def test_scrubbed_env_accepts_explicit_base() -> None:
    """When ``base`` is provided, it's the source instead of os.environ."""
    base = {"GIT_DIR": "/x", "PATH": "/y", "OTHER": "z"}

    result = scrubbed_env(base=base)

    assert "GIT_DIR" not in result
    assert result["PATH"] == "/y"
    assert result["OTHER"] == "z"


def test_scrubbed_env_does_not_mutate_explicit_base() -> None:
    """The provided ``base`` dict is not modified."""
    base = {"GIT_DIR": "/x", "PATH": "/y"}

    _ = scrubbed_env(base=base)

    assert base == {"GIT_DIR": "/x", "PATH": "/y"}


def test_scrubbed_env_with_no_git_keys_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No GIT_* keys means the function still returns a clean dict."""
    # The autouse conftest fixture already drops GIT_*, so this is the
    # baseline state. Confirm the function doesn't choke on it.
    monkeypatch.setenv("PATH", "/usr/bin")

    result = scrubbed_env()

    assert "PATH" in result
    assert not any(k.startswith(_GIT_ENV_PREFIX) for k in result)


# ---------------------------------------------------------------------------
# scrub_in_place
# ---------------------------------------------------------------------------


def test_scrub_in_place_mutates_caller_dict() -> None:
    """``scrub_in_place`` removes GIT_* keys from the passed dict."""
    env = {"GIT_DIR": "/x", "GIT_WORK_TREE": "/y", "PATH": "/usr/bin"}

    scrub_in_place(env)

    assert "GIT_DIR" not in env
    assert "GIT_WORK_TREE" not in env
    assert env["PATH"] == "/usr/bin"


def test_scrub_in_place_returns_same_dict_for_chaining() -> None:
    """The function returns the same dict object passed in."""
    env: dict[str, str] = {"GIT_DIR": "/x"}

    result = scrub_in_place(env)

    assert result is env


def test_scrub_in_place_with_empty_dict() -> None:
    """Empty input is handled without error."""
    env: dict[str, str] = {}

    result = scrub_in_place(env)

    assert result == {}


def test_scrub_in_place_with_no_git_keys() -> None:
    """A dict without GIT_* keys is unchanged."""
    env = {"PATH": "/x", "HOME": "/y"}

    scrub_in_place(env)

    assert env == {"PATH": "/x", "HOME": "/y"}
