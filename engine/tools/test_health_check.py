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
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import health_check  # noqa: E402
from health_check import (  # noqa: E402
    CategoryFindings,
    HealthCheckReport,
    audit_bloat,
    audit_dead_weight,
    audit_fit,
    audit_gaps,
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
    ideation, operations dir, report dir. Each starts empty; tests populate
    as needed.
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
        health_check, "IDEATION_PATH", tmp_path / "product" / "docs" / "ideation.md"
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
    assert any("no inbound citations" in obs for obs, _ in findings.observations)


def test_audit_dead_weight_cited_ops_doc(synthetic_repo: Path) -> None:
    (synthetic_repo / "engine" / "operations" / "popular.md").write_text("# Popular\n")
    (synthetic_repo / "README.md").write_text(
        "See engine/operations/popular.md for details.\n"
    )
    findings = audit_dead_weight()
    # Should not flag popular.md as uncited.
    for obs, _ in findings.observations:
        assert "popular.md" not in obs or "no inbound" not in obs


def test_audit_dead_weight_unconsumed_ideation(synthetic_repo: Path) -> None:
    (synthetic_repo / "product" / "docs" / "ideation.md").write_text(
        "# Ideation\n\n## Idea A\n\nSome thought.\n\n## Idea B\n\nConsumed: 2026-04-01.\n"
    )
    findings = audit_dead_weight()
    obs_text = " ".join(obs for obs, _ in findings.observations)
    assert "Idea A" in obs_text
    assert "Idea B" not in obs_text


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


# ---------------------------------------------------------------------------
# Cadence detection
# ---------------------------------------------------------------------------


def test_detect_cadence_default(synthetic_repo: Path) -> None:
    assert detect_cadence() == 30


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
    assert detect_cadence() == 30


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
