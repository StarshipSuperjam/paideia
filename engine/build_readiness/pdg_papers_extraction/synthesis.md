# Synthesis — integrated clusters by Paideia surface

> **Phase D output.** Source inputs: `extraction_paper_1.md`, `extraction_paper_2.md`, and the five `lens_sweep_*.md` files. Total ~330 distinct findings across 66 sub-concerns; 100% coverage with zero justified absences.
>
> **Clustering rule:** by Paideia surface affected, not by claim category. Findings touching the same surface merge into one integrated proposal. The user's requirement — "an integrated finished product, not a line of parallel good measures" — is what this synthesis defends.
>
> **Tier partition:** A (substrate redesign — actionable now, current graph is materially under-modeled), B (authoring discipline — actionable now), C (existing-anti-bias-mechanism extension), D (Phase 7+ teaching architecture), E (Phase 7+ deployment governance).

## Top-level findings before clusters

1. **The current Paideia graph is materially under-modeled at the substrate level.** Two edge types vs the papers' enumerated ~10–12. No confidence model. No provenance per edge. No misconception encoding. No threshold-concept tagging. No node-type taxonomy. No audience/granularity/equity metadata. No goal-relative parameterization. No version history. The papers describe a property-graph; the current schema is a near-flat directed multigraph.
2. **Goal-relativity is the master organizing principle across pedagogy, substrate, and LLM integration.** Backward design (L2.3), path selection (L2.13), edge-necessity (L1.3), and cognitive load (L2.11) all reduce to the same requirement: every pedagogical decision is goal-relative. The single greatest risk in any teaching-layer build is treating edges as goal-independent.
3. **Contestability is atomic, not piecemeal.** Confidence (L1.4) + provenance (L1.5) + counterexamples (L1.7) + version history (L1.14) form a single governance substrate. Adding any one without the others produces unmoored data. The Substrate lens-sweep, the Adversarial lens-sweep, and the Evaluation lens-sweep all converge on this finding independently.
4. **Two distinct bias surfaces require two distinct mechanisms.** The existing Paideia anti-bias mechanism (strip source-identity at the LLM serialization boundary) operates on a subset of the LLM-mediated bias surface. The papers reveal a second surface — **graph-topology bias** — that is wholly uncovered. The existing mechanism cannot be retrofitted; a parallel graph-authoring-time mechanism is required.
5. **The no-silent-mutation rule applies to all five services in the recommended architecture.** This is the same load-bearing pattern as Paideia's existing routine-mode scope-lock. The build-apparatus discipline generalizes cleanly to the teaching-layer architecture; the existing machinery is the existence proof.
6. **Graph-validity evaluation is epistemically prior to and funds learner-outcome evaluation.** Paideia's current SQA census is implicitly phase 1 of a longitudinal validity study — but is not framed that way. Reframing the SQA discipline as predictive-validity tracking is actionable now and dramatically increases its downstream value.
7. **Schema fields stratify by lifecycle: authoring-time / review-time / runtime-adaptive.** Mixing these in single tables creates write-contention and blurs the boundary between graph structure and learner model. Runtime-adaptive fields belong in a separate high-write table.
8. **Case-study and Mermaid diagram sections are denser sources of substrate claims than explicit schema tables.** This is a methodological observation: future deep extractions should not stop at the schema tables. The lens-sweep safety-net pass caught material the section-sequential pass under-tagged.

## Cluster index

| # | Title | Tier | Approx Issues |
|---|---|---|---|
| 1 | Contestability substrate (per-edge) | A | 1 |
| 2 | Edge-type taxonomy expansion + three-relation layered separation | A | 1 |
| 3 | Goal-relative parameterization (learning_outcomes table + edge-outcome necessity) | A | 1 |
| 4 | Node schema redesign (typology + threshold + audience + granularity + equity metadata + assessment + misconception linkage) | A | 1 |
| 5 | Misconception sub-graph encoding (extends C2 + C4) | A | 1 |
| 6 | Backward-design + Decoding-the-Disciplines authoring discipline | B | 1 |
| 7 | Graph predictive-validity extension to SQA discipline | B | 1 |
| 8 | Graph-topology bias mitigation (augments existing anti-bias) | C | 1 |
| 9 | Instructional-spine architecture (foundational Phase 7+ ADR) | D | 1 |
| 10 | Prompt template discipline + content-store | D | 1 |
| 11 | Four sample workflows + role-checkpoint partitioning | D | 1 |
| 12 | Scaffolding fade trajectory + learner-state schema | D | 1 |
| 13 | Alternative-entry-route support + pluralism reserve | D | 1 |
| 14 | LLM-mediated bias mitigation (output side; parallel to existing input-strip) | E | 1 |
| 15 | Privacy / FERPA / NIST alignment + override logging + transparency reports | E | 1 |
| 16 | Learner-outcome evaluation infrastructure | E | 1 |
| 17 | Anomalous routing detection + three-way disambiguation | E | 1 |

**Total: 17 integrated clusters → 17 candidate Issues.** Tier A (substrate) is most consequential and should land in dependency order: 1 → 2 → 4 → 3 → 5. Tiers B + C are immediately actionable in parallel. Tiers D + E are Phase 7+ but architectural decisions made now constrain Phase 6 design.

---

## Tier A — Substrate redesign (current graph is materially under-modeled)

### Cluster 1 — Contestability substrate (per-edge)

**Paideia surface:** `product/seed-graph/` edges schema; new product ADR; new validator soft-warn.

**Sub-concerns integrated:** L1.4 (confidence 3-source), L1.5 (provenance per edge), L1.7 (counterexamples), L1.14 (version history per edge), L4.9 (contestability), L4.10 (opaque automation — partial), L3.9 (no-silent-mutation — partial).

**Why integrated, not parallel:** The substrate lens-sweep cross-cutting observation 1 stated this directly: "every contestable claim requires three concurrent properties: confidence + provenance + counterexamples." The adversarial lens-sweep cross-cutting observation 1 restated it: "single governance substrate serves multiple sub-concerns." These four schema elements are not independent features — they form one governance layer. Adding confidence without provenance produces an unjustified number; adding provenance without counterexamples produces a one-sided record; adding either without version history loses the audit trail.

**Integrated mechanism:** One product ADR + one migration adding the following columns to the edges table:

- `expert_confidence` — enum: `low` / `medium` / `high` (default `low`)
- `trace_confidence` — float 0–1, nullable until learner data exists
- `llm_confidence` — float 0–1, populated when an edge is LLM-proposed
- `disagreement_flag` — boolean (true when expert / trace / llm scores diverge beyond threshold)
- `provenance` — jsonb with required keys: `source_text`, `course_context`, `version`, `reviewer`, `rationale`
- `counterexamples` — jsonb array (each entry: `description`, optional `evidence_link`)
- `version` — integer, monotonically increasing per edge
- `review_status` — enum: `approved` / `pending_review` / `rejected` / `provisional`
- `last_reviewed` — timestamp

Plus a graph-versions table linking version identifiers to active edge/node sets per course/cohort (per L1.14).

Validator soft-warn: any edge with `expert_confidence: high` AND empty `counterexamples` AND empty `provenance.rationale` is flagged as an unguarded high-confidence claim.

**Existing Paideia surface to reuse:** None — this is net-new substrate. The closest existing pattern is the build-apparatus ADR-tracked decision discipline; the contestability substrate is its data-layer analog.

**Contributing claims (representative):** `paper_2:L82` (3-source confidence model); `paper_2:L83` (5-field provenance record); `paper_2:L81` (counterexamples as required edge field); `paper_1:L122` (version history table row); `paper_1:L162` (mitigation framing: "encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict").

**Dependency:** None — this is foundational and lands first.

---

### Cluster 2 — Edge-type taxonomy expansion + three-relation layered separation

**Paideia surface:** `product/seed-graph/` edges schema; new product ADR (likely two: edge-type expansion + relation-layering policy); migration retyping the 516 existing `pedagogical_prerequisite` edges; routing-layer validator check.

**Sub-concerns integrated:** L1.1 (edge type taxonomy), L1.10 (node-type taxonomy — partially; full coverage in Cluster 4), L1.2 (three-relation layered separation).

**Why integrated, not parallel:** L1.1 and L1.2 are interdependent — the controlled vocabulary of `edge_type` must accommodate the three-relation layering (pedagogical / conceptual / historical) AND the within-pedagogical-layer sub-types (hard prereq / soft prereq / bridge / etc.). Splitting them risks the two ADRs contradicting each other on whether `conceptual_relatedness` is an edge type or a separate layer. The substrate lens-sweep found seven distinct edge semantics in Paper 1 alone plus three more in Paper 2 (`supports`, `example-of`, `assessed-before`). Per the cross-cutting observation that case-study diagrams reveal more than schema tables, the Kant/phenomenology Mermaid diagram also implies a `warning_note` or `misuse_risk` edge attribute ("optionally, potentially misleading if overextended") — which folds into Cluster 1's `counterexamples`.

**Integrated mechanism:** One product ADR establishing:

1. **Relation layering** (the structural separation):
   - `pedagogical_dependence` — current `pedagogical_prerequisite` becomes a sub-type within this layer.
   - `conceptual_relatedness` — NEW third layer (Paideia currently has only pedagogical + historical).
   - `historical_influence` — existing layer (ADR 0061 product unchanged).
   - Routing rule (validator soft-warn): any teaching-layer query asking for "prerequisites of X" must filter to `pedagogical_dependence` edges only. Cross-layer traversal must be explicit.

2. **Edge-type controlled vocabulary** (per layer):
   - Within `pedagogical_dependence`: `hard_prerequisite`, `soft_prerequisite`, `helpful_bridge`, `co_requisite`, `contrastive_link`, `misconception_remediation`, `example_of`, `supports`, `assessed_before`, `unlearning_required_before`
   - Within `historical_influence`: `influenced_by`, `received_via`, `reacted_against` (the existing 17 edges retype as `influenced_by` by default)
   - Within `conceptual_relatedness`: `affinity_with`, `contrasts_with`, `same_problem_family`

3. **Edge-type as enum, not free text** (per `paper_2:L80–81`). Postgres enum or controlled-vocabulary lookup table.

Migration: existing 516 `pedagogical_prerequisite` edges retype to **`soft_prerequisite`** by default within the new layer system — NOT `hard_prerequisite`. Per `paper_1:L162`, experts systematically overstate necessity; defaulting to the most dangerous value inverts the epistemically correct prior. Edges upgrade to `hard_prerequisite` only after SQA validation with learner-trace evidence, not via mass retyping (adversarial review E.2.1 + E.11.1). Add a complementary validator soft-warn: any edge with `edge_type: hard_prerequisite` AND `expert_confidence: low` (the C1 default) is flagged as a "provisional hard prerequisite — requires validation before use in routing". The SQA census already produces evidence about which soft-prerequisites are actually hard — that evidence informs upgrades in a follow-up migration.

**Existing Paideia surface to reuse:** ADR 0061 product's `historical_influence` predicate split. The new ADR extends ADR 0061 by adding the missing third layer (`conceptual_relatedness`) and the sub-typing within `pedagogical_dependence`.

**Contributing claims (representative):** `paper_1:L22–26` (PDG-vs-influence-map comparison table with 6 edge semantics); `paper_1:L116–117` (schema table with 7 edge semantics + layered historical_influence); `paper_2:L15` (6 edge types in definitions, including `supports`, `example-of`, `assessed-before`); `paper_2:L19` (explicit three-relation triple); `paper_1:L31` (separate layers rule); `paper_2:L64` (Saussure/Derrida worked example showing the three-layer distinction in operation).

**Dependency:** Independent of Cluster 1 (can land in parallel) but the edge migration is cleaner if Cluster 1's per-edge confidence + provenance columns exist first, so each retyped edge can be authored with `provisional` confidence pending SQA re-validation.

---

### Cluster 3 — Goal-relative parameterization

**Paideia surface:** `product/seed-graph/` — new `learning_outcomes` table + `edge_outcome_necessity` many-to-many junction; major product ADR; teaching-app path-selector contract.

**Sub-concerns integrated:** L1.3 (goal-relative dependency strength), L2.3 (backward design ordering), L2.13 (goal-relative path selection).

**Why integrated, not parallel:** This is the deepest single substrate change in either paper. The substrate lens-sweep cross-cutting observation 2 named it explicitly: "the same edge has a different meaning depending on learning outcome." The pedagogy lens-sweep cross-cutting observation 1 called it the master organizing principle. The same Kant/Husserl edge is `required` when the goal is "compare Husserl and Kant" and `optional` when the goal is "explain phenomenological description." Edge type alone cannot express this; necessity must be parameterized by `learning_outcome`.

**Integrated mechanism:** One product ADR + one migration:

1. New `learning_outcomes` table: `id`, `outcome_text`, `disciplinary_domain`, `granularity` (introductory / analytical / comparative-research as a starting taxonomy), `course_context`, `created_by`, `version`.

2. New `edge_outcome_necessity` junction table: `edge_id` (FK), `outcome_id` (FK), `necessity_level` (enum: `required`, `recommended`, `historical_contextual_only`), `confidence_for_outcome` (enum), `rationale_for_outcome`.

3. Edge schema gains an optional `default_necessity_level` for graph-traversal queries that don't specify an outcome (defaults to `recommended`, never `required`, because per Paper 1 case-study evidence experts systematically overstate necessity).

4. Path-selector contract: `get_path(target_node_id, learning_outcome_id, learner_state)` is the canonical Phase 7+ API signature. A call without `learning_outcome_id` must explicitly opt into the default-necessity traversal and log a soft-warn that goal-relative selection was bypassed.

5. Validator soft-warn: any edge marked `default_necessity_level: required` is reviewed quarterly against goal-specific overrides — if all outcomes that traverse this edge classify it `required`, the default is justified; otherwise the default is downgraded.

**Existing Paideia surface to reuse:** The closest existing pattern is the SQA census's per-edge evidence collection — that evidence can feed `confidence_for_outcome` when SQA shards are tagged with a learning-outcome context.

**Contributing claims (representative):** `paper_1:L110` (construction principle "dependency claims are meaningful only relative to desired performances"); `paper_2:L62` ("the pedagogical dependency path is therefore goal-relative, whereas the influence path is not"); `paper_2:L81 (edge schema table)` (`necessity_level` as a required field); `paper_1:L79` (Kant/Husserl case study demonstrating goal-relative variation).

**Dependency:** Cluster 1 (confidence + provenance per outcome necessity) and Cluster 2 (edge-type controlled vocabulary) should land first so the junction table inherits the substrate. Cluster 3 is the most ambitious substrate change and likely warrants its own session.

---

### Cluster 4 — Node schema redesign

**Paideia surface:** `product/seed-graph/` nodes schema; 1-2 product ADRs; migration; new validator soft-warns for required field population.

**Sub-concerns integrated:** L1.6 (provenance per node), L1.9 (threshold-concept tag), L1.10 (node-type taxonomy), L1.11 (audience tags), L1.12 (granularity), L1.13 (equity metadata), L1.16 (assessment linkage), L2.1 (threshold concepts as primitives), L4.13 partial (graph-topology bias mitigation via tradition labels — full coverage in Cluster 8).

**Why integrated, not parallel:** The pedagogy lens-sweep finding for L2.1 confirmed: "the Paideia graph has no node-type field… adding one — even just `threshold_concept` vs `bridge_concept` vs `background` — is the minimum needed before Phase 7 teaching logic can make principled routing decisions." The substrate lens-sweep showed that the same eight-field node redesign (`node_type`, `disciplinary_domain`, `granularity`, `threshold_concept?`, `canonical_sources`, `approved_examples`, `misconceptions`, `assessment_items`, `mastery_evidence`, `accessibility_notes`) appears across L1.6, L1.9, L1.10, L1.11, L1.12, L1.13, L1.16. The papers treat this as one schema authoring pass, not seven. Splitting would force seven sequential migrations on the same table.

**Integrated mechanism:** One product ADR (or two if equity-metadata warrants separate ADR-tracked deliberation — see Cluster 8) + one migration adding the following columns to the nodes table:

- `node_type` — enum: `threshold_concept`, `bridge_concept`, `disciplinary_practice`, `text_excerpt`, `historical_context`, `misconception`, `comparative_lens`, `assessment_task`
- `disciplinary_domain` — text (e.g., `philosophy`, `literary_theory`, `history`)
- `granularity` — enum: `coarse`, `medium`, `fine`
- `is_threshold_concept` — boolean (subset of `node_type` for fast filtering; or fold into `node_type`)
- `audience_tags` — text array (intro / intermediate / advanced / majors / non-majors / multilingual_cohort)
- `canonical_sources` — jsonb array of citation objects
- `approved_examples` — jsonb array (curated examples LLM may use)
- `misconceptions` — jsonb array (lightweight encoding — see Cluster 5 for full misconception-node treatment)
- `assessment_items` — jsonb array OR FK to an assessments table (FK preferred for analytics)
- `mastery_evidence` — text/jsonb (what counts as evidence of mastery)
- `accessibility_notes` — text
- `assumed_background` — text array
- `jargon_load` — enum: `low`, `medium`, `high`
- `cultural_specificity` — text (what cultural background this node assumes)
- `tradition_label` — text (e.g., `Western_analytic`, `Continental`, `Postcolonial`) — see Cluster 8 for the strip-at-LLM-boundary discipline

Validator soft-warns:
- Any node lacking `node_type` after migration: hard-fail until backfilled.
- Any `threshold_concept` node lacking `assessment_items`: soft-warn (threshold nodes must have direct diagnostics per `paper_1:L136`).
- Any node lacking `cultural_specificity` populated: soft-warn (equity metadata gate).

**Existing Paideia surface to reuse:** The current SQA census's C2/C3 categories (stale citations / jargon-gated) already collect adjacent data that could populate `canonical_sources` and `jargon_load` retroactively. SQA findings feed the node-schema backfill.

**Contributing claims (representative):** `paper_1:L114–123 (schema table)` (the densest single source — 7 schema dimensions enumerated); `paper_2:L80 (node schema table)` (10 required node fields); `paper_1:L121` (equity metadata: assumed background, jargon load, cultural specificity); `paper_1:L160` (cultural-bias risk; "PDGs can make it visible if instructors deliberately tag nodes for assumed background, cultural specificity, and alternatives").

**Dependency:** Independent of Clusters 1-3 (can run in parallel) but the migration's row count (380 nodes) makes it a session-sized work unit on its own.

---

### Cluster 5 — Misconception sub-graph encoding (extends C2 + C4)

**Paideia surface:** `product/seed-graph/` — new `misconception` node type (already in Cluster 4's `node_type` enum) + new edge types `common_misconception_about` and `unlearning_required_before` (both already in Cluster 2's edge-type vocabulary); product ADR for misconception encoding semantics; Phase 7+ teaching-app detect-remediate-retest state machine.

**Sub-concerns integrated:** L1.8 (misconception encoding), L2.6 (misconception remediation), L2.7 (unlearning commonsense meanings).

**Why integrated, not parallel:** The substrate lens-sweep cross-cutting observation 4 made the integration explicit: "Misconception encoding requires both node-type and edge-type additions — neither alone is sufficient." The full misconception sub-graph requires (a) misconception node type (Cluster 4), (b) `common_misconception_about` edge type (Cluster 2), (c) `unlearning_required_before` edge type (Cluster 2). Without all three, the system cannot distinguish "student lacks concept Y" from "student has active misconception X about Y" — and these states require different teaching responses. The pedagogy lens-sweep cross-cutting observation 2 stated the consequence: "the recommender must implement a detect-remediate-retest state machine, separate from the standard prerequisite-check-and-advance loop."

**Integrated mechanism:** One product ADR establishing:

1. **Two-level misconception encoding.** Lightweight: `misconceptions` field on each target node (jsonb array of short descriptions — populated in Cluster 4). Full: standalone misconception nodes with `common_misconception_about` edges → target concept node, and `unlearning_required_before` edges from the target concept's learning task → the misconception node.

2. **Three named representative misconceptions to seed the corpus** (from `paper_1:L126`): "phenomenology = introspection", "deconstruction = anything goes", "historical perspective = sympathy with the past". Plus the five Corrigan unlearning targets (text / meaning / context / form / reading) from `paper_2:L42` and the historiographic presentism target from `paper_2:L64`.

3. **Authoring discipline (feeds into Cluster 6):** every expert-authored target node must include at least one `misconceptions` entry naming the folk or commonsense meaning students bring in. This is the L4.2 expert-blind-spot mitigation.

4. **Phase 7+ teaching-app state machine** (deferred to Cluster 11, but the substrate must support it now): detect-via-diagnostic → remediate-via-unlearning-sequence → re-test → advance. Distinct state-machine from prerequisite-check-and-advance.

**Existing Paideia surface to reuse:** None — the current graph has no misconception encoding whatsoever.

**Contributing claims (representative):** `paper_1:L43` (unlearning-required-before as a distinct dependency type); `paper_1:L126` (three named misconception examples + rationale); `paper_2:L15` (`common-misconception-about` edge type); `paper_2:L80` (misconceptions as required node field); `paper_2:L186` (false prerequisite as silent path-changing failure — schema implication: learner state must distinguish missing-concept from active-misconception).

**Dependency:** Cluster 2 (edge types) AND Cluster 4 (node-type enum) must land first — this cluster requires both.

---

## Tier B — Authoring discipline (actionable now)

### Cluster 6 — Backward-design + Decoding-the-Disciplines authoring discipline

**Paideia surface:** New ops doc `engine/operations/pdg-authoring-discipline.md` (or `product/operations/`); extension to existing seed-authoring ops; possibly a product ADR formalizing the methodology.

**Sub-concerns integrated:** L2.2 (Decoding the Disciplines bottleneck identification), L2.3 (backward design), L4.2 (expert blind spot — Decoding interview is the mitigation), L1.12 (granularity — Decoding informs granularity decisions).

**Why integrated, not parallel:** All four sub-concerns describe the same authoring sequence: outcomes → bottleneck identification → granularity choice → node draft → edge draft → assessment attachment. The papers treat this as one workflow per `paper_1:L110–112`.

**Integrated mechanism:** New ops doc specifying the authoring sequence:

1. **Define target learning outcomes BEFORE drafting any nodes.** Outcome taxonomy at minimum three levels (introductory / analytical / comparative-research). Per `paper_2:L66 (workflow diagram)`: the outcome is step A, before any node seeding.
2. **Bottleneck identification via Decoding interview or prior student-work analysis.** Every `hard_prerequisite` edge requires evidence from one of: (a) Decoding-the-Disciplines-style interview, (b) prior student performance data showing bottleneck behavior, (c) explicit expert rationale with `expert_confidence: low` until validated.
3. **Granularity at the level of teachable, assessable units** (per `paper_2:L202`). Granularity audit on existing 380 Paideia nodes flags those that are too coarse (whole authors) or too fine (sub-distinctions that don't survive as teachable units).
4. **Novice-translation step:** every expert-authored node includes at least one `misconceptions` entry naming the folk/commonsense meaning (L4.2 + L2.7 mitigation).
5. **Default confidence is `low` for newly authored prerequisite edges** in a humanities PDG until validated with learner data (per `paper_1:L162` case-study evidence that experts systematically overstate necessity).

**Existing Paideia surface to reuse:** Extends current seed-authoring discipline. The SQA census methodology (S-0165 audit-the-auditor check confirmed methodology) is the empirical-refinement side of the cycle; the Decoding/backward-design step is the missing front-end.

**Contributing claims (representative):** `paper_1:L110–112` (six-stage construction workflow); `paper_2:L66 (workflow diagram)` (outcome-first sequencing); `paper_1:L162` (expert blind spot mitigation); `paper_2:L202` (granularity rule).

**Dependency:** None — this is operational discipline, no schema changes required. Can land before or in parallel with Tier A.

---

### Cluster 7 — Graph predictive-validity extension to SQA discipline

**Paideia surface:** Extend `engine/operations/seed-qa-discipline.md` (or wherever SQA is documented); product ADR adopting predictive-validity framing; SQA evidence template extension.

**Sub-concerns integrated:** L5.2 (graph predictive validity), L5.9 (validity criteria for the graph itself), L5.7 (iterative cohort refinement — partial; full version is Phase 7+).

**Why integrated, not parallel:** The evaluation lens-sweep cross-cutting observation 1 made the integration explicit: "Graph validity evaluation precedes and funds learner-outcome evaluation… Paideia's current SQA census is implicitly phase 1 of a longitudinal validity study." Reframing the SQA discipline as predictive-validity tracking is one operational change that addresses three sub-concerns.

**Integrated mechanism:** Extend the SQA evidence template with four new fields per audited edge:

1. **`predicted_difficulty_level`** — auditor's prediction of which edge type is empirically right (hard / soft / bridge / etc.). Stored at SQA time so Phase 7+ learner data can falsify it.
2. **`inter_rater_agreement`** — when two auditors score the same edge, record agreement. Disagreements are themselves a validity signal.
3. **`disagreement_topic_cluster`** — when defects are found, cluster by subject area (philosophy / literary theory / history / etc.) rather than only aggregate. High-defect-concentration in a single topic signals systematic miscalibration there.
4. **`revision_rate`** — after expert re-review, track how often the initial classification was revised. Per `paper_2:L204`.

Combine with Cluster 1's `disagreement_flag` field on edges: an edge with `disagreement_flag: true` is automatically queued for higher-cohort-priority validation in Phase 7+.

**Existing Paideia surface to reuse:** Current SQA census (shards 01-19, of which 01-08 are complete at S-0169). Add the four new evidence fields to the shard scoring template. Findings already collected in shards 01-08 can be retroactively re-scored where possible.

**Contributing claims (representative):** `paper_2:L204` (four graph-validity metrics named); `paper_1:L25 (validity criterion table cell)` (better learning, transfer, reduced bottlenecks, assessment alignment); `paper_1:L149` (iterative DBR + expert review + learner validation); `paper_1:L162` ("revise them when learners succeed through routes the graph did not predict").

**Dependency:** None — operational, applies to existing SQA discipline. Most leveraged when Cluster 1 (per-edge confidence + provenance) lands so SQA evidence can populate the new edge fields directly.

---

## Tier C — Existing-anti-bias-mechanism extension

### Cluster 8 — Graph-topology bias mitigation

**Paideia surface:** Extension to existing memory drawer `feedback_anti_bias_implementation_discipline.md`; new product ADR (governance category); new ops doc for graph-canon census; integration with Cluster 4's equity metadata + tradition labels.

**Sub-concerns integrated:** L4.1 (canon bias), L4.13 (existing-mechanism intersection — AUGMENTS + REINFORCES + 1 CONFLICT resolution + 3 GAPS), L4.12 (pluralism in humanities dependencies), L4.5 (anti-pathologizing — partial; full version is Cluster 14 for LLM-output side).

**Why integrated, not parallel:** The adversarial lens-sweep L4.13 produced a structured assessment of the existing Paideia anti-bias mechanism (`feedback_anti_bias_implementation_discipline.md` + `feedback_audit_llm_inputs_for_bias.md`):

- **AUGMENTS** — Papers identify two new attack surfaces the existing mechanism does not cover: (a) graph-topology bias (canon hardening in topology, before any LLM interaction) and (b) LLM output-side bias (separate cluster — Cluster 14).
- **REINFORCES** — Same design philosophy (structural patterns not enumerated tokens; hold discipline in mechanism's own corpus; audit for bias-contaminating fields) applies cleanly at the graph layer.
- **CONFLICT** — Named tradition labels (recommended by papers) vs strip-identity-cues (existing mechanism's philosophy). Resolution: store `tradition_label` in the DB for human-facing contestation and audit; strip or genericize at the LLM serialization boundary (same boundary the existing mechanism already operates on). Two mechanisms can co-exist.
- **GAPS** — Graph topology not in scope of existing; LLM output bias not in scope of existing; subgroup-differential routing not in scope of existing.

This cluster addresses ONE of those new surfaces (graph topology); Cluster 14 addresses the other.

**Integrated mechanism:** One product ADR + one ops-doc extension + one memory drawer extension:

1. **Memory drawer extension** to `feedback_anti_bias_implementation_discipline.md`: name the two surfaces explicitly; the existing mechanism covers (subset of) surface 2; surface 1 (graph topology) requires a parallel mechanism.

2. **Product ADR:** Graph-topology bias policy. Requires:
   - Every node representing a thinker / tradition / text from a single disciplinary lineage carries a `tradition_label` (Cluster 4 schema field).
   - Every `hard_prerequisite` edge with high `canonical_importance` requires an explicit `alternative_routes` reference (entries in `entry_route_type` per Cluster 13) — at minimum one alternative entry route must be enumerated, or the absence must be explicitly justified.
   - LLM serialization boundary STRIPS `tradition_label` before context-injection (resolution of L4.13 CONFLICT). Same boundary the existing mechanism operates on; same mechanism extended.

3. **New ops doc:** Graph-canon census discipline. Periodic count of nodes by `tradition_label` affiliation; flag traditions appearing only as required prerequisites and never as alternative paths. Cadence: at every health-check audit (per existing health-check ADR 0057).

4. **Validator soft-warns:** node lacking `tradition_label`; node with `tradition_label` set but `audience_tags` lacking `multilingual_cohort` or `alternative_route_available`.

**Existing Paideia surface to reuse:** The existing anti-bias serialization boundary becomes the dual-layer enforcement point — strips both source-identity (existing) AND tradition labels (new) before LLM context injection. The structural-patterns-not-enumerated-tokens posture continues at the graph layer.

**Contributing claims (representative):** `paper_1:L160` (canonical-route gatekeeping risk; "PDGs can make it visible if instructors deliberately tag nodes for assumed background, cultural specificity, and alternatives"); `paper_2:L188` ("store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase"); `paper_2:L206` ("Are some traditions overrepresented as 'required prerequisites' rather than 'one valid route'?" — graph census criterion); `paper_1:L160` (all five case studies demonstrate the canonical-prerequisite-overstatement pattern).

**Dependency:** Cluster 4 (schema must carry `tradition_label` + `audience_tags`) must land first. The ADR itself can be drafted in parallel.

---

## Tier D — Phase 7+ teaching architecture

### Cluster 9 — Instructional-spine architecture (foundational ADR)

**Paideia surface:** Large product ADR establishing teaching-layer architectural invariants; Phase 7+ master plan input.

**Sub-concerns integrated:** L3.1 (instructional-spine-vs-adaptive-interface), L3.2 (five-service architecture), L3.7 (hallucinated-structure risk — its structural mitigation IS the spine), L3.9 (no-silent-mutation rule), L3.10 (pre-registered edit policies), L3.11 (LLM scoring as triage not arbiter), L3.12 (model as critic not judge).

**Why integrated, not parallel:** The LLM lens-sweep cross-cutting observation 2 stated the integration directly: "Instructional spine = hallucination control. L3.1 and L3.7 are the same architectural decision at two levels." The spine-vs-interface partition IS the anti-hallucination mechanism for the structural layer. L3.9, L3.10, L3.11, L3.12 are all instantiations of the same invariant: the LLM operationalizes but does not author. These seven sub-concerns form one foundational architectural ADR, not seven.

**Integrated mechanism:** One product ADR establishing as load-bearing architectural invariants:

1. **PDG = instructional spine (authority); LLM = adaptive interface (operationalization); humans arbitrate.** Stated as a non-negotiable design constraint, not a preference. Quoted directly from `paper_2:L140`.

2. **Five-service architecture:** graph store (PDG + provenance + confidence) / content store (approved excerpts + prompt templates) / LLM orchestration / analytics / review layer. Each service has a defined boundary; LLM orchestration writes only to a candidate-edges staging area, never directly to the graph store.

3. **No-silent-mutation rule across all five services** (per LLM lens-sweep cross-cutting observation 1):
   - Graph store: no write without provenance and version bump.
   - Content store: approved excerpts only.
   - LLM orchestration: JSON-only structured output.
   - Analytics layer: candidate edges go to review queue, not directly to graph store.
   - Review layer: no promotion without sign-off; "store suggestion as unresolved" is a required state.

4. **Pre-registered edit policies:** instructor pre-specifies (a) edit classes a single instructor can approve, (b) edit classes requiring committee sign-off, (c) edit classes the system is prohibited from proposing.

5. **LLM as triage / critic / coach — never judge.** Consequential grading is human-reviewed. Student-facing UI distinguishes `instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved` routing decisions.

6. **Tool-stack evaluation:** Postgres + JSONB + recursive CTEs vs Neo4j dual-layer. Per L3.15 finding, the threshold for graph-store evaluation is the introduction of analytics or trace-informed-revision workflows.

**Existing Paideia surface to reuse:** The build-apparatus no-silent-mutation machinery (routine-mode scope_lock per ADR 0051, eager-claim staging, pre-commit hooks) is the existence proof that Paideia can implement this class of constraint. The teaching-layer architecture is architecturally analogous: the graph is the "allowed_paths" analog; LLM outputs are staged and gated exactly as routine-mode commits are staged and gated.

**Contributing claims (representative):** `paper_2:L6–7` (executive summary spine-vs-interface); `paper_2:L17` (sufficiency test); `paper_2:L140` (canonical division-of-labor statement); `paper_2:L186` (hallucinated-structure risk); `paper_2:L194` (no silent mutation rule); `paper_2:L198` (five-service architecture); `paper_2:L202` (pre-registered edit policies); `paper_2:L190` (model as critic not judge).

**Dependency:** Tier A substrate (Clusters 1, 2, 3, 4, 5) should ideally land first — the spine-vs-interface architecture is only meaningful if the PDG is rich enough to constrain LLM behavior. But the ADR can be drafted in parallel with Tier A.

---

### Cluster 10 — Prompt template discipline + content store

**Paideia surface:** New ops doc `engine/operations/prompt-template-discipline.md`; content-store schema (subset of Cluster 9's five-service architecture); skill cascade (new skill or extension to existing `claude-api` discipline).

**Sub-concerns integrated:** L3.5 (graph-refinement prompt template), L3.6 (student-facing explainer template), L3.8 (self-consistency), L3.13 (trace-informed candidate-edge generation discipline).

**Why integrated, not parallel:** The LLM lens-sweep cross-cutting observation 3 stated: "Prompt templates are architectural artifacts, not documentation." The two paper-provided templates (graph-refinement + student-facing explainer) encode service-call ordering, input contracts, and interface shape. They must be versioned alongside the graph and undergo the same review discipline as graph edits. L3.8 (self-consistency) is the reliability mechanism for trace-informed candidate-edge proposals (L3.13). All four sub-concerns describe one prompt-template discipline.

**Integrated mechanism:** One ops doc establishing:

1. **Prompt templates as versioned repo artifacts** in `product/prompts/` (or content store equivalent). Each template carries: version, last_reviewed, reviewer, rationale, change_log.

2. **Adopt two paper-provided templates as Phase 7+ starting artifacts:**
   - Graph-refinement prompt (per `paper_2:L144–167`): JSON-only output, explicit rules section, "never mark an edge as required unless evidence supports instructional dependence."
   - Student-facing explainer (per `paper_2:L169–182`): five-element `Use:` structure (definition / example / contrast / formative question / why-this-matters); `Avoid:` block enforcing prerequisite-state awareness and lexical discipline.

3. **Self-consistency requirement** for graph-refinement outputs: sample N=3 outputs; only surface a candidate edge to the review layer if ≥2 of 3 agree. Per the 32% pre-mitigation failure rate from `paper_2:L50`.

4. **Co-versioning with graph:** prompt template versions are referenced from the graph-version table — when the graph version bumps, prompt-template compatibility is recorded. Prompt drift is as dangerous as graph drift.

5. **Self-grounded discipline:** the prompt-template authoring process itself uses synthetic test data and generic class names per `feedback_anti_bias_implementation_discipline.md`'s "hold-discipline-in-own-corpus" rule.

**Existing Paideia surface to reuse:** The existing `claude-api` skill discipline (per ADR 0070 + 0071 + 0081) is the build-apparatus prompt-discipline analog. The teaching-layer prompt discipline is architecturally similar.

**Contributing claims (representative):** `paper_2:L144–167` (graph-refinement template — complete artifact); `paper_2:L169–182` (student-facing explainer — complete artifact); `paper_2:L50` (Pardos & Bhandari 32% pre-mitigation failure + self-consistency mitigation); `paper_2:L54` (prompt composition and order changed feedback quality).

**Dependency:** Cluster 9 (instructional-spine architecture ADR) should land first to establish that prompt templates live in the content store under change-review.

---

### Cluster 11 — Four sample workflows + role-checkpoint partitioning

**Paideia surface:** Phase 7+ teaching-app architecture ADR; new ops doc for workflow-pattern selection.

**Sub-concerns integrated:** L3.3 (four sample workflows), L3.4 (role-checkpoint partitioning), L3.14 (student-friendly subset exposure).

**Why integrated, not parallel:** The four workflows (instructor-authored + LLM scaffolding / student-authored + LLM critique / adaptive-branching / trace-informed-revision) are the teaching-interaction archetypes. L3.4 (role-checkpoint partitioning) is the substructure within each workflow. L3.14 (student-friendly subset exposure) is the constraint that applies across all workflows. Treating these as one architectural decision avoids workflow proliferation.

**Integrated mechanism:** One product ADR establishing:

1. **Adopt four workflows as Paideia teaching patterns** (per `paper_2:L90–95`):
   - Instructor-authored PDG with LLM scaffolding — lowest-risk Phase 7+ entry point.
   - Student-authored PDG with LLM critique — pedagogically attractive; framed as suggestive not authoritative.
   - Adaptive branching lesson — conservative and coarse-grained for humanities (per `paper_2:L72`).
   - Automated prerequisite inference from traces — highest value, highest governance burden; gated on Cluster 9's no-silent-mutation rule.

2. **Role-checkpoint partition per workflow:** instructor role / LLM role / student role / human checkpoints (per `paper_2:L90–95`). Each checkpoint maps to a review-layer queue or notification event.

   **Path attribution invariant (per adversarial E.7.1):** every routing decision across all four workflows surfaces attribution to the student (`instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved`) per Cluster 15. The adaptive-branching workflow in particular must not silently route a student to a remediation node without showing them that the routing was model-inferred.

   **No-silent-mutation gate for the instructor-authored workflow (per adversarial E.1.2):** even in this lowest-risk workflow, any LLM-proposed edge or misconception node must route to Cluster 9's review-layer queue. The LLM may freely generate explanations from approved nodes (content-store layer) but may not silently propose graph-structure additions during scaffolding interactions.

3. **Student-friendly subset exposure as access-control invariant** (per `paper_2:L200`): the student-facing API returns only the local neighborhood (target node + immediate prerequisites + common misconceptions + upcoming assessments + alternative routes). Enforced at the access-control layer, not just UI convention.

4. **Phase 7+ rollout order:** instructor-authored + LLM scaffolding first; student-authored + LLM critique second; adaptive branching third (with conservative-and-coarse-grained gate); trace-informed revision last (requires the most analytics + review-layer maturity).

**Existing Paideia surface to reuse:** The four-workflow taxonomy maps onto distinct teaching surfaces — none of which Paideia currently has. The ADR is forward-looking architecture.

**Contributing claims (representative):** `paper_2:L90–95` (workflow table — complete artifact); `paper_2:L97–138` (Kant-to-phenomenology workflow diagram — concrete reference design); `paper_2:L140` (canonical division-of-labor); `paper_2:L200` (student-friendly subset rationale).

**Dependency:** Cluster 9 (instructional-spine architecture) is parent. Cluster 11 is the workflow instantiation of the architecture.

---

### Cluster 12 — Scaffolding fade trajectory + learner-state schema

**Paideia surface:** Phase 7+ schema (`learner_state` table); Phase 7+ teaching-app scaffold-fade module; product ADR; privacy classification per field (intersects Cluster 15).

**Sub-concerns integrated:** L1.15 (learner-state schema), L1.17 (fade trajectory per scaffolding edge), L2.4 (scaffolding with fade), L2.5 (expertise reversal).

**Why integrated, not parallel:** The pedagogy lens-sweep cross-cutting observation 3 stated the integration directly: "The scaffolding fade and expertise-reversal problem requires a learner-state store, not just a graph — but a lightweight default can approximate it." All four sub-concerns describe the same architecture: a separate learner-state store + a fade-trajectory rule on scaffolding edges + an expertise-reversal trigger.

**Integrated mechanism:** One product ADR establishing:

1. **Separate `learner_node_state` table** (per substrate lens-sweep cross-cutting observation 3 — lifecycle stratification):
   - Fields: **`learner_session_token`** (pseudonymous; the `learner_id` ↔ `learner_session_token` mapping lives in a separate identifier table governed by Cluster 15's RLS policies — per adversarial review E.6.1; this resolves the C12/C15 internal inconsistency), `node_id`, `mastery_probability` (float 0–1), `evidence_count` (int), `recent_errors` (jsonb array), `visit_count` (int), `last_interaction` (timestamp), `help_seeking_pattern` (jsonb), `language_preference` (text), **`consent_version`** (FK to consent table — per adversarial E.11.2; tracks which consent scope each row was written under), **`active_misconception_ids`** (array of FK to misconception nodes — per adversarial E.9.2; closes the substrate gap that lets C5's detect-remediate-retest state machine distinguish missing-concept from active-misconception per `paper_2:L186`), **`mastery_estimate_calibration_flag`** (boolean indicating whether the mastery estimate has been calibrated against a language-matched cohort — per adversarial E.4.2).
   - Privacy classification per field at authoring time (per L4.6 — intersects Cluster 15).
   - Separate high-write table; not mixed with graph-structure tables.
   - Consent withdrawal: deletes the identifier↔session_token mapping in the identifier table; aggregate analytics in `learner_node_state` remain intact but no longer joinable to a specific learner.

2. **Three-state scaffold approximation as Phase 7+ MVP** (per pedagogy lens-sweep cross-cutting observation 3):
   - State 0: first encounter → full scaffold (definition + worked example + contrast + formative question + why-this-matters).
   - State 1: second encounter OR `mastery_probability` ≥ 0.4 → reduced scaffold (contrast + formative question only).
   - State 2: third encounter OR `mastery_probability` ≥ 0.7 → no scaffold (retrieval prompt only).
   - Implementable without full knowledge-tracing — matches ZPD/fade trajectory well enough to be pedagogically principled.
   - **Path attribution requirement (per adversarial E.7.1):** every state transition (0→1, 1→2) is logged in the override events table (Cluster 15) with attribution `model_inferred_approved`, surfaced to the instructor dashboard (Cluster 17), and visible to the student per Cluster 15's path-attribution rule. A threshold-driven scaffold change without an audit trail directly contradicts Cluster 9's "LLM as triage/critic/coach — never judge" invariant.
   - **Mastery-probability calibration gate (per adversarial E.4.2):** the 0.4 and 0.7 thresholds may not be used for routing decisions until validated per language subgroup. Cluster 14's calibration protocol is a precondition for using these thresholds on multilingual cohorts.

3. **Edge fade trajectory** as derived attribute, not stored:
   - For each edge with `edge_type IN (helpful_bridge, soft_prerequisite)`, compute fade state from learner-state at query time.
   - Cluster 1's `expert_confidence` interacts: low-confidence edges fade slower (more support given longer).

4. **Future evolution:** full knowledge-tracing replaces three-state approximation when sufficient learner trace data exists (per knowledge-space theory pattern from L5.7).

**Existing Paideia surface to reuse:** None — learner state does not exist in current Paideia.

**Contributing claims (representative):** `paper_2:L84 (learner state row in schema table)` (5 fields); `paper_1:L39` ("graph that cannot be adjusted by cohort will not remain pedagogically valid for long"); `paper_2:L40` ("LLM conditioned on a PDG can give heavier support on fragile prerequisite nodes and then fade support as mastery increases"); `paper_1:L57` (Shakespeare + journal-writing expertise reversal evidence).

**Dependency:** Cluster 4 (node schema with `mastery_evidence` field) and Cluster 1 (per-edge confidence) precede. Cluster 15 (privacy/FERPA) constrains field design.

---

### Cluster 13 — Alternative-entry-route support + pluralism reserve

**Tier split (per adversarial review E.3.2):** The `entry_route_type` schema field is **promoted to Tier A** as an authoring-time substrate concern (extends Cluster 2's edge schema). The path-selector teaching logic and student-facing alternative-route surfacing remain Tier D. Reason: encoding alternative routes is authoring discipline per `paper_1:L126`, not Phase 7+ teaching architecture; deferring the schema field to Tier D risks the SEP backfill and other Phase 6 work operating on edges without entry-route classification.

**Paideia surface:** `product/seed-graph/` — `entry_route_type` attribute on incoming edges (extends Cluster 2; Tier A migration); Phase 7+ teaching-app path-selector logic (Tier D); integration with Cluster 8's tradition labels.

**Sub-concerns integrated:** L1.18 (alternative entry routes), L2.8 (multiple routes for ill-structured domains), L2.9 (recursive revisiting), L4.12 (pluralism in dependencies), L4.5 partial (anti-pathologizing via path-agnostic argument scoring).

**Why integrated, not parallel:** The substrate lens-sweep noted L1.18 + L2.8 are the same structural requirement at substrate and pedagogy levels. L4.12 (pluralism) and L4.5 (anti-pathologizing) are the governance restatement: a learner who reaches a target via an alternative route must not be scored as having a misconception just because the path differs from canonical. The four sub-concerns form one mechanism with one schema field and one path-selector rule.

**Integrated mechanism:** One product ADR + schema extension + Phase 7+ teaching-app rule:

1. **Edge attribute `entry_route_type`** (extends Cluster 2's edge schema): enum `case_based`, `conceptual`, `methodological`, `historical` (per `paper_1:L126`). Applies to edges INTO a target node — labels the route by which the prerequisite chain reaches the target.

2. **No canonical-path enforcement.** Validator soft-warn: any node where 100% of incoming `hard_prerequisite` edges share the same `entry_route_type` is flagged (single-lens sequencing risk per `paper_1:L45`).

3. **Path-selector rule (Phase 7+):** when serving a learner the local neighborhood, surface at least two distinct `entry_route_type` paths if available. The student can choose; the system does not force one. **Path attribution (per adversarial E.7.1):** route surfacing carries explicit attribution — `instructor_designed` if the alternative was authored by an instructor, `model_inferred_approved` if the alternative was surfaced via traversal heuristic. Students can ask "why is this route shown?" and receive an answer citing instructor decision or analytics-layer rationale per Cluster 15.

4. **Recursive-revisiting support** (per L2.9): track `visit_count` per (learner, node) — Cluster 12's learner-state field. Differentiate prompt for second vs first encounter (less definition, more comparison and application). Per `paper_2:L72`, knowledge tracing handles this; the three-state scaffold model from Cluster 12 approximates it.

5. **Path-agnostic argument scoring** (L4.5 mitigation): assessment rubrics for argument quality must NOT penalize learners for reaching a conclusion via a non-canonical path. Path-aware scoring only for prerequisite-completeness checks. Documented as rubric design discipline in Cluster 10's ops doc.

**Existing Paideia surface to reuse:** None — current graph has no entry-route categorization.

**Contributing claims (representative):** `paper_1:L126` (four entry-route types named); `paper_1:L45` (Spiro cognitive flexibility against single-lens); `paper_2:L188` (alternative pathways as equity mechanism); `paper_2:L200` ("alternative routes if they are stalled" — student-facing requirement); `paper_2:L70` (student-authored PDG with LLM critique surfaces single-lens assumptions).

**Dependency:** Cluster 2 (edge type vocabulary) — `entry_route_type` is an extension. Cluster 8 (tradition labels) — the equity-side rationale. Cluster 11 (workflow patterns) — the path-selector lives here.

---

## Tier E — Phase 7+ deployment governance

### Cluster 14 — LLM-mediated bias mitigation (output side)

**Paideia surface:** Phase 7+ governance ADR; new ops doc for LLM output audit; skill cascade (extension to `claude-api` discipline); intersects existing anti-bias mechanism.

**Sub-concerns integrated:** L4.3 (multilingual fairness), L4.5 (anti-pathologizing in scoring), L4.11 (assessment distortion), L4.4 partial (subgroup analysis applied to LLM outputs).

**Why integrated, not parallel:** Per the adversarial lens-sweep cross-cutting observation 2: "Two distinct bias surfaces require two distinct interventions." Cluster 8 addresses surface 1 (graph topology). This cluster addresses surface 2 (LLM-mediated output). The existing anti-bias mechanism is input-boundary-only; output-side bias requires parallel mechanisms.

**Integrated mechanism:** One product ADR + ops doc + skill extension:

1. **Multilingual output sampling.** Periodic audit: same input through LLM in N languages; compare output quality. Cadence: per the named-cadence + named-actor rule from adversarial lens-sweep cross-cutting observation 3.

2. **Rubric review for pathologizing risk.** Every scoring rubric authored for Phase 7+ assessment must name at least one "legitimate alternative interpretation" that should NOT trigger misconception-remediation routing.

3. **Scoring calibration against instructor rubrics.** At deployment and quarterly thereafter, sample N student responses; instructor scores in parallel with LLM; compute correlation, score compression (variance ratio), overscoring bias (mean delta), and subgroup performance (per Cluster 16 evaluation infrastructure).

4. **Pre-registered scoring prompt versioning.** Any change to a scoring prompt triggers re-calibration before deployment. Prompt drift is a silent assessment-distortion event.

5. **"Critic or coach, not final judge" framing** in all student-facing UI copy involving LLM-generated feedback or scoring. Per `paper_2:L190`.

6. **Override threshold for repeated misconception routing** (per `paper_2:L206`): a learner routed to misconception-remediation more than N times for the same concept flags for instructor review (heterodox-but-valid interpretive style vs genuine error disambiguation).

**Existing Paideia surface to reuse:** The existing anti-bias mechanism's input-boundary strip is a precedent for the symmetric output-boundary audit. The two together provide bidirectional bias coverage at the LLM serialization layer.

**Contributing claims (representative):** `paper_2:L188` (multilingual fairness UNESCO warning); `paper_2:L190` (assessment distortion — overscoring, compression, criteria shift; "critic or coach, not final judge"); `paper_2:L206` (subgroup discrepancy questions including over-pathologizing); `paper_2:L54` (prompt composition affects scoring).

**Dependency:** Cluster 9 (instructional-spine ADR) — needed for the staging-area architecture that LLM outputs flow through. Cluster 16 (learner-outcome evaluation infrastructure) — provides the calibration sample.

---

### Cluster 15 — Privacy / FERPA / NIST alignment + override logging + transparency reports

**Paideia surface:** Phase 7+ governance ADR; new ops doc `engine/operations/nist-genai-alignment.md` (or product/operations/); RLS policy design; consent management UI; named-cadence schedules.

**Sub-concerns integrated:** L4.6 (FERPA/privacy/consent), L4.7 (NIST GenAI profile alignment), L4.8 (override logging), L4.10 (opaque automation of curriculum authority).

**Why integrated, not parallel:** All four are deployment-side governance concerns; all four require the same infrastructure (override events table, transparency report template, RLS policies, consent management). Adversarial lens-sweep cross-cutting observation 3 was emphatic: "Governance machinery is inert without a named human review cadence." The four sub-concerns require one operations document with named cadence + named responsible actor per check.

**Integrated mechanism:** One product ADR + one ops doc:

1. **RLS policies at schema level** separating `student_id` from `learning_analytics_trace` (per `paper_2:L192`). No default-path foreign-key joins between identifier and analytics tables — pseudonymization at the DB layer, not just application layer.

2. **Consent management schema:**
   - `consent_version` field on every student-record row.
   - `retention_expiry` field on raw writing / trace records.
   - Withdrawal-of-consent workflow that purges identifiable data while preserving aggregate analytics.

3. **Override events table:**
   - Fields: `timestamp`, `overridden_entity_id` (edge or node), `override_type` (score / routing / prerequisite / classification), `overriding_actor` (instructor / committee / student), `reason`, `prior_value`, `new_value`.
   - Surfaced in the review layer (Cluster 9's fifth service).

4. **Transparency report template:**
   - `graph_edit_count_by_type`, `override_rate_by_node`, `override_rate_by_instructor`, `override_rate_by_time_period`, `subgroup_routing_discrepancies`, `provenance_coverage_pct`, `consent_withdrawal_count`.
   - Periodic publication; named cadence (quarterly default).
   - Increasing override rate on a particular node type signals systematic LLM miscalibration — escalation trigger.

5. **NIST four-control mapping:**
   - Empirical testing → Cluster 16 evaluation infrastructure.
   - Documentation of human-domain-knowledge interventions → review-layer event log + provenance per edge (Cluster 1).
   - Source-and-citation review → `provenance.source_text` field per edge (Cluster 1) + content-store approved sources (Cluster 10).
   - Override monitoring → override events table (this cluster).

6. **Named cadence + named responsible actor per check:**
   - Weekly: low-confidence edge review by course instructor.
   - Quarterly: equity audit by course coordinator or designated DEI reviewer.
   - Annually: graph-validity review by discipline committee.
   - At every commit-merge: scoring calibration if prompts changed.

7. **Student-facing path attribution:** every adaptive routing decision carries one of `instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved`. Students can ask "why am I here?" and receive a citing answer.

**Existing Paideia surface to reuse:** The build-apparatus override discipline (HANDOFF.md disposition tracking per ADR 0048; audit_handoff_dispositions.py) is the data-layer override-logging precedent. The teaching-layer override events table is architecturally analogous.

**Contributing claims (representative):** `paper_2:L192` (FERPA/NIST guidance — three concrete schema requirements); `paper_2:L194` (override logging + transparency requirement); `paper_2:L186` (NIST GenAI profile four controls); `paper_2:L194` (student-visible path attribution).

**Dependency:** Cluster 9 (foundational architecture) is parent. Cluster 16 (evaluation infrastructure) provides the data the transparency reports consume.

---

### Cluster 16 — Learner-outcome evaluation infrastructure

**Paideia surface:** Phase 7+ evaluation ADR; new ops doc for evaluation methodology; IRB-side preparation; intersects Cluster 7 (graph-validity in SQA) and Cluster 17 (anomaly detection).

**Sub-concerns integrated:** L5.1 (learner-outcome measurement), L5.3 (PDG-only vs LLM-only vs PDG+LLM comparative designs), L5.4 (HTE / subgroup analysis), L5.5 (process-quality measurement), L5.6 (design-based research), L5.10 (student-experience validity).

**Why integrated, not parallel:** Six evaluation sub-concerns describe one evaluation methodology — they are not six independent studies. Evaluation lens-sweep cross-cutting observation 2: "the evaluation instrument bundle is graph-native, not assessment-generic" — meaning instruments must be co-designed with the graph schema. Cross-cutting observation 4: "HTE analysis is both an equity obligation and a graph-validity instrument" — same measurement, two purposes.

**Integrated mechanism:** One product ADR + one ops doc:

1. **Five-metric outcome bundle** (per `paper_1:L144–146`):
   - Performance on threshold-concept tasks.
   - Comparative essay quality.
   - Transfer to unfamiliar texts/contexts.
   - Delayed retention (≥ 4 weeks post-instruction).
   - Rubric dimensions tied to graph nodes.
   Plus from `paper_2:L204`: help-seeking behavior, time-on-task, student understanding of why a path was recommended.

2. **Comparative experimental designs** (per `paper_2:L204`):
   - Cluster-randomized or cross-over at section/unit level.
   - Three arms: PDG-only, LLM-only, PDG+LLM.
   - Delayed posttest + transfer task mandatory.
   - Cross-over especially relevant for small-cohort early Paideia deployments.

3. **HTE subgroup analysis with pre-registered primary contrasts:**
   - Subgroups: prior preparation, verbal ability proxy, language background, major/non-major.
   - Pre-registration distinguishes confirmatory from exploratory contrasts (per L5.4).
   - HTE is structural to the validity framework, not optional add-on.

4. **Process-quality measurement infrastructure** (per `paper_1:L51` Lucero et al. method):
   - Discourse-coding of transcripts for causal explanation, argumentation, disciplinary vocabulary, peer-knowledge convergence.
   - Trained coders or LLM-assisted coding pipeline with human validation.
   - LMS navigation event logging at node level.

5. **Design-based research as overarching methodology** (per `paper_1:L149`): iterative design / implement / analyze / revise. Treat graph as revisable model. SQA discipline (Cluster 7) is phase 1; learner-outcome evaluation is phase 2 of the same study.

6. **Node-linked student survey instrument** (per L5.10): NOT generic satisfaction. Survey items name specific graph elements ("the optional bridge on Kantian transcendental idealism — did this feel helpful or burdensome?").

7. **Three-arm comparison study as the canonical Phase 7+ first deployment study.** Pre-register design before any deployment; IRB protocol before consent collection.

**Existing Paideia surface to reuse:** Cluster 7's SQA extension provides phase-1 graph-validity data; this cluster's phase-2 learner-outcome data validates or falsifies SQA predictions.

**Contributing claims (representative):** `paper_1:L144–150 (evaluation table)`; `paper_1:L51` (Lucero et al. discourse-analysis method); `paper_1:L152–154` (quasi-experimental humanities design); `paper_2:L204` (additional outcome metrics + cluster-randomized + cross-over framing); `paper_1:L149` (DBR + two-phase methodology); `paper_2:L206` (subgroup discrepancy evaluation criteria).

**Dependency:** Tier A substrate must enable `rubric_dimensions_tied_to_graph_nodes`. Cluster 9 (architecture) provides the analytics-layer infrastructure. Cluster 15 (privacy) constrains data collection.

---

### Cluster 17 — Anomalous routing detection + three-way disambiguation

**Paideia surface:** Phase 7+ analytics-layer module; integrated with Cluster 9's review layer; ops doc.

**Sub-concerns integrated:** L5.8 (anomalous routing detection), L3.13 partial (trace-informed candidate-edge generation — its detection upstream), L5.2 partial (graph predictive validity — its operational signal).

**Why integrated, not parallel:** L5.8 names three anomaly types: missing prerequisite / over-strong edge / bad assessment item. L3.13 names the same three signals as candidate-edge generation triggers. L5.2 graph-predictive-validity uses the same "downstream failure + upstream success" pattern. The three are one detection mechanism with three remediation paths.

**Integrated mechanism:** One product ADR + analytics-layer module + ops doc:

1. **Three anomaly types with distinct interventions:**
   - **Bypass-and-succeed:** student succeeded downstream without completing the supposedly required prerequisite. Falsifies the hard-prerequisite claim. → candidate edge weakening or conversion to `recommended`/`soft_prerequisite`.
   - **Satisfy-and-fail:** student satisfied the prerequisite but failed downstream. Three possible causes: (a) missing intermediate prerequisite, (b) over-strong downstream node, (c) bad assessment item. Requires further investigation.
   - **Cycle-without-progress:** student repeatedly fails on the same node despite remediation. Recommender failure or misconception not yet encoded.

2. **Analytics-layer detection rules:** automated detection of each anomaly type with confidence thresholds. Outputs candidate edges or candidate misconception nodes, NOT silent graph mutations (per Cluster 9's no-silent-mutation rule).

3. **Instructor dashboard queue (review layer):** sorted by anomaly type and frequency. Each anomaly carries: contributing learner traces (anonymized per Cluster 15), suggested intervention class, confidence score.

4. **Three-way disambiguation discipline** (`paper_2:L74`): a `satisfy-and-fail` event must not be auto-classified — it requires instructor disambiguation among the three causes. Auto-classification inflates false positives in graph revision.

5. **Cohort tracking for predictive-validity feedback loop:** anomaly events tagged with `cohort_id` so cross-cohort patterns reveal systematic vs cohort-specific edges.

**Existing Paideia surface to reuse:** None at the teaching-layer level. The build-apparatus alarm patterns (soft-warns per ADR 0042/0049, validator categories) are precedent for the analytics-to-review-queue pattern.

**Contributing claims (representative):** `paper_2:L74` (three-way diagnostic signal types); `paper_2:L72` (conservative-and-coarse-grained branching for humanities); `paper_2:L94` (anomalous paths as named workflow checkpoint); `paper_1:L162` ("revise them when learners succeed through routes the graph did not predict").

**Dependency:** Cluster 9 (analytics-layer service) is parent. Cluster 12 (learner-state schema) provides the traces. Cluster 1 (per-edge confidence + version) provides the targets of revision.

---

## Cross-cluster integration notes

**Tier A clusters share substrate.** The migration sequence is: Cluster 1 (per-edge contestability columns) → Cluster 4 (per-node typology + metadata) → Cluster 2 (edge-type vocabulary + relation layering) → Cluster 3 (learning_outcomes table + edge_outcome_necessity junction) → Cluster 5 (misconception sub-graph using new node + edge types). Cluster 5 cannot land before Cluster 2 + Cluster 4.

**Cluster 8 and Cluster 14 are the two-bias-surface mechanism pair.** They must be authored as a deliberate pair (one product ADR + one Phase 7+ governance ADR) so the surface partition is clear in both directions. The existing anti-bias memory drawer extension names the partition explicitly.

**Cluster 9 is the parent of Clusters 10, 11, 12, 13.** All four are instantiations of the instructional-spine architecture. They can be drafted in parallel after Cluster 9 lands as an architectural commitment.

**Cluster 15 (privacy/FERPA) constrains Clusters 12 (learner state), 14 (LLM output audit), 16 (evaluation infrastructure), 17 (anomaly detection).** Phase 7+ governance must be drafted before any of these schemas are finalized.

**Cluster 7 (SQA extension) is the bridge between Tier A and Tier E.** SQA is phase 1 of the validity study; Cluster 16 is phase 2. The framing must be explicit so the two phases generate compatible data.

## Sub-concern coverage check

Every sub-concern from the 66-item checklist is addressed by at least one cluster:

| Lens | Sub-concerns | Clusters |
|---|---|---|
| L1 Substrate (18) | L1.1, L1.2 → C2 | L1.3 → C3 | L1.4, L1.5, L1.7, L1.14 → C1 | L1.6 → C4 | L1.8 → C5 | L1.9, L1.10, L1.11, L1.12, L1.13, L1.16 → C4 | L1.15 → C12 | L1.17 → C12 | L1.18 → C13 |
| L2 Pedagogy (13) | L2.1 → C4 + C6 | L2.2 → C6 | L2.3 → C6 + C3 | L2.4, L2.5 → C12 | L2.6, L2.7 → C5 | L2.8, L2.9 → C13 | L2.10 → C4 + C13 | L2.11 → C6 + C10 | L2.12 → C4 + C16 | L2.13 → C3 |
| L3 LLM (15) | L3.1, L3.2, L3.7, L3.9, L3.10, L3.11, L3.12 → C9 | L3.3, L3.4 → C11 | L3.5, L3.6, L3.8, L3.13 → C10 | L3.14 → C11 | L3.15 → C9 |
| L4 Adversarial (13) | L4.1 → C8 | L4.2 → C6 + C1 | L4.3, L4.5, L4.11 → C14 | L4.4 → C14 + C16 | L4.6, L4.7, L4.8, L4.10 → C15 | L4.9 → C1 | L4.12 → C13 | L4.13 → C8 + C14 (split by surface) |
| L5 Evaluation (10) | L5.1, L5.3, L5.4, L5.5, L5.6, L5.10 → C16 | L5.2, L5.9 → C7 | L5.7 → C7 + C16 | L5.8 → C17 |

**All 66 sub-concerns mapped. No orphans.**

## Phase 6 master-plan-input subsection

The currently-pending Phase 6 self-correction master plan (per STATE.md) is scoped to embedding/SEP architecture for self-correction — specifically: `users.embedding_model` metadata, vector partition migration, `sep_chunks` junction-table, 380-node SEP backfill, entity-resolution-service application code, tension-log emission scaffolding.

The PDG papers reveal that Phase 6+ scope is broader than the currently-planned self-correction work. The Tier A substrate clusters (1-5) are NOT part of the current Phase 6 plan but they are foundational substrate changes that should land BEFORE the SEP architecture commits to specific node/edge structures — because the SEP-backfill operates on the nodes table, and Cluster 4 redesigns the nodes table.

**Binarized architectural choice (revised per adversarial E.12.1):**

The user's actual choice is binary — Phase 6 either includes Tier A substrate work before SEP backfill, or it does not. The original three-option framing obscured that (b) and (c) produce the same architectural outcome (SEP backfill on the current nodes table) and differ only in administrative mechanism.

- **Option A — Expand Phase 6 scope to include Tier A substrate (Clusters 1, 2, 4 at minimum) before SEP backfill.** Adds ~4-6 session-sized work units. SEP backfill operates on the redesigned nodes table — embeddings are computed on `node_type` / `disciplinary_domain` / `granularity` / `canonical_sources` / `misconceptions` (per adversarial E.12.2, these five fields most affect embedding semantic quality if absent at backfill time). Architecturally coherent; higher upfront cost; avoids re-backfill.
- **Option B — Proceed narrow; accept a follow-up re-backfill.** Tier A lands after Phase 6 SEP work. Existing nodes are embedded based on current sparse representations. After Tier A migration adds the five semantically-rich fields, a follow-up re-backfill recomputes embeddings. Lower upfront cost; SEP work proceeds on the existing schema; re-backfill cost is the cost-of-choice. Administrative implementation may be either a Phase 6.5 plan revision or per-Issue prioritization — both produce the same outcome.

The decision rests on whether the five Tier A fields named above (especially `node_type` and `canonical_sources`) materially affect embedding quality enough to justify the upfront cost. If embedding the current sparse representations produces useful results for self-correction purposes, Option B is acceptable. If self-correction depends on semantic richness in the node representation, Option A is required.
