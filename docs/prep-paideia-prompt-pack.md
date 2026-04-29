# Paideia — Deliberation Prompt Pack

Each prompt below is designed to paste into a fresh session with MCP filesystem access to the Paideia project files. Sessions should be run roughly in order — earlier sessions may produce file updates that later sessions depend on.

> **Updated 2026-04-29 during S-0001 foundation reorganization:** design documents have moved from the repository root into `docs/`. Where this file says "architecture.md", read "docs/architecture.md", and so on for all design documents. References to `CONTEXT.md` (deleted during S-0002 split) are replaced below with `STATE.md` (current state pointer) + `ROADMAP.md` (phase sequence) + relevant ADRs in `adr/` (S-0003). The historical references to "commitment N added in CONTEXT.md" should be read as "absorbed into ADR 000N during S-0003."

**Completed sessions:**
- ~~Schema Foundations~~ (2026-04-07): Node granularity principle, concrete edge schema, node versioning (graph_version counter), portable mastery. Decisions recorded in architecture.md.
- ~~Session Lifecycle & Interaction Design~~ (2026-04-07): Globe as home screen, concept engagement as atomic learning unit, mode transition signals (textual only, no timing inference), proficiency as implied transition, boss encounter UX, five-syllabus hard cap, routing after concept completion, cross-syllabus convergence surfacing. Decisions recorded in session-lifecycle.md; globe vs syllabus tension resolved in tensions.md.
- ~~Assessment & Mastery Verification~~ (2026-04-07): Three-dimensional assessment rubric (reconstruction, application, boundary awareness), scaffolding proximity as evidence discount, rigor tiers (foundational/intermediate/advanced) as per-node property, mastery verification as organic escalation within downstream teaching (not cross-syllabus interruption), engagement depth as composite variable (generative ratio, scaffolding proximity, novelty), interaction types (direct_teaching, assessment, callback_reference, incidental_mention, cross_domain_connection), active-use decay suppression, decay recovery as reconnection not remediation. Decisions recorded in pedagogy.md, session-lifecycle.md, and architecture.md.
- ~~Self-Correction & Node Mapping~~ (2026-04-08): Sonnet/Opus boundary for self-correction (Sonnet logs tensions, Opus reviews in batch), tension log schema with five tension types mapping to the five feedback loops, batch review cycle (weekly/biweekly) over real-time graph editing, teaching session context (current concept + prerequisites + two-hop neighborhood for entity resolution of spontaneous learner references including concepts not in mastery history). Decisions recorded in self-correction.md.
- ~~Reading System & Outline Generation~~ (2026-04-08): Mastery graph as primary parametric teaching surface (no copyright dependency); close reading as optional deep-dive with "bring your own book" model; outline generation from parametric knowledge as baseline, user-supplied commentary as optional enhancement; domain-specific reading profiles (philosophy, literature, history, psychology); event emission from close reading to learner model (high scaffolding proximity, moves concepts to exposed/proficiency, rarely mastery); dialectical text handling via teaching-mode encoding in outline entries; storage economics negligible (~150MB per user with 40 books); repeatable setup per text (acquire, upload, review outline). Decisions recorded in reading-system.md and content-strategy.md; outline rigidity tension resolved in tensions.md; commitment 5 revised, commitment 11 added in CONTEXT.md.
- ~~Product Identity & Institutional Design~~ (2026-04-08): Freshman-level calibration defaults with autodidact ceiling (asymmetry of failure is directional — default toward the learner who cannot recover); audience vs. market distinction (community college students shape defaults, departments are deferred market); syllabus upload pipeline (parse → resolve → gap analysis → generate constrained path) with entity resolution shared with close reading; institutional schema provisions (nullable cohort_id, shareable constrained paths) preserving institutional path without building enterprise wrapper; pricing deferred as premature. Decisions recorded in architecture.md, business.md, pedagogy.md, tensions.md; commitment 12 added in CONTEXT.md.
- ~~Learner Model Implementation~~ (2026-04-09): Exponential decay with rigor-score-modulated parameters (half-life and floor both functions of continuous rigor score 0.0–1.0, replacing categorical rigor tier). Mastery computation function (four-stage: per-event decayed strength, asymptotic aggregation, conditional decay floor, fixed threshold state mapping at 0/0.3/0.7). Backward inference as soft evidence injection via synthetic events modulated by prerequisite rigor score, propagating through immediate prerequisites only. Learner-relative assessment principle (AI evaluates against learner's available conceptual vocabulary, not field knowledge). Server-side mastery computation with thin native clients (event emitters and snapshot consumers). Offline sync via local event queuing with cached mastery snapshots. V1 defaults: BASE_HALF_LIFE = 60 days, MAX_FLOOR = 0.6. Deployment target updated to native iOS/Android as primary, web as test surface. Decisions recorded in learner-model.md and pedagogy.md.
- ~~Seed Graph & Node Schema~~ (2026-04-09): Node schema settled (id, label, domain TEXT[], summary, teaching_notes, aliases, rigor_score_computed, rigor_score_adjustment, provenance, confidence, status, superseded_by, graph_version_added, timestamps). Rigor score computation formula (α·inbound_rigor_mass + β·prerequisite_count + γ·downstream_depth, V1 weights 0.5/0.3/0.2). Two-column override model (adjustments don't propagate). Domain tags as flat labels (no hierarchy; globe spatial grouping from community detection on topology). LOD rendering via Louvain/Leiden. OWL/RDF rejected. Seed graph rebuild reclassified as implementation task (direct database seeding, not JSON). architecture.md split into five files. philosophy-graph-seed.json archived. Decisions recorded in architecture.md and ui-architecture.md.

---

## Session 9: Engagement Depth Aggregation

*Topic: Settling the aggregation function for the three engagement depth signals*

learner-model.md defines three signals composing engagement depth (generative ratio, scaffolding proximity, novelty) but explicitly defers the aggregation function. This needs settling before the mastery computation function can run — engagement depth is an input to every stage.

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, and learner-model.md from the Paideia project folder on the MCP filesystem. Focus on the Engagement Depth section and the Mastery Computation function.

Engagement depth is a composite of three signals — generative ratio, scaffolding proximity, and novelty — but the aggregation function is deferred. I need to settle it. The choice matters because engagement depth feeds both the mastery computation (as a multiplier on raw event strength) and the decay model (as a modifier on half-life). A bad aggregation makes the entire evidentiary pipeline unreliable.

Work through this with me:

1. THE CANDIDATES. Weighted sum, minimum-of-three, geometric mean, or something else? Each has different failure modes. Weighted sum lets one strong signal compensate for weak ones — is that desirable? Minimum-of-three means all three must be present for high depth — is that too strict? Geometric mean penalizes zeros harshly — is that the right behavior when scaffolding proximity is high (near 1.0, meaning heavily scaffolded)?

2. SIGNAL RANGES. Each signal needs a defined range. Are all three 0.0–1.0? Is scaffolding proximity inverted (0 = fully scaffolded, 1 = no scaffolding) or direct? The mastery computation pseudocode multiplies engagement_depth into raw strength and half-life, so the composite value's range directly affects score dynamics.

3. INTERACTION WITH MASTERY COMPUTATION. Walk me through example calculations. Take a concrete teaching exchange where the learner paraphrases the AI's explanation (high scaffolding proximity, low generative ratio, low novelty). Then take one where the learner spontaneously connects to a different domain (low scaffolding proximity, high generative ratio, high novelty). Compute the engagement depth under each candidate aggregation, feed it into the mastery computation, and show me which aggregation produces the most defensible mastery score trajectory.

4. EDGE CASES. What engagement depth does a backward_inference synthetic event carry? What about an incidental_mention? These aren't real teaching exchanges — do the three signals even apply, or do these interaction types bypass the composite and use a fixed depth value?

I want to leave with a specific function, specific signal ranges, and specific fixed-depth values for non-teaching interaction types. Write it as pseudocode I can drop into the mastery computation.
```

---

## Session 10: Decay Parameter Verification

*Topic: Verifying that V1 decay parameters produce correct behavior under realistic usage patterns*

The decay model and mastery computation function have concrete parameters (BASE_HALF_LIFE = 60 days, MAX_FLOOR = 0.6) but no one has run the numbers through realistic scenarios to confirm the behavior is right. This session is pure arithmetic.

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, and learner-model.md from the Paideia project folder on the MCP filesystem. Focus on Mastery Decay, Mastery Computation, and Active-Use Decay Suppression.

The V1 parameters are set (BASE_HALF_LIFE = 60 days, MAX_FLOOR = 0.6) but nobody has verified they produce correct behavior under realistic usage patterns. I need you to run the numbers. Use the mastery computation pseudocode in learner-model.md as the specification.

Work through these scenarios with concrete calculations:

1. ACTIVE LEARNER, LOW-RIGOR CONCEPT. A learner reaches proficiency on "Cartesian Dualism" (rigor ~0.15) through two direct_teaching events with moderate engagement depth (~0.6). They then advance downstream and generate one callback_reference per week for six weeks. Show me the mastery score trajectory week by week. Does the concept stay solidly at proficiency? Does the floor activate correctly?

2. ACTIVE LEARNER, HIGH-RIGOR CONCEPT. Same pattern for "Transcendental Idealism" (rigor ~0.85). Two direct_teaching events, then weekly callbacks. Does the score hold, or does the high decay rate outrun the callback reinforcement? If callbacks aren't sufficient to maintain proficiency on high-rigor concepts, the active-use decay suppression principle is violated.

3. ABANDONED CONCEPT. A learner reaches proficiency on a mid-rigor concept (~0.5), then completely stops engaging for 6 months. Show the decay curve. When does it drop below proficiency? Does the floor behavior feel right — does it land at a score that represents "you knew this once but it's faded" rather than "you never learned it"?

4. MASTERY VERIFICATION TRAJECTORY. A learner reaches proficiency through teaching, then 3 weeks later produces a successful mastery verification event (assessment type, engagement depth ~0.9). Show the score before and after the verification. Does it cross the 0.7 mastery threshold? If not, how many verification-quality events are needed?

5. BACKWARD INFERENCE. A learner masters a downstream concept. The system generates a backward_inference event on a prerequisite (rigor ~0.4) with modulated strength. What mastery state does the prerequisite land at? Does it feel right — should a single backward inference push a concept to proficiency, or only to exposed?

For any scenario where the behavior is wrong, propose adjusted parameters and re-run. I want to leave with either confirmed parameters or revised ones.
```

---

## Session 11: Historical Maximum Tracking

*Topic: Implementation decision for the decay floor's proficiency precondition*

The decay floor only activates if a concept has ever reached proficiency. This requires tracking the historical maximum aggregate. The spec acknowledges two options (stored high-water mark vs. recomputation) and defers. This interacts with offline/sync because the cached snapshot needs floor state.

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, and learner-model.md from the Paideia project folder on the MCP filesystem. Focus on Mastery Computation (Stage 3: Decay Floor), Offline and Sync, and the scale-appropriate engineering principle in infrastructure.md.

The mastery computation's decay floor is conditional: it only activates if the concept's historical maximum aggregate has ever reached the proficiency threshold (0.3). I need to decide how to track this. Two options exist:

1. STORED HIGH-WATER MARK. A `max_historical_score` column on a `user_concept_cache` table. Updated every time mastery is recomputed. Simple to query, trivial to include in the cached snapshot sent to clients. Downside: it's a mutable state column on what's otherwise an event-sourced system — a philosophical compromise, even if practically harmless.

2. RECOMPUTATION FROM EVENT HISTORY. Every time mastery is computed, replay the full event history to determine whether the aggregate ever crossed 0.3 at any point. Correct by construction. Downside: the "historical maximum" isn't just the max of decayed strengths at query time — it requires simulating the aggregate at each event's timestamp with the decay state as of that moment to determine whether proficiency was ever reached. This is heavier than it sounds.

Walk me through the tradeoffs concretely. Which approach should I use at current scale (n=1-3)? Does the answer change at n=10,000? How does the choice interact with the offline sync model — the cached mastery snapshot sent to clients needs to include whether the floor is active, so the tracking mechanism must feed the snapshot generation.

I want a concrete decision and, if it's the stored high-water mark, the schema addition.
```

---

## Session 12: Fork Maintenance Timeline

*Topic: When to stop tracking DeepTutor upstream and accept full independence*

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, infrastructure.md (Implementation Base: DeepTutor Fork), and tensions.md (Fork Maintenance) from the Paideia project folder on the MCP filesystem.

DeepTutor is actively developed. The fork will diverge because the guided reading agent and pedagogical layer are architecturally different from upstream. The tension has been open since the project started. I need to close it.

The practical questions:

1. WHAT'S WORTH TRACKING. Which upstream components actually matter for bug fixes and security patches — the LiteLLM provider abstraction? The session management layer? The RAG pipeline? For each reusable component, how coupled is it to the rest of the codebase? Could patches be cherry-picked, or does divergence make that impractical after a certain point?

2. TIMELINE. At what point does the cost of tracking upstream (reading changelogs, evaluating patches, resolving merge conflicts) exceed the benefit of receiving fixes? My prior assessment said ~6 months. Challenge that if it's wrong.

3. TRIGGER FOR INDEPENDENCE. Is this a calendar decision (stop tracking after N months) or a milestone decision (stop tracking once we've replaced component X)? What's the cleaner framing?

I want to resolve this tension and move it out of tensions.md. Give me a concrete recommendation.
```

---

## Session 13: Gamification & Milestone Tone

*Topic: Drawing the line between emotionally resonant milestones and gamification*

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, tensions.md (Gamification Tone), session-lifecycle.md (Mastery Verification Through Downstream Teaching), and pedagogy.md (Mastery Verification — After Mastery Verification) from the Paideia project folder on the MCP filesystem.

The mastery verification design implicitly answers some of the gamification question — mastery glow activates, tendrils appear, the AI's tone is recognition not congratulation. But the broader tension is still open: where does the line fall between "emotionally resonant milestone" and "gamification that alienates serious learners"?

Work through this with me:

1. WHAT EXISTS. The current design has: globe mastery glow, tendrils activating on mastery, AI tonal recognition at verification moments, and no naming or labeling of assessment mechanics. Is this already sufficient as a milestone system, or is there a gap between "mastery glow on the globe" and something that feels like genuine accomplishment?

2. WHAT DOESN'T BELONG. Badges, streaks, leaderboards, XP, levels — which of these are categorically wrong for this product, and which might work if reconceived? The "dungeon master" insight says achievements should feel earned not accumulated. Does that rule out all of these, or only the ones that reward behavior rather than understanding?

3. THE FAMILY DIMENSION. If age-aware paths eventually exist, younger learners might need more visible reward mechanics than adults. Does this argue for a configurable reward layer, or does introducing gamification for children inevitably leak into the adult experience?

4. RESOLUTION. Can we close this tension with a concrete principle — something like "the only rewards are intrinsic to the knowledge structure itself (territory unlocked, connections visible, new domains accessible)" — or does the question need to stay open until the globe is actually built and we can feel whether the glow is enough?

Push me to close this if it can be closed. Tell me to leave it open if closing it now would be premature.
```

---

## Session 14: Media Edge Quality

*Topic: Whether and how to distinguish types of supplementary media connections*

```
You are a design partner for the Paideia project — a knowledge mastery app built on a pedagogical dependency graph.

Read STATE.md, ROADMAP.md, tensions.md (Media Edge Quality), and expansion.md (Supplementary Media Layer) from the Paideia project folder on the MCP filesystem.

Film/art/music connections to concept nodes range from well-documented intellectual relationships (Wagner and Nietzsche were in direct conversation) to loose thematic rhyming (this film "feels existentialist"). The open question is whether to formally distinguish these in the schema.

Work through this with me:

1. DOES THE DISTINCTION MATTER PEDAGOGICALLY? If a learner has mastered Existentialism and the system suggests Bergman's The Seventh Seal — does it matter whether the system says "Bergman was directly engaging with existentialist philosophy" vs. "this film resonates thematically with existentialism"? Does the learner's experience change based on the classification?

2. SCHEMA COST. If the distinction is worth making, what does it look like in the data model? A `connection_type` field on the media metadata? A confidence score similar to edges? How many categories are useful without being pedantic?

3. GENERATION FEASIBILITY. The generation strategy in expansion.md already flags all connections as unverified until the user confirms. Does that verification step naturally produce the classification (the user says "yes, this is a real intellectual connection" vs. "this is a nice thematic pairing"), or is the user unlikely to make that judgment?

4. RESOLUTION. Is this a "decide now and encode in the schema" question, or a "defer until the media layer is actually being built" question? What's lost by deferring?

If this can be closed with a simple decision, close it. If it's genuinely premature, say so and I'll leave it in tensions.md.
```

---

## Notes on Session Order

**Session 9 is the highest priority** — engagement depth aggregation is a prerequisite for prototype work. Session 10 (decay verification) depends on Session 9. Session 11 (historical max) is a small schema decision that can run anytime. Sessions 12, 13, and 14 are independent and lower priority — they close open tensions but don't block engineering work.

Each session should end by identifying what to update in the project files and confirming the changes before writing.
