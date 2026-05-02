# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012** (§1.1 across S-0004 / S-0005 / S-0006; privacy-posture insertion at S-0007; §1.2 at S-0008; Phase 4.5 input-dataset-survey scaffolding at S-0009; §1.3 at S-0010; privacy ADRs collapsed at S-0011 with ADR 0031; project-direction supersession at S-0012 with ADR 0032 superseding ADR 0002). **Phase 1.5 — Mission Realignment Overhaul fully closed at S-0021** (Phase 1.5.1 at S-0013 with [ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md); Phase 1.5.2 at S-0014 with [ADR 0034](adr/0034-discovery-planning-engagement-triad.md); Phase 1.5.3 at S-0015 with [ADR 0035](adr/0035-multi-platform-apple-expansion.md); Phase 1.5.4 at S-0016 with [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) forbidden-token enumeration extended; Phase 1.5.5 opened at S-0017 with [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) and operational surface [`docs/operations/document-voice.md`](docs/operations/document-voice.md); mechanical-sweep cleanup at S-0018 across seven offender files; Tier 1 machinery hardening at S-0019; Tier 2 machinery hardening at S-0020; ROADMAP.md substantive cleanup at S-0021 closing Phase 1.5.5 and Phase 1.5). The four-layer trace system (ADRs / ENGINE_LOG / MemPalace / git) carries the production trace; governed body prose no longer duplicates it. Phase 1.5 was realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **S-0022 was the Phase 1.5 → Phase 2 bridge:** [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) committed to the engine / product wall and renamed `CHANGELOG.md` → `ENGINE_LOG.md` (the `CHANGELOG.md` filename reserved for the future learner-visible product release log; first entry at Phase 9). **Phase 2 (Build Plan Scaffolding) closed at S-0023** with the [`build_plan/`](build_plan/) tree authored against partition-aware paths per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) — 14 files: `MANIFEST.md`, `00_preamble.md`, `00_session_schedule.md`, `P_0_contract_lock.md` (retroactive), `M_partition_migration.md` (bridge), `P_1_sql_schema.md` through `P_9_ui_prototype.md` (per-phase chunks for Phases 3 / 4 / 4.5 / 5 / DEC.1 / 6 / 7 / 8 / 9). The HANDOFF reserved-CHANGELOG-stub item bundled at boot per its 10-minute scope: `CHANGELOG.md` exists at root with the reserved-stub preamble; `ENGINE_LOG.md`'s preamble light-revised to point at the stub instead of "the absence is the signal". **S-0024 opens with the engine / product folder migration** per [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md). |
| **Last build session** | S-0023 (2026-05-01) — **Phase 2 (Build Plan Scaffolding) close + bundled HANDOFF reserved-CHANGELOG-stub item.** The session authored the [`build_plan/`](build_plan/) tree (14 files: orientation + per-phase chunks + bridge migration) against partition-aware paths per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md). Chunk-to-phase mapping: `P_0` Phase 1+1.5+2 retroactive; `M_partition_migration` engine/product folder migration bridge; `P_1` Phase 3 SQL schema; `P_2` Phase 4 graph validation utility; `P_3` Phase 4.5 input dataset survey; `P_4` Phase 5 seed graph build (per-subdomain sub-sessions enumerated inside one master chunk to keep budget tractable; the ROADMAP Phase 5 internal `P_3 Epistemology`–`P_9 Cross-domain pass` naming is repurposed as sub-session enumeration within `P_4`); `P_5` Phase DEC.1 retrieval/mastery decisions; `P_6` Phase 6 self-correction pipeline; `P_7` Phase 7 Sonnet teaching layer; `P_8` Phase 8 evaluation harness + Apple Developer enrollment + cost-cap test + private TestFlight cold-test; `P_9` Phase 9 UI prototype. Each chunk carries: phase scope, output, success criteria, source documents, load-bearing ADRs, estimated context budget, session sequencing, open tensions consumed. The bundled HANDOFF item created [`CHANGELOG.md`](CHANGELOG.md) at root with the reserved-stub preamble (no `[Unreleased]` section; first entry lands at Phase 9 release prep with v1.0.0); [`ENGINE_LOG.md`](ENGINE_LOG.md)'s preamble light-revised to point at the stub instead of naming the absence as the signal. `tools/validate.py` clean (10 checks, 0 hard-fails, 0 soft-warns) at session close. |

| **Prior build session** | S-0022 (2026-05-01) — **Engine / product wall commitment + CHANGELOG → ENGINE_LOG rename per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md).** The session closes the conflation between Paideia-the-product and the AI build apparatus the user and Claude run together to construct it. Two coupled decisions land in one ADR. **(a) Rename:** `git mv CHANGELOG.md ENGINE_LOG.md`; `ENGINE_LOG.md` carries the dated narrative for material engine changes (the third layer of [ADR 0036](adr/0036-expression-contract-for-inward-documents.md)'s four-layer trace system); the `CHANGELOG.md` filename is reserved for the future learner-visible product release log (first entry at Phase 9 release prep). The session-by-session entry history (S-0002 → S-0021) is preserved verbatim in `ENGINE_LOG.md`'s body — the rename is filename + preamble + title only. **(b) Hard-wall commitment:** ADR 0037 names the proposed `engine/` vs `product/` repo partition with a target shape (`engine/operations/`, `engine/tools/`, `engine/session/`, `engine/adr/`, `engine/ENGINE_LOG.md`, `engine/STATE.md`, `engine/CLAUDE.md`; `product/adr/`, `product/docs/`, `product/seed-graph/`, `product/AGENT_INSTRUCTIONS.md`, `product/CHANGELOG.md`; `ROADMAP.md` and `README.md` stay at root). Trigger window: after Phase 2 close at S-0023 close; before Phase 5 seed-graph build opens. Phase 5 product content is the partition's first content load-test. Phase 2 (S-0023) authors `build_plan/P_*.md` chunks against partition-aware paths so when the migration lands the chunks need zero edits. Cross-reference updates landed in this session: [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) light-revised (four-layer system reference + new Consequences bullet citing ADR 0037; Status remains Accepted); [`tools/validate.py`](tools/validate.py) `changelog_format` check renamed to `engine_log_format` (path + soft-warn message); [`docs/operations/session-shutdown-sequence.md`](docs/operations/session-shutdown-sequence.md) step 4 heading + body updated; [`docs/operations/tools-validate-interpretation.md`](docs/operations/tools-validate-interpretation.md), [`docs/operations/adr-authoring.md`](docs/operations/adr-authoring.md), [`docs/operations/mempalace-tagging-conventions.md`](docs/operations/mempalace-tagging-conventions.md), [`docs/operations/document-voice.md`](docs/operations/document-voice.md), [`docs/operations/README.md`](docs/operations/README.md), [`docs/operations/health-check.md`](docs/operations/health-check.md), [`docs/operations/seed-chunked-authoring.md`](docs/operations/seed-chunked-authoring.md), [`docs/operations/mempalace-operations.md`](docs/operations/mempalace-operations.md) all updated. STATE.md, CLAUDE.md, ROADMAP.md (with new `[ENGINE]` / `[PRODUCT]` phase markers as the first installment of the partition), README.md, HANDOFF.md, [`adr/README.md`](adr/README.md) (new ADR 0037 row, ADR count → 37), [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md), [`docs/tensions.md`](docs/tensions.md), other ADRs (0016, 0022, 0027, 0032, 0036) all updated. MemPalace `decision` drawer paired with ADR 0037 records the conversational reasoning (CHANGELOG-as-conflation diagnosis, four-layer-system pushback, cost-projection at Phase 9, sequenced-execution rationale, Engine-over-Machinery vocabulary correction). `tools/validate.py` clean. |

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

**S-0024 — Engine / product folder migration per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md).** Phase 2 closed at S-0023 with the [`build_plan/`](build_plan/) tree authored against partition-aware paths. S-0024 executes the mechanical `git mv` plus cross-reference sweep that lands the `engine/` and `product/` subtrees per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md)'s shape. The per-session working contract for this work lives at [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md).

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot. After CLAUDE.md and STATE.md, the boot reads [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md) for the per-session contract.

### The work

Per [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md):

- `git mv` execution per the [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) target shape: `engine/operations/`, `engine/tools/`, `engine/session/`, `engine/adr/`, `engine/ENGINE_LOG.md`, `engine/STATE.md`, `engine/CLAUDE.md`; `product/adr/`, `product/docs/`, `product/AGENT_INSTRUCTIONS.md`, `product/CHANGELOG.md`. `ROADMAP.md`, `README.md`, `HANDOFF.md`, `SECURITY.md`, `LICENSE`, `.claude/`, `build_plan/` stay at root.
- ADR partition decision per the criterion enumerated in [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md): which of the 37 ADRs file under `engine/adr/` (about how the AI build apparatus works) vs `product/adr/` (about Paideia as a product). Decision documented in the session's `outcome_summary` plus an ENGINE_LOG entry under `Changed`.
- Cross-reference sweep across every migrated file. Particular attention to: pre-commit hook symlink (relative path retarget per S-0019 recovery procedure); capture-hook wrapper path in `.claude/settings.json`; `tools/validate.py` `REQUIRED_TOP_LEVEL` constants; `docs/CROSS_REFERENCES.md`; CLAUDE.md auto-load resolution mechanism (root pointer or `cd engine/` at boot).
- `engine/tools/validate.py` clean (0 hard-fails) at session close; `cross_reference_broken` soft-warn category at zero.

The chunk's "Risks and mitigations" section enumerates four specific failure modes (pre-commit hook break, capture hook misfire, validator constant break, CROSS_REFERENCES.md staleness) plus the per-mitigation procedure.

### Source documents (read at S-0024 boot beyond CLAUDE.md auto-load)

- [`STATE.md`](STATE.md) — this brief.
- [`build_plan/M_partition_migration.md`](build_plan/M_partition_migration.md) — the per-session contract.
- [`adr/0037-engine-product-wall-and-changelog-rename.md`](adr/0037-engine-product-wall-and-changelog-rename.md) — the partition shape.
- [`ROADMAP.md`](ROADMAP.md) — for `[ENGINE]` / `[PRODUCT]` phase markers as the reference distinction.
- [`docs/operations/session-build-lifecycle.md`](docs/operations/session-build-lifecycle.md) recovery section — for the pre-commit hook symlink retarget procedure.
- [`tools/validate.py`](tools/validate.py) — for the file path constants the migration updates.
- [`adr/README.md`](adr/README.md) — for the ADR index that splits across `engine/adr/README.md` and `product/adr/README.md`.

### Success criteria (S-0024)

- All `git mv` operations completed per the [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) target shape.
- ADR partition decision recorded for every ADR; both `engine/adr/README.md` and `product/adr/README.md` indexed.
- `engine/tools/validate.py` clean (0 hard-fails).
- `cross_reference_broken` soft-warn category at zero.
- Pre-commit hook fires correctly from the new path (verify with a no-op commit).
- Capture-hook wrapper logs OK on session events (verify by clearing `.claude/logs/mempalace-hook.log` and triggering a stop-hook).
- Claude Code auto-loads `CLAUDE.md` correctly from the new location (or via the chosen root-pointer mechanism).
- ENGINE_LOG entry under `[Unreleased]` for `Changed` enumerating the moves and reference updates.

### Estimated context budget (S-0024)

~70% target / 80% cap (mechanical/procedural tier per CLAUDE.md). The substantive judgment is the per-ADR partition; the rest is mechanical `git mv` plus find-and-replace. Two-session fallback: Session 1 lands ADR partition + `git mv` execution + top-level reference updates; Session 2 (S-0025) finishes the cross-reference sweep if budget pressure surfaces.

### After S-0024 (or S-0024 + S-0025 if split)

The migration closes the engine/product partition. The next-priority queued work item is **Phase 3 — SQL Schema Implementation** per [`build_plan/P_1_sql_schema.md`](build_plan/P_1_sql_schema.md). Schema lands under `product/seed-graph/migrations/` (or as decided in `P_1`); deployment target is the `paideia-dev` Supabase project.

The boundary between *project setup* (Phases 0, 1, 1.5, 2 + the migration) and *project build* (Phases 3 onward) is the partition itself.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0023 close, the OQ-prefixed active set is 9 items (OQ-PRIVACY-A and OQ-PRIVACY-B closed by ADR 0031; OQ-PHASE8-A settled by ADR 0032; OQ-BYOK-REGIME withdrawn by ADR 0032; OQ-OUTWARD-VOICE added at S-0019):

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

**ADR count post-S-0023: 37 ADRs total — 35 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035). The contract layer the [`build_plan/`](build_plan/) chunks consume by reference. The session-by-session accumulation of the count across S-0003 → S-0023 lives in ENGINE_LOG and `adr/README.md`'s per-phase tables; [`tools/validate.py`](tools/validate.py)'s `adr_index_consistency` check (per S-0020) audits the ADR-file-vs-index alignment. S-0024's [`M_partition_migration`](build_plan/M_partition_migration.md) settles the per-ADR engine/product subtree; both `engine/adr/README.md` and `product/adr/README.md` indexes land at S-0024 close.
