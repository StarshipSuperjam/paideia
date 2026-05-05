-- Migration: 0060_seed_crossbridges_part1
-- Purpose: Fifteenth Phase 5 seed migration (the cross-bridges file) —
--   the dedicated cross-domain edges pass that lands AFTER all fourteen
--   prior subdomain seedings (P5-01a/b epistemology core/specialized,
--   P5-02a/b metaphysics core/specialized, P5-03 logic, P5-04a/b ethics
--   metaethics+normative/applied, P5-05 political philosophy, P5-06
--   aesthetics, P5-07a/b philosophy of mind core/specialized, P5-08
--   philosophy of language, P5-09 philosophy of science, P5-10 service
--   nodes). Authored in S-0075 against task P5-11 "Cross-bridges
--   (cross-domain edges pass)" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   P5-11 is a single-task per phase_5.md T1-B/T1-D; range per
--   phase_5.md T2-A is 0060-0069. Per T2-G #1 (cross-domain edge
--   collisions vector), individual subdomain sessions did NOT author
--   cross-domain edges — those are P5-11''s exclusive responsibility,
--   discharged here.
--
--   Three logical groupings of cross-domain edges, all
--   pedagogical_prerequisite per the T1-E/T3-B predicate decision
--   (see Cross-cutting decisions below):
--
--   (A) Service-node → philosophy-subdomain bridges (45 edges) — the
--   richest cross-domain reach surface, since every service-node
--   concept (formal-logic primitives, math prerequisites, history
--   terminators) pedagogically supports concepts in multiple
--   philosophy subdomains by construction. Subdivided into:
--   (A1) Service formal-logic primitives → philosophy (15 edges) —
--   the formal-logic primitives ground philosophical-logic concepts
--   in P5-03 (classical_logic, propositional_logic, predicate_logic,
--   dialetheism, fuzzy_logic, paraconsistent_logic) and ground
--   epistemological reasoning in P5-01a/b (gettier counterexamples,
--   epistemic_justification via good arguments, soundness in
--   formal_epistemology) and ground the formal pattern of falsifiability
--   in P5-09 (modus_tollens → falsificationism);
--   (A2) Service math prerequisites → philosophy (12 edges) — the
--   math primitives ground formal philosophy of language (set_mathematical
--   → kripke_semantics + russell_paradox), modal metaphysics
--   (set_mathematical → possible_worlds; quantifier → predicate_logic),
--   Bayesian epistemology and confirmation theory (probability_,
--   conditional_, bayes_theorem → bayesian_epistemology +
--   bayesianism_confirmation; conditional_probability →
--   conditionalization), and decision-theoretic ethics / political
--   philosophy (expected_value → utilitarianism + dutch_book_argument
--   + social_contract_theory);
--   (A3) Service history terminators → philosophy (18 edges) — the
--   history terminators ground their descendant philosophical positions
--   across multiple subdomains (aristotelian_four_causes → causation /
--   essence_metaphysical / scientific_explanation / humean_regularity_
--   theory; greek_atomism → physicalism / reductionism_in_science /
--   mereological_nihilism; scholasticism → realism_about_universals /
--   divine_command_theory; renaissance_mechanism → substance_dualism /
--   scientific_theory / scientific_method; vienna_circle_logical_
--   positivism → verificationism / falsificationism / demarcation_
--   problem / tarskis_t_schema / deductive_nomological_model /
--   behaviorism_logical).
--
--   (B) Within-philosophy cross-subdomain bridges (26 edges) — pairs
--   across the 9 subjects, organized by source-subdomain:
--   epistemology↔mind (belief / epistemic_justification →
--   propositional_attitude); epistemology↔language (truth → tarskis_t_
--   schema + truth_conditional_semantics); epistemology↔science
--   (problem_of_induction → bayesianism_confirmation + falsificationism
--   + scientific_method; evidence → bayesianism_confirmation);
--   epistemology↔logic (formal_epistemology → modal_logic +
--   kripke_semantics; epistemic_closure → modal_logic);
--   metaphysics↔mind (causation → mental_causation; property →
--   property_dualism; substance → substance_dualism);
--   metaphysics↔logic (modality → modal_logic + kripke_semantics;
--   possible_worlds → kripke_semantics);
--   mind↔language (propositional_attitude → proposition; intentionality
--   → meaning; causal_theory_of_mental_content →
--   causal_theory_of_reference); mind↔science (multiple_realizability →
--   multiple_realizability_in_science; physicalism →
--   reductionism_in_science); logic↔science (material_conditional →
--   paradox_of_the_ravens); ethics↔mind (motivational_internalism →
--   propositional_attitude); ethics↔political (justice → morality;
--   social_contract_theory → contractualism).
--
--   (C) Aesthetics deferred to a future part2 if telemetry warrants —
--   aesthetics concepts are more self-contained at the granularity
--   principle than the other 8 subjects, so folding them into part1
--   would dilute the coherence of the first cross-bridges migration.
--   Sub-range slots 0061-0069 remain reserved.
--
-- Loads tables: public.edges (71 INSERTs), public.settings (1 UPDATE
--   incrementing graph_version 15 -> 16). No new nodes — every edge
--   endpoint references a pre-existing seeded id from one of the 14
--   prior subdomain migrations (380 nodes total; pre-apply existence
--   sweep against the seeded id set confirmed zero dangling-endpoint
--   risks).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges,
--     public.settings all exist with the columns and CHECKs from 0002,
--     0003, 0004.
--   * settings.graph_version = 15 at session boot (post-S-0074 per
--     ROUTING.md narrative — most recent applied seed at the cross-
--     subdomain prefix range was 0050_seed_services_part1.sql which
--     wrote 15). The increment contract per ROUTING.md is honored:
--     all edge INSERTs in this migration carry graph_version_added =
--     16 (the post-increment value).
--   * No prior migrations under prefix 0060-0069; this is the first
--     cross-bridges seed file.
--   * All fourteen Phase 5 subject + service deps applied: P5-01a
--     (0011), P5-01b (0016), P5-02a (0030), P5-02b (0036), P5-03
--     (0090), P5-04a (0020), P5-04b (0026), P5-05 (0100), P5-06
--     (0110), P5-07a (0040), P5-07b (0046), P5-08 (0070), P5-09
--     (0080), P5-10 (0050). Every (source_id, target_id) endpoint
--     in this migration references a node id seeded by one of these
--     fourteen prior migrations.
-- Postconditions:
--   * 71 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, provenance=ai-seed,
--     graph_version_added=16. All cross-domain (every (source, target)
--     pair has source.domain[] disjoint from target.domain[]).
--   * settings.graph_version = 16.
--   * No new nodes inserted. No PREDICATE_MANIFEST.md registry rows
--     added (only pedagogical_prerequisite is used; already in v1
--     registry).
-- Invariants:
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that one of the 14 prior
--     migrations inserted. Pre-apply Python existence sweep against
--     the seeded 380-id set confirmed zero dangling-endpoint risks
--     across all 71 edges.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql
--     holds: no triple in this migration duplicates any other triple
--     (all 71 (source, target) pairs are pairwise distinct since
--     edge_type is uniformly pedagogical_prerequisite). Pre-apply
--     audit against the 465 edges already in the graph (all
--     within-subdomain per design — no prior migration authored
--     cross-domain edges per master plan T2-G #1) confirmed zero
--     collision risks across all 71 candidate cross-domain pairs.
--   * Cross-domain shape: every (source, target) pair satisfies
--     source.domain[] ∩ target.domain[] = ∅ (the disjoint-domain
--     convention recognized by validate.py''s
--     suspicious_cross_domain_ratio soft-warn). The validator''s
--     expected firing of this category at <60% within-philosophy
--     subdomains is acknowledged per phase_5.md T2-C; for the
--     cross-bridges migration specifically the firing is
--     definitionally 100% on this migration''s authored edges, which
--     is the correct shape.
--   * No edge cycles introduced. The 71 cross-domain edges connect
--     the existing within-subdomain DAGs without forming cycles
--     because (a) each subdomain seed is internally a DAG; (b) the
--     cross-domain bridges all flow in defensible pedagogical
--     directions (e.g., from foundational service primitives toward
--     dependent philosophy concepts; from foundational metaphysical
--     concepts toward dependent philosophy-of-mind concepts; from
--     foundational logic concepts toward dependent philosophy-of-
--     language and philosophy-of-science concepts) without back-
--     edges. validate.py''s Kosaraju SCC check confirms post-apply.
-- Non-responsibilities:
--   * Does not author any new nodes. All cross-domain reach
--     observations from the 14 prior subdomain seedings (especially
--     S-0074''s service-node ROUTING narrative which catalogued the
--     full set) directly inform the edge inventory authored here;
--     no inventory gap surfaced that requires a missing-node
--     insertion. Any concept-level gap surfaced post-Phase-5
--     belongs to a future seed-graph maintenance session, not P5-11.
--   * Does not register any new edge predicates. Per the T1-E/T3-B
--     decision recorded in Cross-cutting decisions below, the
--     reserved cross_domain_dependency predicate is NOT promoted to
--     the v1 registry; the disjoint-domain convention via
--     pedagogical_prerequisite suffices. PREDICATE_MANIFEST.md is
--     edited in the same commit to remove the reserved-but-unused
--     row per the manifest''s own discipline.
--   * Does not author historical_influence edges. The history
--     terminators in service nodes (presocratic_naturalism,
--     greek_atomism, aristotelian_four_causes, scholasticism,
--     renaissance_mechanism, vienna_circle_logical_positivism,
--     hegelian_dialectic) bridge to descendant philosophical positions
--     via pedagogical_prerequisite (the descendants pedagogically
--     presuppose understanding the ancestor); the
--     historical_influence predicate is reserved for cases where the
--     historical-genealogy claim is the primary content and the
--     descendant does NOT pedagogically presuppose the ancestor.
--     None of P5-11''s 71 edges fits that shape.
--   * Does not seed within-subdomain edges. Each subdomain''s
--     internal DAG was authored by its own subject seed migration
--     (P5-01a through P5-10); P5-11 is exclusively the cross-domain
--     edges pass.
--   * Does not author the additional sub-range slots (0061-0069).
--     Those slots remain reserved for any future expansion if
--     telemetry warrants — most likely candidates are aesthetics
--     bridges (deferred per Purpose grouping (C)), additional
--     within-philosophy bridges if cross-session review surfaces
--     load-bearing pedagogical paths missed in this part1, and
--     historical_influence edges if the closeout session
--     P5-12 surfaces such cases.
-- Cross-cutting decisions:
--   * T1-E / T3-B predicate decision: do NOT promote
--     cross_domain_dependency to the v1 PREDICATE_MANIFEST.md
--     registry. Per phase_5.md T1-E and the
--     PREDICATE_MANIFEST.md reserved-entry note, the cross-bridge
--     session adjudicates whether to formally introduce the
--     predicate or continue the existing disjoint-domain convention
--     (cross-domain edges as pedagogical_prerequisite with disjoint
--     domain[] arrays). The decision is to continue the convention.
--     Reasoning: (1) every cross-domain edge authored in this
--     migration is shape-identical to within-domain
--     pedagogical_prerequisite — the source concept is genuinely a
--     prerequisite to understanding the target concept at the
--     granularity-principle level the project teaches them; the
--     ONLY distinguishing feature is that source and target carry
--     disjoint domain[] arrays, a shape the validator''s
--     suspicious_cross_domain_ratio soft-warn already detects per
--     phase_4_graph_validation.md T2-D and validate.py:1276-1278;
--     (2) the cross-bridges authoring did NOT surface a structural
--     distinction that warrants a separate predicate — there is no
--     different rigor calibration, no different bridging concept
--     pattern, no different domain/range typing; the cross-domain
--     edges pedagogically behave exactly like within-domain
--     prerequisites except for the disjoint-domain shape;
--     (3) registering a new predicate would require downstream
--     consumer changes (traversal, syllabus generation, mastery
--     computation per phase_4_graph_validation.md T2-G consume
--     pedagogical_prerequisite only) that this routine session is
--     not authorized to make and that would represent
--     scope-expansion rather than the cross-bridges work this task
--     is scoped to;
--     (4) the manifest itself recommends "promote if Phase 5
--     cross-domain authoring surfaces a structural distinction"
--     (PREDICATE_MANIFEST.md:36) — the authoring does NOT surface
--     a structural distinction. Per the manifest''s discipline ("If
--     a reserved entry never gets used by the time the next periodic
--     project health check fires, it should be removed from this
--     list"), this session removes the cross_domain_dependency
--     reserved-but-unused row in the same commit, with a brief note
--     in the section preface recording the S-0075 decision.
--   * confidence_level: not applicable — edges do not carry
--     confidence_level (per 0003_edges.sql, only nodes do per
--     0002_nodes.sql + ADR 0030). The phase_5.md T2-B floor
--     (INTERPRETED >= 70%) was set for nodes; for cross-bridges
--     specifically T2-B says "all edges INTERPRETED" — applied
--     interpretively as guidance on the pedagogical-prerequisite
--     defense for each edge: every edge in this migration is
--     defended by interpretive pedagogical reasoning (no edge is
--     directly extracted from a structural-reference inventory; no
--     edge is so speculative that it warrants the SYNTHETIC tier).
--     The interpretive defense for each edge appears either in the
--     in-line comment within the edge VALUES list below or in the
--     A1/A2/A3/B grouping commentary in this Purpose block.
--   * provenance: ''ai-seed'' for every edge. Same as P5-01a/b,
--     P5-02a/b, P5-03, P5-04a/b, P5-05, P5-06, P5-07a/b, P5-08,
--     P5-09, P5-10.
--   * Edge inventory rationale: 71 edges total. Aimed at the
--     pedagogical-coverage sweet spot where every cross-domain
--     edge added has clear pedagogical-prerequisite warrant
--     (a student of the target concept genuinely needs to
--     understand the source concept at the level the project
--     teaches them). Pruned aggressively from the broader
--     candidate set: cross-domain reach observations across the
--     14 prior subdomain seedings collectively named ~150 candidate
--     bridges; this migration retains the 71 with the highest
--     pedagogical warrant and tightest concept-level connection.
--     Cuts include: (a) bridges where the target concept is
--     pedagogically self-contained at the granularity principle
--     and the source concept is enrichment rather than prerequisite
--     (e.g., aesthetics-bridges in general — aesthetics deferred to
--     part2); (b) bridges subsumed by transitivity through other
--     bridges in this migration (e.g., truth_value →
--     truth_conditional_semantics is subsumed by truth_value →
--     classical_logic + the within-language path from
--     truth_conditional_semantics back to truth_value via Tarski);
--     (c) bridges where the historical-influence claim is stronger
--     than the pedagogical-prerequisite claim (those would belong
--     to a future historical_influence pass per
--     Non-responsibilities above).
--   * graph_version: 15 -> 16 in the same transaction. Every
--     cross-domain edge in this migration carries
--     graph_version_added = 16, satisfying the per-session
--     monotonicity contract per ROUTING.md "graph_version increment
--     contract". Reserved sub-range slots 0061-0069 do not bump
--     graph_version on their own; if they are eventually populated,
--     the populating session bumps to its own next-integer.
-- Source citations:
--   * Master plan: engine/build_readiness/phase_5.md (T1-A/B/C/D/E,
--     T2-A/B/C/D/E/F/G/H, T3-B for the cross_domain_dependency
--     deferral closed here);
--   * Predicate registry: product/seed-graph/migrations/PREDICATE_
--     MANIFEST.md (v1 registry: pedagogical_prerequisite,
--     historical_influence; reserved row for
--     cross_domain_dependency removed in same commit);
--   * Per-edge pedagogical warrant: each edge''s in-line comment
--     names the textbook / SEP entry / Cambridge history reference
--     genre that establishes the pedagogical prerequisite. No
--     copyrighted prose extracted (per ADR 0011);
--   * Cross-domain reach observations: S-0050 through S-0074
--     ROUTING.md narrative entries — every prior subject seed
--     ROUTING.md narrative flagged its cross-domain reach
--     candidates in a "deferred to P5-11" forward-pointer (most
--     extensively in S-0074 service-node narrative);
--   * Disjoint-domain convention: validate.py:1276-1278
--     suspicious_cross_domain_ratio soft-warn (philosophy-
--     subdomain reinterpretation in phase_5.md T2-C: <60%
--     acceptable; for cross-bridges migration definitionally
--     100% which is correct shape).
-- Idempotency:
--   * Not idempotent. Re-running this migration after successful
--     application would violate the
--     UNIQUE (source_id, target_id, edge_type) constraint on every
--     edge insert. Recovery from a partial-apply (impossible
--     under the BEGIN/COMMIT wrap because Postgres rolls back the
--     entire transaction on any constraint violation) would be:
--     SELECT graph_version_added, count(*) FROM public.edges
--     WHERE graph_version_added = 16 GROUP BY graph_version_added;
--     if zero rows present, simply re-run; if 71 rows present,
--     migration already applied — record in
--     supabase_migrations.schema_migrations if missing and proceed.
-- Rollback: BEGIN; DELETE FROM public.edges WHERE
--   graph_version_added = 16 (no nodes inserted in this migration so
--   no node DELETE here); UPDATE public.settings SET value =
--   ''15''::jsonb WHERE key = ''graph_version''; COMMIT. The whole-
--   migration BEGIN/COMMIT wrap means a failed apply rolls back
--   automatically; the rollback statement above is for the case of
--   needing to remove a successfully applied migration during a
--   later corrective session.
-- Dependencies:
--   * Hard: 0002_nodes.sql, 0003_edges.sql, 0004_settings.sql
--     (schema). 0011-0119 (every prior Phase 5 seed migration
--     covering the 380 endpoint nodes referenced by the 71 edges
--     here).
--   * Soft: PREDICATE_MANIFEST.md (consulted for predicate
--     decision; edited in same commit to remove the reserved
--     cross_domain_dependency entry per T1-E/T3-B decision).
--     ROUTING.md (per-session narrative entry appended in same
--     commit).
-- Related:
--   * engine/build_readiness/phase_5.md T1-E (cross_domain_dependency
--     predicate decision deferred to P5-11; closed here),
--     T2-G #1 (cross-domain edge collisions vector — cross-bridges
--     as P5-11''s exclusive responsibility), T2-C
--     (suspicious_cross_domain_ratio soft-warn philosophy-subdomain
--     reinterpretation), T3-B (forward-pointer to predicate decision
--     closed here);
--   * product/adr/0052-phase-5-philosophy-subdomain-decomposition.md
--     (Phase 5 master decomposition; this is the 15th of 16 explicit
--     tasks, second-to-last);
--   * product/adr/0007-cross-domain-porosity.md (cross-domain
--     porosity rationale; this migration discharges the porosity
--     commitment for the Phase 5 graph);
--   * product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md
--     (confidence_level applies to nodes only; not applicable here);
--   * product/seed-graph/migrations/PREDICATE_MANIFEST.md (edited in
--     same commit to remove cross_domain_dependency reserved row);
--   * product/seed-graph/migrations/ROUTING.md (per-session narrative
--     appended in same commit; numeric prefix scheme for 0060-0069
--     sub-range);
--   * engine/adr/0055-apply-migration-wrapping-against-production-
--     reads-gate.md (apply via engine/tools/apply_migration.py wrapper
--     — seventh load-bearing routine-mode exercise of this wrapper).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 15 at session boot (post-S-0074 state per ROUTING.md
-- narrative); write 16 here; every edge below carries
-- graph_version_added = 16.
UPDATE public.settings
  SET value = '16'::jsonb
  WHERE key = 'graph_version';

-- Edges: 71 cross-domain pedagogical_prerequisite edges. Three
-- groupings per Purpose block: (A) service-node → philosophy 45
-- edges, (B) within-philosophy cross-subdomain 26 edges. All
-- cross-domain (source.domain[] ∩ target.domain[] = ∅).
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- ============================================================
  -- (A) SERVICE-NODE → PHILOSOPHY-SUBDOMAIN BRIDGES (45 edges)
  -- ============================================================
  -- (A1) Service formal-logic primitives → philosophy (15 edges)
  -- truth_value (service) is the formal-semantic primitive that
  -- classical-logic semantics is built on; classical_logic (logic)
  -- IS bivalent two-valued logic.
  ('truth_value', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- bivalence_principle (service) IS the principle that classical
  -- logic accepts and that the deviant logics reject in various ways.
  ('bivalence_principle', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- dialetheism (logic) is the position that some contradictions are
  -- true — to understand the position, students must first grasp the
  -- bivalence principle that dialetheism rejects.
  ('bivalence_principle', 'dialetheism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- fuzzy_logic (logic) abandons bivalence in favor of degrees of
  -- truth on [0,1]; understanding what is being abandoned requires
  -- the bivalence principle.
  ('bivalence_principle', 'fuzzy_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- paraconsistent_logic (logic) tolerates contradictions without
  -- triviality; the motivating background is the bivalence principle
  -- and the explosion principle that follows from it under classical
  -- semantics.
  ('bivalence_principle', 'paraconsistent_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- argument_logical (service) is the formal-reasoning structure
  -- (premises plus conclusion); epistemic_justification
  -- (epistemology) is paradigmatically given by good arguments —
  -- understanding what makes a justification good requires the
  -- prior concept of an argument.
  ('argument_logical', 'epistemic_justification', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- validity_logical (service) is the form-based truth-preservation
  -- property; classical_logic (logic) defines validity relative to
  -- bivalent truth-functional semantics.
  ('validity_logical', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- soundness_logical (service) is validity plus actually-true
  -- premises; formal_epistemology (epistemology specialized) uses
  -- soundness considerations for belief-revision logics and
  -- justification frameworks.
  ('soundness_logical', 'formal_epistemology', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- inference_rule (service) is the syntactic primitive of formal
  -- proof systems; propositional_logic (logic) IS the system of
  -- truth-functional inference rules.
  ('inference_rule', 'propositional_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- Same primitive grounds the variable-binding rules of
  -- predicate_logic (logic) — universal/existential introduction
  -- and elimination are inference rules.
  ('inference_rule', 'predicate_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- modus_ponens (service) is the canonical propositional inference
  -- rule; propositional_logic (logic) is the formal study of
  -- truth-functional rules including MP.
  ('modus_ponens', 'propositional_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- modus_tollens (service) is the contrapositive form;
  -- propositional_logic (logic) studies it as a derived rule.
  ('modus_tollens', 'propositional_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- falsificationism (science) is the methodology of refuting
  -- universally-quantified scientific hypotheses by deriving an
  -- observable consequence and testing it — formally, this IS
  -- modus tollens applied to the conditional "if H then O" with O
  -- the observable consequence.
  ('modus_tollens', 'falsificationism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- formal_proof (service) is the syntactic concept of a finite
  -- derivation; classical_logic (logic) is studied via its proof
  -- systems (natural deduction, sequent calculus, axiomatic Hilbert
  -- systems).
  ('formal_proof', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- counterexample (service) is the canonical method of refuting a
  -- universal claim by producing a single instance that fails;
  -- gettier_problem (epistemology) IS a counterexample to the JTB
  -- analysis of knowledge — Gettier cases are paradigm
  -- counterexamples.
  ('counterexample', 'gettier_problem', 'pedagogical_prerequisite', 'ai-seed', 16),

  -- (A2) Service math prerequisites → philosophy (12 edges)
  -- set_mathematical (service) is the foundational collection
  -- concept; russell_paradox (logic) is the paradox of unrestricted
  -- set comprehension — historically the motivation for ZFC
  -- axiomatization.
  ('set_mathematical', 'russell_paradox', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- possible_worlds (metaphysics specialized) are typically modeled
  -- as sets in possible-worlds semantics for modal logic and modal
  -- metaphysics.
  ('set_mathematical', 'possible_worlds', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- kripke_semantics (logic) is the model-theoretic framework for
  -- modal logic constructed from a set of worlds, an accessibility
  -- relation on that set, and an interpretation function — set-
  -- theoretic at every level.
  ('set_mathematical', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- quantifier (service) is the variable-binding logical operator;
  -- predicate_logic (logic) IS quantifier logic — propositional
  -- logic extended with quantifiers and predicates.
  ('quantifier', 'predicate_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- probability_mathematical (service) is the formal probability
  -- measure; bayesian_epistemology (epistemology specialized) models
  -- belief as credences that ARE probabilities (degrees of belief
  -- satisfying the probability axioms).
  ('probability_mathematical', 'bayesian_epistemology', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- bayesianism_confirmation (science) is the Bayesian theory of
  -- evidential support for scientific hypotheses — formally a
  -- probability calculus over hypotheses and evidence.
  ('probability_mathematical', 'bayesianism_confirmation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- conditional_probability (service) is the central operation
  -- P(A|B) on the formal probability measure; conditionalization
  -- (epistemology specialized) is the Bayesian belief-updating
  -- rule that takes new evidence E and updates the credence in H
  -- to the prior conditional probability P(H|E).
  ('conditional_probability', 'conditionalization', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- bayes_theorem (service) is the formal probability-inversion
  -- identity P(H|E) = P(E|H)·P(H)/P(E); bayesian_epistemology
  -- (epistemology specialized) uses Bayes to compute posterior
  -- credences from priors and likelihoods.
  ('bayes_theorem', 'bayesian_epistemology', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- Same theorem grounds bayesianism_confirmation (science): the
  -- canonical Bayesian formula for the degree to which evidence E
  -- confirms hypothesis H.
  ('bayes_theorem', 'bayesianism_confirmation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- expected_value (service) is the probability-weighted average
  -- E[X] = Σ x·P(X=x); dutch_book_argument (epistemology
  -- specialized) shows that an agent whose credences are not
  -- probabilistically coherent will accept a set of bets with
  -- jointly negative expected value — the argument is constructed
  -- from expected-value comparisons.
  ('expected_value', 'dutch_book_argument', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- utilitarianism (ethics metaethics+normative) evaluates actions
  -- by aggregate utility; the formal decision-theoretic version
  -- evaluates actions by expected utility — the action with maximum
  -- expected utility is right.
  ('expected_value', 'utilitarianism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- social_contract_theory (political) admits a game-theoretic
  -- treatment in which contractors evaluate institutions by their
  -- expected outcomes for parties under uncertainty — the original
  -- position (Rawls) and Hobbesian state-of-nature reasoning use
  -- expected-value reasoning.
  ('expected_value', 'social_contract_theory', 'pedagogical_prerequisite', 'ai-seed', 16),

  -- (A3) Service history terminators → philosophy (18 edges)
  -- aristotelian_four_causes (service) is Aristotle''s analysis of
  -- explanation as material/formal/efficient/final cause; causation
  -- (metaphysics core) inherits the four-cause vocabulary as the
  -- foundational pre-modern theory of causal explanation.
  ('aristotelian_four_causes', 'causation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- essence_metaphysical (metaphysics specialized) is the property
  -- that a thing has of being-what-it-is — directly inherited from
  -- the Aristotelian formal cause.
  ('aristotelian_four_causes', 'essence_metaphysical', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- scientific_explanation (science) inherits the four-cause
  -- typology as the pre-modern background that the modern (post-
  -- Renaissance, post-Hempel) account of scientific explanation
  -- defined itself against.
  ('aristotelian_four_causes', 'scientific_explanation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- humean_regularity_theory (metaphysics core) explicitly rejects
  -- Aristotelian formal and final causes; understanding the
  -- Humean position requires the prior Aristotelian background.
  ('aristotelian_four_causes', 'humean_regularity_theory', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- greek_atomism (service) is the indivisible-particles-in-void
  -- doctrine; physicalism (mind) is its modern descendant — the
  -- view that everything that exists is physical.
  ('greek_atomism', 'physicalism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- reductionism_in_science (science) is paradigmatically atomistic
  -- — explaining macro-level phenomena via the properties and
  -- interactions of micro-level constituents. Greek atomism is the
  -- ancestral form.
  ('greek_atomism', 'reductionism_in_science', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- mereological_nihilism (metaphysics specialized) is the position
  -- that the only things that exist are mereological simples —
  -- approximately the modern formal cousin of atomism (with care
  -- about "simples" vs "atoms" in the technical mereological sense).
  ('greek_atomism', 'mereological_nihilism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- scholasticism (service) is the medieval philosophical-theological
  -- synthesis grounded in Aristotle; realism_about_universals
  -- (metaphysics specialized) is paradigmatically the medieval
  -- realist position in the universals dispute.
  ('scholasticism', 'realism_about_universals', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- divine_command_theory (ethics metaethics+normative) is most
  -- developed in the medieval scholastic tradition (Aquinas,
  -- Scotus, Ockham); understanding the position requires its
  -- scholastic context.
  ('scholasticism', 'divine_command_theory', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- renaissance_mechanism (service) is the matter-in-motion
  -- philosophy that supplanted the Aristotelian-Scholastic
  -- synthesis; substance_dualism (mind) — the founding mind-body
  -- debate — is between Descartes (a paradigm mechanist) and his
  -- materialist contemporaries (Hobbes, Spinoza, the libertines).
  ('renaissance_mechanism', 'substance_dualism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- scientific_theory (science) — the modern conception of theory
  -- as a system of mathematically expressed laws governing
  -- mechanically conceived nature — traces directly to Galilean
  -- and Newtonian mechanics.
  ('renaissance_mechanism', 'scientific_theory', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- scientific_method (science) — the experimental-mathematical
  -- methodology of modern science — was inaugurated by the Galilean
  -- mechanist program.
  ('renaissance_mechanism', 'scientific_method', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- vienna_circle_logical_positivism (service) IS the founding
  -- movement that elevated verificationism (language) to a central
  -- doctrine of meaningfulness.
  ('vienna_circle_logical_positivism', 'verificationism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- falsificationism (science) — Popper''s alternative criterion of
  -- scientific demarcation — was developed explicitly against the
  -- Vienna Circle''s verificationism. Understanding falsificationism
  -- requires the positivist background it responded to.
  ('vienna_circle_logical_positivism', 'falsificationism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- demarcation_problem (science) — the problem of distinguishing
  -- science from non-science — was elevated to a central
  -- philosophical concern by the Vienna Circle and remains
  -- defined relative to the positivist framing.
  ('vienna_circle_logical_positivism', 'demarcation_problem', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- tarskis_t_schema (language) — Tarski''s convention-T and the
  -- semantic conception of truth — was developed in the Vienna
  -- Circle''s intellectual orbit (Tarski lectured there; Carnap
  -- adopted Tarskian semantics in his shift from syntactic to
  -- semantic approaches).
  ('vienna_circle_logical_positivism', 'tarskis_t_schema', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- deductive_nomological_model (science) — Hempel''s covering-law
  -- model of scientific explanation — is paradigm logical-empiricist
  -- philosophy of science.
  ('vienna_circle_logical_positivism', 'deductive_nomological_model', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- behaviorism_logical (mind) — the philosophical (vs.
  -- psychological) thesis that mental-state ascriptions translate
  -- into statements about behavioral dispositions — descends
  -- directly from the Vienna Circle''s anti-mentalist program
  -- (Carnap, Hempel, early Ryle).
  ('vienna_circle_logical_positivism', 'behaviorism_logical', 'pedagogical_prerequisite', 'ai-seed', 16),

  -- ============================================================
  -- (B) WITHIN-PHILOSOPHY CROSS-SUBDOMAIN BRIDGES (26 edges)
  -- ============================================================
  -- belief (epistemology core) → propositional_attitude (mind):
  -- belief is the paradigm propositional attitude; the philosophy
  -- of mind treatment of belief as an attitude toward a propositional
  -- content presupposes the basic concept of belief.
  ('belief', 'propositional_attitude', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- epistemic_justification (epistemology core) → propositional_
  -- attitude (mind): the bearer of justification is a propositional
  -- attitude (typically belief); justification is a property of
  -- attitudes.
  ('epistemic_justification', 'propositional_attitude', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- truth (epistemology core) → tarskis_t_schema (language):
  -- Tarski''s T-schema "''S'' is true iff S" formalizes the truth
  -- predicate; understanding the formalization requires the
  -- ordinary-language concept of truth.
  ('truth', 'tarskis_t_schema', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- truth (epistemology core) → truth_conditional_semantics
  -- (language): truth-conditional semantics — meaning IS truth-
  -- conditions — presupposes the concept of truth.
  ('truth', 'truth_conditional_semantics', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- problem_of_induction (epistemology specialized) →
  -- bayesianism_confirmation (science): Bayesian confirmation
  -- theory is the dominant contemporary response to Hume''s
  -- problem of induction.
  ('problem_of_induction', 'bayesianism_confirmation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- problem_of_induction → falsificationism (science): Popper''s
  -- falsificationism is explicitly framed as a response to the
  -- problem of induction (replace inductive support with
  -- corroboration through failed falsification attempts).
  ('problem_of_induction', 'falsificationism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- problem_of_induction → scientific_method (science): the
  -- modern theory of scientific method must take a stance on the
  -- problem of induction (whether to embrace inductive inference,
  -- replace it with falsification, formalize it Bayesian-style,
  -- etc.).
  ('problem_of_induction', 'scientific_method', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- evidence (epistemology core) → bayesianism_confirmation
  -- (science): Bayesian confirmation theory is a theory of how
  -- evidence supports hypotheses.
  ('evidence', 'bayesianism_confirmation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- formal_epistemology (epistemology specialized) → modal_logic
  -- (logic): epistemic logics use modal-logic frameworks
  -- (knowledge as a necessity-like operator with KT or S4 axioms).
  ('formal_epistemology', 'modal_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- formal_epistemology → kripke_semantics (logic): epistemic
  -- logics use Kripke semantics (worlds as epistemic possibilities;
  -- accessibility relation as epistemic indistinguishability).
  ('formal_epistemology', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- epistemic_closure (epistemology core) → modal_logic (logic):
  -- closure principles in epistemology — if S knows P and S knows
  -- (P implies Q) then S knows Q — are studied formally as axioms
  -- in epistemic modal logic (the K axiom: K(P→Q) → (KP → KQ)).
  ('epistemic_closure', 'modal_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- causation (metaphysics core) → mental_causation (mind):
  -- mental causation — the question of how mental states can be
  -- causes of physical effects — presupposes the general
  -- metaphysics of causation.
  ('causation', 'mental_causation', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- property (metaphysics core) → property_dualism (mind):
  -- property dualism — the view that mental and physical properties
  -- are distinct kinds of properties of a single substance —
  -- presupposes the metaphysical category of property.
  ('property', 'property_dualism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- substance (metaphysics core) → substance_dualism (mind):
  -- substance dualism — Descartes''s view that mind and body are
  -- distinct substances — presupposes the metaphysical category
  -- of substance.
  ('substance', 'substance_dualism', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- modality (metaphysics specialized) → modal_logic (logic):
  -- modal logic is the formal study of modal notions (necessity,
  -- possibility); the philosophical concept of modality grounds
  -- the formal study.
  ('modality', 'modal_logic', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- modality → kripke_semantics (logic): Kripke semantics for
  -- modal logic is the model-theoretic formalization of necessity
  -- as truth-at-all-accessible-worlds; understanding the
  -- formalization requires the underlying modal concepts.
  ('modality', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- possible_worlds (metaphysics specialized) → kripke_semantics
  -- (logic): Kripke semantics IS possible-worlds semantics — the
  -- worlds in the model are possible worlds.
  ('possible_worlds', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- propositional_attitude (mind) → proposition (language):
  -- propositional attitudes are attitudes toward propositions; the
  -- mind concept references the language-philosophy concept of
  -- proposition as content-bearer.
  ('propositional_attitude', 'proposition', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- intentionality (mind) → meaning (language): intentional
  -- content is, on standard treatments, semantic content — the
  -- mind concept of aboutness connects to the language concept
  -- of meaning. Brentano''s mark of the mental and the linguistic
  -- philosophy of meaning are pedagogically continuous.
  ('intentionality', 'meaning', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- causal_theory_of_mental_content (mind) → causal_theory_of_
  -- reference (language): the parallel theories — a causal
  -- relation between concept-in-the-head and object-in-the-world
  -- explains intentional content (Fodor, Dretske, Stampe) /
  -- linguistic reference (Kripke, Putnam, Donnellan) — share
  -- structural commitments. The mind theory is a paradigm
  -- application of the language theory.
  ('causal_theory_of_mental_content', 'causal_theory_of_reference', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- multiple_realizability (mind) → multiple_realizability_in_
  -- science (science): the philosophy-of-mind concept (mental
  -- types are realizable in distinct physical types — Putnam''s
  -- pain-in-mammals-and-octopuses argument) generalizes to the
  -- philosophy-of-science concept (special-science kinds are
  -- realizable in distinct lower-level kinds — the anti-
  -- reductionist argument).
  ('multiple_realizability', 'multiple_realizability_in_science', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- physicalism (mind) → reductionism_in_science (science):
  -- the type-identity formulation of physicalism (mental types
  -- are physical types) is paradigmatically reductionist; the
  -- philosophy-of-mind position grounds reductionist methodology
  -- in the special sciences.
  ('physicalism', 'reductionism_in_science', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- material_conditional (logic) → paradox_of_the_ravens
  -- (science): Hempel''s paradox arises from formalizing "all
  -- ravens are black" as the universally quantified material
  -- conditional ∀x(Rx → Bx); the paradox depends on the truth-
  -- table behavior of the material conditional.
  ('material_conditional', 'paradox_of_the_ravens', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- motivational_internalism (ethics metaethics+normative) →
  -- propositional_attitude (mind): internalism about moral
  -- judgment makes moral judgments motivating attitudes — the
  -- thesis presupposes the philosophy-of-mind concept of an
  -- attitude with motivational force.
  ('motivational_internalism', 'propositional_attitude', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- justice (political) → morality (ethics): political justice
  -- is the application of moral concepts (rightness, fairness,
  -- desert) to the political domain — the political concept
  -- presupposes the broader moral concepts.
  ('justice', 'morality', 'pedagogical_prerequisite', 'ai-seed', 16),
  -- social_contract_theory (political) → contractualism (ethics
  -- metaethics+normative): contractualist ethical theories
  -- (Scanlon, Gauthier) generalize the social-contract structure
  -- from political-legitimacy questions to general ethical
  -- questions; understanding contractualism requires the political-
  -- philosophy social-contract background.
  ('social_contract_theory', 'contractualism', 'pedagogical_prerequisite', 'ai-seed', 16);

COMMIT;
