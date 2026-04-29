# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock pending |
| **Last build session** | S-0003 (2026-04-29) — 22-ADR collection, MISSION/CROSS_REFERENCES updates, design-reasoning.md retirement |
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

**S-0004 — Phase 1 entry: prompt-pack Session 9 (Engagement Depth Aggregation)**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. The slash command at `.claude/commands/start-engine.md` claims the next slot via the eager-claim ritual. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the 22-ADR collection in `adr/` is the contract layer.

Phase 1 — Contract Lock — opens with prompt-pack Session 9 because it blocks prototype work (composite engagement signal feeds mastery computation). Session prompt: `docs/prep-paideia-prompt-pack.md` Session 9. Source documents to load: `docs/pedagogy.md` (engagement-depth aggregation; assessment rubric per ADR 0010), `docs/learner-model.md` (mastery computation; the consumer of the engagement signal), `docs/architecture.md` (event schema), `adr/0010-continuous-contextual-assessment.md` and `adr/0015-event-sourced-learner-model.md` (the load-bearing ADRs).

Scope (S-0004):
- Settle the composite engagement-depth variable: which sub-signals (generative ratio, scaffolding proximity, novelty, plus any others surfaced in deliberation), how they combine (formula or weighted sum), how `engagement_depth` is stored on `learner_events` (single column with sub-signals derivable, or sub-signal columns with composite computed at query time).
- If the deliberation produces a settled architectural choice, author a new ADR (next number in sequence: ADR 0023). If multiple settled choices, multiple ADRs.
- Update `docs/pedagogy.md` and `docs/learner-model.md` with the resolved details. CHANGELOG entries per material-change criteria.
- If any tensions surface that don't settle in-session, add to `docs/tensions.md`.

S-0004 success criteria: prompt-pack Session 9 closed; engagement-depth variable defined with concrete sub-signal list and composition rule; relevant design docs updated; new ADR(s) (if any) `Status: Accepted`; `tools/validate.py` returns clean.

After S-0004: prompt-pack Session 10 (Decay Parameter Verification) and Session 11 (Historical Maximum Tracking) remain in Phase 1.1. Sessions 12–14 stay deferred per `ROADMAP.md` §1.1. Phase 1.2 (`AGENT_INSTRUCTIONS.md`) and Phase 1.3 (`confidence_level` on node schema) follow.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0001 close, the active set includes 6 newly-added items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers)
- OQ-PHASE8-A — Phase 8 evaluation baseline choice
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit.
