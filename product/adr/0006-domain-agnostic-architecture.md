# ADR 0006 — Domain-agnostic architecture

- **Status:** Accepted
- **Date:** 2026-04-07 (S-0016 sweep updated one residual example)
- **Deciders:** pre-foundation deliberation; formalized in S-0003; S-0016 sweep replaced a stale globe-rendering example per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) and [ADR 0034](0034-discovery-planning-engagement-triad.md).

## Context

Paideia ships with philosophy as the first domain. The temptation is to build philosophy-specific data structures (a node table with subfield enums for "epistemology / ethics / metaphysics", schemas tuned to the shape of philosophical argument, teaching prompts that hard-code references to philosophical traditions) and generalize later when a second domain arrives. This is a familiar architectural mistake: domain-specific structures accumulate quietly, and by the time domain-two arrives, retrofitting touches every table, every query, and every prompt.

The alternative is to build domain-agnostic from day one, treating "domain" as a tag on nodes rather than a structural partition. The marginal cost on day one is small (a `domain TEXT[]` column on nodes; teaching prompts parameterized rather than hardcoded). The cost of *not* doing this is paid in retrofit debt at every domain expansion.

## Decision

The graph schema, edge semantics, learner event model, teaching system, and assessment rubric have **no philosophy-specific logic**. Philosophy is the first domain, not the only one. Domain is a flat-label tag on nodes (per ADR 0018), never a structural partition.

## Consequences

- The same schema, the same teaching system, and the same learner model serve any field where prerequisite relationships matter. Adding a domain (chemistry, music theory, linguistics) means: tag new nodes with the domain label, author the prerequisite edges, ship.
- Cross-domain prerequisite edges are a natural consequence (per ADR 0007) — the same architecture that supports multi-domain naturally supports prerequisites that cross domain boundaries.
- Teaching prompts cannot hardcode philosophical references. The system prompt must derive its examples from the node being taught, not from a fixed library of philosophical canon.
- Philosophy is the **hardest test case**, not the easiest: it has the densest prerequisite structure, the richest cross-domain connections (history, psychology, economics, theology, logic, the natural sciences), and the best-understood corpus. If the architecture works for philosophy, it works for narrower domains.
- Domain-specific *features* (domain-specific reading profiles per [ADR 0005](0005-per-text-interpretive-outline.md); domain-tagged filtering and color-coding in the Discovery-surface catalog per [`docs/ui-architecture.md`](../docs/ui-architecture.md) and [ADR 0034](0034-discovery-planning-engagement-triad.md)) are allowed and expected — they read the domain tag, they don't structurally depend on philosophy being the domain.
- This commitment binds future schema decisions: any column or table that would force a domain-specific assumption needs explicit ADR-level justification.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 6.
- [`docs/architecture.md`](../docs/architecture.md) — Cross-Domain Porosity.
- ADR 0007 — All domains are mutually porous (cross-domain edges are first-class).
- ADR 0018 — Flat domain tags + community detection (the operational shape of "domain" in the schema).
