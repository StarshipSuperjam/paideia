---
description: Convert this conversation to a build session — claims the next slot, allows commits and project file edits.
---

# /start-engine

Convert the current Claude Code conversation from default exploration mode (no commits, no project edits) into a build session (claims a slot, may commit, may modify project files) per [ADR 0044](../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Build sessions are interactive Claude Code sessions where the user has explicitly authorized work that mutates tracked files.

## When to invoke

The user types `/start-engine` (or `Start Engine`) to convert exploration into build. Default-mode (exploration) conversations do NOT run this lifecycle — they make no commits and claim no slot. The conversion is a deliberate user act; never auto-fire.

## How to run it

**Invoke the `session-build-lifecycle` Skill now, via the Skill tool.** That Skill carries the canonical, executable boot procedure; this command body deliberately carries **no step list of its own** so it cannot drift out of sync with the canonical procedure (the drift that produced [Issue #122](https://github.com/StarshipSuperjam/paideia/issues/122), [#123](https://github.com/StarshipSuperjam/paideia/issues/123), [#124](https://github.com/StarshipSuperjam/paideia/issues/124), and [#125](https://github.com/StarshipSuperjam/paideia/issues/125) — stale subset enumerations that silently dropped boot gates and engine_memory boot steps). The Skill is `disable-model-invocation: true`, so it does not auto-fire on description match — you must invoke it deliberately at this point.

The Skill's procedure covers, in order:

- **Boot reading** — `engine/STATE.md` (current phase, last build session, next-session work item).
- **Cadence trigger check** — health-check overdue-catchup logic against `last_audit_session`.
- **Persistent-warn surface** — soft-warn categories firing in 3-of-last-5 archives.
- **engine_memory boot** — `engine_memory_search` against next-session-work terms, then `engine_memory_diary_read last_n=3`, run *before* slot claim so prior context informs the work.
- **Build-readiness report check** — substantive build sessions only; halt on unresolved Tier 1.
- **Concurrent-session collision check** — `check_session_conflict.py` (exit 0/1/2 dispositions).
- **Eager-claim ritual** — bump `next_id`, write `current.json` with the canonical field set (`id`, `started_at`, `status`, `mode: "interactive"`, `working_on`, `declared_scope`, `outcome_summary: null`, `scope_delivery: null`, `next_session_handle: null`, `approved_plan`, `branch`, `worktree`), commit + FF parent + push via [`build_lifecycle_push.py eager-claim`](../../engine/tools/build_lifecycle_push.py) per [ADR 0076](../../engine/adr/0076-build-mode-lifecycle-push-wrapping.md).
- **Begin substantive work** — file edits, tools, incremental commits gated by pre-commit hook.

The Layer 1 source-of-truth prose for every step lives at [`engine/operations/session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md). The Skill mirrors it per [ADR 0044](../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) (recipe-vs-reference); updates flow doc → skill, never the reverse.

## How to close the session

**Invoke the `session-shutdown-sequence` Skill at end of work, via the Skill tool.** Same recipe-vs-reference pattern as the boot Skill: canonical executable procedure, `disable-model-invocation: true`, mirrors the Layer 1 doc [`engine/operations/session-shutdown-sequence.md`](../../engine/operations/session-shutdown-sequence.md). Covers validate.py audit, spot-check, `engine/STATE.md` update, per-session changelog entry at `engine/changelog/<YYYY>/S-NNNN-*.md` (per [ADR 0092](../../engine/adr/0092-per-session-changelog-directory.md)), `outcome_summary` fill, archive of `engine/session/current.json` → `engine/session/archive/S-NNNN.json`, structured-field audits per [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md), engine_memory diary write, final commit + FF + push via [`build_lifecycle_push.py close`](../../engine/tools/build_lifecycle_push.py).

## When NOT to use this command

- **Exploration / sketching.** No commits, no project edits — that's the default mode. The Stop/PreCompact hooks capture the conversation to engine_memory `room='work'` per [ADR 0091](../../engine/adr/0091-engine-memory-substrate-sqlite-fts5.md) so future sessions can recall the discussion without re-litigation.
- **A build session is already in progress.** The Skill's concurrent-session collision check catches this and refuses the eager-claim; see [`engine/operations/session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md) "Concurrent-session collision check" and `engine/tools/check_session_conflict.py`.
- **Routine-mode unattended work.** That's `/start-routine` (which the user's Claude Code Routine invokes on cadence). Routine and build sessions share only the eager-claim ritual; every other concern (boot procedure, scope rules, commit posture, permission model, shutdown logic) is mode-specific per [ADR 0051](../../engine/adr/0051-routine-mode-and-engine-loop.md).

## Posture, permission mode, and interrupt criteria

Build-mode posture (push authorization on `/start-engine`, auto-mode interrupt criteria, budget guidance percentages, standing pushback rule) lives in the [`session-build-lifecycle`](../skills/session-build-lifecycle/SKILL.md) Skill and the Layer 1 doc [`session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md), with cross-cutting standing rules in [`CLAUDE.md`](../../CLAUDE.md) "Standing rules". They are not duplicated here — the Skill is the single source for the build-mode contract.
