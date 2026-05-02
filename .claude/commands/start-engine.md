---
description: Convert this conversation to a build session — claims the next slot, allows commits and project file edits.
---

# /start-engine

Convert the current Claude Code conversation from default exploration mode (no commits, no project edits) into a build session (claims a slot, may commit, may modify project files).

## Boot procedure (the AI runs these in order)

1. **Read `engine/STATE.md`** — get current phase, last build session, next session work item, GitHub URL, Supabase project ref, infrastructure pointers.

2. **Check the health-check cadence trigger.** Read `engine/session/register_state.json`. Parse the trailing 4-digit counter from `next_id` (the slot about to be claimed). If `next_id mod health_check_cadence == 0` (default cadence 30), propose a health-check session: *"Next slot is S-NNNN. Cadence trigger fires for a project health check (see `engine/operations/health-check.md`). Run the audit now or defer?"* User accepts (work becomes the audit) or defers (proceed with planned work). The trigger uses `next_id` (the about-to-be-claimed slot) so the audit runs at the cadence-numbered session itself, matching ROADMAP.md and ADR 0022 prose intent. The off-by-one against `last_claimed` was surfaced by the S-0030 audit and corrected at S-0031 per [ADR 0043](../../engine/adr/0043-hook-architecture.md). The same logic is mirrored in the SessionStart hook script `engine/tools/hooks/session-start.sh`.

2b. **Surface persistent soft-warns from recent archives.** Per [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md). Read the last 5 `engine/session/archive/S-NNNN.json` files (or all that exist if fewer). For each soft-warn category appearing in `outcome_summary_soft_warns` with a non-zero count in 3-or-more of those archives, surface: *"Soft-warn `<category>` has fired in N of the last K sessions; consider addressing or escalating per `engine/operations/soft-warn-lifecycle.md`."* Suppress categories carrying an annotation in `engine/operations/tools-validate-interpretation.md`'s "Persistent-warn annotation" section that matches the current session's condition. Surfacing is informational; the session decides whether to address inline, queue follow-up, or escalate per the 10-session-persistence criterion.

3. **Query MemPalace for context relevant to the next work item.** Use the MemPalace MCP tool `mempalace_search` with a query derived from `engine/STATE.md`'s `next_session_work`. Surface anything the user named in MemPalace that's relevant. (Skip if MemPalace MCP server is not yet loaded — early sessions before S-0002.)

4. **Read referenced ADRs and docs.** `engine/STATE.md` and `ROADMAP.md` will name specific files relevant to the work item. Read them.

5. **Claim the next slot via the eager-claim ritual:**

   a. Read `engine/session/register_state.json`. Note `next_id` (e.g., `0007`).

   b. Bump it: rewrite as `{"next_id": "<next+1>", "last_claimed": "S-<next>", "current_status": "in_progress", "description": ..., "format": ...}`.

   c. Write `engine/session/current.json`:
      ```json
      {
        "id": "S-<next>",
        "started_at": "<ISO-8601 UTC>",
        "status": "in_progress",
        "working_on": "<one-sentence summary of the planned work>",
        "outcome_summary": null,
        "approved_plan": "<path or null>",
        "branch": "<current git branch>",
        "worktree": "<absolute path to current worktree>"
      }
      ```

   d. Stage `engine/session/register_state.json` and `engine/session/current.json`. Commit with message `chore(session): eager-claim S-<NNNN> — <topic>`.

   e. Fast-forward main on the parent repo: `git -C <parent-repo-path> merge --ff-only <branch>`.

   f. Push: `git -C <parent-repo-path> push origin main`. No per-push confirmation. Invoking `/start-engine` is the authorization for the lifecycle's pushes (eager-claim, in-session checkpoints, shutdown). Destructive operations (force-push, `git reset --hard`, branch deletion) still require explicit confirmation per the auto-mode interrupt criteria.

6. **Begin substantive work.** The slot is held atomically; concurrent sessions cannot collide. Make file edits, run tools, commit incrementally as work progresses. Each commit must pass `engine/tools/validate.py` (enforced by pre-commit hook).

## Session shutdown (at end of work)

7. **Audit pass.** Run `engine/tools/validate.py`. Address any hard-fails. Soft-warns are recorded in `engine/session/current.json`'s `outcome_summary` field.

8. **Spot-check.** For every artifact created or modified in this session: confidence labels honest? type framing correct? cross-references resolve? Audit catches structural mistakes; spot-check catches judgment mistakes.

9. **Update `engine/STATE.md`** with the new last-session pointer and the next session's work item.

10. **Update `engine/ENGINE_LOG.md`** under `[Unreleased]` with Added/Changed/Removed/Deprecated entries for material engine changes (per the material-change criteria in `engine/operations/session-shutdown-sequence.md`). The file was named `CHANGELOG.md` before [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md); the `CHANGELOG.md` filename is now reserved for the future learner-visible product release log (lives at `product/CHANGELOG.md` from S-0024 onward as a reserved stub).

11. **Fill `outcome_summary`** in `engine/session/current.json` (~50 words, what got done — feeds health-check telemetry).

12. **Archive the claim.** Move `engine/session/current.json` to `engine/session/archive/S-<NNNN>.json`. Update `engine/session/register_state.json` to `current_status: closed`.

13. **Final commit + main FF + push.** Conventional commit message. No per-push confirmation — the `/start-engine` invocation already authorizes the shutdown push.

## Default-mode posture (when this command is NOT invoked)

The conversation is exploration. **No project file edits to tracked files. No commits. No slot claim. No ENGINE_LOG/ADR/STATE updates.** Sketch in conversation. If the discussion converges on something worth committing, offer the conversion: *"This feels worth making formal — want to /start-engine?"*

MemPalace captures the exploration conversation under the `exploration` tag (once Claude Code stop/precompact hooks are wired in S-0002) so future sessions can recall "we considered X, rejected for reason Y" without re-litigation.

## Auto-mode interrupt criteria

While running, the AI may NOT pause and escalate to the user EXCEPT for:
- **Irreversible-with-unclear-path:** a decision propagates as irreversible structure across multiple downstream sessions AND the right direction is genuinely unclear
- **Unsolvable:** multiple approaches tried, no viable path
- **Destructive-action confirmation:** any `rm -rf`, `git reset --hard`, force-push, etc. — confirm before executing

Routine judgment calls during the session are session-internal and recorded in `engine/session/current.json`'s outcome_summary, not escalated.

## Budget guidance

Substantive extraction work: target 60% context, hard cap 70%. Mechanical/procedural work: target 70%, hard cap 80%. If a session hits its cap mid-work, halt at the next sensible boundary, write `outcome_summary` with partial-completion notes, archive `engine/session/current.json` with `status: closed_partial`, and the next session picks up from where this one stopped.

## Standing pushback rule

The AI is pre-authorized to surface unnamed risks, hidden pitfalls, and unstated opportunities at the moment of noticing. Push back specifically — name the concern concretely. Apply equally to user proposals AND AI proposals (self-critique). The bar is "I see a specific thing you may not be seeing," not "I should challenge this on principle." Calibrate by mode: looser when user is venting/exploring, tighter when proposing a commitment.
