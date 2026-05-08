"""Tests for engine/tools/validate.py's validate_timestamp_helper_bypass().

Per ADR 0058 / Issue #33. Covers AST-walk detection of ``.isoformat(...)``,
``.strftime(...)``, and ``.fromisoformat(...)`` callsites in
``engine/tools/**/*.py`` outside the helper-routing allowlist; allowlist
honoring (`timestamps.py`, `apply_migration.py`); test-file exclusion;
parse-error and read-error tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402
from validate import validate_timestamp_helper_bypass  # noqa: E402


@pytest.fixture
def stub_tools(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build a tmp_path/engine/tools/ tree the validator will walk."""
    tools_dir = tmp_path / "engine" / "tools"
    tools_dir.mkdir(parents=True)
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    return tools_dir


class TestValidateTimestampHelperBypass:
    def test_no_python_files_no_warns(self, stub_tools: Path) -> None:
        """Empty tools dir produces zero warns and one check entry."""
        result = validate_timestamp_helper_bypass()
        assert result.checks_run == ["timestamp_helper_bypass"]
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_clean_tool_no_warns(self, stub_tools: Path) -> None:
        """A tool that imports the helper and uses no ad-hoc emission is clean."""
        (stub_tools / "clean_tool.py").write_text(
            "from timestamps import emit\ndef f() -> str:\n    return emit()\n"
        )
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_isoformat_call_fires_warn(self, stub_tools: Path) -> None:
        """A bare .isoformat() call fires the soft-warn."""
        (stub_tools / "bad_tool.py").write_text(
            "from datetime import datetime, timezone\n"
            "def f() -> str:\n"
            "    return datetime.now(timezone.utc).isoformat()\n"
        )
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 1
        assert "bad_tool.py:3" in warns[0]
        assert ".isoformat" in warns[0]

    def test_strftime_call_fires_warn(self, stub_tools: Path) -> None:
        """A bare .strftime(...) call fires the soft-warn."""
        (stub_tools / "bad_tool.py").write_text(
            "from datetime import datetime, timezone\n"
            "def f() -> str:\n"
            '    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")\n'
        )
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 1
        assert "bad_tool.py:3" in warns[0]
        assert ".strftime" in warns[0]

    def test_fromisoformat_call_fires_warn(self, stub_tools: Path) -> None:
        """A bare .fromisoformat() call fires the soft-warn (parse-site bypass)."""
        (stub_tools / "bad_parser.py").write_text(
            "from datetime import datetime\n"
            "def f(s: str) -> datetime:\n"
            "    return datetime.fromisoformat(s)\n"
        )
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 1
        assert "bad_parser.py:3" in warns[0]
        assert ".fromisoformat" in warns[0]

    def test_multiple_callsites_in_one_file_each_fire(self, stub_tools: Path) -> None:
        """Two bypasses in one file → two warns with distinct line numbers."""
        (stub_tools / "double.py").write_text(
            "from datetime import datetime, timezone\n"
            "def a() -> str:\n"
            "    return datetime.now(timezone.utc).isoformat()\n"
            "def b() -> str:\n"
            '    return datetime.now(timezone.utc).strftime("%Y")\n'
        )
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 2
        assert any("double.py:3" in w for w in warns)
        assert any("double.py:5" in w for w in warns)

    def test_timestamps_helper_allowlisted(self, stub_tools: Path) -> None:
        """timestamps.py itself is allowlisted (defines canonical shapes)."""
        (stub_tools / "timestamps.py").write_text(
            "from datetime import datetime, timezone\n"
            'def emit() -> str: return datetime.now(timezone.utc).strftime("%Y")\n'
        )
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_apply_migration_allowlisted(self, stub_tools: Path) -> None:
        """apply_migration.py is allowlisted (legacy supabase contract)."""
        (stub_tools / "apply_migration.py").write_text(
            "from datetime import datetime, timezone\n"
            'def version() -> str: return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")\n'
        )
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_test_files_excluded(self, stub_tools: Path) -> None:
        """test_*.py files are excluded (legitimate fixture timestamps)."""
        (stub_tools / "test_something.py").write_text(
            "from datetime import datetime, timezone\n"
            "def test_thing() -> None:\n"
            "    fixture = datetime.now(timezone.utc).isoformat()\n"
            "    assert fixture\n"
        )
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_syntax_error_emits_skip_warn(self, stub_tools: Path) -> None:
        """Unparseable file emits a single skip-warn rather than a crash."""
        (stub_tools / "broken.py").write_text("def f(:\n  return 1\n")  # syntax error
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 1
        assert "broken.py" in warns[0]
        assert "parse failed" in warns[0]

    def test_nested_subdirectory_walked(self, stub_tools: Path) -> None:
        """rglob walks subdirectories (e.g., engine/tools/hooks/foo.py)."""
        nested = stub_tools / "subdir"
        nested.mkdir()
        (nested / "deep.py").write_text(
            "from datetime import datetime, timezone\n"
            "def f() -> str: return datetime.now(timezone.utc).isoformat()\n"
        )
        result = validate_timestamp_helper_bypass()
        warns = result.soft_warns.get("timestamp_helper_bypass", [])
        assert len(warns) == 1
        assert "subdir/deep.py:2" in warns[0]

    def test_unrelated_attribute_call_not_flagged(self, stub_tools: Path) -> None:
        """Other .strftime-shaped attribute calls (e.g., on dict objects) do
        not exist in normal Python code, but unrelated attribute calls like
        .upper() should not fire.
        """
        (stub_tools / "unrelated.py").write_text(
            "def f(s: str) -> str: return s.upper().strip()\n"
        )
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []

    def test_non_python_files_ignored(self, stub_tools: Path) -> None:
        """Shell scripts and Markdown files are not walked."""
        (stub_tools / "hooks").mkdir()
        (stub_tools / "hooks" / "thing.sh").write_text(
            'date -u +"%Y-%m-%dT%H:%M:%SZ"\n'
        )
        (stub_tools / "README.md").write_text("# Tools\n")
        result = validate_timestamp_helper_bypass()
        assert result.soft_warns.get("timestamp_helper_bypass", []) == []
