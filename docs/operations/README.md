# docs/operations/

Procedural documentation. One file per topic. AI sessions discover topics by reading this index or running `ls docs/operations/`.

`CLAUDE.md` names *the rules*. This directory documents *how to apply them*.

## Topics

### Session protocol

- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure, eager-claim ritual mechanics, in-session commit cadence, push policy.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — audit, spot-check, STATE.md update, CHANGELOG material-change criteria, archive, final push.
- [`escalation-criteria.md`](escalation-criteria.md) — auto-mode interrupt criteria with worked examples.

### MemPalace

- [`mempalace-operations.md`](mempalace-operations.md) — install, `init`, `mine`, MCP server registration, Claude Code stop/precompact hook wiring.
- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — `exploration` / `decision` / `work` tags and when each applies.

### Tooling

- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — hard-fail vs soft-warn, per-category meaning, what to do with each.
- [`tools-sweep-worktrees.md`](tools-sweep-worktrees.md) — when to run, what it cleans, abort criteria.

### Decisions and review

- [`adr-authoring.md`](adr-authoring.md) — Nygard template, status conventions, when an ADR is warranted.
- [`document-voice.md`](document-voice.md) — expression contract for inward-facing project documentation; governs voice in the `docs/` tree, ADRs, root-level project files. Sibling tool to [`AGENT_INSTRUCTIONS.md`](../../AGENT_INSTRUCTIONS.md), separately scoped.
- [`sub-agent-validation.md`](sub-agent-validation.md) — when to spawn sub-agents, briefing style, output validation.
- [`health-check.md`](health-check.md) — periodic project audit (per ADR 0022): categories, report template, cadence policy.

### Phase-specific

- [`seed-chunked-authoring.md`](seed-chunked-authoring.md) — per-session migration workflow for Phase 5 seed-graph build (placeholder; Phase 4 fleshes out).

## Conventions

- One concern per file. If a topic grows beyond a single screen of meaningful content, split rather than nest.
- Each file opens with a one-line purpose statement and ends with a "See also" pointer when relevant.
- Procedural files use imperative mood ("Run X. Verify Y."). Reference files use declarative mood ("Hard-fails block the commit.").
- Cross-references inside this directory use relative links. Cross-references to other parts of the repo use repo-relative links from the file's perspective.
