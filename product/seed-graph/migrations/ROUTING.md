# product/seed-graph/migrations/ — Routing manifest

> Routing manifest for SQL migrations under `product/seed-graph/migrations/`. The directory location was settled in S-0027's gate exercise per [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md); files moved from `supabase/migrations/` in the same commit. Per-session narrative section grows one entry per migration file as Phase 5 seed-authoring sessions land.

## Numeric prefix scheme

Migration files follow `00NN_<purpose>_<scope>.sql` so their natural sort order matches the build order. Ranges:

| Range | Purpose |
|---|---|
| `0001` – `0009` | Schema migrations (nodes, edges, learner_events, mastery_snapshots, tension_log, settings) — Phase 3 |
| `0010`          | Seed metadata (graph_version=1, ontology metadata) — Phase 4 (single slot; Phase 4 deliverables are validator + docs and may not author a metadata migration at all) |
| `0011` – `0019` | Seed: epistemology — Phase 5 |
| `0020` – `0029` | Seed: ethics — Phase 5 |
| `0030` – `0039` | Seed: metaphysics — Phase 5 |
| `0040` – `0049` | Seed: philosophy of mind — Phase 5 |
| `0050` – `0059` | Service nodes (logic primitives, mathematical prerequisites, history nodes) — Phase 5 |
| `0060` – `0069` | Cross-domain edges pass — Phase 5 |
| `0070` – `0079` | Phase 6 self-correction schema additions |
| `0080+`         | Reserved for later phases |

**Gaps are acceptable.** A new subdomain claims the next available `00N0` slot rather than re-numbering. Files within a range are committed in numeric order so `supabase db push` applies them deterministically.

**Compound-domain handling.** A concept that spans two subdomains (e.g., a philosophy-of-science concept that's also epistemology) is written into the migration file of the higher-precedence subdomain (per `docs/architecture.md` precedence rules) with `domain[]` carrying both tags. It is NOT split across two migrations.

## graph_version increment contract

The `settings.graph_version` counter is initialized at `1` in the Phase 3 schema migration that creates `settings`. Phase 5 seed-authoring sessions follow this contract:

1. At session boot (after slot claim, before authoring), read the current `settings.graph_version` value.
2. Increment by one in a single transaction at the start of authoring.
3. Every node and edge inserted in this session writes that incremented value to `graph_version_added`.
4. Commit the transaction at session shutdown only if all inserts succeed.

The contract makes `graph_version_added` deterministic per session: a node and an edge from the same Phase 5 session carry the same `graph_version_added`, even if they land in different migration files. Cross-session coordination (two parallel Phase 5 sessions seeding different subdomains) is handled by the eager-claim + atomic-increment combination — each session's increment is its own; concurrent runs produce monotonic values.

Phase 6 self-correction sessions follow the same contract for any nodes/edges they author. Phase 3 schema migrations do not increment the counter; they initialize it at `1` and stop.

Rationale settled in S-0027 build-readiness exercise per T2-D in [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md).

## Per-session narrative

Each migration file gets one entry below documenting what that session added and why (~200-400 words). This is the long-form audit trail. Future sessions read these to understand the seed graph's history without grep-ing the .sql files.

---

### S-0028 — Phase 3 schema lands (`0001` through `0008`)

S-0028 deployed the Phase 3 schema to `paideia-dev` (PostgreSQL 17.6) via eight migrations under [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md)'s contract. The build session inherited a fully-resolved Tier 1 decision set from S-0027's gate exercise; substantive design questions were answered in advance (auth model, RLS posture, JSONB vocabularies, expression contract, gate protocol). S-0028's role was implementation under the universal expression contract per [ADR 0039](../../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md).

**`0001_users_mirror.sql`** — `public.users` mirror table (UUID id, email, created_at) plus `handle_new_auth_user` and `handle_deleted_auth_user` trigger functions on `auth.users`. Both INSERT and DELETE triggers required for ADR 0031's cascade discipline; the gate report T1-A originally specified INSERT only, an under-specification S-0028 corrected. RLS enabled with self-select-only policy.

**`0002_nodes.sql`** — `public.nodes` per architecture.md "Node Schema". `id TEXT PRIMARY KEY` (slugified human-readable concept names). CHECK constraints on `confidence_level` (per ADR 0030) and `status` (3-value enum per gate T2-A). RLS with read-allowed-to-authenticated.

**`0003_edges.sql`** — `public.edges` with `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `source_id`/`target_id TEXT REFERENCES public.nodes(id)`, `edge_type TEXT` (intentionally unconstrained per architecture.md:182), `UNIQUE (source_id, target_id, edge_type)`. Weight and confidence CHECKed [0,1].

**`0004_settings.sql`** — singleton key/value store; seeded with `('graph_version', 1::JSONB)` per gate T2-D. Service-role-only RLS.

**`0005_learner_events.sql`** — event-sourced log per ADR 0015. FK `user_id UUID REFERENCES public.users(id) ON DELETE CASCADE` per ADR 0031. Sub-signals stored raw (`generative_ratio`, `scaffolding_distance`, `novelty`) per ADR 0024. Structured context columns (`path_id`, `source_text_id`, `session_id`) per ADR 0026 + ADR 0031 (no `cohort_id`). Table-level CHECK `sub_signals_range_or_null` per gate T2-B.

**`0006_mastery_snapshots.sql`** — cached mastery state per ADR 0023/0024/0025. Composite PK `(user_id, concept_id)`, `max_historical_score DEFAULT 0`. Two indexes per gate T2-C. RLS with `user_id = auth.uid()` policy.

**`0007_tension_log.sql`** — per self-correction.md + ADR 0026. IMMUTABLE function `tension_log_exchange_summary_valid_v1` enforces v1 vocabularies from [TENSION_VOCABULARY.md](TENSION_VOCABULARY.md). `user_id` added per ADR 0031 Consequences (self-correction.md schema omits the column; cascade discipline mandates it).

**`0008_security_hardening.sql`** — addresses three Supabase advisor findings against S-0028's authored functions: pin search_path on `tension_log_exchange_summary_valid_v1`; `REVOKE EXECUTE` on the two trigger functions from PUBLIC, anon, authenticated. Triggers continue firing through the trigger system; only the PostgREST RPC surface is closed.

**Gate-report corrections recorded inline in `phase_3_sql.md`.** The build session corrected three gate-report drifts from canonical design docs: nodes.id type (T2-C/T2-E declared `concept_id UUID` / `source_id UUID`; architecture.md is `nodes.id TEXT`), `type` vs `edge_type` (architecture.md uses `edge_type`), and edge `provenance`/`evidence` JSONB-vs-TEXT (architecture.md is TEXT for both). Corrections preserve the gate's halting discipline by keeping the report aligned with implemented schema.

**Verification.** `validate.py --sql-gates` clean per migration (4 gates, 0 hard-fails on each); pre-commit gate stack clean across all build commits; live-schema verification via Supabase MCP `list_tables` + `execute_sql` confirms 7 tables, 7 RLS policies, 3 cascade-on-user FKs, and CHECK constraint shapes match design. Post-apply security advisor returned only the Supabase-internal `rls_auto_enable` finding (out of project scope). Branch-based rollback verification per gate T2-H was downgraded to "migrations applied cleanly the first time" because Supabase development branches are cost-bearing and S-0028's auto-mode posture defers cost-bearing operations to explicit user confirmation. Forward-pointer recorded in `outcome_summary` for the next gate exercise (likely Phase 4 / S-0029 — local Supabase CLI setup or branch-based verification).

---

### S-0037 — Phase 4 graph validation lands (no migration authored)

S-0037 implemented the Phase 4 graph validation utility per [ADR 0016](../../../engine/adr/0016-graph-construction-needs-live-validation.md) under the build-readiness gate at [`engine/build_readiness/phase_4_graph_validation.md`](../../../engine/build_readiness/phase_4_graph_validation.md). The session authored no migration file: Phase 4 deliverables are the validator extension plus three docs (this routing manifest, [`PREDICATE_MANIFEST.md`](PREDICATE_MANIFEST.md), [`engine/operations/seed-chunked-authoring.md`](../../../engine/operations/seed-chunked-authoring.md)). The `0010` slot reserved for Phase 4 metadata remains unused; Phase 5 epistemology authoring claims `0011` first.

**Range-collision fix.** The prior table assigned `0010-0019` to Phase 4 metadata and `0011-0019` to Phase 5 epistemology — overlapping ranges. Per gate T2-H, the table is amended to reserve `0010` (single slot) for Phase 4 metadata; `0011-0019` is now unambiguously Phase 5 epistemology. Phase 4's deliverables author no SQL, so the slot may remain permanently unused; reserving it preserves the placement option without committing Phase 4 to any specific metadata migration.

**graph_version increment contract holds.** No node or edge inserts happened this session; the counter remains at `1` until the first Phase 5 seed-authoring session opens. Per the S-0027 settlement (gate T2-D), the contract is unchanged: read counter at session boot, increment in a single transaction, all inserts in the session write that incremented value, commit at shutdown only if all inserts succeed.

**Validator scope.** `validate.py --validate-only` (the default invocation) runs the audit when `SUPABASE_DB_URL` is set in the environment. When unset (most non-seed-authoring commits), the audit records `graph_audit_skipped` and does not query the DB — non-seed-authoring sessions are not gated on connectivity. The service-role pooler URL is required (gate T1-C); service-role bypasses RLS so the audit observes ground truth distinct from anon-filtered views. `--export-snapshot path/to/file.json` writes a full nodes-and-edges JSON dump for offline review.

**Validator categories.** Three hard-fails per ADR 0016: duplicate node IDs, dangling edge references (defense-in-depth — the schema FK constraint prevents inserts but the audit covers any post-restore window before constraints are validated), and prerequisite cycles via Kosaraju SCC restricted to the `pedagogical_prerequisite` subgraph. Seven soft-warn categories per gate T2-D: `undeclared_predicate`, `attribute_shape_inconsistency`, `missing_rigor_score`, `render_readiness_violation`, `synthetic_review_queue`, `orphan_leaf`, `suspicious_cross_domain_ratio`. All seven categories register in `checks_run` even when zero findings fire so cross-session telemetry distinguishes "category clean" from "category did not run."

**Forward-pointer status (gate T3-A reaffirmation).** Branch-based rollback verification remains deferred to Phase 5+ pending Supabase CLI setup or explicit user budget approval for development branches. `validate_graph()` itself is read-only and does not mutate the database, so the rollback question is orthogonal to the validator's correctness; the next gate session for Phase 5 epistemology inherits the open question.

---
