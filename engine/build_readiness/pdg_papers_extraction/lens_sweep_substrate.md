# Lens sweep — Substrate / Schema

> **Filled by Phase C agent.** Re-reads BOTH papers end-to-end through the single lens of graph-level encoding (substrate / schema).
>
> Catches claims that the section-sequential Phase B agents may have under-tagged because the section's headline topic was different.
>
> **Coverage rule:** every sub-concern below must have findings OR an explicit `_No findings because…_` justification.

## Sources

- Paper 1: `/Users/shanekidd/Documents/Claude_Files/temp/Assessing the Utility of Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md` (~5,100 words; 178 lines)
- Paper 2: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md` (~5,200 words; 223 lines)

## Findings by sub-concern

### L1.1 — Edge type taxonomy beyond hard prerequisite

- **paper_1:L15** — The working research definition explicitly calls out that a PDG must be "broader than a strict prerequisite DAG, which matters because humanities learning often includes soft dependencies, contrastive links, and recursive revisiting."
  - **Paideia applicability:** Confirms the two-type current schema (`pedagogical_prerequisite` + `historical_influence`) is structurally insufficient; at minimum, soft prerequisite and contrastive link need separate edge types.

- **paper_1:L22–26 (table)** — The table "Typical edge meaning" in the PDG-vs-influence-map comparison enumerates: "Hard prerequisite, soft prerequisite, bridge, co-requisite, contrast, misconception-remediation" as distinct PDG edge semantics.
  - **Paideia applicability:** Direct taxonomy source for new edge types. Six named types, not two. Each carries distinct pedagogical meaning and should not be collapsed.

- **paper_1:L81** — The Kant/phenomenology discussion distinguishes a "soft or late-stage bridge" from a "universal front-end gate," asserting that encoding this difference is the practical value of the PDG.
  - **Paideia applicability:** `soft_prerequisite` and `helpful_bridge` are not synonymous; the Kant case shows a bridge can be stage-gated (useful only at a certain depth of study) — the edge schema may need a `stage` or `when_relevant` property in addition to edge type.

- **paper_1:L85–96 (Mermaid diagram)** — The sample Kant/phenomenology graph uses four visually distinct arrow types: solid arrows for hard prerequisites, dashed arrows labeled "helpful bridge," "compare and contrast," and "optional, potentially misleading if overextended." This is the only concrete worked example in Paper 1 and contains more edge-type nuance than the prose taxonomy.
  - **Paideia applicability:** "Optional, potentially misleading if overextended" is a schema claim buried in a case study: an edge can carry a *warning* flag about its own overuse — suggesting a `warning_note` or `misuse_risk` attribute per edge, not just an edge type label. This is easy to miss in section-sequential reading.

- **paper_1:L116–117 (schema table)** — The schema table lists edge semantics as: "Hard prerequisite; soft prerequisite; helpful bridge; co-requisite; contrastive link; remediation link; historical influence in separate layer."
  - **Paideia applicability:** Adds `remediation link` (not in the L22 table), and explicitly makes `historical influence` a *separate layer* rather than just another edge type. Seven distinct edge semantics named in this paper alone.

- **paper_2:L15** — Definitions and Scope section enumerates edge types explicitly: "prerequisite-for, supports, contrast-needed-before, example-of, common-misconception-about, assessed-before."
  - **Paideia applicability:** Three edge types here not in Paper 1's tables — `supports`, `example-of`, `assessed-before`. `assessed-before` is especially significant: it links assessment sequencing to graph topology, implying the PDG must encode which diagnostic tasks must precede which instructional nodes.

- **paper_2:L80–81 (node/edge schema table)** — Edge required fields include `edge_type` as a field, implying a controlled vocabulary. The surrounding prose in Paper 2 uses all six types from the L15 enumeration.
  - **Paideia applicability:** `edge_type` should be an enum column in Postgres, not free text, to enable filtering, analytics, and LLM constraint.

### L1.2 — Three-relation separation (pedagogical-dependence / conceptual-relatedness / historical-influence as layered)

- **paper_1:L17** — States explicitly: "Influence maps describe genealogy; PDGs describe instructional dependence. Conflating the two is one of the main sources of false prerequisites in humanities syllabi."
  - **Paideia applicability:** The two layers Paideia already has (`pedagogical_prerequisite` + `historical_influence`) cover relation types 1 and 3. Paper 1 names a third — *conceptual relatedness* — that is distinct from both.

- **paper_1:L31** — "A useful design rule follows from this distinction: keep historical influence and pedagogical dependence in separate graph layers. Doing so preserves intellectual history without turning it automatically into curricular order."
  - **Paideia applicability:** ADR 0061 product already enacted the `historical_influence` layer split, so this confirms that decision. The new gap is that conceptual relatedness (Saussure/signifier-signified as *related* without being a hard prerequisite) has no layer at all in the current schema.

- **paper_2:L19** — Explicitly names all three as a triple: "Historical influence is about who influenced whom. Conceptual relatedness is about ideas that belong together in analysis. Pedagogical dependence is about what a learner must grasp first to succeed at a specific task."
  - **Paideia applicability:** This is the clearest statement of the tripartite distinction in either paper. It establishes that `conceptual_relatedness` is a semantically distinct relation requiring its own edge type or layer — not a soft synonym for `pedagogical_prerequisite`.

- **paper_2:L64** — The literary-theory example (Saussure → structuralism → Derrida) shows the influence-map path, then the PDG ask: "which concepts students need in order to perform structurally informed and then post-structural reading." This is a worked demonstration that the same historical chain produces a different, finer-grained pedagogical path.
  - **Paideia applicability:** In Paideia's existing graph, Saussure/Derrida edges may exist as `pedagogical_prerequisite` derived from the historical lineage — a false-prerequisite risk. The three-layer model would let Paideia encode the influence chain as `historical_influence`, the conceptual cluster as `conceptual_relatedness`, and only the fine-grained pedagogically-needed elements as `pedagogical_prerequisite`.

### L1.3 — Goal-relative dependency strength

- **paper_1:L110** — States the construction principle directly: "dependency claims are meaningful only relative to desired performances: the prerequisites for 'identify key phenomenological themes in a short passage' are not the same as those for 'compare Kantian and Husserlian transcendental philosophy in a research essay.'"
  - **Paideia applicability:** Edges must be parameterizable by `learning_outcome`. The current schema has a single edge with no outcome field — this is a structural gap, not just a missing property.

- **paper_1:L79** — The Kant/phenomenology case study distinguishes: introductory phenomenology (intentionality, epoché) vs. Husserl's transcendental turn (where Kantian distinctions become "a powerful bridge"). The graph encodes this as a soft/late-stage edge, not a hard gate — but the *reason* is goal-relative.
  - **Paideia applicability:** The case study demonstrates that goal-relativity can be *partially* encoded via edge type (hard vs soft/bridge) but fully requires an explicit `learning_outcome` or `course_level` parameterization on each edge. Edge type alone cannot express "only needed when the goal is X."

- **paper_2:L62** — "The pedagogical dependency path is therefore goal-relative, whereas the influence path is not." Illustrated with two outcome variants: "explain why Husserl's transcendental phenomenology is not just empirical psychology" (narrow prereqs) vs. "compare Husserl's transcendental idealism with Kant's" (broader Kantian machinery needed).
  - **Paideia applicability:** This is the clearest operationalization of L1.3 in either paper. The edge schema needs either (a) a `necessity_level` keyed to a `learning_outcome` foreign key, or (b) duplicate edges per distinct outcome with different `necessity_level` values. Option (a) is a more complex relational design but avoids edge proliferation.

- **paper_2:L81 (edge schema table)** — `necessity_level` is listed as a required edge field, confirming that goal-relative parameterization is intended to be encoded per-edge, not just inferred from context.
  - **Paideia applicability:** Add `necessity_level` (enum: `required`, `recommended`, `historical_contextual_only`) as a non-nullable edge field. Consider a companion `learning_outcome_id` FK to an outcomes table.

### L1.4 — Confidence model (expert / trace / LLM / disagreement_flag)

- **paper_1:L112** — The six-stage construction workflow lists "assign edge semantics and confidence levels" as step four, before attaching assessments and misconceptions.
  - **Paideia applicability:** Confidence is a first-class field at edge construction time, not a later annotation. This implies it should be non-nullable with a default (e.g., `low`) rather than optional.

- **paper_1:L118 (schema table)** — Confidence level row: "High, medium, low, with rationale and source basis." The rationale+source clause implies confidence is not a standalone scalar but a composite with provenance.
  - **Paideia applicability:** A single confidence enum is insufficient; the schema should carry `confidence_level` (enum) plus a `confidence_rationale` text field — or link to the provenance record (L1.5).

- **paper_1:L162** — Risks section: "The mitigation is straightforward: encode confidence levels, separate hard from soft edges, validate graphs with actual student work, and revise them when learners succeed through routes the graph did not predict."
  - **Paideia applicability:** This appears in the *risks section*, not the schema table. The paper treats confidence as a contestability/safety mechanism (not just metadata), implying it must be surfaced in the UI, not buried in the DB.

- **paper_2:L82 (confidence model row in schema table)** — Defines explicitly: "`expert_confidence`, `trace_confidence`, `llm_confidence`, `disagreement_flag`." Four fields, not one scalar. Commentary: "Prevents silent overclaiming and allows differential treatment of authoritative versus provisional edges."
  - **Paideia applicability:** This is the most specific schema definition in either paper. The three-source model (expert judgment, learner trace inference, LLM proposal) maps to three independent columns. `disagreement_flag` is a derived boolean or enum. All four should be columns on the edge table.

- **paper_2:L113–114 (Mermaid workflow diagram)** — The workflow shows "Low-confidence edge flagged: Full Kantian system → Husserl essentials" as a distinct node in the graph-review flow — the instructor sees and must approve or reject it. This is operational evidence that LLM-sourced low-confidence edges need a special routing state, not just a column value.
  - **Paideia applicability:** The edge table needs a `review_status` field (enum: `approved`, `pending_review`, `rejected`, `provisional`) in addition to the three confidence dimensions, so that low-confidence edges can be held in a review queue before affecting student routing.

### L1.5 — Provenance per edge

- **paper_1:L112–113** — The sixth construction stage is "revise the graph with empirical evidence from student performance, concept-map artifacts, or learning analytics" — implying that edges need provenance fields to distinguish original-author claims from empirically-revised claims.
  - **Paideia applicability:** Without provenance, revision history is invisible. Each edge revision needs at minimum a `revised_by` and `revision_rationale`.

- **paper_2:L83 (provenance record row in schema table)** — Lists required provenance fields per edge: "`source_text`, `course_context`, `version`, `reviewer`, `rationale`." Commentary: "Essential for auditability, contestability, and revision history in interpretive subjects."
  - **Paideia applicability:** Five distinct provenance fields. `source_text` is the excerpt or citation justifying the edge claim. `course_context` is the specific course/cohort in which the edge was validated. `version` enables edge versioning. `reviewer` is the human who approved. `rationale` is a free-text justification. None of these exist in Paideia's current schema.

- **paper_2:L74** — Trace-informed graph revision pattern: "LLMs can accelerate the search for candidate revisions, but only if every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow."
  - **Paideia applicability:** Provenance is framed here as a prerequisite for LLM-assisted revision to be safe — not optional metadata. This appears in the design-patterns section, not the schema table, and could be missed in section-sequential extraction.

- **paper_2:L95 (workflows table, bottom row)** — "No graph update occurs without expert sign-off and stored rationale." The phrase "stored rationale" is a provenance field requirement expressed as a governance rule.
  - **Paideia applicability:** Provenance is an invariant, not a best practice. The approval workflow described implies the DB transaction that approves an edge also writes the provenance record atomically.

### L1.6 — Provenance per node

- **paper_1:L114–116 (schema table)** — No explicit node-provenance row in the Paper 1 schema table, but the table includes "Outcome alignment: Which assignment, discussion move, or exam item the node supports." This is a functional provenance claim — the node's educational justification.
  - **Paideia applicability:** Partial signal only. Paper 1 doesn't name `canonical_sources` or `approved_examples` as node fields.

- **paper_2:L80 (node schema table row)** — Node required fields include: "`canonical_sources`, `approved_examples`, `misconceptions`, `assessment_items`, `mastery_evidence`, `accessibility_notes`." Commentary: "Lets the LLM explain the node, generate aligned examples, distinguish threshold concepts from background context, and ground outputs in approved sources rather than free-form recall."
  - **Paideia applicability:** `canonical_sources` is a list of citations/excerpts grounding the node's definition. `approved_examples` is a curated list of instances the LLM may use. `mastery_evidence` defines what counts as evidence that a student has mastered this node. These three fields together constitute node-level provenance and are entirely absent from the current Paideia schema.

- **paper_2:L68** — The instructor-authored core pattern: "instructors or discipline teams define the canonical nodes, edge types, learning outcomes, and approved evidence." "Approved evidence" is a node-level provenance concept — who approved what counts as evidence for this node.
  - **Paideia applicability:** This appears in the design-patterns section, not the schema table. The implication is that `approved_examples` and `mastery_evidence` are not just DB columns — they have an approval workflow, just like edges.

### L1.7 — Counterexamples as edge attribute

- **paper_1:L85–96 (Mermaid diagram, node H)** — "Appearance and thing-in-itself distinction — optional, potentially misleading if overextended → E [Husserl's transcendental turn]." The label "potentially misleading if overextended" is a built-in counterexample signal: this edge works in some directions but creates misconceptions if pushed too far.
  - **Paideia applicability:** This is the only concrete worked counterexample in Paper 1, and it appears in a diagram caption, making it easy to miss. It implies that `counterexamples` is not a separate node type but a field on the edge itself — "here is how relying on this dependency can backfire."

- **paper_2:L74** — Trace-informed graph revision: "LLMs can accelerate the search for candidate revisions, but only if every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow." "Contrary evidence" is a synonym for counterexamples on the edge.
  - **Paideia applicability:** This appears in a design-patterns paragraph, not the schema table. The term "contrary evidence" suggests the field should store citations or student-trace evidence that the edge is weaker or narrower than claimed — not just freeform warnings.

- **paper_2:L81 (edge schema table)** — Edge required fields include `counterexamples` explicitly: "Makes prerequisite claims contestable and reviewable; supports low-confidence flagging and assessment alignment."
  - **Paideia applicability:** `counterexamples` is named as a required edge field, not optional metadata. In a Postgres schema this could be a text array or a FK to a `counterexample_evidence` table if structured storage is needed.

### L1.8 — Misconception encoding

- **paper_1:L43** — Threshold-concepts section: "PDGs are well suited to this terrain because they can represent not only 'knowing X before Y' but also 'unlearning a commonsense meaning before a disciplinary meaning becomes available.'"
  - **Paideia applicability:** Unlearning-required-before is a distinct edge type (not a property) — it encodes that a student must actively discard a prior belief as a prerequisite step. This edge type is named in L1.1 but the justification is here in the threshold-concept section, easy to miss.

- **paper_1:L126** — Implementation section: "encode misconception nodes explicitly — for example, 'phenomenology = introspection,' 'deconstruction = anything goes,' or 'historical perspective = sympathy with the past' — because many humanities bottlenecks are caused by misleading prior understandings rather than by absent content."
  - **Paideia applicability:** Misconceptions are named as **nodes**, not just edge annotations. This implies a `misconception` node type that can be the source of a `misconception-remediation` edge pointing to the correct concept. The current Paideia schema has no misconception encoding at all.

- **paper_2:L15** — Edge type enumeration includes `common-misconception-about` as a named edge type.
  - **Paideia applicability:** `common-misconception-about` means a misconception node has an edge pointing at the concept it misrepresents — distinct from a `misconception-remediation` edge that points from the correct concept back to what students must unlearn. These are different directional relationships and should be separate edge types.

- **paper_2:L80 (node schema table)** — Node required fields include `misconceptions` as a field on every node: "Lets the LLM explain the node, generate aligned examples, distinguish threshold concepts from background context."
  - **Paideia applicability:** This creates two encoding options: (a) misconceptions as a property of the target node (a list/text field), or (b) misconceptions as standalone nodes with typed edges. Both papers support option (b) as the richer encoding; option (a) is the lightweight alternative for migration.

- **paper_2:L186** — Risks section: "The most dangerous failure is often a false prerequisite or an omitted prerequisite, because it silently changes the learning path." This appears in a governance/risks section but contains a schema implication: misconceptions must be encoded so the system can distinguish "student has misconception X" from "student lacks concept Y" — different remediation paths.
  - **Paideia applicability:** Learner-state schema (L1.15) must distinguish `missing_concept` from `active_misconception` states — this difference is invisible if the graph has no misconception nodes.

### L1.9 — Threshold-concept tag on nodes

- **paper_1:L11** — Executive summary: PDGs are most useful when "they encode both hard and soft dependencies, alternative entry paths, and likely misconceptions." Threshold concepts are named throughout as the primary mechanism for identifying which nodes are transformative bottlenecks.
  - **Paideia applicability:** Threshold concept status is a distinct property, not just a node type — a node can be a threshold concept regardless of whether it is a "bridge concept" or "disciplinary practice."

- **paper_1:L43–44** — Threshold-concepts section: "Meyer and Land argue that some concepts are transformative and troublesome and that learners may struggle to progress without them." The PDG is described as well-suited to represent these.
  - **Paideia applicability:** `threshold_concept: bool` or a richer tag (`threshold_concept_type` enum: `transformative`, `troublesome`, `irreversible`, `integrative`, `bounded`, `reconstitutive`) based on Meyer & Land's original taxonomy. The minimal version is a boolean; the fuller version supports more nuanced pedagogical routing.

- **paper_2:L80 (node schema table)** — Node required fields include `threshold_concept?` with a `?` indicating a nullable boolean. Commentary: "Lets the LLM...distinguish threshold concepts from background context."
  - **Paideia applicability:** Paper 2 confirms the nullable boolean is the recommended minimal encoding. The `?` notation signals it is optional per node but should be explicit (not absent). Add `is_threshold_concept boolean` to the node table.

- **paper_2:L44** — The Decoding the Disciplines section: "Corrigan's argument that students must cross threshold concepts around text, meaning, context, form, and reading is almost a template for node construction in a humanities PDG."
  - **Paideia applicability:** This appears in the pedagogical rationale section but has a schema implication: the threshold-concept tag on nodes should be populated by a Decoding interview process, not inferred from the edge structure. Provenance for the threshold-concept tag matters — who identified this as a threshold and when.

### L1.10 — Node-type taxonomy

- **paper_1:L114–116 (schema table)** — Node type row lists eight types: "Threshold concept; bridge concept; disciplinary practice; text/excerpt; historical context; misconception; comparative lens; assessment task." Rationale: "Humanities learning depends on interpretive moves and disciplinary habits, not just facts."
  - **Paideia applicability:** This is the most complete node-type taxonomy in either paper. The current Paideia graph has no `node_type` column at all. All 380 nodes are implicitly treated as the same kind of thing. Adding an enum `node_type` with these eight values is the highest-leverage single schema change.

- **paper_2:L80 (node schema table)** — Node required fields include `node_type` and `disciplinary_domain` as separate fields. Commentary: "Lets the LLM explain the node...distinguish threshold concepts from background context."
  - **Paideia applicability:** `disciplinary_domain` is a separate field from `node_type` — a `threshold concept` node can belong to philosophy, literary theory, history, etc. This cross-axis matters for interdisciplinary courses and for filtering/querying the graph.

- **paper_1:L102–103** — The literary theory section adds: "Saussurean notions like signifier/signified and langue/parole can function as bridge concepts." Bridge concept is explicitly named as a node type here in a case study, not just the schema table.
  - **Paideia applicability:** Bridge concept is a learner-facing pedagogical label — it tells students "this is scaffolding, not a terminal destination." The node type should be surfaced in the student-facing UI, not hidden.

- **paper_1:L106** — The history section: "The pedagogical thresholds that help students 'think historically' are different: use of primary evidence, continuity and change, cause and consequence, perspective, and ethical interpretation." These are `disciplinary practice` nodes.
  - **Paideia applicability:** This case study confirms that `disciplinary practice` is a substantively different node type from a threshold concept — practices are skills enacted, not ideas crossed. The distinction affects how mastery evidence is designed.

### L1.11 — Audience/cohort tags

- **paper_1:L39** — Expertise reversal section: "PDGs should encode confidence levels and adaptive fading. A dependency that is 'hard' for novices may become optional for advanced students, and a graph that cannot be adjusted by cohort will not remain pedagogically valid for long."
  - **Paideia applicability:** This appears in the learning-science foundations section, not the schema table. It establishes that audience/cohort tags are not just metadata for UI filtering — they change the *edge necessity_level* for a given cohort. The same edge may be `required` for `introductory` and `optional` for `advanced`.

- **paper_1:L119 (schema table)** — Audience tag row: "Introductory; intermediate; advanced; majors/non-majors; multilingual cohort." Rationale: "Dependencies vary by learner profile and prior preparation."
  - **Paideia applicability:** The schema table places audience tags at the node level, but the earlier prose (L39) implies they need to be at the edge level too — or the `necessity_level` on the edge needs to be a per-cohort lookup, not a single value.

- **paper_2:L202** — Instructor workflow section: "mark edge necessity as required, recommended, or historical/contextual only" — and separately instructs: "during the term, instructors should...examine whether branches are disproportionately burdening specific groups or language backgrounds." This monitoring task presupposes that the graph carries cohort-level data, not just aggregate edge necessity.
  - **Paideia applicability:** This appears in the implementation section, not the schema table. The audit capability implies `audience_tag` must be stored in a way that supports per-subgroup querying — a simple enum column on the node may not be sufficient if the same node is `introductory` for one cohort and `background context` for another.

### L1.12 — Granularity tag

- **paper_1:L112** — Construction workflow step three: "Choose graph granularity: overly coarse graphs hide real obstacles, but overly fine graphs become unteachable."
  - **Paideia applicability:** Granularity is named as a design decision made during construction, but neither paper explicitly encodes it as a node-level field in the way that `node_type` or `audience_tag` are. This is a relative rather than absolute property.

- **paper_2:L80 (node schema table)** — Node required fields include `granularity` explicitly, alongside `node_type` and `disciplinary_domain`.
  - **Paideia applicability:** Paper 2 encodes granularity as a per-node field. Reasonable values: `coarse` (whole tradition or period), `medium` (key concept or method), `fine` (specific distinction or move). Add `granularity` as an enum column on the node table.

- **paper_2:L202** — Instructor workflow: "Define node granularity at the level of teachable, assessable units rather than whole books or authors whenever possible." This appears in the implementation section — reinforcing that granularity is a construction discipline, not just a post-hoc label.
  - **Paideia applicability:** The 380 current nodes are at mixed granularity (some are philosophers, some are specific distinctions). A `granularity` column would expose this variance and support quality review.

### L1.13 — Equity metadata per node

- **paper_1:L121 (schema table)** — Equity metadata row: "Assumed background knowledge, jargon load, culturally specific references." Rationale: "Helps surface hidden barriers and avoid reproducing gatekeeping norms."
  - **Paideia applicability:** Three distinct equity-relevant fields: (1) `assumed_background` (what the instructor silently assumes students know), (2) `jargon_load` (rating or list of field-specific terms), (3) `cultural_specificity` (whether the node assumes familiarity with a particular cultural tradition). None exist in the current schema.

- **paper_1:L160** — Risks section: "If the graph assumes one canonical route through a tradition, it may reproduce disciplinary gatekeeping — for example, by silently privileging European conceptual histories, elite genres, or jargon-heavy formulations as the only valid entry point. The risk is not unique to PDGs, but PDGs can make it visible if instructors deliberately tag nodes for assumed background, cultural specificity, and alternatives."
  - **Paideia applicability:** This is a second statement of the equity metadata need, appearing in the risks section rather than the schema table — the safety-net lens catches it here. The phrase "tag nodes" confirms these are per-node fields.

- **paper_2:L80 (node schema table)** — `accessibility_notes` is listed as a node required field. Commentary is under the LLM-integration column but the field is clearly equity-relevant.
  - **Paideia applicability:** `accessibility_notes` is the Paper 2 term for what Paper 1 calls equity metadata. They are complementary: Paper 1 focuses on cultural-gatekeeping risk; Paper 2 focuses on accessibility in the technical/disability sense. Both should be captured.

- **paper_2:L188** — Bias and cultural-risk section: "store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."
  - **Paideia applicability:** "Tradition labels" is an equity-adjacent schema field — tagging which intellectual tradition a node primarily represents (e.g., `Western analytic`, `Continental`, `Postcolonial`, `Feminist`). This would allow bias audits across tradition coverage.

### L1.14 — Version history per node and per edge

- **paper_1:L122 (schema table)** — Version history row: "Date, course, cohort, revision notes." Rationale: "Lets the graph improve over time instead of becoming canonical."
  - **Paideia applicability:** Four version fields named. The "instead of becoming canonical" rationale is critical — version history is not just auditing; it signals to future sessions that the graph is *revisable* rather than authoritative.

- **paper_1:L130–131** — Instructor workflow: "Draft the graph before the course; expose a student-friendly subset during the course; use formative assessments and discussion transcripts to see where the graph over- or under-predicts difficulty; then revise." The revision cycle implies version history without naming it as a schema field.
  - **Paideia applicability:** This appears in the implementation section, not the schema table. The revision cycle creates a need for version history at the *graph level* (which version of the PDG is active for which course/cohort), not just per-node or per-edge.

- **paper_2:L83 (provenance record row)** — `version` is listed as a required provenance field per edge: "`source_text`, `course_context`, `version`, `reviewer`, `rationale`."
  - **Paideia applicability:** Per-edge `version` is separate from graph-level versioning. In practice this implies either (a) an edge audit table with timestamps, or (b) an explicit `version` integer column on edges plus an archive table for prior states.

- **paper_2:L136–138 (Mermaid workflow diagram)** — Workflow nodes include "Update PDG version" (when instructor approves graph edits) and "Store suggestion as unresolved" (when rejected). This is schema-level evidence that graph version management needs a `version` identifier and a `pending_suggestion` state for rejected edits.
  - **Paideia applicability:** This appears in the workflow diagram, not the schema table — a prime candidate for under-tagging in section-sequential extraction. It implies the graph needs a `pdg_versions` table linking version identifiers to the active edge/node sets for a given course/cohort.

### L1.15 — Learner-state schema separate from graph

- **paper_1:L39** — Expertise reversal section: "A dependency that is 'hard' for novices may become optional for advanced students, and a graph that cannot be adjusted by cohort will not remain pedagogically valid for long." Implies learner state must feed back into edge necessity evaluation.
  - **Paideia applicability:** Learner state is not just a separate table — it must be queryable alongside graph structure to determine *which edges apply* to a given learner at a given moment.

- **paper_2:L84 (learner state row in schema table)** — Defines learner state fields: "`mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`, `language_preference`." Commentary: "Helps the LLM choose explanation depth, detect potential expertise reversal, and adapt questioning."
  - **Paideia applicability:** Five named fields. `mastery_probability` is a float (0–1), not a boolean — this implies a knowledge-tracing model, not just a pass/fail mastery flag. `evidence_count` tracks how many interactions contributed to the estimate. `recent_errors` is a list or count of recent error types. `help_seeking_pattern` and `language_preference` are behavioral/accessibility fields. All five belong in a separate `learner_state` table, not in the graph tables.

- **paper_2:L72** — Adaptive-branching pattern: "The student completes a diagnostic task aligned to PDG nodes; the LLM scores or summarizes the response against a rubric; the system updates mastery estimates; and the next activity is selected from graph neighbors whose prerequisites are satisfied."
  - **Paideia applicability:** This appears in the design-patterns section. The phrase "updates mastery estimates" makes learner state a *writable* table, not just a read-only record. The write path must be gated (the system updates, not the LLM directly) and audited.

- **paper_2:L40** — "A static syllabus often cannot respond to that dynamic, but an LLM conditioned on a PDG can, in principle, give heavier support on fragile prerequisite nodes and then fade support as mastery increases."
  - **Paideia applicability:** This is in the "Why the Combination Is Pedagogically Plausible" section, not the schema table. It reinforces that the learner-state schema drives LLM behavior at runtime — `mastery_probability` per node is the key input to the adaptation decision.

### L1.16 — Assessment linkage per node

- **paper_1:L112** — Construction workflow step five: "Attach assessments and likely misconceptions to nodes and edges."
  - **Paideia applicability:** Assessments are attached at construction time, not as an afterthought. The construction step sequence implies they are a first-class element of the node schema.

- **paper_1:L114–116 (schema table)** — Outcome alignment row: "Which assignment, discussion move, or exam item the node supports." This is the Paper 1 version of assessment linkage.
  - **Paideia applicability:** The Paper 1 framing is about the node *supporting* an outcome (the node → outcome direction). Paper 2 adds the reverse: an assessment task *assessing* whether a node is mastered (assessment → node direction). Both directions matter.

- **paper_2:L80 (node schema table)** — Node required fields include `assessment_items` and `mastery_evidence`. Commentary: "Lets the LLM explain the node...ground outputs in approved sources."
  - **Paideia applicability:** `assessment_items` is a list of diagnostic items/tasks linked to this node. `mastery_evidence` defines what counts as satisfactory performance. In a relational schema, `assessment_items` should be a FK to an `assessments` table, not a text array, to enable analytics.

- **paper_2:L81 (edge schema table)** — Edge required fields include `assessment_link`. Commentary: "Makes prerequisite claims contestable and reviewable; supports low-confidence flagging and assessment alignment."
  - **Paideia applicability:** Assessment linkage exists at both the node level (`assessment_items`) and the edge level (`assessment_link`). The edge-level link is the specific diagnostic that verifies whether the prerequisite condition has been met — not the same as the node-level assessment that checks mastery of the concept itself.

- **paper_1:L136** — Assessment design section: "If a graph treats 'historical perspective taking' or 'disciplinary meaning of text' as a threshold, then assessment tasks should check for those competencies directly rather than only testing downstream essay performance."
  - **Paideia applicability:** This appears in the pedagogical implications section. It implies that nodes tagged as threshold concepts need *threshold-specific* assessment items, not just general topic assessments — a domain integrity rule that the schema should support.

### L1.17 — Temporal / fade trajectory per scaffolding edge

- **paper_1:L39** — Expertise reversal section: "PDGs should encode confidence levels and adaptive fading. A dependency that is 'hard' for novices may become optional for advanced students."
  - **Paideia applicability:** The paper frames fading as a *graph property*, not just an instructional behavior. This implies the edge schema needs a mechanism to encode when a dependency should fade — either a `fade_at` field keyed to learner expertise level, or a separate `scaffolding_edges` table with temporal logic.

- **paper_1:L41** — Scaffolding section: "Not as a gatekeeping machine, but as a scaffold planner that tells instructors where modeling, worked examples, collaborative talk, or comparative framing are most needed and when those supports should be withdrawn."
  - **Paideia applicability:** "When those supports should be withdrawn" is a temporal claim about scaffolding edges. This appears in a theoretical section about Vygotsky/scaffolding, not the schema table — a prime example of a schema claim buried in a non-substrate section.

- **paper_1:L57** — Literary evidence section: "These studies imply that a good PDG should not only state dependencies but also indicate when supports tied to those dependencies should fade."
  - **Paideia applicability:** The Shakespearean-text and writing-to-learn studies provide empirical grounding for the fade trajectory. The schema implication: edges marked as `soft_prerequisite` or `helpful_bridge` should carry a `fade_condition` or `fade_at_expertise_level` field.

- **paper_2:L40** — "An LLM conditioned on a PDG can, in principle, give heavier support on fragile prerequisite nodes and then fade support as mastery increases."
  - **Paideia applicability:** This is in the pedagogical rationale section. The phrase "fragile prerequisite nodes" implies that nodes, not just edges, need a `fragility` indicator — a node that many students struggle with even after formal mastery deserves sustained support during the fade window.

### L1.18 — Alternative-entry-route support

- **paper_1:L11** — Executive summary: PDGs "encode both hard and soft dependencies, alternative entry paths, and likely misconceptions."
  - **Paideia applicability:** Alternative entry paths are named at the opening definitional level — not a secondary feature but a core design requirement.

- **paper_1:L45** — Cognitive-flexibility section: "A good humanities PDG should illuminate where dependencies are real while preserving multiple routes, contrastive cases, and later reorganization of the graph as understanding deepens."
  - **Paideia applicability:** This is in the learning-science section about Spiro's cognitive flexibility, not the schema table. The schema implication: nodes must support multiple in-edges of different types (e.g., a concept can be reached via a `conceptual` entry, a `case-based` entry, or a `methodological` entry) and the graph must not enforce a single canonical path.

- **paper_1:L126** — Implementation: "Preserve multiple routes into complex topics. Spiro's work on ill-structured domains suggests that one-lens sequencing is dangerous; a good PDG should therefore allow case-based, conceptual, methodological, and historical entry points that later converge."
  - **Paideia applicability:** Four named alternative entry-route types: case-based, conceptual, methodological, historical. These could be encoded as an `entry_route_type` attribute on edges pointing *into* a given node — allowing the query "what are all the legitimate paths to reach this concept?"

- **paper_2:L188** — Bias/equity section: "store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."
  - **Paideia applicability:** This appears in the governance/equity section, not the schema table — a substrate claim embedded in an equity framing. "Multiple legitimate entry routes" is both a pedagogical value and a schema requirement: the graph must have a mechanism for labeling routes as `alternative` rather than treating any single path as the canonical one.

- **paper_2:L200** — Syllabus integration: "Students do not need the entire back-end ontology. They need the current local neighborhood: the target node, its immediate prerequisites, common misconceptions, upcoming assessments, and alternative routes if they are stalled."
  - **Paideia applicability:** This appears in the implementation section. "Alternative routes if they are stalled" implies that alternative-entry-route support is a runtime query, not just a design property — the system must be able to find and serve alternative paths on demand for a given learner state. The schema must make this query efficient (e.g., an index on `entry_route_type` or a pre-computed alternative-paths view).

---

## Cross-cutting observations

### 1. Every contestable claim requires three concurrent properties: confidence + provenance + counterexamples

Across both papers, the recommendations for confidence (L1.4), provenance per edge (L1.5), and counterexamples (L1.7) are never proposed in isolation — they always appear together when the papers discuss how to make the graph auditable, revisable, or governable. Paper 2 makes this explicit: "every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow" (L74). The underlying meta-pattern is *contestability as a first-class graph property*, not a monitoring afterthought. For Paideia's schema design, this means these three fields should be added as a unit — adding confidence without provenance produces a number with no traceable basis; adding provenance without counterexamples produces a one-sided record. The three constitute an atomic contestability bundle.

### 2. Goal-relativity is the deepest structural gap: the same edge has a different meaning depending on learning outcome

The most significant substrate claim in either paper — stated explicitly in Paper 2 L62 and grounded in the Kant/phenomenology case study — is that edge necessity is *goal-relative*. The same edge (Kantian distinctions → Husserl's transcendental turn) is `required` when the outcome is "compare Husserl and Kant" and `optional` when the outcome is "explain phenomenological description." This cannot be adequately expressed by any single `edge_type` or `necessity_level` value without parameterizing on `learning_outcome`. The current Paideia schema has no learning outcomes table and no mechanism to attach outcome-relative necessity to edges. This is the most structurally far-reaching gap: it touches edge schema, learner-state schema, and the routing logic of any adaptive system.

### 3. Schema fields are ordered by lifecycle: some fields are authoring-time, some are review-time, some are runtime-adaptive

Both papers implicitly stratify schema fields by *when they are written*. Authoring-time fields (set when the graph is first built): `node_type`, `edge_type`, `granularity`, `audience_tag`, `threshold_concept?`. Review-time fields (set during the expert-review or trace-informed revision cycle): `confidence`, `provenance`, `counterexamples`, `version`. Runtime-adaptive fields (updated during live learner interactions): learner-state fields (`mastery_probability`, `evidence_count`, `recent_errors`). This lifecycle stratification has consequences for the Postgres schema: runtime-adaptive fields should be in a separate, high-write table (`learner_node_state`, not `pdg_nodes`), while authoring-time fields can be in a lower-write table with audit logging. Mixing all fields in a single node/edge table would create write-contention issues at scale and blur the boundary between the stable graph structure and the live learner model.

### 4. Misconception encoding requires both node-type and edge-type additions — neither alone is sufficient

Paper 1 (L126) names misconceptions as standalone nodes. Paper 2 (L15) names `common-misconception-about` as an edge type from a misconception node to the concept it misrepresents, and Paper 1 (L43) names `unlearning-required-before` as an edge type from a target concept back to the misconception that must be cleared. The full misconception sub-graph requires: (a) a `misconception` node type, (b) a `common-misconception-about` edge pointing from misconception → target concept, and (c) an `unlearning-required-before` edge pointing from the target-concept learning-task back to the misconception that blocks it. Without all three elements, the system cannot answer the learner-routing question "does this student have an active misconception that must be remediated before advancing?"

### 5. The case-study and diagram sections are the densest sources of schema claims — section-sequential extraction systematically under-retrieves from them

The Kant/phenomenology Mermaid diagrams in both papers (Paper 1 L85–96, Paper 2 L99–138) and the worked case studies (Paper 1 L77–106, Paper 2 L62–64) contain more concrete schema implications per line than the explicit schema tables. Examples: the "potentially misleading if overextended" edge annotation (diagram, Paper 1) implies a `warning_note` field; the "Low-confidence edge flagged" workflow node (diagram, Paper 2) implies a `review_status` enum; the "Store suggestion as unresolved" outcome (diagram, Paper 2) implies a pending-suggestions table. None of these appear in the schema tables. This confirms the value of the substrate-lens safety-net pass: the schema tables in both papers are necessary but not sufficient for full substrate extraction.

---

## Coverage report

- Sub-concerns with ≥1 finding: **18** / 18
- Sub-concerns with justified absence: **none** — all 18 sub-concerns have at least one finding from at least one paper.
- Notes:
  - L1.6 (provenance per node): Paper 1 has weak signal (outcome-alignment as functional provenance); Paper 2 is the primary source for `canonical_sources`, `approved_examples`, `mastery_evidence`.
  - L1.12 (granularity tag): Paper 1 names granularity as a construction decision but does not encode it as a node field; Paper 2 explicitly adds it to the node schema table.
  - L1.17 (fade trajectory): No paper names a specific schema field (e.g., `fade_at_expertise_level`); both papers assert the pedagogical requirement. The schema design for this sub-concern must be inferred from principle rather than directly specified.
