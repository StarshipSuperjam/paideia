"""Tests for engine/tools/scan_mempalace_activity.py — S-0078 / ADR 0056."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_mempalace_activity import (  # noqa: E402
    EMPTY_ROLLUP,
    main,
    rollup_jsonl,
    truncate_jsonl,
    write_rollup_to_current,
)


def write_jsonl(path: Path, lines: list[dict[str, str]]) -> None:
    path.write_text("\n".join(json.dumps(line) for line in lines) + "\n")


def test_rollup_jsonl_absent_returns_empty(tmp_path: Path) -> None:
    rollup = rollup_jsonl(tmp_path / "missing.jsonl")
    assert rollup == EMPTY_ROLLUP


def test_rollup_counts_per_tool(tmp_path: Path) -> None:
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [
            {"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"},
            {"ts": "2026-05-06T03:01:00Z", "tool": "mcp__mempalace__mempalace_search"},
            {
                "ts": "2026-05-06T03:02:00Z",
                "tool": "mcp__mempalace__mempalace_diary_read",
            },
            {
                "ts": "2026-05-06T03:03:00Z",
                "tool": "mcp__mempalace__mempalace_diary_write",
            },
            {
                "ts": "2026-05-06T03:04:00Z",
                "tool": "mcp__mempalace__mempalace_add_drawer",
            },
            {"ts": "2026-05-06T03:05:00Z", "tool": "mcp__mempalace__mempalace_status"},
            {
                "ts": "2026-05-06T03:06:00Z",
                "tool": "mcp__mempalace__mempalace_list_drawers",
            },
        ],
    )
    rollup = rollup_jsonl(p)
    assert rollup["search_calls"] == 2
    assert rollup["diary_read_calls"] == 1
    assert rollup["diary_write_calls"] == 1
    assert rollup["add_drawer_calls"] == 1
    assert rollup["status_calls"] == 1
    assert rollup["list_drawers_calls"] == 1
    assert rollup["other_calls"] == 0
    assert rollup["total_calls"] == 7
    assert rollup["first_call_ts"] == "2026-05-06T03:00:00Z"
    assert rollup["last_call_ts"] == "2026-05-06T03:06:00Z"


def test_rollup_unknown_tool_falls_into_other(tmp_path: Path) -> None:
    """A truly unknown mempalace tool name (not in TOOL_KEY_MAP) lands in other_calls."""
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [
            {
                "ts": "2026-05-06T03:00:00Z",
                "tool": "mcp__mempalace__mempalace_invented_future_tool",
            },
        ],
    )
    rollup = rollup_jsonl(p)
    assert rollup["other_calls"] == 1
    assert rollup["total_calls"] == 1


def test_rollup_kg_tools_count_into_kg_calls(tmp_path: Path) -> None:
    """All five KG-family tools roll into the kg_calls bucket — S-0087 / ADR 0056 amendment.

    Tracking KG and tunnel invocations in named buckets (rather than other_calls) is
    the foundation for validate.py's mempalace_retired_surface_used soft-warn.
    """
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [
            {
                "ts": "2026-05-07T03:00:00Z",
                "tool": "mcp__mempalace__mempalace_kg_query",
            },
            {"ts": "2026-05-07T03:01:00Z", "tool": "mcp__mempalace__mempalace_kg_add"},
            {
                "ts": "2026-05-07T03:02:00Z",
                "tool": "mcp__mempalace__mempalace_kg_invalidate",
            },
            {
                "ts": "2026-05-07T03:03:00Z",
                "tool": "mcp__mempalace__mempalace_kg_stats",
            },
            {
                "ts": "2026-05-07T03:04:00Z",
                "tool": "mcp__mempalace__mempalace_kg_timeline",
            },
        ],
    )
    rollup = rollup_jsonl(p)
    assert rollup["kg_calls"] == 5
    assert rollup["tunnel_calls"] == 0
    assert rollup["other_calls"] == 0
    assert rollup["total_calls"] == 5


def test_rollup_tunnel_tools_count_into_tunnel_calls(tmp_path: Path) -> None:
    """All five tunnel-family tools roll into the tunnel_calls bucket."""
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [
            {
                "ts": "2026-05-07T03:00:00Z",
                "tool": "mcp__mempalace__mempalace_find_tunnels",
            },
            {
                "ts": "2026-05-07T03:01:00Z",
                "tool": "mcp__mempalace__mempalace_list_tunnels",
            },
            {
                "ts": "2026-05-07T03:02:00Z",
                "tool": "mcp__mempalace__mempalace_create_tunnel",
            },
            {
                "ts": "2026-05-07T03:03:00Z",
                "tool": "mcp__mempalace__mempalace_delete_tunnel",
            },
            {
                "ts": "2026-05-07T03:04:00Z",
                "tool": "mcp__mempalace__mempalace_traverse",
            },
        ],
    )
    rollup = rollup_jsonl(p)
    assert rollup["kg_calls"] == 0
    assert rollup["tunnel_calls"] == 5
    assert rollup["other_calls"] == 0
    assert rollup["total_calls"] == 5


def test_rollup_kg_and_tunnel_mixed(tmp_path: Path) -> None:
    """KG and tunnel calls mixed with normal calls — each lands in its own bucket."""
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [
            {"ts": "2026-05-07T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"},
            {
                "ts": "2026-05-07T03:01:00Z",
                "tool": "mcp__mempalace__mempalace_kg_query",
            },
            {
                "ts": "2026-05-07T03:02:00Z",
                "tool": "mcp__mempalace__mempalace_traverse",
            },
        ],
    )
    rollup = rollup_jsonl(p)
    assert rollup["search_calls"] == 1
    assert rollup["kg_calls"] == 1
    assert rollup["tunnel_calls"] == 1
    assert rollup["other_calls"] == 0
    assert rollup["total_calls"] == 3


def test_rollup_skips_malformed_lines(tmp_path: Path) -> None:
    """A partial / corrupt JSONL line is skipped, not fatal."""
    p = tmp_path / "current_mempalace.jsonl"
    p.write_text(
        '{"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"}\n'
        "{ not valid json\n"
        '{"ts": "2026-05-06T03:01:00Z", "tool": "mcp__mempalace__mempalace_search"}\n'
        "\n"  # blank line tolerated
    )
    rollup = rollup_jsonl(p)
    assert rollup["search_calls"] == 2
    assert rollup["total_calls"] == 2


def test_rollup_handles_missing_ts(tmp_path: Path) -> None:
    """A line without a ts field still counts toward call totals."""
    p = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        p,
        [{"tool": "mcp__mempalace__mempalace_search"}],
    )
    rollup = rollup_jsonl(p)
    assert rollup["search_calls"] == 1
    assert rollup["first_call_ts"] is None
    assert rollup["last_call_ts"] is None


def test_rollup_handles_non_dict_line(tmp_path: Path) -> None:
    """A JSON list or scalar line is skipped (not a valid telemetry entry)."""
    p = tmp_path / "current_mempalace.jsonl"
    p.write_text("[1, 2, 3]\n42\n")
    rollup = rollup_jsonl(p)
    assert rollup == EMPTY_ROLLUP


def test_write_rollup_to_current(tmp_path: Path) -> None:
    """End-to-end: rollup gets written into current.json's mempalace_activity."""
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078", "mode": "interactive"}))

    rollup = dict(EMPTY_ROLLUP)
    rollup["search_calls"] = 3
    rollup["total_calls"] = 3
    write_rollup_to_current(current, rollup)

    data = json.loads(current.read_text())
    assert data["id"] == "S-0078"
    assert data["mode"] == "interactive"
    assert data["mempalace_activity"]["search_calls"] == 3
    assert data["mempalace_activity"]["total_calls"] == 3


def test_write_rollup_merges_with_existing(tmp_path: Path) -> None:
    """Re-running merges with the prior rollup, summing counts (S-0089 fix).

    Pre-S-0089 contract was REPLACE: each scan invocation overwrote the
    prior `mempalace_activity` field. Combined with the post-rollup JSONL
    truncation (Issue #37 / S-0083), running the scan more than once in
    a session LOST earlier counts. S-0089 changes the contract to MERGE:
    counts sum, timestamps span. The function is still safe to invoke
    once-per-session (the scan-once-at-shutdown discipline is unchanged);
    the merge contract just makes accidental re-runs non-destructive.
    """
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": {
                    "search_calls": 2,
                    "diary_read_calls": 1,
                    "diary_write_calls": 0,
                    "total_calls": 3,
                    "first_call_ts": "2026-05-06T01:00:00Z",
                    "last_call_ts": "2026-05-06T01:30:00Z",
                },
            }
        )
    )

    fresh = dict(EMPTY_ROLLUP)
    fresh["diary_write_calls"] = 1
    fresh["search_calls"] = 1
    fresh["total_calls"] = 2
    fresh["first_call_ts"] = "2026-05-06T02:00:00Z"
    fresh["last_call_ts"] = "2026-05-06T02:15:00Z"
    write_rollup_to_current(current, fresh)

    data = json.loads(current.read_text())
    # Counts sum across the merge.
    assert data["mempalace_activity"]["search_calls"] == 3
    assert data["mempalace_activity"]["diary_read_calls"] == 1
    assert data["mempalace_activity"]["diary_write_calls"] == 1
    assert data["mempalace_activity"]["total_calls"] == 5
    # Timestamps span the merge: earliest first, latest last.
    assert data["mempalace_activity"]["first_call_ts"] == "2026-05-06T01:00:00Z"
    assert data["mempalace_activity"]["last_call_ts"] == "2026-05-06T02:15:00Z"


def test_write_rollup_with_no_existing_field_writes_fresh(tmp_path: Path) -> None:
    """First scan against current.json with no mempalace_activity writes the rollup directly."""
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078", "mode": "interactive"}))

    rollup = dict(EMPTY_ROLLUP)
    rollup["search_calls"] = 5
    rollup["total_calls"] = 5
    write_rollup_to_current(current, rollup)

    data = json.loads(current.read_text())
    assert data["mempalace_activity"]["search_calls"] == 5
    assert data["mempalace_activity"]["total_calls"] == 5


def test_write_rollup_handles_null_timestamps(tmp_path: Path) -> None:
    """Merging with all-null timestamps preserves the non-null side."""
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": dict(EMPTY_ROLLUP),  # all None timestamps
            }
        )
    )

    fresh = dict(EMPTY_ROLLUP)
    fresh["search_calls"] = 1
    fresh["total_calls"] = 1
    fresh["first_call_ts"] = "2026-05-07T10:00:00Z"
    fresh["last_call_ts"] = "2026-05-07T10:00:00Z"
    write_rollup_to_current(current, fresh)

    data = json.loads(current.read_text())
    assert data["mempalace_activity"]["first_call_ts"] == "2026-05-07T10:00:00Z"
    assert data["mempalace_activity"]["last_call_ts"] == "2026-05-07T10:00:00Z"
    assert data["mempalace_activity"]["search_calls"] == 1


def test_write_rollup_missing_current_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        write_rollup_to_current(tmp_path / "no-such.json", dict(EMPTY_ROLLUP))


def test_main_dry_run_no_write(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        jsonl,
        [{"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"}],
    )
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078"}))

    rc = main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
            "--dry-run",
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    assert "mempalace_activity" not in data


def test_main_writes_rollup(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        jsonl,
        [
            {"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"},
            {
                "ts": "2026-05-06T03:01:00Z",
                "tool": "mcp__mempalace__mempalace_diary_write",
            },
        ],
    )
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078"}))

    rc = main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    assert data["mempalace_activity"]["search_calls"] == 1
    assert data["mempalace_activity"]["diary_write_calls"] == 1
    assert data["mempalace_activity"]["total_calls"] == 2
    # Per Issue #37 — JSONL truncated after successful write
    assert jsonl.read_text() == ""


def test_truncate_jsonl_clears_file(tmp_path: Path) -> None:
    """truncate_jsonl empties an existing JSONL file in place."""
    jsonl = tmp_path / "current_mempalace.jsonl"
    jsonl.write_text(
        '{"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"}\n'
    )
    truncate_jsonl(jsonl)
    assert jsonl.is_file()
    assert jsonl.read_text() == ""


def test_truncate_jsonl_absent_is_noop(tmp_path: Path) -> None:
    """truncate_jsonl on an absent path does nothing and does not raise."""
    jsonl = tmp_path / "missing.jsonl"
    truncate_jsonl(jsonl)
    assert not jsonl.exists()


def test_main_does_not_truncate_when_current_missing(tmp_path: Path) -> None:
    """If current.json is absent (write fails), JSONL is preserved for recovery."""
    jsonl = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        jsonl,
        [
            {"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"},
        ],
    )
    rc = main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(tmp_path / "no-current.json"),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    # JSONL must be intact — the rollup never landed in current.json
    assert jsonl.read_text() != ""


def test_main_dry_run_does_not_truncate(tmp_path: Path) -> None:
    """Dry-run skips both write AND truncate."""
    jsonl = tmp_path / "current_mempalace.jsonl"
    write_jsonl(
        jsonl,
        [
            {"ts": "2026-05-06T03:00:00Z", "tool": "mcp__mempalace__mempalace_search"},
        ],
    )
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078"}))

    original_jsonl = jsonl.read_text()
    rc = main(
        [
            "--jsonl",
            str(jsonl),
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
            "--dry-run",
        ]
    )
    assert rc == 0
    assert jsonl.read_text() == original_jsonl  # untouched


def test_main_handles_absent_jsonl(tmp_path: Path) -> None:
    """No telemetry → write empty rollup, exit 0."""
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0078"}))

    rc = main(
        [
            "--jsonl",
            str(tmp_path / "missing.jsonl"),
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    assert data["mempalace_activity"]["total_calls"] == 0
    assert data["mempalace_activity"]["first_call_ts"] is None


def test_main_handles_absent_current(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No current.json → exit 0 with stderr message; no crash."""
    rc = main(
        [
            "--jsonl",
            str(tmp_path / "missing.jsonl"),
            "--current-path",
            str(tmp_path / "no-current.json"),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    err = capsys.readouterr().err
    assert "cannot write rollup" in err
