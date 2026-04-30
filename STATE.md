# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | Phase 0 — closed (S-0003); Phase 1 — Contract Lock (substantively closed at S-0010 modulo OQ-PRIVACY-A / OQ-PRIVACY-B which are decide-before-Phase 3); §1.1 fully closed — prompt-pack Sessions 9, 10, 11 settled across S-0004 / S-0005 / S-0006; privacy-posture insertion landed at S-0007; §1.2 fully closed at S-0008 (rendering policy + input-side scope + personal financial cost ceiling); Phase 4.5 input-dataset-survey scaffolding landed at S-0009 (out-of-phase scope expansion absorbed from Önduygu philo-browser exploration per the no-silent-drops rule); §1.3 closed at S-0010 (`confidence_level` column on Node Schema with three-axis orthogonality and the SYNTHETIC review queue cross-link, ADR 0030). The two privacy-policy ADRs remain. |
| **Last build session** | S-0010 (2026-04-30) — Phase 1.3 closed; Phase 1 substantively closes. **`docs/architecture.md`** Node Schema gains `confidence_level TEXT NOT NULL DEFAULT 'INTERPRETED'` with full per-value semantics (EXTRACTED for source-structured concepts, INTERPRETED for pedagogical inference from source material, SYNTHETIC for generated service nodes / Opus-proposed splits without source basis); the existing `confidence` column entry now explicitly notes it "updates over time" to distinguish from the new fixed-at-write evidentiary-mode column. **[ADR 0030](adr/0030-confidence-level-evidentiary-mode-on-nodes.md)** establishes the column as a third epistemic axis orthogonal to `provenance` (who authored, lifecycle stage) and to numeric `confidence` (how-sure-now, updates with evidence); records the orthogonality argument with two test combinations (`provenance='human'` + `SYNTHETIC` for human-authored service nodes; `confidence=0.3` + `EXTRACTED` for source-aligned nodes whose belief decayed under counter-evidence — the label does not update with that decay); records the default-choice argument (`INTERPRETED` matches Phase 5.2 baseline; EXTRACTED would silently overclaim, SYNTHETIC would over-flag the review queue); names the naming risk (`confidence_level` reads as a finer version of `confidence`) and accepts it as the cost of not invalidating downstream references — the ADR's Decision section is the durable mitigation. **`docs/self-correction.md`** gains a new **Synthetic-Node Review Queue** subsection under Self-Correction Pipeline naming SYNTHETIC nodes as first review candidates within the Opus batch cycle, with repromotion via supersession (per [ADR 0021](adr/0021-node-deprecation-status-superseded-by.md)) rather than in-place label update. **`docs/CROSS_REFERENCES.md`** gains a five-consumer entry for ADR 0030. Phase 4 audit alignment confirmed: ROADMAP Phase 4 and ADR 0016 already named the SYNTHETIC soft-warn category; no edits needed. `tools/validate.py` clean (0 hard-fails, 0 soft-warns). |
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

**S-0011 — OQ-PRIVACY-A: erasure-mechanism ADR** *(decide-before-Phase 3 per [ADR 0026](adr/0026-persistent-learner-storage-structural-not-substantive.md); closes one of the two remaining Phase 1 ADRs.)*

Boot procedure: type `Start Engine` (or `/start-engine`) in a fresh Claude Code session. CLAUDE.md is auto-loaded; MemPalace `mempalace_search` is queryable from boot; the ADR collection in `adr/` (30 ADRs after S-0010) is the contract layer. Invocation of `/start-engine` is itself the authorization for the lifecycle's pushes — no per-push confirmation.

Phase 1.3 closed at S-0010. The Node Schema now carries `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`) per [ADR 0030](adr/0030-confidence-level-evidentiary-mode-on-nodes.md). Phase 1 substantively closes — every roadmap-named §1.x deliverable has landed. The two privacy ADRs (OQ-PRIVACY-A, OQ-PRIVACY-B) are decide-before-Phase 3 because both shape the Phase 3 SQL migration: OQ-PRIVACY-A's chosen erasure mechanism dictates whether `learner_events` needs an `encrypted_user_data_key` column (crypto-shredding), a delete-cascade discipline (hard-delete-with-cascade), or a nullable `user_id` post-erasure (anonymize-and-aggregate); OQ-PRIVACY-B reserves at least one column on `learner_events` for institutional-regime eligibility.

S-0011 scope: settle **OQ-PRIVACY-A** (erasure mechanism for learner data). Three candidates per [`docs/tensions.md`](docs/tensions.md): **(1)** crypto-shredding (per-learner KMS key, delete-on-erasure; preserves event-sourcing audit trail; per-learner key column on durable tables); **(2)** hard-delete-with-cascade (simplest; loses audit trail; cascade discipline must be authored across `learner_events`, `mastery_snapshots`, `tension_log`); **(3)** anonymize-and-aggregate (preserves graph-level signal post-erasure; whether it satisfies GDPR Article 17 right-to-erasure is contested and would need legal grounding before adoption). The decision propagates into Phase 3 schema authoring, so it must be settled *before* Phase 3 — and the audit trail vs. simplicity vs. compliance-grounding tradeoff is real, not perfunctory.

Source documents:
- [`docs/tensions.md`](docs/tensions.md) — OQ-PRIVACY-A entry with three candidates and the decide-before-Phase 3 pin.
- [ADR 0026](adr/0026-persistent-learner-storage-structural-not-substantive.md) — privacy posture context and the structural-not-substantive baseline that OQ-PRIVACY-A's chosen mechanism must preserve.
- [ADR 0015](adr/0015-event-sourced-learner-model.md) — event-sourcing discipline (audit-trail-preserving erasure mechanisms align with this; hard-delete erodes it).
- [`docs/learner-model.md`](docs/learner-model.md) — Event-Sourced Architecture and the affected tables.
- [`docs/business.md`](docs/business.md) — Account Ownership and Transfer Path (privacy *posture* vs. *policy* distinction set in S-0007; this session moves the policy-mechanism half toward settlement).

S-0011 success criteria: ADR 0031 lands with Status: Accepted naming the chosen erasure mechanism and the column-shape implications for Phase 3; OQ-PRIVACY-A in `docs/tensions.md` updated to `Settled by ADR 0031`; CHANGELOG entry under `[Unreleased]`; `tools/validate.py` returns clean. If the deliberation surfaces that OQ-PRIVACY-A and OQ-PRIVACY-B should be jointly resolved (because the institutional regime's analytics-eligibility column interacts with the erasure mechanism's column shape), the session may absorb both — judgment call at the session's discretion.

After S-0011: S-0012 settles OQ-PRIVACY-B (institutional vs. individual regime, column reservation Phase 3, policy specification Phase 8) unless S-0011 absorbs it. Then Phase 1 fully closes and Phase 2 (Build Plan Scaffolding) opens. The four S-0008-opened tensions (OQ-BYOK-REGIME, OQ-WALL-BEHAVIOR, OQ-CONTEXT-COMPRESSION, OQ-PEDAGOGY-INFERENCE-LOCUS) sit at later phase boundaries (Phase 7, 8, 9). Sessions 12–14 of the prompt pack remain deferred (per [ROADMAP.md](ROADMAP.md) §1.1). Phase 4.5 (input dataset survey) is queued between Phase 4 and Phase 5.

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

ADR collection landed at S-0003 close; `design-reasoning.md` retired in the same commit. Phase 1 ADRs accumulate from S-0004 onward: ADRs 0023–0024 added in S-0004 (engagement-depth aggregation, sub-signal storage shape); ADR 0025 added in S-0006 (historical maximum tracking); ADR 0026 added in S-0007 (privacy posture, structural-not-substantive); ADRs 0027–0029 added in S-0008 (rendering policy as prompt-layer contract; input-side scope structural-not-prompt; personal financial cost ceiling); ADR 0030 added in S-0010 (`confidence_level` evidentiary-mode column on Node Schema). Total ADR count: 30.
