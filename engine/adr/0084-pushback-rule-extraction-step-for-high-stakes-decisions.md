# ADR 0084 — Pushback rule extension: explicit extraction step for high-stakes decision classes

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0151

## Context

[Issue #77](https://github.com/StarshipSuperjam/paideia/issues/77) (filed at S-0124 from the SWE-hardening audit's cross-check of `addyosmani/agent-skills`) asks whether the `doubt-driven-development` workflow (CLAIM → EXTRACT → DOUBT → RECONCILE) adds value over Paideia's existing posture: the standing pushback rule in [CLAUDE.md](../../CLAUDE.md), the project-wired [/review](../../.claude/skills/review/SKILL.md) skill, [/security-review](../../.claude/skills/security-review/SKILL.md), and the ADR-authoring discipline including the "Alternatives Considered" section per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

The S-0151 audit at [`engine/docs/audits/doubt_driven_evaluation.md`](../docs/audits/doubt_driven_evaluation.md) applies the workflow to four decisions — three historical (ADRs 0049, 0054, 0063) and one in-session upcoming (the [Issue #116](https://github.com/StarshipSuperjam/paideia/issues/116) Phase A1 path proposal) — and surfaces a consistent pattern in the historical failures:

Each of ADR 0054 and ADR 0063 carried a **load-bearing UNVERIFIED premise** that was empirically falsified soon after landing:

- **ADR 0054** asserted at line 137 ("Out of scope") that *"Interactive `/start-engine` sessions don't trigger the gate (user-presence heuristic)"*. Falsified at S-0137; cost = ADR 0076 emergency session + ~400 lines of new wrapper code at S-0138.
- **ADR 0063** asserted that the four functions invoked from `main()`'s "structural phase" were categorically in-memory file/regex. Falsified within ONE session of landing at S-0127 (median ~3700ms structural-phase, dominated by `validate_shared_state_health`'s chromadb subprocess); cost = in-session re-fold adding the health_probe phase.

The audit's diagnosis: the pushback rule is *reactive* ("I see a specific thing you may not be seeing"); the existing posture has no mechanism that forces the AI to *enumerate the premises* the Decision rests on before authoring the Decision. The author themselves didn't see the unverified premise — so there was no specific thing to surface. Doubt-driven workflow's load-bearing value-add over the existing posture is the **EXTRACTION step**: making each load-bearing premise explicit, which surfaces unverified ones for testing at author-time when cheap empirical tests are still on the table.

Wontfix would discard a known-failed posture. A new project-wired skill would add another opt-in invocation surface — empirically weak under the same AI invocation-discipline gap that has left the `/review` and `/security-review` Empirical-record-pending subsections open since S-0134. Extending the standing pushback rule with an explicit extraction-step sub-rule reuses the AI's existing reading-discipline (CLAUDE.md is read every session) and targets the surgical missing piece.

## Decision

[CLAUDE.md](../../CLAUDE.md) Standing rules → Pushback rule section gains a sub-rule: **for decision classes where historical failures cluster, the AI runs an explicit extraction step before authoring the Decision section of an ADR**. The four-step doubt-driven workflow (CLAIM → EXTRACT → DOUBT → RECONCILE) is the procedure; the pushback-rule sub-rule is the trigger.

### Trigger classes (load-bearing)

The extraction step fires for any of:

- **Cross-cutting mechanism authoring** — ADRs whose Consequences would touch ≥5 surfaces per [ADR 0053](0053-mechanism-first-exercise-gate.md) trigger criterion #4 (mechanism-first-exercise gate threshold; reusing it keeps the rule-sets aligned).
- **Supersession ADR** — replacing a load-bearing prior decision (new ADR has a `Supersedes: ADR-XXXX` or "supersedes" relationship; predecessor's Status transitions to Superseded).
- **Posture-to-machinery conversion** — CLAUDE.md "Posture vs machinery" section gains a new entry under "Posture → Machinery" (mechanizing what was previously AI discipline).
- **Contract-shape change** — schema additions to load-bearing structured-archive fields (per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)); target-value adjustments to validator phase budgets (per [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md)); rename or repartition of ADR sequences (per [ADR 0037](0037-engine-product-wall-and-changelog-rename.md)).

The classes are deliberately narrow. Small targeted ADRs (typo fixes, small validator extensions, doc rewrites) do not trigger.

### Procedure

At the bottom of the ADR's Context section, before authoring the Decision section, the AI authors a `### Load-bearing premises` subsection listing:

1. The premises the Decision rests on (one bullet each — extracted from the Decision shape).
2. For each premise: what would falsify it (one sentence).
3. For each premise that can be cheaply tested in-context: the test ran and its result.

If extraction surfaces an unverified premise that can be tested in-context, the test runs before the Decision is authored. If a premise is unverifiable in-context (requires future empirical signal — e.g., depends on the harness behavior of an external system), it is named in the ADR Consequences as a known assumption with a fallback procedure (typically: a first-exercise readiness note per [ADR 0053](0053-mechanism-first-exercise-gate.md), or a Tier-1 closure criterion that the premise will be empirically verified at first natural exercise).

### Relationship to existing surfaces

- **Pushback rule** (CLAUDE.md, this rule's parent): reactive ("specific thing"). Extraction step is the proactive complement.
- **`/review`** (post-authoring code review): reviews staged changes against verified assumptions. Sequential, not redundant.
- **Alternatives Considered** (per ADR 0077, between Decision and Consequences): reviews *which path was chosen and why others were not*. The extraction step is one layer up: *what premises does the chosen path rest on*. Sequential.
- **`/ship` multi-model orchestration** (per [ADR 0081](0081-ship-multi-model-orchestration-skill.md)): pre-merge synthesis of `/review` + `/security-review` + coverage-delta. Same post-authoring surface as `/review`.

## Alternatives Considered

This ADR dogfoods its own extraction step (see Load-bearing premises subsection below) AND the ADR 0077 Alternatives-Considered template.

### New project-wired skill `.claude/skills/doubt-driven/SKILL.md`

- **What:** Author a skill with `disable-model-invocation: true` and documented triggers; the AI invokes it explicitly before authoring a qualifying decision.
- **Pros:** Mirrors the existing `/review` + `/security-review` + `/ship` skill pattern; gives the workflow first-class affordance; allows skill-body refinement over time without CLAUDE.md churn.
- **Cons:** AI invocation discipline is empirically weak — `/review`'s "Empirical record (pending)" subsection has been open since S-0134, suggesting opt-in skills don't reliably fire. A new skill adds vocabulary; the historical failures (0054, 0063) didn't fail for lack of vocabulary — they failed because the author didn't surface the unverified premise. Same root cause, same risk pattern under a new skill.
- **Rejected because:** the audit's evidence is that the *extraction step* is the load-bearing missing piece, not the workflow vocabulary. The pushback rule is read at every session start (CLAUDE.md is auto-loaded); a sub-rule there has tighter reading-discipline than an opt-in skill.

### CLAUDE.md pushback-rule extension *(chosen)*

- **What:** Add an extraction-step sub-rule to the existing pushback rule in CLAUDE.md, with named trigger classes and a procedure for the `### Load-bearing premises` subsection.
- **Pros:** Integrates with the rule the AI already reads at every session start. Reuses the pushback-rule's existing authority. Posture risk shared with the rest of the pushback rule (acknowledged in CLAUDE.md's "Posture vs machinery" section).
- **Cons:** Posture-not-machinery — no mechanical enforcement, only AI discipline. Drift risk: a session may forget extraction on a qualifying decision and no alarm fires.
- **Rejected because:** not rejected — chosen.

### Wontfix close

- **What:** Existing posture (pushback rule + `/review` + ADR 0077 Alternatives Considered + four-eyes user review) is declared sufficient. No new mechanism.
- **Pros:** Minimal change; preserves status quo.
- **Cons:** The audit produces affirmative evidence that the existing posture missed the unverified-premise class historically (ADR 0054 → ADR 0076 emergency; ADR 0063 → S-0127 in-session re-fold). Discarding a known-failed posture without intervention forecloses the cheapest remediation path.
- **Rejected because:** the audit's findings explicitly contradict the wontfix hypothesis. Choosing wontfix against affirmative evidence of failure violates the standing pushback rule's "specific thing" calibration.

### Hard-fail validator gate (machinery, not posture)

- **What:** Mechanize the extraction step as a `validate.py` hard-fail — block commits of new qualifying ADRs that lack a `### Load-bearing premises` subsection in their Context section.
- **Pros:** Eliminates drift risk; treats the rule as machinery, not posture.
- **Cons:** Heuristic detection of "qualifying ADR" is hard — Consequences-surface count requires file parsing across the corpus; Supersession detection requires the ADR's own Status field to be authored before the trigger fires (chicken-and-egg). High false-positive rate for small ADRs that touch ≥5 files for routine reasons (cascade-discipline ADRs, doc updates). Authors would learn to game the heuristic.
- **Rejected because:** the trigger classes resist mechanical detection without producing high false-positive friction on the small-ADR class the rule explicitly excludes. The posture risk is acknowledged and shared with other pushback-rule discipline; mechanization is the wrong tool when the trigger is semantic rather than structural.

## Load-bearing premises

*(Dogfooding the new sub-rule. This ADR is a posture-to-machinery conversion-adjacent decision — it adds posture, not machinery — but the trigger criteria include "cross-cutting" by virtue of the rule affecting all future qualifying ADRs. Authored as worked example for future sessions reading the procedure cold.)*

1. **The historical pattern (ADRs 0054, 0063) generalizes.** Two historical cases is a small sample. *Falsifier:* a corpus-wide audit shows the pattern is exclusive to these two ADRs and other Decisions did not carry comparable unverified premises. *Test status:* the audit's corpus skim (last 30 ADRs) surfaced 0054 and 0063 as the two strongest cases without saturating; ADR 0049 also carried minor doubt-driven gain. The sample is small but the failure cost is concrete (~half a session each). **Premise accepted with the named small-sample risk; sunset criterion in Decision section catches divergence.**
2. **The extraction step adds value the pushback rule does not.** *Falsifier:* the audit's workflow application to ADR 0049 shows the pushback rule could have caught the same premises. *Test status:* ADR 0049's premises were either accepted-with-named-risk in the original ADR (the author DID think them through), or are extensible via mechanism-level improvements (token normalization in `phase:` matching). The unique value-add is on 0054 + 0063 where the author wrote a confident assertion without testing. **Premise accepted.**
3. **AI extraction-step discipline will hold across sessions.** Posture-not-machinery; same risk as the pushback rule itself. *Falsifier:* 3 of 5 qualifying decisions complete with no `### Load-bearing premises` subsection in their Context (i.e., the extraction step was silently skipped). *Test status:* unverifiable in-context; depends on future natural exercise. **Premise accepted with the named drift risk; sunset criterion plus first-exercise observation cover the verification window.**
4. **Trigger classes are well-scoped.** *Falsifier:* future ADRs land that should have triggered but didn't, OR small ADRs trigger spuriously and the friction costs more than the value. *Test status:* unverifiable in-context. **Premise accepted with the named risk; trigger classes are revisable via future ADR amendment if they prove poorly scoped.**

## Consequences

- [CLAUDE.md](../../CLAUDE.md) Standing rules → Pushback rule section grows with the extraction-step sub-rule. The four trigger classes, procedure, and relationship-to-existing-surfaces are documented inline.
- New ADRs authored from S-0151 onward in any of the trigger classes carry a `### Load-bearing premises` subsection at the bottom of their Context section. The four pre-existing ADRs that retrospectively would have triggered (0049, 0054, 0063) are NOT retroactively migrated, per [ADR 0036](0036-expression-contract-for-inward-documents.md) Consequences ("cleanup sweeps that retrofit existing content to a newly-imposed contract... are exempt").
- The [`engine/docs/audits/doubt_driven_evaluation.md`](../docs/audits/doubt_driven_evaluation.md) audit artifact stays as the evidence trail for this decision; future re-evaluations of the rule can reference it cold.
- Sunset criterion: if 5 consecutive qualifying ADRs complete with `### Load-bearing premises` subsections that surface nothing new (i.e., every listed premise is accepted-as-stated, no in-context tests run, no surprises), the rule has converged into implicit discipline and the next audit-cadence health check considers retiring the explicit CLAUDE.md text. The audit-side observation is via the natural ADR inspection that health checks already perform.
- No new validator soft-warn or hook is added — the rule is posture, mechanically inspectable post-hoc via reading the ADRs themselves but not gated at commit. This is deliberate; the "Hard-fail validator gate" alternative is rejected above for false-positive reasons.
- No first-exercise readiness note is authored per [ADR 0053](0053-mechanism-first-exercise-gate.md): this is a posture rule, not a cross-cutting mechanism (no new wrapper around a harness surface; no novel cross-session protocol; trigger criteria #1–#4 do not fire).
- ADR 0049, ADR 0054, ADR 0063 each gain a back-pointer in their See-also section (cascade per [ADR 0041](0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md)) so a future session reading any of them cold encounters the audit-derived analysis.

## See also

- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — sibling discipline; the Alternatives Considered section lives between Decision and Consequences and reviews *which path was chosen*. The extraction step lives at the bottom of Context and reviews *what premises the chosen path rests on*.
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — historical workflow application #1 (modest doubt-driven gain on a well-considered ADR).
- [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — historical workflow application #2 (load-bearing unverified premise at line 137; falsified at S-0137).
- [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — historical workflow application #3 (structural-phase composition assumption falsified at S-0127).
- [ADR 0076](0076-build-mode-lifecycle-push-wrapping.md) — the emergency response to ADR 0054's falsified premise; the concrete cost of the missing extraction step.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — trigger criterion #4 reused as the cross-cutting-mechanism trigger class.
- [`engine/docs/audits/doubt_driven_evaluation.md`](../docs/audits/doubt_driven_evaluation.md) — the audit artifact; four workflow applications + outcome reasoning + sunset criterion.
- [CLAUDE.md](../../CLAUDE.md) Standing rules → Pushback rule — the rule this ADR extends.
- [`/review`](../../.claude/skills/review/SKILL.md), [`/security-review`](../../.claude/skills/security-review/SKILL.md), [`/ship`](../../.claude/skills/ship/SKILL.md) — post-authoring counterparts; sequential, not redundant.
- [Issue #77](https://github.com/StarshipSuperjam/paideia/issues/77) — closes.
