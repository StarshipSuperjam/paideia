# Phase 5 production audit evidence — ethics

> Authored by S-0108 (routine session) per T-PHASE-5-AUDIT task `AUDIT-ETH`.
> SEP-anchored review per [`engine/build_readiness/phase_5_production_audit.md`](../phase_5_production_audit.md).
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: ethics (within-domain edges; cross-bridges to other philosophy subdomains and to service-domain primitives are AUDIT-CB scope, not duplicated here)
- Edge population: 68 within-ethics edges (34 in `0020_seed_ethics_part1.sql` metaethics + normative-theory + 34 in `0026_seed_ethics_part1.sql` applied ethics; matches master-plan figure)
- Edge sample size: **24** (35.3% density per master-plan §"Sample-size policy" AUDIT-ETH row)
- Sample density: **35.3%** (24/68)
- Sample selection: deterministic md5(seed='AUDIT-ETH' || source_id || '|' || target_id) ordering across the 68-edge population, take first 24. Inputs sourced from the two seed migrations (live-DB read denied in routine mode per ADR 0055; the migrations are the canonical authoring record, applied verbatim to production).
- Node sample size: **12** (~12 edge-anchored per master-plan §"Sample-size policy")
- Node sample selection: union of source/target endpoints across the 24 sampled edges (34 unique nodes), then md5(seed='AUDIT-ETH' || node_id) ordering, take first 12
- Generation date: 2026-05-09
- Methodology: parametric SEP-anchored review only (no empirical-fortification branch — routine-mode prohibition load-bearing per master-plan §"Empirical-fortification branch" until T1-A through T1-D close at the closeout per ADR 0053)

## Sampled-edge candidate findings

### Finding E-1
EDGE: `environmental_ethics` [ethics] → `ecocentrism` [ethics]
   edge_type = pedagogical_prerequisite, weight/confidence per migration; evidence text null graph-wide (master-plan §T2-E).
SEP-ANCHORED REASONING: SEP entries "Environmental Ethics" and "Environmental Holism" treat anthropocentrism / biocentrism / ecocentrism as the canonical taxonomic axis along which environmental-ethical positions are introduced. The genus (environmental ethics as a field) is the natural place to introduce the species (ecocentrism, biocentrism, anthropocentrism); SEP entries follow this teaching order. Pedagogical direction sound — students need the field's framing question (what entities have moral standing in the environmental domain?) before they can engage ecocentrism as one structural answer.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-2
EDGE: `environmental_ethics` [ethics] → `anthropocentrism` [ethics]
SEP-ANCHORED REASONING: Same taxonomic structure as E-1. SEP entry "Environmental Ethics" presents anthropocentrism as the orthodox view environmental-ethics historically defines itself against (Routley/Sylvan's 1973 last-man-on-Earth thought experiment is the canonical SEP framing). Field-level framing required before the position can be engaged. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-3
EDGE: `environmental_ethics` [ethics] → `climate_ethics` [ethics]
SEP-ANCHORED REASONING: SEP entry "Climate Justice" treats climate ethics as a development within environmental ethics distinguished by its intergenerational, global, and cumulative structure (per Gardiner 2011 "A Perfect Moral Storm"). Climate ethics inherits the field's basic question (what's the moral standing of nature, future generations, distant others?) and adds structural complications. Pedagogical direction sound — climate ethics requires environmental ethics' framing as conceptual ancestor.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-4
EDGE: `is_ought_distinction` [ethics] → `moral_naturalism` [ethics]
SEP-ANCHORED REASONING: SEP entries "Moral Naturalism" and "Naturalism in Moral Philosophy" treat the is-ought distinction (Hume 1739; Moore 1903's open-question argument as its 20th-century reformulation) as the foundational challenge moral naturalism must address. Naturalism cannot be coherently introduced without the gap-objection in view; the position is structurally a response to the challenge. Pedagogical direction sound — students need the is-ought distinction as the structural setup before naturalism's reductive or non-reductive moves register as taking on the challenge.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-5
EDGE: `motivational_internalism` [ethics] → `expressivism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Cognitivism vs. Non-Cognitivism" treats motivational internalism as one of the two main argumentative motivations for expressivism — alongside the open-question argument. The standard SEP teaching order presents internalism as the foundational thesis, then expressivism as a position designed to explain it (if moral judgments express motivating states like desires or plans, the necessary connection between sincere judgment and motivation falls out for free; on a Humean account of motivation, expressivism puts the desire INSIDE the moral judgment). The migration's direction (internalism → expressivism) follows this order: internalism in view, then expressivism as the metaethical view that explains it. Defensible reading: internalism could also be taught DOWNSTREAM of expressivism (once expressivism is the framework, internalism is its natural prediction), but the SEP-canonical order treats internalism as the foundational thesis with expressivism the position-that-explains-it.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Direction is supportable on standard SEP teaching order. Closeout may consider whether this edge clusters with E-2 / E-20 of S-0105 epistemology (frameworks-vs-motivations dialectical-ordering pattern) — expressivism is framework, motivational internalism is the motivation/setup; the migration treats setup-as-prereq-for-framework. Either order is supportable; the cross-cutting pattern across subdomains may be worth synthesis at closeout.

### Finding E-6
EDGE: `technology_ethics` [ethics] → `ai_ethics` [ethics]
SEP-ANCHORED REASONING: SEP entries "Ethics of Artificial Intelligence and Robotics" and "Computer and Information Ethics" treat AI ethics as a contemporary specialization within the broader technology-ethics tradition (Joseph Weizenbaum 1976 ethics-of-computer-systems work; James Moor's logic-malleability-of-computers thesis; Bostrom & Yudkowsky 2014). Genus-species pedagogical ordering is sound — AI ethics inherits technology ethics' framing (intentional design embedding values, dual-use risks, distributive impact of technical systems) and applies it to a specific technical surface.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-7
EDGE: `deontology` [ethics] → `kantian_ethics` [ethics]
SEP-ANCHORED REASONING: SEP entries "Deontological Ethics" and "Kant's Moral Philosophy" treat Kantian ethics as the canonical exemplar of deontology — the position the family is most commonly introduced through. The family-before-canonical-exemplar ordering is the standard SEP teaching approach (analogous to the consequentialism → utilitarianism edge). Pedagogical direction sound — students grasp the family's structural shape (agent-centered restrictions; non-consequentialist evaluation) before engaging Kant's specific apparatus (categorical imperative, dignity-as-end, kingdom of ends).
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-8
EDGE: `applied_ethics` [ethics] → `technology_ethics` [ethics]
SEP-ANCHORED REASONING: SEP entry "Applied Ethics" treats technology ethics as one of the canonical sub-areas (alongside bioethics, business ethics, environmental ethics). Genus-species pedagogical ordering. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-9
EDGE: `moral_realism` [ethics] → `moral_naturalism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Realism" presents moral naturalism as the empirically-friendly variety of realism — the Cornell-realist line (Boyd 1988, Brink 1989, Sturgeon 1985). Naturalism is a SPECIES of realism: cognitivism + moral facts + mind-independence + the additional claim that moral facts are natural facts. The species-of-genus pedagogical ordering is sound — students need realism's commitments before they can grasp how naturalism fills them out.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-10
EDGE: `applied_ethics` [ethics] → `bioethics` [ethics]
SEP-ANCHORED REASONING: SEP entry "Applied Ethics" treats bioethics as the most-developed sub-area of applied ethics, with its own canonical literature (Beauchamp & Childress 1979 Principles of Biomedical Ethics; Engelhardt 1986 The Foundations of Bioethics). Genus-species pedagogical ordering. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-11
EDGE: `moral_realism` [ethics] → `moral_non_naturalism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Non-Naturalism" presents the position (Moore 1903 PRINCIPIA ETHICA; Parfit 2011 ON WHAT MATTERS) as the variety of realism that takes moral properties to be sui generis — irreducible to natural properties. Non-naturalism is a species of realism (cognitivism + moral facts + mind-independence + non-reducibility). Species-of-genus ordering. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-12
EDGE: `normative_ethics` [ethics] → `divine_command_theory` [ethics]
SEP-ANCHORED REASONING: SEP entry "Religion and Morality" treats divine command theory as one option in the normative-theory taxonomy (alongside consequentialism, deontology, virtue ethics, contractualism). The genus-to-species ordering is the standard pedagogical approach: introduce the field, then study its options. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-13
EDGE: `normative_ethics` [ethics] → `supererogation` [ethics]
SEP-ANCHORED REASONING: SEP entry "Supererogation" presents the category as a structural concept that any normative theory must engage — the praiseworthy-but-not-required actions whose existence tests theories against the demandingness objection (Williams 1973, Singer 1972). The category presupposes a normative-ethics framing in which the categories of obligatory / permissible / prohibited are in view; supererogation is the FOURTH category that the standard tripartite scheme must accommodate. Pedagogical direction sound — students need the standard normative-ethics scheme before supererogation registers as a structural test.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-14
EDGE: `ecocentrism` [ethics] → `deep_ecology` [ethics]
SEP-ANCHORED REASONING: SEP entry "Environmental Ethics" treats deep ecology (Næss 1973 "The Shallow and the Deep, Long-Range Ecology Movement") as a development within ecocentric environmental ethics that combines ecocentric value commitments with a critique of industrial-modern civilization. Deep ecology presupposes ecocentrism's foundational move (intrinsic value of ecosystems as wholes); the additional content (eight platform principles, deep questioning of consumerism, biospheric egalitarianism) builds on it. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-15
EDGE: `normative_ethics` [ethics] → `moral_particularism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Particularism" presents Dancy's 1993/2004 position as the systematic rejection of principlism in normative ethics. Particularism is a meta-position about the structure of normative-ethical knowledge (it consists in the perception of relevant features in particular cases, not in the application of exceptionless principles). The position is intelligible only against the principlist target it rejects — students need normative ethics' standard rule-application picture in view before particularism's holism objection registers. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-16
EDGE: `animal_ethics` [ethics] → `sentientism` [ethics]
SEP-ANCHORED REASONING: SEP entries "The Moral Status of Animals" and "Animal Ethics" treat sentientism (or the sentience criterion) as the foundational stance underwriting contemporary animal ethics — Bentham's 1789 footnote ("the question is not, can they reason? nor, can they talk? but, can they suffer?") is the canonical text, with Singer 1975 ANIMAL LIBERATION as its systematic 20th-century development. The conceptual ordering in SEP is sentientism (or sentience-based moral status more broadly) → animal ethics: once you accept sentience as the criterion of moral status, the obligations toward sentient non-human animals follow as a derived conclusion. The migration's direction (animal_ethics → sentientism) treats sentientism as content-within-animal-ethics rather than as foundation-for-animal-ethics. This inverts the canonical SEP teaching order. Singer's argumentative move IS to derive animal ethics FROM sentientism (or its equivalent — equal consideration of interests applied to all sentient creatures); the field's intellectual structure is sentientism-prior-and-foundational.
VERDICT: reversed
CONFIDENCE: medium
NOTES: A more canonical direction would be `sentientism → animal_ethics`. The reversal could also be read as a weak/redundant edge: the more proximate prereq for sentientism is plausibly an epistemic / philosophy-of-mind concept (the capacity for subjective experience grounds moral status), which P5-11 cross-bridges may handle. Closeout may consider whether this is a direction reversal, a weak/redundant within-subdomain edge, or both. Note that the E-16 reversal pattern parallels S-0105's E-13 (problem_of_induction → pyrrhonian_skepticism) — in both cases the migration treats a tradition-or-foundational-stance as DOWNSTREAM of an application or specific subfield, when the canonical SEP ordering runs the other way.

### Finding E-17
EDGE: `virtue_ethics` [ethics] → `moral_particularism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Particularism" notes that particularism is a natural ally of virtue ethics (both privilege practical wisdom / phronesis over rule-application), but Dancy's 1993/2004 articulation of particularism is NOT specifically motivated by virtue ethics — Dancy himself comes from a deontological (Rossian) starting point and explicitly resists collapsing particularism into virtue ethics. The graph already contains the parallel edge `normative_ethics → moral_particularism` (E-15 in this sample), which is the more proximate prereq: particularism is a meta-position about the structure of normative-ethical knowledge, not a specific outgrowth of virtue ethics. The virtue_ethics → moral_particularism edge adds a more specific connection but is largely redundant given the broader edge from normative_ethics; it functions as a long-distance shortcut that may not contribute additional pedagogical value.
VERDICT: weak
CONFIDENCE: medium
NOTES: Closeout may consider whether to prune this edge in favor of the broader normative_ethics → moral_particularism edge, or to keep both (with virtue_ethics → moral_particularism as the more specific connection capturing the virtue-particularism alliance). Either choice is defensible; the pedagogical value of the virtue-specific edge is the SEP-recognized alliance between particularism and virtue ethics (both privilege practical wisdom). The redundancy concern is the parallel edge through the broader genus.

### Finding E-18
EDGE: `four_principles_bioethics` [ethics] → `non_maleficence` [ethics]
SEP-ANCHORED REASONING: SEP entry "The Definition of Death" and the broader bioethics literature treat non-maleficence as one of Beauchamp & Childress's four principles (autonomy, non-maleficence, beneficence, justice). The framework introduces the principles as its constitutive content — students cannot grasp the four-principles approach except by reference to its four principles. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-19
EDGE: `future_generations` [ethics] → `intergenerational_justice` [ethics]
SEP-ANCHORED REASONING: SEP entries "Intergenerational Justice" and "The Non-Identity Problem" treat the abstract concept of future generations (people who do not yet exist but will) as the foundational concept on which any normative theory of intergenerational obligations must build. The justice question (what do we owe future generations? how should benefits and burdens be distributed across generations?) presupposes the moral standing of future people; without that prior conceptual move, the justice questions don't get traction. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-20
EDGE: `moral_realism` [ethics] → `moral_epistemology` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Epistemology" treats moral epistemology as a question that BOTH realists and anti-realists must answer — error theorists explain why we don't know moral truths (because there are no moral truths to know); expressivists explain how moral judgments can be reasoned about despite not being truth-apt; realists face the canonical challenge of how we have epistemic access to mind-independent moral facts. Moral epistemology is downstream of metaethics broadly, not specifically of realism. The graph already contains the parallel edge `metaethics → moral_epistemology` (in 0020 line 643, not in this sample but present in the full population), which is the more proximate prereq: moral epistemology is metaethics applied to the question of moral knowledge, regardless of which metaethical position one holds. The moral_realism → moral_epistemology edge is plausibly weak/redundant — the strongest pressure on moral epistemology DOES come from realism (how do we know mind-independent moral truths?), but the prereq need not run through realism specifically; metaethics in general suffices.
VERDICT: weak
CONFIDENCE: medium
NOTES: Closeout may consider whether to prune this edge in favor of the broader metaethics → moral_epistemology edge, or to keep both (with moral_realism → moral_epistemology as the realist-specific connection capturing the access-to-mind-independent-truths challenge). Either choice is defensible; the redundancy concern is the parallel edge through the broader genus. The pattern parallels E-17 (virtue_ethics → moral_particularism alongside normative_ethics → moral_particularism) — both cases involve a species-level edge running parallel to a genus-level edge already in the graph.

### Finding E-21
EDGE: `metaethics` [ethics] → `moral_anti_realism` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Anti-Realism" treats anti-realism as one of the two principal metaethical positions on the existence of moral facts (alongside realism). Anti-realism is a species of metaethics — students need the metaethical framing question (do moral facts exist?) before they can engage anti-realism's negative answer. Genus-species ordering. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-22
EDGE: `moral_anti_realism` [ethics] → `error_theory` [ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Anti-Realism" treats error theory (Mackie 1977 ETHICS: INVENTING RIGHT AND WRONG) as a species of anti-realism that combines cognitivism (moral utterances are truth-apt) with the claim that all positive moral claims are systematically false (because there are no moral facts). The position is intelligible only as a specific anti-realist option — students need anti-realism's framing in view before error theory's distinctive cognitivism-plus-systematic-falsity move registers. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-23
EDGE: `four_principles_bioethics` [ethics] → `beneficence` [ethics]
SEP-ANCHORED REASONING: Same structure as E-18 — SEP entry on principlism in bioethics treats beneficence as the second of Beauchamp & Childress's four principles (the positive duty-to-benefit, complementary to non-maleficence's negative duty-not-to-harm). The framework introduces the principle as constitutive content. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding E-24
EDGE: `morality` [ethics] → `normative_ethics` [ethics]
SEP-ANCHORED REASONING: SEP entries "The Definition of Morality" and "Normative Ethics" treat normative ethics as the branch of ethics asking what we ought to do (what character to cultivate, what acts to perform, what reasons obligate). The branch presupposes the framing concept of morality (the domain of right and wrong action, distinct from etiquette / legality / prudence). The graph's foundational ordering — morality → metaethics + morality → normative_ethics — mirrors SEP's canonical genus-and-two-branches structure. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high
NOTES: —

## Sampled-node candidate findings

### Finding N-1
NODE: `moral_particularism` [Moral Particularism, domain=ethics]
   summary: "Jonathan Dancy's 1993 / 2004 view (MORAL REASONS; ETHICS WITHOUT PRINCIPLES) that there are no exceptionless moral principles; moral judgment in particular cases is irreducible to rule-application..."
SEP-ANCHORED REASONING: SEP entry "Moral Particularism" treats Dancy's particularism as a definite metaethical/normative position with structured content (holism about moral reasons, rejection of principlism, the same-feature-opposite-valence argument). Concept-level granularity: yes, an atomic mastery unit (the position with its arguments). Summary reads as instructional voice with concept-grounded specificity (Dancy's two books, holism, the rejection of principlism, the alliance with virtue ethics). Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-2
NODE: `supererogation` [Supererogation, domain=ethics]
   summary: "The category of morally PRAISEWORTHY actions that go beyond what is morally REQUIRED..."
SEP-ANCHORED REASONING: SEP entry "Supererogation" treats it as a structural category in normative ethics — the praiseworthy-but-not-required actions whose existence tests normative theories. Concept-level granularity: yes, the category is an atomic mastery unit (the obligatory/permissible/supererogatory tripartite scheme, plus the structural test it provides). Summary captures the category's content (the tripartite distinction), the demandingness objection it tests (Williams 1973, Singer 1972), and the differential treatment across normative theories (consequentialism struggles; deontology and virtue ethics handle naturally). Instructional voice, concept-grounded specificity.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-3
NODE: `moral_non_naturalism` [Moral Non-Naturalism, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Non-Naturalism" treats it as a definite metaethical position (Moore 1903, Parfit 2011) — moral properties are sui generis, irreducible to natural properties. Concept-level: yes, a definite position with the open-question argument as its canonical defense and the epistemological challenge (how do we have access to non-natural properties?) as its persistent objection. Summary cites Moore, Parfit, the open-question argument, intuitionism (Ross 1930). Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-4
NODE: `moral_epistemology` [Moral Epistemology, domain=ethics]
   summary: "The branch of metaethics asking how we know moral truths (if any)..."
SEP-ANCHORED REASONING: SEP entry "Moral Epistemology" treats moral epistemology as a sub-discipline within metaethics that applies general epistemological apparatus (knowledge, justification, evidence, intuition) to the moral domain. Granularity check: the label is explicitly framed in the summary as "the branch of metaethics" — a sub-discipline name. Per ADR 0008 the warning is for thinker-framework / school / discipline labels at granularity-mismatch with concept-level mastery units. Moral epistemology is on the borderline — it has crystallized into a research area with structured options (intuitionism, coherentism, reliabilism, skepticism), but the label itself reads as a sub-discipline name. Closer to discipline-shaped than concept-shaped, parallel to the bayesian_epistemology / virtue_epistemology pattern noted at S-0105 N-8.
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Closeout may consider whether to retitle to a more concept-shaped label (e.g., a specific moral-knowledge thesis), OR to accept that sub-discipline-labels-with-doctrinal-content can sit at concept-level granularity. Consistent treatment with `bayesian_epistemology` (N-8 at S-0105, granularity-mismatch), `virtue_epistemology`, `formal_epistemology` is a structural decision the closeout adjudicates. The pattern recurring across subdomains (ethics + epistemology so far) is itself a finding worth flagging at closeout — sub-discipline labels with content cluster as a graph-wide structural choice, not as per-node defects.

### Finding N-5
NODE: `expressivism` [Expressivism, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Cognitivism vs. Non-Cognitivism" / "Expressivism" treats expressivism as a definite metaethical position (Ayer 1936, Stevenson 1944, Hare 1952, Blackburn quasi-realism, Gibbard norm-expressivism / plan-expressivism). Concept-level: yes, a definite position with the Frege-Geach problem as its canonical technical challenge. Summary cites the major figures, the foundational books, the Frege-Geach problem (Geach 1965), and the connection to motivational internalism. Instructional voice, concept-grounded.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-6
NODE: `non_maleficence` [Non-Maleficence, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "The Doctrine of Double Effect" and bioethics literature treat non-maleficence (primum non nocere) as one of Beauchamp & Childress's four principles — the negative duty to refrain from harming. Concept-level: yes, a definite principle with structured content (the negative-vs-positive distinction with beneficence; the priority of harm-avoidance; the application to research-ethics risk-minimization). Summary captures the principle's three distinguishing features (negative; priority over beneficence; harm-benefit-ratio attention) and its connection to the doctrine of double effect (Aquinas, Foot 1967, McMahan 1994, Quinn 1989). Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-7
NODE: `divine_command_theory` [Divine Command Theory, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Religion and Morality" / "Voluntarism, Theological" treats divine command theory as a definite normative-theory option — moral truths are grounded in God's commands. Concept-level: yes, a definite position with the Euthyphro dilemma (Plato EUTHYPHRO 10a) as its canonical structural challenge and modified-DCT (Adams 1999) as the contemporary refinement that grounds the GOOD in God's nature while grounding OBLIGATIONS in God's commands. Summary captures the position's three varieties (unrestricted DCT, modified DCT, natural law theology), the Euthyphro dilemma, and Adams's modern resolution attempt. Authentic.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-8
NODE: `deontology` [Deontology, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Deontological Ethics" treats deontology as a family of normative theories taking action-structure (not consequences alone) to determine moral status. Concept-level: yes, a definite family-of-positions with structural commitments (agent-centered restrictions, agent-centered options) shared across its members (Kantian ethics, Rossian pluralism, modern deontologists like Nagel, Kamm, Scanlon). Summary captures the family's structural commitments, the canonical Kantian articulation, Ross's 1930 prima facie duties, the restrictions-vs-options distinction, and the canonical objections (rigorism, conflicting duties, motivational sufficiency). Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-9
NODE: `animal_ethics` [Animal Ethics, domain=ethics]
   summary: "The branch of applied ethics treating moral questions about humans' relations to non-human animals..."
SEP-ANCHORED REASONING: SEP entry "The Moral Status of Animals" treats animal ethics as a developed subfield of applied ethics with its own canonical literature (Singer 1975, Regan 1983) and contemporary developments (virtue-ethical, care-ethical, capabilities approaches; Donaldson & Kymlicka 2011 zoopolis). Granularity check: the label is explicitly framed in the summary as "the branch of applied ethics" — a sub-discipline name parallel to bioethics, environmental ethics, business ethics. Per ADR 0008 the warning is for sub-discipline labels at granularity-mismatch. Animal ethics is on the same borderline as moral_epistemology (N-4) — it has crystallized into a research area with structured options, but the label itself reads as a sub-discipline name with content rather than as an atomic concept-level mastery unit.
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Closeout may consider whether the applied-ethics-subfield-label pattern (animal_ethics, bioethics, environmental_ethics, business_ethics, technology_ethics) is a graph-wide structural choice that should be either consistently flagged or consistently accepted. The Phase 5 decomposition's design treats these subfield labels as nodes; flagging every one as granularity-mismatch would amount to a structural rejection of the approach. Recommend the closeout adjudicate at the structural level rather than per-node. The same observation applies to sub-discipline labels in metaethics (moral_epistemology) and epistemology (bayesian_epistemology, virtue_epistemology, formal_epistemology — the S-0105 pattern).

### Finding N-10
NODE: `intergenerational_justice` [Intergenerational Justice, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Intergenerational Justice" treats it as a definite normative concept with structured content — the fair distribution of benefits and burdens across generations. Concept-level: yes, an atomic mastery unit (the framework spanning utilitarian aggregation, Rawlsian just-savings, capabilities, sufficientarian, prioritarian options). Summary captures the major theoretical frameworks (utilitarian — with the discount-rate question; Rawls 1971 just-savings; capabilities — Nussbaum; sufficientarian; prioritarian), the climate-ethics application as concrete instantiation, and the non-identity problem as the persistent complication. Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-11
NODE: `beneficence` [Beneficence, domain=ethics]
SEP-ANCHORED REASONING: SEP entry on principlism in bioethics treats beneficence as one of Beauchamp & Childress's four principles — the positive duty to benefit patients. Concept-level: yes, a definite principle. Summary captures the principle's positive character, the Hippocratic-tradition lineage, the contemporary tension with autonomy (paternalism debate), the soft-vs-hard paternalism distinction (Beauchamp 2009; Dworkin 1972), and the rescue-cases / fiduciary distinction. Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

### Finding N-12
NODE: `motivational_internalism` [Motivational Internalism, domain=ethics]
SEP-ANCHORED REASONING: SEP entry "Moral Motivation" / "Internalism vs. Externalism in Ethics" treats motivational internalism as a definite metaethical position (Hare 1952, Blackburn 1984, Smith 1994) — sincere moral judgment is necessarily connected to motivation. Concept-level: yes, a definite thesis with structured content (the strong-vs-weak distinction; the connection to expressivism via Humean motivation; the amoralist counterexample debate). Summary captures the thesis, the strong-vs-weak distinction, the expressivist connection (judgments express motivating states; on Humean motivation, expressivism puts the desire INSIDE the judgment), Smith's 1994 refined version, and the cross-bridge to philosophy of mind (P5-07a) on practical reason structure. Authentic instructional voice.
VERDICT: sound
CONFIDENCE: high
NOTES: —

## Cross-cutting observations

Three load-bearing aggregate patterns surfaced; recorded sparingly per master-plan §T2-D:

1. **Defect rate above epistemology, well below cross-bridge baseline.** Substantive defects (reversed | weak | thematic | historical | granularity-mismatch | authenticity) total **6 of 36 sampled elements** (16.7%): 1 reversed edge (E-16 animal_ethics → sentientism), 2 weak/redundant edges (E-17 virtue_ethics → moral_particularism, E-20 moral_realism → moral_epistemology), 1 defensible edge (E-5 motivational_internalism → expressivism — flagged as defensible-not-defect but worth tracking), and 2 granularity-mismatch nodes (N-4 moral_epistemology, N-9 animal_ethics). Edge-only substantive-defect rate is 3/24 = 12.5%; node defect rate 2/12 = 16.7%. Overall 16.7% — meaningfully higher than S-0105 epistemology's 5.4% but well below S-0104 AUDIT-CB's 35.2% cross-bridge baseline. Consistent with the structural prediction that within-subdomain edges run cleaner than cross-domain bridges; the higher-than-epistemology rate plausibly reflects ethics' broader internal taxonomy (metaethics + normative + applied as three layers, with each layer adding edges and granularity-mismatch surface). The mid-sample-defect-rate expansion trigger (>60% at half-sample → expand to 50%) was nowhere near firing — half-sample defect rate (E-1 through E-12) was 1/12 = 8.3% (E-5 defensible only); the substantive defects clustered in the second half (E-16, E-17, E-20). Standard 35% density held.

2. **Two parallel-edge weak/redundant pairs surfaced.** E-17 (virtue_ethics → moral_particularism) and E-20 (moral_realism → moral_epistemology) both run parallel to broader-genus edges already in the graph (normative_ethics → moral_particularism for E-17; metaethics → moral_epistemology for E-20). The pattern: a more-specific within-subdomain edge sits alongside a less-specific within-subdomain edge that already covers the prereq. The closeout may consider whether the species-level edges add pedagogical value (capturing specific alliances or pressures) or function as long-distance shortcuts that invite pruning. The pattern may recur across subdomains; an aggregate scan at closeout could surface a graph-wide cleanup pass.

3. **Sub-discipline-label-with-content pattern is graph-wide, not per-node.** N-4 moral_epistemology and N-9 animal_ethics are both sub-discipline labels (explicitly framed in their summaries as "the branch of metaethics" / "the branch of applied ethics") with substantive doctrinal content. The same pattern surfaced at S-0105 in N-8 bayesian_epistemology, and is present (un-sampled here) in virtue_epistemology, formal_epistemology, bioethics, environmental_ethics, business_ethics, technology_ethics, just_war_theory. The Phase 5 decomposition's design treats these subfield labels as nodes; flagging every one as granularity-mismatch would amount to a structural rejection of the approach. Recommend the closeout adjudicate at the structural level (is this granularity choice load-bearing or a defect-class?) rather than per-node. If the closeout decides the granularity is acceptable, all such flags retire as no-action-no-defect. If the closeout decides the granularity is a defect, a graph-wide cleanup pass is needed — far beyond per-node disposition.

## SEP citations consulted

- SEP entry: "Environmental Ethics"
- SEP entry: "Environmental Holism"
- SEP entry: "Climate Justice"
- SEP entry: "Moral Naturalism"
- SEP entry: "Naturalism in Moral Philosophy"
- SEP entry: "Moral Cognitivism vs. Non-Cognitivism"
- SEP entry: "Expressivism"
- SEP entry: "Moral Anti-Realism"
- SEP entry: "Moral Realism"
- SEP entry: "Moral Non-Naturalism"
- SEP entry: "Moral Particularism"
- SEP entry: "Deontological Ethics"
- SEP entry: "Kant's Moral Philosophy"
- SEP entry: "Applied Ethics"
- SEP entry: "Ethics of Artificial Intelligence and Robotics"
- SEP entry: "Computer and Information Ethics"
- SEP entry: "Religion and Morality"
- SEP entry: "Voluntarism, Theological"
- SEP entry: "Supererogation"
- SEP entry: "The Moral Status of Animals"
- SEP entry: "Animal Ethics"
- SEP entry: "Intergenerational Justice"
- SEP entry: "The Non-Identity Problem"
- SEP entry: "Moral Epistemology"
- SEP entry: "The Doctrine of Double Effect"
- SEP entry: "Moral Motivation"
- SEP entry: "Internalism vs. Externalism in Ethics"
- SEP entry: "The Definition of Morality"
- SEP entry: "Normative Ethics"
