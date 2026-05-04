"""Tests for audit_archive_structured_fields.py — Issue #13 (S-0055)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_archive_structured_fields import main  # noqa: E402


def write_current(tmp_path: Path, payload: dict[str, object]) -> Path:
    """Write a current.json fixture and return its path."""
    p = tmp_path / "current.json"
    p.write_text(json.dumps(payload))
    return p


def test_field_present_non_empty_passes(tmp_path: Path) -> None:
    """Standard happy path — field with one or more categories."""
    p = write_current(
        tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": {"issue_collision": 6}}
    )
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_field_present_empty_dict_passes(tmp_path: Path) -> None:
    """Empty dict is the legitimate 'clean session, no warnings' shape."""
    p = write_current(tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": {}})
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 0


def test_field_absent_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing key — the lapse pattern from S-0043 through S-0047."""
    p = write_current(tmp_path, {"id": "S-0055"})
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "outcome_summary_soft_warns" in err
    assert "missing" in err.lower()


def test_field_null_hard_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Null is a placeholder, not a value."""
    p = write_current(tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": None})
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
        tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": ["wrong", "shape"]}
    )
    rc = main(["--current-path", str(p), "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HARD-FAIL" in err
    assert "expected dict" in err


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
    p = write_current(tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": {}})
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
    p = write_current(tmp_path, {"id": "S-0055", "outcome_summary_soft_warns": {}})
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

    payload = json.dumps({"id": "S-0055", "outcome_summary_soft_warns": {"x": 1}})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    rc = main(["--from-stdin", "--repo-root", str(tmp_path)])
    assert rc == 0


def test_from_stdin_hard_fails_when_field_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Stdin mode hard-fails on missing field — closing commit blocked."""
    import io

    payload = json.dumps({"id": "S-0055"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    rc = main(["--from-stdin", "--repo-root", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "stdin is missing" in err
