# ADR 0008 — Nodes are concepts, not thinkers

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

The graph needs an atomic unit. Three candidates: **thinker-level** (one node per philosopher: "Kant", "Husserl"), **work-level** (one node per text: "*Critique of Pure Reason*", "*Logical Investigations*"), or **concept-level** (one node per idea: "Transcendental Idealism", "Intentionality"). The choice determines what an edge claim *means*.

A thinker-level edge says "all of Kant is a prerequisite for all of Husserl" — which is essentially never true. Phenomenology depends on Kantian *transcendental* idealism but not on the *Categorical Imperative*; routing a learner through Kant's full corpus to reach Husserl is pedagogically wasteful. A work-level edge has the same problem at a smaller scale: "all of the *Critique of Pure Reason* is a prerequisite" is too coarse for most downstream concepts, which need only specific arguments from the work.

Concept-level granularity makes each edge a complete claim: this entire idea is required for that entire idea. The edge has no internal qualifier ("which aspect of Kant matters?") because there's nothing aspectual left to qualify — the node *is* the aspect. This also makes per-session assessment feasible: you can assess whether a learner grasps Transcendental Idealism in a conversation; you cannot assess whether they grasp "Kant."

The deprecated v0.2 prototype used thinker-level nodes (45 of them) and was retired because the edge claims were too coarse to be meaningful.

## Decision

The atomic node is a **concept** — an idea at the granularity where a clean prerequisite claim is possible. Never a person, school, work, or tradition. Thinkers and works appear in node text content (`summary`, `teaching_notes`) but not as node identities.

## Consequences

- The granularity principle is the load-bearing test: a node is correctly granular when both prerequisite claims and assessment claims are possible at its scope. If either is too coarse, split.
- The graph carries hundreds of concept nodes per subdomain (per ROADMAP Phase 5) rather than tens of thinker nodes. The cost is editorial — more nodes to author. The benefit is meaningful edges and assessable mastery.
- Mastery becomes portable (per ADR 0009) because concepts are stable across paths. A learner who understands Transcendental Idealism via Kant's text understands the same concept as a learner who reached it via a contemporary commentary; the mastery state belongs to the concept, not to the path.
- Node splits are a recovery mechanism for granularity errors. If a node is found to be too coarse (an edge through it doesn't carry a clean prerequisite claim), it splits into finer nodes; the original is deprecated (per ADR 0021) but retained because learner events reference it by ID.
- Service nodes from other domains (per ADR 0007) get concept-level treatment, not domain-level: a node like *Bayesian Updating* from statistics, not a node like *Statistics*.
- The graph audit (Phase 4, per ADR 0016) gains an attribute-shape inconsistency soft-warn: same-domain nodes with materially different attribute coverage suggest granularity drift across authoring sessions.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 8.
- [`docs/architecture.md`](../docs/architecture.md) — Node Granularity Principle, Node Schema.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — assessment rubric assumes concept-level nodes.
- ADR 0009 — Portable mastery (consequence of concept granularity).
- ADR 0021 — Node deprecation via status + superseded_by (handles split-driven deprecations).
- ADR 0016 — Graph construction needs live validation (granularity-drift soft-warn).
