# MemPalace regression diagnostic — S-0187 (2026-05-15)

> Authored by S-0187 per [ADR 0090](../../adr/0090-phase-6-recall-substrate-decision.md) commitment 2a follow-on. S-0186 closed claiming MemPalace substrate restored to working order; S-0187 boot found the substrate already degraded back to a near-identical broken state (Mode 2 search throws; sessions-wing pollution re-accumulated). This audit names the root causes, lands inline fixes, and documents what wasn't understood enough to fix in-session.
>
> Sibling to [`mempalace_state_S-0186.md`](mempalace_state_S-0186.md). Where S-0186 said "fixed", this audit reports "fixed-with-caveats; here's what was actually broken".

## Headline

The S-0186 fix shipped working immediately post-rebuild but did not durably hold. Three coupled causes (one ALREADY-KNOWN-AND-AUTHORED-BUT-DEFERRED-TO-S-0187; one ROOT-CAUSE-BUG-IN-S-0186-CODE; one SECONDARY-S-0186-FIX-INCOMPLETE):

| Cause | Status pre-S-0187 | S-0187 fix |
|---|---|---|
| **C1 — Rebuild-tool persists nothing at create-time** (the originally-planned S-0187 work per ADR 0090 commitment 2a). The rebuild inherits mempalace `_HNSW_BLOAT_GUARD` (`sync_threshold=50_000`) at create-collection time; `_apply_batch._persist()` never fires during the rebuild's 5K-batch adds; `link_lists.bin = 0 bytes`; `index_metadata.pickle` never written; upstream `quarantine_stale_hnsw` quarantines the post-rebuild segment within minutes; subsequent opens loop-quarantine the placeholder. | Already-known via S-0186 audit; scheduled for S-0187. | ADR 0079 amendment + `mempalace_rebuild_hnsw.py` updates: override `hnsw:sync_threshold=3` at create-collection time so per-batch persist fires; raise to 100 via `collection.modify(configuration=...)` post-adds. |
| **C2 — Defensive post-hook prune field-name bug (S-0186 implementation flaw).** `mempalace_post_hook_prune.py` classifier hardcoded `em_t.key='created_at'`. Mempalace writes the drawer-add timestamp as `filed_at`, not `created_at`. The join condition returned ZERO rows on every fire. The defensive prune logged `post_prune_deleted=0` on every hook, while `sessions/technical` accumulated 67 pollution drawers within S-0186's own rebuild window. | Bug introduced at S-0186; surfaced at S-0187 via Probe 4. | Field-name correction: `created_at → filed_at`. New `_DRAWER_TIMESTAMP_KEY` constant. Updated test fixture (the prior fixture also used `created_at` — fixture-vs-reality discipline broken; corrected). New regression guard exercises the bug shape. |
| **C3 — Supabase pgbouncer strips session-level `options=-c`.** The S-0186 fix added `connect_timeout=10` + `options="-c statement_timeout=30000"` on `validate.py`'s `psycopg.connect`. The project's `SUPABASE_DB_URL` points at the transaction-pool URL; pgbouncer in transaction-pool mode silently strips session-level `options=-c` parameters from the startup packet. The server-side cap is inert. Hang vector survives — observed 8+ minute hang on S-0187 boot's first eager-claim attempt. | S-0186 fix incomplete (claim of "recurring psycopg.connect hang fixed" was premature). | New client-side wall-clock watchdog (45s default; thread + `threading.Event` + `conn.cancel()`) on top of S-0186's caps. Server-side cap retained as defense-in-depth for direct-connection URLs. Test coverage: cancel-fires-on-cap + no-spurious-cancel-on-fast-query. |

C1, C2, C3 are independent failure modes. C1 was always going to fire; C2 hid it (drawers accumulated unchecked); C3 made even diagnosing it painful.

## Probe results

### Probe 1 — palace-on-disk forensic state

Read live state of `~/.mempalace/palace/`:

| Segment | Status | `link_lists.bin` | `index_metadata.pickle` |
|---|---|---|---|
| `a897c0a0-d0e4-43e0-8164-971ab608ab28` (drawers, active) | Active since 13:48 UTC | **0 bytes** | **missing** |
| `548d3597-ddc4-4a45-bee0-a39d360c9e4c` (closets, active) | Active since 14:10 UTC | **0 bytes** | **missing** |
| `97a76464-c626-474f-af1b-f4ce81a847e6.drift-20260515-134824` (S-0186 rebuild drawers — already quarantined) | Quarantined 13:48 UTC, ~18 min after S-0186 close | 0 bytes | missing |
| `d9e7ab09-d422-40e5-9cf8-46f5b7a99da1` (pre-S-0186 corrupt drawers) | Reference: still present with `index_metadata.pickle` (124 bytes) | 0 bytes | **present** (forensic) |

**Quarantine accumulation:** 49 directories total (13 `.drift-*` + 36 `.corrupt-*`). The S-0153 observability vector per ADR 0079 is firing repeatedly — every open quarantines the previous segment, creates a fresh-empty placeholder, the next open quarantines THAT too.

### Probe 2 — `configuration.hnsw.sync_threshold` (both channels, both collections)

| Collection | metadata.hnsw:sync_threshold | configuration.hnsw.sync_threshold | count |
|---|---|---|---|
| `mempalace_drawers` | (not in metadata dict) | **100** ← S-0186 set via `mempalace_set_sync_threshold.py` | 745 |
| `mempalace_closets` | **50000** | **50000** ← NOT migrated by S-0186 | 51 |

The drawers collection has the project steady-state threshold; closets still has mempalace's `_HNSW_BLOAT_GUARD` default. S-0186 didn't migrate closets — narrow oversight (closets is small, low-volume; not visible at 0-1 drawer/session pace).

### Probe 3 — hook log inspection

`mempalace-hook.log` is scattered across 26 worktrees (each worktree resolves `git rev-parse --show-toplevel` to its own worktree path, NOT the main repo). The pre-S-0186 hook fires logged without `post_prune_deleted=`; post-S-0186 fires logged it.

Only ONE worktree shows the `post_prune_deleted=` field (the `magical-bhabha-c20f19` worktree where S-0186 was authored). All entries show `post_prune_deleted=0`. The defensive prune fired on every hook completion since S-0186 close and deleted zero drawers each time.

### Probe 4 — defensive-prune classifier validation against live db

`SELECT DISTINCT key FROM embedding_metadata` returned:
`added_by, agent, chroma:document, chunk_index, date, drawer_count, entities, extract_mode, filed_at, hall, ingest_mode, normalize_version, room, source_file, topic, type, wing`.

**NO `created_at` field.** Mempalace writes `filed_at` (ISO-8601 with microseconds, e.g. `2026-05-15T13:48:32.596151`).

Running the production classifier query (with `em_t.key='created_at'`) against the live db with `since='last hour'` returned 0 rows. Running it with `em_t.key='filed_at'` returned 0 rows for the last-hour window (no new pollution in last hour). Running it WITHOUT any timestamp filter returned all 67 sessions/technical pollution drawers — confirming the wing + room classifier is correct; only the timestamp-field name was wrong.

The 67 pollution drawers carried `filed_at` values in a 7-second window: `2026-05-15T13:48:25.942394` → `2026-05-15T13:48:32.596151`. That window aligns with S-0186's HNSW rebuild — these drawers are auto-capture of S-0186's own pre-commit hook's noisy stderr (validator soft-warn dumps, commit messages, etc.).

### Probe 5 — wing-filter failure isolation

| Call | Result |
|---|---|
| `mempalace_drawers.query(query_texts=['pushback rule extraction'], n_results=5)` | Returns 5 results — ALL from `sessions/technical` (the pollution). HNSW is functional in some sense but indexed only the recent adds. |
| `mempalace_drawers.query(query_texts=['pushback rule extraction'], where={'wing':'paideia'}, n_results=5)` | `InternalError: Error finding id` (upstream MemPalace/mempalace#1082 surface). |
| `mempalace_drawers.get(limit=5, include=['metadatas'])` | Returns 5 paideia/diary drawers cleanly (bypasses HNSW; direct ID fetch). |

Interpretation: HNSW's empty graph (link_lists.bin=0) has only the recently-added drawers indexed; older curated content is in SQLite but not reachable from HNSW. Wing-filter traversal can't find IDs in the filtered set → upstream error.

### Probe 6 — sync_threshold cross-check

`mempalace_drawers` has 745 drawers; gained ~72 since S-0186 close (673). At `sync_threshold=100`, persist should have fired 0-1 times. `link_lists.bin = 0` is consistent with 0 persists — the threshold-100 hasn't been reached in a single chromadb client lifetime (each hook fire is a fresh process; each fresh process adds 2-5 drawers; 100 is never crossed within a process).

This confirms ADR 0079's premise was structurally fragile from S-0145: the persist-recurrence vector is inversely proportional to per-session drawer volume × sync_threshold. The S-0187 amendment (in-rebuild override) addresses the rebuild boundary; the steady-state writes after that are still subject to the 100-per-process-lifetime cap. **For the project's 2-5-drawer-per-session workload, persist will fire roughly every 20-50 sessions during steady-state operation.** That's the recurrence floor — not the rebuild boundary.

## Inline fixes landed in S-0187

1. **`engine/tools/validate.py` + `test_validate.py`** — client-side wall-clock query timeout on `_read_graph_from_db()`. 45s default cap; `threading.Event` watchdog calls `conn.cancel()` (PQcancel) on cap exceed. New constants `_GRAPH_AUDIT_WALL_CLOCK_TIMEOUT_S`. Two new tests in `TestReadGraphFromDbTimeouts`.

2. **`engine/tools/mempalace_post_hook_prune.py` + `test_mempalace_post_hook_prune.py`** — classifier field-name correction `created_at → filed_at`. New `_DRAWER_TIMESTAMP_KEY` constant. Updated fixture (12 metadatas). New regression test asserts the constant pinned and that a palace seeded with the wrong key returns 0 candidates.

3. **`engine/tools/mempalace_rebuild_hnsw.py` + `test_mempalace_rebuild_hnsw.py`** — ADR 0079 amendment. New `REBUILD_SYNC_THRESHOLD` (= 3) and `STEADY_STATE_SYNC_THRESHOLD` (= 100) constants. Create-collection metadata override; post-adds configuration-channel raise. Two new regression tests + existing-test update.

4. **`engine/adr/0079-hnsw-sync-threshold-tuning.md`** — S-0187 Amendment subsection naming the in-rebuild threshold override mechanism, the falsified ≥150-session premise + root cause, the new constants, the scheduled-rebuild-cadence decision (no scheduled rebuild; named re-evaluation triggers).

5. **Live palace remediation** (post-fix-landing): audit-mode prune via `prune_mempalace.py --audit-sessions-pollution --apply` to drain the 67 pollution drawers; rebuild via the amended `mempalace_rebuild_hnsw.py` to restore HNSW; empirical re-verification.

## Issues filed for follow-up

1. **Supabase pgbouncer strips session-level `options=-c statement_timeout=30000`.** The watchdog is the load-bearing protection; the server-side cap is decorative on the transaction-pool URL. Confirm with Supabase docs or test against direct-connection URL. Track as upstream-coordination posture if no immediate project-side fix is warranted beyond the watchdog.

2. **HNSW persist-recurrence at steady-state** (~20-50 sessions). The S-0187 amendment fixes the rebuild boundary but not the steady-state cadence. If the recurrence proves problematic between rebuilds, consider lowering steady-state sync_threshold further OR scheduling a maintenance rebuild.

3. **`mempalace_closets` collection** still at sync_threshold=50_000 (S-0186 set drawers only). Low-priority (51 drawers, low write volume) but worth a follow-up `mempalace_set_sync_threshold.py` invocation against the closets collection.

4. **Hook log fragmentation across worktrees.** Each worktree has its own `.claude/logs/mempalace-hook.log` because the hook wrapper resolves `git rev-parse --show-toplevel`. Operational orientation: aggregating signal across worktrees requires looping over the worktree set. Consider whether the hook should log to a single main-repo path instead.

5. **Quarantine accumulation discipline.** 49 quarantine directories accumulated over 4 days. The S-0153 telemetry per ADR 0079 surfaces them via the `mempalace_quarantine_accumulation` soft-warn. A periodic cleanup mechanism (e.g., delete quarantine dirs older than N days) would reduce filesystem load and forensic noise. Trigger-gated on the soft-warn firing.

## Empirical re-verification — the swap-into-live damaged the rebuild's output

S-0187 ran the rebuild via the amended `mempalace_rebuild_hnsw.py` against a scratch palace (`~/.mempalace/palace.S-0187-scratch`). The post-rebuild state on the scratch palace, verified before the swap:

- `<scratch>/45640116-*/link_lists.bin = 6044 bytes` (drawers segment; 678 drawers)
- `<scratch>/45640116-*/index_metadata.pickle = 80878 bytes`
- `<scratch>/0ca73a87-*/link_lists.bin = 272 bytes` (closets segment; 51 drawers)
- `<scratch>/0ca73a87-*/index_metadata.pickle = 6410 bytes`

**The S-0187 amendment's primary claim is empirically verified on the scratch:** `_persist()` fires during the rebuild's batched adds; `link_lists.bin` is non-zero; `index_metadata.pickle` is written.

The atomic-rename swap (`mv scratch → palace; mv old → palace.pre-swap-broken`) completed cleanly. Within ~seconds of the swap, the next `mempalace_search` MCP invocation opened the new palace path. **Immediately after that open:**

- `<live>/45640116-*/link_lists.bin = 0 bytes (0 blocks allocated)` — file content gone; no sparse-file disguise
- `<live>/45640116-*/index_metadata.pickle` — **file deleted**
- Same for `0ca73a87-*`

The MCP server (and / or any other consumer process that opens the palace via chromadb's `PersistentClient`) is **destroying the rebuild's persisted state on first read-after-swap**. This is the same fundamental pattern S-0186 reported claiming-to-have-fixed; the S-0187 forensic data shows it's still active.

### Candidate mechanism (unverified; for the follow-up Issue)

Three running mempalace MCP server processes were observed during the swap:
- PIDs 50594 (1:49PM start), 59088 (2:33PM start), 72901 (post-swap). The OLD MCP servers held chromadb in-memory state from the OLD palace (the one renamed to `.pre-swap-broken`); when they next interact with the path `~/.mempalace/palace`, they may write their stale in-memory state (which contains the "fresh empty" log records for the OLD broken palace) over the rebuilt files on disk. The mtimes confirm: live segments updated at 15:41:36 (matches `mempalace_search` invocation timing); rebuild completed at 15:39:xx.

**The S-0187 amendment is correct at the rebuild boundary; durability of the rebuilt state through the MCP-server-open path is a separate problem layer.**

### What was attempted to repair

- Audit-mode prune drained 67 pollution drawers (745 → 678; confirmed via `mempalace_status`).
- Scratch-then-swap rebuild via amended tool: rebuild succeeded; scratch state was verified non-zero; swap completed; live state observed as zeroed-by-MCP-open within seconds.
- Embed-fn check broadened to accept `onnx_mini_lm_l6_v2` (chromadb 1.5.x's named default) in addition to the older `default` sentinel. Subsidiary fix landed inline; was blocking the rebuild's safety check from accepting the live palace's actual embedding-function name.

### What's needed to close the gap (deferred per the diagnostic-only scope)

- Reproduce the destroy-on-open path with `lsof` capture of which MCP-server FDs touch which files at which moment.
- Confirm whether killing all MCP servers BEFORE the swap (then letting a fresh one spawn post-swap) preserves the rebuild's on-disk state.
- If yes, the swap procedure documented in `mempalace-operations.md` needs a "kill MCP servers first" step.
- If no, the destruction is structural to chromadb's open path and a different mitigation is warranted.

This is the substrate-decision tension surfacing again: even with all three S-0187 fixes landed (watchdog + field-name + rebuild amendment), the MCP-server-open destruction is a separate failure layer. Filed as Issue (see below).

## What worked vs what didn't (honest assessment)

**Worked:**
- Probe 1 immediately surfaced the link_lists.bin=0 state.
- Probe 4 immediately surfaced the field-name bug.
- The watchdog test passed on first try; the watchdog mechanism is sound (even if the live observation didn't catch the hang within 45s — that's a separate question explored below).

**Didn't work or partial:**
- The watchdog didn't catch the live hang on the first eager-claim attempt (8+ minute hang against an established TCP connection). Unclear whether the watchdog's `conn.cancel()` actually issued PQcancel cleanly over the pgbouncer transaction-pool URL. The second eager-claim attempt completed in 10s. Possible explanations: (a) Supabase was transiently responsive at attempt 2; (b) watchdog fired correctly at attempt 1 but the hang continued elsewhere (e.g., conn.close() phase); (c) some other coupling. The watchdog's test coverage exercises the mechanism in isolation; under-the-microscope diagnosis of the live hang isn't in this session's scope.
- The S-0186 audit's claim that wing-filter Mode 2 search "now returns 15 results per query" appears to have been a brief post-rebuild window (~18 minutes per the quarantine timestamp). The audit's snapshot was correct at capture time; the durability claim was inferred from that snapshot rather than re-verified over a longer window.

## Cross-references

- [ADR 0079](../../adr/0079-hnsw-sync-threshold-tuning.md) — amended in this session (Amendment subsection).
- [ADR 0090](../../adr/0090-phase-6-recall-substrate-decision.md) — commitment 2a follow-on; this session is the S-0187+ deliverable named in the ADR's Consequences.
- [`mempalace_state_S-0186.md`](mempalace_state_S-0186.md) — the audit this session re-verified.
- [`engine/tools/mempalace_rebuild_hnsw.py`](../../tools/mempalace_rebuild_hnsw.py) — amended.
- [`engine/tools/mempalace_post_hook_prune.py`](../../tools/mempalace_post_hook_prune.py) — field-name fix.
- [`engine/tools/validate.py`](../../tools/validate.py) — watchdog added.
- Upstream [MemPalace/mempalace#1082](https://github.com/MemPalace/mempalace/issues/1082) — Mode 2 wing-filter throw; the failure surface re-observed at S-0187.
- Upstream [MemPalace/mempalace#1322 + #1342](https://github.com/MemPalace/mempalace/issues/1322) — `quarantine_stale_hnsw`; the mechanism doing the 49 quarantine accumulations.
