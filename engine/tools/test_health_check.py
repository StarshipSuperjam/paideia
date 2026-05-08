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
import shutil
import subprocess
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
    _resolve_mempalace_binary,
    _run_mempalace,
    audit_bloat,
    audit_dead_weight,
    audit_fit,
    audit_gaps,
    audit_mempalace,
    detect_cadence,
    detect_last_check,
    emit_report,
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
    report = HealthCheckReport(session_id="S-0030")
    report.fit.add("F1")
    report.gaps.add("G1")
    report.dead_weight.add("D1")
    report.bloat.add("B1")
    rendered = render_report(report)
    assert "# Health Check S-0030" in rendered
    assert "## Fit" in rendered
    assert "## Gaps" in rendered
    assert "## Dead weight" in rendered
    assert "## Bloat" in rendered
    assert "## Cadence calibration" in rendered
    assert "## Summary" in rendered
    assert "F1" in rendered and "G1" in rendered
    assert "D1" in rendered and "B1" in rendered


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


def test_resolve_mempalace_binary_returns_none_when_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Force shutil.which to miss and the home-fallback path to point at
    # nothing executable.
    monkeypatch.setattr(shutil, "which", lambda _: None)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert _resolve_mempalace_binary() is None


def test_resolve_mempalace_binary_prefers_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/mempalace")
    assert _resolve_mempalace_binary() == "/usr/bin/mempalace"


def test_resolve_mempalace_binary_falls_back_to_user_scope(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Build an executable file at the user-scope fallback path.
    fallback_dir = tmp_path / "Library" / "Python" / "3.9" / "bin"
    fallback_dir.mkdir(parents=True)
    fallback_file = fallback_dir / "mempalace"
    fallback_file.write_text("#!/bin/sh\necho test")
    fallback_file.chmod(0o755)
    monkeypatch.setattr(shutil, "which", lambda _: None)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert _resolve_mempalace_binary() == str(fallback_file)


def test_run_mempalace_returns_stdout_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResult:
        returncode = 0
        stdout = "drawer count: 42"

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
    assert _run_mempalace("/fake/mempalace", "status") == "drawer count: 42"


def test_run_mempalace_returns_none_on_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResult:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
    assert _run_mempalace("/fake/mempalace", "status") is None


def test_run_mempalace_returns_none_on_subprocess_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_error(*args: Any, **kwargs: Any) -> None:
        raise OSError("simulated")

    monkeypatch.setattr(subprocess, "run", raise_error)
    assert _run_mempalace("/fake/mempalace", "status") is None


def test_audit_mempalace_when_binary_absent(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(health_check, "_resolve_mempalace_binary", lambda: None)
    findings = audit_mempalace([])
    # One observation naming the missing-CLI condition.
    assert len(findings.observations) == 1
    obs, _action = findings.observations[0]
    assert "MemPalace CLI not on PATH" in obs


def test_audit_mempalace_status_failure(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", lambda *a, **kw: None)
    findings = audit_mempalace([])
    # Status-failure finding plus per-tag failures plus diary-calibration finding.
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("mempalace status returned no output" in obs for obs in obs_texts)


def test_audit_mempalace_decisions_room_healthy_ratio(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two ADRs, three decisions-room drawers → ratio 1.5 (healthy).
    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    write_adr(synthetic_repo, engine=False, num="0001", status="Accepted")
    status_output = (
        "MemPalace Status\n"
        "  WING: paideia\n"
        "    ROOM: decisions    3 drawers\n"
        "    ROOM: general    100 drawers\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return status_output
        # Empty body for tag searches → no `Tags:` lines, so 0 tagged drawers.
        return ""

    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
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
    status_output = "  WING: paideia\n    ROOM: decisions    1 drawers\n"
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(
        health_check,
        "_run_mempalace",
        lambda binary, *args: status_output if args == ("status",) else "",
    )
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any(
        "significantly below" in obs and "ratio 0.10" in obs for obs in obs_texts
    )


def test_audit_mempalace_tag_filter_excludes_false_positives(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Search returns two results. One is a real pushback drawer with a
    # `Tags: pushback, decision` line. The other mentions "pushback" in
    # the body but has no Tags line — operations doc that *describes*
    # the convention. Only the first should count.
    search_output = (
        "  [1] paideia / decisions\n"
        "    # Decision: real pushback moment\n"
        "    Tags: pushback, decision\n"
        "    Body content here\n"
        "\n"
        "  [2] paideia / operations\n"
        "    # Operations doc mentioning pushback\n"
        "    The pushback convention says ...\n"
        "    Body content here\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: decisions    1 drawers\n"
        if "pushback" in args:
            return search_output
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    # Should report exactly 1 pushback drawer (not 2 from raw search count).
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)


def test_audit_mempalace_content_prefix_match_counted(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Issue #55: drawers leading their content with `[pushback]` count.

    No Tags-line on this drawer; the convention is the content prefix.
    Pre-S-0099 audit_mempalace() reported 0 here despite the substantive
    drawer; this test asserts the new content-prefix path catches it.
    """
    search_output = (
        "  [1] paideia / problems\n"
        "    [pushback] AI authored 'correctable in any future session'.\n"
        "    User pushback: 'What session will pick up that JSON edit?'\n"
        "\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: problems    1 drawers\n"
        if "pushback" in args:
            return search_output
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)
    assert any("[pushback]-content-prefix match: 1" in obs for obs in obs_texts)


def test_audit_mempalace_both_forms_deduplicated(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A drawer carrying BOTH Tags-line AND content-prefix counts once."""
    search_output = (
        "  [1] paideia / problems\n"
        "    [pushback] User pushback content.\n"
        "    Tags: pushback, decision\n"
        "\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: problems    1 drawers\n"
        if "pushback" in args:
            return search_output
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 1" in obs for obs in obs_texts)


def test_audit_mempalace_prefix_match_case_insensitive_and_whitespace(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[PUSHBACK] (uppercase) and `   [pushback]` (whitespace) both count."""
    search_output = (
        "  [1] paideia / problems\n"
        "    [PUSHBACK] Uppercase variant.\n"
        "\n"
        "  [2] paideia / problems\n"
        "       [pushback] Leading-whitespace variant.\n"
        "\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: problems    2 drawers\n"
        if "pushback" in args:
            return search_output
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`pushback`-tagged drawers in MemPalace: 2" in obs for obs in obs_texts)


def test_audit_mempalace_lesson_tag_extension_parallel_to_pushback(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same bifurcated counting applies to the lesson convention."""
    pushback_search = "  [1] paideia / problems\n    [pushback] real pushback.\n\n"
    lesson_search = (
        "  [1] paideia / lessons\n"
        "    [lesson] real lesson content.\n"
        "    Tags: lesson, project\n"
        "\n"
        "  [2] paideia / lessons\n"
        "    [LESSON] uppercase lesson without Tags-line.\n"
        "\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: lessons    2 drawers\n"
        if "pushback" in args:
            return pushback_search
        if "lesson" in args:
            return lesson_search
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("`lesson`-tagged drawers in MemPalace: 2" in obs for obs in obs_texts)


def test_audit_mempalace_neither_form_excluded(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A block mentioning `pushback` mid-body without Tags-line or prefix
    is not counted — the false-positive guard from the original heuristic
    is preserved alongside the new content-prefix path."""
    search_output = (
        "  [1] paideia / general\n"
        "    Some operations doc that describes the pushback convention\n"
        "    in a paragraph but never tags or prefixes itself.\n"
        "\n"
    )

    def fake_run(binary: str, *args: str) -> str | None:
        if args == ("status",):
            return "  WING: paideia\n    ROOM: general    1 drawers\n"
        if "pushback" in args:
            return search_output
        return ""

    write_adr(synthetic_repo, engine=True, num="0001", status="Accepted")
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", fake_run)
    findings = audit_mempalace([])
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("No drawers tagged `pushback`" in obs for obs in obs_texts)


def test_audit_mempalace_diary_calibration_when_no_field_present(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Archives without diary_skipped key → calibration window message.
    write_archive(synthetic_repo, "S-0030", soft_warns={"adr_back_reference_orphan": 0})
    write_archive(synthetic_repo, "S-0031", soft_warns={"adr_back_reference_orphan": 1})
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", lambda *a, **kw: None)
    findings = audit_mempalace(list_archives())
    obs_texts = [obs for obs, _ in findings.observations]
    assert any("calibration window" in obs for obs in obs_texts)


def test_audit_mempalace_diary_high_skip_rate(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Three of four archives have diary_skipped=1 → 75% skip rate.
    for sid, skipped in (("S-0033", 1), ("S-0034", 1), ("S-0035", 0), ("S-0036", 1)):
        write_archive(synthetic_repo, sid, soft_warns={"diary_skipped": skipped})
    monkeypatch.setattr(
        health_check, "_resolve_mempalace_binary", lambda: "/fake/mempalace"
    )
    monkeypatch.setattr(health_check, "_run_mempalace", lambda *a, **kw: None)
    findings = audit_mempalace(list_archives())
    obs_texts = [obs for obs, _ in findings.observations]
    # Skip rate: 3/4 = 75%
    assert any("Diary skip rate: 3/4" in obs and "75%" in obs for obs in obs_texts)


def test_render_report_includes_mempalace_section(
    synthetic_repo: Path,
) -> None:
    report = HealthCheckReport(session_id="S-0033")
    report.mempalace.add("MemPalace stub finding", "test action")
    rendered = render_report(report)
    assert "## MemPalace" in rendered
    assert "MemPalace stub finding" in rendered
    # Section intro from render_report.
    assert "Is the project's semantic-memory layer in healthy use?" in rendered
