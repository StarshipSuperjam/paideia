# Seed-graph QA census evidence — shard 10

> Authored by S-0172 (routine session) per T-SEED-QA task SQA-10.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 10
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — paraconsistent_logic → dialetheism
EDGE: Paraconsistent Logic [paraconsistent_logic, logic] → Dialetheism [dialetheism, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Paraconsistent logic is the formal framework that allows for true contradictions without explosion (LP and variants); dialetheism is the metaphysical thesis (Priest) that some contradictions are true. Priest's dialetheism explicitly uses the paraconsistent framework — the formal apparatus is the pedagogical prereq for the philosophical position.
AUDIT-TOUCHED: none

### E-2 — morality → metaethics
EDGE: Morality [morality, ethics] → Metaethics [metaethics, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Metaethics is reasoning about morality (the nature of moral facts, moral language, moral knowledge). Morality is the first-order phenomenon; metaethics is the second-order inquiry. Standard direction.
AUDIT-TOUCHED: none

### E-3 — predicate_logic → russell_paradox
EDGE: Predicate Logic [predicate_logic, logic] → Russell's Paradox [russell_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Russell's paradox is set-theoretic (the set of all sets not containing themselves), but its formal statement uses predicate-logic comprehension/quantification — "{x : x ∉ x}". Predicate logic is the formal-language prereq for stating and analyzing the paradox.
AUDIT-TOUCHED: none

### E-4 — possible_worlds → ersatz_modal_realism
EDGE: Possible Worlds [possible_worlds, metaphysics] → Ersatz Modal Realism [ersatz_modal_realism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Ersatz modal realism is a specific ontological stance on what possible worlds are (linguistic/set-theoretic surrogates, contra Lewis's concrete worlds). The possible-worlds framework is the pedagogical prereq.
AUDIT-TOUCHED: none

### E-5 — externalism_epistemic → reliabilism
EDGE: Epistemic Externalism [externalism_epistemic, epistemology] → Reliabilism [reliabilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reliabilism is the paradigm species of epistemic externalism — justification depends on external facts about process reliability, not on factors accessible to the subject. Genus → species direction.
AUDIT-TOUCHED: none

### E-6 — distributive_justice → socialism
EDGE: Distributive Justice [distributive_justice, political] → Socialism [socialism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Socialism is grounded in claims about distributive justice (typically that capitalist distributions are unjust). Distributive justice is theory-neutral about the right pattern; socialism is one specific position. The general framework is the prereq for the specific position.
AUDIT-TOUCHED: none

### E-7 — existence → abstract_object
EDGE: Existence [existence, metaphysics] → Abstract Object [abstract_object, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Abstract objects (numbers, propositions, universals) are a contested category within existence. The general concept of existence is the prereq for asking whether abstract objects exist.
AUDIT-TOUCHED: none

### E-8 — truth_conditional_semantics → character_and_content
EDGE: Truth-Conditional Semantics [truth_conditional_semantics, language] → Character and Content (Two-Dimensional Semantics) [character_and_content, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kaplan's character/content distinction is a refinement of truth-conditional semantics for indexicals and demonstratives (character is the rule from context to content; content is the proposition expressed). The base framework is the prereq for the refinement.
AUDIT-TOUCHED: none

### E-9 — proper_name → causal_theory_of_reference
EDGE: Proper Name [proper_name, language] → Causal Theory of Reference [causal_theory_of_reference, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kripke's causal theory is a theory of how proper names refer. The concept of proper name is the topical prereq for the theory of reference.
AUDIT-TOUCHED: none

### E-10 — validity_logical → classical_logic
EDGE: Validity (Logical) [validity_logical, service] → Classical Logic [classical_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Validity (informal: conclusion follows necessarily from premises) is the general logical concept; classical logic is one specific formal system that operationalizes validity via its consequence relation. Informal validity precedes formalization pedagogically. The classification of the source as a "service" domain (cross-domain logical scaffolding) supports the umbrella reading.
AUDIT-TOUCHED: none

### E-11 — bivalence_principle → counterexample
EDGE: Principle of Bivalence [bivalence_principle, service] → Counterexample [counterexample, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Counterexample (a single instance refuting a universal claim) is a general logical/argumentative concept; bivalence (every proposition is either true or false) is a structural assumption. Pedagogically, students encounter counterexamples in everyday argument before encountering bivalence. The defensible reading is structural: a counterexample's "definitively false" status in classical logic IS underwritten by bivalence (in many-valued logics, the notion is murkier). The link is foundational rather than pedagogical-canonical. Not a defect, but a non-canonical framing — recurring "structural-vs-pedagogical" shape worth flagging for closeout.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-12 — free_will → principle_of_alternative_possibilities
EDGE: Free Will [free_will, metaphysics] → Principle of Alternative Possibilities [principle_of_alternative_possibilities, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: PAP ("could have done otherwise" as a condition for moral responsibility) is one specific thesis within the free-will debate. Free will is the broader topic; PAP is a substantive claim within it (defended by libertarians, contested by Frankfurt-cases).
AUDIT-TOUCHED: none

### E-13 — mental_state → consciousness
EDGE: Mental State [mental_state, mind] → Consciousness [consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mental states include both conscious and non-conscious states (e.g., sub-personal mental representations). Consciousness is the specific feature/kind that some mental states have. Genus → species pedagogical direction.
AUDIT-TOUCHED: none

### E-14 — consciousness → easy_problems_of_consciousness
EDGE: Consciousness [consciousness, mind] → Easy Problems of Consciousness [easy_problems_of_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Easy problems are defined relative to consciousness (Chalmers's easy-vs-hard carve-up: easy problems are functional-mechanistic aspects of conscious processes). The concept consciousness is the prereq for the easy/hard distinction.
AUDIT-TOUCHED: none

### E-15 — existence → causation
EDGE: Existence [existence, metaphysics] → Causation [causation, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Causation as a metaphysical relation between events (or facts, or objects) presupposes the existence of its relata. Existence is the foundational metaphysical concept; causation is one of metaphysics' subtopics. The connection is weakly pedagogical (students learn causation through concrete cause-effect examples, not through existence first), but existence-as-foundational reading is sound.
AUDIT-TOUCHED: none

### E-16 — soundness_logical → formal_epistemology
EDGE: Soundness (Logical) [soundness_logical, service] → Formal Epistemology [formal_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Formal epistemology uses logical soundness (an argument is sound iff valid and premises are true) and related logical concepts as part of its formal apparatus. Service-domain logical scaffolding feeds into formal-epistemological work.
AUDIT-TOUCHED: none

### E-17 — ontology → existence
EDGE: Ontology [ontology, metaphysics] → Existence [existence, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The recurring "target is the more general/foundational concept" shape. Ontology IS the systematic study of existence/being; existence is the topic, not a prereq, of ontology. Standard pedagogical direction is existence (intuitive, everyday) → ontology (formal study of existence). However, a concrete-entry-point reading supports the current direction: students often encounter ontology through specific debates (Platonism about numbers, nominalism about universals, modal ontology) as the natural entry into thinking about existence philosophically — that is, ontology functions as the concrete pedagogical doorway to the abstract concept of existence. Held at Defensible per the established calibration (concrete-entry-point reading supports the direction). Recurring shape across shards 05–10; rubric-calibration question for closeout.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — biocentrism → deep_ecology
EDGE: Biocentrism [biocentrism, ethics] → Deep Ecology [deep_ecology, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: Biocentrism (all life has intrinsic value) is the foundational ethical position; deep ecology (Naess 1973) is a specific normative framework that presupposes biocentric value claims and adds the platform of social-ecological reorganization. Foundational position → derivative framework. The 0.85 confidence/weight signals authoring acknowledgment that biocentrism and deep ecology are intertwined.
AUDIT-TOUCHED: none

### E-19 — renaissance_mechanism → vienna_circle_logical_positivism
EDGE: Renaissance and Early-Modern Mechanism [renaissance_mechanism, service] → Vienna Circle and Logical Positivism [vienna_circle_logical_positivism, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Long historical jump (16th–17th century Renaissance/early-modern mechanism → 1920s–30s logical positivism), spanning Enlightenment empiricism, 19th-century positivism (Comte, Mach), and Russell's logical analysis. The 0061 audit retyped renaissance_mechanism's other outbound edges (→ scientific_theory, → scientific_method) to historical_influence but explicitly KEPT this edge as pedagogical_prerequisite — the audit's keep-decision endorses the genealogical-line reading (mechanistic-science → logical-positivist science is a recognized pedagogical succession in philosophy-of-science teaching, distinct from the more diffuse historical influence of mechanism on individual scientific concepts). The audit-validation reading carries weight; the long-distance shape would otherwise suggest Weak-redundant.
AUDIT-TOUCHED: 0061 retyping list (touched the SOURCE node's other outbound edges and the TARGET node's other outbound edges, but did NOT retype this specific pair — explicit keep-decision)

### E-20 — a_theory_of_time → growing_block_theory
EDGE: A-Theory of Time [a_theory_of_time, metaphysics] → Growing Block Theory [growing_block_theory, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: A-theory holds that temporal becoming is objective (past/present/future distinction is mind-independent). Growing block (Broad, Tooley) is one specific A-theory: past and present exist, future does not. The general framework is the prereq for the specific variant.
AUDIT-TOUCHED: none

### E-21 — belief → propositional_knowledge
EDGE: Belief [belief, epistemology] → Propositional Knowledge [propositional_knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional knowledge (S knows that p) is canonically analyzed as belief + truth + justification (JTB) plus a Gettier-corrective condition. Belief is the B in JTB — a structural component prereq.
AUDIT-TOUCHED: none

### E-22 — reductionism_in_science → multiple_realizability_in_science
EDGE: Reductionism (in Science) [reductionism_in_science, science] → Multiple Realizability (Anti-Reductionist Argument) [multiple_realizability_in_science, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Multiple realizability is the canonical anti-reductionist argument (Putnam, Fodor). The argument presupposes reductionism (the target being argued against) — you have to understand reductionism to grasp what MR refutes. Same shape as shard 07's E-13 physicalism → reductionism_in_science (audit-validated).
AUDIT-TOUCHED: none

### E-23 — causation → causal_powers
EDGE: Causation [causation, metaphysics] → Causal Powers [causal_powers, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Causal powers (the dispositionalist/powers-ontology account of causation, per Harré-Madden, Mumford, Bird) is one specific metaphysical view about what causation IS. Causation is the broader topic that powers-theorists analyze. General topic → specific theory.
AUDIT-TOUCHED: none

### E-24 — paradigm → research_programme
EDGE: Paradigm (Kuhnian) [paradigm, science] → Research Programme (Lakatos) [research_programme, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Lakatos explicitly developed the research-programme concept as a successor/refinement of Kuhn's paradigm (with the hard-core/protective-belt distinction addressing perceived weaknesses in paradigm-incommensurability). Pedagogically the standard sequence is Kuhn-then-Lakatos.
AUDIT-TOUCHED: none

### E-25 — possible_worlds → counterpart_theory
EDGE: Possible Worlds [possible_worlds, metaphysics] → Counterpart Theory [counterpart_theory, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Counterpart theory (Lewis) is a specific stance on trans-world identity within the possible-worlds framework — individuals at other worlds are counterparts rather than identical to actual-world individuals. The framework is the prereq for the trans-world-identity stance.
AUDIT-TOUCHED: none

### E-26 — pyrrhonian_skepticism → problem_of_induction
EDGE: Pyrrhonian Skepticism [pyrrhonian_skepticism, epistemology] → Problem of Induction [problem_of_induction, epistemology]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: The correction: Pyrrhonian tradition (Pyrrho, Sextus Empiricus) is millennia-older than Hume's problem; the Agrippan trilemma does not depend on induction-skepticism. Direction should be pyrrhonian_skepticism > problem_of_induction."
VERDICT: Sound
RATIONALE: Audit-validated direction (per 0062 direction-flip). Pyrrhonian skepticism (Pyrrho, Sextus Empiricus, ancient) raised broad skeptical doubts including the Agrippan trilemma (regress / circularity / dogmatism). Hume's problem of induction (18th century) is a specific application of that broader skeptical framework to inductive inference. Pyrrhonian → induction is genus → species pedagogically; the audit's direction-flip explicitly settled this.
AUDIT-TOUCHED: migration 0062 — direction-flipped from `problem_of_induction → pyrrhonian_skepticism` per S-0122 audit; current direction is audit-validated and scored Sound on that direction.

### E-27 — applied_ethics → just_war_theory
EDGE: Applied Ethics [applied_ethics, ethics] → Just War Theory [just_war_theory, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: Just war theory (jus ad bellum + jus in bello) is one specific applied-ethics domain alongside biomedical ethics, business ethics, environmental ethics, etc. Applied ethics is the umbrella framework. The 0.85 confidence/weight signals authoring acknowledgment that just war theory has its own historical/theological depth somewhat independent of applied-ethics-as-discipline framing.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — turing_test
NODE: Turing Test [turing_test, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three-question distinction (sufficient / necessary / useful condition for intelligence) with concrete responses (Searle's Chinese Room; Block, French on necessity; descendant AI benchmarks). Pedagogical traction is strong.
C3 (summary cold-readability): yes — first sentence states Turing's 1950 operational benchmark plainly; the test mechanism is fully described; "operational benchmark" and "empirically tractable criterion" are accessible plain-language phrases.

### N-2 — liar_paradox
NODE: Liar Paradox [liar_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strengthened-liar teaching strategy, Tarski-Kripke-Priest-Field response-spectrum walk-through, the (T-schema + self-reference + classical-logic)-trilemma framing.
C3 (summary cold-readability): yes — first sentence's "this sentence is false" example is intuitively graspable; "bivalence" appears but the paradox-structure (true iff false) is the conceptual load and is independent of the bivalence vocabulary. The diagonal-lemma reference in the third sentence is formal-foundations detail, not load-bearing for grasping the paradox.

### N-3 — fuzzy_logic
NODE: Fuzzy Logic [fuzzy_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — sorites-paradox dissolution walk-through, list of difficulties (higher-order vagueness, ad hoc continuum choice, classical theorem failure), Smith's defense.
C3 (summary cold-readability): yes — first sentence's "continuous degrees, typically the real interval [0, 1]" is the conceptual core and is graspable; "t-norm"/"t-conorm" appear in sentence 2 as undefined formal apparatus, but sentence 4 ("Sentences about borderline cases get intermediate truth values matching the degree to which the predicate applies") supplies the conceptual gloss for what the formalism does. Borderline — strict reading would FAIL on t-norm jargon; charitable reading PASSES on the conceptual gloss across the summary. Flagged for closeout consistency review.

### N-4 — tarskis_t_schema
NODE: Tarski's T-Schema [tarskis_t_schema, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — pre-Tarski → Tarski's recursive definition → Davidson's natural-language application walk-through; "appearance vs underlying machinery" framing.
C3 (summary cold-readability): yes — first sentence's "T(S) iff p, where T is the truth predicate, S is a name (or structural description) of a sentence, and p is a translation of S into the metalanguage" gives all variable names inline; second sentence's "snow is white" example is the canonical accessible illustration. "Metalanguage" is mildly jargon-gated but is contextually graspable as "the language used to talk about S."

### N-5 — mental_causation
NODE: Mental Causation [mental_causation, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three-premise (mental causation / physical closure / non-overdetermination) framing, type-identity vs non-reductive vs property-dualism response-mapping, Davidson/Kim/realization-literature references.
C3 (summary cold-readability): yes — direct opening question; concrete examples (thirst → hand-to-glass; decision → leg-to-step); "causally closed" glossed inline as "every physical event has a sufficient physical cause"; "epiphenomenalism" and "overdetermined" are introduced as labels for the disjunctive alternatives.

### N-6 — formalism_artistic
NODE: Formalism (Artistic) [formalism_artistic, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strengths-and-weaknesses analysis with concrete examples (Duchamp's readymades for the weakness, Bell's "significant form" circularity diagnosis).
C3 (summary cold-readability): yes — first sentence gives concrete examples for both visual art ("lines, colors, shapes, masses") and music ("pitches, durations, dynamics, rhythms"); historical anchors (Bell 1914, Fry, Post-Impressionism) are named with enough context to orient a cold reader.

### N-7 — numerical_identity
NODE: Numerical Identity [numerical_identity, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete contrast (identical twins are qualitatively similar but numerically distinct; you-now and you-yesterday are numerically identical despite qualitative differences); Leibniz's-law structural exposition. Brief but operationally useful.
C3 (summary cold-readability): yes — first sentence defines numerical identity directly ("a is numerically identical to b iff a and b are one and the same entity"); qualitative identity glossed inline ("sharing all properties"); Leibniz's law given in both halves with the indiscernibles half flagged as contested.

### N-8 — basic_belief
NODE: Basic Belief [basic_belief, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names the canonical challenge (Sellars's myth-of-the-given) and the standard response (modest foundationalism with defeasible prima facie justification). Brief but pedagogically useful.
C3 (summary cold-readability): yes — first sentence defines basic belief directly via the contrast with inferential support; concrete candidates given ("perceptual beliefs about one's immediate experience and self-evident logical or mathematical truths"). "Foundationalist theories" appears but the structural role (the foundational layer) is the conceptual load and is self-explanatory.

### N-9 — narrow_content
NODE: Narrow Content [narrow_content, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the appeal-and-difficulty pedagogical structure: psychological-explanation motivation, Fodor-Loar program, the specification difficulty, externalist replies, contemporary disposition.
C3 (summary cold-readability): yes — first sentence's "depends only on the intrinsic properties of the thinker or speaker" is the conceptual core; second sentence's Putnam's Twin Earth (Earth-Oscar means H2O; Twin-Oscar means XYZ) is the canonical accessible illustration. "Internalist counterpoint to externalist wide content" appears but is operationally glossed by the Twin Earth example that follows.

### N-10 — supervaluationism
NODE: Supervaluationism [supervaluationism, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete bald-example walk-through; the penumbral-connections payoff (Tom-and-Tim case); list of difficulties (classical conditional proof, higher-order vagueness, admissible-sharpening vagueness).
C3 (summary cold-readability): yes — "sharpenings" appears in scare quotes immediately followed by inline gloss ("precise extensions for each vague predicate consistent with clear cases"); super-true / super-false defined inline. The technical apparatus is built up as introduced.

### N-11 — equality_political
NODE: Equality (Political) [equality_political, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — multi-dimensional pedagogical structure (foundational equal-moral-worth; formal/opportunity/outcome/relational dimensions); leveling-down objection; Rawls / Dworkin / Anderson / capability-approach references; equality-vs-liberty framing-critique.
C3 (summary cold-readability): yes — first sentence introduces the topic plainly; each dimension is glossed inline (formal, opportunity, outcome, relational, equal-moral-worth).

### N-12 — generality_problem
NODE: Generality Problem [generality_problem, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names the structural difficulty (no principled non-circular process-type specification), surveys responses (statistical, dispositional, etiological), notes the no-consensus state.
C3 (summary cold-readability): yes — borderline. First sentence references "reliabilism" without inline gloss (a cold reader does not necessarily know what reliabilism is); however, second sentence supplies the concrete structural problem with vivid examples ("vision-in-good-light, vision-in-good-light-on-Tuesday, vision-by-this-particular-perceiver") so the generality problem itself is grasped from the examples. Strict-reading FAIL (undefined load-bearing term); charitable-reading PASS (the conceptual problem is independently illustrated). Flagged for closeout consistency review alongside N-3.

### N-13 — hypothetico_deductivism
NODE: Hypothetico-Deductive Method [hypothetico_deductivism, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong pedagogical structure: H-D schema setup, three technical objections (tacking paradox, Goodman's new-riddle, strength problem), Bayesian alternative framing.
C3 (summary cold-readability): yes — first sentence ("scientific hypotheses are confirmed by deducing observational predictions from them and finding the predictions to hold") is the conceptual core and is fully accessible cold. Subsequent technical-objection mentions are not load-bearing for grasping the concept.

### N-14 — multiple_realizability
NODE: Multiple Realizability [multiple_realizability, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — argument-structure walk-through (four-step inference from MR to functionalism), challenges (Bechtel-Mundale on pain heterogeneity; Polger on empirical support), connection to philosophy of science.
C3 (summary cold-readability): yes — first sentence's "the same mental state can be realized in many distinct physical substrates" carries the load with concrete examples ("pain can be C-fiber firing in humans, some other neural pattern in octopuses, possibly some silicon configuration in artificial systems"). Functionalism is named but the inference structure is glossed in the second half of the summary.

### N-15 — behaviorism_logical
NODE: Logical Behaviorism [behaviorism_logical, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — anti-Cartesian motivation, the multiplication-of-qualifications objection (holistic structure of mental states), connection to functionalism's spirit-without-letter inheritance.
C3 (summary cold-readability): yes — first sentence defines logical behaviorism via translation-into-behavior; concrete example ("Smith believes it is raining" → behavioral dispositions about umbrellas); the contrast with psychological/methodological behaviorism (Watson, Skinner) is explicitly drawn.

### N-16 — linguistic_relativity
NODE: Linguistic Relativity (Sapir-Whorf Hypothesis) [linguistic_relativity, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong/weak-claim distinction, evidence-against-strong (universal cognitive abilities; bilingual reframing), evidence-for-weak (Boroditsky on Russian color; Pederson on spatial frames), interface with philosophy of mind and philosophy of science.
C3 (summary cold-readability): yes — first sentence states the thesis plainly ("the structure of a language influences the cognition or worldview of its speakers"); strong/weak forms are explicitly differentiated inline ("strong form (language determines thought) and weak form (language influences thought)"); Sapir/Whorf dates and the contemporary empirical landscape are named.

### N-17 — philosophical_zombie
NODE: Philosophical Zombie [philosophical_zombie, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — argument-structure walk-through (four-step from conceivability to anti-physicalism), the standard responses (Dennett denies conceivability; Yablo/Loar/Papineau deny conceivability-to-possibility; Russellian-monism reframings); pairing with the knowledge argument as the two-canonical anti-physicalist arguments.
C3 (summary cold-readability): yes — first sentence defines zombies via the "physically and functionally identical to a normal human but lacking phenomenal consciousness" specification; "phenomenal consciousness" is glossed inline as "there is nothing it is like to be a zombie." "Supervene" appears in the argument step but the conclusion is independently stated ("so physicalism is false") so the argument-trajectory is graspable without precise supervenience-vocabulary.

### N-18 — environmental_ethics
NODE: Environmental Ethics [environmental_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong multi-wave pedagogical structure (Routley's last-man, Singer's animal liberation, Naess's deep ecology); value-locus axis (anthropocentrism / biocentrism / ecocentrism); applied subfields (animal / climate / conservation / environmental justice).
C3 (summary cold-readability): yes — first sentence frames the topic plainly; Routley's last-man / Singer 1975 / Naess 1973 each named with concrete description (the last-man argument's structure is explicit). Lengthy but every technical term is unpacked as introduced.

### N-19 — determinism
NODE: Determinism [determinism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three-thesis distinction (determinism / physical determinism / predictability); QM-stochasticity discussion; compatibilism / luck-objection context.
C3 (summary cold-readability): yes — first sentence states the thesis plainly ("the complete state of the world at any time, together with the laws of nature, fixes the complete state of the world at every later time"); three distinguishing contrasts (fatalism, predictability, denial-of-randomness) glossed inline.

### N-20 — scientific_method
NODE: Scientific Method [scientific_method, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — textbook-vs-post-Kuhnian contrast (Hanson, Kuhn, Feyerabend), normative split (falsificationism vs Bayesianism), methodological-pluralism contemporary mainstream.
C3 (summary cold-readability): yes — first sentence states the activity plainly ("generating, testing, and refining empirical hypotheses ... via observation, experiment, and inference"); the philosophical question framing (one method or many) is explicit; "theory-laden" appears but is contextually graspable.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
  - Sound 25, Defensible 2 (E-11 bivalence→counterexample; E-17 ontology→existence)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 0 (0.0%) | teaching_notes ABSENT 0

## Cross-cutting observations

The C3 0-fail count is a notable break in the 5-shard streak (shards 05–09 all produced ≥1 C3 fail). The shape is composition-driven, not authoring-drift: shard 10's nodes are heavier on foundational/introductory topics (turing_test, mental_causation, determinism, philosophical_zombie, multiple_realizability, equality_political, scientific_method) where the authoring's pedagogical care reads as accessible cold, and lighter on the technical-philosophy framework concentration that drove shard 09's five-instance count (modal_systems_hierarchy, bayes_theorem, chisholm_paradox, causal_exclusion_argument, representationalism_perception). Two borderline-PASS calls — N-3 fuzzy_logic (t-norm jargon undefined load-bearing in sentence 2 but conceptually glossed across the summary) and N-12 generality_problem (reliabilism undefined load-bearing in sentence 1 but the structural problem independently illustrated by the vision-in-good-light examples) — would FAIL on a strict-reading interpretation. Flagged for closeout consistency review against the shard 09 calibration ("load-bearing technical term must be glossed inline").

The "target is the more general/foundational concept" Defensible shape continues across shards 05–10: E-17 ontology → existence this shard. Six consecutive shards with at least one instance; the rubric-calibration question (should this tip to Reversed?) now has six consecutive data points feeding it. E-11 bivalence → counterexample is a different Defensible shape — structural-foundational rather than pedagogical-canonical — recorded separately.

E-26 pyrrhonian_skepticism → problem_of_induction is this shard's audit-touched edge (0062 direction-flip per S-0122 audit). Scored Sound on the audit-validated direction. E-19 renaissance_mechanism → vienna_circle_logical_positivism is the long-distance edge that survived 0061's retyping pass — its endpoints' other edges were retyped to historical_influence but this specific pair was explicitly kept as pedagogical_prerequisite. Scored Sound on the audit-keep-decision reading; the long-distance shape would otherwise suggest Weak-redundant.
