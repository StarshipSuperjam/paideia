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

3. **Query MemPalace.** Use `mempalace_search` with terms derived from STATE.md's next-session work item. Surface anything the user previously named that's relevant. Skip if MemPalace is not yet initialized (early sessions before S-0002 close). **Mechanically backstopped by `mempalace_boot_query_skipped` soft-warn (per ADR 0056, S-0078)** — `engine/tools/hooks/post-mempalace-tool-use.sh` records the call to `engine/session/current_mempalace.jsonl`; `validate.py --final-check` at shutdown step 7 emits the soft-warn if no `mempalace_search` call landed.

   **Boot-search orchestrator (per ADR 0056 S-0093 amendment, Issue #38).** Invoke [`engine/tools/mempalace_boot_search.py`](../tools/mempalace_boot_search.py) at this step. The orchestrator runs three formulations of the work-item phrase (literal / conceptual / adjacent) through `mempalace.mcp_server.tool_search` with `min_similarity=0.6`, filters returned drawers, and writes an idempotent `## Prior context (MemPalace boot search)` section into `engine/session/current_plan.md`. JSONL telemetry shim writes one entry per formulation to `current_mempalace.jsonl` so `search_calls` increments correctly (the orchestrator imports `tool_search` directly, bypassing the PostToolUse hook). The AI reads the section before authoring the session plan; surfaced drawers that bear on the work get cited in plan rationale or commit messages, satisfying the closed-loop `mempalace_zero_citations_after_search` audit at shutdown.

3b. **Read recent diary entries.** Per [`mempalace-operations.md`](mempalace-operations.md) "Project usage scope" (diary adopted at S-0032). Call `mempalace_diary_read agent_name="claude" last_n=3` to see the previous three sessions' first-person AI reflections — what surprised the prior AI, what they noticed but deferred, what felt load-bearing for this session, where their judgment was uncertain. Surface anything that bears on the work about to be claimed; skip silently when the diary is empty (early adoption window). **Mechanically backstopped by `mempalace_diary_read_skipped` soft-warn (per ADR 0056, S-0078).**

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
     "working_on": "<one-sentence summary>",
     "declared_scope": "<1-3 sentences naming what this session commits to deliver. Optionally end with `phase: <id>` matching a build_plan/MANIFEST.md identifier (e.g., `phase: P_3` or `phase: 4.5`); use `phase: NA-...` for operational/engine-apparatus work that doesn't map to a build-plan phase.>",
     "outcome_summary": null,
     "scope_delivery": null,
     "approved_plan": "<path or null>",
     "branch": "<current git branch>",
     "worktree": "<absolute path>"
   }
   ```

   The `declared_scope` field is required from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The validator's `empty_declared_scope` soft-warn fires every commit until the field is populated; the `phase_mismatch_declared_scope` soft-warn fires when a `phase:` token doesn't match the build-plan manifest. Both checks are scope-discipline backstops — the field is the boot-time declaration that the shutdown-time scope-delivery audit will compare against.

   The `scope_delivery` field starts as `null` (in-flight) and is populated at shutdown with `{"delivered": bool, "user_confirmed_changes": bool, "explanation": str}` per the shutdown-sequence audit step.

4. Stage both files. Commit:

   ```
   chore(session): eager-claim S-<NNNN> — <topic>
   ```

5. Fast-forward main on the parent repo:

   ```bash
   git -C <parent-repo-path> merge --ff-only <branch>
   ```

6. Push:

   ```bash
   git -C <parent-repo-path> push origin main
   ```

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

### Pre-commit hook symlink

The hook itself lives at [`tools/hooks/pre-commit`](../tools/hooks/pre-commit) (tracked). The parent repo's `.git/hooks/pre-commit` is a symlink to that path; worktrees share the parent's `.git/hooks/` directory, so one symlink covers every worktree.

On a fresh clone, or if `readlink .git/hooks/pre-commit` shows a broken target (for example, a removed worktree), restore the symlink from the parent repo root:

```bash
cd .git/hooks
rm -f pre-commit
ln -s ../../tools/hooks/pre-commit pre-commit
```

Verify: `head -3 .git/hooks/pre-commit` resolves and prints the bash shebang plus the Paideia hook header.

### MemPalace capture-hook failure log

The Stop and PreCompact hooks invoke [`tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh), which always exits 0 to the harness and routes capture failures (binary missing, daemon down, capture errored) to `.claude/logs/mempalace-hook.log`. The log is gitignored per-clone state.

At session boot, after reading STATE.md and before the MemPalace context query, check the log. If `.claude/logs/mempalace-hook.log` exists and is non-empty, surface its contents to the user — capture may have failed silently in earlier sessions running from this worktree, and the conversational substrate they recorded may be missing from MemPalace.

```bash
test -s .claude/logs/mempalace-hook.log && cat .claude/logs/mempalace-hook.log
```

Acknowledged entries can be cleared by truncating the file (`: > .claude/logs/mempalace-hook.log`); fresh failures will append on the next hook fire. Persistent failures usually mean the `mempalace` binary is not in PATH from the harness's environment or the MemPalace daemon is not running — see [`mempalace-operations.md`](mempalace-operations.md) for diagnosis steps.

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — close-of-session protocol.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — what to do with hard-fails and soft-warns.
- [`escalation-criteria.md`](escalation-criteria.md) — when to interrupt the user mid-session.
- `.claude/commands/start-engine.md` — the slash command implementation.
