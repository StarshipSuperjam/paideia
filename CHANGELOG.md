# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with project-specific calibration: changes are scoped to **state-of-record** (design docs, schemas, seed graph migrations, build_plan, ADRs, OPERATIONS-equivalent docs, top-level project files). Application code (React, API endpoints, UI) is **git-only** — its history lives in the commit log, not here.

This project does not yet follow [Semantic Versioning](https://semver.org/) — versions are milestones (`0.0.x` for foundation; `0.1.0` at foundation close; later versions track product readiness).

---

## [Unreleased]

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
