# engine/build_readiness/

> Build-readiness reports authored by gate sessions per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md). Each report sits at `<phase>_<chunk>.md` and is consumed by the build session that follows.

## Contract

Each report covers one substantive build session's worth of decisions. The gate session that authors the report is named in the report's header. The build session that consumes it boots, reads the report, and halts if Tier 1 contains unresolved items.

## Authoring procedure

See [`../operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) — the operational surface for the gate protocol. Reports follow the template in that document's "Build-readiness report template" section.

## Index

| Report | Gate session | Build session | Status |
|---|---|---|---|
| [`phase_3_sql.md`](phase_3_sql.md) | S-0027 | S-0028 | Build session closed |
| [`phase_4_graph_validation.md`](phase_4_graph_validation.md) | S-0034 | S-0037 | Build session closed |
| [`phase_5.md`](phase_5.md) | S-0045 (master plan) | Routine-mode (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md)) — 16 explicit tasks per [`engine/session/auto_target.json`](../session/auto_target.json) | Routine block executed S-0050 → S-0076; phase closed |
| [`phase_5_production_audit_gate.md`](phase_5_production_audit_gate.md) | S-0081 (audit-warrant gate, novel class) | Audit master-plan session pending PROCEED recommendation | Gate authored; PROCEED recommended; master plan + 12-evidence-session block + closeout(s) follow |

The `phase_5_production_audit_gate.md` report is a new class — an *audit-warrant gate* — that determines whether a multi-session production audit is warranted before the master-plan session sets it up. Structurally it parallels the standard build-readiness gate (Tier 1/2/3 triage adapted to PROCEED/RESCOPE/CANCEL outcomes) but its consumer is a future gate session (the audit master-plan), not a build session. The closeout session of the audit will introduce two further report classes (production-audit, audit-system-input) and update this index accordingly per [Issue #26](https://github.com/StarshipSuperjam/paideia/issues/26).

Closeout-class reports (e.g., [`phase_5_closeout.md`](phase_5_closeout.md)) and first-exercise readiness notes (e.g., [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md), [`mempalace_mechanical_adoption_first_exercise.md`](mempalace_mechanical_adoption_first_exercise.md), [`routine_lifecycle_push_first_exercise.md`](routine_lifecycle_push_first_exercise.md)) and apparatus-improvement reports (e.g., [`engine_apparatus_improvements_s0042.md`](engine_apparatus_improvements_s0042.md)) currently live in this directory without being indexed in the table above. The closeout session of the production audit (currently planned for S-0094 or thereabouts) is the natural surface to introduce a multi-class indexing structure resolving Issue #26.

## Lifecycle

A report is authored at gate-session close, consumed at build-session boot, and remains in place after the build session closes. Reports do not get retired or archived — they document what the build session inherited and serve as historical artifacts for downstream sessions and health checks.

When a build session discovers that the report under-specified a decision (a Tier 2 entry that the build session had to refine in-flight, or a Tier 3 deferral that turned out to be Tier 1 in disguise), the build session records the discovery in its `outcome_summary` and the next gate exercise refines its triage criteria. The report itself is not retroactively edited; the discrepancy is the signal.

## See also

- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — citable contract for the gate protocol.
- [`../operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) — operational surface; report template.
- [`../operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) — boot procedure; build sessions read reports at boot.
- [`../STATE.md`](../STATE.md) — "Next session work item" links to the active report.
