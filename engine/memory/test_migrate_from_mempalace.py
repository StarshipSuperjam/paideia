"""Tests for ``engine.memory.migrate_from_mempalace``.

Fixtures build a minimal chroma.sqlite3-shaped palace (the read-only
enumeration surface) plus a chromadb stub for content fetch, so we can
exercise the migration end-to-end without depending on a live mempalace
install.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from engine.memory import migrate_from_mempalace as m
from engine.memory.connection import get_conn


# --------------------------------------------------------------------
# Palace fixture (read-only sqlite shape used by enumerate_*)
# --------------------------------------------------------------------


def _make_palace(palace_path: Path, drawers: list[dict[str, Any]]) -> None:
    """Build a fake chroma.sqlite3 with embedding_metadata + embeddings rows.

    Each ``drawers`` entry is a dict with keys: ``internal_id`` (int),
    ``uuid`` (str), ``wing`` (str), ``room`` (str), ``filed_at`` (str or None).
    """
    palace_path.mkdir(parents=True, exist_ok=True)
    db = palace_path / "chroma.sqlite3"
    con = sqlite3.connect(db)
    try:
        con.executescript(
            """
            CREATE TABLE embedding_metadata (
                id INTEGER,
                key TEXT,
                string_value TEXT
            );
            CREATE TABLE embeddings (
                id INTEGER PRIMARY KEY,
                embedding_id TEXT
            );
            """
        )
        for d in drawers:
            con.execute(
                "INSERT INTO embeddings (id, embedding_id) VALUES (?, ?)",
                (d["internal_id"], d["uuid"]),
            )
            con.execute(
                "INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, 'wing', ?)",
                (d["internal_id"], d["wing"]),
            )
            con.execute(
                "INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, 'room', ?)",
                (d["internal_id"], d["room"]),
            )
            if d.get("filed_at"):
                con.execute(
                    "INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, 'filed_at', ?)",
                    (d["internal_id"], d["filed_at"]),
                )
        con.commit()
    finally:
        con.close()


class _StubCollection:
    """Stands in for chromadb's collection.get(ids=..., include=...)."""

    def __init__(self, by_uuid: dict[str, dict[str, Any]]) -> None:
        self._by_uuid = by_uuid

    def get(
        self, ids: list[str], include: list[str] | None = None
    ) -> dict[str, list[Any]]:
        ids_present = [u for u in ids if u in self._by_uuid]
        docs = [self._by_uuid[u]["content"] for u in ids_present]
        metas = [self._by_uuid[u]["metadata"] for u in ids_present]
        return {"ids": ids_present, "documents": docs, "metadatas": metas}


class _StubClient:
    def __init__(self, by_uuid: dict[str, dict[str, Any]]) -> None:
        self._col = _StubCollection(by_uuid)

    def get_collection(self, name: str) -> _StubCollection:
        assert name == "mempalace_drawers"
        return self._col


@pytest.fixture
def chromadb_stub(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, dict[str, Any]]:
    """Patch the chromadb import inside fetch_content_batch."""
    by_uuid: dict[str, dict[str, Any]] = {}

    class _ChromadbModule:
        @staticmethod
        def PersistentClient(path: str) -> _StubClient:  # noqa: N802
            return _StubClient(by_uuid)

    import sys

    monkeypatch.setitem(sys.modules, "chromadb", _ChromadbModule)
    return by_uuid


# --------------------------------------------------------------------
# Enumeration tests
# --------------------------------------------------------------------


def test_enumerate_drawers_picks_only_curated_rooms(tmp_path: Path) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u-keep-decision",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": "2026-05-15 10:00:00",
            },
            {
                "internal_id": 2,
                "uuid": "u-keep-pushback",
                "wing": "wing_paideia",
                "room": "pushback",
                "filed_at": "2026-05-15 11:00:00",
            },
            {
                "internal_id": 3,
                "uuid": "u-drop-work",
                "wing": "wing_paideia",
                "room": "work",
                "filed_at": None,
            },
            {
                "internal_id": 4,
                "uuid": "u-drop-general",
                "wing": "paideia",
                "room": "general",
                "filed_at": None,
            },
        ],
    )
    con = m.open_palace_ro(palace)
    try:
        found = m.enumerate_drawers(con)
    finally:
        con.close()
    rooms = {c.room for c in found}
    assert rooms == {"decisions", "pushback"}
    assert all(c.uuid == "" for c in found)  # uuid not hydrated yet


def test_enumerate_diary_picks_diary_room_any_wing(tmp_path: Path) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 10,
                "uuid": "u-diary-claude",
                "wing": "wing_claude",
                "room": "diary",
                "filed_at": "2026-05-16 09:00:00",
            },
            {
                "internal_id": 11,
                "uuid": "u-diary-paideia",
                "wing": "paideia",
                "room": "diary",
                "filed_at": None,
            },
            {
                "internal_id": 12,
                "uuid": "u-not-diary",
                "wing": "wing_claude",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    con = m.open_palace_ro(palace)
    try:
        found = m.enumerate_diary(con)
    finally:
        con.close()
    assert {e.internal_id for e in found} == {"10", "11"}


def test_map_internal_ids_to_uuids_returns_mapping(tmp_path: Path) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "uuid-A",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
            {
                "internal_id": 2,
                "uuid": "uuid-B",
                "wing": "paideia",
                "room": "lessons",
                "filed_at": None,
            },
        ],
    )
    mapping = m.map_internal_ids_to_uuids(palace, ["1", "2"])
    assert mapping == {"1": "uuid-A", "2": "uuid-B"}


def test_map_internal_ids_to_uuids_empty_returns_empty(tmp_path: Path) -> None:
    palace = tmp_path / "palace"
    _make_palace(palace, drawers=[])
    assert m.map_internal_ids_to_uuids(palace, []) == {}


# --------------------------------------------------------------------
# Content fetch + hydrate
# --------------------------------------------------------------------


def test_fetch_content_batch_returns_doc_and_metadata(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    palace.mkdir()
    chromadb_stub["uuid-A"] = {
        "content": "A decision body",
        "metadata": {"wing": "paideia", "room": "decisions"},
    }
    result = m.fetch_content_batch(palace, ["uuid-A", "uuid-missing"])
    assert "uuid-A" in result
    assert "uuid-missing" not in result
    assert result["uuid-A"]["content"] == "A decision body"


def test_hydrate_candidates_fills_uuid_and_content(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "uuid-D",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    chromadb_stub["uuid-D"] = {
        "content": "decision content",
        "metadata": {
            "wing": "paideia",
            "room": "decisions",
            "added_by": "claude-s0042",
        },
    }
    drawers = [
        m.DrawerCandidate(
            internal_id="1", wing="paideia", room="decisions", filed_at=None
        )
    ]
    m.hydrate_candidates(palace, drawers, [])
    assert drawers[0].uuid == "uuid-D"
    assert drawers[0].content == "decision content"
    assert drawers[0].metadata["added_by"] == "claude-s0042"


# --------------------------------------------------------------------
# Tag encoding
# --------------------------------------------------------------------


def test_encode_tags_list_input() -> None:
    assert m._encode_tags({"tags": ["adr", "decision-narrative"]}) == json.dumps(
        ["adr", "decision-narrative"]
    )


def test_encode_tags_json_string_input() -> None:
    assert m._encode_tags({"tags": '["x", "y"]'}) == '["x", "y"]'


def test_encode_tags_csv_string_input() -> None:
    assert m._encode_tags({"tags": "a, b , c"}) == json.dumps(["a", "b", "c"])


def test_encode_tags_missing_returns_empty_array() -> None:
    assert m._encode_tags({}) == "[]"


def test_encode_tags_unknown_shape_returns_empty_array() -> None:
    assert m._encode_tags({"tags": 42}) == "[]"


# --------------------------------------------------------------------
# End-to-end migration
# --------------------------------------------------------------------


def test_run_migration_inserts_curated_drawers(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u1",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": "2026-05-15 10:00:00",
            },
            {
                "internal_id": 2,
                "uuid": "u2",
                "wing": "wing_paideia",
                "room": "pushback",
                "filed_at": "2026-05-15 11:00:00",
            },
            {
                "internal_id": 3,
                "uuid": "u3",
                "wing": "wing_paideia",
                "room": "work",
                "filed_at": None,
            },  # dropped
        ],
    )
    chromadb_stub.update(
        {
            "u1": {
                "content": "ADR 0091 decision narrative",
                "metadata": {"wing": "paideia", "room": "decisions", "tags": ["adr"]},
            },
            "u2": {
                "content": "pushback against MCP-only path",
                "metadata": {"wing": "wing_paideia", "room": "pushback"},
            },
        }
    )
    target_db = tmp_path / "engine_memory.sqlite3"
    report = m.run_migration(palace, target_db)
    assert report.drawer_candidates == 2
    assert report.drawer_inserted == 2
    assert report.drawer_skipped_already_imported == 0
    assert report.drawer_per_room == {"decisions": 1, "pushback": 1}
    assert report.fts_count_after == report.drawers_count_after == 2
    assert report.assertion_failures == []


def test_run_migration_is_idempotent_on_rerun(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u1",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    chromadb_stub["u1"] = {
        "content": "first body",
        "metadata": {"wing": "paideia", "room": "decisions"},
    }
    target_db = tmp_path / "engine_memory.sqlite3"
    first = m.run_migration(palace, target_db)
    second = m.run_migration(palace, target_db)
    assert first.drawer_inserted == 1
    assert second.drawer_inserted == 0
    assert second.drawer_skipped_already_imported == 1
    # Post-state still consistent
    target = get_conn(path=target_db)
    try:
        n = target.execute("SELECT count(*) FROM drawers").fetchone()[0]
        ln = target.execute(
            "SELECT count(*) FROM lineage WHERE source=?",
            (m.MIGRATION_SOURCE,),
        ).fetchone()[0]
    finally:
        target.close()
    assert n == 1
    assert ln == 1


def test_run_migration_imports_diary_with_deterministic_ids(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 10,
                "uuid": "diary-uuid",
                "wing": "wing_claude",
                "room": "diary",
                "filed_at": "2026-05-16 12:00:00",
            },
        ],
    )
    chromadb_stub["diary-uuid"] = {
        "content": "today I learned X",
        "metadata": {"topic": "engine-memory cutover", "session_id": "S-0192"},
    }
    target_db = tmp_path / "engine_memory.sqlite3"
    first = m.run_migration(palace, target_db)
    assert first.diary_inserted == 1
    target = get_conn(path=target_db)
    try:
        rows = target.execute(
            "SELECT id, session_id, topic FROM diary WHERE agent_name='claude'"
        ).fetchall()
    finally:
        target.close()
    assert len(rows) == 1
    assert rows[0][1] == "S-0192"
    assert rows[0][2] == "engine-memory cutover"
    # Rerun deterministic ID → no duplicate
    second = m.run_migration(palace, target_db)
    assert second.diary_inserted == 0
    assert second.diary_skipped_already_imported == 1


def test_run_migration_skips_drawers_with_missing_content(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u-missing",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    # uuid-missing not registered in chromadb_stub → content not fetched
    target_db = tmp_path / "engine_memory.sqlite3"
    report = m.run_migration(palace, target_db)
    assert report.drawer_inserted == 0
    assert report.drawer_skipped_missing_content == 1


def test_run_migration_dry_run_does_not_touch_target(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u1",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    chromadb_stub["u1"] = {"content": "body", "metadata": {}}
    target_db = tmp_path / "engine_memory.sqlite3"
    report = m.run_migration(palace, target_db, dry_run=True)
    assert report.drawer_candidates == 1
    assert report.drawer_inserted == 0
    # Target DB not even created on dry-run
    assert not target_db.exists()


def test_verify_migration_detects_per_room_mismatch(tmp_path: Path) -> None:
    target_db = tmp_path / "engine_memory.sqlite3"
    target = get_conn(path=target_db)
    try:
        failures, _, _, _ = m.verify_migration(
            target,
            expected_drawers_lineage=0,
            expected_per_room={"decisions": 5},
        )
    finally:
        target.close()
    assert any("decisions" in f for f in failures)


def test_main_exits_2_when_palace_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "no-palace"
    rc = m.main(["--palace", str(missing)])
    assert rc == 2
    captured = capsys.readouterr()
    assert "palace not found" in captured.err


def test_main_exits_3_on_assertion_failure(
    tmp_path: Path,
    chromadb_stub: dict[str, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u1",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    chromadb_stub["u1"] = {"content": "body", "metadata": {}}
    target_db = tmp_path / "engine_memory.sqlite3"
    original_verify = m.verify_migration

    def _broken_verify(*args: Any, **kwargs: Any) -> tuple[list[str], int, int, int]:
        return (["injected drift"], 0, 0, 0)

    monkeypatch.setattr(m, "verify_migration", _broken_verify)
    rc = m.main(["--palace", str(palace), "--db-path", str(target_db)])
    assert rc == 3
    monkeypatch.setattr(m, "verify_migration", original_verify)


def test_main_exits_0_on_clean_dry_run(
    tmp_path: Path, chromadb_stub: dict[str, dict[str, Any]]
) -> None:
    palace = tmp_path / "palace"
    _make_palace(
        palace,
        drawers=[
            {
                "internal_id": 1,
                "uuid": "u1",
                "wing": "paideia",
                "room": "decisions",
                "filed_at": None,
            },
        ],
    )
    chromadb_stub["u1"] = {"content": "body", "metadata": {}}
    rc = m.main(["--palace", str(palace), "--dry-run"])
    assert rc == 0
