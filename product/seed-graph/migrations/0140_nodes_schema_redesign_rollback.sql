-- Migration: 0140_nodes_schema_redesign_rollback
-- Purpose: Paired rollback for 0140_nodes_schema_redesign.sql per
--   engine/operations/migration-discipline.md "Rollback authorship".
--   Reverses all schema additions that 0140 introduced. End-to-end
--   round-trip verification at S-0213 close: apply 0140; capture
--   \d+ public.nodes; apply this rollback; re-apply 0140; diff
--   post-re-apply \d+ output against first capture for stability.
-- Loads tables: public.nodes (2 DROP CONSTRAINT for table-level
--   CHECKs + 14 DROP COLUMN statements; column-level CHECKs on
--   granularity + jargon_load drop via Postgres' DROP COLUMN cascade).
-- Preconditions:
--   * 0140 has been applied — public.nodes carries the 14 new
--     columns + 4 new CHECK constraints.
--   * The 380 rows are in their post-0140 default-populated state
--     (node_type = '{unclassified}' on all 380; the other 13 columns
--     at column defaults).
--   * No sequel-session backfill migrations (0141-0149) have been
--     applied. If they have, this rollback would lose the backfilled
--     classification data — sequel-session rollback discipline
--     requires reverting sequel migrations first, then this base
--     migration. In practice this rollback is exercised within the
--     same session as 0140's apply, so this case is structurally
--     impossible at landing.
-- Postconditions:
--   * public.nodes loses 14 columns:
--     node_type, disciplinary_domain, granularity, audience_tags,
--     canonical_sources, approved_examples, misconceptions,
--     assessment_items, mastery_evidence, accessibility_notes,
--     assumed_background, jargon_load, cultural_specificity,
--     tradition_label.
--   * public.nodes loses 4 CHECK constraints:
--     nodes_node_type_valid, nodes_node_type_nonempty (both
--     table-level, dropped explicitly); nodes_granularity_valid,
--     nodes_jargon_load_valid (both column-level on granularity +
--     jargon_load, dropped via DROP COLUMN cascade).
--   * public.nodes row count = 380 (invariant).
--   * PRIMARY KEY (id) preserved.
--   * RLS policy nodes_authenticated_read preserved.
--   * All 17 pre-existing columns (id, label, domain, summary, etc.)
--     unchanged in shape and value.
--   * Cluster 1 + 2 columns on public.edges unchanged (rollback is
--     layer-orthogonal to edges).
-- Postcondition-Assertions:
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'node_type' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'disciplinary_domain' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'granularity' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'audience_tags' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'canonical_sources' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'approved_examples' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'misconceptions' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'assessment_items' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'mastery_evidence' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'accessibility_notes' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'assumed_background' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'jargon_load' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'cultural_specificity' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'tradition_label' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_node_type_valid' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_node_type_nonempty' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_granularity_valid' :: 0
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_jargon_load_valid' :: 0
--   SELECT count(*)::int FROM public.nodes :: 380
-- Invariants:
--   * Row count preserved (380).
--   * PRIMARY KEY preserved.
--   * RLS preserved.
--   * Pre-existing 17 columns untouched.
--   * Cluster 1 + 2 columns + constraints on public.edges untouched.
-- Non-responsibilities:
--   * Does not rollback Cluster 1 substrate (that's
--     0120_edges_contestability_substrate_rollback.sql).
--   * Does not rollback Cluster 2 substrate (that's
--     0130_edges_three_relation_layering_rollback.sql).
--   * Does not advance / decrement settings.graph_version.
--   * Does not handle sequel-session backfill data loss (see
--     Preconditions caveat — sequel rollbacks land first if any
--     have been applied).
-- Cross-cutting decisions:
--   * Drop table-level CHECK constraints (nodes_node_type_valid,
--     nodes_node_type_nonempty) BEFORE dropping the node_type column
--     so the constraint references resolve cleanly during DROP.
--     Postgres' DROP COLUMN does auto-cascade to constraints, but
--     explicit DROP CONSTRAINT is cleaner for table-level constraints
--     that reference the dropped column.
--   * Column-level CHECK constraints (nodes_granularity_valid,
--     nodes_jargon_load_valid) drop via DROP COLUMN cascade — no
--     explicit DROP CONSTRAINT needed for those.
--   * Order of DROP COLUMN statements does not matter (columns are
--     independent; no FK or generated-column dependencies between them).
--     Listed in reverse-of-add order for readability.
--   * BEGIN/COMMIT wraps all statements atomically; partial rollback
--     would surface as a transaction-level abort.
-- Rollback (of this rollback): re-apply 0140_nodes_schema_redesign.sql.
-- See also: product/seed-graph/migrations/0140_nodes_schema_redesign.sql,
--   engine/operations/migration-discipline.md "Rollback authorship".

BEGIN;

-- 1. Drop table-level CHECK constraints on node_type before dropping
--    the column. Column-level CHECKs on granularity + jargon_load
--    drop via DROP COLUMN cascade in step 2.
ALTER TABLE public.nodes DROP CONSTRAINT nodes_node_type_valid;
ALTER TABLE public.nodes DROP CONSTRAINT nodes_node_type_nonempty;

-- 2. Drop all 14 new columns in reverse-of-add order. The column-
--    level CHECKs on granularity + jargon_load drop automatically
--    via Postgres' DROP COLUMN cascade.
ALTER TABLE public.nodes DROP COLUMN tradition_label;
ALTER TABLE public.nodes DROP COLUMN cultural_specificity;
ALTER TABLE public.nodes DROP COLUMN jargon_load;
ALTER TABLE public.nodes DROP COLUMN assumed_background;
ALTER TABLE public.nodes DROP COLUMN accessibility_notes;
ALTER TABLE public.nodes DROP COLUMN mastery_evidence;
ALTER TABLE public.nodes DROP COLUMN assessment_items;
ALTER TABLE public.nodes DROP COLUMN misconceptions;
ALTER TABLE public.nodes DROP COLUMN approved_examples;
ALTER TABLE public.nodes DROP COLUMN canonical_sources;
ALTER TABLE public.nodes DROP COLUMN audience_tags;
ALTER TABLE public.nodes DROP COLUMN granularity;
ALTER TABLE public.nodes DROP COLUMN disciplinary_domain;
ALTER TABLE public.nodes DROP COLUMN node_type;

COMMIT;
