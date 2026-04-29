# Paideia — Project Context

> **Read this file at the start of every session.** It is the canonical state of the project. Pull in downstream files as needed based on the conversation topic.

## What This Is

Paideia is a knowledge mastery app built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense, not just what influenced what.

Philosophy has the densest coverage first, but the graph is inherently multi-domain from day one. Philosophical concepts have prerequisite dependencies on history, psychology, economics, theology, logic, and the natural sciences. These cross-domain nodes are first-class graph elements, not future expansion. The architecture is domain-agnostic — the same graph structure, teaching system, and learner model serve any field where prerequisite relationships matter.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus (primary + supplementary) for each step. A persistent learner model tracks mastery across sessions and texts.

## File Index

| File | Contains | Pull when discussing... |
|------|----------|------------------------|
| `architecture.md` | Graph data model: node schema, edge schema, node granularity principle, cross-domain porosity, portable mastery, node versioning, rigor score (continuous, with computation formula and two-column override model), entity resolution service, syllabus upload pipeline, institutional schema provisions | Graph structure, schemas, what nodes and edges look like |
| `learner-model.md` | Event-sourced architecture, engagement depth (three signals), interaction types (six types incl. backward_inference), mastery decay (exponential with rigor-modulated parameters), mastery computation function (four-stage), offline/sync model | Mastery scoring, decay, learner events, how mastery is computed |
| `self-correction.md` | Five feedback loops, Sonnet/Opus pipeline boundary, tension log schema, teaching session context (two-hop neighborhood), batch review cycle, model tiering | Graph self-correction, tension logging, which model does what |
| `infrastructure.md` | Tech stack (Vercel + Supabase + Anthropic API), DeepTutor fork assessment, deployment target (native iOS/Android primary, web as test surface), MCP database access, prototype status, RAG pipeline, build approach, cost mitigation | How to build, what exists, hosting, engineering decisions |
| `ui-architecture.md` | Globe navigation model, level-of-detail rendering (community detection from topology), domain tags as color/filter (not spatial grouping), cross-domain tendrils, zoom behavior | Globe design, visualization, rendering at scale |
| `pedagogy.md` | Expression contract, teaching modes, assessment rubric (3 dimensions), scaffolding proximity, rigor score (assessment implications), learner-relative assessment, v1 calibration defaults, Style/instruction layering, learner model, mastery verification mechanics | Teaching behavior, Socratic mode, session design, assessment, audience calibration |
| `content-strategy.md` | Graph curation, source licensing, corpus pipeline, copyright model, user text ingestion pipeline, commerce layer | What goes in the graph, legal, data sources, close reading acquisition |
| `session-lifecycle.md` | Globe home screen, concept engagement model, mode transitions, proficiency/mastery UX, routing, mastery verification through downstream teaching | Entry flow, session design, interaction patterns, what the user sees |
| `reading-system.md` | Close reading as optional deep-dive, bring-your-own-book model, outline generation (parametric + optional commentary), domain-specific profiles, event emission to learner model, dialectical text handling | The close reading tool, text-level instruction, copyright constraints |
| `expansion.md` | Film/art/music layer, age-aware paths, family vision, new domains | Supplementary media, teaching children, broader scope |
| `business.md` | Commercial analysis, cost model, grant strategy, audience vs. market distinction, syllabus upload as institutional wedge | Money, pricing, audience, viability, institutional strategy |
| `tensions.md` | All unresolved questions and active tradeoffs | Any open question, what to think about next |
| `design-reasoning.md` | Why specific decisions were made — the reasoning behind commitments | When questioning or revisiting a settled decision, when adding a new commitment |
| `ideation.md` | Ideas captured in sessions but not yet consumed into downstream files | When an idea surfaces that isn't ready for a specific file |
| `_archive/` | Deprecated files preserved for reference | Historical context only |

## Current Phase

Design and prototyping. A working React prototype exists with ~45 philosophy nodes (at thinker-level granularity — deprecated, needs rebuilding at concept level). The reading system architecture is designed but not built. DeepTutor (Apache 2.0) identified as a fork candidate for implementation base — infrastructure reusable, pedagogical layer to be replaced. No infrastructure deployed. Primary deployment target: native iOS/Android apps; web retained as test surface and additional UI.

The schema foundations session (2026-04-07) settled four entangled questions: node granularity principle, concrete edge schema, node versioning (graph_version counter), portable mastery. Cross-domain porosity was established as a structural requirement. These decisions are recorded in architecture.md.

The session lifecycle session (2026-04-07) settled the globe-vs-syllabus relationship, concept engagement as the atomic learning unit, mode transition signals, proficiency-as-implied-transition, boss encounter UX, and the five-syllabus cap. These decisions are recorded in session-lifecycle.md.

The assessment & mastery verification session (2026-04-07) settled the three-dimensional assessment rubric (reconstruction, application, boundary awareness), scaffolding proximity as an evidence discount, rigor tiers as a per-node property scaling assessment thresholds, mastery verification as organic escalation within downstream teaching (replacing the cross-syllabus interruption model), engagement depth as a composite variable, five interaction types for the event log, and active-use decay suppression. These decisions are recorded in pedagogy.md, session-lifecycle.md, and architecture.md.

The self-correction pipeline session (2026-04-08) settled the Sonnet/Opus boundary for graph self-correction (Sonnet logs tensions, Opus reviews in batch), the tension log schema and tension type taxonomy, batch review cycles over real-time graph editing, and teaching session context requirements (current concept + prerequisites + two-hop local neighborhood for entity resolution of spontaneous learner references). These decisions are recorded in self-correction.md.

The reading system session (2026-04-08) settled the relationship between the mastery graph and close reading (mastery graph is the primary parametric teaching surface; close reading is an optional deep-dive), the "bring your own book" copyright model (user supplies all copyrighted text; the app never hosts or distributes copyrighted material), outline generation from parametric knowledge as baseline with user-supplied commentary as optional enhancement, domain-specific reading profiles (philosophy, literature, history, psychology), event emission from close reading to the learner model (high scaffolding proximity, moves concepts to exposed/proficiency but rarely mastery), dialectical text handling via teaching-mode encoding in outline entries, storage economics (negligible — ~150MB per user with 40 books), and the repeatable setup process per text. These decisions are recorded in reading-system.md and content-strategy.md; the "Outline Rigidity for Dialectical Texts" tension is resolved in tensions.md.

The product identity session (2026-04-08) settled the v1 audience defaults (freshman-level calibration with autodidact ceiling — the asymmetry of failure is directional, so defaults favor the learner who cannot recover on their own), the audience-vs-market distinction (community college students shape pedagogical defaults; departments are the deferred institutional market), the syllabus upload pipeline architecture (parse → resolve → gap analysis → generate constrained path, with entity resolution shared with the close reading pipeline), and institutional schema provisions (nullable cohort_id on events, shareable constrained paths) that preserve the institutional path without building the enterprise wrapper. Pricing was deferred as premature. These decisions are recorded in architecture.md, business.md, pedagogy.md, and tensions.md.

The learner model session (2026-04-09) settled the decay function (exponential with rigor-score-modulated parameters), the decay floor (conditional on having reached proficiency, scaled inversely by rigor score so simple concepts cannot decay below solid proficiency), the mastery computation function (four-stage: per-event decayed strength, asymptotic aggregation, conditional floor, fixed threshold state mapping at 0/0.3/0.7), backward inference as soft evidence injection (synthetic events modulated by prerequisite rigor score, propagating through immediate prerequisites only with natural attenuation), learner-relative assessment (AI evaluates against the learner's available conceptual vocabulary, not against the field), the rigor score as a continuous 0.0–1.0 value replacing the categorical rigor tier (computed from topology, stored as editable column), server-side mastery computation with thin native clients (event emitters and snapshot consumers), and offline sync via local event queuing with cached mastery snapshots. V1 parameter defaults: BASE_HALF_LIFE = 60 days, MAX_FLOOR = 0.6. Deployment target updated to native iOS/Android as primary with web as test surface. These decisions are recorded in learner-model.md and pedagogy.md.

The seed graph and node schema session (2026-04-09) settled the node schema (id, label, domain as flat tag array, summary, teaching_notes, aliases, rigor_score_computed, rigor_score_adjustment, provenance, confidence, status, superseded_by, graph_version_added, timestamps), the rigor score computation formula (weighted combination of inbound rigor mass, prerequisite count, and max downstream depth with V1 weights α=0.5, β=0.3, γ=0.2), the two-column rigor score override model (computed values never manually edited; human adjustments stored separately and do not propagate through the formula), domain tags as flat labels with no hierarchy (globe spatial grouping comes from community detection on edge topology, not categories), level-of-detail rendering via community detection algorithms (Louvain/Leiden), and the OWL/RDF assessment (rejected — Paideia's traversal needs are narrow and relational, not open-ended semantic reasoning). The seed graph rebuild was reclassified from a planning task to an implementation task — seeding happens directly in the database at build time, not via JSON. architecture.md was split into five files: architecture.md (graph data model), learner-model.md, self-correction.md, infrastructure.md, ui-architecture.md. The deprecated philosophy-graph-seed.json (v0.2, epistemology-focused) was archived. These decisions are recorded in architecture.md and ui-architecture.md.

## Strong Working Commitments

These are the strongest current ideas — not closed questions, but the positions that would require substantial new thinking to displace. Nothing is settled at this phase.

1. **Pedagogical edges, not historical.** The graph encodes "must understand X before Y" — never just "X influenced Y."
2. **Commercial sustainability without pedagogical compromise.** Revenue logic must never change what the product teaches or how it teaches. The product is designed to sustain itself financially and reach users beyond the builder. Personal use remains the primary testing ground for pedagogical quality. *(Revised: 2026-04-07 — replaces "build for yourself first")*
3. **Supplementary media is metadata, not structure.** Film, art, and music attach to concept nodes as companions. They never create prerequisite edges or structural dependencies in the graph.
4. **The learner model is relational.** It tracks connections between concepts and forward-looking teaching opportunities, not just a flat checklist.
5. **Each text gets its own interpretive outline.** No templates. The outline is generated at ingestion from the AI's parametric knowledge of the scholarly tradition, optionally enhanced by user-supplied commentary, and locked in before reading begins. The outline encodes argument structure, dialectical reversals, and teaching modes per section. *(Revised: 2026-04-08 — generalized from commentary-only generation to parametric-first with optional commentary)*
6. **Domain-agnostic architecture.** Philosophy is the first domain, not the only one. The graph, teaching system, and learner model are designed to work across any knowledge domain with prerequisite structure.
7. **All domains are mutually porous.** Cross-domain prerequisite edges are first-class graph elements. Prerequisite chains terminate when further depth stops affecting comprehension of the target concept. Service nodes from other domains carry exactly enough depth to make the target concept comprehensible. No domain can claim complete coverage without nodes from neighboring domains. *(Revised: 2026-04-07 — replaces narrower "math and science are service nodes" framing)*
8. **Nodes are concepts, not thinkers.** The graph's atomic unit is an idea — "Transcendental Idealism," "Eudaimonia," "Syllogistic Logic" — never a person or school. A node must be the smallest unit at which every inbound edge is required for the whole node and the whole node is required by every outbound edge. *(Added: 2026-04-07)*
9. **Mastery is portable.** One mastery state per concept, regardless of which learning path the user was on. If mastery doesn't transfer to a new context, the node is too coarse and should be split. *(Added: 2026-04-07)*
10. **Assessment is continuous and contextual.** The AI evaluates every exchange along three dimensions (reconstruction, application, boundary awareness), discounted by scaffolding proximity. The rigor score (continuous, 0.0–1.0) on each node scales assessment depth, decay rate, and decay floor. Assessment is learner-relative: the AI evaluates against what someone with the learner's current prerequisite mastery should be able to produce, not against the AI's own knowledge. Mastery verification happens organically within downstream teaching, never as a cross-syllabus interruption, and is never named or labeled to the user. *(Added: 2026-04-07 | Revised: 2026-04-09 — rigor score continuous; learner-relative assessment added)*
11. **The app never hosts or distributes copyrighted material.** The mastery graph teaches parametrically with no copyrighted text in context. Close reading uses a "bring your own book" model — all copyrighted material is user-supplied, stored in a user-scoped personal corpus. This separation is clean across every domain. *(Added: 2026-04-08)*
12. **Freshman defaults, autodidact ceiling.** The system calibrates cold-start defaults for a learner encountering ideas for the first time. The adaptive teaching system escalates rapidly based on engagement quality. Both audiences are served by the same product without either knowing the other exists. *(Added: 2026-04-08)*

## File Dependencies

When changing a commitment or a downstream file, check the files that depend on it. This is not exhaustive — it captures the high-value connections where a change would silently break something.

- **Commitments 8 or 9** (node granularity, portable mastery) → architecture.md (Node Granularity Principle, Portable Mastery, Edge Schema, Node Schema), pedagogy.md (assessment rubric assumes concept-level nodes)
- **Commitment 3** (media as metadata) → expansion.md, architecture.md (graph traversal assumes no media edges)
- **Commitment 11** (no hosted copyrighted material) → content-strategy.md (Copyright Model), reading-system.md (bring-your-own-book architecture)
- **pedagogy.md expression contract** (three teaching modes) ↔ session-lifecycle.md (mode transition signals) — these must stay synchronized; pedagogy states the principle, session-lifecycle operationalizes the triggers
- **learner-model.md engagement depth / scaffolding proximity** ↔ pedagogy.md (assessment rubric, mastery verification) — both define and consume the same evidentiary model
- **architecture.md entity resolution service** → reading-system.md (outline generation), architecture.md (syllabus upload pipeline), self-correction.md (teaching session context) — three consumers of the same shared capability
- **business.md audience defaults** ↔ pedagogy.md (V1 Calibration Defaults) — the audience decision drives the pedagogical starting posture
- **architecture.md rigor score computation** → learner-model.md (mastery decay, mastery computation) — the effective rigor score feeds decay rate, decay floor, and assessment calibration
- **architecture.md node schema (status, superseded_by)** → learner-model.md (event remapping on node splits) — deprecated nodes with learner events need successor pointers

## How to Update These Files

- **Strong idea clarified or strengthened** → Add to the relevant downstream file. If it rises to a core commitment, add to "Strong Working Commitments" above.
- **New tension** → Add to `tensions.md` with enough context for a future session to understand the stakes.
- **Tension resolved** → Move from `tensions.md` to the relevant downstream file. Note the resolution.
- **Dead ends** → Do not record. These files are forward-looking.
- **New commitment settled** → Add the reasoning to `design-reasoning.md` explaining *why*, not just *what*.
- **Idea surfaces but isn't ready for a file** → Capture in `ideation.md`. When consumed into a downstream file or rejected, update its status.
- **Deprecated files** → Move to `_archive/` with a version suffix. Update references.
- **Always note the date** when adding or revising entries.

---
*Last updated: 2026-04-09 (node schema session; architecture.md split into five files; file index updated; seed graph rebuild reclassified as implementation task)*
