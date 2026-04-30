# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012**; §1.1 closed across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 closed at S-0008; Phase 4.5 input-dataset-survey scaffolding landed at S-0009; §1.3 closed at S-0010; privacy ADRs collapsed at S-0011 (ADR 0031); project-direction supersession landed at S-0012 (ADR 0032 supersedes ADR 0002). **Phase 1.5 — Mission Realignment Overhaul** opened at S-0013 ([ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md)) and continues. **Phase 1.5.2 closed at S-0014** with [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) (Discovery / Planning / Engagement triad as primary product structure) and substantial rewrites of [`docs/ui-architecture.md`](docs/ui-architecture.md) and [`docs/session-lifecycle.md`](docs/session-lifecycle.md) against the triad. Phase 1.5 spans S-0013 → S-0016 and is realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **Phase 2 (Build Plan Scaffolding) defers to S-0017** so the per-phase chunks consume the realigned contract. |
| **Last build session** | S-0014 (2026-04-30) — Phase 1.5.2 closes. **[ADR 0034](adr/0034-discovery-planning-engagement-triad.md)** commits the Discovery / Planning / Engagement triad as primary product structure, replacing the globe-as-home-screen + concept-engagement-surface architecture retired by [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md). Three surfaces, one each for the three structurally distinct problems the structured-guidance value claim answers: **Discovery** (figuring out what to learn at all — dual-path: AI conversational onboarding bounded by [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md) + browseable concept catalog whose organization may consume [ADR 0018](adr/0018-flat-domain-tags-community-detection.md)'s community-detection algorithm; both first-class, neither a fallback for the other; both feed the same plan-generation pipeline downstream); **Planning** (knowing what to understand first — syllabus-as-plan, prerequisite gating, quiet completion markers, current/active syllabus view with the hard-cap-of-five preserved, mastered-concepts-in-syllabus-context, cross-syllabus convergence noting at routing-after-concept-completion); **Engagement** (knowing whether you have actually learned the thing — structurally inherited from [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md): three bounded contexts unchanged). Cross-domain edges remain first-class graph data per [ADR 0007](adr/0007-cross-domain-porosity.md); rendering convention is **bridge surfacing in context** (during planning, during engagement). Explicit foreclosures: no globe; no game-world rendering; no separate trophy surface; no library/bookshelf as a third primary surface; no mastery-glow / tendril / colored-trail visualization; no general chat surface (per [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md)). Two open-for-amendment-without-supersession items: library/bookshelf surface (Phase 9 cold-test path); discovery dual-path narrowing (Phase 9 cold-test path). **`docs/ui-architecture.md` substantially rewritten** — Globe Navigation Model and Level-of-Detail Rendering sections dropped wholesale; new Discovery Surface, Planning Surface, Engagement Surface sections; cross-surface concerns documented (mastery state single-source-of-truth, secondary surfaces enumerated, render-readiness contract per [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) applies across all surfaces). **`docs/session-lifecycle.md` substantially rewritten** — Globe as Home Screen dropped wholesale; trophy/glow/tendril reward framing stripped from Mastery Verification ("mastery glow activates and tendrils appear" → "the syllabus marks the concept as mastered; cross-domain bridges surface contextually in subsequent engagement"); Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, organic-verification framing per [ADR 0013](adr/0013-mastery-verification-organic-escalation.md), and Concurrent Syllabus Limit (hard cap of five) all preserved; new Entry Surfaces and Exit and Return subsections added. **`adr/README.md`** — Phase 1.5 — Mission Realignment table extended with ADR 0034 row; orientation paragraph updated. ADR count after S-0014: 34 ADRs total — 33 Accepted plus 1 Superseded. MemPalace decision drawer for ADR 0034 filed: `drawer_paideia_general_b0bf9b7cc2e14fe97e6fd515`. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0015 — Phase 1.5.3: Multi-platform Apple expansion + Phase 9 rewrite** *(continues Phase 1.5 per ROADMAP.md; consumes the triad committed by S-0014's [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) and supersedes [ADR 0032](adr/0032-personal-project-disposition.md) by broadening commitment 1.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (34 ADRs after S-0014 — 33 Accepted + 1 Superseded) is the contract layer. [ADR 0032](adr/0032-personal-project-disposition.md) (the supersession target) and [ADR 0034](adr/0034-discovery-planning-engagement-triad.md) (the just-landed triad whose surfaces Phase 9 implements) are the load-bearing inputs.

S-0015 authors **ADR 0035 — Multi-platform Apple expansion**, supersedes [ADR 0032](adr/0032-personal-project-disposition.md), substantially rewrites [ROADMAP.md](ROADMAP.md) Phase 9 success criteria against the triad + multi-platform, and amends [`docs/business.md`](docs/business.md) Pricing and Distribution.

ADR 0035 broadens commitment 1 from single-platform iOS to *Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish (Mac-idiom keyboard shortcuts, menu bar items, window resize handling). No Android, no web app, no native AppKit/Catalyst Mac app.* The justification: the editorial / typographic / library-shaped product structure that follows from the globe drop works best when larger screens do the heavy work and the phone is a follow-up surface; serious philosophy reading benefits from iPad screen real estate; "Designed for iPad on Mac" is essentially free distribution (Apple Silicon Macs run iPad apps from the App Store by default unless the developer opts out).

Commitments 2–6 from [ADR 0032](adr/0032-personal-project-disposition.md) are restated verbatim or by direct cross-reference: cost-priced subscription via Apple In-App Purchase with no free tier; builder eats API costs within a fixed annual operating subsidy budget; no BYOK / no institutional regime; [ADR 0029](adr/0029-personal-financial-cost-ceiling.md) cost ceiling reframed as fixed annual operating subsidy budget — nothing ever raises it; polish is static, never dynamic, maintenance is minimum-shape (no social, sharing, leaderboards, streaks, push notifications beyond auth/billing, community, in-app messaging). The disposition spirit is preserved while the platform scope broadens.

The supersession discipline applies: a future session proposing Android, web, or native AppKit Mac must supersede ADR 0035.

Substantial rewrite of [ROADMAP.md](ROADMAP.md) Phase 9 success criteria:

- Replace globe-as-home-screen + concept-engagement-surface with the **Discovery / Planning / Engagement triad** per [ADR 0034](adr/0034-discovery-planning-engagement-triad.md)
- Restate platform target as iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad
- Drop "iOS/Android primary, web test surface" entirely (Android already foreclosed; web foreclosed)
- Preserve: cost-cap mechanism on production user-facing surface (per [ADR 0029](adr/0029-personal-financial-cost-ceiling.md)), no general chat surface (per [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md)), exit affordance as first-class UI primitive (per [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md)), delete-account affordance (per [ADR 0031](adr/0031-erasure-mechanism-and-individual-only-regime.md)), data-export affordance (per [ADR 0032](adr/0032-personal-project-disposition.md) commitment 6 inherited unchanged into ADR 0035)
- Preserve: static-polish discipline; dynamic-feature foreclosure

Amendment to [`docs/business.md`](docs/business.md) Pricing and Distribution:

- Distribution row becomes: "Apple App Store. iPhone + iPad first-class; Mac via Designed-for-iPad."
- Apple Developer Program row unchanged ($99/yr)
- Other rows unchanged

Light revision to [`adr/0032-personal-project-disposition.md`](adr/0032-personal-project-disposition.md):

- `Status:` flipped from `Accepted` to `Superseded by ADR 0035`
- File preserved per ADR convention; supersession does not delete

S-0015 also files a MemPalace `decision`-tagged drawer for ADR 0035 (verbatim conversational reasoning per the two-layer decision-recording discipline in CLAUDE.md), updates `adr/README.md` (Phase 1.5 table extended with ADR 0035; ADR 0032 row updated to show `Superseded by [ADR 0035]`; orientation paragraph updated), and adds CHANGELOG entries under `[Unreleased]`.

### Source documents (read at S-0015 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — **Phase 1.5.3** subsection (this session's scope); **Phase 9** success criteria (rewrite target).
- [`adr/0032-personal-project-disposition.md`](adr/0032-personal-project-disposition.md) — supersession target; commitments 2–6 to restate.
- [`adr/0034-discovery-planning-engagement-triad.md`](adr/0034-discovery-planning-engagement-triad.md) — the just-landed triad whose surfaces Phase 9 implements.
- [`adr/0033-mission-realignment-structured-guidance-for-self-learners.md`](adr/0033-mission-realignment-structured-guidance-for-self-learners.md) — names ADR 0035 as the platform-scope supersession at S-0015 in its Consequences.
- [`adr/0029-personal-financial-cost-ceiling.md`](adr/0029-personal-financial-cost-ceiling.md) — cost ceiling mechanism preserved; reframed as fixed annual operating subsidy budget by ADR 0035 (inherited from ADR 0032's S-0012 reframe).
- [`adr/0028-input-side-scope-structural-not-prompt.md`](adr/0028-input-side-scope-structural-not-prompt.md), [`adr/0031-erasure-mechanism-and-individual-only-regime.md`](adr/0031-erasure-mechanism-and-individual-only-regime.md) — Phase 9 success-criteria commitments preserved (exit affordance, delete-account, no-general-chat).
- [`docs/business.md`](docs/business.md) — Pricing and Distribution amendment target.
- [`docs/operations/adr-authoring.md`](docs/operations/adr-authoring.md) — Nygard template; supersession discipline.
- [`/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md`](/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md) — the Phase 1.5 plan (local developer config; not a tracked project artifact); reference only, not load-bearing.

### Success criteria (S-0015)

- ADR 0035 lands at Status: Accepted; ADR 0032 Status flipped to `Superseded by ADR 0035`
- ADR 0035 restates commitments 2–6 verbatim or by direct cross-reference; commitment 1 broadened to iPhone + iPad first-class + Mac via Designed-for-iPad
- ROADMAP Phase 9 success criteria rewritten against triad + multi-platform; Android/web references gone; cost-cap, exit affordance, delete-account, data-export, no-general-chat all preserved
- `docs/business.md` Distribution row amended; other rows unchanged
- MemPalace `decision` drawer filed for ADR 0035
- `tools/validate.py` returns clean (0 hard-fails)
- STATE.md updated with S-0016 next-session work item (Phase 1.5.4 — rendering policy revision + secondary docs sweep)
- CHANGELOG entry under `[Unreleased]` for S-0015

### Estimated context budget (S-0015)

~50–60% (substantive ADR write with significant restatement; bounded ROADMAP and business.md revisions). Within the 60% target / 70% cap for substantive work per CLAUDE.md.

### After S-0015

S-0016 — **Phase 1.5.4: rendering policy revision + secondary docs sweep** — extends [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md)'s forbidden-token enumeration with globe / reward / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language, updates [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md), light-revises [ADR 0012](adr/0012-freshman-defaults-autodidact-ceiling.md) and [ADR 0014](adr/0014-sonnet-teaches-opus-reviews.md), sweeps ~10 secondary docs (`docs/pedagogy.md`, `docs/tensions.md`, `docs/architecture.md`, `docs/learner-model.md`, `docs/CROSS_REFERENCES.md`, `README.md`, `docs/prep-paideia-prompt-pack.md`, `docs/pedagogy/inferences.md`, `docs/infrastructure.md`) to drop residual references. Phase 1.5 closes at S-0016. Phase 2 (Build Plan Scaffolding) opens at S-0017 with the realigned contract as input.

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

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema); ADR 0031 added in S-0011 (erasure mechanism — hard-delete with cascade — and individual-only data regime); ADR 0032 added in S-0012 (personal project disposition; refusal-not-deferral commercial closure; supersedes ADR 0002). **ADR count after Phase 1: 32 ADRs total — 31 Accepted plus 1 Superseded** (ADR 0002 by ADR 0032). **Phase 1.5 grows the count further**: ADR 0033 added in S-0013 (mission realignment as structured guidance for self-learners; records globe / reward visual-system obsolescence as deliberate architectural removal); ADR 0034 added in S-0014 (Discovery / Planning / Engagement triad as primary product structure; replaces the globe-as-home-screen + concept-engagement-surface architecture). ADR count after S-0014: 34 ADRs total — 33 Accepted + 1 Superseded. Phase 1.5 will land ADR 0035 (S-0015, supersedes ADR 0032), bringing the post-Phase-1.5 total to 35 ADRs (33 Accepted + 2 Superseded).
