-- Migration: 0016_seed_epistemology_part1
-- Purpose: Second Phase 5 seed migration — specialized epistemology
--   concepts and within-domain pedagogical_prerequisite edges. Authored
--   in S-0053 against task P5-01b "Epistemology specialized seed" of
--   target T-PHASE-5 per engine/build_readiness/phase_5.md (gate report)
--   and product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the specialized half of epistemology that S-0050's P5-01a
--   foundational seed (knowledge / justification / belief / Gettier /
--   theories of justification / closure / certainty / cartesian
--   skepticism) intentionally deferred: social epistemology, virtue
--   epistemology, formal/Bayesian epistemology, reliabilism (as a
--   theory in its own right, distinct from externalism the access
--   thesis), knowledge-first epistemology (Williamson), understanding
--   (vs knowledge), evidentialism (Conee-Feldman), skepticism varieties
--   beyond cartesian (pyrrhonian, agrippan trilemma, problem of
--   induction, contextualism, relevant alternatives), and norms
--   (norm-of-assertion, closure denial).
-- Loads tables: public.nodes (26 INSERTs), public.edges (38 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 2 -> 3).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * P5-01a's 0011_seed_epistemology_part1 has been applied (28 foundational
--     nodes already present in public.nodes); this migration's edges
--     reference those P5-01a node IDs as sources (within-domain bridges
--     from foundational to specialized) and the new IDs introduced here
--     as both sources and targets. The schema FK on public.edges will
--     reject any reference that does not resolve.
--   * settings.graph_version = 2 at session boot (post-S-0050; verified
--     via Supabase MCP execute_sql at S-0053 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 3 (the
--     post-increment value).
--   * No prior migrations under prefix 0016-0019; this is the first
--     P5-01b epistemology specialized seed file.
-- Postconditions:
--   * 26 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'epistemology'}, status=active, graph_version_added=3.
--   * 38 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=3. All edges are
--     within-domain (source and target both tagged epistemology;
--     P5-01a sources are also tagged epistemology only); cross-domain
--     edges are P5-11's exclusive responsibility per phase_5.md T2-G #1.
--   * settings.graph_version = 3.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 3 AND 'epistemology' = ANY(domain) :: 26
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 3 AND edge_type = 'pedagogical_prerequisite' :: 38
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 3
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that either exist already (the
--     21 cross-references from P5-01a anchors) or that this migration
--     also inserts (the 17 within-cluster edges among the 26 new
--     nodes).
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     21 cross-references all run from P5-01a (foundational) to P5-01b
--     (specialized) — no back-edges. The 17 within-cluster edges are
--     layered (umbrella concepts -> branch theories; sub-cluster
--     analysis -> particular theses): formal_epistemology -> credence
--     -> bayesian_epistemology -> {conditionalization, dutch_book_
--     argument}; virtue_epistemology -> {intellectual_virtue,
--     virtue_reliabilism, virtue_responsibilism}; intellectual_virtue
--     -> virtue_responsibilism; reliabilism -> {generality_problem,
--     virtue_reliabilism}; social_epistemology -> {epistemic_injustice,
--     peer_disagreement, epistemic_dependence, expertise}; expertise
--     -> epistemic_dependence; pyrrhonian_skepticism ->
--     agrippan_trilemma; problem_of_induction -> pyrrhonian_skepticism.
--     validate.py's Kosaraju SCC check confirms post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach into other subdomains — bayesian_
--     epistemology, problem_of_induction, formal_epistemology bridge
--     to philosophy of science (P5-09); credence, conditionalization,
--     dutch_book_argument bridge to logic (P5-03) and decision theory;
--     understanding bridges to philosophy of mind (P5-07a); norm_of_
--     assertion bridges to philosophy of language (P5-08); peer_
--     disagreement bridges to political philosophy (P5-05) on
--     deliberative norms — wait for P5-11's cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional epistemology sub-ranges (0017-
--     0019). Those slots remain reserved for future epistemology
--     extension if Phase 6+ telemetry warrants additional concepts;
--     this seed completes P5-01b's task at the granularity principle
--     within the 0016 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 26/26 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the analytic tradition
--     (or the contemporary philosophical literature in the case of
--     formal-epistemology technical terms) explicitly names. The
--     0% SYNTHETIC mirrors P5-01a's distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'epistemology'. Multiple cross-domain reaches exist (Bayesian
--     epistemology / problem of induction reach into philosophy of
--     science; understanding reaches into philosophy of mind; norm-
--     of-assertion reaches into philosophy of language) but per
--     phase_5.md T2-G #4 (domain-tag cardinality explosions vector),
--     cross-domain tagging belongs to P5-11. The canonical home for
--     each of these concepts in the analytic literature is
--     epistemology, so the single tag is correct.
--   * provenance: 'ai-seed' for every node and edge. Same as P5-01a.
--   * Node selection rationale: the 26 concepts cover the specialized
--     half of epistemology that P5-01a's foundational seed deferred,
--     organized into seven clusters: (1) social epistemology
--     [social_epistemology, epistemic_injustice, peer_disagreement,
--     epistemic_dependence, expertise]; (2) virtue epistemology
--     [virtue_epistemology, intellectual_virtue, virtue_reliabilism,
--     virtue_responsibilism]; (3) formal/Bayesian epistemology
--     [formal_epistemology, credence, bayesian_epistemology,
--     conditionalization, dutch_book_argument]; (4) reliabilism
--     [reliabilism, generality_problem]; (5) knowledge-first /
--     understanding / evidentialism [knowledge_first_epistemology,
--     understanding, evidentialism]; (6) skepticism varieties beyond
--     cartesian [pyrrhonian_skepticism, agrippan_trilemma,
--     problem_of_induction, contextualism_epistemic,
--     relevant_alternatives_theory]; (7) norms [norm_of_assertion,
--     closure_denial]. Each cluster is anchored by an umbrella concept
--     (where applicable) plus the most pedagogically load-bearing
--     downstream theses; deeper sub-disciplinary detail (e.g.,
--     specific imprecise-credence frameworks, specific virtue
--     taxonomies, specific contextualist semantic theories) is
--     deferred — those are research-frontier specialties beyond the
--     undergraduate-mastery granularity that Paideia's pedagogical
--     graph is sized to.
--   * Edge structure: 38 edges total — 21 cross-references from
--     P5-01a anchors into specialized concepts, 17 within-cluster
--     edges among the 26 new specialized concepts. All 38 are
--     pedagogical_prerequisite. The split is heavier on cross-
--     references because the specialized cluster is fundamentally
--     extension-of-foundational; the foundational P5-01a seed is the
--     natural prerequisite layer for nearly every specialized concept
--     here.
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 3; DELETE FROM public.nodes WHERE id IN (the 26 ids inserted
--   here); UPDATE public.settings SET value = '2'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 65 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; this migration's
--   prerequisite layer); product/docs/architecture.md (Node/Edge
--   schema + Granularity Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 2 at session boot (post-S-0050 state); write 3 here;
-- every node/edge below carries graph_version_added = 3.
UPDATE public.settings
  SET value = '3'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 26 INSERTs covering the specialized half of epistemology.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'social_epistemology',
    'Social Epistemology',
    ARRAY['epistemology'],
    'The epistemology of belief formation in social contexts: testimony, peer disagreement, group belief, expertise, and the epistemic significance of social structure. Treats knowers as embedded in epistemic communities rather than as isolated Cartesian inquirers, and asks how social practices and institutions shape what we can know.',
    'Frame social epistemology as an extension rather than a rival of individualist epistemology. The individualist machinery (justification, evidence, reliability) still applies; social epistemology adds questions the individualist framework leaves untouched (when does aggregating opinions track truth? does an asymmetry in social power create epistemic asymmetries?). Goldman''s ''Knowledge in a Social World'' (1999) is the foundational systematic treatment.',
    ARRAY['social_epistemics'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'epistemic_injustice',
    'Epistemic Injustice',
    ARRAY['epistemology'],
    'The wrong done to a person specifically as a knower: testimonial injustice (unfairly low credibility assigned because of identity-prejudice) and hermeneutical injustice (the structural absence of conceptual resources to make sense of one''s own experience). Introduced as a category by Miranda Fricker (2007).',
    'Fricker''s book is short and pedagogically clean; teach it through the two paradigm cases (a witness disbelieved on the basis of race, a victim of harassment lacking the concept of sexual harassment) before generalizing. The category sits at the intersection of epistemology and social/political philosophy; its placement here reflects the analytic tradition''s reception of it as a contribution to social epistemology.',
    ARRAY['testimonial_injustice', 'hermeneutical_injustice'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'peer_disagreement',
    'Peer Disagreement',
    ARRAY['epistemology'],
    'The problem of how to revise one''s beliefs upon discovering that an epistemic peer (someone equally well-informed and equally rational) disagrees. Two main camps: equal-weight views (split the difference; Christensen, Elga, Feldman) and steadfast views (you may rationally retain your prior credence under certain conditions; Kelly, van Inwagen).',
    'Set up the problem with a concrete vignette (you and a colleague calculate a restaurant tip and get different answers; you both have the same competence in arithmetic). The intuitions about whether you should split the difference, fully defer, or retain your view track the contrast between equal-weight and steadfast camps. The dispute matters for political and religious disagreement well beyond the toy case.',
    ARRAY['epistemology_of_disagreement'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'epistemic_dependence',
    'Epistemic Dependence',
    ARRAY['epistemology'],
    'The condition in which a believer''s justified belief depends on others'' epistemic states — the testifier''s reliability, the expert''s competence, the community''s collective practice. John Hardwig''s 1985 articulation foregrounded the asymmetry: a layperson''s justification for trusting an expert cannot itself rest on first-hand evidence about the matter at hand.',
    'Epistemic dependence is the inevitable upshot of the division of cognitive labor in modern societies; almost no one has first-hand evidence for almost anything they justifiably believe. Use this to introduce the puzzle that anti-reductionist accounts of testimony are responding to (Reid, Coady) — independent verification is unavailable, so the structure of trust must do the work justification cannot do directly.',
    ARRAY['cognitive_dependence'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'expertise',
    'Expertise',
    ARRAY['epistemology'],
    'The epistemic standing of being an expert: possessing reliable, articulable, and recognizable competence in a domain that warrants others'' deference on questions within that domain. The epistemological questions are who counts as an expert, how laypersons identify experts, and when expert testimony confers justification on the hearer.',
    'Goldman''s ''Experts: Which Ones Should You Trust?'' (2001) sets out five sources of evidence laypersons use to evaluate experts (track record, peer reviews, etc.) — useful to teach as a checklist that students can apply to current public-controversy cases. The novice/expert problem is at the heart of social-epistemology applications to medicine, climate, and policy.',
    ARRAY['epistemic_expertise'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'virtue_epistemology',
    'Virtue Epistemology',
    ARRAY['epistemology'],
    'The approach to epistemology that takes intellectual virtues — reliable cognitive faculties or character traits productive of true belief — as the primary unit of analysis. Two main camps: virtue reliabilism (intellectual virtues are reliable cognitive capacities; Sosa, Greco) and virtue responsibilism (intellectual virtues are character traits; Zagzebski, Code).',
    'Virtue epistemology arose as a reorientation: instead of starting with belief and asking what makes a belief justified, start with the believer and ask what makes a knower a good knower. Useful as a foil to belief-centered analyses (JTB, reliabilism). Sosa''s ''A Virtue Epistemology'' (2007) is the contemporary canon for the reliabilist branch; Zagzebski''s ''Virtues of the Mind'' (1996) for the responsibilist branch.',
    ARRAY['virtue_theoretic_epistemology'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'intellectual_virtue',
    'Intellectual Virtue',
    ARRAY['epistemology'],
    'A reliable cognitive disposition (faculty-virtue) or a character trait directed at epistemic goods (character-virtue). Examples include open-mindedness, intellectual humility, conscientiousness, intellectual courage, and adequately calibrated confidence. Virtue epistemology takes intellectual virtues as primary in the analysis of knowledge and justification.',
    'Distinguish intellectual from moral virtues: an intellectually virtuous agent need not be morally virtuous (a careful but cruel investigator) and vice versa. The faculty/character distinction is internal to virtue epistemology — the reliabilist branch treats intellectual virtues as reliable cognitive capacities (vision, memory, inferential competence), the responsibilist branch as character traits cultivated by intellectual practice.',
    ARRAY['epistemic_virtue', 'cognitive_virtue'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'virtue_reliabilism',
    'Virtue Reliabilism',
    ARRAY['epistemology'],
    'Ernest Sosa''s version of virtue epistemology: knowledge is true belief reliably produced by an intellectual virtue (a stable cognitive competence). Distinguishes animal knowledge (apt belief — a true belief whose truth manifests competence) from reflective knowledge (apt belief that is also defensibly held — apt apt belief).',
    'Sosa''s AAA structure (Accuracy, Adroitness, Aptness) is the load-bearing teaching anchor: a belief is accurate if true, adroit if competently formed, apt if accurate because adroit. Aptness is the key innovation — it answers Gettier cases by requiring the truth of the belief to manifest competence rather than merely coincide with it. Sits midway between traditional reliabilism and responsibilist virtue epistemology.',
    ARRAY['sosa_virtue_epistemology'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'virtue_responsibilism',
    'Virtue Responsibilism',
    ARRAY['epistemology'],
    'The branch of virtue epistemology that takes intellectual virtues as character traits the believer cultivates — open-mindedness, intellectual conscientiousness, courage, humility — and grounds knowledge or justification in the agent''s exercise of those traits. Linda Zagzebski''s ''Virtues of the Mind'' is the canonical statement.',
    'Where virtue reliabilism analyzes intellectual virtues as truth-conducive faculties, responsibilism analyzes them as cultivated character. The distinction matters: a reliable but uncultivated faculty (perceiving color) counts as virtuous on Sosa''s account but not on Zagzebski''s. Responsibilism draws on Aristotelian moral psychology and connects naturally to philosophy of education.',
    ARRAY['responsibilist_virtue_epistemology'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'formal_epistemology',
    'Formal Epistemology',
    ARRAY['epistemology'],
    'The application of formal tools (probability theory, logic, decision theory, computability theory) to epistemological problems. Encompasses Bayesian epistemology, formal learning theory, judgment aggregation, and the epistemology of probabilistic reasoning. Studies belief, evidence, and inference under quantitative discipline.',
    'Formal epistemology is methodologically continuous with classical epistemology but substitutes precise models for informal arguments. Useful for showing how rigorous treatment exposes hidden assumptions in classical positions (Bayesian conditionalization formalizes Hume''s problem of induction; the lottery and preface paradoxes formalize tensions between certainty and partial belief). Hájek and Hendricks''s ''Probabilistic Methods in Cognitive Science'' is a standard introduction.',
    ARRAY['mathematical_epistemology'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'credence',
    'Credence',
    ARRAY['epistemology'],
    'A degree of belief — a quantitative attitude representing the strength with which a believer holds a proposition true, typically modeled as a real number in [0, 1]. Bayesian epistemology takes credences (rather than full beliefs) as the basic doxastic attitudes; the relationship between credence and full belief (the Lockean thesis, threshold accounts) is itself a topic of inquiry.',
    'Introduce credence by contrasting binary belief (you believe p or you don''t) with graded belief (you''re 70% confident in p). Empirical work (probabilistic reasoning, calibration studies) supports treating credence as cognitively real. The hard question is how credences relate to full beliefs — the Lockean thesis (full belief = credence above some threshold) is intuitive but generates the lottery and preface paradoxes.',
    ARRAY['degree_of_belief', 'partial_belief'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'bayesian_epistemology',
    'Bayesian Epistemology',
    ARRAY['epistemology'],
    'The framework that models rational belief as conformity to the probability calculus (probabilism) and rational belief revision as conditionalization on new evidence. Provides a quantitative, normatively rigorous account of evidence, confirmation, and inductive reasoning. Dominant in formal epistemology and influential across philosophy of science.',
    'Frame Bayesian epistemology around three theses: (1) probabilism — credences obey the probability axioms; (2) conditionalization — update by Bayes''s rule on new evidence; (3) decision theory — rational action maximizes expected utility relative to current credences. The Dutch book argument provides one motivation for probabilism; Lewis''s diachronic Dutch book motivates conditionalization. Earman''s ''Bayes or Bust?'' is a classic critical introduction.',
    ARRAY['bayesianism', 'probabilist_epistemology'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'conditionalization',
    'Conditionalization',
    ARRAY['epistemology'],
    'The Bayesian rule for belief revision: upon learning evidence E with certainty, set new credence in any hypothesis H equal to the old conditional credence Pr_old(H | E). The operation transforms one coherent credence function into another and is the canonical Bayesian update rule. Refinements include Jeffrey conditionalization (uncertain evidence) and imaging (counterfactual update).',
    'Teach conditionalization with a worked example before stating the rule formally — a witness updates credence in a defendant''s guilt upon hearing testimony. Note the strict-evidence assumption: standard conditionalization requires Pr_new(E) = 1, which is rarely literally true; Jeffrey conditionalization weakens this. The rule has both a synchronic justification (Dutch book) and diachronic ones (van Fraassen, Lewis).',
    ARRAY['bayesian_update', 'bayes_rule_update'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'dutch_book_argument',
    'Dutch Book Argument',
    ARRAY['epistemology'],
    'A pragmatic argument that an agent whose credences violate the probability axioms is exploitable: there exists a set of bets each of which she rationally accepts but which together guarantee her a loss. Used to motivate probabilism (synchronic Dutch book) and conditionalization (diachronic Dutch book, due to Lewis and Teller).',
    'The Dutch book setup is unusually concrete for a philosophical argument; teach it by walking through a worked case with two violating credences and showing the bookmaker''s sure-loss combination. The argument is pragmatic, not directly epistemic, which is itself a subject of dispute — does inability-to-be-Dutch-booked really show that probabilistic credences are *epistemically* required? Joyce''s accuracy-dominance argument is the contemporary alternative.',
    ARRAY['dutch_book', 'sure_loss_argument'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'reliabilism',
    'Reliabilism',
    ARRAY['epistemology'],
    'The theory of justification (Goldman 1979) on which a belief is justified iff it is produced by a reliable cognitive process — one that produces a high ratio of true beliefs to false beliefs. The canonical externalist account; treats justification as an external, world-involving property rather than an internally accessible one.',
    'Reliabilism is best taught against the backdrop of internalism: a brain-in-a-vat with internally indistinguishable mental states from your own would have justified beliefs on internalist accounts but not on reliabilism (its processes are unreliable). The new evil demon problem is the canonical objection; the generality problem is the structural one. Goldman''s ''What Is Justified Belief?'' is the foundational paper.',
    ARRAY['process_reliabilism'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'generality_problem',
    'Generality Problem',
    ARRAY['epistemology'],
    'The objection (Conee and Feldman 1998) that reliabilism cannot non-arbitrarily specify which process produced a given belief. Any belief is the output of indefinitely many processes at different levels of generality (vision-in-good-light, vision-in-good-light-on-Tuesday, vision-by-this-particular-perceiver), and the reliability of these processes can differ wildly.',
    'The generality problem is reliabilism''s structural Achilles'' heel — there is no principled way to specify the relevant process type without circularly invoking justification or making the specification gerrymandered. Various responses (statistical, dispositional, etiological) exist but no consensus solution. Useful for teaching how a precise objection can pin down a sophisticated theory.',
    ARRAY['process_individuation_problem'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'knowledge_first_epistemology',
    'Knowledge-First Epistemology',
    ARRAY['epistemology'],
    'Timothy Williamson''s (2000) approach: treat knowledge as conceptually primitive and explain belief, evidence, and justification in terms of knowledge rather than the reverse. Knowledge is the most general factive mental state; evidence is what one knows; justified belief is belief that is appropriately related to one''s knowledge.',
    'Knowledge-first epistemology inverts the analysis-of-knowledge tradition: instead of analyzing knowledge in terms of belief, truth, and justification, take knowledge as the unanalyzed primitive and define the others derivatively. Williamson''s ''Knowledge and Its Limits'' is the foundational text. Useful as the contemporary alternative to JTB-and-its-amendments; raises the question of whether the analytic project itself was misconceived.',
    ARRAY['williamson_knowledge_first', 'knowledge_as_primitive'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'understanding',
    'Understanding',
    ARRAY['epistemology'],
    'The cognitive achievement of grasping how the components of a body of information fit together — the structure of explanation, the relations of dependence, the connections among parts. Distinct from mere knowledge of a list of facts; valuable independently and arguably the more central goal of inquiry. Pritchard, Kvanvig, and Zagzebski have argued for understanding-first or understanding-equally-central views.',
    'Distinguish three senses: understanding-that (as in ''she understands that p''), understanding-why (grasping why p is true), and objectual understanding (grasping a subject matter as a coherent whole). Pedagogically the third is the most distinctive: a student who has memorized historical dates differs from one who understands the period. The theoretical question is whether understanding reduces to knowledge or stands as a separate category.',
    ARRAY['epistemic_understanding', 'objectual_understanding'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'evidentialism',
    'Evidentialism',
    ARRAY['epistemology'],
    'The thesis (Conee and Feldman 1985) that justification is fully determined by the believer''s evidence: a belief is justified iff it fits the believer''s evidence at the time. Allows that justification is internally accessible (mentalism) without requiring that the evidence be of any particular cognitive kind.',
    'Evidentialism is the canonical contemporary internalist position; teach it as an alternative to reliabilism in the externalism-internalism dispute. The slogan ''justification supervenes on the mental'' is a useful pedagogical anchor. The hard questions are what counts as evidence (perceptual experience, memory, prior beliefs?) and what fitting means (evidential relations are themselves contested).',
    ARRAY['conee_feldman_evidentialism'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'pyrrhonian_skepticism',
    'Pyrrhonian Skepticism',
    ARRAY['epistemology'],
    'The ancient skeptical tradition (Pyrrho, Sextus Empiricus) on which suspending judgment (epoché) is the appropriate response to the equipollence of contrary arguments, and tranquility (ataraxia) is the practical upshot. Distinct from Cartesian skepticism: Pyrrhonism is a way of life rather than a methodological tool, and it suspends rather than denies.',
    'Pyrrhonism is best taught through Sextus''s modes — the ten tropes of Aenesidemus and the five tropes of Agrippa — that systematically generate equipollent arguments for and against any thesis. The Agrippan trilemma in particular (regress, circularity, or arbitrary stopping) crystallizes the structural problem any justification must face. Distinguish from academic skepticism (the dogmatic claim that nothing can be known).',
    ARRAY['pyrrhonism', 'skeptical_tradition_pyrrhonian'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'agrippan_trilemma',
    'Agrippan Trilemma',
    ARRAY['epistemology'],
    'The skeptical argument that any attempt to justify a belief faces three exhaustive and unappealing options: an infinite regress, a circular justification, or an arbitrary stopping point. Named for the ancient Pyrrhonist Agrippa; encoded by Sextus Empiricus as three of the five Agrippan modes. Structurally the argument behind the foundationalism / coherentism / infinitism trilemma.',
    'The Agrippan trilemma is the structural challenge every theory of justification responds to: foundationalism accepts arbitrary (basic) stopping points; coherentism accepts circularity (re-described as mutual support); infinitism accepts the infinite regress. Teach it as the puzzle that motivates the structural debate, then return to the three theories from P5-01a as named responses to the trilemma.',
    ARRAY['agrippa_modes', 'regress_problem'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'problem_of_induction',
    'Problem of Induction',
    ARRAY['epistemology'],
    'David Hume''s (1739) skeptical argument that no inference from observed regularities to unobserved cases can be justified non-circularly: inductive inference presupposes the uniformity of nature, and any argument for the uniformity of nature must itself be either deductive (and thus question-begging) or inductive (and thus circular). The canonical challenge to empirical knowledge of unobserved cases.',
    'Distinguish Hume''s problem (no rational warrant for induction) from Goodman''s ''new riddle of induction'' (which inductive predicates are projectible — green vs grue). Hume''s problem motivates Bayesian and reliabilist responses (Bayesian: rational credence in uniformity is presupposed by the structure of degrees of belief; reliabilist: induction is reliable, even if non-circularly unjustifiable). Reichenbach''s pragmatic vindication and Strawson''s ordinary-language dissolution are also pedagogically useful.',
    ARRAY['humes_problem_of_induction', 'inductive_skepticism'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'contextualism_epistemic',
    'Epistemic Contextualism',
    ARRAY['epistemology'],
    'The semantic thesis (Cohen, DeRose, Lewis) that ''knows'' is context-sensitive: what counts as knowledge depends on conversational context — the standards in play, the salient alternatives, what is at stake. Contextualism preserves both ordinary knowledge claims (low standards) and the apparent force of skeptical scenarios (high standards) without contradiction.',
    'Contextualism is best taught through bank cases (DeRose''s contrast: the same speaker truly says ''I know the bank is open Saturday'' in low-stakes context and truly says ''I don''t know'' in high-stakes context). The semantic move (relativizing ''know'' to context) is what does the work. Critics object that contextualism mislocates the variation (subject-sensitive invariantism / Stanley) or that it gets the linguistic data wrong.',
    ARRAY['epistemological_contextualism', 'attributer_contextualism'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'relevant_alternatives_theory',
    'Relevant Alternatives Theory',
    ARRAY['epistemology'],
    'Fred Dretske''s (1970) thesis that knowing p requires ruling out only the relevant alternatives to p, not all logically possible alternatives. Skeptical scenarios (brain-in-a-vat) are typically not relevant alternatives in ordinary contexts, so failure to rule them out does not undermine ordinary knowledge claims. A non-contextualist anti-skeptical strategy with a closure-denying upshot.',
    'Distinguish from contextualism: relevant alternatives theory is a theory about knowledge itself (an alternative is or isn''t relevant relative to a knowledge ascription, in some objective or epistemically-fixed way), not about the semantics of ''knows''. The closure-denying consequence (you can know you have hands while not knowing you''re not a brain-in-a-vat) is shared with Nozick''s tracking theory; Dretske and Nozick converge on closure denial from different starting points.',
    ARRAY['dretske_relevant_alternatives'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'norm_of_assertion',
    'Norm of Assertion',
    ARRAY['epistemology'],
    'The constitutive rule that governs assertion: candidates include the knowledge norm (one may assert p only if one knows p; Williamson, DeRose), the truth norm (only if p is true), the justified-belief norm (only if one justifiedly believes p), and the certainty norm. The rule connects epistemology to the philosophy of language: an account of knowledge has implications for how we may speak.',
    'Williamson''s argument for the knowledge norm runs through Moorean paradoxes (''p, but I don''t know that p'' is uniformly defective) and lottery propositions (''ticket #7 will lose'' is defective even with overwhelming probability — defective in a way that the belief itself is not). The dispute matters: differing norms predict different patterns of conversational repair, criticism, and challenge.',
    ARRAY['knowledge_norm_of_assertion', 'assertion_norm'],
    'INTERPRETED',
    'ai-seed',
    3
  ),
  (
    'closure_denial',
    'Closure Denial',
    ARRAY['epistemology'],
    'The position that epistemic closure under known entailment fails: one can know p without knowing all the consequences one knows to follow from p. Defended by Dretske (1970) via relevant alternatives and Nozick (1981) via the sensitivity condition; both motivated by the desire to preserve ordinary knowledge while accepting the skeptic''s closure inference at face value.',
    'Closure denial is the price both Dretske and Nozick pay for their anti-skeptical strategies, and the price most other epistemologists are unwilling to pay (closure under known entailment is intuitively plausible and serves logical reasoning). The dispute illustrates how anti-skeptical and pro-closure intuitions can pull a theory apart; the contextualist response is one attempt to keep both.',
    ARRAY['epistemic_closure_denial'],
    'INTERPRETED',
    'ai-seed',
    3
  );

-- Edges: 38 INSERTs, all pedagogical_prerequisite. Cross-references
-- run from P5-01a foundational anchors to P5-01b specialized concepts
-- (within-domain bridges); within-cluster edges run among the 26 new
-- nodes only. No cross-domain edges (P5-11's exclusive surface).
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Cross-references from P5-01a anchors (foundational) into P5-01b (specialized)
  -- Social epistemology branch
  ('testimonial_knowledge', 'social_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('knowledge', 'social_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Virtue epistemology branch (responds to JTB / justification machinery)
  ('knowledge', 'virtue_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('epistemic_justification', 'virtue_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Reliabilism (extends externalism the access thesis into a theory of justification)
  ('epistemic_justification', 'reliabilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('externalism_epistemic', 'reliabilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Evidentialism (the internalist counterpart)
  ('epistemic_justification', 'evidentialism', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('internalism_epistemic', 'evidentialism', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Formal/Bayesian branch
  ('belief', 'credence', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('evidence', 'bayesian_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Knowledge-first contrast with the analytic tradition
  ('knowledge', 'knowledge_first_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('justified_true_belief', 'knowledge_first_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Understanding contrasts with propositional knowledge
  ('propositional_knowledge', 'understanding', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Skepticism varieties extend the cartesian baseline
  ('skepticism_epistemic', 'pyrrhonian_skepticism', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('skepticism_epistemic', 'agrippan_trilemma', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('evidence', 'problem_of_induction', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Anti-skeptical responses
  ('skepticism_epistemic', 'contextualism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('skepticism_epistemic', 'relevant_alternatives_theory', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Closure responses
  ('epistemic_closure', 'closure_denial', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('epistemic_closure', 'contextualism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Norm of assertion connects propositional knowledge to assertion
  ('propositional_knowledge', 'norm_of_assertion', 'pedagogical_prerequisite', 'ai-seed', 3),

  -- Within-cluster edges among the 26 new nodes
  -- Social epistemology cluster
  ('social_epistemology', 'epistemic_injustice', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('social_epistemology', 'peer_disagreement', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('social_epistemology', 'epistemic_dependence', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('social_epistemology', 'expertise', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('expertise', 'epistemic_dependence', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Virtue epistemology cluster
  ('virtue_epistemology', 'intellectual_virtue', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('virtue_epistemology', 'virtue_reliabilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('virtue_epistemology', 'virtue_responsibilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('intellectual_virtue', 'virtue_responsibilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Formal/Bayesian cluster
  ('formal_epistemology', 'credence', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('credence', 'bayesian_epistemology', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('bayesian_epistemology', 'conditionalization', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('bayesian_epistemology', 'dutch_book_argument', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Reliabilism connects to virtue reliabilism through Sosa's lineage
  ('reliabilism', 'generality_problem', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('reliabilism', 'virtue_reliabilism', 'pedagogical_prerequisite', 'ai-seed', 3),
  -- Skepticism cluster: Pyrrhonism subsumes the trilemma; induction motivates Pyrrhonism
  ('pyrrhonian_skepticism', 'agrippan_trilemma', 'pedagogical_prerequisite', 'ai-seed', 3),
  ('problem_of_induction', 'pyrrhonian_skepticism', 'pedagogical_prerequisite', 'ai-seed', 3);

COMMIT;
