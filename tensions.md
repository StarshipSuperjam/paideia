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

*Last updated: 2026-04-08 (Self-Learner Product vs. Institutional Product resolved)*
