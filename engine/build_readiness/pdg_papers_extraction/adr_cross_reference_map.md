# PDG Papers Extraction — Session α: ADR cross-reference map

> Phase α output of the 6-session pre-phase deliberation plan (per HANDOFF.md "PDG papers extraction" entry). Maps each of the 17 integrated clusters in [`synthesis.md`](synthesis.md) against the current ADR corpus (92 ADRs = 51 engine + 41 product). Author Session δ's foundational ADRs against this map; the map narrows the surface that needs deliberation by naming what already settles, what extends, what conflicts, and what is genuinely net-new.
>
> **Posture.** Quality-first deliberation per S-0193 user direction ("set the stage fully before stepping into the next stage"). No ADRs authored here; no Issues fire (per the no-Issues-before-Session-ζ rule); no schema changes. This is research output for Session δ's input.

## Methodology

For each of 17 clusters, six categories of ADR relationship are surfaced:

- **Intersecting** — ADR's surface overlaps; cluster must cross-reference but does not conflict.
- **Conflicting** — cluster's proposed direction contradicts an existing ADR commitment; supersession or amendment required.
- **Extending** — cluster builds on / continues a prior decision; the new ADR would cite as parent.
- **Net-new substrate** — no current ADR covers this surface; the new ADR carries the full deliberation burden.
- **Supersession candidates** — specific ADRs that would flip to `Superseded by` status (named with reason).
- **Amendment candidates** — specific ADRs that would need a Consequences amendment (named with which section).

Each cluster section ends with an **Adversarial probe** paragraph naming one ADR the cluster's "Paideia surface" description does not obviously implicate but which deserves checking — a deliberate counter-move against the synthesis's own framing.

Targeted ADR reads (rather than blanket reading) used the cluster's `Paideia surface` + `Sub-concerns integrated` + `Existing Paideia surface to reuse` + `Contributing claims` fields as targeting input. Approximately 18 ADRs read in full for this map (mostly product-side; engine ADRs read for pattern analogs to validator soft-warns, no-silent-mutation discipline, and substrate-decision shape).

## Summary table

| # | Cluster | Intersect | Conflict | Extend | Net-new | Supersession candidates | Amendment candidates |
|---|---|---|---|---|---|---|---|
| 1 | Contestability substrate (per-edge) | 4 | 0 | 3 | partial | none | ADR 0021 |
| 2 | Edge-type taxonomy expansion + three-relation layering | 3 | 0 | 2 | no | none | ADR 0001 |
| 3 | Goal-relative parameterization | 4 | 0 | 1 | yes | none | ADR 0014 |
| 4 | Node schema redesign | 7 | 1 (potential) | 4 | partial | none | ADR 0008 |
| 5 | Misconception sub-graph encoding | 3 | 0 | 1 | yes | none | none |
| 6 | Backward-design + Decoding-the-Disciplines | 3 | 0 | 1 | yes | none | none |
| 7 | Graph predictive-validity → SQA discipline | 2 | 0 | 2 | no | none | none |
| 8 | Graph-topology bias mitigation | 4 | 0 | 1 | yes | none | none |
| 9 | Instructional-spine architecture (foundational) | 8 | 0 | 5 | partial | none | ADR 0014, ADR 0017 |
| 10 | Prompt template discipline + content store | 5 | 1 (potential) | 2 | no | none | ADR 0027 |
| 11 | Four sample workflows + role-checkpoint partitioning | 4 | 0 | 2 | partial | none | ADR 0028 |
| 12 | Scaffolding fade trajectory + learner-state schema | 8 | 0 | 3 | partial | none | ADR 0004, ADR 0026 |
| 13 | Alternative-entry-route support + pluralism reserve | 3 | 0 | 1 | yes | none | none |
| 14 | LLM-mediated bias mitigation (output side) | 4 | 0 | 1 | yes | none | none |
| 15 | Privacy / FERPA / NIST + override logging | 5 | 1 (load-bearing) | 2 | partial | none | ADR 0031 |
| 16 | Learner-outcome evaluation infrastructure | 4 | 0 | 2 | yes | none | none |
| 17 | Anomalous routing detection + three-way disambiguation | 4 | 0 | 2 | yes | none | none |

**Conflict count: 3 potential** (1 load-bearing). Net-new substrate: **8 clusters** carry net-new mechanism. Amendment candidates: **9 distinct ADRs** named. No supersession candidates surfaced — all conflicts admit resolution via amendment or scoping clarification.

---

## Per-cluster sections

### Cluster 1 — Contestability substrate (per-edge)

**Paideia surface (from synthesis):** `product/seed-graph/` edges schema; new product ADR; new validator soft-warn.

**Intersecting ADRs:**
- **Product 0030** (`confidence_level` is the evidentiary-mode axis on nodes) — already commits per-NODE three-axis epistemic model (`provenance` / numeric `confidence` / categorical `confidence_level`). Cluster 1 commits parallel per-EDGE model. Naming-risk lesson from ADR 0030 transfers: avoid creating two more "confidence_x" names that read as bins of each other.
- **Product 0014** (Sonnet teaches, Opus reviews) — Opus reviewer "proposes graph edits through a confidence-weighted pipeline." Cluster 1's `llm_confidence` field is the persistence target for that pipeline's output; `disagreement_flag` is its trigger condition.
- **Engine 0042** (soft-warn lifecycle archive canon) — Cluster 1's validator soft-warn ("any edge with `expert_confidence: high` AND empty `counterexamples` AND empty `provenance.rationale`") is a new soft-warn category that joins the canonical archive surface + 3-of-5 persistent-warn surface.
- **Engine 0049** (scope-lock at boot, descope/reorder audit at shutdown) — pattern analog for the "review_status" enum lifecycle (provisional / approved / pending_review / rejected); ADR 0049's scope-delivery audit shape generalizes.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0030** — extends per-node 3-axis epistemic model to per-edge 3-axis model (`expert_confidence` enum + `trace_confidence` float + `llm_confidence` float + `disagreement_flag`). Cluster 1's ADR cites 0030 as the per-node precedent.
- **Product 0021** (node deprecation via status + `superseded_by`) — extends per-node lifecycle pattern to per-edge `version` (integer, monotonic) + graph-versions table. NOT a duplicate: 0021 governs replacement-on-correction; Cluster 1's `version` governs revision-history.
- **Engine 0091** (engine-memory substrate SQLite + FTS5) — pattern analog for `provenance` jsonb structure (engine_memory's drawer `source_kind` + `tags[]` is the analogous bounded vocabulary; Cluster 1's `provenance.source_text` / `course_context` / `version` / `reviewer` / `rationale` is the same shape applied to edges).

**Net-new substrate:** Partial. Confidence-on-edges is net-new; counterexamples-as-jsonb-array is net-new; review_status enum is net-new. The pattern of "per-row epistemic columns with mechanical validator backstop" is established (per ADR 0030 + Engine 0042) — Cluster 1 transposes the pattern, not invents it.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0021** — Consequences section says "edge queries filter through active nodes only; deprecated nodes carry no traversal weight." Cluster 1's `review_status: rejected` / `pending_review` semantics need parallel traversal-filter rules at the edge level. Amend 0021's Consequences with the edge-lifecycle parallel, OR Cluster 1's ADR carries the full edge-lifecycle rule. Session δ chooses.

**Adversarial probe:** Does Cluster 1's `version` integer on edges interact with the graph-versions table that ADR 0017 (Postgres + recursive CTEs) commits to? ADR 0017 commits to "recursive CTEs for directed prerequisite walks, joined with `learner_events` and `mastery_snapshots`" — Cluster 1's per-edge version would require recursive-CTE walks to filter by `(graph_version, edge_version)` pairs. The traversal-cost implications are not in the cluster body; Session δ's tool-stack decision (per Cluster 9's tool-stack-evaluation sub-decision) should verify the per-edge `version` filter does not cross the recursive-CTE performance threshold ADR 0017 names. Additionally: ADR 0091's engine_memory substrate uses an FTS5 + BM25 + recency + tag-class composite rank — the same compositional pattern Cluster 1's `disagreement_flag` could leverage if Phase 7+ analytics needs to rank edges by contestability signal. Not a conflict; an unexplored substrate analog.

---

### Cluster 2 — Edge-type taxonomy expansion + three-relation layered separation

**Paideia surface (from synthesis):** `product/seed-graph/` edges schema; new product ADR (likely two: edge-type expansion + relation-layering policy); migration retyping the 516 existing `pedagogical_prerequisite` edges; routing-layer validator check.

**Intersecting ADRs:**
- **Product 0001** (pedagogical edges, not historical) — the foundational edge-semantic commitment. Originally committed "historical relationships are out of scope; if a learner wants the history of an idea, that's a different product surface (or absent entirely from V1)." ADR 0061 has since activated the `historical_influence` predicate; Cluster 2's third layer (`conceptual_relatedness`) extends further. ADR 0001's "edges encode pedagogical prerequisite relationships" survives intact — Cluster 2 sub-types within the pedagogical layer (hard_prerequisite, soft_prerequisite, helpful_bridge, etc.).
- **Product 0061** (historical_influence retyping for history-terminator bridges) — the precedent the cluster builds on. ADR 0061's mass-retype of 17 edges from `pedagogical_prerequisite` to `historical_influence` is the same operation Cluster 2 proposes for the 516 default-to-soft retyping.
- **Engine 0016** (graph construction needs live validation) — the existing graph-audit utility is where Cluster 2's new validator soft-warns ("any teaching-layer query asking for 'prerequisites of X' must filter to `pedagogical_dependence` edges only"; "any edge with `edge_type: hard_prerequisite` AND `expert_confidence: low` flagged as provisional") would land.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0001** — extends from binary-edge-semantic to three-layer-semantic. The pedagogical-edges-not-historical commitment is preserved; the layering is additive.
- **Product 0061** — extends the activated-predicate set. ADR 0061 activated `historical_influence`; Cluster 2 activates `conceptual_relatedness` as the third layer plus a controlled vocabulary within each layer.

**Net-new substrate:** No. The PREDICATE_MANIFEST.md surface already exists; Cluster 2 adds new predicates + sub-types using the existing pattern.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0001** — Consequences section currently says "the graph carries no `influenced_by` predicate." This was already partially false after ADR 0061 (which activated `historical_influence`). Cluster 2's ADR should amend ADR 0001's Consequences to record the now-three-layer structure: "edges encode pedagogical prerequisite relationships at the structural-load-bearing layer; `historical_influence` carries display-only genealogy per ADR 0061; `conceptual_relatedness` carries display-only conceptual affinity per Cluster 2 ADR." This is a cleanup amendment, not a substantive change to ADR 0001's commitment.

**Adversarial probe:** Cluster 2 proposes retyping 516 existing `pedagogical_prerequisite` edges to `soft_prerequisite` by default. ADR 0061 just landed a 17-edge retyping at S-0122 (production audit closeout). The two operations are different in target (different edges) but identical in shape. Does the apparatus support back-to-back mass-retyping migrations? Engine ADR 0055 (apply-migration wrapping against Production Reads gate) governs the retyping migration's mechanical execution; Cluster 2's migration may exceed the per-migration assertion budget that ADR 0055 + ADR 0039 Layer 2.5 imply for 516 retypings. Session δ should size the migration shape (single migration vs sharded) against the existing apply_migration.py postcondition surface — this is operational not architectural, but it constrains the cluster's deliverable shape. Additionally: Cluster 2's "routing rule (validator soft-warn): any teaching-layer query asking for 'prerequisites of X' must filter to `pedagogical_dependence` edges only" is a query-time check that ADR 0016 doesn't currently surface — adding it requires the query-layer surface to exist (Phase 7+).

---

### Cluster 3 — Goal-relative parameterization

**Paideia surface (from synthesis):** `product/seed-graph/` — new `learning_outcomes` table + `edge_outcome_necessity` many-to-many junction; major product ADR; teaching-app path-selector contract.

**Intersecting ADRs:**
- **Product 0010** (continuous and contextual assessment) — the rubric (reconstruction / application / boundary awareness) is per-concept; Cluster 3's learning_outcomes table adds the goal layer above the concept. The rubric does not currently encode goal; Cluster 3 introduces goal-as-input. Both layers needed; Cluster 3 sits above 0010, not in conflict.
- **Product 0014** (Sonnet teaches, Opus reviews) — Sonnet's per-turn context currently includes "current concept + one-hop prerequisites + two-hop entity-resolution neighborhood." Cluster 3's `get_path(target_node_id, learning_outcome_id, learner_state)` signature would extend Sonnet's input contract. Sonnet's prompt assembly already does goal-blind path-selection; Cluster 3 introduces goal-relativity to that surface.
- **Product 0027** (rendering policy is the prompt-layer contract) — AGENT_INSTRUCTIONS.md currently doesn't carry learning-outcome tokens. Cluster 3's introduction of `learning_outcome_id` in the prompt context affects what the rendering policy must (forbid? allow?) emit. Likely: the outcome identifier is internal; the outcome's `outcome_text` may or may not appear in learner-facing prose. Session δ adjudicates.
- **Engine 0091** (engine-memory substrate) — cluster's `default_necessity_level` default-to-recommended-not-required pattern matches engine_memory's "no embedding model; semantic relevance delivered by Claude reading top-K" default-to-conservative pattern. Pattern analog for default-shape under uncertainty.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0014** — extends Sonnet's input contract with the goal parameter. ADR 0014's role split survives; Cluster 3 enriches the teaching-side input.

**Net-new substrate:** Yes. `learning_outcomes` table is wholly new; `edge_outcome_necessity` junction is wholly new; necessity-level enum (`required`, `recommended`, `historical_contextual_only`) is wholly new.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0014** — Consequences section names per-session context shape ("current concept + one-hop prerequisites + two-hop entity-resolution neighborhood"). Cluster 3 adds the goal as a new context dimension. Amend 0014's per-session context shape to include `learning_outcome_id` once Cluster 3 lands. OR keep 0014 silent on the goal dimension and have Cluster 3's ADR carry the full prompt-shape (less load-bearing on 0014). Session δ chooses.

**Adversarial probe:** ADR 0017 (Postgres + recursive CTEs) commits the graph-traversal substrate as Postgres recursive CTEs filtered by mastery state. Cluster 3's `get_path(target_node_id, learning_outcome_id, learner_state)` adds a third filter dimension to the recursive CTE. The recursive-CTE performance bound ADR 0017 names ("chains rarely deeper than 8-10 hops") would now be cross-filtered by learning-outcome edge-necessity rows. At n=1-3 users this is bounded; at scale the join shape needs design attention. Additionally: ADR 0085 (server-side mastery confirmed) names "mastery snapshot fetch, two-hop neighborhood fetch, prerequisite fetch" as the per-turn back-end-call surface — Cluster 3 may introduce a fourth call type ("goal-relative necessity fetch") OR fold goal-relativity into the prerequisite fetch. Bandwidth and latency budget for Phase 7+ teaching-loop should be considered when sizing the schema.

---

### Cluster 4 — Node schema redesign

**Paideia surface (from synthesis):** `product/seed-graph/` nodes schema; 1-2 product ADRs; migration; new validator soft-warns for required field population.

**Intersecting ADRs:**
- **Product 0008** (nodes are concepts, not thinkers) — foundational node-granularity commitment. Cluster 4's `node_type` enum (`threshold_concept`, `bridge_concept`, `disciplinary_practice`, `text_excerpt`, `historical_context`, `misconception`, `comparative_lens`, `assessment_task`) potentially breaks 0008's "never a person, school, work, or tradition" rule. `text_excerpt` is work-shaped; `historical_context` could be tradition-shaped.
- **Product 0017** (Postgres + recursive CTEs) — node schema extensions land in the existing Postgres tables. ADR 0017's CTE traversal pattern is unaffected by additional columns.
- **Product 0021** (node deprecation via status + `superseded_by`) — Cluster 4's `node_type` migration produces backfill semantics that interact with 0021's deprecated-node-still-in-table discipline. Backfill must populate `node_type` for deprecated nodes too, OR the audit accepts NULL on deprecated.
- **Product 0030** (`confidence_level` on nodes) — already commits per-node fields (`provenance`, `confidence`, `confidence_level`). Cluster 4's 13+ new node columns join the same table. Naming risk lesson from 0030 transfers (e.g., `granularity` vs `confidence_level: 'EXTRACTED'` — both record "what kind of evidence/depth"); design care needed.
- **Product 0061** (historical_influence retyping) — Phase 6 audit-system-input Proposal 4 names the validator soft-warn `historical_node_as_prereq_source` as needing "node_class tagging schema extension." Cluster 4's `node_type` enum IS that extension. Cluster 4 enables the soft-warn 0061 anticipated.
- **Engine 0016** (graph construction needs live validation) — Cluster 4's three new validator soft-warns (lacking node_type / lacking assessment_items on threshold_concept / lacking cultural_specificity) land in the graph-audit utility ADR 0016 already provisions.
- **Engine 0042** (soft-warn lifecycle archive canon) — three new soft-warn categories joining the canonical archive surface + persistent-warn surface; lifecycle pattern unchanged.

**Conflicting ADRs:**
- **Product 0008** (potential, requires Session δ adjudication) — `text_excerpt` as a node_type appears to violate 0008's "never a person, school, work, or tradition" prohibition. Two readings: (a) `text_excerpt` here means a teachable-unit-derived-from-a-text-passage (concept-level, ADR 0008 compatible); (b) `text_excerpt` means the passage itself as a node (work-level, 0008 conflict). The cluster body uses the term without clarification. Session δ MUST adjudicate the read at ADR-authoring time. Same potential concern with `historical_context` (a node about a historical period vs. a concept that happens to have historical depth).

**Extending ADRs:**
- **Product 0008** — extends node typology if the `node_type` enum stays concept-level-only (the compatible read).
- **Product 0030** — extends per-node metadata. ADR 0030's three epistemic axes survive; Cluster 4 adds 13+ orthogonal columns (typology / pedagogy / equity).
- **Product 0061** — extends to enable the deferred `historical_node_as_prereq_source` validator soft-warn (Issue #115 documents the pending need).
- **Engine 0042** — pattern continues. New soft-warns inherit the archive-canon + 3-of-5 persistence-detection lifecycle.

**Net-new substrate:** Partial. The pattern of "add columns to nodes table, backfill, add soft-warn" is established (ADR 0030 is the precedent). Many specific fields are net-new: `audience_tags`, `canonical_sources` (jsonb), `approved_examples` (jsonb), `misconceptions` (jsonb — see Cluster 5), `assessment_items`, `mastery_evidence`, `accessibility_notes`, `assumed_background`, `jargon_load`, `cultural_specificity`, `tradition_label` (see Cluster 8).

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0008** — Consequences section says "the granularity principle is the load-bearing test: a node is correctly granular when both prerequisite claims and assessment claims are possible at its scope." Cluster 4's `node_type` enum either preserves this (every type is concept-level) or breaks it (allowing work/tradition/period nodes). If preserved: amend 0008's Consequences to record the typology adds a within-concept-level type tag, not a granularity-level escape hatch. If broken: 0008 needs substantive amendment.

**Adversarial probe:** Cluster 4 adds 13+ columns to the nodes table in one migration. Engine ADR 0055 (apply-migration wrapping) + ADR 0039 Layer 2.5 (postcondition assertions) constrain migration shape: each column with a soft-warn-detectable invariant needs an assertion. The migration's postcondition-assertion count could exceed 10+ if every soft-warn from Cluster 4 (3 named) plus column-existence assertions (13+) plus enum-value assertions plus FK assertions get separate lines. The cluster body doesn't size this. Additionally: Cluster 8 (graph-topology bias) requires `tradition_label` + `audience_tags` from Cluster 4's schema; these two clusters are coupled in their migration ordering. ADR 0030's "Phase 4 audit category lands without code change" pattern is the right shape for Cluster 4's three new soft-warns — implementation cost is low; the question is governance shape.

---

### Cluster 5 — Misconception sub-graph encoding (extends C2 + C4)

**Paideia surface (from synthesis):** `product/seed-graph/` — new `misconception` node type (Cluster 4) + new edge types `common_misconception_about` and `unlearning_required_before` (Cluster 2); product ADR for misconception encoding semantics; Phase 7+ teaching-app detect-remediate-retest state machine.

**Intersecting ADRs:**
- **Product 0008** (nodes are concepts, not thinkers) — `misconception` as a node type carries the same Session δ adjudication question as Cluster 4's other node types: misconception-as-concept (cluster-compatible) vs. misconception-as-text-passage (conflict).
- **Product 0010** (continuous and contextual assessment) — Cluster 5's "detect-remediate-retest state machine" is the misconception-handling counterpart to ADR 0010's rubric. The rubric currently presumes the learner is acquiring a concept; Cluster 5 introduces the case where the learner is unlearning an active misconception first.
- **Product 0013** (mastery verification organic escalation) — Cluster 5's two-state distinction ("missing concept" vs "active misconception") changes ADR 0013's organic-escalation pattern. A callback to a misconception-flagged concept needs different teaching moves than a callback to a never-learned concept.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0010** — extends rubric coverage to "boundary awareness includes saying what the concept is NOT against the seeded misconception." Cluster 5's three named misconception examples (phenomenology=introspection; deconstruction=anything goes; historical perspective=sympathy with the past) plus the Corrigan unlearning targets are the seed misconception corpus.

**Net-new substrate:** Yes. No current Paideia surface encodes misconceptions; the two-level scheme (lightweight `misconceptions` jsonb field on target nodes + full standalone misconception nodes with `common_misconception_about` / `unlearning_required_before` edges) is wholly new.

**Supersession candidates:** None.

**Amendment candidates:** None. Cluster 5 lands as a new ADR consuming Cluster 4's node_type enum + Cluster 2's edge-type vocabulary; no existing ADR carries text that needs revision.

**Adversarial probe:** The "detect-remediate-retest state machine" is a teaching-layer behavior not currently captured by any product ADR — ADR 0014 (Sonnet teaches) commits the role split but doesn't formalize state machines, and ADR 0027 (rendering policy) commits prose constraints but doesn't commit pedagogical sequence. Cluster 11 (four sample workflows) introduces workflow-as-architecture but at coarser grain than per-misconception state. Session δ should clarify: is Cluster 5's state machine a new Phase 7+ teaching architecture commitment (Cluster 11-shaped) or a within-teaching-turn micro-state? The shape affects whether Cluster 5's ADR has Phase 7+ implementation implications or is contained at the schema layer.

---

### Cluster 6 — Backward-design + Decoding-the-Disciplines authoring discipline

**Paideia surface (from synthesis):** New ops doc `engine/operations/pdg-authoring-discipline.md` (or `product/operations/`); extension to existing seed-authoring ops; possibly a product ADR formalizing the methodology.

**Intersecting ADRs:**
- **Engine 0036** (expression contract for inward-facing documentation) — the new ops doc inherits the contract (front-matter, governance, line-budget).
- **Engine 0038** (expression contract for AI-authored code) — pattern analog. ADR 0038's three-layer expression contract (contract-first prose / mechanical gates / cold-context review) generalizes to Cluster 6's authoring-discipline-for-edges shape: outcomes-first / Decoding-interview / novice-translation / default-low-confidence.
- **Engine 0039** (universal expression contract across AI authoring patterns) — Cluster 6's discipline fits the universal contract's pattern instantiation table; ADR 0039's row-before-authoring rule applies.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Engine 0036 / 0038 / 0039** — Cluster 6 instantiates the universal expression contract for the PDG-authoring pattern (which doesn't yet have a row in the pattern-instantiation table). The cluster's ADR would add the row.

**Net-new substrate:** Yes. No current Paideia surface commits to backward-design as authoring discipline; the per-edge "default expert_confidence: low" commitment is wholly new; the Decoding-the-Disciplines interview as the bottleneck-identification mechanism is wholly new.

**Supersession candidates:** None.

**Amendment candidates:** None at ADR level. The existing seed-authoring discipline (per `engine/operations/seed-qa-discipline.md` and similar) needs operational extension, but Cluster 6's ADR introduces the discipline rather than amending an existing one.

**Adversarial probe:** Cluster 6's "every `hard_prerequisite` edge requires evidence from one of: (a) Decoding-the-Disciplines-style interview, (b) prior student performance data, (c) explicit expert rationale with `expert_confidence: low` until validated" is a validator-enforceable invariant on edge creation. This is a stronger gate than ADR 0016 (graph construction needs live validation) currently enforces. Session δ should decide whether the gate is mechanical (pre-commit hook check on new edges) or postcondition-audit (Phase 4 surface for human review). Mechanical enforcement requires the SQA census's per-edge evidence to be schema-resolvable; Cluster 7 (SQA extension) provides the field shape that enables the mechanical check.

---

### Cluster 7 — Graph predictive-validity extension to SQA discipline

**Paideia surface (from synthesis):** Extend `engine/operations/seed-qa-discipline.md` (or wherever SQA is documented); product ADR adopting predictive-validity framing; SQA evidence template extension.

**Intersecting ADRs:**
- **Product 0010** (continuous and contextual assessment) — ADR 0010's "Phase 8 evaluation harness" is the long-term consumer; Cluster 7 is the phase-1 of that evaluation, framed as graph-validity tracking.
- **Engine 0057** (adversarial stance for project health-check audits) — Cluster 7's "graph-validity-as-longitudinal-study" framing parallels 0057's adversarial-stance + freshness-probes-per-external-system pattern.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0010** — extends from per-learner-utterance rubric to per-edge predictive-validity tracking. The four new SQA evidence fields (`predicted_difficulty_level`, `inter_rater_agreement`, `disagreement_topic_cluster`, `revision_rate`) bring Phase-8-evaluation-harness data into the Phase-5-SQA-census loop.
- **Engine 0022** (periodic project health checks) — pattern analog. Cluster 7 frames SQA as longitudinal validity study just as ADR 0022 frames project health as longitudinal audit cadence.

**Net-new substrate:** No. SQA discipline exists; Cluster 7 extends the evidence-field set within that discipline.

**Supersession candidates:** None.

**Amendment candidates:** None.

**Adversarial probe:** Cluster 7's SQA-as-phase-1 framing assumes SQA shards remain the data-collection vehicle through Phase 7+. The SQA census was sized for Phase 5 production audit (8/20 shards complete at S-0169). Once Phase 5 closes fully, does SQA discipline continue as ongoing operational discipline, or does it retire? If it retires, Cluster 7's framing needs a successor data-collection mechanism. Session δ should clarify the SQA lifecycle envelope before committing to the predictive-validity extension. Additionally: Cluster 7's `inter_rater_agreement` field implies multiple auditors per edge; current SQA is single-auditor. Adding inter-rater discipline is a meaningful expansion of audit cost.

---

### Cluster 8 — Graph-topology bias mitigation

**Paideia surface (from synthesis):** Extension to existing memory drawer `feedback_anti_bias_implementation_discipline.md`; new product ADR (governance category); new ops doc for graph-canon census; integration with Cluster 4's equity metadata + tradition labels.

**Intersecting ADRs:**
- **Product 0001** (pedagogical edges, not historical) — Cluster 8's `alternative_routes` requirement on `hard_prerequisite` edges with high `canonical_importance` operates within the pedagogical-edges layer. Doesn't conflict; adds an authoring-time constraint.
- **Product 0006** (domain-agnostic architecture) — Cluster 8's tradition-label discipline reinforces 0006's commitment that no single tradition is privileged structurally.
- **Product 0008** (nodes are concepts, not thinkers) — `tradition_label` on a node is metadata, not identity. Cluster 8 must clarify that `tradition_label` is a tag on concept-level nodes, not a separate node type representing the tradition itself. Compatible with 0008 with that clarification.
- **Engine 0057** (adversarial stance for project health-check audits) — Cluster 8's "graph-canon census discipline" cadence (per health-check audit) plugs directly into 0057's audit-stance framework. The retire-candidate-recommendation rule from 0057 transfers to Cluster 8's canon-overrepresented-tradition surfacing.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Engine 0057** — extends adversarial-stance audits to include graph-topology bias as a per-audit input. The Forward-fit map subsection from 0057 (TEMPLATE.md sibling to Fit posture) gains a new check: "tradition representation balance" per the health-check audit's freshness-probes-per-external-system pattern.

**Net-new substrate:** Yes. Graph-topology bias is wholly uncovered by existing Paideia surfaces. The `tradition_label` field, the alternative-routes-required-for-canonical-edges rule, and the canon-census ops doc are all net-new.

**Supersession candidates:** None.

**Amendment candidates:** None at ADR level. The memory drawer `feedback_anti_bias_implementation_discipline.md` extension is documented in the synthesis (two-bias-surface partition); the drawer extension is not an ADR amendment.

**Adversarial probe:** Cluster 8 commits the strip-tradition-label-at-LLM-serialization-boundary discipline as the resolution of the CONFLICT identified in lens_sweep_adversarial L4.13 (named tradition labels for human contestation vs strip-identity-cues for LLM input). Under ADR 0065 (OSS+BYOK), LLM serialization happens client-side. The strip discipline must be enforced in the iOS client's prompt-assembly code, not in a server-side serialization step. This is an implementation-surface question Cluster 8's ADR should explicitly address — the existing anti-bias memory drawer was written when serialization was server-side. Session δ should verify the discipline survives the architectural shift.

---

### Cluster 9 — Instructional-spine architecture (foundational ADR)

**Paideia surface (from synthesis):** Large product ADR establishing teaching-layer architectural invariants; Phase 7+ master plan input.

**Intersecting ADRs:**
- **Product 0014** (Sonnet teaches, Opus reviews) — most-directly-related. Cluster 9's "PDG = instructional spine (authority); LLM = adaptive interface (operationalization); humans arbitrate" is the same load-bearing claim ADR 0014 commits at the role-split level. Cluster 9 extends to five-service architecture.
- **Product 0017** (Postgres + recursive CTEs over OWL/RDF) — Cluster 9's §6 tool-stack evaluation ("Postgres + JSONB + recursive CTEs vs Neo4j dual-layer") explicitly names ADR 0017's commitment as the revisit point. ADR 0017 is "revisitable at scale"; Cluster 9 forces the question at Phase 7+.
- **Product 0026** (persistent learner storage structural-not-substantive) — Cluster 9's no-silent-mutation rule across five services has 0026's privacy posture as a parallel: both commit "writes are constrained at the schema/contract level, not at the prompt level."
- **Product 0027** (rendering policy is the prompt-layer contract) — Cluster 9's "Pre-registered edit policies" is a structural counterpart to 0027's prompt-layer contract: ADR 0027 governs what the agent emits; Cluster 9 governs what edits are authorized.
- **Product 0085** (server-side mastery computation confirmed) — Cluster 9's analytics layer + review layer presume server-side computation per ADR 0085. Aligned.
- **Product 0086** (model-agnostic embedding storage) — Cluster 9's "graph store" includes entity-resolution embeddings per 0086's per-dim partition pattern.
- **Engine 0049** (scope-lock at boot, descope/reorder audit at shutdown) — pattern analog for Cluster 9's no-silent-mutation rule. ADR 0049's scope-lock at boot + descope/reorder audit at shutdown is precisely the pattern Cluster 9 transposes from build-apparatus to teaching-layer.
- **Engine 0051** (routine-mode and engine-loop foundation) — pattern analog for the staging-area architecture. ADR 0051's routine-mode scope_lock on auto_target.json is the build-apparatus existence proof that this constraint class is implementable. Cluster 9's `cluster body explicitly cites this as the precedent ("the build-apparatus no-silent-mutation machinery... is the existence proof").

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0014** — extends role split into five-service architecture. The 2-role pair (Sonnet teaches / Opus reviews) factors into roles operating within each of the five services (graph store / content store / LLM orchestration / analytics / review).
- **Product 0027** — extends prompt-layer contract from rendering-only to "rendering + edit-policy + staging-area" contract.
- **Product 0028** — extends bounded-contexts framework: ADR 0028's three input contexts (concept engagement / diagnostic / BYOB close reading) gain three more (instructor authoring / student authoring / analytics review) per Cluster 11's four workflows.
- **Product 0085 + 0086** — extends Phase 6 entry decisions into Phase 7+ architectural commitments.
- **Engine 0049 + 0051** — extends the no-silent-mutation pattern from build-apparatus to product-teaching-layer.

**Net-new substrate:** Partial. The five-service architecture as a named commitment is net-new; the no-silent-mutation rule at five-service granularity is net-new. Many implementations leverage existing patterns (per-row provenance from Cluster 1; per-edge confidence from Cluster 1; pre-registered policies parallel to engine ADR 0051 routine-mode allowed_paths).

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0014** — Consequences section names per-session context shape and Phase 6/7 implementation pointers. Cluster 9's five-service architecture would re-anchor the Consequences forward-pointer to Cluster 9's ADR. Light editorial amendment.
- **Product 0017** — Consequences section names the "revisitable at scale" trigger. Cluster 9's tool-stack §6 is the revisit. Amend 0017's Consequences to point at Cluster 9's tool-stack evaluation as the formal revisit decision (whether or not the revisit retains Postgres).

**Adversarial probe:** Cluster 9 is the largest single architectural ADR proposed (seven sub-decisions); under ADR 0084 (pushback-rule extraction step) it ABSOLUTELY triggers the extraction-step gate. The cluster body lists architectural invariants but doesn't enumerate load-bearing premises with falsifiers per ADR 0084's contract. Session δ MUST author the extraction-step subsection BEFORE the Decision section per ADR 0084 — running this gate is a discipline observation, not an Optional. Additionally: under ADR 0065 (OSS+BYOK) the "LLM orchestration" service operates client-side, not server-side; Cluster 9's five-service diagram needs to encode the on-device-vs-server-side split per service. The five services do NOT all run in the same execution surface. Session δ should clarify which services are server-side (graph store, content store, analytics, review) vs client-side (LLM orchestration) before drafting.

---

### Cluster 10 — Prompt template discipline + content store

**Paideia surface (from synthesis):** New ops doc `engine/operations/prompt-template-discipline.md`; content-store schema (subset of Cluster 9's five-service architecture); skill cascade (new skill or extension to existing `claude-api` discipline).

**Intersecting ADRs:**
- **Product 0011** (no hosted copyrighted material) — Cluster 10's "content store (approved excerpts + prompt templates)" potentially conflicts. Approved excerpts of copyrighted texts cannot be hosted per 0011's BYOB commitment.
- **Product 0027** (rendering policy is the prompt-layer contract) — this is Cluster 10's parent at the teaching-prompt level. ADR 0027 commits AGENT_INSTRUCTIONS.md as the contract artifact; Cluster 10 generalizes to multiple prompt templates with versioning + co-versioning + self-consistency. ADR 0027's "rendering policy is a contract artifact, not a tunable" discipline transfers.
- **Product 0028** (input-side scope structural-not-prompt) — bidirectional contract sibling per 0027 ↔ 0028 partition. Cluster 10's prompt templates inherit the same input-output contract structure.
- **Product 0086** (model-agnostic embedding storage) — Cluster 10's content store consumes embedding-storage substrate for retrieval of approved excerpts (when allowed).
- **Engine 0044** (skill conversion: recipe vs reference) — Cluster 10's "skill cascade (new skill or extension to existing claude-api discipline)" inherits the recipe-vs-reference partition. The prompt templates ARE recipes; the discipline ops doc is reference.

**Conflicting ADRs:**
- **Product 0011** (potential, requires scoping clarification) — Cluster 10 names "approved excerpts" in the content store. ADR 0011 forbids hosted/distributed copyrighted material; "approved excerpts" of copyrighted texts cross that boundary. Two reads: (a) approved excerpts = instructor-curated short fair-use snippets (potentially OK under fair-use doctrine for educational purposes; still risky under 0011's strict reading); (b) approved excerpts = openly-licensed or public-domain content only (0011-compatible). Session δ MUST scope this explicitly. The conflict admits resolution but cannot be silent.

**Extending ADRs:**
- **Product 0027** — extends from single AGENT_INSTRUCTIONS.md to multiple-template + versioned content store. ADR 0027's asymmetric-amendment discipline (additions = ENGINE_LOG-tracked; removals = superseding ADR) is the precedent.
- **Engine 0044** — extends Skill discipline to product-side teaching skills. Pattern analog.

**Net-new substrate:** No. Pattern exists (AGENT_INSTRUCTIONS.md is the precedent prompt-as-contract; engine memory boot orchestrator is the precedent for inline-rendered context). Cluster 10 multiplies the surface and adds versioning + self-consistency.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0027** — Consequences section names AGENT_INSTRUCTIONS.md as the contract artifact at the repo root. Cluster 10's content-store would relocate prompt templates to a content store directory. ADR 0027 needs amendment to record AGENT_INSTRUCTIONS.md as one of multiple prompt-template artifacts in the content store, OR Cluster 10 keeps AGENT_INSTRUCTIONS.md in its repo-root location and adds new templates beside it. Editorial decision for Session δ.

**Adversarial probe:** Cluster 10's "self-consistency requirement for graph-refinement outputs: sample N=3 outputs; only surface a candidate edge to the review layer if ≥2 of 3 agree" is an N=3 LLM-call multiplier on every candidate-edge proposal. Under ADR 0065 (OSS+BYOK) this is the user's API spend — the user pays for 3 calls per edge proposal. The cost-shifted-to-user reality means N=3 must be defensible to the user's per-edge spend. The cluster body doesn't address this. Session δ should clarify whether N=3 is fixed or user-tunable, and whether the "32% pre-mitigation failure rate" from paper_2:L50 justifies the cost at single-user scale.

---

### Cluster 11 — Four sample workflows + role-checkpoint partitioning

**Paideia surface (from synthesis):** Phase 7+ teaching-app architecture ADR; new ops doc for workflow-pattern selection.

**Intersecting ADRs:**
- **Product 0014** (Sonnet teaches, Opus reviews) — the role split survives across all four workflows; Cluster 11 specifies which role does what in each pattern.
- **Product 0028** (input-side scope structural-not-prompt) — the four workflows add new bounded contexts (instructor authoring surface; student authoring surface) beyond 0028's original three. ADR 0028's purpose-not-topic discrimination transfers to the new surfaces.
- **Product 0027** (rendering policy) — rendering policy applies in any workflow with a teaching-agent turn; ADR 0027's forbidden-tokens enumeration applies across workflows.
- **Engine 0049** (scope-lock at boot) — pattern analog for the no-silent-mutation gate in the instructor-authored workflow per adversarial E.1.2.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0028** — extends bounded-contexts framework from 3 (concept engagement / diagnostic / BYOB) to 5+ (adding instructor-authored + student-authored + adaptive-branching as distinct contexts). The exit-affordance + purpose-not-topic discipline transfers.
- **Product 0014** — extends Sonnet/Opus role partition to four-workflow granularity.

**Net-new substrate:** Partial. The four workflows are new teaching-pattern commitments; the role-checkpoint partition per workflow is new. The architectural shape (bounded contexts; structural-not-prompt enforcement) is established.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0028** — Consequences section names "three bounded input contexts (V1)." Cluster 11 introduces more bounded contexts at Phase 7+. Light amendment to record the V1-vs-Phase 7+ context-count growth, OR the cluster's ADR carries the new contexts independently. Editorial decision.

**Adversarial probe:** Cluster 11 names "automated prerequisite inference from traces" as one of the four workflows but flags it as "highest governance burden; gated on Cluster 9's no-silent-mutation rule." Under ADR 0065 (OSS+BYOK), traces are derived client-side per ADR 0026 (structural-not-substantive); the trace-informed-revision workflow needs to operate on server-side aggregate analytics, not on per-learner raw traces. Cluster 11 doesn't address the BYOK-derived constraint on trace availability. Session δ should clarify: is the trace-informed workflow's Opus consumer reading the same `learner_events` table ADR 0014 commits to, or a separate aggregated trace store? Implementation-shape, but with significant data-availability implications.

---

### Cluster 12 — Scaffolding fade trajectory + learner-state schema

**Paideia surface (from synthesis):** Phase 7+ schema (`learner_state` table); Phase 7+ teaching-app scaffold-fade module; product ADR; privacy classification per field (intersects Cluster 15).

**Intersecting ADRs:**
- **Product 0004** (relational learner model) — Cluster 12's `learner_node_state` table IS the operationalization of ADR 0004's relational commitment. ADR 0004 commits to relational; Cluster 12 specifies the relational table at field-level.
- **Product 0010** (continuous and contextual assessment) — Cluster 12's three-state scaffold (State 0/1/2) IS the operationalization of ADR 0010's scaffolding-proximity discount. ADR 0010 commits the rubric discipline; Cluster 12 commits the cross-encounter state machine.
- **Product 0013** (mastery verification organic escalation) — Cluster 12's `visit_count` + state transitions feed ADR 0013's callback selection. Aligned.
- **Product 0014** (Sonnet teaches, Opus reviews) — Cluster 12's `learner_node_state` is the structured input to Sonnet's per-turn context. ADR 0014's pedagogical-degradation discipline (absorbed from ADR 0029 via ADR 0065) maps to Cluster 12's state transitions.
- **Product 0015** (event-sourced learner model) — load-bearing. Cluster 12's `mastery_probability` field MUST be derived from events per 0015's append-only invariant. ADR 0015 commits "mastery is derived state, not a stored flag" + "snapshot table caches recent computation, source of truth is the event log." Cluster 12's `learner_node_state` is the new snapshot/cache shape.
- **Product 0026** (persistent learner storage structural-not-substantive) — Cluster 12's `recent_errors` jsonb array, `help_seeking_pattern` jsonb, `active_misconception_ids` array must respect 0026's structural-not-substantive discipline. These are bounded structural records, not free-text — compatible.
- **Product 0031** (erasure mechanism and individual-only regime) — Cluster 12's `learner_session_token` + identifier-table separation pattern aligns with ADR 0031's hard-delete-with-cascade discipline. `consent_version` field per Cluster 12 is new, anticipates Cluster 15.
- **Product 0085** (server-side mastery computation confirmed) — Cluster 12's state computation runs server-side per 0085. Aligned.

**Conflicting ADRs:** None identified (provided the alignment with ADR 0015's source-of-truth-is-events discipline holds).

**Extending ADRs:**
- **Product 0004** — extends from relational-commitment to table-level schema.
- **Product 0015** — extends event-sourcing pattern with the new `learner_node_state` snapshot table. The snapshot is cache; events remain source per 0015.
- **Product 0014** — extends per-turn context shape with the new fields (mastery_probability, visit_count, active_misconception_ids).

**Net-new substrate:** Partial. The `learner_node_state` table is net-new; the three-state scaffold approximation is net-new; many specific fields (`active_misconception_ids`, `mastery_estimate_calibration_flag`, `consent_version`) are net-new. The pattern of "snapshot/cache table derived from event log" is established per 0015.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0004** — Consequences section is high-level. Cluster 12's `learner_node_state` schema would land as the concrete operationalization; ADR 0004 gains a forward-pointer in See-also.
- **Product 0026** — Consequences section enumerates structural-not-substantive surfaces. Cluster 12's new jsonb fields (`recent_errors`, `help_seeking_pattern`) need to be confirmed as structural records per ADR 0026's discipline. Light amendment to add Cluster 12's new fields to the enumeration.

**Adversarial probe:** Cluster 12 commits the 0.4 and 0.7 mastery-probability thresholds for state transitions (State 0→1 at ≥0.4; State 1→2 at ≥0.7). These thresholds are not derived from any existing ADR. ADR 0010's rubric discipline says "the defaults live in `docs/learner-model.md` and are revisitable as evidence accumulates (Phase 8 evaluation harness)" — Cluster 12's thresholds inherit this revisability-but-need-baseline pattern. Session δ should clarify: are the 0.4/0.7 defaults provisional pending Cluster 14's calibration protocol (which the cluster body names as a precondition for multilingual cohorts), or are they baked in until Cluster 16's evaluation infrastructure produces falsifying evidence? The latter is consistent with ADR 0030's most-common-state default rationale. Also: ADR 0085's "Phase 7 formula-stability review" is the natural co-evaluation surface for these thresholds — Cluster 12 should explicitly join that review.

---

### Cluster 13 — Alternative-entry-route support + pluralism reserve

**Paideia surface (from synthesis):** `product/seed-graph/` — `entry_route_type` attribute on incoming edges (extends Cluster 2; Tier A migration per adversarial E.3.2 split); Phase 7+ teaching-app path-selector logic (Tier D); integration with Cluster 8's tradition labels.

**Intersecting ADRs:**
- **Product 0001** (pedagogical edges, not historical) — `entry_route_type` is metadata on pedagogical edges; ADR 0001's commitment to pedagogical-prerequisite-edges holds. Cluster 13's tag enriches the metadata, doesn't reopen the edge-semantic.
- **Product 0007** (cross-domain porosity) — Cluster 13's "alternative entry routes" intersect ADR 0007's cross-domain edges. A cross-domain entry route is one kind of alternative; Cluster 13's `entry_route_type` enum (`case_based`, `conceptual`, `methodological`, `historical`) operates within domain as well. Limited overlap.
- **Engine 0016** (graph construction needs live validation) — Cluster 13's validator soft-warn ("any node where 100% of incoming `hard_prerequisite` edges share the same `entry_route_type`") lands in ADR 0016's graph-audit surface.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Cluster 2's edge schema** (not yet an ADR) — `entry_route_type` is an Edge-schema extension promoted to Tier A per adversarial E.3.2.

**Net-new substrate:** Yes. No current Paideia surface encodes entry-route classification; the schema field + the path-selector pluralism rule + the path-agnostic argument scoring discipline are all net-new.

**Supersession candidates:** None.

**Amendment candidates:** None.

**Adversarial probe:** Cluster 13's "no canonical-path enforcement" rule could be in tension with ADR 0017 (Postgres + recursive CTEs over OWL/RDF). ADR 0017 commits Postgres recursive CTEs as the traversal substrate; recursive CTEs return paths-in-traversal-order, not paths-classified-by-route-type. Cluster 13's path-selector that surfaces "at least two distinct `entry_route_type` paths" needs additional query infrastructure: either pre-computed alternative-paths by route type (materialized closure) or runtime classification at query time (additional cost). Session δ should clarify whether the path-selector is a real-time query against recursive CTE results filtered by entry_route_type, or a pre-computed alternative-paths cache. Performance + freshness tradeoff.

---

### Cluster 14 — LLM-mediated bias mitigation (output side)

**Paideia surface (from synthesis):** Phase 7+ governance ADR; new ops doc for LLM output audit; skill cascade (extension to `claude-api` discipline); intersects existing anti-bias mechanism.

**Intersecting ADRs:**
- **Product 0027** (rendering policy) — Cluster 14's "pre-registered scoring prompt versioning" extends 0027's prompt-as-contract discipline to scoring prompts specifically.
- **Engine 0067** (gitleaks pre-commit secret scanning) — pattern analog for periodic-audit-at-commit. Cluster 14's "multilingual output sampling. Periodic audit: same input through LLM in N languages" is the same shape as a periodic-audit category.
- **Engine 0068** (bandit SAST pre-commit and CI) — pattern analog for periodic + commit-time + CI gating of LLM-mediated outputs.
- **Engine 0070** (project-wired /review skill) — pattern analog. ADR 0070's anti-rationalization table parallels Cluster 14's "critic or coach, not final judge" framing.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0027** — extends prompt-layer contract to scoring prompts specifically. Versioning + co-versioning are new constraints joining 0027's existing rendering-prompt contract.

**Net-new substrate:** Yes. The output-side audit cadence + multilingual sampling + scoring calibration against instructor rubrics + override threshold for repeated misconception routing are all net-new mechanisms. The existing anti-bias mechanism (per memory drawer `feedback_anti_bias_implementation_discipline.md`) covers input-boundary only.

**Supersession candidates:** None.

**Amendment candidates:** None at ADR level.

**Adversarial probe:** Under ADR 0065 (OSS+BYOK), the LLM call happens client-side with the user's own key. Cluster 14's "multilingual output sampling. Periodic audit: same input through LLM in N languages" requires N additional LLM calls per audit cycle, paid by the user. The audit's cadence + sample size determines the user-side spend impact. Cluster 14 doesn't explicitly address this. Session δ should clarify whether the audit runs against the maintainer's reference model (separate from the user's per-session use) OR against the user's own deployment. The former requires maintaining a reference Anthropic account (post-BYOK departure); the latter shifts cost to every user. Major architectural question.

---

### Cluster 15 — Privacy / FERPA / NIST alignment + override logging + transparency reports

**Paideia surface (from synthesis):** Phase 7+ governance ADR; new ops doc `engine/operations/nist-genai-alignment.md` (or product/operations/); RLS policy design; consent management UI; named-cadence schedules.

**Intersecting ADRs:**
- **Product 0011** (no hosted copyrighted material) — privacy posture sibling; both commit structural constraints over prompt constraints.
- **Product 0026** (persistent learner storage structural-not-substantive) — load-bearing precedent. Cluster 15's RLS + consent + transparency mechanisms operate within 0026's structural-only persistence regime.
- **Product 0031** (erasure mechanism and individual-only regime) — direct conflict on cohort-tracking scope (see Conflicting section).
- **Product 0065** (OSS pivot and BYOK disposition) — load-bearing. The OSS pivot reopens the scope question Cluster 15 must address: Paideia ships individual-only per ADR 0031; OSS deployers may extend to institutional regimes that need FERPA + NIST + cohort discipline.
- **Engine 0048** (HANDOFF.md narrowed; Issues for cross-session deferrals) — pattern analog for the override events table + transparency reports surface. ADR 0048's disposition discipline maps cleanly to Cluster 15's per-override-event dispositions.

**Conflicting ADRs:**
- **Product 0031** (load-bearing conflict, requires Session δ scoping decision) — ADR 0031 settled OQ-PRIVACY-B as moot (no institutional regime; cohort_id removed; "the institutional schema provisions in `docs/architecture.md` become dead-weight"). Cluster 15's transparency reports include `subgroup_routing_discrepancies` — subgroup analysis requires cohort/grouping data, which ADR 0031 removed. Under ADR 0065 (OSS pivot), third-party deployers may want to layer institutional features back on. Cluster 15's ADR must explicitly scope: (a) Paideia's shipped surface remains individual-only per ADR 0031 (Cluster 15's transparency reports omit subgroup analysis OR limit to individual self-comparison); (b) Cluster 15 reopens institutional-regime scope under OSS for third-party deployers (ADR 0031 amendment required to record the scope expansion). Conflict admits resolution; choice has substantial downstream implications.

**Extending ADRs:**
- **Product 0026** — extends structural-not-substantive persistence with operational governance machinery (named cadence + named actor per check; transparency report template; override events table).
- **Engine 0048** — extends disposition discipline to teaching-layer override events.

**Net-new substrate:** Partial. The override events table is net-new; the named-cadence + named-actor matrix per check is net-new; the NIST four-control mapping is net-new at product level. The structural-not-substantive precedent + the disposition discipline are established.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0031** — Decision section says "(2) Institutional vs. individual regime: individual only. The project has no institutional regime." Under ADR 0065 OSS pivot, third-party deployers can implement institutional regimes from the open codebase. Cluster 15 may need 0031 amendment recording the scope partition: Paideia's shipped binary remains individual-only; the OSS codebase admits third-party institutional extensions. The cohort_id removal commitment can survive at the shipped-binary level while the codebase admits the option. OR Cluster 15 scopes to Paideia-only (individual-only) and a future ADR reopens institutional scope when an actual third-party deployer arrives. Session δ chooses.

**Adversarial probe:** ADR 0031's foundation rests on the personal-project-disposition framework (ADR 0032, since superseded by ADR 0035, since superseded by ADR 0065). The institutional-foreclosure half of ADR 0065 commitment 4 explicitly preserves the institutional foreclosure for Paideia itself but is silent on third-party deployers under OSS. Cluster 15's privacy framework is one of the first ADRs to test the OSS-pivot's edge — what does Paideia commit to for itself, and what does it leave open for third-party deployers? This is a meta-question Session δ may need to resolve at the policy level before Cluster 15's specific schema commitments can settle. Additionally: ADR 0026's GDPR Article 9 reasoning (philosophical / religious / political beliefs as special-category data the structural-not-substantive discipline keeps out of persistent storage) extends to Cluster 15's `consent_version` design — what does consent cover when the structural discipline already minimizes the substantive data surface?

---

### Cluster 16 — Learner-outcome evaluation infrastructure

**Paideia surface (from synthesis):** Phase 7+ evaluation ADR; new ops doc for evaluation methodology; IRB-side preparation; intersects Cluster 7 (graph-validity in SQA) and Cluster 17 (anomaly detection).

**Intersecting ADRs:**
- **Product 0010** (continuous and contextual assessment) — ADR 0010's "Phase 8 evaluation harness" is Cluster 16's natural home. Cluster 16 IS the evaluation harness specification.
- **Product 0013** (mastery verification organic escalation) — Cluster 16's outcome metrics (performance on threshold-concept tasks; delayed retention) consume ADR 0013's organic-verification evidence stream.
- **Product 0014** (Sonnet teaches, Opus reviews) — Cluster 16's evaluation produces aggregate cross-session patterns; ADR 0014's Opus-reviewer reads aggregated patterns, not individual data. Aligned.
- **Engine 0022** (periodic project health checks) — pattern analog for the longitudinal evaluation cadence.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0010** — extends from per-turn rubric to longitudinal outcome bundle (5 metrics + comparative experimental designs + HTE subgroup analysis + process-quality measurement + DBR methodology + node-linked survey + three-arm comparison study).
- **Engine 0022** — extends periodic-cadence pattern from build-apparatus to learner-outcome evaluation.

**Net-new substrate:** Yes. The five-metric outcome bundle, comparative experimental designs (cluster-randomized, cross-over, three-arm), HTE pre-registration discipline, process-quality measurement infrastructure (discourse-coding pipeline), and IRB protocol structure are all net-new at the product-ADR level.

**Supersession candidates:** None.

**Amendment candidates:** None.

**Adversarial probe:** Cluster 16's "node-linked student survey instrument" (NOT generic satisfaction; items name specific graph elements) requires a survey-instrument schema that Paideia doesn't currently have. The schema needs to handle versioning (graph nodes can be deprecated per ADR 0021; survey items pointing at deprecated nodes need lifecycle handling). Additionally: ADR 0031 (erasure mechanism + individual-only regime) governs the data-collection footprint Cluster 16 implies. The three-arm comparison study with cluster-randomization assumes cohort/section/unit grouping — same scope question Cluster 15 raises. Session δ should resolve Cluster 15's scope question BEFORE Cluster 16's experimental-design commitments (both rest on the institutional-scope decision).

---

### Cluster 17 — Anomalous routing detection + three-way disambiguation

**Paideia surface (from synthesis):** Phase 7+ analytics-layer module; integrated with Cluster 9's review layer; ops doc.

**Intersecting ADRs:**
- **Product 0010** (continuous and contextual assessment) — Cluster 17's "satisfy-and-fail" anomaly consumes ADR 0010's per-utterance rubric evidence. The three-way disambiguation operates against the rubric's evidence stream.
- **Product 0013** (mastery verification organic escalation) — Cluster 17's "bypass-and-succeed" anomaly type contradicts the prerequisite claim; this is precisely the case ADR 0013's "callback references during teaching of downstream concepts double as verification probes" generates as falsifying evidence.
- **Engine 0042** (soft-warn lifecycle archive canon) — pattern analog for Cluster 17's analytics-layer detection rules. Three anomaly types map to three soft-warn categories with confidence thresholds; the 3-of-5 persistence-detection pattern transfers.
- **Engine 0049** (scope-lock at boot, descope/reorder audit at shutdown) — pattern analog for Cluster 17's "outputs candidate edges or candidate misconception nodes, NOT silent graph mutations." ADR 0049's audit-time descope-reorder check is the analytical sibling.

**Conflicting ADRs:** None identified.

**Extending ADRs:**
- **Product 0014** (Sonnet teaches, Opus reviews) — Cluster 17 IS the candidate-edge generation half of Opus's review responsibility. ADR 0014 commits Opus reads tension records + proposes graph edits via the confidence-weighted pipeline; Cluster 17 specifies the anomaly-detection rules that drive specific edit-class proposals.
- **Engine 0042 + 0049** — extends build-apparatus soft-warn + scope-discipline patterns to the teaching-layer analytics surface.

**Net-new substrate:** Yes. The three anomaly types with distinct interventions, the three-way disambiguation discipline, the instructor dashboard queue, and the cohort-tracked predictive-validity feedback loop are all net-new mechanisms.

**Supersession candidates:** None.

**Amendment candidates:**
- **Product 0014** — Consequences section says "Opus reviews — runs as a scheduled batch job, reads the accumulated tension log, proposes graph edits..." Cluster 17 specifies HOW Opus reads. Light extension to 0014's Consequences listing Cluster 17 as the specific anomaly-detection methodology Opus employs.

**Adversarial probe:** Cluster 17's "cohort tracking for predictive-validity feedback loop: anomaly events tagged with `cohort_id`" reopens the cohort_id question ADR 0031 removed. Same conflict shape as Cluster 15. Cluster 17's `cohort_id` could mean (a) self-defined learner cohort (anonymous grouping by enrollment timing, no institutional structure) — 0031-compatible; (b) institutional cohort — 0031-conflict. Session δ should coordinate the cohort_id question across Clusters 15 + 16 + 17 — all three need the answer. Additionally: under ADR 0065 (OSS+BYOK), individual users' anomaly events live in their own Supabase rows; cross-cohort aggregation requires cross-user query authorization that the individual-only regime doesn't naturally permit. Architectural-level question.

---

## Cross-cluster integration audit

**ADRs touched by multiple clusters (≥3 clusters):**

| ADR | Clusters touching | Most common relationship | Implication |
|---|---|---|---|
| Product 0001 (pedagogical edges) | 2, 8, 13 | Intersecting / Extending | Session δ ADR for Cluster 2 should be coordinated with 8 + 13 to avoid recursive ADR 0001 amendments |
| Product 0008 (concept nodes not thinkers) | 4, 5, 8 | Intersecting (potential conflict at C4) | The `node_type` enum question (C4) must settle before C5's misconception-node-type and C8's tradition-label placement can lock |
| Product 0010 (continuous contextual assessment) | 3, 5, 6, 7, 16, 17 | Intersecting / Extending | Most-intersecting product ADR. The rubric is load-bearing across substrate (C5 misconceptions affect rubric), discipline (C6, C7), and evaluation (C16, C17) |
| Product 0014 (Sonnet teaches, Opus reviews) | 3, 6, 9, 11, 12, 17 | Intersecting / Extending | Amendment candidate for Clusters 3 (input shape), 9 (five-service expansion), 17 (anomaly detection methodology). Risk: 3 separate amendments accreting on 0014. Better: Cluster 9's ADR amends 0014 once at five-service expansion; downstream Clusters 3, 17 cite Cluster 9, not 0014 directly |
| Product 0017 (Postgres + recursive CTEs) | 1, 3, 9, 13 | Intersecting (revisit candidate at C9) | C9's §6 tool-stack evaluation is the formal revisit. C1 + C3 + C13 add traversal-cost considerations that affect the revisit's premise base |
| Product 0026 (structural-not-substantive storage) | 12, 15 | Load-bearing / Amendment | C15's privacy framework lives within 0026's discipline; C12's `learner_node_state` new jsonb fields need 0026 amendment to confirm they remain structural |
| Product 0027 (rendering policy) | 3, 10, 11, 14 | Intersecting / Extending / Amendment | C10's content-store relocation is the main amendment trigger; C14's scoring-prompt versioning extends the contract surface |
| Product 0028 (input-side scope) | 3, 10, 11 | Intersecting / Extending | C11's four workflows extend bounded-contexts framework; C10's prompt-discipline contract co-exists |
| Product 0031 (erasure mechanism + individual-only) | 15, 16, 17 | Conflict (load-bearing at C15) | The cohort_id / institutional-scope question must settle once across C15 + C16 + C17. ADR 0031 amendment OR scope-clarification ADR is the single resolution |
| Product 0065 (OSS pivot + BYOK) | 8, 10, 11, 14, 15 | Architectural reframe | Cluster ADRs must explicitly address on-device-vs-server-side execution per cluster's mechanisms. The five clusters touching 0065 each have a BYOK-derived implementation question Session δ must resolve |
| Engine 0042 (soft-warn lifecycle) | 1, 4, 17 | Intersecting (pattern analog) | New soft-warn categories from clusters inherit the canonical archive + 3-of-5 persistence-detection lifecycle |
| Engine 0049 / 0051 (scope-lock + routine-mode) | 9, 17 | Pattern analog | The no-silent-mutation pattern from build-apparatus is the existence proof for Cluster 9's teaching-layer commitment |

**Cluster-to-cluster ADR conflicts (cross-cluster):**

- **C4 (node_type enum) ↔ C5 (misconception encoding) ↔ C8 (tradition_label placement)** — all three require the `node_type` enum question to settle. If `node_type` is concept-level-only (ADR 0008 compatible), C5's misconception-node-type and C8's tradition-on-concept-node both land cleanly. If `node_type` admits work/tradition shapes, ADR 0008 amendment cascades through C5 + C8.
- **C1 (per-edge confidence) ↔ C7 (SQA evidence extension)** — Cluster 7 names "Combine with Cluster 1's `disagreement_flag` field on edges." C7's four new SQA fields populate C1's edge columns; the two clusters must land in dependency order (C1 first, then C7's extension).
- **C2 (edge-type taxonomy) ↔ C13 (entry_route_type)** — Cluster 13 explicitly "extends Cluster 2's edge schema." The two ADRs may land separately but the schema migrations must be coordinated.
- **C3 (goal-relative parameterization) ↔ C12 (learner-state schema) ↔ C13 (alternative-route path-selector)** — all three contribute to the path-selector signature `get_path(target_node_id, learning_outcome_id, learner_state)`. The three function-signature designs must be coordinated; otherwise the path-selector API is over-determined or under-specified.
- **C9 (instructional-spine architecture) ↔ everything in Tier D** — Clusters 10, 11, 12, 13 are all named as children of Cluster 9 in the synthesis. Session δ's foundational-ADR sequencing should land Cluster 9 first.
- **C15 (privacy/FERPA/NIST scope) ↔ C16 (evaluation experimental design) ↔ C17 (cohort-tracked anomaly feedback)** — all three rest on the institutional-vs-individual scope decision (the ADR 0031 + ADR 0065 OSS partition question). Single decision should resolve all three.

---

## Phase 6 master-plan implications subsection

Per [`synthesis.md`](synthesis.md) "Phase 6 master-plan-input subsection," the choice is binary:

- **Option A — Expand Phase 6 scope to include Tier A substrate (Clusters 1, 2, 4 at minimum) before SEP backfill.**
- **Option B — Proceed narrow; accept a follow-up re-backfill.**

**This Session α reaffirms the synthesis's framing and adds the following ADR-level evidence:**

### ADRs constraining Option A (expand-scope)

- **Product 0086** (model-agnostic embedding storage) — already commits the per-dim partition pattern. The first Phase 6 migration is the one authoring `node_embeddings_<dim>` partition tables. If Cluster 4's node schema redesign lands first, embeddings are computed on the redesigned columns (`node_type`, `disciplinary_domain`, `granularity`, `canonical_sources`, `misconceptions`) — semantically richer.
- **Product 0087** (two-hop neighborhood retrieval shape) — already commits to `prereq + historical_influence` edge filter for two-hop traversal. Cluster 2's three-layer schema (adds `conceptual_relatedness`) means ADR 0087's two-hop edge filter would need to extend to three edge types if `conceptual_relatedness` is also semantically relevant to recognition routing.
- **Product 0088** (SEP chunk-resolver index) — already commits `sep_chunks` junction table. Cluster 10's content store + Cluster 11's instructor-authored workflow both intersect SEP onward-reading at the teaching layer. The 380-node SEP backfill assumes the current node table shape; if Cluster 4 lands, backfill operates on the new shape (more semantically grounded mappings).

### ADRs constraining Option B (proceed-narrow)

- **Product 0030** (per-node confidence_level) — already committed. If Phase 6 narrow lands embeddings on current nodes (`confidence_level` + `provenance` + `confidence` axes only), the re-backfill required after Cluster 4 would recompute embeddings on the new `node_type` + `disciplinary_domain` axes — semantic shift, not just additive enrichment.
- **Product 0085** (server-side mastery computation confirmed) — Phase 6 entry is unblocked at the architectural level; the question is purely about substrate-richness sequencing, not architectural-decision sequencing.

### Additional Session α evidence

The cross-cluster integration audit above surfaces three coordination requirements that strengthen Option A:

1. **Cluster 9 (instructional-spine architecture) is named as the parent of Clusters 10, 11, 12, 13.** Phase 6 entry without Cluster 9 means downstream Phase 7+ teaching-layer ADRs land without a coherent foundation.
2. **Cluster 15 (privacy/FERPA/NIST scope question) blocks Clusters 16 + 17** — the institutional-vs-individual scope decision must settle before evaluation infrastructure or anomaly detection can specify experimental designs.
3. **The Tier A cluster ordering** (C1 → C4 → C2 → C3 → C5 per synthesis cross-cluster integration notes) is roughly 5 session-sized work units. Adding Cluster 1's per-edge confidence + Cluster 4's node schema enables Cluster 6's authoring-discipline-with-confidence-defaults — even further downstream value compound.

### Recommendation Session α surfaces (for Session δ deliberation)

Lean Option A — the Cluster 4 + Cluster 1 substrate enrichment materially affects the semantic content of embeddings, and the re-backfill cost under Option B materially exceeds the upfront authoring cost under Option A. **Caveat:** this lean is a recommendation only; the actual scope decision rests on Session δ's ADR for Phase 6 scope (the four-option ADR named in the HANDOFF's Session δ description).

**Session δ ADR sequencing recommendation:** author the Phase 6 scope ADR first (Option A vs B), then the tool-stack ADR, then the learning-outcome taxonomy ADR, then the product-trajectory confirmation ADR. Each subsequent ADR's premise base depends on the prior settled.

---

## Top-level adversarial findings

This map surfaces three top-level concerns Session δ should not skip:

1. **The `node_type` enum question (ADR 0008 compatibility)** spans Clusters 4, 5, 8. A single Session δ adjudication of "is the enum concept-level-only or does it admit work/tradition shapes" resolves three cluster-level questions. Defer this adjudication and three clusters' ADRs delay simultaneously.

2. **The institutional-vs-individual scope question (ADR 0031 amendment)** spans Clusters 15, 16, 17. Under ADR 0065 OSS pivot, the question is no longer "what regime does Paideia ship?" but "what regime does Paideia ship vs. what regime does the OSS codebase admit for third-party deployers?" The answer should land at the policy level (a meta-ADR or Cluster 15's ADR) before downstream cluster ADRs commit specific schemas.

3. **The BYOK execution-surface question (ADR 0065 implications)** spans Clusters 8, 10, 11, 14, 15. Each cluster has on-device-vs-server-side execution implications that the cluster body under-specifies. Session δ should produce a per-cluster execution-surface table (what runs client-side vs server-side under BYOK) BEFORE drafting individual cluster ADRs.

These three adjudications can be resolved in a single Session δ deliberation (likely the foundational-ADR session producing the four ADRs the HANDOFF names) — surfacing them here means Session δ's plan-mode reading can target them deliberately.

---

## See also

- [`synthesis.md`](synthesis.md) — the 17 cluster bodies this map cross-references.
- [`adversarial_review.md`](adversarial_review.md) — adversarial-pass calibration; surfaced 22 findings; 3 critical landed inline; 19 carried to Issue bodies.
- [`issue_drafts.md`](issue_drafts.md) — 17 ready-to-file Issue drafts; **NOT to fire before Session ζ** per quality-first posture.
- HANDOFF.md "PDG papers extraction — pre-phase deliberation plan ready for interactive pickup" — Session α-ζ sequence and posture.
- [`engine/STATE.md`](../../STATE.md) Current row — ADR count (92) at S-0199 boot.
- [`engine/adr/README.md`](../../adr/README.md) — engine ADR index.
- [`product/adr/README.md`](../../../product/adr/README.md) — product ADR index.
- [ADR 0084](../../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — pushback-rule extraction step; relevant for Session δ's foundational ADRs (Cluster 9 especially triggers all three high-stakes classes per ADR 0084).
- [ADR 0077](../../adr/0077-adr-template-alternatives-considered-section.md) — Alternatives Considered section required for all new ADRs.
