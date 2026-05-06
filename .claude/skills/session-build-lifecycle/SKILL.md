---
name: session-build-lifecycle
description: Boot a Paideia build session — claim the next slot via the eager-claim ritual, run the in-session commit cadence, follow the push policy. Invoke at session boot when /start-engine has converted the conversation from exploration mode to build mode.
disable-model-invocation: true
---

# session-build-lifecycle

> Canonical executable form of the Paideia build-session boot procedure. The Layer 1 source-of-truth prose lives at [`engine/operations/session-build-lifecycle.md`](../../../engine/operations/session-build-lifecycle.md) per [ADR 0036](../../../engine/adr/0036-expression-contract-for-inward-documents.md). This skill body is the procedural form of the same procedure per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Updates flow doc → skill, never the reverse.

## When to invoke

A build session is any conversation that types `Start Engine` or invokes `/start-engine`. The `/start-engine` slash command's documented procedure routes through this skill. Default-mode (exploration) conversations do NOT run this lifecycle — they make no commits and claim no slot.

## Boot procedure (run in order)

### 1. Read `engine/STATE.md`

Get current phase, last build session, prior build session, next session work item, GitHub URL, Supabase project ref, infrastructure pointers. The "Next session work item" block names the work the session is about to do.

### 2. Cadence trigger check

Read `engine/session/register_state.json`. Parse the trailing 4-digit counter from `next_id` (the slot about to be claimed) and `last_audit_session` (the most recent completed audit). Compute `slots_since = next_id - last_audit_session`. The trigger fires when `slots_since >= health_check_cadence` (default cadence: 10 as of S-0033, was 30 pre-S-0033; overdue-catchup logic introduced at S-0041 — see ADR 0022 Consequences amendments). Two surfaces:

- When `slots_since == cadence` ("due"):

  > "Next slot is S-NNNN. Cadence trigger fires for a project health check (see `engine/operations/health-check.md`). Run the audit now or defer?"

- When `slots_since > cadence` ("overdue"):

  > "Cadence trigger fires; audit is OVERDUE by N session(s). The cadence-aligned slot was consumed by user-directed work without the audit firing. Run the audit now or document explicit deferral in outcome_summary."

User accepts → the session's work becomes the audit (which bumps `last_audit_session` at report-emit time, clearing the trigger). User defers → proceed with planned work; record the deferral in `outcome_summary` at close; the trigger fires again next session.

The overdue-catchup logic replaces the prior `next_id % cadence == 0` strict-modulo at S-0041 ([ADR 0022](../../../engine/adr/0022-periodic-project-health-checks.md) + [ADR 0043](../../../engine/adr/0043-hook-architecture.md) Consequences amendments) — strict-modulo silently slid the trigger by a full cadence whenever the aligned slot was consumed by other work. The SessionStart hook (`engine/tools/hooks/session-start.sh`) emits the same surface from the harness side regardless of how the session is launched. If `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041), the hook falls back to strict-modulo with a stderr log line so the regression surfaces.

### 2b. Persistent-warn surface

Per [ADR 0042](../../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md). Read the last 5 `engine/session/archive/S-NNNN.json` files (or all that exist if fewer). For each soft-warn category appearing in `outcome_summary_soft_warns` with a non-zero count in 3-or-more of those archives, surface:

> "Soft-warn `<category>` has fired in N of the last K sessions; consider addressing or escalating per `engine/operations/soft-warn-lifecycle.md`."

Suppress categories carrying an annotation in `engine/operations/tools-validate-interpretation.md`'s "Persistent-warn annotation" section. Surfacing is informational; the session decides whether to address inline, queue follow-up, or escalate per the 10-session-persistence criterion.

The calibration window per `soft-warn-lifecycle.md` is in effect until 5 structured-field archives accumulate (≈ S-0033). During the window, surface defers.

### 3. Query MemPalace

Use the MemPalace MCP tool `mempalace_search` with terms derived from `engine/STATE.md`'s next-session work item. Surface anything the user previously named that's relevant. Skip if MemPalace is not yet initialized (early sessions before S-0002).

**Mechanically backstopped by `mempalace_boot_query_skipped` soft-warn (per ADR 0056, S-0078).** The PostToolUse hook at `engine/tools/hooks/post-mempalace-tool-use.sh` records the call to `engine/session/current_mempalace.jsonl`; `validate.py --final-check` at shutdown emits the soft-warn if no `mempalace_search` call landed during the session.

### 3b. Read recent diary entries

Per [`mempalace-operations.md`](../../../engine/operations/mempalace-operations.md) "Project usage scope" (diary adopted at S-0032). Call `mempalace_diary_read agent_name="claude" last_n=3` to see the previous three sessions' first-person AI reflections — what surprised the prior AI, what they noticed but deferred, what felt load-bearing for this session, where their judgment was uncertain. Surface anything that bears on the work about to be claimed; skip silently when the diary is empty (early adoption window).

**Mechanically backstopped by `mempalace_diary_read_skipped` soft-warn (per ADR 0056, S-0078).**

### 4. Read referenced docs

`engine/STATE.md` and `ROADMAP.md` will name specific files relevant to the work. Read them before claiming the slot — the slot claim should be informed.

### 5. Build-readiness report check (substantive build sessions only)

Per [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md). STATE.md's "Next session work item" block names the report at `engine/build_readiness/<phase>_<chunk>.md` for substantive build sessions. Read the report end-to-end:

- **Pre-session decisions section** — Tier 1 resolutions inherited from the gate session. Implement against these, not around them.
- **Tier 2 decisions** — concrete column shapes, constraint forms, default values. Implement exactly as documented; the gate session settled these in advance precisely so the build session does not re-decide under build pressure.
- **Tier 3 forward pointers** — decisions explicitly deferred. Honor the deferral; do not pre-empt by inventing answers.
- **Success criteria** — verify these at shutdown.

If the report is **absent** for a session work item that requires one, convert this session to a gate session: do not author the planned artifacts; instead invoke the `build-readiness-gate` skill and produce the report. The next session opens as the build session.

If the report is **present but contains unresolved Tier 1 items**, halt and escalate to the user — the gate session did not finish its job. Do not attempt to resolve Tier 1 in-flight; the build session's mode is auto-by-default for routine judgment, not for foundational decisions.

Operational sessions (health checks, ENGINE_LOG-only edits, retrievability cleanups, gate sessions themselves) skip this step.

### 6. Eager-claim ritual

Atomic slot reservation. Run before any substantive work edits.

a. Read `engine/session/register_state.json`. Note `next_id` (e.g., `0007`).

b. Bump it to `next + 1`, set `last_claimed: "S-<next>"`, `current_status: "in_progress"`. Preserve the `description` and `format` fields.

c. Write `engine/session/current.json`:

```json
{
  "id": "S-<next>",
  "started_at": "<ISO-8601 UTC>",
  "status": "in_progress",
  "working_on": "<one-sentence summary>",
  "declared_scope": "<1-3 sentences naming what this session commits to deliver. Optionally end with `phase: <id>` matching a build_plan/MANIFEST.md identifier (e.g., `phase: P_3` or `phase: 4.5`); use `phase: NA-...` for operational/engine-apparatus work.>",
  "outcome_summary": null,
  "scope_delivery": null,
  "approved_plan": "<path or null>",
  "branch": "<current git branch>",
  "worktree": "<absolute path>"
}
```

The `declared_scope` field is required from S-0042 onward per [ADR 0049](../../../engine/adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The validator's `empty_declared_scope` soft-warn fires every commit until the field is populated; `phase_mismatch_declared_scope` fires when a `phase:` token doesn't match the build-plan manifest. The `scope_delivery` field starts `null` (in-flight) and is filled at shutdown.

d. Stage both files. Commit:

```
chore(session): eager-claim S-<NNNN> — <topic>
```

e. Fast-forward main on the parent repo:

```bash
git -C <parent-repo-path> merge --ff-only <branch>
```

f. Push:

```bash
git -C <parent-repo-path> push origin main
```

No per-push confirmation. Invoking `/start-engine` (or typing `Start Engine`) is the authorization for the lifecycle's pushes — eager-claim, in-session checkpoints, shutdown. Destructive operations (force-push, `git reset --hard`, branch deletion) still require explicit confirmation per the auto-mode interrupt criteria in [`escalation-criteria.md`](../../../engine/operations/escalation-criteria.md).

### 7. Begin substantive work

The slot is held atomically; concurrent sessions cannot collide. Make file edits, run tools, commit incrementally. Each commit must pass `engine/tools/validate.py` (enforced by the pre-commit hook).

For substantive build sessions, the build-readiness report is the canonical decision-of-record. When implementation choices arise that the report did not anticipate, they fall into one of three buckets:

- (a) routine in-session judgment, recorded in `outcome_summary`;
- (b) escalation candidates per [`escalation-criteria.md`](../../../engine/operations/escalation-criteria.md);
- (c) signals that the gate session under-specified — surface in `outcome_summary` so the next gate exercise refines.

## In-session commit cadence

- Commit at every meaningful checkpoint, not at session close. A session that produces 12 file changes should produce roughly 3-6 commits, not one giant commit.
- Each commit must pass `engine/tools/validate.py`. Hard-fails block; fix and retry.
- Soft-warns are allowed but accumulate in `outcome_summary_soft_warns` at close.
- Conventional Commits format. Types in active use: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`, `perf`. Eager-claim and archive use `chore(session):`.
- Always attribute via the `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` footer.

## Push policy within a session

- All routine pushes within a build session proceed without per-push confirmation.
- Destructive operations remain gated: force-push, amends to published commits, branch deletion, `git reset --hard`. Explicit confirmation regardless of session mode.
- Always FF main locally before pushing. Never push the worktree branch directly to remote main without going through the parent repo's main.

## Worktrees

Build sessions typically run in a Claude Code worktree (`/Users/.../.claude/worktrees/<name>/`). The worktree shares git history with the parent repo via the linked `.git` file. All commits land on the same branch as the worktree (`claude/<name>`). Fast-forward to main happens in the parent repo.

Before pushing, fast-forward main locally first; resolve any divergence in the worktree before forwarding. If the parent's main has moved (another session merged), rebase the worktree branch onto main, re-run validate, then re-attempt the FF.

## Recovery paths

### Eager-claim race (concurrent slot collision)

Two sessions reading `register_state.json` near-simultaneously can both write `S-NNNN` claim commits against the same slot. The first push wins; the second session's `git -C <parent> merge --ff-only <branch>` rejects because main has moved.

Resolution (still in boot procedure, no substantive work yet):

1. `git fetch origin main`, then inspect `git log origin/main..HEAD`. A peer's `eager-claim S-<same N>` commit on the upstream confirms collision.
2. From the worktree branch: `git reset --hard origin/main`. The destruction is bounded — only the local claim commit is lost; the boot rule is *claim first, work second*, so no substantive work is in flight.
3. Re-read `register_state.json` (now showing the peer's bumped `next_id`).
4. Re-run the eager-claim ritual against the new slot. Update `current.json`'s `id` and `working_on`. Commit, FF, push.
5. Resume substantive work.

### Pre-commit hook symlink

The hook itself lives at [`engine/tools/hooks/pre-commit`](../../../engine/tools/hooks/pre-commit) (tracked). The parent repo's `.git/hooks/pre-commit` is a symlink to that path; worktrees share the parent's `.git/hooks/` directory.

On a fresh clone, or if `readlink .git/hooks/pre-commit` shows a broken target:

```bash
cd .git/hooks
rm -f pre-commit
ln -s ../../engine/tools/hooks/pre-commit pre-commit
```

Verify: `head -3 .git/hooks/pre-commit` resolves and prints the bash shebang plus the Paideia hook header.

### MemPalace capture-hook failure log

The `Stop` and `PreCompact` hooks invoke [`engine/tools/hooks/mempalace-hook-wrapper.sh`](../../../engine/tools/hooks/mempalace-hook-wrapper.sh), which always exits 0 to the harness and routes capture failures to `.claude/logs/mempalace-hook.log` (gitignored per-clone state).

At session boot, after reading STATE.md and before the MemPalace context query, check the log:

```bash
test -s .claude/logs/mempalace-hook.log && cat .claude/logs/mempalace-hook.log
```

If non-empty, surface contents to the user — capture may have failed silently in earlier sessions. Acknowledged entries can be cleared by truncating the file (`: > .claude/logs/mempalace-hook.log`).

## Closing the session

When work is at a commitable checkpoint, invoke the `session-shutdown-sequence` skill to run the close-of-session protocol.

## See also

- [`engine/operations/session-build-lifecycle.md`](../../../engine/operations/session-build-lifecycle.md) — Layer 1 source-of-truth prose.
- [`engine/operations/session-shutdown-sequence.md`](../../../engine/operations/session-shutdown-sequence.md) — close-of-session protocol.
- [`engine/operations/escalation-criteria.md`](../../../engine/operations/escalation-criteria.md) — when to interrupt the user.
- [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md) — hard-fail vs soft-warn handling.
- [`.claude/commands/start-engine.md`](../../commands/start-engine.md) — slash command entry point.
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition this skill instantiates.
