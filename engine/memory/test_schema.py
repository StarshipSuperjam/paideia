"""Tests for ``engine/memory/schema.py`` — schema application + idempotency.

Per the T1-A criterion: every DDL uses ``IF NOT EXISTS``; the
``schema_version`` seed uses ``INSERT OR IGNORE``; applying ``SCHEMA_SQL``
twice produces identical state with no errors.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.memory.connection import get_conn
from engine.memory.schema import SCHEMA_SQL, SCHEMA_VERSION

EXPECTED_TABLES = {
    "schema_version",
    "drawers",
    "diary",
    "lineage",
    "capture_state",
    "query_log",
}
EXPECTED_INDEXES = {
    "drawers_room_filed_at",
    "drawers_session_id",
    "drawers_filed_at",
    "diary_agent_created_at",
    "lineage_session_id",
    "query_log_session_id",
}
EXPECTED_TRIGGERS = {
    "drawers_fts_insert",
    "drawers_fts_delete",
    "drawers_fts_update",
}


def _list_objects(conn: sqlite3.Connection, kind: str) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type=? AND name NOT LIKE 'sqlite_%'",
        (kind,),
    ).fetchall()
    return {r[0] for r in rows}


def test_schema_creates_all_tables(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        names = _list_objects(conn, "table")
        # FTS5 creates shadow tables (drawers_fts_data, drawers_fts_idx,
        # drawers_fts_docsize, drawers_fts_config) that are internal —
        # require the named user tables AND the FTS5 root entry.
        assert EXPECTED_TABLES <= names, f"missing tables: {EXPECTED_TABLES - names}"
        assert "drawers_fts" in names, "drawers_fts virtual table missing"
    finally:
        conn.close()


def test_schema_creates_all_indexes(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        names = _list_objects(conn, "index")
        # FTS5 also registers internal indexes whose names start with
        # sqlite_autoindex_ or are FTS5-internal; the filter above drops
        # sqlite_autoindex_*. Require exactly the user-declared indexes
        # as a subset.
        assert EXPECTED_INDEXES <= names, f"missing indexes: {EXPECTED_INDEXES - names}"
    finally:
        conn.close()


def test_schema_creates_fts_triggers(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        names = _list_objects(conn, "trigger")
        assert EXPECTED_TRIGGERS <= names, (
            f"missing triggers: {EXPECTED_TRIGGERS - names}"
        )
    finally:
        conn.close()


def test_schema_version_seeded(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        rows = conn.execute(
            "SELECT version FROM schema_version ORDER BY version"
        ).fetchall()
        assert rows == [(SCHEMA_VERSION,)], (
            f"expected single version-{SCHEMA_VERSION} row, got {rows!r}"
        )
    finally:
        conn.close()


def test_schema_is_idempotent(tmp_path: Path) -> None:
    """Applying SCHEMA_SQL a second time produces no errors + identical state."""
    db_path = tmp_path / "test.sqlite3"
    conn1 = get_conn(db_path)
    try:
        tables_before = _list_objects(conn1, "table")
        version_before = conn1.execute("SELECT count(*) FROM schema_version").fetchone()
    finally:
        conn1.close()

    # Second get_conn applies SCHEMA_SQL again — must not raise.
    conn2 = get_conn(db_path)
    try:
        tables_after = _list_objects(conn2, "table")
        version_after = conn2.execute("SELECT count(*) FROM schema_version").fetchone()
    finally:
        conn2.close()

    assert tables_before == tables_after
    assert version_before == version_after == (1,), (
        "schema_version row count drifted across re-apply"
    )


def test_schema_executescript_directly(tmp_path: Path) -> None:
    """Apply SCHEMA_SQL directly to a raw sqlite3 connection.

    Belt-and-braces: even if ``get_conn`` adds shape over time, the raw
    SQL still applies cleanly.
    """
    db_path = tmp_path / "raw.sqlite3"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_SQL)
        # Re-apply must not error either.
        conn.executescript(SCHEMA_SQL)
        names = _list_objects(conn, "table")
        assert EXPECTED_TABLES <= names
    finally:
        conn.close()


def test_drawers_room_check_constraint(tmp_path: Path) -> None:
    """A drawer with an out-of-domain room raises CHECK violation."""
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO drawers (id, room, source_kind, content) "
                "VALUES ('t1', 'bogus_room', 'manual', 'x')"
            )
    finally:
        conn.close()


def test_drawers_source_kind_check_constraint(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO drawers (id, room, source_kind, content) "
                "VALUES ('t1', 'general', 'bogus_kind', 'x')"
            )
    finally:
        conn.close()


def test_fts_trigger_round_trip(tmp_path: Path) -> None:
    """Insert into drawers → FTS5 trigger populates drawers_fts → MATCH finds it.

    Delete from drawers → FTS5 trigger removes the row → MATCH no longer finds it.
    The unicode61 tokenizer treats hyphens as separators; tests use
    underscore-joined needles so MATCH does not parse them as exclusion
    operators.
    """
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        conn.execute(
            "INSERT INTO drawers (id, room, source_kind, content) "
            "VALUES ('t1', 'general', 'manual', 'hello world uniqueneedlexyz')"
        )
        rows = conn.execute(
            "SELECT content FROM drawers_fts WHERE drawers_fts MATCH 'uniqueneedlexyz'"
        ).fetchall()
        assert rows == [("hello world uniqueneedlexyz",)]

        conn.execute("DELETE FROM drawers WHERE id='t1'")
        rows_after = conn.execute(
            "SELECT content FROM drawers_fts WHERE drawers_fts MATCH 'uniqueneedlexyz'"
        ).fetchall()
        assert rows_after == []
    finally:
        conn.close()


def test_fts_update_trigger_replaces_content(tmp_path: Path) -> None:
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        conn.execute(
            "INSERT INTO drawers (id, room, source_kind, content) "
            "VALUES ('t1', 'general', 'manual', 'alphaneedle')"
        )
        conn.execute("UPDATE drawers SET content='betaneedle' WHERE id='t1'")
        alpha_rows = conn.execute(
            "SELECT content FROM drawers_fts WHERE drawers_fts MATCH 'alphaneedle'"
        ).fetchall()
        beta_rows = conn.execute(
            "SELECT content FROM drawers_fts WHERE drawers_fts MATCH 'betaneedle'"
        ).fetchall()
        assert alpha_rows == []
        assert beta_rows == [("betaneedle",)]
    finally:
        conn.close()


def test_lineage_cascades_on_drawer_delete(tmp_path: Path) -> None:
    """Deleting a drawer cascades to its lineage rows (FK ON DELETE CASCADE)."""
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        conn.execute(
            "INSERT INTO drawers (id, room, source_kind, content) "
            "VALUES ('t1', 'general', 'manual', 'x')"
        )
        conn.execute(
            "INSERT INTO lineage (drawer_id, source, session_id) "
            "VALUES ('t1', 'test', 'S-test')"
        )
        before = conn.execute("SELECT count(*) FROM lineage").fetchone()
        assert before == (1,)
        conn.execute("DELETE FROM drawers WHERE id='t1'")
        after = conn.execute("SELECT count(*) FROM lineage").fetchone()
        assert after == (0,)
    finally:
        conn.close()
