# Lens sweep — Evaluation / Verification

> **Filled by Phase C agent — S-0170.** Re-reads BOTH papers end-to-end through the single lens of measurement discipline (learner outcomes AND graph quality). Lens covers L5.1–L5.10.
>
> **Coverage rule:** every sub-concern below must have findings OR an explicit `_No findings because…_` justification.
>
> **Distinction in force throughout:** graph-validity evaluation (does the graph predict real learning bottlenecks?) vs learner-outcome evaluation (do learners learn better with PDG/LLM?). These fund different Paideia surfaces: graph-validity extends existing SQA discipline; learner-outcome evaluation is Phase 7+ new infrastructure.

## Sources

- Paper 1: `/Users/shanekidd/Documents/Claude_Files/temp/Assessing the Utility of Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`
- Paper 2: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`

---

## Findings by sub-concern

### L5.1 — Learner-outcome measurement (threshold-concept tasks, comparative essays, transfer prompts, delayed retention)

- **paper_1:L144-146** — The evaluation table explicitly enumerates learner-outcome metrics: "Performance on threshold-concept tasks, comparative essays, transfer prompts, delayed retention, rubric dimensions tied to graph nodes." Strong designs named are "Randomized or cluster-randomized comparisons of PDG-informed vs conventional sequencing; pre/post designs with delayed posttest."
  - **Paideia applicability:** Phase 7+ evaluation infrastructure should adopt this five-metric bundle (threshold tasks / comparative essays / transfer / delayed retention / node-aligned rubric dimensions) as the canonical learner-outcome measurement contract. "Rubric dimensions tied to graph nodes" is the critical link — it requires the graph's node schema to include `assessment_items` and `mastery_evidence` fields *before* learner deployment, so the evaluation instrument is co-designed with the graph. Paideia can begin this alignment work now in the SQA phase by tagging nodes with candidate rubric dimensions even before learners exist.

- **paper_1:L152-154** — On realistic design for humanities: "One cohort can receive a traditional historically organized unit; another can receive a PDG-informed unit that explicitly distinguishes hard prerequisites, soft bridges, and optional background. Outcomes should include not only final grades but also threshold-concept tasks, transfer to unfamiliar texts, quality of peer discussion, and delayed retention."
  - **Paideia applicability:** The multi-outcome bundle rules out final-grade-only evaluation. If Paideia reaches Phase 7+ deployment, the evaluation plan must instrument at least four outcome dimensions — not just grade or quiz-score proxies. Highlights that "transfer to unfamiliar texts" and "quality of peer discussion" are distinct from quiz outcomes, requiring separate assessment rubrics.

- **paper_2:L204** — "Outcomes should include immediate learning, delayed retention, quality of written interpretation, reduction in bottleneck errors, appropriateness of cited evidence, time-on-task, help-seeking behavior, and student understanding of why a path was recommended."
  - **Paideia applicability:** Paper 2 extends Paper 1's list with "student understanding of why a path was recommended" and "help-seeking behavior" — both require logging infrastructure (LMS navigation logs, help-request events). "Appropriateness of cited evidence" is a humanities-specific rubric dimension that has no analog in STEM tutoring systems. Paideia's Phase 7+ evaluation plan should treat this as a discipline-specific addition, not borrowable from existing LLM-tutoring benchmarks.

- **paper_2:L50** — Three empirical LLM-tutoring studies cited as outcome benchmarks: ChatGPT math tutoring +0.23 SD vs control (Kestin et al.), Tutor CoPilot +4 pct points mastery overall / +9 pct for lower-rated tutors. These are comparator effect sizes for calibration, not direct humanities evidence.
  - **Paideia applicability:** When Paideia eventually designs a power calculation for a learner-outcome study, these effect sizes (0.23 SD, 4–9 pct points) are the available calibration range from LLM tutoring. Humanities effects may be smaller given the open-ended nature of outcomes. Plan accordingly; don't borrow STEM power assumptions.

---

### L5.2 — Graph predictive validity (which predicted bottlenecks occurred, which "hard" edges proved unnecessary, where alternative paths worked)

- **paper_1:L149** — Evaluation table row for graph validity: "Which predicted bottlenecks occurred; which 'hard' edges proved unnecessary; where alternative paths worked." Recommended design: "Iterative design-based research; expert review plus learner-performance validation."
  - **Paideia applicability:** This is the most directly applicable sub-concern for current Paideia work, because graph-validity evaluation does NOT require deployed learners. The two-part verification method — expert review (available now) + learner-performance validation (Phase 7+) — means Paideia can begin graph predictive validity work in the SQA phase. Specifically: (a) expert review of which edges are marked "hard prerequisite" vs "soft bridge" and whether that classification is defensible; (b) post-deployment check of whether student trace data confirms or falsifies those classifications. Current SQA census (shards 01-08) is implicitly doing part (a) but is not yet framed as a "predictive validity" instrument. A future SQA iteration should explicitly track "predicted difficulty by edge-type" so that the learner-performance check has a prior to test against.

- **paper_1:L154** — "If possible, the graph itself should be scored for predictive validity: which edges actually corresponded to observed learning bottlenecks, and which turned out to be unnecessary or cohort-specific."
  - **Paideia applicability:** "Cohort-specific" is load-bearing — it means a hard edge validated for one cohort may be unnecessary for another (expert vs novice, major vs non-major). The current graph has no `audience_tag` per edge, which would be required to track cohort-specific validity. This is a schema gap (L1.11) with direct evaluation consequences.

- **paper_2:L74** — On trace-informed graph revision: "If many students repeatedly fail on a supposedly downstream node but perform well on its represented prerequisites, the system can flag either a missing prerequisite, an over-strong edge, or a bad assessment item." This is the operational definition of predictive-validity feedback loop.
  - **Paideia applicability:** This "downstream failure + upstream success" pattern is the empirical signal that falsifies a prerequisite claim. Paideia's Phase 7+ analytics layer should instrument this signal explicitly — it is not captured by pass/fail rates on individual nodes alone. Requires the graph to have stable node identifiers that persist across cohorts and graph revisions (versioning requirement per L1.14).

- **paper_2:L204** — "Graph validity itself should be evaluated: expert agreement on edge labels, revision rates after review, disagreement concentrations by topic, and whether trace-inferred edits improve or worsen downstream learning."
  - **Paideia applicability:** Four distinct graph-validity metrics named: (1) expert agreement on edge labels — operationalizable now via SQA; (2) revision rates after review — requires version-tracked graph with change log; (3) disagreement concentrations by topic — requires SQA to cluster findings by subject area, not just report aggregate defect rates; (4) downstream-learning improvement from trace-inferred edits — Phase 7+ only. Metrics 1–3 are accessible in the current SQA discipline; metric 4 requires learners.

---

### L5.3 — Comparative experimental designs (PDG-only vs LLM-only vs PDG+LLM)

- **paper_2:L25-33** — Comparative frame table explicitly enumerates three conditions: PDG-only, LLM-only, PDG+LLM, across six dimensions: accuracy about instructional structure, adaptivity during tutoring, scalability, transparency, bias/cultural risk, instructor workload. This is not a proposed experiment but a structured design rationale — it argues why PDG+LLM dominates on most dimensions when governance conditions are met.
  - **Paideia applicability:** This table is the strongest argument for the PDG+LLM design choice. It also implies that any evaluation study comparing conditions should measure all six dimensions, not just learning outcomes. For Paideia, "transparency and inspectability" and "bias/cultural risk" are measurable through graph audit and override-log analysis even before learner deployment.

- **paper_2:L204** — "The right research designs are randomized or quasi-experimental studies that compare PDG-only, LLM-only, and PDG+LLM conditions on common tasks. For upper-division humanities courses, a good design is a cluster-randomized or cross-over trial at the section or unit level, with delayed posttests and transfer tasks."
  - **Paideia applicability:** Phase 7+ experimental design specification: cluster-randomized (or cross-over) at section/unit level; three arms; delayed posttest plus transfer tasks mandatory. The "cross-over trial at the section or unit level" formulation is practically significant — it means a single course can contribute to all three conditions across units, reducing the enrollment required. Relevant for Paideia's likely small-cohort early deployments.

- **paper_1:L152-154** — Quasi-experimental framing: "One cohort can receive a traditional historically organized unit; another can receive a PDG-informed unit." This is the realistic humanities variant — not a lab experiment, but a course-level quasi-experiment with a contemporaneous comparison group.
  - **Paideia applicability:** Paper 1's quasi-experimental framing is more actionable for early Paideia deployment than Paper 2's RCT framing. A single course with multiple sections or a sequential-cohort design (this year vs last year) is the most feasible first evaluation design.

---

### L5.4 — Heterogeneity-of-treatment-effects analysis (subgroup gains)

- **paper_1:L148** — Evaluation table row for equity effects: "Differential gains by prior preparation, verbal ability, language background, major/non-major status." Recommended designs: "Heterogeneity-of-treatment analysis; matched-cohort quasi-experiments."
  - **Paideia applicability:** Phase 7+ evaluation must collect subgroup covariates at enrollment (prior preparation, verbal ability proxy, language background, major/non-major). These must be collected with appropriate consent as part of the IRB protocol — not retrofitted from existing records. The evaluation plan should pre-register which subgroup contrasts are primary (confirmatory) vs exploratory, to avoid multiple-comparison inflation in a small-N humanities study.

- **paper_2:L206** — Subgroup evaluation explicitly named in implementation guidance: "Do multilingual students receive poorer feedback or less accurate scoring? Does the system over-pathologize certain interpretive styles as misconceptions? Are some traditions overrepresented as 'required prerequisites' rather than 'one valid route'?" The governance requirement: "publish periodic transparency reports on graph edits, override rates, subgroup discrepancies, and content-provenance coverage."
  - **Paideia applicability:** Three distinct fairness-oriented subgroup questions beyond simple differential-gains: (1) scoring quality by language background, (2) misconception-pathologizing by interpretive style/tradition, (3) canon overrepresentation in prerequisite classification. Questions 2 and 3 are graph-level evaluation questions — answerable before learner deployment by auditing graph structure. The transparency-report requirement is the governance surface; Paideia's SQA documentation (shards census) is the embryonic form of this.

- **paper_2:L50** — Tutor CoPilot finding: "+9 points for lower-rated tutors" is an HTE signal — the benefit of AI tutoring support is larger for less-experienced tutors (a moderator, not just an average). This is cited as direct evidence that heterogeneity-of-effects analyses matter in AI-tutoring contexts.
  - **Paideia applicability:** The moderator-of-tutor-quality finding suggests that Paideia's evaluation should not only track student subgroup effects but also instructor/facilitator subgroup effects — whether less-experienced Paideia instructors benefit more from the graph scaffolding. This moderator is rarely tracked in small humanities deployments.

---

### L5.5 — Process-quality measurement (discussion moves, causal explanation, navigation patterns)

- **paper_1:L147** — Evaluation table row for process quality: "Discussion moves, causal explanation, argumentation, use of disciplinary vocabulary, navigation patterns in LMS." Methods named: "Discourse analysis, trace-data analysis, think-alouds, screen capture, annotation logs."
  - **Paideia applicability:** Process-quality measurement requires fundamentally different instrumentation from outcome measurement: discourse analysis of transcripts, LMS navigation trace extraction, annotation logs. These cannot be retrofitted from grade data. Paideia's Phase 7+ evaluation plan should decide upfront whether to invest in process-quality infrastructure (which is expensive) or to focus on outcome metrics (cheaper but misses the "why"). The papers' weight on process data suggests this is scientifically important for humanities — discourse analysis and causal explanation are closer to the actual learning goals than test scores.

- **paper_1:L51** — Lucero et al. history study cited as strongest humanities-adjacent experiment: "Students in the mapping condition engaged significantly more in causal explanation and argumentation, used more historical and metahistorical concepts, and showed more convergence and integration of peer knowledge contributions." This was measured via discourse analysis of discussion transcripts.
  - **Paideia applicability:** The Lucero et al. measurement approach (discourse-coding transcripts for causal explanation, argumentation, disciplinary vocabulary use, peer-knowledge convergence) is the most directly transferable process-quality method for Paideia humanities content. This is a qualitative coding methodology, not an automated metric — it requires trained coders or an LLM-assisted coding pipeline with human validation.

- **paper_2:L72** — Navigation patterns as process signal: "the practical implication is that branching should initially be conservative and coarse-grained, with explicit confidence intervals and human review for persistent anomalies." This implies navigation anomaly detection is itself a process-quality signal.
  - **Paideia applicability:** Navigation patterns in LMS (node visit order, time on node, help-request frequency, back-tracking patterns) are automatically logged if the LMS is instrumented. Paideia's Phase 7+ analytics layer should capture navigation events at the node level (not just page views) so that anomalous routing can be detected and investigated. This requires stable node-level URLs or identifiers in the learner-facing interface, tied to graph node IDs.

---

### L5.6 — Design-based research as realistic high-quality humanities design

- **paper_1:L149** — Evaluation table explicitly names "Iterative design-based research" as the recommended design for graph validity evaluation. The realistic design framing appears at L152–154: "For humanities contexts, the most realistic high-quality design is often design-based research or a quasi-experimental course comparison, not a perfectly controlled lab experiment."
  - **Paideia applicability:** Design-based research (DBR) is the methodological commitment Paideia should adopt for graph development and validation. DBR is iterative — design, implement, analyze, revise — and it treats the graph as a revisable model, not a fixed intervention. This aligns with the SQA census approach (iterative quality audit across shards) but needs to be formally acknowledged as the evaluation methodology so that findings from each cohort are systematically fed back into graph revision.

- **paper_1:L112** — Construction workflow step 6: "Revise the graph with empirical evidence from student performance, concept-map artifacts, or learning analytics. Knowledge-space research is especially useful here because it formalizes a cycle of expert elicitation followed by empirical refinement, rather than treating expert judgment as final."
  - **Paideia applicability:** "Expert elicitation followed by empirical refinement" is the DBR cycle operationalized for PDGs. Paideia's current SQA census is expert-elicitation mode. The empirical-refinement phase requires learner data. The phase transition (census → empirical refinement) is a future milestone that should be named in the ROADMAP.

- **paper_1:L130** — Instructor workflow framing: "Draft the graph before the course; expose a student-friendly subset during the course; use formative assessments and discussion transcripts to see where the graph over- or under-predicts difficulty; then revise."
  - **Paideia applicability:** This is the DBR operational cycle at the course-run level. "Over- or under-predicts difficulty" is the empirical signal. The cycle requires the graph to have a revision mechanism (version history per L1.14) so that revisions are tracked and their effects on subsequent cohorts can be evaluated.

---

### L5.7 — Iterative cohort refinement (knowledge-space theory pattern)

- **paper_1:L59** — Knowledge-space theory cited as the formal mechanism for cohort-iterative refinement: "Knowledge-space theory shows that expert-built state spaces can be refined with empirical data; ALEKS demonstrates large-scale practical use of such models; and educational data mining research shows that prerequisite relations can sometimes be inferred from learner data and can improve predictive student models."
  - **Paideia applicability:** Knowledge-space theory's formal architecture — expert-elicited state space + empirical refinement from learner traces — is the theoretical foundation for Paideia's long-term graph development lifecycle. "ALEKS demonstrates large-scale practical use" is the proof-of-concept at scale. For Paideia, the most relevant implication is that graph revisions should be treated as scientific hypotheses: each revision predicts that the modified graph will produce better downstream learning, and that prediction should be tested in the next cohort. This requires a cohort-tracking data model.

- **paper_1:L112** — Construction workflow step 6 (same citation as L5.6 above): "Revise the graph with empirical evidence from student performance... Knowledge-space research is especially useful here because it formalizes a cycle of expert elicitation followed by empirical refinement, rather than treating expert judgment as final."
  - **Paideia applicability:** The knowledge-space cycle is the evaluation methodology for graph refinement specifically — distinct from DBR which covers the broader design. Paideia's graph schema should capture the cohort and revision version for every node and edge (per L1.14) so that the refinement cycle can be tracked and analyzed across multiple deployments.

- **paper_2:L56** — "E-PRISM retrieved promising prerequisite structures from learner traces; dialogue knowledge tracing with LLMs outperformed prior methods on two tutoring dialogue datasets; and LLM-assisted graph completion for curriculum/domain modeling showed good expert acceptance in higher education."
  - **Paideia applicability:** LLM-assisted graph completion via dialogue knowledge tracing is the semi-automated variant of the knowledge-space refinement cycle. When Paideia has learner traces, this method (LLM proposes edge modifications based on trace patterns, instructor approves) is the operationally realistic refinement path. The "good expert acceptance" finding is encouraging but domain-specific (STEM context). Expect humanities acceptance to require stronger provenance and transparency requirements.

- **paper_2:L72** — "Branching should initially be conservative and coarse-grained, with explicit confidence intervals and human review for persistent anomalies."
  - **Paideia applicability:** "Conservative and coarse-grained" branching in early cohorts is a DBR principle — start simple to get clean signal, add nuance as refinement proceeds. Paideia's Phase 7+ deployment should explicitly plan a multi-cohort refinement arc rather than deploying the full graph immediately.

---

### L5.8 — Anomalous routing detection

- **paper_2:L72** — Adaptive branching pattern: "For humanities, the practical implication is that branching should initially be conservative and coarse-grained, with explicit confidence intervals and human review for persistent anomalies." The sample workflow table (L90–95) includes: "Review anomalous paths and override routing decisions" as an explicit instructor role in the adaptive-branching workflow.
  - **Paideia applicability:** Anomalous routing detection requires the analytics layer (service 4 in Paper 2's five-service architecture) to surface divergent path patterns. "Anomalous" means: student routed to a prerequisite node after already satisfying it; student bypassing a required node and succeeding anyway (falsifying the hard-prerequisite claim); student cycling repeatedly on the same node without progress. These are different anomaly types with different interventions. Paideia's Phase 7+ analytics should define the anomaly taxonomy before deployment.

- **paper_2:L94** — Adaptive branching lesson workflow row: "Review anomalous paths and override routing decisions" as a human checkpoint. This is the anomaly-detection surface named explicitly in the workflow.
  - **Paideia applicability:** The review layer (service 5) is the anomaly-surface interface. For Paideia, this means instructors need a dashboard or periodic report showing students whose paths diverge from graph predictions. The dashboard design is a Phase 7+ UX requirement that should be specified before the analytics layer is built, not after.

- **paper_2:L74** — Trace-informed graph revision as anomaly processing: "If many students repeatedly fail on a supposedly downstream node but perform well on its represented prerequisites, the system can flag either a missing prerequisite, an over-strong edge, or a bad assessment item."
  - **Paideia applicability:** The three-way disambiguation (missing prerequisite vs over-strong edge vs bad assessment item) requires separate investigation procedures. A bad assessment item is a measurement failure, not a graph failure — this distinction must be built into the anomaly-response workflow. Mixing them inflates graph revision rates artificially.

---

### L5.9 — Validity criteria for the graph itself (expert agreement, revision rates, disagreement concentrations, downstream improvement from trace-inferred edits)

- **paper_2:L204** — Explicit enumeration of four graph-validity metrics: "expert agreement on edge labels, revision rates after review, disagreement concentrations by topic, and whether trace-inferred edits improve or worsen downstream learning."
  - **Paideia applicability:** This is the clearest direct specification of what Paideia's SQA census discipline should evolve into. Currently the SQA census measures C1 (fresh defects), C2 (stale citations), C3 (jargon-gated), C4 (rigor scores) — these are internal quality dimensions, not predictive validity dimensions. The four Paper 2 metrics extend the validity framework: (1) inter-rater agreement on edge label classification (hard/soft/bridge) — add to SQA protocol; (2) revision rates post-expert-review — currently tracked implicitly but not reported as a validity metric; (3) disagreement concentrations by topic — SQA currently reports aggregate defect rates, not cluster by subject area; (4) downstream-learning improvement — Phase 7+. Metrics 1–3 are actionable in current SQA.

- **paper_1:L25** — Validity criterion appears in the PDG vs influence-map comparison table: "Validity criterion: Better learning, transfer, reduced bottlenecks, assessment alignment" (for PDG) vs "Better historiography, source tracing, reception history" (for influence map).
  - **Paideia applicability:** This is the clearest statement of what "graph validity" means for a PDG: not internal consistency or expert agreement alone, but predictive performance against learning outcomes. The four criteria (better learning, transfer, reduced bottlenecks, assessment alignment) are the validity criteria Paideia's graph must ultimately satisfy. Assessment alignment is partially testable now (do nodes have associated assessment items?); the other three require learners.

- **paper_1:L149** — Evaluation table graph-validity row: "Iterative design-based research; expert review plus learner-performance validation" as the recommended methodology.
  - **Paideia applicability:** The two-phase methodology (expert review first, learner-performance validation second) maps cleanly onto Paideia's current position: SQA census is phase 1 (expert review), Phase 7+ deployment is phase 2 (learner-performance validation). This framing should be explicit in the ROADMAP so the two phases are treated as a connected validity study, not separate activities.

- **paper_1:L162** — Expert blind spot as a validity threat: "encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict."
  - **Paideia applicability:** "Succeed through routes the graph did not predict" is a specific validity check — it requires Paideia's learner-facing interface to log which graph path the student actually took, not just whether they passed the assessment. If a student bypasses a prerequisite node and still succeeds, that falsifies the hard-prerequisite claim for that edge. This requires path-logging infrastructure at the level of individual graph traversal decisions, not just final assessment outcomes.

- **paper_2:L82** — Confidence model in schema: "`expert_confidence`, `trace_confidence`, `llm_confidence`, `disagreement_flag`" — three independent confidence sources. The `disagreement_flag` is particularly relevant to graph validity: when expert reviewers disagree, the disagreement should be surfaced and tracked, not averaged away.
  - **Paideia applicability:** `disagreement_flag` on edges is a graph-validity instrument. Edges with `disagreement_flag` set are the edges most likely to have incorrect necessity classification (hard vs soft). Paideia's SQA should track inter-rater disagreement as a metric, not just final consensus scores. High-disagreement edges are priority candidates for the "expert review plus learner-performance validation" two-phase check.

---

### L5.10 — Student-experience validity (perceived coherence, overload, agency, usefulness of optional bridges, sense of progression)

- **paper_1:L150** — Evaluation table student-experience row: "Perceived coherence, overload, agency, usefulness of optional bridges, sense of progression." Methods named: "Interviews, focus groups, survey items tied to specific nodes/edges."
  - **Paideia applicability:** Student-experience validity is distinct from learning-outcome validity and from graph-predictive validity. It requires a qualitative or survey instrument that names specific graph elements ("the optional bridge on Kantian transcendental idealism — did this feel helpful or burdensome?"). Generic course satisfaction surveys cannot substitute. Paideia's Phase 7+ evaluation plan should design a node-linked student survey instrument, not a generic satisfaction scale.

- **paper_2:L200** — Implementation guidance: "Students do not need the entire back-end ontology. They need the current local neighborhood: the target node, its immediate prerequisites, common misconceptions, upcoming assessments, and alternative routes if they are stalled." The student-facing exposure design directly affects their perceived coherence and agency.
  - **Paideia applicability:** Student-experience validity is partly a function of the UX design (which graph elements are exposed and how), not just the graph content. "Alternative routes if they are stalled" is the agency-preserving feature — its absence produces a "stuck and nowhere to go" experience that would appear in student-experience evaluation as low agency scores. Paideia's learner-facing design should treat alternative-route visibility as a first-class feature requirement, not an optional enhancement.

- **paper_2:L202** — Instructor during-term review: "examine whether branches are disproportionately burdening specific groups or language backgrounds." This is a student-experience equity check, overlapping with L5.4 but framed from the experience side rather than the outcome side.
  - **Paideia applicability:** Cognitive burden disparities by subgroup are a student-experience validity concern — some students perceive the graph as overwhelming not because they lack ability but because the prerequisite chain is longer for them (more assumed background to remediate). Paideia's student-experience evaluation should include a burden/overload scale disaggregated by subgroup, not just an aggregate coherence rating.

- **paper_2:L194** — Opaque-automation risk: "Students should also be able to see when a path was altered because of model inference rather than instructor design." Transparency in path recommendation is a student-experience validity concern — students who perceive the system as a black box report lower agency.
  - **Paideia applicability:** This is an interface-transparency requirement with student-experience consequences. Paideia's learner-facing interface should distinguish instructor-designed path recommendations from algorithmically-inferred ones. Students should be able to ask "why am I here?" and receive an answer that cites either an instructor decision or a learner-trace inference. This requires the review layer to expose provenance to students (not just to instructors).

---

## Cross-cutting observations

### 1. Graph validity evaluation precedes and funds learner-outcome evaluation

Both papers treat graph-validity evaluation (L5.2, L5.9) as epistemically prior to learner-outcome evaluation (L5.1, L5.3). Paper 1's two-phase method is explicit: expert review first, learner-performance validation second. This means Paideia's current SQA census work is not merely quality control — it is phase 1 of a longitudinal validity study. To make this framing productive, SQA findings should be recorded in a format that can be compared against Phase 7+ learner data. Concretely: the SQA census should record, per edge, its predicted difficulty level (hard/soft/bridge) and any expert disagreement, so that Phase 7+ data can directly falsify or confirm those predictions. The current SQA methodology (C1/C2/C3/C4 categories) is internal quality measurement — it should be augmented with predictive validity fields.

### 2. The evaluation instrument bundle is graph-native, not assessment-generic

Both papers insist that evaluation instruments should be tied to graph nodes (Paper 1 L144: "rubric dimensions tied to graph nodes"; Paper 2 L204: "reduction in bottleneck errors" node-specifically). This means evaluation cannot be designed independently of the graph. Generic final exams or standardized tests cannot serve as validity instruments — they are too coarse to reveal whether specific edges predicted specific bottlenecks. For Paideia, this means the evaluation instrument (assessment items, rubric dimensions, navigation logs) must be co-designed with the graph schema, not designed after the graph is complete. The implication for current SQA work: when reviewing nodes, flag which nodes lack candidate assessment items, since those nodes will be blind spots in any future validity study.

### 3. Student-experience validity and process-quality measurement are under-resourced in typical evaluation designs but are highest-priority for humanities

Both papers flag that humanities learning goals are not well captured by quiz-score outcomes alone. Paper 1 cites the Lucero et al. study as the strongest humanities-adjacent evidence precisely because it measured causal explanation and argumentation via discourse analysis — not test scores. Paper 2 adds help-seeking behavior, time-on-task, and "student understanding of why a path was recommended" as additional process signals. The evaluation discipline for a humanities PDG is therefore more expensive than for a STEM tutoring system: it requires trained discourse coders, navigation-log extraction, and qualitative interview infrastructure. Paideia should treat this as a Phase 7+ infrastructure investment decision — the cost of process-quality measurement is non-trivial and should be planned explicitly, not assumed.

### 4. HTE analysis (L5.4) is both an equity obligation and a graph-validity instrument

Heterogeneity-of-treatment-effects analysis appears in both papers as an equity concern (Paper 2 L206: subgroup discrepancies in scoring quality and misconception-pathologizing) and as a graph-validity signal (Paper 1 L154: "cohort-specific" edges that are valid for one subgroup but not another). These are the same measurement, serving two different purposes. Paideia's Phase 7+ evaluation plan should not treat HTE analysis as an optional equity add-on — it is structural to the graph validity framework, because an edge that is a valid hard prerequisite for majors but not for non-majors is not correctly classified as a universally hard prerequisite. This ties directly back to the schema's `audience_tag` field (L1.11): without audience tagging on edges, HTE results cannot be fed back into graph revision.

### 5. Iterative refinement (L5.7) requires organizational infrastructure that is not part of the graph itself

The knowledge-space theory pattern — expert elicitation followed by empirical refinement — requires a multi-cohort organizational commitment that goes beyond graph engineering. Paideia must plan for: (a) a stable graph-version identifier per cohort so that analyses can distinguish "graph v1 cohort 1" from "graph v2 cohort 2"; (b) a revision-review workflow where instructor approval of trace-inferred edits is recorded with rationale (Paper 2 L95: "No graph update occurs without expert sign-off and stored rationale"); (c) a cross-cohort comparison methodology. None of these are graph schema requirements — they are process and tooling requirements. They are the operationalization of the "iterative" in "iterative design-based research."

---

## Coverage report

- Sub-concerns with ≥1 finding: **10 / 10**
- Sub-concerns with justified absence: none — all 10 have findings
- Finding counts by sub-concern:
  - L5.1: 4 findings (paper_1:L144-146, paper_1:L152-154, paper_2:L204, paper_2:L50)
  - L5.2: 4 findings (paper_1:L149, paper_1:L154, paper_2:L74, paper_2:L204)
  - L5.3: 3 findings (paper_2:L25-33, paper_2:L204, paper_1:L152-154)
  - L5.4: 3 findings (paper_1:L148, paper_2:L206, paper_2:L50)
  - L5.5: 3 findings (paper_1:L147, paper_1:L51, paper_2:L72)
  - L5.6: 3 findings (paper_1:L149, paper_1:L112, paper_1:L130)
  - L5.7: 4 findings (paper_1:L59, paper_1:L112, paper_2:L56, paper_2:L72)
  - L5.8: 3 findings (paper_2:L72, paper_2:L94, paper_2:L74)
  - L5.9: 5 findings (paper_2:L204, paper_1:L25, paper_1:L149, paper_1:L162, paper_2:L82)
  - L5.10: 4 findings (paper_1:L150, paper_2:L200, paper_2:L202, paper_2:L194)
- Cross-cutting observations: 5
- Distinction maintained (graph-validity vs learner-outcome): yes — each finding explicitly flags which surface it applies to
