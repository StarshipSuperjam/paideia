---
name: routine-mode-lifecycle
description: Boot a Paideia routine-mode session — read auto_target.json, pick the next eligible task, run plan-then-scope-check, claim the slot if eligible or exit gracefully without claiming. Invoke at session boot when /start-routine has been called by a Claude Code Routine.
disable-model-invocation: true
---

# routine-mode-lifecycle

> Canonical executable form of the Paideia routine-mode boot procedure. The Layer 1 source-of-truth prose lives at [`engine/operations/routine-mode-operations.md`](../../../engine/operations/routine-mode-operations.md) per [ADR 0036](../../../engine/adr/0036-expression-contract-for-inward-documents.md). This skill body is the procedural form of the same procedure per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Updates flow doc → skill, never the reverse.
>
> Architecturally distinct from [`session-build-lifecycle`](../session-build-lifecycle/SKILL.md) per S-0044 user direction: routine-mode invocations route through `/start-routine` and this skill; interactive build sessions route through `/start-engine` and `session-build-lifecycle`. The two share the eager-claim ritual (step 8 below) but differ in everything else.

## When to invoke

A routine-mode session is any conversation spawned by a Claude Code Routine that types `/start-routine` (per [ADR 0051](../../../engine/adr/0051-routine-mode-and-engine-loop.md)). The routine's "Instructions" field invokes the slash command. Interactive sessions and exploration conversations do NOT run this lifecycle.

## Boot procedure (run in order)

### 0a. Boot-freshness gate (per ADR 0052)

Run `python3 engine/tools/routine_boot_freshness.py`. Mechanically fast-forwards the worktree to `origin/main` before any shared-state read. Per Issue #15 — the S-0054 loser session read stale `register_state.json` and re-claimed an already-taken slot.

- Exit 0 → proceed to step 0b.
- Exit 2 → HEAD has diverged from origin/main (real anomaly, not auto-recoverable). Write HANDOFF "routine boot refused: HEAD diverged from origin/main; needs human adjudication" with `**Disposition:** out-of-scope` → exit 0 without claiming.

### 0b. Concurrency lock (per ADR 0052)

Run `python3 engine/tools/routine_lock.py acquire`. Defense-in-depth against true concurrent fires (the residual case the freshness gate doesn't cover).

- Exit 0 → proceed to step 1. (Release happens at step 11 shutdown.)
- Exit 1 → another routine session is in progress. Log "another routine in progress, exiting cleanly" → exit 0 without claiming. No commit, no shared-state writes.

### 1. Detect routine-mode preconditions

Confirm `engine/session/auto_target.json` exists at repo root. If absent → log "no target file; routine has nothing to do (interactive sessions use /start-engine)" → exit 0 without claiming any slot.

### 2. Pause check

Read `auto_target.json`. If `paused: true` → log "target paused for `<target_id>`, no claim" → exit 0.

### 3. Target-met check

Run `python3 engine/tools/check_target.py`. If every task in the target file is `complete` AND every criterion still passes → log "target met for `<target_id>`, no claim" → exit 0.

The `check_target.py` exit code is 0 when every task's criteria all pass; non-zero when at least one criterion fails. Use the exit code AND the per-task `status` field together — a task with `status == complete` whose criteria now report failing means the work has regressed; that's a Tier-1 escalation (write HANDOFF + exit), not a "pick this task" eligibility match.

### 4. Max-sessions check

Count routine-mode session archives matching the active `target_id` in `engine/session/archive/`. If reached `max_sessions` → write a HANDOFF entry "max_sessions reached for `<target_id>`" with valid Disposition (`tracked-as-issue #<n>` if a follow-up Issue was filed; otherwise `deferred-with-user-confirmation` and reference the absent confirmation in the body) → exit 0.

### 5. Eligibility selection

Walk tasks in order. Pick the first whose `status == pending` AND every task id in `depends_on` has `status == complete`. None found (all remaining `blocked` or unsatisfied dependencies) → write HANDOFF "no eligible task in `<target_id>`" → exit 0 without claiming.

### 6. Plan authoring

Write a session plan to `engine/session/current_plan.md`:

```text
paths_to_modify: ["<glob>", ...]
criteria_addressed: [<index>, ...]

<prose rationale: why these paths address these criteria for this task>
```

The plan is the externalization-as-quality-gate equivalent of plan mode. Be specific — list the exact globs you intend to touch (not `**/*` wildcards), and the exact criterion indices you intend to satisfy.

### 7. Boot-time scope-check

Run `python3 engine/tools/check_routine_scope.py --plan engine/session/current_plan.md`. Exit 0 → proceed to step 8. Non-zero → write HANDOFF "scope-check failed: `<reason>`" with valid Disposition → exit 0 without claiming.

### 8. Eager-claim ritual

Same procedure as `/start-engine` (see [`session-build-lifecycle`](../session-build-lifecycle/SKILL.md) "Eager-claim ritual"). Three differences:

- **Mark the active task `in_progress` in `auto_target.json` as part of the claim commit.** Single commit covers register_state.json, current.json, AND auto_target.json status update.
- **Set `current.json.working_on`** to a one-line description naming the task: `"Routine task <task_id>: <task_name>"`.
- **Set `current.json.declared_scope`** from the task's `scope_lock.allowed_paths` plus a one-line summary. End with `phase: <id>` if the target's `target_id` corresponds to a build_plan/MANIFEST.md phase, else `phase: NA-routine`.

Commit message: `chore(session): eager-claim S-<NNNN> — routine task <task_id>`. FF main, push.

**Push-rejection branch (per ADR 0052):** if `git push origin main` is rejected with "Updates were rejected because the tip of your current branch is behind its remote counterpart" or similar, run `python3 engine/tools/routine_eager_claim_recovery.py`.

- Exit 0 → recovery complete (HEAD reset to origin/main; loser commit gone). Run `python3 engine/tools/routine_lock.py release` and exit cleanly without re-claiming.
- Exit 2 → ambiguous state (multiple commits ahead, or shape doesn't match). Write HANDOFF "eager-claim race recovery refused: ambiguous state" with `**Disposition:** out-of-scope`, run `routine_lock.py release`, exit 0.

### 9. Execute the work

The pre-commit hook re-runs `check_routine_scope.py --staged` against staged files (`task.scope_lock.allowed_paths` ∪ operational allowlist) and the master-plan-integrity check on `auto_target.json`.

**Operational allowlist** (always permitted):
- `engine/session/current.json`
- `engine/session/current_plan.md`
- `engine/session/auto_target.json` (status fields only)
- `engine/session/archive/S-*.json`
- `engine/session/register_state.json`
- `engine/ENGINE_LOG.md`
- `HANDOFF.md`

**Discovered findings outside current task scope** → `gh issue create` per [ADR 0048](../../../engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) issue-discipline. No tracked files touched. Continue with assigned task.

**Genuine blockers** (cannot complete current task) → mark task `blocked: <reason>`, write HANDOFF entry with valid Disposition, proceed to step 11 (early shutdown).

### 10. Verify completion

After the work commits clean: re-run task criteria via `python3 engine/tools/check_target.py --task-id <id>`. All pass → mark task `complete` in `auto_target.json` (commit). Any fail → mark `blocked: <reason>` (commit) + write HANDOFF.

### 11. Run the standard shutdown sequence

Same as `/start-engine` close per [`session-shutdown-sequence`](../session-shutdown-sequence/SKILL.md):

- Audit pass (`validate.py`)
- Spot-check
- Update `engine/STATE.md` (next-session pointer + last-session line)
- Update `engine/ENGINE_LOG.md` under `[Unreleased]`
- Fill `outcome_summary` in `current.json` (~50 words)
- Archive `current.json` → `engine/session/archive/S-<NNNN>.json`
- Final commit + main FF + push
- **Last action**: `python3 engine/tools/routine_lock.py release` (per ADR 0052; releases the lock acquired at step 0b so the next routine fire can claim it).

Issues created during the session count into `outcome_summary` for shutdown review.

## Routine-mode posture (load-bearing)

- **`scope_lock` is invariant on task-deliverable paths.** Pre-commit hook hard-fails commits touching paths outside the active task's `scope_lock.allowed_paths` ∪ the operational allowlist.
- **`gh issue create` is explicitly authorized** for in-band discoveries.
- **HANDOFF additions are explicitly authorized** for blockers, scope-expansion-needed, decision-required.
- **Master plan revisions ONLY via HANDOFF — never unilateral edits.** Pre-commit hook hard-fails any routine commit to `auto_target.json` that diffs keys other than `tasks[*].status` and `tasks[*].blocked_reason`.

## Permission-mode posture

Routines run in Claude Code's `Default` permission mode, NOT `plan` mode. Plan mode requires human `ExitPlanMode` approval that an unattended session cannot provide. The plan-then-scope-check (steps 6–7) is the externalization-as-quality-gate equivalent — mechanically enforced by `check_routine_scope.py` rather than human-gated.

## Auto-mode interrupt criteria

While running unattended, the AI may NOT pause and escalate to the user EXCEPT for:

- **Destructive-action confirmation:** `rm -rf`, `git reset --hard`, force-push. Refuse and write HANDOFF "destructive-action-required" instead.
- **Genuine blocker:** mark task `blocked: <reason>`, write HANDOFF, exit cleanly.
- **Scope-expansion-needed:** mark task `blocked: scope-expansion-needed: <reason>`, write HANDOFF, exit cleanly.
- **Decision required:** mark task `blocked: decision-required: <reason>`, write HANDOFF, exit cleanly.

There is no human in the loop. Surface findings via Issue or HANDOFF; the next interactive (`/start-engine`) session adjudicates.
