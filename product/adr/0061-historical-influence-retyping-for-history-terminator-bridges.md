# ADR 0061 — Retype history-terminator cross-bridges from `pedagogical_prerequisite` to `historical_influence`

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0122 (Phase 5 production-audit closeout)

## Context

The Phase 5 production audit (T-PHASE-5-AUDIT, S-0104 → S-0120) ran SEP-anchored review across all 71 cross-domain edges authored at S-0075 in `0060_seed_crossbridges_part1.sql`. The audit's full census of cross-bridges (AUDIT-CB at S-0104) found 14 of 71 edges (19.7%) typed as `pedagogical_prerequisite` but verdicted historical-not-pedagogical. The S-0122 closeout's empirical-fortification pass (per [`engine/adr/0059-audit-time-structural-reference-fetching.md`](../../engine/adr/0059-audit-time-structural-reference-fetching.md)) corroborated 9 of these 14 via SEP forward-cross-reference absence; partial corroboration for the remaining 5 (SEP entries link forward to broader-topic entries but not to the specifically-claimed modern targets).

The 14 cross-bridges share a coherent pattern: a service-domain history-terminator node sources a `pedagogical_prerequisite_edge` to a modern-philosophy concept where the SEP-canonical exposition treats the connection as historical genealogy, not as a pedagogical prerequisite. Examples:

- `aristotelian_four_causes → causation`: SEP "Aristotle on Causality" links forward to medieval causation, NOT to the contemporary causation entry which treats the four causes as historical preface.
- `greek_atomism → physicalism`: SEP "Ancient Atomism" does not link forward to physicalism; the contemporary physicalism entry treats Greek atomism as genealogical antecedent, not as pedagogical prerequisite.
- `vienna_circle_logical_positivism → tarskis_t_schema`: SEP "Vienna Circle" links to Tarski (the figure) sociologically; the conceptual prereq for the T-schema is the formal-semantic apparatus, not Vienna Circle context.

The PREDICATE_MANIFEST.md `historical_influence` predicate has been reserved-but-unused since the schema's initial draft: display-only (Discovery-surface annotation), not consumed by traversal / syllabus generation / mastery computation, may form cycles. It is the natural predicate for "the source concept historically influenced the target concept's development" — exactly the relation the 14 mis-typed cross-bridges encode.

The S-0122 closeout's findings report at [`engine/build_readiness/phase_5_production_audit_findings.md`](../../engine/build_readiness/phase_5_production_audit_findings.md) §"Historical genealogy cluster" lists all 14 with fortification outcomes. The audit also surfaced 2 within-service A3-internal historical edges (SVC-E-2 `presocratic_naturalism → aristotelian_four_causes`; SVC-E-3 `aristotelian_four_causes → vienna_circle_logical_positivism`) plus 1 within-mind edge (MIN-E-23 `consciousness → phenomenology` where the target is a school/movement and the connection is tradition-as-context). These 3 are co-scope as part of the same retyping decision.

The retyping is the canonical disposition the Phase 5 production-audit master plan ([`engine/build_readiness/phase_5_production_audit.md`](../../engine/build_readiness/phase_5_production_audit.md) §"Structural reopen pre-flag") anticipated:

> Expected closeout disposition. A fresh ADR memo proposing activation of the reserved-but-unused historical_influence predicate (per PREDICATE_MANIFEST.md) for cross-bridges of historical shape, with retyping of the ~19 affected edges. Likely lands as a product ADR, not engine ADR.

The audit's evidence shows the canonical figure is 14 (cross-bridges) + 2 (within-service) + 1 (within-mind) = 17 retyping candidates, not 19. The pre-flagged threshold (≥10 of 71) is exceeded.

## Decision

**Retype 17 edges from `pedagogical_prerequisite` to `historical_influence`** in a follow-up cleanup migration.

The retyped edges:

### A. Cross-bridges A3 grouping — service-domain history-terminator → modern philosophy (14 edges)

**From `aristotelian_four_causes` (4 edges):**

1. `aristotelian_four_causes → causation` (CB-E-28)
2. `aristotelian_four_causes → essence_metaphysical` (CB-E-29)
3. `aristotelian_four_causes → scientific_explanation` (CB-E-30)
4. `aristotelian_four_causes → humean_regularity_theory` (CB-E-31)

**From `greek_atomism` (3 edges):**

5. `greek_atomism → physicalism` (CB-E-32)
6. `greek_atomism → reductionism_in_science` (CB-E-33)
7. `greek_atomism → mereological_nihilism` (CB-E-34)

**From `scholasticism` (2 edges):**

8. `scholasticism → realism_about_universals` (CB-E-35)
9. `scholasticism → divine_command_theory` (CB-E-36)

**From `renaissance_mechanism` (2 edges):**

10. `renaissance_mechanism → scientific_theory` (CB-E-38)
11. `renaissance_mechanism → scientific_method` (CB-E-39)

**From `vienna_circle_logical_positivism` (3 edges):**

12. `vienna_circle_logical_positivism → falsificationism` (CB-E-41)
13. `vienna_circle_logical_positivism → demarcation_problem` (CB-E-42)
14. `vienna_circle_logical_positivism → tarskis_t_schema` (CB-E-43)

### B. Within-service A3-internal historical edges (2 edges)

15. `presocratic_naturalism → aristotelian_four_causes` (SVC-E-2)
16. `aristotelian_four_causes → vienna_circle_logical_positivism` (SVC-E-3)

### C. Within-mind school/movement target (1 edge)

17. `consciousness → phenomenology` (MIN-E-23)

### Disposition mode: retype, not dual-type

The schema permits multiple edges of different `edge_type` between the same source-target pair. The decision is to **retype** (single edge with `historical_influence` replacing `pedagogical_prerequisite`), not **dual-type** (keep `pedagogical_prerequisite` and add `historical_influence`).

The retype mode reflects the audit's evidence: the verdict was "mis-typed: historical-not-pedagogical," not "additionally historical." Dual-typing would falsely imply both relations are pedagogically load-bearing when the audit shows the pedagogical-prerequisite reading is the structural error.

### Retyping migration

A new migration `0061_retype_historical_influence_crossbridges_part1.sql` authors the 17 retypings:

- DELETE each affected row from `pedagogical_prerequisite_edge`
- INSERT a corresponding row into `historical_influence_edge` (or whatever the schema-table name is for the predicate; PREDICATE_MANIFEST.md is the source of truth on table naming)
- Populate the `evidence` field on each INSERT with the migration's authoring rationale — extracted from the original migration's `teaching_notes` plus the audit's verdict reasoning per [`phase_5_production_audit_findings.md`](../../engine/build_readiness/phase_5_production_audit_findings.md) §"Historical genealogy cluster"

The migration is **not** authored as part of this ADR's adoption — the ADR ratifies the retyping decision; the migration follows in a subsequent build session.

### Layer 2.5 postcondition assertions

Per [ADR 0039 product](../../product/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) Layer 2.5 amendment + [ADR 0055 engine](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5, the retyping migration's contract header includes inline postcondition assertions:

- `SELECT count(*) FROM pedagogical_prerequisite_edge WHERE (source_id, target_id) IN ((...17 pairs...)) :: 0` (verify all 17 retypings landed)
- `SELECT count(*) FROM historical_influence_edge WHERE (source_id, target_id) IN ((...17 pairs...)) :: 17` (verify the inverse)
- `SELECT count(*) FROM pedagogical_prerequisite_edge WHERE source_id IN ('aristotelian_four_causes', 'greek_atomism', 'scholasticism', 'renaissance_mechanism', 'vienna_circle_logical_positivism', 'presocratic_naturalism', 'consciousness') :: <expected-residue>` (verify no over-retyping; the source nodes have other pedagogical_prerequisite edges that should remain; the expected residue is computed at migration authoring time from a count of preserved-edges)

## Consequences

**Modified:**

- 17 rows: `pedagogical_prerequisite_edge` → `historical_influence_edge` retypings (executed in the retyping migration, NOT this ADR)
- [PREDICATE_MANIFEST.md](../seed-graph/migrations/PREDICATE_MANIFEST.md) — the `historical_influence` row's "Status" column moves from `reserved-but-unused` to `active` (or whatever the canonical activation field is)
- [`product/docs/architecture.md`](../docs/architecture.md) "Edge Schema" — note the predicate's now-active status
- The audit's evidence files (crossbridges.md, service.md, mind.md) — add a "Post-closeout disposition: retyped via ADR 0061" annotation to the 17 finding sections

**Display-only semantics preserved.** Per PREDICATE_MANIFEST.md, `historical_influence` is display-only: not consumed by traversal, syllabus generation, or mastery computation. This means:

- Discovery surface (per [ADR 0034](0034-discovery-planning-engagement-triad.md)) MAY annotate "X historically influenced Y" alongside cross-references when surfacing a node; this is a learner-facing affordance, not a structural pedagogical claim.
- The retyping does NOT eliminate the 17 conceptual connections from the graph — they remain visible to learners exploring concept neighborhoods.
- Mastery computation per [ADR 0015](0015-event-sourced-learner-model.md) ignores the predicate — student mastery on, e.g., `causation` is not gated on prior mastery of `aristotelian_four_causes`. This is the canonical pedagogical correction the audit found.
- Syllabus generation (Phase 7 teaching layer per [ADR 0014](0014-sonnet-teaches-opus-reviews.md)) ignores the predicate — the four-causes apparatus does not appear in the prereq chain when a student studies modern causation. The teaching layer MAY surface "this concept developed historically from X" as enrichment, but the structural prereq is not present.

**Cycles permitted, ignored by audit.** Per PREDICATE_MANIFEST.md, `historical_influence` may legitimately form cycles. The audit's cycle-detection (validator soft-warn `cycle_detected`) ignores `historical_influence` rows. This matters because mutual-influence patterns (concept-A influenced concept-B AND concept-B influenced concept-A's later refinement) are common in philosophy and not structural errors.

**No mastery-computation backward-compatibility hack needed.** The retyping happens once; learner data does not yet exist for these 17 edges (Phase 5 seed graph is pre-deployment); no migration of learner-mastery state is required.

**Phase 6 self-correction implications.** The retyping signals to Phase 6 self-correction infrastructure that history-terminator-source edges to modern philosophy are a recurring mis-typing pattern. Phase 6's own audit infrastructure should incorporate the validator soft-warn `historical_node_as_prereq_source` (per [`phase_5_audit_system_input.md`](../../engine/build_readiness/phase_5_audit_system_input.md) Proposal 4) once the node-class tagging schema extension lands.

## Alternatives considered

**Alternative 1 — keep all 17 edges as `pedagogical_prerequisite`.** Rejected. The audit's 14 cross-bridge findings + 2 within-service + 1 within-mind exceed the master plan's pre-flagged ADR-warranting threshold of ≥10 historical-not-pedagogical findings. Keeping the mis-typings would mean (a) syllabus generation and mastery computation propagate a structural pedagogical claim that the SEP-canonical exposition contradicts, and (b) Phase 6 self-correction has to redo the audit pass to surface the same finding.

**Alternative 2 — dual-typing.** Rejected. The audit's verdict was "mis-typed: historical-not-pedagogical," meaning the `pedagogical_prerequisite` reading is the structural error. Dual-typing would falsely imply both relations are pedagogically load-bearing.

**Alternative 3 — defer the retyping to Phase 6+ alongside thinker-overlay work.** Rejected per the no-preemptive-deferral discipline in [CLAUDE.md](../../CLAUDE.md). Foundations land before work that builds on them; Phase 6 self-correction will encounter these edges and propagate their mis-typing structurally if not retyped at Phase 5's closeout. The retyping is also small (17 edges, single migration), well within session budget.

**Alternative 4 — retype only the 9 fortification-corroborated edges; defer the 5 partial-corroboration cases.** Rejected. The partial-corroboration cases (CB-E-35, CB-E-36, CB-E-41, CB-E-43; SCI partial — actually CB-E-35, CB-E-36, CB-E-41, CB-E-43 + CB-E-28's medieval-cross-link) have SEP forward links to broader-topic entries (e.g., scholasticism's `properties` cross-ref; vienna_circle's `popper` cross-ref) but not to the specifically-claimed modern targets. The verdict's "historical-not-pedagogical" reading stands on the within-evidence-file reasoning even when broader-topic links exist. Splitting the retyping creates inconsistency across the cluster and signals that fortification is necessary-and-sufficient evidence when the closeout's reasoning explicitly notes fortification is only one input to the disposition.

## References

- Master plan: [`engine/build_readiness/phase_5_production_audit.md`](../../engine/build_readiness/phase_5_production_audit.md) §"Structural reopen pre-flag"
- Findings report: [`engine/build_readiness/phase_5_production_audit_findings.md`](../../engine/build_readiness/phase_5_production_audit_findings.md) §"Historical genealogy cluster"
- Audit-system-input report: [`engine/build_readiness/phase_5_audit_system_input.md`](../../engine/build_readiness/phase_5_audit_system_input.md) Proposal 4
- Evidence files: [`crossbridges.md`](../../engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md) §A3; [`service.md`](../../engine/build_readiness/phase_5_production_audit_evidence/service.md); [`mind.md`](../../engine/build_readiness/phase_5_production_audit_evidence/mind.md) E-23 / N-2
- Predicate manifest: [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../seed-graph/migrations/PREDICATE_MANIFEST.md) `historical_influence` row
- [ADR 0001 product](0001-pedagogical-edges-not-historical.md) (the structural distinction between pedagogical and historical edges)
- [ADR 0008 product](0008-concept-nodes-not-thinkers.md) (concept-vs-thinker granularity)
- [ADR 0052 product](0052-phase-5-philosophy-subdomain-decomposition.md) (Phase 5 decomposition)
- [ADR 0055 engine](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) (Layer 2.5 postcondition assertions for the retyping migration)
- [ADR 0059 engine](../../engine/adr/0059-audit-time-structural-reference-fetching.md) (the audit-time fortification mechanism)
