# Phase 5 production audit evidence — hubs 1–5 (top hubs by total degree)

> Authored by S-0119 (routine session) per T-PHASE-5-AUDIT task AUDIT-HT-1 — first half of decomposed-AUDIT-HT (decomposed at S-0117 administrative close per Issue #58 because the original 96-edge + 10-node + 3-trace single-task scope hit context cap mid-authoring).
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: hubs (top 5 by total degree across all subdomains; full incident-edge census on each hub plus per-node review of the hub nodes themselves)
- Hub identification (parametric scan of the 15 Phase 5 seed migrations 0011 / 0016 / 0030 / 0036 / 0040 / 0046 / 0050 / 0060 / 0070 / 0080 / 0090 / 0100 / 0110 / 0020 / 0026): epistemic_justification (epistemology, deg 14 — 11 out + 3 in), existence (metaphysics, deg 11 — 10 out + 1 in), propositional_knowledge (epistemology, deg 11 — 8 out + 3 in), causation (metaphysics, deg 10 — 6 out + 4 in), physicalism (mind, deg 10 — 8 out + 2 in)
- Edge population (incident to any of the 5 hubs): 56 raw edges, 54 unique after deduplication of 2 inter-hub edges (epistemic_justification → propositional_knowledge counted once across HUB-A and HUB-C; existence → causation counted once across HUB-B and HUB-D)
- Edge sample size: 54; sample density: 100% (full census on incident edges per master-plan §"Sample-size policy" hubs row — hubs are calibration anchors for the closeout's aggregate-scan synthesis, not a stochastic sample)
- Node sample size: 5; selection: the 5 hub nodes themselves
- Generation date: 2026-05-10
- Routine-mode posture: parametric-only review per master-plan §"Empirical-fortification branch" routine-mode prohibition (load-bearing until T1-A through T1-D close at the closeout interactive session per ADR 0053). Medium-confidence + mutation-implying verdicts get fortified at the closeout per master-plan §"Forward pointers to closeout" / ADR 0059.
- AUDIT-HT-2 scope (sequential after this task per the auto_target depends_on chain): hubs 6–10 (classical_logic, meaning, normative_ethics, vienna_circle_logical_positivism, aristotelian_four_causes — ~48 unique incident edges) + 3 syllabus traces (gettier_problem, modal_realism, social_contract_theory).

## Sampled-edge candidate findings

### HUB A — epistemic_justification (epistemology, deg 14)

#### Finding E-1
EDGE: epistemic_justification [domain=epistemology] → propositional_knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Epistemic Justification" / "The Analysis of Knowledge" — justification is the third clause of the standard JTB (justified true belief) analysis of propositional knowledge, and the surface where the contemporary positions (foundationalism, coherentism, infinitism; internalism, externalism; reliabilism, evidentialism, virtue epistemology) compete. Pedagogically, the JTB analysis of propositional knowledge is articulated by composing belief, truth, and justification — students must hold each component before the analysis can be presented. The seed's edge structure makes the same composition explicit (belief → propositional_knowledge, truth → propositional_knowledge, epistemic_justification → propositional_knowledge — three converging prereqs of pk). SEP "The Analysis of Knowledge" runs in this direction: introduce the JTB clauses serially (belief, truth, justification) before the Gettier-resistant fourth-clause work. The migration's edge runs ej → pk in the canonical components-to-composition direction. Direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: Edge is one of two inter-hub edges in this audit-task scope (the other is existence → causation in HUB B/D); recorded once here to avoid double-count.

#### Finding E-2
EDGE: belief [domain=epistemology] → epistemic_justification [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Belief" / "Epistemic Justification" — justification is a normative property OF beliefs. The belief concept (the propositional-attitude shape; the cognitive-state-with-mind-to-world-direction-of-fit; the dispositional-vs-occurrent question) is the bearer of the justified/unjustified property; you cannot articulate "this belief is justified" without prior grasp of "belief." SEP "Epistemic Justification" entry opens by characterizing justification as the property a believer's belief has under appropriate epistemic conditions. The migration's own ej teaching_notes lead with the normative-relative-to-epistemic-obligations framing, presupposing the believer-belief shape. The migration's edge runs belief → ej in the canonical bearer-to-property direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-3
EDGE: evidence [domain=epistemology] → epistemic_justification [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Evidence" / "Epistemic Justification" / "Evidentialism" — evidence is the standard input to justification on the dominant evidentialist tradition (Conee and Feldman 1985 "Evidentialism"; Conee and Feldman 2004 EVIDENTIALISM): a belief is justified iff it fits the believer's total evidence. Even non-evidentialist positions (reliabilism, virtue epistemology) typically retain evidence as one input to the justification-conferring process. Pedagogically, the evidence concept (the propositional-vs-non-propositional debate; the having-vs-possessing distinction; the bayesian-vs-non-bayesian conceptions) is articulated as input to justification-bearing accounts; SEP exposition runs in this direction. The migration's edge runs evidence → ej in the canonical input-to-property direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-4
EDGE: epistemic_justification [domain=epistemology] → foundationalism [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Foundationalist Theories of Epistemic Justification" / "Epistemic Justification" — foundationalism is one of three principal structural theories of epistemic justification (alongside coherentism and infinitism), addressing the Agrippan regress problem by positing basic beliefs whose justification does not derive from inferential support. The conceptual relationship is master-question-to-structural-answer: the regress problem about justification's structure (where does justification stop?) is the question, foundationalism is one of the three canonical answers. Pedagogically the student needs the master concept of justification in hand (the regress problem; the inferential-vs-non-inferential distinction; the basic-belief notion as the proposed terminator) before foundationalism as one structural answer makes sense. SEP exposition runs in this direction: introduce justification and the regress problem, then introduce foundationalism / coherentism / infinitism as the three structural responses. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-5
EDGE: epistemic_justification [domain=epistemology] → coherentism [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Coherentist Theories of Epistemic Justification" / "Epistemic Justification" — coherentism is the second of the three structural theories (BonJour 1985 THE STRUCTURE OF EMPIRICAL KNOWLEDGE; Lehrer 1990 THEORY OF KNOWLEDGE), holding that justification arises from coherence relations among beliefs without privileged basic beliefs. Same master-question-to-structural-answer relationship as E-4: the regress problem motivates the structural answers, coherentism being one. Pedagogically the student needs the justification concept first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-6
EDGE: epistemic_justification [domain=epistemology] → infinitism [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Infinitism in Epistemology" / "Epistemic Justification" — infinitism (Klein 1999 "Human Knowledge and the Infinite Regress of Reasons"; Klein 2007) is the third structural theory, holding that justification arises from infinite non-repeating chains of reasons. Same master-question-to-structural-answer relationship as E-4 / E-5. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-7
EDGE: epistemic_justification [domain=epistemology] → internalism_epistemic [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Internalist vs. Externalist Conceptions of Epistemic Justification" / "Epistemic Justification" — the internalism / externalism divide is one of the two principal axes structuring contemporary justification theory (alongside the structural foundationalism / coherentism / infinitism axis), addressing whether justifiers must be accessible to the believer (internalism) or whether external reliability-conferring properties suffice (externalism). The conceptual relationship is master-concept-to-meta-theoretic-axis: the master concept of justification is what the divide is a divide ABOUT; pedagogically the student needs the justification concept before the divide makes sense. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-8
EDGE: epistemic_justification [domain=epistemology] → externalism_epistemic [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Internalist vs. Externalist Conceptions of Epistemic Justification" / "Epistemic Justification" — externalism is the second pole of the access-axis (E-7's mate), permitting non-access-conditioned justifiers (paradigmatically reliabilism's reliable-process condition; Goldman 1979 "What Is Justified Belief?"). Same master-concept-to-meta-theoretic-axis relationship as E-7. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-9
EDGE: epistemic_justification [domain=epistemology] → skepticism_epistemic [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Skepticism" / "Epistemic Justification" / "Cartesian Skepticism" — epistemic skepticism is the position that we lack knowledge (or justification) of some target proposition class (external-world skepticism, other-minds skepticism, inductive skepticism). The conceptual relationship is master-concept-to-denial-of-its-instances: skepticism denies that justification (or knowledge) is achievable across some range; the denial presupposes the master concept. Pedagogically the student needs the justification concept first to formulate the skeptical challenge to it (the closure-based skeptical argument; the Agrippan regress as skeptical engine; underdetermination by evidence). SEP exposition runs in this direction. Direction sound. Note: skepticism could equally well be edge-anchored to propositional_knowledge (the more standard target of skeptical denial), but the migration's choice to anchor to ej is also defensible — Pyrrhonian skepticism in particular targets justification-suspension as the canonical move. Direction sound under either reading.
VERDICT: sound
CONFIDENCE: medium

#### Finding E-10
EDGE: epistemic_justification [domain=epistemology] → virtue_epistemology [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 3
SEP-ANCHORED REASONING: SEP entry on "Virtue Epistemology" — virtue epistemology (Sosa 1980 "The Raft and the Pyramid"; Zagzebski 1996 VIRTUES OF THE MIND; Greco 2010 ACHIEVING KNOWLEDGE) frames justification (and knowledge more broadly) in terms of the believer's intellectual virtues — character traits or cognitive faculties whose exercise produces well-grounded belief. Two principal strands: virtue-reliabilism (Sosa, Greco — virtues as reliable cognitive faculties) and virtue-responsibilism (Zagzebski, Code — virtues as character traits requiring intellectual motivation). Master-concept-to-theoretical-framework relationship: virtue epistemology proposes a way to ground or reframe justification (and knowledge); pedagogically the student needs the justification concept first to grasp what virtue epistemology is doing differently. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-11
EDGE: epistemic_justification [domain=epistemology] → reliabilism [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 3
SEP-ANCHORED REASONING: SEP entry on "Reliabilist Epistemology" — reliabilism (Goldman 1979 "What Is Justified Belief?"; Goldman 1986 EPISTEMOLOGY AND COGNITION; Alston 1995 "How to Think About Reliability") is the canonical externalist theory of justification: a belief is justified iff produced by a reliable cognitive process. Master-concept-to-specific-theory: reliabilism is one specific theory of justification (externalist; process-reliability-grounded); pedagogically the student needs the justification concept first. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-12
EDGE: epistemic_justification [domain=epistemology] → evidentialism [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 3
SEP-ANCHORED REASONING: SEP entries on "Evidentialism" / "Epistemic Justification" — evidentialism (Conee and Feldman 1985 "Evidentialism"; Conee and Feldman 2004 EVIDENTIALISM) is the canonical internalist theory of justification: a belief is justified iff it fits the believer's total evidence at the time. Master-concept-to-specific-theory analogous to E-11: evidentialism is one specific theory (internalist; evidence-fit-grounded); pedagogically the student needs the justification concept first. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-13
EDGE: argument_logical [domain=logic] → epistemic_justification [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from logic to epistemology)
SEP-ANCHORED REASONING: SEP entries on "Argument" (in the logical-formal sense) / "Logical Consequence" / "Epistemic Justification" — the concept of a logical argument (a sequence of premises supporting a conclusion via inference rules) is the structural backbone of inferential justification: when a belief is justified inferentially (i.e., by other beliefs supplying support), the support relation is articulated as an argument. Foundationalism, coherentism, and infinitism all presuppose argument-structure to articulate the regress problem (each step in the regress is a premise-conclusion link). Pedagogically the student needs the argument concept (premises, conclusion, validity, soundness, deductive-vs-inductive) before the inferential-justification machinery makes sense. SEP exposition: "Epistemic Justification" entry routinely uses argument-structure as primitive in articulating the regress problem and inferential support. The migration's edge runs argument_logical → ej in the canonical formal-structure-to-substantive-application direction. Direction sound. The cross-bridge is well-motivated: logic supplies the structural primitives that epistemology applies to belief-support relations.
VERDICT: sound
CONFIDENCE: medium

#### Finding E-14
EDGE: epistemic_justification [domain=epistemology] → propositional_attitude [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from epistemology to mind)
SEP-ANCHORED REASONING: SEP entries on "Propositional Attitude Reports" / "Belief" / "Intentionality" — propositional attitudes (belief, desire, intention, hope, fear, doubt — mental states with propositional content and aboutness) are the philosophy-of-mind-anchored category whose principal members include belief; the SEP-canonical entry treats propositional attitudes as basic to philosophy of mind and intentionality, with belief as one species. The conceptual flow runs: propositional_attitude is the genus from philosophy of mind; belief is one species; epistemic justification is a normative property OF the belief species. Pedagogically the student does NOT need epistemic justification first to grasp the propositional-attitude category — propositional attitudes are introduced in philosophy of mind via the intentionality / aboutness frame (Brentano; Frege's sense-and-reference apparatus; Russell's multiple-relation theory; the contemporary fine-grained / coarse-grained content debate) without invoking justification. The migration's edge runs ej → propositional_attitude (i.e., teach justification before propositional_attitude as a category), which inverts the canonical conceptual ordering. Per the master-plan §T1-A verdict taxonomy this is REVERSED: propositional_attitude is the broader genus that justification's species (belief) instantiates; pedagogical prerequisite should run propositional_attitude → belief → ej. The seed's reverse direction is also weakly supportable on the reading "students grasp justified-belief through epistemology before encountering propositional-attitudes-as-a-philosophy-of-mind-category" — but this is a curriculum-ordering claim, not the conceptual-dependency direction the edge is meant to encode. Distinct in shape from prior reversal patterns in the routine block: this is a CROSS-BRIDGE-INVERTING-GENUS-SPECIES pattern, where the cross-bridge runs from species (justification-as-property-of-belief) to genus (propositional_attitude as broader category). Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.
VERDICT: reversed
CONFIDENCE: medium

### HUB B — existence (metaphysics, deg 11)

#### Finding E-15
EDGE: ontology [domain=metaphysics] → existence [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Logic and Ontology" / "Existence" / "Quine on Ontology" — ontology is the philosophical study of what there is (in Quine's framing: the question "what exists?" and the methodological apparatus for answering it via the existential commitment of a theory's quantifiers). Existence is the focal property at issue — a theory's ontology is the inventory of things-that-exist according to that theory. Conceptual relationship: ontology is the master discipline whose central question is articulated using the existence concept. SEP exposition: "Logic and Ontology" introduces ontology as the field whose central question is the existence-question; the existence concept is the unit of ontological dispute. Pedagogically the student does need the field-concept of ontology to frame the existence-question as the field's central question — the seed's edge runs ontology → existence in the canonical discipline-to-its-central-question direction. **Foundation-spine-pattern observation**: the discipline-label-as-prereq foundation-spine pattern surfaced repeatedly in the routine block (S-0112 philosophy_of_language E-6; S-0113 philosophy_of_science E-2/E-3/N-5; S-0114 political_philosophy E-11/N-5; S-0115 aesthetics E-4/E-8/E-11) has a sub-discipline-label-as-prereq variant here: ontology is a sub-discipline-label (within metaphysics), and existence is its first central concept. Distinct from top-level discipline-label-as-prereq (where the discipline-label-source has IN-DEGREE 0 and OUT-DEGREE >> 1) — ontology has IN-DEGREE 1 (within metaphysics it's IN the foundation spine itself, not at the very top). Direction sound on the discipline-to-its-central-question reading.
VERDICT: sound
CONFIDENCE: medium
NOTES: Closeout pattern-aggregation candidate for the pre-listed `discipline_label_node_at_root` validator soft-warn (master-plan §"Audit-system-input proposals" #2) — this is a SUB-discipline-label variant alongside the top-level variants surfaced at S-0112/S-0113/S-0114/S-0115.

#### Finding E-16
EDGE: existence [domain=metaphysics] → substance [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Substance" / "Existence" / "Aristotle's Categories" — substance is the canonical Aristotelian ontological category, the bearer of properties and the subject of change, with primary substances being individual concrete particulars and secondary substances being species and genera. The conceptual relationship is master-concept-to-ontological-category: existence is the master concept (the most-basic property-or-quantifier-shape), substance is one of the principal historical categories of existing things. Pedagogically the student needs the existence concept (the Frege-Quine quantifier reading; the Meinongian alternative; the existence-as-property dispute) before substance as one ontological-category posit makes sense. SEP exposition: "Existence" entry treats the existence concept as primitive, then "Substance" entry treats substance as one major ontological category whose existence is the central question. The seed's existence → substance edge runs in the canonical direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-17
EDGE: existence [domain=metaphysics] → property [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Properties" / "Existence" / "Universals vs Tropes" — property is the ontological category of attributes things have (color, shape, mass; redness, sphericality, gravitational mass) with the principal positions being universals-realism (Plato; Armstrong 1978 UNIVERSALS AND SCIENTIFIC REALISM), trope theory (Williams 1953 "On the Elements of Being"; Campbell 1990), and class nominalism. Master-concept-to-ontological-category like E-16: existence is the master concept, properties are one major ontological-category posit. Pedagogically the student needs the existence concept first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-18
EDGE: existence [domain=metaphysics] → relation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Relations (Stanford Encyclopedia of Philosophy)" / "Existence" — relations are the polyadic ontological category (loving, taller-than, between) whose ontological status mirrors that of monadic properties (universals-realism, trope theory, class nominalism). Master-concept-to-ontological-category like E-16/E-17: existence is the master concept, relations are one major ontological-category posit. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-19
EDGE: existence [domain=metaphysics] → event [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Events" / "Existence" — events are the dynamic ontological category (Kim 1976 property-exemplifications; Davidson 1969/1980 unstructured-particulars) whose existence and individuation are the central questions ("when do two event-descriptions pick out the same event?"). Master-concept-to-ontological-category. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-20
EDGE: existence [domain=metaphysics] → abstract_object [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entry on "Abstract Objects" / "Existence" — abstract objects (numbers, sets, propositions, possible worlds, types) are non-spatiotemporal non-causal entities whose existence is contested between platonist realists (Frege, Gödel, Quine reluctantly) and nominalists (Goodman, Field 1980 SCIENCE WITHOUT NUMBERS). Master-concept-to-ontological-category, with existence being precisely the disputed property at issue. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-21
EDGE: existence [domain=metaphysics] → concrete_object [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Abstract Objects" (which characterizes the abstract/concrete distinction) / "Existence" — concrete objects (spatiotemporally-located causally-efficacious entities — tables, electrons, persons) are the contrast class to abstract objects. The existence question for concrete objects is the noncontroversial half of the abstract/concrete dispute. Master-concept-to-ontological-category like E-16 through E-20. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-22
EDGE: existence [domain=metaphysics] → numerical_identity [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Identity" / "Identity Over Time" / "Existence" — numerical identity (the relation each thing bears to itself and only itself; Leibniz's Law of indiscernibility of identicals; the puzzle of qualitative-vs-numerical identity) presupposes the existence of relata to be (or fail to be) numerically identical. The conceptual relationship is master-concept-to-relation-on-existing-things: identity is a relation whose holding depends on the existing entities; pedagogically the student needs the existence concept before the identity-of-existing-things question is posed. SEP exposition: "Identity" entry treats existence as background, then articulates the identity relation. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-23
EDGE: existence [domain=metaphysics] → causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Metaphysics of Causation" / "Existence" / "Events" — causation is the relation between cause and effect (events, states of affairs) — and like identity (E-22), it is a relation whose holding presupposes the existence of relata. The conceptual relationship is master-concept-to-relation-on-existing-things. Pedagogically the student needs the existence concept (and arguably also the event concept per E-19) before the causation relation is articulated. The seed's edge runs existence → causation in the canonical direction. Direction sound. NOTE: this edge is the second of two inter-hub edges in this audit-task scope (alongside E-1 ej → pk); recorded once here.
VERDICT: sound
CONFIDENCE: high

#### Finding E-24
EDGE: existence [domain=metaphysics] → time [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Time" / "The Experience and Perception of Time" / "Existence" — time is the metaphysical topic of temporal becoming, A-theory vs B-theory, presentism vs eternalism vs growing block, and the persistence-through-time apparatus. The conceptual relationship is master-concept-to-philosophical-topic-with-existence-question-built-in: time's existence (in any robust sense beyond a sequence of A-properties or B-relations) is itself one of the disputed questions of the SEP "Time" entry. Pedagogically the student needs the existence concept before time as a metaphysical topic with its own existence-questions is articulated. Direction sound.
VERDICT: sound
CONFIDENCE: medium

#### Finding E-25
EDGE: existence [domain=metaphysics] → modality [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 5
SEP-ANCHORED REASONING: SEP entries on "Possibilism and Actualism" / "Modal Logic" / "Existence" — modality is the metaphysics of possibility and necessity, with the principal positions being modal realism (Lewis 1986 ON THE PLURALITY OF WORLDS; possible worlds as concrete maximal mereological sums), ersatz modal realism (possible worlds as abstract representations — propositions, properties, structures), and modal anti-realism. The existence-of-possibilia question (do possible-but-non-actual entities exist?) is the load-bearing question of the modality-existence interface. Pedagogically the student needs the existence concept (especially the actualism-vs-possibilism axis on whether existence is restricted to the actual) before modality as a topic that probes existence's bounds is articulated. SEP exposition: existence-and-quantifier apparatus is treated before modal apparatus; modal-existence questions are articulated against the existence-baseline. Direction sound.
VERDICT: sound
CONFIDENCE: high

### HUB C — propositional_knowledge (epistemology, deg 11)

(E-1 already recorded ej → propositional_knowledge as inter-hub edge.)

#### Finding E-26
EDGE: belief [domain=epistemology] → propositional_knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Belief" / "The Analysis of Knowledge" — propositional knowledge in the standard JTB analysis is a species of belief (specifically, justified true belief plus a Gettier-resistant condition); the student must hold the belief concept before the analysis of pk-as-belief-with-extra-conditions can be presented. SEP "The Analysis of Knowledge" entry composes belief, truth, justification, and a fourth clause; belief is the genus. Pedagogically belief comes first; the migration's edge runs belief → pk in the canonical genus-to-species direction (in the JTB sense). Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-27
EDGE: truth [domain=epistemology] → propositional_knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Truth" / "The Analysis of Knowledge" — truth is the second component of the JTB analysis (factivity: knowledge implies truth — one cannot know what is false). Pedagogically the student needs the truth concept (correspondence, coherence, deflationary, pragmatist theories; the factivity feature distinguishing knowing from merely believing) before the JTB composition is articulated. The migration's edge runs truth → pk in the canonical component-to-composition direction. Direction sound. Note: the migration places truth in the epistemology domain rather than philosophy of language; this is a domain-assignment choice that the closeout's aggregate-scan already considered (cross-bridges audit S-0104) — for this edge the assignment is irrelevant to the verdict (the JTB-component reading holds regardless of which subdomain "owns" truth).
VERDICT: sound
CONFIDENCE: high

#### Finding E-28
EDGE: propositional_knowledge [domain=epistemology] → justified_true_belief [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entry on "The Analysis of Knowledge" — justified_true_belief is the canonical pre-Gettier analysis of propositional knowledge (Plato Theaetetus precursor; mid-20th-century formalization). The conceptual relationship is concept-to-its-classical-analysis: pk is the analysandum, JTB is the proposed analysis (subsequently challenged by Gettier 1963 "Is Justified True Belief Knowledge?"). Pedagogically the student is introduced to pk as the analysandum and JTB as the canonical (and Gettier-falsified) analysis. The migration's edge runs pk → JTB. The direction is somewhat unusual on the canonical pedagogy: SEP exposition typically presents the JTB analysis as a way of articulating what pk IS, then notes Gettier counterexamples — students often learn JTB AS the entry-point to thinking about pk, suggesting JTB → pk would be the more natural direction. However the seed's direction (pk → JTB) is defensible on the reading "the student first needs the pk concept (knowledge-that as the target of analysis) before the proposed JTB analysis can be evaluated as an analysis OF pk." Both readings are SEP-supportable; the seed's choice runs concept → its-classical-analysis (vs. analysis → concept-it-analyzes, which the closeout might judge equally defensible). Recorded as defensible-medium per the master-plan §T1-A verdict taxonomy.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059. The shape is a CONCEPT-TO-CLASSICAL-ANALYSIS defensibility — distinct from prior routine-block reversal patterns; closeout adjudicates whether this analysis-direction-ordering pattern warrants a category in the disposition matrix.

#### Finding E-29
EDGE: propositional_knowledge [domain=epistemology] → knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "Knowledge" (broad survey) / "The Analysis of Knowledge" — the migration's `knowledge` node is the genus-level concept (the general epistemic standing encompassing both propositional knowledge / knowing-that and procedural knowledge / knowing-how), with the migration's own teaching_notes explicitly framing knowledge as "the genus of which the analyzed kinds are species" and noting the introductory ordering of "knowledge as undifferentiated intuition, then split into propositional and procedural." Per the migration's own framing the canonical pedagogical ordering is knowledge → pk (genus to species, undifferentiated intuition first, then split). The seed's edge runs the OPPOSITE direction: pk → knowledge. This is REVERSED on the migration's own framing. The seed's framing suggests the pedagogical ordering goes from the analyzable species (pk, where the JTB analysis is tractable) to the broader undifferentiated genus (knowledge); but this inverts the standard SEP and migration teaching_notes ordering. Distinct in shape: this is a SPECIES-TO-GENUS-INVERSION pattern within a single epistemology cluster, where the more-analyzed species is taught before the broader genus the species is part of. Distinct from prior routine-block patterns (S-0112 tools-vs-position; S-0114 question-vs-answer; S-0105 frameworks-vs-motivations; S-0108 position-vs-criterion; S-0110 argument-vs-position; S-0112/S-0113 developmental-arc; S-0115 cross-cluster-theoretical-thread; E-14 cross-bridge-inverting-genus-species). Note: the alternative reading is that the genus `knowledge` is so undifferentiated that students learn the species pk first as the more substantive concept, then come back to the genus retrospectively — this curriculum-ordering reading is plausible but conflates pedagogical-prerequisite (conceptual dependency) with curriculum-sequencing (presentation order). Per the master-plan §T1-A verdict taxonomy this is REVERSED on the conceptual-dependency reading. Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.
VERDICT: reversed
CONFIDENCE: medium
NOTES: This is the second REVERSED finding in this evidence file (after E-14). Closeout adjudicates whether to retype, redirect, or accept on the curriculum-sequencing reading.

#### Finding E-30
EDGE: propositional_knowledge [domain=epistemology] → knowledge_how [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entry on "Knowledge How" — knowledge-how (knowing how to do something) is distinguished from propositional knowledge (knowing-that) by Ryle 1949 THE CONCEPT OF MIND (the regress argument against intellectualism), with Stanley and Williamson 2001 "Knowing How" arguing for a reduction of knowledge-how to propositional knowledge of a way to perform the action. The conceptual relationship is contrast-class-to-foil: knowledge-how is pedagogically introduced AS the foil for propositional knowledge ("knowing-that is contrasted with knowing-how"); the student needs the propositional-knowledge concept first to understand what knowledge-how is being contrasted with. SEP exposition: "Knowledge How" entry opens with the propositional-knowledge contrast as the entry-point. The migration's own teaching_notes confirm: "Useful as a foil for showing what propositional knowledge isn't." Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-31
EDGE: propositional_knowledge [domain=epistemology] → tracking_theory_of_knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entries on "The Analysis of Knowledge" / "Reliabilist Epistemology" — tracking theory (Nozick 1981 PHILOSOPHICAL EXPLANATIONS chapter 3) is the canonical post-Gettier modal account of knowledge, replacing JTB's justification clause with sensitivity (in nearby possible worlds where p is false, S would not believe p) and safety. Master-concept-to-specific-theory: pk is the master concept (the thing-being-analyzed); tracking theory is one specific post-Gettier modal analysis. Pedagogically the student needs the pk concept first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-32
EDGE: propositional_knowledge [domain=epistemology] → testimonial_knowledge [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entry on "Epistemological Problems of Testimony" — testimonial knowledge (knowledge acquired through the testimony of others; the social-epistemology backbone of how most knowledge is in fact acquired in real life) is one source-kind of propositional knowledge alongside perception, memory, inference, introspection. Master-concept-to-source-kind: pk is the master concept; testimonial knowledge is one species individuated by source. Pedagogically the student needs pk first to articulate the source-question that testimonial knowledge answers. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-33
EDGE: propositional_knowledge [domain=epistemology] → certainty [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 2
SEP-ANCHORED REASONING: SEP entry on "Certainty" — certainty (the strongest epistemic standing; psychological certainty as conviction; epistemic certainty as the impossibility of being mistaken) is a higher-or-distinct epistemic standing relative to knowledge. The conceptual relationship is graded-epistemic-standing: pk is the focal standing being articulated; certainty is the stronger neighboring standing whose relation to pk is the central question (does knowledge require certainty? — Cartesian yes; modern fallibilism no). Pedagogically the student needs pk first to articulate the certainty-question as a question about epistemic stronger-than-pk. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: medium

#### Finding E-34
EDGE: propositional_knowledge [domain=epistemology] → understanding [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 3
SEP-ANCHORED REASONING: SEP entry on "Understanding" — understanding (Kvanvig 2003 THE VALUE OF KNOWLEDGE AND THE PURSUIT OF UNDERSTANDING; Pritchard 2010; Riggs 2003) is a contrast-and-extension epistemic standing with respect to pk — it is the grasping-of-explanatory-relations standing (understanding-WHY versus knowing-THAT) that contemporary value-of-knowledge debates argue is more valuable than pk. Master-concept-to-related-standing: pk is the focal standing; understanding is the related standing whose relation to pk is the central question (does understanding reduce to pk-of-explanatory-relations? — reductionists yes; non-reductionists no). Pedagogically the student needs pk first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: medium

#### Finding E-35
EDGE: propositional_knowledge [domain=epistemology] → norm_of_assertion [domain=epistemology]
   edge_type = pedagogical_prerequisite, weight = 3
SEP-ANCHORED REASONING: SEP entries on "Assertion" / "Knowledge Norm of Assertion" — the knowledge norm of assertion (Williamson 2000 KNOWLEDGE AND ITS LIMITS; "assert p only if you know p") is the leading position in the contemporary debate over what epistemic standing licenses assertion (alternatives: truth norm, justification norm, certainty norm). Master-concept-to-its-normative-application: pk is the master concept; the knowledge-norm-of-assertion is a normative-pragmatic claim ABOUT pk (specifically: pk is the norm). Pedagogically the student needs pk first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

### HUB D — causation (metaphysics, deg 10)

(E-23 already recorded existence → causation as inter-hub edge.)

#### Finding E-36
EDGE: event [domain=metaphysics] → causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Events" / "Metaphysics of Causation" — events are one of the two principal candidate-categories for the relata of causation (alongside states-of-affairs / facts; Kim 1976 / Davidson 1969-1980 events as relata; Mellor 1995 facts as relata). The conceptual relationship is relata-to-relation: events are the entities-in-question; causation is the relation that holds between them. Pedagogically the student needs the event concept (its individuation criteria; the unstructured-vs-structured debate; the fine-grained Kim / coarse-grained Davidson divide) before causation as a relation on events makes sense. SEP exposition: events articulated first, then causation as a relation typed over events. The migration's edge runs event → causation in the canonical relata-to-relation direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-37
EDGE: time [domain=metaphysics] → causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Time" / "Metaphysics of Causation" / "Causation and Manipulability" — time and causation are deeply entangled: causes typically precede their effects (the temporal-priority condition in Hume's analysis; the asymmetry-of-causation question; the closed-timelike-curve / backwards-causation debate). The conceptual relationship is structural-frame-to-relation-respecting-it: time is the metaphysical structure (A-theory / B-theory; presentism / eternalism / growing block) whose temporal-priority feature the causation relation typically respects. Pedagogically the student needs the time concept (the temporal-asymmetry; the past-present-future structure; the temporal-priority direction) before causation as a temporally-ordered relation is articulated. SEP exposition: time treated first, then causation against the temporal background. The migration's edge runs time → causation in the canonical structural-frame-to-relation-respecting-it direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-38
EDGE: causation [domain=metaphysics] → humean_regularity_theory [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Hume on Causation" / "Causal Processes" — the Humean regularity theory (Hume's Enquiry; Mackie's INUS conditions 1974 THE CEMENT OF THE UNIVERSE; the contemporary Best-System Analysis from Lewis-Beebee-Loewer) is the canonical reductive theory: c causes e iff c-types are constantly conjoined with e-types under appropriate temporal-priority and contiguity conditions. Master-concept-to-specific-theory: causation is the master concept; Humean regularity is one of the three principal accounts (alongside counterfactual and powers). Pedagogically the student needs the causation concept first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-39
EDGE: causation [domain=metaphysics] → counterfactual_theory_of_causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Counterfactual Theories of Causation" / "Metaphysics of Causation" — the counterfactual theory (Lewis 1973 "Causation"; Lewis 2000 "Causation as Influence") analyzes causation in terms of counterfactual dependence: c causes e iff (roughly) had c not occurred, e would not have occurred. Master-concept-to-specific-theory like E-38; the second of the three principal accounts. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-40
EDGE: causation [domain=metaphysics] → causal_powers [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 4
SEP-ANCHORED REASONING: SEP entries on "Dispositions" / "Powers" / "Metaphysics of Causation" — the causal-powers theory (Aristotelian neo-revival in Mumford 1998 DISPOSITIONS; Mumford and Anjum 2011 GETTING CAUSES FROM POWERS; Heil 2012 THE UNIVERSE AS WE FIND IT) holds that causation is grounded in the dispositional powers of objects rather than reduced to regularities or counterfactuals. Master-concept-to-specific-theory like E-38/E-39; the third of the three principal accounts. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-41
EDGE: causation [domain=metaphysics] → free_will [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 5
SEP-ANCHORED REASONING: SEP entries on "Free Will" / "Compatibilism" / "Causal Determinism" — free will is the metaphysical question of whether agents possess the kind of control over their actions that grounds moral responsibility, with the principal positions being compatibilism (free will compatible with determinism), libertarianism (free will requires indeterminism), and hard determinism / hard incompatibilism (no free will). Causation enters as the central machinery: the free-will question is precisely the question of whether the causal-explanation pattern that applies to natural events (deterministic or probabilistic) applies in a way that excludes free will. Pedagogically the student needs the causation concept (the causal-explanation pattern; the deterministic-vs-probabilistic divide; the supervenience-on-physical-causation question) before the free-will question is articulated. SEP exposition: causation treated first as the metaphysical machinery, then free-will as the question of how human action relates to causal-explanation patterns. The migration's edge runs causation → free_will in the canonical structural-machinery-to-question-it-frames direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-42
EDGE: causation [domain=metaphysics] → determinism [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 5
SEP-ANCHORED REASONING: SEP entry on "Causal Determinism" — determinism is the thesis that the entire history of the world is fixed by the natural laws plus the state of the world at any time; equivalently, every event is causally necessitated by prior events plus laws. The conceptual relationship is master-concept-to-thesis-formulated-using-it: causation is the master concept; determinism is a thesis whose statement uses causation as the central machinery. Pedagogically the student needs the causation concept (especially the deterministic-vs-probabilistic dimension) before determinism as the universal-causal-necessitation thesis is formulated. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-43
EDGE: aristotelian_four_causes [domain=service] → causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to metaphysics)
SEP-ANCHORED REASONING: SEP entries on "Aristotle on Causality" / "Aristotle's Metaphysics" / "Metaphysics of Causation" — Aristotle's four-causes analysis (material, formal, efficient, final causes from Physics II.3 and Metaphysics V.2) is one of the foundational historical frameworks for thinking about causation, distinguishing four ways of "answering the why-question" about a phenomenon. The seed's domain assignment places aristotelian_four_causes in the SERVICE subdomain (per ADR 0052 product Phase 5 subdomain decomposition; service nodes are "history-terminator" nodes — historical movements / schools / thinker-frameworks that anchor cross-domain pedagogy without belonging to any of the live philosophical subdomains). The cross-bridge runs aristotelian_four_causes → causation as pedagogical_prerequisite. **PER MASTER-PLAN §"Per-edge prompt template" verdict (e) — Mis-typed: historical-not-pedagogical**: the source is a thinker-framework (literally one of the named examples in the master-plan §"Per-node prompt template" step 2 granularity-mismatch list — "Aristotelian Four Causes"); the relation to causation is **influence**, not prerequisite. The contemporary theories of causation (Humean regularity, counterfactual, powers) are NOT pedagogical descendants of the four-causes framework — they are largely independent reformulations of the causation question, with the four-causes framework serving as historical context rather than as a conceptual ancestor that students need before encountering Hume / Lewis / Mumford. Per [PREDICATE_MANIFEST.md](../../../product/seed-graph/migrations/PREDICATE_MANIFEST.md), the reserved-but-unused `historical_influence` predicate is the appropriate retyping target for this edge. **Strengthens the structural reopen pre-flag** at master-plan §"Structural reopen pre-flag" — the cross-bridge census at S-0104 already cleared the ≥10 historical-not-pedagogical threshold, and within-service findings at S-0116 (E-2 presocratic_naturalism→aristotelian_four_causes; E-3 aristotelian_four_causes→vienna_circle_logical_positivism) extended the pattern from cross-bridges to within-service edges; this within-this-AUDIT-HT-1-fire finding extends the pattern to the cross-bridge-from-service-to-substantive-domain class as well. The closeout's predicate-activation memo can cite this evidence file as additional within-AUDIT-HT-1 confirmation. Distinct in shape from prior routine-block historical-not-pedagogical findings: this is a CROSS-BRIDGE-FROM-HISTORY-TERMINATOR-TO-SUBSTANTIVE-CONCEPT pattern, where the historical thinker-framework anchors the cross-bridge to a substantive subdomain concept that is canonically taught without the historical framework as prereq.
VERDICT: historical
CONFIDENCE: high
NOTES: Closeout fortifies as primary `historical_influence` retyping candidate. Closeout pattern-aggregation candidate alongside S-0104 / S-0116 historical-not-pedagogical findings.

#### Finding E-44
EDGE: causation [domain=metaphysics] → mental_causation [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from metaphysics to mind)
SEP-ANCHORED REASONING: SEP entry on "Mental Causation" — mental causation is the philosophy-of-mind question of how mental events (beliefs, desires, intentions) cause physical events (bodily movements) and other mental events, with the canonical machinery being the causal exclusion argument (Kim 1989 "Mechanism, Purpose, and Explanatory Exclusion"; Kim 1998 MIND IN A PHYSICAL WORLD) and the supervenience-of-mental-on-physical apparatus. The conceptual relationship is master-concept-to-restricted-application: causation is the master concept (the relation between cause and effect); mental causation is the application of the causation concept to the mental-physical interface, with its own distinctive puzzles (causal exclusion; over-determination; epiphenomenalism). Pedagogically the student needs the causation concept (especially the structural-machinery: relata, relation, exclusion, over-determination) before mental causation as an application-with-distinctive-puzzles is articulated. SEP "Mental Causation" entry presupposes general causation as background. The migration's edge runs causation → mental_causation in the canonical master-concept-to-restricted-application direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

### HUB E — physicalism (mind, deg 10)

#### Finding E-45
EDGE: mental_state [domain=mind] → physicalism [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entries on "Mental Representation" / "Physicalism" / "Mind" — mental states (beliefs, desires, perceptions, sensations, qualia, intentions) are the philosophy-of-mind primitive whose ontological status is precisely what physicalism takes a stand on. The conceptual relationship is target-of-thesis-to-thesis: mental states are the entities at issue; physicalism is the thesis that all mental states are physical (or grounded in the physical). Pedagogically the student needs the mental-state concept (the propositional-attitude / qualitative-experience taxonomy; the intentionality / phenomenality features) before physicalism as a thesis ABOUT mental states is articulated. SEP exposition: mental states treated first, then physicalism as the dominant ontological thesis about them. The migration's edge runs mental_state → physicalism in the canonical target-of-thesis-to-thesis direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-46
EDGE: physicalism [domain=mind] → type_identity_theory [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entries on "Mind/Brain Identity Theory" / "Physicalism" — type-identity theory (Place 1956 "Is Consciousness a Brain Process?"; Smart 1959 "Sensations and Brain Processes"; Lewis 1966 "An Argument for the Identity Theory"; Armstrong 1968 A MATERIALIST THEORY OF THE MIND) is the strongest reductive physicalist position: mental-state types are identical to brain-state types (pain IS C-fiber firing). Master-concept-to-specific-theory: physicalism is the umbrella thesis; type-identity theory is one of the principal type-physicalist positions, defended historically as the cleanest physicalist alternative to behaviorism. Pedagogically the student needs the physicalism umbrella first; SEP exposition runs in this direction. The migration's own physicalism teaching_notes confirm: "Teach type-identity theory as the cleanest physicalist position before functionalism complicates the picture." Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-47
EDGE: physicalism [domain=mind] → functionalism [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entry on "Functionalism" — functionalism (Putnam 1967 "The Nature of Mental States"; Lewis 1972 "Psychophysical and Theoretical Identifications"; Block 1978 "Troubles with Functionalism") is the dominant non-reductive physicalist position: mental states are individuated by their functional role (causal connections to inputs, outputs, and other mental states), allowing multiple physical realizations. Master-concept-to-specific-theory like E-46: physicalism is the umbrella; functionalism is the standard contemporary post-multiple-realizability physicalist position. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-48
EDGE: physicalism [domain=mind] → behaviorism_logical [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entry on "Behaviorism" — logical (or analytical) behaviorism (Ryle 1949 THE CONCEPT OF MIND; Hempel 1949 "The Logical Analysis of Psychology"; Carnap's 1932/1959 protocol-statement work) is the historical reductive physicalist position: mental-state ascriptions reduce to dispositional behavioral statements. Master-concept-to-specific-theory: physicalism is the umbrella; behaviorism is a historical physicalist proposal that motivated the type-identity / functionalism alternatives. Pedagogically the student needs the physicalism umbrella before behaviorism as one historical proposal is articulated. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-49
EDGE: physicalism [domain=mind] → eliminative_materialism [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entry on "Eliminative Materialism" — eliminative materialism (Feyerabend 1963 "Mental Events and the Brain"; Rorty 1965 "Mind-Body Identity, Privacy, and Categories"; Churchland 1981 "Eliminative Materialism and the Propositional Attitudes"; Churchland 1986 NEUROPHILOSOPHY) is the radical physicalist position: folk-psychological mental-state categories (belief, desire, etc.) are theoretical posits of a flawed proto-theory and may be eliminated rather than reduced as cognitive science matures. Master-concept-to-specific-theory: physicalism is the umbrella; eliminativism is one of the most radical species. Pedagogically the student needs the physicalism umbrella first; SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-50
EDGE: physicalism [domain=mind] → supervenience_mental [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 10
SEP-ANCHORED REASONING: SEP entries on "Supervenience" / "Physicalism" — mental supervenience is the central technical apparatus contemporary non-reductive physicalists use to articulate their position: mental properties supervene on physical properties (no mental difference without a physical difference) without being reducible to them. Davidson 1970 "Mental Events" introduced supervenience to the mind literature; Kim 1984 "Concepts of Supervenience" formalized strong / weak / global supervenience. Master-concept-to-technical-apparatus: physicalism is the substantive thesis; supervenience is the technical machinery used to articulate non-reductive physicalist versions. Pedagogically the student needs physicalism as the substantive thesis before the supervenience apparatus is introduced as the way to articulate non-reductive variants. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-51
EDGE: physicalism [domain=mind] → type_b_materialism [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 12
SEP-ANCHORED REASONING: SEP entries on "Physicalism" / "Phenomenal Concepts" / "The Knowledge Argument Against Physicalism" — type-B materialism (Loar 1990 "Phenomenal States"; Papineau 1993 PHILOSOPHICAL NATURALISM; Block and Stalnaker 1999) is one of the principal physicalist responses to the conceivability and knowledge arguments for dualism: the phenomenal-vs-physical conceptual dualism is real but does not entail metaphysical dualism — phenomenal concepts and physical concepts pick out the same physical properties via different modes of presentation. Master-concept-to-specific-theory like E-46/E-47/E-48/E-49: physicalism is the umbrella; type-B materialism is one specific physicalist position responding to the phenomenal-concepts challenge. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-52
EDGE: physicalism [domain=mind] → easy_problems_of_consciousness [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 12
SEP-ANCHORED REASONING: SEP entries on "Consciousness" / "The Hard Problem of Consciousness" — the easy / hard problems distinction (Chalmers 1995 "Facing Up to the Problem of Consciousness"; Chalmers 1996 THE CONSCIOUS MIND) carves consciousness questions into the easy problems (functional / cognitive abilities — discrimination, attention, integration, report) and the hard problem (phenomenal experience). The seed's edge runs physicalism → easy_problems_of_consciousness as pedagogical_prerequisite. The conceptual relationship is somewhat unusual on the canonical pedagogy: the easy/hard problems distinction is typically introduced as a way to FRAME the physicalism-dualism debate (the hard problem is the focus of anti-physicalist arguments; the easy problems are what physicalism CAN handle straightforwardly). The seed's direction (physicalism → easy_problems) reads as "physicalism is needed before the easy-problems concept is articulated" — but the easy-problems concept is articulated alongside the hard-problems concept as a Chalmers framing-device that students often encounter as the entry-point to the consciousness debate, with physicalism's relation to it being WHAT the easy/hard distinction is FOR. The reverse direction (easy_problems_of_consciousness → physicalism, as part of the framing machinery) might be more natural; the seed's direction is defensible on the reading "students need the physicalism umbrella to grasp what kinds of cognitive abilities physicalism can handle" but this reads physicalism as more entry-level than the consciousness-framing-device, which inverts standard pedagogy. Per the master-plan §T1-A verdict taxonomy this is DEFENSIBLE-MED (not strictly REVERSED because the physicalism-can-handle-easy-problems reading is supportable on contemporary physicalist literature, but the canonical entry-point reading favors the opposite direction). Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Distinct in shape from prior routine-block defensibility patterns. This is a FRAMING-DEVICE-VS-POSITION-ORDERING pattern, where a Chalmers-introduced framing-distinction (easy/hard problems) and a metaphysical position (physicalism) have an ambiguous canonical-pedagogical-ordering. Closeout adjudicates against the broader Chalmers-framing-device cluster.

#### Finding E-53
EDGE: greek_atomism [domain=service] → physicalism [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to mind)
SEP-ANCHORED REASONING: SEP entries on "Ancient Atomism" / "Democritus" / "Epicurus" / "Physicalism" — Greek atomism (Leucippus, Democritus, Epicurus, Lucretius's De Rerum Natura) is the historical-canonical materialist tradition, holding that all that exists is atoms and void. The seed's domain assignment places greek_atomism in the SERVICE subdomain (history-terminator class per ADR 0052 product). The cross-bridge runs greek_atomism → physicalism as pedagogical_prerequisite. **PER MASTER-PLAN §"Per-edge prompt template" verdict (e) — Mis-typed: historical-not-pedagogical** — same shape as E-43 (aristotelian_four_causes → causation): the source is a historical-school name (literally one of the named examples in the master-plan §"Per-node prompt template" step 2 granularity-mismatch list — "Vienna Circle, Scholasticism" is the exemplar, with greek_atomism in the same school-of-thought class); the relation to physicalism is influence, not prerequisite. Contemporary physicalism (type-identity, functionalism, eliminativism, non-reductive physicalism, type-B materialism) is NOT a pedagogical descendant of Greek atomism — the contemporary positions are framed against contemporary phenomenal-concepts / multiple-realizability / mental-causation puzzles, not against Greek atomistic precedents. Greek atomism is historical context, not conceptual ancestor. Per PREDICATE_MANIFEST.md, the reserved-but-unused `historical_influence` predicate is the appropriate retyping target. **Strengthens the structural reopen pre-flag** at master-plan §"Structural reopen pre-flag" — second within-AUDIT-HT-1 historical-not-pedagogical finding (after E-43). The closeout's predicate-activation memo can cite both within-AUDIT-HT-1 findings.
VERDICT: historical
CONFIDENCE: high
NOTES: Closeout fortifies as primary `historical_influence` retyping candidate. Closeout pattern-aggregation candidate alongside E-43 + S-0104 / S-0116 historical-not-pedagogical findings. The two within-AUDIT-HT-1 historical findings (E-43 + E-53) both involve service-to-substantive-subdomain cross-bridges, supporting the closeout's posture that the history-terminator sub-class is the principal locus of the historical_influence predicate-activation case.

#### Finding E-54
EDGE: physicalism [domain=mind] → reductionism_in_science [domain=science]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from mind to science)
SEP-ANCHORED REASONING: SEP entries on "Scientific Reduction" / "Physicalism" / "Multiple Realizability" — reductionism in science (Nagel 1961 THE STRUCTURE OF SCIENCE on inter-theoretic reduction via bridge laws; Kim 1992 "Multiple Realization and the Metaphysics of Reduction"; Sober 1999 "The Multiple Realizability Argument Against Reductionism") is the methodological / metaphysical thesis that higher-level scientific theories reduce to lower-level theories (typically: psychology to neuroscience, biology to chemistry, chemistry to physics). The conceptual relationship is canonical-application-to-broader-thesis: physicalism in mind (especially type-identity-theory and reductive physicalism) is the canonical philosophical case study for reductionism's prospects, but reductionism-in-science is a broader thesis covering all inter-theoretic-reduction questions across the sciences. Pedagogically the canonical exposition runs: introduce reductionism-in-science as the broader methodological thesis (via Nagel, the unity-of-science programme, the Oppenheim-Putnam levels), then introduce physicalism in mind as one prominent application. The seed's edge runs physicalism → reductionism_in_science (i.e., physicalism is prereq to reductionism-in-science), which inverts the canonical broader-thesis-to-application ordering. The seed's direction is defensible on the reading "students learn physicalism first as a familiar metaphysical thesis in the mind cluster, then encounter reductionism-in-science as the generalization of physicalism's reductive ambition" — but this reads physicalism as the entry-point to reductionism-in-science, which inverts the canonical SEP exposition where reductionism-in-science is the broader methodological frame and physicalism is one canonical application. Per the master-plan §T1-A verdict taxonomy this is REVERSED-MED on the broader-to-application reading; defensible-MED on the application-as-entry-point reading. The closeout adjudicates which reading governs — but the inversion is salient. Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.
VERDICT: reversed
CONFIDENCE: medium
NOTES: Third REVERSED finding in this evidence file (after E-14 ej → propositional_attitude and E-29 pk → knowledge). Distinct in shape from E-14 (cross-bridge-inverting-genus-species) and E-29 (within-cluster species-to-genus-inversion); this is a CROSS-BRIDGE-INVERTING-BROADER-THESIS-AND-APPLICATION pattern, where the cross-bridge runs from a canonical APPLICATION (physicalism in mind) to the broader METHODOLOGICAL THESIS (reductionism-in-science). Closeout fortifies and aggregates with E-14 / E-29 to assess whether cross-cluster genus-species inversion is a recurrent shape worth a soft-warn proposal.

## Sampled-node candidate findings

### Finding N-1
NODE: epistemic_justification [id=epistemic_justification, domain=epistemology]
   summary = "The property a belief has when the believer has adequate epistemic grounds for holding it. The third clause of the standard JTB analysis of knowledge and the surface where theories of justification (internalism vs externalism, foundationalism vs coherentism vs infinitism) compete."
SEP-ANCHORED REASONING: SEP entry on "Epistemic Justification" — stand-alone canonical entry. Granularity: concept-level (a specific philosophical concept — the normative property of beliefs — with the precise dialectical content of the structural axis (foundationalism / coherentism / infinitism), the access axis (internalism / externalism), and the principal theories (reliabilism, evidentialism, virtue epistemology)). The migration's framing of justification as normative-relative-to-epistemic-obligations, distinct from mere reliability and from truth (fallibilism), is SEP-canonical. Summary reads as instructional voice with concept-grounded specificity (canonical references implicit through the structural / access axis taxonomy and the foundationalism / coherentism / infinitism + internalism / externalism + reliabilism / evidentialism / virtue epistemology + skepticism dialectical map). No granularity-mismatch (epistemic_justification is at appropriate concept-level — the JTB clause and the surface of contemporary justification-theory dispute, not a discipline-label or school-name). No authenticity concerns. Hub-node observation: this hub's deg-14 fan-out is structurally well-grounded (the 11 outgoing edges instantiate the canonical taxonomy of justification theories — three structural / two access / three principal theories / one skeptical denial / two cross-bridges; the 3 incoming edges instantiate the canonical components of justification — belief, evidence, argument). The single REVERSED finding (E-14 ej → propositional_attitude) is the lone structural defect in the hub's fan-out.
VERDICT: sound
CONFIDENCE: high

### Finding N-2
NODE: existence [id=existence, domain=metaphysics]
   summary = "The most basic property a thing has when it is — when it figures in the world rather than being merely thought of, hoped for, or denied. Whether existence is a property at all (Kant, Frege, Quine) is itself contested. Treated by Quine and standard predicate logic as captured by the existential quantifier rather than as a first-order predicate of individuals."
SEP-ANCHORED REASONING: SEP entries on "Existence" / "Logic and Ontology" / "Possible Objects" — stand-alone canonical entries. Granularity: concept-level (a specific philosophical concept — the most-basic-property-or-quantifier-shape — with the precise three-layer dialectical content of (1) the metaphysical question whether existence is univocal, (2) the logical question whether existence is a quantifier or a predicate (Kant: not a real predicate; Frege/Russell: a property of concepts; Meinong: a predicate of objects, some of which lack it), (3) the ontological question what kinds of thing exist). The migration's three-layer framing, the Frege-Quine mainstream characterization, and the Meinongian alternative with serious contemporary defenders (Parsons, Routley, Priest) is SEP-canonical. Summary reads as instructional voice with concept-grounded specificity (canonical citations Kant, Frege, Russell, Quine, Meinong, Parsons, Routley, Priest; the three-layer structure; the mainstream-vs-Meinongian dispute). No granularity-mismatch (existence is at appropriate concept-level — a specific philosophical concept with precise dialectical content, not a discipline-label or school-name). No authenticity concerns. Hub-node observation: this hub's deg-11 fan-out is the canonical ontology-as-discipline-output spread (substance, property, relation, event, abstract_object, concrete_object, numerical_identity, time, modality, causation as the core ontological-category and ontology-relation taxonomy). The fan-out is structurally well-grounded with no defects observed in the 11 incident edges; the inter-hub edge to causation (E-23) and to the time / modality neighbors (E-24 / E-25) shows this hub's centrality to metaphysics.
VERDICT: sound
CONFIDENCE: high

### Finding N-3
NODE: propositional_knowledge [id=propositional_knowledge, domain=epistemology]
   summary = "Knowledge that some proposition is true — knowing-that. The primary target of the analysis-of-knowledge tradition, standardly analyzed as justified true belief plus a Gettier-resistant condition. Contrasts with knowledge-how (knowing how to do something)."
SEP-ANCHORED REASONING: SEP entries on "The Analysis of Knowledge" / "Knowledge How" — stand-alone canonical entries. Granularity: concept-level (a specific philosophical concept — knowing-that — with the precise dialectical content of the JTB analysis, the Gettier-resistant fourth-clause work (no false lemmas, defeasibility, sensitivity, safety, virtue-theoretic), and the contrast with knowledge-how (Ryle 1949 vs Stanley-Williamson 2001)). The migration's framing of pk as the analysis-of-knowledge target (because belief, truth, justification are independently studied components and the JTB analysis is tractable), the Stanley-Williamson reductionist position on knowledge-how, and the propositional / procedural distinction is SEP-canonical. Summary reads as instructional voice with concept-grounded specificity (canonical citations Ryle, Stanley-Williamson; the JTB structure; the Gettier-resistant condition; the propositional / procedural distinction). No granularity-mismatch (propositional_knowledge is at appropriate concept-level — a specific philosophical concept with precise dialectical content, not a discipline-label or school-name). No authenticity concerns. Hub-node observation: this hub's deg-11 fan-out is structurally well-grounded for the JTB-analysis cluster (10 of 11 incident edges are canonical analysis-of-knowledge content); the single REVERSED finding (E-29 pk → knowledge) reflects an unusual species-to-genus-inversion within the cluster, distinct from prior routine-block patterns and a candidate for closeout fortification.
VERDICT: sound
CONFIDENCE: high

### Finding N-4
NODE: causation [id=causation, domain=metaphysics]
   summary = "The relation between cause and effect — what one event or state of affairs does to bring another about. Cited in scientific explanation, ordinary action description, legal responsibility attribution, and counterfactual reasoning. The metaphysics of causation asks what the relation consists in; the major contemporary accounts are regularity, counterfactual, and dispositional/powers theories."
SEP-ANCHORED REASONING: SEP entries on "Metaphysics of Causation" / "Causation and Manipulability" / "Hume on Causation" / "Counterfactual Theories of Causation" / "Powers" — stand-alone canonical entries. Granularity: concept-level (a specific philosophical concept — the cause-effect relation — with the precise dialectical content of the post-Humean three-account taxonomy (regularity, counterfactual, powers) and the cross-domain employment in scientific explanation, action description, legal responsibility, and counterfactual reasoning). The migration's framing of Hume's starting move (deny direct perception of necessary connection — observe constant conjunction, infer causation), the post-Humean split (regularity reductionists, Lewis counterfactual, Aristotelian-powers Mumford-Anjum), and the pedagogical recommendation to teach the three theories in dialogue is SEP-canonical. Summary reads as instructional voice with concept-grounded specificity (canonical citations Hume, Lewis, Mumford-Anjum; the three-account taxonomy; the cross-domain employment). No granularity-mismatch (causation is at appropriate concept-level — a specific philosophical concept with precise dialectical content, not a discipline-label or school-name). No authenticity concerns. Hub-node observation: this hub's deg-10 fan-out is structurally well-grounded except for the one historical cross-bridge defect (E-43 aristotelian_four_causes → causation, which retypes to historical_influence rather than the seed's pedagogical_prerequisite); the substantive theory-fan (E-38 / E-39 / E-40 to humean / counterfactual / powers) and the application-fan (E-41 free_will, E-42 determinism, E-44 mental_causation) are all canonical.
VERDICT: sound
CONFIDENCE: high

### Finding N-5
NODE: physicalism [id=physicalism, domain=mind]
   summary = "The thesis that everything is physical: every concrete particular is a physical particular; every property either is a physical property or is grounded in physical properties; minds are not exceptions. The dominant metaphysical framework in contemporary analytic philosophy of mind. Differentiates into type-identity theory, functionalism, behaviorism, eliminativism, and non-reductive physicalism according to how it handles the apparent autonomy of the mental."
SEP-ANCHORED REASONING: SEP entries on "Physicalism" / "Multiple Realizability" / "Mind/Brain Identity Theory" — stand-alone canonical entries. Granularity: concept-level (a specific philosophical thesis — everything is physical, with mental states no exception — with the precise dialectical content of the type / token-physicalism distinction, the principal species (type-identity, functionalism, behaviorism, eliminativism, non-reductive physicalism), the principal anti-physicalist arguments (Mary / knowledge argument, zombies / conceivability, multiple-realizability against type-physicalism), and the contemporary majority position (non-reductive token-physicalist functionalism)). The migration's framing of physicalism as umbrella-not-particular-theory, the type / token distinction, the Davidson anomalous-monism reference, the multiple-realizability and Mary / zombies anti-physicalist machinery, and the contemporary-majority non-reductive functionalist position is SEP-canonical. Summary reads as instructional voice with concept-grounded specificity (canonical citations Davidson, Mary / Jackson 1982, zombies / Chalmers 1996, multiple-realizability / Putnam 1967, contemporary functionalism; the type / token-physicalism distinction; the anti-physicalist argument taxonomy). No granularity-mismatch (physicalism is at appropriate concept-level — a specific philosophical thesis with precise dialectical content, not a discipline-label or school-name). No authenticity concerns. Hub-node observation: this hub's deg-10 fan-out is structurally well-grounded for the principal-species cluster (E-46 / E-47 / E-48 / E-49 to type-identity / functionalism / behaviorism / eliminativism; E-50 supervenience; E-51 type-B-materialism; E-52 easy-problems-of-consciousness defensible-MED; E-45 mental_state inbound). The two cross-bridge defects (E-53 greek_atomism→physicalism historical-HIGH; E-54 physicalism→reductionism_in_science reversed-MED) constitute 2 of the 10 incident edges (20%) and are the primary structural defects in this hub.
VERDICT: sound
CONFIDENCE: high

## Cross-cutting observations

Three observations recorded sparingly per master-plan §T2-D — closeout is the synthesis surface, not the per-session evidence file.

1. **HISTORICAL_INFLUENCE PREDICATE-ACTIVATION continued strengthening.** Two within-AUDIT-HT-1 historical-not-pedagogical findings (E-43 aristotelian_four_causes → causation HIGH, E-53 greek_atomism → physicalism HIGH) extend the pattern from cross-bridges (S-0104) and within-service edges (S-0116) to the cross-bridge-from-history-terminator-to-substantive-domain class. Both findings have HIGH confidence — the source nodes are precisely the named examples in the master-plan §"Per-node prompt template" granularity-mismatch list ("Aristotelian Four Causes"; "Vienna Circle, Scholasticism"-class school-name greek_atomism), and the contemporary theories of causation / physicalism are framed against contemporary puzzles, not against the historical precedents the cross-bridges anchor. The structural reopen pre-flag at master-plan §"Structural reopen pre-flag" (≥10 ADR-warranting threshold) is now well-clear with 14 cross-bridges from S-0081/S-0104 + within-service S-0116 + 2 within-AUDIT-HT-1 = 16+ historical-not-pedagogical findings; the closeout's predicate-activation memo (whether to activate `historical_influence` per PREDICATE_MANIFEST.md, or maintain the S-0075 rejection of `cross_domain_dependency`) has decisive evidence. AUDIT-HT-2 may add further history-terminator-anchored cross-bridge findings (vienna_circle_logical_positivism is in HUB 6–10 scope per the auto_target task description); the closeout aggregates the full corpus.

2. **CROSS-CLUSTER GENUS-SPECIES INVERSION as a recurrent shape across AUDIT-HT-1.** Three REVERSED findings (E-14 ej → propositional_attitude — cross-bridge-inverting-genus-species; E-29 pk → knowledge — within-cluster species-to-genus-inversion; E-54 physicalism → reductionism_in_science — cross-bridge-inverting-broader-thesis-and-application) cluster around the same structural pattern: a more-specific concept (or specific application) is taught before the broader genus (or broader methodological thesis) that contains or generalizes it. Two of the three are cross-bridges (E-14, E-54) and one is within-cluster (E-29). The pattern is distinct from prior routine-block reversal patterns (S-0112 tools-vs-position; S-0114 question-vs-answer; S-0105 frameworks-vs-motivations; S-0108 position-vs-criterion; S-0110 argument-vs-position; S-0112 / S-0113 developmental-arc; S-0115 cross-cluster-theoretical-thread-ordering). The clustering of three instances within a single hub-audit fire raises the closeout's question of whether GENUS-SPECIES-INVERSION-AT-CROSS-BRIDGE merits a soft-warn proposal in addition to the four pre-listed proposals at master-plan §"Audit-system-input proposals" — specifically, a candidate `cross_bridge_genus_species_direction_inverted` validator soft-warn that fires when a cross-bridge runs species → genus rather than genus → species. Per master-plan §T2-B verdict-taxonomy "other" provision, recording for closeout aggregation; the closeout decides whether to add a category to the disposition matrix.

3. **HUB-CENTRALITY VALIDATES as a DEFENSE-SIDE finding.** All 5 hubs reviewed have substantively well-grounded N-verdicts (5 sound-high) and predominantly sound E-verdicts (47 of 54 = 87% sound; 4 defensible / reversed clustering as observation 2 above; 2 historical clustering as observation 1 above; 1 sound-medium E-9 skepticism with cross-target-anchoring ambiguity not constituting a defect). The high-substantive-soundness-rate of the top-5 hubs is a calibration-positive finding for the closeout — the graph's most-central nodes are not the principal locus of substantive defects, suggesting that the per-subdomain defect rates surfaced in the routine block (S-0112 language 21%, S-0108 ethics 17%, S-0109 metaphysics 14%, S-0116 service 22%, etc.) are concentrated in lower-degree edges and nodes rather than in the structural backbone. AUDIT-HT-2 (hubs 6–10 + 3 syllabus traces) extends this calibration to the next 5 hubs and tests whether the trend holds; if so, the closeout's audit summary can record the structural-backbone-is-sound finding alongside the lower-degree-defect findings.

## SEP citations consulted

- SEP entry: "Epistemic Justification"
- SEP entry: "Foundationalist Theories of Epistemic Justification"
- SEP entry: "Coherentist Theories of Epistemic Justification"
- SEP entry: "Infinitism in Epistemology"
- SEP entry: "Internalist vs. Externalist Conceptions of Epistemic Justification"
- SEP entry: "Reliabilist Epistemology"
- SEP entry: "Evidentialism"
- SEP entry: "Virtue Epistemology"
- SEP entry: "Skepticism"
- SEP entry: "Cartesian Skepticism"
- SEP entry: "The Analysis of Knowledge"
- SEP entry: "Belief"
- SEP entry: "Evidence"
- SEP entry: "Argument" (logical sense)
- SEP entry: "Logical Consequence"
- SEP entry: "Propositional Attitude Reports"
- SEP entry: "Intentionality"
- SEP entry: "Truth"
- SEP entry: "Knowledge How"
- SEP entry: "Epistemological Problems of Testimony"
- SEP entry: "Certainty"
- SEP entry: "Understanding"
- SEP entry: "Assertion"
- SEP entry: "Knowledge Norm of Assertion"
- SEP entry: "Existence"
- SEP entry: "Logic and Ontology"
- SEP entry: "Quine on Ontology"
- SEP entry: "Substance"
- SEP entry: "Aristotle's Categories"
- SEP entry: "Properties"
- SEP entry: "Universals vs Tropes"
- SEP entry: "Relations" (Stanford Encyclopedia of Philosophy)
- SEP entry: "Events"
- SEP entry: "Abstract Objects"
- SEP entry: "Identity"
- SEP entry: "Identity Over Time"
- SEP entry: "Time"
- SEP entry: "The Experience and Perception of Time"
- SEP entry: "Possibilism and Actualism"
- SEP entry: "Modal Logic"
- SEP entry: "Metaphysics of Causation"
- SEP entry: "Causation and Manipulability"
- SEP entry: "Hume on Causation"
- SEP entry: "Causal Processes"
- SEP entry: "Counterfactual Theories of Causation"
- SEP entry: "Dispositions"
- SEP entry: "Powers"
- SEP entry: "Free Will"
- SEP entry: "Compatibilism"
- SEP entry: "Causal Determinism"
- SEP entry: "Aristotle on Causality"
- SEP entry: "Aristotle's Metaphysics"
- SEP entry: "Ancient Atomism"
- SEP entry: "Democritus"
- SEP entry: "Epicurus"
- SEP entry: "Mental Causation"
- SEP entry: "Mental Representation"
- SEP entry: "Physicalism"
- SEP entry: "Mind/Brain Identity Theory"
- SEP entry: "Functionalism"
- SEP entry: "Behaviorism"
- SEP entry: "Eliminative Materialism"
- SEP entry: "Supervenience"
- SEP entry: "Phenomenal Concepts"
- SEP entry: "The Knowledge Argument Against Physicalism"
- SEP entry: "Consciousness"
- SEP entry: "The Hard Problem of Consciousness"
- SEP entry: "Multiple Realizability"
- SEP entry: "Scientific Reduction"
