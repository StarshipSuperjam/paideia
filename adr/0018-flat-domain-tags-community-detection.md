# ADR 0018 — Flat domain tags + community detection

- **Status:** Accepted
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Once domain-agnostic architecture is settled (per ADR 0006) and cross-domain porosity is a structural commitment (per ADR 0007), the question is how to represent "domain" in the schema. Two candidates: **hierarchical taxonomy** (Philosophy → Epistemology, Ethics, Metaphysics → sub-areas) used to organize the globe spatially and to constrain queries; **flat labels** (a `domain TEXT[]` array on each node, used for color-coding and filtering).

A hierarchical taxonomy was the initial instinct. Two problems killed it.

**Categories don't map to spatial regions.** Ethics concepts don't cluster in one area of the globe — the categorical imperative is spatially near transcendental idealism (its prerequisite) not near eudaimonia (its fellow ethics concept). The globe's layout is determined by edge topology, not by labels. Imposing categorical regions would either conflict with the topology or redundantly mirror it.

**Categorical boundaries are non-linear and contested.** Is the categorical imperative ethics or epistemology? Is historical materialism political philosophy or economics? Forcing concepts into a single hierarchical bucket requires judgment calls that add no pedagogical value and create maintenance burden.

The flat-label alternative sidesteps both. Domain tags become metadata for color-coding and filtering; a node can carry multiple domain tags simultaneously (the categorical imperative is `["ethics", "epistemology"]`); spatial grouping comes from a different mechanism — community detection (Louvain/Leiden) running on edge topology, producing emergent clusters that reflect actual prerequisite relationships rather than imposed labels.

## Decision

**Domain tags are flat labels** stored as a `TEXT[]` array on each node. They provide color-coding, filtering, and dashboard surfaces. Spatial grouping at different zoom levels on the globe comes from **community detection algorithms** (Louvain or Leiden) running on edge topology; the resulting clusters are emergent from actual prerequisite structure, not imposed by a taxonomy.

## Consequences

- Schema is simple: `domain TEXT[] NOT NULL DEFAULT '{}'`. Multi-domain nodes are first-class; queries by domain use array containment operators.
- Globe rendering (per `docs/ui-architecture.md`) runs community detection at multiple zoom levels and renders the resulting communities as visual regions. The colors come from the domain tag (or from a blend if multiple tags are present); the spatial grouping comes from topology.
- **Domain-agnostic by construction.** Adding a new domain (chemistry, music theory) requires no schema change — author the new nodes with the appropriate tag. Globe rendering picks them up via community detection.
- No "primary domain" or "subfield" hierarchy. If the product surface needs to communicate a domain at a glance, it picks the first tag in the array (with stable ordering as a convention) or surfaces all tags equally.
- Cross-domain edges (per ADR 0007) compose naturally with this. The query "show me all cross-domain edges into ethics" is a join with array containment; no schema partition needed.
- Performance of community detection on the live graph at projected scale (low thousands of nodes per subdomain) is well within budget. Recomputation is needed only after non-trivial graph edits; cache the layouts per graph_version.
- The flat-tag approach makes future domain additions **cheap**. The cost of a hierarchical taxonomy would have been paid every time a domain was added (slot it into the hierarchy; reconcile with sibling categories; update queries that filter by parent domain).

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Node Schema, Cross-Domain Porosity.
- [`docs/ui-architecture.md`](../docs/ui-architecture.md) — Level-of-Detail Rendering.
- ADR 0006 — Domain-agnostic architecture.
- ADR 0007 — All domains are mutually porous.
- ADR 0008 — Concept nodes (granularity at which domain tags apply).
