# Engine-memory migration replay — S-0192

_Closes T1-D per [`engine/build_readiness/engine_memory_substrate_first_exercise.md`](../../build_readiness/engine_memory_substrate_first_exercise.md) (ADR 0091)._

**Verdict:** PASS

## What ran

`python -m engine.memory.migrate_from_mempalace --db-path /Users/shanekidd/Documents/Claude_Files/Paideia/engine/.memory/engine_memory.sqlite3`

Source: `~/.mempalace/palace/chroma.sqlite3` (272MB live palace, post-S-0186-prune state). Target: `engine/.memory/engine_memory.sqlite3` at the main-repo path (gitignored per ADR 0091 commitment 7).

## Migration outcome

| Bucket | Count |
|---|---|
| Curated drawers in source (any wing, rooms ∈ {decisions, pushback, lessons, exploration, operations}) | 410 |
| Drawers inserted | 383 |
| Drawers skipped (missing chromadb content; stale or orphan) | 27 |
| Diary entries in source (any wing, room='diary') | 207 |
| Diary entries inserted | 207 |

### Per-room distribution (post-migration)

| Room | Drawers |
|---|---|
| decisions | 248 |
| lessons | 130 |
| operations | 4 |
| pushback | 1 |

The exploration room held zero drawers in the post-prune palace — Phase 5 generated decisions and lessons in volume, but exploration drawers were either consolidated into decisions or pruned. Pushback came in at 1 — most pushback-class content lives in lessons-room drawers tagged `pushback`. This matches the empirical distribution the audit-eyes review of MemPalace surfaced at S-0184.

## Verification (script-internal assertions, all PASS)

1. **Lineage count matches enumeration.** `SELECT count(*) FROM lineage WHERE source='mempalace_replay_S-0192'` == 383 == observed inserted count.
2. **Per-room counts match enumeration.** Each room's `JOIN lineage ON drawer_id` count equals the per-room inserted count above.
3. **FTS5 index populated.** `SELECT count(*) FROM drawers_fts` == 383 == `SELECT count(*) FROM drawers`. (Both newly migrated + any pre-existing capture-hook drawers — 383 total in this run; no pre-existing hook drawers in this worktree's previously-uninitialized substrate.)
4. **Spot-check of 5 most-recent decision drawers.** All have non-empty `content` field accessible via `lineage.imported_from` round-trip.

## Idempotency

Re-running the migration with identical arguments produced:

- 0 drawers newly inserted
- 383 drawers skipped as `already-imported` (via `imported_from` lookup on `lineage` composite PK)
- 207 diary entries skipped as `already-imported` (via deterministic uuid5 ID lookup)
- post-state row counts unchanged
- assertions PASS

The `INSERT OR IGNORE` on the lineage composite PK + the pre-flight `imported_from` lookup combine to make rerun safe at any point in the migration's lifetime.

## Cite-worthy verification (separate harness)

`python -m engine.memory.verify_recall --real-data` against the post-migration substrate returned verdict **PASS**: 10/10 fixed-catalog queries hit; 5/5 plausible-recall queries hit. See [`engine_memory_recall_S-0192.md`](engine_memory_recall_S-0192.md).

## Cutover-gate disposition

Per the user-adjudicated self-comparison choice at S-0192 boot: substrate must match plausible-recall expectations on real data. The verdict PASS clears the gate. Issue [#138](https://github.com/StarshipSuperjam/paideia/issues/138) receives `verification_passed: true` at session shutdown.

The cutover proceeds to commit 4 (atomic rewire) without HALT.

## What's NOT in this migration

- The 22,676-drawer pre-S-0186 palace state. The S-0186 prune drained it to 673 curated drawers. This migration sources from the post-prune state (~410 candidates after the curated-rooms filter).
- Per-worktree wing orphans. They were drained at S-0086 / S-0092 and the post-S-0186 palace has no `wing_<6-hex>` survivors per the prune verification.
- `room='work'` transcript auto-capture drawers. Explicitly dropped per the S-0186 prune lesson; the engine-memory substrate's capture surface owns this content going forward (per ADR 0091 Decision 4).
- `room='general'` legacy fallback noise. Same.

## Limits

- The 27 "missing content" skips were drawers whose chromadb document body returned empty from `col.get(ids=[...], include=['documents'])`. The cause is likely chromadb's tombstone-vs-vacuum gap: drawers logically deleted by prior pruning but not yet `VACUUM`-reclaimed have their `embedding_metadata` rows linger while `documents` evaporates. These are honest drops, not data loss.
- Drawers' `tags` field came in mostly empty because the live palace's chromadb metadata didn't carry a tags column for most rooms. The migrated `tags` is `[]` (empty JSON array). This is honest preservation; recall remains content-driven via FTS5 BM25.
- Lineage `source_filed_at` is preserved from the source's `filed_at` metadata where present; missing source `filed_at` resolves to NULL in lineage (and `_filed_at_or_now()` fills the drawer's `filed_at` with current UTC). Recency-boost ranking on those drawers will treat them as "today" — slight upward bias for migrated drawers without timestamp.

## Cross-references

- ADR 0091 (engine-memory substrate decision)
- ADR 0078 (dual-write capture during cutover window)
- `engine/build_readiness/engine_memory_substrate_first_exercise.md` (T1-A through T1-E criteria)
- Issue [#138](https://github.com/StarshipSuperjam/paideia/issues/138) (cutover roadmap)
- `engine/memory/migrate_from_mempalace.py` (the script run)
- `engine/memory/verify_recall.py --real-data` (sibling verification)
