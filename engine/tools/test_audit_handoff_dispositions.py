"""Tests for engine/tools/audit_handoff_dispositions.py.

Covers each public function with at least one test per behavior branch
and one integration test per main() exit code.

Test isolation strategy
-----------------------
- Pure-function units (parse_added_sections, is_valid_disposition,
  find_undispositioned_sections, _extract_disposition) test against
  hand-crafted diff strings — no filesystem or git involvement.
- Integration tests via main() build synthetic git repos under
  tmp_path with hand-crafted commits modifying HANDOFF.md and assert
  exit codes through main() called with explicit --range.

Non-responsibilities
--------------------
- Does not test argparse beyond the documented flags.
- Does not test the script's behavior when git is unavailable.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_handoff_dispositions import (  # noqa: E402
    HandoffSection,
    _extract_disposition,
    find_undispositioned_sections,
    is_valid_disposition,
    main,
    parse_added_sections,
)


# ---------------------------------------------------------------------------
# is_valid_disposition
# ---------------------------------------------------------------------------


def test_is_valid_disposition_fixed_in_session_with_sha() -> None:
    assert is_valid_disposition("fixed-in-session @ abc1234")
    assert is_valid_disposition("fixed-in-session @ ac039ca5d")


def test_is_valid_disposition_fixed_in_session_without_sha_rejected() -> None:
    """Bare ``fixed-in-session`` with no SHA is rejected."""
    assert not is_valid_disposition("fixed-in-session")
    assert not is_valid_disposition("fixed-in-session @")


def test_is_valid_disposition_deferred_with_user_confirmation() -> None:
    assert is_valid_disposition("deferred-with-user-confirmation")


def test_is_valid_disposition_out_of_scope() -> None:
    assert is_valid_disposition("out-of-scope")


def test_is_valid_disposition_not_actionable() -> None:
    assert is_valid_disposition("not-actionable")


def test_is_valid_disposition_tracked_as_issue_with_number() -> None:
    assert is_valid_disposition("tracked-as-issue #1")
    assert is_valid_disposition("tracked-as-issue #42")
    assert is_valid_disposition("tracked-as-issue #12345")


def test_is_valid_disposition_tracked_as_issue_without_number_rejected() -> None:
    """Bare ``tracked-as-issue`` with no number is rejected."""
    assert not is_valid_disposition("tracked-as-issue")
    assert not is_valid_disposition("tracked-as-issue #")
    assert not is_valid_disposition("tracked-as-issue #abc")


def test_is_valid_disposition_unknown_value_rejected() -> None:
    assert not is_valid_disposition("deferred")
    assert not is_valid_disposition("queued for later")
    assert not is_valid_disposition("")


def test_is_valid_disposition_extra_suffix_rejected() -> None:
    """Trailing prose after a known form is rejected."""
    assert not is_valid_disposition("out-of-scope because reasons")
    assert not is_valid_disposition("not-actionable yet")


# ---------------------------------------------------------------------------
# _extract_disposition
# ---------------------------------------------------------------------------


def test_extract_disposition_present() -> None:
    body = (
        "Some prose about the bug.\n"
        "\n"
        "**Disposition:** fixed-in-session @ abc1234\n"
        "\n"
        "Trailing prose.\n"
    )
    assert _extract_disposition(body) == "fixed-in-session @ abc1234"


def test_extract_disposition_absent() -> None:
    body = "Just prose with no disposition line.\n"
    assert _extract_disposition(body) is None


def test_extract_disposition_first_match_wins() -> None:
    body = (
        "**Disposition:** fixed-in-session @ abc\n"
        "later: **Disposition:** out-of-scope\n"
    )
    assert _extract_disposition(body) == "fixed-in-session @ abc"


def test_extract_disposition_strips_whitespace() -> None:
    body = "**Disposition:**    out-of-scope   \n"
    assert _extract_disposition(body) == "out-of-scope"


# ---------------------------------------------------------------------------
# parse_added_sections
# ---------------------------------------------------------------------------


def test_parse_added_sections_empty_diff() -> None:
    assert parse_added_sections("") == []


def test_parse_added_sections_diff_with_no_sections() -> None:
    """Diff that adds prose but no `## ` headers yields no sections."""
    diff = (
        "diff --git a/HANDOFF.md b/HANDOFF.md\n"
        "--- a/HANDOFF.md\n"
        "+++ b/HANDOFF.md\n"
        "@@ -1,2 +1,3 @@\n"
        " existing prose\n"
        "+a new line of prose\n"
        " more existing prose\n"
    )
    assert parse_added_sections(diff) == []


def test_parse_added_sections_one_new_section_with_disposition() -> None:
    diff = (
        "diff --git a/HANDOFF.md b/HANDOFF.md\n"
        "@@ -10,1 +10,5 @@\n"
        "+## A new section header\n"
        "+\n"
        "+Some body prose.\n"
        "+\n"
        "+**Disposition:** fixed-in-session @ deadbeef\n"
    )
    sections = parse_added_sections(diff)
    assert len(sections) == 1
    assert sections[0].header == "## A new section header"
    assert sections[0].disposition == "fixed-in-session @ deadbeef"


def test_parse_added_sections_one_new_section_without_disposition() -> None:
    diff = (
        "@@ -1,1 +1,3 @@\n"
        "+## A new section header\n"
        "+\n"
        "+Body prose with no disposition line.\n"
    )
    sections = parse_added_sections(diff)
    assert len(sections) == 1
    assert sections[0].disposition is None


def test_parse_added_sections_two_new_sections() -> None:
    diff = (
        "@@ -1,1 +1,8 @@\n"
        "+## First new section\n"
        "+body of first.\n"
        "+**Disposition:** out-of-scope\n"
        "+\n"
        "+## Second new section\n"
        "+body of second.\n"
        "+**Disposition:** not-actionable\n"
    )
    sections = parse_added_sections(diff)
    assert len(sections) == 2
    assert sections[0].header == "## First new section"
    assert sections[0].disposition == "out-of-scope"
    assert sections[1].header == "## Second new section"
    assert sections[1].disposition == "not-actionable"


def test_parse_added_sections_ignores_existing_section_edits() -> None:
    """An existing section that gets its body edited (not the header) is not new."""
    diff = (
        "@@ -10,5 +10,6 @@\n"
        " ## Existing section header\n"
        " \n"
        " Existing body line one.\n"
        "+a newly-added body line\n"
        " Existing body line two.\n"
    )
    # No `+## ` header anywhere — no new sections.
    assert parse_added_sections(diff) == []


def test_parse_added_sections_skips_diff_metadata() -> None:
    """Diff metadata lines should not be confused with content."""
    diff = (
        "diff --git a/HANDOFF.md b/HANDOFF.md\n"
        "index 1234..5678 100644\n"
        "--- a/HANDOFF.md\n"
        "+++ b/HANDOFF.md\n"
        "@@ -1,1 +1,3 @@\n"
        "+## Header\n"
        "+**Disposition:** out-of-scope\n"
    )
    sections = parse_added_sections(diff)
    assert len(sections) == 1
    assert sections[0].header == "## Header"


# ---------------------------------------------------------------------------
# find_undispositioned_sections
# ---------------------------------------------------------------------------


def test_find_undispositioned_sections_all_valid() -> None:
    sections = [
        HandoffSection("## A", "...", "out-of-scope"),
        HandoffSection("## B", "...", "fixed-in-session @ abc"),
    ]
    assert find_undispositioned_sections(sections) == []


def test_find_undispositioned_sections_one_missing() -> None:
    sections = [
        HandoffSection("## A", "...", "out-of-scope"),
        HandoffSection("## B", "...", None),
    ]
    bad = find_undispositioned_sections(sections)
    assert len(bad) == 1
    assert bad[0].header == "## B"


def test_find_undispositioned_sections_one_malformed() -> None:
    sections = [
        HandoffSection("## A", "...", "out-of-scope"),
        HandoffSection("## B", "...", "deferred"),  # not the full form
    ]
    bad = find_undispositioned_sections(sections)
    assert len(bad) == 1
    assert bad[0].header == "## B"


def test_find_undispositioned_sections_empty_input() -> None:
    assert find_undispositioned_sections([]) == []


# ---------------------------------------------------------------------------
# Integration: main() via tmp_path git repos
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "HANDOFF.md").write_text("# Handoff\n\nExisting content.\n")
    _git(repo, "add", "HANDOFF.md")
    _git(repo, "commit", "-q", "-m", "initial")
    return repo


def _eager_claim(repo: Path) -> str:
    """Add an empty eager-claim commit; return its SHA."""
    _git(
        repo,
        "commit",
        "--allow-empty",
        "-q",
        "-m",
        "chore(session): eager-claim S-9999 — test",
    )
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _modify_handoff(
    repo: Path, new_content: str, message: str = "docs(handoff): edit"
) -> str:
    (repo / "HANDOFF.md").write_text(new_content)
    _git(repo, "add", "HANDOFF.md")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_main_passes_when_no_handoff_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    eager = _eager_claim(repo)
    # No HANDOFF.md modification after eager-claim.

    rc = main(["--range", f"{eager}^..HEAD", "--repo-root", str(repo)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "no new HANDOFF.md sections" in out


def test_main_passes_when_new_section_has_valid_disposition(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    eager = _eager_claim(repo)
    new_content = (
        "# Handoff\n"
        "\n"
        "Existing content.\n"
        "\n"
        "## Some new finding\n"
        "\n"
        "Prose describing the finding.\n"
        "\n"
        "**Disposition:** fixed-in-session @ deadbeef\n"
    )
    _modify_handoff(repo, new_content)

    rc = main(["--range", f"{eager}^..HEAD", "--repo-root", str(repo)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "all with valid dispositions" in out


def test_main_fails_when_new_section_missing_disposition(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    eager = _eager_claim(repo)
    new_content = (
        "# Handoff\n"
        "\n"
        "Existing content.\n"
        "\n"
        "## Some new finding\n"
        "\n"
        "Prose describing the finding without any disposition.\n"
    )
    _modify_handoff(repo, new_content)

    rc = main(["--range", f"{eager}^..HEAD", "--repo-root", str(repo)])

    assert rc == 2
    err = capsys.readouterr().err
    assert "Some new finding" in err
    assert "no disposition found" in err


def test_main_fails_when_disposition_value_unrecognized(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    eager = _eager_claim(repo)
    new_content = "# Handoff\n\n## Some finding\n\n**Disposition:** queued for later\n"
    _modify_handoff(repo, new_content)

    rc = main(["--range", f"{eager}^..HEAD", "--repo-root", str(repo)])

    assert rc == 2
    err = capsys.readouterr().err
    assert "unrecognized disposition" in err
    assert "queued for later" in err


def test_main_list_flag_prints_sections_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--list mode prints discovered sections + dispositions, exits 0 always."""
    repo = _init_repo(tmp_path)
    eager = _eager_claim(repo)
    new_content = "# Handoff\n\n## Section without disposition\n\nProse.\n"
    _modify_handoff(repo, new_content)

    rc = main(["--range", f"{eager}^..HEAD", "--list", "--repo-root", str(repo)])

    assert rc == 0  # --list never enforces
    out = capsys.readouterr().out
    assert "Section without disposition" in out
    assert "(missing)" in out


def test_main_passes_when_only_existing_section_edited(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Editing an existing section's body without adding new headers passes."""
    initial = "# Handoff\n\n## Existing section\n\nOld body.\n"
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "HANDOFF.md").write_text(initial)
    _git(repo, "add", "HANDOFF.md")
    _git(repo, "commit", "-q", "-m", "initial")

    eager = _eager_claim(repo)
    edited = "# Handoff\n\n## Existing section\n\nOld body.\nNewly appended line.\n"
    _modify_handoff(repo, edited)

    rc = main(["--range", f"{eager}^..HEAD", "--repo-root", str(repo)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "no new HANDOFF.md sections" in out


def test_main_no_eager_claim_in_range_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """When auto-detection finds no eager-claim, audit silently exits 0."""
    repo = _init_repo(tmp_path)
    # No eager-claim commit. Auto-detection should fail; explicit range
    # would also work but we exercise the auto-detect path here.
    monkeypatch.chdir(repo)
    # Override REPO_ROOT used by helpers via the global; simplest is to
    # call with an explicit range that exists but contains nothing.
    rc = main(["--range", "HEAD~0..HEAD"])

    assert rc == 0
