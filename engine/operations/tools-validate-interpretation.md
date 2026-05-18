# Interpreting `tools/validate.py` output

> The validator is the project's structural conscience. It runs in the pre-commit hook on every commit and on demand. This file documents what each output category means and the response posture for each.

## Exit codes

| Exit | Meaning | Response |
|---|---|---|
| `0` | Clean — no hard-fails, no soft-warns | Proceed. |
| `1` | Soft-warns only — no hard-fails | Allowed by hook (configurable via env), but every soft-warn must be acknowledged in `outcome_summary` at session close. |
| `2` | At least one hard-fail | Blocking. Pre-commit hook rejects the commit. Fix and retry. |

## Hard-fails (always blocking)

Hard-fails are structural mistakes that, if committed, would degrade the project's machinery. Always fix before the commit lands.

Categories:

- **Missing required top-level file** — README, LICENSE, SECURITY, ROADMAP, HANDOFF (top-level) plus engine/STATE.md and engine/changelog/README.md (engine-required per [ADR 0092](../adr/0092-per-session-changelog-directory.md)) must all exist. If you're intentionally retiring one, that's an architectural decision; ADR it first. (`engine/changelog/` replaces the pre-S-0198 monolithic `engine/ENGINE_LOG.md`, which itself was named `CHANGELOG.md` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md). The `CHANGELOG.md` filename is reserved for the future learner-visible product release log.)
- **`session/register_state.json` missing or malformed** — required keys: `next_id`, `last_claimed`, `current_status`. Format must parse as JSON.
- **`session/current.json` missing keys** — when present (during an in-progress session), must have `id`, `started_at`, `status`, `working_on`. `id` must match `^S-\d{4}$`.
- **Graph-audit hard-fails** — duplicate node IDs, dangling edge references, prerequisite cycles in the `pedagogical_prerequisite` subgraph (detected via Kosaraju SCC). Active when `SUPABASE_DB_URL` is set in the environment; absent env var records `graph_audit_skipped` and runs no DB query (non-seed-authoring sessions are not gated on DB connectivity). See [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) for the full contract.
- **`engine_memory_diary_write_skipped`** — diary-write hard-fail per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) (S-0078); **engine mode only** per S-0091. Fires when `engine_memory_activity.diary_write_calls == 0` AND `outcome_summary` lacks the `engine_memory_unavailable_acknowledged: <reason>` token AND `current.json` `mode` is not `routine`. Gated by `--final-check`. Engine asymmetry justified: interactive fix path is immediate (write the diary or write the token + reason); the hard-fail catches AI laziness in skipping the only first-person reflection layer. Recoverable by invoking `engine_memory_diary_write` and re-running `validate.py --final-check`, OR by adding `engine_memory_unavailable_acknowledged: <one-line reason>` to `outcome_summary` and re-running. Routine sessions hit the soft-warn `engine_memory_diary_write_skipped_routine` instead — see below.

If a hard-fail blocks a commit and the fix is non-obvious, escalate per [`escalation-criteria.md`](escalation-criteria.md). Don't bypass the hook (`--no-verify`) — investigate the root cause.

## Soft-warns (signal, not blocker)

Soft-warns indicate slipping discipline or expected gaps. Each one rolls up into a category count recorded in `outcome_summary` at session close. Trend analysis (per [`health-check.md`](health-check.md)) consumes the per-category counts to detect drift.

Categories and meaning:

### `expected_future_file_missing`

A file expected to exist in a future session (per `EXPECTED_FROM_S0002` in `validate.py`) hasn't been authored yet. Expected during the session that's *about to* author it; should drop to zero after that session closes.

Example: during S-0001 the warns for `CLAUDE.md`, `docs/MISSION.md`, `docs/CROSS_REFERENCES.md`, `docs/operations/README.md` are expected. After S-0002 closes, all four should resolve.

If still warning after the session that was supposed to author the file: investigate. Either the file got missed or the file's authored but at a different path than expected.

### `changelog_entry_soft_cap` / `changelog_entry_hard_cap`

A per-session changelog entry at `engine/changelog/<YYYY>/S-*.md` exceeds the body line cap (50 soft / 70 hard, including frontmatter). Per [ADR 0092](../adr/0092-per-session-changelog-directory.md). Recoverable — compress toward summary+pointers shape (the structured archive at `engine/session/archive/S-NNNN.json` carries the canonical narrative; the changelog entry is the categorical view). Release synthesis entries are the named exception that uses the soft-cap slack.

### `changelog_entry_schema_violation` / `changelog_entry_no_frontmatter` / `changelog_entry_filename_mismatch`

Hard-fail. A per-session changelog entry violates [`engine/schemas/changelog-entry.schema.json`](../schemas/changelog-entry.schema.json), lacks YAML frontmatter delimiters, or its filename's `S-NNNN` token does not match the `session_id` frontmatter field. Per [ADR 0092](../adr/0092-per-session-changelog-directory.md). Recoverable — fix the offending field/delimiter/filename; re-run.

### `changelog_readme_governance`

Line-cap soft-warn (>50) / hard-fail (>70) on `engine/changelog/README.md` (declared `governed: true / line_cap_soft: 50 / line_cap_hard: 70` in HTML frontmatter). Per [ADR 0092](../adr/0092-per-session-changelog-directory.md). Recoverable — compress the README; the changelog directory's reading surface is intentionally narrow.

### `engine_log_format`

Retired at S-0198 per [ADR 0092](../adr/0092-per-session-changelog-directory.md). The monolithic `engine/ENGINE_LOG.md` retired in favor of the per-session changelog directory; the `[Unreleased]` synthesis is produced on demand via `engine/tools/changelog_aggregate.py`.

### `state_format`

`STATE.md` missing the "Current phase" field. Recoverable — restore the field. Indicates structural drift.

### `cross_reference_broken`

A markdown link in `docs/CROSS_REFERENCES.md` points at a `.md` file that doesn't exist. Recoverable — either the target path is wrong, or the target file was renamed/retired without updating CROSS_REFERENCES.md.

### `adr_missing_status`

An ADR file (matching `adr/NNNN-*.md`) doesn't contain a `Status:` line. Active from S-0003 onward. Recoverable — add a Status field per [`adr-authoring.md`](adr-authoring.md).

### `adr_index_inconsistent`

An ADR file in `adr/` either is not referenced from `adr/README.md`'s per-phase tables, or its `Status:` core keyword (Accepted / Superseded / Deprecated / Proposed) differs from the index's status column for that ADR. Active from S-0020 onward.

Recoverable — either add the missing index row (most common case: a new ADR was authored without the index update), or align the `Status:` field to match the index. The check normalizes around the four core status keywords; markdown-link decoration inside the status column is tolerated. False positives should refine the check rather than be papered over.

### `superseded_adr_currency`

A doc cites an ADR whose `Status:` is now `Superseded by ADR NNNN`, and the citation does not mark itself as historical. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Recoverable — re-point the citation to the new ADR, or add a `(superseded by ADR NNNN)` qualifier if the reference is intentionally historical, or rewrite the surrounding paragraph if the supersession changes substance. The check excludes `*/adr/*.md`, the legacy `engine/ENGINE_LOG.md` filename, and the `engine/changelog/` directory per [ADR 0092](../adr/0092-per-session-changelog-directory.md).

False positives: a superseded-ADR mention that legitimately reads as historical context but the surrounding 50 chars do not include "superseded" or the new ADR id. Suppress by adding the qualifier or by widening the surrounding context to include the marker.

### `adr_back_reference_orphan`

An ADR with `Status: Accepted` has zero citations from `.md` files outside `*/adr/*`. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). The warn names a question, not a defect: is this ADR load-bearing for future work, or is it dead weight?

Suppress with the `Orphan-OK` annotation per [`cascade-discipline.md`](cascade-discipline.md):

```markdown
- **Orphan-OK:** <reason>; revisit at <session-id-or-phase>
```

The annotation is a deferral, not a permanent exemption. The periodic health check audits the orphan-OK list.

### `adr_consequences_deliverable_audit`

An ADR's Consequences section anticipated a deliverable "around S-NNNN," that session is closed (per `engine/session/archive/`), and a deliverable file path also named in the ADR text is absent on disk. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Heuristic regex: catches the literal "tools/foo.py around S-0025" shape; does not catch promises in different prose forms.

Recoverable — either land the deliverable (with closing-commit handshake per [`cascade-discipline.md`](cascade-discipline.md): cite the ADR id in the commit message), or amend the ADR's Consequences section to remove the now-obsolete promise, or document the deferral with a new expected session.

### `duplicate_adr_number`

An ADR number (4-digit prefix) appears in both `engine/adr/NNNN-*.md` and `product/adr/NNNN-*.md`. Per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) the engine/product partition shares a single ADR numbering sequence — numbers must not duplicate across the partition. Active from S-0149 onward — defense-in-depth landed alongside the engine ADR 0052 → 0082 renumber that closed [Issue #91](https://github.com/StarshipSuperjam/paideia/issues/91)'s collision.

Recoverable — pick one of the two ADRs to renumber (typically the one with the smaller forward-cascade), run the `git grep -l '<old-path>'` rename procedure per [`cascade-discipline.md`](cascade-discipline.md), and land the rename + all present-truth reference updates in a single atomic commit.

### `engine_memory_boot_query_skipped`

No `engine_memory_search` call was recorded during the session. Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md). Sourced from `engine_memory_activity.search_calls == 0` on `current.json`. Gated by `--final-check` (the shutdown step's audit invocation, not pre-commit hook fires).

Recoverable mid-session by invoking `engine_memory_search` once with the next-session work item terms; the post-tool-use hook captures the call into the session's JSONL, the rollup picks it up at shutdown, and the warn clears.

### `engine_memory_diary_read_skipped`

No `engine_memory_diary_read` call was recorded. Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md). Same telemetry path as the boot-query skip; same recovery (invoke once via the MCP tool with `agent_name="claude" last_n=3`).

### `engine_memory_boot_query_late`

The `engine_memory_search` boot query ran, but its first call landed *after* `current.json`'s `started_at` — i.e. after the eager-claim ritual, not at boot. Active from S-0160 onward per [Issue #124](https://github.com/StarshipSuperjam/paideia/issues/124). Sourced from `engine_memory_activity.search_first_ts` (per-tool first-call timestamp written by `scan_engine_memory_activity.py`) vs `current.json.started_at`. Gated by `--final-check`.

This is the timing counterpart to `engine_memory_boot_query_skipped`: skipped fires when the call never happened; late fires when it happened but too late to matter. The boot query exists to surface prior lessons and decisions *before* the session plans and executes; run after the deliverable is authored, it produces clean telemetry without the benefit — the recalled context can no longer change the work. Backward-compatible: skips silently when `search_first_ts` is absent (pre-S-0160 archives, JSONL-absent path) or when `started_at` is unparseable — fires only on a positive, unambiguous late signal. Not recoverable in-session (the work is already done); the fix is procedural — run the boot query at boot, before plan authoring.

### `engine_memory_diary_read_late`

The `engine_memory_diary_read` boot step ran, but its first call landed *after* `current.json`'s `started_at`. Active from S-0160 onward per [Issue #124](https://github.com/StarshipSuperjam/paideia/issues/124). Sourced from `engine_memory_activity.diary_read_first_ts` vs `current.json.started_at`. Gated by `--final-check`. Same shape, rationale, backward-compat, and non-recoverability as `engine_memory_boot_query_late` — the diary read exists to surface prior sessions' first-person reflections before planning; run late, they are recalled into a context where they can no longer inform the work.

### `engine_memory_diary_write_skipped_routine`

**Routine mode only**, per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) S-0091 routine-protection refinement. Fires when `engine_memory_activity.diary_write_calls == 0` AND `outcome_summary` lacks the `engine_memory_unavailable_acknowledged:` token AND `current.json` `mode == "routine"`. Engine sessions hit `engine_memory_diary_write_skipped` (hard-fail) instead — the asymmetry is justified by the unattended-vs-interactive difference.

Body is uniformly LOUD: `⚠️ ROUTINE DIARY DEFERRED — DO NOT BURY THIS`. Side effect: the validator appends an entry to [`engine/session/diary_pending_index.json`](../session/diary_pending_index.json) so the next session boot's SessionStart hook surfaces the count + IDs at every subsequent boot.

Recovery is *not* in-session — routines cannot recover their own dropped MCP. Recovery procedure: reconnect MCP (typically Claude Desktop reboot), open an interactive session, follow the "Deferred diary recovery" procedure at [`engine/operations/routine-mode-operations.md`](routine-mode-operations.md). The recovery session reads each pending archive, authors a diary entry from the structured fields, calls `engine_memory_diary_write`, and removes the entry from the index.

Persistent firing across 3-of-5 sessions deserves investigation — the routine-mode-lifecycle skill body's token-write branch may be buggy, OR the MCP substrate is failing more often than expected.

### `engine_memory_diary_write_acknowledged_skip`

No `engine_memory_diary_write` call was recorded BUT `outcome_summary` carries the `engine_memory_unavailable_acknowledged: <reason>` token, AND the in-process engine_memory healthcheck (`engine.memory.connection.healthcheck()` per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md)) confirms the substrate IS unreachable at close-time (the S-0089 contract tightening, retooled for the SQLite substrate at S-0192). Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) (superseded by ADR 0091 at S-0188); contract tightened at S-0089 per the Consequences amendment.

Body is uniformly LOUD per S-0091: `⚠️ DIARY WRITE SKIPPED — DO NOT BURY THIS` prefix in both engine and routine modes. The S-0089 engine/routine differentiation is dropped (see `mempalace_diary_write_skipped_substrate_intermittent` above for the rationale).

The token always downgrades the diary-write hard-fail to a soft-warn (so the session closes); the soft-warn category depends on the substrate state at close-time. Substrate unreachable → this category (`engine_memory_diary_write_acknowledged_skip`); substrate reachable → `mempalace_diary_write_skipped_substrate_intermittent` (per S-0090). The S-0087/S-0088 burial pattern stays hard to repeat because both paths now have uniformly LOUD bodies surfacing the AI's claim alongside the substrate state.

Persistent firing across 3-of-5 sessions deserves investigation; single-session firing is itself investigation-worthy under the S-0089 contract.

### `engine_memory_zero_citations_after_search`

The session invoked engine-memory boot search (`search_calls > 0`) but the citation scan at shutdown found zero drawer references in `outcome_summary` + today's diary entry + commit messages. Active from S-0093 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) S-0093 amendment + [Issue #39](https://github.com/StarshipSuperjam/paideia/issues/39) (ADR 0056 superseded by [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) at S-0188; the check carried forward unchanged). Sourced from `engine_memory_activity.search_calls > 0 AND engine_memory_activity.engine_memory_citations.total == 0` on `current.json` (the rollup field renamed from `mempalace_activity` to `engine_memory_activity` at the S-0192 cutover). The citations block is written by [`engine/tools/scan_engine_memory_citations.py`](../tools/scan_engine_memory_citations.py) at shutdown step 12. The check is gated on session id ≥ S-0093 (pre-S-0093 archives lack the block by design).

This is the closed-loop counterpart to `engine_memory_boot_query_skipped`. Boot-query-skipped fires when the call did not happen; zero-citations-after-search fires when the call happened but produced no observable behavior change. Either side firing is signal that the boot-search apparatus is not delivering value.

Expected zero in well-functioning sessions — the boot-search orchestrator surfaces drawers that bear on the work, the AI cites them in plan rationale or commit messages, and the citation scan picks them up. Persistent firing across 3-of-5 sessions per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) signals one of two regressions: (a) the boot-search formulations aren't surfacing drawers the session would cite — tune the formulation set in [`engine/memory/boot_surface.py`](../memory/boot_surface.py) (synonyms, similarity threshold, keyword-extraction heuristic; module relocated and renamed from `engine/tools/mempalace_boot_search.py` at the S-0192 cutover); (b) retrieved drawers ARE being surfaced but the AI isn't weaving them into authored artifacts — discipline issue, surface in the next pushback drawer.

### `health_check_overdue`

The cadence-aligned health-check audit slot has been consumed by other work and the audit slid past one full cadence. Active from S-0041 onward per [ADR 0022](../adr/0022-periodic-project-health-checks.md) Consequences amendment (overdue-catchup logic).

Fires when `(register_state.json.next_id - last_audit_session) > health_check_cadence`. The SessionStart hook (`engine/tools/hooks/session-start.sh`) surfaces both "due" (`slots_since == cadence`) and "overdue" (`slots_since > cadence`) at boot per the same amendment; this validator soft-warn is defense-in-depth so a silently-failing hook (the S-0033 / S-0034 vector pattern) cannot mask the slide. The validator stays silent at the natural-cadence slot — that case is the hook's "due" surface, not an overdue condition.

Skips quietly when `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041); the `checks_run` field still records the attempt so cross-session telemetry distinguishes "field absent" from "check did not run."

Recoverable — run `engine/tools/health_check.py --session S-NNNN` (the report-emit bumps `last_audit_session`, clearing both the hook surface and this soft-warn) or document explicit deferral in `outcome_summary`.

### `repo_config_health`

The shared-state probe at [`engine/tools/probe_repo.py`](../tools/probe_repo.py) reported a level-1 (suspect) condition. Active from S-0035 onward per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md). Currently no level-1 conditions are emitted (reserved for future calibration like dirty working tree or detached HEAD); all probe findings today reach hard-fail level.

The probe escalates to a **hard-fail** when `core.bare=true` is set on either the worktree's effective config or the parent clone's standalone `.git/config` (the S-0033 vector — masked by a worktree override but breaks parent-side boot operations like `merge --ff-only` and `push origin main`), or when HEAD does not resolve, or when basic `git rev-parse` queries fail.

Recoverable — the probe's stderr names the exact `git -C <repo> config --unset core.bare` command needed for the bare-misconfig case; HEAD-resolution failures are typically detached-HEAD or partial-checkout artifacts and are addressed by the appropriate `git checkout` or `git switch` operation.

### `issue_collision`

The Issue-collision scanner at [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) found one or more open GitHub Issues whose body or title contains either a keyword from this session's `declared_scope` (or fallback `working_on`) field in `current.json`, or a path from this commit's staged-files diff. Active from S-0042 onward per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

Each soft-warn body names the colliding Issue's number, title, and the matched keyword(s) or path(s). The signal is informational — non-blocking — surfaced so the AI can decide whether to (a) fix the colliding Issue first and reference it in the eventual commit, (b) work on it in parallel with the planned scope, or (c) proceed and trust the existing scope is independent of the Issue's named breakage.

**Filter for structurally-non-actionable Issues** (per S-0143 / [Issue #110](https://github.com/StarshipSuperjam/paideia/issues/110)): Issues carrying the `upstream` label (ADR 0048 cleanup-batch discipline says don't pick these up) and Issues whose titles match the trigger-gate marker pattern `[TRIGGER: <condition>]` (gated work whose external condition has not fired) are filtered out before collision matching. Both classes collided constantly in the pre-S-0143 corpus (median 22-23 collisions/commit; acted-on rate 1/19 across the S-0122 → S-0140 audit window) without producing acted-on signal. The persistent-warn annotation below remains in place to suppress the surface; the filter brings the volume down to a level where the annotation captures genuine baseline noise rather than habituated firehose.

A `gh` failure (no auth, no network, repo not on GitHub) silently skips the check; the scanner emits a stderr note and the validator records 0 collisions. The scanner-missing case (e.g., during `validate.py` migration) surfaces as a single soft-warn naming the missing path.

Recoverable per the choice the AI makes; the warn does not require resolution to commit.

### `empty_declared_scope`

A **routine-mode** session's `engine/session/current.json` is missing the `declared_scope` field or holds an empty string. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md); **mode-gated to routine sessions** at S-0125 per S-0121 audit Retire-F. The field is the routine-mode boot-time scope declaration: a 1-3 sentence statement of what the session commits to deliver, optionally including a `phase: <id>` token tying the work to a `build_plan/MANIFEST.md` identifier (or `phase: NA-...` for operational sessions).

The routine-mode eager-claim ritual writes this field at slot-claim time. The soft-warn fires every commit until the field is populated when the session is routine-mode.

Recoverable — open `engine/session/current.json`, add the `declared_scope` field with prose naming the session's deliverable. Skipped silently when `current.json` is absent (exploration mode) OR when the session declares any non-routine mode (interactive build sessions don't carry `declared_scope`; the field is a routine-mode contract surface per ADR 0049 §Routine-mode scope-lock).

### `phase_mismatch_declared_scope`

The `declared_scope` field contains a `phase:` token whose identifier doesn't appear in `build_plan/MANIFEST.md`. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). Catches the S-0037 reordering vector: a session declaring it's working on Phase 5 while the build-plan's next-due item is Phase 4.5 surfaces the mismatch at first-commit, before the session has authored anything substantive.

Matching is case-insensitive substring against the manifest text plus a heuristic token extraction (P_3, Phase 3, 3.0, 4.5, etc.). The literal prefix `NA` (e.g., `phase: NA-engine-apparatus`) is the explicit operational opt-out marker and skips the manifest match.

Recoverable — either correct the identifier to match the manifest, or replace it with `phase: NA-...` for operational/engine-apparatus work that doesn't map to a build-plan phase. If the session intends to reorder, update the build plan with explicit user-confirmed reorder before declaring scope on the new phase.

### `scope_delivery_non_yes`

A session's `engine/session/current.json` has `scope_delivery.delivered: false` at validator-run time. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The field is structured: `{delivered: bool, user_confirmed_changes: bool, explanation: str}`; the warn fires on `delivered: false` regardless of `user_confirmed_changes` because the warn is signal for cross-session aggregation, not punishment.

The shutdown audit step (added in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) per ADR 0049) prompts the AI with: *"Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?"* The structured answer goes into the field. The persistent-warn surface (per ADR 0042) escalates a 3-of-5 firing into the boot-time multi-session erosion signal in `session-start.sh`.

Recoverable — the warn is informational at the artifact level. The recoverable action is at the *next* session's planning: tighten scope, split the work, or address the systemic descoping-pressure pattern.

### `outcome_summary_unhandled_defer`

A session's `outcome_summary` contains hedge-pattern phrasing referring to deferred work, but `next_session_handle` is absent from the JSON entirely. Active from S-0100 onward per [ADR 0049 Decision 6 (S-0100 amendment)](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) / [Issue #54](https://github.com/StarshipSuperjam/paideia/issues/54). Closes Pushback Cluster A from the S-0097 audit.

Hedge regex set (case-insensitive, whitespace-tolerant; conservative starting set, expand if false negatives surface): `future session`, `next session will`, `correctable in any`, `preserved for manual review`, `picked up by`, `defer indefinitely`, `revisit when`. The shutdown step 10 prompt (added in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) per ADR 0049 Decision 6) explicitly asks the AI for the handle whenever hedge phrasing is being authored.

Recoverable — declare `next_session_handle` as one of: `"#<num>"` (Issue reference), `"S-<NNNN>"` (session reference), or explicit `null` (when the phrasing is intentional forward-pointer prose, not a deferral). The structured-field requirement anchors on a positive contract ("must declare the handle") rather than a negative one ("must not use these words"). False positives become "you forgot to declare" rather than "your prose tripped a regex."

### `next_session_handle_unknown_issue`

`next_session_handle` is `"#<num>"` but `gh issue view <num> --json state` reports the GitHub Issue does not exist (definitive `Could not resolve to an Issue` / `no issue or pr` stderr response). Active from S-0100 onward per [ADR 0049 Decision 6](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) / Issue #54. Diagnostic verification category — sibling to `outcome_summary_unhandled_defer`.

Verification is best-effort + offline-graceful: `gh` not installed, network failure, auth issues, timeouts all suppress the warn (don't false-positive). Only definitive "not found" responses fire. The validator stays usable offline; the warn catches typos and stale references when online.

Recoverable — fix the typo, file the missing Issue, or change the handle to `null` if the deferral is no longer applicable.

### `next_session_handle_unknown_session`

`next_session_handle` is `"S-<NNNN>"` but no archive exists at `engine/session/archive/S-<NNNN>.json` AND the session ID does not match the next-claim slot in `register_state.json` `next_id`. Active from S-0100 onward per [ADR 0049 Decision 6](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) / Issue #54.

A valid session handle references either an existing archived session OR the very next claim slot (so a session can promise "S-NNNN will pick this up" only if S-NNNN is imminent). Anything else fires.

Recoverable — fix the digit typo, point to an existing archive, declare the handle as the next-claim slot, or change to `null` if the session reference was speculative rather than committed.

### `next_session_handle_malformed`

`next_session_handle` is a non-null value that doesn't match either `^#\d+$` or `^S-\d{4}$`. Includes both string-but-wrong-shape (e.g., `"see-the-other-doc"`, `"S-99"` not 4-digit) and non-string non-null types (e.g., int, list, dict). Active from S-0100 onward per [ADR 0049 Decision 6](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) / Issue #54.

Note: shape errors at the JSON-type level (non-string non-null) ALSO trigger `audit_archive_structured_fields.py`'s hard-fail at closing-commit time via the `str_or_null` shape check. The soft-warn here is the in-flight surface during the session — it fires under `validate.py --final-check` before the archive ritual. The hard-fail catches the same case at the audit-archive layer as defense-in-depth.

Recoverable — change the value to one of the three valid forms (`"#<num>"`, `"S-<NNNN>"`, or `null`), or remove the hedge-pattern phrasing from `outcome_summary` if the prose was unintentional.

### `state_md_row_count`

Per [ADR 0062](../adr/0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) (S-0126; Issue #87). Fires when `engine/STATE.md` exceeds `STATE_MD_ROW_COUNT_THRESHOLD` (default 180; baseline at S-0126 was 118 rows). STATE.md committed at S-0121 to a scope-discipline preamble (present-state only); per-session prose belongs in `engine/session/archive/S-NNNN.json` + `engine/changelog/<YYYY>/S-NNNN-*.md`.

Recoverable: trim the file per the preamble's guidance. If the row count exceeds the threshold for legitimate reasons (additions to the SWE-hardening rollout section, new audit-tracking subsections, etc.), bump `STATE_MD_ROW_COUNT_THRESHOLD` in `validate.py` with evidence in the commit.

### `adr_consequences_amendment_header`

Per [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) + [ADR 0062](../adr/0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) (S-0126; Issue #87). Zero-tolerance pattern catch — fires on any `### Amendment` header in any `engine/adr/*.md` or `product/adr/*.md` file. ADR body content is present-truth declarative; authorship history belongs in `engine/changelog/<YYYY>/S-NNNN-*.md` entries / engine_memory `decisions`-room drawers / git, not in ADR body.

Recoverable: fold the amendment substance into the body as present-truth (refining contract clauses, deleting blocks whose substance lives in tool docstrings / engine/changelog/ entries / git), then delete the `### Amendment` header.

### `handoff_long_resolved_sections`

Per [ADR 0062](../adr/0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) (S-0126; Issue #87). Fires under two conditions: (1) total `**Resolved:**` section count exceeds `HANDOFF_RESOLVED_COUNT_THRESHOLD` (default 5); (2) any single resolved section's `S-NNNN` is more than `HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS` (default 10) older than the current session. HANDOFF.md's preamble commits to prune-on-resolve at the next interactive session that touches HANDOFF; this soft-warn is the gate-time backstop.

Recoverable: prune resolved sections per the preamble's discipline (content preserved in git history; each section's `**Resolved:**` line names the downstream artifact). If a resolved section is intentionally retained as a load-bearing reference, move its content elsewhere (a per-session changelog entry, an ops doc, the relevant ADR) and prune the HANDOFF entry.

### `validator_runtime_phase_regression`

Per [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) (S-0126; four-phase model from S-0127 Issue #90; HISTORY_FILE pinning from S-0205 Issue #150). Fires when any one of the four validator phases (`duration_structural_ms`, `duration_health_probe_ms`, `duration_graph_audit_ms`, `duration_total_ms`) exceeds 1.5× its tiered target (500ms / 5000ms / 5000ms / 11000ms) across the last 3 consecutive runs in `engine/tools/validate-history.jsonl` (the current run participates in the rolling window). Pre-S-0126 entries that carry only `duration_ms` and pre-S-0127 entries that carry the three-field schema are skipped (insufficient per-phase fields).

**HISTORY_FILE resolution** — the JSONL log lives at the canonical main-repo path resolved via `_resolve_canonical_history_path()` in `validate.py`: `git rev-parse --git-common-dir` returns `<main-repo>/.git` from any worktree or the main repo itself, and the canonical history is `<main-repo>/engine/tools/validate-history.jsonl`. All worktrees + the main repo write to the same shared file, so the regression check sees a single time-series of runs across the project's actual validate activity. Falls back to per-clone path on subprocess failure (covers test harnesses, tarball extractions). Pre-S-0205 per-worktree files are abandoned in place (gitignored, harmless). Concurrent appends are atomic under POSIX (records ~500 bytes, well under PIPE_BUF 4KB).

Recoverable: investigate the offending phase's hot path (which subcheck regressed?). If the phase boundary itself is wrong (a slow concern misclassified into the wrong phase), correct it — the S-0126 first-fire was resolved this way at S-0127 by extracting `validate_shared_state_health` from the structural phase into its own `health_probe` phase. If the steady-state has legitimately shifted (new infrastructure raised a baseline, or live-DB load varies), adjust `VALIDATOR_PHASE_TARGETS_MS` in `validate.py` with evidence in the commit.

### `uv_lock_out_of_date`

Per [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) (S-0127; Issue #65). Fires when `uv lock --check` (run from the repo root) exits non-zero — i.e., `uv.lock` does not match `pyproject.toml`'s declared dependency surface. Three no-op cases preserve clean exits when the contract isn't installed: missing `pyproject.toml`, missing `uv.lock`, missing `uv` binary.

Recoverable: from the repo root, run `uv lock` to regenerate the lockfile, then `uv sync` to align the local venv, then stage `pyproject.toml` and `uv.lock` together in the same commit. Refresh procedure: [`dependency-discipline.md`](dependency-discipline.md).

The check runs in the `health_probe` phase per ADR 0063 (subprocess to `uv`).

The soft-warn is intentionally per-session-resolvable — every fire indicates a missing `uv lock` step. Persistent firing across 10 sessions per `soft-warn-lifecycle.md` reaches the escalation criterion as either: (a) the dep change should be reverted; (b) the lockfile-regeneration step should be CI-automated.

### `timestamp_helper_bypass`

A `Call` node in `engine/tools/**/*.py` (excluding `test_*.py` and the four allowlisted files) invokes `.isoformat(...)`, `.strftime(...)`, or `.fromisoformat(...)` directly. Per [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md) + [`timestamp-discipline.md`](timestamp-discipline.md), all timestamp emission and parsing in the engine subtree routes through `engine/tools/timestamps.py` (`emit` / `emit_micros` / `parse` / `today`) so format knowledge concentrates in one place.

Recoverable: replace the bare call with the appropriate helper function, or — if the site has a legitimate non-canonical contract — add the file to `_TIMESTAMP_HELPER_BYPASS_ALLOWLIST` in `validate.py` with an inline comment naming what the helper would break if applied. The current allowlist entries (`apply_migration.py`, `probe_push_gate.py`, `scan_engine_memory_citations.py`) document the contract pattern; a fourth entry `audit_mempalace_attribution.py` retired at S-0193 per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) cutover (the tool no longer exists on disk).

Persistent firing across multiple sessions per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md)'s 3-of-5-archives surface signals new ad-hoc emission slipping in — investigate the offending file and either route through the helper or extend the allowlist with rationale.

### `skill_layer1_parity_drift`

Per [ADR 0089](../adr/0089-skill-layer1-parity-validator-check.md) (S-0163; [Issue #129](https://github.com/StarshipSuperjam/paideia/issues/129)). Fires when a recipe Skill's procedure step-number *set* diverges from its Layer-1 ops doc's — a step present on one side and absent from the other. Covers the four recipe Skill ↔ doc pairs (`routine-mode-lifecycle`, `session-build-lifecycle`, `session-shutdown-sequence`, `build-readiness-gate`); config is the `_SKILL_LAYER1_PAIRS` tuple in `validate.py`. One soft-warn per drifting pair, plus one per missing file / unlocatable section / empty section (the check self-reports its own parsing failure rather than going silent). Compares step numbers, not titles — skill voice and reference voice legitimately differ in wording per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md). Scope limit: catches enumeration drift only, not intra-step content drift (a step's prose drifting, or a step omitting required fields) — that remains hand-discipline per the ADR 0044 Consequences amendment.

Recoverable: reconcile the drifting pair — bring the Skill and its Layer-1 doc to the same step set (updates flow doc → skill). If the divergence is a section-heading or step-grammar change rather than genuine drift, update the `_SKILL_LAYER1_PAIRS` config in `validate.py` to match the new structure.

### Graph-audit soft-warns (S-0037 onward, active when SUPABASE_DB_URL is set)

The ten categories the validator extends from ADR 0016's contract (seven from S-0037; three added at S-0146 from the S-0122 audit's gate-feasible recommendations per [Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62) + [`engine/build_readiness/phase_5_audit_system_input.md`](../build_readiness/phase_5_audit_system_input.md)). All ten register in `checks_run` even when zero findings fire, so cross-session telemetry distinguishes "category clean" from "category did not run" (the schema convention at [`session-shutdown-sequence.md`](session-shutdown-sequence.md)).

- `undeclared_predicate` — edge.type not in `product/seed-graph/migrations/PREDICATE_MANIFEST.md`. Recoverable: add the row to the registry in the same session that uses the predicate, paired with a per-session changelog entry naming the schema-class addition. Per [`seed-chunked-authoring.md`](seed-chunked-authoring.md) step 5.
- `attribute_shape_inconsistency` — same-domain nodes with materially different attribute coverage. v1 metric: `teaching_notes` populated-vs-NULL split with the minority class above 30% within a domain tag. Phase 5 calibration is a [`engine/build_readiness/phase_4_graph_validation.md`](../build_readiness/phase_4_graph_validation.md) T3-C deferral.
- `missing_rigor_score` — node carries inbound `pedagogical_prerequisite` edges and `rigor_score_computed` is at the schema default `0.5` (per [`product/seed-graph/migrations/0002_nodes.sql`](../../product/seed-graph/migrations/0002_nodes.sql)). The architecture.md formula expects topology data; the warn fires on "could be computed but wasn't."
- `render_readiness_violation` — node label contains a scaffolding token (`service_node`, `synthetic`, `stub`). Per [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) applied to label authoring; recoverable by renaming the node before commit.
- `synthetic_review_queue` — node has `confidence_level = 'SYNTHETIC'` per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md). Not a defect — populates the Opus batch review consumer per [`product/docs/self-correction.md`](../../product/docs/self-correction.md).
- `orphan_leaf` — zero inbound + zero outbound `pedagogical_prerequisite` edges (other edge types do not count toward in/out degree for this category). Recoverable when downstream subdomains add edges that reach the leaf, or by re-evaluating whether the node belongs at the granularity principle.
- `suspicious_cross_domain_ratio` — subdomain (single domain tag) where >40% of inbound `pedagogical_prerequisite` edges originate from nodes carrying no overlap with that domain tag. Likely a missing service node on the inside of the subdomain; recoverable by introducing the service node and re-routing the cross-domain edges through it.
- `edge_evidence_empty` (S-0146 per Issue #62 Proposal 1) — cross-domain `pedagogical_prerequisite` edge with NULL or empty `evidence` field. Cross-bridges only — within-subdomain edges run cleaner and their pedagogical justification is often implicit in the parent migration's narrative. Recoverable by populating `evidence` with the migration's `teaching_notes` pedagogical-warrant prose at authoring time. Backfill of pre-S-0146 cross-bridges is a separate cleanup pass (likely scope of a future structural-reopen migration).
- `top_level_discipline_label_as_prereq_source` (S-0146 per Issue #62 Proposal 2b) — node whose label is a canonical top-level discipline name (`philosophy_of_language`, `philosophy_of_science`, `philosophy_of_mind`, `political_philosophy`, `metaethics`, `epistemology`, `metaphysics`, `ethics`, `logic`, `aesthetics` — see `TOP_LEVEL_DISCIPLINE_LABELS` in `validate.py`) AND that node sources ≥3 prereq edges AND those edges' targets span ≥2 distinct domains. The umbrella-as-prereq-source shape per the audit's findings (philosophy_of_science N-5/E-2/E-3, political_philosophy N-5/E-11). Fix posture: retain-with-explicit-umbrella-semantics — record the umbrella framing in the node's `teaching_notes`. New top-level discipline nodes added in Phase 6 self-correction trigger this check at validate-time.
- `prereq_direction_summary_inconsistency` (S-0146 per Issue #62 Proposal 3+5 merged) — cross-domain `pedagogical_prerequisite` edge whose target.summary contains a structural sentence of shape `<target.label> is/are ...<connecting-phrase>... <source.label>` where the connecting phrase signals broader-category / content-of / property-of / class-of semantics (see `DIRECTION_REVERSAL_PHRASES` in `validate.py`). Phrase list anchored on the audit's 5 documented cross-bridge reversals (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70). Recoverable by flipping the edge direction or revising the structural prose if the authored direction is correct; the dual-mode resolution is intentional — the warn surfaces a contradiction, not a unilateral defect. Phrase-pattern false-positive rate calibrates over Phase 6; promotion to LLM-flagged is a deferred enhancement.

## Response posture

- **A soft-warn that recurs across multiple sessions** — formalized into a discipline per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). The boot-time persistent-warn surface flags categories firing in 3-or-more of the last 5 archives; categories firing in 10 consecutive archives reach the escalation criterion (promote to hard-fail, accept and annotate, or address inline) per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md).
- **A new hard-fail in CI on a commit that passed locally** — clock skew on `validate-history.jsonl` writes is fine to ignore; everything else is a real divergence to investigate.
- **Validator runtime budgets** — per [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) the tiered targets are: structural phase < 500ms (in-process file/regex checks; no DB, no subprocess), health-probe phase < 5s (external-subprocess probes: chromadb open via `probe_palace.py`, repo state via `probe_repo.py`, GitHub Issues via `gh issue list`), graph audit phase < 5s (live-DB consultation per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md)), total runtime < 11s. The `validator_runtime_phase_regression` soft-warn fires when any phase exceeds 1.5× its target across 3 consecutive runs. Investigate the phase's hot path on the soft-warn, correct the phase boundary if a concern is misclassified, or — with evidence the steady-state has shifted legitimately — adjust the target in `VALIDATOR_PHASE_TARGETS_MS`.

## Validator-pipeline classification map

Every soft-warn category emitted by `engine/tools/validate.py` lands in exactly one of five buckets per the S-0101 sweep (Issue #52 — closes Non-obvious finding A from the S-0097 audit). The buckets are:

- **Actively-tracked (default)** — drift detector working as intended; per-fire action expected when the warn is non-trivial. Includes both categories that fire periodically (e.g., `adr_consequences_deliverable_audit` surfaces real ADR cleanup work) and silent guards that protect structural invariants (e.g., `cross_reference_broken` rarely fires because the project keeps cross-references current; the absence of fire is the system working).
- **Persistent-warn annotation** — fires structurally under named conditions documented in this file's "Persistent-warn annotation" section; boot surface suppresses for matching sessions per the [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md) annotation pattern.
- **Informational-only-accepted** — fires by design; passive observability serves audit-time aggregation; per-session action not expected. Documented per category in the "Informational-only-accepted classifications" section.
- **Actively-tracked, deferred re-audit** — added to the validator within the last ~5 archives; insufficient telemetry coverage to compute a stable fire-rate. Re-classify at the next cadence-fired audit (S-0117 projected). Documented per category in the "Actively-tracked, deferred re-audit" sub-section.
- **Retire-candidate (flagged for next audit)** — fires 0 times in the cadence-20 window AND ≤1 time in the full archive corpus AND no documented structural-invariant role. Routes through user adjudication at the next health-check audit per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) user-buffered execution. Documented per category in the "Retire candidates flagged for next health-check audit" sub-section.

**Re-run methodology** (the next cadence audit reproduces this sweep):

```bash
# Enumerate static-emission categories
grep -oE 'r\.soft_warn\(\s*"[a-z_][a-z0-9_]*"' engine/tools/validate.py | \
  grep -oE '"[a-z_][a-z0-9_]*"' | tr -d '"' | sort -u
# Add dynamic-emission categories (probe loop at validate.py:687):
#   chromadb_palace_health, repo_config_health
```

```python
# Fire-rate per category over the cadence-20 window (S-NNNN-19 → S-NNNN, exclusive of audit slot)
import json, glob
files = sorted(glob.glob('engine/session/archive/S-*.json'))[-20:]
def fire_rate(category):
    return sum(1 for f in files
               if (json.load(open(f)).get('outcome_summary_soft_warns') or {}).get(category, 0))
```

```bash
# Acted-on rate per category (commits that name the category since the cadence-window's start date)
git log --since=YYYY-MM-DD --grep=<category> --oneline | wc -l
```

The since-date matches the calendar span of the cadence-20 window. The `git log --grep` proxy captures both `Closes #NN` references and direct mentions in commit messages; imperfect but adequate signal at the audit-aggregate level.

**Threshold matrix** (calibration baseline, S-0101; tune at S-0117 if friction surfaces):

| Bucket | Predicate |
|---|---|
| **Actively-tracked (default)** | Fired ≥1 in window AND has ≥1 commit-references; OR fired 0 in window AND guards a structural invariant the validator pipeline must check |
| **Persistent-warn annotation** | Fires structurally under named conditions; resolution condition documented; boot surface suppresses for matching sessions |
| **Informational-only-accepted** | Fired ≥3 in last 5 archives AND acted-on rate ≤2 commits in window — passive observability without per-fire action expected |
| **Actively-tracked, deferred re-audit** | Added to validator within last 5 archives — re-classify at next cadence audit once ≥10 archives accumulate |
| **Retire-candidate (flagged)** | Fired 0/20 AND ≤1/100 AND no documented structural-invariant role |

**Classification table — S-0101 sweep against the cadence-20 window (S-0081 → S-0100), git log since 2026-04-25:**

| Category | Bucket | Fire/20 | Fire/100 | Commits | Invariant guarded / role |
|---|---|---|---|---|---|
| `missing_rigor_score` | Persistent-warn annotation (S-0077) | 20 | 51 | 31 | Phase 5 partial-seed pattern; Phase 6 rigor-calibration resolves |
| `issue_collision` | Persistent-warn annotation (S-0077) | 17 | 51 | 33 | Open-Issue keyword overlap defense; ADR 0048 broad-keyword design |
| `health_check_overdue` | Persistent-warn annotation (S-0077) | 10 | 17 | 22 | Cadence-trigger defense-in-depth; clears at audit close |
| `engine_memory_diary_read_skipped` | Informational-only-accepted (S-0098) | 5 | 5 | 2 | engine-memory adoption observability per ADR 0091 |
| `engine_memory_boot_query_skipped` | Informational-only-accepted (S-0098) | 4 | 4 | 3 | engine-memory adoption observability per ADR 0091 |
| `adr_consequences_deliverable_audit` | Actively-tracked | 15 | 16 | 14 | Surfaces stale ADR Consequences-section deliverable promises per [ADR 0041](../adr/0041-cascade-analysis-discipline.md) cascade discipline; high acted-on rate |
| `engine_memory_diary_write_acknowledged_skip` | Actively-tracked | 2 | 2 | 2 | Substrate-unavailable acknowledged sessions per ADR 0056 escape hatch |
| `empty_declared_scope` | Actively-tracked | 1 | 1 | 6 | ADR 0049 Decision 6 — eager-claim ritual must write `declared_scope` as 1-3 sentence string |
| `adr_back_reference_orphan` | Actively-tracked | 0 | 1 | 4 | Cascade discipline — ADR back-reference orphans per ADR 0041 |
| `routine_issue_spam` | Actively-tracked | 0 | 1 | 1 | Routine-mode anti-pattern per ADR 0051 |
| `adr_index_inconsistent` | Actively-tracked | 0 | 0 | 2 | `adr/README.md` index sync vs file system |
| `adr_missing_status` | Actively-tracked | 0 | 0 | 1 | ADR Status field per [`adr-authoring.md`](adr-authoring.md) |
| `attribute_shape_inconsistency` | Actively-tracked | 0 | 0 | 1 | Phase 4+ graph audit per ADR 0016 |
| `chromadb_palace_health` | Actively-tracked (dynamic) | 0 | 0 | 0 | Palace-probe failure path per ADR 0045; emitted via probe loop at `validate.py:687` |
| `cross_reference_broken` | Actively-tracked | 0 | 0 | 6 | Cross-reference integrity in `docs/CROSS_REFERENCES.md` |
| `engine_log_format` | Retired (S-0198 per ADR 0092) | — | — | — | Retired with the monolithic ENGINE_LOG.md; per-session entries validated by `changelog_entry_*` checks |
| `expected_future_file_missing` | Actively-tracked | 0 | 0 | 0 | Phase-staged file expectations per `EXPECTED_FROM_S0002` |
| `engine_memory_diary_write_skipped_routine` | Actively-tracked | 0 | 0 | 3 | Routine-mode no-token-no-diary soft-warn per S-0091 routine-protection |
| `mempalace_diary_write_skipped_substrate_intermittent` | Actively-tracked | 0 | 0 | 1 | Substrate-down contradiction case per ADR 0056 amendment (S-0089) |
| `mempalace_hnsw_divergence` | Actively-tracked | 0 | 0 | 2 | Palace HNSW vs SQLite divergence per ADR 0045 amendment (S-0084) |
| `mempalace_quarantine_accumulation` | Actively-tracked | 0 | 0 | 0 | `.drift-*` / `.corrupt-*` accumulation under palace root (S-0153, corroborating MemPalace/mempalace#1489) |
| `mempalace_retired_surface_used` | Actively-tracked | 0 | 0 | 3 | KG / tunnels usage defense per S-0087 retirement |
| `mempalace_substrate_at_close` | Actively-tracked | 0 | 0 | 2 | Substrate-down at close defense per ADR 0056 amendment (S-0089) |
| `mempalace_wing_count_growth` | Actively-tracked | 0 | 0 | 4 | Wing accumulation per Issue #46 (S-0088) |
| `engine_memory_zero_citations_after_search` | Actively-tracked | 0 | 0 | 3 | Closed-loop boot-search effectiveness per ADR 0056 amendment (S-0093) |
| `orphan_leaf` | Actively-tracked | 0 | 0 | 1 | Phase 4+ graph audit — zero-degree pedagogical_prerequisite nodes (the lone fire, `phenomenology`, resolved at S-0155 via migration 0065) |
| `phase_mismatch_declared_scope` | Actively-tracked | 0 | 0 | 1 | declared_scope phase-token vs `build_plan/MANIFEST.md` per ADR 0049 |
| `render_readiness_violation` | Actively-tracked | 0 | 0 | 1 | Phase 4+ graph audit — scaffolding tokens in node labels |
| `repo_config_health` | Actively-tracked (dynamic) | 0 | 0 | 1 | Repo-probe failure path per ADR 0045; emitted via probe loop at `validate.py:687` |
| `routine_no_target_reference` | Actively-tracked | 0 | 0 | 0 | Routine-mode T- token check per ADR 0051 |
| `scope_delivery_non_yes` | Actively-tracked | 0 | 0 | 2 | ADR 0049 scope-delivery shape check |
| `state_format` | Actively-tracked | 0 | 0 | 0 | "Current phase" field presence in STATE.md |
| `superseded_adr_currency` | Actively-tracked | 0 | 0 | 3 | Cascade discipline — superseded-ADR citation currency per ADR 0041 |
| `suspicious_cross_domain_ratio` | Actively-tracked | 0 | 0 | 2 | Phase 4+ graph audit — cross-domain inbound edge ratio threshold |
| `synthetic_review_queue` | Actively-tracked | 0 | 0 | 1 | `confidence_level: SYNTHETIC` review-queue surface per ADR 0030 |
| `undeclared_predicate` | Actively-tracked | 0 | 0 | 1 | Phase 4+ graph audit — edge.type vs PREDICATE_MANIFEST.md |
| `timestamp_helper_bypass` | Actively-tracked, deferred (S-0095) | 0 | 0 | 8 | Canonical timestamp helper per ADR 0058; AST-walk soft-warn (the 2 `scan_dependabot_prs.py` baseline sites allowlisted at S-0155 — see deferred-re-audit note below) |
| `outcome_summary_unhandled_defer` | Actively-tracked, deferred (S-0100) | 0 | 0 | 3 | ADR 0049 Decision 6 — outcome_summary hedge-pattern + missing handle |
| `next_session_handle_unknown_issue` | Actively-tracked, deferred (S-0100) | 0 | 0 | 2 | ADR 0049 Decision 6 — handle references unknown Issue |
| `next_session_handle_unknown_session` | Actively-tracked, deferred (S-0100) | 0 | 0 | 2 | ADR 0049 Decision 6 — handle references unknown session |
| `next_session_handle_malformed` | Actively-tracked, deferred (S-0100) | 0 | 0 | 2 | ADR 0049 Decision 6 — handle malformed (not `#NN` or `S-NNNN`) |
| `validator_runtime_phase_regression` | Actively-tracked, deferred (S-0126) | 0 | 0 | 1 | Per-phase runtime regression per ADR 0063 four-phase model (S-0127 fold) |
| `uv_lock_out_of_date` | Actively-tracked, deferred (S-0127) | 0 | 0 | 0 | uv.lock vs pyproject.toml staleness per ADR 0064 |
| `dependabot_pr_stale` | Actively-tracked, deferred (S-0147) | 0 | 0 | 0 | Open Dependabot PR aged ≥ 7 days per ADR 0080 (engine); one fire per stale PR |
| `engine_memory_boot_query_late` | Actively-tracked, deferred (S-0160) | 0 | 0 | 0 | Boot `engine_memory_search` ran after `started_at` per Issue #124 — timing counterpart to `engine_memory_boot_query_skipped` |
| `engine_memory_diary_read_late` | Actively-tracked, deferred (S-0160) | 0 | 0 | 0 | Boot `engine_memory_diary_read` ran after `started_at` per Issue #124 — timing counterpart to `engine_memory_diary_read_skipped` |

**Coverage check:** 44 rows above; 42 static-emission category strings (per `grep -oE 'r\.soft_warn\(\s*"[a-z_]+"' engine/tools/validate.py | sort -u`) plus 2 dynamic-emission categories (`chromadb_palace_health`, `repo_config_health`) emitted from the probe loop at `validate.py:687`. Two ghost keys appear in some historical archives (`graph_audit_skipped` is an `add_check` not a `soft_warn`; `engine_memory_diary_write_skipped` is a hard-fail not a soft-warn) — both excluded from this map by design.

**Concordance check (per S-0101 plan verification step 2):** the 3 S-0077 persistent-warn annotations and 2 S-0098 informational-only classifications survive the new threshold matrix unchanged. No category flipped relative to its prior assignment.

**Retire-candidate finding:** zero categories meet the retire-candidate predicate. Every silent category guards an identifiable structural invariant in the current pipeline (cascade discipline, graph audit, engine-memory adoption, ADR-routing, cross-reference integrity, format checks, routine-mode protocol). The "Retire candidates flagged for next health-check audit" section below is therefore intentionally empty at this sweep.

## Informational-only-accepted classifications

Some soft-warn categories are documented as "fires by design and the user does not act on each fire" — distinct from the persistent-warn annotation pattern below (which is about expected-firing-under-named-conditions). An informational-only-accepted category fires whenever its predicate matches; the signal serves passive observability or trend-watching at audit time but does not require per-fire action.

The classification is documented per category in this section so the validator's pipeline visibly distinguishes intent. Re-classification routes through user adjudication at health-check audits; the audit's "Affirmative retire candidates" section is the canonical surface where re-classification is proposed and adjudicated.

The first two classifications land at the S-0098 adjudication of S-0097's audit (per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) Retire candidate B). At audit-window-acted-on rates of 1 commit and 2 commits respectively across S-0078 → S-0096 (despite firing in 5 and 4 archives), the two MemPalace-skip categories below were near-zero-acted-on; the user adjudicated re-classify-not-retire to preserve the passive-observability signal that some sessions don't query MemPalace at boot or read the diary, while clarifying that no per-fire action is required.

The S-0101 systematic sweep (per the classification map above) added no further categories to this bucket. The remaining audit-window-firing categories (`adr_consequences_deliverable_audit`, `engine_memory_diary_write_acknowledged_skip`, `empty_declared_scope`) carry acted-on rates that confirm them as actively-tracked rather than informational-only.

### `engine_memory_boot_query_skipped` (informational-only-accepted, S-0098)

**Why classified informational-only:** the category surfaces a engine-memory adoption gap (no `engine_memory_search` call in the session) for cross-session trend visibility. Per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) the warn ships to make adoption observable; the warn's value is in audit-time aggregation across N sessions rather than mid-session correction. Individual sessions that legitimately do no engine-memory boot search (rare maintenance work, short hot-fix sessions) leave the warn intact without triggering remediation.

**What still warrants action:** persistent firing across 3-of-5 sessions per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) is the audit-time surface that asks whether the boot-search apparatus is delivering enough value to be exercised. Cross-reference with `engine_memory_zero_citations_after_search` to distinguish "boot search not happening" from "boot search happening but not informing the work."

### `engine_memory_diary_read_skipped` (informational-only-accepted, S-0098)

**Why classified informational-only:** sibling to `engine_memory_boot_query_skipped`. The category surfaces a engine-memory adoption gap (no `engine_memory_diary_read` call) for cross-session trend visibility. Same passive-observability rationale per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md). The diary-read skip is correctable in-session by invoking `engine_memory_diary_read` once via the MCP tool with `agent_name="claude" last_n=3`, but the absence of the call within a single session is not a per-session-action signal.

**What still warrants action:** persistent firing across 3-of-5 sessions per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) is the audit-time surface. Combined persistent firing with `engine_memory_boot_query_skipped` is signal that the project's engine-memory consumption discipline (boot-search + diary-read at session start) is structurally lapsing rather than per-session lapsing. **Boot-surface note (S-0196):** also annotated below for boot-surface suppression per [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133) — the per-boot recurrence saturated the alert lane; the cadence-fired audit retains the longer-window view.

## Persistent-warn annotation

When the escalation criterion ([`soft-warn-lifecycle.md`](soft-warn-lifecycle.md), 10 consecutive archives) lands on "accept and annotate," the category gets an entry below explaining why the persistence is expected and what condition would resolve it. The boot surface respects the annotation by suppressing the surface for sessions that match the named condition.

The first three annotations land at the S-0077 audit (`docs/health-checks/S-0077.md` Fit section). Prior audits (S-0052, S-0065) referenced "annotated as expected per phase_5.md T2-C / scope breadth" in audit prose, but the canonical home below was empty — the annotations were conceptual rather than persisted in the document the boot-time persistent-warn surface actually reads. The S-0077 audit's reading of "the structured-data window has matured" trigger fired with three categories crossing the persistence threshold across multiple windows.

### `health_check_overdue` (annotated S-0077)

**Expected when:** at any session boot whose `last_audit_session` is more than `health_check_cadence` slots back (i.e., the trigger has fired but the audit hasn't been accepted yet — see [`health-check.md`](health-check.md) cadence-trigger logic).

**Resolution condition:** clears the moment `engine/tools/health_check.py --session S-NNNN` runs at audit close (the report-emit bumps `last_audit_session` and the next boot's hook + this validator both see `slots_since == 0`).

**Why annotated rather than addressed:** the soft-warn is the cadence-trigger's defense-in-depth (per the same hook silently failing — the S-0033/S-0034 vector pattern). It's structurally expected to fire whenever the user defers an audit through one or more sessions; promoting to hard-fail would block any session that overlaps the cadence window. The persistent-warn surface should suppress this category for the session that *is* the audit (the audit's own commits will fire it once before health_check.py bumps the field; this is correct).

### `issue_collision` (annotated S-0077)

**Expected when:** the session's `declared_scope` (or fallback `working_on`) and/or staged-files diff contains keywords or paths that broad-scope open Issues mention. The intentionally-broad keyword match in [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) catches scope-overlap risk so the AI can decide whether to fix-the-issue-first, work-in-parallel, or trust-independent-scope. Routine-mode sessions in particular fire this consistently because routine work has narrow paths but broad operational keywords (`session`, `start-engine`, `validate`, `routine-mode`, `boot`, etc.) that cross-cut most open Issues.

**Resolution condition:** declines naturally as the open-Issues backlog clears (cleanup-batch sessions) or as Issues are filed with narrower keyword surfaces. Does not require resolution to commit; the warn is informational by design per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

**Why annotated rather than addressed:** the warn's intentional broadness is the design choice from ADR 0048 — narrowing the keyword scanner would defeat the purpose (it's defense against "AI didn't realize the same concern was already filed"). The persistent-warn surface should suppress this category for build sessions that exhibit `issue_collision >= 5` with no >7 spike.

### `missing_rigor_score` (annotated S-0077)

**Expected when:** during phases that author concept nodes faster than the rigor-backfill cadence — Phase 5 partial-seed shape per [`engine/build_readiness/phase_5.md`](../build_readiness/phase_5.md) T2-C established the pattern; Phase 6 self-correction per [`product/docs/self-correction.md`](../../product/docs/self-correction.md) is the resolution surface.

**Resolution condition:** the Phase 6 self-correction backlog counter (per the Phase 5 closeout's "Forward pointers to Phase 6+" rigor-calibration deliverable) drains as Phase 6 routine sessions backfill `rigor_score_computed` against topology-bearing nodes. Does not require resolution to commit; structural per the architecture.md formula's expectation that topology data feeds the rigor score.

**Why annotated rather than addressed:** addressing in Phase 5 was the wrong shape — the rigor score depends on neighborhood structure (inbound edges), and partial seeds during phase build-up genuinely cannot compute the score reliably. The Phase 5 closeout deferred the calibration to Phase 6 as a pre-decided architectural choice, not a slip.

### `edge_evidence_empty` (annotated S-0196)

**Expected when:** `SUPABASE_DB_URL` is set and the graph audit runs against the production seed. The category fires at high baseline against the existing ~71 NULL-evidence cross-bridges documented in the S-0122 production audit. Routine-mode work that does not author new cross-bridges does not reduce the baseline.

**Resolution condition:** Phase 6 self-correction backfills the missing `evidence` payloads as part of the cross-bridge-fortification work plan (the same surface that drains `missing_rigor_score`). When the audit-documented cross-bridges acquire evidence rows, the per-session firing count drops to whatever new authoring introduces.

**Why annotated rather than addressed:** the S-0146 introduction (per [Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62) Proposal 1) shipped as deferred-re-audit pending ≥10 archives of post-introduction telemetry. The S-0184 cadence audit (≥10 archives accumulated) confirmed steady-state high baseline; Phase 6 backfill is the resolution surface and Phase 6 has not opened. Cross-reference: the deferred-re-audit entry below preserves the introduction context; this annotation is the boot-surface suppression hook landed via [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133) at S-0196.

### `engine_memory_diary_read_skipped` (annotated S-0196)

**Expected when:** any session whose boot procedure does not invoke `engine_memory_diary_read`. Per S-0098 the category is classified `informational-only-accepted` — fires by design when a session legitimately skips the diary read (short hot-fix sessions, mid-session resumption from a prior interactive context, audit-only sessions) and the audit-time signal lives in cross-session aggregation, not per-session correction.

**Resolution condition:** does not require resolution to commit. The signal is consumed by the cadence-fired audit's review of structured archive data — a sustained gap between session count and diary-read count over N sessions is the actionable shape, not the per-session fire.

**Why annotated rather than addressed:** the boot surface was burying genuinely-action-needed alerts under per-boot recurrence of this category through S-0184 → S-0196 (3-of-5 firings in every window). The annotation suppresses the boot surface so the cadence-fired audit (which consumes the same archive data with a longer window) remains the audit-time signal — preserves the design intent without saturating the alert lane. Cross-reference: the `informational-only-accepted` entry above preserves the per-fire interpretation; this annotation is the boot-surface suppression hook landed via [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133) at S-0196.

## Actively-tracked, deferred re-audit

Categories added to the validator within the last ~5 archives carry insufficient telemetry coverage for a stable fire-rate computation. Per the S-0101 sweep, they are recorded here as actively-tracked with re-audit deferred to the next cadence-fired audit (S-0117 projected) — by which point ≥10 archives of post-introduction telemetry will be available and the threshold matrix can re-evaluate without false-negative bias.

Until re-audit, the categories carry their as-shipped semantics from their introducing ADR / Issue. Sessions act on each fire per the per-category guidance in the "Soft-warns (signal, not blocker)" section above. The deferred-re-audit status only constrains the *re-classification* decision, not the per-fire response.

### `timestamp_helper_bypass` (deferred re-audit; introduced S-0095)

**Why deferred:** introduced at S-0095 per [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md). The 5-archive coverage at S-0101 (S-0096 → S-0100) shows zero fires — but the AST-walk that detects bypass patterns may not be exercising any code paths in routine cleanup-batch sessions. Routine-mode Phase 5 sessions or new-tool-authoring sessions are likelier triggers; without those in the window, classification can't distinguish "guard works correctly" from "guard never runs against the relevant code path."

**Re-audit at S-0117** once the window includes at least one routine-batch session OR a new-tool-authoring session.

**Resolved at S-0155.** The guard works correctly: it caught two genuine bypass sites in `scan_dependabot_prs.py` (`age_days`'s `fromisoformat` parse + `--simulate-age`'s `isoformat` emit) — `scan_dependabot_prs.py` is the new-tool case (ADR 0080, S-0147) the re-audit pointer was waiting for. Both sites parse/emit gh's external wire format, not engine-canonical stored timestamps, so routing through `timestamps.py` would impose the wrong format; the file was added to `_TIMESTAMP_HELPER_BYPASS_ALLOWLIST` with inline ADR 0058 justification at each site (the same disposition as the four prior allowlist entries). The `timestamp_helper_bypass: 2` baseline carryover is cleared. The category remains actively-tracked for future ad-hoc emission.

### `outcome_summary_unhandled_defer` (deferred re-audit; introduced S-0100)

**Why deferred:** introduced at S-0100 per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) Decision 6 (Issue #54). Gated to `--final-check`; fires when `outcome_summary` matches a hedge-pattern regex AND `next_session_handle` is null. Single-archive coverage at S-0101.

**Re-audit at S-0117** once at least 10 archives carry post-introduction telemetry.

### `next_session_handle_unknown_issue` (deferred re-audit; introduced S-0100)

**Why deferred:** introduced at S-0100 per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) Decision 6 (Issue #54). Fires when `next_session_handle` is set to `#NN` but `gh issue view NN` returns "not found" (offline-graceful). Single-archive coverage.

**Re-audit at S-0117**.

### `next_session_handle_unknown_session` (deferred re-audit; introduced S-0100)

**Why deferred:** introduced at S-0100 per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) Decision 6 (Issue #54). Fires when `next_session_handle` is set to `S-NNNN` but no archive matches AND the slot is not the next-claim slot. Single-archive coverage.

**Re-audit at S-0117**.

### `next_session_handle_malformed` (deferred re-audit; introduced S-0100)

**Why deferred:** introduced at S-0100 per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) Decision 6 (Issue #54). Fires when `next_session_handle` is set to a non-null string that doesn't match the `#<num>` or `S-<NNNN>` shape. Single-archive coverage.

**Re-audit at S-0117**.

### `edge_evidence_empty` (deferred re-audit; introduced S-0146; promoted to Persistent-warn annotation S-0196)

**Why deferred:** introduced at S-0146 per [Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62) Proposal 1. Predicate runs only when `SUPABASE_DB_URL` is set; expected to fire at high baseline against the existing 71 cross-bridges (universally NULL evidence per the S-0122 audit). Audit-time backfill of pre-S-0146 cross-bridges is a deferred cleanup pass.

**Re-audit verdict (S-0184):** the cadence audit window (≥10 post-introduction archives) confirmed steady-state high baseline — Phase 6 backfill is the resolution surface and Phase 6 has not opened. The category was promoted to the Persistent-warn annotation section above at S-0196 per [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133) for boot-surface suppression; this deferred-re-audit entry is preserved as the introduction-context record.

### `top_level_discipline_label_as_prereq_source` (deferred re-audit; introduced S-0146)

**Why deferred:** introduced at S-0146 per [Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62) Proposal 2b. Predicate runs only when `SUPABASE_DB_URL` is set; expected to fire on the 3 audit-documented umbrella nodes (`philosophy_of_language`, `philosophy_of_science`, `political_philosophy`) until their `teaching_notes` record explicit umbrella semantics. Re-audit at the next cadence audit once the umbrella-semantics annotation pass has landed (closing the documented cases) — remaining fires would then surface new umbrella-label introductions in Phase 6 self-correction.

### `prereq_direction_summary_inconsistency` (deferred re-audit; introduced S-0146)

**Why deferred:** introduced at S-0146 per [Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62) Proposal 3+5 merged. Predicate runs only when `SUPABASE_DB_URL` is set; phrase-pattern list anchored on the audit's 5 documented cross-bridge reversals. Re-audit at the next cadence audit to assess false-positive rate against post-S-0146 authoring; if the rate is non-trivial, evaluate either tightening the phrase list, narrowing the regex bounds, or promoting to LLM-flagged per the audit input doc's deferred enhancement path.

### `engine_memory_boot_query_late` / `engine_memory_diary_read_late` (deferred re-audit; introduced S-0160)

**Why deferred:** introduced at S-0160 per [Issue #124](https://github.com/StarshipSuperjam/paideia/issues/124). Both fire from `--final-check` when a MemPalace boot step's per-tool first-call timestamp (`engine_memory_activity.search_first_ts` / `diary_read_first_ts`) is later than `current.json.started_at`. Zero post-introduction telemetry at landing; the per-tool `*_first_ts` rollup fields are also new (pre-S-0160 archives lack them, so the check skips silently for the historical corpus — no backfill). Re-audit at the next cadence audit once ≥10 archives carry the new fields: a low-fire steady state confirms boot-step timing discipline holds; persistent firing signals the boot procedure is being consulted late despite the #123 thin-pointer fix, and the per-fire procedural guidance ("run the boot step at boot, before plan authoring") should escalate.

### `mempalace_hnsw_status_suspect` (retired at S-0193 per ADR 0091 cutover; entry preserved as historical record)

**Historical record:** introduced at S-0163 per [Issue #127](https://github.com/StarshipSuperjam/paideia/issues/127) (ADR 0089's sibling fix). Fired from the palace probe when `mempalace repair-status` reported `status: UNKNOWN` / unflushed metadata. Retired at S-0193 along with the entire mempalace probe surface per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) (substrate swap: chromadb+mempalace → SQLite+FTS5). The substrate-decision question this entry's deferred-re-audit was waiting on (durable HNSW fix vs. git-grep-as-recall-substrate) was settled by ADR 0091 with a third option (SQLite+FTS5) that retired the HNSW concern entirely. Distinct from `mempalace_hnsw_divergence` (also retired at S-0193) — the two never fired together (divergence needed parseable counts; UNKNOWN meant none existed).

### `skill_layer1_parity_drift` (deferred re-audit; introduced S-0163)

**Why deferred:** introduced at S-0163 per [ADR 0089](../adr/0089-skill-layer1-parity-validator-check.md) ([Issue #129](https://github.com/StarshipSuperjam/paideia/issues/129)). Structural-phase check; fires per recipe Skill ↔ Layer-1 doc pair whose procedure step-number sets diverge. At landing it fires on `session-build-lifecycle` ([Issue #125](https://github.com/StarshipSuperjam/paideia/issues/125), open, out of S-0163 scope) — that fire is the mechanism working as intended, not a false positive. Re-audit at the next cadence audit once ≥10 archives carry post-introduction telemetry: a low-fire steady state (drift caught and reconciled promptly) confirms the check converged; persistent firing of the *same* pair signals the reconciliation is being deferred and should escalate, while persistent firing across *rotating* pairs signals the doc-drift generator is still active and the ADR 0044 amendment's hand-discipline boundary needs revisiting.

## Retire candidates flagged for next health-check audit

Categories meeting the retire-candidate predicate (fired 0/20 in cadence window AND ≤1/100 in full corpus AND no documented structural-invariant role) land here. Per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) user-buffered execution, retirement is recommended to the next cadence-fired audit's "Affirmative retire candidates" section, not executed inline; the audit author surfaces the recommendation, the user adjudicates, and the disposition routes through GitHub Issues per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

**S-0101 sweep finding:** zero retire-candidates. Every silent category in the classification map above guards an identifiable structural invariant in the current pipeline. The 23 silent-in-cadence-window categories cluster into seven invariant families: cascade discipline (`adr_back_reference_orphan`, `adr_index_inconsistent`, `adr_missing_status`, `superseded_adr_currency`); graph audit per ADR 0016 (`attribute_shape_inconsistency`, `orphan_leaf`, `render_readiness_violation`, `suspicious_cross_domain_ratio`, `synthetic_review_queue`, `undeclared_predicate`); engine_memory shared-state per ADR 0045 / ADR 0056 (`chromadb_palace_health`, `engine_memory_diary_write_skipped_routine`, `mempalace_diary_write_skipped_substrate_intermittent`, `mempalace_hnsw_divergence`, `mempalace_retired_surface_used`, `mempalace_substrate_at_close`, `mempalace_wing_count_growth`, `engine_memory_zero_citations_after_search`); cross-reference integrity (`cross_reference_broken`); format checks (`engine_log_format`, `state_format`); phase-staged file expectations (`expected_future_file_missing`); routine-mode protocol per ADR 0051 (`routine_issue_spam`, `routine_no_target_reference`); ADR 0049 scope discipline (`empty_declared_scope`, `phase_mismatch_declared_scope`, `scope_delivery_non_yes`); and dynamic-emission probe failures (`repo_config_health`).

**Re-audit at S-0117** with the same predicate; if any silent category is then found to lack invariant cover (e.g., its referenced ADR has been superseded without amending the validator, or its consumer was retired), surface as retire-candidate at that audit.

## Telemetry

Trend canon: committed `engine/session/archive/S-NNNN.json` field `outcome_summary_soft_warns` per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). Read by `engine/tools/health_check.py` and the `/start-engine` boot procedure.

Per-invocation forensics: `engine/tools/validate-history.jsonl` (gitignored; canonical main-repo location since S-0205 per ADR 0063 Consequences amendment — all worktrees + main repo write to the same shared file via `_resolve_canonical_history_path()`). Useful for "when did this warn first appear" / "which commit introduced it" / "validator runtime drift."

## Closing-commit audits (hard-fail outside validate.py)

Two audits fire from the pre-commit hook only on `closing` commits (per `engine/tools/hooks/pre-commit`). They are structurally separate from validate.py but use the same exit-2-blocks-the-commit semantics.

- **`audit_handoff_dispositions.py`** (added at S-0036) — every new HANDOFF.md section in the session's range must carry a `**Disposition:**` line in one of five accepted forms. Per CLAUDE.md "Default to fix-in-context."
- **`audit_archive_structured_fields.py`** (added at S-0055 per [Issue #13](https://github.com/StarshipSuperjam/paideia/issues/13)) — the staged archive file (`engine/session/archive/S-NNNN.json`) must have `outcome_summary_soft_warns` present and non-null. Empty dict (`{}`) is permitted. Defends [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s persistent-warn surface against silent field-absence lapses (S-0043–S-0047 lapse pattern).

Both audits also have manual invocation forms documented in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) steps 6a and 6b — running them by hand before staging the close commit catches issues earlier than the hook.

## Tool invocation under venv

Tools that import `psycopg` (currently [`check_target.py`](../tools/check_target.py), [`validate.py`](../tools/validate.py), [`setup_env.py`](../tools/setup_env.py)) self-reexec under the project venv via [`engine/tools/_venv_reexec.py`](../tools/_venv_reexec.py) when invoked under a Python that lacks `psycopg`. Bare `python3 engine/tools/<x>.py` invocations work the same as if [`scrub_env.sh`](../tools/scrub_env.sh) had been sourced first. Per Issue #14 (S-0055): routine fires were resolving to system Python and emitting misleading `[FAIL] migration_applied — psycopg not available; cannot verify` output even though the migrations were genuinely applied.

The reexec is silent on success (the venv interpreter takes over without printing). If no `.venv/bin/python3` exists on the walk-up from `engine/tools/` to the filesystem root, the function returns silently and the caller's `import psycopg` raises the original `ImportError` — the prior behavior is preserved for genuinely-broken environments.

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — where soft-warn counts get recorded.
- [`health-check.md`](health-check.md) — periodic audit consuming the JSONL telemetry.
- `tools/validate.py` — implementation.
