# ADR 0003 — Supplementary media as metadata, not structure

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

A philosophy concept like *Existentialism* has rich connections to film (Bergman, Tarkovsky), art (Bacon, Giacometti), and music. Treating those connections as graph edges is tempting — they're real, they're searchable, and they would surface naturally in product features. But what's the **type** of those edges? If they're prerequisite edges, the graph's traversal would route learners through films and albums as mandatory prerequisites of the concept. That's pedagogically wrong (you can master Existentialism without watching Bergman) and operationally bad (path generation becomes unpredictable, with media insertions appearing in topologically sorted syllabi).

The alternative is to admit a non-prerequisite edge type for "associated media" — but then the graph's edge schema fragments into multiple semantic categories, and every traversal needs to filter by edge type. The point of the graph (per ADR 0001) is that edges have one meaning: prerequisite.

## Decision

Supplementary media — film, art, music, documentary footage — is **metadata attached to concept nodes**, not graph structure. There is no media edge type; the edge schema carries only pedagogical prerequisite relationships and their kin (per the canonical `PREDICATE_MANIFEST.md` from Phase 4 onward).

## Consequences

- Media references live in a node's `summary` or `teaching_notes`, or in a separate per-node metadata field if richer rendering is needed. They never participate in topological sorts.
- Rare exceptions (Aesthetics requires encountering actual art) are handled by making the encounter itself a node — a concept like *Direct Aesthetic Encounter* that can have prerequisites and downstream nodes. The encounter is now a first-class graph element with proper pedagogical semantics, not a film-as-prerequisite.
- Path generation stays deterministic and predictable. A learner targeting Existentialism gets Phenomenology and Heidegger, not Bergman.
- The product can still surface media recommendations in a separate UI layer (e.g., a "companion media" panel beside the teaching surface). That layer reads the per-node metadata; it does not query the graph for media edges.
- This commitment locks in a strict edge schema. Adding a media edge type later would be a Status: Superseded change to this ADR plus a corresponding update to `PREDICATE_MANIFEST.md`.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 3.
- [`docs/expansion.md`](../docs/expansion.md) — Supplementary Media Layer.
- [`docs/architecture.md`](../docs/architecture.md) — Edge Schema (no media edges).
- ADR 0001 — Pedagogical edges, not historical (the same single-meaning principle).
- `supabase/migrations/PREDICATE_MANIFEST.md` (Phase 4) — canonical edge-type registry.
