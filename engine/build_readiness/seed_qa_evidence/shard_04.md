# Seed-graph QA census evidence — shard 04

> Authored by S-0164 (routine session) per T-SEED-QA task SQA-04.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 04
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-14

## Edge findings (C1)

### E-1 — 44a9099c-74f4-4314-9bc9-70927fcc3060
EDGE: Proposition [proposition, language] → Truth-Conditional Semantics [truth_conditional_semantics, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Truth-conditional semantics holds that sentence meaning is given by truth conditions; propositions are the truth-bearers it trades in. A learner needs the truth-bearer concept before the theory built on it. The reverse is not more compelling — propositions are the more basic notion.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-2 — 70024ccf-5375-4542-b16a-873ed730cf11
EDGE: Existence [existence, metaphysics] → Property [property, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Existence/being is the most general metaphysical frame; property is one specific ontological category populating that frame. Genus-frame → category. (Alternative reading: "property" is independently graspable and arguably co-equal foundational — but it is not the prerequisite OF existence, so the direction is not a defect either way.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-3 — 82652012-87dd-473d-b3eb-407f54ec1bcb
EDGE: Mental State [mental_state, mind] → Mental Causation [mental_causation, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mental causation is the problem of how mental states cause physical events and one another. The constituent concept (what a mental state is) must precede the problem stated in terms of it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-4 — 58c9c803-1da3-46d1-8e4c-a2c5d71acfaa
EDGE: Applied Ethics [applied_ethics, ethics] → Environmental Ethics [environmental_ethics, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Environmental ethics is a branch of applied ethics. Field → subfield, the standard pedagogical order.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-5 — deab045d-96a5-4f07-9ff4-aab31c5f37c2
EDGE: Axiom (Mathematical) [axiom_mathematical, service] → Formal Proof [formal_proof, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: A formal proof is a sequence derived from axioms via inference rules. The concept of an axiom is a clear definitional prerequisite for formal proof.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-6 — d73e7065-7720-4d02-bd4f-65645b73f680
EDGE: Existence [existence, metaphysics] → Substance [substance, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Substance is a specific category of being — that which exists independently and bears properties. Existence (being in general) → substance (a kind of being). Genus → species.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-7 — 8356ace1-2e6a-49b9-a0c5-4ef4d0f557c0
EDGE: Philosophy of Science [philosophy_of_science, science] → Scientific Method [scientific_method, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The philosophy_of_science node's own summary lists "what scientific method is and whether there is one" as a central question of the field; scientific_method is a topic studied within it. Field → topic, consistent with the seed's genus→species convention (cf. E-4, E-9, E-11, E-17, E-18). Sub-observation for the closeout: a real alternative reading runs scientific_method → philosophy_of_science (the concrete practice is familiar first; philosophical reflection follows) — flagged for consistency review, not scored a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-8 — 5b9a89b4-8d06-4e6a-8779-6d0b29ca62c7
EDGE: Free Will [free_will, metaphysics] → Incompatibilism [incompatibilism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Incompatibilism is the position that free will is incompatible with determinism. The concept of free will precedes a specific position about it. Concept → position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-9 — 4e11ee9b-c750-4329-9423-a97f00bf8836
EDGE: Mereology [mereology, metaphysics] → Composition (Mereological) [composition_mereological, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mereology is the general theory of parts and wholes; composition is a core relation/question (the special composition question) within it. Field/theory → core notion. (Mereology takes parthood as primitive and defines composition from it, reinforcing the direction.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-10 — 713a97a3-aa9b-4d48-a2f1-4729206604c6
EDGE: Persistence [persistence, metaphysics] → Endurantism [endurantism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Persistence is the question of how objects persist through time; endurantism is one answer (objects are wholly present at each time). Topic → specific theory of it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-11 — 33e2185b-4c9f-4675-acfd-8e0fef4b0150
EDGE: Philosophy of Language [philosophy_of_language, language] → Reference [reference, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Reference is a core topic of philosophy of language. Field-frame → topic, the standard order.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-12 — 1ade7af7-04d1-43f1-a9ce-039236dd265d
EDGE: Conditional Probability [conditional_probability, service] → Conditionalization [conditionalization, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Conditionalization (Bayesian updating: new credence = prior conditional probability) is defined directly on conditional probability. A clear definitional prerequisite. Cross-domain (service → epistemology), which is expected for a service-tier mathematical primitive feeding a philosophical application.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-13 — a8534bb6-a258-4540-a6ad-bed42382c640
EDGE: Liberty (Political) [liberty_political, political] → Republicanism [republicanism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The neo-Roman republican tradition (Pettit, Skinner) is centrally a theory about liberty — liberty as non-domination. The concept of political liberty precedes the theory that reconceives it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-14 — 44319f52-edfa-48a1-bb97-c73013bffddd
EDGE: Bioethics [bioethics, ethics] → End-of-Life Ethics [end_of_life_ethics, ethics]
  weight=0.85, confidence=0.85, evidence=NULL
VERDICT: Sound
RATIONALE: End-of-life ethics is a subfield of bioethics. Field → subfield.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-15 — 490d9753-7886-4e57-a241-f11d858f1092
EDGE: Political Authority [political_authority, political] → Democracy [democracy, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Political authority is the general question of the right to rule and its legitimacy; democracy is one account of how authority is legitimated. General question → specific answer. (Alternative: democracy is concrete and familiar and could be taught first — noted, not a defect.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-16 — 0d79a611-a79c-42ab-be58-55dc26048670
EDGE: Environmental Ethics [environmental_ethics, ethics] → Climate Ethics [climate_ethics, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Sound
RATIONALE: Climate ethics is a subfield of environmental ethics. Field → subfield. Forms a coherent chain with E-4: applied_ethics → environmental_ethics → climate_ethics.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-17 — b6737329-cf61-4967-b9bf-0443274085bc
EDGE: Numerical Identity [numerical_identity, metaphysics] → Mereology [mereology, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Numerical identity (being one and the same thing) is a foundational metaphysical primitive; mereological theses are stated in terms of it (extensionality of parthood: same parts → identical; composition as identity). The primitive notion precedes the theory that deploys it. Forms a chain with E-9: numerical_identity → mereology → composition_mereological.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-18 — b926bfe3-0a26-4a90-8ed8-ceee1919cbbe
EDGE: Metaethics [metaethics, ethics] → Moral Realism [moral_realism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Metaethics is the field; moral realism is one position within it. Field → position.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-19 — 24c9b062-e74f-4f68-8aea-6b3ce9a1b0af
EDGE: Philosophy of Language [philosophy_of_language, language] → Meaning (Linguistic) [meaning, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Meaning is a core topic of philosophy of language. Field-frame → topic. (Parallels E-11.)
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-20 — 67c76e24-a6ac-40e7-8c9a-a3f231c8d0c6
EDGE: Material Conditional [material_conditional, logic] → Indicative Conditional [indicative_conditional, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: In the standard logic curriculum the material conditional is introduced first as the truth-functional connective; the indicative conditional is the later, harder topic, engaged via the puzzle of whether the material conditional captures natural-language "if...then" (the paradoxes of material implication). Curricular order is material → indicative. Sub-observation for the closeout: a phenomenon-before-theory reading would run indicative → material — but the material conditional is a logical primitive, not primarily "a theory of" the indicative conditional, so the standard order dominates.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-21 — ad72a33c-73a3-42c3-9454-9b1205cc4dd2
EDGE: Speech Act [speech_act, language] → Gricean Maxims (Cooperative Principle) [gricean_maxims, language]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Speech act theory (Austin 1955, Searle 1969) and Gricean conversational implicature (Grice 1975) are somewhat-parallel developments in pragmatics rather than a tight prerequisite chain — one can teach the cooperative principle without speech act theory and vice versa. The direction is supportable: speech acts supply the "utterances as actions" frame the maxims regulate, and pragmatics curricula often run speech acts → implicature. But it is not the canonical tight dependency. Not a defect.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-22 — 23854189-3835-49ec-996e-1f4d68dd6892
EDGE: Intellectual Virtue [intellectual_virtue, epistemology] → Virtue Responsibilism [virtue_responsibilism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Virtue responsibilism is the strand of virtue epistemology centered on intellectual virtues as responsibly-acquired character traits. The constituent concept (intellectual virtue) precedes the position deploying it.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-23 — 3792b4d8-2c1e-4833-92ed-3333d5668932
EDGE: Art [art, aesthetics] → Historical Theory of Art [historical_theory_of_art, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The historical theory of art (Levinson) is one theory of what art is. The concept "art" precedes a specific theory of it. Concept → theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-24 — d4c77e5a-b613-48d6-a975-3976b5f9aeb8
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Evidentialism [evidentialism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Evidentialism is the theory that justification is determined by evidence. The general concept of epistemic justification precedes a specific theory of it. Concept → theory.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-25 — 6ed9a87b-fb0f-4973-acd0-64c82e623494
EDGE: Composition (Mereological) [composition_mereological, metaphysics] → Mereological Nihilism [mereological_nihilism, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Mereological nihilism is the view that composition never occurs (there are no composite objects). The concept of composition precedes the position denying it ever happens. Concept → position. Completes the chain mereology → composition_mereological → mereological_nihilism.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-26 — 0d72b015-7b64-493b-b424-83a1ecf24754
EDGE: Function (Mathematical) [function_mathematical, service] → Expected Value [expected_value, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Expected value is defined as a function — a weighted sum (or integral) over the values of a random variable, itself a function. A genuine definitional prerequisite. Sub-observation: probability (a random-variable / probability-measure notion) is arguably the MORE proximate prerequisite; if a probability→expected_value edge also exists in the graph this would be a Weak-redundant long-distance shortcut — but that cannot be confirmed from the shard, so scored Sound.
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

### E-27 — 4d7209b5-f899-4475-a2dd-ac0edf009893
EDGE: Material Conditional [material_conditional, logic] → Curry's Paradox [curry_paradox, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Curry's paradox arises from the conditional (with contraction) — "if this sentence is true, then [arbitrary claim]." The connective precedes the paradox that arises from it. Framework → puzzle within it (parallels the deontic-logic→paradox edges in shard 03).
AUDIT-TOUCHED: none
EVIDENCE NOTE: absent

## Node findings (C2 + C3)

### N-1 — state_political
NODE: State (Political) [state_political, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — opens with the Weberian definition and unpacks each element (territorial, monopoly, legitimate, force), locates the state historically (early-modern Europe, Westphalia 1648, decolonization), and names three contemporary debates. Rich, worked foothold.
C3 (summary cold-readability): yes — the Weberian "territorial organization that claims a monopoly on the legitimate use of physical force" is the standard, intelligible gloss; the contrast with earlier political forms grounds it for a cold reader.

### N-2 — beneficence
NODE: Beneficence [beneficence, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names the Hippocratic-tradition core, the beneficence/autonomy tension, the soft/hard paternalism distinction, and the rescue-case calibration. Multi-angle foothold.
C3 (summary cold-readability): yes — "the principle imposing positive duties to benefit patients" is plainly stated and the contrast with non-maleficence ("the negative duty to refrain from harming") is explicit.

### N-3 — russells_theory_of_descriptions
NODE: Russell's Theory of Descriptions [russells_theory_of_descriptions, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "a textbook case of philosophical logical analysis," with three numbered motivations (Meinong's puzzle, excluded middle, substitution failure) and the wide/narrow scope distinction. Strong worked angle.
C3 (summary cold-readability): yes — gives the actual paraphrase ("there is one and only one thing that is F, and that thing is G"), which makes the abstract claim concrete for a cold reader.

### N-4 — easy_problems_of_consciousness
NODE: Easy Problems of Consciousness [easy_problems_of_consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains why the easy problems are "easy" (their solutions consist in specifying mechanisms), names where empirical progress has been made, and gives the physicalist response. Genuine angle.
C3 (summary cold-readability): yes — concrete examples (discriminating stimuli, integrating information, controlling behavior) and the explicit gloss that "easy" means "we know what kind of explanation would solve them." The reference to "the hard problem" is mild jargon but the summary survives without resolving it.

### N-5 — set_mathematical
NODE: Set (Mathematical) [set_mathematical, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames set theory by its characteristic operations (membership, subset, union, intersection, complement, cardinality), gives the ZFC history and the paradox motivation. Excellent foothold.
C3 (summary cold-readability): yes — "a collection of distinct objects... considered as a single object in its own right" is immediately clear; extensional characterization is glossed plainly.

### N-6 — biocentrism
NODE: Biocentrism [biocentrism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — lays out the argumentative move (extending moral status by the "good of its own" criterion), the attractive and counterintuitive implications, Taylor's responses, and the cross-bridges to deep ecology and animal ethics. Very rich.
C3 (summary cold-readability): yes — "all individual living things possess intrinsic moral value" is plain; Schweitzer's "reverence for life" and Taylor's four core beliefs anchor it concretely.

### N-7 — philosophy_of_science
NODE: Philosophy of Science [philosophy_of_science, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — six numbered central questions (method, confirmation, explanation, realism, change, values), each with a canonical literature. A genuine map of the field.
C3 (summary cold-readability): yes — the field is framed by its questions in plain terms ("what scientific method is and whether there is one, what scientific theories are and how they relate to evidence") with no undefined jargon.

### N-8 — anti_intentionalism
NODE: Anti-Intentionalism [anti_intentionalism, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes the two strands of the Wimsatt-Beardsley argument (epistemic, semantic), shows how critics target each, and names the contemporary synthesis. Worked foothold.
C3 (summary cold-readability): yes — "an artwork's meaning is fixed by features and conventions independent of the artist's intentions" is plainly stated; the Intentional Fallacy reference is glossed.

### N-9 — qualia_eliminativism
NODE: Qualia Eliminativism [qualia_eliminativism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Dennett's argument, the crucial clarification that the position is not denial that experience exists, Frankish's illusionism, the standard objections, and a pedagogical caution. Strong.
C3 (summary cold-readability): yes — "qualia... do not exist — what we introspect... is something else" is clear; the parenthetical list of qualia's conceived features (intrinsic, ineffable, private) is mildly technical but does not gate the core claim.

### N-10 — truth_value
NODE: Truth Value [truth_value, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes two questions students conflate (what kinds of values sentences take vs what truth IS) and shows the choice drives the choice of logic. Real angle.
C3 (summary cold-readability): yes — "the value (typically true or false) that a sentence or proposition takes under an interpretation" is plain; the many-valued examples extend rather than gate it.

### N-11 — fallibilism
NODE: Fallibilism [fallibilism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — borderline (short), but not a restatement: it names a genuine consequence (the closure puzzle) and why it matters ("different responses reveal one's broader epistemological commitments"). Brief but gives a real angle. Flagged for the closeout's consistency review of short teaching_notes.
C3 (summary cold-readability): yes — "one can know that p even though one's grounds for p do not entail p — knowledge does not require certainty" is concise and immediately intelligible.

### N-12 — scientific_realism
NODE: Scientific Realism [scientific_realism, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three components of realism, the antirealism contrasts, the two central arguments (no-miracles, pessimistic meta-induction), and the contemporary refinements. Very rich.
C3 (summary cold-readability): yes — "mature scientific theories are (approximately) true... their theoretical terms refer to real entities... science makes genuine cumulative progress" is plain and well-structured.

### N-13 — explanatory_gap
NODE: Explanatory Gap [explanatory_gap, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — locates Levine's claim as weaker than Chalmers's, distinguishes type-A and type-B materialist responses, and notes why the gap is the cleanest entry to the hard problem. Genuine angle.
C3 (summary cold-readability): yes — the concrete gloss ("even if we knew all the physical facts about pain, we would not understand why pain feels the way it does") makes the thesis cold-readable.

### N-14 — computational_theory_of_mind
NODE: Computational Theory of Mind [computational_theory_of_mind, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishes three claims often run together (hardware, process, functional), names Fodor's strong language-of-thought version, and lists the standard challenges. Worked foothold.
C3 (summary cold-readability): yes — "the mind is a computational system — mental processes are computations defined over mental representations, and the brain is the hardware that implements those computations" is plainly stated.

### N-15 — fictional_truth
NODE: Fictional Truth [fictional_truth, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Walton's make-believe framework, the primary/secondary fictional-truth distinction, Lewis's modal alternative, and where the two frameworks make different predictions. Strong.
C3 (summary cold-readability): yes — the concrete Sherlock Holmes example ("true IN the story that Holmes lives at 221B Baker Street") makes the phenomenon immediately graspable.

### N-16 — philosophy_of_mind
NODE: Philosophy of Mind [philosophy_of_mind, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames the field by its central tension (mental phenomena seem both part of nature and recalcitrant to natural methods) and names the contemporary analytic lineage. Genuine angle.
C3 (summary cold-readability): yes — "the nature of mental phenomena: their relation to the physical world, the structure of conscious experience..." is a plain enumeration with no undefined jargon.

### N-17 — illusionism
NODE: Illusionism (about Consciousness) [illusionism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the view's three-part structure, how it differs from Dennett's version, the standard objections (self-undermining, empirical adequacy), and the defenders' replies. Strong.
C3 (summary cold-readability): yes — "phenomenal consciousness is an introspective illusion" is plainly stated and the next sentence unpacks the mechanism in plain terms.

### N-18 — temporal_parts
NODE: Temporal Parts [temporal_parts, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the concrete road-analogy ("a road's lifetime has temporal parts — the road in 1950, the road in 2025"), names the contestation, and cites Sider's systematic defense. Good foothold.
C3 (summary cold-readability): yes — borderline: the summary opens on "the constituents of a perduring four-dimensional object," which is jargon-gated, but immediately rescues it with the cold-reader-friendly gloss "analogs of spatial parts, but along the temporal dimension" and names the perdurantism/endurantism debate. A motivated cold reader gets there. Among the closer-to-the-line summaries in this shard.

### N-19 — moral_epistemology
NODE: Moral Epistemology [moral_epistemology, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — four numbered approaches (intuitionism, coherentism / reflective equilibrium, reliabilism, skepticism), each with canonical figures, plus the cross-bridge to general epistemology. Rich.
C3 (summary cold-readability): yes — "how we know moral truths (if any)" is plain; the central questions and major positions are enumerated clearly.

### N-20 — indexical
NODE: Indexical Expression [indexical, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks the puzzle indexicals raise, gives Kaplan's character/content solution, taxonomizes the categories (pure indexicals, demonstratives, tense markers), and bridges to the essential-indexical puzzle. Strong.
C3 (summary cold-readability): yes — concrete examples carry it ("'I' refers to the speaker, 'you' to the addressee, 'here' to the place of utterance"); "deictic" is glossed inline.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0

## Cross-cutting observations (optional)
- C1 defect rate is 0.0% (0/27) — the first 0-defect shard of the census. Running C1 across shards 01–04: 10.7% / 3.6% / 3.6% / 0.0%, well below the production audit's 13% baseline. The closeout should weigh whether shard 01 is the outlier and what the convergence toward ~0–4% implies for the C1 drift comparison.
- Zero audit-touched edges in this shard — all 27 carry `evidence=NULL` and none of the (source, target) pairs match the concept pairs in the S-0122 follow-up migrations 0061–0065. This shard sampled no prior audit decisions.
- The single non-Sound verdict (E-21 speech_act → gricean_maxims, Defensible) reflects two somewhat-parallel pragmatic theories rather than a tight dependency — direction supportable, not a defect.
- Three Sound verdicts carry a noted both-ways alternative (E-2 existence→property, E-7 philosophy_of_science→scientific_method, E-20 material→indicative_conditional). All resolve to Sound by the seed's established field→topic / curricular-order conventions; flagged so the closeout can check scoring consistency against shards that scored similar shapes differently.
- Node quality is uniformly high: 0% C2 fail, 0% C3 fail across 20 INTERPRETED/active nodes. N-11 (fallibilism, brief teaching_notes) and N-18 (temporal_parts, jargon-opening summary rescued by an inline gloss) were the only near-the-line calls — the same "dense-open-then-rescue" C3 shape shards 02–03 also flagged.
