# ADR 0034 — Discovery / Planning / Engagement triad as primary product structure

- **Status:** Accepted
- **Date:** 2026-04-30
- **Deciders:** S-0014 (lands the replacement product structure paired with [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md)'s closure of the prior globe / reward visual system)

## Context

[ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) (S-0013) retired the globe-as-home-screen UI metaphor and the mastery-glow / cross-domain-tendrils / trophy reward visual system as deliberate architectural removal. It records the rationale (form-vs-content tonal mismatch; presentation surfaces drifting attention from the value claim) and names the survivors (graph + instructor + BYOB + bounded engagement contexts + mastery model + privacy + cost ceiling). What it does not name is the replacement product structure. ADR 0033 alone leaves a hole — the project has a sharpened mission claim and a list of preserved mechanisms, but no coherent answer to *what surfaces the user touches when they open the app.* This ADR closes that hole.

The structured-guidance gap [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) names — *filling the gap a self-learner has when there is no teacher to open doors and show the way* — decomposes into three concrete problems:

1. **Figuring out what to learn at all.** A self-learner without a teacher does not have someone opening doors. They may arrive with a clear target ("I want to understand phenomenology") or with curiosity that has not yet resolved into a target ("I keep hearing about Wittgenstein and I want to know why he matters"). A surface that only serves the first kind of learner abandons the second; a surface that only serves the second kind frustrates the first.
2. **Knowing what they need to understand first.** Even with a target identified, the prerequisite topology is not visible to a learner who does not already know the field. The graph's job is to make that topology answerable.
3. **Knowing whether they have actually learned the thing rather than become familiar with its facts.** The mastery-gating instructor's job is to verify understanding rather than recognition; this happens inside concept-level work and is not a separate surface in the user's mental model — it is *what teaching does* when teaching is gated.

Each of these problems has a structurally distinct answer, which produces a structurally distinct surface:

- The answer to "what to learn" is **discovery** — a surface where targets get identified, whether brought by the user or surfaced by the system.
- The answer to "in what order" is **planning** — a surface where the prerequisite topology becomes a sequenced syllabus and the user commits to study it.
- The answer to "did you actually learn it" is **engagement** — the surfaces where the AI instructor teaches, probes, and gates, already settled by [ADR 0028](0028-input-side-scope-structural-not-prompt.md) as three bounded contexts (concept engagement, diagnostic, close reading).

The mapping is one-to-one — three problems, three surfaces, and the surfaces are not interchangeable. A discovery affordance cannot answer "in what order"; a planning surface cannot answer "what to learn at all" without first having a target; an engagement surface cannot answer either of the upstream questions because concept engagement presumes a committed concept. The triad is therefore not a decorative grouping; it is the structural decomposition of the value claim into the surfaces that deliver it.

The discovery-side dual-path question — *AI conversational onboarding, or a browseable concept catalog?* — has both candidates active in the design conversation that produced [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) and the Phase 1.5 plan. The case for AI conversational onboarding: a learner without a target needs a guided way to surface one, and the AI instructor that already does the teaching is the natural agent for "tell me what interests you and I'll propose targets and a plan." The case for the browseable catalog: a learner who already has a target benefits from being able to see the system's coverage map directly, without negotiating it through conversation; users with strong intent are penalized by being made to converse to find what they already know they want. Choosing between them forces a disposition the design does not actually have — the project serves both kinds of learners (per the freshman-defaults / autodidact-ceiling commitment in [ADR 0012](0012-freshman-defaults-autodidact-ceiling.md)), and forcing them through one path is a category error. Dual-path is structurally correct: both affordances feed into the same plan-generation pipeline downstream, so the cost of supporting both is the discovery-surface UI work, not duplicated teaching infrastructure.

A library/bookshelf-of-mastered-concepts surface as a third *primary* view is a candidate worth naming explicitly so it can be foreclosed coherently. The argument for it: mastered concepts represent durable accomplishment and the user might want to return to them as orientation ("what have I actually learned?"). The argument against: a standalone trophy/library surface re-introduces exactly the corruption vector [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) named — a reward / visualization surface acquiring gravitational pull on attention — under a new name. Mastered concepts surface contextually within the syllabus view (the concept appears as part of a completed plan, the user can see it there) and within engagement (callbacks per [ADR 0013](0013-mastery-verification-organic-escalation.md) reference upstream concepts during downstream teaching). A separate trophy surface adds nothing the syllabus view cannot already deliver, and the cost is pulling attention back toward accumulation-as-spectacle. Foreclosed.

A second forcing function: cross-domain edges remain first-class graph data per [ADR 0007](0007-cross-domain-porosity.md), and the prior contract rendered them as visual tendrils on the globe. With the globe gone, cross-domain rendering needs a replacement. The replacement is structural: cross-domain bridges surface contextually during planning ("studying this concept advances your path toward [other target] as well") and during engagement (callback references that bridge between domains; in-engagement surfacing of cross-domain prerequisites that have just become reachable). This is not a UI primitive — it is a behavior of the AI instructor and the planning surface that uses cross-domain edge data as input. The convention is "bridge surfacing in context," and it is consistent with [ADR 0028](0028-input-side-scope-structural-not-prompt.md)'s structural-not-spectacular discipline.

## Decision

**The Discovery / Planning / Engagement triad is committed as Paideia's primary product structure.** Three surfaces, one each for the three structurally distinct problems the structured-guidance value claim answers. The triad replaces the prior globe-as-home-screen + concept-engagement-surface architecture in full.

### The three surfaces

**Discovery surface.** The entry point for identifying what to learn. Two parallel affordances feed into the same plan-generation pipeline:

- **AI conversational onboarding.** The user describes interests, fragments of curiosity, areas they keep encountering — and the AI proposes specific targets and a plan to reach them. This is the path for users without a clear target. The conversational surface is bounded by the same purpose-not-topic discipline as the diagnostic context per [ADR 0028](0028-input-side-scope-structural-not-prompt.md); it is not a general chat surface and does not become one.
- **Browseable concept catalog.** A directly-navigable view of the system's coverage, organized by domain and topic. The user with a clear target ("I want phenomenology") finds it without conversation. Catalog organization heuristics may consume the flat-domain-tags + community-detection algorithm preserved by [ADR 0018](0018-flat-domain-tags-community-detection.md) (concept clustering by edge topology) as a graph-analysis primitive — the algorithm's UI consumer shifts from globe-rendering to catalog-organization.

Both paths terminate at the same handoff: the user has identified a target concept (or a small set of related concepts), and the system generates a syllabus. The discovery surface owns target identification; it does not own plan execution.

**Planning surface.** The committed working mode for a chosen target. Each plan is a syllabus — an ordered sequence of concept nodes that traces prerequisite chains from the user's current mastery state to the target. The planning surface affordances:

- **Syllabus-as-plan.** A syllabus is a first-class object the user can see in full: prerequisite ordering, current position, mastered concepts visible in their syllabus context (no separate trophy surface), upcoming concepts gated until prerequisites resolve. The user navigates the syllabus to advance.
- **Prerequisite gating.** Concepts with unmet prerequisites are visible in the syllabus but not yet available for engagement; the gate is structural, not editorial. The user sees what is coming and what is required to reach it.
- **Quiet completion markers.** Completed concepts are marked completed within the syllabus. There is no celebration affordance, no glow visual, no badge. Completion is information, not spectacle. (The existing organic-verification framing per [ADR 0013](0013-mastery-verification-organic-escalation.md) — proficiency is quiet, mastery is a moment in the conversation, not a UI event — survives unchanged. The planning surface reflects state; it does not generate reward feedback.)
- **Current/active syllabus view.** The hard cap of five concurrent active syllabi survives from the prior contract. The user sees their active set on the planning surface; the most recent or decay-urgent syllabus may be foregrounded; switching between active syllabi is a one-action move within the planning surface.
- **Mastered concepts visible in context.** A mastered concept appears in the syllabus(s) that included it, marked as mastered. There is no standalone "library" or "bookshelf" surface that aggregates mastered concepts independently of their syllabus context.

**Engagement surface.** Where actual concept-level work happens. The Engagement surface is *not a new commitment* — it inherits the three bounded engagement contexts already settled by [ADR 0028](0028-input-side-scope-structural-not-prompt.md):

1. **Concept engagement** (Mode 2/3 teaching per [`docs/pedagogy.md`](../docs/pedagogy.md))
2. **Diagnostic conversation** (cold-start probe; calibration)
3. **Bring-your-own-book close reading** (per [ADR 0011](0011-no-hosted-copyrighted-material.md))

The user reaches the Engagement surface from the Planning surface (selecting the next concept in an active syllabus) or, for close reading, from a text the user has uploaded. The exit affordance per [ADR 0028](0028-input-side-scope-structural-not-prompt.md) returns the user to the Planning surface (or, for diagnostic, to the Discovery surface). The bidirectional teaching-surface contract — input-side structural per [ADR 0028](0028-input-side-scope-structural-not-prompt.md), output-side prompt-layer per [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — applies unchanged.

### Discovery dual-path as commitment

Both affordances on the Discovery surface — AI conversational onboarding and browseable concept catalog — are committed as first-class. Neither is a fallback for the other. A learner with a clear target should not need to converse to find what they already know they want; a learner without a clear target should not need to navigate a catalog they do not yet know how to read. The two paths are structurally appropriate to the two kinds of learners the project serves (per [ADR 0012](0012-freshman-defaults-autodidact-ceiling.md)'s freshman-defaults / autodidact-ceiling spectrum).

### Cross-domain edges: bridge surfacing in context

Cross-domain prerequisite edges remain first-class graph data per [ADR 0007](0007-cross-domain-porosity.md). Their UI rendering is **bridge surfacing in context**, not standalone visualization:

- **In planning:** when two active syllabi share a concept or are approaching an intersection via cross-domain edges, the planning surface notes it ("This concept also appears on your path toward [other target]; studying it advances both"). This is the existing cross-syllabus convergence framing from [`docs/session-lifecycle.md`](../docs/session-lifecycle.md), preserved.
- **In engagement:** the AI instructor surfaces cross-domain bridges contextually during teaching — callback references that bridge between domains; in-engagement surfacing of cross-domain prerequisites that have just become reachable. This is the natural extension of the organic-verification pattern per [ADR 0013](0013-mastery-verification-organic-escalation.md): callbacks are pedagogically genuine *and* probe-valuable; they are also bridge-revealing where the upstream concept lives in a neighboring domain.

There is no separate cross-domain-bridge visualization surface. The data is first-class; the rendering is contextual.

### Explicit foreclosures

The triad is the primary product structure. The following are explicitly foreclosed without a superseding ADR:

- **No globe.** No globe-as-home-screen, no spatial-traversal navigation, no "knowledge as a world" metaphor. (Already foreclosed by [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md); restated here so the triad's foreclosures are coherent in one place.)
- **No game-world rendering.** No spatial map surface, no character-on-map framing, no exploration-as-traversal mechanic.
- **No separate trophy surface.** Mastered concepts surface contextually within syllabi (per the Planning surface above); they do not aggregate into a standalone view.
- **No library/bookshelf as a third primary surface.** A separate accumulation surface for mastered concepts (or, by extension, for completed syllabi as historical artifacts) is foreclosed for the same reason as the trophy: it pulls toward accumulation-as-spectacle, which is the corruption vector [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) names.
- **No mastery-glow / tendril / colored-trail visualization.** Already foreclosed by [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md); restated as triad-level foreclosure.

### Open variability — flagged for downstream amendment

Two questions are committed to the triad shape but held *open for amendment* without superseding this ADR:

- **Library/bookshelf surface, on cold-test.** If Phase 9 implementation surfaces a concrete cold-test concern that mastered-concepts-in-syllabus-context is under-served (a learner can't find concepts they know they've completed because they don't remember which syllabus carried them), a quiet aggregated mastered-concepts view consistent with the no-trophy-spectacle discipline can be added without superseding this ADR. The discipline that survives: information surface, not reward surface; consistent visual register with the planning surface; no glow / badges / animation. This amendment path exists because the no-library decision is not as foundational as the no-globe decision.
- **Discovery dual-path, on cold-test.** If Phase 9 cold-test surfaces concrete evidence that one of the two discovery paths is materially under-used or counterproductive, the affordance set may be narrowed. The decision committed: dual-path is structurally correct; the affordance presence is held open to evidence.

A third question — **Mac-via-Designed-for-iPad polish depth** — is downstream of [ADR 0035](0035-multi-platform-apple-expansion.md) (lands at S-0015), not this ADR. Flagged here because the triad's surface design will inform what "modest keyboard/menu polish" means in practice.

These three are explicitly *future-amendment-friendly*. The remaining decisions in this ADR are committed.

## Consequences

- **`docs/ui-architecture.md` and `docs/session-lifecycle.md` are substantially rewritten in this session.** [`docs/ui-architecture.md`](../docs/ui-architecture.md) drops the Globe Navigation Model and Level-of-Detail Rendering sections wholesale (per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) obsolescence) and authors new Discovery Surface / Planning Surface / Engagement Surface sections. [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) drops the Globe as Home Screen section and the trophy/glow/tendrils framing in Mastery Verification; preserves the Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, and Mastery Verification Through Downstream Teaching's organic-escalation framing per [ADR 0013](0013-mastery-verification-organic-escalation.md). Concurrent Syllabus Limit (hard cap of five) survives.

- **The Concurrent Syllabus Limit (hard cap of five) survives as a planning-surface constraint.** The pedagogical rationale (more than five concurrent paths means insufficient momentum) survives unchanged from the prior contract. The visual-density-of-the-globe-itself signaling rationale drops with the globe; the planning surface signals the cap directly when the user attempts to start a sixth.

- **Cross-syllabus convergence noting (the "this concept also appears on your path toward [other target]" routing prompt) survives, attached to the Planning surface.** The mechanism was attached to the Routing After Concept Completion moment in the prior contract; it remains attached to that moment. The change is only that the user returns to the Planning surface (not the globe) when a concept engagement completes, and the convergence note appears there.

- **Phase 9 success criteria are substantially rewritten at S-0015 in [ROADMAP.md](../ROADMAP.md), as part of [ADR 0035](0035-multi-platform-apple-expansion.md).** The current Phase 9 success criteria reference globe-as-home-screen + concept-engagement-surface; they will be rewritten against the triad. The exit affordance (per [ADR 0028](0028-input-side-scope-structural-not-prompt.md)), delete-account affordance (per [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md)), data-export affordance (per [ADR 0032](0032-personal-project-disposition.md)), no-general-chat-surface (per [ADR 0028](0028-input-side-scope-structural-not-prompt.md)), and cost-cap-on-production-surface (per [ADR 0029](0029-personal-financial-cost-ceiling.md)) commitments are unchanged by the triad — they are commitments about *bounded-context behavior* and *surface-level constraints*, both of which survive the triad replacement.

- **[ADR 0027](0027-rendering-policy-prompt-layer-contract.md)'s forbidden-token enumeration is extended at S-0016** to add globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language as forbidden in agent output. The voice-discipline closure is bidirectional with this ADR's surface-level closure: the AI instructor's voice does not reach for game-master / world-explorer / trophy-grant framing because the forbidden-token list rules it out, and the surface around the instructor does not invite it because the triad does not include those surfaces. (S-0016 work, recorded here so the cascade is visible.)

- **Discovery's catalog organization may consume [ADR 0018](0018-flat-domain-tags-community-detection.md)'s flat-domain-tags + community-detection algorithm** as the concept-clustering primitive for catalog browseability. The algorithm survives [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md)'s globe drop because its consumer shifts; this ADR names the new consumer (Discovery surface) without committing to a specific catalog UI. The algorithm-and-storage-shape commitment in [ADR 0018](0018-flat-domain-tags-community-detection.md) is unchanged.

- **The Discovery surface inherits [ADR 0028](0028-input-side-scope-structural-not-prompt.md)'s purpose-not-topic discipline** for the AI conversational onboarding affordance. The diagnostic conversation per [ADR 0028](0028-input-side-scope-structural-not-prompt.md) and the conversational onboarding affordance here are structurally similar (both bounded conversational contexts that surface targets / probes; both forbid drift to general chat). Whether they share UI implementation, prompt structure, or routing is a Phase 9 decision; the structural commitment is that conversational onboarding is bounded and is not a general chat surface.

- **The Engagement surface is structurally inherited from [ADR 0028](0028-input-side-scope-structural-not-prompt.md), not freshly committed here.** This ADR does not modify the three bounded engagement contexts, the purpose-not-topic discrimination, the exit affordance, or the prompt-level off-topic-refusal foreclosure. The triad's contribution to engagement is *what surface routes the user there* (Planning, primarily) and *what surface the user returns to* (Planning, on exit; Discovery, on exit from a diagnostic). Concept-engagement internals are preserved.

- **The triad is the primary product structure.** Future feature design that proposes a primary surface outside Discovery / Planning / Engagement (e.g., a stand-alone library, a globe alternative, a community / sharing surface, a settings-as-primary-surface) must supersede this ADR with explicit reasoning. Settings, account management, billing, data-export, delete-account, and similar housekeeping surfaces are *secondary* — accessed from a menu within or alongside the primary surfaces — and do not require superseding this ADR. The line is whether the surface answers one of the three structured-guidance problems (primary) or supports operational continuity (secondary).

- **Bridge-surfacing-in-context is the durable convention for cross-domain rendering across the project.** Future design choices about cross-domain UI inherit it: cross-domain edge data is consulted contextually during planning and engagement; standalone cross-domain visualizations require superseding this ADR. The convention is structural-not-spectacular and consistent with [ADR 0028](0028-input-side-scope-structural-not-prompt.md)'s broader "structural over spectacular" discipline.

- **The MemPalace decision drawer for this ADR carries the conversational reasoning verbatim** per the two-layer decision-recording discipline in CLAUDE.md. The drawer is filed in the same session.

- **This ADR does not rise to [`docs/MISSION.md`](../docs/MISSION.md)'s strong-working-commitments list.** The triad is product-structural, not pedagogical commitment — same precedent as ADRs 0026 / 0029 / 0031 / 0032 / 0033. The pedagogical commitments (graph-grounded learning, mastery-not-familiarity, BYOB close reading) are unchanged; this ADR specifies *which surfaces deliver those commitments*, not *what the commitments are*.

- **Phase 1.5 advances by one session.** Phase 1.5.1 (mission realignment + globe/reward closure) closed at S-0013 with [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md). This ADR closes Phase 1.5.2. S-0015 lands [ADR 0035](0035-multi-platform-apple-expansion.md) (multi-platform Apple expansion + Phase 9 rewrite); S-0016 lands the rendering-policy revision and secondary-docs sweep. Phase 2 (Build Plan Scaffolding) opens at S-0017 with the realigned contract as input.

## See also

- [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) — paired closure ADR; this ADR's rationale. The two are structurally inseparable: 0033 records what was retired and why; 0034 records what replaces it.
- [ADR 0028](0028-input-side-scope-structural-not-prompt.md) — three bounded engagement contexts, inherited unchanged as the Engagement surface; the purpose-not-topic discipline applies to the Discovery surface's AI conversational onboarding affordance.
- [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — output-side prompt-layer contract; extended at S-0016 with forbidden-token additions for globe / reward / territory metaphors. Bidirectional with this ADR.
- [ADR 0007](0007-cross-domain-porosity.md) — cross-domain edges as first-class graph data; rendering convention shifts to bridge-surfacing-in-context.
- [ADR 0013](0013-mastery-verification-organic-escalation.md) — organic verification through downstream teaching; preserved unchanged. The Planning surface's quiet completion markers and the Engagement surface's callback-driven verification both inherit from this ADR.
- [ADR 0010](0010-continuous-contextual-assessment.md), [ADR 0023](0023-engagement-depth-aggregation.md), [ADR 0024](0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](0025-historical-maximum-tracking.md) — the mastery model that gates progression on the Planning surface and verifies through the Engagement surface; all preserved.
- [ADR 0011](0011-no-hosted-copyrighted-material.md), [ADR 0005](0005-per-text-interpretive-outline.md) — bring-your-own-book close reading; one of the three Engagement contexts. Preserved.
- [ADR 0009](0009-portable-mastery.md) — one mastery state per concept; the Planning surface displays this directly (mastered-in-this-syllabus = mastered-everywhere).
- [ADR 0012](0012-freshman-defaults-autodidact-ceiling.md) — the audience commitment that justifies the Discovery dual-path (freshman without a target needs onboarding; autodidact with a target benefits from catalog navigation).
- [ADR 0018](0018-flat-domain-tags-community-detection.md) — flat-domain-tags + community-detection algorithm; consumer shifts from globe-rendering (retired) to Discovery-surface catalog organization heuristics.
- [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — the AI instructor that runs the Engagement surface; the natural agent for the Discovery surface's AI conversational onboarding.
- [ADR 0035](0035-multi-platform-apple-expansion.md) (lands at S-0015) — multi-platform Apple expansion; Phase 9 success criteria rewritten against the triad as part of that ADR.
- [`docs/ui-architecture.md`](../docs/ui-architecture.md) — substantially rewritten in this session against the triad.
- [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) — substantially rewritten in this session against the triad.
- [`docs/architecture.md`](../docs/architecture.md) — graph data model; cross-domain edges remain first-class; the data-side commitments survive.
- [ROADMAP.md](../ROADMAP.md) — Phase 1.5.2 (this session); Phase 9 success criteria rewritten at S-0015 per [ADR 0035](0035-multi-platform-apple-expansion.md).
- The Phase 1.5 plan reference: `/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md` (local developer config; not a tracked project artifact).
