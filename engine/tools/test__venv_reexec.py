"""Tests for engine/tools/_venv_reexec.py — Issue #14 (S-0055)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_reexec import ensure_venv_python  # noqa: E402


def test_noops_when_module_importable() -> None:
    """If find_spec returns a spec, no re-exec attempted."""
    fake_spec = object()
    with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=fake_spec):
        with mock.patch("_venv_reexec.os.execv") as exec_mock:
            ensure_venv_python("psycopg")
            exec_mock.assert_not_called()


def test_noops_when_already_under_venv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If sys.executable already matches the resolved venv python, no re-exec."""
    venv_python = tmp_path / ".venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    venv_python.chmod(0o755)

    fake_module = tmp_path / "subdir" / "fake_tool.py"
    fake_module.parent.mkdir()
    fake_module.touch()

    monkeypatch.setattr(sys, "executable", str(venv_python.resolve()))
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                exec_mock.assert_not_called()


def test_finds_worktree_local_venv_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Walk-up: worktree-local .venv/ takes precedence over main-repo .venv/."""
    main_repo = tmp_path / "main"
    main_venv_python = main_repo / ".venv" / "bin" / "python3"
    main_venv_python.parent.mkdir(parents=True)
    main_venv_python.touch()
    main_venv_python.chmod(0o755)

    worktree = main_repo / ".claude" / "worktrees" / "wt"
    worktree_venv_python = worktree / ".venv" / "bin" / "python3"
    worktree_venv_python.parent.mkdir(parents=True)
    worktree_venv_python.touch()
    worktree_venv_python.chmod(0o755)

    fake_module = worktree / "engine" / "tools" / "fake_tool.py"
    fake_module.parent.mkdir(parents=True)
    fake_module.touch()

    monkeypatch.setattr(sys, "executable", "/usr/bin/python3")  # not a venv path
    monkeypatch.setattr(sys, "argv", [str(fake_module), "--flag"])
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                # Worktree-local should win (encountered first on walk-up).
                # Path is unresolved so Python sees the venv via pyvenv.cfg lookup.
                expected_python = str(worktree_venv_python)
                exec_mock.assert_called_once_with(
                    expected_python, [expected_python, str(fake_module), "--flag"]
                )


def test_falls_back_to_main_repo_venv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no worktree-local .venv/, walk continues up to main-repo .venv/."""
    main_repo = tmp_path / "main"
    main_venv_python = main_repo / ".venv" / "bin" / "python3"
    main_venv_python.parent.mkdir(parents=True)
    main_venv_python.touch()
    main_venv_python.chmod(0o755)

    worktree = main_repo / ".claude" / "worktrees" / "wt"
    fake_module = worktree / "engine" / "tools" / "fake_tool.py"
    fake_module.parent.mkdir(parents=True)
    fake_module.touch()
    # Note: no worktree-local .venv/ created.

    monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
    monkeypatch.setattr(sys, "argv", [str(fake_module)])
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                expected_python = str(main_venv_python)
                exec_mock.assert_called_once_with(
                    expected_python, [expected_python, str(fake_module)]
                )


def test_silent_when_no_venv_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No .venv/ anywhere on the walk-up: return silently (caller's import will fail)."""
    fake_module = tmp_path / "isolated" / "fake_tool.py"
    fake_module.parent.mkdir(parents=True)
    fake_module.touch()

    monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
    monkeypatch.setattr(sys, "argv", [str(fake_module)])
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                exec_mock.assert_not_called()
