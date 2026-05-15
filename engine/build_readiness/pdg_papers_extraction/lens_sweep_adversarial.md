# Lens sweep — Adversarial / Governance / Bias / Equity (L4.1–L4.13)

> **Filled by Phase C adversarial lens agent.** Re-reads BOTH papers end-to-end through the single lens of failure modes, governance machinery, equity protections, regulatory alignment (FERPA, NIST GenAI profile, UNESCO). Section-sequential extraction tends to under-tag adversarial/bias claims that appear in case studies, schema tables, or evaluation sections rather than the dedicated risks section. This pass is the safety net.
>
> **Coverage rule:** every sub-concern below must have ≥1 finding OR an explicit `_No findings because…_` justification.

## Sources

- Paper 1: `/Users/shanekidd/Documents/Claude_Files/temp/Assessing the Utility of Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`
- Paper 2: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`

---

## Findings by sub-concern

### L4.1 — Cultural / canon bias

- **paper_1:Limitations section** — "A second risk is **cultural and epistemic bias**. If the graph assumes one canonical route through a tradition, it may reproduce disciplinary gatekeeping — for example, by silently privileging European conceptual histories, elite genres, or jargon-heavy formulations as the only valid entry point."
  - **Paideia applicability:** New ADR needed — graph-structure bias policy. The PDG node schema must include an `L1.13`-compatible equity-metadata field (`assumed_background`, `cultural_specificity_label`, `jargon_load`) AND require that any node or edge representing a single-tradition pathway carries a `tradition_label` and an `alternative_routes` reference. This is distinct from the existing anti-bias mechanism (which addresses LLM input bias), because the bias here lives in the graph topology itself, not in the LLM's context window.

- **paper_1:Limitations section** — "The risk is not unique to PDGs, but PDGs can make it visible if instructors deliberately tag nodes for assumed background, cultural specificity, and alternatives." Mitigation direction: tags that surface bias rather than hide it, and Hovland's humanities SoTL work is cited as a model for resisting reduction to narrow predefined outcomes.
  - **Paideia applicability:** The equity-metadata schema column (named in Paper 1's schema table: "Equity metadata — Assumed background knowledge, jargon load, culturally specific references") must be a required field in the Paideia graph schema. A new graph-linting validator soft-warn should fire when any node lacks a `cultural_specificity_label` entry.

- **paper_2:Risks, Governance, and Equity section** — "A graph can harden one tradition's pathway into the default route and convert a contestable curriculum choice into a pseudo-natural learning dependency." Paper 2 sharpens Paper 1's concern: the PDG's claim to represent pedagogical necessity makes it a stronger vehicle for canon-bias reification than a mere reading list or syllabus.
  - **Paideia applicability:** New operations procedure in `engine/operations/` for graph-structure-bias review: when a node representing a thinker, tradition, or text from a single disciplinary lineage is authored, the workflow must include a contestation check — is there a non-canonical, non-European, or non-jargon-heavy entry route to the same learning outcome? Posture rule until mechanizable.

- **paper_2:Risks, Governance, and Equity section** — Mitigation named: "store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."
  - **Paideia applicability:** Extension to the graph schema (via ADR) — `alternative_route_ids` as a required field on prerequisite edges that carry high `canonical_importance` but unverified `pedagogical_necessity`. Pairs with L1.18 (alternative-entry-route support) from Lens 1 but specifically motivated here by equity, not just cognitive flexibility.

- **paper_2:Implementation and Evaluation section** — "Are some traditions overrepresented as 'required prerequisites' rather than 'one valid route'?" Framed as an empirically testable evaluation criterion, not just a normative concern.
  - **Paideia applicability:** New periodic graph census metric — count nodes by tradition/canon affiliation; flag traditions that appear only as required prerequisites and never as alternative paths. This is a health-check cadence artifact, not a one-time authoring check.

- **paper_1:Case studies section** — The five case studies (Kant/Husserl, Saussure/Derrida, Austin/Butler, Nietzsche/Foucault, Ranke/historiography) each demonstrate how influence maps encode European canonical lineage as the "natural" prerequisite sequence. In every case the paper argues that pedagogical necessity is far weaker than the canonical narrative implies.
  - **Paideia applicability:** When authoring Phase 5+ PDG nodes covering continental philosophy, literary theory, or historiography, each node's prerequisites must be audited against the case-study findings: historical prestige is not a sufficient basis for a `hard_prerequisite` edge.

---

### L4.2 — Expert blind spot

- **paper_1:Limitations section** — "A third risk is the creation of **false prerequisites** through expert blind spot. Scheines and colleagues explicitly note that expert knowledge is subject to this problem, and Corrigan's literary-studies essay shows how experts forget that disciplinary meanings of common words are not obvious to students."
  - **Paideia applicability:** Node-authoring workflow must include a "novice translation" step: every node added by a domain expert must include at least one entry in `misconceptions` naming the folk or commonsense meaning students bring in, distinct from the disciplinary meaning the node teaches. This prevents expert blind spot from silently encoding a prerequisite that only appears necessary because experts have forgotten the folk-to-disciplinary transition.

- **paper_1:Limitations section** — Mitigation: "encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict."
  - **Paideia applicability:** `confidence` is a required schema field (Paper 1 schema table: "Confidence level — High, medium, low, with rationale and source basis"). A `confidence: null` row on any edge is an uncaught expert-blind-spot claim. New validator soft-warn: edges with null or missing confidence values.

- **paper_2:Comparative frame table** — "Instructor-authored or instructor-validated graphs; provenance for every edge; low-confidence and culturally loaded edges visibly flagged." Expert blind spot mitigation is linked to the same provenance-and-confidence apparatus used for bias and governance generally.
  - **Paideia applicability:** Provenance per edge (L1.5) — fields `created_by`, `rationale`, `last_reviewed` — creates an audit trail that allows future reviewers to ask whether a `hard_prerequisite` edge was validated with student data or rests on pure expert assumption.

- **paper_1:How to construct section** — "Second, identify bottlenecks through student work, diagnostic discussion, or a Decoding interview." Expert elicitation alone is insufficient; bottleneck identification must involve student-facing evidence.
  - **Paideia applicability:** Operations procedure for PDG authoring: any edge classified as `hard_prerequisite` must cite either (a) a Decoding-the-Disciplines-style interview, (b) prior student performance data showing bottleneck behavior, or (c) an explicit expert rationale with `confidence: low` until validated. Edges without such citation must default to `soft_prerequisite` or `helpful_bridge`.

---

### L4.3 — Multilingual fairness

- **paper_2:Risks, Governance, and Equity section** — "UNESCO warns that many countries lack adequate regulation and validation practices for GenAI in education, and multilingual evaluation work shows that educational-task performance can vary by language, often disadvantaging lower-resource languages."
  - **Paideia applicability:** For Phase 7+ student-facing deployment, LLM-generated node explanations, formative questions, and feedback must be audited for multilingual quality disparity. A transparency report metric should include LLM output quality by language of instruction. Flag as a Phase 7 GitHub Issue: multilingual quality audit is currently absent from the Paideia roadmap.

- **paper_2:Risks, Governance, and Equity section** — "In humanities, this extends beyond language to canon formation, interpretive tradition, and epistemic authority." Multilingual fairness in humanities is not only about translation quality but about whose intellectual tradition is treated as the default prerequisite sequence.
  - **Paideia applicability:** Two distinct interventions are required: (1) LLM output quality by language (technical monitoring), and (2) graph-level canon audit (structural — see L4.1). These are independent problems; the `language_preference` field in the learner-state schema (Paper 2) enables the former; the canon audit addresses the latter.

- **paper_2:Implementation and Evaluation section** — "Do multilingual students receive poorer feedback or less accurate scoring?" Named as an explicit evaluation criterion in deployment design.
  - **Paideia applicability:** Paideia evaluation plan for Phase 7+ must include subgroup comparison of feedback quality and scoring accuracy by learner language background as a non-optional analysis stratum.

- **paper_1:Schema table** — "Audience tag — Introductory; intermediate; advanced; majors/non-majors; **multilingual cohort**." The schema explicitly includes `multilingual cohort` as a first-class audience tag — the expected learning path may differ for multilingual students within the same course.
  - **Paideia applicability:** `audience_tags` on nodes and edges must include `multilingual_cohort` as a first-class enumerated value, not a free-text annotation. This enables the adaptive layer to select different scaffolds or alternative routes for multilingual learners rather than routing through a monolingual-canonical sequence.

---

### L4.4 — Subgroup-analysis discipline

- **paper_1:Evaluation metrics table** — "Equity effects — Differential gains by prior preparation, verbal ability, language background, major/non-major status. Heterogeneity-of-treatment analysis; matched-cohort quasi-experiments."
  - **Paideia applicability:** Any Paideia PDG deployment evaluation must include heterogeneity-of-treatment-effects analysis as a named metric, not just aggregate learning gains. Write this into the evaluation protocol as a non-optional stratum.

- **paper_2:Implementation and Evaluation section** — "During the term, instructors should review low-confidence edges weekly, audit a sample of scored diagnostics, and examine whether branches are disproportionately burdening specific groups or language backgrounds."
  - **Paideia applicability:** The review layer must expose branch-routing statistics by learner cohort, not just aggregate counts. Disproportionate routing of specific subgroups (first-generation students, non-majors, multilingual learners) onto extended remediation paths is a graph-equity signal. New operations procedure item: "Weekly instructor review includes an equity routing check."

- **paper_2:Implementation and Evaluation section** — "For fairness and governance, evaluation must also ask subgroup questions" — naming three: multilingual feedback quality, over-pathologizing of interpretive styles, tradition overrepresentation as required prerequisites.
  - **Paideia applicability:** The three subgroup questions map to three distinct Paideia mechanisms: (a) multilingual feedback quality → LLM output audit (L4.3), (b) over-pathologizing → scoring rubric review (L4.5), (c) tradition overrepresentation → graph canon census (L4.1). Document these as three separate periodic review tasks in the review-layer operations procedure.

- **paper_2:Implementation and Evaluation section** — "A credible LLM+PDG deployment should therefore publish periodic transparency reports on graph edits, override rates, subgroup discrepancies, and content-provenance coverage."
  - **Paideia applicability:** Transparency report template as a named operations artifact with explicit fields: `graph_edit_count_by_type`, `override_rate_by_node`, `subgroup_routing_discrepancies`, `provenance_coverage_pct`. Named output of the periodic health check cadence.

- **paper_1:Empirical evidence section** — Nesbit and Adesope meta-analysis: "learners with lower verbal ability may benefit more than high-verbal-ability learners from maps, plausibly because node-link syntax can reduce the linguistic burden of scholarly prose." Positive equity finding — PDGs may preferentially benefit less linguistically privileged learners.
  - **Paideia applicability:** Node-level `jargon_load` field (equity metadata, L1.13) is the enabling mechanism. Without it, the PDG risks providing the same jargon-heavy description to all learners. The `accessibility_notes` field (named in Paper 2's node schema) should include lower-register paraphrases as a first-class authoring concern, not a post-hoc accessibility add-on.

---

### L4.5 — Anti-pathologizing-interpretive-styles

- **paper_2:Risks, Governance, and Equity section** — "It [LLM scoring] can also move students toward uncritical acceptance of AI-generated interpretations. That concern is magnified in humanities because many learning goals involve argument quality, interpretive judgment, nuance, and evidential reasoning rather than closed-form correctness."
  - **Paideia applicability:** Scoring rubrics fed to the LLM must explicitly distinguish legitimate alternative interpretations from genuine misconceptions that block further learning. A rubric that treats one canonical reading as the only correct answer will systematically over-pathologize heterodox interpretive styles. New rubric design principle: every assessment item must name at least one "legitimate alternative interpretation" that should NOT trigger the misconception-remediation path.

- **paper_2:Implementation and Evaluation section** — "Does the system over-pathologize certain interpretive styles as misconceptions?" Named as an explicit evaluation criterion.
  - **Paideia applicability:** When a learner is routed to a misconception-remediation node more than N times for the same concept, flag for instructor review rather than auto-escalating remediation intensity. Repeated "misconception" routing may indicate a heterodox-but-valid interpretive style, not a genuine error. New soft-warn in the review layer.

- **paper_2:Student-facing explainer prompt template** — "Avoid: introducing unapproved terminology; assuming mastery of unmet prerequisites." The `approved_examples` and `approved terminology` constraint implicitly creates a pathologizing risk: if approved terminology excludes alternative interpretive traditions, students reasoning from those traditions will appear to be using incorrect language.
  - **Paideia applicability:** The `approved_examples` field on nodes must be populated from multiple interpretive traditions. Operations procedure check: when adding approved examples to a node, require at least one example drawn from a non-dominant interpretive tradition (feminist, postcolonial, non-Western philosophical) where the node's concept is applicable cross-traditionally.

- **paper_1:How to construct section** — "Third, preserve **multiple routes** into complex topics. Spiro's work on ill-structured domains suggests that one-lens sequencing is dangerous; a good PDG should therefore allow case-based, conceptual, methodological, and historical entry points that later converge."
  - **Paideia applicability:** Multiple-entry-route support (L1.18) is the structural mechanism for anti-pathologizing. A learner who takes a case-based route must not be scored as having a misconception because they reached a target concept via a different path than the canonical one. Scoring rubrics must be path-agnostic for argument quality and path-aware only for prerequisite-completeness checks.

---

### L4.6 — FERPA / privacy / consent

- **paper_2:Risks, Governance, and Equity section** — "Educational AI systems often need detailed trace data that go beyond conventional student records, and the U.S. Department of Education explicitly warns that AI's dependence on such data requires renewed attention to governance and may not align automatically with FERPA or state privacy obligations."
  - **Paideia applicability:** Phase 7+ deployment requires a FERPA compliance review before any student trace data is stored. Paideia's Postgres/Supabase schema has no student-identifiable data yet. When it does, RLS policies must separate identifiers from learning analytics at the database schema level, not just at the application layer. Capture as a Phase 7 product ADR requirement before schema work begins.

- **paper_2:Risks, Governance, and Equity section** — "FERPA's regulations emphasize protection of student privacy, limitations on personally identifiable information, and agreements governing research use and destruction of data when no longer needed."
  - **Paideia applicability:** Data retention policy must be explicit: student writing submitted for LLM scoring should not be retained beyond the immediate session unless explicit consent is obtained with a defined retention period. Product ADR candidate: "Student trace data retention and consent policy for LLM+PDG systems."

- **paper_2:Risks, Governance, and Equity section** — "NIST further recommends options for withdrawal of consent, anonymization or privacy-enhancing techniques, and documentation of provenance and monitoring. For LLM+PDG systems, the obvious implication is to minimize stored traces, separate identifiers from learning analytics, and avoid retaining raw student writing longer than needed for validated educational purposes."
  - **Paideia applicability:** Three concrete schema requirements: (1) `student_id` and `learning_analytics_trace` must be stored in separate tables with no foreign key joins in the default query path (pseudonymization at schema level), (2) a `consent_version` field must exist on any student-record row, (3) a `retention_expiry` field must exist on raw writing/trace records. None of these exist in current Paideia schema.

- **paper_2:Recommended schema — Learner state** — Fields include `language_preference` and `help_seeking_pattern`. Both are student-identifiable behavioral attributes; the paper does not flag them as privacy-sensitive, but they are.
  - **Paideia applicability:** The learner-state schema (L1.15) must carry a privacy classification alongside each field at authoring time. `language_preference` is lower-risk (aggregatable). `help_seeking_pattern` combined with `recent_errors` is potentially re-identifiable in small cohorts. Treat the learner-state schema as a privacy-sensitive surface from day one of design.

---

### L4.7 — NIST GenAI profile alignment

- **paper_2:Risks, Governance, and Equity section** — "NIST's GenAI profile explicitly treats confabulation as a core risk and recommends empirical testing, documentation of human-domain-knowledge interventions, review of sources and citations, and monitoring of overrides."
  - **Paideia applicability:** The four NIST-recommended controls must be first-class operations requirements: (1) empirical testing of LLM outputs against expert-validated graph structure before deployment, (2) documentation of human-domain-knowledge interventions (the instructor-review checkpoints in Paper 2's workflows), (3) source-and-citation review for every LLM-generated node explanation or candidate edge, (4) override monitoring (see L4.8). A new operations doc (`engine/operations/nist-genai-alignment.md`) should name these four controls and reference where each is implemented in Paideia's architecture.

- **paper_2:Comparative frame table** — "Transparency and inspectability — Higher than LLM-only if graph provenance, confidence, and overrides are logged." NIST's transparency requirement maps directly to the provenance-and-confidence apparatus.
  - **Paideia applicability:** Provenance per edge (L1.5) and confidence model (L1.4) are the NIST transparency controls at the graph layer. They are not optional schema enrichments — they are the mechanism by which the Paideia system meets the NIST transparency requirement. This framing (provenance-as-NIST-control) should appear in the relevant ADR.

- **paper_2:Implementation and Evaluation section** — The Department of Education AI report is cited alongside NIST, emphasizing "evidence of effectiveness and varied educational settings" as a deployment requirement.
  - **Paideia applicability:** A Phase 7 pre-deployment gate must include empirical testing in at least one real humanities course context, with the PDG+LLM system compared against a PDG-only or conventional condition. This is the "evidence of effectiveness" requirement. Name it as a Tier 1 criterion in the Phase 7 build-readiness gate.

- **paper_2:Evidence Base section** — "Even in a tightly bounded worked-solution context, ChatGPT-generated help initially failed quality checks on 32 percent of problems before mitigation." (Pardos & Bhandari study.)
  - **Paideia applicability:** The 32% pre-mitigation failure rate is the empirical baseline for unmitigated LLM confabulation in tutoring contexts. Paideia must implement self-consistency (L3.8) or equivalent quality gates — first-pass LLM outputs are not deployment-ready. The 32% figure should appear in any Paideia governance document as the prior for unmitigated LLM confabulation risk.

---

### L4.8 — Override logging

- **paper_2:Risks, Governance, and Equity section** — "NIST likewise recommends documenting human-AI configuration, using structured feedback from users and impacted communities, and **tracking when human operators override AI decisions**."
  - **Paideia applicability:** Override events must be a first-class schema entity. A dedicated `override_events` table (or graph-level `override_log` on edges/nodes) should record: `timestamp`, `overridden_entity` (edge_id or node_id), `override_type` (score, routing, prerequisite), `overriding_actor` (instructor, committee, student), `reason`, `prior_value`, `new_value`. This is the mechanization of the override-logging posture the paper recommends.

- **paper_2:Risks, Governance, and Equity section** — "A credible LLM+PDG deployment should therefore publish periodic transparency reports on graph edits, override rates, subgroup discrepancies, and content-provenance coverage."
  - **Paideia applicability:** Transparency report structure must include `override_rate_by_node_type`, `override_rate_by_instructor`, and `override_rate_by_time_period`. An increasing override rate on a particular node type signals systematic LLM miscalibration for that domain — a graph-governance alarm requiring escalation.

- **paper_2:Workflow table — Adaptive branching lesson** — "Human checkpoint on anomalies or disputed scoring — Instructor adjusts score/path." The instructor override is a named checkpoint in the workflow, not an exception path.
  - **Paideia applicability:** The review layer (service 5 in the five-service architecture) must surface override events prominently: a dashboard view showing "recent overrides this week" and "nodes with highest override rate" is the instructor-facing operationalization of NIST's override-tracking recommendation.

- **paper_2:Design Patterns section** — "No silent graph mutation. Every proposed edit should be attributable, reviewable, and reversible. **Students should also be able to see when a path was altered because of model inference rather than instructor design.**"
  - **Paideia applicability:** Student-facing transparency about routing decisions requires a lightweight explanation surface distinguishing model-inferred from instructor-designed path changes. This is a distinct accountability surface from the instructor-facing override log; both are required.

---

### L4.9 — Contestability

- **paper_2:Recommended schema — Edge** — `counterexamples` and `provenance` are required edge fields. "Makes prerequisite claims contestable and reviewable; supports low-confidence flagging and assessment alignment."
  - **Paideia applicability:** `counterexamples` is a load-bearing contestability field. Every hard-prerequisite edge must require at least one `counterexample` entry (a pedagogical route that succeeded WITHOUT this prerequisite) or an explicit `no_known_counterexamples` attestation. An empty `counterexamples` field on a hard-prerequisite edge is a contestability gap, not evidence of the edge's strength.

- **paper_2:Executive Summary** — "For humanities courses, the best use of LLM+PDG is not to automate curricular authority away from instructors. It is to make expert disciplinary structure more visible, **more contestable**, and more adaptable."
  - **Paideia applicability:** Contestability is a primary design goal, not a compliance checkbox. The instructor interface must make it easy to challenge an edge — not just technically possible in the schema but surfaced as an action ("Challenge this prerequisite"). This is a UX requirement with ADR-level implications for Phase 7 product design.

- **paper_2:Risks, Governance, and Equity section** — "Every proposed edit should be attributable, reviewable, and reversible." Reversibility is the operational form of contestability after the fact.
  - **Paideia applicability:** Edge version history (L1.14) is the reversibility mechanism. Each graph edit must produce a new version record, not overwrite the prior. Rollback to any prior version must be a named, tested operation. Same pattern Paideia already uses for ADR versioning; extend to graph structure.

- **paper_1:Limitations section** — "The mitigation is straightforward: encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict."
  - **Paideia applicability:** "Revise them when learners succeed through routes the graph did not predict" is an evidence-driven contestation mechanism. The analytics layer must detect "unexpected success paths" — learners who reached mastery without completing a required prerequisite — and flag these as graph-contestation signals, not just routing anomalies.

- **paper_1:Evaluation metrics table** — "Graph validity — Which predicted bottlenecks occurred; which 'hard' edges proved unnecessary; where alternative paths worked."
  - **Paideia applicability:** Graph validity evaluation (L5.9 in Lens 5) is the periodic contestation audit for the graph as a whole. It must be a named artifact in the health-check cadence, not just an aspiration.

---

### L4.10 — Opaque automation of curriculum authority

- **paper_2:Risks, Governance, and Equity section** — "The Department of Education's AI report emphasizes that educational AI should be inspectable, explainable, and overridable, with humans in the loop and **the most affected stakeholders involved in development**."
  - **Paideia applicability:** "Most affected stakeholders" includes students, who must have structured input into graph authoring, not just receive its outputs. A new operations procedure for Phase 7+ should name a "stakeholder review" step in graph authoring — student-authored concept maps reviewed against instructor-authored PDG to surface mismatch. This is not just a student-satisfaction step; it is a governance requirement.

- **paper_2:Risks, Governance, and Equity section** — "Students should also be able to see when a path was altered because of model inference rather than instructor design."
  - **Paideia applicability:** Every adaptive routing decision surfaced to a student must carry one of three attribution labels: `instructor_designed`, `model_inferred_pending_review`, `model_inferred_approved`. A student routed to a remediation node by model inference has a right to know that and to contest it. Both an equity and a governance requirement.

- **paper_2:Executive Summary** — "Graph updates gated by human review." Stated as a non-negotiable design principle in the executive summary.
  - **Paideia applicability:** The no-silent-mutation rule (L3.9) is the engine-side version. At the product level it means the graph is never automatically updated from LLM trace analysis without an instructor-approved gate. State this as an explicit hard constraint in the product ADR for LLM+PDG integration.

- **paper_2:Design Patterns section** — "The instructor-authored core graph with LLM augmentation at the edges... the LLM then generates primers, examples, misconceptions, formative questions, and candidate refinements, but it **never silently rewrites the graph**."
  - **Paideia applicability:** Any Paideia product design that allows LLM outputs to flow directly into the PDG without a human-review gate violates this principle. State as a hard constraint in the product ADR.

- **paper_2:Workflow table — Automated prerequisite inference from traces** — "No graph update occurs without expert sign-off and **stored rationale**."
  - **Paideia applicability:** Expert sign-off plus stored rationale is the minimum governance bar for trace-inferred graph edits. The stored rationale requirement means approval is not just a click but a documented justification — connecting L4.10 to L4.9 (contestability requires that the rationale for past decisions is recoverable).

---

### L4.11 — Assessment distortion

- **paper_2:Risks, Governance, and Equity section** — "LLM scoring can look plausible while smoothing extremes, overscoring, or shifting criteria subtly." Evidence: 70% of ChatGPT gradings fell within 10% of teacher scores, "yet the system still tended to overscore slightly and compressed extremes."
  - **Paideia applicability:** Paideia's scoring architecture must implement: (1) score calibration against instructor grades on a held-out sample at each deployment, (2) explicit monitoring for score compression (variance of AI scores vs instructor scores), (3) consequential decisions (grades affecting progression or certification) routed to human review by default.

- **paper_2:Risks, Governance, and Equity section** — "The mitigation is to reserve consequential grading for human judgment or moderated hybrid workflows, to validate AI scoring against instructor rubrics and subgroup performance, and to present the AI as a **critic or coach**, not as the final judge."
  - **Paideia applicability:** "Critic or coach, not final judge" must be embedded in the student-facing explainer prompt template and in all UX copy presented with AI-generated assessment feedback. This framing is a governance commitment, not just a UX choice.

- **paper_2:Evidence Base section** — "Prompt composition and order changed feedback quality and scoring behavior." Different prompt formulations of the same rubric produced different scoring outcomes.
  - **Paideia applicability:** Scoring prompt templates must be versioned and frozen. A prompt change without re-calibration is a silent assessment-distortion event. New operations procedure: any change to a scoring prompt template triggers a re-calibration check against a held-out instructor-scored sample before the new template is deployed.

- **paper_2:Evidence Base section** — "LLM grading studies remain mixed." No study cited shows LLM grading reliably matching human judgment in humanities specifically; all positive evidence is from math or structured domains.
  - **Paideia applicability:** Humanities-specific LLM scoring calibration cannot be assumed from cross-domain evidence. Treat humanities LLM scoring as unvalidated until Paideia-specific calibration data exists. Phase 7 research task, not a deployment assumption.

- **paper_2:Risks, Governance, and Equity section** — "In humanities, the concern is magnified because many learning goals involve argument quality, interpretive judgment, nuance, and evidential reasoning rather than closed-form correctness."
  - **Paideia applicability:** LLM's known weaknesses (score compression, overscoring) are worst precisely where humanities assessment is most important (nuanced argument, interpretive range). Human-in-the-loop for assessment is a Phase 7 hard constraint, not a future luxury.

---

### L4.12 — Pluralism in humanities dependencies

- **paper_2:Open questions** — "A second open question is how to model **legitimate pluralism** in humanities dependencies. Some thresholds are real, but many routes into a topic are defensible. The research challenge is to distinguish genuine bottlenecks from merely traditional sequences."
  - **Paideia applicability:** Named as an open empirical problem, not a solved design challenge. The graph schema's `necessity_level` field (`required` / `recommended` / `historical_contextual_only`) is the structural acknowledgment that prerequisite claims are empirically contestable. Any edge claiming `required` status must carry a stronger evidence burden than any other claim in the graph.

- **paper_2:Open questions** — "Threshold-concept and Decoding approaches can help, but they do not by themselves solve disagreements among schools of interpretation."
  - **Paideia applicability:** When multiple schools of interpretation disagree about what is a prerequisite, the graph must represent the disagreement explicitly — not resolve it by fiat. The `disagreement_flag` field in the confidence model (L1.4) is the mechanism. A `disagreement_flag: true` edge routes to human adjudication before being classified as `required`.

- **paper_1:Limitations section** — "Spiro's work on ill-structured domains is the clearest warning here: tidy representations can create durable misconceptions when complexity, context, and multiple representations are exactly what advanced learning requires."
  - **Paideia applicability:** Spiro's warning applies directly to humanities. A "tidy" Paideia graph topology — few alternative routes, mostly hard prerequisites, high confidence throughout — is a red flag for pluralism suppression. New graph-health metric: ratio of soft-or-optional edges to hard-required edges. A humanities graph with fewer than 30% non-required edges warrants review.

- **paper_1:Case studies section** — All five case studies conclude that the historically canonical "required" sequence is WEAKER than assumed, and that alternative entry routes exist. This is a consistent cross-case empirical pattern: experts systematically overestimate how many prerequisites are genuinely required.
  - **Paideia applicability:** Default confidence level for newly authored prerequisite edges in a humanities PDG should be `low` until validated with student data — not `medium` or `high`. The cross-case evidence is that expert judgment overstates necessity.

- **paper_2:Risks, Governance, and Equity section** — "The mitigation is not to abandon structuring, but to make graph structure visibly provisional where appropriate: store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."
  - **Paideia applicability:** "Multiple legitimate entry routes" is not just a design aspiration — it is the anti-pathologizing mechanism (L4.5) and the canon-bias mitigation (L4.1) expressed at the graph topology level. A new graph-authoring requirement: every threshold-concept node must have at least two edges from different entry routes (case-based, conceptual, methodological, historical) before it is classified as deployment-ready.

---

### L4.13 — Connection to existing Paideia anti-bias mechanism

> The existing Paideia mechanism (per `feedback_anti_bias_implementation_discipline.md` and `feedback_audit_llm_inputs_for_bias.md`): strip source-identity / authority-cue tokens from LLM inputs at the serialization boundary, using structural patterns rather than enumerated tokens. The mechanism's own corpus uses synthetic test data and generic class names so the anti-bias discipline holds in its own implementation.

#### What the existing mechanism covers

The existing mechanism addresses **LLM input bias**: when data flows into an LLM context window, source-identity fields (author name, institution, cultural marker) are stripped so the LLM cannot give disproportionate weight to prestigious or familiar sources. This is a serialization-boundary intervention — it operates when data enters the LLM's context, not at graph authoring time.

#### AUGMENTS the existing mechanism (new attack surfaces the papers identify)

- **Canon bias in graph structure.** Even if source-identity is stripped at the LLM input boundary, the graph itself can encode canonical authority bias in its topology: European philosophical traditions appear as required prerequisites, non-canonical routes are absent or demoted to optional. The LLM may receive an anonymized node label, but if that node is always a prerequisite and never an alternative, the bias is structural, not informational. The papers identify a bias vector the current mechanism does not cover: the graph topology, before any LLM interaction occurs. Paideia needs a companion mechanism — a graph-structure bias review at authoring time, not at serialization time.

- **Multilingual output quality disparity.** Stripping source-identity prevents authority-cue bias in LLM inputs; it does not prevent LLM output quality from varying by target language. These are independent dimensions. The papers AUGMENT the existing mechanism by surfacing output-quality-by-language as an uncovered bias surface.

- **Scoring-output bias.** The existing mechanism is input-boundary-only. Papers' findings on LLM scoring calibration (score compression, overscoring, criteria shift) and over-pathologizing of interpretive styles are all output-side bias concerns. A parallel output-side mechanism is needed: scoring calibration audits, multilingual output quality sampling, rubric review for pathologizing risk.

#### REINFORCES the existing mechanism (same philosophy, different layer)

- **Structural patterns not enumerated tokens.** The existing mechanism uses structural patterns rather than named tokens to strip bias. Paper 1's recommendation for `tradition_labels` on nodes and Paper 2's `counterexamples` on edges are structural mechanisms for making bias visible and contestable — they do not enumerate "biased" items but create structural affordances for bias detection. Same design philosophy as the existing mechanism, applied at the graph layer.

- **Hold discipline in the mechanism's own corpus.** The existing mechanism requires synthetic test data and generic class names in its own corpus. Paper 2's prompt template ("Avoid: introducing unapproved terminology") and the node schema's `approved_examples` field encode the same discipline: the mechanism's own content must not exemplify the bias it is mitigating. REINFORCES the posture.

- **Audit for bias-contaminating fields.** The existing mechanism requires auditing each field for source-identity / authority cues. Paper 2's `canonical_sources` node field is a candidate for this audit: if populated with prestige-affiliated sources, it may carry authority-cue bias into LLM context via the prompt. The existing field-level audit practice applies here.

#### CONFLICTS with the existing mechanism (tension requiring resolution)

- **Named tradition labels vs. stripping identity cues.** The papers recommend explicitly attaching `tradition_labels` to nodes and edges so that alternative pathways can be identified and canonical traditions visibly marked. The existing mechanism's philosophy is to strip identity cues rather than name them. These are in tension: the graph-structure bias problem may require naming traditions (so alternatives can be offered), while the LLM input bias problem requires stripping names (so the LLM is not swayed by prestige). Resolution: `tradition_label` should exist in the graph database for human-facing contestation and audit, but be stripped or genericized at the LLM serialization boundary — the same boundary the existing mechanism already operates on. The two mechanisms can co-exist if the serialization layer strips tradition labels from LLM context while preserving them in the database.

#### GAPS revealed by the papers (not covered by existing or extended mechanism)

- **Graph topology is not in scope.** The existing mechanism has no coverage of bias in the graph's structural topology — which nodes appear as prerequisites, how many alternative routes exist, how many traditions are represented in the prerequisite set. This is the largest gap. A graph where all required prerequisites trace to European continental philosophy with no alternative routes is not addressed by stripping source-identity from LLM inputs.

- **LLM output bias is not in scope.** The existing mechanism is input-boundary only. Scoring calibration bias, multilingual output quality disparity, and over-pathologizing are all output-side surfaces requiring a parallel output audit mechanism.

- **Subgroup-differential routing is not in scope.** If the adaptive system routes certain learner subgroups disproportionately onto extended remediation paths, that is a runtime-behavior bias that neither the input mechanism nor the graph-authoring mechanism catches. It requires an analytics-layer monitor (L4.4) that is currently absent from Paideia's architecture.

---

## Cross-cutting observations

### Pattern 1 — A single governance substrate serves multiple sub-concerns

Provenance-per-edge (L1.5), confidence model (L1.4), counterexamples (L1.7), and version history (L1.14) are cited across L4.1, L4.2, L4.9, L4.10, and L4.13 as the shared substrate for contestability, override logging, canon-bias visibility, and expert-blind-spot mitigation. These four schema elements are not independent features — they form a single governance layer on the graph. Paideia should implement them as a unit (one ADR, one schema migration) rather than incrementally, because each element is only as useful as the others: provenance without counterexamples is unchallenged, counterexamples without version history lose their audit trail, confidence without provenance is ungrounded.

### Pattern 2 — Two distinct bias surfaces require two distinct interventions

The papers consistently distinguish two attack surfaces:

1. **Graph-structure bias** (before LLM interaction): canon-encoding in topology, false prerequisites hardening tradition, absence of alternative routes. Mitigation: authoring-time audit, tradition labels, alternative-route requirements, confidence defaults.

2. **LLM-mediated bias** (during and after LLM interaction): output-quality disparity by language, over-pathologizing of interpretive styles, scoring calibration drift. Mitigation: output-side audit, multilingual quality sampling, rubric review, scoring calibration.

The existing Paideia mechanism operates on surface 2 (input-to-LLM), but only on a subset of it (source-identity stripping). Surface 1 is entirely unaddressed. Both surfaces need distinct mechanisms; treating one as a substitute for the other leaves the other wholly uncovered.

### Pattern 3 — Governance machinery is inert without a named human review cadence

Sub-concerns L4.4, L4.7, L4.8, and L4.11 all converge on the same operational requirement: the governance machinery the papers recommend (override logs, transparency reports, subgroup audits, scoring calibration) produces value only if a human reviews outputs on a regular cadence. Paideia's operations procedure for any LLM+PDG deployment must name a specific cadence (weekly instructor review, quarterly equity audit, annual graph-validity review) and a specific responsible actor for each. Without named cadence and named actor, the machinery is governance theater, not governance.

---

## Coverage report

| Sub-concern | Findings | Status |
|---|---|---|
| L4.1 — Cultural / canon bias | 6 | Covered — richest sub-concern; explicit in both papers across risks, case study, and schema sections |
| L4.2 — Expert blind spot | 4 | Covered — Paper 1 primary; Paper 2 reinforces via provenance apparatus |
| L4.3 — Multilingual fairness | 4 | Covered — Paper 2 risks section primary; Paper 1 schema provides the `multilingual cohort` audience tag |
| L4.4 — Subgroup-analysis discipline | 5 | Covered — evaluation metrics table (Paper 1), implementation section (Paper 2) |
| L4.5 — Anti-pathologizing-interpretive-styles | 4 | Covered — Paper 2 risks section + prompt template + Paper 1 multiple-routes principle |
| L4.6 — FERPA/privacy/consent | 4 | Covered — Paper 2 risks section exclusively; three concrete schema requirements identified |
| L4.7 — NIST GenAI profile alignment | 4 | Covered — Paper 2 risks section; 32% Pardos & Bhandari finding is the key empirical anchor |
| L4.8 — Override logging | 4 | Covered — Paper 2 risks section and workflow tables |
| L4.9 — Contestability | 5 | Covered — schema fields, executive summary, evaluation metrics |
| L4.10 — Opaque automation of curriculum authority | 5 | Covered — executive summary through workflow table; DoE report cited |
| L4.11 — Assessment distortion | 5 | Covered — evidence base and risks section; humanities-specific gap identified |
| L4.12 — Pluralism in humanities dependencies | 5 | Covered — open questions and five case studies provide consistent cross-case evidence |
| L4.13 — Connection to existing Paideia mechanism | Synthesis | Covered — 2 AUGMENTS, 3 REINFORCES, 1 CONFLICT (with resolution), 3 GAPS |

**All 13 sub-concerns have findings. No justified absences.**
