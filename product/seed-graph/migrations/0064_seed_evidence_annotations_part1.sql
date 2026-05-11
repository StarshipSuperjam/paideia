-- Migration: 0064_seed_evidence_annotations_part1
-- Purpose: Fourth Phase-5 production-audit follow-up migration. Backfill
--   evidence column on 7 edges verdicted defensible-with-annotation
--   per S-0122 findings report Disposition matrix. Each edge encodes
--   a specific dialectical / metaontological / framework commitment
--   the broader genus-level prereq does not capture; the
--   pedagogical-prereq framing is supportable but warrants explicit
--   annotation rather than NULL evidence. Issue #63.
--
--   The 7 annotations:
--   - MET-E-3 modality → essence_metaphysical (modality supplies the
--     conceptual apparatus in which contemporary essentialism is
--     articulated)
--   - MET-E-12 abstract_object → possible_worlds (possible worlds
--     typically construed as abstract objects; abstract-object
--     framework is conceptually foundational for semanticist
--     approaches)
--   - MIN-E-12 supervenience_mental → mental_causation
--     (supervenience is the Kim-style apparatus for the modern
--     mental-causation puzzle; the puzzle predates the apparatus)
--   - LAN-E-3 speech_act → presupposition (presuppositions sit
--     within speech-act pragmatics; depend on illocutionary-act
--     structure)
--   - LAN-E-5 causal_theory_of_reference → rigid_designator (rigid
--     designators paradigmatically explained via causal-historical
--     accounts; designator concept motivated by causal-reference
--     semantics)
--   - POL-E-6 social_contract_theory → political_legitimacy (the
--     historical answer-family to the legitimacy question; canonical
--     SEP framing inverts the order, but the migration treats the
--     tradition as self-contained machinery)
--   - AES-E-3 fictional_truth → metaphor (Walton's make-believe
--     framework extends to metaphor; fictional-truth apparatus
--     supplies a thread for some contemporary metaphor treatments,
--     though canonical SEP order inverts)
--
--   Distinct from 0063's "retain-with-annotation" set (5 edges in
--   the weak/parallel-edge verdict category). 0064's set is from
--   the "defensible-with-annotation" verdict category — the
--   pedagogical-prereq framing is genuinely defensible (not just
--   weak-but-retained-as-alliance) and the annotation captures the
--   specific commitment.
--
--   Each UPDATE populates the evidence column with a 1-3 sentence
--   rationale extracted from the audit's verdict reasoning. Closes
--   one face of the universal-null evidence-field gap (broader
--   cleanup tracked at Issue #62).
-- Loads tables: public.edges (7 UPDATEs; no INSERTs, no DELETEs, no DDL).
-- Preconditions:
--   * 0061 + 0062 + revert + 0063 applied (graph is in post-cleanup
--     state with 17 historical_influence + 515 pedagogical_prerequisite
--     = 532 total edges).
--   * All 7 annotate-pairs exist as pedagogical_prerequisite with
--     evidence column NULL (verified in S-0123 plan-mode pre-apply
--     snapshot).
-- Postconditions:
--   * 7 rows in public.edges have evidence column populated with
--     the audit's defensible-with-annotation rationale per finding;
--     edge_type, source_id, target_id, and other fields preserved.
--   * Total pedagogical_prerequisite edges: 515 (unchanged — UPDATE
--     does not change row count).
--   * Total historical_influence edges: 17 (unchanged).
--   * Total edges: 532 (unchanged).
--   * Cumulative evidence non-NULL count across 0061+0062+0063+0064:
--     17 (0061 retypings) + 14 (0062 flips, post-revert)
--     + 5 (0063 annotates) + 7 (0064 annotates) = 43 edges with
--     non-NULL evidence (the CB-E-63 row also has evidence from
--     the 0062 revert migration, bringing the total to 44).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.edges WHERE evidence IS NOT NULL AND edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('modality','essence_metaphysical'),('abstract_object','possible_worlds'),('supervenience_mental','mental_causation'),('speech_act','presupposition'),('causal_theory_of_reference','rigid_designator'),('social_contract_theory','political_legitimacy'),('fictional_truth','metaphor')) :: 7
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 515
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially: UPDATEs touch only evidence column.
--   * No new nodes inserted. No new edges inserted. No edges deleted.
--   * Cycle detection: validate.py's Kosaraju SCC check unchanged
--     by these UPDATEs (graph topology unchanged; only evidence
--     metadata).
-- Non-responsibilities:
--   * Does not flip direction (0062), retype edge_type (0061), or
--     prune edges (0063).
--   * Does not annotate edges with the "weak/retain-with-annotation"
--     verdict (those are 0063).
--   * Does not modify edges outside the 7-pair scope.
--   * Does not increment public.settings.graph_version.
-- Cross-cutting decisions:
--   * Defensible-with-annotation discipline: per S-0122 closeout,
--     this verdict category captures edges where the
--     pedagogical-prereq framing encodes a specific commitment
--     (dialectical position, metaontological choice, framework
--     application) that the broader genus-level prereq does not
--     name. Annotation makes the commitment visible in the evidence
--     column without retiring or re-typing the edge.
--   * Evidence backfill scope: 7 specific defensible-with-annotation
--     cases. The broader universal-null evidence-field cleanup
--     (Issue #62 validator soft-warn) is a separate work item.
-- Source citations:
--   * Findings report:
--     engine/build_readiness/phase_5_production_audit_findings.md
--     §"Disposition matrix" (rows MET-E-3, MET-E-12, MIN-E-12,
--     LAN-E-3, LAN-E-5, POL-E-6, AES-E-3 — all flagged
--     defensible/retain with documentation label).
--   * Audit evidence files:
--     phase_5_production_audit_evidence/metaphysics.md (MET-E-3,
--       MET-E-12)
--     phase_5_production_audit_evidence/mind.md (MIN-E-12)
--     phase_5_production_audit_evidence/language.md (LAN-E-3,
--       LAN-E-5)
--     phase_5_production_audit_evidence/political.md (POL-E-6)
--     phase_5_production_audit_evidence/aesthetics.md (AES-E-3)
--   * GitHub Issue #63: defensible-with-annotation evidence-backfill
--     filing record.
-- Idempotency:
--   * Idempotent in operation. Re-running would re-set evidence to
--     the same string on each of 7 rows; UPDATEs match by
--     (source_id, target_id, edge_type) which UPDATE does not
--     change. Wrapper's exit-6 gate is the canonical re-fire defense.
-- Rollback:
--   BEGIN;
--   UPDATE public.edges SET evidence = NULL
--    WHERE (source_id, target_id) IN
--          (('modality','essence_metaphysical'),
--           ('abstract_object','possible_worlds'),
--           ('supervenience_mental','mental_causation'),
--           ('speech_act','presupposition'),
--           ('causal_theory_of_reference','rigid_designator'),
--           ('social_contract_theory','political_legitimacy'),
--           ('fictional_truth','metaphor'))
--      AND edge_type = 'pedagogical_prerequisite';
--   COMMIT;
-- Dependencies:
--   * Hard: 0002, 0003 (schema). Originating migrations for the 7
--     affected edges (0030, 0036, 0046, 0070, 0100, 0110).
--     0061, 0062, 0063 (preceding follow-ups; baseline pp count = 515).
--   * Soft: ROUTING.md (per-session narrative).
-- Related:
--   * engine/build_readiness/phase_5_production_audit_findings.md
--     §"Disposition matrix";
--   * GitHub Issue #63;
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md;
--   * engine/operations/migration-discipline.md Layer 2.5.

BEGIN;

-- MET-E-3: modality → essence_metaphysical
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Modern essence metaphysics (Fine, Lowe) is developed partly through modal frameworks (essence as counterfactual-robustness); modality supplies the conceptual apparatus in which contemporary essentialism is articulated.'
 WHERE source_id = 'modality' AND target_id = 'essence_metaphysical'
   AND edge_type = 'pedagogical_prerequisite';

-- MET-E-12: abstract_object → possible_worlds
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Possible worlds are typically construed as abstract objects (structured or unstructured propositions; maximally consistent sets of propositions; properties of properties); the abstract-object framework is conceptually foundational for semanticist approaches.'
 WHERE source_id = 'abstract_object' AND target_id = 'possible_worlds'
   AND edge_type = 'pedagogical_prerequisite';

-- MIN-E-12: supervenience_mental → mental_causation
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: The basic puzzle of mental causation predates supervenience apparatus (Princess Elisabeth 1643); supervenience is one sophisticated framework (Kim-style) for formulating the modern version, but the puzzle is conceptually prior.'
 WHERE source_id = 'supervenience_mental' AND target_id = 'mental_causation'
   AND edge_type = 'pedagogical_prerequisite';

-- LAN-E-3: speech_act → presupposition
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Presuppositions are a sub-topic in speech-act pragmatics; the notion of what an utterance presupposes depends on understanding the illocutionary-act structure of utterances (Searle F(P) framework).'
 WHERE source_id = 'speech_act' AND target_id = 'presupposition'
   AND edge_type = 'pedagogical_prerequisite';

-- LAN-E-5: causal_theory_of_reference → rigid_designator
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Rigid designators are paradigmatically explained via causal-historical accounts of reference (Kripke 1972, Putnam); the designator concept is motivated by and interpreted through causal-reference semantics.'
 WHERE source_id = 'causal_theory_of_reference' AND target_id = 'rigid_designator'
   AND edge_type = 'pedagogical_prerequisite';

-- POL-E-6: social_contract_theory → political_legitimacy
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Social contract theory is the historical answer-family to the legitimacy question; the canonical SEP framing runs question-then-answers, but the migration treats the tradition as self-contained machinery that applies to legitimacy.'
 WHERE source_id = 'social_contract_theory' AND target_id = 'political_legitimacy'
   AND edge_type = 'pedagogical_prerequisite';

-- AES-E-3: fictional_truth → metaphor
UPDATE public.edges
   SET evidence = 'Per S-0122 audit: Walton''s make-believe framework extends to metaphor (1993 Metaphor and Prop Oriented Make-Believe); fictional-truth apparatus supplies a theoretical thread for certain contemporary metaphor treatments, though canonical SEP metaphor entry runs the opposite direction.'
 WHERE source_id = 'fictional_truth' AND target_id = 'metaphor'
   AND edge_type = 'pedagogical_prerequisite';

COMMIT;
