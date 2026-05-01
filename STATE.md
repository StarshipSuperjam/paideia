# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012** (§1.1 across S-0004 / S-0005 / S-0006; privacy-posture insertion at S-0007; §1.2 at S-0008; Phase 4.5 input-dataset-survey scaffolding at S-0009; §1.3 at S-0010; privacy ADRs collapsed at S-0011 with ADR 0031; project-direction supersession at S-0012 with ADR 0032 superseding ADR 0002). **Phase 1.5 — Mission Realignment Overhaul fully closed at S-0021** (Phase 1.5.1 at S-0013 with [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md); Phase 1.5.2 at S-0014 with [ADR 0034](adr/0034-discovery-planning-engagement-triad.md); Phase 1.5.3 at S-0015 with [ADR 0035](adr/0035-multi-platform-apple-expansion.md); Phase 1.5.4 at S-0016 with [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) forbidden-token enumeration extended; Phase 1.5.5 opened at S-0017 with [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) and operational surface [`docs/operations/document-voice.md`](docs/operations/document-voice.md); mechanical-sweep cleanup at S-0018 across seven offender files; Tier 1 machinery hardening at S-0019; Tier 2 machinery hardening at S-0020; ROADMAP.md substantive cleanup at S-0021 closing Phase 1.5.5 and Phase 1.5). The four-layer trace system (ADRs / ENGINE_LOG / MemPalace / git) carries the production trace; governed body prose no longer duplicates it. Phase 1.5 was realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **S-0022 is the Phase 1.5 → Phase 2 bridge:** [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) commits to the engine / product wall and renames `CHANGELOG.md` → `ENGINE_LOG.md` (the `CHANGELOG.md` filename is reserved for the future learner-visible product release log; first entry at Phase 9). **Phase 2 (Build Plan Scaffolding) opens at S-0023** with the engine / product partition committed-to as input — `build_plan/P_*.md` chunks reference partition-aware paths from the start so the post-Phase-2 mechanical migration needs zero edits to them. |
| **Last build session** | S-0022 (2026-05-01) — **Engine / product wall commitment + CHANGELOG → ENGINE_LOG rename per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md).** The session closes the conflation between Paideia-the-product and the AI build apparatus the user and Claude run together to construct it. Two coupled decisions land in one ADR. **(a) Rename:** `git mv CHANGELOG.md ENGINE_LOG.md`; `ENGINE_LOG.md` carries the dated narrative for material engine changes (the third layer of [ADR 0036](adr/0036-expression-contract-for-inward-documents.md)'s four-layer trace system); the `CHANGELOG.md` filename is reserved for the future learner-visible product release log (first entry at Phase 9 release prep). The session-by-session entry history (S-0002 → S-0021) is preserved verbatim in `ENGINE_LOG.md`'s body — the rename is filename + preamble + title only. **(b) Hard-wall commitment:** ADR 0037 names the proposed `engine/` vs `product/` repo partition with a target shape (`engine/operations/`, `engine/tools/`, `engine/session/`, `engine/adr/`, `engine/ENGINE_LOG.md`, `engine/STATE.md`, `engine/CLAUDE.md`; `product/adr/`, `product/docs/`, `product/seed-graph/`, `product/AGENT_INSTRUCTIONS.md`, `product/CHANGELOG.md`; `ROADMAP.md` and `README.md` stay at root). Trigger window: after Phase 2 close at S-0023 close; before Phase 5 seed-graph build opens. Phase 5 product content is the partition's first content load-test. Phase 2 (S-0023) authors `build_plan/P_*.md` chunks against partition-aware paths so when the migration lands the chunks need zero edits. Cross-reference updates landed in this session: [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) light-revised (four-layer system reference + new Consequences bullet citing ADR 0037; Status remains Accepted); [`tools/validate.py`](tools/validate.py) `changelog_format` check renamed to `engine_log_format` (path + soft-warn message); [`docs/operations/session-shutdown-sequence.md`](docs/operations/session-shutdown-sequence.md) step 4 heading + body updated; [`docs/operations/tools-validate-interpretation.md`](docs/operations/tools-validate-interpretation.md), [`docs/operations/adr-authoring.md`](docs/operations/adr-authoring.md), [`docs/operations/mempalace-tagging-conventions.md`](docs/operations/mempalace-tagging-conventions.md), [`docs/operations/document-voice.md`](docs/operations/document-voice.md), [`docs/operations/README.md`](docs/operations/README.md), [`docs/operations/health-check.md`](docs/operations/health-check.md), [`docs/operations/seed-chunked-authoring.md`](docs/operations/seed-chunked-authoring.md), [`docs/operations/mempalace-operations.md`](docs/operations/mempalace-operations.md) all updated. STATE.md, CLAUDE.md, ROADMAP.md (with new `[ENGINE]` / `[PRODUCT]` phase markers as the first installment of the partition), README.md, HANDOFF.md, [`adr/README.md`](adr/README.md) (new ADR 0037 row, ADR count → 37), [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md), [`docs/tensions.md`](docs/tensions.md), other ADRs (0016, 0022, 0027, 0032, 0036) all updated. MemPalace `decision` drawer paired with ADR 0037 records the conversational reasoning (CHANGELOG-as-conflation diagnosis, four-layer-system pushback, cost-projection at Phase 9, sequenced-execution rationale, Engine-over-Machinery vocabulary correction). `tools/validate.py` clean. |

| **Prior build session** | S-0021 (2026-05-01) — **ROADMAP.md substantive cleanup; Phase 1.5.5 and Phase 1.5 close.** [`ROADMAP.md`](ROADMAP.md) reauthored under [ADR 0036](adr/0036-expression-contract-for-inward-documents.md)'s three-speech-acts handling per [`docs/operations/document-voice.md`](docs/operations/document-voice.md): phase scope, output, success criteria, and the cross-phase strong working commitments list survive at present-state voice; per-phase date-stamp markers, supersession narration, and per-assertion ADR parentheticals migrated to ENGINE_LOG and git. Phase 1.5.5 + Phase 1.5 close at S-0021 close. (Full per-section breakdown lives in `ENGINE_LOG.md`'s S-0021 entry.) |

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

**S-0023 — Phase 2 (Build Plan Scaffolding) opens.** Phase 1.5 closed at S-0021; the engine / product wall and CHANGELOG → ENGINE_LOG rename landed at S-0022 per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md). The realigned, voice-clean contract layer plus the partition commitment are the input. Phase 2 authors the `build_plan/` directory naming the chunked authoring sessions for Phases 3–9 plus the per-session working contract.

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot.

### The work

Phase 2's deliverable per [`ROADMAP.md`](ROADMAP.md):

- `build_plan/MANIFEST.md` — orientation, session schedule, phase mapping
- `build_plan/00_preamble.md` — orienting prose
- `build_plan/00_session_schedule.md` — every session by ID with scope, source documents, output target, budget tier
- `build_plan/P_0_contract_lock.md` — retroactive Phase 1 record
- `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` — per-phase chunks for Phases 3–9 (the prefix `P_N` mapping to ROADMAP phases will be settled at S-0023 boot — the original Phase 2 plan from S-0001 named eight per-phase files; the Phase 1.5 realignment may shift the chunking).

ROADMAP.md is the high-level arc; `build_plan/` is the per-session work within each phase. Once Phase 2 lands, every downstream session boots from a per-phase build_plan chunk plus STATE.md plus MemPalace, and the build_plan chunk names the per-session contract (scope, sources, output, success criteria) so the next session does not re-derive its own scope.

**Critical constraint per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md):** `build_plan/P_*.md` chunks reference **partition-aware paths** even though the `engine/` and `product/` subtrees do not yet exist. Phase 5 outputs reference `product/seed-graph/...`; validator references go to `engine/tools/validate.py`; operations docs reference `engine/operations/...`. The partition itself doesn't exist when Phase 2 runs; the chunks anticipate it so when the post-Phase-2 mechanical migration lands the chunks need zero edits. This is the load-bearing reason for landing ADR 0037 at S-0022 ahead of Phase 2 rather than after.

### Source documents (read at S-0023 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`ROADMAP.md`](ROADMAP.md) — the high-level arc the build_plan chunks instantiate; especially Phase 2 (the deliverable) and Phases 3–9 (what each chunk must scope). Phase headings carry `[ENGINE]` / `[PRODUCT]` markers per ADR 0037.
- [`adr/0037-engine-product-wall-and-changelog-rename.md`](adr/0037-engine-product-wall-and-changelog-rename.md) — the partition shape that `build_plan/P_*.md` chunks reference.
- [`docs/operations/document-voice.md`](docs/operations/document-voice.md) — the inward-document expression contract; build_plan files are governed.
- [`adr/0036-expression-contract-for-inward-documents.md`](adr/0036-expression-contract-for-inward-documents.md) — the ADR establishing the inward-voice contract.
- [`docs/operations/session-build-lifecycle.md`](docs/operations/session-build-lifecycle.md) and [`docs/operations/session-shutdown-sequence.md`](docs/operations/session-shutdown-sequence.md) — the per-session protocol the build_plan chunks must align with.
- [`adr/README.md`](adr/README.md) — the contract layer Phase 2 consumes; per-session contracts cite the load-bearing ADRs by reference.

### Success criteria (S-0023)

- `build_plan/MANIFEST.md`, `build_plan/00_preamble.md`, `build_plan/00_session_schedule.md`, `build_plan/P_0_contract_lock.md`, and the per-phase chunks (`build_plan/P_1_*.md` through `build_plan/P_13_*.md` or whatever final numbering the chunking settles on) all exist with non-stub content.
- Each per-phase chunk names: phase scope, output, success criteria, source documents, load-bearing ADRs, estimated context budget. The shape mirrors STATE.md's `## Next session work item` block — a future session boots from the chunk and knows what it's doing without re-deriving from history.
- **Each chunk's path references are partition-aware** (e.g., `product/seed-graph/...`, `engine/tools/validate.py`) per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md), even though the partition directories do not yet exist.
- `tools/validate.py` clean (0 hard-fails); soft-warns acceptable.
- ENGINE_LOG entry under `[Unreleased]` for S-0023 (Added for the new build_plan/ tree).
- STATE.md updated with S-0024 next-session work item (the first per-phase chunk to consume, or the post-Phase-2 mechanical migration if that's the next-priority work item).
- Phase 2 closes at S-0023 close.

### Estimated context budget (S-0023)

~70% target / 80% cap (mechanical/procedural tier per CLAUDE.md — the work is generating the chunked file tree against a known shape, not re-extracting substantive design decisions). Watch for context-amplification if Phase 2 ends up needing to read every load-bearing ADR for every per-phase chunk; if budget pressure surfaces, halt at the next sensible boundary, write `outcome_summary` with partial-completion notes, archive `current.json` with `status: closed_partial`, and S-0024 picks up the remaining chunks.

### After S-0023

The next-priority queued work item after Phase 2 closes is the **mechanical engine / product folder migration** per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) — one or two sessions of `git mv` plus cross-reference updates to land the partition shape committed in ADR 0037. Phase 5 seed-graph authoring (the partition's content load-test) sits downstream of the migration. The first per-phase build session (S-0025+ depending on the migration's session count) opens against the corresponding `build_plan/P_*.md` chunk. The boundary between *project setup* (Phases 0, 1, 1.5, 2 + the migration) and *project build* (Phases 3 onward) is the partition itself.

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

**ADR count post-S-0022: 37 ADRs total — 35 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035). The contract layer Phase 2 (Build Plan Scaffolding) consumes. The session-by-session accumulation of the count across S-0003 → S-0022 lives in ENGINE_LOG and `adr/README.md`'s per-phase tables; [`tools/validate.py`](tools/validate.py)'s `adr_index_consistency` check (per S-0020) audits the ADR-file-vs-index alignment.
