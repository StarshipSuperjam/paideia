# ADR 0012 — Freshman defaults, autodidact ceiling

- **Status:** Accepted
- **Date:** 2026-04-08 (lightly revised 2026-04-30 at S-0016)
- **Deciders:** pre-foundation deliberation; formalized in S-0003; lightly revised at S-0016 per [ADR 0032](0032-personal-project-disposition.md) and [ADR 0035](0035-multi-platform-apple-expansion.md) — residual market framing stripped; the freshman-defaults builder-bias-protection role named explicitly per [ADR 0032](0032-personal-project-disposition.md)'s Consequences (preserved unchanged through [ADR 0035](0035-multi-platform-apple-expansion.md)).

## Context

Cold-start defaults must commit to *some* assumed learner. Two natural anchors: **freshman defaults** (assume the learner is encountering ideas for the first time, no institutional scaffolding) or **autodidact defaults** (assume an experienced self-directed learner who can navigate complexity). Splitting into separate products doubles the build cost and forces the learner into the wrong audience picker before they've used the product.

The asymmetry of failure is **directional**. A freshman encountering content beyond their scope cannot proceed — the failure feels like inadequacy, which is destructive. An autodidact encountering freshman-level calibration is mildly annoyed for a few exchanges before the adaptive system escalates. The cost of defaulting too low is brief annoyance; the cost of defaulting too high is a learner who quits.

This asymmetry resolves the question. Default toward the audience whose failure mode is unrecoverable; the other audience's failure mode is recoverable through normal product use.

## Decision

The system calibrates **cold-start defaults for a learner encountering ideas for the first time**. The adaptive teaching system escalates rapidly based on engagement quality (per the assessment rubric in ADR 0010). Both audiences are served by the same product without either knowing the other exists. The diagnostic conversation and first few exchanges generate enough signal to recalibrate; neither audience requires explicit picking.

## Consequences

- **Audience** (shapes pedagogical defaults): community college students, particularly first-generation learners encountering academic material without institutional scaffolding. This drives V1 calibration: vocabulary defaults, scaffolding density, default rigor at first encounter.
- **No market commitment.** The institutional regime — LMS integration, instructor dashboards, cohort administration, FERPA compliance, grade export, community-college-departments-as-buyers framing — is foreclosed *as a refusal, not a deferral* per [ADR 0032](0032-personal-project-disposition.md) (commitment 4: no institutional regime, period) and preserved through [ADR 0035](0035-multi-platform-apple-expansion.md). The audience-vs-market separation that the original (2026-04-08) version of this ADR named as the operational form of the commitment is retired with it; the replacement framing is the operating-discipline-must-not-corrupt-pedagogy commitment in [`docs/MISSION.md`](../docs/MISSION.md) commitment 2 (rewritten at S-0012 per [ADR 0032](0032-personal-project-disposition.md)).
- Adaptive escalation depends on the assessment rubric (per [ADR 0010](0010-continuous-contextual-assessment.md)) producing fast, clean signal. If escalation is sluggish (many exchanges before the system updates its model of the learner), autodidacts stay annoyed too long. The engagement-depth aggregation work (per [ADR 0023](0023-engagement-depth-aggregation.md)) operationalizes this calibration.
- This commitment doesn't claim that freshmen are the only audience. It claims they are the **calibration anchor**. Autodidacts get served by escalation, not by separate calibration.
- **Freshman calibration is also load-bearing for builder-bias protection** per [ADR 0032](0032-personal-project-disposition.md)'s Consequences (preserved unchanged through [ADR 0035](0035-multi-platform-apple-expansion.md)). The builder is an autodidact; building "for the builder" defaults the system toward autodidact-shaped UX, vocabulary, and scaffolding density, which fails the freshman audience the system commits to. The freshman-defaults discipline is the operational guard against that drift. The Phase 9 small-cohort cold-test (per [ADR 0032](0032-personal-project-disposition.md) Phase 8/9 simplifications) is the verification artifact: 2–3 cold-testers given the TestFlight build with no instructions reveal builder-bias drift that the builder cannot detect from inside the system. The freshman calibration target is precisely what a builder-bias-blind reader needs.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 12; audience framing section. Audience vs. market subsection retired at S-0012 per [ADR 0032](0032-personal-project-disposition.md); the operating-discipline-must-not-corrupt-pedagogy commitment 2 absorbs the threat the audience-vs-market framing originally guarded.
- [`docs/pedagogy.md`](../docs/pedagogy.md) — V1 Calibration Defaults.
- [ADR 0032](0032-personal-project-disposition.md) — personal project disposition; supersedes ADR 0002. Names this ADR's freshman calibration as load-bearing for builder-bias protection in addition to pedagogical-discipline protection. Itself superseded by [ADR 0035](0035-multi-platform-apple-expansion.md) on commitment 1 (platform scope) only; commitments 2–6 (including the builder-bias-protection framing) restate verbatim.
- [ADR 0035](0035-multi-platform-apple-expansion.md) — multi-platform Apple expansion; supersedes [ADR 0032](0032-personal-project-disposition.md) by broadening commitment 1; preserves the builder-bias-protection framing this ADR depends on.
- [ADR 0002](0002-commercial-sustainability-without-pedagogical-compromise.md) — superseded by [ADR 0032](0032-personal-project-disposition.md). Historical reference; the audience-never-pays-market-costs framing is reframed as operating-discipline-must-not-corrupt-pedagogy under [ADR 0032](0032-personal-project-disposition.md).
- [ADR 0010](0010-continuous-contextual-assessment.md) — continuous contextual assessment (engine of escalation).
- [ADR 0023](0023-engagement-depth-aggregation.md) — engagement-depth aggregation; the rubric calibration that escalation depends on.
- [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — rendering policy worked example; also load-bearing for builder-bias detection per [ADR 0032](0032-personal-project-disposition.md)'s Consequences.
