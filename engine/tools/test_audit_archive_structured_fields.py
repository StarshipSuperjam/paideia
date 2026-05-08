"""Tests for audit_archive_structured_fields.py.

Origin: Issue #13 (S-0055) — single-field audit for outcome_summary_soft_warns.
Extended at S-0078: parameterized to declarative REQUIRED_ARCHIVE_FIELDS;
added archive-history mode (closes Issue #20).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_archive_structured_fields import (  # noqa: E402
    REQUIRED_ARCHIVE_FIELDS,
    applicable_fields,
    archive_history_report,
    main,
    parse_session_id,
    shape_check,
)


def make_full_payload(
    session_id: str = "S-0078", **overrides: object
) -> dict[str, object]:
    """Build a payload that satisfies every applicable required field.

    Tests use this as a default and override specific fields to test
    individual failure modes.
    """
    payload: dict[str, object] = {
        "id": session_id,
        "outcome_summary_soft_warns": {},
        "mode": "interactive",
        "mempalace_activity": {
            "search_calls": 0,
            "diary_read_calls": 0,
            "diary_write_calls": 0,
            "add_drawer_calls": 0,
            "status_calls": 0,
            "list_drawers_calls": 0,
            "other_calls": 0,
            "total_calls": 0,
            "first_call_ts": None,
            "last_call_ts": None,
        },
    }
    payload.update(overrides)
    return payload


def write_current(tmp_path: Path, payload: dict[str, object]) -> Path:
    """Write a current.json fixture and return its path."""
    p = tmp_path / "current.json"
    p.write_text(json.dumps(payload))
    return p


# ----- declarative field set --------------------------------------------------


def test_required_fields_are_well_formed() -> None:
    """Every row in REQUIRED_ARCHIVE_FIELDS has the expected keys."""
    for row in REQUIRED_ARCHIVE_FIELDS:
        assert "field" in row
        assert "since_session" in row
        assert "shape" in row
        assert "adr" in row
        assert parse_session_id(row["since_session"]) is not None
        assert row["shape"] in ("dict", "str", "int", "list", "str_or_null")


def test_parse_session_id_well_formed() -> None:
    assert parse_session_id("S-0078") == 78
    assert parse_session_id("S-0001") == 1
    assert parse_session_id("S-9999") == 9999


def test_parse_session_id_malformed() -> None:
    assert parse_session_id(None) is None
    assert parse_session_id("") is None
    assert parse_session_id("x-0078") is None
    assert parse_session_id("S-78") is None  # not 4-digit
    assert parse_session_id("S-00789") is None
    assert parse_session_id(78) is None  # type: ignore[arg-type]


def test_applicable_fields_filters_by_session_vintage() -> None:
    """Old session id only triggers fields whose since_session is <=."""
    # S-0030 — none of the current fields are required yet
    rows = applicable_fields(30)
    assert len(rows) == 0

    # S-0050 — mode (since 48) is required, others are not
    rows = applicable_fields(50)
    fields = {r["field"] for r in rows}
    assert "mode" in fields
    assert "outcome_summary_soft_warns" not in fields
    assert "mempalace_activity" not in fields
    assert "next_session_handle" not in fields

    # S-0078 — first three fields required; next_session_handle (since S-0100) is not
    rows = applicable_fields(78)
    fields = {r["field"] for r in rows}
    assert "mode" in fields
    assert "outcome_summary_soft_warns" in fields
    assert "mempalace_activity" in fields
    assert "next_session_handle" not in fields

    # S-0100 onward — every current field is required including next_session_handle
    rows = applicable_fields(100)
    fields = {r["field"] for r in rows}
    assert "mode" in fields
    assert "outcome_summary_soft_warns" in fields
    assert "mempalace_activity" in fields
    assert "next_session_handle" in fields


def test_applicable_fields_unknown_session_returns_all() -> None:
    """Defensive — unparseable id triggers every check."""
    rows = applicable_fields(None)
    assert len(rows) == len(REQUIRED_ARCHIVE_FIELDS)


def test_shape_check_dict() -> None:
    assert shape_check({}, "dict") is None
    assert shape_check({"x": 1}, "dict") is None
    assert shape_check([], "dict") is not None
    assert shape_check("nope", "dict") is not None
    assert shape_check(None, "dict") is not None


def test_shape_check_str() -> None:
    assert shape_check("interactive", "str") is None
    assert shape_check("", "str") is None  # empty string is the right shape
    assert shape_check(None, "str") is not None
    assert shape_check(42, "str") is not None


def test_shape_check_unknown_shape() -> None:
    """Audit-bug detection — bad expected value reported, not silently ignored."""
    err = shape_check({}, "tuple")
    assert err is not None
    assert "audit bug" in err


# ----- str_or_null shape (S-0100, ADR 0049 Decision 6) ------------------------


def test_shape_check_str_or_null_accepts_str() -> None:
    """Standard string value passes."""
    assert shape_check("#54", "str_or_null") is None
    assert shape_check("S-0123", "str_or_null") is None
    assert shape_check("", "str_or_null") is None  # empty string is shape-correct


def test_shape_check_str_or_null_accepts_null() -> None:
    """None is the load-bearing 'explicit no defer' semantic."""
    assert shape_check(None, "str_or_null") is None


def test_shape_check_str_or_null_rejects_other_types() -> None:
    """Numbers, lists, dicts are not valid."""
    assert shape_check(42, "str_or_null") is not None
    assert shape_check([], "str_or_null") is not None
    assert shape_check({"x": 1}, "str_or_null") is not None
    err = shape_check(42, "str_or_null")
    assert err is not None
    assert "expected str or null" in err


# ----- in-flight mode (default) -----------------------------------------------


def test_field_present_non_empty_passes(tmp_path: Path) -> None:
    """Standard happy path — every required field with valid content."""
    p = write_current(
        tmp_path,
        make_full_payload(outcome_summary_soft_warns={"issue_collision": 6}),
    )
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_field_present_empty_dict_passes(tmp_path: Path) -> None:
    """Empty dict is the legitimate 'clean session' shape."""
    p = write_current(tmp_path, make_full_payload(outcome_summary_soft_warns={}))
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_outcome_summary_field_absent_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing key — the lapse pattern from S-0043 through S-0047."""
    payload = make_full_payload()
    del payload["outcome_summary_soft_warns"]
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "outcome_summary_soft_warns" in err
    assert "missing" in err.lower()


def test_mode_field_absent_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing `mode` — the S-0065/S-0069 pattern Issue #20 escalated."""
    payload = make_full_payload()
    del payload["mode"]
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "mode" in err
    assert "missing" in err.lower()


def test_mempalace_activity_field_absent_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing `mempalace_activity` — the new S-0078-forward field."""
    payload = make_full_payload()
    del payload["mempalace_activity"]
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "mempalace_activity" in err


def test_field_null_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Null is a placeholder, not a value."""
    p = write_current(tmp_path, make_full_payload(outcome_summary_soft_warns=None))
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "null" in err.lower()


def test_field_wrong_type_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A list (or any non-dict) is malformed."""
    p = write_current(
        tmp_path,
        make_full_payload(outcome_summary_soft_warns=["wrong", "shape"]),
    )
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "expected dict" in err


def test_mode_wrong_type_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`mode` must be a string, not a dict."""
    p = write_current(tmp_path, make_full_payload(mode={"this": "wrong"}))
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "expected str" in err


def test_next_session_handle_field_absent_hard_fails_at_s0100(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing `next_session_handle` on S-0100+ archive — Issue #54 closure."""
    payload = make_full_payload(session_id="S-0100")
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "next_session_handle" in err
    assert "missing" in err.lower()


def test_next_session_handle_null_passes_at_s0100(tmp_path: Path) -> None:
    """Explicit null is the load-bearing 'no defer' semantic; passes."""
    payload = make_full_payload(session_id="S-0100", next_session_handle=None)
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_next_session_handle_string_passes_at_s0100(tmp_path: Path) -> None:
    """An issue-handle string passes the shape audit."""
    payload = make_full_payload(session_id="S-0100", next_session_handle="#54")
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_next_session_handle_wrong_type_hard_fails_at_s0100(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An int (or any non-string non-null) is malformed at the shape layer."""
    payload = make_full_payload(session_id="S-0100", next_session_handle=42)
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "next_session_handle" in err
    assert "expected str or null" in err


def test_old_session_skips_new_fields(tmp_path: Path) -> None:
    """A vintage S-0030 archive shouldn't trigger any field check."""
    p = write_current(tmp_path, {"id": "S-0030"})
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_mid_vintage_session_only_checks_applicable_fields(tmp_path: Path) -> None:
    """An S-0050 archive only needs `mode` (others' since_session > 50)."""
    payload: dict[str, object] = {"id": "S-0050", "mode": "interactive"}
    p = write_current(tmp_path, payload)
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_missing_file_passes(tmp_path: Path) -> None:
    """No in-flight session (no current.json) — nothing to audit."""
    nonexistent = tmp_path / "missing.json"
    rc = main(["--current-path", str(nonexistent), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_malformed_json_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Garbage in current.json — fail loudly rather than silently passing."""
    p = tmp_path / "current.json"
    p.write_text("{ not valid json")
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "not valid JSON" in err


def test_advisory_fires_when_empty_with_many_commits(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Empty dict + >= 3 commits since eager-claim → soft advisory (still passes)."""
    p = write_current(tmp_path, make_full_payload(outcome_summary_soft_warns={}))
    with mock.patch(
        "audit_archive_structured_fields.session_commit_count", return_value=5
    ):
        rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "advisory" in err
    assert "5 commits" in err


def test_no_advisory_when_empty_with_few_commits(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Empty dict + only the eager-claim commit → no advisory."""
    p = write_current(tmp_path, make_full_payload(outcome_summary_soft_warns={}))
    with mock.patch(
        "audit_archive_structured_fields.session_commit_count", return_value=1
    ):
        rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "advisory" not in err


def test_from_stdin_passes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Reading via --from-stdin works for the closing-commit hook path."""
    import io

    payload = json.dumps(make_full_payload(outcome_summary_soft_warns={"x": 1}))
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    rc = main(["--from-stdin", "--repo-root", str(tmp_path)])
    assert rc == 0


def test_from_stdin_hard_fails_when_field_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Stdin mode hard-fails on missing field — closing commit blocked."""
    import io

    payload = json.dumps({"id": "S-0078", "mode": "interactive"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    rc = main(["--from-stdin", "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "stdin is missing" in err


# ----- archive-history mode (Issue #20 closure) -------------------------------


def test_archive_history_no_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A clean archive directory yields zero findings in the report."""
    archive_dir = tmp_path / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    archive_dir.joinpath("S-0078.json").write_text(json.dumps(make_full_payload()))

    rc = main(["--archive-history", "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Archive-history audit" in out
    assert "no findings" in out


def test_archive_history_reports_missing_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Archive missing a required field shows up in the report."""
    archive_dir = tmp_path / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    payload = make_full_payload(session_id="S-0078")
    del payload["mempalace_activity"]
    archive_dir.joinpath("S-0078.json").write_text(json.dumps(payload))

    rc = main(["--archive-history", "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "S-0078.json" in out
    assert "mempalace_activity" in out
    assert "missing" in out.lower()


def test_archive_history_skips_old_archives(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Archives older than a field's since_session don't generate findings."""
    archive_dir = tmp_path / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    # S-0030 archive — none of the structured fields were required yet
    archive_dir.joinpath("S-0030.json").write_text(json.dumps({"id": "S-0030"}))

    rc = main(["--archive-history", "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "no findings" in out


def test_archive_history_handles_unparseable_archive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Malformed archive files report as 'could not read or parse'."""
    archive_dir = tmp_path / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    archive_dir.joinpath("S-0078.json").write_text("{ not valid json")

    rc = main(["--archive-history", "--repo-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "could not read or parse" in out


def test_archive_history_report_lists_field_set(tmp_path: Path) -> None:
    """The report ends with the field-set declaration so readers see it."""
    archive_dir = tmp_path / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    out = archive_history_report(archive_dir)
    assert "Field set audited" in out
    for row in REQUIRED_ARCHIVE_FIELDS:
        assert row["field"] in out
        assert row["since_session"] in out


def test_archive_history_no_archive_dir(tmp_path: Path) -> None:
    """Archive-history mode tolerates a missing archive directory."""
    out = archive_history_report(tmp_path / "no-such-dir")
    assert "no archive directory" in out
