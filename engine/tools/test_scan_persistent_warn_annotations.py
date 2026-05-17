"""Tests for engine/tools/scan_persistent_warn_annotations.py.

The parser's contract is small: walk markdown lines, capture H3
``### `category_name``` headings between the
``## Persistent-warn annotation`` H2 marker and the next ``## `` header.

Tests cover:
- Parsing the real ``tools-validate-interpretation.md`` shipped with the
  repo — minimum-set expectation that the three S-0077 annotations are
  captured, regardless of any additions made in this session.
- Minimal positive fixture (1 entry, 3 entries).
- Empty section (header present, no H3 entries).
- Missing section header — should return exit code 2.
- Missing file — should return exit code 2.
- Leakage guard: H3 entries in sibling sections must NOT be captured.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_persistent_warn_annotations import (  # noqa: E402
    DEFAULT_OPS_DOC,
    extract_annotated_categories,
    main,
)


# -- Pure-function tests -------------------------------------------------


def test_extract_minimal_one_entry() -> None:
    text = (
        "# Title\n"
        "## Persistent-warn annotation\n"
        "Intro prose.\n"
        "### `health_check_overdue` (annotated S-0077)\n"
        "Body.\n"
    )
    assert extract_annotated_categories(text) == ["health_check_overdue"]


def test_extract_three_entries_ordered() -> None:
    text = (
        "## Persistent-warn annotation\n"
        "### `first_cat` (annotated S-0001)\n"
        "body\n"
        "### `second_cat` (annotated S-0002)\n"
        "body\n"
        "### `third_cat` (annotated S-0003)\n"
        "body\n"
    )
    assert extract_annotated_categories(text) == [
        "first_cat",
        "second_cat",
        "third_cat",
    ]


def test_extract_empty_section() -> None:
    """Section header present, no H3 entries — return empty list cleanly."""
    text = (
        "## Persistent-warn annotation\n"
        "Intro prose only. No entries yet.\n"
        "## Next section\n"
        "### `not_captured`\n"
    )
    assert extract_annotated_categories(text) == []


def test_extract_terminates_at_next_h2() -> None:
    """Entries in sibling H2 sections must not leak in."""
    text = (
        "## Persistent-warn annotation\n"
        "### `inside_one` (annotated S-0001)\n"
        "body\n"
        "## Actively-tracked, deferred re-audit\n"
        "### `outside_one` (deferred re-audit; introduced S-0146)\n"
        "body\n"
        "### `outside_two` (deferred re-audit; introduced S-0163)\n"
    )
    assert extract_annotated_categories(text) == ["inside_one"]


def test_extract_section_missing_raises() -> None:
    text = "# Some doc\n## Other section\n### `cat` (annotated)\n"
    with pytest.raises(ValueError, match="section header"):
        extract_annotated_categories(text)


def test_extract_skips_non_category_h3() -> None:
    """H3 lines that don't match the backtick-category shape are ignored."""
    text = (
        "## Persistent-warn annotation\n"
        "### Some narrative heading\n"
        "### `real_cat` (annotated S-0099)\n"
        "### Another narrative heading\n"
    )
    assert extract_annotated_categories(text) == ["real_cat"]


def test_extract_ignores_h3_before_section() -> None:
    """H3 entries above the section header must not be captured."""
    text = (
        "## Earlier section\n"
        "### `before_one` (annotated S-0001)\n"
        "### `before_two` (annotated S-0002)\n"
        "## Persistent-warn annotation\n"
        "### `inside` (annotated S-0077)\n"
    )
    assert extract_annotated_categories(text) == ["inside"]


# -- Integration with shipped ops doc ------------------------------------


def test_real_ops_doc_captures_known_minimums() -> None:
    """Parse the actually-shipped ops doc; verify the three S-0077 entries
    and any newer additions made in this session (Phase B of S-0196).

    Loose lower bound — the session that adds more entries should still
    pass without test churn.
    """
    text = DEFAULT_OPS_DOC.read_text(encoding="utf-8")
    cats = extract_annotated_categories(text)

    # The three originals from S-0077 must always be present.
    must_contain = {"health_check_overdue", "issue_collision", "missing_rigor_score"}
    assert must_contain.issubset(set(cats)), (
        f"Expected at minimum {must_contain}, got {cats}"
    )

    # Leakage guard: categories that explicitly live in OTHER sections of
    # the doc must not appear here.
    must_not_contain = {"timestamp_helper_bypass", "next_session_handle_unknown_issue"}
    overlap = must_not_contain.intersection(set(cats))
    assert not overlap, f"Sibling-section leakage detected: {overlap}"


# -- CLI tests -----------------------------------------------------------


def test_cli_default_succeeds(capsys: pytest.CaptureFixture[str]) -> None:
    """Invoking with no args uses the shipped ops doc; exit 0."""
    rc = main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert "health_check_overdue" in captured.out
    assert "issue_collision" in captured.out


def test_cli_missing_file_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bogus = tmp_path / "missing.md"
    rc = main(["--ops-doc", str(bogus)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "ops doc not found" in captured.err


def test_cli_missing_section_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = tmp_path / "no_section.md"
    fixture.write_text("# Doc\n## Some other H2\n### `cat`\n", encoding="utf-8")
    rc = main(["--ops-doc", str(fixture)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "section header" in captured.err


def test_cli_writes_one_category_per_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = tmp_path / "fixture.md"
    fixture.write_text(
        "## Persistent-warn annotation\n"
        "### `alpha` (annotated S-0001)\n"
        "body\n"
        "### `beta` (annotated S-0002)\n"
        "body\n",
        encoding="utf-8",
    )
    rc = main(["--ops-doc", str(fixture)])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == "alpha\nbeta\n"


# -- Process-level invocation (smoke) ------------------------------------


def test_subprocess_invocation_returns_categories() -> None:
    """End-to-end: invoke as the shell hook will, capture stdout, verify."""
    script = Path(__file__).resolve().parent / "scan_persistent_warn_annotations.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert "health_check_overdue" in lines
    assert "issue_collision" in lines
    assert "missing_rigor_score" in lines
