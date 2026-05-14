# ADR 0089 — Skill ↔ Layer-1 procedure-parity validator check

- **Status:** Accepted
- **Date:** 2026-05-14
- **Deciders:** S-0163

## Context

[ADR 0044](0044-skill-conversion-recipe-vs-reference.md) converted three recipe-shaped ops docs to user-defined Skills (a fourth, `routine-mode-lifecycle`, followed at S-0044 per [ADR 0051](0051-routine-mode-and-engine-loop.md)). Each Skill body is the procedural form of its Layer-1 ops doc; the two describe the same procedure in two voices. ADR 0044's Consequences named the resulting failure mode — "Two surfaces per recipe. Drift between them is a new failure mode" — and committed two mitigations: (a) the ops doc is source-of-truth and "updates to the procedure flow doc → Skill, not Skill → doc", and (b) "the next health check audits drift." It also flagged, as a known gap, that "Skills are not validated by `validate.py` ... A future validator extension could add this."

The S-0142→S-0161 window falsified mitigation (a) and exhausted the patience of mitigation (b). Five Issues in that window — [#122](https://github.com/StarshipSuperjam/paideia/issues/122), [#123](https://github.com/StarshipSuperjam/paideia/issues/123), [#124](https://github.com/StarshipSuperjam/paideia/issues/124), [#125](https://github.com/StarshipSuperjam/paideia/issues/125), [#126](https://github.com/StarshipSuperjam/paideia/issues/126) — are the same class: a recipe Skill, an ops doc, or a command body drifting out of sync with its sibling. The drift did not run only doc → skill. [#123](https://github.com/StarshipSuperjam/paideia/issues/123) was command ↔ skill (`start-routine.md` had become a stale 11-step subset of a 16-step procedure); [#125](https://github.com/StarshipSuperjam/paideia/issues/125) was skill ↔ skill (`session-build-lifecycle/SKILL.md` is *missing* a boot step both its command and Layer-1 doc carry). S-0160's own `lesson` drawer named the deeper pattern: *"'the Skill is the canonical form' is an aspiration, not a guarantee; drift can run command→skill too."* The S-0162 cadence health-check audit surfaced the cluster as Non-obvious finding C and filed [Issue #129](https://github.com/StarshipSuperjam/paideia/issues/129): no mechanical check verifies a Skill is in parity with its Layer-1 doc, so the cluster is being fixed one Issue at a time while the generator — unchecked multi-file procedure enumeration — keeps producing.

Issue #129 offered the picking-up session a choice: a validator parity-check, or an ADR 0044 amendment naming the bidirectional drift vector as posture. The user chose the validator check at S-0163. The ADR 0044 amendment lands too — but as a *cascade* of the mechanism, not as the mechanism itself.

The check that lands is deliberately scoped to the *enumeration-drift* subclass: a procedure step present on one side and absent from the other. That subclass covers #123 (stale subset) and #125 (missing step). It does not cover intra-step content drift — #122 (a step's prose mis-described the commit shape) and #126 part 1 (a step omits two required fields) are drift *within* a shared step, which a step-set comparison cannot see and a title comparison cannot see either (skill voice and reference voice legitimately differ in wording per ADR 0044). Intra-step content parity remains hand-discipline, named in the ADR 0044 amendment.

### Load-bearing premises

*(Extraction step per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md): this ADR is a posture-to-machinery conversion — ADR 0044's "kept in sync by hand" posture is partly mechanized — and cross-cutting by Consequences reach.)*

1. **The four recipe Skills and their Layer-1 docs use parallel step numbering**, so comparing step-number *sets* is meaningful. *Falsifier:* a pair where Skill and doc deliberately number the same procedure differently. *Test ran:* the check was run against all four real pairs in this authoring session — `routine-mode-lifecycle` is in exact step-number parity (`{0a, 0b, 0c, 1, 2, 3, 4, 5, 5.5, 5.6, 6, 7, 8, 9, 10, 11}` both sides); the three drifting pairs drift on genuine missing steps (`build-readiness-gate` doc missing step 10, `session-build-lifecycle` `{2b}` vs `{5b}`, `session-shutdown-sequence` doc missing step 0), not on numbering-scheme mismatch. **Premise holds empirically.**
2. **Step numbers, not titles, are the right comparison key.** *Falsifier:* a real drift instance that manifests only as a title-wording change with identical step numbers. *Test ran:* against the #122-#126 cluster — #123 and #125 are enumeration drift (step-set), caught by number comparison; #122 and #126 part 1 are intra-step content drift, caught by *neither* number nor title comparison (and title comparison would add false positives because skill/doc step titles differ by design — e.g. `routine-mode-lifecycle` step 8 is "Eager-claim ritual" in the Skill and "Claim slot" in the doc). Number comparison is the precise key for the enumeration-drift subclass; intra-step drift is explicitly out of scope. **Premise holds.**
3. **The two Layer-1 doc grammars are stably parseable.** Two grammars exist: `### N. Title` headings (`session-shutdown-sequence.md`, `build-readiness-gate.md`) and `N. **Title.**` paragraph-leading numbered lists (`routine-mode-operations.md`, `session-build-lifecycle.md`). *Falsifier:* a doc adopts a third grammar or mixes grammars within one section. *Test ran:* all four docs surveyed and parsed correctly with a per-pair `doc_style` config plus literal `section_end` markers (needed because `routine-mode-operations.md`'s procedure section is followed by a `### Concurrency control` subsection that carries its own decoy `1. 2. 3.` list). If a grammar changes, the check's own "no procedure steps parsed" soft-warn fires — the mechanism self-reports its parsing failure rather than going silent. **Premise holds with the named self-reporting fallback.**
4. **Soft-warn, not hard-fail, is the right severity.** *Falsifier:* drift accumulates because soft-warns are ignored, exactly the way #122-#126 accumulated. *Test status:* unverifiable in-context — depends on whether future sessions act on the warn. **Premise accepted with the named risk**, mitigated by the [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) persistent-warn 3-of-5 escalation surface (a persistently-ignored `skill_layer1_parity_drift` escalates at boot). Hard-fail was rejected because the legitimate-exception surface is non-empty (a Skill may deliberately split or collapse a doc step) and a hard-fail would block unrelated commits on a stale procedure doc.

## Decision

`engine/tools/validate.py` gains a structural-phase soft-warn check, `validate_skill_layer1_parity()`, emitting the category `skill_layer1_parity_drift`.

For each of the four recipe Skill ↔ Layer-1 doc pairs (config in the module-level `_SKILL_LAYER1_PAIRS` tuple), the check:

1. Locates each side's procedure section by a literal start heading, bounded by a literal `section_end` heading (with the next level-2 `## ` heading as a fallback bound).
2. Extracts the *set* of step-number tokens — `\d[\da-z.]*` matching `1`, `0a`, `5.5`, `7b` — from the Skill (always `### N.` heading grammar) and from the doc (per-pair `doc_style`: `### N.` headings or `N. **Title.**` numbered list).
3. Soft-warns once per pair whose step-number sets differ, naming the steps present on one side only.

Missing files, unlocatable sections, and located-but-empty sections each emit their own soft-warn rather than crashing or going silent — a structural change to a procedure doc surfaces as a finding, not as a parser exception.

The check compares step *numbers*, not step *titles* or step *content*. It catches enumeration drift (a step present on one side only); it does not catch intra-step content drift or step-ordering drift. This scope is deliberate (premise 2).

## Trigger-criterion evaluation (per ADR 0053)

`skill_layer1_parity_drift` is evaluated against [ADR 0053](0053-mechanism-first-exercise-gate.md)'s four disjunctive trigger criteria:

- **#1 (new session mode):** does not fire.
- **#2 (new validator soft-warn that depends on session-side discipline):** does not fire. The category is new, but its clearance does not depend on per-session AI discipline — it is a static structural check on committed files (like `cross_reference_broken` or `adr_back_reference_orphan`), cleared by a one-time doc reconciliation, not by a procedural action every session.
- **#3 (new state file the boot procedure reads):** does not fire.
- **#4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files):** **fires** — the Consequences below touch `tools-validate-interpretation.md`, `session-shutdown-sequence.md` (+ its Skill), and `cross-references.md`.

Criterion #4 fires, so the mechanism qualifies as cross-cutting. A separate mechanism-first-exercise gate session is nonetheless **not** warranted, and **no first-exercise readiness note is authored**: the gate exists to catch mechanism bugs before unattended exercise where they cannot be observed, and this mechanism has no deferred or hidden first exercise to gate. It is dogfooded in this authoring session against all four real Skill/doc pairs (it correctly flagged `build-readiness-gate.md`'s missing step 10 — fixed in-context — plus the #125 and pre-#126 drift); it is soft-warn-only, structurally incapable of blocking a commit or mutating state; and its entire behavior surface runs and is observable in every `validate.py` invocation. A first-exercise readiness note would have nothing to verify that this session has not already verified.

## Alternatives Considered

### Validator parity-check *(chosen)*

- **What:** a `validate.py` structural-phase soft-warn comparing each Skill's procedure step-number set against its Layer-1 doc's.
- **Pros:** mechanical — catches future enumeration drift automatically, on every commit and every boot, with no AI discipline required. Matches the project's machinery-over-posture default. The check self-reports its own parsing failures.
- **Cons:** catches only enumeration drift, not intra-step content drift (#122, #126 part 1). Carries a small per-pair config (section headings + doc grammar) that must be updated if a procedure doc is restructured — though a restructure that breaks the config surfaces as an "unlocatable section" soft-warn rather than going silent.
- **Rejected because:** not rejected — chosen by the user at S-0163.

### ADR 0044 amendment only (posture)

- **What:** amend ADR 0044 to name the bidirectional drift vector (skill ↔ skill, command ↔ skill) and commit a same-session parity-check discipline as posture.
- **Pros:** lighter; no new tooling.
- **Cons:** posture is exactly what failed across the #122-#126 window — the "doc → skill only" assumption was itself posture, and it drifted silently across five Issues. Adding more posture against a posture failure repeats the root cause.
- **Rejected because:** the cluster grew *because* there was no mechanism. (The ADR 0044 amendment still lands — but as a present-truth cascade of this mechanism, not as the remediation itself.)

### Step-title or step-content comparison (a richer check)

- **What:** compare normalized step titles, or step body text, not just step numbers.
- **Pros:** would in principle catch intra-step content drift (#122, #126 part 1).
- **Cons:** skill voice and reference voice legitimately differ in wording per ADR 0044 (`routine-mode-lifecycle` step 8 is "Eager-claim ritual" vs "Claim slot") — title comparison would fire constant false positives. Body-text comparison needs semantic similarity, not string equality, to avoid the same noise; that is an LLM-grade judgment, not a structural check.
- **Rejected because:** high false-positive friction with no reliable catch of the intra-step class. Intra-step content parity stays hand-discipline, named in the ADR 0044 amendment.

### Hard-fail instead of soft-warn

- **What:** block any commit while a Skill/doc pair is out of parity.
- **Pros:** zero drift tolerance.
- **Cons:** the legitimate-exception surface is non-empty — a future Skill may deliberately split or collapse a doc step (ADR 0044 itself anticipates the partition shifting). A hard-fail would block *unrelated* commits on a stale procedure doc until someone reconciles it, which is disproportionate.
- **Rejected because:** soft-warn + the ADR 0042 persistent-warn escalation surface gives drift a standing surface without the collateral block.

### Generate the Skill body from the Layer-1 doc

- **What:** the "future enhancement" ADR 0044 mused about — make the Skill body a generated artifact, eliminating drift structurally.
- **Pros:** no drift possible by construction.
- **Cons:** the Skill body is not a *format* transform of the doc — it is a different *voice* (more imperative, terser, restructured for top-to-bottom execution). Generation would either lose that or require a generator sophisticated enough to be its own maintenance burden. Far more invasive than a parity check for the enumeration-drift subclass that actually bit.
- **Rejected because:** disproportionate; the parity check addresses the observed failure class at a fraction of the cost.

## Consequences

- `engine/tools/validate.py` gains `validate_skill_layer1_parity()` (+ helpers `_extract_procedure_section`, `_extract_step_numbers`, the `_SkillDocPair` NamedTuple, and the `_SKILL_LAYER1_PAIRS` config), wired into the structural phase of `main()`. `engine/tools/test_validate_skill_parity.py` carries 15 tests.
- `skill_layer1_parity_drift` joins the soft-warn catalog. It is documented in [`../operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) and added to the canonical `outcome_summary_soft_warns` block in [`../operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) and its Skill.
- [CLAUDE.md](../../CLAUDE.md)'s "Posture vs machinery" section gains a bullet under the mechanized list: Skill ↔ Layer-1 *enumeration* parity is now mechanized; intra-step content parity remains posture.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) gains a present-truth Consequences amendment recording that the "doc → skill only" drift assumption is falsified, that the parity check mechanizes the enumeration-parity slice, and that `routine-mode-lifecycle` is the fourth recipe Skill the check covers.
- [`../operations/cross-references.md`](../operations/cross-references.md) gains entries: ADR 0089 → its consumers; `validate.py` → the four Skill/doc pairs it now reads.
- **Known scope limit (named, not mitigated this session):** intra-step content drift (#122, #126 part 1) is not caught by this check. It remains hand-discipline. If that subclass recurs at audit cadence, a future ADR can revisit — but a structural check is the wrong tool for semantic content parity (see the rejected "step-content comparison" alternative).
- The check fires on `session-build-lifecycle` ([Issue #125](https://github.com/StarshipSuperjam/paideia/issues/125), open, out of S-0163 scope) until #125 lands — this is the mechanism working as intended, not a false positive.

## See also

- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — the recipe-vs-reference partition this check defends; gains a present-truth Consequences amendment from this ADR.
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — added `routine-mode-lifecycle` as the fourth recipe Skill.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the persistent-warn lifecycle `skill_layer1_parity_drift` participates in.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — trigger-criterion evaluation above; criterion #4 fires, gate session not warranted.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — the extraction step dogfooded in the Load-bearing premises subsection.
- [Issue #129](https://github.com/StarshipSuperjam/paideia/issues/129) — closes; the S-0162 health-check finding this ADR resolves.
- [`../operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — `skill_layer1_parity_drift` triage entry.
