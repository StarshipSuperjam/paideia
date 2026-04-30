# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012**; §1.1 closed across S-0004 / S-0005 / S-0006 (prompt-pack Sessions 9, 10, 11); privacy-posture insertion landed at S-0007; §1.2 closed at S-0008; Phase 4.5 input-dataset-survey scaffolding landed at S-0009; §1.3 closed at S-0010; privacy ADRs collapsed at S-0011 (ADR 0031); **project-direction supersession landed at S-0012 — [ADR 0032](adr/0032-personal-project-disposition.md) supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md), records personal-project disposition as refusal-not-deferral, closes OQ-BYOK-REGIME by foreclosure, simplifies OQ-WALL-BEHAVIOR to single-tier, settles OQ-PHASE8-A**; `docs/business.md` and `docs/MISSION.md` substantially rewritten; ROADMAP Phase 4.5 / Phase 8 / Phase 9 simplified; `docs/architecture.md` Institutional Schema Provisions dropped. **Phase 2 (Build Plan Scaffolding) opens at S-0013.** |
| **Last build session** | S-0012 (2026-04-30) — Project-direction supersession; Phase 1 fully closes. **[ADR 0032](adr/0032-personal-project-disposition.md)** records the personal-project disposition settled in the S-0011 conversation: six binding commitments (single-platform iOS App Store; cost-priced subscription via Apple In-App Purchase, no free tier, target $12.99/mo monthly with annual subscription option; builder eats API costs within fixed annual operating subsidy budget; no BYOK neither consumer nor institutional; ADR 0029 cost ceiling reframes as fixed subsidy budget — nothing ever raises it; static polish only, dynamic-feature surfaces foreclosed). Success criterion: "an app I would pay for if it weren't mine." Refusal-not-deferral commitment binding in the success case: *if this scales beyond what the personal subsidy budget supports, the response is to raise prices to slow growth or to cap signups, not to pursue institutional clients, grants, or acquisition.* Corruption-vector identification: "leave the option open to expand later" was the seed pattern; the fix is removing the optionality. **Supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md)** (status flipped to `Superseded by ADR 0032`). **[ADR 0029](adr/0029-personal-financial-cost-ceiling.md)** *Grant timeline interacts with this commitment* consequence retracted; mechanism intact, justification structure changed (subsidy budget, not bridge-to-grants). **`docs/business.md`** substantially rewritten — 11 sections dropped (Market Reality, Cost Model at 10k users, Seasonal Cost Profile, Grant Opportunities, Retention Paradox, Revenue Mechanisms (Explored), Acquisition as Exit Path: Khan Academy, Audience vs. Market: Community College, Non-Profit Incorporation, Syllabus Upload as Institutional Wedge, Generative Graph Independence (moat-for-acquisition framing)); 3 sections reframed (Annual Operating Subsidy Budget, Operating Cost Model, Personal Project Disposition); 1 section added (Pricing and Distribution); 1 slimmed (Cancellation Discipline replacing Account Ownership and Transfer Path); Cost Amplification kept verbatim. **`docs/MISSION.md`** — commitment 2 reframed as "Operating discipline must not corrupt pedagogy"; Audience vs. market subsection removed; What this is updated with personal-project framing. **`ROADMAP.md`** — Phase 4.5 license-tier simplified (consultable for personal use is the operative bucket); Phase 8 substantially simplified (external-rubric and DeepTutor-head-to-head dropped; small private TestFlight cohort cold-test added; OQ-BYOK-REGIME-gating retracted); Phase 9 narrowed to iOS-only-native (delete-account + data-export affordances added; static-polish discipline named; dynamic-feature surfaces foreclosed); commitment 2 in the strong-working-commitments tail rewritten. **`docs/architecture.md`** — Institutional Schema Provisions dropped, replaced with Individual Data Regime; Syllabus Upload Pipeline institutional-wedge framing dropped, personal-use framing kept. **`docs/tensions.md`** — OQ-BYOK-REGIME withdrawn by ADR 0032; OQ-WALL-BEHAVIOR simplified to single-tier ladder; OQ-PHASE8-A settled. **`docs/CROSS_REFERENCES.md`** — six-consumer entry added for ADR 0032; ADR 0029 entry updated; ADR 0031 entry's business.md cross-link updated; Phase 8 → 9 boundary check updated. **`adr/README.md`** Phase 1 index extended with ADR 0032; ADR 0002 row marked Superseded; orientation updated; final tally 31 Accepted + 1 Superseded (32 ADRs total). MemPalace decision drawer for ADR 0032 filed: `drawer_paideia_general_1702dff6411b62f3b82d7be6`. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0013 — Phase 2: Build Plan Scaffolding** *(opens Phase 2 per ROADMAP.md.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (32 ADRs after S-0012 — 31 Accepted + 1 Superseded) is the contract layer. The personal-project disposition per [ADR 0032](adr/0032-personal-project-disposition.md) shapes every per-session contract scaffolded in S-0013.

S-0013 produces the `build_plan/` directory naming the chunked authoring sessions for Phases 3–9. Per [ROADMAP.md](ROADMAP.md) Phase 2:

- `build_plan/MANIFEST.md` — orientation, session schedule, phase mapping
- `build_plan/00_preamble.md` — orienting prose
- `build_plan/00_session_schedule.md` — every session by ID with scope, source documents, output target, budget tier
- `build_plan/P_0_contract_lock.md` — retroactive Phase 1 record (ADR collection + Phase 1.1 / 1.2 / 1.3 / privacy ADRs / project-direction supersession)
- `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` — per-phase chunks (Phase 3 schema; Phase 4 graph validation; Phase 4.5 input dataset survey; Phase 5 seed graph build with subdomain sub-sessions per ROADMAP §5.1; Phase 6 self-correction; Phase 7 Sonnet teaching layer; Phase DEC.1 retrieval / mastery-inference architecture decisions; Phase 8 evaluation harness; Phase 9 UI prototype)

The per-phase chunks should reflect the simplifications committed at S-0012:

- Phase 4.5 license-tier framing (consultable for personal use is the operative bucket; ingestable-for-commercial-use framing dropped)
- Phase 8 simplified scope (stock-Sonnet-without-rendering-policy baseline + small private TestFlight cohort cold-test; external-rubric and DeepTutor-head-to-head dropped)
- Phase 9 iOS-only-native + delete-account / data-export / exit-affordance UI primitives + static-polish discipline + dynamic-feature foreclosure

The chunks should *not* re-include institutional / cohort / LMS / FERPA / grant / acquisition framing — those are foreclosed by [ADR 0032](adr/0032-personal-project-disposition.md) and any proposal to reopen requires a superseding ADR, not per-session re-litigation.

### Source documents (read at S-0013 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — Phase 2 scope; Phase 3–9 success criteria for the per-phase chunk authoring.
- [`adr/0032-personal-project-disposition.md`](adr/0032-personal-project-disposition.md) — the disposition that shapes every per-session contract.
- [`adr/0031-erasure-mechanism-and-individual-only-regime.md`](adr/0031-erasure-mechanism-and-individual-only-regime.md) — Phase 3 cascade discipline; Phase 9 delete-account affordance.
- [`docs/business.md`](docs/business.md) — Pricing and Distribution + Operating Cost Model (informs Phase 8 cost-cap parameter shape and Phase 9 IAP wiring).
- [`docs/MISSION.md`](docs/MISSION.md) — strong working commitments (commitment 2 now reframed; commitments 1 + 3–12 unchanged).
- [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md) — phase-boundary checks per phase.

### After S-0013

Phase 2 closes when `build_plan/` is populated and per-phase chunks reflect the simplifications listed above. Phase 3 (SQL Schema Implementation) opens after S-0013 — the first phase that produces deployed Postgres schema with `ON DELETE CASCADE` discipline per [ADR 0031](adr/0031-erasure-mechanism-and-individual-only-regime.md) and the `confidence_level` column per [ADR 0030](adr/0030-confidence-level-evidentiary-mode-on-nodes.md). The four tensions opened in S-0008 land at later phase boundaries: OQ-WALL-BEHAVIOR at Phase 8 cost-cap wiring (now in single-tier form per S-0012), OQ-CONTEXT-COMPRESSION at Phase 7, OQ-PEDAGOGY-INFERENCE-LOCUS at the registry-size revisit trigger. Sessions 12–14 of the prompt pack remain deferred. Phase 4.5 input dataset survey is queued between Phase 4 and Phase 5.

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

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema); ADR 0031 added in S-0011 (erasure mechanism — hard-delete with cascade — and individual-only data regime); ADR 0032 added in S-0012 (personal project disposition; refusal-not-deferral commercial closure; supersedes ADR 0002). **Final Phase 1 ADR count: 32 ADRs total — 31 Accepted plus 1 Superseded** (ADR 0002 by ADR 0032).
