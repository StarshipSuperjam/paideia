-- Migration: 0130_edges_three_relation_layering
-- Purpose: Tier-A Cluster 2 — Edge-type taxonomy expansion + three-
--   relation layered separation per
--   product/adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md.
--   Second Tier-A cluster-implementation migration per
--   product/adr/0094-phase-6-scope.md dependency order
--   C1 → C2 → C4 → C3 → C5. Lands the structural separation of
--   pedagogical_dependence / conceptual_relatedness / historical_influence
--   layers plus the per-layer controlled-vocabulary edge_type that
--   synthesis.md §Cluster 2 prescribes (paper_2:L80-81 "edge type as
--   enum, not free text"). Retypes the 533 existing rows: 516
--   pedagogical_prerequisite → soft_prerequisite under pedagogical_
--   dependence; 17 historical_influence → influenced_by under
--   historical_influence. The 533-row count is invariant — this is
--   schema + retyping; no INSERT/DELETE of edge rows. Adds 1 new
--   column (edge_layer) and 2 new CHECK constraints. Re-verifies
--   ADR 0094 T1-A + ADR 0095 T1-A at landing.
-- Loads tables: public.edges (1 ADD COLUMN + 1 backfill UPDATE + 1
--   SET NOT NULL + 1 ADD CONSTRAINT for edge_layer validity + 2
--   retyping UPDATEs on edge_type + 1 ADD CONSTRAINT for
--   (edge_layer, edge_type) coupling; no INSERT/DELETE).
-- Preconditions:
--   * Phase 3 schema + Cluster 1 schema in place: public.edges exists
--     with the columns from 0003_edges.sql + the 9 columns added /
--     renamed by 0120_edges_contestability_substrate.sql.
--   * public.edges carries exactly 533 rows total: 516 with
--     edge_type = 'pedagogical_prerequisite' + 17 with edge_type =
--     'historical_influence' (verified via mcp__supabase__execute_sql
--     at S-0208 boot — see ADR 0098 Decision).
--   * No prior migrations in the 0130-0139 prefix range — this is the
--     first claim within the Cluster 2 sub-range (per ROUTING.md S-0207
--     narrative entry's forward-flagged sub-range scheme).
--   * settings.graph_version = 16 at session boot (post-S-0123;
--     unchanged by this migration because no node/edge rows are inserted).
-- Postconditions:
--   * public.edges gains column edge_layer TEXT NOT NULL with
--     CHECK (edge_layer IN ('pedagogical_dependence',
--     'conceptual_relatedness', 'historical_influence')).
--   * The 516 rows with prior edge_type = 'pedagogical_prerequisite'
--     carry edge_layer = 'pedagogical_dependence' + edge_type =
--     'soft_prerequisite' post-migration.
--   * The 17 rows with prior edge_type = 'historical_influence' carry
--     edge_layer = 'historical_influence' + edge_type = 'influenced_by'
--     post-migration.
--   * No row carries edge_layer = 'conceptual_relatedness' at landing
--     (Cluster 5 misconception sub-graph is the natural first author).
--   * No row carries the prior edge_type values 'pedagogical_prerequisite'
--     or 'historical_influence' post-migration.
--   * public.edges gains CHECK constraint edges_edge_layer_type_coupling
--     enforcing the 16 valid (edge_layer, edge_type) pairs per ADR 0098.
--   * public.edges row count = 533 (invariant — pure schema + retyping).
--   * UNIQUE(source_id, target_id, edge_type) preserved (retyping
--     changes the third column's value but no two edges share a
--     (source, target, retyped_edge_type) triple — verified by
--     Postcondition-Assertions below).
--   * RLS policy edges_authenticated_read preserved.
--   * All other columns from 0003_edges.sql + 0120 unchanged:
--     id, source_id, target_id, weight, evidence, graph_version_added,
--     created_at, updated_at, expert_confidence, trace_confidence,
--     llm_confidence, disagreement_flag, counterexamples, version,
--     review_status, last_reviewed, provenance.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. Verifies (a) schema shape — edge_layer
--   column + 2 new CHECK constraints exist as expected; (b) row-count
--   invariance — 533 unchanged; (c) backfill correctness — 516 +
--   17 split into the right layers; (d) retyping correctness — no
--   prior edge_type values remain; (e) UNIQUE preservation — count
--   of unique (source_id, target_id, edge_type) tuples equals row count.)
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'edge_layer' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'edges' AND constraint_name = 'edges_edge_layer_valid' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'edges' AND constraint_name = 'edges_edge_layer_type_coupling' :: 1
--   SELECT count(*)::int FROM public.edges :: 533
--   SELECT count(*)::int FROM public.edges WHERE edge_layer = 'pedagogical_dependence' :: 516
--   SELECT count(*)::int FROM public.edges WHERE edge_layer = 'historical_influence' :: 17
--   SELECT count(*)::int FROM public.edges WHERE edge_layer = 'conceptual_relatedness' :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_layer IS NULL :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'soft_prerequisite' :: 516
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'influenced_by' :: 17
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 0
--   SELECT count(DISTINCT (source_id, target_id, edge_type))::int FROM public.edges :: 533
-- Invariants:
--   * Row count on public.edges is preserved (533 before; 533 after).
--     Pure schema + retyping — no INSERT/DELETE of edges.
--   * UNIQUE(source_id, target_id, edge_type) constraint is preserved.
--     The retyping changes edge_type's value uniformly within each
--     prior class (all 516 'pedagogical_prerequisite' → 'soft_prerequisite';
--     all 17 'historical_influence' → 'influenced_by'); no two edges
--     in the same prior class share (source, target), so the uniform
--     retyping cannot collapse two rows into a colliding (source, target,
--     edge_type) triple. Verified by Postcondition-Assertion that
--     count(DISTINCT (source_id, target_id, edge_type)) = row count.
--   * RLS policy edges_authenticated_read preserved.
--   * Contestability columns from 0120 (expert_confidence,
--     trace_confidence, llm_confidence, disagreement_flag,
--     counterexamples, version, review_status, last_reviewed,
--     provenance) and their constraints are layer-orthogonal to
--     Cluster 2's changes and persist unchanged. Notably,
--     review_status = 'provisional' default on all 533 rows is the
--     coordination point with Cluster 7 SQA validation: the retyped
--     soft_prerequisites stay at provisional until SQA evidence
--     supports upgrade to approved + (optionally) hard_prerequisite.
-- Non-responsibilities:
--   * Does not touch the public.nodes table. Per the S-0208 in-session
--     adjudication on synthesis line 84 ("L1.10 partial coverage"),
--     Cluster 4 (node schema redesign per synthesis §Cluster 4 lines
--     141-176) owns the node-type taxonomy. ADR 0094 dependency order
--     C2 → C4 preserves the scope boundary.
--   * Does not implement the edge_cross_layer_default_routing validator
--     soft-warn (synthesis line 94). Committed as a forward pointer in
--     ADR 0098 Consequences; implementation lands when the Phase 7+
--     routing layer ships (the warn fires on teaching-layer queries
--     that bypass explicit layer-filter; no teaching layer yet).
--   * Does not back-fill or upgrade any retyped soft_prerequisite edges
--     to hard_prerequisite. Per ADR 0098 premise 2 + synthesis line
--     101 + adversarial_review.md E.2.1, hard_prerequisite upgrades
--     require SQA-validated learner-trace evidence which Cluster 7
--     (SQA predictive-validity pipeline) is the natural author of.
--   * Does not implement the (separate) validator soft-warn
--     edge_provisional_hard_prerequisite. ADR 0098 commits it as a
--     same-session deliverable; implementation lands in
--     engine/tools/validate.py alongside the Issue #152
--     edge_contestability_unguarded_high_confidence soft-warn (both
--     consume the contestability schema 0120 committed).
--   * Does not advance settings.graph_version (no node/edge rows
--     inserted; pure schema + retyping does not advance the counter
--     per the ROUTING.md graph_version increment contract).
-- Cross-cutting decisions:
--   * Compound CHECK constraint on (edge_layer, edge_type) per ADR 0098
--     Decision + Alternatives Considered §1 — chosen over Postgres
--     ENUM types and over a lookup table because extension is ALTER
--     TABLE DROP/ADD CONSTRAINT (no ALTER TYPE migration complexity
--     and no JOIN-per-edge-read cost). The constraint body lists 16
--     valid pairs grouped by layer for readability.
--   * Backfill via deterministic CASE on prior edge_type — no row
--     gets NULL edge_layer because the precondition asserts exactly
--     two prior edge_type values exist on the 533 rows. The
--     subsequent SET NOT NULL acts as a structural verifier (would
--     fail if any row remained NULL).
--   * Retype 516 → 'soft_prerequisite' (NOT 'hard_prerequisite') per
--     ADR 0098 premise 2 + synthesis line 101 epistemic-conservatism
--     framing. Retype 17 → 'influenced_by' per ADR 0098 premise 3 +
--     synthesis line 98 default.
--   * Two CHECK constraints land in sequence (layer-validity first;
--     coupling second) so that any unexpected pre-state row would
--     surface at the SET NOT NULL step (NULL violation) or the
--     coupling-CHECK ADD step (invalid pair) — distinct failure
--     modes for distinct precondition assumptions.
--   * No CASCADE discipline change. Edges carry no learner-state FK
--     to users per ADR 0031; edge_layer is a simple TEXT column.
--   * RLS posture unchanged. Edges read by authenticated users; writes
--     service-role-only. The new column does not need its own RLS rule.
-- Rollback: 0130_edges_three_relation_layering_rollback.sql in the
--   same prefix slot. Reverses all changes: DROP the coupling CHECK;
--   UPDATE edge_type back ('soft_prerequisite' → 'pedagogical_
--   prerequisite'; 'influenced_by' → 'historical_influence'); DROP
--   COLUMN edge_layer (which also drops the layer-validity CHECK).
--   End-to-end round-trip verified at S-0208 close per migration-
--   discipline.md "Rollback authorship" — apply 0130; capture \d+
--   public.edges; apply rollback; re-apply 0130; diff post-re-apply
--   \d+ output against first capture for stability.
-- See also: product/adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md,
--   product/adr/0094-phase-6-scope.md (T1-A re-verified here),
--   product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md (T1-A re-verified here),
--   product/adr/0097-tier-a-cluster-1-contestability-substrate.md (review_status='provisional' coordination),
--   product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md (the 17 historical edges this retypes),
--   engine/build_readiness/pdg_papers_extraction/synthesis.md §Cluster 2 (lines 80-110),
--   engine/build_readiness/pdg_papers_extraction/adversarial_review.md E.11.1 (Cluster 1 ↔ Cluster 2 coordination),
--   engine/operations/migration-discipline.md,
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md (Layer 2.5 grammar),
--   product/seed-graph/migrations/0003_edges.sql (pre-state schema),
--   product/seed-graph/migrations/0120_edges_contestability_substrate.sql (Cluster 1 substrate this builds on top of),
--   product/seed-graph/migrations/ROUTING.md S-0208 narrative entry.

BEGIN;

-- 1. ADD COLUMN edge_layer (nullable for backfill). The NOT NULL +
--    CHECK constraints land after the backfill below; introducing
--    them inline would require a DEFAULT that backfills uniformly,
--    which destroys the per-row layer-from-prior-edge_type semantic
--    this migration commits.
ALTER TABLE public.edges ADD COLUMN edge_layer TEXT;

-- 2. Backfill edge_layer from prior edge_type values via deterministic
--    CASE. The precondition asserts exactly two prior values exist on
--    the 533 rows; any row that doesn't match either case will fail
--    the subsequent SET NOT NULL (and surface in Postcondition-
--    Assertions as a non-zero NULL count).
UPDATE public.edges
   SET edge_layer = CASE
     WHEN edge_type = 'pedagogical_prerequisite' THEN 'pedagogical_dependence'
     WHEN edge_type = 'historical_influence' THEN 'historical_influence'
   END;

-- 3. Tighten edge_layer to NOT NULL. Acts as a structural verifier
--    of step 2's backfill completeness — a NULL row here would raise
--    23502 NOT NULL violation and abort the transaction.
ALTER TABLE public.edges ALTER COLUMN edge_layer SET NOT NULL;

-- 4. ADD CONSTRAINT edges_edge_layer_valid — enforces the 3 valid
--    edge_layer values. Lands before the retyping UPDATEs so any
--    invalid edge_layer (e.g., from a manual UPDATE between this
--    migration's BEGIN and step 4) surfaces immediately.
ALTER TABLE public.edges
  ADD CONSTRAINT edges_edge_layer_valid
  CHECK (edge_layer IN (
    'pedagogical_dependence',
    'conceptual_relatedness',
    'historical_influence'
  ));

-- 5. Retype the 516 pedagogical_prerequisite edges to soft_prerequisite
--    per ADR 0098 premise 2 + synthesis line 101 (experts overstate
--    necessity; soft is the epistemically conservative default).
UPDATE public.edges
   SET edge_type = 'soft_prerequisite'
 WHERE edge_type = 'pedagogical_prerequisite';

-- 6. Retype the 17 historical_influence edges to influenced_by per
--    ADR 0098 premise 3 + synthesis line 98 (influenced_by is the
--    most general of the three historical sub-types; matches the
--    framing of all 17 existing edges per ADR 0061 deliberation).
UPDATE public.edges
   SET edge_type = 'influenced_by'
 WHERE edge_type = 'historical_influence';

-- 7. ADD CONSTRAINT edges_edge_layer_type_coupling — couples
--    (edge_layer, edge_type) to the 16-pair vocabulary per ADR 0098
--    Decision. Grouped by layer for readability (mirrors synthesis.md
--    §Cluster 2 lines 96-99 structure). Per ADR 0098 premise 4,
--    extending the vocabulary is an ALTER TABLE DROP/ADD CONSTRAINT
--    on this named constraint (no ALTER TYPE complexity).
ALTER TABLE public.edges
  ADD CONSTRAINT edges_edge_layer_type_coupling
  CHECK (
    (edge_layer = 'pedagogical_dependence' AND edge_type IN (
      'hard_prerequisite',
      'soft_prerequisite',
      'helpful_bridge',
      'co_requisite',
      'contrastive_link',
      'misconception_remediation',
      'example_of',
      'supports',
      'assessed_before',
      'unlearning_required_before'
    ))
    OR
    (edge_layer = 'conceptual_relatedness' AND edge_type IN (
      'affinity_with',
      'contrasts_with',
      'same_problem_family'
    ))
    OR
    (edge_layer = 'historical_influence' AND edge_type IN (
      'influenced_by',
      'received_via',
      'reacted_against'
    ))
  );

COMMIT;
