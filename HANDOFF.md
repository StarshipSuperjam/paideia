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
