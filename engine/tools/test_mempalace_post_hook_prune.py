"""Tests for engine/tools/mempalace_post_hook_prune.py.

Build a small chromadb palace seeded with two cohorts of sessions-wing
drawers (created_at before vs after the test's ``since`` timestamp)
and one curated drawer per preserved room (decisions / lessons /
diary). Verify the prune deletes ONLY the post-``since`` pollution
cohort.

Per-fixture chromadb spin-up costs ~30s (embedding model load); kept
compact — one shared fixture-build with multiple targeted assertions.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mempalace_post_hook_prune  # noqa: E402

# Two reference timestamps. ``BEFORE`` precedes ``SINCE``; ``AFTER``
# follows it. Drawers with created_at == BEFORE must NOT be pruned;
# drawers with created_at == AFTER must be pruned (when the room
# classifier matches).
BEFORE = "2026-05-15T19:00:00Z"
SINCE = "2026-05-15T19:30:00Z"
AFTER = "2026-05-15T19:45:00Z"


def _build_palace(tmp_path: Path) -> Path:
    """Build a synthetic palace with before/after pollution + curated drawers."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("mempalace_drawers")
    col.add(
        ids=[
            "drawer_old_pollution_technical",
            "drawer_old_pollution_planning",
            "drawer_new_pollution_technical",
            "drawer_new_pollution_planning",
            "drawer_new_pollution_architecture",
            "drawer_new_pollution_general",
            "drawer_new_pollution_problems",
            "drawer_new_curated_decisions",
            "drawer_new_curated_lessons",
            "drawer_new_curated_diary",
            "drawer_new_paideia_technical",
        ],
        documents=[
            "old transcript pollution from a prior hook fire",
            "old planning chunk from a prior hook fire",
            "fresh transcript pollution from THIS hook fire",
            "fresh planning chunk from THIS hook fire",
            "fresh ADR architecture excerpt from THIS hook fire",
            "fresh general transcript fragment from THIS hook fire",
            "fresh validator-soft-warn dump from THIS hook fire",
            "fresh curated decision drawer authored via mempalace_add_drawer",
            "fresh curated lesson drawer authored via mempalace_add_drawer",
            "fresh curated diary entry",
            "fresh content in paideia wing (NOT sessions; must be preserved)",
        ],
        metadatas=[
            {"wing": "sessions", "room": "technical", "created_at": BEFORE},
            {"wing": "sessions", "room": "planning", "created_at": BEFORE},
            {"wing": "sessions", "room": "technical", "created_at": AFTER},
            {"wing": "sessions", "room": "planning", "created_at": AFTER},
            {"wing": "sessions", "room": "architecture", "created_at": AFTER},
            {"wing": "sessions", "room": "general", "created_at": AFTER},
            {"wing": "sessions", "room": "problems", "created_at": AFTER},
            {"wing": "sessions", "room": "decisions", "created_at": AFTER},
            {"wing": "sessions", "room": "lessons", "created_at": AFTER},
            {"wing": "sessions", "room": "diary", "created_at": AFTER},
            {"wing": "paideia", "room": "technical", "created_at": AFTER},
        ],
    )
    del col
    del client
    return palace_dir


def test_resolve_palace_path_env_beats_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", "/tmp/from-env")  # nosec B108  # test fixture string; not a path used for I/O
    assert mempalace_post_hook_prune.resolve_palace_path("/tmp/from-arg") == Path(  # nosec B108  # test fixture string; not a path used for I/O
        "/tmp/from-env"  # nosec B108  # test fixture string; not a path used for I/O
    )


def test_resolve_palace_path_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEMPALACE_PROBE_PALACE_PATH", raising=False)
    p = mempalace_post_hook_prune.resolve_palace_path(None)
    assert p == Path.home() / ".mempalace" / "palace"


def test_enumerate_recent_pollution_matches_only_post_since_noise(
    tmp_path: Path,
) -> None:
    palace_dir = _build_palace(tmp_path)
    ids = mempalace_post_hook_prune.enumerate_recent_pollution_internal_ids(
        palace_dir, SINCE
    )
    # Five post-SINCE pollution drawers; pre-SINCE entries and curated
    # rooms are filtered out by the classifier.
    assert len(ids) == 5
    uuids = mempalace_post_hook_prune.fetch_uuids_for_internal_ids(palace_dir, ids)
    # The five fresh pollution drawers must be in the result set.
    assert {
        "drawer_new_pollution_technical",
        "drawer_new_pollution_planning",
        "drawer_new_pollution_architecture",
        "drawer_new_pollution_general",
        "drawer_new_pollution_problems",
    } == set(uuids)


def test_enumerate_recent_pollution_excludes_older_drawers(tmp_path: Path) -> None:
    """Drawers with created_at <= since stay in place."""
    palace_dir = _build_palace(tmp_path)
    ids = mempalace_post_hook_prune.enumerate_recent_pollution_internal_ids(
        palace_dir, SINCE
    )
    uuids = mempalace_post_hook_prune.fetch_uuids_for_internal_ids(palace_dir, ids)
    assert "drawer_old_pollution_technical" not in uuids
    assert "drawer_old_pollution_planning" not in uuids


def test_enumerate_recent_pollution_excludes_curated_rooms(tmp_path: Path) -> None:
    """Curated rooms in the same wing+timeframe are preserved."""
    palace_dir = _build_palace(tmp_path)
    ids = mempalace_post_hook_prune.enumerate_recent_pollution_internal_ids(
        palace_dir, SINCE
    )
    uuids = mempalace_post_hook_prune.fetch_uuids_for_internal_ids(palace_dir, ids)
    assert "drawer_new_curated_decisions" not in uuids
    assert "drawer_new_curated_lessons" not in uuids
    assert "drawer_new_curated_diary" not in uuids


def test_enumerate_recent_pollution_excludes_paideia_wing(tmp_path: Path) -> None:
    """The sessions-wing classifier is wing-exact; paideia/<noise-room> is preserved."""
    palace_dir = _build_palace(tmp_path)
    ids = mempalace_post_hook_prune.enumerate_recent_pollution_internal_ids(
        palace_dir, SINCE
    )
    uuids = mempalace_post_hook_prune.fetch_uuids_for_internal_ids(palace_dir, ids)
    assert "drawer_new_paideia_technical" not in uuids


def test_run_deletes_recent_pollution(tmp_path: Path) -> None:
    palace_dir = _build_palace(tmp_path)
    exit_code, deleted = mempalace_post_hook_prune.run(palace_dir, SINCE)
    assert exit_code == 0
    assert deleted == 5

    # Verify post-state: fresh pollution drawers gone; older pollution
    # and curated drawers preserved.
    db = palace_dir / "chroma.sqlite3"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT em_w.string_value, em_r.string_value, COUNT(DISTINCT em_w.id) "
        "FROM embedding_metadata em_w "
        "JOIN embedding_metadata em_r ON em_w.id=em_r.id "
        "WHERE em_w.key='wing' AND em_r.key='room' "
        "GROUP BY em_w.string_value, em_r.string_value "
        "ORDER BY 1,2"
    ).fetchall()
    con.close()
    by_key = {(w, r): n for w, r, n in rows}
    # Sessions/<noise-rooms> all drained for the post-SINCE cohort.
    assert by_key.get(("sessions", "technical"), 0) == 1  # only the OLD one remains
    assert by_key.get(("sessions", "planning"), 0) == 1
    assert by_key.get(("sessions", "architecture"), 0) == 0
    assert by_key.get(("sessions", "general"), 0) == 0
    assert by_key.get(("sessions", "problems"), 0) == 0
    # Sessions/curated rooms preserved.
    assert by_key.get(("sessions", "decisions"), 0) == 1
    assert by_key.get(("sessions", "lessons"), 0) == 1
    assert by_key.get(("sessions", "diary"), 0) == 1
    # paideia wing untouched.
    assert by_key.get(("paideia", "technical"), 0) == 1


def test_run_idempotent(tmp_path: Path) -> None:
    """Second run with the same since deletes nothing (no candidates)."""
    palace_dir = _build_palace(tmp_path)
    first = mempalace_post_hook_prune.run(palace_dir, SINCE)
    assert first == (0, 5)
    second = mempalace_post_hook_prune.run(palace_dir, SINCE)
    assert second == (0, 0)


def test_run_missing_palace_exits_2(tmp_path: Path) -> None:
    """Palace not yet initialized — exit 2 (advisory; hook is not blocked)."""
    palace_dir = tmp_path / "nope" / "palace"
    exit_code, deleted = mempalace_post_hook_prune.run(palace_dir, SINCE)
    assert exit_code == 2
    assert deleted == 0


def test_main_logs_deleted_count(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    palace_dir = _build_palace(tmp_path)
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(palace_dir))
    rc = mempalace_post_hook_prune.main(["--since", SINCE])
    assert rc == 0
    captured = capsys.readouterr()
    assert "deleted 5" in captured.err
    assert "sessions-wing pollution" in captured.err


def test_main_silent_when_no_candidates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the prune is a no-op, do NOT emit a chatty log line."""
    palace_dir = _build_palace(tmp_path)
    monkeypatch.setenv("MEMPALACE_PROBE_PALACE_PATH", str(palace_dir))
    # Run once to drain; second run finds nothing.
    mempalace_post_hook_prune.main(["--since", SINCE])
    capsys.readouterr()  # clear
    rc = mempalace_post_hook_prune.main(["--since", SINCE])
    assert rc == 0
    captured = capsys.readouterr()
    assert "deleted" not in captured.err


def test_classifier_constants_mirror_prune_mempalace() -> None:
    """The wing+rooms classifier must stay in lock-step with the audit-mode tool."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import prune_mempalace  # noqa: PLC0415  # late import keeps test self-contained

    assert (
        mempalace_post_hook_prune._SESSIONS_POLLUTION_WING
        == prune_mempalace._SESSIONS_POLLUTION_WING
    )
    assert (
        mempalace_post_hook_prune._SESSIONS_POLLUTION_ROOMS
        == prune_mempalace._SESSIONS_POLLUTION_ROOMS
    )
