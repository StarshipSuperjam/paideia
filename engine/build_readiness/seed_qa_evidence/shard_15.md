# Seed-graph QA census evidence — shard 15

> Authored by S-0177 (routine session) per T-SEED-QA task SQA-15.
> Scoring per engine/build_readiness/seed_qa_audit.md.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Shard metadata
- Shard: 15
- Edges scored: 27
- Nodes scored: 20
- Scored: 2026-05-15

## Edge findings (C1)

### E-1 — c6d7bc45-45bb-4409-968a-8b61a6776444
EDGE: Moral Realism [moral_realism, ethics] → Moral Non-Naturalism [moral_non_naturalism, ethics]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Moral realism is the umbrella metaethical thesis (there are objective moral facts); moral non-naturalism (Moore 1903) is one specific realist position holding moral properties are non-natural. Umbrella → specific-variant, same shape as shard 12 E-18 deontology→kantian_ethics (Sound) and shard 10 E-19 reductionism_in_science→multiple_realizability_in_science (Sound).
AUDIT-TOUCHED: none

### E-2 — 8b50f055-4704-4bfc-af6a-caffa4a38de8
EDGE: Liar Paradox [liar_paradox, logic] → Curry's Paradox [curry_paradox, logic]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: The Liar (canonical self-referential semantic paradox) is the historical and pedagogical anchor for the paradox family; Curry's paradox (Curry 1942) is a related semantic paradox using conditional self-reference, typically taught after the Liar as a related variant.
AUDIT-TOUCHED: none

### E-3 — eda785eb-1f08-40bf-afc5-7a6951aa4b3a
EDGE: Sorites Paradox [sorites_paradox, logic] → Epistemicism [epistemicism, logic]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: The sorites is the problem (vagueness paradox with the heap); epistemicism (Williamson 1994) is one canonical response (vagueness is ignorance of a sharp boundary). Problem → response, the recurring sound pattern.
AUDIT-TOUCHED: none

### E-4 — e8776462-e7db-4eb5-a10b-4762809deca1
EDGE: Representationalism (Consciousness) [representationalism_consciousness, mind] → Phenomenal Intentionality [phenomenal_intentionality, mind]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Representationalism (Tye, Dretske) identifies phenomenal character with representational content; phenomenal intentionality (Horgan/Tienson, Loar) is the later move that inverts the explanatory direction (phenomenal grounds intentionality). To grasp phenomenal intentionality you need first to grasp the representationalism framework establishing the relevant phenomenal-intentional relation, then see the inversion.
AUDIT-TOUCHED: none

### E-5 — 9facb8b2-74a7-4eab-9b79-238ae90d9cbe
EDGE: Physicalism [physicalism, mind] → Type-B Materialism [type_b_materialism, mind]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Physicalism is the broad ontological commitment; type-B materialism (Loar) is a specific physicalist position that accepts an explanatory gap but denies an ontological gap. Umbrella → specific-variant.
AUDIT-TOUCHED: none

### E-6 — 9fe38ce8-d524-4c32-b74e-bee120f36456
EDGE: Counterexample [counterexample, service] → Gettier Problem [gettier_problem, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Counterexample is the methodological concept (refutation by case); the Gettier problem is the canonical historical instance of refutation-by-counterexample for the JTB analysis of knowledge. Methodological-concept → its canonical instance.
AUDIT-TOUCHED: none (0060 cross-bridge — original authoring, not audit follow-up)

### E-7 — d983dc77-0d9d-4f74-b9a7-6db092bf3310
EDGE: Fictional Truth [fictional_truth, aesthetics] → Metaphor [metaphor, aesthetics]
  weight=1.0, confidence=NULL, evidence=Per S-0122 audit: Walton's make-believe framework extends to metaphor (1993 Metaphor and Prop Oriented Make-Believe); fictional-truth apparatus supplies a theoretical thread for certain contemporary metaphor treatments, though canonical SEP metaphor entry runs the opposite direction.
VERDICT: Defensible
RATIONALE: Walton's make-believe / fictional-truth framework supplies one specific contemporary thread on metaphor; metaphor is the older, broader concept (pre-Walton Aristotle, Black 1962, Davidson 1978) and does not require fictional-truth machinery on most readings. Defensible on the Walton-aligned reading the 0064 audit accepted; canonical SEP runs the reverse. Same retain-with-annotation shape as shard 13 E-19 (0063 retain-with-annotation).
AUDIT-TOUCHED: migration 0064 AES-E-3 — evidence backfill / retain-with-annotation; audit explicitly noted canonical SEP inverts but kept the migration's framing.
EVIDENCE NOTE: inline `evidence` text confirms the audit decision.

### E-8 — a4474c6c-0e39-4666-af44-1a9b104a6989
EDGE: Gettier Problem [gettier_problem, epistemology] → No-False-Lemmas Response [no_false_lemmas_response, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: The Gettier problem is the explanandum; the no-false-lemmas response (Clark 1963) is one of the canonical responses. Problem → response.
AUDIT-TOUCHED: none

### E-9 — 1a3db128-4b3a-4de4-b9ab-b1bad9a7f932
EDGE: Truth Value [truth_value, service] → Argument (Logical) [argument_logical, service]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Truth-values (T/F or whatever the system admits) are the semantic primitives required to define validity, soundness, and inference; the concept of a (logical) argument presupposes truth-values to articulate "true premises guarantee true conclusion." Definitional dependency.
AUDIT-TOUCHED: none

### E-10 — 9a1107ca-5014-4714-996b-6f6af70a63ff
EDGE: Social Epistemology [social_epistemology, epistemology] → Peer Disagreement [peer_disagreement, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Peer disagreement as a technical term (epistemic peers + steadfast/conciliationist debate) is coined within social epistemology. The technical concept presupposes the discipline that gave it its precisification; the everyday phenomenon of people disagreeing is distinct from the technical concept. Sound on the technical-concept-from-discipline reading consistent with shard 14 E-21 / shard 12 E-26.
AUDIT-TOUCHED: none

### E-11 — 23167c93-aa4b-41c8-9081-cc3957d82dda
EDGE: Truth [truth, epistemology] → Tarski's T-Schema [tarskis_t_schema, language]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Truth is the broader semantic concept; Tarski's T-schema (1933 "Concept of Truth in Formalized Languages") is the formal disquotational apparatus on the side of analyzing truth predicates. Concept → formal analysis. (Proximity-only hit on 0062 — `deflationary_theory_of_truth → tarskis_t_schema` was flipped, that is a different edge.)
AUDIT-TOUCHED: none

### E-12 — 47d1a0c3-597f-46b8-a2a4-ef2c78fb1b01
EDGE: Proper Name [proper_name, language] → Descriptivism (Theory of Reference) [descriptivism, language]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Proper names are the linguistic-semantic category; descriptivism (Frege, Russell) is one theory of how proper names refer (via abbreviated definite descriptions). Phenomenon → theory of it.
AUDIT-TOUCHED: none

### E-13 — 80a36859-b1a9-4f11-bb25-f9eb8db11015
EDGE: Modality [modality, metaphysics] → Kripke Semantics [kripke_semantics, logic]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Modality is the metaphysical/semantic phenomenon (necessity/possibility); Kripke semantics is the possible-worlds model theory for modal logic. Phenomenon → formal model.
AUDIT-TOUCHED: none

### E-14 — a9d5809a-e4d6-4480-bc90-22e3e0d8da0f
EDGE: Knowledge [knowledge, epistemology] → Knowledge-First Epistemology [knowledge_first_epistemology, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Knowledge is the basic epistemological concept; knowledge-first epistemology (Williamson 2000) is the position that knowledge is primitive and other epistemic concepts are to be analyzed in its terms. Concept → its primitivist treatment.
AUDIT-TOUCHED: none

### E-15 — aa8220fa-bbf6-412e-a68f-61df1846e039
EDGE: Bioethics [bioethics, ethics] → Four Principles of Biomedical Ethics [four_principles_bioethics, ethics]
  weight=0.95, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Bioethics is the discipline; the Beauchamp & Childress four-principles approach (1979: autonomy, beneficence, non-maleficence, justice) is the dominant framework within it. Discipline → its dominant framework.
AUDIT-TOUCHED: none

### E-16 — 84e68f67-a74b-4fd9-b3be-aedb31b6c91e
EDGE: Problem of Induction [problem_of_induction, epistemology] → Bayesian Confirmation Theory [bayesianism_confirmation, science]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Hume's problem of induction is the canonical challenge to inductive inference; Bayesian confirmation theory is one principal response (a probabilistic account of how evidence confirms hypotheses). Problem → response.
AUDIT-TOUCHED: none

### E-17 — 782c4058-eb82-4eab-8c8e-2bc7dad52baa
EDGE: Kripke Semantics [kripke_semantics, logic] → Modal Systems Hierarchy [modal_systems_hierarchy, logic]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Kripke semantics supplies the model-theoretic apparatus; the modal systems hierarchy (K, T, S4, S5) is the corresponding axiomatic-semantic hierarchy classified by frame properties (reflexivity, transitivity, symmetry, euclideanness). You need Kripke semantics to characterize the hierarchy via frame conditions. Model-theory → axiomatic hierarchy.
AUDIT-TOUCHED: none

### E-18 — 8fd83596-eba1-4990-a52c-28a8631f1f24
EDGE: Reliabilism [reliabilism, epistemology] → Generality Problem [generality_problem, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Reliabilism (Goldman 1979) is the theory that justification = belief formed by a reliable process; the generality problem (Conee & Feldman 1998) is the canonical objection — any belief is formed by indefinitely many overlapping processes at different levels of generality, with no principled way to pick the relevant one. Theory → its canonical objection.
AUDIT-TOUCHED: none

### E-19 — b864a38b-c0f2-4036-ae0a-6b7845208087
EDGE: Functionalism (Philosophy of Mind) [functionalism, mind] → Computational Theory of Mind [computational_theory_of_mind, mind]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Functionalism (Putnam, Lewis) is the umbrella philosophy-of-mind position that mental states are individuated by functional roles; the computational theory of mind (Putnam, Fodor) is a specific functionalist program identifying functional roles with computational ones. Umbrella → specific program.
AUDIT-TOUCHED: none

### E-20 — e32a2745-9ccf-4b68-a2dd-3a0db2bd37a1
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Knowledge-How [knowledge_how, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Propositional knowledge (knowing-that-p) is the default epistemological topic; knowledge-how is introduced as the Rylean contrast (1949) or the Stanley & Williamson (2001) reduction. Either reading requires having understood propositional knowledge first. Pedagogical priority of the default epistemological concept.
AUDIT-TOUCHED: none

### E-21 — 590dfb11-0aa2-45fb-8d5c-a898b8fc1b41
EDGE: Social Contract Theory [social_contract_theory, political] → Political Legitimacy [political_legitimacy, political]
  weight=1.0, confidence=NULL, evidence=Per S-0122 audit: Social contract theory is the historical answer-family to the legitimacy question; the canonical SEP framing runs question-then-answers, but the migration treats the tradition as self-contained machinery that applies to legitimacy.
VERDICT: Defensible
RATIONALE: Social contract theory is one historical answer-family to legitimacy questions; legitimacy is the broader question that other frameworks (consent, hypothetical-rational-agreement, expressive/relational) also address. Canonical SEP framing puts the question first, then the answer-families. The 0064 audit accepted the migration's answer-precedes-question framing on the "self-contained tradition" reading. Defensible per the audit decision; second instance of the same 0064 retain-with-annotation shape this shard (paired with E-7).
AUDIT-TOUCHED: migration 0064 POL-E-6 — evidence backfill / retain-with-annotation; audit explicitly noted canonical SEP inverts (question-then-answers) but kept the migration's framing.
EVIDENCE NOTE: inline `evidence` text confirms the audit decision.

### E-22 — 10afad85-8b9b-48cb-842d-38f0c130c43d
EDGE: Liberty (Political) [liberty_political, political] → Negative Rights [negative_rights, political]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Political liberty (Berlin's negative-liberty sense: absence of interference) is the broader concept; negative rights (rights against interference: free speech, property, life) are the institutional/rights-framework articulation. Concept → its rights articulation.
AUDIT-TOUCHED: none

### E-23 — 3aae567b-f6fb-4a7d-91ae-61d8668fcf0b
EDGE: Political Philosophy [political_philosophy, political] → Equality (Political) [equality_political, political]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Political philosophy is the discipline; political equality is one of its central concepts/values. Discipline → central-concept-within-it, same shape as E-10 and E-15 this shard.
AUDIT-TOUCHED: none

### E-24 — 0af89830-be7e-4a78-bd85-7c51cd3494d8
EDGE: Propositional Knowledge [propositional_knowledge, epistemology] → Norm of Assertion [norm_of_assertion, epistemology]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: The norm of assertion debate (Williamson 1996: knowledge norm; alternatives: truth, belief, justification) concerns what is required for proper assertion. Propositional knowledge is the leading candidate norm; you need it as the candidate before you can debate whether it's THE norm. Concept → its normative role.
AUDIT-TOUCHED: none

### E-25 — fe44d4cb-ff15-4f29-9ef0-2f5d9d9d8050
EDGE: Modus Tollens [modus_tollens, service] → Propositional Logic [propositional_logic, logic]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Modus tollens (¬Q, P→Q ⊢ ¬P) is taught as a natural inference pattern before students see the full formal apparatus of propositional logic. The pedagogical order matches the edge direction — specific rule taught first as a natural pattern, then formalized within the containing system. Sound on pedagogical-priority of natural-inference-patterns over formal systems.
AUDIT-TOUCHED: none

### E-26 — 9c1fffe5-0e2f-4497-ac48-cb1172d96a1d
EDGE: Morality [morality, ethics] → Normative Ethics [normative_ethics, ethics]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Morality is the everyday practice/phenomenon; normative ethics is the philosophical sub-discipline that theorizes it. Practice-precedes-its-academic-study, consistent with prior shards' calibration on phenomenon-before-academic-discipline.
AUDIT-TOUCHED: none

### E-27 — da0850ff-ab22-4a90-8bac-6bfccbca1d83
EDGE: Aesthetic Property [aesthetic_property, aesthetics] → Aesthetic Value [aesthetic_value, aesthetics]
  weight=1.0, confidence=NULL, evidence=NULL
VERDICT: Sound
RATIONALE: Aesthetic properties (beauty, elegance, sublimity) are the features things have that make them aesthetically appraisable; aesthetic value is the normative dimension grounded in those properties. Properties → value-dimension built on them.
AUDIT-TOUCHED: none

## Node findings (C2 + C3)

### N-1 — is_ought_distinction
NODE: Is-Ought Distinction [is_ought_distinction, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — extensive treatment: Hume's TREATISE quotation, modest-vs-ambitious readings clarified, Searle 1964 promising-counterexample, motivations for moral non-naturalism / error theory / ethical naturalism.
C3 (summary cold-readability): yes — names what the distinction is (descriptive vs normative propositions) and what the claim is (no purely descriptive premise sufficient to derive a normative conclusion); Hume's-law alias supplied; technical terms (descriptive, normative, deductive, premise) either glossed or graspable from context.

### N-2 — luck_egalitarianism
NODE: Luck Egalitarianism [luck_egalitarianism, political], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Cohen / Arneson / Dworkin variants walked through; Anderson's relational-equality critique; contemporary alternatives (relational, sufficientarianism, prioritarianism). Strong foothold.
C3 (summary cold-readability): yes (borderline-PASS) — opening sentence inline-glosses "brute luck" (factors outside responsible control) and "option luck" (responsible choices); load-bearing terms are rescued by their parenthetical definitions. Same calibration as shard 11 N-3 IIT.

### N-3 — pacifism
NODE: Pacifism [pacifism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — four grounds (religious / deontological / consequentialist / non-violent-resistance pragmatism); Walzer 1977 supreme-emergency objection; Chenoweth & Stephan 2011 empirical claim. Strong.
C3 (summary cold-readability): yes — names the position (rejection of just-war permissibility), the two variants (absolute / contingent), historical anchors (Tertullian, Quaker, Buddhist, Jain, Tolstoy, Gandhi).

### N-4 — gettier_problem
NODE: Gettier Problem [gettier_problem, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — brief but pointed: original two-page paper, two canonical cases (ten coins, Brown in Barcelona), structural lesson. Adequate traction even at compact length.
C3 (summary cold-readability): yes — JTB encoded compactly as "justified true belief"; the puzzle stated cleanly (intuitively doesn't count as knowledge); standard case-shape glossed.

### N-5 — presentism
NODE: Presentism [presentism, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — ontological austerity, truthmaker objection, relativity-no-absolute-simultaneity reconciliation challenge; pedagogical-intuition vs metaphysical-demanding tradeoff named.
C3 (summary cold-readability): yes — "A-theoretic" is unglossed-but-immediately-glossed by "only the present time exists; past and future do not exist." The gloss IS the rest of the sentence. PASS on the rephrase-as-gloss reading consistent with shard 11 N-3 / shard 12 N-3.

### N-6 — climate_ethics
NODE: Climate Ethics [climate_ethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Gardiner's three storms (global / intergenerational / theoretical); emissions-equity metrics enumerated (per-capita / cumulative-historical / current / capacity-to-pay); adaptation funding; geoengineering. Strong.
C3 (summary cold-readability): yes — defines the field, enumerates the sub-questions explicitly, names the canonical scholars (Gardiner, Shue, Jamieson).

### N-7 — bioethics
NODE: Bioethics [bioethics, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Hippocratic anchor, 20th-century disruptions (Nuremberg, Tuskegee, Belmont 1979), Beauchamp & Childress four-principles, virtue-ethical / casuistic alternatives. Strong.
C3 (summary cold-readability): yes — defines the field (medicine + biomedical research moral questions); names the historical scandals; gives the institutional crystallization moments.

### N-8 — error_theory
NODE: Error Theory [error_theory, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Mackie's two arguments (relativity and queerness) each unpacked; response paths named (Mackie's "second-best," Garner abolitionist, Joyce 2001 fictionalist). Strong.
C3 (summary cold-readability): yes — cognitivism is glossed inline ("makes truth-apt claims"), the queerness argument is glossed ("intrinsically motivating in a way no plausible natural property is"). Mackie's two-prong structure laid out.

### N-9 — deep_ecology
NODE: Deep Ecology [deep_ecology, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three distinguishing features (metaphysical holism / equal intrinsic value / civilizational critique); influence (Earth First!, environmental-justice movement); contested points (Bookchin's social-ecology critique). Strong.
C3 (summary cold-readability): yes — names Naess 1973 origin, the shallow-vs-deep contrast, the Eight-Point Platform; the position is articulated up-front.

### N-10 — dutch_book_argument
NODE: Dutch Book Argument [dutch_book_argument, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — worked-case suggestion; Joyce's accuracy-dominance alternative as contemporary contrast. Adequate (brief but pointed).
C3 (summary cold-readability): yes (borderline-PASS) — "credences," "probability axioms," "synchronic/diachronic" are load-bearing technical terms unglossed in the opening clause, BUT the immediate rephrase ("there exists a set of bets each of which she rationally accepts but which together guarantee her a loss") supplies the structural shape a cold reader can grasp. Same calibration as shard 11 N-3 IIT, shard 12 N-3 formal_proof, shard 14 N-2 predicate_logic.

### N-11 — property
NODE: Property [property, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — granularity-principle deferral note; four basic ontological categories named. Adequate.
C3 (summary cold-readability): yes — paradigm cases (color, mass, shape, charge, moral character) make the concept immediately graspable; the work-the-concept-does framing (resemblance, change) is clean.

### N-12 — tropes
NODE: Tropes [tropes, metaphysics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — middle-position framing between universals and nominalism; costs articulated (resemblance primitive); connections to bundle theory and causation. Strong.
C3 (summary cold-readability): yes (borderline-PASS) — "abstract particulars" is a technical metaphysical term, but the apple-redness / rose-redness example is built into the second sentence and supplies the working gloss. PASS on the example-as-gloss reading consistent with prior shards.

### N-13 — virtue_responsibilism
NODE: Virtue Responsibilism [virtue_responsibilism, epistemology], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — distinguished from virtue reliabilism (truth-conducive faculties vs cultivated character); the reliable-but-uncultivated example (perceiving color) sharpens the distinction; Aristotelian connection named. Adequate.
C3 (summary cold-readability): yes — defines the branch (intellectual virtues as cultivated character traits); enumerates exemplars (open-mindedness, conscientiousness, courage, humility); cites Zagzebski.

### N-14 — deductive_nomological_model
NODE: Deductive-Nomological Model of Explanation [deductive_nomological_model, science], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — D-N schema setup, three counterexamples worked (symmetry/flagpole, irrelevance/Mr. Smith, statistical-explanation); post-D-N landscape (causal, mechanistic, IBE, unification). Strong.
C3 (summary cold-readability): yes — names Hempel-Oppenheim 1948; states the schema (sound deductive argument with universal law + initial conditions producing the explanandum); names the era and the canonical counterexamples.

### N-15 — taste_aesthetic
NODE: Taste (Aesthetic) [taste_aesthetic, aesthetics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Hume's problem and his five-fold qualification list walked through; subsequent debates (competent-judge identification, tradition-internal vs universal, constitutes-vs-indicates). Strong.
C3 (summary cold-readability): yes — Hume's "Standard of Taste" 1757 anchor; five qualifications enumerated (delicate organs, practiced perception, freedom from prejudice, comparison, sound understanding); both the realist and expert-authority commitments named.

### N-16 — qualia
NODE: Qualia [qualia, mind], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — realist / functionalist / eliminativist (illusionist) map; Dennett 1988 "Quining Qualia" and Frankish 2016 illusionism specifically; the pedagogical advice (treat qualia as contested theoretical posit, not phenomenological datum) is real foothold-work. Strong.
C3 (summary cold-readability): yes — paradigm cases (redness of red, painfulness of pain, sweetness of sugar) anchor the concept; the three positions in the central dispute are named in line.

### N-17 — greek_atomism
NODE: Greek Atomism [greek_atomism, service], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — doctrinal content enumerated (indivisibility, plurality, motion, rearrangement, chance); Epicurean swerve / clinamen; descendants (modern atomic theory, philosophical materialism, reductionism). Strong.
C3 (summary cold-readability): yes — historical anchors (Leucippus 5C BCE, Democritus, Epicurus); paradigm core posit (indivisible particles in empty void); transmission path (Lucretius DE RERUM NATURA).

### N-18 — supererogation
NODE: Supererogation [supererogation, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — three-category structure (obligatory / permissible / supererogatory) sharply distinguished; demandingness objection (Williams 1973, Singer 1972); deontology / virtue-ethics handling. Strong.
C3 (summary cold-readability): yes — clean three-way distinction articulated up-front (obligatory / permissible / supererogatory); paradigm examples (heroic self-sacrifice, charitable donations); the consequentialism-struggles flag is itself a useful pedagogical hook.

### N-19 — classical_logic
NODE: Classical Logic [classical_logic, logic], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — four commitments tightly-coupled framing; bivalence-pressure motivations (vagueness, future contingents, presupposition failure); classical-as-default note for the curriculum. Strong.
C3 (summary cold-readability): yes — defines the orthodox system; enumerates the four commitments (bivalence, LEM, LNC, explosion) with brief glosses; positions non-classical logics as departures.

### N-20 — hedonism
NODE: Hedonism [hedonism, ethics], status=active, confidence_level=INTERPRETED
C2 (teaching_notes traction): yes — Bentham's seven-dimensions vs Mill's quality-of-pleasure refinement; three classical objections (experience machine, content-indifference, Paretian); modern preferentism alternative. Strong.
C3 (summary cold-readability): yes — clean position-statement (pleasure as only intrinsic good, pain as only intrinsic bad); psychological-vs-ethical hedonism distinguished inline; Bentham/Mill anchors named.

## Shard tally
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0.0%) | C3 fail 0 (0.0%) | teaching_notes ABSENT 0

## Cross-cutting observations (optional)

- First shard where TWO audit-touched edges share the SAME 0064 audit-decision type (retain-with-annotation acknowledging canonical SEP inverts): E-7 fictional_truth → metaphor (AES-E-3) and E-21 social_contract_theory → political_legitimacy (POL-E-6) are both in the same 0064 assertion-block tuple list. Both scored Defensible per the audit's explicit "kept-with-acknowledged-inversion" framing. Worth flagging for SQA-20's audit-cross-reference clustering analysis — the 0064 retain-with-annotation class has multiple instances dispersed across shards, and this shard's two-in-one is the first co-occurrence.
- Sixth consecutive 0-defect shard (10/11/12/13/14/15). Cumulative C1 across 01-15: 23/407 = 5.65%, continuing the downward tick under the 13% production-audit baseline (was 6.05% at shard 14).
- No new Defensible sub-shapes this shard; the two Defensibles are both the established "0064 retain-with-annotation" class.
- C3 borderline-PASS calibration continues to hold under the rubric without further drift: four borderline cases this shard (N-2 luck_egalitarianism inline-gloss, N-5 presentism rephrase-as-gloss, N-10 dutch_book_argument rephrase-as-gloss, N-12 tropes example-as-gloss) all pass per the prior batch's calibration anchors.
