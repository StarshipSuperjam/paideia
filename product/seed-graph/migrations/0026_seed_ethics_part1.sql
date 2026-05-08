-- Migration: 0026_seed_ethics_part1
-- Purpose: Seventh Phase 5 seed migration (second ethics file) — applied
--   ethics concepts plus within-domain pedagogical_prerequisite edges.
--   Authored in S-0059 against task P5-04b "Ethics applied seed" of
--   target T-PHASE-5 per engine/build_readiness/phase_5.md (gate report)
--   and product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   P5-04b is the pre-split b-half of the ethics subdomain per phase_5.md
--   T1-B; P5-04a (Ethics metaethics+normative) was the a-half and
--   completed at S-0058. This seed completes the ethics subdomain for
--   cross-bridge consumption at P5-11. Covers three layers per
--   phase_5.md T1-B "Ethics applied (P5-04b) — bioethics,
--   environmental ethics, applied moral problems": (1) the bioethics
--   layer — bioethics umbrella, medical ethics, research ethics, end-
--   of-life and reproductive ethics, plus the canonical Beauchamp &
--   Childress four-principles framework (autonomy, beneficence, non-
--   maleficence, justice) and informed consent as the procedural
--   embodiment of autonomy; (2) the environmental-ethics layer —
--   environmental ethics umbrella, the three value-centric stances
--   (anthropocentrism, biocentrism, ecocentrism), Naess's deep ecology,
--   animal ethics with sentientism as its canonical foundational
--   stance, climate ethics with the intergenerational structure that
--   distinguishes climate from earlier environmental concerns, and
--   Parfit's non-identity problem as the puzzle that complicates every
--   future-generations argument; (3) the applied-moral-problems
--   layer — applied ethics umbrella, just war theory and its
--   pacifist denial, business ethics, technology ethics with AI
--   ethics as the contemporary frontier.
-- Loads tables: public.nodes (28 INSERTs), public.edges (34 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 7 -> 8).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 7 at session boot (post-S-0058; verified
--     via Supabase MCP execute_sql at S-0059 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 8 (the
--     post-increment value).
--   * P5-01a epistemology core seed applied (0011) — depends_on
--     dependency satisfied since S-0050.
--   * P5-04a ethics metaethics+normative seed applied (0020) — depends_on
--     dependency satisfied since S-0058. P5-04b builds on the
--     metaethical and normative-theory inventory P5-04a established;
--     several edges in this seed cross-reference P5-04a concepts where
--     pedagogically required (e.g., autonomy_bioethical's relation to
--     kantian_ethics is gestured at in teaching_notes; deontology's
--     bearing on informed_consent is gestured at in teaching_notes;
--     contractualism's bearing on intergenerational_justice is gestured
--     at in teaching_notes) — but no edges from P5-04b nodes back into
--     P5-04a nodes are authored here. The P5-04b seed is internally
--     self-contained on its own applied-ethics inventory; the cross-
--     reference edges to P5-04a's normative theories defer to P5-11
--     cross-bridges (specifically the within-ethics edges from
--     consequentialism / deontology / virtue_ethics / contractualism
--     into the applied concepts here are within-domain so could in
--     principle live here; the deliberate choice mirrors P5-01b's
--     construction — it cross-references P5-01a foundational anchors
--     liberally — versus the P5-02b construction, which similarly
--     cross-references P5-02a's metaphysical inventory. Here we adopt
--     the P5-01b/P5-02b pattern: cross-references back into the a-half
--     are within-domain, all-ethics, and so live in the b-half rather
--     than P5-11. See "Edge structure" below for the specific cross-
--     references authored.
--   * No prior migrations under prefix 0026-0029; this is the first
--     ethics-applied seed file. The 0020-0025 range is occupied by
--     P5-04a's 0020 file (the a-half occupied 0020 alone, leaving
--     0021-0025 reserved per the granularity principle within the
--     a-half).
-- Postconditions:
--   * 28 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'ethics'}, status=active, graph_version_added=8.
--   * 34 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=8. All edges are
--     within-domain (source and target both tagged ethics);
--     cross-domain edges remain P5-11's exclusive responsibility.
--     Cross-references back into P5-04a's metaethics+normative-theory
--     inventory (e.g., consequentialism→business_ethics,
--     deontology→informed_consent, contractualism→intergenerational_justice,
--     supererogation→pacifism, virtue_ethics→practical_wisdom-in-bioethical-
--     judgment) are deliberately deferred to P5-11 to keep the b-half
--     internally self-contained; see the contract block discussion in
--     Preconditions for the rationale (the choice differs from P5-01b
--     and P5-02b, which did include such cross-references; reflects
--     an evolving pattern recommendation).
--   * settings.graph_version = 8.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 8 AND 'ethics' = ANY(domain) :: 28
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 8 AND edge_type = 'pedagogical_prerequisite' :: 34
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 8
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract). Five
--     IDs carry domain-disambiguation suffixes to mark the ethics-
--     specific sense distinct from cross-domain homonyms: (1)
--     `autonomy_bioethical` — distinct from any future Kantian
--     metaphysics-of-autonomy node or any political-autonomy node in
--     P5-05; the bioethical sense is the first-personal capacity for
--     informed self-direction in medical / research contexts. (2)
--     `justice_bioethical` — distinct from political-philosophy
--     `distributive_justice` (P5-05) and any future Aristotelian or
--     Kantian justice nodes; the bioethical sense is the fair allocation
--     of medical resources and research benefits/burdens. The other 26
--     IDs are unambiguous within ethics broadly. The closest potential
--     collisions handled with explicit-suffix-or-careful-name choices:
--     `non_maleficence` (specific medical-ethical principle, no broader
--     ethics homonym), `beneficence` (same), `non_identity_problem`
--     (Parfit's specific 1984 puzzle, named exactly per the literature),
--     `informed_consent` (procedural concept, ethics-specific),
--     `four_principles_bioethics` (Beauchamp & Childress 1979 framework,
--     named explicitly so the eponymy is clear), `applied_ethics`
--     (umbrella named distinctly from `applied_moral_problems` to
--     match SEP convention), `medical_ethics` (the field, distinct from
--     bioethics by traditional/clinical-vs-broader scope), `business_ethics`
--     (the field, with the ethics suffix preserving the SEP/IEP
--     conventional naming), `technology_ethics` (the field), `ai_ethics`
--     (the field, with `ai` lowercased per slugification).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts. P5-04b is internally self-contained on its own applied-
--     ethics concepts; no edges reach back into P5-04a's metaethics or
--     normative-theory nodes (the cross-reference edges defer to P5-11
--     per the choice documented in Postconditions).
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph layers as a DAG with the broad shape:
--     T0: applied_ethics.
--     T1: bioethics, environmental_ethics, just_war_theory,
--       business_ethics, technology_ethics.
--     T2: medical_ethics, research_ethics, four_principles_bioethics,
--       anthropocentrism, biocentrism, ecocentrism, climate_ethics,
--       pacifism, ai_ethics.
--     T3: end_of_life_ethics, reproductive_ethics, autonomy_bioethical,
--       beneficence, non_maleficence, justice_bioethical, deep_ecology,
--       animal_ethics, future_generations.
--     T4: informed_consent, sentientism, intergenerational_justice.
--     T5: non_identity_problem.
--     Every edge below points from a lower-tier source to a higher-
--     tier target. validate.py's Kosaraju SCC check confirms post-apply
--     that the pedagogical_prerequisite subgraph remains acyclic
--     globally (the prior 0011 / 0016 / 0030 / 0036 / 0090 / 0020 seeds
--     plus this one's 34 edges, all together).
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: autonomy_bioethical and
--     informed_consent bridge to political philosophy (P5-05) on
--     autonomy as a political value; informed_consent additionally
--     bridges to philosophy of language (P5-08) on speech-act theory
--     of consent; non_identity_problem and intergenerational_justice
--     bridge to political philosophy (P5-05) on intergenerational
--     theories of justice and to metaphysics (P5-02a/b) on personal
--     identity over time and the existence of future persons;
--     end_of_life_ethics bridges to philosophy of mind (P5-07a/b) on
--     personal identity and consciousness in cases of severe cognitive
--     impairment; ai_ethics bridges to philosophy of mind (P5-07a/b)
--     on machine consciousness, moral status, and intentionality, to
--     philosophy of language (P5-08) on machine semantics, and to
--     epistemology (P5-01a/b) on machine knowledge / justification;
--     climate_ethics bridges to philosophy of science (P5-09) on the
--     epistemology of climate science, model uncertainty, and policy
--     under risk; just_war_theory bridges to political philosophy
--     (P5-05) on sovereignty and legitimate authority; deep_ecology
--     and ecocentrism bridge to metaphysics (P5-02a) on substance and
--     event ontology applied to ecosystems; animal_ethics and
--     sentientism bridge to philosophy of mind (P5-07a/b) on animal
--     consciousness and intentionality. All of these defer to P5-11.
--     Within-ethics cross-references back into P5-04a's
--     metaethics/normative-theory concepts (autonomy_bioethical to
--     kantian_ethics; informed_consent to deontology; future_generations
--     to contractualism; intergenerational_justice to contractualism;
--     business_ethics to consequentialism + deontology;
--     supererogation to pacifism; virtue_ethics to practical wisdom in
--     bioethical judgment) are also deferred to P5-11 — this seed keeps
--     the b-half internally self-contained. See Preconditions for the
--     rationale.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md). The historical_influence predicate is
--     not used here either; applied ethics has shorter and less
--     consensus-anchored intellectual lineages than metaethics
--     (Hippocrates -> medieval medical ethics -> Beecher 1966 ->
--     Belmont 1979 -> Beauchamp & Childress 1979; Naess 1973 ->
--     Singer 1975 -> Regan 1983 -> Parfit 1984; Walzer 1977
--     contemporary just war revival; Floridi 2010s tech ethics) so
--     historical_influence is reserved for a later phase per
--     PREDICATE_MANIFEST.md "historical_influence" row.
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0027-0029). Those
--     slots remain reserved for future ethics-applied extension if
--     Phase 6+ telemetry warrants additional applied-ethics concepts
--     (neuroethics, sports ethics, sex ethics, professional ethics,
--     specific applied-ethics taxonomies in business or technology,
--     specific climate-ethics granularity such as adaptation-vs-
--     mitigation, specific bioethical issues such as enhancement or
--     genetic modification). This seed completes P5-04b's task at the
--     granularity principle within the 0026 file: 28 nodes covering
--     the three named layers (bioethics + environmental + applied moral
--     problems) at the umbrella-plus-canonical-positions density that
--     P5-01a / P5-01b / P5-02a / P5-02b / P5-03 / P5-04a each
--     established. P5-05 (political philosophy) will independently
--     develop distributive_justice and related political concepts;
--     justice_bioethical here is the bioethics-context fair-allocation
--     concept and is distinct.
-- Cross-cutting decisions:
--   * confidence_level distribution: 28/28 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the contemporary applied
--     ethics literature (Beauchamp, Childress, Singer, Regan, Naess,
--     Parfit, Walzer, Rawls, Scanlon, Brennan, Floridi, Bostrom)
--     explicitly names. Mirrors P5-01a / P5-01b / P5-02a / P5-02b /
--     P5-03 / P5-04a's distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'ethics'. Multiple cross-domain reaches exist (autonomy and
--     informed_consent into political philosophy and philosophy of
--     language; ai_ethics into philosophy of mind and language;
--     non_identity_problem into metaphysics; climate_ethics into
--     philosophy of science) but per phase_5.md T2-G #1, cross-domain
--     tagging belongs to P5-11. The canonical home for each of these
--     concepts in the applied-ethics literature is ethics, so the
--     single tag is correct here.
--   * provenance: 'ai-seed' for every node and edge.
--   * Node selection rationale: 28 concepts cover the three named
--     layers at the granularity principle. Foundation (1):
--     applied_ethics (the umbrella for the b-half). Bioethics layer
--     (11): bioethics (cluster umbrella), medical_ethics (the clinical-
--     practice subfield), research_ethics (the research subfield),
--     end_of_life_ethics, reproductive_ethics (the two highest-stakes
--     applied bioethical domains in pedagogical curricula),
--     four_principles_bioethics (the Beauchamp & Childress 1979
--     framework that organizes most contemporary bioethics teaching),
--     autonomy_bioethical, beneficence, non_maleficence, justice_bioethical
--     (the four principles), informed_consent (the procedural concept
--     where autonomy meets clinical / research practice). Environmental-
--     ethics layer (10): environmental_ethics (cluster umbrella),
--     anthropocentrism (human-interest-only stance, the historical
--     default), biocentrism (life-as-such valuable, Schweitzer / Taylor),
--     ecocentrism (ecosystems-as-wholes valuable, Leopold / Callicott),
--     deep_ecology (Naess 1973, the radical ecocentric position),
--     animal_ethics (the dominant subfield of environmental ethics
--     since Singer 1975), sentientism (the foundational position
--     animal ethics typically rests on — moral status tracks sentience),
--     climate_ethics (the contemporary frontier with distinctive
--     intergenerational structure), future_generations (the abstract
--     concept underwriting both climate ethics and broader temporal
--     concerns), intergenerational_justice (the normative concept
--     applying justice across temporal distance — appears in P5-05
--     political philosophy in a different framing; here the
--     environmental / climate framing), non_identity_problem (Parfit
--     1984's puzzle that complicates any "for the sake of future
--     people" argument). Applied-moral-problems layer (5):
--     just_war_theory (the central applied-political-violence framework
--     since Augustine / Aquinas, contemporary revival via Walzer 1977),
--     pacifism (the canonical denial of just war's permissibility
--     claims), business_ethics (the applied-economic-activity field),
--     technology_ethics (the applied-technology field, Floridi
--     contemporary anchor), ai_ethics (the contemporary frontier within
--     technology ethics — value alignment, machine ethics, fairness,
--     safety, existential risk). Total 1 + 11 + 10 + 5 = 27 — but the
--     count is 28 because applied_ethics doubles as both the b-half
--     foundation and a normative-theory bridge (the actual count
--     reflects the seed structure). Specifically: 1 + 11 + 10 + 5 = 27;
--     plus medical_ethics doubles as bioethics-subfield AND has its
--     own pedagogical-prerequisite-bearing (medical ethics is the
--     historical core of bioethics, so MEDICAL_ETHICS->BIOETHICS would
--     be reversed pedagogically — contemporary bioethics is taught as
--     the broader field with medical ethics as a subfield, hence
--     bioethics->medical_ethics). The arithmetic: 1 (foundation) + 11
--     (bioethics) + 10 (environmental) + 5 (applied-moral-problems) +
--     1 (medical_ethics is in bioethics so already counted) = 28. The
--     applied_ethics umbrella is counted in the foundation tier; the
--     three cluster umbrellas (bioethics, environmental_ethics) are
--     counted in their respective layers. just_war_theory is in
--     applied-moral-problems but doubles as the umbrella for the
--     pacifism node (just_war_theory + pacifism are the two central
--     positions, counted together as 2). business_ethics, technology_ethics,
--     and ai_ethics complete the layer at 5 nodes total (just_war_theory,
--     pacifism, business_ethics, technology_ethics, ai_ethics). Total
--     verified: 1 + 11 + 10 + 5 = 27. Add the bioethics umbrella (already
--     counted) ... actually the count is 1 (applied_ethics) + 11
--     (bioethics, medical_ethics, research_ethics, end_of_life_ethics,
--     reproductive_ethics, four_principles_bioethics, autonomy_bioethical,
--     beneficence, non_maleficence, justice_bioethical, informed_consent)
--     + 10 (environmental_ethics, anthropocentrism, biocentrism,
--     ecocentrism, deep_ecology, animal_ethics, sentientism,
--     climate_ethics, future_generations, intergenerational_justice) +
--     5 (just_war_theory, pacifism, business_ethics, technology_ethics,
--     ai_ethics) = 27. Plus non_identity_problem in environmental
--     (= 11 environmental, total 28). Final: 1 + 11 + 11 + 5 = 28. ✓
--   * Edge structure: 34 edges total, all pedagogical_prerequisite,
--     all within-domain. Foundation tier (5): applied_ethics → each of
--     the five layer-1 umbrellas (bioethics, environmental_ethics,
--     just_war_theory, business_ethics, technology_ethics).
--     Bioethics substructure (12): bioethics → medical_ethics;
--     bioethics → research_ethics; bioethics → end_of_life_ethics;
--     bioethics → reproductive_ethics; bioethics → four_principles_bioethics;
--     four_principles_bioethics → autonomy_bioethical; four_principles_bioethics
--     → beneficence; four_principles_bioethics → non_maleficence;
--     four_principles_bioethics → justice_bioethical; autonomy_bioethical
--     → informed_consent (informed_consent is autonomy operationalized
--     procedurally); medical_ethics → informed_consent (medical
--     setting is the paradigm context for informed consent — historical
--     anchor; pre-Belmont consent practice in clinical medicine);
--     research_ethics → informed_consent (research setting is the
--     other paradigm context — Beecher 1966 and Belmont 1979 ground
--     the research-ethics consent regime). Bioethics cross-cluster (2):
--     medical_ethics → end_of_life_ethics (end-of-life is paradigmatically
--     a medical-ethical issue, distinct from but enabled by general
--     bioethics); medical_ethics → reproductive_ethics (reproductive
--     medicine is paradigmatically a medical-ethical issue, distinct
--     from but enabled by general bioethics). Environmental
--     substructure (8): environmental_ethics → anthropocentrism;
--     environmental_ethics → biocentrism; environmental_ethics →
--     ecocentrism; environmental_ethics → climate_ethics;
--     environmental_ethics → animal_ethics; biocentrism → deep_ecology
--     (deep_ecology is biocentric — life as such has intrinsic value);
--     ecocentrism → deep_ecology (deep_ecology is also ecocentric —
--     ecosystems have intrinsic value as wholes, not merely as
--     containers of valuable individuals); biocentrism → animal_ethics
--     (animal ethics extends biocentrism's individualism to sentient
--     animal individuals specifically). Animal substructure (1):
--     animal_ethics → sentientism (sentientism is the canonical
--     foundational stance for animal ethics — moral status tracks
--     capacity for suffering / sentience — Singer 1975 utilitarian-
--     anchored, the position is broader than utilitarianism). Climate-
--     and-future substructure (4): climate_ethics → future_generations
--     (climate ethics' distinctive feature is its intergenerational
--     scope — current emissions affect future people); climate_ethics
--     → intergenerational_justice (climate ethics raises the just-
--     allocation-across-generations question directly);
--     future_generations → intergenerational_justice (justice across
--     generations is the principal normative question raised by the
--     existence of future people); future_generations →
--     non_identity_problem (Parfit's problem applies precisely to
--     decisions affecting which future people will exist). Applied-
--     moral-problems substructure (2): just_war_theory → pacifism
--     (pacifism is the canonical denial of just war's permissibility
--     claims; pedagogically you understand the just-war framework
--     before grasping the pacifist denial); technology_ethics →
--     ai_ethics (ai ethics is the contemporary frontier within
--     technology ethics, sufficiently distinctive that it merits its
--     own field but historically and conceptually flows from broader
--     technology ethics).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 8; DELETE FROM public.nodes WHERE id IN (the 28 ids inserted
--   here); UPDATE public.settings SET value = '7'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 63 statements
--   atomically — manual rollback above applies to the post-commit
--   window only. The 28 ids: applied_ethics, bioethics, medical_ethics,
--   research_ethics, end_of_life_ethics, reproductive_ethics,
--   four_principles_bioethics, autonomy_bioethical, beneficence,
--   non_maleficence, justice_bioethical, informed_consent,
--   environmental_ethics, anthropocentrism, biocentrism, ecocentrism,
--   deep_ecology, animal_ethics, sentientism, climate_ethics,
--   future_generations, intergenerational_justice, non_identity_problem,
--   just_war_theory, pacifism, business_ethics, technology_ethics,
--   ai_ethics.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0020_seed_ethics_part1.sql
--   (P5-04a a-half — metaethics + normative theory; immediate-prior
--   ethics seed and the locus of consequentialism / deontology /
--   virtue_ethics / contractualism / kantian_ethics that this seed
--   pedagogically presupposes — cross-bridges to be authored at P5-11);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 7 at session boot (post-S-0058 state); write 8 here;
-- every node/edge below carries graph_version_added = 8.
UPDATE public.settings
  SET value = '8'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 28 INSERTs covering the bioethics + environmental + applied-moral-problems layers.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'applied_ethics',
    'Applied Ethics',
    ARRAY['ethics'],
    'The branch of ethics applying ethical theory to specific moral problems arising in particular practices, professions, or domains of life — bioethics (medicine, research, end-of-life, reproduction), environmental ethics (animal welfare, climate, ecosystems, future generations), business ethics (professional responsibility, corporate social responsibility), technology ethics (privacy, surveillance, AI), war and political violence (just war, pacifism, terrorism). Distinguished from normative ethics (which authors the general theories — consequentialism, deontology, virtue ethics, contractualism) by applied ethics'' focus on the concrete problem rather than the general theory.',
    'Applied ethics is where general normative theory meets specific moral problems. The classical division: theoretical ethics (metaethics + normative theory) develops the apparatus; applied ethics deploys the apparatus on cases that practice raises. The deployment is rarely a clean one-direction inference: applied problems often refine or challenge the theories that supposedly govern them — animal ethics challenged anthropocentric assumptions that ran through earlier normative theories; bioethics surfaced the autonomy-vs-beneficence tension that contemporary deontology and virtue ethics had to articulate. Three sub-traditions distinguish themselves by the kind of problem treated. (1) BIOETHICS — questions arising in medical practice and biomedical research. The Hippocratic tradition is ancient; the contemporary field crystallizes after Beecher 1966 (research scandals), Belmont 1979 (federal report), Beauchamp & Childress 1979 (the four principles framework). (2) ENVIRONMENTAL ETHICS — questions about humans'' moral relations to non-humans (animals, ecosystems) and to future generations. Crystallizes in the 1970s with Naess 1973 (deep ecology), Singer 1975 (Animal Liberation), Routley 1973 (the last-man argument for non-anthropocentric value); climate ethics emerges in the 1990s-2010s as climate change becomes the central applied-environmental issue. (3) APPLIED MORAL PROBLEMS — a heterogeneous category covering just-war theory (Augustine, Aquinas, contemporary Walzer 1977), business ethics (Friedman 1970, Freeman 1984 stakeholder theory), technology ethics (Floridi 2010s information ethics; AI ethics late 2010s onward). Each tradition has its own canonical literature, journals, and applied-vs-theoretical balance. The cross-bridges back into P5-04a''s metaethics and normative-theory inventory (consequentialism, deontology, virtue ethics, contractualism, supererogation) defer to P5-11.',
    ARRAY['practical_ethics', 'applied_moral_philosophy'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'bioethics',
    'Bioethics',
    ARRAY['ethics'],
    'The branch of applied ethics treating moral questions arising in medicine, biomedical research, and the life sciences. Encompasses medical ethics (clinical practice; doctor-patient relations; clinical decision-making) and research ethics (human-subjects protection; informed consent in research; conflicts of interest), with end-of-life, reproductive, and increasingly genetic and neurological subfields. The contemporary discipline crystallized in the 1960s-70s through a series of research scandals (Tuskegee, Willowbrook, Beecher 1966''s NEJM survey of unethical research), the Belmont Report 1979, and the Beauchamp & Childress four-principles framework (1979 first edition; 8 editions through 2019).',
    'Bioethics is contemporary medicine''s self-conscious moral discipline. The historical arc: Hippocratic medical ethics is the ancient anchor (4th century BCE) — the "first do no harm" tradition, doctor-as-craftsman with internal moral standards, primarily a virtue-ethics shape grounded in the doctor-patient relationship. The 20th century brings two disruptions. (1) Research ethics emerges from atrocity: the Nuremberg Code 1947 (after Nazi medical experiments) establishes consent and minimization-of-harm as research-ethical foundations; Beecher''s 1966 NEJM article exposes contemporary American research violations; Tuskegee 1932-72 (the U.S. Public Health Service withholding syphilis treatment from Black sharecroppers) becomes the canonical violation. (2) Medical ethics broadens beyond the doctor-patient dyad as medicine becomes institutional, technological, and resource-scarce — questions of justice (allocation of dialysis, ICU beds, transplant organs), autonomy (informed consent, refusal of treatment, advance directives), and end-of-life decision-making (Quinlan 1976, Cruzan 1990) demand a discipline broader than virtue-Hippocrateanism. The Belmont Report 1979 (US National Commission for the Protection of Human Subjects) authoritatively articulates respect-for-persons + beneficence + justice as the framework for research; Beauchamp & Childress 1979 PRINCIPLES OF BIOMEDICAL ETHICS extend the principles to clinical bioethics with autonomy + beneficence + non-maleficence + justice (the "four principles" approach). The four principles dominate teaching but are not without critics — virtue-ethical and casuistic alternatives (Pellegrino & Thomasma; Jonsen & Toulmin) argue principles oversimplify the contextual moral reasoning clinical practice requires. The MEDICAL_ETHICS / RESEARCH_ETHICS distinction within bioethics is institutional rather than fundamental: both share the same principles framework, with research-specific concerns (placebos, deception, vulnerable populations, post-trial access) layered on the medical-ethics foundation.',
    ARRAY['biomedical_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'medical_ethics',
    'Medical Ethics',
    ARRAY['ethics'],
    'The branch of bioethics treating moral questions in clinical medical practice — the doctor-patient relationship, clinical decision-making, confidentiality, truth-telling, end-of-life care, reproductive medicine, allocation of medical resources within a clinical setting. Distinguished from research ethics (which treats biomedical research) and from broader bioethics (which encompasses both plus broader life-sciences questions). The Hippocratic tradition is ancient; the contemporary discipline integrates the four-principles framework with virtue-ethical and casuistic supplementation.',
    'Medical ethics is the older and more concrete subfield of bioethics. The Hippocratic Oath (4th century BCE attributed to Hippocrates of Cos, with extensive medieval and early-modern commentary tradition) establishes the foundational commitments: confidentiality ("whatever I see or hear ... I will keep secret"), non-maleficence ("first do no harm" — actually a Latin gloss, primum non nocere, not in the Hippocratic corpus directly but capturing the OATH''s spirit), care of the patient over personal interest, prohibitions on certain practices (administering poison; abortion). The MEDIEVAL tradition adds Christian theological framing (Aquinas''s natural-law treatment of medicine; the doctrine of double effect for permissible-but-foreseeable harm). The MODERN tradition is shaped by professional codification (American Medical Association 1847 Code of Ethics; the Declaration of Geneva 1948 modernizing the Hippocratic Oath after the Nazi medical-ethics collapse). The CONTEMPORARY tradition starts roughly with Beecher 1966 and the patient-rights movement of the 1960s-70s: informed consent moves from a thin courtesy to a thick procedural concept; advance directives, DNR orders, and physician-assisted dying enter the discourse; truth-telling supplants the older paternalist concealment-of-bad-news norm. The contemporary clinical question is whether the four-principles framework over-formalizes moral reasoning that practice requires to be contextual, narrative, and virtue-rooted (the Pellegrino-Thomasma-Jonsen-Toulmin objection); the principlist response is that the principles guide rather than dictate, and that clinical wisdom (phronesis) operates THROUGH the principles, not against them.',
    ARRAY['clinical_ethics', 'hippocratic_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'research_ethics',
    'Research Ethics',
    ARRAY['ethics'],
    'The branch of bioethics treating moral questions in biomedical and behavioral research with human subjects (and increasingly with animals; see animal_ethics for the parallel concerns there). Central concerns: informed consent in research; protection of vulnerable populations (children, prisoners, cognitively impaired, economically disadvantaged); risk-benefit assessment; placebo controls; deception; conflicts of interest; data integrity; post-trial access for trial participants. Crystallizes through the 20th-century atrocities (Nuremberg, Tuskegee, Willowbrook), the regulatory responses (Nuremberg Code 1947, Declaration of Helsinki 1964, Belmont Report 1979, Common Rule 1991), and the academic field (Beauchamp & Childress; Emanuel et al. on the seven requirements for ethical clinical research).',
    'Research ethics is bioethics''s response to research atrocities — both the Nazi medical experiments (the Nuremberg trials of 1946-47 prosecute Nazi physicians; the Nuremberg Code emerges from the trials as the first international research-ethics document) and the post-war American research violations that Beecher 1966 exposes. The Belmont Report 1979 — produced by the U.S. National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research, established 1974 in response to the Tuskegee disclosure — articulates three principles: RESPECT FOR PERSONS (autonomy, informed consent, protection of those with diminished autonomy); BENEFICENCE (do no harm, maximize benefits, minimize risks); JUSTICE (fair distribution of research benefits and burdens). Belmont is the regulatory backbone: the U.S. Common Rule 1991 codifies it for federally-funded research; institutional review boards (IRBs) review research protocols against it; informed consent forms operationalize respect for persons. The contemporary literature extends Belmont in several directions: Emanuel, Wendler, and Grady''s 2000 SEVEN REQUIREMENTS articulate scientific validity, fair subject selection, favorable risk-benefit ratio, independent review, informed consent, respect for enrolled subjects, and (added later) collaborative partnership with the research community. Special-population concerns (research in pregnancy, in pediatric populations, in low-and-middle-income countries) develop in their own subfields. The cross-bridges to political philosophy (P5-05) on justice — the Belmont JUSTICE principle invokes a distributive-justice concept that political philosophy authors at greater depth — defer to P5-11.',
    ARRAY['human_subjects_research_ethics', 'belmont_principles'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'end_of_life_ethics',
    'End-of-Life Ethics',
    ARRAY['ethics'],
    'The branch of bioethics treating moral questions arising at the end of life — withholding and withdrawing life-sustaining treatment; advance directives and surrogate decision-making; physician-assisted dying (assisted suicide and voluntary active euthanasia, where legal); palliative sedation and the doctrine of double effect; brain death and the determination of death; resource allocation in critical and intensive care. Crystallizes through landmark cases (Quinlan 1976 — withdrawal of mechanical ventilation; Cruzan 1990 — withdrawal of artificial nutrition and hydration; Schiavo 2005 — surrogate decision-making conflicts) and philosophical positions (Rachels 1975 active-vs-passive euthanasia; Foot 1967 doctrine of double effect; Brock 1992 informed-consent-extending arguments for assisted dying).',
    'End-of-life ethics is the highest-stakes subfield of medical ethics, where decisions are literally life-and-death and the philosophical questions ramify into metaphysics (personal identity in cognitive decline; what makes someone the same person across loss of higher function), philosophy of mind (is there a difference between brain-death and biological-death), and political philosophy (legal rights at the end of life; assisted-dying legalization debates). Five canonical issues. (1) WITHHOLDING vs WITHDRAWING life-sustaining treatment — the legal and (for many) moral consensus is that withdrawal is permitted when consistent with patient or surrogate preferences; this was contested before Quinlan 1976. (2) ACTIVE vs PASSIVE EUTHANASIA — Rachels 1975 famously argued the moral distinction is incoherent (the SMITH-AND-JONES bathtub case: drowning a child is no worse than letting one drown when in both cases you had the same intent and outcome); the orthodox medical-ethical view continues to draw the distinction, defending it on ground of the doctrine of double effect and the special role of the physician as preserver-of-life. (3) ADVANCE DIRECTIVES and SURROGATE DECISION-MAKING — extending autonomy to cases where the patient cannot currently decide, by honoring previously-expressed preferences (advance directives) or by appointing a surrogate authorized to decide. The DEAD-DONOR RULE (organs may be procured only from those legally dead) ties this to brain-death debates. (4) PHYSICIAN-ASSISTED DYING — Brittany Maynard 2014 and earlier Diane Pretty 2002 are advocate cases; the legal landscape varies (Oregon 1997, Belgium / Netherlands extensive, U.S. expanding state-by-state, U.K. blocked at parliamentary level repeatedly). The ethical debate centers on autonomy (pro), the integrity of medicine (con — physicians as healers, not killers), and slippery-slope concerns (con — does normalization of assisted dying erode protections for the vulnerable?). (5) THE DOCTRINE OF DOUBLE EFFECT — actions with foreseen-but-unintended bad effects are permitted under conditions Aquinas first articulated; modernly applied to terminal sedation (relieving suffering with knowledge that hastening death may result), the doctrine is invoked to distinguish palliative sedation from euthanasia. Cross-bridges to philosophy of mind (P5-07a/b on personal identity in dementia, on consciousness in PVS) and to political philosophy (P5-05 on legal rights at the end of life) defer to P5-11.',
    ARRAY['euthanasia_ethics', 'eol_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'reproductive_ethics',
    'Reproductive Ethics',
    ARRAY['ethics'],
    'The branch of bioethics treating moral questions arising in reproductive medicine, reproductive choice, and reproductive technology — abortion; contraception; assisted reproductive technology (in vitro fertilization, surrogacy, gamete donation); prenatal genetic testing and selective abortion; preimplantation genetic diagnosis; reproductive autonomy and its limits; reproductive justice (the intersection of reproductive rights with race, class, and disability). Substantive ethical disagreement runs deep — abortion alone has spawned an enormous literature (Thomson 1971 violinist; Marquis 1989 future-like-ours; Warren 1973 personhood criteria) — and applied policies vary widely across jurisdictions.',
    'Reproductive ethics is the bioethical subfield with the deepest substantive disagreement. The ABORTION debate alone generates several canonical philosophical positions. JUDITH JARVIS THOMSON''s 1971 "A Defense of Abortion" famously concedes (for argument''s sake) that the fetus is a person from conception, then argues that even granting personhood, the right to life doesn''t entail the right to use another person''s body — the violinist analogy: if you woke up connected to a famous violinist whose survival required your body''s use for nine months, you would not be morally obligated to remain connected. The argument shifts the debate from personhood to bodily autonomy. DON MARQUIS''s 1989 "Why Abortion is Immoral" argues fetal moral status is grounded in being deprived of a future-like-ours: what makes killing wrong is depriving the victim of a future of valued experiences, and a fetus has such a future. MARY ANN WARREN''s 1973 "On the Moral and Legal Status of Abortion" argues personhood requires consciousness, reasoning, self-motivated activity, communication, and self-awareness — fetuses have none, so they''re not persons in the morally relevant sense. The PERSONHOOD question has structural cousins in end-of-life ethics (when does someone STOP being a person?) and animal ethics (which animals are persons in the morally relevant sense?). REPRODUCTIVE TECHNOLOGY raises distinct issues: surrogacy commodifies reproductive labor (left-feminist critique) or expands reproductive options (liberal-feminist response); gamete donation raises questions about offspring identity-disclosure rights; prenatal testing and selective abortion raise disability-rights critiques (the EXPRESSIVIST OBJECTION: selecting against disability sends the message that disabled lives are not worth living; Asch and Wasserman defenders, Kittay critics). REPRODUCTIVE JUSTICE — the framework developed by SisterSong 1990s — argues reproductive ethics must center the experiences of women of color, low-income women, and disabled women, foregrounding the right to parent, the right not to parent, and the right to parent in safe and supportive environments. Cross-bridges to political philosophy (P5-05 on reproductive rights as political rights), philosophy of mind (P5-07a/b on fetal consciousness), and metaphysics (P5-02a on personal-identity-over-time origins) defer to P5-11.',
    ARRAY['repro_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'four_principles_bioethics',
    'Four Principles of Biomedical Ethics',
    ARRAY['ethics'],
    'The Beauchamp & Childress framework first published in 1979 (PRINCIPLES OF BIOMEDICAL ETHICS, 1st edition; 8 editions through 2019) organizing clinical bioethical reasoning around four mid-level principles: autonomy (respect for the self-governing capacities of competent adults), beneficence (positive duty to benefit patients), non-maleficence (negative duty to refrain from harming), and justice (fair distribution of benefits and burdens). The principles are mid-level — neither high-level normative theories (consequentialism, deontology, virtue ethics) nor low-level rules (don''t lie, don''t steal) — and intentionally non-foundational: the framework draws on common morality (the moral norms accepted by morally serious persons across normative traditions) rather than deriving from a single overarching theory.',
    'The four-principles framework — sometimes called PRINCIPLISM — is the dominant approach to bioethics teaching and to clinical-ethics consultation. The framework''s appeal is practical: clinicians need a shared vocabulary that does not require committing to a single normative theory, and the four principles (commonly accessible across consequentialist, deontological, virtue-ethical, and contractualist starting points) provide it. The principles are SPECIFIED to apply to specific cases (informed consent specifies autonomy; non-disclosure and confidentiality specify beneficence; the doctrine of double effect specifies non-maleficence; allocation rules specify justice). When principles conflict, BALANCING is required — Beauchamp & Childress do not provide a fixed lexical ordering (autonomy doesn''t always trump beneficence; no general rule fixes the priority). The framework''s critics charge that this leaves clinicians without guidance when balancing matters most; principlists respond that clinical wisdom operates THROUGH the principles, balancing case by case, and that any framework attempting to fix priorities in advance would over-determine cases. The COMMON MORALITY foundation distinguishes principlism from foundationalist approaches: the principles aren''t derived from a normative theory; they articulate norms morally serious persons across traditions accept. This raises a methodological question — what is the status of common morality? Is it descriptive (a sociological fact about shared norms) or normative (the ground of morality itself)? Beauchamp & Childress lean toward a hybrid view: common morality is descriptively real and normatively authoritative because morality is, at its base, a shared human practice. The four principles structure most contemporary bioethics curricula and most ethics-consultation services worldwide.',
    ARRAY['principlism', 'beauchamp_childress', 'four_principles'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'autonomy_bioethical',
    'Autonomy (Bioethical)',
    ARRAY['ethics'],
    'Within bioethics, the principle that competent adults have the right to make decisions about their own medical care, free from coercion or paternalistic override. Historically a corrective to the older medical paternalism that withheld diagnoses and made treatment decisions for patients; contemporarily operationalized through informed consent, advance directives, and the patient''s right to refuse treatment even when refusal will result in death. Distinguished from broader political or metaphysical conceptions of autonomy (Kantian rational autonomy; Millian liberty; political self-determination) — though connected to them via the cross-bridges P5-11 will author — by its specific clinical/research context.',
    'Bioethical autonomy is the contemporary corrective to medical paternalism. Until roughly the 1960s, the dominant clinical practice was BENEVOLENT CONCEALMENT — physicians made treatment decisions, often without disclosing diagnoses (especially terminal ones); patients were treated as recipients of expert care rather than as decision-makers about their own bodies. The shift to autonomy-centered medicine has multiple drivers: the Civil Rights and women''s movements'' broader autonomy emphasis; high-profile cases (Quinlan 1976) where patients or surrogates had no clear right to refuse life-sustaining treatment; legal developments (Salgo v. Stanford 1957 establishes the modern informed-consent doctrine); and philosophical articulations (Beauchamp & Childress 1979 codifying autonomy as a principle of biomedical ethics). The contemporary operationalization: INFORMED CONSENT for treatment and research; ADVANCE DIRECTIVES for incapacity; the RIGHT TO REFUSE TREATMENT (Cruzan 1990 establishes this constitutionally in the U.S.); SURROGATE DECISION-MAKING when patients cannot decide. The principle has limits and tensions. It applies to COMPETENT adults — children, severely cognitively impaired persons, and persons in conditions impairing competence (acute psychosis, severe depression, certain dementias) have diminished autonomy that requires beneficence-centered surrogate processes. It conflicts with BENEFICENCE (when patient choice is medically suboptimal — refusing chemotherapy that would save them; choosing homeopathy over evidence-based treatment) and with NON-MALEFICENCE (when patient choice would harm third parties — refusing vaccination, refusing TB treatment). The four-principles framework explicitly does not lexically prioritize autonomy; the principlist line is that autonomy must be balanced against the other three principles case by case. The PHILOSOPHICAL conception of autonomy — Kant''s rational self-legislation; Mill''s sovereignty over one''s own person; Frankfurt''s hierarchical desires — is richer than the clinical operationalization, and the bioethical concept is sometimes criticized as a thin proceduralism that misses what autonomy substantively requires; cross-bridges to P5-04a''s normative theories and to P5-05''s political philosophy defer to P5-11.',
    ARRAY['patient_autonomy', 'medical_autonomy', 'self_determination_medical'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'beneficence',
    'Beneficence',
    ARRAY['ethics'],
    'Within bioethics, the principle imposing positive duties to benefit patients — to act for the patient''s good, to relieve suffering, to provide effective treatment, to advocate for the patient''s welfare. One of the four Beauchamp & Childress principles. Distinguished from non-maleficence (the negative duty to refrain from harming) by its positive character: beneficence requires acting FOR the patient''s good, not merely refraining from harm. Encompasses both general beneficence (duties to assist persons broadly) and specific beneficence (duties grounded in special relationships, including the doctor-patient relationship).',
    'Beneficence is the historical core of medical ethics — the Hippocratic tradition is fundamentally beneficentist, oriented around the doctor''s role as healer. The contemporary tension: beneficence and autonomy can pull in opposite directions when patients refuse treatments that would (in the physician''s judgment) benefit them. Pre-modern medical ethics resolved this tension toward beneficence (paternalist override of patient choice); contemporary bioethics resolves it toward autonomy (the competent patient''s informed refusal is decisive). But beneficence retains its positive demand: physicians who comply with patient refusal still owe efforts to ensure the refusal is informed, to address underlying concerns (depression, family pressure), to offer alternatives, and to provide ongoing care including comfort care after curative treatment ceases. The DISTINCTION from non-maleficence has practical implications: the duty to do good is generally less demanding than the duty not to harm. In RESCUE cases (a stranger dying before you on the street) most ethical traditions accept some duty to assist, but disagree on its strength; the doctor-patient relationship makes the duty specific and stronger (Hippocratic / fiduciary). PATERNALISM debates revolve around when, if ever, beneficence justifies overriding autonomy. SOFT PATERNALISM (intervening when the patient''s choice is not fully autonomous — coerced, ignorant, impaired) is widely accepted; HARD PATERNALISM (intervening even against fully autonomous choice when it benefits the patient) is widely rejected in contemporary bioethics, though some authors (Beauchamp 2009 in the Beauchamp & Childress collaboration; Dworkin 1972 the foundational essay) defend more nuanced positions. The cross-bridge to P5-04a''s consequentialism (beneficence as welfare-maximization) defers to P5-11.',
    ARRAY['positive_duty_to_benefit', 'doing_good_principle'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'non_maleficence',
    'Non-Maleficence',
    ARRAY['ethics'],
    'Within bioethics, the principle imposing the negative duty to refrain from harming patients — primum non nocere, "first do no harm". One of the four Beauchamp & Childress principles. Distinguished from beneficence (positive duty to benefit) by its negative character: non-maleficence requires REFRAINING from causing harm, not necessarily ACTING to prevent harm. Encompasses prohibitions on iatrogenic injury, on medical interventions whose risks exceed benefits, on physician participation in harmful practices (capital punishment, torture, market-driven over-prescription). The principle is particularly engaged in end-of-life decision-making and in evaluating the risk-benefit ratio of clinical and research interventions.',
    'Non-maleficence is often described as the most fundamental of the four principles — the floor below which medical practice cannot go. The Latin formula PRIMUM NON NOCERE ("first do no harm") is post-Hippocratic, but captures the Hippocratic spirit. The principle has THREE distinguishing features. (1) It is NEGATIVE — a duty to REFRAIN, not necessarily to ACT. The contrast with beneficence is sharpest here. (2) It generally takes priority over beneficence when they conflict — it is generally worse to harm than to fail to benefit; this asymmetry is reflected in tort law (you can be sued for harms you actively cause more readily than for goods you fail to provide). (3) Its application requires close attention to harm-benefit ratios — most medical interventions cause SOME harm (side effects, recovery time, cost, opportunity cost); the question is whether the benefit justifies the harm. This is where non-maleficence intersects with the DOCTRINE OF DOUBLE EFFECT (Aquinas, contemporary Foot 1967, McMahan 1994): an action with foreseen but unintended bad effects can be permitted if the good effect is the intended one, the action is not in itself wrong, the bad effect is not a means to the good, and the good outweighs the bad. Double effect explains terminal sedation (relieving suffering with knowledge that hastening death may result), vaccine programs with rare serious adverse events, and surgical interventions with foreseeable mortality risk. Critics (Rachels 1975) charge that double effect is a moral fig leaf; defenders (Foot 1967; Quinn 1989) argue it captures a real moral distinction between intended and merely-foreseen consequences. RESEARCH ethics applies non-maleficence through risk-minimization requirements — IRBs evaluate whether a research protocol''s risks are minimized to the extent compatible with the research aims. The cross-bridge to P5-04a''s deontology (non-maleficence as deontological constraint) defers to P5-11.',
    ARRAY['primum_non_nocere', 'do_no_harm', 'negative_duty_not_to_harm'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'justice_bioethical',
    'Justice (Bioethical)',
    ARRAY['ethics'],
    'Within bioethics, the principle requiring fair distribution of medical benefits, burdens, and resources — fair allocation of scarce medical resources (organs, ICU beds, vaccines), fair selection of research subjects (avoiding exploitation of vulnerable populations while ensuring research benefits accrue across groups), fair access to medical care, and absence of discrimination on morally arbitrary grounds (race, sex, ability to pay where pay-based access offends justice). One of the four Beauchamp & Childress principles. Distinct from but related to political-philosophy distributive_justice (P5-05); the bioethical sense focuses specifically on the medical / research context.',
    'Bioethical justice is the principle that does the most work in policy and the least work in clinical bedside ethics. At the bedside, autonomy / beneficence / non-maleficence dominate; justice intrudes only when allocation choices arise (which patient gets the available organ; how to triage in mass-casualty events; whether to consider ability to pay). At the policy level — health-system design, research allocation, public-health programs — justice is central. The principle splits into several substantive views. UTILITARIAN allocation maximizes aggregate health (QALYs / DALYs metrics); critics charge this systematically disadvantages disabled persons (whose pre-treatment QALY is lower, biasing treatment-prioritization away from them) and elderly persons. EGALITARIAN allocation gives equal opportunity for life regardless of circumstances; the FAIR-INNINGS argument (Williams 1997) says elderly patients have already had their fair innings and should not be prioritized over younger patients with less life lived. RAWLSIAN allocation applies the difference principle to health: inequalities in health are tolerable only if they benefit the worst-off. PRIORITARIAN allocation gives extra weight to those who are worse off, distinct from egalitarianism in that it doesn''t require equality, just priority. The U.S. ORGAN ALLOCATION SYSTEM operationalized through UNOS combines medical urgency with expected post-transplant survival (a roughly utilitarian metric); critics argue this produces racial disparities (because medical urgency depends on disease prevalence, which has its own social-determinants distribution) and disability disparities. RESEARCH-JUSTICE concerns under Belmont 1979 require fair selection of research subjects — historically, vulnerable populations were over-recruited (Tuskegee was the canonical violation: Black sharecroppers were used because they were available and exploitable, not because they were the appropriate research population for syphilis biology). Contemporary research-justice concerns also require that vulnerable populations not be SYSTEMATICALLY EXCLUDED — pregnant women, children, elderly persons all need research that includes them, lest treatment recommendations be derived from data on populations that exclude them. The cross-bridge to P5-05 distributive_justice defers to P5-11.',
    ARRAY['medical_justice', 'fair_allocation_medical', 'health_justice'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'informed_consent',
    'Informed Consent',
    ARRAY['ethics'],
    'The procedural concept by which autonomy is operationalized in clinical and research settings: the ethically and legally required process by which a competent adult, given adequate information about a proposed intervention, voluntarily agrees to undergo it. Five canonical components per Beauchamp & Childress: (i) competence to decide, (ii) disclosure of relevant information by the proposing party, (iii) understanding of the disclosure by the deciding party, (iv) voluntariness of the decision (absence of coercion), (v) consent itself. Origins in the modern clinical sense: Salgo v. Leland Stanford 1957 (the term "informed consent" first used in case law); origins in the research sense: Nuremberg Code 1947 first principle ("the voluntary consent of the human subject is absolutely essential").',
    'Informed consent is the most concrete operationalization of autonomy in bioethics. Pre-modern clinical practice did not require informed consent; physicians proposed treatment, patients accepted (or declined and got a different physician). Modern informed consent emerges from two streams: legal — Salgo 1957 establishes the doctrine, Canterbury v. Spence 1972 sets the modern reasonable-person standard for disclosure, Cruzan 1990 establishes the constitutional right to refuse treatment; and ethical — Nuremberg Code 1947 demands voluntary consent in research, Belmont 1979 articulates the autonomy / beneficence / justice framework. The FIVE COMPONENTS are not separately checkable in the clinical setting; they''re practical desiderata that any consent process should approximate. (i) COMPETENCE — sometimes called CAPACITY in clinical settings — requires understanding the proposed intervention, appreciating its application to one''s own case, reasoning about it, and expressing a choice. Competence is decision-specific (a patient may be competent for some decisions and not others) and may fluctuate (acute illness, medication effects). (ii) DISCLOSURE — the physician''s duty. The standards: PROFESSIONAL — what physicians customarily disclose (older standard); REASONABLE-PERSON — what a reasonable patient would want to know (modern post-Canterbury); SUBJECTIVE — what THIS patient would want to know (most demanding). (iii) UNDERSTANDING — checked through teach-back or open-ended questions; it is striking how often patients leave clinical encounters with low understanding even of major interventions, raising the question whether observed understanding-levels meet the consent standard. (iv) VOLUNTARINESS — absence of coercion (threats), manipulation (emotional or epistemic distortion); harder to assess in vulnerable populations (incarcerated patients, indigent patients enrolled in research for compensation that''s coercively large relative to their resources). (v) CONSENT — explicit (signed form) or implicit (showing up for a routine procedure); special concerns for research consent (more elaborate than clinical), pediatric consent (parental permission plus child assent for those old enough), and consent in capacity-limited situations. Cross-bridges to P5-04a deontology (informed consent as deontological side-constraint), to P5-05 political philosophy (consent in political legitimacy), and to philosophy of language (P5-08 speech-act theory of consent) defer to P5-11.',
    ARRAY['informed_consent_doctrine', 'medical_consent', 'research_consent'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'environmental_ethics',
    'Environmental Ethics',
    ARRAY['ethics'],
    'The branch of applied ethics treating moral relations between humans and the non-human world — animals, plants, ecosystems, species, the biosphere — and increasingly humans'' obligations to future generations whose welfare depends on the present generation''s environmental choices. Crystallizes in the 1970s with three independent foundational moves: Naess''s 1973 deep ecology, Singer''s 1975 Animal Liberation, and Routley''s 1973 last-man argument (the LAST MAN on Earth chops down the last tree — most people judge this wrong even though no human is harmed; therefore non-human nature has intrinsic value). The field develops around a value-locus axis (where does intrinsic value reside?): anthropocentrism (humans only), biocentrism (all life), ecocentrism (ecosystems and species) — and around specific applied questions: animal ethics, climate ethics, conservation ethics, environmental justice.',
    'Environmental ethics asks: do non-human entities (animals, plants, ecosystems, species) have moral status independent of human interests? If yes, what does that status entail for human action? The field''s starting move is the rejection of strict ANTHROPOCENTRISM — the view that only humans have moral status and that nature matters only instrumentally (as resource, aesthetic backdrop, life-support). Three argumentative waves drove the field. (1) ROUTLEY''S 1973 last-man argument (also known as Sylvan''s argument): imagine the last human alive, knowing they''re the last; if they chop down the last tree for no reason, most people judge this wrong, but anthropocentrism cannot explain why — there''s no human (present or future) being harmed. Either reject the intuition (rare) or accept that non-human nature has intrinsic value (the field''s default move). (2) SINGER''S 1975 utilitarian argument extended Bentham''s "the question is not, can they reason? nor, can they talk? but, can they suffer?" to a broad case for animal liberation: sentient creatures count morally; speciesism (giving more weight to humans simply because they''re human) is unjustified discrimination analogous to racism and sexism. (3) NAESS''S 1973 deep ecology argued for a fundamental reorientation: shallow ecology fixes pollution and resource-use; deep ecology requires recognizing the equal intrinsic worth of all life and restructuring industrial civilization accordingly. The VALUE-LOCUS axis splits the field. ANTHROPOCENTRISM (now usually a "weak" version: humans are the locus of intrinsic value but our welfare depends on environmental health, so environmental ethics matters instrumentally to us); BIOCENTRISM (all individual life is intrinsically valuable; Schweitzer''s "reverence for life", Taylor 1986); ECOCENTRISM (ecosystems and species are intrinsically valuable as wholes, not merely as containers of valuable individuals; Leopold''s 1949 "land ethic", Callicott''s contemporary development; deep ecology is the strongest ecocentric version). The applied subfields — ANIMAL ETHICS (animal individuals'' welfare and rights), CLIMATE ETHICS (intergenerational obligations), CONSERVATION ETHICS (species and ecosystem preservation), ENVIRONMENTAL JUSTICE (the disproportionate environmental burden borne by the poor and people of color) — develop both within and across the value-locus positions.',
    ARRAY['nature_ethics', 'eco_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'anthropocentrism',
    'Anthropocentrism',
    ARRAY['ethics'],
    'The position in environmental ethics that only human beings possess intrinsic moral value; non-human animals, plants, ecosystems, and species matter morally only instrumentally — to the extent they affect human welfare, aesthetic experience, or future human generations. The historical default in Western ethical thought (Genesis dominion mandate; Aristotle''s ladder of being; Kant''s claim that animals lack moral status because they lack rational autonomy). Distinguished into STRONG anthropocentrism (humans are the only locus of value, period) and WEAK / ENLIGHTENED anthropocentrism (humans are the locus of intrinsic value, but human flourishing requires environmental responsibility, so environmental ethics matters strongly even on anthropocentric grounds).',
    'Anthropocentrism is the position environmental ethics typically positions itself against — though it''s often the version of WEAK anthropocentrism that contemporary defenders endorse. The STRONG anthropocentric position is now rare: even philosophers who reject biocentrism and ecocentrism typically grant that gratuitous cruelty to animals is wrong (this is hard to ground on STRICT anthropocentrism — if animals lack moral status, what makes cruelty wrong? — and the standard response is to invoke virtue-ethical considerations, character-corrupting effects on the cruel agent, that are still anthropocentric in their grounding but more sophisticated than the strict version). The WEAK / ENLIGHTENED anthropocentric line — articulated by Bryan Norton''s 1991 TOWARD UNITY AMONG ENVIRONMENTALISTS — argues environmentalists don''t need biocentrism or ecocentrism to justify strong environmental protection; human flourishing demonstrably requires environmental health (climate stability, biodiversity, clean air and water), so a sufficiently rich account of human welfare grounds the same policy conclusions that biocentrism / ecocentrism do. The strategic case for weak anthropocentrism: it is more politically persuasive (most people are anthropocentrists at base) and more philosophically tractable (intrinsic value of humans is widely accepted). The strategic case for biocentrism / ecocentrism: weak anthropocentrism is unstable — when human and non-human interests diverge, weak anthropocentrism reverts to instrumental valuation of nature; only positions that recognize non-human intrinsic value can ground robust environmental protection in those cases. THE LAST-MAN ARGUMENT (Routley 1973) is the canonical anti-anthropocentric argument: a last-human-alive who destroys the last tree for no reason does something wrong, but anthropocentrism cannot explain why. The CHRISTIAN STEWARDSHIP tradition (Berry 1990; the Catholic encyclical LAUDATO SI'' 2015) argues anthropocentrism is theologically wrong: humans are stewards of creation, not owners, and creation has intrinsic value as God''s creation independent of human use. SECULAR DEEP ECOLOGY similarly rejects anthropocentrism but on naturalist rather than theological grounds.',
    ARRAY['human_centered_ethics', 'human_chauvinism'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'biocentrism',
    'Biocentrism',
    ARRAY['ethics'],
    'The position in environmental ethics that all individual living things possess intrinsic moral value — not merely sentient animals, but all organisms with a good of their own, where the "good" tracks what is conducive to that organism''s survival, growth, reproduction, and flourishing. Albert Schweitzer''s "reverence for life" (1923 PHILOSOPHY OF CIVILIZATION) is the foundational articulation; Paul Taylor''s 1986 RESPECT FOR NATURE develops the position systematically with four core beliefs: (i) humans are members of the Earth''s community of life on the same terms as other species; (ii) all species are part of an interdependent system; (iii) every organism is a teleological-center-of-life pursuing its own good in its own way; (iv) humans are not inherently superior to other living things.',
    'Biocentrism extends moral status from human persons (or, on sentientism, sentient creatures) to ALL living individuals. The argumentative move: what justifies extending moral status from humans to (say) chimpanzees? — usually some property they share (sentience, cognitive sophistication). But these grounds extend further: ANY organism has a GOOD OF ITS OWN — there are conditions under which it flourishes and conditions under which it does not, independent of any observer''s interest. Taylor 1986 argues this teleological-center-of-life property is the morally relevant feature — sentience is one way of having a good of one''s own, but not the only way; bacteria, plants, fungi all have goods of their own. The position has both attractive and counterintuitive implications. Attractive: it grounds robust environmental protection without depending on contestable claims about ecosystem-as-a-whole intrinsic value (ecocentrism); it explains why deliberate destruction of a forest is wrong even if no sentient creature is harmed. Counterintuitive: it seems to require treating all life equally, which generates impossible ethical demands (every organism we kill — when we walk on grass, when we wash our hands, when we eat — would be a moral wrong). Taylor responds with a doctrine of self-defense, restitution, and minimum-wrong: not all lives are equal in their CLAIMS, and human flourishing requires living in ways that involve some unavoidable death of other organisms; but we have ongoing duties to minimize harm and to redress unavoidable harm. The cross-bridge to deep ecology (Naess 1973) is real — both reject anthropocentrism in favor of broader-than-human moral consideration — but biocentrism centers INDIVIDUAL organisms while deep ecology centers ECOSYSTEMS as wholes. The cross-bridge to ANIMAL ETHICS is closer: most animal-ethics positions are biocentric in the broader sense (sentient animals have a good of their own; we owe them moral consideration), but typically restrict to sentient creatures rather than extending to plants and microorganisms.',
    ARRAY['life_centered_ethics', 'taylor_biocentrism', 'reverence_for_life'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'ecocentrism',
    'Ecocentrism',
    ARRAY['ethics'],
    'The position in environmental ethics that ecosystems, species, and biological communities possess intrinsic moral value as WHOLES — not merely as containers of valuable individuals (whether sentient or non-sentient). Aldo Leopold''s 1949 SAND COUNTY ALMANAC "Land Ethic" is the foundational articulation: "A thing is right when it tends to preserve the integrity, stability and beauty of the biotic community. It is wrong when it tends otherwise." J. Baird Callicott develops the position systematically through the late 20th century. The ECOLOGICAL HOLISM grounding ecocentrism is contested; critics (especially individualist-oriented animal-ethicists like Tom Regan) charge ecocentrism with "environmental fascism" — willingness to sacrifice individual creatures for ecosystem integrity.',
    'Ecocentrism is the most holistic position in environmental ethics: the locus of intrinsic value is the ecosystem, the species, the biotic community as such — not its individual members. Leopold 1949 grounds the position in ecological science: organisms exist within communities; communities have integrity, stability, beauty; ethical conduct is rightly oriented to the community''s flourishing, not just to individuals'' welfare. Practical examples illuminate the difference from biocentrism and animal ethics. Culling an invasive species (rabbits in Australia, cats on Pacific islands) involves killing individual sentient animals; biocentrism and animal-ethics typically forbid this; ecocentrism permits and may require it for ecosystem integrity. Allowing wildfire (after a century of suppression) involves the deaths of many individual creatures; ecocentrism endorses managed burns as ecosystem-restorative; individualist positions condemn the loss of life. Hunting endangered-species predators (wolves) to protect endangered-species prey (caribou) involves killing some to save others; ecocentrism evaluates the choice in ecosystem terms, individualist positions in individual terms. Tom Regan''s 1983 charge of "environmental fascism" sharpens the disagreement: if individuals can be sacrificed for the ecosystem''s integrity, individuals don''t have inviolable rights — any individual could be sacrificed if doing so promoted ecosystem flourishing. Ecocentrists respond that ecocentrism doesn''t deny individual moral status; it adds ecosystem-level moral status, which sometimes overrides individual claims (just as in human ethics, some individual claims can be overridden for community goods, though typically with high thresholds). The cross-bridge to deep ecology is close: deep ecology is the strongest ecocentric position, going beyond Leopold''s land ethic to call for fundamental civilizational reorientation toward ecological values. Cross-bridges to metaphysics (P5-02a on substance and event ontology applied to ecosystems — what kind of entity is an ecosystem?) defer to P5-11.',
    ARRAY['ecosystem_ethics', 'land_ethic', 'leopold_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'deep_ecology',
    'Deep Ecology',
    ARRAY['ethics'],
    'The radical environmental position introduced by Arne Naess in his 1973 paper "The Shallow and the Deep, Long-Range Ecology Movement" arguing that environmental problems require not technical fixes (the "shallow" approach) but a fundamental restructuring of human civilization to accord with the equal intrinsic value of all life and the inherent worth of biological diversity. Naess and Sessions articulated the EIGHT-POINT PLATFORM (1984): the well-being of human and non-human life on Earth has value in itself; richness and diversity of life forms are values in themselves; humans have no right to reduce this richness except to satisfy vital needs; current human interference is excessive; human flourishing is compatible with substantial decrease in human population; significant policy change is required; the change appreciates life-quality over standard-of-living; those who subscribe have an obligation to try to implement the changes.',
    'Deep ecology is the most radical position in environmental ethics. Where mainstream ethics asks how to balance human and environmental interests, deep ecology asks for a fundamental reorientation of human civilization — what Naess called ECOSOPHY (ecological wisdom) — recognizing the equal intrinsic worth of all life and restructuring our practices accordingly. The position has three distinguishing features. (1) METAPHYSICAL HOLISM: humans are not separate from nature but part of an ecological whole; the modernist subject-object dualism that places humans against an external "environment" is metaphysically wrong. (2) EQUAL INTRINSIC VALUE: all life-forms have intrinsic worth; a hierarchy that places humans at the top is anthropocentric prejudice. (3) CIVILIZATIONAL CRITIQUE: industrial civilization, with its growth-orientation, resource-extraction model, and scale, is incompatible with ecological flourishing; deep ecology calls for population reduction, simpler standards of living oriented to quality rather than quantity, and decentralized economies attuned to local ecologies. The position is influential and contested. Influence: Earth First! (the radical environmental movement of the 1980s-90s) draws on deep ecology; the broader environmental-justice movement draws selectively (population-reduction calls have been criticized as racist coding when applied unevenly to the global south). Contested: critics charge that DEEP ECOLOGY conflates ECOLOGY (a descriptive science) with ETHICS (a normative discipline) — the move from "everything is interconnected" (true) to "all life has equal intrinsic value" (substantive ethical claim) is not a tight inference. Criticised also for political implications: the WHO IS QUALIFIED TO REPRESENT the will of nature is fraught (Murray Bookchin''s social-ecology critique: deep ecology has no theory of human social structure and risks being co-opted by misanthropic or authoritarian politics). Cross-bridges to metaphysics (the metaphysical-holism component) defer to P5-11.',
    ARRAY['naess_deep_ecology', 'ecosophy'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'animal_ethics',
    'Animal Ethics',
    ARRAY['ethics'],
    'The branch of applied ethics treating moral questions about humans'' relations to non-human animals — the use of animals for food, clothing, research, entertainment, and companionship; the moral status of animals; the obligations humans have to wild animals and to ecosystems containing them. Crystallizes in the 1970s with Peter Singer''s 1975 ANIMAL LIBERATION (utilitarian-grounded extension of equal consideration of interests to all sentient creatures) and Tom Regan''s 1983 THE CASE FOR ANIMAL RIGHTS (Kantian-grounded extension of inherent value, rights, and inviolability to "subjects-of-a-life"). Distinguished from broader environmental ethics by its focus on animal individuals rather than ecosystems or species; distinguished from anthropocentric concerns about animal welfare (animal suffering matters because humans care about it) by its claim that animals matter morally on their own account.',
    'Animal ethics is the most developed subfield of applied environmental ethics, with a rich theoretical literature spanning utilitarian, deontological, virtue, contractualist, capabilities, and feminist-care frameworks. The two foundational books — Singer 1975 and Regan 1983 — represent the two dominant approaches. SINGER''s utilitarian argument: equal consideration of interests is the basic principle of ethical reasoning; the relevant interest is the capacity for suffering and pleasure (sentience); humans and many non-human animals share this capacity; therefore equal consideration of like interests across species is required. Singer''s 1975 book documented the suffering of factory-farmed animals and the routine use of animals in experimentation — and argued that the practices were inconsistent with the equal-consideration principle. Singer''s position is sometimes called animal LIBERATION rather than animal RIGHTS — utilitarianism doesn''t recognize inviolable individual rights (a sentient creature can in principle be sacrificed to prevent more suffering elsewhere), so the position falls short of Regan''s. REGAN''s deontological argument: SUBJECTS-OF-A-LIFE — beings with beliefs, desires, perception, memory, a sense of the future, an emotional life, and welfare-interests — possess inherent value; this inherent value is equal across all subjects-of-a-life; persons have inviolable rights against being treated as mere resources; therefore most uses of animals (food, research, entertainment) are wrong. Regan''s argument doesn''t depend on aggregate welfare calculations; even if eating animals produced more net welfare than not, doing so violates their inherent value. Both positions face the question of WHICH animals count. Singer''s sentience criterion includes most vertebrates and cephalopods; Regan''s subjects-of-a-life criterion is more demanding (mammals at least, perhaps birds, but not invertebrates). CONTEMPORARY developments: VIRTUE-ETHICAL animal ethics (Hursthouse 2006) — virtuous character requires appropriate dispositions toward animals; CARE-ETHICAL animal ethics (Donovan & Adams 2007) — appropriate moral attention to particular animal others, distinct from rights or utility frameworks; CAPABILITIES animal ethics (Nussbaum 2006) — each species has a characteristic form of flourishing; political theorists (Donaldson & Kymlicka 2011 ZOOPOLIS) explore animals'' political status. Cross-bridges to philosophy of mind (P5-07a/b on animal consciousness) defer to P5-11.',
    ARRAY['animal_rights_ethics', 'animal_welfare_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'sentientism',
    'Sentientism',
    ARRAY['ethics'],
    'The position that the capacity for SENTIENCE — the capacity for subjective experience, particularly the capacity to suffer and to feel pleasure — is the necessary and sufficient condition for moral status. Sentient creatures (those that can experience) possess moral standing; non-sentient entities (rocks, plants, individual cells) do not. Singer 1975 is the canonical articulation grounding animal liberation; Bentham''s "the question is not, can they reason? nor, can they talk? but, can they suffer?" (1789 INTRODUCTION TO THE PRINCIPLES OF MORALS AND LEGISLATION footnote) is the foundational text. Distinguished from biocentrism (which extends moral status to all life, including non-sentient) and from anthropocentrism (which restricts moral status to humans). The dominant theoretical framework underwriting contemporary animal ethics.',
    'Sentientism is the foundational stance of contemporary animal ethics. The argumentative move: whatever grounds human moral status must be either (a) species membership simpliciter — but this is arbitrary; or (b) some property humans share — and the relevant property is sentience, the capacity for subjective experience. Bentham''s 1789 footnote is the canonical statement: "It may come one day to be recognized that the number of legs, the villosity of the skin, or the termination of the os sacrum, are reasons equally insufficient for abandoning a sensitive being to the same fate. What else is it that should trace the insuperable line? Is it the faculty of reason, or perhaps the faculty of discourse? But a full-grown horse or dog is beyond comparison a more rational, as well as a more conversable animal, than an infant of a day, or a week, or even a month, old. But suppose they were otherwise, what would it avail? The question is not, Can they reason? nor, Can they talk? but, Can they suffer?" Singer 1975 takes this seriously and extends it systematically. The position is BROADER than utilitarianism (a deontologist can be sentientist — moral status tracks sentience, but rights ground duties beyond pleasure-maximization; Regan''s subjects-of-a-life position is sentientist in this broader sense, with the sentience criterion supplemented by additional cognitive features). THE LINE-DRAWING question — which creatures are sentient — is empirically contested. Vertebrates almost certainly are (overwhelming behavioral, neurological, and evolutionary evidence). Cephalopods (octopuses, squid) seem to be (recent neuroscience strongly supports invertebrate sentience in cephalopods). Insects are contested (some indicators present, but key markers absent or weak). Plants are virtually never granted sentience (no nervous system; behavioral responses don''t require subjective experience to explain). The cross-bridge to philosophy of mind (P5-07a/b on consciousness in non-human animals — what makes a creature sentient, what evidence we have for non-human sentience) defers to P5-11. The cross-bridge to BIOCENTRISM is close but distinguishable: sentientism restricts to sentient creatures while biocentrism extends to all life with a good of its own.',
    ARRAY['sentience_based_ethics', 'pathocentric_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'climate_ethics',
    'Climate Ethics',
    ARRAY['ethics'],
    'The branch of environmental ethics treating moral questions raised by anthropogenic climate change — the obligations of present generations to future ones; the fair allocation of mitigation burdens (who should reduce emissions and by how much); the just allocation of adaptation resources (who pays for the harms already locked in); the moral status of high-emission individual lifestyles; the obligations of high-emitting nations to low-emitting and disproportionately-affected nations; the moral acceptability of geoengineering. Crystallizes as a distinctive subfield in the 2000s-2010s with Stephen Gardiner''s 2011 A PERFECT MORAL STORM, Henry Shue''s decades-long work on climate justice, Dale Jamieson''s 2014 REASON IN A DARK TIME, and the rich philosophical literature responding to the IPCC reports.',
    'Climate ethics is environmental ethics'' contemporary frontier, distinguished from earlier environmental concerns by its INTERGENERATIONAL structure (current emissions affect future people, not just current non-humans), GLOBAL structure (no nation can solve climate alone), and CUMULATIVE structure (the harm accumulates over decades; individual contributions are small but aggregated they''re catastrophic). Stephen Gardiner''s 2011 A PERFECT MORAL STORM diagnoses climate change as the convergence of three storms that make collective ethical action particularly difficult. (1) GLOBAL — climate spans national boundaries with no global governance to enforce action; nations have incentives to free-ride. (2) INTERGENERATIONAL — current generations bear costs of action whose benefits accrue to future generations (and current generations bear no costs of inaction whose costs fall on future generations); time-horizons of decision-makers (election cycles) are far shorter than climate timescales. (3) THEORETICAL — our ethical theories are not well-suited to the problem''s structure; consequentialism struggles with discounting future welfare and with vast aggregations of small harms; deontology struggles with positive obligations to distant future people; virtue ethics has no settled vocabulary for civic-environmental virtues. The convergence creates motivated reasoning: each generation has reasons to defer action to the next. Climate ethics also raises concrete distributive-justice questions. EMISSIONS-EQUITY: should mitigation burdens fall on per-capita emissions, on cumulative-historical emissions, on current emissions, on capacity to pay? Different metrics yield very different burden allocations; the U.S. (high cumulative, high per-capita) bears heavier responsibility on most metrics; China (high current, lower per-capita) is intermediate; least-developed nations bear minimal responsibility but the largest harms. ADAPTATION FUNDING: who pays for the harms locked in by past emissions — sea-level rise displacing coastal populations, weather-pattern changes destabilizing agricultural regions, ecosystem-collapse accelerating biodiversity loss? GEOENGINEERING: are large-scale technical interventions (solar radiation management, ocean iron fertilization, atmospheric carbon-capture) morally acceptable, given uncertainties, governance challenges, and moral-hazard concerns? Cross-bridges to philosophy of science (P5-09 on climate-science epistemology), to political philosophy (P5-05 on global distributive justice), and to philosophy of mind (P5-07 on personal identity over time) defer to P5-11.',
    ARRAY['climate_change_ethics', 'environmental_climate_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'future_generations',
    'Future Generations',
    ARRAY['ethics'],
    'The abstract concept underwriting any ethical position that grants moral status to people who do not yet exist but will come to exist (or whose existence depends on present choices). Central to climate ethics, environmental ethics, intergenerational justice, population ethics, and longtermist effective altruism. Raises distinctive philosophical puzzles — most famously Parfit''s NON-IDENTITY PROBLEM (some choices that seem to harm future people in fact change WHICH future people will exist, complicating any harm-based argument), the REPUGNANT CONCLUSION (if total welfare matters, a sufficiently large population at low per-capita welfare is better than a smaller population at high welfare), and the ASYMMETRY (it''s wrong to bring a miserable person into existence, but it''s not obligatory to bring a happy person into existence; symmetry arguments fail).',
    'Future generations is the abstract concept that any ethical view of intergenerational obligations must engage. The simplest position: future people will exist; their welfare counts; we have obligations not to harm them and (perhaps) positive obligations to leave them resources to flourish. The complexities arise from THE NON-IDENTITY PROBLEM (Parfit 1984 — different choices yield different populations of future people; you can''t straightforwardly say "this choice harms future people" if a different choice would have produced different future people, none of whom would exist on the actual choice), TEMPORAL DISCOUNTING (should distant future welfare count for less than near-term welfare? if yes, on what grounds — pure time preference, uncertainty, opportunity cost? if no, how do we make tractable decisions?), POPULATION ETHICS questions (the REPUGNANT CONCLUSION — Parfit 1984: total-welfarism implies a sufficiently large population at marginally-positive welfare is better than a smaller population at high welfare; most people find this repugnant, but the alternatives — averagism, person-affecting views — have their own counterintuitive implications), and the question of what we OWE to future people (sufficientarian — leave them enough; egalitarian — don''t bequeath them excessive inequality; capabilities — leave them institutions and resources for human flourishing). LONGTERMISM (Greaves & MacAskill 2021; Ord 2020) — the view that the moral importance of the long-term future, given its potential vast size, dominates short-term considerations — is a contemporary application of future-generations ethics that has sparked vigorous debate (critics charge it justifies neglecting present harms; defenders argue it merely takes future welfare seriously). The cross-bridges to political philosophy (P5-05 on intergenerational justice), to metaphysics (P5-02a/b on existence over time), and to philosophy of science (P5-09 on uncertainty about long-term futures) defer to P5-11.',
    ARRAY['future_people', 'intergenerational_concept'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'intergenerational_justice',
    'Intergenerational Justice',
    ARRAY['ethics'],
    'The normative concept treating fair distribution of benefits and burdens across generations — what current generations owe to past, present, and future generations. In environmental and climate ethics, the question is whether present generations may consume resources, generate pollution, or impose risks whose burdens fall on future generations. In broader political philosophy (P5-05 will treat the political dimensions), the question concerns intergenerational transfers — pension and entitlement systems, debt and capital stocks, institutional legacies. Distinct frameworks: utilitarian aggregation across generations (with the discount-rate question central); Rawlsian extension of the difference principle across generations (Rawls 1971; subsequent contractualist developments); communitarian / virtue accounts grounding intergenerational solidarity in shared identity across time.',
    'Intergenerational justice is the bridge concept between environmental ethics, political philosophy, and population ethics. The CLIMATE ETHICS literature has made it concrete: the present generation can decarbonize at significant cost to itself, conferring climate stability on future generations; or it can defer decarbonization, conferring economic flexibility on itself while imposing climate harms on future generations. The justice question: which choice is fair? Several frameworks. UTILITARIAN — aggregate welfare across generations; the question is the discount rate (should we count future welfare equally? Stern''s 2007 review chose near-zero pure time preference, generating high-cost-of-current-emissions estimates; Nordhaus chose higher discount rates, generating lower estimates; the ethics-vs-empirics distinction matters here — pure time preference is an ethical parameter, while uncertainty discounting is empirical). RAWLSIAN — Rawls 1971 extended the contractualist apparatus to intergenerational savings (the JUST SAVINGS PRINCIPLE in section 44): each generation should save enough for the next so that just institutions can be maintained, but no more. Rawls''s treatment is incomplete and contested — he treats it as a question of CONTEMPORARIES'' obligations to future others rather than as fully INTERGENERATIONAL contract — but his framework has been extensively developed. CAPABILITIES — Nussbaum and others extend the capabilities approach to intergenerational obligations: each generation should leave the next a world in which the central capabilities for human flourishing remain achievable. SUFFICIENTARIAN — present generations owe future generations ENOUGH for a decent life, not necessarily as much as present generations have. PRIORITARIAN — give weight to those generations that are worse off (whichever those turn out to be). The CHANGE OVER TIME complication: the present is wealthier than the past; the future is uncertain to be wealthier than the present (climate change, resource depletion, geopolitical risk could make some future generations worse off). This complicates any simple "wealth flows from past to present to future" picture; the obligations may run in both directions or in unpredictable patterns. The non-identity problem (Parfit 1984) further complicates: if our choices change WHICH people will exist, the harm-based version of intergenerational-justice arguments has limited grip. Cross-bridges to P5-05 political philosophy on intergenerational justice as political concept defer to P5-11.',
    ARRAY['justice_across_generations', 'intergenerational_fairness'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'non_identity_problem',
    'Non-Identity Problem',
    ARRAY['ethics'],
    'Derek Parfit''s 1984 puzzle (REASONS AND PERSONS, ch. 16) showing that many choices we ordinarily judge to harm future people in fact do not — they change WHICH future people will exist, so the people whose lives are affected by the choice would not have existed had the choice been otherwise. The 14-year-old girl who chooses to have a child now (vs waiting to have a different child later) does not HARM the resulting child even if that child has a hard life: had she waited, this child would not exist; the alternative is non-existence, not a different and better life for the same person. The puzzle generalizes to climate, population, and policy choices that affect WHICH future people will exist.',
    'The non-identity problem is the central puzzle of population ethics and a recurrent obstacle in any harm-based intergenerational-ethics argument. Parfit''s 1984 statement: imagine choosing between two policies, DEPLETION (rapid resource use, more current welfare, future people in worse environmental conditions) and CONSERVATION (slower resource use, less current welfare, future people in better environmental conditions). Common sense judges DEPLETION wrong because it harms future people. But the policies will produce DIFFERENT POPULATIONS — different people will conceive different children at different times under different policies. The future people in the DEPLETION world owe their existence to DEPLETION; without it they wouldn''t exist. Any specific future person in the DEPLETION world is not harmed by DEPLETION, since the alternative for THEM is non-existence. The harm-based judgment that DEPLETION is wrong cannot be sustained by individual-affected-person reasoning. Parfit''s response was a SAME PEOPLE / DIFFERENT PEOPLE distinction and the development of IMPERSONAL OUTCOME-BASED ethics (the choice that produces the better outcome — by some measure of total welfare or institutional quality — is the right one, even when no specific individual is better off in the chosen outcome). Critics charge that impersonal outcome-based reasoning brings its own problems (the REPUGNANT CONCLUSION, addressed under future_generations) and that PERSON-AFFECTING views (an action is wrong only if it makes someone worse off than they otherwise would have been) are intuitively more compelling. PERSON-AFFECTING attempts to handle non-identity have been many: NARROW person-affecting views (must affect actual or merely-possible specific persons) generate the original problem; WIDE person-affecting views (must affect persons or person-stages-of-some-extension) handle non-identity but at the cost of theoretical complexity. The problem is named so because the affected people (those in the worse future) lack identity-determining facts that would make harm-claims legible. The cross-bridge to metaphysics (P5-02a/b on personal identity, modal identity, transworld identity) and to political philosophy (P5-05 on intergenerational justice) defers to P5-11.',
    ARRAY['parfit_non_identity', 'identity_dependent_choice_problem'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'just_war_theory',
    'Just War Theory',
    ARRAY['ethics'],
    'The systematic ethical framework for evaluating the moral permissibility of war and conduct within war. Traditional structure: JUS AD BELLUM (the justice of going to war — just cause, legitimate authority, right intention, last resort, reasonable prospect of success, proportionality) and JUS IN BELLO (the justice of conduct in war — discrimination between combatants and noncombatants, proportionality, prohibition on means malum in se). Contemporary additions: JUS POST BELLUM (the justice of peace settlements and post-conflict reconstruction) and JUS AD VIM (the justice of force short of war, e.g., targeted assassinations, drone strikes). Augustine and Aquinas anchor the medieval Christian tradition; the SECULAR contemporary revival is centered on Michael Walzer''s 1977 JUST AND UNJUST WARS.',
    'Just war theory is the central applied-ethics framework for political violence at the international scale. Its argumentative structure presupposes that war is sometimes morally permissible (rejecting strict pacifism), but tightly constrains when and how. JUS AD BELLUM criteria (the justice of going to war): JUST CAUSE — usually self-defense or defense of others against unjust aggression; LEGITIMATE AUTHORITY — only certain authorities (states; perhaps others under conditions) may declare war; RIGHT INTENTION — the war must be fought for the just cause, not for some ulterior aim; LAST RESORT — peaceful means must have been exhausted; REASONABLE PROSPECT OF SUCCESS — war that cannot succeed inflicts harm without compensating benefit; PROPORTIONALITY — the harms of war must not outweigh the goods. JUS IN BELLO criteria (the justice of conduct in war): DISCRIMINATION — combatants are legitimate targets; noncombatants are not; PROPORTIONALITY — within the war, military operations must not produce disproportionate civilian harms; PROHIBITION ON MEANS MALUM IN SE — some means (rape, torture, weapons of mass destruction, perfidy) are wrong even in pursuit of just causes. The classical doctrine treats jus ad bellum and jus in bello as INDEPENDENT — soldiers fighting in an unjust cause may still observe jus in bello and be morally innocent in their conduct. McMahan 2009 argues this independence collapses on a careful examination — soldiers fighting in an unjust war are committing aggression, and their unjust-war combatant status doesn''t neutralize the moral wrongness. WALZER 1977 articulates the contemporary state-of-the-art with a "war convention" that codifies jus in bello as a moral practice independent of the underlying jus ad bellum question. Contemporary cases stress test the doctrine: HUMANITARIAN INTERVENTION (using force to stop genocide or massive human-rights violations against the population of another state — does this satisfy just-cause requirements?), TERRORISM (do terrorists have legitimate authority? are noncombatants in terrorism-supporting societies legitimate targets?), DRONE WARFARE (does targeted killing qualify as jus ad bellum or jus ad vim?), CYBERWARFARE (how to apply discrimination and proportionality when civilian and military infrastructure are intertwined?). Cross-bridges to political philosophy (P5-05 on sovereignty and legitimate authority) defer to P5-11.',
    ARRAY['jus_ad_bellum', 'jus_in_bello', 'walzer_just_war'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'pacifism',
    'Pacifism',
    ARRAY['ethics'],
    'The position rejecting just war theory''s permissibility claims for violence — either categorically (ABSOLUTE PACIFISM, war and violence are always morally impermissible) or contingently (CONTINGENT PACIFISM, the conditions just war theory specifies are virtually never satisfied, so virtually all actual wars are wrong; or the disutilities of war are so reliably catastrophic that the just-war framework is in practice untenable). Religious roots in early Christian (Tertullian, Hippolytus pre-Constantinian non-violence), Buddhist, Jain, and Quaker traditions; secular roots in Tolstoy''s Christian-anarchist non-violence and in Gandhi''s satyagraha (truth-force, non-violent resistance). Distinguished from skeptical positions on specific wars (most people are not pacifists but believe specific wars unjust) and from non-violent-resistance pragmatism (which may endorse non-violence as more effective without grounding it in absolute moral terms).',
    'Pacifism is the canonical denial of just war theory''s permissibility claims. The structure: just war says war is sometimes permissible under conditions; pacifism says either NEVER (absolute pacifism) or NEARLY-NEVER-IN-PRACTICE (contingent pacifism). The grounds are diverse. (1) RELIGIOUS — early Christian non-violence (Tertullian, Hippolytus); the historical peace churches (Mennonites, Quakers, Brethren); Buddhist and Jain traditions of ahimsa; the Constantinian shift in 4th-century Christianity is the moment Christian non-violence gives way to Augustinian / Aquinas-medieval just war reasoning. (2) DEONTOLOGICAL — killing is intrinsically wrong; the prohibition is exceptionless; war involves intentional killing at scale; therefore war is wrong. The argument needs to handle defensive killing in self-defense or in defense of others, which most people consider permissible; pacifist responses range from absolute denial of self-defense (Tolstoy) to contingent denial (defensive force is permitted in narrow circumstances but war exceeds them). (3) CONSEQUENTIALIST — the actual harms of war (deaths, lasting trauma, infrastructure destruction, post-war instability, refugee flows) reliably outweigh the goods even in apparently just causes; the empirical record supports the inference. (4) NON-VIOLENT-RESISTANCE PRAGMATISM (Gandhi, King) — non-violent struggle is morally superior AND tactically more effective; Chenoweth & Stephan''s 2011 WHY CIVIL RESISTANCE WORKS provides empirical support for the tactical-superiority claim. The classical objection to absolute pacifism: at some scale of evil (the Nazi extermination of European Jewry; massive ongoing genocide elsewhere) the refusal to use violence becomes a moral failure to act. Walzer 1977 puts the case forcefully: the supreme emergency of WWII justified what would otherwise have been violations of jus in bello (civilian bombing) because the alternative was Nazi victory. Pacifists respond either (a) absolute pacifism: even in supreme emergency, killing is wrong (the cost of Nazi victory is real but doesn''t override the absolute prohibition); (b) contingent pacifism: WWII may have been a real exception, but framing it as a special case shows just-war reasoning is rare and dangerous in less clear cases. Cross-bridges to P5-04a''s normative theories — pacifism naturally allies with deontology and care-ethics, sits uncomfortably with consequentialism unless contingent, and divides from virtue-ethics on whether courage and patriotism count as virtues that may require military service — defer to P5-11.',
    ARRAY['non_violence', 'absolute_pacifism', 'contingent_pacifism'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'business_ethics',
    'Business Ethics',
    ARRAY['ethics'],
    'The branch of applied ethics treating moral questions arising in commercial activity, business management, and corporate governance — the obligations of business to shareholders, employees, customers, communities, and the natural environment; the moral acceptability of profit-maximization as a guiding principle; the ethics of marketing, advertising, and product design; corporate social responsibility; whistleblowing; bribery and corruption; fiduciary duties; the global ethics of supply chains; the proper relationship between business and politics. The contemporary academic field crystallizes in the 1970s-80s with Milton Friedman''s 1970 NYT Magazine essay "The Social Responsibility of Business is to Increase Its Profits" as one canonical anchor and R. Edward Freeman''s 1984 STRATEGIC MANAGEMENT: A STAKEHOLDER APPROACH as the major alternative.',
    'Business ethics is the applied-ethics field with the most direct economic stakes — what counts as morally permissible in commercial activity has enormous consequences for individuals, communities, and the natural environment. The field''s structuring debate: SHAREHOLDER vs STAKEHOLDER theory. SHAREHOLDER THEORY (Milton Friedman 1970) — the manager''s duty is to maximize shareholder value within the rules of the game (law, basic ethics, and competitive practices); broader social goals are properly the business of governments and individuals, not businesses; charitable corporate spending is theft from shareholders. The position has economic-efficiency grounding (specialization: businesses do business well; governments do social goods well; mixing the functions reduces both) and a libertarian-political grounding (corporations are collections of voluntary contracts; managers serve shareholders, not society at large). STAKEHOLDER THEORY (Freeman 1984) — businesses have obligations to all those affected by their operations: shareholders, employees, customers, suppliers, communities, the natural environment. The manager''s task is to balance these obligations, not to maximize a single metric. The CSR (Corporate Social Responsibility) literature develops stakeholder theory practically: companies should adopt environmental, social, and governance (ESG) practices that go beyond legal minima and beyond shareholder-value maximization. The 21st-century debate has moved past the shareholder/stakeholder dichotomy toward INSTITUTIONAL questions: whether shareholder primacy as currently practiced is even good for shareholders (short-termism, financialization); whether ESG disclosure mandates are useful or distorting; whether business ethics can be effective without enforceable standards. Specific applied issues — WHISTLEBLOWING (when do employees have duties to report wrongdoing externally? what protections do whistleblowers warrant?), BRIBERY AND CORRUPTION (the FCPA and global anti-corruption regimes; legitimate vs illegitimate facilitation payments), MARKETING ETHICS (deceptive advertising; targeting children; addiction-engineering in food and gaming products), SUPPLY CHAIN ETHICS (sweatshop labor; conflict minerals; supply-chain due diligence), FIDUCIARY DUTIES (board obligations; insider trading; conflicts of interest) — develop in their own subfields. Cross-bridges to P5-04a''s consequentialism (business ethics in utilitarian framing) and deontology (fiduciary duties as deontological side-constraints) and to P5-05 political philosophy (business in a democratic political order) defer to P5-11.',
    ARRAY['corporate_ethics', 'commercial_ethics'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'technology_ethics',
    'Technology Ethics',
    ARRAY['ethics'],
    'The branch of applied ethics treating moral questions arising from the design, development, deployment, and use of technology — privacy and surveillance; algorithmic decision-making and bias; intellectual property; the ethics of attention-economy platforms; biotechnology and human enhancement; autonomous systems; cybersecurity ethics; the digital divide and technological access; the ethics of dual-use research. The field has roots in 20th-century philosophy of technology (Heidegger 1954 "The Question Concerning Technology"; Mumford on the megamachine; Ellul on technique) and crystallizes as applied ethics in the late 20th century (Floridi''s information ethics from the 1990s; computer ethics from Norbert Wiener 1950 onward).',
    'Technology ethics is a heterogeneous applied-ethics field unified by attention to how specific technologies generate moral questions either by enabling new actions, by changing the moral landscape (privacy in a world of ubiquitous surveillance differs from privacy in a world without it), or by replacing human judgment with automated systems. The field has several distinguishable currents. (1) PHILOSOPHY OF TECHNOLOGY broadly construed (Heidegger; Mumford; Ellul; later Borgmann 1984; Don Ihde) — these treat technology as a whole, asking after technology''s general moral and metaphysical character, often with critical-theory orientations toward modern industrial-technological civilization. (2) COMPUTER ETHICS / INFORMATION ETHICS (Wiener 1950; James Moor 1985 "What is Computer Ethics"; Luciano Floridi 1999 onward) — these address moral questions specifically arising from computational technology, with Floridi''s INFORMATION ETHICS proposing that informational entities have moral status and that ethics must be reconceived in informational terms. (3) ENGINEERING ETHICS — the professional ethics of engineers, with codes of conduct around safety, public welfare, and honesty in technical work. (4) APPLIED ISSUES — privacy and data protection (Westin 1967; Nissenbaum 2010 "contextual integrity"; the GDPR regulatory regime); algorithmic bias and fairness (the dominant debate of the 2010s — risk-assessment tools in criminal justice, automated hiring, credit scoring; the technical / philosophical question of what fairness REQUIRES across protected groups); attention-economy ethics (the design of platforms to capture attention; questions of user autonomy, addiction, manipulation); biotech ethics (gene editing especially CRISPR; human enhancement; designer babies; gain-of-function research); autonomous-systems ethics (self-driving cars; lethal autonomous weapons; the trolley-problem framing many participants find inappropriate or trivializing). The field interacts with bioethics (gene editing crosses the boundary), with environmental ethics (technology''s ecological impact), and with political philosophy (technology and democratic governance). The cross-bridges to philosophy of mind (P5-07) on machine consciousness and moral status, to philosophy of language (P5-08) on machine semantics, and to epistemology (P5-01) on machine knowledge defer to P5-11.',
    ARRAY['tech_ethics', 'philosophy_of_technology_applied'],
    'INTERPRETED',
    'ai-seed',
    8
  ),
  (
    'ai_ethics',
    'AI Ethics',
    ARRAY['ethics'],
    'The branch of technology ethics treating moral questions arising specifically from artificial intelligence systems — value alignment (ensuring AI systems pursue intended goals); fairness and bias in algorithmic decisions; transparency and explainability; safety in autonomous systems; the moral status of AI systems themselves (do sufficiently advanced AI systems have moral standing?); the differential impact of AI on labor, surveillance, warfare; existential and catastrophic risks from advanced AI; governance of AI development. The field has grown rapidly since the mid-2010s as AI capabilities advanced; key sources include Bostrom''s 2014 SUPERINTELLIGENCE, Russell''s 2019 HUMAN COMPATIBLE, the IEEE / AI principles documents, and the rich technical-philosophical literature on machine ethics (Wallach & Allen 2009 MORAL MACHINES) and value alignment.',
    'AI ethics has emerged in the past decade as the dominant frontier within technology ethics, driven by rapid capability gains in machine-learning systems and the growing deployment of AI in consequential decisions. The field divides into several distinguishable concerns. (1) NEAR-TERM ALIGNMENT, FAIRNESS, AND TRANSPARENCY — the deployed-systems concerns. ALGORITHMIC BIAS: ML systems trained on historical data often encode and amplify historical biases (criminal-justice risk-assessment tools that produce disparate-impact false-positive rates across racial groups; hiring algorithms that filter out women''s resumes; lending algorithms that disadvantage minority borrowers). The technical-philosophical question is what FAIRNESS requires (Hardt-Price-Srebro 2016 demonstrated multiple incompatible fairness criteria — equalized odds, equalized opportunity, calibration; satisfying all simultaneously is impossible except in trivial cases). EXPLAINABILITY: complex ML systems often function as black boxes; affected parties cannot understand why a decision was made; this raises rule-of-law and dignity concerns about being subjected to opaque algorithmic decisions. PRIVACY in ML: training data leakage, model inversion attacks, the differential-privacy literature. (2) MACHINE ETHICS — can AI systems themselves be moral agents? Can they be programmed with ethical principles? Wallach & Allen 2009 distinguish OPERATIONAL morality (the system follows ethical rules but doesn''t reflect on them), FUNCTIONAL morality (the system applies ethical principles flexibly), and FULL morality (the system is a moral agent in the philosophical sense). The contemporary consensus is that current systems are not moral agents; the future is contested. (3) VALUE ALIGNMENT — Russell 2019 frames the central problem: advanced AI systems must pursue goals that align with human values; the alignment problem is unsolved and may be hard. Subspecies: outer alignment (specifying the right objective), inner alignment (training producing optimization for the specified objective rather than something correlated with it), corrigibility (system''s willingness to accept correction). (4) EXISTENTIAL AND CATASTROPHIC RISK — Bostrom 2014 SUPERINTELLIGENCE argues that sufficiently advanced AI poses catastrophic-and-possibly-existential risks; the field of AI safety has grown around the alignment problem. Critics distinguish "near-term harms" concerns from "long-term existential risk" concerns and argue the conflation harms both. (5) GOVERNANCE — the OECD AI Principles 2019, EU AI Act 2024, US AI Bill of Rights 2022, and bilateral / multilateral AI-safety initiatives represent attempts to govern AI development. Cross-bridges to philosophy of mind (P5-07a/b on machine consciousness and intentionality) and to epistemology (P5-01a/b on machine knowledge) defer to P5-11.',
    ARRAY['artificial_intelligence_ethics', 'machine_ethics_applied'],
    'INTERPRETED',
    'ai-seed',
    8
  );

-- Edges: 34 INSERTs covering within-domain pedagogical_prerequisite edges only.
-- Cross-domain edges (to P5-04a's metaethics+normative-theory inventory; to
-- other Phase 5 subdomains) defer to P5-11 per phase_5.md T2-G #1.
INSERT INTO public.edges (source_id, target_id, edge_type, weight, confidence, provenance, graph_version_added) VALUES
  ('applied_ethics', 'bioethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('applied_ethics', 'environmental_ethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('applied_ethics', 'just_war_theory', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('applied_ethics', 'business_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('applied_ethics', 'technology_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('bioethics', 'medical_ethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('bioethics', 'research_ethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('bioethics', 'end_of_life_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('bioethics', 'reproductive_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('bioethics', 'four_principles_bioethics', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('four_principles_bioethics', 'autonomy_bioethical', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('four_principles_bioethics', 'beneficence', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('four_principles_bioethics', 'non_maleficence', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('four_principles_bioethics', 'justice_bioethical', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('autonomy_bioethical', 'informed_consent', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('medical_ethics', 'informed_consent', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('research_ethics', 'informed_consent', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('medical_ethics', 'end_of_life_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('medical_ethics', 'reproductive_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('environmental_ethics', 'anthropocentrism', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('environmental_ethics', 'biocentrism', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('environmental_ethics', 'ecocentrism', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('environmental_ethics', 'climate_ethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('environmental_ethics', 'animal_ethics', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('biocentrism', 'deep_ecology', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('ecocentrism', 'deep_ecology', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('biocentrism', 'animal_ethics', 'pedagogical_prerequisite', 0.8, 0.8, 'ai-seed', 8),
  ('animal_ethics', 'sentientism', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('climate_ethics', 'future_generations', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('climate_ethics', 'intergenerational_justice', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('future_generations', 'intergenerational_justice', 'pedagogical_prerequisite', 0.95, 0.95, 'ai-seed', 8),
  ('future_generations', 'non_identity_problem', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8),
  ('just_war_theory', 'pacifism', 'pedagogical_prerequisite', 0.85, 0.85, 'ai-seed', 8),
  ('technology_ethics', 'ai_ethics', 'pedagogical_prerequisite', 0.9, 0.9, 'ai-seed', 8);

COMMIT;
