# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); **Phase 1 — Contract Lock fully closed at S-0012** (§1.1 across S-0004 / S-0005 / S-0006; privacy-posture insertion at S-0007; §1.2 at S-0008; Phase 4.5 input-dataset-survey scaffolding at S-0009; §1.3 at S-0010; privacy ADRs collapsed at S-0011 with ADR 0031; project-direction supersession at S-0012 with ADR 0032 superseding ADR 0002). **Phase 1.5 — Mission Realignment Overhaul fully closed at S-0021** (Phase 1.5.1 at S-0013 with [ADR 0033](../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md); Phase 1.5.2 at S-0014 with [ADR 0034](../product/adr/0034-discovery-planning-engagement-triad.md); Phase 1.5.3 at S-0015 with [ADR 0035](../product/adr/0035-multi-platform-apple-expansion.md); Phase 1.5.4 at S-0016 with [ADR 0027](../product/adr/0027-rendering-policy-prompt-layer-contract.md) forbidden-token enumeration extended; Phase 1.5.5 opened at S-0017 with [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) and operational surface [`docs/operations/document-voice.md`](operations/document-voice.md); mechanical-sweep cleanup at S-0018 across seven offender files; Tier 1 machinery hardening at S-0019; Tier 2 machinery hardening at S-0020; ROADMAP.md substantive cleanup at S-0021 closing Phase 1.5.5 and Phase 1.5). The four-layer trace system (ADRs / ENGINE_LOG / MemPalace / git) carries the production trace; governed body prose no longer duplicates it. Phase 1.5 was realignment, not rebuild — the pedagogical dependency graph, AI instructor model, BYOB close reading, mastery model, privacy posture, cost ceiling all survive intact. **S-0022 was the Phase 1.5 → Phase 2 bridge:** [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) committed to the engine / product wall and renamed `CHANGELOG.md` → `ENGINE_LOG.md` (the `CHANGELOG.md` filename reserved for the future learner-visible product release log; first entry at Phase 9). **Phase 2 (Build Plan Scaffolding) closed at S-0023** with the [`build_plan/`](../build_plan/) tree authored against partition-aware paths. **S-0024 executed the engine/product folder migration** per [`build_plan/M_partition_migration.md`](../build_plan/M_partition_migration.md): tree restructured into `engine/` and `product/` subtrees (4 engine ADRs vs 33 product ADRs, plus operations/tools/session/STATE/ENGINE_LOG into engine/, docs/AGENT_INSTRUCTIONS/CHANGELOG into product/); CLAUDE.md stays at root per the in-session light-revision to ADR 0037's edge-case (c). Tree boots, commits, and validates clean (0 hard-fails); S-0025 sweeps the 15 cross-reference soft-warns. |
| **Last build session** | S-0024 (2026-05-02) — **Engine/product folder migration per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md), structural batch.** Executed the partition committed at S-0022. Tree restructures into `engine/` (the AI build apparatus: `engine/operations/`, `engine/tools/`, `engine/session/`, `engine/adr/`, `engine/STATE.md`, `engine/ENGINE_LOG.md`) and `product/` (Paideia-the-product: `product/adr/`, `product/docs/`, `product/AGENT_INSTRUCTIONS.md`, `product/CHANGELOG.md`). `CLAUDE.md` stays at root per a light-revision to ADR 0037's edge-case (c) settled in-session — Claude Code's auto-load walks ancestor directories from cwd UP, not into subdirectories, so a naive `engine/CLAUDE.md` would break the boot ceremony; the same rationale `.claude/` already had ("Claude Code expects it there") extends to `CLAUDE.md`. The previously-enumerated mitigations (root symlink, thin pointer, `cd engine/` at boot, `@engine/CLAUDE.md` import) are obviated by staying at root. ADR partition decision: 4 engine ADRs (0016 graph validation, 0022 health checks, 0036 inward-voice contract, 0037 the partition itself); 33 product ADRs (everything else). Auxiliary updates: `engine/tools/validate.py` constants rebased (REPO_ROOT depth +1, REQUIRED_TOP_LEVEL slim to root-only files plus CLAUDE.md, new REQUIRED_ENGINE_FILES list, ADR check iterates both subtrees with per-subtree README.md indexes); `engine/tools/hooks/pre-commit` paths and exploration-mode allowed paths updated; `engine/tools/hooks/mempalace-hook-wrapper.sh` fallback REPO_ROOT walk extended one level; `engine/tools/setup.sh` HOOK_SOURCE updated; `.claude/settings.json` hook commands prefixed with `engine/`; `.git/hooks/pre-commit` symlink retargeted to `../../engine/tools/hooks/pre-commit`; `CLAUDE.md`, `README.md`, `.claude/commands/start-engine.md` rewritten for new paths; `engine/adr/README.md` authored fresh; `product/adr/README.md` rewritten removing the 4 engine ADRs from per-phase tables and adding inline pointers. Light-revisions to [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md) edge-case (c) and [`build_plan/M_partition_migration.md`](../build_plan/M_partition_migration.md) Risk #5 (committed as checkpoint A before the moves). `engine/tools/validate.py` clean (11 checks, 0 hard-fails) at session close; 15 `cross_reference_broken` soft-warns from `product/docs/CROSS_REFERENCES.md`'s relative-path geometry shifting one level deeper — explicit S-0025 work item. `supabase/` left at root: per [`build_plan/P_1_sql_schema.md`](../build_plan/P_1_sql_schema.md), Phase 3 SQL Schema settles its destination (likely `product/seed-graph/migrations/`) at that session, not pre-content. |

| **Prior build session** | S-0023 (2026-05-01) — **Phase 2 (Build Plan Scaffolding) close + bundled HANDOFF reserved-CHANGELOG-stub item.** The session authored the [`build_plan/`](../build_plan/) tree (14 files: orientation + per-phase chunks + bridge migration) against partition-aware paths per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md). Chunk-to-phase mapping: `P_0` Phase 1+1.5+2 retroactive; `M_partition_migration` engine/product folder migration bridge; `P_1` Phase 3 SQL schema; `P_2` Phase 4 graph validation utility; `P_3` Phase 4.5 input dataset survey; `P_4` Phase 5 seed graph build (per-subdomain sub-sessions enumerated inside one master chunk to keep budget tractable; the ROADMAP Phase 5 internal `P_3 Epistemology`–`P_9 Cross-domain pass` naming is repurposed as sub-session enumeration within `P_4`); `P_5` Phase DEC.1 retrieval/mastery decisions; `P_6` Phase 6 self-correction pipeline; `P_7` Phase 7 Sonnet teaching layer; `P_8` Phase 8 evaluation harness + Apple Developer enrollment + cost-cap test + private TestFlight cold-test; `P_9` Phase 9 UI prototype. Each chunk carries: phase scope, output, success criteria, source documents, load-bearing ADRs, estimated context budget, session sequencing, open tensions consumed. The bundled HANDOFF item created [`CHANGELOG.md`](../product/CHANGELOG.md) at root with the reserved-stub preamble (no `[Unreleased]` section; first entry lands at Phase 9 release prep with v1.0.0); [`ENGINE_LOG.md`](ENGINE_LOG.md)'s preamble light-revised to point at the stub instead of naming the absence as the signal. `tools/validate.py` clean (10 checks, 0 hard-fails, 0 soft-warns) at session close. |

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

**S-0025 — Engine/product migration cross-reference sweep (continuation of S-0024).** S-0024 landed the structural moves; the tree boots, commits, and validates with 0 hard-fails. 15 `cross_reference_broken` soft-warns remain — all from `product/docs/CROSS_REFERENCES.md`'s relative-path geometry shifting one level deeper post-partition. S-0025 closes those and sweeps for stale references in the broader migrated tree.

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded from root (per ADR 0037 edge-case (c) settled at S-0024); MemPalace `mempalace_search` is queryable from boot. After `CLAUDE.md` and `engine/STATE.md`, boot reads [`build_plan/M_partition_migration.md`](../build_plan/M_partition_migration.md) for the migration contract context.

### The work

- **Cross-reference sweep across the migrated tree.** Every `[label](relative-path.md)` markdown link in moved files needs verification; rewrite where the relative-path geometry changed. Particular attention to:
  - [`product/docs/CROSS_REFERENCES.md`](../product/docs/CROSS_REFERENCES.md) — the load-bearing offender (15 soft-warns at S-0024 close). Its relative-path links to `../STATE.md`, `../ROADMAP.md`, `../adr/...`, `operations/...` all need rebasing for `product/docs/` depth.
  - Engine ADRs (`engine/adr/0016`, `0022`, `0036`, `0037`) — their internal cross-references to other ADRs may need updates where the target moved across the partition (e.g., engine ADR → product ADR is now `../../product/adr/...`).
  - Product ADRs (`product/adr/0001`–`0035` minus the 4 engine) — same concern in the reverse direction; cross-references to engine artifacts need `../../engine/...`.
  - Engine operations docs (`engine/operations/*.md`) — internal links to other operations docs should resolve relatively (siblings, no path change), but links to ADRs, STATE, ENGINE_LOG, CROSS_REFERENCES need rebasing.
  - [`product/docs/tensions.md`](../product/docs/tensions.md), [`product/docs/MISSION.md`](../product/docs/MISSION.md), and other product/docs/*.md — their links to engine artifacts (operations, ADRs, STATE) and to root files (ROADMAP) need rebasing.
  - Build plan chunks (`build_plan/P_*.md`, `M_*.md`) — already partition-aware per ADR 0037, but verify by reading each. Stale references here are highest-leverage because downstream sessions read them cold.
  - HANDOFF.md — historical narrative, leave path references as-is (they reflect the path at the time the entry was written).
  - Existing engine archive entries (`engine/session/archive/S-NNNN.json`) — historical snapshots; do not retroactively update their `working_on`/`outcome_summary` strings.
- **`product/docs/CROSS_REFERENCES.md` asymmetry decision.** Currently indexes a flat tree; post-migration it lives under `product/docs/` but spans both subtrees. Decide in-session: stay product-side (per ADR 0037's `docs/` placement) or split into engine + product cross-reference indexes. ADR 0037 doesn't settle this — name the choice explicitly in `outcome_summary`.
- **Validator clean.** `engine/tools/validate.py` runs with 0 hard-fails AND 0 `cross_reference_broken` soft-warns at session close.

### Source documents (read at S-0025 boot beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](STATE.md) — this brief.
- [`build_plan/M_partition_migration.md`](../build_plan/M_partition_migration.md) — the migration contract; reread the Risks-and-Mitigations section.
- [`engine/adr/0037-engine-product-wall-and-changelog-rename.md`](adr/0037-engine-product-wall-and-changelog-rename.md) — the partition shape (light-revised at S-0024 to fold CLAUDE.md into edge-case (c)).
- [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) S-0024 entry — full enumeration of what moved and what was updated; the diff target for the sweep.
- [`product/docs/CROSS_REFERENCES.md`](../product/docs/CROSS_REFERENCES.md) — the file most in need of repair.
- [`engine/operations/tools-validate-interpretation.md`](operations/tools-validate-interpretation.md) — for the `cross_reference_broken` soft-warn category semantics.

### Success criteria (S-0025)

- `engine/tools/validate.py` clean: 0 hard-fails AND 0 soft-warns (the 15 `cross_reference_broken` warnings from S-0024 close at zero).
- All migrated docs' markdown links resolve when read from their new locations.
- `product/docs/CROSS_REFERENCES.md` asymmetry decision recorded in `outcome_summary` (stay-or-split named explicitly).
- ENGINE_LOG entry under `[Unreleased]` → `Changed` enumerating the cross-reference sweep scope.

### Estimated context budget (S-0025)

~60% target / 70% cap (mechanical/procedural tier; the work is find-and-replace plus per-file verification, with one judgment call on CROSS_REFERENCES.md asymmetry). The sweep is bounded by the file count rather than substantive complexity.

### After S-0025

The engine/product partition is fully closed. The next-priority queued work item is **Phase 3 — SQL Schema Implementation** per [`build_plan/P_1_sql_schema.md`](../build_plan/P_1_sql_schema.md). Schema lands under `product/seed-graph/migrations/` (or as decided in `P_1`; the `supabase/` placeholder at root migrates to its destination at that session); deployment target is the `paideia-dev` Supabase project.

The boundary between *project setup* (Phases 0, 1, 1.5, 2 + the migration) and *project build* (Phases 3 onward) is the partition itself, now structurally complete.

## Open tensions and deferred decisions

See [`product/docs/tensions.md`](../product/docs/tensions.md). As of S-0024 close, the OQ-prefixed active set is 9 items (OQ-PRIVACY-A and OQ-PRIVACY-B closed by ADR 0031; OQ-PHASE8-A settled by ADR 0032; OQ-BYOK-REGIME withdrawn by ADR 0032; OQ-OUTWARD-VOICE added at S-0019):

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- **OQ-WALL-BEHAVIOR** (added S-0008, per ADR 0029; simplified S-0012) — soft-wall degradation ladder at cost cap; **single-tier ladder** under cost-priced subscription model (free-vs-paid tier-shaped framing collapsed at S-0012); four candidate steps remain (model downshift, retrieval shrink, concept-engagement length cap, soft refusal); decide-before Phase 8 cost-cap wiring
- **OQ-CONTEXT-COMPRESSION** (added S-0008, per ADR 0029; unaffected by S-0012) — token-amplification mitigation for multi-turn engagements (structured-state replacement + automatic compression + explicit summarization candidates); decide-before Phase 7
- **OQ-PEDAGOGY-INFERENCE-LOCUS** (added S-0008, tagged `watch`) — rule layer vs. distributed inference; revisit when inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR an operational complaint surfaces
- **OQ-OUTWARD-VOICE** (added S-0019) — third expression-contract gap covering outward product surfaces (UI labels, button text, error messages, learner-facing help, public README, App Store description, learner-visible CHANGELOG entries) that neither ADR 0027 nor ADR 0036 governs; decide-before Phase 7 (the earliest plausible moment such a surface ships)
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs** — the contract layer, now split across [`engine/adr/`](adr/) (4 engine ADRs about the build apparatus) and [`product/adr/`](../product/adr/) (33 product ADRs about Paideia-as-product). The audience-facing summary lives in [`product/docs/MISSION.md`](../product/docs/MISSION.md) (commitments 1–12 with ADR cross-refs; commitment 2 reframed at S-0012 as "operating discipline must not corrupt pedagogy" per ADR 0032); the canonical list with ADR pointers lives in [`ROADMAP.md`](../ROADMAP.md) ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

**ADR count post-S-0024: 37 ADRs total — 35 Accepted plus 2 Superseded** (ADR 0002 by ADR 0032; ADR 0032 by ADR 0035), partitioned into 4 engine + 33 product per [ADR 0037](adr/0037-engine-product-wall-and-changelog-rename.md). The contract layer the [`build_plan/`](../build_plan/) chunks consume by reference. [`engine/tools/validate.py`](tools/validate.py)'s `adr_index_consistency` check (refactored at S-0024 to iterate both subtree READMEs) audits the ADR-file-vs-index alignment.
