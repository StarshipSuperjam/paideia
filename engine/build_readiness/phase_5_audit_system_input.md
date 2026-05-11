# Phase 5 production audit — audit-system input report

> Authored by S-0122 (interactive closeout) per the master plan at [`phase_5_production_audit.md`](phase_5_production_audit.md) §"Forward pointers to closeout" — the audit-system synthesis surface. Pairs with the findings report at [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md).
>
> The Phase 5 production audit's secondary deliverable: aggregate the per-edge / per-node candidate findings into structural recommendations for the audit system itself (validator soft-warns, evidence-field discipline, node-class tagging). The recommendations here are scoped to gate-feasible additions to the validator — extensions that can fire without the live LLM-in-the-loop apparatus the audit itself uses.

## Proposal 1 — `edge_evidence_empty` validator soft-warn (gate-feasible)

**Status.** Pre-listed in master plan §"Audit-system-input proposals" #1. Audit corroborates the master-plan finding.

**Empirical basis.** The `evidence` field on `pedagogical_prerequisite_edge` is universally NULL across all 536 Phase 5 edges (confirmed across all 13 evidence sessions). The audit revealed substantive defects that *would have been visible* in a populated `evidence` field — the 5 contradicted-by-own-prose reversals (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70) all had pedagogical-warrant prose in the migration's `teaching_notes` that argued the opposite direction from the authored edge. Had the `evidence` field been populated with this prose at authoring time, the inconsistency would have been visible without an audit pass.

**Specification.** The soft-warn fires per-edge when:
- The edge's `evidence` field is NULL or empty string, AND
- The edge is a cross-domain bridge (`source.domain ≠ target.domain`)

**Why cross-bridges only.** Within-subdomain edges run cleaner (5.0-21.0% defect rate vs 35.2% for cross-bridges) and their pedagogical justification is often implicit in the parent migration's narrative. Cross-bridges are the high-value population for evidence-field discipline: they bridge curriculum-design choices across subdomain boundaries and the rationale benefits from explicit recording.

**Phase 6+ adoption discipline.** Cross-bridges authored in Phase 6 (self-correction outputs) must populate `evidence`. Backfill of the existing 71 cross-bridges is a separate cleanup pass — likely scope of the structural-reopen migration that retypes the 14 historical-not-pedagogical bridges, which has access to the migration's `teaching_notes` prose as the natural source for the backfill.

**Implementation cost.** Low — `validate.py` already iterates over `pedagogical_prerequisite_edge` rows; the additional `evidence IS NULL` predicate is a one-line check.

**Routing.** GitHub Issue label `enhancement` (validator gate addition).

## Proposal 2 — `discipline_label_node_at_root` refined to two categories (gate-feasible)

**Status.** Pre-listed in master plan §"Audit-system-input proposals" #2. Audit refines.

**Empirical basis.** The audit surfaced TWO distinct shapes of discipline-label issue:

**2a. Sub-discipline-label-with-content** (5 instances across the corpus):
- `bayesian_epistemology` (S-0105 N-8)
- `moral_epistemology` (S-0108 N-4)
- `animal_ethics` (S-0108 N-9)
- `modality` (S-0109 N-4)
- `mereology` (S-0109 N-6)

These are sub-discipline labels within a parent discipline that have crystallized into specific doctrinal clusters with structured options. SEP often treats them as stand-alone entries with substantial content (35K+ words for bayesian_epistemology and moral_epistemology). The Phase 5 decomposition's design treats these as nodes with concept-level granularity; the closeout's recommendation is **accept** the granularity as load-bearing, not flag-as-defect.

**2b. Top-level-discipline-label-as-prereq-source** (3 instances across the corpus):
- `philosophy_of_language` (S-0112 E-6 implicit)
- `philosophy_of_science` (S-0113 N-5 explicit, plus E-2 / E-3 incident edges)
- `political_philosophy` (S-0114 N-5 explicit, plus E-11 incident edge)

These are TOP-LEVEL discipline labels that source foundation-spine `pedagogical_prerequisite` edges to their field's central topics. The closeout's recommendation is **retain with explicit "discipline-as-umbrella" semantics** plus a validator soft-warn that flags any TOP-LEVEL discipline label whose label string matches a canonical subdomain name AND that serves as a `pedagogical_prerequisite_edge.source` to multiple subdomain concepts.

**Specification.** Single validator soft-warn `top_level_discipline_label_as_prereq_source` fires when:
- A node's label string matches a canonical top-level discipline name from a fixed list (`philosophy_of_language`, `philosophy_of_science`, `political_philosophy`, `philosophy_of_mind`, `metaethics`, etc.), AND
- That node sources ≥ 3 `pedagogical_prerequisite_edge` rows, AND
- Those edges' targets span multiple sub-areas of the named discipline

**Why ≥ 3 / multiple sub-areas.** A top-level discipline label sourcing a single internal-coherence edge (e.g., `philosophy_of_mind → mental_state`) is not the problem shape; the problem shape is the foundation-spine pattern where the discipline-label sources prereq edges that fan out to several disconnected sub-areas (the umbrella-as-prereq shape).

**Phase 6+ adoption discipline.** New top-level discipline-label nodes (e.g., `philosophy_of_religion` if readmitted; `philosophy_of_action`; `social_epistemology` at sub-domain scale) trigger this check at validate-time. The fix posture (retain-with-umbrella-semantics) is recorded in the node's `teaching_notes`.

**Implementation cost.** Medium — requires the canonical-discipline-name list and the "multiple sub-areas" predicate (which can use existing `domain` field cardinality on the targets, but the sub-area discrimination beyond `domain` requires either node-class tagging or a label-substring heuristic).

**Routing.** GitHub Issue label `enhancement`.

## Proposal 3 — `prereq_direction_summary_inconsistency` (gate-feasible, NLP-flagged)

**Status.** Pre-listed in master plan §"Audit-system-input proposals" #3 with implementation-cost caveat. Audit corroborates.

**Empirical basis.** 5 of the 8 cross-bridge reversals (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70) have the migration's own pedagogical-warrant prose in the `teaching_notes` arguing the opposite direction from the authored edge. The pattern is shape-detectable: when target.summary contains a structural sentence whose subject is the target-concept and whose object/dependency-clause names the source-concept, the conceptual dependency runs target→source (in NL semantics) but the edge runs source→target. Examples:

- E-63 `propositional_attitude → proposition`: `proposition.summary` says "propositions are the contents of propositional attitudes" — proposition is content, PA is attitude; structural sentence runs proposition-supplies-content-to-PA, so PA depends on proposition.
- E-70 `justice → morality`: `morality.summary` says "morality is the broader normative framework"; structural sentence runs morality-is-broader-than-justice, so justice (specific) depends on morality (broader).

**Specification.** The soft-warn fires per-edge when:
- The edge is a cross-domain `pedagogical_prerequisite_edge`, AND
- The target.summary contains a structural-dependency phrase pattern of shape `<target-name> (is|are) <connecting-phrase> <source-name>` where the connecting-phrase signals broader-category / content-of / property-of-bearer / class-of-position semantics

**Implementation cost.** Medium-high — requires either a curated phrase-pattern list (broader-than, content-of, applies-to, etc.) or a small LLM call against the migration's `teaching_notes`. The phrase-pattern approach is cheaper but produces more false negatives; the LLM-call approach is more accurate but adds dependency.

**Closeout recommendation.** Implement the phrase-pattern approach as a Phase 6 enhancement; promote to LLM-call if false-negative rate proves limiting.

**Routing.** GitHub Issue label `enhancement` + Issue body documents the trade-off; closeout defers implementation choice (phrase-pattern vs LLM-call) to the Phase 6 implementer.

## Proposal 4 — `historical_node_as_prereq_source` (gate-feasible pending node-class tagging)

**Status.** Pre-listed in master plan §"Audit-system-input proposals" #4 with sub-class-tagging-required caveat. Audit corroborates and extends.

**Empirical basis.** 14 cross-bridge edges from service-domain history-terminator nodes (aristotelian_four_causes / greek_atomism / scholasticism / renaissance_mechanism / vienna_circle_logical_positivism) are mis-typed historical-not-pedagogical. Plus 2 within-service edges (presocratic_naturalism → aristotelian_four_causes; aristotelian_four_causes → vienna_circle_logical_positivism). Plus 1 within-mind edge (consciousness → phenomenology) where the school/movement target makes the standard pedagogical_prerequisite framing awkward.

**Specification.** The soft-warn fires per-edge when:
- The edge is `pedagogical_prerequisite_edge`, AND
- The source-node's `node_class` tag (or its label-substring heuristic) matches one of: `history-terminator`, `school-movement`, `thinker-framework`

**Node-class extension.** Requires a new column or tag-set on `node`:
- `history-terminator`: `aristotelian_four_causes`, `greek_atomism`, `scholasticism`, `renaissance_mechanism`, `presocratic_naturalism` (current service-domain history-terminators)
- `school-movement`: `vienna_circle_logical_positivism`, `phenomenology` (and others if a graph-wide pass identifies more)
- `thinker-framework`: `aristotelian_four_causes` (overlaps with history-terminator), `kantian_aesthetic_judgment` (likely), `russells_theory_of_descriptions` (likely)

**Closeout recommendation.** Promote the soft-warn pending the schema extension. The schema extension is a separate ADR (sub-class tagging on node schema). Phase 6 self-correction infrastructure can absorb the schema-extension work as part of its own node-quality-tagging arc.

**Routing.** GitHub Issue label `enhancement` + cross-reference to the schema-extension ADR (TBD; deferred to Phase 6 master plan authoring).

## Proposal 5 — `cross_bridge_pedagogical_direction_inconsistent_with_summary` (gate-feasible, S-0104 candidate)

**Status.** NEW candidate surfaced at S-0104 in the cross-bridges aggregate observations.

**Empirical basis.** Subset of Proposal 3 specifically for cross-bridges. The 5 contradicted-by-own-prose reversal cases (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70) are all cross-bridges. The pattern's discriminator is the cross-domain shape (source and target in different `domain` values).

**Specification.** Identical to Proposal 3 but predicated on `source.domain ≠ target.domain`. Tighter false-positive profile than the general Proposal 3.

**Closeout recommendation.** Merge into Proposal 3 (Proposal 5 is the cross-bridges-only specialization; the validator can ship as Proposal 3 with the cross-bridges-only firing predicate added as a configuration option).

**Routing.** Same Issue as Proposal 3.

## Proposal 6 — `developmental_arc_reversal` (closeout-candidate, NEW)

**Status.** NEW candidate surfaced in S-0112 E-2 (speech_act → performative_utterance), S-0113 E-4 (paradigm → theory_ladenness_of_observation), with related shapes in MIN-E-14 (hard_problem → explanatory_gap) and S-0112 E-10 (deflationary_theory → tarskis_t_schema).

**Pattern shape.** The historical seed observation / antecedent thesis / pre-systematized motivator is authored as DOWNSTREAM of the systematized framework / position / formalization that it motivated. Direction-of-development reversal: the authored edge runs framework → seed-observation, but the canonical SEP-exposition runs seed-observation → framework (Hanson 1958 → Kuhn 1962; Austin 1955 performatives → speech-act framework; Tarski 1933 T-schema → 1970 deflationism).

**Specification.** Hard to gate-implement because the discriminator predicate is "historical-temporal-precedence + conceptual-foundationality." Two candidate heuristics:
- **Citation-year proxy:** If both nodes' `teaching_notes` cite canonical-text years, and the source's earliest canonical-text year postdates the target's earliest canonical-text year, the edge direction is suspect.
- **LLM-flagged:** A small LLM call against both nodes' summaries that judges whether the source-concept is described as motivated-by or extending the target-concept.

**Closeout recommendation.** Defer to Phase 6+ — the heuristic approach has too high a false-positive rate (many sound edges connect later-developed-concepts to their conceptual primitives); the LLM-flagged approach is more accurate but adds dependency. Phase 6 self-correction infrastructure is the natural place to evaluate whether this proposal is worth implementing.

**Routing.** GitHub Issue label `enhancement` + `deferred-phase-6` (new label TBD) + Issue body documents the trade-off.

## Cross-references

- Master plan: [`phase_5_production_audit.md`](phase_5_production_audit.md)
- Findings report: [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md)
- Validator: [`engine/tools/validate.py`](../tools/validate.py)
- [ADR 0042 soft-warn-lifecycle-archive-canon](../adr/0042-soft-warn-lifecycle-archive-canon.md)
- [`engine/operations/soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md)
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md)
