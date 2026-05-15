# Lens sweep — Pedagogical Method

> **Filled by Phase C agent.** Re-reads BOTH papers end-to-end through the single lens of how teaching uses graph structure.
>
> **Coverage rule:** every sub-concern below must have findings OR an explicit `_No findings because…_` justification.

## Sources

- Paper 1: `/Users/shanekidd/Documents/Claude_Files/temp/Assessing the Utility of Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`
- Paper 2: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md`

## Findings by sub-concern

### L2.1 — Threshold concepts as load-bearing pedagogical primitives (Meyer & Land)

- **paper_1:§3** — Meyer and Land's threshold-concept argument is named as the fifth theoretical pillar for PDGs: "some concepts are transformative and troublesome and that learners may struggle to progress without them." The paper treats threshold concepts as the primary reason that humanities PDGs require something richer than "knowing X before Y" — they require explicit recognition that crossing a threshold reorganizes the learner's entire conceptual apparatus.
  - **Paideia applicability:** Nodes should carry a `threshold_concept` boolean (or tri-value: threshold / bridge / background). The recommender must gate advancement differently on threshold nodes than on ordinary content nodes — a student who has not crossed a threshold is not merely missing a fact; they may be unable to interpret downstream material at all. This is a qualitatively different routing rule from a standard prerequisite check.

- **paper_1:§5 (schema table)** — The recommended node-type taxonomy explicitly lists "Threshold concept" as a distinct node type alongside bridge concept, disciplinary practice, text/excerpt, historical context, misconception, comparative lens, and assessment task.
  - **Paideia applicability:** The current Paideia graph has no node-type field. Adding one — even just `threshold_concept` vs `bridge_concept` vs `background` — is the minimum needed before Phase 7 teaching logic can make principled routing decisions.

- **paper_1:§6 (implications)** — "If a graph treats 'historical perspective taking' or 'disciplinary meaning of text' as a threshold, then assessment tasks should check for those competencies directly rather than only testing downstream essay performance."
  - **Paideia applicability:** Assessment-design rule: for every threshold node, the teaching app must have a direct formative check for that threshold — not just downstream essay quality. Threshold nodes are the places where indirect assessment most systematically misleads instructors.

- **paper_2:§Why combination is plausible** — Corrigan's threshold-concept work in literary studies is described as "almost a template for node construction in a humanities PDG": "students must cross threshold concepts around text, meaning, context, form, and reading" to think like literary scholars. Paricio's finding that "perspective functions as a threshold concept in learning history" is cited as a second concrete disciplinary case.
  - **Paideia applicability:** The Paideia graph already contains phenomenology, structuralism, and historiography nodes. These should be audited against the Corrigan/Paricio threshold-concept template — identifying which of the current 380 nodes are actually transformative/troublesome vs which are merely content summaries. That distinction changes how the teaching app routes and scaffolds.

- **paper_2:§Definitions** — "In literary studies, Paul Corrigan argues that disciplinary understandings of text, meaning, context, form, and reading differ sharply from commonsense understandings and function as threshold concepts that students must cross to think like literary scholars." Named here as a core rationale for the PDG architecture, not just a citation.
  - **Paideia applicability:** These five terms (text, meaning, context, form, reading) are strong candidates for threshold-tagged nodes in any literary-theory subgraph Paideia builds. Their presence in the graph as threshold nodes — rather than as ordinary definitional nodes — would change the scaffolding logic around them.

- **paper_2:§Implementation** — The recommended instructor workflow begins: "First, identify the course's threshold concepts and bottlenecks." This is step zero before granularity assignment, diagnostic attachment, or edge-necessity marking.
  - **Paideia applicability:** The Phase 7 teaching-app build procedure should begin with a threshold-concept audit of the existing graph, not with recommender logic. The threshold census must precede path-selection algorithm design.

---

### L2.2 — Bottleneck identification via Decoding the Disciplines (Middendorf & Pace)

- **paper_1:§3** — "Decoding the Disciplines operationalizes [threshold-concept theory] by asking experts to identify where students get stuck and what tacit operations experts perform to move through the bottleneck." Positioned as one of the five core pillars of PDG theory.
  - **Paideia applicability:** The Decoding interview protocol should be part of the Phase 6/7 graph validation process. Without it, the current Paideia graph reflects expert-authored conceptual topology but not expert-identified student-facing bottlenecks — two different things. A Decoding pass would produce a ranked bottleneck list that maps onto nodes requiring the highest-priority scaffolding instrumentation.

- **paper_1:§4 (construction workflow)** — The recommended six-stage construction workflow explicitly names Decoding the Disciplines as a co-method alongside backward design and knowledge-space discipline. Stage 2 is: "identify bottlenecks through student work, diagnostic discussion, or a Decoding interview." Decoding comes before drafting nodes and edges.
  - **Paideia applicability:** The existing Paideia graph was not constructed via Decoding interviews — it was built from corpus extraction. A future Decoding pass would be the primary method for distinguishing which existing edges are genuine learning bottlenecks vs which merely reflect disciplinary genealogy. The teaching app cannot prioritize scaffolding investment without this information.

- **paper_1:§7 (implications — interdisciplinarity)** — "Research on interdisciplinary humanities learning remains relatively sparse, but recent work confirms that the area is under-studied and conceptually demanding, which strengthens the case for explicit dependency modeling rather than leaving bridges implicit."
  - **Paideia applicability:** Cross-domain edges in the Paideia graph (e.g., a node that bridges philosophy of language and feminist theory) are the candidates most at risk of being tacit assumptions. These are exactly the bottleneck-identification targets for a Decoding pass.

- **paper_2:§Why combination is plausible** — "Middendorf and Pace's Decoding framework explicitly focuses on bottlenecks, making disciplinary thinking visible, modeling constituent parts, giving practice on isolated subskills, and assessing whether students have mastered those subskills. That is structurally very close to what a PDG formalizes."
  - **Paideia applicability:** The Decoding framework's four-step pattern (make visible → model → practice subskills → assess subskills) maps directly onto four teaching-app capabilities that Paideia's Phase 7 architecture should implement. The graph must support "modeled constituent parts" as intermediate scaffold nodes between a bottleneck and the target concept.

- **paper_2:§Implementation (instructor workflow)** — "Instructors should review low-confidence edges weekly, audit a sample of scored diagnostics, and examine whether branches are disproportionately burdening specific groups." This is a sustained Decoding-informed review loop, not a one-time pre-semester exercise.
  - **Paideia applicability:** The teaching app needs a review-layer dashboard that surfaces low-confidence edges and anomalous routing patterns — inputs to an ongoing Decoding-style bottleneck census across cohorts.

---

### L2.3 — Backward design ordering (outcomes → assessment → sequence)

- **paper_1:§4 (construction workflow)** — "Start by specifying learning outcomes and acceptable evidence of learning; then identify bottlenecks and tacit expert operations; only then draft nodes and edges. This order matters because dependency claims are meaningful only relative to desired performances: the prerequisites for 'identify key phenomenological themes in a short passage' are not the same as those for 'compare Kantian and Husserlian transcendental philosophy in a research essay.' Constructive alignment and backward design both insist that outcomes and assessment should drive teaching sequence, not the reverse."
  - **Paideia applicability:** The Paideia graph was built from corpus content, not from a defined learning-outcome hierarchy. Before Phase 7, at minimum a lightweight outcome taxonomy should be imposed on the graph so that path-selection logic can be parameterized by outcome. Without outcomes, the recommender will be forced to use historical/topical structure as a proxy for pedagogical sequence — exactly the conflation both papers warn against.

- **paper_1:§4 (schema table)** — "Outcome alignment: which assignment, discussion move, or exam item the node supports. Keeps the graph tied to constructive alignment rather than abstract field lore." Listed as a required schema element.
  - **Paideia applicability:** An `outcome_alignment` or `learning_outcome` field on nodes is a Phase 6/early-Phase 7 schema addition. Without it, every node in the current graph is effectively assessed only by downstream connectivity, not by what the student should be able to do after mastering it.

- **paper_2:§Definitions** — "A PDG asks the different question of what students must understand first for a given learning goal, at what granularity, with what evidence, and with what confidence." The goal-specificity of prerequisite claims is the definitional characteristic of a PDG as distinguished from an influence map.
  - **Paideia applicability:** The teaching app's path-selector must accept a learning-goal parameter as input, not just a target node. Two students arriving at the same node with different downstream goals should receive different prerequisite paths — this requires outcome-parameterized edge weights.

- **paper_2:§Design patterns (instructor-authored workflow)** — The sample workflow diagram begins with "Instructor defines target outcome: Explain Husserl's transcendental turn" as step A, before any node seeding or edge proposal. The outcome is the anchor; the graph is derived from it.
  - **Paideia applicability:** The Kant-to-phenomenology workflow diagram is a concrete template for how Paideia's teaching app should structure unit planning. The outcome is stated first; the LLM then proposes candidate edges relative to that outcome; the instructor reviews. This is the backward-design sequence operationalized as a software workflow.

- **paper_2:§Implementation** — "Define node granularity at the level of teachable, assessable units rather than whole books or authors whenever possible. Attach at least one diagnostic task to every node that can plausibly function as a prerequisite."
  - **Paideia applicability:** Many Paideia nodes are currently keyed to authors or texts (whole books). Backward design demands granularity at the level of assessable subskills. A Phase 6 granularity audit should flag nodes that are too coarse to support a diagnostic check.

---

### L2.4 — Scaffolding with explicit fade trajectory (Wood/Bruner/Ross + Vygotsky ZPD)

- **paper_1:§3** — "Vygotsky's zone of proximal development defines the range of tasks learners can complete with guidance but not yet alone, while Wood, Bruner, and Ross's tutorial model and later scaffolding reviews characterize good support as contingent, fading, and responsibility-transferring. That is almost a formal description of how a humane PDG should be used: not as a gatekeeping machine, but as a scaffold planner that tells instructors where modeling, worked examples, collaborative talk, or comparative framing are most needed and when those supports should be withdrawn."
  - **Paideia applicability:** The teaching app's scaffolding logic must be explicitly time-bounded. For each scaffolded edge, there should be a mastery-growth trigger that withdraws the scaffold (reduces explanation depth, removes worked examples, shifts to retrieval-practice mode). This is a fade-trajectory field on edges or a separate learner-state rule, not a static on/off support.

- **paper_1:§6 (implications — scaffolding precision)** — "The principal pedagogical benefit of PDGs is that they can make scaffolding more precise. Instead of giving the same amount of background to everyone, instructors can target where support is likely to matter most, then fade it as students gain fluency."
  - **Paideia applicability:** Precision scaffolding requires two things the current graph lacks: (1) node-level marking of where scaffolding is needed most (high bottleneck score), and (2) a learner-state model that tracks fluency growth. The teaching app can implement a lightweight version — "scaffold at first encounter, fade at second encounter, remove at third" — as a default before full learner-state tracking is in place.

- **paper_1:§4 (empirical evidence — Shakespeare and journal writing)** — "Oksa, Kalyuga, and Chandler found an expertise-reversal effect in reading Shakespearean texts: explanatory supports that aided less knowledgeable learners became detrimental for more knowledgeable readers. Nückles and colleagues found a similar pattern in writing-to-learn journal prompts across a term: prompts helped earlier, and then lost their advantage or reversed as learners gained expertise. These studies imply that a good PDG should not only state dependencies but also indicate when supports tied to those dependencies should fade."
  - **Paideia applicability:** The fade-trajectory implication is stated explicitly by paper 1 here. For Paideia's humanities content (phenomenology, structuralism, gender theory), the Shakespeare and journal-writing analogies are close: scaffolding secondary texts is pedagogically similar to scaffolding Shakespeare close reading. The fade heuristic should apply to reading guides, definitional scaffolds, and worked-example prompts — not just to prerequisite gates.

- **paper_2:§Why combination is plausible** — "A static syllabus often cannot respond to that dynamic, but an LLM conditioned on a PDG can, in principle, give heavier support on fragile prerequisite nodes and then fade support as mastery increases."
  - **Paideia applicability:** The LLM+PDG integration specifically enables runtime fade — the LLM adjusts explanation depth based on the learner-state field `mastery_probability`. This is only possible if the PDG graph carries `mastery_evidence` per node and the learner-state is updated per interaction.

- **paper_2:§Learner state schema** — The schema table includes `mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`, `language_preference` as learner-state fields. The explicit rationale: "Helps the LLM choose explanation depth, detect potential expertise reversal, and adapt questioning."
  - **Paideia applicability:** Phase 7 architecture must include a learner-state store separate from the graph. The fade trajectory is computed from learner-state (`mastery_probability` rising) against a node-level threshold. Without the learner-state store, the scaffolding system can only deliver static scaffolds.

---

### L2.5 — Novice-vs-expert differentiation (expertise reversal effect — Kalyuga)

- **paper_1:§3** — "The expertise reversal effect shows that guidance that helps novices can become redundant or counterproductive for more advanced learners. Kalyuga's review and the broader adaptive-learning literature both emphasize that instruction should change as learner expertise grows; the latter explicitly notes related evidence in ill-defined domains including literary text and journal writing. In practical terms, this means PDGs should encode confidence levels and adaptive fading. A dependency that is 'hard' for novices may become optional for advanced students, and a graph that cannot be adjusted by cohort will not remain pedagogically valid for long."
  - **Paideia applicability:** Edge necessity level should be audience-parameterized: `necessity_level` can be `required_for_novice` / `optional_for_intermediate` / `skip_for_advanced`. A single static edge weight misrepresents the learner-dependence structure for any heterogeneous cohort. The teaching app must have a cohort-profile input that adjusts which edges are treated as hard vs soft vs optional.

- **paper_1:§4 (evidence — Shakespeare and journal writing)** — "Oksa, Kalyuga, and Chandler found an expertise-reversal effect in reading Shakespearean texts: explanatory supports that aided less knowledgeable learners became detrimental for more knowledgeable readers." The literary-humanities evidence is cited because it is the closest-domain analog to Paideia's content area.
  - **Paideia applicability:** For any Paideia node where a scaffolding material has been designed (reading guide, worked-example prompt, explainer text), the teaching app should implement an expertise check before delivering that material — not assume it is universally helpful. "Show scaffold if `mastery_probability` < 0.4; suppress if > 0.7" is a reasonable default threshold policy.

- **paper_2:§Why combination is plausible** — "The expertise reversal effect then adds a further complication: scaffolds that help novices can become redundant or even counterproductive for more advanced learners. A static syllabus often cannot respond to that dynamic, but an LLM conditioned on a PDG can, in principle, give heavier support on fragile prerequisite nodes and then fade support as mastery increases."
  - **Paideia applicability:** This frames the LLM+PDG combination specifically as the solution to the expertise-reversal problem. The LLM's conversational flexibility, constrained by the PDG's mastery-state, enables the fade that a static syllabus cannot perform.

- **paper_2:§Node schema** — The `learner_state` schema field `mastery_probability` and `evidence_count` are the operationalization of the expertise-reversal detection signal. When `mastery_probability` is high and `evidence_count` is sufficient, the system should trigger fade.
  - **Paideia applicability:** The teaching app needs a simple mastery-state update rule: each correct diagnostic answer raises `mastery_probability`; each error lowers it. The fade trigger fires when `mastery_probability` crosses the configured threshold for the node's `necessity_level`. This is the minimum viable expertise-reversal implementation before full knowledge-tracing is in place.

---

### L2.6 — Misconception remediation as explicit pedagogy

- **paper_1:§4 (implementation — three principles)** — "Encode misconception nodes explicitly—for example, 'phenomenology = introspection,' 'deconstruction = anything goes,' or 'historical perspective = sympathy with the past'—because many humanities bottlenecks are caused by misleading prior understandings rather than by absent content."
  - **Paideia applicability:** These three examples are directly relevant to Paideia's content domain. The graph currently has no misconception nodes. Adding them — even as a lightweight `common_misconception` text field on existing nodes before adding a distinct misconception node type — would immediately enable the teaching app to surface and address the most common entry errors. The three named misconceptions are almost certainly present in any introductory cohort studying phenomenology, deconstruction, or historiography.

- **paper_1:§4 (schema table)** — "Node type: … Misconception" is listed as one of the eight recommended node types. The schema table also includes "likely misconceptions" as an edge-level attribute: "Attach assessments and likely misconceptions to nodes and edges."
  - **Paideia applicability:** Two-level misconception encoding is recommended: (1) a `misconceptions` field on nodes (common wrong beliefs about this concept), and (2) a `misconception-remediation` edge type linking a misconception node to the corrective concept node. The Paideia graph currently has neither.

- **paper_1:§6 (assessment design)** — "PDGs are also useful for assessment design. If a graph treats 'historical perspective taking' or 'disciplinary meaning of text' as a threshold, then assessment tasks should check for those competencies directly rather than only testing downstream essay performance."
  - **Paideia applicability:** Formative diagnostics should include misconception-detection items: "Which of the following best describes what phenomenologists mean by 'reduction'?" with distractor options derived from the named misconceptions. The graph's misconception field feeds the diagnostic item bank.

- **paper_2:§Definitions** — "In literary studies, Paul Corrigan argues that disciplinary understandings of text, meaning, context, form, and reading differ sharply from commonsense understandings and function as threshold concepts that students must cross." The commonsense-vs-disciplinary clash is a misconception at the definitional level.
  - **Paideia applicability:** For each of the five Corrigan terms (text, meaning, context, form, reading), the teaching app needs a specific misconception-remediation entry point: show the student what the word means colloquially, then explicitly demonstrate how the disciplinary meaning diverges. This is not just a definition — it is an unlearning sequence.

- **paper_2:§Node schema** — `misconceptions` is a required field on the node schema: "Lets the LLM explain the node, generate aligned examples, distinguish threshold concepts from background context, and ground outputs in approved sources rather than free-form recall." The LLM uses the `misconceptions` field to generate targeted pushback when a student's diagnostic response reveals the misconception.
  - **Paideia applicability:** The LLM integration depends on `misconceptions` being populated in the graph. Without it, the LLM must confabulate plausible misconceptions — exactly the failure mode the graph is designed to prevent. Populating `misconceptions` on the highest-traffic Paideia nodes is Phase 6/7 priority work.

---

### L2.7 — Unlearning commonsense meanings (Corrigan)

- **paper_1:§3** — "Corrigan's work in literary studies is especially relevant because it shows that many humanities obstacles are not missing facts but clashes between commonsense and disciplinary meanings of terms like text, meaning, context, form, and reading. PDGs are well suited to this terrain because they can represent not only 'knowing X before Y' but also 'unlearning a commonsense meaning before a disciplinary meaning becomes available.'"
  - **Paideia applicability:** The teaching app needs a distinct edge type for unlearning dependencies — not "A is a prerequisite for B" but "the commonsense reading of A must be actively displaced before B is accessible." This is architecturally different from a soft prerequisite: it requires a specific remediation sequence, not just coverage. Edge type: `unlearning_required_before`.

- **paper_1:§5 (case study — literary theory)** — "Corrigan's threshold-concept argument suggests that the real obstacles often lie in disciplinary meanings of text, meaning, context, and reading; Saussurean notions like signifier/signified and langue/parole can function as bridge concepts, but requiring exhaustive structural linguistics before any work on deconstruction is usually unnecessary."
  - **Paideia applicability:** The Saussure/Derrida subgraph in Paideia should mark the folk-meaning obstacles explicitly. The pedagogical path for deconstruction is not "learn all of Saussure → learn deconstruction" but "displace folk notion of 'text as transparent container' → introduce signifier/signified instability → introduce Derrida's trace." The order and the type of dependency differ from a simple prerequisite chain.

- **paper_1:§4 (limitations — cultural bias risk)** — "A second risk is cultural and epistemic bias. If the graph assumes one canonical route through a tradition, it may reproduce disciplinary gatekeeping—for example, by silently privileging European conceptual histories, elite genres, or jargon-heavy formulations as the only valid entry point." This risk is amplified when unlearning requirements embed one tradition's folk meanings as universal.
  - **Paideia applicability:** Unlearning edges in particular risk cultural specificity — what counts as the "commonsense" meaning of "text" or "meaning" is not universal. The teaching app should allow instructor configuration of which folk meanings to address, rather than hard-coding a single "commonsense baseline" into the graph.

- **paper_2:§Definitions** — "These are pedagogical dependencies even when they do not map neatly onto historical influence networks." The unlearning of commonsense meanings is the primary example of a dependency that has no historical-influence parallel — there is no influence relationship between colloquial English "text" and Barthes's "Text"; the dependency is entirely pedagogical.
  - **Paideia applicability:** The three-relation separation (historical influence / conceptual relatedness / pedagogical dependence) in paper 2 is especially important here. Unlearning edges are purely pedagogical — they should live only in the PDG layer, not in any influence layer.

- **paper_2:§A humanities-specific implication** — "In history, an influence map may be nearly irrelevant compared with the threshold concept of perspective, which students need before they can stop reading the past through presentist assumptions." Presentism is named as a commonsense temporal assumption that must be actively displaced before historical thinking is possible.
  - **Paideia applicability:** "Presentism" (reading the past through contemporary assumptions) is a named unlearning target for historiography nodes in the Paideia graph. The teaching app should have a presentism-detection diagnostic that fires before the student is routed to primary-source analysis nodes.

---

### L2.8 — Multiple-entry-routes for ill-structured domains (Spiro cognitive flexibility)

- **paper_1:§3** — "Spiro and colleagues' cognitive-flexibility work argues that advanced learning in complex conceptual domains is often undermined by oversimplification, single-lens instruction, and tidy but misleading schema. Their remedy is multiple representations, revisiting, and explicit attention to irregularity and context-dependence. This is the best argument against simplistic PDGs and the best argument for sophisticated ones: a good humanities PDG should illuminate where dependencies are real while preserving multiple routes, contrastive cases, and later reorganization of the graph as understanding deepens."
  - **Paideia applicability:** The teaching app must not collapse the graph into a single recommended path. For any given learning goal, the path-selector should surface at least two or three distinct entry routes (e.g., conceptual, case-based, methodological) and allow the student or instructor to choose. The graph's edge semantics must support this: `helpful_bridge` and `alternative_entry` edge types are distinct from `hard_prerequisite`.

- **paper_1:§4 (three implementation principles)** — "Preserve multiple routes into complex topics. Spiro's work on ill-structured domains suggests that one-lens sequencing is dangerous; a good PDG should therefore allow case-based, conceptual, methodological, and historical entry points that later converge."
  - **Paideia applicability:** This is one of the paper's three named implementation principles — equal weight to misconception encoding and soft-dependency preference. For Phase 7 path-selection, the algorithm must support multi-route entry explicitly. The UI should show the student their current path and the existence of alternatives, so they do not mistakenly believe there is only one valid approach.

- **paper_1:§3 (SoTL humanities example)** — "In a later SoTL study in Women in Christian History, Hovland argued that concept maps can function as 'working objects' in a humanities classroom and can invite students toward multiple, undefined learning outcomes rather than only ranking them against tightly predefined ones."
  - **Paideia applicability:** The "working object" framing is a pedagogical posture the Paideia teaching app can adopt: expose the local neighborhood graph to students not as "this is the required path" but as "here are the concepts and their relations — what do you want to explore?" This is a different UX mode from adaptive-branching: it is student-directed graph navigation rather than system-directed sequencing.

- **paper_2:§Governance — cultural/linguistic bias** — "The mitigation is not to abandon structuring, but to make graph structure visibly provisional where appropriate: store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."
  - **Paideia applicability:** The phrase "multiple legitimate entry routes" appears here as a governance requirement, not just a pedagogical preference. The teaching app must surface alternative paths visibly, with tradition labels where relevant. For example, a student approaching deconstruction might see "structuralist entry (via Saussure)" and "literary-critical entry (via close reading instability)" as distinct labeled routes.

- **paper_2:§Design patterns — student-authored graph with LLM critique** — The student-authored PDG pattern is specifically designed to prevent single-lens instruction: "humanities threshold-concept work shows that making tacit disciplinary structure explicit is itself part of learning." Having students construct their own dependency maps surfaces their single-lens assumptions for the LLM to interrogate.
  - **Paideia applicability:** The student-authored graph pattern is one of four recommended design patterns for Phase 7. It is the anti-single-lens intervention: the LLM asks "What concept seems assumed but not represented?" to force the student to notice their own missing alternative routes.

---

### L2.9 — Recursive revisiting

- **paper_1:§2 (definition section)** — "A workable research definition for humanities teaching is: a directed graph whose nodes are teachable concepts, practices, texts, or thresholds, and whose edges represent empirically or instructionally justified claims that mastery of one node materially improves the chances of mastering another for a specified audience and outcome. That definition is narrower than a concept map and broader than a strict prerequisite DAG, which matters because humanities learning often includes soft dependencies, contrastive links, and recursive revisiting."
  - **Paideia applicability:** Recursive revisiting is named in the definitional section as a structural requirement. The current Paideia graph is a DAG (directed acyclic graph). If recursive revisiting requires nodes to be revisited at different levels of depth (not just traversed once), the graph may need either (1) annotated re-traversal edges, or (2) a "depth layer" system where the same node appears at multiple granularity levels. The teaching app must support "you've already seen this node — here is what you can now notice that you couldn't before."

- **paper_1:§4 (implementation — instructor workflow)** — "Draft the graph before the course; expose a student-friendly subset during the course; use formative assessments and discussion transcripts to see where the graph over- or under-predicts difficulty; then revise." The iterative cycle is implicitly recursive: the same graph is traversed, assessed, revised, and re-traversed.
  - **Paideia applicability:** The teaching app should track which nodes a student has visited, at what mastery level, and when. Revisits should be differentiated from first encounters — the LLM prompt for a second encounter should differ from the first-encounter prompt (less definition, more comparison and application).

- **paper_1:§4 (open questions)** — "How best to model recursive revisiting and interpretive plurality without collapsing into either rigidity or vagueness" is named as one of the three major open empirical questions for PDG research.
  - **Paideia applicability:** This is acknowledged as unsolved. The Paideia teaching app should not assume a clean solution exists — it should implement a conservative default (track visit count, differentiate prompt by count) while flagging recursive-revisiting as a research question to be evaluated with real learner data.

- **paper_2:§Design patterns — adaptive branching** — "The system updates mastery estimates; and the next activity is selected from graph neighbors whose prerequisites are satisfied." Mastery estimate updating implies that a node's status can change over time — the learner may revisit a previously mastered node if errors downstream suggest the mastery estimate was wrong.
  - **Paideia applicability:** The knowledge-tracing component of the adaptive-branching pattern handles recursive revisiting implicitly: if downstream errors reveal a shaky prerequisite, the system routes back. The teaching app should expose this to the student ("We're revisiting X because your recent work on Y suggests we should consolidate it") rather than silently looping.

---

### L2.10 — Interdisciplinarity as bridge

- **paper_1:§7 (interdisciplinarity section)** — "A PDG can show where an interdisciplinary concept is a bridge rather than an origin. This can reduce curricular confusion: students can be told, for example, that a short module on speech acts is included not because they are being made into philosophers of language, but because that bridge will support later reading in feminist and queer theory. Research on interdisciplinary humanities learning remains relatively sparse, but recent work confirms that the area is under-studied and conceptually demanding, which strengthens the case for explicit dependency modeling rather than leaving bridges implicit."
  - **Paideia applicability:** Interdisciplinary bridge nodes should be explicitly labeled as `bridge_concept` rather than `threshold_concept` or `background`. The teaching app's student-facing UI should explain WHY an interdisciplinary module is present ("this bridge supports X later") — which requires the `outcome_alignment` field on bridge nodes to be populated. Without explicit bridge labeling, students experience interdisciplinary modules as arbitrary detours.

- **paper_1:§5 (case study — Austin and Butler)** — "In gender theory, Austin's speech-act distinctions and later performativity debates matter historically, but the pedagogical dependencies are more fine-grained. Students often need to understand what a performative utterance is, how illocution differs from perlocution, and why discourse and repetition matter before Butler's claims about gender performativity become intelligible rather than sloganized."
  - **Paideia applicability:** The Austin → Butler path is a named interdisciplinary bridge: philosophy of language bridging into gender theory. This is a concrete Paideia-relevant case where the bridge edge type is needed. The graph should mark the Austin speech-act nodes as `bridge_concept` with `outcome_alignment` pointing to the Butler/performativity nodes.

- **paper_1:§5 (case study — Nietzsche and Foucault)** — "What conceptual moves do students need before they can read genealogy as method rather than as mere historical narrative? Selective dependency: contingency, critique of origins, discourse/power, and anti-teleology matter more than exhaustive prior coverage of Nietzsche."
  - **Paideia applicability:** The Nietzsche → Foucault case is another interdisciplinary bridge where the bridge is partial (not "all of Nietzsche" but specific conceptual moves). The teaching app must support partial-bridge traversal: "You need these three Nietzsche concepts as a bridge to genealogical method — not the full Nietzsche curriculum."

- **paper_2:§A humanities-specific implication** — "In rhetoric/philosophy of language, an influence map may show Austin → later speech-act theorists, while a PDG for analyzing performatives may first require 'utterances can do actions,' 'locution/illocution/perlocution,' and 'contextual felicity conditions.'"
  - **Paideia applicability:** The speech-act → performativity bridge is described at the sub-concept level: three specific concepts from Austin, not Austin as an author node. The Paideia graph's current author-level granularity may be too coarse for bridge traversal. Phase 6 should break author nodes into sub-concept nodes where the author is primarily a bridge contributor.

---

### L2.11 — Cognitive load management (Sweller)

- **paper_1:§3** — "Sweller's classic argument is that conventional problem solving can consume working-memory resources needed for schema acquisition, and later formulations place special emphasis on limited working memory, schema construction, and the need to manage intrinsic complexity. For humanities teaching, the implication is not that difficult texts should be simplified away, but that instructors should avoid piling too many unintegrated conceptual demands onto novices at once. A PDG can therefore function as a tool for controlling element interactivity—for example, by isolating one conceptual threshold before adding a second and by distinguishing optional background from genuinely load-bearing preparation."
  - **Paideia applicability:** The teaching app's sequencing algorithm should implement an element-interactivity budget: for any session or module, limit the number of new threshold or high-complexity nodes introduced simultaneously. The PDG graph supports this by marking which nodes are threshold-level (high intrinsic complexity) vs bridge (lower standalone complexity). The sequencer should never co-schedule two threshold nodes without an integration exercise between them.

- **paper_1:§3 (element interactivity framing)** — "A PDG can therefore function as a tool for controlling element interactivity — for example, by isolating one conceptual threshold before adding a second." This is the specific cognitive-load application of PDG structure.
  - **Paideia applicability:** Element interactivity is operationalized in the graph by the edge structure: a node that is a prerequisite for multiple downstream nodes has high element interactivity if those downstream nodes are introduced in parallel. The teaching app should detect "parallel prerequisite fan-out" patterns and enforce sequential introduction of downstream nodes, not simultaneous.

- **paper_1:§4 (construction — granularity)** — "Choose graph granularity: overly coarse graphs hide real obstacles, but overly fine graphs become unteachable." The granularity rule is a cognitive-load rule: too fine-grained a graph overwhelms both instructor and student with unnecessary interacting elements.
  - **Paideia applicability:** Paideia's 380-node graph needs a granularity audit before Phase 7. Nodes that are too coarse (whole authors, whole movements) should be broken down; nodes that are too fine (sub-distinctions that don't survive as teachable units) should be merged. The right granularity level is "teachable, assessable unit" — the cognitive-load criterion.

- **paper_2:§Why combination is plausible** — "Cognitive load theory predicts that novices suffer when tasks require them to integrate too many unfamiliar elements at once." The LLM+PDG combination addresses this because the PDG constrains what the LLM explains — preventing the LLM from front-loading too many unintegrated concepts in a single response.
  - **Paideia applicability:** The student-facing explainer prompt template in paper 2 ("one short definition, one humanities-relevant example, one contrast with a nearby concept, one formative question, one why-this-matters sentence") is a cognitive-load management heuristic: it limits element count per LLM response to five constrained moves, preventing overwhelming explanations. The Paideia teaching app should adopt this template as its default LLM response structure.

- **paper_2:§LLM-generated concept maps finding** — "LLM-generated concept maps reduced perceived cognitive load by 31.5 percent and improved reading efficiency by 14.1 percent with comparable comprehension accuracy." The strongest direct empirical finding on LLM+graph → cognitive load reduction.
  - **Paideia applicability:** This finding supports investing in student-facing graph visualization as a cognitive-load reduction tool, not just as a navigation aid. Showing students the local neighborhood of their current position reduces the cognitive overhead of figuring out "where am I in this topic?" and frees working memory for conceptual work.

---

### L2.12 — Formative assessment alignment per node

- **paper_1:§4 (six-stage construction workflow)** — Stage 5 is: "attach assessments and likely misconceptions to nodes and edges." Formative assessment alignment is a construction-time activity, not an afterthought. The schema table includes "Outcome alignment: which assignment, discussion move, or exam item the node supports."
  - **Paideia applicability:** The `assessment_items` and `mastery_evidence` fields in the recommended node schema are Phase 6/7 additions. Every node that can plausibly serve as a prerequisite needs at least one attached diagnostic item before the teaching app can make adaptive routing decisions. Without assessment alignment, the system cannot distinguish "not yet encountered" from "encountered but not mastered."

- **paper_1:§6 (assessment design section)** — "PDGs are also useful for assessment design. If a graph treats 'historical perspective taking' or 'disciplinary meaning of text' as a threshold, then assessment tasks should check for those competencies directly rather than only testing downstream essay performance. Concept-map research is valuable here because it treats mapping not only as instruction but as an assessment of connected understanding, while history-education research shows that mapping tasks can reveal causal and argumentative reasoning processes that ordinary summaries may hide."
  - **Paideia applicability:** Two distinct assessment-design implications: (1) threshold nodes need threshold-specific diagnostics (not proxy measures), and (2) concept-map elicitation can itself function as a formative assessment in Paideia — asking students to draw their understanding of a subgraph reveals relational comprehension that a multiple-choice item cannot.

- **paper_1:§4 (schema table)** — "Assessment task" is a node type in the recommended taxonomy. Assessment nodes are first-class citizens in the graph, not metadata attached to content nodes.
  - **Paideia applicability:** The Paideia graph could include assessment-task nodes linked to content nodes via `assessed_before` or `assessed_via` edges. This allows the teaching app to navigate to an assessment node when the content node is marked as requiring diagnostic verification before advancement.

- **paper_2:§Workflow table** — The "adaptive branching lesson" workflow makes assessment explicit: "Student completes diagnostic task → LLM scores diagnostic task using rubric linked to PDG nodes → Mastery sufficient? → [No] Route to unmet prerequisite node, Generate targeted scaffold / [Yes] Advance to comparison task."
  - **Paideia applicability:** This is the core adaptive loop. Every prerequisite edge must have a corresponding diagnostic item; without one, the adaptive branching cannot fire. The minimum viable teaching app requires: for each edge, one scored diagnostic question. The Kant-to-phenomenology workflow diagram makes this concrete: the rubric is linked to PDG nodes, not to a generic competency taxonomy.

- **paper_2:§Implementation** — "Attach at least one diagnostic task to every node that can plausibly function as a prerequisite." Stated as a minimum implementation requirement before deploying adaptive branching.
  - **Paideia applicability:** A Phase 6 diagnostic-coverage audit should enumerate all prerequisite edges in the current Paideia graph and count how many have an attached diagnostic item. Zero-coverage nodes are blocked from being used in adaptive routing until covered. This is the minimum gate before Phase 7 teaching-app build begins.

- **paper_2:§Node schema** — Required node fields include `assessment_items` and `mastery_evidence`. The explicit rationale: "Lets the LLM explain the node, generate aligned examples, distinguish threshold concepts from background context, and ground outputs in approved sources rather than free-form recall." Without `assessment_items`, the LLM cannot generate targeted diagnostic questions for the node.
  - **Paideia applicability:** `assessment_items` population can be LLM-assisted: given a node's `label`, `node_type`, and `misconceptions`, the LLM can draft candidate diagnostic items for instructor review. This is a feasible Phase 6 enrichment workflow before full human authoring of assessment items.

---

### L2.13 — Goal-relative path selection

- **paper_1:§4 (construction workflow)** — "Dependency claims are meaningful only relative to desired performances: the prerequisites for 'identify key phenomenological themes in a short passage' are not the same as those for 'compare Kantian and Husserlian transcendental philosophy in a research essay.' Constructive alignment and backward design both insist that outcomes and assessment should drive teaching sequence, not the reverse."
  - **Paideia applicability:** The path-selector in the teaching app must accept a learning-goal parameter. Two students both arriving at "Husserl's transcendental turn" will receive different prerequisite paths depending on whether their goal is (a) close reading of a phenomenological text vs (b) comparative essay on Kantian and Husserlian transcendentalism. The graph needs `learning_outcome`-parameterized edges, or the path-selector needs a goal→edge-weight lookup table.

- **paper_1:§5 (Kant/phenomenology case study)** — The table entry: "Soft/conditional: selected Kantian ideas may become helpful or important later, but full Kantian epistemology is not a universal entry requirement." The soft/conditional classification is explicitly goal-relative: when the outcome shifts from "introductory phenomenology" to "Husserl's transcendental turn compared to Kant," the same Kant nodes move from optional to important.
  - **Paideia applicability:** This is the canonical case for goal-relative path selection in Paideia's content domain. The Kant → Husserl edges in the graph should have a `necessity_level_by_outcome` attribute: `{introductory_phenomenology: "optional", transcendental_comparison: "recommended", full_Kantian_heritage: "required"}`.

- **paper_2:§A humanities-specific implication (full section)** — "If the outcome is 'explain why Husserl's transcendental phenomenology is not just empirical psychology,' then high-value prerequisites may include the idea of a transcendental inquiry into conditions of objectivity, the distinction between taking the world naively and suspending assumptions in analysis, and a first pass at intentionality and psychologism. If the outcome is instead 'compare Husserl's transcendental idealism with Kant's,' then broader Kantian machinery becomes more central. The pedagogical dependency path is therefore goal-relative, whereas the influence path is not."
  - **Paideia applicability:** Paper 2 provides the most explicit statement of goal-relative path selection. "Goal-relative" is the definitional distinguisher between a PDG and an influence map. The teaching app's path-selector must operationalize this: for the first goal, the prerequisite set is {transcendental inquiry, naive-vs-suspended stance, intentionality, psychologism}; for the second goal, {Kantian transcendental idealism, conditions of experience, appearance/thing-in-itself} are added. Different inputs → different paths through the same graph.

- **paper_2:§A humanities-specific implication (Saussure/Derrida and Austin cases)** — "In literary studies, an influence map may show Saussure → structuralism → Derrida, but a PDG for a first encounter with deconstruction may prioritize 'signifier/signified,' 'binary opposition,' 'instability of textual meaning,' and 'close reading of tensions in the text' rather than full coverage of structuralist schools. In rhetoric/philosophy of language, an influence map may show Austin → later speech-act theorists, while a PDG for analyzing performatives may first require 'utterances can do actions,' 'locution/illocution/perlocution,' and 'contextual felicity conditions.'"
  - **Paideia applicability:** Both cases show the goal-relative selection operating at sub-author granularity. For the Derrida goal "first encounter with deconstruction," the prerequisite set is {signifier/signified, binary opposition, textual instability} — not "all of structuralism." For the performativity goal, it is {performative utterance, locution/illocution/perlocution, felicity conditions} — not "all of Austin." The path-selector should operate at this granularity, which requires the Paideia graph to have sub-author nodes for these specific concepts.

- **paper_2:§Design patterns — adaptive branching** — "The student completes a diagnostic task aligned to PDG nodes; the LLM scores or summarizes the response against a rubric; the system updates mastery estimates; and the next activity is selected from graph neighbors whose prerequisites are satisfied." Graph traversal is constrained to satisfied prerequisites — but "satisfied" depends on what the downstream goal is.
  - **Paideia applicability:** The "graph neighbors whose prerequisites are satisfied" selection rule is implicitly goal-relative: which neighbors are available depends on which downstream target the student is headed toward. The adaptive-branching implementation must know the student's current goal to compute the relevant prerequisite satisfaction set.

---

## Cross-cutting observations

### 1. Goal-relativity is the master organizing principle — backward design, path selection, and edge-necessity all collapse to it

Papers 1 and 2 converge on a single structural insight: every pedagogical claim in a PDG is relative to a learning outcome. Backward design (L2.3) says outcomes drive sequence. Goal-relative path selection (L2.13) says the same edge has different necessity depending on the downstream goal. The expertise-reversal effect (L2.5) says the same scaffold is helpful or harmful depending on where the learner is relative to the goal. Cognitive load management (L2.11) says introduce elements one at a time relative to what the learner needs to do next. All five of these sub-concerns reduce to the same architectural requirement: the Paideia teaching app must accept a learning goal as input before making any scaffolding, routing, or sequencing decision. The single greatest risk in Phase 7 is building a path-selector that treats edges as goal-independent — that would reproduce exactly the influence-map conflation the papers most urgently warn against.

**Paideia implication:** Before writing any path-selection code, define the learning-goal taxonomy. Even a coarse three-level taxonomy (introductory reading / analytical essay / comparative research) would unlock goal-parameterized path selection and differentiate the teaching app from a simple graph traversal.

### 2. Unlearning and misconception remediation are structurally different from prerequisite gating — and require different teaching-app logic

Papers 1 and 2 both insist (L2.6, L2.7) that the dominant failure mode in humanities teaching is not missing content but active misconception: students who believe phenomenology is introspection, or that deconstruction means "anything goes," cannot be corrected by adding more content. The teaching app must implement an explicit unlearning/remediation sequence distinct from the standard prerequisite-check-and-advance loop. The recommender logic for a misconception node is: detect the misconception first (via a diagnostic item designed to surface it), then deliver the remediation sequence, then re-test, then advance. This is a different state machine from the standard "prerequisite satisfied → advance." Without this distinction, the teaching app will advance students who have passed a content check while still holding the misconception.

**Paideia implication:** Phase 7 architecture should include a misconception-detection/remediation module separate from the prerequisite-satisfaction check. The graph needs a `misconceptions` field populated for at least the highest-traffic threshold nodes before the module can fire.

### 3. The scaffolding fade and expertise-reversal problem requires a learner-state store, not just a graph — but a lightweight default can approximate it

Papers 1 and 2 are consistent that scaffolding must fade (L2.4) and that the same support can invert in helpfulness as expertise grows (L2.5). Both papers acknowledge that full learner-state tracking (knowledge tracing, mastery probability updating) is the proper solution but that it requires infrastructure the current Paideia project does not yet have. Paper 1 notes that even simple adaptive moves — optional primer modules, branching seminar prompts, differentiated annotation guides — can deliver most of the benefit without high-end automation. Paper 2's learner-state schema (`mastery_probability`, `evidence_count`, `recent_errors`) is the minimum viable model.

**Paideia implication:** The Phase 7 teaching app should implement a three-state scaffold model as a lightweight default: (0) first encounter → full scaffold (definition, worked example, contrast, formative question); (1) second encounter or mastery-estimated-passing → reduced scaffold (contrast and formative question only); (2) third encounter or high-confidence mastery → no scaffold (retrieval prompt only). This is implementable without a full knowledge-tracing system and matches the ZPD/fade trajectory requirement well enough to be pedagogically principled.

---

## Coverage report

- Sub-concerns with ≥1 finding: **13** / 13
- Sub-concerns with justified absence: none — all 13 sub-concerns have findings in one or both papers.

| Sub-concern | Paper 1 findings | Paper 2 findings | Total findings |
|---|---|---|---|
| L2.1 Threshold concepts | 4 | 2 | 6 |
| L2.2 Decoding the Disciplines | 3 | 2 | 5 |
| L2.3 Backward design | 3 | 2 | 5 |
| L2.4 Scaffolding fade trajectory | 3 | 2 | 5 |
| L2.5 Expertise reversal | 2 | 2 | 4 |
| L2.6 Misconception remediation | 3 | 2 | 5 |
| L2.7 Unlearning commonsense meanings | 3 | 2 | 5 |
| L2.8 Multiple-entry-routes | 3 | 2 | 5 |
| L2.9 Recursive revisiting | 3 | 1 | 4 |
| L2.10 Interdisciplinarity as bridge | 3 | 1 | 4 |
| L2.11 Cognitive load management | 4 | 1 | 5 |
| L2.12 Formative assessment alignment | 4 | 2 | 6 |
| L2.13 Goal-relative path selection | 2 | 3 | 5 |
| **Total** | **40** | **24** | **64** |
