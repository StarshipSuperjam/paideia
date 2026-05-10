# Phase 5 production audit evidence — philosophy of mind

> Authored by S-0110 (routine session) per T-PHASE-5-AUDIT task AUDIT-MIN.
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: philosophy of mind
- Edge population: 70 (35 from `0040_seed_mind_part1.sql` covering the foundation spine + dualism / physicalism / mental causation / intentionality / perception / personal identity / computational mind clusters + 35 from `0046_seed_mind_part1.sql` covering consciousness / qualia / hard problem / phenomenology adjacencies / panpsychism / IIT / GWT / higher-order theories / qualia disputes)
- Edge sample size: 25; sample density: 25/70 = 35.7%
- Sample selection: deterministic md5(seed='AUDIT-MIN' || source_id || '|' || target_id) ordering
- Node sample size: 12; selection: edge-anchored union (34 unique nodes from 25 sampled edges) ordered by md5(seed='AUDIT-MIN' || node_id), take first 12
- Generation date: 2026-05-10

## Sampled-edge candidate findings

### Finding E-1
EDGE: consciousness [domain=mind] → representationalism_consciousness [domain=mind]
   edge_type = pedagogical_prerequisite, weight/confidence/evidence not surfaced (per master-plan §T2-E empty `evidence` field is graph-wide; not penalized in verdict)
SEP-ANCHORED REASONING: SEP entry on "Representational Theories of Consciousness" frames representationalism explicitly as a theory ABOUT consciousness — the thesis that the phenomenal character of conscious experience is exhausted by, or determined by, its representational content. The dialectical role of the position is intelligible only once consciousness is on the table as the explanandum. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-2
EDGE: qualia_eliminativism [domain=mind] → multiple_drafts_model [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Consciousness" treats Dennett's multiple drafts model (1991) as the constructive theory paired with his earlier qualia-eliminativist work (1988 "Quining Qualia"). The pedagogical order: motivate the eliminativist negative thesis first (qualia as commonly conceived do not exist), then introduce the positive theory of what consciousness is instead (parallel-streams selection, no Cartesian Theater). The migration's edge runs eliminativism → multiple_drafts_model in this conceptual-dependency direction, which matches the canonical Dennettian exposition order.
VERDICT: sound
CONFIDENCE: high

### Finding E-3
EDGE: mind [domain=mind] → personal_identity [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Personal Identity" frames the diachronic-identity question as one that presupposes some account of what persons are — and persons are characterized in turn by their mental lives (Locke's memory criterion, Parfit's psychological continuity, the animalist's biological-organism view all situate themselves in a debate that takes the mental as the relevant subject matter to discuss). Pedagogically you need the broader notion of mind first; personal identity is the diachronic-identity question for the bearers of mental lives.
VERDICT: sound
CONFIDENCE: high

### Finding E-4
EDGE: qualia [domain=mind] → qualia_realism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Qualia" introduces qualia as the explanandum (the felt qualitative character of conscious experience — the redness of red, the painfulness of pain), then maps the dialectical space of positions: realism (qualia exist as primitive properties), eliminativism (they don't exist), functionalism (they're functional roles), representationalism (they're representational contents). Qualia_realism is one position WITHIN the qualia debate; you need the qualia concept first.
VERDICT: sound
CONFIDENCE: high

### Finding E-5
EDGE: multiple_realizability [domain=mind] → functionalism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Functionalism" treats Putnam's (1967) multiple-realizability argument as the canonical motivation for functionalism: if mental types can be realized in different physical substrates (humans, octopuses, Martians, machines), they cannot be identical to any single physical type, so they must be individuated more abstractly — by functional role. The pedagogical sequence type-identity theory → multiple realizability → functionalism is the standard SEP exposition. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-6
EDGE: hard_problem_of_consciousness [domain=mind] → philosophical_zombie [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Zombies" frames Chalmers's zombie argument (1996) as one of the canonical anti-physicalist arguments arising from the hard-problem framing of consciousness. The argument's force depends on the prior recognition that phenomenal consciousness presents an explanatory difficulty for physicalism — the hard problem articulates the explanatory difficulty; the zombie argument leverages that difficulty into a metaphysical conclusion (physical-functional duplicates can lack phenomenal consciousness, so consciousness does not supervene). Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-7
EDGE: mental_state [domain=mind] → physicalism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Physicalism" frames the philosophy-of-mind question as: are mental states (or properties, or events) physical states (or properties, or events)? The thesis presupposes the explanandum (mental states) it seeks to physicalize. Pedagogically you need the concept of mental states first; physicalism is then the position that those mental states are nothing over and above physical states.
VERDICT: sound
CONFIDENCE: high

### Finding E-8
EDGE: mental_state [domain=mind] → mental_causation [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mental Causation" frames the puzzle as the question of how mental states cause physical events. The puzzle presupposes the concept of mental state as the alleged cause; pedagogically you need the basic concept first, then the puzzle of how things in this category make physical differences.
VERDICT: sound
CONFIDENCE: high

### Finding E-9
EDGE: knowledge_argument [domain=mind] → phenomenal_concept_strategy [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Knowledge Argument" and "Phenomenal Concepts" present the phenomenal-concept strategy (Loar 1990, Papineau 2002) explicitly as the type-B materialist response to Jackson's knowledge argument — the strategy denies Mary learns a new fact on release, while granting she gains a new concept (a phenomenal concept) of a fact she already knew under physical concepts. The strategy's intelligibility depends on having the knowledge argument as the target. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-10
EDGE: perception [domain=mind] → representationalism_perception [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "The Contents of Perception" / "The Problem of Perception" maps the contemporary dialectical space (direct realism vs representationalism vs sense-data theory) as positions WITHIN the philosophy of perception. Representationalism is one of the positions — the thesis that perceptual experience represents the world. You need perception as the topic first.
VERDICT: sound
CONFIDENCE: high

### Finding E-11
EDGE: mind [domain=mind] → mental_state [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries treat the mind as the collection of mental states a creature has — perceptions, beliefs, desires, sensations, emotions. Pedagogically the broad notion of mind comes first as the explanandum (the phenomena to be theorized); mental_state then names the basic explanatory unit — a particular belief, desire, perception, or sensation. The migration's prose explicitly frames it this way ("mental states ARE physical states" / "they are functional states" / "folk-psychological mental states do not exist" — these are theses about what mental states fundamentally are, asked once mind is on the table).
VERDICT: sound
CONFIDENCE: high

### Finding E-12
EDGE: supervenience_mental [domain=mind] → mental_causation [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mental Causation" presents supervenience as part of the apparatus non-reductive physicalists invoke to address the mental-causation puzzle, not as a precondition for grasping the puzzle itself. The basic puzzle (how does the immaterial / non-reducible mental push around the physical?) predates supervenience apparatus by centuries (Princess Elisabeth's 1643 challenge to Descartes); the modern Davidson-Kim supervenience-based formulation is one specific framing. The migration's edge running supervenience → mental_causation supports the Kim-style framing (where supervenience is the load-bearing premise of the exclusion argument that articulates the modern mental-causation puzzle in its sharpest form), but pedagogically the puzzle comes first and the supervenience apparatus comes as one of its tools — the canonical SEP exposition order is mental_causation as topic, then supervenience as tool. The graph already has mental_state → mental_causation (E-8) as the basic dependency; the supervenience_mental → mental_causation edge then says "to fully understand mental causation as Kim formulates it, you also need supervenience" — multi-prereq is fine for a complex topic, supportable on the Kim framing but not the canonical SEP pedagogical entry.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Tools-vs-topic ordering pattern — clusters with S-0105 E-2 (expertise → epistemic_dependence), S-0108 E-5 (motivational_internalism → expressivism), S-0109 E-3 (modality → essence_metaphysical) as instances of the broader frameworks-vs-foundations dialectical-ordering pattern, but with a distinct shape: here the apparatus (supervenience) is supplied as prereq for the topic (mental causation) — the inverse dependency direction from the four prior pattern-instances. Could read as REVERSED on a stronger interpretation; defensible-medium is the conservative call. Mutation-implying.

### Finding E-13
EDGE: personal_identity [domain=mind] → animalism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Personal Identity" presents animalism (Olson 1997, Snowdon 1990) as one of the main contemporary positions in the personal-identity dispute — the thesis that we are human animals and our identity over time is the identity of those animals. Animalism is intelligible only as a position WITHIN the personal-identity debate (the alternative to psychological-continuity theory). Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-14
EDGE: hard_problem_of_consciousness [domain=mind] → explanatory_gap [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Consciousness" treats Levine's (1983) explanatory gap as the precursor framing of Chalmers's (1995) hard problem: Levine argued physical descriptions of pain (e.g., C-fiber firing) leave an explanatory gap — even granting the identity, we don't see WHY pain feels the way it does — and Chalmers's hard-problem formulation builds on this. The conceptual / historical order runs explanatory_gap (1983) → hard_problem (1995); Levine's gap is the more general/prior concept, Chalmers's hard problem the more elaborated, specific successor. The migration's edge runs hard_problem → explanatory_gap, which inverts the canonical conceptual-dependency direction — the pedagogical order should be: introduce the explanatory gap (Levine's framing — physical explanation leaves something unexplained), then introduce the hard problem (Chalmers's elaboration — specifically about phenomenal consciousness, with the explicit easy/hard distinction). Direction reversed.
VERDICT: reversed
CONFIDENCE: medium
NOTES: Historical-conceptual ordering — the migration's prose for hard_problem_of_consciousness's neighbors does not clearly support this directionality (the easy_problems_of_consciousness → hard_problem_of_consciousness edge in the same migration runs the right way conceptually, suggesting this hard_problem → explanatory_gap edge may be a directionality slip). Mutation-implying for closeout: closeout could (a) flip the edge to explanatory_gap → hard_problem_of_consciousness, OR (b) keep both with hard_problem also as a prereq via a parallel-edge structure (the more elaborated framing motivates engagement with the precursor). Empirical-fortification candidate at closeout (parametric verdict here is medium-confidence + mutation-implying).

### Finding E-15
EDGE: consciousness [domain=mind] → what_its_like [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Consciousness" treats Nagel's (1974) "what it is like" formula as the canonical entry point to the phenomenal aspect of consciousness — a creature has conscious experience iff there is something it is like to be that creature. The formula picks out a specific feature OF consciousness; you need the broader concept of consciousness as the explanandum first. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-16
EDGE: physicalism [domain=mind] → type_identity_theory [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mind/Brain Identity Theory" treats type-identity theory (Place 1956, Smart 1959, Lewis 1966, Armstrong 1968) as the first systematic physicalist alternative to behaviorism — explicitly framed as a physicalist position with a particular reductive shape (mental types are brain types). Understanding type-identity theory as a position requires having physicalism (or at least the question physicalism asks: are mental states physical?) on the table first. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-17
EDGE: property_dualism [domain=mind] → knowledge_argument [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Knowledge Argument" and "Dualism" present Jackson's (1982) knowledge argument as one of the canonical arguments FOR property dualism, alongside Chalmers's zombie argument. The dialectical structure is: the argument is the evidence; property dualism is the position the argument supports. SEP introduces the knowledge argument independently of any prior commitment to property dualism — Mary's case is a free-standing thought experiment about color experience that invites a property-dualist conclusion, not a thought experiment whose intelligibility presupposes property dualism. The migration's edge running property_dualism → knowledge_argument inverts the canonical evidence-to-position direction: pedagogically the argument leads TO the position, not the other way around. The same migration also has hard_problem_of_consciousness → knowledge_argument in 0046 (not in this sample), which runs in the right direction (the hard-problem framing motivates engagement with the argument). The property_dualism → knowledge_argument edge is reversed — or at minimum unnecessary, since hard_problem already supplies the prereq context the student needs.
VERDICT: reversed
CONFIDENCE: medium
NOTES: Argument-vs-position ordering pattern — recurring across the philosophy-of-mind subdomain. The same migration also has property_dualism → philosophical_zombie (sampled separately would be the analogous edge for the zombie argument, also reversible on the same grounds). Both knowledge_argument and philosophical_zombie are arguments that motivate property_dualism, not derivatives of it. Mutation-implying for closeout: closeout could (a) flip both edges (knowledge_argument → property_dualism, philosophical_zombie → property_dualism), (b) drop both edges and rely on the hard_problem prereqs, or (c) keep but re-type as historical_influence or as a different relation kind. Distinct in kind from S-0109 E-3 and E-12 metaontological-commitment pattern (those were direction-sound edges that committed to a specific framework; this is a directionality issue). Empirical-fortification candidate at closeout.

### Finding E-18
EDGE: physicalism [domain=mind] → functionalism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Functionalism" treats functionalism as a physicalist theory of mind — mental states are individuated by functional role, but every mental token is realized by a physical token (token-physicalism). Understanding functionalism as a position in the mind-body debate requires having physicalism (or its question) on the table first. SEP's standard exposition runs physicalism (the umbrella) → its variants (type-identity, functionalism, behaviorism, eliminativism). Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-19
EDGE: mental_state [domain=mind] → dualism [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Dualism" frames mind-body dualism as the thesis that mental states (or properties, or substances) are metaphysically distinct from physical states. The thesis presupposes mental states as the relata to be distinguished from the physical. Pedagogically the basic concept of mental states comes first; dualism is then one position on what kind of thing those mental states are.
VERDICT: sound
CONFIDENCE: high

### Finding E-20
EDGE: qualia_functionalism [domain=mind] → inverted_spectrum [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Inverted Qualia" / "Qualia" frames the inverted-spectrum thought experiment (Locke's original; Block, Shoemaker contemporary) as a challenge specifically targeting functionalist accounts of qualia: two subjects with identical functional organizations could have inverted color experiences (one's red-experience matches the other's green-experience), so functional role does not exhaust phenomenal character. The argument's dialectical force depends on having qualia_functionalism as the target. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-21
EDGE: representational_theory_of_mind [domain=mind] → computational_theory_of_mind [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "The Computational Theory of Mind" treats RTM and CTM as a tightly coupled package in Fodor's language-of-thought tradition: RTM supplies the mental representations (symbol-like internal structures with semantic content) that CTM specifies are computed over. Pedagogically the standard exposition introduces the representations first (RTM — there are mental representations with semantic content) and then specifies that mental processes are computations over them (CTM — those processes are computational). Direction sound. Note: there is also a direct functionalism → computational_theory_of_mind edge (in the same migration, not in this sample) supplying CTM's other natural prereq.
VERDICT: sound
CONFIDENCE: high

### Finding E-22
EDGE: intentionality [domain=mind] → functional_role_semantics [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mental Representation" treats functional-role semantics (Block 1986, Harman 1987, Field) as one of the three main contemporary naturalistic theories of mental content — alongside causal/teleosemantic theories and representationalism. FRS is intelligible only as an answer to the intentionality question (what makes a mental state about what it is about?). Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-23
EDGE: consciousness [domain=mind] → phenomenology [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Phenomenology" presents phenomenology as the 20th-century philosophical movement initiated by Husserl and developed by Heidegger, Sartre, and Merleau-Ponty — a tradition with its own method (phenomenological reduction / epoché) that takes consciousness as primary subject matter. The relation consciousness → phenomenology is direction-defensible (engaging with phenomenology presupposes some grasp of consciousness as the topic the tradition theorizes), but the relation type is unusual for pedagogical_prerequisite: phenomenology is a TRADITION/METHODOLOGY that engages with consciousness, not a concept derived from it. The relation is plausibly historical_influence (per PREDICATE_MANIFEST.md reserved-but-unused row) or a methodological-tradition relation rather than pedagogical_prerequisite. Distinct in kind from the typical position-within-a-debate edges (e.g., consciousness → representationalism_consciousness in E-1 of this sample) where the target is a specific theoretical position; phenomenology is a school/movement.
VERDICT: defensible
CONFIDENCE: medium
NOTES: School/movement-as-target pattern. The granularity-mismatch surfaces at the node level (see N-2 phenomenology). Edge here is defensible but mistyped — likely better as historical_influence or as a methodological-tradition relation. Mutation-implying: closeout could (a) re-type to historical_influence (depends on the broader closeout decision about activating the reserved predicate), (b) drop the edge, or (c) keep but flag that phenomenology's school-name granularity makes the standard prereq relation awkward.

### Finding E-24
EDGE: hard_problem_of_consciousness [domain=mind] → integrated_information_theory [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Consciousness" / "Integrated Information Theory" presents IIT (Tononi 2004, 2008, 2012) as one of the positive scientific theories that aims to address the hard problem — by identifying consciousness with integrated information measured by Φ. Understanding IIT as a positive proposal requires having the hard problem (the explanatory difficulty IIT addresses) on the table first. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-25
EDGE: mental_state [domain=mind] → perception [domain=mind]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "The Problem of Perception" treats perceptual experience as a kind of mental state — perceptual states are the mental states by which an organism becomes aware of its surroundings. The basic explanatory category (mental state) is prerequisite to its specific subclass (perception). Direction sound.
VERDICT: sound
CONFIDENCE: high

## Sampled-node candidate findings

### Finding N-1
NODE: physicalism [domain=mind]
   summary = "The thesis that everything is physical: every concrete particular is a physical particular; every property either is a physical property or is grounded in physical properties; minds are not exceptions. The dominant metaphysical framework in contemporary analytic philosophy of mind. Differentiates into type-identity theory, functionalism, behaviorism, eliminativism, and non-reductive physicalism..."
SEP-ANCHORED REASONING: SEP entry on "Physicalism" treats physicalism as a thesis with multiple sub-variants (type-physicalism, token-physicalism, reductive vs non-reductive). At the granularity boundary: physicalism is an umbrella position that the migration's prose itself notes "differentiates into" five named sub-variants — borderline-similar to S-0109 N-3 a_theory_of_time (a position-family with a coherent shared core). However, "physicalism" is itself a SEP-recognized technical thesis with a coherent statable content (everything is physical), with named arguments for and against (Mary, zombies on one side; the success of physical science, supervenience-based responses on the other). Concept-level granularity is borderline-sound: physicalism names a single thesis that admits of variants, distinct in kind from N-2 phenomenology (a school/movement) and from S-0109 N-4 modality (a sub-discipline housing atomic concepts). Summary reads with concrete specificity (named variants, key objections, contemporary mainstream treatment).
VERDICT: sound
CONFIDENCE: medium
NOTES: Position-family-with-coherent-core pattern — same kind as S-0109 N-3 a_theory_of_time. Distinct from sub-discipline-label-with-content (S-0109 N-4 modality, N-6 mereology) and from school/movement (N-2 phenomenology in this sample). Closeout could revisit if the structural decision on N-2 phenomenology (school/movement granularity) extends to clarifying when family-name nodes are vs aren't appropriate.

### Finding N-2
NODE: phenomenology [domain=mind]
   summary = "The 20th-century philosophical movement initiated by Edmund Husserl that takes consciousness as its primary subject matter and proposes a method (phenomenological reduction or epoché) for studying conscious experience as it is given, bracketing questions of metaphysical reality. Major figures: Husserl, Heidegger, Sartre, Merleau-Ponty, Levinas..."
SEP-ANCHORED REASONING: SEP entry on "Phenomenology" treats phenomenology as a 20th-century philosophical MOVEMENT/TRADITION/METHODOLOGY initiated by Husserl, with named major figures (Husserl, Heidegger, Sartre, Merleau-Ponty, Levinas) and a distinctive method (phenomenological reduction / epoché). The summary itself frames it as "the 20th-century philosophical movement initiated by Edmund Husserl..." — explicitly a school/movement, not a single atomic concept. The per-node prompt template (per master-plan §"Per-node prompt template") explicitly flags school names as granularity-mismatch candidates: "If the label is a discipline name (e.g., 'Political Philosophy', 'Metaphysics', 'Ontology') or a school name (e.g., 'Vienna Circle', 'Scholasticism') or a thinker-framework name (e.g., 'Aristotelian Four Causes'), flag for granularity-mismatch review." Phenomenology is a school/movement name — falls squarely in the second clause (Vienna Circle, Scholasticism); in fact phenomenology is a closer parallel to those examples than the migration's other nodes. Distinct in kind from sub-discipline-label-with-content (S-0109 N-4 modality, N-6 mereology) — phenomenology is not a sub-discipline housing atomic concepts that the curriculum could split it into; it's a tradition with named adherents and a distinctive methodology.
VERDICT: granularity-mismatch
CONFIDENCE: high
NOTES: School/movement granularity pattern — first instance in the audit so far. Distinct from sub-discipline-label-with-content. Closeout could (a) demote to a non-pedagogical-prerequisite category-tag (historical-tradition annotation), (b) split into atomic phenomenology-tradition concepts (intentionality-Husserlian-style, lifeworld, embodied-cognition-Merleau-Ponty-style — though many of these would already overlap with existing nodes), or (c) retire the node. The per-node prompt template's explicit flagging of this pattern means the closeout has a clear contract here — phenomenology's case is unambiguous, in contrast to the borderline sub-discipline cases. Mutation-implying.

### Finding N-3
NODE: phenomenal_concept_strategy [domain=mind]
   summary = "The type-B materialist response to the knowledge and zombie arguments: the apparent gap between physical and phenomenal descriptions reflects a conceptual gap between physical concepts and phenomenal concepts (which pick out the same property under different modes of presentation), not a metaphysical gap. Defended by Brian Loar (1990), David Papineau (2002), Joseph Levin, Katalin Balog, and others..."
SEP-ANCHORED REASONING: SEP entries on "Type-B Materialism" / "Phenomenal Concepts" treat the phenomenal-concept strategy as a specific named technical maneuver in the type-B materialist literature — a coherent, atomic strategy with named originators (Loar 1990, Papineau 2002) and named opponents (Chalmers 2007). Concept-level granularity: an atomic mastery unit (a specific theoretical strategy with statable structure). Summary reads with concrete specificity (named originators, named structural moves, specific objections from Chalmers and Stoljar).
VERDICT: sound
CONFIDENCE: high

### Finding N-4
NODE: mental_causation [domain=mind]
   summary = "The puzzle of how mental states cause physical events. Mental events apparently cause physical events all the time (a thirst causes hand-to-glass movement; a decision causes leg-to-step). But if the physical world is causally closed... then either mental events do not really cause physical events (epiphenomenalism) or every action is causally overdetermined. Kim's causal-exclusion argument is the contemporary canonical formulation."
SEP-ANCHORED REASONING: SEP entry on "Mental Causation" treats mental causation as a single coherent puzzle/topic with a clear dialectical structure (three jointly-inconsistent premises: mental causation, physical closure, non-overdetermination) and named contemporary formulation (Kim's exclusion argument). At the granularity boundary: mental causation names BOTH the inquiry-topic and the relation it inquires about (mental-to-physical causation). Same class as S-0109 N-10 time and the broader pattern of basic-category labels (causation, existence) that name both the inquiry and its subject matter. Distinct from sub-discipline-label-with-content (where the label houses many separate atomic-concept children — modality houses possible_worlds, essence_metaphysical, modal_realism; mereology houses composition, simples, gunk). Mental causation has fewer atomic children in the graph (causal_exclusion_argument is the main one in this seed) and reads more as a single puzzle than as a sub-discipline. Concept-level granularity sound at the basic-category-label level. Summary reads with instructional voice (named puzzle structure, named canonical formulation, named contemporary literature).
VERDICT: sound
CONFIDENCE: medium
NOTES: Basic-category-label pattern — clusters with S-0109 N-10 time and the "causation"/"existence" treatment in metaphysics. Distinct from sub-discipline-label-with-content (S-0109 N-4 modality, N-6 mereology) and from school/movement (N-2 phenomenology in this sample).

### Finding N-5
NODE: mind [domain=mind]
   summary = "The collection of mental phenomena exhibited by a conscious creature: its perceptions, beliefs, desires, intentions, sensations, emotions, and reasonings. Whether the mind is identical to the brain, supervenient on it, an emergent feature of it, or a distinct substance is the central metaphysical question of the philosophy of mind."
SEP-ANCHORED REASONING: SEP entry on "Philosophy of Mind" treats "mind" as the umbrella concept of the entire subdomain — the collection of mental phenomena and the ontological category they constitute. The migration's prose itself (teaching_notes for the mind node) flags three uses students conflate: explanandum, metaphysical posit, folk-psychological notion — confirming that "mind" sits at a high abstraction level. At the granularity boundary: like physicalism (N-1 in this sample) and a_theory_of_time (S-0109 N-3), "mind" is the sub-domain's top-level umbrella node. The granularity question is whether the curriculum treats "mind" as a pedagogically meaningful single concept (in which case sound) or as too-broad to be a unit of mastery (in which case granularity-mismatch — students master perception, belief, intentionality, etc. as the actual units, with "mind" as just a tag). The migration's edge structure (philosophy_of_mind → mind → mental_state → various branches) treats mind as a meaningful node in the spine; the alternative would be to retire the node and have philosophy_of_mind → mental_state directly. Borderline-sound at the umbrella-node level.
VERDICT: sound
CONFIDENCE: medium
NOTES: Subdomain-umbrella-node pattern — distinct from the sub-discipline-label-with-content pattern (modality, mereology, moral_epistemology). Mind plays a structural role in the foundation spine (philosophy_of_mind → mind → mental_state) and the basic-category function (every mental state is a state OF a mind). Closeout could revisit if the structural decision on subdomain-umbrella nodes (philosophy_of_mind, mind both as nodes) calls for retiring or restructuring the umbrella layer.

### Finding N-6
NODE: knowledge_argument [domain=mind]
   summary = "Frank Jackson's (1982) thought-experimental argument against physicalism. Mary, a brilliant scientist, has lived her whole life in a black-and-white room studying color vision; she knows every physical fact about color perception. When released and shown red for the first time, she learns something new — what red looks like..."
SEP-ANCHORED REASONING: SEP entry on "Qualia: The Knowledge Argument" treats Jackson's 1982 argument as a specific named historical thought experiment with a clear dialectical structure (the four-step argument from Mary's pre-release knowledge to the falsity of physicalism) and named subsequent literature (Lewis-Nemirow ability hypothesis, Conee acquaintance hypothesis, Loar phenomenal-concept strategy, Dennett denial). Concept-level granularity: an atomic mastery unit (a specific named argument with statable structure). Summary reads with concrete specificity (Jackson 1982 citation, four-step argument structure, named responses, Jackson's later retraction).
VERDICT: sound
CONFIDENCE: high

### Finding N-7
NODE: qualia_realism [domain=mind]
   summary = "The view that qualia are real, irreducible, non-functional, intrinsic properties of conscious experience. Defenders (Block 1990, Chalmers 1996, Jackson 1982 pre-retraction) treat qualia as primitive features... Opposed by qualia eliminativism (Dennett, Frankish), qualia functionalism (Lewis, Lycan), and qualia representationalism (Tye, Dretske)."
SEP-ANCHORED REASONING: SEP entry on "Qualia" treats qualia_realism as a specific position in the qualia dispute — the realist alternative to eliminativist, functionalist, and representationalist treatments. Concept-level granularity: a single position in a clearly-mapped dialectical space (named defenders, named opposing positions). Summary reads with concrete specificity (named defenders, named opposing positions, characterization of the position's content).
VERDICT: sound
CONFIDENCE: high

### Finding N-8
NODE: computational_theory_of_mind [domain=mind]
   summary = "The thesis that the mind is a computational system — that mental processes are computations defined over mental representations, and the brain is the hardware that implements those computations. Putnam (1960s) introduced the analogy; Fodor (1975, 1987, 2008) developed it most extensively in the language-of-thought tradition..."
SEP-ANCHORED REASONING: SEP entry on "The Computational Theory of Mind" treats CTM as a specific thesis (mind is a computational system) with named originators (Putnam) and developers (Fodor, Newell-Simon). Concept-level granularity: a single position in the philosophy of mind / cognitive science literature. The migration's teaching_notes distinguish three claims often run together (hardware claim, process claim, functional claim) — a useful pedagogical refinement that doesn't compromise the atomic-concept status of CTM as the umbrella thesis combining the three. Summary reads with instructional voice (named originators, named contemporary alternatives, structural refinements).
VERDICT: sound
CONFIDENCE: high

### Finding N-9
NODE: what_its_like [domain=mind]
   summary = "Thomas Nagel's (1974) framing of the phenomenal aspect of conscious experience: a creature has conscious experience if there is something it is like, for that creature, to be that creature. Introduced in 'What Is It Like to Be a Bat?', the formula has become the canonical entry point for the phenomenal character of consciousness..."
SEP-ANCHORED REASONING: SEP entry on "Consciousness" treats Nagel's 1974 "what it is like" formula as a specific named pedagogical entry point to the phenomenal aspect of consciousness. The label is unusual (a phrase rather than a noun-phrase concept-name) but the concept it picks out is specific (Nagel's framing, with named subsequent uses by Block 1995 phenomenal/access distinction and Chalmers 1995 hard problem). Concept-level granularity: an atomic mastery unit, well-anchored to a specific text and framing. Summary reads with concrete specificity (Nagel 1974 paper title, framing structure, downstream uses).
VERDICT: sound
CONFIDENCE: medium
NOTES: Phrase-as-label pattern — the node ID `what_its_like` is unusual but the concept is specific. Borderline-sound; closeout could revisit naming conventions if the curriculum prefers noun-phrase IDs throughout (e.g., `nagel_phenomenal_character` or similar). Non-mutation-implying for content — naming-only.

### Finding N-10
NODE: philosophical_zombie [domain=mind]
   summary = "A hypothetical being physically and functionally identical to a normal human but lacking phenomenal consciousness — there is nothing it is like to be a zombie, even though it behaves exactly as a conscious person would. David Chalmers's (1996) zombie argument..."
SEP-ANCHORED REASONING: SEP entry on "Zombies" treats Chalmers's zombie argument as a specific named thought experiment with a clear dialectical structure (the conceivability-to-possibility-to-falsity-of-physicalism inference) and named opposing strategies (Dennett's conceivability denial, Yablo-Loar conceivability-without-possibility, Russellian-monist reframings). Concept-level granularity: an atomic mastery unit (a specific named hypothetical entity / argument). Summary reads with concrete specificity (Chalmers 1996 citation, four-step argument structure, named opposing strategies).
VERDICT: sound
CONFIDENCE: high

### Finding N-11
NODE: multiple_drafts_model [domain=mind]
   summary = "Daniel Dennett's (1991) positive theory of consciousness: there is no single point in the brain or moment in time when conscious experience 'happens'; instead, the brain runs many parallel drafts of representational processes, and what becomes conscious is a function of which drafts get globally promoted to influence behavior, memory, and report. Distinguished from the 'Cartesian Theater' picture..."
SEP-ANCHORED REASONING: SEP entry on "Consciousness" / "Daniel Dennett" treats the multiple drafts model as Dennett's specific 1991 positive theory of consciousness with named contrast (Cartesian Theater) and named relations to other theories (Global Workspace Theory). Concept-level granularity: an atomic mastery unit (a specific named theory with statable structure). Summary reads with concrete specificity (Dennett 1991 citation, contrast with Cartesian Theater, empirical content).
VERDICT: sound
CONFIDENCE: high

### Finding N-12
NODE: dualism [domain=mind]
   summary = "The thesis that mind and body are metaphysically distinct: the mental and the physical are not one and the same kind of thing. Substance dualism (Descartes) holds they are distinct substances; property dualism (Chalmers, Jackson) holds the substance is physical but bears non-physical mental properties..."
SEP-ANCHORED REASONING: SEP entry on "Dualism" treats mind-body dualism as a position-family with a coherent shared core (mental and physical are metaphysically distinct) and named sub-variants (substance dualism, property dualism). The migration's summary itself frames it as encompassing two sub-variants. At the granularity boundary: like physicalism (N-1 in this sample) and a_theory_of_time (S-0109 N-3), "dualism" is a position-family-name with a coherent shared core. Concept-level granularity is borderline-sound at the family-name level; the shared core (mental-physical distinctness) is statable, and the family-name is itself a SEP-recognized technical construct. The migration's edge structure (mental_state → dualism → substance_dualism + property_dualism) treats dualism as a meaningful node housing the sub-variants.
VERDICT: sound
CONFIDENCE: medium
NOTES: Position-family-with-coherent-core pattern — same kind as N-1 physicalism in this sample and S-0109 N-3 a_theory_of_time. Distinct from sub-discipline-label-with-content (S-0109 N-4 modality, N-6 mereology) and from school/movement (N-2 phenomenology in this sample). Closeout could revisit if the structural decision on family-name nodes (physicalism, dualism, a_theory_of_time) calls for any uniform treatment.

## Cross-cutting observations

Four load-bearing aggregate patterns surfaced for the closeout's synthesis surface:

1. **School/movement granularity pattern surfaces (N-2 phenomenology).** First instance in the audit so far of the per-node prompt template's school-name flag (the template explicitly names "Vienna Circle, Scholasticism" as examples; phenomenology is a closer parallel to those than any node previously surfaced). Distinct in kind from the sub-discipline-label-with-content pattern (S-0105 N-8 bayesian_epistemology; S-0108 N-4 moral_epistemology, N-9 animal_ethics; S-0109 N-4 modality, N-6 mereology). The per-node prompt template's explicit flagging means the closeout has a clear contract for phenomenology — disposition is mutation-implying but the kind of mutation (split, retire, demote-to-tag, re-type to historical_influence) is closeout-judgment. Worth closeout cross-check for other school/movement nodes elsewhere in the graph: candidate-instances NOT in this sample but worth checking include `vienna_circle_logical_positivism` (logic / epistemology — appears in the wider node list), `scholasticism` (metaphysics — appears in the wider node list), `aristotelian_four_causes` (metaphysics — appears in the wider node list), `greek_atomism` (metaphysics).

2. **Argument-vs-position directionality pattern surfaces (E-17 property_dualism → knowledge_argument; E-14 hard_problem_of_consciousness → explanatory_gap).** Two edges in this sample run from a position to its supporting argument or precursor framing, where the canonical SEP exposition runs argument/precursor → position. E-17 inverts the standard knowledge-argument-supports-property-dualism direction; E-14 inverts the standard explanatory-gap-precedes-hard-problem direction. The same migration also has property_dualism → philosophical_zombie (not in this sample) which is the analogous instance for the zombie argument. First subdomain audit to surface this pattern in two distinct edges in the same sample — suggests the philosophy-of-mind seed may have a systematic directionality issue around argument-supports-position vs position-supplies-context-for-argument. Closeout aggregate scan across the full mind subdomain (and possibly the graph) could surface a systematic cleanup pass; both medium-confidence + mutation-implying and so qualify as empirical-fortification candidates at closeout.

3. **Tools-vs-topic ordering pattern (E-12 supervenience_mental → mental_causation).** Distinct in shape from the prior frameworks-vs-foundations dialectical-ordering pattern (S-0105 E-2 expertise → epistemic_dependence; S-0108 E-5 motivational_internalism → expressivism; S-0109 E-3 modality → essence_metaphysical) — those four prior pattern-instances run from a sub-position back to a more general topic; this E-12 instance runs from an apparatus (supervenience) to the topic it addresses (mental causation). The shape is the inverse: tool supplied as prereq for topic. Could be re-grouped as a single broader pattern (any apparatus/sub-position → topic-it-addresses ordering) at closeout aggregation, OR kept as distinct shapes within a "directionality" cluster.

4. **Position-family-name pattern surfaces in two distinct nodes in the same sample (N-1 physicalism, N-12 dualism).** Both name position-families with coherent shared cores (everything-is-physical / mental-and-physical-are-metaphysically-distinct) and named sub-variants in the graph as separate nodes (type_identity_theory, functionalism, behaviorism_logical, eliminative_materialism / substance_dualism, property_dualism). Same class as S-0109 N-3 a_theory_of_time. Distinct from sub-discipline-label-with-content (S-0109 N-4 modality, N-6 mereology) — those housed many atomic concepts at sub-discipline granularity; these house specific positions at family-name granularity. Closeout could revisit if a structural decision on family-name nodes (physicalism, dualism, a_theory_of_time) — to keep them as meaningful umbrella nodes with explicit family-name status, or to retire in favor of direct edges to the sub-variants — applies uniformly.

Empty `evidence` field uniform null across all 70 within-mind edges (master-plan §T2-E pre-listed; confirmed graph-wide again — fifth session in a row).

No new gate-feasible audit-system-input class surfaced — the four pre-listed master-plan proposals plus S-0104's cross_bridge_pedagogical_direction_inconsistent_with_summary candidate were not extended (within-mind data did not corroborate the cross-bridge-specific pattern). The argument-vs-position directionality pattern (observation #2) is on track to qualify as a new gate-feasible class via aggregate scan at closeout — could be operationalized as a validator soft-warn that flags pedagogical_prerequisite edges from a node tagged as a "position" to a node tagged as an "argument" (the schema would need position/argument sub-class tagging, parallel to the proposed history-terminator sub-class tagging in master-plan proposal #4).

Mid-sample expansion trigger (master-plan §"Sample-size policy": >60% defect rate at half-sample → expand to 50%): half-sample (E-1 through E-12) defect rate = 1/12 = 8.3% (E-12 defensible; E-14 reversed and E-17 reversed both fall in the second half); well below the 60% trigger. Standard 35% density held.

## SEP citations consulted

- SEP entry: "Consciousness"
- SEP entry: "Representational Theories of Consciousness"
- SEP entry: "Personal Identity"
- SEP entry: "Qualia"
- SEP entry: "Qualia: The Knowledge Argument"
- SEP entry: "Inverted Qualia"
- SEP entry: "Functionalism"
- SEP entry: "Mind/Brain Identity Theory"
- SEP entry: "Physicalism"
- SEP entry: "Type-B Materialism"
- SEP entry: "Phenomenal Concepts"
- SEP entry: "Mental Causation"
- SEP entry: "Dualism"
- SEP entry: "Zombies"
- SEP entry: "The Computational Theory of Mind"
- SEP entry: "Mental Representation"
- SEP entry: "The Problem of Perception"
- SEP entry: "The Contents of Perception"
- SEP entry: "Phenomenology"
- SEP entry: "Integrated Information Theory of Consciousness"
- SEP entry: "Daniel Dennett"
- SEP entry: "Philosophy of Mind"
