# ADR 0014 — Sonnet teaches, Opus reviews

- **Status:** Accepted
- **Date:** 2026-04-08
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Two AI roles are needed: a **teaching layer** that produces learner-facing turns (per turn, low latency, contextually rich) and a **review layer** that diagnoses graph errors (across many sessions, high judgment, low frequency). Putting both on the same model — and the same call — would require carrying the full graph in context during every teaching session and would produce dangerous single-signal corrections (one learner struggling once is treated as evidence of a bad edge).

The right shape separates the roles. The teaching model has a narrow context (current concept + prerequisites + small neighborhood for entity resolution) and emits **structured tension records** when teaching doesn't resolve through normal moves. The review model reads accumulated tensions in batch, looks for patterns across sessions and learners, and proposes graph edits through a confidence-weighted pipeline.

A week of tension data showing three learners all struggling at the same transition is a structural signal. One struggle is noise. The batch cadence makes pattern-detection possible and prevents reactive overcorrection.

Cost shape also favors the split: teaching is per-turn (the high-volume path; latency-sensitive); review is per-cycle (low-volume; throughput-sensitive). Different model tiers fit each.

## Decision

**Sonnet teaches** — produces learner-facing turns against the rendering policy (`AGENT_INSTRUCTIONS.md`, lands in Phase 1), reads narrow per-session context, emits tension records when normal teaching moves don't resolve a difficulty. **Opus reviews** — runs as a scheduled batch job, reads the accumulated tension log, proposes graph edits (node splits, edge weight adjustments, prerequisite additions) through the confidence-weighted pipeline, writes provisional ADR-status decisions for human review.

## Consequences

- Sonnet's context budget stays bounded and cheap per turn. The full graph is never in-context during teaching; the per-session slice (current concept + one-hop prerequisites + two-hop entity-resolution neighborhood) is what's loaded.
- Tension log schema (per `docs/self-correction.md`) defines the structured emission contract: five tension types (`struggle_unresolved`, `unexpected_ease`, `spontaneous_connection`, `source_ineffective`, `mastery_contradiction`) mapping to five feedback loops.
- The graph is **stable between review cycles**. Learners never encounter mid-session structural changes to the graph they're traversing. Opus's proposed edits land in a review queue; accepted edits ship at the next graph-version cut.
- Single-event reactivity is structurally prevented. Sonnet cannot edit the graph; Opus cannot run except in batch. Bad signals require multiple instances across sessions before they become candidate corrections.
- Opus operates on aggregated patterns, not on individual learner data. This preserves the privacy posture and matches the analytical task: structural correction wants population-level signal, not individual cases.
- The Phase 6 self-correction pipeline implements this. The Phase 7 Sonnet teaching layer implements the emission side.
- Sonnet/Opus are the V1 choice; the architecture allows substitution (the "teaching" and "reviewing" roles are abstract; specific model choices change as model capabilities evolve).

## See also

- [`docs/self-correction.md`](../docs/self-correction.md) — Self-Correction Pipeline, Tension Log Schema.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — teaching modes and turn structure.
- [`ROADMAP.md`](../ROADMAP.md) — Phase 6 (self-correction pipeline), Phase 7 (Sonnet teaching layer).
- ADR 0013 — Mastery verification as organic escalation (Sonnet emits the verification events).
- ADR 0016 — Graph construction needs live validation (separate from but complementary to Opus review).
