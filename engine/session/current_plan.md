paths_to_modify: ["engine/build_readiness/seed_qa_evidence/shard_12.md"]
criteria_addressed: [0, 1]

# Plan — S-0174 routine task SQA-12

Routine evidence session for the T-SEED-QA seed-graph QA census. Task SQA-12: score
shard 12 — 27 `pedagogical_prerequisite` edges against C1 (prerequisite soundness) and
20 nodes against C2 (teaching_notes traction) + C3 (summary cold-readability), per the
pinned rubric in `engine/build_readiness/seed_qa_audit.md`.

Shard content is read from the committed `seed_qa_evidence/shards.json` (`shard_12`
key) — routine sessions never touch the DB. Parametric judgment first per the rubric;
SEP fetch reserved for genuinely-uncertain verdicts. Audit follow-up migrations
0061–0065 were cross-referenced against every (source, target) tuple in this shard's
edge set before scoring.

**Zero audit-touched edges this shard.** Cross-reference of every shard-12 edge tuple
against the assertion-block tuple lists in migrations 0061 / 0062 / 0063 / 0064 / 0065
returned zero exact-or-reverse matches. This is the lowest audit-footprint shard in
the routine batch so far (vs shard 11's 5/27 = 18.5% and shard 10's 2/27 = 7.4%). The
naive grep returned two near-misses worth recording for closeout: (a) `evidence →
problem_of_induction` (E-9) — 0062 flipped a different edge whose target is
`problem_of_induction` (`pyrrhonian_skepticism → problem_of_induction`); the
shard-12 edge is unrelated. (b) `modality → possible_worlds` (E-25) — 0064 backfilled
evidence for `abstract_object → possible_worlds` and `modality → essence_metaphysical`,
not for this specific pair. Both edges are scored as fresh authoring, not as
re-opening any audit decision.

Implication: shard 12 is a clean fresh-authoring drift check. Any C1 defect found here
is a fresh defect, not a re-opening of an audit decision.

The single deliverable is the scope-locked evidence file
`engine/build_readiness/seed_qa_evidence/shard_12.md`, written to the fixed schema in
`seed_qa_audit.md`. This satisfies criterion 0 (`file_exists`) and criterion 1
(`validate_passes`). No other tracked paths are touched.

## Prior-context notes from the diary (shards 09 / 10 / 11)

1. **Cumulative C1 across shards 01–11: 23 / 299 = 7.7%** — firmly under the
   production audit's 13% baseline. The cumulative rate ticked DOWN from 9.4% at
   shard 09 → 8.5% at shard 10 → 7.7% at shard 11. Six 0-defect shards bracketing the
   3.6–3.7% pickup shards.

2. **C3 fail-streak shape is composition-driven, not authoring drift.** Shards 05–09
   each produced ≥1 C3 fail (shard 09 = five); shard 10 broke the streak; shard 11
   produced one (N-17 conditional_logic — load-bearing modal-logic vocabulary not
   glossed inline in the summary). Shape predicts: a shard whose nodes lean
   logic-tech-philosophy or modal-semantics will pick up C3 fails; a shard whose
   nodes lean foundational/introductory will not.

3. **"Target is the more general/foundational concept" shape continues.** Shards
   05–11 each produced ≥1 instance of the discipline-→-object-of-study or
   umbrella-→-foundational sub-shape; calibration held at Defensible (not Reversed)
   when a concrete-entry-point reading supports the graph's direction. The
   SQA-20 closeout rubric-calibration question now has seven consecutive data points.
   Shard 11's E-4 `philosophy_of_mind → mind` was flagged as the strongest tip-to-
   Reversed candidate yet.

4. **Defensible cluster middle band.** Counts across shards 04–11: 1 / 4 / 6 / 3 / 1
   / 2 / 2 / 4. Over-Defensible-drift watch item not worsening.

5. **First cycle-deferred companion edge encountered in shard 11** (E-14
   `propositional_attitude → proposition`). S-0123 cycle-deferral kept the opposite
   direction as a documented co-companion to break the resulting graph cycle. Scored
   Sound on the cycle-deferral signal; calibration anchor for any subsequent cases.

## Shard-12-specific look-aheads (parametric pre-scan, not the verdict)

- **E-1 `art → institutional_theory_of_art`** — Dickie's institutional theory is a
  specific theory of WHAT art is. Topic → theory shape. Sound.
- **E-2 `meaning → sense_and_reference`** — Frege's Sinn/Bedeutung distinction is the
  paradigm structural analysis of linguistic meaning. Meaning is the topic;
  sense/reference is one foundational analysis. Sound (topic → analysis).
- **E-3 `propositional_knowledge → justified_true_belief`** — JTB IS the standard
  analysis of propositional knowledge. Topic → analysis. Sound.
- **E-4 `substance → bundle_theory`, E-5 `tropes → bundle_theory`** — bundle theory
  (Hume, Russell) analyzes substance/object as a bundle of properties (or tropes).
  E-4 is umbrella-→-theory (substance is the umbrella metaphysical category; bundle
  theory is one analysis). E-5 is prereq-component-→-theory (tropes are the
  ontological building blocks bundle theory works with). Both likely Sound.
- **E-6 `vienna_circle_logical_positivism → behaviorism_logical`** — logical
  behaviorism (Ryle, Carnap, Hempel) was developed by Vienna-Circle-adjacent
  philosophers as the philosophy-of-mind application of verificationism (mental
  state ascriptions are reducible to behavioral dispositions). Long historical jump
  but the conceptual prereq is real. Likely Sound; watch for Weak-redundant if a
  more proximate prereq (verificationism, anti-mentalism) exists in the graph.
- **E-7 `kripke_semantics → conditional_logic`** — Kripke-style frames with
  accessibility relations are the model-theoretic apparatus for both modal logic and
  Stalnaker/Lewis counterfactual conditional logic. The model-theoretic prereq is
  real. Likely Sound.
- **E-8 `epistemic_justification → externalism_epistemic`** — externalism is a
  position about WHAT justification consists in (reliabilism, proper-functionalism).
  Topic → theory. Sound.
- **E-9 `evidence → problem_of_induction`** — Hume's problem is whether
  evidence-from-past-instances justifies belief about future ones. Evidence is the
  conceptual prereq for the problem (the problem is about evidence's role). Sound.
- **E-10 `phenomenal_consciousness → hard_problem_of_consciousness`** — Block's
  phenomenal/access distinction precedes and motivates Chalmers's hard problem.
  Sound.
- **E-11 `formal_proof → classical_logic`** — slightly tricky. Formal proof is a
  general syntactic notion; classical logic is one specific proof system. Standard
  pedagogical direction is classical-logic-first (you learn modus ponens, then you
  understand "proof"). Edge runs opposite. Possibly Defensible on the
  "formal-syntactic-machinery is the umbrella" reading, possibly Reversed on the
  pedagogical reading. Flag for careful scoring.
- **E-12 `deontology → supererogation`, E-26 `normative_ethics → supererogation`** —
  supererogation (going beyond duty) is a category that emerges where there is a
  notion of duty/obligation. E-12 (deontology as the duty-centric ethical tradition)
  is the proximate prereq. E-26 (normative_ethics as the broader umbrella) is a
  more distant prereq. Both Sound on their own; E-26 may be Weak-redundant if E-12
  already encodes the duty-prereq more proximately. Calibration question.
- **E-13 `deductive_nomological_model → inference_to_the_best_explanation`** — DN
  model (Hempel) is covering-law; IBE (Harman) is abductive. Both are accounts of
  scientific explanation but they're parallel rivals, not one prereq of the other.
  Possibly Weak-redundant or Reversed; check whether one historically/conceptually
  preconditions the other.
- **E-14 `intentionality → meaning`** — intentionality (aboutness, Brentano) is the
  mental property; meaning is the semantic property. Standard direction in
  philosophy of mind is mental-intentionality-first; in philosophy of language it
  often runs meaning-first. Possibly Sound on Brentano-Husserl-Searle reading;
  possibly Reversed on the language-first reading. Flag for careful scoring.
- **E-15 `modus_tollens → falsificationism`** — Popper's falsificationism is the
  application of modus tollens to scientific theories (if T predicts P and ¬P, then
  ¬T). Inference rule → philosophical application. Sound.
- **E-16 `social_epistemology → epistemic_injustice`** — Fricker's epistemic
  injustice operates within the social-epistemology framework (knowers as situated
  social agents). Framework → specific account. Sound.
- **E-17 `reference → sense_and_reference`** — sense/reference IS Frege's analysis
  of reference (and meaning). Reference is the topic; sense/reference is the
  Fregean analysis. Topic → analysis. Sound.
- **E-18 `deontology → kantian_ethics`** — Kantian ethics is the canonical
  deontological theory but historically Kant invented it; deontology is a
  category-name that came later. Standard pedagogical direction is Kant-first
  (you learn the categorical imperative) → deontology (the category-name).
  Edge runs opposite. Same "umbrella → specific theory" shape as elsewhere. Likely
  Defensible.
- **E-19 `probability_mathematical → expected_value`** — expected value is defined
  in terms of probability. Component-prereq. Sound.
- **E-20 `existence → event`** — events are entities that exist; existence is
  presupposed. Component-prereq. Sound (same shape as shard 10's E-15 `existence →
  causation`).
- **E-21 `knowledge → social_epistemology`** — social epistemology is epistemology
  applied to socially-situated knowers. Topic → specialization. Sound.
- **E-22 `social_epistemology → epistemic_dependence`** — epistemic dependence
  (Hardwick, Coady) is a phenomenon studied within social epistemology. Framework
  → specific phenomenon. Sound.
- **E-23 `scientific_theory → scientific_realism`** — scientific realism is a
  position about the truth-content of scientific theories. Theory is the prereq
  concept. Sound.
- **E-24 `belief → credence`** — credence (subjective probability) is a
  graded/quantitative refinement of binary belief. Topic → refinement. Sound.
- **E-25 `modality → possible_worlds`** — possible worlds (Lewis, Kripke) are the
  standard model-theoretic apparatus for modal claims. Modality is the topic;
  possible worlds is one analysis. Sound.
- **E-27 `kantian_aesthetic_judgment → free_play_imagination_understanding`** — the
  free play of imagination and understanding is Kant's specific account of WHAT
  pure aesthetic judgment consists in (Critique of Judgment, §§9, 35). Topic →
  Kant's analysis. Sound.

Node look-aheads (C3 cold-readability watch list):

- **N-2 `mereology`** — formal theory of parts and wholes; "part-whole structure"
  is the conceptual core, easy to gloss. Likely PASS.
- **N-3 `formal_proof`** — Gentzen-style natural deduction or Hilbert axiomatic
  proof; load-bearing technical apparatus. Check inline gloss.
- **N-4 `representational_theory_of_mind`** — Fodor; "Language of Thought";
  computational-formal symbols. Technical-philosophy node. C3 watch.
- **N-7 `function_mathematical`** — formal definition (ordered pairs, domain,
  codomain). Math-tech node. Check whether the summary glosses for a cold reader.
- **N-8 `duhem_quine_thesis`** — confirmation holism; "no experiment tests a
  hypothesis in isolation." Check inline gloss of confirmation-holism vocabulary.
- **N-10 `sensitivity_condition`** — Nozick's tracking theory; "if p were false, S
  would not believe p." Check inline statement of the counterfactual condition.
- **N-11 `deflationary_theory_of_truth`** — equivalence schema / T-schema /
  Tarski / Horwich; logic-tech vocabulary. C3 watch.
- **N-12 `demarcation_problem`** — Popper's falsifiability criterion; "what
  distinguishes science from pseudoscience." Familiar-domain framing; likely PASS.
- **N-14 `chinese_room_argument`** — Searle 1980 thought experiment; concrete
  example carries cold readers. Likely PASS.
- **N-16 `externalism_epistemic`** — load-bearing technical position; check
  whether the "justification depends on factors outside the head" gloss is inline.
- **N-20 `modus_tollens`** — basic inference rule (if A→B and ¬B, then ¬A); concrete
  symbolic form usually glosses well. Likely PASS.

These are pre-scan flags, not verdicts. The actual scoring follows the rubric in the
evidence file.
