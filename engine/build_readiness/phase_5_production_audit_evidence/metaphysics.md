# Phase 5 production audit evidence — metaphysics

> Authored by S-0109 (routine session) per T-PHASE-5-AUDIT task AUDIT-MET.
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: metaphysics
- Edge population: 66 (30 from `0030_seed_metaphysics_part1.sql` covering being/ontology, identity, causation, time + 36 from `0036_seed_metaphysics_part1.sql` covering modality, free will, properties/universals, mereology)
- Edge sample size: 23; sample density: 23/66 = 34.8%
- Sample selection: deterministic md5(seed='AUDIT-MET' || source_id || '|' || target_id) ordering
- Node sample size: 12; selection: edge-anchored union (26 unique nodes from 23 sampled edges) ordered by md5(seed='AUDIT-MET' || node_id), take first 12
- Generation date: 2026-05-10

## Sampled-edge candidate findings

### Finding E-1
EDGE: concrete_object [domain=metaphysics] → mereology [domain=metaphysics]
   edge_type = pedagogical_prerequisite, weight/confidence/evidence not surfaced (per master-plan §T2-E empty `evidence` field is graph-wide; not penalized in verdict)
SEP-ANCHORED REASONING: SEP entry on "Mereology" frames the formal theory of parts and wholes around concrete particulars as the paradigm bearers of parthood (the ship, the lump, the cat). The standard pedagogical entry to mereology is the concrete-object case ("does the cat have legs as parts?") rather than the abstract case (sets vs members). Direction matches SEP framing: understanding what a concrete object is is prerequisite to asking how its parts relate to it.
VERDICT: sound
CONFIDENCE: high

### Finding E-2
EDGE: possible_worlds [domain=metaphysics] → haecceity [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Haecceitism" treats the haecceity construct (a non-qualitative thisness property) as a response to the transworld-identity problem in possible-worlds semantics — the question what makes Socrates-at-this-world the same individual as Socrates-at-some-other-world. The motivating problem only arises once possible worlds are on the table. Pedagogically you need possible-worlds machinery to motivate haecceities at all; the haecceity-vs-counterpart-theory choice (Adams, Plantinga vs Lewis) presupposes worlds.
VERDICT: sound
CONFIDENCE: high

### Finding E-3
EDGE: modality [domain=metaphysics] → essence_metaphysical [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Essential vs Accidental Properties" presents the post-Kripke modal-essentialist analysis as the modern default — an essence is the set of necessary properties — which makes the modality → essence direction correct: you need possibility/necessity machinery to define essential properties as those holding at every world. However, Kit Fine's "Essence and Modality" (1994) and the SEP entry on "Essence" reverse the dependency: essence is non-modal and prior; necessary truths are necessary BECAUSE of essences, not constitutive of them. The modal-essentialist framing pre-Fine and the Aristotelian / Finean framing post-1994 give different pedagogical orderings; the migration's choice (modality → essence) is the modern-modal-default direction. Direction is not the canonical SEP framing on the Finean reading but is supportable on the modal-essentialist reading.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Frameworks-vs-foundations ordering pattern — clusters with S-0105 E-2 (expertise → epistemic_dependence) and E-20 (bayesian_epistemology → dutch_book_argument) and S-0108 E-5 (motivational_internalism → expressivism). Mutation-implying for closeout if Fine's reversal is taken as authoritative; non-mutation if modal-essentialism is the curriculum's intended framing.

### Finding E-4
EDGE: modality [domain=metaphysics] → possible_worlds [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Possible Worlds" treats them explicitly as the semantic apparatus for modality: a proposition is necessarily true iff true at every possible world, possibly true iff at some. The pedagogical order is: introduce the modal notions (necessity, possibility — the things students already use in ordinary reasoning), then introduce possible worlds as the apparatus that interprets them rigorously. SEP entry on "Modality" itself organizes around modal logic and possible-worlds semantics in this order.
VERDICT: sound
CONFIDENCE: high

### Finding E-5
EDGE: numerical_identity [domain=metaphysics] → counterpart_theory [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Counterpart Theory" presents Lewis's account explicitly as an ALTERNATIVE to literal transworld identity. Counterpart theory replaces "Socrates at this world IS THE SAME as Socrates at that world" with "Socrates at this world has a counterpart at that world related by qualitative similarity." To understand what counterpart theory is doing — what it's denying — you need the strict numerical-identity notion it rejects. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-6
EDGE: existence [domain=metaphysics] → numerical_identity [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Identity" presupposes existing entities as the relata of the identity relation; the relation a=a presupposes that a refers to something. SEP entry on "Existence" notes the Quinean treatment via the existential quantifier, which is the same logical machinery underwriting identity claims. Pedagogically you cannot teach numerical identity without first having the notion of an existing thing for things to be identical to.
VERDICT: sound
CONFIDENCE: high

### Finding E-7
EDGE: time [domain=metaphysics] → b_theory_of_time [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Time" presents the A/B-theory distinction as the central framework for the metaphysics of time. B-theory is one of the two main positions; understanding it requires having the broader question — what is the metaphysical structure of time? — already in view. SEP entry on "Time" introduces B-theory as a position WITHIN the philosophy of time. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-8
EDGE: universals [domain=metaphysics] → tropes [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Tropes" introduces the trope construct (D.C. Williams 1953, Campbell 1990) explicitly as a middle position between realism about universals and austere nominalism. The dialectical role of tropes — abstract particulars that avoid both universals' regress problems and nominalism's reductive costs — only becomes intelligible once the universals dispute is on the table. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-9
EDGE: mereology [domain=metaphysics] → composition_mereological [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mereology" introduces parthood as the primitive relation, then derives composition (the relation of some objects making up a further object) from it. Van Inwagen's "Special Composition Question" is the canonical organizing question of contemporary mereology. Understanding composition requires understanding mereology's basic notions and axioms first.
VERDICT: sound
CONFIDENCE: high

### Finding E-10
EDGE: time [domain=metaphysics] → mctaggarts_paradox [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Time" presents McTaggart's argument as the foundational challenge to the reality of time — directly about time, so direction is correct. However, McTaggart's argument is technically formulated in terms of A-series and B-series, which means a more proximate prereq exists in the graph: `a_theory_of_time → mctaggarts_paradox` (E-17 in this sample). The pattern is a long-distance shortcut: time → mctaggarts_paradox runs over the more proximate time → a_theory_of_time → mctaggarts_paradox path. The shortcut edge is not strictly wrong (the paradox IS about time) but is redundant given the longer path is in the graph.
VERDICT: weak
CONFIDENCE: medium
NOTES: Parallel-edge weak/redundant pattern — clusters with S-0108 E-17 (virtue_ethics → moral_particularism) and E-20 (moral_realism → moral_epistemology). The closeout could prune the shortcut and keep the more proximate edge, OR keep both with a note that the shortcut conveys "the paradox is about time at a high level" while the proximate edge conveys "the paradox specifically attacks A-theory commitments." Mutation-implying.

### Finding E-11
EDGE: existence [domain=metaphysics] → relation [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Relations" treats relations as features borne jointly by existing relata. The category presupposes existing entities to bear the relations. Pedagogically, the basic ontological inventory (what kinds of things are there) is prerequisite to the question of how those things relate to each other.
VERDICT: sound
CONFIDENCE: high

### Finding E-12
EDGE: abstract_object [domain=metaphysics] → possible_worlds [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Possible Worlds" frames the metaphysical question of what worlds ARE as separate from the semantic role they play. On Lewis's modal realism (SEP entry on "Modal Realism" / "David Lewis"), possible worlds are CONCRETE — they are not abstract objects at all; they are spatiotemporal totalities exactly like the actual world but causally isolated. On ersatzist views (Plantinga, Stalnaker, Adams, Armstrong), possible worlds ARE abstract entities of various kinds. The migration's edge `abstract_object → possible_worlds` commits to the ersatzist family as the curriculum's framing — pedagogically supportable if the curriculum prefers ersatzism, but not the canonical SEP-neutral framing (which presents the ontological question as open). The Lewisian alternative would not require abstract_object as a prereq for possible_worlds.
VERDICT: defensible
CONFIDENCE: medium
NOTES: Substantive-content commitment — the edge encodes a metaontological choice (ersatzism over modal realism) that SEP treats as open. Closeout could (a) keep the edge with a note that it commits to ersatzism, (b) prune it as over-committing, or (c) add a parallel structure that handles both options. Mutation-implying.

### Finding E-13
EDGE: existence [domain=metaphysics] → modality [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Modality" treats necessity and possibility as features of how existing things could have been — the basic modal claims (it is necessary that 7+5=12; it is possible that I could have stayed home today) are about existing entities' actual or counterfactual properties. To understand modality you need the prior notion that things exist (or could). Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-14
EDGE: numerical_identity [domain=metaphysics] → leibniz_law [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Identity" presents Leibniz's Law (the indiscernibility of identicals + the contested identity of indiscernibles) as the principle GOVERNING the numerical identity relation. To state Leibniz's Law you must first have the notion of numerical identity it governs. Pedagogically: introduce a=b first (numerical identity), then introduce the principle that licenses substitution salva veritate (Leibniz's Law).
VERDICT: sound
CONFIDENCE: high

### Finding E-15
EDGE: ontology [domain=metaphysics] → existence [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Logic and Ontology" treats existence as the central question of ontology — Quine's "what is there?" is the canonical formulation. Ontology is the inquiry; existence is the topic-of-inquiry. Pedagogically you introduce ontology first as the discipline, then existence as its core question.
VERDICT: sound
CONFIDENCE: high

### Finding E-16
EDGE: a_theory_of_time [domain=metaphysics] → presentism [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Presentism" frames the view as one of the main A-theoretic positions (alongside growing-block and moving-spotlight). Understanding presentism requires having the A-theoretic framework — the claim that the present is metaphysically privileged — already in view. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-17
EDGE: a_theory_of_time [domain=metaphysics] → mctaggarts_paradox [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Time" presents McTaggart's argument as the canonical challenge specifically to A-theoretic positions: McTaggart argues the A-series is self-contradictory (every event is past, present, AND future). Understanding the paradox in its sharp technical form requires having A-theory's commitments in view as the target of the attack. SEP entry on "McTaggart's Argument" presents the dialectical structure as: A-theory's tensed framework is what the paradox exposes as contradictory. Direction sound; this is the more proximate prereq edge that E-10 (time → mctaggarts_paradox) shortcuts over.
VERDICT: sound
CONFIDENCE: high

### Finding E-18
EDGE: metaphysics [domain=metaphysics] → ontology [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Metaphysics" frames ontology (the inquiry into what exists) as a central branch of metaphysics. Pedagogically you need the broader notion of metaphysical inquiry first, then ontology as its first sub-branch. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-19
EDGE: causation [domain=metaphysics] → free_will [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Free Will" frames the contemporary debate around the causal-determinism dilemma: if the past + the laws fix the future causally, how can we be free? Understanding the free-will debate (compatibilism, determinism, libertarianism) requires having the causation notion already in view. SEP entry on "Causal Determinism" makes the dependency explicit. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-20
EDGE: concrete_object [domain=metaphysics] → composition_mereological [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mereology" frames composition (the special composition question) as primarily about concrete objects: when do some objects compose a further object? Standard examples (the ship, the lump of clay, organisms) are concrete particulars. Pedagogically you need the concept of a concrete object before asking under what conditions concrete objects compose larger concrete objects. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-21
EDGE: existence [domain=metaphysics] → abstract_object [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Abstract Objects" frames the abstract-object debate as a question about what kinds of things EXIST: do non-spatial, non-causal entities (numbers, sets, propositions) exist? The dependency is direct: abstract objects are a CATEGORY of existing thing (or candidate-existing thing), so the broader notion of existence is prerequisite.
VERDICT: sound
CONFIDENCE: high

### Finding E-22
EDGE: composition_mereological [domain=metaphysics] → mereological_nihilism [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Mereological Nihilism" presents nihilism as one of the answers to van Inwagen's Special Composition Question — the question composition_mereological encodes. Understanding nihilism (no objects compose any further object, except perhaps simples or organisms) requires having the composition question in view. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-23
EDGE: b_theory_of_time [domain=metaphysics] → eternalism [domain=metaphysics]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Eternalism (Philosophy of Time)" frames eternalism as the ontology that goes naturally with B-theory: if the present has no metaphysical privilege, then past and future must be just as real as present. Sider's "Four-Dimensionalism" defends the package. Pedagogically: B-theory's tenseless ordering is prerequisite for understanding why eternalism is the right ontology to pair with it.
VERDICT: sound
CONFIDENCE: high

## Sampled-node candidate findings

### Finding N-1
NODE: haecceity [domain=metaphysics]
   summary = "The non-qualitative property of being identical to a particular individual: the haecceity of Socrates is the property *being identical to Socrates*. Posited to ground transworld identity..."
SEP-ANCHORED REASONING: SEP entry on "Haecceitism" treats the haecceity as a specific technical posit in the transworld-identity dispute — atomic, specific, with named defenders (Adams, Plantinga, Rosenkrantz) and named opponents (Lewis). Concept-level granularity per ADR 0008: a single named technical construct, not a discipline label or thinker-framework. Summary reads with concrete specificity (Socrates as standing example, named alternative position via counterpart theory).
VERDICT: sound
CONFIDENCE: high

### Finding N-2
NODE: presentism [domain=metaphysics]
   summary = "The A-theoretic view that only the present time exists. Past entities (Socrates) and future entities (the first human born in the next millennium) do not exist..."
SEP-ANCHORED REASONING: SEP entry on "Presentism" presents the view as a specific A-theoretic position with named defenders (Prior, Bigelow, Markosian, Crisp). Concept-level granularity: a single position in a clearly-mapped dialectical space. Summary reads with concrete specificity (named defenders, named challenges, contrast with growing-block and eternalism).
VERDICT: sound
CONFIDENCE: high

### Finding N-3
NODE: a_theory_of_time [domain=metaphysics]
   summary = "The view that the A-series — the ordering of events by tensed properties (past, present, future) — captures a real feature of reality, and that the present is metaphysically privileged..."
SEP-ANCHORED REASONING: SEP entry on "Time" treats A-theory as a family of positions (presentism, growing block, moving spotlight) sharing a core commitment (metaphysical reality of tense). At the granularity boundary: arguably a position-family rather than a single atomic concept. However, "A-theory of time" is itself a SEP-recognized technical construct with a coherent shared core; the family-level treatment is standard pedagogical practice. Concept-level granularity is borderline-sound. Summary reads with instructional voice (frames the family commitment, contrasts with B-theory, names the three sub-positions).
VERDICT: sound
CONFIDENCE: medium
NOTES: Borderline at the granularity layer — A-theory is a family, but the family designation is itself a single SEP-recognized construct with a coherent shared core. Distinct in kind from the sub-discipline-with-content pattern (modality, mereology, moral_epistemology) where the node names a topical area not a position.

### Finding N-4
NODE: modality [domain=metaphysics]
   summary = "The metaphysics of necessity and possibility: what it is for a proposition to be necessarily true (true at every possible way the world could have been), what it is for it to be possibly true (true at some such way)..."
SEP-ANCHORED REASONING: SEP entry on "Modal Logic" / "Modality" treats modality as a SUB-DISCIPLINE / TOPIC AREA within metaphysics — not a single atomic concept. The summary itself frames it as "the metaphysics of necessity and possibility" — a topic label naming an inquiry, not a single position or technical construct. Concept-level granularity (per ADR 0008: atomic mastery unit, not a discipline label) is mismatched: modality is a sub-discipline housing many atomic concepts (necessity, possibility, possible_worlds, essence, modal_realism, etc.) — the children edges in the graph confirm this (modality → possible_worlds, modality → essence_metaphysical). Pattern parallels S-0105 N-8 (bayesian_epistemology) and S-0108 N-4 (moral_epistemology), N-9 (animal_ethics).
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Sub-discipline-label-with-content pattern — recurring graph-wide. Closeout should adjudicate at STRUCTURAL level (what to do with sub-discipline labels generally) rather than per-node disposition. Mutation-implying — could be (a) kept as a hub node with explicit sub-discipline status, (b) split into atomic children with the modality label retired, or (c) demoted to a non-pedagogical-prerequisite category-tag.

### Finding N-5
NODE: concrete_object [domain=metaphysics]
   summary = "A spatially located, causally efficacious entity: this rock, that person, the moon. Contrasts with abstract objects..."
SEP-ANCHORED REASONING: SEP entry on "Abstract Objects" treats the abstract/concrete distinction as basic to ontology, with concrete objects defined positively (spatiotemporally located, causally efficacious) or negatively (not abstract). Concept-level granularity: an atomic ontological category. Summary reads with instructional voice (concrete examples, contrast with abstract, role in downstream disputes).
VERDICT: sound
CONFIDENCE: high

### Finding N-6
NODE: mereology [domain=metaphysics]
   summary = "The formal theory of parts and wholes. Classical extensional mereology (Lesniewski, Goodman-Leonard) takes parthood as primitive and characterizes composition via a few axioms..."
SEP-ANCHORED REASONING: SEP entry on "Mereology" treats mereology as a SUB-DISCIPLINE / FORMAL THEORY — the body of work, not a single concept. The summary itself names it "the formal theory of parts and wholes" and references specific axiom-systems (Lesniewski, Goodman-Leonard). Concept-level granularity is mismatched: mereology is the discipline housing parthood, composition_mereological, simples, gunk, mereological_universalism, mereological_nihilism — all of which appear as separate nodes in the graph. The mereology node sits at sub-discipline-with-content granularity, parallel to modality (N-4) above and to S-0105 N-8 (bayesian_epistemology), S-0108 N-4 (moral_epistemology), N-9 (animal_ethics).
VERDICT: granularity-mismatch
CONFIDENCE: medium
NOTES: Sub-discipline-label-with-content pattern — same kind as N-4 modality. Closeout adjudicates structurally. Mutation-implying.

### Finding N-7
NODE: essence_metaphysical [domain=metaphysics]
   summary = "The properties an entity has of metaphysical necessity — those it could not lack while continuing to exist. The Aristotelian conception is non-modal..."
SEP-ANCHORED REASONING: SEP entry on "Essence" presents essence as a specific technical concept with a clear modal-essentialist analysis (necessary properties) and a contesting Finean analysis (essence prior to modality). Concept-level granularity: an atomic mastery unit, well-defined position-space. Summary reads with concrete specificity (Fine 1994 cited, three-position taxonomy named explicitly). The label `essence_metaphysical` (with the disambiguating suffix) correctly distinguishes it from other essence-uses (e.g., chemical essence) per the granularity principle.
VERDICT: sound
CONFIDENCE: high

### Finding N-8
NODE: eternalism [domain=metaphysics]
   summary = "The B-theoretic view that all times — past, present, and future — are equally real. The block universe contains all events at all times..."
SEP-ANCHORED REASONING: SEP entry on "Eternalism (Philosophy of Time)" presents eternalism as a specific B-theoretic position with named defenders (Sider, Mellor) and clear contrast (presentism, growing-block). Concept-level granularity: a single position in a clearly-mapped dialectical space. Summary reads with instructional voice (block-universe metaphor, four-dimensionalism connection, relativity alignment).
VERDICT: sound
CONFIDENCE: high

### Finding N-9
NODE: mctaggarts_paradox [domain=metaphysics]
   summary = "J.M.E. McTaggart's (1908) argument for the unreality of time: the A-series is self-contradictory (every event is past, present, and future, which are incompatible determinations); the B-series alone cannot capture genuine temporal change..."
SEP-ANCHORED REASONING: SEP entry on "Time" presents McTaggart's argument as a specific named historical argument (1908 paper, two-stage structure, named subsequent literature). Concept-level granularity: a single named argument with a specific dialectical role. Summary reads with concrete specificity (citation, two-stage structure, named A-theoretic and B-theoretic responses).
VERDICT: sound
CONFIDENCE: high

### Finding N-10
NODE: time [domain=metaphysics]
   summary = "The dimension of temporal experience and physical change. The metaphysical questions are whether time is a real feature of reality or a structuring feature of cognition, what its directionality consists in..."
SEP-ANCHORED REASONING: SEP entry on "Time" treats time as the central concept of an entire sub-area but ALSO as a single concept that organizes the A/B-theory dispute, McTaggart's paradox, persistence, and the philosophy-of-physics interface. Borderline at granularity: time COULD be marked sub-discipline-mismatch (parallel to mereology, modality), but it has stronger atomic-concept warrant — "time" names the conceptual subject matter that A-theory and B-theory dispute about, not just the inquiry-area. Compare to N-4 modality (which names an inquiry area whose subject matter is necessity / possibility) and N-6 mereology (which names the formal theory whose subject matter is parthood). The time node is at the same conceptual layer as `causation` and `existence` — basic metaphysical categories that name BOTH the inquiry and its subject matter; this is consistently treated as concept-level in the graph.
VERDICT: sound
CONFIDENCE: medium
NOTES: Distinct from the N-4/N-6 sub-discipline-label-with-content pattern — `time` names a metaphysical category (the temporal dimension), not just a sub-discipline; falls in the same class as `causation`, `existence`, `numerical_identity`. Closeout could revisit if the structural decision on N-4/N-6 sub-discipline labels also covers basic-category labels.

### Finding N-11
NODE: composition_mereological [domain=metaphysics]
   summary = "The relation that holds when some objects (the parts) make up a further object (the whole). The Special Composition Question (van Inwagen 1990): under what conditions do some objects compose a further object?..."
SEP-ANCHORED REASONING: SEP entry on "Mereology" treats van Inwagen's Special Composition Question as the canonical contemporary organizing question; composition is a specific named relation with a clear dialectical role (universalism vs nihilism vs moderate-views span the answer space). Concept-level granularity: an atomic concept (the composition relation) with a specific named question. Summary reads with concrete specificity (van Inwagen 1990 citation, three-position taxonomy).
VERDICT: sound
CONFIDENCE: high

### Finding N-12
NODE: abstract_object [domain=metaphysics]
   summary = "A non-spatial, non-causal entity: numbers, sets, propositions, possible worlds (on some accounts), types as opposed to tokens. The contrast class is concrete objects..."
SEP-ANCHORED REASONING: SEP entry on "Abstract Objects" treats abstract object as a basic ontological category with a clear contrast class (concrete objects). Concept-level granularity: an atomic ontological category, parallel to N-5 concrete_object. Summary reads with instructional voice (canonical examples, contrast class, motivating worries).
VERDICT: sound
CONFIDENCE: high

## Cross-cutting observations

Three load-bearing aggregate patterns surfaced for the closeout's synthesis surface:

1. **Sub-discipline-label-with-content granularity pattern recurs again** (N-4 modality, N-6 mereology). This is now the third subdomain audit to surface the same structural pattern — S-0105 N-8 (bayesian_epistemology), S-0108 N-4 (moral_epistemology), N-9 (animal_ethics) — confirming that sub-discipline labels housing atomic-concept children are graph-wide. Metaphysics-specific instances flagged here: modality and mereology. Other candidate-instances NOT in this sample but worth closeout cross-check: `causation` (sound here as a basic category, but borderline), `time` (marked sound at medium confidence with NOTES — distinct from sub-discipline-label-with-content pattern). Closeout should adjudicate at the structural level (a single decision covering all sub-discipline labels) rather than per-node.

2. **Parallel-edge weak/redundant pattern recurs** (E-10 time → mctaggarts_paradox shortcuts over the more proximate time → a_theory_of_time → mctaggarts_paradox path). This is the second subdomain audit to surface the pattern — S-0108 E-17, E-20 — suggesting it may be graph-wide. The S-0108 instances were species-level edges shadowing genus-level edges; this S-0109 instance is a longer-distance shortcut over a multi-hop path. Both are forms of the same redundancy class (a more proximate prereq exists in the graph). Closeout aggregate scan across all evidence files could surface a graph-wide cleanup pass.

3. **Substantive-content commitment edges encode metaontological choices** (E-12 abstract_object → possible_worlds commits to ersatzism over Lewisian modal realism; E-3 modality → essence_metaphysical commits to modal-essentialism over Finean essentialism). These are not defects under the routine prompt template (the migration is internally consistent) but are pedagogical-philosophical commitments worth marking for closeout dispositions. The curriculum may want to make the commitments explicit, OR add parallel structures, OR weaken to a more neutral framing.

Empty `evidence` field uniform null across all 66 within-metaphysics edges (master-plan §T2-E pre-listed; confirmed graph-wide again). No new gate-feasible audit-system-input class surfaced — the four pre-listed master-plan proposals plus S-0104's cross_bridge_pedagogical_direction_inconsistent_with_summary candidate were not extended (within-metaphysics data did not corroborate the cross-bridge-specific pattern; the parallel-edge pattern from S-0108 + this session is on track to qualify but the closeout adjudicates via aggregate scan).

Mid-sample expansion trigger (master-plan §"Sample-size policy": >60% defect rate at half-sample → expand to 50%): half-sample (E-1 through E-11) defect rate = 2/11 = 18.2% (E-3 defensible + E-10 weak); well below the 60% trigger. Standard 35% density held.

## SEP citations consulted

- SEP entry: "Mereology"
- SEP entry: "Mereological Nihilism"
- SEP entry: "Haecceitism"
- SEP entry: "Possible Worlds"
- SEP entry: "Modality"
- SEP entry: "Modal Logic"
- SEP entry: "Modal Realism" / "David Lewis"
- SEP entry: "Essence"
- SEP entry: "Essential vs Accidental Properties"
- SEP entry: "Counterpart Theory"
- SEP entry: "Identity"
- SEP entry: "Time"
- SEP entry: "Presentism"
- SEP entry: "Eternalism (Philosophy of Time)"
- SEP entry: "McTaggart's Argument"
- SEP entry: "Tropes"
- SEP entry: "Logic and Ontology"
- SEP entry: "Metaphysics"
- SEP entry: "Free Will"
- SEP entry: "Causal Determinism"
- SEP entry: "Abstract Objects"
- SEP entry: "Relations"
