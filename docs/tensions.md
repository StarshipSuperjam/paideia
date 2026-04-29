# Open Tensions

Active tradeoffs and unresolved questions. When one is resolved, move it to the relevant downstream file and note the resolution.

---

## Build Scope vs. Personal Tool
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. The product is a commercially sustainable venture, not a personal tool and not a donation. The standing disposition in business.md has been revised accordingly. Pedagogical integrity is the hard constraint on commercial decisions — revenue logic must never change what the product teaches or how it teaches — but the product is designed to sustain itself and reach users beyond the builder.

---

## Gamification Tone
**Added: 2026-04-07 | Partially resolved: 2026-04-07**

The "dungeon master" insight is compelling — learning as RPG, badges as records of what you've done, not Pavlovian rewards for showing up. Badges tied to intellectual achievement ("Traced Hume's skepticism to Kant's response") feel different from generic activity badges. The map filling in over time as the trophy. Boss encounters for hard concepts (Kant's Critique, Being and Time) as genuinely dramatic moments.

**Partial resolution:** The dungeon master framing is a personal insight about what learning could *feel like* — not necessarily a product feature to build. It informs the emotional register of milestone design and how mastery moments are narrated back to the learner. It does not commit the product to a game layer. A game gatekept by reading Hegel is unlikely to find a large audience, and building it that way is also significantly harder to build. The insight survives as a design sensibility: achievements should feel *earned*, not accumulated. The AI's role at milestone moments is closer to DM narration than to a notification badge.

**Remaining tension:** Where exactly the line falls between "emotionally resonant milestone" and "gamification that alienates serious learners" is not yet drawn.

---

## Graph Scaling
**Added: 2026-04-07 | Partially resolved: 2026-04-07**

45 nodes in the philosophy prototype. Hundreds needed per domain at concept-level granularity (see Node Granularity Principle in architecture.md). Each node requires expert judgment for prerequisite edges plus resource recommendations. **Partially resolved:** Two developments substantially reduce this bottleneck. First, existing academic reference works (encyclopedias, Oxford dictionaries per domain) serve as curated node inventories with cross-references — the nodes exist and don't need to be invented. Claude generates first-pass prerequisite edges; the user validates through experience. This makes initial construction an ingestion problem, not a scholarship problem (see content-strategy.md). Second, the self-correcting feedback loops (see architecture.md) mean the graph doesn't need to be perfect at launch — wrong edges cost a minor detour, not a catastrophic failure, and consistent usage patterns reshape the graph over time. **Remaining tension:** the initial ingestion pipeline itself is nontrivial engineering, and cross-domain edges still require human judgment that no reference work provides.

---

## Multi-Domain Expansion
**Added: 2026-04-07**

The architecture is domain-agnostic but every new domain requires its own curated graph, corpus sourcing, and potentially its own supplementary media connections. Cross-domain edges (philosophy ↔ theology, mathematics ↔ physics) are architecturally simple but editorially complex. No prioritization of which domains come after philosophy, or whether the owner curates them personally or finds another path.

---

## API Cost at Engagement
**Added: 2026-04-07**

Most engaged users are most expensive. Mitigation ideas exist (caching, tiered depth, smaller models) but none are tested. The fundamental tension between rich Socratic teaching and affordable operation is unresolved.

---

## Media Edge Quality
**Added: 2026-04-07**

Film/art/music connections range from well-documented (Wagner ↔ Nietzsche) to loose thematic rhyming. Whether to formally distinguish "participated in the conversation" from "happens to resonate" adds value but also complexity. Not yet decided.

---

## Outline Rigidity for Dialectical Texts
**Added: 2026-04-07 | Resolved: 2026-04-08**

Resolved. The outline encodes teaching mode per section, including dialectical reversals. A dialectical entry specifies that the reader should be led to find the current position compelling (mode 2) before the reversal arrives, at which point the AI shifts to testing the reader's interpretation (mode 3). The outline scripts the reader's encounter with self-undermining arguments rather than forcing linearity. This format applies to any text with intentional reversals — Hegel, Kierkegaard, Nietzsche, Wittgenstein, and literary works. Resolution details in reading-system.md under "Dialectical Text Handling."

---

## MCP Persistence vs. Database
**Added: 2026-04-07 | Partially resolved: 2026-04-07**

Original tension: learner model designed for MCP filesystem (markdown files), needs a database if multi-user. **Partially resolved:** MCP on Claude Pro can connect to databases directly (PostgreSQL, SQLite) via official MCP servers. No forced choice — MCP is the connection protocol, the database is the storage. The learner model can start on a relational database from day one, even for personal use. Remaining tension: local database on your own machine vs. cloud-hosted if the app ever serves other users.

---

## Personal Tool vs. Sustainable Service
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. Subsumed by the resolution of "Build Scope vs. Personal Tool" above. The standing disposition now reads as a commercial sustainability commitment with pedagogical integrity as the hard constraint. The gap between "build for yourself" and "find a way to make it accessible" has closed — the product is being built to sustain itself commercially from the start.

---

## Self-Learner Product vs. Institutional Product
**Added: 2026-04-07 | Resolved: 2026-04-08**

Resolved. Community college students are the primary audience (shaping pedagogical defaults); community college departments are the primary market (shaping eventual enterprise features). The v1 build priority is the teaching system, not the institutional wrapper. Freshman-level calibration defaults serve both audiences because the asymmetry of failure is directional — the freshman cannot proceed if the interaction is beyond their scope, while the autodidact is mildly annoyed at worst and rapidly escalated by the adaptive system. The cold-start framing communicates that the system adapts to engagement quality, which simultaneously reassures the freshman and activates the autodidact. Schema provisions (nullable cohort_id on events, shareable constrained paths) preserve the institutional path without building the enterprise wrapper now. LMS integration, instructor dashboards, FERPA compliance, and grade export are all bolt-on features deferred until the teaching system proves itself. Resolution details in business.md under "Audience vs. Market: Community College," pedagogy.md under "V1 Calibration Defaults," and architecture.md under "Institutional Schema Provisions."

---

## Fork Maintenance
**Added: 2026-04-07**

DeepTutor is actively developed (v1.0.0-beta.1 shipped April 2026). Forking means diverging from upstream. The guided reading agent is architecturally different enough from their roadmap that contributing upstream is unlikely. Tension: how long to track upstream changes (bug fixes, provider updates, security patches) before the fork is fully independent? No resolution yet.

---

## Non-Profit Structure vs. Cost Recovery
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. Defer incorporation until grant applications or institutional pilots are actually in scope — likely 12–24 months out. The App Store requires no non-profit status; incorporating before that point adds overhead with no concrete benefit. The right triggers are grant eligibility requirements or entering formal institutional relationships with community colleges. Mechanics and timing documented in business.md under "Non-Profit Incorporation."

---

## Mastery State Terminology
**Added: 2026-04-07**

The working vocabulary is: **not encountered → exposed → proficiency → mastery**. This collapses the earlier four-state model (not encountered / exposed / demonstrated / inferred) by renaming "demonstrated" to "proficiency" and folding "inferred" into "mastery" (mastery of a downstream concept implies mastery of prerequisites via backward inference).

What isn't yet resolved: whether these four states are the right granularity, and whether the labels match the phenomenology of learning well enough to be legible to a user. The globe prototype used a simpler three-state model (awareness / proficiency / mastery), which collapses "not encountered" and "exposed" into a single pre-engagement state. There's an argument for that: from the learner's perspective, the distinction between "never seen this" and "vaguely familiar" may not feel meaningfully different, whereas the system needs both states to route teaching correctly. Whether the user-facing vocabulary should mirror the internal model or be a simplified presentation layer over it is unresolved.

---

## Globe Navigation vs. Syllabus Path Generation
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. The globe is the home screen and exploratory surface. The syllabus is the committed working mode entered when a user taps a concept and chooses to study it. Active syllabi (max five) appear as colored trails on the globe; completed syllabi leave no trail — mastery glow is the only persistent record. Full resolution in session-lifecycle.md and architecture.md under Globe Navigation Model.

---

## Concept Node Versioning
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. Full node versioning is not justified at current scale. A `graph_version` monotonic counter is recorded on each learner event, making future full versioning a migration rather than a reconstruction. Resolution details in architecture.md under "Node Versioning."

---

## Per-Path vs. Portable Mastery
**Added: 2026-04-07 | Resolved: 2026-04-07**

Resolved. Mastery is portable — per-concept, not per-concept-per-path. One glow state per concept on the globe. If mastery doesn't transfer to a new context, the node is too coarse and should be split (the granularity principle does the work). Path context is recorded on events for analysis but not used in mastery computation. Resolution details in architecture.md under "Portable Mastery."

---

## OQ-DEC1-A: Server-side mastery computation — confirm or revisit?
**Added: 2026-04-29 (S-0001) | Status: Open | Decide before: Phase 6**

Current architecture (per `learner-model.md`) computes mastery server-side with thin native clients (event emitters and snapshot consumers). Phase DEC.1 (between Phase 5 and Phase 6) is the natural moment to revisit. Reasons to confirm: keeps clients thin, allows mastery formula updates without client deploys, single source of truth. Reasons to revisit: client-side could enable richer offline UX, lower API cost. Decision lands as an ADR with Status: Accepted, implementation tag Phase 6.

---

## OQ-DEC1-B: Two-hop neighborhood retrieval shape for teaching session context
**Added: 2026-04-29 (S-0001) | Status: Open | Decide before: Phase 6**

`self-correction.md` names "current concept + prerequisites + two-hop local neighborhood for entity resolution of spontaneous learner references" as the teaching context. Phase DEC.1 settles the concrete retrieval shape: which prerequisites count (immediate only, all-recursive-up-to-rigor-floor, etc.), which two-hop edges count (prerequisite-only, also `enables` and `informed_by`), how aliases are resolved, what the per-turn token cost is. Decision lands as an ADR.

---

## OQ-DEC1-C: Embedding strategy for entity resolution
**Added: 2026-04-29 (S-0001) | Status: Open | Decide before: Phase 6**

The entity-resolution service (per `architecture.md`) needs embeddings to map spontaneous learner references ("the categorical imperative") onto graph node IDs. pgvector is the leaning option (already a Supabase extension, already enabled). Open question: which embedding model? OpenAI ada-002, voyage-3, claude-3-5-sonnet-embeddings, or open-weights (BGE / Nomic / Stella)? Trade-offs: API cost, dimensionality (storage), domain-fit for philosophical vocabulary, control over future model changes. Decision lands as an ADR.

---

## OQ-DEC1-D: Chunk-resolver index vs direct SEP URL pointers
**Added: 2026-04-29 (S-0001) | Status: Open | Decide before: Phase 6**

When the teaching layer wants to point a learner at SEP for onward reading, two options: (a) maintain a chunk-resolver index that maps node IDs → SEP article section anchors (more retrieval precision, more upfront indexing work), or (b) store direct SEP URL pointers per node and let the learner browse from the section landing (simpler, less precise). Decision lands as an ADR.

---

## OQ-PHASE8-A: Evaluation baseline choice
**Added: 2026-04-29 (S-0001) | Status: Open | Decide at: Phase 8 entry**

Per the principle "closed-loop validation is weak signal" (becomes ADR in S-0003), Phase 8 evaluation must use external baselines. Three candidates: (a) external rubric — community college instructor blind review of teaching transcripts, (b) head-to-head against DeepTutor unmodified (same input, both systems' output graded blind), (c) head-to-head against stock Sonnet without rendering policy (same input, control vs treatment). Or some combination. Decision deferred to Phase 8 entry; needs at least the (a)+ (c) pair to have signal at all (a) tests teaching-quality absolutely; (c) isolates the rendering policy's contribution).

---

## OQ-PRIVACY-A: Erasure mechanism for learner data
**Added: 2026-04-29 (S-0007) | Status: Open | Decide before: Phase 3**

ADR 0026 commits to "persistent learner storage is structural, not substantive" but does not settle the GDPR Article 17 right-of-erasure mechanism. Three candidates on the table:

(a) **Crypto-shredding** — encrypt events with a per-learner key; delete the key on erasure. Strongest fit for the event-sourced architecture (`mastery_snapshots` derive from decrypted reads; deleting the key renders events permanently inert without a cascading event-delete). Implementation cost: per-learner KMS key, encrypted-at-rest column or table-level encryption. Compatible with the audit-trail benefit ADR 0015 calls out — events remain in the table, just unreadable.

(b) **Hard-delete with cascade** — `DELETE FROM learner_events WHERE user_id = ?` plus recompute of affected `mastery_snapshots`. Simplest. Loses the audit trail; cohort-aggregated analytics that included the user retroactively change.

(c) **Anonymize-and-aggregate** — strip user identifiers, retain events for graph-level signal. Preserves structural learning across users. Whether it constitutes "erasure" under GDPR Article 17 is the contested question — depends on whether the residual data is genuinely de-identifiable, which depends on event sparsity and the rest of the schema. Likely fails the test if a learner has a distinctive engagement pattern.

Decide before Phase 3 schema authoring; the choice shapes whether `learner_events` needs an `encrypted_user_data_key` column (path a), a delete-cascade discipline (path b), or a nullable `user_id` post-erasure (path c). Decision lands as an ADR.

---

## OQ-PRIVACY-B: Institutional vs. individual data regime
**Added: 2026-04-29 (S-0007) | Status: Open | Decide before: Phase 3 (column reservation); Phase 8 (policy specification)**

Cohort-bound events (`cohort_id NOT NULL`, per the institutional schema provision in [`architecture.md`](architecture.md) Institutional Schema Provisions) may live under a different analytics-eligibility regime than individual events. The direction is itself open and worth not anchoring prematurely:

- One reading: institutional cohorts arrive via Data Processing Agreement contracts that may grant aggregate analytics rights individuals (clicking through ToS) haven't granted. Cohort-bound events are *more* eligible.
- Converse reading: institutional context (FERPA, minor users in some community-college populations) imposes stricter regime than individual ToS click. Cohort-bound events are *less* eligible.

One concrete proposal to evaluate: a column on `learner_events` like `eligible_for_aggregate_analytics`, with Opus's batch review filtering on the column. Both the column shape and the default are open. Other proposals (a separate `cohort_consent` table, runtime policy lookup, regime per cohort_id rather than per event) are also on the table.

Decide before Phase 3 to reserve any required columns (column slot is cheap to add then, expensive later). The policy specification (what governs eligibility, what defaults are correct, what runtime gates apply) defers to Phase 8 alongside actual institutional partner conversations — speculative regime design without a real partner produces brittle policy. Decision lands as an ADR (or two: one for the column at Phase 3, one for the policy at Phase 8).

---

## OQ-WATCH-FLAG-FILE
**Added: 2026-04-29 (S-0001) | Status: Open (tagged: `watch`) | Decide at: ~session 30 health check**

When the volume of "things to watch for in future evidence that aren't actionable yet but shouldn't be forgotten" justifies a separate `docs/watch-flags.md` file (vs. the current "fold into tensions.md with explicit `watch` tag"), separate it. The session-30 health check (per ADR 0022) should re-evaluate this. If `watch`-tagged tensions exceed ~10 entries, separating reduces the cognitive load of scanning tensions.md. If fewer, the unified file is simpler.

---

## OQ-BYOK-REGIME: Institutional vs. consumer bring-your-own-key
**Added: 2026-04-29 (S-0008) | Status: Open | Decide before: any non-builder consumer launch (Phase 8 entry or earlier)**

[ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) commits to bounded builder exposure but does not settle the bring-your-own-key (BYOK) regime. Two regimes have substantially different cost-architecture, privacy, and audience implications:

(a) **Institutional BYOK.** A community college, library, university, or K-12 system holds the Anthropic API key; cost flows institution → Anthropic; Paideia is the application layer above. Sidesteps [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md)'s builder-exposure problem entirely. Compatible with the institutional schema provisions in [`architecture.md`](architecture.md) Institutional Schema Provisions and the institutional path in [`business.md`](business.md) Audience vs. Market. Requires per-institution onboarding (API key configuration, billing relationship, possibly a Data Processing Agreement). The institutional users themselves never see or manage the key.

(b) **Consumer BYOK.** Individual users obtain a key at the Anthropic console and paste it into Paideia; the system uses their key for their sessions. Self-selects technically sophisticated users — not the freshman audience the system is calibrated for per [ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md). Has a meaningful interaction with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md): under consumer BYOK, Anthropic logs API calls against the user's own account per Anthropic's data retention policy, even though Paideia's own storage observes the structural-not-substantive discipline. The user's mental model of "Paideia doesn't keep my transcripts" does not include Anthropic-the-vendor's logging under their account; this needs disclosure.

The leaning shape is: **institutional BYOK keep open and pursue actively as the primary non-builder access path; consumer BYOK foreclose unless a future regime change justifies revisiting**. The leaning is not yet a settled decision because the institutional onboarding work has not been scoped, the legal-relationship surface (DPA, vendor-of-record) has not been authored, and the precise interaction with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s privacy posture under each regime needs to be worked through rather than asserted.

Decide-before any non-builder consumer launch. Decision lands as an ADR. The institutional onboarding pipeline (if accepted) becomes a Phase 8 / Phase 9 work item.

---

## OQ-WALL-BEHAVIOR: Soft-wall degradation ladder at cost cap
**Added: 2026-04-29 (S-0008) | Status: Open | Decide before: Phase 8 (cost-cap mechanism wiring) per ADR 0029**

[ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) commits the principle that walls degrade rather than terminate (the atomic unit of teaching is the concept engagement per [`session-lifecycle.md`](session-lifecycle.md), which spans hours or days; a wall that fires mid-engagement violates that integrity). What it does not settle is the **specific degradation ladder** — what changes at each step of approach to the cap, in what order.

Candidate steps to compose into a ladder:

- **Model downshift** — Opus → Sonnet for self-correction reviewer pass; or Sonnet → smaller-model-class once available. Composes with [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md)'s teaching/reviewing role split: the teaching layer can downshift independently of the review layer.
- **Retrieval shrink** — two-hop entity-resolution neighborhood → one-hop; deeper context window → shallower; reduces per-turn input token cost.
- **Cross-domain bridge cap** — bridges-per-month threshold reduces (consistent with the free-tier framing in [`business.md`](business.md) Revenue Mechanisms Explored).
- **Concept-engagement length cap** — upper-bound on per-engagement turn count or total token cost; on hit, agent surfaces a "we've spent some real time on this; let's pause and pick up next session" pattern that respects engagement integrity.
- **Soft refusal with explanation** — final fallback; agent acknowledges the cap, explains the situation, points at the exit affordance per [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md). Explicit, never silent.

The open questions: (1) what's the order? (2) at what fraction of cap does each step trigger? (3) is the ladder per-user, per-aggregate-system, or both? (4) how is the user notified, if at all, between steps? Notification is itself a design decision — silent degradation respects the [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) "no machinery narration" discipline but may surprise the user; explicit degradation creates a moment of friction that may be the right honesty trade.

Decide-before any non-builder access. Decision lands as an ADR (with operational parameters held in private configuration, per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md)'s pattern).

---

## OQ-CONTEXT-COMPRESSION: Token-amplification mitigation for multi-turn concept engagements
**Added: 2026-04-29 (S-0008) | Status: Open | Decide before: Phase 7 (Sonnet teaching prototype)**

Per-turn cost compounds with session length when the per-turn context grows turn-over-turn. Concept engagements are explicitly designed as continuous threads spanning hours or days (per [`session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit). The naive shape — load all prior turns into each subsequent turn's context — produces quadratic token growth per engagement, which interacts unfavorably with [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md)'s cost-ceiling commitment.

Three mitigation candidates (described in [`business.md`](business.md) Cost Amplification with Session Length):

(a) **Structured-state replacement.** Instead of loading full prior turns, load the structured learner state (current concept node + prerequisite states + recent event history) and only the most recent N turns; rely on the persistent event stream and `mastery_snapshots` for cross-session continuity. Matches [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript-non-persistence commitment and [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md)'s bounded-context discipline. Risk: subtle conversational state (the learner's current train of thought, the framing of an ongoing analogy) is lost when older turns drop out.

(b) **Automatic context compression at platform-supported windows.** Anthropic's prompt-caching surface mediates some of this transparently for the system-prompt portion (notably the AGENT_INSTRUCTIONS.md system prompt is an obvious cache target per [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md)'s consequences). The dynamic per-turn portion is what remains the engineering surface. Risk: vendor-mediated; we control less of the trade.

(c) **Explicit per-turn summarization.** The agent summarizes the conversation-so-far into a structured note that replaces older raw turns at a sliding window. Preserves more conversational state than (a) at the cost of an extra Sonnet call per N turns to produce the summary. Has potential interaction with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md): if the summary is persisted (e.g., to support session resume), it may reintroduce substantive content into durable state — needs to be ephemeral (in-session-scoped) or explicitly structured to honor the structural-not-substantive discipline.

The leaning shape is: **(a) for cross-session continuity (already implied by [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and event-sourcing) + (c) for within-engagement compression**, with (b) as a transparent layer underneath (we use prompt caching; we do not depend on it for correctness). Not yet settled because the precise sliding-window parameters, the summarization-prompt structure, and the cost-quality tradeoff measurements have not been done.

Decide-before Phase 7 (the prototype that produces the first multi-turn teaching-cost data). Decision lands as an ADR.

---

## OQ-PEDAGOGY-INFERENCE-LOCUS: Where pedagogical inference lives — distributed code vs. explicit rule layer
**Added: 2026-04-29 (S-0008) | Status: Open (tagged: `watch`) | Revisit when: inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR the locus complaint surfaces operationally**

The system makes pedagogical inferences continuously: "if user has mastered A and B, surface C as unlock candidate"; "if user is below mastery threshold M for >N days, downshift teaching mode"; "if user struggles with X in domain D1, search analogous concepts in D2..Dn that they've mastered, surface as bridge"; "if user spontaneously connects to a concept the graph doesn't link, log a `spontaneous_connection` tension." Where each inference *lives today* is distributed: some in the schema (which relationships are encoded), some in queries (Cypher/SQL/CTE retrieval logic per [ADR 0017](../adr/0017-postgres-recursive-ctes-over-owl-rdf.md)), some in application code (TypeScript that interprets query results), some in the rendering policy (which mode to enter, how to weight evidence).

The standing position is that this distribution is appropriate at current scale: TypeScript with good naming and good tests is already declarative-ish; a dedicated rule layer (Drools-like, or a custom DSL) is premature abstraction. But the position has not been argued through against the alternative.

The right diagnostic is **findability**, not **abstraction**: can someone — including a future Claude session — answer "how many pedagogical inferences does Paideia have, where does each live, what does each trigger on?" without grepping the entire codebase? Today, the answer is no. The cheap intermediate step that buys the deferral honestly is a **registry**: [`docs/pedagogy/inferences.md`](pedagogy/inferences.md) (stub created in S-0008) enumerates each inference, where it's expressed, what triggers it. The registry is created in this session as a forcing function for the population to become visible.

Two failure modes a rule layer would risk if adopted prematurely:
- **Conflict accumulation.** Drools-style systems are famously hard to reason about at scale because rules conflict and resolution requires meta-rules (priorities, salience, retraction). The complexity grows superlinearly.
- **Performance opacity.** A query plan is inspectable. A rule engine evaluating against working memory is much less so. For interactive Socratic teaching latency, this matters.

One thing a rule layer would buy that nothing else does: **declarative pedagogical review by non-engineers.** If the long-term contributor model includes learning scientists or subject-matter experts shaping pedagogical inference *without writing TypeScript*, that is the forcing function. If it doesn't, distributed code wins.

Revisit when: the registry crosses ~30 entries (the population is genuinely complex), or cross-domain edges per domain-pair exceed ~50 (cross-domain inference becomes the dominant traversal cost), or a concrete operational complaint surfaces (someone needs to change inference behavior and the change is hard *because* the inference is distributed). Until then, distributed code is the working position; the registry keeps the population visible. Decision lands as an ADR.

---

*Last updated: 2026-04-29 (S-0008 added four tension entries: OQ-BYOK-REGIME institutional-vs-consumer; OQ-WALL-BEHAVIOR soft-wall degradation ladder; OQ-CONTEXT-COMPRESSION token-amplification mitigation; OQ-PEDAGOGY-INFERENCE-LOCUS rule layer vs distributed inference. Three are tied to ADR 0029 cost-ceiling; the fourth opens the pedagogy-inference architecture question with a registry as the cheap intermediate step.)*
