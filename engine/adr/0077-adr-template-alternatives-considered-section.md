# ADR 0077 — ADR template gains "Alternatives Considered" section; Deprecated ADRs join the back-reference orphan check

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0139

## Context

[Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81) was filed at S-0124 from a cross-check of `addyosmani/agent-skills`'s `documentation-and-adrs` skill against Paideia's existing ADR practice. The Issue named three structural patterns from the skill as additive to Paideia: (1) an "Alternatives Considered" section, (2) a PROPOSED lifecycle state, (3) a DEPRECATED-vs-SUPERSEDED distinction.

Reading [`engine/operations/adr-authoring.md`](../operations/adr-authoring.md) at S-0139 boot shows the lifecycle-state half of the Issue is already in place: the Status template at line 12 already lists `Proposed | Accepted | Deprecated | Superseded by ADR NNNN`, and the Status conventions section documents all four states with the DEPRECATED-vs-SUPERSEDED distinction. The Issue body was authored against a stale picture of the doc.

What remains is the structural pattern — Alternatives Considered as a uniform template section rather than ad-hoc prose. Four existing ADRs ([ADR 0051](0051-routine-mode-and-engine-loop.md), [ADR 0056](0056-mempalace-mechanical-adoption-checks.md), [ADR 0060](0060-routine-wedge-detect-and-pause.md), [product/ADR 0061](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md)) use "Alternatives Considered" or "Alternatives considered" sections informally, with inconsistent capitalization and varying internal structure (some use prose paragraphs, some use partial bullet lists). The template change names the canonical form going forward without retroactively churning the four existing ADRs.

A secondary observation from the lifecycle-states half: today there are zero Deprecated ADRs in the corpus (all retired ADRs are Superseded-by-NNNN). The DEPRECATED state is documented but not yet exercised. When the first ADR transitions to Deprecated, it should — like Accepted ADRs — be cited by something downstream (a successor decision, an ops doc, a notes-and-lessons section). The existing `validate_adr_back_reference_orphan` check in `validate.py` filters to `Accepted` only; extending it to also cover `Deprecated` closes the gap before it manifests.

## Decision

Two coupled changes land at S-0139.

### 1. Add "Alternatives Considered" as a standard section in the Nygard template

The section lives between Decision and Consequences. Per-alternative pattern:

```markdown
### <alternative name>

- **What:** brief description of the alternative.
- **Pros:** ...
- **Cons:** ...
- **Rejected because:** the deciding reason.
```

Section name **"Alternatives Considered"** (title-case) is canonical. The four existing ADRs that use lowercase "considered" or other forms remain valid; new ADRs should match the canonical form.

The section is **optional but encouraged** — author it when rejected paths are non-obvious or future sessions might re-litigate; omit for small targeted ADRs where the chosen path was obviously correct. Prose-form alternatives discussions remain valid where they read better than the structured pattern; the structured pattern's value is comparability (Pros / Cons / Rejected because for each alternative) rather than a strict formatting requirement.

### 2. Extend `validate_adr_back_reference_orphan` to cover Deprecated ADRs

The check at [`engine/tools/validate.py:1314`](../tools/validate.py:1314) previously filtered Status to `Accepted` only. The S-0139 change extends the regex to `(Accepted|Deprecated)`. The rest of the check is unchanged — citation search, `Orphan-OK` escape annotation, soft-warn emit semantics. The local binding is renamed from `accepted_status` to `eligible_status` for clarity.

Backward compatible: zero Deprecated ADRs exist in the corpus today, so the check produces zero new findings on land. It will fire only when a future ADR is authored or amended to Status `Deprecated` without being cited from at least one non-ADR markdown file.

## Alternatives Considered

This ADR dogfoods the new section.

### Author the Alternatives Considered section as a strict requirement for all new ADRs

- **What:** Make the section mandatory; soft-warn (or hard-fail) on its absence in any new ADR.
- **Pros:** Forces deliberate consideration of alternatives at authoring time; eliminates the "I forgot to write it down" failure mode.
- **Cons:** Adds friction to small targeted ADRs where the chosen path was obviously correct and there really were no meaningful alternatives. Encourages performative authoring ("Alternative: do nothing") that crowds the ADR with noise.
- **Rejected because:** the cost of false-positive friction on small ADRs exceeds the benefit of catching the rare case where alternatives were genuinely overlooked. The encouraged-not-required posture preserves authorial judgment without removing the prompt.

### Retroactively migrate the four existing informal Alternatives sections to the canonical form

- **What:** Rewrite [ADR 0051](0051-routine-mode-and-engine-loop.md), [ADR 0056](0056-mempalace-mechanical-adoption-checks.md), [ADR 0060](0060-routine-wedge-detect-and-pause.md), [product/ADR 0061](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md) to use the canonical structured pattern with title-case section name.
- **Pros:** Uniform style across the corpus from S-0139 onward; easier scanning for readers.
- **Cons:** Retrofit cost on prose that already reads clearly; no behavior change; risks introducing subtle interpretation drift when reshaping existing prose into Pros / Cons / Rejected because buckets.
- **Rejected because:** per [ADR 0036](0036-expression-contract-for-inward-documents.md) Consequences ("cleanup sweeps that retrofit existing content to a newly-imposed contract... are exempt and belong in the new contract's own Consequences section"). The canonical form applies to new ADRs from 0077 onward; the four pre-existing ADRs stay as they are.

### Make the back-reference orphan check also cover Superseded ADRs

- **What:** Extend the eligible-status regex to `(Accepted|Deprecated|Superseded)`.
- **Pros:** Superseded ADRs that no longer have inbound citations are arguably also orphaned in the same sense — a decision-record that nothing downstream references.
- **Cons:** Superseded ADRs are deliberately kept for historical reasoning; many will never have outbound citations after the superseding ADR replaces them in active doc references. The existing `validate_superseded_adr_currency` check already handles the related concern (docs citing a Superseded ADR without a historical marker). Adding Superseded to the orphan check would produce a high false-positive rate.
- **Rejected because:** semantic mismatch — Superseded means "intentionally retired in favor of a named successor"; the successor carries the load-bearing role. The Deprecated case is different: no successor exists; the decision-record stands on its own and should be referenced by something downstream to avoid silent rot.

### Defer the Deprecated-coverage extension until the first Deprecated ADR is authored

- **What:** Land only the template change at S-0139; defer the `validate.py` extension to a future session when the first Deprecated ADR is on the horizon.
- **Pros:** Smaller scope at S-0139; the extension is verified against a real Deprecated ADR rather than a hypothetical one.
- **Cons:** Per `feedback_no_pilot_wait_and_see.md`: deferral-without-mechanism is silent indefinite deferral. The extension is one regex change with two new tests; landing it now costs essentially nothing and removes the future-session burden.
- **Rejected because:** standing memory rules out the deferral framing. The mechanism lands in the same session as the contract.

## Consequences

- New ADRs from 0077 onward use the canonical "Alternatives Considered" section pattern where applicable. The four pre-existing informal uses (ADRs 0051, 0056, 0060, product/0061) remain valid; no retroactive migration.
- The Nygard template in [`engine/operations/adr-authoring.md`](../operations/adr-authoring.md) gains the section between Decision and Consequences with optionality + canonical pattern + back-reference to the four pre-existing prose-form uses.
- `validate_adr_back_reference_orphan` at [`engine/tools/validate.py:1314`](../tools/validate.py:1314) extends to cover Deprecated ADRs. Two new pytests under `TestAdrBackReferenceOrphan` (`test_uncited_deprecated_adr_warns`, `test_cited_deprecated_adr_does_not_warn`). All 6 orphan-check tests green at land.
- Issue #81's lifecycle-state half (PROPOSED state + DEPRECATED label) is already in place pre-S-0139; this ADR records that observation so future sessions reading the Issue cold understand the closure path. The Issue closes at S-0139 shutdown.
- No first-exercise readiness note required per [ADR 0053](0053-mechanism-first-exercise-gate.md): this is a template change + small validator extension, not a cross-cutting mechanism (single ops doc + one regex change + ADR + ENGINE_LOG row; no wrapper around a harness gate; no novel cross-session protocol; trigger criteria do not fire).

## See also

- [Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81) — original analysis-outcome from `addyosmani/agent-skills` cross-check; closes at S-0139.
- [`engine/operations/adr-authoring.md`](../operations/adr-authoring.md) — Layer 1 source-of-truth for ADR authoring.
- [`engine/tools/validate.py:1314`](../tools/validate.py:1314) — `validate_adr_back_reference_orphan`, extended at S-0139.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — Consequences clause exempting retroactive migration sweeps; load-bearing for the rejection of "retroactively migrate four existing sections" alternative.
- [ADR 0041](0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md) — original framing of the back-reference orphan check.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — trigger criteria for first-exercise readiness notes (evaluated and not triggered for S-0139).
