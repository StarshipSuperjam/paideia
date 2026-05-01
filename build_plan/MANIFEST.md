# build_plan/ — chunked authoring sessions for Phases 3–9

This directory carries the per-session working contracts for every downstream phase. [`ROADMAP.md`](../ROADMAP.md) names the phases at a high level — what each phase does, what its output is, what success looks like at the phase boundary. `build_plan/` instantiates that arc into per-session work — what files a session authors, what files it reads at boot, what its success criterion is at session close, what its estimated context budget is.

A future build session boots from one of these chunks plus [`engine/STATE.md`](../engine/STATE.md) plus MemPalace and knows what it is doing without re-deriving its own scope from history.

## Layout

| File | Role |
|---|---|
| [`MANIFEST.md`](MANIFEST.md) | This file — orientation, layout, P-numbering convention. |
| [`00_preamble.md`](00_preamble.md) | Orienting prose for what `build_plan/` is and how to consume it. |
| [`00_session_schedule.md`](00_session_schedule.md) | Single-table view of every chunk: ID, scope, phase mapping, source documents, output target, budget tier, sequencing. |
| [`P_0_contract_lock.md`](P_0_contract_lock.md) | Retroactive record of the work already done (Phases 0, 1, 1.5, 2). Not a future session contract — a backward-looking summary so the chunk numbering opens at zero. |
| [`M_partition_migration.md`](M_partition_migration.md) | Bridge session(s) between Phase 2 close and Phase 5 open: mechanical `git mv` + cross-reference updates landing the [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) `engine/` ↔ `product/` partition. |
| [`P_1_sql_schema.md`](P_1_sql_schema.md) | Phase 3 — SQL schema implementation (Postgres on Supabase). |
| [`P_2_graph_validation.md`](P_2_graph_validation.md) | Phase 4 — graph validation utility (extension of `engine/tools/validate.py`). |
| [`P_3_input_dataset_survey.md`](P_3_input_dataset_survey.md) | Phase 4.5 — input dataset survey for Phase 5 seed authoring. |
| [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md) | Phase 5 — seed graph build (parallelizable subdomain sessions). |
| [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) | Phase DEC.1 — retrieval / mastery-inference architecture decisions. |
| [`P_6_self_correction.md`](P_6_self_correction.md) | Phase 6 — self-correction pipeline. |
| [`P_7_teaching_layer.md`](P_7_teaching_layer.md) | Phase 7 — Sonnet teaching layer (first prototype). |
| [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) | Phase 8 — evaluation harness + Apple Developer enrollment + cost-cap test + small private TestFlight cold-test. |
| [`P_9_ui_prototype.md`](P_9_ui_prototype.md) | Phase 9 — UI prototype (Discovery / Planning / Engagement triad on iPhone + iPad first-class via SwiftUI; Mac via Designed-for-iPad). |

## Numbering convention

`P_N` chunks are per-phase: one chunk per [`ROADMAP.md`](../ROADMAP.md) phase, indexed from `P_0` (the retroactive contract lock) through `P_9` (Phase 9 UI prototype). The mapping is `P_0` → Phases 0/1/1.5/2 retroactive, `P_1` → Phase 3, `P_2` → Phase 4, `P_3` → Phase 4.5, `P_4` → Phase 5, `P_5` → Phase DEC.1, `P_6` → Phase 6, `P_7` → Phase 7, `P_8` → Phase 8, `P_9` → Phase 9. The mapping is contiguous; no gaps, no skips.

`M_*` chunks are bridge sessions distinct from per-phase work — one-off mechanical migrations, machinery hardening, or other cross-phase engine work. `M_partition_migration.md` is the only `M_*` chunk at the build_plan's authoring; future bridge sessions get their own `M_*` chunks as they are scoped.

The original Phase 2 plan from S-0001 forecast `P_1` through `P_13` per-phase chunks under a different chunking. The realignment across S-0013 → S-0022 collapsed the count: the per-subdomain Phase 5 sessions (originally each their own `P_*` chunk) live as enumerated sub-sessions inside [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md), because they share scope, workflow, and validator and benefit from being colocated under one per-phase contract. The Phase 5 internal session-naming in [`ROADMAP.md`](../ROADMAP.md) (P_3 Epistemology through P_9 Cross-domain pass) is sub-session enumeration *within* `P_4`, not a clash with the `build_plan/P_N` chunk numbering.

## Engine / product partition awareness

Per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md), the repo restructures into `engine/` and `product/` subtrees between Phase 2 close and Phase 5 open. The `M_partition_migration.md` chunk executes the `git mv`. Every per-phase chunk in `build_plan/` references **partition-aware paths** from the start — `engine/tools/validate.py` rather than `tools/validate.py`, `product/seed-graph/...` rather than `supabase/migrations/...` for Phase 5 outputs, `engine/operations/...` rather than `docs/operations/...` for procedural references — so when the migration lands the chunks need zero edits. Until the migration runs, the partition-aware paths in these chunks point at directories that do not yet exist; this is deliberate.

The reservation extends to file references in success criteria, source-document lists, and load-bearing-ADR pointers. Per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md)'s edge-case resolutions: `ROADMAP.md` and `README.md` stay at root (they orient to both subtrees); `STATE.md`, `CLAUDE.md`, and `ENGINE_LOG.md` migrate to `engine/`; `AGENT_INSTRUCTIONS.md` and `CHANGELOG.md` migrate to `product/`. Chunks reference each by its post-migration path.

## How to consume a chunk

A future session boots by reading [`engine/STATE.md`](../engine/STATE.md) per the boot procedure in [`engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md), then opens the `build_plan/P_N_*.md` chunk that matches `engine/STATE.md`'s next-session work item. The chunk names what to author, what to read, what success looks like, and what budget to target. The session does not re-derive its own scope from `ROADMAP.md` history; the chunk is the contract.

Boot order at S-0024+:

1. `engine/CLAUDE.md` (auto-loaded by Claude Code; resolution mechanism settled at [`M_partition_migration.md`](M_partition_migration.md)).
2. `engine/STATE.md` — names the next-session work item by `P_N` reference.
3. `build_plan/P_N_*.md` — the per-session contract.
4. The chunk's named source documents (read in the order the chunk lists them).
5. MemPalace `mempalace_search` against terms derived from the chunk's scope.

Then claim the slot per [`engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md) and execute the chunk.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) — phase scope and success criteria at roadmap granularity.
- [`../engine/STATE.md`](../engine/STATE.md) — current phase and next-session work item.
- [`../adr/0037-engine-product-wall-and-changelog-rename.md`](../adr/0037-engine-product-wall-and-changelog-rename.md) — the engine/product partition contract `build_plan/` chunks reference.
- [`../engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md) — boot procedure that consumes `build_plan/` chunks.
- [`../engine/operations/document-voice.md`](../engine/operations/document-voice.md) — the inward-document expression contract `build_plan/` chunks are governed by.
