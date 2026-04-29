# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with project-specific calibration: changes are scoped to **state-of-record** (design docs, schemas, seed graph migrations, build_plan, ADRs, OPERATIONS-equivalent docs, top-level project files). Application code (React, API endpoints, UI) is **git-only** — its history lives in the commit log, not here.

This project does not yet follow [Semantic Versioning](https://semver.org/) — versions are milestones (`0.0.x` for foundation; `0.1.0` at foundation close; later versions track product readiness).

---

## [Unreleased]

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
