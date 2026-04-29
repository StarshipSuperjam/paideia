# Business

## Market Reality

- Small, price-sensitive audience per domain. Serious learners are mostly students (broke) and autodidacts (resistant to paying for structure).
- Selling enrichment, not productivity. People chronically undervalue enrichment.
- Competition isn't other apps — it's free alternatives: YouTube, Wikipedia, reading groups, asking Claude directly in a normal conversation.
- Multi-domain coverage broadens the addressable market but multiplies the curation burden.

## Cost Model (at ~10,000 users)

- Estimated operating costs: $100–120k/year, dominated by API spend.
- Token-heavy features: syllabus generation, Socratic teaching, persistent learner model.
- A single serious user working through Hegel could burn significant API costs per month.
- At $15–20/month pricing, risk of losing money on power users (the exact users you want).

## Seasonal Cost Profile
**Added: 2026-04-07**

At 10,000 users on college quarter schedules, usage concentrates into three ~12-week bursts per year with significant dead periods between them. The $100–120k/year API cost estimate assumes relatively even distribution — actual quarterly peaks will be higher, actual off-quarter costs much lower. Grant budgeting and infrastructure provisioning should account for this shape rather than treating costs as flat monthly spend. This also creates a natural window for graph maintenance, corpus updates, and feature work during low-usage periods.

## Cost Amplification with Session Length
**Added: 2026-04-29 (S-0008)**

Per-turn cost compounds with session length when the per-turn context grows turn-over-turn. The naive shape — load all prior turns into each subsequent turn's context — produces quadratic token growth in a single concept engagement. With concept engagements explicitly designed as "one continuous conversational thread, possibly spanning days" (per [`docs/session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit), the naive shape would burn cost rapidly on the kind of deep, sustained engagement Paideia is built for.

The mitigation surface has three candidates: (a) **structured-state replacement** — instead of loading full prior turns, load the structured learner state and the most recent few turns, relying on the persistent event stream and `mastery_snapshots` for cross-session continuity (this matches [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript non-persistence commitment); (b) **automatic context compression** at platform-supported windows (Anthropic's prompt-caching surface mediates some of this transparently for the system-prompt portion; the dynamic per-turn portion remains the engineering surface); (c) **explicit per-turn summarization** — the agent summarizes the conversation-so-far into a structured note that replaces older raw turns. The choice has real quality-vs-cost stakes — aggressive compression loses subtle conversational state that affects pedagogical mode classification.

The specific strategy is open and tracked in [`tensions.md`](tensions.md) as **OQ-CONTEXT-COMPRESSION**, decide-before Phase 7 (the Sonnet teaching prototype is the first phase that produces multi-turn teaching-cost data; Phase 5 seed-graph generation is API-driven but not multi-turn). The combination of (a) and (c) appears most consistent with [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) and the bounded-context discipline in [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), but the trade space has not been argued through. The cost ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) is the upper-bound forcing function: a strategy that cannot keep typical concept-engagement cost inside the per-user cap is not deployable.

## Grant Opportunities

Strongest funding angle: community college humanities departments (for philosophy domain). Other domains may open other grant paths.

| Funder | Focus | Fit |
|--------|-------|-----|
| NEH (National Endowment for the Humanities) | Digital humanities, open educational tools | Strong (philosophy/humanities) |
| Mellon Foundation | Humanities access, community college equity | Strong (philosophy/humanities) |
| Gates Foundation | Community college completion initiatives | Moderate |
| NSF | STEM education tools | Potential (if STEM domains added) |
| State community college systems | Digital learning budgets | Moderate |

A $150–200k annual grant would cover operating costs at 10,000 users and fund continued development.

## Retention Paradox

A user who achieves mastery in one domain leaves — unless there's another domain to enter. Multi-domain coverage is the natural retention answer, but each domain is expensive to build.

## Revenue Mechanisms (Explored)
**Added: 2026-04-07 | Revised: 2026-04-29 (S-0008 — tier reframing, soft-wall principle, seasonal pre-buy, anti-vendor-SKU pricing-language principle, BYOK regime cross-link)**

These are candidates, not commitments. The goal is net-zero operating costs before opening to general use, bounded by the personal financial cost ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md).

**Amazon Associates affiliate links.** The mastery map already generates reading lists — each title deep-links to Amazon/Kindle. Associates program pays 4.5% on physical books (~$0.68 on a $15 text, more on collected works and Cambridge Companions in the $30-60 range). Perfectly aligned with the product since the user was going to buy the book anyway. Won't cover API costs alone but reduces the gap with zero friction.

**Tiered access by learning intensity (preferred framing over raw-interaction pricing).** The natural pricing axis is *learning intensity*, not *number of interactions*. Interaction-count pricing hides the real cost structure (token-weighted and model-weighted: a Sonnet teaching exchange is cheap; an Opus cross-domain edge generation pass or self-correction review is expensive but infrequent) and produces volatile per-user margins. Tiering by learning intensity maps the pricing onto the architectural choices already made and produces a coherent upsell story.

The active V1 sketch — to be revised against actual cost data at Phase 7+:

- **Free tier.** Full graph traversal, Sonnet-driven teaching, the persistent learner model, *bounded* cross-domain bridges per month (a few — enough for the user to *experience* the differentiator without absorbing its cost without limit). No Opus self-correction reviewer in the teaching loop (the user sees Sonnet's output unreviewed).
- **Paid tier.** Unlimited cross-domain bridges, Opus reviewer in the teaching loop, longer / deeper concept engagements. Target price-point in the $8–15/month range, positioned against Coursera / Great Courses.
- **Usage packs.** Explicit Opus-heavy operations beyond the paid tier (e.g., "request scholarly review of my interpretation," "generate a custom syllabus for a topic outside the standard graph"). Pre-buyable; non-expiring within a season.

The framing rule: **do not paywall the architectural differentiator entirely.** Cross-domain edges and self-correction are what make Paideia ≠ "asking Claude directly in a normal conversation" (the competitive line in *Market Reality* above). Hiding them entirely behind the paid tier makes the free tier a worse Claude — hard to convert from. Constrained doses on the free tier let the user taste what's behind the wall and creates legible upgrade motivation.

**Pricing language is user-meaningful, not vendor-SKU-meaningful.** The pricing surface should not say "Opus tier" or "GPT-4-class access" — that prices the vendor's price list, not the learning value. Use surface terms like "scholarly review," "cross-domain insight," "deep close reading." The architecture-side mapping (which model handles what) is internal. Sophisticated users who infer the SKU mapping should not feel the pricing leaks vendor pass-through; they should feel they are paying for learning, with vendor choice as an internal optimization.

**Soft walls degrade, they do not terminate.** When a user approaches their per-tier cap (free-tier monthly bridge count, paid-tier session-depth budget, etc.), the agent downshifts gracefully — Opus → Sonnet, deeper retrieval → shallower, two-hop neighborhood → one-hop — rather than terminating mid-concept-engagement. The atomic unit of teaching is the concept engagement (per [`docs/session-lifecycle.md`](session-lifecycle.md), Concept Engagement as the Atomic Unit), which spans hours or days. A wall that fires mid-engagement violates that integrity. The specific degradation ladder is the open question tracked as **OQ-WALL-BEHAVIOR** in [`docs/tensions.md`](tensions.md); the principle (degrade, don't terminate) is committed by [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md).

**Seasonal pre-buy smooths the seasonal cost spike.** The Seasonal Cost Profile section above names a real interaction with payment willingness: students have summer-job cash in August but use the system most in October. Letting users pre-buy a quarter-pack in summer for use in fall is good for both parties — the pack smooths the user's perception of value across the gap, and pre-collected revenue smooths the operator's exposure to the quarterly cost spike. Roll-forward terms (purchased pack does not expire within the academic year; perhaps with a 12-month outer cap) give the gesture credibility.

**Bring-your-own-key (BYOK) — institutional, not consumer.** Consumer BYOK self-selects technically sophisticated users who already have API access — not the freshman audience the system is calibrated for. The legitimate BYOK lane is **institutional**: a community college, library, or university holds the Anthropic API key, gets bulk pricing or uses an existing institutional contract, and Paideia is the application layer above. Cost flows institution → Anthropic (sidesteps the [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) builder-exposure problem entirely); Paideia charges the institution a per-seat or flat license. The consumer-vs-institutional regime question — and the privacy implications when transcripts log against the user's account at Anthropic — is tracked as **OQ-BYOK-REGIME** in [`docs/tensions.md`](tensions.md), decide-before consumer launch.

**Classroom/institutional tier.** $5/seat/month for professors or reading groups. Philosophy departments are the natural first customer. This is the volume play — 30-student seminars at a price point low enough that department budgets absorb it. Composes with the institutional BYOK regime above when the institution provides the API key.

**Internal fine-tuning from session data.** Selling conversation data externally raises privacy/consent problems and requires volume guarantees. The practical version: use accumulated teaching sessions internally to fine-tune a smaller, cheaper model that handles routine interactions, reducing API costs rather than generating revenue. This connects to the cost mitigation ideas in architecture.md. **Constrained by [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md):** any fine-tuning use draws on the structured event log and structured tension records, not on raw transcripts (which are not persisted as system-of-record data). This forecloses transcript-based fine-tuning of a session-specific model without a superseding ADR. **Priority is raised by [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md):** internal fine-tuning is one of the few cost-mitigations that scales superlinearly with user count, and the cost ceiling is a hard constraint not a target.

## Personal-Use Cost Estimates
**Added: 2026-04-07**

Build phase: covered by existing Claude Max subscription (used via Claude Code). No additional build cost. Hosting: $5–15/month for a small VPS or managed platform (Railway, Fly.io, Vercel + managed database). Lightweight requirements for single-user or small-user-count operation. API costs for 3–5 books/month active use on Sonnet 4.6 ($3/$15 per million tokens): approximately $5–7/month at standard rates. With prompt caching on system prompts and learner state (90% reduction on repeated context), drops to $3–4/month. Steady-state all-in for personal use: under $20/month. A handful of paying users at even a modest price point would achieve net-zero.

## Personal Financial Risk Ceiling
**Added: 2026-04-29 (S-0008)**

Paideia is a private project with zero outside funding and no realistic path to VC funding (education apps with AI-driven marginal costs are not the kind of company VCs fund). The funding situation is structural, not transitional: the builder is the only buffer against runaway operating cost. Between the personal-use floor (~$3–7/month) and the 10,000-user steady state (~$100–120k/year, dominated by API spend), every increment of non-builder usage shifts cost onto the builder personally.

The asymmetry is non-negotiable: there is no value of an unmonitored 10x usage spike that justifies the personal financial exposure. A viral moment that delivers $4,000 of value to learners while delivering a $4,000 surprise bill to the builder is a *failure mode*, not a success — even if the upside is positive. **Cost protection is therefore a precondition for opening the system to non-builder use, not a feature added later.**

[ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) commits the principle: no phase that opens the system to non-builder users may close without a cost-cap mechanism wired and tested (per-user cap, aggregate-system cap, real-time spend telemetry, defined behavior at the cap). The specific cost ceiling number remains private operational configuration, not a public artifact. The mechanism's behavior at the cap is the **degrade-don't-terminate** principle described in *Revenue Mechanisms (Explored)* above; the specific degradation ladder is tracked as OQ-WALL-BEHAVIOR in [`docs/tensions.md`](tensions.md).

The trade is deliberate: the system will reject some users at the soft wall who would have been profitable at scale, and will downshift quality for some users who would have benefited from the higher tier. Both are acceptable costs of bounded personal exposure. The alternative — open access with no cap — has expected value dominated by the personal-financial-risk failure mode regardless of upside. This trade is the load-bearing decision; the mechanisms that implement it are downstream.

## Audience vs. Market: Community College
**Added: 2026-04-07 | Revised: 2026-04-08**

Community college students are the primary **audience** — they shape the pedagogical defaults, the cold-start calibration, the expression contract's starting posture, and the diagnostic conversation's assumptions. The system is built for learners encountering these ideas for the first time in a structured context, not experienced readers supplementing existing knowledge. This is the right default because the asymmetry of failure is directional: a freshman encountering content beyond their scope cannot proceed; an autodidact encountering freshman-level defaults is mildly annoyed at worst and rapidly escalated by the adaptive teaching system.

Community college **departments** are the primary market — the eventual paying customer at institutional scale. But the enterprise wrapper (LMS integration, instructor dashboards, FERPA compliance, grade export) is deferred until the teaching system has proven itself with real learners. Every month spent on Canvas integration is a month not spent on the teaching system itself, and the teaching system is the product. The institutional requirements are all bolt-on features that sit above the data model — API adapter layers, read-only views, and policy work — and require no core architecture changes given the schema provisions in architecture.md (nullable cohort_id on events, shareable constrained paths).

The product identity resolves as: a self-learner product calibrated for beginners, with schema provisions that preserve the institutional path. The autodidact and the freshman use the same product. The cold-start framing communicates that the system adapts to the quality of the learner's engagement, which simultaneously reassures the freshman (this will meet me where I am) and activates the autodidact (I'm being invited to perform). Neither knows that both are being served.

This framing gives the work a mission that survives beyond personal use — infrastructure for a kind of liberal education that community colleges often promise but can't fully deliver — while keeping the build priority on the teaching system rather than institutional plumbing.

## Acquisition as Exit Path: Khan Academy
**Added: 2026-04-07**

Khan Academy is a plausible acquirer. They are a non-profit, they have invested in AI tutoring via Khanmigo, and their humanities coverage is weak relative to STEM. A well-built pedagogy graph with validated community college usage data fills a genuine gap in their offering. Non-profit to non-profit acquisition is structurally cleaner than a commercial sale — mission alignment reduces friction on their board, no awkward commercial pivot required. The realistic timeline is 3–4 years: build, launch with community college focus, secure institutional partnerships, accumulate learner data, then approach with evidence. The primary risk is that demonstrating the concept publicly invites replication rather than acquisition — the moat is the data and the institutional relationships, not the architecture itself. Personal use continues regardless of whether acquisition happens, which means the downside of pursuing this path is zero.

## Account Ownership and Transfer Path
**Added: 2026-04-07**

Building under personal accounts (GitHub, Supabase, Vercel, Anthropic) is the correct starting position. All three primary services have native org transfer mechanisms: GitHub repo transfer to an org preserves forks, issues, and history with automatic URL redirect; Supabase project transfer moves database, schema, and data intact; Vercel project transfer carries deployments, domains, and environment variables. The Anthropic API has no transfer mechanism — it's a key rotation, taking minutes.

The one transfer path with real friction is the App Store. Apple requires a formal transfer request between developer accounts; both must be enrolled and the app must be in good standing. Budget 2–4 weeks lead time when that moment comes. Google Play is similar but lighter.

The one thing to design intentionally before opening to general users: data ownership clarity. Users who interact with the app while it's under personal accounts need a clear record of who the data controller was at each point. This matters for privacy policy continuity and for any grant or non-profit filing that requires clean IP chain-of-title. The privacy *posture* — what kinds of data persist at all — is settled in [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md); the privacy *policy* (the ToS-adjacent legal document) is Phase 8 work pinned to Apple App Store submission per [ROADMAP.md](../ROADMAP.md) Phase 8 success criteria.

## Non-Profit Incorporation: Mechanics and Timing
**Added: 2026-04-07**

**How it works in Washington State.** File Articles of Incorporation with the WA Secretary of State (~$30, online), draft bylaws, hold an organizational meeting, obtain an EIN from the IRS, then file IRS Form 1023-EZ for federal 501(c)(3) status. The 1023-EZ is available as long as projected annual revenue stays under $50,000 for the first three years, which is almost certainly true at early scale. Total filing fees are under $300. Realistic timeline from filing to IRS determination letter: 3–6 months for 1023-EZ.

Ongoing requirements: annual state report, annual IRS Form 990-N (the postcard version, for small orgs), a board of directors (minimum 3 people in WA with required officers), and records demonstrating pursuit of the exempt purpose. Not burdensome at small scale, but not zero overhead either.

**When to incorporate.** The App Store doesn't require non-profit status and incorporating early provides no practical advantage at that transition point. The right triggers are: (1) applying for grants — NEH, Mellon, and most institutional funders require 501(c)(3) status before issuing a grant; (2) entering institutional relationships with community colleges — a department piloting the tool will want to know who they're contracting with, and a WA State 501(c)(3) is a cleaner answer than an individual developer; or (3) wanting IP held by an entity rather than a personal name from the start for acquisition chain-of-title purposes.

**Working resolution:** Defer incorporation until grant applications or institutional pilots are actually in scope — likely 12–24 months out at minimum given the current build phase. Revisit when either trigger becomes real.

## Generative Graph Independence
**Added: 2026-04-07**

The graph is no longer dependent on SEP or any licensed dataset for its content. Concept nodes and prerequisite edges are generated by AI and curated through use — the academic reference works (SEP, IEP, Oxford dictionaries) serve as inventories and cross-reference checks, not as source material requiring licensing. This eliminates the licensing constraint that would have made commercial use of SEP-derived content legally uncertain, and it creates a stronger competitive position: the graph is proprietary through accumulated curation and correction, not through a licensing agreement any funded competitor could also sign. This is the kind of moat that matters for acquisition — a potential acquirer would be buying something they can't replicate by pointing engineers at the same public sources.

## Syllabus Upload as Institutional Wedge
**Added: 2026-04-07 | Revised: 2026-04-08**

A professor uploads a course syllabus; Paideia maps the readings and topics to the existing graph and generates a learning path that fills in the prerequisite gaps the syllabus implicitly assumes students will handle on their own. The syllabus is a *constraint* on graph traversal, not a replacement for it — the professor's sequencing decisions are respected, and Paideia catches students who can't make the inferential leaps the syllabus silently demands. This is the version that sells at $5/seat/month to a department chair, because the pitch is: "your syllabus stays the same, your students just stop getting lost."

This feature sits at the boundary between the self-learner product and the institutional product. For autodidacts, it's a power-user feature — upload a course you're following online, get structured support. For institutions, it's the sales wedge — the thing that makes a department willing to try the tool with a live class. The implementation is the same; the framing and acquisition channel differ.

The concrete pipeline architecture (parse → resolve → gap analysis → generate constrained path), the shared entity resolution service with close reading, and the failure mode hierarchy are documented in architecture.md under "Syllabus Upload Pipeline."

## Standing Disposition

Build a commercially sustainable product. Revenue logic must never change what the product teaches or how it teaches — gamification, broader-but-shallower coverage, and engagement mechanics optimized for retention over learning remain off the table. But the product is designed to sustain itself financially and reach users beyond the builder. The community college mission and Khan Academy acquisition path are now active planning considerations, not daydreams. Personal use continues regardless and remains the primary testing ground for pedagogical quality.

---
*Last updated: 2026-04-29 (S-0008 — personal financial cost ceiling section added per ADR 0029; Revenue Mechanisms reframed by learning intensity with cross-domain bridges as differentiator and tier-language as user-meaningful not vendor-SKU; soft-wall degradation principle and seasonal pre-buy added; institutional-vs-consumer BYOK regime split added with OQ-BYOK-REGIME pointer; Cost Amplification with Session Length section added with OQ-CONTEXT-COMPRESSION pointer)*
