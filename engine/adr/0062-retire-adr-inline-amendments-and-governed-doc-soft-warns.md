# ADR 0062 — Retire ADR inline-amendment pattern + governed-doc validator soft-warns

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0126

## Context

[ADR 0036](0036-expression-contract-for-inward-documents.md) committed the project to a four-layer expression contract for governed inward documents: ADRs / `engine/ENGINE_LOG.md` / MemPalace / git carry authorship history, supersession narration, and per-session revision markers. ADR body content is present-truth declarative.

Eight engine ADRs accumulated 14 `### Amendment (S-XXXX)` blocks inside their Consequences sections post-ADR-0036 — body content that narrated *when* and *why* the contract changed rather than stating the current contract directly. The [S-0121 cadence-fired audit](../../docs/health-checks/S-0121.md) surfaced this as Retire-C: the inline-amendment pattern is a journal-shape masquerading as contract; the trace system (ENGINE_LOG entries, `decision`-tagged MemPalace drawers, git blame) already carries the same substance with proper temporal framing.

The same audit flagged three related governed-doc surfaces where similar drift could re-emerge — `engine/STATE.md` (which had been trimmed at S-0121 from 155 rows back to 118 after 37 prior-session prose rows were retired into the archive); `engine/adr/*.md` and `product/adr/*.md` more generally (re-introduction risk after Retire-C lands); `HANDOFF.md` (resolved-section accumulation against the preamble's prune-on-resolve discipline). The audit recommended retire-on-the-current-instance + mechanize-against-re-introduction; user adjudicated ACCEPT (both halves) at S-0125.

## Decision

Three coupled actions at S-0126:

### 1. Retire all 14 inline-amendment blocks across 8 ADRs

The retirements partition by amendment substance:

- **Pure-narration amendments** (delete the block; substance already in trace system): ADR 0042 (1 — S-0101), ADR 0045 (1 — S-0084), ADR 0047 (2 — S-0103, S-0106), ADR 0048 (1 — S-0051), ADR 0054 (1 — S-0072). For these, the amendment substance lives in tool docstrings / ENGINE_LOG / git. Bodies updated only where helpful (e.g., a one-paragraph present-truth pointer replaces the amendment block in ADR 0042).
- **Contract-refinement amendments** (fold into body as present-truth contract; delete the block): ADR 0049 (2 — S-0100, S-0083), ADR 0056 (5 — S-0087, S-0089, S-0090, S-0091, S-0093), ADR 0057 (1 — S-0102). For these, the body is restructured to state the *current* contract. ADR 0049 loses Decision 3 entirely (retired at S-0083), gains Decision 5 (defer-handle field from S-0100); Decisions renumber 1/2/4/5 → 1/2/3/4/5. ADR 0056 gets a major restructure: Layer 1 extended to name boot-search orchestrator + citation scanner (S-0093 substance); new "Scoped surface" subsection naming retired families (S-0087); Layer 3 audit table rewritten as the complete post-S-0091 contract; new subsections for the boot-time substrate probe, pending-diary index, and effectiveness check. ADR 0057's "No code changes to health_check.py" Consequences bullet is rewritten to the post-S-0102 reality (script emits TEMPLATE.md shape via 11 per-section emitters).

`grep -rE "^### Amendment" engine/adr/ product/adr/` returns empty post-retirement.

### 2. Three new validator soft-warns in `engine/tools/validate.py`

All three run in the structural-phase block per [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) (file-only, in-process).

- **`state_md_row_count`** — fires when `engine/STATE.md` exceeds `STATE_MD_ROW_COUNT_THRESHOLD` (default 180; baseline at S-0126 was 118 rows, giving ~50% headroom).
- **`adr_consequences_amendment_header`** — zero-tolerance pattern catch on any `### Amendment` header in any `engine/adr/*.md` or `product/adr/*.md` file. One soft-warn per offending header with `file:line` in the body.
- **`handoff_long_resolved_sections`** — fires under two conditions: (1) total `**Resolved:**` section count exceeds `HANDOFF_RESOLVED_COUNT_THRESHOLD` (default 5); (2) any single resolved section's `S-NNNN` is more than `HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS` (default 10) older than the current session. Per-section age uses the `S-NNNN` parsed from the section's `**Resolved:**` line; pre-S-NNNN-discipline sections that pre-date the resolved-line shape are simply not matched (the regex requires the bold `**Resolved:**` + session-id shape).

All three participate in the standard archive surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md); no schema change (the `soft_warns` dict accepts arbitrary category names). Documented per category in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md).

### 3. First-exercise readiness note per ADR 0053

Authored at [`engine/build_readiness/governed_doc_soft_warns_first_exercise.md`](../build_readiness/governed_doc_soft_warns_first_exercise.md). T1-A closes when the validator surfaces any of the three categories against a real (non-synthetic) candidate. T1-B closes when the surfaced soft-warn motivates a corrective edit (not silenced via threshold bump without evidence).

## Consequences

- Three new soft-warn categories land in the standard archive surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md); no schema change.
- The cadence-fired audit per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) is relieved of mechanical detection of amendment-pattern drift — the gate catches the pattern at commit time. Audits remain responsible for the judgment work (which patterns to retire; what affirmative case preserves an artifact).
- The 8 ADR rewrites at S-0126 are the substantive present-truth pass; future ADRs author against the prohibition from day one. The validator's zero-tolerance pattern catch is the backstop.
- The contract refinement in ADR 0049 (Decision 6 added at S-0100; Decision 3 retired at S-0083) and ADR 0056 (5 amendments compounding the substrate-availability + boot-search + citation-telemetry surfaces) are no longer second-class citizens at the bottom of their Consequences sections — they're the current contract, read as such.
- `engine/STATE.md` was trimmed at S-0121 (37 prior-session rows retired); current 118 rows is the post-trim state. The `state_md_row_count` threshold at 180 is preventative; if STATE.md grows for legitimate reasons (new audit-tracking subsections, SWE-hardening rollout additions), bump the threshold with evidence rather than silencing the warn.
- HANDOFF.md was pruned at S-0121 (8 resolved sections retired, content preserved in git history per the prune-on-resolve discipline). Current state is zero open + zero resolved sections; the `handoff_long_resolved_sections` thresholds (5 count / 10 sessions age) reflect the prune-on-resolve cadence the file's preamble commits to.
- The `adr_consequences_amendment_header` pattern catch is zero-tolerance — any future ADR author tempted to add an amendment block sees the soft-warn at first-commit. If the discipline needs a refresh, the soft-warn surfaces the violation, not the next cadence audit.

## See also

- [ADR 0036](0036-expression-contract-for-inward-documents.md) — the expression contract this ADR mechanizes for governed-doc surfaces.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; the three new categories participate in the standard surface.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — HANDOFF.md narrowing discipline that the `handoff_long_resolved_sections` soft-warn enforces at gate time.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this ADR triggers a readiness note covering all three categories.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — adversarial-stance audit posture; the audit surfaced this work at S-0121 and is relieved of the mechanical detection burden by the new soft-warns.
- [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — sibling validator-instrumentation ADR landed in the same session.
- [Issue #87](https://github.com/StarshipSuperjam/paideia/issues/87) — closes.
- `docs/health-checks/S-0121.md` — audit source (Retire-C + recommended soft-warns).
- [`engine/build_readiness/governed_doc_soft_warns_first_exercise.md`](../build_readiness/governed_doc_soft_warns_first_exercise.md) — first-exercise readiness.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — per-category soft-warn documentation.
