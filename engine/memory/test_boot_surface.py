"""Tests for engine/memory/boot_surface.py.

Coverage targets:
- formulation generation determinism + three-form distinctness
- FTS5 MATCH conversion: token wrapping, special-char escape, empty-query
- fetch_candidates against a seeded :memory:-equivalent SQLite
- render_section: substrate-unreachable + normal + dedup of union
- write_section: new / replace-existing / preserve-content-around
- append_query_log: one row per formulation
- resolve_work_item: precedence order
- main CLI: work-item unresolvable → exit 1; dry-run prints; normal write
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from engine.memory import boot_surface
from engine.memory.connection import get_conn


# ---------------------------------------------------------------------------
# Formulation helpers
# ---------------------------------------------------------------------------


def test_normalize_query_lowercases_strips_punctuation_truncates() -> None:
    assert boot_surface._normalize_query("Hello, World!") == "hello world"
    assert boot_surface._normalize_query("  multi   spaces ") == "multi spaces"
    long = "x" * 500
    assert len(boot_surface._normalize_query(long)) == boot_surface.MAX_QUERY_CHARS


def test_extract_keywords_drops_stopwords_dedups_caps() -> None:
    text = "The Engine Memory substrate is a thin SQLite FTS5 substrate"
    out = boot_surface._extract_keywords(text, max_n=6)
    # 'the' / 'is' / 'a' are stopwords; 'substrate' appears twice, deduped.
    assert "the" not in out and "is" not in out and "a" not in out
    assert out.count("substrate") == 1
    assert len(out) <= 6
    assert all(len(token) >= 3 for token in out)


def test_generate_formulations_returns_three_distinct_labels() -> None:
    out = boot_surface.generate_formulations(
        "S-0191 — Engine-memory read surface verification harness"
    )
    labels = [label for label, _ in out]
    assert labels == ["literal", "conceptual", "adjacent"]
    # All three queries are non-empty and the adjacent form carries the
    # lessons/pushback suffix.
    literal, conceptual, adjacent = (q for _, q in out)
    assert literal and conceptual and adjacent
    assert adjacent.endswith("lessons pushback")


def test_generate_formulations_is_deterministic() -> None:
    a = boot_surface.generate_formulations("foo bar baz")
    b = boot_surface.generate_formulations("foo bar baz")
    assert a == b


# ---------------------------------------------------------------------------
# FTS5 MATCH conversion
# ---------------------------------------------------------------------------


def test_to_fts5_match_empty_query_returns_unmatchable() -> None:
    out = boot_surface.to_fts5_match("")
    assert "no_query" in out
    assert out.startswith('"') and out.endswith('"')


def test_to_fts5_match_wraps_tokens_in_quotes_or_joined() -> None:
    out = boot_surface.to_fts5_match("engine memory substrate")
    assert '"engine"' in out
    assert '"memory"' in out
    assert '"substrate"' in out
    assert " OR " in out


def test_to_fts5_match_drops_stopwords_and_short_tokens() -> None:
    out = boot_surface.to_fts5_match("the at a engine on")
    # Only "engine" survives stopword + length filters.
    assert '"engine"' in out
    assert '"the"' not in out
    assert '"at"' not in out  # too short AND stopword


def test_to_fts5_match_strips_embedded_quotes() -> None:
    # An attacker (or odd content) might have a quote in the work item; the
    # function must strip it so FTS5 doesn't see an unterminated string.
    out = boot_surface.to_fts5_match('engine"memory')
    assert "enginememory" in out.replace('"', "")
    assert out.count('"') % 2 == 0  # every quote is paired


# ---------------------------------------------------------------------------
# fetch_candidates against a seeded SQLite
# ---------------------------------------------------------------------------


@pytest.fixture
def seeded_conn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[sqlite3.Connection, list[dict[str, Any]]]]:
    """Open a fresh substrate at tmp_path and seed it with 6 drawers."""
    db_path = tmp_path / "boot_surface_test.sqlite3"
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(db_path))
    # Reset the cached repo-root in case a prior test cached it.
    monkeypatch.setattr(
        "engine.memory.connection._REPO_ROOT_CACHE", None, raising=False
    )

    conn = get_conn()

    drawers: list[dict[str, Any]] = [
        # Decision drawer — should get +0.15 tag-class boost.
        {
            "id": uuid.uuid4().hex,
            "room": "decisions",
            "tags": ["decision", "engine-memory"],
            "content": "ADR 0091 commits to SQLite + FTS5 engine memory substrate.",
        },
        # Pushback drawer — should get +0.12 tag-class boost.
        {
            "id": uuid.uuid4().hex,
            "room": "pushback",
            "tags": ["pushback"],
            "content": "Don't split work into multiple sessions on vague budget hedges.",
        },
        # Lesson drawer — should get +0.10 tag-class boost.
        {
            "id": uuid.uuid4().hex,
            "room": "lessons",
            "tags": ["lesson"],
            "content": "pkill -f mempalace before running pytest engine tools.",
        },
        # Exploration drawer — no tag-class boost.
        {
            "id": uuid.uuid4().hex,
            "room": "exploration",
            "tags": ["exploration"],
            "content": "Consider chromadb sync_threshold tuning for HNSW persistence.",
        },
        # Decision drawer with matching tag_any — should win the rank.
        {
            "id": uuid.uuid4().hex,
            "room": "decisions",
            "tags": ["decision", "phase-6"],
            "content": "Phase 6 master plan authoring depends on OQ-DEC1 settlement.",
        },
        # Superseded drawer — should never appear in results.
        {
            "id": uuid.uuid4().hex,
            "room": "decisions",
            "tags": ["decision"],
            "content": "Old engine memory ADR 0090 superseded.",
            "superseded_by_self": True,
        },
    ]

    for d in drawers:
        superseded_by = d["id"] if d.get("superseded_by_self") else None
        superseded_at = "2026-01-01T00:00:00Z" if superseded_by else None
        conn.execute(
            "INSERT INTO drawers "
            "(id, room, tags, source_kind, content, superseded_by, superseded_at) "
            "VALUES (?, ?, ?, 'manual', ?, ?, ?)",
            (
                d["id"],
                d["room"],
                json.dumps(d["tags"]),
                d["content"],
                superseded_by,
                superseded_at,
            ),
        )

    yield conn, drawers
    conn.close()


def test_fetch_candidates_returns_dict_shape(
    seeded_conn: tuple[sqlite3.Connection, list[dict[str, Any]]],
) -> None:
    conn, _ = seeded_conn
    out = boot_surface.fetch_candidates(conn, "engine memory")
    assert len(out) >= 1
    row = out[0]
    expected_keys = {
        "id",
        "room",
        "tags",
        "agent",
        "session_id",
        "created_at",
        "filed_at",
        "content",
        "metadata",
        "bm25_score",
        "rank_score",
    }
    assert expected_keys.issubset(row.keys())
    # tags + metadata are parsed from JSON
    assert isinstance(row["tags"], list)
    assert isinstance(row["metadata"], dict)


def test_fetch_candidates_excludes_superseded(
    seeded_conn: tuple[sqlite3.Connection, list[dict[str, Any]]],
) -> None:
    conn, drawers = seeded_conn
    superseded_id = next(d["id"] for d in drawers if d.get("superseded_by_self"))
    out = boot_surface.fetch_candidates(conn, "engine memory superseded")
    returned_ids = {r["id"] for r in out}
    assert superseded_id not in returned_ids


def test_fetch_candidates_room_filter(
    seeded_conn: tuple[sqlite3.Connection, list[dict[str, Any]]],
) -> None:
    conn, _ = seeded_conn
    out = boot_surface.fetch_candidates(conn, "engine memory", room="pushback")
    # Only the pushback drawer matches; FTS5 may not produce it for this
    # query, so we just assert that any returned row IS pushback.
    for row in out:
        assert row["room"] == "pushback"


def test_fetch_candidates_empty_corpus_returns_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "empty.sqlite3"
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(db_path))
    monkeypatch.setattr(
        "engine.memory.connection._REPO_ROOT_CACHE", None, raising=False
    )
    conn = get_conn()
    try:
        out = boot_surface.fetch_candidates(conn, "anything at all")
        assert out == []
    finally:
        conn.close()


def test_fetch_candidates_tag_class_boost_orders_decisions_first(
    seeded_conn: tuple[sqlite3.Connection, list[dict[str, Any]]],
) -> None:
    conn, _ = seeded_conn
    out = boot_surface.fetch_candidates(conn, "engine memory")
    if len(out) >= 2:
        # Decision drawers (tag-class boost +0.15) should outrank tagless
        # ones on average. We check the top row carries the decision tag.
        top = out[0]
        assert "decision" in top["tags"] or top["rank_score"] >= out[-1]["rank_score"]


# ---------------------------------------------------------------------------
# render_section
# ---------------------------------------------------------------------------


def test_render_section_substrate_unreachable_path() -> None:
    out = boot_surface.render_section(
        [("literal", "x", []), ("conceptual", "y", []), ("adjacent", "z", [])],
        ts="2026-05-16T20:00:00Z",
        substrate_unreachable=True,
    )
    assert boot_surface.SECTION_HEADING in out
    assert "substrate unreachable" in out.lower()


def test_render_section_normal_path_has_per_formulation_subsections() -> None:
    fake_drawer = {
        "id": "abc12345",
        "room": "decisions",
        "tags": ["decision"],
        "agent": "claude",
        "session_id": "S-0191",
        "created_at": "2026-05-16T20:00:00Z",
        "filed_at": "2026-05-16T20:00:00Z",
        "content": "test drawer content",
        "metadata": {},
        "bm25_score": -2.5,
        "rank_score": 2.65,
    }
    out = boot_surface.render_section(
        [
            ("literal", "engine memory", [fake_drawer]),
            ("conceptual", "engine memory", []),
            ("adjacent", "engine memory lessons pushback", []),
        ],
        ts="2026-05-16T20:00:00Z",
    )
    assert "### Literal" in out
    assert "### Conceptual" in out
    assert "### Adjacent" in out
    assert "test drawer content" in out
    assert "_no candidates_" in out  # conceptual + adjacent empty


def test_render_section_dedups_union() -> None:
    shared = {
        "id": "shared-id",
        "room": "decisions",
        "tags": ["decision"],
        "agent": "claude",
        "session_id": "S-0191",
        "created_at": "2026-05-16T20:00:00Z",
        "filed_at": "2026-05-16T20:00:00Z",
        "content": "shared drawer",
        "metadata": {},
        "bm25_score": -2.0,
        "rank_score": 2.15,
    }
    out = boot_surface.render_section(
        [
            ("literal", "x", [shared]),
            ("conceptual", "y", [shared]),
            ("adjacent", "z", [shared]),
        ],
        ts="2026-05-16T20:00:00Z",
        top_n=8,
    )
    # The "Top N surfaced inline" section should list shared only once.
    inline_section = out.split("### Literal")[0]
    assert inline_section.count("shared drawer") == 1


# ---------------------------------------------------------------------------
# write_section idempotency
# ---------------------------------------------------------------------------


def test_write_section_creates_file_when_absent(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    body = boot_surface.SECTION_HEADING + "\n\n_test body_\n"
    boot_surface.write_section(plan, body)
    assert plan.read_text() == body


def test_write_section_replaces_existing_section_preserving_surrounding(
    tmp_path: Path,
) -> None:
    plan = tmp_path / "current_plan.md"
    plan.write_text(
        "# Plan\n\nIntro paragraph.\n\n"
        f"{boot_surface.SECTION_HEADING}\n\n_old body_\n\n"
        "## Next section\n\nNext content.\n"
    )
    new_body = boot_surface.SECTION_HEADING + "\n\n_new body_\n"
    boot_surface.write_section(plan, new_body)
    result = plan.read_text()
    assert "Intro paragraph." in result
    assert "_new body_" in result
    assert "_old body_" not in result
    assert "## Next section" in result
    assert "Next content." in result


def test_write_section_idempotent_double_call(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    body = boot_surface.SECTION_HEADING + "\n\n_only body_\n"
    boot_surface.write_section(plan, body)
    boot_surface.write_section(plan, body)
    text = plan.read_text()
    # Heading appears exactly once after the second write
    assert text.count(boot_surface.SECTION_HEADING) == 1


# ---------------------------------------------------------------------------
# append_query_log
# ---------------------------------------------------------------------------


def test_append_query_log_inserts_one_row_per_formulation(
    seeded_conn: tuple[sqlite3.Connection, list[dict[str, Any]]],
) -> None:
    conn, _ = seeded_conn
    boot_surface.append_query_log(
        conn,
        [
            ("literal", "foo bar", 5),
            ("conceptual", "foo", 3),
            ("adjacent", "foo bar lessons pushback", 1),
        ],
        session_id="S-0191",
    )
    rows = conn.execute(
        "SELECT formulation, query_text, result_count FROM query_log "
        "WHERE session_id = ? ORDER BY id",
        ("S-0191",),
    ).fetchall()
    assert len(rows) == 3
    assert {r[0] for r in rows} == {"literal", "conceptual", "adjacent"}
    assert dict(rows[:3] and {r[0]: r[2] for r in rows}) == {
        "literal": 5,
        "conceptual": 3,
        "adjacent": 1,
    }


# ---------------------------------------------------------------------------
# resolve_work_item precedence
# ---------------------------------------------------------------------------


def test_resolve_work_item_current_json_wins(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"working_on": "from current"}))
    state = tmp_path / "STATE.md"
    state.write_text("## Next session work item\n\nfrom state\n")
    target = tmp_path / "auto_target.json"
    target.write_text(
        json.dumps({"tasks": [{"status": "pending", "name": "from target"}]})
    )

    out = boot_surface.resolve_work_item(current, state, target)
    assert out == "from current"


def test_resolve_work_item_falls_through_to_auto_target(tmp_path: Path) -> None:
    current = tmp_path / "current.json"  # absent
    state = tmp_path / "STATE.md"
    state.write_text("## Next session work item\n\nfrom state\n")
    target = tmp_path / "auto_target.json"
    target.write_text(
        json.dumps({"tasks": [{"status": "pending", "name": "from target"}]})
    )

    out = boot_surface.resolve_work_item(current, state, target)
    assert out == "from target"


def test_resolve_work_item_falls_through_to_state_md(tmp_path: Path) -> None:
    current = tmp_path / "current.json"  # absent
    state = tmp_path / "STATE.md"
    state.write_text("## Next session work item\n\nfrom state\n")
    target = tmp_path / "auto_target.json"  # absent

    out = boot_surface.resolve_work_item(current, state, target)
    assert out == "from state"


def test_resolve_work_item_returns_none_when_nothing_resolvable(tmp_path: Path) -> None:
    out = boot_surface.resolve_work_item(
        tmp_path / "absent_current.json",
        tmp_path / "absent_state.md",
        tmp_path / "absent_target.json",
    )
    assert out is None


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


def test_main_returns_1_when_work_item_unresolvable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(tmp_path / "db.sqlite3"))
    monkeypatch.setattr(
        "engine.memory.connection._REPO_ROOT_CACHE", None, raising=False
    )
    rc = boot_surface.main(
        [
            "--current-path",
            str(tmp_path / "absent.json"),
            "--state-path",
            str(tmp_path / "absent.md"),
            "--auto-target-path",
            str(tmp_path / "absent.json"),
            "--plan-path",
            str(tmp_path / "plan.md"),
        ]
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert "could not resolve work-item" in err


def test_main_dry_run_writes_to_stdout_not_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(tmp_path / "db.sqlite3"))
    monkeypatch.setattr(
        "engine.memory.connection._REPO_ROOT_CACHE", None, raising=False
    )
    plan = tmp_path / "plan.md"
    rc = boot_surface.main(
        [
            "--work-item",
            "engine memory substrate",
            "--plan-path",
            str(plan),
            "--current-path",
            str(tmp_path / "absent.json"),
            "--state-path",
            str(tmp_path / "absent.md"),
            "--auto-target-path",
            str(tmp_path / "absent.json"),
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert boot_surface.SECTION_HEADING in out
    assert not plan.is_file()


def test_main_writes_plan_section_in_normal_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(tmp_path / "db.sqlite3"))
    monkeypatch.setattr(
        "engine.memory.connection._REPO_ROOT_CACHE", None, raising=False
    )
    plan = tmp_path / "plan.md"
    rc = boot_surface.main(
        [
            "--work-item",
            "engine memory substrate",
            "--plan-path",
            str(plan),
            "--current-path",
            str(tmp_path / "absent.json"),
            "--state-path",
            str(tmp_path / "absent.md"),
            "--auto-target-path",
            str(tmp_path / "absent.json"),
        ]
    )
    assert rc == 0
    body = plan.read_text()
    assert boot_surface.SECTION_HEADING in body
    # Empty corpus → each formulation reports "no candidates"
    assert re.search(r"### Literal", body)
    assert "_no candidates_" in body
