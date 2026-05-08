-- Migration: 0046_seed_mind_part1
-- Purpose: Eleventh Phase 5 seed migration (second philosophy-of-mind file) —
--   the consciousness / specialized cluster of philosophy-of-mind concepts
--   and within-domain pedagogical_prerequisite edges. Authored in S-0070
--   against task P5-07b "Philosophy of mind consciousness/specialized seed"
--   of target T-PHASE-5 per engine/build_readiness/phase_5.md (gate report)
--   and product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers exactly the concepts deliberately deferred from P5-07a per the
--   non-responsibilities clause of 0040_seed_mind_part1.sql: consciousness
--   itself (Block's phenomenal/access distinction; Nagel's what-it-is-like
--   framing); the hard problem (Chalmers 1995; Levine's explanatory gap);
--   the canonical arguments against physicalism about phenomenal
--   consciousness (Jackson's knowledge argument / Mary; Chalmers's zombies);
--   phenomenology adjacencies (the philosophical movement; phenomenal
--   concepts and the phenomenal-concept strategy as the type-B materialist
--   response); the leading positive theories of consciousness (panpsychism,
--   integrated information theory, global workspace theory, higher-order
--   theories with HOT as the dominant subtype); qualia disputes (realism,
--   eliminativism, functionalism, the inverted-spectrum challenge);
--   representational accounts of consciousness (representationalism,
--   phenomenal intentionality); and the eliminativist family (Frankish's
--   illusionism, Dennett's multiple-drafts model). Within-domain edges
--   span the new cluster and bridge to P5-07a's existing
--   property_dualism, physicalism, and functionalism nodes — these are
--   within-mind edges (both endpoints tagged 'mind') and therefore the
--   present session's responsibility, not P5-11's. Cross-domain edges
--   (consciousness ↔ epistemology on phenomenal knowledge; phenomenology
--   ↔ epistemology and philosophy of language; panpsychism ↔ metaphysics
--   on fundamentality; IIT/GWT ↔ philosophy of science on cognitive
--   science methodology; phenomenal concept strategy ↔ philosophy of
--   language on concept individuation) remain P5-11's exclusive surface.
-- Loads tables: public.nodes (27 INSERTs), public.edges (35 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 11 -> 12).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 11 at session boot (post-S-0068 per
--     ROUTING.md narrative — most recent applied seed at this prefix
--     range was 0110_seed_aesthetics_part1.sql which wrote 11).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 12 (the
--     post-increment value).
--   * No prior migrations under prefix 0046-0049; this is the first
--     specialized philosophy-of-mind seed file.
--   * P5-07a applied (0040_seed_mind_part1.sql at S-0066): the 30 core
--     mind nodes including mental_state, physicalism, functionalism, and
--     property_dualism that this migration's edges reference exist in
--     public.nodes. Verifying their presence is implicit in the FK
--     constraint on edges (source_id, target_id REFERENCES nodes(id));
--     the apply step's transaction will fail if any reference is
--     unsatisfied.
--   * P5-01a + P5-01b epistemology seeds applied. No edge in this
--     migration references epistemology nodes — within-mind specialization
--     here; cross-domain bridges to epistemology (perception ↔
--     justification; phenomenal vs propositional knowledge) land at
--     P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 27 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'mind'}, status=active, graph_version_added=12.
--   * 35 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=12. All edges are
--     within-domain (source and target both tagged mind); cross-domain
--     edges are P5-11's exclusive responsibility. Edges spanning P5-07a
--     nodes (mental_state, property_dualism, physicalism, functionalism)
--     are within-mind and therefore in scope here.
--   * settings.graph_version = 12.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 12 AND 'mind' = ANY(domain) :: 27
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 12 AND edge_type = 'pedagogical_prerequisite' :: 35
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 12
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that either this migration also
--     inserts OR that 0040_seed_mind_part1.sql previously inserted (the
--     four nodes referenced in cross-cluster bridges: mental_state,
--     property_dualism, physicalism, functionalism).
--   * No edge cycles in the pedagogical_prerequisite subgraph, including
--     when combined with P5-07a's existing edges. Tier assignment
--     (relative to this migration's nodes plus referenced P5-07a nodes):
--     T0 mental_state (P5-07a anchor); T1_new consciousness; T2_new
--     what_its_like, access_consciousness, easy_problems_of_consciousness,
--     phenomenology, global_workspace_theory, higher_order_theory_
--     consciousness, representationalism_consciousness; T3_new
--     phenomenal_consciousness, higher_order_thought_theory, phenomenal_
--     intentionality; T4_new qualia, phenomenal_concept, hard_problem_of_
--     consciousness; T5_new explanatory_gap, knowledge_argument,
--     philosophical_zombie, panpsychism, integrated_information_theory,
--     qualia_realism, qualia_eliminativism, qualia_functionalism;
--     T6_new phenomenal_concept_strategy, illusionism,
--     multiple_drafts_model, inverted_spectrum; T7_new type_b_materialism.
--     P5-07a nodes referenced as edge endpoints: property_dualism (T4 in
--     P5-07a's tiering; bridges to T5_new arguments), physicalism (T3 in
--     P5-07a's; bridges to T2_new and T7_new), functionalism (T4 in
--     P5-07a's; bridges to T5_new and T6_new). Every cross-cluster
--     bridge points from a P5-07a node to one of this migration's nodes
--     of strictly higher tier — no edge points back into P5-07a. SCC
--     freedom holds; validate.py's Kosaraju check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     no triple in this migration duplicates any triple in P5-07a's
--     edge block.
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: phenomenal vs access consciousness
--     and phenomenal_concept bridge to epistemology (P5-01b on phenomenal
--     vs propositional knowledge; bridges to philosophy of language P5-08
--     on concept individuation); phenomenology bridges broadly to
--     epistemology, philosophy of language, and political philosophy
--     (Husserl, Heidegger, Merleau-Ponty's traditions); panpsychism
--     bridges to metaphysics (P5-02a's causation, P5-02b's fundamentality
--     and modality); integrated_information_theory and
--     global_workspace_theory bridge to philosophy of science (P5-09 on
--     cognitive-science methodology, the explanatory adequacy of
--     information-theoretic and global-availability models for
--     consciousness); knowledge_argument and philosophical_zombie bridge
--     to philosophy of language (P5-08 on phenomenal concept reference
--     and the semantics of imagination). Wait for P5-11's cross-bridges
--     pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional specialized-mind sub-ranges
--     (0047-0049). Those slots remain reserved for future Phase 6+
--     extension if telemetry warrants additional consciousness concepts
--     (further sub-positions in the higher-order family; specific
--     theories like attention-schema theory, predictive-processing
--     accounts of consciousness; consciousness-and-attention literature;
--     consciousness in animals and infants; bodily and embodied
--     consciousness; the unity of consciousness and split-brain cases;
--     phenomenal-judgment paradoxes); this seed completes P5-07b's task
--     at the granularity principle within the 0046 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 27/27 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference's entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here
--     is well-named in the SEP/IEP entry inventory and corresponds to a
--     concept the contemporary analytic philosophy-of-mind literature
--     on consciousness (Block, Chalmers, Jackson, Levine, Nagel,
--     Dennett, Tononi, Baars, Rosenthal, Lycan, Tye, Dretske, Searle,
--     Strawson, Goff, Frankish, Loar, Papineau, Stoljar, Horgan,
--     Tienson) explicitly names. Mirrors P5-07a's distribution and the
--     ten prior Phase 5 subject seeds.
--   * domain[] cardinality: every node carries exactly one tag, 'mind'.
--     Multiple cross-domain reaches exist (phenomenology has independent
--     standing as a continental tradition; panpsychism is a metaphysical
--     position; integrated_information_theory is a cognitive-science
--     theory; phenomenal_concept_strategy intersects philosophy of
--     language) but per phase_5.md T2-G #4 (domain-tag cardinality
--     explosions vector), cross-domain tagging belongs to P5-11. The
--     canonical home for each of these concepts in the analytic
--     philosophy-of-mind literature is the consciousness sub-literature,
--     so the single 'mind' tag is correct here.
--   * provenance: 'ai-seed' for every node and edge. Same as
--     P5-01a/b, P5-02a/b, P5-03, P5-04a/b, P5-05, P5-06, P5-07a.
--   * Node selection rationale: 27 concepts cover the six core
--     consciousness/specialized clusters at the granularity principle:
--     (1) foundation (4) [consciousness, phenomenal_consciousness,
--     access_consciousness, qualia] — the umbrella, Block 1995's pivotal
--     phenomenal/access distinction that organizes the whole
--     consciousness literature, plus qualia as the contested
--     philosophical loaded notion of phenomenal-character properties;
--     (2) hard problem and arguments against physicalism (6)
--     [hard_problem_of_consciousness, easy_problems_of_consciousness,
--     explanatory_gap, knowledge_argument, philosophical_zombie,
--     what_its_like] — Chalmers 1995 hard/easy distinction, Levine's
--     1983 explanatory gap framing, Jackson 1982's knowledge argument
--     via Mary, Chalmers 1996's zombie conceivability argument, and
--     Nagel 1974's foundational what-it-is-like-to-be-a-bat paper;
--     (3) phenomenology adjacencies (2) [phenomenology, phenomenal_
--     concept] — the continental tradition (Husserl, Heidegger,
--     Merleau-Ponty) read pedagogically through its consciousness
--     concerns, plus the analytic notion of phenomenal concepts that
--     anchors the type-B materialist response strategy;
--     (4) positive theories of consciousness (5) [panpsychism,
--     integrated_information_theory, global_workspace_theory,
--     higher_order_theory_consciousness, higher_order_thought_theory] —
--     the four leading positive frameworks plus HOT as the dominant
--     higher-order subtype (Strawson/Goff panpsychism;
--     Tononi IIT; Baars/Dehaene GWT; Rosenthal HOT);
--     (5) qualia disputes (4) [qualia_realism, qualia_eliminativism,
--     qualia_functionalism, inverted_spectrum] — the three main
--     positions on qualia plus the canonical thought experiment that
--     pressures functionalist treatments;
--     (6) representational, eliminativist, and type-B replies (6)
--     [representationalism_consciousness, phenomenal_intentionality,
--     phenomenal_concept_strategy, type_b_materialism, illusionism,
--     multiple_drafts_model] — Tye/Dretske representationalism for
--     consciousness; Horgan-Tienson phenomenal intentionality; Loar's
--     phenomenal-concept strategy and the type-B materialism it yields;
--     Frankish's contemporary illusionism and Dennett's multiple-drafts
--     model as the leading eliminativist positive views.
--   * Edge structure: 35 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation spine flows mental_state (P5-07a) →
--     consciousness, with consciousness branching to the seven
--     mid-tier surfaces (what_its_like as Nagel's entry; access_
--     consciousness as Block's other half; easy_problems_of_consciousness
--     as the contrast pole; phenomenology, global_workspace_theory,
--     higher_order_theory_consciousness, representationalism_consciousness
--     as parallel positive frameworks). What_its_like → phenomenal_
--     consciousness (Block's technical formalization of Nagel's intuition)
--     → qualia (the property-talk version), and → phenomenal_concept
--     (the second-order conceptual machinery), and → hard_problem_of_
--     consciousness (Chalmers's framing). Easy_problems → hard_problem
--     (the contrast structure). Hard_problem → explanatory_gap (Levine's
--     1983 priority becomes a bullet under Chalmers's later framing
--     pedagogically), → knowledge_argument, → philosophical_zombie (the
--     two canonical arguments that pressure physicalism), → panpsychism,
--     → integrated_information_theory (the two leading non-physicalist /
--     fundamental-consciousness positive theories that respond to the
--     hard problem). Property_dualism (P5-07a) → knowledge_argument,
--     property_dualism → philosophical_zombie (the position is taught
--     before the supporting arguments per the position-then-argument
--     ordering convention). Knowledge_argument → phenomenal_concept_
--     strategy (Loar's response targets the argument); phenomenal_concept
--     → phenomenal_concept_strategy (the strategy uses the conceptual
--     machinery); phenomenal_concept_strategy → type_b_materialism
--     (the strategy yields the position); physicalism → type_b_
--     materialism (genus-species). Physicalism → easy_problems (the
--     easy problems are tractable for physicalism). Higher_order_theory_
--     consciousness → higher_order_thought_theory (umbrella → dominant
--     subtype). Representationalism_consciousness → phenomenal_
--     intentionality (the two related representational accounts).
--     Qualia → qualia_realism, qualia → qualia_eliminativism, qualia →
--     qualia_functionalism (three parallel positions). Qualia_
--     eliminativism → illusionism (Frankish's contemporary version) and
--     → multiple_drafts_model (Dennett's specific positive theory).
--     Qualia_functionalism → inverted_spectrum (the canonical objection
--     to functionalist treatment of qualia). Functionalism (P5-07a) →
--     qualia_functionalism (genus-species), and functionalism →
--     inverted_spectrum (the inverted-spectrum thought experiment is
--     pressed against functionalism generally, not just qualia
--     functionalism — Block 1978 China-brain is its companion).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 12; DELETE FROM public.nodes WHERE id IN (the 27 ids inserted
--   here); UPDATE public.settings SET value = '11'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 63 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry);
--   product/seed-graph/migrations/0040_seed_mind_part1.sql (P5-07a
--   philosophy-of-mind core seed; pattern reference and the source of
--   the four bridge-target nodes mental_state, property_dualism,
--   physicalism, functionalism);
--   product/seed-graph/migrations/0030_seed_metaphysics_part1.sql
--   (P5-02a metaphysics core; pattern reference);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 11 at session boot (post-S-0068 state per ROUTING.md
-- narrative); write 12 here; every node/edge below carries
-- graph_version_added = 12.
UPDATE public.settings
  SET value = '12'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 27 INSERTs covering the six consciousness/specialized clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'consciousness',
    'Consciousness',
    ARRAY['mind'],
    'The umbrella term for the diverse phenomena unified by the fact that there is something it is like to undergo them: perceptions, sensations, thoughts, emotions, moods, dreams. Philosophy of mind treats consciousness as the central explanandum, asking how something physical can also be experiential and what relations hold between conscious experience and the brain, behavior, and the contents of thought.',
    'Distinguish consciousness from related notions students often conflate: (1) wakefulness as a global state vs. consciousness of particular contents; (2) self-consciousness (awareness of oneself) vs. consciousness simpliciter (awareness of anything at all); (3) creature consciousness (the organism is conscious) vs. state consciousness (a particular state is conscious). The contemporary analytic literature is dominated by the question of phenomenal consciousness specifically — the qualitative, what-it-is-like aspect — and its relation to physical processes, with Block''s 1995 phenomenal/access distinction, Chalmers''s 1995 hard problem, and Nagel''s 1974 bat paper as the field''s pedagogical entry points. Beyond analytic philosophy, the phenomenological tradition (Husserl, Heidegger, Merleau-Ponty) treats consciousness as the structuring feature of human experience and develops a distinctive vocabulary (intentionality in Husserl''s noematic sense, being-in-the-world for Heidegger, embodied perception for Merleau-Ponty); analytic engagement with that tradition has grown via Dreyfus and others.',
    ARRAY['conscious_experience', 'awareness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'phenomenal_consciousness',
    'Phenomenal Consciousness',
    ARRAY['mind'],
    'Ned Block''s (1995) term for the experiential aspect of conscious mental states: their qualitative, felt, what-it-is-like character. Distinguished from access consciousness (the functional aspect of being globally available for reasoning, report, and behavioral control). Phenomenal consciousness is what the hard problem and the knowledge and zombie arguments target; access consciousness is the functional notion physicalists most easily accommodate.',
    'Block''s distinction is the single most important pedagogical move in the consciousness literature post-1995. P-consciousness is the felt redness of a red experience, the painfulness of pain, the eerie quality of fear. A-consciousness is the same state being available for verbal report, for use in reasoning, for the rational guidance of action. Block argues these can come apart in principle: a state could be P-conscious without being A-conscious (someone hearing a sound but not yet attending to it) or A-conscious without being P-conscious (a hypothetical zombie''s functional state). The standard physicalist response is either to reject the distinction (consciousness is just A-consciousness) or to accept it and deny that P-consciousness is anything beyond what its A-consciousness implements. Use Block''s distinction whenever a student asks "what kind of consciousness do you mean?" — the honest answer is almost always "phenomenal."',
    ARRAY['p_consciousness', 'qualitative_consciousness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'access_consciousness',
    'Access Consciousness',
    ARRAY['mind'],
    'Ned Block''s (1995) term for the functional aspect of conscious mental states: their being globally available for use in reasoning, verbal report, and the rational control of behavior. Distinguished from phenomenal consciousness (the qualitative, what-it-is-like aspect). Access consciousness is functional and structural; physicalist theories — type-identity theory, functionalism, global workspace theory — accommodate it readily.',
    'A-consciousness is what cognitive science measures: the conditions under which a subject can report a stimulus, use it in reasoning, control action with it. The empirical research on subliminal perception, attentional blink, change blindness, and binocular rivalry is largely about A-consciousness. The philosophical interest of the access/phenomenal distinction is that A-consciousness leaves the hard problem untouched: even a complete functional explanation of why states are A-conscious does not explain why those states are P-conscious. Block''s framing forces theorists to be explicit about which they are theorizing — the global workspace tradition (Baars, Dehaene) primarily theorizes A-consciousness; higher-order theories aim at both but are most successful with A; representationalist theories aim at unifying both via representational content.',
    ARRAY['a_consciousness', 'functional_consciousness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'qualia',
    'Qualia',
    ARRAY['mind'],
    'The qualitative properties of conscious experience: the redness of red, the painfulness of pain, the sweetness of sugar. The traditional notion in philosophy of mind for the felt character of phenomenal states. Whether qualia exist as primitive phenomenal properties (qualia realism), are functional properties (qualia functionalism), or do not exist as commonly conceived (qualia eliminativism, illusionism) is the central dispute structuring the contemporary literature.',
    'The qualia debate is where students most need a careful map. Realists (Block, Chalmers, early Nagel) treat qualia as irreducible introspectible properties that any complete theory of mind must accommodate. Functionalists (Lewis, Lycan in some moods) try to identify qualia with functional roles. Eliminativists (Dennett 1988 "Quining Qualia"; Frankish 2016 illusionism) deny the philosophical loaded notion of qualia, holding that what we introspect when we appear to attend to qualia is something else entirely — judgments, dispositions, or representational content. The eliminativist move is not denial that experience exists; it is denial that the special philosophical concept (intrinsic, ineffable, infallibly accessible, private) refers to anything. Pedagogically, treat qualia as a contested theoretical posit, not a phenomenological datum: that experience has felt character is data; that the felt character is non-functional, non-representational, and irreducibly intrinsic is a claim qualia realists make on behalf of the data, which their opponents dispute.',
    ARRAY['qualia_phenomenal', 'qualitative_character'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'hard_problem_of_consciousness',
    'Hard Problem of Consciousness',
    ARRAY['mind'],
    'David Chalmers''s (1995) framing of the central explanatory challenge for consciousness: explaining why physical processes are accompanied by phenomenal experience at all. Distinguished from the easy problems (explaining how the brain integrates information, controls behavior, reports its states, etc.), which yield to standard cognitive-scientific methodology. The hard problem is hard because no functional or structural story seems to entail why those functions and structures should be accompanied by what-it-is-like character.',
    'Teach the hard problem via Chalmers''s framing: the easy problems (perceptual discrimination, integration of information, the difference between wakefulness and sleep, attention, behavioral control, verbal report) ask how the mechanisms work — they admit answers in computational, neurobiological, and functional terms. The hard problem asks why any of those mechanisms is accompanied by phenomenal experience — why isn''t it all "in the dark"? Chalmers''s claim is that even a complete answer to all easy problems leaves the hard problem open: no functional account entails the existence of phenomenal consciousness. The hard problem motivates Chalmers''s naturalistic dualism (consciousness is fundamental and irreducible). Standard physicalist responses include rejecting the easy/hard distinction (Dennett), accepting it but denying that phenomenal consciousness is anything beyond functional consciousness (type-A materialism), or accepting it and adopting a phenomenal-concept-strategy response (type-B materialism: the apparent gap is conceptual, not metaphysical).',
    ARRAY['chalmers_hard_problem', 'consciousness_hard_problem'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'easy_problems_of_consciousness',
    'Easy Problems of Consciousness',
    ARRAY['mind'],
    'Chalmers''s (1995) term for the cluster of explanatory challenges about consciousness that admit of standard cognitive-scientific or neurobiological solution: explaining how the brain discriminates stimuli, integrates information, controls behavior, reports its states, distinguishes wakefulness from sleep, focuses attention. "Easy" relative to the hard problem of phenomenal consciousness — these are not easy in absolute terms, only in the methodological sense that we know what kind of explanation would solve them.',
    'The easy/hard distinction does the heavy lifting in Chalmers''s argument. Easy problems are easy because their solutions consist in specifying mechanisms — neural circuits, computational processes, information-flow architectures — that perform the function in question. We can say with confidence what would count as an answer even if we do not yet have one. Hard problems are hard because no specification of any mechanism, however detailed, seems to entail the phenomenal existence of what-it-is-like character. Pedagogically the easy problems set the contrast that motivates the hard. Empirically the easy problems are where cognitive neuroscience has made enormous progress (binocular rivalry, attentional blink, the global workspace, neural correlates of consciousness). Physicalists who reject the hard/easy distinction (Dennett, Searle in some moods, Frankish) typically argue that solving all the easy problems IS solving the hard problem — there is no further phenomenon left over.',
    ARRAY['chalmers_easy_problems', 'cognitive_consciousness_problems'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'explanatory_gap',
    'Explanatory Gap',
    ARRAY['mind'],
    'Joseph Levine''s (1983) thesis that there is an explanatory gap between physical descriptions of brain states and the phenomenal character of conscious experience: even if we knew all the physical facts about pain, we would not understand why pain feels the way it does. The thesis precedes Chalmers''s 1995 hard-problem framing and is often treated as its epistemic-side companion: the hard problem is metaphysical (what is the relation?), the explanatory gap is epistemic (why can''t we explain the relation?).',
    'Levine''s 1983 paper "Materialism and Qualia: The Explanatory Gap" is a foundational text. Levine''s claim is weaker than Chalmers''s: he holds that the gap is real but does not draw immediate metaphysical conclusions. The gap could be a permanent feature of human cognition (consciousness has a special epistemic status that resists physical explanation) without showing that consciousness is metaphysically distinct from the physical. Type-B materialists (Loar, Papineau) accept the explanatory gap and explain it via the special character of phenomenal concepts: phenomenal concepts and physical concepts pick out the same property under different modes of presentation, and the conceptual gap does not reflect a metaphysical gap. Type-A materialists (Dennett, Frankish) deny the gap is genuine — they hold the apparent inexplicability is itself a cognitive illusion. Pedagogically the explanatory gap is the cleanest entry point into the hard problem because it states the explanatory difficulty without committing to its metaphysical interpretation.',
    ARRAY['levine_explanatory_gap', 'consciousness_explanatory_gap'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'knowledge_argument',
    'Knowledge Argument (Mary)',
    ARRAY['mind'],
    'Frank Jackson''s (1982) thought-experimental argument against physicalism. Mary, a brilliant scientist, has lived her whole life in a black-and-white room studying color vision; she knows every physical fact about color perception. When released and shown red for the first time, she learns something new — what red looks like. So there are facts beyond the physical facts; physicalism, which holds that all facts are physical, is false. The leading 20th-century argument for property dualism, alongside the zombie argument.',
    'Teach the knowledge argument via the simple structure: (1) before release, Mary knows all physical facts about color experience; (2) on release, she learns something new (what red looks like); (3) so there are facts she did not know before, and those facts are not physical; (4) physicalism is false. The standard physicalist responses include: ability hypothesis (Lewis, Nemirow — Mary gains a new ability, not a new fact), acquaintance hypothesis (Conee — she gains a new mode of acquaintance with a fact she already knew), phenomenal concepts strategy (Loar — she gains a new phenomenal concept of a physical fact she already knew under a physical concept), and outright denial (Dennett — she does not learn anything new, as a complete physical knowledge would already include knowing what red looks like). Jackson himself eventually retracted the argument in favor of physicalism (2003), but the original 1982 paper remains the canonical pedagogical entry point. Pair with the zombie argument: zombies make the metaphysical claim (consciousness is not physical); Mary makes the epistemic claim (knowledge of consciousness is not exhausted by knowledge of the physical).',
    ARRAY['marys_room', 'jackson_knowledge_argument'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'philosophical_zombie',
    'Philosophical Zombie',
    ARRAY['mind'],
    'A hypothetical being physically and functionally identical to a normal human but lacking phenomenal consciousness — there is nothing it is like to be a zombie, even though it behaves exactly as a conscious person would. David Chalmers''s (1996) zombie argument: if zombies are conceivable they are possible; if possible, phenomenal consciousness does not supervene on the physical; so physicalism is false. The argument presses the conceivability-to-possibility inference into service against physicalism.',
    'Chalmers''s zombie argument is the leading metaphysical anti-physicalist argument. The structure: (1) zombies (physical/functional duplicates lacking phenomenal consciousness) are conceivable; (2) what is conceivable is possible (the conceivability-to-possibility inference, defended via two-dimensional semantics); (3) if zombies are possible, phenomenal consciousness does not supervene on the physical with metaphysical necessity; (4) so physicalism is false. The argument relies heavily on the conceivability-possibility link. Standard responses target each step: deny zombies are conceivable on careful reflection (Dennett — what we imagine when we imagine zombies is not a coherent scenario); deny the conceivability-possibility inference (Yablo, Loar, Papineau — conceptual possibility does not entail metaphysical possibility, and apparent zombie conceivability reflects only the special structure of phenomenal concepts); accept the inference but reframe the metaphysics (some Russellian monists accept zombie possibility but deny it refutes the relevant physicalism). Pair with the knowledge argument as the two canonical anti-physicalist arguments: zombies target the metaphysics (what consciousness IS); Mary targets the epistemology (what we KNOW about consciousness).',
    ARRAY['chalmers_zombie', 'zombie_argument'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'what_its_like',
    'What It Is Like (Nagel)',
    ARRAY['mind'],
    'Thomas Nagel''s (1974) framing of the phenomenal aspect of conscious experience: a creature has conscious experience if there is something it is like, for that creature, to be that creature. Introduced in "What Is It Like to Be a Bat?", the formula has become the canonical entry point for the phenomenal character of consciousness — the thing that physicalist reduction has trouble accounting for.',
    'Nagel''s 1974 paper is one of the most influential short texts in 20th-century philosophy of mind. The argument: even if we knew everything physical about a bat — its echolocation system, its neural architecture, its behavioral repertoire — we would not know what it is like to be a bat, because the bat''s phenomenal perspective is essentially first-personal and inaccessible from any third-personal physical description. Nagel does not draw a metaphysical conclusion (he is not an anti-physicalist) but he establishes the phenomenon: phenomenal consciousness has a subjective character that resists objective description. The "what it is like" formula precedes Block''s phenomenal/access distinction (1995) by 21 years and Chalmers''s hard problem (1995) by 21 years; both later framings build on Nagel''s framing. Use Nagel''s bat as the pedagogical opening for any consciousness lesson — it isolates the phenomenon without committing to a particular metaphysics.',
    ARRAY['nagel_bat', 'subjective_character'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'phenomenology',
    'Phenomenology',
    ARRAY['mind'],
    'The 20th-century philosophical movement initiated by Edmund Husserl that takes consciousness as its primary subject matter and proposes a method (phenomenological reduction or epoché) for studying conscious experience as it is given, bracketing questions of metaphysical reality. Major figures: Husserl, Heidegger, Sartre, Merleau-Ponty, Levinas. Distinguished from analytic philosophy of mind by methodology and vocabulary but engaged with overlapping subject matter.',
    'Phenomenology and analytic philosophy of mind are two traditions theorizing consciousness from largely independent vocabularies. Husserl''s phenomenology centers on intentionality (consciousness is always consciousness of something) and seeks to describe the structures of conscious experience — perception, imagination, memory, intersubjectivity — without metaphysical commitment. Heidegger reframes intentionality as being-in-the-world: conscious life is always already engaged with a meaningful world. Merleau-Ponty develops embodied phenomenology: perception is structured by the lived body. Pedagogically, phenomenology offers the analytic student a richer vocabulary for first-personal description of experience (the structure of attention, the phenomenology of the body, the temporal flow of consciousness) than analytic frameworks typically provide. Hubert Dreyfus''s analytic-phenomenology bridge work and the more recent neurophenomenology (Varela) connect the traditions. The analytic literature on consciousness has grown more receptive to phenomenological description, especially around embodied cognition and the phenomenology of attention.',
    ARRAY['husserlian_phenomenology', 'phenomenological_tradition'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'phenomenal_concept',
    'Phenomenal Concept',
    ARRAY['mind'],
    'A concept that picks out a phenomenal property under a phenomenal mode of presentation — the kind of concept we deploy when we attend to and refer to our own conscious experience as such. Phenomenal concepts are typically held to be conceptually distinct from any physical concept, even when both refer to the same underlying property. Central to the type-B materialist response to the knowledge and zombie arguments.',
    'Phenomenal concepts are the conceptual machinery type-B materialists use to explain the apparent gap between physical and phenomenal descriptions while remaining physicalists about the metaphysics. The view: phenomenal concepts and physical concepts are conceptually independent (you can possess one without the other) but pick out the same physical property. Mary''s new knowledge on release is a new way of grasping a property she already knew under a different mode of presentation; zombies are conceivable because the phenomenal concept and the physical concept are conceptually independent, but conceivability does not entail metaphysical possibility. Standard objections target the explanatory adequacy of the phenomenal-concept story (Chalmers — phenomenal concepts cannot do the work needed without smuggling in the very phenomenal properties they are supposed to explain away) and the apparent specialness of phenomenal concepts (Stoljar, Levin — what makes phenomenal concepts special if all concepts ultimately track physical properties?). Pedagogically, phenomenal concepts are the entry point to type-B materialism: a sophisticated middle position between Dennett-style eliminativism and Chalmers-style anti-physicalism.',
    ARRAY['phenomenal_concepts', 'experiential_concept'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'panpsychism',
    'Panpsychism',
    ARRAY['mind'],
    'The thesis that consciousness or its precursors are fundamental and ubiquitous features of the physical world — present in some form in even simple physical systems. Defended in various contemporary versions by Galen Strawson (2006), Philip Goff (2017), and David Chalmers (2015 in his constitutive Russellian moods). A serious revival of a historically marginal position, motivated by the difficulty of explaining the emergence of consciousness from non-conscious matter (the combination problem aside).',
    'Contemporary panpsychism is not the view that rocks have rich inner lives. It is the view that the intrinsic nature of fundamental physical entities (whatever ultimately fills the roles physics describes structurally) is or includes phenomenal or proto-phenomenal properties. Russellian monism is the most refined version: physics describes only the dispositional/structural roles of physical entities; their categorical or intrinsic nature must be something — Russell suggested experience or its precursors. The advantage: consciousness need not "emerge" mysteriously from non-conscious matter because it was already at the bottom. The major problem is the combination problem (Chalmers, Goff, Coleman): how do micro-level proto-phenomenal properties combine to yield the unified macro-level phenomenal experience of, say, a human subject? Various sophisticated combination accounts exist (constitutive panpsychism, cosmopsychism via priority monism, integrated information panpsychism connecting to IIT) but none is uncontroversial. Pedagogically, panpsychism is the most credible non-physicalist alternative to property dualism in contemporary philosophy of mind.',
    ARRAY['panexperientialism', 'russellian_monism'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'integrated_information_theory',
    'Integrated Information Theory',
    ARRAY['mind'],
    'Giulio Tononi''s theory of consciousness as integrated information: a system is conscious to the degree that its informational structure is irreducibly integrated, measured by the quantity Φ (phi). Consciousness is identified with maximally integrated information; the quantity and structure of a system''s consciousness are determined by its causal organization. Defended in Tononi 2004, 2008, 2012 and refined extensively since.',
    'IIT is the most explicit attempt to provide a quantitative theory of consciousness. The core claims: (1) consciousness is integrated information; (2) integrated information is measured by Φ, computed over the system''s causal structure; (3) Φ predicts both whether and to what extent a system is conscious, and the structure of Φ predicts the qualitative character of conscious experience. IIT has empirical purchase (it predicts patterns in EEG and fMRI data on disorders of consciousness, anesthesia, and dreamless sleep) and metaphysical bite (it implies consciousness in any system with sufficient integrated information, leading some — Tononi himself, Koch, Goff — to a panpsychist conclusion). The theory faces both empirical challenges (Φ is computationally intractable for any large system; alternative theories like global workspace make different predictions) and conceptual challenges (Bayne and Tsuchiya — IIT''s axioms about consciousness may not be well-grounded; Searle — IIT is a category mistake confusing information with experience). Pedagogically, IIT is the canonical example of a positive scientific theory of consciousness with both quantitative predictive content and explicit metaphysical implications.',
    ARRAY['iit_consciousness', 'tononi_iit', 'phi_consciousness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'global_workspace_theory',
    'Global Workspace Theory',
    ARRAY['mind'],
    'Bernard Baars''s (1988) cognitive theory that consciousness arises from the global broadcasting of information across the brain: a piece of information becomes conscious when it is selected for entry into a global workspace and made available to specialized cognitive processes throughout the system. Extended into a neurobiological theory by Stanislas Dehaene and colleagues (the Global Neuronal Workspace), with extensive empirical support from masking, attentional-blink, and binocular-rivalry studies.',
    'GWT is the leading scientific (rather than primarily philosophical) theory of consciousness. The core claim: the brain operates with a vast set of specialized parallel processes; only a small subset of their outputs gets selected, broadcast across the system, and made available to all the others. That broadcast is what consciousness is, on the GWT. Pedagogically the theory shines at the easy problems: it explains why conscious states are reportable (they are globally available, including to verbal-output processes), why they are limited in capacity (the workspace is bandwidth-limited), why they integrate information across modalities (they are broadcast widely). It explains less obviously why broadcast should be accompanied by phenomenal experience — that is, GWT primarily theorizes A-consciousness, leaving the hard problem about P-consciousness underaddressed. Defenders (Dehaene, especially in his 2014 book "Consciousness and the Brain") argue that GWT makes specific empirical predictions about neural correlates of consciousness that are well-confirmed; critics (Block, Chalmers) argue that even granting GWT''s account of access consciousness, it leaves phenomenal consciousness untouched.',
    ARRAY['gwt_consciousness', 'baars_workspace_theory', 'global_neuronal_workspace'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'higher_order_theory_consciousness',
    'Higher-Order Theory of Consciousness',
    ARRAY['mind'],
    'The family of theories that hold a mental state is conscious in virtue of being the object of a higher-order mental state about it: a first-order pain becomes conscious when there is a higher-order representation that one is in pain. Variants differ on what kind of higher-order state matters (thought, perception, or representation more broadly). Defended by David Rosenthal, William Lycan, Peter Carruthers, and others.',
    'Higher-order theories occupy a distinctive space in the consciousness literature: they offer a reductive functional account of consciousness while preserving the intuition that conscious states have a special second-order structure. The motivation: only states represented to oneself feel conscious; unrepresented states (subliminal perception, peripheral processing) do not. Pedagogically the theories solve a puzzle the global workspace tradition leaves open: what makes broadcast information specifically conscious rather than just widely available? The higher-order answer: it becomes available to the higher-order representational system. Standard objections target the empirical adequacy (Block — conscious states do not always seem accompanied by self-attributions) and the threat of regress (if higher-order states themselves need higher-order states to be conscious, there is a regress; if they do not, the theory is asymmetric). Rosenthal''s solution: only first-order states are made conscious by their higher-order partners; the higher-order states themselves are not conscious unless yet-higher-order states represent them.',
    ARRAY['hot_theory_family', 'higher_order_consciousness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'higher_order_thought_theory',
    'Higher-Order Thought Theory',
    ARRAY['mind'],
    'David Rosenthal''s (1986, 1997, 2005) version of higher-order theory: a mental state is conscious in virtue of being accompanied by a thought (a HOT) about that state. To be in conscious pain is to be in pain plus to think one is in pain, where the thought is non-inferentially produced and accurately represents the first-order state. The dominant subtype of higher-order theory.',
    'Rosenthal''s HOT theory is the most developed higher-order account. The view''s structure: (1) a first-order mental state M; (2) a higher-order thought H about M, formed non-inferentially; (3) M''s being conscious consists in there being such an H. The theory has elegant features: it offers a reductive account of consciousness in terms of representations alone (no special phenomenal properties needed), it explains why conscious states are introspectible (introspection is having yet-higher-order thoughts about the lower-order ones), and it predicts dissociations between first-order processing and consciousness (states processed without a HOT about them are unconscious). Standard challenges: misrepresentation cases (what if the HOT misrepresents? Rosenthal: the consciousness is determined by how the state is represented, not what it actually is — a feature critics call counterintuitive); the empirical question of whether non-human animals and pre-linguistic infants have HOTs (Rosenthal''s defenders: HOT does not require linguistic structure; critics: any non-linguistic version is too thin to do the work). Pair with HOP (higher-order perception, Lycan) as the two main subtypes within the higher-order family.',
    ARRAY['hot_consciousness', 'rosenthal_hot'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'qualia_realism',
    'Qualia Realism',
    ARRAY['mind'],
    'The view that qualia are real, irreducible, non-functional, intrinsic properties of conscious experience. Defenders (Block 1990, Chalmers 1996, Jackson 1982 pre-retraction) treat qualia as primitive features that any complete theory of mind must accommodate, not as functional or representational properties. The position is opposed by qualia eliminativism (Dennett, Frankish), qualia functionalism (Lewis, Lycan), and qualia representationalism (Tye, Dretske).',
    'Qualia realism is a metaphysically robust position: it commits to phenomenal properties existing as part of the basic ontology of mind. Different qualia realists adopt different metaphysical complements: anti-physicalists who treat qualia as non-physical (Chalmers — naturalistic dualism); physicalists who treat qualia as identical to specific physical properties under a special mode of presentation (Block''s NCC physicalism in some moods); panpsychists who treat qualia as fundamental and ubiquitous (Strawson, Goff). The view''s appeal is its respect for the apparent face value of phenomenal experience — what we directly know about pain seems to be its painfulness, not its functional role. The view''s costs are explanatory: how do irreducible qualia fit into a physical world? How do they relate to behavior, to neural states, to the rest of psychology? Pedagogically, qualia realism is the position the eliminativists and functionalists are denying; teaching the dispute requires giving qualia realism its strongest formulation as a starting point.',
    ARRAY['phenomenal_realism', 'qualia_property_realism'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'qualia_eliminativism',
    'Qualia Eliminativism',
    ARRAY['mind'],
    'The view that qualia, as commonly conceived (intrinsic, ineffable, infallibly accessible, private phenomenal properties), do not exist — what we introspect when we appear to attend to qualia is something else (representational content, functional roles, reactive dispositions). Daniel Dennett''s (1988) "Quining Qualia" is the canonical statement; Keith Frankish''s (2016) illusionism is the contemporary version. Distinguished from eliminative materialism about consciousness as a whole.',
    'Dennett''s 1988 paper argues that the philosophical concept of qualia (with its four canonical features — intrinsic, ineffable, immediately apprehensible in consciousness, immediately known) is a confused theoretical posit that does not pick out anything real. What introspection delivers is reactive dispositions, judgments, and information about one''s mental states — not special phenomenal properties. The position is not denial that experience exists; it is denial that the technical philosophical concept refers. Frankish''s illusionism formalizes this into the claim that phenomenal consciousness is an introspective illusion — there is something it is like to introspect, but the felt phenomenal properties are how introspection misrepresents non-phenomenal physical states, not properties the states genuinely have. Standard objections: the position is self-undermining (the experience of reading the argument is itself phenomenal; Dennett''s claim that this is illusion seems to require that there be an illusory phenomenal seeming, which is itself phenomenal); the empirical question of whether the philosophical concept of qualia is really as the eliminativist describes it (Block, Chalmers — the concept is innocent of the canonical features Dennett attacks). Pedagogically, qualia eliminativism is the most surprising position in the consciousness literature; teach it carefully because students typically dismiss it before understanding it.',
    ARRAY['quining_qualia', 'dennett_qualia_eliminativism'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'qualia_functionalism',
    'Qualia Functionalism',
    ARRAY['mind'],
    'The view that qualia are functional properties — qualia are what they do, individuated by their typical causal relations to perceptual inputs, cognitive states, and behavioral outputs. Defended by David Lewis, William Lycan in some moods, Sydney Shoemaker. A minority position because of the inverted-spectrum and absent-qualia objections that pressure functionalist treatments specifically of phenomenal character.',
    'Qualia functionalism is the natural extension of functionalism about mental states to the specific case of phenomenal properties. If beliefs and desires are functional roles, why not pains and color experiences too? The view''s appeal is theoretical economy: it preserves a unified functionalist ontology of mind without admitting irreducible non-functional phenomenal properties. The view''s costs are the canonical objections to functionalism: the inverted-spectrum case (Block, Shoemaker — two functional duplicates could have systematically inverted color experience, which functionalism cannot distinguish), the absent-qualia case (Block 1978 China-brain — a functional duplicate could lack qualia altogether, which functionalism must deny). Shoemaker''s response: appeal to the role of qualia in their own self-monitoring, holding that inverted spectrum is impossible because the inverted experiences would not have the same functional relation to their introspective effects. Pedagogically, qualia functionalism is the position that motivates teaching the inverted-spectrum thought experiment — it is the natural target.',
    ARRAY['functionalism_qualia', 'role_functionalism_qualia'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'inverted_spectrum',
    'Inverted Spectrum',
    ARRAY['mind'],
    'A thought-experimental scenario in which two subjects are functional duplicates but their color experiences are systematically inverted: where one experiences red the other experiences green, with all other functional relations preserved (both call ripe tomatoes "red", both stop at red traffic lights). The scenario is the canonical objection to functionalist treatments of qualia: if the two subjects are functionally identical but phenomenally different, qualia are not functional properties.',
    'The inverted spectrum has a long history (Locke 1689 considered the possibility) but became central in the late-20th-century functionalism debate via Block, Shoemaker, and Harman. The argument structure: (1) inverted spectrum is conceivable; (2) if conceivable, possible; (3) if possible, two functional duplicates can differ in qualia; (4) so qualia are not functional properties; (5) so qualia functionalism is false. Standard responses target each step. Shoemaker (1982): inverted spectrum is impossible because the inverted experiences would not have the same functional relation to their own introspection (the subject would notice the inversion). Harman (1990): inverted-spectrum scenarios are not coherent given representationalism — if perceptual experience is essentially representational and ripe tomatoes look red because they represent ripe-tomato-color, the functional duplicate represents the same color and so has the same phenomenal character. Block: inverted spectrum is genuinely conceivable and possible, refuting functionalism; the right move is to acknowledge non-functional qualia. Pair with the absent-qualia argument (Block 1978 China-brain) as the two canonical anti-functionalist arguments about phenomenal character.',
    ARRAY['inverted_qualia', 'spectrum_inversion'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'representationalism_consciousness',
    'Representationalism (Consciousness)',
    ARRAY['mind'],
    'The view that the phenomenal character of conscious experience is wholly determined by, or identical to, its representational content: what it is like to have an experience is fixed by what the experience represents the world as being. Defended by Michael Tye (1995, 2000), Fred Dretske (1995), William Lycan (1996), and Alex Byrne. Distinguished from representationalism about perception (a narrower thesis) and from representational theory of mind (which is about content, not specifically consciousness).',
    'Representationalism about consciousness is the most ambitious unifying program in contemporary philosophy of mind. The view ties phenomenal character to representational content, allowing physicalists to explain the phenomenal in terms of the representational, which is in turn naturalized via causal/teleosemantic theories. Pedagogically the view''s elegance is its main attraction: a single relation (representation) explains both intentionality and phenomenal character. Standard objections target the same kinds of cases that pressure functionalism: inverted spectrum (two subjects can represent the same content with inverted phenomenal characters — but Harman and Tye argue that inversion changes content and so is not a counterexample); blurry vision and afterimages (these have phenomenal character but no straightforward representational content of features in the world — but representationalists argue they represent their own representational properties); moods and undirected emotions (a free-floating anxiety has phenomenal character without obvious content — but representationalists hold these represent diffuse environmental properties). Strong representationalism (phenomenal character is identical to representational content) is the contested thesis; weak representationalism (phenomenal character supervenes on representational content) is more widely accepted.',
    ARRAY['intentionalism_consciousness', 'tye_representationalism'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'phenomenal_intentionality',
    'Phenomenal Intentionality',
    ARRAY['mind'],
    'The view, defended by Terence Horgan and John Tienson (2002) and developed by David Pitt and others, that phenomenal character grounds intentionality rather than the reverse: original intentional content is constituted by, or fixed by, phenomenal character. Inverts the direction of explanation in standard naturalistic theories of content (which start with intentionality and try to derive phenomenal character via representationalism).',
    'The phenomenal-intentionality program is a contemporary alternative to standard naturalistic theories of content. The motivating contrast: standard theories (causal/teleosemantic) explain intentionality via external relations between mental states and the world, leaving phenomenal character as a separate problem; the phenomenal-intentionality view holds that the phenomenal character of conscious thought IS what makes it about what it is about. To think about a horse phenomenally — to have a horse-thought with horse-phenomenal character — is for the thought to be about a horse; the aboutness is constituted by the felt character. The view connects intentionality to consciousness in a way that the standard naturalistic accounts do not, and gives phenomenal consciousness an explanatory role beyond merely being a property of mental states. Standard objections: the view is hard to combine with thoroughgoing physicalism (if phenomenal character is special, the resulting theory of intentionality inherits that specialness); the empirical question of whether non-conscious mental states (subliminal processing, dispositional belief states) have intentionality remains hard for the view (Bourget, Mendelovici offer extensions). Pedagogically, phenomenal intentionality is the natural counterpart to representationalism about consciousness in the topology of contemporary positions: representationalism explains phenomenal character via intentional content; phenomenal intentionality explains intentional content via phenomenal character.',
    ARRAY['phenomenal_intentionality_program', 'horgan_tienson_phenomenal_intentionality'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'phenomenal_concept_strategy',
    'Phenomenal Concept Strategy',
    ARRAY['mind'],
    'The type-B materialist response to the knowledge and zombie arguments: the apparent gap between physical and phenomenal descriptions reflects a conceptual gap between physical concepts and phenomenal concepts (which pick out the same property under different modes of presentation), not a metaphysical gap. Defended by Brian Loar (1990), David Papineau (2002), Joseph Levin, Katalin Balog, and others. The leading sophisticated physicalist response to consciousness-based anti-physicalism arguments.',
    'The phenomenal-concept strategy is the most developed type-B materialist position in the contemporary literature. The structure: (1) phenomenal concepts and physical concepts are conceptually distinct (you can possess one without the other); (2) but they pick out the same properties (those properties are physical); (3) the apparent inexplicability of phenomenal facts in physical terms is the conceptual gap, not a metaphysical gap; (4) physicalism is true, the explanatory gap is real, and there is no contradiction. Mary on release gains a new phenomenal concept of a property she already knew under a physical concept; zombies are conceivable because the conceptual independence of phenomenal and physical concepts permits coherent imagination of physical-without-phenomenal scenarios, but conceivability does not entail metaphysical possibility. Standard objections: Chalmers''s (2007) challenge that any account of why phenomenal concepts are special enough to do the work the strategy requires must either presuppose the very phenomenal properties the strategy is trying to physicalize, or else be too thin to explain the apparent gap. Stoljar''s (2005) analysis of the various forms the strategy can take and the costs of each. Pedagogically, the phenomenal-concept strategy is the sophisticated middle-ground physicalist position students should learn alongside straightforward type-A materialism (Dennett-style eliminativism) and outright anti-physicalism (Chalmers-style property dualism).',
    ARRAY['phenomenal_concepts_strategy', 'loar_phenomenal_concepts', 'pcs_strategy'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'type_b_materialism',
    'Type-B Materialism',
    ARRAY['mind'],
    'The form of physicalism that accepts the conceptual / explanatory gap between physical and phenomenal descriptions but holds that the gap is conceptual, not metaphysical: phenomenal properties are physical properties (so physicalism is true), but they are conceived under a special phenomenal mode of presentation that conceptually outruns physical concepts. Distinguished from type-A materialism (Dennett, Frankish — which denies the gap is genuine) and type-C materialism (which holds the gap is real but tractable in principle).',
    'Chalmers (2003, 2007) introduces the type-A/type-B/type-C/type-D taxonomy of physicalist responses to the hard problem. Type-A materialists deny there is a genuine epistemic gap; phenomenal facts are functional/representational facts and a complete physical-functional story exhausts the phenomenal. Type-B materialists accept the gap but localize it conceptually: phenomenal concepts and physical concepts are independent, but their referents are physical. Type-C materialists hold the gap is real and unbridgeable in our current state but tractable in principle. Type-D dualists accept the gap as genuine and metaphysical. Type-B is the dominant moderate physicalist position, sustained by the phenomenal-concept strategy. Standard objections: Chalmers''s 2007 dilemma argues type-B materialism cannot succeed without either collapsing into type-A (making the gap explainable away) or admitting type-D (making the gap metaphysical). Defenders (Loar, Papineau, Stoljar) develop specific phenomenal-concept accounts that try to thread the needle. Pedagogically, type-B materialism is the position students should grasp as the sophisticated physicalist alternative to both Dennett-style dismissals and Chalmers-style anti-physicalism.',
    ARRAY['posteriori_physicalism', 'a_posteriori_materialism'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'illusionism',
    'Illusionism (about Consciousness)',
    ARRAY['mind'],
    'Keith Frankish''s (2016) contemporary version of qualia eliminativism: phenomenal consciousness is an introspective illusion. There is something it is like to introspect, but the felt phenomenal properties are how introspection misrepresents non-phenomenal physical states, not properties the states genuinely have. Distinguished from older eliminativisms (Dennett 1988) by its focus on the introspective mechanism that produces the illusion.',
    'Frankish''s illusionism is the most sustained contemporary defense of the position that phenomenal consciousness, as commonly conceived, does not exist. The view''s structure: (1) introspection delivers seemings of phenomenal properties (qualia, what-it-is-like character); (2) those seemings are produced by a representational mechanism in the brain that systematically misrepresents non-phenomenal physical states as phenomenal; (3) the phenomenal-seeming is real, but the phenomenal-content is illusory. The position differs from Dennett''s 1988 quining-qualia version by giving an explicit account of the introspective mechanism — a developmental and evolutionary story about why systems would have introspective architectures that produce phenomenal-seeming representations. Standard objections (Strawson, Goff, Chalmers): the view is self-undermining (the experience of arguing for illusionism is itself phenomenal; if phenomenal seemings are real and felt, illusionism has not eliminated them); the empirical adequacy question (no actual neural evidence for the proposed introspective-misrepresentation mechanism). Defenders (Frankish, Dennett, Pereboom): the seemings are real but they are not phenomenal in the philosophical-loaded sense; and the absence of direct neural evidence is hardly surprising given the difficulty of identifying neural correlates of any aspect of consciousness. Pedagogically, illusionism is the most theoretically refined eliminativist position; teach it as the most challenging-to-imagine alternative.',
    ARRAY['frankish_illusionism', 'illusionism_consciousness'],
    'INTERPRETED',
    'ai-seed',
    12
  ),
  (
    'multiple_drafts_model',
    'Multiple Drafts Model',
    ARRAY['mind'],
    'Daniel Dennett''s (1991) positive theory of consciousness: there is no single point in the brain or moment in time when conscious experience "happens"; instead, the brain runs many parallel drafts of representational processes, and what becomes conscious is a function of which drafts get globally promoted to influence behavior, memory, and report. Distinguished from the "Cartesian Theater" picture in which conscious experience is presented to a unified observer at a particular time and place.',
    'Dennett''s multiple drafts model is his constructive alternative to the Cartesian Theater: the picture, criticized by Dennett, of consciousness as a temporally and spatially localized presentation of contents to a unified subject. On the multiple drafts view, the brain processes information in many parallel streams, and what we report as our conscious experience is the result of a selection-and-promotion process that has no single locus. Crucially, the phenomenal content of consciousness is not fixed by some single moment of conscious experience but by which drafts win the selection process. The view connects to Dennett''s qualia eliminativism (1988) and his heterophenomenology methodology (1991). Pedagogically, the multiple drafts model is the canonical Dennettian alternative to standard pictures of consciousness; students who only know Dennett''s 1988 negative argument against qualia should learn the 1991 positive theory. The model has empirical content (predictions about the temporal structure of conscious report; the relationship between conscious experience and memory consolidation) and has been influential in cognitive science even among theorists who reject Dennett''s eliminativism. Pair with global workspace theory: both deny a Cartesian theater but multiple drafts emphasizes the temporal and processual nature of consciousness more than GWT does.',
    ARRAY['dennett_multiple_drafts', 'cartesian_theater_alternative'],
    'INTERPRETED',
    'ai-seed',
    12
  );

-- Edges: 35 INSERTs, all pedagogical_prerequisite. All within-domain
-- (source and target both tagged mind). Cross-domain edges (consciousness
-- ↔ epistemology on phenomenal vs propositional knowledge; phenomenology
-- ↔ epistemology and philosophy of language; panpsychism ↔ metaphysics on
-- fundamentality; IIT/GWT ↔ philosophy of science on cognitive science;
-- phenomenal concept strategy ↔ philosophy of language on concept
-- individuation) are P5-11''s exclusive surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Foundation spine: from P5-07a's mental_state into the new consciousness cluster
  ('mental_state', 'consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('consciousness', 'what_its_like', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('what_its_like', 'phenomenal_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('consciousness', 'access_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('phenomenal_consciousness', 'qualia', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Hard problem cluster
  ('phenomenal_consciousness', 'hard_problem_of_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('consciousness', 'easy_problems_of_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('easy_problems_of_consciousness', 'hard_problem_of_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('hard_problem_of_consciousness', 'explanatory_gap', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('hard_problem_of_consciousness', 'knowledge_argument', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('hard_problem_of_consciousness', 'philosophical_zombie', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Bridges from P5-07a's property_dualism to the supporting arguments
  ('property_dualism', 'knowledge_argument', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('property_dualism', 'philosophical_zombie', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Phenomenology adjacencies
  ('consciousness', 'phenomenology', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('phenomenal_consciousness', 'phenomenal_concept', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Phenomenal-concept strategy and type-B materialism
  ('phenomenal_concept', 'phenomenal_concept_strategy', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('knowledge_argument', 'phenomenal_concept_strategy', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('phenomenal_concept_strategy', 'type_b_materialism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('physicalism', 'type_b_materialism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('physicalism', 'easy_problems_of_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Positive theories of consciousness
  ('hard_problem_of_consciousness', 'panpsychism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('hard_problem_of_consciousness', 'integrated_information_theory', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('consciousness', 'global_workspace_theory', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('consciousness', 'higher_order_theory_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('higher_order_theory_consciousness', 'higher_order_thought_theory', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Representational accounts
  ('consciousness', 'representationalism_consciousness', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('representationalism_consciousness', 'phenomenal_intentionality', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Qualia disputes
  ('qualia', 'qualia_realism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('qualia', 'qualia_eliminativism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('qualia', 'qualia_functionalism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('qualia_eliminativism', 'illusionism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('qualia_eliminativism', 'multiple_drafts_model', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('qualia_functionalism', 'inverted_spectrum', 'pedagogical_prerequisite', 'ai-seed', 12),
  -- Cross-cluster within-mind bridges from P5-07a's functionalism
  ('functionalism', 'qualia_functionalism', 'pedagogical_prerequisite', 'ai-seed', 12),
  ('functionalism', 'inverted_spectrum', 'pedagogical_prerequisite', 'ai-seed', 12);

COMMIT;
