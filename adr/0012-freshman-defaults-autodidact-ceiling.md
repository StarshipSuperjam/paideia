# ADR 0012 — Freshman defaults, autodidact ceiling

- **Status:** Accepted
- **Date:** 2026-04-08
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Cold-start defaults must commit to *some* assumed learner. Two natural anchors: **freshman defaults** (assume the learner is encountering ideas for the first time, no institutional scaffolding) or **autodidact defaults** (assume an experienced self-directed learner who can navigate complexity). Splitting into separate products doubles the build cost and forces the learner into the wrong audience picker before they've used the product.

The asymmetry of failure is **directional**. A freshman encountering content beyond their scope cannot proceed — the failure feels like inadequacy, which is destructive. An autodidact encountering freshman-level calibration is mildly annoyed for a few exchanges before the adaptive system escalates. The cost of defaulting too low is brief annoyance; the cost of defaulting too high is a learner who quits.

This asymmetry resolves the question. Default toward the audience whose failure mode is unrecoverable; the other audience's failure mode is recoverable through normal product use.

## Decision

The system calibrates **cold-start defaults for a learner encountering ideas for the first time**. The adaptive teaching system escalates rapidly based on engagement quality (per the assessment rubric in ADR 0010). Both audiences are served by the same product without either knowing the other exists. The diagnostic conversation and first few exchanges generate enough signal to recalibrate; neither audience requires explicit picking.

## Consequences

- **Audience** (shapes pedagogical defaults): community college students, particularly first-generation learners encountering academic philosophy without institutional scaffolding. This drives V1 calibration: vocabulary defaults, scaffolding density, default rigor at first encounter.
- **Market** (shapes eventual enterprise features): community college departments and similar institutional buyers. Schema provisions exist (nullable `cohort_id` on events, shareable constrained paths) so the institutional path remains open without building the enterprise wrapper now.
- The audience-vs-market separation is the operational form of this commitment. The audience never pays the cost of a market-driven decision (per ADR 0002); the market never demands a product-shape that breaks the audience's experience.
- Adaptive escalation depends on the assessment rubric (per ADR 0010) producing fast, clean signal. If escalation is sluggish (many exchanges before the system updates its model of the learner), autodidacts stay annoyed too long. The engagement-depth aggregation work (prompt-pack Session 9, first Phase 1 item) operationalizes this calibration.
- LMS integration, instructor dashboards, FERPA compliance, and grade export are bolt-on features deferred until the teaching system proves itself. The teaching system is V1; the institutional wrapper is later.
- This commitment doesn't claim that freshmen are the only audience. It claims they are the **calibration anchor**. Autodidacts get served by escalation, not by separate calibration.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 12; audience framing section.
- [`docs/business.md`](../docs/business.md) — Audience vs. Market.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — V1 Calibration Defaults.
- ADR 0002 — Commercial sustainability without pedagogical compromise (audience never pays market costs).
- ADR 0010 — Continuous contextual assessment (engine of escalation).
