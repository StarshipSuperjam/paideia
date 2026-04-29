# ADR 0002 — Commercial sustainability without pedagogical compromise

- **Status:** Accepted
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

An education product needs revenue to exist. The risk: revenue mechanisms commonly degrade the pedagogy that makes the product worth using. Free-to-play games shape difficulty curves around monetization moments; ad-supported content shapes recommendations around dwell time; "engagement-optimized" loops route around the cognitive friction that genuine learning requires. Once revenue logic touches what gets taught or how, the teaching system is no longer optimizing for learning — it's optimizing for whatever the revenue function rewards.

This is a normative decision, not a tactical one. It binds future product, business, and engineering choices: which monetization patterns are acceptable, which UX patterns are acceptable, what telemetry is acceptable to collect.

## Decision

Revenue logic must never change what the product teaches or how it teaches. Monetization mechanics — subscription tiers, paywalls, premium features, advertising, recommendation logic — are confined to surfaces that do not influence the graph's structure, the teaching system's prompts, the learner model's computation, or the assessment rubric.

## Consequences

- Acceptable monetization patterns include: per-user subscription, institutional licensing, premium content surfaces (e.g., expanded reading-system features), paid expert review queues. Unacceptable: ad-supported teaching surfaces, dwell-time-optimized recommendation, paywalled prerequisites, "premium difficulty" tuning.
- The audience-vs-market distinction (per ADR 0012) operationalizes this: the audience (community college students, first-generation learners) shapes pedagogical defaults; the market (institutional buyers) shapes enterprise feature decisions. The audience never pays the cost of a market-driven mechanism.
- Telemetry decisions are constrained: metrics exist to improve teaching, not to drive monetization. Engagement-depth aggregation (per `docs/pedagogy.md`) is for assessment; it must not be repurposed as a "time-on-app" KPI.
- This commitment does not require Paideia to be free. It requires that paid and free experiences differ in scope (more content, more features, more support), not in pedagogical quality.
- Future revenue decisions get the audit: does this change what's taught, how it's taught, or how mastery is computed? If yes, it's blocked. The pedagogical commitments (this ADR, plus 0001, 0004, 0008–0012) are the test.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 2.
- [`docs/business.md`](../docs/business.md) — revenue model constraints, audience vs market.
- ADR 0012 — Freshman defaults, autodidact ceiling (audience vs market separation).
- ADR 0011 — No hosted copyrighted material (related independence: pedagogy decoupled from licensing dependencies).
