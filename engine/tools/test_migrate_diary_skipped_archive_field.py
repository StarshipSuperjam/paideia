"""Tests for migrate_diary_skipped_archive_field.py — ADR 0056 / S-0078."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_diary_skipped_archive_field import (  # noqa: E402
    NEW_KEY,
    OLD_KEY,
    main,
    migrate_one,
)


def _write_archive(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload))


def test_renames_old_key_to_new(tmp_path: Path) -> None:
    archive = tmp_path / "S-0050.json"
    archive.write_text(
        "{\n"
        '  "id": "S-0050",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 1,\n'
        '    "issue_collision": 5\n'
        "  }\n"
        "}\n"
    )

    touched, old_value = migrate_one(archive, dry_run=False)
    assert touched is True
    assert old_value == 1

    data = json.loads(archive.read_text())
    assert OLD_KEY not in data["outcome_summary_soft_warns"]
    assert data["outcome_summary_soft_warns"][NEW_KEY] == 1
    assert data["outcome_summary_soft_warns"]["issue_collision"] == 5


def test_no_old_key_no_change(tmp_path: Path) -> None:
    archive = tmp_path / "S-0078.json"
    payload: dict[str, object] = {
        "id": "S-0078",
        "outcome_summary_soft_warns": {"issue_collision": 5},
    }
    _write_archive(archive, payload)

    touched, old_value = migrate_one(archive, dry_run=False)
    assert touched is False
    assert old_value == 0

    # File unchanged.
    data = json.loads(archive.read_text())
    assert data == payload


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    archive = tmp_path / "S-0050.json"
    original_text = (
        "{\n"
        '  "id": "S-0050",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 3\n'
        "  }\n"
        "}\n"
    )
    archive.write_text(original_text)

    touched, _ = migrate_one(archive, dry_run=True)
    assert touched is True
    assert archive.read_text() == original_text


def test_zero_value_last_key_strips_prior_comma(tmp_path: Path) -> None:
    """diary_skipped as LAST key in dict → must strip prior key's trailing comma."""
    archive = tmp_path / "S-0032.json"
    archive.write_text(
        "{\n"
        '  "id": "S-0032",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "issue_collision": 5,\n'
        '    "diary_skipped": 0\n'
        "  }\n"
        "}\n"
    )

    touched, old_value = migrate_one(archive, dry_run=False)
    assert touched is True
    assert old_value == 0

    # Result must be valid JSON.
    data = json.loads(archive.read_text())
    assert OLD_KEY not in data["outcome_summary_soft_warns"]
    assert data["outcome_summary_soft_warns"]["issue_collision"] == 5


def test_zero_value_old_key_removed_no_new_key(tmp_path: Path) -> None:
    """0-valued diary_skipped: line removed entirely, new key NOT created."""
    archive = tmp_path / "S-0050.json"
    archive.write_text(
        "{\n"
        '  "id": "S-0050",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 0,\n'
        '    "issue_collision": 5\n'
        "  }\n"
        "}\n"
    )

    touched, old_value = migrate_one(archive, dry_run=False)
    assert touched is True
    assert old_value == 0

    data = json.loads(archive.read_text())
    assert OLD_KEY not in data["outcome_summary_soft_warns"]
    # Zero-value migration does NOT create the new key (zero == absent per ADR 0042).
    assert NEW_KEY not in data["outcome_summary_soft_warns"]
    # Sibling key untouched
    assert data["outcome_summary_soft_warns"]["issue_collision"] == 5


def test_preserves_unicode_in_other_fields(tmp_path: Path) -> None:
    """Unicode (em dashes, arrows) elsewhere in the file survives untouched."""
    archive = tmp_path / "S-0050.json"
    archive.write_text(
        "{\n"
        '  "id": "S-0050",\n'
        '  "working_on": "Audit window S-0066 → S-0076 — work text with non-ASCII.",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 0\n'
        "  }\n"
        "}\n",
        encoding="utf-8",
    )

    touched, _ = migrate_one(archive, dry_run=False)
    assert touched is True

    text = archive.read_text(encoding="utf-8")
    assert "→" in text  # not re-escaped to →
    assert "—" in text  # not re-escaped to —


def test_idempotent(tmp_path: Path) -> None:
    """Re-running on an already-migrated archive is a no-op."""
    archive = tmp_path / "S-0050.json"
    archive.write_text(
        "{\n"
        '  "id": "S-0050",\n'
        '  "outcome_summary_soft_warns": {\n'
        '    "mempalace_diary_write_skipped": 2\n'
        "  }\n"
        "}\n"
    )

    touched1, _ = migrate_one(archive, dry_run=False)
    assert touched1 is False
    after_first = archive.read_text()

    touched2, _ = migrate_one(archive, dry_run=False)
    assert touched2 is False
    assert archive.read_text() == after_first


def test_malformed_archive_skipped(tmp_path: Path) -> None:
    """Bad JSON or missing soft_warns key — no crash, no change."""
    archive = tmp_path / "S-0050.json"
    archive.write_text("{ not valid")
    touched, _ = migrate_one(archive, dry_run=False)
    assert touched is False


def test_main_walks_archive_dir(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    (archive_dir / "S-0050.json").write_text(
        '{\n  "id": "S-0050",\n  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 1\n  }\n}\n'
    )
    (archive_dir / "S-0051.json").write_text(
        '{\n  "id": "S-0051",\n  "outcome_summary_soft_warns": {\n'
        '    "diary_skipped": 0\n  }\n}\n'
    )
    (archive_dir / "S-0052.json").write_text(
        '{\n  "id": "S-0052",\n  "outcome_summary_soft_warns": {\n'
        '    "issue_collision": 5\n  }\n}\n'
    )

    rc = main(["--archive-dir", str(archive_dir)])
    assert rc == 0

    s50 = json.loads((archive_dir / "S-0050.json").read_text())
    assert s50["outcome_summary_soft_warns"][NEW_KEY] == 1
    assert OLD_KEY not in s50["outcome_summary_soft_warns"]

    s51 = json.loads((archive_dir / "S-0051.json").read_text())
    assert OLD_KEY not in s51["outcome_summary_soft_warns"]

    s52 = json.loads((archive_dir / "S-0052.json").read_text())
    assert s52["outcome_summary_soft_warns"]["issue_collision"] == 5


def test_main_handles_missing_dir(tmp_path: Path) -> None:
    rc = main(["--archive-dir", str(tmp_path / "no-such-dir")])
    assert rc == 0
