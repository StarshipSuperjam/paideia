"""Tests for engine/tools/health_check.py.

Test contract — what this suite covers and does not cover.

The suite covers each public surface of health_check.py with at least one
test per function and one test per logical branch within each function.
Coverage targets: archive parsing edge cases (missing dir, malformed JSON,
mixed structured/unstructured archives), per-audit findings (clean / dirty
input paths), report rendering, and CLI exit codes.

Test isolation strategy:

- Filesystem isolation via pytest's tmp_path and monkeypatch fixtures.
  Tests construct synthetic repo trees in tmp_path and patch
  health_check's path constants to point there.
- No subprocess invocations (the script is pure Python; no external tool
  dependencies).
- No real-repo dependencies (every test builds the inputs it needs).

Non-responsibilities:

- Does not test markdown rendering exhaustively; spot-checks structural
  integrity (section headers present, four sections appear, summary
  paragraph present).
- Does not test argparse beyond exit-code paths.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import health_check  # noqa: E402
from health_check import (  # noqa: E402
    CategoryFindings,
    HealthCheckReport,
    _count_adrs,
    _drawer_documents_via_sqlite,
    _room_counts_via_sqlite,
    audit_bloat,
    audit_dead_weight,
    audit_fit,
    audit_gaps,
    audit_mempalace,
    detect_cadence,
    detect_last_check,
    emit_accumulated_pushbacks_and_lessons,
    emit_affirmative_retire_candidates,
    emit_bloat,
    emit_cadence_calibration,
    emit_cold_context_probe,
    emit_fit,
    emit_forward_fit_map,
    emit_freshness_probes_run,
    emit_gaps,
    emit_infrastructure_without_function,
    emit_non_obvious_findings,
    emit_operative_diagnostic_applied,
    emit_preamble,
    emit_report,
    emit_summary,
    emit_user_adjudication,
    list_archives,
    main,
    read_archive,
    render_report,
    render_section,
    soft_warns_from_archive,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal synthetic repo and patch health_check's path constants.

    Builds: archive dir, ADR dirs (engine + product), engine_log, tensions,
    operations dir, report dir. Each starts empty; tests populate as needed.
    """
    (tmp_path / "engine" / "session" / "archive").mkdir(parents=True)
    (tmp_path / "engine" / "adr").mkdir(parents=True)
    (tmp_path / "product" / "adr").mkdir(parents=True)
    (tmp_path / "product" / "docs").mkdir(parents=True)
    (tmp_path / "engine" / "operations").mkdir(parents=True)
    (tmp_path / "engine" / "tools").mkdir(parents=True)
    (tmp_path / "docs" / "health-checks").mkdir(parents=True)

    monkeypatch.setattr(health_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        health_check, "ARCHIVE_DIR", tmp_path / "engine" / "session" / "archive"
    )
    monkeypatch.setattr(health_check, "ENGINE_ADR_DIR", tmp_path / "engine" / "adr")
    monkeypatch.setattr(health_check, "PRODUCT_ADR_DIR", tmp_path / "product" / "adr")
    monkeypatch.setattr(
        health_check, "ENGINE_LOG_PATH", tmp_path / "engine" / "ENGINE_LOG.md"
    )
    monkeypatch.setattr(
        health_check, "TENSIONS_PATH", tmp_path / "product" / "docs" / "tensions.md"
    )
    monkeypatch.setattr(
        health_check, "OPERATIONS_DIR", tmp_path / "engine" / "operations"
    )
    monkeypatch.setattr(
        health_check,
        "VALIDATE_HISTORY_PATH",
        tmp_path / "engine" / "tools" / "validate-history.jsonl",
    )
    monkeypatch.setattr(health_check, "REPORT_DIR", tmp_path / "docs" / "health-checks")
    # Universal-scan paths added at S-0041; monkeypatch so tests don't scan the real repo.
    monkeypatch.setattr(health_check, "BUILD_PLAN_DIR", tmp_path / "build_plan")
    return tmp_path


def write_archive(
    repo: Path, session_id: str, soft_warns: dict[str, int] | None = None
) -> None:
    """Helper: write an archive file with the given soft-warn counts."""
    archive_path = repo / "engine" / "session" / "archive" / f"{session_id}.json"
    payload: dict[str, Any] = {
        "id": session_id,
        "started_at": "2026-05-01T10:00:00Z",
        "closed_at": "2026-05-01T11:30:00Z",
        "status": "closed",
        "outcome_summary": "test",
    }
    if soft_warns is not None:
        payload["outcome_summary_soft_warns"] = soft_warns
    archive_path.write_text(json.dumps(payload))


def write_adr(
    repo: Path, *, engine: bool, num: str, status: str, body: str = ""
) -> Path:
    """Helper: write an ADR file with the given Status field."""
    adr_dir = repo / ("engine" if engine else "product") / "adr"
    path = adr_dir / f"{num}-test-{num}.md"
    path.write_text(
        f"# ADR {num} — Test\n\n- **Status:** {status}\n- **Date:** 2026-05-01\n\n"
        f"## Context\n\nTest.\n\n## Decision\n\nTest.\n\n## Consequences\n\n{body}\n"
    )
    return path


# ---------------------------------------------------------------------------
# CategoryFindings
# ---------------------------------------------------------------------------


def test_category_findings_starts_empty() -> None:
    findings = CategoryFindings()
    assert findings.is_empty()


def test_category_findings_add_observation() -> None:
    findings = CategoryFindings()
    findings.add("observed something", "queue follow-up")
    assert not findings.is_empty()
    assert findings.observations == [("observed something", "queue follow-up")]


def test_category_findings_default_action() -> None:
    findings = CategoryFindings()
    findings.add("noted")
    assert findings.observations[0][1] == "no action"


# ---------------------------------------------------------------------------
# Archive helpers
# ---------------------------------------------------------------------------


def test_list_archives_empty(synthetic_repo: Path) -> None:
    assert list_archives() == []


def test_list_archives_returns_sorted(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0003")
    write_archive(synthetic_repo, "S-0001")
    write_archive(synthetic_repo, "S-0002")
    archives = list_archives()
    assert [p.stem for p in archives] == ["S-0001", "S-0002", "S-0003"]


def test_list_archives_missing_dir(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(health_check, "ARCHIVE_DIR", synthetic_repo / "nonexistent")
    assert list_archives() == []


def test_read_archive_valid(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0001", soft_warns={"foo": 1})
    archive = read_archive(
        synthetic_repo / "engine" / "session" / "archive" / "S-0001.json"
    )
    assert archive["id"] == "S-0001"
    assert archive["outcome_summary_soft_warns"] == {"foo": 1}


def test_read_archive_malformed(synthetic_repo: Path) -> None:
    bad = synthetic_repo / "engine" / "session" / "archive" / "S-0001.json"
    bad.write_text("not valid json {")
    assert read_archive(bad) == {}


def test_read_archive_nonexistent(synthetic_repo: Path) -> None:
    assert read_archive(synthetic_repo / "missing.json") == {}


def test_soft_warns_from_archive_present() -> None:
    archive = {"outcome_summary_soft_warns": {"cat_a": 2, "cat_b": 0}}
    assert soft_warns_from_archive(archive) == {"cat_a": 2, "cat_b": 0}


def test_soft_warns_from_archive_absent() -> None:
    archive = {"outcome_summary": "no structured field"}
    assert soft_warns_from_archive(archive) == {}


def test_soft_warns_from_archive_filters_non_int() -> None:
    archive = {"outcome_summary_soft_warns": {"cat_a": 1, "cat_b": "two", 5: 3}}
    assert soft_warns_from_archive(archive) == {"cat_a": 1}


# ---------------------------------------------------------------------------
# audit_fit
# ---------------------------------------------------------------------------


def test_audit_fit_no_archives(synthetic_repo: Path) -> None:
    findings = audit_fit([])
    assert any("No closed sessions" in obs for obs, _ in findings.observations)


def test_audit_fit_no_structured_archives(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0001")
    findings = audit_fit(list_archives())
    assert any(
        "structured outcome_summary_soft_warns" in obs
        for obs, _ in findings.observations
    )


def test_audit_fit_persistent_warn_below_escalation(synthetic_repo: Path) -> None:
    for n in range(5):
        write_archive(synthetic_repo, f"S-{n + 1:04d}", soft_warns={"cat_a": 1})
    findings = audit_fit(list_archives())
    assert any("Soft-warn `cat_a` recurring" in obs for obs, _ in findings.observations)


def test_audit_fit_persistent_warn_at_escalation(synthetic_repo: Path) -> None:
    for n in range(10):
        write_archive(synthetic_repo, f"S-{n + 1:04d}", soft_warns={"cat_a": 1})
    findings = audit_fit(list_archives())
    assert any(
        "Soft-warn `cat_a` persistent" in obs for obs, _ in findings.observations
    )


def test_audit_fit_adr_status_distribution(synthetic_repo: Path) -> None:
    write_adr(synthetic_repo, engine=True, num="0050", status="Accepted")
    write_adr(synthetic_repo, engine=True, num="0051", status="Superseded by ADR 0052")
    findings = audit_fit([])
    assert any(
        "accepted" in obs.lower() and "superseded" in obs.lower()
        for obs, _ in findings.observations
    )


def test_audit_fit_engine_log_missing_session_entry(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0001")
    (synthetic_repo / "engine" / "ENGINE_LOG.md").write_text(
        "# Engine log\n\n## [Unreleased]\n\nNo entries.\n"
    )
    findings = audit_fit(list_archives())
    assert any("no reference in ENGINE_LOG" in obs for obs, _ in findings.observations)


# ---------------------------------------------------------------------------
# audit_gaps
# ---------------------------------------------------------------------------


def test_audit_gaps_no_inputs(synthetic_repo: Path) -> None:
    findings = audit_gaps()
    assert any("No Gaps surfaced" in obs for obs, _ in findings.observations)


def test_audit_gaps_aged_tension(synthetic_repo: Path) -> None:
    # Establish a recent session so the latest_session calculation works.
    write_archive(synthetic_repo, "S-0030")
    (synthetic_repo / "product" / "docs" / "tensions.md").write_text(
        "# Tensions\n\n## OQ-OLD\n\nAdded at S-0005.\n\nSome content.\n"
    )
    findings = audit_gaps()
    assert any("aged tension" in obs for obs, _ in findings.observations)


def test_audit_gaps_resolved_tension_excluded(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0030")
    (synthetic_repo / "product" / "docs" / "tensions.md").write_text(
        "# Tensions\n\n## OQ-DONE\n\nAdded at S-0005.\n\nResolved: 2026-04-01.\n"
    )
    findings = audit_gaps()
    assert not any("aged tension" in obs for obs, _ in findings.observations)


def test_audit_gaps_promised_deliverable_absent(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0005")
    write_adr(
        synthetic_repo,
        engine=True,
        num="0050",
        status="Accepted",
        body="`tools/missing_thing.py` lands around S-0005.",
    )
    findings = audit_gaps()
    assert any("Consequences promise" in obs for obs, _ in findings.observations)


def test_audit_gaps_promised_deliverable_present(synthetic_repo: Path) -> None:
    write_archive(synthetic_repo, "S-0005")
    (synthetic_repo / "tools").mkdir()
    (synthetic_repo / "tools" / "delivered.py").write_text("# delivered")
    write_adr(
        synthetic_repo,
        engine=True,
        num="0051",
        status="Accepted",
        body="`tools/delivered.py` lands around S-0005.",
    )
    findings = audit_gaps()
    assert not any("Consequences promise" in obs for obs, _ in findings.observations)


def _write_adr_with_orphan_ok(
    repo: Path,
    *,
    engine: bool,
    num: str,
    status: str,
    orphan_ok_lines: list[str],
) -> Path:
    """Write an ADR file with one or more Orphan-OK annotations after Status."""
    adr_dir = repo / ("engine" if engine else "product") / "adr"
    path = adr_dir / f"{num}-test-{num}.md"
    annotations = "\n".join(orphan_ok_lines)
    path.write_text(
        f"# ADR {num} — Test\n\n"
        f"- **Status:** {status}\n"
        f"- **Date:** 2026-05-01\n"
        f"{annotations}\n\n"
        f"## Context\n\nTest.\n\n## Decision\n\nTest.\n\n## Consequences\n\nTest.\n"
    )
    return path


def _seed_state_md_with_phase(repo: Path, phase_num: int) -> None:
    """Write a STATE.md with a Current-phase headline-table row."""
    state_path = repo / "engine" / "STATE.md"
    state_path.write_text(
        "# Project State\n\n## Current\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| **Current phase** | **Phase {phase_num} — Test phase.** |\n"
    )


def _seed_register_with_last_claimed(repo: Path, last_claimed: str | None) -> None:
    """Write a register_state.json with the given last_claimed value."""
    register_path = repo / "engine" / "session" / "register_state.json"
    payload: dict[str, Any] = {
        "next_id": "0099",
        "current_status": "closed",
    }
    if last_claimed is not None:
        payload["last_claimed"] = last_claimed
    register_path.write_text(json.dumps(payload))


def test_audit_orphan_ok_list_session_trigger_passed_surfaces_finding(
    synthetic_repo: Path,
) -> None:
    """ADR with `revisit at S-0050`; current session S-0099 → stale finding."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=[
            "- **Orphan-OK:** future Phase 6 grounding; revisit at S-0050"
        ],
    )
    findings = health_check.audit_orphan_ok_list()
    assert any("trigger `S-0050` has passed" in obs for obs, _ in findings.observations)
    assert any("current session: S-0099" in obs for obs, _ in findings.observations)


def test_audit_orphan_ok_list_session_trigger_not_yet_reached_no_finding(
    synthetic_repo: Path,
) -> None:
    """ADR with `revisit at S-0150`; current session S-0099 → no finding."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** Phase 8 grounding; revisit at S-0150"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert findings.is_empty()


def test_audit_orphan_ok_list_phase_trigger_passed_surfaces_finding(
    synthetic_repo: Path,
) -> None:
    """`revisit at Phase 5` with current phase 5 → stale (>= triggers fire)."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _seed_state_md_with_phase(synthetic_repo, phase_num=5)
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0041",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** decided in Phase 4; revisit at Phase 5"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert any(
        "trigger `Phase 5` has been reached" in obs for obs, _ in findings.observations
    )


def test_audit_orphan_ok_list_phase_trigger_not_yet_reached_no_finding(
    synthetic_repo: Path,
) -> None:
    """`revisit at Phase 8` with current phase 5 → no finding."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _seed_state_md_with_phase(synthetic_repo, phase_num=5)
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0041",
        status="Accepted",
        orphan_ok_lines=[
            "- **Orphan-OK:** Phase 8 cost-cap grounding; revisit at Phase 8"
        ],
    )
    findings = health_check.audit_orphan_ok_list()
    assert findings.is_empty()


def test_audit_orphan_ok_list_no_annotation_returns_empty(
    synthetic_repo: Path,
) -> None:
    """Accepted ADR without Orphan-OK annotation → no findings."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    write_adr(synthetic_repo, engine=True, num="0040", status="Accepted")
    findings = health_check.audit_orphan_ok_list()
    assert findings.is_empty()


def test_audit_orphan_ok_list_non_accepted_adr_skipped(
    synthetic_repo: Path,
) -> None:
    """ADR with Orphan-OK but Status != Accepted is skipped (Superseded etc.)."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Superseded by ADR 0099",
        orphan_ok_lines=["- **Orphan-OK:** old reason; revisit at S-0050"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert findings.is_empty()


def test_audit_orphan_ok_list_malformed_trigger_surfaces_informational_finding(
    synthetic_repo: Path,
) -> None:
    """A trigger that's neither S-NNNN nor Phase-N is surfaced as malformed."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** vague reason; revisit at someday"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert any(
        "is neither S-NNNN nor Phase-N shape (malformed)" in obs
        for obs, _ in findings.observations
    )


def test_audit_orphan_ok_list_register_missing_session_trigger_cannot_evaluate(
    synthetic_repo: Path,
) -> None:
    """Without register_state.json, session-id triggers surface as informational."""
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** test; revisit at S-0050"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert any(
        "cannot be evaluated (register_state.json missing or last_claimed malformed)"
        in obs
        for obs, _ in findings.observations
    )


def test_audit_orphan_ok_list_state_missing_phase_trigger_cannot_evaluate(
    synthetic_repo: Path,
) -> None:
    """Without STATE.md, phase triggers surface as informational findings."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    # No STATE.md.
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** test; revisit at Phase 6"],
    )
    findings = health_check.audit_orphan_ok_list()
    assert any(
        "cannot be evaluated (STATE.md Current-phase row not parseable)" in obs
        for obs, _ in findings.observations
    )


def test_audit_orphan_ok_list_multiple_annotations_in_one_adr(
    synthetic_repo: Path,
) -> None:
    """A single ADR with multiple Orphan-OK lines yields a finding per stale line."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=[
            "- **Orphan-OK:** first reason; revisit at S-0050",
            "- **Orphan-OK:** second reason; revisit at S-0150",
        ],
    )
    findings = health_check.audit_orphan_ok_list()
    # Only the first (S-0050, passed) is stale; the second (S-0150, not yet) isn't.
    stale_count = sum(1 for obs, _ in findings.observations if "has passed" in obs)
    assert stale_count == 1


def test_audit_orphan_ok_list_integrated_into_audit_gaps(
    synthetic_repo: Path,
) -> None:
    """audit_gaps() folds audit_orphan_ok_list() findings into Gaps observations."""
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    _write_adr_with_orphan_ok(
        synthetic_repo,
        engine=True,
        num="0040",
        status="Accepted",
        orphan_ok_lines=["- **Orphan-OK:** stale; revisit at S-0050"],
    )
    findings = audit_gaps()
    assert any(
        "Orphan-OK revisit-by trigger" in obs and "S-0050" in obs
        for obs, _ in findings.observations
    )


def test_audit_orphan_ok_list_corpus_today_has_zero_findings(
    synthetic_repo: Path,
) -> None:
    """Empirical baseline: with no ADRs carrying Orphan-OK, no findings emit.

    Documents the pre-S-0099 corpus state that motivated this audit being
    additive: zero existing annotations means the function is load-bearing
    only when annotations begin to be authored. No false positives on first
    deployment.
    """
    _seed_register_with_last_claimed(synthetic_repo, "S-0099")
    write_adr(synthetic_repo, engine=True, num="0040", status="Accepted")
    write_adr(synthetic_repo, engine=False, num="0050", status="Accepted")
    findings = health_check.audit_orphan_ok_list()
    assert findings.is_empty()


def test_audit_gaps_promised_path_relative_to_adr_dir(synthetic_repo: Path) -> None:
    """Path resolution tries ADR-directory-relative when repo-root-relative fails."""
    write_archive(synthetic_repo, "S-0014")
    # Sibling ADR exists in the same product/adr/ directory.
    sibling = synthetic_repo / "product" / "adr" / "0099-sibling.md"
    sibling.write_text("# ADR 0099 — Sibling")
    write_adr(
        synthetic_repo,
        engine=False,
        num="0050",
        status="Accepted",
        body="See [ADR 0099](0099-sibling.md), lands at S-0014.",
    )
    findings = audit_gaps()
    # `0099-sibling.md` does not resolve from REPO_ROOT but does resolve
    # from product/adr/. Should NOT warn (mirrors validate.py dual-resolution).
    assert not any("Consequences promise" in obs for obs, _ in findings.observations)


# ---------------------------------------------------------------------------
# audit_dead_weight
# ---------------------------------------------------------------------------


def test_audit_dead_weight_no_inputs(synthetic_repo: Path) -> None:
    findings = audit_dead_weight()
    assert any("No Dead-weight" in obs for obs, _ in findings.observations)


def test_audit_dead_weight_deprecated_adr(synthetic_repo: Path) -> None:
    write_adr(synthetic_repo, engine=True, num="0099", status="Deprecated")
    findings = audit_dead_weight()
    assert any("Deprecated ADR" in obs for obs, _ in findings.observations)


def test_audit_dead_weight_uncited_ops_doc(synthetic_repo: Path) -> None:
    (synthetic_repo / "engine" / "operations" / "lonely.md").write_text(
        "# Lonely\n\nNo one cites me.\n"
    )
    findings = audit_dead_weight()
    # S-0041 universal-scan rewrite changed wording from "no inbound" to
    # "zero inbound citations"; both phrasings target the same finding.
    assert any("zero inbound citations" in obs for obs, _ in findings.observations)


def test_audit_dead_weight_cited_ops_doc(synthetic_repo: Path) -> None:
    (synthetic_repo / "engine" / "operations" / "popular.md").write_text("# Popular\n")
    (synthetic_repo / "README.md").write_text(
        "See engine/operations/popular.md for details.\n"
    )
    findings = audit_dead_weight()
    # Should not flag popular.md as uncited.
    for obs, _ in findings.observations:
        assert "popular.md" not in obs or "zero inbound" not in obs


# ---------------------------------------------------------------------------
# audit_bloat
# ---------------------------------------------------------------------------


def test_audit_bloat_no_inputs(synthetic_repo: Path) -> None:
    findings = audit_bloat()
    assert any("No Bloat" in obs for obs, _ in findings.observations)


def test_audit_bloat_large_ops_doc(synthetic_repo: Path) -> None:
    big_doc = synthetic_repo / "engine" / "operations" / "huge.md"
    big_doc.write_text("# Huge\n" + "line\n" * 350)
    findings = audit_bloat()
    assert any("over 300 lines" in obs for obs, _ in findings.observations)


def test_audit_bloat_session_duration_trend(synthetic_repo: Path) -> None:
    for n in range(3):
        write_archive(synthetic_repo, f"S-{n + 1:04d}")
    findings = audit_bloat()
    assert any("session duration" in obs for obs, _ in findings.observations)


def test_audit_bloat_duration_trend_handles_legacy_plus_offset(
    synthetic_repo: Path,
) -> None:
    """Verifies the helper-routed duration parse (ADR 0058 / Issue #33)
    survives mixed Z-suffix and legacy +00:00 archive shapes — the
    smoking-gun fix at health_check.py:960-961 removed the bare
    .replace("Z", "+00:00") gymnastics in favor of timestamps.parse()."""
    archive_dir = synthetic_repo / "engine" / "session" / "archive"
    # One archive in canonical Z-suffix shape.
    (archive_dir / "S-0001.json").write_text(
        json.dumps(
            {
                "id": "S-0001",
                "started_at": "2026-05-01T10:00:00Z",
                "closed_at": "2026-05-01T11:30:00Z",
                "status": "closed",
                "outcome_summary": "z-shape",
            }
        )
    )
    # One archive in legacy Python .isoformat() shape (+00:00 offset).
    (archive_dir / "S-0002.json").write_text(
        json.dumps(
            {
                "id": "S-0002",
                "started_at": "2026-05-02T10:00:00.123456+00:00",
                "closed_at": "2026-05-02T11:30:00.654321+00:00",
                "status": "closed",
                "outcome_summary": "plus-offset-shape",
            }
        )
    )
    findings = audit_bloat()
    # Both archives must be parseable and contribute to the duration trend.
    duration_observations = [
        obs for obs, _ in findings.observations if "session duration" in obs
    ]
    assert duration_observations, (
        "duration-trend observation should fire across both shapes; "
        "if helper migration broke parsing, this assertion would fail."
    )


# ---------------------------------------------------------------------------
# Report emission
# ---------------------------------------------------------------------------


def test_render_section_with_findings() -> None:
    findings = CategoryFindings()
    findings.add("observed", "queue")
    out = render_section("Fit", findings, "intro")
    assert "## Fit" in out
    assert "> intro" in out
    assert "observed. queue." in out


def test_render_section_empty() -> None:
    out = render_section("Gaps", CategoryFindings(), "intro")
    assert "no findings. no action." in out


def test_render_report_structure(synthetic_repo: Path) -> None:
    """render_report emits the 14-body-section TEMPLATE.md shape, in order.

    Per ADR 0057 + Issue #53 (closed at S-0102): the script's contract is
    to produce the canonical 14-section adversarial-stance shape from
    docs/health-checks/TEMPLATE.md. Each section header must appear in
    order; data sections must include their findings; scaffolding
    sections must include their placeholder markers; the User adjudication
    section must be left blank on arrival per ADR 0057 element 1.
    """
    report = HealthCheckReport(session_id="S-0030")
    report.fit.add("F1")
    report.gaps.add("G1")
    report.dead_weight.add("D1")
    report.bloat.add("B1")
    report.mempalace.add("M1")
    rendered = render_report(report)

    # Preamble.
    assert "# Health Check S-0030" in rendered
    assert "engine/adr/0022-periodic-project-health-checks.md" in rendered, (
        "preamble must cite ADR 0022"
    )
    assert (
        "engine/adr/0057-adversarial-stance-for-health-check-audits.md" in rendered
    ), "preamble must cite ADR 0057"
    assert "conversational by default" in rendered

    # All 14 body sections present, in TEMPLATE.md order.
    expected_headers_in_order = [
        "## Freshness probes run",
        "## Operative diagnostic applied",
        "## Forward-fit map",
        "## Non-obvious finding(s)",
        "## Fit",
        "## Gaps",
        "## Infrastructure-without-function (dead weight)",
        "## Bloat",
        "## Accumulated pushbacks and lessons",
        "## Affirmative retire candidates",
        "## Cold-context probe",
        "## User adjudication",
        "## Cadence calibration",
        "## Summary",
    ]
    last_index = -1
    for header in expected_headers_in_order:
        idx = rendered.find(header)
        assert idx != -1, f"missing section header: {header!r}"
        assert idx > last_index, (
            f"section {header!r} appears out of TEMPLATE.md order "
            f"(idx={idx} <= last_index={last_index})"
        )
        last_index = idx

    # Data findings flow into their sections.
    assert "F1" in rendered and "G1" in rendered
    assert "D1" in rendered and "B1" in rendered
    assert "M1" in rendered, "audit_mempalace findings flow into Accumulated section"

    # Old shape has been retired.
    assert "## Dead weight\n" not in rendered, (
        "old 'Dead weight' header must be retired in favor of "
        "'Infrastructure-without-function (dead weight)'"
    )
    assert "## MemPalace\n" not in rendered, (
        "old standalone 'MemPalace' section folds into "
        "'Accumulated pushbacks and lessons'"
    )


# ---------------------------------------------------------------------------
# Per-section emitter unit tests (added at S-0102 per Issue #53)
#
# Each new emit_*() function from health_check.py gets at least one test
# verifying the section header + adversarial-prompt / scaffolding content
# its TEMPLATE.md row commits to. Data emitters (Fit / Gaps /
# Infrastructure-without-function / Bloat) get with-data + empty-data
# coverage; scaffolding emitters get structural-presence coverage.
# ---------------------------------------------------------------------------


def test_emit_preamble_with_last_check_computes_delta() -> None:
    report = HealthCheckReport(session_id="S-0102", cadence=20, last_check="S-0097")
    out = emit_preamble(report)
    assert "# Health Check S-0102" in out
    assert "**Cadence:** every 20 sessions." in out
    assert "Last check: S-0097 (Δ = 5)." in out
    assert "user-buffered execution" in out


def test_emit_preamble_without_last_check() -> None:
    report = HealthCheckReport(session_id="S-0102", cadence=20, last_check=None)
    out = emit_preamble(report)
    assert "Last check: none (first check)." in out
    assert "Δ = " not in out


def test_emit_preamble_handles_malformed_session_id_gracefully() -> None:
    """Malformed session ids skip delta computation rather than raising."""
    report = HealthCheckReport(session_id="S-XYZX", cadence=10, last_check="S-0097")
    out = emit_preamble(report)
    assert "Last check: S-0097." in out
    assert "Δ = " not in out


def test_emit_freshness_probes_run_lists_five_systems() -> None:
    out = emit_freshness_probes_run()
    assert out.startswith("## Freshness probes run")
    assert "stats-as-proxy-for-function" in out
    for system in (
        "**MemPalace.**",
        "**Validator.**",
        "**Supabase.**",
        "**Hooks.**",
        "**Registries.**",
    ):
        assert system in out, (
            f"freshness probes section missing system bullet: {system!r}"
        )
    assert "<observation" in out, "section must carry placeholder for AI population"


def test_emit_operative_diagnostic_applied_carries_scaffolding() -> None:
    out = emit_operative_diagnostic_applied()
    assert out.startswith("## Operative diagnostic applied")
    assert "dead-weight scanner output" in out
    assert "<observations>" in out


def test_emit_forward_fit_map_carries_scaffolding_table() -> None:
    out = emit_forward_fit_map()
    assert out.startswith("## Forward-fit map")
    assert "dual-temporal-frame" in out
    assert "Load-bearing forward" in out
    assert "Candidate-among-substrates" in out
    assert "| Forward state need |" in out, "scaffolding table header must be present"
    assert "<upcoming phase or OQ>" in out, (
        "scaffolding row placeholder must be present"
    )


def test_emit_non_obvious_findings_carries_first_finding_scaffold() -> None:
    out = emit_non_obvious_findings()
    assert out.startswith("## Non-obvious finding(s)")
    assert "≥1 required" in out
    assert "### Non-obvious finding A — <title>" in out


def test_emit_fit_with_data_carries_findings_and_adversarial_prompt() -> None:
    findings = CategoryFindings()
    findings.add("FIT-OBSERVATION-XYZ", "FIT-ACTION-XYZ")
    out = emit_fit(findings)
    assert out.startswith("## Fit")
    assert "**Adversarial prompt:**" in out
    assert "silently ignored" in out
    assert "FIT-OBSERVATION-XYZ" in out
    assert "FIT-ACTION-XYZ" in out


def test_emit_fit_empty_data_renders_no_findings_line() -> None:
    out = emit_fit(CategoryFindings())
    assert out.startswith("## Fit")
    assert "**Adversarial prompt:**" in out
    assert "no findings. no action." in out


def test_emit_gaps_with_data_carries_findings_and_adversarial_prompt() -> None:
    findings = CategoryFindings()
    findings.add("GAP-OBSERVATION-XYZ", "GAP-ACTION-XYZ")
    out = emit_gaps(findings)
    assert out.startswith("## Gaps")
    assert "new collaborator joined the project tomorrow" in out
    assert "GAP-OBSERVATION-XYZ" in out


def test_emit_infrastructure_without_function_uses_renamed_header() -> None:
    findings = CategoryFindings()
    findings.add("DW-OBSERVATION-XYZ", "DW-ACTION-XYZ")
    out = emit_infrastructure_without_function(findings)
    assert out.startswith("## Infrastructure-without-function (dead weight)")
    assert "argue this candidate's retirement" in out
    assert "DW-OBSERVATION-XYZ" in out
    assert "## Dead weight\n" not in out, "old header retired"


def test_emit_bloat_with_data_carries_findings_and_adversarial_prompt() -> None:
    findings = CategoryFindings()
    findings.add("BLOAT-OBSERVATION-XYZ", "BLOAT-ACTION-XYZ")
    out = emit_bloat(findings)
    assert out.startswith("## Bloat")
    assert "halve in size" in out
    assert "BLOAT-OBSERVATION-XYZ" in out


def test_emit_accumulated_pushbacks_and_lessons_with_mempalace_data() -> None:
    findings = CategoryFindings()
    findings.add("MEMPALACE-OBSERVATION-XYZ", "MEMPALACE-ACTION-XYZ")
    out = emit_accumulated_pushbacks_and_lessons(findings)
    assert out.startswith("## Accumulated pushbacks and lessons")
    assert "Mechanical observations from `audit_mempalace()`:" in out
    assert "MEMPALACE-OBSERVATION-XYZ" in out
    assert "### Pushback clusters" in out
    assert "### Lesson clusters" in out


def test_emit_accumulated_pushbacks_and_lessons_without_mempalace_data() -> None:
    """Empty audit_mempalace findings still yield scaffolding for AI clustering."""
    out = emit_accumulated_pushbacks_and_lessons(CategoryFindings())
    assert out.startswith("## Accumulated pushbacks and lessons")
    assert "Mechanical observations from `audit_mempalace()`:" not in out
    assert "### Pushback clusters" in out
    assert "### Lesson clusters" in out


def test_emit_affirmative_retire_candidates_carries_both_alternatives() -> None:
    """Section scaffolds both Retire-candidate-A and No-retire-candidates paths."""
    out = emit_affirmative_retire_candidates()
    assert out.startswith("## Affirmative retire candidates")
    assert "### Retire candidate A — <title>" in out
    assert "### No retire candidates this audit" in out
    assert "adversarially scrutinizing" in out


def test_emit_cold_context_probe_carries_random_pick_procedure() -> None:
    out = emit_cold_context_probe()
    assert out.startswith("## Cold-context probe")
    assert "**Artifact selected (random):**" in out
    assert "**Cold-read findings:**" in out
    assert "shuf -n 1" in out


def test_emit_user_adjudication_blank_on_arrival_with_lanes_listed() -> None:
    """Per ADR 0057 element 1: section is blank-on-arrival but the four
    routing lanes (inline / STATE / Issue / tension) are listed."""
    out = emit_user_adjudication()
    assert out.startswith("## User adjudication")
    assert "Left blank on arrival" in out
    assert "<populated post-audit by the user>" in out
    assert "Inline trivial cleanup" in out
    assert "Next-session work item" in out
    assert "New GitHub Issue" in out
    assert "New tension" in out


def test_emit_cadence_calibration_emits_report_cadence() -> None:
    report = HealthCheckReport(session_id="S-0102", cadence=20)
    out = emit_cadence_calibration(report)
    assert out.startswith("## Cadence calibration")
    assert "every 20 sessions" not in out, (
        "phrasing-check guard: cadence prose uses 'current cadence (N sessions)' shape"
    )
    assert "current cadence (20 sessions)" in out
    assert "<keep at 20 | raise to M | lower to M>" in out


def test_emit_summary_carries_observation_count_footer() -> None:
    report = HealthCheckReport(session_id="S-0102")
    report.fit.add("F1")
    report.gaps.add("G1")
    report.gaps.add("G2")
    report.dead_weight.add("D1")
    report.bloat.add("B1")
    report.mempalace.add("M1")
    out = emit_summary(report)
    assert out.startswith("## Summary")
    assert "_Mechanical-data baseline (script-emitted): 6 observation(s)" in out


def test_emit_summary_zero_observations_is_clean() -> None:
    report = HealthCheckReport(session_id="S-0102")
    out = emit_summary(report)
    assert "0 observation(s)" in out


def test_emit_report_writes_file(synthetic_repo: Path) -> None:
    report = HealthCheckReport(session_id="S-0030")
    report.fit.add("test")
    out_path = emit_report(report)
    assert out_path is not None
    assert out_path.is_file()
    content = out_path.read_text()
    assert "S-0030" in content
    assert "test" in content


def test_emit_report_dry_run(
    synthetic_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = HealthCheckReport(session_id="S-0030")
    report.fit.add("dry-run-test")
    result = emit_report(report, dry_run=True)
    assert result is None
    captured = capsys.readouterr()
    assert "dry-run-test" in captured.out


def test_emit_report_bumps_last_audit_session(synthetic_repo: Path) -> None:
    """emit_report (non-dry-run) bumps register_state.json's last_audit_session.

    Per ADR 0022 Consequences amendment at S-0041: the audit script is the
    canonical "audit happened" producer and so owns the field bump that the
    SessionStart hook + validate.py overdue check both consume.
    """
    register_path = synthetic_repo / "engine" / "session" / "register_state.json"
    register_path.write_text(
        json.dumps(
            {
                "next_id": "0042",
                "last_claimed": "S-0041",
                "current_status": "in_progress",
                "health_check_cadence": 10,
                "last_audit_session": "S-0030",
            }
        )
    )
    report = HealthCheckReport(session_id="S-0041")
    report.fit.add("catchup")
    emit_report(report)
    register = json.loads(register_path.read_text())
    assert register["last_audit_session"] == "S-0041"
    # Cadence and other fields preserved.
    assert register["health_check_cadence"] == 10
    assert register["next_id"] == "0042"


def test_emit_report_bump_creates_field_when_absent(synthetic_repo: Path) -> None:
    """When last_audit_session is absent, emit_report adds it.

    Covers the legacy → new-schema transition: a register_state.json that
    predates the field still gets the bump on the first audit emission.
    """
    register_path = synthetic_repo / "engine" / "session" / "register_state.json"
    register_path.write_text(
        json.dumps(
            {
                "next_id": "0050",
                "last_claimed": "S-0049",
                "current_status": "in_progress",
            }
        )
    )
    report = HealthCheckReport(session_id="S-0050")
    report.fit.add("first-bump")
    emit_report(report)
    register = json.loads(register_path.read_text())
    assert register["last_audit_session"] == "S-0050"


def test_emit_report_dry_run_does_not_bump(synthetic_repo: Path) -> None:
    """Dry-run mode skips the field bump (no report on disk = no audit happened)."""
    register_path = synthetic_repo / "engine" / "session" / "register_state.json"
    register_path.write_text(
        json.dumps(
            {
                "next_id": "0042",
                "last_claimed": "S-0041",
                "current_status": "in_progress",
                "last_audit_session": "S-0030",
            }
        )
    )
    report = HealthCheckReport(session_id="S-0041")
    report.fit.add("dry")
    emit_report(report, dry_run=True)
    register = json.loads(register_path.read_text())
    assert register["last_audit_session"] == "S-0030"


def test_emit_report_bump_handles_absent_register(
    synthetic_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """When register_state.json is absent, emit_report still writes the report
    and surfaces a stderr warning about the failed bump."""
    report = HealthCheckReport(session_id="S-0041")
    report.fit.add("orphan")
    out_path = emit_report(report)
    assert out_path is not None and out_path.is_file()
    captured = capsys.readouterr()
    assert "register_state.json absent" in captured.err
    assert "S-0041" in captured.err


def test_main_bump_only_skips_file_write(
    synthetic_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--bump-only bumps the field without writing/overwriting the report.

    Per Issue #108: when an audit-author hand-writes
    docs/health-checks/S-NNNN.md before invoking the script, the default flow
    overwrites hand-authored prose with the scaffold. --bump-only preserves
    the hand-authored file by skipping the audit pipeline + render entirely.
    """
    register_path = synthetic_repo / "engine" / "session" / "register_state.json"
    register_path.write_text(
        json.dumps(
            {
                "next_id": "0150",
                "last_claimed": "S-0149",
                "current_status": "in_progress",
                "health_check_cadence": 20,
                "last_audit_session": "S-0141",
            }
        )
    )
    report_path = synthetic_repo / "docs" / "health-checks" / "S-0149.md"
    hand_authored = "# Hand-authored audit report\n\nFindings prose preserved.\n"
    report_path.write_text(hand_authored)

    exit_code = main(["--session", "S-0149", "--bump-only"])
    assert exit_code == 0
    assert report_path.read_text() == hand_authored
    register = json.loads(register_path.read_text())
    assert register["last_audit_session"] == "S-0149"
    captured = capsys.readouterr()
    assert "Bumped last_audit_session to S-0149" in captured.out


def test_main_bump_only_bumps_without_existing_report(
    synthetic_repo: Path,
) -> None:
    """--bump-only bumps the field even when no report exists on disk yet.

    The audit-author can run --bump-only before or after the file is in place;
    the field-bump contract is independent of file presence.
    """
    register_path = synthetic_repo / "engine" / "session" / "register_state.json"
    register_path.write_text(
        json.dumps(
            {
                "next_id": "0150",
                "last_claimed": "S-0149",
                "last_audit_session": "S-0141",
            }
        )
    )
    exit_code = main(["--session", "S-0149", "--bump-only"])
    assert exit_code == 0
    register = json.loads(register_path.read_text())
    assert register["last_audit_session"] == "S-0149"


def test_main_bump_only_and_dry_run_mutually_exclusive(
    synthetic_repo: Path,
) -> None:
    """argparse rejects --bump-only + --dry-run combination.

    Mutual exclusion is at the argparse layer (SystemExit with code 2).
    """
    with pytest.raises(SystemExit) as exc_info:
        main(["--session", "S-0149", "--bump-only", "--dry-run"])
    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Cadence detection
# ---------------------------------------------------------------------------


def test_detect_cadence_default(synthetic_repo: Path) -> None:
    # Default tightened from 30 → 10 at S-0033 per ADR 0022 Consequences
    # amendment. The user-direction rationale: too many silent failures
    # accumulated under the 30-session window.
    assert detect_cadence() == 10


def test_detect_cadence_custom(synthetic_repo: Path) -> None:
    register = synthetic_repo / "engine" / "session" / "register_state.json"
    register.write_text(
        json.dumps(
            {
                "next_id": "0030",
                "last_claimed": "S-0029",
                "current_status": "closed",
                "health_check_cadence": 50,
            }
        )
    )
    assert detect_cadence() == 50


def test_detect_cadence_malformed(synthetic_repo: Path) -> None:
    register = synthetic_repo / "engine" / "session" / "register_state.json"
    register.write_text("not valid json")
    # Malformed-fallback default also tightened from 30 → 10 at S-0033.
    assert detect_cadence() == 10


def test_detect_last_check_none(synthetic_repo: Path) -> None:
    assert detect_last_check() is None


def test_detect_last_check_present(synthetic_repo: Path) -> None:
    (synthetic_repo / "docs" / "health-checks" / "S-0030.md").write_text("# Health")
    (synthetic_repo / "docs" / "health-checks" / "S-0060.md").write_text("# Health")
    assert detect_last_check() == "S-0060"


def test_detect_last_check_ignores_template(synthetic_repo: Path) -> None:
    (synthetic_repo / "docs" / "health-checks" / "TEMPLATE.md").write_text("# T")
    (synthetic_repo / "docs" / "health-checks" / "README.md").write_text("# R")
    (synthetic_repo / "docs" / "health-checks" / "S-0030.md").write_text("# H")
    assert detect_last_check() == "S-0030"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_main_writes_report(synthetic_repo: Path) -> None:
    rc = main(["--session", "S-0030"])
    assert rc == 0
    assert (synthetic_repo / "docs" / "health-checks" / "S-0030.md").is_file()


def test_main_invalid_session_id(
    synthetic_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--session", "not-a-session"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "S-NNNN" in captured.err


def test_main_dry_run(synthetic_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--session", "S-0030", "--dry-run"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "S-0030" in captured.out
    # Dry-run should not have written a file.
    assert not (synthetic_repo / "docs" / "health-checks" / "S-0030.md").is_file()


# ---------------------------------------------------------------------------
# MemPalace audit (added at S-0033 per the S-0032 MemPalace audit plan)
# ---------------------------------------------------------------------------


def test_count_adrs_counts_engine_and_product(synthetic_repo: Path) -> None:
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    write_adr(synthetic_repo, engine=True, num="0002", status="Accepted")
    write_adr(synthetic_repo, engine=False, num="0001", status="Accepted")
    assert _count_adrs() == 3


def test_count_adrs_zero_when_dirs_empty(synthetic_repo: Path) -> None:
    assert _count_adrs() == 0


# ---------------------------------------------------------------------------
# audit_mempalace — wing-agnostic SQLite queries (S-0163 per Issue #128)
# ---------------------------------------------------------------------------


def _make_palace_sqlite(palace_dir: Path, rows: list[tuple[str, str]]) -> None:
    """Build a minimal chromadb-shaped sqlite store under ``palace_dir``.

    ``rows`` is a list of ``(key, string_value)`` tuples written into an
    ``embedding_metadata`` table — enough for the room-count and
    document queries `audit_mempalace`'s SQLite helpers read. Not a full
    chromadb store; just the one table those helpers touch.
    """
    palace_dir.mkdir(parents=True, exist_ok=True)
    db = palace_dir / "chroma.sqlite3"
    con = sqlite3.connect(db)
    con.execute(
        "CREATE TABLE embedding_metadata (id INTEGER, key TEXT, string_value TEXT)"
    )
    con.executemany(
        "INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, ?, ?)",
        [(i, k, v) for i, (k, v) in enumerate(rows)],
    )
    con.commit()
    con.close()


def test_room_counts_via_sqlite_spans_all_wings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The room-count query sums a room across every wing — the Issue #128
    fix. The `decisions` room appears under three distinct wings; the
    wing-agnostic GROUP BY returns 5, not the single-wing 2/2/1."""
    palace = tmp_path / "palace"
    # `wing` rows are present but the room query ignores them — the point
    # is that `room=decisions` rows exist regardless of wing.
    _make_palace_sqlite(
        palace,
        [
            ("room", "decisions"),
            ("room", "decisions"),
            ("room", "decisions"),
            ("room", "decisions"),
            ("room", "decisions"),
            ("room", "general"),
            ("wing", "paideia"),
            ("wing", "wing_abc"),
            ("wing", "wing_def"),
        ],
    )
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(palace))
    counts = _room_counts_via_sqlite()
    assert counts == {"decisions": 5, "general": 1}


def test_room_counts_via_sqlite_absent_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A palace path with no chroma.sqlite3 yields None, not a crash."""
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(tmp_path / "nonexistent"))
    assert _room_counts_via_sqlite() is None


def test_drawer_documents_via_sqlite_returns_all_documents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The document query returns every `chroma:document` body, wing-agnostic."""
    palace = tmp_path / "palace"
    _make_palace_sqlite(
        palace,
        [
            ("chroma:document", "[pushback] drawer one"),
            ("chroma:document", "ordinary drawer two"),
            ("room", "decisions"),  # non-document rows excluded
            ("wing", "paideia"),
        ],
    )
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(palace))
    docs = _drawer_documents_via_sqlite()
    assert docs is not None
    assert sorted(docs) == ["[pushback] drawer one", "ordinary drawer two"]


def test_drawer_documents_via_sqlite_absent_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A palace path with no chroma.sqlite3 yields None, not a crash."""
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(tmp_path / "nonexistent"))
    assert _drawer_documents_via_sqlite() is None


def test_audit_mempalace_sqlite_absent(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the chromadb sqlite store is absent, the audit records findings
    naming that condition and still runs the archive-sourced diary check."""
    monkeypatch.setattr(health_check, "_room_counts_via_sqlite", lambda: None)
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: None)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("chromadb sqlite store not found" in obs for obs in obs_texts)
    assert any("not readable for pushback/lesson" in obs for obs in obs_texts)


def test_audit_mempalace_decisions_room_healthy_ratio(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two ADRs, three decisions-room drawers → ratio 1.5 (healthy).
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    write_adr(synthetic_repo, engine=False, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check,
        "_room_counts_via_sqlite",
        lambda: {"decisions": 3, "general": 100},
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: [])
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any(
        "ratio 1.50" in obs and "two-layer recording is healthy" in obs
        for obs in obs_texts
    )


def test_audit_mempalace_decisions_room_low_ratio_flags_gap(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ten ADRs, one decisions-room drawer → ratio 0.1 (gap).
    for n in range(1, 11):
        write_adr(synthetic_repo, engine=True, num=f"{n:04d}", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"decisions": 1}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: [])
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any(
        "significantly below" in obs and "ratio 0.10" in obs for obs in obs_texts
    )


def test_audit_mempalace_decisions_count_sums_across_wings(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The Issue #128 regression guard: a 236-drawer decisions room reported
    as the cross-wing sum, not a single wing's slice. Two ADRs + 236
    decisions drawers → ratio well above 0.9 (healthy), NOT a false gap."""
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    write_adr(synthetic_repo, engine=False, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"decisions": 236}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: [])
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    # 236 / 2 = 118.0 — healthy, not a "significantly below" compliance gap.
    assert any("two-layer recording is healthy" in obs for obs in obs_texts)
    assert not any("significantly below" in obs for obs in obs_texts)


def test_audit_mempalace_tag_filter_excludes_false_positives(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two drawer documents. One is a real pushback drawer with a
    # `Tags: pushback, decision` line. The other mentions "pushback" in
    # the body but has no Tags line or prefix. Only the first counts.
    documents = [
        "# Decision: real pushback moment\nTags: pushback, decision\nBody content here\n",
        "# Operations doc mentioning pushback\nThe pushback convention says ...\n",
    ]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"decisions": 1}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)


def test_audit_mempalace_content_prefix_match_counted(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Issue #55: drawers leading their content with `[pushback]` count.

    No Tags-line on this drawer; the convention is the content prefix.
    """
    documents = [
        "[pushback] AI authored 'correctable in any future session'.\n"
        "User pushback: 'What session will pick up that JSON edit?'\n"
    ]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"problems": 1}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)
    assert any("[pushback]-content-prefix match: 1" in obs for obs in obs_texts)


def test_audit_mempalace_both_forms_deduplicated(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A drawer carrying BOTH Tags-line AND content-prefix counts once."""
    documents = ["[pushback] User pushback content.\nTags: pushback, decision\n"]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"problems": 1}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)


def test_audit_mempalace_prefix_match_case_insensitive_and_whitespace(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[PUSHBACK] (uppercase) and `   [pushback]` (whitespace) both count."""
    documents = [
        "[PUSHBACK] Uppercase variant.\n",
        "   [pushback] Leading-whitespace variant.\n",
    ]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_room_counts_via_sqlite", lambda: {"problems": 2}
    )
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 2" in obs for obs in obs_texts)


def test_audit_mempalace_lesson_tag_extension_parallel_to_pushback(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same bifurcated counting applies to the lesson convention."""
    documents = [
        "[pushback] real pushback.\n",
        "[lesson] real lesson content.\nTags: lesson, project\n",
        "[LESSON] uppercase lesson without Tags-line.\n",
    ]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(health_check, "_room_counts_via_sqlite", lambda: {"lessons": 2})
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`lesson`-tagged drawers in MemPalace: 2" in obs for obs in obs_texts)


def test_audit_mempalace_neither_form_excluded(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A drawer mentioning `pushback` mid-body without a Tags-line or prefix
    is not counted — the false-positive guard is preserved."""
    documents = [
        "Some operations doc that describes the pushback convention\n"
        "in a paragraph but never tags or prefixes itself.\n"
    ]
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(health_check, "_room_counts_via_sqlite", lambda: {"general": 1})
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: documents)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("No drawers tagged `pushback`" in obs for obs in obs_texts)


def test_audit_mempalace_diary_calibration_when_no_field_present(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Archives without diary_skipped key → calibration window message.
    write_archive(synthetic_repo, "S-0030", soft_warns={"adr_back_reference_orphan": 0})
    write_archive(synthetic_repo, "S-0031", soft_warns={"adr_back_reference_orphan": 1})
    monkeypatch.setattr(health_check, "_room_counts_via_sqlite", lambda: None)
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: None)
    findings = audit_mempalace(list_archives())
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("calibration window" in obs for obs in obs_texts)


def test_audit_mempalace_diary_high_skip_rate(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Three of four archives have diary_skipped=1 → 75% skip rate.
    for sid, skipped in (("S-0033", 1), ("S-0034", 1), ("S-0035", 0), ("S-0036", 1)):
        write_archive(synthetic_repo, sid, soft_warns={"diary_skipped": skipped})
    monkeypatch.setattr(health_check, "_room_counts_via_sqlite", lambda: None)
    monkeypatch.setattr(health_check, "_drawer_documents_via_sqlite", lambda: None)
    findings = audit_mempalace(list_archives())
    obs_texts = [obs for obs, _ in findings.observations]
    # Skip rate: 3/4 = 75%
    assert any("Diary skip rate: 3/4" in obs and "75%" in obs for obs in obs_texts)


def test_render_report_audit_mempalace_data_flows_into_accumulated_section(
    synthetic_repo: Path,
) -> None:
    """audit_mempalace observations flow into the Accumulated pushbacks and
    lessons section per the S-0102 refactor (Issue #53). The old standalone
    ## MemPalace section is retired in favor of folding mempalace data
    under TEMPLATE.md's pushback/lesson section per ADR 0057."""
    report = HealthCheckReport(session_id="S-0033")
    report.mempalace.add("MemPalace stub finding", "test action")
    rendered = render_report(report)
    assert "## Accumulated pushbacks and lessons" in rendered
    assert "Mechanical observations from `audit_mempalace()`:" in rendered
    assert "MemPalace stub finding" in rendered
    # Old standalone section is retired.
    assert "## MemPalace\n" not in rendered
    assert "Is the project's semantic-memory layer in healthy use?" not in rendered
