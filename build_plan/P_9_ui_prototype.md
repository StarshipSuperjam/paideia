# P_9 — UI prototype (Phase 9)

> The Discovery / Planning / Engagement triad surfaces, implemented as a single SwiftUI codebase shipping iPhone + iPad first-class plus Mac via Designed-for-iPad, distributed through the Apple App Store. Application code; ENGINE_LOG / ADR discipline does not apply (state-of-record-only). Normal git history.

## Phase scope

Phase 9 is the product-ship phase. Per [ROADMAP Phase 9](../ROADMAP.md), the deliverable is the Discovery / Planning / Engagement triad surfaces per [`product/docs/ui-architecture.md`](../product/docs/ui-architecture.md), implemented in SwiftUI for iPhone + iPad first-class plus Mac via Designed-for-iPad opt-in per [ADR 0035](../product/adr/0035-multi-platform-apple-expansion.md).

The DeepTutor fork (per [`product/docs/infrastructure.md`](../product/docs/infrastructure.md)) is consulted only for what serves the Apple-native target. No Android, no web client, no native AppKit/Catalyst Mac app.

This is the chunk where the engine-tracked discipline relaxes. **ENGINE_LOG and ADR discipline do not apply to application code** — git history is the trace. The discipline still applies to engine-side work that supports the UI (e.g., backend changes, schema updates), but the SwiftUI implementation lives in normal git history.

## Output

Per [ROADMAP Phase 9 success criteria](../ROADMAP.md), the triad surfaces and the supporting first-class UI primitives:

- **Discovery surface** — dual-path: AI conversational onboarding bounded by the purpose-not-topic discipline per [ADR 0028](../product/adr/0028-input-side-scope-structural-not-prompt.md), plus a browseable concept catalog whose organization may consume the flat-domain-tags + community-detection algorithm per [ADR 0018](../product/adr/0018-flat-domain-tags-community-detection.md).
- **Planning surface** — syllabus-as-plan with prerequisite gating; current/active syllabus view (hard-cap-of-five preserved per [`product/docs/session-lifecycle.md`](../product/docs/session-lifecycle.md)); quiet completion markers; mastered concepts visible in syllabus context (no separate trophy / library surface — foreclosed); cross-syllabus convergence noting at routing-after-concept-completion.
- **Engagement surface** — three bounded contexts inherited structurally per [ADR 0028](../product/adr/0028-input-side-scope-structural-not-prompt.md): concept engagement, diagnostic, BYOB close reading.
- **Bridge surfacing in context** — cross-domain edges surface contextually during planning ("studying this concept advances your path toward [other target] as well") and during engagement (callback references that bridge between domains). No standalone cross-domain visualization surface; no globe; no game-world rendering; no mastery-glow / tendril / colored-trail visualization per [ADR 0033](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md).
- **Exit affordance** — first-class UI primitive; single visible control reachable in one action from any concept-engagement / diagnostic / close-reading surface.
- **Delete-account affordance** — first-class UI primitive wired to the `ON DELETE CASCADE` discipline per [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md); satisfies Apple App Store guideline 5.1.1.
- **Data-export affordance** — first-class UI primitive; preserves cancellation-discipline honesty per [`product/docs/business.md`](../product/docs/business.md).
- **Cost-cap mechanism** operates against the production user-facing surface, not just the [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) harness.
- **No "general chat" surface** — free-form input only inside the three bounded contexts and within the Discovery surface's bounded AI conversational onboarding.
- **Static polish only** — visual design, typography, animation, copy quality, layout, iconography, sound design, haptics. Mac-via-Designed-for-iPad polish pass is consistent. Dynamic-feature surfaces foreclosed.
- **No primary surface outside the triad** — secondary surfaces (settings, account, billing, parked-syllabus list, user library) accessed from menus.
- App Store submission completes; v1.0.0 release.

## Success criteria

The full success-criteria block lives in [ROADMAP Phase 9](../ROADMAP.md). The chunk does not duplicate it; the chunk's responsibility is to verify each criterion holds at session close and record verification in `outcome_summary` (per session — Phase 9 spans many sessions).

Phase 9 closes when the v1.0.0 build ships to the Apple App Store and a `CHANGELOG.md` entry under v1.0.0 lands per the [reservation](../product/CHANGELOG.md). The first `CHANGELOG.md` entry is the Phase 9 close artifact; the file's reserved-stub preamble is replaced with the Keep-a-Changelog format and the v1.0.0 entry.

## Source documents (boot reads beyond CLAUDE.md auto-load)

Per session within Phase 9 (the boot read is selective; not every session needs every doc):

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 9.
- [`product/docs/ui-architecture.md`](../product/docs/ui-architecture.md) — the triad surface design.
- [`product/docs/session-lifecycle.md`](../product/docs/session-lifecycle.md) — concept engagement, mode transitions, mastery verification, hard-cap-of-five.
- [`product/docs/infrastructure.md`](../product/docs/infrastructure.md) — DeepTutor fork.
- [`product/AGENT_INSTRUCTIONS.md`](../product/AGENT_INSTRUCTIONS.md) — teaching prompt (the engagement surface is the consumer).
- [`product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md`](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [`product/adr/0034-discovery-planning-engagement-triad.md`](../product/adr/0034-discovery-planning-engagement-triad.md), [`product/adr/0035-multi-platform-apple-expansion.md`](../product/adr/0035-multi-platform-apple-expansion.md).
- [`product/CHANGELOG.md`](../product/CHANGELOG.md) — the reservation; v1.0.0 entry lands here at Phase 9 close.

## Load-bearing ADRs

[ADR 0007](../product/adr/0007-cross-domain-porosity.md), [ADR 0011](../product/adr/0011-no-hosted-copyrighted-material.md), [ADR 0018](../product/adr/0018-flat-domain-tags-community-detection.md), [ADR 0027](../product/adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0028](../product/adr/0028-input-side-scope-structural-not-prompt.md), [ADR 0029](../product/adr/0029-personal-financial-cost-ceiling.md), [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0033](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](../product/adr/0034-discovery-planning-engagement-triad.md), [ADR 0035](../product/adr/0035-multi-platform-apple-expansion.md).

## Estimated context budget

Mixed across sessions. UI authoring is iterative — most Phase 9 sessions are app-code sessions, normal git history, no engine discipline. Substantive moments (e.g., `OQ-WATCH-FLAG-FILE` settling, the open-for-amendment-without-supersession items in [ROADMAP Phase 9](../ROADMAP.md) that may consume cold-test evidence) warrant the substantive tier; UI-implementation sessions warrant the mechanical tier.

## Session sequencing

Multi-session — many sessions. The chunk is more of a phase-arc record than a per-session contract. Per-session boundaries are settled session-by-session as work progresses; STATE.md tracks the next session.

Natural session families:

- **Foundation** — SwiftUI project scaffolding, navigation, theme, design system.
- **Discovery surface** — concept catalog browser, AI onboarding flow.
- **Planning surface** — syllabus view, prerequisite gating, completion markers, cross-syllabus convergence noting.
- **Engagement surface** — concept engagement, diagnostic, BYOB close reading; consumes the [`P_7_teaching_layer.md`](P_7_teaching_layer.md) endpoint.
- **System surfaces** — settings, account, billing, delete-account, data-export.
- **Polish** — typography, animation, copy quality, iconography, haptics, Mac-via-Designed-for-iPad polish pass.
- **App Store submission** — TestFlight regression run, App Store binary submission, review iteration if rejected.
- **Release** — v1.0.0 ship; first `CHANGELOG.md` entry replaces the reserved-stub preamble.

## Open tensions consumed

- May surface concrete need that resolves the `OQ-WATCH-FLAG-FILE` watch entry per [`product/docs/tensions.md`](../product/docs/tensions.md).
- May surface concrete need that opens an amendment to [ADR 0034](../product/adr/0034-discovery-planning-engagement-triad.md) for the library/bookshelf surface or the discovery dual-path narrowing (the two open-for-amendment-without-supersession items in [ROADMAP Phase 9](../ROADMAP.md)).

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 9 — full phase scope and success criteria.
- [`product/docs/ui-architecture.md`](../product/docs/ui-architecture.md) — triad surface design.
- [`product/docs/session-lifecycle.md`](../product/docs/session-lifecycle.md) — concept engagement, mode transitions, mastery verification.
- [`../adr/0034-discovery-planning-engagement-triad.md`](../product/adr/0034-discovery-planning-engagement-triad.md), [`../adr/0035-multi-platform-apple-expansion.md`](../product/adr/0035-multi-platform-apple-expansion.md).
- [`product/CHANGELOG.md`](../product/CHANGELOG.md) — the reserved product release log; first entry at Phase 9 close.
