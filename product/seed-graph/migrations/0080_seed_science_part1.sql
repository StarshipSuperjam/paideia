-- Migration: 0080_seed_science_part1
-- Purpose: Thirteenth Phase 5 seed migration (the philosophy-of-science file)
--   — the methodology-anchored core of philosophy of science and within-
--   domain pedagogical_prerequisite edges. Authored in S-0073 against task
--   P5-09 "Philosophy of science seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md. P5-09
--   is a single-task subdomain per phase_5.md T1-B (philosophy of science
--   is methodology-anchored, well-bounded enough for a single migration).
--   Covers the nine coverage clusters identified at master-plan time:
--   foundation (the field umbrella, scientific method as the central
--   activity, scientific theory as the central product); confirmation
--   (hypothetico-deductive confirmation, Bayesian confirmation,
--   Hempel''s paradox of the ravens — Hume''s problem of induction is
--   canonical-homed under epistemology in P5-01a, with the cross-domain
--   edges from scientific_method and to bayesianism_confirmation
--   deferred to P5-11);
--   demarcation and structure (Popper''s demarcation problem,
--   falsificationism, Kuhn''s paradigm, paradigm shift, Lakatos''s
--   research programme); theories of explanation (scientific explanation,
--   Hempel-Oppenheim deductive-nomological model, inference to the best
--   explanation, unification theory of explanation); realism and
--   antirealism (scientific realism, van Fraassen''s constructive
--   empiricism, the no-miracles argument, Laudan''s pessimistic meta-
--   induction); underdetermination and observation (the underdetermination
--   thesis, the Duhem-Quine thesis, theory-ladenness of observation);
--   laws and models (laws of nature, scientific models); reduction and
--   unity (reductionism in science, multiple realizability as anti-
--   reductionist response); values in science (the value-free ideal).
--   Within-domain edges span the nine clusters with the pedagogical-
--   prerequisite structure rooted at philosophy_of_science. Cross-domain
--   edges (problem_of_induction ↔ epistemology on Hume''s problem and
--   inductive justification; scientific_realism ↔ metaphysics on natural
--   kinds and laws; multiple_realizability_in_science ↔ philosophy of
--   mind on functionalism and anti-reductionism; value_free_ideal ↔
--   ethics on values in inquiry; underdetermination/duhem_quine_thesis ↔
--   epistemology on holism and theory-choice; verificationism (in P5-08
--   philosophy-of-language) ↔ this seed on the logical-positivist
--   criterion of meaningfulness as a pre-condition for the demarcation
--   debate) remain P5-11''s exclusive surface.
-- Loads tables: public.nodes (27 INSERTs), public.edges (30 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 13 -> 14).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 13 at session boot (post-S-0071 per
--     ROUTING.md narrative — most recent applied seed at the cross-
--     subdomain prefix range was 0070_seed_language_part1.sql which
--     wrote 13).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 14 (the
--     post-increment value).
--   * No prior migrations under prefix 0080-0089; this is the first
--     philosophy-of-science seed file.
--   * P5-01a epistemology core applied (the only depends_on for P5-09).
--     No edge in this migration references epistemology nodes — within-
--     science seeding here; cross-domain bridges to epistemology
--     (problem_of_induction ↔ Hume; underdetermination ↔ holism and
--     theory-choice; bayesianism_confirmation ↔ Bayesian epistemology)
--     land at P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 27 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'science'}, status=active, graph_version_added=14.
--   * 30 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=14. All edges are
--     within-domain (source and target both tagged science); cross-
--     domain edges are P5-11''s exclusive responsibility. No edges
--     reference nodes outside this migration; the philosophy-of-science
--     subdomain is structurally self-contained at the methodology-
--     anchored core (the cross-domain reaches identified above are real
--     but live in P5-11). The problem_of_induction node is intentionally
--     not authored here because it is canonical-homed under epistemology
--     (P5-01a, domain=epistemology); the within-confirmation-cluster
--     edges that would otherwise originate from / terminate at
--     problem_of_induction are cross-domain edges in this graph and
--     are deferred to P5-11 by the same rule.
--   * settings.graph_version = 14.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 14 AND 'science' = ANY(domain) :: 27
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 14 AND edge_type = 'pedagogical_prerequisite' :: 30
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 14
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also inserts.
--   * No edge cycles in the pedagogical_prerequisite subgraph. Tier
--     assignment (relative to this migration''s nodes only — there are
--     no cross-migration endpoints; tiers reflect longest-path-from-
--     root): T0 philosophy_of_science; T1 scientific_method,
--     scientific_theory, scientific_explanation; T2 hypothetico_
--     deductivism, demarcation_problem, underdetermination,
--     value_free_ideal, scientific_realism, law_of_nature,
--     scientific_model, reductionism_in_science,
--     deductive_nomological_model, unification_theory_of_explanation;
--     T3 bayesianism_confirmation, paradox_of_the_ravens,
--     falsificationism, constructive_empiricism, no_miracles_argument,
--     pessimistic_meta_induction, multiple_realizability_in_science,
--     inference_to_the_best_explanation, duhem_quine_thesis; T4
--     paradigm (multi-bridge: scientific_theory T1 + falsificationism
--     T3 + duhem_quine_thesis T3); T5 paradigm_shift, research_programme,
--     theory_ladenness_of_observation. Every edge points from a strictly
--     lower-tier node to a strictly higher-tier node — no edges point
--     back, no same-tier edges. SCC freedom holds; validate.py''s
--     Kosaraju check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     no triple in this migration duplicates any other triple (the 30
--     edges are pairwise distinct in (source_id, target_id) since
--     edge_type is uniformly pedagogical_prerequisite). Note that
--     bayesianism_confirmation has one within-domain in-edge (from
--     hypothetico_deductivism — the problem_of_induction edge is cross-
--     domain and deferred to P5-11); inference_to_the_best_explanation
--     has two distinct in-edges (from scientific_explanation and from
--     deductive_nomological_model); paradigm has three distinct in-
--     edges (from scientific_theory, from falsificationism, from
--     duhem_quine_thesis); theory_ladenness_of_observation has two
--     distinct in-edges (from paradigm and from duhem_quine_thesis)
--     — each (source, target) pair is unique.
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: problem_of_induction bridges to
--     epistemology (P5-01a/b on Hume''s problem of induction as the
--     paradigm case for inductive justification — the philosophy-of-
--     science framing emphasizes its role in confirmation theory,
--     while the epistemology framing emphasizes its role as a defeater
--     for empirical knowledge); bayesianism_confirmation bridges to
--     epistemology (P5-01b on Bayesian epistemology as the formal
--     framework for credence-update — the philosophy-of-science framing
--     emphasizes its role in confirmation, the epistemology framing in
--     justification); scientific_realism bridges to metaphysics (P5-02a
--     on natural kinds and laws — Putnam-Boyd realism is partly a
--     metaphysical thesis about the mind-independence of unobservable
--     entities); multiple_realizability_in_science bridges to
--     philosophy of mind (P5-07a/b on functionalism and the anti-
--     reductionist argument from multiple realizability — Putnam 1967
--     formulated multiple realizability initially as a philosophy-of-
--     mind argument before its generalization to anti-reductionism in
--     special sciences); value_free_ideal bridges to ethics (P5-04a/b
--     on the role of values in inquiry — the value-laden vs. value-free
--     debate in philosophy of science is a special case of the broader
--     metaethical question about the relation of facts and values);
--     underdetermination and duhem_quine_thesis bridge to epistemology
--     (P5-01a on confirmational holism, theory-choice, and the
--     epistemic limits of evidence); verificationism (in P5-08, the
--     philosophy-of-language seed) bridges to this seed via
--     demarcation_problem and falsificationism (the logical-positivist
--     verification criterion of meaningfulness was the precursor to
--     Popper''s falsifiability criterion of demarcation, and both are
--     attempts to draw the boundary between science and non-science).
--     Wait for P5-11''s cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0081-0089).
--     Those slots remain reserved for any future Phase 6+ telemetry-
--     driven extensions to philosophy of science (e.g., specific topics
--     warranting follow-on seeding: scientific progress; structural
--     realism (epistemic vs. ontic); social epistemology of science;
--     mechanistic explanation; computational simulation in science;
--     perspectivism; specific specializations: philosophy of physics,
--     philosophy of biology, philosophy of chemistry, philosophy of
--     economics, philosophy of medicine, philosophy of statistics);
--     this seed completes P5-09''s task at the granularity principle
--     within the 0080 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 27/27 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference''s entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here
--     is well-named in the SEP/IEP entry inventory and corresponds to a
--     concept the contemporary analytic philosophy-of-science literature
--     (Hempel, Popper, Kuhn, Lakatos, Quine, Hanson, Feyerabend,
--     Putnam, Boyd, Laudan, van Fraassen, Friedman, Kitcher, Lipton,
--     Salmon, Cartwright, Suppes, Giere, Longino, Douglas, Kim, Fodor)
--     explicitly names. Mirrors the twelve prior Phase 5 subject seeds
--     (P5-01a/b epistemology, P5-02a/b metaphysics, P5-03 logic,
--     P5-04a/b ethics, P5-05 political philosophy, P5-06 aesthetics,
--     P5-07a/b philosophy of mind, P5-08 philosophy of language).
--   * domain[] cardinality: every node carries exactly one tag,
--     ''science''. Multiple cross-domain reaches exist (problem_of_
--     induction intersects epistemology; scientific_realism intersects
--     metaphysics; multiple_realizability_in_science intersects
--     philosophy of mind; value_free_ideal intersects ethics) but per
--     phase_5.md T2-G #4 (domain-tag cardinality explosions vector),
--     cross-domain tagging belongs to P5-11. The canonical home for
--     each of these concepts in the analytic literature is the
--     philosophy-of-science sub-literature, so the single ''science''
--     tag is correct here.
--   * provenance: ''ai-seed'' for every node and edge. Same as
--     P5-01a/b, P5-02a/b, P5-03, P5-04a/b, P5-05, P5-06, P5-07a/b,
--     P5-08.
--   * Node selection rationale: 27 concepts cover the nine core
--     methodology-anchored clusters at the granularity principle
--     (the originally-planned twenty-eighth concept,
--     problem_of_induction, is canonical-homed under epistemology in
--     P5-01a per phase_5.md T2-G #4 and not re-authored here; the
--     concept''s cross-domain reach into philosophy of science via
--     confirmation theory lands at P5-11):
--     (1) foundation (3) [philosophy_of_science, scientific_method,
--     scientific_theory] — the field umbrella, the central activity-
--     side concept, the central product-side concept;
--     (2) confirmation (3) [hypothetico_deductivism,
--     bayesianism_confirmation, paradox_of_the_ravens] — the H-D
--     model as the mid-twentieth-century mainstream, the Bayesian
--     framework as the dominant contemporary alternative, the
--     paradox of the ravens as the central technical puzzle in
--     Hempelian confirmation theory;
--     (3) demarcation and structure (5) [demarcation_problem,
--     falsificationism, paradigm, paradigm_shift, research_programme]
--     — Popper''s demarcation problem as the central question about
--     what distinguishes science from non-science, falsificationism as
--     Popper''s answer, Kuhn''s paradigm and paradigm_shift as the
--     canonical alternative framework that reframed philosophy of
--     science around scientific revolutions, Lakatos''s research
--     programme as the synthesis attempt;
--     (4) theories of explanation (4) [scientific_explanation,
--     deductive_nomological_model, inference_to_the_best_explanation,
--     unification_theory_of_explanation] — the central question about
--     what scientific explanation is, Hempel-Oppenheim 1948 as the
--     classical formal account, IBE as the dominant contemporary
--     account, the Friedman-Kitcher unification account as the major
--     alternative;
--     (5) realism and antirealism (4) [scientific_realism,
--     constructive_empiricism, no_miracles_argument,
--     pessimistic_meta_induction] — the central debate about whether
--     science gives us knowledge of unobservable reality, van
--     Fraassen''s 1980 constructive empiricism as the dominant
--     antirealist position, the no-miracles argument (Putnam 1975 /
--     Boyd 1983) as the central argument for realism, the pessimistic
--     meta-induction (Laudan 1981) as the central argument against
--     realism;
--     (6) underdetermination and observation (3) [underdetermination,
--     duhem_quine_thesis, theory_ladenness_of_observation] — the
--     thesis that data underdetermine theory choice, the holist
--     refinement of that thesis (Duhem 1906 / Quine 1951), the
--     Hanson-Kuhn-Feyerabend thesis that observation itself depends
--     on prior theoretical commitments;
--     (7) laws and models (2) [law_of_nature, scientific_model] —
--     laws as the traditional explanatory currency in the sciences,
--     models as the increasingly central alternative explanatory
--     vehicle (the model-based view of science: Cartwright, Suppes,
--     Giere);
--     (8) reduction and unity (2) [reductionism_in_science,
--     multiple_realizability_in_science] — the question of whether
--     special-science theories reduce to fundamental physics, multiple
--     realizability as the central anti-reductionist argument
--     (originating in Putnam 1967 on philosophy of mind, generalized
--     by Fodor 1974 to special sciences);
--     (9) values in science (1) [value_free_ideal] — the question of
--     whether scientific inquiry can or should be value-free
--     (Longino, Douglas, the inductive-risk argument).
--   * Edge structure: 30 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation spine flows philosophy_of_science →
--     {scientific_method, scientific_theory, scientific_explanation},
--     with scientific_method branching into hypothetico_deductivism,
--     demarcation_problem, underdetermination, and value_free_ideal
--     (the otherwise-natural scientific_method → problem_of_induction
--     edge is cross-domain, deferred to P5-11); scientific_theory
--     branching into scientific_realism, law_of_nature,
--     scientific_model, reductionism_in_science, and (skip-tier)
--     paradigm; scientific_explanation branching into deductive_
--     nomological_model and (skip-tier) inference_to_the_best_
--     explanation and unification_theory_of_explanation. Confirmation
--     cluster: hypothetico_deductivism → paradox_of_the_ravens;
--     hypothetico_deductivism → bayesianism_confirmation (Bayesian
--     confirmation as the contemporary refinement of H-D; the
--     parallel problem_of_induction → bayesianism_confirmation edge
--     is cross-domain and deferred to P5-11). Demarcation cluster:
--     demarcation_problem → falsificationism. Realism cluster:
--     scientific_realism → constructive_empiricism (the antirealist
--     foil); scientific_realism → no_miracles_argument (the central
--     pro-realism argument); scientific_realism → pessimistic_meta_
--     induction (the central anti-realism argument). Reduction
--     cluster: reductionism_in_science → multiple_realizability_in_
--     science (the central anti-reductionist response). Underdeter-
--     mination cluster: underdetermination → duhem_quine_thesis (the
--     holist refinement). Explanation chain: deductive_nomological_
--     model → inference_to_the_best_explanation (IBE as the post-D-N
--     successor account). Multi-bridge into paradigm (T4):
--     scientific_theory → paradigm (skip-tier T1→T4: paradigm is the
--     Kuhnian reframing of what scientific theory is); falsificationism
--     → paradigm (cross-cluster bridge T3→T4: Kuhn explicitly responds
--     to Popper''s falsificationism); duhem_quine_thesis → paradigm
--     (cross-cluster bridge T3→T4: Quinean holism is one of the key
--     argumentative levers Kuhn uses for paradigm-relativism). Paradigm
--     terminus (T5): paradigm → paradigm_shift (Kuhn''s second central
--     concept); paradigm → research_programme (Lakatos''s refinement);
--     paradigm → theory_ladenness_of_observation (Kuhn''s third central
--     concept, drawing on Hanson 1958); duhem_quine_thesis → theory_
--     ladenness_of_observation (cross-cluster bridge T3→T5: holism
--     and theory-ladenness reinforce each other — the Duhem-Quine
--     thesis is one route to theory-ladenness). Three central cross-
--     cluster bridges tie the nine clusters into a coherent within-
--     domain DAG: (a) falsificationism → paradigm (Kuhn''s
--     historicist reframing of scientific change is explicitly a
--     response to Popperian falsificationism — this bridge captures
--     the central Popper-Kuhn debate of the 1960s-1970s); (b)
--     duhem_quine_thesis → paradigm (Quinean confirmational holism is
--     one of the philosophical resources Kuhn draws on; this bridge
--     captures the convergence of confirmation-theoretic holism and
--     historicist paradigm-relativism); (c) duhem_quine_thesis →
--     theory_ladenness_of_observation (the holist thesis that no
--     observation is theory-neutral connects directly to the Hanson-
--     Kuhn-Feyerabend theory-ladenness thesis).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 14; DELETE FROM public.nodes WHERE id IN (the 27 ids inserted
--   here); UPDATE public.settings SET value = ''13''::jsonb WHERE key =
--   ''graph_version''; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 58 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry);
--   product/seed-graph/migrations/0070_seed_language_part1.sql (P5-08
--   philosophy-of-language seed; pattern reference for the most recent
--   single-task subject subdomain seed);
--   product/seed-graph/migrations/0046_seed_mind_part1.sql (P5-07b
--   philosophy-of-mind specialized seed; pattern reference for cluster-
--   bridge edge structure);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 13 at session boot (post-S-0071 state per ROUTING.md
-- narrative); write 14 here; every node/edge below carries
-- graph_version_added = 14.
UPDATE public.settings
  SET value = '14'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 27 INSERTs covering the nine philosophy-of-science clusters
-- (problem_of_induction is canonical-homed under epistemology in P5-01a
-- per phase_5.md T2-G #4 and intentionally not re-authored here).
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'philosophy_of_science',
    'Philosophy of Science',
    ARRAY['science'],
    'The philosophical study of the sciences as a form of inquiry: what scientific method is and whether there is one, what scientific theories are and how they relate to evidence, what scientific explanation accomplishes, whether the unobservable entities scientific theories posit are real, how scientific change happens across history, and whether and how values enter scientific work. The field is methodology-anchored — its central questions are about the structure of scientific reasoning rather than first-order claims about nature — and the analytic tradition has been the dominant idiom since the Vienna Circle in the 1920s-1930s.',
    'Frame the field for students by its central questions: (1) the method question — is there a scientific method, and if so what is it? (2) the confirmation question — how does evidence support scientific claims? (3) the explanation question — what does it take for a scientific account to explain a phenomenon? (4) the realism question — are the unobservable entities physics posits (electrons, fields, quarks) real? (5) the change question — how do scientific theories succeed each other across history? (6) the values question — can or should science be value-free? Each question has a canonical literature and a small number of canonical positions. The field is dominated by analytic philosophy of science (Hempel, Popper, Kuhn, Lakatos, Quine, Hanson, Feyerabend, Putnam, Boyd, Laudan, van Fraassen, Friedman, Kitcher, Lipton, Salmon, Cartwright, Suppes, Giere, Longino, Douglas) but key methodological figures sit awkwardly at the analytic/continental boundary (Polanyi, Feyerabend in his anarchist phase). For this seed, focus is on the methodology-anchored analytic surface; specializations (philosophy of physics, biology, chemistry, economics, medicine, statistics) are out of scope and live in Phase 6+ if and when telemetry warrants.',
    ARRAY['phil_science', 'philosophy_science'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'scientific_method',
    'Scientific Method',
    ARRAY['science'],
    'The activity of generating, testing, and refining empirical hypotheses about the natural world via observation, experiment, and inference — and the philosophical question of whether there is a single such method or many. The traditional textbook story (a stepwise procedure: observe, hypothesize, predict, test, conclude) is widely rejected by contemporary philosophy of science as a romanticized abstraction; the actual practice of the sciences is more pluralistic, more theory-laden, and more dependent on background commitments than any stepwise account captures.',
    'Use the contrast between textbook scientific method and post-Kuhnian critiques to motivate the topic. The textbook account: science proceeds by observation → hypothesis → prediction → experimental test → confirmation/refutation → theory. Each step is supposed to be impersonal, replicable, and methodologically neutral. The post-Kuhnian critique (Hanson 1958, Kuhn 1962, Feyerabend 1975): observation is theory-laden (what counts as relevant data depends on the theoretical framework); hypothesis-generation is creative and not reducible to a method; experimental testing depends on holistic background assumptions (Duhem-Quine); the inference from successful prediction to theory-confirmation is contestable. The methodology question splits: (1) is there *a* scientific method, common to all sciences? (Feyerabend: no; pluralists like Cartwright: many local methods; the textbook view: yes, the H-D method); (2) what *normative* lessons does it carry? — falsificationism prescribes one set of methodological rules, Bayesianism prescribes another. The contemporary mainstream is methodological pluralism: different sciences (physics, biology, social sciences) have different evidential standards, different theory-construction practices, different experimental protocols, and the philosopher of science is in the business of describing and clarifying these rather than legislating a single method.',
    ARRAY['method_scientific', 'sci_method'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'scientific_theory',
    'Scientific Theory',
    ARRAY['science'],
    'The systematic representation of a domain of phenomena that scientific inquiry produces — the central product (as distinct from the activity, scientific method, that produces it). What a scientific theory *is* metaphysically — a set of sentences, a structure, a family of models, a set of practices — is contested; what theories *do* (predict, explain, unify, classify, intervene) is broadly agreed.',
    'Help students see that "what is a scientific theory?" is itself a philosophical question with several answers. (1) The syntactic view (Carnap, Hempel, the logical positivists): a scientific theory is a set of sentences in a formal language, consisting of theoretical postulates plus correspondence rules linking theoretical terms to observable predicates. (2) The semantic view (Suppes 1957, van Fraassen 1980, Giere 1988): a scientific theory is a family of models — set-theoretic structures that satisfy the theory''s equations — and the theory is "applied" by claiming that some target system in the world is similar to one of those models in relevant respects. (3) The pragmatic view (Cartwright 1983, Hacking 1983): a scientific theory is a collection of practices, models, exemplars, and instruments — a "tool kit" rather than a body of axiomatized claims. The semantic view is the contemporary mainstream; the syntactic view dominated mid-twentieth-century philosophy of science but largely collapsed under the weight of theoretical-term-to-observable-predicate linkage problems; the pragmatic view is the influential alternative for sciences (chemistry, biology, engineering) where the model-theoretic framing fits awkwardly.',
    ARRAY['theory_scientific', 'sci_theory'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'scientific_explanation',
    'Scientific Explanation',
    ARRAY['science'],
    'The philosophical analysis of what it is for a scientific account to explain a phenomenon — to render it intelligible by exhibiting why it occurred or what it depends on. Explanation is closer to the heart of philosophy of science than confirmation: confirmation tells us when a theory is supported by evidence, but explanation tells us what the theory contributes when we have it. The dominant contemporary accounts are causal, mechanistic, model-based, and unification-theoretic.',
    'Set up the topic for students by distinguishing explanation from prediction (the H-D model conflates them; Salmon and others sharply separate them) and from description (the deductive-nomological account threatens to collapse explanation into systematic description; this was a central objection to it). The classical account is Hempel-Oppenheim 1948''s deductive-nomological model: an explanation is a sound deductive argument from premises that include at least one law of nature plus initial conditions, with the explanandum (the thing explained) as the conclusion. Counterexamples (the flagpole-and-shadow case where the shadow''s length and the angle of the sun deduce the flagpole''s height symmetrically — but the flagpole explains the shadow, not vice versa; the irrelevant-conjunction case where a true law plus an irrelevant initial condition still satisfies the schema) drove the field to alternative accounts: causal accounts (the explanans must causally produce the explanandum — Salmon, Lewis, Woodward); mechanistic accounts (the explanans must describe the mechanism — Bechtel, Machamer-Darden-Craver); inference-to-the-best-explanation accounts (explanation is inference from observed consequences to the hypothesis that, if true, would best explain them — Lipton, Harman); unification accounts (explanation is unification of disparate phenomena under a small number of patterns — Friedman, Kitcher).',
    ARRAY['explanation_scientific', 'sci_explanation'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'hypothetico_deductivism',
    'Hypothetico-Deductive Method',
    ARRAY['science'],
    'The view that scientific hypotheses are confirmed by deducing observational predictions from them and finding the predictions to hold. The dominant mid-twentieth-century account of confirmation in the analytic tradition — Hempel, Carnap (in some periods), Popper (negatively, via falsification), and the textbook account — though largely supplanted by Bayesian approaches in the contemporary literature for technical reasons (the irrelevant-conjunction problem, the tacking paradox, the inability to distinguish strong from weak confirmation).',
    'Set up the H-D schema for students: from hypothesis H plus auxiliary assumptions A, deduce observational prediction O. If O is observed, H is confirmed; if not-O is observed, H is disconfirmed. The schema is intuitively appealing — it captures something right about how scientists reason from hypotheses to tests — and was the textbook account of scientific reasoning for half a century. The technical objections (raised across the 1950s-1970s) are deep: (1) the tacking paradox: if H entails O, then so does H ∧ X for any irrelevant X; the H-D schema confirms the irrelevant conjunction equally to H. (2) the new-riddle problem (Goodman): the H-D schema is silent on which hypotheses to test, but the choice matters — testing "all emeralds are green" and testing "all emeralds are grue" have the same observational consequences before the projection cutoff but support incompatible predictions after. (3) the strength problem: the H-D schema gives a binary verdict (confirmed/disconfirmed) but science distinguishes degrees of confirmation. The Bayesian framework addresses all three: it compares posterior probabilities (irrelevant conjuncts wash out by likelihood-ratio considerations), it places the projection question on the prior (which projections deserve high prior probability is part of the analysis), and it gives continuous confirmation by likelihood-ratio updating. The H-D account is a useful starting point pedagogically but is no longer the contemporary mainstream account.',
    ARRAY['h_d_method', 'hd_method', 'hypothetico_deductive_method'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'bayesianism_confirmation',
    'Bayesian Confirmation Theory',
    ARRAY['science'],
    'The view that confirmation is a relation between hypothesis H and evidence E captured by Bayesian conditionalization: H is confirmed by E to the extent that E raises H''s posterior probability (P(H|E) > P(H)). The dominant contemporary account of confirmation, supplanting the H-D account in the analytic tradition since the 1970s. Bayesianism handles the technical problems that defeated H-D (irrelevant conjunctions, the strength problem, the tacking paradox) by relying on the formal apparatus of conditional probability.',
    'Walk students through the Bayesian framework: start with prior probabilities P(H) over a partition of hypotheses; on observing evidence E, update each hypothesis by Bayes''s theorem to its posterior P(H|E) = P(E|H)·P(H)/P(E). Confirmation is increase in posterior probability over prior. The framework solves H-D''s problems: irrelevant conjunctions wash out (P(H ∧ X|E) = P(H|E)·P(X|H ∧ E), with P(X|H ∧ E) = P(X) for irrelevant X — so confirmation of the conjunction is bounded by confirmation of H); the strength problem dissolves (confirmation comes in degrees, indexed by the magnitude of the posterior shift); the projection question is partly displaced onto the prior (which prior distributions are reasonable is a deeper question, but the framework does not pretend to be neutral on it). Bayesianism connects philosophy of science to epistemology (Bayesian epistemology — Joyce, Pettigrew, Howson-Urbach — uses the same formal apparatus to model rational belief), to formal decision theory (expected utility maximization), and to cognitive science (Bayesian models of perception, learning, and reasoning). Difficulties: the problem of priors (where do reasonable priors come from?); the problem of old evidence (Glymour 1980 — if E is already known, P(E) = 1, so Bayes update is trivial; how can old evidence still confirm new theories like general relativity?); the problem of logical omniscience (the framework assumes the agent knows all logical consequences of their beliefs, which is unrealistic).',
    ARRAY['bayesian_confirmation', 'bayesianism_in_science'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'paradox_of_the_ravens',
    'Paradox of the Ravens',
    ARRAY['science'],
    'Hempel''s paradox of confirmation: the hypothesis "all ravens are black" is logically equivalent to "all non-black things are non-ravens"; by Hempel''s 1945 equivalence condition, observing instances confirms equivalent hypotheses equally; but observing a white shoe (a non-black non-raven) seems to confirm "all ravens are black", which is absurd. The central technical puzzle in Hempelian confirmation theory and a load-bearing case for evaluating any confirmation account.',
    'Set up the puzzle for students step by step: (1) Hempel''s instance condition: if H is "all F are G", then observing an Fa that is also Ga confirms H. (2) Hempel''s equivalence condition: if H1 and H2 are logically equivalent, what confirms H1 confirms H2 equally. (3) "All ravens are black" is logically equivalent to "all non-black things are non-ravens" (contrapositive). (4) Observing a non-black non-raven (a white shoe, a yellow banana, a green leaf) is an instance of the contrapositive; by (1) and (2), it confirms "all ravens are black" — and by parity, observing anything other than a black raven (literally any non-black thing or any non-raven) confirms the hypothesis. This is absurd: we can confirm zoological generalizations from our sock drawer. Responses: (a) bite the bullet (Hempel''s own — accept the conclusion but argue the confirmation is so weak it is practically negligible); (b) reject the equivalence condition; (c) reject the instance condition (Goodman''s grue case is one route); (d) use a Bayesian framework where the relevant likelihood ratios give the white shoe a confirmation increment so small as to be unmeasurable while still preserving the qualitative result; (e) reject Hempel''s qualitative framework entirely in favor of a purely quantitative one. The Bayesian dissolution (b) plus quantitative reframing (d) is the contemporary mainstream resolution.',
    ARRAY['hempels_paradox', 'ravens_paradox', 'hempel_ravens'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'demarcation_problem',
    'Demarcation Problem',
    ARRAY['science'],
    'The problem of distinguishing genuine science from non-science (or pseudo-science) — articulated by Karl Popper in the 1930s as the central question of philosophy of science. Popper''s falsificationist solution proposed that a theory is scientific iff it is falsifiable: it makes predictions that could in principle be refuted by observation. Subsequent work has largely abandoned the search for a single criterion (Laudan 1983 "The Demise of the Demarcation Problem") in favor of a cluster-of-features account, while preserving demarcation as a live practical question for cases like astrology, parapsychology, intelligent-design creationism, and climate-change denial.',
    'Walk students through Popper''s motivation: in the 1920s-1930s, Popper was struck by the contrast between Einstein''s general relativity (which made specific, risky predictions like the bending of starlight near the sun, and would have been refuted if those predictions failed) and Marxist historical materialism / Freudian psychoanalysis (which seemed to explain everything in retrospect but made no predictions that could refute them). The asymmetry suggested a criterion: science is the activity that exposes itself to refutation. The criterion has the right shape — it picks out general relativity as paradigmatically scientific and astrology as paradigmatically pseudo-scientific — but suffers from technical problems: (1) holism (Duhem-Quine): no single hypothesis is falsifiable in isolation; auxiliary assumptions can always be revised to save the hypothesis. (2) the historical fact that scientists routinely save apparently-falsified theories by post-hoc auxiliary hypotheses — and this is sometimes the right thing to do (Mercury''s perihelion was an apparent falsification of Newtonian mechanics that turned out to vindicate it once general relativity was developed). (3) Laudan''s argument that no single feature suffices for demarcation; the best we can do is a cluster (testability, explanatory power, fruitfulness, agreement with established science, empirical adequacy, theoretical virtue). The contemporary view abandons the search for a single criterion but preserves the practical demarcation work — the pseudoscience-detection literature (Pigliucci, Boudry).',
    ARRAY['demarcation', 'science_pseudoscience_demarcation'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'falsificationism',
    'Falsificationism',
    ARRAY['science'],
    'Karl Popper''s 1934/1959 view that the criterion of scientific status is falsifiability (the theory makes predictions that could in principle be refuted by observation), and that science makes progress by attempting to falsify conjectures and discarding those that fail. Popper rejected both inductivism (no inference from particulars to generals is valid) and verificationism (theories cannot be conclusively verified, only falsified) — science is the systematic exposure of conjectures to refutation. Largely supplanted in the contemporary mainstream by Bayesian and other frameworks but remains influential in working scientists'' self-understanding.',
    'Walk students through the Popperian framework: the asymmetry of confirmation and refutation is logical — universal generalizations are not deducible from any finite set of confirming instances, but they *are* refutable by a single counterexample. So science cannot, on Popper''s view, *confirm* its hypotheses at all; what it can do is fail to refute them. A theory that has survived many serious refutation-attempts is *corroborated* (a Popperian term distinct from confirmed); corroboration is not probability. Popper''s methodology: scientists should propose bold conjectures (high content, hence high falsifiability), expose them to severe tests, and discard those that fail. Methodological criticisms: (1) Duhem-Quine holism: no single hypothesis is falsifiable in isolation, since deductive predictions depend on auxiliary assumptions; a failed prediction can always be located in the auxiliaries rather than the main hypothesis. (2) the practical fact that scientists often retain apparently-falsified theories by ad-hoc adjustments — and this is sometimes the rational thing to do. (3) Lakatos''s critique: Popper''s model treats theories as monolithic, but scientific work is organized around research programmes with hard cores that are protected from falsification by belt of auxiliary hypotheses. (4) Kuhn''s historical critique: the actual history of science shows long periods of normal science (puzzle-solving within a paradigm) punctuated by paradigm shifts — not a steady stream of conjecture-and-refutation. Popper remains a touchstone for working scientists but is no longer the dominant philosophical account.',
    ARRAY['popper_falsificationism', 'falsifiability', 'falsifiability_criterion'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'paradigm',
    'Paradigm (Kuhnian)',
    ARRAY['science'],
    'The shared framework of theoretical commitments, exemplary problem-solutions, instruments, and methodological norms that constitutes a scientific community at a given period. Introduced by Thomas Kuhn in The Structure of Scientific Revolutions (1962/1970) as the unit of scientific change: scientific work happens within paradigms (normal science) and paradigms succeed each other through paradigm shifts (scientific revolutions). The concept reframed philosophy of science around historical and sociological structure rather than purely logical structure.',
    'Walk students through Kuhn''s framework: a paradigm has two senses, which Kuhn distinguished in the 1969 postscript. (1) The disciplinary matrix: the entire constellation of beliefs, values, techniques, and exemplars shared by a scientific community — including symbolic generalizations (laws like F=ma), models of how the world works, values about what counts as a good theory, and exemplars (concrete problem-solutions that students learn to imitate). (2) The exemplar sense: the concrete problem-solutions that serve as models for further work — the harmonic-oscillator solution as the exemplar all of Newtonian mechanics works by analogy with. Both senses converge on the structural point: scientific work is not the application of an algorithm but the extension of exemplary work, by analogy and judgment, to new cases. Paradigms organize what counts as a problem, what counts as a solution, what counts as evidence, what counts as a serious objection. They are not theories in the syntactic sense — they are richer than any axiomatization can capture. The concept was transformative for philosophy of science: it placed historical and sociological work at the center (rather than as a supplement to logical analysis), and it reframed the realism-antirealism debate (paradigm-relativism is one form of antirealism: different paradigms answer to different worlds).',
    ARRAY['kuhnian_paradigm', 'kuhn_paradigm', 'disciplinary_matrix'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'paradigm_shift',
    'Paradigm Shift',
    ARRAY['science'],
    'The non-cumulative replacement of one paradigm by another in a scientific revolution — Kuhn''s second central concept. Paradigm shifts are not the gradual accumulation of better theories; they are gestalt-switch-like reorganizations of the scientific community''s framework, in which the new paradigm is *incommensurable* with the old (cannot be translated into the old without remainder, has different exemplars, different problems, different solutions, sometimes different ontology).',
    'Use Kuhn''s canonical examples to make the concept vivid for students: the Copernican revolution (heliocentrism replacing geocentrism — not just a change in calculation but a change in what astronomy is about); the chemical revolution (Lavoisier''s oxygen replacing Stahl''s phlogiston — the same combustion phenomena reorganized into a new chemical framework); the Einsteinian revolution (relativity replacing Newtonian mechanics — same observations reorganized under different conceptions of space, time, mass, and gravitation). In each case the new paradigm is not a refinement of the old; it is a different way of carving the world. Kuhn''s incommensurability thesis says: practitioners of the old paradigm and the new cannot fully communicate — they apply the same words to different referents, see different things in the same diagrams, count different events as data. This is the most controversial part of Kuhn''s view; critics (Putnam, Davidson, Hacking) have argued that Kuhn overstates incommensurability, that paradigm-shift cases are translationally tractable in principle. The mainstream contemporary view: paradigm shifts are real and important, but Kuhn''s incommensurability thesis is too strong — translation is hard but not impossible, and there is more rational continuity across revolutions than Kuhn allowed. Note that "paradigm shift" has been thoroughly absorbed into popular usage, often loosely; the technical Kuhnian sense is more specific.',
    ARRAY['scientific_revolution', 'kuhnian_revolution', 'kuhnian_paradigm_shift'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'research_programme',
    'Research Programme (Lakatos)',
    ARRAY['science'],
    'Imre Lakatos''s 1970 unit of methodological appraisal in philosophy of science, designed as a synthesis between Popper''s falsificationism and Kuhn''s paradigm-relativism. A research programme has a *hard core* of central commitments protected from refutation, a *protective belt* of auxiliary hypotheses that absorb apparent falsifications, and a *positive heuristic* directing the development of the programme. Programmes are appraised as *progressive* (predicting novel phenomena that turn out to be confirmed) or *degenerating* (saving phenomena only by post-hoc adjustment); the methodology is rationally to abandon degenerating programmes for progressive ones.',
    'Walk students through Lakatos''s framework as a refinement of Popper plus an absorption of Kuhn. From Popper: science aims at falsifiable theories and progresses through critical engagement. From Kuhn: scientific work is organized around larger structures than individual hypotheses (Lakatos''s research programmes vs. Kuhn''s paradigms), and apparent falsifications are routinely absorbed by adjusting auxiliary hypotheses (Lakatos''s protective belt). The synthesis: appraise programmes (not individual hypotheses) over time. A *progressive* programme generates novel predictions that the protective belt can defend and that turn out to be empirically confirmed (Newtonian mechanics from 1687 to ~1850 — predicting tides, perturbations, the existence of Neptune); a *degenerating* programme can only absorb apparent falsifications by ad-hoc adjustments that yield no novel content (Marxist historical predictions in the twentieth century, on Lakatos''s example). Methodologically: it is rational to work in a progressive programme and rational to abandon a degenerating one for a more progressive alternative — but the appraisal is *historical*, not synchronic. A degenerating programme might recover; a progressive one might degenerate. Lakatos''s framework is widely taught and influential but criticized for under-determining when appraisal-shifts should occur and for relying on a "novel prediction" criterion that is harder to apply than Lakatos suggested.',
    ARRAY['lakatos_programme', 'methodology_of_research_programmes', 'mssrp'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'deductive_nomological_model',
    'Deductive-Nomological Model of Explanation',
    ARRAY['science'],
    'Hempel and Oppenheim''s 1948 account of scientific explanation: an explanation is a sound deductive argument from premises that include at least one universal law of nature plus particular initial conditions, with the explanandum (the thing to be explained) as the conclusion. The classical formal account of scientific explanation, dominant from 1948 to ~1970 and the touchstone for all subsequent accounts. Largely defeated by counterexamples (the flagpole case, the irrelevant-conjunction case, the asymmetry case) but remains the default starting point for any discussion of explanation.',
    'Set up the D-N schema for students: explanans (the explaining premises) consists of laws L1, L2, ... Ln plus initial conditions C1, C2, ... Cm; the explanandum (the thing explained) is logically deducible from the explanans. The schema is appealingly clean: explanation is essentially the same as prediction (the only difference is temporal — predictions look forward, explanations look back), and explanation reduces to the logical structure of the argument. Counterexamples that brought it down: (1) the *symmetry* problem (Bromberger 1966): from "the angle of the sun is θ and the flagpole is h tall and light travels in straight lines" we can deduce "the shadow is L = h/tan(θ)"; from "the angle of the sun is θ and the shadow is L and light travels in straight lines" we can deduce "the flagpole is h = L·tan(θ)". The D-N schema is satisfied in both directions, but only the first is a genuine explanation — the flagpole''s height explains the shadow''s length, not vice versa. The asymmetry suggests explanation requires more than deductive structure — it requires causal direction. (2) the *irrelevance* problem: from "Mr. Smith took birth control pills and males who take birth control pills do not become pregnant" we can deduce "Mr. Smith did not become pregnant"; the D-N schema is satisfied but the explanation is absurd (Mr. Smith does not become pregnant because he is male, not because he took the pills). (3) statistical-explanation cases: most actual scientific explanations cite statistical regularities, not strict universals; Hempel-Oppenheim''s schema covers only deterministic explanations. The post-D-N landscape splits into causal accounts, mechanistic accounts, IBE, and unification accounts.',
    ARRAY['dn_model', 'hempel_oppenheim_model', 'covering_law_model', 'd_n_explanation'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'inference_to_the_best_explanation',
    'Inference to the Best Explanation',
    ARRAY['science'],
    'The view that scientific (and ordinary) reasoning is centrally constituted by inference from a body of observations to the hypothesis that, if true, would best explain them. Articulated as a general framework by Gilbert Harman in 1965 and developed extensively by Peter Lipton in Inference to the Best Explanation (1991/2004). IBE is the dominant contemporary account of inferential reasoning in science alongside Bayesian confirmation theory, and is a central plank in arguments for scientific realism (the no-miracles argument is a form of IBE).',
    'Walk students through the IBE structure: from a body of evidence E, infer the hypothesis H such that, if H were true, H would best explain E. The framework is naturally decomposed into two questions: (1) what makes one hypothesis a *better explanation* than another? (Lipton''s answer: a combination of *loveliness* — explanatory power, depth, unification — and *likeliness* — antecedent plausibility); (2) what justifies the inference from "best explanation" to "probably true"? (the central worry: the best of a bad lot might still be quite bad — IBE only delivers a true conclusion if the true hypothesis is in the comparison class). IBE captures something right about how scientists reason — when evidence underdetermines theory choice, scientists weigh explanatory considerations (does this hypothesis unify the data? does it predict novel phenomena? does it cohere with established theory?) and infer to the hypothesis that best satisfies them. The relation to Bayesianism is contested: some Bayesians (van Fraassen, Lipton) treat IBE as a non-Bayesian alternative or as a heuristic for setting Bayesian priors; others (Lipton again, in some moods; Okasha) treat IBE as a special case of Bayesian inference once the Bayesian apparatus is properly set up. IBE is central to the realism debate: the no-miracles argument is the IBE that the success of mature science is best explained by the approximate truth of its theories, so we should infer the truth (or approximate truth) of those theories.',
    ARRAY['ibe', 'best_explanation_inference', 'abductive_inference'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'unification_theory_of_explanation',
    'Unification Theory of Explanation',
    ARRAY['science'],
    'The view that scientific explanation consists in the unification of disparate phenomena under a small number of explanatory patterns. Developed by Michael Friedman (1974) and extended by Philip Kitcher (1981, 1989), the unification account is one of the major post-D-N alternatives, alongside causal and mechanistic accounts. On the unification view, a theory explains by reducing the number of independent phenomena that need to be accepted as brute — by bringing many explananda under a small number of argument patterns.',
    'Walk students through the Friedman-Kitcher framework: the explanatory power of a theory is measured by how much it unifies — how many disparate phenomena it brings under a single pattern of explanation. Newton''s mechanics is paradigmatically unifying: it brought planetary motion (Kepler''s laws), terrestrial motion (Galileo''s laws of falling bodies), and tides under a single argument pattern (the inverse-square law of gravitation plus F=ma). Maxwell''s electromagnetism brought electricity, magnetism, and light under a single set of equations. The contemporary unification account (Kitcher) makes this precise: the explanatory store of a theory is the smallest set of argument patterns that, when applied as widely as possible, yields the most theorems of the theory; explanatory power is measured by the unification this achieves. The view captures one of the central scientific virtues — when Maxwell unified electricity and magnetism, this was felt to be explanatory progress, not just calculational economy. Difficulties: (1) unification can be cheap (any two unrelated theories can be conjoined into a "unified" theory by simple conjunction; the unification account needs to rule this out); (2) some explanations seem to be local rather than unifying (mechanistic explanations of biological phenomena often resist unification); (3) the relation to causation is unclear (is unification a kind of causal explanation, or an alternative to causal explanation?).',
    ARRAY['friedman_kitcher_unification', 'unification_explanation', 'unificationism_explanation'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'scientific_realism',
    'Scientific Realism',
    ARRAY['science'],
    'The view that mature scientific theories are (approximately) true, that their theoretical terms refer to real entities (including unobservable ones like electrons and fields), and that science makes genuine cumulative progress toward truth about the world. The central position in the realism debate, opposed by various antirealisms (constructive empiricism, instrumentalism, social constructivism, paradigm-relativism). The contemporary realism debate is methodology-anchored — the question is what status to attribute to the unobservable entities scientific theories posit, given that we never observe them directly.',
    'Walk students through the realist position by contrasting it with antirealism. Realism: (1) semantic — theoretical claims have truth-value (electrons exist or do not exist, full stop); (2) epistemic — we have warrant to believe mature theories are approximately true; (3) metaphysical — the unobservable entities theories posit are mind-independently real. Antirealism rejects one or more: instrumentalism rejects (1) (theoretical claims are instruments for prediction, not truth-evaluable); constructive empiricism (van Fraassen) rejects (2) (theories aim at empirical adequacy, not truth, and we are not entitled to believe their unobservable claims); social constructivism rejects (3) (the entities are constituted by scientific practice, not independently real). The two central arguments shape the debate: the *no-miracles argument* (Putnam-Boyd) — the predictive success of mature science would be a miracle if the theories were not approximately true; therefore we should infer they are approximately true. The *pessimistic meta-induction* (Laudan) — the history of science is a graveyard of formerly successful theories that turned out to be false (caloric, phlogiston, ether, classical mechanics); by induction we should expect current theories to share that fate. The contemporary debate has produced refinements: structural realism (Worrall, Ladyman) splits the difference — preserve realism about structure even if entities change. Selective realism (Psillos) — be realist only about the parts of theories that play a working role in their predictive success.',
    ARRAY['realism_in_science', 'scientific_realism_position'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'constructive_empiricism',
    'Constructive Empiricism',
    ARRAY['science'],
    'Bas van Fraassen''s 1980 antirealist position in The Scientific Image: science aims at *empirical adequacy* (saving the phenomena), not truth, and theory acceptance involves belief in empirical adequacy plus commitment to use the theory but not belief in the truth of its unobservable claims. The dominant contemporary antirealist position, defining itself against scientific realism while preserving most of the realist''s framework about theory acceptance and scientific practice.',
    'Walk students through van Fraassen''s position. Constructive empiricism makes a sharp observable/unobservable distinction: observable entities are those a properly-functioning human observer could in principle observe directly (a planet, a moon, a moss); unobservable entities are those that no human could observe directly even in principle (an electron, a quark, a field). Theories make claims about both. Van Fraassen: science aims to find theories that are empirically adequate — that "save the phenomena", that get the observable consequences right. Theories that do this are acceptable for use; we are not entitled to believe their unobservable claims, only to believe they are empirically adequate. Theory acceptance has two components: belief in empirical adequacy and a pragmatic commitment to use the theory (its language, its puzzles, its explanatory schemata). The framework preserves most of scientific realism''s account of practice (scientists work within theories, take their commitments seriously, develop them) while rejecting the realist''s metaphysical claim about the entities. Van Fraassen''s arguments: (1) the observable/unobservable line is principled (anchored in the limits of human perception, even if currently extended by instruments); (2) the no-miracles argument fails (the success of science can be explained by the empirical adequacy of theories, without needing to invoke their truth — Darwinian-style selection of theories that work); (3) the historical record favors humility about what survives (pessimistic meta-induction). Critics (Churchland, Psillos, Hacking) have pressed the observable/unobservable line and the legitimacy of inference to unobservables.',
    ARRAY['van_fraassen_empiricism', 'empirical_adequacy_view'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'no_miracles_argument',
    'No-Miracles Argument',
    ARRAY['science'],
    'The central argument for scientific realism: the predictive and practical success of mature scientific theories would be a miracle if the theories were not (approximately) true; the only non-miraculous explanation of scientific success is that science is approximately true; therefore we should be scientific realists. Articulated by Hilary Putnam (1975) and developed by Richard Boyd (1983); its structure is an inference to the best explanation operating at the meta-level (about scientific success itself, not about a particular theory).',
    'Walk students through the argument''s structure. Premise 1: mature scientific theories are predictively and practically successful — they predict novel phenomena, support technological intervention, unify disparate domains, and continue to do so under sustained testing. Premise 2: this success would be a stunning coincidence (a "miracle") if the theories did not somehow latch onto the structure of reality. Premise 3: the best explanation of the success is that the theories are approximately true — they do latch onto the structure of reality (or much of it). Conclusion: we should be scientific realists. The argument is a form of inference to the best explanation operating at the meta-level: the explanandum is the success of science itself, the candidate explanations are realism (theories are true) and antirealism (theories happen to work despite being false), and the realist explanation is judged best. The argument''s force depends on the implausibility of antirealist alternatives — if the antirealist can offer a non-truth-involving explanation of success (van Fraassen''s Darwinian selection of empirically adequate theories; Stanford''s "unconceived alternatives" account), the argument''s grip loosens. The pessimistic meta-induction is the major counter-argument — it argues that the history of science shows successful theories repeatedly turn out to be false, so the inference from success to truth is empirically unwarranted.',
    ARRAY['putnam_no_miracles', 'miracle_argument', 'success_of_science_argument'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'pessimistic_meta_induction',
    'Pessimistic Meta-Induction',
    ARRAY['science'],
    'Larry Laudan''s 1981 argument against scientific realism: the history of science is full of theories that were predictively successful in their time but later turned out to be false (the caloric theory of heat, the phlogiston theory of combustion, the ether theory of light, classical Newtonian mechanics); by induction from this historical record, current successful theories are likely to be false too; therefore the inference from success to truth (the no-miracles argument) is empirically unwarranted. The central anti-realist counter-argument and a load-bearing case in the contemporary realism debate.',
    'Walk students through Laudan''s historical case. The argument''s structure is itself an induction: a base of cases (historical theories that were predictively successful but turned out false), a generalization (predictively successful theories often turn out false), and a projection to current theories (current predictively successful theories will probably also turn out false). Laudan''s 1981 list included roughly a dozen examples: the caloric theory of heat (predictively successful in chemistry and engineering, turned out false — heat is molecular motion, not a fluid); phlogiston (likewise); the optical ether (predictively successful in nineteenth-century optics, turned out false — there is no ether); Newtonian mechanics (predictively successful for two centuries, turned out false at high velocities and small scales); the crystalline-spheres model of the heavens; humoral medicine; spontaneous generation. The argument''s force: if predictive success has historically not been a reliable guide to truth, why should we treat it as a reliable guide now? Realist responses: (1) selective realism (Psillos) — be realist only about the parts of theories that play working roles in their successful predictions; the predictively load-bearing parts of caloric theory survive in modern thermodynamics, the load-bearing parts of phlogiston survive in modern combustion chemistry, etc. (2) structural realism (Worrall) — preserve realism about mathematical structure even when ontology changes; the equations of classical mechanics survive (in low-velocity limits) within general relativity. (3) reframe success as "novel predictive success" — many of Laudan''s examples had limited novel predictive success, so the realist target is narrower than Laudan suggests.',
    ARRAY['laudan_pmi', 'pmi', 'historical_argument_against_realism'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'underdetermination',
    'Underdetermination of Theory by Data',
    ARRAY['science'],
    'The thesis that any body of empirical evidence is compatible with multiple incompatible theories: data underdetermine theory choice. The thesis comes in several strengths: weak underdetermination (there are always *some* alternative theories compatible with any data); strong underdetermination (for any theory we accept, there is a serious empirically-equivalent rival); transient underdetermination (data underdetermine theory choice at a given time, even if more data later distinguishes the theories). Underdetermination is a central pressure point for scientific realism (if data underdetermine theory, what justifies belief in any particular theory?) and a central premise in many antirealist arguments.',
    'Walk students through the underdetermination thesis at three strengths. Weak: the deductive structure of confirmation guarantees that any finite body of data is compatible with infinitely many theories (curve-fitting cases — given any finite set of data points, infinitely many curves pass through them). This is uncontroversial but methodologically tame: simplicity, fit with background theory, and other theoretical virtues distinguish among the curves. Strong (Quine 1975): for any theory we accept, there is a serious empirically-equivalent rival — a theory that makes exactly the same observable predictions, differs in unobservable claims, and has comparable theoretical virtue. This is the philosophically explosive form: if true, it threatens the realist''s inference from successful theory to true theory (the rival is equally successful, but they cannot both be true). Quine''s example: the choice between Newtonian mechanics with absolute space and a Newtonian mechanics with the spatial framework reinterpreted as a convention. Transient (Stanford 2006): we have repeatedly failed to imagine the relevant alternatives to the theories we accept; subsequent science has overturned theories not by disconfirming them but by introducing previously unconceived alternatives that were also empirically adequate. The realist responses: (1) reject strong underdetermination (skeptics about empirically-equivalent-but-distinct theories — Laudan, Leplin); (2) accept underdetermination but appeal to non-empirical theoretical virtues (simplicity, unification, explanatory depth) to break ties; (3) embrace selective realism, being realist only about parts of theories that survive across the underdetermination space.',
    ARRAY['underdetermination_thesis', 'theory_underdetermination', 'data_theory_underdetermination'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'duhem_quine_thesis',
    'Duhem-Quine Thesis',
    ARRAY['science'],
    'The thesis that hypotheses are tested only as parts of larger theoretical wholes: a single hypothesis cannot be falsified in isolation because any apparent falsification can be located in auxiliary assumptions rather than in the hypothesis itself. Articulated by Pierre Duhem in 1906 (The Aim and Structure of Physical Theory) for physics specifically, generalized by W. V. O. Quine in 1951 ("Two Dogmas of Empiricism") to all empirical theory. The thesis is the canonical articulation of confirmational holism and a central technical pressure on Popperian falsificationism.',
    'Walk students through the thesis carefully. Duhem''s point: in physics, deriving an observational prediction from a hypothesis H requires auxiliary assumptions A — about the experimental apparatus, about the conditions of observation, about the laws governing measurement instruments. The deductive prediction is from H ∧ A, not from H alone. So if the prediction fails, what is refuted is the conjunction H ∧ A, not H. The experimenter has logical latitude to locate the failure in A rather than H — to revise the auxiliary assumptions and save the hypothesis. Quine''s generalization: this is true not just in physics but throughout empirical knowledge — every empirical claim is tested only in conjunction with its theoretical neighbors and with general principles of inference. Knowledge is a "web of belief" that meets experience at the periphery; recalcitrant experience can be accommodated by revising any part of the web, with the choice of which part to revise constrained only by considerations of conservatism, simplicity, and explanatory power. Implications: (1) Popperian falsification is logically defective — no individual hypothesis is falsifiable in isolation; (2) underdetermination is structural — given the latitude to revise auxiliaries, multiple incompatible theories are typically compatible with the same data; (3) the analytic/synthetic distinction collapses — every supposedly-analytic truth could in principle be revised under sufficient empirical pressure (Quine''s second dogma); (4) confirmational holism — confirmation flows to entire theoretical wholes, not to individual hypotheses. The thesis is foundational for confirmational holism in contemporary epistemology and philosophy of science.',
    ARRAY['duhem_quine', 'confirmational_holism', 'web_of_belief'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'theory_ladenness_of_observation',
    'Theory-Ladenness of Observation',
    ARRAY['science'],
    'The thesis that scientific observation is not theory-neutral — what one observes depends on one''s theoretical framework, conceptual training, and prior expectations. Articulated by Norwood Russell Hanson in Patterns of Discovery (1958) using gestalt-perception examples, and central to Kuhn''s (1962) and Feyerabend''s (1975) historicist accounts of scientific change. The thesis is a major source of paradigm-relativism and a central plank in arguments against the empiricist "given" of theory-neutral data.',
    'Use Hanson''s examples and Kuhn''s extensions to make the thesis vivid for students. Hanson''s gestalt cases: when Tycho Brahe and Kepler watch the sun rise, do they see the same thing? On a naive view, yes — they both see the sun appear over the horizon. On Hanson''s view, no — Brahe (a geocentrist) sees the sun moving up; Kepler (a heliocentrist) sees the horizon falling away to reveal a stationary sun. What they see depends on what theory they have internalized about the structure of the solar system. The thesis generalizes: an X-ray image looks like a meaningless gray smear to the untrained, but a trained radiologist sees pneumonia, fluid in the lung, calcification; an oscilloscope trace looks like a green line to a layperson but reveals a specific waveform pattern to an electrical engineer. The relevant framework is required to see the relevant features. Kuhn''s extension: scientific practitioners trained in different paradigms see different things in the same instruments, the same diagrams, the same experimental setups — and this contributes to incommensurability across paradigms. Feyerabend (in his anarchist phase): the thesis dissolves any sharp distinction between observation and theory, undercutting any methodology that relies on neutral data. Critics (Fodor 1984 The Modularity of Mind) have argued the thesis is overstated: perception has substantial modular, theory-neutral structure (pre-attentive shape perception, object recognition) that is not penetrated by higher-order theoretical commitments. The contemporary view: observation is *partly* theory-laden in upstream cognitive processing but has substantial theory-neutral structure at the perceptual level — too laden to support naive empiricism, too modular to support strong incommensurability.',
    ARRAY['hanson_thesis', 'observation_theory_laden', 'theory_loaded_observation'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'law_of_nature',
    'Law of Nature',
    ARRAY['science'],
    'The traditional explanatory and predictive currency of the sciences: a true generalization of unrestricted scope describing how things must be (or, on regularity views, how things are everywhere and always). The metaphysics of laws — what makes a generalization a law as opposed to a mere accidental regularity — is contested: regularity theories (Hume, Mill, Lewis) treat laws as just regularities, the necessitarian/governing-laws view (Armstrong, Dretske, Tooley) treats laws as relations between universals that govern instances, dispositional essentialism (Bird, Ellis) treats laws as flowing from the essences of natural kinds.',
    'Set up the topic for students with the canonical contrast: "all golden spheres are less than a mile in diameter" is presumably true (no one has ever made one) and "all uranium spheres are less than a mile in diameter" is presumably true (the critical mass would prevent it). Both are true generalizations of unrestricted scope. But the second is a law (it follows from physics); the first is an accidental regularity (it could have been false; nothing in nature requires golden spheres to be small). What distinguishes laws from accidental regularities? Three main answers. (1) Regularity views (Hume, Mill, the Mill-Ramsey-Lewis view): laws are just regularities, distinguished from accidents by their place in the simplest, strongest deductive system that captures all the regularities. There is no further fact about laws — Lewis''s "Humean supervenience" — beyond the mosaic of categorical facts. (2) Necessitarian / governing-laws views (Armstrong 1983, Dretske 1977, Tooley 1977): laws are second-order relations of necessitation between universals (N(F,G) means "Fness necessitates Gness"); these relations *govern* the instances and explain why the regularities hold. (3) Dispositional essentialism (Bird 2007, Ellis 2001): natural kinds have essential dispositions; laws are derivative from the essential dispositions of kinds (water is essentially H2O, and its essential dispositions include the laws of its behavior). The contemporary debate is unresolved; each view has its constituency. The distinction between laws and ceteris-paribus generalizations (in special sciences) is a separate live issue (Cartwright''s "How the Laws of Physics Lie" 1983, Schiffer, Pietroski-Rey).',
    ARRAY['natural_law', 'law_of_physics', 'scientific_law'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'scientific_model',
    'Scientific Model',
    ARRAY['science'],
    'A representation of a target system used in scientific reasoning — concrete or abstract, mathematical or physical, idealized or realistic. Models have become central to philosophy of science since the 1980s as the alternative to the syntactic conception of theories: rather than scientific theories being sets of sentences, theories are families of models, and scientific reasoning is centrally model-based. Key figures: Patrick Suppes, Ronald Giere, Bas van Fraassen, Nancy Cartwright, Margaret Morrison.',
    'Walk students through the diversity of scientific models. (1) Mathematical models: the Hardy-Weinberg equation in population genetics, the Black-Scholes model in finance, the Lotka-Volterra equations in ecology — sets of equations that describe the dynamics of a target system, often with substantial idealization (no migration, no selection, no genetic drift in Hardy-Weinberg). (2) Physical models: the double-helix model of DNA, ball-and-stick chemistry models, scale models of planes for wind-tunnel testing — concrete physical objects that share structural features with the target. (3) Computational models: climate models, weather models, neural-network models of cognition — running simulations that mimic target dynamics. (4) Idealized models: Galilean idealization (frictionless planes), the ideal gas, the perfectly competitive market — models that deliberately misrepresent the target by abstracting away features judged inessential. The semantic/model-theoretic view of theories (Suppes, van Fraassen, Giere, Suppe): a theory is a family of such models; the theory is "applied" by claiming that the target system is *similar* to one of the models in relevant respects. This handles the holistic and pragmatic features of scientific work better than the syntactic view: the same equations can model many different targets (the harmonic oscillator models pendula, springs, LC circuits...); different equations can model the same target with different fidelities; idealization and approximation are central to model use. The model-based view is the dominant framework in contemporary philosophy of science, alongside the practice-based view (Cartwright, Hacking) that emphasizes models as one of many scientific practices.',
    ARRAY['scientific_modeling', 'model_in_science', 'representation_scientific'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'reductionism_in_science',
    'Reductionism (in Science)',
    ARRAY['science'],
    'The view that the theories and phenomena of higher-level (special) sciences are (or could in principle be) reducible to the theories and phenomena of fundamental physics. Reductionism comes in several forms: ontological (everything is composed of fundamental physical entities — broadly accepted), theoretical (special-science theories are derivable from physics plus bridge laws — heavily contested), explanatory (special-science explanations bottom out in physical mechanisms — partly accepted, partly contested). The contemporary mainstream is non-reductive physicalism: ontological reduction without theoretical or explanatory reduction.',
    'Walk students through the three senses of reductionism. (1) Ontological reductionism: every entity is composed of, or supervenes on, fundamental physical entities (atoms, particles, fields). Almost universally accepted in contemporary philosophy of science (with debate at the margins about emergent properties). (2) Theoretical reductionism (Nagel 1961): theories of one science are derivable from theories of a more fundamental science via bridge laws (the gas laws derive from statistical mechanics; thermodynamic temperature reduces to mean kinetic energy). The Nagelian model was the mid-twentieth-century textbook account but has been heavily attacked: actual cases of intertheoretic reduction are few, partial, and approximate; bridge laws are typically not biconditionals but only one-directional implications; the special sciences (biology, psychology, economics, sociology) have failed to reduce to physics in the strict Nagelian sense. (3) Explanatory reductionism: the explanations of phenomena in special sciences ultimately bottom out in mechanisms describable at lower levels of organization. Partly accepted (mechanistic explanations in molecular biology, neuroscience) but contested for cases where higher-level patterns appear genuinely explanatory and not "merely" derivative (Putnam''s 1975 square peg / round hole — the geometric explanation for why the peg does not fit is at the level of geometry, not at the level of the physics of constituent atoms). The contemporary mainstream: non-reductive physicalism — accept ontological reduction, deny theoretical and (in many cases) explanatory reduction. The position is associated with the multiple-realizability argument and with functionalism in philosophy of mind.',
    ARRAY['scientific_reductionism', 'reduction_science', 'theoretical_reduction'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'multiple_realizability_in_science',
    'Multiple Realizability (Anti-Reductionist Argument)',
    ARRAY['science'],
    'The argument that the kinds and properties of higher-level (special) sciences are *multiply realizable* by different lower-level configurations, so the higher-level theories are not reducible to lower-level theories: pain is realizable in human neural tissue, octopus neural tissue, hypothetical silicon-based brains, etc.; if pain is identical to any specific neural configuration, the others would not be pain. The argument originates in Hilary Putnam''s 1967 "The Nature of Mental States" as a philosophy-of-mind argument against type-identity theory; Jerry Fodor''s 1974 "Special Sciences" generalized it to all special sciences as the central anti-reductionist argument.',
    'Walk students through Putnam''s argument first. Type-identity theory says mental states are identical to brain states (pain = C-fiber firing). Putnam''s objection: pain seems realizable in many different physical substrates — humans (C-fibers), other mammals (different neural configurations), invertebrates (radically different nervous systems), hypothetical aliens (silicon-based brains), eventually maybe digital computers (different again). If pain is identical to one of these configurations, the others are not pain — but they all *seem* to be pain. So pain is not identical to any specific physical configuration; pain is a *functional* state defined by its causal role, and that role can be realized in many different ways. Fodor''s 1974 generalization: not just mental states but all special-science kinds are multiply realizable. Money is realizable in cowrie shells, gold coins, paper currency, electronic balances — any reductive identification of money with one realization fails. Geological kinds, economic kinds, biological kinds, computational kinds — all multiply realizable, all irreducible to physics. The argument is the canonical case for non-reductive physicalism (the higher-level theories are autonomous from physics) and for functionalism in philosophy of mind. Critics (Kim 1992, Bickle 1998, Polger-Shapiro 2016) have pressed back: (1) the multiple realizability is often less radical than claimed (in practice, multiple realizers share substantial structure); (2) reduction is often *local* and *approximate* — physics doesn''t reduce special sciences in a single global theorem, but it does in domain-specific cases; (3) the relation between functional kinds and their realizers can support a more nuanced non-reductionism than the standard story.',
    ARRAY['multiple_realizability', 'fodor_special_sciences', 'putnam_multiple_realizability'],
    'INTERPRETED',
    'ai-seed',
    14
  ),
  (
    'value_free_ideal',
    'Value-Free Ideal',
    ARRAY['science'],
    'The view that scientific inquiry can and should be value-free: that scientists should not let non-epistemic values (moral, political, social, economic) influence their judgments about which hypotheses to accept, which evidence to weigh, or what to conclude. The ideal has been defended by classical philosophy of science (the logical positivists, much of mid-twentieth-century methodology) and challenged by feminist philosophy of science (Longino), the inductive-risk argument (Rudner, Douglas), and historicist work (Kuhn on values internal to paradigms). The contemporary mainstream rejects the strong version of the value-free ideal while preserving a more nuanced account of the proper place of values in science.',
    'Walk students through the value-free ideal and its critics. The classical position (Reichenbach''s context of discovery / context of justification distinction; the logical positivist program; much of mid-twentieth-century methodology): values may influence the *choice of research question* (the context of discovery is anything-goes), but they should not influence the *evaluation of evidence and the acceptance of theories* (the context of justification must be value-free if science is to be objective). Three main lines of critique: (1) The inductive-risk argument (Rudner 1953, Douglas 2009): theory acceptance always involves a risk of error (false positives, false negatives); the magnitude of acceptable risk depends on the practical consequences of error (accepting a false theory about drug safety carries different costs than accepting a false theory in pure mathematics); rationally calibrating the risk requires non-epistemic value judgments; therefore science cannot be value-free in the context of justification. (2) The feminist critique (Longino 1990, Anderson 2004, Kourany 2010): "epistemic" values (simplicity, scope, fruitfulness) are not value-neutral — they reflect substantive commitments about what science is for; the boundary between epistemic and non-epistemic values cannot be drawn in a principled way; female and minority perspectives have historically been excluded from the scientific community, with substantive consequences for what hypotheses get tested. (3) The Kuhnian critique: paradigms include value-commitments (about what counts as a good theory, what counts as a serious problem); these are internal to scientific practice rather than external impositions. The contemporary mainstream view: values are unavoidable in science but the right response is not to deny them but to make them transparent, to invite criticism, and to design scientific institutions that make value-influenced reasoning accountable.',
    ARRAY['value_freedom_science', 'value_neutral_science', 'value_laden_science'],
    'INTERPRETED',
    'ai-seed',
    14
  );

-- Edges: 30 within-domain pedagogical_prerequisite INSERTs (the two
-- otherwise-natural edges involving problem_of_induction —
-- scientific_method -> problem_of_induction and problem_of_induction
-- -> bayesianism_confirmation — are cross-domain because
-- problem_of_induction is canonical-homed under epistemology, and per
-- phase_5.md T2-G #1 cross-domain edges are P5-11's exclusive
-- responsibility).
-- Foundation spine (T0 -> T1): philosophy_of_science -> {scientific_method,
-- scientific_theory, scientific_explanation}.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  ('philosophy_of_science', 'scientific_method', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('philosophy_of_science', 'scientific_theory', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('philosophy_of_science', 'scientific_explanation', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- scientific_method -> {confirmation cluster, demarcation cluster, underdetermination, value_free_ideal}.
  -- (problem_of_induction omitted: already seeded under epistemology in P5-01a; cross-domain edge from scientific_method is P5-11's responsibility)
  ('scientific_method', 'hypothetico_deductivism', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_method', 'demarcation_problem', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_method', 'underdetermination', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_method', 'value_free_ideal', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- scientific_theory -> {realism, laws, models, reductionism, paradigm (skip-tier)}.
  ('scientific_theory', 'scientific_realism', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_theory', 'law_of_nature', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_theory', 'scientific_model', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_theory', 'reductionism_in_science', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_theory', 'paradigm', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- scientific_explanation -> {D-N, IBE (skip-tier), unification (skip-tier)}.
  ('scientific_explanation', 'deductive_nomological_model', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_explanation', 'inference_to_the_best_explanation', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_explanation', 'unification_theory_of_explanation', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Confirmation cluster (T2 -> T3 within cluster + cross-cluster bridge).
  -- (problem_of_induction -> bayesianism_confirmation omitted: cross-domain edge to epistemology, P5-11's responsibility)
  ('hypothetico_deductivism', 'paradox_of_the_ravens', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('hypothetico_deductivism', 'bayesianism_confirmation', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Demarcation cluster.
  ('demarcation_problem', 'falsificationism', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Realism cluster.
  ('scientific_realism', 'constructive_empiricism', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_realism', 'no_miracles_argument', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('scientific_realism', 'pessimistic_meta_induction', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Reduction cluster.
  ('reductionism_in_science', 'multiple_realizability_in_science', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Underdetermination cluster.
  ('underdetermination', 'duhem_quine_thesis', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Explanation chain (D-N -> IBE).
  ('deductive_nomological_model', 'inference_to_the_best_explanation', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Cross-cluster bridges into paradigm (T4): falsificationism (Popper -> Kuhn), duhem_quine_thesis (holism -> paradigm).
  ('falsificationism', 'paradigm', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('duhem_quine_thesis', 'paradigm', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Paradigm terminus (T4 -> T5).
  ('paradigm', 'paradigm_shift', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('paradigm', 'research_programme', 'pedagogical_prerequisite', 'ai-seed', 14),
  ('paradigm', 'theory_ladenness_of_observation', 'pedagogical_prerequisite', 'ai-seed', 14),
  -- Cross-cluster bridge: Duhem-Quine holism reinforces theory-ladenness.
  ('duhem_quine_thesis', 'theory_ladenness_of_observation', 'pedagogical_prerequisite', 'ai-seed', 14);

COMMIT;
