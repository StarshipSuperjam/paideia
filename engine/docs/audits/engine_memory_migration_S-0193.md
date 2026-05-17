# Engine-memory migration extension replay — S-0193

_Closes T1-E per [`engine/build_readiness/engine_memory_substrate_first_exercise.md`](../../build_readiness/engine_memory_substrate_first_exercise.md) (ADR 0091) by recovering content that the S-0192 original migration filter dropped._

**Verdict:** PASS — 102 new drawers inserted; cross-substrate parity confirmed by [`engine_memory_parity_S-0193.md`](engine_memory_parity_S-0193.md) (verdict PASS, 0 coverage failures across 95 sampled load-bearing drawers).

## What ran

```
python -m engine.memory.migrate_from_mempalace \
  --db-path /Users/shanekidd/Documents/Claude_Files/Paideia/engine/.memory/engine_memory.sqlite3
```

Source: `~/.mempalace/palace/chroma.sqlite3` (same post-S-0186-prune palace S-0192 read; the live palace post-S-0192 had also acquired a `sessions` wing of 1142 auto-capture drawers, which the new wing filter excludes at SQL level). Target: the canonical `engine/.memory/engine_memory.sqlite3` at the main repo path. Lineage source tag: `mempalace_replay_S-0193_extension` (distinct from S-0192's `mempalace_replay_S-0192`; the source-agnostic existing-import lookup means the 383 S-0192 drawers are skipped intact).

## Why the extension was needed

S-0192's audit recorded the migration as complete: 383 drawers + 207 diary entries with assertions PASS. The script enumerated only 5 hardcoded curated rooms (`decisions`, `pushback`, `lessons`, `exploration`, `operations`). The plan-mode parity audit at the start of S-0193 sampled the live mempalace by wing × room and surfaced load-bearing content in rooms the filter never touched:

| Room (paideia wing) | Count | Sample classification |
|---|---|---|
| `problems` | 87 | All `[pushback]`-prefixed pushback content misfiled into a `problems` room name |
| `foundation-planning-s0001` | 10 | Verbatim S-0001 founding-decision exchanges that became ADRs |
| `s0003-adr-collection` | 2 | Phase 0 ADR-collection decision narrative |
| `project` | 1 | PDG papers extraction state snapshot (2026-05-14) |
| `general` | 28 | Mixed — some `[pushback]`-prefixed, others legitimate exploration framings, some legacy noise |

Sessions wing (1142 drawers in `technical`/`architecture`/`problems` rooms, all `added_by=mempalace`) was confirmed auto-capture transcript residue and is correctly droppable.

The mismatch happened because mempalace's auto-classifier uses non-canonical room names — the migration script's CURATED_ROOMS tuple was a closed set that drifted out of sync with what users wrote (or what upstream classified into). The S-0193 extension closes this by routing on both source room name (via EXTENDED_ROOM_MAPPING) and content prefix (via CONTENT_PREFIX_OVERRIDES, defense-in-depth).

## Extension outcome

| Bucket | Count |
|---|---|
| Source candidates enumerated (extended room set, paideia + wing_paideia wings) | 538 drawers |
| Source diary entries enumerated (any wing, `room='diary'`) | 207 |
| Drawers already-imported under prior tag (S-0192) — skipped | 383 |
| Drawers with missing chromadb content (honest tombstone drop) — skipped | 51 |
| Drawers without a recognized room mapping or canonical content prefix — skipped | 2 |
| **Drawers newly inserted under `mempalace_replay_S-0193_extension`** | **102** |
| Diary entries already-imported via deterministic uuid5 | 207 |
| New diary inserts | 0 |

### Source → target room remap (this run's inserts)

| Source room | Target room | Count |
|---|---|---|
| `problems` | `pushback` | **87** |
| `foundation-planning-s0001` | `decisions` | **10** |
| `s0003-adr-collection` | `decisions` | **2** |
| `project` | `operations` | **1** |
| `general` | `pushback` (via content-prefix override) | **2** |

### Post-state per-room totals (S-0192 baseline + S-0193 extension)

| Room | Count |
|---|---|
| decisions | 260 (248 S-0192 + 12 S-0193) |
| lessons | 130 (unchanged from S-0192) |
| pushback | 90 (1 S-0192 + 89 S-0193) |
| operations | 5 (4 S-0192 + 1 S-0193) |

Total: **485 drawers** (383 S-0192 + 102 S-0193 = 485) + **207 diary entries** + **485 FTS5 index rows** (synced via triggers).

## Verification (script-internal assertions, all PASS)

1. **Lineage count under new source tag matches enumeration.** `SELECT count(*) FROM lineage WHERE source='mempalace_replay_S-0193_extension'` == 102 == observed inserted count.
2. **Per-target-room counts match the source→target pair tally.** Each (source_room → target_room) inserted count matches `JOIN lineage ON drawer_id WHERE source=<S-0193 tag> AND d.room=<target>`.
3. **FTS5 index synced.** `SELECT count(*) FROM drawers_fts` == 485 == `SELECT count(*) FROM drawers`.
4. **Spot-check of 5 most-recent S-0193-tagged drawers.** All have non-empty `content` field accessible via `lineage.imported_from` round-trip.

## Idempotency

Re-running the migration with identical arguments will:

- Skip 383 S-0192 drawers (source-agnostic lineage lookup matches the S-0192 imported_from values regardless of current MIGRATION_SOURCE tag).
- Skip 102 S-0193 extension drawers (same mechanism).
- Skip 51 still-tombstoned drawers (chromadb still returns empty content).
- Skip 2 no-mapping drawers (deterministic classifier outcome).
- Diary entries skip via deterministic uuid5 IDs.

The composite `lineage` PK + `INSERT OR IGNORE` + the pre-flight `SELECT drawer_id FROM lineage WHERE imported_from=? LIMIT 1` combine to make rerun safe at any point in either the original or extension migration's lifetime.

## What is still NOT in this migration (intentional drops)

- **Sessions wing (1142 drawers across `technical`/`architecture`/`problems` rooms).** All `added_by=mempalace` auto-capture transcript residue. Excluded at SQL level via `em_w.string_value IN ('paideia', 'wing_paideia')`.
- **51 chromadb tombstone drawers** (mostly `paideia/operations` closet chunks with internal IDs like `closet_paideia_operations_<hex>_<N>`). The sqlite `embedding_metadata` rows persist but `col.get(ids=[...])` returns empty; content is unrecoverable from chromadb regardless of approach. Documented as honest drops in both the S-0192 and S-0193 audits.
- **26 `general`-room drawers with no canonical content prefix.** Legacy fallback noise (matches the S-0186 prune lesson's reason for excluding general by default).

## Companion: worktree-shared substrate path resolver fix

Discovered mid-execution: the S-0192 `connection.py` resolver used `git rev-parse --show-toplevel`, which returns the *current worktree's* path. With Claude Code sessions running in fresh worktrees, each session was getting its own `engine_memory.sqlite3` — the substrate's cross-session continuity guarantee was structurally broken. Fix in the same atomic commit as the migration extension: switch to `git rev-parse --git-common-dir`, then `.parent`, which returns the shared main-repo working-tree root regardless of caller's worktree. All worktrees of the same clone now resolve to the same canonical file. This is the reason this S-0193 worktree can read back what the S-0192 zealous-lederberg worktree migrated into the main-repo path.

## Cross-references

- [ADR 0091](../../adr/0091-engine-memory-substrate-sqlite-fts5.md) — engine-memory substrate decision
- [`engine_memory_parity_S-0193.md`](engine_memory_parity_S-0193.md) — cross-substrate HARD GATE verification (PASS)
- [`engine_memory_migration_S-0192.md`](engine_memory_migration_S-0192.md) — original migration audit (the run this extends)
- [`engine/build_readiness/engine_memory_substrate_first_exercise.md`](../../build_readiness/engine_memory_substrate_first_exercise.md) — T1-A through T1-E readiness criteria
- [Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138) — 5-session cutover roadmap (T1-E recovery + closure landed at S-0193)
- `engine/memory/migrate_from_mempalace.py` (the extension that ran)
- `engine/memory/verify_mempalace_parity.py` (the HARD GATE)
- Backup of source palace state at session start: `~/.mempalace-backup-S-0193-20260517T012057Z.tar.gz` (167MB, sha256 `d6f23743adb0a238031be3f5a143088a353b57dab26b8c58cf472d54a9582e39`)
