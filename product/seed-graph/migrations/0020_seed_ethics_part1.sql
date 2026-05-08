-- Migration: 0020_seed_ethics_part1
-- Purpose: Sixth Phase 5 seed migration (first ethics file) — metaethics
--   and normative-theory concepts plus within-domain
--   pedagogical_prerequisite edges. Authored in S-0058 against task
--   P5-04a "Ethics metaethics+normative seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   P5-04a is the pre-split a-half of the ethics subdomain per
--   phase_5.md T1-B; P5-04b (Ethics applied — bioethics, environmental
--   ethics, applied moral problems) is the b-half and depends on this
--   one's foundational ethics inventory. Covers two layers: (1) the
--   metaethics layer — moral realism, moral anti-realism (with error
--   theory and expressivism as anti-realist sub-positions), moral
--   naturalism vs non-naturalism, the open-question argument, moral
--   epistemology, motivational internalism vs externalism, the
--   is-ought distinction; (2) the normative-theory layer —
--   consequentialism (with utilitarianism canonical and hedonism as
--   value theory), deontology (with Kantian ethics and the
--   categorical imperative as the canonical articulation), virtue
--   ethics (with eudaimonia and practical wisdom as the Aristotelian
--   anchors), contractualism, divine command theory, ethical egoism,
--   moral particularism, plus supererogation as the structural concept
--   that tests every normative theory.
-- Loads tables: public.nodes (28 INSERTs), public.edges (34 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 6 -> 7).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 6 at session boot (post-S-0057; verified
--     via Supabase MCP execute_sql at S-0058 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 7 (the
--     post-increment value).
--   * P5-01a epistemology core seed applied (0011) — depends_on
--     dependency satisfied since S-0050. P5-04a has no other Phase 5
--     dependencies; ethics concepts are introduced de novo in this seed,
--     independent of metaphysics or logic inventories. Cross-domain
--     bridges into logic (deontology↔deontic_logic; the formal logic of
--     obligation that von Wright introduced; chisholm_paradox bears on
--     contrary-to-duty obligations within deontology), into metaphysics
--     (free_will and moral_responsibility from P5-02b are presupposed
--     by every normative theory's account of moral agency; the
--     principle_of_alternative_possibilities bears on libertarian-vs-
--     compatibilist accounts of desert), into epistemology (knowledge,
--     belief, justification all bear on moral_epistemology; testimonial_
--     knowledge bears on moral testimony debates), and into political
--     philosophy (P5-05's contractualist tradition and theories of
--     justice both extend ethical contractualism into the political
--     register) all defer to P5-11 cross-bridges per phase_5.md T2-G #1.
--   * No prior migrations under prefix 0020-0029; this is the first
--     ethics seed file.
-- Postconditions:
--   * 28 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'ethics'}, status=active, graph_version_added=7.
--   * 34 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=7. All edges are
--     within-domain (source and target both tagged ethics);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 7.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 7 AND 'ethics' = ANY(domain) :: 28
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 7 AND edge_type = 'pedagogical_prerequisite' :: 34
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 7
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract). The
--     `_ethics` suffix is used on no node here — every concept's bare
--     name is unambiguous within ethics, and cross-domain disambiguation
--     against e.g. P5-02b's free_will / moral_responsibility (which
--     live in metaphysics, distinct from ethics-side normative concepts)
--     happens via domain[] arrays rather than name suffixes. The closest
--     potential collisions are `expressivism` (could appear in
--     philosophy of language under emotivist-meaning theories — the
--     concept is fundamentally metaethical even when applied to language)
--     and `naturalism` / `non_naturalism` (general philosophical positions
--     that have ethics-specific articulations) — handled here with the
--     `moral_` prefix to mark the ethics-specific sense.
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts. Like P5-03 (single-task, internally self-contained),
--     P5-04a's a-half is self-contained on its own foundational
--     concepts; P5-04b's applied-ethics b-half will reference back
--     into these metaethics-and-normative concepts.
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph layers as a DAG with the broad shape:
--     T0: morality.
--     T1: metaethics, normative_ethics.
--     T2: moral_realism, moral_anti_realism, is_ought_distinction;
--       consequentialism, deontology, virtue_ethics, contractualism,
--       ethical_egoism, divine_command_theory, moral_particularism.
--     T3: moral_epistemology, moral_naturalism, moral_non_naturalism,
--       error_theory, supererogation, utilitarianism, kantian_ethics,
--       eudaimonia, practical_wisdom.
--     T4: open_question_argument, motivational_internalism, hedonism,
--       categorical_imperative.
--     T5: motivational_externalism, expressivism.
--     Every edge below points from a lower-tier source to a higher-
--     tier target. validate.py's Kosaraju SCC check confirms post-apply
--     that the pedagogical_prerequisite subgraph remains acyclic
--     globally (the prior 0011 / 0016 / 0030 / 0036 / 0090 seeds plus
--     this one's 34 edges, all together).
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: deontology bridges to logic
--     (P5-03's deontic_logic is the formal apparatus deontology motivates;
--     chisholm_paradox bears on contrary-to-duty obligations within
--     deontological theories); kantian_ethics bridges to philosophy of
--     mind (Kant's account of rational agency presupposes a robust
--     conception of practical reason that bears on P5-07a's intentionality
--     and free_will themes); virtue_ethics bridges to philosophy of mind
--     (eudaimonia and practical_wisdom presuppose substantive accounts
--     of human nature and rational agency); contractualism bridges to
--     political philosophy (P5-05's social contract tradition extends
--     ethical contractualism into political legitimacy); moral_realism
--     and moral_anti_realism bridge to metaphysics (the existence
--     question for moral properties is metaphysically substantive);
--     moral_naturalism bridges to philosophy of science (Cornell-style
--     naturalists treat moral properties as natural properties amenable
--     to empirical investigation); moral_epistemology bridges to
--     epistemology (knowledge, belief, justification, intuition — the
--     general epistemological apparatus is what moral_epistemology
--     applies to moral claims); is_ought_distinction bridges to
--     philosophy of language (the meaning of normative vocabulary in
--     natural language); free_will and moral_responsibility from P5-02b
--     are presupposed by every normative theory's account of moral
--     agency — desert-tracking views in particular need libertarianism
--     or compatibilism to ground responsibility ascriptions. All of
--     these defer to P5-11.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md). The historical_influence predicate is
--     not used here either; ethics's intellectual history (Aristotle ->
--     Aquinas -> Kant -> Mill -> Moore -> Ross -> Hare -> Foot -> Anscombe
--     -> Rawls -> Scanlon -> Williamson) is rich but the historical-
--     influence pass is deferred to a later phase per PREDICATE_MANIFEST.md
--     "historical_influence" row.
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0021-0025). Those
--     slots remain reserved for future ethics extension if Phase 6+
--     telemetry warrants additional metaethics or normative concepts
--     (prima facie duties, agent-relative vs agent-neutral reasons, moral
--     dilemma, moral luck, supervenience-of-the-moral, the role of
--     intuition in reflective equilibrium, the Frege-Geach problem against
--     expressivism). This seed completes P5-04a's task at the
--     granularity principle within the 0020 file: 28 nodes covering the
--     two named layers (metaethics + normative theory) at the umbrella-
--     plus-canonical-positions density that P5-01a / P5-01b / P5-02a /
--     P5-02b / P5-03 each established. P5-04b (applied ethics —
--     bioethics, environmental ethics, applied moral problems) will
--     claim 0026-0029 per phase_5.md T2-A.
-- Cross-cutting decisions:
--   * confidence_level distribution: 28/28 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the contemporary analytic
--     literature (Mackie, Moore, Ayer, Stevenson, Blackburn, Gibbard,
--     Boyd, Brink, Smith, Hume, Mill, Kant, Aristotle, Aquinas, Anscombe,
--     Foot, Hursthouse, MacIntyre, Rawls, Scanlon, Adams, Dancy, Ross)
--     explicitly names. Mirrors P5-01a / P5-01b / P5-02a / P5-02b /
--     P5-03's distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'ethics'. Multiple cross-domain reaches exist (deontology into
--     logic for deontic_logic; moral_responsibility ↔ free_will into
--     metaphysics; contractualism into political philosophy) but per
--     phase_5.md T2-G #1, cross-domain tagging belongs to P5-11. The
--     canonical home for each of these concepts in the analytic
--     literature is ethics, so the single tag is correct here.
--   * provenance: 'ai-seed' for every node and edge.
--   * Node selection rationale: 28 concepts cover the two named layers
--     at the granularity principle. Foundation (1): morality (the
--     subdomain umbrella). Metaethics layer (12): metaethics (cluster
--     umbrella); moral_realism, moral_anti_realism (the central
--     ontological cleavage); error_theory, expressivism (the two
--     dominant anti-realist positions); moral_naturalism,
--     moral_non_naturalism (the central naturalism question; the dispute
--     over whether moral properties reduce to natural ones);
--     open_question_argument (Moore 1903's canonical attack on
--     naturalism); moral_epistemology (the umbrella for how we know
--     moral facts); motivational_internalism, motivational_externalism
--     (the central motivation question; whether sincere moral judgment
--     necessarily motivates); is_ought_distinction (Hume's canonical
--     gap between descriptive and normative claims). Normative theory
--     layer (15): normative_ethics (cluster umbrella); consequentialism,
--     utilitarianism, hedonism (the consequentialist family with
--     classical utilitarianism canonical and hedonism as the value
--     theory underwriting it); deontology, kantian_ethics,
--     categorical_imperative (the deontological family with Kantian
--     ethics canonical and the categorical imperative as the central
--     formulation); virtue_ethics, eudaimonia, practical_wisdom (the
--     virtue family with Aristotelian eudaimonism canonical and
--     phronesis as the central virtue); contractualism (Scanlon-style
--     "what no one can reasonably reject"); divine_command_theory
--     (the religious normative family); ethical_egoism (rational
--     self-interest as moral basis); moral_particularism (Dancy's
--     anti-principlism); supererogation (the structural concept
--     testing whether every normative theory has space for "above and
--     beyond duty" — utilitarianism famously has trouble with it,
--     deontology and virtue ethics handle it more naturally).
--   * Edge structure: 34 edges total, all pedagogical_prerequisite,
--     all within-domain. Foundation tier (2) wires morality →
--     metaethics and morality → normative_ethics. Metaethics
--     substructure (4): metaethics → moral_realism; metaethics →
--     moral_anti_realism; metaethics → moral_epistemology;
--     metaethics → is_ought_distinction. Within metaethics (11):
--     moral_anti_realism → error_theory; moral_anti_realism →
--     expressivism; moral_realism → moral_naturalism; moral_realism →
--     moral_non_naturalism; moral_realism → moral_epistemology
--     (realism makes moral epistemology especially pressing —
--     epistemic access to a mind-independent moral order is the
--     question); moral_naturalism → open_question_argument (Moore's
--     argument targets naturalism specifically; pedagogically you
--     understand naturalism before grasping the open-question
--     critique); is_ought_distinction → moral_naturalism (Hume's gap
--     motivates skepticism about reducing ought-claims to is-claims);
--     is_ought_distinction → error_theory (Mackie's queerness
--     argument extends Hume's gap into a positive case that moral
--     properties don't exist in the natural world); moral_epistemology
--     → motivational_internalism (the question how moral knowledge
--     motivates is itself moral-epistemological); motivational_
--     internalism → motivational_externalism (externalism is the
--     direct response to internalism); motivational_internalism →
--     expressivism (expressivism explains internalism most naturally
--     — moral judgments express desires, which intrinsically
--     motivate). Normative umbrellas (7): normative_ethics → each of
--     the seven normative theories. Within consequentialism (2):
--     consequentialism → utilitarianism (utilitarianism is the
--     canonical consequentialism); utilitarianism → hedonism (classical
--     utilitarianism is hedonistic about the good — Bentham, Mill — so
--     hedonism's value theory underwrites utilitarianism's normative
--     theory). Within deontology (2): deontology → kantian_ethics
--     (Kantian ethics is the canonical deontology); kantian_ethics →
--     categorical_imperative (the categorical imperative is the
--     central principle of Kantian ethics). Within virtue ethics (3):
--     virtue_ethics → eudaimonia; virtue_ethics → practical_wisdom;
--     virtue_ethics → moral_particularism (Dancy's particularism is
--     virtue-ethics-adjacent — judgment in particulars resembles
--     phronesis, and particularism resists principle-codification in
--     a way virtue ethics also tends to). Supererogation (3):
--     normative_ethics → supererogation; deontology → supererogation
--     (deontology faces the question whether supererogation is
--     coherent — if perfect duties exhaust the obligatory, what room
--     for the supererogatory?); consequentialism → supererogation
--     (consequentialism notoriously has trouble with supererogation
--     — every act of charity producing more good is OBLIGATORY on
--     act-utilitarianism, leaving no space for "above and beyond";
--     this is one of the canonical objections to consequentialism).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 7; DELETE FROM public.nodes WHERE id IN (the 28 ids inserted
--   here); UPDATE public.settings SET value = '6'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 63 statements
--   atomically — manual rollback above applies to the post-commit
--   window only. The 28 ids: morality, metaethics, moral_realism,
--   moral_anti_realism, error_theory, expressivism, moral_naturalism,
--   moral_non_naturalism, open_question_argument, moral_epistemology,
--   motivational_internalism, motivational_externalism,
--   is_ought_distinction, normative_ethics, consequentialism,
--   utilitarianism, hedonism, deontology, kantian_ethics,
--   categorical_imperative, virtue_ethics, eudaimonia, practical_wisdom,
--   contractualism, divine_command_theory, ethical_egoism,
--   moral_particularism, supererogation.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0090_seed_logic_part1.sql (P5-03
--   logic seed; immediate-prior pattern reference and the locus of
--   deontic_logic which P5-04a's deontology cross-bridges to at P5-11);
--   product/seed-graph/migrations/0036_seed_metaphysics_part1.sql
--   (P5-02b specialized; locus of free_will and moral_responsibility
--   that ethics presupposes — P5-11 cross-bridges to those);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 6 at session boot (post-S-0057 state); write 7 here;
-- every node/edge below carries graph_version_added = 7.
UPDATE public.settings
  SET value = '7'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 28 INSERTs covering the metaethics layer plus the normative-theory layer.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'morality',
    'Morality',
    ARRAY['ethics'],
    'The domain of right and wrong action, good and bad character, and the reasons we have to act in some ways and not others. Distinct from etiquette (which carries no overriding force), legality (whose authority is institutional rather than universal), and prudence (which tracks self-interest rather than the moral). Morality''s canonical questions split into the metaethical (what makes moral claims true; what their meaning is; how we know them) and the normative (what specifically is right, what character traits are virtuous, what reasons obligate us).',
    'Begin ethics by drawing the morality-vs-non-morality boundary carefully. Etiquette governs polite behavior but has no overriding moral force — breaking a dinner-party rule is not a moral failing in any robust sense. Legality has institutional rather than universal authority — what is legal in one jurisdiction is illegal in another, and bad laws can persist that morality condemns (slavery, apartheid). Prudence governs self-interest — eating well to live longer is prudentially required but not morally so. Morality lays claim to overriding, universal, agent-relative-or-neutral reasons in a way these adjacent normative domains do not. The two principal questions: METAETHICS asks "what makes moral claims true / meaningful / knowable"; NORMATIVE ETHICS asks "what specifically should we do, what character should we cultivate, what is right". The two questions are connected — your metaethics constrains which normative theories are even coherent — but distinct enough to teach in succession.',
    ARRAY['the_moral', 'moral_domain', 'ethical_domain'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'metaethics',
    'Metaethics',
    ARRAY['ethics'],
    'The branch of ethics asking second-order questions about morality itself: what makes moral claims true (the ontology of moral facts), what moral language means (the semantics of moral discourse), how we come to know moral truths (moral epistemology), what moral judgments express (cognitive belief or non-cognitive attitude), and how moral judgments motivate action (the connection between judgment and motivation). Distinguished from normative ethics, which asks first-order questions about what is right and what we should do.',
    'Metaethics is ethics about ethics. Where normative ethics asks "is abortion morally permissible?" or "what does courage require?", metaethics asks "what would make any answer to those questions TRUE?", "what does the word ''wrong'' MEAN?", "how could we KNOW the answer?", and "would knowing it MOVE us to act?". The distinction was drawn sharply by 20th-century moral philosophy (Moore 1903 inaugurates the field; the Stevenson-Hare-Mackie-Brink tradition develops it through the century) but the questions are older. The four canonical metaethical axes are: (i) realism vs anti-realism — are there mind-independent moral facts? (ii) cognitivism vs non-cognitivism — do moral utterances express beliefs (truth-apt) or attitudes (not truth-apt)? (iii) naturalism vs non-naturalism — IF moral facts exist, are they natural facts (descriptive, empirically tractable) or sui generis? (iv) internalism vs externalism — does sincere moral judgment necessarily motivate, or is motivation a separate matter? Each axis has multiple defensible positions; combinations form distinct overall metaethical packages.',
    ARRAY['meta_ethics', 'second_order_ethics'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_realism',
    'Moral Realism',
    ARRAY['ethics'],
    'The metaethical position that there are mind-independent moral facts — moral truths are TRUE not because we (individually or collectively) believe, prefer, or accept them, but because they correctly describe an objective moral order. Standard moral realisms commit to (i) cognitivism (moral utterances express truth-apt beliefs), (ii) the existence of moral facts (some moral propositions are true), and (iii) the mind-independence of those facts. Compatible with both naturalism (moral facts are natural facts) and non-naturalism (moral facts are sui generis).',
    'Moral realism is the default common-sense view: when we say "torturing innocents for fun is wrong", we mean it is REALLY wrong, not just disapproved-of-by-our-culture or contrary-to-our-preferences. The realist takes moral discourse at face value as describing a moral reality. The challenge facing realism is the metaphysics: WHAT KIND of fact is a moral fact? If natural (the Cornell-realist line: Boyd, Brink, Sturgeon — moral properties are natural properties amenable to empirical investigation), the realist owes an account of which natural properties they are and how we know which they are. If non-natural (the Moore-Parfit line — moral properties are sui generis, irreducible to natural properties), the realist owes an account of how we have epistemic access to non-natural properties. Mackie''s 1977 ARGUMENT FROM QUEERNESS attacks realism on metaphysical and epistemological grounds: moral properties (if they existed) would have to be intrinsically motivating ("to-be-pursued-ness", as Mackie put it, built into the property), and no plausibly natural property has this character. Realism remains a leading position; the queerness objection is taken seriously and answered, not dismissed.',
    ARRAY['moral_objectivism', 'ethical_realism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_anti_realism',
    'Moral Anti-Realism',
    ARRAY['ethics'],
    'The umbrella for metaethical positions denying mind-independent moral facts. Includes (a) error theory — moral utterances aim at truth but are systematically false because the moral facts they purport to describe don''t exist; (b) expressivism / non-cognitivism — moral utterances don''t aim at truth at all but rather express attitudes, prescriptions, or commitments; (c) constructivism — moral facts exist but are constituted by an idealized procedure of agreement, deliberation, or reasoned reflection rather than tracking a mind-independent order. Anti-realisms differ on whether moral discourse is COGNITIVE (truth-apt) and whether moral propositions can be TRUE.',
    'Anti-realism is the family of views denying that moral discourse describes a mind-independent moral reality. The three main branches: (i) ERROR THEORY (Mackie 1977) — moral discourse is cognitive (it makes truth-apt claims) but systematically false (the moral facts it claims to describe don''t exist; we are all in error when we make first-order moral claims). (ii) EXPRESSIVISM / NON-COGNITIVISM (Ayer 1936, Stevenson 1944, Hare 1952, Blackburn 1984, Gibbard 1990) — moral utterances aren''t even truth-apt; they express attitudes, emotions, prescriptions, or normative commitments rather than describing facts. The Frege-Geach problem (how can expressivism account for unasserted moral claims in conditionals and inferences?) is the central technical challenge. (iii) CONSTRUCTIVISM (Korsgaard 1996, Street 2008) — moral facts are real, but they''re constituted by an idealized procedure (Kantian rational agency, Humean attitudes, Rawlsian original position) rather than tracking a pre-given moral order. Constructivism occupies a middle position: arguably realist about moral facts (they exist and are objective in some sense) while anti-realist about their grounding (they depend on rational/practical procedures rather than independent moral reality). The boundaries between constructivism, sophisticated naturalist realism, and certain expressivisms are contested.',
    ARRAY['anti_realism_ethics', 'moral_irrealism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'error_theory',
    'Error Theory',
    ARRAY['ethics'],
    'J.L. Mackie''s 1977 metaethical position (Ethics: Inventing Right and Wrong): moral discourse is cognitive — it makes truth-apt claims — but those claims are SYSTEMATICALLY FALSE because the moral facts they presuppose do not exist. Mackie defends error theory via two arguments: (i) the ARGUMENT FROM RELATIVITY — actual moral disagreement across cultures and traditions is best explained by the absence of a fact of the matter; (ii) the ARGUMENT FROM QUEERNESS — moral properties, if they existed, would be intrinsically motivating in a way no plausible natural property is, and we have no faculty for detecting non-natural intrinsically-motivating properties.',
    'Error theory is the position that all positive moral assertions are FALSE — not just controversial moral claims, but every positive moral utterance, including "torture is wrong" and "you should help your friend in need". Mackie''s 1977 argument has two prongs. The argument from RELATIVITY observes that moral disagreement persists across cultures and historical periods on questions where (if there were moral facts) we should expect convergence; the best explanation is that there are no moral facts to converge on. The argument from QUEERNESS argues metaphysically and epistemologically: moral properties (if they existed) would need to be intrinsically action-guiding ("to-be-pursued-ness" built into them), which is "queer" — no other property in the natural world has this character; and even if such properties existed, we''d have no plausible epistemic access to them. Error theory is striking because it accepts cognitivism (moral claims are truth-apt) but rejects realism (the truth-makers don''t exist). The first-order practical question is what to do — Mackie himself proposed a kind of "second-best" project of inventing morality knowing it''s an invention; "abolitionist" error theorists (Garner) propose abandoning moral discourse; "fictionalist" error theorists (Joyce 2001) propose retaining moral discourse as a useful fiction.',
    ARRAY['mackie_error_theory', 'moral_error_theory'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'expressivism',
    'Expressivism',
    ARRAY['ethics'],
    'The metaethical position that moral utterances do not describe facts but EXPRESS attitudes — emotions, prescriptions, plans, normative commitments. "Murder is wrong" doesn''t describe a fact about murder; it expresses the speaker''s disapproval of murder, or their endorsement of a norm against murdering. Originated in A.J. Ayer''s 1936 emotivism (LANGUAGE, TRUTH AND LOGIC) and Charles Stevenson''s 1944 ETHICS AND LANGUAGE; refined through Hare''s 1952 prescriptivism and developed in the late 20th century by Simon Blackburn (quasi-realism) and Allan Gibbard (norm-expressivism, plan-expressivism). The central technical challenge is the FREGE-GEACH PROBLEM.',
    'Expressivism is the dominant non-cognitivist view in contemporary metaethics. The basic move is to interpret "murder is wrong" not as describing the property "wrongness" inhering in murder, but as expressing the speaker''s attitude toward murder. The view explains MOTIVATIONAL INTERNALISM elegantly: if moral judgments express desires (or other motivating states), they intrinsically motivate. The Frege-Geach problem (after Peter Geach''s 1965 paper) is the central technical challenge: in inferences like "if murder is wrong then getting your sibling to murder is wrong; murder is wrong; therefore getting your sibling to murder is wrong", the second occurrence of "murder is wrong" inside the conditional is not asserted, so it doesn''t express a current attitude — yet inference treats it as having the same meaning as the third (asserted) occurrence. Sophisticated expressivisms (Blackburn''s quasi-realism, Gibbard''s plan-expressivism) develop apparatus for embedded moral claims. The result is theoretically sophisticated but contested: critics charge that successful Frege-Geach responses make expressivism look more like sophisticated realism than non-cognitivism. The cross-bridge to philosophy of language (P5-08) is real: expressivism is fundamentally a thesis about the meaning of moral discourse.',
    ARRAY['non_cognitivism', 'emotivism', 'prescriptivism', 'norm_expressivism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_naturalism',
    'Moral Naturalism',
    ARRAY['ethics'],
    'The metaethical position that moral properties are NATURAL properties — properties of the kind investigated by the natural and social sciences. Two main varieties: (i) REDUCTIVE naturalism — moral properties are identical to specific descriptive properties (e.g., goodness is happiness, or rightness is welfare-maximization); (ii) NON-REDUCTIVE naturalism (the Cornell realists — Boyd 1988, Brink 1989, Sturgeon 1985) — moral properties are natural but not reducible to a specific descriptive predicate; they SUPERVENE on natural properties and are amenable to empirical inquiry through the methods of philosophy and social science. Compatible with moral realism and (typically) with cognitivism.',
    'Moral naturalism is the empirically-friendly form of moral realism. The reductive variety identifies moral properties with natural properties (Bentham''s utilitarianism reduces "right" to "welfare-maximizing"; Aristotelian ethical naturalism reduces "good for X" to "what makes X function well as the kind of thing X is"). The non-reductive variety (Cornell realism) takes moral properties to be natural but irreducible — like biological or psychological properties, they can be investigated empirically without being identical to any specific lower-level descriptive property. The Cornell realists explicitly model moral inquiry on scientific inquiry: we discover moral truths the way we discover scientific truths, through observation, theory-construction, and reflective equilibrium. The HUMEAN GAP (the is-ought distinction) and Moore''s OPEN-QUESTION ARGUMENT are the two central historical challenges: how can a descriptive natural property capture the normative force of moral claims? Naturalists answer in different ways — reductivists deny the gap (the descriptive IS the normative, properly understood); non-reductivists accept the gap as a methodological reminder but deny it forecloses naturalism (moral properties are natural but normative, just as biological functions are natural but teleological).',
    ARRAY['ethical_naturalism', 'cornell_realism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_non_naturalism',
    'Moral Non-Naturalism',
    ARRAY['ethics'],
    'The metaethical position that moral properties are SUI GENERIS — irreducibly moral, not identical to or reducible to any natural (descriptive, empirical) property. G.E. Moore''s 1903 PRINCIPIA ETHICA inaugurates the position: "good" is a simple, indefinable, non-natural property, immediately known by intellectual intuition. Derek Parfit''s ON WHAT MATTERS (2011) revives non-naturalism in a sophisticated form, defending non-natural normative truths discovered through reasoned reflection. Compatible with realism (Moore, Parfit are realists); typically faces the epistemological challenge of how we have access to non-natural properties.',
    'Moral non-naturalism takes the moral domain at metaphysical face value — moral properties exist and are genuinely moral, not reducible to any descriptive property the natural sciences study. Moore''s 1903 OPEN-QUESTION ARGUMENT is the position''s canonical defense: for any natural property P proposed as identical to goodness (pleasure, desire-satisfaction, welfare), the question "is P good?" remains a substantive open question, not an analytic triviality the way "is the bachelor unmarried?" is. So goodness is not P. The argument generalizes to all natural properties. The position is metaphysically unparsimonious — you''re committed to non-natural properties — but accommodates the seeming irreducibility of normative force. Parfit''s 2011 sophisticated defense rests on the claim that non-natural normative truths are discovered by reasoning, much as mathematical truths are. The epistemological challenge: HOW do we have access to non-natural moral properties? Moore appealed to intellectual intuition; Ross''s 1930 development of Mooreanism (THE RIGHT AND THE GOOD) extends intuitionism to specific prima facie duties. Critics charge that moral intuitionism is mysterious — we have no faculty for detecting non-natural properties, and treating moral intuitions as data is suspiciously circular. Non-naturalism remains a respectable but minority position; naturalism and constructivism dominate contemporary realism.',
    ARRAY['ethical_non_naturalism', 'mooreanism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'open_question_argument',
    'Open Question Argument',
    ARRAY['ethics'],
    'G.E. Moore''s 1903 (PRINCIPIA ETHICA, ch. 1) argument against moral naturalism. For any naturalistic definition of "good" — say, "good" = "pleasure" — the question "is pleasure good?" remains a substantively open question, not a closed analytic question like "is the bachelor unmarried?". So "good" is not analytically equivalent to any naturalistic predicate; goodness is a sui generis non-natural property. Moore takes the argument to refute every naturalistic identification of moral properties; Frankena 1939 famously calls the argument an instance of the "naturalistic fallacy".',
    'Moore''s open-question argument is the most discussed argument in 20th-century metaethics. The structure: for ANY proposed definition "good = N" (where N is some natural property), competent speakers of English can ask "is N good?" and find this a substantive question whose answer they don''t know just from understanding the words. By contrast, "is the bachelor unmarried?" is closed for competent speakers — given the meaning of "bachelor", the answer is trivially yes. The contrast shows that "good" is not analytically equivalent to N; the meaning of "good" outstrips any naturalistic analysis. Moore concludes goodness must be a non-natural simple property. The argument has been defended (Parfit 2011) and challenged. Frankena''s 1939 "Naturalistic Fallacy" charge: Moore equivocates between conceptual identity (a stronger claim) and real-world identity (a weaker claim); the latter survives the open-question argument (water = H₂O is informative even though "is H₂O water?" is open to the naive). Modern defenders (Strandberg 2004) restate the argument in terms of conceptual rather than referential analysis: even if pleasure REFERS to the same property as goodness, the CONCEPT of pleasure isn''t identical to the CONCEPT of goodness, since the concepts can be entertained separately and the identification debated. The argument''s legacy is to put the burden of proof on naturalist reductions, not to refute them outright.',
    ARRAY['moore_open_question', 'naturalistic_fallacy'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_epistemology',
    'Moral Epistemology',
    ARRAY['ethics'],
    'The branch of metaethics asking how we know moral truths (if any). Central questions: do we have moral knowledge (and if so, of what)? what justifies our moral beliefs? what role do MORAL INTUITIONS play in justification? are first-order moral judgments warranted by anything besides their convergence with reflective equilibrium across our considered judgments? Major positions include intuitionism (Moore, Ross — moral truths are immediately known via rational intuition), coherentism / reflective equilibrium (Rawls — moral beliefs are justified by their fit with our considered judgments and moral principles in mutual support), and skepticism / error-theoretic positions denying moral knowledge.',
    'Moral epistemology applies the general epistemological apparatus (knowledge, justification, evidence, intuition, testimony) to the moral domain. The four main approaches: (i) INTUITIONISM (Moore, Ross 1930, Audi 2004) — some moral truths are self-evident, immediately apparent to a rational agent who understands them, in a way analogous to how "1+1=2" is immediately evident; first-order moral intuitions are evidence for moral propositions. (ii) COHERENTISM / REFLECTIVE EQUILIBRIUM (Rawls 1971, Daniels 1979) — moral beliefs are justified holistically by their mutual coherence; we adjust both moral principles and moral judgments to reach equilibrium where they support one another. (iii) RELIABILISM applied to morality — beliefs are justified if produced by reliable processes (evolutionary debunking arguments — Street 2006 — challenge the reliability of our moral faculties). (iv) MORAL SKEPTICISM — we lack moral knowledge, either because moral knowledge is impossible (Mackie''s queerness extends to epistemology) or because no faculty reliably tracks moral truth. The cross-bridge to general epistemology (P5-01a/b) is real: moral_epistemology is just epistemology applied to the moral domain. P5-11 will land the bridge edges to knowledge, belief, justification, and the foundationalism-coherentism axis.',
    ARRAY['ethical_epistemology', 'epistemology_of_morals'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'motivational_internalism',
    'Motivational Internalism',
    ARRAY['ethics'],
    'The metaethical position that there is a NECESSARY connection between sincere moral judgment and motivation: someone who sincerely judges that they OUGHT to do A is thereby (at least defeasibly) motivated to do A. Strong internalism holds the connection is not even defeasible — sincere moral judgment ENTAILS some motivation. Weak internalism allows the motivation to be defeated by countervailing desires or weakness of will. Defended by Hare 1952, Blackburn 1984, Smith 1994 (in a refined form). Compatible with expressivism (which explains the connection by making moral judgments express motivational states) but not strictly required by it.',
    'Motivational internalism is the thesis that there''s a NECESSARY (not contingent) link between sincere moral judgment and being motivated to act. If you sincerely judge "I ought to feed my hungry friend", internalism claims you must thereby be at least somewhat motivated to feed them. Externalism (the alternative) treats motivation as a separate matter: a perfectly sincere moral judgment combined with the wrong desires might leave you completely unmotivated. The disagreement bears on AMORALISTS (people who make moral judgments without caring) — internalism says strict amoralism is impossible (anyone who really judges X to be wrong has some motivation against X); externalism allows it. Internalism is naturally explained by expressivism: moral judgments EXPRESS desires, plans, or commitments, which are intrinsically motivating; on a Humean account of motivation (motivation = belief + desire), expressivism puts the desire INSIDE the moral judgment itself. Smith''s 1994 (THE MORAL PROBLEM) refined version distinguishes weak from strong internalism — for weak internalism, sincere moral judgment GIVES one motivation absent overriding factors; for strong internalism the motivation is ineliminable. The debate connects to philosophy of mind (P5-07a) on the structure of practical reason and moral action.',
    ARRAY['internalism_about_motivation', 'humean_internalism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'motivational_externalism',
    'Motivational Externalism',
    ARRAY['ethics'],
    'The metaethical position that the connection between sincere moral judgment and motivation is CONTINGENT, not necessary: moral judgment expresses belief about how things are morally; whether one is motivated by the judgment is a separate question depending on one''s desires and character. Defended by David Brink 1989 (MORAL REALISM AND THE FOUNDATIONS OF ETHICS), Sigrun Svavarsdóttir 1999, and (in a different way) Kantian rationalists who locate the motivation in pure practical reason rather than judgment plus desire.',
    'Motivational externalism treats moral motivation as extrinsic to moral judgment — sincere moral belief plus appropriate desire produces motivation, but the desire isn''t part of the judgment itself. Brink''s 1989 defense (the canonical contemporary statement) emphasizes the AMORALIST as a possible character: someone who fully understands moral truths but is unmoved by them. Strict internalism makes the amoralist incoherent; externalism allows them. The key argument for externalism: real-world moral failure (depression, weakness of will, sociopathy) often involves unmotivating moral judgment — depressed agents may judge "I should call my mother" without any motivation to do so, suggesting the judgment-motivation link is contingent. Internalists (Smith 1994) respond by distinguishing CASES (the depressed agent isn''t in the right rational frame to count as a sincere full moral judgment; sociopaths lack moral judgment in the relevant sense). The externalism-internalism debate connects to the structure of moral psychology: if motivation tracks sincere judgment necessarily, moral psychology has a tightly-integrated structure; if not, motivation is a separate component requiring independent explanation. The cross-bridge to philosophy of mind (P5-07a) on practical rationality and to metaethical realism is real.',
    ARRAY['externalism_about_motivation'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'is_ought_distinction',
    'Is-Ought Distinction',
    ARRAY['ethics'],
    'David Hume''s 1739 (TREATISE OF HUMAN NATURE, III.i.1) observation that descriptive (is) and normative (ought) propositions differ in kind, with no purely descriptive premise sufficient to derive a normative conclusion. The "Humean gap" or "Hume''s law" formalizes this — a deductive argument with only is-premises cannot validly conclude an ought-claim. Distinguished from Moore''s OPEN-QUESTION ARGUMENT (which is about CONCEPTUAL irreducibility), though related: both target attempts to ground ethics in non-normative facts.',
    'Hume''s remark in the TREATISE: "In every system of morality... I have always remark''d, that the author proceeds for some time in the ordinary way of reasoning... when of a sudden I am surpriz''d to find, that instead of the usual copulations of propositions, IS, and IS NOT, I meet with no proposition that is not connected with an OUGHT, or an OUGHT NOT. This change is imperceptible; but is, however, of the last consequence." The point: derivations of normative conclusions from purely descriptive premises commit a logical error. The distinction has both modest and ambitious readings. The MODEST reading: any deductive argument concluding an ought-statement requires at least one ought-premise. (This is technically obvious — if conclusions can only contain content from premises, and the conclusion contains "ought", at least one premise must too.) The AMBITIOUS reading: there''s no rational path from is to ought at all — moral philosophy can''t be grounded in descriptive facts about human nature, well-being, rationality, or anything else. The ambitious reading is contested (Searle 1964 famously attempted a counterexample — promising-as-an-institution generates obligations from descriptive facts; subsequent debate is rich). The is-ought distinction motivates moral non-naturalism (Moore), error theory (Mackie''s queerness), and ethical naturalism''s need to find a way around or through the gap.',
    ARRAY['humes_law', 'humean_gap', 'fact_value_distinction', 'is_ought_problem'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'normative_ethics',
    'Normative Ethics',
    ARRAY['ethics'],
    'The branch of ethics asking first-order questions about what is right, what we should do, and what character traits are virtuous. Distinguished from metaethics (which asks second-order questions about the nature, meaning, and epistemology of moral claims) and applied ethics (which addresses specific moral problems — bioethics, environmental ethics — in detail). The major theoretical families are consequentialism (the right is what produces best outcomes), deontology (the right has features beyond consequences), virtue ethics (the right is what the virtuous person does), contractualism (the right is what no one can reasonably reject), and divine command theory (the right is what God commands).',
    'Normative ethics asks "what should I do?" rather than "what does ''should'' MEAN?". The five major theoretical families: (i) CONSEQUENTIALISM — outcomes are what matter morally; the right action is the one with the best consequences; utilitarianism is the canonical version. (ii) DEONTOLOGY — there are intrinsic features of actions (kept promises, refraining from harm, respecting autonomy) that matter morally beyond consequences; Kantian ethics is the canonical version. (iii) VIRTUE ETHICS — the right action is what the virtuous person would do; the central question is what character to cultivate; Aristotelian eudaimonism is the canonical version, revived in 20th-century philosophy by Anscombe (1958), Foot, MacIntyre (1981), Hursthouse (1999). (iv) CONTRACTUALISM — the right action is what principles no one could reasonably reject; Scanlon (1998) is the canonical version, with Rawls (1971) the earlier political variant. (v) DIVINE COMMAND THEORY — the right is what God commands; defended in the Christian tradition (Adams 1999) and the Islamic Asharite tradition (the right is whatever God''s law decrees). Each family has internal variation (act- vs rule-utilitarianism within consequentialism; deontology of agent-centered restrictions vs deontology of rights; virtue ethics with Aristotelian vs Stoic vs Christian backgrounds). Contemporary normative ethics also includes ethical egoism (rational self-interest as moral basis) and moral particularism (the rejection of exceptionless principles altogether).',
    ARRAY['first_order_ethics', 'normative_theory'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'consequentialism',
    'Consequentialism',
    ARRAY['ethics'],
    'The family of normative theories holding that the moral status of an action is determined entirely by its consequences. The right action is the one whose consequences are best (most good, least bad). Pure consequentialism holds NO consideration besides outcomes matters — not the agent''s intentions, not whether rights are violated, not whether promises are kept (except instrumentally as those affect outcomes). Specific consequentialisms differ on (a) what counts as good outcomes (welfare, preference-satisfaction, perfectionist excellence) and (b) at what level the consequence calculation applies (individual acts, action-types, rules, motives, characters).',
    'Consequentialism is the simplest normative theory in structure: only outcomes matter. The right action MAXIMIZES good consequences. Variations come from (i) the THEORY OF VALUE — what makes outcomes good? Hedonism (Bentham, Mill — pleasure and absence of pain); preferentism (modern welfare economics — preference-satisfaction); objective-list theories (Parfit — health, achievement, autonomy on a list); perfectionism (Aristotelian-style — flourishing in human-typical ways). (ii) The LEVEL of evaluation — ACT consequentialism evaluates each action individually by its consequences (Singer''s utilitarianism most famously); RULE consequentialism (Brandt 1979, Hooker 2000) evaluates ACTIONS by reference to RULES whose general adoption would produce best consequences. (iii) The SCOPE of moral consideration — utilitarianism aggregates across persons; egoism considers only self-effects; partialist views weight family or community interests differently. The classical objections to consequentialism: it seemingly licenses HEINOUS ACTIONS when they produce better consequences (the trolley case; harvesting one for five organ transplants); it has trouble with SUPEREROGATION (every act of charity producing more good is OBLIGATORY on act-utilitarianism, leaving no space for "above and beyond"); it requires PERFECT INFORMATION about consequences in advance, which we lack; and it has trouble with INTEGRITY (Williams 1973 — the consequentialist agent is reduced to a maximization-machine, with no special claim to their own projects or relationships).',
    ARRAY['consequentialist_ethics'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'utilitarianism',
    'Utilitarianism',
    ARRAY['ethics'],
    'The classical and canonical consequentialist theory. The right action is the one that maximizes overall utility — typically interpreted hedonically (Bentham, Mill — pleasure minus pain) or in terms of preference-satisfaction (modern economists). Founded by Jeremy Bentham (1789, INTRODUCTION TO THE PRINCIPLES OF MORALS AND LEGISLATION) and refined by John Stuart Mill (1861, UTILITARIANISM). Standard variations: ACT utilitarianism evaluates each action; RULE utilitarianism evaluates rules; HEDONIC utilitarianism takes pleasure as the value; PREFERENCE utilitarianism takes preference-satisfaction as the value.',
    'Utilitarianism is the canonical consequentialism — the right action is the one that maximizes the total balance of pleasure over pain (or, in modern formulations, preference-satisfaction over preference-frustration), aggregated across all affected parties. Bentham''s 1789 founding: morality is governed by the "principle of utility" — choose the action producing the greatest pleasure for the greatest number, with each person counting equally ("everybody to count for one, nobody for more than one"). Mill''s 1861 refinement: pleasures differ in QUALITY as well as quantity (the higher pleasures of intellectual and moral life are not commensurable with mere bodily pleasures), and Mill''s utilitarianism is more nuanced about which goods matter and how. The ACT-RULE distinction: Act utilitarianism (Singer, Smart) evaluates each ACTION by its direct consequences; Rule utilitarianism (Brandt, Hooker) evaluates actions by reference to RULES whose general adoption would maximize utility, accommodating the fact that rule-following has indirect benefits. Classical objections: the trolley problem and lifeboat cases (utilitarianism seemingly endorses sacrificing the few for the many); the experience machine (Nozick 1974 — would you plug into a machine producing maximal simulated pleasure?); the demands of utilitarianism (Singer 1972 — every dollar spent on yourself when you could give it to charity is morally wrong). Pedagogically utilitarianism is the test case students reason about; the objections drive most of the dialectic in 20th-century normative ethics.',
    ARRAY['classical_utilitarianism', 'mill_bentham_utilitarianism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'hedonism',
    'Hedonism',
    ARRAY['ethics'],
    'The value-theoretical view that PLEASURE is the only intrinsic good and PAIN the only intrinsic bad — every other "good" (knowledge, friendship, achievement) is derivatively valuable as a source of pleasure or absence of pain. Distinguished from PSYCHOLOGICAL hedonism (the descriptive claim that humans always pursue pleasure, contested) from ETHICAL hedonism (the normative claim that they should). Underwrites classical utilitarianism (Bentham, Mill): if pleasure is the only intrinsic good, then maximizing pleasure is the single moral imperative.',
    'Hedonism is a theory of VALUE rather than of right action — it doesn''t directly say what to do, but rather what makes outcomes good or bad. Combined with consequentialism (outcomes are what matter morally), it generates classical utilitarianism (maximize pleasure, minimize pain). Bentham''s 1789 founding hedonism was crude — pleasure and pain measured along seven dimensions including duration, intensity, propinquity, fecundity, purity. Mill''s 1861 refinement introduced the QUALITY of pleasure (the higher pleasures of intellectual and aesthetic life are different in kind from bodily pleasures, and "competent judges" — those who have experienced both — prefer the higher). The classical objections: (i) the EXPERIENCE MACHINE (Nozick 1974) — if hedonism is true, plugging into a machine producing maximal simulated pleasure should be the highest good, but most people don''t want to; pleasure isn''t enough. (ii) the CONTENT-INDIFFERENT objection — hedonism doesn''t care WHAT we take pleasure in; pleasure from cruelty seems clearly inferior to pleasure from achievement, but pure hedonism can''t distinguish them. (iii) PARETIAN concerns — hedonism is sometimes accused of leveling all welfare considerations to subjective experience, ignoring autonomy and objective goods. Modern welfare economics replaces hedonism with PREFERENTISM (well-being is preference-satisfaction), avoiding some of these objections at the cost of new ones. The bridge to philosophy of mind (P5-07a/b) on the nature of pleasure and consciousness is real; the bridge to economics on welfare is also real.',
    ARRAY['hedonistic_value_theory', 'pleasure_principle'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'deontology',
    'Deontology',
    ARRAY['ethics'],
    'The family of normative theories holding that the moral status of an action is determined by features beyond its consequences — including whether the action keeps promises, respects autonomy, refrains from using persons as mere means, fulfills duties, and respects rights. Pure deontology rejects consequence-only evaluation: an action can be wrong even when its consequences are best (because it violates rights), and right even when its consequences are not best (because it fulfills a duty). The canonical articulation is Kantian ethics; Ross''s 1930 PRIMA FACIE DUTIES is the major refinement; agent-centered restrictions (Nagel) and agent-centered options (Scheffler) are central structural concepts.',
    'Deontology is the family of normative theories that take the structure of action — what KIND of action it is — to matter morally beyond its consequences. The deontologist holds that there are agent-centered RESTRICTIONS prohibiting certain action-types (don''t lie, don''t murder, don''t use persons as mere means) that hold even when violating them would produce better consequences. Kant''s 1785 GROUNDWORK and 1788 CRITIQUE OF PRACTICAL REASON give the canonical formulation: morality is grounded in pure practical reason; the categorical imperative (in its three formulations — universal-law, humanity-as-end, kingdom-of-ends) tests maxims for moral permissibility. W.D. Ross''s 1930 THE RIGHT AND THE GOOD develops a PLURALISTIC deontology — not one master principle but seven prima facie duties (fidelity, reparation, gratitude, beneficence, non-maleficence, justice, self-improvement) which can conflict; moral judgment in particular cases requires weighing them. Modern deontologists (Nagel, Kamm, Scanlon) develop the structural distinction between agent-centered RESTRICTIONS (prohibitions on action-kinds that hold even at the cost of worse consequences) and agent-centered OPTIONS (permissions to NOT maximize good consequences when doing so would be too demanding). Classical objections: deontology can seem RIGORISTIC (Kant''s notorious example of refusing to lie even to a murderer at the door); it has trouble with CONFLICTING DUTIES (when prima facie duties clash, what trumps what?); and PURE deontology is hard to motivate without consequentialist substructure. The bridge to logic (P5-03''s deontic_logic) is real: deontology motivates the formal study of obligation, permission, and prohibition.',
    ARRAY['deontological_ethics', 'rights_based_ethics', 'duty_ethics'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'kantian_ethics',
    'Kantian Ethics',
    ARRAY['ethics'],
    'Immanuel Kant''s 1785 (GROUNDWORK OF THE METAPHYSICS OF MORALS) and 1788 (CRITIQUE OF PRACTICAL REASON) deontological theory. Morality is grounded in PURE PRACTICAL REASON — the rational structure shared by all rational agents. The CATEGORICAL IMPERATIVE is the supreme principle of morality, expressed in three classical formulations: (1) UNIVERSAL LAW — act only on maxims you could will to be universal laws; (2) HUMANITY AS END — treat humanity (in yourself or others) always as an end, never merely as a means; (3) KINGDOM OF ENDS — act as a member of a community of rational agents legislating universal laws. Kant''s ethics is rationalist (the moral law is discovered by pure reason, not experience) and universalist (the moral law applies to all rational beings without exception).',
    'Kantian ethics is the most influential deontological theory in Western philosophy. The central insight: morality is a constraint that pure practical reason imposes on rational agents — not a contingent set of cultural norms or natural facts about human flourishing, but a NECESSARY structure of rational agency itself. The categorical imperative is the principle distinguishing genuinely moral norms from merely PRUDENTIAL norms (which depend on contingent desires) and from HYPOTHETICAL imperatives (which are conditional on goals). Three classical formulations: (i) UNIVERSAL LAW — "act only according to that maxim which you can at the same time will to become a universal law". You assess a proposed action by asking: could everyone act on this maxim? If universalizing the maxim is impossible (lying-promising would destroy the institution of promising) or self-defeating, the maxim is impermissible. (ii) HUMANITY AS END — "act so as to treat humanity, in yourself and in others, always as an end and never merely as a means". Persons have intrinsic dignity (Würde) — they cannot be used merely instrumentally for someone else''s purposes. (iii) KINGDOM OF ENDS — act as if you were legislating universal laws for a kingdom of rational agents. Kantian ethics is RIGORISTIC — it allegedly forbids lying even to a murderer at the door. Modern Kantians (Korsgaard 1996, Hill, O''Neill) defend more flexible Kantian deontologies that allow context-sensitivity without abandoning the categorical-imperative structure. The cross-bridge to philosophy of mind (P5-07a) on practical rationality and to political philosophy (P5-05) on autonomy and dignity is real.',
    ARRAY['kantianism', 'kantian_deontology'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'categorical_imperative',
    'Categorical Imperative',
    ARRAY['ethics'],
    'Immanuel Kant''s supreme principle of morality, distinguishing genuinely moral commands (which apply unconditionally to rational agents) from hypothetical imperatives (conditional on contingent desires). Three classical formulations in the GROUNDWORK: (1) Universal Law — act only on maxims you could will to be universal laws; (2) Humanity as End — treat humanity always as an end, never merely as a means; (3) Kingdom of Ends — act as a member of a community of rational agents legislating universal laws. Kant claimed the three formulations are equivalent (all three give the same verdicts on test cases), though commentators dispute whether they actually are.',
    'The categorical imperative is Kant''s response to the metaethical challenge of grounding morality. A HYPOTHETICAL imperative says "if you want X, do Y" — its force depends on the contingent end. The categorical imperative is unconditioned: "do Y" full stop, applying to all rational agents regardless of contingent desires. Three classical formulations test maxims: (1) UNIVERSAL LAW formulation. Test: could the maxim be willed as a universal law? Examples: lying-to-extract-money fails because if everyone did it, the institution of trustworthy speech would dissolve, making the maxim self-defeating. Suicide-from-self-love fails because the very faculty (self-love) instructed to terminate life is the one whose sustenance is its function, generating contradiction. (2) HUMANITY-AS-END formulation. Test: does the action treat persons as ends with intrinsic dignity, or merely as means to one''s purposes? Examples: lying treats the deceived person as a means (to one''s own end) rather than as a rational agent capable of consenting to the relationship. Coercion treats the coerced as a means (to one''s purposes) rather than as an autonomous chooser. (3) KINGDOM OF ENDS formulation. Test: would I legislate this maxim as a member of a community of rational agents legislating universal laws? Together these formulations test moral permissibility. The categorical imperative is the engine of Kantian moral judgment; the three formulations are the testing apparatus. The three are claimed equivalent but, on examination, give modestly different verdicts on edge cases — Korsgaard 1996 gives a unified Kantian theory that resolves the tensions. The bridge to logic (P5-03''s deontic_logic and conditional logic) is real: the categorical imperative is a NORMATIVE LOGIC, distinguishing valid from invalid moral inferences.',
    ARRAY['ci', 'kant_supreme_principle'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'virtue_ethics',
    'Virtue Ethics',
    ARRAY['ethics'],
    'The family of normative theories holding that the central question of ethics is not "what should I DO?" but "what should I BE?" — what character traits (virtues) should I cultivate? The right action is what the virtuous person would do; the foundational question is virtue and its cultivation. Aristotelian eudaimonism is the canonical version (NICOMACHEAN ETHICS, c. 350 BCE); revived in 20th-century philosophy by Anscombe (1958, "Modern Moral Philosophy"), Foot, MacIntyre (1981, AFTER VIRTUE), Hursthouse (1999, ON VIRTUE ETHICS). Distinguished from consequentialism (which evaluates actions by outcomes) and deontology (which evaluates actions by features intrinsic to action) by its focus on the agent''s CHARACTER as the primary locus of moral evaluation.',
    'Virtue ethics shifts the central question from "what should I do?" (the action-focus shared by consequentialism and deontology) to "what kind of person should I be?" (the character-focus). The right action is what the virtuous person would do; understanding right action requires first understanding virtue and its cultivation. Aristotle''s NICOMACHEAN ETHICS gives the canonical version: virtues are STABLE DISPOSITIONS to act, feel, and judge well; they''re cultivated through habituation (you become courageous by performing courageous acts in the right circumstances, not by reading about courage); the unity of virtue thesis (the virtues hang together; you can''t fully have one without the others); eudaimonia (human flourishing) is the highest good, and virtues are the constitutive components of eudaimonia, not mere instruments to it. Anscombe''s 1958 "Modern Moral Philosophy" launched the contemporary revival, charging that modern ethics had stripped morality of its substantive content (DUTY without divine command becomes empty; obligation without an end-of-flourishing becomes arbitrary). MacIntyre''s 1981 AFTER VIRTUE develops a historicist virtue ethics (virtues are practice-dependent, traditions of moral inquiry are required for ethical thought). Hursthouse 1999 develops a neo-Aristotelian naturalism (virtues track features of human nature; eudaimonia is the human good). Classical objections: SITUATIONIST critics (Doris 2002) argue empirical psychology shows people don''t HAVE stable character traits — what looks like courage is actually situation-dependent. Action-guidance critics charge virtue ethics gives no clear guidance in HARD cases (what does the virtuous person do?). Defenders respond that practical wisdom (phronesis) is irreducible to algorithm and that situationist data have been overstated.',
    ARRAY['aretaic_ethics', 'character_ethics', 'aristotelian_ethics'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'eudaimonia',
    'Eudaimonia',
    ARRAY['ethics'],
    'Aristotle''s conception of human flourishing — the highest human good, the activity in accordance with virtue characteristic of human life. Translated variously as "happiness", "flourishing", "well-being", "the good life" — though all translations are imperfect because eudaimonia is not a subjective state (mere satisfaction or pleasure) but an OBJECTIVE achievement of living well as a human being. Constituted by the virtues rather than caused by them; the virtuous activity IS the flourishing. The central concept of Aristotelian and neo-Aristotelian virtue ethics.',
    'Eudaimonia (εὐδαιμονία) is Aristotle''s term for the highest human good. Crucially it is NOT happiness in the modern subjective sense (a feeling of pleasure or satisfaction). It is an OBJECTIVE achievement — living well as a human being, fulfilling the human function (ergon) of rational activity in accordance with virtue. Aristotle''s argument in NICOMACHEAN ETHICS Book I: every human pursues some good; some goods are pursued for their own sake AND for the sake of further goods (wealth, health); some are pursued only for their own sake; the supreme good must be pursued only for its own sake AND be self-sufficient (lacking nothing). That good is eudaimonia. The function (ergon) argument: every kind of thing has a function; the function of a human being is rational activity; doing this WELL — i.e., in accordance with virtue — constitutes eudaimonia. Eudaimonia is constitutive of, not caused by, virtuous activity — the virtuous activity IS the flourishing, not its means. This distinguishes Aristotle from instrumental conceptions of virtue (where virtue is a means to a separate good like pleasure or external rewards). Modern translations: "flourishing" captures the objective character better than "happiness" but still imperfectly; "the good life" is colloquial but loses the philosophical weight. Hursthouse 1999 develops a NATURALIST eudaimonism: eudaimonia for humans tracks species-typical functioning, parallel to flourishing for non-human animals. Critics charge eudaimonism is too thick (presupposing a substantive theory of human nature) or too thin (eudaimonia for whom — individual versus communal flourishing?). The bridge to philosophy of mind (P5-07a) on rational activity and consciousness, and to political philosophy (P5-05) on the social conditions for flourishing, is real.',
    ARRAY['flourishing', 'aristotelian_happiness', 'human_good'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'practical_wisdom',
    'Practical Wisdom',
    ARRAY['ethics'],
    'Aristotelian phronesis (φρόνησις) — the intellectual virtue of judging well in particular circumstances about what to do. Distinguished from theoretical wisdom (sophia, which concerns universal truths), technical skill (techne, which concerns making), and clever calculation (deinotes, which can be used for bad ends). Practical wisdom is THE master virtue in Aristotelian ethics: without it, the moral virtues (courage, temperance, justice) cannot be properly exercised, since they require judgment about what the present circumstance calls for. Action-guidance in virtue ethics depends crucially on practical wisdom rather than rule-application.',
    'Practical wisdom is Aristotle''s answer to a question that troubles every normative theory: how do general moral principles apply to particular cases? Theoretical knowledge (sophia) concerns necessary universal truths; technical skill (techne) concerns making things well according to a recipe; CLEVER CALCULATION (deinotes) is the bare ability to figure out means to ends, which can serve good or evil ends equally. Practical wisdom is distinct from all of these: the capacity to perceive in a particular situation what the situation morally calls for, and to act accordingly. It cannot be reduced to algorithm — Aristotle is explicit that ethical judgment in particulars cannot be codified into universal rules without remainder. Three central features: (i) PERCEPTION — phronesis sees the relevant moral features of a situation, distinguishing what matters from what doesn''t; (ii) DELIBERATION — phronesis weighs competing considerations and decides what to do; (iii) DESIRE-INTEGRATION — phronesis is connected to right desire (orexis), so the wise agent not only sees what to do but is moved to do it. Modern virtue ethicists (McDowell 1979, Nussbaum 1990) emphasize the IRREDUCIBILITY of practical wisdom to algorithm. The cross-bridge to moral_particularism is real — both deny that ethical principle alone settles practical questions, and both privilege judgment in particulars over rule-application. The cross-bridge to philosophy of mind (P5-07a) on practical rationality and the structure of reasoning is also real.',
    ARRAY['phronesis', 'prudence_aristotelian'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'contractualism',
    'Contractualism',
    ARRAY['ethics'],
    'T.M. Scanlon''s 1998 (WHAT WE OWE TO EACH OTHER) normative theory: an action is wrong if it would be disallowed by any principle that no one could reasonably reject as a basis for general informed agreement. Distinguished from social contract theories of POLITICAL legitimacy (Hobbes, Locke, Rousseau, Rawls), though continuous with them. Contractualism is a moral theory grounding right action in what principles agents could justify to one another; the moral motivation is the desire to be ABLE TO JUSTIFY one''s actions to those affected. Compatible with realism about moral facts; contractualism is a theory of what makes actions wrong, not a metaethical theory of what moral facts are.',
    'Scanlon''s contractualism (WHAT WE OWE TO EACH OTHER, 1998) gives an account of WRONGNESS in terms of justifiability to those affected. The central formula: "an act is wrong if its performance under the circumstances would be disallowed by any principle for the general regulation of behavior that no one could reasonably reject as a basis for informed, unforced general agreement". The moral motivation is the desire to live with others on terms that none of them could reasonably reject — to be able to JUSTIFY one''s actions to all those affected. This grounds rights (you wrong me when you act on a principle I could reasonably reject) and duties (you owe me actions that are justifiable to me). Distinguished from the SOCIAL CONTRACT TRADITION (Hobbes, Locke, Rousseau, Rawls) of political philosophy — that tradition explains political legitimacy in terms of hypothetical agreement; contractualism extends a related structure to interpersonal moral obligation. Scanlon''s contractualism makes the AGGREGATION PROBLEM central: in trolley-style cases, contractualism asks "is there ANY person who could reasonably reject the principle?" rather than "do the numbers work out?". This blocks some utilitarian conclusions (you can''t kill one to save five just because the numbers favor it — the one could reasonably reject) while accommodating others (you can save the many when the few are merely inconvenienced rather than killed). Critics charge contractualism is parasitic on prior moral facts (what counts as REASONABLY rejecting requires a prior moral judgment about reasonableness); defenders respond that this is a feature, not a bug — moral theory should be reflective rather than reductive. The bridge to political philosophy (P5-05) is direct.',
    ARRAY['scanlonian_contractualism', 'what_we_owe_to_each_other'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'divine_command_theory',
    'Divine Command Theory',
    ARRAY['ethics'],
    'The normative theory that moral truths are grounded in God''s commands — what is right is what God commands; what is wrong is what God forbids. Defended in Christian philosophy (William of Ockham, Robert Adams 1999 FINITE AND INFINITE GOODS), Islamic Asharite theology (the right is whatever God''s law decrees), and Jewish philosophical tradition (in tension with Maimonidean rationalism). The CENTRAL CHALLENGE is the EUTHYPHRO DILEMMA from Plato''s dialogue of that name: is what is right right BECAUSE God commands it, or does God command it because it is right? The first horn makes morality arbitrary; the second makes morality independent of God.',
    'Divine command theory grounds normative truth in God''s will. Several versions: (i) UNRESTRICTED DCT — every moral truth depends on God''s actual or counterfactual commands; even logical and mathematical truths might depend on divine will. (ii) MODIFIED DCT (Adams 1999) — God''s commands constitute moral obligations specifically; the GOOD is grounded in God''s nature (rather than commands), and what God commands aligns with the good. (iii) NATURAL LAW theology (Aquinas, Finnis) — moral truths are part of God''s creation; we discover them through natural reason, not through specific revelation. The EUTHYPHRO DILEMMA (Plato''s EUTHYPHRO, 10a) is the persistent challenge: when Socrates asks whether the pious is loved by the gods because it is pious or pious because it is loved by the gods, he forces a choice. (a) If God''s commands MAKE actions right, morality is arbitrary — God could have commanded torture and that would make torture right. (b) If God commands actions because they are right, morality is INDEPENDENT of God — God''s commands track an antecedent moral order. Modern divine command theorists (Adams) attempt to escape the dilemma by grounding the GOOD in God''s nature (not commands) while grounding OBLIGATIONS in God''s commands; the moral law is then non-arbitrary (because God''s nature is necessarily good) but properly grounded in divinity. Secular critics challenge whether DCT is coherent at all without theological foundations; the cross-bridge to philosophy of religion is real but P5-04a treats DCT as a normative-theory option among others, with assumptions about theism remaining outside the seed.',
    ARRAY['dct', 'theological_voluntarism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'ethical_egoism',
    'Ethical Egoism',
    ARRAY['ethics'],
    'The normative theory that the right action for an agent is the one that maximizes the agent''s OWN long-term self-interest. Distinguished from PSYCHOLOGICAL egoism (the descriptive claim that humans always do pursue self-interest, contested) from ETHICAL egoism (the normative claim that we should). Defended in various forms by Ayn Rand (RATIONAL SELFISHNESS), some interpretations of Hobbes (where prudential rationality grounds morality), and contemporary egoists (Brink''s 1989 limited defense in MORAL REALISM). Distinct from MORAL EGOISM that licenses harmful action toward others; many ethical egoists hold that pursuing one''s own long-term interest reliably tracks cooperative behavior.',
    'Ethical egoism makes the agent''s own self-interest the foundation of moral evaluation: the right action for me is the one that maximizes MY long-term welfare. Distinguished from PSYCHOLOGICAL egoism (the empirical claim that humans always do pursue self-interest — contested by altruistic behavior) — the descriptive does not entail the normative. Distinguished also from MORAL EGOISM that endorses harmful action toward others when convenient — most sophisticated ethical egoists hold that the agent''s genuine long-term interest reliably tracks cooperative, honest, friendship-respecting behavior, since trust and cooperation are the foundation of long-term well-being. Defenses of ethical egoism: (i) AGENT-RELATIVITY — moral reasons are agent-relative; my reasons attach to MY ends, your reasons to YOUR ends; egoism is just the consistent application of this. (ii) RATIONAL-CHOICE foundations — what counts as "rational" is maximizing one''s OWN ends; the moral question collapses into the prudential question. (iii) HOBBESIAN reduction — morality is a coordination convention rational self-interested agents adopt for mutual benefit; "morality" reduces to enlightened self-interest. Classical objections: (a) the COUNTEREXAMPLE of clear other-regarding obligations (saving a drowning stranger when no one will know — most people judge this morally required, but pure egoism cannot account for it); (b) the SELF-DEFEATING charge (Parfit 1984) — pure egoists would publish their egoism, undermining the cooperative trust that egoism depends on; (c) the IMPARTIALITY objection — morality seems to demand impartial concern, which egoism explicitly rejects. Ethical egoism remains a minority normative theory; it is included here because it''s a major dialectical option in normative-theory taxonomies.',
    ARRAY['rational_egoism', 'egoism_ethics'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'moral_particularism',
    'Moral Particularism',
    ARRAY['ethics'],
    'Jonathan Dancy''s 1993 / 2004 view (MORAL REASONS; ETHICS WITHOUT PRINCIPLES) that there are no exceptionless moral principles; moral judgment in particular cases is irreducible to rule-application. The same feature that counts in favor of an action in one case can count AGAINST that action in another case (HOLISM about moral reasons). Particularism is the rejection of PRINCIPLISM — the view that moral knowledge consists in knowing principles and that moral judgment is principle-application. Compatible with realism about moral facts (the facts exist, just not in the form of exceptionless principles).',
    'Particularism is the systematic rejection of moral principlism. The classical principlist view holds that moral knowledge consists in knowing principles ("don''t lie", "keep promises", "minimize suffering"), and moral judgment is principle-application: identify the relevant principles, apply them to the case, get a verdict. Dancy''s 1993 MORAL REASONS challenges this: many moral features behave HOLISTICALLY — the same feature can count in favor of an action in one context and against it in another. EXAMPLES: the fact that an action causes pleasure usually counts in favor, but the fact that an action causes the SADIST pleasure counts against. The fact that an action is requested usually counts in favor, but the fact that an action was requested by a lying manipulator counts against. The same FEATURE has opposite valences in different contexts. If this is right, moral principles can''t be exceptionless: there''s no formula "pleasure is always good" — pleasure''s contribution to moral evaluation depends on context. Dancy''s 2004 ETHICS WITHOUT PRINCIPLES extends and refines: moral judgment is more like aesthetic judgment than mathematical proof — it requires the perception of relevant features in particular situations, with no exception-free formula available. Particularism is the natural ally of virtue ethics (which privileges practical wisdom over rule-application) and of some moral realisms (the moral facts exist, but they''re fact-particular rather than principle-shaped). Critics charge that particularism makes moral KNOWLEDGE TRANSMISSION impossible (we can''t teach moral judgment without principles to teach) and renders moral judgment irrationally case-by-case. Dancy responds: principles aren''t needed to explain how transmission works; we transfer moral skill through case-based learning, the way we transfer aesthetic taste.',
    ARRAY['dancy_particularism', 'anti_principlism'],
    'INTERPRETED',
    'ai-seed',
    7
  ),
  (
    'supererogation',
    'Supererogation',
    ARRAY['ethics'],
    'The category of morally PRAISEWORTHY actions that go beyond what is morally REQUIRED — actions that are good but not obligatory, going "above and beyond the call of duty". Examples include heroic self-sacrifice, very large charitable donations, extreme acts of forgiveness. The category requires a normative theory to distinguish (i) the morally OBLIGATORY (what we must do, failure of which is wrong), (ii) the morally PERMISSIBLE (what we may do, neither required nor forbidden), and (iii) the morally SUPEREROGATORY (what we may do that exceeds requirement, the omission of which is permissible but the performance of which is praiseworthy). Some normative theories struggle to accommodate supererogation; consequentialism is the canonical example.',
    'Supererogation is the structural test for normative theories: does the theory have CONCEPTUAL SPACE for the morally praiseworthy-but-not-required? Three categories must be distinguished: (a) OBLIGATORY actions — those that must be performed; failure to perform them is wrong (paying one''s debts; refraining from murder). (b) PERMISSIBLE actions — those that may but need not be performed; either performing or omitting is fine (eating chocolate; reading a novel). (c) SUPEREROGATORY actions — those that go BEYOND what is required; performing them is praiseworthy (heroic self-sacrifice; very generous charity), but failing to perform them is permissible — you''re not blameworthy for not being a hero. The conceptual space for supererogation requires that "above-and-beyond" actions exist and are real. CONSEQUENTIALISM struggles: if the right action is the one with best consequences, every action that produces more good is OBLIGATORY (not supererogatory) — you''re always required to maximize, leaving no space for "permissible to do less". This is the DEMANDINGNESS OBJECTION (Williams 1973, Singer 1972) — pure consequentialism appears to demand always-maximizing, hence has no space for supererogation. DEONTOLOGY handles supererogation more naturally: there are agent-centered restrictions on action-types; outside those restrictions, you may but need not do whatever maximizes good. VIRTUE ETHICS handles it through character: the heroic agent has gone beyond what virtue demands of an ordinary agent, and we praise excess virtue without requiring it. The ethics of supererogation is itself a substantial topic (Wolf 1982, Heyd 1982, Archer 2018). For Phase 5, supererogation serves as the structural concept that lets students see how each normative theory handles "above and beyond"; pedagogically, it''s a productive lens for theory-comparison.',
    ARRAY['supererogatory', 'beyond_duty'],
    'INTERPRETED',
    'ai-seed',
    7
  );

-- Edges: 34 INSERTs, all pedagogical_prerequisite, all within-domain.
-- Foundation tier (2): morality → metaethics; morality → normative_ethics.
-- Metaethics structure (4): metaethics → moral_realism; metaethics →
--   moral_anti_realism; metaethics → moral_epistemology; metaethics →
--   is_ought_distinction.
-- Within metaethics (11): moral_anti_realism → error_theory; moral_anti_
--   realism → expressivism; moral_realism → moral_naturalism; moral_realism
--   → moral_non_naturalism; moral_realism → moral_epistemology; moral_
--   naturalism → open_question_argument; is_ought_distinction → moral_
--   naturalism; is_ought_distinction → error_theory; moral_epistemology →
--   motivational_internalism; motivational_internalism → motivational_
--   externalism; motivational_internalism → expressivism.
-- Normative umbrellas (7): normative_ethics → consequentialism;
--   normative_ethics → deontology; normative_ethics → virtue_ethics;
--   normative_ethics → contractualism; normative_ethics → ethical_egoism;
--   normative_ethics → divine_command_theory; normative_ethics →
--   moral_particularism.
-- Within consequentialism (2): consequentialism → utilitarianism;
--   utilitarianism → hedonism.
-- Within deontology (2): deontology → kantian_ethics; kantian_ethics →
--   categorical_imperative.
-- Within virtue ethics (3): virtue_ethics → eudaimonia; virtue_ethics →
--   practical_wisdom; virtue_ethics → moral_particularism.
-- Supererogation (3): normative_ethics → supererogation; deontology →
--   supererogation; consequentialism → supererogation.

INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  ('morality', 'metaethics', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('morality', 'normative_ethics', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('metaethics', 'moral_realism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('metaethics', 'moral_anti_realism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('metaethics', 'moral_epistemology', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('metaethics', 'is_ought_distinction', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_anti_realism', 'error_theory', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_anti_realism', 'expressivism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_realism', 'moral_naturalism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_realism', 'moral_non_naturalism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_realism', 'moral_epistemology', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_naturalism', 'open_question_argument', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('is_ought_distinction', 'moral_naturalism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('is_ought_distinction', 'error_theory', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('moral_epistemology', 'motivational_internalism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('motivational_internalism', 'motivational_externalism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('motivational_internalism', 'expressivism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'consequentialism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'deontology', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'virtue_ethics', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'contractualism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'ethical_egoism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'divine_command_theory', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'moral_particularism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('consequentialism', 'utilitarianism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('utilitarianism', 'hedonism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('deontology', 'kantian_ethics', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('kantian_ethics', 'categorical_imperative', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('virtue_ethics', 'eudaimonia', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('virtue_ethics', 'practical_wisdom', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('virtue_ethics', 'moral_particularism', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('normative_ethics', 'supererogation', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('deontology', 'supererogation', 'pedagogical_prerequisite', 'ai-seed', 7),
  ('consequentialism', 'supererogation', 'pedagogical_prerequisite', 'ai-seed', 7);

COMMIT;
