"""Tests for engine/memory/verify_recall.py.

Coverage:
- harness PASS verdict against the canonical seed corpus
- per-query expectations (specific tag/room targets fire correctly)
- report-file emission shape
- CLI: --no-write prints to stdout; --output-md writes to file
- boundary case (empty-result query returns 0 hits without erroring)
- formulation distinctness check
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.memory import verify_recall
from engine.memory.connection import get_conn


# ---------------------------------------------------------------------------
# Harness end-to-end
# ---------------------------------------------------------------------------


def test_run_harness_returns_aggregate_pass_against_seeded_corpus(
    tmp_path: Path,
) -> None:
    db = tmp_path / "verify.sqlite3"
    aggregate, results = verify_recall.run_harness(db)
    # All 10 queries are expected to PASS the mechanical checks.
    failures = [r for r in results if r.verdict == "FAIL"]
    assert aggregate in ("PASS", "PARTIAL"), (
        f"unexpected aggregate {aggregate}; failures: "
        + "\n".join(f"{r.spec.name}: {r.reason}" for r in failures)
    )
    assert len(results) == len(verify_recall.QUERY_CATALOG)


def test_run_harness_aggregate_is_pass_when_all_queries_pass(tmp_path: Path) -> None:
    """At least the canonical seed corpus should drive all 10 to PASS — the
    fixtures are engineered specifically to satisfy the expectations."""
    db = tmp_path / "verify.sqlite3"
    aggregate, _ = verify_recall.run_harness(db)
    assert aggregate == "PASS"


# ---------------------------------------------------------------------------
# Per-query specs
# ---------------------------------------------------------------------------


def test_decision_query_finds_decision_room_top1(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    _, results = verify_recall.run_harness(db)
    decision_results = [
        r for r in results if r.spec.category == "Decision-drawer recall"
    ]
    assert decision_results
    for r in decision_results:
        if r.top_drawer is not None:
            assert r.top_drawer["room"] == "decisions"
            assert "decision" in r.top_drawer.get("tags", [])


def test_pushback_query_finds_pushback_room_top1(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    _, results = verify_recall.run_harness(db)
    pushback_results = [r for r in results if r.spec.category == "ADR-pushback recall"]
    for r in pushback_results:
        if r.top_drawer is not None:
            assert r.top_drawer["room"] == "pushback"


def test_lesson_query_finds_lessons_room_top1(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    _, results = verify_recall.run_harness(db)
    lesson_results = [r for r in results if r.spec.category == "Lesson recall"]
    for r in lesson_results:
        if r.top_drawer is not None:
            assert r.top_drawer["room"] == "lessons"


def test_boundary_no_hits_query_returns_zero_literal_candidates(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    _, results = verify_recall.run_harness(db)
    boundary = next(r for r in results if r.spec.name == "boundary_no_hits")
    # Literal + conceptual produce zero hits (no drawer contains the
    # nonsense token). Adjacent matches lessons/pushback-tagged drawers
    # because the adjacent formulation OR-injects those tokens — that's
    # expected behavior, not a boundary violation.
    assert boundary.formulation_hits["literal"] == 0
    assert boundary.formulation_hits["conceptual"] == 0
    assert boundary.verdict == "PASS"


def test_formulation_distinctness_check(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    _, results = verify_recall.run_harness(db)
    distinct = next(r for r in results if r.spec.name == "formulation_distinctness")
    # All three formulations must yield distinct FTS5 MATCH expressions.
    assert len(set(distinct.formulation_matches.values())) == 3
    assert distinct.verdict == "PASS"


# ---------------------------------------------------------------------------
# Seed integrity
# ---------------------------------------------------------------------------


def test_seed_substrate_inserts_all_drawers(tmp_path: Path) -> None:
    db = tmp_path / "seed.sqlite3"
    conn = get_conn(db)
    try:
        verify_recall.seed_substrate(conn)
        count = conn.execute("SELECT count(*) FROM drawers").fetchone()[0]
    finally:
        conn.close()
    assert count == len(verify_recall.SEED_CORPUS)


def test_seed_corpus_covers_all_curated_rooms(tmp_path: Path) -> None:
    rooms = {d.room for d in verify_recall.SEED_CORPUS}
    expected = {
        "decisions",
        "pushback",
        "lessons",
        "exploration",
        "operations",
        "general",
    }
    assert expected.issubset(rooms), f"missing rooms: {expected - rooms}"


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def test_render_report_contains_verdict_and_query_table(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    aggregate, results = verify_recall.run_harness(db)
    report = verify_recall.render_report(aggregate, results, "2026-05-16T20:00:00Z")
    assert f"**Verdict:** {aggregate}" in report
    assert "## Per-query results" in report
    assert "## Cutover-gate handoff" in report
    # All 10 query names should appear in the table
    for spec in verify_recall.QUERY_CATALOG:
        # Either by category or by query text snippet
        assert spec.category in report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_main_no_write_prints_report_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = tmp_path / "verify.sqlite3"
    rc = verify_recall.main(["--db-path", str(db), "--no-write"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "# Engine-memory recall verification — S-0191" in out
    assert "**Verdict:**" in out


def test_main_writes_to_output_md(tmp_path: Path) -> None:
    db = tmp_path / "verify.sqlite3"
    output = tmp_path / "report.md"
    rc = verify_recall.main(["--db-path", str(db), "--output-md", str(output)])
    assert rc == 0
    assert output.is_file()
    body = output.read_text()
    assert "# Engine-memory recall verification — S-0191" in body


def test_main_with_no_db_path_uses_tempfile(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """When --db-path is omitted, a tempfile is created and cleaned up."""
    output = tmp_path / "report.md"
    rc = verify_recall.main(["--output-md", str(output)])
    assert rc == 0
    assert output.is_file()
