# 00 — Session schedule

Single-table view of every per-session chunk. The chunk is the contract — this table is the index.

## Table

| Chunk | Phase | Title | Output target | Sequencing | Budget tier |
|---|---|---|---|---|---|
| [`P_0_contract_lock.md`](P_0_contract_lock.md) | 0 / 1 / 1.5 / 2 | Foundation, contract lock, mission realignment, build_plan scaffolding | Retroactive — closed at S-0023. | Done. | n/a |
| [`M_partition_migration.md`](M_partition_migration.md) | Bridge | Engine / product folder migration per [ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md) | `engine/` and `product/` subtrees populated by `git mv`; cross-references updated; `engine/tools/validate.py` clean. | First post-S-0023; one or two sessions. | Mechanical (target 70%, cap 80%). |
| [`P_1_sql_schema.md`](P_1_sql_schema.md) | 3 | SQL schema implementation | Postgres migrations under `product/seed-graph/migrations/` (or wherever the migration directory resolves post-`M_partition_migration`); `nodes`, `edges`, `learner_events`, `mastery_snapshots`, `tension_log`, `settings` tables live on Supabase dev project. | After `M_partition_migration`; single session. | Substantive (target 60%, cap 70%). |
| [`P_2_graph_validation.md`](P_2_graph_validation.md) | 4 | Graph validation utility — `engine/tools/validate.py` extension | `engine/tools/validate.py`'s `validate_graph()` connects to live Supabase DB; hard-fail and soft-warn categories per [ROADMAP §4.1](../ROADMAP.md); `product/seed-graph/migrations/PREDICATE_MANIFEST.md`, `product/seed-graph/migrations/ROUTING.md`, `engine/operations/seed-chunked-authoring.md` populated. | After `P_1`; single session. | Substantive (target 60%, cap 70%). |
| [`P_3_input_dataset_survey.md`](P_3_input_dataset_survey.md) | 4.5 | Input dataset survey | New section in `product/docs/content-strategy.md` ("Cross-Domain Reference Inventories — Survey") with per-candidate assessment against the five usability axes per [ROADMAP §4.5](../ROADMAP.md). | Independent of `P_2`; can run in parallel; single session. | Substantive (target 60%, cap 70%). |
| [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md) | 5 | Seed graph build (parallelizable subdomain sessions) | Concept-level seed across philosophy subdomains: epistemology, ethics, metaphysics, philosophy of mind, philosophy of language, philosophy of science, service nodes, cross-domain edges pass. Each subdomain sub-session writes a migration file; per-subdomain working contracts enumerated inside the chunk. | After `P_1`/`P_2`/`P_3`; multi-session (~8 subdomain sub-sessions; parallelizable per the eager-claim discipline). | Substantive per sub-session (target 60%, cap 70%). |
| [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) | DEC.1 | Retrieval / mastery-inference architecture decisions | ADRs settling OQ-DEC1-A through OQ-DEC1-D per [ROADMAP Phase DEC.1](../ROADMAP.md). | After `P_4`; single session. | Substantive (target 60%, cap 70%). |
| [`P_6_self_correction.md`](P_6_self_correction.md) | 6 | Self-correction pipeline | Sonnet-side tension emission; Opus-batch reviewer; provisional-ADR pipeline per `product/docs/self-correction.md`. | After `P_1` and `P_5`; single or paired session. | Substantive (target 60%, cap 70%). |
| [`P_7_teaching_layer.md`](P_7_teaching_layer.md) | 7 | Sonnet teaching layer (first prototype) | Callable teaching endpoint consuming `product/AGENT_INSTRUCTIONS.md` verbatim as system prompt; one-hop prerequisite + two-hop neighborhood retrieval; DeepTutor fork integration. | After `P_4`/`P_5`/`P_6`; single session for prototype, multiple for hardening. | Substantive (target 60%, cap 70%). |
| [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) | 8 | Evaluation harness + Apple Developer enrollment + cost-cap test + private TestFlight cold-test | Stock-Sonnet-without-rendering-policy baseline harness; Apple Developer Program enrollment in flight; cost-cap mechanism wired and tested; small private TestFlight cold-test recorded as the verification artifact. | After `P_7`; multi-session (Apple lead time pins enrollment to phase open). | Mixed (mechanical for harness, substantive for cold-test debrief). |
| [`P_9_ui_prototype.md`](P_9_ui_prototype.md) | 9 | UI prototype — Discovery / Planning / Engagement triad | SwiftUI codebase shipping iPhone + iPad first-class; Mac via Designed-for-iPad; App Store distribution. Per [`product/docs/ui-architecture.md`](../product/docs/ui-architecture.md). Application code; ENGINE_LOG / ADR discipline does not apply. | After `P_4`/`P_7`/`P_8`; multi-session (application code; git-only). | Mixed (UI authoring is iterative; not extraction-tier). |

## Open tensions consumed by phase

The `OQ-*` entries in [`product/docs/tensions.md`](../product/docs/tensions.md) that gate or feed each chunk:

- **`P_1`** (Phase 3): no `OQ-*` blockers as of S-0023; `OQ-PRIVACY-A` and `OQ-PRIVACY-B` were closed by [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) before S-0023.
- **`P_2`** (Phase 4): no `OQ-*` blockers.
- **`P_3`** (Phase 4.5): no `OQ-*` blockers.
- **`P_4`** (Phase 5): consumes the [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) survey output from `P_3`; no `OQ-*` blockers.
- **`P_5`** (Phase DEC.1): closes `OQ-DEC1-A` through `OQ-DEC1-D` by ADR.
- **`P_6`** (Phase 6): no `OQ-*` blockers.
- **`P_7`** (Phase 7): closes `OQ-CONTEXT-COMPRESSION` by ADR before sustained multi-turn engagements run; closes `OQ-OUTWARD-VOICE` by ADR before any learner-facing surface ships.
- **`P_8`** (Phase 8): closes `OQ-WALL-BEHAVIOR` by ADR before evaluation users are admitted.
- **`P_9`** (Phase 9): may surface concrete need that resolves the `OQ-*` watch entries; consumes the `OQ-WALL-BEHAVIOR` decision from `P_8`.

## Engine vs product subtree per chunk

Per [ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md):

- **Engine chunks:** `M_partition_migration`, `P_1` (schema is engine because the schema is the substrate the engine validates against; the *content* loaded into the schema is product), `P_2` (validator is engine), `P_5` (retrieval architecture is engine), `P_6` (self-correction pipeline is engine), `P_8` (evaluation harness is engine).
- **Product chunks:** `P_3` (input dataset survey lands in `product/docs/content-strategy.md`), `P_4` (seed graph content), `P_7` (teaching layer is *about* how the engine talks to learners — files under `product/` per the ADR 0037 edge-case resolution for `AGENT_INSTRUCTIONS.md` and ADR 0027), `P_9` (UI prototype is product).

## Cadence triggers

The health-check cadence trigger fires every 10 sessions as of S-0033 (was every 30 from S-0001 to S-0032, tightened by user direction per ADR 0022 Consequences amendment; configurable per [`engine/operations/health-check.md`](../engine/operations/health-check.md)). The trigger fires at the boot of the cadence-numbered session itself when `next_id mod health_check_cadence == 0` (the slot about to be claimed; per [ADR 0043](../engine/adr/0043-hook-architecture.md) which corrected the original `last_claimed` off-by-one at S-0031):

- S-0030 — first cadence trigger; landed manually as a phase-boundary fire (see [`docs/health-checks/S-0030.md`](../docs/health-checks/S-0030.md)).
- S-0040, S-0050, S-0060, ... — subsequent firings under the corrected logic at the new cadence-10.

Sessions that fire the cadence trigger pause and propose the audit at boot per the boot procedure in [`engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md).

## See also

- [`MANIFEST.md`](MANIFEST.md) — file index.
- [`00_preamble.md`](00_preamble.md) — orientation and chunk shape.
- [`../ROADMAP.md`](../ROADMAP.md) — phase scope and success criteria.
- [`engine/STATE.md`](../engine/STATE.md) — current next-session work item.
