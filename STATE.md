# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); prompt-pack Sessions 9 + 10 closed at S-0004 / S-0005 |
| **Last build session** | S-0005 (2026-04-29) — V1 decay parameters (`BASE_HALF_LIFE = 60 days`, `MAX_FLOOR = 0.6`) verified across five realistic trajectory scenarios under the engagement-depth distribution settled in ADR 0023; all scenarios match design intent, no parameter revisions; closes prompt-pack Session 10 without an ADR per ROADMAP.md §1.1. Procedure side-fix: `/start-engine` no longer requires per-push user confirmation — invocation is itself the authorization (docs + `.claude/settings.json` permission rules updated). |
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

**S-0006 — Phase 1.1 continuation: prompt-pack Session 11 (Historical Maximum Tracking)**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (24 ADRs) is the contract layer. The `/start-engine` procedure no longer requires per-push user confirmation — invocation is itself the authorization (per the S-0005 procedure fix).

Phase 1.1 continues with prompt-pack Session 11 because Session 10 (S-0005) confirmed V1 decay parameters. Session 11 settles a small schema decision: how to track the historical maximum aggregate that the decay floor's proficiency precondition depends on. Two options on the table per `docs/learner-model.md` ("Historical maximum tracking" paragraph): (a) stored high-water mark on a `user_concept_cache` table — simple, mutable, philosophically a compromise; or (b) recomputation from event history at query time — correct by construction but heavier than it sounds (requires simulating the running aggregate at each event's timestamp). Session 11 also interacts with `docs/learner-model.md` Offline and Sync because cached snapshots need to carry floor-active state.

Session prompt: `docs/prep-paideia-prompt-pack.md` Session 11. Source documents: `docs/learner-model.md` (Mastery Computation Stage 3 — Decay Floor; Offline and Sync), `docs/infrastructure.md` (scale-appropriate engineering principle), `adr/0015-event-sourced-learner-model.md` (the discipline that option (a) bends slightly), `adr/0017-postgres-recursive-ctes-over-owl-rdf.md` (the substrate cost of option (b)).

Scope (S-0006):
- Walk the tradeoffs concretely. At n=1–3 (current scale), recomputation is fine — but does this answer change at n=10,000? At n=100,000?
- Specify how the decision interacts with the offline-sync model: cached mastery snapshot pushed to clients must include floor-active state, so the tracking mechanism must feed snapshot generation in either branch.
- Land a concrete decision. If option (a): land an ADR documenting the schema addition (a `max_historical_score` column on whatever cache table emerges) and the philosophical compromise plus its bounds. If option (b): land an ADR documenting the recomputation algorithm and the scale at which it must be revisited.
- Either way: ADR is warranted because this decision has structural propagation across schema + sync + computation.

S-0006 success criteria: prompt-pack Session 11 closed; concrete decision recorded as a Phase 1 ADR (numbered 0025 if accepted as the next ADR slot); `docs/learner-model.md` Stage-3 paragraph updated to point at the ADR; `tools/validate.py` returns clean.

After S-0006: Phase 1.2 (`AGENT_INSTRUCTIONS.md` rendering policy) and Phase 1.3 (`confidence_level` column on node schema) close out Phase 1. Sessions 12–14 stay deferred (per `ROADMAP.md` §1.1).

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0001 close, the active set includes 6 newly-added items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers)
- OQ-PHASE8-A — Phase 8 evaluation baseline choice
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward (ADRs 0023–0024 added in S-0004 — engagement-depth aggregation, sub-signal storage shape).
