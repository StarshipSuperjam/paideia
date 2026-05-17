"""Tests for ``engine.memory.verify_mempalace_parity``.

Focused on the pure-function components — classification, verdict
decision, n-gram extraction, FTS5 query — without spinning up a full
chromadb-backed palace stub. Coverage + content-fidelity end-to-end
runs are exercised in-session against the live substrate (the audit
report at ``engine/docs/audits/engine_memory_parity_S-0193.md`` is the
empirical evidence those paths work).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.memory import verify_mempalace_parity as v
from engine.memory.connection import get_conn


# --------------------------------------------------------------------
# classify_drawer
# --------------------------------------------------------------------


def test_classify_drawer_excludes_non_load_bearing_wings() -> None:
    is_lb, reason = v.classify_drawer("sessions", "decisions", "anything")
    assert not is_lb
    assert "non-load-bearing wing" in reason


def test_classify_drawer_empty_content_is_tombstone_not_load_bearing() -> None:
    """Empty content always returns non-load-bearing, even if room qualifies.

    Regression guard: pre-fix the classifier treated empty content as
    load-bearing whenever the room name was in LOAD_BEARING_ROOMS;
    that produced 9 spurious coverage failures during the S-0193
    parity run for chromadb-tombstoned ``paideia/operations`` closets.
    """
    is_lb, reason = v.classify_drawer("paideia", "operations", "")
    assert not is_lb
    assert "tombstone" in reason
    is_lb2, reason2 = v.classify_drawer("paideia", "decisions", "   \n  ")
    assert not is_lb2
    assert "tombstone" in reason2


def test_classify_drawer_content_prefix_overrides_room() -> None:
    is_lb, reason = v.classify_drawer(
        "paideia", "general", "[pushback] S-0155 self-pushback"
    )
    assert is_lb
    assert "content-prefix '[pushback]'" in reason
    is_lb2, reason2 = v.classify_drawer(
        "paideia", "decisions", "# Verbatim exchange — bimodal session model"
    )
    assert is_lb2
    assert "content-prefix '# Verbatim exchange'" in reason2


def test_classify_drawer_load_bearing_room_name() -> None:
    is_lb, reason = v.classify_drawer("paideia", "decisions", "ADR 0091 narrative")
    assert is_lb
    assert "load-bearing room 'decisions'" in reason
    # The S-0193 extended room set also qualifies
    is_lb2, _ = v.classify_drawer(
        "paideia", "problems", "S-0075 cross-bridge curation rationale"
    )
    assert is_lb2
    is_lb3, _ = v.classify_drawer(
        "paideia", "foundation-planning-s0001", "verbatim S-0001 exchange"
    )
    assert is_lb3


def test_classify_drawer_unmapped_room_no_prefix_skips() -> None:
    is_lb, reason = v.classify_drawer(
        "paideia", "general", "freeform exploration notes"
    )
    assert not is_lb
    assert "non-load-bearing room 'general'" in reason


# --------------------------------------------------------------------
# pick_ngram
# --------------------------------------------------------------------


def test_pick_ngram_returns_words_from_middle() -> None:
    content = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    ngram = v.pick_ngram(content, 4)
    # Words are stripped + filtered to ≥3 chars (eta/iota are 3-4)
    parts = ngram.split()
    assert len(parts) == 4
    assert all(len(p) >= 3 for p in parts)


def test_pick_ngram_short_content_returns_all() -> None:
    content = "one two three"
    # Tokens filtered to ≥3 chars; "one" and "two" are 3-char so kept;
    # "two" has only 3 letters but is short word anyway
    ngram = v.pick_ngram(content, 10)
    parts = ngram.split()
    assert set(parts).issubset({"one", "two", "three"})


def test_pick_ngram_strips_punctuation() -> None:
    content = "(hello) world! foo.bar [baz]"
    ngram = v.pick_ngram(content, 3)
    # No raw punctuation chars survive the tokenization
    for ch in "()[]!{}'\":,;":
        assert ch not in ngram


# --------------------------------------------------------------------
# fts_match (live substrate behavior)
# --------------------------------------------------------------------


def test_fts_match_returns_results_for_present_term(tmp_path: Path) -> None:
    """FTS5 round-trip works with the schema's content_rowid='rowid' join."""
    db = tmp_path / "engine_memory.sqlite3"
    con = get_conn(path=db)
    try:
        con.execute(
            """
            INSERT INTO drawers (id, room, tags, source_kind, agent,
                                 session_id, filed_at, content, metadata)
            VALUES ('drawer-A', 'pushback', '[]', 'manual', 'claude',
                    'S-0193-test', '2026-05-17 00:00:00',
                    'pushback against silent indefinite deferral', '{}')
            """
        )
        results = v.fts_match(con, "pushback", top_k=5)
    finally:
        con.close()
    assert len(results) >= 1
    assert results[0][0] == "drawer-A"


def test_fts_match_handles_no_match(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    con = get_conn(path=db)
    try:
        results = v.fts_match(con, "nonexistent_word_xyz", top_k=5)
    finally:
        con.close()
    assert results == []


def test_fts_match_empty_query_returns_empty() -> None:
    # No connection use — empty query early-returns.
    fake_con = sqlite3.connect(":memory:")
    try:
        assert v.fts_match(fake_con, "", top_k=5) == []
        assert v.fts_match(fake_con, "   ", top_k=5) == []
    finally:
        fake_con.close()


# --------------------------------------------------------------------
# decide_verdict
# --------------------------------------------------------------------


def _empty_report() -> v.ParityReport:
    # Path strings here are placeholders for the dataclass field — never
    # touched on the filesystem. Avoid /tmp paths so bandit's
    # hardcoded-tmp-directory check (B108) doesn't flag the test as
    # using shared writable locations.
    return v.ParityReport(
        palace_path="<test-palace-placeholder>",
        substrate_path="<test-substrate-placeholder>",
    )


def test_decide_verdict_pass_when_all_clean() -> None:
    r = _empty_report()
    r.coverage_pass_count = 10
    r.coverage_fail_count = 0
    r.sessions_wing_in_engine_memory = 0
    r.source_diary_count = 207
    r.substrate_diary_count = 207
    # No spot-checks scenario — still PASS
    v.decide_verdict(r)
    assert r.verdict == "PASS"
    assert r.fail_reasons == []
    assert r.partial_reasons == []


def test_decide_verdict_fail_on_coverage_gap() -> None:
    r = _empty_report()
    r.coverage_fail_count = 3
    v.decide_verdict(r)
    assert r.verdict == "FAIL"
    assert any("3 load-bearing sample" in reason for reason in r.fail_reasons)


def test_decide_verdict_fail_on_sessions_wing_leak() -> None:
    r = _empty_report()
    r.sessions_wing_in_engine_memory = 5
    v.decide_verdict(r)
    assert r.verdict == "FAIL"
    assert any("sessions-wing drawer" in reason for reason in r.fail_reasons)


def test_decide_verdict_partial_on_fts_below_threshold() -> None:
    r = _empty_report()
    r.content_spot_checks = [
        v.ContentFidelityResult(
            uuid=f"u-{i}",
            source_room="decisions",
            target_room="decisions",
            content_matches=True,
            content_byte_diff=0,
            fts_hit=(i < 5),  # only 5/20 hits → below 70%
            fts_top_k_count=10 if i < 5 else 0,
            fts_ngram_used="…",
        )
        for i in range(20)
    ]
    v.decide_verdict(r)
    assert r.verdict == "PARTIAL"
    assert any("FTS5 retrievability" in reason for reason in r.partial_reasons)


def test_decide_verdict_partial_on_diary_drift() -> None:
    r = _empty_report()
    r.source_diary_count = 200
    r.substrate_diary_count = 50  # delta = 150 ≫ tolerance
    v.decide_verdict(r)
    assert r.verdict == "PARTIAL"
    assert any("diary count delta" in reason for reason in r.partial_reasons)


def test_decide_verdict_diary_within_tolerance_no_partial() -> None:
    r = _empty_report()
    r.source_diary_count = 207
    r.substrate_diary_count = 205  # delta = 2 < tolerance of 5
    v.decide_verdict(r)
    assert r.verdict == "PASS"


def test_decide_verdict_fail_supersedes_partial() -> None:
    r = _empty_report()
    r.coverage_fail_count = 1
    r.source_diary_count = 1000
    r.substrate_diary_count = 1  # also a partial signal
    v.decide_verdict(r)
    assert r.verdict == "FAIL"  # FAIL wins; partial reasons still recorded
    assert len(r.fail_reasons) >= 1


# --------------------------------------------------------------------
# main exit codes (without live palace)
# --------------------------------------------------------------------


def test_main_exits_3_when_palace_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = v.main(["--palace", str(tmp_path / "no-palace")])
    assert rc == 3
    captured = capsys.readouterr()
    assert "palace not found" in captured.err
