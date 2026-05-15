# Seed-graph QA census evidence — shard 07

> Authored by S-0168 (routine session) per T-SEED-QA task SQA-07.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 07
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — e81a2f62-dc65-4ba7-b6a7-0e829b4cf77d
EDGE: Causation [causation, metaphysics] → Free Will [free_will, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The free-will debate (determinism, compatibilism, libertarianism) is fundamentally about whether causal determination is compatible with free action; a learner cannot frame the problem without a grip on causation.
AUDIT-TOUCHED: none

### E-2 — ce43452b-8ba4-45c6-b1b9-9c1e95f0da15
EDGE: Aesthetics [aesthetics, aesthetics] → Aesthetic Judgment [aesthetic_judgment, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → subtopic. The general field framing of aesthetics genuinely scaffolds the specific topic of aesthetic judgment.
AUDIT-TOUCHED: none

### E-3 — c09137c7-5a19-428c-b533-3a3f1a97ccc1
EDGE: Propositional Logic [propositional_logic, logic] → Modal Logic [modal_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Modal logic extends propositional logic with modal operators; the propositional base is a strict prerequisite.
AUDIT-TOUCHED: none

### E-4 — 30d1a594-8718-4f85-b615-098b1cc9afd2
EDGE: Belief [belief, epistemology] → Basic Belief [basic_belief, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Basic belief (foundationalism's non-inferentially-justified beliefs) presupposes the general concept of belief.
AUDIT-TOUCHED: none

### E-5 — 38b67c57-5eac-4d94-b0d5-49282f865f25
EDGE: Political Philosophy [political_philosophy, political] → Justice [justice, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → subtopic. Political philosophy as the field framing introduces justice as a central topic within it.
AUDIT-TOUCHED: none

### E-6 — d86d8ec5-f100-49d1-9ec6-2be0bb5baaa9
EDGE: Knowledge [knowledge, epistemology] → Epistemic Skepticism [skepticism_epistemic, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Epistemic skepticism is the thesis that we lack (or cannot have) knowledge; the concept of knowledge is genuinely prior to skepticism about it.
AUDIT-TOUCHED: none

### E-7 — 87c18f93-d5f0-4086-9284-6d5dc104f3f3
EDGE: Epistemic Justification [epistemic_justification, epistemology] → Epistemic Skepticism [skepticism_epistemic, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Skeptical arguments centrally trade on whether beliefs can be justified — the regress problem, the criterion problem, underdetermination. Justification is a canonical conceptual input to skepticism, not merely a defensible one; this is a second genuine prerequisite alongside E-6.
AUDIT-TOUCHED: none

### E-8 — 4f3ffc8d-8005-48c7-9370-ba9cf71494dc
EDGE: Representational Theory of Mind [representational_theory_of_mind, mind] → Computational Theory of Mind [computational_theory_of_mind, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: CTM is RTM plus the claim that operations over representations are computational; the representational base is a strict prerequisite.
AUDIT-TOUCHED: none

### E-9 — 3b9410d9-c8bd-4cd8-ae7d-fef5d4b902dc
EDGE: Climate Ethics [climate_ethics, ethics] → Future Generations [future_generations, ethics]
  weight=0.9, confidence=0.9, evidence=NULL
VERDICT: Defensible
RATIONALE: The canonical direction is general-before-applied — future_generations (the intergenerational-ethics apparatus: the non-identity problem, discounting, Parfitian puzzles) is the foundational concept that climate ethics applies. The edge runs the other way. It is supportable on a real concrete-entry-point reading — contemporary courses frequently use climate as the vivid, salient hook that motivates the abstract future-generations problem — so it is not a clear Reversed. But it is not the canonical framing. The down-weighted 0.9 weight suggests the authoring itself carried hesitation. Shares the "target is the more general concept" shape flagged in the cross-cutting observations.
AUDIT-TOUCHED: none

### E-10 — a497ddc3-a6c1-49f7-8aac-787494f46883
EDGE: Causation [causation, metaphysics] → Counterfactual Theory of Causation [counterfactual_theory_of_causation, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The counterfactual theory (Lewis) is a specific theory OF causation; the general topic is prior to a specific theory of it.
AUDIT-TOUCHED: none

### E-11 — 91789670-bc92-47ad-8ff4-3b88deeb992b
EDGE: Gettier Problem [gettier_problem, epistemology] → Defeasibility Analysis [defeasibility_analysis, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Defeasibility analysis is a direct response to the Gettier problem — it adds a no-defeaters condition to JTB. The problem motivates the response.
AUDIT-TOUCHED: none

### E-12 — 61613f29-3b7e-49d7-a824-4cf70a0b9824
EDGE: Truth [truth, epistemology] → Correspondence Theory of Truth [truth_correspondence, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The correspondence theory is a specific theory of truth; the general concept is prior to a specific theory of it.
AUDIT-TOUCHED: none

### E-13 — 52b6209f-8f48-4d7b-b860-07f1198e57e2
EDGE: Physicalism [physicalism, mind] → Reductionism (in Science) [reductionism_in_science, science]
  weight=1.0, confidence=1.0, evidence="Per S-0122 audit: Physicalism commits to the doctrine that every property is either physical or grounded in physical properties; reductionism_in_science is one central strategy for implementing that commitment across domains."
VERDICT: Sound
RATIONALE: Physicalism (the metaphysical doctrine) motivates reductionism in science as one central implementation strategy. The S-0122 audit examined this exact edge as a weak-edge prune candidate (CB-E-67) and deliberately KEPT it, attaching the evidence annotation now carried in the shard. The direction and retention are audit-confirmed; I concur on independent review.
AUDIT-TOUCHED: migration 0063 — weak-edge cleanup pass examined this edge as a prune candidate and kept it with the evidence annotation justifying retention (not flipped, not pruned). The shard's `evidence` text is that 0063 annotation verbatim.

### E-14 — dc168afd-24fc-459a-8568-6063f5698cba
EDGE: Numerical Identity [numerical_identity, metaphysics] → Leibniz's Law [leibniz_law, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Leibniz's Law (the indiscernibility of identicals) is a principle ABOUT numerical identity; the concept of numerical identity is prior.
AUDIT-TOUCHED: none

### E-15 — abc05170-ba50-43f4-befb-34679ac3c825
EDGE: Moral Epistemology [moral_epistemology, ethics] → Motivational Internalism [motivational_internalism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Motivational internalism — the thesis that moral judgment is intrinsically motivating — is primarily a position in moral psychology / the metaethics of motivation. Its canonical prerequisites would be the concept of moral judgment or moral motivation, not specifically moral epistemology (the theory of how we know moral truths). The edge is supportable on a reading where moral epistemology, broadly construed, frames the nature of moral judgment that internalism then makes a claim about — but the connection is real-but-indirect, not the canonical proximate prerequisite. Note: migration 0062 flipped a different incoming edge to motivational_internalism (motivational_internalism→propositional_attitude became propositional_attitude→motivational_internalism); this edge was not touched by that pass.
AUDIT-TOUCHED: none

### E-16 — bc4d7fa3-a844-41f1-bebb-fcb0331c081c
EDGE: Aesthetics [aesthetics, aesthetics] → Art Criticism [art_criticism, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → subtopic. Aesthetics as the field framing scaffolds art criticism as a topic within it.
AUDIT-TOUCHED: none

### E-17 — 66123052-39e5-4445-a67a-e14a00360516
EDGE: Functionalism (Philosophy of Mind) [functionalism, mind] → Inverted Spectrum [inverted_spectrum, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The inverted spectrum is a classic objection/thought experiment against functionalism; understanding it requires the functionalist position it targets.
AUDIT-TOUCHED: none

### E-18 — 584e241f-82e6-48cb-9ff4-b39ad2bd5d33
EDGE: Formal Epistemology [formal_epistemology, epistemology] → Credence [credence, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → subtopic, the same pattern as E-2/E-5/E-16/E-24. Formal epistemology as the field/approach provides the framing within which credence (degree of belief) is introduced as a core concept. An intro to formal epistemology introduces credence among its first concepts, so the field-framing-first ordering holds.
AUDIT-TOUCHED: none

### E-19 — 731aa175-4a64-4cb1-be26-3d1a46bbe475
EDGE: Mental State [mental_state, mind] → Physicalism [physicalism, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Physicalism about the mind is the thesis that mental states are physical; the concept of a mental state is prior to a thesis about its nature.
AUDIT-TOUCHED: none

### E-20 — 5cf7cb5d-8123-43e8-9a81-60b14eee22bb
EDGE: Social Contract Theory [social_contract_theory, political] → Contractualism [contractualism, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Contractualism (Scanlon) is the moral-philosophy descendant of the classical social contract tradition (Hobbes, Locke, Rousseau), extending the contract idea from political legitimacy to moral rightness generally. The historical and conceptual ancestor is genuinely prior.
AUDIT-TOUCHED: none

### E-21 — 2886d0d1-4596-4110-82bf-fe1ce6f53754
EDGE: Scientific Method [scientific_method, science] → Value-Free Ideal [value_free_ideal, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The value-free ideal is a normative thesis about scientific method/practice; a grip on scientific method is prior to debating whether it should be value-free.
AUDIT-TOUCHED: none

### E-22 — cb3d902a-1c67-4277-ae7d-88e1113d5021
EDGE: Equality (Political) [equality_political, political] → Capability Approach [capability_approach, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The capability approach (Sen, Nussbaum) is a specific framework answering "equality of what?"; the general concept of political equality is prior to a specific answer.
AUDIT-TOUCHED: none

### E-23 — 9459e051-8fd2-4725-8b01-087441003cc3
EDGE: Mental Causation [mental_causation, mind] → Causal Exclusion Argument [causal_exclusion_argument, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: The causal exclusion argument (Kim) is an argument about mental causation — that physical causes exclude mental ones. The problem of mental causation frames the argument.
AUDIT-TOUCHED: none

### E-24 — 10d9e222-cb50-4b02-aef0-97a11be7666c
EDGE: Aesthetics [aesthetics, aesthetics] → Aesthetic Experience [aesthetic_experience, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Field → subtopic. Aesthetics as the field framing scaffolds aesthetic experience as a topic within it.
AUDIT-TOUCHED: none

### E-25 — 04dec5a4-852b-4f2f-a01e-ae31591b393d
EDGE: Argument (Logical) [argument_logical, service] → Validity (Logical) [validity_logical, service]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Validity is a property OF arguments; the concept of an argument is strictly prior to the concept of validity.
AUDIT-TOUCHED: none

### E-26 — e855b236-a23c-4c4f-873a-09891e664ac5
EDGE: Scientific Theory [scientific_theory, science] → Law of Nature [law_of_nature, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Scientific theory and law of nature are close to co-equal in the basic philosophy-of-science vocabulary, and the prerequisite relation does not run unambiguously in either direction. There is a real reading supporting the edge — theories are the broader law-containing structure, so "understand theories, then ask what the laws within them are" is a coherent ordering. But there is an equally canonical reading running the other way (the D-N model of explanation uses laws; theories are then understood as law-involving structures, so law_of_nature is taught first). Supportable on an alternative reading, not the canonical framing — Defensible, not Reversed. Shares the "near-co-equal / target is the more foundational concept" shape flagged in the cross-cutting observations.
AUDIT-TOUCHED: none

### E-27 — b4648e7f-ad09-4347-8ef2-5dd7818bd147
EDGE: Hard Problem of Consciousness [hard_problem_of_consciousness, mind] → Integrated Information Theory [integrated_information_theory, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: IIT (Tononi) is a specific candidate theory of consciousness, presented as an attempted response to the hard problem; the hard-problem framing is prior to IIT as an answer.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — aristotelian_four_causes
NODE: Aristotelian Four Causes [aristotelian_four_causes, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the bronze-statue walkthrough and the acorn example are concrete worked entry points; the mechanist-revolt framing gives a genuine "why it matters" angle.
C3 (summary cold-readability): yes — each of the four causes is glossed with a plain-language question ("what is it made of?", "what is it for?"); a cold reader can parse it.

### N-2 — open_question_argument
NODE: Open Question Argument [open_question_argument, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the closed/open-question contrast is spelled out as a usable structure, with Frankena's charge and modern defenders giving traction.
C3 (summary cold-readability): yes — the bachelor contrast makes the argument concrete; "sui generis non-natural property" is light jargon but the surrounding prose carries it.

### N-3 — material_conditional
NODE: Material Conditional [material_conditional, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — concrete examples ("If 2+2=5 then the moon is cheese") and a clear explanation of why the paradoxes are not really paradoxes.
C3 (summary cold-readability): yes (borderline) — "truth-functional connective" in the opening clause is mild jargon-gating, but it is immediately followed by a plain-language definition ("false exactly when P is true and Q is false") that a cold reader can parse; the symbolic "¬P ∨ Q" is supplementary, not load-bearing.

### N-4 — mereological_universalism
NODE: Mereological Universalism [mereological_universalism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains the attraction (simplicity) against the cost (non-commonsense objects) and situates the Lewis-Sider package; a genuine angle in.
C3 (summary cold-readability): yes — the trout-turkey and Eiffel-Tower-plus-Mars examples make the abstract thesis concrete; "Special Composition Question" is referenced but the opening sentence already conveys the idea.

### N-5 — virtue_epistemology
NODE: Virtue Epistemology [virtue_epistemology, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — "instead of starting with belief... start with the believer" is a genuine reorienting intuition, and it names the canonical texts for each branch.
C3 (summary cold-readability): yes — the two camps are introduced with glosses; reads clearly cold.

### N-6 — no_miracles_argument
NODE: No-Miracles Argument [no_miracles_argument, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — walks the premises 1–3 and conclusion explicitly, names the IBE structure, surfaces the major counter-arguments.
C3 (summary cold-readability): yes — the core argument ("success would be a miracle if theories were not true") is stated in plain language.

### N-7 — representationalism_consciousness
NODE: Representationalism (Consciousness) [representationalism_consciousness, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — explains the program's elegance, runs the standard objections (inverted spectrum, blurry vision, moods), and draws the strong/weak distinction.
C3 (summary cold-readability): yes — "phenomenal character" is glossed by "what it is like to have an experience"; reasonably parseable cold.

### N-8 — liberalism
NODE: Liberalism [liberalism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — thorough: foundational commitments, the principal internal divides, and the principal critics, each as a usable teaching structure.
C3 (summary cold-readability): yes — accessible prose; the strands are each glossed with representative figures.

### N-9 — performative_utterance
NODE: Performative Utterance [performative_utterance, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — felicity conditions, misfires, and the three categories give a concrete, worked entry.
C3 (summary cold-readability): yes — the paradigm cases ("I now pronounce you husband and wife", "I name this ship...") make it immediately concrete.

### N-10 — causal_powers
NODE: Causal Powers [causal_powers, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — situates powers theory as the contemporary alternative to Humean regularity and counterfactual reduction, with the disposition and laws-of-nature connections.
C3 (summary cold-readability): yes — the match-igniting example is right in the summary.

### N-11 — animalism
NODE: Animalism [animalism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the three motivating arguments (thinking-animal, fetal-existence, persistence-through-PVS) are spelled out, plus the standard objection.
C3 (summary cold-readability): yes — "we are human animals — biological organisms" is plain and clear.

### N-12 — unification_theory_of_explanation
NODE: Unification Theory of Explanation [unification_theory_of_explanation, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the Newton and Maxwell examples, Kitcher's precise account, and the three difficulties give strong traction.
C3 (summary cold-readability): yes — the core idea (explanation as unification under a small number of patterns) is clear; the unexplained "post-D-N" reference is mild jargon but parenthetical and skippable without losing the thread.

### N-13 — morality
NODE: Morality [morality, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the careful boundary-drawing against etiquette, legality, and prudence is a usable opening move; the metaethics/normative split is clean.
C3 (summary cold-readability): yes — very accessible; the contrasts are concrete.

### N-14 — supervenience_mental
NODE: Mental Supervenience [supervenience_mental, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the three increasingly strong supervenience theses are distinguished explicitly, with the standard critique.
C3 (summary cold-readability): yes — "supervene" is immediately glossed ("there cannot be two beings physically identical but mentally different").

### N-15 — meaning
NODE: Meaning (Linguistic) [meaning, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguishing six senses of "meaning" is a genuine, usable disambiguation a learner can hold onto.
C3 (summary cold-readability): yes — clear; frames meaning as the central explanandum of philosophy of language without circularity.

### N-16 — ship_of_theseus
NODE: Ship of Theseus [ship_of_theseus, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — names the endurantist and perdurantist readings and advises using the puzzle to set up deeper disputes rather than as a stand-alone problem.
C3 (summary cold-readability): yes — the puzzle and the reassembly twist are laid out plainly.

### N-17 — twin_earth
NODE: Twin Earth [twin_earth, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the Oscar / Twin-Oscar setup, the externalist and internalist intuitions, and the variants (arthritis, Kripke's "Aristotle") give a fully worked entry.
C3 (summary cold-readability): yes — the thought experiment is laid out concretely and self-containedly.

### N-18 — free_play_imagination_understanding
NODE: Free Play of Imagination and Understanding [free_play_imagination_understanding, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the notes do give a foothold: they explain why aesthetic experience feels cognitively significant without delivering a determinate proposition, and why beautiful objects feel "made for" cognition. That is a genuine intuition a learner can grasp, even though it leans on "the four moments".
C3 (summary cold-readability): no — jargon-gated / assumes-the-concept. The summary depends on undefined technical terms a cold reader would not know — "the judgment of taste", "determinate concept" (in Kant's technical sense), "universal communicability" — and the load-bearing sentence ("this free play... generates the pleasurable feeling that grounds the universal communicability of the judgment of taste") cannot be parsed without prior familiarity with Kant's third-Critique framework.

### N-19 — applied_ethics
NODE: Applied Ethics [applied_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the theoretical/applied division, the observation that applied problems refine the theories that govern them, and the three sub-traditions with their canonical literature give strong traction.
C3 (summary cold-readability): yes — clear; the sub-areas are each glossed concretely.

### N-20 — speech_act
NODE: Speech Act [speech_act, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the three-step reconstruction of Austin's move, Searle's F(P) formalization, and the influence across pragmatics/law/feminist philosophy give a worked entry.
C3 (summary cold-readability): yes — the locutionary/illocutionary/perlocutionary triad is each glossed inline; reads clearly cold.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 1 (5.0%) | teaching_notes ABSENT 0

## Cross-cutting observations
- Third 0-defect C1 shard of the census (after shards 04 and 06). Running C1 across shards 01–07: 10.7% / 3.6% / 3.6% / 0.0% / 3.7% / 0.0% / 0.0% — firmly under the production audit's 13% baseline.
- Defensible cluster: 3/27 (E-9, E-15, E-26) — within the recent per-shard range (shard 04→1, shard 05→4, shard 06→6). Two of the three — E-9 `climate_ethics → future_generations` and E-26 `scientific_theory → law_of_nature` — share the exact "target is the more general / more foundational / near-co-equal concept, so the edge could be read as Reversed" shape the shard 05 and 06 evidence files flagged. Per the calibration those prior sessions established, each was held at Defensible (not Reversed) because a real concrete-entry-point reading (E-9) or a genuinely co-equal pedagogical relationship (E-26) supports the graph's direction — not as a comfortable hedge. The SQA-20 closeout should review this recurring shape as a cross-shard pattern and decide whether the rubric should tip such "could-be-reversed-because-target-is-more-general" edges toward Reversed; that is a rubric-calibration question above an evidence session's remit.
- The single C3 fail (N-18 free_play_imagination_understanding) is the census's third C3 fail, and again the same shape as shard 05's N-8 and shard 06's N-16: a load-bearing first/summary sentence gated on undefined technical vocabulary. N-18 sits further over the line than those two — it is gated on a whole framework ("the judgment of taste", Kant's technical "determinate concept", "universal communicability"), not a single unexpanded term — so it is a clearer fail than the borderline shard 05/06 cases. The recurrence across three consecutive shards suggests jargon-gated summaries are a real, non-noise C3 failure mode worth a pattern entry in the closeout.
