# 00 — Preamble

`build_plan/` is the per-session operational layer between [`ROADMAP.md`](../ROADMAP.md) (phase-level scope) and [`engine/STATE.md`](../engine/STATE.md) (per-session pointer). A future session reading the `P_N` chunk that matches the next-session work item knows what it is authoring, what it reads at boot, what success looks like at close, and what context budget to target — without re-deriving any of that from roadmap history or session archives.

The chunks are operational session contracts. They cite ADRs by reference rather than re-extracting their substance, they cite source documents by path rather than embedding their content, they cite success criteria from [`ROADMAP.md`](../ROADMAP.md) and add per-session granularity rather than re-stating the phase's purpose. The discipline is to keep each chunk lean — a ~200-line per-session contract that loads cheaply and points at the heavier artifacts when they need to be consumed.

## What a chunk contains

Each per-phase chunk follows a common shape, mirroring the `## Next session work item` block in [`engine/STATE.md`](../engine/STATE.md):

- **Phase scope** — one-paragraph orientation. What this phase does in the project's arc, with a [`ROADMAP.md`](../ROADMAP.md) cross-reference for the full phase context.
- **Output** — concrete deliverables. Files authored, schemas migrated, behaviors implemented. Partition-aware paths per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md).
- **Success criteria** — testable bullets. The session knows it is done when these hold.
- **Source documents** — files the session reads at boot beyond the CLAUDE.md auto-load. Listed in the order the session reads them.
- **Load-bearing ADRs** — ADRs the chunk consumes by contract. The chunk does not re-extract their content; the chunk relies on them and cites them.
- **Estimated context budget** — target / cap percentages and tier (substantive extraction vs mechanical/procedural per CLAUDE.md). Includes notes on context-amplification risk where the work spans many files.
- **Session sequencing** — single session vs multi-session. If multi-session, the chunking strategy and the partial-closure protocol per [`engine/operations/session-shutdown-sequence.md`](../engine/operations/session-shutdown-sequence.md).
- **Open tensions consumed** — `OQ-*` entries from [`product/docs/tensions.md`](../product/docs/tensions.md) that the phase's work resolves or depends on.

## How chunks relate to ROADMAP

[`ROADMAP.md`](../ROADMAP.md) is forward-looking and phase-grained; `build_plan/P_N_*.md` chunks are session-grained and contract-of-record. When a chunk's phase is in progress or closed, [`ROADMAP.md`](../ROADMAP.md) carries the present-state phase scope and success criteria; the chunk carries the per-session operational contract. The two layers do not duplicate each other — the chunk does not re-extract phase scope; the roadmap does not enumerate per-session deliverables.

When a chunk's phase closes, the chunk remains in `build_plan/` as the historical session-contract record, recoverable for any future session that needs to understand how the phase was actually executed (paired with [`engine/session/archive/`](../engine/session/archive/) for the per-session outcomes).

## Voice

Chunks are governed by [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) and operationalized through [`engine/operations/document-voice.md`](../engine/operations/document-voice.md). The voice is present-tense declarative: a chunk describes the contract a session takes on when it claims the corresponding slot. ADR cross-references are bibliographic (end-of-section "See also" pointers, not parenthetical commentary on every assertion). The chunk does not narrate its own revision history — that lives in the four-layer trace ([ADRs / `engine/ENGINE_LOG.md` / MemPalace / git](../engine/operations/document-voice.md#where-the-trace-lives)).

## Sequencing

Per [`engine/STATE.md`](../engine/STATE.md) and [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md), the execution order across the build_plan is:

1. [`P_0_contract_lock.md`](P_0_contract_lock.md) — retroactive; not a future session.
2. [`M_partition_migration.md`](M_partition_migration.md) — bridge between Phase 2 close and Phase 5 open. Executes first after S-0023 because partition-aware path references in every downstream chunk presuppose the migration has run.
3. [`P_1_sql_schema.md`](P_1_sql_schema.md) — Phase 3, first substantive build phase.
4. [`P_2_graph_validation.md`](P_2_graph_validation.md) — Phase 4. Depends on `P_1` because validation runs against the schema.
5. [`P_3_input_dataset_survey.md`](P_3_input_dataset_survey.md) — Phase 4.5. Independent of `P_1`/`P_2`; can run in parallel with `P_2` if budget allows.
6. [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md) — Phase 5. Depends on `P_1` (schema), `P_2` (validator), `P_3` (input survey).
7. [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — Phase DEC.1. Depends on `P_4` because retrieval-shape decisions become testable only after the seed graph is mature.
8. [`P_6_self_correction.md`](P_6_self_correction.md) — Phase 6. Depends on `P_1` (`tension_log` schema) and `P_5` (retrieval shape).
9. [`P_7_teaching_layer.md`](P_7_teaching_layer.md) — Phase 7. Depends on `P_4` (seed graph), `P_5` (retrieval), `P_6` (self-correction loop).
10. [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) — Phase 8. Depends on `P_7`. Apple Developer Program enrollment starts at `P_8` boot per the 2–4 week lead-time constraint.
11. [`P_9_ui_prototype.md`](P_9_ui_prototype.md) — Phase 9. Depends on `P_4` (seed graph for content), `P_7` (teaching endpoint), `P_8` (cost cap, App Store readiness).

The dependency graph is not strictly linear. The estimates above are the longest-path order; parallelizable work is named in the chunks themselves.

## See also

- [`MANIFEST.md`](MANIFEST.md) — file index and numbering convention.
- [`00_session_schedule.md`](00_session_schedule.md) — single-table view of every chunk.
- [`../ROADMAP.md`](../ROADMAP.md) — phase scope and success criteria.
- [`engine/operations/document-voice.md`](../engine/operations/document-voice.md) — the expression contract `build_plan/` chunks follow.
