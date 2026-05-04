"""Tests for engine/tools/load_env.py.

Use ``tmp_path`` + ``monkeypatch.chdir`` to exercise walk-up behavior
without touching the real filesystem above the test root. Each test
that mutates ``os.environ`` cleans up via ``monkeypatch.delenv`` so
state cannot leak across tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import (  # noqa: E402
    WALK_UP_DEPTH_CAP,
    find_dotenv,
    load_dotenv,
    load_dotenv_walk_up,
)


# ---------------------------------------------------------------------------
# find_dotenv
# ---------------------------------------------------------------------------


def test_find_dotenv_returns_at_start(tmp_path: Path) -> None:
    """`.env` exists at the start path -> return it immediately."""
    (tmp_path / ".env").write_text("X=1\n")
    assert find_dotenv(start=tmp_path) == tmp_path / ".env"


def test_find_dotenv_walks_up_through_nested_dirs(tmp_path: Path) -> None:
    """Walks up through several ancestor levels until `.env` is found."""
    (tmp_path / ".env").write_text("X=1\n")
    deep = tmp_path / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    assert find_dotenv(start=deep) == tmp_path / ".env"


def test_find_dotenv_prefers_nearest(tmp_path: Path) -> None:
    """When two `.env` files exist on the walk path, the nearest wins."""
    (tmp_path / ".env").write_text("X=outer\n")
    middle = tmp_path / "inner"
    middle.mkdir()
    (middle / ".env").write_text("X=inner\n")
    deep = middle / "deeper"
    deep.mkdir()
    assert find_dotenv(start=deep) == middle / ".env"


def test_find_dotenv_returns_none_when_absent(tmp_path: Path) -> None:
    """No `.env` reachable -> returns None (no exception)."""
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    # Important: walk up from `deep` will eventually hit / which DOES
    # NOT have a .env in any sane test environment. The depth cap fires
    # before that happens. Either way: return None.
    assert find_dotenv(start=deep) is None


def test_find_dotenv_respects_depth_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Build a path deeper than WALK_UP_DEPTH_CAP and confirm cap fires.

    The `.env` lives above the cap so a healthy walk-up from deep would
    find it; with the cap, find_dotenv returns None.
    """
    (tmp_path / ".env").write_text("X=1\n")
    cur = tmp_path
    for i in range(WALK_UP_DEPTH_CAP + 5):
        cur = cur / f"d{i}"
    cur.mkdir(parents=True)
    assert find_dotenv(start=cur) is None


def test_find_dotenv_default_start_is_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Default start is `Path.cwd()`."""
    (tmp_path / ".env").write_text("X=1\n")
    monkeypatch.chdir(tmp_path)
    assert find_dotenv() == tmp_path / ".env"


# ---------------------------------------------------------------------------
# load_dotenv
# ---------------------------------------------------------------------------


def test_load_dotenv_sets_missing_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env = tmp_path / ".env"
    env.write_text("FOO=fooval\nBAR=barval\n")
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAR", raising=False)
    applied = load_dotenv(env)
    assert applied == {"FOO": "fooval", "BAR": "barval"}
    assert os.environ["FOO"] == "fooval"
    assert os.environ["BAR"] == "barval"
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAR", raising=False)


def test_load_dotenv_skips_already_set_when_override_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pre-set value wins; explicit `KEY=value python3 ...` invocations stick."""
    env = tmp_path / ".env"
    env.write_text("FOO=from_env_file\n")
    monkeypatch.setenv("FOO", "from_shell")
    applied = load_dotenv(env)
    assert applied == {}
    assert os.environ["FOO"] == "from_shell"


def test_load_dotenv_overrides_when_flag_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env = tmp_path / ".env"
    env.write_text("FOO=from_env_file\n")
    monkeypatch.setenv("FOO", "from_shell")
    applied = load_dotenv(env, override=True)
    assert applied == {"FOO": "from_env_file"}
    assert os.environ["FOO"] == "from_env_file"


def test_load_dotenv_skips_empty_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`.env.example`-style files have many empty placeholders; skip them."""
    env = tmp_path / ".env"
    env.write_text("POPULATED=value\nEMPTY=\n")
    monkeypatch.delenv("POPULATED", raising=False)
    monkeypatch.delenv("EMPTY", raising=False)
    applied = load_dotenv(env)
    assert applied == {"POPULATED": "value"}
    assert "EMPTY" not in os.environ
    monkeypatch.delenv("POPULATED", raising=False)


def test_load_dotenv_ignores_comments_and_blank_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env = tmp_path / ".env"
    env.write_text("# top comment\n\nFOO=fooval\n# inline comment\nBAR=barval\n")
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAR", raising=False)
    applied = load_dotenv(env)
    assert applied == {"FOO": "fooval", "BAR": "barval"}
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAR", raising=False)


# ---------------------------------------------------------------------------
# load_dotenv_walk_up
# ---------------------------------------------------------------------------


def test_load_dotenv_walk_up_no_env_returns_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No `.env` reachable -> empty dict, no exception."""
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    assert load_dotenv_walk_up() == {}


def test_load_dotenv_walk_up_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Calling twice produces the same env state; second call is a no-op."""
    (tmp_path / ".env").write_text("FOO=fooval\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FOO", raising=False)
    first = load_dotenv_walk_up()
    second = load_dotenv_walk_up()
    assert first == {"FOO": "fooval"}
    assert second == {}  # already set on first call; no-op
    assert os.environ["FOO"] == "fooval"
    monkeypatch.delenv("FOO", raising=False)


def test_load_dotenv_walk_up_finds_main_repo_env_from_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mirror the worktree-launched scenario: `.env` lives several
    ancestors up; CWD is in a subdirectory mimicking
    `.claude/worktrees/<branch>/`. Walk-up reaches it."""
    (tmp_path / ".env").write_text("SUPABASE_DB_URL=postgresql://test\n")
    worktree_branch = tmp_path / ".claude" / "worktrees" / "test-branch"
    worktree_branch.mkdir(parents=True)
    monkeypatch.chdir(worktree_branch)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    applied = load_dotenv_walk_up()
    assert applied == {"SUPABASE_DB_URL": "postgresql://test"}
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
