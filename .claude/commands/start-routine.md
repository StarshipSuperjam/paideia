---
description: Convert this conversation to a routine-mode session — read auto_target.json, pick the next eligible task, run plan-then-scope-check, execute or exit gracefully without claiming.
---

# /start-routine

Convert the current Claude Code conversation into a routine-mode session per [ADR 0051](../../engine/adr/0051-routine-mode-and-engine-loop.md). Routine-mode sessions are unattended Claude Code sessions fired by a Claude Code Routine on a cadence; each fired session reads a frozen target contract at `engine/session/auto_target.json`, picks the next eligible task, runs plan-then-scope-check, executes or exits gracefully without claiming.

## When to invoke

The user-created Claude Code Routine's "Instructions" field invokes this command. The routine fires on cadence (Manual or Hourly) and the spawned session enters here.

**Do not invoke `/start-routine` interactively.** Interactive sessions go through `/start-engine`. If you want to author or edit a target file (master plan session), that's a `/start-engine` interactive session — the master plan session is what authors the target that subsequent routine sessions execute against.

## Boot procedure (the AI runs these in order)

The full Layer 1 source-of-truth lives at [`engine/operations/routine-mode-operations.md`](../../engine/operations/routine-mode-operations.md). The procedure is mirrored in the [`routine-mode-lifecycle`](../skills/routine-mode-lifecycle/SKILL.md) Skill. This command body is the user-facing entry point; run the steps in order.

1. **Detect routine-mode preconditions.** Confirm `engine/session/auto_target.json` exists. If absent → log "no target file; routine has nothing to do" → exit 0 without claiming. (User probably intended `/start-engine`.)

2. **Pause check.** Read `auto_target.json`. If `paused: true` → log "target paused, no claim" → exit 0.

3. **Target-met check.** Run `python3 engine/tools/check_target.py`. If every task is `complete` AND its criteria still pass → log "target met for `<target_id>`, no claim" → exit 0. The exit code is 0 from check_target when all-pass; non-zero when any criterion fails (which means there's still work to do, proceed).

4. **Max-sessions check.** Count routine-mode sessions in `engine/session/archive/` matching the active `target_id`. Reached `max_sessions` → write a HANDOFF entry "max_sessions reached for `<target_id>`" with valid Disposition, exit 0.

5. **Eligibility selection.** Walk tasks in order. Pick the first whose `status == pending` AND every entry in `depends_on` has `status == complete`. None found → write HANDOFF "no eligible task in `<target_id>`" → exit 0 without claiming.

6. **Plan authoring.** Write a session plan to `engine/session/current_plan.md`:

   ```text
   paths_to_modify: ["<glob>", ...]
   criteria_addressed: [<index>, ...]

   <prose rationale: why these paths address these criteria for this task>
   ```

7. **Boot-time scope-check.** Run `python3 engine/tools/check_routine_scope.py --plan engine/session/current_plan.md`. Exit 0 → proceed; non-zero → write HANDOFF "scope-check failed: `<reason>`" → exit 0 without claiming.

8. **Claim slot via the eager-claim ritual.** Same procedure as `/start-engine` (see [`engine/operations/session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md) "Eager-claim ritual"):
   - Read `engine/session/register_state.json`. Note `next_id`.
   - Bump to `next + 1`, set `last_claimed: "S-<next>"`, `current_status: "in_progress"`.
   - Write `engine/session/current.json` with the standard fields, including `declared_scope` per [ADR 0049](../../engine/adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). Set `working_on` to the active task's `name` and `id`. Set `declared_scope` from the task's scope_lock.allowed_paths plus a one-line summary.
   - Mark the task `in_progress` in `auto_target.json` (commit this together with the eager-claim).
   - Stage register_state.json + current.json + auto_target.json. Commit with message `chore(session): eager-claim S-<NNNN> — routine task <task_id>`. FF main, push.

9. **Execute the work.** The pre-commit hook re-runs `check_routine_scope.py --staged` against staged files (`task.scope_lock.allowed_paths` ∪ operational allowlist) and the master-plan-integrity check on `auto_target.json`. Out-of-scope discoveries route to `gh issue create` per [ADR 0048](../../engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md). Genuine blockers route to HANDOFF + mark task `blocked` + early shutdown per step 11.

10. **Verify completion.** After clean commit: re-run task criteria via `python3 engine/tools/check_target.py --task-id <id>`. All pass → mark task `complete` in `auto_target.json` (commit). Any fail → mark `blocked: <reason>` (commit) + write HANDOFF.

11. **Run the standard shutdown sequence.** Same as `/start-engine` close per [`engine/operations/session-shutdown-sequence.md`](../../engine/operations/session-shutdown-sequence.md): audit, spot-check, STATE.md update, ENGINE_LOG entry, archive `current.json` to `engine/session/archive/S-<NNNN>.json`, final commit + main FF + push. Issues created during the session count into `outcome_summary` for shutdown review.

## Routine-mode posture

- **`scope_lock` is invariant on task-deliverable paths.** Pre-commit hook hard-fails commits touching paths outside the active task's `scope_lock.allowed_paths` ∪ the operational allowlist.
- **Operational allowlist always permitted:** `engine/session/current.json`, `engine/session/current_plan.md`, `engine/session/auto_target.json` (status fields only — master-plan-integrity check), `engine/session/archive/S-*.json`, `engine/session/register_state.json`, `engine/ENGINE_LOG.md`, `HANDOFF.md`.
- **`gh issue create` is explicitly authorized** for in-band discoveries outside the current task's scope. No tracked files touched. Continue with assigned task.
- **HANDOFF additions are explicitly authorized** for blockers, scope-expansion-needed, decision-required signals. The existing `audit_handoff_dispositions.py` audit catches malformed entries.
- **Master plan revisions ONLY via HANDOFF.** Pre-commit hook hard-fails any routine commit to `auto_target.json` that diffs keys other than `tasks[*].status` and `tasks[*].blocked_reason`. The user adjudicates revisions in the next interactive (`/start-engine`) session.

## Permission-mode posture

Routines run in Claude Code's `Default` permission mode, NOT `plan` mode. Plan mode requires human `ExitPlanMode` approval that an unattended session cannot provide. The plan-then-scope-check (step 6 + 7) is the externalization-as-quality-gate equivalent — mechanically enforced by `check_routine_scope.py` rather than human-gated.

## When NOT to use this command

- **Authoring or editing the master plan.** That's `/start-engine` (interactive). The master plan session writes `auto_target.json` and `engine/build_readiness/<phase>.md`; subsequent routine sessions execute against the result.
- **A routine session is already in progress.** Eager-claim race recovery handles concurrent slot collisions; see [`session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md) "Recovery". For interactive-mid-routine, see [Issue #3](https://github.com/StarshipSuperjam/paideia/issues/3) and the procedural guidance in [`routine-mode-operations.md`](../../engine/operations/routine-mode-operations.md) "Mixing interactive and routine sessions".
- **Auto-target.json is absent.** Step 1 catches this; the session exits 0 without claiming. The user probably intended `/start-engine`.

## Auto-mode interrupt criteria

While running unattended, the AI may NOT pause and escalate to the user EXCEPT for:

- **Destructive-action confirmation:** `rm -rf`, `git reset --hard`, force-push, etc. — refuse and write HANDOFF "destructive-action-required" instead of executing.
- **Genuine blocker:** mark task `blocked: <reason>`, write HANDOFF, exit cleanly.
- **Scope-expansion-needed:** mark task `blocked: scope-expansion-needed: <reason>`, write HANDOFF, exit cleanly.
- **Decision required:** mark task `blocked: decision-required: <reason>`, write HANDOFF, exit cleanly.

There is no human in the loop to escalate to. Surface findings via Issue (`gh issue create`) or HANDOFF (with valid Disposition); the next interactive session adjudicates.
