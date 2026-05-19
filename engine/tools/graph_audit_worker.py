"""Subprocess worker for graph_audit's psycopg read.

Per [ADR 0101](../adr/0101-subprocess-isolation-for-graph-audit.md). The
parent (``engine.tools.validate``) spawns this module as a subprocess so
the kernel can SIGKILL the psycopg connection when the in-process
watchdog cannot — the S-0211 empirical pin established that ``conn.cancel()``
itself can wedge against the same poisoned socket the original query
wedged on, so no in-process defense escapes.

Worker contract
---------------
- **Input** — ``SUPABASE_DB_URL`` in env. Mandatory; absence is a parent
  contract violation (exit 2).
- **Stdout** — single line of JSON on success::

      {"nodes": [...], "edges": [...]}

  UUIDs and datetimes are coerced to strings via ``default=str``
  (matches the existing ``_write_snapshot`` discipline at
  ``validate.py:_write_snapshot``).
- **Stderr** — diagnostic lines (psycopg exception type/message on
  errors). Empty on success.
- **Exit codes** —
    - 0: success
    - 2: ``SUPABASE_DB_URL`` env missing (parent contract violation)
    - 3: psycopg ``ImportError`` (parent's audit-skip path covers this
      under normal operation; defense-in-depth here)
    - 4: psycopg connect or query error (the parent surfaces as
      ``graph_audit`` hard-fail with the stderr message)
    - 5: JSON serialization failure on the result (defense-in-depth;
      not expected under today's schema)

The parent's wrapper at ``validate._run_graph_audit_subprocess`` enforces
a hard wall-clock timeout via ``subprocess.run(timeout=...)``. When the
timeout fires, ``subprocess.run`` SIGKILLs the worker before this script
gets any chance to exit cleanly — the parent records
``graph_audit_subprocess_timeout`` as a hard-fail and the pre-commit run
exits non-zero. The subsequent commit attempt re-tries cleanly because
the wedged worker is dead.

The S-0186 ``connect_timeout`` + S-0187 in-process watchdog + S-0208 TCP
keepalive layers continue to run inside the worker as inner defense-in-
depth — they handle the cases (healthy queries, server-side query stalls,
pooler wedges where ``conn.cancel()`` still functions) where the inner
layers can produce a cleaner exit than the outer SIGKILL.

Why a separate module instead of ``validate.py --graph-audit-subprocess``
- Smaller startup cost: only the worker's imports run, not all of
  ``validate.py``'s 4000+ LOC.
- Smaller blast radius for subprocess-level failures: a bug in the worker
  cannot accidentally corrupt the parent's validation state.
- Clearer test surface: ``test_graph_audit_worker.py`` covers the worker's
  ``main()`` contract directly without coupling to ``validate.py``'s test
  fixtures.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


# Exit codes — kept in sync with ADR 0101 Decision 1 and the parent's
# dispatch logic in ``validate._run_graph_audit_subprocess``.
EXIT_SUCCESS = 0
EXIT_ENV_MISSING = 2
EXIT_PSYCOPG_IMPORT_ERROR = 3
EXIT_DB_ERROR = 4
EXIT_JSON_ERROR = 5


def main() -> int:
    """Run graph_audit's DB read in a subprocess; emit JSON on stdout.

    Returns the exit code (also used as ``sys.exit`` target). Kept as a
    pure function so tests can call it without spawning a subprocess.

    The function imports ``engine.tools.validate`` lazily so tests can
    monkey-patch ``validate._read_graph_from_db`` after the worker
    module loads but before ``main()`` runs.
    """
    conn_str = os.environ.get("SUPABASE_DB_URL")
    if not conn_str:
        print(
            "[graph-audit-worker] SUPABASE_DB_URL env missing (parent "
            "contract violation; parent must set it before spawning)",
            file=sys.stderr,
        )
        return EXIT_ENV_MISSING

    try:
        # Lazy import — keeps test fixtures' monkey-patching surface intact
        # and keeps worker startup cost off the no-op-skip path.
        from engine.tools import validate
    except ImportError as exc:
        print(
            f"[graph-audit-worker] cannot import engine.tools.validate: {exc!s}",
            file=sys.stderr,
        )
        return EXIT_DB_ERROR

    try:
        nodes, edges = validate._read_graph_from_db(conn_str)
    except ImportError as exc:
        # psycopg unavailable inside the subprocess. The parent's
        # audit-skip path should have caught this before spawning, but
        # defense-in-depth: surface as exit-3 so the parent can record
        # ``graph_audit_skipped`` instead of a hard-fail.
        print(
            f"[graph-audit-worker] psycopg unavailable: {exc!s}",
            file=sys.stderr,
        )
        return EXIT_PSYCOPG_IMPORT_ERROR
    except Exception as exc:  # noqa: BLE001
        # Any other failure (psycopg connect/query error, watchdog-fired
        # QueryCanceled, etc.) routes to exit-4. Stderr carries the
        # exception type + message so the parent can build a clear
        # ``graph_audit`` hard-fail message.
        print(
            f"[graph-audit-worker] {type(exc).__name__}: {exc!s}",
            file=sys.stderr,
        )
        return EXIT_DB_ERROR

    payload: dict[str, Any] = {"nodes": nodes, "edges": edges}
    try:
        # ``default=str`` matches the existing ``_write_snapshot`` discipline
        # at validate.py — UUIDs, datetimes, and any other non-JSON-native
        # types coerce to their str() representation. The parent's
        # downstream functions (_detect_duplicate_node_ids etc.) work
        # with str ids the same way they work with UUID ids — set
        # membership and dict-key semantics are type-consistent within
        # any single subprocess run.
        line = json.dumps(payload, default=str, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        # Serialization failure. Under today's schema this cannot fire
        # (premise 3 of ADR 0101 Load-bearing premises); the path exists
        # for future schema growth that introduces an unserializable type.
        print(
            f"[graph-audit-worker] JSON serialization failed: "
            f"{type(exc).__name__}: {exc!s}",
            file=sys.stderr,
        )
        return EXIT_JSON_ERROR

    sys.stdout.write(line)
    sys.stdout.flush()
    return EXIT_SUCCESS


if __name__ == "__main__":  # pragma: no cover  (driven via subprocess in prod)
    sys.exit(main())
