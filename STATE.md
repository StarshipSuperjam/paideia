# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012**; §1.1 closed across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 closed at S-0008; Phase 4.5 input-dataset-survey scaffolding landed at S-0009; §1.3 closed at S-0010; privacy ADRs collapsed at S-0011 (ADR 0031); project-direction supersession landed at S-0012 (ADR 0032 supersedes ADR 0002). **Phase 1.5 — Mission Realignment Overhaul opens at S-0013** with [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) (mission realignment as structured guidance for self-learners; records obsolescence of globe / mastery-glow / cross-domain-tendrils / trophy / "knowledge as a world" UI metaphor as deliberate architectural removal); light revision to [ADR 0018](adr/0018-flat-domain-tags-community-detection.md) (globe-rendering use case retired, algorithm survives as graph-analysis primitive); reframe of [`docs/MISSION.md`](docs/MISSION.md) What this is around the structured-guidance gap. Phase 1.5 spans S-0013 → S-0016 and is realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **Phase 2 (Build Plan Scaffolding) defers from S-0013 to S-0017** so the per-phase chunks consume the realigned contract. |
| **Last build session** | S-0013 (2026-04-30) — Phase 1.5 (Mission Realignment Overhaul) opens. **[ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md)** records the mission drift identified across the S-0008–S-0013 exploration arc: the globe / mastery-glow / cross-domain-tendrils / trophy / "knowledge as a world" UI metaphor was a UI-layer optimization that drifted attention away from the project's core value claim — *filling the gap a self-learner has when there is no teacher to open doors and show the way.* Diagnosis: form (spatial-traversal UI with character-on-map framing, mastery glow, trophy framing) signals casual play / low stakes; content (phenomenology, advanced epistemology) demands contemplation / sustained attention / real difficulty; cold-test users absorb form before content; a casual-register form makes the contemplation-register content fight uphill on every concept engagement. Compounds with [ADR 0032](adr/0032-personal-project-disposition.md) commitment 6's foreclosure of social/sharing/leaderboards/streaks — globe + reward visualization pulls toward exactly the gamification ADR 0032 forecloses, even when those mechanics are absent in code. ADR 0033 records deliberate architectural removal (not deferral); names what survives intact (graph + instructor + BYOB + mastery model + privacy + cost ceiling + bounded engagement contexts + ADR 0032 commitments 2–6); names the cascade of paired artifacts (ADR 0034 Discovery / Planning / Engagement triad at S-0014; ADR 0035 multi-platform Apple expansion superseding ADR 0032 at S-0015; rendering policy ADR 0027 forbidden-token extension at S-0016). Operating-discipline ADR per the ADRs 0026/0029/0031/0032 precedent — does not rise to MISSION.md's strong-working-commitments list. **Light revision to [ADR 0018](adr/0018-flat-domain-tags-community-detection.md)**: globe-rendering use case retired with the globe; flat-domain-tags + community-detection algorithm survives as graph-analysis primitive (potential downstream consumers: Discovery surface concept-clustering for browseable catalog organization at S-0014, Planning-side syllabus organization heuristics, graph-quality audits per ADR 0016 Phase 4); storage shape unchanged; Status remains Accepted. **`docs/MISSION.md`** — What this is gains a new "The gap Paideia fills" subsection naming the structured-guidance gap as the core value claim, the three concrete problems a self-learner without a teacher faces, and the two novel-value mechanisms (graph + instructor) that address all three; "ships as personal project" framing moves under a new "Disposition" subhead; single-iOS-platform language survives as-is until S-0015 (when ADR 0035 multi-platform Apple expansion lands and rewrites it). **`ROADMAP.md`** — new Phase 1.5 section inserted between Phase 1 (closed) and Phase 2 (deferred to S-0017); names the four-session arc with sub-phase scopes and Phase 1.5 success criteria; references the Phase 1.5 plan at `/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md` (approved at S-0013 boot, local developer config). **`adr/README.md`** — orientation paragraph extended with Phase 1.5 arc; new Phase 1.5 — Mission Realignment table added with ADR 0033 row; Phase 1 ADR count clarified as "after Phase 1: 32" (Phase 1.5 grows the count further). MemPalace decision drawer for ADR 0033 filed: `drawer_paideia_general_43b28d4bbab2382f44196600`. **Recovery from a silent drop recorded**: the Phase 1.5 plan was approved via plan-mode at S-0013 boot but the plan file landed at `/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md` (local developer config), not in tracked project artifacts; STATE.md still pointed S-0013 at Phase 2 per the S-0012-close handoff; the recovery (recording Phase 1.5 in ROADMAP.md / STATE.md / ADR 0033) is part of S-0013's scope; lesson: plan-mode artifacts do not propagate into the project's session protocol on their own. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0014 — Phase 1.5.2: Discovery / Planning / Engagement triad architecture** *(continues Phase 1.5 per ROADMAP.md; replaces the globe model committed by S-0013's [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) closure.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (33 ADRs after S-0013 — 32 Accepted + 1 Superseded) is the contract layer. [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) (just-landed mission realignment) is the rationale; ADR 0028 (input-side bounded engagement contexts, preserved unchanged) and ADR 0007 (cross-domain porosity, preserved as data) are the load-bearing constraints.

S-0014 authors **ADR 0034 — Discovery / Planning / Engagement triad as primary product structure** and substantially rewrites two foundational documents.

ADR 0034 commits the three-surface product structure that replaces the globe model:

- **Discovery surface** — dual-path entry. (a) Conversational onboarding ("tell me what interests you" → AI proposes targets and a plan). (b) Browseable concept catalog organized by domain/topic. Users with clear targets browse; users without clear targets converse. Both feed into the same plan-generation pipeline.
- **Planning surface** — syllabus-as-plan with prerequisite gating, current/active syllabus view (hard cap of five concurrent active syllabi survives from `docs/session-lifecycle.md`), quiet completion markers, mastered-concepts visible in the syllabus view (no separate trophy/library surface).
- **Engagement surface** — cross-references [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md) for the three bounded contexts (concept engagement, diagnostic, close reading); preserved unchanged. The engagement surface receives the user from the Planning surface; the exit affordance per ADR 0028 returns the user to graph navigation (now Discovery + Planning, not the globe).

Explicit foreclosures named in ADR 0034: no separate trophy surface; no globe; no game-world rendering; no library/bookshelf as a third primary surface (mastered concepts surface contextually within syllabi, not as a standalone trophy).

Substantial rewrite of [`docs/ui-architecture.md`](docs/ui-architecture.md):

- Drop **Globe Navigation Model** and **Level-of-Detail Rendering** sections wholesale (per ADR 0033 obsolescence)
- Author new sections: **Discovery Surface**, **Planning Surface**, **Engagement Surface** (the latter cross-references ADR 0028 for the bounded contexts; describes how the engagement surface receives the user from the Planning surface)
- Cross-domain edges remain first-class graph data (per ADR 0007); their UI rendering is **bridge surfacing in context** during engagement and planning (e.g., "this concept also appears on your path toward X" notes; "studying it advances both" hints; in-engagement surfacing of cross-domain prerequisites that have just become reachable), not visual tendrils on a globe

Substantial rewrite of [`docs/session-lifecycle.md`](docs/session-lifecycle.md):

- Drop **Globe as Home Screen** and the trophy/glow/tendrils framing in **Mastery Verification** (the "mastery glow activates and tendrils appear" reward language)
- Preserve: **Concept Engagement as Atomic Unit**, **Mode Transitions** (1→2→3 teaching modes), **Proficiency as Implied Transition**, **Routing After Concept Completion** (the "this concept also appears on your path toward X" cross-syllabus convergence noting), **Mastery Verification Through Downstream Teaching**'s organic-escalation framing per [ADR 0013](adr/0013-mastery-verification-organic-escalation.md). Concurrent Syllabus Limit (hard cap of five) survives.
- Replace the globe-reward language with: "the syllabus marks the concept as mastered; cross-domain bridges surface contextually in subsequent engagement"

S-0014 also files a MemPalace `decision`-tagged drawer for ADR 0034 (verbatim conversational reasoning per the two-layer decision-recording discipline in CLAUDE.md), updates `adr/README.md` with the ADR 0034 row, and adds CHANGELOG entries under `[Unreleased]`.

Whether the discovery-surface dual-path needs an ADR-level commitment to specific affordances (e.g., the conversational onboarding's prompt structure, the catalog's ordering algorithm, the search affordance) is a judgment call — if S-0014 surfaces tradeoffs that propagate into Phase 9 implementation, those land as additional ADRs (potentially in the 0036+ range) at S-0014 close or as deferred-to-Phase-9 tensions in `docs/tensions.md`.

### Source documents (read at S-0014 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — **Phase 1.5** section (the four-session arc); **Phase 1.5.2** subsection (this session's scope); Phase 9 success criteria (the implementation surface that consumes the triad).
- [`adr/0033-mission-realignment-structured-guidance-for-self-learners.md`](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) — the just-landed mission realignment; the rationale ADR 0034 builds on.
- [`adr/0028-input-side-scope-structural-not-prompt.md`](adr/0028-input-side-scope-structural-not-prompt.md) — the three bounded engagement contexts preserved unchanged; the Engagement-surface commitment is structurally inherited from this ADR.
- [`adr/0007-cross-domain-porosity.md`](adr/0007-cross-domain-porosity.md) — cross-domain edges remain first-class graph data; bridge-surfacing-in-context replaces tendril-visualization.
- [`adr/0013-mastery-verification-organic-escalation.md`](adr/0013-mastery-verification-organic-escalation.md) — organic verification preserved; only the visual-reward framing is stripped from `docs/session-lifecycle.md`.
- [`docs/ui-architecture.md`](docs/ui-architecture.md) — rewrite target.
- [`docs/session-lifecycle.md`](docs/session-lifecycle.md) — rewrite target.
- [`docs/architecture.md`](docs/architecture.md) — cross-references; the data-side cross-domain framing survives.
- [`/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md`](/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md) — the Phase 1.5 plan (local developer config; not a tracked project artifact); reference only, not load-bearing.

### Success criteria (S-0014)

- ADR 0034 lands at Status: Accepted with the three-surface structure named, the discovery-side dual-path (AI conversation + catalog) committed, and the planning-side prerequisite-gating + quiet-progress committed
- [`docs/ui-architecture.md`](docs/ui-architecture.md) rewritten end-to-end with no remaining globe/glow/tendril references; Globe Navigation Model and Level-of-Detail Rendering sections gone; Discovery / Planning / Engagement sections present
- [`docs/session-lifecycle.md`](docs/session-lifecycle.md) rewritten with concept-engagement atomic-unit framing and organic-verification framing preserved; reward-visual language stripped; Concurrent Syllabus Limit and Mode Transitions intact
- Cross-domain edges remain first-class graph data; bridge-surfacing happens contextually during planning/engagement, not as a tendril visualization
- MemPalace `decision` drawer filed for ADR 0034
- `tools/validate.py` returns clean (0 hard-fails)
- STATE.md updated with S-0015 next-session work item (Phase 1.5.3 — multi-platform Apple expansion + Phase 9 rewrite)
- CHANGELOG entry under `[Unreleased]` for S-0014

### Estimated context budget (S-0014)

~60–70% (substantive ADR write + two foundational doc rewrites). At the upper end of the substantive-work target per CLAUDE.md. If the budget approaches 70% mid-session, finish the ADR and one rewrite (ui-architecture.md), defer the session-lifecycle.md rewrite to S-0015 or S-0016 with a partial-close note in outcome_summary.

### After S-0014

S-0015 — **Phase 1.5.3: multi-platform Apple expansion + Phase 9 rewrite** — authors ADR 0035 superseding ADR 0032 in full (commitment 1 broadens to iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad; commitments 2–6 restated verbatim from ADR 0032), rewrites ROADMAP Phase 9 success criteria against the triad + multi-platform, amends `docs/business.md` Pricing and Distribution. S-0016 — **Phase 1.5.4: rendering policy revision + secondary docs sweep** — extends ADR 0027's forbidden-token enumeration with globe / reward / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language, updates AGENT_INSTRUCTIONS.md, light-revises ADRs 0012/0014, sweeps ~10 secondary docs to drop residual references. Phase 1.5 closes at S-0016. Phase 2 (Build Plan Scaffolding) opens at S-0017 with the realigned contract as input.

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

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema); ADR 0031 added in S-0011 (erasure mechanism — hard-delete with cascade — and individual-only data regime); ADR 0032 added in S-0012 (personal project disposition; refusal-not-deferral commercial closure; supersedes ADR 0002). **ADR count after Phase 1: 32 ADRs total — 31 Accepted plus 1 Superseded** (ADR 0002 by ADR 0032). **Phase 1.5 grows the count further**: ADR 0033 added in S-0013 (mission realignment as structured guidance for self-learners; records globe / reward visual-system obsolescence as deliberate architectural removal). ADR count after S-0013: 33 ADRs total — 32 Accepted + 1 Superseded. Phase 1.5 will land ADRs 0034 (S-0014) and 0035 (S-0015, supersedes ADR 0032), bringing the post-Phase-1.5 total to 35 ADRs (33 Accepted + 2 Superseded).
