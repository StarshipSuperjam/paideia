# supabase/migrations/ — Routing manifest

> **Placeholder created S-0001. Fleshed out in Phase 4** when graph construction begins. The numeric prefix scheme below is the contract; the per-session narrative section grows one entry per migration file.

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

## Per-session narrative

Each migration file gets one entry below documenting what that session added and why (~200-400 words). This is the long-form audit trail. Future sessions read these to understand the seed graph's history without grep-ing the .sql files.

(Empty until Phase 5. Each Phase 5 subdomain session appends one section here at session close.)

---

### `0001_schema_nodes_edges.sql` — *(Phase 3)*

(Placeholder: fleshed out in Phase 3 when the schema lands.)

---
