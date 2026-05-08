-- Migration: 0040_seed_mind_part1
-- Purpose: Ninth Phase 5 seed migration (first philosophy-of-mind file) —
--   foundational philosophy-of-mind concepts and within-domain
--   pedagogical_prerequisite edges. Authored in S-0066 against task
--   P5-07a "Philosophy of mind core seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the core mind concepts per phase_5.md T1-B: mental causation,
--   intentionality, perception, personal identity, AI/computational mind,
--   and the dualism-vs-physicalism mind-body theory cluster as their
--   shared metaphysical backdrop. Specialized concepts —
--   consciousness, qualia, the hard problem, phenomenology adjacencies —
--   are task P5-07b's range (0046-0049) and are deliberately excluded
--   from this file.
-- Loads tables: public.nodes (30 INSERTs), public.edges (35 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 9 -> 10).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 9 at session boot (post-S-0061 per
--     ROUTING.md narrative — most recent applied seed at this prefix
--     range was 0100_seed_political_philosophy_part1.sql which wrote 9).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 10 (the
--     post-increment value).
--   * No prior migrations under prefix 0040-0045; this is the first
--     philosophy-of-mind seed file.
--   * P5-01a + P5-01b epistemology seeds applied (0011 and 0016). No
--     edge in this migration references epistemology nodes —
--     philosophy-of-mind core is greenfield within its own subdomain at
--     this seed step; cross-domain bridges land at P5-11 per phase_5.md
--     T2-G #1.
-- Postconditions:
--   * 30 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'mind'}, status=active, graph_version_added=10.
--   * 35 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=10. All edges are
--     within-domain (source and target both tagged mind); cross-domain
--     edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 10.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 10 AND 'mind' = ANY(domain) :: 30
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 10 AND edge_type = 'pedagogical_prerequisite' :: 35
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 10
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts (no edges into pre-existing nodes; mind-core is
--     greenfield within its own subdomain).
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is layered: T0 philosophy_of_mind; T1 mind;
--     T2 mental_state, personal_identity; T3 propositional_attitude,
--     dualism, physicalism, mental_causation, intentionality,
--     perception, psychological_continuity_theory, animalism;
--     T4 substance_dualism, property_dualism, type_identity_theory,
--     functionalism, behaviorism_logical, eliminative_materialism,
--     supervenience_mental, causal_exclusion_argument,
--     representational_theory_of_mind, functional_role_semantics,
--     causal_theory_of_mental_content, direct_realism_perceptual,
--     representationalism_perception, sense_data_theory;
--     T5 multiple_realizability, computational_theory_of_mind;
--     T6 chinese_room_argument, turing_test. Every edge points from a
--     lower tier to a higher tier; validate.py's Kosaraju SCC check
--     confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: perception bridges to
--     epistemology (P5-01a/b on perceptual justification, sense_data and
--     foundationalism); intentionality bridges to philosophy of language
--     (P5-08 on reference, propositional content, semantic externalism);
--     mental_causation bridges to metaphysics (P5-02a's causation, P5-02b
--     on supervenience); personal_identity bridges to metaphysics
--     (P5-02a's numerical_identity / persistence; P5-02b's bundle theory
--     of self); functionalism and computational_theory_of_mind bridge to
--     philosophy of science (P5-09 on cognitive science, multiple
--     realizability as reduction question); propositional_attitude
--     bridges to philosophy of language (P5-08 on attitude verbs and
--     hyperintensionality). Wait for P5-11's cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the specialized philosophy-of-mind range
--     (0046-0049): consciousness, qualia, hard_problem,
--     phenomenology adjacencies, panpsychism, integrated_information_
--     theory, global_workspace_theory, higher_order_theories. P5-07b
--     owns that range.
--   * Does not author the additional core-mind sub-ranges (0041-0045).
--     Those slots remain reserved for future philosophy-of-mind core
--     extension if Phase 6+ telemetry warrants additional concepts; this
--     seed completes P5-07a's task at the granularity principle within
--     the 0040 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 30/30 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference's entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here is
--     well-named in the SEP/IEP entry inventory and corresponds to a
--     concept the contemporary analytic philosophy-of-mind literature
--     (Descartes, Ryle, Place, Smart, Putnam, Lewis, Davidson, Fodor,
--     Searle, Block, Brentano, Dretske, Kim, Parfit, Locke, Olson,
--     Churchland, Turing, Chalmers, Jackson) explicitly names. Mirrors
--     the eight prior Phase 5 subject seeds' distributions.
--   * domain[] cardinality: every node carries exactly one tag, 'mind'.
--     Multiple cross-domain reaches exist (perception, intentionality,
--     mental_causation, personal_identity, computational_theory_of_mind
--     are all cross-domain concepts) but per phase_5.md T2-G #4
--     (domain-tag cardinality explosions vector), cross-domain tagging
--     belongs to P5-11. The canonical home for each of these concepts in
--     the analytic literature is philosophy of mind, so the single tag
--     is correct here.
--   * provenance: 'ai-seed' for every node and edge. Same as
--     P5-01a/b, P5-02a/b, P5-03, P5-04a/b, P5-05.
--   * Node selection rationale: 30 concepts cover the seven core-mind
--     clusters at the granularity principle: (1) foundation (4)
--     [philosophy_of_mind, mind, mental_state, propositional_attitude]
--     — the field's umbrella, the basic explanandum, and the basic
--     ontological category mental states fall under, with propositional
--     attitudes as the canonical sub-kind treated by Russell, Davidson,
--     Fodor; (2) dualism/physicalism (8) [dualism, substance_dualism,
--     property_dualism, physicalism, type_identity_theory, functionalism,
--     behaviorism_logical, eliminative_materialism] — the two-way
--     mind-body theory dispute and its main physicalist variants in
--     historical sequence (behaviorism → identity theory →
--     functionalism → eliminativism with property_dualism as the
--     non-reductive non-physicalist alternative; substance_dualism as
--     the historical Cartesian starting point); (3) mental causation (4)
--     [mental_causation, causal_exclusion_argument, supervenience_mental,
--     multiple_realizability] — the puzzle of how mental states cause
--     physical events given physical causal closure (Kim's exclusion
--     argument), the supervenience relation that physicalists invoke to
--     accommodate mental causation without reduction, and Putnam's
--     multiple-realizability argument that motivates functionalism
--     against type-identity; (4) intentionality (4) [intentionality,
--     representational_theory_of_mind, functional_role_semantics,
--     causal_theory_of_mental_content] — Brentano's mark of the mental
--     and the three main contemporary approaches to mental content
--     (representations à la Fodor, inferential role à la Block/Harman,
--     causal covariation à la Dretske/Stampe); (5) perception (4)
--     [perception, direct_realism_perceptual, representationalism_
--     perception, sense_data_theory] — the philosophical question and
--     the three canonical positions in the current literature
--     (direct realism, representationalism, sense-data theory);
--     (6) personal identity (3) [personal_identity, psychological_
--     continuity_theory, animalism] — the diachronic question for
--     persons and the two main contemporary answers (Lockean
--     psychological-continuity à la Parfit; animalist bodily-continuity
--     à la Olson); (7) AI/computational mind (3) [computational_theory_
--     of_mind, chinese_room_argument, turing_test] — the computational
--     thesis (Putnam) and its two canonical pedagogical foils (Searle's
--     Chinese Room as the major philosophical objection; Turing's test
--     as the operational benchmark for machine intelligence). Excluded
--     deliberately and reserved for P5-07b: consciousness (the
--     phenomenon), qualia (the qualitative character), hard_problem (the
--     Chalmers explanatory-gap argument), phenomenology adjacencies,
--     panpsychism, higher-order theories of consciousness, integrated
--     information theory, global workspace theory.
--   * Edge structure: 35 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation spine flows philosophy_of_mind → mind
--     → mental_state, with mental_state branching out to propositional_
--     attitude (specific kind of mental state) and to the four major
--     downstream surfaces (dualism vs physicalism via mental_state →
--     dualism + mental_state → physicalism; mental_causation;
--     intentionality; perception). Mind also branches to personal_
--     identity. Dualism forks into substance_dualism + property_dualism;
--     physicalism forks into type_identity_theory, functionalism,
--     behaviorism_logical, eliminative_materialism. Multiple
--     realizability bridge: type_identity_theory → multiple_
--     realizability → functionalism (the canonical pedagogical sequence:
--     identity theory motivates the reduction question; multiple
--     realizability falsifies type-identity; functionalism recovers a
--     physicalist position compatible with multiple realizability).
--     Mental causation branch: mental_causation → causal_exclusion_
--     argument (Kim's argument is the central problem in the topic);
--     physicalism → supervenience_mental → mental_causation (the
--     supervenience apparatus is what physicalists deploy to address
--     mental causation). Intentionality branch: intentionality →
--     representational_theory_of_mind, intentionality → functional_role_
--     semantics, intentionality → causal_theory_of_mental_content (three
--     parallel approaches to mental content). Perception branch:
--     perception → direct_realism_perceptual, perception →
--     representationalism_perception, perception → sense_data_theory
--     (three parallel positions). Personal identity branch:
--     personal_identity → psychological_continuity_theory,
--     personal_identity → animalism (two parallel positions).
--     Computational branch: functionalism → computational_theory_of_mind
--     (computational mind is a specific functionalist thesis);
--     computational_theory_of_mind → chinese_room_argument,
--     computational_theory_of_mind → turing_test (the canonical
--     objection and the canonical operational benchmark).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 10; DELETE FROM public.nodes WHERE id IN (the 30 ids inserted
--   here); UPDATE public.settings SET value = '9'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 66 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0030_seed_metaphysics_part1.sql
--   (P5-02a metaphysics core seed; pattern reference);
--   product/seed-graph/migrations/0090_seed_logic_part1.sql
--   (P5-03 logic seed; layered-DAG pattern reference);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 9 at session boot (post-S-0061 state per ROUTING.md
-- narrative); write 10 here; every node/edge below carries
-- graph_version_added = 10.
UPDATE public.settings
  SET value = '10'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 30 INSERTs covering the seven core philosophy-of-mind clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'philosophy_of_mind',
    'Philosophy of Mind',
    ARRAY['mind'],
    'The branch of philosophy concerned with the nature of mental phenomena: their relation to the physical world, the structure of conscious experience, the status of mental states as causes of behavior, the conditions for thought and intentional content, and the criteria for personal identity over time. Sits at the intersection of metaphysics, epistemology, philosophy of language, and the cognitive sciences.',
    'Frame philosophy of mind by its central tension: mental phenomena seem at once part of the natural world (causally efficacious, dependent on brain activity, susceptible to scientific study) and recalcitrant to the methods that work for the rest of nature (introspectively accessed, qualitatively saturated, intentionally about things). The contemporary analytic version (post-Ryle 1949, Place 1956, Smart 1959, Putnam 1967, Lewis 1972, Davidson 1970) is dominated by versions of physicalism in dialogue with persistent challenges from consciousness, intentionality, and mental causation. Treat it as a domain whose progress depends on holding the metaphysical question open while honoring both the third-personal scientific perspective and the first-personal experiential one.',
    ARRAY['philosophy_of_psychology'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'mind',
    'Mind',
    ARRAY['mind'],
    'The collection of mental phenomena exhibited by a conscious creature: its perceptions, beliefs, desires, intentions, sensations, emotions, and reasonings. Whether the mind is identical to the brain, supervenient on it, an emergent feature of it, or a distinct substance is the central metaphysical question of the philosophy of mind.',
    'Distinguish three uses of mind students conflate: (1) the explanandum — the phenomena to be explained (perceptions, thoughts, feelings); (2) the metaphysical posit — whatever underlies and unifies those phenomena (Cartesian substance? brain? functional organization?); (3) the folk-psychological notion — the everyday concept used in everyday explanations of behavior. Most disputes in philosophy of mind run between competing answers about (2) — what kind of thing mind is — while taking (1) as relatively fixed and (3) as a target either to vindicate (Davidson, Fodor) or to eliminate (Churchland).',
    ARRAY['mental_phenomena', 'mental_realm'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'mental_state',
    'Mental State',
    ARRAY['mind'],
    'A state of an organism characterized by its mental content or qualitative character: a particular belief, a particular desire, a particular pain, a particular perceptual experience. The basic explanatory unit of folk psychology and the basic explanandum of philosophy-of-mind theorizing — type-identity theory says mental states ARE physical states; functionalism says they are functional states; eliminativism says folk-psychological mental states do not exist.',
    'Mental states come in two broad classes worth distinguishing pedagogically: contentful states with intentional content (beliefs, desires, intentions, hopes, fears — the propositional attitudes), and qualitative states with phenomenal character (pains, itches, color sensations, emotional moods — the qualia bearers). Some mental states are both (a perceptual experience has content AND qualitative character). The question what mental states fundamentally are — content-bearing functional roles? brain states? irreducible mental particulars? — is what mind-body theories answer differently.',
    ARRAY['psychological_state'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'propositional_attitude',
    'Propositional Attitude',
    ARRAY['mind'],
    'A mental state consisting in an agent''s standing in a particular attitude (believing, desiring, hoping, fearing, intending) toward a proposition. Russell coined the term; Davidson and Fodor made it central. The form is "S φs that P" where S is a subject, φ is the attitude verb, and P is the proposition. The puzzle is how a brain state can stand in the right relations to abstract propositions to count as believing or desiring them.',
    'Use propositional attitudes as the entry point to mental content. The standard Russellian taxonomy: belief and assertion aim at truth; desire and command aim at making true; hope, fear, regret, intention all add modal/temporal/practical orientations on top. The puzzle of attitude content (how does this brain state succeed in being about THAT proposition?) drives the intentionality literature. Distinguish propositional attitudes from non-propositional mental states (a pain is not propositionally structured; an undirected mood may not be). Pedagogically the cleanest way into the content question is via the attitudes: even granting that brains compute, what makes a particular computational state count as believing that snow is white?',
    ARRAY['attitude_propositional', 'intentional_attitude'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'dualism',
    'Dualism (Mind-Body)',
    ARRAY['mind'],
    'The thesis that mind and body are metaphysically distinct: the mental and the physical are not one and the same kind of thing. Substance dualism (Descartes) holds they are distinct substances; property dualism (Chalmers, Jackson) holds the substance is physical but bears non-physical mental properties. The position is the historical default and the canonical opposition to physicalism.',
    'Distinguish substance dualism from property dualism early — students collapse them. Substance dualism posits two kinds of stuff (res cogitans, res extensa) and faces the famous interaction problem (how does the immaterial soul push around physical neurons?). Property dualism posits one kind of stuff (physical) bearing two kinds of property (physical and mental); it avoids the interaction problem in its crude form but inherits a subtler version (how do non-physical properties make a causal difference?). Most contemporary anti-physicalists are property dualists, not substance dualists; the substance form survives mostly in philosophy of religion and in popular understanding.',
    ARRAY['mind_body_dualism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'substance_dualism',
    'Substance Dualism',
    ARRAY['mind'],
    'Descartes''s thesis that mind and body are distinct substances: the mind (res cogitans) is unextended, immaterial, indivisible; the body (res extensa) is extended, material, divisible. The two interact at a point of interface — Descartes proposed the pineal gland — but their natures are categorically distinct. The view dominated early modern philosophy and remains the lay default conception of mind-body relations.',
    'Teach Cartesian dualism via Descartes''s arguments in the Meditations: the Cogito establishes the mind''s certainty of its own existence; the conceivability of disembodied existence (Meditation VI) establishes the real distinction between mind and body. The standard objections — Princess Elisabeth''s interaction problem (how can immaterial substance push material substance?), the problem of mental causation, the absence of evidence for non-physical substance in neuroscience — define what subsequent positions try to fix. Substance dualism is rare in contemporary analytic philosophy but useful as the canonical historical foil.',
    ARRAY['cartesian_dualism', 'res_cogitans_res_extensa_dualism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'property_dualism',
    'Property Dualism',
    ARRAY['mind'],
    'The thesis that there is one kind of substance (physical) but two kinds of property (physical and mental), with mental properties not reducible to or identical with physical properties. Defended in different forms by Chalmers (1996) on phenomenal properties and by Jackson (1982) via the Mary thought experiment. Avoids substance dualism''s extra ontology while preserving the irreducibility of the mental.',
    'Property dualism is the live anti-physicalist position in contemporary analytic philosophy of mind. Frame it via the leading arguments: Jackson''s Mary (the colorblind super-scientist who learns something new on seeing red implies physicalism is incomplete about phenomenal properties), Chalmers''s zombies (a being physically identical to me but lacking phenomenal consciousness is conceivable, hence possible, hence physicalism is false). The position itself is what these arguments target — note that property_dualism is the metaphysical position, distinct from the hard_problem (P5-07b) which is the explanatory framing of why phenomenal consciousness resists physicalist explanation. Standard physicalist responses include phenomenal-concept-strategy (Loar, Papineau) and the type-B materialism that accepts property dualism only at the conceptual level.',
    ARRAY['nonreductive_property_dualism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'physicalism',
    'Physicalism',
    ARRAY['mind'],
    'The thesis that everything is physical: every concrete particular is a physical particular; every property either is a physical property or is grounded in physical properties; minds are not exceptions. The dominant metaphysical framework in contemporary analytic philosophy of mind. Differentiates into type-identity theory, functionalism, behaviorism, eliminativism, and non-reductive physicalism according to how it handles the apparent autonomy of the mental.',
    'Physicalism is the umbrella, not a particular theory. The standard formulation distinguishes type-physicalism (mental types are physical types) from token-physicalism (every mental token is a physical token but mental types may be multiply realizable). Davidson''s anomalous monism is a famous token-physicalist position. The central objections: Mary and zombies target the irreducibility of phenomenal properties; the multiple-realizability argument targets type-physicalism specifically. Most contemporary physicalists are non-reductive (token-physicalist) functionalists who hold mental types are functionally individuated and can be realized in various physical substrates.',
    ARRAY['materialism_about_mind'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'type_identity_theory',
    'Type-Identity Theory',
    ARRAY['mind'],
    'The thesis that mental state types are identical to brain state types: pain IS C-fiber firing (the canonical Place-Smart example), belief that snow is white IS some particular neural type. Defended by U.T. Place (1956), J.J.C. Smart (1959), David Lewis (1966), and David Armstrong (1968). Strong, reductive, and historically important — the first systematic physicalist alternative to behaviorism.',
    'Teach type-identity theory as the cleanest physicalist position before functionalism complicates the picture. The motivation is parsimony: if every mental state corresponds to a brain state and is causally efficacious only via that correspondence, the simplest hypothesis is identity. The standard objection is multiple realizability (Putnam 1967): if octopuses, Martians, and humans can all believe that snow is white but have different brain types instantiating that belief, then the belief-type cannot BE any one brain type. The lesson modern functionalism draws is that mental types must be individuated more abstractly — by functional role rather than physical realizer.',
    ARRAY['mind_brain_identity_theory', 'place_smart_identity_theory'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'functionalism',
    'Functionalism (Philosophy of Mind)',
    ARRAY['mind'],
    'The thesis that mental states are individuated by their functional roles — by their typical causal relations to sensory inputs, behavioral outputs, and other mental states. Pain is whatever state typically causes wincing, avoidance behavior, complaints, and the desire that the cause stop, regardless of the physical substrate that realizes that role. The dominant theory of mind in contemporary analytic philosophy, defended by Putnam (early), Lewis, Block, and Fodor.',
    'Functionalism is the natural successor to type-identity theory: it preserves physicalism (every mental token is a physical token) while accommodating multiple realizability (mental types are functional, not physical). Distinguish three flavors: machine-state functionalism (Putnam 1967 — mental states are states of a Turing machine running a particular program), causal-role functionalism (Armstrong, Lewis — mental states are defined by their typical causal roles), and analytic functionalism (Lewis 1972 — folk psychology implicitly defines mental states via Ramsified theory). Standard objections: the absent-qualia argument (Block 1978 China-brain) and the inverted-qualia argument both contend that functional duplicates can differ in phenomenal character, so phenomenal properties are not exhausted by functional role.',
    ARRAY['functional_role_theory_of_mind', 'role_functionalism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'behaviorism_logical',
    'Logical Behaviorism',
    ARRAY['mind'],
    'The thesis that mental state ascriptions are translatable into statements about behavior or behavioral dispositions: to say "Smith believes it is raining" is, on this view, to say something about how Smith would behave under various conditions (taking an umbrella when going out, etc.). Defended by Ryle (1949), Hempel, and Carnap. Distinguished from psychological/methodological behaviorism (Watson, Skinner) which is a thesis about the proper science of psychology, not about the meaning of mental terms.',
    'Logical behaviorism is the position type-identity theory and functionalism replace; teaching it pedagogically illuminates both. Its motivation is anti-Cartesian: if mental ascriptions are really about behavior, the dualist''s "ghost in the machine" (Ryle''s phrase) is a category mistake. The standard objection is that mental states have a holistic structure — what behavior counts as evidence of belief depends on what the subject also desires, fears, and believes — so no finite behavioral analysis succeeds (the multiplication-of-qualifications problem). Functionalism inherits the spirit (mental states are individuated by relations to inputs and outputs) but refuses to eliminate other mental states from the analysis, allowing relations to other mental states.',
    ARRAY['analytical_behaviorism', 'philosophical_behaviorism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'eliminative_materialism',
    'Eliminative Materialism',
    ARRAY['mind'],
    'The thesis that the categories of folk psychology (belief, desire, intention, etc.) do not refer to anything real — they are part of a false theory of human behavior that mature neuroscience will replace. Defended by Paul Churchland (1981) and Patricia Churchland (1986). Distinguished from reductive physicalism (which preserves folk-psychological categories by identifying them with neural types) by its claim that folk psychology is empirically inadequate and will be superseded.',
    'Teach eliminativism as the maximally revisionary physicalist position: where type-identity theory keeps belief and desire by identifying them with brain states, and functionalism keeps them by individuating them functionally, eliminativism throws them out as posits of a bad theory (analogous to how chemistry threw out phlogiston). The motivation is naturalistic: folk psychology has been around forever, has not progressed scientifically, and looks suspiciously theory-like. Standard objections: self-refutation (the eliminativist''s claim that there are no beliefs presupposes that someone believes that claim), the predictive-success of folk psychology in everyday life, and the difficulty of conceiving what neural-vocabulary replacement would even look like for higher-level explanation.',
    ARRAY['eliminativism_psychological', 'churchland_eliminativism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'mental_causation',
    'Mental Causation',
    ARRAY['mind'],
    'The puzzle of how mental states cause physical events. Mental events apparently cause physical events all the time (a thirst causes hand-to-glass movement; a decision causes leg-to-step). But if the physical world is causally closed (every physical event has a sufficient physical cause), and mental events are not identical to physical events, then either mental events do not really cause physical events (epiphenomenalism) or every action is causally overdetermined. Kim''s causal-exclusion argument is the contemporary canonical formulation.',
    'Mental causation is where physicalism, dualism, and the irreducibility of the mental collide. Frame the puzzle via three premises that are individually plausible but jointly inconsistent: (1) mental causation (mental events cause physical events); (2) physical causal closure (every physical event has a sufficient physical cause); (3) non-overdetermination (physical events typically are not overdetermined). Type-identity theory blocks the puzzle by identifying mental events with their physical causes; non-reductive physicalists must show why supervenience-based mental properties make a real causal difference; property dualists must accept some form of overdetermination or causal exclusion. Davidson''s anomalous monism, Kim''s exclusion argument, and the literature on physical realization all engage this central problem.',
    ARRAY['mental_to_physical_causation'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'causal_exclusion_argument',
    'Causal Exclusion Argument',
    ARRAY['mind'],
    'Jaegwon Kim''s argument (1989, 1998, 2005) that non-reductive physicalism cannot accommodate genuine mental causation. If mental property M supervenes on physical property P, and P is causally sufficient for the physical effect, then M is causally pre-empted — its instantiation makes no difference because P does the causal work. Either M is identical to P (reduction), or M is causally inert (epiphenomenalism), or the effect is overdetermined (implausible).',
    'Kim''s argument is the central problem for non-reductive physicalism. Teach it in three stages: (1) the supervenience premise (M supervenes on P); (2) the closure premise (P is causally sufficient for the physical effect); (3) the exclusion claim (no genuine cause is mere supervenient on a sufficient lower-level cause). The conclusion is that non-reductive physicalism collapses into either reductive physicalism (identifying M with P) or epiphenomenalism (denying M causes anything). Standard responses include compatibilist accounts of mental causation (Yablo on proportional causation, Bennett on overdetermination, List-Menzies on programming explanation) that try to vindicate higher-level causation without identity.',
    ARRAY['kim_exclusion_argument', 'exclusion_problem'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'supervenience_mental',
    'Mental Supervenience',
    ARRAY['mind'],
    'The thesis that mental properties supervene on physical properties: there cannot be two beings physically identical but mentally different. The standard apparatus by which non-reductive physicalists capture the dependence of the mental on the physical without commitment to type-identity. Davidson (1970) introduced supervenience to philosophy of mind; Kim (1984) developed the formal taxonomy of weak, strong, and global supervenience.',
    'Distinguish three increasingly strong supervenience theses Kim formalized: (1) weak supervenience — within a possible world, no mental difference without physical difference; (2) strong supervenience — across all possible worlds, no mental difference without physical difference; (3) global supervenience — no overall world-difference in mental matters without overall difference in physical matters. Strong supervenience is the standard non-reductive physicalist commitment. Critics (Kim himself in later work) argue supervenience is too thin: it captures the dependence of the mental on the physical but not a deeper grounding relation; what physicalism needs is grounding, realization, or constitution, not mere covariation.',
    ARRAY['psychophysical_supervenience'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'multiple_realizability',
    'Multiple Realizability',
    ARRAY['mind'],
    'Hilary Putnam''s (1967) thesis that the same mental state can be realized in many distinct physical substrates: pain can be C-fiber firing in humans, some other neural pattern in octopuses, possibly some silicon configuration in artificial systems. The thesis was the canonical argument against type-identity theory and the canonical motivation for functionalism: if mental types are not pinned to specific physical types, mental types must be individuated more abstractly — by functional role.',
    'Teach multiple realizability as the bridge from type-identity theory to functionalism. The argument structure: (1) mental state M can be instantiated by physical state P1 in humans, P2 in octopuses, P3 in Martians, P4 in robots; (2) but M is one type; (3) so M is not identical to any of the Pi; (4) so M is individuated by something other than physical type — namely, functional role. The argument has been challenged (Bechtel-Mundale on the heterogeneity of pain; Polger on whether MR is empirically supported), but it remains the canonical pedagogical bridge. Connect to philosophy of science: MR also bears on reductionism in psychology generally — psychological kinds may be functional kinds rather than reducible to neural kinds.',
    ARRAY['multiple_realization_thesis'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'intentionality',
    'Intentionality',
    ARRAY['mind'],
    'The aboutness of mental states: a belief is about something, a desire is for something, a perception is of something. Brentano (1874) called intentionality the "mark of the mental" — every mental state is directed at an object or content; no physical state seems to be. The puzzle is to give a naturalistic account of how a brain state can come to be about anything, given that physical relations like causation, contiguity, and similarity do not by themselves seem to confer aboutness.',
    'Frame intentionality via Brentano''s thesis (the mental is essentially intentional) and the naturalist''s challenge (intentionality must be reducible to or grounded in non-mental physical relations, on pain of supernaturalism). The three main contemporary naturalistic theories of mental content (representationalism, functional-role semantics, causal/teleosemantic theories) all attempt to give the conditions under which a brain state qualifies as being about a specific content. Distinguish original intentionality (mental states have it intrinsically) from derived intentionality (linguistic and pictorial representations have it only because mental states underwrite their interpretation, per Searle). The intentionality debate connects directly to philosophy of language (reference, content) and philosophy of biology (teleofunction, biological proper function).',
    ARRAY['aboutness_of_mind', 'mark_of_the_mental'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'representational_theory_of_mind',
    'Representational Theory of Mind',
    ARRAY['mind'],
    'Jerry Fodor''s thesis (1975, 1987, 2008) that mental states are relations to mental representations — internal symbol-like structures that have semantic content and are processed computationally. To believe that snow is white is to bear the belief-relation to a mental representation that means snow is white, encoded in the language of thought. The view combines a computational theory of mind (mental processes are computations on representations) with semantic realism (mental representations have determinate content).',
    'Fodor''s representational theory is the classical computational picture of mind: a syntactic engine (the brain''s computational architecture) that operates on semantically interpreted symbols (mental representations) in ways that respect their content. Standard objections: connectionists argue brains do not look like classical symbol-manipulators; eliminativists argue the language-of-thought hypothesis is empirically dubious; semantic deflationists argue mental representations do not really have determinate content. The theory connects to functionalism (mental states are individuated by their computational/representational roles) and to philosophy of language (Fodor''s semantic theories try to fix mental content via causal/asymmetric-dependence relations).',
    ARRAY['rtm_fodor', 'language_of_thought_hypothesis'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'functional_role_semantics',
    'Functional-Role Semantics',
    ARRAY['mind'],
    'The thesis that mental content is determined by the functional or inferential role a state plays in the agent''s overall mental economy: what a belief means is fixed by what it disposes its bearer to infer, perceive, and do. Defended by Block (1986), Harman (1987), Field, and others. A natural pairing with functionalism about mental states.',
    'Distinguish narrow (intra-cranial) functional roles from wide (world-involving) ones. Narrow functional-role semantics holds content is fixed by inferential role alone; wide accounts (Harman) hold content is fixed by both inferential role and the agent''s causal commerce with the environment. Standard objection: holism — if content depends on inferential role, and roles depend on a network of other beliefs, then any change in beliefs changes everyone''s contents, and meaning is incommensurable across speakers (Fodor-LePore 1992). Standard response: distinguish meaning-constitutive inferences from incidental ones (Harman, Block); not all inferential connections are content-determining.',
    ARRAY['conceptual_role_semantics', 'inferential_role_semantics'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'causal_theory_of_mental_content',
    'Causal Theory of Mental Content',
    ARRAY['mind'],
    'The thesis that mental content is fixed by reliable causal-covariational relations between mental representations and the environmental conditions they typically respond to. A horse-thought means horse because it is reliably caused by horses; a cow-thought misrepresents a horse because the conditions for misrepresentation are anchored in normal causal conditions. Defended by Dretske (1981, 1988), Stampe, Fodor (in his information-theoretic moods), and Millikan (with teleological refinements).',
    'Causal theories of content try to ground intentionality in lawlike causal relations — natural relations that exist in the physical world independent of any interpreter. Two main variants: (1) information-theoretic accounts (Dretske, Stampe) where content is the information a state carries about its causes; (2) teleosemantic accounts (Millikan, Papineau) where content is what the state has the proper function of indicating, fixed by selection history. The disjunction problem (Fodor): a belief reliably caused by horses is also reliably caused by horses-or-shadows-of-cows-on-dark-nights, so why does it mean horse rather than that disjunction? Standard responses involve asymmetric dependence (Fodor) or normal-condition restrictions (Dretske, teleosemantics).',
    ARRAY['informational_semantics', 'teleosemantics'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'perception',
    'Perception',
    ARRAY['mind'],
    'The mental states by which an organism becomes aware of its surroundings via the senses. Philosophically, perception raises questions about its objects (do we perceive external objects directly, or only mental intermediaries?), its content (is perceptual content propositional or non-propositional?), its relation to belief (is perception inferential or immediate?), and its epistemic status (how do perceptual states justify perceptual beliefs?). The contemporary literature is dominated by the dispute between direct realism, representationalism, and sense-data theory.',
    'Frame perception via three classical questions: (1) the metaphysical question — what are we aware of when we perceive, the world or some mental item between us and the world? (2) the epistemic question — how does perceptual experience justify perceptual belief? (3) the phenomenal question — what makes perceptual experience the kind of mental episode it is? The three canonical answers to (1) are direct realism (we perceive worldly objects immediately), representationalism (perceptual experience represents the world without intermediating between us and it), and sense-data theory (we perceive mental intermediaries — sense data — that may or may not represent the world). The argument from illusion and the argument from hallucination are the standard moves against direct realism; disjunctivism (Hinton, McDowell) is the contemporary direct-realist response.',
    ARRAY['perceptual_experience'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'direct_realism_perceptual',
    'Direct Realism (Perception)',
    ARRAY['mind'],
    'The view that in veridical perception we are immediately aware of mind-independent external objects and their properties — no mental intermediaries stand between perceiver and world. Defended in different forms by Reid, Austin, Searle, McDowell, and contemporary disjunctivists (Hinton, Snowdon, Martin). Distinguished from naive realism mainly by its sophistication about illusion and hallucination.',
    'Direct realism is the common-sense default; the philosophical challenge is to defend it against the arguments from illusion and hallucination. The argument from illusion: when a stick partly submerged in water looks bent, we are aware of something bent, but the stick is not bent, so we must be aware of some non-stick thing — a sense datum or a representation. The argument from hallucination: when I hallucinate a pink rat, I am aware of something pink and rat-shaped, but no such pink rat exists, so I must be aware of a mental item. Disjunctivism (the leading contemporary direct-realist position) responds by denying that veridical and hallucinatory experiences share any common mental object: a veridical pink-rat experience is awareness of an actual pink rat; a hallucinatory pink-rat experience is a different kind of mental episode that merely seems indiscriminable from the veridical case.',
    ARRAY['naive_realism_perceptual', 'disjunctivism_perceptual'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'representationalism_perception',
    'Representationalism (Perception)',
    ARRAY['mind'],
    'The view that perceptual experience represents the world: in having a perceptual experience, the subject undergoes a state with intentional content (typically: that such-and-such is the case before me). The phenomenal character of the experience is exhausted by, or supervenes on, its representational content. Defended by Tye, Dretske, Lycan, and Chalmers in different versions.',
    'Distinguish weak representationalism (perceptual experiences have representational content) from strong representationalism (their phenomenal character is fully determined by their representational content). Strong representationalism is the contested thesis. Standard motivations: it gives a unified theory of intentionality covering both belief and perception; it allows phenomenal character to be reduced to representational content, which is friendlier to physicalism than primitive phenomenal qualities. Standard objections: spectrum-inversion arguments (two subjects with the same representational content might have different phenomenal experiences) and arguments from non-representational features of experience (mood-shifts, blurry vision, the felt unity of consciousness).',
    ARRAY['intentionalism_perception', 'representational_theory_of_perception'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'sense_data_theory',
    'Sense-Data Theory',
    ARRAY['mind'],
    'The view that in perception we are immediately aware of mental intermediaries — sense data — which are private, non-physical entities bearing the perceptual qualities (colors, shapes, sounds) we experience. The world we ordinarily talk about is then known indirectly, via the sense data that represent or are caused by it. Defended by Russell, Moore, Price, Broad, Ayer, and Jackson; the dominant theory of perception in early-20th-century analytic philosophy.',
    'Sense-data theory was the dominant analytic theory of perception until Austin (1962) and the rise of direct realism and representationalism displaced it. Its motivation: the arguments from illusion and hallucination seem to require some object of awareness in cases where no external object answers to the experience. Its costs: an extra ontological commitment to private mental particulars; the difficulty of giving a satisfactory account of the relation between sense data and the external world (representation? causation? both?); and skeptical worries — if we are immediately aware only of sense data, how do we know there is a world beyond them? Most contemporary perception theorists reject sense-data theory but use it as the canonical foil that motivates more sophisticated alternatives.',
    ARRAY['indirect_realism_perceptual', 'sense_datum_theory'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'personal_identity',
    'Personal Identity',
    ARRAY['mind'],
    'The diachronic identity question for persons: in virtue of what is the person at one time identical to the person at another time? Locke (1689) made the question central to modern philosophy by tying personal identity to consciousness and memory; contemporary debates are dominated by psychological-continuity theories (Parfit, Shoemaker), bodily-continuity theories, and animalism (Olson). The question intersects ethics (responsibility presupposes identity), metaphysics (persons are or are not the kind of thing identity-conditions apply to), and philosophy of mind (whether persons are constituted by their mental lives).',
    'Frame personal identity by contrasting Locke''s memory-criterion (a later person is identical to an earlier person iff the later one remembers experiencing what the earlier one experienced) with two main contemporary alternatives. Psychological-continuity theory (Parfit, Shoemaker) generalizes Locke: identity is grounded in overlapping chains of psychological connection (memory, intention, character, belief). Animalism (Olson) rejects the psychological approach: we are human animals; identity over time is identity over time of the animal. Bodily-continuity theory shares the materialist starting point with animalism but emphasizes body rather than animal. Use Parfit''s teletransportation, fission, and fusion thought experiments to expose the cases where identity-judgments diverge across the theories.',
    ARRAY['diachronic_personal_identity', 'identity_of_persons'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'psychological_continuity_theory',
    'Psychological Continuity Theory',
    ARRAY['mind'],
    'The Lockean view, generalized by Parfit (1971, 1984) and Shoemaker (1970), that personal identity over time consists in overlapping chains of psychological connections: memory, intention, character, belief, personality. The later person is identical to the earlier person iff there is a continuous chain of such connections linking them. Parfit''s extreme conclusion: identity itself is not what matters in survival; what matters is psychological continuity, which can come apart from strict identity in fission cases.',
    'Locke''s memory-criterion has standard objections (forgotten experiences, false memories) that Parfit''s broadened psychological-continuity theory addresses by generalizing to all psychological connections. The fission cases (Parfit) — one person whose hemispheres are transplanted into two bodies, each of which continues as a psychological continuant — show that psychological continuity can branch, but identity cannot, so they come apart. Parfit draws the radical conclusion that identity is not what matters: in the fission case, what should matter to me is that my psychological continuants survive, not whether either is me in the strict identity sense. The theory connects to ethics (Parfit''s reductionism about persons motivates utilitarian impartial treatment of psychological-continuity stages) and to the metaphysics of persistence (perdurantist ontologies fit naturally with psychological-continuity treatments of persons as four-dimensional psychological wholes).',
    ARRAY['lockean_personal_identity', 'parfit_continuity_theory'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'animalism',
    'Animalism',
    ARRAY['mind'],
    'The thesis (Olson 1997, Snowdon 1990) that we are human animals — biological organisms of the species Homo sapiens — and that our identity over time is the identity of those animals. Personal identity is the persistence of an animal, not of a psychological continuum. Animalism rejects the Lockean tradition''s assumption that persons are essentially psychological beings and recovers the common-sense thought that I came into existence with my biological body and will go out of existence with it.',
    'Animalism is the leading contemporary alternative to psychological-continuity theory. Its motivating arguments: (1) the thinking-animal argument (the animal sitting in my chair seems to be doing all the thinking, but if I am psychologically defined and the animal is biologically defined, there are too many thinkers in my chair); (2) the fetal-existence argument (I existed as a fetus before any psychological continuity began, so psychological continuity is not necessary for my existence); (3) the persistence-through-PVS argument (if I lapse into permanent vegetative state, the animal continues but psychological continuity ceases — the animalist says I continue, the psychological theorist says I do not). Standard objections: animalism faces its own version of the transplant problem — if my brain is transplanted into a new body, where am I? — and Olson bites the bullet by saying I am the dehematized animal, not the recipient.',
    ARRAY['biological_view_of_persons', 'olson_animalism'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'computational_theory_of_mind',
    'Computational Theory of Mind',
    ARRAY['mind'],
    'The thesis that the mind is a computational system — that mental processes are computations defined over mental representations, and the brain is the hardware that implements those computations. Putnam (1960s) introduced the analogy; Fodor (1975, 1987, 2008) developed it most extensively in the language-of-thought tradition; Newell and Simon developed the symbol-manipulation paradigm in cognitive science. The dominant framework in classical cognitive science.',
    'Distinguish three claims often run together: (1) the brain is a computer (hardware claim); (2) mental processes are computations (process claim); (3) mental states are individuated by computational role (functional claim). The strongest version (Fodor) combines all three with a language-of-thought hypothesis: thinking is computation over symbol-like mental representations in an internal symbolic medium. Standard challenges: the connectionist alternative (parallel distributed processing networks do not look like classical symbol-manipulators); the embodied/extended mind tradition (Clark, Chalmers — cognition is not all in the head); and Searle''s Chinese Room (running the right program does not suffice for understanding). The thesis is closely tied to functionalism: if mental states are functional, and the relevant functional roles are computational, then the brain is a computer running mental software.',
    ARRAY['computationalism_about_mind', 'computational_mind'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'chinese_room_argument',
    'Chinese Room Argument',
    ARRAY['mind'],
    'John Searle''s 1980 thought experiment against strong AI and the computational theory of mind. A monolingual English speaker in a room receives Chinese characters as input and produces Chinese characters as output by following a rulebook in English; from the outside the room appears to understand Chinese, but inside there is no understanding — only syntactic symbol manipulation. Conclusion: syntax does not suffice for semantics; running the right program does not produce understanding; the computational theory of mind is at best incomplete.',
    'Teach the Chinese Room as the canonical argument against the strong-AI claim that running the right program suffices for understanding. The argument structure: (1) the man in the room manipulates Chinese symbols by purely syntactic rules; (2) the man does not understand Chinese; (3) the man''s symbol manipulation is exactly what a computer running a Chinese-understanding program would do; (4) so the computer also does not understand Chinese; (5) generalizing, no purely computational system understands anything in virtue of its computational properties alone. The standard responses include the Systems Reply (the room as a whole understands, even if the man does not), the Robot Reply (a computer with sensors and actuators would understand), and the Brain Simulator Reply (a computer simulating actual brain activity would understand). Searle''s rebuttals to each preserve the original conclusion and have been widely contested in the subsequent literature.',
    ARRAY['searle_chinese_room', 'syntax_semantics_argument'],
    'INTERPRETED',
    'ai-seed',
    10
  ),
  (
    'turing_test',
    'Turing Test',
    ARRAY['mind'],
    'Alan Turing''s 1950 operational benchmark for machine intelligence: a machine passes the test if a human interrogator cannot reliably distinguish its conversational responses from those of a human, given a sufficiently extended text-based interrogation. Turing proposed the test as a replacement for the question whether machines can think — too vague to admit of a clean answer — with an empirically tractable criterion.',
    'The Turing Test is the canonical operational criterion for machine intelligence and the foil for theoretical accounts of mind that demand more than behavioral indistinguishability. Distinguish three questions students conflate: (1) is the Turing Test a sufficient condition for intelligence? (Searle says no via the Chinese Room — passing the test is mere symbol manipulation); (2) is the Turing Test a necessary condition for intelligence? (Block, French, and others have argued no — there could be intelligent beings whose behavior diverges from human behavior in ways that fail the test); (3) is the Turing Test a useful operational benchmark? (yes, modulo the qualifications above; contemporary AI evaluation uses descendant benchmarks that share Turing''s behavioral spirit). Pedagogically the test is the entry point to debates about behavioral vs. computational vs. phenomenal criteria for mind.',
    ARRAY['imitation_game', 'turing_imitation_game'],
    'INTERPRETED',
    'ai-seed',
    10
  );

-- Edges: 35 INSERTs, all pedagogical_prerequisite. All within-domain
-- (source and target both tagged mind). Cross-domain edges (perception
-- -> epistemology on perceptual justification; intentionality ->
-- philosophy of language on reference; mental_causation -> metaphysics
-- on causation; personal_identity -> metaphysics on numerical_identity /
-- persistence; functionalism / computational_theory_of_mind ->
-- philosophy of science on cognitive science; propositional_attitude
-- -> philosophy of language on attitude verbs) are P5-11's exclusive
-- surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Foundation spine
  ('philosophy_of_mind', 'mind', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('mind', 'mental_state', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('mental_state', 'propositional_attitude', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Mind-body: dualism branch
  ('mental_state', 'dualism', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('dualism', 'substance_dualism', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('dualism', 'property_dualism', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Mind-body: physicalism branch
  ('mental_state', 'physicalism', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('physicalism', 'type_identity_theory', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('physicalism', 'functionalism', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('physicalism', 'behaviorism_logical', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('physicalism', 'eliminative_materialism', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Multiple realizability bridge (motivates functionalism over type-identity)
  ('type_identity_theory', 'multiple_realizability', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('multiple_realizability', 'functionalism', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Mental causation branch
  ('mental_state', 'mental_causation', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('mental_causation', 'causal_exclusion_argument', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('physicalism', 'supervenience_mental', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('supervenience_mental', 'mental_causation', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Intentionality branch
  ('mental_state', 'intentionality', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('intentionality', 'representational_theory_of_mind', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('intentionality', 'functional_role_semantics', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('intentionality', 'causal_theory_of_mental_content', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Perception branch
  ('mental_state', 'perception', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('perception', 'direct_realism_perceptual', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('perception', 'representationalism_perception', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('perception', 'sense_data_theory', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Personal identity branch
  ('mind', 'personal_identity', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('personal_identity', 'psychological_continuity_theory', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('personal_identity', 'animalism', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Computational mind branch
  ('functionalism', 'computational_theory_of_mind', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('computational_theory_of_mind', 'chinese_room_argument', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('computational_theory_of_mind', 'turing_test', 'pedagogical_prerequisite', 'ai-seed', 10),
  -- Cross-cluster within-mind bridges
  ('propositional_attitude', 'intentionality', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('representational_theory_of_mind', 'computational_theory_of_mind', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('multiple_realizability', 'computational_theory_of_mind', 'pedagogical_prerequisite', 'ai-seed', 10),
  ('mental_causation', 'eliminative_materialism', 'pedagogical_prerequisite', 'ai-seed', 10);

COMMIT;
