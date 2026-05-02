# ADR 0019 — Two-column rigor score override model

- **Status:** Accepted
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

The rigor score is a per-node property (continuous 0.0–1.0) computed from graph topology — roughly, how much weight the node carries given its prerequisite mass, prerequisite count, and downstream depth. It feeds mastery decay parameters (half-life and floor are functions of rigor) and assessment calibration (harder concepts demand higher-quality evidence).

The score is computed by a formula. But occasionally the formula is wrong — a node's topological position underweights a concept that's pedagogically dense, or overweights one that's structurally connected but conceptually trivial. Editorial correction is needed.

The naive approach is a **single column** that's either computed or manually overridden. This creates a cascading problem. The formula is recursive: a node's score depends on its prerequisites' scores. If you override one node, every downstream node's computed score shifts. If any of those downstream nodes were also overridden, you have a conflict — does the downstream override hold, or is it now stale because its input changed? You either propagate the conflict (re-compute downstream and reapply overrides, hoping they still make sense) or freeze the downstream overrides (and accept that they're now disconnected from current topology). Both are bad.

## Decision

Separate the computed value from the human adjustment into **two columns**:

- `rigor_score_computed` — always the formula output, never manually touched.
- `rigor_score_adjustment` — a human-applied delta (default `0.0`), independent of computation.

The effective score is `clamp(computed + adjustment, 0.0, 1.0)`. The formula always runs on **computed values only**; adjustments are invisible to propagation.

## Consequences

- **No cascading.** An editorial adjustment on one node changes only that node's effective score. No downstream node is affected because the formula never sees the adjustment. Adjustments are local and stable.
- The adjustment communicates intent more clearly than a raw override. An adjustment of `-0.2` says "moderately simpler than topology suggests"; a raw override of `0.3` doesn't tell you what the formula would have produced. The delta carries the editorial signal explicitly.
- Recomputation of the formula (after graph edits) is safe — adjustments survive untouched, and the new computed values combine with existing adjustments via the same `clamp` rule. No conflict resolution needed.
- Editorial adjustments should result from considered analysis and evidence, not casual opinion. The Opus batch review (per ADR 0014) can propose adjustments alongside edge edits; human review accepts or rejects per the existing review queue.
- Querying the rigor score is straightforward: a generated column or view returns the effective value. Most query consumers don't need to know about the two-column structure.
- The schema cost is one extra column on `nodes`. This is trivial.
- This pattern (separate computed-from-formula and human-delta) generalizes to other places where a formula needs editorial correction without breaking propagation. If similar needs arise (e.g., confidence overrides on edges), the same pattern applies.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Rigor Score Computation, Two-Column Override Model, Node Schema.
- ADR 0014 — Sonnet teaches, Opus reviews (Opus can propose adjustments).
- ADR 0010 — Continuous contextual assessment (the rubric reads the effective rigor score).
- [`docs/learner-model.md`](../docs/learner-model.md) — decay parameters as functions of rigor.
