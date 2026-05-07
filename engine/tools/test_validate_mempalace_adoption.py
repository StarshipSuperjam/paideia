"""Tests for validate.validate_mempalace_adoption — ADR 0056 / S-0078; S-0089 amendment."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402

# Captured at module load before any monkeypatching happens — used by
# TestCheckMempalaceSubstrateAlive to restore the real helper for the
# subprocess-mocking tests in that class.
_REAL_SUBSTRATE_CHECK = validate._check_mempalace_substrate_alive


@pytest.fixture(autouse=True)
def _stub_substrate_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default substrate-alive=True for tests that don't care.

    The S-0089 substrate-availability check (`_check_mempalace_substrate_alive`)
    runs a `python3 -m mempalace status` subprocess on every
    validate_mempalace_adoption call. Tests that don't explicitly probe
    the substrate path get a stable True default so they don't hit the
    real mempalace install on the dev machine. Tests that DO care (the
    S-0089 substrate / token-tightening branches) override the fixture
    with their own monkeypatch.
    """
    monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: True)


def _make_activity(**overrides: int) -> dict[str, object]:
    base: dict[str, object] = {
        "search_calls": 0,
        "diary_read_calls": 0,
        "diary_write_calls": 0,
        "add_drawer_calls": 0,
        "status_calls": 0,
        "list_drawers_calls": 0,
        "kg_calls": 0,
        "tunnel_calls": 0,
        "other_calls": 0,
        "total_calls": 0,
        "first_call_ts": None,
        "last_call_ts": None,
    }
    base.update(overrides)
    return base


def _write_current(
    tmp_path: Path,
    activity: dict[str, object] | None,
    outcome_summary: str | None = None,
) -> Path:
    payload: dict[str, object] = {"id": "S-0078", "mode": "interactive"}
    if activity is not None:
        payload["mempalace_activity"] = activity
    if outcome_summary is not None:
        payload["outcome_summary"] = outcome_summary
    p = tmp_path / "current.json"
    p.write_text(json.dumps(payload))
    return p


def _patch_repo_root_to(tmp_path: Path) -> "mock._patch[Path]":
    """Patch validate.REPO_ROOT to a tmp_path layout containing engine/session/."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    return mock.patch.object(validate, "REPO_ROOT", tmp_path)


def test_no_current_returns_clean(tmp_path: Path) -> None:
    """Default-mode (no current.json) → no checks fire, no warnings."""
    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.checks_run) == 1
        assert len(result.hard_fails) == 0
        assert len(result.soft_warns) == 0


def test_all_calls_present_clean(tmp_path: Path) -> None:
    """Search + diary_read + diary_write all > 0 → clean."""
    _write_current(
        tmp_path,
        _make_activity(search_calls=2, diary_read_calls=1, diary_write_calls=1),
    )
    # Move the file under the expected path.
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        (tmp_path / "current.json").read_text()
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert len(result.soft_warns) == 0


def test_search_skipped_soft_warns(tmp_path: Path) -> None:
    """No search call → soft-warn mempalace_boot_query_skipped."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": _make_activity(
                    diary_read_calls=1, diary_write_calls=1
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_boot_query_skipped" in result.soft_warns


def test_diary_read_skipped_soft_warns(tmp_path: Path) -> None:
    """No diary_read call → soft-warn mempalace_diary_read_skipped."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": _make_activity(
                    search_calls=1, diary_write_calls=1
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_diary_read_skipped" in result.soft_warns


def test_diary_write_skipped_hard_fails(tmp_path: Path) -> None:
    """No diary_write call AND no acknowledgement → HARD-FAIL."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": _make_activity(
                    search_calls=1, diary_read_calls=1
                ),
                "outcome_summary": "Did stuff this session.",
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 1
        assert "mempalace_diary_write_skipped" in result.hard_fails[0]


def test_diary_write_skip_with_acknowledgement_downgrades(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Acknowledgement token + substrate genuinely down → soft-warn (S-0089 contract)."""
    monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": _make_activity(
                    search_calls=1, diary_read_calls=1
                ),
                "outcome_summary": (
                    "Did stuff. mempalace_unavailable_acknowledged: MCP server "
                    "unreachable mid-session; diary write deferred."
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_diary_write_acknowledged_skip" in result.soft_warns
        # Substrate-at-close fires when substrate is unreachable, regardless
        # of diary-write state (per S-0089 — surfaces broken substrate as
        # its own signal).
        assert "mempalace_substrate_at_close" in result.soft_warns


def test_three_categories_fire_in_one_session(tmp_path: Path) -> None:
    """All-zero activity (and no acknowledgement) → 2 soft-warns + 1 hard-fail."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0078",
                "mempalace_activity": _make_activity(),
                "outcome_summary": "Nothing happened.",
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert "mempalace_boot_query_skipped" in result.soft_warns
        assert "mempalace_diary_read_skipped" in result.soft_warns
        assert len(result.hard_fails) == 1


# ---------------------------------------------------------------------------
# S-0089 amendment: substrate-availability + token-tightening
# ---------------------------------------------------------------------------


class TestSubstrateTokenTightening:
    """ADR 0056 token contract per S-0089: token valid only when substrate fails."""

    def _make_session(
        self,
        tmp_path: Path,
        *,
        mode: str = "interactive",
        diary_write_calls: int = 0,
        outcome_summary: str = "",
    ) -> None:
        (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
        (tmp_path / "engine" / "session" / "current.json").write_text(
            json.dumps(
                {
                    "id": "S-0089",
                    "mode": mode,
                    "mempalace_activity": _make_activity(
                        search_calls=1,
                        diary_read_calls=1,
                        diary_write_calls=diary_write_calls,
                    ),
                    "outcome_summary": outcome_summary,
                }
            )
        )

    def test_token_invalid_when_substrate_alive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Token + substrate alive → hard-fail invalid_token (S-0087/S-0088 burial pattern)."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: True)
        self._make_session(
            tmp_path,
            outcome_summary=(
                "Worked on stuff. "
                "mempalace_unavailable_acknowledged: MCP not connected."
            ),
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            assert len(result.hard_fails) == 1
            assert "mempalace_diary_write_skipped_invalid_token" in result.hard_fails[0]
            # The standard acknowledged-skip soft-warn does NOT fire when
            # the token is invalidated — only the hard-fail.
            assert "mempalace_diary_write_acknowledged_skip" not in result.soft_warns

    def test_token_valid_when_substrate_down(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Token + substrate down → soft-warn (genuinely unreachable)."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(
            tmp_path,
            outcome_summary=(
                "Worked on stuff. mempalace_unavailable_acknowledged: substrate down."
            ),
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            assert len(result.hard_fails) == 0
            assert "mempalace_diary_write_acknowledged_skip" in result.soft_warns

    def test_engine_session_acknowledged_skip_uses_loud_body(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Interactive (engine) sessions get the LOUD ⚠️ prefix on the soft-warn body."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(
            tmp_path,
            mode="interactive",
            outcome_summary=(
                "Worked. mempalace_unavailable_acknowledged: substrate down."
            ),
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            body = result.soft_warns["mempalace_diary_write_acknowledged_skip"][0]
            assert body.startswith("⚠️")
            assert "DO NOT BURY THIS" in body

    def test_routine_session_acknowledged_skip_uses_standard_body(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Routine sessions get a one-line standard body (unattended; no LOUD)."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(
            tmp_path,
            mode="routine",
            outcome_summary=(
                "Routine work. mempalace_unavailable_acknowledged: substrate down."
            ),
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            body = result.soft_warns["mempalace_diary_write_acknowledged_skip"][0]
            assert not body.startswith("⚠️")

    def test_substrate_at_close_fires_independently_of_diary_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Substrate down + diary write done → substrate_at_close still fires."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(tmp_path, diary_write_calls=1, outcome_summary="Clean run.")

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            assert len(result.hard_fails) == 0
            assert "mempalace_substrate_at_close" in result.soft_warns

    def test_substrate_at_close_silent_when_alive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Substrate alive → substrate_at_close check runs but does NOT fire."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: True)
        self._make_session(tmp_path, diary_write_calls=1, outcome_summary="Clean run.")

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            assert len(result.hard_fails) == 0
            assert "mempalace_substrate_at_close" not in result.soft_warns
            # Check is registered even when not firing (telemetry distinguishes
            # "ran clean" from "did not run" per soft-warn-lifecycle.md).
            assert "mempalace_substrate_at_close" in result.checks_run

    def test_substrate_at_close_engine_loud_body(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Substrate down + engine mode → substrate_at_close body is LOUD."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(
            tmp_path, diary_write_calls=1, mode="interactive", outcome_summary="x"
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            body = result.soft_warns["mempalace_substrate_at_close"][0]
            assert body.startswith("⚠️")
            assert "DO NOT BURY THIS" in body

    def test_substrate_at_close_routine_standard_body(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Substrate down + routine mode → substrate_at_close body is standard."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: False)
        self._make_session(
            tmp_path, diary_write_calls=1, mode="routine", outcome_summary="x"
        )

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            body = result.soft_warns["mempalace_substrate_at_close"][0]
            assert not body.startswith("⚠️")
            assert "MemPalace substrate is unreachable" in body

    def test_no_diary_no_token_substrate_alive_hard_fails(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No diary write + no token + substrate alive → existing hard-fail still fires."""
        monkeypatch.setattr(validate, "_check_mempalace_substrate_alive", lambda: True)
        self._make_session(tmp_path, outcome_summary="No reflection here.")

        with _patch_repo_root_to(tmp_path):
            result = validate.validate_mempalace_adoption()
            assert len(result.hard_fails) == 1
            assert "mempalace_diary_write_skipped" in result.hard_fails[0]
            # The S-0089 message references the tightened contract.
            assert "S-0089 tightening" in result.hard_fails[0]


class TestCheckMempalaceSubstrateAlive:
    """The substrate-availability subprocess helper."""

    @pytest.fixture(autouse=True)
    def _use_real_helper(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Restore the real helper so subprocess-mock tests reach the
        real implementation.

        The module-level ``_stub_substrate_alive`` autouse fixture
        replaces ``_check_mempalace_substrate_alive`` with a constant-
        True lambda for tests that don't care about substrate logic.
        Tests in this class DO care — they exercise the
        subprocess.run-driven branches — so this class-level autouse
        fixture re-monkeypatches the real implementation after the
        module-level one has run.
        """
        monkeypatch.setattr(
            validate, "_check_mempalace_substrate_alive", _REAL_SUBSTRATE_CHECK
        )

    def test_returns_true_on_zero_exit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _OK:
            returncode = 0

        def fake_run(*args: object, **kwargs: object) -> _OK:
            return _OK()

        monkeypatch.setattr("validate.subprocess.run", fake_run)
        assert validate._check_mempalace_substrate_alive() is True

    def test_returns_false_on_nonzero_exit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class _Fail:
            returncode = 1

        def fake_run(*args: object, **kwargs: object) -> _Fail:
            return _Fail()

        monkeypatch.setattr("validate.subprocess.run", fake_run)
        assert validate._check_mempalace_substrate_alive() is False

    def test_returns_false_when_cli_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run(*args: object, **kwargs: object) -> None:
            raise FileNotFoundError("mempalace not on PATH")

        monkeypatch.setattr("validate.subprocess.run", fake_run)
        assert validate._check_mempalace_substrate_alive() is False

    def test_returns_false_on_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*args: object, **kwargs: object) -> None:
            raise subprocess.TimeoutExpired(cmd=["mempalace"], timeout=8)

        monkeypatch.setattr("validate.subprocess.run", fake_run)
        assert validate._check_mempalace_substrate_alive() is False

    def test_uses_python_dash_m_form(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Per ADR 0050 / S-0089: invoke via `python3 -m mempalace` not bare `mempalace`."""
        captured: list[list[str]] = []

        class _OK:
            returncode = 0

        def fake_run(cmd: list[str], **kwargs: object) -> _OK:
            captured.append(cmd)
            return _OK()

        monkeypatch.setattr("validate.subprocess.run", fake_run)
        validate._check_mempalace_substrate_alive()
        assert len(captured) == 1
        cmd = captured[0]
        # First arg is sys.executable (varies by environment); second is "-m";
        # third is "mempalace"; fourth is the subcommand.
        assert cmd[1] == "-m"
        assert cmd[2] == "mempalace"
        assert cmd[3] == "status"


def test_missing_activity_field_skips_audit(tmp_path: Path) -> None:
    """If mempalace_activity is absent (scan tool didn't run), skip — the
    structural audit catches it."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"id": "S-0078", "mode": "interactive"})
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        # No checks beyond the marker — the field is absent so we don't audit.
        assert len(result.hard_fails) == 0
        assert len(result.soft_warns) == 0


def test_malformed_current_json_skips(tmp_path: Path) -> None:
    """Bad JSON in current.json → no audit emission (validate_repo_structure
    catches this elsewhere)."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text("{ not valid")

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert len(result.soft_warns) == 0


# ---------------------------------------------------------------------------
# mempalace_retired_surface_used (S-0087 / ADR 0056 Consequences amendment)
# ---------------------------------------------------------------------------


def test_kg_call_fires_retired_surface_warn(tmp_path: Path) -> None:
    """kg_calls > 0 → soft-warn mempalace_retired_surface_used."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0087",
                "mempalace_activity": _make_activity(
                    search_calls=1, diary_read_calls=1, diary_write_calls=1, kg_calls=1
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_retired_surface_used" in result.soft_warns


def test_tunnel_call_fires_retired_surface_warn(tmp_path: Path) -> None:
    """tunnel_calls > 0 → soft-warn mempalace_retired_surface_used."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0087",
                "mempalace_activity": _make_activity(
                    search_calls=1,
                    diary_read_calls=1,
                    diary_write_calls=1,
                    tunnel_calls=2,
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_retired_surface_used" in result.soft_warns


def test_both_kg_and_tunnel_fire_single_warn(tmp_path: Path) -> None:
    """Both kg_calls > 0 AND tunnel_calls > 0 → ONE soft-warn naming both counts."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0087",
                "mempalace_activity": _make_activity(
                    search_calls=1,
                    diary_read_calls=1,
                    diary_write_calls=1,
                    kg_calls=3,
                    tunnel_calls=2,
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        # Single soft-warn entry, not two separate ones.
        assert "mempalace_retired_surface_used" in result.soft_warns
        # Body names both counts so the user can see the scope of the regression.
        # soft_warns values are lists of message strings.
        bodies = result.soft_warns["mempalace_retired_surface_used"]
        assert any("kg_calls=3" in b for b in bodies)
        assert any("tunnel_calls=2" in b for b in bodies)


def test_zero_kg_and_tunnel_no_retired_surface_warn(tmp_path: Path) -> None:
    """kg_calls == 0 AND tunnel_calls == 0 → NO retired-surface warn (default state)."""
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps(
            {
                "id": "S-0087",
                "mempalace_activity": _make_activity(
                    search_calls=1, diary_read_calls=1, diary_write_calls=1
                ),
            }
        )
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert "mempalace_retired_surface_used" not in result.soft_warns


def test_legacy_activity_without_kg_tunnel_fields_no_warn(tmp_path: Path) -> None:
    """Pre-S-0087 archives lack kg_calls/tunnel_calls fields entirely;
    validate must treat absence as zero (defensive .get default), not crash
    or fire the retired-surface warn spuriously."""
    legacy_activity: dict[str, object] = {
        "search_calls": 1,
        "diary_read_calls": 1,
        "diary_write_calls": 1,
        "add_drawer_calls": 0,
        "status_calls": 0,
        "list_drawers_calls": 0,
        "other_calls": 0,
        "total_calls": 3,
        "first_call_ts": "2026-05-06T00:00:00Z",
        "last_call_ts": "2026-05-06T00:01:00Z",
    }
    (tmp_path / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "session" / "current.json").write_text(
        json.dumps({"id": "S-0086", "mempalace_activity": legacy_activity})
    )

    with _patch_repo_root_to(tmp_path):
        result = validate.validate_mempalace_adoption()
        assert len(result.hard_fails) == 0
        assert "mempalace_retired_surface_used" not in result.soft_warns
