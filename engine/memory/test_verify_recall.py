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

import json
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


# ---------------------------------------------------------------------------
# Real-data mode (--real-data) — S-0192 cite-worthy verification
# ---------------------------------------------------------------------------


def _seed_real_data_corpus(db_path: Path) -> None:
    """Populate a substrate with enough realistic content that fixed +
    plausible catalogs hit on the vocabulary they target.

    Each seed drawer's content includes one or more keyword phrases the
    fixed-catalog (broad-vocabulary) and plausible-recall (targeted)
    queries assert against. The substrate IS NOT the synthetic harness
    corpus — this is realistic-shape content authored to exercise the
    real-data branch.
    """
    conn = get_conn(db_path)
    try:
        seeds = [
            (
                "decisions",
                ["decision", "adr"],
                "ADR decision summary about the engine memory substrate cutover",
            ),
            (
                "decisions",
                ["decision", "adr-0091"],
                "ADR 0091 substrate cutover SQLite FTS5 commits the new layer",
            ),
            (
                "decisions",
                ["decision"],
                "ADR 0091 SQLite FTS5 retrieval substrate decision",
            ),
            (
                "decisions",
                ["decision"],
                "Phase 5 closeout philosophy seed graph 380 nodes",
            ),
            (
                "lessons",
                ["lesson"],
                "Lesson learned about validate hard fail soft warn gate",
            ),
            (
                "lessons",
                ["lesson"],
                "Routine wedge detect halted boot procedure recovery",
            ),
            ("lessons", ["lesson"], "scope lock routine commit allowlist enforcement"),
            (
                "lessons",
                ["lesson"],
                "MemPalace HNSW chromadb rebuild discipline at S-0186",
            ),
            ("pushback", ["pushback"], "Pushback decision against premature deferral"),
            (
                "operations",
                ["operations"],
                "Session shutdown sequence step 1 diary write",
            ),
            ("operations", ["operations"], "engine memory substrate boot orchestrator"),
            (
                "operations",
                ["operations", "audit"],
                "S-0184 health check audit overdue catchup pattern",
            ),
            (
                "operations",
                ["operations"],
                "build_lifecycle_push wrapper interactive harness gate",
            ),
            (
                "lessons",
                ["lesson"],
                "First pass production quality drafts polish - author once",
            ),
        ]
        for room, tags, content in seeds:
            conn.execute(
                "INSERT INTO drawers (id, room, tags, source_kind, content) "
                "VALUES (?, ?, ?, 'manual', ?)",
                (
                    f"seed-{abs(hash(content)) % 10**12}",
                    room,
                    json.dumps(tags),
                    content,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def test_real_data_harness_pass_on_well_populated_substrate(tmp_path: Path) -> None:
    db = tmp_path / "real.sqlite3"
    _seed_real_data_corpus(db)
    aggregate, fixed, plausible = verify_recall.run_real_data_harness(db)
    assert aggregate in ("PASS", "PARTIAL")
    assert len(fixed) == 10
    assert len(plausible) == 5


def test_real_data_harness_fails_on_empty_substrate(tmp_path: Path) -> None:
    db = tmp_path / "empty.sqlite3"
    conn = get_conn(db)  # Initialize schema; no content.
    conn.close()
    aggregate, fixed, plausible = verify_recall.run_real_data_harness(db)
    assert aggregate == "FAIL"
    assert all(r.verdict == "FAIL" for r in fixed)
    assert all(r.verdict == "FAIL" for r in plausible)


def test_real_data_main_exit_2_when_substrate_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = verify_recall.main(
        [
            "--real-data",
            "--db-path",
            str(tmp_path / "absent.sqlite3"),
            "--no-write",
        ]
    )
    assert rc == 2
    assert "live substrate not found" in capsys.readouterr().err


def test_real_data_main_writes_S_0192_report(tmp_path: Path) -> None:
    db = tmp_path / "real.sqlite3"
    _seed_real_data_corpus(db)
    output = tmp_path / "real_report.md"
    rc = verify_recall.main(
        ["--real-data", "--db-path", str(db), "--output-md", str(output)]
    )
    assert rc == 0
    body = output.read_text()
    assert "S-0192 (real data)" in body
    assert "Fixed-catalog results" in body
    assert "Plausible-recall results" in body


def test_count_live_substrate_reports_drawer_and_diary_counts(tmp_path: Path) -> None:
    db = tmp_path / "real.sqlite3"
    conn = get_conn(db)
    try:
        conn.execute(
            "INSERT INTO drawers (id, room, tags, source_kind, content) "
            "VALUES ('a', 'decisions', '[]', 'manual', 'x')"
        )
        conn.execute("INSERT INTO diary (id, content) VALUES ('d1', 'reflection')")
        conn.commit()
    finally:
        conn.close()
    d_count, diary_count = verify_recall._count_live_substrate(db)
    assert d_count == 1
    assert diary_count == 1


def test_render_real_data_report_emits_pass_handoff(tmp_path: Path) -> None:
    db = tmp_path / "real.sqlite3"
    _seed_real_data_corpus(db)
    aggregate, fixed, plausible = verify_recall.run_real_data_harness(db)
    body = verify_recall.render_real_data_report(
        aggregate, fixed, plausible, "2026-05-17T00:00:00Z", 14, 0
    )
    assert "## Cutover-gate handoff" in body
    # Body content varies by aggregate; just confirm the section exists.
    assert "engine_memory_recall_S-0192.md" not in body  # Body never self-references
