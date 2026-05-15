# Seed-graph QA census evidence — shard 06

> Authored by S-0167 (routine session) per T-SEED-QA task SQA-06.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 06
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — 02441213-60b9-47ca-ac9d-ab0b5e1fda67
EDGE: Art [art, aesthetics] → Expression Theory of Art [expression_theory_art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The general concept of art is genuinely prior to a specific theory of what art is; the expression theory presupposes the explanandum.
AUDIT-TOUCHED: none

### E-2 — 77948420-72f4-4d73-a9e3-61e89303f012
EDGE: Technology Ethics [technology_ethics, ethics] → AI Ethics [ai_ethics, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: AI ethics is a sub-field of technology ethics; the broader field's framing (autonomy, responsibility, value-laden artifacts) genuinely scaffolds the narrower one.
AUDIT-TOUCHED: none

### E-3 — 9a242890-db33-4a2d-ba50-5be7f4db00c0
EDGE: Truth [truth, epistemology] → Truth-Conditional Semantics [truth_conditional_semantics, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Truth-conditional semantics analyses meaning in terms of truth conditions; the concept of truth is a strict prerequisite.
AUDIT-TOUCHED: none

### E-4 — e1d39d1e-28d7-463c-a453-9538a042b314
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Epistemic Internalism [internalism_epistemic, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Internalism is a position about the nature of justification; the learner needs the concept being theorised before the theory.
AUDIT-TOUCHED: none

### E-5 — 9b427acd-bf81-4ec7-aa0d-a877815b48e4
EDGE: Property [property, metaphysics] → Nominalism [nominalism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nominalism is the denial of universals/abstract properties; the concept of property is what the position contests, so it is prerequisite.
AUDIT-TOUCHED: none

### E-6 — 59ead684-ca85-4f15-9133-48c714a85054
EDGE: Renaissance and Early-Modern Mechanism [renaissance_mechanism, service] → Substance Dualism [substance_dualism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Cartesian substance dualism is motivated by the mechanical conception of the physical world — the mind is what the mechanistic picture leaves unaccounted for. The service-domain historical-context node is a genuine scaffolding prerequisite for the mind-domain position, matching the seed's established historical-context → position shape.
AUDIT-TOUCHED: none

### E-7 — 84b2b621-e31e-47a6-9e41-73126dca3bab
EDGE: Liberalism [liberalism, political] → Toleration [toleration, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → topic: liberalism is the broad political tradition, toleration a value/topic studied within it. Noted alternative: historically, 17th-century religious-toleration debates (Locke's Letter) predate and feed into liberalism, so a learner-history reading could run target → source. Resolved Sound on the seed's curricular field→topic convention; alternative recorded for the closeout.
AUDIT-TOUCHED: none

### E-8 — 8374f6ea-46c1-4f7b-883e-b33ae45d619c
EDGE: Art [art, aesthetics] → Formalism (Artistic) [formalism_artistic, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: As with E-1: the concept of art is prior to formalism, a specific theory locating aesthetic value in form.
AUDIT-TOUCHED: none

### E-9 — 30859bbb-330e-400f-a06d-8a4d3094b42a
EDGE: Semantic Paradox [semantic_paradox, logic] → Russell's Paradox [russell_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Russell's paradox is standardly classified as a logical/set-theoretic paradox, not a semantic one (Ramsey's distinction separates the set-theoretic family from the liar-style semantic family). Treating it as downstream of "semantic paradox" is not the canonical taxonomy. But a self-reference / diagonalisation family grouping — under which the general notion of a self-referential paradox introduces Russell's as a member — is a supportable pedagogical approach. Not a defect; flagged for the closeout's consistency review.
AUDIT-TOUCHED: none

### E-10 — 45fc17c7-2642-4cba-ba73-a284a865a66d
EDGE: Ontology of Artworks [ontology_of_artworks, aesthetics] → Fictional Truth [fictional_truth, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Fictional truth (truth-in-fiction, Lewis-style) and the ontology of artworks are largely parallel topics in aesthetics; one can treat truth-in-fiction without a settled artwork ontology. The direction is supportable — knowing what kind of thing a fictional work *is* can precede asking what is true *within* it — but it is not a tight canonical dependency.
AUDIT-TOUCHED: none

### E-11 — a4a701ef-7e5b-4655-b311-e571320e9500
EDGE: Presocratic Naturalism [presocratic_naturalism, service] → Greek Atomism [greek_atomism, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Greek atomism (Leucippus, Democritus) is a specific school within — and the late culmination of — the Presocratic naturalist project. Movement → specific-school, and historically prior. Confirmed by the node summaries, which place the Atomists inside the Presocratic list.
AUDIT-TOUCHED: none

### E-12 — b36151f3-21c9-43fc-8462-0c53745ecb28
EDGE: Social Contract Theory [social_contract_theory, political] → Political Obligation [political_obligation, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: There is a real problem-vs-solution tension here — the problem of political obligation ("why obey the state?") is the explanandum, and social contract theory is a canonical answer to it, which would favour target → source. But social contract theory also functions as the historical-canonical entry framework through which political obligation is studied in most curricula (students meet Hobbes/Locke before "political obligation" as an abstract topic with its consent/fair-play/natural-duty/associative variants). Scored Defensible on the entry-framework reading; the could-be-reversed concern is flagged prominently for the closeout.
AUDIT-TOUCHED: none

### E-13 — 869c8c6f-06ce-45fc-ab80-59e56a403af1
EDGE: Future Generations [future_generations, ethics] → Non-Identity Problem [non_identity_problem, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: The non-identity problem (Parfit) is a puzzle that arises specifically about obligations to future generations — our choices change *which* future people exist. The domain concept is a clean prerequisite for the puzzle within it.
AUDIT-TOUCHED: none

### E-14 — 49c26874-377c-44ee-ba7e-0ff3a61b5e56
EDGE: Is-Ought Distinction [is_ought_distinction, ethics] → Moral Naturalism [moral_naturalism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Moral naturalism (moral facts are natural facts) must answer Hume's is-ought challenge; the distinction is the problem that sets the stakes for the position. Direct, canonical dependency.
AUDIT-TOUCHED: none

### E-15 — 768043ef-2f2c-4eac-b2bf-65a0214f1c00
EDGE: Hegelian Dialectic [hegelian_dialectic, service] → Vienna Circle and Logical Positivism [vienna_circle_logical_positivism, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The logical positivists defined their anti-metaphysical programme largely against German idealist metaphysics; understanding Hegelian dialectic is genuine historical context for what logical positivism rejected. Both are service-domain historical nodes and the curricular sequence (German idealism before logical positivism) supports the direction.
AUDIT-TOUCHED: none

### E-16 — 2e0ed265-1d05-4520-a01e-0afae5afc766
EDGE: Paradigm (Kuhnian) [paradigm, science] → Paradigm Shift [paradigm_shift, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The concept of a paradigm is a strict prerequisite for the concept of a paradigm shift.
AUDIT-TOUCHED: none

### E-17 — 03726e5b-9427-460b-b398-55d32105a65e
EDGE: Truth-Conditional Semantics [truth_conditional_semantics, language] → Compositionality (Semantic) [compositionality_semantic, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Compositionality is a *general* constraint on any semantic theory, not specifically a truth-conditional one — which favours treating it as the more foundational, hence prior, concept (target → source). But the Davidsonian tradition is a real, citable position on which the truth-theoretic framework is the vehicle and compositionality is the property the framework secures; many semantics texts introduce truth conditions first and articulate compositionality within that frame. Scored Defensible on the Davidsonian reading; the could-be-reversed concern (target is the more general concept) is flagged for the closeout.
AUDIT-TOUCHED: none

### E-18 — 5be6fa0a-67b2-4e18-bd7a-5929e0d47147
EDGE: Political Philosophy [political_philosophy, political] → Social Contract Theory [social_contract_theory, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → topic: political philosophy is the broad field, social contract theory a major tradition within it.
AUDIT-TOUCHED: none

### E-19 — d6f311f5-7474-4ed2-aa60-5ac19771ce89
EDGE: Consciousness [consciousness, mind] → What It Is Like (Nagel) [what_its_like, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Nagel's "what it is like" is a specific gloss characterising (phenomenal) consciousness; the broad concept is prior to the specific characterisation.
AUDIT-TOUCHED: none

### E-20 — 433a0975-9101-434d-8467-698e29e17798
EDGE: Scientific Method [scientific_method, science] → Hypothetico-Deductive Method [hypothetico_deductivism, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Hypothetico-deductivism is a specific account of scientific method; general concept → specific theory.
AUDIT-TOUCHED: none

### E-21 — dd167a1a-1bd6-4c98-8d69-7e5119cf7525
EDGE: Propositional Attitude [propositional_attitude, mind] → Intentionality [intentionality, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Conceptually, intentionality is the genus (the mind's directedness/aboutness) and propositional attitudes are a species of intentional state — which favours target → source on a generality reading (and there is non-propositional intentionality too). But propositional attitudes (belief, desire) are the concrete, folk-psychologically familiar entry point that makes the abstract notion of intentionality vivid, so a concrete → abstract pedagogical order is a supportable direction. Scored Defensible; the could-be-reversed concern is flagged for the closeout. (Not audit-touched — migration 0062 flipped several propositional_attitude pairs but not this one.)
AUDIT-TOUCHED: none

### E-22 — 2e68a486-7835-40d3-93bb-db33c65ad650
EDGE: Bayesian Epistemology [bayesian_epistemology, epistemology] → Conditionalization [conditionalization, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Conditionalization is the canonical Bayesian update rule (confirmed by the conditionalization node summary); the framework is prior to its component update rule.
AUDIT-TOUCHED: none

### E-23 — d11066fa-fcaa-4fc4-ba7c-4538d6851853
EDGE: Free Will [free_will, metaphysics] → Compatibilism [compatibilism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Compatibilism is a position about free will (free will is compatible with determinism); concept/problem → position.
AUDIT-TOUCHED: none

### E-24 — 21e40287-ce41-45ef-8d51-ebb01b9cc70e
EDGE: Is-Ought Distinction [is_ought_distinction, ethics] → Error Theory [error_theory, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The is-ought distinction is genuine foundational background for metaethics broadly: the difficulty of locating moral facts in the natural world that it highlights sets up the question error theory answers negatively. The connection is less direct than is-ought → moral naturalism (E-14), but it is a legitimate prerequisite, not a defect.
AUDIT-TOUCHED: none

### E-25 — 2f163070-b62c-4adf-a143-80350048c6b9
EDGE: Set (Mathematical) [set_mathematical, service] → Quantifier [quantifier, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: The set-theoretic semantics of quantification (a domain is a set; ∀/∃ range over it) is a real connection that supports set → quantifier. But quantifiers are standardly taught in introductory logic before — or independently of — set theory, and the basic notion of "everything is F" does not conceptually require sets; the set-theoretic semantics is a later sophistication. Supportable but not a clean canonical prerequisite.
AUDIT-TOUCHED: none

### E-26 — 4cd1d7f8-6dd3-48f3-8648-23662a11bc63
EDGE: Truth Value [truth_value, service] → Principle of Bivalence [bivalence_principle, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bivalence is the principle that every proposition has exactly one of two truth values; the concept of truth value is a strict prerequisite for a principle stated about truth values.
AUDIT-TOUCHED: none

### E-27 — 72d3612c-9c0c-47fe-9d3d-ff70b0ba0021
EDGE: Mind [mind, mind] → Personal Identity [personal_identity, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Domain → topic: "Mind" is the broad domain concept, personal identity a standard topic studied within philosophy of mind. Noted: personal identity also has a metaphysical home and its bodily/biological theories do not centrally invoke the mind — but the domain→topic convention supports the direction.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — normative_ethics
NODE: Normative Ethics [normative_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks through all five theoretical families with canonical versions, key figures, and internal variation; a genuine map a learner can navigate by.
C3 (summary cold-readability): yes — opens with "first-order questions about what is right," cleanly distinguishes from metaethics and applied ethics, and itemises the families in plain terms.

### N-2 — reproductive_ethics
NODE: Reproductive Ethics [reproductive_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Thomson/Marquis/Warren each walked through with their actual arguments, plus reproductive-technology issues and reproductive justice; strong concrete foothold.
C3 (summary cold-readability): yes — enumerates the topic area and names the canonical literature; parseable with zero prior context.

### N-3 — evidentialism
NODE: Evidentialism [evidentialism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the pedagogical anchor ("justification supervenes on the mental"), positions it against reliabilism, and names the hard questions (what counts as evidence, what fitting means).
C3 (summary cold-readability): yes — the core thesis ("justification is fully determined by the believer's evidence") is stated plainly; "iff" and the "mentalism" label are mild and the prose restates the idea readably.

### N-4 — abstract_object
NODE: Abstract Object [abstract_object, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — mathematical platonism as the canonical case, nominalist alternatives named, the contested distinction flagged.
C3 (summary cold-readability): yes — defined by examples (numbers, sets, propositions) and an explicit contrast class (concrete objects); cold-readable.

### N-5 — relation
NODE: Relation [relation, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — internal vs external relations distinguished with examples, Russell vs the idealists, the current mainstream view.
C3 (summary cold-readability): yes — "a feature borne jointly by two or more entities" with examples, plus the one-place/many-place contrast with properties.

### N-6 — informed_consent
NODE: Informed Consent [informed_consent, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the five components each unpacked, the disclosure standards, the double-effect connection; substantial, navigable foothold.
C3 (summary cold-readability): yes — clear definition, the five canonical components listed, origins given; parseable cold.

### N-7 — descriptivism
NODE: Descriptivism (Theory of Reference) [descriptivism, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains *why* descriptivism was attractive (four concrete payoffs), then how Kripke's arguments turn each against it, then the contemporary defense.
C3 (summary cold-readability): yes — the core view ("names refer to whatever uniquely satisfies a description") is stated with worked illustration ("Aristotle" abbreviates "the teacher of Alexander").

### N-8 — intergenerational_justice
NODE: Intergenerational Justice [intergenerational_justice, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — climate ethics makes it concrete, then the utilitarian/Rawlsian/capabilities/sufficientarian/prioritarian frameworks each given substance, plus the non-identity complication.
C3 (summary cold-readability): yes — "fair distribution of benefits and burdens across generations" is immediately graspable; the frameworks are itemised plainly.

### N-9 — dialetheism
NODE: Dialetheism [dialetheism, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Priest's LP as the underlying logic, the liar as paradigm case, candidate dialetheia listed, the central charge and Priest's response.
C3 (summary cold-readability): yes — the central idea ("some sentences are both true AND false — true contradictions") is stated with maximum clarity; "paraconsistent logic" and "LP" follow the clear core and are not load-bearing for the basic concept.

### N-10 — counterfactual_theory_of_causation
NODE: Counterfactual Theory of Causation [counterfactual_theory_of_causation, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — foundational and refinement papers named, why the analysis is pedagogically powerful, the standard objections (preemption, absence causation) with the Suzy/Billy case.
C3 (summary cold-readability): yes — "had c not occurred, e would not have occurred either" glosses the counterfactual dependence in plain language.

### N-11 — social_epistemology
NODE: Social Epistemology [social_epistemology, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames it as an extension not a rival of individualist epistemology, names what it adds, cites Goldman's foundational treatment.
C3 (summary cold-readability): yes — "the epistemology of belief formation in social contexts" with concrete examples (testimony, peer disagreement, expertise).

### N-12 — democracy
NODE: Democracy [democracy, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — institutional taxonomy first, then the three normative theories (intrinsic/instrumental/epistemic) with figures, then the contemporary critiques; a thorough teaching map.
C3 (summary cold-readability): yes — "political authority ultimately derives from the people governed," with the institutional/normative split laid out plainly.

### N-13 — intentionalism_artistic
NODE: Intentionalism (Artistic) [intentionalism_artistic, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three positions (strong actual / moderate actual / hypothetical intentionalism) cleanly distinguished, with the live contemporary debate located between two of them.
C3 (summary cold-readability): yes — "the meaning of an artwork is fixed by the artist's intentions" is immediately clear; the named theorists scaffold rather than gate.

### N-14 — capability_approach
NODE: Capability Approach [capability_approach, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Sen's critique of competing metrics, the functionings/capabilities architecture, the Sen/Nussbaum disagreement, the practical influence (HDI).
C3 (summary cold-readability): yes — the contrast with primary goods and welfare is drawn explicitly, "capabilities" glossed as "substantive freedoms to achieve functionings."

### N-15 — presocratic_naturalism
NODE: Presocratic Naturalism [presocratic_naturalism, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames the methodological revolution (mythos → logos), gives the historical context, explains why the Presocratics matter beyond their specific cosmologies.
C3 (summary cold-readability): yes — "explaining the natural world in terms of natural principles rather than mythological narratives," with the figures named.

### N-16 — conditionalization
NODE: Conditionalization [conditionalization, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — directs teaching with a worked example before the formal rule, flags the strict-evidence assumption and the Jeffrey-conditionalization weakening, names the justifications.
C3 (summary cold-readability): no — jargon/notation-gated. The load-bearing first sentence depends on "credence" (an undefined epistemology term of art) and the conditional-probability notation "Pr_old(H | E)"; a zero-context reader cannot parse what gets updated or how. The teaching_notes themselves acknowledge this ("Teach conditionalization with a worked example before stating the rule formally"). Borderline call — "credence" is somewhat more accessible than the shard-05 ross_paradox failure ("SDL", "modal closure on disjunction-introduction") and the surrounding prose scaffolds it slightly — but applied literally against the jargon-gated criterion it fails. Flagged as borderline for the closeout.

### N-17 — causal_theory_of_reference
NODE: Causal Theory of Reference [causal_theory_of_reference, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks Kripke's baptism-and-chain setup, the semantic and modal cases descriptivism struggles with, the Putnam/Donnellan extensions, the qua-problem difficulty.
C3 (summary cold-readability): yes — "refer to their bearers via causal-historical chains: an initial baptism establishes the reference, subsequent uses inherit it" is cold-readable.

### N-18 — non_maleficence
NODE: Non-Maleficence [non_maleficence, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three distinguishing features unpacked, the doctrine of double effect with its four conditions and worked applications, the research-ethics angle.
C3 (summary cold-readability): yes — "the negative duty to refrain from harming patients — primum non nocere," explicitly contrasted with beneficence.

### N-19 — inference_to_the_best_explanation
NODE: Inference to the Best Explanation [inference_to_the_best_explanation, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — gives the IBE structure, decomposes it into the two governing questions (loveliness/likeliness; best-of-a-bad-lot), the Bayesianism relation, the realism connection.
C3 (summary cold-readability): yes — "inference from a body of observations to the hypothesis that, if true, would best explain them" is plainly parseable.

### N-20 — type_token_artworks_distinction
NODE: Type-Token Distinction (Artworks) [type_token_artworks_distinction, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Wolterstorff vs Levinson vs Goodman vs Currie laid out as the live working terrain of art-ontology, with the discovered/created divergence made vivid.
C3 (summary cold-readability): yes — borderline-positive: "the Peircean type-token distinction" is named as if known and "type-tokens of themselves" is briefly opaque, but the Beethoven-symphony illustration ("the symphony is a type, performances are its tokens; the score is a recipe") rescues the whole passage for a cold reader.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 1 (5.0%) | teaching_notes ABSENT 0

## Cross-cutting observations

- **Defensible cluster — 6/27, a notable count.** Shard 06 carries six Defensible verdicts (E-9, E-10, E-12, E-17, E-21, E-25) against shard 04's one and shard 05's four. The diary flags over-Defensible drift as a watch item, so this was examined directly: each was re-checked and confirmed as a genuine "supportable on an alternative reading, but not the canonical framing" call backed by a citable position (Davidsonian compositionality for E-17; the self-reference-family grouping for E-9; social-contract-as-entry-framework for E-12), not disguised Sound-vs-defect uncertainty. The defect count is 0 either way.
- **Three Defensibles share a "could-be-reversed: target is the more general/foundational concept" shape** — E-12 (political obligation is the explanandum social contract theory answers), E-17 (compositionality is a general constraint on any semantics, not specifically truth-conditional), E-21 (intentionality is the genus, propositional attitudes a species). None was scored Reversed because each has a real concrete-entry-point or historical-canonical-framework reading supporting the graph's direction — but the cluster is the most salient pattern in this shard and is flagged explicitly for the SQA-20 closeout's consistency review, since whether this shape should tip toward Reversed is a rubric-calibration question above an evidence session's remit.
- **C1 0.0% continues the convergence** — running C1 across shards 01–06 is 10.7% / 3.6% / 3.6% / 0.0% / 3.7% / 0.0%, the second 0-defect shard, still firmly under the production audit's 13% baseline.
- **C3 fail N-16 is a borderline jargon-gated call** — see the N-16 entry. It is the census's second C3 fail (after shard 05's N-8 ross_paradox), and like that one it is a load-bearing-first-sentence jargon problem, but "credence" sits closer to the accessibility line than shard 05's failure did; recorded as borderline for the closeout.
