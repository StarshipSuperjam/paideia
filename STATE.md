# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007 ahead of §1.2 |
| **Last build session** | S-0007 (2026-04-29) — Phase 1 insertion ahead of planned Phase 1.2: privacy posture commitments. ADR 0026 lands the principle (persistent learner storage is structural, not substantive) with three sub-decisions: `tension_log.exchange_summary` becomes JSONB-with-named-fields (replacing `TEXT NOT NULL`); `learner_events.context` schematized as fixed structured columns at Phase 3; conversation transcripts are not persisted as system-of-record data (operational TTL: session-end default, 24-hour hard cap). OQ-PRIVACY-A (erasure mechanism) and OQ-PRIVACY-B (institutional vs individual regime, direction-neutral) opened in `docs/tensions.md` — both decide-before-Phase 3. ROADMAP Phase 8 success criteria gains a privacy-policy/Apple-App-Store-questionnaire bullet pinning that work to the 2–4 week Apple lead time. `docs/self-correction.md` `tension_log` schema updated; cross-refs added in `architecture.md`, `business.md`, `CROSS_REFERENCES.md`. `tools/validate.py` clean. |
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

**S-0008 — Phase 1.2: `AGENT_INSTRUCTIONS.md` rendering policy** *(formerly planned for S-0007; bumped one slot by the S-0007 privacy-posture insertion)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (26 ADRs) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

Phase 1.1 closed at S-0006 (prompt-pack Sessions 9, 10, 11 settled). S-0007 inserted the privacy-posture commitment (ADR 0026) ahead of Phase 1.2 because the Phase 8 Apple App Store privacy questionnaire is a blocking artifact whose 2–4 week Apple lead time means the posture had to settle now, before Phase 3 schema authoring locks shapes that would otherwise need retrofit. Phase 1.2 itself is unchanged in scope, just shifted one slot.

Phase 1.2 authors a standalone `AGENT_INSTRUCTIONS.md` rendering-policy file extracted from `docs/pedagogy.md`. The file specifies what tokens the teaching agent may surface to the learner versus what stays internal to the system — the prompt-layer contract that keeps mastery-state names, evidence-event references, edge-confidence values, and graph-machinery tokens out of learner-facing prose.

Source documents:
- `docs/pedagogy.md` (extraction source — find the rendering-policy material currently embedded there)
- ADR 0010 (continuous and contextual assessment — the rubric that defines forbidden assessment-mechanic tokens)
- ADR 0014 (Sonnet teaches, Opus reviews — the two-agent split that affects what each surface emits)
- ADR 0023 (engagement-depth aggregation — `scaffolding_distance` is the canonical surviving variable name; `scaffolding_proximity` language is forbidden)
- ADR 0026 (privacy posture — the new constraint that Sonnet's `tension_log.exchange_summary.pattern_observed` writing policy must enforce; rendering policy and emission policy are adjacent contracts)
- `docs/MISSION.md` (audience framing — freshman-default rendering posture)

Scope (S-0008):
- Identify the rendering-policy material currently in `docs/pedagogy.md` and decide what gets extracted vs what stays.
- Author `AGENT_INSTRUCTIONS.md` at production quality (end-state-quality first-pass per CLAUDE.md):
  - **Forbidden tokens** with explicit rationale per ADR: mastery-state names (`exposed`/`proficiency`/`mastery`), prerequisite-edge framing, evidence-event references (`learner_events`, `engagement_depth`, `raw_strength`), scaffolding-proximity/scaffolding-distance language, weight/confidence/provenance exposure, `graph_version` references, tension-log mechanism (`tension_log` table, `OQ-*` IDs).
  - **Surviving tokens**: concept names, domain-area names. Citation rules. Uncertainty posture.
  - **Worked example** showing the policy in operation against a stub learner-state input.
  - **Tension emission policy** (per ADR 0026): the `pattern_observed` writing constraint (third-person, descriptive-not-quotational, length-bounded, forbidden substantive-content categories). This is adjacent to but distinct from learner-facing rendering — Sonnet's writes to `tension_log` are read by Opus, not the learner, but the structural-not-substantive discipline applies.
- Cross-link `docs/pedagogy.md` → `AGENT_INSTRUCTIONS.md`.
- An ADR is warranted: the rendering policy is the prompt-layer contract for the teaching agent, with structural propagation to every Sonnet teaching session. Number ADR 0027 if accepted (ADR 0026 was taken by the privacy-posture insertion).

S-0008 success criteria: `AGENT_INSTRUCTIONS.md` exists at repo root with the forbidden/surviving token lists, citation rules, uncertainty posture, worked example, and tension-emission policy; `docs/pedagogy.md` cross-links to it; ADR 0027 lands as the rendering-policy contract; `tools/validate.py` returns clean.

After S-0008: Phase 1.3 (`confidence_level` column on node schema in `docs/architecture.md`) closes out Phase 1. The two open privacy questions (OQ-PRIVACY-A erasure mechanism, OQ-PRIVACY-B institutional regime) are decide-before-Phase 3 and need ADRs of their own before Phase 3 schema authoring begins — likely a session each. Sessions 12–14 of the prompt pack remain deferred (per `ROADMAP.md` §1.1).

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0007 close, the active set includes 8 items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- OQ-PHASE8-A — Phase 8 evaluation baseline choice; decide at Phase 8 entry
- **OQ-PRIVACY-A** (added S-0007, per ADR 0026) — erasure mechanism (crypto-shredding vs hard-delete-with-cascade vs anonymize-and-aggregate); decide-before Phase 3
- **OQ-PRIVACY-B** (added S-0007, per ADR 0026) — institutional vs individual data regime, direction-neutral; column reservation Phase 3, policy specification Phase 8
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward (ADRs 0023–0024 added in S-0004 — engagement-depth aggregation, sub-signal storage shape; ADR 0025 added in S-0006 — historical maximum tracking; ADR 0026 added in S-0007 — privacy posture, structural-not-substantive). Total ADR count: 26.
