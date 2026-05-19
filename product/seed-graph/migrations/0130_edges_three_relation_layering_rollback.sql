-- Migration: 0130_edges_three_relation_layering_rollback
-- Purpose: Paired rollback for 0130_edges_three_relation_layering.sql
--   per engine/operations/migration-discipline.md "Rollback authorship".
--   Reverses all schema + retyping changes that 0130 introduced.
--   End-to-end round-trip verification at S-0208 close: apply 0130;
--   capture \d+ public.edges; apply this rollback; re-apply 0130;
--   diff post-re-apply \d+ output against first capture for stability.
-- Loads tables: public.edges (1 DROP CONSTRAINT for the coupling
--   CHECK + 2 retyping UPDATEs on edge_type back to prior values +
--   1 DROP COLUMN for edge_layer which also drops the layer-validity
--   CHECK constraint).
-- Preconditions:
--   * 0130 has been applied — public.edges carries edge_layer NOT NULL
--     with the layer-validity CHECK + the coupling CHECK.
--   * The 516 + 17 = 533 rows are in their post-0130 retyped state
--     (edge_type IN ('soft_prerequisite', 'influenced_by') only).
--   * No new edges have been INSERTed with edge_type values from the
--     other 14 vocab entries (e.g., 'helpful_bridge', 'affinity_with',
--     'reacted_against'). If they have, this rollback's reverse
--     UPDATE step would leave those edges in an unconstrained state
--     (the coupling CHECK is dropped before the column is dropped,
--     so they survive); the prior column-state (free-text edge_type)
--     accepts any value, so this is not a data-integrity violation
--     but a semantic drift the rollback itself cannot remediate. In
--     practice the rollback is exercised within the same session as
--     0130's apply, so this case is structurally impossible.
-- Postconditions:
--   * public.edges loses column edge_layer (and its CHECK constraint
--     edges_edge_layer_valid which was attached to the column).
--   * public.edges loses CHECK constraint edges_edge_layer_type_coupling.
--   * The 516 rows previously retyped to 'soft_prerequisite' carry
--     edge_type = 'pedagogical_prerequisite' post-rollback.
--   * The 17 rows previously retyped to 'influenced_by' carry
--     edge_type = 'historical_influence' post-rollback.
--   * public.edges row count = 533 (invariant).
--   * UNIQUE(source_id, target_id, edge_type) preserved.
--   * RLS policy edges_authenticated_read preserved.
--   * Cluster 1's contestability columns (expert_confidence, etc.)
--     unchanged — rollback is layer-orthogonal to those.
-- Postcondition-Assertions:
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'edge_layer' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'edges' AND constraint_name = 'edges_edge_layer_valid' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'edges' AND constraint_name = 'edges_edge_layer_type_coupling' :: 0
--   SELECT count(*)::int FROM public.edges :: 533
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 516
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'soft_prerequisite' :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'influenced_by' :: 0
--   SELECT count(DISTINCT (source_id, target_id, edge_type))::int FROM public.edges :: 533
-- Invariants:
--   * Row count preserved (533).
--   * UNIQUE preserved.
--   * RLS preserved.
--   * Cluster 1's columns + constraints (from 0120) untouched.
-- Non-responsibilities:
--   * Does not rollback Cluster 1's contestability substrate (that's
--     0120_edges_contestability_substrate_rollback.sql).
--   * Does not advance settings.graph_version.
--   * Does not handle edges INSERTed with non-prior edge_type values
--     between 0130 apply and this rollback (see Preconditions caveat).
-- Cross-cutting decisions:
--   * Drop coupling CHECK before retyping UPDATEs so the retyping
--     to 'pedagogical_prerequisite' / 'historical_influence' (which
--     are NOT in the 16-pair vocabulary) does not violate the
--     constraint.
--   * Drop edge_layer column LAST so the layer-validity CHECK
--     attached to it is dropped via the cascade (Postgres DROP COLUMN
--     auto-drops column-level CHECK constraints).
--   * No transaction nesting concern — the BEGIN/COMMIT wraps all
--     four statements atomically; partial rollback would surface as
--     a transaction-level abort.
-- Rollback (of this rollback): re-apply 0130_edges_three_relation_layering.sql.
-- See also: product/seed-graph/migrations/0130_edges_three_relation_layering.sql,
--   engine/operations/migration-discipline.md "Rollback authorship".

BEGIN;

-- 1. DROP the (edge_layer, edge_type) coupling CHECK so the
--    subsequent retyping UPDATEs (to values NOT in the 16-pair
--    vocabulary) do not violate the constraint.
ALTER TABLE public.edges DROP CONSTRAINT edges_edge_layer_type_coupling;

-- 2. Retype the 516 soft_prerequisites back to pedagogical_prerequisite.
UPDATE public.edges
   SET edge_type = 'pedagogical_prerequisite'
 WHERE edge_type = 'soft_prerequisite';

-- 3. Retype the 17 influenced_by edges back to historical_influence.
UPDATE public.edges
   SET edge_type = 'historical_influence'
 WHERE edge_type = 'influenced_by';

-- 4. DROP COLUMN edge_layer — the column-level CHECK constraint
--    edges_edge_layer_valid is dropped via Postgres' DROP COLUMN
--    cascade.
ALTER TABLE public.edges DROP COLUMN edge_layer;

COMMIT;
