# ADR 0021 — Node deprecation via status + superseded_by

- **Status:** Accepted
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Nodes occasionally need to be split (granularity correction per ADR 0008), merged, or retired. The naive approach — delete the old node, insert the new ones — breaks two contracts simultaneously. (1) The event-sourced learner model (per ADR 0015) has an append-only invariant; rewriting historical events to point at new node IDs would violate it. (2) Even if events were rewritten, the audit trail would be lost — "the learner mastered concept X at time T" becomes meaningless if X no longer exists and we have no record of what it was.

A self-correction pipeline (per ADR 0014's Opus reviewer) needs to be able to **propose node operations**, not just edge operations. Opus might recommend splitting a coarse node into two finer ones because the rubric evidence shows learners differentiating in their answers. Those new nodes should enter the graph as `ai_proposed` with low confidence, accumulating evidence through the same confidence-weighted pipeline that governs edge additions.

The node schema needs fields that mirror the edge schema's `provenance` and `confidence`, plus a way to mark nodes as deprecated without deleting them, plus a way to record what they were replaced with.

## Decision

The node schema carries:

- `provenance` (TEXT) — `seed`, `ai_proposed`, `human_verified`, etc., mirroring the edge schema.
- `confidence` (NUMERIC, 0.0–1.0) — confidence score, mirroring the edge schema.
- `status` (TEXT) — `active`, `deprecated`, `superseded`. `deprecated` and `superseded` nodes stop participating in traversal and teaching but remain in the table.
- `superseded_by` (UUID[] or TEXT[]) — pointers to the replacement nodes when a node is split or merged.

When a node is split, the original is marked `superseded` with `superseded_by` pointing to the replacement nodes. Learner events continue to reference the original by ID; the audit trail is intact. Mastery computation walks the `superseded_by` pointers to apply event evidence to the appropriate replacement.

## Consequences

- **No data loss on splits or merges.** Original nodes remain queryable; events remain valid; the audit trail traces structural history.
- **Self-correction pipeline can operate on nodes.** Opus's batch review (per ADR 0014) can propose node operations through the same confidence-weighted gating that governs edge operations.
- Mastery remapping is a defined operation. When events reference a `superseded` node, the mastery function applies them against the replacement(s) as the `superseded_by` array specifies (with potential weight splitting if the original split into multiple finer concepts).
- Traversal queries filter on `status = 'active'` by default. Edge queries filter through active nodes only; deprecated nodes carry no traversal weight.
- The `validate_graph()` utility (per ADR 0016) flags any active edge pointing at a deprecated node as a soft-warn (cleanup needed) and as a hard-fail if the edge's source is itself active (broken structure).
- This pattern composes with the rigor score's two-column override (per ADR 0019) and the summary/teaching-notes separation (per ADR 0020). All three are forms of "the schema accommodates correction without breaking what's already there."
- The Phase 3 SQL schema implements these columns; Phase 6 (self-correction pipeline) is the first consumer of node deprecation operations.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Node Schema (provenance, confidence, status, superseded_by).
- [`docs/learner-model.md`](../docs/learner-model.md) — event remapping on node splits.
- ADR 0008 — Concept nodes (granularity errors are corrected via splits).
- ADR 0014 — Sonnet teaches, Opus reviews (Opus proposes node operations).
- ADR 0015 — Event-sourced learner model (events remain valid through node deprecation).
- ADR 0016 — Graph construction needs live validation (audits for stale references).
