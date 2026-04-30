# ADR 0018 — Flat domain tags + community detection

- **Status:** Accepted
- **Date:** 2026-04-09 (light-revised 2026-04-30 at S-0013 — globe-rendering use case retired per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md); algorithm and storage shape commitments unchanged)
- **Deciders:** pre-foundation deliberation; formalized in S-0003; light-revised at S-0013 per ADR 0033 mission realignment

## Context

Once domain-agnostic architecture is settled (per [ADR 0006](0006-domain-agnostic-architecture.md)) and cross-domain porosity is a structural commitment (per [ADR 0007](0007-cross-domain-porosity.md)), the question is how to represent "domain" in the schema. Two candidates: **hierarchical taxonomy** (Philosophy → Epistemology, Ethics, Metaphysics → sub-areas) used to constrain queries and to organize visual surfaces; **flat labels** (a `domain TEXT[]` array on each node, used for color-coding and filtering).

A hierarchical taxonomy was the initial instinct. Two problems killed it.

**Categories don't map to natural concept neighborhoods.** Ethics concepts don't cluster in one area of the conceptual space — the categorical imperative sits near transcendental idealism (its prerequisite) not near eudaimonia (its fellow ethics concept). Concept neighborhoods are determined by edge topology, not by labels. Imposing categorical regions would either conflict with the topology or redundantly mirror it.

**Categorical boundaries are non-linear and contested.** Is the categorical imperative ethics or epistemology? Is historical materialism political philosophy or economics? Forcing concepts into a single hierarchical bucket requires judgment calls that add no pedagogical value and create maintenance burden.

The flat-label alternative sidesteps both. Domain tags become metadata for color-coding and filtering; a node can carry multiple domain tags simultaneously (the categorical imperative is `["ethics", "epistemology"]`); concept neighborhoods come from a different mechanism — community detection (Louvain/Leiden) running on edge topology, producing emergent clusters that reflect actual prerequisite relationships rather than imposed labels.

## Decision

**Domain tags are flat labels** stored as a `TEXT[]` array on each node. They provide color-coding, filtering, and dashboard surfaces. Concept neighborhoods (clusters that reflect actual prerequisite structure) come from **community detection algorithms** (Louvain or Leiden) running on edge topology; the resulting clusters are emergent from prerequisite structure, not imposed by a taxonomy.

## Consequences

- Schema is simple: `domain TEXT[] NOT NULL DEFAULT '{}'`. Multi-domain nodes are first-class; queries by domain use array containment operators.
- Community detection runs as a **graph-analysis primitive** independent of any specific UI surface. Potential downstream consumers include the Discovery surface's concept-clustering for browseable catalog organization (per [ADR 0034](0034-discovery-planning-engagement-triad.md), lands at S-0014), Planning-side syllabus organization heuristics, and graph-quality audits during seed authoring (per [ADR 0016](0016-graph-construction-needs-live-validation.md) Phase 4 audit).
- **Domain-agnostic by construction.** Adding a new domain (chemistry, music theory) requires no schema change — author the new nodes with the appropriate tag. Community detection picks them up via emergent clustering on the edges they participate in.
- No "primary domain" or "subfield" hierarchy. If a product surface needs to communicate a domain at a glance, it picks the first tag in the array (with stable ordering as a convention) or surfaces all tags equally.
- Cross-domain edges (per [ADR 0007](0007-cross-domain-porosity.md)) compose naturally with this. The query "show me all cross-domain edges into ethics" is a join with array containment; no schema partition needed.
- Performance of community detection on the live graph at projected scale (low thousands of nodes per subdomain) is well within budget. Recomputation is needed only after non-trivial graph edits; cache the layouts per graph_version.
- The flat-tag approach makes future domain additions **cheap**. The cost of a hierarchical taxonomy would have been paid every time a domain was added (slot it into the hierarchy; reconcile with sibling categories; update queries that filter by parent domain).
- **Globe-rendering use case retired at S-0013 per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md).** The original ADR named globe-rendering as the primary consumer of community detection ("globe rendering runs community detection at multiple zoom levels and renders the resulting communities as visual regions"). That use case is gone with the globe; the algorithm survives because its other consumers (Discovery clustering, syllabus heuristics, audit) do not depend on a globe surface. The algorithm-and-storage-shape commitment is unchanged; only the named consumer shifts.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Node Schema, Cross-Domain Porosity.
- [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) — globe-rendering use case retired at S-0013; algorithm survives as graph-analysis primitive.
- [ADR 0034](0034-discovery-planning-engagement-triad.md) (lands at S-0014) — Discovery / Planning / Engagement triad; Discovery surface is a potential downstream consumer of community-detection clustering for browseable catalog organization.
- [ADR 0006](0006-domain-agnostic-architecture.md) — Domain-agnostic architecture.
- [ADR 0007](0007-cross-domain-porosity.md) — All domains are mutually porous.
- [ADR 0008](0008-concept-nodes-not-thinkers.md) — Concept nodes (granularity at which domain tags apply).
- [ADR 0016](0016-graph-construction-needs-live-validation.md) — Phase 4 graph-quality audit; potential downstream consumer of community-detection signal.
