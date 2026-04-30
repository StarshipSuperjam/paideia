# Session Lifecycle & Interaction Design
**Substantially rewritten: 2026-04-30 (S-0014 — per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). The prior Globe as Home Screen section was dropped wholesale per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md); the trophy/glow/tendrils framing in Mastery Verification was retired in the same closure. The atomic-unit framing, mode transitions, proficiency-as-implied-transition, routing-after-concept-completion, and organic-verification framing per [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md) all survive intact and are preserved below.)**

This file describes how the user moves through the app on a per-concept basis: how a concept engagement is structured, how the AI shifts teaching modes, how proficiency transitions happen, how routing works between concepts, and how mastery is verified. It complements [`ui-architecture.md`](ui-architecture.md), which describes the triad of primary surfaces (Discovery / Planning / Engagement) — this file describes what happens *within* the Engagement surface and how the user moves between concepts.

## Entry Surfaces

The user reaches a concept engagement from the Planning surface — selecting the next available (prerequisite-met) concept on an active syllabus. The Planning surface is the home of concept-level work; concepts are launched from it and the user returns to it.

A cold-start user without an established mastery profile is routed through the diagnostic context (one of the three bounded engagement contexts per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md)) as part of plan generation; the diagnostic is reached from the Discovery surface and exits to the Planning surface with a generated syllabus. Bring-your-own-book close reading is reached from a user-uploaded text within the user's text library (a secondary surface accessed from Planning); the close-reading session itself is an Engagement context.

Active syllabi (max five, hard cap) are visible on the Planning surface. The most recent or decay-urgent syllabus may be foregrounded for one-action resume. The user can switch between active syllabi within the Planning surface, or step into discovery to identify a new target. Parked syllabi (paused by the user) are accessible from a list within the Planning surface; parking preserves all progress and frees an active slot.

## Concurrent Syllabus Limit

Hard cap of five active syllabi. If the user attempts to start a sixth, the app states plainly: "You have five active paths. To start a new one, complete or set aside one of your current paths."

The rationale is pedagogical, not aesthetic. More than five concurrent learning paths means insufficient momentum on any one path to reach mastery depth. The limit respects the user's ambition while protecting their investment.

## Concept Engagement as the Atomic Unit

The atomic unit of learning is the **concept engagement** — the entire arc of working through one concept step on a syllabus, from entry to proficiency, however many sittings that takes. A concept engagement is one continuous conversational thread. The user can close the app mid-conversation and resume hours or days later; the thread picks up seamlessly. The AI does not announce the gap or ask "where were we?" unless the gap exceeds roughly a day, in which case a brief, minimal reorientation is offered — restating the last point of discussion, not re-explaining the concept.

This means "session" in Paideia does not mean "a block of time the user spent in the app." It means "the complete interaction arc for one concept." A concept engagement may span a ten-minute bus ride, a pause of several hours, and a thirty-minute stretch on the couch — all one engagement.

## Mode Transitions

The three teaching modes from the expression contract ([`pedagogy.md`](pedagogy.md)) are triggered entirely by textual signals in the user's most recent response. No timing-based inference — long pauses are never interpreted as confusion. The mode classification signals:

**Mode 1 (direct explanation):** The user explicitly asks for clarification. The user's response misrepresents what the text says. The user's response reveals missing vocabulary or context the concept depends on.

**Mode 2 (Socratic leading):** The user can paraphrase correctly but doesn't see significance. The user asks "so what?" or "why does this matter?" The user's response is accurate but shallow.

**Mode 3 (testing interpretation):** The user makes a claim about what the text means. The user draws a connection. The user proposes an interpretation.

The AI shifts between modes without announcing the shift. The ideal arc within a single concept engagement is 1→2→3, but the AI follows wherever the user's responses lead, including backward transitions (a user in mode 3 who reveals a gap drops back to mode 1 for that gap, then re-advances).

## Proficiency as Implied Transition

Proficiency is never announced. The AI does not say "you've demonstrated understanding" or label the user's mastery state. When the AI judges the user has grasped the concept, it eases the conversation toward closure — naturally wrapping up, connecting the concept to what comes next. The Planning surface advances the user's position within the syllabus when the engagement closes; the user moves to the next step when ready.

If the AI judges the user has not reached proficiency, it does not say so. It continues teaching, continues probing, keeps the conversation going. The system never labels a user as stuck or unproficient.

## Routing After Concept Completion

When a concept engagement completes (the user advances past the proficiency point), the user returns to the Planning surface. From there, the user can: continue to the next step on the current syllabus, switch to another active syllabus, return to Discovery to identify a new target, or close the app.

This is the moment to surface cross-syllabus convergence. If two active syllabi share an upcoming concept or are approaching an intersection via cross-domain edges, the Planning surface notes it: "This concept also appears on your path toward [other target]. Studying it advances both." This is the cross-domain bridge discovery mechanism (per [ADR 0007](../adr/0007-cross-domain-porosity.md) and [`architecture.md`](architecture.md)) surfaced contextually during planning rather than as a standalone visualization. Cross-domain edges remain first-class graph data; the rendering convention is **bridge surfacing in context** per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md).

## Mastery Verification Through Downstream Teaching

Mastery verification happens within the syllabus the concept belongs to — never as a cross-syllabus interruption. The mechanism is organic escalation, not scheduled testing. This is the commitment settled by [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md) and preserved unchanged by [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md) and [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md); only the visual-reward framing is stripped from this section.

**Callback references.** As the learner moves downstream from a proficient concept, the AI naturally references it while teaching subsequent concepts. These callbacks are pedagogically genuine — you cannot teach Phenomenology without referencing Transcendental Idealism. Each callback is also a probe: the AI observes how fluently the learner engages with the referenced concept. These interactions are logged as reinforcing events with moderate engagement depth per [ADR 0023](../adr/0023-engagement-depth-aggregation.md) / [ADR 0024](../adr/0024-engagement-depth-sub-signals-stored-raw.md). Where the upstream concept lives in a neighboring domain, the callback also surfaces a cross-domain bridge contextually — the same teaching move serves as pedagogical reference, mastery probe, and bridge-revealing moment.

**Escalation to verification.** Over several downstream concepts, the callbacks accumulate evidence about the learner's retention. At some point — when enough distance separates the learner from the original teaching — the AI stops scaffolding a callback and instead asks the learner to do the work. This is the mastery verification moment. It is not announced or labeled. The AI applies the zero-scaffolding constraint (questions only, no explaining, no hinting) and evaluates the response against the three-dimensional rubric (reconstruction, application, boundary awareness — see [`pedagogy.md`](pedagogy.md)).

**No naming, no labeling.** The system never uses the term "boss encounter," "mastery test," or any equivalent in the user-facing experience. The user experiences a moment where the AI asks a harder question than usual. If they succeed, the syllabus marks the concept as mastered (a quiet completion marker on the Planning surface per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)) and cross-domain bridges surface contextually in subsequent engagement and planning moments. If they don't, the AI continues teaching without announcing failure, and another opportunity will arise naturally further downstream.

**Tonal shift as the signal.** The AI's behavior during a verification moment is the only signal that the rules have changed. It becomes less helpful, more demanding — deliberately withholding the scaffolding the user is accustomed to. The experience should feel challenging, not procedural.

**Quiet recognition.** After successful verification, the syllabus on the Planning surface marks the concept as mastered. The AI's tone in the closing turn is recognition, not congratulation — it treats the user as someone who accomplished something real, not someone who needs a gold star. A brief note of what mastery of this concept opens up (cross-domain bridges that have just become reachable, downstream concepts now available on the syllabus) serves as the natural continuation of the teaching, not a reward affordance. The recognition is intrinsic to the system — new territory of inquiry becomes reachable, surfaced contextually — not a badge earned.

Proficiency is quiet. Mastery is a moment in the conversation, reflected as state on the Planning surface — not a UI event.

## Exit and Return

The exit affordance per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md) is a first-class UI primitive across every Engagement context. A single visible control, reachable in one action from any concept engagement / diagnostic / close-reading surface, returns the user to the Planning surface (or, for the diagnostic, to the Discovery surface — the diagnostic was reached from Discovery, the exit returns there).

The exit affordance is the structural alternative to general chat. The user who wants to do something else takes the exit and enters a different bounded context (or leaves the app), rather than drifting the current one. There is no general chat surface; "ask Paideia anything" is foreclosed by [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md).

When the user returns to a concept engagement after exiting, the conversational thread resumes per the atomic-unit framing above — same brief reorientation discipline (none under a day, minimal otherwise) applies whether the gap is intra-session (exit and return) or inter-session (close the app and reopen).

---
*Last updated: 2026-04-30 (S-0014 — substantial rewrite per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md). Globe as Home Screen section dropped wholesale and Mastery Verification's trophy/glow/tendril reward language stripped, both per [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md). Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, Mastery Verification Through Downstream Teaching's organic-escalation framing per [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md), and Concurrent Syllabus Limit (hard cap of five) all preserved. CHANGELOG remains the authoritative session-by-session ledger.)*
