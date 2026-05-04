-- Migration: 0030_seed_metaphysics_part1
-- Purpose: Third Phase 5 seed migration (first metaphysics file) —
--   foundational metaphysics concepts and within-domain
--   pedagogical_prerequisite edges. Authored in S-0054 against task
--   P5-02a "Metaphysics core seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the four core pillars per phase_5.md T1-B: being/ontology,
--   identity, causation, time. Specialized metaphysics — modality,
--   free will, properties/universals, mereology — is task P5-02b's
--   range (0036-0039).
-- Loads tables: public.nodes (27 INSERTs), public.edges (30 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 3 -> 4).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 3 at session boot (post-S-0053; verified
--     via Supabase MCP execute_sql at S-0054 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 4 (the
--     post-increment value).
--   * No prior migrations under prefix 0030-0035; this is the first
--     metaphysics seed file.
--   * P5-01a + P5-01b epistemology seeds applied (0011 and 0016). No
--     edge in this migration references epistemology nodes — metaphysics
--     core is greenfield within its own subdomain at this seed step;
--     cross-domain bridges land at P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 27 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'metaphysics'}, status=active, graph_version_added=4.
--   * 30 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=4. All edges are
--     within-domain (source and target both tagged metaphysics);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 4.
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts (no edges into pre-existing nodes; metaphysics is
--     greenfield within its own subdomain).
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is layered: metaphysics -> ontology -> existence
--     -> {substance, property, relation, event, abstract_object,
--     concrete_object, numerical_identity, causation, time}; identity
--     branch flows numerical_identity -> {leibniz_law, persistence};
--     persistence -> {endurantism, perdurantism, ship_of_theseus};
--     perdurantism -> temporal_parts; causation branch flows
--     {existence, event, time} -> causation -> {humean_regularity_
--     theory, counterfactual_theory_of_causation, causal_powers}; time
--     branch flows time -> {a_theory_of_time, b_theory_of_time,
--     mctaggarts_paradox, persistence}; a_theory_of_time -> {presentism,
--     growing_block_theory, mctaggarts_paradox}; b_theory_of_time ->
--     eternalism. validate.py's Kosaraju SCC check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach into other subdomains — causation bridges
--     to philosophy of science (P5-09) on scientific explanation and
--     to philosophy of mind (P5-07a) on mental causation; time bridges
--     to philosophy of science (P5-09) on time in physics; numerical_
--     identity / persistence bridges to philosophy of mind (P5-07a) on
--     personal identity; existence / ontology bridges to philosophy of
--     language (P5-08) on Quine's ontological commitment and to
--     epistemology (P5-01a/b) on knowledge of abstract objects;
--     abstract_object bridges to logic (P5-03) on mathematical
--     platonism — wait for P5-11's cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the specialized metaphysics range (0036-0039):
--     modality, possible worlds, free will, properties/universals/
--     tropes, bundle theory, mereology. P5-02b owns that range.
--   * Does not author the additional metaphysics core sub-ranges (0031-
--     0035). Those slots remain reserved for future metaphysics
--     extension if Phase 6+ telemetry warrants additional concepts;
--     this seed completes P5-02a's task at the granularity principle
--     within the 0030 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 27/27 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the analytic tradition
--     (or earlier philosophical tradition in the case of substance,
--     ontology, McTaggart's paradox) explicitly names. Mirrors
--     P5-01a / P5-01b's distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'metaphysics'. Multiple cross-domain reaches exist (causation,
--     time, persistence, abstract_object are all cross-domain
--     concepts) but per phase_5.md T2-G #4 (domain-tag cardinality
--     explosions vector), cross-domain tagging belongs to P5-11. The
--     canonical home for each of these concepts in the analytic
--     literature is metaphysics, so the single tag is correct here.
--   * provenance: 'ai-seed' for every node and edge. Same as P5-01a /
--     P5-01b.
--   * Node selection rationale: the 27 concepts cover the four core
--     pillars per phase_5.md T1-B at the granularity principle:
--     (1) being/ontology cluster [metaphysics, ontology, existence,
--     substance, property, relation, event, abstract_object,
--     concrete_object] — the field's basic ontological categories;
--     (2) identity cluster [numerical_identity, leibniz_law,
--     persistence, endurantism, perdurantism, temporal_parts,
--     ship_of_theseus] — synchronic identity (Leibniz's law) plus
--     diachronic identity (the 3D vs 4D persistence dispute and its
--     paradigm puzzle); (3) causation cluster [causation,
--     humean_regularity_theory, counterfactual_theory_of_causation,
--     causal_powers] — the three canonical theories of causation
--     (Humean reductive, Lewisian counterfactual, neo-Aristotelian
--     dispositional); (4) time cluster [time, a_theory_of_time,
--     b_theory_of_time, presentism, eternalism, growing_block_theory,
--     mctaggarts_paradox] — the metaphysics of time, organized around
--     McTaggart's A/B-series distinction and the three main A-theoretic
--     positions (presentism, growing block) vs B-theoretic eternalism.
--     Property is included as a basic ontological category (alongside
--     substance, relation, event) but its deeper unfolding into
--     universals, tropes, and bundle theory is P5-02b. Free will is
--     entirely P5-02b. Modality and possible worlds (Lewis, Kripke,
--     Stalnaker) are P5-02b. Mereology (parthood, simples, gunk,
--     mereological essentialism) is P5-02b — though ship_of_theseus
--     gestures at it as a paradigm puzzle for diachronic identity.
--   * Edge structure: 30 edges total, all pedagogical_prerequisite,
--     all within-domain. Spine from metaphysics -> ontology ->
--     existence -> ten downstream categories/topics; identity branch
--     flows from numerical_identity through leibniz_law and
--     persistence; persistence forks into endurantism, perdurantism
--     (which has temporal_parts as its constituent), and the
--     ship_of_theseus paradigm puzzle; causation branch has three
--     inbound (existence, event, time) reflecting the three structural
--     bases for causal analysis (existence as ontological ground,
--     event as relata, time as direction-fixing) and three outbound
--     theories; time branch forks into A/B series and McTaggart's
--     paradox, with a_theory_of_time forking into presentism and
--     growing_block_theory. The cross-cluster edges (time ->
--     persistence, time -> causation, event -> causation) tie the
--     four pillars into a coherent within-subdomain dependency
--     structure.
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 4; DELETE FROM public.nodes WHERE id IN (the 27 ids inserted
--   here); UPDATE public.settings SET value = '3'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 58 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0016_seed_epistemology_part1.sql
--   (P5-01b specialized seed; pattern reference);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 3 at session boot (post-S-0053 state); write 4 here;
-- every node/edge below carries graph_version_added = 4.
UPDATE public.settings
  SET value = '4'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 27 INSERTs covering the four core metaphysics pillars.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'metaphysics',
    'Metaphysics',
    ARRAY['metaphysics'],
    'The philosophical investigation of the most general features of reality: what kinds of things exist, what their fundamental natures are, and how they relate. Encompasses ontology (categories of being), identity and persistence, causation, time and space, modality, properties, free will, and the mind-body relation. Distinct from physics in asking conceptual rather than empirical questions about reality''s structure.',
    'Frame metaphysics by contrast with adjacent domains: physics asks which causal laws hold; epistemology asks what we can know; metaphysics asks what is. The contemporary analytic version (Lewis, Armstrong, Sider, Williamson) is more austere than its scholastic ancestor — driven by argument and parsimony rather than systematic theological exposition. The discipline''s legitimacy was challenged by logical positivism (Carnap) and then rehabilitated by Quine''s On What There Is and the post-1970s revival.',
    ARRAY['metaphysical_inquiry'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'ontology',
    'Ontology',
    ARRAY['metaphysics'],
    'The branch of metaphysics that asks what entities exist and what their basic categories are. Distinguishes (with Quine) the ontological question — what is there? — from the descriptive question — what is the nature of what is there? Inventories range from austere (only physical objects) to lavish (sets, propositions, possibilia, universals, tropes).',
    'Quine''s "On What There Is" (1948) is the foundational contemporary text and the place to begin. The criterion of ontological commitment ("to be is to be the value of a variable") is technically sharp and pedagogically useful. Distinguish ontology (which categories of thing exist) from metaontology (what we are doing when we ask which things exist) — the latter has its own substantial literature (Schaffer, Hirsch, Cameron, Sider).',
    ARRAY['ontological_inquiry'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'existence',
    'Existence',
    ARRAY['metaphysics'],
    'The most basic property a thing has when it is — when it figures in the world rather than being merely thought of, hoped for, or denied. Whether existence is a property at all (Kant, Frege, Quine) is itself contested. Treated by Quine and standard predicate logic as captured by the existential quantifier rather than as a first-order predicate of individuals.',
    'Distinguish three layers: (1) the metaphysical question whether existence is a univocal feature; (2) the logical question whether existence is a quantifier or a predicate (Kant: not a real predicate; Frege/Russell: a property of concepts; Meinong: a predicate of objects, some of which lack it); (3) the ontological question what kinds of thing exist. The contemporary mainstream follows the Frege-Quine analysis but the Meinongian alternative (existence as a predicate of objects, with non-existent objects being legitimate referents) has serious defenders (Parsons, Routley, Priest).',
    ARRAY['being'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'substance',
    'Substance',
    ARRAY['metaphysics'],
    'A traditional ontological category: an independently existing entity that is the bearer of properties and the subject of change. Aristotle''s primary substances are individual concrete particulars (this man, this horse); his secondary substances are species and genera. The category is contested in contemporary metaphysics — bundle theorists deny that anything answers to it.',
    'Substance is a category-concept that does heavy work for Aristotelian metaphysics and gets challenged by everyone after Hume. Pedagogically useful as the canonical contrast for bundle theory (substance is what bundle theory denies). Distinguish primary substance (individual concrete particulars: Socrates, this tree) from secondary substance (kinds and species). The contemporary debate over substance is technical (substance versus the bundle of its properties) and metaontologically charged.',
    ARRAY['substantial_being'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'property',
    'Property',
    ARRAY['metaphysics'],
    'A feature an object has — its color, mass, shape, charge, or moral character. Properties are introduced to make sense of the fact that distinct objects can resemble one another (sharing a property) and that one object can change while remaining the same (gaining or losing a property). The deeper analysis (universals vs tropes vs nominalist resemblance classes) is P5-02b''s range.',
    'At the granularity principle the bare concept of property suffices for P5-02a; the unfolding into universals (Plato, Armstrong), tropes (Williams, Campbell), and nominalist alternatives (Lewis, Goodman) is specialized metaphysics. Property is one of four basic ontological categories alongside substance, relation, and event — the standard analytic inventory.',
    ARRAY['attribute', 'feature'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'relation',
    'Relation',
    ARRAY['metaphysics'],
    'A feature borne jointly by two or more entities: being-taller-than, being-north-of, being-the-cause-of. Where properties are one-place (unary), relations are many-place (binary, ternary, etc.). The metaphysical question is whether relations are real features of the world or reducible to properties of the relata.',
    'Internal relations (taller-than, larger-than) are determined by intrinsic properties of the relata; external relations (spatial separation, causal connection) are not. Russell argued in the early 20th century that external relations are indispensable, against the British idealists who claimed all relations reduce to internal ones. The current analytic mainstream accepts irreducibly external relations.',
    ARRAY['relational_property'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'event',
    'Event',
    ARRAY['metaphysics'],
    'A particular occurrence located in space and time: the explosion of a bomb, the running of a race, the signing of a treaty. Davidson (1969) argued events are basic ontological particulars on a par with concrete objects, distinct from the propositions that describe them and from the properties they instantiate. The action theory and causation literature both presuppose an event ontology.',
    'Davidson''s "The Individuation of Events" is the foundational analytic text. The criterion-of-individuation question — when are two events identical? — has competing answers (Kim: events are property-time-object triples; Davidson: events are identical iff they have the same causes and effects; Lewis: events are sets of regions). Pedagogically the dispute matters because action theory and causation analyses pick up an event ontology and run with it.',
    ARRAY['eventuality'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'abstract_object',
    'Abstract Object',
    ARRAY['metaphysics'],
    'A non-spatial, non-causal entity: numbers, sets, propositions, possible worlds (on some accounts), types as opposed to tokens. The contrast class is concrete objects (spatially located, causally efficacious). Abstract objects raise epistemological worries (how can we know about entities we cannot causally interact with?) and ontological ones (do they exist at all?).',
    'Mathematical platonism is the canonical case for abstract objects: numbers exist, are non-spatial, and lack causal powers; mathematical knowledge is knowledge of them. Nominalists (Field, Hellman) construct alternatives that avoid commitment to abstract objects. The abstract/concrete distinction itself is contested — neither defining the categories by what they lack (negative criterion) nor by some positive property gives universally accepted boundaries.',
    ARRAY['abstract_entity', 'abstract_particular'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'concrete_object',
    'Concrete Object',
    ARRAY['metaphysics'],
    'A spatially located, causally efficacious entity: this rock, that person, the moon. Contrasts with abstract objects. Concrete objects are paradigmatically what most metaphysicians treat as basic; the question of how to individuate them, how they persist, and how they relate to their parts dominates non-modal metaphysics.',
    'Concrete object is best taught as the unmarked default — the kind of thing students already think exists — set against the abstract-object foil. The harder questions (when are two concrete objects the same? what are the parts of a concrete object?) are downstream: persistence, mereology, identity. Use concrete object as the entry point to the identity and mereology disputes.',
    ARRAY['concrete_particular', 'concrete_entity'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'numerical_identity',
    'Numerical Identity',
    ARRAY['metaphysics'],
    'The relation a thing bears only to itself: a is numerically identical to b iff a and b are one and the same entity. Distinguished from qualitative identity (sharing all properties) and exact resemblance. Governed by Leibniz''s law: identicals share all properties; things sharing all properties are identical (the latter half is the contested principle of identity of indiscernibles).',
    'Numerical identity is logically simple (a=a; if a=b then F(a) iff F(b)) but philosophically loaded — it grounds questions of persistence, personal identity, constitution, and the metaphysics of qualitative variation. Distinguish from qualitative identity early: identical twins are qualitatively similar but numerically distinct; you-now and you-yesterday are numerically identical despite qualitative differences.',
    ARRAY['identity_strict', 'absolute_identity'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'leibniz_law',
    'Leibniz''s Law',
    ARRAY['metaphysics'],
    'The principle governing numerical identity, with two halves: the indiscernibility of identicals (if a is identical to b, then a and b share all properties) and the identity of indiscernibles (if a and b share all properties, they are identical). The first half is logical commonplace; the second half is contested (Black''s 1952 two-spheres argument is the canonical counterexample).',
    'Teach the two halves separately. Indiscernibility of identicals follows from the very logic of identity (a=b licenses substitution salva veritate) and is not seriously disputed. Identity of indiscernibles is substantive: Max Black''s symmetric universe (two qualitatively identical spheres in an otherwise empty space) is the standard counterexample, defended by Black against arguments that haecceities or relational properties save the principle. The principle''s status interacts with the metaphysics of properties (more properties → easier to satisfy → principle survives).',
    ARRAY['leibnizs_law', 'indiscernibility_of_identicals'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'persistence',
    'Persistence',
    ARRAY['metaphysics'],
    'Identity through time: the relation between a thing at one time and the same thing at another time. The two main accounts are endurantism (a thing is wholly present at each time at which it exists) and perdurantism (a thing has temporal parts at each time at which it exists, and exists in virtue of having such parts). The persistence debate is structurally analogous to the spatial-parts debate.',
    'Persistence is the diachronic analog of synchronic identity, and the topic where most concrete-object identity puzzles arise. Set up the dispute by way of contrasts: how does the cat at noon relate to the cat at 1pm? On endurantism, the same whole cat exists at both times. On perdurantism, the cat is a four-dimensional whole, of which the noon-cat-stage and 1pm-cat-stage are temporal parts. The choice has consequences for ship-of-theseus puzzles, the metaphysics of constitution, and the philosophy of time.',
    ARRAY['identity_through_time', 'diachronic_identity'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'endurantism',
    'Endurantism',
    ARRAY['metaphysics'],
    'The three-dimensionalist view of persistence: a persisting object is wholly present at every time at which it exists, lacking temporal parts. The whole cat is here now, and the whole same cat will be here tomorrow. Naturally aligned with presentism (only present things exist) but compatible with eternalism (then the whole cat exists at multiple times, multiply located).',
    'Endurantism is the intuitive starting point — most students arrive thinking the cat is a single three-dimensional thing that exists at successive times. Its main challenges come from constitution puzzles (how can the cat be wholly present at t1 and at t2 if its constituent matter has changed?) and the indiscernibility-of-identicals problem (the cat at t1 is bent, the cat at t2 is not, but they''re identical). Endurantists respond by relativizing properties to times.',
    ARRAY['three_dimensionalism', 'enduring_object'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'perdurantism',
    'Perdurantism',
    ARRAY['metaphysics'],
    'The four-dimensionalist view of persistence: a persisting object exists by having temporal parts at each time at which it exists. The cat is a 4D whole spanning a temporal interval; the noon-cat is its temporal part at noon. Naturally aligned with eternalism. Lewis, Sider, and Heller defend versions of the view.',
    'Perdurantism handles the indiscernibility puzzle straightforwardly: the noon-cat-stage is bent and the 1pm-cat-stage is not bent; the whole cat is neither bent nor not-bent simpliciter but has bent and not-bent parts at different times. The cost is metaphysical commitment to temporal parts as a basic ontological category. Perdurantism comes in stage-theory variants (Sider): we are temporal stages, and "I will exist tomorrow" is true in virtue of the counterpart relation between today''s stage and tomorrow''s stage.',
    ARRAY['four_dimensionalism', 'perduring_object'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'temporal_parts',
    'Temporal Parts',
    ARRAY['metaphysics'],
    'The constituents of a perduring four-dimensional object at each time of its existence — analogs of spatial parts, but along the temporal dimension. Perdurantism takes them as basic; endurantism rejects them. The metaphysics of temporal parts is technical: how thinly are they sliced (instantaneous stages? finite intervals?), and what is their relation to the persisting whole?',
    'Frame temporal parts by analogy with spatial parts: just as a road has spatial parts (the section through the city, the section through the country), a road''s lifetime has temporal parts (the road in 1950, the road in 2025). The analogy is contested — endurantists hold that the spatial analogy is misleading because objects are not spread out across time the way they are across space. Sider''s "Four-Dimensionalism" (2001) is the systematic defense.',
    ARRAY['time_slices', 'temporal_part'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'ship_of_theseus',
    'Ship of Theseus',
    ARRAY['metaphysics'],
    'The ancient puzzle (Plutarch) about diachronic identity through complete part-replacement: the ship whose planks are gradually all replaced one by one. Is the resulting ship the same ship? What if the replaced planks are reassembled into a second ship? Either both ships are Theseus''s ship (impossible by transitivity of identity) or neither is, or only one — and the principle of choice is contested.',
    'The ship of Theseus is the canonical pedagogical entry point to the persistence debate, the constitution-versus-identity question, and the Aristotelian distinction between matter and form. Endurantists tend toward "the gradually-replaced ship is Theseus''s; the reassembled ship is a different ship" (form persists through matter change); perdurantists describe the situation in terms of overlapping temporal parts. Use the puzzle to set up the deeper metaphysical disputes rather than treating it as a stand-alone problem with a stand-alone solution.',
    ARRAY['theseuss_ship'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'causation',
    'Causation',
    ARRAY['metaphysics'],
    'The relation between cause and effect — what one event or state of affairs does to bring another about. Cited in scientific explanation, ordinary action description, legal responsibility attribution, and counterfactual reasoning. The metaphysics of causation asks what the relation consists in; the major contemporary accounts are regularity, counterfactual, and dispositional/powers theories.',
    'Causation is everywhere in our talk and reasoning, but analytically resists reduction. Hume''s starting move was to deny that we directly perceive causal connection — we observe constant conjunction and infer causation. The post-Humean tradition splits over whether constant conjunction is all there is (regularity theories), whether counterfactual dependence does the work (Lewis), or whether causal powers are an irreducible feature of the world (Aristotelian / Mumford / Anjum). Useful to teach the three theories in dialogue rather than serially.',
    ARRAY['causal_relation'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'humean_regularity_theory',
    'Humean Regularity Theory of Causation',
    ARRAY['metaphysics'],
    'The reductive theory of causation deriving from Hume''s "Enquiry": event c causes event e iff c is of a type that is constantly conjoined with events of e''s type, c is temporally prior to e, and c is spatiotemporally contiguous with e. Eliminates necessary connection from the world; what we call "necessity" is a felt expectation in the observer.',
    'Hume''s motivating epistemology — we observe conjunction, not necessity — pulls the metaphysics: if necessity is unobservable, it has no place in the world picture. The contemporary analytic descendants (Mackie''s INUS conditions, the Best-System Analysis from Lewis-Beebee-Loewer) refine the regularity backbone. Standard objections: spurious correlations (day follows night without causation), one-off causation (a single big bang), and the absence of asymmetry (regularity is symmetric; causation is not).',
    ARRAY['regularity_theory_of_causation', 'humean_causation'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'counterfactual_theory_of_causation',
    'Counterfactual Theory of Causation',
    ARRAY['metaphysics'],
    'David Lewis''s (1973) account: c causes e iff e counterfactually depends on c — had c not occurred, e would not have occurred either. The counterfactual conditional is analyzed via possible-worlds semantics. The theory recovers the asymmetry of causation (effects do not counterfactually determine their causes) and handles preemption cases that defeat regularity theory.',
    'Lewis''s "Causation" (1973) is the foundational paper; "Causation as Influence" (2000) is his later refinement responding to preemption objections. The counterfactual analysis is pedagogically powerful because it lets us reason about causation using familiar conditional reasoning. Standard objections: preemption (had Suzy not thrown her rock, Billy''s rock would have broken the bottle — so Suzy''s throw doesn''t cause the breaking?), absence causation (failures-to-act causing harms), and the analysis of counterfactuals themselves (which possible worlds count as nearby?).',
    ARRAY['counterfactual_causation', 'lewis_counterfactual_theory'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'causal_powers',
    'Causal Powers',
    ARRAY['metaphysics'],
    'The neo-Aristotelian / dispositional account: causation is the manifestation of an object''s causal powers. A match has a power to ignite; striking it activates the power and produces flame. Powers are irreducible features of objects; causation is what powers do. Defended by Harré-Madden, Cartwright, Mumford-Anjum, and Bird.',
    'Powers theory is the contemporary alternative to both Humean regularity and counterfactual reduction. The metaphysical claim is anti-reductive: causation is not analyzable in terms of constant conjunction or counterfactual dependence; it is the manifestation of intrinsic causal powers. Powers are connected to the metaphysics of dispositions (Mellor, Bird) and to the laws-of-nature debate (Bird argues laws are descriptions of what powers do; rivals make laws independent).',
    ARRAY['dispositional_theory_of_causation', 'powers_theory'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'time',
    'Time',
    ARRAY['metaphysics'],
    'The dimension of temporal experience and physical change. The metaphysical questions are whether time is a real feature of reality or a structuring feature of cognition, what its directionality consists in, what relation tense (past/present/future) bears to the tenseless ordering of events, and whether all times are equally real. Contrasts with the physics of time (relativity, thermodynamic asymmetry) which informs but does not settle the metaphysical questions.',
    'Frame the metaphysics of time around McTaggart''s A/B-series distinction. The A-series orders events by tensed properties (past, present, future); the B-series orders them by tenseless relations (earlier-than, later-than, simultaneous-with). The deep dispute is whether the A-series captures something real (A-theorists: yes, the present is metaphysically privileged) or whether tense reduces to perspective on the tenseless B-series ordering (B-theorists: yes). Distinguish metaphysics-of-time questions from physics-of-time questions: relativity says simultaneity is observer-relative, but whether the present is metaphysically privileged is not directly answered by relativity.',
    ARRAY['time_metaphysical'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'a_theory_of_time',
    'A-Theory of Time',
    ARRAY['metaphysics'],
    'The view that the A-series — the ordering of events by tensed properties (past, present, future) — captures a real feature of reality, and that the present is metaphysically privileged. Tensed propositions ("it is now raining") are irreducible to tenseless ones. The three main A-theoretic positions are presentism, the growing-block theory, and the moving-spotlight theory.',
    'A-theorists hold that tense is metaphysically real: the present moment is objectively privileged, and the difference between past, present, and future is a difference in the world, not in the observer. The standard defenses appeal to the felt passage of time, the asymmetry between fixed past and open future, and the linguistic primacy of tensed expression. The standard objections are McTaggart''s paradox and the alleged tension with special relativity (which makes simultaneity observer-relative).',
    ARRAY['tensed_theory_of_time'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'b_theory_of_time',
    'B-Theory of Time',
    ARRAY['metaphysics'],
    'The view that the B-series — the tenseless ordering of events by earlier-than/later-than/simultaneous-with — exhausts the metaphysics of time. Tense is observer-relative or merely linguistic; "now" indexes the speaker''s temporal location, not a metaphysically privileged moment. Mellor, Smart, and Williams are canonical defenders.',
    'B-theorists hold that all times are equally real (eternalism), tensed propositions reduce to tenseless ones with implicit time-references ("it is now raining" = "it is raining at t, where t is the time of utterance"), and the present is no more metaphysically privileged than the here. The view aligns naturally with relativity (no absolute simultaneity, no privileged present) and with perdurantist theories of persistence. Critics charge that it cannot accommodate the felt passage of time (the "now"-feeling) or the asymmetry of the open future.',
    ARRAY['tenseless_theory_of_time'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'presentism',
    'Presentism',
    ARRAY['metaphysics'],
    'The A-theoretic view that only the present time exists. Past entities (Socrates) and future entities (the first human born in the next millennium) do not exist; only what is happening now is part of reality. Defended by Prior, Bigelow, Markosian, and Crisp.',
    'Presentism is the most ontologically austere A-theoretic position: only the present moment exists, and statements about the past and future are made true (when they are made true) by present-time properties of the world (the world contains traces of Socrates; the world contains tendencies toward future events). The challenges are accounting for true past-tense claims (the truthmaker objection) and reconciling with relativity (which has no absolute simultaneity to fix the present). Pedagogically the most intuitive A-theory; metaphysically the most demanding.',
    ARRAY['presentism_metaphysical'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'eternalism',
    'Eternalism',
    ARRAY['metaphysics'],
    'The B-theoretic view that all times — past, present, and future — are equally real. The block universe contains all events at all times; "now" is an indexical referring to the time of utterance, not a metaphysically privileged moment. Often paired with perdurantism in the four-dimensionalist package.',
    'Eternalism is the ontology that makes B-theory work: if the present has no metaphysical privilege, the past and future must be just as real as the present (otherwise we''d need a past-and-present-only or future-only ontology, but those would re-introduce a privileged present). The view fits naturally with special relativity (the four-dimensional block universe is the relativistic space-time geometry). Sider''s "Four-Dimensionalism" defends eternalism via considerations from persistence; Mellor''s "Real Time II" defends it via considerations from temporal ontology.',
    ARRAY['block_universe_theory'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'growing_block_theory',
    'Growing Block Theory',
    ARRAY['metaphysics'],
    'The A-theoretic view that past and present are real but the future is not — the universe is a growing block to which new presents are added at each moment. The leading edge of the block is the present; the open future is not yet part of reality. Broad and Tooley are canonical defenders.',
    'Growing block sits between presentism and eternalism: past times are real (against presentism) but the future is open (against eternalism). The view captures asymmetric intuitions about time: the past is fixed and real, the future is genuinely open. The challenge is explaining what makes a particular time the present, given that the past is also real (Tooley argues it''s the leading edge of the block; critics say this re-introduces an unanalyzed privileging of one time). Useful as a moderate A-theoretic position to teach alongside the more extreme presentism.',
    ARRAY['growing_block_universe'],
    'INTERPRETED',
    'ai-seed',
    4
  ),
  (
    'mctaggarts_paradox',
    'McTaggart''s Paradox',
    ARRAY['metaphysics'],
    'J.M.E. McTaggart''s (1908) argument for the unreality of time: the A-series is self-contradictory (every event is past, present, and future, which are incompatible determinations); the B-series alone cannot capture genuine temporal change; therefore time is unreal. The argument launches the entire A-theory / B-theory dispute and remains the canonical challenge for A-theoretic positions.',
    'McTaggart''s argument has two stages worth teaching separately. Stage 1: the B-series alone is insufficient because earlier-than/later-than relations are static — nothing in the B-series tells us that any particular time is now. Stage 2: the A-series is contradictory because every event must be past, present, and future, but these are incompatible. The standard A-theoretic responses (Broad: the contradiction is only apparent; events have these properties at different times) and B-theoretic responses (Mellor: McTaggart''s second stage works; the A-series is self-contradictory; B-series alone suffices for genuine time) both get extensive contemporary literature.',
    ARRAY['mctaggart_paradox', 'unreality_of_time_argument'],
    'INTERPRETED',
    'ai-seed',
    4
  );

-- Edges: 30 INSERTs, all pedagogical_prerequisite. All within-domain
-- (source and target both tagged metaphysics). Cross-domain edges
-- (causation -> philosophy of science / philosophy of mind, time ->
-- philosophy of science, persistence -> philosophy of mind on personal
-- identity, abstract_object -> logic / mathematics, ontology ->
-- philosophy of language) are P5-11's exclusive surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Ontology spine
  ('metaphysics', 'ontology', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('ontology', 'existence', 'pedagogical_prerequisite', 'ai-seed', 4),
  -- Existence -> ontological categories and downstream topics
  ('existence', 'substance', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'property', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'relation', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'event', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'abstract_object', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'concrete_object', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'numerical_identity', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'causation', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('existence', 'time', 'pedagogical_prerequisite', 'ai-seed', 4),
  -- Identity branch
  ('numerical_identity', 'leibniz_law', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('numerical_identity', 'persistence', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('persistence', 'endurantism', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('persistence', 'perdurantism', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('perdurantism', 'temporal_parts', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('persistence', 'ship_of_theseus', 'pedagogical_prerequisite', 'ai-seed', 4),
  -- Causation branch (event and time also feed in)
  ('event', 'causation', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('causation', 'humean_regularity_theory', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('causation', 'counterfactual_theory_of_causation', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('causation', 'causal_powers', 'pedagogical_prerequisite', 'ai-seed', 4),
  -- Time branch
  ('time', 'a_theory_of_time', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('time', 'b_theory_of_time', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('a_theory_of_time', 'presentism', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('a_theory_of_time', 'growing_block_theory', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('b_theory_of_time', 'eternalism', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('time', 'mctaggarts_paradox', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('a_theory_of_time', 'mctaggarts_paradox', 'pedagogical_prerequisite', 'ai-seed', 4),
  -- Cross-cluster edges (within-subdomain, tying the four pillars)
  ('time', 'persistence', 'pedagogical_prerequisite', 'ai-seed', 4),
  ('time', 'causation', 'pedagogical_prerequisite', 'ai-seed', 4);

COMMIT;
