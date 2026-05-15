# Seed-graph QA census evidence — shard 18

> Authored by S-0180 (routine session) per T-SEED-QA task SQA-18.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 18
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — ec7f8659-67ab-42c5-8ced-889f16b719ba
EDGE: Time [time, metaphysics] → Causation [causation, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Time is a basic metaphysical category (B-theory's earlier-than/later-than relations; A-theory's past/present/future) that causation presupposes on most readings: cause precedes effect, and counterfactual / regularity / process / powers theories of causation all use temporal ordering as their primitive scaffolding. Pedagogically the standard intro-metaphysics sequence introduces time first as a fundamental category, then introduces causation as a relation defined over temporally-ordered events. Same shape as the basic-category → relation-defined-over-it pattern (cf. shard 16 E-25 existence → relation, scored Defensible because both are co-fundamental categories — here causation is genuinely later in the standard pedagogical sequence, so Sound rather than Defensible).
AUDIT-TOUCHED: none (0061 proximity-only on `time` keyword — 0061 retypes the deleted `time → mctaggarts_paradox` edge, a different tuple; 0063 proximity-only on `time` — 0063 deletes `time → mctaggarts_paradox`, again a different tuple; 0064 proximity-only on `causation` — 0064 annotates `supervenience_mental → mental_causation`, a different tuple).

### E-2 — ef429047-e232-4361-96f9-06cb51991ca5
EDGE: Pictorial Representation [pictorial_representation, aesthetics] → Depiction [depiction, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Pictorial representation is the broader phenomenon (the relation by which a picture depicts its subject); depiction is the specific perceptual-mode theory (Wollheim's "seeing-in"). N-7 depiction (shard 11) opens with "the specific perceptual mode by which a viewer recognizes what a picture pictures" — explicitly framed as a sub-topic of pictorial representation. Phenomenon → specific theoretical account, canonical Sound shape.
AUDIT-TOUCHED: none

### E-3 — c12cb375-a5ac-42af-a993-90921c0de70a
EDGE: Multiple Realizability [multiple_realizability, mind] → Computational Theory of Mind [computational_theory_of_mind, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Multiple realizability (Putnam 1967) is one of the foundational arguments motivating functionalism and, downstream, computational theories of mind (Fodor 1975 *Language of Thought*, 1981 *Representations*). The argument — pain in humans and octopuses cannot be brain-state-type-identical because the implementing physical substrate differs, so mental kinds must be functionally individuated — is precisely what makes CTM coherent (compute-on-substrate-neutral-symbol-systems requires substrate-independence of mental types). Argument → the theory the argument motivates, Sound.
AUDIT-TOUCHED: none

### E-4 — c05834c6-74c7-4c4a-9e38-0df42aae9b29
EDGE: Set (Mathematical) [set_mathematical, service] → Kripke Semantics [kripke_semantics, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: N-1 kripke_semantics (this shard) opens "A Kripke model is a triple ⟨W, R, V⟩ where W is a non-empty set of possible worlds, R ⊆ W × W is the accessibility relation, and V is a valuation" — three set-theoretic objects (set, relation-as-subset-of-Cartesian-product, valuation-as-function) are constitutive of the framework. Mathematical formal apparatus → its application in modal logic semantics, canonical service-domain → consumer pattern (`source_domain = service`).
AUDIT-TOUCHED: none (0062 proximity-only on `kripke_semantics` — 0062 flips `formal_epistemology → kripke_semantics`, a different tuple).

### E-5 — 88acee18-4798-4a94-a77f-7a79648e5329
EDGE: Qualia Eliminativism [qualia_eliminativism, mind] → Multiple Drafts Model [multiple_drafts_model, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Dennett's multiple drafts model (1991 *Consciousness Explained*) is a positive theory of consciousness that pairs with his qualia eliminativism — the model proposes that conscious experience is a continuous stream of parallel narrative-fragments without a privileged "Cartesian theater," explaining away the appearance of unified phenomenal content that qualia realism takes at face value. Pedagogically the eliminativist position frames why a positive theory like multiple drafts is needed (eliminating qualia leaves a positive explanatory task: account for the appearances). Position → its constructive complement, Sound.
AUDIT-TOUCHED: none

### E-6 — 754611e9-4e43-44cf-8251-3ab386456392
EDGE: Possible Worlds [possible_worlds, metaphysics] → Kripke Semantics [kripke_semantics, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Possible worlds is the metaphysical motivation (Leibniz's possible-other-ways-the-world-could-have-been; Lewis 1986 modal realism; Plantinga abstract states-of-affairs); Kripke semantics is the formal apparatus that takes possible-world talk and gives it model-theoretic precision (the set W of worlds; R as the accessibility relation between them). Standard pedagogical order: introduce the metaphysics, then introduce the formal semantics that operationalizes it. Cross-domain metaphysics → logic, canonical Sound shape.
AUDIT-TOUCHED: none (0062 proximity-only on `kripke_semantics`; 0064 proximity-only on both `possible_worlds` and `kripke_semantics` — 0064 annotates `abstract_object → possible_worlds`, a different tuple).

### E-7 — 4d2b114a-0e2d-4674-b2fd-9732ed4827d3
EDGE: Epistemic Skepticism [skepticism_epistemic, epistemology] → Pyrrhonian Skepticism [pyrrhonian_skepticism, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Epistemic skepticism is the umbrella category (any position denying knowledge is achievable in some domain); Pyrrhonian skepticism is one specific tradition within it (Sextus Empiricus's mode-based suspension-of-judgment, distinct from academic skepticism's dogmatic denial of knowledge and from Cartesian methodological skepticism's pursuit of certainty). Umbrella → species, canonical Sound shape; same pattern as shard 17 E-22 modality → modal_logic (broader phenomenon → specific tradition handling it).
AUDIT-TOUCHED: none (0062 proximity-only — 0062 flips `problem_of_induction → pyrrhonian_skepticism`, a different tuple).

### E-8 — fe1ae83a-f76b-49ff-8688-aacd41453e84
EDGE: Composition (Mereological) [composition_mereological, metaphysics] → Gunk [gunk, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Composition (the Special Composition Question: under what conditions do parts compose a whole?) is the umbrella topic; gunk (Lewis: an object every part of which has further proper parts, no mereological simples) is a specific position about the structure of composition (denies that composition bottoms out at atomless simples). Topic → its specific structural position, Sound. N-9 composition_mereological (shard 17) framed van Inwagen 1990 / Lewis universalism / Markosian as the three composition-question camps; gunk extends this with the no-atoms structural commitment.
AUDIT-TOUCHED: none

### E-9 — a9e1c740-031e-403d-8ea1-3ca6d64ffc4a
EDGE: Numerical Identity [numerical_identity, metaphysics] → Haecceity [haecceity, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Numerical identity (the relation each thing bears uniquely to itself; Leibniz's law) is the basic concept; haecceity (Scotus's thisness — the non-qualitative property of being identical with a specific individual) is a posited explanans for what grounds numerical identity. Concept → theoretical posit explaining it, Sound. Pedagogically standard: introduce numerical identity as the relation we want to understand, then introduce haecceity as one metaphysical proposal for what its truthmakers are.
AUDIT-TOUCHED: none

### E-10 — 11b9a877-62be-49cf-9fda-0c63b134eda9
EDGE: Gettier Problem [gettier_problem, epistemology] → Causal Theory of Knowing [causal_theory_of_knowing, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Gettier 1963 → Goldman 1967 "A Causal Theory of Knowing." The causal theory was one of the major historical responses to the Gettier problem (add a causal connection between fact and belief to JTB to rule out Gettier counterexamples). Problem → its historical solution, canonical Sound shape; same pattern as shard 14 E-26 / various other epistemology-response edges across the routine batch.
AUDIT-TOUCHED: none

### E-11 — 549e5f6f-f188-4536-a9b2-ab5e52d26942
EDGE: Tracking Theory of Knowledge [tracking_theory_of_knowledge, epistemology] → Safety Condition [safety_condition, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Tracking theory (Nozick 1981 *Philosophical Explanations* — sensitivity: if p were false, S would not believe p) historically precedes the safety condition (Sosa 1999, Williamson 2000 — if S believes p, p is true in nearby possible worlds). The safety condition was developed partly as a refinement of the sensitivity condition (preserves Nozick's modal-counterfactual machinery while avoiding objections such as that sensitivity blocks knowledge by inductive inference). Original theory → its refinement, Sound.
AUDIT-TOUCHED: none

### E-12 — 74790195-ec65-43da-90a6-c992437034c4
EDGE: Principle of Bivalence [bivalence_principle, service] → Dialetheism [dialetheism, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Bivalence (every statement is true or false, exclusively and exhaustively) is the classical-logic standard; dialetheism (Priest 1987 *In Contradiction* — some statements are both true and false) rejects bivalence's exclusivity. Pedagogical sequence: introduce the standard, then introduce its rejection-via-counterexample (liar paradoxes treated as true contradictions). Same standard-then-rejection shape as shard 16's four-edge position-and-rejection cluster (E-11 bivalence_principle → fuzzy_logic, E-13 epistemic_closure → closure_denial, E-22 certainty → fallibilism, E-26 justified_true_belief → knowledge_first_epistemology) and as E-26 explosion_principle → paraconsistent_logic in this shard. Cross-domain service → logic, Sound.
AUDIT-TOUCHED: none (0063 proximity-only — 0063 DELETES `bivalence_principle → paraconsistent_logic`, a different tuple from this shard's E-12 `bivalence_principle → dialetheism`).

### E-13 — 4fba1dcb-11ce-4280-acd4-977fcdb07ca5
EDGE: Biocentrism [biocentrism, ethics] → Animal Ethics [animal_ethics, ethics]
  weight=0.8, confidence=0.8
  evidence=NULL
VERDICT: Defensible
RATIONALE: Inverted-from-canonical-direction. Animal ethics (Singer 1975 *Animal Liberation*, Regan 1983 *Case for Animal Rights*) is the older field and was largely established before biocentrism (Taylor 1986 *Respect for Nature*; Schweitzer 1923 "reverence for life") emerged as a distinct metaethical position. The canonical contemporary environmental-ethics pedagogical sequence runs animal ethics first (extends moral consideration from humans to sentient animals), then biocentrism (extends further to all living organisms), then ecocentrism (Leopold's land ethic, holistic ecosystem-level value). N-13 animal_ethics (shard 17) explicitly frames the field via the 1970s Singer/Regan crystallization, and biocentrism in shard 04's N-13 is framed as the broader extension. The edge runs sub-field → broader-field, the same "specific-position → broader-field" inverted shape shard 17 introduced (E-5 testimonial_knowledge → social_epistemology, E-6 consequentialism → supererogation). Held at Defensible on the foothold reading: biocentrism's "all living things have intrinsic moral value" thesis grounds a meta-ethical extension principle that animal ethics implicitly relies on (any defense of animal moral status against pure anthropocentrism can be parsed as a special case of biocentrism's broader value-extension move). Alternative readings: Sound on the "metaethical foundation grounds applied field" reading; Reversed on the strict historical-priority reading (animal ethics predates biocentrism as a named position). SQA-20 calibration: the specific-position → broader-field sub-shape now has at least three exemplars in the routine batch (shard 17 E-5, E-6 + this shard's E-13).
AUDIT-TOUCHED: none (0062 proximity-only on `animal_ethics` — 0062 flips `animal_ethics → sentientism`, a different tuple, and the flipped direction confirms animal_ethics is the broader field, supporting the Defensible call here).

### E-14 — 8c2a9a96-1c39-40c4-9511-72553b163e9a
EDGE: Medical Ethics [medical_ethics, ethics] → End-of-Life Ethics [end_of_life_ethics, ethics]
  weight=0.85, confidence=0.85
  evidence=NULL
VERDICT: Sound
RATIONALE: Medical ethics is the umbrella applied-ethics field; end-of-life ethics is a specific sub-topic (euthanasia, physician-assisted dying, withdrawal of life-sustaining treatment, advance directives). Umbrella → sub-area, canonical Sound shape; same pattern as the multi-shard applied-ethics ladder shard 17 surfaced (applied_ethics > bioethics > research_ethics > informed_consent, and now this shard adds medical_ethics > end_of_life_ethics on a parallel branch).
AUDIT-TOUCHED: none

### E-15 — 20c4f6da-ae71-4167-b710-1d576c6e662a
EDGE: Scientific Realism [scientific_realism, science] → No-Miracles Argument [no_miracles_argument, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Scientific realism (the position that mature scientific theories are approximately true descriptions of the world); no-miracles argument (Putnam 1975, Boyd 1980, Smart 1968 — realism is the only philosophy that doesn't make the predictive success of mature science a miracle). Position → its principal argument-for, canonical Sound shape; paired with E-24 (this shard) scientific_realism → pessimistic_meta_induction, which gives the position → its principal argument-against. Together E-15 and E-24 form a two-edge introduction-of-the-debate cluster within shard 18.
AUDIT-TOUCHED: none

### E-16 — ba7e3008-49e9-4a01-ae07-c960430f94e6
EDGE: Art Criticism [art_criticism, aesthetics] → Anti-Intentionalism [anti_intentionalism, aesthetics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Art criticism is the practice (interpreting and evaluating works of art); anti-intentionalism (Wimsatt & Beardsley 1946 "The Intentional Fallacy") is a methodological position within it (the artist's intent is irrelevant to the interpretation/evaluation of the work). Practice → methodological position-within-the-practice, canonical Sound shape.
AUDIT-TOUCHED: none

### E-17 — 594fdc58-7319-4159-b5d2-f201be23f676
EDGE: Moral Anti-Realism [moral_anti_realism, ethics] → Error Theory [error_theory, ethics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Moral anti-realism is the umbrella category (any view denying mind-independent moral facts); error theory (Mackie 1977 *Ethics: Inventing Right and Wrong*) is one specific anti-realist position — moral statements purport to describe but systematically fail to refer (companion-in-guilt with statements about phlogiston). Umbrella → species, canonical Sound shape; pairs with N-13 expressivism (this shard) as the other major anti-realist family (non-cognitivist).
AUDIT-TOUCHED: none

### E-18 — 014195e7-ef60-49c3-9046-49d9b3662db1
EDGE: Hypothetico-Deductive Method [hypothetico_deductivism, science] → Paradox of the Ravens [paradox_of_the_ravens, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: H-D method (Popper-Hempel — confirmation by deriving testable predictions); ravens paradox (Hempel 1945 — "all ravens are black" is logically equivalent to "all non-black things are non-ravens," so observing a green apple confirms the raven generalization). The paradox arises within and threatens H-D confirmation theory. Method → its internal paradox, canonical Sound shape; same pattern as E-15/E-24 (position → arguments), here position → its puzzle-within.
AUDIT-TOUCHED: none

### E-19 — c10dd851-15e9-426f-87ea-e0943091137d
EDGE: Temporal Parts [temporal_parts, metaphysics] → Mereology [mereology, metaphysics]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Inverted-from-canonical-direction. Mereology is the general formal theory of parts and wholes (Lesniewski, Goodman-Leonard — classical extensional mereology with transitivity, reflexivity, supplementation axioms); temporal parts is a specific metaphysical doctrine that applies mereological reasoning to the temporal dimension (perdurantism: a persisting object has temporal parts at each time of its existence, analogous to its spatial parts). N-12 mereology (shard 12) and shard 04's temporal_parts node both treat mereology as the broader formal theory; the canonical contemporary metaphysics-of-persistence pedagogy (Sider 2001 *Four-Dimensionalism*, Loux *Metaphysics*) introduces mereology first as background, then introduces temporal parts as the application. The edge runs specific-application → general-theory, the inverted shape. Held at Defensible on the foothold reading: introducing temporal parts gives a concrete metaphysical entry point (the persistence-through-change puzzle) that motivates the abstract part-whole formalism — Sider explicitly uses temporal-parts-as-motivation for mereology in his pedagogical setup. Alternative readings: Sound on the "motivate-formalism-from-application" reading; Reversed on the canonical-priority reading (formal theory grounds its applications). Same "specific → broader" inverted shape as E-13 biocentrism → animal_ethics this shard and shard 17's E-5/E-6 cluster.
AUDIT-TOUCHED: none

### E-20 — 79ee0589-6b40-4be9-8e4e-44bc448f9699
EDGE: Phenomenal Consciousness [phenomenal_consciousness, mind] → Phenomenal Concept [phenomenal_concept, mind]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Phenomenal consciousness is the phenomenon (what-it-is-like-ness, the subjective character of experience); phenomenal concepts (Loar 1990, Papineau 2002, Stoljar 2005) are the special concepts we deploy in introspectively referring to phenomenal states (a phenomenal concept of "red" picks out red-as-experienced, distinct from a physical/functional concept of red). Phenomenon → concepts-about-the-phenomenon, canonical Sound shape; pedagogically required because phenomenal-concept strategy responses to the conceivability argument depend on first establishing the explanandum (phenomenal consciousness) as the target of the concept's distinctive mode of presentation.
AUDIT-TOUCHED: none

### E-21 — d45e1034-aa04-450a-95b7-88f7ae351b64
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Testimonial Knowledge [testimonial_knowledge, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional knowledge (knowing-that p) is the umbrella category; testimonial knowledge (knowledge acquired by accepting another's assertion) is one of its major sources (alongside perception, memory, inference, introspection). N-15 testimonial_knowledge (this shard) explicitly frames testimony as "a genuine source of [propositional] knowledge." Umbrella → source-of-instances, canonical Sound shape; mirrors E-27 propositional_knowledge → understanding (this shard) on a different sub-relation (source vs cognate-state).
AUDIT-TOUCHED: none

### E-22 — 14ee90a0-bc28-47d9-8cce-4f056d865bb9
EDGE: Evidence [evidence, epistemology] → Bayesian Epistemology [bayesian_epistemology, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Evidence is the basic epistemological concept (whatever bears on the truth of a proposition); Bayesian epistemology is one formal-theory family for handling evidential reasoning (conditional probability + Bayes' rule + diachronic updating). Concept → formal-theory-handling-it, canonical Sound shape. Same pattern as shard 15 E-19 bayesian_epistemology → dutch_book_argument's underlying logic (formal-theory's distinctive argument) and shard 17 E-22 modality → modal_logic (phenomenon → formal apparatus).
AUDIT-TOUCHED: none (0063 EXACT-TUPLE hit on `evidence` and `bayesian_epistemology`, but the 0063 mention is `evidence IS NOT NULL AND ... (source_id, target_id) IN (... ('bayesian_epistemology','dutch_book_argument'))` — a SQL postcondition assertion checking that 0063 successfully wrote an `evidence` column value on the DIFFERENT edge `bayesian_epistemology → dutch_book_argument`, NOT on this shard's edge `evidence → bayesian_epistemology`. False positive — same node-name coincidence as the shard 15 E-11 `truth → tarskis_t_schema` 0062 false-positive workflow note).

### E-23 — 88452b4b-7e31-4f00-b5de-6bf24580e33c
EDGE: Natural Rights [natural_rights, political] → Libertarianism (Political) [libertarianism_political, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Natural rights theory (Locke's life-liberty-property; the Declaration of Independence inheritance) is foundational; political libertarianism (Nozick 1974 *Anarchy, State, and Utopia* — minimal state justified only by individual rights against coercion) builds directly on natural-rights premises. Foundation → theory-built-on-foundation, canonical Sound shape. Distinct from libertarianism_metaphysical (N-11 this shard, free-will libertarianism) — the political/metaphysical disambiguation flagged in N-11's own teaching notes.
AUDIT-TOUCHED: none

### E-24 — 0c3e80d2-31eb-4b17-aa4a-1de02fcf2b9c
EDGE: Scientific Realism [scientific_realism, science] → Pessimistic Meta-Induction [pessimistic_meta_induction, science]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Scientific realism (theory-truth-of-mature-science position); pessimistic meta-induction (Laudan 1981 "A Confutation of Convergent Realism" — many past successful theories were false at their core posits, so by induction current ones likely false too). Position → its principal argument-against, canonical Sound shape; mirror of E-15 scientific_realism → no_miracles_argument (this shard) which is position → principal argument-for. Together E-15 and E-24 form a two-edge introduction-of-the-debate cluster.
AUDIT-TOUCHED: none

### E-25 — 5c68cd9b-479d-4b59-a83d-5f0fee052426
EDGE: Political Obligation [political_obligation, political] → Conservatism [conservatism, political]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Defensible
RATIONALE: Inverted-from-canonical-direction. Political obligation is a topic in political philosophy (the moral duty to obey law); conservatism (Burke 1790 *Reflections*; Oakeshott 1962 *Rationalism in Politics*) is a broader political tradition that has distinctive views on political obligation (rooted in institutional respect, accumulated wisdom, gradualist reform) but is not pedagogically subordinate to political obligation in the standard contemporary political-philosophy sequence — conservatism is more typically introduced as a tradition alongside liberalism, socialism, libertarianism, communitarianism, with views on a range of topics including obligation, distribution, identity, and authority. The edge runs topic → broader-tradition, the "specific-topic → broader-field" inverted shape. Held at Defensible on the foil-into-tradition reading: political obligation as a question gives the framing within which conservatism's distinctive Burkean answer (obey because of tradition's accumulated wisdom, not because of consent or fair-play) becomes intelligible — establishing the question primes the conservative response. Alternative readings: Sound on the "establish-the-canonical-question-before-introducing-distinctive-answers" reading; Reversed on the strict-canonical-priority reading (conservatism is broader and can be introduced via its views on tradition/institutions without first establishing political obligation). Same inverted shape as E-13 biocentrism → animal_ethics and E-19 temporal_parts → mereology this shard.
AUDIT-TOUCHED: none (0064 annotates `social_contract_theory → political_legitimacy`, an adjacent-but-distinct political-philosophy tuple — confirming the shape that legitimacy/obligation/contract form a cluster but not flagging this specific edge).

### E-26 — d0aa112d-ef1f-4058-bdb7-e8f555e0e877
EDGE: Explosion Principle [explosion_principle, logic] → Paraconsistent Logic [paraconsistent_logic, logic]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Explosion (ex contradictione quodlibet — from a contradiction, any conclusion follows; the classical-logic theorem (A ∧ ¬A) → B); paraconsistent logic (Priest, da Costa) rejects explosion (allows contradictions without trivialization). Standard → its rejection-via-counter-system, canonical Sound shape; pairs with E-12 bivalence_principle → dialetheism (this shard) — both rejection-of-classical-tenet edges, with dialetheism as the philosophical thesis and paraconsistent logic as the formal-logic family that accommodates it.
AUDIT-TOUCHED: none (0063 proximity-only on `paraconsistent_logic` — 0063 deletes `bivalence_principle → paraconsistent_logic`, a different tuple).

### E-27 — d07367f6-eb7f-4a91-a9ec-c05dbba5fd74
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Understanding [understanding, epistemology]
  weight=1.0, confidence=1.0, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional knowledge (knowing-that p) is the well-developed canonical epistemic state; understanding (Pritchard 2010 *Epistemological Disjunctivism*; Kvanvig 2003 *The Value of Knowledge and the Pursuit of Understanding*; Zagzebski 2001 — grasping how a body of information hangs together explanatorily) is a distinct cognitive achievement contemporary epistemology has marked off from propositional knowledge. Pedagogical sequence: introduce knowledge first (the historically dominant target of analysis), then introduce understanding as the cognate-but-distinct state. Cognate-state → cognate-state on the establish-canonical-then-introduce-cousin reading, Sound. Pairs with E-21 propositional_knowledge → testimonial_knowledge as two edges from the same source on different sub-relations (E-21: source-of-instances; E-27: cognate-state).
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — kripke_semantics
NODE: Kripke Semantics [kripke_semantics, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (978c) walk through the pre-Kripke landscape (C.I. Lewis S1-S5 syntactically motivated, no clear interpretive framework), Kripke's structural contribution (possible-worlds + accessibility as the unifying semantic interpretation), and the completeness theorem as the load-bearing achievement (each axiomatic modal system pairs with a frame class). Strong.
C3 (summary cold-readability): yes — the formal model is laid out explicitly as a triple ⟨W, R, V⟩ with each component glossed inline (W = non-empty set of possible worlds, R ⊆ W × W = accessibility relation, V = valuation); the recursive truth-clause for □ is stated; the completeness pairings between modal-systems (K, T, B, S4, S5) and frame-classes (no constraint, reflexive, symmetric, transitive, equivalence-relational) named. The structural-shape gloss carries the technical content.

### N-2 — liberty_political
NODE: Liberty (Political) [liberty_political, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1298c) walk through the three concepts students should keep separate (negative liberty: non-interference; positive liberty: self-mastery; republican liberty: non-domination), the Berlin 1958 *Two Concepts of Liberty* anchor, contemporary republican developments (Skinner, Pettit), and the social-justice tension (Berlin's worry about positive liberty's totalitarian potential vs Taylor's defense as genuine concept). Strong.
C3 (summary cold-readability): yes — "the absence of constraints on a person's ability to do or be what they have reason to value" is fully accessible; the Berlin 1958 *Two Concepts of Liberty* anchor supplies the canonical distinction between negative liberty (non-interference, Hobbes-Hayek-Berlin) and positive liberty (self-mastery, Hegel-Marx); the republican-liberty third option (Skinner, Pettit — non-domination) named.

### N-3 — business_ethics
NODE: Business Ethics [business_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extremely extensive (2624c) walk through the field's three principal frames (stakeholder vs shareholder theory, corporate moral agency, market-and-justice macroethics), with named anchors per frame (Friedman 1970 / Freeman 1984 / French 1984 / Velasquez); applied topics enumerated (whistleblowing, corporate-social-responsibility, marketing-ethics, international-business-ethics, finance-ethics, sustainability); pedagogical recommendation to teach the field as the intersection of normative theory with institutional economics. Strong.
C3 (summary cold-readability): yes — "branch of applied ethics treating moral questions arising in commercial activity, business management, and corporate governance" is fully accessible; the obligation-targets enumerated (shareholders, employees, customers, suppliers, communities, the environment); founding works dated (Beauchamp & Bowie 1979, Donaldson 1989, Werhane); business-ethics pedagogy as field-tradition framing supplied.

### N-4 — value_free_ideal
NODE: Value-Free Ideal [value_free_ideal, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1949c) walk through the classical position (Reichenbach's context-of-discovery / context-of-justification; logical positivist program; Weber 1917 on social science), three lines of critique (Rudner 1953 inductive risk: every hypothesis-acceptance trades off Type I vs Type II error so non-epistemic values inevitably enter; Longino 1990 contextual values shape evidence-relations; Douglas 2009 the institutional role of science makes value-freedom incoherent), and the modified-value-free-ideal compromise. Strong.
C3 (summary cold-readability): yes — the position is stated transparently ("scientists should not let non-epistemic values (moral, political, social, economic) influence their judgments about which hypotheses to accept and what counts as evidence"); the contemporary critics named (Rudner 1953, Longino 1990, Douglas 2009); the "evidence sufficiency assessment requires non-epistemic value judgments" critique articulated.

### N-5 — truth_conditional_semantics
NODE: Truth-Conditional Semantics [truth_conditional_semantics, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1483c) walk through why the program has been dominant (Davidson's "Truth and Meaning" 1967 program, Tarskian truth-definitions as the formal apparatus, Montague's 1970s formal extension); the compositionality argument (truth-conditions compose because syntax composes); the inference-explanation argument (truth-conditions explain why some inferences are valid); standard objections (Wittgenstein meaning-as-use; speech-act conventions can't be captured by truth conditions; expressivism in metaethics). Strong dialectical scaffold.
C3 (summary cold-readability): yes — the program statement is self-glossing ("the meaning of a sentence with its truth conditions — the conditions under which the sentence is true; to know what a sentence means is to know what would have to be the case for it to be true"); Davidson 1967 dated; Tarski-Davidson formal program supplied as the canonical instantiation.

### N-6 — epistemic_dependence
NODE: Epistemic Dependence [epistemic_dependence, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames epistemic dependence as the inevitable upshot of the division of cognitive labor; introduces the topic via near-universal applicability (almost nothing any individual justifiably believes is first-hand evidence); pedagogical entry via the contrast between epistemic individualism (Cartesian self-sufficiency) and the dependence framework (Hardwig 1985 *Journal of Philosophy* article). Brief (415c) but functional foothold.
C3 (summary cold-readability): yes — "the condition in which a believer's justified belief depends on others' epistemic states — the testifier's reliability, the expert's competence, the community's collective practice" is fully accessible; John Hardwig 1985 *Journal of Philosophy* "Epistemic Dependence" cited as the founding statement; the division-of-cognitive-labor framing supplies the macro-setting.

### N-7 — proper_name
NODE: Proper Name [proper_name, language], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1283c) dialectical setup ("how does 'Aristotle' pick out Aristotle?"), three positions laid out (descriptivism: early Russell, late Frege, Searle — names abbreviate descriptions; Millianism / direct reference: Kripke 1980, Donnellan, Putnam — names are rigid designators; causal-historical theory: Kripke's baptism-and-chain account), and the contemporary integration (two-dimensional semantics, predicativism). Strong.
C3 (summary cold-readability): yes — "linguistic expression that refers to a particular individual" is fully accessible; three paradigm examples (Aristotle, Venus, Mount Everest) carry the concept; the descriptivism-vs-direct-reference dispute named as the central twentieth-century debate; Kripke 1980 *Naming and Necessity* as the watershed reference work.

### N-8 — compatibilism
NODE: Compatibilism [compatibilism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Frankfurt 1971 "Freedom of the Will and the Concept of a Person" hierarchical structure (first-order desires harmonized with second-order volitions); the Frankfurt-cases against the principle of alternate possibilities (the demon stand-by who would intervene if you tried to choose otherwise but doesn't because you choose what they want anyway); Strawson 1962 *Freedom and Resentment* reactive-attitudes defense (compatibilist freedom is whatever underwrites our reactive practices). Strong dialectical scaffold.
C3 (summary cold-readability): yes — "the view that free will is compatible with determinism — that we can be free even if the past plus the laws of nature fix everything we do" is fully accessible; "determinism" load-bearing but glossed inline; classical compatibilism (Hume) introduced via its analysis of free action; contemporary developments (Frankfurt-hierarchical, reasons-responsive) named.

### N-9 — mctaggarts_paradox
NODE: McTaggart's Paradox [mctaggarts_paradox, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — two-stage argument structured pedagogically (Stage 1: B-series alone is insufficient because earlier-than/later-than relations are static, nothing tells us what TIME it is; Stage 2: A-series is self-contradictory because every event must be past, present, and future, mutually-incompatible determinations); the standard A-theorist response (tensed-fact / present-as-the-only-real defense). Compact (666c) but well-structured foothold.
C3 (summary cold-readability): yes — borderline-PASS. McTaggart 1908 dated; the A-series and B-series load-bearing technical terms appear without explicit gloss BUT the structural-shape gloss is supplied immediately ("the A-series is self-contradictory (every event is past, present, and future, which are incompatible determinations); the B-series alone cannot account for genuine temporal change because relations of earlier-than/later-than are static"). Same calibration as shard 17 N-10 pyrrhonian_skepticism's *epoché*/*ataraxia* — load-bearing technical terms gated through immediate inline structural gloss.

### N-10 — aesthetic_disinterest
NODE: Aesthetic Disinterest [aesthetic_disinterest, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — pedagogical framing of the aesthetic-attitude tradition (Kant 1790, Schopenhauer 1819, Bullough 1912 "psychical distance," Stolnitz 1960, Aldrich 1963); the contemporary status (Dickie 1964 "The Myth of the Aesthetic Attitude" critique — there's no special psychological attitude, only ordinary attention to aesthetic features; Carroll's 2001 selective defense — disinterest survives as a criterion of relevance even after Dickie). Strong.
C3 (summary cold-readability): yes — "the appropriate aesthetic engagement with an object suspends practical interest in the object — the observer attends to the object for what it is rather than for what it can do for them" is fully accessible; the Kantian "disinterested pleasure" inheritance named; the contrast with practical/cognitive/moral engagement supplies the working differential.

### N-11 — libertarianism_metaphysical
NODE: Libertarianism (Metaphysical) [libertarianism_metaphysical, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the luck objection introduced as the central challenge (if determinism is false at the moment of choice, what determines which choice? If nothing, choice is random not free); event-causal libertarianism (Kane 1996 *The Significance of Free Will* — self-forming actions resolve in indeterministic neural-attention episodes); agent-causal libertarianism (O'Connor 2000 *Persons and Causes*; Clarke 2003 — irreducible agent-cause distinct from event-causation); the dualist commitments many agent-causal accounts carry. Strong.
C3 (summary cold-readability): yes — "the metaphysical position that we have free will and that this requires the falsity of determinism — at least for the actions we count as freely chosen" is fully accessible; the disambiguation from political libertarianism (right-libertarianism Nozick, left-libertarianism Otsuka, libertarian-paternalism Thaler-Sunstein) explicit in the opening — flagging the term's two senses.

### N-12 — aesthetic_property
NODE: Aesthetic Property [aesthetic_property, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — the realism question framed as the entry point (Sibley 1959 "Aesthetic Concepts" — aesthetic properties real but require taste to perceive, competent observers under appropriate conditions converge); the supervenience question (aesthetic properties supervene on non-aesthetic descriptive properties — the same painting can't have different aesthetic properties without different descriptive properties); irreducibility (cannot be reduced to those descriptive properties); contemporary positions (Levinson 2001 / Goldman 1995). Strong.
C3 (summary cold-readability): yes — paradigm examples enumerated in the opening (beauty, ugliness, gracefulness, elegance, balance, harmony, sublimity); "aesthetic discourse" load-bearing but example-grounded; cognitive/emotional/expressive aesthetic-property sub-categories supplied; the metaphysical-realism question framed.

### N-13 — expressivism
NODE: Expressivism [expressivism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive (1307c) walk through the basic move (interpret "murder is wrong" as expressing disapproval-of-murder rather than describing the property of wrongness inhering in murder); the Frege-Geach problem (logical embedding "if murder is wrong, then ... " requires sub-sentences to have content that survives embedding, hard for expression-of-attitude readings); contemporary expressivist responses (Blackburn 1984 quasi-realism: earn truth-talk via projectivist commentary; Gibbard 1990 norm-expressivism, 2003 plan-expressivism: utterances express plans, plans embed under conditionals naturally; minimalism + expressivism). Strong dialectical scaffold.
C3 (summary cold-readability): yes — "moral utterances do not describe facts but EXPRESS attitudes — emotions, prescriptions, plans, normative commitments" — the position is self-glossing via the contrast with descriptivism; classical exemplars dated (Stevenson 1937 emotivism, Hare 1952 prescriptivism); contemporary developments named (Blackburn, Gibbard).

### N-14 — perception
NODE: Perception [perception, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three classical questions framed (metaphysical: direct-vs-indirect realism; epistemic: how perception justifies beliefs; phenomenological: what perception is like); the contemporary realism options (direct realism / sense-data / adverbialism / disjunctivism / representationalism) enumerated; the contemporary debate framing. Strong.
C3 (summary cold-readability): yes — "the mental states by which an organism becomes aware of its surroundings via the senses" is fully accessible; three philosophical question-types (objects, justification, phenomenology) supply the working analytical framework; the perception-cognition distinction (cognitive penetration) flagged.

### N-15 — testimonial_knowledge
NODE: Testimonial Knowledge [testimonial_knowledge, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — two-camps framing (reductionists Hume — require hearer to have independent evidence for speaker's reliability; anti-reductionists Reid, Coady — testimony as sui generis source). Brief (304c) but functional foothold.
C3 (summary cold-readability): yes — "knowledge acquired by accepting a speaker's assertion" is fully accessible; the social-epistemology connection ("most of what any individual knows comes from testimony rather than first-hand evidence") supplies the macro-importance framing; the central question ("what makes testimony a genuine source of knowledge?") explicit.

### N-16 — multiculturalism
NODE: Multiculturalism [multiculturalism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extremely extensive (2449c) walk through the position's two roots (communitarian critique of liberal individualism via Taylor 1992 "The Politics of Recognition," Sandel; liberal political theory via Kymlicka 1995 *Multicultural Citizenship* — minority groups need group-differentiated rights to flourish), the internal tensions (Okin 1999 "Is Multiculturalism Bad for Women?" — group rights can entrench intra-group oppression; Barry 2001 *Culture and Equality* — liberal universalism critique). Strong.
C3 (summary cold-readability): yes — "the political-philosophy position holding that liberal-democratic societies should accommodate the cultural and group identities of their members through group-differentiated rights" is fully accessible; concrete operationalizations enumerated (group-differentiated rights, language recognition, religious accommodation); Taylor 1992 / Kymlicka 1995 named.

### N-17 — infinitism
NODE: Infinitism [infinitism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — frames infinitism as the minority view, the third logical possibility in the regress trilemma (terminate / circle / continue forever); Klein's defense (only option compatible with epistemic responsibility and the non-arbitrary-stopping requirement); the principal objection (humans don't have infinite cognitive resources, so infinitism describes no actual human cognition). Compact (280c) but well-targeted foothold.
C3 (summary cold-readability): yes — "Peter Klein's structural thesis that justified beliefs are justified by infinite, non-repeating chains of reasons" is fully accessible; the trilemma framing explicit ("rejects both the foundationalist's terminating chain and the coherentist's circular structure"); Klein named as the founder.

### N-18 — type_b_materialism
NODE: Type-B Materialism [type_b_materialism, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Chalmers 2003 / 2007 type-A/B/C/D taxonomy framing (type-A: deny gap, type-B: gap is conceptual not metaphysical, type-C: gap closeable in principle, type-D: gap is metaphysical = property dualism); the phenomenal-concepts strategy (special introspective concepts of phenomenal states have a different mode of presentation than physical-functional concepts of the same physical state, so the conceivability of zombies follows without supporting their metaphysical possibility); contemporary defenders (Loar 1990, Papineau 2002, Hill 1997). Strong.
C3 (summary cold-readability): yes — "physicalism that accepts the conceptual / explanatory gap between physical and phenomenal descriptions but holds that the gap is conceptual, not metaphysical" — the position is self-glossing via the conceptual-vs-metaphysical distinction; Chalmers's taxonomic placement (between type-A denial and type-D property dualism) framed.

### N-19 — epistemic_injustice
NODE: Epistemic Injustice [epistemic_injustice, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Fricker 2007 *Epistemic Injustice* anchor with two paradigm cases (a witness disbelieved on basis of race = testimonial injustice; a victim of sexual harassment lacking the concept = hermeneutical injustice — pre-1970s "sexual harassment" wasn't conceptually available as a category) carrying the concepts; the pedagogical entry via specific concrete examples. Brief (417c) but functionally well-targeted.
C3 (summary cold-readability): yes — both sub-types glossed inline parenthetically ("testimonial injustice (unfairly low credibility assigned because of identity-prejudice) and hermeneutical injustice (the structural absence of concepts ...)"); Fricker 2007 named; the wrong-done-to-a-knower-as-knower framing supplies the conceptual position.

### N-20 — what_its_like
NODE: What It Is Like (Nagel) [what_its_like, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Nagel 1974 "What Is It Like to Be a Bat?" pedagogical scaffold: even complete physical knowledge of a bat (echolocation system, neural architecture, behavior) does not give us imaginative access to its phenomenal point of view (the subjective character of echolocation experience); the argument's role in motivating the explanatory-gap intuition that Type-A materialists deny, Type-B materialists explain away, Type-C materialists promise to close, and Type-D materialists take as evidence for dualism; Jackson 1986 *Mary's Room* pairing as the conceptually-cleaner sibling argument. Strong.
C3 (summary cold-readability): yes — "a creature has conscious experience if there is something it is like, for that creature, to be that creature" is the self-glossing canonical statement; Nagel 1974 dated; the subjective-vs-objective framing supplies the working analytical distinction; bat-echolocation example invoked.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0
- Defensible: 3 (E-13 biocentrism → animal_ethics — specific-position → broader-field; E-19 temporal_parts → mereology — specific-application → general-formalism; E-25 political_obligation → conservatism — topic → broader-tradition)
- Audit-touched: 0 (first shard in the routine batch with zero audit-touched edges)

## Cross-cutting observations

**NINTH consecutive 0-defect shard (10–18).** Shards 10/11/12/13/14/15/16/17/18 all 0/27. C1 cumulative across 01–18 = 23/488 = 4.71%, continuing to tick DOWN from the 4.99% mark at shard 17, well below the 13% production-audit baseline. The 0-defect run is now NINE consecutive shards (prior longest the same run, now extended). Composition-driven: the pre-sharding random sample is hitting the audit-cleaned regions of the graph; shards 18–19 + closeout (SQA-20) remain. The 4.71% cumulative-rate over 488 of 516 edges (94.6%) is materially below 13% and the residual 28 edges in shard 19 would have to be 100% defective to bring the cumulative to even 9.7% — so the census's headline finding is settled regardless of shard 19's outcome.

**Defensible sub-shape stabilizes — third exemplar set of "specific → broader" inverted shape.** This shard's three Defensibles (E-13 biocentrism → animal_ethics, E-19 temporal_parts → mereology, E-25 political_obligation → conservatism) all share the "specific-position / specific-topic / specific-application → broader-field / broader-tradition / broader-formalism" inverted-from-canonical shape that shard 17 introduced (E-5 testimonial_knowledge → social_epistemology, E-6 consequentialism → supererogation). The sub-shape now has at least FIVE exemplars across two consecutive shards; the "specific → broader" inverted pattern is empirically a meaningful Defensible class within the routine batch, distinct from the prior framework→concept (shard 13/14), canonical-direction-inversion / 0064 retain-with-annotation (shard 14/15/16), and co-fundamental-category (shard 16) sub-shapes. SQA-20 calibration question for this sub-shape (carried from shard 17, sharpened by shard 18's three-in-one): when should an edge running specific → broader score Defensible vs Reversed? The foothold-into-bigger-field (E-13, E-19) and foil-into-tradition (E-25) readings all have force; held at Defensible across all five exemplars; the closeout adjudicates the threshold and whether the inverted shape merits a validator soft-warn flag (`prereq_canonical_direction_inversion` candidate, deferrable).

**First shard with zero audit-touched edges in the routine batch.** Workflow note: ZERO of shard 18's 27 edges carry inline `evidence` text — the gold signal per shards 13–17 workflow learnings. The programmatic proximity check returned 9 raw proximity hits across migrations 0061–0065 (filter 0060 applied), narrowed to ONE EXACT-TUPLE hit (E-22 `evidence → bayesian_epistemology` against 0063's tuple list), and per-hit exact-tuple inspection of that hit confirmed it as a false-positive — the 0063 SQL postcondition references `evidence` (the column name) AND `('bayesian_epistemology','dutch_book_argument')` (a different edge tuple), not the `evidence → bayesian_epistemology` edge. ALL 9 proximity hits resolve to false positives via either (a) different tuple sharing a node name (E-1 time, E-4 set/kripke_semantics, E-6 possible_worlds/kripke_semantics, E-7 pyrrhonian_skepticism, E-12 bivalence_principle, E-13 animal_ethics, E-26 paraconsistent_logic, E-27 propositional_knowledge) or (b) keyword collision with SQL column name (E-22 evidence). The workflow conclusion across shards 13–18 hardens: inline `evidence` text is the necessary-and-sufficient gold signal for audit-touched edges; proximity hits without inline evidence are uniformly false-positives across SIX consecutive shards. Recommendation for SQA-20 aggregation: rely on inline `evidence IS NOT NULL` as the audit-touched filter; treat proximity-without-evidence as a heuristic that consistently produces false positives.

**Two-edge introduction-of-the-debate cluster: scientific realism.** E-15 scientific_realism → no_miracles_argument (argument-for) + E-24 scientific_realism → pessimistic_meta_induction (argument-against) form a two-edge cluster from a single source pedagogically introducing both sides of the realism debate within one shard. Same structural shape as the multi-edge framework-decomposition clusters in prior shards (shard 16 four_principles_bioethics → three principles; shard 14 virtue_ethics → eudaimonia + three sibling edges). Notable for SQA-20: this is the first arguments-for-and-against cluster from a single source observed in the routine batch — the seed graph encodes both sides of the realism debate via two prerequisite edges, a clean two-step pedagogical setup.

**Two-edge sub-relation cluster: propositional knowledge.** E-21 propositional_knowledge → testimonial_knowledge (source-of-instances sub-relation) + E-27 propositional_knowledge → understanding (cognate-state sub-relation) form a two-edge cluster from a single source. Distinct from the realism-debate cluster (E-15 + E-24): there the two edges encode argument-for and argument-against of the same position; here the two edges encode different sub-relations between the same source (knowledge) and two distinct downstream targets. Notable for SQA-20: the seed graph's epistemology subdomain has a clean radial topology from `propositional_knowledge` as a central pedagogical anchor (also recall shard 17 E-5 testimonial_knowledge → social_epistemology and shard 17 E-3 evidence → epistemic_justification edges populate the same neighborhood).

**Two-edge logic rejection-cluster: paraconsistent family.** E-12 bivalence_principle → dialetheism (philosophical thesis) + E-26 explosion_principle → paraconsistent_logic (formal-logic family) form a two-edge cluster around the paraconsistent program: dialetheism (Priest) is the philosophical thesis that some contradictions are true; paraconsistent logic is the formal family of logics that accommodate dialetheic theses without trivializing. The two edges together pedagogically scaffold the dialetheic-paraconsistent neighborhood — introduce the classical tenets (bivalence, explosion) and their rejection-by-counter-system. Same standard-then-rejection shape as shard 16's four-edge position-and-rejection cluster but here distributed across two source-target pairs rather than four parallel edges from the same source.
