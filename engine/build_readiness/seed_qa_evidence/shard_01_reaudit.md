# Seed-graph QA census — fortified re-audit of shard 01

> Authored by S-0165 (interactive build session) per the approved plan at
> `~/.claude/plans/four-routine-sessions-have-eventual-parnas.md` ("Audit the
> auditor"). This is **not** a routine census evidence file — it is a
> methodology check that re-scores shard 01 with **mandatory** anchoring to test
> whether the original parametric-first pass ([`shard_01.md`](shard_01.md),
> S-0158) was glossing.
>
> **Method difference from the routine pass.** The routine rubric
> ([`seed_qa_audit.md`](../seed_qa_audit.md)) makes SEP fetching *optional*
> ("reserved for genuinely-uncertain verdicts"). This re-audit removes that
> discretion: every C1 edge verdict carries an `ANCHOR:` line that is *either* a
> SEP structural fetch (via [`fetch_structural_reference.py`](../../tools/fetch_structural_reference.py)
> per [ADR 0059](../../adr/0059-audit-time-structural-reference-fetching.md))
> *or* an explicit written analytic warrant where direction is forced by
> definitional containment. No bare parametric "Sound" is permitted. C2/C3 are
> re-scored adversarially (actively trying to fail each summary/teaching-note);
> C2/C3 have no external anchor per the rubric, so that pass is a same-model
> second read, weaker evidence than the C1-with-SEP comparison.
>
> SEP briefs are anonymized structural skeletons (titles + forward
> cross-references + word counts + section path), fetched once into `/tmp/sep/`
> for this session. The fortification check follows the S-0122 production-audit
> method: does the source concept's cross-reference structure support the
> claimed prerequisite direction, and does the target back-link the source
> (a reversal signal)?

## Shard metadata
- Shard: 01 (re-audit)
- Original evidence: `shard_01.md` (S-0158, 2026-05-14)
- Edges scored: 28
- Nodes scored: 20
- Re-scored: 2026-05-14 (S-0165)
- SEP fetches consumed: 24 distinct entries (2 slugs 404'd — `phenomenal-concepts`,
  `science-underdetermination`; affected edges fall back to analytic warrant +
  adjacent-entry anchoring, noted inline)

## Edge findings (C1)

### E-1 — Knowledge → Epistemic Closure
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `closure-epistemic` — its cross-references include
`knowledge-analysis`; section path "1. Knowledge Closure". The closure entry is
framed *in terms of* knowledge. Mutual link with `knowledge-analysis`, but
knowledge is the general concept and closure is a principle about it.
RATIONALE: Epistemic closure is a principle about knowledge (closure under known
entailment); the general concept is genuinely prior.

### E-2 — Qualia Functionalism → Inverted Spectrum
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `inverted-qualia` — its cross-references include
`functionalism`. The inverted-spectrum entry forward-links functionalism,
consistent with the inverted spectrum being a standard *objection to*
functionalism; understanding the functionalist target is prerequisite.
RATIONALE: The inverted-spectrum scenario earns its force as an objection to
qualia functionalism; the functionalist position is the genuine prerequisite.

### E-3 — Probability (Mathematical) → Conditional Probability
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — conditional probability is *defined* as
P(A|B) = P(A∩B)/P(B), constructed directly from the probability measure.
Definitional containment; the relation is mathematical, not interpretive.
RATIONALE: The base concept is strictly prior; conditional probability is built
from it.

### E-4 — Bioethics → Reproductive Ethics
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `theory-bioethics` (6 cross-references, all theory-internal —
no topic map, so no forward link to reproductive ethics specifically) + analytic
warrant: reproductive ethics is uncontroversially a subfield of bioethics
(field → subfield containment).
RATIONALE: The general field framing is the natural pedagogical entry before its
specialized branch.

### E-5 — Phenomenal Concept Strategy → Type-B Materialism
VERDICT: Reversed  (original: Reversed — AGREE)
ANCHOR: `phenomenal-concepts` 404'd (no standalone SEP entry — itself a weak
signal that the phenomenal concept strategy is downstream specialized
machinery). SEP-fetch `physicalism` (24 cross-references) is the major entry for
the family type-B materialism sits in; nothing in its structure makes the
phenomenal concept strategy prior. Analytic warrant: a defensive strategy
presupposes the position it defends.
RATIONALE: The phenomenal concept strategy is the explanatory machinery deployed
*in defense of* type-B materialism; type-B materialism is the prerequisite, not
the reverse. The edge runs the dependency backwards. **Original verdict
confirmed under fortification.**

### E-6 — Quantifier → Predicate Logic
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `quantifiers-and-quantification` — cross-references include
`logic-classical` (predicate logic is classical first-order logic). Quantifiers
are the defining apparatus distinguishing predicate logic from propositional
logic.
RATIONALE: Understanding quantifiers (∀, ∃) is genuinely prior to the system
built on them.

### E-7 — Property → Tropes
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `properties` — its cross-references include `tropes` (forward
link present). SEP-fetch `tropes` — section path "1. Historical Background",
back-links `properties`. Trope theory is a theory *of* properties; the general
concept is prerequisite.
RATIONALE: The general concept of a property is the genuine prerequisite of the
trope-theoretic account.

### E-8 — Qualia → Qualia Eliminativism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — eliminativism *about qualia* is named for what it
denies; the concept being eliminated is definitionally prior. Corroborated by
the `qualia` SEP entry (smoke-test fetch): its cross-references carry no
"eliminativism" slug, consistent with eliminativism being a downstream position.
RATIONALE: The concept being eliminated must come before the position that
eliminates it.

### E-9 — Perception → Representationalism (Perception)
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `perception-problem` — cross-references include
`consciousness-representational`. SEP-fetch `consciousness-representational` —
does NOT back-link `perception-problem`. Forward link present, no reversal
signal: the phenomenon is prior to the theory of it.
RATIONALE: Representationalism is a theory of perception; the phenomenon precedes
the theory.

### E-10 — Inference Rule → Propositional Logic
VERDICT: Defensible  (original: Defensible — AGREE)
ANCHOR: analytic warrant — `inference_rule` has no standalone SEP entry; the
canonical curricular ordering introduces inference rules *within* propositional
logic, not before it. But the seed's service tier deliberately abstracts a
truth-preserving inference-rule concept applicable before any specific logic is
chosen. Supportable on that reading; not canonical.
RATIONALE: Not the canonical ordering, but supportable on the service-tier
reading. Not a defect.

### E-11 — Philosophy of Science → Scientific Explanation
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — `philosophy_of_science` is a top-level discipline
label sourcing a foundation-spine edge to a central topic. Per the S-0122
production audit's granularity finding #3, this "discipline-as-umbrella" pattern
is *accepted* (retain with discipline-as-umbrella semantics), not a defect.
RATIONALE: The field framing is the natural pedagogical entry point before its
core topics. Sub-observation: discipline-label-as-source — accepted pattern, not
scored a defect.

### E-12 — Inference Rule → Modus Ponens
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — modus ponens *is* an inference rule; genus → species,
definitional containment.
RATIONALE: The general concept precedes the specific instance.

### E-13 — Motivational Internalism → Expressivism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `moral-motivation` — cross-references span the
`moral-cognitivism` / `moral-anti-realism` cluster that expressivism sits in
(no standalone "expressivism" slug). The expressivist argument standardly runs
*through* motivational internalism (judgments motivate; beliefs don't; so
judgments aren't beliefs). Near the Sound/Defensible line — expressivism can be
introduced without naming internalism — but internalism is the canonical
motivating premise.
RATIONALE: Motivational internalism is a genuine foothold for the expressivist
argument.

### E-14 — Evidence → Bayesian Confirmation Theory
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `evidence` — only 2 cross-references, and *both* are
`epistemology-bayesian` and `confirmation` — i.e. the evidence entry forward-links
exactly the target cluster. Strong corroboration.
RATIONALE: Bayesian confirmation theory formalizes how evidence confirms
hypotheses; the concept of evidence is prior.

### E-15 — Liberty (Political) → Natural Rights
VERDICT: Defensible  (original: Defensible — AGREE)
ANCHOR: SEP-fetch `positive-and-negative-liberty` — cross-references include
`rights` and `rights-human` (forward link present). SEP-fetch `rights` — does
NOT back-link liberty; it links `natural-law-theories` and `locke`. The forward
link is necessary-not-sufficient (per the production audit's own caveat); the
competing reading — natural-rights theory as the foundational apparatus from
which liberty is derived — remains live.
RATIONALE: Arguable in both directions; supportable that intuitive political
liberty is the experiential entry point. Borderline; not a defect.

### E-16 — Hard Problem of Consciousness → Philosophical Zombie
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `consciousness` (the hard problem's home entry) —
cross-references include `zombies`. SEP-fetch `zombies` — back-links
`consciousness`. Mutual; the zombie thought experiment is a tool deployed within
the hard-problem discourse.
RATIONALE: The hard-problem framing makes the zombie's significance legible.

### E-17 — Liar Paradox → Dialetheism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `liar-paradox` — cross-references include `dialetheism`
(forward link present). SEP-fetch `dialetheism` — back-links `liar-paradox`.
Dialetheism is motivated principally by the liar.
RATIONALE: The paradox is the genuine prerequisite of the dialetheist response.

### E-18 — Belief → Epistemic Justification
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `belief` — a 41-cross-reference hub entry (consistent with
belief being a foundational upstream concept). No standalone "epistemic
justification" SEP slug; analytic warrant: epistemic justification is
justification *of belief* — the concept of belief is definitionally prior.
RATIONALE: The concept of belief is prior to the justification of belief.

### E-19 — Falsificationism → Paradigm (Kuhnian)
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `karl-popper` — cross-references include `thomas-kuhn`.
SEP-fetch `thomas-kuhn` — back-links `popper`. Popper (LScD 1959) genuinely
precedes Kuhn (1962); Kuhn's paradigm concept is standardly taught as a response
to falsificationism. This is the *correct* developmental order — distinct from
the developmental-arc *reversal* shape the production audit flagged (SCI-E-4,
where the historical seed was placed after the framework that subsumed it).
RATIONALE: Popper-before-Kuhn is the canonical historical and pedagogical
ordering.

### E-20 — Existence → Modality
VERDICT: Defensible  (original: Defensible — AGREE)
ANCHOR: SEP-fetch `existence` — cross-references include `possibilism-actualism`
(a modal-metaphysics topic), giving weak forward support, but no general
"modality" entry is linked. Existence and modality are genuinely co-foundational
metaphysical concepts; the ordering is supportable but not uniquely canonical.
RATIONALE: Both foundational; the ordering is supportable. Not a defect.

### E-21 — Universals → Realism about Universals
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — realism *about universals* is a position on the
existence of universals; the concept must precede the position about it.
Corroborated by `properties` (universals' close kin): it links `platonism` and
`nominalism-metaphysics` as downstream positions about universals/properties.
RATIONALE: The concept must precede the position about it.

### E-22 — Intentionality → Representational Theory of Mind
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `mental-representation` (the RTM entry) — its cross-references
*include* `intentionality`. The target back-links the source: RTM presupposes
intentionality. SEP-fetch `intentionality` — does not forward-link
mental-representation, consistent with intentionality being the upstream
phenomenon.
RATIONALE: The representational theory of mind is an account *of* intentionality;
the phenomenon is prior to the theory.

### E-23 — Property → Property Dualism
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — property dualism is the thesis that mental and
physical properties are distinct kinds; it presupposes the general concept of a
property. Corroborated by `properties` being a 45-cross-reference hub entry
(clearly foundational/upstream).
RATIONALE: The general concept of a property is the genuine prerequisite.

### E-24 — Set (Mathematical) → Axiom (Mathematical)
VERDICT: Reversed  (original: Reversed — AGREE)
ANCHOR: SEP-fetch `set-theory` — only 4 cross-references, *all* set-theory-internal
(`settheory-early`, `large-cardinals-determinacy`, `continuum-hypothesis`,
`independence-large-cardinals`). Nothing links "axiom" as a concept set theory
grounds. Analytic warrant: a mathematical axiom is a general concept of formal
systems; axioms of geometry and arithmetic predate and are independent of set
theory. If anything axiomatic set theory presupposes the notion of an axiom.
RATIONALE: The edge asserts a prerequisite relation that is at best backwards or
orthogonal. **Original verdict confirmed under fortification** — the SEP
cross-reference structure corroborates: set theory's entry is inward-facing, not
a grounding source for the axiom concept.

### E-25 — Meaning (Linguistic) → Linguistic Relativity
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: analytic warrant — linguistic relativity (Sapir-Whorf) is a thesis about
how linguistic *meaning* shapes thought; the concept of meaning is stated in the
thesis and is definitionally prior. Corroborated by SEP structure: `meaning`
appears as an upstream node in the cross-reference sets of `speech-acts` and
`implicature` (the pragmatics entries), confirming meaning is a language-domain
hub concept.
RATIONALE: The concept of linguistic meaning is genuinely prior to a thesis about
its effects on thought.

### E-26 — Knowledge-How → Knowledge
VERDICT: Reversed  (original: Reversed — AGREE)
ANCHOR: SEP-fetch `knowledge-how` — its cross-references include
`knowledge-analysis` (and `knowledg`). SEP-fetch `knowledge-analysis` — does NOT
back-link `knowledge-how`. The cross-reference structure shows knowledge-how
*depending on* the general analysis of knowledge, not the reverse. The edge as
authored (Knowledge-How → Knowledge) claims knowledge-how is prerequisite to
knowledge — backwards.
RATIONALE: "Knowledge" is the general concept; "Knowledge-How" is the specialized
species (Ryle's knowledge-how vs knowledge-that). **Original verdict confirmed
under fortification** — the SEP cross-reference structure directly corroborates
the reversal: knowledge-how's entry links knowledge-analysis forward, not vice
versa.

### E-27 — Duhem-Quine Thesis → Theory-Ladenness of Observation
VERDICT: Defensible  (original: Defensible — AGREE)
ANCHOR: `science-underdetermination` 404'd (correct slug `scientific-underdetermination`,
not retried). SEP-fetch `science-theory-observation` (the theory-ladenness entry)
— cross-references include `duhem` (the figure behind Duhem-Quine), giving weak
forward support but not establishing a strict prerequisite. The two are distinct
theses, each largely graspable independently.
RATIONALE: Supportable that Duhem-Quine holism is groundwork that motivates
theory-ladenness, but not a strict prerequisite. Borderline; not a defect.

### E-28 — Perception → Direct Realism (Perception)
VERDICT: Sound  (original: Sound — AGREE)
ANCHOR: SEP-fetch `perception-problem` — direct realism has no standalone slug
(discussed within the perception entry, alongside `sense-data`,
`perception-disjunctive`, `idealism` — i.e. as one position among theories of
perception). Analytic warrant: the phenomenon is prior to a theory of it.
RATIONALE: Direct realism is a theory of perception; the phenomenon precedes the
theory.

## Node findings (C2 + C3)

Re-scored adversarially. **All 20 nodes: AGREE with the original verdicts.**
C2: 0 fail. C3: 2 fail (N-4, N-13) — identical to `shard_01.md`.

Per-node confirmations (deviations and near-the-line calls noted explicitly):

- **N-1 verificationism** — C2 yes / C3 yes (AGREE). "non-analytic" appears in
  the opening parenthetical but does not gate the core idea (meaning = method of
  empirical verification).
- **N-2 justice_as_fairness** — C2 yes / C3 yes (AGREE). "lexical priority"
  recurs undefined but qualifies the principles rather than gating them.
- **N-3 phenomenology** — C2 yes / C3 yes (AGREE). "epoché" parenthetical;
  "bracketing questions of metaphysical reality" carries the method's gist.
  (Granularity — phenomenology as a movement — is a separate axis the rubric
  does not score under C2/C3.)
- **N-4 curry_paradox** — C2 yes / **C3 no** (AGREE — confirmed FAIL).
  Jargon-gated: "deduction theorem" and "contraction" are load-bearing,
  undefined; the central mechanism sentence is unparseable cold.
- **N-5 paradox_of_the_ravens** — C2 yes / C3 yes (AGREE). The white-shoe example
  grounds the equivalence machinery.
- **N-6 consequentialism** — C2 yes / C3 yes (AGREE).
- **N-7 expertise** — C2 yes / C3 yes (AGREE). Teaching note is brief but the
  five-sources checklist is a genuine applicable foothold.
- **N-8 moral_realism** — C2 yes / C3 yes (AGREE). "sui generis" appears
  unglossed in a non-load-bearing parenthetical; core claim stays plain.
- **N-9 categorical_imperative** — C2 yes / C3 yes (AGREE).
- **N-10 relevant_alternatives_theory** — C2 yes / C3 yes (AGREE).
- **N-11 theory_ladenness_of_observation** — C2 yes / C3 yes (AGREE).
- **N-12 modal_realism** — C2 yes / C3 yes (AGREE).
- **N-13 aesthetic_experience** — C2 yes / **C3 no** (AGREE — confirmed FAIL).
  Circular / assumes-the-concept: "aesthetic experience" is defined via
  "aesthetic objects" and "aesthetic properties," the latter left undefined.
- **N-14 probability_mathematical** — C2 yes / C3 yes (AGREE — **near the line**).
  "measure-theoretic primitive" opens with jargon but is immediately rescued by
  a concrete restatement ("a function P that assigns to each event ... a real
  number in [0,1]") plus three plainly-stated axioms. Survives, narrowly.
- **N-15 art_criticism** — C2 yes / C3 yes (AGREE).
- **N-16 foundationalism** — C2 yes / C3 yes (AGREE).
- **N-17 eternalism** — C2 yes / C3 yes (AGREE — **near the line**). "B-theoretic"
  is undefined in the opening clause but is immediately restated in plain terms
  ("all times ... are equally real"). Survives, narrowly.
- **N-18 virtue_ethics** — C2 yes / C3 yes (AGREE).
- **N-19 propositional_attitude** — C2 yes / C3 yes (AGREE).
- **N-20 intellectual_virtue** — C2 yes / C3 yes (AGREE).

## Shard tally (re-audit)
- Edges: 28 total | Reversed 3 | Weak-redundant 0 | defective 3 (10.7%)
- Nodes: 20 total | C2 fail 0 (0%) | C3 fail 2 (10.0%) | teaching_notes ABSENT 0
- **Identical to `shard_01.md` on every count.**

## Comparison to the original pass
- **C1: 28/28 verdicts match.** 3 Reversed (E-5, E-24, E-26), 4 Defensible
  (E-10, E-15, E-20, E-27), 21 Sound — all confirmed under mandatory anchoring.
  Zero MISSES (no edge the original scored Sound that the re-audit found
  defective). Zero FALSE POSITIVES (no edge the original flagged that the
  re-audit cleared). The three reversals were not only confirmed but *strengthened*
  — for E-26 and E-24 the SEP cross-reference structure directly corroborates the
  reversal, which the original pass reached parametrically.
- **C2/C3: 40/40 verdicts match.** Same 2 C3 failures (N-4, N-13). Two passes
  (N-14, N-17) sit close to the C3 line on the "dense-open-then-rescue" shape but
  survive an adversarial read — they are not misses.
- **Net: 68/68 (100%) verdict agreement on shard 01.**

## Cross-cutting observations
- The shard 01 routine pass — the *first* routine fire of the census, before any
  possibility of cross-session scorer drift — holds up completely under mandatory
  SEP anchoring. Its 10.7% C1 defect rate was accurate, not a glossing artifact.
- The fortification *upgraded confidence* on the three reversals rather than
  overturning anything: the SEP cross-reference structure independently
  corroborates E-24 and E-26, which S-0158 reached by parametric reasoning alone.
- This establishes the **baseline-calibration** half of the audit-the-auditor
  test: at its most careful, the parametric-first method did not miss defects on
  this shard. Whether that rigor *held* across later shards is the
  drift question — see the shard 04 re-audit (`shard_04_reaudit.md`) and the
  comparison report (`../seed_qa_auditor_check.md`).
