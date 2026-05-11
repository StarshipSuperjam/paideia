# ADR 0033 — Mission realignment: structured guidance for self-learners

- **Status:** Accepted
- **Date:** 2026-04-30
- **Deciders:** S-0013 (formal recording of a mission drift identified across several exploration conversations leading into S-0013; the realignment was settled in the S-0013 plan-mode conversation)

## Context

The contract layer at Phase 1 close (S-0012) presumed a globe-as-home-screen UI metaphor with a mastery-glow / cross-domain-tendrils reward visual system as the primary feedback for learner progress. That UI metaphor was authored before the project's mission framing was sharpened, and the exploration arc that produced this ADR surfaced a mission drift: the globe and reward system were UI-layer optimizations that drifted attention away from the core value claim, which is **filling the gap a self-learner has when there is no teacher to open doors and show the way.**

The novel value Paideia offers, restated:

1. The **structured pedagogical knowledge graph** that grounds learning in subject (concept-prerequisite chains) rather than schools (historical influence lineages) — preserved by [ADR 0001](0001-pedagogical-edges-not-historical.md), [ADR 0007](0007-cross-domain-porosity.md), [ADR 0008](0008-concept-nodes-not-thinkers.md).
2. The **AI instructor that supports and gates progression** to ensure mastery (not familiarity) along the way — preserved by [ADR 0010](0010-continuous-contextual-assessment.md), [ADR 0013](0013-mastery-verification-organic-escalation.md), [ADR 0014](0014-sonnet-teaches-opus-reviews.md), [ADR 0023](0023-engagement-depth-aggregation.md), [ADR 0024](0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](0025-historical-maximum-tracking.md).

The globe metaphor was not corrupted on its own. The corruption appeared at the interaction of the globe with the reward visualization. "Navigating a little 8-bit character around a map" — the way a cold-test learner reads any spatial-traversal UI — signals *this is play, low stakes, casual exploration.* The content (phenomenology, advanced epistemology, cross-domain bridges) signals *this is contemplation, sustained attention, real difficulty.* The form taxes the content. Cold-test users absorb form before content; a casual-register form makes the contemplation-register content fight uphill on every concept engagement.

This compounds with [ADR 0032](0032-personal-project-disposition.md) commitment 6, which forecloses social, sharing, leaderboards, streaks, push notifications, and other dynamic-feature surfaces. The globe + reward-visualization framing pulls toward exactly the gamification mechanics ADR 0032 forecloses, even when those mechanics are absent in code. Users' game-shaped expectations don't read source — they read the surface.

A self-learner without a teacher faces three concrete problems the structured-guidance gap names: (a) figuring out what to learn at all (no one is opening doors); (b) knowing what they need to understand first (no one is sequencing prerequisites); (c) knowing whether they have actually learned the thing rather than become familiar with its facts (no one is gating mastery). Paideia's structured graph + mastery-gating instructor addresses all three. The globe was a presentation choice that did not advance the value claim and did distract from it.

The drift was not "we picked a bad UI." It was "we picked a UI before the value claim was sharp, and then the UI started shaping what work felt aligned with the project." The pattern is structurally analogous to the corruption vector ADR 0032 named ("leave the option open to expand later" pulling design toward business outcomes pedagogy never warranted): a presentation surface acquires gravitational pull on the design once it is committed, and that pull is not visible until the value claim is sharpened against it.

## Decision

**The globe-as-home-screen UI metaphor and the mastery-glow / cross-domain-tendrils / trophy reward visual system are retired from Paideia's design as a deliberate architectural removal, not a deferral.** The replacement product structure is a Discovery / Planning / Engagement triad authored at S-0014 in ADR 0034. The mission framing of Paideia is realigned to name *filling the gap where a self-learner has no teacher* as the core value claim, with the structured pedagogical knowledge graph and the mastery-gating AI instructor as the load-bearing mechanisms.

**What is retired:**

- Globe-as-home-screen as the primary navigation surface (per the prior `docs/ui-architecture.md` Globe Navigation Model + Level-of-Detail Rendering sections, both dropped at S-0014 per ADR 0034)
- Mastery glow as the visual feedback for proficiency / mastery transitions (per the prior `docs/session-lifecycle.md` Globe as Home Screen + Mastery Verification reward framing)
- Cross-domain tendrils as the visual representation of cross-domain bridges
- Trophy framing of the globe ("the globe is the trophy as well as the map")
- Game-flavored "exploring a world / territory of knowledge" framing
- "Knowledge as a world" metaphor

**What survives intact:**

- The pedagogical dependency graph as data ([ADR 0001](0001-pedagogical-edges-not-historical.md), [ADR 0017](0017-postgres-recursive-ctes-over-owl-rdf.md), [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md))
- Concept-not-thinker node granularity ([ADR 0008](0008-concept-nodes-not-thinkers.md))
- Cross-domain porosity as a data commitment ([ADR 0007](0007-cross-domain-porosity.md)) — bridges remain first-class graph elements; their UI rendering becomes contextual surfacing during engagement and planning, not visual tendrils on a globe
- The mastery model: portable mastery, continuous contextual assessment, organic verification, engagement-depth aggregation, sub-signal storage, historical-max tracking ([ADR 0009](0009-portable-mastery.md), [ADR 0010](0010-continuous-contextual-assessment.md), [ADR 0013](0013-mastery-verification-organic-escalation.md), [ADR 0023](0023-engagement-depth-aggregation.md), [ADR 0024](0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](0025-historical-maximum-tracking.md))
- The AI instructor split: Sonnet teaches, Opus reviews ([ADR 0014](0014-sonnet-teaches-opus-reviews.md))
- Bring-your-own-book close reading ([ADR 0011](0011-no-hosted-copyrighted-material.md), [ADR 0005](0005-per-text-interpretive-outline.md))
- Privacy posture: structural-not-substantive storage, hard-delete-with-cascade, individual-only data regime ([ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md))
- The cost ceiling mechanism ([ADR 0029](0029-personal-financial-cost-ceiling.md))
- Three bounded engagement contexts (concept engagement, diagnostic, close reading) per [ADR 0028](0028-input-side-scope-structural-not-prompt.md)
- The personal-project disposition commitments 2–6 from [ADR 0032](0032-personal-project-disposition.md) (cost-priced subscription, no free tier, builder eats API costs, no BYOK, no funnel mechanics, static polish). Commitment 1 (single iOS) broadens at S-0015 in ADR 0035 to iPhone + iPad + Mac via Designed-for-iPad; the disposition spirit is preserved (single SwiftUI codebase, bounded maintenance, no Android, no web, no native AppKit Mac).

**This is realignment, not a reversal of [ADR 0032](0032-personal-project-disposition.md).** The personal-project disposition continues. The mission realignment is operating discipline that protects the *mission*, in the same way ADR 0032 is operating discipline that protects *pedagogy* from builder-funnel-mechanic corruption. Both commit *removing optionality* as the fix for slow drift toward optimizing for the wrong thing.

## Consequences

- **The globe / reward closure is structural, not deferral.** Future sessions encountering "could we add a globe / mastery glow / tendril visualization" must supersede this ADR; per-session re-litigation is not authorized. The closure binds in the success case (per the [ADR 0032](0032-personal-project-disposition.md) refusal-not-deferral pattern): if the app succeeds and a globe / reward visualization "would be cool," the response is to author a superseding ADR with explicit reasoning for why the original rationale no longer holds, or to keep the surface clean.

- **`docs/MISSION.md` What this is reframes around the structured-guidance gap** at S-0013 (light revision in this session). The pedagogical-graph-as-novel-value framing survives; the cross-domain-porosity commitment survives. The "users select a target topic / system traverses prerequisites / generates a reading syllabus" framing survives — it's the operational version of the structured-guidance value.

- **[ADR 0018](0018-flat-domain-tags-community-detection.md) is light-revised at S-0013 to remove the globe-rendering use case.** The flat-domain-tags + community-detection algorithm survives as a graph-analysis primitive; potential downstream uses include discovery-surface concept clustering, syllabus organization heuristics, and graph-quality audits during seed authoring. The Decision section's "spatial grouping at different zoom levels on the globe" framing strips; the algorithm-and-storage-shape commitment is unchanged.

- **The replacement product structure (Discovery / Planning / Engagement triad) is committed at S-0014 in ADR 0034.** This ADR records the obsolescence of the prior structure; ADR 0034 records what replaces it. The two are paired by design — ADR 0033 alone would leave a hole; ADR 0034 alone would have no recorded justification for breaking the prior commitment.

- **The platform-scope supersession (iPhone + iPad + Mac via Designed-for-iPad) lands at S-0015 in ADR 0035, superseding [ADR 0032](0032-personal-project-disposition.md).** The reasoning is connected: the editorial / typographic / library-shaped product structure that follows from the globe drop works best when larger screens do the heavy work and the phone is a follow-up surface. The Apple-platform broadening preserves the disposition spirit (single SwiftUI codebase, bounded maintenance, no Android, no web, no native AppKit Mac) while widening commitment 1.

- **Rendering policy [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) is extended at S-0016 to add forbidden tokens for globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language in agent output.** The voice-discipline intent — Paideia's AI instructor sounds like an editorial-scholarly tutor, not a game master — is structurally enforced via the forbidden-token contract. The closure is bidirectional: surface drops in this ADR; voice-discipline drops in ADR 0027's revision.

- **`docs/ui-architecture.md` and `docs/session-lifecycle.md` are substantially rewritten at S-0014.** The Globe Navigation Model and Level-of-Detail Rendering sections drop wholesale; the trophy/glow/tendril framing in Mastery Verification drops. The settled survivors (Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, Mastery Verification Through Downstream Teaching's organic-escalation framing per [ADR 0013](0013-mastery-verification-organic-escalation.md)) are preserved. Concurrent Syllabus Limit (hard cap of five) survives.

- **Secondary docs sweep at S-0016 lands `Resolved: 2026-04-30` markers on globe/trophy tension entries in `docs/tensions.md`** and removes residual references in `docs/pedagogy.md`, `docs/architecture.md`, `docs/learner-model.md`, `docs/CROSS_REFERENCES.md`, `README.md`, `docs/prep-paideia-prompt-pack.md`, `docs/pedagogy/inferences.md`, and `docs/infrastructure.md`. Tension entries are not deleted (per the project's tension-resolution discipline); they are re-marked Resolved.

- **The corruption-vector pattern recorded here generalizes.** The drift was not "we picked a bad UI" but "we picked a UI without first sharpening the value claim, and then the UI started shaping what work felt aligned with the project." Future sessions reading this ADR cold should apply the test: does this proposal commit to a presentation surface before the value claim it serves is sharp? If yes, the proposal needs the value claim sharpened first.

- **This ADR does not rise to [`docs/MISSION.md`](../docs/MISSION.md)'s strong-working-commitments list.** This is operating discipline (mission focus), not a new pedagogical commitment. Same precedent as [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0029](0029-personal-financial-cost-ceiling.md), [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0032](0032-personal-project-disposition.md). The MISSION.md commitment 2 ("Operating discipline must not corrupt pedagogy") absorbs this — the threat the commitment guards is the same one operating here (presentation surfaces drifting attention from the value claim).

- **The MemPalace decision drawer for this ADR carries the conversational reasoning verbatim.** The S-0013 exploration that surfaced the mission drift — including the user's identification that "the globe and reward systems distract from the simple mission" plus the recognition that "discussing complex phenomenology to mastery after navigating a little 8-bit character around a map seems like a tonal mismatch" — is recall-by-similarity content for future sessions facing analogous "we have a great UI metaphor but does it serve the value claim" choices. The drawer is filed in the same session per the two-layer decision-recording discipline in CLAUDE.md.

- **Phase 1.5 opens at S-0013 (this session) and closes at S-0016.** Phase 2 (Build Plan Scaffolding) — previously queued for S-0013 per [ADR 0032](0032-personal-project-disposition.md)'s S-0012-close STATE.md handoff — defers to S-0017 so the per-phase chunks Phase 2 produces consume the realigned contract.

- **Recovery from a silent drop is recorded here.** The Phase 1.5 plan was approved via plan-mode at S-0013 boot but the plan file landed in a developer-local plans directory, not in tracked project artifacts. STATE.md still pointed S-0013 at Phase 2. A subsequent session starting cold from STATE.md would have found no record of the realignment. The recovery — recording Phase 1.5 in [ROADMAP.md](../../ROADMAP.md), STATE.md, and this ADR — is part of S-0013's scope, recorded so the silent-drop pattern is itself part of the visible session history. The lesson: plan-mode artifacts are durable for the AI's session-internal use but do not propagate into the project's session protocol on their own.

## See also

- ADR 0034 (lands at S-0014) — Discovery / Planning / Engagement triad as primary product structure; the replacement structure paired with this ADR's closure.
- ADR 0035 (lands at S-0015) — Multi-platform Apple expansion; supersedes [ADR 0032](0032-personal-project-disposition.md) by broadening commitment 1 to iPhone + iPad + Mac via Designed-for-iPad.
- [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — extended at S-0016 with forbidden tokens for globe / reward / territory / exploration language in agent output.
- [ADR 0018](0018-flat-domain-tags-community-detection.md) — light-revised at S-0013 to remove the globe-rendering use case; algorithm survives as graph-analysis primitive.
- [ADR 0032](0032-personal-project-disposition.md) — operating discipline that protects pedagogy from builder-funnel-mechanic corruption; this ADR is the parallel "operating discipline that protects mission focus from presentation-surface drift."
- [ADR 0001](0001-pedagogical-edges-not-historical.md) and [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — the two load-bearing mechanisms of the realigned mission claim (structured graph + mastery-gating instructor).
- [`docs/MISSION.md`](../docs/MISSION.md) — What this is reframed at S-0013 in this session.
- [ROADMAP.md](../../ROADMAP.md) — Phase 1.5 inserted at S-0013 in this session; Phase 9 success criteria rewritten at S-0015 per ADR 0035.
- [`docs/ui-architecture.md`](../docs/ui-architecture.md) and [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) — substantially rewritten at S-0014 per ADR 0034.
