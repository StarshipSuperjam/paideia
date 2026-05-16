# `engine/memory/` — engine-memory substrate (SQLite + FTS5)

> Per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md). The engine-memory substrate that replaces MemPalace. Lives entirely inside the engine subtree; preserves the engine/product wall per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) (zero PostgreSQL coupling, zero schema/data relationship to `paideia-dev`).

## Substrate

Single SQLite file at `engine/.memory/engine_memory.sqlite3` (gitignored). Stdlib `sqlite3` driver; FTS5 virtual table backs full-text retrieval; six regular tables plus the FTS5 mirror.

| Table | Purpose |
|---|---|
| `schema_version` | Schema-version stamp (currently `1`). |
| `drawers` | Curated + transcript drawers; primary content surface. |
| `drawers_fts` | FTS5 virtual table mirroring `drawers.content`; sync triggers keep it current. |
| `diary` | Per-session reflections (one entry per session at close). |
| `lineage` | Per-drawer provenance (session, commit, source path, import metadata). |
| `capture_state` | Per-session capture watermark for Stop/PreCompact hook idempotency. |
| `query_log` | Per-query telemetry for the cite-worthy-rate audit. |

Schema lives at [`schema.py`](schema.py) as a single multi-statement string applied via `executescript()` at every connect. All DDL uses `IF NOT EXISTS`; the `schema_version` seed uses `INSERT OR IGNORE`. Idempotent by construction — no migration framework.

## File location and path resolution

Order:

1. Explicit `path` argument to `get_conn()`.
2. `ENGINE_MEMORY_PATH` env var.
3. `<repo root>/engine/.memory/engine_memory.sqlite3` (default).

Repo root is resolved via `git rev-parse --show-toplevel` with `GIT_*` env scrubbed (per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md)).

## MCP tool surface (six-tool ceiling)

Adding a seventh tool requires a new ADR superseding or amending ADR 0091.

| Tool | S-0189 status | Wired at |
|---|---|---|
| `engine_memory_search` | not wired | S-0191 |
| `engine_memory_add_drawer` | not wired | S-0190 |
| `engine_memory_get_drawer` | not wired | S-0191 |
| `engine_memory_list_drawers` | not wired | S-0191 |
| `engine_memory_diary_read` | not wired | S-0190 |
| `engine_memory_diary_write` | not wired | S-0190 |

The MCP server skeleton ([`mcp_server.py`](mcp_server.py)) ships at S-0189 with the JSON-RPC stdio scaffolding and an empty tool registry. `python -m engine.memory.mcp_server` runs cleanly; the server responds to `initialize`, `tools/list` (returns empty array), `ping`, and `tools/call` (returns `-32601` for any tool name).

## Backup and cross-device sync

Backup: copy the file. `cp engine/.memory/engine_memory.sqlite3{,.bak}` is the entire procedure. For a consistent hot snapshot under WAL mode, use `VACUUM INTO 'backup.sqlite3'`.

Cross-device sync is **user-managed** (per ADR 0091 Decision 3). The file is gitignored. Sync via Dropbox/iCloud/etc. or accept per-machine memory — matches MemPalace's actual prior behavior. Litestream-style replication is named out-of-scope for the initial cutover (additive future change if it ever becomes load-bearing).

## Health probe

```python
from engine.memory.connection import healthcheck
healthcheck()  # raises on integrity_check failure or schema-unreachable
```

`validate.py`'s substrate-alive check wires this in at S-0193 (replaces `_check_mempalace_substrate_alive`).
