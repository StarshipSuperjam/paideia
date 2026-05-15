paths_to_modify: ["engine/build_readiness/seed_qa_evidence/shard_09.md"]
criteria_addressed: [0, 1]

# Plan — S-0170 routine task SQA-09

Routine evidence session for the T-SEED-QA seed-graph QA census. Task SQA-09: score
shard 09 — 27 `pedagogical_prerequisite` edges against C1 (prerequisite soundness) and
20 nodes against C2 (teaching_notes traction) + C3 (summary cold-readability), per the
pinned rubric in `engine/build_readiness/seed_qa_audit.md`.

Shard content is read from the committed `seed_qa_evidence/shards.json` (`shard_09` key)
— routine sessions never touch the DB. Parametric judgment first per the rubric; SEP
fetch reserved for genuinely-uncertain verdicts. Audit follow-up migrations 0061–0065
were cross-referenced before scoring: of the 27 (source,target) pairs in this shard,
**exactly one matches** a migration-touched pair — E-16 `expertise → epistemic_dependence`,
examined by 0063 (weak-edge cleanup) and KEPT with the evidence annotation now carried
verbatim in the shard. The other 26 edges are fresh, non-audit-touched authoring; any
C1 defect found on those is a fresh defect, not a re-opening of an audit decision.

The single deliverable is the scope-locked evidence file
`engine/build_readiness/seed_qa_evidence/shard_09.md`, written to the fixed schema in
`seed_qa_audit.md`. This satisfies criterion 0 (`file_exists`) and criterion 1
(`validate_passes`). No other tracked paths are touched.

Prior-context notes from the diary (last 3 entries — shards 06/07/08):

1. **Over-Defensible-drift watch item.** Defensible counts across shards 04–08:
   1, 4, 6, 3, 1. Not monotone — shard 08 returned to shard 04's floor — so the watch
   item is NOT worsening at the moment. This session continues to apply the rubric
   literally and flags Defensibles only where a real concrete-entry-point or
   near-co-equal reading supports the graph's direction.

2. **"Target is the more general/foundational concept" shape — recurring across
   shards 05/06/07/08.** Four consecutive shards have produced this Defensible-cluster
   pattern (edges where the target is the more general or foundational concept and the
   edge "could be Reversed" but a concrete-entry-point reading supports the current
   direction). Established calibration: hold at Defensible (not Reversed) when a real
   concrete-entry-point reading exists. A rubric-calibration question above an
   evidence session's remit — flagged for the SQA-20 closeout.

3. **C3 jargon-gating pattern — four consecutive shards (05 N-8 SDL, 06 N-16 credence,
   07 N-18 Kantian-framework, 08 N-9 + N-19 modal/intentionality).** Shard 08 produced
   TWO instances rather than one. Strong cross-shard pattern signal for the SQA-20
   closeout. This session applies C3 literally per the pinned criterion — load-bearing
   first sentence gated on undefined technical framework counts as C3-fail.

4. **One Reversed call in shard 08 (E-4 CTM → Turing Test).** The strongest-warranted
   Reversed of the recent run, established by applying the Defensible calibration
   (concrete-entry-point reading required) literally: CTM is more abstract than the
   Turing Test, not more concrete. Authoring defect, not audit-touched. Carry the
   same calibration into this shard.

Shard-09-specific look-aheads (parametric pre-scan, not the verdict):

- **E-16 `expertise → epistemic_dependence`** — the one audit-touched edge this shard.
  0063 examined it as a weak-edge prune candidate and KEPT it with an explicit evidence
  annotation. Re-scoring against C1 is in scope; the disposition will note the audit
  touchpoint.
- **E-12 `causation → determinism`** — classic "target is the more general/foundational
  concept" shape (determinism is arguably the more abstract metaphysical thesis;
  causation is the concrete relation it depends on or rejects). Default-Sound but
  examine for the recurring shape. May produce another Defensible instance for the
  cluster.
- **E-13 `belief → certainty`** — certainty is arguably a graded property of belief;
  the natural pedagogical direction may be belief → degrees → certainty. Watch for
  Defensible if a "certainty is a stronger form of belief" reading dominates.
- **E-9 `argument_logical → inference_rule`** and **E-23 `argument_logical → counterexample`** —
  both share the same source (`argument_logical`); check for Weak-redundant if a more
  proximate prereq chain exists, or if `inference_rule` and `counterexample` are co-equal
  consequences. Likely fine — `argument_logical` is a plausible umbrella prereq for both.
- **E-2 `modus_ponens → propositional_logic`** — direction shape: modus_ponens is a
  rule WITHIN propositional logic, so the standard pedagogical direction is reverse
  (propositional_logic introduces modus_ponens, not the other way around). Carefully
  examine for a possible Reversed verdict, unless a "modus_ponens as the cognitive
  entry point to propositional logic's machinery" concrete-entry-point reading saves
  it as Defensible.
- **E-21 `knowledge_argument → phenomenal_concept_strategy`** — the phenomenal_concept
  strategy is a *response to* the knowledge argument. Direction looks correct
  (response presupposes the argument). Default-Sound.
- **E-15 `universals → nominalism`** — nominalism is a *rejection of* universals as
  abstract entities. The realism-vs-nominalism debate presupposes the concept of
  universals. Default-Sound.
- **E-14 `universals → tropes`** — tropes are an alternative ontology to universals
  (particularized properties). Direction is the standard pedagogical entry. Default-Sound.
- **E-20 `physicalism → behaviorism_logical`** — logical behaviorism is one variant
  *of* physicalism (or a precursor to type identity, on some readings). Default-Sound
  given physicalism is the umbrella framework. Examine for the multi-physicalism shape
  (this shard has E-5 physicalism → type_identity_theory, E-6 physicalism →
  easy_problems, E-20 physicalism → behaviorism_logical — all share source `physicalism`,
  pattern is consistent with physicalism as the framework prereq).
- **N-13 `credence`, N-14 `modal_logic`, N-19 `modal_systems_hierarchy`** — three nodes
  with known framework-gating risk from prior shards (credence flagged C3 in shard 06,
  modal_systems was the framework gating N-9 in shard 08). Apply C3 literally; if the
  load-bearing first sentence presupposes Bayesian probability formalism or modal
  logic axioms without unpacking, it C3-fails.
- **N-17 `kantian_aesthetic_judgment`** — Kantian aesthetics framework was the C3
  gating in shard 07 N-18. If this node's summary repeats the "free play of imagination
  and understanding" technical jargon load-bearing in the first sentence without
  unpacking, it's another C3-fail of the same shape.

These are pre-scan flags, not verdicts. The actual scoring follows the rubric in the
evidence file.

## Prior context (MemPalace boot search)

_Generated by `engine/tools/mempalace_boot_search.py` at 2026-05-15T04:03:47Z. Three formulations × similarity ≥0.60 = 0 drawers._

### Literal — `shard 09 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file`
- _no drawers above threshold_

### Conceptual — `shard census score edges prerequisite soundness`
- _no drawers above threshold_

### Adjacent — `shard 09 qa census score 27 edges c1 prerequisite soundness 20 nodes c2 teaching_notes traction c3 summary cold-readability per the seed_qa_audit md rubric read the shard from seed_qa_evidence shards json write the evidence file lessons pushback`
- _no drawers above threshold_
