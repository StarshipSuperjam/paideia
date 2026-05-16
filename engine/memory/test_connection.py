"""Tests for ``engine/memory/connection.py`` — open, pragmas, fallbacks, healthcheck."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.memory.connection import get_conn, healthcheck, resolve_db_path


def test_get_conn_creates_file(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    assert not db_path.exists()
    conn = get_conn(db_path)
    try:
        assert db_path.exists()
        assert db_path.stat().st_size > 0
    finally:
        conn.close()


def test_get_conn_creates_parent_directory(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "subdir" / "test.sqlite3"
    assert not db_path.parent.exists()
    conn = get_conn(db_path)
    try:
        assert db_path.exists()
    finally:
        conn.close()


def test_get_conn_is_idempotent(tmp_path: Path) -> None:
    """Calling get_conn twice on the same path returns working connections each time."""
    db_path = tmp_path / "test.sqlite3"
    conn1 = get_conn(db_path)
    try:
        conn1.execute(
            "INSERT INTO drawers (id, room, source_kind, content) "
            "VALUES ('idem-1', 'general', 'manual', 'x')"
        )
    finally:
        conn1.close()

    conn2 = get_conn(db_path)
    try:
        rows = conn2.execute("SELECT id FROM drawers").fetchall()
        assert rows == [("idem-1",)]
    finally:
        conn2.close()


def test_wal_mode_active(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    conn = get_conn(db_path)
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"
    finally:
        conn.close()


def test_foreign_keys_pragma_on(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    conn = get_conn(db_path)
    try:
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1
    finally:
        conn.close()


def test_busy_timeout_set(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    conn = get_conn(db_path)
    try:
        timeout_ms = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        assert timeout_ms == 5000
    finally:
        conn.close()


def test_exp_function_fallback(tmp_path: Path) -> None:
    """The Python ``exp`` function is registered for the retrieval SQL.

    The BM25 retrieval contract (wired at S-0191) uses ``exp()`` for the
    recency half-life weight. Some SQLite builds don't compile math
    functions in; the connection module registers a Python fallback so
    the SQL is portable.
    """
    db_path = tmp_path / "test.sqlite3"
    conn = get_conn(db_path)
    try:
        result = conn.execute("SELECT exp(0)").fetchone()[0]
        assert result == pytest.approx(1.0)
        result_one = conn.execute("SELECT exp(1)").fetchone()[0]
        assert result_one == pytest.approx(2.718281828, rel=1e-6)
    finally:
        conn.close()


def test_resolve_db_path_explicit_arg(tmp_path: Path) -> None:
    db_path = tmp_path / "explicit.sqlite3"
    assert resolve_db_path(db_path) == db_path


def test_resolve_db_path_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "from_env.sqlite3"
    monkeypatch.setenv("ENGINE_MEMORY_PATH", str(target))
    assert resolve_db_path() == target


def test_resolve_db_path_default_uses_repo_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default path falls back to <repo-root>/engine/.memory/engine_memory.sqlite3."""
    monkeypatch.delenv("ENGINE_MEMORY_PATH", raising=False)
    # Reset the cache so the test exercises actual git rev-parse.
    import engine.memory.connection as conn_mod

    monkeypatch.setattr(conn_mod, "_REPO_ROOT_CACHE", None)
    resolved = resolve_db_path()
    assert resolved.name == "engine_memory.sqlite3"
    assert resolved.parent.name == ".memory"
    assert resolved.parent.parent.name == "engine"


def test_healthcheck_passes_on_fresh_file(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    healthcheck(db_path)  # must not raise


def test_healthcheck_raises_on_corrupted_file(tmp_path: Path) -> None:
    """A file with non-SQLite bytes triggers a clear error.

    sqlite3 may raise ``DatabaseError`` (file is not a database) at open
    time, or ``RuntimeError`` from our integrity_check assertion if the
    file is technically valid SQLite but corrupted in a way sqlite can
    open. Either is acceptable — both signal "this is not the substrate
    we expect."
    """
    db_path = tmp_path / "corrupt.sqlite3"
    db_path.write_bytes(b"this is not a sqlite database")
    with pytest.raises((sqlite3.DatabaseError, RuntimeError)):
        healthcheck(db_path)


def test_drawers_default_timestamps(tmp_path: Path) -> None:
    """Newly-inserted drawer rows carry non-null ``created_at`` and ``filed_at``."""
    conn = get_conn(tmp_path / "test.sqlite3")
    try:
        conn.execute(
            "INSERT INTO drawers (id, room, source_kind, content) "
            "VALUES ('t1', 'general', 'manual', 'x')"
        )
        row = conn.execute(
            "SELECT created_at, filed_at, tags, metadata, agent FROM drawers WHERE id='t1'"
        ).fetchone()
        created_at, filed_at, tags, metadata, agent = row
        assert created_at and len(created_at) >= len("2025-01-01 00:00:00")
        assert filed_at and len(filed_at) >= len("2025-01-01 00:00:00")
        assert tags == "[]"
        assert metadata == "{}"
        assert agent == "claude"
    finally:
        conn.close()
