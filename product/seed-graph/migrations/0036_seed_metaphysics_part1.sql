-- Migration: 0036_seed_metaphysics_part1
-- Purpose: Fourth Phase 5 seed migration (second metaphysics file) —
--   specialized metaphysics concepts and within-domain
--   pedagogical_prerequisite edges. Authored in S-0056 against task
--   P5-02b "Metaphysics specialized seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the four specialized clusters phase_5.md T1-B explicitly
--   defers to P5-02b: modality (with possible-worlds machinery), free
--   will, properties/universals, mereology. Builds on the four core
--   metaphysics pillars (being/ontology, identity, causation, time)
--   that S-0054 authored under task P5-02a in 0030_seed_metaphysics_
--   part1.sql.
-- Loads tables: public.nodes (25 INSERTs), public.edges (36 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 4 -> 5).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 4 at session boot (post-S-0054; verified
--     via Supabase MCP execute_sql at S-0056 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 5 (the
--     post-increment value).
--   * P5-02a metaphysics core seed applied (0030). Cross-references
--     from this migration into P5-02a's nodes — property, substance,
--     existence, abstract_object, numerical_identity, causation,
--     concrete_object, temporal_parts — all resolve to nodes that
--     0030 inserted.
--   * No prior migrations under prefix 0036-0039; this is the first
--     specialized-metaphysics seed file.
-- Postconditions:
--   * 25 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'metaphysics'}, status=active, graph_version_added=5.
--   * 36 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=5. All edges are
--     within-domain (source and target both tagged metaphysics);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 5.
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that either this migration
--     also inserts or that 0030 (P5-02a) inserted. Cross-references
--     run forward (P5-02a -> P5-02b) only — no back-edges from
--     P5-02b nodes to P5-02a nodes.
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is layered. Modality cluster: modality ->
--     {possible_worlds, essence_metaphysical}; possible_worlds ->
--     {modal_realism, ersatz_modal_realism, haecceity,
--     counterpart_theory}. Free will cluster: free_will ->
--     {determinism, compatibilism, incompatibilism, moral_
--     responsibility, principle_of_alternative_possibilities};
--     incompatibilism -> libertarianism_metaphysical. Universals
--     cluster: universals -> {realism_about_universals, nominalism,
--     tropes}; tropes -> bundle_theory. Mereology cluster: mereology
--     -> composition_mereological -> {simples, gunk, mereological_
--     universalism, mereological_nihilism}. Cross-references from
--     P5-02a anchor in: existence -> modality; abstract_object ->
--     possible_worlds; numerical_identity -> {counterpart_theory,
--     haecceity, mereology}; causation -> {free_will, determinism};
--     property -> {universals, realism_about_universals, nominalism,
--     tropes}; substance -> bundle_theory; concrete_object ->
--     {mereology, composition_mereological}; temporal_parts ->
--     mereology. All forward (P5-02a -> P5-02b); no back-edges.
--     validate.py's Kosaraju SCC check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach into other subdomains — modality bridges
--     to logic (P5-03) on modal logic and to philosophy of language
--     (P5-08) on Kripke semantics; possible_worlds bridges to
--     philosophy of language (P5-08) on counterfactuals; free_will
--     and moral_responsibility bridge to ethics (P5-04a) on the
--     metaphysics of moral agency; principle_of_alternative_
--     possibilities bridges to ethics (P5-04a) on the libertarian-
--     consequentialist debate; universals bridge to philosophy of
--     mathematics (within P5-09 / P5-10) on mathematical platonism;
--     bundle_theory bridges to philosophy of mind (P5-07a/b) on
--     bundle theory of self; mereology bridges to philosophy of
--     science (P5-09) on composition in physics — wait for P5-11's
--     cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author specialized concepts beyond the four clusters
--     phase_5.md T1-B explicitly names. Dispositions (already touched
--     in P5-02a via causal_powers; deeper unfolding into Bird /
--     Mumford-Anjum is not at the canonical-coverage layer); structural
--     realism (philosophy of science territory); four-categories
--     ontology (deeper Lowe metaphysics); transcendental idealism
--     (history-of-philosophy territory). All deferred.
--   * Does not author the additional sub-range slots (0037-0039).
--     Those slots remain reserved for future metaphysics extension if
--     Phase 6+ telemetry warrants additional specialized concepts;
--     this seed completes P5-02b's task at the granularity principle
--     within the 0036 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 25/25 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the contemporary
--     analytic literature (Lewis, Kripke, Plantinga, Stalnaker,
--     Williamson, Sider, Armstrong, Williams, van Inwagen, Fine)
--     explicitly names. Mirrors P5-01a / P5-01b / P5-02a's
--     distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'metaphysics'. Multiple cross-domain reaches exist (modality
--     into logic, free_will into ethics, universals into philosophy
--     of mathematics, mereology into philosophy of science) but per
--     phase_5.md T2-G #4, cross-domain tagging belongs to P5-11. The
--     canonical home for each of these concepts in the analytic
--     literature is metaphysics, so the single tag is correct here.
--   * provenance: 'ai-seed' for every node and edge.
--   * Node selection rationale: the 25 concepts cover the four
--     specialized clusters per phase_5.md T1-B at the granularity
--     principle: (1) modality cluster [modality, possible_worlds,
--     modal_realism, ersatz_modal_realism, essence_metaphysical,
--     haecceity, counterpart_theory] — the metaphysics of necessity
--     and possibility, organized around the possible-worlds machinery
--     (Lewis's genuine modal realism vs Plantinga / Stalnaker's
--     ersatzism) plus essence (Fine 1994 reviving the Aristotelian
--     non-modal conception) and the transworld-identity question
--     (haecceity vs counterpart theory); (2) free will cluster
--     [free_will, determinism, compatibilism, incompatibilism,
--     libertarianism_metaphysical, moral_responsibility, principle_
--     of_alternative_possibilities] — the metaphysics of agency,
--     organized around the determinism dilemma (compatibilist Hume /
--     Frankfurt / Wolf / Fischer vs incompatibilist Kane / Pereboom)
--     and PAP (with Frankfurt-style cases gestured at in the
--     teaching_notes for principle_of_alternative_possibilities);
--     (3) properties / universals cluster [universals, realism_about_
--     universals, nominalism, tropes, bundle_theory] — the deeper
--     unfolding of P5-02a's "property" into Plato + Armstrong realism,
--     class / predicate / mereological nominalism, Williams 1953
--     trope theory, and the bundle-theoretic alternative to substance
--     ontology; (4) mereology cluster [mereology, composition_
--     mereological, simples, gunk, mereological_universalism,
--     mereological_nihilism] — the formal theory of parts and wholes,
--     organized around composition (Lewis-Sider universalism vs van
--     Inwagen near-nihilism) and the simples-vs-gunk question.
--   * Edge structure: 36 edges total, all pedagogical_prerequisite,
--     all within-domain. 21 within-cluster forward edges layered by
--     pedagogical dependency (umbrella concept -> theories /
--     positions; theories -> derivative positions like libertarianism
--     under incompatibilism). 15 cross-references from P5-02a's
--     foundational concepts into the new specialized concepts: the
--     existence -> modality bridge anchors modes-of-being into the
--     ontological ground; abstract_object -> possible_worlds
--     reflects ersatzism's treating possible worlds as abstract
--     objects; numerical_identity branches into counterpart_theory
--     and haecceity (the transworld-identity question) and into
--     mereology (composition-as-identity); causation branches into
--     free_will and determinism (free will is fundamentally about
--     causal structure and the determinism thesis is about causation);
--     property branches into universals / realism / nominalism /
--     tropes (the deeper analysis); substance -> bundle_theory
--     (bundle theory denies substance — pedagogically must understand
--     substance to understand the rejection); concrete_object ->
--     mereology / composition_mereological (mereology is about how
--     concrete objects have parts); temporal_parts -> mereology
--     (temporal parts are mereological).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 5; DELETE FROM public.nodes WHERE id IN (the 25 ids inserted
--   here); UPDATE public.settings SET value = '4'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 62 statements
--   atomically — manual rollback above applies to the post-commit
--   window only. The 25 ids: modality, possible_worlds, modal_realism,
--   ersatz_modal_realism, essence_metaphysical, haecceity, counterpart_
--   theory, free_will, determinism, compatibilism, incompatibilism,
--   libertarianism_metaphysical, moral_responsibility, principle_of_
--   alternative_possibilities, universals, realism_about_universals,
--   nominalism, tropes, bundle_theory, mereology, composition_
--   mereological, simples, gunk, mereological_universalism,
--   mereological_nihilism.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0030_seed_metaphysics_
--   part1.sql (P5-02a foundational seed; pattern reference and
--   cross-reference target);
--   product/seed-graph/migrations/0011_seed_epistemology_part1.sql
--   (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0016_seed_epistemology_part1.sql
--   (P5-01b specialized seed; pattern reference for a/b split shape);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 4 at session boot (post-S-0054 state); write 5 here;
-- every node/edge below carries graph_version_added = 5.
UPDATE public.settings
  SET value = '5'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 25 INSERTs covering the four specialized metaphysics clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'modality',
    'Modality',
    ARRAY['metaphysics'],
    'The metaphysics of necessity and possibility: what it is for a proposition to be necessarily true (true at every possible way the world could have been), what it is for it to be possibly true (true at some such way), and what relation these notions bear to actual truth. Distinguishes alethic modality (necessity / possibility simpliciter) from deontic, epistemic, and temporal modalities, which are the subject of philosophical logic and other domains.',
    'Modality is the natural successor to existence and identity in the metaphysics curriculum. The dominant analytic framework is the possible-worlds analysis (Kripke, Lewis): a proposition is necessarily true iff it is true at every possible world, possibly true iff at some possible world. Distinguish de re modality (necessity / possibility of a property holding of an individual) from de dicto (necessity / possibility of a proposition simpliciter) early — the difference matters for transworld identity and for the metaphysics of essence. Quine''s mid-century skepticism about modality (modal contexts are referentially opaque) was answered by Kripke''s "Naming and Necessity" (1980) defense of de re modality via rigid designation.',
    ARRAY['alethic_modality', 'metaphysics_of_modality'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'possible_worlds',
    'Possible Worlds',
    ARRAY['metaphysics'],
    'Total ways the world could have been — alternative complete situations that ground modal claims. A proposition is necessarily true iff it is true at every possible world, possibly true iff at some possible world. The semantic apparatus is uncontested; the metaphysical question is what possible worlds *are*: real concrete worlds isomorphic to ours (Lewis), or abstract structures of some other kind (Plantinga, Stalnaker, Adams).',
    'Teach possible worlds first as a semantic device — the truth conditions of "necessarily P" reduce to a universal quantifier over worlds. Then turn to the metaphysical question of what kinds of thing worlds are. Lewis''s "On the Plurality of Worlds" (1986) defends genuine modal realism: possible worlds are concrete things just like the actual world, differing only in being unactualized. The ersatzist alternatives (Plantinga: worlds as maximal consistent states of affairs; Stalnaker: worlds as ways the world might be, abstract; Adams: worlds as maximal sets of consistent propositions) all hold worlds to be abstract entities of some kind. The choice has substantial costs and benefits: Lewis''s modal realism delivers reductive analyses of modality but at high ontological cost; ersatzism preserves an austere ontology but must explain what makes propositions about possibilia true.',
    ARRAY['possible_world'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'modal_realism',
    'Modal Realism',
    ARRAY['metaphysics'],
    'David Lewis''s view that possible worlds are concrete entities just like the actual world: spatiotemporally and causally isolated from one another but each as real and as concrete as our own. The actual world is just the world we inhabit; "actual" is an indexical, not a metaphysical privileging. Defended in "Counterfactuals" (1973) and "On the Plurality of Worlds" (1986).',
    'Lewis''s motivating argument is reductive: if we want a non-circular analysis of modality (necessity is truth at all possible worlds, possibility is truth at some), and if possible worlds must therefore be the things that ground these analyses, the cheapest realistic interpretation is that worlds are concrete things — just maximally isolated from one another. The cost is the so-called incredulous stare: we are committed to the literal existence of infinitely many concrete worlds containing flying pigs, talking donkeys, and every other possibility. Lewis embraces the cost; critics (Stalnaker, Plantinga) reject it and turn to ersatzism. Pedagogically Lewis''s view is the most ontologically extreme position in metaphysics — useful as a contrast to motivate alternatives.',
    ARRAY['lewis_modal_realism', 'genuine_modal_realism'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'ersatz_modal_realism',
    'Ersatz Modal Realism',
    ARRAY['metaphysics'],
    'The family of views holding that possible worlds are abstract entities of some kind — maximal consistent states of affairs (Plantinga), abstract uninstantiated ways the world might be (Stalnaker), maximal consistent sets of propositions (Adams), or recombinations of actual properties (Armstrong). All preserve the semantic role of possible worlds while denying that worlds are concrete.',
    'Ersatzism is the contemporary mainstream alternative to Lewis''s modal realism. The varieties differ in what kind of abstract entity plays the world role: Plantinga''s "states of affairs" are abstract entities that might or might not obtain; Stalnaker''s "ways" are properties that worlds might have; Adams''s sets of propositions are linguistic in a sense; Armstrong''s combinatorial worlds are recombinations of actual universals and particulars. Each version trades different costs against Lewis''s. The standard Lewis-style objection is that ersatz worlds cannot do the analytic work Lewis''s concrete worlds do — they explain modality only by appealing to consistency, possibility, or recombination, which are themselves modal notions; the analysis becomes circular. Ersatzists deny this circularity charge in various ways.',
    ARRAY['ersatzism', 'abstract_modal_realism'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'essence_metaphysical',
    'Essence',
    ARRAY['metaphysics'],
    'The properties an entity has of metaphysical necessity — those it could not lack while continuing to exist. The Aristotelian conception is non-modal: an essence is what answers the "what is it?" question for an entity, prior to any consideration of necessity. Kit Fine''s "Essence and Modality" (1994) revived the non-modal conception against the standard modal-essentialist account that identifies essences with necessary properties.',
    'Distinguish three positions: (1) modal essentialism — an essence is just the set of necessary properties of an entity (the modern post-Kripke default); (2) Aristotelian / Finean essentialism — essence is prior to modality and what is necessarily true of an entity is necessary because of its essence (Fine 1994); (3) skepticism about essence — essence-talk is dispensable. Fine''s key argument: Socrates is necessarily a member of the singleton {Socrates}, but membership in {Socrates} is not part of what Socrates *is*. So necessary properties are not essential properties; the modal account collapses essence into necessity but they come apart. Pedagogically essence is the place where the deepest disputes about modality live.',
    ARRAY['essence', 'aristotelian_essence'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'haecceity',
    'Haecceity',
    ARRAY['metaphysics'],
    'The non-qualitative property of being identical to a particular individual: the haecceity of Socrates is the property *being identical to Socrates*. Posited to ground transworld identity (the identity of an individual across possible worlds) without reducing it to qualitative similarity. Defended by Adams, Plantinga, and Rosenkrantz; rejected by Lewis (who replaces transworld identity with counterpart theory).',
    'The motivating problem is transworld identity: what makes Socrates-at-this-world the same individual as Socrates-at-some-other-world? A purely qualitative answer (same properties at both worlds) fails because qualitative twins are possible (Black''s two-spheres). A haecceity provides a non-qualitative anchor: each individual has a distinctive *thisness* that goes with it across worlds. The cost is ontological — primitive non-qualitative individuating properties are unwelcome additions to the ontology. Lewis avoids the cost via counterpart theory: there is no transworld identity; an individual at one world has counterparts at other worlds, related by qualitative similarity. The choice between haecceitism and counterpart theory tracks deeper commitments about whether qualitative descriptions exhaust an individual''s metaphysical character.',
    ARRAY['thisness', 'individual_essence'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'counterpart_theory',
    'Counterpart Theory',
    ARRAY['metaphysics'],
    'David Lewis''s account of de re modality: an individual at the actual world has counterparts at other possible worlds (entities qualitatively similar in relevant respects), but not literal identity-across-worlds. "Socrates could have been a carpenter" is true iff Socrates has a counterpart in some possible world who is a carpenter. Replaces transworld identity (literal sameness) with the counterpart relation (qualitative similarity).',
    'Counterpart theory is part of Lewis''s package: modal realism (worlds are concrete) plus counterpart theory (no transworld identity). The motivation is partly ontological (no need for haecceities) and partly logical (the counterpart relation is intransitive and non-symmetric, which fits Lewis''s observation that modal claims about an individual depend on which respects we hold fixed for similarity). The theory has counterintuitive consequences: strictly, *I* could not have been a carpenter — only a counterpart of me could have been. Lewis bites the bullet: the de re modal claims we make are made true by counterpart relations, not by identity. Critics charge that this changes the subject; Lewis charges that the alternative (haecceitism) is metaphysically extravagant.',
    ARRAY['counterpart_relation', 'lewis_counterpart_theory'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'free_will',
    'Free Will',
    ARRAY['metaphysics'],
    'The capacity for an agent to be the source of their actions in a way that grounds moral responsibility. The conceptual core is contested: classical compatibilists analyze free will as the ability to do what one wants; libertarians analyze it as the metaphysically robust ability to do otherwise; hard determinists deny that any analysis is satisfied. The metaphysics of free will is the question of what kind of agency, if any, we actually have.',
    'Frame the dispute by way of the determinism dilemma. If determinism is true (the past + the laws of nature fix the future), how can we be free? The compatibilist says: we are free when our actions flow from our own deliberation and desires, regardless of whether the deliberation is itself determined. The incompatibilist says: this is not enough — true freedom requires the ability to do otherwise in a sense determinism rules out. The libertarian says: incompatibilism is right and we have free will; determinism is therefore false at least in the human-action domain. The hard determinist says: incompatibilism is right, we have no free will, and our practices of holding morally responsible need substantial revision (Pereboom). Pedagogically the debate is best taught with all four positions in dialogue, since each is the negation of one or the other premises.',
    ARRAY['freedom_of_will', 'agential_freedom'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'determinism',
    'Determinism',
    ARRAY['metaphysics'],
    'The thesis that the complete state of the world at any time, together with the laws of nature, fixes the complete state of the world at every later time. Distinguished from fatalism (the future will be what it will be regardless of what we do), from predictability (we could in principle compute the future), and from the denial of randomness in physics (a separate physical question).',
    'Distinguish three theses early: (1) determinism — past + laws fix the future; (2) physical determinism — the laws of physics are deterministic; (3) predictability — we could compute the future from the past. Determinism is a metaphysical thesis; predictability is epistemic. Quantum mechanics has stochastic dynamics in standard interpretations (Copenhagen), so physical determinism is at least contested; this matters less than philosophers sometimes think for the free-will debate, because (a) compatibilists hold that determinism is compatible with free will so its truth is moot, (b) the relevant macroscale dynamics governing human action may be effectively deterministic regardless of underlying quantum stochasticity, and (c) substituting indeterministic randomness for determinism does not obviously deliver libertarian free will (the luck objection).',
    ARRAY['causal_determinism'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'compatibilism',
    'Compatibilism',
    ARRAY['metaphysics'],
    'The view that free will is compatible with determinism — that we can be free even if the past plus the laws of nature fix everything we do. Classical compatibilism (Hume) analyzes free action as action that flows from the agent''s desires without external constraint; modern compatibilism (Frankfurt, Wolf, Fischer-Ravizza) develops more sophisticated criteria — hierarchical desires, reasons-responsiveness, ownership of one''s mechanism.',
    'Compatibilism is the dominant position in contemporary philosophy. Frankfurt''s "Freedom of the Will and the Concept of a Person" (1971) introduces the hierarchical structure: free will requires that one''s first-order desires be endorsed by second-order desires (one wants to want what one wants). Wolf''s "Reason View" requires the ability to act in accordance with the True and the Good. Fischer and Ravizza''s "Responsibility and Control" (1998) requires a moderately reasons-responsive mechanism that is one''s own. The unifying compatibilist intuition: the kind of freedom worth wanting — the freedom that grounds moral responsibility — does not require the metaphysical "could have done otherwise" of incompatibilism, only certain structural features of the actual deliberation and action.',
    ARRAY['compatibilist_free_will'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'incompatibilism',
    'Incompatibilism',
    ARRAY['metaphysics'],
    'The view that free will is incompatible with determinism — that if the past plus the laws fix everything we do, we are not free. The motivating intuition is the "could have done otherwise" requirement: genuine free choice requires that the agent could have chosen differently in a strong sense, and determinism precludes this. Incompatibilists divide into libertarians (we have free will, therefore not all our actions are determined) and hard determinists / hard incompatibilists (we have no free will).',
    'The Consequence Argument (van Inwagen 1983) is the canonical incompatibilist argument: (1) if determinism is true, our actions are consequences of the past and the laws; (2) we have no power over the past or the laws; (3) we have no power over the consequences of things over which we have no power; (4) therefore we have no power over our actions. Compatibilists object at step 3 (the modal logic of "having power over" is more subtle than the inference allows) or analyze "power over actions" in terms compatible with determinism. Incompatibilists insist that the argument captures the intuitive shape of the worry: under determinism, our actions trace back to states of the world before we were born, over which we manifestly have no power.',
    ARRAY['incompatibilist_free_will'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'libertarianism_metaphysical',
    'Libertarianism (Metaphysical)',
    ARRAY['metaphysics'],
    'The metaphysical position that we have free will and that this requires the falsity of determinism — at least for the actions we count as freely chosen. Distinguished from political libertarianism (the philosophy of minimal-state political liberty), which is a separate doctrine. Defenders include Kane (event-causal libertarianism), O''Connor (agent-causal libertarianism), Clarke, and Ginet.',
    'Libertarianism faces the luck objection: if determinism is false at the moment of choice, then what determines which choice we make? If nothing, the choice is random, not free. Event-causal libertarians (Kane) reply that the indeterminism is structured — the agent has reasons for both options and the indeterministic outcome is sensitive to those reasons, so the choice is the agent''s even if it is not deterministic. Agent-causal libertarians (O''Connor) reply that the agent is a substance whose direct causation of the choice is the form of agency the libertarian needs, distinct from event-causation. Both responses are technical and contested. Pedagogically: separate libertarianism (this metaphysical position) from political libertarianism early — students conflate them; the only shared root is "free."',
    ARRAY['metaphysical_libertarianism', 'libertarian_free_will'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'moral_responsibility',
    'Moral Responsibility',
    ARRAY['metaphysics'],
    'The metaphysical conditions under which an agent is appropriately held accountable — praiseworthy or blameworthy — for an action. The free-will debate is largely fueled by the question of which account of agency suffices for moral responsibility: compatibilist (Frankfurt, Fischer-Ravizza), libertarian (Kane), or skeptical (Pereboom, Caruso) approaches all converge on the responsibility question.',
    'P.F. Strawson''s "Freedom and Resentment" (1962) is the influential analysis: moral responsibility is grounded in the reactive attitudes (resentment, gratitude, indignation, guilt) we directed at agents. The question of free will is the question of whether these attitudes are appropriate — and Strawson argues they are constitutive of human relationships in a way that makes the metaphysical question of determinism beside the point. Pereboom''s "Living Without Free Will" (2001) and "Free Will, Agency, and Meaning in Life" (2014) defend hard incompatibilism: we lack the kind of free will required for genuine deserved blame, but we can still hold each other accountable in a forward-looking, consequentialist sense. The metaphysical question and the practical question (what changes if we''re not metaphysically free?) come apart.',
    ARRAY['moral_responsibility_metaphysical'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'principle_of_alternative_possibilities',
    'Principle of Alternative Possibilities',
    ARRAY['metaphysics'],
    'The principle that an agent is morally responsible for an action only if the agent could have done otherwise. Often labelled PAP. Treated as a near-axiom of incompatibilist intuitions about freedom; challenged by Frankfurt''s "Alternate Possibilities and Moral Responsibility" (1969) via counterexamples in which the agent could not have done otherwise but is intuitively still responsible.',
    'Frankfurt''s counterexample structure: a counterfactual intervener (Black) is poised to ensure that the agent (Jones) chooses to do A, but does not need to intervene because Jones chooses A on his own. Jones could not have chosen otherwise (Black would have prevented it), yet Jones is intuitively responsible because he chose A through his own deliberation. If Frankfurt cases work, PAP is false: moral responsibility does not require alternative possibilities. The case launched a substantial literature: do Frankfurt cases really show what they purport to (some say the agent does have alternatives — perhaps the alternative of being intervened upon — that ground responsibility)? Even if PAP is false, does that vindicate compatibilism (compatibilists rejoice; incompatibilists must find a different formulation of the freedom-requires-determinism-falsity link)? Pedagogically PAP and Frankfurt cases are the entry point to the modern debate over the structural conditions of free will.',
    ARRAY['pap', 'alternative_possibilities'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'universals',
    'Universals',
    ARRAY['metaphysics'],
    'Properties or relations conceived as repeatable entities — single things wholly present in each of their instances. The redness of the apple and the redness of the rose are, on the universals view, the very same entity wholly present in both. Contrasts with tropes (abstract particulars, non-repeatable) and nominalist views (no universals at all). The universals dispute is the central problem of the metaphysics of properties.',
    'The dispute begins with Plato (forms as separately existing universals) and Aristotle (universals as immanent in their instances). Modern realists about universals (Armstrong, Bealer) defend universals as in re — wholly present in each instance, no separate Platonic existence required. Modern nominalists (Lewis''s class nominalism, Goodman''s resemblance nominalism, the predicate / concept / mereological variants) deny universals while preserving talk of properties via reductive analyses. The arguments cluster around: (1) the One Over Many — what makes two distinct things share a property? (2) abstract reference — what is the referent of "redness"? (3) the regress concerns — does positing universals just push the question one level up? Pedagogically Armstrong''s "Universals: An Opinionated Introduction" (1989) is the modern systematic defense; Lewis''s "New Work for a Theory of Universals" (1983) is the qualified counterpart from the other side.',
    ARRAY['universal_property', 'platonic_universal'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'realism_about_universals',
    'Realism about Universals',
    ARRAY['metaphysics'],
    'The position that universals exist as entities in their own right — either separately (Platonic realism: universals exist whether or not they are instantiated) or in re (Aristotelian realism: universals exist only as instantiated in their instances, but are real entities distinct from the instances). Contemporary defenders (Armstrong, Bigelow) typically take the in re position.',
    'Distinguish Platonic from Aristotelian realism early. Platonic realism is committed to uninstantiated universals (the property of being a unicorn exists even though no unicorns do); the cost is heavy commitment to a non-spatial, non-temporal realm of forms. Aristotelian realism (Armstrong) restricts universals to those that are actually instantiated; the cost is that some apparent properties (being a unicorn, being phlogiston) cannot be universals on this account. Both versions face the regress concerns ("relational realism," Russell-style: if universals are wholly present in instances, what relates the universal to the instance? a further universal? regress?). Realist responses build the relation in non-relationally — Armstrong''s "states of affairs" treat the instantiation as a basic non-relational structure.',
    ARRAY['platonism_about_universals', 'aristotelian_realism'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'nominalism',
    'Nominalism',
    ARRAY['metaphysics'],
    'The denial of universals — the view that nothing in reality answers to the universals talk of natural language. Nominalists analyze property attributions (the apple is red) via predicates (the predicate "red" is true of the apple), classes (the apple belongs to the class of red things), resemblance (the apple resembles paradigm red things), or in austere versions, treat property talk as primitive and irreducible. Defenders include Goodman, Quine (early), Lewis (class nominalism), and Armstrong (in his earlier ostrich-nominalist phase).',
    'The varieties of nominalism organize by what they substitute for universals. Predicate nominalism: the apple is red because "red" is true of it (Quine). Concept nominalism: in virtue of falling under the concept *red*. Class nominalism: in virtue of belonging to the class of red things (Lewis 1983). Resemblance nominalism: in virtue of resembling paradigm red things (Goodman, Rodriguez-Pereyra). Mereological nominalism: in virtue of being a part of the aggregate of red things. Each version faces specific objections: predicate / concept nominalism faces the problem of unactualized predicates / concepts; class nominalism faces the problem of co-extensive but distinct properties (creatures with hearts vs creatures with kidneys); resemblance nominalism faces the regress problem (resemblance is itself a relation that needs explaining). The systematic comparison is Rodriguez-Pereyra''s "Resemblance Nominalism" (2002).',
    ARRAY['nominalism_about_properties', 'anti_realism_about_universals'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'tropes',
    'Tropes',
    ARRAY['metaphysics'],
    'Abstract particulars: property-instances conceived as non-repeatable particulars that are nonetheless themselves the things their bearers have. The redness of this apple is a distinct trope from the redness of the rose, even if the two tropes exactly resemble one another. D.C. Williams''s "On the Elements of Being" (1953) is the foundational analytic treatment; Keith Campbell''s "Abstract Particulars" (1990) the modern systematic development.',
    'Tropes are an attractive middle position between realism about universals and austere nominalism. They are particulars (not repeatable) so they avoid the regress concerns of universals; they are abstract (the apple''s redness is not the apple itself) so they can do the work of properties. Resemblance among tropes (rather than universal-instantiation or class-membership) does the work of grounding shared property attributions. The position has costs: the resemblance among tropes is either a primitive non-reducible relation (a primitive that nominalists complained about in resemblance nominalism) or further analyzed at high cost. Trope theory connects directly to bundle theory (objects are bundles of compresent tropes) and to the metaphysics of causation (causal powers as tropes — Mumford-Anjum).',
    ARRAY['abstract_particulars', 'property_instances'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'bundle_theory',
    'Bundle Theory',
    ARRAY['metaphysics'],
    'The view that an ordinary object is nothing but a bundle of its properties — there is no underlying substance bearing the properties. The apple just is the bundle of compresent properties: round, red, sweet, located here, etc. Defenders include Russell (in the "Inquiry into Meaning and Truth" and elsewhere), Castaneda, and (in trope-theoretic form) Williams and Campbell.',
    'Bundle theory is the canonical alternative to substance ontology — its existence is one of the reasons substance is interesting. The motivating argument: if we strip away an object''s properties one by one, what remains? Nothing intelligible (Hume''s missing missing-something objection to substance). So the object is nothing more than the bundle. The standard objections: (1) the duplicates problem (Black''s two-spheres) — two objects sharing all qualitative properties would be identical on bundle theory, but they could be qualitatively indiscernible while numerically distinct; (2) change — how can a bundle of properties change properties without becoming a different bundle? (3) the role of compresence — what makes the properties bundle rather than just exist? Compresence becomes a primitive structural relation that does substance-like work. Trope-theoretic bundle theory (objects are bundles of compresent tropes rather than universals) avoids the duplicates problem, since distinct tropes ground the numerical distinctness of qualitatively identical objects.',
    ARRAY['bundle_theory_of_objects', 'compresence_theory'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'mereology',
    'Mereology',
    ARRAY['metaphysics'],
    'The formal theory of parts and wholes. Classical extensional mereology (Lesniewski, Goodman-Leonard) takes parthood as primitive and characterizes composition via a few axioms (transitivity, reflexivity, supplementation). Studies the relation between an object and its parts, when parts compose a whole, what the simples (partless ultimates) are if any, and whether composition is ever genuine versus always pluralism-in-disguise.',
    'Distinguish mereology (the formal theory of parts and wholes; can be done as logic without metaphysical commitments) from the metaphysics of composition (the substantive question of when objects compose). Classical extensional mereology is a mathematically tractable theory that makes universalist commitments by default — any objects whatsoever compose a further object. The metaphysical disputes are largely about whether classical mereology is the right theory: nihilists (van Inwagen) deny most of its composition principles; non-extensional theorists (Fine, Koslicki) reject the extensionality axiom (objects with the same parts may differ — a statue and the lump of clay it is made of). Pedagogically the entry point is the question "when do parts compose a whole?" rather than the formal axioms; the axioms are then the technical machinery the metaphysical answer must accommodate.',
    ARRAY['theory_of_parts', 'parthood_theory'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'composition_mereological',
    'Composition (Mereological)',
    ARRAY['metaphysics'],
    'The relation that holds when some objects (the parts) make up a further object (the whole). The Special Composition Question (van Inwagen 1990): under what conditions do some objects compose a further object? Possible answers range from universalism (any objects compose) to nihilism (no objects compose, except perhaps simples or organisms) to moderate views (only objects standing in specific relations — fastening, life, contact — compose).',
    'Van Inwagen''s "Material Beings" (1990) is the contemporary anchor. He poses the Special Composition Question and surveys answers, ultimately defending a near-nihilist view that composition occurs only when the parts are caught up in a life (so organisms exist; tables, statues, and stars do not compose, strictly speaking, though we can talk *as if* they do for ordinary purposes). Lewis and Sider defend universalism as the simplest answer: composition is unrestricted, every fusion exists. Moderate views (Markosian''s contact-based answer) try to capture commonsense ontology but face the arbitrariness charge — what privileges contact over other relations? The dispute is not just about which everyday objects exist; it is about whether the answer to the composition question can be principled or must accept a surprising near-extreme position.',
    ARRAY['mereological_composition', 'special_composition_question'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'simples',
    'Simples',
    ARRAY['metaphysics'],
    'Partless ultimate entities — objects with no proper parts. Atomism (the view that there are simples) is contested by gunk theorists (no simples, every part has further proper parts). The question whether the world contains simples is empirically informed (physics suggests fundamental particles or strings) but not settled by physics, since metaphysical simples need not coincide with physical fundamentals.',
    'The Aristotelian and modern atomist intuition is that finite division must terminate: at some level of structural decomposition, the things we encounter must be partless. The opposing intuition (gunk) is that division could go all the way down without termination. The simples question intersects with composition: classical mereology requires either simples or gunk (the axioms force the issue); if there are simples they are the building blocks of every composite; if everything is gunk every object has proper parts at every level. Pedagogically the entry point is: ask whether there must be partless ultimates and watch the mathematical, metaphysical, and physical considerations diverge in their answers.',
    ARRAY['mereological_simples', 'atomic_simples'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'gunk',
    'Gunk',
    ARRAY['metaphysics'],
    'The hypothesis that there are no simples — that every object has proper parts, which themselves have proper parts, ad infinitum. The alternative to atomism. The term "gunk" is Lewis''s. Gunk theorists hold that classical mereology can hold even without simples; nothing in the axioms requires that division terminate.',
    'Gunk is the radical alternative to the simples hypothesis. The motivating intuition is that there is no obvious reason division must terminate — either physical division (we keep finding finer structure) or conceptual division (any extended thing has spatial parts). Gunk has costs: it conflicts with most natural pictures of fundamental physics (which posits fundamental particles); it puts pressure on certain analyses of supervenience and grounding (where do we anchor the metaphysical foundations?); it has surprising consequences for theories of persistence and constitution. But it has defenders (Sider, Schaffer in some moods) who argue the costs are not decisive. Pedagogically gunk is useful as a thought-experiment that exposes hidden atomist commitments in seemingly neutral theories.',
    ARRAY['atomless_gunk'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'mereological_universalism',
    'Mereological Universalism',
    ARRAY['metaphysics'],
    'The view that any plurality of objects whatsoever composes a further object. Lewis, Sider, and the classical mereologists hold that the trout-turkey (a fusion of a trout and a turkey) and the Eiffel-Tower-plus-Mars (a fusion of those two objects) exist just as much as ordinary objects do. The view is the universalist answer to the Special Composition Question.',
    'Universalism is attractive for its simplicity: composition is utterly unrestricted, requires no specific relations among the parts, and gives classical mereology a clean field. The cost is heavy commitment to non-commonsense objects: trout-turkeys, Eiffel-Tower-plus-Mars, and arbitrarily gerrymandered fusions all exist. Universalists embrace this as a feature: the gerrymandered objects exist; we just rarely care about them, refer to them, or have words for them — but their existence is no more puzzling than the existence of objects we do care about. The Lewis-Sider universalist package goes naturally with perdurantism (which has temporal as well as spatial parts) and modal realism (which extends the same atomistic-fusion logic across worlds). Universalism is the simplest answer; what it lacks in commonsense fit it makes up for in mathematical economy.',
    ARRAY['unrestricted_composition', 'universal_composition'],
    'INTERPRETED',
    'ai-seed',
    5
  ),
  (
    'mereological_nihilism',
    'Mereological Nihilism',
    ARRAY['metaphysics'],
    'The view that no objects compose any further object — strictly speaking, only simples exist; tables, chairs, and stars do not. Strict nihilism (Cian Dorr, Ted Sider in some moods) holds that all composition talk is loose; van Inwagen''s "Material Beings" (1990) defends a moderate near-nihilism on which composition occurs only when the parts are caught up in a life (so organisms exist; ordinary inanimate objects do not).',
    'Nihilism is the universalism-rejecting answer to the Special Composition Question. Strict nihilists deny that anything composes; the only objects are simples (or, for gunk-friendly nihilists, even simples are derivative). Van Inwagen''s near-nihilism is a compromise: most ordinary objects don''t exist (no statues, no rocks, no chairs in the strict sense), but living organisms do — life is the kind of structure that genuinely brings about composition. The motivation in both cases is principled answer to the composition question: instead of accepting all fusions (universalism) or arbitrarily privileging some over others (moderate views), nihilism keeps composition restrictive and motivated. The cost is the gap with everyday talk; nihilists explain away ordinary object talk via paraphrase or pretense.',
    ARRAY['mereological_nihilism_metaphysics', 'compositional_nihilism'],
    'INTERPRETED',
    'ai-seed',
    5
  );

-- Edges: 36 INSERTs, all pedagogical_prerequisite. All within-domain
-- (source and target both tagged metaphysics). Cross-domain edges
-- (modality -> logic / philosophy of language; free_will -> ethics;
-- universals -> philosophy of mathematics; mereology -> philosophy of
-- science; bundle_theory -> philosophy of mind on bundle theory of
-- self) are P5-11's exclusive surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Modality cluster (within-cluster forward edges)
  ('modality', 'possible_worlds', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('modality', 'essence_metaphysical', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('possible_worlds', 'modal_realism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('possible_worlds', 'ersatz_modal_realism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('possible_worlds', 'haecceity', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('possible_worlds', 'counterpart_theory', 'pedagogical_prerequisite', 'ai-seed', 5),
  -- Free will cluster (within-cluster forward edges)
  ('free_will', 'determinism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('free_will', 'compatibilism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('free_will', 'incompatibilism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('free_will', 'moral_responsibility', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('free_will', 'principle_of_alternative_possibilities', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('incompatibilism', 'libertarianism_metaphysical', 'pedagogical_prerequisite', 'ai-seed', 5),
  -- Properties / Universals cluster (within-cluster forward edges)
  ('universals', 'realism_about_universals', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('universals', 'nominalism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('universals', 'tropes', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('tropes', 'bundle_theory', 'pedagogical_prerequisite', 'ai-seed', 5),
  -- Mereology cluster (within-cluster forward edges)
  ('mereology', 'composition_mereological', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('composition_mereological', 'simples', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('composition_mereological', 'gunk', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('composition_mereological', 'mereological_universalism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('composition_mereological', 'mereological_nihilism', 'pedagogical_prerequisite', 'ai-seed', 5),
  -- Cross-references from P5-02a foundational concepts into specialized concepts
  ('existence', 'modality', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('abstract_object', 'possible_worlds', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('numerical_identity', 'counterpart_theory', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('numerical_identity', 'haecceity', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('numerical_identity', 'mereology', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('causation', 'free_will', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('causation', 'determinism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('property', 'universals', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('property', 'realism_about_universals', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('property', 'nominalism', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('property', 'tropes', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('substance', 'bundle_theory', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('concrete_object', 'mereology', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('concrete_object', 'composition_mereological', 'pedagogical_prerequisite', 'ai-seed', 5),
  ('temporal_parts', 'mereology', 'pedagogical_prerequisite', 'ai-seed', 5);

COMMIT;
