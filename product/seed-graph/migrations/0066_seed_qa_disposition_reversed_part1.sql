-- Migration: 0066_seed_qa_disposition_reversed_part1
-- Purpose: Disposition of the S-0182 T-SEED-QA census C1 findings: the
--   seven pedagogical_prerequisite edges scored Reversed across shards
--   01, 02, 03, 05, 08 are corrected to the pedagogically-canonical
--   direction. Per the S-0183 user direction ("Always DELETE + INSERT
--   for clean provenance"), each reversal lands as a DELETE of the
--   original UUID followed by an INSERT in the corrected direction
--   with a fresh provenance of 'qa_census_disposition_s_0183' and an
--   evidence column populated with the census sub-shape rationale.
--   This is distinct from the 0062 audit-followup posture (UPDATE in
--   place to preserve UUID + created_at + graph_version_added) — the
--   QA census disposition is recorded as a corrective re-authoring,
--   not a modification of the original audit's edge identity.
--
--   The 7 Reversed verdicts cluster into three structural sub-shapes
--   (per seed_qa_findings.md §6.1):
--
--   Sub-shape A — theory > its constitutive concept (4 instances):
--     * knowledge_how > knowledge (shard 01 E-26)
--     * utilitarianism > hedonism (shard 02 E-15)
--     * perdurantism > temporal_parts (shard 03 E-14)
--     * computational_theory_of_mind > turing_test (shard 08 E-4)
--   Sub-shape B — specific position > defining thought-experiment /
--     sub-position (2 instances):
--     * phenomenal_concept_strategy > type_b_materialism (shard 01 E-5)
--     * property_dualism > philosophical_zombie (shard 05 E-7)
--   Sub-shape C — derived service-node > foundational service-node
--     (1 instance):
--     * set_mathematical > axiom_mathematical (shard 01 E-24)
--
--   Census prevalence: 7 / 516 = 1.36%, all within-domain (cross-domain
--   edges scored 0/55 defective — the audit's cross-bridge fortification
--   per migrations 0061-0065 durably held). The disposition is bounded
--   to these 7 unambiguous Reversed verdicts. The 9 "target is more
--   general / more foundational" Defensible exemplars (shards 05-09;
--   findings §6.2) are held at Defensible per the rubric and routed to
--   a separate rubric-calibration GitHub Issue authored in the same
--   session.
-- Loads tables: public.edges (7 DELETEs + 7 INSERTs).
-- Preconditions:
--   * 0065 applied (the phenomenology cross-bridge landed; total
--     pedagogical_prerequisite count = 516 pre-apply).
--   * settings.graph_version = 16.
--   * All 7 (OLD source, OLD target) pairs exist as
--     pedagogical_prerequisite (verified via S-0183 pre-author DB query
--     against the 7 original UUIDs).
--   * All 7 (NEW source, NEW target) flipped pairs do NOT exist as
--     pedagogical_prerequisite (verified via S-0183 pre-author DB
--     collision check — zero canonical-direction collisions).
-- Postconditions:
--   * 0 rows remain in public.edges with the 7 original UUIDs.
--   * 7 new rows in public.edges with (source_id, target_id) in the
--     pedagogically-canonical direction, fresh UUIDs (auto-generated
--     via gen_random_uuid()), provenance='qa_census_disposition_s_0183',
--     graph_version_added=16, evidence populated with the census
--     sub-shape rationale.
--   * Total pedagogical_prerequisite edges: 516 (unchanged — DELETE 7
--     and INSERT 7 nets to zero count delta).
--   * Total historical_influence edges: 17 (unchanged from 0061).
--   * settings.graph_version = 16 (unchanged).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.edges WHERE id::text IN ('d17a5b8c-d860-4d51-a399-07af73871218','b8ee8fa0-0547-4f89-9448-52514c930094','71caae36-41e7-4171-9bc3-55b14f8ad1b6','aa9df59f-2f78-4a53-9690-5225f5b99f80','cd9b6148-191f-4ca0-84c7-9841e38b406f','592adf3d-d223-46f2-a479-ed688c989a2f','ad62e0e4-7098-46cf-82dc-f2af314eed0b') :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('type_b_materialism','phenomenal_concept_strategy'),('axiom_mathematical','set_mathematical'),('knowledge','knowledge_how'),('hedonism','utilitarianism'),('temporal_parts','perdurantism'),('philosophical_zombie','property_dualism'),('turing_test','computational_theory_of_mind')) :: 7
--   SELECT count(*)::int FROM public.edges WHERE provenance = 'qa_census_disposition_s_0183' :: 7
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 516
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds.
--     The DELETE removes the OLD triple before the INSERT introduces
--     the NEW triple; pre-apply collision check confirmed no
--     canonical-direction collisions exist.
--   * No new nodes inserted. No edges retyped.
--   * Cycle detection: validate.py's Kosaraju SCC check will re-run
--     post-apply. The 7 reversals do not introduce cycles by
--     construction — they correct directions to the pedagogically
--     canonical orientation; no new edge runs in a direction not
--     already implied as canonical by the existing graph topology.
-- Non-responsibilities:
--   * Does not author new edges beyond the 7 reversal pairs.
--   * Does not modify edges outside the disposition set.
--   * Does not increment public.settings.graph_version (follows the
--     0061-0065 audit-followup precedent: corrections to published
--     version 16 stay at 16).
--   * Does not flip direction on edges with verdicts other than
--     "Reversed" — the 9 "target is more general" Defensible
--     exemplars are routed to a separate rubric-calibration Issue.
-- Cross-cutting decisions:
--   * Implementation shape: DELETE + INSERT per S-0183 user direction.
--     Distinct from 0062 (UPDATE in place). The census disposition
--     records each reversal as a corrective re-authoring with fresh
--     row identity and provenance string, rather than as an in-place
--     direction swap on the audit's original edge.
--   * Provenance string: 'qa_census_disposition_s_0183' identifies
--     the reversing migration. The evidence column carries the census
--     sub-shape rationale (A / B / C per §6.1) and the original-edge
--     UUID for traceability across the DELETE.
--   * graph_version posture: follows 0061-0065 — audit-followup
--     corrections stay at graph_version 16; new rows carry
--     graph_version_added=16 (they join the current published cohort).
-- Source citations:
--   * QA census closeout findings:
--     engine/build_readiness/seed_qa_findings.md §6.1 Reversed cluster
--     (sub-shapes A / B / C; the 7 edges).
--   * QA census per-shard evidence files:
--     engine/build_readiness/seed_qa_evidence/shard_01.md (E-5, E-24, E-26)
--     engine/build_readiness/seed_qa_evidence/shard_02.md (E-15)
--     engine/build_readiness/seed_qa_evidence/shard_03.md (E-14)
--     engine/build_readiness/seed_qa_evidence/shard_05.md (E-7)
--     engine/build_readiness/seed_qa_evidence/shard_08.md (E-4)
--   * Original migrations whose graph_version_added carried the 7
--     originals: 0011 (E-26 knowledge_how/knowledge gv=2), 0026 (E-14
--     perdurantism/temporal_parts gv=4), 0030 (gv-range for E-15
--     utilitarianism/hedonism gv=7), 0040 (gv=10 for E-4 CTM/Turing;
--     gv=12 for E-5 phenomenal_concept_strategy and E-7 property_dualism),
--     0050 (gv=15 for E-24 set/axiom). Per-row gv values captured in
--     S-0183 pre-author DB query for revert authorship.
--   * Closest precedent (audit-followup direction corrections):
--     0062_seed_direction_flips_part1.sql (used UPDATE; this migration
--     uses DELETE+INSERT per user direction).
-- Idempotency:
--   * Not idempotent. Re-applying after the first apply would error
--     on the DELETE (zero rows matching the OLD UUIDs) or the INSERT
--     (UNIQUE constraint on the NEW source/target pair). The wrapper's
--     exit-6 already-applied gate is the canonical re-fire defense.
-- Rollback:
--   See sibling 0066_seed_qa_disposition_reversed_revert_part1.sql
--   which DELETEs the 7 reversals (matching on the
--   qa_census_disposition_s_0183 provenance + reversed source/target)
--   and re-INSERTs the 7 originals with their preserved UUIDs,
--   original provenance='ai-seed', original evidence=NULL, and
--   original graph_version_added values (2, 4, 7, 10, 12, 12, 15).
-- Dependencies:
--   * Hard: 0002, 0003 (schema). 0011, 0026, 0030, 0040, 0050 + the
--     subsequent seed batches that authored the 7 originals. 0065
--     (most recent applied; pre-apply baseline pedagogical_prerequisite
--     count = 516).
--   * Soft: ROUTING.md (per-session narrative appended in same commit).
-- Related:
--   * engine/build_readiness/seed_qa_findings.md §6.1 + §7.2;
--   * engine/build_readiness/seed_qa_audit.md (pinned census rubric);
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--     (apply via wrapper; Layer 2.5 postcondition assertions);
--   * engine/operations/migration-discipline.md Layer 2.5;
--   * engine/adr/0059-audit-time-structural-reference-fetching.md
--     (the census's structural-reference-fetching discipline);
--   * product/adr/0001-pedagogical-edges-not-historical.md
--     (pedagogical edge direction discipline);
--   * 0066_seed_qa_disposition_reversed_revert_part1.sql (sibling).

BEGIN;

-- ============================================================
-- 7 DELETEs of the Reversed-direction originals.
-- ============================================================

-- Shard 01 E-5 (Sub-shape B): phenomenal_concept_strategy >
-- type_b_materialism. The phenomenal-concept strategy is the
-- explanatory machinery deployed in defense of type-B materialism —
-- the strategy presupposes the position it serves.
DELETE FROM public.edges
 WHERE id = 'd17a5b8c-d860-4d51-a399-07af73871218';

-- Shard 01 E-24 (Sub-shape C): set_mathematical > axiom_mathematical.
-- Axioms of geometry and arithmetic predate and are independent of
-- set theory; axiomatic set theory presupposes the notion of an axiom.
DELETE FROM public.edges
 WHERE id = 'b8ee8fa0-0547-4f89-9448-52514c930094';

-- Shard 01 E-26 (Sub-shape A): knowledge_how > knowledge. Knowledge
-- is the genus; Knowledge-How is the specialized species — Ryle's
-- knowledge-how vs knowledge-that distinction is drawn against the
-- backdrop of knowledge in general.
DELETE FROM public.edges
 WHERE id = '71caae36-41e7-4171-9bc3-55b14f8ad1b6';

-- Shard 02 E-15 (Sub-shape A): utilitarianism > hedonism. Hedonism
-- is a constituent axiology of classical (Benthamite/Millian)
-- utilitarianism, not a downstream consequence of it; hedonism is
-- intelligible on its own without utilitarianism.
DELETE FROM public.edges
 WHERE id = 'aa9df59f-2f78-4a53-9690-5225f5b99f80';

-- Shard 03 E-14 (Sub-shape A): perdurantism > temporal_parts.
-- Perdurantism is defined in terms of temporal parts — the view that
-- objects persist by having temporal parts (4D worms). The constituent
-- notion must be grasped before the theory.
DELETE FROM public.edges
 WHERE id = 'cd9b6148-191f-4ca0-84c7-9841e38b406f';

-- Shard 05 E-7 (Sub-shape B): property_dualism > philosophical_zombie.
-- The zombie thought experiment is the intuition pump that motivates
-- property dualism (Chalmers's conceivability argument). Consistent
-- with the 0062 precedent flipping the structurally-identical pair
-- property_dualism > knowledge_argument to knowledge_argument >
-- property_dualism.
DELETE FROM public.edges
 WHERE id = '592adf3d-d223-46f2-a479-ed688c989a2f';

-- Shard 08 E-4 (Sub-shape A): computational_theory_of_mind >
-- turing_test. The Turing Test (1950) is a concrete behavioral
-- criterion requiring no metaphysical framework; CTM (1960s-70s) is
-- a later metaphysical thesis. Intro philosophy-of-mind textbooks
-- (Kim, Crane, Heil) introduce the Turing Test first as the
-- historical/motivational entry point.
DELETE FROM public.edges
 WHERE id = 'ad62e0e4-7098-46cf-82dc-f2af314eed0b';

-- ============================================================
-- 7 INSERTs of the pedagogically-canonical direction.
-- Fresh UUIDs (gen_random_uuid() default), fresh provenance, and
-- evidence carrying the census sub-shape rationale plus the original
-- UUID for traceability across the DELETE.
-- ============================================================

INSERT INTO public.edges
  (source_id, target_id, edge_type, weight, confidence, provenance,
   graph_version_added, evidence)
VALUES
  -- Sub-shape B (shard 01 E-5)
  ('type_b_materialism',
   'phenomenal_concept_strategy',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 01 E-5, Sub-shape B). The phenomenal-concept strategy is the explanatory machinery deployed in defense of type-B materialism; the strategy presupposes the position it serves. Original edge d17a5b8c-d860-4d51-a399-07af73871218 (phenomenal_concept_strategy > type_b_materialism, graph_version_added=12) deleted in this migration.'),
  -- Sub-shape C (shard 01 E-24)
  ('axiom_mathematical',
   'set_mathematical',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 01 E-24, Sub-shape C). Axioms of geometry and arithmetic predate and are independent of set theory; axiomatic set theory presupposes the notion of an axiom. Original edge b8ee8fa0-0547-4f89-9448-52514c930094 (set_mathematical > axiom_mathematical, graph_version_added=15) deleted in this migration.'),
  -- Sub-shape A (shard 01 E-26)
  ('knowledge',
   'knowledge_how',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 01 E-26, Sub-shape A). Knowledge is the genus; Knowledge-How is the specialized species — Ryle''s knowledge-how vs knowledge-that distinction is drawn against the backdrop of knowledge in general. Original edge 71caae36-41e7-4171-9bc3-55b14f8ad1b6 (knowledge_how > knowledge, graph_version_added=2) deleted in this migration.'),
  -- Sub-shape A (shard 02 E-15)
  ('hedonism',
   'utilitarianism',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 02 E-15, Sub-shape A). Hedonism is a constituent axiology of classical (Benthamite/Millian) utilitarianism, not a downstream consequence; hedonism is intelligible on its own without utilitarianism. Original edge aa9df59f-2f78-4a53-9690-5225f5b99f80 (utilitarianism > hedonism, graph_version_added=7) deleted in this migration.'),
  -- Sub-shape A (shard 03 E-14)
  ('temporal_parts',
   'perdurantism',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 03 E-14, Sub-shape A). Perdurantism is defined in terms of temporal parts — the view that objects persist by having temporal parts (4D worms); the constituent notion must be grasped before the theory. Original edge cd9b6148-191f-4ca0-84c7-9841e38b406f (perdurantism > temporal_parts, graph_version_added=4) deleted in this migration.'),
  -- Sub-shape B (shard 05 E-7)
  ('philosophical_zombie',
   'property_dualism',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 05 E-7, Sub-shape B). The zombie thought experiment is the intuition pump that motivates property dualism (Chalmers''s conceivability argument). Consistent with migration 0062''s precedent flipping the structurally-identical property_dualism > knowledge_argument pair. Original edge 592adf3d-d223-46f2-a479-ed688c989a2f (property_dualism > philosophical_zombie, graph_version_added=12) deleted in this migration.'),
  -- Sub-shape A (shard 08 E-4)
  ('turing_test',
   'computational_theory_of_mind',
   'pedagogical_prerequisite',
   1.0, 1.0,
   'qa_census_disposition_s_0183',
   16,
   'QA census S-0182 Reversed (shard 08 E-4, Sub-shape A). The Turing Test (1950) is a concrete behavioral criterion requiring no metaphysical framework; CTM (1960s-70s) is a later metaphysical thesis. Intro philosophy-of-mind textbooks (Kim, Crane, Heil) introduce the Turing Test first as the historical/motivational entry point. Original edge ad62e0e4-7098-46cf-82dc-f2af314eed0b (computational_theory_of_mind > turing_test, graph_version_added=10) deleted in this migration.');

COMMIT;
