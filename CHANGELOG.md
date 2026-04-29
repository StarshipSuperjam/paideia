# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with project-specific calibration: changes are scoped to **state-of-record** (design docs, schemas, seed graph migrations, build_plan, ADRs, OPERATIONS-equivalent docs, top-level project files). Application code (React, API endpoints, UI) is **git-only** — its history lives in the commit log, not here.

This project does not yet follow [Semantic Versioning](https://semver.org/) — versions are milestones (`0.0.x` for foundation; `0.1.0` at foundation close; later versions track product readiness).

---

## [Unreleased]

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
