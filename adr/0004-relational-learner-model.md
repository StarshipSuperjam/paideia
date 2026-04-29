# ADR 0004 — The learner model is relational

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

A learner model can be a flat checklist (mastered / not-mastered per concept) or it can model the **structure of what a learner knows** — connections between concepts, decay over time, forward-looking teaching opportunities, cross-domain bridges the learner has and hasn't crossed. Flat models are easier to query and easier to display; structural models are harder to query but enable adaptive teaching that responds to *what the learner knows in relation to what they're about to encounter*.

If teaching adapts only to a checklist, the system can decide whether to teach a concept but not how to teach it. If teaching adapts to the relational model, the system can pick callbacks that land (because the learner has the upstream concept), surface cross-domain analogies that resonate (because the learner has the analogous concept in another domain), and route around concepts the learner is currently weak on.

## Decision

The learner model is **relational** — it tracks mastery state per concept, the events that produced that state, the paths the learner has taken between concepts, and the cross-domain bridges the learner has crossed. The teaching system reads this structure to make per-turn decisions about callbacks, examples, and routing.

## Consequences

- The learner model schema is event-sourced (per ADR 0015) — events carry path context, source context, and interaction type so the relational structure is recoverable from the log.
- Mastery is a derived state, not a stored flag. A `mastery_snapshot` table caches recent computation, but the source of truth is the event log.
- Teaching prompts to Sonnet (per ADR 0014, ADR 0007) carry not just "what the learner is studying now" but "what concepts they have access to" — enabling the model to choose callbacks that the learner can actually receive.
- Querying the learner model is more expensive than a checklist would be. This cost is paid because adaptive teaching is the product.
- Cross-domain edges (per ADR 0007) become useful: a learner who studied a concept in one domain has a bridge available when an analogous concept appears in another. The relational model is what makes cross-domain bridges *teachable*, not just *visible*.
- Forward-looking teaching opportunities (the system knows a concept the learner is about to need is upstream of three current concepts) are computable because the structural relationships are present in the model.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 4.
- [`docs/learner-model.md`](../docs/learner-model.md) — schema, decay, computation.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — assessment rubric reads the relational model.
- ADR 0015 — Event-sourced learner model.
- ADR 0009 — Portable mastery (per-concept, regardless of path; the structural model still records the path).
- ADR 0010 — Continuous contextual assessment (assessment computes against the relational model).
