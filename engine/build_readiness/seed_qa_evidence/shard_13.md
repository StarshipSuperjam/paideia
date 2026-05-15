# Seed-graph QA census evidence — shard 13

> Authored by S-0175 (routine session) per T-SEED-QA task SQA-13.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 13
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — justified_true_belief → gettier_problem
EDGE: Justified True Belief [justified_true_belief, epistemology] → Gettier Problem [gettier_problem, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: JTB is the canonical pre-Gettier analysis of propositional knowledge (S knows that p iff S has a justified true belief that p). Gettier's 1963 paper is the famous counterexample to JTB-as-sufficient. The Gettier problem presupposes JTB as the target it disrupts. Standard analysis → counterexample-to-the-analysis shape.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-2 — set_mathematical → probability_mathematical
EDGE: Set Theory (Mathematical) [set_mathematical, service] → Probability (Mathematical) [probability_mathematical, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kolmogorov's 1933 axiomatization of probability is set-theoretic — events are subsets of a sample space, probability is a measure on a σ-algebra of events. Set theory is the foundational vocabulary in which modern probability is formulated. Foundation → built-on-foundation.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — a_theory_of_time → mctaggarts_paradox
EDGE: A-Theory of Time [a_theory_of_time, metaphysics] → McTaggart's Paradox [mctaggarts_paradox, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: McTaggart's 1908 argument introduced the A-series / B-series distinction and concluded the A-series is contradictory. The A-theory is the contemporary position that takes the A-series (past/present/future temporal predicates) as fundamental. Pedagogically, the A-theory / B-theory taxonomy of time is introduced first (the philosophical landscape of positions about time), then McTaggart's paradox as the historic argument targeting the A-series. Taxonomy-of-positions → argument-targeting-one-position.
AUDIT-TOUCHED: migration 0063 — 0063 deleted the shortcut edge `time → mctaggarts_paradox` (MET-E-10 weak-disposition) and explicitly named `a_theory_of_time → mctaggarts_paradox` as the more proximate path retained ("Long-distance shortcut over the more proximate path: time → a_theory_of_time → mctaggarts_paradox (already in graph)"). The edge itself was not modified; the audit endorsed it implicitly by pruning the shortcut.
EVIDENCE NOTE: absent

### E-4 — aesthetic_judgment → taste_aesthetic
EDGE: Aesthetic Judgment [aesthetic_judgment, aesthetics] → Taste (Aesthetic) [taste_aesthetic, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kant's Critique of Judgment (1790) and Hume's "Of the Standard of Taste" (1757) treat aesthetic judgment and taste as tightly linked — taste is the faculty exercised in making aesthetic judgments. In introductory aesthetics, "what is an aesthetic judgment?" is the structuring question, then taste enters as the faculty-or-disposition by which such judgments are made. Topic → faculty-exercise.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — ecocentrism → deep_ecology
EDGE: Ecocentrism [ecocentrism, ethics] → Deep Ecology [deep_ecology, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Deep ecology (Arne Naess 1973) is grounded in an ecocentric worldview — moral value resides in ecosystems and biospheric wholes, not just sentient individuals. Ecocentrism is the broader value-theoretic position; deep ecology is a specific philosophical-activist movement built on it with normative additions (self-realization, biocentric egalitarianism, intrinsic value of nonhuman life). Foundational value-position → specific-movement.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-6 — normative_ethics → consequentialism
EDGE: Normative Ethics [normative_ethics, ethics] → Consequentialism [consequentialism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Normative ethics is the branch of moral philosophy concerned with what makes actions right or wrong. Consequentialism (Bentham, Mill, Sidgwick, Singer) is one of the three major traditions within it (alongside deontology and virtue ethics). Standard umbrella → specific-instance shape (parallel to shard 11's E-18 deontology → kantian_ethics and shard 10's E-19 reductionism_in_science → multiple_realizability_in_science).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-7 — perception → sense_data_theory
EDGE: Perception [perception, mind] → Sense-Data Theory [sense_data_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Sense-data theory (Russell 1912, Moore, Price 1932, Ayer 1940) is a specific representationalist theory of perception — perceptual experience involves direct awareness of mind-dependent sense-data, which then represent (or fail to represent) external objects. Perception is the broader phenomenon; sense-data theory is one analysis. Topic → analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-8 — phenomenal_consciousness → qualia
EDGE: Phenomenal Consciousness [phenomenal_consciousness, mind] → Qualia [qualia, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Qualia (C.I. Lewis 1929, Dennett 1988, Block 1995) are the individual qualitative "what-it's-likeness" properties of phenomenally conscious experience — the redness of red, the painfulness of pain. Phenomenal consciousness is the broader phenomenon (the hard-problem backdrop); qualia are the theoretical posit for its constituent qualitative features. Topic → theoretical-component.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-9 — personal_identity → psychological_continuity_theory
EDGE: Personal Identity [personal_identity, mind] → Psychological Continuity Theory [psychological_continuity_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The personal identity question (what makes someone the same person across time?) generates a taxonomy of theories: psychological continuity (Locke 1689, Parfit 1984), biological / animalist (Olson 1997), narrative identity (Schechtman 1996). Psychological continuity is one specific theory. Topic → specific-theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-10 — applied_ethics → technology_ethics
EDGE: Applied Ethics [applied_ethics, ethics] → Technology Ethics [technology_ethics, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Applied ethics is the umbrella branch (bioethics, business ethics, environmental ethics, technology ethics, etc.). Technology ethics is a sub-branch addressing the moral questions raised by technology specifically. Umbrella → sub-branch.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-11 — set_mathematical → possible_worlds
EDGE: Set Theory (Mathematical) [set_mathematical, service] → Possible Worlds [possible_worlds, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Possible worlds are formally modeled set-theoretically — a model for modal logic is a triple ⟨W, R, V⟩ (a set of worlds W, an accessibility relation R, a valuation V); Plantinga's worlds are maximal consistent states of affairs (set-theoretically modelable); Adams's worlds are maximal consistent sets of propositions. Set-theoretic machinery underlies the formal apparatus of modal semantics. Foundation → application. Cross-domain (service → metaphysics) is consistent with possible worlds being formally definable in set-theoretic terms.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-12 — scientific_explanation → deductive_nomological_model
EDGE: Scientific Explanation [scientific_explanation, science] → Deductive-Nomological Model [deductive_nomological_model, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Hempel and Oppenheim's 1948 deductive-nomological model is the canonical mid-20th-century formal account of scientific explanation — an explanation is a deductively valid argument from explanans (containing at least one law of nature) to explanandum. Scientific explanation is the topic; DN is the foundational analysis (later refined / challenged by Salmon's statistical-relevance, van Fraassen's pragmatic, Woodward's interventionist accounts). Topic → analysis.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — motivational_internalism → motivational_externalism
EDGE: Motivational Internalism [motivational_internalism, ethics] → Motivational Externalism [motivational_externalism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Internalism (Hare 1952, Blackburn 1984, Smith 1994) and externalism (Brink 1986, Svavarsdóttir 1999) are opposing metaethical positions on the connection between moral judgment and motivation. Internalism is historically prior — the dominant view through mid-20th-century — and externalism arose as a critical response challenging the necessity-of-the-connection claim. Pedagogically, externalism cannot be characterized except as a rejection of internalism's necessary-connection thesis; internalism must be in place to motivate externalism as a position. Historical-priority + position-being-criticized shape (distinct from but adjacent to shard 11's E-18 anti_intentionalism → intentionalism_artistic, where the anti-position was historically more salient pedagogically).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-14 — normative_ethics → divine_command_theory
EDGE: Normative Ethics [normative_ethics, ethics] → Divine Command Theory [divine_command_theory, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Divine command theory (St. Augustine, Aquinas qualified, Pufendorf strong, contemporary Adams 1973 / 1999) is a theory within normative ethics — moral facts are constituted by God's commands. Same umbrella → specific-instance shape as E-6 normative_ethics → consequentialism.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-15 — virtue_epistemology → intellectual_virtue
EDGE: Virtue Epistemology [virtue_epistemology, epistemology] → Intellectual Virtue [intellectual_virtue, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Virtue epistemology (Zagzebski 1996, Greco 1993, Sosa 1991/2007) takes intellectual virtues — open-mindedness, intellectual honesty, perseverance, reliability, attentiveness — as the foundational epistemic concepts; justification and knowledge are analyzed in terms of belief-formation by intellectually-virtuous agents. The direction at issue: framework first, then its central concept? Or concept first, then the framework that builds on it? Two readings. (1) Framework-introduces-concept reading (the direction the edge runs): virtue epistemology is the theoretical position; intellectual virtue is its central theoretical posit; sound on the position-first reading. (2) Concept-first reading (the opposite direction): parallel to Aristotelian ethics, where ethical virtues (courage, temperance) are introduced as character traits before the virtue-ethical framework that takes them as foundational, an intellectual virtue is recognizable as a character trait of an inquirer prior to the epistemological framework that builds on it; on this reading the edge runs opposite. Both readings are independently defensible. Defensible on the framework-introduces-concept reading per the prior-shards' "discipline / framework → object-or-concept" calibration (shard 11 E-2 aesthetics → aesthetic_property, E-4 philosophy_of_mind → mind, both Defensible); not Reversed because the framework genuinely defines the technical sense of "intellectual virtue" (e.g., reliabilist-virtue vs responsibilist-virtue) that virtue epistemology contributes; not Weak-redundant because no more-proximate prereq exists for the technical concept.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-16 — physicalism → supervenience_mental
EDGE: Physicalism [physicalism, mind] → Supervenience (Mental) [supervenience_mental, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mental supervenience (Davidson 1970 "Mental Events"; Kim 1984; Lewis 1983) is the thesis that mental properties supervene on physical properties — no two beings differ mentally without differing physically. It is the standard formal-articulation tool for physicalism (and the weak-supervenience / strong-supervenience / global-supervenience distinctions enable articulations of non-reductive physicalism). Physicalism is the broader metaphysical position; mental supervenience is one formulation / test. Position → formulation-tool.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-17 — climate_ethics → intergenerational_justice
EDGE: Climate Ethics [climate_ethics, ethics] → Intergenerational Justice [intergenerational_justice, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Climate ethics raises distinctive intergenerational-justice issues — present actions affect future generations who cannot consent; the moral status of future-but-not-yet-existing persons; discounting future welfare (Stern Review 2006 vs Nordhaus on the discount rate); the non-identity problem (Parfit 1984 as applied to climate). Intergenerational justice is a key sub-topic the climate-ethics literature addresses. Topic → sub-topic.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — consciousness → representationalism_consciousness
EDGE: Consciousness [consciousness, mind] → Representationalism (Consciousness) [representationalism_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Representationalism about consciousness (Dretske 1995, Tye 1995, Lycan 1996) is a specific theory of phenomenal consciousness — phenomenal character is identical to or determined by representational content. Consciousness is the topic; representationalism is one analysis (alongside higher-order theories, global workspace, IIT, etc.). Topic → theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — bayesian_epistemology → dutch_book_argument
EDGE: Bayesian Epistemology [bayesian_epistemology, epistemology] → Dutch Book Argument [dutch_book_argument, epistemology]
  weight=1.0, confidence=1.0, evidence=Per S-0122 audit: Dutch book arguments provide the canonical pragmatic motivation for Bayesian probabilism (agents violating probability axioms are exploitable); DBA is the foundational justification internal to Bayesian doctrine.
VERDICT: Sound
RATIONALE: Dutch book arguments (Ramsey 1926, de Finetti 1937) are the canonical pragmatic motivation for Bayesian probabilism — an agent whose credences violate the probability axioms is exploitable via a series of bets that guarantees them a sure loss. The S-0122 audit's retain-with-annotation disposition explicitly notes DBA as the "foundational justification internal to Bayesian doctrine." Pedagogically, Bayesian epistemology is the position introduced first (probabilistic credences, conditionalization, etc.), then DBA as the central foundational argument for the probabilism component. Sound on the audit-validated rationale.
AUDIT-TOUCHED: migration 0063 — retain-with-annotation disposition (EPI-E-20). The S-0122 audit considered this edge as a weak / parallel-edge candidate but retained it on the rationale that DBA is the canonical pragmatic-foundational argument internal to Bayesian doctrine, not merely a downstream technical result. The evidence field carries the audit text.
EVIDENCE NOTE: present (S-0122 audit rationale)

### E-20 — causal_theory_of_reference → causal_theory_of_mental_content
EDGE: Causal Theory of Reference [causal_theory_of_reference, language] → Causal Theory of Mental Content [causal_theory_of_mental_content, mind]
  weight=1.0, confidence=1.0, evidence=Per S-0122 audit: The correction: Kripke-Putnam reference theory (1970s) predates and inspired Fodor's mental-content theory (1980s). Direction should be causal_theory_of_reference > causal_theory_of_mental_content.
VERDICT: Sound
RATIONALE: Kripke 1972 (Naming and Necessity) and Putnam 1975 ("The Meaning of 'Meaning'") developed causal theories of reference for natural-kind terms and proper names — reference is fixed by historical causal chains anchored in baptismal events. Fodor 1987 (Psychosemantics) and others later extended causal / historical analyses to mental content. The S-0122 audit direction-flipped this edge (CB-E-65) from `causal_theory_of_mental_content → causal_theory_of_reference` because the linguistic theory historically and conceptually precedes the mental-content extension. Cross-domain (language → mind) is consistent with the extension's direction (from reference in language to representational content in mind). Sound on the audit-validated direction.
AUDIT-TOUCHED: migration 0062 — direction flip CB-E-65 (Kripke-Putnam 1970s precedes Fodor 1980s). Evidence carries the audit text.
EVIDENCE NOTE: present (S-0122 audit rationale)

### E-21 — meaning → speech_act
EDGE: Meaning (Linguistic) [meaning, language] → Speech Act [speech_act, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Speech act theory (Austin 1962 "How to Do Things With Words", Searle 1969 "Speech Acts") is a pragmatic theory of meaning-in-use — utterances perform acts (locutionary content, illocutionary force, perlocutionary effect). Meaning is the broader topic in philosophy of language; speech-act theory is one approach (alongside truth-conditional semantics, conceptual-role semantics, pragmatic-inferential accounts). Topic → specific-theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-22 — propositional_logic → semantic_paradox
EDGE: Propositional Logic [propositional_logic, logic] → Semantic Paradox [semantic_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Semantic paradoxes (the Liar — "this sentence is false"; Curry's paradox; the Knower) are paradoxes that arise in formal-logical systems once a truth-predicate or self-reference is added. Propositional logic is the foundational formal system in which the syntactic and semantic apparatus is first introduced; semantic paradoxes are advanced topics that emerge once the foundation is extended with truth-related machinery (Tarski 1933 hierarchy as the structural response). Foundation → advanced-topic.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-23 — mental_state → perception
EDGE: Mental State [mental_state, mind] → Perception [perception, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Perception is a kind of mental state — perceptual experiences are mental states with representational content (or qualitative character, on phenomenalist accounts). Mental state is the genus / umbrella category in philosophy of mind; perception is one species (alongside belief, desire, emotion, etc.). Standard umbrella → specific-instance shape (parallel to E-6 normative_ethics → consequentialism and E-14 normative_ethics → divine_command_theory in this shard).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-24 — justice_as_fairness → luck_egalitarianism
EDGE: Justice as Fairness [justice_as_fairness, political] → Luck Egalitarianism [luck_egalitarianism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Rawls's justice as fairness (1971 Theory of Justice, 2001 Restatement) is the seminal contemporary liberal-egalitarian theory of distributive justice. Luck egalitarianism (Cohen 1989, Dworkin 1981, Arneson 1989) refines and modifies the Rawlsian framework: distributive justice should neutralize the effects of brute luck (unchosen circumstances — genetic endowment, family background) while allowing inequalities tracking option luck (gambles consciously taken). Luck egalitarianism is historically and conceptually downstream of Rawls's framework. Foundational-theory → refinement / response.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-25 — liberty_political → liberalism
EDGE: Liberty (Political) [liberty_political, political] → Liberalism [liberalism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Political liberty is the foundational political-philosophical concept (Berlin's 1958 "Two Concepts of Liberty" — positive vs negative liberty; Pettit's republican liberty as non-domination). Liberalism (Locke 1689, Mill 1859, Rawls 1971) is the political-philosophical tradition centrally organized around individual liberty as a core value. Pedagogically a working concept of liberty is needed to understand what makes liberalism the tradition it is. Foundational-concept → tradition-built-on-it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-26 — counterfactual_conditional → conditional_logic
EDGE: Counterfactual Conditional [counterfactual_conditional, logic] → Conditional Logic [conditional_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Stalnaker 1968 and Lewis 1973 developed conditional logic — the formal logic of counterfactuals — as a theory of counterfactual conditionals. Counterfactual conditionals are the topic / data (the puzzling-but-pervasive natural-language construction "if it had been the case that P, it would have been the case that Q" that material-implication semantics cannot capture); conditional logic is the formal theory developed to handle them, adding a selection function or similarity ordering on top of standard Kripke modal apparatus. Topic / phenomenon → formal-theory-of-it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-27 — internalism_epistemic → evidentialism
EDGE: Epistemic Internalism [internalism_epistemic, epistemology] → Evidentialism [evidentialism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Epistemic internalism is the broader position that justification depends on factors internal to the subject (mental states accessible to reflection / introspection — the access internalism variant; or mental states simpliciter — the mentalist variant). Evidentialism (Feldman & Conee 1985 "Evidentialism") is one specific internalist view: justification at time t is determined by the believer's evidence at t. Umbrella → specific-version.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

## Node findings (C2 + C3)

### N-1 — sorites_paradox
NODE: Sorites Paradox [sorites_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — classical formulation laid out (P1/P2/C), three contemporary responses (supervaluationism, epistemicism, fuzzy logic) each given a concrete diagnosis of where the inductive premise fails. Real foothold for a learner.
C3 (summary cold-readability): yes — defines via the heap example, names the three canonical formulations (conditional, mathematical-induction, line-drawing). Self-contained.

### N-2 — hegelian_dialectic
NODE: Hegelian Dialectic [hegelian_dialectic, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — contrast with formal-logical reasoning, applications across logic / history / political-philosophy / phenomenology, intellectual lineage (Marx, Frankfurt School, Sartre, British absolute idealism), the Vienna-Circle reaction. Rich foothold.
C3 (summary cold-readability): yes — defines via thesis-antithesis-synthesis with the contradiction-as-driver framing; the proper-noun references (Science of Logic, Philosophy of History) are titles, not jargon-gating terms; the methodological-alternative framing is parseable cold.

### N-3 — problem_of_induction
NODE: Problem of Induction [problem_of_induction, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes Hume's problem from Goodman's new riddle, names Bayesian / reliabilist / pragmatic / ordinary-language responses with their key moves.
C3 (summary cold-readability): yes — Hume's dilemma laid out (deductive justification is question-begging; inductive justification is circular); the uniformity-of-nature framing is glossed inline.

### N-4 — medical_ethics
NODE: Medical Ethics [medical_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Hippocratic / medieval / modern / contemporary historical arc, the Beecher 1966 inflection point, the principlism-vs-virtue debate (Pellegrino-Thomasma-Jonsen-Toulmin objection and the principlist response). Extensive concrete material.
C3 (summary cold-readability): yes — defined as branch of bioethics; contrasted with research ethics and broader bioethics; the four-principles framework is named (technical but contextually placed).

### N-5 — knowledge
NODE: Knowledge [knowledge, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explicit pedagogical-order observation (species precede the genus: knowing-that and knowing-how grasped concretely before knowledge-as-such). Brief but targeted.
C3 (summary cold-readability): yes (borderline) — "the general epistemic standing a believer has when she knows something" is mildly self-referential, but the species naming (propositional knowledge: knowing-that; procedural knowledge: knowing-how) immediately follows and grounds it. Held at PASS on the species-naming-as-gloss reading.

### N-6 — conversational_implicature
NODE: Conversational Implicature [conversational_implicature, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Grice's tests (cancelability, calculability, non-detachability, non-conventionality) walked through with the canonical examples (scalar, relevance-based, manner-based); applications (politeness, indirect requests, irony, hedging); limits acknowledged.
C3 (summary cold-readability): yes — defined via the two concrete examples ("Some students passed", "Where can I get gas?"), the cooperation-plus-maxim apparatus named, the four properties listed.

### N-7 — soundness_logical
NODE: Soundness (Logical) [soundness_logical, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gold-standard framing, why formal logic teaches validity rather than soundness, pedagogical sequencing (structure → validity → soundness), the meta-logical sense (system soundness paired with completeness) flagged for later coverage.
C3 (summary cold-readability): yes — sound iff valid AND premises true, with the conditional-vs-unconditional framing; meta-logical sense explicitly cordoned off.

### N-8 — skepticism_epistemic
NODE: Epistemic Skepticism [skepticism_epistemic, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — position vs argument distinction, Pyrrhonian-therapeutic vs Cartesian-methodological framings, contemporary anti-skeptical orientation noted.
C3 (summary cold-readability): yes — global vs local scope distinction, the bar-setting role for epistemology.

### N-9 — scholasticism
NODE: Scholasticism [scholasticism, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — twin importance (the negative reference point for early-modern philosophy; the source of much contemporary metaphysical vocabulary), the summa and quaestio methodologies, university-curriculum framing (trivium + quadrivium).
C3 (summary cold-readability): yes — dates, key figures, central role (Aristotelian-Christian synthesis), legacy (technical vocabulary).

### N-10 — ersatz_modal_realism
NODE: Ersatz Modal Realism [ersatz_modal_realism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the four ersatzist variants distinguished (Plantinga states of affairs; Stalnaker ways; Adams sets of propositions; Armstrong combinatorial), Lewis-style circularity objection named and the ersatzist response gestured at.
C3 (summary cold-readability): yes (borderline) — "possible worlds" is a load-bearing term used without external gloss, but the "abstract entities" + "denying that worlds are concrete" pair inline in the summary establishes ersatzism by contrast (abstract-rather-than-concrete). Held at PASS on the inline-contrast-as-gloss reading, consistent with shard 11 N-3 IIT (Φ named-and-functioned via context) and shard 12's borderline calibration. Could be flagged for closeout review.

### N-11 — metaphor
NODE: Metaphor [metaphor, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three positions cleanly distinguished (cognitivist, pragmatic, causalist) with their canonical defenders, the aesthetic-significance framing (whether art delivers cognitive value).
C3 (summary cold-readability): yes — the literal/figurative contrast laid out, three concrete examples ("Juliet is the sun"; "the mind is a stage"; "this argument is on shaky ground"), the philosophical-dispute taxonomy named.

### N-12 — ai_ethics
NODE: AI Ethics [ai_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — five subdivisions (near-term alignment / fairness / transparency, machine ethics, value alignment, existential risk, governance) with named arguments (Hardt-Price-Srebro impossibility, Wallach-Allen operational/functional/full distinction, Russell's outer-vs-inner-alignment), policy initiatives (OECD, EU AI Act, US AI Bill of Rights). Extensive concrete material.
C3 (summary cold-readability): yes — defined as branch of technology ethics with AI-specific scope, the eight enumerated concerns, key sources (Bostrom 2014, Russell 2019, Wallach & Allen 2009).

### N-13 — end_of_life_ethics
NODE: End-of-Life Ethics [end_of_life_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — five canonical issues (withholding vs withdrawing; active vs passive euthanasia via Rachels's Smith-and-Jones case; advance directives + surrogate decision-making + dead-donor rule; physician-assisted dying with the legal landscape; doctrine of double effect). Concrete cases throughout (Maynard, Pretty, Quinlan, Cruzan, Schiavo).
C3 (summary cold-readability): yes — clear scope, landmark cases (Quinlan 1976, Cruzan 1990, Schiavo 2005), key philosophical positions (Rachels 1975, Foot 1967, Brock 1992).

### N-14 — moral_particularism
NODE: Moral Particularism [moral_particularism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Dancy's argument structure laid out, the sadist-pleasure and lying-manipulator-request examples for the holism claim, ETHICS WITHOUT PRINCIPLES 2004 refinement, allies (virtue ethics, some moral realisms), critics' transmission-impossibility charge with Dancy's response.
C3 (summary cold-readability): yes — Dancy's 1993/2004 view stated, HOLISM glossed inline ("the same feature ... can count AGAINST that action in another case"), PRINCIPLISM glossed as "the view that moral knowledge consists in knowing principles".

### N-15 — motivational_internalism
NODE: Motivational Internalism [motivational_internalism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete-judgment example ("I ought to feed my hungry friend"), externalism contrast, amoralist debate, expressivism naturally explaining the internalist link, Smith's weak/strong distinction.
C3 (summary cold-readability): yes — necessary connection between sincere moral judgment and motivation, strong vs weak variants, key defenders (Hare 1952, Blackburn 1984, Smith 1994), expressivism connection.

### N-16 — intentionality
NODE: Intentionality [intentionality, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Brentano's thesis + naturalist's challenge framing, three contemporary naturalistic theories (representationalism, functional-role semantics, causal/teleosemantic), original-vs-derived intentionality (Searle), connections to philosophy of language and philosophy of biology.
C3 (summary cold-readability): yes — aboutness laid out via three concrete examples (belief about, desire for, perception of), Brentano's mark-of-the-mental named, the naturalistic puzzle stated.

### N-17 — counterexample
NODE: Counterexample [counterexample, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — mathematical example (9 = 3 × 3 refutes "every odd number greater than 1 is prime"), philosophical example (Gettier 1963 refuting JTB), the bivalence dependency (paracomplete logics complicate the method).
C3 (summary cold-readability): yes — the universal-claim refutation strategy, the confirmation-vs-refutation asymmetry, the falsificationist connection.

### N-18 — bivalence_principle
NODE: Principle of Bivalence [bivalence_principle, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three closely-related-but-distinct laws (non-contradiction, excluded middle, bivalence) separated, where they come apart in non-classical logics (intuitionistic, many-valued, supervaluationism).
C3 (summary cold-readability): yes — exactly-two-truth-values formulation, distinguished from excluded middle inline ("bivalence is a semantic principle about truth values, while excluded middle is a syntactic theorem").

### N-19 — renaissance_mechanism
NODE: Renaissance and Early-Modern Mechanism [renaissance_mechanism, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — four contrasts with what mechanism rejected (no substantial forms; no final causes; primary-vs-secondary qualities; mathematical-not-qualitative description), intellectual lineage (Cartesian animal-machine, Locke's formalization, transmission to British empiricism, modern physicalism).
C3 (summary cold-readability): yes — dates, key figures with dates, central commitment (matter-in-motion supplanting Aristotelian-Scholastic), philosophical commitments (rejected formal + final causes, qualitative description, substantial forms).

### N-20 — possible_worlds
NODE: Possible Worlds [possible_worlds, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explicit pedagogical-sequencing recommendation (semantic device first, then metaphysical question), Lewis's modal realism vs three ersatzist alternatives (Plantinga, Stalnaker, Adams) characterized.
C3 (summary cold-readability): yes — "total ways the world could have been" gloss, necessary-truth / possible-truth characterized in terms of quantification over worlds, the metaphysical-vs-semantic question explicitly distinguished.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 0 (0.0%) | teaching_notes ABSENT 0

## Cross-cutting observations

Cumulative C1 across shards 01–13: 10.7/3.6/3.6/0.0/3.7/0.0/0.0/3.7/0.0/0.0/0.0/0.0/0.0 → 23 defective / 353 scored = 6.5%, continuing the tick-down trend (was 7.1% at shard 12). The 0-defect run now stands at FOUR consecutive shards (10, 11, 12, 13) and EIGHT 0-defect shards overall (04, 06, 07, 09, 10, 11, 12, 13). Audit-touched footprint this shard: 3 edges total — E-3 (audit-context-named as the proximate path retained by 0063 when the shortcut `time → mctaggarts_paradox` was deleted, but not directly modified), E-19 (0063 retain-with-annotation evidence backfill), E-20 (0062 direction flip CB-E-65). All three scored Sound on the audit-validated direction / rationale; the audit's decisions continue to hold up against fresh parametric judgment 13 shards in.

Defensible count this shard: 1 (E-15 virtue_epistemology → intellectual_virtue), a single-Defensible shard after shard 12's 3 and shard 11's 4 — middle-band counts across shards 04–13 are now 1/4/6/3/1/2/2/4/3/1. E-15 instantiates the "framework introduces its central concept" sub-shape, distinct from the prior shards' recurring "discipline → object-of-study" sub-shape but closely related (both run framework-or-discipline-first into a concept that's also recognizable in isolation).
