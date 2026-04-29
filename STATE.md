# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (in progress); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 fully closed at S-0008 (rendering policy + input-side scope + personal financial cost ceiling). §1.3 (`confidence_level` column) and the OQ-PRIVACY-A / OQ-PRIVACY-B decision sessions remain to close Phase 1. |
| **Last build session** | S-0008 (2026-04-29) — Phase 1.2 closure with three ADRs and substantial sibling work absorbed from exploration per the no-silent-drops feedback rule. **AGENT_INSTRUCTIONS.md** lands at repo root as the rendering-policy contract that ships verbatim as Sonnet's system prompt (Phase 7); eight sections including forbidden-token enumeration with per-category ADR rationale, surviving tokens, citation rules, uncertainty posture, scope discipline, tension-emission policy operationalizing ADR 0026, and a worked example that is the gradeable Phase 7 test artifact. **ADR 0027** (rendering policy as prompt-layer contract) commits the asymmetric-amendment discipline (additions cheap, removals require ADR). **ADR 0028** (input-side scope structural-not-prompt) commits the bidirectional input-output contract pairing with ADR 0027 — three bounded input contexts, purpose-not-topic discrimination, exit affordance UI primitive, "architectural-constraint-beats-prompt-guardrail" principle generalized as citable commitment. **ADR 0029** (personal financial cost ceiling) commits cost protection as a precondition (not a feature) for any non-builder access; soft-walls-degrade-don't-terminate principle preserves concept-engagement integrity; ceiling value held in private operational configuration; does not rise to MISSION.md commitments list (operating discipline, ADR 0026 precedent). Four tension entries opened: OQ-BYOK-REGIME (institutional vs. consumer), OQ-WALL-BEHAVIOR (degradation ladder), OQ-CONTEXT-COMPRESSION (token-amplification mitigation), OQ-PEDAGOGY-INFERENCE-LOCUS (rule layer vs. distributed; tagged `watch`). **docs/pedagogy/inferences.md** seeded with ~19 inferences across six categories as the cheap intermediate step before deciding the rule-layer question. **docs/business.md** revised: Personal Financial Risk Ceiling section, Cost Amplification with Session Length subsection, Revenue Mechanisms reframed by learning intensity with cross-domain bridges as differentiator (constrained doses on free tier, not paywalled entirely), pricing language is user-meaningful not vendor-SKU, soft-walls-degrade principle, seasonal pre-buy, institutional vs. consumer BYOK split. **docs/pedagogy.md** Layered Instruction Architecture table revised to reflect API-app architecture (rows for Rendering policy and Interaction-surface scope; existing rows updated to current locations). **ROADMAP.md** Phase 1.2 expansion, Phase 7/8/9 success-criteria additions. **docs/MISSION.md** commitment 2 gains inline ADR 0029 cross-link (without rising to commitments list). **docs/CROSS_REFERENCES.md** three new shared-capability-consumer entries + three new phase-boundary checks. **adr/README.md** Phase 1 index extended. `tools/validate.py` clean. |
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

**S-0009 — Phase 1.3: `confidence_level` column on node schema** *(closes Phase 1; Phase 1.2 closed at S-0008.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (29 ADRs) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

Phase 1.2 closed at S-0008 with three ADRs (0027 rendering policy, 0028 input-side scope structural-not-prompt, 0029 personal financial cost ceiling), `AGENT_INSTRUCTIONS.md` at repo root, four new tension entries (OQ-BYOK-REGIME, OQ-WALL-BEHAVIOR, OQ-CONTEXT-COMPRESSION, OQ-PEDAGOGY-INFERENCE-LOCUS), the pedagogical inference registry stub at `docs/pedagogy/inferences.md`, and substantial cross-document updates (business.md, pedagogy.md, MISSION.md, ROADMAP.md, CROSS_REFERENCES.md, adr/README.md). Per the no-silent-drops feedback rule, all four exploration topics surfaced before the slot were absorbed as artifacts.

Phase 1.3 adds a single column to the node schema: `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`), orthogonal to the existing `provenance` field and the numeric `confidence` value. Synthetic nodes are first candidates for self-correction review (per [`docs/self-correction.md`](docs/self-correction.md)). The column is declared in [`docs/architecture.md`](docs/architecture.md) (Node Schema), shipped in the Phase 3 SQL migration, and consumed by [`tools/validate.py`](tools/validate.py)'s Phase 4 graph audit (per [ROADMAP.md](ROADMAP.md) Phase 4 soft-warn category — "`confidence_level: SYNTHETIC` nodes flagged for review queue").

Source documents:
- [`docs/architecture.md`](docs/architecture.md) Node Schema (extension target).
- [ROADMAP.md](ROADMAP.md) Phase 1.3 (the spec); Phase 4 (the consumer in the graph audit); Phase 5 (seed-graph authoring sets `confidence_level: INTERPRETED` until validated).
- [ADR 0016](adr/0016-graph-construction-needs-live-validation.md) (the live-validation discipline this column feeds).

Scope (S-0009):
- Add `confidence_level` to the Node Schema in [`docs/architecture.md`](docs/architecture.md) with explicit semantics for each enum value.
- Cross-link from [`docs/self-correction.md`](docs/self-correction.md) (synthetic nodes as first review candidates) and [ROADMAP.md](ROADMAP.md) Phase 4 (the soft-warn integration).
- Whether an ADR is warranted is a judgment call: the column is a small schema addition that fits naturally under the broader graph-validation discipline of [ADR 0016](adr/0016-graph-construction-needs-live-validation.md). If the enum semantics or the synthetic-review pipeline implications require recording a tradeoff, author ADR 0030. Otherwise, document in `docs/architecture.md` and note in CHANGELOG.

S-0009 success criteria: `confidence_level` column added to the Node Schema with enum semantics specified; cross-links updated; Phase 4 audit category alignment confirmed; `tools/validate.py` returns clean.

After S-0009: Phase 1 closes. The two open privacy questions (OQ-PRIVACY-A erasure mechanism, OQ-PRIVACY-B institutional regime) are decide-before-Phase 3 and need ADRs of their own before Phase 3 schema authoring begins — likely one session each. The four S-0008-opened tensions (OQ-BYOK-REGIME, OQ-WALL-BEHAVIOR, OQ-CONTEXT-COMPRESSION, OQ-PEDAGOGY-INFERENCE-LOCUS) sit at later phase boundaries (Phase 7, 8, 9). Sessions 12–14 of the prompt pack remain deferred (per [ROADMAP.md](ROADMAP.md) §1.1).

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
