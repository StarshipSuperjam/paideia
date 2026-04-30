# Architecture

This file covers the graph data model: node and edge schemas, structural principles, and shared services that operate on the graph. For other concerns, see:

- **learner-model.md** — Event-sourced learner model, engagement depth, interaction types, mastery decay, mastery computation, offline/sync
- **self-correction.md** — Five feedback loops, tension log, Sonnet/Opus pipeline, batch review cycle, model tiering
- **infrastructure.md** — Tech stack, DeepTutor fork, deployment target, cloud hosting, build approach
- **ui-architecture.md** — Globe navigation model, level-of-detail rendering, domain tag visualization

## Graph Structure

- Domain-agnostic directed graph of concepts with pedagogical prerequisite edges.
- Production target: hundreds of nodes per domain at concept-level granularity.
- Edges require genuine subject-matter judgment — not crowdsourceable or auto-generable.
- Philosophy prototype covers: foundations, epistemology, metaphysics, ethics, political philosophy, philosophy of mind/language/science, continental, Eastern traditions.
- The same graph structure, traversal logic, and teaching system apply to any knowledge domain with prerequisite relationships.

### Node Granularity Principle
**Added: 2026-04-07**

A node is the smallest unit at which a coherent prerequisite claim can be made. Every inbound edge to a node must be required for the whole node, and the whole node must be required by every outbound edge. If understanding a downstream concept only requires *part* of a node, the node is too coarse and should be split.

Nodes are concepts or ideas — never thinkers, schools, or historical periods. "Aristotle" is not a node. "Eudaimonia," "Hylomorphism," "Aristotelian Categories," and "Syllogistic Logic" are nodes. A thinker's system decomposes into the concepts that constitute it; those concepts are the atomic units of the graph.

This principle is testable: take any node, list its outbound edges, and for each one ask whether the downstream concept requires understanding *everything* this node covers. If the answer is "no, just the ethics part" or "no, just the epistemology," the node needs splitting.

This granularity rule does the work that edge-internal qualifiers would otherwise have to do. If nodes are fine-grained enough, each edge is a clean prerequisite claim and doesn't need metadata about *which aspect* of the source node matters. It also makes mastery assessment feasible per-session — a concept-level node like "Transcendental Idealism" is assessable; a thinker-level node like "Kant" is not.

### Cross-Domain Porosity
**Added: 2026-04-07**

All domains are mutually porous. Cross-domain prerequisite edges are first-class graph elements, not a future expansion feature. No domain can claim complete coverage without nodes from neighboring domains — you cannot master Existentialism without understanding the historical context of early 20th century Europe, and you cannot master the Categorical Imperative without understanding the Enlightenment as an intellectual movement.

**Termination principle:** Prerequisite chains terminate when further depth stops affecting comprehension of the target concept. A service node from another domain carries exactly enough depth to make the target concept comprehensible, and no more. "The Scientific Revolution as an intellectual event" is a prerequisite for Kantian Epistemology. "17th century Dutch trade networks" is not, even though it contributed to the conditions that made the Scientific Revolution possible. The pedagogical prerequisite test — "would a learner struggle without this?" — is the boundary.

**Domain density hierarchy for philosophy:** Not all neighboring domains contribute equally. History has the highest cross-domain prerequisite density — almost every philosophical concept has a historical prerequisite. Logic and Mathematics are structurally necessary for the analytic tradition. Psychology, Economics, Theology, and Natural Sciences (at the conceptual level) contribute medium-density prerequisites. Sociology and Linguistics contribute fewer but genuine prerequisite nodes. Literature, visual art, music, and film are mostly enrichment metadata on concept nodes (commitment 3), with rare exceptions where they are genuine prerequisites (e.g., Aesthetics requires encountering actual art).

**Reference domain list:** The following domains are used as tags on concept nodes for globe visualization coloring and filtering. This list is a suggested vocabulary for tagging consistency, not a taxonomy to enforce. Drawn from ISCED-F 2013 narrow fields and adapted to Paideia's humanities-centered mission. Domain tags are flat labels with no hierarchy — the globe's spatial grouping comes from edge topology via community detection (see ui-architecture.md), not from domain categories.

- Philosophy & Ethics
- History & Archaeology
- Religion & Theology
- Arts (visual, performing, music)
- Languages & Linguistics
- Psychology
- Economics
- Political Science
- Sociology
- Law (conceptual — jurisprudence, rights theory)
- Mathematics & Logic (service nodes — conceptual, not operational)
- Natural Sciences (service nodes — conceptual, not operational)

New domains can be added as tags without migration. The graph structure doesn't change; only the domain metadata on nodes does.

### Rigor Score (Node Property)
**Added: 2026-04-07 | Revised: 2026-04-09**

Each concept node carries a **rigor score** — a continuous value (0.0–1.0) that determines assessment depth, decay behavior, and mastery verification difficulty. Low scores (e.g. 0.15 for Cartesian Dualism) indicate concepts that are structurally foundational, simple to hold, and stable once understood. High scores (e.g. 0.85 for Transcendental Idealism) indicate concepts that are internally complex, structurally load-bearing, and fragile without active maintenance.

Full behavioral implications are described in pedagogy.md under "Rigor Score" and in learner-model.md under Mastery Computation and Mastery Decay.

#### Rigor Score Computation
**Added: 2026-04-09**

The rigor score is computed from graph topology using three signals:

**Inbound rigor mass.** The sum of rigor scores of the node's immediate prerequisites. A concept whose prerequisites are themselves complex is likely complex. This signal is recursive and computed bottom-up: root nodes (no prerequisites) receive a base score near zero, and complexity propagates upward through the graph.

**Prerequisite count.** The raw number of inbound prerequisite edges. A concept requiring many prerequisites integrates more ideas, which correlates with conceptual difficulty.

**Maximum downstream depth.** The longest path from this node to any terminal node (a node with no outbound edges). This captures how far the consequences reach if this node decays — the cost of failure, not the difficulty of the concept itself.

**Formula:**
```
rigor_score_computed = clamp(
  α * normalized_inbound_rigor_mass +
  β * normalized_prerequisite_count +
  γ * normalized_max_downstream_depth,
  0.0, 1.0
)
```

**V1 parameter defaults:** α = 0.5, β = 0.3, γ = 0.2. These weights favor "how hard are the things you need to know first" (α) over structural importance (γ). All three signals are normalized against the graph's own distribution (min-max scaling across all nodes) before weighting.

The computation is a one-time bottom-up traversal run whenever the graph changes. Root nodes (zero inbound edges) receive a rigor score near zero. The recursion terminates because the graph is a DAG — a cycle in the prerequisite graph is always a bug, and the computation hanging is a useful structural integrity check.

The formula is domain-agnostic. It produces sensible scores for any knowledge domain because it only references graph topology, not domain-specific properties.

#### Two-Column Override Model
**Added: 2026-04-09**

The node schema stores two columns: `rigor_score_computed` (always the formula output, never touched by humans) and `rigor_score_adjustment` (a human-applied delta, defaulting to 0.0). The effective rigor score consumed by all downstream systems is:

```
effective_rigor = clamp(rigor_score_computed + rigor_score_adjustment, 0.0, 1.0)
```

**Adjustments do not propagate.** The formula always runs on `rigor_score_computed` values of prerequisite nodes, ignoring any adjustments applied to them. This eliminates cascading effects: an editorial adjustment on one node changes only that node's effective score. Downstream nodes whose computed scores depend on the adjusted node are unaffected because the formula sees the computed value, not the adjusted one.

This design keeps the computation pure, makes overrides local by construction, and produces an audit trail — you can always see what the formula said versus what the human decided. An adjustment of -0.2 communicates "this is moderately simpler than topology suggests" more clearly than an opaque override value.

Editorial adjustments should result from considered analysis and evidence that the computed score is incorrect — not from casual opinion. The Opus batch review (see self-correction.md) can propose adjustments alongside edge edits.

### Node Schema
**Added: 2026-04-09 | Revised: 2026-04-30 (S-0010 — `confidence_level` column added per Phase 1.3 and [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md))**

```sql
CREATE TABLE nodes (
  id                      TEXT PRIMARY KEY,
  label                   TEXT NOT NULL,
  domain                  TEXT[] NOT NULL,
  summary                 TEXT NOT NULL,
  teaching_notes          TEXT,
  aliases                 TEXT[] DEFAULT '{}',
  rigor_score_computed    REAL NOT NULL DEFAULT 0.5,
  rigor_score_adjustment  REAL NOT NULL DEFAULT 0.0,
  provenance              TEXT NOT NULL DEFAULT 'human',
  confidence              REAL NOT NULL DEFAULT 1.0,
  confidence_level        TEXT NOT NULL DEFAULT 'INTERPRETED',
  status                  TEXT NOT NULL DEFAULT 'active',
  superseded_by           TEXT[] DEFAULT '{}',
  graph_version_added     INTEGER NOT NULL DEFAULT 1,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Column justifications:**

- **id** (TEXT): Human-readable slugified concept name (e.g. `transcendental_idealism`, `french_revolution`). Readable across every domain without needing a label lookup.
- **label** (TEXT): Display name. "Transcendental Idealism," "The French Revolution."
- **domain** (TEXT[]): Flat domain tags for color-coding and filtering on the globe. No hierarchy — spatial grouping comes from edge topology (see ui-architecture.md). Array because boundary concepts belong to multiple domains (e.g. `['ethics', 'epistemology']` for the categorical imperative).
- **summary** (TEXT): Concise semantic fingerprint (one to two sentences) optimized for the entity resolution service. Stable, search-oriented, not pedagogical.
- **teaching_notes** (TEXT, nullable): Pedagogical guidance specific to this concept — known confusion points, recommended teaching mode entry points, common misunderstandings. Consumed by the teaching AI alongside prerequisites and learner state. Provides a per-node remediation avenue for addressing pedagogical shortcomings without reshaping the node design or system-level weights.
- **aliases** (TEXT[]): Alternative names for entity resolution. Translational variants ("das Ding an sich"), abbreviations ("JTB"), common phrasings ("the problem of other minds"). The entity resolution service matches incoming references against labels, aliases, and summaries.
- **rigor_score_computed** (REAL): Formula output from graph topology. Never manually edited. See Rigor Score Computation above.
- **rigor_score_adjustment** (REAL): Human-applied delta. Defaults to 0.0. Does not propagate to downstream computations. See Two-Column Override Model above.
- **provenance** ('human' | 'ai_proposed' | 'ai_confirmed'): Who created the node and its lifecycle stage. Mirrors the edge provenance model. AI-proposed nodes enter via the self-correction pipeline (e.g. Opus recommending a node split). Human-curated nodes require stronger counter-evidence to deprecate.
- **confidence** (REAL, 0.0–1.0): How certain we are that this node belongs in the graph at all. Orthogonal to provenance — a human-curated node has high confidence; an AI-proposed split candidate starts low and rises as evidence accumulates. **Updates over time** as evidence accumulates through learner events and Opus batch review.
- **confidence_level** ('EXTRACTED' | 'INTERPRETED' | 'SYNTHETIC'): Categorical label for the *type* of evidence backing the node's existence, fixed at authoring time. Per [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md), this is a third epistemic axis orthogonal to `provenance` (who authored) and to numeric `confidence` (how sure we are it belongs and how that belief moves with evidence). **Does not update over time** — the label records the evidentiary mode at the moment of authoring; supersession is the channel for changing that record (a node split's replacement nodes carry their own authored `confidence_level`). Enum semantics:
  - **EXTRACTED:** The concept is lifted from a source's own structuring — a SEP article whose TOC names it as a coherent unit, a curriculum prerequisite list, a graph dataset already framing it as a node. The pedagogical work is vocabulary alignment, not concept invention. Highest evidentiary mode: a third-party source has independently judged the concept coherent at the granularity it appears.
  - **INTERPRETED:** The concept emerges from pedagogical judgment about source material that does not itself structure around the concept. Source material exists and is consulted; the human curator or AI infers that the concept exists at the granularity required by the Node Granularity Principle. Most Phase 5 first-pass nodes are INTERPRETED (per [ROADMAP.md](../ROADMAP.md) Phase 5.2 — "Generate first-pass prerequisite edges via Claude; mark `confidence_level: INTERPRETED` until validated against learner outcomes or expert review").
  - **SYNTHETIC:** The concept is generated wholesale, with no clear source structuring it as a coherent unit. Service nodes constructed to terminate cross-domain prerequisite chains (per the Termination Principle in Cross-Domain Porosity above) are common SYNTHETIC candidates: the graph needs them for prerequisite chains to close cleanly, but no source frames them as named concepts. Opus batch-review node-split proposals that lack direct source basis also start as SYNTHETIC. **First candidates for self-correction review** per [`docs/self-correction.md`](self-correction.md) and the Phase 4 audit soft-warn category per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) and [ROADMAP.md](../ROADMAP.md) Phase 4.

  The default `'INTERPRETED'` matches Phase 5.2's seed-authoring baseline and is the middle epistemic claim. Authoring sessions that produce SYNTHETIC service nodes or EXTRACTED corpus-aligned nodes must downgrade or upgrade explicitly. The naming risk — `confidence_level` reads as a finer version of `confidence` despite being a categorical evidentiary mode rather than a numeric belief — is acknowledged in [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md); the ADR is the durable mitigation.
- **status** ('active' | 'deprecated'): Whether the node participates in traversal and teaching. Deprecated nodes are retained because learner events reference them by ID.
- **superseded_by** (TEXT[]): When a node is split, points to the replacement node IDs. Enables learner event remapping and audit trails. Empty for active nodes.
- **graph_version_added** (INTEGER): The value of the graph_version counter when this node was created. Enables historical graph reconstruction without a full edits log. See Node Versioning below.
- **timestamps**: created_at and updated_at are table stakes.

**What is not on the node table:**

- **Source recommendations** (books, editions, translations per concept): Many-to-many relationship — belongs in a junction table between nodes and a sources table.
- **Globe position** (x/y/z coordinates): Computed by layout algorithm from edge topology. Storing it creates a maintenance nightmare on every graph edit.
- **Learner-facing label**: The label should just be good. If it's intimidating, that's a UI problem (tooltips, subtitles), not a schema problem.
- **Era/period tag**: Too domain-specific. The teaching AI infers temporal context from prerequisites and description.
- **Cluster assignment**: Computed by community detection at the rendering layer. Not stored.

### Edge Schema
**Added: 2026-04-07 | Revised: 2026-04-09**

Edges are not bare foreign key pairs. Each edge carries metadata that serves distinct, load-bearing functions:

```sql
CREATE TABLE edges (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id           TEXT NOT NULL REFERENCES nodes(id),
  target_id           TEXT NOT NULL REFERENCES nodes(id),
  edge_type           TEXT NOT NULL DEFAULT 'pedagogical_prerequisite',
  weight              REAL NOT NULL DEFAULT 1.0,
  provenance          TEXT NOT NULL DEFAULT 'human',
  confidence          REAL NOT NULL DEFAULT 1.0,
  evidence            TEXT,
  graph_version_added INTEGER NOT NULL DEFAULT 1,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE (source_id, target_id, edge_type)
);
```

**Column justifications:**

- **weight** (0.0–1.0): How strong the prerequisite relationship is *if it exists*. 1.0 = hard prerequisite ("you will struggle without this"). 0.3 = helpful context ("useful background but not strictly necessary"). Load-bearing for path generation: when building a syllabus to a target, should it include soft prerequisites or skip them based on time constraints?
- **provenance** ('human' | 'ai_proposed' | 'ai_confirmed'): Who created the edge and its lifecycle stage. Human-curated edges require stronger counter-evidence to remove. AI-proposed edges start at lower confidence. The three values capture the lifecycle: AI proposes → evidence accumulates → human or system confirms.
- **confidence** (0.0–1.0): How certain we are that this relationship exists at all. Orthogonal to weight. An AI-proposed edge might have high weight (if it exists, it's critical) but low confidence (we're not sure it exists). A human-curated edge has high confidence but might have low weight (helpful, not essential). Both dimensions are necessary.
- **evidence**: Free-text field for why this edge exists. Useful for debugging, user review of AI-proposed edges, and the self-correction audit trail. May be structured (JSON) later if needed.
- **graph_version_added** (INTEGER): The value of the graph_version counter when this edge was created. Enables historical graph reconstruction alongside the same column on nodes. *(Added: 2026-04-09)*
- **timestamps**: created_at and updated_at are table stakes.
- **edge_type**: Text field (not enum) so new types can be added without migration. Only `pedagogical_prerequisite` is used in traversal, syllabus generation, and mastery computation. Other types (e.g. `historical_influence`) are display features, not structural. No application logic should be built around non-pedagogical edge types until needed.

**Unique constraint on `(source_id, target_id, edge_type)`**: Multiple edge types between the same node pair are needed (pedagogical prerequisite vs. historical influence between related concepts). Multiple edges of the *same type* between the same pair are not — the self-correction system should update the existing row, not create a duplicate. The database enforces this, which is cheaper and safer than application logic.

**Prior art:** The ACE paper (Aytekin et al., Journal of Educational Data Mining) formalizes Educational Knowledge Graphs with prerequisite scoring that is conceptually similar to the confidence field. The Graphiti framework (Zep) implements episode-to-edge provenance tracing that parallels the self-correction feedback loops. Both validate the column choices but neither provides an off-the-shelf schema — the integrated system (pedagogical edges + confidence-weighted self-correction + AI teacher generating correction proposals in Postgres) is novel.

### Portable Mastery
**Added: 2026-04-07**

Mastery is per-concept, not per-concept-per-path. If a user masters "Empiricism" while studying toward Kant, that mastery fully transfers to a Philosophy of Science path. The globe shows one glow state per concept. The mastery computation function is `f(events for user U and concept C) → score` with no path dimension.

If mastery of a concept doesn't transfer well to a new context, that is evidence the node is too coarse and should be split (see Node Granularity Principle above). The correct response is a graph edit, not context-dependent mastery scoring.

Path context is still recorded on each learner event (which learning path the user was on when they engaged). This metadata supports analysis — e.g., "do certain paths produce better mastery?" — but is not used in the mastery computation itself.

### Node Versioning
**Added: 2026-04-07**

Full node versioning (each edit creates a new version; learner events point to the version they interacted with) is not justified at current scale (n=1–3 users with infrequent graph edits). But the decision must be made at schema time, because retrofitting versioning onto an unversioned schema requires migrating every existing learner event.

**Decision: graph_version monotonic counter.** A `graph_version` integer in a settings table is incremented whenever any node or edge is edited. Each learner event records the current graph_version at time of creation. This is not node-level versioning — it's a global counter that says "the graph had been edited N times when this event was recorded."

This makes future full versioning a migration rather than a reconstruction: when needed, pair the counter with a `graph_edits` log table (which node changed, when, what the old value was) to reconstruct which graph state any event was recorded against. The edits log table can be added later; the counter on events must be there from day one.

Both the nodes and edges tables carry a `graph_version_added` column recording the counter value at creation time. This enables lightweight historical reconstruction without the full edits log. *(Revised: 2026-04-09)*

At concept-level granularity the graph will have hundreds of nodes, not dozens. The graph_version approach scales to this — it's one integer per event regardless of node count.

## Ideas as Nodes, Books as Metadata
**Added: 2026-04-07**

The graph's fundamental unit is the idea, not the book. Books are many-to-many metadata on nodes — sources where an idea can be encountered, studied, or deepened. One idea may appear across several books; one book may contain dozens of ideas. This means the graph tracks what the user actually understands, not what they've read. A user who reads all of the Critique of Pure Reason without grasping transcendental idealism has not mastered that node.

The app carries its own source recommendations per node (editions, translations, annotated versions). Users can optionally input their existing library or reading history to enable gap detection (books they don't own that would unlock graph paths) and source-preference routing (which of their books best teaches a given concept). A user's personal library is an input signal, not a design dependency — the system assumes nothing about what any user owns.

## Entity Resolution Service
**Added: 2026-04-08**

Entity resolution — mapping a freeform string like "Kant's epistemology" or "the problem of induction" to one or more concept nodes in the graph — is a shared operation that serves multiple pipelines. The teaching session context uses it for resolving spontaneous learner references against the two-hop neighborhood. The close reading outline generation uses it for mapping text sections to mastery graph concepts. The syllabus upload pipeline uses it for mapping course topics and readings to graph nodes. All three need the same core capability: take a natural-language reference and resolve it against the node inventory with fuzzy matching, partial matching, and clean miss detection.

**Fuzzy matching** handles vocabulary variation. A syllabus that says "the problem of induction" must resolve to a graph node labeled "Humean Skepticism about Induction" or similar. This is semantic similarity, not string matching — the resolution layer needs access to node labels, aliases, and summaries.

**Partial matching** handles granularity mismatch. A syllabus that says "Kant" or "Kantian philosophy" must resolve to the set of Kant-related concept nodes (Transcendental Idealism, Categorical Imperative, Synthetic A Priori, etc.), not to a single node. The resolution returns a set of candidates with confidence scores, and the calling pipeline decides how to use them.

**Clean misses** must be reported honestly. When a reference doesn't match anything in the graph, the system says so rather than forcing a bad match. The calling pipeline decides how to handle the miss — the syllabus pipeline flags it to the professor, the teaching session logs it as a tension record, the outline generator notes it as a gap.

The entity resolution service is shared infrastructure. The teaching session uses it against the two-hop neighborhood (lightweight, low-latency). The close reading and syllabus pipelines use it against the full graph (heavier, but these are ingestion-time operations, not real-time). The same resolution logic scales to both contexts by accepting a node set as input rather than always querying the full graph.

## Syllabus Upload Pipeline
**Added: 2026-04-08**

A professor (or autodidact following an online course) uploads a course syllabus. The system parses it, maps it to the mastery graph, identifies prerequisite gaps, and generates a constrained learning path. The syllabus is a constraint on graph traversal, not a replacement for it — the professor's sequencing is respected, and the system catches learners who can't make the inferential leaps the syllabus silently demands.

### Pipeline Steps

**Step 1: Parse.** Opus extracts structured data from a short semi-structured document (typically 2–5 pages). The output is a sequence of topic-reading pairs with ordering information: Week 1, "Introduction to Philosophy / Descartes, Meditations I-II"; Week 2, "The Problem of Knowledge / Hume, Enquiry §4-5." Syllabi have high structural regularity across institutions. No chunking or embedding needed — this is information extraction from a short document.

**Step 2: Resolve.** Each topic and reading passes through the entity resolution service against the full graph. "Descartes, Meditations I-II" resolves to concept nodes like "Cartesian Doubt," "Cogito," "Mind-Body Dualism" and to a text reference in the reading system. "The Problem of Knowledge" resolves to concept nodes like "Empiricism," "Rationalism," "Skepticism." Each resolution carries a confidence score. Ambiguous and empty resolutions are flagged for the next step.

**Step 3: Gap analysis.** Take the resolved concept nodes in syllabus order. For each one, check its prerequisites against what the syllabus has already covered earlier in its sequence and against the learner's current mastery state. Any prerequisite that the syllabus doesn't cover and the learner hasn't mastered is a gap. These gaps are what the system fills. A Phil 101 syllabus that jumps from Descartes to Kant assumes students will absorb Empiricism, Hume's fork, and the Analytic-Synthetic distinction in the process. The system makes that assumption explicit and generates teaching for those gaps.

**Step 4: Generate constrained path.** The output is a learning path that interleaves the syllabus's own sequence with prerequisite gap-fill. The professor's ordering is preserved — the system inserts prerequisite concepts before the syllabus topics that need them, never reorders the syllabus itself. The constrained path is a first-class data object that references graph nodes, carries the professor's sequence as a structural constraint, and can be assigned to multiple learners.

### Failure Modes

**Near-miss.** The syllabus says "virtue ethics" and the graph has "Eudaimonia" and "Aristotelian Virtue." Entity resolution handles this — the resolved nodes cover the syllabus topic. No user-facing issue.

**Genuine gap.** The syllabus covers a topic the graph doesn't have nodes for. The system flags it: "This syllabus covers [topic]. The system doesn't have structured teaching for this yet. Surrounding concepts are covered." This is an acceptable v1 failure — it tells the professor exactly where coverage ends, and it generates a tension record that feeds graph expansion.

**Mostly outside coverage.** If the syllabus is predominantly outside the graph's coverage (a Phil 400 seminar on specialized topics), the system should say so upfront rather than producing a path that's more gap than coverage. The threshold is a judgment call, but roughly: if fewer than half the syllabus topics resolve to graph nodes, the system should be honest that coverage is too thin to be useful.

### Relationship to Close Reading

The syllabus pipeline and the close reading pipeline share the entity resolution service but diverge after that point. The syllabus pipeline produces a constrained learning path (a sequence of graph nodes with gap-fill). The close reading pipeline produces an interpretive outline (a section-by-section teaching plan encoding argument structure and teaching modes). These are structurally different artifacts. The close reading pipeline needs chunking, embedding, and Opus-generated outlines. The syllabus pipeline needs information extraction from a short document and graph traversal for gap analysis. Forcing them into a single abstraction would create complexity without benefit.

## Institutional Schema Provisions
**Added: 2026-04-08**

The system is built for individual learners first. Institutional use (community college departments assigning the tool to classes) is the eventual market but not the v1 build target. The following schema provisions preserve the institutional path without building the enterprise wrapper now.

**Cohort association on learner events.** The learner event schema carries a nullable `cohort_id` field. In v1, this is always null — every learner uses the app independently. When institutional use becomes viable, a cohort represents a course section: "Phil 101, Fall 2027, Prof. Martinez." The cohort_id on events enables queries like "aggregate mastery for all learners in this section" without schema migration. The mastery computation ignores cohort_id — mastery is always per-learner, never averaged or pooled.

**Shareable constrained paths.** The constrained path produced by the syllabus upload pipeline has an ownership model. In v1, the creator owns it and it governs their own learning. When institutional use becomes viable, a professor creates a constrained path from their syllabus and assigns it to a cohort. Each student's mastery state is individual, and the gap-fill may differ per student (one already knows Empiricism, another doesn't), but the syllabus constraint is shared. The data model supports this from day one: the constrained path references graph nodes and the cohort, not individual learner state.

**What is explicitly deferred.** LMS integration (Canvas/Blackboard LTI), instructor dashboards, FERPA compliance review, grade export, and institutional onboarding workflows. All of these are bolt-on features that sit above the data model. None require schema changes — they are API adapter layers, read-only views over existing data, and policy/process work. They should not be built until the teaching system has proven itself with real learners and an institutional pilot is concretely in scope.

**Privacy posture inheritance.** Per [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) (persistent learner storage is structural, not substantive), cohort-bound events under any future institutional regime layer additional constraints on top of the structural baseline; they do not have to retroactively strip substantive content because none was persisted in the first place. The institutional vs. individual data regime is open as **OQ-PRIVACY-B** in [`tensions.md`](tensions.md) — column slot reservation lands at Phase 3, policy specification lands at Phase 8 alongside actual institutional partner conversations.

---
*Last updated: 2026-04-30 (S-0010 — `confidence_level` column added to Node Schema per Phase 1.3 and [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md); orthogonality with `provenance` and `confidence` recorded inline. Prior footer dated 2026-04-09 — S-0007's privacy-posture-inheritance paragraph in Institutional Schema Provisions did not bump the footer; CHANGELOG remains the authoritative session-by-session ledger.)*
