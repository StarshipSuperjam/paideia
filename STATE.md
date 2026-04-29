# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 fully closed at S-0008 (rendering policy + input-side scope + personal financial cost ceiling); Phase 4.5 input-dataset-survey scaffolding landed at S-0009 (out-of-phase scope expansion absorbed from Önduygu philo-browser exploration per the no-silent-drops rule). §1.3 (`confidence_level` column) and the OQ-PRIVACY-A / OQ-PRIVACY-B decision sessions remain to close Phase 1. |
| **Last build session** | S-0009 (2026-04-29) — out-of-phase scope expansion absorbed from exploration. **ROADMAP.md** gains new **Phase 4.5 (Input Dataset Survey for Phase 5 Seed Authoring)** between Phase 4 (validation utility) and Phase 5 (seed graph build): five usability axes (graph-shape orientation, license, form, coverage breadth, depth uniformity); tiered survey scope (Tier 1 exhaustive on prerequisite-shaped graphs, Tier 2 comprehensive on per-domain cross-reference inventories outside philosophy, Tier 3 representative on bibliographies/citation graphs, Tier 4 minimal on long-form prose already parametrically accessible); Önduygu philo-browser worked example (propositions+edges layer graph-shape-incompatible and consciously not consulted; tag layer + reference list + author's caveat are usable); Phase 4.5 success criteria; scope discipline (research-and-recording, not commitment; specific adoption decisions defer to Phase 5 sessions). **docs/content-strategy.md** gains **Cross-Domain Reference Inventories — Survey** section that operationalizes Phase 4.5 (five axes with three-bucket license distinction; tiered scope mirrored; Önduygu worked example expanded with usable layers ranked; per-candidate assessment template). **docs/tensions.md** Multi-Domain Expansion tension partially addressed (per-domain inventory sub-question forcing-functioned by Phase 4.5 Tier 2). Two MemPalace `exploration` drawers filed (Önduygu assessment + five usability axes). The new phase **does not** revise "Generative Graph Independence" (`business.md`) or the SEP-as-structural-reference posture (`content-strategy.md`); the survey targets cross-reference inventories and prerequisite-shape priors, not corpus dependencies. `tools/validate.py` clean. |
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

**S-0010 — Phase 1.3: `confidence_level` column on node schema** *(closes Phase 1; Phase 1.2 closed at S-0008; Phase 4.5 scaffolding landed out-of-phase at S-0009.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (29 ADRs) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

Phase 1.2 closed at S-0008. S-0009 absorbed an out-of-phase scope expansion from exploration (Önduygu philo-browser converged on the need for a tiered input-dataset survey before Phase 5 seed authoring); the new ROADMAP Phase 4.5 + `docs/content-strategy.md` Cross-Domain Reference Inventories survey scaffolding + two MemPalace `exploration` drawers landed without revising any settled commitment.

Phase 1.3 adds a single column to the node schema: `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`), orthogonal to the existing `provenance` field and the numeric `confidence` value. Synthetic nodes are first candidates for self-correction review (per [`docs/self-correction.md`](docs/self-correction.md)). The column is declared in [`docs/architecture.md`](docs/architecture.md) (Node Schema), shipped in the Phase 3 SQL migration, and consumed by [`tools/validate.py`](tools/validate.py)'s Phase 4 graph audit (per [ROADMAP.md](ROADMAP.md) Phase 4 soft-warn category — "`confidence_level: SYNTHETIC` nodes flagged for review queue").

Source documents:
- [`docs/architecture.md`](docs/architecture.md) Node Schema (extension target).
- [ROADMAP.md](ROADMAP.md) Phase 1.3 (the spec); Phase 4 (the consumer in the graph audit); Phase 5 (seed-graph authoring sets `confidence_level: INTERPRETED` until validated).
- [ADR 0016](adr/0016-graph-construction-needs-live-validation.md) (the live-validation discipline this column feeds).

Scope (S-0010):
- Add `confidence_level` to the Node Schema in [`docs/architecture.md`](docs/architecture.md) with explicit semantics for each enum value.
- Cross-link from [`docs/self-correction.md`](docs/self-correction.md) (synthetic nodes as first review candidates) and [ROADMAP.md](ROADMAP.md) Phase 4 (the soft-warn integration).
- Whether an ADR is warranted is a judgment call: the column is a small schema addition that fits naturally under the broader graph-validation discipline of [ADR 0016](adr/0016-graph-construction-needs-live-validation.md). If the enum semantics or the synthetic-review pipeline implications require recording a tradeoff, author ADR 0030. Otherwise, document in `docs/architecture.md` and note in CHANGELOG.

S-0010 success criteria: `confidence_level` column added to the Node Schema with enum semantics specified; cross-links updated; Phase 4 audit category alignment confirmed; `tools/validate.py` returns clean.

After S-0010: Phase 1 closes. The two open privacy questions (OQ-PRIVACY-A erasure mechanism, OQ-PRIVACY-B institutional regime) are decide-before-Phase 3 and need ADRs of their own before Phase 3 schema authoring begins — likely one session each. The four S-0008-opened tensions (OQ-BYOK-REGIME, OQ-WALL-BEHAVIOR, OQ-CONTEXT-COMPRESSION, OQ-PEDAGOGY-INFERENCE-LOCUS) sit at later phase boundaries (Phase 7, 8, 9). Sessions 12–14 of the prompt pack remain deferred (per [ROADMAP.md](ROADMAP.md) §1.1). Phase 4.5 (input dataset survey) is queued between Phase 4 and Phase 5 — per [ROADMAP.md](ROADMAP.md) Phase 4.5 — and may slot to a single dedicated session or fold into early Phase 5 sessions depending on the survey's eventual size.

## Open tensions and deferred decisions

See `docs/tensions.md`. As of S-0008 close, the active set includes 12 items:

- OQ-DEC1-A through D — Phase DEC.1 architecture decisions (server-side mastery, two-hop retrieval, embedding strategy, chunk-resolver vs URL pointers); decide-before Phase 6
- OQ-PHASE8-A — Phase 8 evaluation baseline choice; decide at Phase 8 entry
- **OQ-PRIVACY-A** (added S-0007, per ADR 0026) — erasure mechanism (crypto-shredding vs hard-delete-with-cascade vs anonymize-and-aggregate); decide-before Phase 3
- **OQ-PRIVACY-B** (added S-0007, per ADR 0026) — institutional vs individual data regime, direction-neutral; column reservation Phase 3, policy specification Phase 8
- **OQ-BYOK-REGIME** (added S-0008, per ADR 0029) — institutional vs. consumer BYOK; institutional preferred, consumer foreclosed unless future regime change justifies; decide-before any non-builder consumer launch
- **OQ-WALL-BEHAVIOR** (added S-0008, per ADR 0029) — soft-wall degradation ladder at cost cap (model downshift, retrieval shrink, bridge cap, length cap, soft refusal); decide-before Phase 8 cost-cap wiring
- **OQ-CONTEXT-COMPRESSION** (added S-0008, per ADR 0029) — token-amplification mitigation for multi-turn engagements (structured-state replacement + automatic compression + explicit summarization candidates); decide-before Phase 7
- **OQ-PEDAGOGY-INFERENCE-LOCUS** (added S-0008, tagged `watch`) — rule layer vs. distributed inference; revisit when inference registry crosses ~30 entries OR cross-domain edges per domain-pair exceed ~50 OR an operational complaint surfaces
- OQ-WATCH-FLAG-FILE (tagged `watch`) — separate watch-flag file consideration, surfaced at session-30 health check

## Paperclip integration

**Deferred.** Phase 5 trial / Phase 7 commit per ROADMAP.md. Not installed in Foundation.

## Strong working commitments

12 commitments inherited from pre-Foundation design plus 10 architectural decisions. **All 22 are recorded as ADRs in [`adr/`](adr/)** — the contract layer. The audience-facing summary lives in `docs/MISSION.md` (commitments 1–12 with ADR cross-refs); the canonical list with ADR pointers lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). The conversational story behind each decision is recoverable from MemPalace `decision`-tagged drawers.

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling). Total ADR count: 29.
