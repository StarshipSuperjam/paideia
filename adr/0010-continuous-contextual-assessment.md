# ADR 0010 — Assessment is continuous and contextual

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Mastery requires evidence. Two structural choices about evidence: **discrete assessment** (separate moments where the system explicitly tests the learner — quizzes, problem sets, exit tickets) or **continuous assessment** (every learner utterance during teaching is evidence; the assessment rubric runs on the conversational stream). Discrete assessment is auditable and cheap to compute; it also produces poor signal because it tests what the rubric anticipated rather than what the learner can do, and because the testing context is artificial (no genuine application demand).

Continuous assessment exploits the fact that a teaching session is already producing the evidence. When a learner reconstructs a concept in their own words, applies it to a new case, or notices its boundary against a related concept, that's mastery evidence — produced naturally, in context, against a real teaching demand.

The cost is that continuous assessment must be **contextual**: the same utterance is stronger evidence when produced spontaneously than when produced one minute after the teacher just said it (high scaffolding proximity discounts the evidence). Without contextualization, all utterances would be over-credited.

## Decision

Assessment is **continuous and contextual**. Three-dimensional rubric (reconstruction, application, boundary awareness), discounted by **scaffolding proximity** (how recently was this scaffolded by the teaching turn?), scaled by **rigor score** (harder concepts demand higher-quality evidence to clear the same threshold).

## Consequences

- The teaching session emits assessment-bearing events continuously, not at discrete checkpoint moments. Each event carries the rubric dimensions it touched, the scaffolding-proximity score, and the source rigor score.
- The mastery computation function (per `docs/learner-model.md`) consumes these events with the proximity discount and rigor scaling baked in. Same utterance, different context → different mastery contribution.
- Mastery verification is **organic** (per ADR 0013) — when a downstream concept references an upstream one, the natural reference doubles as a mastery probe with low scaffolding proximity (the original teaching is days or weeks behind). Scheduled cross-syllabus interruptions are rejected.
- The rubric's three dimensions are intentionally narrow. **Reconstruction** (can the learner restate?), **application** (can the learner use it on a new case?), **boundary awareness** (can the learner say what it's not, where it doesn't apply?). Other dimensions (recall speed, vocabulary fluency) were considered and rejected as proxies that shape teaching toward the wrong target.
- The scaffolding-proximity discount is the single most important calibration. Too aggressive and the system never accumulates mastery; too lenient and freshly-scaffolded reconstruction reads as deep mastery. The defaults live in `docs/learner-model.md` and are revisitable as evidence accumulates (Phase 8 evaluation harness).
- Engagement-depth aggregation (composite signal feeding mastery; prompt-pack Session 9, the first Phase 1 work item) operationalizes the rubric. Closing Session 9 is gated on this commitment being settled.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 10.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — three-dimensional rubric, scaffolding proximity, mastery verification.
- [`docs/learner-model.md`](../docs/learner-model.md) — mastery computation, decay, events.
- ADR 0013 — Mastery verification as organic escalation (continuous assessment over discrete interrupts).
- ADR 0004 — Relational learner model (the structure assessment computes against).
- ADR 0019 — Two-column rigor score override model (the rigor signal that scales rubric thresholds).
