# Lens sweep — LLM Integration & Architecture

> **Filled by Phase C agent.** Re-reads BOTH papers end-to-end through the single lens of LLM consumption of the graph and architectural integration.
>
> **Coverage rule:** every sub-concern below must have findings OR an explicit `_No findings because…_` justification.

## Sources

- Paper 1: `/Users/shanekidd/Documents/Claude_Files/temp/Assessing the Utility of Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`
- Paper 2: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`

## Findings by sub-concern

### L3.1 — Instructional-spine-vs-adaptive-interface architecture

- **paper_2:L6–7** — The executive summary names the division of labor directly: "the PDG should serve as the **instructional spine** and the LLM as the **adaptive interface**." Rationale: "the graph supplies what LLMs lack: explicit structure, traceable pedagogical assumptions, assessment hooks, and human-auditable prerequisites. The LLM then does what static graphs do poorly: generate explanations at multiple levels, adapt prompts and examples to students' current state, propose missing edges for expert review, score or summarize diagnostic responses, and turn graph structure into conversational tutoring."
  - **Paideia applicability:** This is the founding architectural claim for the teaching-side LLM integration layer. The Phase 7+ ADR for teaching LLM integration should commit to this partition explicitly as a load-bearing architectural invariant — the graph is the authority, the LLM is the interface. Not merely a design preference: the evidence cited (unconstrained LLMs still can't match ITS fidelity, L52) makes it a correctness argument.

- **paper_2:L17** — Restated in the scope section: "The integration matters only if the graph materially constrains or informs what the model explains, asks, scores, or proposes next." The LLM without graph constraint is explicitly out of scope.
  - **Paideia applicability:** Operationalizes the spine-vs-interface rule as a sufficiency test: if the graph is not constraining LLM outputs, the integration is not functioning correctly. Future validator checks for the teaching layer could surface this as an audit criterion.

- **paper_2:L68** — Under Design Patterns: "The safest and most pedagogically defensible pattern is the **instructor-authored core graph with LLM augmentation at the edges**. In this pattern, instructors or discipline teams define the canonical nodes, edge types, learning outcomes, and approved evidence. The LLM then generates primers, examples, misconceptions, formative questions, and candidate refinements, but it **never silently rewrites the graph**."
  - **Paideia applicability:** The "never silently rewrites" clause is the teaching-layer equivalent of Paideia's no-silent-mutation rule. Both the ADR-level machinery (L3.9) and the spine-vs-interface partition reduce to the same invariant: the LLM proposes, humans arbitrate.

- **paper_1:L130** — Paper 1 anticipates the architecture without naming it: "Draft the graph before the course; expose a student-friendly subset during the course; use formative assessments and discussion transcripts to see where the graph over- or under-predicts difficulty; then revise." The graph is treated as the stable artifact; student-facing interaction as the derivative layer.
  - **Paideia applicability:** Confirms that even in the graph-only paper the instructional spine is the graph and interaction is derivative. The LLM in Paper 2 slots into the derivative layer without changing the underlying architecture.

---

### L3.2 — Five-service architecture

- **paper_2:L198** — Named explicitly in Implementation and Evaluation: "A practical architecture has five services. The **graph store** holds PDG nodes, edges, provenance, confidence, and assessment alignment. A **content store** holds approved excerpts, lecture notes, prompts, and exemplars. The **LLM orchestration layer** handles tutoring, graph-refinement proposals, feedback generation, and rubric-linked scoring. The **analytics layer** tracks student traces and mastery evidence. The **review layer** exposes all low-confidence outputs, contested edges, and override events to instructors."
  - **Paideia applicability:** This is the direct backend architecture template for Paideia's Phase 7+ teaching system. The current Paideia backend (Postgres/Supabase) covers aspects of graph store and possibly content store; analytics layer, review layer, and LLM orchestration layer do not yet exist as teaching-layer services. Each of the five should map to a named service or schema boundary in Phase 7 planning.

- **paper_2:L198** — Tooling per service: "For the graph store, a property-graph database such as **Neo4j** is a strong fit when edges need rich attributes; **RDF tooling** such as Apache Jena is useful when interoperability and linked-data semantics matter; **NetworkX** is appropriate for prototyping analytics pipelines; and **Mermaid** is a low-friction way to embed text-defined graph visualizations into syllabi or course documentation."
  - **Paideia applicability:** The graph-store tooling choice is the most immediate decision with schema consequences — feeds directly into L3.15.

_No findings in Paper 1 for the five-service architecture by name; Paper 1 is pre-LLM-integration and mentions only lightweight planning tools (Mermaid, Graphviz, yEd, Kumu, CmapTools) appropriate for planning-only use, not a teaching-system architecture._

---

### L3.3 — Four sample workflows

- **paper_2:L90–95** — The workflow table (Section "Sample workflows with roles and checkpoints") names all four explicitly:
  1. **Instructor-authored PDG with LLM scaffolding** — instructor defines core nodes/outcomes/approved sources; LLM generates primers, examples, low-stakes questions, summaries; student studies and answers diagnostics; checkpoints are approve graph, review low-confidence outputs, spot-check scoring.
  2. **Student-authored PDG with LLM feedback** — instructor provides rubric and anchor examples; LLM diagnoses missing nodes/unsupported edges/ambiguous labels; student constructs and revises graph; instructor samples subset for validity and disciplinary nuance.
  3. **Adaptive branching lesson** — instructor sets branching policy and mastery thresholds; LLM scores diagnostic tasks, chooses next node, generates hints; student completes tasks and reflects on path; instructor reviews anomalous paths and overrides routing decisions.
  4. **Automated prerequisite inference from traces** — instructor approves metrics and reviews candidate edits; LLM proposes new edges or weakening of existing edges from error patterns; student generates learning traces; "No graph update occurs without expert sign-off and stored rationale."
  - **Paideia applicability:** These are the four teaching-interaction archetypes. Phase 7 scoping should evaluate which workflows to implement first. The instructor-authored + LLM scaffolding workflow is the lowest-risk entry point (no student-authored graph, no adaptive branching, no automated inference). Trace-informed revision is highest value but highest governance burden.

- **paper_2:L68–74** — Same four workflows described in prose in "Design Patterns for LLM and PDG Integration," with richer caveats. Adaptive branching: "For humanities, the practical implication is that branching should initially be **conservative and coarse-grained**, with explicit confidence intervals and human review for persistent anomalies." Trace-informed revision: "LLMs can accelerate the search for candidate revisions, but only if every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow."
  - **Paideia applicability:** The caveats map to Phase 7 posture decisions for the ADR: conservative/coarse-grained branching, confidence-plus-provenance required on every candidate edge.

_Paper 1 mentions the instructor workflow (six-stage construction) and student-facing exposure, but does not describe LLM roles in workflows — consistent with Paper 1 being the graph-only paper._

---

### L3.4 — Role-checkpoint partitioning

- **paper_2:L90–95** — The workflow table has four explicit columns: instructor role / LLM role / student role / human checkpoints. The checkpoint column per workflow:
  - Instructor-authored: "Approve graph; review low-confidence outputs; spot-check scoring."
  - Student-authored: "Instructor samples a subset for validity and disciplinary nuance."
  - Adaptive branching: "Review anomalous paths and override routing decisions."
  - Trace-informed revision: "No graph update occurs without expert sign-off and stored rationale."
  - **Paideia applicability:** The checkpoint column is the audit surface. Every checkpoint corresponds to a review-layer event (cf. L3.2 fifth service). For Paideia's teaching review layer, each checkpoint type should map to a concrete queue or notification. "No graph update without expert sign-off and stored rationale" is the mechanical enforcement of L3.9 (no-silent-mutation).

- **paper_2:L97–138** — The Kant-to-phenomenology Mermaid workflow diagram enumerates checkpoints as diamond decision nodes: `{Instructor review}` → Approve / Revise / Reject low-confidence edge; `{Mastery sufficient?}` → route; `{Human checkpoint on anomalies or disputed scoring}` → Override / Continue; `{Instructor approves graph edits?}` → Update PDG version / Store suggestion as unresolved. These are the four concrete checkpoint classes in the full lifecycle.
  - **Paideia applicability:** "Store suggestion as unresolved" is a distinct required state — the review queue must preserve it, not discard it and not auto-approve. The four checkpoint diamond classes map to four distinct event types the review layer must support.

- **paper_2:L140** — Closing summary of the workflow diagram: "This workflow embodies the best-supported division of labor: **the graph carries the pedagogical commitments, the LLM operationalizes them conversationally, and human reviewers arbitrate contested structure and consequential decisions**."
  - **Paideia applicability:** Three-role definition in canonical form. Should be quoted directly in the Phase 7 LLM integration ADR.

---

### L3.5 — Prompt template discipline

- **paper_2:L144–167** — The graph-refinement prompt template. Key discipline features:
  - Explicit role framing: "You are assisting with pedagogical graph review, **not rewriting the course**."
  - Bounded input set: "target learning outcome / current PDG nodes and edges / student error traces / approved source excerpts."
  - **JSON-only output**: "Return only JSON with: 1. candidate_new_edges / 2. candidate_weakened_edges / 3. evidence_for_each / 4. possible_false_prerequisites / 5. confidence_score_0_to_1 / 6. instructor_review_questions."
  - **Explicit rules section**: "prefer minimal edits / distinguish historical influence from pedagogical necessity / flag contested claims / never mark an edge as required unless evidence supports instructional dependence."
  - **Paideia applicability:** This template is a concrete artifact Paideia can adopt in Phase 7 with minimal modification. The JSON-only output constraint is critical: it prevents free-form LLM elaboration from bypassing the structured review workflow. The "never mark an edge as required unless evidence supports instructional dependence" rule is the prompt-level enforcement of the pedagogical-dependence/historical-influence separation. Paideia's prompt authoring should use this template as the starting schema.

- **paper_2:L169–182** — The student-facing explainer template's `Avoid:` block ("introducing unapproved terminology / assuming mastery of unmet prerequisites") is the negative-space constraint discipline. The avoid-block pattern is a prompt-discipline technique that should carry into all LLM teaching prompts.
  - **Paideia applicability:** Any teaching-side prompt should have an explicit negative-constraint section listing what the LLM must not introduce. This is operationalized prompt discipline, not just good style.

- **paper_2:L50** — Supporting evidence for why prompt discipline matters: "32 percent of generated hints initially failed quality checks" in the Pardos & Bhandari math tutoring study; "self-consistency was needed to reduce error rates." This is the empirical justification for the structured-output + explicit-rules approach.
  - **Paideia applicability:** The 32% initial-failure rate is the quantitative anchor for why undisciplined prompts are unacceptable in teaching contexts. Should be included in the Phase 7 LLM integration ADR rationale.

---

### L3.6 — Student-facing explainer template

- **paper_2:L169–182** — Full template:
  ```
  Explain the current node to a student who has mastered the listed prerequisites but not the target.
  Use:
  - one short definition
  - one humanities-relevant example
  - one contrast with a nearby concept
  - one formative question
  - one sentence explaining why this node matters for the next task
  Avoid:
  - introducing unapproved terminology
  - assuming mastery of unmet prerequisites
  ```
  - **Paideia applicability:** Production-quality artifact Paideia can adopt directly. The five-element `Use:` structure maps to five pedagogically distinct functions: definitional grounding / worked example / contrastive framing / diagnostic probe / motivational bridge. The `Avoid:` block enforces prerequisite-state awareness and lexical discipline. Critically, the template requires the runtime to inject "listed prerequisites" as a variable — which means the teaching runtime must resolve learner state from the analytics layer before calling the LLM. This is an architectural constraint, not just a stylistic preference.

- **paper_1:L130** — Paper 1 anticipates the student-facing exposure constraint without a template: "expose a student-friendly subset during the course." This is the motivation; Paper 2 operationalizes it.
  - **Paideia applicability:** Confirms that the subset-exposure requirement (L3.14) and the explainer template are the same concern at two levels of abstraction — subset exposure is the graph-level policy, the explainer template is the content-generation policy.

---

### L3.7 — Hallucinated-STRUCTURE risk

- **paper_2:L186** — Named explicitly and distinguished from hallucinated facts: "The largest pedagogical risk is **hallucinated structure**, not just hallucinated facts. In an LLM+PDG system, the most dangerous failure is often a **false prerequisite or an omitted prerequisite**, because it **silently changes the learning path**. That is especially acute in humanities, where canonical importance can be mistaken for pedagogical necessity."
  - **Paideia applicability:** The risk taxonomy for Paideia's teaching LLM integration must distinguish: (1) hallucinated facts — LLM claims X about a concept that is false; (2) hallucinated structure — LLM proposes a prerequisite relationship that silently mis-routes learners. Type 2 is harder to detect because it looks like reasonable pedagogical judgment, not a factual error. The no-silent-mutation rule (L3.9) and instructor review gates (L3.4) are the mitigations.

- **paper_2:L186** — Empirical anchor: "The empirical signal from math tutoring is sobering: even in a tightly bounded worked-solution context, ChatGPT-generated help initially **failed quality checks on 32 percent of problems** before mitigation."
  - **Paideia applicability:** Even in the constrained tutoring context (single worked solution, bounded domain), 32% failure rate. In open-ended humanities graph refinement, structural hallucination risk is likely higher. This is the empirical argument for requiring human review on every LLM-proposed graph edit.

- **paper_2:L186** — "NIST's GenAI profile explicitly treats confabulation as a core risk and recommends empirical testing, documentation of human-domain-knowledge interventions, review of sources and citations, and monitoring of overrides."
  - **Paideia applicability:** NIST alignment is an external governance anchor the Phase 7 ADR should cite. The four NIST recommendations map to Paideia concerns: empirical testing = L5.2/L5.9 (evaluation lens); human-domain-knowledge interventions = instructor review layer; source review = provenance field per L1.5; override monitoring = L4.8.

---

### L3.8 — Self-consistency for LLM output reliability

- **paper_2:L50** — "32 percent of generated hints initially failed quality checks, and **self-consistency was needed to reduce error rates**" (Pardos & Bhandari ChatGPT math tutoring study).
  - **Paideia applicability:** Self-consistency (sampling multiple outputs and comparing for agreement) is the technical mitigation for prompt-level unreliability. For graph-refinement prompts specifically, self-consistency checking across multiple runs before surfacing a candidate edge to the review layer would reduce false-positive load on human reviewers. This is an implementation pattern for the LLM orchestration service (L3.2).

- **paper_2:L52** — "The second thing the evidence supports is that **free-form LLM tutoring is not yet pedagogically reliable enough on its own**. A recent benchmark comparing LLM instructional moves with the adaptivity of an intelligent tutoring system concluded that current models still struggle to respond effectively to key context signals such as student errors and knowledge components."
  - **Paideia applicability:** Self-consistency is a symptom-level mitigation; the root mitigation is the PDG constraint layer. Self-consistency cannot rescue a poorly constrained prompt — it helps when outputs are sometimes correct and sometimes not, not when the prompt is systematically miscalibrated.

- **paper_2:L54** — "LLM grading studies remain mixed: one higher-education comparison found that ChatGPT grading looked plausibly human and that 70 percent of gradings fell within 10 percent of teacher scores, yet the system still tended to **overscore slightly** and **compressed extremes**."
  - **Paideia applicability:** Overscoring bias and extreme-compression are systematic failures that self-consistency alone does not fix. The mitigation is recalibration against instructor rubrics per L3.11 — a process correction, not a sampling correction.

---

### L3.9 — No-silent-mutation rule

- **paper_2:L194** — Stated as an explicit rule: "For PDG edits, this means a simple rule: **no silent graph mutation**. Every proposed edit should be attributable, reviewable, and reversible. Students should also be able to see when a path was altered because of model inference rather than instructor design."
  - **Paideia applicability:** Three properties — attributable, reviewable, reversible — map to: provenance field (L1.5), review-layer queue (L3.2 fifth service), version history (L1.14). The student-visibility clause extends the rule to the student-facing interface layer — a requirement beyond what the build-apparatus no-silent-mutation rule covers.

- **paper_2:L95** — Workflow table, trace-informed revision row: "No graph update occurs without expert sign-off and stored rationale." "Stored rationale" is the provenance field for LLM-proposed edits specifically — a required field on the candidate-edge schema, not optional.
  - **Paideia applicability:** The review layer must not permit approval of an edit without a rationale. The form should not structurally allow it.

- **paper_2:L68** — "The LLM then generates primers, examples, misconceptions, formative questions, and candidate refinements, but it **never silently rewrites the graph**." The emphasis is on "silently" — the prohibition is on mutation without a review step, not on the LLM generating candidates.
  - **Paideia applicability:** LLM can freely generate candidate edits into a staging area; the prohibition is on promoting those candidates to the live graph without human review. The staging area is a system design requirement. This parallels Paideia's routine-mode approach: proposed changes stage (eager-claim) and the delivery commit requires human review.

---

### L3.10 — Pre-registered edit policies

- **paper_2:L202** — Under instructor workflow: "Fifth, **pre-register which graph edits the system may suggest and which require disciplinary committee review**."
  - **Paideia applicability:** Pre-registration prevents the review layer from becoming a rubber stamp by forcing instructors to classify edit types upfront. For Paideia, this translates to a per-graph (or per-course) configuration object specifying: (a) edit classes a single instructor can approve; (b) edit classes requiring committee sign-off; (c) edit classes the system is prohibited from proposing (e.g., converting a "historical/contextual" edge to "required prerequisite" without provenance). This is a schema and workflow design requirement, not just a policy document.

- **paper_2:L68** — "instructors or discipline teams define the canonical nodes, edge types, learning outcomes, and **approved evidence**." The upfront definition of "approved evidence" is a form of pre-registration — the system can only propose edits grounded in evidence types the instructor pre-authorized.
  - **Paideia applicability:** "Approved evidence" as a per-graph configuration field. The content store holds only pre-approved source material; LLM proposals must cite sources from the content store, not free-recall. This bounds the LLM's evidence space mechanically.

- **paper_2:L95** — "Approve metrics and review candidate edits" (instructor role, trace-informed revision workflow). "Approve metrics" is pre-registration of the evaluation criteria the inference engine uses — not just approval of individual edits, but approval of the edge-discovery algorithm's parameters.
  - **Paideia applicability:** The analytics layer configuration (which trace metrics trigger edge-revision proposals, what confidence threshold surfaces a proposal to the review queue) should be an instructor-configurable, version-controlled artifact — not a hardcoded constant.

---

### L3.11 — LLM scoring as triage/drafting aid

- **paper_2:L54** — Directly stated: "For humanities teaching, that means LLM scoring should be used as a **triage or drafting aid**, not as an unreviewed arbiter."
  - **Paideia applicability:** The term "triage" captures the appropriate role precisely: LLM scoring surfaces items for human attention and prioritizes the reviewer's queue, but does not issue verdicts. For Paideia's formative assessment layer, LLM-scored diagnostics should be displayed with their score AND a flag indicating whether human review has confirmed the score — defaulting to "unconfirmed" until a human reviews.

- **paper_2:L50** — "In a large feedback study, receiving LLM-generated explanatory feedback was associated with small but significant posttest gains **for those who actually used it**." The conditional is important — effect depends on student uptake, which depends on trust in feedback quality.
  - **Paideia applicability:** Triage/drafting framing also matters for student-facing feedback. If students know feedback is LLM-drafted and human-reviewed, uptake may differ from feedback presented as AI-authoritative. The transparency rule (L3.9 student-visibility clause) interacts with triage framing.

- **paper_2:L190** — "The mitigation is to reserve consequential grading for human judgment or moderated hybrid workflows, to validate AI scoring against instructor rubrics and subgroup performance, and to **present the AI as a critic or coach**, not as the final judge."
  - **Paideia applicability:** "Critic or coach" is the student-facing framing; "triage or drafting aid" is the system-design framing. Both are the same underlying rule at different audience levels. Paideia should use "critic or coach" language in all student-facing UI copy that involves LLM-generated feedback or scoring.

---

### L3.12 — Model-as-critic-not-judge framing

- **paper_2:L190** — "The mitigation is to reserve consequential grading for human judgment or moderated hybrid workflows, to validate AI scoring against instructor rubrics and subgroup performance, and to **present the AI as a critic or coach, not as the final judge**."
  - **Paideia applicability:** The critic/coach vs. judge distinction should appear in: (1) student-facing UI copy wherever LLM output is shown; (2) instructor documentation; (3) the Phase 7 ADR for LLM integration as a named invariant. The framing also governs how LLM critique is phrased in the student-authored PDG workflow — LLM questions like "Which edge is evidentially strongest?" are critic moves, not authoritative verdicts.

- **paper_2:L70** — "the LLM responds with questions such as 'Which edge is evidentially strongest?', 'What concept seems assumed but not represented?', or 'Which node would you assess before asking for this comparison essay?' ... But the graph critique should be framed as **suggestive**, not authoritative, especially for contested interpretive domains."
  - **Paideia applicability:** "Suggestive, not authoritative" for contested interpretive domains is a precision refinement. In humanities specifically — where reasonable interpreters disagree — the LLM must not only avoid final-judge framing but must actively signal its own tentativeness on contested claims. Prompt discipline requirement: critique prompts should include a rule like "when the target concept involves contested interpretive claims, frame critiques as 'one reading suggests' rather than 'the correct view is'."

- **paper_2:L54** — "prompt composition and order changed feedback quality and scoring behavior." The judge framing fails doubly in humanities: LLM scoring is compositionally sensitive AND the targets are interpretive (no ground-truth verdict). Both arguments support the critic framing.
  - **Paideia applicability:** Compositional sensitivity to prompt changes is an argument for prompt version control in the LLM orchestration layer. Each teaching prompt should be versioned alongside the graph version — prompt drift is as dangerous as graph drift.

---

### L3.13 — Trace-informed candidate-edge generation

- **paper_2:L74** — "If many students repeatedly fail on a supposedly downstream node but perform well on its represented prerequisites, the system can flag either a missing prerequisite, an over-strong edge, or a bad assessment item. That is valuable because false prerequisites are one of the main risks in humanities PDGs: instructors can mistake a canonically central text or lineage for a learner-necessary precondition. LLMs can accelerate the search for candidate revisions, but only if **every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow**."
  - **Paideia applicability:** Four required fields per candidate edge (confidence, provenance, contrary evidence, approval workflow) are a schema requirement for the candidate-edge staging area. The three diagnostic signal types (repeated downstream failure despite prerequisite success / over-strong edge / bad assessment item) each suggest a different remediation: add an edge / weaken or convert to "recommended" / invalidate the mastery evidence.

- **paper_2:L56** — Evidence supporting automated inference feasibility: "E-PRISM retrieved promising prerequisite structures from learner traces; dialogue knowledge tracing with LLMs outperformed prior methods on two tutoring dialogue datasets; and LLM-assisted graph completion for curriculum/domain modeling showed good expert acceptance in higher education." All three are from STEM/structured domains — humanities applications will require additional validation.
  - **Paideia applicability:** These three results are the empirical foundation for Phase 7's trace-informed revision workflow. The STEM-concentration gap is a named risk to carry into Phase 7 scoping.

- **paper_2:L72** — "For humanities, the practical implication is that branching should initially be **conservative and coarse-grained**, with explicit confidence intervals and human review for persistent anomalies."
  - **Paideia applicability:** Conservative and coarse-grained = the starting posture for Phase 7's trace-informed workflow. Begin with threshold-level signals (learner consistently fails to reach a terminal outcome) rather than fine-grained per-edge inference. The analytics layer should implement this progression deliberately.

- **paper_2:L95** — Workflow table: "No graph update occurs without expert sign-off and stored rationale" (trace-informed revision row, human checkpoints column).
  - **Paideia applicability:** The approval gate is not optional — it is the mechanism that distinguishes trace-informed revision from autonomous graph mutation. The review layer must enforce the gate mechanically, not rely on instructor discipline to check a queue.

---

### L3.14 — Student-friendly subset exposure

- **paper_2:L200** — "In syllabus integration, the best practice is to expose the graph **sparingly and purposefully**. Students do not need the entire back-end ontology. They need the **current local neighborhood: the target node, its immediate prerequisites, common misconceptions, upcoming assessments, and alternative routes if they are stalled**. Instructors, by contrast, need the fuller graph for planning, diagnostic interpretation, and course revision."
  - **Paideia applicability:** Five elements of the student-visible neighborhood: target node / immediate prerequisites / common misconceptions / upcoming assessments / alternative routes. This is a concrete API contract for the student-facing graph view. Paideia's Phase 7 teaching frontend should implement a `get_local_neighborhood(learner_state, target_node)` endpoint that resolves exactly this set and no more.

- **paper_1:L130** — "expose a student-friendly subset during the course. This separation mirrors Decoding the Disciplines: students benefit from explicit bottlenecks and modeled subskills, while instructors need the more complex design map behind them."
  - **Paideia applicability:** The instructor/student split has a learning-science rationale (not just UX preference): exposing the full graph to students may be counterproductive, revealing the expert map before students have the conceptual scaffolding to read it correctly.

- **paper_2:L200** — Paper 2 restates the same Decoding the Disciplines rationale: "This separation mirrors Decoding the Disciplines: students benefit from explicit bottlenecks and modeled subskills, while instructors need the more complex design map behind them."
  - **Paideia applicability:** The instructor-view vs. student-view API split should be enforced at the access-control layer, not just as a UI convention. The student-facing API should structurally prevent returning the full graph, regardless of client behavior.

- **paper_2:L97–138** — The Kant-to-phenomenology workflow diagram shows student-facing exposure points as content generated from graph position: "LLM generates primers at novice, intermediate, advanced depth" and "LLM generates formative questions per node." Students see the primers and questions, not the nodes and edges directly.
  - **Paideia applicability:** The student-facing view is mediated by LLM-generated content anchored to graph nodes — students never directly navigate the graph. This is a critical architectural implication: the student-facing view is a content layer over the graph, not a graph viewer. The graph is backend structure; the student UI is LLM-generated content keyed to graph position.

---

### L3.15 — Tool-stack considerations

- **paper_2:L198** — Full tool-stack statement: "For the graph store, a property-graph database such as **Neo4j** is a strong fit when edges need rich attributes; **RDF tooling** such as Apache Jena is useful when interoperability and linked-data semantics matter; **NetworkX** is appropriate for prototyping analytics pipelines; and **Mermaid** is a low-friction way to embed text-defined graph visualizations into syllabi or course documentation."
  - **Paideia applicability:** This is the direct evaluation prompt for Paideia's current Postgres/Supabase stack. The full schema (L1.4, L1.5, L1.7 per schema lens, plus learner-state fields) requires edges with: source, target, edge_type, necessity_level, confidence (three independent scores), provenance (five fields), created_by, last_reviewed, counterexamples, assessment_link. Postgres supports rich attributes via JSONB, but graph traversal queries (prerequisite chains, neighborhood resolution, path-finding) in SQL become expensive at scale. The Phase 7 architecture ADR must explicitly evaluate: (a) whether Postgres JSONB + recursive CTEs is sufficient for anticipated query patterns; (b) whether a dual-layer approach (Postgres for transactional record-of-truth, Neo4j for query-layer) is warranted; (c) whether operational overhead of maintaining Neo4j alongside Supabase is justified at Paideia's current scale.

- **paper_1:L128** — Paper 1: "For planning and syllabus integration, **Mermaid, Graphviz, yEd, or Kumu** are usually sufficient. For concept-map elicitation with students, **CmapTools** remains the classic option."
  - **Paideia applicability:** These are appropriate for the planning-only use case (Phase 5 current state). The moment Paideia introduces an LLM integration layer with adaptive branching or trace-informed revision, lightweight tools become insufficient — they do not support the provenance, confidence, or learner-state schemas. Phase 7 planning should mark the threshold explicitly: the tool upgrade from lightweight (Mermaid/Postgres) to property-graph-capable storage is triggered by the introduction of the analytics or trace-informed-revision workflows, not by Phase 7 launch itself.

- **paper_2:L83–85** — The edge schema table implies specific query requirements: `confidence` (three fields), `provenance` (five fields), `counterexamples`, `assessment_link`. Learner-state schema (`mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`, `language_preference`) requires join-efficient access patterns keyed by learner + node.
  - **Paideia applicability:** Postgres can hold all fields, but the query patterns for adaptive branching (given learner state, find unmet prerequisites, rank by mastery probability, filter by confidence) are graph traversal queries. If the graph stays small (hundreds of nodes per course), SQL is viable. If the graph scales across multiple courses, the graph-store evaluation becomes urgent.

---

## Cross-cutting observations

### 1. The no-silent-mutation rule is load-bearing across all five services

Every service in the five-service architecture (L3.2) has a version of the no-silent-mutation constraint:
- **Graph store**: no silent write without provenance and version bump.
- **Content store**: approved excerpts only; unapproved sources cannot flow to LLM inputs.
- **LLM orchestration**: JSON-only structured output, never free-form graph rewrite.
- **Analytics layer**: candidate edges go to review queue, not directly to graph store.
- **Review layer**: no promotion without sign-off; "store suggestion as unresolved" is a required state.

Paideia's build-apparatus already has a version of this rule in the routine-mode pre-commit hook (scope_lock enforcement). The teaching-layer equivalent is architecturally analogous: the graph is the "allowed_paths" analog — the LLM's outputs are staged and gated exactly as routine-mode commits are staged and gated. The pattern is generalizable. When authoring the Phase 7 ADR, the build-apparatus no-silent-mutation machinery can serve as the existence proof that Paideia can implement this class of constraint.

### 2. The instructional-spine architecture is the structural answer to the hallucinated-structure risk

L3.1 and L3.7 are not independent sub-concerns — the spine-vs-interface architecture is the structural mitigation for hallucinated-structure risk. Without the spine (explicit, human-validated prerequisite graph), the LLM has no constraint against proposing structurally plausible but pedagogically wrong prerequisite chains. The PDG spine is not just useful for adaptivity — it is the anti-hallucination mechanism for the structural layer. Every design choice that weakens the spine (e.g., letting LLMs author graph nodes without instructor validation, or treating LLM-proposed edges as tentatively approved by default) directly increases hallucinated-structure risk. The two concerns must be evaluated together in any Phase 7 design review.

### 3. Prompt templates are architectural artifacts, not documentation

The two prompt templates in Paper 2 (L3.5 graph-refinement, L3.6 student-facing explainer) encode architectural constraints, not style choices:
- The graph-refinement prompt's JSON-only output requirement forces a structured interface between LLM and review layer. If output is free-form prose, the review layer cannot machine-parse candidate edges for the approval workflow.
- The student-facing explainer's "listed prerequisites" input variable requires the calling runtime to resolve learner state (from the analytics layer) before the prompt is issued. The prompt template implies a service-call ordering.
- The `Avoid:` block on the student-facing template ("assuming mastery of unmet prerequisites") requires the runtime to inject the full list of unmet prerequisites as a negative constraint — not just met prerequisites as positive context. Both lists must be passed.

Paideia should treat these templates as versioned, tested engineering artifacts (stored in the content store per L3.2, under version control, with prompt-version co-versioned with graph version). Changes to prompt templates should go through the same review discipline as graph edits.

---

## Coverage report

| Sub-concern | Status | Primary source |
|---|---|---|
| L3.1 Instructional-spine-vs-adaptive-interface | Found — 4 findings | paper_2:L6–7, L17, L68; paper_1:L130 |
| L3.2 Five-service architecture | Found — 2 findings | paper_2:L198 (×2) |
| L3.3 Four sample workflows | Found — 2 findings | paper_2:L90–95, L68–74 |
| L3.4 Role-checkpoint partitioning | Found — 3 findings | paper_2:L90–95, L97–138, L140 |
| L3.5 Prompt template discipline | Found — 3 findings | paper_2:L144–167, L169–182, L50 |
| L3.6 Student-facing explainer template | Found — 2 findings | paper_2:L169–182; paper_1:L130 |
| L3.7 Hallucinated-STRUCTURE risk | Found — 3 findings | paper_2:L186 (×3) |
| L3.8 Self-consistency for reliability | Found — 3 findings | paper_2:L50, L52, L54 |
| L3.9 No-silent-mutation rule | Found — 3 findings | paper_2:L194, L95, L68 |
| L3.10 Pre-registered edit policies | Found — 3 findings | paper_2:L202, L68, L95 |
| L3.11 LLM scoring as triage/drafting aid | Found — 3 findings | paper_2:L54, L50, L190 |
| L3.12 Model-as-critic-not-judge framing | Found — 3 findings | paper_2:L190, L70, L54 |
| L3.13 Trace-informed candidate-edge generation | Found — 4 findings | paper_2:L74, L56, L72, L95 |
| L3.14 Student-friendly subset exposure | Found — 4 findings | paper_2:L200; paper_1:L130; paper_2:L200, L97–138 |
| L3.15 Tool-stack considerations | Found — 3 findings | paper_2:L198; paper_1:L128; paper_2:L83–85 |

- Sub-concerns with ≥1 finding: **15 / 15**
- Sub-concerns with justified absence: **none**
- Total individual findings: **43**
- Paper 1 contributions: L3.1, L3.6, L3.14, L3.15 (supporting findings; Paper 1 is pre-LLM-integration, so LLM-specific claims are absent by design, not by omission)
