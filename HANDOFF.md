# Handoff Log

> Running log of items deferred to a future major-state-transition session. Not a contract; a convenience so transition sessions don't re-solve already-solved problems. Add entries when you encounter something a future session needs to know but that doesn't belong in ENGINE_LOG, an ADR, or `docs/tensions.md`.

---

## Reserved CHANGELOG.md stub (set in S-0022 for S-0023 boot)

**Bundle into S-0023's boot, before the Phase 2 build_plan authoring begins.** The S-0022 ADR 0037 rename ([ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md)) reserved the `CHANGELOG.md` filename for the future learner-visible product release log (first entry at Phase 9). S-0022 left the filename absent from the tree and called the absence "the signal." That framing is functionally weak — absence only signals the reservation to a reader who already loaded ADR 0037, and a future contributor or Claude session walking up cold can reasonably re-create `CHANGELOG.md` from scratch without knowing it's reserved.

**The fix:** create `CHANGELOG.md` at the repo root as a reserved stub. Contents:

- Title: `# Paideia Changelog (reserved)`
- Preamble naming the reservation explicitly: this file is reserved for product release notes per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md); first entry lands at Phase 9 release prep with v1.0.0; engine state-of-record audit log lives in [`ENGINE_LOG.md`](ENGINE_LOG.md); the third expression-contract gap governing learner-visible release-log voice settles at OQ-OUTWARD-VOICE before Phase 7
- No `[Unreleased]` section, no entries — just the reservation notice
- Cross-link from `ENGINE_LOG.md`'s preamble (already names "the absence is the signal" — rewrite that line to point at the reserved stub instead)

**Validator carve-out:** `tools/validate.py` doesn't currently require `CHANGELOG.md` (REQUIRED_TOP_LEVEL was updated at S-0022 to name `ENGINE_LOG.md` instead). The new stub is purely informational; the validator can stay as-is. If a future check ever wants to enforce the stub's preamble shape, that's a separate refinement under [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md)'s amendment discipline.

**Scope:** ~10 minutes at S-0023 boot. Add the file, update `ENGINE_LOG.md`'s preamble line, log a single ENGINE_LOG entry under `[Unreleased]` (Added: reserved CHANGELOG.md stub), then proceed to the Phase 2 build_plan work.

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
