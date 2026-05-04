# Routine-mode operations

> Layer 1 contract per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md). Reference doc — describes the routine-mode session pattern, the master-plan-session procedure, the per-task target contract, and the apparatus that enforces anti-rogue safeguards. Not a Skill.
>
> Companion ADR: [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md). Schema reference: [`engine/session/auto_target.schema.md`](../session/auto_target.schema.md).

## What routine-mode is

A third session mode alongside `exploration` (default — no commits) and `build` (`/start-engine` — full lifecycle). Routine sessions are unattended Claude Code sessions fired on a cadence by a Claude Code Routine. Each fired session reads a frozen target contract at [`engine/session/auto_target.json`](../session/auto_target.json), picks the next eligible task, runs plan-then-scope-check, executes or exits.

The motivating use case: dispatching Phase 5's eight subdomain seeds (and similar multi-session batches) over hours of unattended runtime, on subscription billing, without spawning rogue work in the gap between target completion and the user's next interactive check-in.

The routine itself is a first-party Claude Code feature (Routines / scheduled tasks). The user creates and configures the routine in the Claude Code UI; this project supplies the boot procedure, target schema, and mechanical safeguards that make routine-mode safe to leave unattended.

## When to use it

Use routine mode for batched mechanical work: a sequence of tasks each defined by objective acceptance criteria, with scope-locks the routine session can't expand, where wall-clock parallelism is unnecessary or undesirable. Phase 5's seed authoring is the canonical example.

Do **not** use routine mode for:

- **Architectural decisions.** ADR authoring, OQ resolution, contract changes — these need the user in plan mode. Tasks containing controversial decision points belong in interactive sessions.
- **Open-ended exploration.** "Investigate X and tell me what you find" has no objective acceptance criterion. Routine sessions need a target they can mechanically verify.
- **Master-plan revisions.** A routine session that discovers the master plan is wrong writes a HANDOFF entry and exits. The next interactive session adjudicates.

## The two-layer pattern

### Layer 1 — master plan session (interactive, per phase)

A single interactive session, run in plan mode with the user, that authors:

1. [`engine/session/auto_target.json`](../session/auto_target.json) — the executable contract (frozen task list, scope_locks, dependencies, criteria). Schema at [`auto_target.schema.md`](../session/auto_target.schema.md).
2. [`engine/build_readiness/<phase>.md`](../build_readiness/) — the human-readable rationale (cross-cutting conventions, anti-patterns, bridge-concept ownership rules, anti-rogue specifics for the phase). Aligns with the ADR 0040 build-readiness-gate posture; routine sessions read both files at boot.

Master plan sessions are themselves regular `/start-engine` build sessions; they happen to author target/readiness artifacts as their primary deliverable. The session that does this is interactive — there is no chicken-and-egg of "routine session bootstraps the routine target."

### Layer 2 — routine engine loop (unattended, per task)

The Claude Code Routine fires on cadence (Manual or Hourly). Each fire:

1. Detects routine-mode (auto_target.json + current_plan.md + an in_progress task).
2. Walks task eligibility against the target's dependency graph.
3. Writes a session plan, runs `check_routine_scope.py --plan` against it.
4. On pass: claims a slot per the existing eager-claim ritual, executes, runs criteria, marks `complete` or `blocked`, closes.
5. On fail or no eligible task: writes HANDOFF, exits without claiming.

Routine sessions never edit the master plan. Status fields and `blocked_reason` are the only writable surfaces; `check_routine_scope.py --staged` enforces this at commit time.

## Routine boot procedure

This is referenced by [`session-build-lifecycle.md`](session-build-lifecycle.md) as the routine-mode branch. The exact sequence:

1. **Detect mode.** `engine/session/auto_target.json` exists → routine-mode candidate; else fall through to standard interactive boot.
2. **Pause check.** Target `paused: true` → log "target paused, no claim" → exit 0.
3. **Target-met check.** Run `check_target.py` against every task; every task `status == complete` AND its criteria still pass → log "target met, no claim" → exit 0.
4. **Max-sessions check.** Count routine-mode sessions in `engine/session/archive/` matching the current `target_id`; ≥ `max_sessions` → write HANDOFF "max_sessions reached for `<target_id>`" → exit 0.
5. **Eligibility selection.** Walk tasks in order; pick the first whose `status == pending` AND `depends_on` are all `complete`. None found → write HANDOFF "no eligible task" → exit 0.
6. **Plan authoring.** Write a session plan to [`engine/session/current_plan.md`](../session/current_plan.md) with fields:
   - `paths_to_modify: [<glob>, ...]` — every file the session intends to touch
   - `criteria_addressed: [<criterion_index>, ...]` — indices into the active task's criteria list
   - prose rationale (free-form; ignored by the checker)
7. **Scope-check.** Run `engine/tools/check_routine_scope.py --plan engine/session/current_plan.md`. Exit 0 → proceed; non-zero → write HANDOFF "scope-check failed: `<reason>`" → exit 0.
8. **Claim slot.** Standard eager-claim ritual: bump `register_state.json`, write `engine/session/current.json`, mark task `in_progress` in target file, commit, FF main, push.
9. **Execute work.** Pre-commit hook re-runs `check_routine_scope.py --staged` against staged files (task scope_lock ∪ operational allowlist). Out-of-scope discoveries route to `gh issue create`. Genuine blockers route to HANDOFF + mark task `blocked` + early shutdown.
10. **Verify completion.** After work commits clean: re-run task criteria via `check_target.py --task-id <id>`. All pass → mark task `complete` (commit). Any fail → mark `blocked: <reason>` (commit) + write HANDOFF.
11. **Shutdown.** Run the standard shutdown sequence per [`session-shutdown-sequence.md`](session-shutdown-sequence.md). Issues created during the session count into `outcome_summary` for shutdown review.

## Scope-lock model

Two classes of paths matter at commit time:

**Task-deliverable** — controlled by the active task's `scope_lock.allowed_paths`. The work artifact (e.g., `engine/migrations/0042_*`).

**Operational** — always allowed for routine sessions, regardless of which task is active. The apparatus the session itself runs on:

- `engine/session/current.json`
- `engine/session/current_plan.md`
- `engine/session/auto_target.json` (status field updates only — master-plan-integrity check enforces)
- `engine/session/archive/S-*.json`
- `engine/session/register_state.json`
- `engine/ENGINE_LOG.md`
- `HANDOFF.md`

A staged file is permitted iff it matches **either** the active task's `scope_lock.allowed_paths` **or** the operational allowlist. Pattern matching is segment-aware: `*` matches any non-`/` characters within a segment; `**` matches zero or more whole segments.

## Discovered-issues triage in routine mode

A routine session that, mid-task, notices something out of scope (a bug elsewhere, dead config, stale docs, security concern, tech-debt item) **must not crash and must not paper over**. Same triage rules as ADR 0048's existing issue-discipline:

- **Outside current task scope** → `gh issue create` with the appropriate label (`bug`, `tech-debt`, `cleanup`, `enhancement`, `priority:urgent`). No tracked files touched. Continue with assigned task.
- **Inside current task scope** → default to fix-in-context per CLAUDE.md.
- **Genuine blocker** → mark task `blocked: <reason>`, write HANDOFF entry with valid Disposition, exit cleanly. User adjudicates next interactive session.
- **Validate.py soft-warns** → record in `outcome_summary` per ADR 0042.

`gh issue create` is permitted unilaterally in routine mode — CLAUDE.md's routine-mode posture authorizes this explicitly.

**Backstop against issue spam**: `validate.py` soft-warns when a routine session creates more than 3 issues. Real concern (legitimate fix-this-many findings) overrides; the warn just surfaces "this session was unusually noisy" for human review.

## Anti-rogue mechanical safeguards

| Layer | Mechanism | What it prevents |
|---|---|---|
| Boot-time | `check_routine_scope.py --plan` on the session plan | Session embarks on out-of-scope work |
| Commit-time | Pre-commit hook with `check_routine_scope.py --staged` (task scope ∪ operational allowlist) | Out-of-scope task-deliverable file lands |
| Master-plan integrity | Pre-commit hook hard-fails routine-mode commit to `auto_target.json` diffing keys other than `tasks[*].status` and `tasks[*].blocked_reason` | Routine session unilaterally edits master plan |
| HANDOFF integrity | Existing `audit_handoff_dispositions.py` (per ADR 0048) | HANDOFF entries lacking proper Disposition |
| Issue-spam | `validate.py` soft-warn at >3 issues created per session | Confused session floods backlog |
| Validate-time | `validate.py` soft-warn: routine-mode session committed without referencing the active task in its plan | Routine session ran without target alignment |

## Criterion catalog

Five types ship at landing. New types are one Python function in [`check_target.py`](../tools/check_target.py)'s `CRITERION_TYPES` dict plus a test. The `predicate` type is the explicit escape hatch for criteria that don't fit the four named types.

| Type | Use | Notes |
|---|---|---|
| `migration_applied` | `{type, id}` | Queries Supabase migration history; `SUPABASE_DB_URL` required. Cannot-verify reports as not-satisfied. |
| `validate_passes` | `{type}` | Runs `validate.py`; passes iff zero hard-fails. Soft-warns advisory. |
| `adr_status` | `{type, id, status}` | Reads ADR file `Status:` line. `status: "*"` accepts any non-empty value. |
| `file_exists` | `{type, path}` | Literal path check, no glob expansion. |
| `predicate` | `{type, name, params}` | Looks up `name` in `PREDICATE_REGISTRY`; calls with `params` as kwargs. |

Schema details and the full predicate registry convention live in [`auto_target.schema.md`](../session/auto_target.schema.md).

## Routine UI configuration

The Claude Code Routine that drives the engine loop is configured once and reused across phases. Recommended settings:

| Field | Value | Notes |
|---|---|---|
| Name | `paideia-engine-loop` | Persistent identifier. |
| Description | "Paideia engine session — reads auto_target.json, executes next eligible task or exits gracefully." | One line. |
| Instructions | `/start-routine` (single line; the slash command body handles the rest) | Generic. Phase-specific work is in the target file, not the instructions. |
| Ask permissions | Default | The routine procedure's complete Bash command surface is pre-allowlisted in [`.claude/settings.json`](../../.claude/settings.json) `permissions.allow` per S-0046 (see [Harness permission allowlist](#harness-permission-allowlist) below). Plan mode would deadlock unattended. |
| Folder | Project root | Routine sessions need access to engine/. |
| Worktree | ✅ checked | Project uses worktrees; matches existing posture. |
| Schedule | Manual until S-0044 lands; Hourly thereafter | 24/day is plenty; eager-claim handles overlap. |

To **pause** the loop without disabling the routine in the UI: edit `auto_target.json` and set `paused: true`. Routine fires continue but exit immediately.

To **swap targets** (one phase ends, another begins): the master plan session for the new phase replaces `auto_target.json`. There is no stacked-target support; one target at a time.

## Mixing interactive and routine sessions

The current apparatus assumes **one active session at a time**. Starting an interactive session while a routine session is `in_progress` will corrupt shared state — interactive's eager-claim writes a new `engine/session/current.json` and bumps `register_state.json`, overwriting the routine session's view of which slot it owns. The routine session's commit/shutdown will then fail or write incorrect archive data.

The existing "Eager-claim race" recovery in [`session-build-lifecycle.md`](session-build-lifecycle.md) covers two sessions racing for the *same* slot at boot. It does **not** cover a fresh session starting while another is already `in_progress`.

### Safe procedure (starting interactive mid-routine)

1. **Pause the routine.** Edit [`engine/session/auto_target.json`](../session/auto_target.json), set `paused: true`, commit. The pause check is the very first step of the routine boot procedure; subsequent fires exit immediately without claiming.
2. **Wait for any in-flight routine session to finish.** Confirm via [`engine/session/register_state.json`](../session/register_state.json) — `current_status` flips from `in_progress` to `closed` at session shutdown. Typical wait: under one hour. Check `engine/session/archive/` for the closed S-NNNN.json archive as the definitive signal.
3. **Run `/start-engine` interactively.** The pause holds, no routine fires interfere.
4. **At interactive close, decide whether to resume.** Set `paused: false` and commit if you want the loop to continue, or leave it paused if you're between phases.

### What to do if you forgot to pause

If you've already started interactive while routine is `in_progress` and notice the collision:

- **Don't run substantive work yet.** The slot claim has corrupted the routine session's state, but interactive can still recover cleanly if you abort before authoring anything.
- **Inspect `engine/session/current.json`** — if it carries the *interactive's* claimed id (rather than the routine's), the routine has been clobbered.
- **Escalate to recovery.** The routine session's worktree still holds its in-flight work locally; the user can decide whether to manually preserve it (via `git stash` or branch save) before reconciling state. Preferred path: let the interactive session run, document the collision in `outcome_summary`, and re-run the routine task at the next routine fire (it will re-pick the now-orphaned `in_progress` task and either resume or mark `blocked`).

### Mechanical safeguard (landed at S-0048 per Issue #3)

[`engine/tools/check_session_conflict.py`](../tools/check_session_conflict.py) inspects `engine/session/register_state.json` + `engine/session/current.json` and emits one of three dispositions: exit 0 (no conflict), exit 1 (recent collision <1h or mid-window ambiguity 1h–24h), exit 2 (stale >24h, likely dead session — offer auto-recovery).

Wired in two places:

- **[`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh)** runs the check after the cadence-trigger surface and before the shared-state probe. The hook surfaces stderr from the tool but always exits 0 (per its "never blocks" design); the AI sees the surface at boot.
- **[`.claude/commands/start-engine.md`](../../.claude/commands/start-engine.md) step 4b** + **[`engine/operations/session-build-lifecycle.md`](session-build-lifecycle.md) step 5b** both run the tool *before* the eager-claim ritual and refuse the claim on exit 1; offer auto-recovery on exit 2. The procedural cooperation rule above remains the human-mediated safety belt for the cases the mechanical safeguard cannot handle (e.g., user explicitly overriding to claim despite a recent rival).

## Harness permission allowlist

**Operational stance for routine sessions: Auto permission mode.** Project-level mechanical safeguards are the load-bearing anti-rogue layer; the harness allowlist in [`.claude/settings.json`](../../.claude/settings.json) is supplementary and serves *interactive* sessions, not unattended routines. The allowlist remains in tree because interactive `/start-engine` sessions still benefit from it; routine sessions sidestep it via Auto mode rather than relying on it.

### Why Auto mode for routine sessions (the journey through S-0044 → S-0046 → S-0048)

S-0044 shipped the routine-mode foundation assuming an allowlist would handle the unattended permission gap (*"Ask permissions: Default — Use `.claude/settings.local.json` allowlist for routine's needs"* in the original UI configuration table). That sentence shipped a load-bearing assumption without authoring the allowlist; the first manual routine fire after S-0045 master plan deadlocked at the very first Bash invocation. S-0046 authored a comprehensive 60+ pattern allowlist to close the gap.

The first manual fire after S-0046's allowlist landed *still* deadlocked — on the same target-met boot step. Root cause: the AI inside a routine session naturally uses compound Bash forms (`python3 engine/tools/check_target.py; echo "EXIT: $?"` to capture exit codes; `cmd1 && cmd2` to chain dependent steps), and the harness's permission system matches the *whole* compound command against patterns rather than the leading prefix. Adding patterns for every variation never converges — the AI's compound-form vocabulary outpaces enumeration. (Issue #6 documents the realization.)

The post-S-0048 stance: **configure the routine in Auto permission mode.** The harness no longer gates Bash execution; project-level safeguards remain operational regardless and cover what matters:

- [`engine/tools/check_routine_scope.py --plan`](../tools/check_routine_scope.py) at boot — refuses to claim if the plan touches paths outside the active task's `scope_lock.allowed_paths`.
- [`engine/tools/check_routine_scope.py --staged`](../tools/check_routine_scope.py) at every commit (pre-commit hook) — hard-fails the commit if staged paths fall outside scope ∪ operational allowlist.
- Master-plan-integrity check (pre-commit hook) — hard-fails any routine commit to [`engine/session/auto_target.json`](../session/auto_target.json) that diffs keys other than `tasks[*].status` and `tasks[*].blocked_reason`.
- [`engine/tools/audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py) at session shutdown — hard-fails if any new HANDOFF section lacks a recognized `Disposition:` line (per ADR 0048).
- [`engine/tools/validate.py`](../tools/validate.py) soft-warns (`routine_no_target_reference`, `routine_issue_spam`) — defense in depth at validate-time.
- Eager-claim atomic protocol — slot reservation via git, immune to harness-mode.

None of those depend on harness permissions. Destructive operations (`rm -rf`, `git reset --hard`, force-push) are not in the routine procedure and the [routine-mode-lifecycle Skill](../../.claude/skills/routine-mode-lifecycle/SKILL.md) explicitly refuses them and writes HANDOFF instead — Auto mode does not enable them either, because the Skill body governs whether the AI even *attempts* them.

### Trade-off: what Auto mode permits vs what project safeguards prevent

| Surface | Auto mode permits | Project safeguard prevents |
|---|---|---|
| Routine task work within `scope_lock.allowed_paths` | yes | n/a — by design |
| Edits outside `scope_lock.allowed_paths` | yes (no harness gate) | `check_routine_scope.py --staged` hard-fails the commit |
| Master-plan body revisions via `auto_target.json` | yes (no harness gate) | pre-commit hook hard-fails (only `tasks[*].status`/`blocked_reason` may diff) |
| Destructive ops (`rm -rf`, `git reset --hard`, force-push) | yes (no harness gate) | Skill body refuses + writes HANDOFF |
| HANDOFF entry without `Disposition:` line | yes | `audit_handoff_dispositions.py` hard-fails at shutdown |
| `gh issue create` for in-band discoveries | yes | n/a — explicitly authorized per ADR 0048 |
| Arbitrary new Bash invocation from inside a routine | yes (no harness gate) | scope-lock + master-plan-integrity catch any staged-file consequences; the AI's Skill-body discipline catches the rest |

Auto mode eliminates the brittle compound-form mismatch; project safeguards still cover everything load-bearing; the Skill body covers the destructive-op gap that no project tool can mechanically detect at staging time. Routine-mode safety does not depend on harness permissions.

### Allowlist remains useful for interactive sessions

For interactive `/start-engine` sessions, **Default** permission mode + the existing `.claude/settings.json` allowlist remains the right posture. A human can answer permission prompts in real time; granular gating with the human-in-the-loop catches anomalies the project safeguards don't surface (typo'd commands, unexpected tool invocations). The S-0046 allowlist additions remain in `.claude/settings.json` for that purpose. They cover engine python tools, worktree-side git lifecycle, the test/lint stack, the GitHub Issues path, Supabase migration tooling, hook scripts, shell utilities, the MemPalace CLI, and `source engine/tools/scrub_env.sh`. The compound-form mismatch is less load-bearing under Default mode because the human-in-the-loop can approve a one-off compound that no pattern covers.

### Editing `.claude/settings.json` from a worktree

When a Claude Code session running in a git worktree edits `.claude/settings.json` via the Write tool, the harness redirects the write to the **main repo's** `.claude/settings.json` (where the harness reads from), not the worktree's local `.claude/settings.json` (where git tracks for the worktree's branch). Result: the worktree's tracked copy stays stale, `git status` from the worktree sees no change, `git add -A` captures nothing, and the close commit silently ships without the deliverable looking complete.

S-0046 hit this exactly — the 60+ pattern allowlist extension landed in main's copy but never made it into git; S-0047 manually patched. S-0048 mechanizes the catch with [`engine/tools/check_settings_sync.py`](../tools/check_settings_sync.py), invoked from the pre-commit hook: hard-fails any commit from a worktree where `<main>/.claude/settings.json` differs from the worktree's tracked copy AND the worktree's copy is not staged for the current commit.

**Procedure when editing `.claude/settings.json` from a worktree:**

1. Edit normally via the Write tool — the harness redirects to main's copy (this is fine).
2. Before staging the commit, sync main's copy into the worktree's tracked copy:
   ```bash
   cp <main_repo>/.claude/settings.json .claude/settings.json
   git add .claude/settings.json
   ```
   Replace `<main_repo>` with the absolute path of the main repo (e.g., `/Users/<you>/<project>`).
3. Commit. The pre-commit guard verifies the sync and passes.

If you forget the cp step, the pre-commit guard hard-fails with the exact procedure printed to stderr — no silent ship-as-no-op anymore. The guard is also a backstop for non-routine commits and applies to any session running from a worktree.

### Procedural rule (replaces the S-0046 same-commit pairing rule)

Adding a new Bash invocation to the routine procedure (Skill body, slash command body, criterion predicate that shells out, per-task `scope_lock` workflow) does **not** require an allowlist entry under the Auto-mode stance — the routine runs unprompted regardless. The addition *should* still ship a paired allowlist entry for the interactive-session ergonomics, but the absence does not deadlock the routine. The S-0046 same-commit pairing rule is hereby retired.

### What if a routine deadlocks on a permission prompt anyway

If a routine session deadlocks despite Auto-mode configuration:

1. **Verify the routine config is actually Auto.** Manual misconfiguration (Default selected by accident) is the most likely cause.
2. **If Auto is confirmed and the prompt still fires**, this is a harness-side anomaly worth reporting upstream. Deny the prompt, document in `outcome_summary`, and escalate.
3. **If the user has chosen Default mode for the routine** (e.g., during initial verification), extend `.claude/settings.json` with the missing pattern and any obvious siblings. Note that pattern proliferation is the cost paid for Default-mode rigor; once verification is complete, switch the routine back to Auto.

### Optional `routine_mode_misconfigured` soft-warn — infeasible

Considered: a `validate.py` soft-warn that fires when `auto_target.json` is present (routine-mode work staged/active) AND the routine config introspectively shows Default rather than Auto. Investigation surfaced no introspection path for permission mode — Claude Code Routines do not currently expose their mode to running code (no `$CLAUDE_PERMISSION_MODE` or equivalent env var; ADR 0051 §"Permission-mode posture" treats Default as fixed for the foundation). Detection from inside the project is therefore infeasible. The operational rule lives in this doc; the user is the gate when configuring the routine.

## Troubleshooting

**Routine fires but always exits "not in routine mode."**
Check three preconditions: `auto_target.json` exists; `current_plan.md` exists; at least one task has `status: in_progress`. The first two are present after the first routine-mode session; in a fresh state, the boot procedure writes both. The third is set by step 8 of the boot procedure (slot claim).

**Scope-check rejects a path that should be in scope.**
Verify the glob pattern. `*` is segment-bounded — `engine/migrations/0042_*` does NOT match `engine/migrations/0042/sub.sql`. Use `**` for cross-segment matching: `engine/migrations/0042_**`.

**Master-plan-integrity hard-fails a status update.**
The check permits `tasks[*].status` and `tasks[*].blocked_reason` only. Verify the diff isn't accidentally touching `tasks[*].name` or top-level fields. Common cause: pretty-printer reformatted the JSON; ensure the writer preserves the canonical key order and only mutates the intended fields.

**Routine session creates more than 3 issues.**
Soft-warn fires; commit lands. Review the issues; if legitimate, ignore. If the session is genuinely confused, abort by setting `paused: true` and adjudicate.

**Routine target completes but routine keeps firing.**
Expected. Each fire exits within seconds at step 3 (target-met check). Disable the routine in the UI between phases or leave it; cost is negligible.

**Eager-claim collision (next routine fires before previous completes).**
The existing eager-claim protocol handles this: routine N+1 reads register_state.json, sees the slot is claimed, exits cleanly. Routine N continues; routine N+2 picks up where N left off.

## See also

- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — the contract.
- [`auto_target.schema.md`](../session/auto_target.schema.md) — target file schema.
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure, including the routine-mode branch.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — shutdown sequence (unchanged from interactive sessions).
- [`build-readiness-gate.md`](build-readiness-gate.md) — gate posture; phase_5.md and successors inherit.
- [`issue-discipline.md`](issue-discipline.md) — HANDOFF vs Issue routing; routine sessions follow it unchanged.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn taxonomy; the new routine-mode soft-warns plug into this.
- [`engine/tools/check_target.py`](../tools/check_target.py), [`engine/tools/check_routine_scope.py`](../tools/check_routine_scope.py) — the foundation tools.
