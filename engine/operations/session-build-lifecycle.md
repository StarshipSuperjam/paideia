# Session build lifecycle

> How a build session boots, runs, and commits. The shutdown sequence (close work) lives in [`session-shutdown-sequence.md`](session-shutdown-sequence.md).

## When this applies

A build session is any conversation that types `Start Engine` or invokes `/start-engine`. Default-mode (exploration) conversations do not run this lifecycle — they make no commits and claim no slot.

## Boot procedure (run in order)

1. **Read `STATE.md`.** Get current phase, last build session, next-session work item, GitHub URL, Supabase project ref, infrastructure pointers.

2. **Health-check cadence trigger.** Read `session/register_state.json`. Parse the trailing 4-digit counter from `last_claimed`. If `counter % health_check_cadence == 0` (default cadence: 30), propose:

   > "Last claimed was S-NNNN. Cadence trigger fires for a project health check (see `docs/operations/health-check.md`). Run the audit now or defer?"

   User accepts → the session's work becomes the audit. User defers → proceed with planned work; flag re-fires next session.

3. **Query MemPalace.** Use `mempalace_search` with terms derived from STATE.md's next-session work item. Surface anything the user previously named that's relevant. Skip if MemPalace is not yet initialized (early sessions before S-0002 close).

4. **Read referenced docs.** STATE.md and ROADMAP.md will name specific files relevant to the work. Read them before claiming the slot — the slot claim should be informed.

5. **Read the build-readiness report** (substantive build sessions only, per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)). STATE.md's "Next session work item" names the report at `engine/build_readiness/<phase>_<chunk>.md` for substantive build sessions. Read the report end-to-end:

   - **Pre-session decisions section** — Tier 1 resolutions inherited from the gate session. The build session implements against these, not around them.
   - **Tier 2 decisions section** — concrete column shapes, constraint forms, default values. Implement exactly as documented; the gate session settled these in advance precisely so the build session does not re-decide under build pressure.
   - **Tier 3 forward pointers** — decisions explicitly deferred. Honor the deferral; do not pre-empt by inventing answers.
   - **Success criteria** — the build session verifies these at shutdown.

   If the report is **absent** for a session work item that requires one (substantive build phase), the session converts to a gate session: do not author the planned artifacts; instead run the gate procedure per [`build-readiness-gate.md`](build-readiness-gate.md) and produce the report. The next session opens as the build session.

   If the report is **present but contains unresolved Tier 1 items**, the session halts and escalates to the user — the gate session did not finish its job. Do not attempt to resolve Tier 1 in-flight; the build session's mode is auto-by-default for routine judgment, not for foundational decisions.

   Operational sessions (health checks, ENGINE_LOG-only edits, retrievability cleanups, gate sessions themselves) skip this step — they do not require build-readiness reports per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s scope.

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
     "outcome_summary": null,
     "approved_plan": "<path or null>",
     "branch": "<current git branch>",
     "worktree": "<absolute path>"
   }
   ```

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
