# P_4 — Seed graph build (Phase 5)

> Concept-level seed graph across philosophy subdomains. Hundreds of nodes per subdomain. Cross-domain edges first-class. Multiple subdomain sub-sessions run concurrently per the eager-claim discipline; this is the **first natural parallel-work moment** and the **Paperclip orchestration trial moment**.

## Phase scope

Phase 5 populates the schema landed at [`P_1_sql_schema.md`](P_1_sql_schema.md), validated by [`P_2_graph_validation.md`](P_2_graph_validation.md), informed by the survey landed at [`P_3_input_dataset_survey.md`](P_3_input_dataset_survey.md). Per [ROADMAP Phase 5](../ROADMAP.md), each subdomain session writes one `00NN_seed_<subdomain>_partN.sql` migration with `INSERT` statements; sessions run in parallel without merge conflicts because each writes a distinct migration file.

This is one chunk in `build_plan/` because the per-subdomain sessions share scope, workflow, and validator — colocation under one per-phase contract is operationally cleaner than fragmenting into one chunk per subdomain. The per-subdomain working contracts live as enumerated sub-sessions inside this chunk.

## Sub-sessions (the parallel work)

The subdomain sub-sessions per [ROADMAP Phase 5.1](../ROADMAP.md). Each claims its own slot via the eager-claim ritual; each writes its own migration file; each runs `engine/tools/validate.py` independently:

- **5.epistemology** — start here. The deprecated v0.2 prototype was epistemology-focused so judgment is calibrated. SEP article structure, concept inventory, prerequisite edges.
- **5.ethics** — second-priority subdomain.
- **5.metaphysics** — third subdomain.
- **5.mind** — Philosophy of Mind.
- **5.language** — Philosophy of Language.
- **5.science** — Philosophy of Science.
- **5.services** — Service nodes: logic primitives, mathematical prerequisites, history nodes that terminate where they stop affecting comprehension. Settles before cross-domain pass because cross-domain edges may depend on service-node bridging.
- **5.crossdomain** — Cross-domain edges pass. Closes Phase 5. Runs after subdomain interiors are stable; generates edges spanning subdomain boundaries.

ROADMAP Phase 5 enumerates these as `P_3 Epistemology` through `P_9 Cross-domain edges pass` — that internal naming is the per-Phase-5 sub-session enumeration, not a clash with the `build_plan/P_N` chunk numbering. The sub-sessions claim canonical Session IDs (S-NNNN) per the eager-claim ritual; the `5.<subdomain>` shorthand here is for cross-reference within this chunk.

## Output (per sub-session)

A migration file at `product/seed-graph/migrations/00NN_seed_<subdomain>_partN.sql`:

- `INSERT` statements for nodes and edges.
- `graph_version_added` set to the current `settings` counter at session start.
- Explicit `confidence_level` per node (`EXTRACTED | INTERPRETED | SYNTHETIC` per [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md)). First-pass prerequisite edges marked `confidence_level: INTERPRETED` until validated.
- Each node's `provenance` field carries its source attribution.

## Source approach

Per [ROADMAP §5.2](../ROADMAP.md):

- **SEP** as **structural reference only** — concept inventory, cross-references. SEP does not become hosted text per [ADR 0011](../product/adr/0011-no-hosted-copyrighted-material.md).
- **Wikipedia** for accessible summaries (CC BY-SA — permits use with attribution).
- **First-pass prerequisite edges generated via Claude;** mark `confidence_level: INTERPRETED` until validated against learner outcomes or expert review.
- **Phase 4.5 survey output** ([`product/docs/content-strategy.md`](../product/docs/content-strategy.md) "Cross-Domain Reference Inventories — Survey") names the per-domain inventories and any prerequisite-shaped graph priors worth consulting. Sub-sessions consult it as a checklist; specific adoption decisions land as ADRs in-session if they involve non-trivial tradeoffs.

## Per-sub-session migration workflow

Per [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md) (filled out at [`P_2_graph_validation.md`](P_2_graph_validation.md)):

1. Sub-session reads target subdomain's SEP article structure; identifies in-scope concepts at the granularity principle (one mastery state per concept).
2. Sub-session writes a new migration file `product/seed-graph/migrations/00NN_seed_<subdomain>_partN.sql` with `INSERT` statements; sets `graph_version_added` to current settings counter; sets `confidence_level` per node.
3. Sub-session runs `supabase db push`.
4. Sub-session runs `engine/tools/validate.py --validate-only` against the post-push DB.
5. Hard-fails fix in-session before commit.
6. Soft-warns recorded in sub-session `outcome_summary` per category.
7. Sub-session closes; commits the migration file (ENGINE_LOG entry tracked).

## Success criteria (per sub-session)

- Each sub-session closes with zero hard-fails from `engine/tools/validate.py`.
- Soft-warn counts recorded per category in sub-session `outcome_summary`.
- Migration files atomically attributable to the sub-session that wrote them via the sub-session's ENGINE_LOG entry.
- Cross-session schema drift detected by the predicate-manifest audit (the `undeclared_predicate` soft-warn category in `engine/tools/validate.py`).

## Success criteria (Phase 5 close — at the end of all sub-sessions)

- All 8 subdomain sub-sessions closed; cross-domain edges pass committed.
- Concept-level seed graph spans all named subdomains. Hundreds of nodes per subdomain.
- Cross-domain edges first-class — `cross_domain_dependency` predicate populated per [ADR 0007](../product/adr/0007-cross-domain-porosity.md).
- `engine/tools/validate.py` clean against the full graph at Phase 5 close.

## Source documents (boot reads beyond CLAUDE.md auto-load)

Per sub-session:

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 5.
- [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) — the Phase 4.5 survey output.
- [`product/docs/architecture.md`](../product/docs/architecture.md) — node/edge schema, granularity principle.
- [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md) — workflow.
- The target subdomain's SEP article(s) (web-fetched, not in-tree).
- `product/seed-graph/migrations/PREDICATE_MANIFEST.md` — to verify predicate registration before using a new edge type. (Authored by `P_2` Phase 4; the path is forward-pointing until then.)
- `product/seed-graph/migrations/ROUTING.md` — to identify the next migration filename. (Same forward-pointing status.)

## Load-bearing ADRs

[ADR 0001](../product/adr/0001-pedagogical-edges-not-historical.md) (pedagogical edges, not historical), [ADR 0006](../product/adr/0006-domain-agnostic-architecture.md) (domain-agnostic architecture), [ADR 0007](../product/adr/0007-cross-domain-porosity.md) (cross-domain porosity), [ADR 0008](../product/adr/0008-concept-nodes-not-thinkers.md) (concept nodes, not thinkers), [ADR 0011](../product/adr/0011-no-hosted-copyrighted-material.md), [ADR 0016](../engine/adr/0016-graph-construction-needs-live-validation.md), [ADR 0018](../product/adr/0018-flat-domain-tags-community-detection.md), [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md).

## Estimated context budget

Substantive per sub-session: target 60%, cap 70%. Each sub-session reads its target SEP article(s), authors `INSERT` statements at the granularity principle, runs validation, fixes soft-warns. Context-amplification risk is moderate — SEP articles are long, but selective reading at the concept-inventory level is the discipline.

## Session sequencing

Multi-session, parallelizable. The eager-claim ritual prevents collision. Order:

1. **5.epistemology first** — calibration matters; the deprecated v0.2 prototype was epistemology-focused.
2. **5.ethics, 5.metaphysics, 5.mind, 5.language, 5.science** — can run in any order, in parallel where session-scheduling allows.
3. **5.services** — runs after at least one subdomain interior is stable so service-node candidates are visible.
4. **5.crossdomain** — runs last; closes Phase 5.

Total session count: ~8 sub-sessions minimum, more if any subdomain needs partial-closure due to budget.

## Paperclip trial

When two or more subdomain sub-sessions queue up to run in parallel, this is the trial moment for Paperclip orchestration: tickets per subdomain, scheduled heartbeats, atomic dispatch. Decision to commit ([`P_7_teaching_layer.md`](P_7_teaching_layer.md), Phase 7) hinges on this trial's results.

## Open tensions consumed

None directly. The seed authoring may surface domain-specific tensions (e.g., a concept that doesn't fit the granularity principle cleanly); these file under [`product/docs/tensions.md`](../product/docs/tensions.md) per the [tension-resolution discipline](../engine/operations/session-shutdown-sequence.md).

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 5 — full phase scope.
- [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) — survey output consumed by every sub-session.
- [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md) — per-sub-session workflow.
- [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — successor; depends on Phase 5 close.
