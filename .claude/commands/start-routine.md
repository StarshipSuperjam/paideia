---
description: Convert this conversation to a routine-mode session — read auto_target.json, pick the next eligible task, run plan-then-scope-check, execute or exit gracefully without claiming.
---

# /start-routine

Convert the current Claude Code conversation into a routine-mode session per [ADR 0051](../../engine/adr/0051-routine-mode-and-engine-loop.md). Routine-mode sessions are unattended Claude Code sessions fired by a Claude Code Routine on a cadence; each fired session reads a frozen target contract at `engine/session/auto_target.json`, picks the next eligible task, runs plan-then-scope-check, executes or exits gracefully without claiming.

## When to invoke

The user-created Claude Code Routine's "Instructions" field invokes this command. The routine fires on cadence (Manual or Hourly) and the spawned session enters here.

**Do not invoke `/start-routine` interactively.** Interactive sessions go through `/start-engine`. If you want to author or edit a target file (master plan session), that's a `/start-engine` interactive session — the master plan session is what authors the target that subsequent routine sessions execute against.

## How to run it

**Invoke the `routine-mode-lifecycle` Skill now, via the Skill tool.** That Skill carries the canonical, executable boot procedure; this command body deliberately carries **no step list of its own** so it cannot drift out of sync with the canonical procedure (the drift that produced [Issue #122](https://github.com/StarshipSuperjam/paideia/issues/122), [#123](https://github.com/StarshipSuperjam/paideia/issues/123), and [#124](https://github.com/StarshipSuperjam/paideia/issues/124) — a stale subset enumeration that silently dropped boot gates and MemPalace boot steps). The Skill is `disable-model-invocation: true`, so it does not auto-fire on description match — you must invoke it deliberately at this point.

The Skill's procedure covers, in order:

- **Boot gates** — boot-freshness (0a), concurrency-lock acquire (0b), wedge detection (0c).
- **Eligibility** — routine-mode precondition / pause / target-met / max-sessions checks, then eligible-task selection.
- **MemPalace boot** — boot query (5.5) and diary read (5.6), run *before* plan authoring so prior context informs the work.
- **Plan-then-scope-check** — write `engine/session/current_plan.md`, run `check_routine_scope.py --plan`.
- **Eager-claim** — claim the slot and push via the lifecycle wrapper.
- **Execute** — do the task's work within `scope_lock`.
- **Verify completion** — re-run task criteria; stage the `auto_target.json` status flip (it rides with the close commit).
- **Shutdown** — the standard shutdown sequence, ending with the concurrency-lock release.

The Layer 1 source-of-truth prose for every step lives at [`engine/operations/routine-mode-operations.md`](../../engine/operations/routine-mode-operations.md). The Skill mirrors it per [ADR 0044](../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) (recipe-vs-reference); updates flow doc → skill, never the reverse.

## When NOT to use this command

- **Authoring or editing the master plan.** That's `/start-engine` (interactive). The master plan session writes `auto_target.json` and `engine/build_readiness/<phase>.md`; subsequent routine sessions execute against the result.
- **A routine session is already in progress.** The Skill's boot gates (concurrency lock, eager-claim race recovery) handle concurrent fires; see [`routine-mode-operations.md`](../../engine/operations/routine-mode-operations.md) "Concurrency control" and "Mixing interactive and routine sessions".
- **`auto_target.json` is absent.** The Skill's precondition check catches this; the session exits 0 without claiming. The user probably intended `/start-engine`.

## Posture, permission mode, and interrupt criteria

Routine-mode posture (scope-lock invariance, operational allowlist, `gh issue create` authorization, HANDOFF authorization, master-plan-revisions-only-via-HANDOFF), the `Default`-not-`plan` permission-mode posture, and the auto-mode interrupt criteria all live in the [`routine-mode-lifecycle`](../skills/routine-mode-lifecycle/SKILL.md) Skill and the Layer 1 doc [`routine-mode-operations.md`](../../engine/operations/routine-mode-operations.md). They are not duplicated here — the Skill is the single source for the routine-mode contract.
