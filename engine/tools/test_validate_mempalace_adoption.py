"""Tests for validate.validate_mempalace_adoption — ADR 0056 / S-0078."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402


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


def test_diary_write_skip_with_acknowledgement_downgrades(tmp_path: Path) -> None:
    """Acknowledgement token in outcome_summary → soft-warn instead of hard-fail."""
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
