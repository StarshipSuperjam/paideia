# engine/build_readiness/

> Reports about engine readiness — gating substantive work, recording its outcome, or capturing first-exercise observations of new mechanisms. Six file classes coexist here, each with a distinct authoring trigger, governing ADR, and downstream consumer. Issue [#26](https://github.com/StarshipSuperjam/paideia/issues/26) flagged the original single-class README that only indexed gate reports; this document now indexes all six classes per their actual contracts.

## File classes

Each class below names: when it gets authored, the contract that governs it, and what (if anything) consumes it.

### 1. Gate reports — pre-build adversarial reconnaissance

**Authoring trigger:** before a substantive build session opens, per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md).

**Contract:** the gate session probes the build plan adversarially — looking for what's broken / underspecified / wrong, not what looks fine. Tier 1 (must-resolve) / Tier 2 (decide-in-build) / Tier 3 (defer) triage. Report sits at `<phase>_<chunk>.md`.

**Consumer:** the build session that follows reads the report at boot; halts if Tier 1 contains unresolved items.

**Authoring procedure:** [`../operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) "Build-readiness report template".

| Report | Gate session | Build session | Status |
|---|---|---|---|
| [`phase_3_sql.md`](phase_3_sql.md) | S-0027 | S-0028 | Build session closed |
| [`phase_4_graph_validation.md`](phase_4_graph_validation.md) | S-0034 | S-0037 | Build session closed |
| [`phase_5.md`](phase_5.md) | S-0045 (master plan) | Routine-mode (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md)) — 16 explicit tasks per [`engine/session/auto_target.json`](../session/auto_target.json) | Routine block executed S-0050 → S-0076; phase closed |

### 2. Audit-warrant gate reports — pre-audit go/no-go decision

**Authoring trigger:** before a multi-session production audit is committed to, per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) extended at S-0081 to cover the audit-warrant case.

**Contract:** structurally parallels the standard build-readiness gate but the triage is PROCEED / RESCOPE / CANCEL rather than Tier 1/2/3 resolution; the consumer is a downstream gate session (the audit master plan), not a build session. The gate samples a fraction of the audit-target population, applies the audit's intended methodology to the sample, and projects defect rates onto the full population to settle whether the multi-session investment is warranted.

**Consumer:** the audit master-plan session reads the gate report and decides whether to set up the routine block (PROCEED), rescope (RESCOPE), or abandon (CANCEL).

| Report | Gate session | Master-plan session | Status |
|---|---|---|---|
| [`phase_5_production_audit_gate.md`](phase_5_production_audit_gate.md) | S-0081 | S-0082 | PROCEED recommended; master plan landed; routine block pending |

### 3. Audit master-plan reports — multi-session audit setup

**Authoring trigger:** after an audit-warrant gate recommends PROCEED, per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — the master plan codifies methodology (prompt template, evidence schema, sample-size policy), Tier 1/2/3 triage carried over from the gate, and the routine task list (`engine/session/auto_target.json`) the routine block will execute against.

**Contract:** the master plan is the executable contract for the routine block. Methodology is fixed at master-plan close; routine sessions execute against the pinned methodology and surface deviations (e.g., expansion-rule firings) within their own scope.

**Consumer:** routine evidence sessions read the master plan at boot; the closeout session reads it (along with all evidence files) when authoring the audit's final report.

| Report | Master-plan session | Routine block | Status |
|---|---|---|---|
| [`phase_5_production_audit.md`](phase_5_production_audit.md) | S-0082 | S-0083+ pending | Master plan landed; routine block pending |

### 4. Closeout reports — phase-end retrospective

**Authoring trigger:** at phase end, after the last routine task target-met fires, per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — an interactive session reviews the routine block, files cross-session deferrals as Issues, authors any ADR memos needed, and records overall observations.

**Contract:** retrospective rather than gate. The closeout doesn't gate downstream work; it documents what the phase actually accomplished, what surfaced for follow-up, and what should change about how the next phase runs.

**Consumer:** subsequent gate sessions and audits read closeouts to understand prior-phase decisions; the phase's `next_session_work` in [`engine/STATE.md`](../STATE.md) typically points at the closeout as the orientation surface.

| Report | Closeout session | Phase | Status |
|---|---|---|---|
| [`phase_5_closeout.md`](phase_5_closeout.md) | S-0076 (routine task P5-12) | Phase 5 | Phase closed |

### 5. First-exercise readiness notes — mechanism observability gate

**Authoring trigger:** when a novel cross-cutting mechanism (a wrapper tool, a new validator gate, a new lifecycle hook) lands and is about to be exercised in production for the first time, per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). The note documents what the mechanism is supposed to do, what would constitute success at first exercise, what failure modes to watch for, and how to recover.

**Contract:** the note is consulted at the first invocation of the mechanism in production conditions. The session that exercises the mechanism reads the note, executes, and records the outcome. If the first exercise reveals ADR-warranting structure, the note's findings flow into a follow-up ADR or an amendment to the originating ADR.

**Consumer:** the session that first exercises the mechanism, in production. Subsequent invocations don't re-read the note — once the first exercise lands cleanly, the note becomes a historical artifact.

| Report | Authoring session | First-exercise session | Status |
|---|---|---|---|
| [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md) | S-0064 (per [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md)) | T1-A pending — closes at next routine fire post-S-0064 | Pre-first-exercise |
| [`mempalace_mechanical_adoption_first_exercise.md`](mempalace_mechanical_adoption_first_exercise.md) | S-0078 (per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md)) | T1-B pending — closes at next routine fire post-S-0078 with non-zero `diary_write_calls` in archived `mempalace_activity` | Pre-first-exercise |
| [`routine_lifecycle_push_first_exercise.md`](routine_lifecycle_push_first_exercise.md) | S-0061 (per [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md)) | First exercise landed at S-0062 routine eager-claim push | Closed |
| [`adversarial_stance_first_exercise.md`](adversarial_stance_first_exercise.md) | S-0085 (per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md)) | T1-A through T1-E pending — close at next cadence-fired audit (S-0087 by recommended sequencing) | Pre-first-exercise |
| [`apply_migration_postcondition_first_exercise.md`](apply_migration_postcondition_first_exercise.md) | S-0094 (per [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) + [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Consequences amendments — Layer 2.5 postcondition verification) | T1-A pending — closes at next routine fire post-S-0094 OR next interactive `--force` re-apply of an annotated seed | Pre-first-exercise |

### 6. Apparatus-improvement reports — engine-apparatus retrospectives

**Authoring trigger:** when an engine-apparatus session's work warrants a cross-cutting retrospective beyond what the session archive captures — typically a session that lands multiple intertwined ADRs or contracts and benefits from a single document tying them together. Currently one instance, authored as a hybrid gate-plus-build report (the apparatus-improvement frame compresses the gate and build into one session per the report's "Compression note").

**Contract:** the report enumerates the apparatus changes, the commits / ADRs they ride on, the user-facing improvements, and remaining gaps. Distinct from a closeout: closeouts are phase-end (one phase's product work); apparatus-improvement reports cover engine-apparatus work that doesn't sit cleanly inside a phase.

**Consumer:** future health-check audits; the retrospective is a freshness-probe input ("did the apparatus changes hold up?").

| Report | Authoring session | Subject | Status |
|---|---|---|---|
| [`engine_apparatus_improvements_s0042.md`](engine_apparatus_improvements_s0042.md) | S-0042 (hybrid gate + build per the report's "Compression note") | HANDOFF narrowing per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) + scope-lock at boot per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) | Closed |

## Lifecycle

Reports across all six classes share a lifecycle:

- Authored at trigger time (per the per-class table above).
- Consumed at the consumer's natural read point.
- Remain in place after consumption — no retirement, no archival. The repo's history (commits, session archives, ADR cross-refs) is the change record; the report itself is the artifact.

When a downstream session discovers that a report under-specified a decision (a Tier 2 that should have been Tier 1; a closeout that overlooked a pattern visible in retrospect), the discovery is recorded in the discovering session's `outcome_summary` and the next exercise of that report class refines its template. The report itself is not retroactively edited; the discrepancy is the signal.

## See also

- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — citable contract for gate reports (classes 1, 2).
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — routine-mode operations; governs audit master-plan and closeout reports (classes 3, 4).
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — citable contract for first-exercise readiness notes (class 5).
- [`../operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) — operational surface; report template (classes 1, 2).
- [`../operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) — operational surface for classes 3, 4.
- [`../operations/mechanism-first-exercise-gate.md`](../operations/mechanism-first-exercise-gate.md) — operational surface for class 5.
- [`../operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) — boot procedure; gate-class consumers read reports at boot.
- [`../STATE.md`](../STATE.md) — "Next session work item" links to the active report.
