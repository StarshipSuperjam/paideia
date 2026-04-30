# Mission

> What Paideia is, who it serves, and the commitments that make it different. Vision and audience framing extracted from CONTEXT.md (now retired) at S-0002. Project disposition revised at S-0012 per [ADR 0032](../adr/0032-personal-project-disposition.md).

## What this is

Paideia is a knowledge mastery app built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense, not just what influenced what.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus (primary + supplementary) for each step. A persistent learner model tracks mastery across sessions and texts.

It ships as a **personal project** the builder makes available to other people via a single iOS App Store cost-priced subscription, calibrated for first-encounter learners because the builder values the pedagogical discipline of that calibration (per [ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md)) — not because of market-fit. The option to grow into an institutional product, a non-profit, a grant-funded organization, or an acquisition target is foreclosed *as a refusal, not a deferral* per [ADR 0032](../adr/0032-personal-project-disposition.md), including in the success case. The freshman-defaults calibration survives because it protects against **builder-bias drift** — the failure mode where knowing how the system works obscures whether it's usable cold to a learner encountering it for the first time. The success criterion is "an app I would pay for if it weren't mine," verified at Phase 9 by a small TestFlight cohort cold-test (see [`business.md`](business.md) Personal Project Disposition).

## Cross-domain porosity (load-bearing)

Philosophy has the densest coverage first, but the graph is **inherently multi-domain from day one**. Philosophical concepts have prerequisite dependencies on history, psychology, economics, theology, logic, and the natural sciences. These cross-domain nodes are first-class graph elements, not future expansion. The architecture is domain-agnostic — the same graph structure, teaching system, and learner model serve any field where prerequisite relationships matter.

No domain can claim complete coverage without nodes from neighboring domains. Service nodes from other domains carry exactly enough depth to make the target concept comprehensible. Prerequisite chains terminate when further depth stops affecting comprehension of the target concept.

## Audience framing

### Freshman defaults, autodidact ceiling

The system calibrates **cold-start defaults for a learner encountering ideas for the first time**. The adaptive teaching system escalates rapidly based on engagement quality. Both audiences are served by the same product without either knowing the other exists.

The asymmetry of failure is directional: a freshman encountering content beyond their scope cannot proceed (and the failure feels like inadequacy, which is destructive). An autodidact encountering freshman-level calibration is mildly annoyed for a few exchanges before the adaptive system escalates. The cost of defaulting too low is brief annoyance; the cost of defaulting too high is a learner who quits.

The audience does not double as a market. The "audience vs. market" distinction in the prior version of this document presumed an institutional product path (community college departments as eventual buyers, grant funding, non-profit incorporation, acquisition exit) that [ADR 0032](../adr/0032-personal-project-disposition.md) forecloses. There is no market in this disposition's framing — only an audience the builder calibrates for because the calibration is pedagogically right and protects against builder-bias drift.

## Strong working commitments

These are the strongest current ideas — not closed questions, but the positions that would require substantial new thinking to displace. The full set lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). Each is recorded as an ADR; this list is the audience-facing summary, the ADR is the contract.

1. **Pedagogical edges, not historical.** The graph encodes "must understand X before Y" — never just "X influenced Y." ([ADR 0001](../adr/0001-pedagogical-edges-not-historical.md))
2. **Operating discipline must not corrupt pedagogy.** The threat is not revenue logic touching the product's teaching content (the prior framing); the threat is *builder*-funnel mechanics — retention metrics, conversion ceremonies, free-tier-as-acquisition-channel framing — pulling the builder's attention toward optimizing for retention and conversion over teaching quality. The commitment binds the operating shape: single iOS App Store cost-priced subscription, no free tier, no institutional regime, no funnel-mechanic surfaces. ([ADR 0032](../adr/0032-personal-project-disposition.md) supersedes the prior [ADR 0002](../adr/0002-commercial-sustainability-without-pedagogical-compromise.md) framing; supporting operating discipline: [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) — personal financial cost ceiling, reframed in S-0012 as fixed annual operating subsidy budget)
3. **Supplementary media is metadata, not structure.** Film, art, music attach to concept nodes as companions; never structural prerequisites. ([ADR 0003](../adr/0003-supplementary-media-as-metadata-not-structure.md))
4. **The learner model is relational.** Tracks connections between concepts and forward-looking teaching opportunities, not a flat checklist. ([ADR 0004](../adr/0004-relational-learner-model.md))
5. **Each text gets its own interpretive outline.** No templates. Generated from parametric knowledge of the scholarly tradition, optionally enhanced by user-supplied commentary. ([ADR 0005](../adr/0005-per-text-interpretive-outline.md))
6. **Domain-agnostic architecture.** Philosophy is the first domain, not the only one. ([ADR 0006](../adr/0006-domain-agnostic-architecture.md))
7. **All domains are mutually porous.** Cross-domain prerequisite edges are first-class graph elements. ([ADR 0007](../adr/0007-cross-domain-porosity.md))
8. **Nodes are concepts, not thinkers.** The atomic unit is an idea, never a person or school. ([ADR 0008](../adr/0008-concept-nodes-not-thinkers.md))
9. **Mastery is portable.** One mastery state per concept, regardless of path. ([ADR 0009](../adr/0009-portable-mastery.md))
10. **Assessment is continuous and contextual.** Three-dimensional rubric (reconstruction, application, boundary awareness), discounted by scaffolding distance (per [ADR 0023](../adr/0023-engagement-depth-aggregation.md), high distance → high evidentiary weight), scaled by rigor score. ([ADR 0010](../adr/0010-continuous-contextual-assessment.md))
11. **The app never hosts or distributes copyrighted material.** Mastery graph teaches parametrically; close reading uses bring-your-own-book. ([ADR 0011](../adr/0011-no-hosted-copyrighted-material.md))
12. **Freshman defaults, autodidact ceiling.** Cold-start defaults; adaptive escalation. ([ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md))

The reasoning behind each — including the architectural decisions that flowed from them — lives in [`adr/`](../adr/) (Nygard format, status-tracked). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

## What's settled, what's open

`STATE.md` — current phase and next session's work item.
`ROADMAP.md` — full phase arc with success criteria.
`docs/tensions.md` — active tradeoffs and unresolved questions.
`docs/CROSS_REFERENCES.md` — high-value file dependencies.

## See also

- `README.md` — repo orientation.
- `CLAUDE.md` — AI session conventions.
- `docs/architecture.md` — graph data model.
- `docs/pedagogy.md` — teaching design and assessment.
- `docs/learner-model.md` — mastery, decay, events.
