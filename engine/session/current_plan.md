paths_to_modify: ["engine/build_readiness/seed_qa_evidence/shard_11.md"]
criteria_addressed: [0, 1]

# Plan — S-0173 routine task SQA-11

Routine evidence session for the T-SEED-QA seed-graph QA census. Task SQA-11: score
shard 11 — 27 `pedagogical_prerequisite` edges against C1 (prerequisite soundness) and
20 nodes against C2 (teaching_notes traction) + C3 (summary cold-readability), per the
pinned rubric in `engine/build_readiness/seed_qa_audit.md`.

Shard content is read from the committed `seed_qa_evidence/shards.json` (`shard_11` key)
— routine sessions never touch the DB. Parametric judgment first per the rubric; SEP
fetch reserved for genuinely-uncertain verdicts. Audit follow-up migrations 0061–0065
were cross-referenced before scoring. This shard carries an unusually heavy audit
footprint — **five of 27 edges are audit-touched** (vs shard 10's 1-of-27), and three
of those five involve `modal_logic` as the source endpoint:

- **E-1 `explanatory_gap → hard_problem_of_consciousness`** — S-0122 audit
  direction-flip (Levine 1983 precedes and motivates Chalmers 1995). Score Sound on
  the audit-validated direction.
- **E-3 `modal_logic → epistemic_closure`** — S-0122 audit direction-flip (modal
  logic is the formal apparatus; closure is formalized via the K axiom). Score Sound
  on the audit-validated direction.
- **E-14 `propositional_attitude → proposition`** — S-0123 cycle-deferral. 0062
  flipped CB-E-63 from `propositional_attitude → proposition` to `proposition →
  propositional_attitude` per S-0122 verdict (propositions are content-bearers;
  attitudes hold propositions). The current shard's edge has the **original
  pre-flip direction**, which means either (a) the database state was rolled back,
  (b) this is a different edge with the same endpoints, or (c) the shards.json
  snapshot pre-dates the flip. Worth scrutinizing — score against the audit-validated
  direction (proposition → propositional_attitude); if the current direction is
  pre-flip, that's a Reversed verdict against the audit decision.
- **E-24 `virtue_ethics → moral_particularism`** — S-0122 audit. Virtue ethics's
  practical-wisdom focus encodes a commitment to particularism. Score Sound on the
  audit-validated direction.
- **E-25 `modal_logic → formal_epistemology`** — S-0122 audit direction-flip
  (modal logic is foundational; formal epistemology uses modal logic). Score Sound
  on the audit-validated direction.

The other 22 edges are fresh, non-audit-touched authoring; any C1 defect found on
those is a fresh defect, not a re-opening of an audit decision.

The single deliverable is the scope-locked evidence file
`engine/build_readiness/seed_qa_evidence/shard_11.md`, written to the fixed schema in
`seed_qa_audit.md`. This satisfies criterion 0 (`file_exists`) and criterion 1
(`validate_passes`). No other tracked paths are touched.

Prior-context notes from the diary (last 3 entries — shards 08/09/10):

1. **Cumulative C1 across shards 01–10: 23 / 272 = 8.5%** — firmly under the
   production audit's 13% baseline (ticked DOWN from 9.4% to 8.5% with shard 10's
   0-defect score). Five 0-defect shards (04, 06, 07, 09, 10) bracketing the
   3.6–3.7% pickup shards. The drift signal is "no drift."

2. **C3 streak break at shard 10** — shards 05–09 each produced ≥1 C3 fail; shard
   10 broke the streak (0 fails). The shape is composition-driven, not authoring
   drift: shard 10's nodes leaned foundational/introductory; shard 09's leaned
   technical-philosophy. Two borderline-PASS calls on shard 10 (N-3 fuzzy_logic
   t-norm jargon; N-12 generality_problem reliabilism jargon) flagged for closeout.

3. **"Target is the more general/foundational concept" shape** — recurring across
   shards 05–10 (at least one instance per shard). Established calibration: hold at
   Defensible (not Reversed) when a real concrete-entry-point reading supports the
   graph's direction. Rubric-calibration question flagged for the SQA-20 closeout.
   Six consecutive data points feeding it; shard 11 has at least three candidate
   instances (see look-aheads below).

4. **Calibration on glossed vs ungated jargon** — load-bearing technical term must
   be glossed inline (S-0170 representationalism calibration). Same node concept
   can pass or fail depending on whether the gloss is present.

Shard-11-specific look-aheads (parametric pre-scan, not the verdict):

- **E-2 `aesthetics → art`, E-12 `aesthetics → aesthetic_property`** — both have
  aesthetics as source. Aesthetics is the philosophical-study-OF the topic; the
  standard pedagogical direction is topic-first (art / aesthetic_property) then
  the discipline that studies them. Recurring "target more general/foundational"
  shape OR the "discipline→object-of-study" shape. Check whether the concrete-entry-
  point reading saves the direction (do students learn aesthetics-as-discipline as
  the doorway to thinking about art and aesthetic properties?). Likely Defensible.
- **E-4 `philosophy_of_mind → mind`** — most extreme version of the same shape.
  Philosophy of mind is THE philosophical study of mind; mind is the topic. Standard
  pedagogical direction is mind-first (you have a mind; you can think about minds)
  then philosophy of mind (you can do philosophy about that). Likely Defensible
  on the discipline-as-doorway reading; possibly Reversed on strict reading.
- **E-18 `anti_intentionalism → intentionalism_artistic`** — anti-intentionalism IS
  a response to intentionalism (the New Critics's Wimsatt-Beardsley "intentional
  fallacy" was a response to intentionalism). The natural direction is
  intentionalism → anti_intentionalism (positive position first, critical response
  second). Possibly Reversed; check for a concrete-entry-point or audit-validated
  reading that saves the current direction.
- **E-26 `semantic_paradox → liar_paradox`** — the liar IS the paradigm semantic
  paradox. Standard pedagogical direction is liar-first (you encounter it as the
  paradigmatic case) then semantic_paradox (you theorize the category). But the
  genus→species reading is also defensible (category-first, then instance). Likely
  Sound or Defensible.
- **E-13 `validity_logical → soundness_logical`** — soundness = valid AND true
  premises. Validity is a component of soundness. Sound (component-prereq).
- **E-21 `substance → substance_dualism`** — substance is the metaphysical concept;
  substance dualism is a specific position in philosophy of mind that posits two
  substances. Sound (umbrella → specific position).
- **E-22 `scientific_theory → reductionism_in_science`** — reductionism is a
  meta-theoretic thesis about how theories relate. Theory is the prereq concept.
  Sound.
- **E-23 `existence → numerical_identity`** — numerical identity is about being one
  and the same thing; existence is presupposed. Sound (same shape as shard 10's
  E-15 `existence → causation`, scored Sound).
- **E-15 `scientific_realism → constructive_empiricism`** — constructive empiricism
  (van Fraassen) is the canonical anti-realist position. Same shape as shard 10's
  E-22 `reductionism_in_science → multiple_realizability_in_science` and shard 07's
  audit-validated `physicalism → reductionism_in_science`. Sound on the
  presupposes-target-of-criticism reading.
- **E-19 `composition_mereological → simples` and E-9 `knowledge → virtue_epistemology`,
  E-17 `moral_realism → moral_naturalism`, E-20 `epistemic_justification → coherentism`,
  E-11 `consciousness → higher_order_theory_consciousness`, E-6 `meaning → use_theory_of_meaning`,
  E-10 `modal_logic → counterfactual_conditional`, E-27 `accessibility_relation →
  kripke_semantics`, E-7 `epistemic_justification → propositional_knowledge`,
  E-8 `event → causation`, E-5 `causal_theory_of_reference → semantic_externalism`** —
  all default-Sound on first inspection (umbrella→species, framework→specialization,
  or component-prereq shape).
- **E-16 `communitarianism → multiculturalism`** — communitarianism (Taylor, Sandel,
  MacIntyre) and multiculturalism (Kymlicka) are parallel/overlapping political-
  philosophy positions. Whether one strictly prerequisites the other or whether
  they're parallel responses to the liberal-individualist mainstream is unclear.
  Possibly Defensible.
- **N-3 `integrated_information_theory`** — Φ (phi) is load-bearing technical
  apparatus in the first sentence ("a system is conscious to the degree that its
  informational structure is irreducibly integrated, measured by the quantity Φ").
  Apply C3 strictly — is Φ glossed enough inline that a cold reader gets it?
- **N-8 `rigid_designator`** — "designates the same object in every possible world
  in which that object exists" is the conceptual core. Modal-semantics vocabulary.
  Check inline gloss.
- **N-13 `qualia_functionalism`** — "qualia are functional properties" — both
  qualia and functionalism are technical terms. C3 likely PASS via the contextual
  gloss "individuated by their typical causal relations to perceptual inputs,
  cognitive states, and behavioral outputs."
- **N-15 `depiction`** — Wollheim's "seeing-in" is the technical core; check inline
  gloss in the first sentence.
- **N-17 `conditional_logic`** — Stalnaker/Lewis counterfactual logic; "non-truth-
  functional binary connective" and "accessibility structure" appear in the first
  sentence. Strict-reading FAIL candidate.
- **N-9 `phenomenal_consciousness`, N-4 `access_consciousness`** — paired Block
  distinction. Check whether each summary stands on its own without requiring the
  other.
- **N-12 `vagueness`** — borderline cases, sorites paradox. Likely PASS (familiar
  examples in the summary).
- **N-6 `justice_bioethical`** — long teaching_notes (UNOS, Belmont, Tuskegee).
  C2 trivially PASS; C3 check on the bioethics-specific framing in the summary.

These are pre-scan flags, not verdicts. The actual scoring follows the rubric in the
evidence file.

## Prior context (MemPalace boot search)

_Generated by `engine/tools/mempalace_boot_search.py` at 2026-05-15T06:19:00Z. Three formulations × similarity ≥0.60 = 4 drawers._

### Literal — `shard 11 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file`
- **wing_claude/diary** (source: `?`; sim: 0.61) — SESSION:2026-05-15|S-0172|routine.T-SEED-QA.SQA-10|seed-graph.QA.census.shard.10|★★★ What I worked on. Tenth routine fire of the T-SEED-QA census. Scored shard 10 — 27 pedagogic...
- **sessions/planning** (source: `af166e8d-af02-4471-afd3-601e640ada15.jsonl`; sim: 0.62) — **Results** - Wrote [engine/build_readiness/seed_qa_evidence/shard_10.md](engine/build_readiness/seed_qa_evidence/shard_10.md): 27 edges scored against C1, 20 nodes against C2/C...

### Conceptual — `shard census score edges prerequisite soundness`
- _no drawers above threshold_

### Adjacent — `shard 11 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file lessons pushback`
- **wing_claude/diary** (source: `?`; sim: 0.62) — SESSION:2026-05-15|S-0172|routine.T-SEED-QA.SQA-10|seed-graph.QA.census.shard.10|★★★ What I worked on. Tenth routine fire of the T-SEED-QA census. Scored shard 10 — 27 pedagogic...
- **sessions/planning** (source: `af166e8d-af02-4471-afd3-601e640ada15.jsonl`; sim: 0.62) — **Results** - Wrote [engine/build_readiness/seed_qa_evidence/shard_10.md](engine/build_readiness/seed_qa_evidence/shard_10.md): 27 edges scored against C1, 20 nodes against C2/C...
