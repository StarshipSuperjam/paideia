# Seed-graph QA census evidence — shard 09

> Authored by S-0170 (routine session) per T-SEED-QA task SQA-09.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 09
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — b777009b-852c-48dd-ba90-78be62bbcb82
EDGE: State (Political) [state_political, political] → Sovereignty [sovereignty, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The state is the concrete political entity that bears sovereignty (the supreme authority over a territory); learning what a state is gives the entity to which the abstract property of sovereignty attaches. Standard pedagogical sequence in political theory.
AUDIT-TOUCHED: none

### E-2 — 28a8cdd8-3196-4831-a42b-eaec96f72ba9
EDGE: Modus Ponens [modus_ponens, service] → Propositional Logic [propositional_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Recurring "target is the more general/foundational concept" shape (PL is the formal framework that contains MP as one of its rules). The could-be-Reversed reading is strong — formal textbooks introduce PL (syntax, semantics, truth tables) first and derive MP as a rule of that system, so MP-as-prereq-for-PL is non-canonical. Held at Defensible because informal MP exposure (the "if P then Q; P; therefore Q" pattern in everyday and informal-logic teaching) is a real concrete-entry-point that can precede formal PL — students often meet MP as the prototypical deductive inference before the formal apparatus is built. Not Reversed because that concrete-entry-point reading is more than a stretch. Flagged as fifth instance of the "target is more general/foundational" shape (post shards 05/06/07/08).
AUDIT-TOUCHED: none

### E-3 — 4387527e-d961-4a34-969d-d6bd6adcdcf8
EDGE: Aristotelian Four Causes [aristotelian_four_causes, service] → Scholasticism [scholasticism, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Scholasticism (medieval Christian and Islamic philosophy) inherited and built systematically on Aristotelian metaphysics, including the four causes, as the framework it synthesized with theological commitments. Understanding the four causes is a prerequisite for understanding scholastic metaphysics.
AUDIT-TOUCHED: none

### E-4 — 77ea8634-0678-4956-b2f6-e377648b8999
EDGE: Natural Rights [natural_rights, political] → Human Rights [human_rights, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Modern human rights discourse derives historically and conceptually from the natural rights tradition (Locke; the founding declarations of the late 18th century). Natural rights is the historical-and-conceptual precursor concept.
AUDIT-TOUCHED: none

### E-5 — a01769d2-dc85-44b9-b5ca-a8c587442b90
EDGE: Physicalism [physicalism, mind] → Type-Identity Theory [type_identity_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Type-identity theory (mental types ARE physical types — e.g., pain IS C-fiber firing) is explicitly defined as a physicalist position about mind. Without the physicalist framework (the broader thesis that mental states are physical), type-identity does not have a position to occupy.
AUDIT-TOUCHED: none

### E-6 — 7db18d6e-8ad1-4f72-a02e-8c4e19593ac2
EDGE: Physicalism [physicalism, mind] → Easy Problems of Consciousness [easy_problems_of_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Chalmers' "easy problems" (explaining functional/cognitive features of consciousness — discrimination, integration, reportability) are easy precisely because they are tractable under broadly physicalist (functionalist) approaches; the easy/hard partition presupposes a physicalist methodological context against which "easy" makes sense. A more proximate prereq (chalmers_hard_problem) might be a closer entry point, but the shard does not carry that concept and physicalism is the appropriate umbrella prereq among available alternatives.
AUDIT-TOUCHED: none

### E-7 — 0a7e3e6c-ae9d-4019-bd1f-91ea47ba54c0
EDGE: Medical Ethics [medical_ethics, ethics] → Reproductive Ethics [reproductive_ethics, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: Reproductive ethics (abortion, IVF, surrogacy, genetic selection) is a topical subfield WITHIN medical/bioethics; medical ethics provides the broader principles (autonomy, beneficence, non-maleficence, justice — the Beauchamp-Childress four principles) that reproductive ethics applies to a specific class of cases. Standard subdomain-applies-broader-framework relationship.
AUDIT-TOUCHED: none

### E-8 — 89c90ee5-3c57-4418-a930-d0dcda49ca23
EDGE: Political Authority [political_authority, political] → Political Legitimacy [political_legitimacy, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Political authority is the entity-like concept (the right to rule, the power to issue binding directives); political legitimacy is the normative property that justifies a given authority claim. Understanding authority as a phenomenon lets you then ask what makes it legitimate — standard pedagogical sequence (Weber's typology of authority first, then normative legitimation theories). Some risk of the recurring "target more general" shape (legitimacy as the more general normative concept), but the entity-then-property direction is canonical here.
AUDIT-TOUCHED: none

### E-9 — dbf436b9-53c1-4ba4-8d9e-d393710acd76
EDGE: Argument (Logical) [argument_logical, service] → Inference Rule [inference_rule, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: An inference rule is a rule for moving from premises to conclusions within an argument. Understanding what an argument is (premises, conclusion, validity, soundness) is a prerequisite for understanding the rules that license such moves.
AUDIT-TOUCHED: none

### E-10 — d5326a81-16b8-4f8c-8026-bb0dd0b1fa02
EDGE: Pyrrhonian Skepticism [pyrrhonian_skepticism, epistemology] → Agrippan Trilemma [agrippan_trilemma, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The Agrippan trilemma (the five modes of Agrippa — dispute, infinite regress, relativity, hypothesis, circularity) is a Pyrrhonian argument structure developed within the ancient Greek Pyrrhonian skeptical tradition. The historical and conceptual framework precedes its specific argument-form.
AUDIT-TOUCHED: none

### E-11 — 6beacdd3-e3b8-4420-b384-2e4c7918ae6e
EDGE: Probability (Mathematical) [probability_mathematical, service] → Bayesian Epistemology [bayesian_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bayesian epistemology models degrees of belief as probabilities and uses Bayes's theorem (a result of mathematical probability theory) for updating. The formal mathematical framework is a clear prerequisite.
AUDIT-TOUCHED: none

### E-12 — 7e13795b-a5b8-416b-9d31-b5d9be1e55bc
EDGE: Causation [causation, metaphysics] → Determinism [determinism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Determinism (the thesis that the state of the universe at any time, with the laws, fixes the state at any other time) is typically introduced and defined via causal language ("every event is caused by prior events"). Some versions are nomological-not-causal, but the standard pedagogical entry to determinism is through causation. Direction is canonical.
AUDIT-TOUCHED: none

### E-13 — 451ed26b-8e62-4ec2-863b-a32ccc5aad45
EDGE: Belief [belief, epistemology] → Epistemic Certainty [certainty, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Epistemic certainty is conceptually a property of beliefs — the maximal degree of confidence, or a special incorrigible kind of belief. The concept of certainty presupposes the concept of belief (something to be certain of).
AUDIT-TOUCHED: none

### E-14 — cb5f48a4-d911-4f80-9b02-7a2f92e07713
EDGE: Universals [universals, metaphysics] → Tropes [tropes, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Tropes (particularized properties — "this red here" rather than redness in general) are an alternative ontology defined against universals. Understanding what tropes are an alternative TO (universals as repeatable entities) is the natural pedagogical entry point.
AUDIT-TOUCHED: none

### E-15 — 1cbe60e1-7ff7-4a1c-8cab-fd72438884c2
EDGE: Universals [universals, metaphysics] → Nominalism [nominalism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nominalism is the rejection of universals as real entities — only particulars exist; "universals" reduce to names, concepts, classes, or resemblance relations. The position is defined against universals; understanding what is being rejected is the prerequisite.
AUDIT-TOUCHED: none

### E-16 — 12e59c98-2421-49f7-887b-16fea78c92b9
EDGE: Expertise [expertise, epistemology] → Epistemic Dependence [epistemic_dependence, epistemology]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Expertise is one paradigm mode of epistemic dependence (the asymmetric layperson-to-expert form); it exemplifies the broader social-epistemological phenomenon of dependence on others' epistemic states."
VERDICT: Sound
RATIONALE: Expertise (the asymmetric layperson-to-expert form of relying on others' epistemic states) is the everyday concrete entry point to the broader social-epistemological concept of epistemic dependence (any form of relying on others' epistemic states — testimony, distributed cognition, institutional knowledge). The audit examined this edge as a weak-edge prune candidate (CB-E-XX in 0063's surface) and deliberately KEPT it with the evidence annotation now carried in the shard, attaching a concrete-entry-point justification. Direction is audit-confirmed; concur on independent review. Note: the edge instantiates the recurring "target is the more general/foundational concept" shape but is held at Sound because the concrete-entry-point reading is explicit, audit-validated, and the asymmetric-expertise reading is genuinely the entry phenomenon.
AUDIT-TOUCHED: migration 0063 — weak-edge cleanup pass examined this edge as a prune candidate and kept it with the evidence annotation justifying retention (not flipped, not pruned). The shard's `evidence` text is that 0063 annotation verbatim.

### E-17 — 4ace6288-c4cb-4532-9879-ea891f8cdc7e
EDGE: Meaning (Linguistic) [meaning, language] → Verificationism [verificationism, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Verificationism is a theory of meaning (logical positivism: a sentence is meaningful iff empirically verifiable, or analytic). Understanding what meaning is (the explanandum of philosophy of language) is the prerequisite for understanding a specific theory about it.
AUDIT-TOUCHED: none

### E-18 — 996073bd-ae59-4459-96cb-0be4b7c69960
EDGE: Concrete Object [concrete_object, metaphysics] → Composition (Mereological) [composition_mereological, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mereological composition (the part-whole relationship — when do parts compose a whole?) is primarily applied to concrete objects (this hand is part of my body; these planks compose this ship). Concrete objects are the paradigm domain over which the composition question is asked; understanding what concrete objects are is the entry point.
AUDIT-TOUCHED: none

### E-19 — cef815af-ca1e-4033-bff1-ffce3858916f
EDGE: Environmental Ethics [environmental_ethics, ethics] → Anthropocentrism [anthropocentrism, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Anthropocentrism (the position that only human interests have direct moral standing) is one position WITHIN the broader debate of environmental ethics (what has moral standing — humans only? animals? ecosystems? future generations?). The framing debate precedes the specific position.
AUDIT-TOUCHED: none

### E-20 — 48a80311-3e7c-4659-9b35-64e59ca04014
EDGE: Physicalism [physicalism, mind] → Logical Behaviorism [behaviorism_logical, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Logical behaviorism (Ryle 1949: mental states reduce to behavioral dispositions) is one form of physicalist analysis of mind — a reductionist proposal about how to physicalize mental talk. The contemporary pedagogical sequence introduces physicalism as the umbrella metaphysical commitment first and then surveys behaviorism, identity theory, functionalism, etc. as physicalist proposals. Some historical-direction concern (behaviorism predates the term "physicalism" in philosophy of mind), but in contemporary teaching physicalism is the framework prereq.
AUDIT-TOUCHED: none

### E-21 — cd9ec9b9-af94-4b9a-ad76-24685b301ed5
EDGE: Knowledge Argument (Mary) [knowledge_argument, mind] → Phenomenal Concept Strategy [phenomenal_concept_strategy, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The phenomenal concept strategy (Loar, Papineau, Tye) is explicitly a response TO the knowledge argument — it accepts the argument's intuitive force but argues that the qualia conclusion is blocked by a distinction between phenomenal and physical concepts (rather than between phenomenal and physical facts). Response presupposes the argument it responds to.
AUDIT-TOUCHED: none

### E-22 — 32f00d9f-dbd8-4073-aaf9-c9229698f719
EDGE: Possible Worlds [possible_worlds, metaphysics] → Modal Realism [modal_realism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Modal realism (Lewis: possible worlds are concrete entities just like the actual world, "many worlds") is a position about possible worlds. Understanding the concept of possible worlds is the prerequisite for understanding a specific ontological commitment about their nature.
AUDIT-TOUCHED: none

### E-23 — d12d6010-5d8e-4019-b55a-bea5eb43f270
EDGE: Argument (Logical) [argument_logical, service] → Counterexample [counterexample, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: A counterexample in logic is an instance that refutes a generalization or shows an argument-form invalid. The concept presupposes the concept of an argument or generalization (the thing to be refuted). Standard direction.
AUDIT-TOUCHED: none

### E-24 — f864bc15-f8b5-430a-9e5d-62cca4d96c09
EDGE: Truth-Conditional Semantics [truth_conditional_semantics, language] → Tarski's T-Schema [tarskis_t_schema, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Truth-conditional semantics is the general project of giving meaning via truth conditions (a sentence's meaning IS its truth conditions); Tarski's T-schema ("S" is true iff S) is the specific formal instrument articulating this. Standard pedagogical sequence: introduce the truth-conditional idea informally first, then meet the T-schema as the formalization. Historical-vs-pedagogical direction concern (Tarski 1933 predates Davidson's articulation of "truth-conditional semantics" as a programmatic label), but the contemporary teaching direction holds.
AUDIT-TOUCHED: none

### E-25 — c11a94e0-aaba-4b02-bc57-2d841665b3a7
EDGE: Intentionality [intentionality, mind] → Functional-Role Semantics [functional_role_semantics, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Functional-role semantics (Block, Harman: mental content is determined by the functional role of states in inferential and behavioral interactions) is a theory of intentionality — an account of how mental states get their content / aboutness. The phenomenon being theorized about (intentionality) precedes the specific theory.
AUDIT-TOUCHED: none

### E-26 — ddc7221f-eaac-4fc8-8968-47435f8c035b
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Knowledge [knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Recurring "target is the more general/foundational concept" shape (propositional knowledge is one SPECIES of the broader GENUS knowledge, which also covers knowing-how and knowing-by-acquaintance). The could-be-Reversed reading is strong on the genus/species relationship — formal pedagogy would introduce knowledge as the category first, then carve out propositional knowledge (the JTB-analyzed kind) as one form. Held at Defensible because the concrete-entry-point reading is real — students first encounter "knowledge" as propositional knowledge in everyday usage ("I know that Paris is the capital of France"), and only later meet the genus/species distinction explicitly. The graph's direction tracks the natural-encounter sequence even if not the genus-first taxonomic sequence. Sixth instance of the recurring shape (post shards 05/06/07/08 + this shard's E-2); strengthens the closeout's rubric-calibration question.
AUDIT-TOUCHED: none

### E-27 — 28bcfad4-5f1c-4036-87f7-a3d1c0390a99
EDGE: Type-Token Distinction (Artworks) [type_token_artworks_distinction, aesthetics] → Ontology of Musical Works [ontology_musical_works, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The ontology of musical works asks what kind of entity a musical work is (a type? a sound-structure? a created abstract artifact?), and the type-token distinction (a symphony is the type, performances are tokens) is the central theoretical apparatus for the standard answers. Understanding type-token first gives you the tool with which to formulate the ontology of musical works.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — expected_value
NODE: Expected Value [expected_value, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the fair-die illustration (1+2+3+4+5+6)/6 = 3.5 is a concrete worked entry that demonstrates the "value the die can never actually show" point cleanly; the connection to expected-utility (von Neumann-Morgenstern, Savage), to utilitarianism, to game-theoretic philosophy, and to the canonical paradoxes (St. Petersburg, Allais, Ellsberg) provides a navigable scholarly map.
C3 (summary cold-readability): yes — borderline. "Random variable" in the load-bearing first sentence is mild jargon, but the formula is supplementary and the second sentence ("Distinct from the everyday 'expected' sense — the formal expected value is a probability-weighted statistical quantity that may not correspond to any actually-possible outcome") provides cold-reader scaffolding that recovers the gist. Math-literate cold reader can parse the formula; non-math-literate cold reader still gets the disambiguation.

### N-2 — realism_about_universals
NODE: Realism about Universals [realism_about_universals, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes Platonic from Aristotelian realism crisply (uninstantiated universals vs in re), names contemporary defenders (Armstrong, Bigelow), discusses the regress concerns (Russell-style relational realism), names Armstrong's "states of affairs" response. Usable scholarly map.
C3 (summary cold-readability): yes — borderline. The summary does not concretely define "universals" (no example like "redness of apple and rose"), so a strict cold-reader test would flag "assumes-the-concept." But the structural ontological commitment is clearly stated (universals exist as entities in their own right), and the two sub-positions are explained with clear differentia (Platonic: exist whether instantiated; Aristotelian: exist only as instantiated but real distinct entities). Cold reader gets the structural shape of the position even without a concrete grip on what universals are. PASS borderline.

### N-3 — socialism
NODE: Socialism [socialism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — exceptional traction. Foundational normative commitments (equality, democratic control, anti-exploitation) named; Marxian analytical framework (labor theory, structural critique, historical materialism) walked through; Cohen's camping-trip thought experiment; internal divisions (revolutionary/reformist, planned/market, democratic socialism/social democracy with named figures and texts); distinctive concepts (alienation, exploitation, class consciousness); standard liberal objections + socialist replies.
C3 (summary cold-readability): yes — clear opening ("family of political-economic doctrines committing to collective or social ownership of the means of production"), motivating commitments named, Marx 1867 Capital cited as a canonical anchor, contemporary academic landscape (Cohen 2009, Wright 2010, Roemer 1994) located. Accessible cold.

### N-4 — evidence
NODE: Evidence [evidence, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames evidence as "the input variable in justification theories" and contrasts internalism's access-question with externalism's reliability-question; names evidentialism (Conee and Feldman) as the position that makes evidence-fit constitutive of justification. Has traction, though somewhat abstract.
C3 (summary cold-readability): yes — very accessible. "What a believer has access to that bears on whether a proposition is true" is plain. The concrete instances (perceptual experience, testimony, memory, inference) anchor the abstract definition. Closing sentence frames the central question cleanly.

### N-5 — paradigm
NODE: Paradigm (Kuhnian) [paradigm, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the two senses of paradigm distinguished (disciplinary matrix vs exemplar) following Kuhn's own 1969 postscript; concrete example (harmonic-oscillator as exemplar); what paradigms organize (problem/solution/evidence/objection); the implications for philosophy of science (historical and sociological work centered; realism-antirealism reframed). Strong scholarly map.
C3 (summary cold-readability): yes — concrete elements (theoretical commitments, exemplary problem-solutions, instruments, methodological norms) ground the abstract opener; Kuhn + Structure of Scientific Revolutions 1962/1970 cited; normal science / paradigm shift introduced clearly.

### N-6 — causal_exclusion_argument
NODE: Causal Exclusion Argument [causal_exclusion_argument, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three-stage walkthrough (supervenience premise → closure premise → exclusion claim → disjunctive conclusion of reductive physicalism or epiphenomenalism), standard responses (Yablo on proportional causation, Bennett on overdetermination, List-Menzies on programming explanation). Strong scholarly map for the philosophy-of-mind reader.
C3 (summary cold-readability): no — jargon-gated. The load-bearing first sentence depends on "non-reductive physicalism" (undefined), and the second sentence depends on "M supervenes on P" (undefined) and "epiphenomenalism" (parenthetically named, not glossed). A cold reader without philosophy-of-mind background sees a structural argument but cannot parse the relations between the technical primitives. Same shape as the recurring cluster (shards 05 N-8 SDL/modal-closure, 06 N-16 credence/notation, 07 N-18 Kantian framework, 08 N-9 + N-19 modal/intentionality).

### N-7 — chisholm_paradox
NODE: Chisholm Paradox [chisholm_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the four claims formalized (Oh, O(h→t), ¬h→O¬t, ¬h), the contradiction derived step by step in SDL, the diagnosis (SDL has no way to express conditional obligations defined over violations), the response families named (dyadic deontic logic Hansson 1969, defeasible/non-monotonic deontic logics Horty, Belnap-Horty stit). Excellent scholarly traction.
C3 (summary cold-readability): no — jargon-gated. The load-bearing first sentence uses the unexpanded acronym "SDL" ("Standard Deontic Logic" — expanded only later in the teaching_notes via N-7's links to deontic_logic, not in this summary). Same EXACT failure shape as shard 05's N-8 ross_paradox (also SDL-undefined in the load-bearing first sentence). The Jones-helps-neighbor example is concrete and clear, but the FORMAL claim "SDL cannot consistently formalize" is the load-bearing definition of what the paradox IS, and SDL itself is undefined. A cold reader gets "there's a paradox involving Jones and contrary-to-duty obligations and some logical system" but cannot grasp the SDL/formal-failure framing the summary commits to.

### N-8 — bayes_theorem
NODE: Bayes's Theorem [bayes_theorem, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — two-line derivation from conditional probability is the cleanest possible introduction; the medical-test example (Casscells-Schoenberger-Graboys 1978 — rare disease, accurate test, surprising posterior) is a concrete worked anchor that demonstrates physician miscalibration empirically; connections to Bayesian epistemology, confirmation theory, and statistical inference each named with the philosophical payoff; the problem of priors located as the most-discussed objection. Excellent traction.
C3 (summary cold-readability): no — jargon-gated. The load-bearing first sentence puts the formula P(H|E) = P(E|H) · P(H) / P(E) front-and-center and the inline definitions use additional technical terms ("prior probability," "likelihood," "marginal probability," "law of total probability over a partition of hypotheses," "posterior probability"). For a cold reader without prior probability theory, the formula AND each term are jargon — there is no plain-language gloss of "what Bayes's theorem does" before the formula and technical terms hit. Same shape as shard 06 N-16 (conditionalization — formula + technical-term-gated load-bearing first sentence).

### N-9 — defeasibility_analysis
NODE: Defeasibility Analysis [defeasibility_analysis, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — acknowledges the theory is technically demanding (specifying which true propositions count as legitimate vs misleading defeaters is the hard problem), names the pedagogical payoff (articulating the intuition that Gettier-knowledge is fragile against further evidence).
C3 (summary cold-readability): yes — borderline. "Gettier response" assumes Gettier as background, but the STRUCTURAL definition is parseable on its own: "knowledge requires justification that cannot be defeated by any true proposition the believer does not yet have." Cold reader gets the structural proposal (defeater-proof justification) even without the Gettier setup. The "Aims to capture the idea that Gettier cases involve hidden defeaters" second sentence is the gated part. PASS borderline.

### N-10 — norm_of_assertion
NODE: Norm of Assertion [norm_of_assertion, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Williamson's argument for the knowledge norm walked through (Moorean paradoxes "p, but I don't know that p" + lottery propositions); explains why the dispute matters (different patterns of conversational repair, criticism, challenge).
C3 (summary cold-readability): yes — clear and parseable. The candidates are listed with self-explanatory glosses ("knowledge norm: one may assert p only if one knows p"), the connection between epistemology and philosophy of language is explained.

### N-11 — haecceity
NODE: Haecceity [haecceity, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the motivating problem (transworld identity) introduced, Black's two-spheres given as the qualitative-twins case, the haecceitist answer (non-qualitative thisness anchor) and its ontological cost named, Lewis's counterpart-theory alternative as the alternative cost-allocation. Good scholarly map.
C3 (summary cold-readability): yes — the Socrates example ("the haecceity of Socrates is the property *being identical to Socrates*") makes the abstract concept (non-qualitative property of being identical to a particular individual) concretely graspable in the load-bearing definition. "Transworld identity" + "possible worlds" + "counterpart theory" follow but are not load-bearing for the core concept.

### N-12 — explosion_principle
NODE: Explosion Principle [explosion_principle, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the four-step classical proof (P∧¬P → P → P∨Q → ¬P → Q via disjunctive syllogism) given explicitly; the consequence (any inconsistent classical theory is trivial) named; the bridge from liar/Russell paradoxes to paraconsistent/dialetheist responses framed as "explosion is the axiom that forces the choice." Strong logical-philosophy traction.
C3 (summary cold-readability): yes — the formula "P ∧ ¬P ⊢ Q" is paired with a plain-English gloss in the load-bearing first sentence ("anything follows from a contradiction"), so the gist is accessible cold even without symbol-fluency. "Ex contradictione quodlibet, ECQ" is named and Latin-glossed. Paraconsistent logics described inline ("logics that reject explosion — that allow inconsistent theories without trivializing them").

### N-13 — credence
NODE: Credence [credence, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — contrast with binary belief introduced, the empirical-cognitive-reality point made (probabilistic reasoning + calibration studies), the Lockean thesis named with its lottery/preface failures as the standard objection.
C3 (summary cold-readability): yes — clear self-defining opening: "A degree of belief — a quantitative attitude representing the strength with which a believer holds a proposition true, typically modeled as a real number in [0, 1]." The follow-up locates credences in Bayesian epistemology and names the relationship-to-full-belief problem; well-scaffolded.

### N-14 — modal_logic
NODE: Modal Logic [modal_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Kripke frame ⟨W, R⟩ introduced, K/T/S4/S5 hierarchy with accessibility-relation constraints mapped to applications (alethic, deontic, epistemic), quantified modal logic flagged with the trans-world identity cross-bridge, explicit pedagogical guidance ("don't teach modal logic without teaching Kripke semantics — pre-Kripke axiom systems are conceptually obscure without the model-theoretic interpretation").
C3 (summary cold-readability): yes — the first sentence ("The formal logic of necessity and possibility") gives a parseable cold-reader gist of WHAT the topic IS. The technical machinery (Kripke semantics, accessibility relation, alethic interpretation) follows in the second sentence and is framework-gated, but the cold reader has the topic-handle from sentence one and can choose to go deeper. Comparable to shard 05 kantian_ethics in structure — technical terms appear but the opener anchors the topic.

### N-15 — universals
NODE: Universals [universals, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Plato/Aristotle origin, modern realists (Armstrong, Bealer), modern nominalists (Lewis class nominalism, Goodman resemblance nominalism, predicate/concept/mereological variants), the cluster of arguments (One Over Many, abstract reference, regress concerns), and explicit pointer to Armstrong 1989 + Lewis 1983 as the systematic references. Excellent scholarly map.
C3 (summary cold-readability): yes — the concrete example carries the load: "The redness of the apple and the redness of the rose are, on the universals view, the very same entity wholly present in both." The abstract definition ("properties or relations conceived as repeatable entities — single things wholly present in each of their instances") is unpacked by the apple/rose case immediately. Contrasts with tropes and nominalism named for orientation.

### N-16 — representationalism_perception
NODE: Representationalism (Perception) [representationalism_perception, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes weak vs strong representationalism (the latter is the contested thesis), names the motivations (unified intentionality theory; physicalism-friendliness via reducing phenomenal character to representational content), names the standard objections (spectrum-inversion arguments; non-representational features of experience — mood-shifts, blurry vision, felt unity of consciousness).
C3 (summary cold-readability): no — jargon-gated. The first sentence is accessible ("perceptual experience represents the world"), and "intentional content" is glossed parenthetically ("such-and-such is the case before me"), BUT the second load-bearing sentence puts "phenomenal character" (undefined) + "supervenes on" (undefined) + "representational content" (undefined as a noun phrase) front-and-center. Compared to shard 07's N-7 representationalism_consciousness which PASSED because "phenomenal character" was glossed there as "what it is like to have an experience," this summary leaves phenomenal-character ungated — a localized authoring difference between two adjacent perception/consciousness representationalism nodes. Same shape as the recurring cluster.

### N-17 — kantian_aesthetic_judgment
NODE: Kantian Aesthetic Judgment [kantian_aesthetic_judgment, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the four moments tracked explicitly (disinterest, universality, purposiveness-without-purpose, necessity), each with a plain-language exposition; the philosophical significance flagged (the anchor for taking aesthetic judgments seriously as cognitively significant; the bridge between Hume's standard-of-taste empiricism and contemporary cognitivism).
C3 (summary cold-readability): yes — the central puzzle is stated plainly in the load-bearing second sentence: "judgments of beauty (this rose is beautiful) appear to claim universal validity (every judger should agree) yet rest on the singular feeling of pleasure or displeasure rather than on conceptual rules." The solution-sentence uses Kantian terms ("free play of imagination and understanding," "subsumed under a determinate concept," "universal communicability") but each is glossed inline ("free play" = "cognitive faculties are engaged by an object without being subsumed under a determinate concept"; "universal communicability" = "a feature of the cognitive faculties shared by all rational beings"). Comparable to shard 05's N-9 kantian_ethics which PASSED with the same structure — Kantian technical terms followed by plain-language unpacking. Distinct from shard 07's N-18 free_play_imagination_understanding which FAILED because the FREE PLAY summary itself was framework-gated without inline glosses — here the broader concept is being defined and the technical primitives ARE glossed.

### N-18 — divine_command_theory
NODE: Divine Command Theory [divine_command_theory, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three versions distinguished crisply (unrestricted DCT, modified DCT per Adams 1999, natural-law theology per Aquinas/Finnis); the Euthyphro dilemma laid out as Socrates' question with both horns spelled out; the modern attempt to escape (grounding good in God's nature, obligations in commands) named. Strong scholarly map.
C3 (summary cold-readability): yes — crystal clear. "What is right is what God commands; what is wrong is what God forbids" is the load-bearing definition stated in everyday language. The Euthyphro dilemma is introduced inline with the explicit question ("is what is right right BECAUSE God commands it, or does God command it because it is right?") and both horns named. Cold reader gets the full conceptual landscape from the summary alone.

### N-19 — modal_systems_hierarchy
NODE: Modal Systems Hierarchy [modal_systems_hierarchy, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the hierarchy taught as progressive enrichment (K-as-minimal, T-adds-reflexivity, S4-adds-transitivity, S5-adds-Euclideanness), the philosophical mappings (alethic ≈ S5, deontic ≈ KD because we have unfulfilled obligations, epistemic ≈ S4 or S5 depending on introspection commitments, provability ≈ GL with its idiosyncratic axiom). Excellent scholarly map.
C3 (summary cold-readability): no — jargon-gated. The load-bearing first sentence puts "normal modal propositional logics — K ⊂ T ⊂ S4 ⊂ S5 — generated by progressively strengthening the accessibility relation" front-and-center, and the subsequent sentences give the axioms in symbolic form (□P → P, □P → □□P, ◇P → □◇P) without natural-language glosses. A cold reader without modal-logic background sees five system names, a subset notation, and three formulas, with "accessibility relation" undefined load-bearing. Compared to shard 09's N-14 modal_logic which PASSED because its first sentence "The formal logic of necessity and possibility" gave a topic-handle, this summary's first sentence assumes the entire modal-logic framework as known. Same shape as the recurring cluster (shards 05/06/07/08 + this shard's N-6, N-7, N-8, N-16).

### N-20 — aesthetics
NODE: Aesthetics [aesthetics, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames the domain as a family-of-questions, distinguishes the broad sense (natural + artistic aesthetic phenomena, including Burke/Kant on the sublime) from the narrow sense (philosophy of art with artwork as paradigm bearer); traces the contemporary analytic lineage from Hume 1757 + Kant 1790 through Bell, Collingwood, Wimsatt-Beardsley, Goodman, Wollheim, Dickie, Walton, Levinson.
C3 (summary cold-readability): yes — concrete aesthetic properties enumerated (beauty, sublimity, gracefulness, elegance) in the load-bearing first sentence; the central questions are listed plainly (what is aesthetic value, what makes something a work of art, what the appropriate response to art is, what role intention and convention play in fixing artistic meaning). Cold reader gets the topic and the central questions accessibly.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 5 (25.0%) | teaching_notes ABSENT 0

## Cross-cutting observations

- **C3 jargon-gating cluster strengthens to its highest count yet — five instances this shard.** Shards 05/06/07/08 each had 1-2 instances of the load-bearing-first-sentence-gated-on-undefined-framework pattern; shard 09 has five (N-6 phil-mind framework, N-7 SDL undefined, N-8 formula+probability jargon, N-16 phenomenal-character ungated, N-19 modal-systems framework). The shard's high concentration of technical-philosophy nodes (causal exclusion, Chisholm paradox, Bayes's theorem, representationalism, modal-systems hierarchy) drives the count — three of the five fails involve modal-logic / probability-formalism framework gating, and two involve philosophy-of-mind framework gating. The localized authoring differences across adjacent nodes are striking: shard 07's N-7 representationalism_consciousness PASSED because "phenomenal character" was glossed as "what it is like to have an experience"; this shard's N-16 representationalism_perception FAILED because phenomenal character is not glossed. Similarly, shard 09's N-17 kantian_aesthetic_judgment PASSED because Kantian technical terms are unpacked inline (matching shard 05's N-9 kantian_ethics pattern); shard 07's N-18 free_play_imagination_understanding FAILED because the SAME Kantian framework was deployed without inline glosses. The pattern is now reliable enough across shards that the SQA-20 closeout should articulate a clear authoring rule: "load-bearing first sentence may use technical terms but must gloss each one inline."

- **Defensible cluster — 2 verdicts, both instances of the recurring "target is the more general/foundational concept" shape.** E-2 modus_ponens → propositional_logic (PL is the formal framework containing MP) and E-26 propositional_knowledge → knowledge (knowledge is the genus, propositional knowledge the species). Both are held at Defensible (not Reversed) on the concrete-entry-point reading — informal MP exposure for E-2 (MP as the prototypical inference encountered in everyday and informal-logic teaching), everyday usage for E-26 (propositional knowledge is what "knowledge" is in everyday speech before the genus/species distinction). Both instances strengthen the cross-shard cluster (now nine consecutive shards from 01-09 with the shape, six with explicit Defensible verdicts: shards 05, 06, 07, 08, 09 × E-2 and 09 × E-26). The SQA-20 closeout's rubric-calibration question — should this shape tip to Reversed? — gains another data point.

- **One audit-touched edge, scored Sound on audit-validated direction.** E-16 expertise → epistemic_dependence was examined by migration 0063 (weak-edge cleanup) as a prune candidate and KEPT with an evidence annotation explicitly justifying the direction ("Expertise is one paradigm mode of epistemic dependence ... it exemplifies the broader social-epistemological phenomenon"). The edge instantiates the recurring "target more general" shape but the audit's keep-with-annotation decision endorses the concrete-entry-point reading. Same scoring pattern as shard 07's E-13 physicalism → reductionism_in_science (audit-touched, kept-with-annotation, scored Sound on audit-validated direction).

- **Defensible count moderate (2), not a watch-list driver.** Shard 04: 1, 05: 4, 06: 6, 07: 3, 08: 1, 09: 2. The over-Defensible-drift watch item is not worsening across the recent run; the shape persists but counts have been within range since shard 06's peak.
