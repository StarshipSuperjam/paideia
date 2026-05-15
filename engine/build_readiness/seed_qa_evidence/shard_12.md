# Seed-graph QA census evidence — shard 12

> Authored by S-0174 (routine session) per T-SEED-QA task SQA-12.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 12
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — art → institutional_theory_of_art
EDGE: Art [art, aesthetics] → Institutional Theory of Art [institutional_theory_of_art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Dickie's institutional theory (1974) is a specific theory of what art is — works of art are those things conferred the status by the artworld practice. Art is the topic; the institutional theory is one particular analysis of it. Standard topic → theory shape.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-2 — meaning → sense_and_reference
EDGE: Meaning (Linguistic) [meaning, language] → Sense and Reference (Sinn und Bedeutung) [sense_and_reference, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Frege's 1892 Sinn/Bedeutung distinction is the paradigm structural analysis of linguistic meaning — the morning-star / evening-star puzzle motivates positing sense in addition to reference. Meaning is the topic; sense/reference is the foundational Fregean analysis. Topic → analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — propositional_knowledge → justified_true_belief
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Justified True Belief [justified_true_belief, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: JTB IS the canonical (pre-Gettier) analysis of propositional knowledge — S knows that p iff S has a justified true belief that p. Propositional knowledge is the analysandum; JTB is the proposed analysans. Topic → analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-4 — substance → bundle_theory
EDGE: Substance [substance, metaphysics] → Bundle Theory [bundle_theory, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bundle theory (Hume, Russell, more recently Paul, Robb) is a substantive theory of what a substance/object IS — a bundle of co-instantiated properties (or tropes, depending on the variant) rather than a property-bearing substratum. Substance is the umbrella metaphysical category; bundle theory is one analysis. Umbrella → analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — tropes → bundle_theory
EDGE: Tropes [tropes, metaphysics] → Bundle Theory [bundle_theory, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The trope-bundle theory of substance (D.C. Williams 1953, Campbell 1990) takes tropes as the ontological building blocks — a particular is a bundle of compresent tropes. On the trope-bundle reading the direction is Sound (tropes is the component-prereq for trope-bundle theory). But the more general bundle theory of substance (Hume's bundle theory of mind used impressions/ideas; Russell's used universals) does NOT require tropes — universal-bundle and trope-bundle are alternative ontologies of the bundle constituents. So tropes is a prereq for ONE version of bundle theory but not for bundle theory in general. Defensible on the trope-version reading; not Reversed because the conceptual dependency genuinely runs that way for the trope-bundle variant; not strictly Weak-redundant because bundle theory in the trope-variant really does need the tropes concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-6 — vienna_circle_logical_positivism → behaviorism_logical
EDGE: Vienna Circle and Logical Positivism [vienna_circle_logical_positivism, service] → Logical Behaviorism [behaviorism_logical, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Logical behaviorism (Carnap 1932 "Psychology in Physical Language", Hempel 1949 "The Logical Analysis of Psychology", Ryle 1949 The Concept of Mind) is the philosophy-of-mind application of Vienna Circle verificationism: mental-state ascriptions must be reducible to behavioral predicates because behavior is the only publicly verifiable evidence. The conceptual lineage from Vienna Circle (verificationism, logical empiricism, anti-mentalism) to logical behaviorism is direct historical and conceptual succession.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-7 — kripke_semantics → conditional_logic
EDGE: Kripke Semantics [kripke_semantics, logic] → Conditional Logic [conditional_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Stalnaker (1968) and Lewis (1973) developed conditional logic — the formal logic of counterfactual conditionals — as an extension of Kripke-style modal apparatus. The framework adds a similarity ordering or selection function on top of Kripke frames (worlds + accessibility). Kripke semantics is the foundational model-theoretic framework; conditional logic is one extension/application. Foundation → application.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-8 — epistemic_justification → externalism_epistemic
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Epistemic Externalism [externalism_epistemic, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Externalism (Goldman's reliabilism, Plantinga's proper-functionalism, Nozick's tracking theory) is a position about what justification consists in — externalist accounts hold that some justification-conferring factors lie outside the believer's reflective access. Justification is the topic; externalism is one substantive stance. Topic → theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-9 — evidence → problem_of_induction
EDGE: Evidence [evidence, epistemology] → Problem of Induction [problem_of_induction, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Hume's problem of induction is the question of whether evidence drawn from past instances can rationally justify belief about future or unobserved instances. The problem is FORMULATED in terms of evidence — without grasping what evidence is and how it is supposed to support belief, the problem cannot be articulated. Component-prereq.
AUDIT-TOUCHED: none. Cross-reference: 0062's direction-flip touched `pyrrhonian_skepticism → problem_of_induction` (a different edge whose target is problem_of_induction); the shard-12 edge `evidence → problem_of_induction` has a different source and was untouched by the audit migrations.
EVIDENCE NOTE: absent

### E-10 — phenomenal_consciousness → hard_problem_of_consciousness
EDGE: Phenomenal Consciousness [phenomenal_consciousness, mind] → Hard Problem of Consciousness [hard_problem_of_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Block's phenomenal/access consciousness distinction (1995) and the prior phenomenal-consciousness tradition (Nagel 1974 "What is it like to be a bat?") are the conceptual ground on which Chalmers's 1995 hard problem is articulated — the hard problem is specifically the problem of phenomenal consciousness (why physical processes give rise to subjective experience at all), distinguished from the "easy problems" of cognitive function. Phenomenal consciousness is the conceptual prereq for the hard-problem framing.
AUDIT-TOUCHED: none. (The related S-0122 edge `explanatory_gap → hard_problem_of_consciousness`, audit-touched in 0062, addresses the Levine-1983 priority over Chalmers; the present edge captures a different conceptual prereq pathway from phenomenal consciousness itself.)
EVIDENCE NOTE: absent

### E-11 — formal_proof → classical_logic
EDGE: Formal Proof [formal_proof, service] → Classical Logic [classical_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Two readings disagree on the direction. (a) PEDAGOGICAL reading: students typically learn classical logic first — propositional, then predicate, with modus ponens and natural-deduction proof-rules — and only later abstract to "formal proof" as a general syntactic-derivation concept across logical systems (intuitionistic, modal, relevance). On this reading the edge runs opposite to pedagogical succession (classical-logic → formal-proof would match). (b) STRUCTURAL reading: formal proof is the umbrella syntactic-derivation primitive (any sequence of formulas justified by axioms / assumptions / inference rules); classical logic is one specific proof system that instantiates it. On this reading, the abstract notion of formal proof is conceptually prior to the specific system. The seed-graph appears to take the structural-priority reading consistently (umbrella concept → specific instance), as the formal_proof node summary explicitly frames formal proof as "the syntactic-derivation primitive of formal logic" — i.e., the general concept. Defensible on the structural-priority reading; same shape as shards 05–11's "target is the more pedagogically-familiar concrete concept" calibration question for the SQA-20 closeout.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-12 — deontology → supererogation
EDGE: Deontology [deontology, ethics] → Supererogation [supererogation, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Supererogation (acts above and beyond duty — Urmson 1958 "Saints and Heroes") presupposes a notion of duty/obligation, which is the central concept of deontological ethics (Kant, Ross). Although Urmson framed supererogation as a problem for any moral theory with a notion of obligation, the standard pedagogical introduction to supererogation comes through deontological frameworks where duty is primary. Framework → category-that-presupposes-framework. (See E-26 for the broader normative-ethics dependency — both edges encode distinct framework-prereqs.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — deductive_nomological_model → inference_to_the_best_explanation
EDGE: Deductive-Nomological Model of Explanation [deductive_nomological_model, science] → Inference to the Best Explanation [inference_to_the_best_explanation, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: DN (Hempel-Oppenheim 1948, Hempel 1965) and IBE (Harman 1965 "The Inference to the Best Explanation", Lipton 1991/2004) are two distinct theories of scientific explanation, often presented as RIVALS or complementary accounts addressing different aspects (DN is covering-law-deductive; IBE is abductive-qualitative). Conceptually, IBE does not strictly PRESUPPOSE DN — you can teach IBE as the abductive-reasoning paradigm without first teaching DN as the deductive-paradigm. Historically and dialectically, however, DN dominated philosophy of science from 1948 to the 1970s and IBE was developed partly in response to recognized DN-limitations; the standard textbook sequence places DN before IBE. Defensible on the historical-and-dialectical-succession reading; the conceptual-prereq reading is weak. Not strictly Weak-redundant (no obvious more-proximate prereq in the graph). Recorded as a "two parallel theories of X, one historically prior" shape — flagged for closeout pattern-analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-14 — intentionality → meaning
EDGE: Intentionality [intentionality, mind] → Meaning (Linguistic) [meaning, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Brentano's thesis (1874): intentionality (aboutness) is the mark of the mental — mental states are about something. The dominant Brentano-Husserl-Searle tradition in philosophy of mind treats mental intentionality as primary and linguistic meaning as derivative (Grice 1957's analysis of speaker-meaning grounds linguistic meaning in speakers' intentional states). The competing language-first tradition (Frege, early Wittgenstein, formal-semantics tradition) treats meaning as primary as a property of public language. The seed-graph encodes the mind-first reading, which is the dominant contemporary analytic pedagogical sequence (the Searle 1983 "derived intentionality of language" framing).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-15 — modus_tollens → falsificationism
EDGE: Modus Tollens [modus_tollens, service] → Falsificationism [falsificationism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Popper's falsificationism is the application of modus tollens to scientific theory testing: theory T predicts observation O; ¬O is observed; therefore ¬T. The N-20 modus_tollens teaching_notes (this shard) explicitly frame this connection: "modus tollens is pedagogically the bridge from elementary deductive reasoning to scientific reasoning: it captures the core logical structure of falsificationist scientific testing per Popper." Inference rule → philosophical application. Clean component-prereq.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-16 — social_epistemology → epistemic_injustice
EDGE: Social Epistemology [social_epistemology, epistemology] → Epistemic Injustice [epistemic_injustice, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Miranda Fricker's Epistemic Injustice (2007) — testimonial injustice (prejudice deflates a speaker's credibility) and hermeneutical injustice (gaps in shared interpretive resources prevent a knower from making sense of their experience) — operates within the social-epistemology framework where knowers are situated social agents and knowledge is distributed across testimony networks. Framework → specific account within framework.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-17 — reference → sense_and_reference
EDGE: Reference [reference, language] → Sense and Reference (Sinn und Bedeutung) [sense_and_reference, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Frege's 1892 sense/reference distinction is HIS analysis of reference (and meaning) — distinguishing the mode of presentation (sense) from the object referred to (reference). Reference is the topic the analysis addresses; sense/reference is the Fregean two-tiered structural treatment. Topic → analysis. (Companion edge to E-2 meaning → sense_and_reference; the two encode distinct prereq pathways into the Fregean apparatus.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — deontology → kantian_ethics
EDGE: Deontology [deontology, ethics] → Kantian Ethics [kantian_ethics, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kantian ethics is the paradigm deontological theory — duty-centered, with the categorical imperative as the procedural test for action-permissibility. Deontology is the categorial umbrella; Kantian ethics is the specific instance within it. The standard seed-graph categorial-first pattern (umbrella ethical-theory-type → specific instance) — same shape as shard 10's E-19 `reductionism_in_science → multiple_realizability_in_science` (broader thesis → specific instance), held at Sound. Historically Kant precedes the term "deontology" (coined later by Bentham, refined in 20th-century meta-ethics), but the seed-graph encodes conceptual umbrella-first prereq structure, not historical chronology — consistent calibration across the census.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — probability_mathematical → expected_value
EDGE: Probability (Mathematical) [probability_mathematical, service] → Expected Value [expected_value, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Expected value is defined in terms of probability: E[X] = Σ x·P(X=x) for discrete distributions, ∫ x·f(x) dx for continuous. Probability is the formal apparatus; expected value is constructed from it. Pure component-prereq.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-20 — existence → event
EDGE: Existence [existence, metaphysics] → Event [event, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Events are entities that exist (the explosion, the meeting, the storm); to take events as a metaphysical category is to take a stance on what kinds of things exist. Existence is the prior concept presupposed by any ontological category. Same shape as shard 10's E-15 `existence → causation`, held at Sound. Component-prereq.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-21 — knowledge → social_epistemology
EDGE: Knowledge [knowledge, epistemology] → Social Epistemology [social_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Social epistemology applies epistemological concepts (knowledge, justification, evidence, testimony) to socially-situated knowers and group cognition. Knowledge is the foundational concept; social epistemology is a subfield investigating its social dimensions (testimony, peer disagreement, group belief, epistemic dependence). Topic → specialization.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-22 — social_epistemology → epistemic_dependence
EDGE: Social Epistemology [social_epistemology, epistemology] → Epistemic Dependence [epistemic_dependence, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Epistemic dependence (Hardwig 1985 "Epistemic Dependence on Experts", Goldberg 2010) — the phenomenon that we depend cognitively on others for most of what we know (testimony, division of cognitive labor, expert deference) — is a central phenomenon studied within social epistemology. Framework → specific phenomenon within framework.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-23 — scientific_theory → scientific_realism
EDGE: Scientific Theory [scientific_theory, science] → Scientific Realism [scientific_realism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Scientific realism is the position that scientific theories aim at and (in mature science) approximately succeed in describing a mind-independent reality, including unobservable entities posited by theory. Scientific theory is the prereq concept — the position is articulated as a stance ABOUT theories. Topic → metatheoretic position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-24 — belief → credence
EDGE: Belief [belief, epistemology] → Credence [credence, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Credence (subjective probability, degree of belief — Ramsey 1926, de Finetti 1937, Jeffrey 1965) is a graded refinement of binary belief, mapping doxastic states onto the [0,1] interval. The standard pedagogical sequence introduces the folk notion of belief first, then refines to credence as the formal apparatus. Topic → refinement. (Some radical Bayesians treat credence as primary and binary belief as derivative; on that reading the direction is contested, but the standard pedagogical direction is belief-first.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-25 — modality → possible_worlds
EDGE: Modality [modality, metaphysics] → Possible Worlds [possible_worlds, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Possible worlds (Lewis's modal realism, Kripke's quantified modal logic, Plantinga's actualist possible-world theory, Stalnaker's pragmatist treatment) are the canonical model-theoretic apparatus for analyzing modal claims (necessity, possibility, counterfactuals). Modality is the topic — students grasp "could have" / "must" pre-philosophically — possible worlds is one (very influential) formal analysis. Topic → analysis. (Note: my crude grep cross-reference flagged 0064 as touching this edge because that migration backfilled evidence for `abstract_object → possible_worlds` and `modality → essence_metaphysical` separately — but no edge with this exact tuple was touched. Recorded as not-audit-touched.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-26 — normative_ethics → supererogation
EDGE: Normative Ethics [normative_ethics, ethics] → Supererogation [supererogation, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Supererogation as a category arises in any ethical framework that distinguishes obligatory / permitted / forbidden acts. Normative ethics is the umbrella that includes this obligation-permission-prohibition framework. Urmson's 1958 "Saints and Heroes" originally framed supererogation as a problem for any normative-ethical theory with a notion of duty, not just deontology. Duplicate-prereq pattern with E-12 (deontology → supererogation) — the two edges encode distinct framework-prereqs (specific deontological theory vs broader normative-ethics umbrella), neither strictly subsumes the other. Not Weak-redundant because the dependency is genuinely distinct from the deontology-specific one; recorded as a "duplicate prereq" observation for closeout pattern-analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-27 — kantian_aesthetic_judgment → free_play_imagination_understanding
EDGE: Kantian Aesthetic Judgment [kantian_aesthetic_judgment, aesthetics] → Free Play of Imagination and Understanding [free_play_imagination_understanding, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The free play of imagination and understanding (Kant, Critique of the Power of Judgment §§9, 35) is Kant's specific cognitive-mechanistic account of WHAT pure aesthetic judgment consists in — the harmonious but non-determinate engagement of imagination and understanding in response to a beautiful object. Kantian aesthetic judgment is the broader topic (Kant's theory of aesthetic judgment as such); free play is the specific cognitive mechanism within it. Topic → specific account.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

## Node findings (C2 + C3)

### N-1 — physicalism
NODE: Physicalism [physicalism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give structured taxonomy (type vs token, anomalous monism, contemporary non-reductive functionalism), name the central objections (Mary, zombies, multiple realizability), and surface the umbrella-vs-particular-theory distinction explicitly.
C3 (summary cold-readability): yes — summary defines the thesis clearly ("everything is physical: every concrete particular is a physical particular; every property either is a physical property or is grounded in physical properties; minds are not exceptions") and names the differentiation into named sub-positions. Cold reader gets the thesis and the position-landscape.

### N-2 — mereology
NODE: Mereology [mereology, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes distinguish formal theory from metaphysical-of-composition disputes, name canonical positions (nihilism per van Inwagen, non-extensional per Fine/Koslicki), give the statue-and-clay example, and explicitly recommend the pedagogical entry point.
C3 (summary cold-readability): yes — opens with "The formal theory of parts and wholes," names the axiomatic foundation (transitivity, reflexivity, supplementation) with the historical anchors (Lesniewski, Goodman-Leonard). Some technical vocabulary but the conceptual core is clearly stated.

### N-3 — formal_proof
NODE: Formal Proof [formal_proof, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes contrast informal and formal proofs explicitly, name three formalisms (Hilbert-style, natural-deduction, sequent-calculus), describe each, recommend the pedagogically-friendliest, and surface the deep results (Gödel, Curry-Howard, soundness-completeness) as gateway destinations.
C3 (summary cold-readability): yes — borderline. Summary names the concept structurally ("syntactic-derivation primitive of formal logic: a finite sequence of formulas where each formula is either an axiom, an assumption, or follows by an inference rule") and the soundness-completeness anchor. "Inference rule" is unglossed in the summary but the structural shape (axiom-or-assumption-or-rule-application sequence) is independently parsable. The teaching_notes do the heavy gloss-work; the summary stands on its own at borderline-PASS. Flagged for closeout consistency review alongside shard 11's N-3 IIT and shard 10's N-3 fuzzy_logic borderlines.

### N-4 — representational_theory_of_mind
NODE: Representational Theory of Mind [representational_theory_of_mind, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give the classical computational picture clearly, name standard objections (connectionist, eliminativist, semantic-deflationist) and named figures, connect to functionalism and philosophy of language.
C3 (summary cold-readability): yes — clear summary: "mental states are relations to mental representations — internal symbol-like structures that have semantic content and are processed computationally"; gives the canonical concrete example ("to believe that snow is white is to bear the belief-relation to a mental representation that means snow is white"). The concrete example does substantial gloss-work for "mental representation" and "computational."

### N-5 — inference_rule
NODE: Inference Rule [inference_rule, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes explicitly bridge semantic and syntactic reasoning, name modus ponens as the canonical worked example, recommend natural-deduction as pedagogically friendliest, surface the soundness-completeness anchor.
C3 (summary cold-readability): yes — clear: "rule that licenses the derivation of one or more conclusion-formulas from one or more premise-formulas based purely on the syntactic shape of those formulas." Lists familiar examples (modus ponens, modus tollens, hypothetical syllogism, etc.). Cold reader gets the concept.

### N-6 — aesthetic_value
NODE: Aesthetic Value [aesthetic_value, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give three structured pedagogical axes (experiential/property-based; intrinsic/instrumental; pluralist/monist), name positions and authors for each, locate the autonomy-of-aesthetic-value debate at the intersection.
C3 (summary cold-readability): yes — opens with concrete examples (beautiful sunset, elegant proof, moving symphony, graceful performance) that anchor the abstract category; distinguishes from neighboring value species; surfaces the central question.

### N-7 — function_mathematical
NODE: Function (Mathematical) [function_mathematical, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes systematically distinguish relation / function / total-function, name the property classification (injective / surjective / bijective), enumerate applications across logic / type theory / probability / lambda calculus.
C3 (summary cold-readability): yes — gives both the formal definition ("relation that associates each element of a domain set with exactly one element of a codomain set") and the everyday gloss ("rule that takes an input and produces an output"); explicitly disambiguates from other senses of "function" used elsewhere in philosophy. Cold reader gets the mathematical-function concept.

### N-8 — duhem_quine_thesis
NODE: Duhem-Quine Thesis [duhem_quine_thesis, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes walk through the thesis carefully (Duhem's physics-specific point, Quine's generalization), enumerate four major implications (falsification-defect, underdetermination, analytic/synthetic collapse, confirmational holism), name the "web of belief" image.
C3 (summary cold-readability): yes — clear opening ("hypotheses are tested only as parts of larger theoretical wholes: a single hypothesis cannot be falsified in isolation because any apparent falsification can be located in auxiliary assumptions"); names the canonical articulation (Duhem 1906) and the generalization (Quine 1951); identifies the position-name (confirmational holism) and its target (Popperian falsificationism).

### N-9 — libertarianism_political
NODE: Libertarianism (Political) [libertarianism_political, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes very detailed: foundational commitments laid out, Wilt Chamberlain argument walked through, right vs left libertarian distinction surfaced with named figures, principal objections enumerated.
C3 (summary cold-readability): yes — long but readable: opens with the conceptual framing (individual liberty + natural rights → minimal state), names the canonical contemporary statement (Nozick 1974), walks through the entitlement theory, defines the night-watchman state, distinguishes from libertarianism about free will at the end.

### N-10 — sensitivity_condition
NODE: Sensitivity Condition [sensitivity_condition, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes short but substantive: surface the closure-failure feature, name the post-Nozick safety-condition alternative, point to the trade-off.
C3 (summary cold-readability): yes — borderline. Summary states the condition cleanly with the counterfactual ("S's belief that p is sensitive iff in the nearest possible world where p is false, S does not believe p") and gives the intuitive gloss ("knowledge tracks truth across counterfactual variation"). "Possible world" appears unglossed but the conjunction "nearest possible world where p is false" is parsable on a cold reading because of the counterfactual rephrasing. PASS at borderline.

### N-11 — deflationary_theory_of_truth
NODE: Deflationary Theory of Truth [deflationary_theory_of_truth, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes walk through Ramsey's observation, Quine's disquotational schema, Horwich's minimalism, and the critic-response dialectic. Concrete examples (the infinite-conjunction case, the hypothetical-truth-without-specifying-the-sentence case) anchor the abstract minimalist move.
C3 (summary cold-readability): yes — opening sentence is clear ("predicate 'is true' has no substantive philosophical analysis: it is a logical or quasi-logical device, not a name for a metaphysically loaded property"); contrasts with named substantive theories (correspondence, coherence, pragmatist) and lists the major deflationist versions (redundancy, disquotational, prosentential, minimalism) with named figures.

### N-12 — demarcation_problem
NODE: Demarcation Problem [demarcation_problem, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give Popper's motivation with concrete contrast (Einstein's bending-of-starlight vs Marxist / Freudian explanatory totalism), surface three technical problems with falsifiability (holism, save-by-auxiliary, Laudan's cluster argument), point to the contemporary practical view.
C3 (summary cold-readability): yes — clear: "the problem of distinguishing genuine science from non-science (or pseudo-science)"; identifies Popper as the central historical figure; gives Popper's solution; lists concrete contemporary applications (astrology, parapsychology, intelligent-design, climate-change denial).

### N-13 — technology_ethics
NODE: Technology Ethics [technology_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes are very detailed and structured: four major currents enumerated (philosophy of technology, computer/information ethics, engineering ethics, applied issues), each with named figures and works; cross-bridges to bioethics / environmental ethics / political philosophy surfaced.
C3 (summary cold-readability): yes — long, but readable: opens with structural framing ("branch of applied ethics treating moral questions arising from..."), lists concrete topics (privacy, algorithmic decision-making, intellectual property, attention-economy, biotech, autonomous systems, cybersecurity, digital divide, dual-use research), gives historical anchors (Heidegger 1954, Mumford, Ellul, Floridi 1990s, Wiener 1950).

### N-14 — chinese_room_argument
NODE: Chinese Room Argument [chinese_room_argument, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes walk through the argument structure step-by-step (five-step reconstruction), name the three standard replies (Systems, Robot, Brain Simulator) and Searle's rebuttal-stance, anchor the contestation in subsequent literature.
C3 (summary cold-readability): yes — excellent: describes the thought experiment concretely (monolingual English speaker, Chinese characters, rulebook), states the conclusion clearly ("syntax does not suffice for semantics; running the right program does not produce understanding"). One of the most cold-reader-friendly summaries in the shard.

### N-15 — character_and_content
NODE: Character and Content (Two-Dimensional Semantics) [character_and_content, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes walk through Kaplan's two-stage setup in detail (character as function from contexts to contents; content as proposition once context is supplied), give the "I" worked example concretely, surface two key formal results (direct reference; rigidity prediction), point to broader applications.
C3 (summary cold-readability): yes — borderline. Summary opens with technical vocabulary load ("two-dimensional framework for handling indexical and demonstrative expressions"), then defines character and content abstractly. The "I" example in the summary itself ("'I' has a constant character (the speaker of the context) and contents that vary across contexts") rescues the cold reader — after the example the abstract definitions retroactively parse. PASS at borderline; similar shape to N-16 below where a load-bearing technical term gets glossed via concrete example.

### N-16 — externalism_epistemic
NODE: Epistemic Externalism [externalism_epistemic, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes short but substantive: name the motivation (epistemic legitimacy of cognitively unsophisticated agents; difficulty meeting internalist conditions for perceptual knowledge), name the canonical objection (new-evil-demon).
C3 (summary cold-readability): yes — borderline. Two sentences. First sentence uses "justification-conferring factors" and "reflective access" as jargon but glosses the position via "typically the reliability of the belief-forming process" — the gloss does the rescue. Second sentence lists positions (reliabilism per Goldman; tracking and proper-function theories) without elaborating them. PASS — the gloss is inline within the same sentence, which is the calibration the rubric demands.

### N-17 — political_philosophy
NODE: Political Philosophy [political_philosophy, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give the authority question as the opening framing, name canonical distinctions (justice vs other values; state vs other institutions; rights vs interests vs preferences; ideal vs nonideal theory), surface the three traditions (social-contract, natural-law, consequentialist), distinguish from ethics structurally.
C3 (summary cold-readability): yes — clear: "branch of philosophy concerned with the legitimate uses of collective coercive power, the moral foundations of political institutions, and the principles that should govern social life." Distinguishes from political science (descriptive); enumerates central questions concretely.

### N-18 — moral_responsibility
NODE: Moral Responsibility [moral_responsibility, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give Strawson's reactive-attitudes analysis, Pereboom's hard-incompatibilist alternative, and the metaphysical/practical-question disjunction explicitly.
C3 (summary cold-readability): yes — clear: "metaphysical conditions under which an agent is appropriately held accountable — praiseworthy or blameworthy — for an action"; names the three position-clusters (compatibilist per Frankfurt/Fischer-Ravizza, libertarian per Kane, skeptical per Pereboom/Caruso) and surfaces the free-will-debate framing.

### N-19 — art
NODE: Art [art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give three structured pedagogical axes (intrinsic vs relational; extensional adequacy via avant-garde test cases; functional vs procedural), name positions and authors, surface the shape of the contemporary debate.
C3 (summary cold-readability): yes — concrete: opens with concrete examples of artwork-kinds (paintings, sculptures, musical compositions, novels, poems, films, performances, photographs, installations, conceptual works); states the central philosophical question; lists the canonical account-types (imitation, expression, formalism, institutional, historical, anti-essentialist).

### N-20 — modus_tollens
NODE: Modus Tollens [modus_tollens, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — teaching_notes give the pedagogical bridge to scientific reasoning (Popper falsification), surface the Duhem-Quine caveat, walk through schematic / concrete / scientific-testing instances, pair with the denying-the-antecedent fallacy.
C3 (summary cold-readability): yes — clean: "from 'if P then Q' and 'not Q', derive 'not P'"; gives the Latin etymology gloss ("method of denying"); pairs with modus ponens and distinguishes from the denying-the-antecedent fallacy.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 0 (0.0%) | teaching_notes ABSENT 0

## Cross-cutting observations (optional)

Shard 12 is a clean fresh-authoring drift check: **zero audit-touched edges** in the canonical S-0122 follow-up migrations 0061–0065 (the lowest audit footprint in the routine batch so far; vs shard 11's 5/27 = 18.5% and shard 10's 2/27 = 7.4%). Any C1 finding here is fresh authoring, not a re-opening of an audit decision. The 0% C1 defect rate is therefore an especially clean signal.

Two patterns flagged for closeout pattern-analysis:

- **E-11 `formal_proof → classical_logic`** instantiates the "target is the more pedagogically-familiar concrete concept" shape (eighth consecutive shard, after shards 05–11). The structural-priority reading (formal_proof as umbrella concept; classical_logic as instance) saves the direction at Defensible per established calibration, but the pedagogical-priority reading runs opposite (students learn classical-logic before "formal proof" as an abstract notion). Continued data for the SQA-20 rubric-calibration question.

- **Duplicate prereq pattern: E-12 + E-26 → supererogation**. Two distinct framework-prereqs for the same target (deontology specifically and normative_ethics broadly). Neither edge is strictly Weak-redundant of the other — they encode distinct dependency pathways — but the seed-graph carries both. First instance of this duplicate-prereq shape encountered in the routine batch; flag for closeout consistency review (does the graph systematically carry both specific-theory and broader-category prereq pathways for ethical-concept targets, or is this a one-off?).
