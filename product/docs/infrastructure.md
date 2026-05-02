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
**Added: 2026-04-07 | Revised: 2026-04-09**

Primary deployment target is native iOS and Android apps. Primary reading happens on iPhone/iPad and Android devices, not at a desktop.

1. **Web app as test surface.** DeepTutor's Next.js frontend is already responsive. Use the web app to work out system logic, prove the pedagogy, and iterate on the teaching interaction before investing in native packaging. The web UI is retained as an additional access point at negligible marginal cost.
2. **Native iOS/Android as primary.** Apache 2.0 permits App Store distribution with attribution only. Build native frontends talking to the Python backend via API. The native apps are thin clients — event emitters and mastery snapshot consumers — with computation on the server (see learner-model.md, Offline and Sync).
3. **Sideloading option (iOS).** WebView wrapper for personal use avoids App Store entirely. $99/year Apple developer account or free with 7-day expiration.

## MCP Database Access
**Added: 2026-04-07**

Claude Pro supports MCP database connections as of March 2026. The relational learner model can use a real database (PostgreSQL or SQLite via MCP server) from day one, even in the personal-use phase. This means no forced choice between MCP and a proper database — the MCP protocol is the connection layer, the database is the storage layer. Anthropic ships an official PostgreSQL MCP server.

## Cloud Hosting Stack
**Added: 2026-04-07**

Chosen stack: **Vercel + Supabase + Anthropic API**. Three managed services, no servers to operate, free tiers cover personal use and early public access comfortably. All components use standard formats with straightforward migration paths — no proprietary lock-in.

Supabase (managed Postgres) handles both the relational learner state and vector search via pgvector, consolidating two concerns into one service. This eliminates Neo4j Aura as a separate graph database. The prerequisite graph lives as a nodes/edges table structure in Postgres; traversal logic runs in application code. A dedicated graph database adds migration complexity (Cypher, no universal export standard) with no performance benefit at projected scale.

Claude Code interacts with all three services directly — Supabase via CLI and SDK, Vercel via CLI for deploy and environment management, Anthropic API natively in code. No manual copy-paste between environments after initial credential setup.

## Build Approach
**Added: 2026-04-07**

Schema-first, everything-else-iterative. The graph schema and learner model tables in Supabase are the one place a bad early decision compounds — wrong tables simultaneously touch migrations, seeded data, and API logic when refactored. Write a deliberate schema spec before the first `CREATE TABLE`. Everything else — the Discovery / Planning / Engagement triad surfaces (per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)), interaction model, teaching behavior — sits on top of the data model and refactors cheaply via Git. Build order: settle the schema, then let the rest emerge through building. GitHub handles the surface; the schema is the one thing worth protecting upfront.

**Scale-appropriate engineering (n=1-3 users).** *(Added: 2026-04-07)* At current projected user count, the event-sourced learner model can be queried live with no performance concerns. Do not build materialized views, caching layers, or precomputed mastery scores. Build the event-sourced architecture because the *structure* demands it, but defer the performance optimization layer until user count actually requires it. This applies equally to graph traversal — recursive CTEs or client-side traversal are both fine at this scale. Choose whichever is simpler to implement and revisit if the graph exceeds several hundred nodes with per-user mastery joins.

## Cost Mitigation Ideas (Untested)

- Cache common path generations (many users target the same topics).
- Tiered session depth — lighter API use for browsing, heavier only for active teaching.
- Fine-tuned smaller model over time for routine interactions.

---
*Last updated: 2026-04-09 (split from architecture.md)*
