# MemPalace mechanical adoption — first-exercise gate report

> Authored by S-0078 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first interactive exercise of the four-layer MemPalace mechanical adoption mechanism that [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) introduces. Required because the mechanism qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥5 tooling files — the change touches the new hook + new rollup tool + parameterized audit + validate.py + migration script + 4 SKILLs + 4 ops docs + ADR + CLAUDE.md + .claude/settings.json + .gitignore = 16 surfaces).

## Mechanism summary

End-to-end mechanization of the three deliberate uses of MemPalace (boot `mempalace_search`, boot `mempalace_diary_read`, shutdown `mempalace_diary_write`) across interactive (`/start-engine`) AND routine (`/start-routine`) session modes:

- **Layer 1 (telemetry):** `engine/tools/hooks/post-mempalace-tool-use.sh` PostToolUse hook matched on `mcp__mempalace__.*` appends one JSONL line per MCP call to `engine/session/current_mempalace.jsonl`.
- **Layer 2 (rollup):** `engine/tools/scan_mempalace_activity.py` reads the JSONL at shutdown step 0 and writes the structured `mempalace_activity` field to `engine/session/current.json`.
- **Layer 3 (audit):** `validate.py --final-check` (gated CLI flag, only invoked at shutdown step 1) reads `mempalace_activity` and emits `mempalace_boot_query_skipped` (soft-warn), `mempalace_diary_read_skipped` (soft-warn), and `mempalace_diary_write_skipped` (hard-fail with acknowledgement-token escape hatch).
- **Layer 4 (structural):** `engine/tools/audit_archive_structured_fields.py` parameterized to `REQUIRED_ARCHIVE_FIELDS` declarative list; `mempalace_activity` declared since-S-0078. Closes Issue #20.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | **Yes** (three new categories: `mempalace_boot_query_skipped`, `mempalace_diary_read_skipped`, `mempalace_diary_write_acknowledged_skip`; plus the `mempalace_diary_write_skipped` hard-fail with escape-hatch discipline) |
| #3 — introduces a new state file the boot procedure reads | **Yes** (`engine/session/current_mempalace.jsonl` is per-session telemetry that the PostToolUse hook writes during the session and the rollup tool reads at shutdown) |
| #4 — Consequences span ≥3 ops docs OR ≥5 tooling files | **Yes** (16 surfaces) |

**Qualifies on three criteria; gate session needed before unattended use.** This report IS the gate report; the gate session is S-0078 (build session is also the first-exercise session per the same compression precedent set in `apply_migration_first_exercise.md` at S-0064 and `routine_lifecycle_push_first_exercise.md` at S-0060).

## Phase 0 empirical findings

The load-bearing question: does the four-layer mechanism reliably catch a session that fails to invoke the three deliberate MemPalace uses, AND avoid spurious nag during normal session operation?

### Run 0 — design verification (S-0078 boot)

Plan-mode adversarial review during S-0078 plan authoring identified two potential failure modes:

1. **PostToolUse hook fires on default-mode (exploration) sessions where there's no formal session.** The telemetry would land in a stale `current_mempalace.jsonl` that the next session would inherit. Mitigation: the rollup tool is invoked only at shutdown by build/routine sessions; default-mode sessions never write to current.json or run the shutdown sequence. The boot procedure's eager-claim ritual implicitly resets the session state. (Future tightening: have the boot ceremony explicitly clear `current_mempalace.jsonl` before claiming the slot. Deferred to S-0079+ because the residual risk is low — at worst a stale telemetry line gets rolled into a fresh session's archive without affecting the audit's threshold logic.)

2. **The `--final-check` flag is gated; if the SKILL forgets to pass it, the audit doesn't fire.** Mitigation: the structural-fields audit (Layer 4) catches the case where `mempalace_activity` is absent (the rollup tool didn't run); the `mempalace_diary_write_skipped` hard-fail still fires when the rollup ran with zero diary_write_calls. Mid-session evidence will tell whether this is sufficient defense-in-depth, or whether the pre-commit hook should also invoke `--final-check` on closing commits. Deferred to T1-A below.

### Run 1 — interactive S-0078 self-test

S-0078 is the build session that lands the mechanism. The session itself exercises the mechanism end-to-end:

- The PostToolUse hook is wired into `.claude/settings.json` and immediately starts capturing this session's MemPalace MCP calls (boot `mempalace_search` for Issues #27/#20 context, boot `mempalace_diary_read`, plus the eventual shutdown `mempalace_diary_write`). The hook fires for the first time when this session's first `mcp__mempalace__*` call lands AFTER the settings.json change is committed (which happens in the eager-claim, so it's already active).
- `scan_mempalace_activity.py` runs at shutdown step 0 (per the updated SKILL).
- `validate.py --final-check` runs at shutdown step 1 (per the updated SKILL). The diary write at step 7 must land before step 1's re-run, OR the AI uses the acknowledgement-token escape hatch.
- `audit_archive_structured_fields.py --from-stdin` runs in the closing-commit pre-commit hook (existing wiring) and validates the `mempalace_activity` field shape.

**Expected outcome:** all three categories report zero counts at the start of shutdown (no MemPalace calls yet recorded if the hook didn't fire pre-eager-claim); the AI adds a `mempalace_unavailable_acknowledged: hook landed mid-session; pre-eager-claim calls untracked` to `outcome_summary`, OR the actual call counts are sufficient for the boot query and diary read because they happen post-eager-claim.

**T1-A is the load-bearing test for this mechanism's first interactive exercise.**

### Run 2 — first routine fire post-S-0078

The next routine fire post-S-0078 exercises the routine-mode-lifecycle SKILL changes. Routine boot procedure runs steps 5.5 (boot query) and 5.6 (diary read) after eligibility selection; shutdown step 11 explicitly invokes the diary write + pushback/lesson capture asks. The validator's adoption check fires from `validate.py --final-check` at the standard shutdown sequence (step 1).

**T1-B is the routine-context first-exercise test.** Defer until the next routine fire opens.

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | The mechanism's interactive first-exercise must verify all four layers compose correctly: PostToolUse hook fires, rollup tool reads the JSONL, `validate.py --final-check` reads the rollup, the structural-fields audit accepts the field shape. | **Pending S-0078 shutdown.** If the close commit lands cleanly (validate.py --final-check passes OR acknowledgement-token downgrade succeeds; closing-commit hook accepts the archive shape), T1-A closes. If the close commit blocks unexpectedly, file follow-up Issue and adjudicate inline. |
| T1-B | The mechanism's routine-context first-exercise must verify the SKILL changes (steps 5.5/5.6/11 enumeration) are honored by an actual routine fire. | **Pending the next routine fire post-S-0078.** Phase 6 master plan (S-0079 candidate) and the first Phase 6 routine fire are the natural exercise points. T1-B closes when a routine session lands a clean close with non-zero diary_write_calls in its archived `mempalace_activity`. |
| T1-C | The acknowledgement-token escape hatch must be detectable and not abusable. | **Resolved at S-0078** by per-token-presence soft-warn category (`mempalace_diary_write_acknowledged_skip`) participating in the same 3-of-5 escalation. Persistent acknowledged-skips fire the same surface as unacknowledged ones. |
| T1-D | Pre-S-0078 historical archives carrying the legacy `diary_skipped` field must be migrated to `mempalace_diary_write_skipped` so the persistent-warn surface treats them as a single trend. | **Resolved at S-0078** by `engine/tools/migrate_diary_skipped_archive_field.py`. Migration ran cleanly against 32 archives (all with value 0; line-removal preserves formatting and UTF-8). 10 unit tests cover the migration logic including the last-key-strip-prior-comma edge case. |
| T1-E | The four-layer mechanism must be operative in default-mode (exploration) sessions WITHOUT firing spurious soft-warns. | **Resolved at S-0078** by `validate_mempalace_adoption()` early-return when `current.json` is absent (sentinel for default mode). The PostToolUse hook continues to log calls but the rollup and audit don't fire. |

## Tier 2 findings (resolve in-session OR defer with explicit forward pointer)

| ID | Finding | Status |
|---|---|---|
| T2-A | The boot ceremony does not explicitly clear `current_mempalace.jsonl`. A stale line from a prior default-mode session could carry into a fresh build session's archive. | Deferred to a follow-up cleanup batch (likely S-0079+). Risk is low — at worst a single stale telemetry line gets rolled into the fresh session's archive without affecting the audit's threshold logic (the audit cares about counts > 0, not ≤ N). Tracked as a low-priority cleanup. |
| T2-B | The pre-commit hook on closing commits does NOT also invoke `validate.py --final-check`. The defense-in-depth comes from the structural-fields audit (Layer 4), which catches missing `mempalace_activity`; the semantic check (Layer 3) only runs via the SKILL. | Deferred. Wait for one quarter of routine sessions post-S-0078 to confirm the SKILL invocation is reliable. If a routine session manages to skip both the SKILL invocation AND the structural-field audit doesn't catch the resulting absence, escalate by adding the closing-commit pre-commit hook invocation. |
| T2-C | The acknowledgement token format (`mempalace_unavailable_acknowledged: <reason>`) is not formally schema-validated. A typo would silently fail to bypass the hard-fail. | Resolved at S-0078 by the validator's substring search being case-sensitive and exact-prefix. Typos surface as a continued hard-fail; the AI sees the failure and can correct. Documented in the SKILL and ops docs. |

## Tier 3 forward pointers

| ID | Finding | Status |
|---|---|---|
| T3-A | Recovery of lost MemPalace content from S-0032 → S-0077 (diary entries, ADR-companion `decision` drawers, `pushback` drawers, `lesson` drawers) is bounded as Part B of the S-0078 plan. | Deferred to S-0079+ per plan. Audit script + transcript-crawl executor + per-mode breakdown report. ~45 sessions to crawl; ~2-4 hours subagent work. |
| T3-B | Wing-naming bug (Issue [#1](https://github.com/StarshipSuperjam/paideia/issues/1)) and wing-filtered search bug (Issue [#2](https://github.com/StarshipSuperjam/paideia/issues/2)) remain upstream-blocked. The mechanism uses unfiltered `mempalace_search` to work around. | No-op for this mechanism; remains tracked. |
| T3-C | The HNSW vector-index divergence (~34% of drawers invisible to vector search) flagged in the boot-time MemPalace query is a pre-existing issue not addressed by this work. | The user can run `mempalace repair` independently; not in scope for S-0078. |

## Success criteria

- **At S-0078 close:** `validate.py --final-check` passes (with diary write landed) OR the acknowledgement-token downgrade succeeds; the closing-commit hook accepts the `mempalace_activity` field shape; Issues #27 and #20 are closed via `gh issue close`.
- **Within one cadence cycle (~10 sessions) post-S-0078:** at least one routine session has landed a clean close with non-zero `diary_write_calls` recorded in its archived `mempalace_activity`. This is T1-B closing.
- **Within three cadence cycles (~30 sessions) post-S-0078:** the persistent-warn 3-of-5 surface fires correctly on a session that legitimately skipped a category (e.g., `mempalace_boot_query_skipped` if a session truly forgot to query at boot). Healthy noise floor: 0-1 categories firing across the rolling 5-archive window during normal operation.

## Cross-references

- [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) — the contract this report exercises.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate framework this report instantiates.
- [Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27) — closes.
- [Issue #20](https://github.com/StarshipSuperjam/paideia/issues/20) — closes.
- Plan file: `/Users/shanekidd/.claude/plans/use-of-mempalace-by-velvety-pebble.md` — the approved-and-sequenced design this implementation realizes.
