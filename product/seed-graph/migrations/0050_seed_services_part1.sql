-- Migration: 0050_seed_services_part1
-- Purpose: Fourteenth Phase 5 seed migration (the service-node tier file)
--   — formal-logic primitives, math prerequisites, and history terminators
--   that several philosophy subdomains pedagogically require but that no
--   single subject canonically owns. Authored in S-0074 against task P5-10
--   "Service nodes seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md. P5-10
--   is a single-task subdomain per phase_5.md T1-B (the service-node tier
--   is well-bounded enough for a single migration; sub-range slots
--   0051-0059 remain reserved for any future Phase 6+ extension if
--   telemetry warrants additional foundational primitives).
--   Covers three sub-clusters identified at master-plan time:
--   (A) formal-logic primitives — sub-philosophical foundations of
--   reasoning that the philosophical-logic concepts in P5-03 (propositional
--   logic, predicate logic, modal logic, etc.) build on top of: truth_value
--   (the formal semantic value primitive — distinct from substantive
--   theories of truth canonical-homed in language); the principle of
--   bivalence; argument structure (premises and conclusion); validity
--   (form-based truth preservation); soundness (validity plus true
--   premises); the abstract notion of an inference rule; the canonical
--   propositional inference rules modus ponens and modus tollens; the
--   notion of a formal proof as a finite derivation; and counterexample as
--   the canonical method of refuting a universal claim;
--   (B) math prerequisites — the basic mathematical structures that
--   formal philosophy presupposes: set (the foundational collection
--   concept); function (many-to-one mapping, distinct from the seeded
--   metaphysical "relation"); axiom (primitive statement assumed without
--   proof); quantifier (the variable-binding operators ∀ and ∃);
--   probability as a formal measure; conditional probability; Bayes''s
--   theorem as the formal probability-inversion identity; and expected
--   value as a probability-weighted average;
--   (C) history terminators — doctrines and movements that several
--   philosophy subdomains historically descend from but that no single
--   subdomain canonically owns: presocratic naturalism (the early-Greek
--   project of explaining nature in non-mythological terms); Greek atomism
--   (Leucippus, Democritus, Epicurus); the Aristotelian four-cause
--   analysis (material, formal, efficient, final); medieval Scholasticism
--   as the philosophical-theological synthesis grounded in Aristotle;
--   Renaissance and early-modern mechanism (Descartes, Hobbes, Boyle —
--   matter in motion against Aristotelian teleology); the Vienna Circle
--   and logical positivism (1920s-1930s — the founding movement of
--   analytic philosophy); and Hegelian dialectic (thesis-antithesis-
--   synthesis as the developmental method of nineteenth-century German
--   idealism). All seven are concept/doctrine/movement nodes per
--   ADR 0008 (concepts not thinkers); none names an individual figure as
--   the canonical id.
--   Within-service edges span the three clusters in a layered DAG.
--   Cross-domain edges from service nodes into the philosophy subdomains
--   they pedagogically support (bayes_theorem ↔ bayesian_epistemology in
--   P5-01b and bayesianism_confirmation in P5-09; modus_ponens ↔
--   propositional_logic in P5-03; quantifier ↔ predicate_logic in P5-03;
--   set_mathematical ↔ russell_paradox in P5-03; aristotelian_four_causes
--   ↔ causation in P5-02a and the metaphysics-of-causation cluster;
--   greek_atomism ↔ physicalism in P5-07a and reductionism in metaphysics;
--   renaissance_mechanism ↔ substance_dualism in P5-07a and the mind-body
--   problem; vienna_circle_logical_positivism ↔ verificationism in P5-08
--   and falsificationism / demarcation_problem in P5-09; hegelian_
--   dialectic ↔ critique_of_metaphysics-style positions across multiple
--   subdomains) remain P5-11''s exclusive surface.
-- Loads tables: public.nodes (25 INSERTs), public.edges (28 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 14 -> 15).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 14 at session boot (post-S-0073 per
--     ROUTING.md narrative — most recent applied seed at the cross-
--     subdomain prefix range was 0080_seed_science_part1.sql which
--     wrote 14).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 15 (the
--     post-increment value).
--   * No prior migrations under prefix 0050-0059; this is the first
--     service-node seed file.
--   * P5-01a epistemology core applied (the only depends_on for P5-10).
--     No edge in this migration references philosophy-subdomain nodes —
--     within-service seeding here; cross-domain bridges from service
--     nodes to philosophy-subdomain nodes (the rich set named in the
--     Purpose block above) land at P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 25 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'service'}, status=active, graph_version_added=15.
--   * 28 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=15. All edges are
--     within-service (source and target both tagged service); cross-
--     domain edges from service nodes to philosophy-subdomain nodes are
--     P5-11''s exclusive responsibility.
--   * settings.graph_version = 15.
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Naming-collision discipline (per phase_5.md T2-G #2 bridge-concept
--     naming drift vector): suffixes (_logical, _mathematical,
--     _principle) are used on service-node ids whose unsuffixed name
--     would collide or near-collide with a seeded canonical-home concept.
--     truth_value (vs. seeded "truth", canonical-homed in language as the
--     truth-bearer concept and "truth_correspondence" as a substantive
--     theory of truth — the service-node id is the formal-semantic value
--     primitive); validity_logical and soundness_logical (no seeded
--     unsuffixed forms but the suffix preserves discoverability and
--     prevents accidental future re-authoring under different names);
--     argument_logical (the philosophical "argument" word is reserved
--     for substantive uses across subdomains — this is the formal-
--     reasoning structure); set_mathematical and function_mathematical
--     (vs. seeded "relation" canonical-homed in metaphysics as the
--     metaphysical category — set_mathematical is the formal collection
--     and function_mathematical is the formal mapping); axiom_
--     mathematical (axiom-as-primitive in formal systems; the unsuffixed
--     "axiom" is reserved for any future substantive uses);
--     bivalence_principle (the suffix preserves clarity that this is
--     the principle of bivalence, not the bivalent semantic values
--     themselves which are captured by truth_value); probability_
--     mathematical (vs. any future "probability" in epistemology / a
--     theory of credence — this is the formal measure-theoretic
--     primitive). counterexample, conditional_probability, bayes_theorem,
--     expected_value, modus_ponens, modus_tollens, formal_proof,
--     inference_rule, and quantifier are unsuffixed because no
--     collision exists in the seeded set or the seeded near-misses.
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also inserts.
--   * No edge cycles in the pedagogical_prerequisite subgraph. Tier
--     assignment (relative to this migration''s nodes only — there are
--     no cross-migration endpoints; tiers reflect longest-path-from-
--     a-cluster-root): T0 truth_value, set_mathematical,
--     presocratic_naturalism (the three cluster roots);
--     T1 bivalence_principle, argument_logical (formal-logic cluster
--     T1); function_mathematical, axiom_mathematical, quantifier,
--     probability_mathematical (math cluster T1); greek_atomism,
--     aristotelian_four_causes (history cluster T1);
--     T2 validity_logical, inference_rule, counterexample (formal-
--     logic T2); conditional_probability, expected_value (math T2);
--     scholasticism (history T2);
--     T3 soundness_logical, modus_ponens, modus_tollens (formal-logic
--     T3); bayes_theorem (math T3); renaissance_mechanism (history T3);
--     T4 formal_proof (formal-logic T4 — receives in-edges from
--     modus_ponens at T3 and from axiom_mathematical at T1 via the
--     math-to-logic service bridge, longest path is 4);
--     hegelian_dialectic (history T4 — distance-from-presocratic-root is
--     1 directly but pedagogical-flow places it after the renaissance/
--     scholastic chain); vienna_circle_logical_positivism (history T4
--     — receives in-edges from aristotelian_four_causes T1, renaissance_
--     mechanism T3, and hegelian_dialectic T4-by-pedagogy; the longest
--     pedagogical-prerequisite path through this migration is 4 hops
--     via presocratic_naturalism → aristotelian_four_causes →
--     scholasticism → renaissance_mechanism → vienna_circle_logical_
--     positivism). Every edge points from a strictly lower-tier node to
--     a strictly higher-tier node — no edges point back, no same-tier
--     edges. SCC freedom holds; validate.py''s Kosaraju check confirms
--     post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     no triple in this migration duplicates any other triple (all 28
--     edges are pairwise distinct in (source_id, target_id) since
--     edge_type is uniformly pedagogical_prerequisite). Note the multi-
--     in-edge nodes: formal_proof has two distinct in-edges (from
--     modus_ponens and from axiom_mathematical — the math-to-logic
--     service bridge); validity_logical has two distinct in-edges (from
--     argument_logical and from bivalence_principle); counterexample
--     has two distinct in-edges (from argument_logical and from
--     bivalence_principle); expected_value has two distinct in-edges
--     (from probability_mathematical and from function_mathematical);
--     vienna_circle_logical_positivism has three distinct in-edges
--     (from renaissance_mechanism, from aristotelian_four_causes, from
--     hegelian_dialectic) — each (source, target) pair is unique.
-- Non-responsibilities:
--   * Does not author cross-domain edges. The rich set of cross-domain
--     reaches from service nodes into the philosophy subdomains they
--     pedagogically support (named in the Purpose block above:
--     bayes_theorem ↔ bayesian_epistemology / bayesianism_confirmation;
--     modus_ponens ↔ propositional_logic; quantifier ↔ predicate_logic;
--     set_mathematical ↔ russell_paradox; aristotelian_four_causes ↔
--     causation; greek_atomism ↔ physicalism / reductionism;
--     renaissance_mechanism ↔ substance_dualism / mind-body problem;
--     vienna_circle_logical_positivism ↔ verificationism /
--     falsificationism / demarcation_problem; hegelian_dialectic ↔
--     critique-of-metaphysics positions) belongs to P5-11.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0051-0059).
--     Those slots remain reserved for any future Phase 6+ telemetry-
--     driven extensions to the service-node tier (e.g., specific
--     additional foundations the cross-bridges pass surfaces as missing:
--     measure theory primitives if probability nodes need deeper
--     grounding; basic linear algebra if specific philosophy-of-physics
--     specialization arrives; additional history terminators like
--     Stoicism, Kantian transcendental method, Husserlian phenomenology
--     as a method, Anglo-Saxon ordinary-language philosophy as a
--     methodology, post-1960s analytic-philosophy schools); this seed
--     completes P5-10''s task at the granularity principle within the
--     0050 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 25/25 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference''s entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here
--     is well-named in the standard logic / math / history-of-philosophy
--     curriculum (introductory logic textbooks like Hurley, Bergmann-
--     Moor-Nelson, or Sider; standard set-theory and probability
--     textbooks like Halmos, Enderton, Jech for set theory and Ross or
--     Feller for probability; standard history-of-philosophy surveys like
--     Russell, Copleston, Kenny, the Cambridge histories) explicitly
--     covers. Mirrors the thirteen prior Phase 5 subject seeds (P5-01a/b
--     epistemology, P5-02a/b metaphysics, P5-03 logic, P5-04a/b ethics,
--     P5-05 political philosophy, P5-06 aesthetics, P5-07a/b philosophy
--     of mind, P5-08 philosophy of language, P5-09 philosophy of science).
--   * domain[] cardinality: every node carries exactly one tag,
--     ''service''. The service tag is introduced in this migration as
--     the canonical home tag for the service-node tier — no node from
--     a prior P5 migration carries it. All cross-domain reach (every
--     service node has multiple subdomains it pedagogically supports)
--     belongs to P5-11 per phase_5.md T2-G #4 (domain-tag cardinality
--     explosions vector). The single ''service'' tag here is correct
--     because the canonical home for each of these concepts is "the
--     foundational tier that other subdomains build on" — they are
--     definitionally not the property of any single philosophy subdomain.
--   * provenance: ''ai-seed'' for every node and edge. Same as P5-01a/b,
--     P5-02a/b, P5-03, P5-04a/b, P5-05, P5-06, P5-07a/b, P5-08, P5-09.
--   * Node selection rationale: 25 concepts cover the three sub-clusters
--     at the granularity principle:
--     (A) formal-logic primitives (10) [truth_value, bivalence_principle,
--     argument_logical, validity_logical, soundness_logical, inference_
--     rule, modus_ponens, modus_tollens, formal_proof, counterexample]
--     — semantic-value primitive, the principle that fixes how many
--     truth values there are, the formal-reasoning structure, the form-
--     based notion of validity, the validity-plus-true-premises notion
--     of soundness, the abstract notion of an inference rule, the two
--     canonical propositional rules, the syntactic concept of a formal
--     proof, and the canonical method of universal-claim refutation by
--     a single instance. Together these primitives ground the
--     philosophical-logic concepts in P5-03 (propositional_logic,
--     predicate_logic, modal_logic, classical_logic, etc.) and the
--     epistemological concepts that depend on logical reasoning in
--     P5-01a (justified_true_belief, knowledge as inferential, the
--     analysis of knowledge tradition) without re-authoring those
--     downstream concepts.
--     (B) math prerequisites (8) [set_mathematical, function_
--     mathematical, axiom_mathematical, quantifier, probability_
--     mathematical, conditional_probability, bayes_theorem, expected_
--     value] — the foundational collection concept on which both
--     functions and probability are built; the formal mapping concept;
--     the primitive-statement-assumed concept (axioms ground formal
--     proofs); the variable-binding operators that ground predicate
--     logic; the formal probability measure; conditional probability
--     as the central operation; Bayes''s theorem as the formal identity
--     that drives Bayesian epistemology, Bayesian confirmation, and
--     Bayesian decision theory; expected value as the probability-
--     weighted average that drives formal decision theory and the
--     statistical methodology that several philosophy-of-science topics
--     presuppose. Together these primitives ground bayesian_epistemology
--     in P5-01b, bayesianism_confirmation in P5-09, predicate_logic and
--     classical_logic in P5-03, and the formal-decision-theoretic
--     framing of utilitarianism in P5-04a.
--     (C) history terminators (7) [presocratic_naturalism, greek_
--     atomism, aristotelian_four_causes, scholasticism, renaissance_
--     mechanism, vienna_circle_logical_positivism, hegelian_dialectic]
--     — the early-Greek non-mythological-explanation project as the
--     founding moment of Western philosophy; Greek atomism as the
--     ancestor of modern materialism / physicalism; Aristotle''s four-
--     cause analysis as the conceptual structure that medieval
--     Scholasticism systematized and that Renaissance mechanism
--     overthrew; medieval Scholasticism as the philosophical-theological
--     synthesis that made Aristotle the dominant figure for a millennium;
--     Renaissance and early-modern mechanism as the founding moment of
--     modern science and modern materialism; the Vienna Circle and
--     logical positivism as the founding movement of twentieth-century
--     analytic philosophy and the proximate ancestor of the philosophy-
--     of-language and philosophy-of-science topics seeded in P5-08 and
--     P5-09; Hegelian dialectic as the central nineteenth-century
--     alternative methodology that the Vienna Circle defined itself
--     against (the Carnap-Heidegger contrast). Each of these is a
--     historical position or methodological tradition, not an
--     individual figure (per ADR 0008); each is referenced by multiple
--     philosophy subdomains but canonical-homed nowhere prior to this
--     seed.
--   * Edge structure: 28 edges total, all pedagogical_prerequisite, all
--     within-service. Formal-logic cluster (11): truth_value →
--     bivalence_principle (bivalence is a principle ABOUT truth values);
--     truth_value → argument_logical (formal-reasoning structure
--     presupposes truth-valued sentences); bivalence_principle →
--     validity_logical (classical validity is defined relative to
--     bivalent truth-functional semantics); argument_logical →
--     validity_logical (validity is a property of arguments); validity_
--     logical → soundness_logical (soundness adds the truth-of-premises
--     requirement on top of validity); argument_logical → counterexample
--     (counterexamples are arguments showing universal claims fail);
--     bivalence_principle → counterexample (counterexamples presuppose
--     bivalence — a single false instance refutes the universal); argument_
--     logical → inference_rule (inference rules generate sound steps
--     within arguments); inference_rule → modus_ponens (the canonical
--     propositional inference rule); inference_rule → modus_tollens
--     (the canonical contrapositive form); modus_ponens → formal_proof
--     (formal proofs use inference rules including MP). Math cluster (8):
--     set_mathematical → function_mathematical (functions are special
--     sets of ordered pairs); set_mathematical → axiom_mathematical
--     (axioms are statements about set-theoretic primitives in modern
--     mathematics); set_mathematical → quantifier (quantifiers range
--     over a domain — typically a set); set_mathematical → probability_
--     mathematical (probability is a measure on a sample space — a
--     set); probability_mathematical → conditional_probability (the
--     central operation on the formal measure); conditional_probability
--     → bayes_theorem (Bayes''s theorem is the conditional-probability
--     inversion identity); probability_mathematical → expected_value
--     (the probability-weighted average); function_mathematical →
--     expected_value (E[X] is a function of the probability
--     distribution). History cluster (5): presocratic_naturalism →
--     greek_atomism (atomism is a presocratic naturalist position);
--     presocratic_naturalism → aristotelian_four_causes (Aristotle''s
--     causal analysis responds to and synthesizes presocratic causal
--     theories); aristotelian_four_causes → scholasticism (medieval
--     Aristotelianism inherits and systematizes the four-cause analysis);
--     scholasticism → renaissance_mechanism (Renaissance and early-
--     modern mechanism arose in opposition to Scholastic-Aristotelian
--     teleology); aristotelian_four_causes → renaissance_mechanism (the
--     mechanist break is most pointedly the rejection of the Aristotelian
--     formal and final causes — the direct edge from four-causes to
--     mechanism captures the conceptual rather than purely temporal
--     descent). Cross-cluster service-to-service bridges (4):
--     axiom_mathematical → formal_proof (formal proofs start from
--     axioms; this bridge ties the math cluster into the formal-logic
--     cluster pedagogically — students of formal proof need to
--     understand that axioms are the proof-theoretic primitive starting
--     points, not just the logical inference rules); aristotelian_four_
--     causes → vienna_circle_logical_positivism (the Vienna Circle
--     positivists explicitly rejected the four-cause analysis as
--     metaphysical pseudo-science — pedagogically essential to
--     understanding what the positivists thought they were rejecting);
--     renaissance_mechanism → vienna_circle_logical_positivism (the
--     mechanist empiricist tradition — Hobbes, Locke, Hume — feeds
--     into early-twentieth-century logical empiricism through the
--     British empiricist line via Mach and Russell); hegelian_dialectic
--     → vienna_circle_logical_positivism (the Vienna Circle defined
--     itself partly against German idealist dialectic — Carnap''s
--     "Elimination of Metaphysics through Logical Analysis of Language"
--     uses Heidegger as the foil but the broader target is the
--     Hegelian-idealist tradition; pedagogically essential for the
--     Carnap-Heidegger contrast in the founding-of-analytic-philosophy
--     story). The history cluster therefore has both intra-cluster
--     temporal-descent edges and the three cross-cluster bridges into
--     vienna_circle_logical_positivism that pedagogically connect the
--     ancient/medieval/early-modern history to the founding of modern
--     analytic philosophy.
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 15; DELETE FROM public.nodes WHERE id IN (the 25 ids inserted
--   here); UPDATE public.settings SET value = ''14''::jsonb WHERE key =
--   ''graph_version''; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 54 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry);
--   product/seed-graph/migrations/0080_seed_science_part1.sql (P5-09
--   philosophy-of-science seed; pattern reference for the most recent
--   single-task subject subdomain seed and the canonical-home-conflict
--   resolution discipline);
--   product/seed-graph/migrations/0090_seed_logic_part1.sql (P5-03
--   philosophical-logic seed; the philosophical-logic concepts that
--   build on top of the formal-logic primitives in this seed);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 14 at session boot (post-S-0073 state per ROUTING.md
-- narrative); write 15 here; every node/edge below carries
-- graph_version_added = 15.
UPDATE public.settings
  SET value = '15'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 25 INSERTs covering the three service-node sub-clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'truth_value',
    'Truth Value',
    ARRAY['service'],
    'The formal-semantic primitive: the value (typically true or false) that a sentence or proposition takes under an interpretation. The service-tier concept distinct from substantive philosophical theories of truth (correspondence, coherence, deflationary, pragmatist) which are canonical-homed in philosophy of language. In classical bivalent logic, the truth values are exactly two — true (T, 1) and false (F, 0); in many-valued logics they may be more numerous (Lukasiewicz three-valued: true, false, indeterminate; fuzzy logic: the real interval [0, 1]); in paracomplete or paraconsistent logics they may be structured differently (gappy or glutty values).',
    'For students approaching formal logic, distinguish two questions: (1) what *kinds* of values can sentences take? — the truth-value question, answered by the choice of semantic framework (bivalent, three-valued, fuzzy, etc.); (2) what *is* truth, philosophically? — the substantive theory question, answered by correspondence, coherence, deflationary, or pragmatist accounts. Beginning logic courses assume bivalent semantics implicitly; the truth-value primitive is the formal hook on which all of propositional and first-order semantics hangs. Students should see that the choice of how many truth values to admit is a methodological choice that drives the choice of logic — classical logic presupposes bivalence; many-valued, intuitionistic, paraconsistent, and fuzzy logics each weaken or modify the bivalent assumption.',
    ARRAY['truth_values', 'semantic_value', 'logical_value'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'bivalence_principle',
    'Principle of Bivalence',
    ARRAY['service'],
    'The semantic principle that every meaningful proposition is either true or false — exactly two truth values, no third option. The foundational assumption of classical logic, distinguishing it from intuitionistic logic (which rejects the law of excluded middle as a theorem but may still accept bivalence as a meta-principle), from many-valued logics (which admit more than two truth values), and from supervaluationism / paracomplete logics (which admit truth-value gaps). Bivalence is sometimes conflated with the law of excluded middle (P or not-P) but is conceptually distinct — bivalence is a semantic principle about truth values, while excluded middle is a syntactic theorem of classical logic.',
    'For students, separate three closely related but distinct claims: (1) the law of non-contradiction — no proposition is both true and false; (2) the law of excluded middle — every proposition is true or its negation is true; (3) the principle of bivalence — every proposition has exactly one of two truth values. In classical logic all three hold and are mutually reinforcing, but they come apart in non-classical logics. Intuitionistic logic accepts non-contradiction but rejects excluded middle as a logical theorem (intuitionists insist on constructive proof); many-valued logics may accept excluded middle in some forms but reject bivalence; supervaluationism rejects bivalence but preserves excluded middle. Use the distinctions to motivate the move from classical to non-classical semantics in P5-03 logic topics (vagueness, paradox, paraconsistency).',
    ARRAY['bivalence', 'principle_of_bivalence'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'argument_logical',
    'Argument (Logical)',
    ARRAY['service'],
    'The formal-reasoning primitive: a finite sequence of statements (the premises) followed by a single statement (the conclusion), where the premises are offered in support of the conclusion. The service-tier concept distinct from "argument" in the conversational or rhetorical senses, distinct from "argument" as the logical-philosophical term for the position-defending discourse type, and distinct from "argument" as the formal-semantic term for the entity that fills a predicate''s argument-place (which is captured by the seeded epistemological / semantic notions of singular term and reference).',
    'For students, frame logical argument by contrast with the surrounding senses of the word: a logical argument is not necessarily a quarrel (everyday sense), not necessarily a defense of a controversial position (rhetorical sense), and not the entity-that-fills-a-predicate-place (formal-semantic sense). It is a structured pair: a set of premises plus a conclusion, with the premises offered as reasons for the conclusion. The structural notion grounds the central evaluative notions of validity (does the conclusion follow from the premises?) and soundness (is the argument valid AND are the premises true?). Walk through a sample argument explicitly: numbered premises, a horizontal rule, the conclusion below — the textbook display format makes the structure visible. Once students see the structural framing, the leap to formal validity-checking is short.',
    ARRAY['logical_argument', 'argument_structure'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'validity_logical',
    'Validity (Logical)',
    ARRAY['service'],
    'The form-based truth-preservation property of arguments: an argument is valid iff it is impossible for all premises to be true and the conclusion false. The central evaluative notion of formal logic — validity is *necessary* truth preservation, not just truth-preservation in the actual case. Validity is a property of *form*: an argument''s validity depends only on its logical structure, not on the contents of its propositions. Two arguments with the same logical form are either both valid or both invalid.',
    'For students, the canonical illustration is the contrast between a valid argument with false premises (and a true or false conclusion: "All cats are dogs; all dogs are reptiles; therefore all cats are reptiles" — valid form, false premises, false conclusion) and an invalid argument with true premises and a true conclusion ("All cats are mammals; some mammals are dogs; therefore all cats are dogs" — true premises, false conclusion, hence invalid). The contrast hammers home that validity is about form, not about actual truth values: a valid argument *would* preserve truth from premises to conclusion *if* the premises were true. Walk through the modus-ponens form ("If P then Q; P; therefore Q") and contrast with the affirming-the-consequent fallacy ("If P then Q; Q; therefore P") to make the form-dependence of validity crisp. The semantic definition (no truth-value assignment makes premises all true and conclusion false) and the syntactic definition (derivability via inference rules in a formal proof system) coincide for classical logic — a non-trivial result called the soundness-and-completeness of classical logic.',
    ARRAY['validity', 'logical_validity'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'soundness_logical',
    'Soundness (Logical)',
    ARRAY['service'],
    'The composite property of arguments: an argument is sound iff it is valid AND all its premises are actually true. Validity guarantees that *if* the premises are true then the conclusion is true; soundness adds the actual-truth-of-premises clause to give an unconditional guarantee that the conclusion is true. Distinct from "soundness" as the meta-logical property of formal proof systems (a system is sound iff every theorem provable in it is semantically valid) — the meta-logical sense is captured by separate course material; the service-tier id here is the argument-property sense.',
    'For students, soundness is the gold standard of evaluation: a sound argument *demonstrates* its conclusion. Most actual reasoning is at best valid-and-disputed-premises, since the heavy lifting in real argumentation is establishing the truth of the premises. Formal logic teaches validity-checking because validity is the part that depends only on form and is therefore systematizable; soundness depends on the empirical or substantive truth of premises and falls outside formal logic''s domain. The pedagogical sequencing is: introduce argument structure → introduce validity (the form-based property logic can systematize) → introduce soundness (the validity-plus-true-premises property that is the actual goal of reasoning but that depends on extra-logical truth-assessment of premises). Note the meta-logical sense (system is sound iff every provable formula is semantically valid) — this is a distinct concept covered when students get to formal proof systems and is often paired with completeness (every semantically valid formula is provable).',
    ARRAY['soundness', 'logical_soundness'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'inference_rule',
    'Inference Rule',
    ARRAY['service'],
    'The syntactic primitive of formal proof systems: a rule that licenses the derivation of one or more conclusion-formulas from one or more premise-formulas based purely on the syntactic shape of those formulas. Inference rules are the building blocks of formal proofs — each step of a proof must be justified either as an axiom (a starting point, primitive assumption) or as the application of an inference rule to one or more earlier lines of the proof. The most familiar inference rules are propositional: modus ponens, modus tollens, hypothetical syllogism, disjunctive syllogism, conjunction-introduction, conjunction-elimination, etc. First-order rules add quantifier-introduction and quantifier-elimination rules.',
    'For students, the inference-rule concept marks the transition from semantic reasoning ("the argument is valid because no truth-assignment makes premises true and conclusion false") to syntactic reasoning ("the conclusion can be derived from the premises by a finite sequence of rule applications"). The semantic and syntactic perspectives are connected by the soundness-and-completeness theorem: a formula is semantically valid iff it is syntactically derivable. Walk through one or two paradigm inference rules in detail (modus ponens is the canonical example) and show how a multi-step formal proof chains rule applications. The natural-deduction style of presentation (introduction and elimination rules for each connective) is pedagogically friendlier than Hilbert-style axiomatic systems for first-time students; either way, the key concept is that inference rules are the syntactic building blocks of derivations.',
    ARRAY['rule_of_inference', 'derivation_rule'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'modus_ponens',
    'Modus Ponens',
    ARRAY['service'],
    'The canonical propositional inference rule: from "if P then Q" and "P", derive "Q". The form-name is Latin for "method of affirming" (affirming the antecedent of a conditional licenses inferring the consequent). The most basic and most frequently invoked inference rule in formal proof systems and in everyday deductive reasoning. Distinct from the affirming-the-consequent fallacy (from "if P then Q" and "Q", incorrectly deriving "P") which is the canonical illustration of an *invalid* inference form.',
    'For students, modus ponens is both the simplest formal inference rule and the rule whose application is most often implicit in everyday reasoning. Walk through the form schematically (P → Q; P; ∴ Q), then with a concrete instance ("If it is raining, the streets are wet; it is raining; therefore the streets are wet"), then with a multi-step argument that uses it twice or three times. Pair the introduction of modus ponens with the affirming-the-consequent fallacy: the surface similarity (both have one conditional and one categorical premise) makes the contrast pedagogically essential. Modus ponens is also the rule that grounds the deduction theorem (if Γ, P ⊢ Q then Γ ⊢ P → Q) — the syntactic counterpart to the conditional-introduction step in semantic reasoning. Once students have modus ponens internalized, the broader notion of an inference rule generalizes naturally and the move to multi-rule formal proof systems becomes easier.',
    ARRAY['mp_rule', 'detachment_rule'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'modus_tollens',
    'Modus Tollens',
    ARRAY['service'],
    'The contrapositive inference rule: from "if P then Q" and "not Q", derive "not P". The form-name is Latin for "method of denying" (denying the consequent of a conditional licenses inferring the negation of the antecedent). Together with modus ponens, the second canonical propositional inference rule for the conditional. Distinct from the denying-the-antecedent fallacy (from "if P then Q" and "not P", incorrectly deriving "not Q") which is the affirming-the-consequent fallacy''s mirror image.',
    'For students, modus tollens is pedagogically the bridge from elementary deductive reasoning to scientific reasoning: it captures the core logical structure of falsificationist scientific testing per Popper (P5-09). The schema is: a theory T predicts observation O; we observe not-O; therefore not-T. The inference is valid; whether the application is appropriate in any given case depends on auxiliary assumptions (the Duhem-Quine point — the negation of T might really be the negation of an auxiliary, not of T itself), but the underlying logical form is exactly modus tollens. Walk through the form schematically (P → Q; ¬Q; ∴ ¬P), then with a concrete instance ("If it is raining, the streets are wet; the streets are not wet; therefore it is not raining"), then with a scientific-testing instance to set up the cross-domain connection to philosophy of science. Pair with the denying-the-antecedent fallacy ("If P then Q; not P; therefore not Q" — invalid) for the mirror-image contrast.',
    ARRAY['mt_rule', 'denying_consequent'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'formal_proof',
    'Formal Proof',
    ARRAY['service'],
    'The syntactic-derivation primitive of formal logic: a finite sequence of formulas where each formula is either an axiom of the proof system, an assumption (in proofs from premises), or follows from earlier formulas in the sequence by an inference rule. Formal proofs are the syntactic counterpart to semantic validity: a conclusion is provable from a set of premises iff every model of the premises is a model of the conclusion (the soundness-and-completeness theorem of classical first-order logic, due to Kurt Gödel 1929-1930). The proof-theoretic perspective complements the model-theoretic perspective on logical consequence; both are central to mathematical logic.',
    'For students, frame formal proof as the systematic, mechanical counterpart to informal deductive reasoning. An informal mathematical proof presents the key steps in natural language with the inference rules implicit; a formal proof spells out every step explicitly with each line justified by an axiom, an assumption, or an inference rule. Different formalisms present formal proofs differently: Hilbert-style axiomatic systems (many axioms, few inference rules — typically just modus ponens and generalization), natural-deduction systems (few axioms, many inference rules — pairs of introduction and elimination rules for each connective), sequent-calculus systems (proof structure as inference between sequents). All are equivalent in expressive power; pedagogically, natural deduction is friendliest for beginners. The concept of formal proof is the gateway to several deep results: Gödel''s incompleteness theorems (no consistent formal system rich enough for arithmetic can prove all true statements about arithmetic), the Curry-Howard correspondence (proofs are programs), the soundness-and-completeness theorems of classical logic.',
    ARRAY['proof_formal', 'derivation_formal', 'syntactic_proof'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'counterexample',
    'Counterexample',
    ARRAY['service'],
    'The canonical method of refuting a universal claim: produce a single instance for which the claim fails. A universal generalization "all F are G" is refuted by exhibiting an F that is not G. The asymmetry between confirmation (no finite number of instances conclusively confirms a universal generalization) and refutation (a single counterexample conclusively refutes it) is one of the central asymmetries in scientific and philosophical reasoning, and grounds the falsificationist methodology in philosophy of science (P5-09).',
    'For students, the counterexample method is the workhorse refutation strategy in mathematics and philosophy. Walk through the strategy with a mathematical case ("all primes greater than 2 are odd" — refuted? no, this one is actually true, but we can refute "every odd number greater than 1 is prime" by noting 9 = 3 × 3) and a philosophical case (Gettier 1963 refuted "knowledge is justified true belief" by producing the canonical Gettier cases — situations of justified true belief that intuitively are not knowledge). The Gettier example connects directly to seeded epistemological content (gettier_problem in P5-01a) and shows students how counterexample reasoning drives substantive philosophical progress. Pair the counterexample concept with the bivalence-principle dependency: a counterexample refutes a universal claim only on the assumption that the claim has a definite truth value — paracomplete logics that allow truth-value gaps (e.g., for vague predicates) complicate the counterexample method, since the failed instance might be neither clearly true nor clearly false.',
    ARRAY['counter_example', 'refutation_by_instance'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'set_mathematical',
    'Set (Mathematical)',
    ARRAY['service'],
    'The foundational primitive of modern mathematics: a collection of distinct objects (the elements or members), considered as a single object in its own right. Sets are characterized extensionally — two sets are equal iff they have exactly the same members, regardless of how they are described. Set theory (Zermelo-Fraenkel with the axiom of choice — ZFC — is the standard formalization) provides the foundational framework for nearly all of contemporary mathematics: every mathematical structure (number, function, relation, sequence, geometric object) can be encoded as a set in ZFC. Distinct from the seeded metaphysical "relation" (in P5-02a) and from any future ontological / mereological notion of collection (which is governed by mereology rather than set theory).',
    'For students approaching formal mathematics or formal philosophy, sets are the first abstract structure they encounter and the most foundational. Frame set theory by its characteristic operations: membership (x ∈ S — x is an element of S); subset (S ⊆ T — every element of S is also an element of T); union (S ∪ T — elements in S or T or both); intersection (S ∩ T — elements in both); complement (relative to a universe); cardinality (the size of a finite set; for infinite sets, the deeper notion of cardinal number due to Cantor). The standard axiomatization (ZFC) was developed in the early twentieth century in response to the paradoxes (Russell''s paradox in particular — see russell_paradox in P5-03) that arose from naive set theory''s unrestricted comprehension principle. The axiomatic framework restricts comprehension to safe forms (separation, replacement) that avoid the paradoxes while remaining strong enough to support the rest of mathematics. Set theory grounds the formal-semantic framework for predicate logic (the domain of quantification is a set), the formal framework for probability (a probability measure is defined on a set of outcomes), and the formal framework for many philosophical applications (possible-worlds semantics in P5-03 and P5-08, type theory, formal epistemology).',
    ARRAY['set_theory_primitive', 'mathematical_set', 'collection_set'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'function_mathematical',
    'Function (Mathematical)',
    ARRAY['service'],
    'The mapping primitive: a relation that associates each element of a domain set with exactly one element of a codomain set. Equivalently, a set of ordered pairs (x, y) such that no two pairs share the same first element. Functions formalize the everyday notion of "rule that takes an input and produces an output" and are the second-most-foundational mathematical structure after sets themselves. Distinct from the seeded metaphysical "relation" (P5-02a) and from the seeded "function" senses elsewhere in philosophy (functional role in mind, communicative function in language); the suffix _mathematical preserves clarity that this is the formal set-theoretic mapping concept.',
    'For students, distinguish three closely related notions: (1) a relation (a set of ordered pairs, no constraints); (2) a function (a relation where each first element appears at most once); (3) a total function (a function whose domain is exactly the relevant set, no missing inputs). Functions can be classified by additional properties: injective (one-to-one — no two inputs give the same output), surjective (onto — every codomain element is reached), bijective (both — sets up a one-to-one correspondence). The function concept is the gateway to: the formal definition of probability distributions (a probability mass function or density function), the formal-semantic definition of logical interpretation (an interpretation function maps non-logical symbols to denotations), the type-theoretic notion of function type (functions are first-class values), and the lambda-calculus notion of function application. Functions also ground the formal definition of expected value in probability and the concept of expected utility in formal decision theory.',
    ARRAY['math_function', 'formal_function', 'mapping'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'axiom_mathematical',
    'Axiom (Mathematical)',
    ARRAY['service'],
    'The primitive-statement-assumed concept of formal systems: a statement taken as a starting point of a system without proof, used together with inference rules to derive the system''s theorems. In the modern Hilbertian view, axioms are not "self-evident truths" (the older Aristotelian-Euclidean view) but stipulations — chosen for the system''s desired properties (consistency, expressiveness, model-theoretic neatness). Modern mathematics is structured around several canonical axiomatizations: the Peano axioms for arithmetic, the ZFC axioms for set theory, the Hilbert axioms for Euclidean geometry, the field axioms for algebra, the topological-space axioms for topology, etc.',
    'For students approaching formal mathematics, two senses of "axiom" need to be distinguished: (1) the older Aristotelian sense — a self-evident truth that no rational person could deny; (2) the modern Hilbertian sense — a stipulation that defines the formal system being studied. The shift from (1) to (2) is one of the philosophical revolutions of the late nineteenth and early twentieth centuries, driven by the discovery of non-Euclidean geometries (Lobachevsky, Bolyai, Riemann) which showed that the Euclidean parallel postulate could be coherently rejected and replaced with alternatives. Modern axiomatic mathematics is conditional in form: "in a system with these axioms, these theorems hold". The choice of axioms is itself a substantive activity — Gödel''s incompleteness theorems show that no consistent axiomatization of arithmetic powerful enough to prove the basic facts of arithmetic can prove all true arithmetic statements, so the axiom-choice activity is genuinely creative rather than mechanical. Pedagogically, the axiomatic method is the gateway to formal proof: students see that proofs proceed from axioms via inference rules, and the relationship between the syntactic notion of proof and the semantic notion of truth-in-a-model becomes central.',
    ARRAY['axiom', 'formal_axiom'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'quantifier',
    'Quantifier',
    ARRAY['service'],
    'The variable-binding logical operator that converts an open formula (one with free variables) into a closed formula (with all variables bound) by specifying how many objects in the domain satisfy the formula. The two canonical quantifiers in classical first-order logic are the universal quantifier ∀ (read "for all") and the existential quantifier ∃ (read "there exists"). Quantifiers range over a domain — typically a set — and their semantic interpretation depends on the domain choice: "∀x P(x)" is true in a domain D iff every member of D satisfies P. Quantifier theory is the central technical advance of late-nineteenth-century logic (Frege''s 1879 Begriffsschrift introduced the modern formalization) over the prior Aristotelian categorical-logic tradition.',
    'For students, the quantifier-introduction step is the move from propositional logic (which handles only sentences as wholes) to predicate logic (which can express the internal structure of sentences). Walk through the contrast: propositional logic can represent "Socrates is mortal" only as a single propositional letter P; predicate logic can represent it as M(s) — a predicate M (mortal) applied to a singular term s (Socrates). The quantifiers then permit expressing universal and existential generalizations: ∀x (H(x) → M(x)) — every human is mortal; ∃x P(x) — at least one prime exists. Quantifier scope (which variables are bound by which quantifiers, and the order of nested quantifiers) is the most difficult formal-logic skill to develop and the most pedagogically valuable: the difference between ∀x ∃y L(x,y) (everyone has someone they love) and ∃y ∀x L(x,y) (someone is loved by everyone) is the scope-order distinction made vivid. Quantifier theory grounds the seeded predicate_logic concept (P5-03) and is presupposed by every formal application of quantification in epistemology (∀x (knows(s, x) → ...)), philosophy of mind, and formal-semantic philosophy of language.',
    ARRAY['logical_quantifier', 'first_order_quantifier'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'probability_mathematical',
    'Probability (Mathematical)',
    ARRAY['service'],
    'The formal measure-theoretic primitive: a function P that assigns to each event (a subset of a sample space) a real number in the interval [0, 1] satisfying the Kolmogorov axioms — non-negativity (P(A) ≥ 0), normalization (P(sample space) = 1), and countable additivity (the probability of a countable union of disjoint events equals the sum of their probabilities). Distinct from substantive philosophical interpretations of probability (frequentist, propensity, classical, subjectivist — see Bayesian epistemology in P5-01b) which give different accounts of what probability *means*; the service-tier concept is the formal mathematical object on which all interpretations agree.',
    'For students, two distinct questions about probability need to be separated: (1) what is the formal mathematics of probability? — answered by the Kolmogorov axiomatization (1933), which is uncontroversial; (2) what does probability *mean*? — the contested philosophical question, with several competing interpretations (frequentist: probability is long-run relative frequency; propensity: probability is a physical disposition of chance setups; classical: probability is the ratio of favorable to equipossible outcomes; subjectivist / Bayesian: probability is degree of rational belief). The service-tier concept here is (1) — the formal apparatus. Walk through the standard machinery: sample space (set of possible outcomes), event (subset of the sample space), probability measure (function from events to [0, 1]). Then introduce the central derived notions: conditional probability (P(A|B) = P(A ∩ B)/P(B) when P(B) > 0), independence (P(A ∩ B) = P(A) · P(B)), the law of total probability, Bayes''s theorem. Connect to the philosophical applications: the formal apparatus underwrites Bayesian epistemology (P5-01b), Bayesian confirmation theory (P5-09), the Dutch-book argument (P5-01b), and formal decision theory.',
    ARRAY['probability_formal', 'mathematical_probability', 'kolmogorov_probability'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'conditional_probability',
    'Conditional Probability',
    ARRAY['service'],
    'The probability of one event given another, defined as P(A|B) = P(A ∩ B)/P(B) for events A and B with P(B) > 0. The central operation on the formal probability measure: nearly every applied use of probability — Bayesian updating, statistical inference, formal decision theory under uncertainty — proceeds via conditional probabilities rather than unconditional ones. Conditional probability captures the formal sense of "given the information that B has occurred, what is the probability that A occurred / will occur?" and is the formal apparatus underlying inductive learning from evidence.',
    'For students, the conditional-probability concept is the bridge from the static formal measure (probability_mathematical) to the dynamic activity of updating beliefs in light of evidence. Walk through the definitional formula carefully — the division by P(B) is the renormalization that makes the conditional measure a proper probability measure on the restricted sample space "given B occurred". Use a concrete example with explicit numerical values (e.g., the standard fair-die illustration: P(rolled even | rolled prime) = P(rolled 2)/P(rolled 2 or 3 or 5) = (1/6)/(3/6) = 1/3). Pair the introduction with the contrast between conditional and unconditional probability: P(A|B) is generally NOT equal to P(A) — they are equal exactly when A and B are independent, which is the formal definition of independence. The conditional-probability concept grounds the law of total probability (P(A) = ΣᵢP(A|Bᵢ)·P(Bᵢ) for a partition {Bᵢ}) and Bayes''s theorem (which inverts the conditioning); both are essential for formal Bayesian reasoning. Connect to the philosophical applications: conditional probability underlies the Bayesian framework for modeling rational degrees of belief in P5-01b (bayesian_epistemology) and the Bayesian framework for confirmation in P5-09 (bayesianism_confirmation).',
    ARRAY['conditional_prob', 'p_a_given_b'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'bayes_theorem',
    'Bayes''s Theorem',
    ARRAY['service'],
    'The formal probability-inversion identity: P(H|E) = P(E|H) · P(H) / P(E), where P(H) is the prior probability of hypothesis H, P(E|H) is the likelihood of evidence E given H, P(E) is the marginal probability of E (computed by the law of total probability over a partition of hypotheses), and P(H|E) is the posterior probability of H after observing E. The mathematical centerpiece of Bayesian epistemology, Bayesian confirmation theory, and Bayesian statistical inference. Named for Thomas Bayes (1701-1761), whose posthumous 1763 essay introduced the result in the special case of binary outcomes; the modern general formulation traces to Pierre-Simon Laplace.',
    'For students, derive Bayes''s theorem in two lines from the definition of conditional probability: P(A|B) = P(A∩B)/P(B) and P(B|A) = P(A∩B)/P(A) — solve both for P(A∩B), set the right-hand sides equal, and solve for P(A|B). The result is the inversion identity. The pedagogically important point is what the formula *does*: it converts a likelihood (P(evidence | hypothesis), often computable from the hypothesis) into a posterior probability (P(hypothesis | evidence), the quantity we usually want), via the prior probability of the hypothesis. Walk through a concrete Bayesian-updating example with explicit numerical values (the standard medical-test example: rare disease, accurate test, the surprising posterior — see Casscells-Schoenberger-Graboys 1978 study showing physicians wildly miscalibrate this). Connect to the philosophical applications: Bayes''s theorem is the formal core of Bayesian epistemology (the framework of degree-of-belief modeling in P5-01b — bayesian_epistemology), Bayesian confirmation theory (the dominant contemporary account of evidential support in philosophy of science — bayesianism_confirmation in P5-09), and statistical inference (Bayesian alternatives to frequentist hypothesis testing). The deep philosophical question is where the prior probability P(H) comes from — the "problem of priors" is the most-discussed objection to Bayesianism.',
    ARRAY['bayes_rule', 'bayes_formula'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'expected_value',
    'Expected Value',
    ARRAY['service'],
    'The probability-weighted average of a random variable''s possible outcomes, formalized as E[X] = Σᵢ xᵢ · P(X = xᵢ) for discrete X (or the analogous integral for continuous X). Expected value is the central operation underlying formal decision theory under uncertainty: the principle of maximizing expected utility (the dominant formal model of rational choice — von Neumann-Morgenstern 1944) treats agents as choosing actions to maximize the expected value of a utility function over outcomes. Distinct from the everyday "expected" sense (what one anticipates) — the formal expected value is a probability-weighted statistical quantity that may not correspond to any actually-possible outcome.',
    'For students, the expected-value concept is the bridge from formal probability to formal decision theory and the philosophical accounts of rational action that depend on it. Walk through the formula with the standard fair-die illustration: the expected value of a fair six-sided die roll is (1+2+3+4+5+6)/6 = 3.5 — a value the die can never actually show, but the long-run average of many rolls. Then introduce expected utility: instead of weighting outcomes by their probability alone, weight outcomes by their probability AND a utility function that captures the agent''s preferences over outcomes. The expected-utility framework (von Neumann-Morgenstern 1944, formalized further by Savage 1954) is the dominant formal model of rational decision under uncertainty in economics, decision theory, and game theory; it underlies the formal accounts of utilitarianism in ethics (P5-04a — utilitarian decision-making is expected-utility-maximizing for an aggregated utility), the formal accounts of practical rationality in epistemology (P5-01a), and the formal frameworks of game-theoretic political philosophy (P5-05). The expected-value-as-criterion is also the source of the canonical paradoxes in decision theory (St. Petersburg paradox, Allais paradox, Ellsberg paradox) which motivate non-expected-utility accounts.',
    ARRAY['expectation', 'expected_outcome', 'mean_random_variable'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'presocratic_naturalism',
    'Presocratic Naturalism',
    ARRAY['service'],
    'The early-Greek philosophical project (sixth and fifth centuries BCE) of explaining the natural world in terms of natural principles — water, air, fire, the apeiron (the unbounded), love and strife, the four elements, atoms — rather than in terms of mythological or theological narratives. The Presocratics (Thales, Anaximander, Anaximenes, Heraclitus, Parmenides, Empedocles, Anaxagoras, the Atomists Leucippus and Democritus) inaugurated Western philosophy by replacing mythological cosmogony with naturalistic explanation, and their methodological commitment to natural-principle explanation is the founding moment of Western natural philosophy and modern science.',
    'For students, the Presocratics matter philosophically less for their specific cosmological proposals (which were rapidly superseded) than for the methodological revolution they enacted: the move from explanation-by-narrative-of-divine-action to explanation-by-natural-principle. Frame the historical context: pre-Presocratic Greek cosmogony is the Hesiodic Theogony (gods generate the world through divine action and family relations); the Presocratic move is to seek non-divine explanatory principles ("what is everything made of?" — Thales: water; Anaximenes: air; Heraclitus: fire-as-process; Empedocles: four elements in cycles of love and strife; the Atomists: indivisible particles in void). The methodological commitment to natural-principle explanation is what makes the Presocratics the founding moment of Western philosophy and science — every subsequent philosophical and scientific tradition inherits this commitment, even when rejecting specific Presocratic content. Pedagogically, the Presocratic move from mythos to logos is also the pedagogical anchor for understanding the pre-philosophical baseline against which all subsequent philosophy defines itself.',
    ARRAY['presocratics', 'early_greek_naturalism'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'greek_atomism',
    'Greek Atomism',
    ARRAY['service'],
    'The Presocratic and Hellenistic doctrine, originating with Leucippus (fifth century BCE) and developed by Democritus (c. 460-370 BCE) and Epicurus (341-270 BCE), that the natural world consists of indivisible material particles (atomos = uncuttable) moving in an empty void. The atomic doctrine combined with the doctrine that all change is rearrangement of atoms gave Greek thought its most radical materialist option and the proximate ancestor of modern atomic theory in physics and modern materialist metaphysics in philosophy. The Epicurean tradition transmitted Greek atomism to Roman philosophy (Lucretius, De Rerum Natura) and through Lucretius into the early-modern revival.',
    'For students, Greek atomism is doctrinally a compact and historically a load-bearing position: just two posits (atoms and void; nothing else exists fundamentally) plus the metaphysical implication (all macroscopic phenomena reduce to atom-arrangements and atom-motions). Walk through the doctrinal content: indivisibility (atoms are the bottom — change cannot reach below them); plurality (many atoms, of various shapes and sizes); motion (atoms are in constant motion in the void); rearrangement (apparent change is atom-rearrangement, not creation or destruction); chance (the cosmic-scale distribution of atoms results from chance configurations rather than from teleological design — a sharp contrast with Aristotelian natural philosophy). The Epicurean version adds the famous "swerve" (clinamen) — atoms occasionally deviate from their straight-line paths by an indeterminate amount, providing both the source of cosmic compositions and the metaphysical ground for free will (Lucretius). Greek atomism is the proximate ancestor of: modern atomic theory in physics (which inherits the materialist commitment but radically revises the mechanics); modern philosophical materialism and physicalism (in P5-07a — physicalism in philosophy of mind); modern reductionist programs in philosophy of science (in P5-09 — reductionism_in_science). The cross-domain pedagogical edges from greek_atomism into these downstream concepts are P5-11''s responsibility.',
    ARRAY['atomism_greek', 'democritean_atomism', 'epicurean_atomism'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'aristotelian_four_causes',
    'Aristotelian Four Causes',
    ARRAY['service'],
    'Aristotle''s 4th-century BCE analysis of explanation as fourfold: a complete explanation of why a thing is as it is or why an event occurred answers four distinct kinds of "why" questions — material cause (what is it made of?), formal cause (what shape, structure, or pattern does it have?), efficient cause (what brought it about?), final cause (what is it for? — what purpose does it serve?). The four-cause analysis dominated Western natural philosophy from Aristotle through the medieval Scholastic synthesis and was the central target of Renaissance and early-modern mechanism, which retained efficient causation but rejected formal and (especially) final causation as illegitimate in natural-scientific explanation.',
    'For students, the four-cause analysis is the most influential pre-modern theory of explanation and the conceptual structure that the Scientific Revolution defined itself against. Walk through Aristotle''s canonical example (the bronze statue): material cause = the bronze; formal cause = the shape (the statue''s form); efficient cause = the sculptor; final cause = the purpose (commemoration, decoration). The four causes are co-applicable to natural objects too: an acorn''s material cause is its tissue, formal cause is its species-form, efficient cause is the parent oak, final cause is the mature oak it is becoming (Aristotle''s teleological natural philosophy treats the final cause as central in biology). The Scientific Revolution''s mechanist revolt (Galileo, Descartes, Hobbes, Boyle) targeted formal and final causes specifically: mechanism retains material cause (matter) and efficient cause (motion-and-impact) but eliminates formal cause (substantial forms are dismissed as scholastic obscurantism) and final cause (teleology is banished from physics — natural phenomena are not "for" anything). The four-cause analysis is also the structural ancestor of contemporary multi-aspect theories of explanation (causal explanation, mechanistic explanation, structural explanation, teleological explanation in biology). The cross-domain pedagogical edges from aristotelian_four_causes into causation in metaphysics (P5-02a) and into the Scientific Revolution-era concepts in philosophy of science are P5-11''s responsibility.',
    ARRAY['four_causes', 'aristotle_causes', 'four_causes_aristotle'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'scholasticism',
    'Scholasticism',
    ARRAY['service'],
    'The medieval (roughly 11th-15th century) philosophical-theological synthesis that integrated Aristotelian philosophy with Christian theology and developed a systematic curriculum and methodology for university teaching and disputation. The dominant intellectual movement of the European Middle Ages, with central figures Anselm, Peter Abelard, Thomas Aquinas (1225-1274 — the most influential Scholastic synthesis), Duns Scotus, William of Ockham. Scholasticism made Aristotle ("the Philosopher") the canonical figure for European thought from roughly 1250 to 1600 and developed the technical vocabulary (substance, essence, accident, potency, act, matter, form, quiddity, haecceity) that contemporary metaphysics still uses.',
    'For students, Scholasticism is doubly important historically: as the system the Scientific Revolution and modern philosophy defined themselves against (the "schoolmen" became the negative reference point for early-modern philosophers from Descartes through Locke), and as the source of much contemporary metaphysical vocabulary still in use (substance, essence, accident, modal vocabulary, the distinction between de re and de dicto modality). Frame the Scholastic project: integrate Aristotelian natural philosophy, ethics, and metaphysics with Christian theological doctrine using the recently-recovered Aristotelian corpus (translated into Latin from Arabic via Averroes and others in the 12th century); develop systematic textbooks (the summa form — Aquinas''s Summa Theologiae is the canonical example), the disputational method (quaestio — pose a question, present arguments pro and contra, give a determination, respond to the contra arguments), and the university curriculum (the trivium of grammar/logic/rhetoric and the quadrivium of arithmetic/geometry/music/astronomy). The Scholastic synthesis dominated European university education for four centuries and shaped the conceptual vocabulary of metaphysics permanently. The cross-domain pedagogical edges from scholasticism into the seeded metaphysical concepts (substance, essence, modality, etc.) are P5-11''s responsibility.',
    ARRAY['medieval_scholasticism', 'schoolmen', 'scholastic_method'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'renaissance_mechanism',
    'Renaissance and Early-Modern Mechanism',
    ARRAY['service'],
    'The early-modern (roughly late 16th through 17th century) philosophical-scientific movement that explained natural phenomena as the motion of material particles in space, governed by impact and (later) attractive and repulsive forces — the matter-in-motion picture of nature that supplanted the Aristotelian-Scholastic synthesis. Central figures: Galileo Galilei (1564-1642), René Descartes (1596-1650 — the systematic mechanist metaphysics in the Meditations and Principles), Thomas Hobbes (1588-1679), Pierre Gassendi (1592-1655 — Christianized Epicureanism), Robert Boyle (1627-1691 — corpuscular chemistry), Isaac Newton (1643-1727 — universal mechanics, with the controversial addition of action-at-a-distance gravity). Mechanism rejected the Aristotelian formal and final causes, rejected substantial forms, rejected the qualitative/sensory description of nature in favor of mathematical-geometrical description, and inaugurated the modern scientific worldview.',
    'For students, mechanism is the philosophical movement that bridges medieval Scholasticism and modern science — and indirectly, modern materialist philosophy of mind and physicalism. Frame the mechanist commitments by contrast with what they rejected: (1) against formal causes — there are no substantial forms; objects are aggregates of particles arranged in space; (2) against final causes — natural phenomena are not directed at any goal; the apparent purposiveness of biological organisms is to be explained mechanistically (Cartesian animal-machine doctrine, ultimately a research program completed only in the twentieth century by molecular biology); (3) against qualitative description — primary qualities (size, shape, motion, number) are real properties of matter, while secondary qualities (color, sound, taste, smell) are merely powers in objects to produce sensations in observers (Locke''s formalization of an originally Galilean distinction); (4) for mathematical description — the book of nature is written in mathematical language (Galileo) and the proper scientific account of any natural phenomenon is a mathematical-mechanical model. Mechanism is the proximate ancestor of: modern physicalism in philosophy of mind (P5-07a — substance dualism vs. mechanist physicalism is the founding mind-body debate, between Descartes and his materialist contemporaries Hobbes and Spinoza); the modern conception of scientific theory (P5-09 — scientific_theory and scientific_explanation); the British empiricist tradition (Hobbes, Locke, Hume) which transmitted the mechanist worldview into eighteenth-century epistemology. The cross-domain pedagogical edges from renaissance_mechanism into substance_dualism, physicalism, and the philosophy-of-science theory concepts are P5-11''s responsibility.',
    ARRAY['mechanism_early_modern', 'mechanical_philosophy', 'mechanist_worldview'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'vienna_circle_logical_positivism',
    'Vienna Circle and Logical Positivism',
    ARRAY['service'],
    'The 1920s-1930s philosophical movement centered on the Vienna Circle (Moritz Schlick, Rudolf Carnap, Otto Neurath, Hans Hahn, Friedrich Waismann, Herbert Feigl, Philipp Frank, Kurt Gödel) and the closely related Berlin Group (Hans Reichenbach), which combined logical analysis (drawing on the new mathematical logic of Frege, Russell, Wittgenstein''s Tractatus) with empiricism (drawing on Mach and the British empiricist tradition) to produce the founding movement of twentieth-century analytic philosophy. The positivists held that all meaningful statements are either analytic (true by definition, like mathematics and logic) or empirical (testable by sense-experience, like the natural sciences); statements that are neither — including most of traditional metaphysics, theology, and German idealist philosophy — were dismissed as "meaningless" rather than false. The verifiability criterion of meaningfulness was the central technical doctrine.',
    'For students, the Vienna Circle is the historical hinge between nineteenth-century European philosophy (German idealism, neo-Kantianism, Lebensphilosophie) and twentieth-century analytic philosophy. Frame the movement''s historical context: post-WWI Vienna, the rise of mathematical logic, the success of Einstein''s general relativity (1915 — a new physics that displaced Newton, prompting reflection on the nature of scientific theories), and the Tractatus Logico-Philosophicus (Wittgenstein 1921 — interpreted by the Circle as supporting their verificationist program, though Wittgenstein himself rejected this reading). Walk through the central doctrines: the verifiability criterion of meaningfulness (a statement is cognitively meaningful iff it is empirically verifiable in principle); the rejection of metaphysics as a body of meaningless pseudo-statements (Carnap''s "Elimination of Metaphysics through Logical Analysis of Language" 1932 uses Heidegger as the paradigm target); the unity-of-science program (all sciences in principle reducible to physics, with a common observation language); the emotivist account of ethics (ethical statements express attitudes rather than describing facts — see ayer_emotivism in P5-04a metaethics). The movement dispersed in the mid-1930s under Nazi pressure (Schlick was murdered in 1936; many positivists emigrated to the United States and the United Kingdom — Carnap to Chicago and UCLA, Reichenbach to UCLA, Feigl to Minnesota) and reshaped Anglo-American philosophy, founding what became contemporary analytic philosophy of science (P5-09 — falsificationism, demarcation_problem, hypothetico_deductivism all directly respond to or descend from logical positivism), philosophy of language (P5-08 — verificationism), and metaethics (P5-04a — ayer_emotivism). The cross-domain pedagogical edges from vienna_circle_logical_positivism into these descendant philosophical movements are P5-11''s responsibility.',
    ARRAY['vienna_circle', 'logical_positivism', 'logical_empiricism'],
    'INTERPRETED',
    'ai-seed',
    15
  ),
  (
    'hegelian_dialectic',
    'Hegelian Dialectic',
    ARRAY['service'],
    'G. W. F. Hegel''s (1770-1831) philosophical method, in which thought develops through the contradiction-driven movement from a thesis (an initial position) to its antithesis (the contradiction or negation that the thesis itself generates) to a synthesis (a higher-order position that resolves the contradiction by incorporating both prior moments at a more adequate level). Hegel applied the dialectical method to logic (the Science of Logic), to history (the Philosophy of History — world history as the progressive realization of spirit / freedom), to political philosophy (the Philosophy of Right), and to philosophy itself (the Phenomenology of Spirit traces the dialectical development of consciousness). Hegelian dialectic is the central methodological alternative to formal-logical reasoning that nineteenth-century European philosophy produced, and the central methodology that twentieth-century analytic philosophy (in the Vienna-Circle tradition and after) defined itself against.',
    'For students, Hegelian dialectic is pedagogically valuable as the contrast case for understanding what makes analytic philosophy methodologically distinctive. Frame the dialectical method by contrast with the formal-logical method: where formal logic insists on the law of non-contradiction (no proposition is both true and false) and analyzes by decomposing complex statements into atomic ones, dialectic *uses* contradiction as a developmental mechanism — a thesis generates its antithesis precisely because the thesis is one-sided or partial, and the contradiction drives the move to the synthesis that incorporates both. The dialectical method is also developmentally historical: thought progresses through stages, each more adequate than the prior, and the philosophical task is to retrace and articulate the developmental sequence. Hegelian dialectic shaped Marx (historical-materialist dialectics — class contradictions drive historical development), Hegelian-influenced political philosophy and social theory (Frankfurt School, Sartre''s existentialism), and the early-twentieth-century absolute idealism (Bradley, McTaggart) that the British analytic founders (Russell, Moore) explicitly rejected. The Vienna Circle''s dismissal of metaphysics as meaningless used Hegelian-tradition writing (and Heidegger, who inherited a related broadly Continental tradition) as the paradigm of what they were rejecting. Pedagogically, situating Hegelian dialectic as the methodological alternative makes vivid what the analytic tradition''s methodological commitments (formal-logical analysis, conceptual clarification, attention to natural-language meaning, the rejection of speculative system-building) actually amount to. The cross-domain pedagogical edges from hegelian_dialectic into critique-of-metaphysics positions and methodological-contrast positions across multiple subdomains are P5-11''s responsibility.',
    ARRAY['hegel_dialectic', 'dialectical_method', 'dialectic_hegelian'],
    'INTERPRETED',
    'ai-seed',
    15
  );

-- Edges: 28 within-service pedagogical_prerequisite edges across the
-- three sub-clusters plus four cross-cluster service-to-service bridges.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Formal-logic cluster (11 edges)
  ('truth_value', 'bivalence_principle', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('truth_value', 'argument_logical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('bivalence_principle', 'validity_logical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('argument_logical', 'validity_logical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('validity_logical', 'soundness_logical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('argument_logical', 'counterexample', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('bivalence_principle', 'counterexample', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('argument_logical', 'inference_rule', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('inference_rule', 'modus_ponens', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('inference_rule', 'modus_tollens', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('modus_ponens', 'formal_proof', 'pedagogical_prerequisite', 'ai-seed', 15),
  -- Math cluster (8 edges)
  ('set_mathematical', 'function_mathematical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('set_mathematical', 'axiom_mathematical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('set_mathematical', 'quantifier', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('set_mathematical', 'probability_mathematical', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('probability_mathematical', 'conditional_probability', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('conditional_probability', 'bayes_theorem', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('probability_mathematical', 'expected_value', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('function_mathematical', 'expected_value', 'pedagogical_prerequisite', 'ai-seed', 15),
  -- History cluster (5 edges)
  ('presocratic_naturalism', 'greek_atomism', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('presocratic_naturalism', 'aristotelian_four_causes', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('aristotelian_four_causes', 'scholasticism', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('scholasticism', 'renaissance_mechanism', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('aristotelian_four_causes', 'renaissance_mechanism', 'pedagogical_prerequisite', 'ai-seed', 15),
  -- Cross-cluster service-to-service bridges (4 edges)
  ('axiom_mathematical', 'formal_proof', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('aristotelian_four_causes', 'vienna_circle_logical_positivism', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('renaissance_mechanism', 'vienna_circle_logical_positivism', 'pedagogical_prerequisite', 'ai-seed', 15),
  ('hegelian_dialectic', 'vienna_circle_logical_positivism', 'pedagogical_prerequisite', 'ai-seed', 15);

COMMIT;
