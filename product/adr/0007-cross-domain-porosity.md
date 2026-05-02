# ADR 0007 — All domains are mutually porous

- **Status:** Accepted
- **Date:** 2026-04-07 (S-0016 sweep updated two residual globe-rendering passages)
- **Deciders:** pre-foundation deliberation; formalized in S-0003; S-0016 sweep updated two residual globe-rendering passages per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) and [ADR 0034](0034-discovery-planning-engagement-triad.md). The cross-domain-porosity commitment itself is unchanged; the rendering convention is now bridge-surfacing-in-context per [ADR 0034](0034-discovery-planning-engagement-triad.md).

## Context

Once the architecture is domain-agnostic (per ADR 0006), the question becomes: are domain partitions hard or soft? A hard partition treats each domain as a self-contained sub-graph (philosophy nodes connect only to other philosophy nodes; chemistry nodes connect only to other chemistry nodes), and cross-domain references live in node text content rather than edges. A soft partition treats domains as labels but lets edges cross domain boundaries freely.

Hard partitions are simpler to organize for browsing (each domain becomes its own catalog region) and simpler to reason about (a query about philosophy returns only philosophy). They also lie about what learning actually requires. Real prerequisite structure crosses domains constantly: philosophical concepts depend on history, psychology, economics, theology, logic, and the natural sciences. Forcing those dependencies to live in node text strips them of structural force — the topological sort can't see them, mastery computation can't propagate through them, and adaptive teaching can't route around them.

## Decision

All domains are **mutually porous**. Cross-domain prerequisite edges are first-class graph elements, indistinguishable in schema from same-domain edges. Service nodes from neighboring domains carry exactly enough depth to make the target concept comprehensible — they terminate when further depth stops affecting comprehension of the target.

## Consequences

- The edge schema does not carry a "cross-domain" boolean. Cross-domain edges are detected by comparing the domain tags of source and target nodes; this is a query-time concern, not a schema concern.
- The seed-graph build (Phase 5) explicitly includes a **cross-domain edges pass** (subdomain `P_9` per `ROADMAP.md`) after the subdomain interiors are stable. The pass produces edges spanning subdomain boundaries; service nodes from other domains are added as needed.
- The graph audit (Phase 4, per ADR 0016) flags suspicious cross-domain edge ratios as a soft-warn. A subdomain with > 40% cross-domain inbound edges likely indicates a missing service node — the structural signal is "you keep depending on the same outside concept; that concept should probably have its own node here."
- Service nodes get the same schema treatment as concept nodes — `confidence_level`, `provenance`, `teaching_notes`. They're not a second-class node type. The render-readiness guard prevents them from leaking the term "service node" into learner-facing prose.
- The Discovery-surface catalog (per [ADR 0034](0034-discovery-planning-engagement-triad.md), specified in [`docs/ui-architecture.md`](../docs/ui-architecture.md)) does not partition organization by domain. Catalog organization heuristics consume community detection on the edge topology (per [ADR 0018](0018-flat-domain-tags-community-detection.md)), so concepts cluster by structural prerequisite relationships rather than by domain tag, and cross-domain bridges appear naturally as catalog regions where concepts from different domains co-cluster. The cross-domain rendering convention more broadly is **bridge surfacing in context** per [ADR 0034](0034-discovery-planning-engagement-triad.md): bridges surface during planning (cross-syllabus convergence noting) and during engagement (callback references that bridge between domains), not as a standalone visualization surface.
- The granularity principle (per ADR 0008) bears on this: a service node from outside the target domain should be at the right granularity to serve as a prerequisite — concept-level, not thinker-level or domain-level.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 7; cross-domain section is load-bearing.
- [`docs/architecture.md`](../docs/architecture.md) — Cross-Domain Porosity.
- [`ROADMAP.md`](../../ROADMAP.md) — Phase 5 cross-domain pass; service nodes subphase.
- ADR 0006 — Domain-agnostic architecture.
- ADR 0008 — Concept nodes (granularity for service nodes).
- ADR 0016 — Graph construction needs live validation (cross-domain ratio check).
- ADR 0018 — Flat domain tags (domain as label, not partition).
