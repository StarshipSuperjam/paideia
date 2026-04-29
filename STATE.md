# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); prompt-pack Session 9 closed at S-0004 |
| **Last build session** | S-0004 (2026-04-29) — engagement-depth aggregation settled (ADR 0023: floored weighted geometric mean); sub-signal storage shape settled (ADR 0024: sub-signals stored raw, composite derived); `scaffolding_proximity` renamed to `scaffolding_distance` across living docs |
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

**S-0005 — Phase 1.1 continuation: prompt-pack Session 10 (Decay Parameter Verification)**

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (now 24 ADRs) is the contract layer.

Phase 1.1 continues with prompt-pack Session 10 because Session 9 (S-0004) settled the engagement-depth aggregation. Session 10 verifies whether the V1 decay parameters (`BASE_HALF_LIFE = 60 days`, `MAX_FLOOR = 0.6`) produce correct trajectories under realistic usage patterns — pure arithmetic, run the numbers. Session prompt: `docs/prep-paideia-prompt-pack.md` Session 10. Source documents: `docs/learner-model.md` (Mastery Decay, Mastery Computation, Active-Use Decay Suppression, **and the new compute_engagement_depth helper from S-0004**), `adr/0023-engagement-depth-aggregation.md` (so the engagement_depth distribution scenarios use the settled formula), `adr/0015-event-sourced-learner-model.md` (the storage discipline), `adr/0019-two-column-rigor-score-override.md` (the rigor signal that modulates decay).

Scope (S-0005):
- Run five concrete trajectory calculations: (1) active learner / low-rigor concept with weekly callbacks, (2) active learner / high-rigor concept with weekly callbacks, (3) abandoned concept (6-month silence), (4) mastery verification trajectory across multiple events, (5) backward-inference event impact on prerequisite mastery state.
- For each: verify floor activates correctly, decay rate matches phenomenology, callbacks suppress decay sufficiently, mastery threshold (0.7) is reachable through realistic event chains.
- **New constraint from S-0004:** trajectories must be computed using the engagement-depth distribution that ADR 0023's aggregation actually produces (roughly 0.1–0.9 for real teaching exchanges; 0.5 fixed for `backward_inference`; 0.3 fixed for `incidental_mention`). The double-leverage of `engagement_depth` (multiplies `raw_strength` AND modulates `half_life`) means BASE_HALF_LIFE was set assuming a particular depth distribution; verify that `BASE_HALF_LIFE = 60 days` still produces correct phenomenology under the settled formula.
- If any V1 parameters need adjustment, propose revised values and re-run the scenarios. Land revised parameters as a revision to `docs/learner-model.md` V1 defaults paragraph + a CHANGELOG entry. If the parameter system itself needs structural change (e.g., MAX_FLOOR should be rigor-specific), author an ADR.
- If parameters survive verification: record the verification calculations in MemPalace (`decision`-tagged) and close Session 10 without an ADR (verification of pre-existing parameters does not require a new ADR; the verification record + CHANGELOG note is sufficient).

S-0005 success criteria: prompt-pack Session 10 closed; five scenario trajectories computed; V1 parameters either confirmed or revised with rationale; `tools/validate.py` returns clean.

After S-0005: prompt-pack Session 11 (Historical Maximum Tracking) — small schema decision, can run anytime per `ROADMAP.md` §1.1. Sessions 12–14 stay deferred. Phase 1.2 (`AGENT_INSTRUCTIONS.md`) and Phase 1.3 (`confidence_level` on node schema) follow.

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
