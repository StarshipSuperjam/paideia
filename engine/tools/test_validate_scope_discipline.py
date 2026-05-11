"""Tests for validate_scope_discipline (per ADR 0049).

The function reads engine/session/current.json and emits up to three
soft-warns. Tests use monkeypatch to redirect REPO_ROOT to a tmp_path
fixture so each test runs against a synthetic project.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402


def _make_repo(
    tmp_path: Path,
    declared_scope: object = None,
    scope_delivery: object = None,
    manifest_text: str | None = None,
    mode: str | None = "routine",
) -> Path:
    """Build a minimal synthetic repo under tmp_path and return it.

    Default mode is "routine" because that is the mode against which
    declared_scope checks are gated post-S-0125 (S-0121 audit Retire-F).
    Tests that exercise the interactive-session no-warn path pass
    mode="build" or mode=None.
    """
    sess_dir = tmp_path / "engine" / "session"
    sess_dir.mkdir(parents=True)
    payload: dict[str, object] = {
        "id": "S-0001",
        "started_at": "2026-05-04T00:00:00Z",
        "status": "in_progress",
    }
    if mode is not None:
        payload["mode"] = mode
    if declared_scope is not None:
        payload["declared_scope"] = declared_scope
    if scope_delivery is not None:
        payload["scope_delivery"] = scope_delivery
    (sess_dir / "current.json").write_text(json.dumps(payload))

    if manifest_text is not None:
        (tmp_path / "build_plan").mkdir(parents=True)
        (tmp_path / "build_plan" / "MANIFEST.md").write_text(manifest_text)

    return tmp_path


def test_skips_when_current_json_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert r.hard_fails == []
    assert r.soft_warns == {}


def test_soft_warn_on_missing_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(tmp_path)  # No declared_scope written.
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" in r.soft_warns
    assert r.soft_warns["empty_declared_scope"]


def test_soft_warn_on_empty_string(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(tmp_path, declared_scope="")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" in r.soft_warns


def test_soft_warn_on_whitespace_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(tmp_path, declared_scope="   \n  \t  ")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" in r.soft_warns


def test_clean_when_field_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(tmp_path, declared_scope="Doing useful work this session.")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" not in r.soft_warns


def test_na_phase_token_skips_manifest_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """phase: NA-... is the operational opt-out marker."""
    _make_repo(
        tmp_path,
        declared_scope="Operational work. phase: NA-engine-apparatus",
        manifest_text="# Build Plan Manifest\n\n| Phase | ID |\n|---|---|\n| 3 | P_3 |\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "phase_mismatch_declared_scope" not in r.soft_warns


def test_phase_mismatch_when_token_not_in_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(
        tmp_path,
        declared_scope="Working on phase 99 of the build plan. phase: P_99",
        manifest_text="# Build Plan\n\n- P_3 SQL\n- P_4 Graph\n- P_5 Seed\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "phase_mismatch_declared_scope" in r.soft_warns


def test_phase_match_when_token_in_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(
        tmp_path,
        declared_scope="Phase 3 SQL build. phase: P_3",
        manifest_text="# Build Plan\n\n- P_3 SQL\n- P_4 Graph\n- P_5 Seed\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "phase_mismatch_declared_scope" not in r.soft_warns


def test_phase_match_tolerates_decimal_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """phase: 4.5 should match a manifest naming Phase 4.5."""
    _make_repo(
        tmp_path,
        declared_scope="Survey for phase 4.5. phase: 4.5",
        manifest_text="# Build Plan\n\n- Phase 4.5 — Input Dataset Survey\n",
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "phase_mismatch_declared_scope" not in r.soft_warns


def test_no_phase_token_no_mismatch_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A scope without any phase: token doesn't trigger mismatch."""
    _make_repo(tmp_path, declared_scope="Doing operational work.")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "phase_mismatch_declared_scope" not in r.soft_warns


def test_scope_delivery_non_yes_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(
        tmp_path,
        declared_scope="Did stuff.",
        scope_delivery={
            "delivered": False,
            "user_confirmed_changes": True,
            "explanation": "Reordered with user agreement.",
        },
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "scope_delivery_non_yes" in r.soft_warns
    body = r.soft_warns["scope_delivery_non_yes"][0]
    assert "user_confirmed_changes=True" in body


def test_scope_delivery_true_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_repo(
        tmp_path,
        declared_scope="Did stuff.",
        scope_delivery={
            "delivered": True,
            "user_confirmed_changes": False,
            "explanation": "Yes",
        },
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "scope_delivery_non_yes" not in r.soft_warns


def test_scope_delivery_null_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """scope_delivery: null is the in-flight state; no warn yet."""
    _make_repo(
        tmp_path,
        declared_scope="Did stuff.",
        scope_delivery=None,
    )
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "scope_delivery_non_yes" not in r.soft_warns


def test_all_three_checks_register_in_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even when no warns fire, all three categories are in checks_run."""
    _make_repo(tmp_path, declared_scope="All clear.")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" in r.checks_run
    assert "phase_mismatch_declared_scope" in r.checks_run
    assert "scope_delivery_non_yes" in r.checks_run


# --- S-0125: mode-gating for empty_declared_scope per Retire-F ---


def test_missing_scope_in_build_mode_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Interactive build mode: missing declared_scope no longer fires."""
    _make_repo(tmp_path, mode="build")  # No declared_scope.
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" not in r.soft_warns


def test_empty_scope_in_build_mode_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Interactive build mode: empty declared_scope no longer fires."""
    _make_repo(tmp_path, declared_scope="", mode="build")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" not in r.soft_warns


def test_missing_scope_with_no_mode_field_no_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Legacy current.json without a mode field — treated as non-routine."""
    _make_repo(tmp_path, mode=None)
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" not in r.soft_warns


def test_missing_scope_in_routine_mode_still_fires(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Routine mode: missing declared_scope fires per ADR 0049."""
    _make_repo(tmp_path, mode="routine")
    monkeypatch.setattr(validate, "REPO_ROOT", tmp_path)
    r = validate.validate_scope_discipline()
    assert "empty_declared_scope" in r.soft_warns
    body = r.soft_warns["empty_declared_scope"][0]
    assert "routine-mode" in body
