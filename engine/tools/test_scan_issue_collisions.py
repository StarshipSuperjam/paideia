"""Tests for engine/tools/scan_issue_collisions.py.

Pure-function tests. gh and git subprocesses are monkey-patched so the
suite runs without network or repo state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_issue_collisions import (  # noqa: E402
    extract_keywords,
    find_collisions,
    is_actionable_now,
    main,
    read_declared_scope,
)


# ---------------------------------------------------------------------------
# extract_keywords
# ---------------------------------------------------------------------------


def test_extract_keywords_drops_stopwords() -> None:
    keywords = extract_keywords("the quick brown fox jumps over the lazy dog")
    assert "quick" in keywords
    assert "brown" in keywords
    assert "jumps" in keywords
    assert "over" in keywords
    assert "lazy" in keywords  # 4 chars, kept
    # Stopwords dropped:
    assert "the" not in keywords
    # Short words dropped (under MIN_KEYWORD_LEN=4):
    assert "fox" not in keywords
    assert "dog" not in keywords


def test_extract_keywords_lowercases() -> None:
    keywords = extract_keywords("Phase Five Epistemology")
    # 'phase' is a stopword (added to the project-specific list).
    assert "phase" not in keywords
    assert "five" in keywords
    assert "epistemology" in keywords


def test_extract_keywords_handles_empty_string() -> None:
    assert extract_keywords("") == set()


def test_extract_keywords_handles_kebab_and_snake() -> None:
    keywords = extract_keywords("scan_issue_backlog and build-readiness gate")
    assert "scan_issue_backlog" in keywords
    assert "build-readiness" in keywords
    # 'gate' is 4 chars exactly (matches MIN_KEYWORD_LEN), kept.
    assert "gate" in keywords
    # 3-char tokens are dropped.
    assert "and" not in keywords  # also a stopword


# ---------------------------------------------------------------------------
# read_declared_scope
# ---------------------------------------------------------------------------


def test_read_declared_scope_returns_field(tmp_path: Path) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text(json.dumps({"declared_scope": "Implementing thing X"}))

    assert read_declared_scope(tmp_path) == "Implementing thing X"


def test_read_declared_scope_returns_empty_when_file_missing(tmp_path: Path) -> None:
    assert read_declared_scope(tmp_path) == ""


def test_read_declared_scope_returns_empty_when_field_missing(tmp_path: Path) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text(json.dumps({"id": "S-0042"}))

    assert read_declared_scope(tmp_path) == ""


def test_read_declared_scope_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text("not valid json")

    assert read_declared_scope(tmp_path) == ""


def test_read_declared_scope_falls_back_to_working_on(tmp_path: Path) -> None:
    """When declared_scope is missing or empty, working_on is the fallback."""
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0001",
                "working_on": "Building thing X",
            }
        )
    )

    assert read_declared_scope(tmp_path) == "Building thing X"


def test_read_declared_scope_prefers_declared_over_working_on(tmp_path: Path) -> None:
    """When both fields are present and non-empty, declared_scope wins."""
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text(
        json.dumps(
            {
                "declared_scope": "The new field value",
                "working_on": "The old field value",
            }
        )
    )

    assert read_declared_scope(tmp_path) == "The new field value"


def test_read_declared_scope_falls_back_when_declared_empty(tmp_path: Path) -> None:
    """An empty-string declared_scope falls back to working_on."""
    (tmp_path / "engine" / "session").mkdir(parents=True)
    current = tmp_path / "engine" / "session" / "current.json"
    current.write_text(
        json.dumps(
            {
                "declared_scope": "",
                "working_on": "Fallback prose",
            }
        )
    )

    assert read_declared_scope(tmp_path) == "Fallback prose"


# ---------------------------------------------------------------------------
# find_collisions
# ---------------------------------------------------------------------------


def test_find_collisions_matches_path_in_body() -> None:
    issues = [
        {
            "number": 1,
            "title": "Some bug",
            "body": "Affects engine/tools/validate.py — needs investigation",
        },
    ]
    collisions = find_collisions(
        issues=issues,
        keywords=set(),
        paths=["engine/tools/validate.py"],
    )
    assert len(collisions) == 1
    assert collisions[0].issue_number == 1
    assert "engine/tools/validate.py" in collisions[0].matches


def test_find_collisions_matches_keyword_in_body() -> None:
    issues = [
        {
            "number": 2,
            "title": "Title here",
            "body": "There is an epistemology problem",
        },
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"epistemology"},
        paths=[],
    )
    assert len(collisions) == 1
    assert "epistemology" in collisions[0].matches


def test_find_collisions_matches_keyword_in_title() -> None:
    issues = [
        {
            "number": 3,
            "title": "Epistemology gate failure",
            "body": "Generic description",
        },
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"epistemology"},
        paths=[],
    )
    assert len(collisions) == 1


def test_find_collisions_no_match_when_no_overlap() -> None:
    issues = [
        {
            "number": 4,
            "title": "Unrelated thing",
            "body": "About something else entirely",
        },
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"epistemology", "phase"},
        paths=["engine/tools/validate.py"],
    )
    assert collisions == []


def test_find_collisions_word_boundary_matching() -> None:
    """Keyword 'mast' should not match inside 'mastery'."""
    issues = [
        {"number": 5, "title": "Mastery snapshots", "body": ""},
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"mast"},
        paths=[],
    )
    # 'mast' word-boundary-matched against 'Mastery' — 'mast' is a prefix
    # of 'mastery', not a standalone word. Should not match.
    assert collisions == []


def test_find_collisions_deduplicates_keyword_within_path() -> None:
    """A keyword that's a substring of a matched path doesn't double-report."""
    issues = [
        {
            "number": 6,
            "title": "About validate",
            # Body contains the full path so the path-match step fires first.
            "body": "Affects engine/tools/validate.py — please review",
        },
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"validate"},
        paths=["engine/tools/validate.py"],
    )
    assert len(collisions) == 1
    # Both the path and the keyword appear in the body, but the keyword
    # is a substring of the matched path so dedup suppresses it.
    assert "engine/tools/validate.py" in collisions[0].matches
    assert "validate" not in collisions[0].matches


def test_find_collisions_multiple_issues_each_reported() -> None:
    issues = [
        {"number": 10, "title": "Issue A", "body": "epistemology stuff"},
        {"number": 11, "title": "Epistemology issue", "body": ""},
        {"number": 12, "title": "Unrelated", "body": "ethics things"},
    ]
    collisions = find_collisions(
        issues=issues,
        keywords={"epistemology"},
        paths=[],
    )
    nums = sorted(c.issue_number for c in collisions)
    assert nums == [10, 11]


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_exit_zero_when_no_collisions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"declared_scope": "Implementing harmless thing"})
    )

    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        "scan_issue_collisions.fetch_open_issues",
        lambda gh_repo=None: [
            {"number": 1, "title": "Other", "body": "Nothing relevant"},
        ],
    )

    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 0


def test_main_exit_one_when_collisions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"declared_scope": "Working on epistemology"})
    )

    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        "scan_issue_collisions.fetch_open_issues",
        lambda gh_repo=None: [
            {"number": 5, "title": "Epistemology gate", "body": "Bug here"},
        ],
    )

    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "#5" in err
    assert "Epistemology gate" in err


def test_main_skips_when_nothing_to_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No declared_scope, no staged files → nothing to match → clean exit."""
    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: [],
    )

    # fetch_open_issues should not even be called in this path; confirm
    # by raising if it is.
    def _raise(gh_repo: str | None = None) -> None:
        raise AssertionError(
            "fetch_open_issues should not be called when nothing to match"
        )

    monkeypatch.setattr("scan_issue_collisions.fetch_open_issues", _raise)

    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 0


def test_main_silent_skip_on_gh_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"declared_scope": "Some scope here"})
    )

    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        "scan_issue_collisions.fetch_open_issues",
        lambda gh_repo=None: None,
    )

    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "gh issue list failed" in err


def test_main_json_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "engine" / "session").mkdir(parents=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"declared_scope": "Working on epistemology fixes"})
    )

    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: ["foo.py"],
    )
    monkeypatch.setattr(
        "scan_issue_collisions.fetch_open_issues",
        lambda gh_repo=None: [
            {"number": 7, "title": "Epistemology problem", "body": ""},
        ],
    )

    rc = main(["--repo-root", str(tmp_path), "--json"])
    assert rc == 1
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["scope_keywords"] == ["epistemology", "fixes", "working"]
    assert payload["staged_paths"] == ["foo.py"]
    assert len(payload["collisions"]) == 1
    assert payload["collisions"][0]["number"] == 7


# ---------------------------------------------------------------------------
# is_actionable_now (S-0143 / Issue #110)
# ---------------------------------------------------------------------------


def test_is_actionable_now_true_for_plain_issue() -> None:
    issue = {"number": 1, "title": "Regular bug", "body": "x", "labels": []}
    assert is_actionable_now(issue) is True


def test_is_actionable_now_false_for_trigger_gated_title() -> None:
    issue = {
        "number": 84,
        "title": "Add monthly metrics workflow [TRIGGER: ≥2 collaborators]",
        "body": "x",
        "labels": [],
    }
    assert is_actionable_now(issue) is False


def test_is_actionable_now_false_for_upstream_labeled() -> None:
    issue = {
        "number": 2,
        "title": "MemPalace upstream bug",
        "body": "x",
        "labels": [{"name": "upstream"}, {"name": "bug"}],
    }
    assert is_actionable_now(issue) is False


def test_is_actionable_now_label_match_is_case_insensitive() -> None:
    issue = {
        "number": 3,
        "title": "Some bug",
        "body": "",
        "labels": [{"name": "Upstream"}],
    }
    assert is_actionable_now(issue) is False


def test_is_actionable_now_handles_missing_labels_field() -> None:
    """Legacy gh response shape (pre-S-0143) lacks labels — default actionable."""
    issue = {"number": 4, "title": "Plain bug", "body": "x"}
    assert is_actionable_now(issue) is True


def test_is_actionable_now_handles_empty_title() -> None:
    issue = {"number": 5, "title": "", "body": "x", "labels": []}
    assert is_actionable_now(issue) is True


def test_main_skips_upstream_and_trigger_gated_in_collision_loop(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Integration: upstream + trigger-gated Issues are not reported even
    when their body/title would otherwise match this session's scope."""
    (tmp_path / "engine" / "session").mkdir(parents=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"declared_scope": "Working on epistemology gates"})
    )

    monkeypatch.setattr(
        "scan_issue_collisions.staged_files",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        "scan_issue_collisions.fetch_open_issues",
        lambda gh_repo=None: [
            {
                "number": 1,
                "title": "Upstream issue mentioning epistemology",
                "body": "",
                "labels": [{"name": "upstream"}],
            },
            {
                "number": 2,
                "title": "[TRIGGER: future condition] epistemology work",
                "body": "",
                "labels": [],
            },
            {
                "number": 3,
                "title": "Actionable epistemology bug",
                "body": "",
                "labels": [{"name": "bug"}],
            },
        ],
    )

    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 1  # one actionable collision remains (#3)
    err = capsys.readouterr().err
    assert "#3" in err
    assert "#1" not in err  # upstream filtered out
    assert "#2" not in err  # trigger-gated filtered out
