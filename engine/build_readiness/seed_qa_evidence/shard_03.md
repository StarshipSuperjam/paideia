# Seed-graph QA census evidence — shard 03

> Authored by S-0161 (routine session) per T-SEED-QA task SQA-03.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 03
- Edges scored: 28
- Nodes scored: 20
- Scored: 2026-05-14

## Edge findings (C1)

### E-1 — fcb31839-1a2b-4bda-89db-13d075428c12
EDGE: Normative Ethics [normative_ethics, ethics] → Contractualism [contractualism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Normative ethics is the field; contractualism is one normative theory within it. A learner needs the general frame before a specific theory. Genus → species.
AUDIT-TOUCHED: none

### E-2 — 5230d3a4-c265-48f5-9b1d-9e626a6df54a
EDGE: Semantic Externalism [semantic_externalism, language] → Narrow Content [narrow_content, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: "Narrow content" is the notion of content that does not depend on the external factors externalism identifies; it arose as a response to externalism ("what content survives if we grant externalism?"). Understanding externalism is the motivating prerequisite.
AUDIT-TOUCHED: none

### E-3 — 7485f986-012b-45ce-ad41-8308c5d72e16
EDGE: Functionalism (Philosophy of Mind) [functionalism, mind] → Qualia Functionalism [qualia_functionalism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Qualia functionalism is functionalism applied specifically to qualia. The general theory precedes its application to a hard case.
AUDIT-TOUCHED: none

### E-4 — bbf08a72-26a8-42e0-8327-54ea46bb2c51
EDGE: Phenomenal Concept [phenomenal_concept, mind] → Phenomenal Concept Strategy [phenomenal_concept_strategy, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The phenomenal-concept strategy deploys phenomenal concepts to defend physicalism. The constituent notion (what a phenomenal concept is) precedes the strategy built on it.
AUDIT-TOUCHED: none

### E-5 — cd040501-a76f-43f1-b4b5-dbd0d9184ec8
EDGE: Computational Theory of Mind [computational_theory_of_mind, mind] → Chinese Room Argument [chinese_room_argument, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The Chinese Room is Searle's argument against strong-AI computationalism. A learner must grasp the computational theory before the argument targeting it.
AUDIT-TOUCHED: none

### E-6 — 2e42c675-e5f1-441c-8518-1fd852a9e472
EDGE: Consciousness [consciousness, mind] → Global Workspace Theory [global_workspace_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Consciousness is the explanandum; global workspace theory is one specific theory of it. General concept → specific theory.
AUDIT-TOUCHED: none

### E-7 — a464c52a-7352-4653-a97f-3e9739be16be
EDGE: Morality [morality, ethics] → Justice [justice, political]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: ... morality is the broader normative framework; political justice is a domain-specific application. Direction should be morality > justice."
VERDICT: Sound
RATIONALE: Morality is the broader normative framework; political justice is a domain-specific application. The current direction is correct.
AUDIT-TOUCHED: migration 0062 (CB-E-70 direction flip — was justice → morality; current direction matches the audit correction).

### E-8 — 5c263860-d8ca-4173-a165-73763aadc905
EDGE: Metaphysics [metaphysics, metaphysics] → Ontology [ontology, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Metaphysics is the broad field; ontology is the subdiscipline studying being and categories of existence. Field-frame → subdiscipline is the standard pedagogical order.
AUDIT-TOUCHED: none

### E-9 — a7e40636-6060-45bb-aeef-ef8c504aa6da
EDGE: Modality [modality, metaphysics] → Essence [essence_metaphysical, metaphysics]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Modern essence metaphysics (Fine, Lowe) is developed partly through modal frameworks ... modality supplies the conceptual apparatus in which contemporary essentialism is articulated."
VERDICT: Sound
RATIONALE: Modal notions (possible/necessary) are more familiar and accessible to a learner than the technical notion of essence, and contemporary essentialism is articulated through modal frameworks. Pedagogically modality precedes essence. (Fine's metaphysical-priority claim — essence explains modality — is a thesis about explanatory order, not pedagogical order; it does not reverse the edge.)
AUDIT-TOUCHED: migration 0064 (MET-E-3 evidence annotation; direction not changed by the audit).

### E-10 — bc629a26-3eed-4758-a3e5-52289a519f60
EDGE: Multiple Realizability [multiple_realizability, mind] → Multiple Realizability (Anti-Reductionist Argument) [multiple_realizability_in_science, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The general concept of multiple realizability (from philosophy of mind) precedes its specific deployment as an anti-reductionist argument in philosophy of science.
AUDIT-TOUCHED: none

### E-11 — afd3775a-4d31-4465-a9d5-0ba40820f8e9
EDGE: Four Principles of Biomedical Ethics [four_principles_bioethics, ethics] → Justice (Bioethical) [justice_bioethical, ethics]
  weight=0.95, confidence=0.95, evidence=NULL
VERDICT: Sound
RATIONALE: Justice is one of the four principles (autonomy, beneficence, non-maleficence, justice). The framework precedes the component principle within it.
AUDIT-TOUCHED: none

### E-12 — e6aaee9b-36a7-47d2-aa21-dcc1ad969fa1
EDGE: Moral Realism [moral_realism, ethics] → Moral Epistemology [moral_epistemology, ethics]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: If moral properties are real (as realism claims), the question arises how we know them; realism frames the epistemic challenge that moral_epistemology addresses as a specific dialectical position."
VERDICT: Sound
RATIONALE: Realism gives the learner a concrete substantive position whose epistemic burden — how do we access mind-independent moral facts? — moral epistemology then examines. The dependency is genuine. (A live alternative reading: moral epistemology is a broader field that does not presuppose realism, since anti-realists have their own epistemology — flagged for the closeout, but not a defect.)
AUDIT-TOUCHED: migration 0063 (ETH-E-20 — reviewed as a weak-edge candidate in the S-0122 cleanup pass and kept with an evidence justification rather than pruned).

### E-13 — 87be8066-1f11-4b24-9d30-6f5c5fb8bed5
EDGE: Probability (Mathematical) [probability_mathematical, service] → Bayesian Confirmation Theory [bayesianism_confirmation, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bayesian confirmation theory is built directly on the probability calculus (Bayes' theorem). The mathematical foundation is a clear prerequisite.
AUDIT-TOUCHED: none

### E-14 — cd9b6148-191f-4ca0-84c7-9841e38b406f
EDGE: Perdurantism [perdurantism, metaphysics] → Temporal Parts [temporal_parts, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Reversed
RATIONALE: Perdurantism is *defined* in terms of temporal parts — the view that objects persist by having temporal parts (4D worms). The constituent notion "temporal part" must be grasped before the theory that employs it; one cannot state perdurantism without it. The edge runs theory → constituent, which is backwards. Moderate-high confidence. (Alternative reading: the endurantism/perdurantism dispute is the famous debate-entry and "temporal parts" is sometimes unpacked within it — but "temporal part" is a self-standing mereological primitive used by the stage theory and general mereology too, so the constituent-concept logic dominates.)
AUDIT-TOUCHED: none

### E-15 — 784efa12-4e05-409a-b9f7-e1ae2fe79bd3
EDGE: Kantian Aesthetic Judgment [kantian_aesthetic_judgment, aesthetics] → Aesthetic Disinterest [aesthetic_disinterest, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Disinterestedness is the "first moment" of Kant's judgment of taste, and its precise technical sense is supplied by the Kantian framework — supporting source → target. But aesthetic disinterest also has a pre-Kantian lineage (Shaftesbury, Hutcheson) and is plausibly teachable as a prior building block, which would reverse the edge. A genuine both-ways call; not a defect, flagged for the closeout's consistency review.
AUDIT-TOUCHED: none

### E-16 — 98130bfa-65ea-4f8d-8a07-e4b9d3deee8d
EDGE: Aesthetic Judgment [aesthetic_judgment, aesthetics] → Kantian Aesthetic Judgment [kantian_aesthetic_judgment, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The general concept of aesthetic judgment precedes Kant's specific theory of it. Genus → species. (Forms a coherent chain with E-15: aesthetic_judgment → kantian_aesthetic_judgment → aesthetic_disinterest.)
AUDIT-TOUCHED: none

### E-17 — 3ff6199f-5939-41d6-bef1-87b087baf2e5
EDGE: Proposition [proposition, language] → Deflationary Theory of Truth [deflationary_theory_of_truth, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositions are the standard bearers of truth; understanding what a proposition is precedes a theory of what truth is (deflationism's "'p' is true iff p" presupposes the truth-bearer).
AUDIT-TOUCHED: none

### E-18 — bcaec720-c94b-4b93-8469-df4284b70ada
EDGE: Deontic Logic [deontic_logic, logic] → Chisholm Paradox [chisholm_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The Chisholm (contrary-to-duty) paradox is a puzzle internal to deontic logic. The framework precedes the puzzle that arises within it.
AUDIT-TOUCHED: none

### E-19 — ef7ef1e3-808b-46e5-8fb6-0373bd040cce
EDGE: Qualia [qualia, mind] → Qualia Realism [qualia_realism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Qualia is the concept; qualia realism is the position that qualia are real. Concept → position about the concept.
AUDIT-TOUCHED: none

### E-20 — ad4ff1cd-f36f-438d-a232-601eb7dd56e5
EDGE: Free Will [free_will, metaphysics] → Moral Responsibility [moral_responsibility, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The canonical pedagogical order: free will is taught as the prerequisite for the moral-responsibility debate (does responsibility require free will?). The reverse-priority view (start from responsibility practices) exists but is not the standard curricular order.
AUDIT-TOUCHED: none

### E-21 — 9b38ac21-08cc-45c4-8631-a8e3c464493c
EDGE: Knowledge Argument (Mary) [knowledge_argument, mind] → Property Dualism [property_dualism, mind]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Jackson's knowledge argument is an argument FOR property dualism; pedagogically the argument motivates the position, not the reverse. Direction should be knowledge_argument > property_dualism."
VERDICT: Sound
RATIONALE: Jackson's knowledge argument motivates property dualism; the motivating argument precedes the position. The current direction is correct.
AUDIT-TOUCHED: migration 0062 (MIN-E-17 direction flip — was property_dualism → knowledge_argument; current direction matches the audit correction).

### E-22 — edeba7aa-d8b9-4c4d-a6dd-adf2a02dcd4a
EDGE: Definite Description [definite_description, language] → Russell's Theory of Descriptions [russells_theory_of_descriptions, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Russell's theory is an analysis *of* definite descriptions. The phenomenon precedes the theory analyzing it.
AUDIT-TOUCHED: none

### E-23 — 5499d567-d600-4d6a-90d0-244b93d3b94b
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Virtue Epistemology [virtue_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Virtue epistemology is one approach to justification/knowledge. The general notion of epistemic justification precedes a specific theory of it.
AUDIT-TOUCHED: none

### E-24 — 97056f39-0830-4f82-a311-a57ef81e1f6e
EDGE: Deontic Logic [deontic_logic, logic] → Ross Paradox [ross_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Ross's paradox (Ob(p) seeming to entail Ob(p ∨ q)) is a puzzle internal to deontic logic. Framework → puzzle within it. (Parallels E-18.)
AUDIT-TOUCHED: none

### E-25 — 99ea07d8-ed70-4d0f-9e1b-a44ab256d0a3
EDGE: Normative Ethics [normative_ethics, ethics] → Virtue Ethics [virtue_ethics, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Virtue ethics is one of the three main normative theories. The field precedes a theory within it. (Parallels E-1.)
AUDIT-TOUCHED: none

### E-26 — f2200ba7-9b10-487f-8a62-debeb50a80a8
EDGE: Sentientism [sentientism, ethics] → Animal Ethics [animal_ethics, ethics]
  weight=0.9, confidence=0.9, evidence="Per S-0122 audit: sentientism (Bentham, Singer) is foundational; animal ethics derives FROM the sentience criterion. Direction should be sentientism > animal_ethics."
VERDICT: Sound
RATIONALE: Sentientism (the sentience criterion for moral status) is foundational; animal ethics derives from it. The current direction is correct.
AUDIT-TOUCHED: migration 0062 (ETH-E-16 direction flip — was animal_ethics → sentientism; current direction matches the audit correction).

### E-27 — ca7baa2a-e0f5-42ba-9115-27a0fe95d34f
EDGE: Kripke Semantics [kripke_semantics, logic] → Formal Epistemology [formal_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Kripke semantics is the model-theoretic framework for modal logic; epistemic logic is one application of that framework. Direction should be kripke_semantics > formal_epistemology."
VERDICT: Sound
RATIONALE: Kripke semantics is the model-theoretic framework underlying modal/epistemic logic; the current direction is correct. Sub-observation for the closeout: the audit's rationale targets *epistemic logic* specifically, but the target node "Formal Epistemology" is broader (it also covers Bayesian epistemology and formal learning theory, which do not depend on Kripke semantics) — a minor scope mismatch, not a direction defect.
AUDIT-TOUCHED: migration 0062 (CB-E-55 direction flip — was formal_epistemology → kripke_semantics; current direction matches the audit correction).

### E-28 — 083f0389-dbe4-42fa-87c5-116aaed98b84
EDGE: Underdetermination of Theory by Data [underdetermination, science] → Duhem-Quine Thesis [duhem_quine_thesis, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Underdetermination is the general epistemological problem (multiple theories fit the data); the Duhem-Quine thesis is a specific holist source/version of it (hypotheses tested in bundles). Genus → species. (A defensible alternative teaches Duhem-Quine first as the mechanism that generates underdetermination, but the general-concept-then-specific-version order is standard.)
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — propositional_knowledge
NODE: Propositional Knowledge [propositional_knowledge, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains *why* epistemology centers propositional knowledge (the JTB components are independently tractable) and names the contested propositional/procedural distinction with the Stanley & Williamson reduction. A genuine angle, not a restatement.
C3 (summary cold-readability): yes — "knowing-that" gloss plus the JTB-plus-Gettier framing is parseable; "Gettier-resistant condition" is mild jargon but the core claim survives without it.

### N-2 — natural_rights
NODE: Natural Rights [natural_rights, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens with the concrete Lockean argument, names the grounding question, supplies canonical critiques (Bentham, Marx, MacIntyre) and the connection to contemporary human rights. Rich, worked foothold.
C3 (summary cold-readability): yes — defines the concept plainly ("pre-political moral entitlements held by all persons in virtue of their nature") and anchors it historically. A cold reader can extract what it is.

### N-3 — sovereignty
NODE: Sovereignty [sovereignty, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens with the Bodinian definition and unpacks each property, then a battery of canonical distinctions and the contemporary contestation. Strong traction.
C3 (summary cold-readability): yes — "supreme political authority within a defined territory or population" is immediately clear; historical anchoring (Bodin, Hobbes, Westphalia) supports it.

### N-4 — concrete_object
NODE: Concrete Object [concrete_object, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "best taught as the unmarked default — the kind of thing students already think exists — set against the abstract-object foil," and names the downstream disputes (persistence, mereology, identity). A genuine pedagogical strategy.
C3 (summary cold-readability): yes — concrete examples (this rock, that person, the moon) and the abstract-object contrast make it cold-readable.

### N-5 — just_war_theory
NODE: Just War Theory [just_war_theory, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — exhaustive worked treatment: all jus ad bellum / jus in bello criteria spelled out, the McMahan-vs-Walzer dispute, contemporary stress-test cases. Very strong foothold.
C3 (summary cold-readability): yes — the jus ad bellum / jus in bello structure is stated plainly with the Latin glossed in plain English.

### N-6 — time
NODE: Time [time, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "Frame the metaphysics of time around McTaggart's A/B-series distinction," then unpacks A-series/B-series and the A-theorist/B-theorist dispute, and separates metaphysics-of-time from physics-of-time. Genuine angle.
C3 (summary cold-readability): yes — frames the metaphysical questions in plain terms (is time real or a structuring feature of cognition; what is its directionality; tense vs tenseless ordering) without undefined jargon.

### N-7 — positive_rights
NODE: Positive Rights [positive_rights, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — conceptual distinction, canonical objections, standard replies, the socialist/capability traditions, Marshall 1950. Worked, multi-angle foothold.
C3 (summary cold-readability): yes — "rights that require positive action by others or by the state to provide goods or services," with concrete examples and the negative-rights contrast.

### N-8 — reference
NODE: Reference [reference, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "Use Frege's 1892 puzzle to motivate the topic" — a concrete worked entry point (Hesperus/Phosphorus), then sense/reference, descriptivism vs causal theory, and downstream consequences. Strong traction.
C3 (summary cold-readability): yes — defines reference as the expression-to-world relation with concrete sub-cases (names→individuals, predicates→properties); the post-Frege determination question is stated clearly.

### N-9 — inverted_spectrum
NODE: Inverted Spectrum [inverted_spectrum, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — history, an explicit 5-step argument structure, the standard responses keyed to specific steps (Shoemaker, Harman, Block), and a pairing with the absent-qualia argument. Strong foothold.
C3 (summary cold-readability): yes — the thought experiment is described concretely (functional duplicates, inverted color experience, both call tomatoes "red") and the anti-functionalist payload is stated plainly.

### N-10 — ontology_of_artworks
NODE: Ontology of Artworks [ontology_of_artworks, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "Use the multiple-instances puzzle as entry," with a concrete contrast (painting destroyed vs symphony surviving), the standard taxonomy, and the contemporary Platonist/creationist/nominalist/structural debate. Genuine angle.
C3 (summary cold-readability): yes — states the question plainly and immediately illustrates with the radically-different-ontological-categories observation (painting vs symphony vs novel vs photograph).

### N-11 — higher_order_thought_theory
NODE: Higher-Order Thought Theory [higher_order_thought_theory, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the view's structure laid out (1)(2)(3), its elegant features, the standard challenges (misrepresentation, animal/infant HOTs), and the HOP pairing. Worked foothold.
C3 (summary cold-readability): yes — the concrete "conscious pain = pain plus the thought that one is in pain" example makes the abstract HOT thesis cold-readable.

### N-12 — epistemicism
NODE: Epistemicism [epistemicism, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames it as "the most metaphysically conservative response to vagueness," names the cost, and walks Williamson's three-part defense (safety, margin-for-error, meaning-by-use). Dense but a real worked angle.
C3 (summary cold-readability): yes — the heap example (some specific n where n grains is a heap and n−1 is not, unknowable in principle) makes the sharp-but-unknowable-cutoff claim concrete.

### N-13 — scientific_model
NODE: Scientific Model [scientific_model, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "Walk students through the diversity of scientific models" with four concrete categories and named examples (Hardy-Weinberg, double-helix, climate models, ideal gas), then the semantic/model-theoretic view. Excellent foothold.
C3 (summary cold-readability): yes — "a representation of a target system used in scientific reasoning" is plainly stated; "syntactic conception of theories" is mild jargon but the core survives without it.

### N-14 — b_theory_of_time
NODE: B-Theory of Time [b_theory_of_time, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — states the package (eternalism, tensed-to-tenseless reduction with a concrete translation example, no privileged present), the alignment with relativity and perdurantism, and the critics' charge. Genuine angle.
C3 (summary cold-readability): yes — borderline: it opens on "B-series," but glosses it inline ("the tenseless ordering of events by earlier-than/later-than/simultaneous-with"), so a motivated cold reader can extract the view. One of the closer-to-the-line summaries in this shard.

### N-15 — coherentism
NODE: Coherentism [coherentism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — short but pointed: names the two load-bearing problems (specifying what coherence amounts to; the input objection) and the pedagogically useful BonJour arc (defense then abandonment). Real traction.
C3 (summary cold-readability): yes — clear and even vivid ("the web replaces the pyramid").

### N-16 — negative_rights
NODE: Negative Rights [negative_rights, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — conceptual distinction, the two stock priority arguments (enforceability, demandingness), the canonical objections, and the human-rights-instruments framing. Worked foothold.
C3 (summary cold-readability): yes — "rights that require only forbearance from others — duties of non-interference," with concrete examples and the positive-rights contrast.

### N-17 — truth_correspondence
NODE: Correspondence Theory of Truth [truth_correspondence, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — short, but gives a real angle: teach it as the default baseline, and here are the pressure points critics target (what is a fact? how does a sentence correspond?). Not a restatement.
C3 (summary cold-readability): yes — "a proposition is true when it corresponds to a fact about the world" is about as plain as a truth-theory summary can be.

### N-18 — counterfactual_conditional
NODE: Counterfactual Conditional [counterfactual_conditional, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names the three domains where counterfactuals do work (causal, historical, metaphysical reasoning), the Stalnaker/Lewis closest-world theory, the non-monotonicity example, and the impossible-antecedent wrinkle. Strong foothold.
C3 (summary cold-readability): yes — concrete examples ("if it were raining, the streets would be wet"), the explicit argument for why it cannot be the material conditional, and the closest-world analysis stated plainly.

### N-19 — consciousness
NODE: Consciousness [consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "Distinguish consciousness from related notions students often conflate" with three concrete distinctions, then the analytic entry points (Block, Chalmers, Nagel) and the phenomenological tradition. Genuine pedagogical angle.
C3 (summary cold-readability): yes — "there is something it is like to undergo them" is the standard gloss and is intelligible to a cold reader; the example list grounds it.

### N-20 — historical_theory_of_art
NODE: Historical Theory of Art [historical_theory_of_art, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "the cleanest entry to lineage-based accounts," with four numbered strengths and three numbered weaknesses. Worked, balanced foothold.
C3 (summary cold-readability): yes — borderline: Levinson's definition ("intended for regard-as-a-work-of-art in some way that earlier-recognized art has been correctly regarded") is a dense mouthful, but the following sentences unpack it (recursive, historical, recursion bottoms out in the Ur-arts). A motivated cold reader gets there. Among the closer-to-the-line summaries in this shard.

## Shard tally
- Edges: 28 total | Reversed 1 | Weak-redundant 0 | defective 1 (3.6%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0

## Cross-cutting observations (optional)
- C1 defect rate 3.6% (1/28) matches shard 02 exactly and sits well below shard 01's 10.7% and the production audit's 13% baseline. The single defect (E-14 perdurantism → temporal_parts) is the recurring "theory placed before its defining constituent" shape that S-0158 also saw (E-26 knowledge_how → knowledge); the closeout should check whether this shape clusters.
- Six of the 28 edges are audit-touched (E-7, E-9, E-12, E-21, E-26, E-27); all six verified Sound, i.e. this shard re-confirmed every S-0122 audit decision it sampled — zero re-openings.
- Node quality is uniformly high: 0% C2 fail, 0% C3 fail across 20 INTERPRETED/active nodes. N-14 (b_theory_of_time) and N-20 (historical_theory_of_art) were the only C3 summaries near the line — both open on a dense technical formulation but rescue it with an inline gloss or immediate unpacking. Flagged so the closeout can check C3-threshold consistency against shards that did fail summaries.
