# ADR 0013 — Mastery verification as organic escalation

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Once a learner has accumulated mastery evidence on a concept, the question is how to verify the mastery is genuine and durable. Two approaches are available. **Cross-syllabus interruption**: pull the learner out of their current concept to test an upstream one — schedule the verification, surface a quiz or boss encounter on a cadence. **Organic escalation**: when downstream teaching naturally references the upstream concept (which good pedagogy already does), let those callback references accumulate as mastery probes.

Cross-syllabus interruption breaks conversational flow. Paideia's expression contract (per `docs/pedagogy.md`) is built around a coherent teaching-mode arc; injecting an unrelated verification quiz cuts the arc and frames learning as test-bearing. It also produces lower-quality signal: the verification context is artificial (no genuine application demand), and scaffolding proximity is high if the verification is recent.

Organic escalation exploits the fact that **good teaching already revisits upstream concepts**. When you teach Phenomenology, you have to reference Transcendental Idealism — without it, the new concept doesn't land. Those callbacks are both genuine pedagogy and mastery probes; they accumulate evidence over several downstream concepts at lower scaffolding proximity (the original teaching is days or weeks behind), in novel contexts (the concept is being applied, not restated). This produces higher-quality verification than a scheduled interrupt.

## Decision

Mastery verification happens **organically through downstream teaching**, not through cross-syllabus interruption. Callback references during teaching of downstream concepts double as verification probes. The assessment rubric (per ADR 0010) credits these references with the appropriate scaffolding-proximity discount and rigor scaling; sustained evidence across multiple downstream concepts produces verified mastery.

## Consequences

- The teaching system tracks which upstream concepts are due for verification (e.g., not-yet-verified mastery; mastery approaching decay floor) and weights its callback choices accordingly. The system surfaces a callback that's both pedagogically natural and probe-valuable.
- No scheduled verification surface in V1. "Boss encounter" or quiz UX is not a verification mechanism — if used at all, it's a learner-initiated review tool, not a system-driven interruption.
- The downstream-teaching session-lifecycle (per `docs/session-lifecycle.md`) names this explicitly: mastery verification through downstream teaching is an in-session pattern, not a cross-session pattern.
- Edge cases (a learner abandons a path before reaching a downstream concept that would have probed an upstream one) are handled by decay: unverified mastery decays per the rigor-modulated decay function (per `docs/learner-model.md`). Decayed mastery is not a verification failure; it's a state-of-evidence statement.
- This commitment combines with continuous contextual assessment (ADR 0010): together they say *all evidence is conversational, all verification is organic*. There is no separate "test mode."
- The Sonnet teaching layer (Phase 7) implements this: callback selection, upstream-concept reference, and rubric emission are part of the teaching prompt's contract.

## See also

- [`docs/pedagogy.md`](../docs/pedagogy.md) — Mastery Verification.
- [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) — Mastery Verification Through Downstream Teaching.
- [`docs/learner-model.md`](../docs/learner-model.md) — decay function (handles unverified mastery without panic).
- ADR 0010 — Continuous contextual assessment (the rubric organic verification computes against).
- ADR 0014 — Sonnet teaches, Opus reviews (the layer that emits callback-driven verification events).
