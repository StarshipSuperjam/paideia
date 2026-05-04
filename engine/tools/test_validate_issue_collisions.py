"""Tests for validate_issue_collisions (per ADR 0048).

Wrapper-layer tests: the underlying scanner is unit-tested in
test_scan_issue_collisions.py. These tests cover the wrapper's
exit-code-to-soft-warn translation and missing-scanner posture.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402


class _FakeProc:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_clean_when_scanner_exits_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "validate.subprocess.run",
        lambda *a, **kw: _FakeProc(returncode=0),
    )
    r = validate.validate_issue_collisions()
    assert "issue_collision" in r.checks_run
    assert r.soft_warns == {}
    assert r.hard_fails == []


def test_soft_warn_per_collision_when_scanner_exits_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = (
        '[scan-issue-collisions] Open issue #1 "Wing-filter bug" appears '
        "to touch this session's scope: handoff.\n"
        '[scan-issue-collisions] Open issue #2 "Wing-naming bug" appears '
        "to touch this session's scope: context.\n"
    )
    monkeypatch.setattr(
        "validate.subprocess.run",
        lambda *a, **kw: _FakeProc(returncode=1, stderr=stderr),
    )
    r = validate.validate_issue_collisions()
    assert "issue_collision" in r.soft_warns
    assert len(r.soft_warns["issue_collision"]) == 2
    # Body should be stripped of the [scan-issue-collisions] prefix.
    body = r.soft_warns["issue_collision"][0]
    assert not body.startswith("[scan-issue-collisions]")
    assert "#1" in body or "#2" in body


def test_soft_warn_on_missing_scanner(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When the scanner script doesn't exist, a single soft-warn fires."""
    monkeypatch.setattr(validate, "SCAN_ISSUE_COLLISIONS", tmp_path / "nonexistent.py")
    r = validate.validate_issue_collisions()
    assert "issue_collision" in r.soft_warns
    body = r.soft_warns["issue_collision"][0]
    assert "missing" in body.lower()


def test_unexpected_exit_code_surfaces_as_soft_warn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exit codes other than 0 or 1 surface as soft-warn (defensive)."""
    monkeypatch.setattr(
        "validate.subprocess.run",
        lambda *a, **kw: _FakeProc(returncode=99, stderr="something broke"),
    )
    r = validate.validate_issue_collisions()
    assert "issue_collision" in r.soft_warns
    body = r.soft_warns["issue_collision"][0]
    assert "exited 99" in body
