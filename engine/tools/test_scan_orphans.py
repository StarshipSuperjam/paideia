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
    _build_boot_surface_reachable_set,
    _detect_session_id,
    _table_emptiness,
    axis_ops_doc_uncited,
    axis_register_emptiness,
    main,
    render_json,
    render_markdown,
)


def _init_git(tmp_path: Path) -> None:
    """Initialize a synthetic tmp_path repo with one commit so git-aware
    helpers (count_inbound_references, last_substantive_change) work.
    """
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


# ---------------------------------------------------------------------------
# axis_ops_doc_uncited — refined predicate (S-0126, Issue #89)
#
# The refined axis flags an ops doc when BOTH predicates fire:
#   (1) fewer than 5 unique inbound file references, AND
#   (2) unreachable from the boot-surface link graph rooted at
#       CLAUDE.md + engine/STATE.md (treating operations/README.md as a
#       visit-but-don't-traverse leaf).
# ---------------------------------------------------------------------------


def _seed_minimal_repo_with_ops_doc(
    tmp_path: Path,
    *,
    ops_doc_name: str,
    inbound_refs_from_files: list[tuple[str, str]],
    boot_link_to_ops_doc: bool,
    extra_files: list[tuple[str, str]] | None = None,
) -> Path:
    """Create a tmp_path repo with a single ops doc + optional inbound refs.

    Parameters
    ----------
    ops_doc_name:
        Filename (no path) of the ops doc to create under engine/operations/.
    inbound_refs_from_files:
        List of (relative_path, content) for additional files that may mention
        the ops doc's basename. The basename mention counts as an inbound ref.
    boot_link_to_ops_doc:
        If True, engine/STATE.md links directly to the ops doc via a markdown
        link, making the doc reachable from the boot surface.
    extra_files:
        Extra files to create (path, content) with no implicit refs.

    Returns the path of the created ops doc.
    """
    ops_dir = tmp_path / "engine" / "operations"
    ops_dir.mkdir(parents=True)
    ops_doc_path = ops_dir / ops_doc_name
    ops_doc_path.write_text(f"# {ops_doc_name}\n\nBody.\n")

    # operations/README.md is the ops-doc index — present so the BFS
    # encounters it as a leaf (visited but not traversed).
    (ops_dir / "README.md").write_text(
        f"# Operations index\n\n- [{ops_doc_name}]({ops_doc_name})\n"
    )

    # Boot-surface seeds. STATE.md is at engine/STATE.md, so its relative
    # link to an ops doc is operations/<name>.md (not engine/operations/).
    state_link = (
        f"\n\nSee [{ops_doc_name}](operations/{ops_doc_name})."
        if boot_link_to_ops_doc
        else ""
    )
    (tmp_path / "engine" / "STATE.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "STATE.md").write_text(
        f"# Project State\n\nBoot pointer.{state_link}\n"
    )
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\nAI orientation. Links: "
        "[ops-index](engine/operations/README.md).\n"
    )

    # Inbound-ref files.
    for rel, content in inbound_refs_from_files:
        full = tmp_path / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)

    for rel, content in extra_files or []:
        full = tmp_path / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)

    _init_git(tmp_path)
    return ops_doc_path


def test_axis_ops_doc_uncited_flags_truly_orphan_doc(tmp_path: Path) -> None:
    """An ops doc with 0 inbound refs AND no boot-surface link is flagged."""
    _seed_minimal_repo_with_ops_doc(
        tmp_path,
        ops_doc_name="orphan-doc.md",
        inbound_refs_from_files=[],
        boot_link_to_ops_doc=False,
    )
    candidates = axis_ops_doc_uncited(tmp_path)
    flagged = {c.path for c in candidates}
    assert "engine/operations/orphan-doc.md" in flagged


def test_axis_ops_doc_uncited_skips_boot_reachable_doc(tmp_path: Path) -> None:
    """An ops doc reachable from STATE.md is NOT flagged, even with 0 refs."""
    _seed_minimal_repo_with_ops_doc(
        tmp_path,
        ops_doc_name="boot-reachable.md",
        inbound_refs_from_files=[],
        boot_link_to_ops_doc=True,
    )
    candidates = axis_ops_doc_uncited(tmp_path)
    flagged = {c.path for c in candidates}
    assert "engine/operations/boot-reachable.md" not in flagged


def test_axis_ops_doc_uncited_skips_high_reference_doc(tmp_path: Path) -> None:
    """An ops doc with >= 5 unique inbound refs is NOT flagged, even when
    unreachable from boot.
    """
    refs = [(f"refs/file{i}.md", "Mentions: boot-irreachable.md\n") for i in range(6)]
    _seed_minimal_repo_with_ops_doc(
        tmp_path,
        ops_doc_name="boot-irreachable.md",
        inbound_refs_from_files=refs,
        boot_link_to_ops_doc=False,
    )
    candidates = axis_ops_doc_uncited(tmp_path)
    flagged = {c.path for c in candidates}
    assert "engine/operations/boot-irreachable.md" not in flagged


def test_axis_ops_doc_uncited_readme_not_traversed_as_path(tmp_path: Path) -> None:
    """operations/README.md indexing a doc must NOT alone make it reachable
    from the boot surface. The BFS visits README.md as a leaf so README's
    outbound links are not followed for reachability purposes.
    """
    # Only README.md mentions the ops doc; no boot link, no other refs.
    _seed_minimal_repo_with_ops_doc(
        tmp_path,
        ops_doc_name="readme-only.md",
        inbound_refs_from_files=[],
        boot_link_to_ops_doc=False,
    )
    candidates = axis_ops_doc_uncited(tmp_path)
    flagged = {c.path for c in candidates}
    # README.md mentions readme-only.md (as an index entry) but BFS does NOT
    # traverse README.md, AND count_inbound_references discounts the
    # operations/README.md mention. So readme-only.md has 0 refs and is
    # unreachable → flagged.
    assert "engine/operations/readme-only.md" in flagged


def test_build_boot_surface_reachable_set_treats_readme_as_leaf(
    tmp_path: Path,
) -> None:
    """README.md is reached from CLAUDE.md, but its outbound links are NOT
    traversed. A doc only linked from README.md is NOT in the reachable set.
    """
    ops_dir = tmp_path / "engine" / "operations"
    ops_dir.mkdir(parents=True)
    (ops_dir / "indexed-only.md").write_text("# indexed\n")
    (ops_dir / "README.md").write_text("# Index\n\n- [indexed](indexed-only.md)\n")
    (tmp_path / "engine" / "STATE.md").write_text("# State\n[no ops links]\n")
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE\n[ops-index](engine/operations/README.md)\n"
    )

    reachable = _build_boot_surface_reachable_set(tmp_path)

    # CLAUDE.md and STATE.md are seeds → in set.
    assert (tmp_path / "CLAUDE.md").resolve() in reachable
    assert (tmp_path / "engine" / "STATE.md").resolve() in reachable
    # README.md is visited as a leaf → in set.
    assert (ops_dir / "README.md").resolve() in reachable
    # But the doc indexed by README.md is NOT reached, because the BFS does
    # not traverse README.md's outbound links.
    assert (ops_dir / "indexed-only.md").resolve() not in reachable
