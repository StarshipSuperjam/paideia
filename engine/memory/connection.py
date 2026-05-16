"""SQLite connection factory for the engine-memory substrate.

Path resolution order: explicit ``path`` arg → ``ENGINE_MEMORY_PATH``
env var → ``<repo root>/engine/.memory/engine_memory.sqlite3`` (the
repo root is the worktree root returned by ``git rev-parse
--show-toplevel``; subprocess env scrubbed per ADR 0045).

Every ``get_conn`` call:

* Resolves the path and ensures the parent directory exists.
* Opens with ``isolation_level=None`` (autocommit) + ``check_same_thread=False``
  — the MCP server may dispatch tool handlers across threads and hooks
  may invoke from sub-shells.
* Sets ``PRAGMA busy_timeout=5000`` (covers transient ``SQLITE_BUSY``
  per the SQLite single-writer model — risk #3 in the approved plan).
* Sets ``PRAGMA foreign_keys=ON`` (per-connection; the schema's
  ``PRAGMA journal_mode=WAL`` is persistent).
* Registers a Python ``exp`` function so the BM25-recency retrieval SQL
  (wired in S-0191) works even on SQLite builds without math compiled
  in. ``conn.create_function`` is per-connection — registering on every
  ``get_conn`` is the simplest correct path.
* Applies the schema via ``executescript(SCHEMA_SQL)``. Idempotent by
  construction (all DDL uses ``IF NOT EXISTS``); the ``schema_version``
  row uses ``INSERT OR IGNORE``.

:func:`healthcheck` is the substrate-alive probe. ``validate.py``'s
substrate-alive check (wired at S-0193) calls it from the hook
context.
"""

from __future__ import annotations

import math
import os
import sqlite3
import subprocess
from pathlib import Path

# Import is local to avoid pulling engine/tools onto the import path for
# the engine/memory package's clients. ``scrub_env.scrubbed_env`` lives
# in engine/tools/ and is only needed when we shell out to ``git
# rev-parse`` for the fallback path resolution.
_REPO_ROOT_CACHE: Path | None = None


def _scrubbed_env() -> dict[str, str]:
    """Return os.environ minus ``GIT_*`` keys (per ADR 0045)."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _resolve_repo_root() -> Path:
    """Resolve the worktree root via ``git rev-parse --show-toplevel``.

    The result is cached per-process. ``GIT_*`` env vars are scrubbed
    per ADR 0045 to prevent inherited git context from pointing at the
    wrong repo (the S-0033 vector).
    """
    global _REPO_ROOT_CACHE
    if _REPO_ROOT_CACHE is not None:
        return _REPO_ROOT_CACHE
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        env=_scrubbed_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    _REPO_ROOT_CACHE = Path(result.stdout.strip())
    return _REPO_ROOT_CACHE


def resolve_db_path(path: Path | str | None = None) -> Path:
    """Resolve the SQLite file path. See module docstring for order.

    Exposed so tests and hook scripts can introspect path resolution
    without opening a connection.
    """
    if path is not None:
        return Path(path)
    env_path = os.environ.get("ENGINE_MEMORY_PATH")
    if env_path:
        return Path(env_path)
    return _resolve_repo_root() / "engine" / ".memory" / "engine_memory.sqlite3"


def get_conn(path: Path | str | None = None) -> sqlite3.Connection:
    """Open (or create) the engine-memory SQLite file and apply schema.

    Idempotent: safe to call repeatedly. Each call returns a fresh
    connection — the caller is responsible for ``conn.close()`` when
    done (or letting GC reclaim it).
    """
    # Local import avoids a circular reference if schema.py ever needs
    # to import connection.py for its own helpers (it currently doesn't,
    # but the boundary keeps the door open).
    from engine.memory.schema import SCHEMA_SQL

    db_path = resolve_db_path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(db_path),
        isolation_level=None,
        check_same_thread=False,
    )
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.create_function("exp", 1, math.exp)
    conn.executescript(SCHEMA_SQL)
    return conn


def healthcheck(path: Path | str | None = None) -> None:
    """Probe substrate integrity. Raises on any failure.

    Two checks: ``PRAGMA integrity_check`` returns exactly ``'ok'``, and
    ``SELECT count(*) FROM drawers`` succeeds (proves schema is reachable).
    Used by ``validate.py``'s substrate-alive check (wired at S-0193).
    """
    conn = get_conn(path)
    try:
        rows = conn.execute("PRAGMA integrity_check").fetchall()
        if rows != [("ok",)]:
            raise RuntimeError(f"integrity_check did not return 'ok': {rows!r}")
        conn.execute("SELECT count(*) FROM drawers").fetchone()
    finally:
        conn.close()
