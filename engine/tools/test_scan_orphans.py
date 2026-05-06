"""Tests for engine/tools/scan_orphans.py.

Tests focus on the per-axis logic and the _table_emptiness helper.
The integration with git is exercised via real subprocess calls
inside synthetic tmp_path repos so the tests run without the real
project's archive history.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_orphans import (  # noqa: E402
    OrphanCandidate,
    _detect_session_id,
    _table_emptiness,
    axis_register_emptiness,
    main,
    render_json,
    render_markdown,
)


# ---------------------------------------------------------------------------
# _table_emptiness helper
# ---------------------------------------------------------------------------


def test_table_emptiness_recognizes_empty_register() -> None:
    text = (
        "# Some Register\n"
        "\n"
        "| Date | Idea | Status |\n"
        "|------|------|--------|\n"
        "| | | |\n"
        "\n"
        "Some prose after.\n"
    )
    headers, data = _table_emptiness(text)
    assert headers == 1
    assert data == 0


def test_table_emptiness_counts_data_rows() -> None:
    text = (
        "| Date | Idea |\n"
        "|------|------|\n"
        "| 2026-05-04 | Try this |\n"
        "| 2026-05-05 | And that |\n"
    )
    headers, data = _table_emptiness(text)
    assert headers == 1
    assert data == 2


def test_table_emptiness_handles_no_table() -> None:
    text = "Just prose. No tables.\n"
    headers, data = _table_emptiness(text)
    assert headers == 0
    assert data == 0


def test_table_emptiness_handles_multiple_tables() -> None:
    text = (
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n"
        "\n"
        "Some prose between tables.\n"
        "\n"
        "| X | Y |\n"
        "|---|---|\n"
        "| | |\n"
    )
    headers, data = _table_emptiness(text)
    assert headers == 2
    assert data == 1  # First table has data; second is empty.


def test_table_emptiness_partially_empty_row_still_counts() -> None:
    """A row with content in any cell counts as data."""
    text = "| A | B | C |\n|---|---|---|\n| | x | |\n"
    headers, data = _table_emptiness(text)
    assert data == 1


# ---------------------------------------------------------------------------
# axis_register_emptiness against synthetic register
# ---------------------------------------------------------------------------


def test_axis_register_emptiness_flags_empty_tensions(tmp_path: Path) -> None:
    """An empty tensions.md is flagged."""
    docs = tmp_path / "product" / "docs"
    docs.mkdir(parents=True)
    (docs / "tensions.md").write_text(
        "# Tensions Register\n\n"
        "| Date | Tension | Status |\n"
        "|------|---------|--------|\n"
        "| | | |\n"
    )
    # Initialize git in tmp_path so the count_inbound_references call doesn't
    # fail when scanning for refs.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
    )

    candidates = axis_register_emptiness(tmp_path)
    assert len(candidates) == 1
    assert candidates[0].path == "product/docs/tensions.md"
    assert candidates[0].axis == "register-empty"


def test_axis_register_emptiness_skips_populated(tmp_path: Path) -> None:
    """A populated tensions.md is NOT flagged."""
    docs = tmp_path / "product" / "docs"
    docs.mkdir(parents=True)
    (docs / "tensions.md").write_text(
        "# Tensions Register\n\n"
        "| Date | Tension | Status |\n"
        "|------|---------|--------|\n"
        "| 2026-05-04 | OQ-EXAMPLE | open |\n"
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
    )

    candidates = axis_register_emptiness(tmp_path)
    assert candidates == []


def test_axis_register_emptiness_no_register_file(tmp_path: Path) -> None:
    """No register file present → no candidates."""
    candidates = axis_register_emptiness(tmp_path)
    assert candidates == []


# ---------------------------------------------------------------------------
# render_json / render_markdown
# ---------------------------------------------------------------------------


def test_render_json_emits_array() -> None:
    candidates = [
        OrphanCandidate(
            path="foo.md",
            axis="reference-count",
            signal="0 inbound references",
            last_substantive_change="abc12345 2026-05-01",
            inbound_references=0,
        ),
    ]
    out = render_json(candidates)
    payload = json.loads(out)
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["path"] == "foo.md"


def test_render_json_empty() -> None:
    out = render_json([])
    assert json.loads(out) == []


def test_render_markdown_groups_by_path() -> None:
    candidates = [
        OrphanCandidate(
            path="foo.md",
            axis="reference-count",
            signal="x",
            last_substantive_change="y",
            inbound_references=0,
        ),
        OrphanCandidate(
            path="foo.md",
            axis="last-mod-age",
            signal="z",
            last_substantive_change="w",
            inbound_references=0,
        ),
        OrphanCandidate(
            path="bar.md",
            axis="reference-count",
            signal="x",
            last_substantive_change="y",
            inbound_references=0,
        ),
    ]
    out = render_markdown(candidates, "S-0042")
    # Each path appears once as a heading.
    assert out.count("### `foo.md`") == 1
    assert out.count("### `bar.md`") == 1
    # foo.md has both axes listed under it.
    foo_section = out.split("### `foo.md`")[1].split("### `bar.md`")[0]
    assert "reference-count" in foo_section
    assert "last-mod-age" in foo_section


def test_render_markdown_includes_diagnostic_question() -> None:
    out = render_markdown([], "S-0042")
    assert "doing the work it was created to do" in out
    assert "0 candidate(s)" in out


# ---------------------------------------------------------------------------
# _detect_session_id
# ---------------------------------------------------------------------------


def test_detect_session_id_returns_id(tmp_path: Path) -> None:
    sess_dir = tmp_path / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "current.json").write_text(json.dumps({"id": "S-0042"}))
    assert _detect_session_id(tmp_path) == "S-0042"


def test_detect_session_id_returns_placeholder_when_missing(tmp_path: Path) -> None:
    assert _detect_session_id(tmp_path) == "S-XXXX"


def test_detect_session_id_returns_placeholder_on_invalid_json(tmp_path: Path) -> None:
    sess_dir = tmp_path / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "current.json").write_text("not valid json")
    assert _detect_session_id(tmp_path) == "S-XXXX"


# ---------------------------------------------------------------------------
# main() — end-to-end against the live repo (smoke test)
# ---------------------------------------------------------------------------


def test_main_against_live_repo_completes(tmp_path: Path) -> None:
    """Smoke test: against a fresh tmp repo, main() exits 0."""
    rc = main(["--repo-root", str(tmp_path), "--json"])
    assert rc == 0


def test_main_writes_output_file(tmp_path: Path) -> None:
    out_path = tmp_path / "report.md"
    rc = main(
        [
            "--repo-root",
            str(tmp_path),
            "--output",
            str(out_path),
        ]
    )
    assert rc == 0
    assert out_path.is_file()
    content = out_path.read_text()
    assert "Dead-weight candidates" in content


def test_main_axis_filter_runs_only_named_axis(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--axis register-empty against an empty repo emits an empty result."""
    rc = main(
        [
            "--repo-root",
            str(tmp_path),
            "--json",
            "--axis",
            "register-empty",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert json.loads(out) == []
