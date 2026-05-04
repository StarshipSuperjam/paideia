# Session plan — S-0050 routine — P5-01a Epistemology core seed

paths_to_modify: ["product/seed-graph/migrations/0011_seed_epistemology_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

## Rationale

Task P5-01a from `engine/session/auto_target.json` (T-PHASE-5). Phase 5 first
routine-mode session against the executable contract authored at S-0045 per
[ADR 0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md).
P5-01a has no dependencies; it is the calibration anchor for every other Phase 5
subject subdomain task per [phase_5.md](../build_readiness/phase_5.md) T1-D.

**Scope of P5-01a per phase_5.md T1-B.** Foundational epistemology concepts:
knowledge, justification, belief, certainty, the analysis-of-knowledge tradition.
Excludes specialized epistemology (social, virtue, formal, skepticism varieties)
which P5-01b owns. The core/specialized split was settled at S-0045.

**Authoring approach.** A single migration file in the `0011-0015` sub-range
(`0011_seed_epistemology_part1.sql`). Concept count target ~25-30 nodes per the
seed-chunked-authoring.md worked example for an epistemology session. Edges are
within-domain `pedagogical_prerequisite` only — cross-domain edges are P5-11's
exclusive responsibility per phase_5.md T2-G #1 (cross-domain edge collisions).
Confidence_level composition targets `INTERPRETED >= 70%` floor with the small
remainder distributed between `EXTRACTED` (rare; only where SEP entry titles
directly map a concept name 1:1) and `SYNTHETIC` (`<= 20%` ceiling, used for
concepts where the authoring infers structure SEP doesn't itself name).

**Predicate registry.** Only `pedagogical_prerequisite` is used in this
migration; PREDICATE_MANIFEST.md needs no edit. The reserved
`cross_domain_dependency` predicate decision is deferred to P5-11 per T1-E /
T3-B and is not consumed by within-domain core authoring.

**ROUTING.md.** Per-session narrative entry appended (~200-400 words) describing
what S-0050 added and why, per ROUTING.md "Per-session narrative" discipline.

## Criteria mapping

- **Criterion 0** (`migration_applied: 0011_seed_epistemology_part1`) — addressed
  by authoring `0011_seed_epistemology_part1.sql` and applying via the live
  Supabase paideia-dev DB. The migration file lands in
  `product/seed-graph/migrations/0011_seed_epistemology_part1.sql`; the
  `apply_migration` MCP call marks it in `supabase_migrations.schema_migrations`.
- **Criterion 1** (`validate_passes`) — addressed by running
  `python3 engine/tools/validate.py --validate-only` after migration apply.
  Hard-fails (duplicate IDs, dangling references, prereq cycles) must be zero;
  soft-warns recorded in `outcome_summary_soft_warns` at session shutdown per
  [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md).

## Out-of-scope (forward-pointers)

- Cross-domain edges (e.g., epistemology → philosophy of science): P5-11.
- Specialized epistemology concepts (social, virtue, formal, skepticism
  varieties beyond cartesian skepticism): P5-01b.
- `cross_domain_dependency` predicate formal introduction: P5-11 per T1-E.
- Branch-based rollback verification: T3-A inherited; not engaged this session.

## See also

- [`engine/build_readiness/phase_5.md`](../build_readiness/phase_5.md) — gate
  report (Tier 1/2/3 settled at S-0045).
- [`engine/operations/seed-chunked-authoring.md`](../operations/seed-chunked-authoring.md)
  — Layer 1 per-session workflow.
- [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md)
  — contract-block shape.
- [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md)
  — numeric prefix scheme + graph_version contract.
- [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)
  — canonical edge-type registry.
- ADR 0052 — Phase 5 9-subdomain decomposition.
