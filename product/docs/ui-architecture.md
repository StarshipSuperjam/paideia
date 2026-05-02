# UI Architecture
**Substantially rewritten: 2026-04-30 (S-0014 — per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). The prior Globe Navigation Model and Level-of-Detail Rendering sections were dropped wholesale per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md); this file now describes the Discovery / Planning / Engagement triad as primary product structure.)**

Paideia's UI is organized around three primary surfaces — **Discovery**, **Planning**, and **Engagement** — corresponding to the three structurally distinct problems the structured-guidance value claim answers (per [`MISSION.md`](MISSION.md) and [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md)): figuring out what to learn at all, knowing what to understand first, and knowing whether you have actually learned the thing rather than become familiar with its facts. Each surface owns one of those answers; the surfaces are not interchangeable.

The triad is committed by [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). This file specifies how the surfaces are structured and how they connect.

## Discovery Surface

The Discovery surface is the entry point for identifying what to learn. Two parallel affordances feed into the same plan-generation pipeline downstream. Both are first-class — neither is a fallback for the other.

### AI conversational onboarding

The user describes interests, fragments of curiosity, areas they keep encountering. The AI proposes specific concept-level targets and a plan to reach them. This is the path for learners who arrive without a specific target and need a guided way to surface one.

The conversational onboarding surface is bounded by [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md)'s purpose-not-topic discipline. It is structurally similar to the diagnostic context — both are bounded conversational surfaces whose semantic frame is "the user is bringing material toward identifying a learning target," not "the user is initiating an arbitrary task." The agent's response to redirected-task input on this surface follows the same pattern as the diagnostic and concept-engagement contexts (per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md) and [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md)): a brief acknowledgment that this surface is for finding learning targets, an offer to step out via the exit affordance, no lecturing.

The output of a conversational onboarding session is one or more candidate target concepts plus a syllabus proposal that the user accepts (handing off to the Planning surface) or rejects (returning to the Discovery surface to try a different framing).

### Browseable concept catalog

A directly-navigable view of the system's concept coverage. The user with a clear target ("I want phenomenology," "I want the categorical imperative," "I want to read Hume") finds it without conversation. The catalog is organized by domain and topic, with concept-level granularity (per [ADR 0008](../adr/0008-concept-nodes-not-thinkers.md)).

**Catalog organization heuristics may consume the flat-domain-tags + community-detection algorithm preserved by [ADR 0018](../adr/0018-flat-domain-tags-community-detection.md).** The algorithm — Louvain or Leiden community detection on edge topology to produce concept neighborhoods — survives [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md)'s globe drop because its consumer shifts; the new consumer is the catalog's organization (which concepts cluster together in the catalog view) rather than spatial layout on a globe. The algorithm's output is a hierarchy of concept neighborhoods that the catalog UI can use to organize browsing — concepts share a neighborhood when they share many prerequisite relationships, which is the same structural signal that made the algorithm useful for spatial grouping. Domain tags (per the Node Schema in [`architecture.md`](architecture.md)) provide additional categorical organization (filter-by-domain, color-coding) without enforcing taxonomy.

**Catalog state surfaces mastery contextually.** Mastered concepts in the catalog are marked as mastered (consistent with the Planning surface's contextual surfacing of mastery — see below). The catalog is not a separate trophy / library surface; it is a coverage view that happens to also show what the user has mastered when they pass through it.

### Discovery output: handoff to Planning

Both Discovery affordances terminate at the same handoff: the user has identified a target concept (or a small set of related concepts), and the system generates a syllabus to reach it. The syllabus generation pipeline traces prerequisite chains from the user's current mastery state to the target, producing an ordered sequence of concept nodes.

The Discovery surface owns target identification. It does not own plan execution; that belongs to the Planning surface.

## Planning Surface

The Planning surface is the committed working mode for a chosen target. Each plan is a syllabus — an ordered sequence of concept nodes that traces prerequisite chains from the user's current mastery state to the target.

### Syllabus-as-plan

A syllabus is a first-class object the user can see in full. The syllabus view shows:

- **Prerequisite ordering.** The concept sequence the user will work through, with prerequisite chains made visible.
- **Current position.** Where the user is in the syllabus right now.
- **Mastered concepts in their syllabus context.** Concepts the user has already mastered are visible within the syllabus; they are not hidden, and they are not aggregated into a separate library/bookshelf surface (foreclosed by [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)). Mastery is contextual information, not a standalone view.
- **Upcoming concepts, prerequisite-gated.** Concepts whose prerequisites are unmet are visible in the syllabus but not yet available for engagement. The gate is structural — the user sees what is coming and what is required to reach it.
- **Completion markers.** Completed concepts are marked completed within the syllabus. There is no celebration affordance, no glow visual, no badge. Completion is information, not spectacle.

### Prerequisite gating

Concepts with unmet prerequisites are visible but not yet available for engagement. The gate is structural — the user is shown what is coming and what is required to reach it, not blocked from seeing the future shape of the plan. This makes the syllabus pedagogically transparent: the user can see why the current concept matters (it unlocks downstream concepts) and what the prerequisite topology looks like for the rest of the plan.

The gating mechanism consumes the mastery state per [ADR 0009](../adr/0009-portable-mastery.md) (one mastery state per concept, regardless of path) and the engagement-depth aggregation per [ADR 0023](../adr/0023-engagement-depth-aggregation.md) / [ADR 0024](../adr/0024-engagement-depth-sub-signals-stored-raw.md). When prerequisite mastery is reached, the gate opens and the concept becomes available for engagement.

### Quiet completion markers

Completed concepts are marked completed within the syllabus. No celebration affordance, no glow visual, no badge, no animation, no sound. Completion is state, not spectacle.

The organic-verification framing per [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md) survives unchanged: proficiency is quiet (the AI eases the conversation toward closure without announcing the transition), mastery is a moment in the conversation (a quiet zero-scaffolding question after sufficient distance has accumulated through downstream callbacks), and the Planning surface reflects that state when it changes. The surface does not generate reward feedback; it reflects what the engagement and verification mechanisms have already produced.

### Current/active syllabus view

The hard cap of five concurrent active syllabi survives from the prior contract. The pedagogical rationale (more than five concurrent paths means insufficient momentum on any path to reach mastery depth) is unchanged.

The Planning surface shows the user's active set. The most recent or decay-urgent syllabus may be foregrounded for one-action resume; the user can switch between active syllabi within the planning surface. If the user attempts to start a sixth, the app states plainly: "You have five active paths. To start a new one, complete or set aside one of your current paths." The Planning surface signals the cap directly when the user attempts to exceed it (the prior contract's "the visual density of the globe itself signals" rationale dropped with the globe).

Parked syllabi (paused by the user) are not displayed alongside active syllabi but are accessible from a list within the Planning surface. Parking a syllabus preserves all progress and frees up an active slot.

### Cross-syllabus convergence — bridge surfacing in context

When two active syllabi share an upcoming concept or are approaching an intersection via cross-domain edges, the Planning surface notes it: "This concept also appears on your path toward [other target]. Studying it advances both."

This is the cross-domain bridge discovery mechanism, surfaced contextually during planning rather than as a standalone visualization. Cross-domain edges remain first-class graph data per [ADR 0007](../adr/0007-cross-domain-porosity.md); the rendering convention is **bridge surfacing in context**, not visual tendrils on a separate surface (the prior contract's tendril visualization was retired with the globe per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md)).

Bridge surfacing happens at two natural moments:

- **At Routing After Concept Completion** (when a concept engagement completes and the user returns to the Planning surface). The system surfaces the convergence at this moment because it is when the user is choosing what to do next.
- **At plan generation** (when a new syllabus is being generated and overlaps with an active one). The system flags the overlap so the user can see the cross-domain shape of their study before committing.

There is no separate cross-domain-bridge visualization surface. Bridge data is first-class; rendering is contextual.

## Engagement Surface

The Engagement surface is where actual concept-level work happens. It is **structurally inherited from [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md)** — the three bounded engagement contexts settled there are the Engagement surface, unchanged. This file describes how the Engagement surface connects to the rest of the UI; it does not redefine the contexts themselves.

### Three bounded engagement contexts

Per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md):

1. **Concept engagement (Mode 2/3 teaching).** The atomic unit of teaching per [`session-lifecycle.md`](session-lifecycle.md). The user has entered a concept and is working through it; the agent classifies input under the three teaching modes per [`pedagogy.md`](pedagogy.md) and responds within the mode.
2. **Diagnostic conversation.** The cold-start probe (Cold Start / Initial Calibration per [`pedagogy.md`](pedagogy.md)). The user is answering targeted prerequisite probes; the conversation is bounded semantically by the probe set.
3. **Bring-your-own-book close reading.** Per [ADR 0011](../adr/0011-no-hosted-copyrighted-material.md). The user is working through a specific text they have uploaded; the text and the current passage bound the conversational scope.

Within each context, the discrimination line is purpose-not-topic per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md): on-task means the user's input *brings material* (a connection, an example, a question about significance, an interpretation, a struggle); off-task means the user's input *redirects* the system to a different task. Cross-context Mode 3 connections are explicitly preserved — the discipline is "stay on the *learning*," not "stay on the concept."

### How users reach Engagement

- **From Planning.** Selecting the next available (prerequisite-met) concept on an active syllabus enters concept engagement.
- **From Discovery (diagnostic).** A cold-start user without an established mastery profile is routed through the diagnostic context as part of plan generation; the diagnostic is reached from the Discovery surface, exits to the Planning surface with a generated syllabus.
- **From a user-uploaded text (close reading).** Bring-your-own-book close reading is reached from the user's library of uploaded texts (a secondary surface accessed from within Planning or from a menu); the close reading session itself is an Engagement context. The exit affordance returns the user to the source text or to the Planning surface.

### Exit affordance — first-class UI primitive

Per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md), the user has a visible, intentional way to step out of any concept engagement / diagnostic / close reading surface. The exit affordance:

- **Is a single visible control**, reachable in one action from any Engagement context.
- **Returns the user to the Planning surface** when exiting concept engagement or close reading.
- **Returns the user to the Discovery surface** when exiting a diagnostic conversation (the diagnostic was reached from Discovery; the exit returns there).
- **Is not a "general chat" surface.** The user who wants to do something else takes the exit and enters a different bounded context (or leaves the app), rather than drifting the current one.

The exit affordance is the structural alternative to general chat. Its first-class status across all Engagement surfaces is a Phase 9 implementation requirement per the Phase 9 success criteria in [ROADMAP.md](../../ROADMAP.md).

### Bridge surfacing in engagement

The AI instructor surfaces cross-domain bridges contextually during teaching:

- **Callback references** per [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md) — when teaching a downstream concept, the AI naturally references upstream concepts. Where the upstream concept lives in a neighboring domain, the callback is also a bridge-revealing moment ("this connects to what you've worked through in [other domain]"). Callbacks are pedagogically genuine *and* probe-valuable *and* bridge-revealing — three uses of the same teaching move.
- **In-engagement prerequisite surfacing.** When a cross-domain prerequisite has just become reachable (a prerequisite chain has unblocked through the user's recent mastery progress), the agent may note it in passing during a relevant teaching turn. This is contextual surfacing, not a notification.

This is the same bridge-surfacing-in-context convention as the Planning surface — same data ([ADR 0007](../adr/0007-cross-domain-porosity.md) cross-domain edges as first-class graph data), same convention (contextual, not standalone visualization), different moment (during teaching versus during plan navigation).

## Cross-surface concerns

### Mastery state across surfaces

Mastery is per-concept, per [ADR 0009](../adr/0009-portable-mastery.md) (one mastery state per concept, regardless of path). The same mastery state surfaces on:

- **Discovery (catalog).** Mastered concepts in the catalog show as mastered.
- **Planning (syllabus view).** Mastered concepts within a syllabus show as mastered; this is the primary surface where mastery state is visible.
- **Engagement (callback references).** Mastered upstream concepts are eligible for callback references during downstream teaching.

The state itself is single-source-of-truth (the `mastery_snapshots` table per the data model in [`architecture.md`](architecture.md) and [`learner-model.md`](learner-model.md)). The surfaces consume it; they do not maintain independent representations.

### Secondary surfaces

The triad is the *primary* product structure. Secondary surfaces — accessed from menus within or alongside the primary surfaces — include:

- **Settings / account.** Profile, sign-out, subscription management.
- **Delete-account affordance** per [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) — first-class UI primitive (Phase 9 success criterion); reachable from the settings menu; satisfies Apple App Store guideline 5.1.1.
- **Data-export affordance** per [ADR 0032](../adr/0032-personal-project-disposition.md) commitment 6 — first-class UI primitive (Phase 9 success criterion); preserves cancellation-discipline honesty; reachable from the settings menu.
- **User library of uploaded texts.** The list of texts the user has uploaded for bring-your-own-book close reading (per [ADR 0011](../adr/0011-no-hosted-copyrighted-material.md)). Accessed from within Planning (the close-reading entry point) or from a menu.
- **Parked-syllabus list.** The set of syllabi the user has paused. Accessed from within the Planning surface.

Secondary surfaces support operational continuity; they do not answer one of the three structured-guidance problems and therefore are not part of the triad. Adding a *primary* surface outside the triad (e.g., a globe, a stand-alone library/trophy view, a community surface, a globe-shaped alternative under another name) requires superseding [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md).

### Render-readiness across surfaces

The render-readiness contract per [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) ([`AGENT_INSTRUCTIONS.md`](../AGENT_INSTRUCTIONS.md)) applies to all agent output across all surfaces — Discovery (conversational onboarding), Planning (occasional agent-authored copy in convergence notes), and Engagement (the three bounded contexts). The forbidden-token enumeration is extended at S-0016 per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md)'s consequences to add globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language; the agent's voice across all surfaces is editorial-scholarly, not game-master.

The triad's surface design and the forbidden-token enumeration are bidirectional: the surface around the agent does not invite game-master framing because the triad does not include game-shaped surfaces, and the agent's voice does not reach for that framing because the rendering policy rules it out.

### What is foreclosed at the surface level

Per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md) (foreclosures restated for visibility in this file):

- No globe, no spatial-traversal navigation, no "knowledge as a world" metaphor.
- No game-world rendering, no character-on-map framing, no exploration-as-traversal mechanic.
- No separate trophy surface; mastered concepts surface contextually within syllabi (Planning) and within the catalog (Discovery).
- No library/bookshelf as a third primary surface.
- No mastery-glow / tendril / colored-trail visualization.
- No general chat surface (per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md), restated here for completeness).

Adding any of these as a primary surface requires superseding [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). The library/bookshelf and the Discovery dual-path are explicitly held *open for amendment* per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)'s open-variability section — Phase 9 cold-test evidence may justify amending without supersession in those two specific cases.

---
*Last updated: 2026-04-30 (S-0014 — substantial rewrite per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). Globe Navigation Model and Level-of-Detail Rendering sections from the prior 2026-04-09 file dropped wholesale per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md). ENGINE_LOG remains the authoritative session-by-session ledger.)*
