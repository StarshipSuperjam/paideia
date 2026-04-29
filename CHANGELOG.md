# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with project-specific calibration: changes are scoped to **state-of-record** (design docs, schemas, seed graph migrations, build_plan, ADRs, OPERATIONS-equivalent docs, top-level project files). Application code (React, API endpoints, UI) is **git-only** — its history lives in the commit log, not here.

This project does not yet follow [Semantic Versioning](https://semver.org/) — versions are milestones (`0.0.x` for foundation; `0.1.0` at foundation close; later versions track product readiness).

---

## [Unreleased]

### Added
- Industry-standard top-level files: `README.md`, `LICENSE` (proprietary, all rights reserved Shane Kidd), `SECURITY.md`, `STATE.md`, `ROADMAP.md`, `HANDOFF.md`, `CHANGELOG.md` (this file)
- Bimodal session protocol scaffolding: `session/register_state.json` + `session/current.json` + `session/archive/` directory
- Eager-slot-claim ritual (commit + push the claim atomically before substantive work)
- Backup tag `pre-foundation-v0.0.0` at commit `fa70b8c` for one-command rollback if foundation work goes sideways
- MemPalace 3.3.3 installed with MCP server registered in `.mcp.json` (indexing deferred to S-0002)
- Slash command `.claude/commands/start-engine.md` (self-sufficient claim procedure for S-0001 → expanded by S-0002 once `docs/operations/` lands)
- `.gitignore` exception for `.claude/commands/` so the slash command ships with the repo

### Changed
- `.mcp.json` now registers both Supabase and MemPalace MCP servers (gitignored, contains PATs)

---

## S-0001 — 2026-04-29 — Structural foundation + retirement of obsolete pre-foundation source files

(See `[Unreleased]` above; promoted at S-0001 close.)

---

## Pre-foundation history

Prior to S-0001, the project ran in a Claude project with custom instructions paste-in workflow, tracked in `IMPLEMENTATION_PLAN.md`. Pre-Phase 0 (Pre-0.1, Pre-0.2, Pre-0.3) closed sequentially in commits `93bdd9b` (Pre-0.1), `fa70b8c` (Pre-0.2 + Pre-0.3 substrate). The foundation reorganization at S-0001 supersedes that workflow with the industry-standard structure documented in `README.md` and `ROADMAP.md`.
