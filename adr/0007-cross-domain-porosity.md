# ADR 0007 — All domains are mutually porous

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Once the architecture is domain-agnostic (per ADR 0006), the question becomes: are domain partitions hard or soft? A hard partition treats each domain as a self-contained sub-graph (philosophy nodes connect only to other philosophy nodes; chemistry nodes connect only to other chemistry nodes), and cross-domain references live in node text content rather than edges. A soft partition treats domains as labels but lets edges cross domain boundaries freely.

Hard partitions are simpler to render (each domain is its own region of the globe) and simpler to reason about (a query about philosophy returns only philosophy). They also lie about what learning actually requires. Real prerequisite structure crosses domains constantly: philosophical concepts depend on history, psychology, economics, theology, logic, and the natural sciences. Forcing those dependencies to live in node text strips them of structural force — the topological sort can't see them, mastery computation can't propagate through them, and adaptive teaching can't route around them.

## Decision

All domains are **mutually porous**. Cross-domain prerequisite edges are first-class graph elements, indistinguishable in schema from same-domain edges. Service nodes from neighboring domains carry exactly enough depth to make the target concept comprehensible — they terminate when further depth stops affecting comprehension of the target.

## Consequences

- The edge schema does not carry a "cross-domain" boolean. Cross-domain edges are detected by comparing the domain tags of source and target nodes; this is a query-time concern, not a schema concern.
- The seed-graph build (Phase 5) explicitly includes a **cross-domain edges pass** (subdomain `P_9` per `ROADMAP.md`) after the subdomain interiors are stable. The pass produces edges spanning subdomain boundaries; service nodes from other domains are added as needed.
- The graph audit (Phase 4, per ADR 0016) flags suspicious cross-domain edge ratios as a soft-warn. A subdomain with > 40% cross-domain inbound edges likely indicates a missing service node — the structural signal is "you keep depending on the same outside concept; that concept should probably have its own node here."
- Service nodes get the same schema treatment as concept nodes — `confidence_level`, `provenance`, `teaching_notes`. They're not a second-class node type. The render-readiness guard prevents them from leaking the term "service node" into learner-facing prose.
- Globe rendering (per `docs/ui-architecture.md`) doesn't partition spatially by domain. Spatial grouping comes from community detection on the edge topology (per ADR 0018), so cross-domain bridges appear naturally as visually adjacent regions where dense bridges exist.
- The granularity principle (per ADR 0008) bears on this: a service node from outside the target domain should be at the right granularity to serve as a prerequisite — concept-level, not thinker-level or domain-level.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 7; cross-domain section is load-bearing.
- [`docs/architecture.md`](../docs/architecture.md) — Cross-Domain Porosity.
- [`ROADMAP.md`](../ROADMAP.md) — Phase 5 cross-domain pass; service nodes subphase.
- ADR 0006 — Domain-agnostic architecture.
- ADR 0008 — Concept nodes (granularity for service nodes).
- ADR 0016 — Graph construction needs live validation (cross-domain ratio check).
- ADR 0018 — Flat domain tags (domain as label, not partition).
