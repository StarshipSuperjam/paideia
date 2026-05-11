# Infrastructure

## Prototype

- Working React app with directed prerequisite graph, DFS traversal, topological sort.
- Claude-powered syllabus generation (primary + supplementary readings, key concepts per step).
- Tap any step to expand details.
- Currently philosophy only. Architecture is domain-agnostic.
- Uses thinker-level nodes (deprecated). Needs rebuilding at concept level once the database is stood up.

## RAG Pipeline (Designed, Not Built)

- One-time corpus ingest per domain, not runtime scraping.
- Chunk and embed into a vector database.
- Semantic search at query time to retrieve relevant passages.
- Grounded, citable text rather than pure parametric knowledge.

## Implementation Base: DeepTutor Fork
**Added: 2026-04-07**

DeepTutor (HKUDS/DeepTutor on GitHub, Apache 2.0 license) evaluated as a fork candidate. Assessment:

**Reusable infrastructure:** Agent loop with independent workspace/memory/personality per bot. Two-layer memory persistence (PROFILE.md for long-term facts, SUMMARY.md for chronological history, with auto-consolidation when sessions grow large). RAG pipeline (LlamaIndex-based: document ingestion, chunking, embedding, retrieval). Session management with SQLite adapter. LLM provider abstraction (LiteLLM, supports multiple backends). Multi-channel delivery (Telegram, Discord, Slack, email, etc.). Soul Templates for persona definition.

**Needs replacing:** Guided Learning mode atomizes texts into discrete "knowledge points" with interactive HTML pages — the opposite of tracking a sustained argument. Memory is flat (simple markdown facts like "PhD student in computer science"), not relational (no concept mastery, cross-concept connections, or progressive confidence levels). Soul Template is a personality sketch, not a pedagogical method. Summary agent generates report-card-style assessments, not interpretive continuity.

**Recommendation:** Fork. Keep the infrastructure. Build a new "guided reading" agent alongside (or replacing) existing modes. The codebase is modular enough for surgery, not a rewrite.

## Deployment Target

Apple-only deployment per [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) commitment 1. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. No Android, no web app, no native AppKit/Catalyst Mac app.

The user-facing iOS app calls Anthropic's API directly using the user's own API key (BYOK per [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) commitment 8); the Paideia-controlled back-end (Supabase) holds only per-user mastery state derived from `learner_events` the client emits. No proxy. No transit of the user key or the raw API exchange through Paideia infrastructure.

## BYOK key handling

The user's Anthropic API key is held in iOS Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` — the user configures each device once, and iCloud Keychain sync is suppressed by design (security-clarity choice plus a match for the Anthropic "one place to rotate" model). The key never appears in logs, never appears in crash reports (Sentry/Crashlytics integration must scrub Authorization headers from any captured outgoing request), never appears in telemetry, never appears in error traces. A force-crash test pre-submission verifies zero key material in the captured crash report — this is the verification posture for Apple App Store guideline 5.1.1.

**What does and does not run on the user's device.** The user's device calls Anthropic's API directly with the user's Keychain-held key, holds the conversation, and emits per-user mastery-state `learner_events` (concept node ID, interaction_type, engagement_depth sub-signals per [ADR 0024](../adr/0024-engagement-depth-sub-signals-stored-raw.md), context fields) to the Supabase back-end — the same emission shape that was already implied by [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript-non-persistence commitment (the back-end has never seen raw transcripts even in the prior thin-clients architecture). **Graph build and graph analysis are back-end maintainer work, not user-device work** — Phase 5 seed authoring, the Opus reviewer pipeline per [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), the self-correction batch review cycle, and graph validation via `engine/tools/validate.py` all run on the maintainer's infrastructure. The user's conversations may *surface signals* the back-end's review pipeline consumes as candidate graph-update inputs (a `spontaneous_connection`, a `struggle_unresolved`, a `mastery_contradiction`), but the user's device does not author graph edits any more than a bug report authors a code patch — the maintainer adjudicates and acts. The BYOK shift narrows what passes through the back-end (no API proxy, no observation of the API exchange); it does not move any work onto the user's device that did not already live there.

The Apple App Privacy questionnaire answer for the API credential is "data not collected." The privacy *policy* (the ToS-adjacent legal document) is Phase 8 work pinned to Apple App Store submission per [ROADMAP.md](../../ROADMAP.md) Phase 8 success criteria.

## MCP Database Access
**Added: 2026-04-07**

Claude Pro supports MCP database connections as of March 2026. The relational learner model can use a real database (PostgreSQL or SQLite via MCP server) from day one, even in the personal-use phase. This means no forced choice between MCP and a proper database — the MCP protocol is the connection layer, the database is the storage layer. Anthropic ships an official PostgreSQL MCP server.

## Cloud Hosting Stack
**Added: 2026-04-07**

Chosen stack: **Vercel + Supabase + Anthropic API**. Three managed services, no servers to operate, free tiers cover personal use and early public access comfortably. All components use standard formats with straightforward migration paths — no proprietary lock-in.

Supabase (managed Postgres) handles both the relational learner state and vector search via pgvector, consolidating two concerns into one service. This eliminates Neo4j Aura as a separate graph database. The prerequisite graph lives as a nodes/edges table structure in Postgres; traversal logic runs in application code. A dedicated graph database adds migration complexity (Cypher, no universal export standard) with no performance benefit at projected scale.

Claude Code interacts with all three services directly during build-tooling work — Supabase via CLI and SDK for migration / seed work, Vercel via CLI where it serves build-side tooling, Anthropic API natively in engine-side scripts. The user-facing iOS app under BYOK does *not* consume Vercel-hosted endpoints for AI inference — the iOS client calls Anthropic directly with the user's own key per the Deployment Target section above. The Vercel surface remains relevant only to engine-side build tooling, not to the deployed user surface.

## Build Approach
**Added: 2026-04-07**

Schema-first, everything-else-iterative. The graph schema and learner model tables in Supabase are the one place a bad early decision compounds — wrong tables simultaneously touch migrations, seeded data, and API logic when refactored. Write a deliberate schema spec before the first `CREATE TABLE`. Everything else — the Discovery / Planning / Engagement triad surfaces (per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)), interaction model, teaching behavior — sits on top of the data model and refactors cheaply via Git. Build order: settle the schema, then let the rest emerge through building. GitHub handles the surface; the schema is the one thing worth protecting upfront.

**Scale-appropriate engineering (n=1-3 users).** *(Added: 2026-04-07)* At current projected user count, the event-sourced learner model can be queried live with no performance concerns. Do not build materialized views, caching layers, or precomputed mastery scores. Build the event-sourced architecture because the *structure* demands it, but defer the performance optimization layer until user count actually requires it. This applies equally to graph traversal — recursive CTEs or client-side traversal are both fine at this scale. Choose whichever is simpler to implement and revisit if the graph exceeds several hundred nodes with per-user mastery joins.

## User Cost Mitigation Patterns (Untested)

Under BYOK these are patterns the in-app teaching layer applies on the user's behalf to make the user's *own* Anthropic bill predictable — they are not Paideia-side cost protection (there is no Paideia-side cost; per [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) commitment 5, Paideia is not in the API path).

- Cache common path generations (many users target the same topics).
- Tiered session depth — lighter API use for browsing, heavier only for active teaching.
- Fine-tuned smaller model over time for routine interactions, where available.

The pedagogical-degradation discipline absorbed into [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md) per [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) is the qualitative guardrail: downshifting retrieval window or narrowing two-hop neighborhood to one-hop is a teaching move that respects engagement integrity, not a cost protection move.

## See also

- [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) — OSS pivot and BYOK disposition; commitment 1 (Apple-only deployment); commitment 8 (key handling architecture).
- [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) — transcript-non-persistence guarantee; the architectural shape that lets the server stay key-blind under BYOK.
- [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md) — Sonnet-teaches-Opus-reviews role split; absorbs the pedagogical-degradation principle that survives from the retired cost-ceiling mechanism.

---
*Last updated: 2026-05-11 (Session B of OSS+BYOK refactor per ADR 0065).*
