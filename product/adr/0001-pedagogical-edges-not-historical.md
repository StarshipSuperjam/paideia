# ADR 0001 — Pedagogical edges, not historical

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

A graph that connects ideas can encode different relationships. Two candidate semantics are immediately available: **historical influence** ("Kant influenced Husserl") and **pedagogical prerequisite** ("you need Kant's epistemology before phenomenology"). The two are correlated but not identical — many historical influences are pedagogically irrelevant, and many pedagogical prerequisites cross historical lines (e.g., a learner today often needs basic logic from a much later tradition before tackling Aristotelian syllogism).

The graph is the spine of every downstream system: traversal generates syllabi, edges constrain teaching order, the learner model tracks mastery against nodes the graph names. Once the edge semantics is chosen, every traversal, every assessment, and every UX assumption is built around it. The choice is structurally load-bearing.

## Decision

Edges in the Paideia graph encode **pedagogical prerequisite relationships** — "must understand X before Y makes sense" — not historical influence. Historical relationships are out of scope; if a learner wants the history of an idea, that's a different product surface (or absent entirely from V1).

## Consequences

- Traversal is meaningful for syllabus generation: a topological sort over pedagogical edges yields a learnable order, not a chronological one.
- Edge authoring requires a different judgment than encyclopedia editing. The question is "would a learner struggle without this?" — not "did this thinker read that one?". This raises the bar on graph authoring (the test is empirical-pedagogical, not bibliographic) and reduces the bar on completeness (we don't owe a complete intellectual history).
- Influence-style metadata (which thinker proposed what, dates, schools) attaches to nodes as text content (`summary`, `teaching_notes`) but never as edges. The graph carries no `influenced_by` predicate.
- Cross-domain edges become natural and necessary (per ADR 0007). A historical-influence graph would partition by tradition; a pedagogical graph routes through whatever prerequisites are actually load-bearing, including across domain boundaries.
- The deprecated v0.2 prototype's edge claims were a mix of historical and pedagogical — part of why it was retired.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 1.
- [`ROADMAP.md`](../../ROADMAP.md) — strong working commitments referenced throughout.
- [`docs/architecture.md`](../docs/architecture.md) — Edge Schema (no historical-influence predicates).
- [`docs/pedagogy.md`](../docs/pedagogy.md) — assessment rubric assumes prerequisite-shaped edges.
- ADR 0008 — Concept nodes (the granularity that makes prerequisite edges meaningful).
