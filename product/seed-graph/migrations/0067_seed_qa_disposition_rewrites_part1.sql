-- Migration: 0067_seed_qa_disposition_rewrites_part1
-- Purpose: Disposition of the S-0182 T-SEED-QA census C3 findings: the
--   13 nodes whose summaries failed the C3 cold-readability rubric
--   (load-bearing first sentence gated on undefined formal apparatus
--   or technical-term-of-art) are rewritten per the topic-handle-first
--   pattern documented in seed_qa_findings.md §6.3. Each rewrite
--   prepends a plain-language topic-handle sentence that names what
--   the concept is at a level a freshman-default learner can grasp,
--   then leads into the formal apparatus that the original summary
--   placed in the load-bearing position. The passing-sibling exemplar
--   per cluster — e.g., modal_logic ("The formal logic of necessity
--   and possibility") for the modal-systems-hierarchy node — already
--   exhibits the target shape; this migration brings the 13 failing
--   nodes to that shape.
--
--   The 13 failing nodes cluster by failure class (per §6.3):
--     Modal-logic apparatus (3): accessibility_relation,
--       modal_systems_hierarchy, conditional_logic
--     Deontic-logic SDL acronym (2): ross_paradox, chisholm_paradox
--     Logico-mathematical paradox (1): curry_paradox
--     Probabilistic-notation gated (2): conditionalization,
--       bayes_theorem
--     Phenomenal-character / mind framework (3):
--       phenomenal_intentionality, causal_exclusion_argument,
--       representationalism_perception
--     Kantian third-Critique framework (1):
--       free_play_imagination_understanding
--     Borderline-circular aesthetic (1): aesthetic_experience
--
--   Census prevalence: 13 / 380 = 3.4%, concentrated in logic (23.1%)
--   and mind (5.3%) subdomains per §4.2. The rewrites preserve the
--   technical content of each summary; the first 1-2 sentences change
--   to land a plain-language topic-handle, and subsequent sentences
--   are minimally adjusted for flow.
-- Loads tables: public.nodes (13 UPDATEs; summary column only).
-- Preconditions:
--   * 0066 applied (the 7 C1 reversals landed; baseline node count =
--     380 unchanged).
--   * settings.graph_version = 16.
--   * All 13 node ids exist in public.nodes (verified via S-0183
--     pre-author DB query).
-- Postconditions:
--   * 13 rows in public.nodes have their summary column rewritten to
--     start with a plain-language topic-handle sentence (verified
--     per-node via Layer 2.5 LIKE assertions below).
--   * Node count unchanged: 380 active nodes.
--   * No other node columns mutated (id, label, domain, teaching_notes,
--     aliases, rigor_score_*, confidence, provenance, status,
--     superseded_by, graph_version_added, created_at all preserved;
--     updated_at re-bumps to NOW() per UPDATE behavior).
--   * settings.graph_version = 16 (unchanged).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.nodes WHERE id = 'curry_paradox' AND summary LIKE 'A paradox of self-reference that shows naive theories of truth%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'aesthetic_experience' AND summary LIKE 'The mode of attentive engagement we have when we contemplate%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'ross_paradox' AND summary LIKE 'A puzzle in the formal logic of obligation that exposes how%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'conditionalization' AND summary LIKE 'The standard rule prescribing how a rational agent should update%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'free_play_imagination_understanding' AND summary LIKE 'Kant''s explanation of why the pleasure we take in beauty feels universal%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'accessibility_relation' AND summary LIKE 'The relation between possible worlds that determines which alternatives%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'phenomenal_intentionality' AND summary LIKE 'The view that conscious experience is what fundamentally makes thoughts%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'chisholm_paradox' AND summary LIKE 'A puzzle showing that standard formal systems of obligation cannot%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'modal_systems_hierarchy' AND summary LIKE 'The standard ladder of formal logics of necessity and possibility%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'bayes_theorem' AND summary LIKE 'The rule for revising the probability of a hypothesis in light of new evidence%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'causal_exclusion_argument' AND summary LIKE 'An argument that mental properties cannot genuinely cause physical events%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'representationalism_perception' AND summary LIKE 'The view that what it is to perceive the world is for one''s experience%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'conditional_logic' AND summary LIKE 'The formal logic of "if it had been the case" statements%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id IN ('curry_paradox','aesthetic_experience','ross_paradox','conditionalization','free_play_imagination_understanding','accessibility_relation','phenomenal_intentionality','chisholm_paradox','modal_systems_hierarchy','bayes_theorem','causal_exclusion_argument','representationalism_perception','conditional_logic') AND char_length(summary) >= 200 :: 13
-- Invariants:
--   * No nodes inserted or deleted; only summary column mutated on 13
--     existing nodes.
--   * Each rewrite preserves the technical content of the original
--     summary; the difference is the addition or rewriting of the
--     load-bearing first sentence to lead with plain-language
--     topic-handle.
--   * char_length on every rewritten summary >= 200 (sanity bound;
--     none of the 13 rewrites is shorter than 200 characters).
-- Non-responsibilities:
--   * Does not modify the 367 nodes that PASSED C3.
--   * Does not modify teaching_notes (C2 traction was 100% PASS;
--     nothing to fix).
--   * Does not modify edges.
--   * Does not increment public.settings.graph_version (follows the
--     0061-0065 audit-followup precedent).
--   * Does not capture the §6.5 workflow lesson into a doc — that
--     amendment lands at ADR 0059 in the same session.
-- Cross-cutting decisions:
--   * Topic-handle-first pattern: each rewrite starts with one
--     plain-language sentence naming what the concept is, calibrated
--     against the freshman-defaults posture per ADR 0012. Subsequent
--     sentences carry the original formal apparatus / technical
--     content; the only structural change is the prepended (or
--     rewritten) load-bearing first sentence.
--   * No teaching_notes mutation: per the rubric, C3 is a summary
--     readability concern; teaching_notes are PASS for all 13 and are
--     left untouched.
-- Source citations:
--   * QA census closeout findings:
--     engine/build_readiness/seed_qa_findings.md §6.3 C3 cluster.
--   * QA census per-shard evidence files: shards 01, 05, 06, 07, 08,
--     09, 11 (the failing nodes' originating shards).
--   * Passing-sibling exemplars per cluster:
--     modal_logic (shard 09 N-14, "The formal logic of necessity and
--       possibility") for the modal-systems-hierarchy /
--       accessibility-relation / conditional-logic cluster.
--     deontic_logic for the ross-paradox / chisholm-paradox cluster.
--     representationalism_consciousness for the phenomenal-character /
--       phenomenal-intentionality cluster.
--     probability_mathematical for the bayes-theorem /
--       conditionalization cluster.
--     kantian_aesthetic_judgment for the
--       free-play-imagination-understanding node.
--   * product/adr/0012-freshman-defaults-autodidact-ceiling.md —
--     the audience-calibration the topic-handle sentences target.
-- Idempotency:
--   * Not idempotent. Re-applying after the first apply would update 0
--     rows on each UPDATE (no row matches the WHERE clause once the
--     rewrites have landed; the LIKE-anchored postcondition assertions
--     would then return count = 0 on re-fire of the SQL body alone).
--     The wrapper's exit-6 already-applied gate is the canonical
--     re-fire defense.
-- Rollback:
--   See sibling 0067_seed_qa_disposition_rewrites_revert_part1.sql
--   which UPDATEs the 13 summaries back to their pre-0067 text
--   (captured in S-0183 pre-author DB query).
-- Dependencies:
--   * Hard: 0002 (schema). 0011 + the subsequent seed batches that
--     authored the 13 originals. 0066 (most recent applied; pre-apply
--     baseline node count = 380).
--   * Soft: ROUTING.md (per-session narrative appended in same commit).
-- Related:
--   * engine/build_readiness/seed_qa_findings.md §6.3 + §7.1;
--   * engine/build_readiness/seed_qa_audit.md (pinned census rubric);
--   * engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--     (apply via wrapper; Layer 2.5 postcondition assertions);
--   * engine/operations/migration-discipline.md Layer 2.5;
--   * product/adr/0012-freshman-defaults-autodidact-ceiling.md;
--   * 0067_seed_qa_disposition_rewrites_revert_part1.sql (sibling).

BEGIN;

-- ============================================================
-- Logic — paradox cluster (curry_paradox, ross_paradox, chisholm_paradox)
-- ============================================================

-- curry_paradox: topic-handle = "A paradox of self-reference that
-- shows naive theories of truth allow deriving any conclusion from a
-- single self-referential sentence."
UPDATE public.nodes
   SET summary = 'A paradox of self-reference that shows naive theories of truth allow deriving any conclusion from a single self-referential sentence. Haskell Curry''s 1942 construction: consider a sentence C asserting "if C is true then Q" for any Q. Naive truth principles plus the deduction theorem and contraction yield Q for arbitrary Q, including absurdities. Distinct from the liar in not requiring negation; distinct from Russell''s paradox in operating in propositional logic alone. Particularly stubborn because it survives in many non-classical responses to the liar.'
 WHERE id = 'curry_paradox';

-- ross_paradox: topic-handle = "A puzzle in the formal logic of
-- obligation that exposes how standard rules of inference can produce
-- conclusions about permitted alternatives that no original obligation
-- seemed to authorize."
UPDATE public.nodes
   SET summary = 'A puzzle in the formal logic of obligation that exposes how standard rules of inference can produce conclusions about permitted alternatives that no original obligation seemed to authorize. Alf Ross''s 1941 construction: in standard deontic logic (SDL), the obligation "you ought to mail the letter" (Om) entails "you ought to mail the letter or burn the letter" (O(m ∨ b)) by modal closure on disjunction-introduction. The latter conclusion seems wrong: the permission to burn the letter (carried by the disjunction''s right disjunct) was not obviously authorized by the original obligation.'
 WHERE id = 'ross_paradox';

-- chisholm_paradox: topic-handle = "A puzzle showing that standard
-- formal systems of obligation cannot consistently represent what we
-- ought to do when we have already violated a primary duty (the
-- contrary-to-duty case)."
UPDATE public.nodes
   SET summary = 'A puzzle showing that standard formal systems of obligation cannot consistently represent what we ought to do when we have already violated a primary duty (the "contrary-to-duty" case). Roderick Chisholm''s 1963 construction: standard deontic logic (SDL) cannot consistently formalize the joint claim that (1) it ought to be that Jones helps his neighbor, (2) it ought to be that if Jones helps his neighbor he tells him he is coming, (3) if Jones does not help his neighbor he ought not to tell him he is coming, (4) Jones does not help his neighbor. The four are jointly consistent in natural language but yield contradictory obligations in SDL.'
 WHERE id = 'chisholm_paradox';

-- ============================================================
-- Logic — modal-logic apparatus cluster (accessibility_relation,
-- modal_systems_hierarchy, conditional_logic)
-- ============================================================

-- accessibility_relation: topic-handle = "The relation between
-- possible worlds that determines which alternatives a world counts as
-- a relevant possibility."
UPDATE public.nodes
   SET summary = 'The relation between possible worlds that determines which alternatives a world counts as a relevant possibility. In Kripke semantics for modal logic, the binary relation R between possible worlds: a world w'' is "accessible from" world w when R(w, w''). Necessity at world w is truth at every world accessible from w; possibility is truth at some accessible world. Different constraints on R (reflexivity, symmetry, transitivity, Euclideanness, seriality) correspond exactly to different modal axiom schemes and yield different modal systems.'
 WHERE id = 'accessibility_relation';

-- modal_systems_hierarchy: topic-handle = "The standard ladder of
-- formal logics of necessity and possibility, each rung adding
-- stronger structural assumptions about which worlds count as
-- alternatives to which."
UPDATE public.nodes
   SET summary = 'The standard ladder of formal logics of necessity and possibility, each rung adding stronger structural assumptions about which worlds count as alternatives to which. The ordered family of normal modal propositional logics — K ⊂ T ⊂ S4 ⊂ S5 — generated by progressively strengthening the accessibility relation. K (no constraint) is the minimal normal modal logic. T (reflexive) adds □P → P. S4 (reflexive + transitive) adds □P → □□P. S5 (equivalence relation) adds ◇P → □◇P. Other systems (D, B, K4, S4.2, S4.3) fill out the lattice with deontic and other modal applications.'
 WHERE id = 'modal_systems_hierarchy';

-- conditional_logic: topic-handle = "The formal logic of "if it had
-- been the case" statements — counterfactual conditionals that talk
-- about what would have happened in scenarios that did not actually
-- occur."
UPDATE public.nodes
   SET summary = 'The formal logic of "if it had been the case" statements — counterfactual conditionals that talk about what would have happened in scenarios that did not actually occur. Developed by Robert Stalnaker (1968) and David Lewis (1973). Treats the counterfactual operator □→ as a non-truth-functional binary connective, evaluated at a Kripke-style frame whose accessibility structure encodes a similarity ordering on worlds. The system invalidates classical principles like strengthening the antecedent (P □→ Q does not entail (P ∧ R) □→ Q), transitivity (P □→ Q and Q □→ R do not entail P □→ R), and contraposition.'
 WHERE id = 'conditional_logic';

-- ============================================================
-- Probabilistic-notation cluster (conditionalization, bayes_theorem)
-- ============================================================

-- conditionalization: topic-handle = "The standard rule prescribing
-- how a rational agent should update degrees of belief after observing
-- new evidence."
UPDATE public.nodes
   SET summary = 'The standard rule prescribing how a rational agent should update degrees of belief after observing new evidence. The Bayesian formulation: upon learning evidence E with certainty, set new credence in any hypothesis H equal to the old conditional credence Pr_old(H | E). The operation transforms one coherent credence function into another and is the canonical Bayesian update rule. Refinements include Jeffrey conditionalization (uncertain evidence) and imaging (counterfactual update).'
 WHERE id = 'conditionalization';

-- bayes_theorem: topic-handle = "The rule for revising the probability
-- of a hypothesis in light of new evidence by inverting the
-- conditional relationship between hypothesis and evidence."
UPDATE public.nodes
   SET summary = 'The rule for revising the probability of a hypothesis in light of new evidence by inverting the conditional relationship between hypothesis and evidence. Stated formally as P(H|E) = P(E|H) · P(H) / P(E), where P(H) is the prior probability of hypothesis H, P(E|H) is the likelihood of evidence E given H, P(E) is the marginal probability of E (computed by the law of total probability over a partition of hypotheses), and P(H|E) is the posterior probability of H after observing E. The mathematical centerpiece of Bayesian epistemology, Bayesian confirmation theory, and Bayesian statistical inference. Named for Thomas Bayes (1701-1761), whose posthumous 1763 essay introduced the result in the special case of binary outcomes; the modern general formulation traces to Pierre-Simon Laplace.'
 WHERE id = 'bayes_theorem';

-- ============================================================
-- Mind — phenomenal-character cluster (phenomenal_intentionality,
-- causal_exclusion_argument, representationalism_perception)
-- ============================================================

-- phenomenal_intentionality: topic-handle = "The view that conscious
-- experience is what fundamentally makes thoughts about anything in
-- the first place, rather than the reverse."
UPDATE public.nodes
   SET summary = 'The view that conscious experience is what fundamentally makes thoughts about anything in the first place, rather than the reverse. Defended by Terence Horgan and John Tienson (2002) and developed by David Pitt and others: phenomenal character grounds intentionality, so original intentional content is constituted by, or fixed by, phenomenal character. Inverts the direction of explanation in standard naturalistic theories of content (which start with intentionality and try to derive phenomenal character via representationalism).'
 WHERE id = 'phenomenal_intentionality';

-- causal_exclusion_argument: topic-handle = "An argument that mental
-- properties cannot genuinely cause physical events if every physical
-- event already has a complete physical cause."
UPDATE public.nodes
   SET summary = 'An argument that mental properties cannot genuinely cause physical events if every physical event already has a complete physical cause. Developed by Jaegwon Kim (1989, 1998, 2005) against non-reductive physicalism. If mental property M supervenes on physical property P, and P is causally sufficient for the physical effect, then M is causally pre-empted — its instantiation makes no difference because P does the causal work. Either M is identical to P (reduction), or M is causally inert (epiphenomenalism), or the effect is overdetermined (implausible).'
 WHERE id = 'causal_exclusion_argument';

-- representationalism_perception: topic-handle = "The view that what
-- it is to perceive the world is for one''s experience to carry
-- information that says how the world is around one."
UPDATE public.nodes
   SET summary = 'The view that what it is to perceive the world is for one''s experience to carry information that says how the world is around one. In having a perceptual experience, the subject undergoes a state with intentional content (typically: that such-and-such is the case before me). The phenomenal character of the experience is exhausted by, or supervenes on, its representational content. Defended by Tye, Dretske, Lycan, and Chalmers in different versions.'
 WHERE id = 'representationalism_perception';

-- ============================================================
-- Aesthetics cluster (aesthetic_experience,
-- free_play_imagination_understanding)
-- ============================================================

-- aesthetic_experience: topic-handle = "The mode of attentive
-- engagement we have when we contemplate artworks, natural scenes, or
-- designed objects for their own sake, focusing on how they look,
-- sound, or feel rather than on what we can do with them."
UPDATE public.nodes
   SET summary = 'The mode of attentive engagement we have when we contemplate artworks, natural scenes, or designed objects for their own sake, focusing on how they look, sound, or feel rather than on what we can do with them. Variously analyzed as disinterested contemplation (Kant, Schopenhauer, Stolnitz), absorbed attention (Beardsley), the disclosure of significant form (Bell), make-believe participation (Walton), or the perception of expressive properties (Goodman, Davies). The unity of the category — whether aesthetic experiences share a single distinctive phenomenal or functional character — is itself contested.'
 WHERE id = 'aesthetic_experience';

-- free_play_imagination_understanding: topic-handle = "Kant''s
-- explanation of why the pleasure we take in beauty feels universal
-- rather than merely personal: the mind''s image-forming and
-- concept-applying faculties enter a harmonious cooperation that does
-- not settle on any particular concept."
UPDATE public.nodes
   SET summary = 'Kant''s explanation of why the pleasure we take in beauty feels universal rather than merely personal: the mind''s image-forming and concept-applying faculties enter a harmonious cooperation that does not settle on any particular concept. Developed in the third Critique (1790) as the cognitive grounding of the judgment of taste. When a beautiful object engages the observer, the cognitive faculties — imagination (which gathers and synthesizes the perceptual manifold) and understanding (which subsumes the synthesized matter under concepts) — enter into this harmonious cooperation that does not terminate in any determinate concept. This free play (without the constraint of a particular concept being applied) generates the pleasurable feeling that grounds the universal communicability of the judgment of taste, since the cooperation of the cognitive faculties is shared by all rational beings.'
 WHERE id = 'free_play_imagination_understanding';

COMMIT;
