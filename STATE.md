# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012** (§1.1 across S-0004 / S-0005 / S-0006; privacy-posture insertion at S-0007; §1.2 at S-0008; Phase 4.5 input-dataset-survey scaffolding at S-0009; §1.3 at S-0010; privacy ADRs collapsed at S-0011 with ADR 0031; project-direction supersession at S-0012 with ADR 0032 superseding ADR 0002). **Phase 1.5 — Mission Realignment Overhaul fully closed at S-0021** (Phase 1.5.1 at S-0013 with [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md); Phase 1.5.2 at S-0014 with [ADR 0034](adr/0034-discovery-planning-engagement-triad.md); Phase 1.5.3 at S-0015 with [ADR 0035](adr/0035-multi-platform-apple-expansion.md); Phase 1.5.4 at S-0016 with [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) forbidden-token enumeration extended; Phase 1.5.5 opened at S-0017 with [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) and operational surface [`docs/operations/document-voice.md`](docs/operations/document-voice.md); mechanical-sweep cleanup at S-0018 across seven offender files; Tier 1 machinery hardening at S-0019; Tier 2 machinery hardening at S-0020; ROADMAP.md substantive cleanup at S-0021 closing Phase 1.5.5 and Phase 1.5). The four-layer trace system (ADRs / CHANGELOG / MemPalace / git) carries the production trace; governed body prose no longer duplicates it. Phase 1.5 was realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **Phase 2 (Build Plan Scaffolding) opens at S-0022** with hardened machinery and the stable inward-voice contract both as input. |
| **Last build session** | S-0021 (2026-05-01) — **ROADMAP.md substantive cleanup; Phase 1.5.5 and Phase 1.5 close.** The originally-scheduled ROADMAP.md cleanup landed here per the approved adversarial-analysis plan (Tier 1 + Tier 2 machinery hardening at S-0019/S-0020 ran first). [`ROADMAP.md`](ROADMAP.md) reauthored under [ADR 0036](adr/0036-expression-contract-for-inward-documents.md)'s three-speech-acts handling per [`docs/operations/document-voice.md`](docs/operations/document-voice.md): phase scope, output, success criteria, and the cross-phase strong working commitments list survive at present-state voice; per-phase date-stamp markers, supersession narration, and per-assertion ADR parentheticals migrate to CHANGELOG and git. Specifics: (a) §1.2 `**Revised: 2026-04-29 (S-0008 — ...)**` header marker dropped; per-bullet `[ADR NNNN](...)` parentheticals consolidated to a single end-of-section "See also" pointer; OQ-BYOK-REGIME line dropped (closed by foreclosure under [ADR 0032](adr/0032-personal-project-disposition.md)). (b) Phase 1.5 header marker dropped; the meta-procedural "**The realignment is recorded as a phase, not as scattered amendments**" paragraph dropped; subsection titles 1.5.1–1.5.4 lost their `(S-NNNN)` session-attribution suffixes; substance under each rewritten from plan-as-it-was form to present-state form ("ADR 0033 contracts the mission realignment ..."); new subsection 1.5.5 (Inward-document expression contract) authored to parallel the substance-organized form; **Phase 1.5 success criteria** rewritten with ADR-count delta lines dropped (adr/README.md per-phase tables and S-0020's `adr_index_consistency` check carry the audit) and the `git grep` zero-matches criterion preserved with present-state framing; **Phase 1.5 plan reference** subsection (absolute path to a private local plan file) dropped — phase closed; plan not actionable. (c) Phase 4.5 `**Added: 2026-04-29 (S-0009)**` header marker dropped; axis 2 (License) supersession narration about the prior tripartite distinction rewritten as the present-state "consultable for personal use is the operative bucket" assertion. (d) Phase 8 `**Substantially simplified: 2026-04-30 (S-0012 — per [ADR 0032] ...)**` header marker dropped; the full "prior three-candidate framing dropped under ADR 0032" supersession-narration paragraph dropped; output paragraph rewritten to assert directly what the evaluation does; per-bullet ADR parentheticals consolidated to end-of-section "See also" (ADRs 0026 / 0027 / 0029 / 0031 / 0035); trailing "*Note: OQ-BYOK-REGIME no longer gates Phase 8*" retraction dropped. (e) Phase 9 phase-level `**Substantially rewritten at S-0015 ...**` header marker dropped; success-criteria block-level `**Added: 2026-04-29 (S-0008); revised: ...; substantially rewritten: ...**` marker dropped; per-bullet ADR parentheticals (11 bullets, most multi-cited) consolidated to a single end-of-section "See also" block (ADRs 0007 / 0011 / 0018 / 0028 / 0029 / 0031 / 0033 / 0034 / 0035); supersession remnants removed throughout ("reframed at S-0012", "preserved unchanged through ADR 0035", "explicitly foreclosed by ADR 0033 and ADR 0034", "inherited from [ADR 0032]"); bullets now assert what is the case. (f) Strong working commitments: preamble shortened, commitment 2 supersession parenthetical reduced from "([ADR 0032], supersedes [ADR 0002]; supporting ADR 0029)" to "([ADR 0032]; supporting: [ADR 0029])" — the supersession chain lives in ADR Status fields and adr/README.md; bare-text ADR cites converted to live markdown links for navigability; architectural-decisions sub-list preamble shortened from a historical narrative to "Architectural decisions:". Spot-check pass surfaced one staleness fix unrelated to S-0021's primary scope but inside the same file: Phase 0 header `(in progress)` suffix stripped (Phase 0 closed at S-0003). `tools/validate.py` clean (0 hard-fails, 0 soft-warns). **Phase 1.5.5 + Phase 1.5 close at S-0021 close.** Phase 2 (Build Plan Scaffolding) opens at S-0022. |

| **Prior build session** | S-0020 (2026-05-01) — **Pre-Phase-2 machinery hardening (Tier 2 of approved adversarial-analysis plan).** Three opportunistic items bundled into a dedicated session bridging S-0019's Tier 1 hardening and S-0021's Phase 1.5.5 close. **A2 — MemPalace capture-hook wrapper** at [`tools/hooks/mempalace-hook-wrapper.sh`](tools/hooks/mempalace-hook-wrapper.sh) (tracked, executable; always exits 0 to harness; routes capture failures to `.claude/logs/mempalace-hook.log` per-clone; manual failure test verified) wired into `.claude/settings.json` Stop and PreCompact hooks; boot-recovery surfacing in `docs/operations/session-build-lifecycle.md`'s Recovery section. **B4 — ADR-index/file consistency validator extension** in [`tools/validate.py`](tools/validate.py) (tenth check `adr_index_consistency`, soft-warn under `adr_index_inconsistent` when an ADR file is missing from `adr/README.md`'s per-phase tables or its Status core keyword diverges; documented in [`docs/operations/tools-validate-interpretation.md`](docs/operations/tools-validate-interpretation.md)). **C4 — STATE.md backup-tag framing softened** from operational-fallback framing to historical-anchor framing. `tools/validate.py` clean at session close. |

| **Last commit on main** | (see `git log --oneline -1` on main) |
| **Backup tag** | `pre-foundation-v0.0.0` at commit `fa70b8c` — historical anchor (pre-machinery state; not an operational fallback target — file-level retrieval via `git show pre-foundation-v0.0.0:path` is the legitimate use). |

## Infrastructure

| Component | Value |
|---|---|
| **Supabase project** | `paideia-dev`, project ref `ozooosgnuzxqqypotlke`, PostgreSQL 17.6 |
| **Supabase MCP** | configured in `.mcp.json` (gitignored, contains PAT) |
| **MemPalace** | installed at `/Users/shanekidd/Library/Python/3.9/bin/`; MCP server `mempalace-mcp` configured in `.mcp.json`; wing `paideia` indexed at S-0002 (414 drawers across rooms `general` + `operations`); capture hooks wired in `.claude/settings.json` |
| **Python** | system Python 3.9.6 at `/usr/bin/python3`; user-scope packages at `/Users/shanekidd/Library/Python/3.9/bin/` |
| **Anthropic API** | env var `ANTHROPIC_API_KEY` set in local `.env` (gitignored) |

## Next session work item

**S-0022 — Phase 2 (Build Plan Scaffolding) opens.** Phase 1.5 closed at S-0021; the realigned, voice-clean contract layer is the input. Phase 2 authors the `build_plan/` directory naming the chunked authoring sessions for Phases 3–9 plus the per-session working contract.

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot.

### The work

Phase 2's deliverable per [`ROADMAP.md`](ROADMAP.md):

- `build_plan/MANIFEST.md` — orientation, session schedule, phase mapping
- `build_plan/00_preamble.md` — orienting prose
- `build_plan/00_session_schedule.md` — every session by ID with scope, source documents, output target, budget tier
- `build_plan/P_0_contract_lock.md` — retroactive Phase 1 record
- `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` — per-phase chunks for Phases 3–9 (the prefix `P_N` mapping to ROADMAP phases will be settled at S-0022 boot — the original Phase 2 plan from S-0001 named eight per-phase files; the Phase 1.5 realignment may shift the chunking).

ROADMAP.md is the high-level arc; `build_plan/` is the per-session work within each phase. Once Phase 2 lands, every downstream session boots from a per-phase build_plan chunk plus STATE.md plus MemPalace, and the build_plan chunk names the per-session contract (scope, sources, output, success criteria) so the next session does not re-derive its own scope.

### Source documents (read at S-0022 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — the high-level arc the build_plan chunks instantiate; especially Phase 2 (the deliverable) and Phases 3–9 (what each chunk must scope).
- [`docs/operations/document-voice.md`](docs/operations/document-voice.md) — the inward-document expression contract; build_plan files are governed.
- [`adr/0036-expression-contract-for-inward-documents.md`](adr/0036-expression-contract-for-inward-documents.md) — the ADR establishing the contract.
- [`docs/operations/session-build-lifecycle.md`](docs/operations/session-build-lifecycle.md) and [`docs/operations/session-shutdown-sequence.md`](docs/operations/session-shutdown-sequence.md) — the per-session protocol the build_plan chunks must align with.
- [`adr/README.md`](adr/README.md) — the contract layer Phase 2 consumes; per-session contracts cite the load-bearing ADRs by reference.

### Success criteria (S-0022)

- `build_plan/MANIFEST.md`, `build_plan/00_preamble.md`, `build_plan/00_session_schedule.md`, `build_plan/P_0_contract_lock.md`, and the per-phase chunks (`build_plan/P_1_*.md` through `build_plan/P_13_*.md` or whatever final numbering the chunking settles on) all exist with non-stub content.
- Each per-phase chunk names: phase scope, output, success criteria, source documents, load-bearing ADRs, estimated context budget. The shape mirrors STATE.md's `## Next session work item` block — a future session boots from the chunk and knows what it's doing without re-deriving from history.
- `tools/validate.py` clean (0 hard-fails); soft-warns acceptable.
- CHANGELOG entry under `[Unreleased]` for S-0022 (Added for the new build_plan/ tree).
- STATE.md updated with S-0023 next-session work item (the first per-phase chunk to consume; presumably P_3 Epistemology per the Phase 5 ordering, or the Phase 3 SQL schema work if the dependencies pull that earlier).
- Phase 2 closes at S-0022 close.

### Estimated context budget (S-0022)

~70% target / 80% cap (mechanical/procedural tier per CLAUDE.md — the work is generating the chunked file tree against a known shape, not re-extracting substantive design decisions). Watch for context-amplification if Phase 2 ends up needing to read every load-bearing ADR for every per-phase chunk; if budget pressure surfaces, halt at the next sensible boundary, write `outcome_summary` with partial-completion notes, archive `current.json` with `status: closed_partial`, and S-0023 picks up the remaining chunks.

### After S-0022

S-0023 opens the first per-phase build session against the corresponding `build_plan/P_*.md` chunk. The first concrete substantive work the project ships against the realigned contract layer plus the Phase 2 scaffolding — the boundary between *project setup* (Phases 0, 1, 1.5, 2) and *project build* (Phases 3 onward).

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0021 close, the OQ-prefixed active set is 9 items (OQ-PRIVACY-A and OQ-PRIVACY-B closed by ADR 0031; OQ-PHASE8-A settled by ADR 0032; OQ-BYOK-REGIME withdrawn by ADR 0032; OQ-OUTWARD-VOICE added at S-0019):

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- **OQ-WALL-BEHAVIOR** (added S-0008, per ADR 0029; simplified S-0012) — soft-wall degradation ladder at cost cap; **single-tier ladder** under cost-priced subscription model (free-vs-paid tier-shaped framing collapsed at S-0012); four candidate steps remain (model downshift, retrieval shrink, concept-engagement length cap, soft refusal); decide-before Phase 8 cost-cap wiring
- **OQ-CONTEXT-COMPRESSION** (added S-0008, per ADR 0029; unaffected by S-0012) — token-amplification mitigation for multi-turn engagements (structured-state replacement + automatic compression + explicit summarization candidates); decide-before Phase 7
- **OQ-PEDAGOGY-INFERENCE-LOCUS** (added S-0008, tagged `watch`) — rule layer vs. distributed inference; revisit when inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR an operational complaint surfaces
- **OQ-OUTWARD-VOICE** (added S-0019) — third expression-contract gap covering outward product surfaces (UI labels, button text, error messages, learner-facing help, public README, App Store description, learner-visible CHANGELOG entries) that neither ADR 0027 nor ADR 0036 governs; decide-before Phase 7 (the earliest plausible moment such a surface ships)
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs; commitment 2 reframed at S-0012 as "operating discipline must not corrupt pedagogy" per ADR 0032); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

**ADR count post-Phase-1.5: 36 ADRs total — 34 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035). The contract layer Phase 2 (Build Plan Scaffolding) consumes. The session-by-session accumulation of the count across S-0003 → S-0017 lives in CHANGELOG and `adr/README.md`'s per-phase tables; [`tools/validate.py`](tools/validate.py)'s `adr_index_consistency` check (per S-0020) audits the ADR-file-vs-index alignment.
