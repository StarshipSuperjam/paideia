# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122).** 380 nodes + 536 edges across 15 seed migrations. Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md). **Production audit (T-PHASE-5-AUDIT) ran S-0104 → S-0120; closeout at S-0122** — findings report at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input report at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); structural-reopen ADR for historical_influence retyping at [`product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md`](../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) (per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md)): 31 successful SEP fetches, 0 anonymization violations, ~2.0s rate-limit empirically observed. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout is complete. ADR collection: **61 (59 Accepted + 2 Superseded; 25 engine + 36 product)**. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0122 (2026-05-11) — Phase 5 production-audit closeout.** Empirical-fortification pass via [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) against `plato.stanford.edu`: 33 SEP fetches queued / 31 succeeded / 0 `AnonymizationViolation` events / rate-limit ~2.0s/fetch empirically observed (closes T1-A through T1-D in [`fetch_structural_reference_first_exercise.md`](build_readiness/fetch_structural_reference_first_exercise.md) per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md)). Verdict-update tally: 30 corroborated / 15 with forward link present / 1 structural-only. Authored findings report + audit-system-input report + product [ADR 0061](../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md) retyping 17 history-terminator cross-bridges from `pedagogical_prerequisite` to `historical_influence`. Filed 5 GitHub Issues per disposition matrix (15 direction reversals to flip, 17 historical retypings, 4 weak-edge prunes + 5 retentions-with-annotation, 4 validator soft-warn proposals, 7 evidence-field annotations). Both optional ADRs (philosophy-of-religion readmission, engine-side post-phase-audit pattern) skipped — no crystallization in the data justified authoring. |

## Next session work item

**S-0123 — execute Phase 5 production-audit follow-ups.** Interactive `/start-engine`. Per S-0122 findings report's disposition matrix:

- **Author the retyping migration** (Issue [#60](https://github.com/StarshipSuperjam/paideia/issues/60)) — 17 history-terminator cross-bridges retyped from `pedagogical_prerequisite` to `historical_influence` per [ADR 0061 product](../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md). Author `product/seed-graph/migrations/0061_retype_historical_influence_crossbridges_part1.sql` with Layer 2.5 postcondition assertions per [ADR 0055](adr/0055-apply-migration-wrapping-against-production-reads-gate.md).
- **Author the direction-flip migration** (Issue [#59](https://github.com/StarshipSuperjam/paideia/issues/59)) — 15 reversed edges flipped (8 cross-bridge + 7 within-subdomain).
- **Author the weak-edge cleanup migration** (Issue [#61](https://github.com/StarshipSuperjam/paideia/issues/61)) — 4 prunes + 5 retain-with-annotation.
- **Author the evidence-field annotation migration** (Issue [#63](https://github.com/StarshipSuperjam/paideia/issues/63)) — 7 defensible edges with annotation prose.

These four migrations can batch into one session if budget allows, or split across sessions per the user's preference. The retyping migration (Issue #60) is the gating item since it activates `historical_influence` in PREDICATE_MANIFEST.md.

**S-0124+ candidates:**

- **Add the 4 validator soft-warns from the audit-system-input report** (Issue [#62](https://github.com/StarshipSuperjam/paideia/issues/62)). Three are gate-feasible immediately; one (`historical_node_as_prereq_source`) waits on a node-class schema extension.
- **Adjudicate S-0121 audit findings** per the report's User adjudication subsection (junk-drawer-prose recommendations, ADR Consequences inline-amendment pattern, operations-doc bloat survey). Standard execution-lane routing per [ADR 0048](adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).
- **OQ-DEC1-A through OQ-DEC1-D settlement** — Phase 6 self-correction master plan is blocked behind these.
