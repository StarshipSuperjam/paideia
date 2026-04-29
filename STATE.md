# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — Foundation (in progress) |
| **Last build session** | S-0001 (2026-04-29) — structural foundation + retirement of obsolete pre-foundation source files |
| **Last commit on main** | (set at S-0001 close commit; see `git log --oneline -1` on main) |
| **Backup tag** | `pre-foundation-v0.0.0` at commit `fa70b8c` (pre-foundation state; recoverable via `git reset --hard pre-foundation-v0.0.0`) |

## Infrastructure

| Component | Value |
|---|---|
| **Supabase project** | `paideia-dev`, project ref `ozooosgnuzxqqypotlke`, PostgreSQL 17.6 |
| **Supabase MCP** | configured in `.mcp.json` (gitignored, contains PAT) |
| **MemPalace** | installed at `/Users/shanekidd/Library/Python/3.9/bin/`; MCP server `mempalace-mcp` configured in `.mcp.json`; **wing/rooms/drawers indexed in S-0002** |
| **Python** | system Python 3.9.6 at `/usr/bin/python3`; user-scope packages at `/Users/shanekidd/Library/Python/3.9/bin/` |
| **Anthropic API** | env var `ANTHROPIC_API_KEY` set in local `.env` (gitignored) |

## Next session work item

**S-0002 — Procedural layer + MemPalace indexing + CONTEXT.md split**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. The slash command at `.claude/commands/start-engine.md` claims the next slot via the eager-claim ritual.

Scope:
- `CLAUDE.md` (~80 lines) — lightweight startup ceremony + standing rules + topical pointers into `docs/operations/`. Includes the Standing Pushback Rule, Auto-Mode Interrupt Criteria, Budget Guidance, End-State-Quality First-Pass principle, Two-Layer Decision Recording, Commit Conventions, and the 5-step build-session boot procedure (with health-check cadence trigger).
- `docs/operations/README.md` + 11 topic files: session-build-lifecycle, session-shutdown-sequence, mempalace-operations, mempalace-tagging-conventions, tools-validate-interpretation, tools-sweep-worktrees, escalation-criteria, adr-authoring, sub-agent-validation, seed-chunked-authoring (Phase 4 placeholder), health-check (audit categories + report template + cadence policy)
- `docs/MISSION.md` — extracted from CONTEXT.md ("What This Is" + cross-domain porosity + audience framing)
- `docs/CROSS_REFERENCES.md` — extracted from CONTEXT.md File Dependencies table
- MemPalace: `mempalace init docs/` to auto-detect rooms from folder structure; `mempalace mine docs/` to index design docs as drawers
- User-level memory: write `feedback_pushback_rule.md` to the user-memory system; add to MEMORY.md index
- Configure Claude Code stop/precompact hooks per the MemPalace-capture finding in HANDOFF.md
- **Final scrub:** delete `CONTEXT.md` (after content fully absorbed). `design-reasoning.md` stays for S-0003.

S-0002 success criteria: a fresh cold-start session reading CLAUDE.md + STATE.md + querying MemPalace can identify the next work item without ambiguity. `tools/validate.py` returns clean.

After S-0002: **S-0003 — ADR collection** (22 ADRs absorbing CONTEXT.md commitments + design-reasoning entries + new architectural decisions). Then Phase 1 begins.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0001 close, the active set includes 6 newly-added items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers)
- OQ-PHASE8-A — Phase 8 evaluation baseline choice
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions absorbed from prior design-reasoning. **Becoming ADRs 0001-0022 in S-0003.** During S-0001 the source content remains at `CONTEXT.md` (repo root, transitional) and `design-reasoning.md` (also transitional); S-0002 splits CONTEXT.md and deletes it; S-0003 absorbs design-reasoning.md into ADRs and deletes it.

See ROADMAP.md "Strong working commitments referenced throughout" for the canonical list.
