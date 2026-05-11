# ADR 0014 — Sonnet teaches, Opus reviews

- **Status:** Accepted
- **Date:** 2026-04-08 (S-0016 audit confirmed no residual cohort/institutional framing requires revision; See also extended to record the privacy and disposition framework Opus now operates within)
- **Deciders:** pre-foundation deliberation; formalized in S-0003; S-0016 light-revision audit per [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md) and [ADR 0032](0032-personal-project-disposition.md)

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
- Opus operates on aggregated patterns across many individual learners, not on individual learner data and not on cohort-administrative groupings (the latter is foreclosed by [ADR 0032](0032-personal-project-disposition.md)'s no-institutional-regime commitment, preserved through [ADR 0035](0035-multi-platform-apple-expansion.md); the individual-only data regime per [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md) is the framework Opus operates within). This preserves the privacy posture per [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md) (structural-not-substantive storage) and matches the analytical task: structural correction wants statistical signal across many individuals, not individual cases.
- The Phase 6 self-correction pipeline implements this. The Phase 7 Sonnet teaching layer implements the emission side.
- Sonnet/Opus are the V1 choice; the architecture allows substitution (the "teaching" and "reviewing" roles are abstract; specific model choices change as model capabilities evolve).
- **Pedagogical-degradation discipline absorbed.** Under [ADR 0065](0065-oss-pivot-and-byok-disposition.md) the cost-ceiling mechanism per [ADR 0029](0029-personal-financial-cost-ceiling.md) retires (mechanism is structurally absent under BYOK — no Paideia-controlled API account; no per-user cap; no aggregate cap), but the pedagogical-integrity principle the cost ceiling protected — *degrade rather than terminate mid-concept-engagement* — survives as a teaching discipline that lives inside this ADR's role split. When an engagement runs long enough that the per-turn context grows unwieldy, the teaching layer downshifts (deeper retrieval window → shallower; two-hop neighborhood → one-hop) as a pedagogical move that respects engagement integrity per the atomic-unit-of-teaching commitment in [`docs/session-lifecycle.md`](../docs/session-lifecycle.md), not as a cost-protection move. The Sonnet/Opus role split is the framework this discipline lives inside: teaching-layer downshifts are scoped to Sonnet's per-turn context preparation; Opus's batch-review aggregation is unaffected. OQ-WALL-BEHAVIOR closes with this absorption per [ADR 0065](0065-oss-pivot-and-byok-disposition.md); the four candidate degradation steps the OQ enumerated (model downshift, retrieval shrink, concept-engagement length cap, soft refusal with explanation) lose their cost-cap framing entirely — the surviving discipline is "engagement integrity preserved under context-amplification pressure," not "approach to a spending cap."

## See also

- [`docs/self-correction.md`](../docs/self-correction.md) — Self-Correction Pipeline, Tension Log Schema.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — teaching modes and turn structure.
- [`ROADMAP.md`](../../ROADMAP.md) — Phase 6 (self-correction pipeline), Phase 7 (Sonnet teaching layer).
- [ADR 0013](0013-mastery-verification-organic-escalation.md) — Mastery verification as organic escalation (Sonnet emits the verification events).
- [ADR 0016](../../engine/adr/0016-graph-construction-needs-live-validation.md) — Graph construction needs live validation (separate from but complementary to Opus review).
- [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md) — persistent learner storage structural-not-substantive; the privacy posture Sonnet's tension emission writes to and Opus reads from.
- [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — rendering policy; Sonnet emits learner-facing prose against this contract.
- [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md) — erasure mechanism and individual-only regime; the data-regime framework Opus's aggregated analysis operates within.
- [ADR 0032](0032-personal-project-disposition.md) — personal project disposition; commitment 4 forecloses the institutional regime, which constrains "aggregated patterns" to mean across-many-individuals statistical aggregation, not cohort-administrative aggregation. (Superseded by ADR 0035, then by ADR 0065; institutional-regime foreclosure preserved through the chain.)
- [ADR 0035](0035-multi-platform-apple-expansion.md) — multi-platform Apple expansion; preserved the no-institutional-regime commitment unchanged. (Superseded by ADR 0065.)
- [ADR 0065](0065-oss-pivot-and-byok-disposition.md) — OSS pivot and BYOK disposition; supersedes ADRs 0029 and 0035; preserves the institutional-regime foreclosure; retires the cost-ceiling mechanism whose pedagogical-degradation principle is absorbed into this ADR's role split per the Consequences extension above.
