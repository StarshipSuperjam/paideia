"""Tests for engine/tools/setup_env.py.

Cover the parsing + write helpers + the determine_blocks orchestrator.
The SUPABASE_DB_URL validator is exercised manually during live setup —
not unit-tested here because mocking psycopg meaningfully would buy
little (the validator's only logic is the prefix check + delegate-to-
psycopg pattern).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setup_env import (  # noqa: E402
    determine_blocks,
    parse_env,
    parse_env_example,
    write_env_atomic,
)


# ---------------------------------------------------------------------------
# parse_env_example
# ---------------------------------------------------------------------------


def test_parse_env_example_simple() -> None:
    text = "# comment 1\nKEY1=\n\n# comment 2\nKEY2=\n"
    blocks = parse_env_example(text)
    assert [k for k, _ in blocks] == ["KEY1", "KEY2"]
    assert blocks[0][1] == ["# comment 1"]
    assert blocks[1][1] == ["", "# comment 2"]


def test_parse_env_example_no_comments() -> None:
    blocks = parse_env_example("KEY=\n")
    assert blocks == [("KEY", [])]


def test_parse_env_example_multiline_comment_block() -> None:
    text = "# line a\n# line b\n# line c\nKEY=\n"
    blocks = parse_env_example(text)
    assert blocks[0][1] == ["# line a", "# line b", "# line c"]


# ---------------------------------------------------------------------------
# parse_env
# ---------------------------------------------------------------------------


def test_parse_env_basic() -> None:
    text = "K1=v1\n# comment\nK2=v2\n"
    assert parse_env(text) == {"K1": "v1", "K2": "v2"}


def test_parse_env_strips_whitespace() -> None:
    text = "K1 = v1 \n  K2=v2\n"
    assert parse_env(text) == {"K1": "v1", "K2": "v2"}


def test_parse_env_value_can_contain_equals() -> None:
    text = "URL=postgresql://user:pw@host/db?x=1\n"
    parsed = parse_env(text)
    assert parsed["URL"] == "postgresql://user:pw@host/db?x=1"


def test_parse_env_ignores_blank_and_comment_lines() -> None:
    text = "\n# comment\n\nK=v\n"
    assert parse_env(text) == {"K": "v"}


def test_parse_env_ignores_lines_without_equals() -> None:
    text = "garbage\nK=v\n"
    assert parse_env(text) == {"K": "v"}


# ---------------------------------------------------------------------------
# write_env_atomic
# ---------------------------------------------------------------------------


def test_write_env_atomic_round_trip(tmp_path: Path) -> None:
    target = tmp_path / ".env"
    blocks = [
        ("K1", ["# c1"], "v1"),
        ("K2", [], "v2"),
    ]
    write_env_atomic(target, blocks)
    assert target.read_text() == "# c1\nK1=v1\nK2=v2\n"
    parsed = parse_env(target.read_text())
    assert parsed == {"K1": "v1", "K2": "v2"}


def test_write_env_atomic_sets_0600_permission(tmp_path: Path) -> None:
    target = tmp_path / ".env"
    write_env_atomic(target, [("K", [], "v")])
    mode = target.stat().st_mode & 0o777
    assert mode == 0o600


def test_write_env_atomic_overwrites_existing(tmp_path: Path) -> None:
    target = tmp_path / ".env"
    target.write_text("K=old\n")
    write_env_atomic(target, [("K", [], "new")])
    assert parse_env(target.read_text())["K"] == "new"


# ---------------------------------------------------------------------------
# determine_blocks
# ---------------------------------------------------------------------------


def test_determine_blocks_all_populated_no_prompt() -> None:
    example = [("K1", ["# c1"]), ("K2", [])]
    existing = {"K1": "v1", "K2": "v2"}

    def fail_prompt(_key: str, _comments: list[str]) -> str:
        raise AssertionError("should not prompt when all keys populated")

    blocks, prompted = determine_blocks(example, existing, prompt_fn=fail_prompt)
    assert prompted is False
    assert blocks == [("K1", ["# c1"], "v1"), ("K2", [], "v2")]


def test_determine_blocks_missing_key_prompts() -> None:
    example = [("K1", []), ("K2", ["# guidance"])]
    existing = {"K1": "v1"}
    prompt_calls: list[tuple[str, list[str]]] = []

    def stub_prompt(key: str, comments: list[str]) -> str:
        prompt_calls.append((key, comments))
        return "user-pasted-value"

    blocks, prompted = determine_blocks(example, existing, prompt_fn=stub_prompt)
    assert prompted is True
    assert prompt_calls == [("K2", ["# guidance"])]
    assert blocks == [
        ("K1", [], "v1"),
        ("K2", ["# guidance"], "user-pasted-value"),
    ]


def test_determine_blocks_empty_existing_value_prompts() -> None:
    """A key present in .env but with empty value counts as missing."""
    example: list[tuple[str, list[str]]] = [("K1", [])]
    existing = {"K1": ""}

    def stub_prompt(_key: str, _comments: list[str]) -> str:
        return "newvalue"

    blocks, prompted = determine_blocks(example, existing, prompt_fn=stub_prompt)
    assert prompted is True
    assert blocks == [("K1", [], "newvalue")]


def test_determine_blocks_skipped_value_stays_empty() -> None:
    """If the user skips (returns empty from prompt), the key stays empty."""
    example: list[tuple[str, list[str]]] = [("K1", [])]
    existing: dict[str, str] = {}

    def stub_prompt(_key: str, _comments: list[str]) -> str:
        return ""

    blocks, prompted = determine_blocks(example, existing, prompt_fn=stub_prompt)
    assert prompted is True
    assert blocks == [("K1", [], "")]
