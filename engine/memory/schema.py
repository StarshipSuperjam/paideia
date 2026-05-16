"""SQL schema for the engine-memory substrate.

The full schema lives as a single multi-statement string applied via
``sqlite3.Connection.executescript`` from
:func:`engine.memory.connection.get_conn`. Every DDL statement uses
``IF NOT EXISTS`` so repeated application is idempotent — there is no
migration framework. Schema version is tracked in the
``schema_version`` table; bumping the version requires authoring an
additive migration script that runs after ``executescript(SCHEMA_SQL)``
applies version-1 to a fresh file.

Authored verbatim from the approved plan
``~/.claude/plans/mempalace-overhead-is-dragging-twinkly-harp.md``
(lines 147-240) per ADR 0091.
"""

from __future__ import annotations

SCHEMA_VERSION = 1

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
  version    INTEGER NOT NULL PRIMARY KEY,
  applied_at TEXT    NOT NULL DEFAULT (datetime('now')),
  notes      TEXT
);
INSERT OR IGNORE INTO schema_version (version, notes) VALUES (1, 'initial');

CREATE TABLE IF NOT EXISTS drawers (
  id            TEXT PRIMARY KEY,
  room          TEXT NOT NULL
                  CHECK (room IN ('decisions','pushback','lessons',
                                  'exploration','operations','work','general')),
  tags          TEXT NOT NULL DEFAULT '[]',
  source_kind   TEXT NOT NULL
                  CHECK (source_kind IN ('manual','hook_stop','hook_precompact',
                                         'export_replay','migration_seed')),
  agent         TEXT NOT NULL DEFAULT 'claude',
  session_id    TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  filed_at      TEXT NOT NULL DEFAULT (datetime('now')),
  content       TEXT NOT NULL,
  metadata      TEXT NOT NULL DEFAULT '{}',
  superseded_by TEXT REFERENCES drawers(id),
  superseded_at TEXT
);
CREATE INDEX IF NOT EXISTS drawers_room_filed_at ON drawers (room, filed_at DESC);
CREATE INDEX IF NOT EXISTS drawers_session_id    ON drawers (session_id);
CREATE INDEX IF NOT EXISTS drawers_filed_at      ON drawers (filed_at DESC);

-- FTS5 virtual table mirrors drawer content; rebuilt via triggers.
CREATE VIRTUAL TABLE IF NOT EXISTS drawers_fts USING fts5(
  content,
  content='drawers',
  content_rowid='rowid',
  tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS drawers_fts_insert AFTER INSERT ON drawers BEGIN
  INSERT INTO drawers_fts(rowid, content) VALUES (new.rowid, new.content);
END;
CREATE TRIGGER IF NOT EXISTS drawers_fts_delete AFTER DELETE ON drawers BEGIN
  INSERT INTO drawers_fts(drawers_fts, rowid, content) VALUES('delete', old.rowid, old.content);
END;
CREATE TRIGGER IF NOT EXISTS drawers_fts_update AFTER UPDATE OF content ON drawers BEGIN
  INSERT INTO drawers_fts(drawers_fts, rowid, content) VALUES('delete', old.rowid, old.content);
  INSERT INTO drawers_fts(rowid, content) VALUES (new.rowid, new.content);
END;

CREATE TABLE IF NOT EXISTS diary (
  id         TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL DEFAULT 'claude',
  session_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  content    TEXT NOT NULL,
  topic      TEXT
);
CREATE INDEX IF NOT EXISTS diary_agent_created_at ON diary (agent_name, created_at DESC);

CREATE TABLE IF NOT EXISTS lineage (
  drawer_id       TEXT NOT NULL REFERENCES drawers(id) ON DELETE CASCADE,
  source          TEXT NOT NULL,
  session_id      TEXT,
  commit_sha      TEXT,
  source_path     TEXT,
  source_adr_id   TEXT,
  imported_from   TEXT,
  source_wing     TEXT,
  source_filed_at TEXT,
  imported_at     TEXT,
  PRIMARY KEY (drawer_id, source)
);
CREATE INDEX IF NOT EXISTS lineage_session_id ON lineage (session_id);

CREATE TABLE IF NOT EXISTS capture_state (
  session_id               TEXT PRIMARY KEY,
  last_stop_save_at        TEXT,
  message_count_since_save INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS query_log (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  queried_at       TEXT NOT NULL DEFAULT (datetime('now')),
  session_id       TEXT,
  formulation      TEXT NOT NULL,
  query_text       TEXT NOT NULL,
  result_count     INTEGER NOT NULL,
  cited_in_outcome INTEGER
);
CREATE INDEX IF NOT EXISTS query_log_session_id ON query_log (session_id);
"""
