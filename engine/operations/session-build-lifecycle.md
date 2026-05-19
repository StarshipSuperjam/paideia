# Session build lifecycle

> How a build session boots, runs, and commits. The shutdown sequence (close work) lives in [`session-shutdown-sequence.md`](session-shutdown-sequence.md).
>
> **Canonical invocation:** Skill `session-build-lifecycle` (per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md)). The skill's body is the procedural form of this document; this document is the Layer 1 source-of-truth prose. Updates flow doc → skill, never the reverse.

## When this applies

A build session is any conversation that types `Start Engine` or invokes `/start-engine`. Default-mode (exploration) conversations do not run this lifecycle — they make no commits and claim no slot.

## Boot procedure (run in order)

> **If `engine/session/auto_target.json` exists**, you may have reached this lifecycle via `/start-engine` when you intended `/start-routine` (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md)). Routine-mode sessions use a separate entry point — see [`routine-mode-operations.md`](routine-mode-operations.md). This lifecycle is for interactive build sessions; if you continue, the slot will be claimed for interactive work and the routine state may need attention. Surface this to the user before proceeding.

1. **Read `STATE.md`.** Get current phase, last build session, next-session work item, GitHub URL, Supabase project ref, infrastructure pointers.

2. **Health-check cadence trigger.** Read `session/register_state.json`. Parse the trailing 4-digit counter from `next_id` (the slot about to be claimed) and `last_audit_session` (the most recent completed audit). The trigger fires when `(next_id - last_audit_session) >= health_check_cadence` (default cadence: 10 as of S-0033, was 30 pre-S-0033; overdue-catchup logic introduced at S-0041 — see ADR 0022 Consequences amendments). Two surfaces:

   - When `slots_since == cadence` ("due"):

     > "Next slot is S-NNNN. Cadence trigger fires for a project health check (see `engine/operations/health-check.md`). Run the audit now or defer?"

   - When `slots_since > cadence` ("overdue"):

     > "Cadence trigger fires; audit is OVERDUE by N session(s). The cadence-aligned slot was consumed by user-directed work without the audit firing. Run the audit now or document explicit deferral in outcome_summary."

   User accepts → the session's work becomes the audit (which bumps `last_audit_session` at report-emit time, clearing the trigger). User defers → proceed with planned work; record deferral in `outcome_summary` at close; the trigger fires again next session.

   The overdue-catchup logic replaces the prior `next_id % cadence == 0` strict-modulo at S-0041 ([ADR 0022](../adr/0022-periodic-project-health-checks.md) + [ADR 0043](../adr/0043-hook-architecture.md) Consequences amendments) — strict-modulo silently slid the trigger by a full cadence whenever the aligned slot was consumed (S-0040's slot was taken by deferred-fix work, leaving the next fire at S-0050, a 19-session gap). The SessionStart hook (`engine/tools/hooks/session-start.sh`) emits the same surface from the harness side regardless of how the session is launched. If `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041), the hook falls back to strict-modulo with a stderr log line so the regression surfaces.

2b. **Persistent-warn surface.** Per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). The `SessionStart` hook (`engine/tools/hooks/session-start.sh`) reads the last 5 `engine/session/archive/S-NNNN.json` files and emits the persistent-warn surface mechanically — the AI does not read the archives directly. Since S-0196 ([Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133)), the surface splits into two output lanes:

   - **Action-needed** — categories firing in ≥3 of the last 5 archives WITHOUT an annotation in `engine/operations/tools-validate-interpretation.md`'s "Persistent-warn annotation" section. Per-category fires listed individually with the escalation hint. This is the alert lane; consult for new threshold-crossings and decide whether to address inline, queue follow-up, or escalate per the 10-session-persistence criterion.
   - **Annotated baselines** — categories firing in ≥3 of the last 5 archives that DO carry a documented annotation. Surfaces as a single-line count + pointer to the annotation section; per-category list intentionally omitted to keep the lane a periodic reminder rather than an alert. Categories continue to fire per-commit; the cadence-fired audit per [ADR 0022](../adr/0022-periodic-project-health-checks.md) consumes the same archive data with a longer window.

   Membership is computed by [`engine/tools/scan_persistent_warn_annotations.py`](../tools/scan_persistent_warn_annotations.py) parsing the annotation section's H3 entries; the hook partitions firings into the two lanes. The annotation-driven suppression is mechanical, not AI posture — landing a category in the annotation section is the documented "accept and annotate" escalation resolution that now structurally moves it out of the action-needed lane. Helper-failure (script absent, parse error, exit != 0) falls back to empty-annotated-list — all categories surface as action-needed, preserving visibility on parser break.

   See [`engine/operations/soft-warn-lifecycle.md`](soft-warn-lifecycle.md) "Annotated-baselines lane" subsection for operational detail.

3. **Query engine_memory.** Use the `engine_memory_search` MCP tool with terms derived from STATE.md's next-session work item. Surface anything previously recorded that's relevant. (Pre-S-0192 sessions used `engine_memory_search` per ADR 0056; ADR 0091 supersedes that contract.) **Mechanically backstopped by `engine_memory_boot_query_skipped` soft-warn (per ADR 0091, S-0192)** — `engine/tools/hooks/post-engine-memory-tool-use.sh` records the call to `engine/session/current_engine_memory.jsonl`; `validate.py --final-check` at shutdown step 3 emits the soft-warn if no `engine_memory_search` call landed.

   **Boot-search orchestrator (per ADR 0091, S-0192).** Invoke `python3 -m engine.memory.boot_surface` at this step. The orchestrator runs three formulations of the work-item phrase (literal / conceptual / adjacent) through FTS5 + BM25 + recency + tag-class-boost retrieval, deduplicates and ranks, and writes an idempotent `## Prior context (engine memory)` section into `engine/session/current_plan.md`. One `query_log` row is written per formulation. The AI reads the section before authoring the session plan; surfaced drawers that bear on the work get cited in plan rationale or commit messages, satisfying the closed-loop `engine_memory_zero_citations_after_search` audit at shutdown.

3b. **Read recent diary entries.** Per [`engine-memory-operations.md`](engine-memory-operations.md). Call `engine_memory_diary_read agent_name="claude" last_n=3` to see the previous three sessions' first-person AI reflections — what surprised the prior AI, what they noticed but deferred, what felt load-bearing for this session, where their judgment was uncertain. Surface anything that bears on the work about to be claimed; skip silently when the diary is empty. **Mechanically backstopped by `engine_memory_diary_read_skipped` soft-warn (per ADR 0091, S-0192).**

4. **Read referenced docs.** STATE.md and ROADMAP.md will name specific files relevant to the work. Read them before claiming the slot — the slot claim should be informed.

5. **Read the build-readiness report** (substantive build sessions only, per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)). STATE.md's "Next session work item" names the report at `engine/build_readiness/<phase>_<chunk>.md` for substantive build sessions. Read the report end-to-end:

   - **Pre-session decisions section** — Tier 1 resolutions inherited from the gate session. The build session implements against these, not around them.
   - **Tier 2 decisions section** — concrete column shapes, constraint forms, default values. Implement exactly as documented; the gate session settled these in advance precisely so the build session does not re-decide under build pressure.
   - **Tier 3 forward pointers** — decisions explicitly deferred. Honor the deferral; do not pre-empt by inventing answers.
   - **Success criteria** — the build session verifies these at shutdown.

   If the report is **absent** for a session work item that requires one (substantive build phase), the session converts to a gate session: do not author the planned artifacts; instead run the gate procedure per [`build-readiness-gate.md`](build-readiness-gate.md) and produce the report. The next session opens as the build session.

   If the report is **present but contains unresolved Tier 1 items**, the session halts and escalates to the user — the gate session did not finish its job. Do not attempt to resolve Tier 1 in-flight; the build session's mode is auto-by-default for routine judgment, not for foundational decisions.

   Operational sessions (health checks, ENGINE_LOG-only edits, retrievability cleanups, gate sessions themselves) skip this step — they do not require build-readiness reports per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s scope.

5b. **Concurrent-session collision check** (per [Issue #3](https://github.com/StarshipSuperjam/paideia/issues/3) / S-0048). Run [`engine/tools/check_session_conflict.py`](../tools/check_session_conflict.py). The tool inspects `engine/session/register_state.json` and `engine/session/current.json` and disposes:

   - **Exit 0** (no conflict): `current_status` is `closed` (or absent), or `current.json` is absent. Proceed to step 6.
   - **Exit 1** (recent collision or ambiguous mid-window): a routine-mode or interactive session is in flight (`current_status: in_progress`, `started_at` < 24h). The session must NOT claim a new slot — the eager-claim would overwrite the rival's `current.json` and corrupt its archive. Surface the tool's stderr to the user and refuse: name the rival session ID, name the cooperation procedure (pause the routine via `auto_target.json` `paused: true`, or wait for the rival to close), and exit the boot procedure cleanly.
   - **Exit 2** (stale): an `in_progress` session has been open for >24h with no close. Almost certainly a dead session (force-killed harness, machine reboot, etc.). Offer auto-recovery to the user: edit `register_state.json` to set `current_status: 'closed'`, archive the stale `current.json` to `engine/session/archive/<rival_id>.json` with `status: closed_partial` and a note in `outcome_summary`, then re-run the boot procedure.

   The same surface fires in [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) at every boot regardless of how the session is launched, but the hook itself never blocks (per its "always exits 0" design). The slash command's boot procedure is the actual refusal point.

6. **Claim the slot via the eager-claim ritual** (see below).

7. **Begin substantive work.** The slot is held atomically; concurrent sessions cannot collide. Make file edits, run tools, commit incrementally as work progresses. Each commit must pass `tools/validate.py` (enforced by the pre-commit hook in `tools/hooks/pre-commit`). For substantive build sessions, the build-readiness report is the canonical decision-of-record — when implementation choices arise that the report did not anticipate, they fall into one of three buckets: (a) routine in-session judgment, recorded in `outcome_summary`; (b) escalation candidates per [`escalation-criteria.md`](escalation-criteria.md); (c) signals that the gate session under-specified — surface in `outcome_summary` so the next gate exercise refines.

## Eager-claim ritual

Atomic slot reservation. Run before any substantive work edits.

1. Read `session/register_state.json`. Note `next_id` (e.g., `0007`).

2. Bump it to `next + 1`, set `last_claimed: "S-<next>"`, `current_status: "in_progress"`. Preserve the `description` and `format` fields.

3. Write `session/current.json`:

   ```json
   {
     "id": "S-<next>",
     "started_at": "<ISO-8601 UTC>",
     "status": "in_progress",
     "mode": "interactive",
     "working_on": "<one-sentence summary>",
     "declared_scope": "<1-3 sentences naming what this session commits to deliver. Optionally end with `phase: <id>` matching a build_plan/MANIFEST.md identifier (e.g., `phase: P_3` or `phase: 4.5`); use `phase: NA-...` for operational/engine-apparatus work that doesn't map to a build-plan phase.>",
     "outcome_summary": null,
     "scope_delivery": null,
     "next_session_handle": null,
     "approved_plan": "<path or null>",
     "branch": "<current git branch>",
     "worktree": "<absolute path>"
   }
   ```

   The `mode` field is required from S-0048 onward per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) and hard-fail-enforced on the close commit by [`audit_archive_structured_fields.py`](../tools/audit_archive_structured_fields.py). Build sessions (`/start-engine`) set `"interactive"`; routine-mode sessions set `"routine"` (per the routine-mode-lifecycle Skill). The value records the durable session-execution style — a human-attended interactive session vs. an unattended cadence-fired routine — not a project-phase label. The audit's `allowed_values` guard hard-fails any other value. Writing it into the template (rather than hand-patching at close) was the S-0157 fix for [Issue #121](https://github.com/StarshipSuperjam/paideia/issues/121).

   The `declared_scope` field is required from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The validator's `empty_declared_scope` soft-warn fires every commit until the field is populated; the `phase_mismatch_declared_scope` soft-warn fires when a `phase:` token doesn't match the build-plan manifest. Both checks are scope-discipline backstops — the field is the boot-time declaration that the shutdown-time scope-delivery audit will compare against.

   The `scope_delivery` field starts as `null` (in-flight) and is populated at shutdown with `{"delivered": bool, "user_confirmed_changes": bool, "explanation": str}` per the shutdown-sequence audit step.

   The `next_session_handle` field is required from S-0100 onward per [ADR 0049 Decision 6 (S-0100 amendment)](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). Initialized `null` at eager-claim. Filled at shutdown step 10 (defer-handle audit): when `outcome_summary` contains hedge-pattern phrasing referring to deferred work (e.g., "future session will pick up X"), the field declares either an Issue number (`"#<num>"`) or a specific session ID (`"S-<NNNN>"`) that owns the deferred fix. Explicit `null` at shutdown means "any hedge phrasing in `outcome_summary` is intentional forward-pointer prose, not a deferral." The `validate_outcome_summary_unhandled_defer` check at `--final-check` fires the soft-warn `outcome_summary_unhandled_defer` when hedge-pattern prose appears with the field absent (forgot to declare); fires `next_session_handle_unknown_issue` / `next_session_handle_unknown_session` when verification finds a stale reference; fires `next_session_handle_malformed` when the value is a string but doesn't match `#<num>` or `S-<NNNN>`.

4. Stage both files. Commit:

   ```
   chore(session): eager-claim S-<NNNN> — <topic>
   ```

5. Push the eager-claim via the build-mode lifecycle wrapper (per [ADR 0076](../adr/0076-build-mode-lifecycle-push-wrapping.md)):

   ```bash
   python3 engine/tools/build_lifecycle_push.py eager-claim
   ```

   The wrapper mechanically shape-verifies HEAD (eager-claim subject pattern, exactly 1 ahead of `origin/main`, register_state transition, allowed path set) before pushing. On success it performs the parent-side FF best-effort. Exit codes 0 (success) / 2 (verification refused) / 3 (push rejected by remote) / 4 (network failure) / 5 (generic git error). The wrapper bypasses the harness's "Default Branch Push" classifier via subprocess-spawned git from a permitted python tool — same pattern as `routine_lifecycle_push.py` (ADR 0054) for routine sessions.

   No per-push confirmation. Invoking `/start-engine` (or typing `Start Engine`) is the authorization for the lifecycle's pushes — eager-claim, in-session checkpoints, and shutdown. Destructive operations (force-push, `git reset --hard`, branch deletion) still require explicit confirmation per the auto-mode interrupt criteria in `escalation-criteria.md`.

The slot is now reserved. Concurrent sessions reading `register_state.json` will see `next_id` already bumped and pick the following slot.

## Routine-mode is a separate lifecycle

Per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md), routine-mode sessions are architecturally distinct from interactive build sessions. They have their own slash command (`/start-routine`), their own Skill ([`routine-mode-lifecycle`](../../.claude/skills/routine-mode-lifecycle/SKILL.md)), and their own Layer 1 ops doc ([`routine-mode-operations.md`](routine-mode-operations.md)). They share only the eager-claim ritual (below) — every other concern (target detection, plan-then-scope-check, scope-lock enforcement, master-plan integrity, completion verification) is routine-specific.

This separation was a S-0044 user-directed clarification: bolting routine-mode into `/start-engine` conflated two concerns with five differences (boot procedure, scope rules, commit posture, permission model, shutdown logic). Two entry points keeps the mental model clean.

## Worktrees

Build sessions typically run in a Claude Code worktree (`/Users/.../.claude/worktrees/<name>/`). The worktree shares git history with the parent repo via the linked `.git` file. All commits land on the same branch as the worktree (`claude/<name>`). Fast-forward to main happens in the parent repo.

Before pushing, fast-forward main locally first; resolve any divergence in the worktree before forwarding. If the parent's main has moved (another session merged), rebase the worktree branch onto main, re-run validate, then re-attempt the FF.

## In-session commit cadence

- Commit at every meaningful checkpoint, not at session close. A session that produces 12 file changes should produce roughly 3-6 commits, not one giant commit.
- Each commit must pass `tools/validate.py`. Hard-fails block the commit; fix and retry.
- Soft-warns are allowed but accumulate in `session/current.json`'s `outcome_summary` at close — they are signal, not noise.
- Conventional Commits format. Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`, `perf`. Eager-claim and archive use `chore(session):`.

## Push policy within a session

- All routine pushes within a build session proceed without per-push confirmation. The `/start-engine` invocation is the authorization for the lifecycle.
- Destructive operations remain gated: force-push, amends to published commits, branch deletion, `git reset --hard`. These require explicit confirmation regardless of session mode.
- Always FF main locally before pushing. Never push the worktree branch directly to remote main without going through the parent repo's main.

## Recovery

The lifecycle runs cleanly in the common case. These procedures cover edge cases not yet exercised in production.

### Eager-claim race (concurrent slot collision)

Two sessions reading `register_state.json` near-simultaneously can both write `S-NNNN` claim commits against the same slot. The first push wins; the second session's `git -C <parent> merge --ff-only <branch>` rejects because main has moved.

Resolution path (still in boot procedure, no substantive work yet):

1. `git fetch origin main`, then inspect `git log origin/main..HEAD`. A peer's `eager-claim S-<same N>` commit on the upstream confirms collision.
2. From the worktree branch: `git reset --hard origin/main`. The destruction is bounded — only the local claim commit is lost; the boot rule is *claim first, work second*, so no substantive work is in flight.
3. Re-read `register_state.json` (now showing the peer's bumped `next_id`).
4. Re-run the eager-claim ritual against the new slot. Update `current.json`'s `id` and `working_on`. Commit, FF, push.
5. Resume substantive work.

The mechanism's collision resistance is in place but not stress-tested by an actual concurrent collision. The first real exercise will likely come during Phase 5 parallel seed-graph build.

### Pre-commit hook installation (`core.hooksPath`, per ADR 0100)

The hook itself lives at [`tools/hooks/pre-commit`](../tools/hooks/pre-commit) (tracked). Per [ADR 0100](../adr/0100-engine-inspired-hook-installation-and-close-friction-mitigations.md), hook discovery uses `git config core.hooksPath engine/tools/hooks` (set once per clone, stored in main's `.git/config`). Worktrees share main's `.git/config`, so the setting propagates automatically. Each worktree's commits resolve the pre-commit script from its OWN working tree at HEAD — hook-content edits authored in a worktree take effect on the same worktree's next commit, no longer dependent on main's working tree being FF'd first. Cures the S-0209 symlink-staleness lesson at the root.

On a fresh clone, run once from the main repo root:

```bash
git config --local core.hooksPath engine/tools/hooks
```

Verify: `git -C <main-repo> config --get core.hooksPath` prints `engine/tools/hooks`. A test commit (even `--allow-empty`) should fire the hook and run `validate.py`.

The pre-S-0210 setup used a relative symlink at `<main>/.git/hooks/pre-commit → ../../engine/tools/hooks/pre-commit`. If you find such a symlink on a clone that pre-dates S-0210, remove it after setting `core.hooksPath`:

```bash
rm <main-repo>/.git/hooks/pre-commit
```

If the `core.hooksPath` setting is missing on a clone, Git falls back to `<main>/.git/hooks/` which now lacks `pre-commit` — commits would proceed UNGATED. A future session that finds itself in an ungated state should suspect missing `core.hooksPath` first.

### Parent-FF refusal on `.claude/settings.json` edits from worktrees

When a build session edits `.claude/settings.json` via the harness Write/Edit tools, the harness lands the change on the parent repo's tracked copy. The worktree's tracked copy stays stale, and the pre-commit [`check_settings_sync.py`](../tools/check_settings_sync.py) hard-fails the close commit until the worktree's copy is brought into sync. The documented remediation is `cp <parent>/.claude/settings.json .claude/settings.json && git add .claude/settings.json` — or, mechanized at S-0150, `python3 engine/tools/update_settings.py` from inside the worktree (resolves both paths, copies, stages, emits the post-push reminder).

After the worktree commit succeeds, a second surface fires: `build_lifecycle_push.py` (and `routine_lifecycle_push.py`'s sibling helper) run a best-effort parent-side `git -C <parent> merge --ff-only origin/<target>` to advance the parent's local main. Git's safety check refuses with *"Your local changes to the following files would be overwritten by merge: .claude/settings.json"* even though the FF would land byte-identical content — git doesn't know the cp made the working-tree copy match the incoming commit.

[ADR 0054 Consequences amendment landed at S-0150](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) extends `parent_ff()` with a bounded auto-recovery for this specific signature. On the *"would be overwritten by merge"* refusal, the function parses the affected file list, compares each working-tree copy to its `origin/<target>` version via `git diff --quiet`, and when every file is byte-identical runs `git checkout -- <files>` followed by a retry FF. The wrapper's stdout reads *"parent main FF'd to <short>; auto-recovered from identical-content overwrite refusal on N file(s)"*.

When **any** affected file diverges from `origin/<target>`, the auto-recovery bails without mutating state, returning *"working-tree diverges from origin/<target> on <files>; manual recovery required"*. This is the case to investigate by hand:

```bash
git -C <parent-repo-path> diff HEAD origin/main -- .claude/settings.json
git -C <parent-repo-path> checkout .claude/settings.json   # only if discard is intentional
git -C <parent-repo-path> merge --ff-only origin/main
```

The `diff` step lets you compare the diverged content to the incoming commit. If the parent's working-tree copy is residual stale state from a prior session (no current work depends on it), `git checkout` discards it safely. If the working-tree copy is in-flight uncommitted work, preserve it via `git stash` or by committing in the parent before retrying the FF.

The `parent_ff()` failure is non-fatal — the wrapper exits 0 (push succeeded). The push itself landed; the parent's stale HEAD is a separate problem the next session's boot-freshness gate ([ADR 0082](../adr/0082-routine-boot-freshness-and-concurrency-defense.md)) will catch.

### engine_memory capture-hook failure log

The Stop and PreCompact hooks invoke [`tools/hooks/engine-memory-capture.sh`](../tools/hooks/engine-memory-capture.sh), which always exits 0 to the harness and routes capture failures (venv python missing, substrate write failed, jq absent) to `.claude/logs/engine-memory-hook.log`. The log is gitignored per-clone state.

At session boot, after reading STATE.md and before the engine_memory context query, check the log. If `.claude/logs/engine-memory-hook.log` exists and is non-empty, surface its contents to the user — capture may have failed silently in earlier sessions running from this worktree, and the conversational substrate they recorded may be missing from engine_memory.

```bash
test -s .claude/logs/engine-memory-hook.log && cat .claude/logs/engine-memory-hook.log
```

Acknowledged entries can be cleared by truncating the file (`: > .claude/logs/engine-memory-hook.log`); fresh failures will append on the next hook fire. Persistent failures usually mean the venv python isn't resolving or the substrate file path is unwritable — see [`engine-memory-operations.md`](engine-memory-operations.md) for diagnosis steps.

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — close-of-session protocol.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — what to do with hard-fails and soft-warns.
- [`escalation-criteria.md`](escalation-criteria.md) — when to interrupt the user mid-session.
- `.claude/commands/start-engine.md` — the slash command implementation.
