# Seed-graph QA census evidence — shard 11

> Authored by S-0173 (routine session) per T-SEED-QA task SQA-11.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 11
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — explanatory_gap → hard_problem_of_consciousness
EDGE: Explanatory Gap [explanatory_gap, mind] → Hard Problem of Consciousness [hard_problem_of_consciousness, mind]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: The correction: Levine's explanatory gap (1983) precedes and motivates Chalmers' hard problem (1995). Direction should be explanatory_gap > hard_problem_of_consciousness."
VERDICT: Sound
RATIONALE: Audit-validated direction. Levine's "Materialism and Qualia: The Explanatory Gap" (1983) identified WHY physical accounts seem incomplete with respect to phenomenal consciousness — an explanatory gap between physical descriptions and subjective experience. Chalmers's "Facing Up to the Problem of Consciousness" (1995) crystallized this into the structural easy-vs-hard distinction. Pedagogically and historically, Levine's gap is the prerequisite for Chalmers's diagnosis.
AUDIT-TOUCHED: S-0122 audit direction-flip (per 0061/0062 follow-ups); current direction is audit-validated.

### E-2 — aesthetics → art
EDGE: Aesthetics [aesthetics, aesthetics] → Art [art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The "discipline → object-of-study" shape. Aesthetics is the philosophical study of aesthetic value and (centrally) art; art is the concrete topic that aesthetics theorizes about. Standard pedagogical direction is art-first (students have intuitions about paintings, music, novels) → aesthetics (the formal philosophical study of those intuitions). Edge runs opposite. Defensible on the discipline-as-doorway reading: students entering university-level philosophy of art often enter through "aesthetics" as the broader inherited tradition (Plato on beauty, Aristotle on tragedy, Kant on judgment) and then narrow to specific art-theoretic questions. Same "target is the more general/foundational" shape that has recurred across shards 05–10 (held at Defensible on alternative-reading grounds in every prior instance). Recorded under the same calibration.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — modal_logic → epistemic_closure
EDGE: Modal Logic [modal_logic, logic] → Epistemic Closure [epistemic_closure, epistemology]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: The correction: modal logic exists independently of epistemic-closure considerations and is the formal apparatus in which closure gets formalized (the K axiom). Direction should be modal_logic > epistemic_closure."
VERDICT: Sound
RATIONALE: Audit-validated direction. Epistemic closure (if S knows p, and S knows p→q, then S knows q) is formalized in epistemic logic via the K axiom, which is itself a fragment of modal logic. Modal logic is the formal-apparatus prereq; closure is one specific epistemic-logical principle expressible within it.
AUDIT-TOUCHED: S-0122 audit direction-flip; current direction is audit-validated.

### E-4 — philosophy_of_mind → mind
EDGE: Philosophy of Mind [philosophy_of_mind, mind] → Mind [mind, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The strongest instance of the "discipline → object-of-study" shape encountered in the census. Philosophy of mind is THE philosophical study of mind; mind is the topic the discipline theorizes about. Standard pedagogical direction is mind-first (students have intuitions about their own minds; they encounter the concept of "mind" pre-philosophically) → philosophy_of_mind (formal study). Edge runs opposite. The concrete-entry-point reading that has saved the "target-more-general" shape across shards 05–10 applies here too but is more strained: a student really does encounter "mind" as a concept before any philosophical reflection on it, in a way they don't necessarily encounter "existence" before ontology. Held at Defensible (consistent with established calibration; not reversed to Reversed) but flagged as the rubric-calibration question's strongest data point yet — if the closeout decides the "target-more-general" shape should tip to Reversed, this is the edge that would tip first.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — causal_theory_of_reference → semantic_externalism
EDGE: Causal Theory of Reference [causal_theory_of_reference, language] → Semantic Externalism [semantic_externalism, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kripke's causal theory of reference (1972) for proper names — naming-ceremony + causal chain — was extended by Putnam (1975) to natural-kind terms ("meaning ain't in the head") and by Burge (1979) to general semantic externalism (mental content is partly determined by environmental factors). Specific case → broader thesis is the historical and pedagogical sequence.
AUDIT-TOUCHED: none

### E-6 — meaning → use_theory_of_meaning
EDGE: Meaning (Linguistic) [meaning, language] → Use Theory of Meaning [use_theory_of_meaning, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The use theory of meaning (Wittgenstein, later Sellars and inferentialists) is one specific theory of what linguistic meaning consists in. Meaning is the topic; use theory is one substantive position within the topic. Standard topic → theory shape.
AUDIT-TOUCHED: none

### E-7 — epistemic_justification → propositional_knowledge
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Propositional Knowledge [propositional_knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The standard JTB analysis of propositional knowledge requires justification as one of its three structural components (justified true belief). Justification is component-prereq of knowledge — you cannot fully understand the analysis of propositional knowledge without grasping what justification is.
AUDIT-TOUCHED: none

### E-8 — event → causation
EDGE: Event [event, metaphysics] → Causation [causation, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Davidson's (1969) event ontology treats events as the basic relata of causation (the explosion caused the fire); the alternative fact-causation (Mellor) and object-causation accounts still presuppose some ontology of relata. Whether one accepts Davidson's specific account or not, an account of the relata is prereq for an account of the causal relation. Event is the standard candidate relatum; causation is the relation defined over it.
AUDIT-TOUCHED: none

### E-9 — knowledge → virtue_epistemology
EDGE: Knowledge [knowledge, epistemology] → Virtue Epistemology [virtue_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Virtue epistemology (Sosa, Zagzebski, Greco) is a theory of knowledge that grounds knowledge in the exercise of intellectual virtues (reliable cognitive faculties or character-traits). Topic → theory; you need to know what knowledge IS (the target of analysis) before grasping how virtue epistemology proposes to analyze it.
AUDIT-TOUCHED: none

### E-10 — modal_logic → counterfactual_conditional
EDGE: Modal Logic [modal_logic, logic] → Counterfactual Conditional [counterfactual_conditional, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Stalnaker (1968) and Lewis (1973) developed counterfactual logic as an extension of modal-logical apparatus — Kripke-style frames with an additional similarity ordering on worlds. The basic modal apparatus (worlds, accessibility) is the prereq for the counterfactual extension (closest-world selection or comparative similarity).
AUDIT-TOUCHED: none

### E-11 — consciousness → higher_order_theory_consciousness
EDGE: Consciousness [consciousness, mind] → Higher-Order Theory of Consciousness [higher_order_theory_consciousness, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Higher-order theories (Rosenthal's HOT, Carruthers's dispositional-HOT, higher-order perception accounts) are theories of what makes mental states conscious — typically, that conscious states are accompanied by suitable higher-order representations. Consciousness is the topic; HOT is one substantive position. Topic → theory shape.
AUDIT-TOUCHED: none

### E-12 — aesthetics → aesthetic_property
EDGE: Aesthetics [aesthetics, aesthetics] → Aesthetic Property [aesthetic_property, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Same "discipline → object-of-study" shape as E-2 (aesthetics → art). Aesthetic properties (beauty, gracefulness, elegance, sublimity) are part of what aesthetics studies; they are the concrete features of objects that the discipline theorizes about. Standard pedagogical direction is aesthetic_property-first (students have direct experience of finding things beautiful) → aesthetics (the discipline that systematizes those judgments). Edge runs opposite. Defensible on the discipline-as-doorway reading. Same calibration as E-2 and the recurring "target-more-general" shape.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — validity_logical → soundness_logical
EDGE: Validity (Logical) [validity_logical, service] → Soundness (Logical) [soundness_logical, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Soundness is defined as validity PLUS true premises — soundness is a strictly stronger property that has validity as a structural component. You cannot understand soundness without first understanding validity. Component-prereq of the canonical kind.
AUDIT-TOUCHED: none

### E-14 — propositional_attitude → proposition
EDGE: Propositional Attitude [propositional_attitude, mind] → Proposition [proposition, language]
  weight=1.0, confidence=1.0, evidence="Per S-0123 cycle-deferral: 0062 flipped CB-E-63 from propositional_attitude > proposition to proposition > propositional_attitude per S-0122 audit verdict (propositions are content-bearers, attitudes ..."
VERDICT: Sound
RATIONALE: The evidence text identifies this as a cycle-deferred preservation: 0062 direction-flipped the audit-target edge (CB-E-63) to proposition → propositional_attitude per the S-0122 audit's content-bearers-first reasoning, and S-0123 cycle-deferral kept the opposite direction as a documented co-companion to break the resulting cycle. The kept direction (propositional_attitude → proposition) is defensible on its own pedagogical merit: students encounter beliefs/desires/hopes (propositional attitudes — concrete mental states they have intuitions about) before they encounter "proposition" as a technical term naming the content those attitudes take. Standard introductory move: explain belief, then introduce "proposition" as the BLANK in "S believes that BLANK." Scored Sound on the cycle-deferral signal — the evidence text explicitly names the deliberate keep-decision; this is not a defect.
AUDIT-TOUCHED: S-0123 cycle-deferral preserves this direction as the co-companion to 0062's audit-flipped CB-E-63 (proposition → propositional_attitude). Both directions deliberately exist; the closeout may wish to spot-check the cycle-deferral pattern.

### E-15 — scientific_realism → constructive_empiricism
EDGE: Scientific Realism [scientific_realism, science] → Constructive Empiricism [constructive_empiricism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Constructive empiricism (van Fraassen 1980, The Scientific Image) is the canonical contemporary anti-realist position about science (accept observable claims; remain agnostic about unobservables). Its content is defined by what it rejects — you cannot grasp constructive empiricism without first understanding scientific realism (the position it argues against). Same shape as shard 10's E-22 reductionism_in_science → multiple_realizability_in_science and shard 07's audit-validated physicalism → reductionism_in_science.
AUDIT-TOUCHED: none

### E-16 — communitarianism → multiculturalism
EDGE: Communitarianism [communitarianism, political] → Multiculturalism [multiculturalism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Communitarianism (Taylor, Sandel, MacIntyre, Walzer; 1980s) develops the metaphysical-and-ethical thesis that individual identity is constituted by group membership, traditions, and shared practices. Multiculturalism (Kymlicka, Taylor 1992) is the political-theoretic position that distinct cultural communities deserve recognition and accommodation. The communitarian metaphysics-of-identity is the conceptual prerequisite for the multicultural political theory: you ground the political case for group rights in the communitarian claim that group membership is identity-constitutive. The two positions emerged contemporaneously, but the communitarian framework runs deeper in the philosophical anthropology and is the standard pedagogical entry-point.
AUDIT-TOUCHED: none

### E-17 — moral_realism → moral_naturalism
EDGE: Moral Realism [moral_realism, ethics] → Moral Naturalism [moral_naturalism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Moral naturalism (Cornell realism — Boyd, Brink, Sturgeon; Railton's "Moral Realism") is a species of moral realism that identifies moral properties with (or holds them to be constituted by) natural properties. You cannot grasp moral naturalism without first understanding moral realism (the genus). Genus → species.
AUDIT-TOUCHED: none

### E-18 — anti_intentionalism → intentionalism_artistic
EDGE: Anti-Intentionalism [anti_intentionalism, aesthetics] → Intentionalism (Artistic) [intentionalism_artistic, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The "anti-position → position-being-criticized" shape. Anti-intentionalism (Wimsatt and Beardsley 1946, "The Intentional Fallacy") is the New Critical response to the positive intentionalist position that authorial intention determines or constrains literary meaning. Standard pedagogical direction is intentionalism (the older, default view) → anti_intentionalism (the critical response that gave the position its name). Edge runs opposite. Defensible on the slogan-as-doorway reading: in literary-theory teaching, students often encounter "the intentional fallacy" before they encounter intentionalism as a positive philosophical position — the New Critical critique is the gateway through which the underlying intentionalist commitment becomes visible. Same shape considerations apply as to other Defensible direction-shape cases; held at Defensible on the documented pedagogical reading.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — composition_mereological → simples
EDGE: Composition (Mereological) [composition_mereological, metaphysics] → Simples [simples, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mereological composition is the part-whole relation; simples are the mereologically atomic objects (those with no proper parts). The definition of "simple" is parasitic on the composition relation — a simple is precisely something that does not stand in the proper-parthood relation. Composition is the prerequisite framework for stating what simples are.
AUDIT-TOUCHED: none

### E-20 — epistemic_justification → coherentism
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Coherentism [coherentism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Coherentism (BonJour 1985, Lehrer) is a theory of epistemic justification — beliefs are justified by their coherence with the believer's overall belief system. Topic → theory shape; you need to know what justification IS to grasp coherentism's account of it.
AUDIT-TOUCHED: none

### E-21 — substance → substance_dualism
EDGE: Substance [substance, metaphysics] → Substance Dualism [substance_dualism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Substance is the metaphysical category (Aristotle's primary ousia, Descartes's res, Spinoza's God-or-Nature). Substance dualism (paradigmatically Cartesian) is the philosophy-of-mind position that posits two fundamental substances (mental and physical). The metaphysical category is the prereq for the specific position that uses it. Umbrella concept → specific application.
AUDIT-TOUCHED: none

### E-22 — scientific_theory → reductionism_in_science
EDGE: Scientific Theory [scientific_theory, science] → Reductionism (in Science) [reductionism_in_science, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reductionism is a meta-theoretic thesis about how scientific theories relate (one theory's terms can be defined in or derived from another's). Scientific theory is the prereq concept; reductionism is a relation between theories. You cannot state the reductionism debate without an account of what theories are.
AUDIT-TOUCHED: none

### E-23 — existence → numerical_identity
EDGE: Existence [existence, metaphysics] → Numerical Identity [numerical_identity, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Numerical identity (a and b are one and the same entity) presupposes the existence of its relata: it makes no sense to ask whether a is identical to b unless a and b exist. Existence is the foundational metaphysical concept; numerical identity is one relation defined over existing things. Same shape as shard 10's E-15 existence → causation, scored Sound.
AUDIT-TOUCHED: none

### E-24 — virtue_ethics → moral_particularism
EDGE: Virtue Ethics [virtue_ethics, ethics] → Moral Particularism [moral_particularism, ethics]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Virtue ethics's emphasis on practical wisdom (phronesis) and attention to particularity of character encodes a commitment to the particularist rejection of universal moral rules in f..."
VERDICT: Sound
RATIONALE: Audit-validated direction. Virtue ethics's emphasis on phronesis (practical wisdom — the capacity to discern the right action in particular circumstances) encodes a commitment to the moral-particularist thesis that moral judgment cannot be cashed out in universal rules. Dancy's moral particularism (Ethics Without Principles, 2004) is the metaethical formalization of the virtue-theoretic insight. The audit verdict makes virtue ethics the conceptual prerequisite for moral particularism.
AUDIT-TOUCHED: S-0122 audit; current direction is audit-validated.

### E-25 — modal_logic → formal_epistemology
EDGE: Modal Logic [modal_logic, logic] → Formal Epistemology [formal_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: The correction: modal logic is the foundational formal apparatus; formal epistemology USES modal logic (particularly epistemic logic) as a tool. Direction should be modal_logic > formal_epistemology."
VERDICT: Sound
RATIONALE: Audit-validated direction. Modal logic (Lewis, Kripke) is the foundational formal apparatus; formal epistemology uses modal logic (particularly epistemic logic — Hintikka 1962) as one of its core tools for representing knowledge and belief states. Modal logic is the prerequisite formal framework.
AUDIT-TOUCHED: S-0122 audit direction-flip; current direction is audit-validated.

### E-26 — semantic_paradox → liar_paradox
EDGE: Semantic Paradox [semantic_paradox, logic] → Liar Paradox [liar_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Semantic paradoxes are the class of paradoxes involving semantic predicates (truth, denotation, satisfaction) — the Tarskian framework identifies them as a kind. The liar paradox is the canonical instance ("this sentence is false"). Genus → species pedagogical shape; once a student understands what makes a paradox "semantic" (self-reference involving a semantic predicate), the liar is the iconic instance. Alternative pedagogical encounters (liar-first as the iconic example) exist, but the category-first direction is supported by the Tarskian theoretical organization of the topic.
AUDIT-TOUCHED: none

### E-27 — accessibility_relation → kripke_semantics
EDGE: Accessibility Relation [accessibility_relation, logic] → Kripke Semantics [kripke_semantics, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Kripke semantics for modal logic is defined in terms of a frame ⟨W, R⟩ where W is a set of possible worlds and R is the accessibility relation between them. The accessibility relation is the central technical primitive — different modal systems (K, T, S4, S5) correspond to different formal constraints on R (reflexivity, transitivity, symmetry, euclideanness). You cannot state Kripke semantics without an accessibility relation.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — epistemic_justification
NODE: Epistemic Justification [epistemic_justification, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes justification from mere reliability (the internalist test), distinguishes from truth (the fallibilist move), names normativity as the load-bearing feature. Concrete operational distinctions.
C3 (summary cold-readability): yes — "adequate epistemic grounds for holding [a belief]" is the operational gloss; "third clause of the standard JTB analysis" identifies the structural role; the competing theory-families (internalism/externalism, foundationalism/coherentism/infinitism) are listed as labels with the load borne by the structural-role statement.

### N-2 — certainty
NODE: Epistemic Certainty [certainty, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Cartesian-vs-fallibilist historical contrast; "teach certainty as the limit case to clarify what knowledge does and does not require" is a sharp pedagogical move; the certainty-knowledge structural distinction ("knowledge is consistent with the bare possibility of error, certainty is not") is operationally useful.
C3 (summary cold-readability): yes — "doubt is impossible" is intuitively graspable; "the believer's evidence rules out every alternative" gives the structural condition; "Distinct from psychological certainty (mere felt confidence)" forestalls the standard confusion inline.

### N-3 — integrated_information_theory
NODE: Integrated Information Theory [integrated_information_theory, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong: three numbered core claims; empirical purchase named (EEG/fMRI on disorders of consciousness, anesthesia, dreamless sleep); metaphysical bite named (panpsychism implication via Tononi, Koch, Goff); both empirical (Φ computational intractability) and conceptual challenges (Bayne-Tsuchiya axioms; Searle category-mistake objection); pedagogical framing ("the canonical example of a positive scientific theory of consciousness with both quantitative predictive content and explicit metaphysical implications").
C3 (summary cold-readability): yes — borderline. The first sentence states the position plainly: "consciousness as integrated information: a system is conscious to the degree that its informational structure is irreducibly integrated, measured by the quantity Φ (phi)." Φ is named-and-functioned (it's "the quantity that measures integrated information") rather than glossed in the abstract — that's a contextual gloss. "Causal organization" appears in sentence 2 as the explanans for what Φ measures. A cold reader can grasp the position from the substance ("consciousness scales with how irreducibly integrated a system's information is") even without prior IIT context. Borderline PASS on the same calibration that scored shard 10's N-3 fuzzy_logic (t-norm) PASS.

### N-4 — access_consciousness
NODE: Access Consciousness [access_consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "what cognitive science measures" framing immediately gives traction; concrete empirical-research examples (subliminal perception, attentional blink, change blindness, binocular rivalry); the access/phenomenal philosophical interest is sharpened ("A-consciousness leaves the hard problem untouched"); maps each major theoretical tradition (global workspace, higher-order, representationalism) onto which kind of consciousness it primarily theorizes.
C3 (summary cold-readability): yes — Block 1995 named; "the functional aspect of conscious mental states: their being globally available for use in reasoning, verbal report, and the rational control of behavior" is the operational gloss; phenomenal consciousness named with inline contrast ("the qualitative, what-it-is-like aspect"); the physicalist-friendly status is explicit.

### N-5 — justified_true_belief
NODE: Justified True Belief [justified_true_belief, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names JTB as "the central reference point for the analysis-of-knowledge tradition"; pedagogical sequencing advice ("understand its three clauses as independently motivated ... before encountering Gettier"); the post-Gettier-retains-JTB observation locates the position in the literature.
C3 (summary cold-readability): yes — gives all three clauses (1)(2)(3) explicitly inline; Plato's Theaetetus named as historical anchor; Gettier 1963 named as the decisive challenge.

### N-6 — justice_bioethical
NODE: Justice (Bioethical) [justice_bioethical, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong: substantive views laid out (utilitarian QALY/DALY; egalitarian + fair-innings; Rawlsian difference principle; prioritarian); concrete-institution case study (UNOS organ allocation, with disparities critique); research-justice history (Belmont 1979; Tuskegee as canonical violation; the under-recruitment vs systematic-exclusion balance). Substantial pedagogical traction.
C3 (summary cold-readability): yes — "fair distribution of medical benefits, burdens, and resources" is the immediate operational gloss; concrete examples follow ("organs, ICU beds, vaccines"); "Beauchamp & Childress principles" appears without inline gloss but is a contextual proper-name reference (the four-principles framework) rather than load-bearing technical apparatus the cold reader must decode; "distributive_justice (P5-05)" is a graph-internal cross-reference that does not block summary parseability. The substance is independently graspable.

### N-7 — persistence
NODE: Persistence [persistence, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — sets up the dispute via the concrete cat-at-noon-vs-1pm contrast; "diachronic analog of synchronic identity" gives structural location; lists downstream consequences (ship-of-theseus, constitution, philosophy of time).
C3 (summary cold-readability): yes — "Identity through time" is the immediate gloss; endurantism and perdurantism each defined inline ("wholly present at each time at which it exists" / "has temporal parts at each time at which it exists"); the spatial-parts analogy provides structural orientation.

### N-8 — rigid_designator
NODE: Rigid Designator [rigid_designator, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — vivid modal argument against descriptivism walked through ("Aristotle" rigid; "the teacher of Alexander" non-rigid; the necessary-vs-contingent diagnosis); the necessary/a-priori cut (Hesperus-Phosphorus); the bridge to natural-kind essentialism and modal logic of essential properties.
C3 (summary cold-readability): yes — "an expression that designates the same object in every possible world in which that object exists" is the operational gloss; concrete examples immediately follow ("Aristotle" picks out Aristotle in every world; "the teacher of Alexander" varies). "Possible worlds" is undefined as a technical term but is contextually graspable from the everyday "in every possible scenario" sense; the examples carry the modal load.

### N-9 — phenomenal_consciousness
NODE: Phenomenal Consciousness [phenomenal_consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete phenomenal examples ("the felt redness of a red experience, the painfulness of pain, the eerie quality of fear"); the A-conscious/P-conscious can-come-apart argument; the physicalist response options; pedagogical advice ("the honest answer is almost always 'phenomenal'").
C3 (summary cold-readability): yes — "the experiential aspect of conscious mental states: their qualitative, felt, what-it-is-like character" gives the technical name and the inline gloss simultaneously; Block 1995 named; the contrast with access consciousness is operationally glossed; the hard-problem / knowledge / zombie connection placed.

### N-10 — a_theory_of_time
NODE: A-Theory of Time [a_theory_of_time, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names defenses (felt passage, asymmetry between fixed past and open future, linguistic primacy); names objections (McTaggart's paradox, special-relativity tension); names the three A-theoretic positions (presentism, growing-block, moving-spotlight).
C3 (summary cold-readability): yes — "A-series" is named with inline gloss ("the ordering of events by tensed properties (past, present, future)"); "the present is metaphysically privileged" gives the philosophical claim; the contrast with tenseless propositions ("it is now raining" vs ...) shows the load-bearing distinction. "Metaphysically privileged" appears but is the conceptual claim being made, not a hidden technical apparatus.

### N-11 — contractualism
NODE: Contractualism [contractualism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong: Scanlon's central formula given verbatim; the moral motivation made explicit ("the desire to be ABLE TO JUSTIFY one's actions to those affected"); aggregation-problem trolley discussion; contrast with social-contract tradition (Hobbes, Locke, Rousseau, Rawls) drawn carefully; the parasitism-on-prior-moral-facts objection named.
C3 (summary cold-readability): yes — Scanlon 1998 named with book title (WHAT WE OWE TO EACH OTHER); the operational formula given inline ("an action is wrong if it would be disallowed by any principle that no one could reasonably reject as a basis for general informed agreement"); social-contract distinction explicit; the meta-ethical-vs-normative status clarified.

### N-12 — vagueness
NODE: Vagueness [vagueness, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — sorites pattern fully walked through with the bald example; three philosophical response-classes (supervaluationism, epistemicism, fuzzy/degree-theoretic) each named with their characteristic costs; cross-bridge to philosophy of language named.
C3 (summary cold-readability): yes — "predicates with borderline cases — 'is bald', 'is a heap', 'is tall'" gives three concrete examples immediately; "no sharp cutoff" and "admits of degree" carry the conceptual load; the disambiguation from ambiguity / generality / underspecification is explicit and helpful.

### N-13 — qualia_functionalism
NODE: Qualia Functionalism [qualia_functionalism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — appeal-and-costs structure; canonical objections (inverted-spectrum from Block/Shoemaker; absent-qualia / China-brain from Block 1978); Shoemaker's response; pedagogical role ("the position that motivates teaching the inverted-spectrum thought experiment").
C3 (summary cold-readability): yes — borderline. "Qualia" appears in the first sentence without inline gloss; "functional properties" is glossed by "individuated by their typical causal relations to perceptual inputs, cognitive states, and behavioral outputs." A cold reader gets "mental properties defined by causal role" from sentence 1's second half. Sentence 3 supplies "phenomenal character" as the implicit gloss for what qualia are ("inverted-spectrum and absent-qualia objections that pressure functionalist treatments specifically of phenomenal character"). Borderline PASS on the same calibration as N-3: the load-bearing technical term ("qualia") is contextually glossed across the summary even without inline definition in sentence 1.

### N-14 — event
NODE: Event [event, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Davidson's "The Individuation of Events" named as foundational text; three competing criteria-of-individuation (Kim's property-time-object triples; Davidson's same-causes-and-effects; Lewis's sets-of-regions); pedagogical relevance ("the dispute matters because action theory and causation analyses pick up an event ontology and run with it").
C3 (summary cold-readability): yes — "A particular occurrence located in space and time" is the immediate operational gloss; three concrete examples ("the explosion of a bomb, the running of a race, the signing of a treaty"); Davidson 1969 named; distinction from "propositions that describe them" and "properties they instantiate" forestalls standard confusions.

### N-15 — depiction
NODE: Depiction [depiction, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — two-foldedness thesis made central ("simultaneously and inseparably aware of the picture's marked surface AND of the depicted subject"); strategic positioning between Goodman's conventionalism and naive resemblance theory; preservation-of-phenomenology argument; the standard pressure ("how exactly does seeing-in work? what is its psychological reality?").
C3 (summary cold-readability): yes — "the specific perceptual mode by which a viewer recognizes what a picture pictures" is the immediate gloss; Wollheim 1968 and 1987 named; "seeing-in" introduced in scare quotes with inline gloss ("the viewer sees the depicted subject IN the picture's marked surface, simultaneously seeing the surface as marked and the subject as visually present"); the sui-generis status named ("neither reducible to resemblance recognition nor to inferential decoding of convention").

### N-16 — anthropocentrism
NODE: Anthropocentrism [anthropocentrism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong: STRONG-vs-WEAK distinction; the strict-anthropocentrism difficulty with animal cruelty; Norton 1991's weak-anthropocentrism convergence argument; strategic-case framing for each position; the last-man argument (Routley 1973) walk-through; Christian-stewardship contrast (Berry 1990; Laudato Si' 2015); secular deep ecology placement.
C3 (summary cold-readability): yes — "only human beings possess intrinsic moral value" is the immediate operational gloss; the alternative ("matter morally only instrumentally — to the extent they affect human welfare, aesthetic experience, or future human generations") is unpacked inline; historical default named with three concrete anchors (Genesis dominion mandate; Aristotle's ladder of being; Kant on rational autonomy); the STRONG-vs-WEAK structural distinction is glossed in the summary itself.

### N-17 — conditional_logic
NODE: Conditional Logic [conditional_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Stalnaker 1968 and Lewis 1973 named with book titles; the critical pedagogical advice ("The crucial negative results are the ones to teach"); concrete failure-of-strengthening example (the match struck while submerged); concrete failure-of-transitivity example (Hoover/Communist/traitor/disgraced); cross-bridge to philosophy of language.
C3 (summary cold-readability): no — first sentence load-bearing terms are not glossed inline: "counterfactual conditionals" (the topic itself), "non-truth-functional binary connective" (pure formal-logic jargon), "Kripke-style frame" (undefined), "accessibility structure" (undefined), "similarity ordering on worlds" (undefined). Sentence 2 introduces the failures with formal notation ("P □→ Q does not entail (P ∧ R) □→ Q"). A cold reader without modal-logic vocabulary cannot parse the summary. The teaching_notes (where the Hoover and match-submerged examples appear) would rescue cold-readability; the summary itself does not. Same failure mode as shard 09's N-19 representationalism_perception and shard 08's load-bearing-modal-vocabulary cluster. Strict-reading FAIL on undefined load-bearing apparatus.

### N-18 — no_false_lemmas_response
NODE: No-False-Lemmas Response [no_false_lemmas_response, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the natural-first-response motivation ("Gettier cases all seem to involve a false intermediate belief"); the Smith-has-a-Ford canonical example; the fakeness-cases countermove (Goldman's barn-facade county) that defeats the proposal.
C3 (summary cold-readability): yes — borderline. "Gettier response" and "JTB" appear without inline gloss in the first sentence; the conceptual core ("the believer's justification must not essentially rest on any false belief") is independently parseable. A cold reader gets the structural claim — knowledge requires no false essential premises — even without knowing what Gettier cases are. The motivation is opaque without Gettier context but the position's content is graspable. Borderline PASS on the structural-content-is-clear reading; flagged.

### N-19 — distributive_justice
NODE: Distributive Justice [distributive_justice, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong four-dimensional framework (metric / rule / site / scope); Nozick's patterned-vs-historical contrast; Wilt Chamberlain argument walked through; Cohen 2008 RESCUING JUSTICE site-of-justice critique; Pogge 2002 cosmopolitan-scope critique. Substantial traction.
C3 (summary cold-readability): yes — "the proper distribution of advantages and burdens across persons within a society" is the immediate operational gloss; Rawls 1971 named with "basic structure" framing; the competing positions ("strict equality, Rawlsian justice as fairness with the difference principle, libertarian entitlement theories that reject patterned distribution entirely, capability-approach metrics of substantive freedom, luck-egalitarian distinctions between choice and circumstance, and desert-based distributions tracking productive contribution") each given with a one-clause inline gloss. Long but every term unpacks.

### N-20 — deontology
NODE: Deontology [deontology, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — strong: family-of-positions framing; Kant Groundwork 1785 + CPR 1788 with the three categorical-imperative formulations; Ross 1930 prima-facie-duties seven-fold list; Nagel/Kamm/Scanlon contemporary structural moves (restrictions vs options); classical objections (rigorism, conflicting duties, the pure-deontology motivational difficulty); cross-bridge to deontic logic.
C3 (summary cold-readability): yes — "moral status of an action is determined by features beyond its consequences" is the immediate operational gloss; the concrete features named ("keeping promises, respecting autonomy, refraining from using persons as mere means, fulfilling duties, respecting rights"); the consequentialist contrast ("an action can be wrong even when its consequences are best") explicit; Ross 1930 named; agent-centered restrictions / options named as structural concepts.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
  - Sound 23, Defensible 4 (E-2 aesthetics→art; E-4 philosophy_of_mind→mind; E-12 aesthetics→aesthetic_property; E-18 anti_intentionalism→intentionalism_artistic)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 1 (5.0%) | teaching_notes ABSENT 0
  - C3 fail: N-17 conditional_logic (load-bearing modal-logic vocabulary not glossed inline in summary)

## Cross-cutting observations

This shard carries the highest audit-touched edge count in the routine batch so far — **5 of 27 edges (18.5%) are audit-touched**, vs shard 10's 2-of-27 and shard 07's similar concentration. Three of the five involve `modal_logic` as the source endpoint (E-3 → epistemic_closure; E-10 → counterfactual_conditional; E-25 → formal_epistemology), reflecting the S-0122 audit's cluster of direction-flips that established modal logic as the foundational formal apparatus on which several specific applications depend. All three audit-validated directions scored Sound on their conceptual merit; the audit's keep-and-flip decisions hold up on parametric re-inspection. E-1 explanatory_gap → hard_problem_of_consciousness (S-0122 Levine-before-Chalmers direction-flip) and E-24 virtue_ethics → moral_particularism (S-0122 phronesis-encodes-particularism) likewise scored Sound on the audit-validated direction.

E-14 propositional_attitude → proposition is the cycle-deferred companion to 0062's audit-flip (CB-E-63 was direction-flipped to proposition → propositional_attitude per S-0122's content-bearers-first reasoning; the current shard 11 edge has the OPPOSITE direction, deliberately preserved per S-0123 cycle-deferral). Scored Sound on the cycle-deferral signal — the evidence text explicitly names the keep-decision. The closeout may wish to spot-check the broader cycle-deferral pattern: this is the first instance the routine batch has encountered of an edge whose direction is preserved as a cycle co-companion to an audit-flipped edge, and the calibration ("Sound on cycle-deferral signal" vs "Reversed contradicts the audit") is worth articulating for SQA-20.

The "target is the more general/foundational concept" Defensible shape continues — **seven consecutive shards (05–11)** each producing ≥1 instance. This shard's instances cluster around the **"discipline → object-of-study"** sub-shape: E-2 aesthetics → art, E-4 philosophy_of_mind → mind, E-12 aesthetics → aesthetic_property. E-4 is the most extreme instance encountered to date — philosophy_of_mind IS the philosophical study of mind, and mind is the topic the discipline theorizes about. Held at Defensible on the discipline-as-doorway reading per the established calibration; flagged as the rubric-calibration question's strongest data point yet (if SQA-20 decides this shape should tip from Defensible to Reversed, E-4 is the edge that would tip first). E-18 anti_intentionalism → intentionalism_artistic is a different Defensible shape — "anti-position → position-being-criticized" — recorded separately; same slogan-as-doorway logic as the literary-theory pedagogical encounter pattern.

C3 fail at N-17 conditional_logic is the only C3 failure this shard. The shape is exactly the calibration-anchor case from S-0170's representationalism comparison: load-bearing technical terminology (counterfactual conditionals, non-truth-functional binary connective, Kripke-style frame, accessibility structure, similarity ordering on worlds — all in the first two sentences) is not glossed inline in the summary. The teaching_notes recover (Hoover/Communist/traitor and match-submerged examples make the failure-of-strengthening and failure-of-transitivity concrete), but C3 is scored against the summary alone. This is the second straight shard (after shard 10's break-in-streak) to produce a single, isolated C3 fail — distinct from the high-concentration pattern of shard 09 (5 fails in technical-philosophy-heavy nodes). Two borderline-PASS calls this shard worth flagging for closeout consistency review: N-3 integrated_information_theory (Φ named-and-functioned rather than glossed-in-the-abstract) and N-13 qualia_functionalism (qualia ungated in sentence 1; "phenomenal character" supplied as gloss in sentence 3). N-18 no_false_lemmas_response is a third borderline call (Gettier and JTB context for motivation; structural content independently parseable) — held at PASS but flagged. The N-3 / N-13 / N-18 cluster fits the shard 10 N-3 / N-12 calibration: load-bearing technical term ungated in the load-bearing sentence but contextually glossed across the summary.

Running C1 across shards 01–11: 10.7% / 3.6% / 3.6% / 0.0% / 3.7% / 0.0% / 0.0% / 3.7% / 0.0% / 0.0% / 0.0%. Cumulative 23/299 = 7.7%, continuing to tick DOWN under the production audit's 13% baseline (was 8.5% at shard 10). Six 0-defect shards now (04, 06, 07, 09, 10, 11). The drift signal remains "no drift" — the cumulative rate continues to converge below the audit baseline as the sample grows.
