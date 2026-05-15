paths_to_modify: ["engine/build_readiness/seed_qa_evidence/shard_10.md"]
criteria_addressed: [0, 1]

# Plan — S-0172 routine task SQA-10

Routine evidence session for the T-SEED-QA seed-graph QA census. Task SQA-10: score
shard 10 — 27 `pedagogical_prerequisite` edges against C1 (prerequisite soundness) and
20 nodes against C2 (teaching_notes traction) + C3 (summary cold-readability), per the
pinned rubric in `engine/build_readiness/seed_qa_audit.md`.

Shard content is read from the committed `seed_qa_evidence/shards.json` (`shard_10` key)
— routine sessions never touch the DB. Parametric judgment first per the rubric; SEP
fetch reserved for genuinely-uncertain verdicts. Audit follow-up migrations 0061–0065
were cross-referenced before scoring: of the 27 (source,target) pairs in this shard,
**exactly one matches** a migration-touched pair — E-26 `pyrrhonian_skepticism →
problem_of_induction`, the result of a 0062 direction-flip (the prior direction was
`problem_of_induction → pyrrhonian_skepticism`; 0062 flipped it per S-0122 audit because
Pyrrhonian tradition pre-dates Hume's problem by millennia and the Agrippan trilemma
does not depend on induction-skepticism). The other 26 edges are fresh, non-audit-touched
authoring; any C1 defect found on those is a fresh defect, not a re-opening of an audit
decision. (The `renaissance_mechanism → vienna_circle_logical_positivism` edge mentions
both endpoints in 0061's retyping list as endpoints of OTHER retyped edges, but this
specific pair was NOT retyped — it remains a fresh, non-audit-touched
`pedagogical_prerequisite` edge.)

The single deliverable is the scope-locked evidence file
`engine/build_readiness/seed_qa_evidence/shard_10.md`, written to the fixed schema in
`seed_qa_audit.md`. This satisfies criterion 0 (`file_exists`) and criterion 1
(`validate_passes`). No other tracked paths are touched.

Prior-context notes from the diary (last 3 entries — shards 07/08/09):

1. **Cumulative C1 across shards 01–09: 23 / 245 = 9.4%** — firmly under the production
   audit's 13% baseline. Three 0-defect shards (04, 06, 07, 09) bracketing the
   3.6–3.7% pickup shards. The drift signal is "no drift" so far.

2. **C3 jargon-gating cluster — five consecutive shards** (05 N-8 SDL, 06 N-16 credence,
   07 N-18 Kantian framework, 08 N-9 + N-19 modal/intentionality, 09 N-6/N-7/N-8/N-16/N-19
   five instances driven by a high concentration of technical-philosophy nodes). The
   pattern is now strong enough that the SQA-20 closeout should articulate the implied
   authoring rule: "load-bearing first sentence may use technical terms but must gloss
   each one inline." This session applies C3 literally per the pinned criterion.

3. **"Target is the more general/foundational concept" shape — recurring across shards
   05–09** (at least one Defensible-instance per shard). Established calibration: hold
   at Defensible (not Reversed) when a real concrete-entry-point reading supports the
   graph's direction. Rubric-calibration question flagged for the SQA-20 closeout.

4. **Calibration on glossed vs ungated jargon (from S-0170).** Shard 07
   `representationalism_consciousness` PASSED C3 because "phenomenal character" was
   glossed as "what it is like to have an experience"; shard 09
   `representationalism_perception` FAILED on the same load-bearing term left ungated.
   Pass standard: load-bearing technical term must be glossed inline. Same node concept
   can pass or fail depending on whether the gloss is present.

Shard-10-specific look-aheads (parametric pre-scan, not the verdict):

- **E-26 `pyrrhonian_skepticism → problem_of_induction`** — the one audit-touched edge
  this shard. 0062 direction-flipped it from `problem_of_induction → pyrrhonian_skepticism`
  per the S-0122 audit. Score against C1 normally; the verdict against the new
  audit-validated direction will note the audit touchpoint.
- **E-7 `existence → abstract_object`, E-15 `existence → causation`, E-17 `ontology →
  existence`** — all share `existence` as endpoint and look like umbrella/general-concept
  edges. Check for the "target more general" Defensible shape, especially `ontology →
  existence` (existence is arguably the centerpiece OF ontology, not its prerequisite).
- **E-2 `morality → metaethics`** — direction shape: metaethics is reasoning ABOUT
  morality, so the natural pedagogical direction is morality → metaethics. Default-Sound.
- **E-12 `free_will → principle_of_alternative_possibilities`** — PAP is a thesis
  within the free-will debate; free_will is the broader concept. Default-Sound.
- **E-13 `mental_state → consciousness`, E-14 `consciousness → easy_problems_of_consciousness`**
  — both look like standard pedagogical direction (mental states being the genus,
  consciousness being a specific kind; consciousness preceding the easy/hard problem
  carve-up). Default-Sound on both.
- **E-19 `renaissance_mechanism → vienna_circle_logical_positivism`** — long historical
  jump across the predicate. Vienna Circle's logical positivism is 1920s+; Renaissance
  mechanism is ~16th–17th century. The intermediate history (Enlightenment empiricism,
  19th-century positivism) makes this a long-distance edge — examine for Weak-redundant
  if more proximate prerequisites exist in the graph.
- **E-22 `reductionism_in_science → multiple_realizability_in_science`** — multiple
  realizability is the canonical ANTI-reductionist argument (it presupposes reductionism
  to argue against). Default-Sound.
- **E-24 `paradigm → research_programme`** — Lakatos's research programmes are
  explicitly the successor framework to Kuhn's paradigm concept (Lakatos developed it
  as a refinement/response to Kuhn). Default-Sound.
- **E-3 `predicate_logic → russell_paradox`** — Russell's paradox is set-theoretic
  (not purely predicate-logic) but predicate logic is the formal-language prereq for
  understanding the paradox's statement. Default-Sound.
- **E-11 `bivalence_principle → counterexample`** — counterexample is a general logical
  notion, not specifically tied to bivalence. The edge direction is plausible but
  bivalence is arguably the wrong proximate prereq. Examine for Weak-redundant.
- **N-1 `turing_test`, N-3 `fuzzy_logic`, N-4 `tarskis_t_schema`, N-13
  `hypothetico_deductivism`** — first sentences with date+author conventions, look
  unlikely to C3-fail (operational benchmark / continuous truth degrees / formal schema
  / standard textbook account are paraphraseable from the first sentence). Apply C3
  literally anyway.
- **N-5 `mental_causation`, N-7 `numerical_identity`, N-12 `generality_problem`,
  N-19 `determinism`** — short summaries; check for C2 traction (do `teaching_notes`
  actually give a learner a foothold or are they restatement-of-summary?).
- **N-10 `supervaluationism`, N-16 `linguistic_relativity`, N-17 `philosophical_zombie`**
  — load-bearing technical jargon (sharpenings / Sapir-Whorf / conceivability-possibility).
  Check whether each is glossed inline in the first sentence of the summary; same
  pass/fail standard as S-0170's representationalism calibration.

These are pre-scan flags, not verdicts. The actual scoring follows the rubric in the
evidence file.

## Prior context (MemPalace boot search)

_Generated by `engine/tools/mempalace_boot_search.py` at 2026-05-14. Three formulations × similarity ≥0.60 = 0 drawers._

### Literal — `shard 10 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file`
- _no drawers above threshold_

### Conceptual — `shard census score edges prerequisite soundness`
- _no drawers above threshold_

### Adjacent — `shard 10 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file lessons pushback`
- _no drawers above threshold_
