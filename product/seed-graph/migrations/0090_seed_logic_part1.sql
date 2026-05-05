-- Migration: 0090_seed_logic_part1
-- Purpose: Fifth Phase 5 seed migration (first logic file) — philosophical
--   logic concepts and within-domain pedagogical_prerequisite edges.
--   Authored in S-0057 against task P5-03 "Logic seed (philosophical
--   logic — modality, conditionals, paradox, vagueness, paraconsistent,
--   deontic)" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the six clusters phase_5.md T1-B explicitly names for P5-03:
--   modal logic (alethic; possible-worlds Kripke semantics; the K/T/S4/S5
--   system hierarchy), conditionals (material vs indicative vs
--   subjunctive; Stalnaker-Lewis closest-world conditional logic),
--   semantic paradox (liar, Russell, Curry — set-theoretic and
--   self-reference paradoxes), vagueness (sorites paradox plus the
--   three contemporary responses: supervaluationism, epistemicism,
--   fuzzy/degree-theoretic), paraconsistent (the explosion principle
--   classical logic obeys, paraconsistent alternatives, the dialetheist
--   defense of true contradictions), deontic (standard deontic logic
--   and its two canonical paradoxes Chisholm contrary-to-duty and Ross
--   disjunctive permission). P5-03 is single-task (not pre-split a/b)
--   per phase_5.md T1-B; the entire logic subdomain seed lands in this
--   one migration.
-- Loads tables: public.nodes (26 INSERTs), public.edges (34 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 5 -> 6).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 5 at session boot (post-S-0056; verified
--     via Supabase MCP execute_sql at S-0057 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 6 (the
--     post-increment value).
--   * P5-01a epistemology core seed applied (0011) — depends_on
--     dependency satisfied since S-0050. P5-03 has no other Phase 5
--     dependencies; logic concepts are introduced de novo in this seed,
--     independent of metaphysics or ethics inventories. Cross-domain
--     bridges into epistemology (epistemic_closure → propositional_logic;
--     skepticism_epistemic argument-form structure), into metaphysics
--     (modality → modal_logic; possible_worlds → kripke_semantics), into
--     philosophy of language (sense/reference uses propositional_logic
--     and predicate_logic; speech-act theory uses conditional_logic),
--     and into philosophy of math (russell_paradox → set theory; classical
--     vs intuitionistic logic) all defer to P5-11 cross-bridges per
--     phase_5.md T2-G #1.
--   * No prior migrations under prefix 0090-0099; this is the first
--     logic seed file.
-- Postconditions:
--   * 26 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'logic'}, status=active, graph_version_added=6.
--   * 34 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=6. All edges are
--     within-domain (source and target both tagged logic);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 6.
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract). The
--     `_logic` suffix is used for nodes whose unsuffixed name is
--     plausibly ambiguous outside the logic subdomain (deontic_logic,
--     paraconsistent_logic, classical_logic, fuzzy_logic, conditional_
--     logic) so cross-bridge sessions can disambiguate semantically;
--     the bare `vagueness` and `dialetheism` are unambiguous because
--     no other subdomain claims those concepts. Modality already lives
--     at id `modality` in P5-02b (metaphysics-side semantic question);
--     this seed introduces `modal_logic` (the formal system) as a
--     distinct logic-side concept — the cross-domain bridge between
--     the two is P5-11's responsibility.
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts. Unlike P5-01b/P5-02b (which reference back into the
--     a-half's foundational concepts), P5-03 has no a/b split and
--     is internally self-contained — every prerequisite edge resolves
--     within the 26 nodes inserted here.
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is layered into 6 tiers:
--     T0: propositional_logic.
--     T1: predicate_logic, modal_logic, material_conditional,
--       semantic_paradox.
--     T2: classical_logic, accessibility_relation, indicative_
--       conditional, liar_paradox, russell_paradox.
--     T3: kripke_semantics, counterfactual_conditional, curry_paradox,
--       vagueness, explosion_principle.
--     T4: modal_systems_hierarchy, conditional_logic, sorites_paradox,
--       paraconsistent_logic, deontic_logic.
--     T5: supervaluationism, epistemicism, fuzzy_logic, dialetheism,
--       chisholm_paradox, ross_paradox.
--     Every edge below points from a lower-tier source to a higher-
--     tier target. validate.py's Kosaraju SCC check confirms post-apply
--     that the pedagogical_prerequisite subgraph remains acyclic
--     globally (the 0011 / 0016 / 0030 / 0036 prior seeds plus this
--     one's 34 edges, all together).
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: propositional_logic and
--     predicate_logic bridge to epistemology (P5-01a's epistemic_closure
--     uses propositional_logic for the inferential closure principle;
--     skepticism_epistemic's regress arguments use propositional
--     proof-theory); modal_logic bridges to metaphysics (P5-02b's
--     modality is the semantic question modal_logic formalizes;
--     possible_worlds is the model-theoretic structure kripke_semantics
--     interprets); modal_logic and kripke_semantics bridge to philosophy
--     of language (P5-08 will house Kripkean rigid-designation and
--     direct-reference semantics that build on modal_logic); russell_
--     paradox bridges to philosophy of mathematics (P5-09 / service
--     nodes P5-10 will house set theory, type theory, Zermelo-Fraenkel
--     axiom system); deontic_logic and conditional_logic bridge to
--     ethics (P5-04a's deontological theory uses deontic_logic for
--     formalizing ought-claims; the Chisholm contrary-to-duty paradox
--     bears on the metaethics of moral conflict); fuzzy_logic and
--     supervaluationism bridge to philosophy of language (P5-08 on
--     vagueness in linguistic meaning); paraconsistent_logic bridges
--     to ethics (moral-dilemma debates) and epistemology (rational-
--     belief in inconsistent evidence). All of these defer to P5-11.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md). The historical_influence predicate is
--     not used here either; logic's intellectual history (Frege ->
--     Russell -> Tarski -> Kripke -> Lewis -> Priest) is rich but the
--     historical-influence pass is deferred to a later phase (display-
--     only edges per PREDICATE_MANIFEST.md "historical_influence" row;
--     not part of P5-03's pedagogical-prerequisite scope).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0091-0099). Those
--     slots remain reserved for future logic extension if Phase 6+
--     telemetry warrants additional logic concepts (intuitionistic logic,
--     relevance logic, substructural logics, type theory, proof theory,
--     model theory, computability and the formal-systems infrastructure
--     that service nodes P5-10 may seed under their own range). This
--     seed completes P5-03's task at the granularity principle within
--     the 0090 file: 26 nodes covering the six explicitly-named clusters
--     at the umbrella-plus-canonical-positions density that P5-01a /
--     P5-01b / P5-02a / P5-02b each established. Logic is denser in
--     formal apparatus than the philosophical subdomains seeded so far
--     but the P5-03 task scope is the philosophical-logic curriculum
--     (the six clusters phase_5.md names), not the broader formal-logic
--     and proof-theory infrastructure.
-- Cross-cutting decisions:
--   * confidence_level distribution: 26/26 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the contemporary analytic
--     literature (Kripke, Lewis, Stalnaker, Priest, Williamson, Fine,
--     Tarski, Russell, Frege, Tarski, Chisholm, Ross, von Wright)
--     explicitly names. Mirrors P5-01a / P5-01b / P5-02a / P5-02b's
--     distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'logic'. Multiple cross-domain reaches exist (modal_logic into
--     metaphysics; propositional_logic into epistemology; deontic_logic
--     into ethics) but per phase_5.md T2-G #1, cross-domain tagging
--     belongs to P5-11. The canonical home for each of these concepts
--     in the analytic literature is logic / philosophical logic, so
--     the single tag is correct here. The borderline case is
--     conditional_logic (Stalnaker-Lewis) which is sometimes housed
--     under philosophy of language (counterfactual conditionals as a
--     semantic phenomenon); the formal apparatus belongs to logic
--     and the natural-language semantic question to language, so
--     conditional_logic is logic and counterfactual_conditional is
--     also logic in this seed (the language-side semantic concerns
--     about when natural-language conditionals are counterfactual
--     are a P5-08 cross-bridge concern).
--   * provenance: 'ai-seed' for every node and edge.
--   * Node selection rationale: 26 concepts cover the six clusters at
--     the granularity principle. Foundation (3): propositional_logic,
--     predicate_logic, classical_logic — these are the formal-system
--     prerequisites every other logic concept presupposes (modality is
--     a propositional extension; conditionals are a propositional /
--     modal question; paradox lives in the predicate-level set-
--     theoretic and self-referential apparatus; vagueness challenges
--     classical bivalence; paraconsistency rejects classical explosion;
--     deontic logic is a modal extension). Modal logic cluster (4):
--     modal_logic, accessibility_relation, kripke_semantics, modal_
--     systems_hierarchy — the formal apparatus for alethic modality
--     (necessity / possibility) plus the K/T/S4/S5 system hierarchy
--     anchored by Kripke's possible-worlds semantics. Conditionals
--     (4): material_conditional, indicative_conditional, counterfactual_
--     conditional, conditional_logic — the truth-functional connective,
--     the natural-language indicative-vs-subjunctive distinction, and
--     the Stalnaker (1968) and Lewis (1973) closest-world semantics
--     that interprets counterfactuals modally. Paradox (4): semantic_
--     paradox (umbrella), liar_paradox (Tarski 1933 hierarchy response;
--     Kripke 1975 truth-gap response), russell_paradox (set-theoretic
--     1901; resolved by ZFC's restricted-comprehension axiom; type
--     theory as alternative response), curry_paradox (the conditional
--     analogue of the liar; explosive in classical logic). Vagueness
--     (5): vagueness (umbrella), sorites_paradox (the heap paradox),
--     supervaluationism (Fine 1975 and the truth-value-gap response),
--     epistemicism (Williamson 1994 and the unknowable-sharp-cutoff
--     response), fuzzy_logic (degree-theoretic / many-valued response;
--     Zadeh 1965, Smith 2008). Paraconsistent (3): explosion_principle
--     (ex contradictione quodlibet — the classical-logic theorem
--     paraconsistency rejects), paraconsistent_logic (the family of
--     logics where contradictions don't trivialize the system),
--     dialetheism (Priest 1979 and the metaphysical commitment that
--     some contradictions are TRUE, not merely tolerable). Deontic (3):
--     deontic_logic (von Wright 1951; standard deontic logic SDL as
--     the modal logic of obligation / permission), chisholm_paradox
--     (Chisholm 1963 contrary-to-duty paradox; the canonical SDL
--     adequacy challenge), ross_paradox (Ross 1941 disjunctive
--     permission paradox; the second canonical SDL adequacy challenge).
--   * Edge structure: 34 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation tier (3) wires the formal foundations
--     into a layered prerequisite chain (propositional → predicate;
--     propositional → classical; predicate → classical). Modal tier (5)
--     wires propositional → modal_logic, then modal_logic →
--     accessibility_relation, modal_logic → kripke_semantics,
--     accessibility_relation → kripke_semantics, kripke_semantics →
--     modal_systems_hierarchy. Conditionals tier (6) wires propositional
--     → material_conditional, material_conditional → indicative_
--     conditional, indicative_conditional → counterfactual_conditional,
--     modal_logic → counterfactual_conditional (counterfactuals are
--     modal), counterfactual_conditional → conditional_logic, kripke_
--     semantics → conditional_logic. Paradox tier (6) wires propositional
--     → semantic_paradox, semantic_paradox → {liar_paradox, russell_
--     paradox}, predicate_logic → russell_paradox (Russell's paradox
--     uses unrestricted comprehension over predicates / sets), liar_
--     paradox → curry_paradox, material_conditional → curry_paradox
--     (Curry's paradox crucially uses the material conditional's
--     contraction-like inference). Vagueness tier (6) wires
--     classical_logic → vagueness (vagueness motivates moving away
--     from classical bivalence), vagueness → sorites_paradox, sorites_
--     paradox → {supervaluationism, epistemicism, fuzzy_logic} (the
--     three contemporary responses), classical_logic → fuzzy_logic
--     (fuzzy logic is the explicitly-degree-theoretic departure from
--     bivalence). Paraconsistent tier (4) wires classical_logic →
--     explosion_principle (the classical theorem paraconsistency
--     rejects), explosion_principle → paraconsistent_logic
--     (paraconsistency is defined by rejecting explosion), paraconsistent_
--     logic → dialetheism, liar_paradox → dialetheism (the liar is
--     dialetheism's most famous candidate for a true contradiction).
--     Deontic tier (4) wires modal_logic → deontic_logic (deontic logic
--     is a modal logic), deontic_logic → {chisholm_paradox, ross_
--     paradox}, conditional_logic → chisholm_paradox (the Chisholm
--     paradox crucially involves nested conditionals).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 6; DELETE FROM public.nodes WHERE id IN (the 26 ids inserted
--   here); UPDATE public.settings SET value = '5'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 61 statements
--   atomically — manual rollback above applies to the post-commit
--   window only. The 26 ids: propositional_logic, predicate_logic,
--   classical_logic, modal_logic, accessibility_relation, kripke_
--   semantics, modal_systems_hierarchy, material_conditional,
--   indicative_conditional, counterfactual_conditional, conditional_
--   logic, semantic_paradox, liar_paradox, russell_paradox, curry_
--   paradox, vagueness, sorites_paradox, supervaluationism,
--   epistemicism, fuzzy_logic, explosion_principle, paraconsistent_
--   logic, dialetheism, deontic_logic, chisholm_paradox, ross_paradox.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0036_seed_metaphysics_part1.sql
--   (P5-02b specialized seed; immediate-prior pattern reference and
--   the locus of `modality` which P5-03's `modal_logic` cross-bridges
--   to at P5-11);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 5 at session boot (post-S-0056 state); write 6 here;
-- every node/edge below carries graph_version_added = 6.
UPDATE public.settings
  SET value = '6'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 26 INSERTs covering the six logic clusters plus the foundation tier.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'propositional_logic',
    'Propositional Logic',
    ARRAY['logic'],
    'The simplest formal logic: sentences (atomic propositions) combined by truth-functional connectives (negation, conjunction, disjunction, material conditional, biconditional). A propositional formula''s truth value is fully determined by the truth values of its atomic constituents. The system is decidable, complete relative to its semantics, and the foundation on which predicate logic, modal logic, and most other formal systems extend.',
    'Teach propositional logic as the curriculum entry point to formal logic: introduce atomic letters P, Q, R standing for whole sentences; the five standard connectives ¬, ∧, ∨, →, ↔ each defined by its truth table; the notions of validity (true under every assignment), satisfiability (true under some assignment), and entailment (Γ ⊨ φ iff every assignment making Γ true makes φ true). Distinguish syntax (well-formed formulas) from semantics (truth conditions). Introduce a proof system — natural deduction or a Hilbert-style axiomatic system — and observe that the proof system is sound (every theorem is valid) and complete (every valid formula is a theorem). Propositional logic is the calibration anchor: every other logic in the curriculum is described as an extension of, restriction of, or alternative to it.',
    ARRAY['sentential_logic', 'zeroth_order_logic', 'classical_propositional_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'predicate_logic',
    'Predicate Logic',
    ARRAY['logic'],
    'Also called first-order logic. Extends propositional logic with internal sentence structure: individual constants and variables, predicates (one-place, two-place, n-place), and the universal (∀) and existential (∃) quantifiers binding variables. Sentences gain truth conditions relative to a model — a domain of individuals plus interpretations for the predicates and constants — instead of relative to assignments of truth values to atomic letters.',
    'First-order logic is the standard logical framework for mathematics and most analytic philosophy. Teach the syntax (terms, atomic formulas, quantified formulas) carefully, then the semantics: a model M = ⟨D, I⟩ where D is the domain and I assigns each predicate a subset of D^n. ∀x φ(x) is true at M iff every member of D satisfies φ; ∃x φ(x) iff some member does. Soundness and completeness theorems (Gödel 1929) hold. Key meta-theorems: compactness (a set of sentences is satisfiable iff every finite subset is), Löwenheim-Skolem (any satisfiable theory has a countable model). First-order logic is the *standard* logic — when philosophers speak of "the predicate calculus" without qualification, they mean classical first-order logic. Higher-order logic (quantifying over predicates and properties) is a strictly stronger system whose meta-theory differs sharply.',
    ARRAY['first_order_logic', 'quantificational_logic', 'fol'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'classical_logic',
    'Classical Logic',
    ARRAY['logic'],
    'The orthodox logical system of mainstream mathematics and analytic philosophy: classical propositional logic plus classical first-order predicate logic. Characterized by bivalence (every proposition is either true or false, never both, never neither), the law of excluded middle (P ∨ ¬P is a theorem for every P), the law of non-contradiction (¬(P ∧ ¬P) is a theorem), and the explosion principle (anything follows from a contradiction). Non-classical logics depart from one or more of these commitments.',
    'Classical logic is the system to which every other logic in this seed is contrasted. Teach the four characterizing commitments together — bivalence, excluded middle, non-contradiction, explosion — and note that they are tightly coupled: rejecting bivalence (intuitionism, paraconsistency, fuzzy logic) typically requires rejecting at least one of the others. The bivalence commitment is the first to come under pressure, motivated by vagueness (sorites cases seem neither clearly true nor clearly false), future contingents (Aristotle''s sea-battle), and presupposition failure ("the present king of France is bald"). Classical logic is the *default* in this curriculum: when later concepts speak of "logic" without qualification, classical logic is what they mean.',
    ARRAY['orthodox_logic', 'standard_logic', 'classical_first_order_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'modal_logic',
    'Modal Logic',
    ARRAY['logic'],
    'The formal logic of necessity and possibility. Extends propositional or first-order logic with two unary modal operators: □ (necessity / "it is necessary that") and ◇ (possibility / "it is possible that"), interdefinable via □P ↔ ¬◇¬P. Standard alethic interpretation: □P is true iff P is true at every possible world (under the relevant accessibility relation); ◇P iff true at some accessible world. The system extends naturally to deontic (obligation / permission), epistemic (knowledge / belief), and temporal (always / sometimes) modalities by reinterpretation of the operators.',
    'Modal logic is the central formal apparatus of philosophical logic and the principal contribution of 20th-century logic to philosophy. Teach the propositional fragment first: add □ and ◇ to the propositional language; the truth conditions invoke a Kripke frame ⟨W, R⟩ where W is a set of possible worlds and R ⊆ W × W is the accessibility relation. Different constraints on R (reflexive, symmetric, transitive, Euclidean) give different modal systems (T, B, S4, S5). The propositional modal logic K is the minimal system; T = K + reflexivity (□P → P); S4 = T + transitivity (□P → □□P); S5 = T + Euclidean (◇P → □◇P). Quantified modal logic adds quantifiers and raises the metaphysical question of trans-world identity (haecceity vs counterpart theory; this is the cross-bridge to P5-02b''s metaphysics modality). Don''t teach modal logic without teaching Kripke semantics — the formal pre-Kripke history (C.I. Lewis''s S1-S5 axiom systems, 1918-1932) is conceptually obscure without the model-theoretic interpretation Kripke (1959, 1963) supplied.',
    ARRAY['alethic_modal_logic', 'modal_propositional_logic', 'sentential_modal_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'accessibility_relation',
    'Accessibility Relation',
    ARRAY['logic'],
    'In Kripke semantics for modal logic, the binary relation R between possible worlds that determines which worlds are "accessible from" a given world. Necessity at world w is truth at every world accessible from w; possibility is truth at some accessible world. Different constraints on R (reflexivity, symmetry, transitivity, Euclideanness, seriality) correspond exactly to different modal axiom schemes and yield different modal systems.',
    'The accessibility relation is the technical heart of Kripke semantics. The crucial point is that *constraints on R determine which modal axioms are valid*. Reflexivity (∀w. wRw) corresponds exactly to the axiom T (□P → P) — what is necessary is true. Symmetry (∀w,v. wRv → vRw) corresponds to B (P → □◇P) — what is true is necessarily possible. Transitivity (∀w,v,u. wRv ∧ vRu → wRu) corresponds to 4 (□P → □□P) — what is necessary is necessarily necessary. Euclideanness (∀w,v,u. wRv ∧ wRu → vRu) corresponds to 5 (◇P → □◇P). Different interpretations of modality fit different constraints: alethic modality (logical necessity) plausibly fits S5 (R is an equivalence relation; what is necessary is necessary in any context); deontic modality fits seriality but typically rejects reflexivity (we have unsatisfied obligations); epistemic modality (knowledge) fits at least T but symmetry is contested (S4 vs S5 epistemic logics differ on positive vs negative introspection).',
    ARRAY['kripke_accessibility', 'modal_accessibility', 'frame_relation'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'kripke_semantics',
    'Kripke Semantics',
    ARRAY['logic'],
    'Saul Kripke''s 1959 / 1963 model-theoretic semantics for modal logic. A Kripke model is a triple ⟨W, R, V⟩ where W is a non-empty set of possible worlds, R ⊆ W × W is the accessibility relation, and V is a valuation assigning each atomic proposition the set of worlds where it holds. Truth of a formula is defined recursively at each world: □P holds at w iff P holds at every world accessible from w. The completeness theorems pair each axiomatic modal system (K, T, B, S4, S5) with the class of frames (no constraint, reflexive, symmetric, transitive, equivalence-relational) where exactly its theorems are valid.',
    'Kripke semantics is the conceptual unification that made modal logic a respectable mathematical subject. Before Kripke, the C.I. Lewis axiom systems S1-S5 (1918-1932) were syntactically motivated lists of axioms with no clear interpretive framework. Kripke''s contribution was to identify a *structural* semantic interpretation — possible worlds plus accessibility — that vindicates each system as the logic of frames satisfying specific accessibility constraints. The completeness theorems for K, T, B, S4, S5 are the canonical positive results. Pedagogically Kripke semantics is also where philosophical questions enter formally: what *is* a possible world (the metaphysics question P5-02b houses)? what *kind* of relation is accessibility (logical compatibility, physical compossibility, deontic permission, epistemic indistinguishability — different applications fit different interpretations)? The semantics is mathematical; the metaphysical interpretation is philosophical.',
    ARRAY['possible_worlds_semantics_logic', 'modal_model_theory'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'modal_systems_hierarchy',
    'Modal Systems Hierarchy',
    ARRAY['logic'],
    'The standard ordered family of normal modal propositional logics — K ⊂ T ⊂ S4 ⊂ S5 — generated by progressively strengthening the accessibility relation. K (no constraint) is the minimal normal modal logic. T (reflexive) adds □P → P. S4 (reflexive + transitive) adds □P → □□P. S5 (equivalence relation) adds ◇P → □◇P. Other systems (D, B, K4, S4.2, S4.3) fill out the lattice with deontic and other modal applications.',
    'Teach the hierarchy as a progressive enrichment, not a list of unrelated systems. K is the rock-bottom normal modal logic — its only modal commitment is K (□(P→Q) → (□P → □Q)) plus the necessitation rule (if ⊢ P then ⊢ □P). T adds reflexivity, which fits any modality where the actual is among the accessible (alethic, epistemic). S4 adds transitivity, which fits any modality where iterations don''t change the modal force (provability, knowledge under positive introspection). S5 adds Euclideanness, which gives an equivalence relation — the strongest standard system, typically the right logic for *logical* necessity (where the accessible worlds from w are a *single* equivalence class). Deontic logic fits D = K + seriality (∀w∃v. wRv) but typically not T (we have unfulfilled obligations, so □P → P fails). The hierarchy answers the question "which modal logic is correct?" with "it depends on the modality": alethic ≈ S5, deontic ≈ KD, epistemic ≈ S4 or S5 depending on introspection commitments, provability ≈ GL (the Gödel-Löb logic, with its idiosyncratic axiom □(□P → P) → □P).',
    ARRAY['k_t_s4_s5', 'normal_modal_logics', 'modal_logic_lattice'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'material_conditional',
    'Material Conditional',
    ARRAY['logic'],
    'The truth-functional connective → in classical propositional logic, defined by the truth table that makes P → Q false exactly when P is true and Q is false (and true in all three other rows). Equivalent to ¬P ∨ Q. The standard formal rendering of "if P then Q" in classical logic, but a notoriously imperfect match to the natural-language indicative — the so-called paradoxes of material implication (a false antecedent makes any conditional true; a true consequent makes any conditional true).',
    'The material conditional is straightforward as a piece of classical syntax: P → Q is true iff P is false or Q is true. The interesting questions are interpretive. The "paradoxes of material implication" are not really paradoxes — they are valid in classical logic, so they show that the material conditional is not the natural-language conditional, not that the system is broken. Examples: "If 2+2=5 then the moon is cheese" is materially true (false antecedent); "If snow is white then 2+2=4" is materially true (true consequent); but neither captures any genuinely conditional connection. The mismatch motivates the indicative_conditional and counterfactual_conditional concepts that follow, and conditional_logic''s closest-world semantics that displaces material implication for natural-language analysis. In *purely formal* contexts (mathematics, computer science), the material conditional is fine; the trouble is uniformly with natural-language modeling.',
    ARRAY['truth_functional_conditional', 'material_implication', 'horseshoe_conditional'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'indicative_conditional',
    'Indicative Conditional',
    ARRAY['logic'],
    'The natural-language conditional in the indicative mood ("if Oswald didn''t kill Kennedy, someone else did"), distinguished from the subjunctive / counterfactual ("if Oswald hadn''t killed Kennedy, someone else would have"). The two famously differ in truth value for the same antecedent and consequent (Adams 1970), so they cannot share truth conditions. Theories of the indicative include the material-conditional account (defended by Grice and Jackson via implicature), the suppositional account (Adams 1965, Edgington 1995), and the Stalnaker-Lewis closest-world account.',
    'Adams''s 1970 example is the canonical entry point: the indicative "if Oswald didn''t kill Kennedy, someone else did" is widely judged true (someone evidently killed Kennedy); the counterfactual "if Oswald hadn''t killed Kennedy, someone else would have" is widely judged false (we have no reason to think a backup assassin was waiting). Same antecedent, same consequent, opposite truth values — so the indicative and the subjunctive cannot share truth conditions. The dominant analyses: (i) the material-conditional account plus pragmatic implicature (Grice, Jackson 1979) — indicatives are materially true when antecedent is false, but conversational norms make assertion of such conditionals misleading; (ii) the suppositional / probability account (Adams 1965, Edgington 1995) — the assertability of "if P then Q" is the conditional probability Pr(Q | P), and indicatives don''t have full truth conditions but only acceptability conditions; (iii) the closest-world account (Stalnaker 1968) — indicatives, like subjunctives, are evaluated at the most similar world(s) where the antecedent holds, with the difference being which worlds count as "similar" (the indicative restricts to epistemically-live worlds; the subjunctive ranges more widely).',
    ARRAY['indicative_if_then', 'open_conditional'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'counterfactual_conditional',
    'Counterfactual Conditional',
    ARRAY['logic'],
    'The natural-language conditional in the subjunctive mood ("if it were raining, the streets would be wet"; "if Oswald hadn''t killed Kennedy, someone else would have"). Typically used to express what would have happened under a counter-to-fact supposition. Cannot be the material conditional: counterfactuals can have false antecedents (so the material reading would make them all vacuously true) yet still differ in truth value from one another. The standard analysis is closest-world: a counterfactual is true iff the consequent holds at the most similar world(s) where the antecedent holds.',
    'Counterfactuals — sometimes called subjunctive conditionals — are the second main natural-language conditional kind. They are the workhorses of causal reasoning ("if I hadn''t flipped the switch, the light wouldn''t have come on"), of historical reasoning ("if Hitler had been assassinated in 1943, Germany would have surrendered earlier"), and of metaphysical inquiry (Lewis''s counterfactual analysis of causation). The standard logical theory is Stalnaker (1968) or Lewis (1973): a counterfactual P □→ Q ("if P were the case, Q would be") is true at world w iff Q is true at every world in the *closest* P-world(s) to w under a similarity ordering. Stalnaker assumes a unique closest world (limit assumption); Lewis allows ties and infinite descent. The counterfactual is *not* monotonic ("if I had struck the match, it would have lit" doesn''t entail "if I had struck the match while submerged in water, it would have lit"), distinguishing it from the material conditional. Counterfactuals interact with modality: counterfactual-with-impossible-antecedent is generically vacuously true on the closest-world account, which Lewis accepts (no nearest impossible world) and others (Williamson, Nolan) push back on with impossible-worlds semantics.',
    ARRAY['subjunctive_conditional', 'would_conditional'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'conditional_logic',
    'Conditional Logic',
    ARRAY['logic'],
    'The formal logic of counterfactual conditionals developed by Robert Stalnaker (1968) and David Lewis (1973). Treats the counterfactual operator □→ as a non-truth-functional binary connective, evaluated at a Kripke-style frame whose accessibility structure encodes a similarity ordering on worlds. The system invalidates classical principles like strengthening the antecedent (P □→ Q does not entail (P ∧ R) □→ Q), transitivity (P □→ Q and Q □→ R do not entail P □→ R), and contraposition.',
    'Conditional logic is the canonical example of a logic where natural-language semantic phenomena drive formal innovation. The Stalnaker (1968) "A Theory of Conditionals" supplies the basic apparatus: a selection function f(w, P) returning the closest P-world to w; (P □→ Q) at w iff Q holds at f(w, P). Lewis (1973) "Counterfactuals" generalizes to a similarity *ordering* (no unique closest world; counterfactuals can have nondegenerate truth-value gaps). The crucial *negative* results are the ones to teach. Strengthening the antecedent fails: "if I had struck the match, it would have lit" does not entail "if I had struck the match while submerged, it would have lit" — the second has a different closest world. Transitivity fails: "if Hoover had been a Communist, he would have been a traitor" and "if Hoover had been a traitor, he would have been disgraced" don''t entail "if Hoover had been a Communist, he would have been disgraced" (the closest worlds differ). Contraposition fails likewise. The valid principles include modus ponens for □→, weakening the consequent, and the substitution of equivalent antecedents. Conditional logic shaped the philosophy-of-language treatment of conditionals for half a century; the cross-bridge to P5-08 is real.',
    ARRAY['stalnaker_lewis_conditional_logic', 'counterfactual_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'semantic_paradox',
    'Semantic Paradox',
    ARRAY['logic'],
    'The family of paradoxes generated by self-referential or improperly stratified semantic notions — truth, satisfaction, denotation, definability — including the liar, Curry, Berry, Grelling-Nelson, and Richard paradoxes. Distinguished from set-theoretic paradoxes (Russell, Burali-Forti, Cantor) which arise from set-theoretic comprehension principles, though the boundary is blurry. The standard Tarskian response is to forbid a semantically closed language from containing its own truth predicate; alternative responses include Kripke''s 1975 fixed-point construction, paracomplete and paraconsistent treatments.',
    'Semantic paradoxes are the central challenge any theory of truth must answer. The crucial structural fact is that intuitively-natural truth principles — the T-schema "⌜P⌝ is true iff P", the closure of truth under conjunction, etc. — combine with self-reference (a sentence about itself) to derive contradiction in classical logic. The dominant responses: (i) Tarskian hierarchy — no language contains its own truth predicate; truth-talk lives in a meta-language; the liar is ungrammatical; (ii) Kripkean fixed-point (1975 "Outline of a Theory of Truth") — sentences may have *no* truth value (truth-value gap); the liar is gappy; (iii) Revision theories (Gupta-Belnap 1993) — truth is governed by a revision rule whose limit-stage behavior is non-classical; (iv) Paracomplete responses (Field 2008) — reject excluded middle for truth-ascriptions; (v) Paraconsistent / dialetheic responses (Priest 1979) — accept the liar as a true contradiction. The semantic paradoxes are the clearest case where revising classical logic is *motivated by the data*, not by abstract dissatisfaction.',
    ARRAY['paradox_semantic', 'self_reference_paradox', 'truth_paradox'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'liar_paradox',
    'Liar Paradox',
    ARRAY['logic'],
    'The paradox generated by a sentence asserting its own falsity — "this sentence is false" (or, more carefully, λ: λ is false). Under naive truth principles, λ is true iff λ is false, contradicting bivalence (or generating absurdity classically). The Eubulides version (4th century BC) is the historical origin; the modern formal treatment uses the diagonal lemma to construct a sentence demonstrably equivalent to its own negation in any sufficiently strong language.',
    'The liar paradox is the canonical semantic paradox and the crucial test case for theories of truth. Teach with the strengthened liar — "this sentence is not true" (rather than "false") — to avoid Tarskian "neither true nor false" responses being immediate. Tarski''s 1933 hierarchy responds by forbidding languages from containing their own truth predicate: the liar is then ungrammatical (it tries to predicate an object-language truth predicate of itself), and truth must be relative to a meta-language. Kripke''s 1975 fixed-point construction permits self-applicative truth via a partial truth predicate that returns "undefined" for the liar (an explicit gap-theoretic option). Priest''s dialetheic response simply accepts the liar as both true and false (a true contradiction; LP-style logic prevents it from exploding). Field''s 2008 "Saving Truth from Paradox" is the canonical contemporary paracomplete defense (rejecting LEM for liar-like sentences; the resulting logic is non-classical without being dialetheic). The liar is also a useful diagnostic: any theory of truth committed to (i) the T-schema, (ii) self-reference, and (iii) classical logic faces the liar; relaxing any one of the three is the choice point.',
    ARRAY['eubulides_paradox', 'paradox_of_the_liar'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'russell_paradox',
    'Russell''s Paradox',
    ARRAY['logic'],
    'Bertrand Russell''s 1901 paradox in naive set theory: consider the set R of all sets that are not members of themselves. Then R ∈ R iff R ∉ R, contradicting bivalence. The paradox refutes the unrestricted comprehension principle (∀φ. {x : φ(x)} is a set) of Frege''s system in the Grundgesetze and Cantor''s naive set theory. The standard response is the Zermelo-Fraenkel restriction to *separation* (sets can be defined only as subsets of already-existing sets), with the cumulative-hierarchy iterative conception of set as the informal motivation.',
    'Russell''s paradox is the locus classicus of foundational crisis in mathematics. Russell discovered it 1901, communicated it to Frege June 1902, and Frege''s response in the appendix to Grundgesetze vol. 2 acknowledged that "arithmetic totters." The technical resolution in the Zermelo (1908) / Fraenkel (1922) ZF axiomatic set theory is the Axiom of Separation: {x ∈ A : φ(x)} is a set only when A is already known to be a set. R cannot be formed because the universe of all sets is not itself a set in ZF. The alternative resolution is Russell''s 1908 Type Theory: variables are stratified into types; "x ∈ x" is a type-violating expression and not well-formed. ZFC is the standard mainstream foundation; Type Theory underlies the constructive / homotopy-type-theoretic foundations program. Pedagogically Russell''s paradox links propositional logic to its real-world consequences in the foundations of mathematics; it also exemplifies the structural similarity to the liar (both involve a definable predicate applied to its own definability).',
    ARRAY['paradox_of_self_membership', 'russell_set_paradox'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'curry_paradox',
    'Curry''s Paradox',
    ARRAY['logic'],
    'Haskell Curry''s 1942 paradox: consider a sentence C asserting "if C is true then Q" for any Q. Naive truth principles plus the deduction theorem and contraction yield Q for arbitrary Q, including absurdities. Distinct from the liar in not requiring negation; distinct from Russell''s paradox in operating in propositional logic alone. Particularly stubborn because it survives in many non-classical responses to the liar.',
    'Curry''s paradox is the unsung hero of paradox theory. The construction: let C be a sentence equivalent to "if C is true then Q" (the diagonal lemma supplies one in any sufficiently expressive language). Reasoning: assume C is true. Then "if C is true then Q" holds, and modus ponens with our assumption gives Q. So if C is true, Q. By the deduction theorem (or conditional proof), "if C is true then Q" — but this just *is* C. So C, and by modus ponens once more, Q. Q was arbitrary; we''ve derived an arbitrary conclusion from no premises. The crucial point is that Curry''s paradox uses no negation. Many responses to the liar (paracomplete / paraconsistent treatments that revise the behavior of negation) leave Curry''s paradox untouched. Curry constructions block the dialetheic-ist easy answer to paradox: one cannot accept Curry as a "true contradiction" and hope to retain non-trivial logic, because Curry derives *Q* (anything you like), not just a contradiction. Responses to Curry typically restrict the structural rule of contraction (P → P → Q ⊢ P → Q) — relevance logic, linear logic, and some substructural logics drop contraction explicitly.',
    ARRAY['curry_lob_paradox', 'curry_conditional_paradox'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'vagueness',
    'Vagueness',
    ARRAY['logic'],
    'The phenomenon of predicates with borderline cases — "is bald", "is a heap", "is tall" — for which there is no sharp cutoff and the application of the predicate seems to admit of degree. Generates the sorites paradox and challenges classical bivalence. Distinguish vagueness in this sense from ambiguity (multiple distinct meanings), generality (a predicate covers a range of cases), and underspecification (a predicate is incompletely defined).',
    'Vagueness is the most important challenge to classical bivalence in 20th- and 21st-century philosophical logic. The Williamson 1994 / Keefe 2000 introductions are canonical. The phenomenon: take a clearly-bald man and the predicate "is bald". Adding one hair to a bald man does not make him non-bald — yet repeated application of this principle leads from the bald to the clearly-non-bald, which is absurd. This is the sorites pattern, and it generalizes: heap, tall, red, child. Vagueness has three philosophical responses: (i) supervaluationism — the predicate has multiple admissible "sharpenings"; what is true is what is true on every sharpening (truth-value gaps for borderline cases); (ii) epistemicism — there *is* a sharp cutoff but it is unknowable; bivalence is preserved (Williamson 1994); (iii) fuzzy / degree-theoretic — truth comes in degrees [0,1]; borderline cases have intermediate truth values. Each response trades different costs: supervaluationism blocks classical conditional proof; epistemicism strains credibility on the unknowability claim; fuzzy logic faces difficulties with the higher-order vagueness of "borderline" itself. Vagueness is also a major locus of the philosophy of language cross-bridge (P5-08): the semantic question of how vague predicates *mean* what they do is parallel to the logical question of how they *behave* in inferences.',
    ARRAY['vague_predicates', 'borderline_cases'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'sorites_paradox',
    'Sorites Paradox',
    ARRAY['logic'],
    'The paradox of the heap (Greek soros). One grain of wheat is not a heap. Adding one grain to a non-heap does not make a heap. Repeated application of the inductive premise leads from one grain (no heap) to one billion grains (still no heap), contradicting our judgment that a billion grains is a heap. The conditional, mathematical-induction, and line-drawing variants are all canonical formulations.',
    'The sorites paradox is the *form* vagueness takes as a logical puzzle. Classical formulation: (P1) one grain is not a heap; (P2) for any n, if n grains is not a heap, then n+1 grains is not a heap; (C) by mathematical induction, no number of grains makes a heap. P1 is uncontroversial; C is absurd; so P2 must fail somewhere — but where? Each instance of P2 ("if 100 grains is not a heap, 101 grains is not a heap") seems individually true. The three contemporary responses (supervaluationism, epistemicism, fuzzy logic) correspond to three diagnoses: supervaluationism rejects P2 globally while accepting all its instances on each sharpening (truth-value gaps prevent the universal generalization); epistemicism accepts P1 + ¬C and rejects some instance of P2 — there *is* a specific n where the instance fails (we just can''t know which); fuzzy logic accepts a continuous truth-value sequence where the inductive step has truth value just barely less than 1, so its repeated application gradually loses force. Pedagogically the sorites is the puzzle that motivates each of the three; teach it before any response.',
    ARRAY['heap_paradox', 'paradox_of_the_heap'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'supervaluationism',
    'Supervaluationism',
    ARRAY['logic'],
    'The treatment of vagueness on which a vague language has multiple admissible "sharpenings" (precise extensions for each vague predicate consistent with clear cases), and a sentence is *super-true* iff true on every admissible sharpening, *super-false* iff false on every sharpening, and lacks truth value otherwise. Originated by Bas van Fraassen for presupposition failure (1966); developed for vagueness by Kit Fine (1975) and Rosanna Keefe (2000).',
    'Supervaluationism is the truth-value-gap response to vagueness. The construction: the language has a vague predicate "bald"; an admissible sharpening is a precise extension of "bald" that classifies all clearly-bald men as bald, all clearly-non-bald men as non-bald, and is otherwise free to draw the line anywhere among borderline cases. A sentence is super-true iff true on every admissible sharpening, super-false iff false on every, and gappy (neither true nor false) otherwise. Borderline-case ascriptions ("Yul Brynner is bald" — let''s say borderline) are gappy. The key payoff is *penumbral connections*: "if Tom is bald and Tim has fewer hairs than Tom, then Tim is bald" is super-true even when "Tom is bald" is gappy and "Tim is bald" is gappy, because every sharpening that makes the first true also makes the second true. Difficulties: classical conditional proof fails (you can have Γ ⊨ P without ⊨ ¬Γ ∨ P in supervaluationist consequence); higher-order vagueness ("borderline borderline cases") generates an infinite regress; the very notion of "admissible sharpening" is itself plausibly vague.',
    ARRAY['supervaluationist_vagueness', 'fine_keefe_supervaluationism'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'epistemicism',
    'Epistemicism',
    ARRAY['logic'],
    'Timothy Williamson''s view (1994 "Vagueness") that vagueness is a *cognitive* phenomenon, not a semantic one. Vague predicates have sharp but unknowable cutoffs: there is some specific number n such that n grains is a heap and n-1 is not, but we cannot in principle know which n it is. Bivalence and classical logic are preserved; vagueness is reconceptualized as ineliminable ignorance about precise meanings.',
    'Epistemicism is the most metaphysically conservative response to vagueness — no truth-value gaps, no degrees of truth, no departure from classical logic — purchased at the cost of an unknowable-sharp-cutoff commitment that strikes many as incredible. Williamson''s 1994 defense rests on (i) the safety condition on knowledge (you know P only if there''s no nearby world where you believe P falsely), which entails that judgments at the borderline must be unsafe, hence not knowledge; (ii) the margin-for-error principle requiring that knowledge of P be reliable across small variations in P''s subject matter — applied to "bald", small variations in hair count must not flip the truth value of one''s judgment, which they would if one knew the cutoff; (iii) the meaning-determined-by-use thesis — meaning is fixed by speaker dispositions, but speakers don''t know exactly what their dispositions select. Epistemicism preserves bivalence and excluded middle, accepts the standard sorites response (some specific instance of the inductive premise is false, we just cannot know which), and gains striking systematicity at the cost of a counterintuitive epistemological claim about meaning. Williamson''s margin-for-error principles are themselves heavy lifting; epistemicism is widely viewed as either deeply correct or strikingly bizarre.',
    ARRAY['williamson_epistemicism', 'epistemic_theory_of_vagueness'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'fuzzy_logic',
    'Fuzzy Logic',
    ARRAY['logic'],
    'A many-valued / degree-theoretic logic in which truth values come in continuous degrees, typically the real interval [0, 1]. Connectives are interpreted by t-norms (for ∧) and their dual t-conorms (for ∨); negation is the order-reversing operation 1 − x. Originated by Łukasiewicz (1920s) for many-valued logics, applied to vagueness by Zadeh (1965 "Fuzzy Sets") and Smith (2008 "Vagueness and Degrees of Truth"). Sentences about borderline cases get intermediate truth values matching the degree to which the predicate applies.',
    'Fuzzy logic is the explicitly degree-theoretic response to vagueness. The basic apparatus: assign every atomic sentence a truth value in [0, 1]; conjunction takes the minimum (or another t-norm such as Łukasiewicz''s max(0, x+y-1) or Gödel''s product); disjunction takes the maximum (or t-conorm); negation is 1 - x. The sorites paradox dissolves naturally: each instance of the inductive premise has truth value just slightly less than 1 (the degree to which adding a grain preserves non-heap-hood), and repeated application of an only-slightly-less-than-1 conditional gradually loses force, so the conclusion has truth value below the threshold where it counts as assertible. Difficulties: (i) higher-order vagueness — the boundary between "fully heap" (truth value 1) and "borderline heap" (truth value 0.5) is itself vague; (ii) the choice of [0, 1] as the value space is ad hoc — why a continuum, why those endpoints, why those connectives; (iii) fuzzy logic does not preserve classical theorems like P ∨ ¬P (excluded middle gets truth value max(x, 1-x), which is below 1 unless x ∈ {0, 1}). Smith''s 2008 defense argues these costs are paid by any adequate theory of vagueness; fuzzy logic at least makes them explicit. Cross-bridge note: fuzzy logic''s core engineering applications (control systems, AI) are out of philosophy''s scope; the philosophical question is whether fuzzy logic''s degree-theoretic semantics correctly models vagueness.',
    ARRAY['degree_theoretic_logic', 'many_valued_logic_continuous'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'explosion_principle',
    'Explosion Principle',
    ARRAY['logic'],
    'The classical-logic theorem (also called *ex contradictione quodlibet*, ECQ) that anything follows from a contradiction: P ∧ ¬P ⊢ Q for any Q. Equivalently, an inconsistent set of premises classically entails everything. The principle is provable in classical propositional logic from disjunction-introduction plus disjunctive syllogism. Paraconsistent logics are exactly those that reject explosion — that allow inconsistent theories without trivializing them.',
    'Explosion is the classical-logic theorem that motivates paraconsistency. The classical proof: from P ∧ ¬P, infer P (∧-elimination), then P ∨ Q (∨-introduction), then ¬P (∧-elimination again), then Q (disjunctive syllogism on the latter two). The principle is a *theorem* of classical logic, not an additional axiom — to reject explosion you must reject one of the steps, typically disjunctive syllogism (paraconsistent logics like LP do this) or one of the introduction / elimination rules. The principle has the striking consequence that any inconsistent classical theory is *trivial* — entails every sentence in its language — which is why classical mathematicians treat the discovery of any contradiction (Russell''s paradox, the Burali-Forti) as a foundational crisis demanding immediate response. Pedagogically, *explosion is the bridge from the liar / Russell paradoxes to the paraconsistent and dialetheist responses*: if classical logic plus naive truth or naive comprehension is inconsistent, and classical logic plus inconsistency is trivial, then either we restrict the truth / comprehension principles (mainstream) or we adopt a non-explosive logic (paraconsistent). Both options are coherent; explosion is the axiom that forces the choice.',
    ARRAY['ex_contradictione_quodlibet', 'ex_falso_quodlibet', 'ecq', 'efq'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'paraconsistent_logic',
    'Paraconsistent Logic',
    ARRAY['logic'],
    'A logic in which the explosion principle (P ∧ ¬P ⊢ Q for all Q) is invalid — inconsistent theories do not trivialize. Paraconsistent logics permit the formal study of inconsistent-but-non-trivial information, with applications to inconsistent databases, naive truth theories, naive set theories, and the dialetheist treatment of paradox. Major systems include LP (Priest 1979 "logic of paradox"), relevance logics (Anderson-Belnap, with constraints on the logical-relevance of premise to conclusion), and adaptive logics (Batens). Paraconsistency is the rejection of explosion; dialetheism is the further claim that some contradictions are TRUE.',
    'Paraconsistency and dialetheism are easily confused. Paraconsistency is the formal property of a logic — explosion fails — and is *neutral* on whether contradictions can be true. Dialetheism is the metaphysical claim that some contradictions are true; dialetheism *requires* paraconsistency (otherwise one true contradiction makes everything true), but paraconsistency does not require dialetheism (one can be a paraconsistent logician about inconsistent databases without thinking the database accurately represents a true contradiction). Major paraconsistent systems: LP (Priest 1979) — three truth values {T, F, B (both)} with B the "both true and false" value; conjunction/disjunction/negation extended naturally; explosion fails because P ∧ ¬P can be B without forcing Q. Relevance logic (Anderson, Belnap, Routley) — the conditional → must satisfy a relevance constraint requiring premise and conclusion to share a propositional variable; explosion fails because P ∧ ¬P doesn''t share variables with arbitrary Q. Adaptive logics (Batens) — start with a paraconsistent base, then dynamically restore classical consequences for parts of the theory that turn out consistent. Pedagogically the contrast with classical_logic is the central point; paraconsistency motivates a re-evaluation of which classical theorems are essential vs derivable-from-explosion.',
    ARRAY['paraconsistency', 'non_explosive_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'dialetheism',
    'Dialetheism',
    ARRAY['logic'],
    'Graham Priest''s view (1979 "The Logic of Paradox"; 2006 "In Contradiction") that some sentences are both true AND false — that there are *true contradictions* (dialetheia, "two-way truths"). Distinguished from triviality (everything is true) by the underlying paraconsistent logic; LP is the standard underlying system. Motivated by the semantic paradoxes (the liar is the paradigm case of a true contradiction), set-theoretic paradoxes (Russell''s set is both a member and not), legal paradoxes (laws can have both-yes-and-no consequences), and certain quantum-logic phenomena.',
    'Dialetheism is paraconsistency''s most metaphysically committed defender. Priest''s 1979 LP supplies the underlying paraconsistent logic; "dialetheism" is the further claim that some contradictions are true — not merely tolerable formally, but *correctly describing reality*. The liar is dialetheism''s paradigm case: "this sentence is not true" is both true and not true, a fact about the truth predicate that classical theorists try to evade by hierarchical tricks but dialetheists embrace. Other candidate dialetheia: Russell''s set (R is both R-membered and not), legal contradictions (a statute permits and forbids the same action), motion (Zeno-style: at the moment of arrival, the moving object is both at and not at the destination — Priest''s "transitional periods" defense). The central charge against dialetheism is that it''s incredible: contradictions cannot really be true, period; *something* must be wrong with any argument concluding that they are. Priest responds that this conviction is itself a classical-logic prejudice that the paradoxes refute; the bullet-biting is correct, not crazy. Dialetheism is the most discussed contemporary non-classical position in metaphysics-of-logic; the debate is unresolved.',
    ARRAY['priest_dialetheism', 'true_contradictions'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'deontic_logic',
    'Deontic Logic',
    ARRAY['logic'],
    'The formal logic of obligation, permission, and prohibition. Founded by Georg Henrik von Wright (1951 "Deontic Logic") as a modal logic with operators O ("it is obligatory that") and P ("it is permitted that"), interdefinable via Pp ↔ ¬O¬p. Standard Deontic Logic (SDL) is the system K + D (the seriality axiom Op → Pp, ruling out moral dilemmas at the system level) interpreted with a Kripke frame whose accessibility relation R picks out "deontically perfect" worlds — worlds where everything obligatory is the case.',
    'Deontic logic is the most philosophically applied modal logic, used wherever ought-claims need formal treatment: ethics (formal characterization of consequentialism vs deontology), legal theory (formal modeling of statutes), AI ethics (representing constraints on agent behavior). Standard Deontic Logic (SDL) is the propositional modal system K plus the deontic-specific axiom D (Op → Pp — what is obligatory is permitted; equivalently, no proposition is both obligatory and forbidden) interpreted on a Kripke frame whose R relates the actual world to the "deontically perfect" worlds where every obligation is satisfied. SDL''s difficulties are well-known and motivate the literature: (i) the Chisholm contrary-to-duty paradox shows SDL cannot consistently formalize "you ought not lie, but if you lie you ought to lie convincingly"; (ii) Ross''s paradox shows the disjunctive permission "you ought to mail the letter" entails "you ought to mail the letter or burn it", which seems wrong; (iii) the gentle-murder paradox (Forrester) similarly generates absurdity from "you should not murder, but if you murder you should murder gently". Each paradox motivates a different SDL refinement: dyadic deontic logic (Hansson), defeasible deontic logic, agency-based deontic logic (Belnap-Horty stit logic). The cross-bridge to ethics (P5-04a) is real: deontic logic is where formal logic and normative ethics meet.',
    ARRAY['logic_of_obligation', 'logic_of_norms', 'sdl', 'standard_deontic_logic'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'chisholm_paradox',
    'Chisholm Paradox',
    ARRAY['logic'],
    'Roderick Chisholm''s 1963 contrary-to-duty obligation paradox: SDL cannot consistently formalize the joint claim that (1) it ought to be that Jones helps his neighbor, (2) it ought to be that if Jones helps his neighbor he tells him he is coming, (3) if Jones does not help his neighbor he ought not to tell him he is coming, (4) Jones does not help his neighbor. The four are jointly consistent in natural language but yield contradictory obligations in SDL.',
    'The Chisholm paradox is the canonical adequacy test for any deontic logic. Chisholm (1963 "Contrary-to-Duty Imperatives and Deontic Logic") presents the four claims: (1) Oh, (2) O(h → t), (3) ¬h → O¬t, (4) ¬h. Intuitively jointly consistent — Jones ought to help; if he does, he ought to announce; he didn''t help, so given that he didn''t, he ought not announce; we have the actual fact that he didn''t help. SDL derives a contradiction: from (1) and (2), by deontic K-axiom and modus ponens within the deontic context, Ot. From (3) and (4), by modus ponens, O¬t. Ot and O¬t together violate D (seriality): an obligation cannot conflict with the obligation of its negation. The paradox shows that SDL''s flat propositional treatment of obligations is wrong. The *contrary-to-duty* obligation in (3) is conditional on a violation having already occurred — and SDL has no way to express conditional obligations defined over violations. Responses: dyadic deontic logic (Bengt Hansson 1969) introduces an explicit conditional obligation operator O(t/¬h) read "given ¬h, t ought to be the case"; defeasible / non-monotonic deontic logics (Horty) treat secondary obligations as overriding primary ones in violation contexts; Belnap-Horty stit (1990s) reformulates obligations as constraints on agency rather than truth-functional propositions.',
    ARRAY['contrary_to_duty_paradox', 'chisholm_contrary_to_duty'],
    'INTERPRETED',
    'ai-seed',
    6
  ),
  (
    'ross_paradox',
    'Ross Paradox',
    ARRAY['logic'],
    'Alf Ross''s 1941 disjunctive permission paradox: in SDL, the obligation "you ought to mail the letter" (Om) entails "you ought to mail the letter or burn the letter" (O(m ∨ b)) by modal closure on disjunction-introduction. The latter conclusion seems wrong: the permission to burn the letter (carried by the disjunction''s right disjunct) was not obviously authorized by the original obligation.',
    'The Ross paradox (Ross 1941) is the second canonical SDL adequacy challenge. The argument: SDL closes obligations under classical consequence (if Op and ⊢ p → q then Oq, since the deontically perfect worlds where p is true are also worlds where q is true). So Om implies O(m ∨ b) by ∨-introduction. But the natural-language reading of "you ought to mail the letter or burn the letter" suggests you may *choose* between them, including burning — a permission to burn that the original "you ought to mail the letter" did not grant. Responses: (i) bite-the-bullet — the natural-language reading is misleading; O(m ∨ b) really just means that in deontically perfect worlds, m ∨ b holds, which is fine; (ii) restrict the closure principle — only deductive closure under "relevant" consequences (relevance logic''s solution), or only closure under conjunctive consequences; (iii) rich semantic accounts that distinguish "doing m" from "making m ∨ b true" (stit logic''s agentive operators). Ross''s paradox is less metaphysically dramatic than Chisholm''s but illustrates the same general lesson: SDL''s closure under classical consequence is too strong for natural-language obligations.',
    ARRAY['disjunctive_permission_paradox', 'ross_disjunctive_paradox'],
    'INTERPRETED',
    'ai-seed',
    6
  );

-- Edges: 34 INSERTs, all pedagogical_prerequisite, all within-domain.
-- Foundation tier (3): propositional → predicate; propositional → classical;
-- predicate → classical.
-- Modal tier (5): propositional → modal_logic; modal_logic →
-- accessibility_relation; modal_logic → kripke_semantics; accessibility_
-- relation → kripke_semantics; kripke_semantics → modal_systems_hierarchy.
-- Conditionals tier (6): propositional → material_conditional; material →
-- indicative; indicative → counterfactual; modal_logic → counterfactual;
-- counterfactual → conditional_logic; kripke_semantics → conditional_logic.
-- Paradox tier (6): propositional → semantic_paradox; semantic_paradox →
-- liar; semantic_paradox → russell; predicate → russell; liar → curry;
-- material_conditional → curry.
-- Vagueness tier (6): classical → vagueness; vagueness → sorites; sorites →
-- supervaluationism; sorites → epistemicism; sorites → fuzzy_logic; classical
-- → fuzzy_logic.
-- Paraconsistent tier (4): classical → explosion; explosion → paraconsistent;
-- paraconsistent → dialetheism; liar → dialetheism.
-- Deontic tier (4): modal_logic → deontic_logic; deontic_logic → chisholm;
-- conditional_logic → chisholm; deontic_logic → ross.

INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  ('propositional_logic', 'predicate_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('propositional_logic', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('predicate_logic', 'classical_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('propositional_logic', 'modal_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('modal_logic', 'accessibility_relation', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('modal_logic', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('accessibility_relation', 'kripke_semantics', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('kripke_semantics', 'modal_systems_hierarchy', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('propositional_logic', 'material_conditional', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('material_conditional', 'indicative_conditional', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('indicative_conditional', 'counterfactual_conditional', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('modal_logic', 'counterfactual_conditional', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('counterfactual_conditional', 'conditional_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('kripke_semantics', 'conditional_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('propositional_logic', 'semantic_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('semantic_paradox', 'liar_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('semantic_paradox', 'russell_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('predicate_logic', 'russell_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('liar_paradox', 'curry_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('material_conditional', 'curry_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('classical_logic', 'vagueness', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('vagueness', 'sorites_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('sorites_paradox', 'supervaluationism', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('sorites_paradox', 'epistemicism', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('sorites_paradox', 'fuzzy_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('classical_logic', 'fuzzy_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('classical_logic', 'explosion_principle', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('explosion_principle', 'paraconsistent_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('paraconsistent_logic', 'dialetheism', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('liar_paradox', 'dialetheism', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('modal_logic', 'deontic_logic', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('deontic_logic', 'chisholm_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('conditional_logic', 'chisholm_paradox', 'pedagogical_prerequisite', 'ai-seed', 6),
  ('deontic_logic', 'ross_paradox', 'pedagogical_prerequisite', 'ai-seed', 6);

COMMIT;
