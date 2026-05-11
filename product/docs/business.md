# Business

> Operating-discipline framing for Paideia. Paideia is an open-source personal project the builder maintains. Source is Apache 2.0; the official Apple App Store binary ships under the maintainer's personal Apple Developer account, free-download-with-IAP-unlock, with the user supplying their own Anthropic API key (BYOK). The option to grow into an institutional product, a non-profit, a grant-funded organization, or an acquisition target is foreclosed *as a refusal, not a deferral* — including in the success case. This file names the operating shape, not a market plan. The pedagogical commitments live in [`MISSION.md`](MISSION.md); the architectural decisions live in [`adr/`](../adr/).

## Personal Project Disposition

Paideia is an open-source personal project. The builder maintains it because the pedagogy is worth maintaining. The official Apple App Store binary ships under the maintainer's personal Apple Developer account; the source is open under Apache 2.0 so the artifact survives the builder's eventual attention loss. Users supply their own Anthropic API key — the app guides them through obtaining and entering it.

Eight commitments are binding:

1. **Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish.** No Android, no web app, no native AppKit/Catalyst Mac app. The DeepTutor fork (per [`infrastructure.md`](infrastructure.md)) is consulted only for what serves the Apple-native target.
2. **Free download with a one-time In-App Purchase unlock. No subscription.** Specific dollar amount deferred to Phase 8/9 implementation session. A free-tier-of-app (graph browse without key, sample syllabus from static fixture) is permitted as a structural affordance under BYOK — the free-tier must not be engineered as a conversion funnel. No streaks, no "unlock more" nudges, no engagement-time-on-free-tier metrics treated as optimization targets.
3. **Builder's operating subsidy is the fixed infrastructure floor (~$200–300/year), independent of user count. Users pay Anthropic directly for their own API usage.** There is no Paideia revenue path that recovers API cost. Should the IAP unlock generate revenue, it is for the app artifact — not for API-cost recovery.
4. **Consumer BYOK is the required regime. Institutional licensing, grants, and acquisition remain foreclosed.** Users supply their own Anthropic API key via an in-app onboarding flow that walks a non-technical user step by step through Anthropic account creation, console navigation, key generation, and key entry. The institutional-foreclosure half of the prior commitment 4 carries forward unchanged.
5. **Cost-ceiling mechanism retires under BYOK.** The user's own Anthropic billing console is the spend-cap surface. There is no Paideia-controlled per-user cap, no aggregated cap, no Paideia-side spend telemetry — Paideia is not in the API path. The pedagogical-degradation principle that the prior cost-ceiling protected (degrade rather than terminate mid-concept-engagement) survives as a teaching discipline absorbed into [`adr/0014-sonnet-teaches-opus-reviews.md`](../adr/0014-sonnet-teaches-opus-reviews.md)'s role split.
6. **Polish is static, never dynamic. Maintenance is minimum-shape, deliberately.** No social, sharing, leaderboards, streaks, push notifications beyond auth/billing, community, in-app messaging. The builder is not a customer service department — FAQ-only support, release cadence at builder discretion. Under OSS+BYOK the funnel-mechanic discipline binds against *user*-funnel-mechanic (engineering retention nudges that bait users into more API spend on their own dime) alongside the *builder*-funnel-mechanic concerns the prior framing identified — the same discipline answers both.
7. **Source is open under Apache 2.0. Copyright attribution to "The Paideia Project Contributors."** The official Apple App Store binary is maintained under the original maintainer's personal Apple Developer account. Forks are permitted under the license; forks distributing through the App Store are encouraged to rebrand to avoid user confusion. The de-facto controls against competing forks are App Store Connect ownership of the canonical listing plus the maintained domain pointer (paideia.app or equivalent). Trademark on "Paideia" is deferred-reactive — file only if a competing fork appears in the wild and gains traction.
8. **The user's Anthropic API key lives only on-device in iOS Keychain.** No Paideia-controlled server receives the key, proxies the API, or observes the API exchange. The key is stored with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` to prevent iCloud Keychain sync; it never appears in logs, crash reports, telemetry, or error traces. Apple App Privacy questionnaire answer for the API credential: "data not collected." Mastery computation continues server-side via structured `learner_events` derived client-side from prompt + response, consistent with the transcript-non-persistence guarantee per [`adr/0026-persistent-learner-storage-structural-not-substantive.md`](../adr/0026-persistent-learner-storage-structural-not-substantive.md).

The success criterion is **"an app I would pay for if it weren't mine."** Self-applying. The builder-bias failure mode (knowing how the system works obscures whether the system is usable cold) is what keeps freshman defaults and the rendering-policy worked example load-bearing — they protect against builder-bias drift, not just against pedagogical drift or market-fit drift. The Phase 9 small-cohort cold-test (2–3 people who haven't seen the project, given the TestFlight build with no instructions) is the verification artifact, not an ongoing program; the cold-test now also exercises the in-app BYOK onboarding flow.

The refusal-not-deferral commitment is binding *in the success case*: **if usage growth pushes user-funnel-mechanic pressure onto pedagogy, the response is to pause the App Store listing or restrict the free-tier affordances — never to pursue institutional clients, grants, or acquisition.** Reopening requires a superseding ADR; per-session re-litigation is not authorized.

### See also

- [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) — OSS pivot and BYOK disposition; supersedes [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) (cost ceiling) and [ADR 0035](../adr/0035-multi-platform-apple-expansion.md) (multi-platform Apple expansion). Full text and reasoning for the eight commitments.
- [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md) — Sonnet-teaches-Opus-reviews role split; absorbs the surviving pedagogical-degradation principle from the retired cost-ceiling mechanism.
- [ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md) — freshman-defaults calibration; one of the load-bearing protections against builder-bias drift; now also calibrates the in-app key-onboarding flow.
- [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) — rendering-policy worked example; the second load-bearing protection.
- [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) — erasure mechanism and individual-only data regime.

## Pricing and Distribution

| Surface | Value |
|---|---|
| Distribution | Apple App Store. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. Not sideload, not TestFlight-only at steady state. No Android, no web app, no native AppKit/Catalyst Mac app. |
| Pricing model | Free download. One-time In-App Purchase unlock. No subscription. No recurring billing. |
| IAP unlock dollar amount | TBD; deferred to Phase 8/9 implementation session. The right price point depends on the in-app key-onboarding UX burden (unknown until the onboarding flow is built and exercised) and on how the App Store cohort responds to "$x.xx for an app that requires an external service subscription" pricing. |
| Trial affordance | Free download with a structural free-tier affordance (graph browse, sample syllabus from static fixture); the IAP unlock gates full teaching-layer access. The free-tier must not be engineered as a conversion funnel — no streaks, no "unlock more" nudges, no engagement-time-on-free-tier as an optimization target. |
| BYOK | Consumer BYOK is the required regime. Institutional BYOK foreclosed. User's Anthropic key stored in iOS Keychain on-device with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`; never transits Paideia-controlled infrastructure. |
| Pricing language | Learning-meaningful, not vendor-SKU-meaningful. Vendor model choices (which tier of Sonnet, when Opus runs) are internal optimization, not pricing surface. |
| Apple Developer Program | $99/year. Phase 8 forcing function (2–4 week enrollment lead time per [`ROADMAP.md`](../../ROADMAP.md)). |

Tiering by learning intensity is foreclosed at this disposition's scale — the no-funnel-mechanic discipline (commitment 6) is structurally incompatible with a free-tier-vs-paid-tier ladder engineered for conversion. A proposal to tier must supersede the OSS+BYOK disposition contract.

## Infrastructure Operating Cost

The operating cost surface under OSS+BYOK is a single fixed annual infrastructure floor (~$200–300/year), independent of user count. Users pay Anthropic directly through their own accounts; Paideia is not in the API path and has no marginal per-user cost to recover.

- Apple Developer Program: $99/year.
- Supabase: free tier for mastery state at expected scale; minimal paid tier only if growth requires.
- Domain registration (paideia.app or equivalent): ~$15/year.
- Total floor: order of **$200–300/year**, paid by the builder. The infrastructure floor does not scale with user count — Supabase reads and writes for mastery state are negligible per user, and the Apple Developer Program floor is independent of installations.

There is no Paideia revenue path that recovers API cost — under BYOK there is no API cost for Paideia to recover. Should the IAP unlock per commitment 2 generate revenue, the revenue is for the app artifact (the developer's work building and maintaining the app), not for API-cost recovery.

## Cost Amplification with Session Length

Per-turn cost compounds with session length when the per-turn context grows turn-over-turn. The naive shape — load all prior turns into each subsequent turn's context — produces quadratic token growth in a single concept engagement. With concept engagements explicitly designed as "one continuous conversational thread, possibly spanning days" (per [`session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit), the naive shape would burn the user's own Anthropic bill rapidly on the kind of deep, sustained engagement Paideia is built for. The pedagogical-degradation discipline (downshift retrieval window, narrow two-hop neighborhood to one-hop) helps the user manage their own spend by preserving engagement integrity without runaway token growth — it is a teaching move that respects engagement integrity, not a Paideia-side cost protection.

The mitigation surface has three candidates: (a) **structured-state replacement** — instead of loading full prior turns, load the structured learner state and the most recent few turns, relying on the persistent event stream and `mastery_snapshots` for cross-session continuity (this matches [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript non-persistence commitment); (b) **automatic context compression** at platform-supported windows (Anthropic's prompt-caching surface mediates some of this transparently for the system-prompt portion; the dynamic per-turn portion remains the engineering surface); (c) **explicit per-turn summarization** — the agent summarizes the conversation-so-far into a structured note that replaces older raw turns. The choice has real quality-vs-cost stakes — aggressive compression loses subtle conversational state that affects pedagogical mode classification.

The specific strategy is open and tracked in [`tensions.md`](tensions.md) as **OQ-CONTEXT-COMPRESSION**, decide-before Phase 7 (the Sonnet teaching prototype is the first phase that produces multi-turn teaching-cost data; Phase 5 seed-graph generation is API-driven but not multi-turn). The combination of (a) and (c) appears most consistent with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and the bounded-context discipline in [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), but the trade space has not been argued through. The pedagogical-degradation discipline absorbed into [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md) per [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) is the qualitative guardrail: a strategy that mid-engagement terminates a concept engagement to manage per-turn token cost violates the atomic-unit-of-teaching commitment regardless of who pays.

## Cancellation Discipline and Account Continuity

The project may be paused or cancelled at any point (per commitment 6 of the personal-project disposition). The architecture preserves user data exportability so cancellation is honest, not destructive — the **data-export affordance** is a Phase 9 success criterion, sibling to the **delete-account affordance** that satisfies Apple App Store guideline 5.1.1 wired to the [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) cascade. Both surfaces are first-class UI primitives; both are required for Phase 9 close.

Under OSS+BYOK, cancellation of the App Store binary does not destroy the artifact — the OSS source remains available, and users with their own Anthropic key can be served by any fork that survives. The Apple Developer Program enrollment lapses if not renewed annually; this is acceptable under the cancellation discipline.

Operating accounts (GitHub, Supabase, Vercel for build tooling) remain under personal accounts. The Anthropic API account is the *user's*, not Paideia's — there is no Anthropic credential to transfer because there is no Paideia-held credential. If the project is cancelled, the operational state can be exported, the App Store listing pulled, and the GitHub repo continues to live as the open-source artifact.

The privacy *posture* (what kinds of data persist at all) is the consumer-individual data regime: persistent storage is structural, not substantive; the erasure mechanism is hard-delete with cascade; the user's API key never persists outside their device's Keychain. The privacy *policy* (the ToS-adjacent legal document) is Phase 8 work pinned to Apple App Store submission per [ROADMAP.md](../../ROADMAP.md) Phase 8 success criteria. No institutional-cohort or DPA framing.

### See also

- [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) — erasure mechanism (hard-delete with cascade) and individual-only data regime.
- [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) — persistent learner storage is structural, not substantive; the transcript-non-persistence guarantee that lets the server stay key-blind under BYOK.
- [ADR 0065](../adr/0065-oss-pivot-and-byok-disposition.md) — OSS pivot and BYOK disposition.
