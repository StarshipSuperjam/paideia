# ADR 0015 — Event-sourced learner model

- **Status:** Accepted
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

The learner model can be implemented as a **mutable state table** (a `user_concepts` table with a `mastery_level` column updated in place) or as an **event-sourced log** (a `learner_events` append-only table; mastery is computed from the log). State tables are simpler to query and faster for the common case ("what does this learner know about X?"). Event-sourced models are more complex but make a class of analyses possible that state tables foreclose.

Five requirements emerged during design that each demand event history, not state:

1. **Temporal decay** — needs timestamps per event to compute decayed strength.
2. **False mastery detection** — needs comparison of current evidence against earlier evidence of the same concept (the learner appeared to know X two months ago; do they still?).
3. **Path efficiency tracking** — needs path context per event to compare which paths produced more durable mastery.
4. **Source effectiveness** — needs source context per event (which texts, which scaffolding kinds, produced better outcomes).
5. **Cross-domain bridge discovery** — needs freeform interaction logging to surface spontaneous connections the learner makes.

Each of these requires the event history. A mutable state table loses the time series and the contextual columns; recovering them after the fact requires schema migration plus the original data — and the original data isn't recoverable if it was overwritten.

## Decision

The learner model is **event-sourced**. The `learner_events` table is append-only, capturing every interaction with timestamps, path context, source context, interaction type, and rubric-dimension fingerprint. Mastery is **derived state** computed from the event log; a `mastery_snapshots` table caches recent computations for query performance, but the source of truth is the events.

## Consequences

- All five analyses above are possible without schema migration. Adding a new analytical dimension requires adding an event-emission column upstream and rerunning analytics; it doesn't require backfilling historical state.
- Mastery computation (per `docs/learner-model.md`) is a function over decayed events: per-event strength, asymptotic aggregation, conditional decay floor, threshold mapping at 0/0.3/0.7. The function reads events, not snapshots; snapshots cache for performance but never override.
- Snapshot invalidation is a known cost. When the mastery function changes (new rigor-modulated decay parameters, revised threshold mapping), snapshots must be invalidated; recomputation is bounded but non-trivial.
- Query cost is higher than a flat state table would be. Recursive queries against the event log feed the snapshot table; live queries hit snapshots first, fall through to events on miss. Postgres handles this without specialized infrastructure (per ADR 0017).
- The audit trail is automatic. Every mastery state has a recoverable history; there is no "who set this mastery?" question without an answer.
- Storage grows linearly with learner activity. At V1 scale (community-college audience, deferred institutional market), this is well within budget. At enterprise scale, partitioning strategies become necessary; the event-sourced architecture supports them naturally.
- The Phase 3 SQL schema implements this. Phase 6 (self-correction) consumes the event log for tension-pattern analysis (per ADR 0014).

## See also

- [`docs/learner-model.md`](../docs/learner-model.md) — Event-Sourced Architecture; mastery computation function.
- [`docs/architecture.md`](../docs/architecture.md) — `learner_events` and `mastery_snapshots` tables.
- ADR 0004 — Relational learner model (event-sourcing operationalizes the relational structure).
- ADR 0017 — Postgres + recursive CTEs over OWL/RDF (the substrate that makes event-sourcing tractable).
- ADR 0014 — Sonnet teaches, Opus reviews (consumes event log for batch tension analysis).
