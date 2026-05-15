# Adversarial review

> Phase E output. Reviews `synthesis.md` against the seven paper-named risks plus open-ended fidelity, consistency, and orphan checks. All paper citations use the paragraph-line convention used in the synthesis (`paper_1:L<n>` = line in Paper 1, `paper_2:L<n>` = line in Paper 2). Cluster IDs follow synthesis numbering (C1–C17).

---

## E.1 — Hallucinated structure

### Finding E.1.1 — C17 (anomalous routing detection) has no gate preventing silent staging-area population

**Paper anchor:** `paper_2:L186` ("the most dangerous failure is often a false prerequisite or an omitted prerequisite, because it silently changes the learning path"); `paper_2:L194` (no silent graph mutation; every proposed edit should be attributable, reviewable, and reversible).

**Cluster affected:** C17 (anomalous routing detection).

**Issue:** C17 specifies that the analytics layer emits "candidate edges or candidate misconception nodes, NOT silent graph mutations." But the cluster does not name who reads the instructor dashboard queue, at what cadence, or what happens to unread queue entries. If the queue silently accumulates and a downstream system reads it without instructor action, the no-silent-mutation guarantee is a naming convention, not a structural guarantee. The synthesis cross-cluster note says C9 is parent and enforces the rule, but C9's no-silent-mutation rule covers the graph store, not the analytics output buffer itself. A false-prerequisite candidate sitting in the queue labeled `bypass-and-succeed` could be acted on by a scripted workflow without instructor sign-off if the queue drain is automated. This is exactly the `paper_2:L186` risk: a false prerequisite enters not via direct write but via a staging buffer that lacks a latching review gate.

**Recommended change:** C17 must name the specific reviewer role, the latching state (item stays in `pending_instructor_review` and is never auto-promoted), the staleness policy (items older than N days escalate, not auto-apply), and an explicit cross-reference back to C9's "store suggestion as unresolved" invariant. The current text says "Outputs candidate edges … NOT silent graph mutations" but that phrasing only prohibits direct writes, not indirect promotion.

---

### Finding E.1.2 — C11 (instructor-authored + LLM scaffolding workflow) does not close the LLM-proposed-prerequisite gap for the lowest-risk workflow

**Paper anchor:** `paper_2:L186` (32% initial quality-check failure rate in bounded math context; hallucinated structure risk is highest in humanities); `paper_2:L90–95` (workflow table, instructor-authored workflow human checkpoints: "approve graph; review low-confidence outputs; spot-check scoring").

**Cluster affected:** C11 (four sample workflows + role-checkpoint partitioning).

**Issue:** The synthesis describes the instructor-authored + LLM scaffolding workflow as the "lowest-risk Phase 7+ entry point." But the paper's 32% failure rate applies to math — the rate in humanities is expected to be higher because canonical importance is more easily mistaken for pedagogical necessity (`paper_2:L186`). C11 lists "approve graph" as a human checkpoint but does not specify that LLM-proposed edges during the scaffolding phase (e.g., "here is a candidate bridge concept the LLM thinks you need") must go through the same no-silent-mutation gate as the trace-informed workflow (workflow 4). A reader implementing C11 could infer that instructor approval is required once at graph launch and the LLM can propose supplementary edges conversationally thereafter. The paper is unambiguous that every proposed edge needs confidence, provenance, contrary evidence, and an approval workflow (`paper_2:L74`).

**Recommended change:** C11 must add an explicit note that the "lowest-risk" label applies only if the LLM is constrained to the content-store layer (generating explanations from approved nodes), never to the graph-structure layer. If LLM proposes a new edge or misconception node within a scaffolding workflow, that proposal routes to C9's review-layer queue regardless of workflow type. The current text says "framed as suggestive not authoritative" for student-authored workflow (workflow 2) but is silent on this for workflow 1.

---

### Finding E.1.3 — C10 self-consistency requirement is under-specified and the N=3 threshold is asserted without grounding

**Paper anchor:** `paper_2:L50` (Pardos and Bhandari: 32% initial failure; self-consistency was used to reduce error rates — but the paper does not specify N=3 as sufficient).

**Cluster affected:** C10 (prompt template discipline + content store).

**Issue:** The synthesis states "sample N=3 outputs; only surface a candidate edge to the review layer if ≥2 of 3 agree." N=3 with ≥2/3 majority is a reasonable heuristic, but the paper reports only that self-consistency was applied — it does not validate N=3 as sufficient for humanities edge proposals. The synthesis treats this as a mechanical gate without flagging that the appropriate N is an open empirical question. Worse, self-consistency of LLM outputs measures internal coherence, not factual correctness — a model can self-consistently propose a false prerequisite. The paper's actual mitigation emphasis is on the provenance+counterexample+confidence governance layer (C1), not on sampling the LLM multiple times. C10's self-consistency rule as written could create false confidence that ≥2/3 agreement filters out hallucinated structure.

**Recommended change:** C10 should (a) caveat the N=3 threshold as a starting heuristic requiring empirical calibration against humanities edge-proposal quality, (b) explicitly state that self-consistency is a first-pass filter only and does not replace C1's provenance+confidence+counterexample governance, and (c) flag that agreement on a false prerequisite across N samples is a well-known failure mode of self-consistency.

---

## E.2 — False prerequisites via expert blind spot

### Finding E.2.1 — The synthesis defaults the 516 existing `pedagogical_prerequisite` edges to `hard_prerequisite` without a validation gate before use

**Paper anchor:** `paper_1:L162` ("encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict"); `paper_2:L74` (three-way diagnostic signal types — a `bypass-and-succeed` event falsifies a hard-prerequisite claim).

**Cluster affected:** C2 (edge-type taxonomy expansion), C7 (graph predictive-validity extension to SQA discipline).

**Issue:** C2 specifies that the 516 existing edges "retype to `hard_prerequisite` by default within the new layer system." The SQA evidence is cited as informing which should be downgraded "in a follow-up migration." This is the expert-blind-spot failure mode named directly in Paper 1: the authors explicitly warn that experts systematically overstate necessity (`paper_1:L162`). The current SQA C1 fresh-defect rate is 3.7% (from commit context). Extrapolated to 516 edges, that is roughly 19 freshly defective edges that the migration would stamp `hard_prerequisite`. But the SQA defect rate captures authoring defects, not pedagogical over-confidence — the actual proportion of over-strong edges could be substantially higher. Paper 1 is explicit that the expert default is overconfidence, so defaulting to `hard_prerequisite` is defaulting to the most dangerous value.

**Recommended change:** C2 should default the mass retyping to `soft_prerequisite` rather than `hard_prerequisite`, with the justification explicit: `paper_1:L162` identifies expert-built PDGs as systematically over-confident, so the correct prior for an un-validated edge is `soft`, not `hard`. Edges should be upgraded to `hard_prerequisite` only after SQA validation, not downgraded from it. The current text inverts the epistemically correct direction.

---

### Finding E.2.2 — C7 does not require that SQA auditors predict difficulty level from a student perspective; they are domain experts with the exact blind spot being mitigated

**Paper anchor:** `paper_1:L162` (expert blind spot: experts forget disciplinary meanings are not obvious); `paper_2:L202` (instructor workflow: identify bottlenecks through student work, diagnostic discussion, or Decoding interview — not through expert re-review alone).

**Cluster affected:** C7 (graph predictive-validity extension to SQA discipline).

**Issue:** C7 extends the SQA template with `predicted_difficulty_level` and `inter_rater_agreement`. Both fields are populated by auditors — who are, by the nature of the SQA process, domain-expert reviewers. The expert-blind-spot risk is that experts cannot reliably predict which edges students will trip over. A `predicted_difficulty_level` produced by domain experts without reference to student work evidence is still an expert estimate, not a validated learner-difficulty signal. The synthesis acknowledges "SQA census is implicitly phase 1 of a longitudinal validity study" but does not note that auditor predictions without student-work calibration re-instantiate the same expert-blind-spot problem at the SQA tier.

**Recommended change:** C7 should require that `predicted_difficulty_level` include a notation of the evidence basis: `expert_intuition` (default, flagged as unvalidated) vs `student_work_evidence` (requires citing the evidence). The field should carry a soft-warn flag that any edge with `expert_intuition` basis for `difficulty_level: high` is treated as `low-confidence` per C1 until learner-trace data upgrades it. This is the `paper_1:L162` mitigation applied to the SQA process itself.

---

### Finding E.2.3 — C6 specifies the Decoding-the-Disciplines bottleneck step but does not require it for existing nodes — only for newly authored nodes

**Paper anchor:** `paper_1:L162` (mitigation: "encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict"); `paper_1:L110–112` (six-stage construction workflow applies to the graph's construction, not only future additions).

**Cluster affected:** C6 (backward-design + Decoding-the-Disciplines authoring discipline).

**Issue:** C6's integrated mechanism specifies the Decoding-interview bottleneck step as part of the authoring workflow for new nodes. But the 380 existing Paideia nodes were not authored through this process. C6 says "extends current seed-authoring discipline" but does not require a retroactive audit of existing nodes against the Decoding criteria. The expert-blind-spot risk (nodes encoding tacit expert assumptions not visible to students) is highest in the existing corpus, not in future authoring, because future authoring will be governed by the new discipline. The synthesis does not close this gap.

**Recommended change:** C6 should add a retroactive audit step: the Decoding-the-Disciplines bottleneck criterion applies to existing `threshold_concept` nodes (once C4 tagging lands) as a Tier B deliverable, not only to future authoring. At minimum, nodes tagged `threshold_concept` and `is_threshold_concept: true` after C4 migration should be required to have a `misconceptions` entry within N sessions of tagging — enforced by the C4 validator soft-warn. Without this, the expert-blind-spot mitigation is prospective only.

---

## E.3 — Cultural / canon bias

### Finding E.3.1 — The L4.13 CONFLICT resolution ("store tradition_label in DB; strip at LLM boundary") creates a new failure mode the synthesis does not address: the graph topology itself encodes the bias before LLM interaction

**Paper anchor:** `paper_2:L188` ("store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase"); `paper_1:L160` (the graph can reproduce disciplinary gatekeeping by silently privileging European conceptual histories).

**Cluster affected:** C8 (graph-topology bias mitigation), C4 (node schema redesign).

**Issue:** The synthesis resolves the CONFLICT between named tradition labels and the existing strip-identity-at-boundary mechanism by stripping `tradition_label` before LLM context injection. This correctly prevents the LLM from being biased by tradition identity cues. But the paper's canon-bias warning (`paper_1:L160`, `paper_2:L188`) is about the graph topology itself — which nodes are marked `required` vs `optional`, which traditions appear only as required prerequisites and never as entry routes. Stripping `tradition_label` at the LLM boundary does not address this: the bias is in the edge structure, not in the label field. A graph where European analytic tradition nodes are uniformly `hard_prerequisite` and postcolonial tradition nodes are uniformly `helpful_bridge` encodes canon bias regardless of whether the LLM sees the labels. The LLM boundary strip is a correct mechanism for a different problem (LLM prior-belief contamination). It does not substitute for the graph-topology audit C8 proposes.

**Issue extension:** C8 proposes the graph-canon census at health-check cadence, which is correct. But the health-check is periodic (ADR 0057 cadence is non-trivial). The synthesis does not name what prevents canon bias from being introduced between censuses — i.e., there is no authoring-time gate analogous to C6's Decoding bottleneck requirement. New edges introducing `hard_prerequisite` for a node from one tradition without a corresponding alternative-route entry could land and persist until the next health-check.

**Recommended change:** C8 should add an authoring-time validator soft-warn: any new `hard_prerequisite` edge whose source node carries `tradition_label` in {Western_analytic, Continental} (or whichever labels represent canonical lineages for a given domain) without a corresponding `alternative_route_available: true` or an explicit justification field is flagged at commit time. This closes the between-census gap. The strip-at-boundary mechanism is correct but insufficient; the synthesis should state this limitation explicitly.

---

### Finding E.3.2 — C13 (alternative-entry-route support) is Tier D (Phase 7+) but the canon-bias it mitigates is an authoring-time substrate problem

**Paper anchor:** `paper_2:L188` (mitigation: store alternative pathways at graph authoring time, not at teaching-layer deployment time); `paper_1:L126` (three implementation principles include preserving multiple routes — this is a graph-construction discipline, not a Phase 7+ teaching-app feature).

**Cluster affected:** C13 (alternative-entry-route support + pluralism reserve), C8 (graph-topology bias mitigation).

**Issue:** The synthesis places C13 in Tier D (Phase 7+ teaching architecture). But the papers frame multiple-entry-route encoding as a graph-construction discipline (`paper_1:L126`: "preserve multiple routes into complex topics … allow case-based, conceptual, methodological, and historical entry points"). The `entry_route_type` attribute is a schema field on edges — it belongs in Tier A substrate, not Tier D teaching architecture. If it is deferred to Phase 7+, the 380+ nodes and 533+ edges will be authored, migrated, and potentially backfilled (including SEP backfill per Phase 6 plans) without any `entry_route_type` encoding. The canon-bias audit (C8's health-check census) would then flag single-lens nodes with no alternative routes, but there would be no substrate support to populate the alternative routes until Phase 7+. This creates a multi-phase gap between identifying the problem (C8, Tier C) and having the substrate to fix it (C13, Tier D).

**Recommended change:** The `entry_route_type` schema field should be extracted from C13 and promoted to Tier A (or Tier B at minimum) as a substrate field on the edges table, even if the path-selector teaching logic remains Tier D. This matches the paper's framing: encoding alternative routes is authoring discipline, not teaching-app architecture.

---

## E.4 — Multilingual / equity gaps

### Finding E.4.1 — The gap between graph-level equity (C8) and LLM-output equity (C14) is real and the synthesis does not bridge it: subgroup-differential routing is not caught by either cluster

**Paper anchor:** `paper_2:L206` ("Do multilingual students receive poorer feedback or less accurate scoring? Does the system over-pathologize certain interpretive styles as misconceptions? Are some traditions overrepresented as 'required prerequisites' rather than 'one valid route'?"); `paper_2:L188` (multilingual evaluation shows performance varies by language).

**Cluster affected:** C8 (graph-topology bias), C14 (LLM-mediated bias — output side), C16 (evaluation infrastructure with HTE analysis).

**Issue:** C8 addresses canon bias in the graph topology. C14 addresses LLM output-side bias (multilingual sampling, rubric review, calibration). But the paper's `paper_2:L206` equity surface includes a third category: subgroup-differential routing — a student from a particular language background or interpretive tradition being systematically routed to harder prerequisite paths because the graph topology or the LLM's mastery-probability estimate is less accurate for that subgroup. This is not graph topology (C8's domain) and not LLM output quality (C14's domain) — it is the interaction between learner-state estimation errors and routing decisions. The synthesis does not name any cluster that closes this.

C16's HTE analysis would detect it retrospectively, but only after deployment. There is no prospective gate that monitors routing patterns by subgroup before a pattern becomes systematic harm.

**Recommended change:** C17 (anomalous routing detection) or C14 should add a subgroup-differential routing detection rule: if learners in a named subgroup (language background, major/non-major) are routed to prerequisite remediation at rates >N% higher than the baseline population for the same target node, flag for instructor review. This is a detection rule on the analytics layer (C17's domain) rather than a retrospective HTE analysis (C16's domain). Without this, the equity audit is entirely post-hoc.

---

### Finding E.4.2 — C12 learner-state schema includes `language_preference` but no field for the confidence calibration of mastery estimates across language groups

**Paper anchor:** `paper_2:L188` (multilingual evaluation shows educational-task performance varies by language, often disadvantaging lower-resource languages); `paper_2:L84` (learner state schema in the paper includes `language_preference` — but the paper frames this as relevant to how the LLM adapts, not only what language to use).

**Cluster affected:** C12 (scaffolding fade trajectory + learner-state schema).

**Issue:** The synthesis correctly includes `language_preference` in the `learner_node_state` table. But the paper's multilingual equity concern is not only about which language to use — it is about whether mastery estimates are equally calibrated across language groups. A `mastery_probability` of 0.7 for a student working in a lower-resource language may be systematically underestimated if the diagnostic rubrics were calibrated on a dominant-language cohort. The learner-state schema as specified in C12 has no field for `mastery_estimate_language_context` or any indicator of whether the mastery estimate is calibrated for that student's language background. The three-state scaffold approximation in C12 uses `mastery_probability` thresholds (0.4 and 0.7) that could systematically route multilingual students to longer remediation paths.

**Recommended change:** C12 should add a note that mastery-probability thresholds in the fade trajectory must be validated per language subgroup before being used for routing decisions, and the `learner_node_state` table should include a `mastery_estimate_calibration_flag` that marks whether the estimate has been calibrated against a language-matched cohort. This is not a Phase 7+ luxury — it is a prerequisite for using `mastery_probability` for routing decisions fairly.

---

## E.5 — Assessment distortion

### Finding E.5.1 — C9 names "LLM as triage / critic / coach — never judge" but C12 uses `mastery_probability` thresholds for routing with no human-in-the-loop gate

**Paper anchor:** `paper_2:L190` ("reserve consequential grading for human judgment or moderated hybrid workflows; validate AI scoring against instructor rubrics and subgroup performance; present the AI as a critic or coach, not as the final judge"); `paper_2:L54` (prompt composition and order changed feedback quality and scoring behavior).

**Cluster affected:** C12 (scaffolding fade trajectory + learner-state schema), C9 (instructional-spine architecture).

**Issue:** C9 commits as a load-bearing invariant: "LLM as triage / critic / coach — never judge. Consequential grading is human-reviewed." C12's three-state scaffold approximation uses `mastery_probability ≥ 0.4` and `mastery_probability ≥ 0.7` as thresholds to reduce or eliminate scaffold support. Reducing scaffold support is a consequential routing decision — a student whose mastery is miscounted at 0.71 loses support they need. C12 frames this as "implementable without full knowledge-tracing," but the paper is explicit that routing based on mastery estimates has a human-checkpoint requirement (`paper_2:L94`, "Review anomalous paths and override routing decisions"). The synthesis does not name any human review gate for mastery-probability-driven scaffold fade; the fade is described as automatic via "edge fade trajectory as derived attribute, not stored, computed at query time."

**Recommended change:** C12 must add that any mastery-probability-driven routing decision that changes scaffold level (state transition 0→1 or 1→2) is logged in the override events table (C15) and surfaced to the instructor dashboard (C17). A threshold that automatically strips scaffold support with no human-visible record directly contradicts C9's load-bearing invariant. The fade may be computed automatically, but it must be auditable and reversible per C15's override framework.

---

### Finding E.5.2 — C16 assumes LLM scoring is used in the three-arm comparison study without naming the calibration requirement as a precondition for deployment

**Paper anchor:** `paper_2:L190` (LLM grading studies: 70% of gradings fall within 10% of teacher scores, but system still overscore and compress extremes; "validate AI scoring against instructor rubrics and subgroup performance" before deployment, not after).

**Cluster affected:** C16 (learner-outcome evaluation infrastructure).

**Issue:** C16 names "process-quality measurement infrastructure" including "LLM-assisted coding pipeline with human validation." But it describes this as the evaluation methodology, not as a system to be validated before use. The paper explicitly warns that LLM scoring looks plausible while overscoring and compressing extremes (`paper_2:L54`, `paper_2:L190`). For the three-arm comparison study (PDG-only vs LLM-only vs PDG+LLM) to produce valid results, the LLM scoring arm must be calibrated against instructor rubrics before the study begins — not during it. If LLM scoring is miscalibrated and that miscalibration varies by treatment arm or subgroup, the study produces invalid results. C16 includes "scoring calibration against instructor rubrics" in C14 (LLM-mediated bias), but C14 is Phase 7+ governance, which means the calibration is concurrent with or after deployment, not prior to the research study.

**Recommended change:** C16 should add an explicit pre-condition: the three-arm comparison study may not begin until LLM scoring has been calibrated against instructor rubrics per C14's protocol (correlation, variance ratio, overscoring bias, subgroup performance). This is a study validity requirement, not an optional governance checkbox.

---

## E.6 — Privacy / consent failure

### Finding E.6.1 — C15 specifies RLS-level pseudonymization but does not address the specific threat that the `learner_node_state` table (C12) joins identifiers to fine-grained mastery traces via `learner_id`

**Paper anchor:** `paper_2:L192` ("minimize stored traces, separate identifiers from learning analytics, and avoid retaining raw student writing longer than needed for validated educational purposes").

**Cluster affected:** C15 (privacy/FERPA/NIST), C12 (learner-state schema).

**Issue:** C15 specifies "RLS policies at schema level separating `student_id` from `learning_analytics_trace`." But C12's `learner_node_state` table contains both `learner_id` and fine-grained mastery evidence fields (`mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`). The table as specified is a direct join of identifier to analytics — the exact join C15 says to prevent. C15 says "no default-path foreign-key joins between identifier and analytics tables — pseudonymization at the DB layer," but C12 proposes a schema where the `learner_id` FK is in the same table as the behavioral trace. This is an internal inconsistency between C15 and C12.

**Recommended change:** C12 should specify that `learner_node_state` uses a pseudonymous `learner_session_token` (not `learner_id`) as the FK, with the `learner_id`↔`learner_session_token` mapping stored in a separate identifier table governed by C15's RLS policies. Consent withdrawal would delete the identifier mapping, leaving the aggregate analytics intact. This resolves the C15/C12 conflict and matches `paper_2:L192`'s explicit guidance.

---

### Finding E.6.2 — No cluster addresses consent withdrawal for raw writing traces that have already been used to infer candidate edges (C17 trace-informed inference)

**Paper anchor:** `paper_2:L192` ("options for withdrawal of consent, anonymization or privacy-enhancing techniques, and documentation of provenance and monitoring" — the NIST framing implies this covers data already ingested).

**Cluster affected:** C15 (privacy/FERPA), C17 (anomalous routing detection + trace-informed revision).

**Issue:** C17's trace-informed revision workflow generates candidate edges from student error patterns. C15's consent withdrawal workflow "purges identifiable data while preserving aggregate analytics." But there is a class of data that is neither raw identifiable trace nor aggregate — the provenance field of a candidate edge may cite specific learner trace events ("5 students with mastery_probability > 0.8 failed downstream node X after completing prerequisite Y"). If a consenting student whose trace generated that evidence later withdraws consent, the candidate edge's provenance record now contains evidence derived from that student's data. C15 does not address this derived-data consent problem. The paper's NIST framing explicitly includes "monitoring" of what derived artifacts exist from a given data subject's records.

**Recommended change:** C15 should add a derived-data audit requirement: when consent is withdrawn, the system must identify any candidate edges whose provenance cites trace events that include the withdrawing learner's data, flag them for instructor review, and either re-derive their provenance from the remaining cohort or downgrade their confidence score. This is structurally analogous to the C1 `disagreement_flag` mechanism but for consent events rather than expert/trace disagreement.

---

## E.7 — Opaque automation of curriculum authority

### Finding E.7.1 — The student-facing path attribution requirement (C15: `instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved`) is specified in C15 but not carried through C11, C12, or C13, which all route students

**Paper anchor:** `paper_2:L194` ("students should also be able to see when a path was altered because of model inference rather than instructor design"); `paper_2:L194` (every proposed edit should be attributable, reviewable, and reversible).

**Cluster affected:** C15 (transparency + attribution), C11 (four sample workflows), C12 (scaffolding fade trajectory), C13 (alternative-entry-route support).

**Issue:** C15 correctly specifies that routing decisions carry `instructor_designed` / `model_inferred_pending_review` / `model_inferred_approved` attribution. But:

- C11's adaptive branching workflow (workflow 3) routes students based on LLM-scored diagnostics and mastery estimates. No mention of routing-decision attribution is in C11.
- C12's scaffold fade trajectory is computed automatically at query time from `mastery_probability`. No mention of attribution for the fade decision is in C12.
- C13's alternative-route surfacing in the student-facing API ("surface at least two distinct `entry_route_type` paths if available") doesn't specify whether the route selection is flagged as `instructor_designed` or `model_inferred`.

Each of these is a routing decision per `paper_2:L194`. A student following an adaptive branch does not know whether that branch was designed by their instructor or inferred by a model — exactly the transparency failure the paper names.

**Recommended change:** C11, C12, and C13 each need an explicit cross-reference to C15's attribution requirement, with the attribution field appearing in the specification of every routing action. C12's fade trajectory should specify that the scaffold-state transition is logged with attribution `model_inferred_approved` (since the mastery-probability computation is model-based). C11's adaptive branching checkpoint must specify that routing decisions surface their attribution to the student UI.

---

### Finding E.7.2 — C8's graph-canon census (periodic count of nodes by tradition_label) is a detect-after-commit mechanism; there is no no-silent-mutation equivalent for authoring-time canon encoding

**Paper anchor:** `paper_2:L194` ("no silent graph mutation … every proposed edit should be attributable, reviewable, and reversible").

**Cluster affected:** C8 (graph-topology bias mitigation), C9 (no-silent-mutation rule).

**Issue:** C9 extends the no-silent-mutation rule across all five services. But C8's canon-bias mitigation is detect-after-commit (health-check census) rather than prevent-before-commit. An instructor adding a new `hard_prerequisite` edge that encodes canon bias (e.g., marking a European analytic tradition concept as the sole required prerequisite for a target node) commits it silently and it remains in the graph until the next health-check catches it. There is no authoring-time gate analogous to C1's `disagreement_flag` or C2's routing validator. The no-silent-mutation rule as implemented in C9 applies to LLM outputs, not to human-authored graph edits that silently reproduce gatekeeping structures.

**Recommended change:** C8's validator soft-warns (currently: "node lacking `tradition_label`; node with `tradition_label` set but `audience_tags` lacking…") should be extended to include commit-time detection of the single-tradition-required-prerequisite pattern described in E.3.1. This transforms the canon-bias check from a periodic audit to a continuous gate, matching the no-silent-mutation principle's spirit.

---

## E.8 — Lossy merges

### Finding E.8.1 — L2.10 (cognitive load modeling per node) is merged into C4 + C13, losing the paper's specific claim about managing element interactivity at sequencing time

**Paper anchor:** `paper_1:L37` (cognitive load theory: "a PDG can function as a tool for controlling element interactivity — isolating one conceptual threshold before adding a second"); `paper_2:L40` (LLM conditioned on PDG can give heavier support on fragile prerequisite nodes — implies node-level load modeling).

**Cluster affected:** C4 (node schema redesign, which gets `jargon_load`), C13 (alternative-entry-route support).

**Issue:** The synthesis maps L2.10 (cognitive load) to "C4 + C13." The C4 schema adds `jargon_load` (enum: low/medium/high) and `accessibility_notes`. But the paper's cognitive-load claim is about **element interactivity at sequencing time** — specifically, how many unintegrated conceptual elements the learner is handling simultaneously. This is not captured by `jargon_load` (a static node property) or by `accessibility_notes`. The paper argues that a PDG can manage this by isolating thresholds before combining them. This is a sequencing constraint, not a node property — it belongs in the `edge_outcome_necessity` junction (C3) as a `cognitive_load_contribution` field or in the path-selector logic (C3/C9). Encoding it only as a static node label loses the dynamic claim entirely.

**Recommended change:** L2.10's full claim should be split: the static per-node `jargon_load` encoding goes in C4 (as currently), but the sequencing-time element-interactivity constraint should be added to C3 (`edge_outcome_necessity` junction) as an optional `element_interactivity_weight` field, allowing the path-selector to limit the number of high-interactivity edges introduced in a single session. Without this, C4's `jargon_load` is a documentation label, not a sequencing gate.

---

### Finding E.8.2 — L5.10 (student-experience validity via node-linked surveys) is merged into C16, but the paper's specific claim is about the survey instrument design, not just the evaluation methodology

**Paper anchor:** `paper_1:L150` (student experience: "survey items should name specific graph elements rather than generic satisfaction items"); `paper_2:L204` ("student understanding of why a path was recommended" as an outcome metric).

**Cluster affected:** C16 (learner-outcome evaluation infrastructure).

**Issue:** C16 names "node-linked student survey instrument" and describes it as "survey items name specific graph elements." This is correct but thin — the synthesis does not note that the paper's student-experience validity claim includes `paper_2:L204`'s metric "student understanding of why a path was recommended." This is not a generic experience measure; it is a direct test of C15's transparency requirement (student-visible path attribution). The synthesis routes this to C16 (evaluation) when it equally belongs as a validation criterion for C15 (transparency). A student who cannot correctly identify whether their path was instructor-designed or model-inferred fails the transparency test even if C15's attribution field is technically present.

**Recommended change:** C16's node-linked survey instrument should include an explicit validation item testing whether students can correctly identify the authority source of their last routing decision (instructor-designed vs model-inferred). This item should be added as a Tier-E acceptance criterion for C15, not only as an evaluation metric in C16. The lossy merge here conflates "evaluate satisfaction" with "validate transparency."

---

## E.9 — Mechanism-match losses

### Finding E.9.1 — C3 reduces "goal-relative dependency strength" to a junction table, but the paper's claim includes the authoring-time enforcement that dependencies must be re-evaluated when learning outcomes change

**Paper anchor:** `paper_1:L110` ("dependency claims are meaningful only relative to desired performances"); `paper_2:L62` ("the pedagogical dependency path is therefore goal-relative, whereas the influence path is not"); `paper_1:L112` (sixth stage of construction workflow: "revise the graph with empirical evidence from student performance").

**Cluster affected:** C3 (goal-relative parameterization).

**Issue:** C3's mechanism is correct as far as it goes: a junction table linking edges to outcomes is the right substrate. But the paper's goal-relativity claim includes a process claim — when a learning outcome changes or a new outcome is added, the existing edge-outcome necessity classifications must be re-evaluated. C3 adds a `default_necessity_level` fallback and a quarterly validator soft-warn, but there is no mechanism that fires when a learning outcome is modified. If an outcome changes scope and an edge previously classified `required` for that outcome is now `optional`, the junction table entry remains `required` until the next quarterly review. In a humanities curriculum that updates outcomes by semester, this creates systematic false prerequisites.

**Recommended change:** C3 should specify that any modification to a `learning_outcomes` row triggers a soft-warn for all `edge_outcome_necessity` entries linked to that outcome, queuing them for re-validation. This is not complex — it is a DB trigger or a pre-commit hook check on the `learning_outcomes` table. Without it, the junction table is correct at authoring time but not dynamically maintained.

---

### Finding E.9.2 — C5 encodes the detect-remediate-retest state machine as a Phase 7+ deferral but the substrate required for it (misconception nodes) is Tier A — this creates a substrate without a use contract

**Paper anchor:** `paper_1:L43` ("unlearning a commonsense meaning before a disciplinary meaning becomes available" — this is a different teaching state, not a future-phase concern); `paper_2:L186` (learner state must distinguish missing-concept from active-misconception — this is a substrate requirement, not a Phase 7+ feature).

**Cluster affected:** C5 (misconception sub-graph encoding).

**Issue:** C5 creates misconception nodes (Tier A substrate) but defers the detect-remediate-retest state machine to "Cluster 11, but the substrate must support it now." This is correct as written, but it creates a substrate layer with no use contract at authoring time. More problematically, `paper_2:L186` is cited in C5's contributing claims as a "schema implication: learner state must distinguish missing-concept from active-misconception." But the learner-state schema (C12) does not include a field distinguishing these two states. `learner_node_state` has `mastery_probability` and `recent_errors` but no `misconception_active_flag` or `misconception_node_id` FK. A student with `mastery_probability: 0.2` on a concept could have a missing-concept state or an active-misconception state — the C12 schema cannot distinguish them, which means the routing logic in C11/C12 cannot implement the paper's required detect-remediate-retest branching.

**Recommended change:** C12 should add `active_misconception_ids` (array of FK to misconception nodes) as a field in `learner_node_state`. This closes the substrate gap that C5 names but C12 omits. Without it, the misconception sub-graph (C5) is an authorable artifact with no learner-state hook, and the detect-remediate-retest state machine cannot be implemented regardless of when Phase 7+ arrives.

---

## E.10 — Sub-concerns landed nowhere

### Finding E.10.1 — L2.12 (assessment linkage at node level) is mapped to C4 + C16 but no Tier A mechanism actually creates or validates the assessments; C4's `assessment_items` field is a jsonb stub with no authoring discipline

**Paper anchor:** `paper_1:L136` (threshold nodes must have direct diagnostics); `paper_1:L114` (schema table: outcome alignment field specifies "which assignment, discussion move, or exam item the node supports").

**Cluster affected:** C4 (node schema redesign), C16 (evaluation infrastructure).

**Issue:** The sub-concern coverage table maps L2.12 to "C4 + C16." C4 adds `assessment_items` as a jsonb array OR FK to an assessments table. But C4 does not define what constitutes a valid assessment item, who is responsible for authoring them, or what the authoring discipline looks like. The validator soft-warn in C4 ("any `threshold_concept` node lacking `assessment_items`: soft-warn") will fire for the entire corpus of 380 nodes after migration, but there is no cluster that specifies how to author those assessment items, what a valid one looks like, or which cluster governs assessment-item quality. C6 (backward-design authoring discipline) covers node and edge authoring but does not mention assessment-item authoring. C16 (evaluation) consumes assessment data but does not produce the assessment items. L2.12 is nominally covered but in practice requires a sub-mechanism that no cluster owns.

**Recommended change:** C6 (authoring discipline) should add a step 6 covering assessment-item authoring discipline: minimum fields per assessment item (learning outcome, task type, rubric pointer, associated node), who can author, and a soft-warn for assessment items that are threshold-concept-attached but lack a rubric pointer. This is not a Phase 7+ concern — assessment items linked to threshold nodes are needed before any evaluation study begins.

---

### Finding E.10.2 — L4.4 (subgroup analysis applied to LLM outputs) is mapped to C14 + C16 but C14 specifies only "subgroup performance" as part of scoring calibration — it does not name which subgroups, at what minimum cell sizes, or at what cadence the analysis must run to produce actionable findings

**Paper anchor:** `paper_2:L206` ("Do multilingual students receive poorer feedback or less accurate scoring? Does the system over-pathologize certain interpretive styles as misconceptions?"); `paper_1:L148` (equity effects: "Heterogeneity-of-treatment analysis; matched-cohort quasi-experiments" — specific methodology named).

**Cluster affected:** C14 (LLM-mediated bias mitigation), C16 (learner-outcome evaluation infrastructure).

**Issue:** C14 mentions "subgroup performance (per Cluster 16 evaluation infrastructure)" as one of four metrics in scoring calibration. C16 names the subgroups for HTE analysis: "prior preparation, verbal ability proxy, language background, major/non-major." But neither cluster names minimum cell sizes, statistical power considerations, or what constitutes an actionable finding (e.g., what differential triggers a remediation or escalation). The paper (`paper_2:L206`) frames this as a concrete governance question with concrete answers required, not a methodology pointer. Without minimum cell sizes and escalation thresholds, subgroup analysis is present in name only — any N < minimum cell size is statistically uninformative and provides false reassurance.

**Recommended change:** C16 should add a pre-registration requirement specifying: (1) minimum cell size per subgroup before a subgroup analysis is reportable (suggest N ≥ 30 as floor), (2) what statistical threshold constitutes an actionable differential (e.g., effect size > 0.2 SD or routing-rate differential > 10 percentage points), and (3) what the escalation path is when the threshold is crossed (named reviewer, named action). Without these, the HTE analysis is a documentation artifact, not an actionable equity mechanism.

---

### Finding E.10.3 — L3.15 (tool-stack evaluation: Postgres+JSONB+CTEs vs Neo4j dual-layer) is mapped to C9 as one item in its mechanism, but the trigger criterion for evaluation ("introduction of analytics or trace-informed-revision workflows") is also the trigger for Phase 7+ work — meaning the evaluation never has a forcing function

**Paper anchor:** `paper_2:L198` (five-service architecture; property-graph database such as Neo4j is a strong fit when edges need rich attributes).

**Cluster affected:** C9 (instructional-spine architecture).

**Issue:** C9 names "Tool-stack evaluation: Postgres+JSONB+recursive CTEs vs Neo4j dual-layer. Per L3.15 finding, the threshold for graph-store evaluation is the introduction of analytics or trace-informed-revision workflows." The Tier A substrate clusters (C1-C5) are adding rich edge attributes (9 new fields in C1 alone, plus the junction table in C3). At some point before Phase 7+ analytics exist, the graph store may already be better served by a property-graph engine. But C9 defers the evaluation to "when analytics or trace-informed-revision workflows are introduced" — at which point the migration cost from Postgres to Neo4j is substantially higher (existing learner traces, existing provenance records, existing junction tables all need migration). The paper recommends Neo4j evaluation at design time, not after the Postgres schema has grown to accommodate 9-field edges, junction tables, and learner state.

**Recommended change:** C9 should add a forcing function: the tool-stack evaluation (Postgres vs Neo4j) must occur before any Tier A migration is applied to production, not when Phase 7+ analytics arrive. The evaluation is a one-time architectural decision; deferring it until after the substrate has been built on Postgres effectively pre-decides in favor of Postgres by accrual.

---

## E.11 — Internal inconsistencies between clusters

### Finding E.11.1 — C1 specifies `expert_confidence` default as `low` but C2's mass retyping defaults to `hard_prerequisite` — these two defaults are in direct tension

**Paper anchor:** `paper_1:L162` (experts systematically overstate necessity; encode confidence levels, separate hard from soft edges, validate with student work); `paper_2:L82` (3-source confidence model; `expert_confidence` differentiates authoritative from provisional edges).

**Cluster affected:** C1 (contestability substrate), C2 (edge-type taxonomy expansion).

**Issue:** C1 states "default `low`" for `expert_confidence` on newly authored edges. This is correct per the paper. C2 states that the 516 existing `pedagogical_prerequisite` edges retype to `hard_prerequisite` by default. A `hard_prerequisite` edge with `expert_confidence: low` is a structural contradiction: the edge type asserts a hard pedagogical necessity while the confidence field asserts the claim is unvalidated. If the C1 default applies to re-typed edges (which is not stated), the system will have 516 `hard_prerequisite` edges with `expert_confidence: low` — which C1's validator soft-warn will immediately flag (any edge with `expert_confidence: high` AND empty `counterexamples` is flagged — but the converse is silent: `hard_prerequisite` with `expert_confidence: low` produces no warning). This is the expert-blind-spot failure mode encoded at the schema level.

**Recommended change:** This conflict is the E.2.1 finding seen from the consistency angle. The resolution is the same: default the 516 edges to `soft_prerequisite`, not `hard_prerequisite`, OR add a validator soft-warn for `edge_type: hard_prerequisite` with `expert_confidence: low` (provisional hard prerequisite — requires validation before use in routing). The synthesis should make this conflict explicit and resolve it consistently.

---

### Finding E.11.2 — C15 specifies `consent_version` on student-record rows but C12's `learner_node_state` table does not inherit consent versioning — meaning rows written under an older consent version are not distinguishable from rows written under a newer one

**Paper anchor:** `paper_2:L192` (consent management, withdrawal options, documentation of provenance and monitoring); NIST recommendation for consent-version tracking.

**Cluster affected:** C15 (privacy/FERPA), C12 (learner-state schema).

**Issue:** C15 specifies `consent_version` on "every student-record row." C12's `learner_node_state` fields do not include `consent_version`. If a student updates their consent scope (e.g., withdrawing consent for trace data use in research but retaining consent for instructional use), the system has no way to know which `learner_node_state` rows were written under which consent version. This is a practical implementation gap that would manifest as either over-retention (using rows written under withdrawn consent) or under-retention (purging rows still covered by current consent) during a withdrawal event.

**Recommended change:** C12 should add `consent_version` as a field in `learner_node_state`, matching C15's schema requirement. This is a one-field addition with significant compliance implications.

---

### Finding E.11.3 — C3's `default_necessity_level: recommended` fallback and C13's "no canonical-path enforcement" rule conflict with C17's `bypass-and-succeed` anomaly trigger

**Paper anchor:** `paper_2:L74` (three-way diagnostic signal types — `bypass-and-succeed` falsifies a hard-prerequisite claim, implying a `hard_prerequisite` was the expected path).

**Cluster affected:** C3 (goal-relative parameterization), C13 (alternative-entry-route support), C17 (anomalous routing detection).

**Issue:** C3 says the default for edges without outcome-specific necessity is `recommended` (never `required`) because experts over-state necessity. C13 says path-selector should surface multiple entry routes and not enforce canonical paths. C17's `bypass-and-succeed` anomaly trigger fires when a student succeeds downstream "without completing the supposedly required prerequisite." But if C3 defaults to `recommended` and C13 surfaces alternative routes, there are no "required" prerequisites to bypass — every path is already `recommended`. The `bypass-and-succeed` detection logic assumes some prerequisites are hard-required; if C3's defaults are applied consistently, the detection trigger fires rarely or never until outcome-specific necessity classifications are manually added. This means C17 is largely inert in Phase 7+ until the `edge_outcome_necessity` junction table has substantial data — which the synthesis does not note.

**Recommended change:** C17 should explicitly acknowledge that its `bypass-and-succeed` detection depends on `edge_type: hard_prerequisite` or `necessity_level: required` classifications in the junction table. Until those classifications are populated (a Phase 7+ authoring task per C3), C17's anomaly detection operates on a much smaller target set than the synthesis implies. The synthesis should name this dependency explicitly rather than presenting C17 as a fully functional detection layer at Phase 7+ launch.

---

## E.12 — Phase 6 master plan interaction

### Finding E.12.1 — Options (a), (b), (c) are not actually distinct — option (c) is a special case of (b) with lower administrative friction, not a third architectural choice

**Paper anchor:** N/A (this is a synthesis-internal structural issue, not a paper-anchored finding).

**Cluster affected:** Phase 6 master-plan-input subsection.

**Issue:** The three options are presented as distinct choices:
- (a) Expand Phase 6 to include Tier A substrate redesign.
- (b) Keep Phase 6 narrow; land Tier A as Phase 6.5 or Phase 7 substrate redesign.
- (c) File Tier A clusters as Issues; user adjudicates per-Issue sequencing.

Option (c) and option (b) produce the same architectural outcome: Tier A does not land before SEP backfill. The difference is only administrative — (b) uses a Phase-numbered plan revision; (c) uses Issues. Both result in SEP backfill operating on the current nodes table. The synthesis says "(c) [is] the simplest path" and "(a) [is] the most architecturally coherent" — which accurately implies (b) and (c) are equivalent. Presenting them as three options obscures the real binary choice: either Phase 6 expands to include Tier A (option a) or it does not (options b and c). The user is not being asked to make three architectural choices; they are being asked to make one and choose an administrative mechanism for the second.

**Recommended change:** The Phase 6 subsection should frame this as a binary architectural choice: (A) expand Phase 6 scope (Clusters 1, 2, 4 at minimum before SEP backfill), or (B) proceed narrow and accept a follow-up re-backfill. Option (c) from the synthesis should be noted as the lower-friction administrative implementation of (B), not a third architectural path. This makes the user's actual decision clearer.

---

### Finding E.12.2 — The synthesis does not name the specific sequencing risk if Phase 6 SEP backfill operates on the nodes table before Cluster 4 redesigns it

**Paper anchor:** `paper_2:L80` (node schema table — 10 required node fields); `paper_1:L114–123` (schema table — 7 schema dimensions, including `node_type`, `disciplinary_domain`, `granularity`).

**Cluster affected:** Phase 6 master-plan-input subsection, C4 (node schema redesign).

**Issue:** The synthesis says "SEP backfill (existing Phase 6 task 4) operates on the nodes table, and Cluster 4 redesigns the nodes table" — but it does not name the specific risk. The SEP backfill will embed existing node records. If those records lack `node_type`, `disciplinary_domain`, and `granularity` (all added by C4), the embeddings will be computed on impoverished node representations. After C4 lands, the nodes will be richer — but the existing embeddings will be stale. A re-backfill will be required. The synthesis acknowledges "accept a follow-up re-backfill" in option (b) but does not quantify the cost or name what fields are specifically missing from the current node representation that would most degrade embedding quality.

**Recommended change:** The Phase 6 subsection should name the specific fields that most degrade embedding quality if absent at backfill time (likely `node_type`, `disciplinary_domain`, `granularity`, `canonical_sources`, and `misconceptions` — the semantically richest fields from C4's schema). This gives the user a concrete basis for the option (A) vs (B) decision: if those five fields affect embedding quality substantially, (A) is strongly preferable; if the current node labels are sufficient for useful embeddings, (B) is acceptable.

---

## Summary

**Total findings: 22**

(E.1: 3 findings; E.2: 3; E.3: 2; E.4: 2; E.5: 2; E.6: 2; E.7: 2; E.8: 2; E.9: 2; E.10: 3; E.11: 3; E.12: 2)

**Highest-priority findings (must address before clusters move to Issues):**

1. **E.2.1 — C2 defaults 516 edges to `hard_prerequisite`.** This is the single most consequential fidelity failure. The paper explicitly says expert default is overconfidence; defaulting to the most dangerous value inverts the epistemically correct prior. The fix is one word in the migration spec (`soft_prerequisite` instead of `hard_prerequisite`) with significant architectural downstream effects. Must be resolved before the C2 Issue is filed.

2. **E.11.1 — C1 and C2 are in direct structural conflict.** `expert_confidence: low` default plus `hard_prerequisite` mass-retyping produces 516 structurally contradictory edges. This is not a minor inconsistency — it means the contestability substrate (C1) and the edge-type expansion (C2) will produce incoherent data on landing. Needs resolution in the same pass that fixes E.2.1.

3. **E.6.1 — C15 specifies RLS separation of identifiers from analytics but C12's `learner_node_state` table directly violates this by placing `learner_id` in the same table as behavioral traces.** This is a concrete privacy compliance failure, not an architectural abstraction. If C12's schema lands as specified, the FERPA/NIST separation C15 promises does not exist at the DB layer.

**Sub-concerns the synthesis claims to cover but where practical coverage is weak:**

- L2.10 (cognitive load at sequencing time) is reduced to a static node label (`jargon_load`) in C4 — loses the element-interactivity sequencing claim (E.8.1).
- L4.4 (subgroup analysis on LLM outputs) is present in name but lacks actionable thresholds — without minimum cell sizes and escalation triggers, it is a documentation checkbox (E.10.2).
- L2.12 (assessment linkage at node level) is a jsonb stub in C4 with no authoring discipline to populate it — the validator soft-warn will fire immediately post-migration with no mechanism to satisfy it (E.10.1).
- L3.15 (tool-stack evaluation) is deferred past the point where the Postgres schema growth effectively pre-decides the architecture (E.10.3).

**Clusters that should split or merge differently:**

- C13's `entry_route_type` schema field should be extracted from Tier D and promoted to Tier A/B substrate (E.3.2). The path-selector teaching logic stays Tier D; the schema field is an authoring-time concern.
- C3's goal-relativity mechanism needs a re-evaluation trigger when learning outcomes change — without this it is correct at authoring time but not maintained (E.9.1). This is a one-step addition to C3, not a split.
- C5's detect-remediate-retest state machine deferral to C11 is acceptable, but C12 needs `active_misconception_ids` added to close the learner-state hook gap (E.9.2). This is a C12 addition, not a C5 split.

**Overall readiness for Phase F (Issue authoring):** The synthesis is not ready for Phase F without resolving at minimum findings E.2.1, E.11.1, and E.6.1. These are not refinements — they are structural errors where the mechanism as specified either contradicts the paper's core claim (E.2.1), contradicts another cluster's schema (E.11.1), or violates the privacy guarantee the synthesis explicitly commits to (E.6.1). The remaining findings are mostly omissions and under-specifications that should be worked into the cluster specs before Issue filing, but they do not block Phase F if the three critical findings are resolved first. The clusters that are cleanest (C1 core mechanism, C7, C8 topology census, C9 architecture invariants, C10 prompt templates, C15 override events table, C16 evaluation methodology) can move to Issues immediately after the critical fixes land; the clusters with structural issues (C2, C3, C12, C13 field tier) need targeted revision first.
