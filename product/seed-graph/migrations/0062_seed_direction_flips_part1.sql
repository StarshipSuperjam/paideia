-- Migration: 0062_seed_direction_flips_part1
-- Purpose: Second Phase-5 production-audit follow-up migration. Flip
--   direction on 15 pedagogical_prerequisite edges whose authored
--   direction is reversed from the SEP-canonical pedagogical-dependency
--   direction. Per S-0122 closeout findings report
--   §"Reversal cluster" + §"Direction-of-development reversal patterns".
--   Issue #59.
--
--   The 15 flips break into two structural sub-groups:
--   (A) Cross-bridges B reversal cluster (8 edges, CB-E-47, CB-E-54,
--       CB-E-55, CB-E-56, CB-E-63, CB-E-65, CB-E-69, CB-E-70). Five of
--       the eight (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70) are
--       contradicted by the migration's own teaching_notes
--       pedagogical-warrant prose, strongly suggesting a mechanical
--       authoring slip (source-target field swap during VALUES list
--       editing in 0060_seed_crossbridges_part1.sql).
--   (B) Within-subdomain direction-of-development reversals (7 edges,
--       distributed across 5 subdomains): EPI-E-13, ETH-E-16, MIN-E-14,
--       MIN-E-17, LAN-E-2, LAN-E-10, SCI-E-4. Patterns:
--       argument-vs-position direction (the argument that supports a
--       position should be prerequisite to the position, not the
--       reverse); developmental-arc reversals (the historical seed
--       observation precedes the systematized framework); tools-vs-
--       position reversals (the formal tool precedes the philosophical
--       thesis built on it).
--
--   The audit's empirical-fortification pass (S-0122) corroborated 11
--   of 15 via SEP forward-cross-reference absence; the remaining 4
--   have forward cross-references present but the verdicts'
--   directional-argument reasoning stands (cross-reference presence
--   is necessary but not sufficient to refute direction).
--
--   Implementation choice: UPDATE in place swapping source_id and
--   target_id (rather than DELETE + INSERT). Preserves the original
--   UUID id, created_at, edge_type='pedagogical_prerequisite', and
--   graph_version_added (16 for cross-bridges; the originating-
--   migration value for within-subdomain edges). UPDATE is safe under
--   the UNIQUE (source_id, target_id, edge_type) constraint because
--   pre-apply audit (S-0123 plan-mode snapshot via
--   validate.py --export-snapshot) confirmed zero canonical-direction
--   collisions across all 15 (NEW source, NEW target) pairs.
--
--   Each UPDATE also populates the evidence column with the audit's
--   directional-correction reasoning. This closes one face of the
--   universal-null evidence gap that
--   phase_5_audit_system_input.md Proposal 1 (Issue #62) flagged
--   graph-wide; the broader cleanup is a separate validator soft-warn
--   work item.
-- Loads tables: public.edges (15 UPDATEs; no INSERTs, no DELETEs, no DDL).
-- Preconditions:
--   * 0061 applied (the 17 retypings landed; total
--     pedagogical_prerequisite count = 519 pre-apply).
--   * All 15 (OLD source, OLD target) pairs exist as
--     pedagogical_prerequisite (verified via pre-apply snapshot).
--   * All 15 (NEW source, NEW target) flipped pairs do NOT exist as
--     pedagogical_prerequisite (verified via pre-apply snapshot — zero
--     canonical-direction collisions).
-- Postconditions:
--   * 15 rows in public.edges have new (source_id, target_id) values
--     reflecting the corrected direction; edge_type and other fields
--     preserved; evidence column populated with the audit's
--     directional-correction reasoning.
--   * 0 rows remain in public.edges with the OLD (source_id, target_id)
--     pairs and edge_type='pedagogical_prerequisite'.
--   * Total pedagogical_prerequisite edges: 519 (unchanged — UPDATE
--     swaps direction, count unchanged).
--   * Total historical_influence edges: 17 (unchanged from 0061).
-- Subsequent revert (S-0123 user adjudication):
--   * The CB-E-63 flip (proposition → propositional_attitude) closed a
--     pre-existing 4-node Kosaraju cycle through the audit-accepted edge
--     propositional_attitude → intentionality (from 0040 mind seed). The
--     cycle was detected by validate.py's pre-commit graph-audit
--     hard-fail. Per S-0123 user adjudication (AskUserQuestion response
--     "Revert CB-E-63 only"), the CB-E-63 flip is reverted via
--     0062_seed_direction_flips_revert_part1.sql, applied immediately
--     after this migration. Net effect at session close: 14 of 15 flips
--     stand; CB-E-63 is back in original direction
--     (propositional_attitude → proposition); deferred for Phase 6
--     audit re-scope of the 4-node cluster (filed as a follow-up
--     GitHub Issue).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('epistemic_justification','propositional_attitude'),('formal_epistemology','modal_logic'),('formal_epistemology','kripke_semantics'),('epistemic_closure','modal_logic'),('propositional_attitude','proposition'),('causal_theory_of_mental_content','causal_theory_of_reference'),('motivational_internalism','propositional_attitude'),('justice','morality'),('problem_of_induction','pyrrhonian_skepticism'),('animal_ethics','sentientism'),('hard_problem_of_consciousness','explanatory_gap'),('property_dualism','knowledge_argument'),('speech_act','performative_utterance'),('deflationary_theory_of_truth','tarskis_t_schema'),('paradigm','theory_ladenness_of_observation')) :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('propositional_attitude','epistemic_justification'),('modal_logic','formal_epistemology'),('kripke_semantics','formal_epistemology'),('modal_logic','epistemic_closure'),('proposition','propositional_attitude'),('causal_theory_of_reference','causal_theory_of_mental_content'),('propositional_attitude','motivational_internalism'),('morality','justice'),('pyrrhonian_skepticism','problem_of_induction'),('sentientism','animal_ethics'),('explanatory_gap','hard_problem_of_consciousness'),('knowledge_argument','property_dualism'),('performative_utterance','speech_act'),('tarskis_t_schema','deflationary_theory_of_truth'),('theory_ladenness_of_observation','paradigm')) :: 15
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 519
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     each UPDATE changes (s_old, t_old, 'pedagogical_prerequisite') to
--     (s_new, t_new, 'pedagogical_prerequisite') = (t_old, s_old,
--     'pedagogical_prerequisite'). The new triple is unique because
--     no canonical-direction edge exists for any of the 15 flipped
--     pairs pre-apply (verified in S-0123 plan-mode snapshot).
--   * No new nodes inserted. No new edges inserted. No edges deleted.
--   * Cycle detection: validate.py's Kosaraju SCC check will re-run
--     post-apply. The 15 flips do not introduce cycles by construction
--     because (a) each flip is a directional correction toward
--     SEP-canonical orientation; (b) the flipped direction is the one
--     the audit found justifies-pedagogical-dependency, so post-flip
--     direction is the canonical DAG direction the cross-bridges and
--     within-subdomain authoring intended in spirit.
-- Non-responsibilities:
--   * Does not author new edges or nodes; does not retype edge_type.
--   * Does not modify edges outside the 15-pair flip set.
--   * Does not increment public.settings.graph_version.
--   * Does not flip direction on edges with verdicts other than
--     "reversed" (e.g., "weak", "defensible") — those are 0063 and
--     0064 dispositions.
-- Cross-cutting decisions:
--   * Direction-correction posture: the audit treats the flipped
--     direction as canonical pedagogical dependency; the original
--     authored direction is recorded in the migration's evidence
--     column for traceability. The teaching layer (Phase 7) consumes
--     post-flip direction; the in-flight learner mastery model
--     (Phase 6) operates on post-flip topology because no learner
--     data exists pre-deployment.
--   * Evidence backfill: each UPDATE populates the evidence column
--     with a 1-3 sentence rationale for the flip extracted from the
--     S-0122 audit findings.
-- Source citations:
--   * Findings report:
--     engine/build_readiness/phase_5_production_audit_findings.md
--     §"Reversal cluster" (cross-bridges B; 8 edges) +
--     §"Direction-of-development reversal patterns" (within-subdomain;
--     7 edges).
--   * Audit evidence files (per finding ID):
--     phase_5_production_audit_evidence/crossbridges.md (CB-E-47,
--       CB-E-54, CB-E-55, CB-E-56, CB-E-63, CB-E-65, CB-E-69, CB-E-70)
--     phase_5_production_audit_evidence/epistemology.md (EPI-E-13)
--     phase_5_production_audit_evidence/ethics.md (ETH-E-16)
--     phase_5_production_audit_evidence/mind.md (MIN-E-14, MIN-E-17)
--     phase_5_production_audit_evidence/language.md (LAN-E-2, LAN-E-10)
--     phase_5_production_audit_evidence/science.md (SCI-E-4)
--   * Original migrations whose teaching_notes prose informs the
--     evidence backfill: 0011, 0016, 0026, 0040, 0046, 0060, 0070,
--     0080, 0090, 0100, 0110.
--   * GitHub Issue #59: direction-flip filing record.
--   * Numeric prefix: 0062 occupies the cross-bridges sub-range
--     (0060-0069) reserved-but-unused slot; sibling to 0061 retyping.
-- Idempotency:
--   * Not idempotent. Re-applying after the first apply would update 0
--     rows on each UPDATE (no rows match the WHERE clause once the
--     flip has landed); no constraint violation. The wrapper's exit-6
--     gate is the canonical re-fire defense.
-- Rollback:
--   BEGIN;
--   -- Reverse each UPDATE by swapping source_id and target_id back.
--   -- Order does not matter (independent updates).
--   UPDATE public.edges SET source_id='epistemic_justification', target_id='propositional_attitude', evidence=NULL WHERE source_id='propositional_attitude' AND target_id='epistemic_justification' AND edge_type='pedagogical_prerequisite';
--   -- ... (14 more reverse-flip UPDATEs)
--   COMMIT;
-- Dependencies:
--   * Hard: 0002, 0003 (schema). 0011, 0016, 0026, 0040, 0046, 0060,
--     0070, 0080, 0090, 0100, 0110 (originating subdomain seedings).
--     0061 (retypings landed; pre-apply pp count baseline = 519).
--   * Soft: ROUTING.md (per-session narrative appended in same commit).
-- Related:
--   * engine/build_readiness/phase_5_production_audit_findings.md
--     §"Reversal cluster" + §"Direction-of-development reversal
--     patterns";
--   * GitHub Issue #59;
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--     (apply via wrapper — ninth load-bearing exercise);
--   * engine/operations/migration-discipline.md Layer 2.5;
--   * product/adr/0001-pedagogical-edges-not-historical.md
--     (pedagogical edge direction discipline).

BEGIN;

-- ============================================================
-- (A) Cross-bridges B reversal cluster (8 flips: CB-E-47, CB-E-54,
--     CB-E-55, CB-E-56, CB-E-63, CB-E-65, CB-E-69, CB-E-70).
-- ============================================================

-- CB-E-47: justification is a PROPERTY of propositional attitudes;
-- bearers (attitudes) are conceptually prior. Pedagogical direction:
-- propositional_attitude → epistemic_justification.
UPDATE public.edges
   SET source_id = 'propositional_attitude',
       target_id = 'epistemic_justification',
       evidence  = 'Per S-0122 audit: The correction: justification is a PROPERTY of propositional attitudes; bearers (attitudes) are conceptually prior. Pedagogical direction should run propositional_attitude > epistemic_justification (properties presuppose bearers).'
 WHERE source_id = 'epistemic_justification' AND target_id = 'propositional_attitude'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-54: modal logic is the foundational formal apparatus; formal
-- epistemology USES modal logic (particularly epistemic logic) as a
-- tool. Direction: modal_logic → formal_epistemology.
UPDATE public.edges
   SET source_id = 'modal_logic',
       target_id = 'formal_epistemology',
       evidence  = 'Per S-0122 audit: The correction: modal logic is the foundational formal apparatus; formal epistemology USES modal logic (particularly epistemic logic) as a tool. Direction should be modal_logic > formal_epistemology.'
 WHERE source_id = 'formal_epistemology' AND target_id = 'modal_logic'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-55: Kripke semantics is the model-theoretic framework for modal
-- logic; epistemic logic is one application. Direction: kripke_semantics
-- → formal_epistemology.
UPDATE public.edges
   SET source_id = 'kripke_semantics',
       target_id = 'formal_epistemology',
       evidence  = 'Per S-0122 audit: The correction: Kripke semantics is the model-theoretic framework for modal logic; epistemic logic is one application of that framework. Direction should be kripke_semantics > formal_epistemology.'
 WHERE source_id = 'formal_epistemology' AND target_id = 'kripke_semantics'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-56: modal logic exists independently of epistemic-closure
-- considerations and is the formal apparatus in which closure gets
-- formalized (the K axiom). Direction: modal_logic → epistemic_closure.
UPDATE public.edges
   SET source_id = 'modal_logic',
       target_id = 'epistemic_closure',
       evidence  = 'Per S-0122 audit: The correction: modal logic exists independently of epistemic-closure considerations and is the formal apparatus in which closure gets formalized (the K axiom). Direction should be modal_logic > epistemic_closure.'
 WHERE source_id = 'epistemic_closure' AND target_id = 'modal_logic'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-63: propositions are content-bearers; attitudes are relations
-- TO those contents. Propositions are conceptually prior as the
-- content that attitudes bear. Direction: proposition → propositional_attitude.
UPDATE public.edges
   SET source_id = 'proposition',
       target_id = 'propositional_attitude',
       evidence  = 'Per S-0122 audit: The correction: propositions are content-bearers; attitudes are relations TO those contents. Propositions are conceptually prior as the content that attitudes bear. Direction should be proposition > propositional_attitude.'
 WHERE source_id = 'propositional_attitude' AND target_id = 'proposition'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-65: Kripke-Putnam reference theory (1970s) predates and
-- inspired Fodor's mental-content theory (1980s). Direction:
-- causal_theory_of_reference → causal_theory_of_mental_content.
UPDATE public.edges
   SET source_id = 'causal_theory_of_reference',
       target_id = 'causal_theory_of_mental_content',
       evidence  = 'Per S-0122 audit: The correction: Kripke-Putnam reference theory (1970s) predates and inspired Fodor''s mental-content theory (1980s). Direction should be causal_theory_of_reference > causal_theory_of_mental_content.'
 WHERE source_id = 'causal_theory_of_mental_content' AND target_id = 'causal_theory_of_reference'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-69: propositional attitudes are the broader category;
-- motivational_internalism is a specific ethical position using that
-- category. Direction: propositional_attitude → motivational_internalism.
UPDATE public.edges
   SET source_id = 'propositional_attitude',
       target_id = 'motivational_internalism',
       evidence  = 'Per S-0122 audit: The correction: propositional attitudes are the broader category; motivational_internalism is a specific ethical position using that category. Direction should be propositional_attitude > motivational_internalism.'
 WHERE source_id = 'motivational_internalism' AND target_id = 'propositional_attitude'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-70: morality is the broader normative framework; political
-- justice is a domain-specific application. Direction: morality →
-- justice.
UPDATE public.edges
   SET source_id = 'morality',
       target_id = 'justice',
       evidence  = 'Per S-0122 audit: The correction: morality is the broader normative framework; political justice is a domain-specific application. Direction should be morality > justice.'
 WHERE source_id = 'justice' AND target_id = 'morality'
   AND edge_type = 'pedagogical_prerequisite';

-- ============================================================
-- (B) Within-subdomain direction-of-development reversals (7 flips:
--     EPI-E-13, ETH-E-16, MIN-E-14, MIN-E-17, LAN-E-2, LAN-E-10,
--     SCI-E-4).
-- ============================================================

-- EPI-E-13: Pyrrhonian tradition (Pyrrho, Sextus Empiricus) is
-- millennia-older than Hume's problem; the Agrippan trilemma does not
-- depend on induction-skepticism. Direction: pyrrhonian_skepticism →
-- problem_of_induction.
UPDATE public.edges
   SET source_id = 'pyrrhonian_skepticism',
       target_id = 'problem_of_induction',
       evidence  = 'Per S-0122 audit: The correction: Pyrrhonian tradition (Pyrrho, Sextus Empiricus) is millennia-older than Hume''s problem; the Agrippan trilemma does not depend on induction-skepticism. Direction should be pyrrhonian_skepticism > problem_of_induction.'
 WHERE source_id = 'problem_of_induction' AND target_id = 'pyrrhonian_skepticism'
   AND edge_type = 'pedagogical_prerequisite';

-- ETH-E-16: sentientism (Bentham, Singer) is foundational; animal
-- ethics derives FROM the sentience criterion. Direction: sentientism
-- → animal_ethics.
UPDATE public.edges
   SET source_id = 'sentientism',
       target_id = 'animal_ethics',
       evidence  = 'Per S-0122 audit: The correction: sentientism (Bentham, Singer) is foundational; animal ethics derives FROM the sentience criterion. Direction should be sentientism > animal_ethics.'
 WHERE source_id = 'animal_ethics' AND target_id = 'sentientism'
   AND edge_type = 'pedagogical_prerequisite';

-- MIN-E-14: Levine's explanatory gap (1983) precedes and motivates
-- Chalmers' hard problem (1995). Direction: explanatory_gap →
-- hard_problem_of_consciousness.
UPDATE public.edges
   SET source_id = 'explanatory_gap',
       target_id = 'hard_problem_of_consciousness',
       evidence  = 'Per S-0122 audit: The correction: Levine''s explanatory gap (1983) precedes and motivates Chalmers'' hard problem (1995). Direction should be explanatory_gap > hard_problem_of_consciousness.'
 WHERE source_id = 'hard_problem_of_consciousness' AND target_id = 'explanatory_gap'
   AND edge_type = 'pedagogical_prerequisite';

-- MIN-E-17: Jackson's knowledge argument is an argument FOR property
-- dualism; pedagogically the argument motivates the position, not
-- the reverse. Direction: knowledge_argument → property_dualism.
UPDATE public.edges
   SET source_id = 'knowledge_argument',
       target_id = 'property_dualism',
       evidence  = 'Per S-0122 audit: The correction: Jackson''s knowledge argument is an argument FOR property dualism; pedagogically the argument motivates the position, not the reverse. Direction should be knowledge_argument > property_dualism.'
 WHERE source_id = 'property_dualism' AND target_id = 'knowledge_argument'
   AND edge_type = 'pedagogical_prerequisite';

-- LAN-E-2: Austin's performatives (1955) were the seed observation
-- that motivated the generalized speech-act framework; historically
-- and pedagogically performatives come first. Direction:
-- performative_utterance → speech_act.
UPDATE public.edges
   SET source_id = 'performative_utterance',
       target_id = 'speech_act',
       evidence  = 'Per S-0122 audit: The correction: Austin''s performatives (1955) were the seed observation that motivated the generalized speech-act framework; historically and pedagogically performatives come first. Direction should be performative_utterance > speech_act.'
 WHERE source_id = 'speech_act' AND target_id = 'performative_utterance'
   AND edge_type = 'pedagogical_prerequisite';

-- LAN-E-10: deflationary theorists (Field, Horwich) appeal to
-- T-schema as a key formal tool; T-schema is the apparatus on which
-- deflationism is built. Direction: tarskis_t_schema →
-- deflationary_theory_of_truth.
UPDATE public.edges
   SET source_id = 'tarskis_t_schema',
       target_id = 'deflationary_theory_of_truth',
       evidence  = 'Per S-0122 audit: Per migration teaching notes: deflationary theorists (Field, Horwich) appeal to T-schema as a key formal tool; T-schema is the apparatus on which deflationism is built.'
 WHERE source_id = 'deflationary_theory_of_truth' AND target_id = 'tarskis_t_schema'
   AND edge_type = 'pedagogical_prerequisite';

-- SCI-E-4: Hanson articulated theory-ladenness (1958) before Kuhn
-- introduced paradigm-talk (1962); Kuhn imported and extended Hanson's
-- thesis. Direction: theory_ladenness_of_observation → paradigm.
UPDATE public.edges
   SET source_id = 'theory_ladenness_of_observation',
       target_id = 'paradigm',
       evidence  = 'Per S-0122 audit: The correction: Hanson articulated theory-ladenness (1958) before Kuhn introduced paradigm-talk (1962); Kuhn imported and extended Hanson''s thesis. Direction should be theory_ladenness_of_observation > paradigm.'
 WHERE source_id = 'paradigm' AND target_id = 'theory_ladenness_of_observation'
   AND edge_type = 'pedagogical_prerequisite';

COMMIT;
