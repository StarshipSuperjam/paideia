# Phase 5 production audit evidence — hubs 6–10 + 3 syllabus traces

> Authored by S-0120 (routine session) per T-PHASE-5-AUDIT task AUDIT-HT-2 — second half of decomposed-AUDIT-HT (decomposed at S-0117 administrative close per Issue #58 because the original 96-edge + 10-node + 3-trace single-task scope hit context cap mid-authoring at S-0117). Sequential after AUDIT-HT-1 (S-0119 closed; depends_on satisfied) so two routine fires don't race to author both halves.
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: hubs 6–10 (next 5 by total degree across all subdomains; full incident-edge census on each hub plus per-node review of the hub nodes themselves) + 3 diagnostic syllabus traces per master-plan §"Three diagnostic syllabus traces"
- Hub identification (parametric scan of the 15 Phase 5 seed migrations 0011 / 0016 / 0030 / 0036 / 0040 / 0046 / 0050 / 0060 / 0070 / 0080 / 0090 / 0100 / 0110 / 0020 / 0026): classical_logic (logic, deg 9 — 3 out + 6 in), meaning (language, deg 9 — 7 out + 2 in), normative_ethics (ethics, deg 9 — 8 out + 1 in), vienna_circle_logical_positivism (service, deg 9 — 6 out + 3 in), aristotelian_four_causes (service, deg 8 — 7 out + 1 in)
- Edge population (incident to any of the 5 hubs): 44 raw edges, 43 unique after deduplication of 1 inter-hub edge (aristotelian_four_causes → vienna_circle_logical_positivism counted once across HUB I and HUB J — recorded under HUB I as a target edge and cross-listed by reference under HUB J)
- Edge sample size: 43; sample density: 100% (full census on incident edges per master-plan §"Sample-size policy" hubs row — hubs are calibration anchors for the closeout's aggregate-scan synthesis, not a stochastic sample)
- Node sample size: 5; selection: the 5 hub nodes themselves
- Syllabus traces: 3 per master-plan §"Three diagnostic syllabus traces" (T1-D locked) — gettier_problem (epistemology, BFS depth 4, 11 nodes including target), modal_realism (metaphysics, depth 5, 8 nodes), social_contract_theory (political philosophy, depth 3, 6 nodes — substituted for absent free_speech per S-0081 gate)
- Generation date: 2026-05-10
- Routine-mode posture: parametric-only review per master-plan §"Empirical-fortification branch" routine-mode prohibition (load-bearing until T1-A through T1-D close at the closeout interactive session per ADR 0053). Medium-confidence + mutation-implying verdicts get fortified at the closeout per master-plan §"Forward pointers to closeout" / ADR 0059.
- Closeout dependency: this fire closes the 12-task evidence corpus for T-PHASE-5-AUDIT; routines exit at step 3 thereafter (target-met). User runs `/start-engine` for the closeout interactive disposition session.

## Sampled-edge candidate findings

### HUB F — classical_logic (logic, deg 9)

#### Finding E-1
EDGE: classical_logic [domain=logic] → vagueness [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 6
SEP-ANCHORED REASONING: SEP entries on "Vagueness" / "The Sorites Paradox" — vagueness theory (epistemicism, supervaluationism, many-valued / fuzzy approaches, contextualism) is articulated as a response to challenges that classical bivalence faces with borderline cases (the bald-man / heap-of-sand sorites). Pedagogically classical bivalence (every proposition is exactly true or false) is the contrast class against which vagueness's borderline-case problem is framed; the SEP "Vagueness" entry opens by stating bivalence and then constructing the sorites against it. The migration's edge runs classical_logic → vagueness in the canonical baseline-to-departure direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-2
EDGE: classical_logic [domain=logic] → fuzzy_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 6
SEP-ANCHORED REASONING: SEP entry on "Fuzzy Logic" — fuzzy logic (Zadeh 1965 "Fuzzy Sets"; Hájek 1998 METAMATHEMATICS OF FUZZY LOGIC) departs from classical bivalence to admit graded truth-values in [0,1] and is one principal many-valued framework. Same baseline-to-departure shape as E-1: pedagogically classical bivalence is the standard against which fuzzy graded-truth is contrasted. The migration's edge runs classical_logic → fuzzy_logic in the canonical direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-3
EDGE: classical_logic [domain=logic] → explosion_principle [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 6
SEP-ANCHORED REASONING: SEP entries on "Paraconsistent Logic" / "Dialetheism" — the explosion principle (ex falso quodlibet, ECQ — from a contradiction anything follows) is a theorem of classical logic that paraconsistent logics drop. Pedagogically the principle is articulated as a feature of classical inference (typically derivable in classical natural-deduction systems via disjunction-introduction + disjunctive-syllogism), then problematized as motivation for paraconsistent alternatives. SEP exposition on paraconsistent logic opens by stating ECQ-as-classical-theorem. Direction sound — the explosion principle is taught AS A consequence OF classical logic.
VERDICT: sound
CONFIDENCE: high

#### Finding E-4
EDGE: truth_value [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 16
SEP-ANCHORED REASONING: SEP entries on "Truth Values" / "Classical Logic" — truth-values (the abstract semantic primitives T, F in two-valued classical logic; 1, 0; varying conventions) are the semantic primitives over which classical-logic connectives and derivations are defined. Pedagogically the truth-value concept must be in hand before truth-functional connectives can be specified by truth-tables. Direction sound (semantic-primitive-to-system).
VERDICT: sound
CONFIDENCE: high

#### Finding E-5
EDGE: bivalence_principle [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 16
SEP-ANCHORED REASONING: SEP entry on "Many-Valued Logic" / "Classical Logic" — bivalence (every proposition is exactly one of true / false) is one of classical logic's defining principles, alongside law-of-excluded-middle and ex-falso-quodlibet. The pedagogical relation is delicate: bivalence and classical logic are typically introduced together rather than serially (a textbook presentation states bivalence as part of stating classical logic). The migration's edge runs bivalence_principle → classical_logic, which suggests teaching bivalence first as a stand-alone principle before teaching the classical system that takes bivalence as constitutive. This is supportable on the reading "introduce the metalogical principle, then build the system that embodies it" (compare: introduce associativity before group theory). Defensible — alternative ordering (classical_logic → bivalence_principle as a defining feature) is also pedagogically legitimate and is in fact closer to how introductory logic textbooks present the material (introduce classical propositional logic, then identify bivalence as one of its features alongside truth-functionality and decidability).
VERDICT: defensible
CONFIDENCE: medium
NOTES: Same shape as the broader question of system-vs-defining-principle ordering. Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.

#### Finding E-6
EDGE: validity_logical [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 16
SEP-ANCHORED REASONING: SEP entries on "Logical Consequence" / "Classical Logic" — validity (truth-preservation across all models / interpretations) is a meta-logical concept that can be articulated in informal terms (a deductively-valid argument is one whose conclusion cannot be false when its premises are true) before any specific logical system is in hand. Pedagogically validity-as-informal-concept comes before classical-logic formalization of validity in terms of truth-functional models. The migration's edge runs validity_logical → classical_logic in the meta-concept-to-formal-system direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-7
EDGE: formal_proof [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 16
SEP-ANCHORED REASONING: SEP entries on "Proof Theory" / "Classical Logic" — formal-proof concepts (axiom, inference rule, derivation, sound proof system, completeness) generalize across logical systems (classical, intuitionistic, modal, paraconsistent). Pedagogically the formal-proof apparatus is articulated first in general terms, then specialized to specific systems. The migration's edge runs formal_proof → classical_logic in the general-apparatus-to-specific-system direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-8
EDGE: propositional_logic [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 6
SEP-ANCHORED REASONING: SEP entries on "Propositional Logic" / "Classical Logic" — propositional_logic refers in standard introductory usage to classical propositional logic (truth-tables, Boolean connectives, soundness/completeness for the classical bivalent semantics). The "classical_logic" hub node refers to the broader meta-classical position uniting propositional + predicate logic + their classical-bivalent semantics. Pedagogically propositional-logic-as-introductory-formalism comes before the meta-classical position is articulated as a stance distinct from intuitionistic / paraconsistent / many-valued alternatives. Direction sound — but reads partly as a granularity-overlap question (propositional_logic IS a part of classical logic at one level of description). See Finding N-1 for the granularity issue at the node level.
VERDICT: sound
CONFIDENCE: medium
NOTES: Defensibility of the direction is high; the medium-confidence flag tracks the granularity-overlap with the classical_logic hub-node per N-1 rather than direction concerns.

#### Finding E-9
EDGE: predicate_logic [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 6
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" — predicate_logic (first-order classical predicate logic; quantifiers, predicates, models with domains) is the second main introductory chapter after propositional_logic. Same pedagogical-direction analysis as E-8: predicate_logic-as-introductory-formalism comes before the meta-classical position is named as a stance. Direction sound; granularity-overlap with the classical_logic hub-node per N-1.
VERDICT: sound
CONFIDENCE: medium
NOTES: Same granularity-overlap pattern as E-8.

### HUB G — meaning (language, deg 9)

#### Finding E-10
EDGE: meaning [domain=language] → sense_and_reference [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entry on "Gottlob Frege" / "Sense and Reference" — Frege's 1892 "Über Sinn und Bedeutung" introduces the sense / reference distinction by refining the prior unstructured notion of "meaning" into two components: reference (Bedeutung — the object designated) and sense (Sinn — the mode of presentation). Pedagogically the unstructured meaning concept is articulated first; Frege's distinction is then introduced as a refinement that solves the morning-star / evening-star puzzle. SEP exposition runs in this direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-11
EDGE: meaning [domain=language] → proposition [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entries on "Propositions" / "Theories of Meaning" — propositions are typically introduced as the bearers of truth-value and the contents that meaningful declarative sentences express. Pedagogically the meaning concept can come first (sentences are meaningful; their meanings are propositions) OR proposition can come first (propositions as basic abstract entities; sentences express them). The migration's direction (meaning → proposition) tracks the contemporary semantics convention treating proposition as a refinement of "what a sentence means" rather than a stand-alone metaphysical primitive. Direction sound under that convention; defensibly reversed under early-Russell propositions-as-primitive readings.
VERDICT: sound
CONFIDENCE: medium
NOTES: Both directions are pedagogically defensible. Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.

#### Finding E-12
EDGE: meaning [domain=language] → use_theory_of_meaning [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entry on "Theories of Meaning" / "Meaning Holism" — the use theory of meaning (later Wittgenstein PHILOSOPHICAL INVESTIGATIONS — "the meaning of a word is its use in the language"; Brandom MAKING IT EXPLICIT) is one specific theory of what meaning is. Master-concept-to-specific-theory: pedagogically the student needs the meaning concept first to grasp what the use-theory is theorizing about. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-13
EDGE: meaning [domain=language] → verificationism [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entries on "The Verifiability Principle" / "Vienna Circle" / "Theories of Meaning" — verificationism (the meaning of a proposition is its method of verification — Carnap THE LOGICAL SYNTAX OF LANGUAGE; Ayer LANGUAGE TRUTH AND LOGIC) is one specific theory of meaning. Master-concept-to-specific-theory analogous to E-12. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-14
EDGE: meaning [domain=language] → speech_act [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entries on "Speech Acts" / "John Langshaw Austin" / "John Searle" — speech-act theory (Austin HOW TO DO THINGS WITH WORDS; Searle SPEECH ACTS; Grice "Logic and Conversation") is a semantics-pragmatics framework that builds on the meaning concept to address how utterances DO things (assert, command, promise, declare). Pedagogically the meaning concept is the foundation; speech-act theory adds the illocutionary-force layer. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-15
EDGE: meaning [domain=language] → indexical [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entry on "Indexicals" / "David Kaplan" — indexicals (context-sensitive expressions whose reference depends on the utterance context — "I", "here", "now", "this") are a specific class of expressions whose semantic treatment refines the meaning concept (Kaplan's character / content distinction). Master-concept-to-refinement; pedagogically meaning is articulated first, then the context-sensitivity refinement. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-16
EDGE: meaning [domain=language] → linguistic_relativity [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: SEP entry on "Linguistic Relativity" / "Edward Sapir" / "Benjamin Lee Whorf" — linguistic relativity (Sapir-Whorf hypothesis: the structure of one's language shapes or constrains what can be cognized or expressed) is a thesis ABOUT the relationship between language, meaning, and cognition. The relationship to the meaning concept is master-concept-to-thesis-about-it: pedagogically the student needs the meaning concept first to grasp what the relativity thesis is claiming about it. Direction sound; defensibly reversed under readings that treat linguistic-relativity as a foundational psycholinguistic claim that frames the meaning concept itself.
VERDICT: sound
CONFIDENCE: medium
NOTES: Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.

#### Finding E-17
EDGE: intentionality [domain=mind] → meaning [domain=language]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from mind to language)
SEP-ANCHORED REASONING: SEP entries on "Intentionality" / "Theories of Meaning" / "Franz Brentano" — intentionality (mental states' aboutness / directedness — Brentano 1874 PSYCHOLOGY FROM AN EMPIRICAL STANDPOINT; revived in 20th-century philosophy of mind by Husserl, Searle INTENTIONALITY) is the philosophy-of-mind-anchored aboutness category that linguistic meaning is one principal extension or analogue of. The Brentano-Husserl-Searle tradition treats mental aboutness as foundational, with linguistic meaning as derivative (linguistic items ARE meaningful because they express intentional mental states). Under that ordering the cross-bridge intentionality → meaning is canonical. The contrasting Frege-Tarski-Kripke truth-conditional / model-theoretic tradition treats linguistic meaning as foundational without invoking mental aboutness. Pedagogically either ordering is defensible; the migration's direction tracks the Brentano-Husserl-Searle ordering. Direction sound.
VERDICT: sound
CONFIDENCE: medium
NOTES: Cross-bridge from mind to language; both pedagogical orderings are canonical. Closeout fortifies medium-confidence + mutation-implying verdict.

#### Finding E-18
EDGE: philosophy_of_language [domain=language] → meaning [domain=language]
   edge_type = pedagogical_prerequisite, weight = 13
SEP-ANCHORED REASONING: philosophy_of_language is the discipline label; meaning is a concept WITHIN philosophy of language. The discipline-label-as-prereq pattern is the literal master-plan §"Audit-system-input proposals" #2 candidate (`discipline_label_node_at_root` validator soft-warn — fires when a discipline-label-shaped node has zero in-edges and serves as a prereq to multiple subdomain concepts). philosophy_of_language has zero in-edges (verified by parametric scan of the 15 Phase 5 seed migrations) and is the source of edges to meaning here AND in similar discipline-label-as-prereq positions elsewhere in the seed corpus. The edge is direction-sound trivially (a discipline contains its concepts) but the edge is structurally redundant — it does not add pedagogical content beyond "this concept lives in this field." Master-plan §T1-A verdict (g) "other" — the edge is direction-sound but pedagogically vacuous. Cross-references the master-plan §"Audit-system-input proposals" #2 directly.
VERDICT: weak
CONFIDENCE: high
NOTES: Substantive defect distinct in shape from prior reversal / historical patterns. Cross-references master-plan §"Audit-system-input proposals" #2 (discipline_label_node_at_root); see also N-3 for the parallel granularity-mismatch question on normative_ethics.

### HUB H — normative_ethics (ethics, deg 9)

#### Finding E-19
EDGE: normative_ethics [domain=ethics] → consequentialism [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entries on "Consequentialism" / "Normative Ethics" — consequentialism (the family of views holding that the moral rightness of actions is determined by the value of their consequences — utilitarianism, ethical egoism, rule-consequentialism) is one of the three principal normative-ethical theory families alongside deontology and virtue ethics. Master-concept-to-theory-family: pedagogically the student needs the normative-ethics frame (the question "what makes actions right or wrong?") before the consequentialist answer is articulated. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-20
EDGE: normative_ethics [domain=ethics] → deontology [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entries on "Deontological Ethics" / "Normative Ethics" — deontology (rightness determined by conformity to moral rules / duties — Kant; Ross THE RIGHT AND THE GOOD) is the second principal family. Same master-concept-to-theory-family relationship as E-19. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-21
EDGE: normative_ethics [domain=ethics] → virtue_ethics [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Virtue Ethics" — virtue ethics (rightness grounded in character traits — Aristotle NICOMACHEAN ETHICS; revived by Anscombe 1958 "Modern Moral Philosophy"; MacIntyre AFTER VIRTUE; Hursthouse ON VIRTUE ETHICS) is the third principal family. Same shape as E-19 / E-20. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-22
EDGE: normative_ethics [domain=ethics] → contractualism [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Contractualism" — contractualism (Scanlon WHAT WE OWE TO EACH OTHER; rooted in social-contract tradition extended to moral theory) holds that moral wrongness consists in actions that no one could reasonably reject by principles for general agreement. Master-concept-to-specific-theory: contractualism is one normative-ethical theory; pedagogically the student needs the normative-ethics frame first. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-23
EDGE: normative_ethics [domain=ethics] → ethical_egoism [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Egoism" — ethical egoism (each agent ought to promote their own interests) is one specific normative-ethical theory. Master-concept-to-specific-theory shape. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-24
EDGE: normative_ethics [domain=ethics] → divine_command_theory [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Religion and Morality" / "Divine Command Theory" — divine command theory (an action is right iff commanded by God; tied to the Euthyphro dilemma) is one specific normative-ethical theory. Master-concept-to-specific-theory shape. Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-25
EDGE: normative_ethics [domain=ethics] → moral_particularism [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Moral Particularism" — moral particularism (Dancy ETHICS WITHOUT PRINCIPLES) holds that moral judgment is not principle-governed and that moral reasons are context-sensitive. The relationship to normative ethics is partial: particularism is a meta-position about HOW normative-ethical theorizing should proceed (rejecting principle-codification), making it more meta-ethical or methodological than a first-order normative theory. Defensibly under "particularism IS a normative-ethical position alongside the codifying theories" the master-concept-to-theory shape holds; defensibly under "particularism is a metaethical / methodological view about normative-ethical theorizing" the relationship is meta-discipline-to-substantive-discipline, distinct in shape. Direction sound under either reading; defensibility-medium reflects the meta-vs-first-order ambiguity.
VERDICT: sound
CONFIDENCE: medium
NOTES: Closeout fortifies medium-confidence + mutation-implying verdict per master-plan §"Forward pointers to closeout" / ADR 0059.

#### Finding E-26
EDGE: normative_ethics [domain=ethics] → supererogation [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "Supererogation" — supererogation (acts that are morally good but not required — saintly / heroic acts) is a category of moral evaluation orthogonal to the principal normative-ethical theories; different theories accommodate it differently (Urmson 1958 "Saints and Heroes"; Heyd SUPEREROGATION; difficult for strict consequentialism). Master-concept-to-categorial-distinction: the category presupposes the normative frame (right / wrong / required / permitted / supererogatory). Direction sound.
VERDICT: sound
CONFIDENCE: high

#### Finding E-27
EDGE: morality [domain=ethics] → normative_ethics [domain=ethics]
   edge_type = pedagogical_prerequisite, weight = 7
SEP-ANCHORED REASONING: SEP entry on "The Definition of Morality" / "Normative Ethics" — morality (the ordinary concept of right and wrong, the moral domain, the set of practices and norms governing how persons ought to treat one another) is the pre-theoretical subject matter that normative ethics theorizes about. Pedagogically the student grasps the moral domain (concrete moral judgments; the felt force of moral demands; common-sense morality) before encountering systematic normative-ethical theorizing about its grounds. Direction sound.
VERDICT: sound
CONFIDENCE: high

### HUB I — vienna_circle_logical_positivism (service, deg 9)

#### Finding E-28
EDGE: vienna_circle_logical_positivism [domain=service] → verificationism [domain=language]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to language)
SEP-ANCHORED REASONING: SEP entries on "Vienna Circle" / "The Verifiability Principle" — verificationism (the meaning of a proposition is its method of empirical verification; Carnap; Ayer; Schlick) is the principal philosophical thesis advanced by the Vienna Circle in the 1920s–30s. The relation between source and target is HISTORICAL: the Vienna Circle is the historical movement; verificationism is the position they originated and advocated. Per master-plan §T1-A verdict (e) "Mis-typed: historical-not-pedagogical — the source is a historical movement, school, or thinker-framework whose relation to the target is influence, not prerequisite." The Vienna Circle is literally the named school in the §"Per-node prompt template" granularity-mismatch list ("e.g., 'Vienna Circle'"). The pedagogically-canonical direction would reverse: students learn what verificationism IS as a meaning-thesis (verifiability criterion; cognitive-significance criterion; observation-vs-theoretical distinction) before learning the historical group that originated it. The edge is mis-typed: relation type is historical_influence (Vienna Circle PROPOSED verificationism), not pedagogical_prerequisite.
VERDICT: historical
CONFIDENCE: high
NOTES: Master-plan §"Per-node prompt template" literal example for granularity-mismatch on Vienna Circle; per-node N-4 below confirms granularity-mismatch on the source. Cross-references master-plan §"Structural reopen pre-flag" for HISTORICAL_INFLUENCE PREDICATE-ACTIVATION (cumulative count further strengthened by this fire's history-terminator concentration).

#### Finding E-29
EDGE: vienna_circle_logical_positivism [domain=service] → falsificationism [domain=science]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to science)
SEP-ANCHORED REASONING: SEP entries on "Karl Popper" / "Vienna Circle" — falsificationism (Popper LOGIK DER FORSCHUNG 1934 / THE LOGIC OF SCIENTIFIC DISCOVERY 1959) is Popper's response TO and rejection OF the Vienna Circle's verificationism; Popper proposed falsifiability as the demarcation criterion in place of verifiability. The historical relation is reactive (Popper-against-Vienna-Circle), making the source-target relation historical_influence-via-opposition. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL. The pedagogically-canonical direction would teach falsificationism as a demarcation thesis directly; the Vienna Circle context is historical scene-setting, not pedagogical prerequisite. Same shape as E-28.
VERDICT: historical
CONFIDENCE: high
NOTES: Same shape as E-28; second of six service-to-X HISTORICAL-NOT-PEDAGOGICAL findings on this hub.

#### Finding E-30
EDGE: vienna_circle_logical_positivism [domain=service] → demarcation_problem [domain=science]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to science)
SEP-ANCHORED REASONING: SEP entry on "Science and Pseudo-Science" — the demarcation problem (how to distinguish science from non-science / pseudo-science) was given its modern formulation by the Vienna Circle (verifiability as demarcation criterion) and Popper (falsifiability as demarcation criterion). The historical relation is the same as E-28 / E-29: Vienna Circle is the historical movement; demarcation_problem is the philosophical question they took up. The pedagogically-canonical direction would teach the demarcation problem directly as a question in philosophy of science (the science / pseudo-science distinction; the cognitive-significance question; Popper's falsifiability proposal as one answer); the Vienna Circle context is historical scene-setting. Direction HISTORICAL-NOT-PEDAGOGICAL.
VERDICT: historical
CONFIDENCE: high
NOTES: Third of six service-to-X HISTORICAL-NOT-PEDAGOGICAL findings on this hub.

#### Finding E-31
EDGE: vienna_circle_logical_positivism [domain=service] → tarskis_t_schema [domain=logic]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to logic)
SEP-ANCHORED REASONING: SEP entries on "Alfred Tarski" / "Tarski's Truth Definitions" — Tarski's T-schema (the disquotational schema "S" is true iff S; THE CONCEPT OF TRUTH IN FORMALIZED LANGUAGES 1933) is a logico-semantic technical apparatus, distinct in shape from a Vienna-Circle-position. Tarski was at periphery of the Vienna Circle (corresponded with Carnap; influenced by them) but the T-schema is a stand-alone technical contribution that does not philosophically depend on Vienna Circle commitments. The migration's edge runs Vienna_Circle → Tarski_T_schema, suggesting historical-influence (Vienna Circle context shaped Tarski's work). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — the pedagogical direction for teaching the T-schema does not pass through the Vienna Circle; the T-schema is taught via the disquotational equivalence and the truth-definitions-for-formalized-languages technical apparatus directly.
VERDICT: historical
CONFIDENCE: high
NOTES: Fourth of six service-to-X HISTORICAL-NOT-PEDAGOGICAL findings on this hub.

#### Finding E-32
EDGE: vienna_circle_logical_positivism [domain=service] → deductive_nomological_model [domain=science]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to science)
SEP-ANCHORED REASONING: SEP entry on "Scientific Explanation" / "Carl Hempel" — the deductive-nomological (D-N) model of scientific explanation (Hempel and Oppenheim 1948 "Studies in the Logic of Explanation"; Hempel ASPECTS OF SCIENTIFIC EXPLANATION 1965) was developed by Hempel — a member of the Vienna Circle / Berlin Group tradition. The historical relation is again influence (Vienna Circle's logical-empiricist program shaped Hempel's D-N model). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL. Pedagogically the D-N model is taught directly as a covering-law account of explanation (premises = laws of nature + initial conditions; conclusion = explanandum); the Vienna Circle context is historical scene-setting, not pedagogical prerequisite.
VERDICT: historical
CONFIDENCE: high
NOTES: Fifth of six service-to-X HISTORICAL-NOT-PEDAGOGICAL findings on this hub.

#### Finding E-33
EDGE: vienna_circle_logical_positivism [domain=service] → behaviorism_logical [domain=mind]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to mind)
SEP-ANCHORED REASONING: SEP entry on "Behaviorism" — logical behaviorism (Carnap; Hempel; Ryle THE CONCEPT OF MIND for a related but more broadly-rooted variant) holds that mental-state attributions are translatable into behavioral or behavioral-disposition statements. The historical roots are within the Vienna Circle's verificationist commitment (mental-state-talk that is not behaviorally verifiable is meaningless). Same historical relation as E-28: Vienna Circle is the historical movement; logical_behaviorism is the position they (and their orbit) developed. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL. Pedagogically logical behaviorism is taught as a position in philosophy of mind (the translation thesis; its connection to verificationism; the multiple-realizability and qualia objections) directly.
VERDICT: historical
CONFIDENCE: high
NOTES: Sixth of six service-to-X HISTORICAL-NOT-PEDAGOGICAL findings on this hub. Note: 6 of 6 outgoing edges from vienna_circle_logical_positivism are historical-not-pedagogical — uniform pattern across the source-edge population.

#### Finding E-34
EDGE: aristotelian_four_causes [domain=service] → vienna_circle_logical_positivism [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Vienna Circle" / "Aristotle's Logic" — both source and target are history-terminator nodes spanning ~2300 years of philosophical history (Aristotle 4th-c. BCE; Vienna Circle 1920s–30s). The relation is school-to-school (or thinker-framework-to-school) historical succession or influence — the historical-development arc of Western philosophical thought, NOT pedagogical prerequisite. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL. Pedagogically a student does not need Aristotelian Four Causes in hand to understand Vienna Circle verificationism; the historical-context relation is history-of-philosophy curriculum scaffolding, not pedagogical-prerequisite-of-content. Inter-hub edge — counted once here under HUB I as target; cross-listed by reference under HUB J's source enumeration.
VERDICT: historical
CONFIDENCE: high
NOTES: Inter-hub edge (HUB I target / HUB J source); counted once here. Both endpoints are master-plan §"Per-node prompt template" literal granularity-mismatch examples (Vienna Circle school-name; Aristotelian Four Causes thinker-framework-name).

#### Finding E-35
EDGE: renaissance_mechanism [domain=service] → vienna_circle_logical_positivism [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Mechanism" / "Vienna Circle" — renaissance mechanism (the 16th–17th century natural-philosophy program of explaining nature through matter-in-motion: Galileo, Hobbes, Descartes, Boyle) and Vienna Circle logical positivism are both historical movements / schools. The relation is historical succession / influence (the Vienna Circle's empiricist program inherits from earlier mechanist-empiricist traditions). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL. Pedagogically Vienna-Circle commitments are taught directly without renaissance_mechanism as prerequisite.
VERDICT: historical
CONFIDENCE: high
NOTES: Both source and target are history-terminator service-domain nodes; same shape as E-34.

#### Finding E-36
EDGE: hegelian_dialectic [domain=service] → vienna_circle_logical_positivism [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Hegel's Dialectics" / "Vienna Circle" — Hegelian dialectic (thesis-antithesis-synthesis; the unfolding of Spirit through contradiction and resolution; Hegel PHENOMENOLOGY OF SPIRIT 1807) and Vienna Circle logical positivism are again historical movements. The Vienna Circle defined themselves AGAINST Hegelian / German-Idealist metaphysics — Carnap's "The Elimination of Metaphysics through the Logical Analysis of Language" (1932) explicitly targeted Heideggerian / Hegelian metaphysical statements as cognitively meaningless. The relation is historical opposition (Vienna Circle reacting against Hegelianism). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — the pedagogically-canonical Vienna-Circle teaching path does not pass through Hegelian dialectic as prerequisite.
VERDICT: historical
CONFIDENCE: high
NOTES: Both source and target are history-terminator service-domain nodes; same shape as E-34 / E-35. Notable verdict: 9 of 9 incident edges on vienna_circle_logical_positivism are HISTORICAL-NOT-PEDAGOGICAL — uniform pattern at this hub, supporting the §"Per-node prompt template" granularity-mismatch flag at the node level (N-4) and the §"Structural reopen pre-flag" HISTORICAL_INFLUENCE PREDICATE-ACTIVATION case.

### HUB J — aristotelian_four_causes (service, deg 8)

> The aristotelian_four_causes → vienna_circle_logical_positivism edge is HUB J's seventh source-edge but is recorded once at HUB I above as Finding E-34. The remaining 7 edges follow.

#### Finding E-37
EDGE: aristotelian_four_causes [domain=service] → causation [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to metaphysics)
SEP-ANCHORED REASONING: SEP entries on "Aristotle on Causality" / "Causation in Metaphysics" — Aristotle's four-causes framework (material, formal, efficient, final — PHYSICS Bk II, METAPHYSICS Bk V) is one specific historical analysis of causation, distinguished by its inclusion of formal and final causes alongside the contemporarily-recognized efficient cause. The relation is influence (Aristotle's framework is ONE historical position in the millennia-long causation debate, with Hume's regularity account, Lewis's counterfactual account, and contemporary mechanism accounts as later developments). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — the pedagogically-canonical causation teaching path does not require Aristotle's Four Causes as prerequisite; the master-plan §"Per-node prompt template" literally lists "Aristotelian Four Causes" as the granularity-mismatch example for thinker-framework-shaped nodes. Same shape as S-0119's E-43 finding (aristotelian_four_causes → causation, identical edge — verifying the shape across audit fires).
VERDICT: historical
CONFIDENCE: high
NOTES: Master-plan §"Per-node prompt template" literal example for granularity-mismatch on Aristotelian Four Causes; per-node N-5 below confirms granularity-mismatch on the source. Cross-references S-0119 hubs_1_5.md E-43 (same edge encountered when reviewing hub causation; recorded there too — but the audit-task partition records causation under HUB D at S-0119 and aristotelian_four_causes under HUB J here; the edge is incident to both. Recorded once at S-0119 E-43; this entry references the same finding).

#### Finding E-38
EDGE: aristotelian_four_causes [domain=service] → essence_metaphysical [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to metaphysics)
SEP-ANCHORED REASONING: SEP entries on "Essential vs. Accidental Properties" / "Aristotle on Definition" — essence (the metaphysical category of properties an entity must have to be the kind of thing it is — Aristotle's substantial-form notion; revived contemporarily by Fine 1994 "Essence and Modality"; Lowe THE FOUR-CATEGORY ONTOLOGY) has Aristotelian roots, but the contemporary metaphysical concept of essence is articulated as a stand-alone metaphysical category (modal essence; definitional essence; real essence) without requiring Aristotle's four-causes framework as prerequisite. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — Aristotle's framework is one historical anchor for the essence concept, not pedagogical prerequisite for it.
VERDICT: historical
CONFIDENCE: high
NOTES: Same shape as E-37; thinker-framework-to-metaphysical-concept HISTORICAL relation.

#### Finding E-39
EDGE: aristotelian_four_causes [domain=service] → scientific_explanation [domain=science]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to science)
SEP-ANCHORED REASONING: SEP entries on "Scientific Explanation" / "Aristotle on Causality" — Aristotle's four-causes framework is one historical theory of explanation; contemporary scientific-explanation theory (Hempel's D-N model; Salmon's causal-mechanical model; Kitcher's unification model; Woodward's interventionist account) is articulated as a stand-alone debate with Aristotle as historical context, not pedagogical prerequisite. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL.
VERDICT: historical
CONFIDENCE: high
NOTES: Same shape as E-37 / E-38; thinker-framework-to-philosophy-of-science-concept HISTORICAL relation.

#### Finding E-40
EDGE: aristotelian_four_causes [domain=service] → humean_regularity_theory [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight = 16 (cross-bridge from service to metaphysics)
SEP-ANCHORED REASONING: SEP entries on "David Hume" / "Causation: Regularity Theories" — Hume's regularity theory of causation (TREATISE OF HUMAN NATURE Bk I Pt III; ENQUIRY CONCERNING HUMAN UNDERSTANDING) is itself a historical-philosophical position. The edge encodes thinker-framework-to-thinker-framework: Aristotle's four-causes framework as prerequisite for Hume's regularity theory. The relation is historical succession (Aristotelian causation as the dominant view through scholasticism; Hume's empiricism rejected formal/final causes in favor of regularity-among-events). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — pedagogically Hume's regularity account can be taught directly (constant-conjunction analysis of cause; necessary-connection skepticism; the projectionist alternative) without Aristotle's framework as prerequisite. Notable: BOTH source and target are thinker-framework-shaped nodes (Aristotelian + Humean), making this the strongest case for granularity-mismatch shape on a single edge.
VERDICT: historical
CONFIDENCE: high
NOTES: Both source and target are thinker-framework-shaped (Aristotelian / Humean); same edge-shape extends granularity-mismatch from single-end-of-edge to both-ends.

#### Finding E-41
EDGE: aristotelian_four_causes [domain=service] → scholasticism [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Aristotle in the Renaissance" / "Medieval Theories of Truth" — scholasticism (the medieval philosophical-theological tradition: Aquinas, Duns Scotus, Ockham, Suárez) inherited and extended Aristotelian metaphysics + logic; the Aristotelian four-causes framework was the dominant analysis of causation throughout the scholastic period. The relation is historical succession (Aristotle's framework adopted and elaborated by scholastics) — the within-service-domain history-terminator-to-history-terminator edge encodes a historical-arc, not pedagogical prerequisite. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL.
VERDICT: historical
CONFIDENCE: high
NOTES: Within-service-domain history-terminator-to-history-terminator edge; same shape as S-0116 service audit's within-service findings (extending the cumulative HISTORICAL_INFLUENCE PREDICATE-ACTIVATION evidence band).

#### Finding E-42
EDGE: aristotelian_four_causes [domain=service] → renaissance_mechanism [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Renaissance Philosophy" / "Mechanism" — renaissance mechanism (the 16th–17th century displacement of Aristotelian formal/final causes by mechanical-philosophy explanation in terms of matter-in-motion: Galileo, Descartes, Hobbes, Boyle) is the historical successor / opponent of Aristotelian-scholastic natural philosophy. The relation is historical reaction (mechanism rejected Aristotelian formal/final causes), not pedagogical prerequisite. Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL.
VERDICT: historical
CONFIDENCE: high
NOTES: Same shape as E-41; within-service-domain history-terminator-to-history-terminator edge encoding historical reaction.

#### Finding E-43
EDGE: presocratic_naturalism [domain=service] → aristotelian_four_causes [domain=service]
   edge_type = pedagogical_prerequisite, weight = 15
SEP-ANCHORED REASONING: SEP entries on "Presocratic Philosophy" / "Aristotle's Logic" — presocratic naturalism (Thales, Anaximander, Anaximenes, Heraclitus, Empedocles, Anaxagoras, the early atomists) is the pre-Socratic Greek philosophical tradition that Aristotle himself surveyed and engaged in METAPHYSICS Bk I. The relation is historical succession (Aristotle developed his four-causes framework in part by evaluating presocratic positions). Per master-plan §T1-A verdict (e) HISTORICAL-NOT-PEDAGOGICAL — the pedagogical relation is again history-of-philosophy curriculum scaffolding, not content prerequisite.
VERDICT: historical
CONFIDENCE: high
NOTES: Within-service-domain history-terminator-to-history-terminator edge; same shape as E-41 / E-42 but in reverse historical direction (presocratic → Aristotle). Notable verdict: 8 of 8 incident edges on aristotelian_four_causes are HISTORICAL-NOT-PEDAGOGICAL — uniform pattern at this hub matching the HUB I pattern (9 of 9 historical at vienna_circle_logical_positivism). Combined HUB I + HUB J: 17 of 17 incident edges historical (with the inter-hub edge E-34 counted once per dedupe). The two history-terminator hubs concentrate the historical-not-pedagogical defects; the three concept-level hubs (classical_logic, meaning, normative_ethics) concentrate the substantive-soundness verdicts.

## Sampled-node candidate findings

### Finding N-1
NODE: classical_logic [domain=logic]
   summary (paraphrased; not verbatim per ADR 0011 / 0046 INTERPRETED-only posture): the system of logic with two truth-values (T, F), the law of bivalence, the law of excluded middle, and the principle of explosion as core commitments — contrasted against many-valued, intuitionistic, paraconsistent, and fuzzy alternatives.
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" — classical logic refers to the standard bivalent first-order logic that serves as the baseline against which non-classical logics depart. The label is concept-level appropriate: it picks out a specific logical system / family of systems with definite formal commitments (bivalence + LEM + ECQ + truth-functionality). Granularity check per master-plan §"Per-node prompt template": NOT a discipline name (compare "Logic"), NOT a school name, NOT a thinker-framework name — it's a system-level concept that students need to grasp as a whole before contrasting non-classical departures. Granularity sound. Note granularity-overlap with the constituent sub-system nodes propositional_logic and predicate_logic (per E-8 / E-9): the classical_logic node sits AT a meta-level above those constituent introductory-formalism nodes, encompassing them under a meta-classical-position label. Defensibility-medium reflects this overlap.
VERDICT: sound
CONFIDENCE: medium
NOTES: Closeout fortifies medium-confidence + mutation-implying verdict — the granularity-overlap with propositional_logic / predicate_logic is a candidate node-consolidation question (does the graph need both classical_logic AND its constituent sub-system nodes, or is one sufficient?).

### Finding N-2
NODE: meaning [domain=language]
   summary (paraphrased): the central concept in philosophy of language — what utterances, sentences, and expressions express; the subject of competing theories (truth-conditional, use-theoretic, verificationist, intentionalist, relevance-theoretic).
SEP-ANCHORED REASONING: SEP entry on "Theories of Meaning" / "Philosophy of Language" — meaning is the foundational concept of philosophy of language, with the principal theory-families competing to analyze it (truth-conditional semantics, use-theory, verificationism, conceptual-role semantics, inferentialism, speaker-meaning vs sentence-meaning vs utterance-meaning distinctions). Granularity check: concept-level, NOT a discipline / school / thinker-framework label. Granularity sound. Summary-authenticity check: the concept is named at the right level of abstraction for an introductory anchor.
VERDICT: sound
CONFIDENCE: high

### Finding N-3
NODE: normative_ethics [domain=ethics]
   summary (paraphrased): the level of ethical theorizing concerned with first-order questions about which actions are right, which character traits virtuous, which states of affairs valuable — distinguished from metaethics (second-order theorizing about the meaning, metaphysics, and epistemology of ethical claims) and applied ethics (ethical analysis of specific domains).
SEP-ANCHORED REASONING: SEP entry on "Normative Ethics" — normative ethics is one of the three principal sub-areas of moral philosophy alongside metaethics and applied ethics. The label is partially-discipline-shaped: it picks out a sub-area of theorizing (level of ethical inquiry) rather than a single concept. Granularity check per master-plan §"Per-node prompt template": at the boundary — closer to a sub-discipline label than to a first-order concept like "consequentialism" or "virtue". Compare to "metaethics" (also discipline-shaped sub-area) and "applied_ethics" (sub-area). Per master-plan §"Audit-system-input proposals" #2 candidate (`discipline_label_node_at_root`): normative_ethics has 1 in-edge (from morality), so does not strictly fire the proposed validator's zero-in-edges precondition; but the shape is similar to philosophy_of_language (per E-18) at the granularity level. GRANULARITY-MISMATCH (medium-tier — defensible as a meta-level concept that organizes the theory-space, but borderline).
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Closeout fortifies medium-confidence + mutation-implying verdict. The §"Audit-system-input proposals" #2 candidate's precondition could be loosened from zero-in-edges to "few-in-edges + many-out-edges-to-domain-concepts" to capture this shape; closeout adjudicates.

### Finding N-4
NODE: vienna_circle_logical_positivism [domain=service]
   summary (paraphrased): the early-20th-century philosophical movement centered in Vienna (1924–1936), advocating logical empiricism — verificationism, the cognitive-significance criterion, the unity of science, the rejection of metaphysics — with members including Schlick, Carnap, Neurath, Hahn, Waismann, Frank.
SEP-ANCHORED REASONING: SEP entry on "Vienna Circle" — the Vienna Circle is a historical movement / school of philosophical activity. The label is LITERALLY the master-plan §"Per-node prompt template" granularity-mismatch example for school names: "(e.g., 'Vienna Circle', 'Scholasticism')". GRANULARITY-MISMATCH high-confidence. The pedagogically-appropriate decomposition would replace the school-name node with concept-level nodes for the school's positions (verificationism, cognitive-significance criterion, unity-of-science thesis, anti-metaphysical posture) — verificationism already exists as a node in the graph (per E-13 / E-28), so the decomposition partially exists; the school-name node is the residual granularity-mismatch.
VERDICT: granularity-mismatch
CONFIDENCE: high
NOTES: Master-plan literal example. Combined with E-28 through E-36 (9 of 9 incident edges historical-not-pedagogical), this hub is a strong candidate for either retypification (to historical_influence per master-plan §"Structural reopen pre-flag") or decomposition (replace the school-name with the school's specific positions).

### Finding N-5
NODE: aristotelian_four_causes [domain=service]
   summary (paraphrased): Aristotle's analysis of four kinds of cause in PHYSICS Bk II and METAPHYSICS Bk V — material cause (the underlying matter), formal cause (the structure or essence), efficient cause (the source of change), and final cause (the end / purpose); the dominant analysis of causation through scholasticism.
SEP-ANCHORED REASONING: SEP entries on "Aristotle on Causality" / "Aristotle's Four Causes" — the Aristotelian four-causes framework is a thinker-framework-shaped concept. The label is LITERALLY the master-plan §"Per-node prompt template" granularity-mismatch example for thinker-framework names: "(e.g., 'Aristotelian Four Causes')". GRANULARITY-MISMATCH high-confidence. The pedagogically-appropriate decomposition would replace the thinker-framework label with concept-level nodes for the four cause-types (material, formal, efficient, final) — these don't currently appear as separate nodes in the graph, so the decomposition would be a structural change beyond simple retypification. Same hub-pattern as N-4: combined with E-37 through E-43 (8 of 8 incident edges historical-not-pedagogical), strong candidate for retypification or decomposition.
VERDICT: granularity-mismatch
CONFIDENCE: high
NOTES: Master-plan literal example. Combined with HUB I (N-4 + 9 historical edges) and HUB J (N-5 + 8 historical edges) — the two history-terminator hubs together account for 17 of the 43 incident edges (40%) and contribute the entirety of this fire's historical-not-pedagogical findings band.

## Syllabus traces

### TRACE 1 — gettier_problem (epistemology, BFS reverse from target)

Topo-sort prereq tree (depth-zero is the target itself; reverse BFS from gettier_problem walking source-of-edge):

```
depth 0: gettier_problem
depth 1: justified_true_belief, counterexample
depth 2: propositional_knowledge (← justified_true_belief),
         argument_logical (← counterexample), bivalence_principle (← counterexample)
depth 3: belief, truth, epistemic_justification (← propositional_knowledge),
         truth_value (← argument_logical, ← bivalence_principle)
depth 4: evidence (← epistemic_justification)
```

- Syllabus length (unique nodes including target): 11 — gettier_problem + 10 prereqs
- Max depth: 4 (evidence)
- Median depth: 2 (the bulk of the prereq mass at depths 2–3)
- Cross-domain hops along shortest paths: argument_logical (logic), bivalence_principle (logic), truth_value (logic) — three logic-domain prereqs cross-bridge into the otherwise-epistemology chain
- Questionable prereqs:
  - **counterexample at depth 1** is defensibly required (to grasp a Gettier case as a counterexample to JTB requires the counterexample concept) but it is unusual to anchor the gettier_problem chain via the counterexample concept's own logic-domain prereq trail (counterexample → argument_logical → truth_value; counterexample → bivalence_principle → truth_value). The counterexample concept is shared across logic, philosophy of science, and ethics; pedagogically introducing it via its argument-structure prereqs may be over-formalized for the gettier teaching context.
- Obvious missing prereqs the chain skips:
  - **fallibilism** (epistemology, in-graph per the soft-warn list above) is the assumption that justified beliefs can be false — Gettier cases require a justified-but-false belief to deliver luckily-true conclusions. SEP "The Analysis of Knowledge" entry treats fallibilism as a load-bearing background assumption for setting up Gettier cases. The chain has fallibilism in the graph but does NOT include it among gettier_problem's depth-1 or depth-2 prereqs. CANDIDATE MISSING PREREQ: fallibilism → gettier_problem (or gettier_problem ← fallibilism via justified_true_belief).
- Trace coherence verdict: **mostly sound but with one notable missing prereq (fallibilism)**. The depth-4 chain captures the JTB analysis decomposition + the counterexample-structure scaffolding adequately; the cross-bridge to logic via counterexample is defensible if somewhat formal. The fallibilism gap is the only candidate-missing-prereq-finding.
- Per-chain SEP citations: "The Analysis of Knowledge", "Justified True Belief", "The Gettier Problem", "Argument", "Bivalence", "Belief", "Epistemic Justification", "Truth", "Evidence", "Fallibilism".

### TRACE 2 — modal_realism (metaphysics, BFS reverse from target)

Topo-sort prereq tree:

```
depth 0: modal_realism
depth 1: possible_worlds
depth 2: modality, abstract_object, set_mathematical (cross-bridge to service domain)
depth 3: existence (← modality, ← abstract_object); set_mathematical is terminal
depth 4: ontology (← existence)
depth 5: metaphysics (← ontology)
```

- Syllabus length (unique nodes including target): 8 — modal_realism + 7 prereqs
- Max depth: 5 (metaphysics)
- Median depth: 3 (the prereq mass concentrates at depths 2–4)
- Cross-domain hops along shortest paths: set_mathematical (service domain) — bridges from metaphysics to service at depth 2; the rest of the chain stays in metaphysics
- Questionable prereqs:
  - **ontology at depth 4** and **metaphysics at depth 5** are discipline-label-shaped nodes (compare master-plan §"Per-node prompt template" example list: "Ontology", "Metaphysics"). Their presence at the top of the prereq chain effectively encodes "to teach modal realism, you need to teach the discipline label first" — discipline-label-as-prereq pattern (master-plan §"Audit-system-input proposals" #2). The chain would be tighter if it terminated at existence (depth 3) without the discipline-label-back-reference; closeout adjudicates.
- Obvious missing prereqs the chain skips: SEP "Modal Realism" / "Possible Worlds" entries center on Lewis's specific commitment to concrete realism about possible worlds (Lewis 1986 ON THE PLURALITY OF WORLDS) and the ersatz-modal-realism alternatives. The chain captures the abstract_object / set_mathematical alternatives via depth-2 but does not separately encode the actuality / concreteness distinction that Lewis's view crucially turns on. CANDIDATE MISSING PREREQ: actualism / concreteness or possibilism. (Note: ersatz_modal_realism appears as a node in the graph but is not in this chain — it would naturally be SIBLING to modal_realism rather than upstream prereq.)
- Trace coherence verdict: **sound but with discipline-label terminals**. The Lewisian + ersatz reading is captured via the abstract_object branch at depth 2; the ontology + metaphysics terminals at depths 4–5 are discipline-label-as-prereq instances flagged for closeout disposition.
- Per-chain SEP citations: "Modal Realism", "Possible Worlds", "Modality", "Abstract Objects", "Sets", "Existence", "Ontology", "Metaphysics".

### TRACE 3 — social_contract_theory (political philosophy, BFS reverse from target — substituted for absent free_speech per S-0081 gate)

Topo-sort prereq tree:

```
depth 0: social_contract_theory
depth 1: expected_value (cross-bridge to service / decision-theory),
         political_philosophy (terminal — discipline label, no prereqs in graph)
depth 2: probability_mathematical (← expected_value),
         function_mathematical (← expected_value)
depth 3: set_mathematical (← probability_mathematical, ← function_mathematical) — terminal
```

- Syllabus length (unique nodes including target): 6 — social_contract_theory + 5 prereqs
- Max depth: 3
- Median depth: 2
- Cross-domain hops along shortest paths: 4 of 5 prereqs are in the service domain (decision-theory + math foundations); only political_philosophy is in the local political domain (and it is a discipline label per the §"Audit-system-input proposals" #2 shape)
- Questionable prereqs:
  - **expected_value at depth 1** is the most striking: SEP entries on "Contemporary Approaches to the Social Contract" / "Social Contract Theory" — the social contract tradition (Hobbes LEVIATHAN; Locke SECOND TREATISE OF GOVERNMENT; Rousseau DU CONTRAT SOCIAL; Rawls A THEORY OF JUSTICE; Scanlon WHAT WE OWE TO EACH OTHER) does NOT in general presuppose expected_value or formal-decision-theoretic concepts. The decision-theoretic apparatus applies most directly to the Rawlsian veil-of-ignorance + maximin-rule strand, but Hobbes's state-of-nature reasoning, Locke's natural-rights-grounded contract, Rousseau's general-will conception, and Scanlon's reasonable-rejection contractualism do not require expected_value. Defensibly the edge targets the Rawlsian strand specifically — but as the principal depth-1 prereq for "social contract theory" as a topic, expected_value is too narrow. CANDIDATE WEAK / REVERSED: expected_value → social_contract_theory direction is defensible only on a narrow-Rawlsian reading; the canonical social-contract teaching path does NOT pass through decision-theoretic expected_value.
  - **political_philosophy at depth 1** is the discipline label; same shape as philosophy_of_language → meaning per E-18 and the master-plan §"Audit-system-input proposals" #2 candidate. WEAK / DISCIPLINE-LABEL-AS-PREREQ.
- Obvious missing prereqs the chain skips:
  - **state_of_nature** (the thought-experiment underwriting Hobbes / Locke / Rousseau / Rawls) is the canonical pedagogical antecedent. SEP entries on "Hobbes's Moral and Political Philosophy" / "Social Contract Theory" make state-of-nature the load-bearing teaching anchor.
  - **political_obligation** and **political_legitimacy** (the questions that social-contract theory is one principal answer to) — SEP "Political Obligation" entry treats consent / contract theories as one principal family of answers; pedagogically the question (what grounds political obligation? what makes political authority legitimate?) precedes the social-contract answer. Both are nodes in the graph (per the soft-warn list above).
  - **consent** / **natural_rights** are also natural pedagogical antecedents in the Lockean strand of the tradition.
- Trace coherence verdict: **partially defensible, with significant skipped antecedents**. The chain's depth-1 prereqs (expected_value, political_philosophy) are both flagged: expected_value is too-narrow (Rawlsian-decision-theoretic-only) and political_philosophy is discipline-label-as-prereq. The canonical social-contract pedagogical antecedents (state_of_nature, political_obligation, political_legitimacy) are absent from the depth-3 chain. CANDIDATE STRUCTURAL FINDING: social_contract_theory's prereq structure under-represents the political-theory pedagogical lineage and over-represents the decision-theory branch.
- Per-chain SEP citations: "Social Contract Theory", "Contemporary Approaches to the Social Contract", "Hobbes's Moral and Political Philosophy", "Locke's Political Philosophy", "Rousseau", "Rawls", "Political Obligation", "State of Nature", "Decision Theory", "Expected Value".

## Cross-cutting observations (sparse — closeout synthesizes)

Three observations from this fire that are useful as forward-pointers, recorded sparingly per master-plan §T2-D:

1. **HISTORICAL_INFLUENCE PREDICATE-ACTIVATION cumulative count further strengthened.** This fire's HUB I (vienna_circle_logical_positivism) and HUB J (aristotelian_four_causes) together produce 17 of 17 (100%) incident-edge HISTORICAL-NOT-PEDAGOGICAL findings. The S-0081 gate's structural-reopen pre-flag noted ~19 of 71 cross-bridges in this band; S-0104 cross-bridge audit confirmed 14 in cross-bridges; S-0116 service audit added within-service findings; S-0119 hubs_1_5 added 2 cross-bridge-from-history-terminator findings (E-43 + E-53). This fire extends the band by 17 hub-incident edges. Cumulative count comfortably exceeds the master-plan §"Structural reopen pre-flag" 10+ ADR-warranting threshold; closeout's expected disposition (activate `historical_influence` predicate; retype affected edges) has decisive evidence.
2. **`discipline_label_node_at_root` proposal scope: borderline cases at concept-meta-level boundary.** This fire surfaces three nodes at the discipline-label boundary: philosophy_of_language (zero in-edges, fires the proposal as currently formulated — E-18); normative_ethics (1 in-edge, doesn't fire strictly but is shape-similar — N-3); ontology and metaphysics (TRACE 2 terminals at depth 4–5; not under per-node review here but flagged). The proposal's precondition (zero in-edges) may be too narrow; closeout adjudicates whether to loosen to "few-in-edges + many-out-edges-to-domain-concepts."
3. **History-terminator hubs concentrate substantive defects; concept-level hubs concentrate substantive soundness.** This fire's split: HUB F + HUB G + HUB H (3 concept-level hubs, 27 incident edges) produced 1 weak finding (E-18, philosophy_of_language → meaning, discipline-label) — substantive-defect rate 1/27 = 3.7%. HUB I + HUB J (2 history-terminator hubs, 17 incident edges) produced 17 historical findings — substantive-defect rate 17/17 = 100%. The bimodal pattern at the hub level mirrors S-0119's hub-centrality finding (top-5 hubs predominantly sound at 87% edge-soundness) but extends with the history-terminator-hub-vs-concept-level-hub axis: concept-level hubs are even MORE sound than the S-0119 top-5 (87% vs 96%); history-terminator hubs are uniformly defective. The hub-centrality defense-side finding is HUB-SHAPE-CONDITIONAL, not flat.

## SEP citations consulted

- "Vagueness", "The Sorites Paradox", "Fuzzy Logic", "Paraconsistent Logic", "Dialetheism", "Truth Values", "Classical Logic", "Many-Valued Logic", "Logical Consequence", "Proof Theory", "Propositional Logic"
- "Theories of Meaning", "Gottlob Frege", "Sense and Reference", "Propositions", "Meaning Holism", "The Verifiability Principle", "Speech Acts", "John Langshaw Austin", "John Searle", "Indexicals", "David Kaplan", "Linguistic Relativity", "Edward Sapir", "Benjamin Lee Whorf", "Intentionality", "Franz Brentano"
- "Consequentialism", "Normative Ethics", "Deontological Ethics", "Virtue Ethics", "Contractualism", "Egoism", "Religion and Morality", "Divine Command Theory", "Moral Particularism", "Supererogation", "The Definition of Morality"
- "Vienna Circle", "Karl Popper", "Science and Pseudo-Science", "Alfred Tarski", "Tarski's Truth Definitions", "Scientific Explanation", "Carl Hempel", "Behaviorism"
- "Aristotle on Causality", "Causation in Metaphysics", "Aristotle's Four Causes", "Essential vs. Accidental Properties", "Aristotle on Definition", "David Hume", "Causation: Regularity Theories", "Aristotle in the Renaissance", "Medieval Theories of Truth", "Renaissance Philosophy", "Mechanism", "Presocratic Philosophy", "Hegel's Dialectics"
- "The Analysis of Knowledge", "Justified True Belief", "The Gettier Problem", "Fallibilism", "Belief", "Truth", "Epistemic Justification", "Evidence"
- "Modal Realism", "Possible Worlds", "Modality", "Abstract Objects", "Sets", "Existence", "Ontology"
- "Social Contract Theory", "Contemporary Approaches to the Social Contract", "Hobbes's Moral and Political Philosophy", "Locke's Political Philosophy", "Rousseau", "Rawls", "Political Obligation", "State of Nature", "Decision Theory", "Expected Value"
