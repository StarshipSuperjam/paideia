# ADR 0009 — Mastery is portable

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Once a learner has demonstrated mastery of a concept, two models are available. **Portable mastery** stores one mastery state per concept regardless of how the learner reached it; the next syllabus that requires that concept treats the learner as already competent. **Per-path mastery** stores mastery per concept per path; a learner could be "mastered" on Empiricism via the Kant path but unmastered on the Philosophy of Science path.

Per-path mastery is operationally tempting because it accommodates the case where a learner appears to grasp a concept in one context but stumbles when it surfaces in another. The interpretation is that the learner has a contextual hold on the concept, not a robust one. But this confuses two different problems. If understanding a concept doesn't transfer, either (a) the learner doesn't actually understand it (in which case the original mastery assessment was wrong, and the fix is in the assessment rubric) or (b) the node is too coarse and should be split into the genuinely distinct concepts the learner is differentiating (in which case the fix is in the granularity principle, per ADR 0008).

Per-path mastery treats the symptom by adding a path dimension to mastery scoring. This compounds without bound: a concept reachable through ten paths has ten mastery states, each updated independently, with no clear answer to "does this learner know X?".

## Decision

**One mastery state per concept, regardless of path.** The mastery computation function takes a concept and a learner; it does not take a path parameter. Path context is recorded on events (for retrospective analysis: "which paths produced more durable mastery") but is not a dimension of the mastery state itself.

## Consequences

- When portable mastery appears to fail (a learner mastered via path A struggles on path B), the diagnostic is one of two: the assessment rubric is wrong, or the node is too coarse. Both are graph-level fixes (rubric tuning or node split per ADR 0021), not learner-model fixes.
- The mastery snapshot table is keyed on `(learner_id, concept_id)`, not `(learner_id, concept_id, path_id)`. Schema is simpler; queries are direct.
- Cross-domain transfer becomes meaningful: a learner who masters Bayesian updating in a statistics path doesn't re-learn it when it appears in a philosophy of science path. The cross-domain edge (per ADR 0007) carries the prerequisite; the portable mastery state covers it.
- Path comparisons (which path produces better mastery, faster mastery, more durable mastery) remain available because event records carry path context. The mastery computation ignores path; the analytics on event history don't.
- This commitment combines with concept-granularity (ADR 0008): if mastery isn't transferring, that's a structural signal to revisit granularity, not a signal to add per-path dimensions.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 9.
- [`docs/architecture.md`](../docs/architecture.md) — Portable Mastery.
- [`docs/learner-model.md`](../docs/learner-model.md) — mastery computation function (no path parameter).
- ADR 0008 — Concept nodes, not thinkers (granularity that makes portability meaningful).
- ADR 0015 — Event-sourced learner model (path context on events).
- ADR 0021 — Node deprecation via status + superseded_by (mechanism for granularity-correction-driven splits).
