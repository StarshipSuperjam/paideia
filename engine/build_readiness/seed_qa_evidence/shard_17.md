# Seed-graph QA census evidence — shard 17

> Authored by S-0179 (routine session) per T-SEED-QA task SQA-17.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 17
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — 8a812a11-5097-4745-b72d-f21ea8ed33cb
EDGE: Modal Logic [modal_logic, logic] → Accessibility Relation [accessibility_relation, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Modal logic is the formal system; the accessibility relation (R(w, w')) is the Kripke-semantic technical device internal to the system, governing which worlds count as possible from which. Pedagogically you introduce modal logic (□, ◇, the modal axioms K/T/4/5), then introduce the accessibility relation as the semantic apparatus that gives the axioms their interpretation. Framework → its internal technical apparatus; same shape as the framework-introduces-its-component pattern across prior shards.
AUDIT-TOUCHED: none

### E-2 — 122f431d-0585-49c4-8558-3c1a36993314
EDGE: Propositional Logic [propositional_logic, logic] → Material Conditional [material_conditional, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional logic is the umbrella formal system; the material conditional (P → Q, defined by the truth table that makes the conditional false only when P is true and Q is false) is one of its five canonical connectives. Umbrella → its component connective, canonical Sound shape. N-18 propositional_logic (shard 16) explicitly listed material conditional among the five connectives — the species relation is encoded in the source's own teaching content.
AUDIT-TOUCHED: none

### E-3 — 16e8d376-751f-4cf0-922a-3eb4f5a0bf9f
EDGE: Evidence [evidence, epistemology] → Epistemic Justification [epistemic_justification, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Evidence is the more basic epistemic notion (what supports beliefs); epistemic justification is what evidence is supposed to confer on belief (a belief is justified to the extent it is properly supported by evidence). Concept → its consequence. Pedagogically you teach what counts as evidence (testimony, perception, reasoning) before you take up the theory of when evidence justifies belief (foundationalism, coherentism, evidentialism). Note: 0062 touches the *propositional_attitude ↔ epistemic_justification* tuple, not this one — proximity false-positive narrowed out.
AUDIT-TOUCHED: none

### E-4 — 1096b523-2f91-427d-b7fe-1ec8512570b4
EDGE: Art Criticism [art_criticism, aesthetics] → Intentionalism (Artistic) [intentionalism_artistic, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Art criticism is the umbrella practice (interpreting and evaluating artworks); artistic intentionalism is one specific position within it (the artist's intentions determine the meaning of the work — opposed by Wimsatt & Beardsley's 1946 anti-intentionalist "Intentional Fallacy," defended in moderated forms by Hirsch and Knapp & Michaels). Practice/field → position-within-it. Same shape as E-7, E-14, E-19 etc.
AUDIT-TOUCHED: none

### E-5 — 9000f480-0ee0-4a4b-81f0-52436f8d9abd
EDGE: Testimonial Knowledge [testimonial_knowledge, epistemology] → Social Epistemology [social_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: This edge runs sub-topic → field, the inverse of the standard field → topic shape that dominates Sound calls. Defensible on the historical-priority + foothold reading: testimony is a long-standing analytic-epistemology topic (Reid, Hume; revived in contemporary form by Coady 1992 *Testimony*, Lackey, Adler) that historically motivated the broader social-epistemology framework (Goldman 1999 *Knowledge in a Social World* takes testimony as a paradigm case alongside judgment aggregation and group knowledge). The pedagogical move "introduce testimony as the entry point to social epistemology" is supported by major textbooks. But the canonical pedagogical convention is field → topic, which would run the edge reversed (social_epistemology → testimonial_knowledge). Both directions have force. Flag for SQA-20: this is a new Defensible sub-shape for the routine batch — *specific-topic → umbrella-field*, distinct from the framework→concept Defensibles (shard 13 E-15, shard 14 E-17), the canonical-direction-inversion Defensibles (shards 14/15/16 0064 cluster), and the co-fundamental-category Defensibles (shard 16 E-25).
AUDIT-TOUCHED: none

### E-6 — 6653db7c-1d6b-40bf-acc1-62d441f4ee65
EDGE: Consequentialism [consequentialism, ethics] → Supererogation [supererogation, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Supererogation (acts morally praiseworthy but not morally required — Urmson 1958 "Saints and Heroes") is a normative-ethical category any normative theory must address, not a consequentialism-internal concept. Aquinas (within Christian ethics) and Kant (via imperfect duties) handle it; Wolf 1982 "Moral Saints" engages it within Kantian and virtue frameworks. The edge claims consequentialism is the prerequisite of supererogation, but the concept stands without consequentialism — pedagogically, supererogation as a normative-ethical phenomenon comes first, with consequentialism as one theory that struggles to accommodate it (Scheffler 1982). Defensible on the "introduce consequentialism, then introduce supererogation as a problem case it must handle" pedagogical pathway — that's a real pedagogical move (Singer's 1972 demandingness argument turns on consequentialism's apparent failure to allow space for the supererogatory). But not a strict prerequisite. Same general "theory → topic-it-struggles-with" sub-shape as E-5 above; the two Defensibles in this shard share the "inverse of the canonical field→topic / umbrella→species" structural feature, recorded for SQA-20.
AUDIT-TOUCHED: none

### E-7 — 874f4fc4-b0eb-4a81-b9f2-baa6f1246520
EDGE: Demarcation Problem [demarcation_problem, science] → Falsificationism [falsificationism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The demarcation problem (what distinguishes science from non-science / pseudoscience?) is the philosophy-of-science question; falsificationism (Popper 1934/1959 *Logik der Forschung* / *Logic of Scientific Discovery*) is one specific answer (a theory is scientific iff it makes risky falsifiable predictions). Question → answer; same shape as E-26 below. Audit cross-reference: 0061 touches *vienna_circle_logical_positivism → falsificationism* (different source), proximity hit narrowed out by exact-tuple inspection.
AUDIT-TOUCHED: none

### E-8 — ae3f6d4e-5218-4b12-8800-b613454f6b7c
EDGE: Concrete Object [concrete_object, metaphysics] → Mereology [mereology, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Concrete objects (tables, organisms, planets) are the intuitive instances that motivate mereological questions about parthood; mereology is the formal theory of parthood relations (Leśniewski 1916, Leonard & Goodman 1940). Pedagogically you introduce concrete objects as the intuitive case, then ask the mereological question (when do parts compose a whole? what is the relation between a whole and its proper parts?). Instance-class → theory-of-its-structure. The reverse direction (mereology → concrete_object) would also be defensible (you can do mereology abstractly without concretes), but the given direction tracks how van Inwagen 1990 *Material Beings* and most introductory metaphysics texts present it.
AUDIT-TOUCHED: none

### E-9 — 2b1c70a1-fe1a-41f1-9b75-20b8fc251867
EDGE: Environmental Ethics [environmental_ethics, ethics] → Ecocentrism [ecocentrism, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Environmental ethics is the umbrella sub-field of applied ethics; ecocentrism (Leopold 1949 *A Sand County Almanac* land ethic, Naess 1973 deep ecology, Callicott) is one specific position within it (the ecosystem itself, not just sentient individuals, is the locus of moral value — vs anthropocentrism and biocentrism). Umbrella → position. Same shape as E-19, E-27.
AUDIT-TOUCHED: none

### E-10 — 82b3b9c9-ca89-40d6-80c5-e210433339b3
EDGE: Political Philosophy [political_philosophy, political] → State (Political) [state_political, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Political philosophy is the umbrella domain; the state is one of its central topics (what is the state? what makes states legitimate? what are the limits of state power? — Hobbes, Locke, Weber, Nozick). Field → central topic. Same shape as E-4, E-26.
AUDIT-TOUCHED: none

### E-11 — 146ed437-cddb-4ccb-b80f-a9b7c9404adb
EDGE: Existence [existence, metaphysics] → Concrete Object [concrete_object, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Existence is the umbrella metaphysical category (what is there? Quine's criterion of ontological commitment); concrete objects are one canonical species of existent (vs abstract objects — numbers, propositions, properties under non-nominalist construals). Umbrella → species. Pedagogically you introduce the existence-question (what counts as an entity? what is it for something to exist?), then take up the concrete/abstract distinction. Standard contrast with shard 16 E-25 (existence → relation, scored Defensible there) — concrete_object is a much cleaner species-of-existent than relation, which sits parallel to existence as a co-fundamental category.
AUDIT-TOUCHED: none

### E-12 — 9050a7f1-5de5-47a7-b85d-3a96a724e6c8
EDGE: Tracking Theory of Knowledge [tracking_theory_of_knowledge, epistemology] → Sensitivity Condition [sensitivity_condition, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nozick's 1981 tracking theory (*Philosophical Explanations*) analyzes knowledge in terms of sensitivity (counterfactual: had p been false, S would not have believed p) + adherence (in close worlds where p remains true, S still believes p). The sensitivity condition is a technical component-concept of the tracking theory — framework-internal, even though "sensitivity" has a broader intuitive sense. Framework → component-concept; same shape as shard 16 E-2/E-10/E-20 (four_principles_bioethics → its component principles). Pairs structurally with shard 16 N-14 safety_condition (the Sosa refinement that is sometimes contrasted with sensitivity).
AUDIT-TOUCHED: none

### E-13 — 444c0202-b798-4adb-a871-41f11048aa6b
EDGE: Art [art, aesthetics] → Pictorial Representation [pictorial_representation, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Art is the umbrella aesthetic category; pictorial representation is one specific topic within philosophy of art (how do pictures depict their subjects? — Goodman 1968 *Languages of Art* symbol-systems, Wollheim 1980 seeing-in, Hopkins 1998 experienced-resemblance, Lopes 1996). Umbrella → topic. Same shape as E-23.
AUDIT-TOUCHED: none

### E-14 — 100b0de7-eb6b-4638-b6e9-7f47f22591b1
EDGE: Normative Ethics [normative_ethics, ethics] → Deontology [deontology, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Normative ethics is the umbrella domain; deontology is one of its three canonical position-families (with consequentialism and virtue ethics — Kantian rule-based ethics, Rossian prima-facie duties, contemporary contractualism). Umbrella → species; canonical Sound shape (see also shard 16 E-7 reliabilism → virtue_reliabilism, E-19 normative_ethics → moral_particularism).
AUDIT-TOUCHED: none

### E-15 — 5b47ebd4-6bcf-4abd-8c8c-2283eedd4629
EDGE: Social Contract Theory [social_contract_theory, political] → Justice as Fairness (Rawls) [justice_as_fairness, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Social contract theory is the umbrella tradition (Hobbes/Locke/Rousseau, with Rawls as the decisive contemporary revival); Rawls's *justice as fairness* (1971 *A Theory of Justice*) is one specific contemporary contractualist version — the original position with veil of ignorance is explicitly a contract-tradition device for deriving principles of justice. Tradition → species; encoded in N-5's own teaching content (which lists Rawls as "updating the tradition by replacing actual consent with hypothetical consent in the original position"). Same shape as E-14.
AUDIT-TOUCHED: none

### E-16 — 66207e58-b5b5-4516-8b45-ec77f0219c5a
EDGE: Time [time, metaphysics] → A-Theory of Time [a_theory_of_time, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Time is the umbrella metaphysical topic; A-theory (McTaggart 1908's A-series — past/present/future ontologically distinguished; tense is real; presentism and growing-block are A-theoretic) is one specific position about time's nature, contrasted with B-theory (the tenseless block universe, eternalism). Umbrella → position. Audit cross-reference: 0063 mentions *time → a_theory_of_time* only as the surviving proximate path after deleting *time → mctaggarts_paradox* (long-distance shortcut); this edge itself was NOT modified by 0063 — proximity false-positive narrowed out by reading the context.
AUDIT-TOUCHED: none

### E-17 — 2d1ae965-7d6a-45b5-b20d-a5611946efeb
EDGE: Research Ethics [research_ethics, ethics] → Informed Consent [informed_consent, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Research ethics is the umbrella sub-field (Nuremberg → Belmont → Common Rule, with Emanuel-Wendler-Grady 2000 seven requirements as a contemporary anchor); informed consent is its central procedural principle — the operationalization of Belmont's "Respect for Persons" principle. Field → its central principle. N-13 research_ethics (shard 16) explicitly listed informed consent in its core teaching scaffold. Pairs structurally with E-27 below (bioethics → research_ethics, the umbrella-to-sub-field relation one level up).
AUDIT-TOUCHED: none

### E-18 — e24ddc3a-15c4-495a-846a-dfa919b0fb34
EDGE: Kantian Ethics [kantian_ethics, ethics] → Categorical Imperative [categorical_imperative, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kantian ethics is the umbrella framework; the categorical imperative (Kant 1785 *Groundwork* — Formula of Universal Law, Formula of Humanity, Formula of Autonomy / Kingdom of Ends) is its central principle. Pedagogically you introduce Kant's ethical project (deontology grounded in rational agency, the supreme principle of morality), then state and unpack the CI's formulations. Framework → central principle; same shape as E-12 (tracking_theory → sensitivity_condition), E-15 (social_contract → justice_as_fairness), and shard 16 E-2/E-10/E-20 (framework → component principles).
AUDIT-TOUCHED: none

### E-19 — 49617b2c-577a-444c-b14f-02bac81f737a
EDGE: Personal Identity [personal_identity, mind] → Animalism [animalism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Personal identity is the umbrella diachronic-identity question (Locke's memory criterion, Parfit's psychological continuity, Olson's animalism, bodily-continuity); animalism (Olson 1997 *The Human Animal*) is one specific position — we ARE human animals, and our persistence tracks biological continuity, not psychological continuity. Umbrella → position. Same shape as E-14, E-15. N-9 personal_identity (shard 16) explicitly listed animalism among the contemporary position-family taxonomy.
AUDIT-TOUCHED: none

### E-20 — b4077fbb-eb7c-491a-83c5-5d02473c39b3
EDGE: Gricean Maxims (Cooperative Principle) [gricean_maxims, language] → Conversational Implicature [conversational_implicature, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Grice's cooperative principle and the four maxims (Quality, Quantity, Relation, Manner — Grice 1975 "Logic and Conversation") are the pragmatic machinery; conversational implicature is what the maxims explain — the gap between what is said (semantic content) and what is communicated (pragmatic content), derived via the assumption that the speaker is observing the maxims (or flouting them visibly). Machinery → its explanandum; canonical pedagogical move in formal pragmatics. Same shape as the framework-introduces-its-component pattern.
AUDIT-TOUCHED: none

### E-21 — cd93cabc-8ef6-4815-9560-ded56e0f9f70
EDGE: Causation [causation, metaphysics] → Mental Causation [mental_causation, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Causation is the general metaphysical relation between events/states; mental causation is the philosophy-of-mind specialization of the question (how do mental events causally interact with physical events — the exclusion problem, Kim's reductive arguments, the supervenience puzzle). General → domain-specific-application; canonical cross-domain shape. Audit cross-reference: 0064 touches *supervenience_mental → mental_causation*, NOT *causation → mental_causation* — proximity false-positive narrowed out by exact-tuple inspection (same workflow note as shard 14/15/16).
AUDIT-TOUCHED: none

### E-22 — 8907d5c2-8813-4678-ace7-18c037bc224a
EDGE: Modality [modality, metaphysics] → Modal Logic [modal_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Modality is the metaphysical phenomenon (possibility, necessity, contingency, impossibility — what could have been, what must be); modal logic is the formal apparatus for reasoning about modality (Lewis-Kripke possible-worlds semantics, the axioms K/T/4/5/B). Phenomenon → its formal apparatus. Pedagogically you introduce modal notions (you grasp "necessarily," "possibly" in natural language and metaphysics), then introduce the formal system. Pairs structurally with E-1 (modal_logic → accessibility_relation) — this shard chains modality → modal_logic → accessibility_relation, the natural pedagogical ladder.
AUDIT-TOUCHED: none

### E-23 — 569da0d4-8e94-40e2-b015-5d78cb69123c
EDGE: Ontology of Artworks [ontology_of_artworks, aesthetics] → Type-Token Distinction (Artworks) [type_token_artworks_distinction, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Ontology of artworks is the umbrella question (what kind of thing is an artwork? — a physical object, an abstract type, a performance, an action?); the type-token framework (Wolterstorff 1980, Wollheim 1968, Currie 1989 *An Ontology of Art*) is one specific apparatus for answering it (a musical work is a type; particular performances are tokens). Field-question → framework-for-answering-it. Same shape as E-13.
AUDIT-TOUCHED: none

### E-24 — eb6b5212-2d2f-4511-8009-af4e3668c9a7
EDGE: Aesthetic Experience [aesthetic_experience, aesthetics] → Expression Theory of Art [expression_theory_art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Aesthetic experience is the experiential phenomenon (the qualitative response to art and to natural beauty — Kantian disinterested pleasure, Beardsley's intensity/coherence/complexity, Stolnitz's aesthetic attitude); the expression theory (Croce 1902, Collingwood 1938 *Principles of Art*, Tolstoy 1898 *What Is Art?*) is one specific theory of what art is — art expresses emotion, and the audience's aesthetic experience is the re-experiencing of the expressed emotion. Phenomenon → specific-theory-that-explains-the-phenomenon. The N-19 imitation_theory_art teaching notes explicitly note "the expression and formalist theories arose specifically as responses to" imitation theory's inadequacies — the expression theory is one of three canonical answer-families to what art is.
AUDIT-TOUCHED: none

### E-25 — 113a97c0-17ae-4d8f-8afa-f83e2b257508
EDGE: Causal Theory of Reference [causal_theory_of_reference, language] → Rigid Designator [rigid_designator, language]
  weight=1.0, confidence=1.0, evidence=Per S-0122 audit: Rigid designators are paradigmatically explained via causal-historical accounts of reference (Kripke 1972, Putnam); the designator concept is motivated by and interpreted through causal-reference semantics.
VERDICT: Sound
RATIONALE: Audit-validated framework-introduces-concept reading (0064 LAN-E-5 retain-with-annotation evidence backfill per S-0122). Rigid designators (Kripke 1972 *Naming and Necessity* — terms that refer to the same individual in every possible world where the individual exists) are paradigmatically introduced and motivated through causal-historical reference semantics (Kripke's baptism-and-causal-chain story; Putnam's "meanings just ain't in the head"). The causal theory of reference is the framework; rigid designation is the central concept within it. Same retain-with-annotation evidence-backfill shape as shard 13 E-19 bayesian_epistemology → dutch_book, shard 15 E-7 fictional_truth → metaphor and E-21 social_contract_theory → political_legitimacy, shard 16 E-17 speech_act → presupposition (all 0064 retain-with-annotation). Inline `evidence` text confirms the audit decision — the gold signal per the shard 13–16 workflow learnings.
AUDIT-TOUCHED: migration 0064 LAN-E-5 — evidence backfill / retain-with-annotation. Inline `evidence` text confirms the audit decision.

### E-26 — 0eb3e754-4743-49d5-8261-c374346f2d99
EDGE: Philosophy of Science [philosophy_of_science, science] → Scientific Theory [scientific_theory, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Philosophy of science is the umbrella field; "scientific theory" is one of its central topics — what is a scientific theory? (the received view's syntactic-axiomatic account; the Suppes/van Fraassen semantic / model-theoretic account; the structural-realist account). Field → central topic. Same shape as E-4, E-10.
AUDIT-TOUCHED: none

### E-27 — d428d89f-05fc-49f3-9139-7750559ed0cd
EDGE: Bioethics [bioethics, ethics] → Research Ethics [research_ethics, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Bioethics is the umbrella sub-field of applied ethics covering biomedical-ethics-broadly; research ethics is one of its principal sub-areas (alongside clinical ethics and public-health ethics). N-13 research_ethics (shard 16) explicitly opens with "branch of bioethics treating moral questions in biomedical and behavioral research with human subjects" — the umbrella relation is encoded in the target's own teaching content. Umbrella → sub-area. Same shape as shard 16 E-9 applied_ethics → bioethics, one level down. The shard contains a three-edge applied-ethics ladder: bioethics → research_ethics (E-27), research_ethics → informed_consent (E-17), and at one further level shard 16 chained applied_ethics → bioethics.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — internalism_epistemic
NODE: Epistemic Internalism [internalism_epistemic, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names two main motivations (deontological intuition: responsibility only for what one can access; new-evil-demon intuition: BIV with same internal states is equally justified) and the contemporary version (Conee & Feldman mentalism). Compact but functional foothold.
C3 (summary cold-readability): yes — "factors that determine whether a belief is justified are factors to which the believer has reflective access — typically her other mental states" is fully accessible; contrast with externalism (reliable causal processes outside the believer's ken) sharpens the position.

### N-2 — axiom_mathematical
NODE: Axiom (Mathematical) [axiom_mathematical, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1300+ chars) walk through the two-senses distinction (Aristotelian-Euclidean self-evident-truth vs Hilbertian stipulation), the historical revolution driven by non-Euclidean geometries (Lobachevsky, Bolyai, Riemann), Gödel's incompleteness as the deep reason axiom-choice is creative-not-mechanical, and the syntactic-vs-semantic / proof-vs-truth pedagogical entry-point framing. Strong.
C3 (summary cold-readability): yes — "primitive-statement-assumed concept of formal systems: a statement taken as a starting point of a system without proof, used together with inference rules to derive the system's theorems" is parsable; the older vs modern senses distinguished plainly; canonical axiomatizations (Peano, ZFC, Hilbert, field, topological-space) enumerated.

### N-3 — ethical_egoism
NODE: Ethical Egoism [ethical_egoism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1500+ chars) walk through the three-fold distinction (ethical / psychological / moral egoism), three defenses (agent-relativity, rational-choice foundations, Hobbesian reduction to enlightened self-interest), three classical objections (other-regarding-obligation counterexamples, Parfit 1984 self-defeating, impartiality), and explicit minority-theory framing. Strong, well-scaffolded.
C3 (summary cold-readability): yes — "the normative theory that the right action for an agent is the one that maximizes the agent's OWN long-term self-interest" is fully accessible; psychological-vs-ethical distinction made explicit; defenders named (Rand, Hobbes-interpretive, Brink 1989).

### N-4 — closure_denial
NODE: Closure Denial [closure_denial, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames closure denial as the price both Dretske and Nozick pay for their anti-skeptical strategies and the price most other epistemologists are unwilling to pay; contextualism named as the response that tries to keep both anti-skepticism and closure. Brief but functional foothold.
C3 (summary cold-readability): yes — "epistemic closure under known entailment fails: one can know p without knowing all the consequences one knows to follow from p" is fully accessible; Dretske 1970 and Nozick 1981 dated with their respective devices (relevant alternatives / sensitivity).

### N-5 — social_contract_theory
NODE: Social Contract Theory [social_contract_theory, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1600+ chars) walk through the master-strategy framing, the canonical historical sequence (Hobbes/Locke/Rousseau/Rawls) each with its distinctive contractarian move, structural variations (actual vs hypothetical consent, state of nature as descriptive vs heuristic, form of agreement), historical-political vs moral contract distinction (Scanlon 1998), and standard objections (state of nature is fiction; Hume 1748 on tacit consent; Dworkin 1973 on hypothetical consent). Strong.
C3 (summary cold-readability): yes — "tradition of grounding political authority and political obligation in actual or hypothetical agreement among the governed" is fully accessible; founding works dated (Hobbes 1651, Locke 1689, Rousseau 1762, Rawls 1971) with each thinker's specific move.

### N-6 — type_identity_theory
NODE: Type-Identity Theory [type_identity_theory, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames type-identity as "the cleanest physicalist position before functionalism complicates the picture"; parsimony motivation; the canonical multiple-realizability objection (Putnam 1967 — octopuses, Martians, humans with same belief but different brain types); the lesson functionalism draws (mental types must be individuated more abstractly). Strong.
C3 (summary cold-readability): yes — "mental state types are identical to brain state types: pain IS C-fiber firing" — the canonical Place-Smart pain-is-C-fiber-firing example serves as the working gloss; defenders dated (Place 1956, Smart 1959, Lewis 1966, Armstrong 1968).

### N-7 — presupposition
NODE: Presupposition [presupposition, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1500+ chars) walk through the Strawson move against Russell's theory of descriptions ("the king of France is bald" — presupposition failure means the question of bald-vs-not doesn't arise), behavior under embedding (projection through negation/questions/modals as the technical signature), Stalnaker's common-ground formalization, the taxonomy of presupposition triggers (definite descriptions, factive verbs, change-of-state verbs, clefts, focus-sensitive operators), and presupposition-failure repair strategies. Strong.
C3 (summary cold-readability): yes — three canonical example sentences ("the king of France is bald" / "John stopped smoking" / "It was Mary who broke the window") carry the concept; the behavior-under-negation diagnostic spelled out; Strawson 1950 and Stalnaker named.

### N-8 — formal_epistemology
NODE: Formal Epistemology [formal_epistemology, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "methodologically continuous with classical epistemology but substitutes precise models for informal arguments"; useful exemplars (Bayesian conditionalization formalizes Hume's induction problem; lottery and preface paradoxes formalize tensions between certainty and partial belief); Hájek and Hendricks's *Probabilistic Methods in Cognitive Science* as standard introduction. Compact but functional foothold.
C3 (summary cold-readability): yes — "application of formal tools (probability theory, logic, decision theory, computability theory) to epistemological problems" is fully accessible; the four sub-areas enumerated (Bayesian epistemology, formal learning theory, judgment aggregation, probabilistic-reasoning epistemology).

### N-9 — composition_mereological
NODE: Composition (Mereological) [composition_mereological, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — van Inwagen 1990 *Material Beings* as the contemporary anchor with his near-nihilist organisms-only view; Lewis/Sider universalism as simplest answer (unrestricted composition, every fusion exists); Markosian's contact-based moderate view with the arbitrariness charge against it; explicit framing of the dispute's stakes (not just which everyday objects exist but whether composition can be principled). Strong dialectical scaffold.
C3 (summary cold-readability): yes — "relation that holds when some objects (the parts) make up a further object (the whole)" is fully accessible; the Special Composition Question (van Inwagen 1990) stated as "under what conditions do some objects compose a further object?"; three positions enumerated (universalism / nihilism / moderate views).

### N-10 — pyrrhonian_skepticism
NODE: Pyrrhonian Skepticism [pyrrhonian_skepticism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Sextus's modes named (ten tropes of Aenesidemus, five of Agrippa) as the systematic generator of equipollent arguments; Agrippan trilemma (regress / circularity / arbitrary stopping) as the crystallizing structural problem; explicit distinction from academic skepticism (the dogmatic claim that nothing can be known). Compact but well-shaped foothold.
C3 (summary cold-readability): yes — borderline-PASS. Greek technical terms (*epoché*, *ataraxia*) appear but are immediately glossed inline ("suspending judgment (epoché)", "tranquility (ataraxia)"); founders named (Pyrrho, Sextus Empiricus); Cartesian-skepticism contrast supplies the working differential. Same calibration as N-9 personal_identity "diachronic" in shard 16 — load-bearing technical term gated through an in-line parenthetical gloss.

### N-11 — semantic_paradox
NODE: Semantic Paradox [semantic_paradox, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1300+ chars) walk through the canonical structural fact (T-schema + closure under conjunction + self-reference → contradiction in classical logic) and the five dominant responses (Tarskian hierarchy / Kripkean fixed-point 1975 / Gupta-Belnap revision 1993 / Field 2008 paracomplete / Priest 1979 paraconsistent-dialetheic); framing of semantic paradoxes as "the clearest case where revising classical logic is *motivated by the data*." Strong.
C3 (summary cold-readability): yes — "family of paradoxes generated by self-referential or improperly stratified semantic notions — truth, satisfaction, denotation, definability" — the technical descriptors (*self-referential*, *improperly stratified*) are load-bearing but immediately concretized by the example list (liar, Curry, Berry, Grelling-Nelson, Richard paradoxes); the set-theoretic-paradox distinction (Russell, Burali-Forti, Cantor) anchors the type difference. Borderline-PASS on the example-as-gloss calibration.

### N-12 — functional_role_semantics
NODE: Functional-Role Semantics [functional_role_semantics, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — narrow (intra-cranial) vs wide (world-involving) functional-role distinction; Block 1986 / Harman 1987 / Field defenders; holism objection (Fodor-LePore 1992 — content depends on inferential role, roles depend on the network, so any belief change changes everyone's contents → meaning incommensurable); the meaning-constitutive-vs-incidental response (Harman, Block). Strong dialectical scaffold.
C3 (summary cold-readability): yes — "mental content is determined by the functional or inferential role a state plays in the agent's overall mental economy: what a belief means is fixed by what it disposes its bearer to infer, perceive, and do" — the *functional/inferential role* technical descriptor is immediately operationalized ("what disposes its bearer to infer, perceive, and do"); functionalism-pairing flagged.

### N-13 — animal_ethics
NODE: Animal Ethics [animal_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extremely extensive (3000+ chars) walk through the foundational pair (Singer 1975 *Animal Liberation* utilitarian / Regan 1983 *Case for Animal Rights* deontological — each laid out with their core argument), the question of which animals count (sentience criterion vs subjects-of-a-life), and contemporary developments (Hursthouse 2006 virtue / Donovan-Adams 2007 care / Nussbaum 2006 capabilities / Donaldson-Kymlicka 2011 *Zoopolis* political). The most pedagogically scaffolded animal-ethics intro I've seen across 17 shards.
C3 (summary cold-readability): yes — "branch of applied ethics treating moral questions about humans' relations to non-human animals" with full enumeration of contexts (food, clothing, research, entertainment, companionship); founding works dated (Singer 1975, Regan 1983); distinction from broader environmental-ethics (animal individuals vs ecosystems) and from anthropocentric-welfare framing (animals matter on their own account, not because humans care). Cross-bridges to philosophy-of-mind defer to P5-11.

### N-14 — non_identity_problem
NODE: Non-Identity Problem [non_identity_problem, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (2500+ chars) walk through Parfit's 1984 statement, the DEPLETION-vs-CONSERVATION canonical example demonstrating different-populations-under-different-policies, Parfit's same-people / different-people distinction and the development of impersonal outcome-based ethics, the repugnant-conclusion connection, and the narrow vs wide person-affecting taxonomy that handles non-identity at varying theoretical costs. Strong.
C3 (summary cold-readability): yes — Parfit 1984 *Reasons and Persons* chapter 16 cited; the 14-year-old girl example carries the concept ("had she waited, this child would not exist; the alternative is non-existence, not a different and better life for the same person"); generalization to climate / population / policy named.

### N-15 — qualia_realism
NODE: Qualia Realism [qualia_realism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames qualia realism as the position eliminativists and functionalists are denying; metaphysical complements enumerated (Chalmers naturalistic dualism, Block NCC physicalism, Strawson/Goff panpsychism); the appeal (respect for the face value of phenomenal experience — "what we directly know about pain seems to be its painfulness, not its functional role") and the costs (explanatory: how do irreducible qualia fit into a physical world?) laid out symmetrically. Strong.
C3 (summary cold-readability): yes — "qualia are real, irreducible, non-functional, intrinsic properties of conscious experience" — the four-feature gloss (real / irreducible / non-functional / intrinsic) defines the position structurally; defenders dated (Block 1990, Chalmers 1996, Jackson 1982 pre-retraction); opponents enumerated (qualia eliminativism: Dennett, Frankish; qualia functionalism: Lewis, Lycan; qualia representationalism: Tye, Dretske).

### N-16 — causation
NODE: Causation [causation, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Hume's starting move (deny direct perception of causal connection — observe constant conjunction, infer causation); the post-Humean tradition split (regularity theories / Lewis counterfactual / Aristotelian-Mumford-Anjum causal powers); pedagogical recommendation to teach the three theories in dialogue rather than serially. Compact but well-shaped.
C3 (summary cold-readability): yes — "relation between cause and effect — what one event or state of affairs does to bring another about" is fully accessible; the four contexts where causal talk arises (scientific explanation, ordinary action description, legal responsibility, counterfactual reasoning) supply the working terrain; three contemporary accounts enumerated.

### N-17 — sublime
NODE: Sublime [sublime, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Burke 1757 (*A Philosophical Enquiry*) terror-modified-by-security-of-observer account, systematically contrasted with the beautiful (small/smooth/gradual/easy vs vast/obscure/powerful/difficult); Kant 1790 (*Critique of the Power of Judgment*) bifurcation into mathematical sublime (imagination fails, reason supplies infinity) and dynamical sublime (nature's might contemplated from safety, supersensible idea of human dignity). Pedagogical framing of the sublime as the entry to aesthetic categories beyond beauty. Strong.
C3 (summary cold-readability): yes — "aesthetic category complementary to the beautiful, characterized by a complex pleasurable response to objects that overwhelm the senses or imagination" is fully accessible; examples enumerated (vast natural scenes, cosmic magnitudes, terrifying spectacles); Burke 1757 and Kant 1790 dated with their respective accounts.

### N-18 — autonomy_bioethical
NODE: Autonomy (Bioethical) [autonomy_bioethical, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (2300+ chars) walk through the historical shift from benevolent-concealment medical paternalism, multiple drivers (civil-rights / women's movements; high-profile cases Quinlan 1976; legal developments Salgo v. Stanford 1957 / Cruzan 1990; Beauchamp & Childress 1979 codification), contemporary operationalizations (informed consent, advance directives, refusal of treatment, surrogate decision-making), and the principle's limits and tensions (competent-adults qualification; conflicts with beneficence and non-maleficence; criticism as thin proceduralism vs richer philosophical-autonomy conceptions). Strong.
C3 (summary cold-readability): yes — "competent adults have the right to make decisions about their own medical care, free from coercion or paternalistic override" is fully accessible; historical corrective framing (vs older medical paternalism) supplies orientation; operationalization mechanisms enumerated (informed consent, advance directives, right to refuse treatment); distinction from broader political/metaphysical autonomy conceptions (Kantian, Millian, political self-determination) explicit.

### N-19 — imitation_theory_art
NODE: Imitation Theory of Art [imitation_theory_art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — historical anchor framing (the theory against which expression and formalism define themselves); strengths (captures figurative painting, sculpture, drama, narrative literature); three standard objections (extensional inadequacy: non-representational music/abstract painting; under-specification: counterfeits and mirrors imitate without being art; misdirection: even of representational arts, what makes them art is imitation done well, suggesting the theory needs supplementation); explicit framing of why expression and formalist theories arose as responses. Strong.
C3 (summary cold-readability): yes — *mimesis* is Greek but immediately glossed by "imitation of reality"; the four targets of imitation enumerated (natural appearances, human actions, character, emotion); Plato (*Republic* Books 3, 10) and Aristotle (*Poetics*) given as the founding pair with their respective treatments (Plato suspicious / Aristotle positive via catharsis); historical scope of dominance (Western art theory through early modern) framed.

### N-20 — reliabilism
NODE: Reliabilism [reliabilism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — pedagogical framing against internalism (BIV with internally-indistinguishable mental states from yours would be justified on internalism but not on reliabilism, because its processes are unreliable); two canonical objections named (new-evil-demon problem / generality problem); Goldman 1979 'What Is Justified Belief?' as foundational paper. Compact but well-targeted.
C3 (summary cold-readability): yes — "belief is justified iff it is produced by a reliable cognitive process — one that produces a high ratio of true beliefs to false beliefs" is fully accessible; Goldman 1979 cited; the externalist framing (world-involving property, not internally accessible) supplies the position's structural feature.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0
- Defensible: 2 (E-5 testimonial_knowledge → social_epistemology — new "specific-topic → umbrella-field" sub-shape; E-6 consequentialism → supererogation — same inverse shape on "theory → topic-it-struggles-with")
- Audit-touched: 1 (E-25 LAN-E-5 0064 retain-with-annotation), Sound on audit-validated direction

## Cross-cutting observations

**EIGHT consecutive 0-defect shards (10–17).** Shards 10/11/12/13/14/15/16/17 all 0/27. C1 cumulative across 01–17 = 23/461 = 4.99%, dropping below 5% for the first time (was 5.30% at shard 16). The 0-defect run is now the longest consecutive sequence in the census by a wide margin (prior longest was three at shards 06–07 + 09–10). Composition-driven: the pre-sharding random sample is hitting the audit-cleaned regions of the graph; the production-audit's 13% baseline was a single-pass metric over the full 516 edges, so a 4.99% rate over 461 of those (89% of the population) materially below 13% is the continuing "audit follow-up migrations 0061–0065 took the rate down" signal. Two shards (18–19) + closeout (SQA-20) remain.

**New Defensible sub-shape — "specific-topic / specific-theory → umbrella-field / general-topic".** This shard's two Defensibles (E-5 testimonial_knowledge → social_epistemology; E-6 consequentialism → supererogation) share the same structural feature: the edge runs the inverse of the canonical field → topic / umbrella → species pattern that grounds most Sound calls in the routine batch. Distinct in kind from the routine batch's prior Defensible sub-shapes: framework→concept (shard 13 E-15 virtue_epistemology → intellectual_virtue, shard 14 E-17 virtue_ethics → eudaimonia); canonical-direction-inversion / 0064 retain-with-annotation (shard 14/15/16 cluster); co-fundamental-category (shard 16 E-25 existence → relation). The shared structural feature is "inverted-from-canonical-direction-but-defensible-on-foothold-or-problem-case-reading." SQA-20 calibration question for this sub-shape: when should an edge running sub-topic → umbrella-field score Defensible vs Reversed? The foothold-into-bigger-field reading (E-5) and the foil-that-makes-the-concept-vivid reading (E-6) both have support in the production-audit corpus and contemporary pedagogical practice; held at Defensible here on the strength of those readings.

**Three-edge applied-ethics ladder.** This shard's bioethics → research_ethics (E-27), research_ethics → informed_consent (E-17), plus shard 16 E-9 applied_ethics → bioethics, form a three-level umbrella-ladder (applied_ethics > bioethics > research_ethics > informed_consent) constructed across two routine shards. All four edges Sound on the umbrella → sub-area shape. Worth flagging for SQA-20: the seed graph's applied-ethics subdomain has a clean, well-shaped umbrella-ladder topology that is consistent with the production-audit's general endorsement of canonical-direction edges in applied ethics.

**Modal-logic ladder.** E-22 modality → modal_logic + E-1 modal_logic → accessibility_relation forms a clean two-step pedagogical chain within this shard (modality the phenomenon → modal_logic the formal apparatus → accessibility_relation the semantic device). The cross-domain edge (E-22 metaphysics → logic) and the within-domain edge (E-1 logic → logic) chain together cleanly, both Sound.

**Audit cross-reference workflow.** ONE genuine audit-touched edge (E-25 causal_theory_of_reference → rigid_designator, 0064 LAN-E-5 retain-with-annotation), detected via inline `evidence` text — the gold signal per shard 13–16 workflow learnings. Five raw proximity hits this shard (0062 evidence ↔ epistemic_justification; 0061 demarcation_problem ↔ falsificationism via vienna_circle; 0063 time mentioned in surviving-path note; 0064 causation ↔ mental_causation via supervenience_mental; 0064 causal_theory_of_reference → rigid_designator), four narrowed out by per-hit exact-tuple inspection. The 0060 cross-bridges-original-authoring filter held; no 0060 false-positives surfaced. The shard 14/15/16 workflow note continues to hold: when an edge carries inline `evidence` text quoting the audit decision, that's the gold signal; proximity-without-evidence requires per-hit exact-tuple confirmation. Recorded for the SQA-20 aggregation.
