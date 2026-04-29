# Design Reasoning

**Added: 2026-04-09**

Records *why* specific design decisions were made. Each entry names the commitment, explains the reasoning, and references where the decision is expressed. Prevents future sessions from re-arguing settled questions without new evidence.

**Inclusion test:** Does this entry explain reasoning that, if absent, would risk a future session reversing a decision without understanding the constraint it satisfies? If yes, it belongs here.

---

## Nodes Are Concepts, Not Thinkers (Commitment 8)

The graph needed an atomic unit that makes clean prerequisite claims. A thinker-level node like "Kant" forces every outbound edge to claim that *all of Kant* is required — which is never true. A downstream concept might need Transcendental Idealism but not the Categorical Imperative. Concept-level granularity eliminates the need for edge-internal qualifiers ("which aspect of the source matters?") because each edge is a complete claim: this entire node is required for that entire node. The granularity principle also makes per-session assessment feasible — you can assess whether someone grasps Transcendental Idealism in a conversation; you cannot assess whether they grasp "Kant."

The original prototype used thinker-level nodes (45 of them). It was deprecated because the edge claims were too coarse to be meaningful.

**Decision expressed in:** architecture.md (Node Granularity Principle), CONTEXT.md (commitment 8)

---

## Portable Mastery, Not Per-Path Mastery (Commitment 9)

The alternative was tracking mastery per-concept-per-path — so a user could "master" Empiricism on the Kant path but still be unmastered on the Philosophy of Science path. This was rejected because it violates what mastery means. If understanding a concept doesn't transfer to a new context, either the learner doesn't actually understand it or the node is too coarse and should be split. The granularity principle does the corrective work: when portable mastery fails, it's a signal to edit the graph, not to add a path dimension to mastery scoring.

Path context is still recorded on events for analysis (which paths produce better mastery), but the mastery computation function has no path parameter.

**Decision expressed in:** architecture.md (Portable Mastery), CONTEXT.md (commitment 9)

---

## Supplementary Media as Metadata, Not Structure (Commitment 3)

Film, art, and music connections don't create prerequisite edges because the prerequisite test — "would a learner struggle without this?" — almost never holds for media. You can master Existentialism without watching Bergman. The rare exceptions (Aesthetics requires encountering actual art) are handled by making those encounters nodes in their own right, not by giving media structural graph power. If media created edges, the graph's topological sort would route learners through films and albums as mandatory prerequisites, which is pedagogically wrong and would make path generation unpredictable.

**Decision expressed in:** CONTEXT.md (commitment 3), expansion.md (Supplementary Media Layer)

---

## Freshman Defaults with Autodidact Ceiling (Commitment 12)

The asymmetry of failure is directional. A freshman encountering content beyond their scope cannot proceed — and the failure feels like inadequacy, which is destructive. An autodidact encountering freshman-level calibration is mildly annoyed for a few exchanges before the adaptive system escalates. The cost of defaulting too low is brief annoyance; the cost of defaulting too high is a learner who quits. Both audiences are served by the same product because the diagnostic conversation and first few exchanges generate enough signal to recalibrate rapidly. Neither audience needs to know the other exists.

**Decision expressed in:** pedagogy.md (V1 Calibration Defaults), business.md (Audience vs. Market), CONTEXT.md (commitment 12)

---

## Mastery Verification as Organic Escalation, Not Cross-Syllabus Interruption

The original design had mastery verification interrupt whatever the user was currently doing — pull them out of a downstream concept to test an upstream one. This was replaced because it breaks the conversational flow that the expression contract depends on, and because good teaching already revisits upstream concepts naturally. When you teach Phenomenology, you *have to* reference Transcendental Idealism. Those callback references are both genuine pedagogy and mastery probes. Letting them accumulate evidence over several downstream concepts produces higher-quality verification than a scheduled interruption, because the scaffolding proximity is lower (the original teaching is days or weeks behind) and the context is novel (the concept is being applied, not restated).

**Decision expressed in:** pedagogy.md (Mastery Verification), session-lifecycle.md (Mastery Verification Through Downstream Teaching)

---

## Sonnet Teaches, Opus Reviews (Self-Correction Pipeline)

Sonnet does not diagnose graph errors in real time because doing so would require carrying the full graph in context during teaching sessions, and because single-signal corrections are dangerous — one learner struggling once is not evidence of a bad edge. Sonnet's job is to log tensions (structured observations that something didn't resolve through normal teaching moves). Opus reviews accumulated tensions in batch because patterns across sessions and learners are qualitatively different from individual moments. A week of tension data showing three learners all struggling at the same transition is a structural signal; one struggle is noise.

The batch cadence also ensures graph stability between review cycles — learners never encounter mid-session structural changes to the graph they're traversing.

**Decision expressed in:** self-correction.md (Self-Correction Pipeline, Tension Log Schema)

---

## Bring Your Own Book (Commitment 11)

The app could theoretically host copyrighted texts under various licensing arrangements. This was rejected for three reasons. First, it creates a licensing dependency that scales with every domain — each new field would require separate publisher negotiations before launch. Second, it makes the mastery graph's copyright profile depend on the close reading system's copyright profile, coupling two surfaces that should be independent. Third, the user-supplied model creates appropriate friction: by the time someone uploads a text, they've been learning conversationally, encountered a concept that warrants deeper engagement, received an AI recommendation, and decided to invest. That friction filters for genuine interest.

The clean separation means the mastery graph teaches parametrically with zero copyright exposure in every domain, forever, regardless of what happens with close reading.

**Decision expressed in:** content-strategy.md (Copyright Model), reading-system.md (Architecture), CONTEXT.md (commitment 11)

---

## Event-Sourced Learner Model, Not State Table

A mutable `mastery_level` column on a `user_concepts` table would be simpler to query but would foreclose five requirements that emerged during design: temporal decay (needs timestamps per event), false mastery detection (needs comparison of current vs. earlier evidence), path efficiency tracking (needs path context per event), source effectiveness (needs source context per event), and cross-domain bridge discovery (needs freeform interaction logging). Each of these requires the event history, not just the current state. The event-sourced architecture is more complex to query but makes all five analyses possible without schema migration.

**Decision expressed in:** learner-model.md (Event-Sourced Architecture)

---

## Domain-Agnostic Architecture with Philosophy First (Commitment 6)

The temptation was to build philosophy-specific data structures and generalize later. This was rejected because the graph schema, edge semantics, learner event model, and teaching system have no philosophy-specific logic in them — and introducing any would create migration debt when the second domain arrives. The cost of building domain-agnostic from day one is near zero (domain is a tag on nodes, not a structural partition). The cost of retrofitting would touch every table and every query.

Philosophy is first because it has the densest prerequisite structure, the richest cross-domain connections, and the best-understood corpus — making it the hardest test case for the architecture, not the easiest.

**Decision expressed in:** CONTEXT.md (commitment 6), architecture.md (Cross-Domain Porosity)

---

## Relational Graph in Postgres, Not OWL/RDF or Graph Database
**Added: 2026-04-09**

OWL/RDF is the standard for knowledge graphs and would provide transitive closure inference, SPARQL for traversal, and interoperability with Wikidata/DBpedia. A dedicated graph database (Neo4j, etc.) would provide native Cypher traversal. Both were rejected because they solve problems Paideia doesn't have and don't solve the one it does.

Paideia's graph traversal is narrow: "given a target concept, return the topologically sorted prerequisite chain, filtered by the learner's mastery state." That's a directed traversal with a filter join against relational event data. The heavy computation is the mastery function running against temporal events in Postgres — not open-ended semantic reasoning across rich ontological relationships.

OWL class hierarchies would reintroduce thinker-level aggregation ("Kantian Epistemology" as a superclass containing Transcendental Idealism, Synthetic A Priori, etc.), which the node granularity principle explicitly rejected. Entity resolution — the one place semantic structure would help — is an LLM task (fuzzy matching against labels and aliases), not a logical entailment task.

A dedicated graph store means a second data system, a second query language, and cross-system joins for mastery-filtered traversal. At projected scale (hundreds to low thousands of nodes), Postgres handles graph traversal natively with recursive CTEs. The performance case for a graph database doesn't exist until tens of thousands of nodes with complex multi-hop queries.

Migration risk is low in both directions. Nodes and edges in Postgres export trivially to RDF triples if the need ever arises.

**Decision expressed in:** architecture.md (Graph Structure), infrastructure.md (Cloud Hosting Stack)

---

## Domain Tags as Flat Labels, Not Hierarchical Taxonomy
**Added: 2026-04-09**

The initial instinct was to build a domain hierarchy (Philosophy → Epistemology, Ethics, Metaphysics) and use it to organize the globe into continental regions and sub-regions. This was rejected for two reasons.

First, the categories don't map to spatial regions. Ethics concepts don't cluster in one area of the globe — the categorical imperative is spatially near transcendental idealism (its prerequisite) not near eudaimonia (its fellow ethics concept). The globe's layout is determined by edge topology, not by labels. Imposing categorical regions would either conflict with the topology or redundantly mirror it.

Second, categorical boundaries are non-linear and contested. Is the categorical imperative ethics or epistemology? Is historical materialism political philosophy or economics? Forcing concepts into a hierarchy requires judgment calls that add no pedagogical value and create maintenance burden.

Domain tags are flat labels stored as an array on each node. They provide color-coding and filtering on the globe. Spatial grouping at different zoom levels comes from community detection algorithms (Louvain/Leiden) running on edge topology — the clusters are emergent from actual prerequisite relationships, not imposed by a taxonomy. This approach is domain-agnostic: it produces sensible visual groupings for any domain without domain-specific configuration.

**Decision expressed in:** architecture.md (Node Schema, Cross-Domain Porosity), ui-architecture.md (Level-of-Detail Rendering)

---

## Two-Column Rigor Score Override Model
**Added: 2026-04-09**

The rigor score is computed from graph topology but needs occasional human correction. The naive approach — a single column that's either computed or manually overridden — creates a cascading problem. The formula is recursive (a node's score depends on its prerequisites' scores). If you override one node, every downstream node's computed score shifts. If any of those downstream nodes were also overridden, you have a conflict: does the downstream override hold, or is it now stale because its input changed?

The solution separates the computed value from the human adjustment into two columns. `rigor_score_computed` is always the formula output, never manually touched. `rigor_score_adjustment` is a human-applied delta (defaulting to 0.0). The effective score is `clamp(computed + adjustment, 0.0, 1.0)`. The formula always runs on computed values only — adjustments are invisible to propagation.

This eliminates cascading entirely. An editorial adjustment on one node changes only that node's effective score. No downstream node is affected because the formula never sees the adjustment. The adjustment also communicates intent more clearly than a raw override: an adjustment of -0.2 says "moderately simpler than topology suggests," while a raw override of 0.3 doesn't tell you what the formula would have produced.

Editorial adjustments should result from considered analysis and evidence, not casual opinion. The Opus batch review can propose adjustments alongside edge edits.

**Decision expressed in:** architecture.md (Rigor Score Computation, Two-Column Override Model, Node Schema)

---

## Teaching Notes as a Separate Column from Summary
**Added: 2026-04-09**

The node schema could have used a single `description` field. Two fields (`summary` and `teaching_notes`) were chosen because they serve different consumers with different optimization targets. The `summary` is a concise semantic fingerprint (one to two sentences) consumed by the entity resolution service — it needs to be stable, search-optimized, and tightly focused on what the concept *is*. The `teaching_notes` are pedagogical guidance consumed by the teaching AI — known confusion points, recommended entry modes, common misunderstandings.

More importantly, `teaching_notes` provides a per-node remediation avenue. When the teaching system consistently fails on a specific concept — learners misunderstand it, the AI approaches it wrong, the default teaching mode doesn't match the concept's shape — the fix can be a `teaching_notes` update rather than reshaping the node's structural properties or adjusting system-level weights. This keeps structural corrections (node splits, edge changes) separate from pedagogical corrections (better teaching guidance), which should have different review cadences and different evidence thresholds.

**Decision expressed in:** architecture.md (Node Schema)

---

## Node Provenance and Lifecycle (Status, Superseded_by)
**Added: 2026-04-09**

Nodes carry `provenance` and `confidence` mirroring the edge schema because the self-correction pipeline can propose node operations, not just edge operations. Opus might recommend splitting a node that's failing the granularity test. Those new nodes should enter the graph as `ai_proposed` with low confidence, accumulating evidence through the same confidence-weighted pipeline that governs edge additions.

The `status` and `superseded_by` fields handle node splits without data loss. When a node is split, the original is deprecated (stops participating in traversal and teaching) but retained because learner events reference it by ID. The `superseded_by` array points to the replacement nodes, enabling event remapping and audit trails. Without these fields, a node split would either orphan learner events (breaking mastery history) or require deleting and re-creating events (violating the event-sourced architecture's append-only principle).

**Decision expressed in:** architecture.md (Node Schema)

---

*Last updated: 2026-04-09 (added: OWL/RDF rejection, flat domain tags, two-column rigor score, teaching notes separation, node provenance and lifecycle)*
