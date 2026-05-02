# P_0 — Contract lock (retroactive)

> Backward-looking record of the work already done. Phases 0, 1, 1.5, and 2 closed across S-0001 through S-0023. This chunk is not a future session contract — it exists so the chunk numbering opens at zero and a future session reading the build_plan does not have to reconstruct what came before from session-archive forensics.

## Phase summary

| Phase | Closed at | What landed |
|---|---|---|
| Phase 0 — Foundation | S-0003 | Session-protocol layer, industry-standard repo skeleton, MemPalace integration, ADR collection (ADRs 0001–0022). |
| Phase 1 — Contract Lock | S-0012 | Prompt-pack sessions 9, 10, 11 closed; rendering-policy sibling commitments (ADRs 0023–0030); privacy ADR collapse ([ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md)); project disposition supersession ([ADR 0032](../product/adr/0032-personal-project-disposition.md) supersedes [ADR 0002](../product/adr/0002-commercial-sustainability-without-pedagogical-compromise.md)). |
| Phase 1.5 — Mission Realignment Overhaul | S-0021 | Mission realignment ([ADR 0033](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md)); Discovery / Planning / Engagement triad ([ADR 0034](../product/adr/0034-discovery-planning-engagement-triad.md)); multi-platform Apple expansion ([ADR 0035](../product/adr/0035-multi-platform-apple-expansion.md) supersedes [ADR 0032](../product/adr/0032-personal-project-disposition.md)); inward-document expression contract ([ADR 0036](../engine/adr/0036-expression-contract-for-inward-documents.md)); mechanical sweep + Tier 1/Tier 2 machinery hardening; ROADMAP.md substantive cleanup. |
| Phase 2 — Build Plan Scaffolding | S-0023 | Engine / product wall + CHANGELOG → ENGINE_LOG rename ([ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md), landed S-0022); reserved CHANGELOG.md stub (S-0023 boot, bundled HANDOFF item); `build_plan/` tree authored at S-0023 (this directory). |

## What this chunk records

The four-layer trace system carries the production trace for what each session did:

- **ADRs** — the contract layer. 37 ADRs total at S-0023 close (35 Accepted plus 2 Superseded; [`adr/README.md`](../product/adr/README.md) carries the index).
- **`ENGINE_LOG.md`** — the dated narrative. Every session's material engine changes recorded by category.
- **MemPalace `decision`-tagged drawers** — the conversational story. `mempalace_search` recovers the reasoning.
- **Git history** — the granular blame. `git log --oneline` against the relevant session window recovers the commit chain.

This chunk does not duplicate any of the four layers. It points at them so a future session reading `build_plan/` knows what came before and where to find the detail.

## Strong working commitments and architectural decisions referenced

Phases 0/1/1.5 contracted the project's load-bearing decisions. The list lives in [`ROADMAP.md`](../ROADMAP.md) (`## Strong working commitments referenced throughout`) and is cited by reference here:

- 12 strong working commitments contracted in [ADR 0001](../product/adr/0001-pedagogical-edges-not-historical.md) through [ADR 0012](../product/adr/0012-freshman-defaults-autodidact-ceiling.md).
- 10 architectural decisions contracted in [ADR 0013](../product/adr/0013-mastery-verification-organic-escalation.md) through [ADR 0022](../engine/adr/0022-periodic-project-health-checks.md).
- Phase 1 Contract Lock additions: [ADR 0023](../product/adr/0023-engagement-depth-aggregation.md) through [ADR 0032](../product/adr/0032-personal-project-disposition.md).
- Phase 1.5 Mission Realignment additions: [ADR 0033](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md) through [ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md).

Every downstream chunk in `build_plan/` consumes these by reference; no chunk re-extracts their content.

## What Phase 2 itself produced (S-0023)

The work this chunk documents the close of:

- [`build_plan/MANIFEST.md`](MANIFEST.md), [`build_plan/00_preamble.md`](00_preamble.md), [`build_plan/00_session_schedule.md`](00_session_schedule.md) — orientation, chunk shape, single-table session schedule.
- [`build_plan/P_0_contract_lock.md`](P_0_contract_lock.md) (this file).
- [`build_plan/M_partition_migration.md`](M_partition_migration.md) — bridge session contract for the `engine/` ↔ `product/` migration.
- [`build_plan/P_1_sql_schema.md`](P_1_sql_schema.md) through [`build_plan/P_9_ui_prototype.md`](P_9_ui_prototype.md) — per-phase chunks for Phases 3–9.
- [`product/CHANGELOG.md`](../product/CHANGELOG.md) — reserved stub per the [HANDOFF.md](../HANDOFF.md) item; bundled at S-0023 boot before the build_plan authoring.
- [`engine/ENGINE_LOG.md`](../engine/ENGINE_LOG.md) preamble — light-revised to point at the reserved `CHANGELOG.md` stub instead of naming the absence as the signal.

## Open tensions still active at Phase 2 close

Per [`product/docs/tensions.md`](../product/docs/tensions.md), the OQ-prefixed open set at S-0023 close (consumed by future chunks):

- `OQ-DEC1-A` through `OQ-DEC1-D` — settled by [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) before Phase 6.
- `OQ-WALL-BEHAVIOR` — settled before [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) admits evaluation users.
- `OQ-CONTEXT-COMPRESSION` — settled before [`P_7_teaching_layer.md`](P_7_teaching_layer.md) runs sustained multi-turn engagements.
- `OQ-PEDAGOGY-INFERENCE-LOCUS` — `watch`-tagged; revisit triggers per the entry.
- `OQ-OUTWARD-VOICE` — settled before [`P_7_teaching_layer.md`](P_7_teaching_layer.md) ships any learner-facing surface, OR earlier if `P_9_ui_prototype.md` work surfaces a concrete labeling decision.
- `OQ-WATCH-FLAG-FILE` — `watch`-tagged.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) — full phase arc.
- [`engine/STATE.md`](../engine/STATE.md) — current next-session work item.
- [`../adr/README.md`](../product/adr/README.md) — ADR index.
- [`engine/ENGINE_LOG.md`](../engine/ENGINE_LOG.md) — dated narrative for material engine changes across S-0001 → S-0023.
- [`../session/archive/`](../engine/session/archive/) — per-session outcome records for S-0001 through S-0022 (S-0023 archives at session close).
