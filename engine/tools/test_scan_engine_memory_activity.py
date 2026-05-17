"""Tests for ``engine.tools.scan_engine_memory_activity`` — ADR 0091 (S-0192).

Sibling of ``test_scan_mempalace_activity.py`` covering the 6-tool
engine_memory MCP surface per ADR 0091 Decision 5.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scan_engine_memory_activity as scan  # type: ignore[import-not-found]  # noqa: E402


# --------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------


def _write_jsonl(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def _write_current(path: Path, payload: dict[str, Any] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    base: dict[str, Any] = {
        "id": "S-0192",
        "started_at": "2026-05-17T00:00:00Z",
        "status": "in_progress",
        "mode": "interactive",
        "working_on": "engine memory cutover",
    }
    if payload:
        base.update(payload)
    path.write_text(json.dumps(base) + "\n")


# --------------------------------------------------------------------
# rollup_jsonl
# --------------------------------------------------------------------


def test_rollup_jsonl_returns_empty_when_file_absent(tmp_path: Path) -> None:
    rollup = scan.rollup_jsonl(tmp_path / "nope.jsonl")
    assert rollup == scan.EMPTY_ROLLUP
    assert rollup["total_calls"] == 0


def test_rollup_jsonl_counts_search_calls(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:01:00Z",
                "tool": "mcp__engine_memory__engine_memory_search",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:02:00Z",
                "tool": "mcp__engine_memory__engine_memory_search",
                "args_summary": "{}",
            },
        ],
    )
    rollup = scan.rollup_jsonl(jsonl)
    assert rollup["search_calls"] == 2
    assert rollup["total_calls"] == 2
    assert rollup["first_call_ts"] == "2026-05-17T00:01:00Z"
    assert rollup["last_call_ts"] == "2026-05-17T00:02:00Z"
    assert rollup["search_first_ts"] == "2026-05-17T00:01:00Z"


def test_rollup_jsonl_counts_all_six_tools(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:00:01Z",
                "tool": "mcp__engine_memory__engine_memory_search",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:00:02Z",
                "tool": "mcp__engine_memory__engine_memory_add_drawer",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:00:03Z",
                "tool": "mcp__engine_memory__engine_memory_get_drawer",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:00:04Z",
                "tool": "mcp__engine_memory__engine_memory_list_drawers",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:00:05Z",
                "tool": "mcp__engine_memory__engine_memory_diary_read",
                "args_summary": "{}",
            },
            {
                "ts": "2026-05-17T00:00:06Z",
                "tool": "mcp__engine_memory__engine_memory_diary_write",
                "args_summary": "{}",
            },
        ],
    )
    rollup = scan.rollup_jsonl(jsonl)
    assert rollup["search_calls"] == 1
    assert rollup["add_drawer_calls"] == 1
    assert rollup["get_drawer_calls"] == 1
    assert rollup["list_drawers_calls"] == 1
    assert rollup["diary_read_calls"] == 1
    assert rollup["diary_write_calls"] == 1
    assert rollup["other_calls"] == 0
    assert rollup["total_calls"] == 6
    assert rollup["diary_read_first_ts"] == "2026-05-17T00:00:05Z"


def test_rollup_jsonl_unknown_tool_goes_to_other_calls(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:00:01Z",
                "tool": "mcp__engine_memory__engine_memory_unmapped_future",
                "args_summary": "{}",
            },
        ],
    )
    rollup = scan.rollup_jsonl(jsonl)
    assert rollup["other_calls"] == 1
    assert rollup["total_calls"] == 1


def test_rollup_jsonl_skips_malformed_lines(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    jsonl.write_text(
        '{"ts":"2026-05-17T00:00:01Z","tool":"mcp__engine_memory__engine_memory_search","args_summary":"{}"}\n'
        "garbage line not json\n"
        '{"ts":"2026-05-17T00:00:02Z","tool":"mcp__engine_memory__engine_memory_diary_write","args_summary":"{}"}\n'
    )
    rollup = scan.rollup_jsonl(jsonl)
    assert rollup["search_calls"] == 1
    assert rollup["diary_write_calls"] == 1
    assert rollup["total_calls"] == 2


def test_rollup_jsonl_handles_empty_file(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    jsonl.write_text("")
    rollup = scan.rollup_jsonl(jsonl)
    assert rollup == scan.EMPTY_ROLLUP


# --------------------------------------------------------------------
# _merge_rollups
# --------------------------------------------------------------------


def test_merge_rollups_sums_counts() -> None:
    existing = {
        "search_calls": 2,
        "diary_write_calls": 1,
        "total_calls": 3,
        "first_call_ts": "2026-05-17T00:00:00Z",
        "last_call_ts": "2026-05-17T00:00:05Z",
        "search_first_ts": "2026-05-17T00:00:00Z",
        "diary_read_first_ts": None,
    }
    new = {
        "search_calls": 3,
        "diary_write_calls": 0,
        "total_calls": 3,
        "first_call_ts": "2026-05-17T00:01:00Z",
        "last_call_ts": "2026-05-17T00:02:00Z",
        "search_first_ts": "2026-05-17T00:01:00Z",
        "diary_read_first_ts": None,
    }
    merged = scan._merge_rollups(existing, new)
    assert merged["search_calls"] == 5
    assert merged["diary_write_calls"] == 1
    assert merged["total_calls"] == 6
    # First-ts keeps the earliest of either side
    assert merged["first_call_ts"] == "2026-05-17T00:00:00Z"
    assert merged["last_call_ts"] == "2026-05-17T00:02:00Z"
    assert merged["search_first_ts"] == "2026-05-17T00:00:00Z"


def test_merge_rollups_handles_null_ts_on_either_side() -> None:
    existing = dict(scan.EMPTY_ROLLUP)
    new = {
        "search_calls": 1,
        "total_calls": 1,
        "first_call_ts": "2026-05-17T00:00:00Z",
        "last_call_ts": "2026-05-17T00:00:00Z",
        "search_first_ts": "2026-05-17T00:00:00Z",
        "diary_read_first_ts": None,
    }
    merged = scan._merge_rollups(existing, new)
    assert merged["first_call_ts"] == "2026-05-17T00:00:00Z"
    assert merged["search_first_ts"] == "2026-05-17T00:00:00Z"


def test_merge_rollups_returns_new_when_existing_not_dict() -> None:
    merged = scan._merge_rollups("not a dict", {"search_calls": 1})
    assert merged == {"search_calls": 1}


# --------------------------------------------------------------------
# write_rollup_to_current
# --------------------------------------------------------------------


def test_write_rollup_to_current_inserts_field(tmp_path: Path) -> None:
    current_path = tmp_path / "engine" / "session" / "current.json"
    _write_current(current_path)
    rollup = {**scan.EMPTY_ROLLUP, "search_calls": 2, "total_calls": 2}
    scan.write_rollup_to_current(current_path, rollup)
    payload = json.loads(current_path.read_text())
    assert payload["engine_memory_activity"]["search_calls"] == 2
    assert payload["engine_memory_activity"]["total_calls"] == 2


def test_write_rollup_to_current_merges_when_field_exists(tmp_path: Path) -> None:
    current_path = tmp_path / "engine" / "session" / "current.json"
    _write_current(
        current_path,
        payload={
            "engine_memory_activity": {
                **scan.EMPTY_ROLLUP,
                "search_calls": 1,
                "total_calls": 1,
            }
        },
    )
    rollup = {**scan.EMPTY_ROLLUP, "diary_write_calls": 1, "total_calls": 1}
    scan.write_rollup_to_current(current_path, rollup)
    payload = json.loads(current_path.read_text())
    assert payload["engine_memory_activity"]["search_calls"] == 1
    assert payload["engine_memory_activity"]["diary_write_calls"] == 1
    assert payload["engine_memory_activity"]["total_calls"] == 2


def test_write_rollup_to_current_raises_when_current_absent(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan.write_rollup_to_current(tmp_path / "absent.json", scan.EMPTY_ROLLUP)


# --------------------------------------------------------------------
# truncate_jsonl
# --------------------------------------------------------------------


def test_truncate_jsonl_clears_existing_file(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_engine_memory.jsonl"
    jsonl.write_text("garbage data\n")
    scan.truncate_jsonl(jsonl)
    assert jsonl.read_text() == ""


def test_truncate_jsonl_no_op_on_absent_file(tmp_path: Path) -> None:
    scan.truncate_jsonl(tmp_path / "absent.jsonl")
    # Should not raise; file remains absent
    assert not (tmp_path / "absent.jsonl").exists()


# --------------------------------------------------------------------
# main / CLI
# --------------------------------------------------------------------


def test_main_writes_to_current_and_truncates_jsonl(tmp_path: Path) -> None:
    jsonl = tmp_path / "engine" / "session" / "current_engine_memory.jsonl"
    current = tmp_path / "engine" / "session" / "current.json"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:00:01Z",
                "tool": "mcp__engine_memory__engine_memory_search",
                "args_summary": "{}",
            },
        ],
    )
    _write_current(current)
    rc = scan.main(["--jsonl", str(jsonl), "--current-path", str(current)])
    assert rc == 0
    assert jsonl.read_text() == ""
    payload = json.loads(current.read_text())
    assert payload["engine_memory_activity"]["search_calls"] == 1


def test_main_dry_run_does_not_write_or_truncate(tmp_path: Path) -> None:
    jsonl = tmp_path / "engine" / "session" / "current_engine_memory.jsonl"
    current = tmp_path / "engine" / "session" / "current.json"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:00:01Z",
                "tool": "mcp__engine_memory__engine_memory_diary_write",
                "args_summary": "{}",
            },
        ],
    )
    _write_current(current)
    original_jsonl = jsonl.read_text()
    rc = scan.main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(current),
            "--dry-run",
        ]
    )
    assert rc == 0
    # JSONL preserved
    assert jsonl.read_text() == original_jsonl
    # current.json unchanged (no engine_memory_activity field added)
    payload = json.loads(current.read_text())
    assert "engine_memory_activity" not in payload


def test_main_zero_exit_when_current_json_absent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    jsonl = tmp_path / "engine" / "session" / "current_engine_memory.jsonl"
    _write_jsonl(
        jsonl,
        [
            {
                "ts": "2026-05-17T00:00:01Z",
                "tool": "mcp__engine_memory__engine_memory_search",
                "args_summary": "{}",
            },
        ],
    )
    rc = scan.main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(tmp_path / "absent_current.json"),
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert "cannot write rollup" in captured.err
