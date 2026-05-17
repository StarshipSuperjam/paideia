# Engine-memory operations

> The engine's recall + reflection substrate. Local SQLite + FTS5 owned by `engine/memory/`. Replaces MemPalace per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md).
>
> Layer 1 source-of-truth for the substrate's operational surface. The recipe-form lives at the three build-mode Skills (`session-build-lifecycle`, `session-shutdown-sequence`, `routine-mode-lifecycle`) per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md); updates flow doc → skill, never the reverse.

## What it is

`engine_memory` is a thin SQLite-backed recall layer that holds:

- **Drawers** — curated decisions, pushback, lessons, exploration notes, operational reference, and hook-driven transcript captures. Schema enforces a 7-room CHECK constraint (`decisions`, `pushback`, `lessons`, `exploration`, `operations`, `work`, `general`).
- **Diary entries** — per-session first-person AI reflections, one row per `engine_memory_diary_write` call. Separate table from drawers; `agent_name` defaults to `'claude'`.
- **Lineage** — provenance trail. Migration import records carry `source='mempalace_replay_S-0192'`; future imports follow the same shape. Composite PK `(drawer_id, source)` makes idempotent replay safe.
- **Capture state** — per-session watermark for the Stop/PreCompact hook's idempotent transcript capture.
- **Query log** — every `engine_memory_search` invocation (boot orchestrator + direct MCP calls) writes one row per formulation. Telemetry surface; not load-bearing for retrieval.

Retrieval is FTS5 (Porter stemmer + Unicode61 tokenizer) with composite ranking: `-bm25 + recency-decay (30-day half-life) + room-filter boost + tag-class boost (decision/pushback/lesson +0.15)`. No vector embeddings. The trade-off rationale is recorded in ADR 0091 Decision 3 and the "Load-bearing premises" section.

## Substrate location

File: `<repo-root>/engine/.memory/engine_memory.sqlite3`. Gitignored. Resolution precedence (in `engine.memory.connection.resolve_db_path`):

1. Explicit `path` argument.
2. `ENGINE_MEMORY_PATH` environment variable.
3. `<git rev-parse --show-toplevel>/engine/.memory/engine_memory.sqlite3`.

The `git rev-parse` fallback runs under a scrubbed `GIT_*` environment per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md).

**Cross-device / cross-worktree implications.** Because the file is gitignored, each worktree creates its own substrate the first time the Stop hook or MCP server runs. There is no built-in sync. If you want continuity across machines, surface the file via Dropbox / iCloud / a syncthing share by overriding `ENGINE_MEMORY_PATH`. Same posture as MemPalace's chromadb (per ADR 0091 commitment 7).

## Schema

Seven tables + one FTS5 virtual table + three FTS5 triggers; defined idempotently in [`engine/memory/schema.py`](../memory/schema.py):

| Table | Purpose |
|---|---|
| `schema_version` | One-row marker (version=1; `INSERT OR IGNORE` on init). |
| `drawers` | Recall content. Composite indices on `(room, filed_at DESC)`, `(session_id)`, `(filed_at DESC)`. |
| `drawers_fts` | FTS5 virtual table mirroring `drawers.content`. Maintained by three triggers (INSERT / DELETE / UPDATE OF content). |
| `diary` | Per-session reflections. Indexed on `(agent_name, created_at DESC)`. |
| `lineage` | Provenance. Composite PK `(drawer_id, source)`. Cascades on drawer DELETE. |
| `capture_state` | Per-session transcript-capture watermark. |
| `query_log` | Telemetry: one row per search formulation. |

All DDL uses `IF NOT EXISTS`. The schema applies on every `get_conn()` call — there is no migration framework, and a fresh sqlite3 file becomes a fully-shaped substrate on first open.

Connection pragmas applied per-connection:

- `PRAGMA journal_mode=WAL` (persistent across connections; set at schema apply).
- `PRAGMA foreign_keys=ON` (per-connection; re-applied every open).
- `PRAGMA busy_timeout=5000` (5 second wait on `SQLITE_BUSY`; covers single-writer overlap between Stop hook + MCP server).

A Python `exp` function is registered per-connection so the BM25-recency SQL works on SQLite builds without compiled math.

## MCP tool surface (ceiling: 6 tools per ADR 0091 Decision 5)

| Tool | Purpose |
|---|---|
| `engine_memory_search` | FTS5 + BM25 + recency + tag-class-boost retrieval. Returns top-K candidates. Wraps `boot_surface.fetch_candidates`; writes one `query_log` row tagged `formulation='mcp_call'`. |
| `engine_memory_add_drawer` | Insert a curated drawer. Validates `room` and `source_kind` against substrate CHECK constraints. Optional lineage row. |
| `engine_memory_get_drawer` | Fetch one drawer by ID + its lineage rows. Raises `LookupError` if missing. |
| `engine_memory_list_drawers` | Paginated browse (room + tag filters; excludes superseded). |
| `engine_memory_diary_read` | Return up to `last_n` diary entries for an agent, ordered most-recent first. |
| `engine_memory_diary_write` | Append one diary entry. Validates non-empty content. |

The ceiling is pre-committed: adding a seventh tool requires a new ADR superseding or amending ADR 0091. The intent is to keep the surface auditable.

MCP server entry point: `python -m engine.memory.mcp_server`. JSON-RPC over stdio; stdout-protection ensures non-protocol output goes to stderr. Wire in `.mcp.json` with the venv python pinned:

```json
"engine_memory": {
  "command": "<absolute path>/.venv/bin/python",
  "args": ["-m", "engine.memory.mcp_server"]
}
```

## Hook wiring

Two hook surfaces feed the substrate:

- **Stop + PreCompact** invoke [`engine/tools/hooks/engine-memory-capture.sh`](../tools/hooks/engine-memory-capture.sh), which runs `python -m engine.memory.capture {stop|precompact}`. The capture handler reads the transcript JSONL via the harness hook env vars, computes a delta since the last save (per-session watermark in `capture_state`), lightly noise-strips huge tool results, chunks large bodies, and INSERTs as `room='work'`, `source_kind='hook_stop'` (or `'hook_precompact'`), `tags=['transcript']`. Always exits 0.
- **PostToolUse on `mcp__engine_memory__.*`** invokes [`engine/tools/hooks/post-engine-memory-tool-use.sh`](../tools/hooks/post-engine-memory-tool-use.sh), which appends one JSONL line per MCP call to `engine/session/current_engine_memory.jsonl`. [`engine/tools/scan_engine_memory_activity.py`](../tools/scan_engine_memory_activity.py) reads that JSONL at shutdown step 2, rolls it into the `engine_memory_activity` field on `current.json`, and truncates the JSONL to zero bytes so the next session starts clean.

Both hooks always exit 0 — they are never permitted to block the harness.

## Query patterns

**Boot orchestrator (canonical session-boot surface).** Run `python -m engine.memory.boot_surface` (or use the public functions in `engine.memory.boot_surface` if invoking programmatically). The orchestrator runs three formulations of the next-session work-item phrase (literal / conceptual / adjacent) through `fetch_candidates`, deduplicates, ranks, and writes an idempotent `## Prior context (engine memory)` section into `engine/session/current_plan.md`. The session reads that section before authoring its plan.

**Direct MCP calls.** When you know a specific term to search for, invoke `engine_memory_search` directly. Common shapes:

- `engine_memory_search query="<phrase>"` — broad search across all rooms.
- `engine_memory_search query="<phrase>" room="lessons"` — narrow to a single room.
- `engine_memory_search query="<phrase>" tag_any="adr"` — narrow to drawers carrying any of the given tags.
- `engine_memory_search query="<phrase>" since_days=30` — narrow to drawers filed in the last N days.

**Listing.** `engine_memory_list_drawers room="decisions"` paginates through a room's drawers. `engine_memory_get_drawer id=<uuid>` fetches one drawer plus its lineage rows.

**Diary.** `engine_memory_diary_read agent_name="claude" last_n=3` returns the last 3 reflections in chronological-descending order. `engine_memory_diary_write content="<reflection>" topic="<optional>"` appends one.

## Adoption-check surface (validator soft-warns + hard-fail)

[`engine/tools/validate.py`](../tools/validate.py)'s `validate_engine_memory_adoption()` runs at shutdown step 3 (`--final-check` flag) and reads the `engine_memory_activity` field that `scan_engine_memory_activity.py` populated at step 2:

| Category | Severity | Fires when |
|---|---|---|
| `engine_memory_boot_query_skipped` | soft-warn | `search_calls == 0` |
| `engine_memory_diary_read_skipped` | soft-warn | `diary_read_calls == 0` |
| `engine_memory_diary_write_skipped` | hard-fail (interactive) | `diary_write_calls == 0` AND no `engine_memory_unavailable_acknowledged:` token in `outcome_summary` |
| `engine_memory_diary_write_skipped_routine` | soft-warn (routine) | same predicate, routine mode |
| `engine_memory_diary_write_acknowledged_skip` | soft-warn | token present (hard-fail downgrade) |
| `engine_memory_zero_citations_after_search` | soft-warn | `search_calls > 0` AND no drawer IDs / S-NNNN refs in outcome_summary or commits |

**Escape-hatch token.** `engine_memory_unavailable_acknowledged: <one-line reason>` in `outcome_summary` downgrades the hard-fail to the `_acknowledged_skip` soft-warn. Use for legitimate edge cases: early-exit sessions with nothing meaningful to reflect on, filesystem recovery scenarios. Persistent acknowledged-skips fire the 3-of-5 escalation per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md).

## Backup discipline

`cp engine/.memory/engine_memory.sqlite3 engine/.memory/engine_memory.sqlite3.backup` is the simplest snapshot (works because WAL mode separates the journal from the main file; a copy during a write captures a consistent transactional state at the journal-checkpoint frontier).

For a guaranteed-consistent snapshot under load:

```bash
sqlite3 engine/.memory/engine_memory.sqlite3 "VACUUM INTO 'engine/.memory/engine_memory.sqlite3.backup'"
```

`VACUUM INTO` issues a transactional dump that reflects the database at the moment the command starts; concurrent writes after that point do not affect the backup.

## Recovery procedures

**Corrupt DB.** `PRAGMA integrity_check` on `get_conn()` returns anything other than `'ok'` → the file is damaged. Two options:

1. Restore from the most recent backup (preferred when reflective content is load-bearing).
2. Delete the file and let the next session recreate from migration replay: `rm engine/.memory/engine_memory.sqlite3; python -m engine.memory.migrate_from_mempalace --db-path engine/.memory/engine_memory.sqlite3` (only useful while the source MemPalace palace still exists; post-S-0193 the replay source is gone).

**Stale FTS5 index.** If `SELECT count(*) FROM drawers_fts` diverges from `SELECT count(*) FROM drawers`, rebuild via `INSERT INTO drawers_fts(drawers_fts) VALUES('rebuild');`. The triggers should keep them in sync, but a manual `INSERT OR REPLACE` outside the trigger path can desync.

**Hook log diagnostics.** The Stop/PreCompact hook writes to `.claude/logs/engine-memory-hook.log` (gitignored, per-worktree). Persistent failure lines indicate the venv python isn't resolving, jq is missing, or the substrate is unreachable. Check:

```bash
test -s .claude/logs/engine-memory-hook.log && cat .claude/logs/engine-memory-hook.log
```

Same diagnosis posture as MemPalace's prior hook log.

## See also

- [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) — substrate decision.
- [ADR 0078](../adr/0078-revert-and-rollback-discipline.md) — dual-write capture during the cutover window (retired at S-0193).
- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle that the adoption-check categories feed.
- [`engine-memory-conventions.md`](engine-memory-conventions.md) — room + source_kind + tag conventions for authored drawers.
- [`engine/memory/README.md`](../memory/README.md) — package-level orientation.
