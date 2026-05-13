"""Tests for engine/tools/probe_versions.py.

Tests are pure-function where possible. Git/subprocess interactions are
monkey-patched so the suite runs without a real worktree layout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from probe_versions import (  # noqa: E402
    _resolve_main_repo,
    _safe_import_version,
    classify_venv,
    format_line,
    gather,
    main,
)


# ---------------------------------------------------------------------------
# _safe_import_version
# ---------------------------------------------------------------------------


def test_safe_import_version_returns_version_for_installed_module() -> None:
    # `json` ships with stdlib, has __version__ (string).
    result = _safe_import_version("json")
    assert isinstance(result, str)
    assert result != "not-installed"


def test_safe_import_version_returns_not_installed_for_missing() -> None:
    assert (
        _safe_import_version("a_module_that_will_never_exist_xyz_123")
        == "not-installed"
    )


# ---------------------------------------------------------------------------
# classify_venv
# ---------------------------------------------------------------------------


def test_classify_venv_worktree_local(tmp_path: Path) -> None:
    """When sys.prefix matches <repo>/.venv, returns 'worktree-local'."""
    repo = tmp_path / "repo"
    repo.mkdir()
    venv = repo / ".venv"
    venv.mkdir()
    label, location = classify_venv(str(venv), str(repo))
    assert label == "worktree-local"
    assert location == str(venv.resolve())


def test_classify_venv_misconfigured_when_prefix_is_system(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When sys.prefix is e.g. system Python, returns MISCONFIGURED."""
    repo = tmp_path / "repo"
    repo.mkdir()
    # Use a path that is definitely not a venv path
    fake_system_prefix = "/usr"
    # Suppress the git subprocess by passing a non-git repo path.
    label, location = classify_venv(fake_system_prefix, str(repo))
    assert label == "MISCONFIGURED"
    assert location == str(Path(fake_system_prefix).resolve())


def test_classify_venv_main_repo_via_git_common_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When sys.prefix matches <main_repo>/.venv (from a worktree subdir),
    returns 'main-repo'."""
    main_repo = tmp_path / "main"
    main_repo.mkdir()
    main_venv = main_repo / ".venv"
    main_venv.mkdir()
    worktree = tmp_path / "worktree"
    worktree.mkdir()

    # Monkey-patch _resolve_main_repo to skip the git subprocess call.
    import probe_versions

    monkeypatch.setattr(probe_versions, "_resolve_main_repo", lambda _: str(main_repo))
    label, location = classify_venv(str(main_venv), str(worktree))
    assert label == "main-repo"
    assert location == str(main_venv.resolve())


# ---------------------------------------------------------------------------
# format_line
# ---------------------------------------------------------------------------


def test_format_line_happy_path() -> None:
    facts = {
        "python": "3.12.13",
        "chromadb": "1.5.9",
        "mempalace": "3.3.5",
        "venv": "/repo/.venv",
        "label": "worktree-local",
    }
    line = format_line(facts)
    assert "python=3.12.13" in line
    assert "chromadb=1.5.9" in line
    assert "mempalace=3.3.5" in line
    assert "venv=/repo/.venv (worktree-local)" in line


def test_format_line_misconfigured_emits_loud_marker() -> None:
    facts = {
        "python": "3.9.6",
        "chromadb": "1.4.1",
        "mempalace": "3.3.3",
        "venv": "/usr",
        "label": "MISCONFIGURED",
    }
    line = format_line(facts)
    assert "MISCONFIGURED" in line
    assert "scrub_env.sh did not source" in line
    assert "system Python won" in line


def test_format_line_handles_not_installed() -> None:
    facts = {
        "python": "3.12.13",
        "chromadb": "not-installed",
        "mempalace": "not-installed",
        "venv": "/some/path",
        "label": "main-repo",
    }
    line = format_line(facts)
    assert "chromadb=not-installed" in line
    assert "mempalace=not-installed" in line


# ---------------------------------------------------------------------------
# _resolve_main_repo
# ---------------------------------------------------------------------------


def test_resolve_main_repo_returns_none_when_not_git(tmp_path: Path) -> None:
    """In a non-git dir, the function returns None."""
    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    result = _resolve_main_repo(str(plain))
    assert result is None


# ---------------------------------------------------------------------------
# gather (integration shape)
# ---------------------------------------------------------------------------


def test_gather_returns_expected_keys(tmp_path: Path) -> None:
    """gather always returns the five expected keys regardless of state."""
    repo = tmp_path / "repo"
    repo.mkdir()
    facts = gather(str(repo))
    assert set(facts.keys()) == {"python", "chromadb", "mempalace", "venv", "label"}
    # Python version should be the actually-running interpreter.
    assert facts["python"] == sys.version.split()[0]


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


def test_main_default_emits_stdout_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--repo", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.startswith("[session-start] Versions:")
    assert "python=" in out
    assert "chromadb=" in out
    assert "mempalace=" in out


def test_main_json_emits_facts_dict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--json", "--repo", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    facts = json.loads(out)
    assert set(facts.keys()) == {"python", "chromadb", "mempalace", "venv", "label"}
