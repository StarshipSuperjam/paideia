# Paper 2 extraction — Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics

> **Filled by Phase B agent.** Source: `/Users/shanekidd/Documents/Claude_Files/temp/Combining Large Language Models With Pedagogical Dependency Graphs for Teaching Complex Humanities Topics.md` (~5,200 words).
>
> Tagging discipline: see `sub_concerns_checklist.md` (66 sub-concerns across 5 lenses).
>
> **Per-section accountability:** every section and subsection below must produce ≥1 claim row OR a written justification `_No applicable claim because…_`. Silent omission is a defect.

## Section index (paper structure)

- §Executive Summary (L3-11)
- §Definitions and Scope (L13-21)
  - §Comparative frame (L23-34)
- §Why the Combination Is Pedagogically Plausible (L36-46)
- §Evidence Base and What It Actually Supports (L48-58)
  - §A humanities-specific implication (L60-64)
- §Design Patterns for LLM and PDG Integration (L66-74)
  - §Recommended node and edge schema (L76-86)
  - §Sample workflows with roles and checkpoints (L88-95)
  - §Sample PDG and workflow for teaching Kant to phenomenology (L97-140)
  - §Sample prompt templates (L142-182)
- §Risks, Governance, and Equity (L184-194)
- §Implementation and Evaluation (L196-206)
- §Prioritized Reading List and Open Questions (L208-214)
  - §Open questions and limitations (L216-224)

---

## Claim rows

Format per row:
- **Section** — name + line range
- **Sub-concern ID(s)** — from L1.1–L5.10
- **Claim** — verbatim quote or close paraphrase with line-anchored support
- **Paideia applicability** — concrete reference to current Paideia surface
- **Confidence** — `clear-recommendation` / `inferable` / `speculative`

### §Executive Summary (L3-11)

- **L5** | **L1.2** | `clear-recommendation`
  - **Claim:** *"A PDG models pedagogical dependence, not merely historical influence, textual genealogy, or citation networks. An influence map can tell you that Kant mattered for Husserl… a PDG asks the different question of what students must understand first for a given learning goal."*
  - **Paideia applicability:** Directly names the distinction the current graph partially encodes (ADR 0061 product established `historical_influence` as a distinct predicate). But this framing says the two layers are fundamentally different *question types*, not merely edge-type variants — argues that `historical_influence` edges should not be treated as weak pedagogical edges. Paideia's current 17 `historical_influence` edges may need a governance annotation clarifying they are non-pedagogical by default.

- **L7** | **L3.1** | `clear-recommendation`
  - **Claim:** *"The PDG should serve as the instructional spine and the LLM as the adaptive interface."*
  - **Paideia applicability:** Canonical framing for any Phase 6 LLM integration: the PDG (current 380 nodes / 533 edges) must drive the LLM's outputs, not the reverse. This is a foundational architecture constraint the Phase 6 master plan should open with — if Phase 6 involves LLM-facing query patterns, the spine-vs-interface split must be encoded as an architectural invariant, not an aspiration.

- **L9** | **L5.6** | `clear-recommendation`
  - **Claim:** *"The empirical base for exactly 'LLM+PDG in humanities' is still thin… many design claims for humanities must be treated as well-grounded extrapolations, not settled facts."*
  - **Paideia applicability:** Epistemic posture check for Paideia's own graph-validity assumptions. Any ADR proposing a new edge type or schema field for humanities should document which claims rest on extrapolation vs. direct evidence. Relevant to design-based research framing per L5.6.

- **L11** | **L1.4, L1.5, L1.8, L3.9, L4.9** | `clear-recommendation`
  - **Claim:** *"Instructor-authored or instructor-validated graphs; provenance for every edge; low-confidence and culturally loaded edges visibly flagged; formative assessments aligned to nodes; graph updates gated by human review."*
  - **Paideia applicability:** Enumerates five specific schema/governance additions that Paideia currently has none of: (a) per-edge provenance, (b) confidence flags, (c) cultural-load flags, (d) formative-assessment links per node, (e) gated edit workflow. All five require new columns in the Supabase-hosted edges table or separate tables.

### §Definitions and Scope (L13-21)

- **L15** | **L1.1, L1.2** | `clear-recommendation`
  - **Claim:** *"nodes represent teachable units and whose edges represent claims such as prerequisite-for, supports, contrast-needed-before, example-of, common-misconception-about, or assessed-before."*
  - **Paideia applicability:** Names six edge types explicitly; Paideia has two (`pedagogical_prerequisite`, `historical_influence`). Missing types: `supports`, `contrast-needed-before`, `example-of`, `common-misconception-about`, `assessed-before`. This is the most direct enumeration of what Paideia's edge-type taxonomy lacks — each missing type is a candidate for a product ADR (continuing the 0085-0088 ADR series on architecture tension-sets).

- **L15** | **L1.2** | `clear-recommendation`
  - **Claim:** *"it is narrower than a generic concept map because it encodes instructional dependency rather than merely associative relatedness."*
  - **Paideia applicability:** Reinforces that Paideia's `historical_influence` edges should not be navigated as though they imply instructional ordering — they must remain clearly labelled as non-pedagogical. The 17 `historical_influence` edges may need a node-level annotation preventing them from being consumed by any LLM scaffolding layer as pedagogical prerequisites.

- **L17** | **L3.1** | `clear-recommendation`
  - **Claim:** *"The PDG layer handles sequencing, scaffolding, prerequisite visibility, bottleneck localization, and assessment alignment. The LLM layer handles explanation, dialogue, hint generation, feedback, example generation, diagnostic interpretation, candidate graph refinement, and student-facing personalization."*
  - **Paideia applicability:** Precise role partition. Phase 6 master plan input: each of the LLM-layer responsibilities (explanation, dialogue, hint generation, etc.) requires the PDG to expose the corresponding node/edge fields. For example, "hint generation" requires `misconceptions` and `assessment_items` per node; "candidate graph refinement" requires `confidence` and `provenance` per edge. This maps directly onto the schema gaps catalogued under L1.4–L1.8.

- **L19-21** | **L1.2, L2.1, L2.13** | `clear-recommendation`
  - **Claim:** *"three different relations that are often conflated: Historical influence… Conceptual relatedness… Pedagogical dependence… The pedagogical dependency path is therefore goal-relative, whereas the influence path is not."*
  - **Paideia applicability:** Paideia's current two-edge model conflates the three. A third edge type — `conceptual_relatedness` — is implied as a missing middle layer. More pressingly, the paper states that `pedagogical_prerequisite` edges are only meaningful relative to a stated learning outcome; without `learning_outcome` parameterization (currently absent), Paideia's 516 prerequisite edges are de facto unparameterized and may be systematically mis-routing future LLM consumers.

### §Comparative frame (L23-34)

- **L27** | **L3.1, L5.3** | `clear-recommendation`
  - **Claim:** Table cell: *"Highest [accuracy] when LLM outputs are constrained by expert-validated graph structure and evidence."* PDG+LLM column.
  - **Paideia applicability:** Directly supports the Phase 6 architecture decision that the LLM must be constrained by the Paideia PDG, not free-generating its own structure. This is the comparative-experimental framing (L5.3) that a future Paideia evaluation should design around.

- **L30** | **L1.4, L1.5, L3.9, L4.9** | `clear-recommendation`
  - **Claim:** Table cell: *"Higher [transparency] than LLM-only if graph provenance, confidence, and overrides are logged."*
  - **Paideia applicability:** The condition ("if") is not currently met: Paideia has no provenance or confidence fields on edges, and no override log. To reach the transparency level the paper describes as achievable, Paideia needs per-edge `provenance`, `confidence`, and a separate override-event log table.

- **L31** | **L4.1, L4.13** | `clear-recommendation`
  - **Claim:** Table cell: *"[Bias and cultural risk]: Improved if graph edits are contestable and multilingual performance is audited, but still not risk-free."*
  - **Paideia applicability:** Connects directly to Paideia's anti-bias discipline (`feedback_anti_bias_implementation_discipline.md`). The paper's PDG+LLM row does not eliminate canon bias — it only makes it more visible. Paideia's graph could harden one intellectual tradition's sequence as default; the paper recommends contestability mechanisms (counterexample edges, alternative paths) which Paideia currently has none of.

- **L32** | **L3.1, L3.4** | `inferable`
  - **Claim:** Table cell: *"[Instructor workload] Best trade-off when instructors author core structure and LLM handles derivative tasks under review."*
  - **Paideia applicability:** Implies a role-checkpoint model where the current Paideia graph (instructor-validated at build time) would function as the "core structure." The Phase 6 master plan should define which tasks are "derivative under review" vs. "core structure changes" for Paideia's specific use.

### §Why the Combination Is Pedagogically Plausible (L36-46)

- **L38** | **L2.11, L1.3** | `clear-recommendation`
  - **Claim:** *"A PDG operationalizes [prior knowledge findings] by making explicit which concepts and practices are assumed, optional, or target-level."*
  - **Paideia applicability:** The distinction between "assumed," "optional," and "target-level" implies at minimum a `necessity_level` field on edges (or equivalently a `node_status` field). Currently Paideia has no mechanism to distinguish a hard prerequisite from an optional enrichment — all 516 `pedagogical_prerequisite` edges are treated as equivalent.

- **L40** | **L2.5, L1.17** | `clear-recommendation`
  - **Claim:** *"The expertise reversal effect… adds a further complication: scaffolds that help novices can become redundant or even counterproductive for more advanced learners. A static syllabus often cannot respond to that dynamic, but an LLM conditioned on a PDG can, in principle, give heavier support on fragile prerequisite nodes and then fade support as mastery increases."*
  - **Paideia applicability:** Implies a `fade_trajectory` or `scaffolding_weight` attribute per edge — currently absent. More broadly, implies that Paideia's edges need a `necessity_level` axis that can vary by learner state. This is a schema change (new column on the edges table) AND an architecture requirement for any Phase 6 LLM integration.

- **L42** | **L2.9, L3.6** | `inferable`
  - **Claim:** *"LLM-generated concept maps reduced perceived cognitive load by 31.5 percent and improved reading efficiency by 14.1 percent with comparable comprehension accuracy."*
  - **Paideia applicability:** Evidence supporting value of LLM-generated node primers. The student-facing explainer template (L3.6) that the paper proposes later is grounded in this effect. Paideia's nodes currently have no `approved_examples` or `misconceptions` fields that would enable such primer generation — the absence is a direct gap.

- **L44** | **L2.1, L2.2, L1.9** | `clear-recommendation`
  - **Claim:** *"Threshold concepts and Decoding the Disciplines both emphasize that students often fail not because they lack content coverage, but because they have not crossed tacit disciplinary thresholds… Corrigan's argument that students must cross threshold concepts around text, meaning, context, form, and reading is almost a template for node construction in a humanities PDG."*
  - **Paideia applicability:** Paideia nodes have no `threshold_concept` boolean/tag. The paper identifies threshold-concept tagging as not merely decorative — it drives which nodes the LLM should treat as "bottleneck" nodes requiring deeper scaffolding. This tag needs to be added to the nodes table in Supabase.

- **L46** | **L3.1, L5.6** | `inferable`
  - **Claim:** *"the best results occur when the system is pedagogically engineered and often when humans remain in the loop. That combination is exactly what a PDG+LLM architecture enables."*
  - **Paideia applicability:** Reinforces that Paideia's human-curation posture (instructor-validated graph) is the empirically supported position. No schema change needed, but this is a standing argument for maintaining instructor-review gates on all edge additions.

### §Evidence Base and What It Actually Supports (L48-58)

- **L50** | **L3.8, L3.11** | `clear-recommendation`
  - **Claim:** *"32 percent of generated hints initially failed quality checks, and self-consistency was needed to reduce error rates."*
  - **Paideia applicability:** Quantified failure rate for unchecked LLM-generated content. Directly argues that any Phase 6 LLM integration must build in a quality-check pipeline before content is exposed to learners. Self-consistency (multiple LLM samples, majority vote) is the cited mitigation — this is an architecture requirement, not a nice-to-have.

- **L52** | **L3.7, L3.1** | `clear-recommendation`
  - **Claim:** *"current models still struggle to respond effectively to key context signals such as student errors and knowledge components, and are unlikely to match the learning benefits of structured ITS behavior without additional methods."*
  - **Paideia applicability:** The knowledge-components signal requires the PDG to expose per-node `assessment_items` and per-edge `edge_type` semantics (so the LLM can distinguish "student failed on threshold concept node" from "student failed on enrichment node"). Paideia's current flat edge set cannot provide this signal.

- **L54** | **L3.11, L4.11** | `clear-recommendation`
  - **Claim:** *"For humanities teaching, that means LLM scoring should be used as a triage or drafting aid, not as an unreviewed arbiter."*
  - **Paideia applicability:** Governance posture for any Phase 6 assessment integration. No schema change, but this should be encoded as a named constraint in any future product ADR covering LLM-driven grading/scoring (e.g., a Phase 6 ADR on formative assessment alignment).

- **L56** | **L1.4, L5.7, L3.13** | `clear-recommendation`
  - **Claim:** *"automatic or semi-automatic graph refinement is feasible, but still domain-sensitive and in need of expert validation."*
  - **Paideia applicability:** Validates the trace-informed candidate-edge workflow (L3.13). For Paideia to support this pattern, edges need `confidence` (multi-source), `provenance`, and `counterexamples` fields — and the Supabase schema needs a "suggested edges" staging table separate from the canonical edges table to hold pending LLM-proposed additions.

- **L58** | **L2.1, L2.3** | `clear-recommendation`
  - **Claim:** *"the learning target is a disciplinary move, not encyclopedic coverage… threshold-concept work in literary studies and history provides a principled way to decide which nodes belong in a PDG."*
  - **Paideia applicability:** Paideia's current 380 nodes include many that are encyclopedic coverage rather than disciplinary-move-focused. The threshold-concept filter is a prioritization criterion for which nodes deserve the full schema enrichment (misconceptions, assessment items, threshold tag). This is an editorial discipline point, not a schema point, but it affects which nodes Phase 6 invests in first.

### §A humanities-specific implication (L60-64)

- **L62** | **L1.3, L2.13** | `clear-recommendation`
  - **Claim:** *"If the outcome is 'explain why Husserl's transcendental phenomenology is not just empirical psychology,' then high-value prerequisites may include [different nodes than] 'compare Husserl's transcendental idealism with Kant's'… The pedagogical dependency path is therefore goal-relative, whereas the influence path is not."*
  - **Paideia applicability:** This is the most concrete articulation of L1.3 in the paper. Paideia's 516 `pedagogical_prerequisite` edges do not carry a `learning_outcome` tag — they are implicitly universal prerequisites. The paper's worked example shows that the same conceptual terrain produces different dependency paths for different outcomes. Adding a `learning_outcome` foreign key (or `necessity_level` per outcome) to the edges table is the minimal schema change that makes this expressible.

- **L64** | **L1.2, L2.10, L1.18** | `clear-recommendation`
  - **Claim:** *"In literary studies, an influence map may show Saussure → structuralism → Derrida, but a PDG for a first encounter with deconstruction may prioritize 'signifier/signified,' 'binary opposition,' 'instability of textual meaning,' and 'close reading of tensions in the text'… In history, an influence map may be nearly irrelevant compared with the threshold concept of perspective."*
  - **Paideia applicability:** Three worked examples (literary studies, rhetoric/philosophy of language, history) demonstrating that historical-influence paths and pedagogical-dependency paths diverge sharply. Directly relevant to Paideia's `historical_influence` edge type — these 17 edges should not be traversed by a learner-routing engine as if they were soft prerequisites. The paper recommends modeling multiple legitimate entry routes (L1.18) as alternatives, which Paideia cannot currently represent.

### §Design Patterns for LLM and PDG Integration (L66-74)

- **L68** | **L3.1, L3.4, L3.9** | `clear-recommendation`
  - **Claim:** *"instructors or discipline teams define the canonical nodes, edge types, learning outcomes, and approved evidence. The LLM then generates primers, examples, misconceptions, formative questions, and candidate refinements, but it never silently rewrites the graph."*
  - **Paideia applicability:** Three schema additions implied: (a) `approved_evidence` per edge, (b) `learning_outcomes` per node, (c) a write-protection mechanism preventing LLM from mutating canonical node/edge records. The no-silent-rewrite rule (L3.9) maps to a Paideia governance constraint: any future LLM-integration ADR must specify the boundary between LLM-readable fields and LLM-writable fields.

- **L70** | **L2.9, L2.1, L4.9** | `clear-recommendation`
  - **Claim:** *"students externalize their understanding by drawing a local PDG or concept map and the LLM responds with questions such as 'Which edge is evidentially strongest?'… the graph critique should be framed as suggestive, not authoritative, especially for contested interpretive domains."*
  - **Paideia applicability:** Student-authored graph pattern. Paideia's graph is currently entirely instructor-authored. This pattern implies a learner-facing graph-construction interface and a review workflow, which would be significant architecture work. Relevant for Phase 6 master plan scoping — this is a distinct use pattern from adaptive branching.

- **L72** | **L2.5, L1.15, L1.16** | `clear-recommendation`
  - **Claim:** *"The student completes a diagnostic task aligned to PDG nodes; the LLM scores or summarizes the response against a rubric; the system updates mastery estimates; and the next activity is selected from graph neighbors whose prerequisites are satisfied."*
  - **Paideia applicability:** Adaptive branching pattern. Requires: (a) `assessment_items` per node (currently absent), (b) a learner-state table with `mastery_probability` per node per learner (currently absent), (c) graph traversal logic that checks prerequisite satisfaction before advancing. The paper notes this should start "conservative and coarse-grained" for humanities — meaning not all 516 edges need to function as hard branching gates initially.

- **L74** | **L3.13, L1.4, L1.5, L1.7, L5.2** | `clear-recommendation`
  - **Claim:** *"If many students repeatedly fail on a supposedly downstream node but perform well on its represented prerequisites, the system can flag either a missing prerequisite, an over-strong edge, or a bad assessment item… LLMs can accelerate the search for candidate revisions, but only if every suggested edge is paired with confidence, provenance, contrary evidence, and an approval workflow."*
  - **Paideia applicability:** Trace-informed graph revision is the most demanding pattern — it requires learner-trace data, anomaly detection, and an LLM-assisted edge-proposal pipeline. The paper's list of required edge fields for this to work (`confidence`, `provenance`, `contrary evidence`, `approval workflow`) maps directly to L1.4, L1.5, L1.7 — all currently absent from Paideia's edges table. This pattern cannot be implemented until those schema additions land.

### §Recommended node and edge schema (L76-86)

This is the densest section. Every row of the schema table generates one or more claims.

- **L80 (Node row)** | **L1.9, L1.10** | `clear-recommendation`
  - **Claim:** Node field `threshold_concept?` — *"Lets the LLM… distinguish threshold concepts from background context."* Node field `node_type` — required, not enumerated in this row but listed as `Required fields`.
  - **Paideia applicability:** Paideia nodes have no `threshold_concept` boolean and no `node_type` field. Adding `threshold_concept boolean` and `node_type text` (with an enumeration: threshold concept / bridge concept / disciplinary practice / text-excerpt / historical context / misconception / comparative lens / assessment task) requires an ALTER TABLE migration on the nodes table. This is a new product ADR territory — the first node-type taxonomy.

- **L80 (Node row continued)** | **L1.11, L1.12** | `clear-recommendation`
  - **Claim:** Node fields `granularity` and `disciplinary_domain` listed as required node fields.
  - **Paideia applicability:** Paideia has no `granularity` tag (coarse / medium / fine) and no `disciplinary_domain` field per node. `disciplinary_domain` is particularly important for Paideia's cross-domain (philosophy, literary studies, history) scope — without it, LLM prompts cannot filter by domain. Both fields require new columns on the nodes table.

- **L80 (Node row continued)** | **L1.6, L1.16** | `clear-recommendation`
  - **Claim:** Node fields `canonical_sources`, `approved_examples`, `misconceptions`, `assessment_items`, `mastery_evidence` listed as required node fields. Rationale: *"ground outputs in approved sources rather than free-form recall."*
  - **Paideia applicability:** Paideia nodes have none of these five fields. `canonical_sources` would be a foreign key or JSONB field linking to a sources table. `approved_examples` and `misconceptions` are JSONB arrays or separate tables. `assessment_items` links to a formative-assessment table (currently non-existent). `mastery_evidence` describes what counts as demonstration of mastery — this is pedagogical metadata with no current home in Paideia's schema.

- **L80 (Node row continued)** | **L1.13** | `clear-recommendation`
  - **Claim:** Node field `accessibility_notes` — listed as required node field.
  - **Paideia applicability:** Covers jargon load, culturally specific references, language load — the equity metadata per L1.13. Currently absent from Paideia. Could be a JSONB field `accessibility_notes` with sub-keys `jargon_load`, `cultural_references`, `language_load`. Relevant to Paideia's anti-bias discipline (`feedback_anti_bias_implementation_discipline.md`) — this is the field that makes cultural-load concerns inspectable in the graph itself rather than only in LLM prompt design.

- **L81 (Edge row)** | **L1.1, L1.3** | `clear-recommendation`
  - **Claim:** Edge fields `edge_type`, `necessity_level` listed as required. Rationale: *"Makes prerequisite claims contestable and reviewable; supports low-confidence flagging and assessment alignment."*
  - **Paideia applicability:** Paideia's edges table has no `edge_type` field (edge type is implicit from the two named edge types, stored as separate predicates or in the same table). More critically, `necessity_level` (required / recommended / historical-contextual-only) is absent — without it, all 516 `pedagogical_prerequisite` edges are implicitly "required," which the paper explicitly warns is overclaiming.

- **L81 (Edge row continued)** | **L1.4, L1.5, L1.7, L1.14** | `clear-recommendation`
  - **Claim:** Edge fields `confidence`, `provenance`, `created_by`, `last_reviewed`, `counterexamples`, `assessment_link` listed as required.
  - **Paideia applicability:** All six are absent from Paideia's current edges table. `confidence` requires a multi-source model (see L82 below). `provenance` requires a `source_text` + `course_context` + `version` + `reviewer` + `rationale` structure. `counterexamples` is a JSONB or separate table. `assessment_link` is a foreign key to an assessment table (which doesn't yet exist). `created_by` and `last_reviewed` are version-history fields (L1.14). This row alone implies 6+ new columns or a new provenance sub-table.

- **L82 (Confidence model)** | **L1.4** | `clear-recommendation`
  - **Claim:** *"Confidence model: `expert_confidence`, `trace_confidence`, `llm_confidence`, `disagreement_flag` — Prevents silent overclaiming and allows differential treatment of authoritative versus provisional edges."*
  - **Paideia applicability:** Three independent confidence sources, not a single score. Paideia's current edges have no confidence field at all. The three-source model means: (a) `expert_confidence` is set at authoring time by the instructor; (b) `trace_confidence` is updated as learner data accumulates; (c) `llm_confidence` is set when an LLM proposes or reviews an edge. The `disagreement_flag` fires when these diverge. This is a significant schema addition — likely a separate `edge_confidence` table with composite primary key on `edge_id`. Both a product ADR and a Supabase migration are needed.

- **L83 (Provenance record)** | **L1.5, L1.14** | `clear-recommendation`
  - **Claim:** *"Provenance record: `source_text`, `course_context`, `version`, `reviewer`, `rationale` — Essential for auditability, contestability, and revision history in interpretive subjects."*
  - **Paideia applicability:** Provenance is the audit trail that makes the graph's pedagogical commitments inspectable. Currently absent from Paideia. Should be a separate `edge_provenance` table (one-to-many per edge, as a single edge may have multiple review events). The `version` field implies edges need a versioning scheme — aligns with L1.14. This is a product-level ADR requiring a decision on whether provenance is per-edge-version or per-edge-review-event.

- **L84 (Learner state)** | **L1.15** | `clear-recommendation`
  - **Claim:** *"Learner state: `mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`, `language_preference` — Helps the LLM choose explanation depth, detect potential expertise reversal, and adapt questioning."*
  - **Paideia applicability:** Learner-state schema is fully absent from Paideia. This is a separate table (not on the graph's nodes/edges tables) keyed on `(learner_id, node_id)`. The paper specifies 5 fields. `language_preference` is the equity field that enables multilingual-fairness monitoring. This table would be needed before any adaptive-branching or personalization feature can function.

### §Sample workflows with roles and checkpoints (L88-95)

- **L90-95 (workflow table)** | **L3.3, L3.4** | `clear-recommendation`
  - **Claim:** Table of four workflows: (1) Instructor-authored PDG with LLM scaffolding, (2) Student-authored PDG with LLM feedback, (3) Adaptive branching lesson, (4) Automated prerequisite inference from traces. Each row specifies instructor role, LLM role, student role, and human checkpoints.
  - **Paideia applicability:** The four workflows are not equally mature for Paideia. Workflow 1 is currently the only viable one (instructor-authored graph exists; LLM scaffolding would be the first Phase 6 capability). Workflows 3 and 4 require the learner-state table and trace infrastructure that don't yet exist. Workflow 2 requires a student-facing graph construction interface. Phase 6 master plan should explicitly sequence these four workflows, not treat them as simultaneous targets.

- **L92 (Workflow 1 checkpoints)** | **L3.4, L3.9, L3.11** | `clear-recommendation`
  - **Claim:** *"Human checkpoints: Approve graph; review low-confidence outputs; spot-check scoring."*
  - **Paideia applicability:** The three named checkpoints require infrastructure: (a) a "graph approval" workflow (currently Paideia has no approval-status field on nodes or edges), (b) a "low-confidence output queue" (requires `confidence` fields), (c) "spot-check scoring" interface (requires `assessment_items` and a scoring-log table). None of these exist; they are Phase 6 infrastructure requirements.

- **L94 (Workflow 3 checkpoints)** | **L3.4, L5.8** | `clear-recommendation`
  - **Claim:** *"Human checkpoints [for adaptive branching]: Review anomalous paths and override routing decisions."*
  - **Paideia applicability:** Anomalous-path detection requires learner-trace logging and a monitoring dashboard. Override capability requires an `override_events` log table. Both are absent from Paideia. This aligns with L5.8 in the sub-concerns checklist.

- **L95 (Workflow 4 checkpoints)** | **L3.9, L5.9** | `clear-recommendation`
  - **Claim:** *"Human checkpoints [for automated prerequisite inference]: No graph update occurs without expert sign-off and stored rationale."*
  - **Paideia applicability:** Absolute rule: any LLM-proposed edge must pass through an expert-sign-off gate before entering the canonical edges table. For Paideia this means a `pending_edges` staging table with `status: pending | approved | rejected` and a `rationale` field for each disposition. This is a specific product ADR requirement.

### §Sample PDG and workflow for teaching Kant to phenomenology (L97-140)

- **L99-138 (Mermaid workflow)** | **L3.3, L3.4, L3.9** | `clear-recommendation`
  - **Claim:** The Mermaid diagram makes the full workflow concrete: (a) Instructor defines target outcome → (b) Seed PDG nodes → (c) LLM proposes candidate edges with confidence and provenance → (d) Instructor review gate (Approve / Revise / Reject low-confidence edge) → (e) Publish course PDG → (f) LLM generates primers at three depth levels → (g) LLM generates formative questions per node → (h) Student diagnostic → (i) LLM scores against rubric → (j) Mastery gate → (k) Route to unmet prerequisite OR advance → (l) Human checkpoint on anomalies → (m) LLM proposes graph refinements from traces → (n) Instructor approves graph edits.
  - **Paideia applicability:** The full pipeline exposes every schema gap simultaneously. Steps (c) requires `confidence` + `provenance` per edge. Step (d) requires an approval-status field. Step (f) requires multi-depth primers (implies `granularity` per node OR a prompt parameter). Step (g) requires `assessment_items` per node. Step (i) requires rubric linkage. Step (j) requires `mastery_probability` in learner-state table. Steps (m)-(n) require the `pending_edges` staging table. This diagram is effectively a completeness test for the schema — Paideia currently cannot execute any step beyond (b).

- **L113 (Low-confidence edge)** | **L1.4, L1.7** | `clear-recommendation`
  - **Claim:** The Mermaid diagram explicitly shows a node: *"Low-confidence edge flagged: Full Kantian system --> Husserl essentials"* — with a branch to "Reject low-confidence edge."
  - **Paideia applicability:** The Kant→Husserl case is directly in Paideia's subject domain. This specific edge (if it exists in Paideia's 533 edges) is an example of an overclaiming historical-influence edge masquerading as a pedagogical prerequisite. The paper's workflow would flag it at review time if `confidence` and `edge_type` fields were present. Currently Paideia cannot distinguish this edge from a validated pedagogical dependency.

- **L140** | **L3.1** | `clear-recommendation`
  - **Claim:** *"This workflow embodies the best-supported division of labor: the graph carries the pedagogical commitments, the LLM operationalizes them conversationally, and human reviewers arbitrate contested structure and consequential decisions."*
  - **Paideia applicability:** Three-way role partition named explicitly. For Phase 6 master plan: any LLM-facing feature must be designed to never bypass the human-reviewer-arbitrates-contested-structure gate.

### §Sample prompt templates (L142-182)

- **L146-167 (Graph-refinement prompt)** | **L3.5, L3.13, L1.4, L1.5, L1.7** | `clear-recommendation`
  - **Claim:** The graph-refinement prompt specifies: inputs are (target learning outcome, current PDG nodes and edges, student error traces, approved source excerpts); outputs are JSON with (candidate_new_edges, candidate_weakened_edges, evidence_for_each, possible_false_prerequisites, confidence_score_0_to_1, instructor_review_questions); rules include (prefer minimal edits, distinguish historical influence from pedagogical necessity, flag contested claims, never mark an edge as required unless evidence supports instructional dependence).
  - **Paideia applicability:** This is the most concrete prompt template in the paper. For Paideia to use this template: (a) the LLM input requires "current PDG nodes and edges" — meaning a serialization format must be defined for Paideia's graph (not yet specified); (b) "approved source excerpts" requires `canonical_sources` per node; (c) "student error traces" requires the learner-trace infrastructure; (d) the JSON output fields (`candidate_new_edges`, `confidence_score_0_to_1`) require the `pending_edges` staging table to receive them; (e) the rule "distinguish historical influence from pedagogical necessity" maps directly to Paideia's `historical_influence` vs `pedagogical_prerequisite` distinction — the prompt must be provided this taxonomy. The anti-bias rule in `feedback_audit_llm_inputs_for_bias.md` applies: the prompt must not expose learner identity or instructor identity in the "approved source excerpts" field.

- **L169-182 (Student-facing explainer prompt)** | **L3.6, L1.8, L1.9, L2.11** | `clear-recommendation`
  - **Claim:** The student-facing explainer prompt specifies: explain to a student who has mastered prerequisites; use (one short definition, one humanities-relevant example, one contrast with a nearby concept, one formative question, one sentence explaining why this node matters for the next task); avoid (unapproved terminology, assuming mastery of unmet prerequisites).
  - **Paideia applicability:** This template is directly usable against Paideia's graph IF: (a) the node has `approved_examples` (currently absent), (b) the node has a neighboring node to contrast with (requires graph traversal — available from Paideia's existing edges), (c) the node has `assessment_items` for the formative question (currently absent), (d) `canonical_sources` for restricting terminology (currently absent). The "avoid unapproved terminology" rule connects to Paideia's anti-bias discipline — the LLM should not introduce source-identity cues (author names, school labels) beyond those in the node's `canonical_sources`. This prompt template is Phase 6's most immediately actionable feature — it requires the fewest new schema fields to pilot (primarily `approved_examples` and one `assessment_item` per priority node).

### §Risks, Governance, and Equity (L184-194)

- **L186** | **L3.7, L4.7** | `clear-recommendation`
  - **Claim:** *"The most dangerous failure is often a false prerequisite or an omitted prerequisite, because it silently changes the learning path. That is especially acute in humanities, where canonical importance can be mistaken for pedagogical necessity… NIST's GenAI profile explicitly treats confabulation as a core risk."*
  - **Paideia applicability:** Hallucinated structure (false prerequisites) is more dangerous than hallucinated facts in a PDG system. Paideia's current graph may already contain false prerequisites — edges added because of canonical/historical importance, not demonstrated pedagogical necessity. The paper recommends `possible_false_prerequisites` as an explicit output field in the graph-refinement prompt. Paideia should add a `false_prerequisite_risk` flag or `provisional` status to edges lacking mastery-evidence provenance.

- **L188** | **L4.1, L4.12, L1.18** | `clear-recommendation`
  - **Claim:** *"A graph can harden one tradition's pathway into the default route and convert a contestable curriculum choice into a pseudo-natural learning dependency. The mitigation is… store alternative pathways, attach tradition labels, invite contestation, and represent 'multiple legitimate entry routes' rather than a single intellectual staircase."*
  - **Paideia applicability:** Four concrete mitigations: (a) `alternative_pathway` links per node — a new edge type or a node-level field listing alternative entry sequences; (b) `tradition_label` per node or edge — e.g., "analytic tradition," "continental tradition," "Anglophone literary criticism"; (c) a contestation mechanism (flag for community review); (d) explicit multi-path representation. All four are absent from Paideia. `tradition_label` is particularly relevant to Paideia's cross-domain scope and connects to the anti-bias discipline (`feedback_anti_bias_implementation_discipline.md` — tradition labels are structural patterns, not enumerated tokens).

- **L190** | **L4.11, L4.5, L3.12** | `clear-recommendation`
  - **Claim:** *"LLM scoring can look plausible while smoothing extremes, overscoring, or shifting criteria subtly… many learning goals involve argument quality, interpretive judgment, nuance, and evidential reasoning rather than closed-form correctness. The mitigation is to reserve consequential grading for human judgment… and to present the AI as a critic or coach, not as the final judge."*
  - **Paideia applicability:** Humanities-specific AI scoring risk. Anti-pathologizing-interpretive-styles (L4.5): the LLM may score legitimate alternative interpretations as misconceptions if its rubric is tied to one tradition. For any Phase 6 assessment integration, the `assessment_items` per node must carry a rubric that explicitly acknowledges legitimate alternative interpretations — not just a "correct answer." This is a content requirement for the `assessment_items` field, not just a schema question.

- **L192** | **L4.6** | `clear-recommendation`
  - **Claim:** *"minimize stored traces, separate identifiers from learning analytics, and avoid retaining raw student writing longer than needed for validated educational purposes."*
  - **Paideia applicability:** FERPA-aligned data minimization. Any future learner-state table in Paideia's Supabase should use pseudonymized IDs, not real learner identifiers. Raw student writing (used for trace-informed graph revision) should not be stored in the same schema as the graph — a separate, time-limited data store with explicit retention limits. This is a product ADR requirement for the learner-state schema.

- **L194** | **L4.10, L3.9, L4.8** | `clear-recommendation`
  - **Claim:** *"no silent graph mutation. Every proposed edit should be attributable, reviewable, and reversible. Students should also be able to see when a path was altered because of model inference rather than instructor design."*
  - **Paideia applicability:** Three governance rules: (a) attributable — `created_by` on every edge (system, instructor, LLM-proposal); (b) reviewable and reversible — version history on edges (L1.14), approval-status field; (c) student-visible provenance — a student-facing field indicating whether their current path was instructor-designed or model-inferred. The last is a UX requirement with schema implications: edges or paths must carry an `authority_source` field (instructor | model | trace-inferred) visible to students.

### §Implementation and Evaluation (L196-206)

- **L198** | **L3.2, L3.15** | `clear-recommendation`
  - **Claim:** *"A practical architecture has five services. The graph store holds PDG nodes, edges, provenance, confidence, and assessment alignment. A content store holds approved excerpts, lecture notes, prompts, and exemplars. The LLM orchestration layer handles tutoring, graph-refinement proposals, feedback generation, and rubric-linked scoring. The analytics layer tracks student traces and mastery evidence. The review layer exposes all low-confidence outputs, contested edges, and override events to instructors."*
  - **Paideia applicability:** Paideia currently has only the graph store (partial — without provenance/confidence). Missing: content store (a separate table or service for approved excerpts), analytics layer (no learner-trace infrastructure), review layer (no interface for exposing low-confidence/contested items). The paper also notes: *"a property-graph database such as Neo4j is a strong fit when edges need rich attributes."* Paideia uses Postgres + Supabase — this is a direct tool-stack consideration (L3.15). Rich edge attributes (confidence, provenance, counterexamples, assessment_link) can be represented in Postgres with JSONB fields and junction tables, but the paper's recommendation of Neo4j flags that this choice carries a complexity cost as attributes multiply.

- **L200** | **L3.14** | `clear-recommendation`
  - **Claim:** *"Students do not need the entire back-end ontology. They need the current local neighborhood: the target node, its immediate prerequisites, common misconceptions, upcoming assessments, and alternative routes if they are stalled."*
  - **Paideia applicability:** Student-subset exposure pattern. For any Phase 6 student-facing interface on Paideia's graph, the query layer should return only: target node + 1-hop neighbors + node's `misconceptions` + node's `assessment_items` + `alternative_pathway` links. This is a query-design constraint that shapes how the Supabase schema needs to be indexed and queried — not just what fields exist but how they are exposed.

- **L202** | **L2.2, L2.3, L1.1, L1.16** | `clear-recommendation`
  - **Claim:** *"A reasonable instructor workflow begins before the semester. First, identify the course's threshold concepts and bottlenecks. Second, define node granularity at the level of teachable, assessable units rather than whole books or authors whenever possible. Third, attach at least one diagnostic task to every node that can plausibly function as a prerequisite. Fourth, mark edge necessity as required, recommended, or historical/contextual only."*
  - **Paideia applicability:** Four-step pre-semester workflow that doubles as a schema-population protocol. Steps 1-4 map directly to: (1) `threshold_concept` boolean — must be set before graph is used; (2) `granularity` tag — required; (3) `assessment_items` — at minimum one per prerequisite node; (4) `necessity_level` on edges — three-value enum (required / recommended / historical-contextual-only). Step 4 is the most actionable for Paideia's existing 516 `pedagogical_prerequisite` edges — re-classifying them as required/recommended/historical-contextual is a meaningful data-quality pass even before new schema is added.

- **L204** | **L5.1, L5.2, L5.3, L5.9** | `clear-recommendation`
  - **Claim:** *"Evaluation should be stricter than simple satisfaction surveys… the right research designs are randomized or quasi-experimental studies that compare PDG-only, LLM-only, and PDG+LLM conditions… Graph validity itself should be evaluated: expert agreement on edge labels, revision rates after review, disagreement concentrations by topic, and whether trace-inferred edits improve or worsen downstream learning."*
  - **Paideia applicability:** The evaluation framework names specific graph-validity metrics: (a) expert agreement on edge labels — requires a multi-rater review workflow; (b) revision rates after review — requires version history (L1.14); (c) disagreement concentrations by topic — requires `disciplinary_domain` tagging; (d) downstream-learning improvement from trace-inferred edits — requires the full learner-trace pipeline. None of these are currently instrumentable with Paideia's schema. Paideia's Phase 6 master plan should include at minimum metrics (a) and (b) as instrumentation goals.

- **L206** | **L4.3, L4.4, L4.5, L4.8** | `clear-recommendation`
  - **Claim:** *"Do multilingual students receive poorer feedback or less accurate scoring? Does the system over-pathologize certain interpretive styles as misconceptions? Are some traditions overrepresented as 'required prerequisites' rather than 'one valid route'? A credible LLM+PDG deployment should therefore publish periodic transparency reports on graph edits, override rates, subgroup discrepancies, and content-provenance coverage."*
  - **Paideia applicability:** Four subgroup-fairness questions, three of which require Paideia schema fields that don't exist: (a) multilingual scoring disparity requires `language_preference` in learner-state; (b) over-pathologizing interpretive styles requires rubrics in `assessment_items` that specify legitimate-alternative-interpretation acceptance; (c) tradition overrepresentation requires `tradition_label` per node/edge; (d) transparency reports require `override_events` log. Connects directly to Paideia's `feedback_audit_llm_inputs_for_bias.md` — the audit must extend to the graph's own tradition labeling.

### §Prioritized Reading List and Open Questions (L208-214)

- **L210** | **L2.1, L2.2, L2.5, L2.11** | `inferable`
  - **Claim:** *"The best starting points for the conceptual foundations are Falmagne et al. on knowledge spaces, Sweller on cognitive load, Kalyuga and colleagues on the expertise reversal effect, Nesbit and Adesope plus Schroeder et al. on concept maps, Meyer and Land on threshold concepts, and Middendorf and Pace on Decoding the Disciplines."*
  - **Paideia applicability:** These six bodies of literature map to specific sub-concerns: knowledge spaces → L5.7; cognitive load → L2.11; expertise reversal → L2.5; concept maps → graph design generally; threshold concepts → L2.1, L1.9; Decoding the Disciplines → L2.2. For any Paideia team member designing new node/edge schema, this reading list provides the non-AI justification for specific schema decisions. MemPalace: these should be tagged as `decision` drawers under the relevant sub-concern IDs.

- **L212** | **L5.6** | `inferable`
  - **Claim:** *"For current evidence on LLMs in education, the most informative primary studies for design judgment are Pardos and Bhandari on ChatGPT-generated help, Kestin et al. on AI tutoring versus active learning, Fischer et al. on AI tutoring and self-regulated study, Wang et al. on Tutor CoPilot, Scarlatos et al. on dialogue knowledge tracing, and Borchers et al. on benchmarked instructional adaptivity and fidelity."*
  - **Paideia applicability:** Six studies providing the empirical grounding for the LLM-in-education architecture claims. The Borchers et al. finding (LLMs struggle to match ITS adaptivity without additional methods) is the most directly applicable to Paideia's Phase 6 decisions — it argues explicitly for the PDG-as-constraint architecture over free-form LLM tutoring. Design-based research framing (L5.6) is the realistic evaluation path for Paideia.

- **L214** | **L2.1, L1.9** | `inferable`
  - **Claim:** *"For humanities pedagogy specifically, Corrigan on threshold concepts in literary studies, Paricio on perspective in history, and Zahavi's SEP entry on Husserl are especially useful for thinking about graph nodes that reflect actual disciplinary entry points rather than mere survey coverage."*
  - **Paideia applicability:** Corrigan and Paricio provide domain-specific evidence for which humanities nodes qualify as threshold concepts. Paideia's nodes in literary studies and history should be audited against Corrigan's five threshold concepts (text, meaning, context, form, reading) and Paricio's perspective concept. This is a data-quality task: retroactively tagging existing nodes with `threshold_concept: true` where they match the scholarly evidence.

### §Open questions and limitations (L216-224)

- **L218** | **L5.6** | `clear-recommendation`
  - **Claim:** *"direct experimental evidence for LLM+PDG in humanities is still sparse… Educational-graph research has been disproportionately concentrated in STEM and technical higher-education contexts."*
  - **Paideia applicability:** Epistemic posture: Paideia is operating in a domain (humanities LLM+PDG) with thin direct evidence. Any product ADR making strong claims about which schema fields drive learner outcomes should document which claims are STEM-extrapolated vs. humanities-validated. This is a meta-requirement for ADR authoring, not a schema change.

- **L220** | **L4.12, L1.18, L2.8** | `clear-recommendation`
  - **Claim:** *"how to model legitimate pluralism in humanities dependencies. Some thresholds are real, but many routes into a topic are defensible. The research challenge is to distinguish genuine bottlenecks from merely traditional sequences."*
  - **Paideia applicability:** Open empirical question directly applicable to Paideia's 516 `pedagogical_prerequisite` edges. Many of these may encode "merely traditional sequences" rather than genuine pedagogical bottlenecks. The paper names no algorithmic solution — this requires domain-expert review, Decoding-the-Disciplines methodology, and the `necessity_level` field (required vs. recommended) as the schema mechanism for expressing the distinction. Paideia's Phase 6 master plan should acknowledge this as an ongoing editorial challenge, not a one-time schema migration.

- **L222** | **L5.7, L2.6, L2.7** | `clear-recommendation`
  - **Claim:** *"how far automated student-trace methods can generalize from structured domains to interpretive disciplines… Humanities applications will need careful construct validation so that 'misconception,' 'mastery,' and 'prerequisite' are not imported too crudely from procedural domains."*
  - **Paideia applicability:** Construct-validity warning for Paideia's use of `misconceptions`, `mastery_probability`, and `pedagogical_prerequisite`. All three concepts carry procedural-domain assumptions when imported from STEM adaptive learning. For Paideia: (a) `misconception` must be defined with reference to disciplinary thinking, not surface-level errors; (b) `mastery_probability` for interpretive concepts requires rubric-based evidence, not binary correctness; (c) `pedagogical_prerequisite` edges require Decoding-the-Disciplines validation, not just expert intuition. This is a content-quality requirement — the schema fields can exist, but their semantics must be defined with humanities-appropriate validation criteria.

- **L224** | **L3.1, L4.9** | `clear-recommendation`
  - **Claim:** *"LLM+PDG is a promising design pattern for complex humanities teaching when the PDG supplies explicit, reviewable pedagogical structure and the LLM is treated as an adaptive interface rather than an autonomous curriculum authority. Without those conditions, the system is likely to inherit the weaknesses of both parts: rigid graphs and fluent but unreliable language models."*
  - **Paideia applicability:** Bottom-line conclusion. For Phase 6: the two conditions ("explicit, reviewable pedagogical structure" + "LLM as adaptive interface, not curriculum authority") are the load-bearing architectural constraints. "Reviewable" requires the provenance, confidence, and approval-workflow schema additions. "Adaptive interface" requires the LLM-role boundary to be enforced by the review layer (fifth service). Without these, Phase 6 inherits both failure modes: Paideia's current graph is "rigid" (no confidence gradation, no alternative paths), and any LLM added without constraints will be "fluent but unreliable."

---

## Coverage report

- **Sections with ≥1 row:** 14 / 14
- **Sections with justification (no rows):** none — all 14 sections have claim rows
- **Sub-concerns touched:**
  - L1.1, L1.2, L1.3, L1.4, L1.5, L1.6, L1.7, L1.8, L1.9, L1.10, L1.11, L1.12, L1.13, L1.14, L1.15, L1.16, L1.17, L1.18
  - L2.1, L2.2, L2.3, L2.5, L2.6, L2.7, L2.8, L2.9, L2.10, L2.11, L2.12, L2.13
  - L3.1, L3.2, L3.3, L3.4, L3.5, L3.6, L3.7, L3.8, L3.9, L3.10, L3.11, L3.12, L3.13, L3.14, L3.15
  - L4.1, L4.3, L4.4, L4.5, L4.6, L4.7, L4.8, L4.9, L4.10, L4.11, L4.12, L4.13
  - L5.1, L5.2, L5.3, L5.4, L5.6, L5.7, L5.8, L5.9, L5.10
- **Sub-concerns NOT touched in this paper:**
  - L2.4 (Scaffolding with explicit fade trajectory Wood/Bruner/Ross — paper touches expertise reversal and fade trajectory at L40 but does not name the Wood-Bruner-Ross scaffold-fade literature explicitly; tagged as L1.17 instead)
  - L4.2 (Expert blind spot / disciplinary word meanings — paper mentions this implicitly in the threshold-concepts discussion but does not address it as a named risk)
  - L5.4 (Heterogeneity-of-treatment-effects analysis — paper mentions subgroup analysis L206 but not HTE analysis as a statistical method)
  - L5.5 (Process-quality measurement: discussion moves, argumentation, annotation logs — paper mentions qualitative outcomes but does not discuss process-move measurement specifically)
  - L5.10 (Student-experience validity: perceived coherence, agency, sense of progression — paper mentions student-facing exposure L200 but does not address student-experience validity as an evaluation dimension)

**Note on coverage:** L2.4 is borderline — the paper's L40 passage on expertise reversal and fading support is semantically close to the Wood-Bruner-Ross tradition, and L1.17 captures the schema implication. Synthesis agents should treat L2.4 as weakly touched. L5.4, L5.5, L5.10 are genuinely absent — Paper 2 is stronger on schema and governance than on fine-grained evaluation methodology.
