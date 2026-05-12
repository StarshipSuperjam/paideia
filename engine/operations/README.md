# docs/operations/

Procedural documentation. One file per topic. AI sessions discover topics by reading this index or running `ls docs/operations/`.

`CLAUDE.md` names *the rules*. This directory documents *how to apply them*.

## Topics

### Session protocol

- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure, eager-claim ritual mechanics, in-session commit cadence, push policy; routine-mode boot branch (per ADR 0051).
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — audit, spot-check, STATE.md update, ENGINE_LOG material-change criteria, archive, final push.
- [`routine-mode-operations.md`](routine-mode-operations.md) — routine-mode session pattern (per ADR 0051): target file schema, master plan procedure, criterion catalog, scope-lock model, mixing interactive and routine sessions.
- [`escalation-criteria.md`](escalation-criteria.md) — auto-mode interrupt criteria with worked examples.
- [`issue-discipline.md`](issue-discipline.md) — HANDOFF.md vs GitHub Issues split (per ADR 0048); label taxonomy; Issue body shape; cleanup-batch workflow; boot-time backlog visibility.

### MemPalace

- [`mempalace-operations.md`](mempalace-operations.md) — install, `init`, `mine`, MCP server registration, Claude Code stop/precompact hook wiring.
- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — `exploration` / `decision` / `work` tags and when each applies.

### Tooling

- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — hard-fail vs soft-warn, per-category meaning, what to do with each.
- [`tools-sweep-worktrees.md`](tools-sweep-worktrees.md) — when to run, what it cleans, abort criteria.

### Decisions and review

- [`build-readiness-gate.md`](build-readiness-gate.md) — pre-flight gate before substantive build sessions (per ADR 0040): adversarial reconnaissance, Tier 1/2/3 triage, gate report at `engine/build_readiness/<phase>_<chunk>.md`.
- [`mechanism-first-exercise-gate.md`](mechanism-first-exercise-gate.md) — pre-flight before unattended use of a novel cross-cutting mechanism (per ADR 0053): mechanism-triggered (vs build-readiness-gate's phase-trigger); one report per qualifying mechanism.
- [`adr-authoring.md`](adr-authoring.md) — Nygard template, status conventions, when an ADR is warranted.
- [`document-voice.md`](document-voice.md) — expression contract for inward-facing project documentation; governs voice in the `docs/` tree, ADRs, root-level project files. Sibling tool to [`AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md), separately scoped.
- [`code-discipline.md`](code-discipline.md) — expression contract for AI-authored code under engine/; three-layer discipline (contract-first prose, mechanical gates, cold-context review pass). Sibling tool to [`document-voice.md`](document-voice.md), separately scoped to code.
- [`revert-and-rollback-discipline.md`](revert-and-rollback-discipline.md) — procedure for undoing a landed commit (per [ADR 0078](../adr/0078-revert-and-rollback-discipline.md)): forward-fix vs revert decision criteria, revert procedure via PR flow, interactions with the lifecycle-push wrappers / `routine_eager_claim_recovery.py` / `apply_migration.py` / ADR supersession / MemPalace decision drawers, hotfix flow. Sibling sub-discipline to `code-discipline.md` and `migration-discipline.md`.
- [`dependency-discipline.md`](dependency-discipline.md) — Layer 1 source-of-truth for Python dependency management per ADR 0064 (S-0127): pyproject.toml as source-of-truth, uv.lock as the install contract, uv sync as canonical install, validate.py freshness gate, refresh procedure, routine-mode interaction.
- [`sub-agent-validation.md`](sub-agent-validation.md) — when to spawn sub-agents, briefing style, output validation.
- [`health-check.md`](health-check.md) — periodic project audit (per ADR 0022): categories, report template, cadence policy.

### Phase-specific

- [`seed-chunked-authoring.md`](seed-chunked-authoring.md) — per-session migration workflow for Phase 5 seed-graph build (placeholder; Phase 4 fleshes out).

## Conventions

- One concern per file. If a topic grows beyond a single screen of meaningful content, split rather than nest.
- Each file opens with a one-line purpose statement and ends with a "See also" pointer when relevant.
- Procedural files use imperative mood ("Run X. Verify Y."). Reference files use declarative mood ("Hard-fails block the commit.").
- Cross-references inside this directory use relative links. Cross-references to other parts of the repo use repo-relative links from the file's perspective.
