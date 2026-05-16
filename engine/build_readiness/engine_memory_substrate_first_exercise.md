# engine_memory substrate (SQLite + FTS5) — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) criterion-4 evaluation (Consequences span ≥3 ops docs OR ≥5 tooling files): satisfied via 1 new ADR (0091) + 5 cascade ADRs (0090/0056/0079/0057 amend + 0045/0050/0080/0037 See-also) + ~9 tooling files (`engine/memory/{schema,connection,mcp_server,capture,transcript_capture,diary,boot_surface,verify_recall,migrate_from_mempalace}.py`) + 1 hook script (`engine-memory-capture.sh`) + 2 new ops docs (`engine-memory-operations.md`, `engine-memory-conventions.md`) + 3 Skill SKILL.md edits + 3 Layer-1 ops doc edits + `.claude/settings.json` + `.mcp.json` + this readiness note = 25+ surfaces total. Readiness note required.
>
> This mechanism is the substrate replacement itself. Tier 1 criteria distribute across the 5 implementation sessions (S-0189 through S-0193) per the approved 6-session rollout plan at `~/.claude/plans/mempalace-overhead-is-dragging-twinkly-harp.md`. Tier 2 + Tier 3 criteria close post-cutover.

## Tier 1 — close at named deliverable sessions (closes between S-0189 and S-0193)

Five Tier 1 criteria, one per implementation session:

- **T1-A — schema applies idempotently from stdlib `sqlite3`.** Closes at **S-0189**. Criterion: `python -c "from engine.memory.connection import get_conn; conn = get_conn(); conn.execute('SELECT 1'); conn.execute('PRAGMA integrity_check')"` against a fresh empty `engine/.memory/` produces `'ok'` and creates the file with all six tables + the FTS5 virtual table + all triggers; a second invocation against the now-populated file produces identical state (idempotency); `engine/memory/test_schema.py` exercises `:memory:` reapply + asserts no `CREATE TABLE` errors. Recorded in S-0189's `outcome_summary` AND updated here at S-0189 close.

- **T1-B — capture surface writes a `room='work'` drawer from the Stop hook.** Closes at **S-0190** (or first post-S-0190 session that fires Stop hook). Criterion: after S-0190 cutover wiring lands, the Stop hook fires on session close; `transcript_capture.py` reads the transcript JSONL via Claude Code hook env vars; INSERTs a drawer with `source_kind='hook_stop'`, `room='work'`, `tags=['transcript']`; `SELECT count(*) FROM drawers WHERE source_kind='hook_stop' AND session_id='S-019X'` returns ≥1. Recorded in S-0190's `outcome_summary` AND updated here at close. **Forward-pointer Tier 2:** if hook env vars don't resolve the transcript path, soft-warn `engine_memory_capture_transcript_path_missing` fires and Tier 1 reopens for diagnosis.

- **T1-C — read surface returns candidates and matches user-relevant queries.** Closes at **S-0191** via the verification harness. Criterion: `engine/memory/verify_recall.py` runs the 25 historical zero-citation queries (extracted from S-0184–S-0187 archive `outcome_summary.boot_search_results`) + 10 fresh queries against BOTH substrates; produces side-by-side comparison report at `engine/docs/audits/engine_memory_recall_S-0191.md`; the new substrate's cite-worthy rate is at least as good as MemPalace's. **Cutover gate fires here.** If the new substrate is materially worse, S-0191 HALTS, the cutover is paused, and ADR 0091 reopens in S-0192. Otherwise: comment `verification_passed: true` lands on Issue #138 and S-0192 proceeds.

- **T1-D — migration replay completes idempotently.** Closes at **S-0192**. Criterion: `engine/memory/migrate_from_mempalace.py` exports the ~673 curated drawers + diary from the post-S-0186-prune palace; INSERTs into `engine_memory` substrate; verification asserts row counts match export, per-room counts match, 5 spot-check decision drawers match content, FTS5 count = drawers count. Idempotent rerun is also tested (`INSERT OR IGNORE` on lineage composite PK). Recorded in S-0192's `outcome_summary`.

- **T1-E — removal completes without dangling references.** Closes at **S-0193**. Criterion: `git grep -i mempalace` at S-0193 close returns zero matches outside `engine/ENGINE_LOG.md` (historical narrative) and the 3 superseded ADRs (0090, 0056, 0079 — which retain their body content per status-conventions one-directional pointer rule). All 11 `engine/tools/mempalace_*.py` + `probe_palace.py` + 2 hook scripts + 2 ops docs deleted; `pyproject.toml` no longer pins `mempalace` or `chromadb`; `uv lock` is regenerated; `validate.py` retires 9 `mempalace_*` soft-warns and adds 3 `engine_memory_*` replacements.

**Tier 1 closeout evidence:** populated in "Empirical record" section below as each session closes. If any T1-A through T1-D criterion fails to close at its named session, the readiness note documents the gap and the next session picks up.

## Tier 2 — close in next natural occasions (post-S-0193 cutover)

- **Recall signal moves.** First 10 sessions post-S-0193 where `engine_memory_zero_citations_after_search` fires <30% (the new substrate's recall delivers cite-worthy content; vs the 25/30 = 83% MemPalace baseline). Target: ≤3/10. Records the cite count per session in `outcome_summary` so the audit-cadence health check can measure the trend.

- **First non-trivial boot citation.** First session post-S-0193 where Claude reads a candidate surfaced inline in `current_plan.md`'s `## Prior context (engine memory)` block AND cites the drawer ID in `outcome_summary`. This is the empirical confirmation that the Stage-2 in-context read pattern produces signal the substrate-level vector retrieval was not producing.

- **First multi-session `room='work'` retrieval.** First session post-S-0193 where boot search finds a transcript drawer authored in a prior session AND that surface materially shapes plan authoring. This validates the "didn't know I'd need it" affordance the user named as load-bearing during the plan deliberation.

- **First `SQLITE_BUSY` encounter (if any).** If concurrent worktree sessions or hook + MCP overlap produces `database is locked`, the `busy_timeout=5000` ms wait should resolve it transparently. If not, retry-with-backoff in `connection.py` is the next mitigation. Record the encounter; one bounded-recover incident is fine; recurrence requires diagnosis.

- **First migration of `engine/` to another project.** Per the portability premise (P6). The substrate's portability is empirically tested when someone (the user, or a future contributor) copies `engine/` into a non-Paideia project, runs the boot-time substrate probe, and observes the SQLite file regenerates empty + the MCP server loads + the boot orchestrator succeeds. Records the test outcome (success ⇒ wall verified; failure ⇒ wall premise reopens for amendment).

## Tier 3 — defer indefinitely (recorded for future audit)

- **30-session window readiness review.** At S-0193 + 30 sessions (i.e., S-0223 cadence-fired audit), the audit revisits:
  - Cumulative `engine_memory_zero_citations_after_search` fire rate (named re-evaluation trigger fires at >60%).
  - Sessions of substrate-coupled work since cutover (named trigger fires at >2; per ADR 0091 named re-evaluation triggers).
  - `engine/memory/` substantive code LOC (named trigger fires at >900 LOC; per ADR 0091 P3).
  - MCP tool count (named trigger fires at >6; per ADR 0091 Decision commitment 5).
  - SQLite file size (informational; if >100MB the auto-capture cadence needs review).

- **Sunset criterion evaluation at S-0243.** Per ADR 0091 sunset criterion: three consecutive clean audits (S-0203, S-0223, S-0243 at cadence-20) + tool ceiling held + LOC under 900 transitions ADR 0091 from active-rollout to steady-state observation. The S-0243 audit considers whether the named re-evaluation triggers can retire.

- **Performance budget.** FTS5 query latency on ~1K-drawer corpus is typically sub-10ms; the boot orchestrator's three-formulation pattern produces ~30ms of total query time. Re-audit if the corpus exceeds 10K drawers OR if boot retrieval becomes a felt latency surface.

- **Cross-device sync mechanism.** Per ADR 0091 out-of-scope pre-commits: Litestream-style replication is an additive future change not in initial scope. Trigger: user reports cross-device-sync as a load-bearing gap (e.g., a session boots without diary entries authored on another machine within the prior 24h).

- **Transcript content sensitivity audit.** Per ADR 0091 risk #10. If transcripts captured into `room='work'` accumulate sensitive content (local paths, env-var snapshots, secrets from file reads), a deny-list-driven redaction pass in `transcript_capture.py` is the next mitigation. Trigger: any session surfaces a sensitive-content concern OR the user requests redaction.

## Empirical record

### S-0188 (the ADR-authoring session) — 2026-05-16

- ADR 0091 landed at Accepted; 4 cascade ADR status flips (0090, 0056, 0079) + 1 in-body amendment (0057 Consequences cluster-detection paragraph) + 4 See-also forward-pointers (0045, 0050, 0080, 0037) + this readiness note authored.
- No code changes yet; substrate creation begins at S-0189.
- Tier 1 status at S-0188 close: all 5 Tier 1 criteria PENDING (none of S-0189–S-0193 has fired yet).

### S-0189 (foundations package) — 2026-05-16 — T1-A CLOSED

- **T1-A criterion closed.** `engine/memory/` package authored: `schema.py` (single `SCHEMA_SQL` multi-statement string applied via `executescript()`; all DDL `CREATE … IF NOT EXISTS`; `schema_version` seed via `INSERT OR IGNORE`); `connection.py` (`get_conn()` + `healthcheck()` + `resolve_db_path()`; WAL mode + `busy_timeout=5000` + `foreign_keys=ON` + `exp` function fallback); `mcp_server.py` (JSON-RPC stdio skeleton; empty tool registry; responds to `initialize` / `tools/list` / `ping` / `tools/call` / notifications); `README.md`; plus `conftest.py` + 3 test files.
- **T1-A primary verification** (per readiness-note criterion): `python -c "from engine.memory.connection import get_conn; conn = get_conn(); conn.execute('SELECT 1'); conn.execute('PRAGMA integrity_check')"` against a fresh empty `engine/.memory/` produces `'ok'` + creates the file with all expected tables, the FTS5 virtual table, all 3 triggers, and the `schema_version=1` seed row. Idempotent re-invocation produces identical state.
- **`.tables` listing on the populated file:** `capture_state  drawers  drawers_fts  drawers_fts_config  drawers_fts_data  drawers_fts_docsize  drawers_fts_idx  diary  lineage  query_log  schema_version` (the `drawers_fts_*` shadow tables are FTS5-internal).
- **FTS5 sync trigger round-trip** verified end-to-end via the sqlite3 CLI: `INSERT INTO drawers (... 'hello world uniqueneedlexyz')` → `SELECT content FROM drawers_fts WHERE drawers_fts MATCH 'uniqueneedlexyz'` returns the content → `DELETE FROM drawers WHERE id='test-1'` cascades to remove the FTS5 row.
- **pytest: 31 passed in 0.12s** against the new `engine/memory/` tests (24 schema/connection + 7 mcp_server skeleton). engine/tools/ regression suite (1503 tests) unaffected: `1503 passed in 120.59s`.
- **Full `validate.py` exits 0** with no hard-fails; soft-warns at baseline (carryover only — `skill_layer1_parity_drift: 1`, `mempalace_hnsw_status_suspect: 1`, `issue_collision: 13`, `missing_rigor_score: 358`, `edge_evidence_empty: 46`; the `mempalace_*` warns retire with the substrate at S-0193).
- **Namespace-package convention** (no `__init__.py` in `engine/memory/`) adopted to match `engine/tools/`. pyproject.toml gains `[tool.pytest.ini_options]` `pythonpath = ["."]` + `[tool.mypy]` `explicit_package_bases` / `namespace_packages` / `mypy_path = "."` so absolute imports work for tests and per-file mypy invocations resolve consistently.
- Tier 1 status at S-0189 close: **T1-A CLOSED**; T1-B (capture surface) PENDING at S-0190; T1-C (read surface + verification gate) PENDING at S-0191; T1-D (migration replay) PENDING at S-0192; T1-E (removal) PENDING at S-0193.

### S-0190 (capture surface + dual-write) — 2026-05-16 — T1-B PENDING first natural Stop fire

- **T1-B (capture-surface writes a `room='work'` drawer from the Stop hook) authored, awaiting first natural fire.** `engine/memory/transcript_capture.py` (~230 LOC) + `engine/memory/capture.py` (~32 LOC entrypoint) + `engine/memory/diary.py` (~95 LOC) + `engine/memory/tools.py` (~210 LOC, 2 of 6 MCP tools wired) + `engine/tools/hooks/engine-memory-capture.sh` (~80 LOC bash shim) all landed. `.claude/settings.json` Stop + PreCompact hooks now invoke BOTH `mempalace-hook-wrapper.sh` AND `engine-memory-capture.sh` (parallel-write per ADR 0078). Allowlist additions cover the new hook + python module invocations.
- **Smoke verification.** MCP smoke: `python -m engine.memory.mcp_server` returns 2 tools via `tools/list` (`engine_memory_add_drawer` + `engine_memory_diary_write`). Capture-hook smoke: synthetic JSONL transcript piped via stdin → 1 drawer in `room='work'`, `source_kind='hook_stop'`, `session_id='S-0190-smoke'`, `capture_state.message_count_since_save=3`; re-fire over identical transcript → 0 new drawers (watermark idempotency confirmed end-to-end).
- **99/99 engine/memory tests pass** (was 31 at S-0189; +68 new). `mypy --strict engine/memory/` clean.
- **T1-B natural-fire closure pending.** The next Stop event after `.claude/settings.json` is reloaded by the harness should write a `room='work'`, `source_kind='hook_stop'` drawer for the live session_id. Verify via `sqlite3 engine/.memory/engine_memory.sqlite3 "SELECT count(*), source_kind FROM drawers WHERE source_kind LIKE 'hook_%' GROUP BY source_kind"`. ≥1 row of `hook_stop` closes T1-B; record evidence here at the next interactive session boot.
- **Operational caveat surfaced (third consecutive recurrence).** Engine/tools regression suite (~1500 tests) was attempted twice and hung on chromadb file-lock contention from accumulated `mempalace-mcp` processes — exactly the failure mode ADR 0091 supersedes (per the S-0188 → S-0189 user-cited note, now reconfirmed at S-0190). `pkill -f "mempalace.*mcp"` workaround dropped validate.py from 8+ min to <60s. `validate.py` itself ran cleanly in <60s; the pre-commit hook caught ruff format misses + 6 mypy errors which were fixed inline. Engine/memory subtree fully tested in isolation. Lesson captured at `mempalace://paideia/lessons/drawer_paideia_lessons_469873d7f0a87934c9aefcbc`.
- Tier 1 status at S-0190 close: T1-A CLOSED (S-0189); T1-B AUTHORED + AWAITING FIRST NATURAL HOOK FIRE; T1-C PENDING at S-0191; T1-D PENDING at S-0192; T1-E PENDING at S-0193.

### S-0191 through S-0193 — populated as each session closes

(To be filled in by each implementation session.)
