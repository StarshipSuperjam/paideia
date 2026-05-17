# ADR 0042 — Soft-warn lifecycle: persistent warns surface at boot; archive is canon

- **Status:** Accepted
- **Date:** 2026-05-02
- **Deciders:** S-0029

## Context

`engine/tools/validate.py` emits soft-warns on every commit. The pre-commit hook calls them informational, not blocking. Two failure modes have manifested:

1. **No cross-session trend tracking.** Soft-warn data accumulates in `engine/tools/validate-history.jsonl`, which is gitignored and per-clone. Across worktrees and across fresh clones, the trend window starts over. The periodic project health check ([ADR 0022](0022-periodic-project-health-checks.md)) is the only mechanism that surfaces persistent warns, and at the time of this ADR it fired every 30 sessions (tightened to every 10 at S-0033 per ADR 0022 Consequences amendment, which makes the cycle gap shorter — but the underlying structural problem this Context describes still applies). A soft-warn category can fire on every commit across many sessions between audits and only get noticed at the next cadence — by which point the AI has habituated to the warn as background noise.
2. **No closed loop on what to do with persistent warns.** Even if a session notices that a category has fired many times, the project carries no protocol for promoting the warn to a hard-fail, accepting it with annotation, or queuing the inline fix. The result is silent re-rolling forward.

[ADR 0041](0041-cascade-analysis-discipline.md) adds three new soft-warn categories (superseded-ADR currency, ADR back-reference orphan, ADR Consequences-deliverable audit). Without a closed loop, the new categories enter the same drift mode.

The two existing data sources have complementary value: `validate-history.jsonl` carries per-invocation granularity (every commit's run, including runtime); `engine/session/archive/S-NNNN.json` carries per-session summary committed to the repo. The latter is the natural place for trend canon — committed, durable, queryable across worktrees, already populated at session shutdown.

## Decision

Three changes compose the new lifecycle:

1. **Trend canon moves to `engine/session/archive/S-NNNN.json`.** A structured field `outcome_summary_soft_warns: {category: count}` is written at session shutdown alongside the prose `outcome_summary`. The `validate-history.jsonl` continues to record per-invocation telemetry for fine-grained debugging but is no longer the trend source.

2. **`/start-engine` surfaces persistent warns at boot.** After reading `STATE.md` and `register_state.json`, the AI reads the last 5 archives, counts soft-warn category occurrences, and surfaces any category appearing in 3-or-more of those 5 archives as a boot prompt. The surface is informational; the session decides whether to address, defer, or escalate.

3. **A 10-session-persistence escalation criterion.** A soft-warn category appearing in 10 consecutive archives becomes a candidate for one of three resolutions, decided by the session at which the threshold is observed: promote to hard-fail (validator code change + new ADR), accept and annotate (`tools-validate-interpretation.md` entry that suppresses the surface for the annotated condition), or address inline (fix lands in the observing session or the next one).

The operational details — exact thresholds, calibration triggers, structured-field shape, migration handling for pre-ADR archives — live in [`engine/operations/soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md).

## Consequences

`engine/session/archive/S-NNNN.json` carries a new structured field. `engine/operations/session-shutdown-sequence.md` is amended to write the field at step 6 alongside the prose `outcome_summary`. The amendment is amendment-only (no new ADR for the lifecycle-doc change) per [ADR 0036](0036-expression-contract-for-inward-documents.md)'s amendment asymmetry.

`engine/tools/health_check.py` (authored later in this session under [ADR 0022](0022-periodic-project-health-checks.md)) reads the structured archive field as its trend source. Its Fit-section reporting on validator soft-warn distribution becomes mechanically computable rather than requiring manual jsonl parsing.

`/start-engine`'s boot procedure (in `.claude/commands/start-engine.md`) gains a step between the existing health-check cadence trigger check and the work-item read. The step is posture for now — there is no hook that fires it; the AI follows the procedure by discipline. Mechanizing the surface as a SessionStart hook is queued for Session β of the approved infrastructure plan.

Trade-offs accepted:

- **Pre-archive trend data is lost for the new system.** Sessions S-0001 through S-0028 archived without the structured field. The boot surface and the first health check have no usable trend window until structured data accumulates. The first ~10 sessions of structured data are a calibration window in which the escalation criterion does not yet apply. This is acknowledged explicitly in [`soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md)'s "Migration" section.
- **`validate-history.jsonl` continues to be authored without a consumer in the new path.** It remains useful for per-invocation forensics (when did this soft-warn first appear? which commit? how long did the validator take?) but the project's discipline-level reads route through the archive. A future cleanup may retire the jsonl entirely if its forensics value is not exercised; this ADR does not commit to that.
- **The 10-session threshold is calibration, not derivation.** It is informed by the 30-session cadence interval — one-third of a cycle is a natural "this is structural, not transient" mark — but no quantitative argument grounds the specific number. Tuning is expected; tuning is amendment-tracked under this ADR.

The `outcome_summary_soft_warns` field is additive to the existing schema; older session-archive readers (e.g., a future audit script written against the pre-S-0029 shape) continue to work and ignore the new field.

The **validator-pipeline classification map** at [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) is the canonical surface for per-category intent visibility under this lifecycle. Every soft-warn category emitted by `validate.py` lands in exactly one of five buckets — Actively-tracked (default), Persistent-warn annotation, Informational-only-accepted, Actively-tracked-deferred-re-audit, Retire-candidate — with a threshold matrix and re-run methodology documented alongside the per-category prose. The map names the *intent* (drift detector, structural invariant, informational, deferred re-audit, retire candidate); the per-category sections name the *meaning*. Re-classification routes through user adjudication at each cadence-fired health-check audit per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) user-buffered execution.

**Amendment (S-0196) — boot-surface split into action-needed and annotated-baselines lanes.** Per [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133), the S-0184 health-check audit surfaced that the boot persistent-warn surface had become a recap rather than an alert — at the audit moment, all 7 then-saturating categories carried documented annotations in `tools-validate-interpretation.md`'s "Persistent-warn annotation" section, so new threshold-crossings would have been buried under the documented-expected baselines. The fix splits Decision 2's surface into two output lanes at the boot hook ([`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh)): action-needed (per-category fires for non-annotated categories, with the existing escalation hint) and annotated-baselines (single-line count + pointer for categories with documented annotations). Membership is computed by [`engine/tools/scan_persistent_warn_annotations.py`](../tools/scan_persistent_warn_annotations.py) parsing the H2 annotation section; helper-failure falls back to empty-list (all categories surface as action-needed, preserving visibility). This is the structural completion of Decision 3's "accept and annotate" escalation resolution — annotation now mechanically suppresses the boot alert lane rather than relying on AI discipline per `.claude/skills/session-build-lifecycle/SKILL.md` posture. The cadence-fired audit per [ADR 0022](0022-periodic-project-health-checks.md) continues to consume the same archive data with a longer window — the boot surface's annotated-baselines lane is a periodic reminder that the bucket exists, not an audit replacement. See operational detail in [`engine/operations/soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md) "Annotated-baselines lane" subsection.

## See also

- [ADR 0022](0022-periodic-project-health-checks.md) — the periodic audit consumer this ADR's structured field unblocks.
- [ADR 0041](0041-cascade-analysis-discipline.md) — three new soft-warn categories whose lifecycle this ADR closes.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — amendment asymmetry for the lifecycle-doc updates.
- [`engine/operations/soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md) — operationalization.
- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) — closing discipline integration.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category meanings; persistent-warn annotation home.
- [`.claude/commands/start-engine.md`](../../.claude/commands/start-engine.md) — boot-time surface step.
