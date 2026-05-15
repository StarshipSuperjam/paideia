# Seed-graph QA census evidence — shard 14

> Authored by S-0176 (routine session) per T-SEED-QA task SQA-14.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 14
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — credence → bayesian_epistemology
EDGE: Credence [credence, epistemology] → Bayesian Epistemology [bayesian_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: A credence is a real-valued degree of belief; Bayesian epistemology is the framework that uses credences (plus the probability axioms and conditionalization) as its central representational apparatus. The conceptual building block must precede the framework that operates on it. Concept → framework-built-on-concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-2 — classical_logic → fuzzy_logic
EDGE: Classical Logic [classical_logic, logic] → Fuzzy Logic [fuzzy_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Fuzzy logic (Zadeh 1965) is presented as a generalization of classical logic with degree-valued rather than two-valued truth assignments. Students need classical logic first to understand what fuzzy logic departs from (bivalence) and what it preserves (truth-functional connectives, extended naturally). Standard system → generalization-of-the-system.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — sorites_paradox → fuzzy_logic
EDGE: Sorites Paradox [sorites_paradox, logic] → Fuzzy Logic [fuzzy_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The sorites paradox (gradually adding grains to a heap; gradually decreasing baldness) is one of the principal motivating problems for fuzzy logic — degrees of truth handle the vague predicates that bivalent logic struggles with. Motivating-problem → formal-solution; same shape as E-24 (sorites_paradox → supervaluationism) below.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-4 — meaning → indexical
EDGE: Meaning (Linguistic) [meaning, language] → Indexical Expression [indexical, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Indexicals (Kaplan 1989) are expressions whose meaning includes a context-sensitive component — their reference depends on context of utterance. The general notion of linguistic meaning must precede the technical class of expressions whose meaning has a distinctive context-sensitivity. General concept → specific subclass.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — epistemic_justification → reliabilism
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Reliabilism [reliabilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reliabilism (Goldman 1979) is a theory of epistemic justification — a belief is justified iff produced by a reliable belief-forming process. The explanandum (justification) must precede the theory (reliabilism). Standard concept → theory-of-the-concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-6 — vienna_circle_logical_positivism → verificationism
EDGE: Vienna Circle and Logical Positivism [vienna_circle_logical_positivism, service] → Verificationism [verificationism, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Verificationism (the verifiability criterion of meaningfulness) was the central technical doctrine of the Vienna Circle and logical positivism — the node summary for the Vienna Circle explicitly names verifiability as "the central technical doctrine." Pedagogically, the movement is introduced first as historical-context (1920s-1930s Vienna; Schlick, Carnap, Neurath; the Tractatus reading), then verificationism enters as the doctrine that movement most distinctively defended. Movement-historical-context → its-central-doctrine.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-7 — environmental_ethics → biocentrism
EDGE: Environmental Ethics [environmental_ethics, ethics] → Biocentrism [biocentrism, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Biocentrism (Taylor 1986) is a specific position within environmental ethics — moral standing extends to all living individuals. The discipline-and-its-positions structure puts the discipline first (environmental ethics as the field) and specific normative positions second. Same calibration as shard 12 E-18 deontology → kantian_ethics (umbrella → specific instance, Sound).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-8 — aesthetic_property → formalism_artistic
EDGE: Aesthetic Property [aesthetic_property, aesthetics] → Formalism (Artistic) [formalism_artistic, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Formalism (Bell 1914, Greenberg) is the view that aesthetic properties of an artwork are determined by its formal/perceptual features rather than its content, history, or context. The notion of aesthetic property must precede the theory about how aesthetic properties are grounded. Concept → theory-about-the-concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-9 — what_its_like → phenomenal_consciousness
EDGE: What It Is Like (Nagel) [what_its_like, mind] → Phenomenal Consciousness [phenomenal_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nagel's "What Is It Like to Be a Bat?" (1974) is the canonical pedagogical entry point to phenomenal consciousness as a technical philosophical category — the slogan is the framing-question whose answer is "phenomenal consciousness." Standard intro phil-of-mind courses use Nagel's formulation as the doorway before introducing "phenomenal consciousness" as a technical term. Framing-question → concept-named-by-the-question.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-10 — future_generations → intergenerational_justice
EDGE: Future Generations [future_generations, ethics] → Intergenerational Justice [intergenerational_justice, ethics]
  weight=0.95, confidence=0.95, evidence=NULL
VERDICT: Sound
RATIONALE: Intergenerational justice is the political-philosophical problem of what obligations the present generation has to future generations (Parfit 1984 Reasons and Persons; Gosseries; Meyer). Need the notion of future generations as moral patients (and the non-identity problem) first to grasp what intergenerational-justice debates are about. Topic-of-concern → theoretical-framing-of-the-concern.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-11 — propositional_knowledge → tracking_theory_of_knowledge
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Tracking Theory of Knowledge [tracking_theory_of_knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The tracking theory (Nozick 1981 Philosophical Explanations) is a theory of propositional knowledge using sensitivity and adherence subjunctive conditionals (S knows p iff: if p were false, S wouldn't believe p; if p were true, S would believe p). The explanandum (propositional knowledge) must precede the analysis (tracking). Concept → analysis-of-the-concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-12 — metaethics → moral_anti_realism
EDGE: Metaethics [metaethics, ethics] → Moral Anti-Realism [moral_anti_realism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Moral anti-realism is one of the principal positions on the realism-vs-anti-realism axis of metaethics (the question of whether there are mind-independent moral facts). Need the metaethical-question framing first to understand what moral anti-realism is denying. Discipline-question → position-on-the-question.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — hard_problem_of_consciousness → knowledge_argument
EDGE: Hard Problem of Consciousness [hard_problem_of_consciousness, mind] → Knowledge Argument (Mary) [knowledge_argument, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Contemporary phil-of-mind courses typically introduce the hard problem (Chalmers 1995) as the framing question and then present the knowledge argument (Jackson 1982) as evidence for the hard problem's diagnosis. The direction is defensible on the framing-question-before-argument reading. But chronologically Jackson 1982 predates Chalmers 1995, and the knowledge argument can be taught self-containedly (the node's own teaching_notes lay out the four-step structure of the argument without requiring the hard-problem framing). Not Reversed: the framing-first pedagogical convention is real, and the audit cluster of related flips (0062 flipped property_dualism → knowledge_argument to knowledge_argument → property_dualism, and explanatory_gap → hard_problem_of_consciousness; the audit did NOT touch this edge despite touching adjacent edges in the same cluster).
AUDIT-TOUCHED: none — adjacent edges are 0062-touched but this specific edge was not in the 15-edge flip set (verified via tuple comparison against 0062 lines 83–84 assertion blocks).
EVIDENCE NOTE: absent

### E-14 — mental_state → propositional_attitude
EDGE: Mental State [mental_state, mind] → Propositional Attitude [propositional_attitude, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional attitudes (belief that p, desire that p, hope that p) are a class of mental states with content directed at propositions. Genus → species. Same shape as shard 10 E-19 reductionism_in_science → multiple_realizability_in_science and shard 12 E-18 deontology → kantian_ethics (both Sound on calibration).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-15 — inference_rule → predicate_logic
EDGE: Inference Rule [inference_rule, service] → Predicate Logic [predicate_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: An inference rule is a structural rule for moving from premises to conclusion (modus ponens, universal instantiation). Predicate logic is a logical system whose proof theory consists of specific inference rules. Need the generic notion of inference rule first to understand the role of the specific rules constituting predicate logic. Concept → system-built-on-instances-of-the-concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-16 — time → persistence
EDGE: Time [time, metaphysics] → Persistence [persistence, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Persistence is the metaphysical problem of how objects exist through time — endurance (wholly present at each time), perdurance (having temporal parts), exdurance (stage theory). The persistence question presupposes the notion of time as the dimension across which persistence is asked. Foundational dimension → problem-defined-against-the-dimension.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-17 — virtue_ethics → eudaimonia
EDGE: Virtue Ethics [virtue_ethics, ethics] → Eudaimonia [eudaimonia, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Eudaimonia is the central goal-concept of Aristotelian virtue ethics (the ultimate end of human action; flourishing in accordance with reason and virtue). The technical Aristotelian sense requires the framework of virtue ethics — function-argument, virtue-as-mean, golden-mean structure. But "eudaimonia" as a Greek word for human flourishing is sometimes introduced standalone in intro ethics courses before the full virtue-ethics framework is laid out (e.g., translating it as "happiness in the deepest sense"); the framework-first reading is the canonical contemporary teaching but the concept-first reading is also pedagogically live. Same "framework-introduces-its-central-concept" shape as shard 13 E-15 virtue_epistemology → intellectual_virtue (Defensible there); calibration consistency requires Defensible here. Second instance of this sub-shape in the routine batch.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — consciousness → access_consciousness
EDGE: Consciousness [consciousness, mind] → Access Consciousness [access_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Access consciousness (Block 1995) is one of the two principal varieties of consciousness Block distinguished (the other being phenomenal consciousness) — information is access-conscious iff it is poised for use in reasoning, reporting, and behavior control. Need the broader notion of consciousness first to understand what Block's taxonomy is dividing. Genus → species.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — medical_ethics → informed_consent
EDGE: Medical Ethics [medical_ethics, ethics] → Informed Consent [informed_consent, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: Informed consent is one of the central principles of contemporary medical ethics (alongside beneficence, non-maleficence, autonomy in the Beauchamp/Childress framework). The discipline provides the context (clinical practice, research ethics, the Nuremberg Code legacy) in which informed consent acquires its specific structural requirements. Discipline → central-principle-within-the-discipline.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-20 — set_mathematical → russell_paradox
EDGE: Set (Mathematical) [set_mathematical, service] → Russell's Paradox [russell_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Russell's paradox concerns the set of all sets that are not members of themselves — formulated entirely in set-theoretic vocabulary. The paradox presupposes the notion of set (and naive comprehension) as the apparatus it destabilizes. Apparatus → paradox-internal-to-the-apparatus.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-21 — vagueness → sorites_paradox
EDGE: Vagueness [vagueness, logic] → Sorites Paradox [sorites_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The sorites paradox is the paradigm illustration of the problem of vagueness — vague predicates (heap, bald, tall) tolerate small differences but compound tolerance generates contradiction. Need the notion of vagueness (predicates without sharp cut-offs) to understand what makes the sorites a paradox rather than just a long chain of conditionals. Phenomenon → paradigm-illustration-of-the-phenomenon.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-22 — persistence → ship_of_theseus
EDGE: Persistence [persistence, metaphysics] → Ship of Theseus [ship_of_theseus, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The Ship of Theseus is the canonical puzzle for theories of persistence — does the ship survive plank-by-plank replacement, or rebuilding from the discarded planks, or both? Need the persistence framing (numerical identity through change) to grasp what's puzzling about the ship. Topic → paradigm-puzzle-of-the-topic; same shape as E-21 above (vagueness → sorites_paradox).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-23 — qualia_eliminativism → illusionism
EDGE: Qualia Eliminativism [qualia_eliminativism, mind] → Illusionism (about Consciousness) [illusionism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Illusionism (Frankish 2016 "Illusionism as a Theory of Consciousness") is the contemporary refinement of qualia eliminativism — the view that phenomenal consciousness as it seems to us is an illusion (we have introspective representations of qualia, but no actual qualia). Frankish explicitly positions illusionism as a sharpening of the Dennett-style eliminativist tradition. Predecessor-position → contemporary-refinement.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-24 — sorites_paradox → supervaluationism
EDGE: Sorites Paradox [sorites_paradox, logic] → Supervaluationism [supervaluationism, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Supervaluationism (Fine 1975) is one of the leading philosophical responses to the sorites paradox — vague predicates have multiple admissible precisifications, and a sentence is super-true iff true on every precisification. Need the paradox first to understand what supervaluationism is responding to. Motivating-problem → formal-response.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-25 — performative_utterance → speech_act
EDGE: Performative Utterance [performative_utterance, language] → Speech Act [speech_act, language]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: The correction: Austin's performatives (1955) were the seed observation that motivated the generalized speech-act framework; historically and pedagogically performatives come first. Direction should be performative_utterance > speech_act."
VERDICT: Sound
RATIONALE: Edge direction was flipped by 0062 (LAN-E-2) per S-0122 audit. Austin's "Performative Utterances" (1956) and How to Do Things with Words (1962 Harvard lectures) introduced performatives as the seed observation that motivated the generalized speech-act framework; pedagogically performatives come first as the concrete sub-phenomenon, then speech-act theory generalizes. Sound on the audit-validated direction.
AUDIT-TOUCHED: migration 0062 (LAN-E-2) — direction flipped from speech_act → performative_utterance to performative_utterance → speech_act per the inline evidence text on the edge. Sole audit-touched edge in shard-14 (1/27 = 3.7%).
EVIDENCE NOTE: evidence text present and identifies the audit decision.

### E-26 — dualism → substance_dualism
EDGE: Dualism (Mind-Body) [dualism, mind] → Substance Dualism [substance_dualism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Substance dualism (Descartes; modern defenders Foster, Swinburne) is one species of mind-body dualism, alongside property dualism. Need the genus dualism first (the rejection of monism about mind and body) to grasp how substance dualism (two kinds of substance) differs from property dualism (one kind of substance, two kinds of property). Genus → species; same shape as E-14 (mental_state → propositional_attitude) and E-18 (consciousness → access_consciousness) above.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-27 — aesthetics → ontology_of_artworks
EDGE: Aesthetics [aesthetics, aesthetics] → Ontology of Artworks [ontology_of_artworks, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The ontology of artworks (what kind of entities artworks are — types, particulars, abstract structures, performances) is a specific sub-problem within aesthetics. Distinct from the discipline-→-object-of-study Defensible shape (e.g., aesthetics → art, aesthetics → aesthetic_property scored Defensible in shard 11) because ontology-of-artworks is not the discipline's *object* but a *sub-problem* within the discipline (parallel to E-12 metaethics → moral_anti_realism here, or shard 12 E-18 deontology → kantian_ethics). Discipline → sub-problem-within-the-discipline.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

## Node findings (C2 + C3)

### N-1 — multiple_drafts_model
NODE: Multiple Drafts Model [multiple_drafts_model, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Dennett's positive theory framed against the Cartesian Theater picture, connections to qualia eliminativism (1988) and heterophenomenology (1991) made explicit, empirical content (temporal structure of conscious report, memory consolidation) named, contrast with global workspace theory drawn.
C3 (summary cold-readability): yes — the negative claim ("no single point in the brain or moment in time when conscious experience 'happens'") and the positive picture (parallel drafts, selection-and-promotion) both laid out, "Cartesian Theater" glossed inline ("conscious experience is presented to a unified observer at a particular time and place"). Borderline-readable for a complete novice but the inline gloss on the load-bearing contrast rescues it.

### N-2 — predicate_logic
NODE: Predicate Logic [predicate_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the model M = ⟨D, I⟩ explicitly laid out, ∀/∃ semantics given, soundness/completeness (Gödel 1929) and compactness/Löwenheim-Skolem meta-theorems named, contrast with higher-order logic drawn.
C3 (summary cold-readability): yes — "Also called first-order logic" anchors the term; quantifiers introduced with their symbols (∀, ∃) and their function (binding variables); the shift from propositional logic to model-relative semantics is explained ("a domain of individuals plus interpretations for the predicates and constants"). Borderline-PASS: the reader takes "propositional logic" as a black box, but the predicate-logic content is self-explained. Same calibration as shard 12 N-3 formal_proof (borderline-PASS on structural-shape parsable).

### N-3 — gricean_maxims
NODE: Gricean Maxims (Cooperative Principle) [gricean_maxims, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the Smith/girlfriend/New York example walked through showing how implicature works, the implicature-vs-saying distinction made concrete, taxonomy of violations (hedged, unobtrusive, flouts) given, foundational role in contemporary linguistic pragmatics noted.
C3 (summary cold-readability): yes — Grice's 1975 paper named, the cooperative principle stated, four maxim categories each given an inline gloss (Quantity = informative-not-over-informative; Quality = truthful; Relation = relevant; Manner = clear-brief-orderly), "flouting" introduced with its mechanism (implicatures).

### N-4 — ontology
NODE: Ontology [ontology, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Quine's "On What There Is" (1948) named as foundational entry point, criterion of ontological commitment ("to be is to be the value of a variable") given verbatim, ontology vs metaontology distinction drawn with literature pointers (Schaffer, Hirsch, Cameron, Sider).
C3 (summary cold-readability): yes — clear two-question framing ("what is there? — from the descriptive question — what is the nature of what is there?"), inventory-range examples (austere vs lavish) given.

### N-5 — human_rights
NODE: Human Rights [human_rights, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive concrete pedagogy: institutional context (UDHR, ICCPR, ICESCR, regional human-rights instruments) opens, structural features (universality, inalienability, pre-institutional, interpretive-priority) laid out, civil-political vs economic-social-cultural taxonomy walked through, two theoretical orientations (moral conceptions Griffin/Gewirth, political conceptions Rawls/Beitz) contrasted, principal contestations (cultural-relativist, proliferation, negative-positive, foundations) named.
C3 (summary cold-readability): yes — "Universal moral entitlements held by all persons in virtue of their humanity" is the clean opening definition; institutional codification (UDHR 1948, ICCPR/ICESCR 1966) gives concrete anchoring; the moral-vs-political conceptions distinction is named with each given a one-line inline gloss.

### N-6 — knowledge_argument
NODE: Knowledge Argument (Mary) [knowledge_argument, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the four-step argument structure laid out verbatim, the standard physicalist responses each glossed (ability hypothesis Lewis-Nemirow, acquaintance hypothesis Conee, phenomenal concepts strategy Loar, outright denial Dennett), Jackson's eventual 2003 retraction noted, pairing with the zombie argument made explicit.
C3 (summary cold-readability): yes — Jackson 1982 named, Mary's setup ("a brilliant scientist, has lived her whole life in a black-and-white room studying color vision") given concretely, the argument's conclusion ("there are facts beyond the physical facts; physicalism, which holds that all facts are physical, is false") stated. "Property dualism" appears at end without gloss but is positioned as a parenthetical-historical landmark, not load-bearing for parsing the argument.

### N-7 — paraconsistent_logic
NODE: Paraconsistent Logic [paraconsistent_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the crucial paraconsistency-vs-dialetheism distinction (formal property vs metaphysical thesis) drawn explicitly with the directionality argument (dialetheism requires paraconsistency, but not vice versa), three major systems (LP/Priest, relevance logics/Anderson-Belnap, adaptive logics/Batens) characterized with their mechanisms.
C3 (summary cold-readability): yes — the explosion principle given verbatim (P ∧ ¬P ⊢ Q for all Q) and glossed inline ("inconsistent theories do not trivialize"), applications named (inconsistent databases, naive truth theories, naive set theories), paraconsistency-vs-dialetheism distinction stated in the closing sentence.

### N-8 — vienna_circle_logical_positivism
NODE: Vienna Circle and Logical Positivism [vienna_circle_logical_positivism, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive historical and doctrinal pedagogy: post-WWI Vienna context, Einstein 1915 and Tractatus 1921 as backdrop, central doctrines (verifiability criterion, rejection of metaphysics via Carnap's 1932 Heidegger paper, unity of science, emotivism), dispersal under Nazi pressure (Schlick murder 1936), reshape of Anglo-American philosophy with cross-domain pedagogical edges named.
C3 (summary cold-readability): yes — long but well-structured: the movement's geographic/temporal location given (1920s-1930s Vienna), member roll-call (Schlick, Carnap, Neurath, ...) embedded but positioned as listing rather than load-bearing for parsing, intellectual sources named (Frege/Russell/Wittgenstein on the logic side; Mach/British empiricism on the empiricism side), the analytic/empirical dichotomy and verifiability criterion stated clearly.

### N-9 — understanding
NODE: Understanding [understanding, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three senses distinguished concretely (understanding-that, understanding-why, objectual understanding), the historical-dates-vs-grasping-a-period contrast for objectual understanding gives a vivid concrete example, theoretical question (does it reduce to knowledge or stand as a separate category) named.
C3 (summary cold-readability): yes — "the cognitive achievement of grasping how the components of a body of information fit together — the structure of explanation, the relations of dependence, the connections among parts" is a clean one-sentence gloss, contrast with mere fact-knowledge drawn, three named proponents (Pritchard, Kvanvig, Zagzebski) listed.

### N-10 — sense_and_reference
NODE: Sense and Reference (Sinn und Bedeutung) [sense_and_reference, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Frege's astronomer / Hesperus-Phosphorus example developed at length, related puzzles (Lois Lane/Superman substitution; Pegasus empty-name) drawn, the foundational role for post-Fregean theory stated.
C3 (summary cold-readability): yes — Frege 1892 dated, sense glossed as "the mode of presentation — the cognitive content one grasps", reference glossed as "what the expression picks out in the world", the motivating puzzle (cognitive significance of identity statements) introduced with the Hesperus-Phosphorus example in the same sentence.

### N-11 — principle_of_alternative_possibilities
NODE: Principle of Alternative Possibilities [principle_of_alternative_possibilities, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Frankfurt's counterexample structure (Black as counterfactual intervener, Jones choosing A on his own) walked through concretely, the logical structure of the conclusion (PAP is false if Frankfurt cases work) made explicit, the standard responses (do the cases really show what they purport; even-if-PAP-false-does-that-vindicate-compatibilism) named.
C3 (summary cold-readability): yes — the principle stated cleanly ("an agent is morally responsible for an action only if the agent could have done otherwise"), abbreviation PAP introduced, the dialectical position (treated as a near-axiom of incompatibilism, challenged by Frankfurt 1969) given.

### N-12 — desert_theory_political
NODE: Desert Theory (Political) [desert_theory_political, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the structural shape of desert claims (person deserves X in virtue of desert basis Y) given, four standard desert bases (contribution, effort, virtue, responsible choice) each glossed, Rawls's "morally arbitrary" critique walked through, standard replies given (causal-determinism objection proves too much; institutional grounding; common-sense moral practice), contemporary partial-revival positions (Miller 1999 spheres-of-justice, Olsaretti 2004 market-grounded) named.
C3 (summary cold-readability): yes — desert-tracking gloss for the just-distribution principle given, Rawls 1971 "natural talents are morally arbitrary" critique stated, Miller 1999 partial-revival named.

### N-13 — semantic_externalism
NODE: Semantic Externalism [semantic_externalism, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Putnam's Twin Earth thought experiment walked through (Earth-Oscar vs Twin-Oscar; H2O vs XYZ; intrinsically identical but meaning-differently), Burge's arthritis case explained, implications across phil-mind (anti-individualism), epistemology (first-person authority puzzles), and metaphysics (Kripkean essentialism) drawn.
C3 (summary cold-readability): yes — the thesis stated cleanly, Putnam's 1975 slogan quoted ("meaning ain't in the head"), Burge's 1979 social-externalism variant glossed inline, consequences for phil-mind/epistemology/metaphysics named.

### N-14 — metaethics
NODE: Metaethics [metaethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the metaethics-vs-normative-ethics distinction made vivid with contrastive examples ("is abortion morally permissible?" vs "what would make any answer TRUE?"), the four canonical metaethical axes (realism/anti-realism, cognitivism/non-cognitivism, naturalism/non-naturalism, internalism/externalism) each given a one-line gloss, historical anchor (Moore 1903 inaugurating the field) named.
C3 (summary cold-readability): yes — second-order question framing stated, each technical area (ontology, semantics, epistemology, expressivism-vs-cognitivism, motivation) glossed inline, contrast with normative ethics drawn.

### N-15 — knowledge_how
NODE: Knowledge-How [knowledge_how, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete examples (a swimmer who knows how to swim need not know propositions about swimming), the central philosophical question named (distinct cognitive kind or special case of propositional knowledge), pedagogical role as foil for propositional knowledge.
C3 (summary cold-readability): yes — "The kind of knowledge involved in being able to do something" plus the riding-bicycle/speak-language/prove-theorem examples gives a clean ostensive definition, Ryle 1949 / Stanley-Williamson 2001 historical anchor.

### N-16 — expression_in_art
NODE: Expression in Art [expression_in_art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Goodman as anchor with the metaphorical-exemplification analysis worked out (the sonata metaphorically possesses sadness), three alternative theories (Davies appearance, Robinson romantic-persona, Kivy contour) each characterized, the underlying agreement (expression IS real and IS a property of the work) named.
C3 (summary cold-readability): yes — the work-vs-artist-vs-audience distinction drawn vividly ("themselves sad, joyful... — distinguished from artworks that depict sad people or were made by sad artists"), the sonata example given concretely (slow tempo, minor key, descending lines), Goodman 1968 anchor.

### N-17 — scientific_theory
NODE: Scientific Theory [scientific_theory, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three views of theory-as-object each developed: syntactic (Carnap/Hempel/positivists; sentences + correspondence rules; collapsed under theoretical-term linkage problems), semantic (Suppes 1957, van Fraassen 1980, Giere 1988; family of models; contemporary mainstream), pragmatic (Cartwright 1983, Hacking 1983; practices + exemplars + instruments; alternative for chemistry/biology/engineering), with the contemporary-vs-historical positioning named.
C3 (summary cold-readability): yes — the product-vs-activity distinction drawn (theory is the central product, scientific method is the activity that produces it), the metaphysical contestation acknowledged with the four-option list (sentences, structure, models, practices), the agreed-upon functions (predict, explain, unify, classify, intervene) named.

### N-18 — gunk
NODE: Gunk [gunk, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — motivating intuition stated (no obvious reason division must terminate), three classes of costs named (conflict with most physics; supervenience/grounding pressure; persistence/constitution surprises), defenders identified (Sider, Schaffer in some moods), pedagogical use as a thought-experiment exposing hidden atomist commitments.
C3 (summary cold-readability): yes — "no simples" load-bearing but immediately glossed by the surrounding ad-infinitum descent definition ("every object has proper parts, which themselves have proper parts, ad infinitum"), "atomism" identified as the alternative to anchor the contrast, Lewis's coinage credited. Borderline-PASS on backwards-inference reading (the reader infers what "simple" means from the surrounding division-terminates account); same calibration as shard 11 N-3 IIT load-bearing-term-ungated-but-contextually-parseable.

### N-19 — constructive_empiricism
NODE: Constructive Empiricism [constructive_empiricism, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — van Fraassen's observable/unobservable distinction worked out concretely (planet/moon/moss vs electron/quark/field), empirical adequacy glossed as "save the phenomena", the two-component theory-acceptance picture (belief in empirical adequacy + pragmatic commitment to use) given, three arguments (observable-line principled; no-miracles fails; pessimistic meta-induction) and the standard critics (Churchland, Psillos, Hacking) named.
C3 (summary cold-readability): yes — van Fraassen 1980 The Scientific Image anchored, "aims at empirical adequacy (saving the phenomena), not truth" glossed inline, theory-acceptance two-component definition spelled out, antirealist positioning vs scientific realism stated.

### N-20 — essence_metaphysical
NODE: Essence [essence_metaphysical, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three positions distinguished sharply (modal essentialism = necessary properties; Aristotelian/Finean = prior-to-modality; skepticism = dispensable), Fine 1994's Socrates-and-singleton argument walked through ("Socrates is necessarily a member of {Socrates}, but membership in {Socrates} is not part of what Socrates IS"), pedagogical positioning (essence as the place where the deepest disputes about modality live).
C3 (summary cold-readability): yes — opening one-sentence definition ("the properties an entity has of metaphysical necessity — those it could not lack while continuing to exist") clean, Aristotelian non-modal conception glossed inline ("answers the 'what is it?' question for an entity, prior to any consideration of necessity"), Fine 1994 historical-revival anchor.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 0 (0.0%) | teaching_notes ABSENT 0

## Cross-cutting observations

Cumulative C1 across shards 01–14: 10.7/3.6/3.6/0.0/3.7/0.0/0.0/3.7/0.0/0.0/0.0/0.0/0.0/0.0 → 23 defective / 380 scored = 6.05%, continuing the tick-down trend (was 6.5% at shard 13). The 0-defect run now stands at FIVE consecutive shards (10, 11, 12, 13, 14) and NINE 0-defect shards overall (04, 06, 07, 09, 10, 11, 12, 13, 14). Audit-touched footprint this shard: 1 edge total — E-25 (0062 LAN-E-2 direction flip from speech_act → performative_utterance per S-0122 audit, Austin 1955 performatives motivating the generalized speech-act framework). Scored Sound on the audit-validated direction; the audit's decisions continue to hold up against fresh parametric judgment 14 shards in.

Defensible count this shard: 2 (E-13 hard_problem_of_consciousness → knowledge_argument, framing-question-before-argument shape; E-17 virtue_ethics → eudaimonia, framework-introduces-its-central-concept shape). Counts across shards 04–14 are now 1/4/6/3/1/2/2/4/3/1/2 — sustained middle-band trend with no over-Defensible drift. E-17 instantiates the same "framework-introduces-its-central-concept" sub-shape as shard 13's E-15 virtue_epistemology → intellectual_virtue (second instance in the routine batch; the calibration question for SQA-20 now has two data points: virtue_epistemology → intellectual_virtue and virtue_ethics → eudaimonia, both Defensible on the same reading). E-13 hard_problem → knowledge_argument is a NEW sub-shape — "framing-question-before-argument-FOR-the-framing's-diagnosis"; flag for SQA-20 alongside the cycle-deferred-companion (shard 11 E-14) and parallel-theories-with-historical-succession (shard 12 E-13 DN→IBE) as Defensible sub-shapes distinct from the dominant discipline→object-of-study and framework→central-concept clusters. Third consecutive quadruple-0 shard (12-13-14); C3 has now produced 0 fails for three shards running, matching C2's clean streak across the routine batch (C2 has 0 fails total across all 14 shards).
