"""Unit tests for :mod:`engine.tools.hang_diagnostic`.

Coverage targets the four invariants the module's contract names:

1. **Best-effort.** A subprocess failure (FileNotFoundError, TimeoutExpired,
   nonzero exit) becomes a ``None`` field, not a raised exception.
2. **Bounded.** Per-subprocess timeout is respected; mocking a slow subprocess
   still produces a dump.
3. **Secret-scrubbing.** Keys matching the secret-pattern list are redacted
   in ``env_scrubbed`` while non-secret keys pass through.
4. **Lazy directory creation.** ``.engine_reports/`` is created at first
   dump, not at import time.

The tests do NOT exercise the integration with ``validate._watchdog`` —
that path lives in ``test_validate.py::TestReadGraphFromDbTimeouts``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Path-extension shim — the existing tests in this directory rely on
# pytest's conftest hoisting to make ``import hang_diagnostic`` work
# from the package's flat layout.
sys.path.insert(0, str(Path(__file__).parent))

import hang_diagnostic  # noqa: E402


class TestCaptureHangDiagnostic:
    """Top-level ``capture_hang_diagnostic`` produces a well-shaped dump."""

    def test_dump_file_has_expected_top_level_keys(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Every contract-documented field appears in the JSON output."""
        monkeypatch.chdir(tmp_path)

        result = hang_diagnostic.capture_hang_diagnostic("unit_test")

        assert result is not None
        assert result.exists()
        payload = json.loads(result.read_text())
        expected_keys = {
            "timestamp_utc",
            "label",
            "pid",
            "ppid",
            "platform",
            "python_executable",
            "python_version",
            "psycopg_version",
            "proc_self",
            "python_procs",
            "lsof_self",
            "netstat_supabase",
            "python_modules_sample",
            "thread_stacks",
            "env_scrubbed",
            "sample_stack",
        }
        assert set(payload.keys()) == expected_keys
        assert payload["label"] == "unit_test"
        # pid defaults to os.getpid(); a fresh pytest invocation always
        # has a positive integer pid.
        assert isinstance(payload["pid"], int) and payload["pid"] > 0

    def test_lazy_output_directory_creation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``.engine_reports/`` is created on first dump.

        Guards against import-time directory creation that would leak
        the directory into the tracked working tree of any caller that
        merely imports the module without firing a capture.
        """
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".engine_reports").exists()

        hang_diagnostic.capture_hang_diagnostic("lazy_dir_test")

        assert (tmp_path / ".engine_reports").is_dir()

    def test_caller_supplied_pid_lands_in_payload(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicit pid argument overrides the os.getpid() default."""
        monkeypatch.chdir(tmp_path)

        result = hang_diagnostic.capture_hang_diagnostic("pid_test", pid=99999)

        assert result is not None
        payload = json.loads(result.read_text())
        assert payload["pid"] == 99999

    def test_filename_carries_timestamp_and_pid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Filename pattern: ``hang-diagnostic-<safe-iso>-<pid>.json``.

        Concurrent captures from different processes (production scenario:
        two pre-commit-hook invocations from sibling worktrees hitting
        the same parent repo) must not collide.
        """
        monkeypatch.chdir(tmp_path)

        result = hang_diagnostic.capture_hang_diagnostic("filename_test", pid=12345)

        assert result is not None
        assert result.name.startswith("hang-diagnostic-")
        assert result.name.endswith("-12345.json")
        # No colons in filename — portability guard.
        assert ":" not in result.name


class TestSubprocessFailureModes:
    """Subprocess failures degrade gracefully to None fields."""

    def test_command_not_found_returns_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``FileNotFoundError`` from ``subprocess.run`` -> field is None.

        Models the scenario of running on a Linux box that lacks the
        macOS-specific ``sample`` tool (or vice versa). Captured fields
        must be ``None``, not absent — the JSON shape stays stable across
        platforms.
        """
        monkeypatch.chdir(tmp_path)

        def raise_fnf(*_args: Any, **_kwargs: Any) -> Any:
            raise FileNotFoundError("simulated: command not found")

        with patch.object(subprocess, "run", side_effect=raise_fnf):
            result = hang_diagnostic.capture_hang_diagnostic("fnf_test")

        assert result is not None
        payload = json.loads(result.read_text())
        # All subprocess-derived fields must be None.
        assert payload["proc_self"] is None
        assert payload["python_procs"] is None
        assert payload["lsof_self"] is None
        assert payload["netstat_supabase"] is None
        assert payload["sample_stack"] is None
        # Non-subprocess fields stay populated.
        assert payload["label"] == "fnf_test"
        assert payload["python_modules_sample"]  # truthy list
        assert payload["thread_stacks"]  # truthy dict

    def test_timeout_returns_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``TimeoutExpired`` from ``subprocess.run`` -> field is None.

        Models the production scenario the module is built for: a wedged
        process can hang our diagnostic tools too. The per-call timeout
        keeps the capture bounded.
        """
        monkeypatch.chdir(tmp_path)

        def raise_timeout(*_args: Any, **_kwargs: Any) -> Any:
            raise subprocess.TimeoutExpired(cmd="stub", timeout=5.0)

        with patch.object(subprocess, "run", side_effect=raise_timeout):
            result = hang_diagnostic.capture_hang_diagnostic("timeout_test")

        assert result is not None
        payload = json.loads(result.read_text())
        assert payload["proc_self"] is None
        assert payload["lsof_self"] is None

    def test_run_command_handles_nonzero_exit_with_stderr(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Nonzero exit code with stderr -> returns stderr (still useful).

        ``ps`` against a dead pid exits nonzero with a stderr message;
        the dump should carry that message rather than silently ``None``.
        """
        stub_result = subprocess.CompletedProcess(
            args=["ps", "-p", "0"],
            returncode=1,
            stdout="",
            stderr="ps: no such process: 0\n",
        )
        with patch.object(subprocess, "run", return_value=stub_result):
            out = hang_diagnostic._run_command(["ps", "-p", "0"])
        assert out is not None
        assert "no such process" in out


class TestSecretScrubbing:
    """``env_scrubbed`` redacts secret-pattern keys while preserving shape."""

    def test_supabase_db_url_is_redacted(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The load-bearing case: SUPABASE_DB_URL must never leak.

        The diagnostic file is gitignored, but the redaction is the
        last line of defense against accidental exfiltration via an
        attached debug log or a future un-gitignored audit surface.
        """
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv(
            "SUPABASE_DB_URL", "postgresql://user:secretpw@pooler.supabase.co:6543/db"
        )

        result = hang_diagnostic.capture_hang_diagnostic("scrub_test")

        assert result is not None
        payload = json.loads(result.read_text())
        assert payload["env_scrubbed"]["SUPABASE_DB_URL"] == "<redacted>"
        # Key remains visible so absence-vs-presence-of-the-key signal
        # is preserved (load-bearing for the contamination hypothesis).
        assert "SUPABASE_DB_URL" in payload["env_scrubbed"]

    def test_secret_patterns_match_case_insensitive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """All five patterns (KEY/SECRET/TOKEN/PASSWORD/URL) redact.

        Lowercased and mixed-case key names must also redact — env var
        names are conventionally upper but lowercased names appear in
        tests, in custom configs, and as substrings within longer keys.
        """
        monkeypatch.chdir(tmp_path)
        cases = {
            "MY_API_KEY": "value-1",
            "client_secret": "value-2",
            "GITHUB_TOKEN": "value-3",
            "DB_PASSWORD": "value-4",
            "PUBLIC_URL": "value-5",
        }
        for k, v in cases.items():
            monkeypatch.setenv(k, v)

        result = hang_diagnostic.capture_hang_diagnostic("pattern_test")

        assert result is not None
        payload = json.loads(result.read_text())
        for key in cases:
            assert payload["env_scrubbed"][key] == "<redacted>", (
                f"key {key!r} should be redacted; pattern match must be "
                f"case-insensitive against KEY/SECRET/TOKEN/PASSWORD/URL"
            )

    def test_non_secret_keys_pass_through(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Non-secret keys must NOT be redacted.

        The contamination hypothesis depends on seeing the actual values
        of PYTHONPATH, PYTHONHOME, PYTHONUSERBASE, VIRTUAL_ENV, PATH —
        these must pass through verbatim so an investigation can spot
        the leak.
        """
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("PYTHONPATH", "/opt/contaminant/site-packages")
        monkeypatch.setenv("VIRTUAL_ENV", "/path/to/venv")

        result = hang_diagnostic.capture_hang_diagnostic("passthrough_test")

        assert result is not None
        payload = json.loads(result.read_text())
        assert payload["env_scrubbed"]["PYTHONPATH"] == "/opt/contaminant/site-packages"
        assert payload["env_scrubbed"]["VIRTUAL_ENV"] == "/path/to/venv"


class TestThreadStacks:
    """``thread_stacks`` captures every live thread's call stack."""

    def test_thread_stacks_includes_main_thread(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The current thread always shows up in the dump.

        The main thread is the watchdog target in production — its
        stack is the most load-bearing piece of evidence for diagnosing
        a poll()-blocked psycopg call.
        """
        monkeypatch.chdir(tmp_path)

        result = hang_diagnostic.capture_hang_diagnostic("thread_test")

        assert result is not None
        payload = json.loads(result.read_text())
        stacks = payload["thread_stacks"]
        assert len(stacks) >= 1
        # At least one stack frame should reference this test file —
        # confirms _current_frames() reached the calling thread.
        all_frames = "\n".join(line for stack in stacks.values() for line in stack)
        assert "test_hang_diagnostic" in all_frames


class TestOutputDirFailure:
    """A failed directory creation returns None rather than raising."""

    def test_mkdir_failure_returns_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An ``OSError`` from ``Path.mkdir`` -> capture returns None.

        Defense against running in a read-only filesystem context (a
        sandboxed CI runner, a read-only checkout, etc.). The watchdog
        must continue to function (call conn.cancel()) even when the
        diagnostic capture cannot persist its output.
        """
        monkeypatch.chdir(tmp_path)

        def raise_oserror(*_args: Any, **_kwargs: Any) -> Any:
            raise OSError("simulated: read-only filesystem")

        with patch.object(Path, "mkdir", side_effect=raise_oserror):
            result = hang_diagnostic.capture_hang_diagnostic("mkdir_fail_test")

        assert result is None
