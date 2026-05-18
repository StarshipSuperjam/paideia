-- Migration: 0120_edges_contestability_substrate_rollback
-- Purpose: Paired rollback for 0120_edges_contestability_substrate.sql.
--   Reverses all 9 column-level changes restoring the pre-0120 schema:
--   DROP the 7 new columns; ALTER provenance JSONB → TEXT with USING-
--   clause back-conversion extracting provenance->>'reviewer' to restore
--   the prior single-token value; rename expert_confidence → confidence
--   restoring the prior column name + CHECK constraint name. End-to-end
--   round-trip verified at S-0207 close per migration-discipline.md
--   "Rollback authorship" (apply 0120; capture \d+ public.edges; apply
--   this rollback; re-apply 0120; diff post-re-apply \d+ output against
--   first capture for stability).
-- Loads tables: public.edges (7 DROP COLUMN statements + 1 ALTER TYPE
--   with USING-clause back-conversion + 1 RENAME COLUMN + 1 RENAME
--   CONSTRAINT + 1 DROP CONSTRAINT on the provenance JSONB shape
--   check; no INSERT/UPDATE/DELETE on edge rows beyond the implicit
--   USING-clause type-conversion which re-writes the 533 JSONB
--   provenance values back to TEXT).
-- Preconditions:
--   * 0120_edges_contestability_substrate.sql has been applied:
--     public.edges carries expert_confidence (REAL), trace_confidence
--     (REAL NULL), llm_confidence (REAL NULL), disagreement_flag
--     (BOOLEAN), counterexamples (JSONB), version (INTEGER),
--     review_status (TEXT), last_reviewed (TIMESTAMPTZ), and
--     provenance is JSONB shape {source_text, course_context, version,
--     reviewer, rationale}.
--   * public.edges currently carries 533 rows (invariant — neither
--     0120 nor this rollback mutate edge data beyond the type-conversion
--     re-writes).
-- Postconditions:
--   * public.edges loses the 7 columns added by 0120: trace_confidence,
--     llm_confidence, disagreement_flag, counterexamples, version,
--     review_status, last_reviewed.
--   * public.edges.provenance column type reverts JSONB → TEXT. The
--     533 existing rows carry post-back-conversion value = the original
--     reviewer token (extracted via provenance->>'reviewer'); for all
--     533 existing rows this is 'human'. The DEFAULT reverts to 'human'.
--     The JSONB-shape CHECK constraint added by 0120 is dropped.
--   * public.edges loses column expert_confidence and gains column
--     confidence carrying the same REAL values (1.0 for all 533
--     existing rows) with CHECK (confidence BETWEEN 0 AND 1) constraint
--     name restored to edges_confidence_check.
--   * public.edges row count = 533 (invariant).
--   * UNIQUE(source_id, target_id, edge_type) preserved.
--   * RLS policy edges_authenticated_read preserved.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 — verifies the rollback restores the
--   pre-0120 schema shape + data signal. The round-trip exercise
--   (apply 0120 → apply rollback → re-apply 0120 → diff \d+) is
--   performed manually at S-0207 close per migration-discipline.md;
--   these assertions verify the rollback's own post-state.)
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'confidence' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'expert_confidence' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'provenance' AND data_type = 'text' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'trace_confidence' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'llm_confidence' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'disagreement_flag' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'counterexamples' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'version' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'review_status' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'last_reviewed' :: 0
--   SELECT count(*)::int FROM public.edges :: 533
--   SELECT count(DISTINCT confidence)::int FROM public.edges :: 5
--   SELECT count(*)::int FROM public.edges WHERE confidence = 1.0 :: 499
--   SELECT count(*)::int FROM public.edges WHERE provenance = 'ai-seed' :: 526
--   SELECT count(*)::int FROM public.edges WHERE provenance = 'qa_census_disposition_s_0183' :: 7
-- Invariants:
--   * Row count on public.edges is preserved (533 before; 533 after).
--   * UNIQUE(source_id, target_id, edge_type) constraint is preserved.
--   * RLS policy edges_authenticated_read is preserved.
--   * Round-trip stability: apply 0120 → apply this rollback → re-apply
--     0120 → resulting \d+ public.edges matches the first apply's \d+
--     output. Verified manually at S-0207 close.
-- Non-responsibilities:
--   * Does not restore the application-layer state of any code that
--     consumed the 7 new columns. Application-layer rollback (deployment
--     code rollback to a version that doesn't reference the new columns)
--     is out of scope for this SQL migration.
--   * Does not record a row in supabase_migrations.schema_migrations.
--     The apply_migration wrapper handles recording; this file is the
--     SQL the wrapper applies for the rollback direction.
-- Cross-cutting decisions:
--   * provenance back-conversion preserves the reviewer token. Rows
--     authored after 0120 with a non-'human' reviewer (none exist at
--     this rollback's authoring, but a future re-rollback could
--     encounter them) carry their reviewer token forward through the
--     rollback. The signal of "originally human-authored" is preserved.
--   * No CASCADE concerns. Edges carry no learner-state FK to users;
--     dropping columns does not affect cascade discipline per ADR 0031.
-- See also: 0120_edges_contestability_substrate.sql,
--   product/adr/0097-tier-a-cluster-1-contestability-substrate.md,
--   engine/operations/migration-discipline.md "Rollback authorship".

BEGIN;

-- 1. DROP the JSONB-shape CHECK constraint on provenance before the
--    type-conversion (the back-conversion to TEXT renders the
--    jsonb_typeof/? checks invalid).
ALTER TABLE public.edges DROP CONSTRAINT edges_provenance_shape_check;

-- 2a. DROP the JSONB default before ALTER TYPE.
--     Same Postgres limitation as the forward direction: '{}'::jsonb
--     cannot auto-cast to TEXT in the DEFAULT expression. Verified
--     empirically at S-0207 rollback round-trip exercise.
ALTER TABLE public.edges ALTER COLUMN provenance DROP DEFAULT;

-- 2b. ALTER provenance JSONB → TEXT with USING-clause back-conversion.
--     Extracts provenance->>'reviewer' to restore the prior single-
--     token TEXT value. Round-trip verified at S-0207: post-rollback
--     yields 526 'ai-seed' + 7 'qa_census_disposition_s_0183' (matching
--     the actual pre-0120 distribution observed at apply time — not
--     all 'human' as the original ADR 0097 prose assumed; the 'human'
--     schema DEFAULT never fired because every Phase 5+ INSERT
--     supplied an explicit reviewer token).
ALTER TABLE public.edges
  ALTER COLUMN provenance TYPE TEXT USING (provenance->>'reviewer');

-- 2c. SET the TEXT default back to the prior schema value.
ALTER TABLE public.edges ALTER COLUMN provenance SET DEFAULT 'human';

-- 3. DROP the 7 new columns. Order does not matter (no FK relationships
--    among them); listed in reverse-add order for symmetry with the
--    forward migration.
ALTER TABLE public.edges DROP COLUMN last_reviewed;
ALTER TABLE public.edges DROP COLUMN review_status;
ALTER TABLE public.edges DROP COLUMN version;
ALTER TABLE public.edges DROP COLUMN counterexamples;
ALTER TABLE public.edges DROP COLUMN disagreement_flag;
ALTER TABLE public.edges DROP COLUMN llm_confidence;
ALTER TABLE public.edges DROP COLUMN trace_confidence;

-- 4. Rename expert_confidence → confidence restoring the prior column
--    name + CHECK constraint name.
ALTER TABLE public.edges RENAME CONSTRAINT edges_expert_confidence_check TO edges_confidence_check;
ALTER TABLE public.edges RENAME COLUMN expert_confidence TO confidence;

COMMIT;
