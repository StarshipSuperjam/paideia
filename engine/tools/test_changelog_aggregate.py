"""Pytests for engine/tools/changelog_aggregate.py (ADR 0092 aggregator)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

import changelog_aggregate as agg

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_SCHEMA = REPO_ROOT / "engine" / "schemas" / "changelog-entry.schema.json"


# ---------- parse_frontmatter ----------


def test_parse_frontmatter_well_formed() -> None:
    text = """---
session_id: S-0198
session_type: build
closed_at: "2026-05-17T17:12:34Z"
material_change_class: mixed
module: changelog
summary: First per-session entry
---

# Body
- bullet
"""
    fm, body = agg.parse_frontmatter(text)
    assert fm["session_id"] == "S-0198"
    assert fm["session_type"] == "build"
    assert fm["closed_at"] == "2026-05-17T17:12:34Z"  # quotes stripped
    assert fm["material_change_class"] == "mixed"
    assert fm["summary"] == "First per-session entry"
    assert body[0] == ""
    assert "# Body" in body


def test_parse_frontmatter_missing_opening_delimiter() -> None:
    with pytest.raises(ValueError, match="opening"):
        agg.parse_frontmatter("session_id: S-0198\n")


def test_parse_frontmatter_missing_closing_delimiter() -> None:
    text = """---
session_id: S-0198
session_type: build
"""
    with pytest.raises(ValueError, match="closing"):
        agg.parse_frontmatter(text)


def test_parse_frontmatter_line_without_colon_rejected() -> None:
    text = """---
session_id S-0198
---
"""
    with pytest.raises(ValueError, match="lacks colon"):
        agg.parse_frontmatter(text)


# ---------- list_entries ----------


def test_list_entries_empty_dir(tmp_path: Path) -> None:
    (tmp_path / "2026").mkdir()
    assert agg.list_entries(tmp_path) == []


def test_list_entries_skips_history(tmp_path: Path) -> None:
    (tmp_path / "2026").mkdir()
    (tmp_path / "_history").mkdir()
    (tmp_path / "2026" / "S-0198-foo.md").write_text("body")
    (tmp_path / "_history" / "S-0099-old.md").write_text("body")
    paths = agg.list_entries(tmp_path)
    assert len(paths) == 1
    assert paths[0].name == "S-0198-foo.md"


def test_list_entries_sorted_across_years(tmp_path: Path) -> None:
    (tmp_path / "2025").mkdir()
    (tmp_path / "2026").mkdir()
    (tmp_path / "2026" / "S-0200-b.md").write_text("body")
    (tmp_path / "2025" / "S-0050-a.md").write_text("body")
    paths = agg.list_entries(tmp_path)
    assert [p.name for p in paths] == ["S-0050-a.md", "S-0200-b.md"]


# ---------- filter_entries ----------


def _make_entry(
    sid: str, module: str, closed_at: str, cls: str = "mixed"
) -> dict[str, Any]:
    return {
        "path": Path(f"/x/{sid}.md"),
        "frontmatter": {
            "session_id": sid,
            "session_type": "build",
            "closed_at": closed_at,
            "material_change_class": cls,
            "module": module,
        },
        "body_lines": [],
        "body_text": "",
        "line_count": 10,
    }


def test_filter_entries_module_filter() -> None:
    entries = [
        _make_entry("S-0198", "changelog", "2026-05-17T17:00:00Z"),
        _make_entry("S-0199", "memory", "2026-05-18T17:00:00Z"),
    ]
    out = agg.filter_entries(entries, since=None, module="changelog")
    assert [e["frontmatter"]["session_id"] for e in out] == ["S-0198"]


def test_filter_entries_since_filter() -> None:
    entries = [
        _make_entry("S-0198", "changelog", "2026-05-17T17:00:00Z"),
        _make_entry("S-0199", "memory", "2026-05-18T17:00:00Z"),
    ]
    cutoff = datetime(2026, 5, 17, 18, 0, 0, tzinfo=timezone.utc)
    out = agg.filter_entries(entries, since=cutoff, module=None)
    assert [e["frontmatter"]["session_id"] for e in out] == ["S-0199"]


# ---------- group_by_class ----------


def test_group_by_class_known_classes() -> None:
    entries = [
        _make_entry("S-0198", "x", "2026-05-17T00:00:00Z", cls="adr"),
        _make_entry("S-0199", "x", "2026-05-18T00:00:00Z", cls="tool"),
    ]
    groups = agg.group_by_class(entries)
    assert len(groups["adr"]) == 1
    assert len(groups["tool"]) == 1


def test_group_by_class_unknown_falls_to_mixed() -> None:
    e = _make_entry("S-0198", "x", "2026-05-17T00:00:00Z", cls="bogus")
    e["frontmatter"]["material_change_class"] = "bogus"
    groups = agg.group_by_class([e])
    assert len(groups["mixed"]) == 1


# ---------- emit_markdown / emit_json ----------


def test_emit_markdown_empty() -> None:
    groups: dict[str, list[dict[str, Any]]] = {
        cls: [] for cls in agg.CLASS_RENDER_ORDER
    }
    out = agg.emit_markdown(groups, since=None)
    assert "[Unreleased]" in out
    assert "_no entries_" in out


def test_emit_markdown_with_entries() -> None:
    groups = agg.group_by_class(
        [_make_entry("S-0198", "changelog", "2026-05-17T00:00:00Z", cls="adr")]
    )
    out = agg.emit_markdown(groups, since="engine-v0.1.0")
    assert "[Unreleased since engine-v0.1.0]" in out
    assert "## ADRs" in out
    assert "**S-0198**" in out


def test_emit_json_shape() -> None:
    entry = _make_entry("S-0198", "changelog", "2026-05-17T00:00:00Z", cls="adr")
    entry["path"] = REPO_ROOT / "engine" / "changelog" / "2026" / "S-0198-test.md"
    groups = agg.group_by_class([entry])
    out = agg.emit_json(groups, since=None)
    payload = json.loads(out)
    assert payload["unreleased_since"] is None
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["session_id"] == "S-0198"


# ---------- validate_all ----------


def test_validate_all_clean_when_frontmatter_valid() -> None:
    schema = json.loads(REAL_SCHEMA.read_text())
    entry = {
        "path": Path("dummy/S-0198-foo.md"),
        "frontmatter": {
            "session_id": "S-0198",
            "session_type": "build",
            "closed_at": "2026-05-17T17:00:00Z",
            "material_change_class": "mixed",
            "module": "changelog",
        },
    }
    violations = agg.validate_all([entry], schema)
    assert violations == []


def test_validate_all_catches_missing_required_field() -> None:
    schema = json.loads(REAL_SCHEMA.read_text())
    entry = {
        "path": Path("dummy/S-0198-foo.md"),
        "frontmatter": {"session_id": "S-0198"},  # missing required fields
    }
    violations = agg.validate_all([entry], schema)
    assert violations, "expected at least one violation"
    assert all(p == entry["path"] for p, _ in violations)


def test_validate_all_filename_session_id_mismatch() -> None:
    schema = json.loads(REAL_SCHEMA.read_text())
    entry = {
        "path": Path("dummy/S-0199-foo.md"),  # mismatch with frontmatter S-0198
        "frontmatter": {
            "session_id": "S-0198",
            "session_type": "build",
            "closed_at": "2026-05-17T17:00:00Z",
            "material_change_class": "mixed",
            "module": "changelog",
        },
    }
    violations = agg.validate_all([entry], schema)
    assert any("filename session_id" in msg for _, msg in violations)


# ---------- CLI / main ----------


def _write_entry(path: Path, sid: str, closed_at: str, cls: str = "mixed") -> None:
    path.write_text(
        f"""---
session_id: {sid}
session_type: build
closed_at: "{closed_at}"
material_change_class: {cls}
module: changelog
summary: smoke test entry
---

# Body
- one bullet
"""
    )


def test_main_validate_only_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "2026").mkdir()
    _write_entry(tmp_path / "2026" / "S-0198-foo.md", "S-0198", "2026-05-17T17:00:00Z")
    rc = _run_main(["--validate-only", "--changelog-root", str(tmp_path)])
    assert rc == 0


def test_main_validate_only_catches_violation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "2026").mkdir()
    _write_entry(
        tmp_path / "2026" / "S-0199-bar.md", "S-0198", "2026-05-17T17:00:00Z"
    )  # mismatch
    rc = _run_main(["--validate-only", "--changelog-root", str(tmp_path)])
    assert rc == 2


def test_main_emits_markdown_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "2026").mkdir()
    _write_entry(
        tmp_path / "2026" / "S-0198-foo.md", "S-0198", "2026-05-17T17:00:00Z", cls="adr"
    )
    rc = _run_main(["--changelog-root", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "[Unreleased]" in captured.out
    assert "## ADRs" in captured.out


def test_main_format_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "2026").mkdir()
    _write_entry(tmp_path / "2026" / "S-0198-foo.md", "S-0198", "2026-05-17T17:00:00Z")
    rc = _run_main(["--format", "json", "--changelog-root", str(tmp_path)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["entries"]) == 1


def _run_main(args: list[str]) -> int:
    """Invoke changelog_aggregate.main() with argv override."""
    import sys

    orig = sys.argv[:]
    sys.argv = ["changelog_aggregate.py", *args]
    try:
        return agg.main()
    finally:
        sys.argv = orig
