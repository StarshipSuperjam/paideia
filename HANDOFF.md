# Handoff Log

> Running log of items deferred to a future major-state-transition session. Not a contract; a convenience so transition sessions don't re-solve already-solved problems. Add entries when you encounter something a future session needs to know but that doesn't belong in ENGINE_LOG, an ADR, or `docs/tensions.md`.
>
> **Disposition discipline (added at S-0036, retroactively applied to live entries at S-0041).** Every section carries a `**Disposition:**` line in one of four forms: `fixed-in-session @ <SHA>`, `deferred-with-user-confirmation`, `out-of-scope`, `not-actionable`. Or, for resolved entries, a `**Resolved:**` line naming the session and downstream artifact (ADR, ENGINE_LOG entry, ops-doc edit). The `engine/tools/audit_handoff_dispositions.py` script audits new sections at session shutdown.

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

**Resolved: 2026-04-29 (S-0002).** All four S-0002-must items landed: (1) `.claude/settings.json` Stop + PreCompact hooks wired and committed; (2) `.gitignore` updated to except `.claude/settings.json`; (3) hook wiring documented in `engine/operations/mempalace-operations.md`; (4) hook fires verified at S-0002 close. The hook-wrapper PATH-fix that this S-0001 framing did not anticipate was landed at S-0032 (per ENGINE_LOG S-0032 Changed entry — the wrapper had been silently failing since S-0002 due to PATH narrowing in Claude Code subshells; S-0032 added the user-scope fallback). Disposition retroactively applied at S-0041 per the audit cleanup pass.

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

**Resolved: 2026-05-03 (S-0035) per [ADR 0045](engine/adr/0045-shared-state-integrity-discipline.md).** The S-0035 engine-hardening pass identified the root cause as subprocess-env-leak: a `GIT_*` environment variable inherited from a parent context was getting written into `.git/config` by a subsequent `git config` invocation. ADR 0045 mechanizes four protections that close this vector: (1) `engine/tools/scrub_env.sh` + `engine/tools/scrub_env.py` strip `GIT_*` from every subprocess invocation across all four hook scripts and `validate.py`'s code-gate subprocess calls; (2) `engine/tools/probe_repo.py` checks both worktree-effective and parent-clone-direct `core.bare` at boot, hard-failing on `core.bare=true` with the exact `git -C <repo> config --unset core.bare` recovery command in the stderr surface; (3) the boot-time `validate.py --health-probe-only` invoked from `session-start.sh` runs `probe_repo.py` so any recurrence surfaces at the next session boot; (4) test fixtures verify the hard-fail path. The 3 open questions in the original entry are answered by ADR 0045's analysis: (Q1) the trigger was env-leak, not a hook or external tool; (Q2) every worktree was structurally at risk; the env-scrub eliminates the leak universally; (Q3) the "permanent fix vs symptom fix" question resolved as: the env-scrub is permanent at the source-of-leak; the worktree-config override was a symptom fix and is no longer needed. Disposition retroactively applied at S-0041 per the audit cleanup pass.

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

**Resolved: 2026-05-03 (S-0041).** The proposed pre-recovery sanity check landed in [`engine/operations/session-shutdown-sequence.md`](engine/operations/session-shutdown-sequence.md) Recovery section and the [`session-shutdown-sequence` Skill](.claude/skills/session-shutdown-sequence/SKILL.md) mirror — both gain a "Pre-recovery sanity check" subsection before the four recovery scenarios. The verification command, the asymmetry rationale, and the concrete trigger condition all match the proposal verbatim. Disposition applied during the S-0041 catch-up audit cleanup pass.

---

## Phase 5 routine-mode blocked: SUPABASE_DB_URL not in worktree env (set at would-be-S-0049 boot)

**Discovered.** Routine fire intended to claim S-0049 for P5-01a (Epistemology core seed) detected at the boot procedure that `SUPABASE_DB_URL` is not in the process env. Investigation:

- `.env` exists in the main repo with the URL populated.
- `.env` does NOT exist in this worktree (`.claude/worktrees/stoic-antonelli-c9ca56/`). It is gitignored, so worktree creation does not propagate it. The session-start hook's onboarding pointer (Issue #7) checks `$REPO_ROOT/.env` where `$REPO_ROOT = git rev-parse --show-toplevel`, which in a worktree resolves to the worktree path, not the main repo.
- Neither [`engine/tools/check_target.py:103`](engine/tools/check_target.py) nor [`engine/tools/validate.py:2325`](engine/tools/validate.py) calls `load_dotenv()` — they read `os.environ.get("SUPABASE_DB_URL")` directly. Even if `.env` were copied into the worktree, the tools would not see the value unless the parent shell sourced it before launching the routine.

Net effect: every Phase 5 routine fire fails the `migration_applied` criterion for all 16 tasks (`SUPABASE_DB_URL not set; cannot verify`). The S-0048 setup-helper closed the dashboard-only-password discoverability gap for interactive use but did not wire the env-loading path that routine sessions need.

**Action taken at would-be-S-0049 boot.** Filed [Issue #8](https://github.com/StarshipSuperjam/paideia/issues/8) (`bug`, `priority:urgent`) with three remediation options (preferred: tools auto-load `.env` via a walk-up helper). Did not claim a slot. Did not author a plan. Did not modify `auto_target.json`. Routine exited 0 after this HANDOFF entry committed and pushed.

**What the next session should do.**

1. **Pause routine first.** Toggle the `paideia-engine-loop` Claude Code Routine to Manual immediately. Otherwise the next hourly fire wakes up, walks the same boot procedure, finds the same blocker, and either (a) re-files a duplicate Issue or (b) — worse — proceeds far enough to claim a slot before failing the criterion check, churning the slot register for nothing. Toggle is at the Routine UI; out-of-tree.
2. **Adjudicate Issue #8.** Pick Option A / B / C. Option A (tools auto-load via walk-up) is preferred and the smallest defensible fix.
3. **Land the fix in an interactive `/start-engine` session** (touches `engine/tools/`, out of every Phase 5 task's `scope_lock`). Verify by running `python3 engine/tools/check_target.py` from a fresh worktree — `migration_applied` should change from `SUPABASE_DB_URL not set; cannot verify` to either `migration X not in schema_migrations` (DB reachable, migration unapplied — expected pre-Phase-5) or pass.
4. **Resume the routine** by flipping back to Hourly.

**Disposition:** tracked-as-issue #8

**Resolved: 2026-05-04 (S-0049, commit 21285f8).** Issue #8 fixed via Option A (walk-up `.env` loader). New [`engine/tools/load_env.py`](engine/tools/load_env.py) provides `find_dotenv` / `load_dotenv` / `load_dotenv_walk_up` (reusing `parse_env` from `engine/tools/setup_env.py`); wired into [`engine/tools/check_target.py`](engine/tools/check_target.py) `main()` and [`engine/tools/validate.py`](engine/tools/validate.py) `main()` before argparse. 14 new tests cover walk-up traversal, override semantics, idempotency, and the worktree-shaped tree case. Verified end-to-end from this worktree (no local `.env`, `SUPABASE_DB_URL` unset in shell): `check_target.py --task-id P5-01a` correctly queries the DB and reports `migration_applied` FAIL with "migration 0011_seed_epistemology_part1 not in schema_migrations" (URL loaded; DB queried; migration is genuinely not yet applied — Phase 5 hasn't started). `validate.py` runs 30 checks (was 23) — graph audit engaged. validate.py psycopg ImportError flipped from hard-fail to soft-skip (records `graph_audit_skipped` + stderr note), which is the right disposition now that the walk-up auto-loads `SUPABASE_DB_URL` in any reachable-`.env` context including pre-commit's system-Python invocation (no psycopg there). User can now toggle `paideia-engine-loop` back to Hourly.

---

## P5-01a Epistemology core — work landed; verifier bug blocks criterion-pass bookkeeping (set at S-0050)

**Discovered.** S-0050 is the first routine-mode session against `T-PHASE-5` and the first task to exercise the `migration_applied` criterion. The work product landed cleanly:

- `product/seed-graph/migrations/0011_seed_epistemology_part1.sql` authored with 28 nodes + 34 edges (the analysis-of-knowledge tradition core); `graph_version` 1 → 2; ROUTING.md per-session narrative entry appended. Committed at `d8c4056` (`feat(seed): seed epistemology part 1 — 28 nodes, 34 edges`), pushed to main.
- Migration applied via Supabase MCP `apply_migration`; `supabase_migrations.schema_migrations` records `version=20260504192422`, `name=0011_seed_epistemology_part1`.
- `python3 engine/tools/validate.py` (with venv Python so `psycopg` is available and the live graph audit engages) reports 30 checks, 0 hard-fails, 27 soft-warns (25 `missing_rigor_score` expected for partial seed per phase_5.md T2-C; 2 `issue_collision` carryover from upstream MemPalace #1 / #2).

**Then the verifier missed it.** `python3 engine/tools/check_target.py --task-id P5-01a` reports `[FAIL] migration_applied — migration 0011_seed_epistemology_part1 not in schema_migrations`. Root cause: [`engine/tools/check_target.py:114`](engine/tools/check_target.py) queries `WHERE version = %s` against `supabase_migrations.schema_migrations`, but `version` is the timestamp (`20260504192422`); the auto_target.json `id` field is the migration name (`0011_seed_epistemology_part1`). The schema doc at [`engine/session/auto_target.schema.md`](engine/session/auto_target.schema.md) explicitly shows the `id` field as the descriptive migration name, so this is a one-line column swap (`version` → `name`). S-0049's e2e verification ran the predicate before any Phase 5 migration existed, so the false-FAIL response looked correct (URL loaded, DB queried, migration genuinely absent); the bug only surfaces post-apply.

**Action taken at S-0050 close.** Filed [Issue #9](https://github.com/StarshipSuperjam/paideia/issues/9) (`bug`, `priority:urgent`) with the diagnosis, reproduction, fix, and blast-radius analysis. Marked P5-01a `blocked: scope-expansion-needed: check_target_migration_applied_uses_version_column` in [`engine/session/auto_target.json`](engine/session/auto_target.json) (status field only — operational allowlist). Did NOT attempt to fix `engine/tools/check_target.py` inline because the file is outside P5-01a's `scope_lock.allowed_paths` and routine-mode posture treats scope_lock as invariant — the pre-commit hook would hard-fail any out-of-scope commit.

**Routine-mode protection.** The next routine fire walks the boot procedure, finds P5-01a `blocked` (not `complete`), and `_select_task` will not pick any sibling task because every other Phase 5 subject task (P5-02a, P5-03, P5-04a, P5-05, P5-06, P5-07a, P5-08, P5-09, P5-10) has `P5-01a` in its `depends_on` list — and the eligibility check requires every `depends_on` entry to have `status == complete`. So no sibling task is eligible until P5-01a flips to `complete`. The routine will exit via the "no eligible task" path: HANDOFF written, no slot churn, no work attempted. Pausing the routine is still cleaner (avoid HANDOFF spam from repeated fires); recommend toggling `paideia-engine-loop` to Manual until the fix lands.

**What the next interactive `/start-engine` session should do.**

1. Land the one-line column-swap fix in [`engine/tools/check_target.py:114`](engine/tools/check_target.py): change `WHERE version = %s` to `WHERE name = %s`.
2. Add a regression test in `engine/tools/test_check_target.py` (create the file if missing) that mocks `psycopg.connect` and asserts the SQL uses the `name` column with the descriptive id.
3. Run `python3 engine/tools/check_target.py --task-id P5-01a` and confirm both criteria PASS.
4. Mark P5-01a `complete` in [`engine/session/auto_target.json`](engine/session/auto_target.json) (status field only — operational allowlist; remove the `blocked_reason` field at the same time). Close [Issue #9](https://github.com/StarshipSuperjam/paideia/issues/9) with a reference to the fix commit.
5. Resume the routine by toggling the `paideia-engine-loop` Routine back to Hourly.

After this fix lands, P5-01b (Epistemology specialized; depends only on P5-01a) becomes eligible and the routine resumes Phase 5 dispatch.

**Disposition:** tracked-as-issue #9

**Resolved: 2026-05-04 (S-0051).** One-line column swap landed at `engine/tools/check_target.py:114` (`version` → `name`); regression test `test_migration_applied_queries_name_column` added asserting SQL uses the `name` column with the descriptive id. Live verification: `check_target.py --task-id P5-01a` reports both criteria PASS. P5-01a flipped to `complete` in `auto_target.json` (status field only); `blocked_reason` cleared. [Issue #9](https://github.com/StarshipSuperjam/paideia/issues/9) closed. The routine resumes — P5-01b through P5-10 become eligible.

---

## S-0061 close commit landed locally but not pushed — routine_lifecycle_push.py close-mode allowlist missing `engine/session/current_plan.md`

**Discovered:** S-0061 (2026-05-05). The routine session for P5-05 Political philosophy completed all substantive work cleanly: eager-claim and deliverable both pushed via the wrapper; P5-05 verified PASS on both criteria; STATE.md, ENGINE_LOG.md, archive S-0061.json all authored; close commit `cd33979` landed locally with subject `chore(session): close S-0061 — Phase 5 political-philosophy seed; P5-05 complete`. The pre-commit hook chain (validate.py + audit_handoff_dispositions.py + audit_archive_structured_fields.py) all passed clean.

The close push via `python3 engine/tools/routine_lifecycle_push.py close` REFUSED with exit 0 + the message:

```
[routine-lifecycle-push] REFUSED (close): close diff touches paths outside the operational allowlist (['HANDOFF.md', 'engine/ENGINE_LOG.md', 'engine/STATE.md', 'engine/session/auto_target.json', 'engine/session/current.json', 'engine/session/register_state.json']): ['engine/session/current_plan.md']
```

The wrapper's hardcoded close-mode allowlist appears to be missing `engine/session/current_plan.md` AND `engine/session/archive/S-*.json` — the close commit deletes `current_plan.md` (the boot-time plan artifact created by step 6 of the routine-mode-lifecycle skill) and creates `archive/S-0061.json` (the close-time archive artifact). The S-*.json appears to be tolerated by some glob path the message doesn't list, but `current_plan.md` is not.

The discrepancy is between:

- The wrapper's hardcoded close-mode allowlist (per the REFUSED message): `HANDOFF.md, ENGINE_LOG.md, STATE.md, auto_target.json, current.json, register_state.json`
- The routine-mode-lifecycle Skill's documented operational allowlist (`.claude/skills/routine-mode-lifecycle/SKILL.md` step 9): the same six PLUS `engine/session/current_plan.md` AND `engine/session/archive/S-*.json`

Per CLAUDE.md "Routine-mode posture (load-bearing)", the operational allowlist is supposed to include `current_plan.md`. The wrapper enforces a narrower allowlist than the documented one.

**Local state at handoff:**

- Local HEAD: `cd33979` (close commit; 1 commit ahead of `origin/main`)
- `origin/main` HEAD: `2ccdd71` (the deliverable commit which DID push successfully; S-0061's substantive work is on origin/main)
- Working tree clean
- Routine lock acquired but pending release (will be released by the cleanup at the end of this routine fire)
- `engine/session/current.json` and `engine/session/current_plan.md` are deleted (staged in close commit)
- `engine/session/register_state.json`: `current_status: "closed"`, `next_id: "0062"`, `last_claimed: "S-0061"`
- `engine/session/auto_target.json`: P5-05 status = `complete`
- `engine/session/archive/S-0061.json`: created
- ENGINE_LOG and STATE.md: updated

**Why HANDOFF instead of in-band fix:** Per CLAUDE.md auto-mode interrupt criteria, this is a routine-mode session that cannot perform `git commit --amend` (forbidden by CLAUDE.md commit conventions) or `git reset --hard` (forbidden by destructive-action confirmation). Filing an Issue + writing HANDOFF + exiting cleanly is the documented routine-mode protocol for blockers per the skill body's "Auto-mode interrupt criteria" section.

**Action for next interactive session:**

1. Adjudicate the wrapper's allowlist gap. Two paths:
   - **Path A (fix the wrapper):** add `engine/session/current_plan.md` (and confirm `engine/session/archive/S-*.json`) to `routine_lifecycle_push.py`'s close-mode `EXPECTED_PATHS` (or whatever the variable is named — see [`engine/tools/routine_lifecycle_push.py`](engine/tools/routine_lifecycle_push.py)). Add a regression test under `engine/tools/test_routine_lifecycle_push.py` covering the close-with-current_plan.md-deletion case. Then push S-0061's close commit (e.g. `git push origin main` from interactive context — the harness gate doesn't fire for interactive sessions per ADR 0054).
   - **Path B (fix the convention):** if the intent is that `current_plan.md` should NOT be deleted at session close (i.e. left in place for next session to overwrite), update the routine-mode-lifecycle Skill body to explicitly say "do not delete current_plan.md at close" AND amend the S-0061 close commit to drop the deletion, then push.

2. Either way, file or extend an Issue documenting the wrapper-vs-skill allowlist gap.

3. After the close push lands, the routine cadence can resume normally; no Phase 5 task work was lost.

**Disposition:** tracked-as-issue #17

