"""Regression test for Issue #56 — pre-commit close-mode archive-path filter.

Layer 1 contract per Issue #56.

The pre-commit hook at ``engine/tools/hooks/pre-commit`` line 233 finds the
staged archive file via:

    git diff --cached --name-only --diff-filter=<X> \\
        | grep -E '^engine/session/archive/S-[0-9]{4}\\.json$' \\
        | head -1

Pre-S-0118 used ``--diff-filter=A`` only. ``git mv current.json
archive/S-NNNN.json`` stages a rename (status ``R``); the ``A`` filter
returned empty and the structured-fields audit silently skipped — tripped
at S-0076 and S-0106.

S-0118 changed the filter to ``--diff-filter=AR``. With ``--name-only``,
``git diff --cached --diff-filter=AR`` outputs the destination path on
renames, so the same grep matches both close shapes (cp+rm+git add and
git mv).

These tests verify the filter-logic delta against tmp-dir git fixtures:
the OLD ``A``-only filter silently skips a git-mv rename, and the NEW
``AR`` filter catches it. Repository-internal state only — no full
pre-commit hook invocation required.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


ARCHIVE_RE = re.compile(r"^engine/session/archive/S-[0-9]{4}\.json$")


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _filtered_archive_path(repo: Path, diff_filter: str) -> str | None:
    """Run the same query the pre-commit hook runs at line 233 and return
    the first matching archive path (or None)."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "diff",
            "--cached",
            "--name-only",
            f"--diff-filter={diff_filter}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if ARCHIVE_RE.match(line.strip()):
            return line.strip()
    return None


def _make_repo_with_current_json(tmp_path: Path) -> Path:
    """Bare repo + clone with a committed engine/session/current.json so a
    `git mv current.json archive/S-NNNN.json` can be staged on top of it.
    """
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "init", "--bare", str(origin)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "clone", str(origin), str(clone)], capture_output=True, check=True
    )
    _git(["config", "user.email", "test@example.com"], clone)
    _git(["config", "user.name", "Test"], clone)

    sess_dir = clone / "engine" / "session"
    sess_dir.mkdir(parents=True)
    (sess_dir / "current.json").write_text(
        '{"id": "S-0001", "status": "in_progress"}\n'
    )
    _git(["add", "."], clone)
    _git(["commit", "-m", "seed current.json"], clone)
    _git(["branch", "-M", "main"], clone)
    _git(["push", "-u", "origin", "main"], clone)
    return clone


def test_git_mv_close_shape_old_filter_silently_skips(tmp_path: Path) -> None:
    """Confirms the original bug: --diff-filter=A misses a git-mv rename.

    Stages `git mv current.json archive/S-0001.json` and queries with the
    pre-fix filter. The query returns no archive path, which is the silent
    skip the structured-fields audit was suffering from at S-0076 and S-0106.
    """
    repo = _make_repo_with_current_json(tmp_path)

    archive_dir = repo / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    _git(
        [
            "mv",
            "engine/session/current.json",
            "engine/session/archive/S-0001.json",
        ],
        repo,
    )

    # Sanity: git records this as a rename.
    name_status = (
        _git(["diff", "--cached", "--name-status"], repo).stdout.strip().splitlines()
    )
    assert any(line.startswith("R") for line in name_status), (
        f"expected a rename in staged diff; got {name_status!r}"
    )

    # Pre-fix filter ('A' only) silently skips renames.
    pre_fix = _filtered_archive_path(repo, "A")
    assert pre_fix is None, (
        f"pre-fix --diff-filter=A unexpectedly found a path "
        f"({pre_fix!r}); the bug should make it return None"
    )


def test_git_mv_close_shape_new_filter_finds_archive(tmp_path: Path) -> None:
    """Confirms the fix: --diff-filter=AR catches a git-mv rename.

    Stages the same `git mv` close shape and queries with the post-fix
    filter. The destination archive path is returned, so the audit body
    inside ``if [ -n "$ARCHIVE_PATH" ]`` will execute.
    """
    repo = _make_repo_with_current_json(tmp_path)

    archive_dir = repo / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    _git(
        [
            "mv",
            "engine/session/current.json",
            "engine/session/archive/S-0001.json",
        ],
        repo,
    )

    post_fix = _filtered_archive_path(repo, "AR")
    assert post_fix == "engine/session/archive/S-0001.json", (
        f"post-fix --diff-filter=AR did not find the renamed archive path; "
        f"got {post_fix!r}"
    )


def test_cp_rm_close_shape_caught_by_both_filters(tmp_path: Path) -> None:
    """Sanity: the cp+rm+git add close shape (status A) was always caught.

    Pre-fix --diff-filter=A and post-fix --diff-filter=AR both find the
    archive path on the cp+rm shape. This guards against a regression
    where the filter change inadvertently breaks the always-working path.
    """
    repo = _make_repo_with_current_json(tmp_path)

    archive_dir = repo / "engine" / "session" / "archive"
    archive_dir.mkdir(parents=True)
    src = repo / "engine" / "session" / "current.json"
    dst = archive_dir / "S-0001.json"
    # Real closes add fields (ended_at, outcome_summary, etc.) so the
    # archive is materially different from current.json — git's rename
    # detection does NOT classify it as R, and the diff stages as A + D.
    dst.write_text(
        '{"id": "S-0001", "status": "closed", '
        '"ended_at": "2026-05-10T12:00:00Z", '
        '"outcome_summary": "test", '
        '"outcome_summary_soft_warns": {}, '
        '"mode": "build", '
        '"mempalace_activity": {}, '
        '"next_session_handle": null}\n'
    )
    src.unlink()
    _git(
        [
            "add",
            "engine/session/archive/S-0001.json",
            "engine/session/current.json",
        ],
        repo,
    )

    name_status = (
        _git(["diff", "--cached", "--name-status"], repo).stdout.strip().splitlines()
    )
    assert any(
        line.startswith("A\tengine/session/archive/S-0001.json") for line in name_status
    ), f"expected an A status on the archive; got {name_status!r}"
    assert any(
        line.startswith("D\tengine/session/current.json") for line in name_status
    ), f"expected a D status on current.json; got {name_status!r}"

    pre_fix = _filtered_archive_path(repo, "A")
    post_fix = _filtered_archive_path(repo, "AR")
    assert pre_fix == "engine/session/archive/S-0001.json"
    assert post_fix == "engine/session/archive/S-0001.json"


def test_no_close_diff_filter_returns_none(tmp_path: Path) -> None:
    """Sanity: filter returns None when no archive path is staged.

    Stages an unrelated change (a markdown edit). Both filters return
    None — the hook's audit-skip is correct in that case.
    """
    repo = _make_repo_with_current_json(tmp_path)
    (repo / "README.md").write_text("hello\n")
    _git(["add", "README.md"], repo)

    pre_fix = _filtered_archive_path(repo, "A")
    post_fix = _filtered_archive_path(repo, "AR")
    assert pre_fix is None
    assert post_fix is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
