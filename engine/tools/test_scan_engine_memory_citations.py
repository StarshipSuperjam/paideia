"""Tests for engine/tools/scan_engine_memory_citations.py — ADR 0091 (S-0193)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scan_engine_memory_citations as scanner  # noqa: E402


# --------------------------------------------------------------------
# DRAWER_ID_PATTERN — matches both engine_memory uuid4 hex IDs AND
# legacy chromadb drawer_*_<hex> forms (for citations of historical
# content via lineage.imported_from)
# --------------------------------------------------------------------


def test_drawer_id_pattern_matches_engine_memory_uuid4_hex() -> None:
    """32-char lowercase hex IDs are how engine_memory_add_drawer writes IDs."""
    text = (
        "Cutover narrative landed at e2dc29e4b7ca4d12b61fb13c6317f636 and "
        "the lesson at d7f8069635c14521898d084620c19277."
    )
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 2


def test_drawer_id_pattern_matches_legacy_chromadb_ids_too() -> None:
    """Migrated drawers cite original IDs via lineage.imported_from."""
    text = (
        "Saw drawer_paideia_a3d64680e953450f011e582f and "
        "drawer_wing_paideia_b7f3c2d1e4a5b6c789d012ef3 in the historical record."
    )
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 2


def test_drawer_id_pattern_mixed_old_and_new() -> None:
    text = (
        "Migrated content originally at drawer_paideia_a3d64680e953450f011e582f "
        "now lives at e2dc29e4b7ca4d12b61fb13c6317f636 in engine_memory."
    )
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 2


def test_drawer_id_pattern_ignores_short_hex() -> None:
    text = "abc123 and deadbeef are not drawer IDs (too short)."
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 0


def test_drawer_id_pattern_ignores_uppercase_hex() -> None:
    """uuid4().hex always produces lowercase; uppercase is not a drawer ID."""
    text = "E2DC29E4B7CA4D12B61FB13C6317F636 is not a drawer ID."
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 0


# --------------------------------------------------------------------
# SESSION_ARCHIVE_PATTERN + TAG_NAMED_PATTERN parity with sibling
# (shape unchanged from the retiring scan_mempalace_citations.py)
# --------------------------------------------------------------------


def test_session_archive_pattern_matches_canonical_forms() -> None:
    text = (
        "Per S-0091 the contract held; from S-0186 we learned; "
        "at S-0078 the mechanism landed."
    )
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 3


def test_session_archive_pattern_possessive_form() -> None:
    text = "S-0193's demolition pass."
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 1


def test_session_archive_pattern_dedupes_within_source() -> None:
    text = "per S-0193 again per S-0193 and S-0193's findings"
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 1


def test_tag_named_pattern_three_kinds() -> None:
    text = "Per pushback drawer X; per lesson drawer Y; per decision drawer Z."
    counts = scanner.scan_text(text)
    assert counts["tag_named_refs"] == 3


# --------------------------------------------------------------------
# _sum_counts + scan_text aggregation
# --------------------------------------------------------------------


def test_scan_empty_text_returns_zero_counts() -> None:
    counts = scanner.scan_text("")
    assert counts == {
        "drawer_id_refs": 0,
        "session_archive_refs": 0,
        "tag_named_refs": 0,
    }


def test_sum_counts_combines_and_computes_total() -> None:
    sources = [
        {"drawer_id_refs": 2, "session_archive_refs": 1, "tag_named_refs": 0},
        {"drawer_id_refs": 0, "session_archive_refs": 4, "tag_named_refs": 1},
        {"drawer_id_refs": 1, "session_archive_refs": 0, "tag_named_refs": 0},
    ]
    summed = scanner._sum_counts(sources)
    assert summed["drawer_id_refs"] == 3
    assert summed["session_archive_refs"] == 5
    assert summed["tag_named_refs"] == 1
    assert summed["total"] == 9


# --------------------------------------------------------------------
# write_citations_to_current — engine_memory_activity field shape
# --------------------------------------------------------------------


def test_write_citations_creates_engine_memory_activity_block(
    tmp_path: Path,
) -> None:
    """Writes nest under engine_memory_activity (not mempalace_activity)."""
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0193", "outcome_summary": "test"}, indent=2)
    )
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 2,
            "session_archive_refs": 1,
            "tag_named_refs": 0,
            "total": 3,
        },
    )
    data = json.loads(current.read_text())
    assert "engine_memory_activity" in data
    assert "engine_memory_citations" in data["engine_memory_activity"]
    assert data["engine_memory_activity"]["engine_memory_citations"]["total"] == 3
    # Does NOT leak into mempalace_activity (retiring at S-0193)
    assert "mempalace_citations" not in data.get("mempalace_activity", {})


def test_write_citations_preserves_existing_engine_memory_activity(
    tmp_path: Path,
) -> None:
    """Updates merge into existing engine_memory_activity, don't overwrite."""
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0193",
                "engine_memory_activity": {
                    "search_calls": 5,
                    "add_drawer_calls": 2,
                    "total_calls": 7,
                },
            },
            indent=2,
        )
    )
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 1,
            "session_archive_refs": 2,
            "tag_named_refs": 0,
            "total": 3,
        },
    )
    data = json.loads(current.read_text())
    activity = data["engine_memory_activity"]
    assert activity["search_calls"] == 5
    assert activity["add_drawer_calls"] == 2
    assert activity["engine_memory_citations"]["total"] == 3


def test_write_citations_idempotent_on_rerun(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0193"}, indent=2))
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 1,
            "session_archive_refs": 1,
            "tag_named_refs": 1,
            "total": 3,
        },
    )
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 2,
            "session_archive_refs": 2,
            "tag_named_refs": 2,
            "total": 6,
        },
    )
    data = json.loads(current.read_text())
    # Re-run overwrites the citations block
    assert data["engine_memory_activity"]["engine_memory_citations"]["total"] == 6


def test_write_citations_missing_current_raises(tmp_path: Path) -> None:
    nonexistent = tmp_path / "no-current.json"
    with pytest.raises(FileNotFoundError):
        scanner.write_citations_to_current(
            nonexistent,
            {
                "drawer_id_refs": 0,
                "session_archive_refs": 0,
                "tag_named_refs": 0,
                "total": 0,
            },
        )


# --------------------------------------------------------------------
# main exit codes
# --------------------------------------------------------------------


def test_main_returns_0_when_current_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No in-flight session is a benign no-op, not an error."""
    rc = scanner.main(["--current-path", str(tmp_path / "no-current.json")])
    assert rc == 0
    captured = capsys.readouterr()
    assert "no in-flight session" in captured.out


def test_main_dry_run_does_not_write(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0193", "outcome_summary": "see S-0192 for context"})
    )
    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),  # no git repo, no commits to scan
            "--dry-run",
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    # Dry-run never writes engine_memory_activity
    assert "engine_memory_activity" not in data


def test_main_end_to_end_writes_block(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0193",
                "outcome_summary": (
                    "Closed per S-0192 cutover; cite engine_memory drawer "
                    "e2dc29e4b7ca4d12b61fb13c6317f636 for narrative."
                ),
            }
        )
    )
    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    citations = data["engine_memory_activity"]["engine_memory_citations"]
    assert citations["drawer_id_refs"] >= 1
    assert citations["session_archive_refs"] >= 1
    assert citations["total"] >= 2
