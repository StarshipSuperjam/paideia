# Seed-graph QA census evidence — shard 16

> Authored by S-0178 (routine session) per T-SEED-QA task SQA-16.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 16
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — a482c924-c395-4fe5-8a5b-2bd42a1513dc
EDGE: Property [property, metaphysics] → Universals [universals, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: "Property" is the everyday/working notion (color, shape, charge); "universals" is the realist's metaphysical thesis about what properties ARE — multiply-instantiable abstract entities (Plato/Aristotle, Armstrong). Pedagogically you teach the working notion of property first, then introduce universals as the metaphysical question about properties. Concept → metaphysical-question-about-it; same shape as shard 13 E-15 virtue_epistemology→intellectual_virtue (Defensible) but cleaner Sound here because property is genuinely pre-theoretic where intellectual_virtue is more tightly bundled with virtue_epistemology.
AUDIT-TOUCHED: none

### E-2 — e48006c7-986e-454c-8c82-64f4f8297f47
EDGE: Four Principles of Biomedical Ethics [four_principles_bioethics, ethics] → Beneficence [beneficence, ethics]
  weight=0.95, confidence=0.95, evidence=NULL
VERDICT: Sound
RATIONALE: The Beauchamp & Childress four-principles framework introduces beneficence as one of its four constitutive principles (with autonomy, non-maleficence, justice). The bioethical-principle sense of beneficence — its specific weight, scope, and conflict-with-autonomy framing — is framework-internal even though the everyday concept of doing-good predates it. Framework → its component principle; same pattern as the framework-introduces-its-component-concepts shape established at shard 13 E-15.
AUDIT-TOUCHED: none

### E-3 — dc6c61e6-d5a5-46df-8f0c-81257735f39c
EDGE: Inference Rule [inference_rule, service] → Modus Tollens [modus_tollens, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Inference rule is the umbrella concept; modus tollens (from "if P then Q" and "not Q", derive "not P") is one specific instance. Umbrella → instance, the canonical Sound shape across shards.
AUDIT-TOUCHED: none

### E-4 — 239c6d52-4136-4f28-9122-cc805c4a9ca6
EDGE: Distributive Justice [distributive_justice, political] → Desert Theory (Political) [desert_theory_political, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Distributive justice is the field-level question (how should goods be distributed among members of society?); desert theory is one canonical answer-family (according to merit/contribution/responsibility). Field-question → answer-family; same shape as shard 11 E-19 etc.
AUDIT-TOUCHED: none

### E-5 — bfcc17c6-8b71-47c0-a6aa-817dba1b9a93
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Epistemic Certainty [certainty, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional knowledge (knowing-that p) is the standard analytic-epistemology object of study; certainty is debated as a possible condition on knowledge (Cartesian project) or as a special epistemic standing distinct from knowledge (Lehrer, Klein on fallibilism). Object-of-study → its candidate-condition; pedagogically you teach what propositional knowledge IS first, then take up whether certainty is required for it. Pairs with E-22 below (certainty → fallibilism) — the position-and-its-rejection pattern surrounding certainty.
AUDIT-TOUCHED: none

### E-6 — cd855ccf-4bc9-4d9d-bb0d-9ad625559265
EDGE: Property [property, metaphysics] → Realism about Universals [realism_about_universals, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Property is the pre-theoretic notion; realism about universals is one specific metaphysical position about properties (universals exist as mind-independent multiply-instantiable entities — Armstrong, Plato; vs nominalism/conceptualism). Concept → position-about-it. Companion to E-1; the shard pairs the umbrella metaphysical move with the specific-realist position via two distinct edges, both Sound.
AUDIT-TOUCHED: none

### E-7 — f2f46075-1dca-4d7a-abec-9c38b2f2426c
EDGE: Reliabilism [reliabilism, epistemology] → Virtue Reliabilism [virtue_reliabilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reliabilism (Goldman 1979) is the umbrella process-reliability epistemological position; virtue reliabilism (Sosa, Greco) is one specific elaboration that re-conceives reliable processes as cognitive virtues seated in the agent. Umbrella → specific-variant, the recurring sound pattern.
AUDIT-TOUCHED: none

### E-8 — 60ffa5c6-7731-46b6-b3a0-e2ce86e66f7d
EDGE: Hypothetico-Deductive Method [hypothetico_deductivism, science] → Bayesian Confirmation Theory [bayesianism_confirmation, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: H-D was the older 20th-century account of confirmation; Bayesian confirmation theory supplanted it in the analytic tradition since the 1970s by handling H-D's technical problems (irrelevant conjunctions, the strength problem, the tacking paradox) via the conditional-probability apparatus. N-17 bayesianism_confirmation summary explicitly says "supplanting the H-D account" — the pedagogical succession is encoded in the target's own teaching content. Predecessor → successor; same shape as shard 14 etc.
AUDIT-TOUCHED: none

### E-9 — 6e0dd87d-c40f-4b76-b39b-6820605b1588
EDGE: Applied Ethics [applied_ethics, ethics] → Bioethics [bioethics, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Applied ethics is the umbrella domain (ethics-applied-to-particular-domains-of-practice); bioethics is one of its major sub-fields (alongside business ethics, environmental ethics, etc.). Umbrella → sub-field.
AUDIT-TOUCHED: none

### E-10 — 03b2e2ae-b44c-4afd-9cfd-dceadfd7aaea
EDGE: Four Principles of Biomedical Ethics [four_principles_bioethics, ethics] → Autonomy (Bioethical) [autonomy_bioethical, ethics]
  weight=0.95, confidence=0.95, evidence=NULL
VERDICT: Sound
RATIONALE: Same shape as E-2: the Beauchamp & Childress framework introduces autonomy as one of its four constitutive principles. The bioethical-autonomy sense (informed-consent-grounding, refusing-treatment, advance-directives) is framework-internal even though the broader Kantian autonomy concept predates the framework. Framework → component.
AUDIT-TOUCHED: none

### E-11 — 834f309f-78e8-4836-bfeb-994d1b3b270b
EDGE: Principle of Bivalence [bivalence_principle, service] → Fuzzy Logic [fuzzy_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: To grasp fuzzy logic as fuzzy you need to grasp bivalence as the principle being abandoned — fuzzy logic admits degrees of truth between 0 and 1, contra the bivalence "every proposition is either true or false." Position → its rejection; the canonical pedagogical move (introduce the standard, then introduce the deviant logic via what it gives up).
AUDIT-TOUCHED: none

### E-12 — 3af30e3a-fc28-4a02-923d-fba8511ede4c
EDGE: Expected Value [expected_value, service] → Dutch Book Argument [dutch_book_argument, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The Dutch book argument (Ramsey, de Finetti) relies on expected-value reasoning to demonstrate that incoherent credences license bets each of which the agent rationally accepts but which together guarantee a sure loss. To grasp the argument you need expected-value first. Concept → its application; same shape as shard 14 N-2 / shard 13 E-19 dutch_book chains.
AUDIT-TOUCHED: none

### E-13 — 76d0e883-c38c-4e5f-add4-be1680c9027d
EDGE: Epistemic Closure [epistemic_closure, epistemology] → Closure Denial [closure_denial, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: To grasp closure denial (Dretske's relevant-alternatives, Nozick's tracking) you need to grasp the closure principle being denied (knowledge transmits across known logical entailment). Position → its rejection; same shape as E-11 above. Canonical move in epistemology pedagogy: introduce the principle, then introduce skeptical pressure on it that motivates denial.
AUDIT-TOUCHED: none

### E-14 — 8b85a205-e10c-4fe2-ae97-a9399ac7f2d1
EDGE: Incompatibilism [incompatibilism, metaphysics] → Libertarianism (Metaphysical) [libertarianism_metaphysical, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Incompatibilism is the umbrella thesis (free will is incompatible with determinism); metaphysical libertarianism is one of its two canonical species (incompatibilism + we have free will → not all our actions are determined; vs hard determinism / hard incompatibilism). N-19 incompatibilism summary explicitly says "Incompatibilists divide into libertarians ... and hard determinists / hard incompatibilists" — the species-relation is encoded in the source's own teaching content. Umbrella → species.
AUDIT-TOUCHED: none

### E-15 — 4c07ab2f-bcbc-46b5-98af-6d556cde0242
EDGE: Numerical Identity [numerical_identity, metaphysics] → Persistence [persistence, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Numerical identity (this is the same X as that — Leibniz's law) is the prerequisite concept; persistence (an object's being identical-to-itself across time) is the diachronic application of identity. Identity-concept → its temporal-application. Pedagogically you teach what identity is, then take up the temporal puzzle (perdurance vs endurance vs stage theory).
AUDIT-TOUCHED: none

### E-16 — cbcced78-af51-476e-870e-3f6fb6ea5a25
EDGE: Theory-Ladenness of Observation [theory_ladenness_of_observation, science] → Paradigm (Kuhnian) [paradigm, science]
  weight=1.0, confidence=1.0, evidence=Per S-0122 audit: The correction: Hanson articulated theory-ladenness (1958) before Kuhn introduced paradigm-talk (1962); Kuhn imported and extended Hanson's thesis. Direction should be theory_ladenness_of_observation > paradigm.
VERDICT: Sound
RATIONALE: Audit-validated direction (0062 SCI-E-4 direction flip per S-0122). Hanson 1958 PATTERNS OF DISCOVERY articulated theory-ladenness; Kuhn's 1962 STRUCTURE imported and extended Hanson's thesis as part of the paradigm framework. Chronological priority + Kuhn's explicit Hanson-citation establishes the prerequisite direction. Same audit-validated-direction-flip Sound shape as shard 14 E-25 performative→speech_act (also 0062).
AUDIT-TOUCHED: migration 0062 SCI-E-4 — direction flip; audit explicitly endorsed theory_ladenness → paradigm direction. Inline `evidence` text confirms the audit decision.

### E-17 — 2b8aaf29-ded3-4c25-9686-a08a2a58e292
EDGE: Speech Act [speech_act, language] → Presupposition [presupposition, language]
  weight=1.0, confidence=1.0, evidence=Per S-0122 audit: Presuppositions are a sub-topic in speech-act pragmatics; the notion of what an utterance presupposes depends on understanding the illocutionary-act structure of utterances (Searle F(P) framework).
VERDICT: Sound
RATIONALE: Audit-validated framework-introduces-sub-topic reading (0064 LAN-E-3 retain-with-annotation evidence backfill per S-0122). Presupposition as a technical pragmatic concept (Strawson, Stalnaker, Heim's projection problem) sits within the speech-act pragmatics machinery (illocutionary-act structure, Searle's F(P) framework); to grasp what it is for an utterance to carry a presupposition you need the speech-act apparatus first. Same retain-with-annotation evidence-backfill shape as shard 13 E-19 bayesian_epistemology→dutch_book and shard 15 E-7/E-21 (all 0064 retain-with-annotation).
AUDIT-TOUCHED: migration 0064 LAN-E-3 — evidence backfill / retain-with-annotation. Inline `evidence` text confirms the audit decision.

### E-18 — fe69838b-d6d7-4840-a871-fca92863da05
EDGE: Metaethics [metaethics, ethics] → Moral Epistemology [moral_epistemology, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Metaethics is the umbrella domain (questions about the nature, status, and grounds of moral claims); moral epistemology is one of its sub-areas (how do we have moral knowledge? — moral intuitionism, perceptualism, sentimentalism, constructivism). Umbrella → sub-area.
AUDIT-TOUCHED: none

### E-19 — 0d1b243e-1273-4190-abaa-af1716a6e269
EDGE: Normative Ethics [normative_ethics, ethics] → Moral Particularism [moral_particularism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Normative ethics is the umbrella domain (what should I do? what makes acts right or wrong?); moral particularism (Dancy 1993, ETHICS WITHOUT PRINCIPLES) is one specific position-family within it (denial that moral judgment proceeds via general principles; case-by-case judgment via salient features). Umbrella → position; same shape as E-7, E-14, E-27.
AUDIT-TOUCHED: none

### E-20 — 44205b84-7a39-42fd-8f48-38d1c44520f3
EDGE: Four Principles of Biomedical Ethics [four_principles_bioethics, ethics] → Non-Maleficence [non_maleficence, ethics]
  weight=0.95, confidence=0.95, evidence=NULL
VERDICT: Sound
RATIONALE: Same shape as E-2 / E-10: the Beauchamp & Childress framework introduces non-maleficence ("first, do no harm" — the negative duty paired with beneficence) as one of its four constitutive principles. Framework → component. The shard's three-edge repeat from this same source (E-2/E-10/E-20 covering beneficence/autonomy/non-maleficence; the fourth principle, justice, is presumably in another shard) is the recurring framework-introduces-its-N-components shape, all three Sound on the bioethical-principle reading.
AUDIT-TOUCHED: none

### E-21 — 9d811e22-92c6-4689-97b0-5cf06dc55d60
EDGE: Metaethics [metaethics, ethics] → Is-Ought Distinction [is_ought_distinction, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Metaethics is the umbrella domain; the is-ought distinction (Hume's TREATISE 1739) is a specific metaethical thesis within it (no normative conclusion validly follows from purely descriptive premises). Umbrella → specific-issue-within-it; companion to E-18 — both run from metaethics into different sub-questions.
AUDIT-TOUCHED: none

### E-22 — dc4b5704-eb7e-4802-bea6-9e58aa0a12aa
EDGE: Epistemic Certainty [certainty, epistemology] → Fallibilism [fallibilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Fallibilism is the position that knowledge does not require certainty — to grasp it you need the certainty-requirement being denied. Position → its rejection; same shape as E-11, E-13, E-26. Pairs with E-5 above (propositional_knowledge → certainty) — the shard contains a three-edge cluster around certainty (E-5 sets it up as a candidate condition on knowledge, E-22 introduces the fallibilist denial that it's required).
AUDIT-TOUCHED: none

### E-23 — 6d215d6d-7d41-479b-9b1a-012ea3100c28
EDGE: Scientific Method [scientific_method, science] → Underdetermination of Theory by Data [underdetermination, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Scientific method is the umbrella concept; underdetermination (Quine-Duhem; Quine 1951 "Two Dogmas") is a specific problem about scientific method — the thesis that any body of evidence is compatible with multiple inconsistent theories. Method-concept → problem-about-method.
AUDIT-TOUCHED: none

### E-24 — e4b7abf2-dc6d-4609-bf97-5fc3b5fc12c0
EDGE: Indexical Expression [indexical, language] → Character and Content (Two-Dimensional Semantics) [character_and_content, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Indexical expressions ("I", "now", "here", demonstratives) are the linguistic phenomenon; Kaplan's 1989 character/content distinction in DEMONSTRATIVES is the formal-semantic apparatus designed to analyze them (character is the rule from context to content; content is what's said in a context). Phenomenon → its theoretical analysis. Same shape as E-1, E-6.
AUDIT-TOUCHED: none

### E-25 — 62675f40-47bd-41b2-ae83-ff66a666537d
EDGE: Existence [existence, metaphysics] → Relation [relation, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Existence and relation are two of the most fundamental metaphysical categories and are typically introduced as orthogonal topics in a metaphysics curriculum (existence: what is there? Quine's criterion of ontological commitment; relation: Russell's discovery of relations as a third category beyond substances and properties). The pedagogical-priority claim "existence before relation" is not the canonical order — they're more parallel topics, and one can introduce relations as a category-of-things-there-are without first laying down a specific existence theory. Defensible on the "existence as the most fundamental ontological notion, all other categories build on it" reading; weakly Sound only on a specific framework-dependent ordering. Distinct in kind from the strong umbrella → species pattern that grounds most Sound calls in this shard. SQA-20 calibration question: should two co-fundamental metaphysical categories carry a prerequisite edge in either direction at all, or are these better modeled as parallel topics? Flag for closeout review of category-pair prerequisite shape.
AUDIT-TOUCHED: none

### E-26 — fcdef9ec-7eeb-4753-813e-7764cb487fb1
EDGE: Justified True Belief [justified_true_belief, epistemology] → Knowledge-First Epistemology [knowledge_first_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: JTB is the traditional analysis of knowledge that knowledge-first epistemology (Williamson 2000, KNOWLEDGE AND ITS LIMITS) explicitly rejects — "knowledge first" means refusing to analyze knowledge into more basic conditions like belief, truth, justification. To grasp the position you need the JTB tradition it inverts. Position → its rejection; same shape as E-11, E-13, E-22. The four-edge concentration of "position → its rejection" in this shard (E-11, E-13, E-22, E-26) is a notable density — flagged in cross-cutting below.
AUDIT-TOUCHED: none

### E-27 — 5871c7f7-9747-4c2d-9f67-6922a19536b5
EDGE: Consequentialism [consequentialism, ethics] → Utilitarianism [utilitarianism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Consequentialism is the umbrella (judge actions by consequences); utilitarianism is the canonical species (consequences = utility, typically pleasure-minus-pain or preference-satisfaction). N-15 utilitarianism summary explicitly opens "The classical and canonical consequentialist theory" — the species-relation is encoded in the target's own teaching content. Umbrella → species; same shape as E-7, E-14, E-19.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — law_of_nature
NODE: Law of Nature [law_of_nature, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens with the canonical golden-spheres / uranium-spheres contrast (true generalization vs accidental regularity), then walks through the three main metaphysical accounts (regularity / necessitarian / dispositional essentialism) with proponents and dates. Strong foothold.
C3 (summary cold-readability): yes — "true generalization of unrestricted scope describing how things must be" is parsable; the three contested views are listed with proponents and clear position-summaries. Reads cleanly.

### N-2 — tracking_theory_of_knowledge
NODE: Tracking Theory of Knowledge [tracking_theory_of_knowledge, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — brief (287 chars) but identifies what sensitivity and adherence each do, names Sosa's safety condition as the contemporary refinement. Compact but functional foothold.
C3 (summary cold-readability): yes — names the position (Nozick 1981), gives the analysans (sensitivity + adherence) in plain English with the counterfactual schema spelled out. Borderline-PASS: "Gettier response" is named without external gloss but appears as contextual frame and is not load-bearing for parsing the analysans itself. Same calibration as shard 14 N-2 predicate_logic and shard 13 N-10 dutch_book where a named-but-not-needed prereq sits next to a structural-shape definition.

### N-3 — conservatism
NODE: Conservatism [conservatism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (2311 chars) walk through foundational commitments (tradition / prudence / organic-conception / skepticism-of-rationalism), the canonical Burkean argument vs the French Revolution, Oakeshott on rationalism in politics, three internal varieties (traditionalist / religious / fusionist), and explicit distinctions from libertarianism / fascism / reactionary politics. Strong, unusually comprehensive.
C3 (summary cold-readability): yes — "political tradition emphasizing tradition, prudence, gradualism, the organic interconnection of social institutions, and skepticism about the rationalist reform of political life" is fully accessible English; Burke 1790 + Oakeshott 1962 + the strand taxonomy are explained inline.

### N-4 — proposition
NODE: Proposition [proposition, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens by distinguishing propositions from sentences and utterances with multilingual examples ("It is raining" / "Es regnet" / "Il pleut"), then walks through three metaphysical accounts (Russellian / Fregean / sets-of-possible-worlds) with each account's specific cost. Strong.
C3 (summary cold-readability): yes — "the truth-evaluable content expressed by a declarative sentence" plus the "asserted / believed / doubted" enumeration grounds the concept; "propositional attitude" is named but immediately exemplified.

### N-5 — indicative_conditional
NODE: Indicative Conditional [indicative_conditional, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Adams's 1970 Oswald-Kennedy example as the canonical entry point (same antecedent/consequent, opposite truth values for indicative vs counterfactual), then three theory variants (material-conditional + Gricean implicature; suppositional / probability; closest-world) with named defenders. Strong.
C3 (summary cold-readability): yes — the indicative/counterfactual contrast is illustrated inline with the Oswald-Kennedy example; theories are named with defenders. The mood-distinction (indicative vs subjunctive) is a load-bearing grammatical concept assumed without gloss but accessible to any educated reader.

### N-6 — causal_theory_of_mental_content
NODE: Causal Theory of Mental Content [causal_theory_of_mental_content, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names two main variants (information-theoretic Dretske/Stampe; teleosemantic Millikan/Papineau), then frames the disjunction problem (Fodor) with named responses (asymmetric dependence / normal-condition restriction). Strong.
C3 (summary cold-readability): yes — "mental content is fixed by reliable causal-covariational relations between mental representations and the environmental conditions they typically respond to" is parsable; the horse/cow example concretizes the misrepresentation puzzle. "Intentionality" / "mental content" are framework concepts but the example carries them.

### N-7 — modus_ponens
NODE: Modus Ponens [modus_ponens, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — schema-then-instance-then-multi-step pedagogical scaffold; pairs with affirming-the-consequent fallacy as the canonical pedagogical contrast; connects to the deduction theorem. Strong, well-shaped.
C3 (summary cold-readability): yes — "from 'if P then Q' and 'P', derive 'Q'" is the inference rule explicitly stated; the "method of affirming" Latin gloss is supplied; the fallacy contrast is described.

### N-8 — property_dualism
NODE: Property Dualism [property_dualism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Mary thought experiment (Jackson) and zombie argument (Chalmers) framed as the leading arguments; explicit distinction from the hard_problem; standard physicalist responses (phenomenal-concept-strategy / type-B materialism) named. Strong.
C3 (summary cold-readability): yes — "one kind of substance (physical) but two kinds of property (physical and mental)" is a clean structural statement; named defenders + dates supplied.

### N-9 — personal_identity
NODE: Personal Identity [personal_identity, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Locke's memory-criterion as the framing, then psychological-continuity (Parfit/Shoemaker) / animalism (Olson) / bodily-continuity laid out, capped by Parfit's teletransportation/fission/fusion thought experiments as the divergence-cases. Strong.
C3 (summary cold-readability): yes — "diachronic identity question for persons" — "diachronic" is technical but immediately glossed by "in virtue of what is the person at one time identical to the person at another time?" Locke 1689 + named contemporary positions supplied.

### N-10 — quantifier
NODE: Quantifier [quantifier, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — propositional-vs-predicate-logic move-via-quantifier-introduction; concrete contrast (Socrates is mortal as P vs M(s)); the everyone-loves-someone scope-order example as the most pedagogically valuable difficulty. Strong.
C3 (summary cold-readability): yes — borderline-PASS. "Variable-binding logical operator" is technical jargon, immediately glossed by "converts an open formula (one with free variables) into a closed formula (with all variables bound)"; ∀ and ∃ are introduced with their plain-English readings ("for all", "there exists") and the truth-condition schema ("∀x P(x) is true in a domain D iff every member of D satisfies P") supplies the working semantics. Same calibration as shard 14 N-2 predicate_logic / shard 12 N-3 formal_proof — load-bearing technical terms gated through an in-line structural-shape gloss.

### N-11 — eliminative_materialism
NODE: Eliminative Materialism [eliminative_materialism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames eliminativism as the maximally revisionary physicalism via contrast with type-identity and functionalism; phlogiston analogy supplies the concrete model; standard objections (self-refutation; folk-psychology's predictive success; the conceivability gap) named. Strong.
C3 (summary cold-readability): yes — "the categories of folk psychology (belief, desire, intention, etc.) do not refer to anything real — they are part of a false theory of human behavior that mature neuroscience will replace" is fully accessible English; defenders named with dates.

### N-12 — eudaimonia
NODE: Eudaimonia [eudaimonia, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1804 chars) walk through Aristotle's NICOMACHEAN ETHICS Book I argument (chains-of-goods, supreme-good criteria), the function (ergon) argument, the constitutive-not-causal relation to virtuous activity, modern translation-difficulty, Hursthouse 1999 naturalist eudaimonism, and standard criticisms (too thick / too thin). Strong.
C3 (summary cold-readability): yes — opens with "Aristotle's conception of human flourishing — the highest human good"; the multi-translation paragraph ("happiness", "flourishing", "well-being", "the good life") explicitly addresses what the term does and does not mean; objective-vs-subjective contrast spelled out.

### N-13 — research_ethics
NODE: Research Ethics [research_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — historical scaffold (Nuremberg → Belmont → Common Rule → contemporary literature), Belmont's three principles named with their content (Respect for Persons / Beneficence / Justice), Emanuel-Wendler-Grady 2000 seven requirements named, special-population concerns enumerated. Strong.
C3 (summary cold-readability): yes — "branch of bioethics treating moral questions in biomedical and behavioral research with human subjects" is fully accessible; central concerns enumerated; founding documents named with dates.

### N-14 — safety_condition
NODE: Safety Condition [safety_condition, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — brief (251 chars) but functional: contrasts safety with sensitivity ("would you still believe p if p were false?" vs "could you easily have believed p falsely?"), names what safety handles that sensitivity does not (skeptical-closure puzzles). Compact but functional foothold; same shape as N-2 above.
C3 (summary cold-readability): yes — "modal condition on knowledge" — modal is technical but immediately demonstrated by the formal counterfactual ("in nearby possible worlds where S forms the belief that p, p is true"). Brief but the formula carries it. Borderline-PASS, same calibration as N-10 above and shard 14 N-2.

### N-15 — utilitarianism
NODE: Utilitarianism [utilitarianism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Bentham 1789 founding ("everybody to count for one"); Mill 1861 quality-not-just-quantity refinement; ACT vs RULE distinction with defenders; classical objections (trolley / experience machine / demands of utilitarianism) each named with provenance. Strong.
C3 (summary cold-readability): yes — "the right action is the one that maximizes overall utility — typically interpreted hedonically (Bentham, Mill — pleasure minus pain) or in terms of preference-satisfaction"; founding works dated; ACT/RULE/HEDONIC/PREFERENCE four-fold variation enumerated.

### N-16 — moral_non_naturalism
NODE: Moral Non-Naturalism [moral_non_naturalism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Moore's 1903 OPEN-QUESTION ARGUMENT walked through with its generalization step; Parfit 2011 sophisticated defense; the epistemological challenge framed (how do we have access to non-natural properties?); Ross 1930 Mooreanism as the prima-facie-duty extension; standard critique (intuitionism is mysterious / circular). Strong.
C3 (summary cold-readability): yes — "moral properties are SUI GENERIS — irreducibly moral, not identical to or reducible to any natural (descriptive, empirical) property" — sui generis is Latin/jargon but immediately glossed by the "irreducibly moral, not identical to or reducible to" continuation; Moore 1903 + Parfit 2011 dated.

### N-17 — bayesianism_confirmation
NODE: Bayesian Confirmation Theory [bayesianism_confirmation, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks through the framework (priors → evidence → posterior via Bayes's theorem with the formula spelled out); shows specifically how it solves H-D's problems (irrelevant conjunctions wash out; strength problem dissolves into degrees); names connections to epistemology / decision theory / cognitive science; identifies open difficulties (priors / old evidence / logical omniscience). Strong.
C3 (summary cold-readability): yes — borderline-PASS. "Bayesian conditionalization" is jargon, immediately glossed by the formula "P(H|E) > P(H)"; "H-D account" is named but tagged as something supplanted, so its specifics aren't load-bearing. The structural-shape (probability raised by evidence = confirmation) is the gist a cold reader extracts. Same calibration as N-10, N-14 — load-bearing technical terms gated through a formal definition that supplies the working content.

### N-18 — propositional_logic
NODE: Propositional Logic [propositional_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — atomic-letters → five connectives with truth-tables → validity / satisfiability / entailment definitions → syntax/semantics distinction → proof system + soundness + completeness. The full pedagogical entry-point scaffold for formal logic. Strong.
C3 (summary cold-readability): yes — "the simplest formal logic: sentences (atomic propositions) combined by truth-functional connectives (negation, conjunction, disjunction, material conditional, biconditional)" — all five connectives named in plain English; "truth-functional" is technical but immediately glossed by "fully determined by the truth values of its atomic constituents." Borderline-PASS, same calibration as N-10 / N-17.

### N-19 — incompatibilism
NODE: Incompatibilism [incompatibilism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — van Inwagen 1983 Consequence Argument laid out in four numbered steps; compatibilist response paths identified (object at step 3 OR analyze "power over" compatibly); restated motivating intuition. Compact but well-shaped.
C3 (summary cold-readability): yes — "free will is incompatible with determinism — that if the past plus the laws fix everything we do, we are not free" plus the "could have done otherwise" gloss; libertarian / hard-determinist split named.

### N-20 — motivational_externalism
NODE: Motivational Externalism [motivational_externalism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Brink 1989 amoralist case as the canonical contemporary statement; real-world moral-failure cases (depression, weakness of will, sociopathy) framed as the motivating data; Smith 1994 internalist response named; structural implication for moral psychology articulated. Strong.
C3 (summary cold-readability): yes — "the connection between sincere moral judgment and motivation is CONTINGENT, not necessary"; named defenders (Brink 1989 / Svavarsdóttir 1999 / Kantian rationalists) with their respective frames.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0
- Defensible: 1 (E-25 existence → relation — co-fundamental categories rather than ordered prerequisite)
- Audit-touched: 2 (E-16 SCI-E-4 0062 direction-flip; E-17 LAN-E-3 0064 retain-with-annotation), both Sound on audit-validated direction

## Cross-cutting observations

**"Position → its rejection" cluster.** Four edges this shard run the same shape — a position introduced as prerequisite to the position that explicitly rejects/denies it (E-11 bivalence_principle → fuzzy_logic, E-13 epistemic_closure → closure_denial, E-22 certainty → fallibilism, E-26 justified_true_belief → knowledge_first_epistemology). Highest concentration of this sub-shape in the routine batch so far (prior shards 11–15 carried 0–1 instances each). The shape is the canonical pedagogical move "introduce the standard, then introduce the deviant via what it gives up" — uniformly Sound here, but the four-in-one density is worth flagging for the SQA-20 closeout's sub-shape inventory.

**Three-edge framework-component repeat.** four_principles_bioethics → beneficence (E-2) / autonomy_bioethical (E-10) / non_maleficence (E-20) is a three-edge concentration from one source covering three of the four Beauchamp & Childress principles (the fourth, justice, is presumably in another shard). All Sound on the framework-introduces-its-N-components shape, but the three-from-one-source density is the densest framework-decomposition cluster in the routine batch's sample (most prior shards carry 0–1 framework-decomposition edges per source).

**Co-fundamental-category Defensible (E-25).** The shard's only Defensible — existence → relation — is a new sub-shape for the routine batch: two co-fundamental metaphysical categories carrying a prerequisite edge in either direction. Distinct from the framework→concept Defensibles (shard 13 E-15, shard 14 E-17), distinct from the canonical-direction-inversion Defensibles (shards 14/15's 0064 retain-with-annotation cluster). Worth a SQA-20 calibration pass on whether co-fundamental category-pair edges should carry prerequisites at all, or whether they're better modeled as parallel topics (validator surface for `category_pair_prereq` candidate, deferrable).

**SEVEN consecutive 0-defect shards.** Shards 10/11/12/13/14/15/16 all 0/27. C1 cumulative across 01–16 = 23/434 = 5.30% (was 5.65% at shard 15), continuing the steady tick DOWN under the production-audit's 13% baseline. The 0-defect run is the longest consecutive sequence in the census (prior longest was three at shards 06–07 + 09–10). Composition-driven: the pre-sharding random sample is hitting the audit-cleaned regions of the graph; the production-audit's 13% baseline was a single-pass metric over the full 516 edges, so a 5.30% rate over 434 of those (84% of the population) materially below 13% is the genuine "audit follow-up migrations 0061–0064 + 0065 took the rate down" signal.

**Audit cross-reference workflow.** Two genuine audit-touched edges, both detected via inline `evidence` text (the canonical cleanest signal — the exact-tuple comparison against assertion-block lists confirmed both, no proximity false-positives this shard). The 0060 cross-bridges-original-authoring filter (per shard 14/15 false-positive learnings) was applied; no 0060 edges scanned. The shard 14 + 15 workflow note holds: when an edge carries inline `evidence` text quoting the audit decision, that's the gold signal — no need to chase proximity hits without it. Recorded for the SQA-20 aggregation.
