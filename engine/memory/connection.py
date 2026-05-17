"""SQLite connection factory for the engine-memory substrate.

Path resolution order: explicit ``path`` arg → ``ENGINE_MEMORY_PATH``
env var → ``<main repo root>/engine/.memory/engine_memory.sqlite3``.
The main repo root is derived from ``git rev-parse --git-common-dir``
(the shared ``.git``) so all worktrees of the same clone resolve to
the SAME SQLite file — that's what makes the substrate's
cross-session continuity actually work when sessions run in fresh
worktrees. Subprocess env scrubbed per ADR 0045. The pre-S-0193
``--show-toplevel`` resolver produced a per-worktree file, defeating
the design; corrected during the S-0193 cutover.

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
    """Resolve the shared main repo root (works from worktrees too).

    Uses ``git rev-parse --git-common-dir`` to get the path to the
    shared ``.git`` directory, then walks one level up to the main
    repo's working tree. This intentionally differs from
    ``--show-toplevel`` (which returns the *current worktree's* path,
    not the shared main repo): engine_memory must resolve to the
    SAME SQLite file from every worktree on the same clone so a
    session in worktree A sees the decision drawers written by an
    earlier session in worktree B. The pre-S-0193 ``--show-toplevel``
    resolver produced a per-worktree SQLite file, defeating the
    substrate's cross-session continuity guarantee — discovered when
    the S-0193 cutover migrated into the main-repo file and the
    worktree session could not read it back.

    The result is cached per-process. ``GIT_*`` env vars are scrubbed
    per ADR 0045 to prevent inherited git context from pointing at the
    wrong repo (the S-0033 vector).
    """
    global _REPO_ROOT_CACHE
    if _REPO_ROOT_CACHE is not None:
        return _REPO_ROOT_CACHE
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        env=_scrubbed_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    # ``--git-common-dir`` returns the shared ``.git`` path: absolute
    # when invoked from a linked worktree, relative ``.git`` when
    # invoked from the main repo's working tree. ``.resolve()`` turns
    # both into the same absolute path; ``.parent`` then yields the
    # main repo's working-tree root regardless of caller's CWD.
    common_dir = Path(result.stdout.strip()).resolve()
    _REPO_ROOT_CACHE = common_dir.parent
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
