# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012**; §1.1 closed across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 closed at S-0008; Phase 4.5 input-dataset-survey scaffolding landed at S-0009; §1.3 closed at S-0010; privacy ADRs collapsed at S-0011 (ADR 0031); project-direction supersession landed at S-0012 (ADR 0032 supersedes ADR 0002). **Phase 1.5 — Mission Realignment Overhaul** opened at S-0013 ([ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md)) and continues. **Phase 1.5.2 closed at S-0014** with [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) (Discovery / Planning / Engagement triad as primary product structure) and substantial rewrites of [`docs/ui-architecture.md`](docs/ui-architecture.md) and [`docs/session-lifecycle.md`](docs/session-lifecycle.md) against the triad. **Phase 1.5.3 closed at S-0015** with [ADR 0035](adr/0035-multi-platform-apple-expansion.md) (multi-platform Apple expansion superseding ADR 0032 by broadening commitment 1 to iPhone + iPad first-class via SwiftUI plus Mac via Designed-for-iPad; commitments 2–6 restate verbatim), substantial rewrite of [ROADMAP.md](ROADMAP.md) Phase 9 success criteria against the triad + multi-platform, and amendment of [`docs/business.md`](docs/business.md) Pricing and Distribution. Phase 1.5 spans S-0013 → S-0016 and is realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **Phase 2 (Build Plan Scaffolding) defers to S-0017** so the per-phase chunks consume the realigned contract. |
| **Last build session** | S-0015 (2026-04-30) — Phase 1.5.3 closes. **[ADR 0035](adr/0035-multi-platform-apple-expansion.md)** commits the multi-platform Apple expansion, **superseding [ADR 0032](adr/0032-personal-project-disposition.md) by broadening commitment 1** from single-platform iOS to *Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. No Android, no web app, no native AppKit/Catalyst Mac app.* Commitments 2–6 restate verbatim from [ADR 0032](adr/0032-personal-project-disposition.md): cost-priced subscription / no free tier; builder eats API costs within fixed annual operating subsidy budget; no BYOK / no institutional regime; [ADR 0029](adr/0029-personal-financial-cost-ceiling.md) reframed as fixed annual operating subsidy budget; static polish / minimum-shape maintenance. The reasoning chain that produced the broadening: the editorial / typographic / library-shaped product structure following from [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) / [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) works best when larger screens (iPad, Mac via Designed-for-iPad) do the heavy work; "Designed for iPad on Mac" is essentially free distribution (Apple Silicon Macs run iPad apps from the App Store by default unless the developer opts out). The disposition spirit survives the broadening intact: single-codebase / single-store / single-billing-path / single review queue / single privacy questionnaire / single refund window. Mac polish target is *modest, not Mac-native* — Mac-idiom keyboard shortcuts, menu bar items, window-resize handling, focus-ring / pointer-hover polish; full macOS idiom (multi-window state restoration, document-based architecture, custom menu bar beyond iPad-app default) out of scope and would require superseding [ADR 0035](adr/0035-multi-platform-apple-expansion.md). The corruption-vector identification carried by [ADR 0032](adr/0032-personal-project-disposition.md) ("leave the option open to expand later" was the seed pattern) survives in this ADR; refusal-not-deferral binding at the new boundary (Android, web, native AppKit/Catalyst Mac each foreclosed; reopening any one requires superseding [ADR 0035](adr/0035-multi-platform-apple-expansion.md)). Settles the Mac-via-Designed-for-iPad polish-depth question that [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) flagged as downstream of S-0015. **[ROADMAP.md](ROADMAP.md) Phase 9 success criteria substantially rewritten** — globe-as-home-screen + concept-engagement-surface framing replaced with Discovery / Planning / Engagement triad per [ADR 0034](adr/0034-discovery-planning-engagement-triad.md); platform target restated as iPhone + iPad first-class via SwiftUI plus Mac via Designed-for-iPad with modest polish; bridge-surfacing-in-context as the cross-domain rendering convention across all three surfaces; Android / web framing dropped entirely; cost-cap mechanism, exit affordance, delete-account, data-export, no-general-chat, static-polish discipline, dynamic-feature foreclosure all preserved; the "iOS/Android primary, web test surface" framing dropped. **[`docs/business.md`](docs/business.md) Pricing and Distribution Distribution row amended** — "Apple App Store. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. Not sideload, not TestFlight-only at steady state. No Android, no web app, no native AppKit/Catalyst Mac app." Other rows in the Pricing and Distribution table unchanged. Personal Project Disposition section's commitment 1 paragraph updated to broadened version; introductory blockquote and disposition cross-link updated from [ADR 0032](adr/0032-personal-project-disposition.md) to [ADR 0035](adr/0035-multi-platform-apple-expansion.md) as the active contract; commitments 2–6 paragraphs unchanged in substance. **[`adr/0032-personal-project-disposition.md`](adr/0032-personal-project-disposition.md)** — Status flipped from `Accepted` to `Superseded by [ADR 0035]`; supersession callout box added explaining the broadening as **supersession-by-narrowing-revision, not supersession-by-reversal** (five of six commitments restate verbatim; only commitment 1 broadens); historical reasoning preserved per the ADR README's supersession discipline (one-directional pointer; old file not deleted). **`adr/README.md`** — Phase 1.5 — Mission Realignment table extended with ADR 0035 row; ADR 0032 row in Phase 1 — Contract Lock table updated to `Superseded by [ADR 0035]`; orientation paragraph updated. ADR count after S-0015: **35 ADRs total — 33 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035). MemPalace decision drawer for ADR 0035 filed: `drawer_paideia_general_680ccb1932c659fc86c72938`. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0016 — Phase 1.5.4: Rendering policy revision + secondary docs sweep** *(closes Phase 1.5 per ROADMAP.md; consumes the realigned contract committed by S-0013 / S-0014 / S-0015. Phase 2 — Build Plan Scaffolding — opens at S-0017.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (35 ADRs after S-0015 — 33 Accepted + 2 Superseded) is the contract layer. [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) (forbidden-token contract; revision target), [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) (names this revision in its Consequences), and [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) (commits the bidirectional closure for which the forbidden-token revision is the voice-discipline half) are the load-bearing inputs.

S-0016 lands the **rendering-policy voice-discipline closure** that ADR 0033 named at its Consequences and ADR 0034 named at its Consequences as bidirectional with this revision. The surface around the agent does not invite globe / reward framing (the triad does not include those surfaces — closure committed at S-0014); the agent's voice does not reach for that framing (closure committed here at S-0016 via the forbidden-token contract). After S-0016 the closure is bidirectional and structurally enforced.

The revision targets are: a revision to [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md), a revision to [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md), light revisions to [ADR 0012](adr/0012-freshman-defaults-autodidact-ceiling.md) and [ADR 0014](adr/0014-sonnet-teaches-opus-reviews.md), and a sweep across ~10 secondary docs. Tension entries for globe / trophy land `Resolved: 2026-04-30` markers per the project's tension-resolution discipline (entries are not deleted; they are re-marked Resolved).

Revision to [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) — extends the forbidden-token enumeration to forbid globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language in agent output. The asymmetric-amendment discipline applies: this is an *addition* to the forbidden-token list, which is the cheap-amendment direction per [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md)'s own commitment. Status remains Accepted.

Revision to [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) — adds the new forbidden tokens to the forbidden-token enumeration; updates the worked example if it references any dropped concepts (globe, mastery glow, tendril, trophy, colored trail, "knowledge as a world"). The worked example is the gradeable test artifact for Phase 7 success criterion (zero forbidden-token leakage on 10 random concept queries).

Light revision to [ADR 0012](adr/0012-freshman-defaults-autodidact-ceiling.md) — strip residual market framing not removed by [ADR 0032](adr/0032-personal-project-disposition.md)'s S-0012 MISSION.md rewrite (the audience-vs-market framing is foreclosed; the ADR text may still reference it); name explicitly the freshman-defaults builder-bias-protection role per [ADR 0032](adr/0032-personal-project-disposition.md)'s Consequences (preserved unchanged through [ADR 0035](adr/0035-multi-platform-apple-expansion.md)). Status remains Accepted.

Light revision to [ADR 0014](adr/0014-sonnet-teaches-opus-reviews.md) — strip residual cohort framing if present (the institutional-cohort schema provisions retired at S-0012 may have left residual references in this ADR). Status remains Accepted.

Sweep across secondary docs — drop residual globe / mastery-glow / tendril / trophy / colored-trail / "knowledge as a world" / game-map / territory / spatial-traversal references in:

- [`docs/pedagogy.md`](docs/pedagogy.md)
- [`docs/tensions.md`](docs/tensions.md) — globe / trophy tension entries land `Resolved: 2026-04-30` markers (entries not deleted)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/learner-model.md`](docs/learner-model.md)
- [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md)
- [`README.md`](README.md)
- [`docs/prep-paideia-prompt-pack.md`](docs/prep-paideia-prompt-pack.md)
- [`docs/pedagogy/inferences.md`](docs/pedagogy/inferences.md)
- [`docs/infrastructure.md`](docs/infrastructure.md)

The sweep terminates when `git grep -i "globe\|mastery glow\|tendril\|trophy\|colored trail\|knowledge as a world\|Globe Navigation Model"` returns zero matches in tracked docs and ADRs except: ADR 0033 (names what's being dropped, by design), ADR 0027 (forbidden-token list, by design), ADR 0018 (revised text explaining algorithm-survives-without-globe, by design), ADR 0032 file (history, by design — superseded), ADR 0035 file (history reference, by design — supersedes ADR 0032), and `CHANGELOG.md` (history, by design).

S-0016 closes Phase 1.5. ADR count after S-0016: still 35 ADRs total (no new ADRs land at S-0016; the four light revisions update existing ADRs in place; the sweep updates non-ADR docs).

### Source documents (read at S-0016 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — **Phase 1.5.4** subsection (this session's scope).
- [`adr/0027-rendering-policy-prompt-layer-contract.md`](adr/0027-rendering-policy-prompt-layer-contract.md) — revision target (forbidden-token enumeration).
- [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) — revision target (mirrors ADR 0027 forbidden-token list; worked example may reference dropped concepts).
- [`adr/0033-mission-realignment-structured-guidance-for-self-learners.md`](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) — names this S-0016 revision in its Consequences.
- [`adr/0034-discovery-planning-engagement-triad.md`](adr/0034-discovery-planning-engagement-triad.md) — names this S-0016 revision in its Consequences as bidirectional with the surface-level closure.
- [`adr/0012-freshman-defaults-autodidact-ceiling.md`](adr/0012-freshman-defaults-autodidact-ceiling.md), [`adr/0014-sonnet-teaches-opus-reviews.md`](adr/0014-sonnet-teaches-opus-reviews.md) — light-revision targets.
- The ~10 secondary docs listed above — sweep targets.
- [`docs/operations/adr-authoring.md`](docs/operations/adr-authoring.md) — Nygard template; ADR-revision conventions (Status remains Accepted on additive revisions).
- [`/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md`](/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md) — the Phase 1.5 plan (local developer config; not a tracked project artifact); reference only, not load-bearing.

### Success criteria (S-0016)

- ADR 0027 forbidden-token enumeration extended with the new categories (globe / world / map / territory / exploration; reward / trophy / glow / mastery-visualization). Status remains Accepted.
- AGENT_INSTRUCTIONS.md mirrors ADR 0027's revised list; worked example free of dropped-concept references. Status of the worked example as a gradeable Phase 7 test artifact is preserved.
- ADR 0012 and ADR 0014 light-revised; Status remains Accepted on both.
- Secondary docs sweep complete; `git grep -i "globe\|mastery glow\|tendril\|trophy\|colored trail\|knowledge as a world\|Globe Navigation Model"` returns zero matches in tracked docs and ADRs except the by-design exceptions listed above.
- Tension entries for globe/trophy in [`docs/tensions.md`](docs/tensions.md) marked `Resolved: 2026-04-30`; entries not deleted.
- `tools/validate.py` returns clean (0 hard-fails).
- STATE.md updated with S-0017 next-session work item (Phase 2 — Build Plan Scaffolding opens; the realigned contract is input).
- CHANGELOG entry under `[Unreleased]` for S-0016.

### Estimated context budget (S-0016)

~60–70% (mechanical sweep across ~10 secondary docs is substantive in volume even if individual edits are small; ADR 0027 revision is the largest single edit). Within the 70% target / 80% cap for mechanical/procedural work per CLAUDE.md.

### After S-0016

**Phase 1.5 closes at S-0016. Phase 2 (Build Plan Scaffolding) opens at S-0017** with the realigned contract as input. S-0017 authors the `build_plan/` directory naming the chunked authoring sessions for Phases 3–9 plus the working contract for each session: `build_plan/MANIFEST.md` (orientation, session schedule, phase mapping), `build_plan/00_preamble.md` (orienting prose), `build_plan/00_session_schedule.md` (every session by ID with scope, source documents, output target, budget tier), `build_plan/P_0_contract_lock.md` (retroactive Phase 1 record incorporating the Phase 1.5 realignment), `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` (per-phase chunks). Per-phase chunks consume the triad ([ADR 0034](adr/0034-discovery-planning-engagement-triad.md)), the multi-platform Apple commitment ([ADR 0035](adr/0035-multi-platform-apple-expansion.md)), and the surviving pedagogical / privacy / cost-ceiling commitments unchanged.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0012 close, the active set is 8 items (OQ-PRIVACY-A and OQ-PRIVACY-B closed by ADR 0031; OQ-PHASE8-A settled by ADR 0032; OQ-BYOK-REGIME withdrawn by ADR 0032):

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- **OQ-WALL-BEHAVIOR** (added S-0008, per ADR 0029; simplified S-0012) — soft-wall degradation ladder at cost cap; **single-tier ladder** under cost-priced subscription model (free-vs-paid tier-shaped framing collapsed at S-0012); four candidate steps remain (model downshift, retrieval shrink, concept-engagement length cap, soft refusal); decide-before Phase 8 cost-cap wiring
- **OQ-CONTEXT-COMPRESSION** (added S-0008, per ADR 0029; unaffected by S-0012) — token-amplification mitigation for multi-turn engagements (structured-state replacement + automatic compression + explicit summarization candidates); decide-before Phase 7
- **OQ-PEDAGOGY-INFERENCE-LOCUS** (added S-0008, tagged `watch`) — rule layer vs. distributed inference; revisit when inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR an operational complaint surfaces
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs; commitment 2 reframed at S-0012 as "operating discipline must not corrupt pedagogy" per ADR 0032); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema); ADR 0031 added in S-0011 (erasure mechanism — hard-delete with cascade — and individual-only data regime); ADR 0032 added in S-0012 (personal project disposition; refusal-not-deferral commercial closure; supersedes ADR 0002). **ADR count after Phase 1: 32 ADRs total — 31 Accepted plus 1 Superseded** (ADR 0002 by ADR 0032). **Phase 1.5 grows the count further**: ADR 0033 added in S-0013 (mission realignment as structured guidance for self-learners; records globe / reward visual-system obsolescence as deliberate architectural removal); ADR 0034 added in S-0014 (Discovery / Planning / Engagement triad as primary product structure; replaces the globe-as-home-screen + concept-engagement-surface architecture); ADR 0035 added in S-0015 (multi-platform Apple expansion; supersedes ADR 0032 by broadening commitment 1 from single-platform iOS to iPhone + iPad first-class via SwiftUI plus Mac via Designed-for-iPad; commitments 2–6 restate verbatim). **ADR count after S-0015: 35 ADRs total — 33 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035). S-0016 lands no new ADRs (light revisions to ADRs 0012, 0014, 0027 in place; secondary docs sweep). Final post-Phase-1.5 total: 35 ADRs (33 Accepted + 2 Superseded).
