# ADR 0086 — Model-agnostic embedding storage architecture

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0152

## Context

[`product/docs/tensions.md`](../docs/tensions.md) carries OQ-DEC1-C ("Embedding strategy for entity resolution") as decide-before-Phase-6, open since 2026-04-29 (S-0001). The original tension framing named five candidate embedding models (OpenAI ada-002, voyage-3, claude-3-5-sonnet-embeddings, BGE / Nomic / Stella) and four tradeoff axes (API cost, dimensionality, domain-fit for philosophical vocabulary, control over future model changes). Phase DEC.1 (between Phase 5 and Phase 6) is the natural moment to settle.

[ADR 0065](0065-oss-pivot-and-byok-disposition.md)'s BYOK regime (S-0128) reshapes the choice fundamentally:

- Paideia is out of the API path entirely (per commitment 5 and commitment 8). Users pay Anthropic directly with their own keys; Paideia has zero embedding-API cost to optimize.
- The "API cost" tradeoff axis from the original framing becomes a user-side concern, not a project-side optimization. Different users may bring different keys (Anthropic for claude-3-5-sonnet-embeddings; Voyage Labs for voyage-3; OpenAI for text-embedding-3-small; a local pgvector instance with open-weights for BGE / Nomic / Stella).
- The decision is no longer "which model" but **"what storage shape allows BYOK users to choose their own model without forcing the project to support all of them at runtime."**

The architecture committed in [`product/docs/infrastructure.md:53`](../docs/infrastructure.md:53) to pgvector on Supabase for vector storage. The entity-resolution service ([`product/docs/architecture.md:214-224`](../docs/architecture.md:214)) is shared infrastructure across three pipelines (teaching session, close reading outline generation, syllabus upload) and operates on graph-node labels + aliases + summaries. The close-reading pipeline (per [`product/docs/content-strategy.md:46`](../docs/content-strategy.md:46)) also uses embeddings — but for text chunks (~500-token book segments), not graph nodes. The 1536-dim figure named in `content-strategy.md:46` is illustrative arithmetic for storage-cost estimation; not a schema commitment.

The migration corpus carries no `CREATE EXTENSION vector` statement and no `vector()`-typed column. The schema-level embedding commitment is not yet made; the docs name the substrate (pgvector on Supabase) but defer the column-shape to the first Phase 6 self-correction migration that needs it.

pgvector's `vector(n)` type fixes dimensionality at the column level: a single `vector(1024)` column cannot store 1536-dim embeddings. A single fixed-dim column forces all BYOK users to use models that produce that dimensionality (or re-embed via an out-of-band pipeline). This is the constraint the storage-shape decision pivots on.

### Load-bearing premises

*Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers the step under the "contract-shape change" class — it commits the schema-level embedding-storage contract that future Phase 6 migrations are bound to.*

1. **pgvector is available on the Supabase project (extension enabled).** *Falsifier:* the first Phase 6 migration that authors `CREATE EXTENSION vector` or a `vector()` column fails with `ERROR: extension "vector" is not available` or `ERROR: type "vector" does not exist`. *Test status:* attempted in-context via MCP `list_extensions` (denied by Claude Code auto-mode classifier per ADR 0055 "Production Reads" gate). Migration corpus check: no `CREATE EXTENSION vector` statement exists in any of the 50+ existing migrations, so the extension has not been enabled by the project. Supabase enables `pgvector` by default in newer projects (post-2023 platform), but the project's own `supabase_migrations.schema_migrations` table is silent on the extension state. **Premise accepted as untestable in-context; verified at first natural exercise via [`engine/build_readiness/embedding_storage_first_exercise.md`](../../engine/build_readiness/embedding_storage_first_exercise.md) Tier-1 criterion (first Phase 6 migration authoring a vector column).**

2. **Per-dim partitioned tables are implementable in pgvector without runtime surprises.** *Falsifier:* a per-dim partition table (`node_embeddings_1024(node_id, embedding vector(1024))` + `node_embeddings_1536(node_id, embedding vector(1536))` + etc.) would surface a constraint at index-creation, query-planning, or application-code-side dispatch that makes the pattern impractical (e.g., pgvector's `<->` operator family is not generic across partitions, or query routing requires N-way UNION at every lookup). *Test status:* pgvector documentation confirms `vector(n)` columns operate independently per-table; partition-by-dim is a known pattern in the pgvector community (used by AWS Bedrock embeddings, Postgres pgvector multi-tenant setups). Application-code-side dispatch on the `users.embedding_dims` metadata column routes each query to the correct partition. **Premise accepted with the documented pattern as in-context evidence.**

3. **The n=1-3 user base makes the multi-pipeline operational cost bounded.** *Falsifier:* even at n=1-3 users, the cost of maintaining per-dim partitions (re-embedding workflows when a user adds a new dim; CI test surface for each partition shape; application-code dispatch logic) exceeds the cost of forcing a single fixed model. *Test status:* operational. At n=1-3 users, expected distinct embedding-model+dim combinations is ≤3; partition count is bounded; CI test surface scales with partition count, not user count. **Premise accepted on operational grounds.**

4. **Entity resolution and close-reading share the per-dim partition scheme.** *Falsifier:* the two consumers' embedding access patterns diverge enough that sharing partition tables produces query-planner pathologies (e.g., close-reading's large-volume chunk-scan dominates the partition's planner stats, degrading entity-resolution's low-latency point lookups). *Test status:* unverifiable in-context — depends on Phase 6+ workload. **Premise accepted with the named risk; Phase 6 first-exercise readiness criterion includes a query-plan check on combined scans (added to first-exercise readiness note).**

## Decision

Embedding storage is **model-agnostic** at the schema level. Per-user embedding-model metadata lives on the `users` table (or equivalent per-user record). Embeddings are stored in **per-dimensionality partition tables**: `node_embeddings_<dim>` for entity-resolution graph-node embeddings (one row per (user_id, node_id) when the user's chosen model produces that dim), and `chunk_embeddings_<dim>` for close-reading text-chunk embeddings (one row per (user_id, chunk_id) at the matching dim). Application-code routes each query to the correct partition by reading the user's `embedding_model` + `embedding_dims` fields. A user who switches embedding models triggers a re-embedding workflow that populates the new partition and (optionally) prunes the old.

The schema-level commitment is the **partition-by-dim shape**, not specific dim values. The first Phase 6 migration that authors entity-resolution infrastructure picks the initial dim values (likely 1024 for voyage-3-class models and 1536 for OpenAI ada-002-class models, but the schema accepts any dim the user's model produces). Adding a new dim is a new migration creating a new partition table; it does not require touching existing partitions.

## Alternatives Considered

### Model-agnostic schema (per-user dim metadata + per-dim partitions) — chosen

- **What:** Schema commits to per-user embedding-model + dim metadata; per-dim partition tables (`node_embeddings_<dim>` + `chunk_embeddings_<dim>`); application-code dispatch on the user's metadata.
- **Pros:** Honors BYOK fully — users bring their own embedding-model choice (Anthropic / Voyage / OpenAI / open-weights local), constrained only by what their key supports. No re-embedding pipeline forced on users who prefer a specific model. Project does not pick winners across the embedding-model market. Adding support for a new dim is a new partition migration; doesn't disrupt existing partitions.
- **Cons:** More upfront schema complexity than a single fixed-dim column. Application-code-side dispatch adds a routing step on every embedding lookup. CI test surface scales with partition count. Multi-tenant query planning may require per-partition statistics tuning at scale (Phase 6+ concern, not Phase 6-entry concern).
- **Rejected because:** not rejected — chosen.

### Single fixed model + dimensionality (e.g., 1024-dim voyage-3)

- **What:** Schema commits to one model + one dim in the first Phase 6 vector migration. BYOK users must use a model that produces that dim, OR run an out-of-band re-embedding pipeline (likely a Python tool that re-embeds graph-node labels into the project's chosen dim using the user's key).
- **Pros:** Simplest schema. Single partition. No per-user dispatch logic. Lowest CI surface. Lowest query-plan complexity. Operational cost minimal at n=1-3 users.
- **Cons:** Constrains user model choice in a regime that explicitly chose BYOK to honor user choice. If a user prefers Stella or BGE for domain-fit reasons (philosophical vocabulary), forcing them to re-embed into a project-chosen model contradicts the BYOK posture. Re-embedding pipeline becomes mandatory infrastructure, not optional; ops cost ends up similar to the model-agnostic shape but with user-facing friction.
- **Rejected because:** the BYOK regime per ADR 0065 commitments 4 + 5 + 8 explicitly chose to let users pick their providers; the schema should not retroactively constrain that choice when the constraint admits a model-agnostic alternative.

### Deferred schema; bootstrap with first-migration-picks-at-Phase-6

- **What:** ADR 0086 commits to no concrete schema shape. The Phase 6 self-correction session that first needs entity resolution picks the model + dim and authors the migration without prior contract.
- **Pros:** Lowest schema-now risk. Pushes the decision into the moment when empirical need surfaces.
- **Cons:** OQ-DEC1-C is explicitly *decide-before-Phase-6*. "Pick at first need" is the absence of a decide-before-Phase-6 settlement. The Phase 6 session that lands the first vector column would face the same single-vs-agnostic question with no prior contract; effectively deferring is re-running this same deliberation at a less convenient moment.
- **Rejected because:** the tension's own decide-before-Phase-6 framing forecloses pure deferral. The ADR may commit to a shape (the partition-by-dim pattern) while leaving concrete dim values for first-migration choice — and that's exactly what the chosen path does.

### JSONB-stored embeddings + application-code similarity search

- **What:** Store embeddings as `jsonb` (or `bytea`) arrays of floats on the existing `nodes` / `chunks` tables; do cosine-similarity search in application code; no pgvector dependency.
- **Pros:** No extension dependency. Single column per consumer. Variable dimensionality natively (the array length isn't constrained by schema). No partition routing.
- **Cons:** No pgvector index acceleration; full-scan similarity at every query. At n=1-3 users this is acceptable, but the operational model doesn't scale and a future migration to pgvector becomes a non-trivial schema change. Loses access to pgvector's HNSW / IVFFlat index options.
- **Rejected because:** the architecture (`infrastructure.md:53`) already committed to pgvector as the substrate; reversing that commitment for variable-dim flexibility ignores that pgvector itself supports variable-dim via partition tables. Choosing the substrate-bypass path because the substrate-native path requires per-dim partitions is bad reasoning when the per-dim partitions are a documented pgvector idiom.

## Consequences

- **Phase 6 entry can proceed against a settled embedding-storage contract.** The first Phase 6 migration that authors entity-resolution infrastructure follows the partition-by-dim pattern. Concrete dim values are picked at first need; the schema shape is fixed.

- **Schema additions when first vector migration lands (Phase 6, not this session):**
  - `users.embedding_model TEXT NOT NULL` + `users.embedding_dims INT NOT NULL` per-user metadata.
  - `CREATE EXTENSION IF NOT EXISTS vector;` at the start of the first migration.
  - `node_embeddings_<dim>(user_id, node_id, embedding vector(<dim>), updated_at TIMESTAMPTZ)` partition table per supported dim.
  - `chunk_embeddings_<dim>(user_id, chunk_id, embedding vector(<dim>), updated_at TIMESTAMPTZ)` partition table per supported dim.
  - Index per partition: `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);` or `ivfflat` per pgvector recommendation for the partition's expected row count.

- **First-exercise readiness note at [`engine/build_readiness/embedding_storage_first_exercise.md`](../../engine/build_readiness/embedding_storage_first_exercise.md)** authored alongside this ADR per [ADR 0053](../../engine/adr/0053-mechanism-first-exercise-gate.md). The note's Tier-1 criteria: (T1-A) first migration authoring a partition table applies cleanly; (T1-B) pgvector extension is available (premise 1 verifies); (T1-C) application-code dispatch on `users.embedding_dims` returns the correct partition for at least two distinct dim configurations.

- **Re-embedding pipeline is a Phase 6+ design concern, not Phase 6-entry concern.** When a user switches embedding models, a Python tool re-embeds their per-user-keyed graph-node and chunk corpus into the new partition. Until the first user switches, the pipeline doesn't need to exist. This deferral is per the [ADR 0014](0014-sonnet-teaches-opus-reviews.md) scale-appropriate-engineering posture ([`infrastructure.md:62`](../docs/infrastructure.md:62)).

- **Cascade:** [`product/docs/architecture.md`](../docs/architecture.md) Entity-Resolution-Service paragraph (lines 216-224) gains a forward-pointer to ADR 0086 for the schema-level commitment. [`product/docs/infrastructure.md:53`](../docs/infrastructure.md:53) pgvector commitment gains a forward-pointer to ADR 0086 for the storage-shape commitment. Done in this commit.

- **`product/docs/tensions.md` OQ-DEC1-C section flips from "Open" to "Resolved by ADR 0086"** in the same commit as this ADR.

- **No supersession.** [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md) (confidence_level + evidentiary_mode on nodes) and ADR 0065 (OSS+BYOK) remain Accepted; this ADR adds new structural commitment without disturbing prior ones.

- **OQ-DEC1-B (two-hop neighborhood retrieval shape) now has the entity-resolution embedding contract it needs.** ADR 0087 (next in this session) can author B's retrieval-shape decision against this concrete substrate.

## See also

- [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — Sonnet teaches, Opus reviews; entity resolution is shared infrastructure across the Sonnet-Opus split.
- [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md) — `confidence_level` and `evidentiary_mode` fields on nodes; node-level metadata that embeddings serve.
- [ADR 0065](0065-oss-pivot-and-byok-disposition.md) — OSS+BYOK; the regime that reshaped this choice from "pick a model" to "pick a storage shape."
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — Extraction step (this ADR exercises it; second of four in this session).
- [`engine/build_readiness/embedding_storage_first_exercise.md`](../../engine/build_readiness/embedding_storage_first_exercise.md) — first-exercise readiness note per ADR 0053.
- [`product/docs/architecture.md`](../docs/architecture.md) "Entity Resolution Service" — shared-infrastructure consumer of this schema.
- [`product/docs/content-strategy.md`](../docs/content-strategy.md) "Storage Economics" — close-reading consumer of this schema.
- [`product/docs/infrastructure.md`](../docs/infrastructure.md) "Cloud Hosting Stack" — pgvector substrate commitment.
- [`product/docs/tensions.md`](../docs/tensions.md) OQ-DEC1-C — resolved by this ADR.
