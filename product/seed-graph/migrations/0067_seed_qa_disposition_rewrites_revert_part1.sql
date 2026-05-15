-- Migration: 0067_seed_qa_disposition_rewrites_revert_part1
-- Purpose: Revert all 13 C3 summary rewrites applied by
--   0067_seed_qa_disposition_rewrites_part1.sql. UPDATEs each node's
--   summary back to its pre-0067 text (captured byte-for-byte from
--   S-0183 pre-author DB query). Used for hotfix rollback per
--   engine/operations/revert-and-rollback-discipline.md (ADR 0078).
--
--   This revert exists for emergency rollback only; the forward 0067
--   is the canonical post-disposition state. Reverting requires user
--   adjudication of why the C3 rewrites should not stand.
-- Loads tables: public.nodes (13 UPDATEs; summary column only).
-- Preconditions:
--   * 0067_seed_qa_disposition_rewrites_part1.sql applied (the 13
--     summaries carry their post-rewrite text).
--   * settings.graph_version = 16 (unchanged from 0067).
-- Postconditions:
--   * 13 rows in public.nodes have their summary column restored to
--     pre-0067 text.
--   * Node count unchanged: 380 active nodes.
--   * No other node columns mutated; updated_at re-bumps to NOW().
--   * settings.graph_version = 16 (unchanged).
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0055 / ADR 0039 amendment.)
--   SELECT count(*)::int FROM public.nodes WHERE id = 'curry_paradox' AND summary LIKE 'Haskell Curry''s 1942 paradox%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'aesthetic_experience' AND summary LIKE 'The distinctive mode of perceptual and reflective engagement%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'ross_paradox' AND summary LIKE 'Alf Ross''s 1941 disjunctive permission paradox%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'conditionalization' AND summary LIKE 'The Bayesian rule for belief revision%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'free_play_imagination_understanding' AND summary LIKE 'Kant''s third Critique (1790) account of the cognitive grounding%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'accessibility_relation' AND summary LIKE 'In Kripke semantics for modal logic, the binary relation R%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'phenomenal_intentionality' AND summary LIKE 'The view, defended by Terence Horgan and John Tienson%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'chisholm_paradox' AND summary LIKE 'Roderick Chisholm''s 1963 contrary-to-duty obligation paradox%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'modal_systems_hierarchy' AND summary LIKE 'The standard ordered family of normal modal propositional logics%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'bayes_theorem' AND summary LIKE 'The formal probability-inversion identity%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'causal_exclusion_argument' AND summary LIKE 'Jaegwon Kim''s argument (1989, 1998, 2005)%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'representationalism_perception' AND summary LIKE 'The view that perceptual experience represents the world%' :: 1
--   SELECT count(*)::int FROM public.nodes WHERE id = 'conditional_logic' AND summary LIKE 'The formal logic of counterfactual conditionals developed by Robert Stalnaker%' :: 1
-- Invariants:
--   * No nodes inserted or deleted; only summary column mutated on the
--     same 13 nodes the forward migration touched.
-- Non-responsibilities:
--   * Does not revert any other surface (ADR 0059 amendment, MemPalace
--     decision drawer, GitHub Issue) authored alongside 0067.
--   * Does not preserve updated_at byte-identically — the UPDATE
--     re-bumps via DEFAULT NOW().
-- Cross-cutting decisions:
--   * Hotfix posture: this file is for emergency rollback per ADR 0078,
--     not for routine application.
-- Source citations:
--   * Forward migration: 0067_seed_qa_disposition_rewrites_part1.sql.
--   * Original summaries captured in S-0183 pre-author DB query
--     (/tmp/s0183_data.json snapshot).
-- Idempotency:
--   * Not idempotent. Re-applying after the first revert apply would
--     update 0 rows on each UPDATE.
-- Rollback:
--   The rollback of the revert is re-applying 0067's forward migration
--   (with manual schema_migrations bookkeeping if needed).
-- Dependencies:
--   * Hard: 0067_seed_qa_disposition_rewrites_part1.sql.
-- Related:
--   * 0067_seed_qa_disposition_rewrites_part1.sql (forward sibling);
--   * engine/operations/revert-and-rollback-discipline.md (ADR 0078);
--   * engine/build_readiness/seed_qa_findings.md §6.3.

BEGIN;

UPDATE public.nodes
   SET summary = 'Haskell Curry''s 1942 paradox: consider a sentence C asserting "if C is true then Q" for any Q. Naive truth principles plus the deduction theorem and contraction yield Q for arbitrary Q, including absurdities. Distinct from the liar in not requiring negation; distinct from Russell''s paradox in operating in propositional logic alone. Particularly stubborn because it survives in many non-classical responses to the liar.'
 WHERE id = 'curry_paradox';

UPDATE public.nodes
   SET summary = 'The distinctive mode of perceptual and reflective engagement characteristic of attending to aesthetic objects (artworks, natural scenes, designed environments) under the aspect of their aesthetic properties. Variously analyzed as disinterested contemplation (Kant, Schopenhauer, Stolnitz), absorbed attention (Beardsley), the disclosure of significant form (Bell), make-believe participation (Walton), or the perception of expressive properties (Goodman, Davies). The unity of the category — whether aesthetic experiences share a single distinctive phenomenal or functional character — is itself contested.'
 WHERE id = 'aesthetic_experience';

UPDATE public.nodes
   SET summary = 'Alf Ross''s 1941 disjunctive permission paradox: in SDL, the obligation "you ought to mail the letter" (Om) entails "you ought to mail the letter or burn the letter" (O(m ∨ b)) by modal closure on disjunction-introduction. The latter conclusion seems wrong: the permission to burn the letter (carried by the disjunction''s right disjunct) was not obviously authorized by the original obligation.'
 WHERE id = 'ross_paradox';

UPDATE public.nodes
   SET summary = 'The Bayesian rule for belief revision: upon learning evidence E with certainty, set new credence in any hypothesis H equal to the old conditional credence Pr_old(H | E). The operation transforms one coherent credence function into another and is the canonical Bayesian update rule. Refinements include Jeffrey conditionalization (uncertain evidence) and imaging (counterfactual update).'
 WHERE id = 'conditionalization';

UPDATE public.nodes
   SET summary = 'Kant''s third Critique (1790) account of the cognitive grounding of the judgment of taste. When a beautiful object engages the observer, the cognitive faculties — imagination (which gathers and synthesizes the perceptual manifold) and understanding (which subsumes the synthesized matter under concepts) — enter into a harmonious cooperation that does not terminate in any determinate concept. This free play (without the constraint of a particular concept being applied) generates the pleasurable feeling that grounds the universal communicability of the judgment of taste, since the cooperation of the cognitive faculties is shared by all rational beings.'
 WHERE id = 'free_play_imagination_understanding';

UPDATE public.nodes
   SET summary = 'In Kripke semantics for modal logic, the binary relation R between possible worlds that determines which worlds are "accessible from" a given world. Necessity at world w is truth at every world accessible from w; possibility is truth at some accessible world. Different constraints on R (reflexivity, symmetry, transitivity, Euclideanness, seriality) correspond exactly to different modal axiom schemes and yield different modal systems.'
 WHERE id = 'accessibility_relation';

UPDATE public.nodes
   SET summary = 'The view, defended by Terence Horgan and John Tienson (2002) and developed by David Pitt and others, that phenomenal character grounds intentionality rather than the reverse: original intentional content is constituted by, or fixed by, phenomenal character. Inverts the direction of explanation in standard naturalistic theories of content (which start with intentionality and try to derive phenomenal character via representationalism).'
 WHERE id = 'phenomenal_intentionality';

UPDATE public.nodes
   SET summary = 'Roderick Chisholm''s 1963 contrary-to-duty obligation paradox: SDL cannot consistently formalize the joint claim that (1) it ought to be that Jones helps his neighbor, (2) it ought to be that if Jones helps his neighbor he tells him he is coming, (3) if Jones does not help his neighbor he ought not to tell him he is coming, (4) Jones does not help his neighbor. The four are jointly consistent in natural language but yield contradictory obligations in SDL.'
 WHERE id = 'chisholm_paradox';

UPDATE public.nodes
   SET summary = 'The standard ordered family of normal modal propositional logics — K ⊂ T ⊂ S4 ⊂ S5 — generated by progressively strengthening the accessibility relation. K (no constraint) is the minimal normal modal logic. T (reflexive) adds □P → P. S4 (reflexive + transitive) adds □P → □□P. S5 (equivalence relation) adds ◇P → □◇P. Other systems (D, B, K4, S4.2, S4.3) fill out the lattice with deontic and other modal applications.'
 WHERE id = 'modal_systems_hierarchy';

UPDATE public.nodes
   SET summary = 'The formal probability-inversion identity: P(H|E) = P(E|H) · P(H) / P(E), where P(H) is the prior probability of hypothesis H, P(E|H) is the likelihood of evidence E given H, P(E) is the marginal probability of E (computed by the law of total probability over a partition of hypotheses), and P(H|E) is the posterior probability of H after observing E. The mathematical centerpiece of Bayesian epistemology, Bayesian confirmation theory, and Bayesian statistical inference. Named for Thomas Bayes (1701-1761), whose posthumous 1763 essay introduced the result in the special case of binary outcomes; the modern general formulation traces to Pierre-Simon Laplace.'
 WHERE id = 'bayes_theorem';

UPDATE public.nodes
   SET summary = 'Jaegwon Kim''s argument (1989, 1998, 2005) that non-reductive physicalism cannot accommodate genuine mental causation. If mental property M supervenes on physical property P, and P is causally sufficient for the physical effect, then M is causally pre-empted — its instantiation makes no difference because P does the causal work. Either M is identical to P (reduction), or M is causally inert (epiphenomenalism), or the effect is overdetermined (implausible).'
 WHERE id = 'causal_exclusion_argument';

UPDATE public.nodes
   SET summary = 'The view that perceptual experience represents the world: in having a perceptual experience, the subject undergoes a state with intentional content (typically: that such-and-such is the case before me). The phenomenal character of the experience is exhausted by, or supervenes on, its representational content. Defended by Tye, Dretske, Lycan, and Chalmers in different versions.'
 WHERE id = 'representationalism_perception';

UPDATE public.nodes
   SET summary = 'The formal logic of counterfactual conditionals developed by Robert Stalnaker (1968) and David Lewis (1973). Treats the counterfactual operator □→ as a non-truth-functional binary connective, evaluated at a Kripke-style frame whose accessibility structure encodes a similarity ordering on worlds. The system invalidates classical principles like strengthening the antecedent (P □→ Q does not entail (P ∧ R) □→ Q), transitivity (P □→ Q and Q □→ R do not entail P □→ R), and contraposition.'
 WHERE id = 'conditional_logic';

COMMIT;
