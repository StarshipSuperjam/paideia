# ADR 0025 — Historical maximum tracking on `mastery_snapshots`

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0006 (prompt-pack Session 11 deliberation)

## Context

The Stage 3 decay floor in `docs/learner-model.md` is conditional: it activates only if the concept's historical maximum aggregate has crossed the proficiency threshold (0.3) at some point. This requires a tracking mechanism. Pre-S-0006, two options were named in the spec:

1. **Stored high-water mark.** A `max_historical_score` column on a (then-unnamed) cache table, updated whenever mastery is recomputed. Simple to query; trivial to include in the cached snapshot pushed to clients. The original framing called this a "philosophical compromise to event-sourcing" because it stores derived state.

2. **Recomputation from event history.** Per query, replay the events to determine whether the aggregate ever crossed 0.3. Correct by construction. The spec acknowledged the per-event-timestamp simulation cost ("heavier than it sounds").

Two facts not visible in the original framing collapse the choice:

**ADR 0015 already commits to a `mastery_snapshots` table** that "caches recent computations for query performance, but the source of truth is the events." `mastery_snapshots` is already mutable derived state. Adding `max_historical_score` to it is not a new architectural concession — it is one more cached column on an existing cache.

**Offline/sync forecloses pure recomputation.** Per `docs/learner-model.md` (Offline and Sync), the snapshot pushed to native clients enables session-start routing without a live server. Clients need to reason about whether the floor is active for each concept. That requires the snapshot to carry either `floor_active` or the `max_historical_score` scalar. Pure Option 2 ("compute everything, cache nothing") cannot satisfy this — and ADR 0015 already requires the snapshot anyway. The remaining choice is whether the cache contract is named.

The remaining substantive question is the **definition** of the historical maximum aggregate, on which the pseudocode in `docs/learner-model.md` Stage 3 was vague (`<running undecayed aggregate at event time>`). Two readings: decayed-at-the-moment max (the system's at-the-moment mastery output ever crossed 0.3) vs undecayed cumulative max (cumulative effort ever potentially crossed 0.3). The undecayed cumulative reading is the design choice — the floor protects concepts the learner once genuinely engaged with, even if the engagement was spread enough over time that the decayed at-the-moment aggregate never quite hit 0.3.

The undecayed cumulative reading raises a tail concern under the V1 constants (per ADR 0023): with `incidental_mention` at fixed engagement_depth 0.3 and type weight 0.2, raw_strength is 0.06 per event, and crossing the 0.357 raw-sum threshold requires only ~6 lifetime incidental mentions on a single concept — even though no individual event represented genuine engagement. Likewise, `backward_inference` is a synthetic event with no learner exchange. Neither interaction type is the "learner once genuinely engaged" evidence the floor is intended to protect. The cumulative sum is therefore taken over **substantive** interaction types only.

## Decision

The decay floor's proficiency precondition is tracked via `max_historical_score` on the existing `mastery_snapshots` table, with the following definition and discipline.

**Definition.** The historical maximum aggregate is the asymptotic cap on the cumulative undecayed raw strength of substantive events:

```
max_historical_score = 1 − exp(−cumulative_substantive_raw / ceiling)

where:
  cumulative_substantive_raw = Σ_e raw_strength(e)
                               for events e where
                               e.interaction_type ∈ substantive_types
  raw_strength(e) = type_weights[e.interaction_type] · compute_engagement_depth(e)
  ceiling = 1.0
```

**Substantive set.** `direct_teaching`, `callback_reference`, `cross_domain_connection`, `assessment`. **Excluded:** `incidental_mention` (concept appeared but learner did not engage) and `backward_inference` (synthetic event, no learner exchange). The substantive set is exactly the set of interaction types where the engagement-depth composite applies (per ADR 0023) — the symmetric move at the historical-max layer.

**Storage.** `mastery_snapshots.max_historical_score NUMERIC(3,2) NOT NULL DEFAULT 0`. No new `user_concept_cache` table — `mastery_snapshots` is already cached derived state per ADR 0015, and a separate cache would duplicate it.

**Update discipline.** On event ingest for a user-concept pair, snapshot regen recomputes `max_historical_score`. The closed-form incremental update is:

```
max_new = 1 − (1 − max_old) · exp(−raw_new)   for substantive events
max_new = max_old                               for non-substantive events
```

When V1 constants (type weights, engagement-depth weights/floor — per ADRs 0023/0024) are tuned, snapshots are invalidated and `max_historical_score` is recomputed from scratch — same invalidation surface as the rest of the snapshot.

**Monotonicity invariant.** `max_historical_score` is monotonically non-decreasing under event ingest. Late-arriving events from offline-sync clients can only raise it; they cannot lower it. (Substantive events have non-negative raw_strength; the asymptotic cap is monotone in the cumulative sum.)

**Offline/sync coupling.** The cached mastery snapshot pushed to native clients carries `max_historical_score`. The client derives `floor_active = max_historical_score ≥ 0.3` locally. No client-side recomputation; consistent with ADR 0015's no-client-side-mastery-computation principle.

## Consequences

- **Schema cost is one column.** Phase 3 SQL implements `max_historical_score` alongside the rest of `mastery_snapshots`. Storage growth is negligible (~3 bytes per (user, concept) pair).

- **Computation cost collapses.** The undecayed cumulative reading is a single sum + asymptotic cap, not the per-event-timestamp simulation the original Option 2 framing envisioned. The walk is O(n) over events for the affected user-concept pair, and the closed-form incremental update is O(1) at ingest. The historical-max tracking does not load Postgres recursive-CTE bandwidth (per ADR 0017).

- **The substantive-set guard is principled, not a hack.** ADR 0023 already treats `incidental_mention` and `backward_inference` as edge cases that bypass the engagement-depth composite (fixed depths). Excluding them from `cumulative_substantive_raw` is the symmetric move at the historical-max layer: events that bypass the composite for engagement-depth reasons also bypass cumulative-raw for floor-precondition reasons. The substantive set is exactly the composite-applicable set.

- **Threshold-crossing economics under V1 constants** (per ADR 0023): a single deep `direct_teaching` (depth 0.6) crosses the 0.357 raw-sum threshold; ~2 typical `callback_reference` events at depth 0.4 cross it; a single `assessment` (depth ~0.9) or `cross_domain_connection` (typically high) crosses it. These match the design intent already verified at S-0005 case 1 — "simple concepts stick once grasped." Incidental and inferred events do not contribute, closing the loophole where ambient passing-mention could permanently activate the floor without genuine engagement.

- **The "philosophical compromise" framing dissolves.** Storing `max_historical_score` on `mastery_snapshots` is one more cached value on a table that ADR 0015 already established as cached derived state. ADR 0015's discipline (raw events as source of truth, derived state cached for performance) is preserved exactly.

- **Snapshot invalidation rules from ADR 0015 absorb this naturally.** When the mastery computation function or V1 constants change, `max_historical_score` is recomputed alongside the rest of the snapshot. No new invalidation surface.

- **Phase 4 graph-validation extension gains a soft-warn category** on the `mastery_snapshots` audit: rows where `max_historical_score` does not match the recomputed value from the user-concept pair's substantive events. Catches drift if event-emission and snapshot-regen become disjoint.

- **Pseudocode in `docs/learner-model.md` Stage 3 is updated** to compute `cumulative_substantive_raw` alongside the decayed `sum`, then compute `max_historical = 1 − exp(−cumulative_substantive_raw / 1.0)`. Replaces the prior `<running undecayed aggregate at event time>` placeholder.

- **At enterprise scale (revisitable):** the partitioning strategies ADR 0015 anticipates absorb the additional column trivially. No revision to this ADR is anticipated unless `raw_strength`'s definition or the substantive set changes.

- **Closes prompt-pack Session 11** per `ROADMAP.md` §1.1. Phase 1.1 has now closed Sessions 9, 10, 11 across S-0004 / S-0005 / S-0006. Sessions 12–14 remain deferred per the same roadmap entry.

## See also

- ADR 0015 — Event-sourced learner model (the snapshot table this ADR extends).
- ADR 0017 — Postgres + recursive CTEs over OWL/RDF (the substrate; historical-max is application-layer, not a recursive query).
- ADR 0023 — Engagement-depth aggregation: weighted geometric mean (raw_strength inputs; the substantive-set guard mirrors ADR 0023's edge-case treatment of `incidental_mention` and `backward_inference`).
- ADR 0024 — Engagement-depth sub-signals stored raw, composite derived (the storage discipline this ADR honors).
- [`docs/learner-model.md`](../docs/learner-model.md) — Mastery Computation Stage 3, Offline and Sync (updated S-0006).
- [`docs/prep-paideia-prompt-pack.md`](../docs/prep-paideia-prompt-pack.md) — Session 11 deliberation prompt.
