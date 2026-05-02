# product/seed-graph/migrations/ — Routing manifest

> Routing manifest for SQL migrations under `product/seed-graph/migrations/`. The directory location was settled in S-0027's gate exercise per [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md); files moved from `supabase/migrations/` in the same commit. Per-session narrative section grows one entry per migration file as Phase 5 seed-authoring sessions land.

## Numeric prefix scheme

Migration files follow `00NN_<purpose>_<scope>.sql` so their natural sort order matches the build order. Ranges:

| Range | Purpose |
|---|---|
| `0001` – `0009` | Schema migrations (nodes, edges, learner_events, mastery_snapshots, tension_log, settings) — Phase 3 |
| `0010` – `0019` | Seed metadata (graph_version=1, ontology metadata) — Phase 4 |
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

(Empty until Phase 5. Each Phase 5 subdomain session appends one section here at session close.)

---

### `0001_schema_nodes_edges.sql` — *(Phase 3)*

(Placeholder: fleshed out in Phase 3 when the schema lands.)

---
