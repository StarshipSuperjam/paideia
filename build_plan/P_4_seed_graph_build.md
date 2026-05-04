# P_4 — Seed graph build (Phase 5)

> Concept-level seed graph across philosophy subdomains. Hundreds of nodes per subdomain. Cross-domain edges first-class. Sub-sessions run unattended via routine-mode per [ADR 0051](../engine/adr/0051-routine-mode-and-engine-loop.md), dispatched against [`engine/session/auto_target.json`](../engine/session/auto_target.json) authored by the S-0045 master plan session.

## Phase scope

Phase 5 populates the schema landed at [`P_1_sql_schema.md`](P_1_sql_schema.md), validated by [`P_2_graph_validation.md`](P_2_graph_validation.md), informed by the survey landed at [`P_3_input_dataset_survey.md`](P_3_input_dataset_survey.md), gated by [`engine/build_readiness/phase_5.md`](../engine/build_readiness/phase_5.md). Per [ROADMAP Phase 5](../ROADMAP.md) and [ADR 0052](../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md), the phase decomposes into 9 subject subdomains plus service nodes plus cross-bridges plus closeout — 16 explicit tasks. Each task writes one or more migrations under the prefix scheme in [`product/seed-graph/migrations/ROUTING.md`](../product/seed-graph/migrations/ROUTING.md) with `INSERT` statements; sub-sessions run sequentially or in parallel per `depends_on` ordering in `auto_target.json` without merge conflicts because each writes distinct migration files.

This is one chunk in `build_plan/` because the per-subdomain sub-sessions share scope, workflow, and validator — colocation under one per-phase contract is operationally cleaner than fragmenting into one chunk per subdomain. The per-subdomain working contracts live as enumerated sub-sessions inside this chunk; the executable contract lives in `engine/session/auto_target.json`.

## Sub-sessions (the routine-mode work)

The 16 sub-sessions per [ROADMAP Phase 5.1](../ROADMAP.md) and [ADR 0052](../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md). Each claims its own slot via the eager-claim ritual; each writes one or more migration files; each runs `engine/tools/validate.py` independently. Subdomains likely too large for one routine session are pre-split at master-plan time per [`auto_target.schema.md:149`](../engine/session/auto_target.schema.md):

**Subject subdomains (9):**

- **P5-01a Epistemology core** — start here. The deprecated v0.2 prototype was epistemology-focused so judgment is calibrated. SEP article structure, concept inventory, prerequisite edges. Migration range `0011-0015`.
- **P5-01b Epistemology specialized** — depends on P5-01a. Migration range `0016-0019`.
- **P5-02a Metaphysics core** — being, identity, causation, time. Migration range `0030-0035`.
- **P5-02b Metaphysics specialized** — depends on P5-02a. Modality, free will, properties, universals. Migration range `0036-0039`.
- **P5-03 Logic** — *philosophical logic*: modality, conditionals, paradox, vagueness, paraconsistent, deontic, intuitionistic, relevance. Migration range `0090-0099`. (Formal-logic primitives belong to P5-10 service nodes.)
- **P5-04a Ethics metaethics+normative** — moral realism, expressivism, virtue, deontological, consequentialist. Migration range `0020-0025`.
- **P5-04b Ethics applied** — depends on P5-04a. Bioethics, environmental ethics, applied moral problems. Migration range `0026-0029`.
- **P5-05 Political philosophy** — authority, justice, rights, liberty, equality, democracy, social contract. Migration range `0100-0109`.
- **P5-06 Aesthetics** — beauty, art, taste, expression, representation, interpretation, criticism. Migration range `0110-0119`.
- **P5-07a Philosophy of mind core** — mental causation, intentionality, perception, personal identity, AI/computational mind. Migration range `0040-0045`.
- **P5-07b Philosophy of mind consciousness/specialized** — depends on P5-07a. Consciousness, qualia, hard problem. Migration range `0046-0049`.
- **P5-08 Philosophy of language** — meaning, reference, sense, speech acts, descriptivism vs. causal theory, semantic externalism. Migration range `0070-0079`.
- **P5-09 Philosophy of science** — scientific method, explanation, confirmation, theory choice, realism vs. anti-realism, philosophy of physics/biology/social sciences. Migration range `0080-0089`.

**Operational tasks (3):**

- **P5-10 Service nodes** — formal-logic primitives, mathematical prerequisites, history terminators. Migration range `0050-0059`.
- **P5-11 Cross-bridges** — depends on all 9 subject subdomain tasks plus P5-10. Cross-domain edges pass. Migration range `0060-0069`. Predicate registry expansion (`cross_domain_dependency` formal introduction) decided in this task.
- **P5-12 Closeout** — Phase 5 close: ENGINE_LOG entry + STATE.md update + [`engine/build_readiness/phase_5_closeout.md`](../engine/build_readiness/phase_5_closeout.md) + optional close ADR.

Sub-session canonical Session IDs (S-NNNN) are claimed at runtime per the eager-claim ritual; the `P5-NN` shorthand here is the task ID in [`engine/session/auto_target.json`](../engine/session/auto_target.json).

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

## Success criteria (Phase 5 close — when all 16 tasks are complete)

- All 16 sub-sessions in [`engine/session/auto_target.json`](../engine/session/auto_target.json) closed at `status: complete` (or HANDOFF entries adjudicate the remainder if `max_sessions: 18` exhausts).
- Concept-level seed graph spans all 9 subject subdomains plus service nodes. Hundreds of nodes per subdomain (subject to subdomain-specific scope per ADR 0052).
- Cross-bridges (P5-11) populated — cross-domain edges first-class per [ADR 0007](../product/adr/0007-cross-domain-porosity.md). Predicate registry includes whatever the cross-bridges session settles on (`pedagogical_prerequisite + disjoint domain[]` continued, OR `cross_domain_dependency` formally introduced).
- `engine/tools/validate.py` clean against the full graph at Phase 5 close (zero hard-fails; soft-warns recorded in archives per [ADR 0042](../engine/adr/0042-soft-warn-lifecycle-archive-canon.md)).
- Closeout (P5-12) lands [`engine/build_readiness/phase_5_closeout.md`](../engine/build_readiness/phase_5_closeout.md) summarizing per-subdomain coverage, soft-warn telemetry, and the predicate registry's final state.

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

[ADR 0001](../product/adr/0001-pedagogical-edges-not-historical.md) (pedagogical edges, not historical), [ADR 0006](../product/adr/0006-domain-agnostic-architecture.md) (domain-agnostic architecture), [ADR 0007](../product/adr/0007-cross-domain-porosity.md) (cross-domain porosity), [ADR 0008](../product/adr/0008-concept-nodes-not-thinkers.md) (concept nodes, not thinkers), [ADR 0011](../product/adr/0011-no-hosted-copyrighted-material.md), [ADR 0016](../engine/adr/0016-graph-construction-needs-live-validation.md), [ADR 0018](../product/adr/0018-flat-domain-tags-community-detection.md), [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md), [ADR 0046](../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) (structural-reference posture for philosophy reference works), [ADR 0051](../engine/adr/0051-routine-mode-and-engine-loop.md) (routine-mode architecture), [ADR 0052](../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) (9-subdomain decomposition).

## Estimated context budget

Substantive per sub-session: target 60%, cap 70%. Each sub-session reads its target SEP article(s), authors `INSERT` statements at the granularity principle, runs validation, fixes soft-warns. Context-amplification risk is moderate — SEP articles are long, but selective reading at the concept-inventory level is the discipline. Subdomains likely too large for one routine session are pre-split at master-plan time per [`auto_target.schema.md:149`](../engine/session/auto_target.schema.md); the discipline is task-sizing pre-execution, not runtime adaptation, because routine sessions have no live context-pressure signal (filed as enhancement Issue #4).

## Session sequencing

Routine-mode dispatches against [`engine/session/auto_target.json`](../engine/session/auto_target.json)'s `depends_on` graph:

1. **P5-01a Epistemology core** — anchor; no deps. Calibration matters; the deprecated v0.2 prototype was epistemology-focused.
2. **P5-01b Epistemology specialized** — depends on P5-01a.
3. **P5-02a/b Metaphysics, P5-03 Logic, P5-04a/b Ethics, P5-05 Political philosophy, P5-06 Aesthetics, P5-07a/b Philosophy of mind, P5-08 Philosophy of language, P5-09 Philosophy of science, P5-10 Service nodes** — depend on P5-01a only; parallel-eligible after the epistemology anchor lands.
4. **P5-11 Cross-bridges** — depends on all 9 subject subdomain tasks plus P5-10.
5. **P5-12 Closeout** — depends on P5-11.

Total task count: 16 explicit. `max_sessions: 18` (count + 2 for HANDOFF retries).

## Paperclip status

Rejected at S-0044 (per [ADR 0051](../engine/adr/0051-routine-mode-and-engine-loop.md) Alternatives Considered). Routine-mode replaces the planned Paperclip trial; Phase 7 commit-decision is moot because the architecture is already chosen.

## Open tensions consumed

None directly. The seed authoring may surface domain-specific tensions (e.g., a concept that doesn't fit the granularity principle cleanly); these file under [`product/docs/tensions.md`](../product/docs/tensions.md) per the [tension-resolution discipline](../engine/operations/session-shutdown-sequence.md).

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 5 — full phase scope.
- [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) — survey output consumed by every sub-session.
- [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md) — per-sub-session workflow.
- [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — successor; depends on Phase 5 close.
