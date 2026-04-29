# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — Foundation (in progress; one foundation session remaining) |
| **Last build session** | S-0002 (2026-04-29) — procedural layer + MemPalace indexing + CONTEXT.md retirement |
| **Last commit on main** | (see `git log --oneline -1` on main) |
| **Backup tag** | `pre-foundation-v0.0.0` at commit `fa70b8c` (pre-foundation state; recoverable via `git reset --hard pre-foundation-v0.0.0`) |

## Infrastructure

| Component | Value |
|---|---|
| **Supabase project** | `paideia-dev`, project ref `ozooosgnuzxqqypotlke`, PostgreSQL 17.6 |
| **Supabase MCP** | configured in `.mcp.json` (gitignored, contains PAT) |
| **MemPalace** | installed at `/Users/shanekidd/Library/Python/3.9/bin/`; MCP server `mempalace-mcp` configured in `.mcp.json`; wing `paideia` indexed at S-0002 (414 drawers across rooms `general` + `operations`); capture hooks wired in `.claude/settings.json` |
| **Python** | system Python 3.9.6 at `/usr/bin/python3`; user-scope packages at `/Users/shanekidd/Library/Python/3.9/bin/` |
| **Anthropic API** | env var `ANTHROPIC_API_KEY` set in local `.env` (gitignored) |

## Next session work item

**S-0003 — ADR collection (closes Phase 0)**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. The slash command at `.claude/commands/start-engine.md` claims the next slot via the eager-claim ritual. CLAUDE.md is now auto-loaded; MemPalace `mempalace_search` is queryable from boot.

Scope:
- `adr/README.md` — index, Nygard template recap, status-conventions table (links to `docs/operations/adr-authoring.md` for full guidance).
- `adr/0001-pedagogical-edges-not-historical.md` through `adr/0012-freshman-defaults-autodidact-ceiling.md` — the 12 strong working commitments now living in `docs/MISSION.md`. Each ADR carries Status, Date (the 2026-04-07 / 04-08 / 04-09 dates from CONTEXT.md's chronological summary, recoverable from MemPalace and from design-doc Added/Revised lines), Context, Decision, Consequences. Status: `Accepted`.
- `adr/0013-mastery-verification-organic-escalation.md` through `adr/0022-periodic-project-health-checks.md` — 10 architectural decisions absorbed from `design-reasoning.md`. ADR 0022 is the "periodic project health checks" decision that the cadence-trigger machinery (already built in S-0001) implements.
- Update `docs/MISSION.md` Strong working commitments section to add ADR cross-references after each commitment.
- Update `docs/CROSS_REFERENCES.md` to add Phase-0 → Phase-1 boundary check (every commitment has a corresponding ADR).
- **Final scrub:** delete `design-reasoning.md` (content fully absorbed into ADRs 0013-0022). Verify by grep that nothing else references it.

S-0003 success criteria: 22 ADRs in `adr/` with `Status: Accepted`; `tools/validate.py` returns clean (the `adr_status` check now actively validates ADR Status fields); `design-reasoning.md` retired; STATE.md current-phase pointer flips to "Phase 0 — closed; Phase 1 — Contract Lock pending."

After S-0003: **Phase 1 — Contract Lock.** Per `ROADMAP.md` §1.1, the first Phase-1 session is prompt-pack Session 9 (Engagement Depth Aggregation) — blocks prototype work. Deferred prompt-pack sessions 12-14 stay deferred.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0001 close, the active set includes 6 newly-added items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers)
- OQ-PHASE8-A — Phase 8 evaluation baseline choice
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions absorbed from prior design-reasoning. **Becoming ADRs 0001-0022 in S-0003.** As of S-0002 close: the 12 commitments live at `docs/MISSION.md` (Strong working commitments section) and `ROADMAP.md` (Strong working commitments referenced throughout). Architectural decisions remain at `design-reasoning.md` (transitional); S-0003 absorbs them into ADRs and deletes the file.

See ROADMAP.md "Strong working commitments referenced throughout" for the canonical list.
