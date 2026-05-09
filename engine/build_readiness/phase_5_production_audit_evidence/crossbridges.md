# Phase 5 production audit evidence — cross-bridges (full census)

> Authored by S-0104 (routine session) per T-PHASE-5-AUDIT task `AUDIT-CB`.
> SEP-anchored review per [`engine/build_readiness/phase_5_production_audit.md`](../phase_5_production_audit.md).
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: cross-bridges (the 71 cross-domain edges authored at S-0075 in `product/seed-graph/migrations/0060_seed_crossbridges_part1.sql`)
- Edge population: 71 cross-domain edges (45 service-node → philosophy in three sub-groupings A1/A2/A3 + 26 within-philosophy cross-subdomain B; per the migration's authoring grouping)
- Edge sample size: **71** (full census)
- Sample density: **100%**
- Sample selection: full census — document order matches the migration's `INSERT ... VALUES` listing; no random sampling required (per master plan §"Sample-size policy" AUDIT-CB row, full census is the design)
- Node sample size: N/A — cross-bridges have no node sample. Per master-plan §"Sample-size policy", node coverage for the source/target endpoints of these edges is the responsibility of the per-subdomain audit tasks (AUDIT-EPI, AUDIT-MET, AUDIT-MIN, AUDIT-LAN, AUDIT-LOG, AUDIT-SCI, AUDIT-POL, AUDIT-AES, AUDIT-ETH, AUDIT-SVC, AUDIT-HT) which each draw edge-anchored node samples within their subdomain
- Generation date: 2026-05-09

## Sampled-edge candidate findings

The 71 findings are organized by the migration's three sub-groupings (A1, A2, A3) plus the within-philosophy bridges (B). The verdict labels follow the master-plan §"Per-edge prompt template" taxonomy: `sound` | `defensible` | `reversed` | `weak` | `historical` (mis-typed: historical-not-pedagogical) | `thematic` | `other`. Confidence: `high` | `medium` | `low`.

### A1 — Service formal-logic primitives → philosophy (15 edges)

#### Finding E-1
EDGE: `truth_value` [service] → `classical_logic` [logic]
   edge_type = pedagogical_prerequisite, weight/confidence/evidence per migration (uniform across all 71 — the evidence text is null graph-wide, a known finding pre-listed in master plan)
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" (and adjacent entry "Many-Valued Logic") frames classical logic by its bivalent two-valued semantics. The semantic value primitive (true/false) is foundational; classical logic's truth-functional connectives are defined over the truth-value set {T, F}. Pedagogical direction matches: to understand classical logic's semantics, the prior concept of truth-value is required.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-2
EDGE: `bivalence_principle` [service] → `classical_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" treats bivalence (every proposition is true or false, exclusively) as one of classical logic's defining commitments alongside LEM and LNC. Pedagogical direction sound: students must grasp bivalence to understand what classical logic IS as a semantic framework — and to understand what the deviant logics deviate from.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-3
EDGE: `bivalence_principle` [service] → `dialetheism` [logic]
SEP-ANCHORED REASONING: SEP entry on "Dialetheism" defines the position as accepting that some contradictions are true. The entry's framing presupposes the reader's familiarity with bivalence and LNC, both of which dialetheism rejects in specific ways. Pedagogical direction sound: dialetheism is intelligible only against bivalence as the rejected commitment.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-4
EDGE: `bivalence_principle` [service] → `fuzzy_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Fuzzy Logic" frames the system by its admission of degrees of truth on [0,1], abandoning bivalence. The pedagogical direction is sound: fuzzy logic's distinguishing feature is precisely the rejection of bivalence in favor of graded truth-values.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-5
EDGE: `bivalence_principle` [service] → `paraconsistent_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Paraconsistent Logic" frames the system by its tolerance of contradictions without explosion (rejecting `A, ¬A ⊢ B`). The most proximate prereq for paraconsistency is the classical principle of explosion (ex contradictione quodlibet), which depends on the broader truth-functional semantics of classical logic — not bivalence specifically. Some paraconsistent systems (LP, FDE) do reject bivalence; relevant logics keep bivalence and reject other features. The bivalence-as-prereq framing is partially right but not the most proximate prereq.
VERDICT: weak
CONFIDENCE: medium
NOTES: A more proximate prereq exists in graph (`classical_logic` itself, via the explosion principle's relationship to classical inferences); could be subsumed by transitivity. Concurs with the S-0081 gate's flag of this edge as questionable.

#### Finding E-6
EDGE: `argument_logical` [service] → `epistemic_justification` [epistemology]
SEP-ANCHORED REASONING: SEP entry on "Epistemic Justification" / "Justification, Epistemic" treats arguments as one paradigmatic vehicle by which beliefs become justified (alongside non-argumentative routes — direct perception, reliabilist process inputs, etc.). The argument concept is genuinely scaffolding for the standard inferential-justification picture, even if not strictly load-bearing for every account (reliabilism, foundationalism without argument-structure). Pedagogical direction sound on the dominant-textbook framing.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-7
EDGE: `validity_logical` [service] → `classical_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" / "Logical Consequence" presents validity as the form-based truth-preservation property that classical logic formalizes. To grasp classical logic as a system, the prior informal concept of validity is required.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-8
EDGE: `soundness_logical` [service] → `formal_epistemology` [epistemology specialized]
SEP-ANCHORED REASONING: SEP entry on "Formal Epistemology" surveys probability theory, decision theory, modal/epistemic logics, belief revision (AGM), and so on. Soundness (validity + true premises) is one logical concept, but it's not the canonical proximate prereq for formal epistemology — the canonical prereqs are probability theory and modal logic. The connection is real (some belief-revision logics appeal to soundness), but the SEP entry would not lead with soundness as a definitional prereq.
VERDICT: defensible
CONFIDENCE: medium
NOTES: A more canonical prereq would be `probability_mathematical` or `modal_logic`. Acceptable as a long-distance shortcut; closeout may consider whether to keep, prune, or reroute.

#### Finding E-9
EDGE: `inference_rule` [service] → `propositional_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" (propositional-logic section) treats propositional logic via its proof systems (natural deduction, sequent calculus, axiomatic), each defined by a set of inference rules. The inference-rule concept is the syntactic primitive on which these systems are built. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-10
EDGE: `inference_rule` [service] → `predicate_logic` [logic]
SEP-ANCHORED REASONING: Same shape as E-9 — predicate logic extends propositional logic with quantifier inference rules (UI, EI, UG, EG). The inference-rule concept is the syntactic primitive. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-11
EDGE: `modus_ponens` [service] → `propositional_logic` [logic]
SEP-ANCHORED REASONING: Modus ponens is the canonical truth-functional inference rule. SEP "Classical Logic" treats MP as paradigm for natural deduction's elimination rules. There is a pedagogical concern about whether MP is *prereq* to propositional logic vs *content* of it (axiomatizations like Łukasiewicz's reduce primitive rules and could in principle reach MP as a derived rule). On dominant textbook framing, students learn MP first informally, then see it formalized — pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-12
EDGE: `modus_tollens` [service] → `propositional_logic` [logic]
SEP-ANCHORED REASONING: Same shape as E-11. MT is the contrapositive form of MP, treated in propositional logic's proof systems. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-13
EDGE: `modus_tollens` [service] → `falsificationism` [science]
SEP-ANCHORED REASONING: SEP entry on "Karl Popper" / "Karl Popper" identifies the formal structure of falsification with modus tollens applied to the conditional `H → O`: derive O, observe ¬O, infer ¬H. The connection is genuinely formal-logical, not merely heuristic. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-14
EDGE: `formal_proof` [service] → `classical_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" / "Proof Theory" treats classical logic via its proof systems; the formal-proof concept (a finite syntactic derivation) is foundational to studying any of those systems. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-15
EDGE: `counterexample` [service] → `gettier_problem` [epistemology]
SEP-ANCHORED REASONING: SEP entry on "The Analysis of Knowledge" treats Gettier cases as paradigm counterexamples to the JTB analysis: a single instance where JTB conditions hold without knowledge suffices to refute the universal claim "JTB ⟹ knowledge." The counterexample concept is genuinely the prerequisite scaffolding. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### A2 — Service math prerequisites → philosophy (12 edges)

#### Finding E-16
EDGE: `set_mathematical` [service] → `russell_paradox` [logic]
SEP-ANCHORED REASONING: SEP entry on "Russell's Paradox" frames the paradox as arising from unrestricted set comprehension over a putatively self-membered set. The set concept is the scaffolding without which the paradox is unintelligible. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-17
EDGE: `set_mathematical` [service] → `possible_worlds` [metaphysics specialized]
SEP-ANCHORED REASONING: SEP entry on "Possible Worlds" surveys multiple ontological accounts (Lewis's modal realism treats worlds as concrete entities; Plantinga treats worlds as abstract maximal states of affairs). Most formal frameworks model worlds set-theoretically (e.g., as sets of propositions, or as primitive elements of a domain). But the philosophical concept of possible-world is not strictly identical to its set-theoretic formalization. Defensible: most formal usages presuppose set theory, but the philosophical concept could be approached without set-theoretic apparatus.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Sound under any formal-semantics framing; defensible under non-set-theoretic framings (Lewis modal realism, Plantinga haecceitism).

#### Finding E-18
EDGE: `set_mathematical` [service] → `kripke_semantics` [logic]
SEP-ANCHORED REASONING: SEP entry on "Modal Logic" / "Possible Worlds Semantics" defines a Kripke frame as a tuple ⟨W, R, V⟩ where W is a set, R ⊆ W×W, and V is an assignment function. Set-theoretic at every level. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-19
EDGE: `quantifier` [service] → `predicate_logic` [logic]
SEP-ANCHORED REASONING: Predicate logic IS quantifier logic — propositional logic plus universal/existential quantification. SEP entry on "Quantifiers and Quantification" treats the variable-binding logical operators as the predicate-logic primitive. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-20
EDGE: `probability_mathematical` [service] → `bayesian_epistemology` [epistemology specialized]
SEP-ANCHORED REASONING: SEP entry on "Bayesian Epistemology" defines credences as belief-degrees satisfying the probability axioms. The formal probability measure is the foundation. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-21
EDGE: `probability_mathematical` [service] → `bayesianism_confirmation` [science]
SEP-ANCHORED REASONING: SEP entry on "Bayes' Theorem" / "Confirmation Theory" treats Bayesian confirmation as a formal probability calculus over hypotheses and evidence. Probability theory is the foundation. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-22
EDGE: `conditional_probability` [service] → `conditionalization` [epistemology specialized]
SEP-ANCHORED REASONING: SEP entry on "Bayesian Epistemology" / "Imaging and Conditionalization" defines conditionalization via P_new(H) = P_old(H | E). The conditional-probability operation is the formal scaffolding. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-23
EDGE: `bayes_theorem` [service] → `bayesian_epistemology` [epistemology specialized]
SEP-ANCHORED REASONING: SEP entry on "Bayes' Theorem" / "Bayesian Epistemology" treats Bayes' theorem as the canonical inversion identity used to compute posterior credences. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-24
EDGE: `bayes_theorem` [service] → `bayesianism_confirmation` [science]
SEP-ANCHORED REASONING: Same shape as E-23 — Bayesian confirmation is canonically formulated using Bayes' theorem to compute the degree of confirmation E lends to H. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-25
EDGE: `expected_value` [service] → `dutch_book_argument` [epistemology specialized]
SEP-ANCHORED REASONING: SEP entry on "Dutch Book Arguments" frames the argument as showing that an agent with probabilistically incoherent credences accepts a set of bets with jointly negative expected value. The expected-value concept is genuinely the formal scaffolding. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-26
EDGE: `expected_value` [service] → `utilitarianism` [ethics metaethics+normative]
SEP-ANCHORED REASONING: SEP entry on "Consequentialism" / "The History of Utilitarianism" surveys both classical utilitarianism (Bentham, Mill) and decision-theoretic versions (Harsanyi, modern expected-utility utilitarianism). Classical utilitarianism uses aggregate utility without expected-value formalism; the formal decision-theoretic version requires expected utility. The edge is defensible on the formal/decision-theoretic reading but not on the classical reading. The canonical SEP framing of utilitarianism would lead with utility/hedonic-calculus, not expected-value.
VERDICT: defensible
CONFIDENCE: medium
NOTES: A more canonical prereq for the "utilitarianism" node label would be a `utility` node (not present in the graph at this granularity), which is conceptually prior to expected-value. Acceptable as a formal-version prereq; closeout may consider tighter framing.

#### Finding E-27
EDGE: `expected_value` [service] → `social_contract_theory` [political]
SEP-ANCHORED REASONING: SEP entries on "Contractarianism" and "Social Contract Theory" foreground state-of-nature reasoning, consent, and political legitimacy. Game-theoretic / decision-theoretic treatments (Rawls's veil of ignorance reasoning, Gauthier's bargaining-based contractarianism) are 20th-century reconstructions, not the canonical framing. Classical social contract theorists (Hobbes, Locke, Rousseau) do not use expected-value reasoning. The pedagogical-prerequisite framing is weak: students of social contract theory can grasp the position fully without expected-value formalism.
VERDICT: weak
CONFIDENCE: medium
NOTES: Concurs with S-0081 gate finding (flagged at gate as questionable). Closeout may consider whether to retain (formal-game-theoretic reading), prune, or replace with a more proximate prereq.

### A3 — Service history terminators → philosophy (18 edges)

#### Finding E-28
EDGE: `aristotelian_four_causes` [service] → `causation` [metaphysics]
SEP-ANCHORED REASONING: SEP entry on "The Metaphysics of Causation" treats Hume, regularity theories, counterfactual theories (Lewis), manipulationist theories (Woodward), process theories (Salmon, Dowe). The four causes appear as historical preface, not as the canonical proximate prereq for the modern concept of causation. SEP entry on "Aristotle on Causality" treats the four causes in their own historical-philosophical right; modern causation theory is in dialogue with Hume's rejection of pre-modern causes, not in continuity with the four-cause taxonomy. The relation is historical-genealogical, not strict pedagogical prerequisite.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Mis-typed: historical-not-pedagogical. Per master-plan §"Structural reopen pre-flag", a candidate for retyping under `historical_influence` (PREDICATE_MANIFEST.md reserved-but-unused).

#### Finding E-29
EDGE: `aristotelian_four_causes` [service] → `essence_metaphysical` [metaphysics specialized]
SEP-ANCHORED REASONING: SEP entry on "Essential vs. Accidental Properties" treats modern essence metaphysics centrally via Kit Fine ("Essence and Modality", 1994), Lowe, and others. The Aristotelian formal cause is a historical antecedent, not the canonical proximate prereq for modern essence-metaphysics. Fine's project is in dialogue with the Aristotelian tradition but not strictly downstream of it.
VERDICT: historical
CONFIDENCE: medium
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-30
EDGE: `aristotelian_four_causes` [service] → `scientific_explanation` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Explanation" treats Hempel's DN-model, Kitcher's unification, Salmon's causal-mechanical, Woodward's manipulationist, and Strevens. The four-cause typology appears as pre-modern background that modern theories of scientific explanation define themselves against. Modern scientific explanation theory does not pedagogically presuppose the four-cause typology.
VERDICT: historical
CONFIDENCE: high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-31
EDGE: `aristotelian_four_causes` [service] → `humean_regularity_theory` [metaphysics]
SEP-ANCHORED REASONING: SEP entry on "Hume's Theory of Causation" frames the regularity theory via Hume's rejection of necessary connection, not directly via the four-cause taxonomy. The dialectical relationship to Aristotle is real but mediated by early-modern mechanism. Direction is defensibly historical (Hume in dialogue with Aristotelian background) but not strict pedagogical prereq.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-32
EDGE: `greek_atomism` [service] → `physicalism` [mind]
SEP-ANCHORED REASONING: SEP entry on "Physicalism" centrally treats 20th-century physicalist positions (Smart, Place, Lewis, Kim, Chalmers's anti-physicalist arguments). Greek atomism (Democritus, Leucippus, Epicurus) is not pedagogically prerequisite — modern physicalism is freestanding and developed in response to mind-body problem rather than in continuity with ancient atomism. The genealogical link is real but not the canonical proximate prereq.
VERDICT: historical
CONFIDENCE: high
NOTES: Concurs with S-0081 gate finding. Mis-typed: historical-not-pedagogical.

#### Finding E-33
EDGE: `greek_atomism` [service] → `reductionism_in_science` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Reduction" treats Nagel's bridge laws, Kim's functional reduction, and contemporary debates. Greek atomism is ancestral but not pedagogically required. Same shape as E-32.
VERDICT: historical
CONFIDENCE: high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-34
EDGE: `greek_atomism` [service] → `mereological_nihilism` [metaphysics specialized]
SEP-ANCHORED REASONING: SEP entry on "Mereological Nihilism" / "Mereology" treats contemporary positions (Unger, van Inwagen, Sider). The Greek atomists' doctrine of indivisible particles in void is not the technical mereological-simples doctrine of contemporary nihilism — the conceptual identification is loose (atomism makes empirical claims about physical decomposition; nihilism makes formal claims about composition). The relation is even weaker than typical history-terminator edges: not just historical but conceptually misaligned.
VERDICT: historical
CONFIDENCE: high
NOTES: Concurs with S-0081 gate finding. Mis-typed: historical-not-pedagogical, and possibly weak even as a historical influence (the conceptual identification is strained).

#### Finding E-35
EDGE: `scholasticism` [service] → `realism_about_universals` [metaphysics specialized]
SEP-ANCHORED REASONING: SEP entry on "The Medieval Problem of Universals" treats the scholastic dispute (realism / conceptualism / nominalism) historically. SEP entry on "Universals" treats also Plato, contemporary trope theory, Armstrong's a-posteriori realism. Modern realism about universals (Armstrong, Lewis) is freestanding and not pedagogically downstream of scholastic mastery. Historical genealogy, not pedagogical prerequisite.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-36
EDGE: `scholasticism` [service] → `divine_command_theory` [ethics metaethics+normative]
SEP-ANCHORED REASONING: SEP entry on "Divine Command Theory" surveys contemporary versions (Adams, Quinn) alongside the medieval Aquinas/Scotus/Ockham tradition. Modern DCT is intelligible without scholastic apprenticeship; the medieval context is enriching but not strict prereq. Same shape as other A3 edges.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Concurs with S-0081 gate finding. Mis-typed: historical-not-pedagogical.

#### Finding E-37
EDGE: `renaissance_mechanism` [service] → `substance_dualism` [mind]
SEP-ANCHORED REASONING: SEP entry on "Dualism" / "René Descartes" centrally treats Descartes as the canonical substance dualist. The Renaissance mechanism context is genuinely load-bearing for understanding why Descartes posited a non-mechanical mind (the historical motivation is the mechanist physics of Galileo + Descartes himself). This A3 edge is closer to a pedagogical prereq than other history-terminator edges because the dialectic between mechanism and dualism is internal to the position, not just background. Defensible — closer call than the other A3 edges.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Closer call. Closeout may consider this a borderline case — historical influence is real but pedagogical-prerequisite framing is more defensible than for the other history terminators.

#### Finding E-38
EDGE: `renaissance_mechanism` [service] → `scientific_theory` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Theories" surveys the syntactic view (Carnap, logical empiricists), the semantic view (Suppes, Suppe, van Fraassen), and pragmatic views. The modern conception of theory does not directly inherit from Galileo's mechanism; the connection is genealogical via the gradual development of mathematical-natural-philosophy into modern science. Historical antecedent, not pedagogical prereq.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-39
EDGE: `renaissance_mechanism` [service] → `scientific_method` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Method" surveys induction (Mill, Whewell), hypothetico-deductivism, falsificationism, IBE, Bayesianism. Modern philosophy of method does not pedagogically require mastery of Renaissance mechanism. Historical antecedent.
VERDICT: historical
CONFIDENCE: medium-high
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-40
EDGE: `vienna_circle_logical_positivism` [service] → `verificationism` [language]
SEP-ANCHORED REASONING: SEP entry on "The Vienna Circle" treats the Circle as the canonical site at which verificationism was elevated to a doctrine of meaningfulness. Verificationism, taught alone, is hard to motivate without the Vienna Circle context (Schlick, Carnap, Ayer's exposition). The connection is closer than typical history-terminator edges: Vienna Circle is the canonical historical-philosophical context for verificationism, not just an antecedent.
VERDICT: sound
CONFIDENCE: medium-high
NOTES: Among the closest A3 cases. Pedagogical and historical content fuse here — the position is defined by the school.

#### Finding E-41
EDGE: `vienna_circle_logical_positivism` [service] → `falsificationism` [science]
SEP-ANCHORED REASONING: SEP entry on "Karl Popper" / "Karl Popper's Philosophy of Science" treats falsificationism as developed in dialogue with the Vienna Circle's verificationism. The dialectical relationship is real, but you can teach falsificationism's core thesis (a hypothesis is scientific iff falsifiable) without prior Vienna Circle apprenticeship — verificationism can be introduced inline as the contrast position. Defensible on dialogue framing, historical otherwise.
VERDICT: historical
CONFIDENCE: medium
NOTES: Mis-typed: historical-not-pedagogical (or defensible at best).

#### Finding E-42
EDGE: `vienna_circle_logical_positivism` [service] → `demarcation_problem` [science]
SEP-ANCHORED REASONING: SEP entry on "Science and Pseudo-Science" treats the demarcation problem as a topic with multiple historical and contemporary contributions (Vienna Circle, Popper, Lakatos, Laudan's "demise of demarcation"). The demarcation problem can be addressed without first studying Vienna Circle. Historical antecedent.
VERDICT: historical
CONFIDENCE: medium
NOTES: Mis-typed: historical-not-pedagogical.

#### Finding E-43
EDGE: `vienna_circle_logical_positivism` [service] → `tarskis_t_schema` [language]
SEP-ANCHORED REASONING: SEP entry on "Tarski's Truth Definitions" introduces Convention T directly via the formal-semantic apparatus. Tarski's T-schema is a logical-semantic technical contribution, intelligible without Vienna Circle context. The connection between Tarski and the Vienna Circle is sociological (Tarski lectured at the Circle's symposia; Carnap adopted Tarskian semantics) more than conceptual. The pedagogical-prerequisite framing is weak.
VERDICT: historical
CONFIDENCE: high
NOTES: Concurs with S-0081 gate finding. Mis-typed: historical-not-pedagogical, and arguably weak even as historical influence (sociological proximity, not conceptual genealogy).

#### Finding E-44
EDGE: `vienna_circle_logical_positivism` [service] → `deductive_nomological_model` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Explanation" treats Hempel's DN-model directly via the schema (E ≡ explanans-derivability of explanandum from laws + initial conditions). Hempel was logical-empiricist adjacent (not strictly Vienna Circle but Berlin Circle / Reichenbach milieu). The DN-model can be taught directly via the schema without prior logical-positivism context.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Defensibly historical (DN-model emerged from logical-empiricist program); pedagogical-prerequisite framing strained.

#### Finding E-45
EDGE: `vienna_circle_logical_positivism` [service] → `behaviorism_logical` [mind]
SEP-ANCHORED REASONING: SEP entry on "Behaviorism" treats logical / philosophical behaviorism (Carnap, Hempel, Ryle) as descending directly from the logical-empiricist anti-mentalist program. The pedagogical-prerequisite framing is closer here than for other Vienna-Circle-as-source edges: the position is defined as a logical-empiricist application to philosophy of mind. Sound to defensible.
VERDICT: sound
CONFIDENCE: medium-high
NOTES: Among the closer A3 cases.

### B — Within-philosophy cross-subdomain bridges (26 edges)

#### Finding E-46
EDGE: `belief` [epistemology] → `propositional_attitude` [mind]
SEP-ANCHORED REASONING: SEP entry on "Propositional Attitude Reports" / "Belief" treats belief as the paradigm propositional attitude. Pedagogical direction sound: students grasp the folk-psychological belief concept first (everyone has it pre-theoretically), then encounter philosophy-of-mind treatment of belief as an attitude toward a propositional content.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-47
EDGE: `epistemic_justification` [epistemology] → `propositional_attitude` [mind]
SEP-ANCHORED REASONING: SEP entry on "Epistemic Justification" / "Justification, Epistemic" treats justification as a property of propositional attitudes (paradigmatically belief). The migration's own rationale states "the bearer of justification is a propositional attitude; justification is a property of attitudes." Properties presuppose bearers — to apply justification to attitudes, you need the attitude concept first. The edge claims propositional_attitude depends on epistemic_justification, which inverts the property-of-bearer relation.
VERDICT: reversed
CONFIDENCE: high
NOTES: The pedagogical direction matches `propositional_attitude → epistemic_justification`, not the authored direction. The migration's own rationale supports the reversed reading.

#### Finding E-48
EDGE: `truth` [epistemology] → `tarskis_t_schema` [language]
SEP-ANCHORED REASONING: SEP entry on "Tarski's Truth Definitions" frames the T-schema ("'S' is true iff S") as a formal characterization of the truth predicate. To grasp the formalization, the prior ordinary-language concept of truth is required.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-49
EDGE: `truth` [epistemology] → `truth_conditional_semantics` [language]
SEP-ANCHORED REASONING: SEP entry on "Truth-Conditional Theories of Meaning" treats the position as identifying meaning with truth-conditions. The truth concept is the foundational primitive. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-50
EDGE: `problem_of_induction` [epistemology specialized] → `bayesianism_confirmation` [science]
SEP-ANCHORED REASONING: SEP entry on "The Problem of Induction" / "Bayesian Epistemology" treats Bayesian confirmation as the dominant contemporary response to Hume's problem. The dialectic is real and the response framing is pedagogically standard.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-51
EDGE: `problem_of_induction` [epistemology specialized] → `falsificationism` [science]
SEP-ANCHORED REASONING: SEP entry on "Karl Popper" treats falsificationism as Popper's response to Hume's problem of induction (replace inductive support with corroboration through failed falsification). The connection is canonical and pedagogically standard.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-52
EDGE: `problem_of_induction` [epistemology specialized] → `scientific_method` [science]
SEP-ANCHORED REASONING: SEP entry on "Scientific Method" surveys positions on induction (Mill, Whewell, modern Bayesian) — every account of method must take a stance on induction. The framing is genuine but slightly broader: scientific method as a topic encompasses much more than induction (experimental design, theory choice, IBE, etc.).
VERDICT: defensible
CONFIDENCE: medium-high
NOTES: Defensibly sound. Scope of the scientific_method node may include topics not directly downstream of problem_of_induction.

#### Finding E-53
EDGE: `evidence` [epistemology] → `bayesianism_confirmation` [science]
SEP-ANCHORED REASONING: SEP entry on "Evidence" / "Bayes' Theorem" treats Bayesian confirmation as a theory of how evidence supports hypotheses. The evidence concept is genuinely the prerequisite scaffolding.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-54
EDGE: `formal_epistemology` [epistemology specialized] → `modal_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Modal Logic" treats modal logic as the formal study of necessity, possibility, and related operators — developed for metaphysics of necessity, deontic, temporal, and (later) epistemic applications. Modal logic is the foundational formal apparatus; epistemic logic is one application that formal epistemology uses. The pedagogical direction is `modal_logic → formal_epistemology` (formal epistemology USES modal logic as a tool), not the authored direction.
VERDICT: reversed
CONFIDENCE: medium-high
NOTES: A clear reversal. Formal epistemology applies modal-logic frameworks (epistemic logic, doxastic logic); modal logic is foundational and prior. The authored direction would imply that modal logic depends on formal epistemology, which is false in pedagogical practice.

#### Finding E-55
EDGE: `formal_epistemology` [epistemology specialized] → `kripke_semantics` [logic]
SEP-ANCHORED REASONING: Same shape as E-54. Kripke semantics is the model-theoretic framework for modal logic, foundational and prior to its epistemic-logic applications.
VERDICT: reversed
CONFIDENCE: medium-high
NOTES: Companion to E-54. Direction should be `kripke_semantics → formal_epistemology` (epistemic logic is an application of Kripke-style model theory).

#### Finding E-56
EDGE: `epistemic_closure` [epistemology] → `modal_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Epistemic Closure" treats closure principles informally (if S knows P and S knows P→Q, then S knows Q) and notes their formal study within epistemic modal logic (the K axiom). Modal logic exists independently of epistemic-closure considerations (used for metaphysics of necessity, deontic, temporal). The pedagogical direction would be `modal_logic → epistemic_closure-as-axiom-in-epistemic-logic`, not the authored direction. Even informally, closure is a topic within epistemology; modal logic is the formal apparatus that closure gets formalized in, not a downstream consumer.
VERDICT: reversed
CONFIDENCE: medium
NOTES: Direction should be `modal_logic → epistemic_closure` if the connection is the formalization-in-K-axiom; alternatively the edge is weak (no strict prereq either way; informal closure can be taught without modal logic).

#### Finding E-57
EDGE: `causation` [metaphysics] → `mental_causation` [mind]
SEP-ANCHORED REASONING: SEP entry on "Mental Causation" frames the topic as the question of how mental states can be causes of physical effects, presupposing the general metaphysics of causation. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-58
EDGE: `property` [metaphysics] → `property_dualism` [mind]
SEP-ANCHORED REASONING: SEP entry on "Dualism" (property-dualism section) frames property dualism as the view that mental and physical properties are distinct kinds of properties of a single substance, presupposing the metaphysical category of property. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-59
EDGE: `substance` [metaphysics] → `substance_dualism` [mind]
SEP-ANCHORED REASONING: SEP entry on "Dualism" / "Substance" frames Cartesian substance dualism as positing mind and body as distinct substances, presupposing the metaphysical category of substance. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-60
EDGE: `modality` [metaphysics specialized] → `modal_logic` [logic]
SEP-ANCHORED REASONING: SEP entry on "Modal Logic" treats modal logic as the formal study of modal notions (necessity, possibility, contingency). The philosophical concept of modality grounds the formal study. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-61
EDGE: `modality` [metaphysics specialized] → `kripke_semantics` [logic]
SEP-ANCHORED REASONING: SEP entry on "Possible Worlds" / "Kripke Semantics" frames Kripke semantics as the model-theoretic formalization of modality (necessity = truth-at-all-accessible-worlds). The philosophical modality concept grounds the formalization. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-62
EDGE: `possible_worlds` [metaphysics specialized] → `kripke_semantics` [logic]
SEP-ANCHORED REASONING: Kripke semantics IS possible-worlds semantics — the worlds in the model are possible worlds (modulo ontological interpretation). The philosophical possible-worlds concept is genuinely the scaffolding. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-63
EDGE: `propositional_attitude` [mind] → `proposition` [language]
SEP-ANCHORED REASONING: SEP entry on "Propositions" treats propositions as content-bearers — abstract objects that are the contents of attitudes (and the meanings of declarative sentences). SEP entry on "Propositional Attitude Reports" frames propositional attitudes as attitudes TOWARD propositions — propositions are the content, attitudes are the relations to that content. To understand propositional attitudes, the proposition concept is conceptually prior. The migration's own rationale ("the mind concept references the language-philosophy concept of proposition as content-bearer") supports the reversed reading.
VERDICT: reversed
CONFIDENCE: high
NOTES: Concurs with S-0081 gate finding (the gate flagged this edge as reversed). Direction should be `proposition → propositional_attitude`.

#### Finding E-64
EDGE: `intentionality` [mind] → `meaning` [language]
SEP-ANCHORED REASONING: SEP entries on "Intentionality" (Brentano's mark of the mental) and "Meaning" treat the two concepts as connected via the broad picture that intentional content IS, on standard treatments, semantic content. Neither is strictly prereq for the other: intentionality applies to mental states; meaning applies to linguistic items. Some accounts unify them (Grice, Fodor); others keep them separate. The pedagogical-prerequisite framing is weak — meaning can be taught semantically without prior intentionality concept.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Defensibly sound on unifying-account framings (intentionality is the broader category); defensible-but-weak on separate-account framings.

#### Finding E-65
EDGE: `causal_theory_of_mental_content` [mind] → `causal_theory_of_reference` [language]
SEP-ANCHORED REASONING: SEP entries on "Causal Theories of Mental Content" (Fodor, Dretske, Stampe — 1980s) and "Reference, Causal Theory of" (Kripke 1972, Putnam, Donnellan — 1970s) treat the parallel theories. Genealogically, the language-philosophy theory predates the mind-philosophy theory and inspired it: Fodor's account is explicitly modeled on Kripke-Putnam reference theory. The migration's own rationale ("the mind theory is a paradigm application of the language theory") supports the reverse direction. The authored edge inverts genealogy.
VERDICT: reversed
CONFIDENCE: medium-high
NOTES: Direction should be `causal_theory_of_reference → causal_theory_of_mental_content` per the canonical genealogy (Kripke-Putnam → Fodor-Dretske).

#### Finding E-66
EDGE: `multiple_realizability` [mind] → `multiple_realizability_in_science` [science]
SEP-ANCHORED REASONING: SEP entry on "Multiple Realizability" centrally treats Putnam's argument (mental types like pain are realizable in distinct physical types — humans, octopuses, hypothetical aliens) and its generalization to special-science kinds (Fodor 1974). The philosophy-of-mind concept is the original; the philosophy-of-science generalization is downstream. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-67
EDGE: `physicalism` [mind] → `reductionism_in_science` [science]
SEP-ANCHORED REASONING: SEP entries on "Physicalism" and "Scientific Reduction" treat the two positions independently. Type-identity physicalism (the type-identity formulation) is reductionist; non-reductive physicalism is explicitly anti-reductive. Reductionism in science (cross-level identification of higher-level kinds with lower-level mechanisms) is broader and not strictly downstream of philosophy-of-mind physicalism — Nagel's classical reductionism predates and exists independently. Both are positions about explanation/identification at different levels of generality; neither is canonically prereq to the other.
VERDICT: weak
CONFIDENCE: medium-high
NOTES: Concurs with S-0081 gate finding (flagged at gate as weak/questionable). Closeout may consider whether to retain (a specific-position-supports-broader-methodology framing), prune, or reroute.

#### Finding E-68
EDGE: `material_conditional` [logic] → `paradox_of_the_ravens` [science]
SEP-ANCHORED REASONING: SEP entry on "Confirmation" / "Paradox of the Ravens" treats Hempel's paradox as arising from formalizing the universal generalization "all ravens are black" as ∀x(Rx → Bx) where → is the material conditional. The paradox depends on the truth-table behavior of the material conditional (a non-raven non-black object trivially satisfies ¬Rx, hence Rx → Bx). Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

#### Finding E-69
EDGE: `motivational_internalism` [ethics metaethics+normative] → `propositional_attitude` [mind]
SEP-ANCHORED REASONING: SEP entry on "Moral Motivation" / "Internalism vs. Externalism in Ethics" treats motivational internalism as the thesis that moral judgments intrinsically motivate (typically formulated as: necessarily, if S judges that φ-ing is right, then S has some motivation to φ). The thesis presupposes the philosophy-of-mind concept of propositional attitudes (judgments are PAs; motivation is a feature of certain PAs). PA is the broader category; motivational_internalism is a specific position that uses PA. The authored direction inverts the position-uses-category relation.
VERDICT: reversed
CONFIDENCE: high
NOTES: Direction should be `propositional_attitude → motivational_internalism` (PA is the broader concept that the position uses).

#### Finding E-70
EDGE: `justice` [political] → `morality` [ethics]
SEP-ANCHORED REASONING: SEP entry on "Justice" treats political justice as a domain-specific application of broader moral concepts (rightness, fairness, desert, equality). SEP entry on "Morality" / "Definition of Morality" treats morality as the broader normative framework. The migration's own rationale ("the political concept presupposes the broader moral concepts") supports the reverse direction. The authored edge inverts the part-whole / specific-general relation.
VERDICT: reversed
CONFIDENCE: high
NOTES: Direction should be `morality → justice` (morality is broader; political justice is a specific application).

#### Finding E-71
EDGE: `social_contract_theory` [political] → `contractualism` [ethics metaethics+normative]
SEP-ANCHORED REASONING: SEP entries on "Contractualism" (Scanlon) and "Contractarianism" (Gauthier, the social-contract reconstruction tradition) treat contractualist ethical theories as generalizing the social-contract structure from political-legitimacy questions to general ethical questions. The pedagogical direction is defensible — students often encounter Hobbes/Locke/Rousseau before Scanlon — but the connection is more analogical than strict prerequisite (Scanlon's "What We Owe to Each Other" can be motivated independently).
VERDICT: defensible
CONFIDENCE: medium
NOTES: Defensibly sound on the structural-generalization framing; defensible-but-weaker on strict-prereq framing.

## Sampled-node candidate findings

N/A — cross-bridges have no node sample. Per master plan §"Sample-size policy" AUDIT-CB row, node coverage for the source/target endpoints of these 71 edges is the responsibility of the per-subdomain audit tasks (AUDIT-EPI, AUDIT-MET, AUDIT-MIN, AUDIT-LAN, AUDIT-LOG, AUDIT-SCI, AUDIT-POL, AUDIT-AES, AUDIT-ETH, AUDIT-SVC, AUDIT-HT). The "service" subdomain endpoints concentrated in groupings A1/A2/A3 will be sampled by AUDIT-SVC.

## Cross-cutting observations

Treated sparingly per master-plan §T2-D — aggregate pattern recognition is the closeout's synthesis surface, not the evidence session's. Three observations the closeout will need:

**1. Aggregate defect rate exceeds the gate's projection.** Verdict tally across the 71-edge full census:

| Verdict | Count | % of 71 |
|---|---|---|
| sound | 38 | 53.5% |
| defensible | 8 | 11.3% |
| weak | 3 | 4.2% |
| reversed | 8 | 11.3% |
| historical (mis-typed: historical-not-pedagogical) | 14 | 19.7% |
| thematic / other | 0 | 0% |

Substantive defects (reversed + weak + historical) total **25/71 = 35.2%**. Adding `defensible` (legitimate but non-canonical framings worth closeout review) brings the non-`sound` rate to **33/71 = 46.5%**. The S-0081 gate's 15-edge sample produced 8 substantive findings (53.3%). The full census's 35.2% substantive-defect rate is lower than the sample but higher than the >15% threshold the master plan set for cross-bridge defect-rate-triggers-density-expansion. The S-0081 gate's recommendation of 35% per-subdomain density (vs the 25–30% baseline) is calibrated correctly by this evidence.

**2. Historical-not-pedagogical density meets the ADR-warranting threshold.** 14 of 71 cross-bridges (19.7%) are historical-not-pedagogical. The master plan's pre-flagged threshold (≥10 of 71 historical-not-pedagogical → ADR memo recommended) is met. The candidates cluster in the A3 grouping (history terminators) almost entirely: 14 of the 18 A3 edges are historical-not-pedagogical. The 4 A3 edges that are NOT historical-not-pedagogical are E-37 (renaissance_mechanism → substance_dualism, defensible), E-40 (vienna_circle → verificationism, sound), E-44 (vienna_circle → deductive_nomological_model, defensible), and E-45 (vienna_circle → behaviorism_logical, sound). The closeout's expected disposition (per master-plan §"Structural reopen pre-flag") is activation of the reserved-but-unused `historical_influence` predicate for the 14 historical edges; the audit finding supports that disposition.

**3. Reversal cluster in cross-domain bridges between epistemology / mind / language / ethics.** The 8 reversed edges share a coherent pattern that suggests a systematic authoring-direction bug, not a series of independent slips. The pattern: **when a cross-domain edge connects a specific position / sub-concept (X) to its broader / parent category (Y), the edge gets authored as `X → Y` instead of `Y → X`.** Specifically:

- E-47: `epistemic_justification → propositional_attitude` (justification applies to PAs; PA is broader) — reversed.
- E-54: `formal_epistemology → modal_logic` (formal epistemology uses modal logic as a tool; modal logic is foundational) — reversed.
- E-55: `formal_epistemology → kripke_semantics` (companion to E-54) — reversed.
- E-56: `epistemic_closure → modal_logic` (closure is a principle formalized within epistemic modal logic; modal logic is foundational apparatus) — reversed.
- E-63: `propositional_attitude → proposition` (PA is an attitude TOWARD a proposition; proposition is the content) — reversed; concurs with S-0081 gate.
- E-65: `causal_theory_of_mental_content → causal_theory_of_reference` (Kripke-Putnam reference theory predates and inspired Fodor-Dretske mental content theory) — reversed.
- E-69: `motivational_internalism → propositional_attitude` (MI is a position about a kind of PA; PA is broader) — reversed.
- E-70: `justice → morality` (political justice is a domain-specific application of broader moral concepts; morality is broader) — reversed.

Five of the eight reversals (E-47, E-63, E-65, E-69, E-70) have the migration's own pedagogical-warrant prose explicitly arguing the opposite direction from what was authored — a strong signal that the reversal is a mechanical authoring slip (perhaps a "source-target field swap during VALUES list editing") rather than a deliberate pedagogical claim. Three of the eight (E-54, E-55, E-56) cluster in the formal-epistemology + epistemic-closure → modal-logic direction, which is the same shape under a different framing (specific-application → general-formal-apparatus, encoded as application-grounds-apparatus instead of apparatus-grounds-application). The closeout's expected disposition is to flip direction on these eight edges (or retire and re-author with corrected direction); a validator soft-warn `cross_bridge_pedagogical_direction_inconsistent_with_summary` is a candidate for new audit-system input — flag where source's summary and target's summary together imply the opposite direction from the authored edge.

**4. Defects are not uniformly distributed across the four sub-groupings.** Per-grouping verdict breakdown:

| Grouping | Total | sound | defensible | weak | reversed | historical | non-sound % |
|---|---|---|---|---|---|---|---|
| A1 (formal-logic primitives → philosophy) | 15 | 14 | 0 | 1 | 0 | 0 | 6.7% |
| A2 (math prerequisites → philosophy) | 12 | 9 | 2 | 1 | 0 | 0 | 25.0% |
| A3 (history terminators → philosophy) | 18 | 2 | 2 | 0 | 0 | 14 | 88.9% |
| B (within-philosophy cross-subdomain) | 26 | 13 | 4 | 1 | 8 | 0 | 50.0% |

A1 (formal-logic primitives) is the cleanest grouping (94% sound) — the formal-logic primitives ground their downstream philosophical-logic concepts cleanly. A2 (math prerequisites) is mostly sound with edge cases at the edges of formal-philosophical reach (E-26 utilitarianism-via-decision-theory, E-27 social-contract-via-decision-theory). A3 is dominated by the historical-not-pedagogical pattern (14 of 18). B carries the reversal cluster (8 of the 8 reversals are in this grouping). The closeout's audit-system-input synthesis can use this distribution to calibrate which subdomain audits should expect more defects (those drawing on B's source endpoints — epistemology, mind, language, ethics, metaphysics — should expect higher defect rates than service-grounded subdomains).

**5. The empty-evidence-text finding (master-plan §"Audit-system-input proposals" item 1) is confirmed graph-wide.** All 71 cross-bridges have `evidence` field NULL (the migration's INSERT statement does not populate it). Per master-plan §T2-E, this is not flagged per-edge — it's a known graph-wide gap pre-listed for audit-system-input. The cross-bridge full census confirms the gate's finding without modification.

## SEP citations consulted

The SEP entries cited across the 71 findings are listed below (deduplicated; consulted from training-knowledge per ADR 0011 / ADR 0046 — INTERPRETED-only posture; no quoted prose extracted). This section is informational; its job is to support closeout spot-check on the verdicts, not to be exhaustive.

- "Classical Logic"
- "Many-Valued Logic"
- "Dialetheism"
- "Fuzzy Logic"
- "Paraconsistent Logic"
- "Epistemic Justification" / "Justification, Epistemic"
- "Logical Consequence"
- "Formal Epistemology"
- "Quantifiers and Quantification"
- "Karl Popper" / "Karl Popper's Philosophy of Science"
- "Proof Theory"
- "The Analysis of Knowledge"
- "Russell's Paradox" / "Set Theory"
- "Possible Worlds"
- "Modal Logic"
- "Possible Worlds Semantics"
- "Bayesian Epistemology"
- "Bayes' Theorem"
- "Imaging and Conditionalization"
- "Confirmation" / "Confirmation Theory"
- "Dutch Book Arguments"
- "Consequentialism" / "The History of Utilitarianism"
- "Contractarianism" / "Social Contract Theory"
- "The Metaphysics of Causation"
- "Aristotle on Causality"
- "Essential vs. Accidental Properties"
- "Aristotle's Metaphysics"
- "Scientific Explanation"
- "Hume's Theory of Causation"
- "Physicalism"
- "Ancient Atomism"
- "Scientific Reduction"
- "Mereological Nihilism" / "Mereology"
- "The Medieval Problem of Universals" / "Universals"
- "Divine Command Theory"
- "Dualism" / "René Descartes"
- "Scientific Theories"
- "Scientific Method"
- "The Vienna Circle"
- "Science and Pseudo-Science"
- "Tarski's Truth Definitions"
- "Behaviorism"
- "Propositional Attitude Reports"
- "Belief"
- "Truth-Conditional Theories of Meaning"
- "The Problem of Induction"
- "Evidence"
- "Mental Causation"
- "Substance"
- "Propositions"
- "Intentionality" / "Meaning"
- "Causal Theories of Mental Content"
- "Reference, Causal Theory of"
- "Multiple Realizability"
- "Paradox of the Ravens"
- "Moral Motivation" / "Internalism vs. Externalism in Ethics"
- "Justice"
- "Morality" / "Definition of Morality"
- "Contractualism"
- "Epistemic Closure"
- "Epistemic Logic"
