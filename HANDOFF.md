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

## Stale-checkout vs halted-shutdown — Recovery section needs a sanity check (logged post-S-0033 close, exploration mode)

**Pattern observed at the S-0033 → S-0034 boundary.** A fresh `/start-engine` session opened immediately after S-0033 closed read the state files in its own worktree and concluded that S-0033 had halted mid-shutdown — `register_state.json` still showed `current_status: in_progress`, `current.json` still existed with `status: in_progress`, `STATE.md` still pointed at S-0033 as the next-session work item. The session's narrative began invoking the Recovery procedure (recovery scenario #1: "Halted before step 8 (archive)") and was about to redo the shutdown.

But S-0033 had closed cleanly. The close commit (`dc3e370`) was already on origin/main: archive landed, register flipped to `closed`, STATE.md updated, ENGINE_LOG entries added, HANDOFF marked Resolved. The next session's worktree just didn't have that commit checked out yet — its branch was created from main at a pre-close state, so its working-tree files showed the post-eager-claim configuration. `git log` could see `dc3e370` (the parent has it) but the worktree's checked-out files reflected an earlier commit.

**Why this is dangerous.** Running the recovery procedure on a stale checkout would have re-archived an already-archived `current.json` (path conflict with `archive/S-0033.json`), re-edited `STATE.md` (overwriting the S-0033 close narrative with a fresh "S-0033 closed today" entry on top of one already there), re-flipped register fields, and appended duplicate ENGINE_LOG entries. The session would have looked productive — commits land, validator passes — while creating real corruption from a phantom problem.

**Proposed fix for next substantive session that touches the shutdown procedure.** Add a sanity check to the Recovery section of [`engine/operations/session-shutdown-sequence.md`](engine/operations/session-shutdown-sequence.md) and the [`session-shutdown-sequence` Skill](.claude/skills/session-shutdown-sequence/SKILL.md) mirror, before any of the four recovery scenarios trigger:

> **Before invoking any recovery scenario, verify the prior close did not already land.** Run `git fetch origin && git log --oneline origin/main -10`. If a `chore(session): close S-NNNN` commit for the slot named in `register_state.json`'s `last_claimed` field is visible upstream, the prior session closed cleanly and the local checkout is stale, not halted. Update the local checkout to that commit (`git pull --ff-only` if the branch tracks origin/main, or `git reset --hard origin/main` on a throwaway branch) and proceed with the *next* session's work; do not run recovery.

The asymmetry that justifies this: a halted shutdown leaves no upstream close commit (the halt prevented the push); a stale checkout always has the upstream close commit. One `git log` check distinguishes them.

**Concrete trigger condition for the new ops-doc entry**: `register_state.json`'s `current_status: in_progress` AND `current.json` exists locally AND `git log origin/main` shows a `close S-<that-slot>` commit. That's the stale-checkout shape. The genuine halt shape is the same minus the third clause.

**Out of scope for this entry**: any heuristic for detecting which commit-message conventions count as "close" (the literal string `chore(session): close S-NNNN` is the project convention; sufficient for the check).

This is the kind of finding that would have been mechanically caught if the side-discovery audit ran across cross-session boundaries — but the audit's scope is "this session's commits," not "the boundary between two sessions." That boundary is exactly where this confusion lives.

---

## Bash 3.2 incompatibility in `session-start.sh` persistent-warn loop (logged at S-0035, not introduced by this session)

**Surfaced during S-0035** while end-to-end testing `engine/tools/hooks/session-start.sh` after the new shared-state probe step landed. Running the hook produced this stderr:

```
engine/tools/hooks/session-start.sh: line 250: declare: -A: invalid option
declare: usage: declare [-afFirtx] [-p] [name[=value] ...]
```

**Root cause.** Lines around the persistent-warn surface use `declare -A CATEGORY_FIRINGS` (associative array) and `${!CATEGORY_FIRINGS[@]}` (associative-array key iteration). Both are bash 4+ features. macOS ships `/bin/bash` 3.2 (Apple's GPLv3 hold). The script's shebang is `#!/bin/bash`, so it picks up the system bash even when bash 4+ is installed via Homebrew at `/usr/local/bin/bash` or `/opt/homebrew/bin/bash`.

**Impact.** On bash 3.2: `declare -A` errors, `CATEGORY_FIRINGS[$cat]=…` writes to a regular indexed array, `${!CATEGORY_FIRINGS[@]}` returns indexed-array indices (numeric, not category names), so the inner `for cat in …` loop never iterates with a real category name. The persistent-warn surface silently emits "none above the 3-of-5 threshold" regardless of actual archive contents. Today this is invisible because S-0030–S-0034 archives all have zero-count soft-warns; if a real persistent warn ever fires, the surface would suppress it on bash 3.2 systems.

**Not introduced by S-0035.** The associative-array idioms predate this session — the hook was authored at S-0031 per ADR 0043 and tightened at S-0032 with the scheduled-audit surface. S-0035's only change to the file was sourcing `scrub_env.sh` and adding a probe block before the persistent-warn surface; the buggy lines are downstream and untouched.

**Proposed fix for the next session that touches `session-start.sh`** (or a future health-check session): convert the persistent-warn aggregation to use parallel indexed arrays (a list of category names + a list of counts at the same index) instead of an associative array. Bash 3.2-portable. Or: switch the shebang to `#!/usr/bin/env bash` AND require a minimum bash version via documentation, recognizing that this changes the run-environment contract. The first option is preferable — it stays compatible with the system shell.

**Verification after fix.** Run `bash --version` to confirm 3.2 (or older); run `bash engine/tools/hooks/session-start.sh` against an archive set carrying a soft-warn that should fire 3-of-5; confirm the persistent-warn surface emits the category, not "none above threshold."

---

---
