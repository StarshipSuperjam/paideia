# Seed chunked authoring

> **Placeholder.** Per-session migration workflow for Phase 5 seed-graph build. Fleshed out in Phase 4 alongside `tools/validate.py`'s graph audit (per ADR 0016) and `supabase/migrations/PREDICATE_MANIFEST.md`. Stubbed here so Phase 5 sessions know where to look.

## Purpose (Phase 5)

Each Phase 5 session writes one subdomain's seed migration: a chunked, atomic addition of nodes and edges to the live graph. Sessions run in parallel (epistemology, ethics, metaphysics, etc.) without merge conflicts because each writes a distinct migration file.

## Anticipated workflow (Phase 4 will finalize)

1. Session reads the target subdomain's SEP article structure. Identifies in-scope concepts at the granularity principle (one mastery state per concept).
2. Session writes a new migration file `supabase/migrations/00NN_seed_<subdomain>_partN.sql` with `INSERT` statements. Sets `graph_version_added` to the current settings counter. Sets `confidence_level` per node (`EXTRACTED` | `INTERPRETED` | `SYNTHETIC`).
3. Session runs `supabase db push`.
4. Session runs `tools/validate.py --validate-only` against the post-push DB.
5. Hard-fails (duplicate IDs, dangling edges, prerequisite cycles) fix in-session before commit.
6. Soft-warns (orphan leaves, missing rigor scores, undeclared predicates, etc.) record in `outcome_summary` per category.
7. Session closes per [`session-shutdown-sequence.md`](session-shutdown-sequence.md). Migration file commits with an ENGINE_LOG entry recording the subdomain and node/edge counts.

## What Phase 4 will add

- The actual graph-audit implementation (`validate_graph()` in `tools/validate.py`).
- `supabase/migrations/PREDICATE_MANIFEST.md` populated with the canonical edge-type registry.
- `supabase/migrations/ROUTING.md` populated with numeric prefix scheme and per-session narrative paragraphs.
- Pre-commit hook integration that runs the graph audit (gated on `supabase` connectivity).
- Concrete examples and templates for migration files.

## See also

- `ROADMAP.md` — Phase 4 success criteria, Phase 5 scope.
- ADR 0016 (S-0003) — graph construction needs live validation.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn category reference; Phase 4 categories enumerated there.
