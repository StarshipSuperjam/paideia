-- Migration: 0011_seed_epistemology_part1
-- Purpose: First Phase 5 seed migration — foundational epistemology
--   concepts and within-domain pedagogical_prerequisite edges. Authored
--   in S-0050 against task P5-01a "Epistemology core seed" of target
--   T-PHASE-5 per engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers the core/foundational half of epistemology (knowledge,
--   justification, belief, certainty, the analysis-of-knowledge
--   tradition). The specialized half (social, virtue, formal, broader
--   skepticism varieties) is task P5-01b's range (0016-0019).
-- Loads tables: public.nodes (28 INSERTs), public.edges (34 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 1 -> 2).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 1 at session boot (read from live DB
--     immediately before this migration was authored). The increment
--     contract per product/seed-graph/migrations/ROUTING.md is honored:
--     all node/edge INSERTs in this migration carry graph_version_added
--     = 2 (the post-increment value).
--   * No prior migrations under prefix 0011-0019; this is the first
--     epistemology seed file.
-- Postconditions:
--   * 28 nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'epistemology'}, status=active, graph_version_added=2.
--   * 34 edges exist in public.edges with edge_type=pedagogical_prerequisite,
--     graph_version_added=2. All edges are within-domain (source and
--     target both tagged epistemology); cross-domain edges are P5-11's
--     exclusive responsibility per phase_5.md T2-G #1.
--   * settings.graph_version = 2.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 2 AND 'epistemology' = ANY(domain) :: 28
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 2 AND edge_type = 'pedagogical_prerequisite' :: 34
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 2
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts (or that already exist — no pre-existing nodes are
--     referenced by this seed since Phase 5 starts greenfield).
--   * No edge cycles in the pedagogical_prerequisite subgraph (verified
--     by structural review at authoring time; validate.py's Kosaraju
--     SCC check confirms post-apply).
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Cross-domain bridges (e.g.,
--     epistemology -> philosophy of science, epistemology -> philosophy
--     of mind) are P5-11's exclusive surface per phase_5.md T2-G #1
--     (cross-domain edge collisions vector).
--   * Does not author the specialized epistemology range (0016-0019):
--     social epistemology, virtue epistemology, formal epistemology,
--     skepticism varieties beyond cartesian_skepticism. P5-01b owns
--     that range.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md). The cross_domain_dependency reserved
--     predicate decision is deferred to P5-11 per phase_5.md T1-E.
--   * Does not seed any historical_influence edges. Historical-influence
--     metadata is Discovery-surface annotation per architecture.md
--     "Edge Schema"; P5+ may add historical edges in a later sweep.
-- Cross-cutting decisions:
--   * confidence_level distribution: 28/28 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-established in the SEP/IEP
--     entry inventory and corresponds to a concept the analytic
--     tradition explicitly names (no inferred-structure-SEP-doesn't-
--     itself-name authoring needed for the foundational layer).
--   * domain[] cardinality: every node carries exactly one tag,
--     'epistemology'. Cross-domain tags (e.g., philosophy of science,
--     philosophy of mind) are NOT applied here even where a concept
--     has cross-domain reach (e.g., evidence is also relevant to
--     philosophy of science) because the canonical home for these
--     concepts is epistemology and cross-domain tagging belongs to
--     P5-11's cross-bridge authoring per phase_5.md T2-G #4 (domain-
--     tag cardinality explosions vector).
--   * provenance: 'ai-seed' for every node and edge. Distinguishes
--     AI-authored seed content from purely human-authored entries; not
--     constrained at the schema layer (the column carries no CHECK).
--   * Node selection rationale: the 28 concepts cover the analysis-of-
--     knowledge tradition end-to-end at the granularity principle
--     (architecture.md "Node Granularity Principle"). Roots are
--     belief, truth, evidence (no inbound from this seed). The
--     analysis-of-knowledge spine runs belief + truth +
--     epistemic_justification -> propositional_knowledge ->
--     justified_true_belief -> gettier_problem and four standard
--     responses (no_false_lemmas, causal, defeasibility, tracking).
--     Theories of justification (foundationalism / coherentism /
--     infinitism, internalism / externalism) attach to
--     epistemic_justification. Knowledge-as-genus emerges from the
--     propositional / knowledge-how distinction.
--   * Edge structure: all 34 edges are pedagogical_prerequisite. No
--     cycles by construction (the spine is layered: roots -> mid-
--     foundation -> JTB -> Gettier -> responses; theories of
--     justification branch off epistemic_justification; knowledge-
--     dependent concepts branch off knowledge / propositional_
--     knowledge). validate.py's SCC check confirms post-apply.
--   * Roots have no inbound from this seed and intentionally so. The
--     orphan_leaf soft-warn may fire on belief / truth / evidence as
--     the audit's leaf-direction check; this is expected for a
--     foundational seed and resolves when service nodes (P5-10) and
--     cross-bridges (P5-11) attach inbound prerequisites from logic,
--     mathematics, and adjacent subdomains.
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 2 AND source_id IN (the 28 ids inserted here) AND target_id IN
--   (same); DELETE FROM public.nodes WHERE id IN (the 28 ids); UPDATE
--   public.settings SET value = '1'::jsonb WHERE key = 'graph_version';
--   COMMIT. The whole-migration BEGIN/COMMIT wrap below means a single
--   transaction failure rolls all 63 statements atomically — manual
--   rollback below applies to the post-commit window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/docs/architecture.md (Node/Edge schema +
--   Granularity Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 1 at session boot; write 2 here; every node/edge
-- below carries graph_version_added = 2.
UPDATE public.settings
  SET value = '2'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 28 INSERTs covering the analysis-of-knowledge tradition core.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'belief',
    'Belief',
    ARRAY['epistemology'],
    'A doxastic attitude toward a proposition: the believer takes the proposition to be true. The most basic propositional attitude in epistemology and the entry point for any analysis of knowledge.',
    'Treat belief as the unit you analyze before composing it into knowledge. The contrast class is non-doxastic attitudes (hoping, fearing, imagining) which involve a proposition without endorsement. Degree-of-belief (credence) is a refinement worth flagging but not unfolding here.',
    ARRAY['doxastic_attitude'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'truth',
    'Truth',
    ARRAY['epistemology'],
    'The property a proposition has when things are as the proposition says they are. Theories of truth (correspondence, coherence, deflationary, pragmatist) compete to characterize this property; the bare concept is presupposed by every account.',
    'Distinguish the concept of truth from theories of truth. Students often arrive with a folk-correspondence intuition that survives intact; the philosophical work is making that intuition precise enough to argue with. Truth is presupposed in the JTB analysis even when no theory of truth is endorsed.',
    ARRAY['being_the_case'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'truth_correspondence',
    'Correspondence Theory of Truth',
    ARRAY['epistemology'],
    'The theory that a proposition is true when it corresponds to a fact about the world. The standard realist account, traceable to Aristotle (saying of what is that it is) and developed in 20th-century analytic philosophy via Russell, Tarski, and others.',
    'Useful as the default theory of truth to teach against. Critics target the correspondence relation itself (what is a fact? how does a sentence correspond?) and propose deflationary or coherence alternatives. For epistemology purposes the correspondence intuition is the unmarked baseline.',
    ARRAY['correspondence_truth'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'evidence',
    'Evidence',
    ARRAY['epistemology'],
    'What a believer has access to that bears on whether a proposition is true. Perceptual experience, testimony, memory, and inference from prior beliefs all serve as evidence. The relation between evidence and the belief it supports is the central problem of epistemic justification.',
    'Evidence is the input variable in justification theories: internalism asks whether the believer has access to her evidence; externalism asks whether the evidence reliably tracks truth. Evidentialism (Conee and Feldman) makes evidence-fit constitutive of justification.',
    ARRAY['epistemic_evidence'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'epistemic_justification',
    'Epistemic Justification',
    ARRAY['epistemology'],
    'The property a belief has when the believer has adequate epistemic grounds for holding it. The third clause of the standard JTB analysis of knowledge and the surface where theories of justification (internalism vs externalism, foundationalism vs coherentism vs infinitism) compete.',
    'Justification is normative: a belief is justified or not relative to the believer''s epistemic obligations. Distinguish from mere reliability (a belief can be reliably formed without the believer being justified, on internalist accounts) and from truth (a justified belief can still be false — fallibilism).',
    ARRAY['justification'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'propositional_knowledge',
    'Propositional Knowledge',
    ARRAY['epistemology'],
    'Knowledge that some proposition is true — knowing-that. The primary target of the analysis-of-knowledge tradition, standardly analyzed as justified true belief plus a Gettier-resistant condition. Contrasts with knowledge-how (knowing how to do something).',
    'Most epistemology focuses on propositional knowledge because the analysis is tractable: belief, truth, justification are independently studied components. The propositional / procedural distinction is contested (Stanley and Williamson defend reduction of knowledge-how to propositional knowledge) but pedagogically useful.',
    ARRAY['knowing_that'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'knowledge_how',
    'Knowledge-How',
    ARRAY['epistemology'],
    'The kind of knowledge involved in being able to do something — knowing how to ride a bicycle, speak a language, prove a theorem. Distinguished from propositional knowledge by Gilbert Ryle (1949) and revisited by Stanley and Williamson (2001) who argue it reduces to propositional knowledge of a way to perform the action.',
    'The intuitive distinction is robust (a swimmer who knows how to swim need not know any propositions about swimming) but the philosophical question is whether knowledge-how is a distinct cognitive kind or a special case of propositional knowledge. Useful as a foil for showing what propositional knowledge isn''t.',
    ARRAY['knowing_how', 'procedural_knowledge'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'knowledge',
    'Knowledge',
    ARRAY['epistemology'],
    'The general epistemic standing a believer has when she knows something — encompassing both propositional knowledge (knowing-that) and procedural knowledge (knowing-how). The genus of which the analyzed kinds are species.',
    'In introductory presentations knowledge is sometimes taught first as an undifferentiated intuition, then split into propositional and procedural. Pedagogically the species precede the genus: students grasp knowing-that and knowing-how as concrete cases before abstracting to knowledge-as-such.',
    ARRAY['knowing'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'justified_true_belief',
    'Justified True Belief',
    ARRAY['epistemology'],
    'The classical analysis of propositional knowledge: S knows that p iff (1) p is true, (2) S believes that p, and (3) S is justified in believing that p. Traceable to Plato''s Theaetetus, codified by 20th-century epistemologists, and decisively challenged by Gettier (1963).',
    'JTB is the central reference point for the analysis-of-knowledge tradition. Understand its three clauses as independently motivated (each rules out a class of non-knowledge cases) before encountering Gettier counterexamples. Most post-Gettier accounts retain JTB and add a fourth condition.',
    ARRAY['jtb', 'standard_analysis_of_knowledge'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'gettier_problem',
    'Gettier Problem',
    ARRAY['epistemology'],
    'The problem of accommodating cases — introduced by Edmund Gettier (1963) — where a believer has a justified true belief that intuitively does not count as knowledge. Standard cases involve the believer making a sound inference from a false premise to a true conclusion, or believing a true proposition for the wrong reason.',
    'Gettier cases are short and surprising; teach them by walking through the original two-page paper''s constructions (the man with ten coins; Brown in Barcelona). The lesson is structural: justification, truth, and belief can all hold without knowledge, so the standard analysis is incomplete or wrong.',
    ARRAY['gettier_cases', 'gettier_counterexamples'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'no_false_lemmas_response',
    'No-False-Lemmas Response',
    ARRAY['epistemology'],
    'A Gettier response (Clark 1963; Harman 1973) adding a fourth condition to JTB: the believer''s justification must not essentially rest on any false belief. Blocks Gettier cases that turn on a sound inference from a false premise.',
    'The natural first response: Gettier cases all seem to involve a false intermediate belief (the man''s belief that Smith has a Ford), so require justifications free of such defects. The trouble is fakeness cases (Goldman''s barn facade county) where no false lemma is involved yet knowledge is absent.',
    ARRAY['no_false_lemmas'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'causal_theory_of_knowing',
    'Causal Theory of Knowing',
    ARRAY['epistemology'],
    'Alvin Goldman''s (1967) Gettier response: S knows that p iff S''s belief that p is appropriately caused by the fact that p. Replaces the justification clause with a causal condition linking the truth-maker of p to S''s belief.',
    'Useful as a paradigm externalist response: it eliminates the internalist requirement that the believer have access to the justifying ground. Difficulties include cases where the causal chain is deviant and cases of mathematical knowledge (where there is no obvious causal interaction with the abstract truth-maker).',
    ARRAY['goldman_causal_theory'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'defeasibility_analysis',
    'Defeasibility Analysis',
    ARRAY['epistemology'],
    'A Gettier response (Lehrer and Paxson 1969; Klein 1971) adding that knowledge requires justification that cannot be defeated by any true proposition the believer does not yet have. Aims to capture the idea that Gettier cases involve hidden defeaters.',
    'Defeasibility theories are technically demanding (specifying which true propositions count as legitimate defeaters versus misleading defeaters is the hard problem) but pedagogically clarifying — they articulate the intuition that Gettier-knowledge is fragile against further evidence.',
    ARRAY['defeasibility_theory'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'tracking_theory_of_knowledge',
    'Tracking Theory of Knowledge',
    ARRAY['epistemology'],
    'Robert Nozick''s (1981) Gettier response: S knows that p iff S''s belief that p tracks the truth of p, in the sense that S would not believe p if p were false (sensitivity) and S would believe p if p were true (adherence). Frames knowledge in counterfactual terms.',
    'Tracking theories shift the analysis from justification to a modal relation between belief and truth. The sensitivity condition does the heavy lifting against Gettier cases; the adherence condition handles cases of unstable belief. Sosa''s safety condition is the contemporary refinement.',
    ARRAY['nozick_tracking', 'truth_tracking'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'sensitivity_condition',
    'Sensitivity Condition',
    ARRAY['epistemology'],
    'Nozick''s counterfactual condition for knowledge: S''s belief that p is sensitive iff in the nearest possible world where p is false, S does not believe p. Captures the intuition that knowledge tracks truth across counterfactual variation.',
    'Sensitivity famously fails to satisfy closure under known entailment (S can be sensitive about ordinary p but not about the denial of skeptical scenarios), which Nozick embraces as a feature. Many post-Nozick epistemologists trade sensitivity for safety to preserve closure.',
    ARRAY['sensitivity_principle'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'safety_condition',
    'Safety Condition',
    ARRAY['epistemology'],
    'A modal condition on knowledge (Sosa 1999; Williamson 2000): S''s belief that p is safe iff in nearby possible worlds where S forms the belief that p, p is true. Replaces sensitivity with a same-direction counterfactual that preserves closure.',
    'Safety is the dominant contemporary modal condition. Where sensitivity asks "would you still believe p if p were false?", safety asks "could you easily have believed p falsely?" The shift handles skeptical-closure puzzles that sensitivity gives up on.',
    ARRAY['safety_principle'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'internalism_epistemic',
    'Epistemic Internalism',
    ARRAY['epistemology'],
    'The thesis that the factors that determine whether a belief is justified are factors to which the believer has reflective access — typically her other mental states. Contrasts with externalism, which allows justification-conferring factors (like reliable causal processes) outside the believer''s ken.',
    'Two main motivations: the deontological intuition (the believer is responsible only for what she can access) and the new-evil-demon intuition (a brain-in-a-vat with the same internal states as you is equally justified). Mentalism (Conee and Feldman) is the contemporary version.',
    ARRAY['internalism_about_justification'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'externalism_epistemic',
    'Epistemic Externalism',
    ARRAY['epistemology'],
    'The thesis that some justification-conferring factors lie outside the believer''s reflective access — typically the reliability of the belief-forming process. Reliabilism (Goldman) is the canonical externalist position; tracking and proper-function theories are kin.',
    'Externalism is motivated by the apparent epistemic legitimacy of cognitively unsophisticated agents (children, non-human animals) and by the difficulty of meeting internalist conditions for perceptual knowledge. The new-evil-demon problem is the canonical objection.',
    ARRAY['externalism_about_justification'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'foundationalism',
    'Foundationalism',
    ARRAY['epistemology'],
    'The structural thesis that justified beliefs come in two kinds: basic beliefs (justified non-inferentially) and non-basic beliefs (justified by inferential support from basic beliefs). All justification ultimately bottoms out in the foundational layer.',
    'Classical foundationalism (Descartes, early modern empiricists) requires basic beliefs to be infallible or incorrigible. Modest foundationalism (BonJour''s critics; Pryor) weakens the requirement to mere prima facie justification. The regress argument is the standard motivation.',
    ARRAY['classical_foundationalism'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'coherentism',
    'Coherentism',
    ARRAY['epistemology'],
    'The structural thesis that beliefs are justified by their coherence with the believer''s overall belief system, not by inferential descent to a foundational layer. The web replaces the pyramid.',
    'Coherentism has to specify what coherence amounts to (logical consistency is too weak; mutual explanatory support is the usual fix) and answer the input objection (how does experience constrain belief if only beliefs justify beliefs?). BonJour''s 1985 defense and his later abandonment are pedagogically useful.',
    ARRAY['coherence_theory_of_justification'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'infinitism',
    'Infinitism',
    ARRAY['epistemology'],
    'Peter Klein''s structural thesis that justified beliefs are justified by infinite, non-repeating chains of reasons. Rejects both the foundationalist''s terminating chain and the coherentist''s circular structure.',
    'Infinitism is the minority view; teach it as the third logical possibility in the regress trilemma (terminate, circle, or continue forever). Klein''s defense is that the third option is the only one consistent with the believer always being able to give a further reason on demand.',
    ARRAY['klein_infinitism'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'basic_belief',
    'Basic Belief',
    ARRAY['epistemology'],
    'A belief whose justification does not derive from inferential support by other beliefs — the foundational layer in foundationalist theories. Candidate basic beliefs include perceptual beliefs about one''s immediate experience and self-evident logical or mathematical truths.',
    'The hard question is how a belief can be justified non-inferentially without being a brute given. Sellars''s critique of the myth of the given is the canonical challenge; modest foundationalists respond by allowing basic beliefs to have prima facie but defeasible justification.',
    ARRAY['foundational_belief', 'properly_basic_belief'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'epistemic_closure',
    'Epistemic Closure',
    ARRAY['epistemology'],
    'The principle that knowledge is closed under (some restricted form of) known entailment: if S knows p, and S knows that p entails q, then S knows q. The exact restriction varies; the bare principle is widely held but consequential.',
    'Closure is at the center of skeptical arguments: if you know you have hands, and you know having hands entails not being a brain-in-a-vat, then you know you''re not a brain-in-a-vat. Sensitivity-based theories (Nozick, Dretske) deny closure; safety-based theories preserve it.',
    ARRAY['closure_under_known_entailment'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'testimonial_knowledge',
    'Testimonial Knowledge',
    ARRAY['epistemology'],
    'Knowledge acquired by accepting a speaker''s assertion. Most of what any individual knows comes from testimony rather than first-hand evidence; the epistemological question is what makes testimony a genuine source of knowledge rather than a mere causal channel.',
    'Two main camps: reductionists (Hume) who require the hearer to have independent evidence for the speaker''s reliability, and anti-reductionists (Reid, Coady) who treat testimony as a sui generis source. Social epistemology (P5-01b''s range) takes this further with norms of testimony, trust, and assertion.',
    ARRAY['knowledge_from_testimony'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'fallibilism',
    'Fallibilism',
    ARRAY['epistemology'],
    'The thesis that one can know that p even though one''s grounds for p do not entail p — knowledge does not require certainty. The default contemporary view, traceable to Peirce and Popper, motivated by the rarity of certainty-grade evidence outside mathematics.',
    'Fallibilism makes knowledge possible in the messy empirical world but creates the closure puzzle: if you know p fallibly and know p entails not-skeptical-scenario, do you know not-skeptical-scenario? Different responses reveal one''s broader epistemological commitments.',
    ARRAY[]::TEXT[],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'certainty',
    'Epistemic Certainty',
    ARRAY['epistemology'],
    'The epistemic standing in which doubt is impossible — the believer''s evidence rules out every alternative. Stronger than knowledge on most contemporary accounts. Distinct from psychological certainty (mere felt confidence).',
    'Cartesian epistemology made certainty the standard for knowledge; contemporary fallibilism rejects this. Teach certainty as the limit case to clarify what knowledge does and does not require: knowledge is consistent with the bare possibility of error, certainty is not.',
    ARRAY['psychological_certainty'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'skepticism_epistemic',
    'Epistemic Skepticism',
    ARRAY['epistemology'],
    'The thesis (or argumentative challenge) that we lack knowledge in some target domain — sometimes globally (no knowledge at all), sometimes locally (no knowledge of the external world, of other minds, of the past). Drives much of epistemology by setting the bar arguments must clear.',
    'Distinguish skepticism as a position (we don''t know X) from skeptical arguments (here''s why you don''t know X). The Pyrrhonian tradition treats skepticism as a therapeutic stance; the Cartesian tradition as a methodological tool. Most contemporary epistemology is anti-skeptical.',
    ARRAY['skepticism', 'philosophical_skepticism'],
    'INTERPRETED',
    'ai-seed',
    2
  ),
  (
    'cartesian_skepticism',
    'Cartesian Skepticism',
    ARRAY['epistemology'],
    'The skeptical challenge mounted from radical doubt — the dreaming argument, the evil-demon scenario, the brain-in-a-vat — that one cannot rule out being deceived about the external world. Originating in Descartes''s First Meditation as methodic doubt and recurring as the canonical contemporary skeptical argument.',
    'Cartesian skepticism is the standard test case for contemporary epistemology: any theory of knowledge has to either explain how we know we''re not being deceived (closure-friendly responses), accept that we don''t (concessive responses), or restrict knowledge claims to local domains where the deception scenario doesn''t bite.',
    ARRAY['cartesian_doubt', 'methodic_doubt'],
    'INTERPRETED',
    'ai-seed',
    2
  );

-- Edges: 34 INSERTs, all pedagogical_prerequisite. Source -> Target
-- pairs traverse the analysis-of-knowledge spine, the theories-of-
-- justification branch, and the knowledge-dependent peripheral
-- (closure, testimony, fallibilism, certainty, skepticism). No
-- cross-domain edges (P5-11's exclusive responsibility).
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Foundations -> propositional_knowledge: belief, truth, epistemic_justification
  ('belief', 'propositional_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('truth', 'propositional_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'propositional_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- belief and evidence feed epistemic_justification
  ('belief', 'epistemic_justification', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('evidence', 'epistemic_justification', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- propositional_knowledge -> JTB (the analysis), knowledge (the genus), knowledge_how (the contrast)
  ('propositional_knowledge', 'justified_true_belief', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('propositional_knowledge', 'knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('propositional_knowledge', 'knowledge_how', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('knowledge_how', 'knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- truth -> truth_correspondence (the standard theory)
  ('truth', 'truth_correspondence', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- belief -> basic_belief -> foundationalism
  ('belief', 'basic_belief', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('basic_belief', 'foundationalism', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- epistemic_justification -> theories of justification (structural and access)
  ('epistemic_justification', 'foundationalism', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'coherentism', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'infinitism', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'internalism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'externalism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- JTB -> Gettier -> four standard responses
  ('justified_true_belief', 'gettier_problem', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('gettier_problem', 'no_false_lemmas_response', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('gettier_problem', 'causal_theory_of_knowing', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('gettier_problem', 'defeasibility_analysis', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('gettier_problem', 'tracking_theory_of_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('propositional_knowledge', 'tracking_theory_of_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- tracking -> sensitivity (Nozickean) and safety (Sosa-Williamson refinement)
  ('tracking_theory_of_knowledge', 'sensitivity_condition', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('tracking_theory_of_knowledge', 'safety_condition', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- knowledge-dependent peripheral
  ('knowledge', 'epistemic_closure', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('propositional_knowledge', 'testimonial_knowledge', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('knowledge', 'fallibilism', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('certainty', 'fallibilism', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('belief', 'certainty', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('propositional_knowledge', 'certainty', 'pedagogical_prerequisite', 'ai-seed', 2),
  -- skepticism branch
  ('knowledge', 'skepticism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('epistemic_justification', 'skepticism_epistemic', 'pedagogical_prerequisite', 'ai-seed', 2),
  ('skepticism_epistemic', 'cartesian_skepticism', 'pedagogical_prerequisite', 'ai-seed', 2);

COMMIT;
