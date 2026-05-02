# ADR 0002 — Commercial sustainability without pedagogical compromise

- **Status:** Superseded by [ADR 0032](0032-personal-project-disposition.md)
- **Date:** 2026-04-07
- **Deciders:** pre-foundation deliberation; formalized in S-0003; superseded in S-0012

> **Superseded 2026-04-30 (S-0012).** [ADR 0032](0032-personal-project-disposition.md) forecloses the commercial option set this ADR's discipline was guarding against. The "leave the option open" pattern that motivated the original framing (subscription tiers, institutional licensing, Khan Academy acquisition path, non-profit incorporation) was identified as the corruption vector itself: every "expand later" decision pulled the design toward business outcomes pedagogy never warranted. ADR 0032's fix is removing the optionality, not strengthening this ADR's guard. The threat reframes from *revenue-logic-touching-pedagogy* to *builder-funnel-mechanic-touching-pedagogy*; MISSION.md commitment 2 is rewritten in the same session to name the new framing. The historical reasoning below is preserved per the ADR README's supersession discipline (one-directional pointer; old file not deleted).

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
