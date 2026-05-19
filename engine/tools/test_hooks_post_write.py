"""Tests for the post-adr-write.sh + post-changelog-write.sh hooks (ADR 0099 Fix D).

Covers the two catch-early-surface reminders Fix D adds:
- post-adr-write.sh ADR-README index entry check
- post-changelog-write.sh `summary:` 200-char cap reminder

Each hook is exercised via subprocess against a tmp-dir git repo with the
canonical directory structure and a synthetic harness PostToolUse JSON
payload piped to stdin. Reminders surface on stderr; hooks always exit 0
per ADR 0043's non-blocking posture.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Resolve hook paths relative to this test file's location (engine/tools/).
_HOOKS_DIR = Path(__file__).resolve().parent / "hooks"
_POST_ADR_WRITE = _HOOKS_DIR / "post-adr-write.sh"
_POST_CHANGELOG_WRITE = _HOOKS_DIR / "post-changelog-write.sh"


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_repo(tmp_path: Path) -> Path:
    """Initialize a tmp-dir git repo with the canonical directory layout
    the hooks expect. Returns the repo root."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=main", str(repo)],
        capture_output=True,
        check=True,
    )
    _git(["config", "user.email", "test@example.com"], repo)
    _git(["config", "user.name", "Test"], repo)
    (repo / "engine" / "adr").mkdir(parents=True)
    (repo / "product" / "adr").mkdir(parents=True)
    (repo / "engine" / "changelog" / "2026").mkdir(parents=True)
    (repo / ".claude" / "logs").mkdir(parents=True)
    return repo


def _run_hook(
    hook: Path, payload: dict[str, Any], repo: Path
) -> subprocess.CompletedProcess[str]:
    """Invoke the hook with the JSON payload on stdin, cwd=repo."""
    return subprocess.run(
        ["bash", str(hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(repo),
        check=False,
    )


# ---------------------------------------------------------------------------
# post-adr-write.sh — ADR-README index consistency check
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _POST_ADR_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent — index-check requires jq for payload parse",
)
def test_post_adr_write_emits_index_reminder_when_index_missing(tmp_path: Path) -> None:
    """An engine ADR with no matching index row in engine/adr/README.md
    triggers the [adr-index-consistency] reminder on stderr."""
    repo = _make_repo(tmp_path)
    adr_path = repo / "engine" / "adr" / "0099-test-adr.md"
    adr_path.write_text("# ADR 0099 — Test ADR\n\n- **Status:** Accepted\n")
    # README exists but has no row for 0099.
    (repo / "engine" / "adr" / "README.md").write_text(
        "# Engine ADR index\n\n| ADR | Title | Status |\n|---|---|---|\n"
    )
    result = _run_hook(
        _POST_ADR_WRITE,
        {"tool_input": {"file_path": str(adr_path)}},
        repo,
    )
    assert result.returncode == 0, "hook must exit 0 per ADR 0043 non-blocking posture"
    assert "[adr-index-consistency]" in result.stderr, (
        f"expected index-consistency reminder; stderr={result.stderr!r}"
    )
    assert "0099" in result.stderr
    assert "engine/adr/README.md" in result.stderr


@pytest.mark.skipif(
    not _POST_ADR_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_adr_write_silent_when_index_present(tmp_path: Path) -> None:
    """An engine ADR with a matching index row in engine/adr/README.md
    does NOT trigger the [adr-index-consistency] reminder."""
    repo = _make_repo(tmp_path)
    adr_path = repo / "engine" / "adr" / "0099-test-adr.md"
    adr_path.write_text("# ADR 0099 — Test ADR\n\n- **Status:** Accepted\n")
    (repo / "engine" / "adr" / "README.md").write_text(
        "# Engine ADR index\n\n"
        "| ADR | Title | Status |\n|---|---|---|\n"
        "| [0099](0099-test-adr.md) | Test ADR | Accepted |\n"
    )
    result = _run_hook(
        _POST_ADR_WRITE,
        {"tool_input": {"file_path": str(adr_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[adr-index-consistency]" not in result.stderr, (
        f"expected silent when index entry present; stderr={result.stderr!r}"
    )


@pytest.mark.skipif(
    not _POST_ADR_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_adr_write_index_check_routes_by_partition(tmp_path: Path) -> None:
    """A product ADR's index lookup must target product/adr/README.md, not
    engine/adr/README.md. The path partition prefix determines routing."""
    repo = _make_repo(tmp_path)
    adr_path = repo / "product" / "adr" / "0100-product-test.md"
    adr_path.write_text("# ADR 0100 — Product Test\n\n- **Status:** Accepted\n")
    # Engine README has the row (wrong partition); product README does not.
    (repo / "engine" / "adr" / "README.md").write_text(
        "| [0100](0100-product-test.md) | mis-filed engine row | Accepted |\n"
    )
    (repo / "product" / "adr" / "README.md").write_text(
        "# Product ADR index\n\n| ADR | Title | Status |\n|---|---|---|\n"
    )
    result = _run_hook(
        _POST_ADR_WRITE,
        {"tool_input": {"file_path": str(adr_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[adr-index-consistency]" in result.stderr, (
        "expected reminder against product/adr/README.md "
        "(engine README's row must NOT satisfy the predicate for a product ADR)"
    )
    assert "product/adr/README.md" in result.stderr


@pytest.mark.skipif(
    not _POST_ADR_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_adr_write_index_accepts_adr_prefix_form(tmp_path: Path) -> None:
    """The regex accepts both `[NNNN](NNNN-foo.md)` and `[ADR NNNN](NNNN-foo.md)`
    forms — both appear in the existing engine + product READMEs."""
    repo = _make_repo(tmp_path)
    adr_path = repo / "engine" / "adr" / "0099-test-adr.md"
    adr_path.write_text("# ADR 0099 — Test ADR\n")
    (repo / "engine" / "adr" / "README.md").write_text(
        "| [ADR 0099](0099-test-adr.md) | Test ADR | Accepted |\n"
    )
    result = _run_hook(
        _POST_ADR_WRITE,
        {"tool_input": {"file_path": str(adr_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[adr-index-consistency]" not in result.stderr


# ---------------------------------------------------------------------------
# post-changelog-write.sh — summary-length reminder
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _POST_CHANGELOG_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_changelog_write_emits_reminder_when_summary_over_cap(
    tmp_path: Path,
) -> None:
    """A changelog entry whose `summary:` exceeds 200 chars triggers the
    [changelog-entry-schema] stderr reminder."""
    repo = _make_repo(tmp_path)
    entry_path = repo / "engine" / "changelog" / "2026" / "S-0209-test-entry.md"
    over_cap = "x" * 250  # 250 > 200 limit
    entry_path.write_text(
        f"---\n"
        f"session_id: S-0209\n"
        f"session_type: build\n"
        f"closed_at: 2026-05-19T00:00:00Z\n"
        f"material_change_class: docs\n"
        f"module: test\n"
        f"summary: {over_cap}\n"
        f"---\n\n# S-0209\n\n## Added\n\n- nothing real\n"
    )
    result = _run_hook(
        _POST_CHANGELOG_WRITE,
        {"tool_input": {"file_path": str(entry_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[changelog-entry-schema]" in result.stderr, (
        f"expected schema reminder; stderr={result.stderr!r}"
    )
    assert "250 chars" in result.stderr
    assert "200" in result.stderr
    assert "S-0209" in result.stderr


@pytest.mark.skipif(
    not _POST_CHANGELOG_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_changelog_write_silent_when_summary_within_cap(tmp_path: Path) -> None:
    """A changelog entry whose `summary:` is within 200 chars does NOT
    trigger the reminder."""
    repo = _make_repo(tmp_path)
    entry_path = repo / "engine" / "changelog" / "2026" / "S-0209-test-entry.md"
    within_cap = "x" * 150  # under the 200 limit
    entry_path.write_text(
        f"---\nsession_id: S-0209\nsummary: {within_cap}\n---\n\n# S-0209\n"
    )
    result = _run_hook(
        _POST_CHANGELOG_WRITE,
        {"tool_input": {"file_path": str(entry_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[changelog-entry-schema]" not in result.stderr


@pytest.mark.skipif(
    not _POST_CHANGELOG_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_changelog_write_silent_on_non_changelog_path(tmp_path: Path) -> None:
    """A write to a file outside engine/changelog/<YYYY>/S-*.md is silently
    skipped (the matcher fires for any Edit|Write; the hook self-filters)."""
    repo = _make_repo(tmp_path)
    unrelated = repo / "engine" / "STATE.md"
    unrelated.write_text("# STATE\n\nsummary: anything\n")
    result = _run_hook(
        _POST_CHANGELOG_WRITE,
        {"tool_input": {"file_path": str(unrelated)}},
        repo,
    )
    assert result.returncode == 0
    assert result.stderr == "", (
        f"expected silent on non-changelog path; got {result.stderr!r}"
    )


@pytest.mark.skipif(
    not _POST_CHANGELOG_WRITE.exists()
    or subprocess.run(["which", "jq"], capture_output=True).returncode != 0,
    reason="hook missing or jq absent",
)
def test_post_changelog_write_silent_when_summary_absent(tmp_path: Path) -> None:
    """If the entry has frontmatter but no `summary:` field, the hook is
    silent — the field is optional per ADR 0092."""
    repo = _make_repo(tmp_path)
    entry_path = repo / "engine" / "changelog" / "2026" / "S-0209-test-entry.md"
    entry_path.write_text(
        "---\nsession_id: S-0209\nsession_type: build\n---\n\n# S-0209\n"
    )
    result = _run_hook(
        _POST_CHANGELOG_WRITE,
        {"tool_input": {"file_path": str(entry_path)}},
        repo,
    )
    assert result.returncode == 0
    assert "[changelog-entry-schema]" not in result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
