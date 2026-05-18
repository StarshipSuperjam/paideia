---
session_id: S-0207
session_type: build
closed_at: "2026-05-18T22:50:00Z"
material_change_class: mixed
module: multi
summary: Tier-A Cluster 1 (contestability substrate) — ADR 0097 + migration 0120 + rollback. Closes ADR 0094 T1-A + ADR 0095 T1-A.
---

# S-0207 — Tier-A Cluster 1 contestability substrate (product ADR 0097 + migration 0120) — 2026-05-18

First Tier-A cluster-implementation ADR per [ADR 0094 product](../../../product/adr/0094-phase-6-scope.md) dependency order C1 → C2 → C4 → C3 → C5. Commits the per-edge atomic contestability substrate per [synthesis.md §Cluster 1](../../build_readiness/pdg_papers_extraction/synthesis.md). Closes ADR 0094 T1-A + ADR 0095 T1-A in-body.

## Added

- **[`product/adr/0097-tier-a-cluster-1-contestability-substrate.md`](../../../product/adr/0097-tier-a-cluster-1-contestability-substrate.md)** — 9 column-level changes to `public.edges`: rename `confidence` → `expert_confidence`; ALTER `provenance` TEXT → JSONB (5-key structure); ADD COLUMN ×7 (trace_confidence, llm_confidence, disagreement_flag, counterexamples JSONB, version, review_status, last_reviewed). Four plan-mode adjudications (symmetric REAL confidence; ALTER+backfill; graph_versions table deferred; DISAGREEMENT_THRESHOLD value deferred). 6 ADR 0084 load-bearing premises (T1-A + T1-B + T2-A + T2-B + T2-C named).
- **[`product/seed-graph/migrations/0120_edges_contestability_substrate.sql`](../../../product/seed-graph/migrations/0120_edges_contestability_substrate.sql)** + paired **[`0120_edges_contestability_substrate_rollback.sql`](../../../product/seed-graph/migrations/0120_edges_contestability_substrate_rollback.sql)** — applied via `mcp__supabase__apply_migration`; round-trip verified end-to-end. Full contract block + Postcondition-Assertions per [ADR 0055](../../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5.
- **[`product/adr/README.md`](../../../product/adr/README.md)** — new "Phase 6 Tier-A cluster-implementation ADRs" section with ADR 0097 entry.
- **[`product/seed-graph/migrations/ROUTING.md`](../../../product/seed-graph/migrations/ROUTING.md)** S-0207 narrative entry — first claim within `0120-0129` Phase 6 self-correction prefix range; forward-flags per-Tier-A-cluster sub-range claims (C1=0120-0129; C2=0130-0139; C4=0140-0149; C3=0150-0159; C5=0160-0169; non-cluster 0170-0199).
- **GitHub Issues:** [#151](https://github.com/StarshipSuperjam/paideia/issues/151) recurring Supabase pooler wedge (priority:urgent; root-cause investigation); [#152](https://github.com/StarshipSuperjam/paideia/issues/152) deferred `validate_edges_contestability_unguarded_high_confidence` validator soft-warn (gates on Cluster 2 retyping).
- **engine_memory drawers:** decisions `14df75b5` (ADR 0097 conversational reasoning); pushback `1d47c76b` (self-pushback on assertion-failure-vs-migration-correctness disambiguation); lesson `fa216b3b` (Postgres ALTER+USING does not auto-cast DEFAULT expression — needs DROP DEFAULT → ALTER TYPE → SET new DEFAULT pattern); diary `1489cc8c`.

## Changed

- **[`product/adr/0094-phase-6-scope.md`](../../../product/adr/0094-phase-6-scope.md)** — T1-A closure marker added in Consequences: closed verified at S-0207 via ADR 0097 landing (Cluster 1 fit in one migration; no scope re-shape).
- **[`product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md`](../../../product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md)** — T1-A closure marker added in Consequences: closed verified at S-0207 (Postgres+JSONB models contestability substrate without shape friction; no Apache AGE escalation).
- **`public.edges` schema (live DB)** — 9 column-level changes per ADR 0097; 533-row count invariant; UNIQUE constraint preserved; RLS policy preserved; `settings.graph_version` unchanged at 16 (pure schema migration).

## Notes

- **End-to-end round-trip verified** (apply → rollback → re-apply): 533 rows preserved at each step; pre-state reviewer-token distribution (526 'ai-seed' + 7 'qa_census_disposition_s_0183'; zero 'human') restored exactly post-rollback; 5-distinct `confidence` value distribution (499×1.0 + 7×0.95 + 15×0.9 + 11×0.85 + 1×0.8 from prior production-audit follow-ups) preserved.
- **DROP DEFAULT lesson:** Postgres ALTER COLUMN TYPE with USING-clause backfill does NOT auto-cast the DEFAULT expression (error 42804) even when USING handles the data. Required split into DROP DEFAULT → ALTER TYPE → SET new DEFAULT for both forward and rollback. Documented in lesson drawer `fa216b3b` + migration discipline reference for Cluster 2+ ADR authors.
- **Issue #151 (Supabase wedge) blocked the pre-commit hook twice** during this session (once at fix-commit, once at migration-files commit); user manually committed with `--no-verify` after Supabase project restart. Issue calls out the recurring nature as needing root-cause work; mitigation candidates enumerated. Validate-history pollution from wedged runs caused `validator_runtime_phase_regression` false-positives — note for next audit.
