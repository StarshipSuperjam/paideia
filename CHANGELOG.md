# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with project-specific calibration: changes are scoped to **state-of-record** (design docs, schemas, seed graph migrations, build_plan, ADRs, OPERATIONS-equivalent docs, top-level project files). Application code (React, API endpoints, UI) is **git-only** — its history lives in the commit log, not here.

This project does not yet follow [Semantic Versioning](https://semver.org/) — versions are milestones (`0.0.x` for foundation; `0.1.0` at foundation close; later versions track product readiness).

---

## [Unreleased]

### Added (S-0007 — Phase 1 insertion ahead of planned Phase 1.2: privacy posture commitments)
- [`adr/0026-persistent-learner-storage-structural-not-substantive.md`](adr/0026-persistent-learner-storage-structural-not-substantive.md) — Persistent learner storage is structural, not substantive. Establishes the principle: persistent state captures structural engagement signals (concept refs, interaction types, sub-signal scores per ADR 0024, timestamps, bounded structural context refs, structured tension records) but does not persist substantive content (beliefs, doctrinal positions, political/religious views, first-person claims, quoted reasoning) in free-text form on any durable table. Three operational sub-decisions: **(1)** `tension_log.exchange_summary` becomes JSONB-with-named-fields (replacing `TEXT NOT NULL`) with constrained shape and Sonnet writing-policy bounds on `pattern_observed` (the only free-text field); **(2)** `learner_events.context` is schematized as fixed structured columns at Phase 3 (no JSONB grab-bag, no free-text columns); **(3)** conversation transcripts are not persisted as system-of-record data — operational TTL bounded (default session-end, hard cap 24 hours), with cross-session continuity supplied by the structured event log and `mastery_snapshots` instead of transcript replay. Forcing function: Phase 8 Apple App Store privacy questionnaire is a blocking artifact whose 2–4 week Apple lead time means the posture must be settled now, not later. Extends ADR 0014's "Opus operates on aggregated patterns, not on individual learner data," ADR 0015's storage discipline, and ADR 0024's structural-signal pattern. Does not rise to MISSION.md's strong-working-commitments list (architectural discipline, not pedagogical commitment). Status: Accepted.
- [`docs/tensions.md`](docs/tensions.md) — Two open questions added per ADR 0026:
  - **OQ-PRIVACY-A** (erasure mechanism for learner data) — three candidates: crypto-shredding (per-learner KMS key, delete on erasure; preserves event-sourcing audit trail), hard-delete-with-cascade (simplest; loses audit), anonymize-and-aggregate (preserves graph-level signal; whether it satisfies GDPR Article 17 is contested). Decide before Phase 3 schema authoring; the choice shapes whether `learner_events` needs an `encrypted_user_data_key` column, a delete-cascade discipline, or a nullable `user_id` post-erasure. Decision lands as an ADR.
  - **OQ-PRIVACY-B** (institutional vs. individual data regime) — direction-neutral; institutional cohorts may be more *or* less analytics-eligible than individuals depending on DPA contract terms vs. FERPA-style stricter regime. Concrete proposal to evaluate at Phase 3: a column on `learner_events` like `eligible_for_aggregate_analytics` (shape and default both open). Decide before Phase 3 to reserve any required columns; policy specification (eligibility rules, defaults, runtime gates) defers to Phase 8 alongside actual institutional partner conversations. Decision lands as an ADR (or two — one Phase 3 column, one Phase 8 policy).

### Changed (S-0007)
- [`docs/self-correction.md`](docs/self-correction.md) — Tension Log Schema: `exchange_summary` column type changed from `TEXT NOT NULL` to `JSONB NOT NULL` with required semantic-field shape documented inline (`teaching_moves_tried`, `friction_type`, `pattern_observed`, `suggested_review_focus`, `unresolved_reference`); `pattern_observed` writing-policy bounds (length cap, third-person, descriptive-not-quotational, forbidden substantive-content categories) and Phase 4 `tools/validate.py` audit pointer added; spontaneous-connection unresolved-reference handling clarified to use `exchange_summary.unresolved_reference` (was: free-text in `exchange_summary`). All per ADR 0026.
- [`ROADMAP.md`](ROADMAP.md) — Phase 3 success criteria extended with `tension_log` and `learner_events` conformance to ADR 0026 and OQ-PRIVACY-A/B settlement requirement; new Phase 8 success-criteria section added with three bullets — eval harness operational against the OQ-PHASE8-A-resolved baseline; Apple Developer Program enrollment in flight or complete; **privacy policy + Apple App Store privacy questionnaire answers exist and align with the privacy ADR collection before App Store submission** (pins privacy-policy authoring against the Apple lead time).
- [`docs/architecture.md`](docs/architecture.md) — Institutional Schema Provisions: "Privacy posture inheritance" paragraph added pointing to ADR 0026 (cohort-bound features inherit the structural-not-substantive baseline) and OQ-PRIVACY-B (column reservation Phase 3, policy specification Phase 8).
- [`docs/business.md`](docs/business.md) — Internal fine-tuning entry: ADR 0026 constraint added (fine-tuning draws on structured event log and structured tension records, not raw transcripts; transcript-based fine-tuning of a session-specific model is foreclosed without a superseding ADR). Account Ownership and Transfer Path: privacy *posture* vs. privacy *policy* distinction clarified — posture settled in ADR 0026, policy is Phase 8 work pinned to Apple App Store submission.
- [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md) — ADR 0026 → five-consumer entry added under "Shared capability consumers" (`docs/self-correction.md`, `docs/learner-model.md`, `docs/architecture.md`, `docs/business.md`, `ROADMAP.md`). Phase 2 → Phase 3 boundary check added requiring OQ-PRIVACY-A/B settlement before Phase 3 schema authoring; existing Phase 1 → Phase 2 entry annotated to clarify it tracks ADR-mapping completeness, not Phase 6 readiness (the actual decide-before for OQ-DEC1-* is Phase 6).
- [`adr/README.md`](adr/README.md) — Phase 1 index extended with ADR 0026; orientation paragraph extended to mention ADR 0026 lands in S-0007 ahead of Phase 1.2 (rendering policy moves to S-0008).
- [`STATE.md`](STATE.md) — current-phase pointer extended to mention S-0007 closes the privacy-posture insertion; last-build-session pointer updated; next-session work item replaced with S-0008 scope (Phase 1.2 rendering policy, formerly planned for S-0007); ADR collection count adjusted from 25 to 26.

### Added (S-0006 — Phase 1.1: prompt-pack Session 11 — Historical Maximum Tracking)
- [`adr/0025-historical-maximum-tracking.md`](adr/0025-historical-maximum-tracking.md) — `max_historical_score` (`NUMERIC(3,2) NOT NULL DEFAULT 0`) added to the existing `mastery_snapshots` table (per ADR 0015) as the decay floor's proficiency precondition. **Definition:** asymptotic cap on cumulative undecayed raw strength over **substantive** interaction types — `max_historical_score = 1 − exp(−Σ_e raw_strength(e) / 1.0)` summed over `direct_teaching`, `callback_reference`, `cross_domain_connection`, `assessment`. **Excluded:** `incidental_mention` and `backward_inference` — neither represents the "learner once genuinely engaged" evidence the floor is intended to protect; the substantive set matches the interaction types where the engagement-depth composite applies (per ADR 0023). **Update discipline:** snapshot regen on event ingest; closed-form incremental `max_new = 1 − (1 − max_old) · exp(−raw_new)` for substantive events, `max_new = max_old` otherwise. **Monotonicity invariant:** non-decreasing under event ingest; late-arriving offline events can only raise it. **Offline/sync coupling:** snapshot pushed to clients carries `max_historical_score`; client derives `floor_active = max_historical_score ≥ 0.3` locally (per ADR 0015's no-client-side-computation principle). The original "philosophical compromise to event-sourcing" framing dissolves — `mastery_snapshots` is already cached derived state by ADR 0015, so this is one more cached column on an existing cache, not a new architectural concession. **Closes prompt-pack Session 11** per `ROADMAP.md` §1.1; Phase 1.1 has now closed Sessions 9, 10, 11 across S-0004 / S-0005 / S-0006. Status: Accepted.

### Changed (S-0006 — Phase 1.1)
- [`docs/learner-model.md`](docs/learner-model.md) — Stage 3 paragraph adds the formal definition of "historical maximum aggregate" with ADR 0025 pointer. Mastery Computation pseudocode updated: tracks `cumulative_substantive_raw` alongside the decayed `sum`, computes `max_historical = 1 − exp(−cumulative_substantive_raw / 1.0)`, applies the floor precondition against this scalar — replaces the prior `<running undecayed aggregate at event time>` placeholder. Historical-maximum-tracking paragraph rewritten to describe the settled position (column on `mastery_snapshots`, substantive-set guard, monotonicity invariant, closed-form incremental update, offline-sync coupling). Footer updated.
- [`adr/README.md`](adr/README.md) — Phase 1 table extended with ADR 0025; orientation paragraph notes Phase 1.1 closed at S-0006.
- [`STATE.md`](STATE.md) — current-phase pointer notes §1.1 fully closed; last-build-session pointer updated to S-0006; next-session work item replaced with S-0007 scope (Phase 1.2 — `AGENT_INSTRUCTIONS.md` rendering policy).

### Verified (S-0005 — Phase 1.1: prompt-pack Session 10 — Decay Parameter Verification)
- V1 decay parameters (`BASE_HALF_LIFE = 60 days`, `MAX_FLOOR = 0.6` from `docs/learner-model.md`) verified against five realistic trajectory scenarios using the engagement-depth distribution settled in ADR 0023. **All scenarios match design intent. No parameter revisions.** Session 10 closes without an ADR per `ROADMAP.md` §1.1 ("verification of pre-existing parameters does not require a new ADR; the verification record + CHANGELOG note is sufficient").
- **Scenarios run** (computation: standard `compute_mastery` per `docs/learner-model.md`):
  1. **Active low-rigor** (Cartesian Dualism, rigor 0.15) — 2 `direct_teaching` @ depth 0.6 + 6 weekly `callback_reference` @ depth 0.4. Holds proficiency throughout active use; brief `MASTERY` excursion at weeks 4–7; drifts to floor 0.51 after callbacks stop. ✓
  2. **Active high-rigor** (Transcendental Idealism, rigor 0.85) — same pattern. Holds proficiency during active use (~0.55–0.61); `MASTERY` is unreachable through callbacks at depth 0.4 alone (peak 0.614). Crashes to `EXPOSED` four weeks after callbacks stop. Sensitivity sweep confirms callbacks at depth ≥ 0.5 reach mastery briefly. ✓ (matches design — high-rigor mastery requires verified understanding, not passive reinforcement.)
  3. **Abandoned mid-rigor** (rigor 0.5) — proficiency reached, then 6 months silence. Aggregate falls below 0.3 around day 60; floor (0.30) catches it. Score sits exactly at the proficiency/exposed boundary indefinitely. ✓
  4. **Mastery verification** — proficiency through teaching, 3 weeks later `assessment` @ depth 0.9. Single assessment event crosses to `MASTERY` at all rigor levels (low: 0.510 → 0.789; mid: 0.436 → 0.770; high: 0.394 → 0.753). ✓
  5. **Backward inference** (rigor 0.4 prerequisite) — single `backward_inference` @ fixed depth 0.5 yields aggregate 0.113 (`EXPOSED`). Across rigors 0.05–0.85: aggregate 0.03–0.17, all `EXPOSED`. ✓ (matches design — defeasible soft-evidence injection, attenuated by rigor.)
- **Findings worth noting** (none triggered parameter changes):
  - Single `direct_teaching` event at depth 0.6 on a low-rigor concept already crosses the 0.3 proficiency threshold (aggregate 0.343) and activates the floor. Consistent with the design ("simple concepts stick once grasped") but more permissive than the Session 10 prompt's "two events" framing suggested.
  - Mid-rigor floor sits *exactly* at proficiency threshold (0.30 = 0.30). Abandoned mid-rigor concepts stay technically `PROFICIENCY` by the inclusive `≥ 0.3` boundary; the continuous score is the fading signal, not the discrete state.
  - Callbacks at typical depth (~0.4) cannot push high-rigor concepts to `MASTERY`. Mastery on high-rigor requires assessment-quality events (depth ~0.9) or sustained callbacks at depth ≥ 0.5.

### Changed (S-0005 — Phase 1.1)
- [`docs/learner-model.md`](docs/learner-model.md) — V1 parameter-defaults paragraph extended with a "Verified at S-0005 (2026-04-29)" note linking back to the verification entry above. No parameter values changed.

### Changed (S-0005 — procedure fix: /start-engine push gating)
- `.claude/commands/start-engine.md` — eager-claim step 5f and shutdown step 13 no longer require per-push user confirmation. Invoking `/start-engine` is itself the authorization for the lifecycle's pushes (eager-claim, in-session checkpoints, shutdown). Destructive operations (force-push, `git reset --hard`, branch deletion) still require explicit confirmation per auto-mode interrupt criteria.
- `docs/operations/session-build-lifecycle.md` — eager-claim step 6 and "Push policy within a session" rewritten to match. The first-push-of-session confirmation gate is removed; routine pushes proceed unconfirmed.
- `docs/operations/session-shutdown-sequence.md` — final-commit step 7 no longer requires per-push confirmation.
- `.claude/settings.json` — `permissions.allow` block added granting standing approval for the parent-repo lifecycle commands (`git -C <parent> merge --ff-only *`, `push origin main`, plus read-only `log`/`status`/`rev-parse`/`fetch`/`diff`). Project-scope so worktree clones inherit. Aligns the harness with the procedure: invocation is authorization.

### Added (S-0004 — Phase 1 entry: prompt-pack Session 9 — Engagement Depth Aggregation)
- [`adr/0023-engagement-depth-aggregation.md`](adr/0023-engagement-depth-aggregation.md) — engagement-depth as floored weighted geometric mean of three sub-signals (`scaffolding_distance^0.5 · generative_ratio^0.3 · novelty^0.2`, floor 0.05). Treats sub-signals as **complements** — closes the false-mastery vulnerability of weighted-sum aggregation. Defines signal ranges (all `[0,1]`, direct evidentiary direction), renames `scaffolding_proximity` → `scaffolding_distance` for direct composition, and pins fixed `engagement_depth` for non-composite interaction types (`backward_inference = 0.5`, `incidental_mention = 0.3`). Closes Session 9 per `ROADMAP.md` §1.1; Session 10 unblocked. Status: Accepted.
- [`adr/0024-engagement-depth-sub-signals-stored-raw.md`](adr/0024-engagement-depth-sub-signals-stored-raw.md) — `learner_events` stores three NUMERIC(3,2) sub-signal columns (`generative_ratio`, `scaffolding_distance`, `novelty`); composite `engagement_depth` is computed at query time. NULL sub-signal columns signal "composite does not apply" (the application layer substitutes the fixed value per ADR 0023). Aggregation tunability is preserved without schema migration; honors ADR 0015's "store raw, derive state" discipline. Status: Accepted.

### Changed (S-0004)
- [`docs/learner-model.md`](docs/learner-model.md) — Engagement Depth section rewritten with the aggregation formula, signal definitions in direct evidentiary direction, and fixed `engagement_depth` values for non-composite interaction types. Mastery Computation pseudocode updated: introduces `compute_engagement_depth(event)` helper that handles fixed values for `backward_inference`/`incidental_mention` and the floored weighted geometric mean for composite cases. V1 parameter examples recomputed with the new formula. `scaffolding_proximity` references renamed to `scaffolding_distance` (interaction-types section + section title); pedagogical concept unchanged.
- [`docs/pedagogy.md`](docs/pedagogy.md) — "Scaffolding Proximity" section renamed to "Scaffolding Distance" with prose updated to direct evidentiary direction; four downstream prose references updated (V1 calibration defaults, structural separation of proficiency/mastery, exception case, zero-scaffolding constraint). Pedagogical concept (how-recently-was-the-scaffolding) is unchanged; only the variable name and value/evidentiary alignment.
- [`docs/MISSION.md`](docs/MISSION.md) — Commitment 10 wording updated: "discounted by scaffolding distance (per ADR 0023, high distance → high evidentiary weight)" replaces "discounted by scaffolding proximity"; ADR 0023 cross-link added.
- [`docs/CROSS_REFERENCES.md`](docs/CROSS_REFERENCES.md) — Bidirectional sync entry for learner-model ↔ pedagogy updated to use `scaffolding_distance`; rename note + ADR 0023 cross-link added.
- [`docs/reading-system.md`](docs/reading-system.md) — Two prose passages on close-reading event scaffolding updated to use `scaffolding_distance` in direct evidentiary direction (close-reading events have *low* distance, not *high* proximity; mastery requires *high* distance demonstration).
- [`adr/README.md`](adr/README.md) — Phase 1 section added with ADRs 0023, 0024; orientation paragraph updated to describe the Phase 1 accumulation pattern.
- [`STATE.md`](STATE.md) — current-phase pointer flips to "Phase 1 — Contract Lock (in progress); prompt-pack Session 9 closed at S-0004"; last-build-session pointer updated to S-0004; next-session work item replaced with S-0005 scope (prompt-pack Session 10 — Decay Parameter Verification).

### Changed (S-0003 continuation — post-foundation cleanup)
- `README.md` — staleness sweep. Foundation status flipped from "in progress" to "closed (S-0003)"; all `(lands in S-NNNN)` parentheticals removed (every referenced artifact now exists); repo map updated to include `_archive/` removal, `docs/entities.json`, `docs/mempalace.yaml`, `docs/prep-paideia-prompt-pack.md`, `tools/validate-history.jsonl`, `.claude/settings.json`; `session/current.json` correctly described as session-scoped; ADR collection (22 ADRs) added to repo-map and Project History; "How to start a session" updated to reflect the now-extant procedural layer.
- `docs/operations/session-shutdown-sequence.md` — "Deprecated files" maintenance entry rewritten to the **absorption + delete** pattern with git-tag/`git show` recovery as primary; `_archive/` retained only as a one-off escape hatch (named cases referenced by current artifacts) rather than the default. CONTEXT.md (S-0002) and design-reasoning.md (S-0003) cited as exemplars of absorption + delete.
- `docs/operations/escalation-criteria.md` — "_archive/ v0.2 keep-or-delete" worked-example replaced with the more general "should this retirement leave a structural artifact behind, or is git tag/history sufficient?" — now points at the escape-hatch pattern in `session-shutdown-sequence.md`.

### Removed (S-0003 continuation — post-foundation cleanup)
- `_archive/philosophy-graph-seed-v0.1.json` and `_archive/philosophy-graph-seed-v0.2.json` — pre-foundation thinker-level seed JSONs. Recoverable via `git show pre-foundation-v0.0.0:_archive/<filename>`. ADR 0008 (concept nodes, not thinkers) preserves the reasoning behind the v0.2 retirement.
- `_archive/` directory — decommissioned as a default protocol. Two pre-foundation JSONs were the only contents and the only candidates the repo had ever produced. Foundation work has consistently followed absorption + delete (CONTEXT.md, design-reasoning.md) without invoking `_archive/`. Future structural-artifact archives use the one-off escape hatch.

### Added (S-0003)
- `adr/` directory with 23 markdown files: `adr/README.md` indexing the collection (with status-conventions table, links to `docs/operations/adr-authoring.md` for full Nygard guidance) plus 22 ADRs (`0001`–`0022`). All ADRs `Status: Accepted`.
- ADRs 0001–0012 — strong working commitments: pedagogical edges, commercial sustainability without pedagogical compromise, supplementary media as metadata, relational learner model, per-text interpretive outline, domain-agnostic architecture, cross-domain porosity, concept nodes (not thinkers), portable mastery, continuous contextual assessment, no hosted copyrighted material, freshman defaults / autodidact ceiling.
- ADRs 0013–0022 — architectural decisions: mastery verification as organic escalation, Sonnet teaches / Opus reviews, event-sourced learner model, graph construction needs live validation (the contract behind `tools/validate.py`'s `validate_graph` stub), Postgres + recursive CTEs over OWL/RDF, flat domain tags + community detection, two-column rigor score override, teaching notes separate from summary, node deprecation via `status` + `superseded_by`, periodic project health checks (the cadence-trigger machinery built in S-0001).

### Changed (S-0003)
- `tools/validate.py` `adr_status` regex updated to accept the documented Nygard template's bold form (`- **Status:** Accepted`). The original regex required plain `Status:` and produced 22 false-positive soft-warns against the canonical template; fixed regex passes all 22 ADRs cleanly.
- `docs/MISSION.md` — Strong working commitments list now carries inline ADR cross-references (one per commitment, linking to the corresponding ADR file).
- `docs/CROSS_REFERENCES.md` — Phase 0 → Phase 1 boundary check marked `verified at S-0003 close` with the full ADR-mapping audit recorded inline. Commitments → downstream-files entries updated to include ADR links.
- `ROADMAP.md` — S-0003 entry rewritten to describe the landed work (adr/README.md indexes; ADR breakdown includes ADR 0016 + ADR 0022 emerged in S-0001 plan); architectural-decisions list updated to point at ADRs 0013–0022.
- `docs/operations/adr-authoring.md` — opening paragraph updated to describe the landed collection rather than the pending one; "Source material" entry no longer references `design-reasoning.md`.
- `docs/operations/session-shutdown-sequence.md` — "New commitment + reasoning" maintenance entry rewritten now that S-0003 has landed; both *what* and *why* now land in an ADR; the conversational story lands in MemPalace under the `decision` tag.
- `STATE.md` — current-phase pointer flips to "Phase 0 — closed (S-0003); Phase 1 — Contract Lock pending"; last-build-session pointer updated to S-0003; next-session work item replaced with S-0004 scope (prompt-pack Session 9 — Engagement Depth Aggregation); strong-working-commitments section rewritten to point at the ADR collection.

### Removed (S-0003)
- `design-reasoning.md` — retired. Eight entries became ADRs 0013, 0014, 0015, 0017, 0018, 0019, 0020, 0021. (ADR 0016 graph-construction-validation and ADR 0022 periodic-health-checks emerged separately in the S-0001 plan conversation.)

### Added (S-0002)
- `CLAUDE.md` — AI orientation; auto-loaded; ~80 lines covering the startup ceremony, the standing pushback rule, auto-mode interrupt criteria, budget guidance, end-state-quality first-pass, two-layer decision recording (ADR + MemPalace), and commit conventions.
- `docs/operations/` library — index README plus 11 topic files: session-build-lifecycle, session-shutdown-sequence, escalation-criteria, mempalace-operations, mempalace-tagging-conventions, tools-validate-interpretation, tools-sweep-worktrees, adr-authoring, sub-agent-validation, seed-chunked-authoring (Phase 4 placeholder), health-check.
- `docs/MISSION.md` — vision, cross-domain porosity, audience framing, strong working commitments. Extracted from CONTEXT.md.
- `docs/CROSS_REFERENCES.md` — high-value file dependencies; links resolve via standard markdown relative-path semantics. Extracted from CONTEXT.md File Dependencies table.
- `.claude/settings.json` — Stop and PreCompact hooks wiring MemPalace capture per `docs/operations/mempalace-operations.md`. Ships with the repo (`.gitignore` exception added; `settings.local.json` remains gitignored).
- `docs/mempalace.yaml` + `docs/entities.json` — MemPalace wing/room config (wing `paideia`, rooms `operations` + `general`) and entity classification (cleaned to projects-only after init heuristics misclassified concept-words as people).
- 414 MemPalace drawers indexed across the `paideia` wing (queryable via `mempalace_search`).
- User-level memory artifact (per-developer, outside the repo): `feedback_pushback_rule.md` + MEMORY.md index at the AI's user-memory directory.

### Changed (S-0002)
- `tools/validate.py` — `cross_references_resolve` now resolves links relative to the containing file (markdown standard) instead of REPO_ROOT.
- `.gitignore` — `.claude/settings.json` exception added so hooks ship with the repo.
- `docs/operations/session-shutdown-sequence.md` — extended with "Updating design docs during a session" section (absorbs CONTEXT.md's "How to Update These Files" protocols).
- `STATE.md` — last-session pointer S-0001 → S-0002; next-session work item S-0002 scope replaced with S-0003 ADR-collection scope; MemPalace infrastructure entry reflects the indexed state.

### Removed (S-0002)
- `CONTEXT.md` — content fully absorbed (Strong Working Commitments → MISSION.md; File Dependencies → CROSS_REFERENCES.md; update protocols → session-shutdown-sequence.md; chronology → recoverable from STATE.md + design-doc Added dates + MemPalace).

### Added (S-0001 — promoted from a prior `[Unreleased]`; folded into the dated section below at S-0002 close)
(See `## S-0001` section.)

---

## S-0001 — 2026-04-29 — Structural foundation + retirement of obsolete pre-foundation source files

### Added
- Industry-standard top-level files: `README.md`, `LICENSE` (proprietary, all rights reserved Shane Kidd), `SECURITY.md`, `STATE.md`, `ROADMAP.md`, `HANDOFF.md`, `CHANGELOG.md` (this file).
- Bimodal session protocol scaffolding: `session/register_state.json` + `session/current.json` + `session/archive/` directory.
- Eager-slot-claim ritual (commit + push the claim atomically before substantive work).
- Backup tag `pre-foundation-v0.0.0` at commit `fa70b8c` for one-command rollback if foundation work goes sideways.
- MemPalace 3.3.3 installed with MCP server registered in `.mcp.json` (indexing deferred to S-0002, completed there).
- Slash command `.claude/commands/start-engine.md` (self-sufficient claim procedure).
- `.gitignore` exception for `.claude/commands/` so the slash command ships with the repo.

### Changed
- `.mcp.json` now registers both Supabase and MemPalace MCP servers (gitignored, contains PATs).

---

## Pre-foundation history

Prior to S-0001, the project ran in a Claude project with custom instructions paste-in workflow, tracked in `IMPLEMENTATION_PLAN.md`. Pre-Phase 0 (Pre-0.1, Pre-0.2, Pre-0.3) closed sequentially in commits `93bdd9b` (Pre-0.1), `fa70b8c` (Pre-0.2 + Pre-0.3 substrate). The foundation reorganization at S-0001 supersedes that workflow with the industry-standard structure documented in `README.md` and `ROADMAP.md`.
