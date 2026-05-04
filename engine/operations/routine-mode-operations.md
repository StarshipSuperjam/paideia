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

### Mechanical safeguard (planned, not yet landed)

Tracked as [Issue #3](https://github.com/StarshipSuperjam/paideia/issues/3): `/start-engine` boot procedure should detect `current_status: in_progress` with a recent `started_at` (<1 hour) and refuse with an override prompt rather than blindly claiming the next slot. Same check belongs in `session-start.sh` for harness-side parity. Surfaced during S-0044 in response to "What if I start a manual interactive session while routine mode sessions are running?" — out of S-0044's scope so routed to Issue per ADR 0048 discovered-issues discipline. Until it lands, the procedural rule above is the safety belt.

## Harness permission allowlist

Routine sessions run unattended — no human is available to answer permission prompts. **Every Bash command the routine procedure invokes must be pre-allowlisted in [`.claude/settings.json`](../../.claude/settings.json) `permissions.allow`.** A single un-allowlisted command deadlocks the session at the prompt that never gets answered.

This is **distinct from** the project-level scope-lock and master-plan integrity checks per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md). Those gate *correctness* (does the AI's plan match the active task?). The harness allowlist gates *executability* (will the harness even let the AI run this command?). Both layers must pass.

### S-0044 lesson (the gap that triggered S-0046)

S-0044 shipped the foundation with this assumption in the routine UI configuration table: *"Ask permissions: Default — Use `.claude/settings.local.json` allowlist for routine's needs."* That sentence shipped a load-bearing assumption — "we'll lean on the allowlist" — without authoring the allowlist. The first manual routine fire after S-0045 master plan deadlocked at the very first Bash invocation: `python3 engine/tools/check_target.py` (boot step 3, target-met check). S-0046 patched the gap.

### The rule

**Adding a new Bash invocation to the routine procedure REQUIRES adding a paired allowlist entry in the same commit.**

This applies to:
- Edits to [`.claude/skills/routine-mode-lifecycle/SKILL.md`](../../.claude/skills/routine-mode-lifecycle/SKILL.md) — the executable Skill body.
- Edits to [`.claude/commands/start-routine.md`](../../.claude/commands/start-routine.md) — the slash command body.
- Edits to this ops doc that introduce new tooling references.
- New criterion types in [`engine/tools/check_target.py`](../tools/check_target.py) that shell out (the `predicate` escape hatch can call subprocess; if it does, the command needs allowlist coverage).
- Per-task scope_lock work that requires invocations the engine apparatus doesn't already cover (e.g., a Phase 5 sub-task that runs a one-off `npm` command would need `Bash(npm:*)` added; the master plan session is the right place to identify these).

### Pre-allowlisted Bash command surface (post-S-0046)

The complete pre-approved set covers:

- **Engine python tools** — every `engine/tools/*.py` script runnable via `python3` with any args. Includes the routine-procedure tools (`check_target`, `check_routine_scope`, `scan_context_telemetry`, `audit_handoff_dispositions`) plus the broader engine tooling (`validate`, `scan_issue_*`, `scan_orphans`, `health_check`, `probe_*`, `parse_structural_reference`).
- **Worktree-side git lifecycle** — `git add/commit/rm/mv/status/diff/log/rev-parse/fetch/show/ls-files/pull --ff-only origin main`. Pairs with the existing main-repo lifecycle entries (`git -C <main> merge --ff-only`, `git -C <main> push origin main`).
- **Test/lint stack** — `pytest`, `ruff`, `mypy`, both as direct invocation and via `python3 -m`.
- **GitHub Issues path** — `gh issue create/list/view/close/comment` plus `gh label list`. Routine sessions file Issues for in-band discoveries per ADR 0048.
- **Supabase migration tooling** — `supabase db push/migration new/migration list/migration repair`. Used by Phase 5 task execution (per `auto_target.json` scope_lock workflows).
- **Hook scripts** — `bash engine/tools/hooks/*.sh` for manual invocation during debugging.
- **Shell utilities** — `date` (ISO timestamps in eager-claim), `ls`, `cat` (engine session files), `head`, `tail`, `wc`, `grep`, `rg`, `find . -name`.
- **MemPalace CLI** — `mempalace search/status/list-drawers/add-drawer/diary read/diary write`.
- **`source engine/tools/scrub_env.sh`** — for shell-side venv PATH wiring.

### Verification path

After extending the allowlist, manually fire the routine and walk the boot procedure:

1. Boot detects routine-mode (target file present).
2. Pause check runs (no Bash call — file read).
3. Target-met check invokes `python3 engine/tools/check_target.py` — should not prompt.
4. Max-sessions check (no Bash call — directory list via Glob tool).
5. Eligibility selection (no Bash call — file read).
6. Plan authoring (no Bash call — Write tool).
7. Boot-time scope-check invokes `python3 engine/tools/check_routine_scope.py --plan ...` — should not prompt.
8. If eligible, eager-claim runs `git add`, `git commit`, `git -C <main> merge --ff-only`, `git -C <main> push origin main` — none should prompt.
9. Per-task work runs whatever the task's scope_lock demands.
10. Shutdown runs `python3 engine/tools/scan_context_telemetry.py`, `python3 engine/tools/audit_handoff_dispositions.py`, `git rm/mv`, `git commit`, push — none should prompt.

A routine session that fires and exits cleanly without any prompt-and-deny event is the working signal.

### What to do when a routine deadlocks on a permission prompt

1. **Deny the prompt.** Don't "Always allow" piecemeal — that adds only the one pattern that fired, and the next un-allowlisted command will deadlock the next fire.
2. **Identify the missing pattern** from the prompt's command preview.
3. **Open an interactive session** (`/start-engine`) and extend `.claude/settings.json` with the missing entry plus any obvious siblings.
4. **Commit + push** so the allowlist propagates to the worktree the routine fires in.
5. **Re-fire the routine manually** to verify.

If the missing command is *task-specific* (one Phase 5 sub-task needs a tool nothing else uses), the right fix may be either the global allowlist (if the tool is genuinely safe) or — preferably — adjusting the task's `scope_lock.allowed_paths` and the `predicate` callable to use already-allowlisted tooling. Avoid pattern proliferation.

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
