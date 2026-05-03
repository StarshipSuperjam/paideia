# ADR 0043 — Hook architecture: enforce two-layer recording, surface cadence, verify STATE.md fields

- **Status:** Accepted
- **Date:** 2026-05-02
- **Deciders:** S-0031

## Context

Three CLAUDE.md "Posture vs machinery" rules are explicitly unenforced and have been carried by AI discipline alone:

1. **Two-layer decision recording** — every settled decision lands in BOTH an ADR AND a MemPalace `decision`-tagged drawer. The S-0030 health-check audit surfaced this: the `decisions` room carried 1 drawer for 42 ADRs (440 drawers across 5 rooms total). The discipline was structurally messy. (Amendment per S-0032 audit: the original "1/42" reading was inflated — it counted by room name only and missed `decision`-tagged drawers filed in the legacy `general` room. ENGINE_LOG cites at least 7 such drawers across S-0007 to S-0024; cross-room compliance was at least ~17% pre-mechanization, not 2.4%. The hook this ADR commits to remains warranted regardless — the room-split itself was a discipline gap, and either reading shows the rule was load-bearing only by AI judgment.)
2. **Startup ceremony order** — the four steps in CLAUDE.md "Startup ceremony" run by AI judgment; nothing prevents skipping or reordering. The cadence-trigger step in particular fires reliably only when `/start-engine` is invoked; a session that skips the slash command also skips the cadence check.
3. **Health-check cadence trigger** — readiness depends on the AI parsing `register_state.json`'s counter at boot. The S-0030 audit also surfaced a related off-by-one (`last_claimed mod 30 == 0` strictly fires at S-0031, not S-0030 as ROADMAP/ADR 0022 prose names) that posture-driven invocation has masked.

The Claude Code harness exposes 28 lifecycle hook events; the project wires 2 (`Stop` and `PreCompact` for MemPalace capture per [`mempalace-operations.md`](../operations/mempalace-operations.md)). The `PostToolUse` event fires after every Edit/Write tool call and exposes the matched file path; the `SessionStart` event fires at every session boot regardless of how the session was launched. Both are usable to mechanize the three posture rules above without altering the AI's authoring loop or blocking work.

The harness's hook contract is non-blocking by default: a hook script's exit code surfaces to the model as a tool result but does not abort the operation. This is the right default — converting posture rules to *blocking* gates would replace AI judgment with mechanical enforcement, which is too coarse for rules that admit legitimate exceptions (an ADR supersession that intentionally reuses an existing decision drawer; a STATE.md edit that legitimately leaves "Last commit on main" as a placeholder pointing at `git log`). The hooks introduced here all surface reminders, never block.

## Decision

The project wires three new Claude Code hooks, all non-blocking, all backed by shell scripts under `engine/tools/hooks/`. Each augments a posture rule into machinery without removing the underlying AI discipline.

1. **PostToolUse on ADR writes — two-layer recording reminder.** Matcher: `Edit|Write` tool with file path matching `^(engine|product)/adr/\d{4}-.*\.md$`. Script `engine/tools/hooks/post-adr-write.sh` parses the ADR id and title from the staged or written file, queries the MemPalace daemon (best-effort, `mempalace_search` via the existing CLI) for a `decision`-tagged drawer matching the ADR title slug or id, and emits a stderr reminder to the AI's tool-result stream when no such drawer exists: *"ADR NNNN '<title>' written; no matching `decision`-tagged MemPalace drawer found. Per CLAUDE.md two-layer recording, the conversation that produced this decision should be filed to MemPalace."* The hook always exits 0; the reminder is informational.

2. **SessionStart — cadence trigger and persistent-warn surface.** Event: `SessionStart`. Script `engine/tools/hooks/session-start.sh` parses `engine/session/register_state.json`, computes the cadence-trigger modulus using the prose-aligned logic (`next_id mod cadence == 0`) introduced as a paired fix in this session (see "Off-by-one fix" below), reads the last 5 `engine/session/archive/*.json` files for the persistent-warn surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md), and emits informational output. The output structure: a "Cadence:" line naming whether the trigger fires this session, followed by a "Persistent warns:" block listing soft-warn categories that fired in 3-or-more of the last 5 archives (or "none" if the calibration window per `soft-warn-lifecycle.md` is still in effect). The hook always exits 0.

3. **PostToolUse on STATE.md edits — required-fields verification.** Matcher: `Edit|Write` tool with file path equal to `engine/STATE.md`. Script `engine/tools/hooks/post-state-edit.sh` reads the post-edit file, verifies that the `## Current` table's "Last build session" row is populated (non-empty, no `<placeholder>` substring) and the `## Next session work item` block is non-empty (and contains no `<TBD>` / `<placeholder>` / `<fill ...>` tokens). Findings emit as a stderr reminder; the hook always exits 0. (An earlier draft of this ADR also named an "ADR count" consistency check between STATE.md prose and the engine ADR README index; that check was dropped before authoring because validate.py's existing `adr_index_consistency` check covers ADR-file-vs-README-index alignment, and STATE.md's prose ADR-count references are too varied to extract robustly. The `post-state-edit.sh` script implements only the two checks named in this paragraph.)

All three scripts follow the precedent established by `mempalace-hook-wrapper.sh`: best-effort execution, log to a per-clone path under `.claude/logs/` on hard error, never block the harness. The new scripts also fall under the existing Shell exemption in [`code-discipline.md`](../operations/code-discipline.md) "Exempt" section by line-count bound; they are not subject to the Layer 2 gate stack that governs Python under `engine/`.

### Off-by-one fix (paired with this ADR)

The S-0030 audit named the cadence-trigger off-by-one: `last_claimed mod 30 == 0` fires at the *boot of the session after* the cadence-numbered session, while ROADMAP/ADR 0022 prose says "the first health check expected around S-0030." Reading carefully: at S-0030's boot, `last_claimed = S-0029`, so `29 % 30 = 29`; the strict logic skips. At S-0031's boot, `last_claimed = S-0030`, so `30 % 30 = 0`; the strict logic fires — but by then the cadence-numbered session has already passed. The prose intent is to fire *at the cadence-numbered session itself*, which is what `next_id mod 30 == 0` produces (at S-0030 boot, `next_id = "0030"` parses to `30`, modulus zero, trigger fires).

Three files carry the cadence trigger logic; all three switch to the `next_id mod cadence == 0` form in this session:

- [`.claude/commands/start-engine.md`](../../.claude/commands/start-engine.md) step 2 — the slash command's documented boot procedure.
- [`engine/operations/health-check.md`](../operations/health-check.md) "When the trigger fires" — the operational reference.
- `engine/tools/hooks/session-start.sh` — the new SessionStart hook authored under this ADR.

The fix is amendment-only (no new ADR for the fix itself per [ADR 0036](0036-expression-contract-for-inward-documents.md)'s amendment asymmetry); this ADR records the fix in passing because the SessionStart hook is the first place the corrected logic lives in code.

## Consequences

`.claude/settings.json` gains three new hook entries. Each entry references a script under `engine/tools/hooks/`. The settings file remains short and readable; the substantive logic lives in the scripts.

`engine/tools/hooks/` gains three new scripts (`post-adr-write.sh`, `session-start.sh`, `post-state-edit.sh`). All three exit 0 unconditionally and log per-clone failures to `.claude/logs/<hook-name>.log` (gitignored) following the `mempalace-hook-wrapper.sh` precedent. The scripts are shell — under the existing exemption in [`code-discipline.md`](../operations/code-discipline.md) — and do not require Python contract blocks.

CLAUDE.md's "Posture vs machinery" section narrows: two-layer decision recording moves from posture to machinery (still soft-enforced — the hook reminds, does not block); the startup ceremony order's cadence-trigger step moves from posture to machinery (the SessionStart hook fires regardless of `/start-engine`); STATE.md required-fields verification was not in the original posture list but joins the machinery set.

The pushback rule and the rest of the startup ceremony order remain posture — no machinery for "AI noticed an unnamed risk" or for "AI read these four files in this order" exists. The reduction in posture surface is meaningful (three rules → zero) but the posture model itself is intact.

Trade-offs accepted:

- **Soft enforcement leaves drift possible.** A hook that reminds but does not block can be ignored. The S-0030 audit estimated posture's yield, originally reported as 1/42 = 2.4% compliance; the S-0032 audit corrected this to a cross-room count of at least ~17% pre-mechanization (the `1/42` measured drawers in the `decisions` room only, missing legacy `decision`-tagged drawers in the `general` room). Soft enforcement is expected to lift compliance materially but not to 100%. The next health check (cadence at S-0040 under the cadence-10 default per ADR 0022 Consequences amendment at S-0032) will measure post-mechanization yield against the corrected baseline.
- **Hook scripts are shell, not Python.** They fall under the line-count-bound exemption in code-discipline.md. Bug surface is wider than for gated Python; mitigation is the non-blocking exit-0 contract — a buggy hook surfaces noise, not failure.
- **MemPalace daemon dependency.** The `post-adr-write.sh` hook queries the MemPalace daemon. When the daemon is down, the hook logs a fail line and exits 0 (no false-positive reminder; reminder defers until daemon is available). Persistent daemon-down state surfaces in `.claude/logs/post-adr-write.log` and at the next session boot via the existing `.claude/logs/mempalace-hook.log` check in `session-build-lifecycle.md`.
- **Cadence-trigger fix changes the reading of past archives.** Pre-fix, `S-NNNN` was conceptually "the audit happens at S-NNNN+1 boot." Post-fix, "the audit happens at S-NNNN boot." S-0030's manual fire honored prose intent; under the cadence-30 default in force at the time of this ADR, future cadence triggers were S-0060 / S-0090 / etc. The cadence tightened to 10 at S-0033 per ADR 0022 Consequences amendment, so post-S-0033 fires land at S-0040, S-0050, S-0060, etc. The off-by-one fix this ADR landed is independent of the cadence value — both interact correctly.
- **Settings.json hook ordering.** Multiple `PostToolUse` hooks can match the same Edit; Claude Code runs them in array order. The two new `PostToolUse` hooks (ADR write, STATE.md edit) match disjoint paths and so do not interact.

The hook architecture is additive to the existing `Stop` and `PreCompact` hooks for MemPalace capture; those continue to fire on the same events as before. No existing hook configuration changes.

## See also

- [ADR 0022](0022-periodic-project-health-checks.md) — the cadence trigger this ADR's SessionStart hook surfaces.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the persistent-warn surface this ADR's SessionStart hook reads.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — amendment asymmetry for the cadence-fix amendments.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — sibling structural decision authored in S-0031; converts recipe-shaped ops docs to user-defined skills (separate concern, paired in scope).
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — the Shell exemption the new scripts fall under.
- [`engine/tools/hooks/`](../tools/hooks/) — the directory the new scripts live in, alongside `pre-commit` and `mempalace-hook-wrapper.sh`.
- [`.claude/settings.json`](../../.claude/settings.json) — where the hooks are wired.
- [`.claude/commands/start-engine.md`](../../.claude/commands/start-engine.md) — slash command updated with the cadence-trigger fix.
- [`engine/operations/health-check.md`](../operations/health-check.md) — operational doc updated with the cadence-trigger fix.
- [`docs/health-checks/S-0030.md`](../../docs/health-checks/S-0030.md) — the audit that surfaced both the two-layer-recording gap and the cadence off-by-one.
