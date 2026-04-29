# `tools/sweep_worktrees.sh`

> Cleanup utility for stale Claude Code worktrees. Run on demand, not automatically.

## What it does

Claude Code creates per-session worktrees under `.claude/worktrees/<name>/`. After a session closes, the worktree directory remains on disk and the corresponding entry remains in `git worktree list`. Over time these accumulate.

`sweep_worktrees.sh` removes worktrees that meet *all* of:

- The worktree branch has no commits ahead of `main`.
- The working tree is clean (no untracked files, no uncommitted changes).
- The session associated with the worktree (per `session/archive/`) is `closed` or `closed_partial`.

## When to run

- After closing a session, manually, if the session's worktree is no longer needed.
- Periodically as housekeeping (the health-check audit checks for stale worktrees and may suggest a sweep — see [`health-check.md`](health-check.md)).
- Before a foundation-changing operation (e.g., a major branch reorganization) where lingering worktrees would interfere.

## When NOT to run

- During an in-progress session (it would attempt to evaluate the active worktree).
- If you have uncommitted exploratory work in any worktree that you haven't decided whether to keep.
- Without first confirming `git worktree list` shows what you expect.

## Usage

From the repo root:

```bash
./tools/sweep_worktrees.sh             # interactive — prompts before each removal
./tools/sweep_worktrees.sh --dry-run   # print what would be removed without removing
```

The script never force-removes. If a worktree fails the safety checks (uncommitted changes, ahead of main, session still open), it's listed as skipped with the reason and left alone.

## Aborting

Ctrl-C at any prompt cancels. Any worktrees already removed before the abort stay removed (that's how `git worktree remove` works).

## Manual cleanup

If a worktree is unrecoverably broken (filesystem corruption, missing `.git` link), use `git worktree remove --force <path>` to detach it, then `rm -rf <path>` if needed. Don't routinely use `--force`; it bypasses the safety checks the sweep script enforces.

## See also

- [`health-check.md`](health-check.md) — periodic audit; worktree count and staleness are tracked metrics.
- `tools/sweep_worktrees.sh` — implementation.
