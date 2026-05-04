"""Tests for engine/tools/scan_issue_backlog.py.

Tests are pure-function — gh subprocess is monkey-patched so the suite
runs without network or auth state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_issue_backlog import (  # noqa: E402
    collect_urgent,
    count_by_label,
    fetch_open_issues,
    format_fyi_line,
    format_loud_block,
    label_names,
    main,
)


# ---------------------------------------------------------------------------
# label_names
# ---------------------------------------------------------------------------


def test_label_names_extracts_name_field() -> None:
    issue = {"labels": [{"name": "bug"}, {"name": "upstream"}]}
    assert label_names(issue) == ["bug", "upstream"]


def test_label_names_handles_missing_labels_field() -> None:
    assert label_names({}) == []


def test_label_names_skips_non_dict_entries() -> None:
    issue = {"labels": [{"name": "bug"}, "not-a-dict", {"name": "tech-debt"}]}
    assert label_names(issue) == ["bug", "tech-debt"]


def test_label_names_handles_label_without_name() -> None:
    issue = {"labels": [{"color": "red"}, {"name": "bug"}]}
    assert label_names(issue) == ["", "bug"]


# ---------------------------------------------------------------------------
# count_by_label
# ---------------------------------------------------------------------------


def test_count_by_label_zero_when_empty() -> None:
    counts = count_by_label([])
    assert counts == {
        "bug": 0,
        "tech-debt": 0,
        "cleanup": 0,
        "enhancement": 0,
        "health-check-finding": 0,
        "upstream": 0,
    }


def test_count_by_label_counts_each_canonical_label() -> None:
    issues = [
        {"labels": [{"name": "bug"}]},
        {"labels": [{"name": "bug"}, {"name": "upstream"}]},
        {"labels": [{"name": "cleanup"}]},
        {"labels": [{"name": "enhancement"}]},
        {"labels": [{"name": "tech-debt"}]},
        {"labels": [{"name": "health-check-finding"}]},
    ]
    counts = count_by_label(issues)
    assert counts["bug"] == 2
    assert counts["upstream"] == 1
    assert counts["cleanup"] == 1
    assert counts["enhancement"] == 1
    assert counts["tech-debt"] == 1
    assert counts["health-check-finding"] == 1


def test_count_by_label_ignores_non_canonical_labels() -> None:
    issues = [{"labels": [{"name": "bug"}, {"name": "wontfix"}]}]
    counts = count_by_label(issues)
    assert counts["bug"] == 1
    # No KeyError for wontfix; not in TYPE_LABELS so silently dropped.
    assert "wontfix" not in counts


# ---------------------------------------------------------------------------
# collect_urgent
# ---------------------------------------------------------------------------


def test_collect_urgent_filters_by_priority_label() -> None:
    issues = [
        {"number": 1, "labels": [{"name": "bug"}]},
        {"number": 2, "labels": [{"name": "bug"}, {"name": "priority:urgent"}]},
        {"number": 3, "labels": [{"name": "priority:urgent"}]},
    ]
    urgent = collect_urgent(issues)
    assert [i["number"] for i in urgent] == [2, 3]


def test_collect_urgent_empty_when_no_urgent() -> None:
    issues = [{"number": 1, "labels": [{"name": "bug"}]}]
    assert collect_urgent(issues) == []


# ---------------------------------------------------------------------------
# format_fyi_line
# ---------------------------------------------------------------------------


def test_format_fyi_line_zero_counts() -> None:
    counts = {
        "bug": 0,
        "tech-debt": 0,
        "cleanup": 0,
        "enhancement": 0,
        "health-check-finding": 0,
        "upstream": 0,
    }
    line = format_fyi_line(counts, urgent_count=0)
    assert line == (
        "[session-start] Issues backlog: 0 bugs, 0 tech-debt, 0 cleanup, "
        "0 enhancement (0 urgent)."
    )


def test_format_fyi_line_with_counts_and_urgent() -> None:
    counts = {
        "bug": 3,
        "tech-debt": 7,
        "cleanup": 12,
        "enhancement": 2,
        "health-check-finding": 0,
        "upstream": 1,
    }
    line = format_fyi_line(counts, urgent_count=1)
    assert "3 bugs" in line
    assert "7 tech-debt" in line
    assert "12 cleanup" in line
    assert "2 enhancement" in line
    assert "(1 urgent)" in line


# ---------------------------------------------------------------------------
# format_loud_block
# ---------------------------------------------------------------------------


def test_format_loud_block_lists_each_urgent() -> None:
    urgent = [
        {
            "number": 7,
            "title": "Repo on fire",
            "labels": [{"name": "bug"}, {"name": "priority:urgent"}],
        },
        {
            "number": 9,
            "title": "Other thing",
            "labels": [{"name": "tech-debt"}, {"name": "priority:urgent"}],
        },
    ]
    lines = format_loud_block(urgent)
    body = "\n".join(lines)
    assert "URGENT: 2 open issue(s)" in body
    assert "#7: Repo on fire" in body
    assert "#9: Other thing" in body
    # Non-priority labels surface in the per-issue brackets.
    assert "[bug]" in body
    assert "[tech-debt]" in body
    # The literal label string `priority:urgent` does not appear in
    # the per-issue brackets (only mentioned in the heading prose).
    assert "[priority:urgent]" not in body
    assert "priority:urgent]" not in body


def test_format_loud_block_handles_no_non_priority_labels() -> None:
    urgent = [
        {
            "number": 1,
            "title": "Only urgent",
            "labels": [{"name": "priority:urgent"}],
        },
    ]
    lines = format_loud_block(urgent)
    body = "\n".join(lines)
    assert "#1: Only urgent" in body
    # No trailing label bracket when none survives the filter.
    assert "#1: Only urgent\n" in body + "\n" or "#1: Only urgent$" in body


# ---------------------------------------------------------------------------
# fetch_open_issues
# ---------------------------------------------------------------------------


def test_fetch_open_issues_returns_none_on_gh_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FailingProc:
        returncode = 1
        stdout = ""
        stderr = "auth required"

    def fake_run(*args: object, **kwargs: object) -> _FailingProc:
        return _FailingProc()

    monkeypatch.setattr("scan_issue_backlog.subprocess.run", fake_run)
    assert fetch_open_issues() is None


def test_fetch_open_issues_returns_none_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _BadJsonProc:
        returncode = 0
        stdout = "not-valid-json"
        stderr = ""

    def fake_run(*args: object, **kwargs: object) -> _BadJsonProc:
        return _BadJsonProc()

    monkeypatch.setattr("scan_issue_backlog.subprocess.run", fake_run)
    assert fetch_open_issues() is None


def test_fetch_open_issues_returns_parsed_list(monkeypatch: pytest.MonkeyPatch) -> None:
    class _OkProc:
        returncode = 0
        stdout = json.dumps([{"number": 1, "title": "x", "labels": [], "body": ""}])
        stderr = ""

    def fake_run(*args: object, **kwargs: object) -> _OkProc:
        return _OkProc()

    monkeypatch.setattr("scan_issue_backlog.subprocess.run", fake_run)
    result = fetch_open_issues()
    assert result == [{"number": 1, "title": "x", "labels": [], "body": ""}]


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_emits_fyi_line(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_issues = [
        {"number": 1, "title": "bug 1", "labels": [{"name": "bug"}], "body": ""},
        {"number": 2, "title": "cleanup", "labels": [{"name": "cleanup"}], "body": ""},
    ]
    monkeypatch.setattr(
        "scan_issue_backlog.fetch_open_issues", lambda repo=None: fake_issues
    )

    rc = main([])
    assert rc == 0

    out = capsys.readouterr().out
    assert "Issues backlog:" in out
    assert "1 bugs" in out
    assert "1 cleanup" in out
    assert "(0 urgent)" in out


def test_main_emits_loud_block_when_urgent(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_issues = [
        {
            "number": 5,
            "title": "On fire",
            "labels": [{"name": "bug"}, {"name": "priority:urgent"}],
            "body": "",
        },
    ]
    monkeypatch.setattr(
        "scan_issue_backlog.fetch_open_issues", lambda repo=None: fake_issues
    )

    rc = main([])
    assert rc == 0

    out = capsys.readouterr().out
    assert "(1 urgent)" in out
    assert "URGENT: 1 open issue(s)" in out
    assert "#5: On fire" in out


def test_main_json_mode_emits_machine_readable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_issues = [
        {"number": 1, "title": "bug 1", "labels": [{"name": "bug"}], "body": ""},
    ]
    monkeypatch.setattr(
        "scan_issue_backlog.fetch_open_issues", lambda repo=None: fake_issues
    )

    rc = main(["--json"])
    assert rc == 0

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["counts"]["bug"] == 1
    assert payload["urgent_count"] == 0


def test_main_handles_gh_failure_gracefully(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("scan_issue_backlog.fetch_open_issues", lambda repo=None: None)

    rc = main([])
    assert rc == 0

    err = capsys.readouterr().err
    assert "gh issue list failed" in err
