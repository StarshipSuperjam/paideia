# Business

> Operating-discipline framing for Paideia. Per [ADR 0035](../adr/0035-multi-platform-apple-expansion.md) (which supersedes [ADR 0032](../adr/0032-personal-project-disposition.md) by broadening commitment 1), Paideia is a personal project the builder ships to the Apple App Store at a cost-priced subscription on iPhone + iPad first-class plus Mac via Designed-for-iPad; the option to grow into an institutional product, a non-profit, a grant-funded organization, or an acquisition target is foreclosed *as a refusal, not a deferral* — including in the success case. This file names the operating shape, not a market plan. The pedagogical commitments live in [`MISSION.md`](MISSION.md); the architectural decisions live in [`adr/`](../adr/).

## Personal Project Disposition

**Substantially revised: 2026-04-30 (S-0012 — supersedes the prior commercial-sustainability framing per [ADR 0032](../adr/0032-personal-project-disposition.md)). Commitment 1 broadened: 2026-04-30 (S-0015 — per [ADR 0035](../adr/0035-multi-platform-apple-expansion.md), which supersedes [ADR 0032](../adr/0032-personal-project-disposition.md) by broadening commitment 1 to iPhone + iPad first-class plus Mac via Designed-for-iPad while restating commitments 2–6 verbatim.)**

Paideia is a personal project. The builder maintains it because the pedagogy is worth maintaining; the project ships to other people via an Apple App Store cost-priced subscription because making it usable to the builder *cold* (per the success criterion below) requires that it be made usable, and once usable there is no pedagogical reason to refuse a small number of paying users who pass the discipline of the App Store's review and refund window.

Six commitments are binding (full text and reasoning in [ADR 0035](../adr/0035-multi-platform-apple-expansion.md), which supersedes [ADR 0032](../adr/0032-personal-project-disposition.md); commitments 2–6 restate verbatim from ADR 0032):

1. **Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish.** No Android, no web app, no native AppKit/Catalyst Mac app. The DeepTutor fork (per [`infrastructure.md`](infrastructure.md)) is consulted only for what serves the Apple-native target.
2. **Cost-priced subscription via Apple In-App Purchase. No free tier.** Target $12.99/mo monthly with an annual subscription option at the typical 15–20% discount. Apple's Small Business Program (15% take rate under $1M annual revenue) is presumed.
3. **Builder eats API costs within a fixed annual operating subsidy budget. No grants, no 501(c)(3), no institutional licensing.**
4. **No bring-your-own-key, neither consumer nor institutional. No institutional regime.** OQ-BYOK-REGIME closes by foreclosure in [ADR 0032](../adr/0032-personal-project-disposition.md).
5. **Cost ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) reframes** as a fixed annual operating subsidy budget — nothing ever raises it. Mechanism unchanged; justification structure changed (subsidy budget, not bridge-to-grants).
6. **Polish is static, never dynamic. Maintenance is minimum-shape, deliberately.** No social, sharing, leaderboards, streaks, push notifications beyond auth/billing, community, in-app messaging. The builder is not a customer service department — FAQ-only support, release cadence at builder discretion.

The success criterion is **"an app I would pay for if it weren't mine."** Self-applying. The builder-bias failure mode (knowing how the system works obscures whether the system is usable cold) is what keeps [ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md) (freshman defaults) and [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) (rendering policy worked example) load-bearing — they protect against builder-bias drift, not just against pedagogical drift or market-fit drift. The Phase 9 small-cohort cold-test (2–3 people who haven't seen the project, given the TestFlight build with no instructions) is the verification artifact, not an ongoing program.

The refusal-not-deferral commitment is binding *in the success case*: **if this scales beyond what the personal subsidy budget supports, the response is to raise prices to slow growth or to cap signups, not to pursue institutional clients, grants, or acquisition.** Reopening requires a superseding ADR; per-session re-litigation is not authorized.

## Pricing and Distribution

**Added: 2026-04-30 (S-0012). Distribution row amended: 2026-04-30 (S-0015) per [ADR 0035](../adr/0035-multi-platform-apple-expansion.md).**

| Surface | Value |
|---|---|
| Distribution | Apple App Store. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. Not sideload, not TestFlight-only at steady state. No Android, no web app, no native AppKit/Catalyst Mac app. |
| Pricing model | Cost-priced subscription via Apple In-App Purchase. No free tier. |
| Monthly | Target $12.99/mo. |
| Annual | ~15–20% discount on the monthly equivalent (Apple App Store standard). |
| Take rate | Apple Small Business Program (15%) presumed under $1M annual revenue. |
| Trial affordance | App Store screenshots + the 7-day Apple refund window. **A separate free-tier UX is not engineered** — a free tier is the canonical builder-funnel-mechanic foreclosed by [ADR 0032](../adr/0032-personal-project-disposition.md). |
| BYOK | Foreclosed (neither consumer nor institutional). |
| Pricing language | Learning-meaningful, not vendor-SKU-meaningful. Vendor model choices (which tier of Sonnet, when Opus runs) are internal optimization, not pricing surface. |
| Apple Developer Program | $99/year. Phase 8 forcing function (2–4 week enrollment lead time per [`ROADMAP.md`](../ROADMAP.md)). |

Tiering by learning intensity is foreclosed at this disposition's scale — the no-funnel-mechanic discipline (per [ADR 0032](../adr/0032-personal-project-disposition.md) commitment 2) is structurally incompatible with a free-tier-vs-paid-tier ladder. If a future session proposes tiering, the proposal must supersede [ADR 0032](../adr/0032-personal-project-disposition.md).

## Operating Cost Model

**Revised: 2026-04-30 (S-0012 — reframed from Personal-Use Cost Estimates and the prior 10k-user steady-state framing)**

The operating cost surface has two parts: the fixed annual infrastructure floor (paid by the builder regardless of user count) and the marginal per-user API cost (recovered at the price point's design margin from each subscriber).

**Annual infrastructure floor (~$300/year):**

- Apple Developer Program: $99/year.
- Small VPS / managed platform: $5–15/month (~$60–180/year). Lightweight requirements; single-instance scale.
- Domain registration: ~$15/year.
- Total floor: **order of $300/year**, paid by the builder. The numeric value is private operational configuration consistent with [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md)'s discipline; the order-of-magnitude is named here for design context.

**Marginal per-user API cost:**

- Sonnet 4.6 at standard rates ($3 input / $15 output per million tokens): ~$5–7/month for a typical engaged user (3–5 books/month). With prompt caching on system prompts and learner state (90% reduction on repeated context per Anthropic's prompt-cache surface), drops to ~$3–4/month.
- The $12.99/mo subscription's design margin is set against this per-user API shape; paid users cover their own marginal API.
- The per-user cost-cap mechanism (per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md)) is the structural bound on the cost-recovery model — a power user who would burn $20/month of API at $12.99/mo of revenue trips the soft-wall ladder before the loss exceeds the ceiling.

The "10,000-user steady-state operating cost" framing in the prior version of this document is dropped per [ADR 0032](../adr/0032-personal-project-disposition.md). The personal-project disposition does not target 10,000 users; if growth approached that scale, the response is the [ADR 0032](../adr/0032-personal-project-disposition.md) refusal-not-deferral commitment (raise prices, cap signups), not a different operating model.

## Annual Operating Subsidy Budget

**Revised: 2026-04-30 (S-0012 — reframed from Personal Financial Risk Ceiling per [ADR 0032](../adr/0032-personal-project-disposition.md))**

The cost ceiling is a fixed annual operating subsidy budget the builder commits in advance and does not exceed. The numeric ceiling and the cost-cap mechanism's parameters remain private operational configuration consistent with [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md). The principle the value implements is reframed:

- Original framing ([ADR 0029](../adr/0029-personal-financial-cost-ceiling.md), pre-S-0012): bridge-to-grants. The ceiling protected the builder until a grant landed, after which it could be raised.
- Current framing ([ADR 0032](../adr/0032-personal-project-disposition.md), S-0012 supersession): fixed annual operating subsidy budget. **Nothing ever raises it.** If usage growth would push spend past the budget, the response is to raise prices to slow growth, cap signups, or pause the App Store listing — never to pursue institutional clients, grants, or acquisition.

The mechanism is unchanged: per-user spend ceiling, aggregate-system spend ceiling, real-time spend telemetry, defined behavior at the cap (per OQ-WALL-BEHAVIOR in [`tensions.md`](tensions.md), now simplified to a single-tier ladder under the cost-priced subscription model). Soft walls degrade rather than terminate (Opus → Sonnet, deeper retrieval → shallower, two-hop neighborhood → one-hop) so concept-engagement integrity (per [`session-lifecycle.md`](session-lifecycle.md)) is preserved within the cap.

The trade is deliberate and binding: the system will reject some users at the soft wall who would have been profitable at scale, and will downshift quality for some users who would have benefited from the higher tier. Both are acceptable costs of bounded personal exposure under a refusal-not-deferral disposition.

## Cost Amplification with Session Length

**Added: 2026-04-29 (S-0008) — unchanged at S-0012 (still load-bearing for OQ-CONTEXT-COMPRESSION at Phase 7, regardless of disposition)**

Per-turn cost compounds with session length when the per-turn context grows turn-over-turn. The naive shape — load all prior turns into each subsequent turn's context — produces quadratic token growth in a single concept engagement. With concept engagements explicitly designed as "one continuous conversational thread, possibly spanning days" (per [`session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit), the naive shape would burn cost rapidly on the kind of deep, sustained engagement Paideia is built for.

The mitigation surface has three candidates: (a) **structured-state replacement** — instead of loading full prior turns, load the structured learner state and the most recent few turns, relying on the persistent event stream and `mastery_snapshots` for cross-session continuity (this matches [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript non-persistence commitment); (b) **automatic context compression** at platform-supported windows (Anthropic's prompt-caching surface mediates some of this transparently for the system-prompt portion; the dynamic per-turn portion remains the engineering surface); (c) **explicit per-turn summarization** — the agent summarizes the conversation-so-far into a structured note that replaces older raw turns. The choice has real quality-vs-cost stakes — aggressive compression loses subtle conversational state that affects pedagogical mode classification.

The specific strategy is open and tracked in [`tensions.md`](tensions.md) as **OQ-CONTEXT-COMPRESSION**, decide-before Phase 7 (the Sonnet teaching prototype is the first phase that produces multi-turn teaching-cost data; Phase 5 seed-graph generation is API-driven but not multi-turn). The combination of (a) and (c) appears most consistent with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and the bounded-context discipline in [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), but the trade space has not been argued through. The cost ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) is the upper-bound forcing function: a strategy that cannot keep typical concept-engagement cost inside the per-user cap is not deployable.

## Cancellation Discipline and Account Continuity

**Revised: 2026-04-30 (S-0012 — replaces the prior Account Ownership and Transfer Path framing; non-profit / acquisition transfer paths foreclosed by [ADR 0032](../adr/0032-personal-project-disposition.md))**

Per [ADR 0032](../adr/0032-personal-project-disposition.md) commitment 6, the project may be paused or cancelled at any point. The architecture preserves user data exportability so cancellation is honest, not destructive — the **data-export affordance** is a Phase 9 success criterion, sibling to the **delete-account affordance** that satisfies Apple App Store guideline 5.1.1 wired to [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md)'s cascade. Both surfaces are first-class UI primitives; both are required for Phase 9 close.

Operating accounts (GitHub, Supabase, Vercel, Anthropic) remain under personal accounts. The Anthropic API has no transfer mechanism — it's a key rotation, taking minutes. If the project is cancelled, the operational state can be exported, the App Store listing pulled, and the Anthropic key rotated — no successor entity is presumed. The Apple Developer Program enrollment lapses if not renewed annually; this is acceptable under the cancellation discipline.

The privacy *posture* (what kinds of data persist at all) is settled in [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and the erasure mechanism in [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md). The privacy *policy* (the ToS-adjacent legal document) is Phase 8 work pinned to Apple App Store submission per [ROADMAP.md](../ROADMAP.md) Phase 8 success criteria. Both reflect the consumer-individual data regime per [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md); no institutional-cohort or DPA framing.

---
*Last updated: 2026-04-30 (S-0015 — Personal Project Disposition commitment 1 broadened per [ADR 0035](../adr/0035-multi-platform-apple-expansion.md), which supersedes [ADR 0032](../adr/0032-personal-project-disposition.md); Pricing and Distribution Distribution row amended to "Apple App Store. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad…"; introductory blockquote and disposition-paragraph cross-link updated to ADR 0035 as the active contract; commitments 2–6 unchanged in substance and continue to reference ADR 0032 inline where they cite the historical commitment text. Prior update: 2026-04-30 (S-0012 — substantially rewritten per [ADR 0032](../adr/0032-personal-project-disposition.md). Dropped sections — now superseded: Market Reality (10k-user analysis), Cost Model at 10k users, Seasonal Cost Profile, Grant Opportunities, Retention Paradox, Revenue Mechanisms (Explored), Acquisition as Exit Path: Khan Academy, Audience vs. Market: Community College, Non-Profit Incorporation, Syllabus Upload as Institutional Wedge, Generative Graph Independence (moat-for-acquisition framing). Reframed: Personal Financial Risk Ceiling → Annual Operating Subsidy Budget, Personal-Use Cost Estimates → Operating Cost Model, Standing Disposition → Personal Project Disposition. Added: Pricing and Distribution. Cost Amplification with Session Length retained verbatim from S-0008 — load-bearing for OQ-CONTEXT-COMPRESSION at Phase 7. Cancellation Discipline and Account Continuity replaces the prior Account Ownership and Transfer Path section.)*
