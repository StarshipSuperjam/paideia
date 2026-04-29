# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006 |
| **Last build session** | S-0006 (2026-04-29) — Phase 1.1 prompt-pack Session 11: historical maximum tracking. Settled `max_historical_score` on the existing `mastery_snapshots` table (per ADR 0015), defined as the asymptotic cap on cumulative undecayed raw strength over **substantive** interaction types (excludes `incidental_mention` and `backward_inference`); `docs/learner-model.md` Stage 3 pseudocode updated; ADR 0025 lands as the next Phase 1 ADR. Closes prompt-pack Session 11 per ROADMAP.md §1.1. Sessions 12–14 remain deferred. |
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

**S-0007 — Phase 1.2: `AGENT_INSTRUCTIONS.md` rendering policy**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (25 ADRs) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

Phase 1.1 closed at S-0006 (prompt-pack Sessions 9, 10, 11 settled). Phase 1.2 authors a standalone `AGENT_INSTRUCTIONS.md` rendering-policy file extracted from `docs/pedagogy.md`. The file specifies what tokens the teaching agent may surface to the learner versus what stays internal to the system — the prompt-layer contract that keeps mastery-state names, evidence-event references, edge-confidence values, and graph-machinery tokens out of learner-facing prose.

Source documents:
- `docs/pedagogy.md` (extraction source — find the rendering-policy material currently embedded there)
- ADR 0010 (continuous and contextual assessment — the rubric that defines forbidden assessment-mechanic tokens)
- ADR 0014 (Sonnet teaches, Opus reviews — the two-agent split that affects what each surface emits)
- ADR 0023 (engagement-depth aggregation — `scaffolding_distance` is the canonical surviving variable name; `scaffolding_proximity` language is forbidden)
- `docs/MISSION.md` (audience framing — freshman-default rendering posture)

Scope (S-0007):
- Identify the rendering-policy material currently in `docs/pedagogy.md` and decide what gets extracted vs what stays.
- Author `AGENT_INSTRUCTIONS.md` at production quality (end-state-quality first-pass per CLAUDE.md):
  - **Forbidden tokens** with explicit rationale per ADR: mastery-state names (`exposed`/`proficiency`/`mastery`), prerequisite-edge framing, evidence-event references (`learner_events`, `engagement_depth`, `raw_strength`), scaffolding-proximity/scaffolding-distance language, weight/confidence/provenance exposure, `graph_version` references, tension-log mechanism (`tension_log` table, `OQ-*` IDs).
  - **Surviving tokens**: concept names, domain-area names. Citation rules. Uncertainty posture.
  - **Worked example** showing the policy in operation against a stub learner-state input.
- Cross-link `docs/pedagogy.md` → `AGENT_INSTRUCTIONS.md`.
- An ADR is warranted: the rendering policy is the prompt-layer contract for the teaching agent, with structural propagation to every Sonnet teaching session. Number ADR 0026 if accepted.

S-0007 success criteria: `AGENT_INSTRUCTIONS.md` exists at repo root with the forbidden/surviving token lists, citation rules, uncertainty posture, and worked example; `docs/pedagogy.md` cross-links to it; ADR 0026 lands as the rendering-policy contract; `tools/validate.py` returns clean.

After S-0007: Phase 1.3 (`confidence_level` column on node schema in `docs/architecture.md`) closes out Phase 1. Sessions 12–14 remain deferred (per `ROADMAP.md` §1.1).

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
