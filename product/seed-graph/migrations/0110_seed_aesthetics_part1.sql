-- Migration: 0110_seed_aesthetics_part1
-- Purpose: Tenth Phase 5 seed migration (first aesthetics file) —
--   foundational aesthetics concepts and within-domain
--   pedagogical_prerequisite edges. Authored in S-0068 against task
--   P5-06 "Aesthetics seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the core aesthetics inventory per phase_5.md T1-B as a
--   single (not pre-split) task: foundation; theories of art;
--   aesthetic value and taste; Kantian aesthetics; representation
--   and meaning; ontology of artworks; criticism and interpretation.
--   Cross-domain bridges (aesthetics ↔ ethics, philosophy of language,
--   philosophy of mind, metaphysics) are P5-11's exclusive surface and
--   are deliberately excluded from this file.
-- Loads tables: public.nodes (27 INSERTs), public.edges (32 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 10 -> 11).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 10 at session boot (post-S-0066 per
--     ROUTING.md narrative — most recent applied seed at this prefix
--     range was 0040_seed_mind_part1.sql which wrote 10).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 11 (the
--     post-increment value).
--   * No prior migrations under prefix 0110-0119; this is the first
--     aesthetics seed file. Sub-range slots 0111-0119 left reserved.
--   * P5-01a epistemology-core seed applied (0011). No edge in this
--     migration references epistemology nodes — aesthetics is greenfield
--     within its own subdomain at this seed step; cross-domain bridges
--     land at P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 27 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'aesthetics'}, status=active, graph_version_added=11.
--   * 32 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=11. All edges are
--     within-domain (source and target both tagged aesthetics);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 11.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 11 AND 'aesthetics' = ANY(domain) :: 27
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 11 AND edge_type = 'pedagogical_prerequisite' :: 32
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 11
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts (no edges into pre-existing nodes; aesthetics is
--     greenfield within its own subdomain).
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is a DAG rooted at aesthetics; every concept
--     introduced here is reachable from aesthetics via at most three
--     edges; validate.py's Kosaraju SCC check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: aesthetic_judgment and
--     kantian_aesthetic_judgment bridge to ethics (P5-04a on moral
--     judgment; the judgment-of-taste vs. moral-judgment analogy
--     central to Kant's third Critique); expression_theory_art and
--     expression_in_art bridge to philosophy of mind (P5-07a/b on
--     intentionality and mental content — expression is a species of
--     intentional content); metaphor bridges to philosophy of language
--     (P5-08 on figurative meaning, Davidson's "What Metaphors Mean",
--     Black's interaction theory); pictorial_representation bridges to
--     philosophy of language (P5-08 on Goodman's symbol-systems
--     framework for both linguistic and pictorial reference);
--     fictional_truth bridges to metaphysics (P5-02b on modal realism,
--     Lewis's counterfactual analysis) and to philosophy of language
--     (P5-08 on fictionalism, the Walton make-believe theory's
--     pragmatic-semantic implications); type_token_artworks_distinction
--     bridges to metaphysics (P5-02b on universals, types, abstract
--     objects — musical works as the canonical philosophical case of
--     abstract artifact). Wait for P5-11's cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the aesthetics sub-ranges (0111-0119). Those slots
--     remain reserved for future aesthetics extension if Phase 6+
--     telemetry warrants additional concepts (e.g., environmental
--     aesthetics, everyday aesthetics, philosophy of dance, philosophy
--     of literature, philosophy of film, evolutionary aesthetics, the
--     aesthetics of nature beyond the sublime). This seed completes
--     P5-06's task at the granularity principle within the 0110 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 27/27 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference's entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here
--     is well-named in the SEP/IEP entry inventory and corresponds to a
--     concept the contemporary analytic aesthetics literature (Plato,
--     Aristotle, Hume, Burke, Kant, Schopenhauer, Tolstoy, Bell, Fry,
--     Collingwood, Wimsatt, Beardsley, Goodman, Wollheim, Dickie,
--     Levinson, Walton, Lewis, Wolterstorff, Davies, Robinson, Hirsch,
--     Stecker, Stolnitz, Black, Davidson) explicitly names. Mirrors the
--     nine prior Phase 5 subject seeds' distributions.
--   * domain[] cardinality: every node carries exactly one tag,
--     'aesthetics'. Multiple cross-domain reaches exist (see
--     Non-responsibilities above) but per phase_5.md T2-G #4
--     (domain-tag cardinality explosions vector), cross-domain tagging
--     belongs to P5-11. The canonical home for each of these concepts
--     in the analytic literature is aesthetics, so the single tag is
--     correct here.
--   * provenance: 'ai-seed' for every node and edge. Same as
--     P5-01a/b, P5-02a/b, P5-03, P5-04a/b, P5-05, P5-07a.
--   * Node selection rationale: 27 concepts cover seven core aesthetics
--     clusters at the granularity principle: (1) foundation (4)
--     [aesthetics, aesthetic_experience, aesthetic_property,
--     aesthetic_judgment] — the field umbrella plus the three central
--     explananda (the experience, the properties, the judgments); (2)
--     definition of art (6) [art, imitation_theory_art,
--     expression_theory_art, formalism_artistic,
--     institutional_theory_of_art, historical_theory_of_art] — the
--     "what is art?" question and the five canonical analytic answers
--     in historical-systematic sequence (mimesis from Plato/Aristotle,
--     expression from Tolstoy/Collingwood, formalism from Bell/Fry,
--     institutional from Dickie 1974, historical from Levinson 1979);
--     (3) aesthetic value & taste (4) [aesthetic_value, taste_aesthetic,
--     aesthetic_disinterest, sublime] — what aesthetic value is, the
--     standard-of-taste tradition (Hume 1757), the disinterest
--     condition that distinguishes aesthetic from practical attention
--     (Kant 1790, Schopenhauer, Stolnitz), and the sublime as the
--     aesthetic mode complementary to beauty (Burke 1757, Kant 1790);
--     (4) Kantian aesthetics (2) [kantian_aesthetic_judgment,
--     free_play_imagination_understanding] — Kant's analysis of the
--     judgment of taste and the transcendental free-play apparatus that
--     grounds it in the harmonious cooperation of imagination and
--     understanding; (5) representation & meaning (4)
--     [pictorial_representation, depiction, expression_in_art,
--     metaphor] — Goodman's resemblance-vs-convention dispute on
--     pictures, Wollheim's seeing-in account of depiction, expression
--     as a property of artworks (distinct from the expression theory
--     of what art IS), and metaphor as the bridging non-literal
--     phenomenon between aesthetics and philosophy of language; (6)
--     ontology of artworks (4) [ontology_of_artworks,
--     type_token_artworks_distinction, fictional_truth,
--     ontology_musical_works] — the field, the type-token framework
--     (musical works as types), Walton's make-believe account of
--     fictional truth, and the canonical case of musical work ontology
--     (Goodman, Levinson, Wolterstorff); (7) criticism & interpretation
--     (3) [art_criticism, intentionalism_artistic, anti_intentionalism]
--     — the practice and the two opposed positions on whether artist's
--     intentions determine work's meaning (intentionalism per Hirsch,
--     Levinson actual-intentionalism, Stecker hypothetical-intentionalism;
--     anti-intentionalism per the Wimsatt-Beardsley intentional fallacy
--     of 1946). Excluded deliberately and reserved for the 0111-0119
--     sub-range or Phase 6+: environmental aesthetics, everyday
--     aesthetics, philosophy of dance, philosophy of literature,
--     philosophy of film, evolutionary aesthetics, the aesthetics of
--     nature beyond the sublime, ugliness as aesthetic category,
--     aesthetic emotion, aesthetic cognitivism, the autonomy of art,
--     conceptual art and post-Duchamp ontology, performance art,
--     aesthetic testimony.
--   * Edge structure: 32 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation spine flows aesthetics → six T1
--     branches (aesthetic_experience, aesthetic_property,
--     aesthetic_judgment, art, ontology_of_artworks, art_criticism).
--     The aesthetic value/judgment branch elaborates aesthetic_judgment
--     → taste_aesthetic / kantian_aesthetic_judgment / sublime, with
--     taste_aesthetic → kantian_aesthetic_judgment encoding the
--     Hume-to-Kant historical-systematic sequence (Hume's standard-of-
--     taste question informs Kant's transcendental answer);
--     kantian_aesthetic_judgment → aesthetic_disinterest /
--     free_play_imagination_understanding encodes Kant's analysis;
--     aesthetic_experience → aesthetic_disinterest captures the
--     Stolnitz-style attitudinal account of aesthetic experience as
--     disinterested attention. The art-definition branch is a fan-out
--     from art to the five theories. The representation branch:
--     art → pictorial_representation → depiction (Wollheim's seeing-in);
--     expression_theory_art → expression_in_art → metaphor (the
--     Goodman-Davidson-Black sequence linking expression as a property
--     of artworks to figurative meaning). The ontology branch:
--     ontology_of_artworks → type_token_artworks_distinction /
--     fictional_truth, with type_token_artworks_distinction →
--     ontology_musical_works (musical works as the canonical case).
--     The criticism branch: art_criticism → intentionalism_artistic /
--     anti_intentionalism, with anti_intentionalism →
--     intentionalism_artistic encoding the historical sequence (the
--     Wimsatt-Beardsley anti-intentionalist position is the target
--     contemporary intentionalism responds to). Cross-cluster
--     within-aesthetics bridges: aesthetic_experience →
--     expression_theory_art (expression theory grounds art in emotional
--     engagement, presupposing aesthetic experience); aesthetic_property
--     → formalism_artistic (formalism's "significant form" IS an
--     aesthetic property); fictional_truth → metaphor (both are
--     non-literal-truth phenomena on the Walton/Lewis side; the Walton
--     make-believe apparatus provides the entry point for theorizing
--     metaphorical content alongside fictional content).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 11; DELETE FROM public.nodes WHERE id IN (the 27 ids inserted
--   here); UPDATE public.settings SET value = '10'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 60 statements
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
--   product/seed-graph/migrations/0040_seed_mind_part1.sql
--   (P5-07a philosophy-of-mind core seed; immediate predecessor at
--   graph_version 10);
--   product/seed-graph/migrations/0100_seed_political_philosophy_part1.sql
--   (P5-05 political-philosophy seed; same single-task shape);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 10 at session boot (post-S-0066 state per ROUTING.md
-- narrative); write 11 here; every node/edge below carries
-- graph_version_added = 11.
UPDATE public.settings
  SET value = '11'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 27 INSERTs covering the seven core aesthetics clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'aesthetics',
    'Aesthetics',
    ARRAY['aesthetics'],
    'The branch of philosophy concerned with the nature of aesthetic experience, aesthetic properties (beauty, sublimity, gracefulness, elegance), aesthetic judgment, the definition and ontology of art, and the practice of art criticism and interpretation. Sits at the intersection of value theory, philosophy of mind, philosophy of language, and metaphysics; its central questions concern what aesthetic value is, what makes something a work of art, what the appropriate response to art is, and what role intention and convention play in fixing artistic meaning.',
    'Frame aesthetics as a domain unified less by a shared object than by a family of questions about aesthetic phenomena: experiences, properties, judgments, the artworks that elicit them, and the criticism that articulates them. Two structural caveats students conflate: (1) "aesthetics" in the broad sense covers BOTH natural and artistic aesthetic phenomena (Burke''s and Kant''s sublime is paradigmatically natural; not all aesthetic experience is aesthetic experience OF art); (2) "aesthetics" in the narrow sense is sometimes used as a synonym for philosophy of art, foregrounding the artwork as the paradigm bearer of aesthetic properties. The contemporary analytic version traces from Hume 1757 ("Of the Standard of Taste") and Kant 1790 (Critique of the Power of Judgment) through Bell, Collingwood, Wimsatt-Beardsley, Goodman, Wollheim, Dickie, Walton, and Levinson; treat it as a domain whose progress depends on holding the experience-properties-judgment-artwork-criticism cycle in view simultaneously.',
    ARRAY['philosophy_of_art', 'philosophy_aesthetics'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'aesthetic_experience',
    'Aesthetic Experience',
    ARRAY['aesthetics'],
    'The distinctive mode of perceptual and reflective engagement characteristic of attending to aesthetic objects (artworks, natural scenes, designed environments) under the aspect of their aesthetic properties. Variously analyzed as disinterested contemplation (Kant, Schopenhauer, Stolnitz), absorbed attention (Beardsley), the disclosure of significant form (Bell), make-believe participation (Walton), or the perception of expressive properties (Goodman, Davies). The unity of the category — whether aesthetic experiences share a single distinctive phenomenal or functional character — is itself contested.',
    'Distinguish three uses students conflate: (1) the phenomenon — what it is like to attend to a sunset, a Bach fugue, a Vermeer; (2) the philosophical posit — whatever it is that aesthetic theories invoke as the distinctive form of engagement aesthetic objects elicit; (3) the criterion — aesthetic experience as a mark of the aesthetic, used to define art (Beardsley) or aesthetic value (Stolnitz, Iseminger). The disunity worry is live: contemporary critics (Dickie 1965 against Beardsley, Carroll against the "aesthetic attitude" tradition) argue that no single phenomenal or functional feature unifies the diverse engagements lumped under "aesthetic experience". Pedagogically, treat aesthetic experience as a working category whose contours theorists draw differently rather than a settled natural kind.',
    ARRAY['aesthetic_attitude', 'aesthetic_engagement'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'aesthetic_property',
    'Aesthetic Property',
    ARRAY['aesthetics'],
    'A property of an object (work of art, natural scene, performance, designed artifact) attributed in aesthetic discourse — paradigmatically beauty, ugliness, gracefulness, elegance, balance, harmony, sublimity, kitsch, garishness, dynamism, serenity. Aesthetic properties are typically held to depend on but not reduce to non-aesthetic perceptual properties (a painting''s gracefulness depends on its lines, colors, composition without being identical to any of them); their epistemology runs through perceptual judgment by competent observers; their realism (do they exist independently of observers?) is a central metaethical-style debate within aesthetics.',
    'Use the realism question as the entry point. Contemporary aesthetic-property realists (Sibley 1959, "Aesthetic Concepts") argue aesthetic properties are real but require taste to perceive — competent observers reliably converge on attributions in the way they converge on shape attributions, but there is no rule-governed inference from non-aesthetic features. Anti-realists (response-dependence theorists, projectivists) argue aesthetic properties are constituted by or projected from observer responses. The supervenience question — aesthetic properties supervene on non-aesthetic properties (no aesthetic difference without a non-aesthetic difference) — is widely accepted; the reduction question (can aesthetic properties be DEFINED in non-aesthetic terms?) is widely rejected per Sibley. The standard taxonomy distinguishes broad evaluative aesthetic properties (beauty, ugliness) from substantive aesthetic properties (graceful, garish, balanced, dynamic).',
    ARRAY['aesthetic_quality', 'aesthetic_concept'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'aesthetic_judgment',
    'Aesthetic Judgment',
    ARRAY['aesthetics'],
    'A judgment attributing an aesthetic property to an object or evaluating it under an aesthetic concept ("the sonata is graceful", "the building is overwrought"). Distinct from descriptive judgments by its evaluative dimension and from moral judgments by its non-prudential, non-deontic character. Kant''s third Critique (1790) made aesthetic judgment philosophically central: judgments of taste claim universal validity (they purport to bind every judger) without resting on conceptual rules — the puzzle that drives the transcendental analysis.',
    'Frame aesthetic judgment by its peculiar combination of features Kant identified: subjective (grounded in the judger''s feeling of pleasure or displeasure), yet purportedly universal (the judger demands agreement from all); singular (about THIS object); non-conceptual in its grounding (no rule fixes which objects are beautiful) yet expressed conceptually (in language with truth-evaluable form); disinterested (the judger sets aside personal stake in the object''s existence). Subsequent traditions take different parts of this package as load-bearing: Hume''s standard-of-taste tradition emphasizes the convergence of competent judges; expressivist accounts treat aesthetic judgments as expressions of attitude; cognitivist accounts (Sibley, Goldman) defend their cognitive content. The judgment-of-taste / moral-judgment analogy in Kant is the bridge to ethics: both purport to bind universally without resting on prudential interest.',
    ARRAY['judgment_of_taste', 'aesthetic_appraisal'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'art',
    'Art',
    ARRAY['aesthetics'],
    'The category whose members are works of art — paintings, sculptures, musical compositions, novels, poems, films, performances, photographs, installations, conceptual works. The philosophical question "what is art?" asks for an account that determines membership: a definition specifying necessary and sufficient conditions, a family-resemblance survey, an institutional or historical relational specification, or an anti-essentialist denial that any informative account is available. Contemporary analytic philosophy of art has moved from the imitation theory and expression theory through formalism toward institutional and historical theories that treat art as a relational rather than intrinsic kind.',
    'Distinguish three pedagogically useful axes. (1) Intrinsic vs. relational accounts: imitation, expression, and formalism specify intrinsic features (representation, embodied emotion, significant form) that artworks must have; institutional and historical theories define art relationally (an artwork is whatever stands in the right relation to an artworld or art-historical lineage). (2) Extensional adequacy: any account must accommodate Duchamp''s readymades, conceptual art, performance art, and the avant-garde — a requirement that motivated the institutional turn. (3) Functional vs. procedural: some accounts (Levinson''s historical theory) define art by procedural relations to past art; others (Dickie''s 1974 institutional theory) by procedural relations to artworld practices; functional accounts hold artworks must be intended to elicit certain experiences. The shape of the contemporary debate is largely determined by which extensional and theoretical desiderata an account prioritizes.',
    ARRAY['work_of_art', 'artwork'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'ontology_of_artworks',
    'Ontology of Artworks',
    ARRAY['aesthetics'],
    'The metaphysical inquiry into what kind of thing artworks are: physical objects (paintings, sculptures), abstract types with concrete tokens (musical compositions, novels), performance events (dance, theater), structured properties (the modernist analysis of musical works), action-tokens (conceptual art), or sui generis artistic kinds. The central observation that drives the field is that artworks come in radically different ontological categories: the painting is a physical object, the symphony is repeatable across performances, the novel is preserved across editions and translations, the photograph admits multiple identical prints — each requires a different ontological account.',
    'Use the multiple-instances puzzle as entry. A painting is destroyed if its physical canvas is destroyed; a Beethoven symphony survives the destruction of any individual score or performance; a novel survives the loss of any particular printed copy. The standard taxonomy: singular artworks (most paintings, drawings, sculptures) — particular physical objects; multiple artworks (musical works, plays, novels, photographs, prints) — typically analyzed as types whose tokens are performances or copies; performance artworks (dance, music in performance) — events. Contemporary debates run between Platonist accounts (musical works are eternal abstract types — Wolterstorff, Kivy), creationist accounts (composers create new types — Levinson 1980), nominalist accounts (musical works are not real entities; the term names a useful fiction — Goodman), and structural accounts (musical works are pure structures — Wolterstorff, Currie). The case of conceptual and performance art presses every framework.',
    ARRAY['art_ontology', 'metaphysics_of_art'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'art_criticism',
    'Art Criticism',
    ARRAY['aesthetics'],
    'The practice of describing, interpreting, evaluating, and contextualizing works of art for an audience. Philosophical analysis of art criticism asks: what kinds of judgments and inferences does criticism legitimately make, what counts as evidence in critical disputes, what role do artist intentions play in interpretation, what are the criteria for evaluating critical interpretations, and how does criticism relate to art-historical and theoretical discourse? Methodologically situated between the practical activity of critics (whose products are reviews, essays, monographs) and the theoretical concerns of philosophical aesthetics.',
    'Treat art criticism philosophically along four axes. (1) Description: the critic articulates the work''s features — what it shows, how it is structured, what techniques it deploys. (2) Interpretation: the critic offers an account of what the work means or expresses; the central philosophical dispute concerns whether artist''s intentions fix the meaning (intentionalism) or whether meaning is fixed by features and conventions independent of intentions (anti-intentionalism). (3) Evaluation: the critic appraises aesthetic value; whether evaluation is rule-governed, principle-governed, or particularist is contested (Sibley, Beardsley, Goldman). (4) Contextualization: the critic places the work in art-historical and cultural context. Pedagogically the most fruitful entry is the interpretation question, since the intentionalism debate connects directly to philosophy of language (meaning, reference, speech-acts) and philosophy of mind (intention, mental content).',
    ARRAY['critical_practice', 'aesthetic_criticism'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'aesthetic_value',
    'Aesthetic Value',
    ARRAY['aesthetics'],
    'The species of value attaching to objects in virtue of their aesthetic properties — the value of a beautiful sunset, an elegant proof, a moving symphony, a graceful performance. Aesthetic value is paradigmatically distinguished from moral, prudential, epistemic, and economic value, though the boundary cases (the moral value of art, the cognitive value of literature, the prudential value of beauty) are themselves much disputed. Whether aesthetic value reduces to aesthetic experience (the experiential or hedonic theory), to functional success in eliciting appropriate responses, to the realization of aesthetic properties, or to something else, is the central question.',
    'Three distinctions help students. (1) Experiential vs. property-based: hedonic theories (Beardsley, Iseminger) reduce aesthetic value to the value of aesthetic experiences; property-based theories (Goldman, Levinson) ground it in the realization of aesthetic properties. (2) Intrinsic vs. instrumental: intrinsicalists hold aesthetic value is final value (worth pursuing for its own sake); instrumentalists hold it derives from aesthetic value''s contribution to other goods (well-being, understanding, community). (3) Pluralist vs. monist: pluralists hold there are multiple distinct kinds of aesthetic value (beauty, sublimity, expressive power, formal interest); monists hold a single underlying value-property unifies the family. The autonomy-of-aesthetic-value debate sits at the intersection of these axes: how much does aesthetic value depend on or reduce to other species of value?',
    ARRAY['aesthetic_worth', 'beauty_value'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'taste_aesthetic',
    'Taste (Aesthetic)',
    ARRAY['aesthetics'],
    'The capacity for discriminating aesthetic properties and forming aesthetic judgments. Hume''s "Of the Standard of Taste" (1757) is the canonical analytic anchor: faced with the apparent variability of aesthetic preferences across individuals and cultures, Hume argues the standard of taste is set by the convergent verdicts of qualified judges — those with delicate organs, practiced perception, freedom from prejudice, comparison across many works, and sound understanding. The framework establishes both the realist commitment (there is a standard) and the recognition of expert authority that competent observers reliably converge.',
    'Hume''s "Of the Standard of Taste" is the cleanest entry. Hume''s problem: aesthetic judgments seem to claim correctness ("Milton is greater than Ogilby") yet face apparent disagreement; both demands cannot be met if the standard is mere preference. Hume''s solution: the standard is fixed by the verdicts of competent judges. Hume''s qualification list: delicate organs (perceptual sensitivity), practiced perception (developed by exposure), freedom from prejudice (suspended self-interest), comparison (knowledge of the broad range of works), sound understanding (general intellectual competence). The five-fold list both diagnoses why ordinary judgers diverge and identifies the corrective procedure. Subsequent debates: who counts as a competent judge? does competence track tradition-internal standards or universal aesthetic facts? does the convergence of competent judges constitute the standard or merely indicate it? Hume''s framework is the launching point for Kant''s deeper transcendental analysis and for contemporary realist defenses of taste.',
    ARRAY['standard_of_taste', 'aesthetic_taste'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'kantian_aesthetic_judgment',
    'Kantian Aesthetic Judgment',
    ARRAY['aesthetics'],
    'Kant''s analysis of the judgment of taste in the Critique of the Power of Judgment (1790, third Critique). The central puzzle: judgments of beauty (this rose is beautiful) appear to claim universal validity (every judger should agree) yet rest on the singular feeling of pleasure or displeasure rather than on conceptual rules. Kant''s solution: the pleasure that grounds the judgment of taste arises from the harmonious free play of imagination and understanding when the cognitive faculties are engaged by an object without being subsumed under a determinate concept; this free play, being a feature of the cognitive faculties shared by all rational beings, grounds the judgment''s purported universal communicability.',
    'Kant''s account has four moments students should track. (1) Disinterest: the pleasure in the beautiful is not based on what the object can do for one practically — it is independent of the object''s existence as a means to ends. (2) Universality: the judgment claims the agreement of every judger, but without resting on a concept (since no concept fixes which objects are beautiful). (3) Purposiveness without purpose: the beautiful object is experienced AS IF designed for the cognitive faculties, without being subsumed under any particular concept of what it was designed for. (4) Necessity: the pleasure is felt as necessary, as the response any properly cognizing subject would have. Kant''s framework is the philosophical anchor for taking aesthetic judgments seriously as cognitively significant and the bridge between Hume''s standard-of-taste empiricism and contemporary cognitivist accounts of aesthetic judgment.',
    ARRAY['kant_third_critique', 'critique_of_judgment_aesthetic'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'imitation_theory_art',
    'Imitation Theory of Art',
    ARRAY['aesthetics'],
    'The view that art is essentially imitation (mimesis) of reality — natural appearances, human actions, character, emotion. Plato (Republic Books 3 and 10) treated visual art and dramatic poetry as imitations of imitations (since the perceptible world is itself an imitation of Forms), grounding his suspicion of art''s epistemic and ethical status. Aristotle (Poetics) reframed mimesis positively: tragedy imitates a complete action and elicits catharsis; mimesis is natural to humans and is one of our principal modes of learning. The imitation theory dominated Western art theory through the early modern period and was the default account against which the expression and formalist theories defined themselves.',
    'Imitation theory is the historical anchor; teach it to give students the context for the post-Romantic shift to expression and the post-Impressionist shift to formalism. The strengths: imitation captures something true of figurative painting, sculpture, drama, and narrative literature — that they often are about, depict, or portray things; it grounds the natural-realist thought that art-making is a species of representational activity. The standard objections: (1) extensional inadequacy — non-representational music, abstract painting, ornament, and architecture do not obviously imitate anything; (2) under-specification — many things imitate without being art (counterfeits, mirrors, photographs in their non-artistic uses); (3) misdirection — even of representational arts, what makes them art is not the imitation but the imitation done well, suggesting the theory needs supplementation by aesthetic-property or expression-property considerations. The expression and formalist theories arose specifically as responses to these inadequacies.',
    ARRAY['mimesis_theory', 'representation_theory_art'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'expression_theory_art',
    'Expression Theory of Art',
    ARRAY['aesthetics'],
    'The view that art is essentially the expression of emotion. Tolstoy (What Is Art? 1898) gave the tradition its most influential statement: art is the activity by which the artist communicates emotion they have experienced to an audience who comes to share the emotion through engaging with the work. Collingwood (Principles of Art 1938) refined the position: art is the imaginative articulation of emotion in a medium, distinguished from mere arousal of emotion (which is craft, not art). Subsequent expression theorists (Bouwsma, Tormey, Wollheim) shifted from Tolstoy''s communication model toward analyses of expression as a property of artworks rather than as a transaction between artist and audience.',
    'Distinguish two threads. (1) Communication models (Tolstoy): the artwork is a vehicle by which the artist transmits emotion to an audience; art succeeds when it reliably elicits the emotion the artist felt. (2) Articulation models (Collingwood): art is the artist''s imaginative discovery of what they feel through working in a medium; the audience''s engagement with the work re-traces the articulation. The Wollheim 1968 question is the contemporary refinement: under what conditions is a work of art genuinely sad or joyful (rather than depicting sad or joyful subjects)? — leading to expression-as-property analyses (Goodman''s metaphorical exemplification, Davies''s experiential perception of expressive properties, Robinson''s romantic theory of authorial expression). The communication model has well-known objections (artists need not have the emotion, audiences need not feel what artists felt, much expressive art is about rather than from the emotion); the articulation and expression-as-property models have been more fruitful in contemporary aesthetics.',
    ARRAY['art_as_expression', 'expressionism_aesthetic_theory'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'formalism_artistic',
    'Formalism (Artistic)',
    ARRAY['aesthetics'],
    'The view that the aesthetically relevant features of a work of art are its formal features — the arrangement of lines, colors, shapes, masses (in visual art); pitches, durations, dynamics, rhythms (in music); the structural relations among these features rather than what they represent or express. Clive Bell (Art 1914) coined "significant form" as the property by which artworks distinctively engage aesthetic emotion; Roger Fry developed the visual-art-historical implications, treating Post-Impressionism as the discovery of art''s formal essence. Formalism flourished as the high-modernist defense of non-representational and non-expressive art, then receded as the institutional and historical theories took up the task of accommodating conceptual art and post-modern practice.',
    'Treat formalism as the theory whose strengths and weaknesses both come from the same move — restricting aesthetically relevant features to formal ones. Strengths: (1) accommodates non-representational art (abstract painting, instrumental music, ornament, architecture) as central rather than peripheral; (2) explains why representational works can be aesthetically failed (the representation alone is not enough); (3) cleanly separates aesthetic from non-aesthetic features. Weaknesses: (1) seems to deny the aesthetic relevance of representational, expressive, and historical features that competent critics treat as central; (2) Bell''s "significant form" was famously circular (significant form = form that elicits aesthetic emotion = emotion elicited by significant form); (3) cannot accommodate works whose interest lies in conceptual or institutional positioning (Duchamp''s readymades, much conceptual art). Formalism remains influential in restricted ways — formal analysis is part of any competent criticism — without sustaining the strong claim that formal features exhaust aesthetic relevance.',
    ARRAY['formalist_aesthetics', 'significant_form_theory'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'institutional_theory_of_art',
    'Institutional Theory of Art',
    ARRAY['aesthetics'],
    'George Dickie''s account (Art and the Aesthetic 1974) that art is whatever has been conferred the status of candidate for appreciation by a person or persons acting on behalf of a social institution called the artworld. Dickie defines work of art procedurally and relationally: an item is an artwork if (i) it is an artifact and (ii) someone with appropriate standing in the artworld has acted to confer upon it the status of candidate for appreciation. The theory is a direct response to the extensional inadequacy of the imitation, expression, and formalist theories given Duchamp''s readymades, found art, and conceptual art.',
    'The institutional theory is the cleanest entry to relational accounts of art. Strengths: (1) accommodates Duchamp''s Fountain, conceptual art, and the avant-garde without strain — these are art because the artworld treats them as art; (2) explains the role of museums, galleries, critical practice, and art-historical narrative in fixing art-status; (3) makes art a recognizably social rather than purely natural kind. Weaknesses: (1) circularity worry — the artworld is defined by reference to artworks; (2) status conferral does not guarantee aesthetic value (the theory is a definition of art, not of GOOD art); (3) the institution-relativism worry (does some practice need to ALREADY be art for the theory to apply, generating an infinite regress?). Dickie''s 1984 revision (The Art Circle) offered a tighter circular formulation that explicitly accepts and defends the institutional reflexivity. The historical theory (Levinson) was developed partly as a response to the institutional theory''s difficulties.',
    ARRAY['dickie_institutional', 'artworld_theory'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'historical_theory_of_art',
    'Historical Theory of Art',
    ARRAY['aesthetics'],
    'Jerrold Levinson''s account (Defining Art Historically 1979; Music, Art, and Metaphysics 1990) that art is whatever is intended for regard-as-a-work-of-art in some way that earlier-recognized art has been correctly regarded. The definition is recursive and historical: at any time, what counts as art is fixed by reference to what is correctly classified as art at earlier times, with the recursion bottoming out in the Ur-arts of the historical lineage. Like the institutional theory, the historical theory is a relational account; unlike the institutional theory, the relevant relation is to art history rather than to artworld practices.',
    'The historical theory is the cleanest entry to lineage-based accounts. Strengths: (1) accommodates the avant-garde and conceptual art without invoking a problematic artworld institution — the lineage rather than the institution does the work; (2) explains how art-status propagates and revises over time as the canon grows; (3) avoids the institutional theory''s reflexivity worry by grounding art-status in past correct classifications rather than present institutional acts; (4) accommodates art''s evolution by allowing intended-regards that depart from earlier modes (avant-garde works are art because intended-for-regard-AS-A-WORK-OF-ART, even if their specific mode of regard is novel). Weaknesses: (1) the bootstrapping question — how did the original Ur-arts come to be art? Levinson invokes intentions of original makers, which raises the question of how those intentions were available before any art existed; (2) the appropriative question — colonial and cross-cultural appropriations complicate the lineage; (3) the uncreated-art-by-machine question. The historical theory is widely treated as the strongest contemporary relational account.',
    ARRAY['levinson_historical', 'art_lineage_theory'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'sublime',
    'Sublime',
    ARRAY['aesthetics'],
    'The aesthetic category complementary to the beautiful, characterized by a complex pleasurable response to objects that overwhelm the senses or imagination — vast natural scenes (mountain ranges, oceans, storms), cosmic magnitudes, terrifying spectacles, and certain morally elevated artworks. Burke (A Philosophical Enquiry into the Origin of Our Ideas of the Sublime and Beautiful 1757) gave the canonical empiricist account: the sublime arises from terror modified by the security of the observer; its pleasure is a delight in the experience of a softened terror. Kant (Critique of the Power of Judgment 1790) gave the canonical transcendental account: the sublime is the feeling that arises when the imagination, failing to grasp the magnitude of the object, succeeds in awakening reason''s apprehension of the supersensible.',
    'Burke and Kant are the canonical pair. Burke''s sublime is a passion arising from terror at a distance — pleasure in vastness, obscurity, power, and difficulty when these features cannot harm the observer; Burke distinguishes the sublime systematically from the beautiful (which is small, smooth, gradual, easy). Kant''s sublime is bifurcated into the mathematically sublime (pleasure in the imagination''s failure to comprehend magnitude, where reason supplies the idea of infinity) and the dynamically sublime (pleasure in nature''s might when contemplated from safety, awakening the supersensible idea of human dignity as not subject to nature). The two categories — mathematical and dynamic — preserve the Burkean phenomenology while embedding it in the transcendental architecture. Pedagogically, the sublime is the entry to aesthetic categories beyond beauty and to Kant''s reckoning with aesthetic experience that escapes harmony into something more conflicted.',
    ARRAY['the_sublime', 'sublimity'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'aesthetic_disinterest',
    'Aesthetic Disinterest',
    ARRAY['aesthetics'],
    'The condition that the appropriate aesthetic engagement with an object suspends practical interest in the object — the observer attends to the object for what it is rather than for what it can do for them. Kant''s third Critique (1790) made disinterest the first moment of the analytic of the beautiful: the pleasure in the beautiful is independent of the object''s existence as a means to ends, distinguishing the judgment of taste from judgments of the agreeable (which depend on appetite) and judgments of the good (which depend on practical reason). Schopenhauer radicalized the position: aesthetic experience is the suspension of the will''s striving and grants temporary release from the suffering inherent in willing.',
    'The aesthetic-attitude tradition (Kant, Schopenhauer, Bullough''s "psychical distance", Stolnitz, Aldrich) makes disinterest the criterion of aesthetic perception. The contemporary status of the position is mixed. Defenders (Stolnitz 1960, Iseminger 2004) argue disinterest captures something real about the difference between appreciating a painting AS A PAINTING and appreciating it as an investment, an heirloom, or a tool of seduction. Critics (Dickie 1964 "The Myth of the Aesthetic Attitude") argue the disinterest condition is either trivial (everyone agrees one should attend to what one is appreciating) or false (much serious engagement with art presupposes practical, biographical, political, and moral interests). Pedagogically, present disinterest as the load-bearing condition of one influential aesthetic-attitude tradition, with contemporary debate divided over whether it survives Dickie''s critique.',
    ARRAY['disinterested_attention', 'aesthetic_distance'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'free_play_imagination_understanding',
    'Free Play of Imagination and Understanding',
    ARRAY['aesthetics'],
    'Kant''s third Critique (1790) account of the cognitive grounding of the judgment of taste. When a beautiful object engages the observer, the cognitive faculties — imagination (which gathers and synthesizes the perceptual manifold) and understanding (which subsumes the synthesized matter under concepts) — enter into a harmonious cooperation that does not terminate in any determinate concept. This free play (without the constraint of a particular concept being applied) generates the pleasurable feeling that grounds the universal communicability of the judgment of taste, since the cooperation of the cognitive faculties is shared by all rational beings.',
    'The free play is Kant''s answer to the puzzle the four moments of the aesthetic judgment pose: how can a judgment claim universal validity if it rests on feeling rather than concept? Kant''s answer: the feeling itself reflects a state of the cognitive faculties (imagination and understanding in harmony) shared by all subjects; thus the feeling, while singular, is universally communicable in principle. The free play thesis is metaphysically loaded but pedagogically illuminating: it explains why aesthetic experience feels cognitively significant even when it does not deliver a determinate proposition, why beautiful objects feel as if they were "made for" cognition, and why the universal communicability of the judgment of taste is a transcendental rather than empirical claim. Subsequent traditions in aesthetics (Schopenhauer''s suspension of will, the psychic-distance tradition, the contemporary cognitivist accounts of aesthetic experience) all engage with Kant''s free-play architecture.',
    ARRAY['kant_free_play', 'cognitive_free_play'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'pictorial_representation',
    'Pictorial Representation',
    ARRAY['aesthetics'],
    'The relation by which a picture (painting, drawing, photograph, sculpture in relief) depicts its subject — a portrait depicts a person, a landscape depicts a scene, a still life depicts an arrangement of objects. The central dispute concerns whether pictorial representation is grounded in resemblance (the picture looks like its subject) or convention (a picture depicts what it does because of culturally inherited conventions, on a par with how a word denotes its referent). Goodman (Languages of Art 1968) gave the canonical convention-based account; resemblance theorists (Peacocke, Hopkins) have responded by reformulating resemblance in non-naive ways.',
    'Goodman''s critique of resemblance is the canonical entry. Goodman argues resemblance is symmetric (X resembles Y iff Y resembles X) but representation is not (a portrait depicts the sitter; the sitter does not depict the portrait); resemblance is reflexive (everything resembles itself maximally) but representation typically is not; and resemblance per se cannot ground the depiction relation since anything resembles many things. Goodman''s positive account: depiction is a symbol-system relation governed by conventions of denotation, on a par with linguistic reference but with different formal properties (depictions are dense and replete in Goodman''s technical sense). Resemblance theorists respond by reformulating resemblance as an experienced or constrained relation (Peacocke''s "experienced resemblance"; Hopkins''s "outline shape"). Wollheim''s seeing-in account is a third position: pictorial representation is a sui generis perceptual capacity whereby viewers see the subject IN the picture''s surface — neither a pure inference from resemblance nor a decoding of convention, but a fundamental visual capacity.',
    ARRAY['pictorial_depiction', 'visual_representation'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'depiction',
    'Depiction',
    ARRAY['aesthetics'],
    'The specific perceptual mode by which a viewer recognizes what a picture pictures. Wollheim (Art and Its Objects 1968; Painting as an Art 1987) gave the canonical contemporary account in terms of "seeing-in": the viewer sees the depicted subject IN the picture''s marked surface, simultaneously seeing the surface as marked and the subject as visually present. Seeing-in is offered as a fundamental visual capacity — neither reducible to resemblance recognition nor to inferential decoding of convention — that grounds pictorial representation while explaining its phenomenal character.',
    'Wollheim''s seeing-in is a sui generis perceptual capacity meant to occupy the middle ground between Goodman''s pure conventionalism (which seems to under-describe the visual phenomenology of looking at pictures) and naive resemblance theory (which ignores the configural aspect of the picture''s surface). The two-foldedness thesis is central: in seeing-in, the viewer is simultaneously and inseparably aware of the picture''s marked surface AND of the depicted subject; neither dimension is psychologically or epistemologically prior. The account preserves the phenomenology of pictorial perception (we DO see things in pictures, in a way distinct from reading text or interpreting symbols) while explaining the conventionality of pictorial styles (different depictive systems can support seeing-in for different audiences). Critics have pressed: how exactly does seeing-in work? what is its psychological reality? — but Wollheim''s framework remains the dominant contemporary alternative to Goodman.',
    ARRAY['wollheim_seeing_in', 'pictorial_seeing_in'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'expression_in_art',
    'Expression in Art',
    ARRAY['aesthetics'],
    'The property of artworks by which they are themselves sad, joyful, melancholy, exuberant, anxious, serene — distinguished from artworks that depict sad people or were made by sad artists. The contemporary literature treats expression as a property of the work rather than as a transaction between artist and audience: a sonata is sad because of its sonic features (slow tempo, minor key, descending lines) that it shares with sad behavior, not because the composer was sad. Goodman (Languages of Art 1968) gave the canonical metaphorical-exemplification analysis; Davies, Robinson, Kivy, and Levinson have developed alternative experiential, persona-based, and intentionalist accounts.',
    'Use Goodman as anchor. Goodman: a work expresses a property when it metaphorically possesses and exemplifies that property — a sonata expresses sadness when it metaphorically IS sad and refers to that property. The metaphorical possession reverses the literal: literally, the sonata has sonic features; metaphorically (by analogical extension from the human-emotion case) those features make the sonata sad in a non-literal but real way. Davies''s "appearance theory": a work expresses a property when it has features perceived as resembling the appearance of someone with that property. Robinson''s romantic theory: expression involves a persona articulating an emotion the artist intends. Kivy''s contour theory: expressive properties of music are perceived in virtue of resemblances to the contours of human emotional behavior. The disagreement is largely about the right analysis of a phenomenon they all take to be real and central: artworks DO express, and that expression is a property of the work, not just of the artist or audience.',
    ARRAY['artwork_expression', 'expressive_property'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'metaphor',
    'Metaphor',
    ARRAY['aesthetics'],
    'The figurative use of an expression in which it carries a meaning that diverges from its literal meaning, typically by transporting a concept from one domain to another to illuminate the target domain ("Juliet is the sun"; "the mind is a stage"; "this argument is on shaky ground"). Aesthetic theories of metaphor are concerned both with metaphor as a feature of literary art and with metaphor as a model for non-literal aesthetic phenomena (expression, depiction, fictional truth). The central philosophical disputes concern whether metaphors have distinctive metaphorical meanings (Black, Beardsley, Goodman), whether they communicate via implicature on top of literal meaning (Searle, Grice), or whether they have only literal meaning and a pragmatic-causal effect (Davidson 1978 "What Metaphors Mean").',
    'Three positions students should distinguish. (1) Cognitivist (Black 1962 interaction theory; Goodman 1968 metaphorical reference): metaphors have distinctive metaphorical meanings or referents that cannot be reduced to literal paraphrase; the interaction between principal subject and subsidiary subject generates new cognitive content. (2) Pragmatic (Searle 1979; Grice): metaphors have only literal meaning; the metaphorical content is conveyed by speaker meaning that diverges from sentence meaning, calculated by pragmatic principles like the Gricean cooperative principle. (3) Causalist (Davidson 1978): metaphors have only literal meaning and no metaphorical meaning; metaphors work by causing the audience to notice things, not by communicating propositional content. The aesthetic significance of the dispute: cognitivist accounts make metaphor a vehicle of cognitive insight (and hence ground claims that art delivers cognitive value); causalist and pragmatic accounts more cautiously locate metaphor''s effect at the boundary of meaning and effect.',
    ARRAY['figurative_metaphor', 'metaphorical_meaning'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'type_token_artworks_distinction',
    'Type-Token Distinction (Artworks)',
    ARRAY['aesthetics'],
    'The application of the Peircean type-token distinction to the ontology of artworks. Some artworks (a particular painting, a particular sculpture) are type-tokens of themselves — there is one canvas, one bronze. Other artworks (a symphony, a novel, a film, a poem) are types whose performances or copies are tokens. The type-token framework is the canonical analytic apparatus for the multiple-instance puzzle: a Beethoven symphony survives any individual performance because the symphony is a type, and performances are its tokens; the score is a recipe specifying how to produce well-formed tokens.',
    'The type-token framework is Wolterstorff''s and Levinson''s shared starting point for artwork ontology, and the place where their views diverge. Wolterstorff (Works and Worlds of Art 1980): musical works are eternal abstract types, discovered by composers rather than created — the symphony existed Platonically before Beethoven wrote it down, and Beethoven discovered rather than created it. Levinson 1980: musical works are created abstract types — the symphony begins to exist when the composer indicates the right type; this preserves the intuition that composers genuinely make new artworks. Goodman (Languages of Art 1968) is structuralist: a musical work is a class of compliant performances of a score; the work has no separate Platonic existence. Currie''s (1989) action-types view: an artwork is the action-type of structuring matter in a specified way, identifiable across instantiations. The disputes among these positions are the live working terrain of contemporary art-ontology.',
    ARRAY['artwork_type_token', 'work_token_distinction'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'fictional_truth',
    'Fictional Truth',
    ARRAY['aesthetics'],
    'The phenomenon of truth-in-fiction: it is true IN the story that Sherlock Holmes lives at 221B Baker Street, and false in the story that Holmes lives in Berlin. Fictional truth is generated by the fictional work''s text plus principles of generation (Walton 1990), reality-importation defaults (Lewis 1978), or counterfactual evaluation against the closest world in which the story is told as known fact (Lewis 1978). The central philosophical question is what makes propositions true-in-the-story and how the fictional and actual generate distinct but related truth-conditions.',
    'Walton''s Mimesis as Make-Believe (1990) is the most influential contemporary framework. Walton: works of fiction are props in games of make-believe; the fictional truths are what the audience is mandated to imagine when engaging with the work as the fiction-game prescribes. The work''s text generates primary fictional truths; principles of generation (e.g., reality importation: assume defaults from the actual world unless the fiction overrides them; genre-based defaults; standard inferences) generate secondary fictional truths. Lewis (1978 "Truth in Fiction") gave the modal-realist alternative: a fictional sentence is true in the fiction if it is true at the closest possible worlds in which the story is told as known fact. The two frameworks make different predictions for cases like inconsistent fictions, fiction-internal authorial errors, and the fiction-vs-reality interface (does Holmes inhabit a world with our laws of physics? our history? our geography?). The dispute is the live core of contemporary fictionalism in aesthetics and philosophy of language.',
    ARRAY['truth_in_fiction', 'walton_make_believe'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'ontology_musical_works',
    'Ontology of Musical Works',
    ARRAY['aesthetics'],
    'The application of artwork ontology to the case of musical works — a domain singled out for sustained analysis because musical works are paradigm cases of multiple-instance art and because their relation to scores, performances, and recordings raises sharp ontological questions. Is Beethoven''s Fifth Symphony an eternal Platonic type (Wolterstorff), a created abstract type (Levinson 1980 "What a Musical Work Is"), a class of compliant performances (Goodman), an action-type structuring sound (Currie), or a structural type discovered like a number (Kivy)? The dispute matters because it bears on what composers do, when works begin to exist, what counts as a performance of a given work, and how works relate to scores and recordings.',
    'Levinson''s "What a Musical Work Is" (1980) is the cleanest entry. Levinson: a musical work is an indicated structure-as-of-time-T-by-composer-C — an abstract type whose identity depends on the structure (the sound-pattern), the composer''s indication (specifying the structure), and the time of indication (which fixes the historical-musical context). This view (called creationism or fine-grained structuralism) preserves three intuitions: (1) composers create rather than discover their works; (2) two acoustically identical works could differ in identity if composed in different historical contexts; (3) performances are tokens whose well-formedness depends on conformity to the indicated structure. Wolterstorff''s Platonism rejects (1) but accepts (3). Goodman''s nominalism rejects the type-realm altogether. Kivy''s discovery-Platonism (Authenticities 1995) accepts (3) and the discoverable nature of works but rejects (2). Pedagogically the case is the most-studied test of every artwork-ontological framework.',
    ARRAY['musical_work_ontology', 'works_of_music'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'intentionalism_artistic',
    'Intentionalism (Artistic)',
    ARRAY['aesthetics'],
    'The view that the meaning of an artwork is fixed (in whole or in part) by the artist''s intentions — what the artist meant, intended, or sought to convey through the work. Hirsch (Validity in Interpretation 1967) gave the canonical defense in literary theory: a work''s verbal meaning is what its author intended; subsequent significance may shift, but meaning does not. In analytic aesthetics, Levinson''s hypothetical intentionalism (Music in the Moment 1996; Aesthetic Concept Cluster) and Stecker''s actual intentionalism (Artworks 1997) are the leading contemporary positions, both responding to the Wimsatt-Beardsley anti-intentionalist legacy.',
    'Distinguish three positions students should track. (1) Strong actual intentionalism (Hirsch): the work means what the author intended, full stop; failed intentions are interpretive errors of the work. (2) Moderate actual intentionalism (Stecker, Carroll): the work means what the author intended provided the work supports that interpretation; intentions constrain but do not unilaterally fix meaning. (3) Hypothetical intentionalism (Levinson): the work means what an ideal audience contemporary with the work, knowing all relevant context, would best hypothesize the author to have intended; this gives intentions a regulative role without making them dispositive. The contemporary debate is largely between (2) and (3), with (1) treated as too strong (it makes failed-intention works interpretive errors) and pure anti-intentionalism (the work''s meaning is wholly fixed by features and conventions independent of intentions) treated as too weak (it ignores the role of expression and authorial selection in fixing meaning).',
    ARRAY['author_intentionalism', 'art_intentionalism'],
    'INTERPRETED',
    'ai-seed',
    11
  ),
  (
    'anti_intentionalism',
    'Anti-Intentionalism',
    ARRAY['aesthetics'],
    'The view that an artwork''s meaning is fixed by features and conventions independent of the artist''s intentions; the artist''s intentions are evidence about the work only insofar as they are accessible through the work itself. Wimsatt and Beardsley (The Intentional Fallacy 1946) gave the canonical statement: it is a fallacy in literary criticism to treat the author''s intention as either available (since it is private and often inaccessible) or relevant (since the meaning of the public work is what the words on the page mean, not what the author privately intended). The position dominated mid-century literary criticism and remains the foil against which contemporary intentionalists position themselves.',
    'The Wimsatt-Beardsley argument has two strands students should distinguish. (1) The epistemic strand: authorial intentions are private mental states and typically inaccessible; even authoritative-sounding biographical declarations may misrepresent or rationalize. (2) The semantic strand: the public work''s meaning is fixed by linguistic and pictorial conventions; private intentions cannot magically alter what the work''s features semantically license. Critics of anti-intentionalism (Hirsch, Levinson, Stecker, Carroll) target both strands: the epistemic strand is too strong (we often have good evidence of intentions, including in the work itself; in any case, evidence-availability does not bear on what is true); the semantic strand is too crude (much linguistic and pictorial meaning is generated by speaker-intention via Gricean mechanisms). Contemporary aesthetic intentionalism is the synthesis: intentions matter for meaning, but they must be accessible through the work and cannot override what the work''s public features demand.',
    ARRAY['intentional_fallacy', 'wimsatt_beardsley_anti_intentionalism'],
    'INTERPRETED',
    'ai-seed',
    11
  );

-- Edges: 32 INSERTs, all pedagogical_prerequisite. All within-domain
-- (source and target both tagged aesthetics). Cross-domain edges
-- (aesthetic_judgment -> ethics on moral judgment; expression_theory_art
-- and expression_in_art -> philosophy of mind on intentionality;
-- metaphor and pictorial_representation -> philosophy of language on
-- meaning and reference; fictional_truth -> metaphysics and philosophy
-- of language; type_token_artworks_distinction -> metaphysics on
-- universals) are P5-11's exclusive surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Foundation spine: aesthetics fans out to six T1 branches
  ('aesthetics', 'aesthetic_experience', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetics', 'aesthetic_property', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetics', 'aesthetic_judgment', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetics', 'art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetics', 'ontology_of_artworks', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetics', 'art_criticism', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Aesthetic value & taste cluster
  ('aesthetic_property', 'aesthetic_value', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetic_judgment', 'taste_aesthetic', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetic_judgment', 'kantian_aesthetic_judgment', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetic_judgment', 'sublime', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetic_experience', 'aesthetic_disinterest', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('kantian_aesthetic_judgment', 'aesthetic_disinterest', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('kantian_aesthetic_judgment', 'free_play_imagination_understanding', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('taste_aesthetic', 'kantian_aesthetic_judgment', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Definition of art cluster
  ('art', 'imitation_theory_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('art', 'expression_theory_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('art', 'formalism_artistic', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('art', 'institutional_theory_of_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('art', 'historical_theory_of_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Representation & meaning cluster
  ('art', 'pictorial_representation', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('pictorial_representation', 'depiction', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('expression_theory_art', 'expression_in_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('expression_in_art', 'metaphor', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Ontology of artworks cluster
  ('ontology_of_artworks', 'type_token_artworks_distinction', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('ontology_of_artworks', 'fictional_truth', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('type_token_artworks_distinction', 'ontology_musical_works', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Criticism & interpretation cluster
  ('art_criticism', 'intentionalism_artistic', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('art_criticism', 'anti_intentionalism', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('anti_intentionalism', 'intentionalism_artistic', 'pedagogical_prerequisite', 'ai-seed', 11),
  -- Cross-cluster within-aesthetics bridges
  ('aesthetic_experience', 'expression_theory_art', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('aesthetic_property', 'formalism_artistic', 'pedagogical_prerequisite', 'ai-seed', 11),
  ('fictional_truth', 'metaphor', 'pedagogical_prerequisite', 'ai-seed', 11);

COMMIT;
