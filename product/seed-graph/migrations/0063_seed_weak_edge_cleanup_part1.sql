-- Migration: 0063_seed_weak_edge_cleanup_part1
-- Purpose: Third Phase-5 production-audit follow-up migration. Cleanup
--   pass over weak / parallel-edge / shortcut findings per S-0122
--   findings report §"Weak / parallel-edge / shortcut findings" and
--   the Disposition matrix. Two operations:
--   (A) PRUNE 4 edges where the more-proximate canonical prerequisite
--       already exists in the graph and the flagged edge is redundant
--       or a long-distance shortcut: CB-E-5
--       (bivalence_principle → paraconsistent_logic), CB-E-27
--       (expected_value → social_contract_theory), MET-E-10
--       (time → mctaggarts_paradox), LOG-E-7
--       (conditional_logic → chisholm_paradox).
--   (B) ANNOTATE 5 edges with retain-with-annotation disposition —
--       the species-level edge captures a real conceptual alliance
--       worth retaining alongside the broader genus-level prereq;
--       evidence column populated with the alliance/dialectic
--       rationale: CB-E-67 (physicalism → reductionism_in_science),
--       ETH-E-17 (virtue_ethics → moral_particularism), ETH-E-20
--       (moral_realism → moral_epistemology), EPI-E-2
--       (expertise → epistemic_dependence), EPI-E-20
--       (bayesian_epistemology → dutch_book_argument).
--
--   Issue #61. The 9 dispositions in this migration are all from the
--   audit's "weak/parallel-edge/shortcut" verdict category — distinct
--   from the "defensible-with-annotation" findings handled by 0064
--   (Issue #63), which involves edges where the pedagogical-prereq
--   framing is supportable but encodes a specific dialectical or
--   metaontological commitment.
--
--   The audit's empirical-fortification pass (S-0122) corroborated
--   most prune verdicts via SEP forward-cross-reference absence;
--   each annotate retention is justified by a SEP-recognized
--   alliance or pressure that the broader genus-level prereq does
--   not encode.
-- Loads tables: public.edges (4 DELETEs + 5 UPDATEs; no INSERTs, no DDL).
-- Preconditions:
--   * 0061 + 0062 (and revert) applied (graph is in post-flip state
--     with 17 historical_influence + 519 pedagogical_prerequisite =
--     536 total edges).
--   * All 4 prune-pairs exist as pedagogical_prerequisite (verified
--     in S-0123 plan-mode pre-apply snapshot).
--   * All 5 annotate-pairs exist as pedagogical_prerequisite with
--     evidence column NULL (verified in pre-apply snapshot).
-- Postconditions:
--   * 4 rows DELETED from public.edges (the prune set).
--   * 5 rows UPDATED in public.edges with evidence column populated
--     (the annotate set); edge_type, source_id, target_id, and
--     other fields preserved.
--   * Total pedagogical_prerequisite edges: 519 - 4 = 515.
--   * Total historical_influence edges: 17 (unchanged).
--   * Total edges: 536 - 4 = 532.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.edges WHERE (source_id, target_id) IN (('bivalence_principle','paraconsistent_logic'),('expected_value','social_contract_theory'),('time','mctaggarts_paradox'),('conditional_logic','chisholm_paradox')) :: 0
--   SELECT count(*)::int FROM public.edges WHERE evidence IS NOT NULL AND edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('physicalism','reductionism_in_science'),('virtue_ethics','moral_particularism'),('moral_realism','moral_epistemology'),('expertise','epistemic_dependence'),('bayesian_epistemology','dutch_book_argument')) :: 5
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 515
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially: DELETEs reduce row counts; UPDATEs touch only
--     evidence column.
--   * No new nodes inserted. No new edges inserted.
--   * Cycle detection: validate.py's Kosaraju SCC check post-apply
--     verifies the prunes do not introduce cycles. Pruning a weak
--     edge in favor of a more-proximate prereq path cannot introduce
--     a cycle — it removes one path between two nodes; the remaining
--     paths are existing canonical-prereq paths.
-- Non-responsibilities:
--   * Does not flip direction (those are 0062).
--   * Does not retype edge_type (those are 0061).
--   * Does not annotate edges with the "defensible-with-annotation"
--     verdict (those are 0064).
--   * Does not modify edges outside the 9-pair scope (4 prunes + 5
--     annotates).
--   * Does not increment public.settings.graph_version.
-- Cross-cutting decisions:
--   * Prune-vs-annotate adjudication: per S-0122 closeout, the
--     decision rule is "prune when the more-proximate canonical
--     prereq is already in graph and the weak edge is redundant or
--     a long-distance shortcut; retain-with-annotation when the
--     species-level edge captures a real alliance or pressure the
--     broader genus-level prereq does not encode."
--   * Evidence backfill on annotates: each UPDATE populates the
--     evidence column with a 1-3 sentence alliance/pressure
--     rationale extracted from the audit's verdict reasoning.
--     Closes one face of the universal-null evidence-field gap
--     (broader cleanup tracked at Issue #62).
-- Source citations:
--   * Findings report:
--     engine/build_readiness/phase_5_production_audit_findings.md
--     §"Weak / parallel-edge / shortcut findings" + Disposition
--     matrix.
--   * Audit evidence files:
--     phase_5_production_audit_evidence/crossbridges.md (CB-E-5,
--       CB-E-27, CB-E-67)
--     phase_5_production_audit_evidence/metaphysics.md (MET-E-10)
--     phase_5_production_audit_evidence/logic.md (LOG-E-7)
--     phase_5_production_audit_evidence/ethics.md (ETH-E-17,
--       ETH-E-20)
--     phase_5_production_audit_evidence/epistemology.md (EPI-E-2,
--       EPI-E-20)
--   * GitHub Issue #61: weak-edge cleanup filing record.
-- Idempotency:
--   * Not idempotent. Re-applying after the first apply would DELETE
--     0 rows (the targeted edges no longer exist) and UPDATE 0 rows
--     (the WHERE clauses match a state that has already been
--     replaced — but the UPDATE still finds rows by source/target).
--     Actually the UPDATEs would be idempotent (re-running would
--     re-set evidence to the same string). The DELETEs are
--     idempotent in effect (nothing to delete); the UPDATEs are
--     idempotent in operation. Wrapper's exit-6 gate is the
--     canonical re-fire defense regardless.
-- Rollback:
--   BEGIN;
--   -- Restore the 4 deleted edges (manual data; original
--   -- graph_version_added values preserved):
--   INSERT INTO public.edges (source_id, target_id, edge_type, weight, provenance, confidence, evidence, graph_version_added)
--     VALUES
--     ('bivalence_principle','paraconsistent_logic','pedagogical_prerequisite',1.0,'ai-seed',1.0,NULL,16),
--     ('expected_value','social_contract_theory','pedagogical_prerequisite',1.0,'ai-seed',1.0,NULL,16),
--     ('time','mctaggarts_paradox','pedagogical_prerequisite',1.0,'ai-seed',1.0,NULL,?),  -- check originating migration for graph_version
--     ('conditional_logic','chisholm_paradox','pedagogical_prerequisite',1.0,'ai-seed',1.0,NULL,?);
--   -- Clear evidence backfills:
--   UPDATE public.edges SET evidence = NULL WHERE (source_id, target_id) IN
--     (('physicalism','reductionism_in_science'),('virtue_ethics','moral_particularism'),
--      ('moral_realism','moral_epistemology'),('expertise','epistemic_dependence'),
--      ('bayesian_epistemology','dutch_book_argument'))
--     AND edge_type='pedagogical_prerequisite';
--   COMMIT;
-- Dependencies:
--   * Hard: 0002, 0003 (schema). Originating migrations for the 9
--     affected edges (0011, 0016, 0020, 0030, 0036, 0046, 0060, 0090).
--     0061, 0062 (preceding follow-up migrations; baseline pp count = 519).
--   * Soft: ROUTING.md (per-session narrative).
-- Related:
--   * engine/build_readiness/phase_5_production_audit_findings.md
--     §"Weak / parallel-edge / shortcut findings";
--   * GitHub Issue #61;
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md;
--   * engine/operations/migration-discipline.md Layer 2.5.

BEGIN;

-- ============================================================
-- (A) PRUNES (4 DELETEs).
-- ============================================================

-- CB-E-5: bivalence_principle → paraconsistent_logic
-- More proximate prereq is the classical principle of explosion (via
-- classical_logic), not bivalence specifically; some paraconsistent
-- systems reject bivalence while others keep it.
DELETE FROM public.edges
 WHERE source_id = 'bivalence_principle' AND target_id = 'paraconsistent_logic'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-27: expected_value → social_contract_theory
-- Classical social contract theorists (Hobbes, Locke, Rousseau) do
-- not use expected-value reasoning; students can grasp the position
-- fully without decision-theoretic formalism.
DELETE FROM public.edges
 WHERE source_id = 'expected_value' AND target_id = 'social_contract_theory'
   AND edge_type = 'pedagogical_prerequisite';

-- MET-E-10: time → mctaggarts_paradox
-- Long-distance shortcut over the more proximate path:
-- time → a_theory_of_time → mctaggarts_paradox (already in graph).
DELETE FROM public.edges
 WHERE source_id = 'time' AND target_id = 'mctaggarts_paradox'
   AND edge_type = 'pedagogical_prerequisite';

-- LOG-E-7: conditional_logic → chisholm_paradox
-- The bare Chisholm paradox can be stated using just standard deontic
-- logic + material conditional; conditional_logic illuminates the
-- response literature (Hansson 1969, Belnap-Horty) but isn't strictly
-- required.
DELETE FROM public.edges
 WHERE source_id = 'conditional_logic' AND target_id = 'chisholm_paradox'
   AND edge_type = 'pedagogical_prerequisite';

-- ============================================================
-- (B) RETAIN-WITH-ANNOTATION (5 evidence backfill UPDATEs).
-- ============================================================

-- CB-E-67: physicalism → reductionism_in_science
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Physicalism commits to the doctrine that every property is either physical or grounded in physical properties; reductionism_in_science is one central strategy for implementing that commitment across domains.'
 WHERE source_id = 'physicalism' AND target_id = 'reductionism_in_science'
   AND edge_type = 'pedagogical_prerequisite';

-- ETH-E-17: virtue_ethics → moral_particularism
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Virtue ethics''s emphasis on practical wisdom (phronesis) and attention to particularity of character encodes a commitment to the particularist rejection of universal moral rules in favor of context-sensitive judgment.'
 WHERE source_id = 'virtue_ethics' AND target_id = 'moral_particularism'
   AND edge_type = 'pedagogical_prerequisite';

-- ETH-E-20: moral_realism → moral_epistemology
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: If moral properties are real (as realism claims), the question arises how we know them; realism frames the epistemic challenge that moral_epistemology addresses as a specific dialectical position.'
 WHERE source_id = 'moral_realism' AND target_id = 'moral_epistemology'
   AND edge_type = 'pedagogical_prerequisite';

-- EPI-E-2: expertise → epistemic_dependence
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Expertise is one paradigm mode of epistemic dependence (the asymmetric layperson-to-expert form); it exemplifies the broader social-epistemological phenomenon of dependence on others'' epistemic states.'
 WHERE source_id = 'expertise' AND target_id = 'epistemic_dependence'
   AND edge_type = 'pedagogical_prerequisite';

-- EPI-E-20: bayesian_epistemology → dutch_book_argument
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Dutch book arguments provide the canonical pragmatic motivation for Bayesian probabilism (agents violating probability axioms are exploitable); DBA is the foundational justification internal to Bayesian doctrine.'
 WHERE source_id = 'bayesian_epistemology' AND target_id = 'dutch_book_argument'
   AND edge_type = 'pedagogical_prerequisite';

COMMIT;
