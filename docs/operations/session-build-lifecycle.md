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

5. **Claim the slot via the eager-claim ritual** (see below).

6. **Begin substantive work.** The slot is held atomically; concurrent sessions cannot collide. Make file edits, run tools, commit incrementally as work progresses. Each commit must pass `tools/validate.py` (enforced by the pre-commit hook in `tools/hooks/pre-commit`).

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

6. **Confirm with the user before pushing the first time per session** — pushing is shared-state. Subsequent pushes within the same session don't need re-confirmation.

   ```bash
   git -C <parent-repo-path> push origin main
   ```

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

- First push of session: confirm with user.
- Subsequent pushes within the same session: no re-confirmation needed unless the change is destructive (force-push, amends to public commits, branch deletion).
- Always FF main locally before pushing. Never push the worktree branch directly to remote main without going through the parent repo's main.

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — close-of-session protocol.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — what to do with hard-fails and soft-warns.
- [`escalation-criteria.md`](escalation-criteria.md) — when to interrupt the user mid-session.
- `.claude/commands/start-engine.md` — the slash command implementation.
