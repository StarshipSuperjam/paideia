# Seed-graph QA census evidence — shard 08

> Authored by S-0169 (routine session) per T-SEED-QA task SQA-08.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 08
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — 6a7e2073-00b5-4fb5-b2e8-2af9ef649b62
EDGE: Higher-Order Theory of Consciousness [higher_order_theory_consciousness, mind] → Higher-Order Thought Theory [higher_order_thought_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Family → variant. Higher-order theories are the family (HOT, HOP, higher-order representation generally); Rosenthal's Higher-Order Thought Theory is the specific variant. Pedagogical direction family-first-then-variant is canonical.
AUDIT-TOUCHED: none

### E-2 — ea167f5c-f800-49db-8734-9c852bb21a1c
EDGE: Truth Value [truth_value, service] → Classical Logic [classical_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The two-valued (true/false) semantics is foundational scaffolding for classical logic. A learner needs the notion of truth value before the system that operates on truth values is intelligible. Note: this shard contains three edges targeting classical_logic (E-2 truth_value, E-16 bivalence_principle, E-25 predicate_logic) — they are conceptually distinct prerequisites (foundational concept, specific axiom, sub-system), not Weak-redundant.
AUDIT-TOUCHED: none

### E-3 — 48e82e2a-bba0-470a-8db6-2f971849cb0a
EDGE: Scientific Method [scientific_method, science] → Demarcation Problem [demarcation_problem, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The demarcation problem ("what distinguishes science from non-science?") presupposes a working notion of scientific method as the thing whose distinctiveness is in question.
AUDIT-TOUCHED: none

### E-4 — ad62e0e4-7098-46cf-82dc-f2af314eed0b
EDGE: Computational Theory of Mind [computational_theory_of_mind, mind] → Turing Test [turing_test, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Reversed
RATIONALE: The pedagogical and historical direction runs the other way. Turing's 1950 paper proposes the imitation game as a behavioral criterion for intelligence — a concrete, accessible scenario that requires no metaphysical framework to grasp. CTM (Putnam 1960s, Fodor 1970s) is a later, more sophisticated metaphysical thesis that mind IS computation. Standard intro-philosophy-of-mind textbooks (Kim, Crane, Heil) introduce the Turing Test FIRST as the historical/motivational entry point, then introduce CTM as the metaphysical position that responds to questions about machine intelligence. CTM does not entail the Turing Test, and the Turing Test does not presuppose CTM — they are independently formulable, and the simpler/earlier concept (Turing Test) is the natural prerequisite. The could-be-Defensible reading (CTM as the framework that makes the Turing Test interpretable as a test for intelligence) is framework-first reasoning, but the rubric calibration the diary established across shards 05-07 — Defensible only when a real concrete-entry-point reading supports the graph's direction — does not save this edge: the source (CTM) is the more abstract concept, not the more concrete entry point. This is a fresh authoring defect, not a re-opening of an audit decision.
AUDIT-TOUCHED: none

### E-5 — 654b7465-50d1-4419-bf2a-f1ec41f46ea1
EDGE: Propositional Logic [propositional_logic, logic] → Predicate Logic [predicate_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Canonical textbook order. Predicate logic extends propositional logic by adding quantifiers and predicates; the propositional base is a strict prerequisite.
AUDIT-TOUCHED: none

### E-6 — fdb9819a-e9bb-43d9-b242-ea1b7add08a4
EDGE: Moral Anti-Realism [moral_anti_realism, ethics] → Expressivism [expressivism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Genus → species. Expressivism is one canonical variety of moral anti-realism (Ayer, Stevenson, Blackburn, Gibbard); learners grasp the genus first.
AUDIT-TOUCHED: none

### E-7 — 28834c86-c4a3-40e8-8f37-661f09772869
EDGE: Argument (Logical) [argument_logical, service] → Epistemic Justification [epistemic_justification, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The structure of inferential support (argument as premises supporting a conclusion) is canonical scaffolding for the analysis of justified belief. Justification is in large part the question of which beliefs one has good arguments for.
AUDIT-TOUCHED: none

### E-8 — (UUID truncated for brevity — see shards.json)
EDGE: Virtue Epistemology [virtue_epistemology, epistemology] → Virtue Responsibilism [virtue_responsibilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Genus → species. Virtue responsibilism (Code, Zagzebski) is one of the two main varieties of virtue epistemology (the other being virtue reliabilism, Sosa-style); the genus framing is needed before the variant distinction is intelligible.
AUDIT-TOUCHED: none

### E-9 — (UUID truncated)
EDGE: Existence [existence, metaphysics] → Time [time, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Existence is the more general/foundational metaphysical concept (being qua being); time is one specific dimension along which things exist. Philosophy-of-time questions (presentism, eternalism, growing-block) take some prior notion of existence for granted. Source IS the more general concept, so the "could-be-Reversed: target is more general/foundational" shape from prior shards does NOT apply here.
AUDIT-TOUCHED: none

### E-10 — (UUID truncated)
EDGE: Aesthetic Experience [aesthetic_experience, aesthetics] → Aesthetic Disinterest [aesthetic_disinterest, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Aesthetic disinterest (Kant's notion that genuine aesthetic appreciation is detached from desire for the object's existence and use) is a feature/structure-of aesthetic experience. Genus → feature.
AUDIT-TOUCHED: none

### E-11 — (UUID truncated)
EDGE: Free Will [free_will, metaphysics] → Determinism [determinism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Shares the cross-shard "could-be-Reversed: target is more general/foundational" shape (shards 05/06/07 cluster). Determinism is a thesis about all causal relations and is arguably the more general/foundational metaphysical thesis; the standard pedagogical entry in many textbooks is determinism FIRST (as the metaphysical thesis), then free will (as the topic that engages with it). The edge runs the other way. It is supportable on a real reading — the free will TOPIC is what makes determinism philosophically salient as a pedagogical concern; without the free-will question, determinism is a less-pressing metaphysical thesis pedagogically. Both readings are at least somewhat compelling, so Defensible (not Reversed). Flagged for the SQA-20 closeout's calibration review on whether this recurring shape should tip to Reversed in future audits.
AUDIT-TOUCHED: none

### E-12 — (UUID truncated)
EDGE: Scientific Theory [scientific_theory, science] → Paradigm (Kuhnian) [paradigm, science] (relabeled "paradigm" in shards.json)
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kuhn's paradigm concept is a more specific and theoretically-loaded concept than the general notion of scientific theory; a learner needs the general "scientific theory" notion before the specific Kuhnian "paradigm" framing is intelligible. Note: this shard contains two edges targeting paradigm (E-12 scientific_theory, E-26 duhem_quine_thesis) — they are distinct prerequisites (general framing vs holism-of-testing), not Weak-redundant.
AUDIT-TOUCHED: none

### E-13 — (UUID truncated)
EDGE: Mind [mind, mind] → Mental State [mental_state, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Genus → species/category. Mind is the most general concept in the philosophy of mind; mental states are the specific types (beliefs, desires, perceptions, intentions, etc.) that minds have. Canonical direction.
AUDIT-TOUCHED: none

### E-14 — (UUID truncated)
EDGE: Physicalism [physicalism, mind] → Eliminative Materialism [eliminative_materialism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Genus → variant. Eliminative materialism (Churchland, Quine) is a strong variety of physicalism that further denies that folk-psychological mental kinds (beliefs, desires) refer to anything real. Canonical direction.
AUDIT-TOUCHED: none

### E-15 — (UUID truncated)
EDGE: Distributive Justice [distributive_justice, political] → Libertarianism (Political) [libertarianism_political, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Question → answer. Libertarianism (Nozick: minimal state, just acquisitions and transfers, anti-redistributive) is one of the major positions on distributive justice. Genus framing is needed first.
AUDIT-TOUCHED: none

### E-16 — (UUID truncated)
EDGE: Principle of Bivalence [bivalence_principle, service] → Classical Logic [classical_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bivalence (every proposition is either true or false, no third value) is one of the constitutive semantic principles of classical logic. Distinct prereq from E-2 truth_value (the foundational concept) and E-25 predicate_logic (the sub-system); not Weak-redundant.
AUDIT-TOUCHED: none

### E-17 — (UUID truncated)
EDGE: Political Authority [political_authority, political] → Political Obligation [political_obligation, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Authority and obligation are correlative political concepts (the state's right to command vs the subject's duty to obey), but the standard pedagogical entry is authority FIRST (the institutional concept that grounds the obligation question). Sound, though authority and obligation are nearly co-equal — Hart and others argue they are conceptually distinct and that one can have authority without the other.
AUDIT-TOUCHED: none

### E-18 — (UUID truncated)
EDGE: Modal Logic [modal_logic, logic] → Deontic Logic [deontic_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Deontic logic uses the modal operators (necessity, possibility) reinterpreted as obligation and permission. The general modal apparatus is a strict prerequisite for the deontic specialization.
AUDIT-TOUCHED: none

### E-19 — (UUID truncated)
EDGE: Possible Worlds [possible_worlds, metaphysics] → Haecceity [haecceity, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Haecceity (this-ness, individual essence — the property an individual has of being THAT individual rather than another) is most natural to formulate in the framework of possible worlds, where the cross-world identity of individuals is the puzzle haecceity is invoked to address.
AUDIT-TOUCHED: none

### E-20 — (UUID truncated)
EDGE: Applied Ethics [applied_ethics, ethics] → Business Ethics [business_ethics, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: Genus → branch. Business ethics is one of the standard branches of applied ethics (alongside bioethics, environmental ethics, etc.). The down-weighted 0.85 weight/confidence is plausibly a pedagogical-importance signal rather than a directional doubt.
AUDIT-TOUCHED: none

### E-21 — (UUID truncated)
EDGE: Art [art, aesthetics] → Imitation Theory of Art [imitation_theory_art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: A pre-theoretical notion of art is the explanandum the imitation theory (Plato, Aristotle, classical mimesis) attempts to define. Genus → theory-of-genus is canonical.
AUDIT-TOUCHED: none

### E-22 — (UUID truncated)
EDGE: Scholasticism [scholasticism, service] → Renaissance and Early-Modern Mechanism [renaissance_mechanism, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Historical-pedagogical sequence. Scholasticism (medieval Aristotelian-theological synthesis) is the framework that early-modern mechanism develops in opposition to and reaction against. The scholastic background frames why the mechanistic shift mattered.
AUDIT-TOUCHED: none

### E-23 — (UUID truncated)
EDGE: Aesthetic Judgment [aesthetic_judgment, aesthetics] → Sublime [sublime, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Aesthetic judgment is the genus framing; the sublime (alongside the beautiful) is one of Kant's specific categories within it. Canonical.
AUDIT-TOUCHED: none

### E-24 — (UUID truncated)
EDGE: Scientific Explanation [scientific_explanation, science] → Unification Theory of Explanation [unification_theory_of_explanation, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Unification theory (Friedman 1974, Kitcher 1981) is one specific theory of what scientific explanation IS. The general explanandum (scientific explanation) precedes any theory of it.
AUDIT-TOUCHED: none

### E-25 — (UUID truncated)
EDGE: Predicate Logic [predicate_logic, logic] → Classical Logic [classical_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: "Classical logic" as a topic in philosophy of logic is the contrast-class with intuitionistic, paraconsistent, relevance, and other non-classical alternatives. To engage that contrast meaningfully, learners need predicate logic as the developed system being labeled "classical." Sub-system (predicate logic) → integrated/named-system framing (classical logic).
AUDIT-TOUCHED: none

### E-26 — (UUID truncated)
EDGE: Duhem-Quine Thesis [duhem_quine_thesis, science] → Paradigm (Kuhnian) [paradigm, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Historical-conceptual chain. Duhem-Quine holism-of-testing (Duhem 1906, Quine 1951) is a strict precursor to Kuhn's paradigm concept (1962); Kuhn's account of how anomalies are absorbed or precipitate revolution incorporates Duhem-Quine holism directly.
AUDIT-TOUCHED: none

### E-27 — (UUID truncated)
EDGE: Hard Problem of Consciousness [hard_problem_of_consciousness, mind] → Panpsychism [panpsychism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Panpsychism (Strawson, Goff, Chalmers) is offered as a response to the hard problem; it makes pedagogical sense only with the hard problem as the motivating challenge already in view. Problem → response.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — simples
NODE: Simples [simples, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the Aristotelian/atomist intuition (finite division must terminate) vs the gunk intuition (could go all the way down), connects to classical mereology, names a concrete pedagogical entry point.
C3 (summary cold-readability): yes — "partless ultimate entities — objects with no proper parts" is accessible; "atomism" and "gunk theorists" are defined inline by their characteristic claims.

### N-2 — underdetermination
NODE: Underdetermination of Theory by Data [underdetermination, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive walk-through of three strengths (weak/curve-fitting, strong/Quine, transient/Stanford) with worked examples and named realist responses. High traction.
C3 (summary cold-readability): yes — clear thesis statement, three strengths each defined inline, motivating connection to scientific realism explained.

### N-3 — belief
NODE: Belief [belief, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the contrast class (non-doxastic attitudes — hoping, fearing, imagining) and flags credence as a refinement worth noting. Brief but provides a concrete handhold.
C3 (summary cold-readability): yes (borderline) — "doxastic attitude toward a proposition" is technical, but the second clause "the believer takes the proposition to be true" self-defines. "Propositional attitude" is recursively brief enough to parse.

### N-4 — institutional_theory_of_art
NODE: Institutional Theory of Art [institutional_theory_of_art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strengths/weaknesses pairs, Dickie's revision history, position vs the historical theory. Genuine traction.
C3 (summary cold-readability): yes — clear procedural definition, Duchamp/readymades context provided.

### N-5 — future_generations
NODE: Future Generations [future_generations, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive walk-through of non-identity, temporal discounting, population ethics, the repugnant conclusion, and longtermism. Names cross-bridges.
C3 (summary cold-readability): yes — long but clear; each technical puzzle is named in caps and defined inline.

### N-6 — epistemic_closure
NODE: Epistemic Closure [epistemic_closure, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the brain-in-a-vat skeptical context and names sensitivity- vs safety-based theory positions. Provides a concrete worked use of closure (the skeptical move).
C3 (summary cold-readability): yes (borderline) — "closed under known entailment" is jargon, but the symbolic clause "if S knows p, and S knows that p entails q, then S knows q" IS the unpacking; a motivated cold reader can parse it via the example.

### N-7 — metaphysics
NODE: Metaphysics [metaphysics, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames the field by contrast with physics and epistemology, provides the Carnap-challenge / Quine-revival historical context. Useful pedagogical scaffolding.
C3 (summary cold-readability): yes — clear definition, examples of subfields (ontology, identity/persistence, causation, time/space, modality, free will, mind-body), explicit contrast with physics.

### N-8 — expression_theory_art
NODE: Expression Theory of Art [expression_theory_art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes communication models (Tolstoy) from articulation models (Collingwood) and expression-as-property analyses (Wollheim, Goodman, Davies, Robinson). Concrete.
C3 (summary cold-readability): yes — clear thesis statement, names canonical figures with dates and texts.

### N-9 — accessibility_relation
NODE: Accessibility Relation [accessibility_relation, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive correspondence table (reflexivity↔T, symmetry↔B, transitivity↔4, Euclideanness↔5) with concrete modal-system applications (alethic, deontic, epistemic). High traction for a learner with the prereqs in place.
C3 (summary cold-readability): no — jargon-gated. The first sentence presupposes Kripke semantics, modal logic, and possible worlds without defining any of them: "In Kripke semantics for modal logic, the binary relation R between possible worlds that determines which worlds are 'accessible from' a given world." The second sentence ("Necessity at world w is truth at every world accessible from w") presupposes a technical understanding of necessity-as-truth-at-all-accessible-worlds that a cold reader does not have. Same shape as the recurring cluster across shards 05 N-8 (SDL/modal-closure), 06 N-16 (credence/notation), 07 N-18 (Kantian framework). FOURTH consecutive shard with the load-bearing-first-sentence-gated-on-undefined-framework pattern.

### N-10 — phenomenal_concept
NODE: Phenomenal Concept [phenomenal_concept, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains type-B materialism, the Mary-on-release case and zombie case applications, standard objections (Chalmers, Stoljar, Levin). Concrete.
C3 (summary cold-readability): yes (borderline) — "phenomenal property under a phenomenal mode of presentation" is heavy technical phrasing, but the ostensive clarification "the kind of concept we deploy when we attend to and refer to our own conscious experience as such" rescues it; the third sentence's "type-B materialist response" is field-specific but does not gate the basic understanding.

### N-11 — practical_wisdom
NODE: Practical Wisdom [practical_wisdom, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three central features (perception, deliberation, desire-integration) named with content; modern virtue-ethics references (McDowell, Nussbaum) and cross-bridges (moral_particularism) flagged. High traction.
C3 (summary cold-readability): yes — phronesis is given with translation; sophia, techne, and deinotes are each defined inline; the master-virtue role and contrast with rule-application are stated clearly.

### N-12 — perdurantism
NODE: Perdurantism [perdurantism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the indiscernibility-puzzle solution concretely (noon-cat-stage bent vs 1pm-cat-stage not bent, whole cat neither simpliciter), names stage-theory variant (Sider). Concrete worked example.
C3 (summary cold-readability): yes — the cat example anchors the abstract claim; "eternalism" is mentioned as alignment but not load-bearing for the basic concept.

### N-13 — political_legitimacy
NODE: Political Legitimacy [political_legitimacy, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive walk-through of consent (Locke/Rawls), fair-play (Hart), democratic (Habermas/Cohen), welfare-instrumentalist, and mixed theories with named challenges. High traction.
C3 (summary cold-readability): yes — clear definition, distinguished from authority/justice/sociological-legitimacy, major theories named.

### N-14 — communitarianism
NODE: Communitarianism [communitarianism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three principal lines of critique (Sandel metaphysical, MacIntyre historical, Walzer methodological) with worked content; standard liberal replies named. High traction.
C3 (summary cold-readability): yes — clear thesis statement; canonical contemporary texts named with dates and one-line summaries.

### N-15 — russell_paradox
NODE: Russell's Paradox [russell_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — historical context (Russell-Frege correspondence, Frege's "arithmetic totters" reply), both technical resolutions named (ZF separation, Russell type theory), structural connection to the liar paradox flagged. High traction.
C3 (summary cold-readability): yes (borderline) — "naive set theory," "comprehension principle," "ZF separation" are technical terms, but the natural-language formulation "the set R of all sets that are not members of themselves" is parseable and the "R ∈ R iff R ∉ R" notation, while symbolic, is widely-enough taught that it does not gate basic comprehension.

### N-16 — paradigm_shift
NODE: Paradigm Shift [paradigm_shift, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three canonical historical examples (Copernican, chemical/Lavoisier, Einsteinian) each with concrete content; mainstream contemporary view on incommensurability flagged with named critics (Putnam, Davidson, Hacking). High traction.
C3 (summary cold-readability): yes — gestalt-switch metaphor anchors the concept; "incommensurable" is defined inline with multiple concrete features.

### N-17 — growing_block_theory
NODE: Growing Block Theory [growing_block_theory, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — positions growing block between presentism and eternalism, names the asymmetric-time intuitions it captures, names the leading-edge-of-the-block challenge (Tooley) with the critic's response. Concrete.
C3 (summary cold-readability): yes — concrete metaphor (growing block, leading edge); "presentism" and "eternalism" are referenced but the position is intelligible without prior expertise in either.

### N-18 — higher_order_theory_consciousness
NODE: Higher-Order Theory of Consciousness [higher_order_theory_consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains motivation (subliminal/peripheral states are not conscious), names the Block objection and the regress objection with Rosenthal's solution. Concrete.
C3 (summary cold-readability): yes — concrete example (first-order pain becomes conscious when there is a higher-order representation that one is in pain) anchors the abstract claim; canonical defenders named.

### N-19 — phenomenal_intentionality
NODE: Phenomenal Intentionality [phenomenal_intentionality, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the contrast with standard naturalistic (causal/teleosemantic) theories of content concretely (the horse-thought example), names the standard objections and the relation to representationalism. Provides traction once the prereqs are in place.
C3 (summary cold-readability): no — jargon-gated. Multiple undefined technical terms in the load-bearing first sentence: "phenomenal character," "intentionality," "intentional content," "representationalism," "naturalistic theories of content." A cold reader without prior philosophy of mind background cannot parse "phenomenal character grounds intentionality rather than the reverse" — both terms undefined; nor "original intentional content is constituted by, or fixed by, phenomenal character." The parenthetical at the end ("which start with intentionality and try to derive phenomenal character via representationalism") presupposes all the same terms. Same shape as N-9 in this shard and the recurring cluster across shards 05/06/07.

### N-20 — contextualism_epistemic
NODE: Epistemic Contextualism [contextualism_epistemic, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — DeRose bank case named as the canonical pedagogical entry (low-stakes-true/high-stakes-true contrast); subject-sensitive invariantism (Stanley) named as the principal alternative. Concrete.
C3 (summary cold-readability): yes — "context-sensitive" is used in its ordinary sense and clarified by "what counts as knowledge depends on conversational context — the standards in play, the salient alternatives, what is at stake." Accessible.

## Shard tally
- Edges: 27 total | Reversed 1 | Weak-redundant 0 | defective 1 (3.7%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 2 (10.0%) | teaching_notes ABSENT 0
- Defensible: 1 (E-11)
- Sound: 25
- Audit-touched edges: 0 (zero match against migrations 0061-0065 forward or reverse)

## Cross-cutting observations

The C3 jargon-gating cluster strengthens. Two C3 fails this shard (N-9 accessibility_relation, N-19 phenomenal_intentionality), both the same load-bearing-first-sentence-gated-on-undefined-framework shape that shards 05 (N-8 SDL), 06 (N-16 credence/notation), and 07 (N-18 Kantian framework) flagged. This is now FOUR consecutive shards with the pattern, and shard 08 produced two instances rather than one — the mechanism is reliable, not noise. The fail-shape is recognizable: load-bearing first sentence presupposes a technical framework (modal logic + Kripke semantics for N-9; phenomenal-character + intentionality + naturalistic-content for N-19) that a cold reader does not have, with the framework not unpacked inline. Distinct from "uses one undefined term" — this is whole-framework gating. Strong signal for the SQA-20 closeout's pattern-clusters section.

The over-Defensible-drift watch item is NOT worsening this shard. Defensible count: 1 (E-11), down from shard 06's 6 and shard 07's 3. The E-11 (free_will → determinism) instance shares the recurring "could-be-Reversed: target is more general/foundational" shape from shards 05/06/07, but only one instance this shard. Consistent with the diary calibration applied literally rather than drift-driven.

E-4 (computational_theory_of_mind → turing_test) is the strongest-warranted Reversed call of the recent census run. Fresh authoring defect (not audit-touched), structurally clear: Turing Test is the historical and pedagogical entry point (1950, simple behavioral idea); CTM is the later metaphysical framework (1960s+, requires functionalism context). Standard intro textbooks teach the Turing Test FIRST. Recorded with detailed rationale so the closeout can disposition cleanly without re-deriving.

Running C1 across shards 01-08: 10.7 / 3.6 / 3.6 / 0.0 / 3.7 / 0.0 / 0.0 / 3.7%. Eight data points, all under the production audit's 13% baseline. The 0-defect runs (shards 04, 06, 07) and the low-single-digit-defect shards (02, 03, 05, 08) bracket a stable "well under baseline" census signal so far. Eleven shards remain.
