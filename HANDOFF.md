# Handoff Log

> Running log of items deferred to a future major-state-transition session. Not a contract; a convenience so transition sessions don't re-solve already-solved problems. Add entries when you encounter something a future session needs to know but that doesn't belong in ENGINE_LOG, an ADR, or `docs/tensions.md`.

---

## MemPalace capture mechanism (set in S-0001 for S-0002)

**Discovered:** MemPalace 3.3.3 does NOT auto-capture conversations on its own. Auto-capture requires Claude Code hooks wired in `.claude/settings.json`.

Two hook types must be configured:

- **Stop hook** — fires after every 15 human messages. Blocks the AI with a save instruction. Tracks save points per session in `~/.mempalace/hook_state/`. Honors `stop_hook_active` to prevent infinite loops.
- **PreCompact hook** — fires before context compaction. Always blocks with a comprehensive save instruction (compaction means the AI is about to lose detailed context).

Both hooks are invoked the same way:
```
echo '{"session_id":"abc","stop_hook_active":false,"transcript_path":"..."}' | mempalace hook run --hook stop --harness claude-code
```

**S-0002 must:**

1. Add `.claude/settings.json` with stop and precompact hook entries pointing at `mempalace hook run --hook <stop|precompact> --harness claude-code`.
2. Update `.gitignore` to except `.claude/settings.json` so the hooks ship with the repo (currently only `.claude/commands/` is excepted; settings.json would be ignored). The precise pattern: change `.claude/*` rules to additionally include `!.claude/settings.json`.
3. Document the hook wiring in `docs/operations/mempalace-operations.md` so future setup-on-fresh-clone sessions can replicate it.
4. Test that the stop hook fires after 15 messages by running a build session and verifying drawers are written to MemPalace at the expected cadence.

**MemPalace MCP server is already configured** in `.mcp.json` (parent repo, gitignored). The 19 MCP tools — including `mempalace_search`, `mempalace_add_drawer`, `mempalace_kg_*`, `mempalace_diary_*` — become available next time Claude Code restarts.

**MemPalace architecture (4-level hierarchy, not 3 as initially read):**
- Wings (projects/people)
- Rooms (topics)
- Closets (summaries)
- Drawers (verbatim memories)

Halls connect rooms within a wing. Tunnels connect rooms across wings.

**Auto-detection:** `mempalace init <dir>` detects rooms from folder structure. Run AFTER S-0001's `docs/` reorganization so rooms map to subdirectories (e.g., `docs/operations/` → operations room). S-0002 plan: `mempalace init docs/` then `mempalace mine docs/`.

---

## Pre-commit hook STATUS-capture bug + side-discovery audit mechanism (set at S-0032 close for S-0033)

**Two coupled items.** The first is a specific bug. The second is the structural fix that would have prevented this entry from being authored at session-end as a postscript (which the user called out as itself being the problematic pattern).

### Item 1: Pre-commit hook silently allows hard-fails through

**Symptom observed at S-0032 across multiple commits:** `engine/tools/hooks/pre-commit` ran the secondary code-gates and sql-gates blocks (lines 109-144), they reported hard-fails (`ruff format check failed`, `mypy --strict failed`) to stderr, but the commit completed anyway with `[pre-commit] Mode: build — OK`.

**Diagnosis:** The `if ! cmd; then STATUS=$?; ...` pattern at lines 94-101, 112-122, and 134-144 captures `$?` after the negated pipeline. When a `! cmd` pipeline runs and `cmd` exits non-zero, the pipeline's exit status (and therefore `$?`) becomes 0 (success of the negation). So `STATUS=$?` always gets 0 inside the then-branch, and `[ "$STATUS" -ge 2 ]` always evaluates false, so the block falls through to `exit 0`.

**Fix:** Replace each `if ! cmd; then STATUS=$?; ...` block with one of these patterns:
- `cmd; STATUS=$?` (simpler — but requires `set +e` / `set -e` toggle around it because `set -e` is on at line 26).
- `cmd || STATUS=$?` (preserves `set -e` semantics — `STATUS` only gets the exit code when `cmd` fails).

After choosing, follow with the existing `if [ "$STATUS" -ge 2 ]; then ... exit 1; fi` block.

**Verification:** Write a Python file with a deliberate syntax error, stage it, attempt commit. Expected: blocked with exit 1 and a clear error message. Without the fix: commit completes despite the hard-fail.

**Why it matters:** A commit gate that silently lets hard-fails through undermines confidence in every gate-checked commit downstream. Fix lands BEFORE the next substantive build session (Phase 4 build-readiness gate) so the gate exercise's own commits are cleanly gated.

### Item 2: Side-discovery audit at shutdown (the structural fix)

**Pattern this addresses:** The AI repeatedly notices out-of-scope issues during a session, mentions them in commit messages or end-of-session prose ("flagged for follow-up"), and they vanish without a mechanical surface that triggers future action. S-0032 demonstrated this twice — the pre-commit bug above was flagged in commit cbff859 and again in the close commit, both times with no scheduled-audit entry. The user called the pattern out at session end. This handoff entry exists because the AI was at 60% context and could not start S-0033 to capture mechanically; the next-best surface was HANDOFF.md.

**Proposed mechanism for S-0033:**

1. New script `engine/tools/audit_side_discoveries.py`. Scans this session's commit messages (between the eager-claim commit and HEAD~ at shutdown time) for follow-up markers: `flagged`, `follow-up`, `TODO`, `FIXME`, `deferred`, `noted for`, `future session`, `next session`, `pending`, `out of scope`. For each match, prints the marker with surrounding context and the commit SHA.

2. The script's exit code: 0 if no markers found OR all markers have a confirmed disposition; 2 (hard-fail) if any unconfirmed marker remains. Disposition confirmation: AI provides a structured input (file, JSON, CLI flag) saying "marker X in commit Y is dispositioned by Z," where Z is one of: a `scheduled_audits.json` entry id, a `tensions.md` OQ-id, a `HANDOFF.md` section heading, an "addressed inline" reference to a fix-commit SHA, or "acceptable, no action required" with reasoning.

3. Wire into `engine/operations/session-shutdown-sequence.md` as a new step before outcome_summary fill (so dispositions feed into outcome_summary, and so a missing capture blocks the close — same mechanical shape as the existing `outcome_summary_soft_warns` discipline). Mirror in the `session-shutdown-sequence` Skill body.

4. Add tests: a session with no follow-up markers passes; a session with markers but all dispositioned passes; a session with markers and any undispositioned fails.

**Note on the "had to load a session to schedule a session" barrier:** The current pre-commit hook treats post-close (no current.json, register status closed) as exploration mode and only allows commits to `.claude/plans/`, `HANDOFF.md`, `product/docs/tensions.md`, `product/docs/ideation.md`. `engine/scheduled_audits.json` is the engine-side surface for one-time future-session triggers but is NOT in the allowed list — so adding an entry between sessions requires opening a new session. That's a self-inflicted barrier. S-0033 should either (a) add `engine/scheduled_audits.json` to the exploration-mode allowed-paths list, or (b) decide that the barrier is intentional (e.g., scheduling is itself substantive engine work) and document the rationale. The user's framing at S-0032 close was "ridiculous" — the (a) path is recommended.

### S-0033 scope

- Pre-commit hook fix (Item 1).
- Side-discovery audit script + ops-doc step + Skill mirror + tests (Item 2).
- Add `engine/scheduled_audits.json` (and any other engine-side scheduling/handoff surfaces) to the pre-commit hook's exploration-mode allowed-paths list with rationale comment.
- Phase 4 build-readiness gate exercise (the originally-planned S-0032 work, deferred at S-0032, deferred again at S-0033 by the user direction at S-0032 close) → moves to S-0034.

**Resolved: 2026-05-02 (S-0033).** All three items landed (commits `2609aaf` and `ca36c17` plus the close commit). Phase 4 build-readiness gate moves to S-0034 as scheduled.

---

## Worktree git operations broke mid-session — `core.bare = true` inheritance from parent (set at S-0033 for next session if it recurs)

**Symptom:** Mid-S-0033, `git status` and `git rev-parse --show-toplevel` from the worktree at `.claude/worktrees/unruffled-ride-236a8d/` started failing with `fatal: this operation must be run in a work tree`. Earlier in the same session, the same commands had worked. `git log` and `git rev-parse HEAD` continued to work; only operations that need a working tree failed.

**Diagnosis:** The parent repo's `.git/config` carries `[core] bare = true`. With `extensions.worktreeConfig = true`, per-worktree config can override the parent's `[core]` section, but the worktree's `.git/worktrees/<name>/config.worktree` did not include `bare = false`. Some operation during S-0033 caused git to start honoring `bare = true` for worktree commands; setting `core.bare = false` in the worktree config resolved it inline.

**Open questions for the next session if it recurs:**

1. **What changed mid-session?** The same git commands worked at the eager-claim and at the Item-1 commit, then stopped working a few commits later. The parent's `.git/config` mtime (20:09 in the session) is suspicious — something modified it. Identify what (a hook, a `git config` invocation, an external tool).
2. **Are other worktrees at risk?** Other worktrees under `.claude/worktrees/` have the same `config.worktree` shape (no `bare = false` override). If the trigger fires on those too, every worktree should grow the override. If only this worktree was affected, the trigger is scoped narrower.
3. **Permanent fix vs symptom fix.** Setting `core.bare = false` in this worktree's `config.worktree` works but is a band-aid. The underlying question is why a bare parent's config bleeds into worktree behavior despite `extensions.worktreeConfig = true`. Investigate or document the limit.

The S-0033 close commit was pushed via `git push . src:main` from the parent (the bare-repo path), since `git -C parent merge --ff-only` no longer works on the bare parent.

---
