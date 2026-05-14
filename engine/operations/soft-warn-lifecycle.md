# Soft-warn lifecycle

> Soft-warns are signal, not noise. They live across sessions because trends matter more than per-invocation events. This document names where soft-warn data lives, how it surfaces at session boot, and the escalation criterion that promotes a persistent soft-warn to a decision. Per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md).

## The problem this addresses

`engine/tools/validate.py` emits soft-warns on every commit. The pre-commit hook calls them informational, not blocking. Recording these warns in a per-clone gitignored `validate-history.jsonl` makes them invisible across worktrees and across fresh clones. A soft-warn category can fire on every commit for many sessions and surface only at the periodic health check (every ~30 sessions per [ADR 0022](../adr/0022-periodic-project-health-checks.md)) — by which point the AI has habituated to the noise.

Cascade discipline ([ADR 0041](../adr/0041-cascade-analysis-discipline.md)) adds three new soft-warn categories. Without a closed loop on persistent warns, the new categories enter the same drift mode.

MemPalace mechanical adoption (ADR 0056, S-0078) adds two more soft-warn categories — `mempalace_boot_query_skipped` and `mempalace_diary_read_skipped` — plus the `mempalace_diary_write_acknowledged_skip` downgrade-from-hard-fail variant. They use the same archive canon and 3-of-5 boot surface as every other category. The previous `diary_skipped` (manually-recorded) is renamed to `mempalace_diary_write_skipped` (mechanically-detected from `mempalace_activity` telemetry); historical archives migrated via `engine/tools/migrate_diary_skipped_archive_field.py`. The hard-fail companion (`mempalace_diary_write_skipped`) is enforced at session shutdown by `validate.py --final-check`.

The S-0093 amendment to ADR 0056 (Issues [#38](https://github.com/StarshipSuperjam/paideia/issues/38) + [#39](https://github.com/StarshipSuperjam/paideia/issues/39)) adds one more category: `mempalace_zero_citations_after_search` — the closed-loop counterpart to `mempalace_boot_query_skipped`. Fires when boot search happened but the citation scan at shutdown found zero drawer references in `outcome_summary`/diary/commit messages. Same archive canon, same 3-of-5 boot surface. See [`tools-validate-interpretation.md`](tools-validate-interpretation.md) `mempalace_zero_citations_after_search` for interpretation and tuning paths.

## Source of truth

The trend canon is the committed `engine/session/archive/S-NNNN.json` field `outcome_summary.soft_warns` — a structured `{category: count}` block written at session shutdown alongside the prose `outcome_summary`. This file is committed; it survives worktree rotation and fresh clones.

The per-invocation `engine/tools/validate-history.jsonl` continues to record every validator run with full granularity (per-category count plus runtime). It is not the trend canon — it is fine-grained debugging data, gitignored and per-clone. Trend reading uses the archive; per-invocation forensics uses the jsonl.

The shape of the structured field at session close:

```json
"outcome_summary": "Phase 3 SQL schema landed: 8 migrations ... pytest 56/56.",
"outcome_summary_soft_warns": {
  "expected_future_file_missing": 0,
  "adr_missing_status": 0,
  "adr_index_inconsistent": 0,
  "cross_reference_broken": 0,
  "engine_log_format": 0,
  "state_format": 0,
  "superseded_adr_currency": 0,
  "adr_back_reference_orphan": 2,
  "adr_consequences_deliverable_audit": 0
}
```

The prose `outcome_summary` retains the narrative role (what got done, what tradeoffs surfaced, what's queued). The `outcome_summary_soft_warns` companion is read mechanically by the boot surface and the health check.

## Boot-time persistent-warn surface

At `/start-engine` boot, after reading `engine/STATE.md` and `engine/session/register_state.json`, the AI reads the last K archives (default `K=5`) and counts soft-warn category occurrences:

- For each soft-warn category appearing in the union of those K archives, count how many of the K archives have a non-zero count for that category.
- Categories appearing in `≥3` of `5` archives surface as a boot-time prompt:

> "Soft-warn `<category>` has fired in N of the last K sessions; consider addressing or escalating per `engine/operations/soft-warn-lifecycle.md`."

The surface is informational; it does not block the session's planned work. The session decides whether to (a) address the underlying cause inline, (b) defer to a follow-up session, or (c) escalate per the criterion below if the warn has persisted long enough.

The default `K=5` and threshold of `3/5` are calibration points. Tighten the threshold if surfaces are consistently no-action; loosen if real persistence goes unsurfaced. Calibration changes are recorded in this document with rationale; major calibration changes (e.g., changing the default K) are ADR-tracked under [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s amendment discipline.

The cadence-trigger health check at `S-mod-N` (where N is `health_check_cadence` in `engine/session/register_state.json`; default 10 as of S-0033, was 30 from S-0001 to S-0032 per ADR 0022 Consequences amendment; see [ADR 0022](../adr/0022-periodic-project-health-checks.md)) consumes the same archive data with a longer window — typically the full archive — and produces the structured Fit / Gaps / Dead-weight / Bloat report. The boot surface is the day-to-day analogue; the health check is the periodic deep audit.

## Closing discipline

At session shutdown step 11 (per [`session-shutdown-sequence.md`](session-shutdown-sequence.md)), the structured `outcome_summary_soft_warns` block is computed from `validate.py`'s `validate-history.jsonl` entries and written to `engine/session/current.json` alongside the prose `outcome_summary`. The archive step preserves the structured field as committed data.

**Aggregation surface (per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md), S-0035 onward):** the block aggregates across every `validate.py` invocation in this session, not just the final pre-commit run. Per-category max-count across all entries with this session's `session_id` (or the timestamp window for entries tagged "outside-session"). This catches boot-time probe firings that resolve before shutdown — the `--health-probe-only` mode invoked by `session-start.sh` writes its own validate-history.jsonl entries which would otherwise be lost. Without aggregation, a `chromadb_palace_health` finding at boot that's been repaired mid-session would not contribute to the cross-session 3-of-5 surface.

Sessions that hit `closed_partial` write the structured block from whatever validator runs were captured up to the partial-close — incomplete sessions still contribute trend data.

## Escalation criterion

A soft-warn category that persists with non-zero count for `≥10` consecutive sessions becomes a candidate for one of three resolutions. The session at which the 10th cumulative occurrence is observed (typically through the boot surface) escalates the choice:

- **Promote to hard-fail.** The category names a structural invariant the project would always want to fix; the soft-tier was a calibration mistake. Promotion is an ADR-tracked decision (amends [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) or supersedes it depending on scope). Validator code moves the check to the hard-fail branch; pre-commit hook now blocks on it.
- **Accept and annotate.** The warn is not actionable in the current project state but is real signal. The category gets a "expected to persist until <condition>" annotation in [`tools-validate-interpretation.md`](tools-validate-interpretation.md), and the boot surface suppresses the category for sessions that match the annotation's condition (e.g., "expected_future_file_missing for Phase 7 file expected to fire until Phase 7 opens"). The annotation is itself revisited at the next health check.
- **Address inline.** The persistent warn names a real fix that has been deferred. The session that observes the 10-session threshold either does the fix or queues it as the next session's primary work.

The 10-session threshold was originally informed by the then-cadence-30 interval (a warn persisting through one-third of a cycle had multiple opportunities to be acted on; persistence beyond that is structural rather than transient). At S-0033 the cadence tightened to 10, so the 10-session threshold is now exactly one cadence cycle; revisit at the first cadence-10 audit (S-0040) whether the threshold should also tighten (e.g., to 5) so that escalation can fire within a cycle. Recording the calibration question here per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s amendment discipline; no immediate change.

## Migration from the jsonl-as-canon model

Sessions before [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s authoring did not write structured `outcome_summary_soft_warns`. The trend window for the boot surface and the first health check is bounded by the archive count *with structured fields*; pre-S-0029 archives carry only prose summaries and contribute prose-mention coverage only.

The first health check that runs against the new canon (S-0030 if Option 2 sequencing per the approved plan) accepts that the 10-session escalation criterion is not yet meaningful and treats the first 10 sessions of structured data as a calibration window. Escalations begin at the first observed 10-session-persistent category after S-0038 or thereabouts; before that, the boot surface still fires for `≥3/5` patterns within the structured-data window.

## See also

- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — the citable contract this document operationalizes.
- [ADR 0022](../adr/0022-periodic-project-health-checks.md) — the periodic audit that does the deep version of what the boot surface does shallowly.
- [ADR 0041](../adr/0041-cascade-analysis-discipline.md) — three new soft-warn categories whose lifecycle this document closes the loop on.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — per-category soft-warn meanings; persistent-warn annotation lives here.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — closing-discipline integration.
- [`health-check.md`](health-check.md) — periodic deep audit.
- [`/start-engine`](../../.claude/commands/start-engine.md) — boot-time persistent-warn surface step.
