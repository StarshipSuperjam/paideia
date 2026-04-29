# Session Lifecycle & Interaction Design
**Added: 2026-04-07**

## Globe as Home Screen

The globe is always the entry surface. It serves three functions no other surface can: it's the orientation device (where am I in the territory of knowledge?), it's the trophy (mastery glow accumulates over time, making the globe more beautiful the more the user learns), and it's the cold-start surface for users who don't yet know what they want to study.

Active syllabi are displayed as colored trails on the globe surface with destination markers showing the target concept. When the user opens the app, the most recent or decay-urgent syllabus is foregrounded with a one-tap resume. The user can always rotate and explore the globe instead.

Completed syllabi leave no trail artifact. The illuminated nodes they produced are the only persistent record. This keeps the globe readable over years of use — accumulated mastery glow enriches it, accumulated trail artifacts would clutter it.

Parked syllabi (paused by the user) are not displayed on the globe. They are accessible from a list or menu elsewhere in the app. Parking a syllabus preserves all progress and frees up an active slot.

## Concurrent Syllabus Limit

Hard cap of five active syllabi. No soft warning — the visual density of the globe itself signals when the user has many active paths. If the user attempts to start a sixth, the app states plainly: "You have five active paths. To start a new one, complete or set aside one of your current paths."

The rationale is pedagogical, not aesthetic. More than five concurrent learning paths means insufficient momentum on any one path to reach mastery depth. The limit respects the user's ambition while protecting their investment.

## Concept Engagement as the Atomic Unit

The atomic unit of learning is the **concept engagement** — the entire arc of working through one concept step on a syllabus, from entry to proficiency, however many sittings that takes. A concept engagement is one continuous conversational thread. The user can close the app mid-conversation and resume hours or days later; the thread picks up seamlessly. The AI does not announce the gap or ask "where were we?" unless the gap exceeds roughly a day, in which case a brief, minimal reorientation is offered — restating the last point of discussion, not re-explaining the concept.

This means "session" in Paideia does not mean "a block of time the user spent in the app." It means "the complete interaction arc for one concept." A concept engagement may span a ten-minute bus ride, a pause of several hours, and a thirty-minute stretch on the couch — all one engagement.

## Mode Transitions

The three teaching modes from the expression contract (pedagogy.md) are triggered entirely by textual signals in the user's most recent response. No timing-based inference — long pauses are never interpreted as confusion. The mode classification signals:

**Mode 1 (direct explanation):** The user explicitly asks for clarification. The user's response misrepresents what the text says. The user's response reveals missing vocabulary or context the concept depends on.

**Mode 2 (Socratic leading):** The user can paraphrase correctly but doesn't see significance. The user asks "so what?" or "why does this matter?" The user's response is accurate but shallow.

**Mode 3 (testing interpretation):** The user makes a claim about what the text means. The user draws a connection. The user proposes an interpretation.

The AI shifts between modes without announcing the shift. The ideal arc within a single concept engagement is 1→2→3, but the AI follows wherever the user's responses lead, including backward transitions (a user in mode 3 who reveals a gap drops back to mode 1 for that gap, then re-advances).

## Proficiency as Implied Transition

Proficiency is never announced. The AI does not say "you've demonstrated understanding" or label the user's mastery state. When the AI judges the user has grasped the concept, it eases the conversation toward closure — naturally wrapping up, connecting the concept to what comes next. The UI surfaces the next step on the syllabus; the user advances when ready.

If the AI judges the user has not reached proficiency, it does not say so. It continues teaching, continues probing, keeps the conversation going. The system never labels a user as stuck or unproficient.

## Routing After Concept Completion

When a concept engagement completes (the user advances past the proficiency point), the system presents routing options: continue to the next step on the current syllabus, switch to another active syllabus, or return to the globe.

This is the moment to surface cross-syllabus convergence. If two active syllabi share an upcoming node or are approaching an intersection via cross-domain edges, the system notes it: "This concept also appears on your path toward [other target]. Studying it advances both." This is the cross-domain bridge discovery mechanism (architecture.md) surfaced through navigation rather than conversation.

## Mastery Verification Through Downstream Teaching
**Revised: 2026-04-07**

Mastery verification happens within the syllabus the concept belongs to — never as a cross-syllabus interruption. The mechanism is organic escalation, not scheduled testing.

**Callback references.** As the learner moves downstream from a proficient concept, the AI naturally references it while teaching subsequent concepts. These callbacks are pedagogically genuine — you cannot teach Phenomenology without referencing Transcendental Idealism. Each callback is also a probe: the AI observes how fluently the learner engages with the referenced concept. These interactions are logged as reinforcing events with moderate engagement depth.

**Escalation to verification.** Over several downstream concepts, the callbacks accumulate evidence about the learner's retention. At some point — when enough distance separates the learner from the original teaching — the AI stops scaffolding a callback and instead asks the learner to do the work. This is the mastery verification moment. It is not announced or labeled. The AI applies the zero-scaffolding constraint (questions only, no explaining, no hinting) and evaluates the response against the three-dimensional rubric (reconstruction, application, boundary awareness — see pedagogy.md).

**No naming, no labeling.** The system never uses the term "boss encounter," "mastery test," or any equivalent in the user-facing experience. The user experiences a moment where the AI asks a harder question than usual. If they succeed, mastery glow activates and tendrils appear. If they don't, the AI continues teaching without announcing failure, and another opportunity will arise naturally further downstream.

**Tonal shift as the signal.** The AI's behavior during a verification moment is the only signal that the rules have changed. It becomes less helpful, more demanding — deliberately withholding the scaffolding the user is accustomed to. A subtle UI reinforcement (a slight shift in background tone or header) may accompany this, but should be understated enough that a first-time user might not consciously notice it. The experience should feel challenging, not procedural.

**Reward.** After successful verification, mastery glow activates on the globe and cross-domain tendrils become visible. The AI's tone is recognition, not congratulation — it treats the user as someone who accomplished something real, not someone who needs a gold star. A brief note of what mastery of this concept opens up (new connections, new territory) serves as the reward. The reward is intrinsic to the system: new territory unlocked, not a badge earned.

Proficiency is quiet. Mastery is a moment.

---
*Last updated: 2026-04-07 (mastery verification revised — organic escalation replaces cross-syllabus interruption model)*
