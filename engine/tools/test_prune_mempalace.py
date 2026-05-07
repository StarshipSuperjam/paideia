"""Tests for engine/tools/prune_mempalace.py.

Strategy: build a real chromadb palace under tmp_path with metadata
matching every classifier branch (mined / canonical-but-not-mined /
orphan-wing / canonical-non-orphan-wing / historical-full-path) and
exercise each audit mode. ChromaDB setup costs ~30 s per test (embedding
model load); the suite is intentionally compact — one fixture seeded
once per test, branches verified at the function level.

Out of scope
------------
- ChromaDB internals (collection.delete is exercised; embedding
  recompute is not asserted; the tool's contract is "drawer absent
  after delete," not "embedding regenerated cleanly").
- Backup correctness (shutil.copytree is stdlib; we assert the OSError
  branch through monkey-patching).
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prune_mempalace  # noqa: E402

TOOL_PATH = Path(__file__).resolve().parent / "prune_mempalace.py"


def _build_palace(tmp_path: Path) -> Path:
    """Build a synthetic palace with one drawer per classifier branch."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("mempalace_drawers")
    col.add(
        ids=[
            "drawer_paideia_general_mined",
            "drawer_paideia_operations_mined",
            "drawer_paideia_general_manual",
            "drawer_paideia_operations_curated",
            "drawer_paideia_decisions",
            "drawer_orphan_wing_aaaaaa",
            "drawer_orphan_wing_bbbbbb_2",
            "drawer_canonical_wing_paideia",
            "drawer_canonical_wing_claude",
            "drawer_historical_fullpath_a",
            "drawer_historical_fullpath_b",
            "drawer_historical_second_wing",
        ],
        documents=[
            "mined chunk of MISSION.md",
            "mined chunk of operations doc",
            "[decision] curated content from S-0002 manual",
            "manual addition by claude post-mining",
            "real decision drawer",
            "diary entry from orphan worktree wing",
            "second diary entry from same orphan wing",
            "main-session capture into wing_paideia",
            "AI diary entry",
            "auto-capture from old worktree path A",
            "second auto-capture from same old worktree A",
            "auto-capture from a different old worktree B",
        ],
        metadatas=[
            {"wing": "paideia", "room": "general", "added_by": "claude-s0002"},
            {"wing": "paideia", "room": "operations", "added_by": "claude-s0002"},
            {"wing": "paideia", "room": "general", "added_by": "claude-s0002-manual"},
            {"wing": "paideia", "room": "operations", "added_by": "claude"},
            {"wing": "paideia", "room": "decisions", "added_by": "claude"},
            {"wing": "wing_aaaaaa", "room": "diary"},
            {"wing": "wing_bbbbbb", "room": "diary"},
            {"wing": "wing_paideia", "room": "diary"},
            {"wing": "wing_claude", "room": "diary"},
            {
                "wing": "-Users-test--claude-worktrees-foo-bar-12abcd",
                "room": "general",
            },
            {
                "wing": "-Users-test--claude-worktrees-foo-bar-12abcd",
                "room": "general",
            },
            {
                "wing": "-Users-other--claude-worktrees-baz-qux-34efgh",
                "room": "general",
            },
        ],
    )
    # Add a closet pointing at the first historical wing so the
    # by-collection deletion path is exercised. Mirrors the live
    # palace shape the S-0092 first apply discovered (drawers AND
    # closets both carry the ``-Users-...`` wing tag).
    closets = client.get_or_create_collection("mempalace_closets")
    closets.add(
        ids=["closet_historical_a"],
        documents=["closet entry referencing historical-wing drawers"],
        metadatas=[
            {
                "wing": "-Users-test--claude-worktrees-foo-bar-12abcd",
                "room": "general",
            },
        ],
    )
    del col
    del closets
    del client
    return palace_dir


# ---------------------------------------------------------------------------
# resolve_palace_path
# ---------------------------------------------------------------------------


def test_resolve_palace_path_uses_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", "/tmp/fake-palace")
    assert prune_mempalace.resolve_palace_path(None) == Path("/tmp/fake-palace")


def test_resolve_palace_path_env_beats_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", "/tmp/from-env")
    assert prune_mempalace.resolve_palace_path("/tmp/from-arg") == Path("/tmp/from-env")


def test_resolve_palace_path_arg_when_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEMPALACE_PROBE_PALACE_PATH", raising=False)
    assert prune_mempalace.resolve_palace_path("/tmp/from-arg") == Path("/tmp/from-arg")


def test_resolve_palace_path_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEMPALACE_PROBE_PALACE_PATH", raising=False)
    p = prune_mempalace.resolve_palace_path(None)
    assert p == Path.home() / ".mempalace" / "palace"


# ---------------------------------------------------------------------------
# Classifier patterns
# ---------------------------------------------------------------------------


def test_orphan_wing_pattern_matches_six_hex() -> None:
    assert prune_mempalace._ORPHAN_WING_RE.match("wing_a5d511")
    assert prune_mempalace._ORPHAN_WING_RE.match("wing_000000")


def test_orphan_wing_pattern_rejects_seven_hex() -> None:
    assert not prune_mempalace._ORPHAN_WING_RE.match("wing_a5d5111")


def test_orphan_wing_pattern_rejects_canonical_names() -> None:
    assert not prune_mempalace._ORPHAN_WING_RE.match("wing_paideia")
    assert not prune_mempalace._ORPHAN_WING_RE.match("wing_claude")


def test_historical_full_path_pattern_matches_dash_users_prefix() -> None:
    assert prune_mempalace._HISTORICAL_FULL_PATH_RE.search(
        "-Users-shanekidd-Documents-Claude-Files-Paideia"
    )


def test_historical_full_path_pattern_matches_claude_worktrees_marker() -> None:
    assert prune_mempalace._HISTORICAL_FULL_PATH_RE.search(
        "Documents-Claude--claude-worktrees-foo-bar-12abcd"
    )


def test_historical_full_path_pattern_rejects_canonical() -> None:
    assert not prune_mempalace._HISTORICAL_FULL_PATH_RE.search("paideia")
    assert not prune_mempalace._HISTORICAL_FULL_PATH_RE.search("wing_paideia")
    assert not prune_mempalace._HISTORICAL_FULL_PATH_RE.search("wing_claude")


# ---------------------------------------------------------------------------
# enumerate_mined_ids — direct sqlite query
# ---------------------------------------------------------------------------


def test_enumerate_mined_ids_matches_only_claude_s0002(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        ids = prune_mempalace.enumerate_mined_ids(con)
    finally:
        con.close()
    # Two mined drawers (general + operations); manual / curated /
    # decisions / orphan / historical do NOT match.
    assert len(ids) == 2


def test_enumerate_mined_ids_excludes_claude_s0002_manual(tmp_path: Path) -> None:
    """The -manual suffix is curated content; must not appear in the prune set."""
    palace_dir = _build_palace(tmp_path)
    # Sanity: the manual drawer must exist in the palace before the test
    # has any meaning.
    con_assert = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        manual_count = con_assert.execute(
            "SELECT COUNT(*) FROM embedding_metadata "
            "WHERE key='added_by' AND string_value='claude-s0002-manual'"
        ).fetchone()[0]
    finally:
        con_assert.close()
    assert manual_count == 1
    # Now confirm enumerate_mined_ids does not pick it up.
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        ids = prune_mempalace.enumerate_mined_ids(con)
    finally:
        con.close()
    # Verify by mapping internal IDs back to drawer UUIDs.
    uuids = prune_mempalace.fetch_drawer_uuids(palace_dir, ids)
    assert "drawer_paideia_general_manual" not in uuids


# ---------------------------------------------------------------------------
# enumerate_orphan_wing_drawers — direct sqlite query
# ---------------------------------------------------------------------------


def test_enumerate_orphan_wing_drawers_matches_pattern(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        pairs = prune_mempalace.enumerate_orphan_wing_drawers(con)
    finally:
        con.close()
    wings = {w for w, _ in pairs}
    assert wings == {"wing_aaaaaa", "wing_bbbbbb"}


def test_enumerate_orphan_wing_drawers_excludes_canonical(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        pairs = prune_mempalace.enumerate_orphan_wing_drawers(con)
    finally:
        con.close()
    wings = {w for w, _ in pairs}
    assert "wing_paideia" not in wings
    assert "wing_claude" not in wings


# ---------------------------------------------------------------------------
# enumerate_historical_paths
# ---------------------------------------------------------------------------


def test_enumerate_historical_paths_matches_full_encoded_paths(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        wings = prune_mempalace.enumerate_historical_paths(con)
    finally:
        con.close()
    names = [w for w, _ in wings]
    assert any("--claude-worktrees-" in n for n in names)


# ---------------------------------------------------------------------------
# Audit modes (dry-run)
# ---------------------------------------------------------------------------


def test_audit_mined_ops_docs_dry_run_finds_candidates(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_mined_ops_docs(palace_dir, apply=False)
    assert report.mode == "mined-ops-docs"
    assert len(report.candidates) == 2
    assert report.deleted == 0


def test_audit_orphan_wings_dry_run_finds_two_wings(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_orphan_wings(palace_dir, apply=False)
    assert report.mode == "orphan-wings"
    # Two distinct orphan wings (aaaaaa + bbbbbb).
    assert len(report.candidates) == 2
    assert report.deleted == 0


def test_audit_historical_paths_dry_run_finds_candidates(tmp_path: Path) -> None:
    """Dry run enumerates per-wing counts without mutation."""
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_historical_paths(palace_dir, apply=False)
    assert report.mode == "historical-paths"
    # Two distinct historical-path wings in the fixture.
    assert len(report.candidates) == 2
    # Four entries total (two drawers + one closet in wing A, one
    # drawer in wing B). enumerate_historical_paths counts everything
    # tagged with the wing — drawers and closets both surface here.
    total = sum(c["drawer_count"] for c in report.candidates)
    assert total == 4
    assert report.deleted == 0


def test_audit_historical_paths_dry_run_note_points_at_apply_path(
    tmp_path: Path,
) -> None:
    """Dry-run note describes the apply path (S-0092 contract)."""
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_historical_paths(palace_dir, apply=False)
    joined = " ".join(report.notes)
    assert "--apply" in joined
    assert "Issue #41" in joined
    assert "S-0092" in joined


# ---------------------------------------------------------------------------
# Apply mode (mutation)
# ---------------------------------------------------------------------------


def test_audit_mined_ops_docs_apply_deletes_mined_only(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_mined_ops_docs(palace_dir, apply=True)
    assert report.deleted == 2

    # Verify post-state: mined drawers gone, others preserved.
    db = palace_dir / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        """
        SELECT em_a.string_value, COUNT(DISTINCT em_a.id)
        FROM embedding_metadata em_a
        WHERE em_a.key='added_by'
        GROUP BY em_a.string_value
        """
    ).fetchall()
    con.close()
    counts = dict(rows)
    # claude-s0002 mined drawers deleted.
    assert counts.get("claude-s0002", 0) == 0
    # claude-s0002-manual preserved.
    assert counts.get("claude-s0002-manual", 0) == 1
    # claude (post-mining manual) preserved.
    assert counts.get("claude", 0) == 2


def test_audit_orphan_wings_apply_deletes_orphans_only(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_orphan_wings(palace_dir, apply=True)
    assert report.deleted == 2  # two drawers across two orphan wings

    # Verify post-state.
    db = palace_dir / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT string_value, COUNT(DISTINCT id) FROM embedding_metadata "
        "WHERE key='wing' GROUP BY string_value"
    ).fetchall()
    con.close()
    wings = dict(rows)
    assert "wing_aaaaaa" not in wings
    assert "wing_bbbbbb" not in wings
    # Canonical wings preserved.
    assert wings.get("wing_paideia", 0) == 1
    assert wings.get("wing_claude", 0) == 1
    assert wings.get("paideia", 0) == 5  # 5 paideia-wing drawers in the fixture


def test_audit_historical_paths_apply_deletes_historical_only(
    tmp_path: Path,
) -> None:
    """Apply mode bulk-deletes ALL historical-wing entries (drawers + closets); canonical wings untouched."""
    palace_dir = _build_palace(tmp_path)
    report = prune_mempalace.audit_historical_paths(palace_dir, apply=True)
    # Three drawers + one closet = four deletions across two wings.
    assert report.deleted == 4

    # Apply note announces the count and points at the signal-probe report.
    joined = " ".join(report.notes)
    assert "APPLY MODE" in joined
    assert "signal-probe" in joined or "signal probe" in joined.replace("-", " ")

    # Verify post-state: historical wings gone, canonical preserved.
    db = palace_dir / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT string_value, COUNT(DISTINCT id) FROM embedding_metadata "
        "WHERE key='wing' GROUP BY string_value"
    ).fetchall()
    con.close()
    wings = dict(rows)
    # Both historical wings absent.
    assert "-Users-test--claude-worktrees-foo-bar-12abcd" not in wings
    assert "-Users-other--claude-worktrees-baz-qux-34efgh" not in wings
    # Canonical wings preserved.
    assert wings.get("paideia", 0) == 5
    assert wings.get("wing_paideia", 0) == 1
    assert wings.get("wing_claude", 0) == 1
    # Orphan wings preserved (not in this audit's scope).
    assert wings.get("wing_aaaaaa", 0) == 1
    assert wings.get("wing_bbbbbb", 0) == 1


def test_audit_historical_paths_apply_idempotent(tmp_path: Path) -> None:
    """Second apply on the same palace deletes nothing (no historical drawers left)."""
    palace_dir = _build_palace(tmp_path)
    first = prune_mempalace.audit_historical_paths(palace_dir, apply=True)
    assert first.deleted == 4
    second = prune_mempalace.audit_historical_paths(palace_dir, apply=True)
    assert second.deleted == 0
    # Candidates list reflects current population, not original.
    assert second.candidates == []


def test_enumerate_historical_path_drawer_internal_ids_aggregates_across_wings(
    tmp_path: Path,
) -> None:
    """Helper enumerator returns (wing, internal_id) for every historical-wing entry across drawers and closets."""
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        pairs = prune_mempalace.enumerate_historical_path_drawer_internal_ids(con)
    finally:
        con.close()
    wings_seen = {w for w, _ in pairs}
    assert wings_seen == {
        "-Users-test--claude-worktrees-foo-bar-12abcd",
        "-Users-other--claude-worktrees-baz-qux-34efgh",
    }
    # Two drawers + one closet in the first wing, one drawer in the second.
    counts: dict[str, int] = {}
    for wing, _ in pairs:
        counts[wing] = counts.get(wing, 0) + 1
    assert counts["-Users-test--claude-worktrees-foo-bar-12abcd"] == 3
    assert counts["-Users-other--claude-worktrees-baz-qux-34efgh"] == 1


def test_fetch_uuids_by_collection_groups_drawers_and_closets(
    tmp_path: Path,
) -> None:
    """fetch_uuids_by_collection buckets UUIDs by their owning chromadb collection."""
    palace_dir = _build_palace(tmp_path)
    con = prune_mempalace.open_sqlite_ro(palace_dir)
    try:
        pairs = prune_mempalace.enumerate_historical_path_drawer_internal_ids(con)
    finally:
        con.close()
    flat_ids = [iid for _, iid in pairs]
    by_col = prune_mempalace.fetch_uuids_by_collection(palace_dir, flat_ids)
    # Both collections present, with the expected per-collection counts.
    assert "mempalace_drawers" in by_col
    assert "mempalace_closets" in by_col
    assert len(by_col["mempalace_drawers"]) == 3
    assert len(by_col["mempalace_closets"]) == 1


def test_fetch_uuids_by_collection_empty_input_returns_empty(
    tmp_path: Path,
) -> None:
    """Empty input does not open a sqlite connection; returns {}."""
    # No fixture needed for this branch — the early return fires before
    # any palace access. Pass a path that doesn't exist to make that
    # explicit.
    out = prune_mempalace.fetch_uuids_by_collection(tmp_path / "nope", [])
    assert out == {}


# ---------------------------------------------------------------------------
# CLI flag handling
# ---------------------------------------------------------------------------


def _run_cli(palace_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["MEMPALACE_PROBE_PALACE_PATH"] = str(palace_dir)
    return subprocess.run(
        [sys.executable, str(TOOL_PATH), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def test_cli_apply_without_backup_dir_exits_2(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    proc = _run_cli(palace_dir, "--audit-mined-ops-docs", "--apply")
    assert proc.returncode == 2
    assert "--backup-dir" in proc.stderr


def test_cli_apply_with_failing_backup_exits_2(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    # Pre-create the backup dir so the FileExistsError fires.
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()
    proc = _run_cli(
        palace_dir,
        "--audit-mined-ops-docs",
        "--apply",
        "--backup-dir",
        str(backup_dir),
    )
    assert proc.returncode == 2
    assert "backup failed" in proc.stderr or "already exists" in proc.stderr


def test_cli_palace_not_found_exits_3(tmp_path: Path) -> None:
    proc = _run_cli(tmp_path / "nonexistent", "--audit-mined-ops-docs")
    assert proc.returncode == 3
    assert "palace not found" in proc.stderr


def test_cli_dry_run_default_emits_dry_run_marker(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    proc = _run_cli(palace_dir, "--audit-mined-ops-docs")
    assert proc.returncode == 0
    assert "MODE: dry-run" in proc.stdout
    assert "candidates: 2" in proc.stdout


def test_cli_apply_with_backup_dir_succeeds(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    backup_dir = tmp_path / "backup-target"
    proc = _run_cli(
        palace_dir,
        "--audit-mined-ops-docs",
        "--apply",
        "--backup-dir",
        str(backup_dir),
    )
    assert proc.returncode == 0
    assert backup_dir.is_dir()
    assert (backup_dir / "chroma.sqlite3").is_file()
    assert "MODE: apply" in proc.stdout


def test_cli_audit_historical_paths_apply_without_backup_exits_2(
    tmp_path: Path,
) -> None:
    """Historical-paths apply requires --backup-dir, mirroring the other two modes."""
    palace_dir = _build_palace(tmp_path)
    proc = _run_cli(palace_dir, "--audit-historical-paths", "--apply")
    assert proc.returncode == 2
    assert "--backup-dir" in proc.stderr


def test_cli_audit_historical_paths_apply_with_backup_succeeds(
    tmp_path: Path,
) -> None:
    """Happy-path apply: backup dir created, drawers deleted, MODE: apply emitted."""
    palace_dir = _build_palace(tmp_path)
    backup_dir = tmp_path / "backup-historical"
    proc = _run_cli(
        palace_dir,
        "--audit-historical-paths",
        "--apply",
        "--backup-dir",
        str(backup_dir),
    )
    assert proc.returncode == 0, proc.stderr
    assert backup_dir.is_dir()
    assert (backup_dir / "chroma.sqlite3").is_file()
    assert "MODE: apply" in proc.stdout
    # The apply note announces the deletion count (3 drawers + 1 closet).
    assert "deleting 4" in proc.stdout or "deleted: 4" in proc.stdout
