# ADR 0091 — Engine-memory substrate: SQLite + FTS5 (replaces MemPalace; supersedes ADR 0090)

- **Status:** Accepted
- **Date:** 2026-05-16
- **Deciders:** S-0188
- **Supersedes:** [ADR 0090](0090-phase-6-recall-substrate-decision.md)

## Context

[ADR 0090](0090-phase-6-recall-substrate-decision.md) (S-0185) committed to **A1-PROPER**: preserve the MemPalace substrate via comprehensive in-project fix campaign + scheduled maintenance + upstream coordination + empirical investigation. Six commitments. Two sessions executed pieces of the plan:

- **S-0186** executed commitments 1 (empirical re-verification) and 4 (ADR 0079 recurrence investigation). Confirmed all three S-0184 failure modes broken at our 22K-drawer scale; traced HNSW UNKNOWN root cause to rebuild-time `sync_threshold` inheritance defeating chromadb's `_persist()`; restored the palace via prune + retrofit + watchdog against `psycopg.connect()` hang.
- **S-0187** executed commitment 2a's rebuild-tool amendment (in-rebuild `sync_threshold=3` override per [ADR 0079](0079-hnsw-sync-threshold-tuning.md) amendment) plus three coupled in-context fixes (defensive-prune field-name bug; client-side wall-clock query watchdog; chromadb 1.5.x default embedding-fn check). **S-0187 surfaced [Issue #134](https://github.com/StarshipSuperjam/paideia/issues/134) as new evidence ADR 0090 did not have**: the rebuild produces correct on-disk state on a scratch palace (`link_lists.bin=6044+272` bytes; `index_metadata.pickle=80878+6410` bytes), then atomic-swap-into-live triggers immediate destruction within seconds of the first `mempalace_search` MCP invocation. The diagnosis: old MCP server processes (PIDs predating the swap) hold chromadb in-memory state from the old palace and write stale state over the rebuilt files.

**ADR 0090's commitment 2a assumed scheduled rebuilds were sustainable maintenance.** Issue #134 empirically falsifies that assumption at the MCP-server-process-lifecycle layer the ADR did not model. The rebuild is correct at the filesystem layer and broken at the layer that materially matters for ongoing operation.

The cost calculus ADR 0090 deliberated has shifted on two axes:

1. **Maintenance burden grew.** Each rebuild now requires kill-MCP-first orchestration with no upstream-tracked fix; the operational complexity is no longer "~30s rebuild per shutdown" per ADR 0090's pros line — it's "kill all MCP server processes, atomically swap, verify destruction-prevention, restart MCP servers" with no documented contract for the kill-and-restart sequence.
2. **Retrieval-value premise weakened further.** ADR 0090 named the 25/30 `mempalace_zero_citations_after_search` telemetry as a load-bearing premise held loosely (its premise 3); five additional sessions have passed without that telemetry signal moving, and the recall harness commitment in ADR 0090 was not authored as a deliverable. The empirical record now spans 30+ sessions of near-zero citation signal, with one substrate-restoration campaign (S-0186) that briefly restored the search surface but the restoration was destroyed within hours per Issue #134.

The user has read the cross-session-memory thesis ("Cross-session memory for AI coding agents: a thesis for stack-aligned environments" — argument that thin custom layer + Postgres + vector + tsvector beats dedicated agent memory systems for stack-aligned coding-agent workflows under flat-rate subscriptions) and adjudicated three foundational choices via plan-mode AskUserQuestion:

1. **No external embedding model.** The thesis's pgvector+tsvector hybrid was sketched assuming embeddings ride a separate billing surface; the user observed that since Claude is in the loop every session, semantic relevance can be delivered by Claude reading top-K candidates inline at boot rather than by an embedding model's vector reranking. Storage is structured fields + full-text search; intelligence sits inside already-paid session turns.
2. **Export-and-replay** the ~673 curated drawers from the post-S-0186-prune palace (decisions, pushback, lessons, diary surfaces preserved; auto-capture residue dropped at the filter boundary).
3. **Engine-only substrate.** Per the engine/product wall in [ADR 0037](0037-engine-product-wall-and-changelog-rename.md), the substrate cannot live in Paideia's Supabase project. The engine must remain portable — drop it into a different project, it works with minimal revision. The substrate is **SQLite + FTS5, single gitignored file under the engine tree**. Stdlib `sqlite3`, no external services, no per-install DB setup, no API dependency. Cross-device continuity is user-managed (matches MemPalace's actual chromadb behavior).

The thesis's anti-thesis is honored as a binding constraint: a thin custom layer is the right call **if and only if it stays thin**. The Decision and Consequences pre-commit specific scope guardrails to prevent the substrate from growing into the failure mode the anti-thesis names ("the maintenance burden of a custom layer may exceed the friction of working around dedicated systems' limitations").

### Load-bearing premises

Per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md). This ADR triggers extraction step under three of the four trigger classes simultaneously: (2) supersession of a load-bearing prior decision; (3) posture-to-machinery conversion (ADR 0090 was posture-with-some-machinery; this ADR commits code); (4) contract-shape change (the MCP tool surface contract narrows from ~19 mempalace tools to exactly 6; the validate.py soft-warn catalog gains 3 and loses 9).

1. **Vector retrieval has been ceremonial, not load-bearing.** FTS5 + BM25 + Claude reading top-K candidates inline delivers equivalent or better cite-worthy recall for the ~1K-drawer engine corpus. *Falsifier:* a session within 10 post-cutover sessions cites ≥3 retrieved drawer IDs that genuinely required cross-vocabulary semantic match (not lexical overlap) that FTS5 missed. *Test status — empirically supported in advance:* `mempalace_zero_citations_after_search` has fired 25/30 sessions per S-0184 audit; 30+ sessions of zero-citation telemetry. The S-0191 verification harness produces the t=0 measurement against historical zero-citation queries + 10 fresh queries.

2. **Rebuild discipline is unsustainable at the MCP-server-open layer.** *Falsifier:* a kill-MCP-first + atomic-swap sequence preserves rebuilt state across 5 consecutive rebuilds without re-destruction. *Test status — not yet tested in repaired form:* Issue #134 surfaced this in S-0187. Even if a kill-MCP orchestration fix works, it adds operational complexity for a substrate empirically delivering low retrieval value (premise 1). The premise is held with the observation that, conditional on premise 1, additional rebuild engineering is paying off a sunk-cost rather than securing future value.

3. **The thin-layer discipline can be held against scope creep.** *Falsifier:* by S-0193 close — `engine/memory/` substantive code (excluding tests) exceeds 900 LOC, OR the MCP server exposes >6 tools, OR any of {contradiction resolution, autonomous decay/recency rebalancing, KG synthesis from drawers, LLM-in-the-loop content summarization} ships. *Test status:* procedural premise held by named out-of-scope commitments in the Decision section and the sunset criterion in Consequences. The 900-LOC budget accommodates the transcript-mining hook (~200 LOC) on top of substrate core (~600 LOC) + verify-harness (~100 LOC) while still constraining scope.

4. **Upstream MemPalace will not converge on Issue #134's fix class within 30 sessions.** *Falsifier:* upstream lands an MCP-server-lifecycle fix that preserves rebuilt state across MCP server lifetimes within 30 sessions. *Test status — unverifiable in-context.* The asymmetric bet: even if upstream lands the fix, the new substrate has zero coupling to mempalace's release cadence; we lose nothing by being early. Conversely, if Issue #134 is a multi-quarter fix, the project saves substantial wait-time.

5. **SQLite + FTS5 + stdlib `sqlite3` is operationally reliable for hook-driven writes from a single-writer engine session.** *Falsifier:* hook write failures exceed 2 sessions across the 30-session window post-cutover, OR `SQLITE_BUSY` fires under normal single-session use. *Test status — partially testable now:* SQLite single-writer is well-characterized; the engine session model is single-writer by construction (one Claude Code instance per repo at a time, enforced by the eager-claim ritual + concurrent-session collision check per [ADR 0082](0082-routine-boot-freshness-and-concurrency-defense.md)). WAL mode + `PRAGMA busy_timeout=5000` handles the transient overlap between hooks and the MCP server. Concurrent worktrees on the same repo resolve to the same shared file via `git rev-parse --show-toplevel`; the eager-claim race protection already covers the concurrency surface.

6. **The engine/product wall holds.** Engine-memory storage stays inside the engine tree and has zero schema/data coupling to Paideia's product database. *Falsifier:* a future session needs to JOIN engine-memory and product-graph data in the same query, OR engine-memory tables appear in `paideia-dev`. *Test status:* architectural premise held by file-location discipline (`engine/.memory/engine_memory.sqlite3`) + the SQLite-not-Postgres substrate choice. The portability smoke test in Consequences verifies this empirically by copying `engine/` into a scratch project unrelated to Paideia.

## Decision

The project replaces **MemPalace** as the engine memory substrate with a **thin SQLite + FTS5 implementation owned entirely by the engine**. The substrate stores curated drawers (decisions, pushback, lessons, exploration, operations, work, general) plus diary entries in a single gitignored SQLite file at `engine/.memory/engine_memory.sqlite3`; retrieval is FTS5 + BM25 + recency + tag-class boost; semantic relevance is delivered by Claude reading top-K candidates surfaced inline at session boot. No embedding model. No external API dependency. No coupling to Paideia's product database. The substrate decision commits to **seven specific shapes**:

1. **Engine/product wall preservation.** Engine memory lives entirely under `engine/.memory/` and `engine/memory/`. Uses no Supabase URLs, no `psycopg`, no PostgreSQL-specific anything. Has no FK or schema relationship to `paideia-dev` tables. Ships as part of `engine/`; copying `engine/` to another project carries the substrate code; the data file regenerates empty on first use at the new location. Per [ADR 0037](0037-engine-product-wall-and-changelog-rename.md).

2. **SQLite + FTS5 storage.** Five regular tables (`drawers`, `diary`, `lineage`, `capture_state`, `query_log`) + one FTS5 virtual table (`drawers_fts`) + a `schema_version` table. Schema created idempotently by `engine/memory/schema.py` on first connect via `CREATE … IF NOT EXISTS` + `INSERT OR IGNORE`. No migration discipline file, no `apply_migration.py` extension. WAL journal mode + `PRAGMA foreign_keys = ON` + `PRAGMA busy_timeout = 5000`. File location overridable via `ENGINE_MEMORY_PATH` env var (else resolves via `git rev-parse --show-toplevel`).

3. **Retrieval contract — two stages.** Stage 1 (SQL, inside `engine_memory_search`): FTS5 `MATCH` filter + room/tag/since-days predicates + composite rank (`-bm25` + recency-decay over 30-day half-life + room-filter boost + tag-any boost + tag-class boost for decision/pushback/lesson), top 30 candidates. Stage 2 (inline, free under subscription): the boot orchestrator (`engine/memory/boot_surface.py`) writes the top 8 candidates inline into `engine/session/current_plan.md` under `## Prior context (engine memory)`; Claude reads them as part of plan authoring. No sub-agent rerank. No extra LLM round-trip.

4. **Capture shape — three surfaces separated by `room`.**
   - **`room='work'` — hook-driven transcript capture.** Stop and PreCompact hooks invoke `engine/memory/capture.py` (which wraps `transcript_capture.py`, ~200 LOC vendored simplification of mempalace's hook chain). Reads transcript JSONL via hook env vars, extracts messages since last save, light noise-stripping for huge tool results, INSERTs as `source_kind='hook_stop'`/`'hook_precompact'` with `tags=['transcript']`. This preserves the "you don't know what you'll need to know before you need to know it" affordance that was MemPalace's load-bearing value when working.
   - **`room IN ('decisions','pushback','lessons','exploration','operations')` — Claude-authored curated drawers.** Deliberate `engine_memory_add_drawer` calls in-session.
   - **`diary` table — per-session reflection.** One `engine_memory_diary_write` per session at close. Mechanically enforced via `engine_memory_diary_write_skipped` soft-warn (hard-fail with escape-hatch token, per ADR 0056's pattern).

5. **MCP surface — exactly six tools.** `engine_memory_search`, `engine_memory_add_drawer`, `engine_memory_get_drawer`, `engine_memory_list_drawers`, `engine_memory_diary_read`, `engine_memory_diary_write`. **Pre-committed as the surface ceiling.** Adding a seventh tool requires a new ADR superseding or amending this one. The list_rooms / list_wings / status / find_tunnels / KG / tunnels / AAAK families from mempalace's ~19-tool surface all retire.

6. **Wing concept retired.** Drawers carry `room` + `tags[]`; no `wing` column. The wing model was a multi-project affordance MemPalace shipped that this project never used (single Paideia install); the per-worktree wing scatter that motivated 21,893 prune operations at S-0186 is structurally precluded by the schema. Wing identity is preserved only in `lineage.source_wing` for forensic traceability of migrated drawers (queryable but not a retrieval routing key).

7. **File location + gitignored discipline.** `engine/.memory/engine_memory.sqlite3` gitignored. Cross-device continuity is user-managed (matches MemPalace's actual chromadb behavior — the project never had built-in cross-device sync). Backup is `cp` or `VACUUM INTO 'backup.sqlite3'` for a consistent snapshot.

## Alternatives Considered

Per [ADR 0077](0077-adr-template-alternatives-considered-section.md). Five alternatives evaluated.

### A1-PROPER — Hold the line per ADR 0090

- **What:** Continue executing ADR 0090's commitments. Fix Issue #134 via kill-MCP-first orchestration in `mempalace_rebuild_hnsw.py`; continue scheduled rebuilds + Mode 3 prunes + upstream coordination across the 5+ open mempalace issues/PRs. Mempalace stays the substrate.
- **Pros:** Preserves existing tooling investment (S-0093 boot orchestrator, S-0078 rebuild tool, S-0163 audit telemetry, ADR 0056 mechanical adoption checks, ADR 0057 element 4 cluster-reading workflow). ADR 0090's six commitments hold without supersession. Continues upstream coordination posture per ADR 0090 commitment 3.
- **Cons:** Issue #134 is the third MCP-server-process-lifecycle bug class to surface in 4 sessions (S-0184 HNSW UNKNOWN; S-0186 chromadb 1.5.x default name; S-0187 MCP-open destroys swap); the substrate's failure surface is wider than ADR 0090 modeled. The 25/30 zero-citation telemetry has stood through one substrate-restoration campaign without moving. Maintenance burden in ADR 0090's pros line ("~30s rebuild per shutdown") no longer holds — the kill-MCP-first orchestration is operational complexity ADR 0090 did not deliberate. The asymmetry: even if upstream lands all 5 pending fixes within 60 sessions, the project's tooling continues paying chromadb-substrate-specific maintenance cost that an in-stack SQLite substrate avoids entirely.
- **Rejected because:** the cost calculus ADR 0090 used has shifted with Issue #134 + 5 more sessions of zero-citation telemetry. Sticking with A1-PROPER means continuing to pay for a substrate empirically delivering low retrieval value while the failure surface grows.

### A4 — Postgres + pgvector in Paideia's Supabase project

- **What:** Author migration `0068_engine_memory_*.sql` in `product/seed-graph/migrations/`. Create `engine_memory_*` tables in `public` schema of `paideia-dev`. Use pgvector (extending [ADR 0086](../../product/adr/0086-model-agnostic-embedding-storage-architecture.md) per-dim partition pattern) OR `tsvector` alone for memory retrieval. MCP server connects via session-pool URL.
- **Pros:** The thesis's recommended architecture explicitly. Phase 6 partition machinery can be reused once it lands. Better tooling for SQL debugging (`psql`, Supabase dashboard). Network-replicated by default (Supabase managed); cross-device built-in.
- **Cons:** **Violates the engine/product wall per ADR 0037.** Engine memory in `paideia-dev` means: the engine cannot be dropped into another project without spinning up that project's own Supabase + reconfiguring; engine schema lives in product migrations directory; engine writes touch the product database. Issue #135 (pgbouncer transaction-pool strips options=-c) bites every connection. Setup overhead per install (env vars, credentials, RLS posture). Couples engine release cadence to product schema evolution. The portability principle ADR 0037 codifies is foundational to the project's "engine is an extractable harness" trajectory.
- **Rejected because:** wall violation. The engine must work standalone in any project that adopts the harness; coupling it to one project's database fails that test architecturally. The thesis's "stack-aligned" framing applies to *the engine's* stack (Python + git + markdown + hooks + MCP), not to whatever product database the engine happens to sit alongside.

### A5 — Pivot to Mem0 / Letta / dedicated managed memory system

- **What:** Adopt a third-party agent memory platform as the substrate (Mem0's managed tier, Zep, Letta's MemFS). Migrate via their import APIs. Drop the project-owned mempalace-replacement work.
- **Pros:** Outsources memory-company-building. Mature retrieval shapes (Mem0's multi-signal hybrid, Letta's MemFS with reflection). Dashboards, analytics, webhooks out of the box. Active product development.
- **Cons:** The user's thesis-document constraint explicitly names "don't rebuild a memory company inside the repo." A5 doesn't rebuild it but does adopt one as a dependency, with API cost (Mem0 Pro ~$250/mo; Zep Flex $125/mo), vendor lock-in, AND the same MCP-server-process-lifecycle class of bugs at a different vendor's surface. Wall violation: vendor-dependency replaces in-stack substrate. Adds an external API dependency on every read/write. Couples engine cadence to vendor SLA.
- **Rejected because:** heavier external coupling than A1-PROPER without proportional retrieval-quality benefit for a ~1K-drawer corpus. The thesis's anti-thesis explicitly warned against this shape ("the misalignment is large enough that the better engineering decision in such environments is to build on existing infrastructure rather than adopt a dedicated system whose feature surface is engineered for problems the environment does not have").

### A6 — git-grep only, no DB substrate

- **What:** Retire substrate entirely. ADR content recall lives in `git grep engine/adr/*.md`; decision-drawer / pushback / lesson content recall retires; diary writes go to a flat markdown file per session under `engine/diary/S-NNNN.md`.
- **Pros:** Zero infrastructure. Maximum portability (git is universal). No DB to maintain. Minimum thin.
- **Cons:** **Capture surface retires too aggressively.** S-0187 cited diary content; the capture+search affordance was load-bearing for that. Retiring transcript capture removes the "didn't know I'd need it" value the user explicitly named as preservation-required. Auto-capture to markdown files would explode git history with binary-ish blobs; gitignored markdown files lose the portability A6 promised.
- **Rejected because:** capture + retrieval are load-bearing per the empirical record; retiring both is over-aggressive. A6 is too thin; SQLite + FTS5 is the thinnest viable position that preserves capture and search.

### A7 — SQLite + FTS5 engine-owned substrate (chosen)

- **What:** Per the seven Decision commitments above.
- **Pros:** Holds the engine/product wall. Stdlib `sqlite3` driver — no new external deps (mempalace + chromadb removed; nothing added). Single gitignored file — portable, easy to backup, easy to drop into a new project. FTS5 + BM25 is a mature, well-documented full-text search stack. WAL mode handles the single-writer concurrency the engine session model already enforces. Preserves transcript-capture affordance via `room='work'` + `tags=['transcript']`. Preserves curated-drawer + diary surfaces. Six-tool MCP ceiling commits to the thin-layer discipline up front. Zero coupling to mempalace release cadence — the new substrate's stability is decoupled from upstream MemPalace's stability.
- **Cons:** Cross-device sync is user-managed (gitignored file). The transcript-capture script vendors ~200 LOC that mempalace previously absorbed; the project owns this surface area going forward. SQLite math functions (`exp` for recency decay) may need a Python fallback for SQLite builds without math compiled in (one-line `conn.create_function`).
- **Rejected because:** not rejected — chosen.

## Consequences

### In this session (S-0188)

- ADR 0091 (this file) lands at `Accepted`.
- ADR 0090 (`engine/adr/0090-phase-6-recall-substrate-decision.md`) Status flips to `Superseded by ADR 0091`. Body untouched per status-conventions one-directional pointer rule. Cascade See-also entry added.
- ADR 0056 (`engine/adr/0056-mempalace-mechanical-adoption-checks.md`) Status flips to `Superseded by ADR 0091` — the 9 mechanical adoption checks retire with the substrate.
- ADR 0079 (`engine/adr/0079-hnsw-sync-threshold-tuning.md`) Status flips to `Superseded by ADR 0091` — HNSW retires with chromadb.
- ADR 0057 (`engine/adr/0057-adversarial-stance-for-health-check-audits.md`) gains an in-body amendment: element 4 (the MemPalace cluster-reading workflow) is marked substrate-coupled and retired; the broader adversarial-stance posture remains Accepted.
- ADRs 0045, 0050, 0080, 0037 gain See-also amendments pointing forward to ADR 0091.
- First-exercise readiness note at [`engine/build_readiness/engine_memory_substrate_first_exercise.md`](../build_readiness/engine_memory_substrate_first_exercise.md) per [ADR 0053](0053-mechanism-first-exercise-gate.md). Trigger criterion #4 fires (Consequences span ≥5 surfaces: ADR 0091 + 5 cascade ADRs + ops docs + 3 skills + ~6 tools + 1 new package directory ≫ 5).
- `.gitignore` adds `engine/.memory/`.
- [Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138) opens with the 5-session implementation roadmap (S-0189 through S-0193) as the body.
- [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) closes with comment naming ADR 0091 supersession.
- STATE.md ADR count 90 → 91; last-session row rotates to S-0188; next-session work item names S-0189 (schema migration + foundations package).
- ENGINE_LOG.md `[Unreleased]` Added entry naming ADR 0091 + the cascade.
- MemPalace `decision`-tagged drawer (one final use of the old surface) captures the supersession reasoning. The S-0192 export-and-replay carries it forward into the new substrate.

### S-0189 deliverable (schema + foundations package)

- New package `engine/memory/` with `__init__.py`, `schema.py` (the full SQL above as Python string constants applied idempotently), `connection.py` (stdlib `sqlite3.connect()` wrapped with WAL mode + `PRAGMA foreign_keys=ON` + `busy_timeout=5000` + `exp` function registration fallback + path resolution via `ENGINE_MEMORY_PATH` or git rev-parse), `mcp_server.py` skeleton (MCP boilerplate; tools wired in S-0190/S-0191).
- README at `engine/memory/README.md` naming the substrate, the six-tool ceiling, the file location, the cross-device sync caveat.
- `engine/.memory/.gitkeep` so the data directory exists on a fresh clone; the SQLite file itself is created on first connect.
- Tests `engine/memory/test_connection.py` + `test_schema.py` using `:memory:` SQLite for isolation; verify schema applies idempotently across repeat connects.
- `apply_migration.py` is **not** modified — engine memory does not use the Postgres migration discipline. Schema is in-code, applied at first connect.

### S-0190 deliverable (capture surface + dual-write)

- `engine/memory/transcript_capture.py` (~200 LOC) — Stop/PreCompact handler. Reads transcript JSONL via Claude Code hook env vars (the same surface mempalace's `hooks_cli.py` consumes). Extracts messages since `capture_state.last_stop_save_at`. For Stop: single chunk per fire, `source_kind='hook_stop'`. For PreCompact: comprehensive chunk covering everything since last save, `source_kind='hook_precompact'`. Both go to `room='work'`, `tags=['transcript']`. Splits into multiple drawers if content exceeds 50KB. Strips obvious noise (long tool results >10KB get summarized to first/last 500 chars + length marker). Updates `capture_state.last_stop_save_at` on success. Idempotent against re-fire.
- `engine/memory/capture.py` (~50 LOC) — thin wrapper invoked from the new hook script; routes Stop/PreCompact to `transcript_capture`.
- `engine/memory/diary.py` (~80 LOC) — diary read/write.
- `engine_memory_add_drawer` + `engine_memory_diary_write` MCP tools wired.
- New hook script `engine/tools/hooks/engine-memory-capture.sh` (~40 LOC) — thin shim: scrubs env (per ADR 0045/0050), resolves venv python, invokes `python -m engine.memory.capture {stop,precompact}`, exits 0 always (capture failures are soft per `engine_memory_capture_failure` soft-warn).
- `.claude/settings.json` updated: Stop and PreCompact hooks invoke BOTH `mempalace-hook-wrapper.sh` AND `engine-memory-capture.sh` (parallel-write per [ADR 0078](0078-revert-and-rollback-discipline.md) safety posture).
- Tests with synthetic transcript JSONL fixtures.
- 3 Skill bodies (session-shutdown-sequence + Layer-1 ops doc) add new tool name as option alongside old; cutover to exclusive-new at S-0192.

### S-0191 deliverable (read surface + verification harness + cutover gate)

- `engine/memory/boot_surface.py` — successor to `engine/tools/mempalace_boot_search.py`. Three-formulation pattern preserved. Runs the FTS5 query (above). Writes idempotent `## Prior context (engine memory)` section to `engine/session/current_plan.md` with top-8 candidates surfaced inline.
- `engine_memory_search` + `engine_memory_get_drawer` + `engine_memory_list_drawers` MCP tools wired. Total tool surface: 6 (matches the pre-committed ceiling).
- `engine/tools/validate.py` adds `engine_memory_zero_citations_after_search` soft-warn (mirrors mempalace_ predecessor; both fire during cutover window).
- `engine/memory/verify_recall.py` + `engine/docs/audits/engine_memory_recall_S-0191.md` — harness runs the 25 historical zero-citation queries (extracted from S-0184–S-0187 archive `outcome_summary.boot_search_results`) + 10 fresh ADR-pushback / lesson-recall / decision-drawer / diary-cross-reference / Issue-history queries against BOTH substrates; produces side-by-side comparison report.
- **Cutover gate.** If the new substrate's cite-worthy rate is materially worse than MemPalace's on the comparison set, S-0191 HALTS and reopens ADR 0091 in S-0192 — does NOT proceed to cutover. Otherwise: `verification_passed: true` written into Issue #138 comment thread; S-0192 proceeds.

### S-0192 deliverable (migration replay + MCP swap + skill/CLAUDE.md rewire)

- `engine/memory/migrate_from_mempalace.py` — export-and-replay. Source: `mempalace_list_drawers --json` per wing. Filters to curated rooms. INSERTs into `drawers` + `lineage` tables with `lineage.source='mempalace_replay_S-0192'`. Diary entries from `wing_claude` import to `diary` table (AAAK-decompressed). Idempotent. Verification step asserts row count, per-room counts, spot-checks 5 curated decision drawers, FTS5 count = drawers count.
- `.mcp.json` swap: replace `mempalace` MCP server entry with `engine_memory` (command points at `engine/memory/mcp_server.py` via venv python).
- `CLAUDE.md` startup ceremony step 3 rewires from `mempalace_search` to `engine_memory_search`. Two-layer-decision-recording line updates ("ADRs are contract; `engine_memory` drawers are story"). ADR 0056 reference in "posture vs machinery" examples removes.
- 3 Skills + their 3 Layer-1 ops docs rewire in lockstep (per [ADR 0089](0089-skill-layer1-parity-validator-check.md) parity).
- PostToolUse `mcp__mempalace__.*` hook removed from `.claude/settings.json`. Capture-side dual-write resolves to single-write to the new substrate.
- New ops docs `engine/operations/engine-memory-operations.md` + `engine/operations/engine-memory-conventions.md` authored from scratch.

### S-0193 deliverable (removal + final cleanup + cascade audit)

- Delete 11 `engine/tools/mempalace_*.py` + their tests; delete `engine/tools/probe_palace.py`; delete `engine/tools/hooks/mempalace-hook-wrapper.sh` + `post-mempalace-tool-use.sh`; delete `engine/operations/mempalace-operations.md` + `mempalace-tagging-conventions.md`.
- `pyproject.toml` removes `mempalace>=3.3.5` + `chromadb>=1.5.9`. `uv lock` regen. No new deps added — `sqlite3` is stdlib.
- `validate.py` retires 9 `mempalace_*` soft-warns; adds 3 `engine_memory_*` (zero_citations_after_search, diary_write_skipped, capture_failure); renames `_check_mempalace_substrate_alive` → `_check_engine_memory_substrate_alive`.
- `scan_mempalace_activity.py` retools → `scan_engine_memory_activity.py` (sources from `query_log` SQL view, not JSONL).
- `scan_mempalace_citations.py` retools to SQL against the new substrate.
- `audit_mempalace_attribution.py` retools as SQL join over `lineage` + `drawers`.
- Issues closed (commit message `closes #1 #2 #134 #135 #136 #137 — superseded by ADR 0091`).
- Issue #138 closes with cascade-audit confirmation.
- **Cascade audit verification:** `git grep -i mempalace` produces zero matches outside `engine/ENGINE_LOG.md` history + 3 superseded ADRs (0090, 0056, 0079) which retain their body content.

### Cross-session consequences

- **Issues #1, #2, #134, #135, #136, #137** all close at S-0193 (superseded by ADR 0091; substrate decoupling makes the upstream mempalace coordination moot for our use).
- **Upstream MemPalace coordination posture (ADR 0090 commitment 3) retires.** No further upstream contributions planned. The project's relationship to MemPalace becomes pure substrate-replacement, not bridge-and-coordinate.
- **The `mempalace_zero_citations_after_search` baseline annotation** retires from the persistent-warn surface at S-0193; replaced by `engine_memory_zero_citations_after_search` with no baseline annotation (the new substrate's signal is fresh data, not legacy annotation).
- **Phase 6 partition machinery** (ADRs 0086 / 0087 / 0088) remains scheduled as planned. Phase 6's `node_embeddings_<dim>` work is for per-user product content embeddings, completely independent of engine memory. The "memory substrate first, Phase 6 rides on it" sequencing surfaced by ADR 0090 commitment 6 still holds, but with looser coupling than ADR 0090 modeled — they share Postgres-the-product-DB but not pgvector partition machinery (engine memory has no embeddings).

### Out-of-scope pre-commits (the "stay thin" guardrails)

Adding any of the following requires a new ADR superseding or amending ADR 0091:

- Contradiction resolution between drawers (no `engine_memory_reconcile` tool; Claude's job at read time)
- Autonomous decay or recency rebalancing beyond `bm25` + recency boost
- Knowledge-graph synthesis from drawers (ADRs + cross-reference files remain the graph layer)
- Cross-drawer summarization (LLM-in-the-loop content rewriting)
- Multi-project wings
- Embedding-model integration of any kind (local or API)
- **Postgres/pgvector reuse** — even though `paideia-dev` runs Postgres and Phase 6 will enable pgvector, the engine substrate stays in SQLite for portability
- **Auto-capture routing to any room other than `'work'`** — defense against the S-0186 pollution shape. Transcript chunks always land in `room='work'`; curated rooms remain Claude-authored only.
- Tool surface beyond the 6-tool ceiling
- Cross-device sync mechanisms (Litestream, etc.) — additive future change if needed; not in scope for the initial cutover

### Named re-evaluation triggers

A new ADR re-deliberates if by S-0193 + 30 sessions any of:

- `engine_memory_zero_citations_after_search` exceeds 60% firing rate sustained.
- Two consecutive health-check audits surface substrate findings.
- `engine/memory/` substantive code (excluding tests) exceeds 900 LOC.
- The MCP server exposes >6 tools.

### Sunset criterion

If three consecutive health-check audits (S-0203, S-0223, S-0243 at cadence-20) report no substrate findings AND the `engine_memory_*` MCP surface stays at exactly six tools AND `engine/memory/` substantive code stays under 900 LOC, ADR 0091 transitions from active-rollout to steady-state observation. The audit-cadence health check at S-0243 considers retiring this ADR's named re-evaluation triggers at that point.

## See also

- [ADR 0090](0090-phase-6-recall-substrate-decision.md) — superseded; its commitments 1, 2a (partial), 4 were executed at S-0186/S-0187 and the empirical findings (Issue #134) inform this supersession.
- [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) — superseded; 9 mechanical adoption checks retire with the substrate.
- [ADR 0079](0079-hnsw-sync-threshold-tuning.md) — superseded; HNSW persist concerns retire with chromadb.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — amended; element 4 cluster-reading workflow retires with substrate; rest of the adversarial-stance posture stays Accepted.
- [ADR 0045](0045-shared-state-integrity-discipline.md) — amended; `probe_palace.py` retires; SQLite WAL is the new durability story.
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — amended; mempalace CLI no longer needed in PATH.
- [ADR 0080](0080-boot-time-dependency-visibility.md) — amended; mempalace + chromadb lines retire from version-visibility surface.
- [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) — the wall this ADR holds; ADR 0091 is the substrate-decision instance that empirically tests the wall principle.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — the extraction-step rule this ADR dogfoods via the Load-bearing premises subsection.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — the Alternatives Considered template this ADR dogfoods with 5 alternatives.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this ADR's first-exercise note covers it.
- [ADR 0078](0078-revert-and-rollback-discipline.md) — the dual-write safety posture S-0190 → S-0192 follows.
- [ADR 0089](0089-skill-layer1-parity-validator-check.md) — Skill ↔ Layer-1 parity that S-0192's lockstep skill rewire respects.
- [`engine/build_readiness/engine_memory_substrate_first_exercise.md`](../build_readiness/engine_memory_substrate_first_exercise.md) — first-exercise readiness note.
- [`~/.claude/plans/mempalace-overhead-is-dragging-twinkly-harp.md`](~/.claude/plans/mempalace-overhead-is-dragging-twinkly-harp.md) — the approved plan for the 6-session rollout S-0188 → S-0193.
- [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) — closes at S-0188 (the substrate-decision Issue ADR 0090 originally closed; reopens conceptually + closes again per supersession).
- [Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138) — opens at S-0188 (tracking issue for the 5-session cutover).
- [Issue #134](https://github.com/StarshipSuperjam/paideia/issues/134) — the critical S-0187 finding (MCP-server-open destroys rebuild) that empirically falsified ADR 0090 commitment 2a; closes at S-0193.
- Upstream MemPalace coordination retires: [#1082](https://github.com/MemPalace/mempalace/issues/1082), [#1398](https://github.com/MemPalace/mempalace/issues/1398), [#1489](https://github.com/MemPalace/mempalace/issues/1489), PRs [#1463](https://github.com/MemPalace/mempalace/issues/1463), [#1511](https://github.com/MemPalace/mempalace/issues/1511), [#1452](https://github.com/MemPalace/mempalace/issues/1452) — the project no longer tracks these; whichever way upstream evolves, the new substrate is decoupled.
