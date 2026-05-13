# Model-agnostic embedding storage — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. [ADR 0086](../../product/adr/0086-model-agnostic-embedding-storage-architecture.md) (S-0152) introduces the per-dim-partition storage architecture for entity-resolution and close-reading embeddings. The schema-level contract is settled in this session; the first natural exercise is the first Phase 6 self-correction migration that authors `CREATE EXTENSION vector` + `node_embeddings_<dim>` + `chunk_embeddings_<dim>` partition tables.
>
> Criterion-4 evaluation (consequences span ≥3 ops docs OR ≥5 tooling files): satisfied via 1 ADR (0086) + ≥3 migrations (initial extension + partition + index creation) + 2 product docs forward-pointer updates (architecture.md + infrastructure.md) + 1 schema-extension on `users` + this readiness note + Phase 6 application-code dispatch layer = ≥10 surfaces total when the first natural exercise lands. Readiness note required.

## What this mechanism does

ADR 0086 commits to **model-agnostic embedding storage**:

- Per-user embedding-model metadata on the `users` table (`embedding_model TEXT NOT NULL` + `embedding_dims INT NOT NULL`).
- Per-dimensionality partition tables: `node_embeddings_<dim>(user_id, node_id, embedding vector(<dim>), updated_at TIMESTAMPTZ)` for entity-resolution graph-node embeddings; `chunk_embeddings_<dim>(user_id, chunk_id, embedding vector(<dim>), updated_at TIMESTAMPTZ)` for close-reading text-chunk embeddings.
- Application-code routes each query to the correct partition by reading the user's `embedding_dims` metadata.
- Adding a new dim is a new partition migration; does not disturb existing partitions.

## Tier 1 — close at first natural exercise (Phase 6 entry)

- **T1-A — first Phase 6 migration authoring a partition table applies cleanly.** The migration:
  1. Creates `CREATE EXTENSION IF NOT EXISTS vector;` at the start.
  2. Adds `users.embedding_model TEXT NOT NULL` + `users.embedding_dims INT NOT NULL` (with safe-default handling for the existing 0-row `users` table at Phase 6 entry).
  3. Authors `node_embeddings_<dim>(user_id, node_id, embedding vector(<dim>), updated_at TIMESTAMPTZ)` for the dim the migration picks.
  4. Creates `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);` (or `ivfflat` per the partition's expected row count).
  5. Applies via `engine/tools/apply_migration.py` per [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) with exit code 0 and `schema_migrations` recorded.
- **T1-B — pgvector extension is available.** Verified via the migration's `CREATE EXTENSION IF NOT EXISTS vector;` succeeding. This closes premise 1 of ADR 0086's load-bearing-premises subsection (which was named as "untestable in-context at S-0152" because Claude Code's auto-mode classifier denied the read-only MCP `list_extensions` query per ADR 0055's "Production Reads" gate). Falsifier signal: migration fails with `ERROR: extension "vector" is not available` or `ERROR: type "vector" does not exist`. If the falsifier fires, escalate to user immediately — pgvector availability is foundational to ADR 0086's chosen path.
- **T1-C — application-code dispatch on `users.embedding_dims` returns the correct partition for two distinct dim configurations.** The first Phase 6 session that touches the entity-resolution service code authors a small dispatch helper (likely `engine/tools/embedding_partition.py` or `paideia/entity_resolution/partition.py`). The helper is tested against synthetic users with `embedding_dims=1024` and `embedding_dims=1536` (one user per dim); each query routes correctly without cross-partition leakage.

## Tier 2 — close at subsequent natural occasions

- **First multi-dim coexistence empirically observed.** Two distinct user records with two distinct embedding_dims values, each with non-empty partition rows. Verifies the partition-by-dim isolation works under real load. Captured in the session's `outcome_summary` field.
- **First re-embedding workflow execution.** A user switches embedding models (e.g., changes their key from Anthropic to Voyage). A `engine/tools/reembed_user.py` (or similar) tool re-embeds the user's per-node and per-chunk corpus into the new partition. Validates the "re-embedding pipeline is feasible as a separate concern, not blocking" premise from ADR 0086.
- **First query-plan check on combined entity-resolution + close-reading scans.** Premise 4 of ADR 0086 named the risk: close-reading's large-volume chunk scans could dominate planner statistics on a shared partition, degrading entity-resolution's low-latency point lookups. Verify via `EXPLAIN ANALYZE` on a combined workload; if the planner pathology surfaces, the response is to split chunk and node partitions (each gets its own per-dim table family, breaking the implicit "they share the partition scheme" assumption). Recorded in the Empirical record subsection.
- **First HNSW vs IVFFlat index choice with empirical rationale.** The first partition migration picks one or the other. Capture the row-count expectation + measured query latency + index build cost. Subsequent partitions consult the recorded rationale rather than re-deriving from pgvector documentation.

## Tier 3 — defer indefinitely (recorded for future audit)

- **Partition-count-driven CI surface.** As partitions multiply (one per supported dim), the CI test surface grows linearly. Auditable at `≥5 distinct dim partitions` — if CI flake rate or build time become a concern, consider a parameterized partition test pattern (one test, N parameterized values).
- **Per-partition statistics tuning.** Postgres' query planner may need per-partition `ALTER TABLE ... SET (autovacuum_analyze_scale_factor = ...)` once any partition exceeds 100K rows. Re-audit when the first partition crosses 50K rows.
- **JSON-stored fallback for exotic dim values.** If a future BYOK user brings a model with an unusual dim (e.g., 384, 768, 2048, 4096), the project commits to a new partition migration — but if the dim is one-off and unlikely to be shared, the user could opt into a JSONB fallback column on the existing `nodes` / `chunks` tables. Defer until a one-off-dim user appears.

## Empirical record (pending)

*Closes when the first Phase 6 migration lands the partition tables.*

This readiness note will be updated with:
- The migration SHA + the dim values chosen.
- The first-natural-exercise empirical signal for T1-A, T1-B, T1-C.
- Any falsifier signal that surfaces and how the session responded.
