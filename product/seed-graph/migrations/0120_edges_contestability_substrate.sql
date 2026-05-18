-- Migration: 0120_edges_contestability_substrate
-- Purpose: Tier-A Cluster 1 — Contestability substrate per
--   product/adr/0097-tier-a-cluster-1-contestability-substrate.md.
--   First Tier-A cluster-implementation migration per
--   product/adr/0094-phase-6-scope.md dependency order
--   C1 → C2 → C4 → C3 → C5. Lands the per-edge atomic contestability
--   substrate the synthesis names: confidence three-source +
--   provenance five-field JSONB + counterexamples JSONB array +
--   version + review_status + last_reviewed. Adjudicates two
--   existing-column overlaps via ALTER + backfill (rename
--   confidence → expert_confidence preserving REAL values; ALTER
--   provenance TEXT → JSONB with USING-clause backfill that maps
--   the prior 'human' single-token value to JSONB
--   {"reviewer": "human", ...}). The 533-row count is invariant —
--   this is pure schema, no INSERT/UPDATE/DELETE of edge rows. Adds
--   7 new columns. Closes ADR 0094 T1-A + ADR 0095 T1-A at landing.
-- Loads tables: public.edges (1 rename + 1 ALTER TYPE with USING
--   backfill + 7 ADD COLUMN statements; no INSERT/UPDATE/DELETE on
--   edge rows beyond the implicit USING-clause type-conversion that
--   re-writes the 533 existing provenance values).
-- Preconditions:
--   * Phase 3 schema in place: public.edges exists with the columns
--     from 0003_edges.sql (confidence REAL, provenance TEXT,
--     plus id/source_id/target_id/edge_type/weight/evidence/
--     graph_version_added/created_at/updated_at + the
--     UNIQUE(source_id, target_id, edge_type) constraint).
--   * public.edges currently carries 533 rows (516
--     pedagogical_prerequisite + 17 historical_influence per
--     ROUTING.md S-0123 narrative entry final-state numbers).
--   * No prior migrations in the 0120-0129 prefix range — this is
--     the first Phase 6 self-correction schema addition and the
--     first claim within the Cluster 1 sub-range (per ROUTING.md
--     S-0207 narrative entry).
--   * settings.graph_version = 16 at session boot (post-S-0123;
--     this migration does not advance the counter because no
--     node/edge rows are inserted).
-- Postconditions:
--   * public.edges loses column `confidence` and gains column
--     `expert_confidence` carrying the prior `confidence` REAL
--     values (1.0 default for all 533 existing rows) with the
--     CHECK (expert_confidence BETWEEN 0 AND 1) constraint
--     (renamed from `edges_confidence_check`).
--   * public.edges.provenance column type alters from TEXT to JSONB.
--     The 533 existing rows carry post-backfill value
--     {"source_text": null, "course_context": null, "version": 1,
--     "reviewer": "human", "rationale": null} — preserving the prior
--     `provenance = 'human'` signal in the new structured shape.
--     CHECK constraint enforces jsonb_typeof = 'object' AND all five
--     required keys present.
--   * public.edges carries seven new columns:
--     - trace_confidence REAL NULL (CHECK NULL OR BETWEEN 0 AND 1)
--     - llm_confidence REAL NULL (CHECK NULL OR BETWEEN 0 AND 1)
--     - disagreement_flag BOOLEAN NOT NULL DEFAULT FALSE
--     - counterexamples JSONB NOT NULL DEFAULT '[]'::jsonb
--       (CHECK jsonb_typeof = 'array'; element shape
--       {description: TEXT, evidence_link?: TEXT} documented in
--       ADR 0097, not CHECK-enforced)
--     - version INTEGER NOT NULL DEFAULT 1 (CHECK >= 1)
--     - review_status TEXT NOT NULL DEFAULT 'provisional'
--       (CHECK IN ('approved', 'pending_review', 'rejected',
--       'provisional'))
--     - last_reviewed TIMESTAMPTZ NULL
--   * public.edges row count = 533 (invariant — pure schema change).
--   * UNIQUE(source_id, target_id, edge_type) preserved.
--   * RLS policy edges_authenticated_read preserved.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. Verifies (a) schema shape — each
--   new/renamed column exists or is removed as expected; (b) backfill
--   correctness — every existing row has the expected default values
--   in the new shape; (c) row-count invariance — pure schema change
--   does not mutate edge data; (d) constraint shape — CHECK and
--   DEFAULT semantics fire correctly. ON CONFLICT skip / partial
--   ALTER / silent backfill divergence would surface as exit 8.)
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'expert_confidence' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'confidence' :: 0
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'provenance' AND data_type = 'jsonb' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'trace_confidence' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'llm_confidence' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'disagreement_flag' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'counterexamples' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'version' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'review_status' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'edges' AND column_name = 'last_reviewed' :: 1
--   SELECT count(*)::int FROM public.edges :: 533
--   SELECT count(*)::int FROM public.edges WHERE expert_confidence = 1.0 :: 533
--   SELECT count(*)::int FROM public.edges WHERE provenance->>'reviewer' = 'human' :: 533
--   SELECT count(*)::int FROM public.edges WHERE provenance ? 'source_text' AND provenance ? 'course_context' AND provenance ? 'version' AND provenance ? 'reviewer' AND provenance ? 'rationale' :: 533
--   SELECT count(*)::int FROM public.edges WHERE counterexamples = '[]'::jsonb :: 533
--   SELECT count(*)::int FROM public.edges WHERE version = 1 :: 533
--   SELECT count(*)::int FROM public.edges WHERE review_status = 'provisional' :: 533
--   SELECT count(*)::int FROM public.edges WHERE disagreement_flag = FALSE :: 533
--   SELECT count(*)::int FROM public.edges WHERE trace_confidence IS NULL :: 533
--   SELECT count(*)::int FROM public.edges WHERE llm_confidence IS NULL :: 533
--   SELECT count(*)::int FROM public.edges WHERE last_reviewed IS NULL :: 533
-- Invariants:
--   * Row count on public.edges is preserved (533 before; 533 after).
--     Pure schema change — no INSERT/UPDATE/DELETE of edges beyond
--     the implicit USING-clause type-conversion on provenance which
--     re-writes the 533 prior values into JSONB form.
--   * UNIQUE(source_id, target_id, edge_type) constraint is preserved.
--   * RLS policy edges_authenticated_read is preserved.
--   * Existing columns unchanged: id, source_id, target_id, edge_type,
--     weight, evidence, graph_version_added, created_at, updated_at.
--     The pre-existing `evidence` column is semantically distinct from
--     the new `counterexamples` column (evidence supports the edge
--     claim; counterexamples records exceptions); both coexist.
--   * The pre-existing `graph_version_added` column (records migration-
--     session graph_version at insertion time per the ROUTING.md
--     graph_version increment contract) is preserved; the new `version`
--     column is the per-edge revision counter (different semantic).
--     Both coexist without conflict; the future graph_versions table
--     (deferred to a Cluster 3-paired migration per ADR 0097) will
--     link to the new `version` column, not `graph_version_added`.
-- Non-responsibilities:
--   * Does not create the `graph_versions` table (deferred to a
--     Cluster 3-paired migration when learning_outcomes lands —
--     cohort/course-scoping for versioning is goal-relative per
--     ADR 0097 Decision "Explicit deferrals").
--   * Does not specify the DISAGREEMENT_THRESHOLD numeric value
--     (deferred to post-SQA calibration per ADR 0097 premise 6;
--     named as ADR 0097 T1-B closure criterion). The computation
--     `disagreement_flag = (max(non_null_confidences) - min(non_null_
--     confidences)) >= DISAGREEMENT_THRESHOLD` is specified in the
--     ADR but not applied here — all 533 rows default disagreement_
--     flag to FALSE (computation collapses to 0 spread because only
--     expert_confidence is populated for existing edges).
--   * Does not implement the `validate_edges_contestability_unguarded_
--     high_confidence` validator soft-warn (synthesis line 70).
--     Committed as a Consequences-deliverable in ADR 0097; implementation
--     defers to a follow-up Issue filed at S-0207 close — implementing
--     now would fire on all 533 existing edges (entire seed corpus has
--     expert_confidence = 1.0 + empty counterexamples + null rationale
--     post-migration), drowning the signal. Post-Cluster 2 retyping
--     to soft_prerequisite with expert_confidence: low defaults makes
--     the soft-warn meaningful.
--   * Does not retype the 516 existing pedagogical_prerequisite edges
--     to soft_prerequisite — that is Cluster 2's responsibility per
--     ADR 0094 dependency order; the `review_status: 'provisional'`
--     default this migration sets is the coordination point with
--     Cluster 2's retyping defaults per ADR 0097 Decision.
--   * Does not enforce per-element JSONB shape on counterexamples
--     array entries ({description, evidence_link?}). Per-element type
--     checking across a JSONB array is unwieldy in plain CHECK; per-
--     element shape is documented in ADR 0097 and verified at the
--     application layer.
--   * Does not advance settings.graph_version (no node/edge rows
--     inserted; pure schema change does not advance the counter per
--     the ROUTING.md graph_version increment contract).
-- Cross-cutting decisions:
--   * Confidence symmetric REAL representation (all three confidence
--     columns REAL 0-1, not asymmetric enum/REAL mix) per ADR 0097
--     Decision §1 + Alternatives Considered §4. The project's
--     enum-band convention (low=0-0.4, medium=0.4-0.7, high=0.7-1.0)
--     remains as a UI/reporting convention, not a storage constraint.
--   * ALTER + backfill on existing confidence and provenance columns
--     per ADR 0097 Decision §1 + Alternatives Considered §1 — preserves
--     existing data signal (the prior 'human' provenance becomes
--     provenance.reviewer = 'human'); converges on the synthesis-target
--     shape with zero data loss.
--   * provenance JSONB CHECK constraint enforces object shape + key
--     presence (jsonb_typeof + ? operator). Per-key value-type validation
--     is documented in ADR 0097 not CHECK-enforced (the five values are
--     either nullable text or integer per the contract); application
--     layer can enforce stricter shape if needed.
--   * No CASCADE discipline change. Edges carry no learner-state FK to
--     users per ADR 0031; edge deletion is not user-coupled. The new
--     columns are append-only to the table; no FK relationships.
--   * RLS posture unchanged. Edges read by authenticated users; writes
--     service-role-only.
-- Rollback: 0120_edges_contestability_substrate_rollback.sql in the
--   same prefix slot. Reverses all 9 column-level changes: DROP the
--   7 new columns; ALTER provenance JSONB → TEXT with USING-clause
--   back-conversion (extracts provenance->>'reviewer' to restore the
--   prior single-token value); rename expert_confidence → confidence
--   restoring the prior column name + CHECK constraint name. End-to-
--   end verified at S-0207 close per migration-discipline.md "Rollback
--   authorship" — apply 0120; capture \d+ public.edges; apply rollback;
--   re-apply 0120; diff post-re-apply \d+ output against first capture
--   for stability.
-- See also: product/adr/0097-tier-a-cluster-1-contestability-substrate.md,
--   product/adr/0094-phase-6-scope.md (T1-A closes here),
--   product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md (T1-A closes here),
--   engine/build_readiness/pdg_papers_extraction/synthesis.md §Cluster 1 (lines 48-78),
--   engine/operations/migration-discipline.md,
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md (Layer 2.5 grammar),
--   product/seed-graph/migrations/0003_edges.sql (pre-state schema),
--   product/seed-graph/migrations/ROUTING.md S-0207 narrative entry.

BEGIN;

-- 1. Rename existing confidence column to expert_confidence.
--    Preserves the 533-row REAL values + CHECK constraint shape.
--    Postgres ALTER TABLE RENAME COLUMN preserves CHECK constraint
--    bound to the column; constraint name is generated from the
--    column name (edges_confidence_check), so the rename leaves
--    constraint-name drift to clean up explicitly.
ALTER TABLE public.edges RENAME COLUMN confidence TO expert_confidence;
ALTER TABLE public.edges RENAME CONSTRAINT edges_confidence_check TO edges_expert_confidence_check;

-- 2. ALTER provenance TEXT → JSONB with USING-clause backfill.
--    The 533 existing rows carry provenance = 'human' (the schema's
--    DEFAULT); the USING clause backfills each row to the five-field
--    JSONB structure preserving the 'human' token as reviewer. The
--    DEFAULT clause is also updated to the empty-object form for any
--    future INSERTs that omit provenance (immediately followed by a
--    CHECK that requires keys, so INSERT-without-provenance will
--    require an explicit JSONB literal — DEFAULT '{}'::jsonb fails
--    the CHECK and surfaces the contract).
--    NB: Postgres has no atomic "ALTER + new CHECK" — the type alter
--    runs first, then CHECK validates against the post-USING-clause
--    values. The backfill ensures all rows satisfy the new CHECK.
ALTER TABLE public.edges
  ALTER COLUMN provenance TYPE JSONB
    USING jsonb_build_object(
      'source_text', NULL::text,
      'course_context', NULL::text,
      'version', 1,
      'reviewer', provenance,
      'rationale', NULL::text
    ),
  ALTER COLUMN provenance SET DEFAULT '{}'::jsonb;

-- 3. CHECK constraint on provenance: object shape + 5 required keys.
ALTER TABLE public.edges
  ADD CONSTRAINT edges_provenance_shape_check
  CHECK (
    jsonb_typeof(provenance) = 'object'
    AND provenance ? 'source_text'
    AND provenance ? 'course_context'
    AND provenance ? 'version'
    AND provenance ? 'reviewer'
    AND provenance ? 'rationale'
  );

-- 4. ADD COLUMN trace_confidence REAL NULL — populated by Cluster 7
--    SQA pipeline; NULL until learner trace data exists.
ALTER TABLE public.edges
  ADD COLUMN trace_confidence REAL NULL
    CHECK (trace_confidence IS NULL OR (trace_confidence BETWEEN 0 AND 1));

-- 5. ADD COLUMN llm_confidence REAL NULL — populated for LLM-proposed
--    edges; NULL for all existing 533 human-authored edges.
ALTER TABLE public.edges
  ADD COLUMN llm_confidence REAL NULL
    CHECK (llm_confidence IS NULL OR (llm_confidence BETWEEN 0 AND 1));

-- 6. ADD COLUMN disagreement_flag BOOLEAN NOT NULL DEFAULT FALSE.
--    Computed-set field — never user-set; populated by a triggered or
--    scheduled job applying the computation in ADR 0097 premise 6
--    (disagreement_flag = (max(non_null_confidences) - min(non_null_
--    confidences)) >= DISAGREEMENT_THRESHOLD) once the threshold is
--    calibrated post-SQA. All 533 existing rows default to FALSE
--    (computation collapses to 0 spread because only expert_confidence
--    is populated).
ALTER TABLE public.edges
  ADD COLUMN disagreement_flag BOOLEAN NOT NULL DEFAULT FALSE;

-- 7. ADD COLUMN counterexamples JSONB NOT NULL DEFAULT '[]'::jsonb.
--    Each entry shape {description, evidence_link?} per ADR 0097
--    premise 5 + Decision; per-element type-check is unwieldy in
--    plain CHECK so element shape is application-layer.
ALTER TABLE public.edges
  ADD COLUMN counterexamples JSONB NOT NULL DEFAULT '[]'::jsonb
    CHECK (jsonb_typeof(counterexamples) = 'array');

-- 8. ADD COLUMN version INTEGER NOT NULL DEFAULT 1 — per-edge
--    revision counter. Distinct from graph_version_added (which records
--    the migration-session graph_version at insertion time). All 533
--    existing rows default to 1; future graph_versions table (deferred)
--    will link to this column.
ALTER TABLE public.edges
  ADD COLUMN version INTEGER NOT NULL DEFAULT 1
    CHECK (version >= 1);

-- 9. ADD COLUMN review_status TEXT NOT NULL DEFAULT 'provisional'.
--    All 533 existing rows default to 'provisional' — they retype to
--    soft_prerequisite via Cluster 2 ADR per ADR 0094 dependency note
--    + synthesis line 109 pending SQA validation; 'provisional' is the
--    matching review-lifecycle posture. Cluster 2 ADR coordinates the
--    default.
ALTER TABLE public.edges
  ADD COLUMN review_status TEXT NOT NULL DEFAULT 'provisional'
    CHECK (review_status IN ('approved', 'pending_review', 'rejected', 'provisional'));

-- 10. ADD COLUMN last_reviewed TIMESTAMPTZ NULL — populated by Cluster 7
--     SQA pipeline or manual reviewer action; NULL until first review.
ALTER TABLE public.edges
  ADD COLUMN last_reviewed TIMESTAMPTZ NULL;

COMMIT;
