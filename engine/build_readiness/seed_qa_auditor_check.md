# Seed-graph QA census — audit-the-auditor methodology check

> Authored by S-0165 (interactive build session) per the approved plan at
> `~/.claude/plans/four-routine-sessions-have-eventual-parnas.md`. A one-off
> methodology-verification report — it does not fit the six standard
> `build_readiness/` file classes ([`README.md`](README.md)); it pairs with the
> class-3 audit master plan [`seed_qa_audit.md`](seed_qa_audit.md) as a check on
> that audit's integrity. Consumed by the SQA-20 closeout and by the user
> deciding whether the `T-SEED-QA` routine should continue as-is.
>
> Evidence files: [`seed_qa_evidence/shard_01_reaudit.md`](seed_qa_evidence/shard_01_reaudit.md),
> [`seed_qa_evidence/shard_04_reaudit.md`](seed_qa_evidence/shard_04_reaudit.md).

## Verdict

**The seed-QA census is not glossing. On the testable criterion (C1 edge
prerequisite-soundness), a fortified re-audit of shards 01 and 04 confirmed
135 of 135 routine verdicts with zero misses and zero false positives — the
graph really is approximately as clean as the census reports, and the
monotonic defect-rate decline across shards is real graph-quality variance, not
scorer drift.** One caveat survives, and it is a rubric-design question rather
than an audit-integrity problem: C2 (teaching-notes traction) has no external
anchor and a "fail" bar low enough that it may never discriminate on this
corpus — see §"Surviving caveat" and Recommendation 3.

## Context — why this check was run

The `T-SEED-QA` routine census had scored 4 of 19 shards and was reporting a
near-clean graph: C1 defect rate 10.7% → 3.6% → 3.6% → 0.0% across shards 01–04,
0 of 111 C2 failures, 2 of 111 C3 failures. Four reasons to distrust the
"near-perfect" read were raised:

1. The defect rate fell **monotonically across randomized shards** — the
   signature of cross-session scorer drift, not graph quality.
2. **0 C2 failures on 111 nodes** on a criterion the rubric itself calls a
   judgment call "with no SEP anchor."
3. The census made **SEP fetching optional** ("parametric-first") — an AI
   grading AI-authored content from shared priors.
4. **Only 12% coverage** (4 of 19 shards) — a small-sample headline.

This check tests concerns 1–3 directly by re-auditing two shards — shard 01
(first routine fire; the careful baseline) and shard 04 (fourth fire; the
0%-defect outlier) — with **mandatory** anchoring: every C1 verdict carries an
`ANCHOR:` line that is either a SEP structural fetch (per
[ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md)) or an
explicit analytic warrant — no bare parametric "Sound" permitted. C2/C3 were
re-scored adversarially.

## Method

- **Source of truth:** the same committed `seed_qa_evidence/shards.json` content
  the routine sessions scored — apples-to-apples.
- **C1 anchoring:** 48 distinct SEP entries fetched once into `/tmp/sep/` via
  [`fetch_structural_reference.py`](../tools/fetch_structural_reference.py)
  (2 slugs 404'd — `phenomenal-concepts`, `science-underdetermination` — those
  edges fell back to analytic warrant + adjacent-entry anchoring). The
  fortification check follows the S-0122 production-audit method: does the source
  concept's forward cross-reference structure support the claimed prerequisite
  direction, and does the target back-link the source (a reversal signal)?
- **Tool status:** `fetch_structural_reference.py` is post-first-exercise (T1-A
  through T1-D closed at S-0122); this run consumed it as a settled tool. 48/50
  fetches exited 0, 0 `AnonymizationViolation` events, polite-fetcher posture
  (2.0s rate-limit, declared User-Agent) accepted by the host throughout — the
  tool's S-0122 empirical record holds.
- **C2/C3:** re-scored by adversarially attempting to fail each summary
  (circular / jargon-gated / assumes-the-concept) and each teaching note
  (restates-summary / throat-clearing / ABSENT). C2/C3 have no external anchor —
  this is a same-model second read, weaker evidence than the C1 comparison.
- **Anti-scope:** no graph migration edits, no `auto_target.json` edits, no
  per-edge Issue filing. The deliverable is the methodology verdict; graph
  corrections route through the existing SQA-20-closeout-then-disposition path.

## Per-shard verdict diff

Every routine verdict was matched against a re-audit verdict. Disagreements are
classified **MISS** (routine scored Sound/pass, re-audit found defective/fail —
the auditor glossed), **FALSE POSITIVE** (routine flagged, re-audit cleared), or
**BOUNDARY SHIFT** (Sound↔Defensible — within scoring noise).

| Shard | Verdicts | Agree | MISS | FALSE POS | BOUNDARY SHIFT |
|---|---|---|---|---|---|
| 01 (S-0158, first fire) | 68 (28 C1 + 40 C2/C3) | 68 | 0 | 0 | 0 |
| 04 (S-0164, fourth fire) | 67 (27 C1 + 40 C2/C3) | 67 | 0 | 0 | 0 |
| **Total** | **135** | **135** | **0** | **0** | **0** |

**100% verdict agreement.** Not one edge the routine scored Sound turned out,
under mandatory SEP anchoring, to be Reversed or Weak-redundant. Not one defect
the routine flagged was a false positive.

### Headline metrics per shard

| Metric | Shard 01 routine | Shard 01 re-audit | Shard 04 routine | Shard 04 re-audit |
|---|---|---|---|---|
| C1 defect rate | 10.7% (3/28) | 10.7% (3/28) | 0.0% (0/27) | 0.0% (0/27) |
| C1 Reversed | E-5, E-24, E-26 | E-5, E-24, E-26 (all confirmed) | none | none |
| C1 Defensible | E-10, E-15, E-20, E-27 | same 4 | E-21 | E-21 |
| C2 fail rate | 0% (0/20) | 0% (0/20) | 0% (0/20) | 0% (0/20) |
| C3 fail rate | 10.0% (2/20: N-4, N-13) | 10.0% (same 2) | 0% (0/20) | 0% (0/20) |

### Where SEP fortification was decisive

The C1 verdicts were not merely re-confirmed parametrically — for several edges
the SEP cross-reference structure independently corroborated the routine's call:

- **Shard 01 E-26 (Knowledge-How → Knowledge, Reversed)** — `knowledge-how`'s SEP
  entry forward-links `knowledge-analysis`; `knowledge-analysis` does *not*
  back-link `knowledge-how`. The cross-reference structure directly shows
  knowledge-how depending on knowledge — corroborating the reversal the routine
  reached by parametric reasoning alone.
- **Shard 01 E-24 (Set → Axiom, Reversed)** — `set-theory`'s SEP entry has only
  4 cross-references, all set-theory-internal; nothing grounds "axiom" as a
  concept. Corroborates the reversal.
- **Shard 04 E-2, E-6 (Existence → Property / Substance, Sound)** — `existence`'s
  SEP entry forward-links both `properties` and `substance`; neither back-links
  `existence`. The structure *supported the authored direction more firmly than
  the routine's own both-ways hedge credited.*
- **Shard 04 E-21 (Speech Act → Gricean Maxims, Defensible)** — `speech-acts` and
  `implicature` mutually cross-reference each other: the relation is real but
  not a tight directional dependency — exactly matching the Defensible verdict.

Fortification **upgraded confidence** across the board; it overturned nothing.

## Drift signal

The original concern: a monotonic defect-rate decline (10.7% → 3.6% → 3.6% →
0.0%) across *randomized* shards looks like a scorer getting faster and more
charitable, not like real quality.

**The drift hypothesis is falsified for C1.** The test was: does the agreement
rate differ between the early shard and the late shard?

- Shard 01 (first fire): **100%** agreement (68/68)
- Shard 04 (fourth fire): **100%** agreement (67/67)
- Gap: **0 percentage points.**

If shard 04's 0.0% defect rate were a drift artifact — a lenient scorer waving
edges through — the fortified re-audit would have surfaced misses (edges scored
Sound that are actually defective). It surfaced **zero**. Shard 04 is exactly as
rigorous as shard 01. The decline 10.7% → 0.0% is **real graph-quality variance
across randomized shards**: shard 01 happened to draw a cluster of three genuine
direction-reversal defects (all SEP-confirmed); shard 04 happened to draw none.
Random shards, real variance — not drift.

This also resolves concern 3 (parametric-first risk): on these 55 edges the
parametric verdicts were 100% confirmed under mandatory SEP anchoring. The
optional-SEP design did not cost C1 accuracy here.

## Surviving caveat — C2 may not discriminate (rubric design, not audit integrity)

Concern 2 (0 C2 failures) is **narrowed but not dismissed**. The adversarial
re-audit confirmed 0 C2 failures across all 40 re-scored nodes — but C2 has no
external anchor, so a same-model reviewer confirming a same-model reviewer is
weak evidence that the C2 *bar* is correctly calibrated.

What the re-audit *can* say, having read all 80 teaching-notes across the two
shards: the seed corpus's `teaching_notes` are **uniformly substantive** —
multi-angle, worked, with named figures and concrete examples. The C2 "fail"
definition (restates summary / abstract throat-clearing / ABSENT) is a low bar,
and this corpus genuinely clears it. The 0% C2 fail rate is therefore *plausibly
real* — but it also means **C2 as currently defined will almost never fail on
this corpus and is not discriminating between strong and merely-adequate
teaching notes.** The single briefest note in either shard (N-11 fallibilism,
shard 04 — two sentences) survives only narrowly.

This is a question for the SQA-20 closeout and the user: if C2 is meant to
*discriminate* teaching-note quality (not just catch absent/degenerate notes),
the bar needs raising. That is a rubric-calibration decision — not evidence the
auditor is glossing.

C3 is in better shape: it has caught 2 genuine failures (N-4 jargon-gated, N-13
circular) and the re-audit confirmed both plus identified the recurring
"dense-open-then-rescue" near-line shape (shard 01 N-14/N-17, shard 04 N-18) —
the bar is discriminating.

## Limits of this check

- **Two shards of nineteen.** This tested the first fire and the
  fourth-of-four — two well-separated points, which is materially stronger than
  testing one — but shards 05–19 are unaudited. The finding is "the method had
  teeth at both ends of the completed run," not "every shard is verified."
- **C1 is genuinely fortified; C2/C3 is a same-model second pass.** The decisive
  evidence is the C1-with-SEP comparison. The C2/C3 agreement is real but cannot
  speak to bar calibration (see above).
- **Two SEP slugs 404'd** (`phenomenal-concepts`, `science-underdetermination`).
  Both affected edges (shard 01 E-5, E-27) were anchored by analytic warrant plus
  adjacent SEP entries; neither verdict turned on the missing fetch.

## Recommendations

For the SQA-20 closeout and the user. None are in-scope for this session
(anti-scope: methodology verdict only).

1. **Let the `T-SEED-QA` routine continue as-is.** The audit-integrity concern
   that motivated this check is resolved for C1: the census is not glossing, and
   there is no scorer-drift signal. Pausing the routine is not warranted.
   Shards 05–19 can run on the existing rubric.

2. **Shards 02 and 03 do not need re-auditing on C1.** With shard 01 (the
   pre-drift baseline) and shard 04 (the post-drift-window outlier) both at 100%
   agreement, the drift hypothesis is falsified at both ends of the completed
   run; shards 02–03 sit between two verified points. Re-auditing them would add
   little. (If the closeout still wants belt-and-suspenders coverage, shard 02 or
   03 is a cheap single re-audit — but it is optional, not indicated.)

3. **Raise the C2 bar — or accept that C2 is an absence-detector, not a quality
   discriminator.** This is the one genuine open question. The closeout should
   either (a) tighten the C2 "fail" definition so it discriminates strong from
   merely-adequate teaching notes, then re-run C2 on the corpus, or (b)
   explicitly re-scope C2 as a degenerate-note *detector* (catches ABSENT /
   restatement only) and stop reading its 0%-fail rate as a quality signal.
   Either is fine; the status quo (reporting 0% C2 fail as if it were a quality
   finding) is misleading.

4. **The SQA-20 closeout's C1 drift-comparison section can cite this check.**
   The closeout was already tasked with explaining the census C1 rate against
   the production audit's 13% baseline and watching for per-shard outliers. This
   report gives it the answer for the first four shards: the variance is real,
   the method is sound, and the convergence toward ~0–4% reflects the graph, not
   the auditor.

## Cross-references

- [`seed_qa_audit.md`](seed_qa_audit.md) — the class-3 audit master plan this
  check verifies.
- [`seed_qa_evidence/shard_01.md`](seed_qa_evidence/shard_01.md) /
  [`shard_04.md`](seed_qa_evidence/shard_04.md) — the original routine evidence.
- [`seed_qa_evidence/shard_01_reaudit.md`](seed_qa_evidence/shard_01_reaudit.md) /
  [`shard_04_reaudit.md`](seed_qa_evidence/shard_04_reaudit.md) — this check's
  per-edge / per-node evidence.
- [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md) —
  the 13% C1 baseline; its fortification method (SEP cross-reference structure)
  is the method this check applied with mandatory rather than optional anchoring.
- [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md) — the
  audit-time SEP-fetch carve-out; [`fetch_structural_reference.py`](../tools/fetch_structural_reference.py)
  the tool.
