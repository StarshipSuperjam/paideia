# ADR 0051 — Routine-mode session pattern and engine-loop foundation

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0044

## Context

Phase 5 (Seed Graph Build) decomposes naturally into ~9–12 sequential sub-sessions: one per philosophy subdomain (epistemology, ethics, metaphysics, logic, philosophy of mind, philosophy of science, political philosophy, aesthetics) plus cross-bridge authoring plus closeout. The user wants to dispatch this work across unattended Claude Code sessions firing on a cadence — turning what would otherwise be a multi-week interactive sequence into a multi-day automated run — without sacrificing the pre-Phase-5 invariants the project relies on (atomic slot claim per ADR 0022's eager-claim ritual, scope discipline per ADR 0049, fix-in-context default per CLAUDE.md).

Three coupled problems must be solved together:

**Problem A — dispatch.** A session must be able to fire on a schedule, without a human in the loop. Eager-claim already handles concurrent-session serialization; what was missing is the *trigger*. Claude Code's first-party Routines (scheduled tasks) provide this. The user has created a routine (currently set to Manual) for this purpose; Manual is the right setting until S-0044 lands the foundation, after which the user flips to Hourly.

**Problem B — termination.** A scheduled routine that fires every hour for 30 hours, when the work only needs 7, must not consume 23 wasted slots. Sessions need to read a definition-of-done at boot and exit gracefully — without claiming a slot — when the target is met. A `paused` flag and a `max_sessions` ceiling cover the additional cases (user pauses mid-batch; runaway loop containment).

**Problem C — anti-rogue.** A routine session that wakes up, reads its target, finds nothing eligible, and *invents* work would be the worst failure mode — silent commits in unintended directions, accumulating across hours. The session must be structurally unable to commit work outside a pre-declared scope, even when invented work would otherwise look plausible. Procedural rules ("don't go rogue") are insufficient; mechanical safeguards at boot and at commit are required.

**Cost calculus rejecting Paperclip.** An earlier proposal in this session was to install Paperclip (`paperclipai/paperclip`, MIT) as the orchestration layer. The investigation surfaced that Paperclip-dispatched Claude work runs on `ANTHROPIC_API_KEY` (per Anthropic's April 2026 policy, third-party orchestration is excluded from Pro/Max subscription coverage; per Paperclip's own GitHub issues #1163 and #3270, subscription-mode is incompatible with unattended heartbeat dispatch). For a solo project on a Max subscription with no real parallelism need, Paperclip's value-add (Node.js + Postgres orchestration plane, governance UI, multi-runtime support) does not justify the recurring per-token API spend. The chosen architecture stays on subscription: Claude Code Routines for dispatch, the project's existing eager-claim protocol for serialization, a small Python-side foundation for termination and anti-rogue.

**MemPalace install lesson.** S-0030's project health check audited MemPalace's S-0002 install pattern and surfaced four failures: (a) auto-mining every operations doc into semantic search diluted retrieval (88 chunks competing with curated drawers); (b) all 19 MCP tools installed but only 4 actually used; (c) coupling to user-scope Python 3.9 silently drifted (resolved at S-0043 by ADR 0050's venv migration); (d) auto-capture hooks failed silently for ~30 sessions (PATH wiring missing; resolved at S-0032). The lesson is install-with-zero-optional-features and validate-mechanically-before-load-bearing-use. This ADR honors it: routine-mode ships with explicit in-scope/out-of-scope feature lists, mechanical adoption check before any real Phase 5 work runs.

## Decision

The project introduces a **two-layer pattern** with a generic **engine loop** routine:

**Layer 1 — Master plan session (interactive, per phase):** runs in plan mode, with the user. Authors two artifacts: the *executable contract* `engine/session/auto_target.json` (frozen task list, scope_locks, dependencies, criteria) and the *human-readable rationale* `engine/build_readiness/<phase>.md` (cross-cutting conventions, anti-patterns, bridge-concept ownership rules). Routine sessions read both at boot.

**Layer 2 — Routine engine loop (unattended, per task):** Claude Code Routine fires on cadence (Manual today; Hourly post-S-0044 once a real target lands). Each fired session reads `auto_target.json`, picks the next eligible task, runs plan-then-scope-check, executes or exits. Routine sessions **never edit the master plan** — revisions surface as HANDOFF entries with `master_plan_revision_needed: <reason>`; the user adjudicates in the next interactive session.

### Target file: `engine/session/auto_target.json`

Single master target file at a fixed path. The file's presence is the routine-mode signal — its absence falls back to the standard interactive boot. Schema documented at [`engine/session/auto_target.schema.md`](../session/auto_target.schema.md).

Top-level fields: `target_id`, `goal`, `paused: bool`, `max_sessions: int`, `max_wall_clock_hours: int` (advisory; not mechanically enforced — wall-clock is harder to attribute reliably than session count), `tasks: list[Task]`.

Per-task fields: `id`, `name`, `depends_on: list[task_id]`, `criteria: list[Criterion]`, `scope_lock: {allowed_paths: list[glob]}`, `status: pending | in_progress | complete | blocked`, optional `blocked_reason`.

Status transitions are write-only by routine sessions: `pending → in_progress` (on slot claim), `in_progress → complete` (all criteria pass), `in_progress → blocked` (any criterion fails or session abandons task). The pre-commit hook's master-plan-integrity check (below) hard-fails any routine-mode commit that diffs `auto_target.json` keys other than `tasks[*].status` and `tasks[*].blocked_reason`.

### Criterion types

Five types ship at landing, all implemented as functions in [`engine/tools/check_target.py`](../tools/check_target.py). New types are one Python function (the registry is a dict; new entries land via PR with a test).

- `migration_applied` — checks Supabase migration history for an applied id (uses `SUPABASE_DB_URL` if set; gracefully degrades to "cannot verify" otherwise, which the runner treats as "not satisfied" rather than crashing).
- `validate_passes` — runs `validate.py`; passes iff zero hard-fails. Soft-warns are advisory and do not fail the criterion (the routine session's job is to cleanly land its task; soft-warns are surfaced for the next session per ADR 0042).
- `adr_status` — checks ADR file frontmatter for the configured `Status` value. Robust to whitespace and case.
- `file_exists` — checks a path exists relative to repo root.
- `predicate` — runs a named callable from a registry in `check_target.py`. Escape hatch for criteria that do not fit the four named types (e.g., "row count in the seed_concepts table is ≥ N"). Predicates author themselves into the registry alongside their tests.

### Routine boot procedure (separate slash command + Skill)

S-0044 user-directed clarification: routine-mode and interactive build are *separate* entry points, not branches of one boot procedure. Conflating them under `/start-engine` confused two concerns with five differences (boot procedure, scope rules, commit posture, permission model, shutdown logic). Two clean entry points:

- **`/start-engine`** + Skill `session-build-lifecycle` — interactive build sessions (the existing path).
- **`/start-routine`** + Skill `routine-mode-lifecycle` — unattended routine-mode sessions invoked by Claude Code Routines (introduced at S-0044).

The routine boot procedure is documented in [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) and mirrored in the Skill body. Sequence:

1. Detect mode: `auto_target.json` exists at repo root → proceed; absent → log "no target; routine has nothing to do" → exit 0 (user probably intended `/start-engine`).
2. If `paused: true` → log "target paused, no claim" → exit 0.
3. Run completion criteria for every task; if every task is `complete` → log "target met, no claim" → exit 0.
4. Count routine-mode sessions in `engine/session/archive/` for this `target_id`; if ≥ `max_sessions` → write HANDOFF "max_sessions reached for `<target_id>`" → exit 0.
5. Find the first task whose `status == pending` AND all `depends_on` are `complete`. None found → write HANDOFF "no eligible task" → exit 0.
6. Selected task → write a session plan to [`engine/session/current_plan.md`](../session/current_plan.md) describing exactly what files will be touched and which criterion each addresses. Plan format is `paths_to_modify: [glob, ...]`, `criteria_addressed: [criterion_index, ...]`, plus prose rationale.
7. Run `engine/tools/check_routine_scope.py --plan engine/session/current_plan.md --task-id <id>`. Exit 0 → proceed; non-zero → write HANDOFF "scope-check failed: `<reason>`" → exit 0.
8. Claim slot per the existing eager-claim ritual; mark task `in_progress` in target file (commit).
9. Execute the work. Pre-commit hook re-runs scope-check against staged files (`task.scope_lock.allowed_paths` ∪ operational allowlist). Discovered out-of-scope findings route to `gh issue create` per the discovered-issues rules below. Genuine blockers route to HANDOFF + mark task `blocked` + early shutdown.
10. After work commits clean: re-run task criteria; all pass → mark task `complete` in target file (commit); any fail → mark `blocked: <reason>` (commit) → write HANDOFF.
11. Run shutdown sequence (existing). Issues created during the session count into `outcome_summary` for shutdown review.

Step 6 is the externalization-as-quality-gate equivalent of plan mode, mechanically enforced rather than human-gated. The forcing function (write a complete plan that survives review) is preserved; the reviewer is `check_routine_scope.py` rather than the user. Plan mode itself is unsuitable for routine sessions because `ExitPlanMode` requires human approval that an unattended session cannot provide.

### Scope-lock model: task-deliverable vs operational paths

Two classes of paths matter at commit time:

**Task-deliverable paths.** Controlled by the active task's `scope_lock.allowed_paths`. The actual work artifact (e.g., `engine/migrations/0042_*`, `build_plan/P_5_subdomains/epistemology.md`).

**Operational paths.** Always allowed for routine sessions, regardless of which task is active. The apparatus the session itself runs on:

```
engine/session/current.json              # session state
engine/session/current_plan.md           # the boot-time plan file
engine/session/auto_target.json          # status field updates only (master-plan-integrity below)
engine/session/archive/S-*.json          # closing archive
engine/session/register_state.json       # next_id / claim updates
engine/ENGINE_LOG.md                     # session log entry
HANDOFF.md                               # blockers, scope-expansion-needed, discovered-issue notes
```

The pre-commit hook accepts a staged file iff it matches **either** the active task's `scope_lock.allowed_paths` **or** the always-allowed operational set.

### Discovered issues and blockers — what routine sessions can and must do

A routine session that, mid-task, notices something out of scope (a bug elsewhere, dead config, stale docs, security concern, tech-debt item) **must not crash and must not paper over**. The triage rules — same as ADR 0048's existing issue-discipline — apply unchanged in routine mode:

- **Discovered finding outside current task scope** → `gh issue create` with the appropriate label (`bug`, `tech-debt`, `cleanup`, `enhancement`, `priority:urgent` if warranted). No tracked files touched, scope_lock irrelevant. Continue with assigned task.
- **Discovered finding inside current task scope** → default to fix-in-context per CLAUDE.md (the fix is already inside `scope_lock.allowed_paths`).
- **Current task cannot complete** (genuine blocker, scope-expansion-needed, decision required) → mark task `blocked: <reason>` in `auto_target.json`, write HANDOFF entry with one of the five accepted Disposition forms (per ADR 0048 + the audit_handoff_dispositions tool), exit cleanly. The user adjudicates next interactive session.
- **Validate.py soft-warns** → record in `outcome_summary` as today; no special handling.

`gh issue create` is permitted unilaterally in routine mode. CLAUDE.md's routine-mode posture authorizes this explicitly.

### Anti-rogue mechanical safeguards (defense in depth)

| Layer | Mechanism | What it prevents |
|---|---|---|
| Boot-time | `check_routine_scope.py` on the session plan | Session embarks on out-of-scope work |
| Commit-time | Pre-commit hook with `--staged` (task scope ∪ operational allowlist) | Out-of-scope task-deliverable file lands |
| Master-plan integrity | Pre-commit hook hard-fails routine-mode commit to `auto_target.json` diffing keys other than `tasks[*].status` and `tasks[*].blocked_reason` | Routine session unilaterally edits master plan |
| HANDOFF integrity | Existing `audit_handoff_dispositions.py` (per ADR 0048) | HANDOFF entries lacking proper Disposition |
| Issue-spam | `validate.py` soft-warn at >3 issues created per session | Confused session floods backlog |
| Validate-time | New `validate.py` soft-warn: routine-mode session committed without referencing the active task in its plan | Routine session ran without target alignment |

The combination makes "routine session goes rogue and lands rogue work at HEAD" structurally impossible. The session can think rogue thoughts and even file an issue about them; it cannot commit task-deliverable changes outside scope.

### Permission-mode posture

Routines run in Claude Code's `Default` permission mode, **not** `plan` mode. Plan mode requires human `ExitPlanMode` approval and would deadlock unattended sessions. The plan-then-scope-check above is the externalization-as-quality-gate equivalent, satisfied procedurally in the boot prompt + mechanically by `check_routine_scope.py`. Interactive sessions retain plan mode as the user's default if configured.

The routine itself (the user-created Claude Code Routine) is configured: Manual schedule today (until S-0044 lands), Hourly post-landing; Worktree checkbox enabled; folder pointing at the project root; **instructions are the single line `/start-routine`**, which dispatches via the new slash command + Skill introduced at S-0044.

## Consequences

**Direct.**

- A solo session pattern (today's only mode) gains a sibling: long-running multi-session work batches run unattended on subscription billing, with mechanical anti-rogue safeguards.
- Phase 5's eight subdomain seeds become a dispatchable batch rather than 8 separately-invoked interactive sessions. The user kicks off the master plan session (S-0045), authors the target file, flips the routine to Hourly, and walks away. Comes back hours later to a completed Phase 5 (or HANDOFF entries on the parts that hit blockers).
- The Phase 5 epistemology build-readiness gate (twice-displaced at S-0042 and S-0043, originally targeted for S-0044) is reframed: the gate report at `engine/build_readiness/phase_5.md` is now authored *as part of* S-0045's master plan session, not as a standalone deliverable. The gate work is preserved, not deferred — its output becomes one of two artifacts the master plan session produces (the other being `auto_target.json`).
- Existing eager-claim protocol, ADR 0049 scope-discipline, ADR 0048 issue-discipline, ADR 0042 soft-warn lifecycle, ADR 0045 shared-state integrity all survive unchanged. Routine-mode is additive; no existing contract is mutated.

**Posture preservation.**

- The pre-commit hook gains two new responsibilities (scope-check on staged files when `auto_target.json` is present and a task is in_progress; master-plan-integrity check when `auto_target.json` itself is staged from a routine session). Both are routine-mode-only — interactive sessions experience no behavior change.
- The validator (`validate.py`) gains two new soft-warns (routine-mode-no-target-reference; routine-mode-issue-spam-over-3). Both are advisory; neither blocks a commit.
- `engine/build_readiness/` was already a real directory with prior reports (Phase 3, Phase 4, S-0042 engine apparatus). Phase 5's report joins them at S-0045.

**Future work surfaced (not deferred).**

- **Anthropic `count_tokens` API integration for accurate post-shutdown telemetry** — explicitly rejected at S-0044 per user direction (introduces recurring API spend for telemetry refinement). *(Note: the surrounding `transcript_token_pct` telemetry that this rejection sat alongside was itself retired at S-0083 per Issues #21/#32 and the ADR 0049 amendment, which makes the rejection moot — the project no longer captures token telemetry of any kind. Preserved here as historical record of the deliberation.)*
- **Hourly-cadence flip** — user action after S-0045 lands the first real target.
- **Additional criterion types beyond the initial five** — added as Phase 5 execution surfaces concrete needs (pure on-demand; no speculative pre-authoring).
- **Routine-mode for non-build-mode work** (e.g., daily review, weekly archive consolidation) — orthogonal pattern; would author its own narrowly-scoped routine, not extend the engine loop.

## Alternatives Considered

### Paperclip trial install (rejected at S-0044)

Earlier in S-0044's planning thread, the proposal was to install `paperclipai/paperclip` (MIT, Node.js + Postgres) as a trial orchestration layer for Phase 5 parallelism, with a Phase 7 commit decision. Investigation surfaced three load-bearing concerns:

1. **Anthropic policy excludes third-party orchestration from subscription coverage.** Per Anthropic's April 2026 policy and Paperclip's own GitHub issues #1163 and #3270, Paperclip-dispatched Claude work runs on `ANTHROPIC_API_KEY` and incurs per-token API charges separately from a Pro/Max subscription. The `claude_local` adapter advertises a subscription-via-OAuth path but the OAuth flow is incompatible with unattended heartbeat dispatch (the only Paperclip feature this project actually wants).
2. **Paperclip's value-add doesn't justify the recurring API spend.** For a solo project, the orchestration plane (Node.js server, Postgres metadata, governance UI, multi-runtime support, board approvals, mobile dashboard) addresses problems Paideia does not have. Eager-claim already serializes; ENGINE_LOG.md + session archives already provide audit trail; ADRs + MemPalace already provide governance. Installing Paperclip to replicate functionality the project already has is value-negative.
3. **MemPalace install lesson.** Installing default-everything-then-discipline-later is the failure pattern S-0030 documented. Paperclip's surface (org charts, roles, multi-company, plugins) is broad and would invite the same pattern.

The rejection is not "Paperclip is bad"; it is "Paperclip is mismatched to a solo subscription-funded project with no real parallelism need." The architecture chosen here (Claude Code Routines + target file + scope-check) accomplishes the same dispatch + termination + anti-rogue goals at zero recurring spend, with no new tech stack, on the project's existing apparatus. If this project ever expands beyond Claude (multi-runtime), or hires collaborators (multi-user governance), or accepts API spend on principle (e.g., for unattended Phase 8 evaluation runs), Paperclip becomes a reasonable revisit.

### Direct DIY orchestrator (rejected as redundant)

A few hundred lines of Python wrapping `claude -p` invocations across worktrees, with SQLite file locks for atomic ticket checkout. Functionally equivalent to the chosen architecture, but rejects a working first-party feature (Claude Code Routines) in favor of a hand-rolled scheduler. Routines already handle the dispatch problem; reinventing it would be the more-work-for-no-value pattern.

### Drop parallelism entirely; stay sequential forever (rejected as too narrow)

ROADMAP §5.4 anticipates parallel epistemology + ethics as the first natural parallel-work moment. Cutting that ambition because Paperclip is mismatched is the wrong fix. The chosen architecture preserves the ability to parallelize *if needed*: target file dependencies could allow N tasks at the same level to run concurrently on N independent machines, each with its own Routine, each respecting eager-claim. The user has indicated 24 sessions/day sequential is plenty; the architecture does not preclude parallel later.

## See also

- [ADR 0022](0022-periodic-project-health-checks.md) — eager-claim ritual; the protocol routine-mode rides on top of.
- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — build-readiness-gate posture; phase_5.md authoring inherits this.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; the new routine-mode soft-warns plug into the same canon.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — issue-discipline; routine sessions follow it unchanged.
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — declared_scope at boot; the routine-mode `scope_lock` extends the same posture mechanically.
- [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) — Layer 1 ops doc; target file schema + master plan procedure + routine boot procedure + criterion catalog + troubleshooting.
- [`engine/session/auto_target.schema.md`](../session/auto_target.schema.md) — target file schema reference.
- [`engine/tools/check_routine_scope.py`](../tools/check_routine_scope.py), [`engine/tools/check_target.py`](../tools/check_target.py) — the foundation tools.
