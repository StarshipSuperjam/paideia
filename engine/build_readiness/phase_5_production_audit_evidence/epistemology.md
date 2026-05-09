# Phase 5 production audit evidence — epistemology

> Authored by S-0105 (routine session) per T-PHASE-5-AUDIT task `AUDIT-EPI`.
> SEP-anchored review per [`engine/build_readiness/phase_5_production_audit.md`](../phase_5_production_audit.md).
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: epistemology (within-domain edges; cross-bridges to other philosophy subdomains and to service-domain primitives are AUDIT-CB scope, not duplicated here)
- Edge population: 72 within-epistemology edges (34 in `0011_seed_epistemology_part1.sql` foundational + 38 in `0016_seed_epistemology_part1.sql` specialized; matches master-plan figure)
- Edge sample size: **25** (35% density per master-plan §"Sample-size policy" AUDIT-EPI row)
- Sample density: **34.7%** (25/72)
- Sample selection: deterministic md5(seed='AUDIT-EPI' || source_id || '|' || target_id) ordering across the 72-edge population, take first 25. Inputs sourced from the two seed migrations (live-DB read denied in routine mode per ADR 0055; the migrations are the canonical authoring record, applied verbatim to production).
- Node sample size: **12** (~12 edge-anchored per master-plan §"Sample-size policy")
- Node sample selection: union of source/target endpoints across the 25 sampled edges (35 unique nodes), then md5(seed='AUDIT-EPI' || node_id) ordering, take first 12
- Generation date: 2026-05-09

## Sampled-edge candidate findings

### Finding E-1
EDGE: `intellectual_virtue` [epistemology] → `virtue_responsibilism` [epistemology]
   edge_type = pedagogical_prerequisite, weight/confidence/evidence per migration (evidence text null graph-wide — known finding pre-listed in master plan §T2-E)
SEP-ANCHORED REASONING: SEP entry "Virtue Epistemology" presents virtue responsibilism (Zagzebski, Code) as the branch that takes intellectual virtues as character traits the believer cultivates (open-mindedness, intellectual humility, conscientiousness). The position is defined precisely by treating intellectual virtues as the load-bearing analytic primitive on the character-trait reading. Pedagogical direction sound: students need the prior concept of intellectual virtue (the species the position centers) before they can engage virtue responsibilism as a thesis ABOUT how those virtues figure in justification or knowledge.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-2
EDGE: `expertise` [epistemology] → `epistemic_dependence` [epistemology]
SEP-ANCHORED REASONING: SEP entries "Social Epistemology" and "Epistemic Aspects of the Division of Cognitive Labor" frame epistemic dependence (Hardwig 1985) as the broader structural condition: a believer's justified belief depends on others' epistemic states. Expertise is one mode of that dependence (the asymmetric layperson-to-expert form), but not the only one — dependence on testimony from non-experts and on community-level practices are also forms. SEP would more naturally treat dependence as the framework concept and expertise as a topic-within. The migration's direction (expertise → dependence) treats expertise as the entry point from which the broader phenomenon is grasped. Defensible on textbook framings that introduce the layperson-trusts-expert case first, then generalize, but the canonical SEP framing runs the other way.
VERDICT: defensible
CONFIDENCE: medium
NOTES: A more canonical proximate prereq for `expertise` would be `social_epistemology` (already in graph: social_epistemology → expertise). The expertise → dependence edge is a within-cluster bridge that could be removed without loss of structural coverage; closeout may consider whether to keep, prune, or reverse.

### Finding E-3
EDGE: `epistemic_justification` [epistemology] → `evidentialism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Evidentialism" defines the position (Conee, Feldman 1985) as the thesis that justification is fully determined by the believer's evidence. The thesis IS a thesis about justification; you cannot grasp evidentialism's content without the prior concept of justification. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-4
EDGE: `epistemic_justification` [epistemology] → `infinitism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Infinitism in Epistemology" presents Klein's position as a structural answer to the regress problem about justified belief. The third option in the regress trilemma (regress, circle, terminate) — and the choice of "regress" — only makes sense once justification and the regress problem are in view. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-5
EDGE: `belief` [epistemology] → `certainty` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Certainty" frames epistemic certainty as a maximally strong form of belief — belief held with no possibility of doubt, or maximum credence. Either reading presupposes belief as the more general doxastic state. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-6
EDGE: `knowledge` [epistemology] → `knowledge_first_epistemology` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Knowledge First Epistemology" / Williamson's `Knowledge and Its Limits` (2000) frames the program as an inversion of the analysis-of-knowledge tradition: take knowledge as primitive and define belief, evidence, justification derivatively. The program's content cannot be stated except by reference to the concept of knowledge it claims as primitive — so the prior concept of knowledge IS required to engage the program even when (especially when) the program rejects further analysis of it. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-7
EDGE: `knowledge_how` [epistemology] → `knowledge` [epistemology]
SEP-ANCHORED REASONING: SEP entries "Knowledge How" and "The Analysis of Knowledge" treat the knowledge-that / knowledge-how distinction (Ryle 1949; Stanley & Williamson 2001) as a content split within the broader concept of knowledge. The migration's `knowledge` summary explicitly defends species-before-genus pedagogy ("the species precede the genus: students grasp knowing-that and knowing-how as concrete cases before abstracting to knowledge-as-such"). SEP's typical entry shape teaches knowledge analysis (knowledge-that) first, then introduces knowledge-how as a contrast; the strict prereq ordering is not load-bearing in SEP's coverage. The direction in the graph is sound on the migration's stated species-genus pedagogy and is consistent with the parallel `propositional_knowledge → knowledge` edge (also in graph).
VERDICT: sound
CONFIDENCE: medium
NOTES: Direction is internally consistent (both species → genus). Closeout may consider whether the species-genus pattern produces a small node-cluster reachability oddity (knowledge requires knowing about both knowledge-how AND propositional-knowledge) but the pattern is defensible pedagogy.

### Finding E-8
EDGE: `reliabilism` [epistemology] → `generality_problem` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Reliabilist Epistemology" presents the generality problem (Conee, Feldman 1998) as reliabilism's structural objection: any belief is the output of indefinitely many processes at different levels of generality. The objection is intelligible only relative to its target — students must have reliabilism in view before the generality complaint registers as a problem. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-9
EDGE: `epistemic_justification` [epistemology] → `foundationalism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Foundationalist Theories of Epistemic Justification" frames foundationalism as one structural answer to the regress problem about justification. To grasp the position, students need the prior concept of justification and the regress problem it addresses. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-10
EDGE: `evidence` [epistemology] → `epistemic_justification` [epistemology]
SEP-ANCHORED REASONING: SEP entries "Epistemic Justification" and "Evidence" treat evidence as a foundational input to justification on the dominant analyses (evidentialism makes evidence-fit constitutive; reliabilism treats evidence as one reliable input among others; foundationalism treats experiential evidence as basic). Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-11
EDGE: `reliabilism` [epistemology] → `virtue_reliabilism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Virtue Epistemology" presents virtue reliabilism (Sosa) as a refinement of process reliabilism: reliable cognitive competence (intellectual virtue) replaces reliable cognitive process. The refinement is intelligible only relative to its base (reliabilism's reliable-process framework). Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-12
EDGE: `propositional_knowledge` [epistemology] → `understanding` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Understanding" (Pritchard, Kvanvig, Zagzebski) frames understanding by contrast with propositional knowledge: students who have memorized facts differ from students who grasp how those facts cohere. The contrast IS the standard pedagogical introduction to understanding-as-distinct-from-knowledge; you need the contrast class first. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-13
EDGE: `problem_of_induction` [epistemology] → `pyrrhonian_skepticism` [epistemology]
SEP-ANCHORED REASONING: SEP entries "Skepticism", "Ancient Skepticism", and "The Problem of Induction" place Pyrrhonism as a millennia-older tradition (Pyrrho, Sextus Empiricus) than Hume's problem of induction. The conceptual ordering in SEP is roughly Pyrrhonist-tradition → modern-skepticism (the latter including induction-skepticism and Cartesian skepticism). Pyrrhonism's structure (the ten modes, the Agrippan trilemma, epoché, ataraxia) does NOT depend on the problem of induction; the problem of induction is one modern instance of the broader Pyrrhonist suspension-style argument. The migration's grouping comment ("induction motivates Pyrrhonism") inverts the canonical SEP ordering: induction is plausibly motivated BY Pyrrhonist-style suspension reasoning, not the other way.
VERDICT: reversed
CONFIDENCE: medium
NOTES: A more canonical direction would be `pyrrhonian_skepticism → problem_of_induction` (Pyrrhonist tradition prior; Hume's problem one modern instance). Alternative reading: weak — the most proximate prereq for Pyrrhonism in the graph is `skepticism_epistemic` (already in graph: skepticism_epistemic → pyrrhonian_skepticism); a long-distance shortcut from problem_of_induction adds little. Closeout may consider whether this is a direction reversal or a weak/redundant edge.

### Finding E-14
EDGE: `justified_true_belief` [epistemology] → `gettier_problem` [epistemology]
SEP-ANCHORED REASONING: SEP entry "The Analysis of Knowledge" presents Gettier's 1963 counterexamples as targeted at the JTB analysis: cases where justification, truth, and belief all hold but knowledge is intuitively absent. The counterexamples are intelligible only relative to the analysis they undermine. Pedagogical direction sound — JTB must be in view before Gettier registers.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-15
EDGE: `knowledge` [epistemology] → `epistemic_closure` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Epistemic Closure Principles" frames closure as a principle ABOUT knowledge: if S knows p, and S knows that p entails q, then S knows q (or some restricted variant). The principle is stated in terms of the concept of knowledge; the prior concept is required to articulate the principle at all. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-16
EDGE: `social_epistemology` [epistemology] → `expertise` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Social Epistemology" treats expertise (Goldman 2001 "Experts: Which Ones Should You Trust?") as one canonical topic within the field's scope. The genus-to-species ordering is the standard textbook approach: introduce the framework, then study its topics. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-17
EDGE: `tracking_theory_of_knowledge` [epistemology] → `safety_condition` [epistemology]
SEP-ANCHORED REASONING: SEP entries "The Analysis of Knowledge" and "Modal Epistemology" present safety (Sosa 1999, Williamson 2000) as a contemporary refinement of Nozickean tracking: replace sensitivity (would-not-believe-p-if-false) with safety (could-not-easily-have-believed-p-falsely) to preserve closure. The refinement is intelligible only against tracking as its starting point. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-18
EDGE: `epistemic_justification` [epistemology] → `externalism_epistemic` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Internalist vs. Externalist Conceptions of Epistemic Justification" frames externalism as a structural thesis about what factors determine justification (factors outside the believer's reflective access). The thesis is a thesis about justification; the prior concept is required. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-19
EDGE: `belief` [epistemology] → `epistemic_justification` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Epistemic Justification" treats justification as a property OF beliefs — the third clause of the JTB analysis applies to beliefs. Without the concept of belief, the very target of justification analysis is not in view. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-20
EDGE: `bayesian_epistemology` [epistemology] → `dutch_book_argument` [epistemology]
SEP-ANCHORED REASONING: SEP entries "Bayesian Epistemology" and "Dutch Book Arguments" present DBA as the canonical pragmatic motivation for Bayesian probabilism — "an agent whose credences violate the probability axioms is exploitable" — with diachronic Dutch books (Lewis, Teller) further motivating conditionalization. The canonical SEP teaching order presents DBA as a setup that motivates the probabilist commitments of Bayesianism, not the reverse. The migration's direction (Bayesianism → DBA) treats DBA as content WITHIN Bayesian doctrine rather than as motivation FOR it. Defensible reading: once Bayesianism is taught as a framework, DBA fits as the constitutive pragmatic argument internal to the doctrine. Not the canonical SEP framing but supportable.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Reversal would also be defensible (DBA → Bayesian probabilism, with conditionalization downstream of probabilism). Closeout may consider whether the framework-then-motivation order or motivation-then-framework order better matches teaching-graph priorities. Joyce's accuracy-dominance argument (not in graph) is the main contemporary alternative motivator.

### Finding E-21
EDGE: `internalism_epistemic` [epistemology] → `evidentialism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Evidentialism" places the position in the internalist camp: "evidentialism is the canonical contemporary internalist position; justification supervenes on the mental." The dialectical framing (evidentialism as one specific internalist thesis) requires internalism as the genus before evidentialism as the species. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-22
EDGE: `epistemic_justification` [epistemology] → `virtue_epistemology` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Virtue Epistemology" presents the program as a reorientation in which intellectual virtues become the primary unit of analysis for both knowledge AND justification. The dialectical motivation requires the prior concept of justification as one of the standard analytic targets the program reorients away from belief-centered analyses of. Pedagogical direction sound. (An alternative proximate prereq would be `knowledge` itself — Sosa's AAA structure is most often introduced as an account of knowledge — but `epistemic_justification` is also a target of virtue-theoretic accounts, especially the responsibilist branch.)
VERDICT: sound
CONFIDENCE: medium
NOTES: Alternative proximate prereq via `knowledge`. Either reading is supportable; the migration's choice fits the responsibilist framing better than the reliabilist (Sosa) framing.

### Finding E-23
EDGE: `tracking_theory_of_knowledge` [epistemology] → `sensitivity_condition` [epistemology]
SEP-ANCHORED REASONING: SEP entry "The Analysis of Knowledge" presents sensitivity as one component of Nozick's 1981 tracking theory ("S would not believe p if p were false"). The condition is intelligible only as a component of the broader tracking apparatus; without tracking in view, sensitivity is just a counterfactual claim with no theoretical home. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-24
EDGE: `basic_belief` [epistemology] → `foundationalism` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Foundationalist Theories of Epistemic Justification" treats basic beliefs as the foundational layer that defines the position structurally: foundationalism = "justified beliefs come in two kinds, basic and non-basic". The position cannot be stated without the basic / non-basic distinction; basic_belief is constitutive content. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-25
EDGE: `epistemic_justification` [epistemology] → `skepticism_epistemic` [epistemology]
SEP-ANCHORED REASONING: SEP entry "Skepticism" presents epistemic skepticism as targeting the possibility of justified belief / knowledge. To engage the skeptical challenge, the prior concept of what skepticism attacks (justification — the conditions under which beliefs count as justified) is required. Pedagogical direction sound. (`knowledge` is also a parallel proximate prereq via the parallel edge `knowledge → skepticism_epistemic`.)
VERDICT: sound
CONFIDENCE: high
NOTES: —

## Sampled-node candidate findings

### Finding N-1
NODE: `pyrrhonian_skepticism` [Pyrrhonian Skepticism, domain=epistemology]
   summary: "The ancient skeptical tradition (Pyrrho, Sextus Empiricus) on which suspending judgment (epoché) is the appropriate response to the equipollence of contrary arguments, and tranquility (ataraxia) is the practical upshot. Distinct from Cartesian skepticism..."
SEP-ANCHORED REASONING: SEP entry "Ancient Skepticism" / "Pyrrho" treats Pyrrhonism as a tradition with definite doctrines (epoché, ataraxia, the modes). The label functions in pedagogical practice both as a school designation (the historical Pyrrhonist movement) and as a specific epistemic position (the doctrine of suspending judgment for tranquility). Concept-shaped enough that students learn it as a position with content; the school-label dimension is real but weaker than for "Vienna Circle" or "Scholasticism" (which lack comparable internal doctrinal content). Summary reads as instructional voice with concept-grounded specificity (epoché, ataraxia, contrast with Cartesian skepticism, distinction from academic skepticism).
VERDICT: sound
CONFIDENCE: medium
NOTES: Borderline granularity — node is a school/tradition label that has crystallized into a specific position; closeout may consider whether the "tradition" framing in the summary should be slightly compressed to the position framing for granularity-cleanness, but no defect observed.

### Finding N-2
NODE: `propositional_knowledge` [Propositional Knowledge, domain=epistemology]
   summary: "Knowledge that some proposition is true — knowing-that. The primary target of the analysis-of-knowledge tradition, standardly analyzed as justified true belief plus a Gettier-resistant condition. Contrasts with knowledge-how..."
SEP-ANCHORED REASONING: SEP entry "The Analysis of Knowledge" treats propositional knowledge as the canonical target of the JTB-and-amendments tradition. Concept-level granularity: yes, the mastery unit "knowing that p" is atomic. Summary reads as instructional voice referencing the analysis tradition, the JTB structure, and the knowing-that / knowing-how contrast. Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-3
NODE: `belief` [Belief, domain=epistemology]
SEP-ANCHORED REASONING: SEP entries "Belief" and "Doxastic Voluntarism" treat belief as the basic propositional attitude in epistemology. Concept-level: atomic mastery unit. Summary contrasts belief with non-doxastic attitudes (hoping, fearing) and flags credence as a refinement — instructional voice, concept-grounded specificity.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-4
NODE: `sensitivity_condition` [Sensitivity Condition, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "The Analysis of Knowledge" treats Nozick's sensitivity condition as a specific counterfactual condition: "S's belief that p is sensitive iff in the nearest possible world where p is false, S does not believe p." Concept-level: yes, a definite modal condition. Summary captures the condition's content, its relation to closure (Nozick embraces non-closure; safety preserves it), and the historical lineage. Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-5
NODE: `epistemic_justification` [Epistemic Justification, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Epistemic Justification" treats it as the third clause of JTB and the surface where internalism / externalism / structural-debate compete. Concept-level: atomic. Summary distinguishes justification from reliability (internalist intuition) and from truth (fallibilism), framing the concept as normative. Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-6
NODE: `expertise` [Expertise, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Social Epistemology" / Goldman 2001 frames expertise as the epistemic standing warranting deference. Concept-level: yes, a definite epistemic standing. Summary cites Goldman's five sources of evidence laypersons use to evaluate experts and connects to medicine / climate / policy applications. Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-7
NODE: `safety_condition` [Safety Condition, domain=epistemology]
SEP-ANCHORED REASONING: SEP entries "The Analysis of Knowledge" and "Modal Epistemology" treat the safety condition (Sosa 1999, Williamson 2000) as the dominant contemporary modal condition on knowledge. Concept-level: yes, a definite modal condition. Summary captures the condition's content, the contrast with sensitivity, and the closure-preservation motivation. Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-8
NODE: `bayesian_epistemology` [Bayesian Epistemology, domain=epistemology]
   summary: "The framework that models rational belief as conformity to the probability calculus (probabilism) and rational belief revision as conditionalization on new evidence..."
SEP-ANCHORED REASONING: SEP entry "Bayesian Epistemology" presents the framework via three theses (probabilism, conditionalization, decision theory). Granularity check: the label functions as a sub-discipline / framework name in much the way "Formal Epistemology" or "Virtue Epistemology" do. Per ADR 0008 the warning is for thinker-framework / school / discipline labels at granularity-mismatch with concept-level mastery units. "Bayesian Epistemology" is on the borderline — it has crystallized into a specific doctrine (probabilism + conditionalization + Bayesian decision theory) that students learn as a content cluster, but the label itself reads as a framework/discipline name. The aliases include `bayesianism`, the doctrine label. Closer to concept-shaped than discipline-shaped on the doctrine reading.
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Closeout may consider whether to retitle to "Bayesianism" (the doctrine) for granularity-cleanness, OR to accept that frameworks-with-doctrinal-content can sit at concept-level granularity. Consistent treatment with `virtue_epistemology` and `formal_epistemology` (also in graph at similar granularity) is a structural decision.

### Finding N-9
NODE: `evidence` [Evidence, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Evidence" treats it as a central epistemological primitive: what a believer has access to that bears on whether p is true. Concept-level: atomic. Summary distinguishes the role evidence plays across internalism (access-based) and externalism (reliability-based) and flags evidentialism (Conee, Feldman). Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-10
NODE: `dutch_book_argument` [Dutch Book Argument, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Dutch Book Arguments" treats DBA as a specific pragmatic argument with named structure (synchronic for probabilism; diachronic — Lewis, Teller — for conditionalization). Concept-level: yes, a definite argument-form. Summary captures the synchronic / diachronic distinction, the pragmatic-vs-epistemic dispute (Joyce's accuracy-dominance alternative), and the canonical teaching approach (worked case with bookmaker's sure-loss combination). Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-11
NODE: `foundationalism` [Foundationalism, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Foundationalist Theories of Epistemic Justification" treats foundationalism as a structural thesis about the architecture of justified belief. Concept-level: yes, a definite position. Summary distinguishes classical (Cartesian, infallibilist) from modest (Pryor) versions and cites the regress argument as standard motivation. Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-12
NODE: `epistemic_closure` [Epistemic Closure, domain=epistemology]
SEP-ANCHORED REASONING: SEP entry "Epistemic Closure Principles" treats closure as a specific principle about knowledge — closure under (some restricted form of) known entailment. Concept-level: yes, a definite principle. Summary captures the principle's role in skeptical arguments and the sensitivity / safety dispute (Nozick, Dretske deny; safety theorists preserve). Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

## Cross-cutting observations

Three load-bearing aggregate patterns surfaced; recorded sparingly per master-plan §T2-D:

1. **Defect rate well below the cross-bridge baseline.** Substantive defects (reversed | weak | thematic | historical | granularity-mismatch | authenticity) total **2 of 37 sampled elements** (5.4%): 1 reversed edge (E-13 problem_of_induction → pyrrhonian_skepticism) + 1 granularity-mismatch node (N-8 bayesian_epistemology). Edge-only defect rate is 1/25 = 4%; node defect rate 1/12 = 8.3%. This is well below the 35.2% substantive defect rate AUDIT-CB found across cross-bridges and is consistent with the structural prediction that within-subdomain edges (textbook-shaped clusters within a single SEP-coherent area) should run cleaner than cross-domain bridges. The mid-sample-defect-rate expansion trigger (>60% at half-sample → expand to 50% density) was nowhere near firing; standard 35% density held.

2. **Defensible-but-not-canonical edges cluster around dialectical orderings of frameworks-vs-motivations.** E-2 (expertise → epistemic_dependence) and E-20 (bayesian_epistemology → dutch_book_argument) are both edges where the migration's chosen direction is supportable but inverts the canonical SEP teaching order (concept-as-framework before motivating-argument-or-broader-phenomenon). These are not defects; they reflect a genuine pedagogical-priority choice (taught-as-content vs taught-as-motivation). Closeout may consider whether the audit's accumulated "defensible" edges across subdomains share this framework-vs-motivation pattern — if yes, a structural choice for the graph rather than per-edge dispositioning.

3. **No new gate-feasible audit-system-input class surfaced.** The four pre-listed proposals from the master plan (edge_evidence_empty, discipline_label_node_at_root, prereq_direction_summary_inconsistency, historical_node_as_prereq_source) all remain applicable but no within-epistemology edge or node uniquely surfaced a fifth class. The S-0104 cross-bridge AUDIT-CB session surfaced one new class (`cross_bridge_pedagogical_direction_inconsistent_with_summary`); within-epistemology data does not corroborate or extend that class beyond the cross-bridge surface (the pattern was specific to cross-bridges where source.summary + target.summary together implied opposite direction). The empty `evidence` field finding (master-plan §T2-E) is confirmed within-epistemology too — uniform null across all 72 within-epistemology edges, consistent with graph-wide.

## SEP citations consulted

- SEP entry: "The Analysis of Knowledge"
- SEP entry: "Epistemic Justification"
- SEP entry: "Foundationalist Theories of Epistemic Justification"
- SEP entry: "Coherentist Theories of Epistemic Justification"
- SEP entry: "Infinitism in Epistemology"
- SEP entry: "Internalist vs. Externalist Conceptions of Epistemic Justification"
- SEP entry: "Reliabilist Epistemology"
- SEP entry: "Evidentialism"
- SEP entry: "Virtue Epistemology"
- SEP entry: "Knowledge How"
- SEP entry: "Knowledge First Epistemology"
- SEP entry: "Understanding"
- SEP entry: "Bayesian Epistemology"
- SEP entry: "Dutch Book Arguments"
- SEP entry: "Epistemic Closure Principles"
- SEP entry: "Modal Epistemology"
- SEP entry: "Skepticism"
- SEP entry: "Ancient Skepticism"
- SEP entry: "Pyrrho"
- SEP entry: "The Problem of Induction"
- SEP entry: "Social Epistemology"
- SEP entry: "Evidence"
- SEP entry: "Belief"
- SEP entry: "Doxastic Voluntarism"
- SEP entry: "Certainty"
