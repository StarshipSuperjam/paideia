-- Migration: 0061_seed_historical_influence_retyping_part1
-- Purpose: First Phase-5 production-audit follow-up migration. Retype 17
--   history-terminator-source edges from edge_type='pedagogical_prerequisite'
--   to edge_type='historical_influence' per ADR 0061 product
--   (engine/build_readiness/phase_5_production_audit_findings.md
--   §"Historical genealogy cluster"). Activates first-use of the
--   historical_influence predicate (registered in v1 PREDICATE_MANIFEST.md
--   since the schema's initial draft, zero edges using it before this
--   migration). Issue #60.
--
--   The 17 retypings span three structural sub-groups identified by the
--   audit:
--   (A) Cross-bridges A3 grouping — service-domain history-terminator →
--       modern philosophy (14 edges, CB-E-28 through CB-E-43 excluding
--       defensible/sound E-37/E-40/E-44/E-45):
--       aristotelian_four_causes (4 outbound), greek_atomism (3 outbound),
--       scholasticism (2 outbound), renaissance_mechanism (2 outbound),
--       vienna_circle_logical_positivism (3 outbound).
--   (B) Within-service A3-internal historical edges (2 edges, SVC-E-2 and
--       SVC-E-3): presocratic_naturalism → aristotelian_four_causes;
--       aristotelian_four_causes → vienna_circle_logical_positivism.
--   (C) Within-mind school/movement target (1 edge, MIN-E-23):
--       consciousness → phenomenology — phenomenology being a 20th-century
--       philosophical movement (Husserl, Heidegger, Sartre,
--       Merleau-Ponty), not an atomic concept; the connection is
--       tradition-as-context, not strict pedagogical prerequisite.
--
--   The audit's empirical-fortification pass (per ADR 0059, executed at
--   S-0122 closeout) corroborated 9 of the 14 cross-bridge cases via SEP
--   forward-cross-reference absence; partial corroboration for the
--   remaining 5 (SEP entries link forward to broader-topic entries but
--   not to the specifically-claimed modern targets).
--
--   Disposition mode: RETYPE (single edge with new edge_type), not
--   DUAL-TYPE (keep pedagogical_prerequisite + add historical_influence).
--   The audit's verdict was "mis-typed: historical-not-pedagogical,"
--   meaning the pedagogical_prerequisite reading is the structural
--   error. Dual-typing would falsely imply both relations are
--   pedagogically load-bearing.
--
--   Implementation choice: UPDATE in place rather than DELETE+INSERT.
--   ADR 0061 §"Retyping migration" reads "DELETE...INSERT into
--   historical_influence_edge or whatever the schema-table name is;
--   PREDICATE_MANIFEST.md is the source of truth on table naming."
--   The schema (per 0003_edges.sql) commits a single public.edges table
--   with edge_type column and UNIQUE (source_id, target_id, edge_type) —
--   there is no per-predicate table. UPDATE in place preserves the
--   original UUID id, created_at, and graph_version_added=16 (from
--   S-0075's cross-bridges authoring), maintaining audit trail.
--
-- Loads tables: public.edges (17 UPDATEs; no INSERTs, no DELETEs, no DDL).
-- Preconditions:
--   * Phase 3 schema in place (0001-0008).
--   * 0060_seed_crossbridges_part1.sql applied at S-0075 (the 14
--     cross-bridge source edges exist with
--     edge_type='pedagogical_prerequisite', graph_version_added=16).
--   * 0050_seed_services_part1.sql applied (the 2 within-service edges
--     SVC-E-2/E-3 exist with edge_type='pedagogical_prerequisite',
--     graph_version_added=15).
--   * 0040_seed_mind_part1.sql applied (the within-mind edge MIN-E-23
--     consciousness → phenomenology exists).
--   * Pre-apply audit (S-0123 plan-mode snapshot via
--     validate.py --export-snapshot) confirmed: all 17 (source, target)
--     pairs exist as pedagogical_prerequisite; zero historical_influence
--     edges in the graph.
-- Postconditions:
--   * 17 rows in public.edges have edge_type='historical_influence'
--     (was pedagogical_prerequisite); evidence column populated with the
--     audit's verdict reasoning per finding (each evidence string
--     extracted from S-0122 audit findings + ADR 0061).
--   * 0 rows remain in public.edges with edge_type='pedagogical_prerequisite'
--     for the 17 (source, target) pairs.
--   * graph_version_added unchanged on the 17 rows (UPDATE preserves;
--     also graph_version unchanged in public.settings — no new
--     authoring; this is a retype of pre-existing edges, not new
--     edge insertion).
--   * Total pedagogical_prerequisite edges: 536 - 17 = 519.
--   * Total historical_influence edges: 0 + 17 = 17.
--   * Residue: the 7 source nodes
--     (aristotelian_four_causes, greek_atomism, scholasticism,
--     renaissance_mechanism, vienna_circle_logical_positivism,
--     presocratic_naturalism, consciousness) collectively retain 15
--     other pedagogical_prerequisite edges (32 currently outbound − 17
--     retyped) — verified via pre-apply snapshot.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment landed at S-0094.)
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'historical_influence' :: 17
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' AND (source_id, target_id) IN (('aristotelian_four_causes','causation'),('aristotelian_four_causes','essence_metaphysical'),('aristotelian_four_causes','scientific_explanation'),('aristotelian_four_causes','humean_regularity_theory'),('greek_atomism','physicalism'),('greek_atomism','reductionism_in_science'),('greek_atomism','mereological_nihilism'),('scholasticism','realism_about_universals'),('scholasticism','divine_command_theory'),('renaissance_mechanism','scientific_theory'),('renaissance_mechanism','scientific_method'),('vienna_circle_logical_positivism','falsificationism'),('vienna_circle_logical_positivism','demarcation_problem'),('vienna_circle_logical_positivism','tarskis_t_schema'),('presocratic_naturalism','aristotelian_four_causes'),('aristotelian_four_causes','vienna_circle_logical_positivism'),('consciousness','phenomenology')) :: 0
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' AND source_id IN ('aristotelian_four_causes','greek_atomism','scholasticism','renaissance_mechanism','vienna_circle_logical_positivism','presocratic_naturalism','consciousness') :: 15
--   SELECT count(*)::int FROM public.edges WHERE edge_type = 'pedagogical_prerequisite' :: 519
--   SELECT count(*)::int FROM public.edges WHERE evidence IS NOT NULL AND edge_type = 'historical_influence' :: 17
-- Invariants:
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     each retyping changes a (s, t, 'pedagogical_prerequisite') row to
--     (s, t, 'historical_influence'). The new triple is unique because
--     no historical_influence edge exists for any of the 17 pairs
--     pre-apply (verified in pre-apply snapshot).
--   * No new nodes inserted. No new edges inserted. No edges deleted.
--   * Cycle detection: historical_influence may legitimately form cycles
--     per PREDICATE_MANIFEST.md; the audit's cycle check skips this
--     predicate. Within-service SVC-E-2 + SVC-E-3 form a triangle of
--     historical_influence edges (presocratic_naturalism →
--     aristotelian_four_causes → vienna_circle_logical_positivism)
--     which is acceptable under the predicate's display-only semantics.
-- Non-responsibilities:
--   * Does not author new edges or nodes.
--   * Does not modify edges outside the 17-pair retype set.
--   * Does not modify PREDICATE_MANIFEST.md table contents
--     (historical_influence already in v1 active registry; first-use
--     narrative reflection lands in ROUTING.md per-session entry, not
--     manifest table edit).
--   * Does not flip direction, prune weak edges, or annotate evidence
--     on edges outside this scope — those are 0062, 0063, 0064.
--   * Does not increment public.settings.graph_version (UPDATE-only
--     migration; the 17 affected rows retain their original
--     graph_version_added=16 or 15 per their original migration).
-- Cross-cutting decisions:
--   * Predicate activation: historical_influence is display-only
--     (Discovery surface annotation per ADR 0034) — not consumed by
--     traversal, syllabus generation, or mastery computation per
--     PREDICATE_MANIFEST.md. ADR 0061 §"Consequences" enumerates the
--     learner-facing semantics: the 17 conceptual connections remain
--     visible to learners exploring concept neighborhoods; mastery on
--     causation is no longer gated on prior mastery of
--     aristotelian_four_causes; teaching layer (Phase 7) MAY surface
--     "this concept developed historically from X" as enrichment but
--     the structural prereq is removed.
--   * No mastery-computation backward-compatibility hack: learner
--     data does not yet exist for these 17 edges (Phase 5 is
--     pre-deployment); no learner-mastery state migration required.
--   * Evidence backfill: each UPDATE populates the evidence column
--     with a 1-3 sentence rationale extracted from the S-0122 audit
--     findings. The audit-derived prose closes one face of the
--     universal-null evidence-field gap that
--     phase_5_audit_system_input.md Proposal 1 (Issue #62) flagged
--     graph-wide; the broader cleanup is a separate validator soft-warn
--     work item.
-- Source citations:
--   * ADR 0061 product (the retyping decision contract):
--     product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md
--   * Findings report:
--     engine/build_readiness/phase_5_production_audit_findings.md
--     §"Historical genealogy cluster" — full disposition table with
--     fortification outcomes for each of the 14 cross-bridge cases.
--   * Audit evidence files:
--     engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md
--       (CB-E-28 through CB-E-43 finding sections)
--     engine/build_readiness/phase_5_production_audit_evidence/service.md
--       (SVC-E-2, SVC-E-3 finding sections)
--     engine/build_readiness/phase_5_production_audit_evidence/mind.md
--       (MIN-E-23 finding section)
--   * GitHub Issue #60: Historical-influence retyping (filing record).
--   * Predicate registry: PREDICATE_MANIFEST.md (historical_influence
--     in v1 active registry; cardinality many-to-many; display-only).
--   * Numeric prefix: 0061 occupies the cross-bridges sub-range
--     (0060-0069) reserved-but-unused slot; ROUTING.md narrative for
--     0060 explicitly forward-flagged "historical_influence edges if
--     the closeout session P5-12 surfaces such cases" — exactly this
--     case.
-- Idempotency:
--   * Not idempotent. Re-applying after the first apply would update
--     0 rows on each UPDATE (no rows match the WHERE clause once the
--     retyping has landed); no constraint violation, but the Layer 2.5
--     assertions would still pass since they verify post-state, not
--     transition. The apply_migration wrapper's exit-6 ("already
--     applied") gate is the canonical re-fire defense.
-- Rollback:
--   BEGIN;
--   UPDATE public.edges SET edge_type = 'pedagogical_prerequisite', evidence = NULL WHERE edge_type = 'historical_influence' AND (source_id, target_id) IN (('aristotelian_four_causes','causation'),('aristotelian_four_causes','essence_metaphysical'),('aristotelian_four_causes','scientific_explanation'),('aristotelian_four_causes','humean_regularity_theory'),('greek_atomism','physicalism'),('greek_atomism','reductionism_in_science'),('greek_atomism','mereological_nihilism'),('scholasticism','realism_about_universals'),('scholasticism','divine_command_theory'),('renaissance_mechanism','scientific_theory'),('renaissance_mechanism','scientific_method'),('vienna_circle_logical_positivism','falsificationism'),('vienna_circle_logical_positivism','demarcation_problem'),('vienna_circle_logical_positivism','tarskis_t_schema'),('presocratic_naturalism','aristotelian_four_causes'),('aristotelian_four_causes','vienna_circle_logical_positivism'),('consciousness','phenomenology'));
--   COMMIT;
-- Dependencies:
--   * Hard: 0002_nodes.sql, 0003_edges.sql (schema). 0040, 0050, 0060
--     (the source migrations for the 17 affected rows).
--   * Soft: PREDICATE_MANIFEST.md (consulted for predicate activation
--     posture; no edit). ROUTING.md (per-session narrative appended
--     in same commit as this migration).
-- Related:
--   * product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md
--     (the ratifying ADR);
--   * engine/build_readiness/phase_5_production_audit_findings.md
--     (the audit's full disposition matrix);
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--     (apply via engine/tools/apply_migration.py wrapper — eighth
--     load-bearing exercise after S-0050 through S-0075's seven
--     subdomain seeds + cross-bridges + audit-time fortification);
--   * engine/operations/migration-discipline.md Layer 2.5 (the
--     postcondition assertions block above);
--   * GitHub Issue #60 (the closing reference);
--   * product/adr/0001-pedagogical-edges-not-historical.md (the
--     structural distinction the retyping enforces);
--   * product/adr/0008-concept-nodes-not-thinkers.md (the
--     concept-vs-thinker granularity that some retypings preserve).

BEGIN;

-- ============================================================
-- (A) Cross-bridges A3 — service-domain history-terminator → modern
--     philosophy (14 retypings).
-- ============================================================

-- (A.1) From aristotelian_four_causes (4 retypings: CB-E-28 through CB-E-31)

-- CB-E-28: Aristotle's four-cause taxonomy is historical antecedent to
-- modern causation theory; modern theories develop in dialogue with
-- Hume's rejection of pre-modern causes rather than in continuity.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Aristotle''s four-cause taxonomy is a historical antecedent to modern causation theory (Hume, Lewis, Woodward), not a strict pedagogical prerequisite; modern theories develop in dialogue with Hume''s rejection of pre-modern causes rather than in continuity with the four-cause framework.'
 WHERE source_id = 'aristotelian_four_causes' AND target_id = 'causation'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-29: Aristotle's formal cause is historical antecedent to
-- contemporary essence metaphysics; Fine's project is in dialogue with
-- the tradition rather than strictly downstream.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Aristotle''s formal cause is a historical antecedent to contemporary essence metaphysics (Kit Fine, Lowe), but Fine''s project is in dialogue with the tradition rather than strictly downstream of mastering Aristotle''s doctrine.'
 WHERE source_id = 'aristotelian_four_causes' AND target_id = 'essence_metaphysical'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-30: Four-cause typology appears as pre-modern background that
-- modern scientific explanation theory defines itself against.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: The four-cause typology appears as pre-modern background that modern scientific explanation theory (Hempel, Kitcher, Salmon, Woodward) defines itself against; modern theories do not pedagogically presuppose mastery of the Aristotelian framework.'
 WHERE source_id = 'aristotelian_four_causes' AND target_id = 'scientific_explanation'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-31: Hume's regularity theory is framed via his rejection of
-- necessary connection rather than directly through four-causes.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Hume''s regularity theory is framed via his rejection of necessary connection rather than directly through the four-cause taxonomy; the relationship to Aristotle is real but mediated by early-modern mechanism.'
 WHERE source_id = 'aristotelian_four_causes' AND target_id = 'humean_regularity_theory'
   AND edge_type = 'pedagogical_prerequisite';

-- (A.2) From greek_atomism (3 retypings: CB-E-32 through CB-E-34)

-- CB-E-32: Modern physicalism is 20th-century, developed in response to
-- the mind-body problem rather than in continuity with Democritus.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Modern physicalism is a 20th-century position developed in response to the mind-body problem rather than in continuity with Democritus and Leucippus; the genealogical link is real but not the canonical proximate pedagogical prerequisite.'
 WHERE source_id = 'greek_atomism' AND target_id = 'physicalism'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-33: Scientific reduction theory treats contemporary frameworks,
-- not Greek atomism; ancient atomism is ancestral but not pedagogically
-- required for understanding modern reductionism.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Scientific reduction theory (Nagel, Kim) treats contemporary frameworks, not Greek atomism; ancient atomism is ancestral but not pedagogically required for understanding modern reductionism.'
 WHERE source_id = 'greek_atomism' AND target_id = 'reductionism_in_science'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-34: Contemporary mereological nihilism treats formal composition
-- questions only loosely aligned with Greek atomists' empirical claims.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Contemporary mereological nihilism treats formal composition questions that are only loosely aligned with the Greek atomists'' empirical claims about physical decomposition; the conceptual identification is strained.'
 WHERE source_id = 'greek_atomism' AND target_id = 'mereological_nihilism'
   AND edge_type = 'pedagogical_prerequisite';

-- (A.3) From scholasticism (2 retypings: CB-E-35 and CB-E-36)

-- CB-E-35: Medieval problem of universals is historical context, but
-- modern realism (Armstrong, Lewis) is freestanding.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: The medieval problem of universals is historical context, but modern realism about universals (Armstrong, Lewis) is freestanding and not pedagogically downstream of scholastic mastery.'
 WHERE source_id = 'scholasticism' AND target_id = 'realism_about_universals'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-36: Modern divine command theory is intelligible without
-- scholastic apprenticeship; medieval context enriches but is not
-- a strict pedagogical prerequisite.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Modern divine command theory (Adams, Quinn) is intelligible without scholastic apprenticeship; the medieval context enriches but is not a strict pedagogical prerequisite.'
 WHERE source_id = 'scholasticism' AND target_id = 'divine_command_theory'
   AND edge_type = 'pedagogical_prerequisite';

-- (A.4) From renaissance_mechanism (2 retypings: CB-E-38 and CB-E-39)

-- CB-E-38: Modern scientific theory does not directly inherit from
-- Galileo's mechanism; connection is genealogical via gradual
-- development rather than pedagogical prerequisite.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Modern scientific theory (syntactic, semantic, pragmatic views) does not directly inherit from Galileo''s mechanism; the connection is genealogical via gradual development rather than pedagogical prerequisite.'
 WHERE source_id = 'renaissance_mechanism' AND target_id = 'scientific_theory'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-39: Modern philosophy of method does not pedagogically require
-- mastery of Renaissance mechanism; it is a historical antecedent.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Modern philosophy of method (induction, falsificationism, IBE, Bayesianism) does not pedagogically require mastery of Renaissance mechanism; that is a historical antecedent.'
 WHERE source_id = 'renaissance_mechanism' AND target_id = 'scientific_method'
   AND edge_type = 'pedagogical_prerequisite';

-- (A.5) From vienna_circle_logical_positivism (3 retypings: CB-E-41
-- through CB-E-43)

-- CB-E-41: Falsificationism can be taught without prior Vienna Circle
-- apprenticeship; verificationism is an instructive contrast but not
-- a strict prerequisite.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Falsificationism can be taught without prior Vienna Circle apprenticeship; verificationism is an instructive contrast but not a strict prerequisite for understanding Popper''s core thesis.'
 WHERE source_id = 'vienna_circle_logical_positivism' AND target_id = 'falsificationism'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-42: The demarcation problem has multiple historical and
-- contemporary contributions; can be addressed without prior Circle
-- study.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: The demarcation problem has multiple historical and contemporary contributions (Vienna Circle, Popper, Lakatos, Laudan); the problem can be addressed without prior Circle study.'
 WHERE source_id = 'vienna_circle_logical_positivism' AND target_id = 'demarcation_problem'
   AND edge_type = 'pedagogical_prerequisite';

-- CB-E-43: Tarski's T-schema is intelligible without Vienna Circle
-- context; connection is more sociological than conceptual.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Tarski''s T-schema is a logical-semantic technical contribution intelligible without Vienna Circle context; the connection is more sociological (Tarski lectured at Circle symposia) than conceptual.'
 WHERE source_id = 'vienna_circle_logical_positivism' AND target_id = 'tarskis_t_schema'
   AND edge_type = 'pedagogical_prerequisite';

-- ============================================================
-- (B) Within-service A3-internal historical edges (2 retypings:
--     SVC-E-2 and SVC-E-3).
-- ============================================================

-- SVC-E-2: Presocratic project inaugurated naturalistic explanation;
-- Aristotle's four causes were developed against this backdrop;
-- relation is historical-influence with Aristotle's machinery
-- graspable without prior mastery of specific Presocratic positions.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: The Presocratic project inaugurated naturalistic explanation, and Aristotle''s four causes were developed against this backdrop (Metaphysics Alpha); the relation is historical-influence where Aristotle''s new machinery can be grasped without prior mastery of specific Presocratic positions.'
 WHERE source_id = 'presocratic_naturalism' AND target_id = 'aristotelian_four_causes'
   AND edge_type = 'pedagogical_prerequisite';

-- SVC-E-3: Vienna Circle defined itself against broad metaphysics, not
-- the four-cause analysis specifically; relation is historical-influence
-- (negative); more proximate prereq path exists via
-- scholasticism → renaissance_mechanism → vienna_circle.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: The Vienna Circle defined itself against broad metaphysics, not the four-cause analysis specifically; the relation is historical-influence-negative, and more proximate prereq path exists via scholasticism > renaissance_mechanism > vienna_circle.'
 WHERE source_id = 'aristotelian_four_causes' AND target_id = 'vienna_circle_logical_positivism'
   AND edge_type = 'pedagogical_prerequisite';

-- ============================================================
-- (C) Within-mind school/movement target (1 retyping: MIN-E-23).
-- ============================================================

-- MIN-E-23: Phenomenology is a 20th-century tradition/methodology
-- (Husserl, Heidegger, Sartre) that takes consciousness as subject
-- matter; relation is historical_influence or
-- methodological-tradition rather than strict
-- pedagogical_prerequisite.
UPDATE public.edges
   SET edge_type = 'historical_influence',
       evidence  = 'Per S-0122 audit: Phenomenology is a 20th-century tradition/methodology (Husserl, Heidegger, Sartre) that takes consciousness as subject matter; the relation is historical_influence or methodological-tradition rather than strict pedagogical_prerequisite.'
 WHERE source_id = 'consciousness' AND target_id = 'phenomenology'
   AND edge_type = 'pedagogical_prerequisite';

COMMIT;
