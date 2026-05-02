# ADR 0020 — Teaching notes separate from summary

- **Status:** Accepted
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

The node schema needs text fields. The minimum is one — a `description`. Two fields (`summary` and `teaching_notes`) were considered as an alternative. The single-field option is simpler; the two-field option separates two consumers with materially different optimization targets.

**Summary** is consumed by the entity resolution service (per ADR 0017's note on entity resolution as an LLM task with summary fingerprints). It needs to be stable, search-optimized, and tightly focused on what the concept *is* — one to two sentences that fingerprint the concept's identity. If the summary drifts (extra detail, contextual asides, pedagogical asides), entity resolution becomes noisier.

**Teaching notes** are consumed by the teaching AI (per ADR 0014's Sonnet layer). They're pedagogical guidance: known confusion points, recommended entry modes, common misunderstandings, callbacks that work well. They're freer in form (longer, more contextual) and revisable as teaching evidence accumulates.

Putting both in one field forces tradeoffs. Optimize for entity resolution and you starve teaching guidance. Optimize for teaching and you compromise resolution accuracy. The two consumers want different things; one field cannot serve both well.

A more important consequence: **per-node remediation avenue**. When the teaching system consistently fails on a specific concept (learners misunderstand it, the AI approaches it wrong, the default teaching mode doesn't match the concept's shape), the fix can be a `teaching_notes` update — a *pedagogical* correction. That's distinct from reshaping the node's structural properties (a node split per ADR 0021) or adjusting system-level weights (a rigor adjustment per ADR 0019). Different kinds of correction should have different review cadences and different evidence thresholds; conflating them in one field obscures which kind of correction is being made.

## Decision

The node schema carries **two distinct text fields**: `summary` (one to two sentences; identity fingerprint; consumed by entity resolution) and `teaching_notes` (pedagogical guidance; freer form; consumed by the Sonnet teaching layer). Both are `TEXT NOT NULL DEFAULT ''`. Updating one does not require updating the other.

## Consequences

- Entity resolution fingerprints stay stable across teaching-driven edits. A node's pedagogical guidance can be revised without touching the field that resolution depends on.
- Pedagogical corrections become a low-friction loop. When tension records (per ADR 0014) indicate teaching failure on a node, the proposed fix may be a `teaching_notes` update — bounded edit, no propagation, fast review cadence.
- Structural corrections (node splits, edge changes) and parametric corrections (rigor adjustments) remain in their own lanes. The schema separates the kinds of correction the self-correction pipeline produces.
- The teaching-side prompt template (per the Phase 7 Sonnet integration) reads `teaching_notes` directly; the entity resolution service reads `summary`. Each consumer pulls only what it needs.
- Storage cost is one extra column. Trivial.
- If `teaching_notes` is empty (a freshly authored node with no pedagogical signal yet), the teaching system uses the `summary` plus structural context (prerequisites, neighborhood). Teaching is degraded but functional; quality improves as evidence accumulates.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Node Schema.
- ADR 0014 — Sonnet teaches, Opus reviews (Sonnet consumes teaching_notes).
- ADR 0017 — Postgres + recursive CTEs over OWL/RDF (entity resolution as LLM task on summary).
- ADR 0019 — Two-column rigor score override model (parametric correction lane).
- ADR 0021 — Node deprecation via status + superseded_by (structural correction lane).
