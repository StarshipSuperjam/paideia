# ADR 0024 — Engagement-depth sub-signals stored raw, composite derived

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0004 (prompt-pack Session 9 deliberation)

## Context

The `learner_events` table records each learner interaction. Each event carries an engagement_depth value that feeds the mastery computation. ADR 0023 settles engagement_depth as a floored weighted geometric mean of three sub-signals — `generative_ratio`, `scaffolding_distance`, `novelty`. The remaining choice: **store the composite engagement_depth scalar on each event, or store the three raw sub-signals and derive the composite at query time?**

Storing the composite is simpler — one column, one query lookup. But it is lossy: once an event is written, the sub-signals are gone.

Three reasons this matters:

1. **Aggregation tunability.** ADR 0023's V1 defaults (0.5/0.3/0.2 weights, 0.05 floor) are tunable. If composites are stored, retuning requires either re-deriving sub-signals from logged conversation transcripts (lossy and may not be possible if transcripts are pruned) or accepting that historical events use the old aggregation. Both options are bad.
2. **Sub-signal analytics.** False-mastery detection, source-effectiveness analysis, and the cross-domain bridge discovery feedback loop (per `docs/self-correction.md`) may need sub-signal questions: "are this learner's high-novelty events concentrated in a particular domain?", "do high-`generative_ratio` events from this scaffolding type produce more durable mastery?". These questions cannot be answered from a stored composite.
3. **ADR 0015 discipline.** The event-sourced learner model commits to storing **raw interaction data** with mastery state derived. Storing only the composite would violate the spirit of that commitment — the composite is derived state, not raw data.

## Decision

The `learner_events` table stores **three sub-signal columns** as raw data:

- `generative_ratio` — `NUMERIC(3,2)`, NULLable, `[0, 1]`
- `scaffolding_distance` — `NUMERIC(3,2)`, NULLable, `[0, 1]`
- `novelty` — `NUMERIC(3,2)`, NULLable, `[0, 1]`

The composite `engagement_depth` is **computed at query time** by the mastery computation function in the application layer, per ADR 0023's formula. There is no `engagement_depth` column on `learner_events`.

**NULL semantics.** For interaction types where the composite does not apply (`backward_inference`, `incidental_mention`), the three sub-signal columns are NULL and the application layer substitutes the fixed value (0.5 and 0.3 respectively, per ADR 0023). NULL in any sub-signal column is the schema-level signal that "composite does not apply for this event."

**Constrained-input semantics.** For interaction types where the composite applies but one sub-signal is constrained at event-emission time (e.g., `assessment` events have `scaffolding_distance = 1.0` locked by the zero-scaffolding constraint), the constrained value is **stored as the literal value** (1.0). The constraint is encoded by the AI's behavior at event-emission, not by the schema.

## Consequences

- **Aggregation tunability is preserved.** Changing weights, floor, or the formula itself is an application-layer change with zero data migration. Recompute mastery; do not migrate events.
- **Sub-signal analytics surface is open.** Future feedback loops can query sub-signals directly without backfilling.
- **Schema cost is small.** Three `NUMERIC(3,2)` columns vs. one. Storage growth at V1 scale is negligible. At enterprise scale, the partitioning strategies ADR 0015 anticipates absorb the additional columns trivially.
- **The application layer must handle NULL sub-signal cases.** The mastery computation function reads `event.interaction_type` first; if it is `backward_inference` or `incidental_mention`, use the fixed value; otherwise, compute from sub-signal columns. NULL sub-signals on a composite-applicable interaction type is a data error — a soft-warn category for `tools/validate.py`'s event-audit extension once Phase 4 builds it.
- **Snapshot invalidation interacts with this.** Per ADR 0015, `mastery_snapshots` cache the *result* of mastery computation, not the composite. When the aggregation function or weights change, snapshots must be invalidated and recomputed. The sub-signal columns themselves are immutable once written.
- **The Phase 3 SQL schema implements these columns.** Phase 4's validate extension adds the NULL-on-composite-applicable soft-warn.
- **This decision aligns with ADR 0015's commitment** to event-sourcing as more than a storage choice: it is a discipline of preserving raw interaction data so that derived analyses can be added without migration.

## See also

- ADR 0023 — Engagement-depth aggregation: weighted geometric mean (the formula computed at query time).
- ADR 0015 — Event-sourced learner model (the storage discipline this ADR operationalizes for engagement signals).
- [`docs/learner-model.md`](../docs/learner-model.md) — Mastery Computation pseudocode (consumes sub-signals and applies fixed values per interaction type).
- [`docs/architecture.md`](../docs/architecture.md) — `learner_events` table schema (Phase 3 implementation target).
