# Seed-graph QA census — fortified re-audit of shard 04

> Authored by S-0165 (interactive build session) per the approved plan at
> `~/.claude/plans/four-routine-sessions-have-eventual-parnas.md` ("Audit the
> auditor"). Companion to [`shard_01_reaudit.md`](shard_01_reaudit.md); same
> method. Re-scores shard 04 — the *last* of the four completed census shards
> and the 0%-defect outlier ([`shard_04.md`](shard_04.md), S-0164) — with
> mandatory C1 anchoring and an adversarial C2/C3 pass, to test whether the
> monotonic defect-rate decline (10.7% → 3.6% → 3.6% → 0.0% across shards 01–04)
> is real graph quality or cross-session scorer drift.
>
> Method as in `shard_01_reaudit.md`: every C1 verdict carries an `ANCHOR:` line
> (SEP structural fetch or explicit analytic warrant); no bare parametric
> "Sound". C2/C3 re-scored adversarially; C2/C3 have no external anchor so that
> pass is a same-model second read.

## Shard metadata
- Shard: 04 (re-audit)
- Original evidence: `shard_04.md` (S-0164, 2026-05-14)
- Edges scored: 27
- Nodes scored: 20
- Re-scored: 2026-05-14 (S-0165)
- SEP fetches consumed: shared `/tmp/sep/` corpus with the shard 01 re-audit

## Edge findings (C1)

### E-1 — Proposition → Truth-Conditional Semantics
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `propositions` — cross-references include `meaning`
(truth-conditional semantics is the meaning-as-truth-conditions theory). No
standalone "truth-conditional-semantics" slug; analytic warrant: propositions
are the truth-bearers the theory trades in — the concept precedes the theory.
RATIONALE: A learner needs the truth-bearer concept before the theory built on it.

### E-2 — Existence → Property
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `existence` — cross-references include `properties` (forward
link present). SEP-fetch `properties` — does NOT back-link `existence`. Forward
link present, no reversal signal: the SEP structure *supports* the authored
direction more firmly than the original's both-ways flag credited.
RATIONALE: Existence/being is the most general metaphysical frame; property is
one category populating it. Genus-frame → category.

### E-3 — Mental State → Mental Causation
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `mental-causation` — a problem-entry whose cross-references
(physicalism, dualism, functionalism, properties, causation-metaphysics …)
presuppose the mental-state concept; section path "1. Preliminaries". Analytic
warrant: mental causation is the *problem* of how mental states cause things —
stated in terms of mental states.
RATIONALE: The constituent concept must precede the problem stated in terms of it.

### E-4 — Applied Ethics → Environmental Ethics
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `environmental-ethics` (32 cross-references, topic-rich) +
analytic warrant: environmental ethics is uncontroversially a branch of applied
ethics. Field → subfield containment.
RATIONALE: Field → subfield, the standard pedagogical order.

### E-5 — Axiom (Mathematical) → Formal Proof
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — a formal proof is a sequence derived *from axioms*
via inference rules; the axiom concept is a definitional component of "formal
proof." Note the contrast with shard 01's E-24 (Set → Axiom, Reversed): there a
set does not ground the axiom concept; here axioms genuinely ground proofs.
RATIONALE: The concept of an axiom is a clear definitional prerequisite for
formal proof.

### E-6 — Existence → Substance
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `existence` — cross-references include `substance` (forward
link present). SEP-fetch `substance` — does NOT back-link `existence`. Forward
link present, no reversal signal.
RATIONALE: Substance is a category of being; existence (being in general) →
substance (a kind of being). Genus → species.

### E-7 — Philosophy of Science → Scientific Method
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `scientific-method` — a 57-cross-reference topic hub; no
"philosophy-of-science" slug exists. `philosophy_of_science` is a top-level
discipline label sourcing a foundation-spine edge. Per the S-0122 production
audit's granularity finding #3, the "discipline-as-umbrella → core-topic"
pattern is *accepted*, not a defect.
RATIONALE: Field-frame → topic, the standard order. Sub-observation:
discipline-label-as-source — accepted pattern; the original's both-ways flag
(concrete practice taught first) is appropriately cautious but not a defect.

### E-8 — Free Will → Incompatibilism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `free-will` — cross-references include *both*
`incompatibilism-arguments` and `incompatibilism-theories`. Strong forward
support.
RATIONALE: Incompatibilism is a position about free will; the concept precedes a
specific position about it.

### E-9 — Mereology → Composition (Mereological)
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `mereology` (28 cross-references; section path "1. 'Part' and
Parthood") — composition has no standalone slug; the special composition
question is a core topic *within* mereology, which takes parthood as primitive
and defines composition from it. Analytic warrant: field/theory → core notion.
RATIONALE: Mereology is the general theory of parts and wholes; composition is a
core relation within it.

### E-10 — Persistence → Endurantism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `temporal-parts` (the home of the persistence debate) —
persistence and endurantism have no standalone slugs; endurantism is one answer
to the persistence question. Analytic warrant: topic → specific theory of it.
RATIONALE: Persistence is the question of how objects persist through time;
endurantism is one answer.

### E-11 — Philosophy of Language → Reference
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `reference` (a topic entry); no "philosophy-of-language" slug.
`philosophy_of_language` is a top-level discipline label; reference is a core
topic of it — accepted discipline-as-umbrella pattern (per E-7).
RATIONALE: Reference is a core topic of philosophy of language. Field-frame →
topic. Sub-observation: discipline-label-as-source — accepted pattern.

### E-12 — Conditional Probability → Conditionalization
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — conditionalization (Bayesian updating: new credence =
prior conditional probability) is *defined* on conditional probability.
Corroborated by SEP-fetch `bayesian-epistemology` whose machinery
(`bayes-theorem`, `conditionals`, `probability-interpret`) is built on
conditional probability.
RATIONALE: A clear definitional prerequisite; cross-domain service → epistemology.

### E-13 — Liberty (Political) → Republicanism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `positive-and-negative-liberty` — cross-references include
`republicanism` (forward link present). The neo-Roman republican tradition
(Pettit, Skinner) is centrally a theory about liberty as non-domination.
RATIONALE: The concept of political liberty precedes the theory that reconceives
it.

### E-14 — Bioethics → End-of-Life Ethics
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `theory-bioethics` (theory-internal cross-references) +
analytic warrant: end-of-life ethics is uncontroversially a subfield of
bioethics.
RATIONALE: Field → subfield.

### E-15 — Political Authority → Democracy
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `authority` — cross-references include `democracy` (forward
link present). SEP-fetch `democracy` — back-links `authority` and `legitimacy`.
The authority entry forward-linking democracy supports general-question →
specific-answer; the mutual link confirms the relation.
RATIONALE: Political authority is the general question of the right to rule;
democracy is one account of how authority is legitimated. The original's
both-ways flag is cautious; SEP forward-link supports the authored direction.

### E-16 — Environmental Ethics → Climate Ethics
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `environmental-ethics` — cross-references include
`justice-climate` (the climate-ethics topic). Forward link present.
RATIONALE: Climate ethics is a subfield of environmental ethics. Coherent chain
with E-4: applied_ethics → environmental_ethics → climate_ethics.

### E-17 — Numerical Identity → Mereology
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `mereology` — cross-references include `identity` and
`identity-time`. Mereological theses are stated in terms of numerical identity
(extensionality of parthood; composition as identity); the mereology entry
linking `identity` corroborates that identity is upstream machinery.
RATIONALE: Numerical identity is a foundational primitive; mereological theses
deploy it. Chain with E-9.

### E-18 — Metaethics → Moral Realism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `metaethics` — cross-references include `moral-realism`
(forward link present). SEP-fetch `moral-realism` — back-links `metaethics`.
Field → position, forward link present.
RATIONALE: Metaethics is the field; moral realism is one position within it.

### E-19 — Philosophy of Language → Meaning (Linguistic)
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — `philosophy_of_language` discipline label → `meaning`,
a core topic; accepted discipline-as-umbrella pattern (parallels E-11). Meaning
is corroborated as a language-domain hub concept by appearing upstream in
`speech-acts` / `implicature` cross-reference sets.
RATIONALE: Meaning is a core topic of philosophy of language. Field-frame →
topic.

### E-20 — Material Conditional → Indicative Conditional
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `indicative-conditionals` — cross-references include
`logic-classical` and `logic-conditionals`; the indicative-conditional entry
references classical logic (where the material conditional lives) as background.
The material conditional is a logical primitive introduced first; the indicative
conditional is the harder topic engaged via the paradoxes of material implication.
RATIONALE: Curricular order is material → indicative; the material conditional is
a logical primitive, not "a theory of" the indicative. The original's
phenomenon-before-theory both-ways flag is cautious but the standard order
dominates.

### E-21 — Speech Act → Gricean Maxims (Cooperative Principle)
VERDICT: Defensible  (original: Defensible — AGREE)
ANCHOR: SEP-fetch `speech-acts` — cross-references include `implicature` and
`grice`. SEP-fetch `implicature` — back-links `speech-acts`. The *mutual*
cross-reference confirms the relation is real but does not establish a tight
directional dependency — exactly the original's reading: two somewhat-parallel
pragmatics developments rather than a tight prerequisite chain.
RATIONALE: Direction supportable (speech acts supply the "utterances as actions"
frame the maxims regulate), but not the canonical tight dependency. Not a defect.
The SEP mutual link is well-matched to the Defensible verdict.

### E-22 — Intellectual Virtue → Virtue Responsibilism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `virtue-epistemology` — virtue responsibilism has no standalone
slug; it is a strand within virtue epistemology. Analytic warrant: the
constituent concept (intellectual virtue) precedes the position deploying it.
RATIONALE: Virtue responsibilism centers on intellectual virtues as
responsibly-acquired character traits; the constituent concept precedes it.

### E-23 — Art → Historical Theory of Art
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `the-definition-of-art` — the home entry for theories of what
art is (the historical theory, Levinson, is one such theory; no standalone
slug). Analytic warrant: the concept "art" precedes a specific theory of it.
RATIONALE: Concept → theory.

### E-24 — Epistemic Justification → Evidentialism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — evidentialism is the theory that justification is
determined by evidence; the general concept of epistemic justification precedes
a specific theory of it. Corroborated by `the-analysis-of-knowledge`
cross-references (`justep-foundational`, `justep-coherence`, `justep-intext` —
theories of justification, downstream of the general concept).
RATIONALE: Concept → theory.

### E-25 — Composition (Mereological) → Mereological Nihilism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — mereological nihilism is the view that composition
never occurs; the concept of composition precedes the position denying it.
Corroborated by `mereology` cross-references (`nominalism-metaphysics`, `monism`,
`material-constitution` — the cluster of positions about composition).
RATIONALE: Concept → position. Completes the chain mereology →
composition_mereological → mereological_nihilism.

### E-26 — Function (Mathematical) → Expected Value
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — expected value is defined as a function (a weighted
sum/integral over a random variable, itself a function); definitional
prerequisite. The original's sub-observation — that probability is arguably the
*more proximate* prerequisite, making this a candidate Weak-redundant if a
parallel `probability → expected_value` edge exists — is correct and correctly
*not scored* a defect: the rubric only scores Weak-redundant when the
more-proximate edge can be confirmed in the graph, and shard data alone cannot
confirm it.
RATIONALE: A genuine definitional prerequisite; potential weak-redundancy flagged
for the closeout but not scoreable from shard data.

### E-27 — Material Conditional → Curry's Paradox
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `liar-paradox` and `dialetheism` both cross-reference
`curry-paradox` and `logic-substructural` — Curry's paradox is a standalone SEP
topic in the conditional/substructural-logic cluster. Analytic warrant: Curry's
construction is *stated using* the conditional ("if this sentence is true, then
Q") with contraction; the connective precedes the paradox arising from it.
RATIONALE: Framework → puzzle within it.

## Node findings (C2 + C3)

Re-scored adversarially. **All 20 nodes: AGREE with the original verdicts.**
C2: 0 fail. C3: 0 fail — identical to `shard_04.md`.

Per-node confirmations (near-the-line calls noted explicitly):

- **N-1 state_political** — C2 yes / C3 yes (AGREE). Weberian definition is the
  standard intelligible gloss.
- **N-2 beneficence** — C2 yes / C3 yes (AGREE). The contrast with
  non-maleficence is stated explicitly in the summary.
- **N-3 russells_theory_of_descriptions** — C2 yes / C3 yes (AGREE). The actual
  paraphrase ("there is one and only one thing that is F …") grounds it.
- **N-4 easy_problems_of_consciousness** — C2 yes / C3 yes (AGREE). Concrete
  examples + explicit gloss of "easy".
- **N-5 set_mathematical** — C2 yes / C3 yes (AGREE).
- **N-6 biocentrism** — C2 yes / C3 yes (AGREE).
- **N-7 philosophy_of_science** — C2 yes / C3 yes (AGREE).
- **N-8 anti_intentionalism** — C2 yes / C3 yes (AGREE).
- **N-9 qualia_eliminativism** — C2 yes / C3 yes (AGREE). The parenthetical list
  of qualia's conceived features is mildly technical but does not gate the core.
- **N-10 truth_value** — C2 yes / C3 yes (AGREE).
- **N-11 fallibilism** — C2 yes / C3 yes (AGREE — **near the line on C2**). The
  teaching note is the briefest in either shard (2 sentences) but is not a
  restatement and not throat-clearing: it compresses an intuition (certainty is
  rare), a worked angle (the closure puzzle it generates), and a payoff
  (responses reveal broader commitments). Survives, narrowly — consistent with
  the original's own flag for the closeout's short-teaching-note review.
- **N-12 scientific_realism** — C2 yes / C3 yes (AGREE).
- **N-13 explanatory_gap** — C2 yes / C3 yes (AGREE). The concrete pain gloss
  carries the thesis cold.
- **N-14 computational_theory_of_mind** — C2 yes / C3 yes (AGREE).
- **N-15 fictional_truth** — C2 yes / C3 yes (AGREE). The Sherlock Holmes example
  makes the phenomenon immediately graspable.
- **N-16 philosophy_of_mind** — C2 yes / C3 yes (AGREE).
- **N-17 illusionism** — C2 yes / C3 yes (AGREE).
- **N-18 temporal_parts** — C2 yes / C3 yes (AGREE — **near the line on C3**).
  Opens on "the constituents of a perduring four-dimensional object" (jargon) but
  the same sentence rescues it with "analogs of spatial parts, but along the
  temporal dimension" — the "dense-open-then-rescue" shape. Survives an
  adversarial read; consistent with the original's own flag.
- **N-19 moral_epistemology** — C2 yes / C3 yes (AGREE).
- **N-20 indexical** — C2 yes / C3 yes (AGREE). Concrete examples + "deictic"
  glossed inline.

## Shard tally (re-audit)
- Edges: 27 total | Reversed 0 | Weak-redundant 0 | defective 0 (0.0%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 0 (0%) | teaching_notes ABSENT 0
- **Identical to `shard_04.md` on every count.**

## Comparison to the original pass
- **C1: 27/27 verdicts match.** 26 Sound + 1 Defensible (E-21) — all confirmed
  under mandatory anchoring. Zero MISSES, zero FALSE POSITIVES. Where SEP
  cross-reference structure was decisive (E-2, E-6, E-8, E-15, E-18, E-21), it
  *supported* the routine's verdict — in several cases more firmly than the
  routine's own both-ways hedge.
- **C2/C3: 40/40 verdicts match.** Same 0 C2 / 0 C3 failures. Two near-the-line
  passes (N-11 brief teaching note, N-18 jargon-open-then-rescue summary) survive
  an adversarial read — both were already flagged by the original.
- **Net: 67/67 (100%) verdict agreement on shard 04.**

## Cross-cutting observations
- Shard 04 — the *last* of the four completed census shards, scored after any
  cross-session scorer drift would have had time to accumulate — holds up
  **completely** under mandatory SEP anchoring. Its 0.0% C1 defect rate is not a
  glossing artifact: zero edges the routine scored Sound turned out, under
  fortification, to be Reversed or Weak-redundant.
- This is the decisive half of the audit-the-auditor test. Shard 01 (first fire,
  10.7% defect) and shard 04 (fourth fire, 0.0% defect) both survive fortified
  re-audit with 100% verdict agreement. The monotonic decline
  10.7% → 3.6% → 3.6% → 0.0% is therefore **real graph-quality variance across
  randomized shards, not scorer drift** — see the comparison report at
  [`../seed_qa_auditor_check.md`](../seed_qa_auditor_check.md).
- C2/C3 caveat unchanged from `shard_01_reaudit.md`: the 0%-fail rate is
  confirmed by an adversarial same-model pass, but C2/C3 have no external anchor.
  The genuine open question is whether the C2 *bar* discriminates at all on a
  corpus whose teaching_notes are uniformly substantive — a rubric-calibration
  question, not an audit-integrity finding. Carried to the comparison report.
