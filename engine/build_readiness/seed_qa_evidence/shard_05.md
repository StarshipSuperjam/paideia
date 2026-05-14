# Seed-graph QA census evidence — shard 05

> Authored by S-0166 (routine session) per T-SEED-QA task SQA-05.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 05
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-14

## Edge findings (C1)

### E-1 — f8f279d4-ecaa-4b61-84ec-4e9a667c910e
EDGE: Mental State [mental_state, mind] → Dualism (Mind-Body) [dualism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Dualism is a position about the relation between the mental and the physical. A learner needs the concept of a mental state before a thesis stated in terms of mental and physical substances/properties. Concept → position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-2 — fb847fe7-76aa-4eaf-8f79-d493e891fab8
EDGE: Reference [reference, language] → Proper Name [proper_name, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reference is the general word-world relation; a proper name is a specific kind of referring expression. General relation → specific case, the seed's standard order. Sub-observation for the closeout: a real alternative runs proper_name → reference (proper names are the concrete, familiar referring terms, and Kripke's "Naming and Necessity" develops reference theory through them) — flagged for consistency review, not scored a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — 1c65509b-95a8-4ffd-914b-8ec68eeda21d
EDGE: Material Conditional [material_conditional, logic] → Paradox of the Ravens [paradox_of_the_ravens, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Hempel's raven paradox depends on reading "all ravens are black" as the material conditional ∀x(Rx → Bx) and on the contrapositive equivalence with ∀x(¬Bx → ¬Rx). The connective and its contraposition are needed to state the paradox at all. Framework → puzzle arising within it. Cross-domain (logic → science) is expected for a logical primitive feeding a confirmation-theory puzzle.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-4 — ae36d0cc-32ff-478b-a263-25bde65ca2d8
EDGE: Justice [justice, political] → Distributive Justice [distributive_justice, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Distributive justice is the branch of justice concerned with the allocation of goods and burdens. General concept → specific aspect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — 9dc89274-fa5e-4daf-9e4f-15ee29c1a883
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Foundationalism [foundationalism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Foundationalism is a theory about the structure of epistemic justification (basic beliefs ground derived ones). The general concept precedes a specific theory of it. Concept → theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-6 — ea4ee341-676d-43a5-a86f-5869de34418f
EDGE: Scientific Theory [scientific_theory, science] → Scientific Model [scientific_model, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: In a philosophy-of-science curriculum "what is a scientific theory" is the foundational, larger-grain concept introduced early; the modeling literature (models as constituents of theories, or as mediators between theory and world) is the more specialized later topic. Curricular order theory → model. Sub-observation for the closeout: the semantic view treats theories AS families of models, and a scale/mathematical model is arguably the more concrete entry — a both-ways alternative, flagged for consistency review, not a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-7 — 592adf3d-d223-46f2-a479-ed688c989a2f
EDGE: Property Dualism [property_dualism, mind] → Philosophical Zombie [philosophical_zombie, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Reversed
RATIONALE: The zombie thought experiment (a being physically identical to a conscious person but lacking phenomenal consciousness) is the intuition pump that *motivates* property dualism: conceivability of zombies → possibility → falsity of physicalism → property dualism (Chalmers). Pedagogically the learner meets the vivid thought experiment as the entry point and derives the dualist conclusion — direction philosophical_zombie → property_dualism. The current edge runs opposite. This is consistent with the production audit's own methodology: migration 0062 flipped the structurally-identical pair property_dualism → knowledge_argument to knowledge_argument → property_dualism (thought experiment is the prerequisite of the position). The audit caught the knowledge_argument sibling but not this one; recording it as a fresh authoring defect that the audit's 0062 logic would also flip.
AUDIT-TOUCHED: none — but note the direct structural parallel to migration 0062's property_dualism→knowledge_argument flip; the closeout should weigh this as a candidate consistency follow-up to 0062, not a re-opening of an audit decision (this specific edge was never audited).
EVIDENCE NOTE: absent

### E-8 — 28d6fc86-8475-4c25-a127-15f70c2c4dc4
EDGE: Liberalism [liberalism, political] → Multiculturalism [multiculturalism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Multiculturalism as a political theory (Kymlicka, Taylor) is largely a development within and debate about liberalism — how liberal theory accommodates cultural group rights. The broader tradition precedes the development engaging it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-9 — a9e8fe11-f5b6-40ce-af32-464d870670e8
EDGE: Gettier Problem [gettier_problem, epistemology] → Tracking Theory of Knowledge [tracking_theory_of_knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nozick's tracking (sensitivity) theory is one of the canonical post-Gettier analyses of knowledge — the Gettier problem (JTB is insufficient) is the problem it responds to. Problem → theory responding to it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-10 — 3c5fe79c-ac8e-4b1c-aee1-9317e5c84c6f
EDGE: Liberalism [liberalism, political] → Communitarianism [communitarianism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Communitarianism (MacIntyre, Sandel, Walzer, Taylor) arose as a critique of liberalism — chiefly Rawlsian liberalism. The learner needs liberalism as the target the critique is aimed at. Tradition → critique of it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-11 — e1080f61-8a4d-4341-89d6-cdccdc6dc906
EDGE: Tarski's T-Schema [tarskis_t_schema, language] → Deflationary Theory of Truth [deflationary_theory_of_truth, language]
  weight=1.0, confidence=1.0, evidence='Per S-0122 audit: ...T-schema is the apparatus on which deflationism is built.'
VERDICT: Sound
RATIONALE: The T-schema is the formal apparatus deflationary theorists (Field, Horwich) build on. This is the post-audit-flip direction and it holds: the formal tool precedes the theory deploying it. Scored Sound on its current (audit-corrected) direction, not re-opened.
AUDIT-TOUCHED: migration 0062 — direction-flipped from deflationary_theory_of_truth → tarskis_t_schema to the current direction. Verdict agrees with the audit's flip.
EVIDENCE NOTE: present — the S-0122 audit annotation justifies the edge.

### E-12 — ddb13577-6e61-46e5-8931-64aca7cb7f14
EDGE: Distributive Justice [distributive_justice, political] → Communitarianism [communitarianism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Distributive justice is one site where the liberal-communitarian debate plays out (Walzer's "Spheres of Justice" is a communitarian theory of distribution; Sandel critiques Rawls's distributive theory), so the direction is supportable. But it is not the canonical tight prerequisite — that is liberalism → communitarianism (E-10 in this same shard), since communitarianism is a critique of liberalism broadly, not of distributive justice specifically. Supportable secondary prerequisite, not a defect; the closeout may want to weigh whether E-10 makes this edge redundant.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — 3fc42142-a989-49ec-b0f1-210a33c1f523
EDGE: Just War Theory [just_war_theory, ethics] → Pacifism [pacifism, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Defensible
RATIONALE: Just war theory and pacifism are the two principal — and opposed — positions on the ethics of war. The direction is supportable as curricular convention (just war theory is the dominant framework taught first; pacifism is presented as the more radical rejection of its permissibility claims), but it is not a tight conceptual dependency: pacifism is graspable without just war theory, and is arguably the simpler position. The sub-1.0 weight (0.85) already signals the seed authors saw this as a soft dependency. Not a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-14 — 8b2cf012-2af1-4124-a2cb-a10c54b7be35
EDGE: Scientific Explanation [scientific_explanation, science] → Inference to the Best Explanation [inference_to_the_best_explanation, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: IBE (abduction) is an inference pattern defined in terms of explanation — inference to the hypothesis that, if true, would best explain the evidence. The concept of explanation is a definitional prerequisite. The scientific_explanation node's own summary lists IBE as one of the dominant accounts. Concept → inference pattern built on it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-15 — b3e1968c-4494-49f7-bedb-851bfda8e165
EDGE: Bayes's Theorem [bayes_theorem, service] → Bayesian Epistemology [bayesian_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bayesian epistemology is the framework built on Bayes's theorem and the probability calculus — conditionalization is updating by Bayes's rule. The formal apparatus precedes the epistemological framework deploying it. Cross-domain (service → epistemology) is expected for a service-tier mathematical primitive feeding a philosophical application (cf. shard 04's conditional_probability → conditionalization).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-16 — 8fbaf456-f0ea-40a1-a1d4-1e1d147c38b6
EDGE: Persistence [persistence, metaphysics] → Perdurantism [perdurantism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Persistence is the question of how objects persist through time; perdurantism is one answer (objects are four-dimensional, with temporal parts). Topic → specific theory of it. Parallels shard 04's persistence → endurantism.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-17 — 2db695b4-d952-408a-9861-bad3ca12a35d
EDGE: Distributive Justice [distributive_justice, political] → Justice as Fairness (Rawls) [justice_as_fairness, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Rawls's justice as fairness is, centrally, a theory of distributive justice. General topic → specific theory of it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — 26d5c3de-7dd3-4083-b579-561f96533a3d
EDGE: Problem of Induction [problem_of_induction, epistemology] → Falsificationism [falsificationism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Popper's falsificationism is explicitly a response to the problem of induction — Popper claimed to dissolve it by denying that science relies on inductive inference. The problem precedes the theory responding to it. Cross-domain (epistemology → science) is expected.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — 1fde0749-590e-41bd-892c-48710a79a3c8
EDGE: Knowledge [knowledge, epistemology] → Fallibilism [fallibilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Fallibilism is a position about the nature of knowledge — that one can know p without one's grounds entailing p; knowledge does not require certainty. The general concept precedes the position about it. Concept → position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-20 — f561c768-1de6-46e9-9c93-0356840c017c
EDGE: Mental Supervenience [supervenience_mental, mind] → Mental Causation [mental_causation, mind]
  weight=1.0, confidence=1.0, evidence='Per S-0122 audit: The basic puzzle of mental causation predates supervenience apparatus (Princess Elisabeth 1643); supervenience is one sophisticated framework (Kim-style) for formulating the modern version, but the puzzle is conceptually prior.'
VERDICT: Defensible
RATIONALE: The direction is supportable on the reading that supervenience is the apparatus the *modern* Kim-style exclusion-argument formulation of mental causation is built on. But it is not the canonical pedagogical order — and notably the audit's *own* evidence annotation says so explicitly: "the puzzle [mental causation] is conceptually prior" (the mind-body causation problem predates supervenience by centuries — Princess Elisabeth 1643). The production audit examined this edge at migration 0064 and chose to *annotate* it rather than flip it (0064 is the evidence-annotations pass, not a direction-flip pass). Scored Defensible — not a defect, because the audit deliberately kept the direction after examination — but flagged prominently: this is the rare case where the audit's attached evidence argues against the edge's own direction. The closeout should decide whether the "modern formulation" reading warrants keeping it or whether 0064 should have flipped rather than annotated.
AUDIT-TOUCHED: migration 0064 — evidence-annotated, direction kept. The annotation itself flags the target (mental_causation) as conceptually prior.
EVIDENCE NOTE: present — but the annotation argues mental_causation is conceptually prior, in tension with the edge it annotates.

### E-21 — 6a5217cf-8d49-480b-a413-ceb51f31f22e
EDGE: Virtue Epistemology [virtue_epistemology, epistemology] → Virtue Reliabilism [virtue_reliabilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Virtue reliabilism (Sosa) is one strand of virtue epistemology. Field/frame → specific position within it. Parallels shard 04's intellectual_virtue → virtue_responsibilism.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-22 — dc42ebe0-2b0f-4a6f-b612-1ea6b4271ea9
EDGE: Indicative Conditional [indicative_conditional, logic] → Counterfactual Conditional [counterfactual_conditional, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: In the logic curriculum the indicative conditional is introduced before the counterfactual/subjunctive conditional, which is the harder topic requiring possible-worlds semantics (Stalnaker, Lewis). Curricular order indicative → counterfactual. Forms a coherent chain with shard 04's material_conditional → indicative_conditional: material → indicative → counterfactual.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-23 — 2cfb352f-7838-4454-add2-a3c73c65d03f
EDGE: Mental Causation [mental_causation, mind] → Eliminative Materialism [eliminative_materialism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The difficulty of integrating mental states into the causal order is one of the pressures that motivates eliminative materialism (if mental states resist causal integration, perhaps eliminate them), so the direction is supportable. But it is not the canonical tight prerequisite — eliminativism's core (folk psychology is a false theory; propositional attitudes do not exist) is graspable without the mental-causation problem specifically, and the more proximate prerequisite would be a concept like mental_state or folk psychology. Supportable but not a tight dependency; not a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-24 — 4fdba9ac-e3e4-4fc4-9e28-86a5ee36e0ab
EDGE: B-Theory of Time [b_theory_of_time, metaphysics] → Eternalism [eternalism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The B-theory's tenseless conception of time (no objective present; all times equally real; only earlier/later-than relations) naturally grounds eternalism (all times exist). B-theorists are standardly eternalists, and the B-theory supplies the conceptual frame within which eternalism is the natural ontology. Sub-observation for the closeout: the link is not strictly necessary — the moving-spotlight view combines A-theory with eternalism — so the two sit on related-but-distinct axes (nature of passage vs. ontology of times); flagged for consistency review, not scored a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-25 — e68d0fc5-d51f-4c0d-9687-a6535921a395
EDGE: Multiple Realizability [multiple_realizability, mind] → Functionalism (Philosophy of Mind) [functionalism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The multiple-realizability argument (Putnam) — the same mental state can be realized by different physical substrates — is the central consideration that motivates functionalism. The learner meets multiple realizability as the argument that makes functionalism attractive. Argument → position it supports. Consistent with the audit's 0062 precedent that the motivating argument is the pedagogical prerequisite of the position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-26 — e9907ada-5b73-46fb-a415-7ee8c0348858
EDGE: Distributive Justice [distributive_justice, political] → Capability Approach [capability_approach, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The capability approach (Sen, Nussbaum) is a theory of distributive justice and well-being — it answers the "equality of what?" question with "capabilities." General topic → specific theory of it. Parallels E-17 (distributive_justice → justice_as_fairness).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-27 — 57d562a9-4604-4715-8bd4-5df942b3a659
EDGE: Propositional Attitude [propositional_attitude, mind] → Epistemic Justification [epistemic_justification, epistemology]
  weight=1.0, confidence=1.0, evidence='Per S-0122 audit: ...justification is a PROPERTY of propositional attitudes; bearers (attitudes) are conceptually prior...'
VERDICT: Sound
RATIONALE: This is the post-audit-flip direction and it holds: justification is a property attitudes bear; the bearer (the propositional attitude) is conceptually prior to a property predicated of it. Scored Sound on its current (audit-corrected) direction. Cross-domain (mind → epistemology), expected. Note: the 0062 *revert* migration concerns a different edge (proposition ↔ propositional_attitude / CB-E-63), not this one — the propositional_attitude → epistemic_justification flip stands.
AUDIT-TOUCHED: migration 0062 — direction-flipped from epistemic_justification → propositional_attitude to the current direction. Verdict agrees with the audit's flip.
EVIDENCE NOTE: present — the S-0122 audit annotation justifies the edge.

## Node findings (C2 + C3)

### N-1 — toleration
NODE: Toleration [toleration, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens with the conceptual structure (toleration is not endorsement; the toleration-paradox), walks the canonical historical arguments (Locke, Mill), the contemporary developments (Rawls's public reason, Popper's paradox of tolerating the intolerant, the multiculturalism relation), and the standard objections (public-private distinction, Connolly, Honneth on recognition). Rich, multi-angle foothold.
C3 (summary cold-readability): yes — "the political stance of refraining from suppressing beliefs and practices one disapproves of" is plainly stated and immediately intelligible; the Locke/Mill/Rawls anchors ground it.

### N-2 — bayesian_epistemology
NODE: Bayesian Epistemology [bayesian_epistemology, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three numbered theses (probabilism, conditionalization, decision theory), the Dutch book and diachronic-Dutch-book motivations, and Earman's "Bayes or Bust?" as a critical entry. Brief but a genuine worked angle.
C3 (summary cold-readability): yes — borderline: "models rational belief as conformity to the probability calculus (probabilism)" assumes "probability calculus," but "probabilism" and "conditionalization" are glossed by apposition and the overall claim ("a quantitative, normatively rigorous account of evidence, confirmation, and inductive reasoning") is clear. Among the closer-to-the-line summaries in this shard.

### N-3 — pictorial_representation
NODE: Pictorial Representation [pictorial_representation, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Goodman's critique of resemblance (the symmetry and reflexivity arguments), Goodman's positive symbol-system account, the resemblance-theorist responses (Peacocke, Hopkins), and Wollheim's seeing-in as a third position. Rich, multi-position foothold.
C3 (summary cold-readability): yes — concrete examples carry it ("a portrait depicts a person, a landscape depicts a scene"); the resemblance-vs-convention dispute is plainly framed.

### N-4 — modality
NODE: Modality [modality, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the possible-worlds analysis, the de re / de dicto distinction (with why it matters for transworld identity), Quine's skepticism and Kripke's response. A genuine map.
C3 (summary cold-readability): yes — "what it is for a proposition to be necessarily true (true at every possible way the world could have been)" carries its own inline gloss; the alethic/deontic/epistemic distinction is plainly drawn.

### N-5 — pessimistic_meta_induction
NODE: Pessimistic Meta-Induction [pessimistic_meta_induction, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks the argument's inductive structure, the historical case base (caloric, phlogiston, ether, Newtonian mechanics), and three realist responses (selective realism, structural realism, the novel-predictive-success reframe). Excellent foothold.
C3 (summary cold-readability): yes — the concrete historical examples (caloric theory of heat, phlogiston, ether) make the argument cold-readable; the success-to-truth inference it targets is plainly stated.

### N-6 — peer_disagreement
NODE: Peer Disagreement [peer_disagreement, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — sets up the problem with a concrete vignette (two competent people calculating a tip differently), maps the equal-weight / steadfast contrast onto the intuitions, and notes the stakes for political and religious disagreement. Real angle.
C3 (summary cold-readability): yes — "epistemic peer" is glossed inline as "someone equally well-informed and equally rational"; the two camps are plainly named.

### N-7 — existence
NODE: Existence [existence, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes three layers (the metaphysical, logical, and ontological questions) and locates Kant, Frege, Russell, Meinong, Quine within them. Genuine angle.
C3 (summary cold-readability): yes — "the most basic property a thing has when it is — when it figures in the world rather than being merely thought of, hoped for, or denied" is plain and concrete; the "whether existence is a property at all" caveat is accessible.

### N-8 — ross_paradox
NODE: Ross Paradox [ross_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — locates it as the second canonical SDL adequacy challenge, gives the closure argument explicitly, and lays out three response families (bite-the-bullet, restrict closure, agentive/stit accounts). Worked foothold.
C3 (summary cold-readability): no — jargon-gated. The summary's load-bearing first sentence uses the unexpanded acronym "SDL", the phrase "modal closure on disjunction-introduction", and the notations "(Om)" and "(O(m ∨ b))" — all of which assume modal-logic background a cold reader does not have. The acronym SDL is expanded in the teaching_notes and in the deontic_logic node's summary, but not here, where C3 is scored. The second sentence partly rescues the *upshot* in plain terms ("the permission to burn the letter ... was not obviously authorized"), but a newcomer still cannot parse what SDL is or what "modal closure on disjunction-introduction" means. Contrast N-13 (deontic_logic), which leads with a fully plain definition and expands "Standard Deontic Logic (SDL)" in full — the principled difference is that ross_paradox uses the apparatus undefined where deontic_logic defines it.

### N-9 — kantian_ethics
NODE: Kantian Ethics [kantian_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the central insight (morality as a constraint pure practical reason imposes on rational agency), each of the three categorical-imperative formulations unpacked, the rigorism point (the murderer-at-the-door case), and modern Kantian flexibilizations. Very rich.
C3 (summary cold-readability): yes — the technical terms ("deontological", "pure practical reason", "categorical imperative") are each followed by plain-language unpacking of the three formulations ("act only on maxims you could will to be universal laws"; "treat humanity ... always as an end, never merely as a means"). The plain glosses rescue the technical openers.

### N-10 — ontology_musical_works
NODE: Ontology of Musical Works [ontology_musical_works, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Levinson's indicated-structure account as the cleanest entry, the three intuitions it preserves, and the alternative positions (Wolterstorff's Platonism, Goodman's nominalism, Kivy's discovery-Platonism). Strong.
C3 (summary cold-readability): yes — "artwork ontology" is mild jargon but the summary immediately concretizes with the Beethoven's Fifth example and the menu of candidate answers (Platonic type, created abstract type, class of performances, action-type, structural type).

### N-11 — virtue_reliabilism
NODE: Virtue Reliabilism [virtue_reliabilism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Sosa's AAA structure (Accuracy, Adroitness, Aptness) as the load-bearing anchor, how aptness answers Gettier cases, and the position's location between traditional reliabilism and responsibilist virtue epistemology. Worked.
C3 (summary cold-readability): yes — "intellectual virtue" is glossed inline as "a stable cognitive competence"; the animal/reflective knowledge distinction carries its own parenthetical glosses.

### N-12 — compositionality_semantic
NODE: Compositionality (Semantic) [compositionality_semantic, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames the principle as the answer to "how do we understand sentences we have never encountered?", gives the productivity argument, notes the formal force in contemporary semantics, and shows how apparent counterexamples (idioms, opaque contexts, metaphor) are handled. Rich.
C3 (summary cold-readability): yes — "the meaning of a complex expression is determined by the meanings of its parts plus the way they are combined" is immediately clear and plain.

### N-13 — deontic_logic
NODE: Deontic Logic [deontic_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names where deontic logic is applied (ethics, legal theory, AI ethics), defines SDL, walks the three canonical paradoxes (Chisholm, Ross, gentle-murder) and the refinement each motivates. Very rich.
C3 (summary cold-readability): yes — borderline: the back half is dense ("the system K + D", "the seriality axiom", "a Kripke frame whose accessibility relation R", "deontically perfect worlds"), but the load-bearing first sentence — "The formal logic of obligation, permission, and prohibition" — is a complete, plain, cold-readable definition, and the summary expands "Standard Deontic Logic (SDL)" in full. The technical material is elaboration on a clean gloss, not the gloss itself. (Contrast N-8, which fails C3 precisely because it uses "SDL" undefined.)

### N-14 — research_programme
NODE: Research Programme (Lakatos) [research_programme, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks Lakatos's framework as a Popper-plus-Kuhn synthesis, the progressive/degenerating distinction with concrete examples (Newtonian mechanics; twentieth-century Marxist prediction), and the standard criticism. Rich.
C3 (summary cold-readability): yes — the technical terms ("hard core", "protective belt", "positive heuristic", "progressive", "degenerating") are each glossed inline as they are introduced.

### N-15 — argument_logical
NODE: Argument (Logical) [argument_logical, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames logical argument by explicit contrast with the everyday, rhetorical, and formal-semantic senses of "argument", grounds validity and soundness on the structural notion, and recommends walking a sample argument in the textbook display format. Worked.
C3 (summary cold-readability): yes — "a finite sequence of statements (the premises) followed by a single statement (the conclusion), where the premises are offered in support of the conclusion" is plain and self-contained.

### N-16 — scientific_explanation
NODE: Scientific Explanation [scientific_explanation, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes explanation from prediction and description, gives the Hempel-Oppenheim D-N model, the driving counterexamples (flagpole-and-shadow, irrelevant conjunction), and the four alternative account families (causal, mechanistic, IBE, unification). Very rich.
C3 (summary cold-readability): yes — "what it is for a scientific account to explain a phenomenon — to render it intelligible by exhibiting why it occurred or what it depends on" is plain; the explanation-vs-confirmation contrast is clearly drawn.

### N-17 — political_obligation
NODE: Political Obligation [political_obligation, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes obligation from duty and reasons, explains the content-independent/exclusionary character, lays out the philosophical-anarchist position, and walks every major theory with its standard objection, plus the practical-political implications. Extremely rich.
C3 (summary cold-readability): yes — "the moral duty (if there is one) to obey the law and support the institutions of one's political community" is plain; the distinction from political legitimacy ("legitimacy is the right to rule, obligation is the duty to obey") is explicitly glossed.

### N-18 — humean_regularity_theory
NODE: Humean Regularity Theory of Causation [humean_regularity_theory, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Hume's motivating epistemology (we observe conjunction, not necessity), the contemporary descendants (Mackie's INUS conditions, the Best-System Analysis), and the standard objections (spurious correlations, one-off causation, the missing asymmetry). Worked.
C3 (summary cold-readability): yes — "reductive theory" is mild jargon but the iff-definition spells the view out concretely (constant conjunction, temporal priority, spatiotemporal contiguity); the closing line ("what we call 'necessity' is a felt expectation in the observer") is plain.

### N-19 — conditional_probability
NODE: Conditional Probability [conditional_probability, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames conditional probability as the bridge from the static measure to the dynamic activity of updating, walks the definitional formula and the renormalization, gives a concrete fair-die worked example, and connects to independence, total probability, Bayes, and the philosophical applications. Excellent foothold.
C3 (summary cold-readability): yes — the plain-language opening ("the probability of one event given another") is a clean cold-readable gloss; the formula P(A|B) = P(A ∩ B)/P(B) is elaboration on it, not a substitute for it.

### N-20 — global_workspace_theory
NODE: Global Workspace Theory [global_workspace_theory, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the core claim, why GWT shines at the easy problems (reportability, capacity limits, cross-modal integration), what it leaves underaddressed (the hard problem / P-consciousness), and the defenders/critics. Worked.
C3 (summary cold-readability): yes — "consciousness arises from the global broadcasting of information across the brain: a piece of information becomes conscious when it is selected for entry into a global workspace and made available to specialized cognitive processes" is plain and concrete.

## Shard tally
- Edges: 27 total | Reversed 1 | Weak-redundant 0 | defective 1 (3.7%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 1 (5.0%) | teaching_notes ABSENT 0

## Cross-cutting observations (optional)
- C1 defect rate is 3.7% (1/27 — E-7 property_dualism → philosophical_zombie, Reversed). Running C1 across shards 01–05: 10.7% / 3.6% / 3.6% / 0.0% / 3.7% — the census continues to track in the 0–4% band well below the production audit's 13% baseline (shard 01 the standing outlier).
- The single defect (E-7) is notable in *kind*: it is the exact structural shape — position → motivating thought experiment — that the production audit's migration 0062 already flipped for the sibling pair property_dualism → knowledge_argument. E-7 reads as a fresh authoring defect the audit's own 0062 logic would catch; the closeout should weigh it as a candidate 0062-consistency follow-up.
- Three audit-touched edges this shard, all behaving as expected: E-11 (tarskis_t_schema → deflationary_theory_of_truth) and E-27 (propositional_attitude → epistemic_justification) are post-0062-flip directions and both verify Sound on their corrected directions. E-20 (supervenience_mental → mental_causation) is the interesting one — 0064 *annotated* rather than flipped it, and the annotation the audit attached argues the target is conceptually prior; scored Defensible, flagged for the closeout as the rare "audit evidence in tension with the edge it annotates" case.
- First C3 failure of the census: N-8 (ross_paradox), jargon-gated on the unexpanded acronym "SDL" plus "modal closure on disjunction-introduction" in the summary's load-bearing first sentence. Worth a closeout cross-check against N-13 (deontic_logic), which handles the *same* apparatus correctly by expanding "Standard Deontic Logic (SDL)" in full — the failure is a localized authoring slip (acronym used before definition), not a subdomain-wide pattern.
- This shard ran four Defensible verdicts (E-12, E-13, E-20, E-23) against shard 04's one — driven by a cluster of political-philosophy and philosophy-of-mind edges that are supportable-but-not-canonical secondary prerequisites (distributive_justice → communitarianism with E-10 supplying the more proximate prereq; just_war_theory → pacifism at weight 0.85; mental_causation → eliminative_materialism). None are defects, but the closeout's consistency review should check whether shards scoring similar secondary-prerequisite shapes scored them Sound.
