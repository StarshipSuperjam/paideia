# Issue drafts — PDG papers extraction

> Phase F output. One Issue draft per integrated cluster from `synthesis.md`, with adversarial fixes incorporated. Ready for `gh issue create --body "..."` after user adjudication of title / label / body wording.
>
> Source artifacts (cite in each Issue): [`synthesis.md`](./synthesis.md), [`adversarial_review.md`](./adversarial_review.md), [`sub_concerns_checklist.md`](./sub_concerns_checklist.md), [`extraction_paper_1.md`](./extraction_paper_1.md), [`extraction_paper_2.md`](./extraction_paper_2.md), [`lens_sweep_*.md`](./).

---

## Issue 1 — [Cluster 1] Edge contestability substrate (confidence + provenance + counterexamples + version)

**Labels:** `enhancement`, `tech-debt`, `priority:urgent` (foundational for Tier A)
**Title:** `feat(seed-graph): add edge contestability substrate (confidence + provenance + counterexamples + version history)`

**Summary**

Add per-edge contestability fields to the seed-graph edges table: a 3-source confidence model (`expert_confidence`, `trace_confidence`, `llm_confidence`, `disagreement_flag`), 5-field provenance jsonb (`source_text`, `course_context`, `version`, `reviewer`, `rationale`), counterexamples jsonb array, version integer, review_status enum, last_reviewed timestamp. Sourced from PDG papers extraction (see `engine/build_readiness/pdg_papers_extraction/synthesis.md` Cluster 1).

**Why**

The current 533-edge graph has no mechanism for expressing that a pedagogical claim is contestable, unvalidated, or revisable. Papers establish (per `paper_2:L82` + `paper_1:L162`) that confidence + provenance + counterexamples form a single atomic governance substrate; missing any one renders the others unmoored. Three lens-sweeps independently converged on this finding (substrate, adversarial, evaluation).

**Mechanism**

- Migration adds 9 columns to `edges` table per synthesis.md Cluster 1.
- Validator soft-warn: any edge with `expert_confidence: high` AND empty `counterexamples` AND empty `provenance.rationale` → unguarded high-confidence claim.
- Companion `graph_versions` table linking version identifiers to active edge/node sets per course/cohort.

**Sub-concerns addressed:** L1.4, L1.5, L1.7, L1.14, L4.9, L4.10 (partial), L3.9 (partial)

**Dependencies:** none — foundational; lands first in Tier A

**Acceptance criteria**

- [ ] Product ADR drafted with contestability-substrate decision recorded
- [ ] Migration adds 9 edge columns + `graph_versions` table
- [ ] Validator soft-warn fires on unguarded high-confidence edges
- [ ] All 533 existing edges populate `expert_confidence: low` (default) + empty provenance until SQA validation

---

## Issue 2 — [Cluster 2] Edge-type taxonomy expansion + three-relation layered separation + entry_route_type field

**Labels:** `enhancement`, `tech-debt`
**Title:** `feat(seed-graph): expand edge-type taxonomy + add conceptual_relatedness layer + entry_route_type field`

**Summary**

Replace the 2-edge-type schema (`pedagogical_prerequisite` + `historical_influence`) with a layered taxonomy: pedagogical_dependence (subtypes: `hard_prerequisite`, `soft_prerequisite`, `helpful_bridge`, `co_requisite`, `contrastive_link`, `misconception_remediation`, `example_of`, `supports`, `assessed_before`, `unlearning_required_before`), historical_influence (subtypes: `influenced_by`, `received_via`, `reacted_against`), and a new conceptual_relatedness layer (subtypes: `affinity_with`, `contrasts_with`, `same_problem_family`). Plus `entry_route_type` enum attribute (`case_based`, `conceptual`, `methodological`, `historical`) on incoming edges.

**Why**

Current schema collapses ~10 distinct pedagogical relations into one type and misses the conceptual_relatedness layer entirely (per `paper_1:L22-26`, `paper_2:L15`, `paper_2:L19`). Per adversarial review E.3.2, `entry_route_type` is an authoring-time substrate concern that must land with the taxonomy, not deferred to Phase 7+.

**Critical mass-retyping decision (per adversarial E.2.1 + E.11.1):**

The 516 existing `pedagogical_prerequisite` edges retype to **`soft_prerequisite`** by default — NOT `hard_prerequisite`. Per `paper_1:L162`, experts systematically overstate necessity; defaulting to the most dangerous value inverts the epistemically correct prior. Upgrades to `hard_prerequisite` only after SQA validation. Companion validator soft-warn: any `hard_prerequisite` with `expert_confidence: low` flags as "provisional — requires validation before use in routing".

**Mechanism**

- 1 product ADR establishing the layered taxonomy and the controlled-vocabulary discipline
- Migration: add `edge_type` enum + `edge_layer` enum + `entry_route_type` enum; retype 516 existing edges to `soft_prerequisite`
- Routing validator: teaching-layer query for "prerequisites of X" must filter to pedagogical_dependence layer only; cross-layer traversal must be explicit
- Soft-warn for any node where 100% of incoming `hard_prerequisite` edges share the same `entry_route_type` (single-lens risk)

**Sub-concerns addressed:** L1.1, L1.2, L1.10 (partial), L1.18 (entry_route_type field)

**Dependencies:** Issue 1 (contestability substrate) lands first so retyped edges carry confidence + provenance from start

**Acceptance criteria**

- [ ] Product ADR drafted (extends ADR 0061)
- [ ] Migration applied; 516 edges retyped to `soft_prerequisite`
- [ ] Routing validator implemented; cross-layer traversal blocked or explicit
- [ ] Single-lens soft-warn fires on test cases

---

## Issue 3 — [Cluster 3] Goal-relative parameterization (learning_outcomes + edge_outcome_necessity junction)

**Labels:** `enhancement`, `tech-debt`
**Title:** `feat(seed-graph): add learning_outcomes table + edge_outcome_necessity junction for goal-relative parameterization`

**Summary**

Add new `learning_outcomes` table + many-to-many `edge_outcome_necessity` junction with `necessity_level` enum (`required`/`recommended`/`historical_contextual_only`), `confidence_for_outcome`, `rationale_for_outcome`. Edges gain `default_necessity_level` for outcome-unspecified queries (defaults to `recommended`, never `required`).

**Why**

The deepest single substrate change in either paper. Per `paper_2:L62`: "the pedagogical dependency path is therefore goal-relative, whereas the influence path is not." The same Kant/Husserl edge is `required` when the goal is "compare Husserl and Kant" and `optional` when the goal is "explain phenomenological description." Edge type alone cannot express this; necessity must be parameterized by `learning_outcome`. Per pedagogy lens-sweep cross-cutting observation 1, this is the master organizing principle across pedagogy + substrate + LLM integration.

**Mechanism**

- 1 product ADR
- 2 new tables: `learning_outcomes`, `edge_outcome_necessity`
- Path-selector contract: `get_path(target_node_id, learning_outcome_id, learner_state)` is the canonical Phase 7+ API signature
- Validator soft-warn: any edge with `default_necessity_level: required` reviewed quarterly against goal-specific overrides
- Per adversarial E.9.1: modifications to a `learning_outcomes` row trigger soft-warns for all linked `edge_outcome_necessity` entries, queuing re-validation

**Sub-concerns addressed:** L1.3, L2.3, L2.13

**Dependencies:** Issue 1 + Issue 2 land first

**Acceptance criteria**

- [ ] Product ADR drafted (this is a major schema-design ADR)
- [ ] Two new tables migrated
- [ ] Path-selector contract documented as Phase 7+ API
- [ ] Re-validation trigger implemented on `learning_outcomes` row updates
- [ ] Initial learning-outcome taxonomy seeded (introductory / analytical / comparative-research at minimum)

---

## Issue 4 — [Cluster 4] Node schema redesign — typology + threshold + audience + granularity + equity metadata + assessment

**Labels:** `enhancement`, `tech-debt`, `priority:urgent` (large)
**Title:** `feat(seed-graph): redesign nodes table — typology + threshold + audience + granularity + equity metadata`

**Summary**

Add ~15 new node columns: `node_type` (enum: threshold_concept / bridge_concept / disciplinary_practice / text_excerpt / historical_context / misconception / comparative_lens / assessment_task), `disciplinary_domain`, `granularity`, `is_threshold_concept`, `audience_tags`, `canonical_sources`, `approved_examples`, `misconceptions` (lightweight), `assessment_items`, `mastery_evidence`, `accessibility_notes`, `assumed_background`, `jargon_load`, `cultural_specificity`, `tradition_label`.

**Why**

Current node schema has no typology, no threshold tagging, no audience/equity metadata, no assessment linkage. The 380 existing nodes are all implicitly the same kind of thing. Paper schema tables (`paper_1:L114–123`, `paper_2:L80`) enumerate these as required fields; the substrate lens-sweep found ~15 distinct node-level claims that collapse to this single redesign.

**Mechanism**

- 1 product ADR
- Migration adds ~15 node columns
- Validator soft-warns:
  - Any node lacking `node_type` after migration: hard-fail until backfilled.
  - Any `threshold_concept` node lacking `assessment_items`: soft-warn.
  - Any node lacking `cultural_specificity` populated: soft-warn (equity metadata gate).
  - Any node lacking `tradition_label` (per adversarial E.7.2): soft-warn at commit time, not just at health-check.

**Sub-concerns addressed:** L1.6, L1.8 (lightweight), L1.9, L1.10, L1.11, L1.12, L1.13, L1.16, L2.1 (partial), L4.13 partial (tradition labels storage)

**Dependencies:** Independent of Issue 1-3 (parallel). Backfill is session-sized work for 380 nodes.

**Acceptance criteria**

- [ ] Product ADR drafted (potentially split into "node typology" + "node equity metadata" if scope warrants)
- [ ] Migration applied; ~15 columns added
- [ ] All 380 existing nodes backfilled with `node_type` (hard-fail gate)
- [ ] Validator soft-warns fire as designed

---

## Issue 5 — [Cluster 5] Misconception sub-graph encoding (full)

**Labels:** `enhancement`, `tech-debt`
**Title:** `feat(seed-graph): encode misconception sub-graph (nodes + remediation edges)`

**Summary**

Two-level misconception encoding: (a) `misconceptions` text field on each target node (lightweight — Cluster 4); (b) standalone misconception nodes with `common_misconception_about` edges → target concept, and `unlearning_required_before` edges from target-concept learning task → misconception node.

**Why**

Per `paper_1:L126`: "encode misconception nodes explicitly... many humanities bottlenecks are caused by misleading prior understandings rather than by absent content." Three named representative misconceptions for the corpus: phenomenology = introspection, deconstruction = anything goes, historical perspective = sympathy with the past. Plus Corrigan's five (text/meaning/context/form/reading) and historiographic presentism. Per substrate lens-sweep cross-cutting observation 4: misconception encoding requires both node-type AND edge-type additions; neither alone is sufficient.

**Mechanism**

- 1 product ADR
- Misconception nodes use `node_type: misconception` (from Cluster 4)
- New edges: `common_misconception_about` (from misconception → target) and `unlearning_required_before` (from target's learning task → misconception) — both in Cluster 2's edge-type taxonomy
- Authoring discipline: every expert-authored target node includes at least one `misconceptions` entry (L4.2 expert-blind-spot mitigation)
- Phase 7+ detect-remediate-retest state machine (deferred to Cluster 11, but substrate must support it now via `active_misconception_ids` in learner_node_state — see Issue 12)

**Sub-concerns addressed:** L1.8, L2.6, L2.7

**Dependencies:** Issue 2 (edge types) AND Issue 4 (node types) must land first

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Misconception nodes seeded with the named representative cases
- [ ] `common_misconception_about` + `unlearning_required_before` edges linked
- [ ] Authoring discipline documented in seed-authoring ops (Issue 6)

---

## Issue 6 — [Cluster 6] Backward-design + Decoding-the-Disciplines authoring discipline + assessment-item authoring (per adversarial E.10.1)

**Labels:** `documentation`, `tech-debt`
**Title:** `docs(operations): PDG authoring discipline — backward design + Decoding the Disciplines + assessment-item authoring`

**Summary**

New ops doc establishing authoring workflow: outcomes → Decoding bottleneck identification → granularity choice → node draft → edge draft → assessment attachment → novice-translation step. Default `expert_confidence: low` for newly authored prerequisite edges. Retroactive audit of existing 380 nodes against the Decoding criteria (per adversarial E.2.3) — at minimum, threshold-tagged nodes must have a `misconceptions` entry within N sessions of tagging. Plus new step covering assessment-item authoring discipline (per adversarial E.10.1).

**Why**

Per `paper_1:L110–112` six-stage construction workflow + `paper_2:L66` outcome-first sequencing. Per `paper_1:L162` and adversarial E.2.2: experts systematically overstate necessity, and SQA auditors (themselves domain experts) cannot reliably predict student-facing difficulty without student-work evidence.

**Mechanism**

New ops doc with seven authoring steps:

1. Define target learning outcomes BEFORE drafting nodes
2. Bottleneck identification via Decoding interview OR prior student-work analysis OR explicit expert rationale with `expert_confidence: low` until validated
3. Granularity at teachable assessable units
4. Novice-translation step (folk-meaning entry per node)
5. Default confidence is `low` for new prerequisite edges
6. **Assessment-item authoring discipline (new — per adversarial E.10.1):** minimum fields per assessment item (learning outcome, task type, rubric pointer, associated node); soft-warn for threshold-concept-attached items lacking a rubric pointer
7. Retroactive audit of existing nodes (per adversarial E.2.3)

**Sub-concerns addressed:** L2.2, L2.3, L4.2, L1.12, L2.12 (assessment-item authoring)

**Dependencies:** None for the doc itself; the retroactive audit step depends on Issue 4 (node typology) landing

**Acceptance criteria**

- [ ] Ops doc authored under `engine/operations/` or `product/operations/`
- [ ] Cross-references added to seed-authoring discipline
- [ ] Retroactive audit checklist enumerated

---

## Issue 7 — [Cluster 7] Graph predictive-validity extension to SQA discipline

**Labels:** `enhancement`, `tech-debt`
**Title:** `feat(operations): extend SQA discipline with graph predictive-validity tracking`

**Summary**

Extend SQA evidence template with 4 new fields per audited edge: `predicted_difficulty_level` (with evidence basis flag per adversarial E.2.2 — `expert_intuition` vs `student_work_evidence`), `inter_rater_agreement`, `disagreement_topic_cluster`, `revision_rate`. Reframe SQA as phase 1 of a longitudinal validity study; phase 2 is Phase 7+ learner-outcome evaluation (Issue 16).

**Why**

Per `paper_2:L204` (four graph-validity metrics named) + evaluation lens-sweep cross-cutting observation 1 ("graph validity evaluation precedes and funds learner-outcome evaluation"). Current SQA (shards 01-08 complete) is implicitly phase 1 but not framed that way. Reframing dramatically increases its downstream value.

**Mechanism**

- 1 product ADR adopting predictive-validity framing
- SQA evidence template updated with 4 new fields
- `predicted_difficulty_level` carries evidence-basis flag (expert_intuition / student_work_evidence) per adversarial E.2.2
- High-disagreement edges automatically queued for Phase 7+ learner-data validation

**Sub-concerns addressed:** L5.2, L5.7 (partial), L5.9

**Dependencies:** Best landed AFTER Issue 1 (so SQA evidence populates the new edge fields directly)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] SQA evidence template updated
- [ ] Methodology documented in operations doc
- [ ] Retroactive update path for shards 01-08 documented (whether to re-score or grandfather)

---

## Issue 8 — [Cluster 8] Graph-topology bias mitigation (augments existing anti-bias mechanism)

**Labels:** `enhancement`, `documentation`, `priority:urgent` (governance)
**Title:** `feat(governance): add graph-topology bias mitigation — augments existing anti-bias mechanism`

**Summary**

Extend the existing Paideia anti-bias mechanism (`feedback_anti_bias_implementation_discipline.md`) to cover the second attack surface the papers identify: graph-topology bias. Existing mechanism covers LLM-input-side bias (strip source-identity at serialization boundary); graph-topology bias is structurally distinct and currently uncovered. Equity metadata (Issue 4 schema fields), tradition labels stored in DB + stripped at LLM serialization boundary (resolves L4.13 CONFLICT), periodic graph-canon census, commit-time validator soft-warn (per adversarial E.7.2).

**Why**

Per adversarial lens-sweep L4.13 synthesis: papers identify 2 new attack surfaces (graph topology + LLM output) that the existing mechanism does not cover. The user's session-opening statement: "we've done nothing whatsoever to shelter the graph from biases of any type." This Issue addresses graph-topology bias; Issue 14 addresses LLM output bias.

**Mechanism**

- Extension to existing memory drawer `feedback_anti_bias_implementation_discipline.md`: name two surfaces, partition coverage
- 1 product ADR: graph-topology bias policy
- New ops doc: graph-canon census discipline (cadence: health-check audits per ADR 0057)
- Commit-time validator soft-warn (per adversarial E.7.2): any new `hard_prerequisite` edge whose source node carries `tradition_label` in {Western_analytic, Continental} without corresponding `alternative_route_available: true` flags at commit time

**Sub-concerns addressed:** L4.1, L4.2 (partial), L4.5 (partial), L4.12, L4.13 (graph-topology half)

**Dependencies:** Issue 4 (tradition_label field) lands first

**Acceptance criteria**

- [ ] Memory drawer updated with two-surface partition
- [ ] Product ADR drafted
- [ ] Graph-canon census ops doc authored
- [ ] Commit-time validator soft-warn implemented and tested

---

## Issue 9 — [Cluster 9] Instructional-spine architecture (foundational Phase 7+ ADR)

**Labels:** `enhancement`, `documentation`, `architecture`
**Title:** `feat(architecture): commit to instructional-spine architecture for teaching-layer (PDG=spine, LLM=adaptive interface)`

**Summary**

Foundational product ADR establishing teaching-layer architectural invariants: PDG = instructional spine, LLM = adaptive interface, humans arbitrate. Five-service architecture (graph store / content store / LLM orchestration / analytics / review layer). No-silent-mutation rule across all five services. Pre-registered edit policies. LLM as triage/critic/coach — never judge. Plus tool-stack evaluation forcing function (per adversarial E.10.3): Postgres+JSONB+CTEs vs Neo4j dual-layer evaluation must occur BEFORE Tier A migrations are applied to production, not after.

**Why**

Per `paper_2:L6–7` + `paper_2:L140` + `paper_2:L198`. Per LLM lens-sweep cross-cutting observation 2: instructional spine IS the structural mitigation for hallucinated-structure risk (per `paper_2:L186`, 32% pre-mitigation failure rate). Per cross-cutting observation 1: no-silent-mutation applies to all five services; the build-apparatus discipline (routine-mode scope-lock per ADR 0051) is the existence proof Paideia can implement this.

**Mechanism**

- 1 large product ADR establishing all invariants enumerated above
- Tool-stack evaluation report authored before Tier A migrations begin (per adversarial E.10.3): if Neo4j dual-layer wins, the Tier A migrations target Neo4j not Postgres; if Postgres+JSONB+CTEs is sufficient at scale, proceed with Postgres
- Cross-references to existing build-apparatus no-silent-mutation machinery as architectural precedent

**Sub-concerns addressed:** L3.1, L3.2, L3.7, L3.9, L3.10, L3.11, L3.12, L3.15

**Dependencies:** Tier A substrate (Issues 1-5) for the ADR to be meaningful; but tool-stack evaluation must occur BEFORE Issue 1 migration applies

**Acceptance criteria**

- [ ] Tool-stack evaluation report authored and decision documented
- [ ] Product ADR drafted with all invariants enumerated
- [ ] Cross-references to existing build-apparatus precedent included
- [ ] Five-service architecture mapped to anticipated Phase 7+ service boundaries

---

## Issue 10 — [Cluster 10] Prompt template discipline + content store

**Labels:** `enhancement`, `documentation`
**Title:** `feat(ops): prompt template discipline + content-store schema for teaching-layer LLM integration`

**Summary**

New ops doc + content store schema: prompt templates as versioned repo artifacts; adopt two paper-provided templates as starting artifacts (graph-refinement prompt + student-facing explainer); self-consistency requirement for graph-refinement outputs (N=3, ≥2 of 3 — but caveat per adversarial E.1.3 as starting heuristic requiring empirical calibration); co-versioning with graph; self-grounded discipline per existing anti-bias mechanism.

**Why**

Per LLM lens-sweep cross-cutting observation 3: "prompt templates are architectural artifacts, not documentation." The two paper-provided templates (`paper_2:L144-167` graph-refinement + `paper_2:L169-182` student explainer) encode service-call ordering, input contracts, and interface shape.

**Mechanism**

- 1 ops doc `engine/operations/prompt-template-discipline.md`
- Prompt templates in `product/prompts/` directory with versioning
- Self-consistency caveat per adversarial E.1.3: N=3 is starting heuristic; does NOT replace Cluster 1 contestability substrate; agreement on a false prerequisite across N samples is a known failure mode

**Sub-concerns addressed:** L3.5, L3.6, L3.8, L3.13

**Dependencies:** Issue 9 (instructional-spine ADR) lands first

**Acceptance criteria**

- [ ] Ops doc authored
- [ ] Two paper-provided templates adopted as starting artifacts
- [ ] Self-consistency caveat documented per adversarial E.1.3
- [ ] Co-versioning policy with graph version table documented

---

## Issue 11 — [Cluster 11] Four sample workflows + role-checkpoint partitioning + path attribution

**Labels:** `enhancement`, `architecture`
**Title:** `feat(architecture): adopt four LLM+PDG sample workflows as Paideia teaching patterns + path attribution invariant`

**Summary**

1 product ADR adopting four workflows: instructor-authored + LLM scaffolding (lowest-risk Phase 7+ entry point); student-authored + LLM critique (framed as suggestive not authoritative); adaptive branching (conservative + coarse-grained for humanities); trace-informed revision (highest governance burden). Role-checkpoint partition per workflow. Student-friendly subset exposure as access-control invariant. Plus path attribution invariant (per adversarial E.7.1): every routing decision across all four workflows surfaces attribution to the student. Plus no-silent-mutation gate for the instructor-authored workflow (per adversarial E.1.2).

**Why**

Per `paper_2:L90-95` workflow table + `paper_2:L200` student-friendly subset rule. Per adversarial E.7.1: path attribution must be carried through every cluster that routes students, not just C15.

**Mechanism**

- 1 product ADR
- Four workflows documented with explicit instructor/LLM/student/reviewer roles and checkpoints
- Conservative-and-coarse-grained gate for adaptive branching (per `paper_2:L72`)
- Path attribution invariant: every routing decision carries `instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved` per Cluster 15
- No-silent-mutation gate for instructor-authored workflow per adversarial E.1.2

**Sub-concerns addressed:** L3.3, L3.4, L3.14

**Dependencies:** Issue 9 (instructional-spine) + Issue 15 (path attribution from privacy/governance cluster)

**Acceptance criteria**

- [ ] Product ADR drafted with four workflows
- [ ] Phase 7+ rollout order specified
- [ ] Path attribution invariant cross-referenced in each workflow
- [ ] Student-friendly subset enforced at access-control layer (not just UI)

---

## Issue 12 — [Cluster 12] Scaffolding fade trajectory + learner-state schema (pseudonymous, consent-versioned)

**Labels:** `enhancement`, `architecture`
**Title:** `feat(architecture): learner-state schema with pseudonymous session token + three-state scaffold fade`

**Summary**

Separate `learner_node_state` table with pseudonymous `learner_session_token` FK (NOT `learner_id` — per adversarial E.6.1; identifier mapping lives in a separate Cluster-15-governed table). Fields: `mastery_probability`, `evidence_count`, `recent_errors`, `visit_count`, `last_interaction`, `help_seeking_pattern`, `language_preference`, `consent_version` (per adversarial E.11.2), `active_misconception_ids` (per adversarial E.9.2), `mastery_estimate_calibration_flag` (per adversarial E.4.2). Three-state scaffold approximation with state transitions logged in override-events table per adversarial E.5.1 + E.7.1.

**Why**

Per `paper_2:L84` learner-state schema + pedagogy lens-sweep cross-cutting observation 3 (lightweight 3-state approximation viable now). Multiple adversarial fixes incorporated to prevent FERPA failure (E.6.1), consent-version blind spot (E.11.2), missing misconception state (E.9.2), uncalibrated multilingual mastery estimates (E.4.2), and silent scaffold-fade routing (E.5.1 + E.7.1).

**Mechanism**

- 1 product ADR
- Migration: `learner_node_state` table + separate `learner_identifier_mapping` table governed by Cluster 15 RLS
- Three-state scaffold rule: state 0 (full scaffold) → state 1 (`mastery_probability ≥ 0.4` AND calibration validated for learner's language subgroup) → state 2 (`mastery_probability ≥ 0.7`)
- All state transitions logged in override-events table with attribution `model_inferred_approved` (Cluster 15)

**Sub-concerns addressed:** L1.15, L1.17, L2.4, L2.5

**Dependencies:** Issue 4 (`mastery_evidence` field on nodes) + Issue 15 (privacy/FERPA framework + override-events table) — Issue 15 must land first to provide the identifier mapping table.

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Migration applied with pseudonymous session token + identifier mapping separation
- [ ] Three-state scaffold logic implemented with override logging
- [ ] Calibration gate enforced for multilingual cohorts

---

## Issue 13 — [Cluster 13 path-selector logic] Alternative-entry-route path-selector + pluralism reserve

**Labels:** `enhancement`, `architecture`
**Title:** `feat(architecture): alternative-entry-route path-selector + pluralism reserve (Phase 7+ teaching logic)`

**Summary**

Phase 7+ teaching-app logic consuming the `entry_route_type` schema field (already added in Issue 2 per adversarial E.3.2). Path-selector rule: surface at least two distinct routes when available; no canonical-path enforcement. Recursive-revisiting support via `visit_count` differentiation. Path-agnostic argument scoring (anti-pathologizing). Path attribution per Cluster 15 (per adversarial E.7.1).

**Why**

Per `paper_1:L126` + `paper_2:L188` (alternative pathways as equity mechanism) + Spiro cognitive flexibility (`paper_1:L45`). The schema field lands in Tier A (Issue 2); the path-selector logic is Phase 7+.

**Mechanism**

- 1 product ADR for path-selector contract
- Phase 7+ teaching-app implementation
- Path attribution invariant: routes labeled `instructor_designed` or `model_inferred_approved` per Cluster 15

**Sub-concerns addressed:** L1.18 (logic-side), L2.8, L2.9, L4.12, L4.5 (partial — path-agnostic argument scoring)

**Dependencies:** Issue 2 (`entry_route_type` field) + Issue 8 (tradition labels) + Issue 11 (workflows) + Issue 15 (path attribution)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Path-selector contract documented
- [ ] Path-agnostic argument scoring rubric discipline documented

---

## Issue 14 — [Cluster 14] LLM-mediated bias mitigation (output side; parallel to existing input-strip mechanism)

**Labels:** `enhancement`, `documentation`, `priority:urgent` (governance)
**Title:** `feat(governance): LLM output-side bias mitigation (multilingual sampling, rubric review, scoring calibration)`

**Summary**

Parallel mechanism to the existing input-strip anti-bias discipline. Output-side audit: multilingual output sampling, rubric review for pathologizing risk, scoring calibration against instructor rubrics (correlation, variance ratio, overscoring bias, subgroup performance), pre-registered scoring prompt versioning, "critic or coach, not final judge" framing in UI copy, override threshold for repeated misconception routing. Plus subgroup-differential routing detection (per adversarial E.4.1).

**Why**

Per adversarial lens-sweep L4.13 synthesis: existing anti-bias mechanism is input-boundary-only. Two distinct bias surfaces require two distinct mechanisms. LLM scoring known weaknesses (`paper_2:L190`: smoothing extremes, overscoring, criteria shift) are worst precisely where humanities assessment is most important (nuanced argument, interpretive range).

**Mechanism**

- 1 product ADR (governance)
- 1 ops doc for LLM output audit
- Skill extension (`claude-api` discipline)
- Subgroup-differential routing detection in Cluster 17 (Issue 17)
- Pre-condition for Issue 16 evaluation: LLM scoring must be calibrated against instructor rubrics BEFORE the three-arm comparison study begins (per adversarial E.5.2)

**Sub-concerns addressed:** L4.3, L4.5 (LLM-output side), L4.11, L4.4 (LLM-output subgroup analysis)

**Dependencies:** Issue 9 (instructional spine — staging area architecture) + Issue 16 (calibration sample source)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Ops doc authored
- [ ] Calibration protocol documented as Phase 7+ pre-deployment gate

---

## Issue 15 — [Cluster 15] Privacy / FERPA / NIST alignment + override logging + transparency reports + path attribution

**Labels:** `enhancement`, `documentation`, `priority:urgent` (governance, foundational for Phase 7+)
**Title:** `feat(governance): Phase 7+ privacy/FERPA/NIST alignment + override logging + transparency reports + path attribution`

**Summary**

Phase 7+ governance ADR + ops doc establishing: RLS-level separation of identifiers from analytics (per `paper_2:L192`); consent management (consent_version + retention_expiry + withdrawal workflow); override events table; transparency report template; NIST four-control mapping; named cadence + named responsible actor per check; student-facing path attribution. Plus derived-data consent audit (per adversarial E.6.2).

**Why**

Per `paper_2:L192` (FERPA/NIST guidance — three concrete schema requirements) + adversarial cross-cutting observation 3: "governance machinery is inert without named human review cadence."

**Mechanism**

- 1 product ADR
- 1 ops doc `engine/operations/nist-genai-alignment.md` (or `product/operations/`)
- RLS policies + `learner_identifier_mapping` table (provides pseudonymous mapping for Issue 12)
- Override events table + transparency report template
- Named cadence: weekly low-confidence edge review (instructor) + quarterly equity audit (course coordinator) + annual graph-validity review (discipline committee) + at-every-commit-merge scoring calibration check (if prompts changed)
- Derived-data audit on consent withdrawal: identify candidate edges whose provenance cites the withdrawing learner's trace events; flag for instructor review; re-derive or downgrade confidence (per adversarial E.6.2)

**Sub-concerns addressed:** L4.6, L4.7, L4.8, L4.10

**Dependencies:** None — foundational for Phase 7+; must land before Issue 12 (learner-state) and Issue 14 (LLM-output bias)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Ops doc authored with named cadence + named actor per check
- [ ] Override events table schema documented
- [ ] Transparency report template documented
- [ ] Derived-data audit workflow documented

---

## Issue 16 — [Cluster 16] Learner-outcome evaluation infrastructure (Phase 7+)

**Labels:** `enhancement`, `documentation`, `architecture`
**Title:** `feat(evaluation): Phase 7+ learner-outcome evaluation infrastructure (3-arm comparison + HTE + DBR)`

**Summary**

Phase 7+ evaluation ADR + ops doc establishing: 5-metric outcome bundle + 3-arm cluster-randomized or cross-over design (PDG-only / LLM-only / PDG+LLM) + HTE subgroup analysis with pre-registered primary contrasts + minimum cell sizes + actionable thresholds (per adversarial E.10.2) + process-quality measurement via discourse coding (Lucero et al. method) + node-linked student survey instrument (per adversarial E.8.2: include path-attribution validation item) + design-based research as overarching methodology.

**Why**

Per `paper_1:L144-150` + `paper_2:L204` + evaluation lens-sweep cross-cutting observations. Per adversarial E.10.2: subgroup analysis is present in name only without minimum cell sizes and escalation thresholds. Per adversarial E.5.2: LLM scoring must be calibrated BEFORE the comparison study begins.

**Mechanism**

- 1 product ADR
- 1 ops doc
- HTE pre-registration: minimum N ≥ 30 per subgroup, effect-size or routing-rate thresholds for actionable findings, named escalation path
- IRB-side preparation
- Pre-condition: Issue 14 calibration protocol completed before study begins

**Sub-concerns addressed:** L5.1, L5.3, L5.4, L5.5, L5.6, L5.10

**Dependencies:** Issue 9 (architecture) + Issue 14 (calibration) + Issue 15 (privacy framework)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Ops doc authored
- [ ] HTE pre-registration framework documented
- [ ] IRB-side preparation tasks enumerated

---

## Issue 17 — [Cluster 17] Anomalous routing detection + three-way disambiguation (Phase 7+)

**Labels:** `enhancement`, `architecture`
**Title:** `feat(architecture): Phase 7+ anomalous routing detection module with three-way disambiguation + subgroup-differential routing detection`

**Summary**

Phase 7+ analytics-layer module detecting three anomaly types with distinct interventions: bypass-and-succeed (false prerequisite) / satisfy-and-fail (missing prereq or over-strong edge or bad assessment item — three-way disambiguation requires instructor review) / cycle-without-progress. Plus subgroup-differential routing detection (per adversarial E.4.1): if learners in a named subgroup are routed to prerequisite remediation at rates >N% higher than baseline, flag for instructor review. Plus latching review gate (per adversarial E.1.1): items stay in `pending_instructor_review` state, never auto-promoted; named reviewer + staleness policy.

**Why**

Per `paper_2:L74` three-way diagnostic signals + `paper_2:L72` conservative branching for humanities. Per adversarial E.1.1: the original C17 spec did not name the specific reviewer, latching state, or staleness policy — without these, the no-silent-mutation guarantee is a naming convention. Per adversarial E.4.1: subgroup-differential routing is a third equity surface not covered by C8 or C14. Per adversarial E.11.3: detection depends on populated necessity classifications in the junction table (Issue 3).

**Mechanism**

- 1 product ADR
- Analytics-layer module + ops doc
- Latching review gate with named reviewer + staleness escalation policy
- Subgroup-differential routing detection with N% threshold (configurable; documented baseline)
- Three-way disambiguation discipline: satisfy-and-fail events not auto-classified; require instructor disambiguation

**Sub-concerns addressed:** L5.8, L3.13 (detection trigger), L5.2 (operational signal)

**Dependencies:** Issue 9 (analytics-layer service) + Issue 12 (learner state) + Issue 1 (per-edge confidence) + Issue 3 (necessity classifications)

**Acceptance criteria**

- [ ] Product ADR drafted
- [ ] Analytics-layer module designed
- [ ] Latching review gate specification documented
- [ ] Subgroup-differential threshold rationale documented

---

## Summary

**17 Issues across 5 tiers.** Land order (with dependencies):

- **Tier A foundational (urgent, in this order):** Issue 1 → Issue 4 (parallel with 1) → Issue 2 (depends on 1) → Issue 5 (depends on 2+4) → Issue 3 (depends on 1+2; deepest)
- **Tier B actionable now (parallel):** Issue 6 (authoring discipline) + Issue 7 (SQA extension)
- **Tier C governance extension (urgent for graph work):** Issue 8 (depends on Issue 4)
- **Tier D Phase 7+ teaching architecture:** Issue 9 (foundational) → Issues 10, 11, 12, 13 (parallel after 9)
- **Tier E Phase 7+ deployment governance:** Issue 15 first (provides infrastructure for 12, 14, 17) → Issues 14, 16, 17 in parallel

**Adversarial fixes incorporated:** 22 adversarial findings; 3 critical applied to synthesis.md inline (E.2.1+E.11.1, E.6.1, E.7.1); 19 additional fixes carried into Issue bodies above (E.1.1, E.1.2, E.1.3, E.2.2, E.2.3, E.3.1, E.3.2, E.4.1, E.4.2, E.5.1, E.5.2, E.6.2, E.7.2, E.8.1, E.8.2, E.9.1, E.9.2, E.10.1, E.10.2, E.10.3, E.11.2, E.11.3, E.12.1, E.12.2).
