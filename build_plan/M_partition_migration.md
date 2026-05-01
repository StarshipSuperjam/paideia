# M_partition_migration — Engine / product folder migration

> Bridge session(s) between Phase 2 close (S-0023) and Phase 5 open. Executes the `git mv` per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md), updates every cross-reference in the tree, runs `tools/validate.py` clean. The first per-phase build session ([`P_1_sql_schema.md`](P_1_sql_schema.md)) opens against the migrated tree.

## Phase scope

The repo restructures into `engine/` and `product/` subtrees per the shape committed in [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md). Phase 5 seed-graph authoring is the partition's first content load-test; the migration must close before Phase 5 opens so the seed graph lands at its partition-aware path from the first migration file.

The migration is mechanical in the sense that file-level moves are `git mv` operations, but it is judgment-laden in three places: (a) which ADRs file under `engine/adr/` vs `product/adr/`, (b) which `docs/` files file under `engine/operations/` vs `product/docs/` vs stay at root, (c) how the cross-reference sweep handles markdown links that span the partition. Each is settled in this chunk's session(s).

## Output

The post-migration tree per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md):

```
(repo root)
├── engine/
│   ├── operations/             ← from docs/operations/
│   ├── tools/                  ← from tools/
│   ├── session/                ← from session/
│   ├── adr/                    ← engine ADRs (criterion settled below)
│   ├── ENGINE_LOG.md           ← from ENGINE_LOG.md
│   ├── STATE.md                ← from STATE.md
│   └── CLAUDE.md               ← from CLAUDE.md
├── product/
│   ├── adr/                    ← product ADRs (criterion settled below)
│   ├── docs/                   ← from docs/ (minus docs/operations/, minus what stays at root)
│   ├── seed-graph/             ← new directory; populated starting at P_4
│   ├── AGENT_INSTRUCTIONS.md   ← from AGENT_INSTRUCTIONS.md
│   └── CHANGELOG.md            ← from CHANGELOG.md (the reserved stub)
├── build_plan/                 ← stays at root; bridges engine and product per-session contracts
├── ROADMAP.md                  ← stays at root
├── README.md                   ← stays at root
├── HANDOFF.md                  ← stays at root (engine-and-product bridge log)
├── SECURITY.md                 ← stays at root (industry-standard)
├── LICENSE                     ← stays at root
├── .claude/                    ← stays at root (Claude Code expects it there)
├── .git/                       ← stays at root
├── .gitignore                  ← stays at root
└── .mcp.json                   ← stays at root (gitignored; engine MCP config)
```

The `supabase/migrations/` tree at the time of migration moves to `product/seed-graph/migrations/` if it carries seed data; if it carries only schema (Phase 3 hasn't run yet at migration time), the path settles as part of `P_1_sql_schema.md`'s output decision.

## Success criteria

- `git status` clean after every `git mv` batch.
- `engine/tools/validate.py` runs clean (0 hard-fails) at session close.
- Every markdown cross-reference in the post-migration tree resolves. `engine/tools/validate.py`'s `cross_reference_broken` soft-warn category at zero.
- The pre-commit hook resolves `engine/tools/hooks/pre-commit` correctly (the symlink under the parent repo's `.git/hooks/` may need the relative-path retargeting per the [recovery procedure](../engine/operations/session-build-lifecycle.md) noted in S-0019).
- Capture-hook wrapper at `engine/tools/hooks/mempalace-hook-wrapper.sh` continues to fire correctly; `.claude/settings.json` paths updated.
- `engine/CLAUDE.md` cross-references resolve from the new location; the auto-load behavior on Claude Code session start continues to find it (Claude Code looks for `CLAUDE.md` in the working directory and walks up — the new location is `engine/CLAUDE.md`, which works if `cwd` is `engine/` at boot, or requires a root-level pointer otherwise; the pointer mechanism is settled in the session).
- `engine/STATE.md` references update; `engine/ENGINE_LOG.md` is the new path; `product/CHANGELOG.md` is the new path for the reserved stub.
- ADR partition decision documented in the session's outcome_summary plus an ENGINE_LOG entry under `Changed`.

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md) — for the current state and any updated migration notes added at S-0023 close.
- [`adr/0037-engine-product-wall-and-changelog-rename.md`](../adr/0037-engine-product-wall-and-changelog-rename.md) — the partition contract.
- [`ROADMAP.md`](../ROADMAP.md) — for `[ENGINE]` / `[PRODUCT]` phase markers as the reference distinction.
- [`engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md) and [`engine/operations/session-shutdown-sequence.md`](../engine/operations/session-shutdown-sequence.md) — to update path references and verify recovery procedures still hold.
- [`engine/operations/document-voice.md`](../engine/operations/document-voice.md) — the inward-voice contract; verify it cross-references the migrated paths correctly.
- [`adr/README.md`](../adr/README.md) — for the ADR index that gets split across `engine/adr/README.md` and `product/adr/README.md`.
- [`engine/tools/validate.py`](../engine/tools/validate.py) — to update file path constants (`REQUIRED_TOP_LEVEL`, `EXPECTED_FROM_S0002`, etc.).
- [`engine/tools/hooks/`](../engine/tools/hooks/) — for hook scripts whose path changes affect `.claude/settings.json` and `.git/hooks/pre-commit`.

## Load-bearing ADRs

- [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) — the partition shape and the sequencing constraint.
- [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — the inward-voice contract; migrated documents preserve the contract.
- [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) and [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md) — the rendering policy ADRs that, per ADR 0037, file under `product/adr/` because their consumer-of-record is learner-facing.

## ADR partition criterion (to settle in-session)

Each ADR files into one of:

- **`engine/adr/`** — ADRs about how the AI build apparatus works. Examples likely to land here: [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) (graph validation), [ADR 0022](../adr/0022-periodic-project-health-checks.md) (health checks), [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) (inward-doc voice), [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) itself.
- **`product/adr/`** — ADRs about Paideia as a product (pedagogy, learner model, curriculum, business). Examples: [ADR 0001](../adr/0001-pedagogical-edges-not-historical.md)–[ADR 0012](../adr/0012-freshman-defaults-autodidact-ceiling.md) (the strong working commitments), [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) (rendering policy — about how the AI talks to learners), [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md), [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md), [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md), [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0032](../adr/0032-personal-project-disposition.md) (Superseded), [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md), [ADR 0035](../adr/0035-multi-platform-apple-expansion.md).
- **Mixed / judgment-call** — ADRs that touch both. The judgment in-session settles each: which subtree has the load-bearing reader, which subtree is the citation-of-record. Candidates worth particular attention: [ADR 0013](../adr/0013-mastery-verification-organic-escalation.md)–[ADR 0021](../adr/0021-node-deprecation-status-superseded-by.md) (architectural decisions about the schema and engine internals — likely engine, but [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md) and [ADR 0017](../adr/0017-postgres-recursive-ctes-over-owl-rdf.md) sit at the boundary), [ADR 0023](../adr/0023-engagement-depth-aggregation.md)–[ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md) (mastery / learner-storage decisions — likely product because they describe learner-state representation).

The migration session names its partition for every ADR in the session's outcome_summary and in the ENGINE_LOG entry. Both `engine/adr/README.md` and `product/adr/README.md` carry their post-migration indexes.

## Estimated context budget

Mechanical/procedural tier: target 70%, cap 80%. The session is mostly `git mv` and find-and-replace across cross-references; the substantive judgment is the ADR partition. If the cross-reference sweep proves more substantial than expected, the session halts at the `git mv` boundary and a follow-up session ([`M_partition_migration_part2.md`](M_partition_migration_part2.md), authored at session close if needed) finishes the cross-reference sweep.

## Session sequencing

Single session preferred; two-session fallback acceptable. The natural split between sessions is:

- **Session 1:** ADR partition decision, `git mv` execution, top-level reference updates (`STATE.md`, `ROADMAP.md`, `README.md`, `.claude/settings.json`, `.git/hooks/pre-commit` symlink retarget).
- **Session 2 (if needed):** cross-reference sweep across migrated docs, validator clean.

## Risks and mitigations

- **Pre-commit hook breaks at first commit.** The hook lives at `tools/hooks/pre-commit` (now `engine/tools/hooks/pre-commit`); the parent repo's `.git/hooks/pre-commit` symlinks to it via relative path. The symlink target needs retargeting per the [recovery procedure](../engine/operations/session-build-lifecycle.md) added in S-0019. **Mitigation:** retarget the symlink as the first action after the first `git mv` batch; verify with a no-op commit before continuing.
- **Capture hook fires against wrong path.** `.claude/settings.json` references `tools/hooks/mempalace-hook-wrapper.sh`; post-migration this is `engine/tools/hooks/mempalace-hook-wrapper.sh`. **Mitigation:** update `.claude/settings.json` in the same commit as the wrapper move; verify with `: > .claude/logs/mempalace-hook.log` then a triggering message.
- **`tools/validate.py` `REQUIRED_TOP_LEVEL` references break.** The validator names `STATE.md`, `ENGINE_LOG.md`, etc. as required top-level files. Post-migration these are `engine/STATE.md`, `engine/ENGINE_LOG.md`. **Mitigation:** update the constants in the same commit as the file moves; the validator's own file moves to `engine/tools/validate.py` and the constants reference the new top-level absolute paths from the repo root.
- **CROSS_REFERENCES.md gets stale.** Every link in [`product/docs/CROSS_REFERENCES.md`](../product/docs/CROSS_REFERENCES.md) (which moves to `product/docs/CROSS_REFERENCES.md`) needs updating. **Mitigation:** run the validator's `cross_reference_broken` check after every batch of cross-reference updates; the soft-warn count surfaces stale links immediately.
- **CLAUDE.md auto-load behavior.** Claude Code looks for `CLAUDE.md` in the working directory by default. Post-migration, the file lives at `engine/CLAUDE.md`. **Mitigation:** decide in-session whether to (a) keep a thin `CLAUDE.md` symlink at root pointing at `engine/CLAUDE.md`, (b) keep a thin orientation pointer at root, or (c) require sessions to `cd engine/` at boot. Option (b) is least disruptive; the root pointer can carry the same auto-load content under `engine/`.

## Open tensions consumed

None directly; the migration is the execution of a settled ADR. The session may surface partition-criterion edge cases that warrant new ADRs; if so, those are authored in-session per the [ADR authoring procedure](../engine/operations/adr-authoring.md).

## What lands in ENGINE_LOG

A `Changed` entry under `[Unreleased]` enumerating: ADR partition decisions, top-level file moves, hook reconfigurations, validator-constant updates, cross-reference updates touched. The entry is large by the material-change criteria — every moved file is a material engine change.

## See also

- [`../adr/0037-engine-product-wall-and-changelog-rename.md`](../adr/0037-engine-product-wall-and-changelog-rename.md) — the partition contract.
- [`engine/operations/session-build-lifecycle.md`](../engine/operations/session-build-lifecycle.md) — the recovery section for hook / symlink retargeting.
- [`engine/operations/tools-validate-interpretation.md`](../engine/operations/tools-validate-interpretation.md) — `cross_reference_broken` soft-warn category.
- [`engine/STATE.md`](../engine/STATE.md) — names this chunk as the next-session work item at S-0023 close.
