# Business

> Operating-discipline framing for Paideia. Paideia is a personal project the builder ships to the Apple App Store at a cost-priced subscription on iPhone + iPad first-class plus Mac via Designed-for-iPad. The option to grow into an institutional product, a non-profit, a grant-funded organization, or an acquisition target is foreclosed *as a refusal, not a deferral* — including in the success case. This file names the operating shape, not a market plan. The pedagogical commitments live in [`MISSION.md`](MISSION.md); the architectural decisions live in [`adr/`](../adr/).

## Personal Project Disposition

Paideia is a personal project. The builder maintains it because the pedagogy is worth maintaining; the project ships to other people via an Apple App Store cost-priced subscription because making it usable to the builder *cold* (per the success criterion below) requires that it be made usable, and once usable there is no pedagogical reason to refuse a small number of paying users who pass the discipline of the App Store's review and refund window.

Six commitments are binding:

1. **Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish.** No Android, no web app, no native AppKit/Catalyst Mac app. The DeepTutor fork (per [`infrastructure.md`](infrastructure.md)) is consulted only for what serves the Apple-native target.
2. **Cost-priced subscription via Apple In-App Purchase. No free tier.** Target $12.99/mo monthly with an annual subscription option at the typical 15–20% discount. Apple's Small Business Program (15% take rate under $1M annual revenue) is presumed.
3. **Builder eats API costs within a fixed annual operating subsidy budget. No grants, no 501(c)(3), no institutional licensing.**
4. **No bring-your-own-key, neither consumer nor institutional. No institutional regime.**
5. **Cost ceiling is a fixed annual operating subsidy budget — nothing ever raises it.**
6. **Polish is static, never dynamic. Maintenance is minimum-shape, deliberately.** No social, sharing, leaderboards, streaks, push notifications beyond auth/billing, community, in-app messaging. The builder is not a customer service department — FAQ-only support, release cadence at builder discretion.

The success criterion is **"an app I would pay for if it weren't mine."** Self-applying. The builder-bias failure mode (knowing how the system works obscures whether the system is usable cold) is what keeps freshman defaults and the rendering-policy worked example load-bearing — they protect against builder-bias drift, not just against pedagogical drift or market-fit drift. The Phase 9 small-cohort cold-test (2–3 people who haven't seen the project, given the TestFlight build with no instructions) is the verification artifact, not an ongoing program.

The refusal-not-deferral commitment is binding *in the success case*: **if this scales beyond what the personal subsidy budget supports, the response is to raise prices to slow growth or to cap signups, not to pursue institutional clients, grants, or acquisition.** Reopening requires a superseding ADR; per-session re-litigation is not authorized.

### See also

- [ADR 0035](../adr/0035-multi-platform-apple-expansion.md) — multi-platform Apple expansion; full text and reasoning for the six commitments.
- [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) — personal financial cost ceiling as the operating constraint commitment 5 binds.
- [ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md) — freshman-defaults calibration; one of the load-bearing protections against builder-bias drift.
- [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) — rendering-policy worked example; the second load-bearing protection.

## Pricing and Distribution

| Surface | Value |
|---|---|
| Distribution | Apple App Store. iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. Not sideload, not TestFlight-only at steady state. No Android, no web app, no native AppKit/Catalyst Mac app. |
| Pricing model | Cost-priced subscription via Apple In-App Purchase. No free tier. |
| Monthly | Target $12.99/mo. |
| Annual | ~15–20% discount on the monthly equivalent (Apple App Store standard). |
| Take rate | Apple Small Business Program (15%) presumed under $1M annual revenue. |
| Trial affordance | App Store screenshots + the 7-day Apple refund window. **A separate free-tier UX is not engineered** — a free tier is the canonical builder-funnel mechanic the disposition forecloses. |
| BYOK | Foreclosed (neither consumer nor institutional). |
| Pricing language | Learning-meaningful, not vendor-SKU-meaningful. Vendor model choices (which tier of Sonnet, when Opus runs) are internal optimization, not pricing surface. |
| Apple Developer Program | $99/year. Phase 8 forcing function (2–4 week enrollment lead time per [`ROADMAP.md`](../../ROADMAP.md)). |

Tiering by learning intensity is foreclosed at this disposition's scale — the no-funnel-mechanic discipline (commitment 2) is structurally incompatible with a free-tier-vs-paid-tier ladder. A proposal to tier must supersede the personal-project disposition contract.

## Operating Cost Model

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

The personal-project disposition does not target 10,000 users; if growth approached that scale, the response is the refusal-not-deferral commitment (raise prices, cap signups), not a different operating model.

## Annual Operating Subsidy Budget

The cost ceiling is a fixed annual operating subsidy budget the builder commits in advance and does not exceed. The numeric ceiling and the cost-cap mechanism's parameters are private operational configuration consistent with [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md). **Nothing ever raises the budget.** If usage growth would push spend past it, the response is to raise prices to slow growth, cap signups, or pause the App Store listing — never to pursue institutional clients, grants, or acquisition.

The mechanism: per-user spend ceiling, aggregate-system spend ceiling, real-time spend telemetry, defined behavior at the cap (per OQ-WALL-BEHAVIOR in [`tensions.md`](tensions.md), a single-tier ladder under the cost-priced subscription model). Soft walls degrade rather than terminate (Opus → Sonnet, deeper retrieval → shallower, two-hop neighborhood → one-hop) so concept-engagement integrity (per [`session-lifecycle.md`](session-lifecycle.md)) is preserved within the cap.

The trade is deliberate and binding: the system will reject some users at the soft wall who would have been profitable at scale, and will downshift quality for some users who would have benefited from the higher tier. Both are acceptable costs of bounded personal exposure under a refusal-not-deferral disposition.

## Cost Amplification with Session Length

Per-turn cost compounds with session length when the per-turn context grows turn-over-turn. The naive shape — load all prior turns into each subsequent turn's context — produces quadratic token growth in a single concept engagement. With concept engagements explicitly designed as "one continuous conversational thread, possibly spanning days" (per [`session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit), the naive shape would burn cost rapidly on the kind of deep, sustained engagement Paideia is built for.

The mitigation surface has three candidates: (a) **structured-state replacement** — instead of loading full prior turns, load the structured learner state and the most recent few turns, relying on the persistent event stream and `mastery_snapshots` for cross-session continuity (this matches [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript non-persistence commitment); (b) **automatic context compression** at platform-supported windows (Anthropic's prompt-caching surface mediates some of this transparently for the system-prompt portion; the dynamic per-turn portion remains the engineering surface); (c) **explicit per-turn summarization** — the agent summarizes the conversation-so-far into a structured note that replaces older raw turns. The choice has real quality-vs-cost stakes — aggressive compression loses subtle conversational state that affects pedagogical mode classification.

The specific strategy is open and tracked in [`tensions.md`](tensions.md) as **OQ-CONTEXT-COMPRESSION**, decide-before Phase 7 (the Sonnet teaching prototype is the first phase that produces multi-turn teaching-cost data; Phase 5 seed-graph generation is API-driven but not multi-turn). The combination of (a) and (c) appears most consistent with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and the bounded-context discipline in [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), but the trade space has not been argued through. The cost ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) is the upper-bound forcing function: a strategy that cannot keep typical concept-engagement cost inside the per-user cap is not deployable.

## Cancellation Discipline and Account Continuity

The project may be paused or cancelled at any point (per commitment 6 of the personal-project disposition). The architecture preserves user data exportability so cancellation is honest, not destructive — the **data-export affordance** is a Phase 9 success criterion, sibling to the **delete-account affordance** that satisfies Apple App Store guideline 5.1.1 wired to the [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) cascade. Both surfaces are first-class UI primitives; both are required for Phase 9 close.

Operating accounts (GitHub, Supabase, Vercel, Anthropic) remain under personal accounts. The Anthropic API has no transfer mechanism — it's a key rotation, taking minutes. If the project is cancelled, the operational state can be exported, the App Store listing pulled, and the Anthropic key rotated — no successor entity is presumed. The Apple Developer Program enrollment lapses if not renewed annually; this is acceptable under the cancellation discipline.

The privacy *posture* (what kinds of data persist at all) is the consumer-individual data regime: persistent storage is structural, not substantive; the erasure mechanism is hard-delete with cascade. The privacy *policy* (the ToS-adjacent legal document) is Phase 8 work pinned to Apple App Store submission per [ROADMAP.md](../../ROADMAP.md) Phase 8 success criteria. No institutional-cohort or DPA framing.

### See also

- [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md) — erasure mechanism (hard-delete with cascade) and individual-only data regime.
- [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) — persistent learner storage is structural, not substantive.
