-- Migration: 0066_seed_qa_disposition_reversed_revert_part1
-- Purpose: Revert all 7 reversals applied by
--   0066_seed_qa_disposition_reversed_part1.sql. DELETEs the 7
--   reversed-direction rows (matched on provenance =
--   'qa_census_disposition_s_0183' + reversed source/target pair) and
--   re-INSERTs the 7 originals with their preserved UUIDs, original
--   provenance='ai-seed', original evidence=NULL, and original
--   graph_version_added values (preserves byte-identical pre-0066 state
--   except for created_at and updated_at, which the schema regenerates
--   at INSERT time per DEFAULT NOW()).
--
--   This revert exists for hotfix rollback per
--   engine/operations/revert-and-rollback-discipline.md (ADR 0078). It
--   is not applied automatically; the forward 0066 is the canonical
--   QA census disposition state.
-- Loads tables: public.edges (7 DELETEs + 7 INSERTs).
-- Preconditions:
--   * 0066_seed_qa_disposition_reversed_part1.sql applied (the 7
--     reversed-direction rows exist with provenance =
--     'qa_census_disposition_s_0183').
--   * No row exists with the 7 ORIGINAL UUIDs (the forward migration
--     deleted them).
--   * settings.graph_version = 16 (unchanged from 0066).
-- Postconditions:
--   * 0 rows in public.edges with provenance =
--     'qa_census_disposition_s_0183' (the 7 reversal rows are removed).
--   * 7 rows in public.edges with the 7 original UUIDs restored, in
--     the original Reversed direction, provenance='ai-seed',
--     evidence=NULL, original graph_version_added values.
--   * Total pedagogical_prerequisite edges: 516 (unchanged).
--   * Total historical_influence edges: 17 (unchanged).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.edges WHERE provenance = 'qa_census_disposition_s_0183' :: 0
--   SELECT count(*)::int FROM public.edges WHERE id::text IN ('d17a5b8c-d860-4d51-a399-07af73871218','b8ee8fa0-0547-4f89-9448-52514c930094','71caae36-41e7-4171-9bc3-55b14f8ad1b6','aa9df59f-2f78-4a53-9690-5225f5b99f80','cd9b6148-191f-4ca0-84c7-9841e38b406f','592adf3d-d223-46f2-a479-ed688c989a2f','ad62e0e4-7098-46cf-82dc-f2af314eed0b') :: 7
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 516
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) holds. The DELETE
--     removes the canonical-direction triples before the INSERT
--     re-introduces the Reversed-direction originals.
--   * No new nodes inserted. No edges retyped. No edges deleted beyond
--     the 7 reversal rows.
-- Non-responsibilities:
--   * Does not roll back the GitHub Issue authored alongside 0066, the
--     ADR 0059 amendment, or the MemPalace decision drawer. Those are
--     separately addressable via their own surfaces if the revert is
--     accompanied by a broader policy reversal.
--   * Does not preserve created_at / updated_at byte-identically — the
--     INSERT regenerates these via DEFAULT NOW(); the timestamp delta
--     reflects the revert event, not the original authoring.
-- Cross-cutting decisions:
--   * Hotfix posture: this file is for emergency rollback per ADR 0078,
--     not for routine application. The forward 0066 is the canonical
--     QA census disposition state; reverting requires user adjudication
--     of why the QA verdicts no longer stand.
-- Source citations:
--   * Forward migration: 0066_seed_qa_disposition_reversed_part1.sql.
--   * Original graph_version_added values captured in S-0183 pre-author
--     DB query (logged in this revert's per-row INSERT values).
-- Idempotency:
--   * Not idempotent. Re-applying after the first revert apply errors
--     on the DELETE (zero rows match) or the INSERT (UNIQUE constraint
--     on the OLD source/target pairs that now exist).
-- Rollback:
--   The rollback of the revert is re-applying 0066's forward migration
--   (with manual schema_migrations bookkeeping if needed).
-- Dependencies:
--   * Hard: 0066_seed_qa_disposition_reversed_part1.sql.
-- Related:
--   * 0066_seed_qa_disposition_reversed_part1.sql (forward sibling);
--   * engine/operations/revert-and-rollback-discipline.md (ADR 0078);
--   * engine/build_readiness/seed_qa_findings.md §6.1.

BEGIN;

-- ============================================================
-- DELETE the 7 reversal rows (matched on provenance + reversed pair).
-- ============================================================

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'type_b_materialism'
   AND target_id = 'phenomenal_concept_strategy';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'axiom_mathematical'
   AND target_id = 'set_mathematical';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'knowledge'
   AND target_id = 'knowledge_how';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'hedonism'
   AND target_id = 'utilitarianism';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'temporal_parts'
   AND target_id = 'perdurantism';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'philosophical_zombie'
   AND target_id = 'property_dualism';

DELETE FROM public.edges
 WHERE provenance = 'qa_census_disposition_s_0183'
   AND source_id = 'turing_test'
   AND target_id = 'computational_theory_of_mind';

-- ============================================================
-- Re-INSERT the 7 originals with preserved UUIDs, original provenance,
-- original NULL evidence, and original graph_version_added values.
-- ============================================================

INSERT INTO public.edges
  (id, source_id, target_id, edge_type, weight, confidence, provenance,
   graph_version_added, evidence)
VALUES
  ('d17a5b8c-d860-4d51-a399-07af73871218'::uuid,
   'phenomenal_concept_strategy', 'type_b_materialism',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 12, NULL),
  ('b8ee8fa0-0547-4f89-9448-52514c930094'::uuid,
   'set_mathematical', 'axiom_mathematical',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 15, NULL),
  ('71caae36-41e7-4171-9bc3-55b14f8ad1b6'::uuid,
   'knowledge_how', 'knowledge',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 2, NULL),
  ('aa9df59f-2f78-4a53-9690-5225f5b99f80'::uuid,
   'utilitarianism', 'hedonism',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 7, NULL),
  ('cd9b6148-191f-4ca0-84c7-9841e38b406f'::uuid,
   'perdurantism', 'temporal_parts',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 4, NULL),
  ('592adf3d-d223-46f2-a479-ed688c989a2f'::uuid,
   'property_dualism', 'philosophical_zombie',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 12, NULL),
  ('ad62e0e4-7098-46cf-82dc-f2af314eed0b'::uuid,
   'computational_theory_of_mind', 'turing_test',
   'pedagogical_prerequisite', 1.0, 1.0, 'ai-seed', 10, NULL);

COMMIT;
