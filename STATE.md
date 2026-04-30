# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (**substantively closed at S-0011**; fully closes at S-0012 once the supersession ADR retiring [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md) lands and the corresponding rewrites of `docs/business.md` / `docs/MISSION.md` / `ROADMAP.md` commit); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 fully closed at S-0008 (rendering policy + input-side scope + personal financial cost ceiling); Phase 4.5 input-dataset-survey scaffolding landed at S-0009; §1.3 closed at S-0010 (`confidence_level` column on Node Schema, ADR 0030); privacy ADRs collapsed at S-0011 under the project-direction shift (ADR 0031 settles OQ-PRIVACY-A as hard-delete-with-cascade and withdraws OQ-PRIVACY-B as moot — no institutional regime to design for). |
| **Last build session** | S-0011 (2026-04-30) — Privacy ADRs closed; project-direction shift settled in conversation, formal supersession queued for S-0012. **[ADR 0031](adr/0031-erasure-mechanism-and-individual-only-regime.md)** settles **OQ-PRIVACY-A** as hard-delete with cascade — `ON DELETE CASCADE` foreign-key discipline across `learner_events`, `mastery_snapshots`, `tension_log` carries deletion through to all rows linked to a user; Apple App Store guideline 5.1.1 (in-app account deletion) is satisfied at the schema level. Withdraws **OQ-PRIVACY-B** as moot — `cohort_id` removed from [ADR 0026](adr/0026-persistent-learner-storage-structural-not-substantive.md) sub-decision (2)'s `learner_events.context` shape (surviving columns: `path_id`, `source_text_id`, `session_id`); institutional schema provisions in `docs/architecture.md` become dead-weight whose removal lands in S-0012. Two rejected candidates from OQ-PRIVACY-A recorded as rejected: **crypto-shredding** (KMS keys earn their keep only when audit-trail-preserving erasure is contractually required) and **anonymize-and-aggregate** (graph-level signal contribution from a single user's events is negligible at consumer scale; residual data potentially re-identifiable). The simplification was enabled by the project-direction shift settled in S-0011 conversation: single-platform iOS App Store consumer subscription, no institutional regime, no BYOK, no enterprise wrapper, no grants, no 501(c)(3), no acquisition exit. The supersession ADR formalizing that shift is queued for S-0012. **`docs/tensions.md`** OQ-PRIVACY-A → "Settled by ADR 0031"; OQ-PRIVACY-B → "Withdrawn by ADR 0031". **`docs/CROSS_REFERENCES.md`** gains a five-consumer entry for ADR 0031; Phase 2 → Phase 3 boundary check marked *satisfied at S-0011 close*. **`adr/README.md`** Phase 1 index extended; orientation updated. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0012 — Project-direction supersession: retire ADR 0002 and rewrite the business framing** *(closes Phase 1 fully; the contract S-0011's ADR 0031 already depends on.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (31 ADRs after S-0011) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

S-0012 is the formal recording of a project-direction shift settled in the S-0011 conversation. **The deliberation has happened. S-0012 is implementation, not re-deliberation.** The brief below names what S-0012 produces and what is already settled (do not re-litigate). If S-0012 surfaces a complication that genuinely reopens any of the settled items, the auto-mode interrupt criteria apply (irreversible-with-unclear-path); otherwise the session implements the contract as specified.

### Settled in S-0011 conversation (do not re-deliberate)

- **Platform.** iOS only. No Android, no web, no Linux/Mac desktop. The DeepTutor fork (Apache 2.0, infrastructure base per `docs/infrastructure.md`) is consulted only for what serves iOS.
- **Distribution.** Apple App Store. Not sideload, not TestFlight-only. Apple Developer Program enrollment ($99/yr) at Phase 8.
- **Pricing model.** Cost-priced subscription via Apple In-App Purchase. **No free tier.** Target $12.99/mo monthly with an annual subscription option (~15–20% discount typical). Apple's Small Business Program (15% take rate under $1M revenue) presumed. App Store screenshots + 7-day Apple refund window function as the trial affordance — do not engineer a separate free-tier UX.
- **Cost discipline.** Builder eats API costs. ~$300/yr personal subsidy budget covers infrastructure (Apple Developer + VPS + domain). Paid users cover their own marginal API at the $12.99 price point; subsidy budget is not expected to fund free-tier API. The "leave it open to expand" pattern that produced the institutional/grants/acquisition framing is closed *as a refusal, not a deferral* — including in the success case.
- **No BYOK.** Neither consumer nor institutional. OQ-BYOK-REGIME closes by foreclosure in this ADR (do not author a separate ADR for OQ-BYOK-REGIME).
- **No institutional regime.** No grants, no 501(c)(3), no community-college audience-vs-market framing, no Khan Academy acquisition exit, no syllabus-upload-as-sales-wedge. Personal-use syllabus upload may survive as a feature; its sales-wedge framing does not.
- **Polish target.** As polished as solo + AI can manage. **Static polish only** — visual design, typography, animation, copy quality, layout, iconography, sound design, haptics. **Dynamic features explicitly foreclosed** — no social, sharing, leaderboards, streaks, push notifications beyond auth/billing, community, in-app messaging, "what's new" surfaces, anything that requires the builder to do something on a recurring schedule for the app to feel alive.
- **Maintenance posture.** Minimum-maintenance shape up front, deliberately. The builder is not a customer service department. No live support email surface; FAQ-only support; release cadence at builder discretion (4–8 week typical baseline).
- **Cancellation discipline.** No obligation to users. The project may be paused or cancelled at any point. The architecture should preserve user data exportability so cancellation is honest, not destructive — Phase 9 work, not S-0012's.
- **Success criterion.** "An app I would pay for if it weren't mine." This is a self-applying criterion; the builder-bias failure mode (knowing how the system works obscures whether it's usable cold) is what keeps [ADR 0012](adr/0012-freshman-defaults-autodidact-ceiling.md) (freshman defaults) and [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) (rendering policy worked example) load-bearing — they protect against builder-bias drift, not just market-fit. A small-cohort cold-test (2–3 people who haven't seen the project, given the TestFlight build with no instructions) is a Phase 9 verification, not an ongoing program.

### S-0012 work items

**1. Author ADR 0032 — Personal project disposition; supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md).** The new ADR commits the disposition above. Required content:

- The corruption-vector identification: "leave the option open" was the seed that recursively pulled the design toward business outcomes; the fix is removing the optionality itself, not just the business mechanisms it preserved.
- The refusal-not-deferral commitment, written in the form of refusal rather than deferral. A specific sentence to include or paraphrase: *"If this scales beyond what the personal subsidy budget supports, the response is to raise prices to slow growth or to cap signups, not to pursue institutional clients, grants, or acquisition."*
- The success criterion ("an app I would pay for if it weren't mine") with the builder-bias-protection consequence (ADR 0012 and ADR 0027 stay load-bearing for new reasons).
- Cross-link to the operating-discipline reframing of [ADR 0029](adr/0029-personal-financial-cost-ceiling.md) — cost ceiling is no longer "bridge to grants" but "fixed annual operating subsidy budget; nothing ever raises it." Numeric values remain private operational config.
- Status: Accepted. Supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md). Does not rise to MISSION.md's strong-working-commitments list (operating discipline, not pedagogical commitment) — same precedent as ADRs 0026 and 0029.

**2. Flip [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md) to `Status: Superseded by ADR 0032`.** One-directional pointer; ADR 0002 file is not deleted (per the ADR README supersession discipline).

**3. Substantially rewrite `docs/business.md`.** Most sections drop; what survives is reframed.
- **Drop:** Market Reality (10k-user analysis), Cost Model at 10k users, Seasonal Cost Profile, Grant Opportunities, Retention Paradox, Revenue Mechanisms (Explored), Acquisition as Exit Path: Khan Academy, Audience vs. Market: Community College, Non-Profit Incorporation, Syllabus Upload as Institutional Wedge.
- **Reframe:** Generative Graph Independence (drop the moat-for-acquisition framing; operational substance — proprietary curation through use — survives in `docs/content-strategy.md`, not as a competitive position). Personal Financial Risk Ceiling → "Annual Operating Subsidy Budget." Personal-Use Cost Estimates → "Operating Cost Model." Cost Amplification with Session Length stays (still relevant for OQ-CONTEXT-COMPRESSION at Phase 7). Standing Disposition → "Personal Project Disposition," cross-links to ADR 0032.
- **Add:** A short section ("Pricing and Distribution") naming the cost-priced subscription, single-platform iOS via App Store IAP, no free tier, no BYOK, the $12.99/mo target, and the App Store refund window as the trial affordance.
- **Suggested final length:** ~30–40% of current.

**4. Substantially rewrite `docs/MISSION.md`.**
- Remove the "Audience vs. market" subsection from the Audience Framing section. Only audience remains; market disappears.
- Rewrite or absorb strong working commitment 2 ("Commercial sustainability without pedagogical compromise"). The replacement framing is "operating discipline must not corrupt pedagogy" — the threat is no longer revenue-mechanism-driven, it's builder-funnel-mechanic-driven (the builder optimizing for retention/conversion over teaching quality). Cross-link to ADR 0032.
- Adjust the closing "What this is" framing: Paideia is now described honestly as a personal project the builder shipped to the iOS App Store at a cost-priced subscription, calibrated for first-encounter learners (because the builder values the pedagogical discipline of that calibration, not because of market-fit). The "freshman defaults" calibration survives because it protects against builder-bias drift.

**5. ROADMAP edits.**
- **Phase 4.5 (input dataset survey).** License-tier framing simplifies — "consultable for personal use" is the operative bucket; "ingestable for commercial use" framing drops. Survey scope is unchanged otherwise.
- **Phase 8 (evaluation harness).** Substantial simplification. Remove: external-rubric (community college instructor blind review), head-to-head against DeepTutor unmodified, OQ-PHASE8-A baseline-mix deliberation. Keep: Apple Developer Program enrollment + 2–4 week lead time; privacy policy authoring (consumer App Store, not institutional); cost-cap mechanism wired and tested (per ADR 0029, narrower form); rendering-policy worked-example check (per ADR 0027). Add: a small private TestFlight cohort (2–3 people who haven't seen the project) as the cold-test verification of the "would I pay for it" success criterion.
- **Phase 9 (UI prototype).** Narrow to iOS-only-native. Remove all Android / Google Play references. Remove `cohort_id`-driven UI affordances. Add: delete-account affordance (satisfies App Store guideline 5.1.1 wired to ADR 0031's cascade). Add: data-export affordance (preserves cancellation-discipline honesty). Static polish discipline named explicitly; dynamic-feature foreclosure named explicitly.
- **Strong working commitments referenced throughout.** Commitment 2 rewritten or removed; cross-link to ADR 0032 added.

**6. `docs/architecture.md` edits.**
- Drop the "Institutional Schema Provisions" section (the institutional regime is foreclosed; `cohort_id` removed by ADR 0031; shareable-constrained-paths-as-institutional-wedge framing dies).
- Drop the syllabus-upload-pipeline's "institutional product wedge" framing; the *feature* may survive as personal-use, but its institutional context dies.

**7. `docs/tensions.md` edits.**
- Close **OQ-BYOK-REGIME** with "Withdrawn by ADR 0032 — no BYOK, neither consumer nor institutional."
- **OQ-WALL-BEHAVIOR** survives but simplifies — single-tier soft-wall ladder. Update the entry to note tier-shaped framing collapses.
- **OQ-CONTEXT-COMPRESSION** unaffected (still load-bearing for Phase 7, regardless of business framing).
- **OQ-PHASE8-A** (evaluation baseline) — the original three candidates (external rubric, head-to-head DeepTutor, head-to-head stock Sonnet) lose the rubric and DeepTutor candidates; settle as "head-to-head stock Sonnet without rendering policy + small private TestFlight cohort cold-test" or close the OQ entirely. Judgment call within S-0012.

**8. `docs/CROSS_REFERENCES.md` edits.**
- Update the Phase 8 → Phase 9 boundary check: OQ-BYOK-REGIME closes by ADR 0032 (foreclosure); OQ-WALL-BEHAVIOR remains in simpler form.
- Add ADR 0032 consumer entry under "Shared capability consumers" (consumers: `docs/business.md` rewrite, `docs/MISSION.md` rewrite, [ADR 0029](adr/0029-personal-financial-cost-ceiling.md) reframing, ROADMAP Phase 8/9 edits, [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md) supersession pointer).

**9. CHANGELOG entry under `[Unreleased]`.** Added (ADR 0032), Changed (ADR 0002 superseded; business.md rewritten; MISSION.md rewritten; ROADMAP Phase 4.5/8/9 edits; architecture.md institutional provisions dropped; tensions.md OQ-BYOK-REGIME withdrawn; CROSS_REFERENCES.md updated).

### S-0012 success criteria

- ADR 0032 lands with Status: Accepted, supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md), and binds the disposition above as a refusal-not-deferral contract.
- ADR 0002 flipped to `Status: Superseded by ADR 0032`.
- `docs/business.md` rewritten — drops listed sections, reframes survivors, adds the Pricing and Distribution section.
- `docs/MISSION.md` rewritten — audience-vs-market removed, commitment 2 rewritten or absorbed.
- ROADMAP Phase 4.5 / 8 / 9 edits committed.
- `docs/architecture.md` Institutional Schema Provisions dropped.
- `docs/tensions.md` OQ-BYOK-REGIME withdrawn; OQ-WALL-BEHAVIOR simplified; OQ-PHASE8-A handled.
- `docs/CROSS_REFERENCES.md` Phase 8 → 9 boundary check updated; ADR 0032 consumer entry added.
- `tools/validate.py` returns clean (0 hard-fails; soft-warns acceptable if recorded in outcome_summary).
- **Phase 1 fully closes.** Phase 2 (Build Plan Scaffolding) opens.
- MemPalace decision drawer for ADR 0032 filed (verbatim conversational reasoning, per the two-layer decision-recording discipline in CLAUDE.md).

### Budget warning

S-0012 is the largest single session since S-0008 (which authored ADRs 0027/0028/0029 plus four tension entries plus the inference registry). Budget guidance per CLAUDE.md applies: substantive extraction work, target 60% context, hard cap 70%. If the session approaches the cap mid-work, halt at the next sensible boundary (after ADR 0032 lands but before all docs rewrites, ideally), write outcome_summary with partial-completion notes, archive `current.json` with `status: closed_partial`, and S-0013 picks up from there.

### Source documents (read at S-0012 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`adr/0002-commercial-sustainability-without-pedagogical-compromise.md`](adr/0002-commercial-sustainability-without-pedagogical-compromise.md) — what is being superseded.
- [`adr/0029-personal-financial-cost-ceiling.md`](adr/0029-personal-financial-cost-ceiling.md) — reframed but not superseded.
- [`adr/0031-erasure-mechanism-and-individual-only-regime.md`](adr/0031-erasure-mechanism-and-individual-only-regime.md) — depends on the supersession; sets the dependency the supersession ratifies.
- [`docs/business.md`](docs/business.md) — the rewrite target.
- [`docs/MISSION.md`](docs/MISSION.md) — the rewrite target.
- [`ROADMAP.md`](ROADMAP.md) — Phase 4.5 / 8 / 9 edit targets.
- [`docs/architecture.md`](docs/architecture.md) — Institutional Schema Provisions section to drop.
- [`docs/tensions.md`](docs/tensions.md) — OQ-BYOK-REGIME / OQ-WALL-BEHAVIOR / OQ-PHASE8-A.
- [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md) — boundary checks and consumer entries.

### After S-0012

Phase 1 fully closes. Phase 2 (Build Plan Scaffolding) opens — `build_plan/` directory naming the chunked authoring sessions for Phases 3–9, with the ADR 0032 disposition shaping every per-session contract. The four originally-S-0008-opened tensions land at later phase boundaries: OQ-WALL-BEHAVIOR at Phase 8 cost-cap wiring, OQ-CONTEXT-COMPRESSION at Phase 7, OQ-PEDAGOGY-INFERENCE-LOCUS at the registry-size revisit trigger. Sessions 12–14 of the prompt pack remain deferred. Phase 4.5 input dataset survey is queued between Phase 4 and Phase 5.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0011 close, the active set is 10 items (OQ-PRIVACY-A and OQ-PRIVACY-B closed by ADR 0031):

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- OQ-PHASE8-A — Phase 8 evaluation baseline choice; will be revisited in S-0012 (the original three-candidate framing — external rubric / DeepTutor head-to-head / stock-Sonnet head-to-head — loses two candidates under the project-direction shift)
- **OQ-BYOK-REGIME** (added S-0008, per ADR 0029) — *to be withdrawn in S-0012* (ADR 0032 forecloses BYOK in both regimes)
- **OQ-WALL-BEHAVIOR** (added S-0008, per ADR 0029) — soft-wall degradation ladder at cost cap; *will simplify in S-0012* to single-tier under cost-priced subscription model; decide-before Phase 8 cost-cap wiring
- **OQ-CONTEXT-COMPRESSION** (added S-0008, per ADR 0029) — token-amplification mitigation for multi-turn engagements (structured-state replacement + automatic compression + explicit summarization candidates); decide-before Phase 7
- **OQ-PEDAGOGY-INFERENCE-LOCUS** (added S-0008, tagged `watch`) — rule layer vs. distributed inference; revisit when inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR an operational complaint surfaces
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema); ADR 0031 added in S-0011 (erasure mechanism — hard-delete with cascade — and individual-only data regime). Total ADR count: 31. ADR 0032 (project-direction supersession) lands in S-0012 and supersedes ADR 0002, leaving Accepted count at 31 and Superseded count at 1.
