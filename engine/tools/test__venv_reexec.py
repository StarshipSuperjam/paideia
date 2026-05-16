"""Tests for engine/tools/_venv_reexec.py — Issue #14 (S-0055) + S-0190 fix.

S-0190 added a script-vs-import gate: ``ensure_venv_python()`` no longer
re-execs when imported by another module (e.g., pytest collecting a test
that transitively imports ``validate.py``). The gate compares
``inspect.stack()[1].filename`` against ``sys.modules['__main__'].__file__``;
they match only when the caller IS the invoked script. To exercise the
positive re-exec path, the tests monkeypatch ``sys.modules['__main__']``
to a fake module whose ``__file__`` equals the test file's path —
because that's what ``inspect.stack()[1].filename`` resolves to when
the call frame is inside this test module.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_reexec import ensure_venv_python  # type: ignore[import-not-found]  # noqa: E402


def _fake_main_matching_caller(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make __main__.__file__ equal the test file so the script-vs-import
    gate in ensure_venv_python sees them as matching."""
    fake_main = types.ModuleType("__main__")
    fake_main.__file__ = str(Path(__file__).resolve())
    monkeypatch.setitem(sys.modules, "__main__", fake_main)


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
    _fake_main_matching_caller(monkeypatch)  # S-0190 script-vs-import gate
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
    _fake_main_matching_caller(monkeypatch)  # S-0190 script-vs-import gate
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                expected_python = str(main_venv_python)
                exec_mock.assert_called_once_with(
                    expected_python, [expected_python, str(fake_module)]
                )


def test_imported_caller_skips_reexec_even_without_psycopg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S-0190 fix: when called from import context (caller != __main__),
    ensure_venv_python returns without re-execing.

    This is the regression test for the silent-hang bug: pre-S-0190,
    pytest's collection of test_validate.py triggered a mid-collection
    os.execv that the harness's output capture couldn't follow.
    """
    main_repo = tmp_path / "main"
    venv_python = main_repo / ".venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    venv_python.chmod(0o755)

    fake_module = main_repo / "engine" / "tools" / "fake_tool.py"
    fake_module.parent.mkdir(parents=True)
    fake_module.touch()

    monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
    # Deliberately DO NOT call _fake_main_matching_caller — leave the real
    # __main__ in place (which is pytest, NOT this test file). The gate
    # should detect "imported by pytest" and skip re-exec.
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("_venv_reexec.os.execv") as exec_mock:
                ensure_venv_python("never_importable_xyz_12345")
                exec_mock.assert_not_called()


def test_silent_when_caller_inspection_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If stack-inspection raises, fall through to legacy behavior (attempt
    re-exec) rather than silently no-op. The script-vs-import gate is
    best-effort; a broken inspect call shouldn't strand a genuine direct
    invocation."""
    main_repo = tmp_path / "main"
    venv_python = main_repo / ".venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    venv_python.chmod(0o755)

    fake_module = main_repo / "engine" / "tools" / "fake_tool.py"
    fake_module.parent.mkdir(parents=True)
    fake_module.touch()

    monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
    monkeypatch.setattr(sys, "argv", [str(fake_module)])
    _fake_main_matching_caller(monkeypatch)
    # Force inspect.stack() to fail; fall-through path attempts re-exec.
    with mock.patch("_venv_reexec.__file__", str(fake_module)):
        with mock.patch("_venv_reexec.importlib.util.find_spec", return_value=None):
            with mock.patch("inspect.stack", side_effect=OSError("inspect broken")):
                with mock.patch("_venv_reexec.os.execv") as exec_mock:
                    ensure_venv_python("never_importable_xyz_12345")
                    # Falls through to walk-up + re-exec.
                    exec_mock.assert_called_once()


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
