# Engine Architecture Decision Records

> Settled architectural decisions about **the AI build apparatus** — how the user and Claude run together to construct Paideia. Validators, hooks, session lifecycle, MemPalace integration, operations conventions, expression contracts for inward documentation. Companion index: [`product/adr/README.md`](../../product/adr/README.md) carries decisions about Paideia-the-product (pedagogy, learner model, schema, business, runtime architecture).
>
> The engine/product partition is committed in [ADR 0037](0037-engine-product-wall-and-changelog-rename.md).

ADRs are durable, structured, and citable — the **contract layer** of two-layer decision recording (per `CLAUDE.md`). The **story layer** (verbatim conversational reasoning) lives in MemPalace `decision`-tagged drawers.

ADRs answer **"what's settled?"**. MemPalace answers **"have we considered X before?"**. Neither replaces the other.

## Authoring guidance

Full procedure — Nygard template, status conventions, when an ADR is warranted, and the ADR-vs-ENGINE_LOG-vs-MemPalace boundary — lives in [`../operations/adr-authoring.md`](../operations/adr-authoring.md). This README only indexes the engine collection.

## Status conventions (quick reference)

| Status | Meaning |
|---|---|
| `Proposed` | Drafted but not yet committed-to. Rare — most ADRs start at `Accepted`. |
| `Accepted` | In force. Downstream files and code may rely on it. Default for newly authored ADRs. |
| `Deprecated` | No longer in force; no replacement exists. ADR remains in place — it carries the historical reasoning. |
| `Superseded by ADR NNNN` | Replaced by a newer ADR. Pointer is one-directional (older → newer). |

The `Status:` field is required; `engine/tools/validate.py` soft-warns on ADR files missing it.

## Index

The engine collection has **44 ADRs total — all Accepted**. Engine ADRs are about how the build apparatus works (graph validation infrastructure, periodic project audits, expression contracts for engine-internal documents and engine-side code, the engine/product partition itself, the universal expression contract spanning all AI authoring patterns, the build-readiness gate before substantive build sessions, cascade-analysis discipline, soft-warn lifecycle, the harness hook architecture, the recipe-vs-reference skill-conversion partition, shared-state integrity discipline, the structural-reference parser tool, HANDOFF/Issues split for cross-session deferrals, scope-lock at boot + descope/reorder audit, project venv with hook PATH wiring, routine-mode session pattern, mechanism-first-exercise gate, lifecycle-push wrapping for routine AND build modes, apply-migration wrapping, MemPalace mechanical adoption checks, adversarial stance for health-check audits, canonical timestamp format and shared helper, audit-time structural-reference fetching for verdict fortification, secret-scan + SAST pre-commit gates, automated dependency vulnerability surfacing, project-wired code-review and security-review skills, project-wired frontend-discipline + paideia-frontend-overlays skills with core-invariant-plus-project-tailoring architectural posture, pytest-cov coverage gate with measured floor, GitHub issue templates mechanizing the body-shape posture, revert and rollback discipline, HNSW sync_threshold tuning for cross-session metadata persistence). The full ADR collection across the project is **81** (44 engine + 37 product).

| ADR | Title | Status |
|---|---|---|
| [0016](0016-graph-construction-needs-live-validation.md) | Graph construction needs live validation | Accepted |
| [0022](0022-periodic-project-health-checks.md) | Periodic project health checks | Accepted |
| [0036](0036-expression-contract-for-inward-documents.md) | Expression contract for inward-facing documentation | Accepted |
| [0037](0037-engine-product-wall-and-changelog-rename.md) | Engine / product wall; CHANGELOG.md renames to ENGINE_LOG.md | Accepted |
| [0038](0038-expression-contract-for-ai-authored-code.md) | Expression contract for AI-authored code | Accepted |
| [0039](0039-universal-expression-contract-across-ai-authoring-patterns.md) | Universal expression contract across AI authoring patterns | Accepted |
| [0040](0040-build-readiness-gate-before-substantive-build-sessions.md) | Build-readiness gate before substantive build sessions | Accepted |
| [0041](0041-cascade-analysis-discipline.md) | Cascade-analysis discipline: mechanical checks plus manual procedures | Accepted |
| [0042](0042-soft-warn-lifecycle-archive-canon.md) | Soft-warn lifecycle: persistent warns surface at boot; archive is canon | Accepted |
| [0043](0043-hook-architecture.md) | Hook architecture: enforce two-layer recording, surface cadence, verify STATE.md fields | Accepted |
| [0044](0044-skill-conversion-recipe-vs-reference.md) | Skill conversion: recipe-shaped procedures become Skills; reference docs stay docs | Accepted |
| [0045](0045-shared-state-integrity-discipline.md) | Shared-state integrity discipline: subprocess env scrubbing, atomic mempalace writes, boot-time health probes | Accepted |
| [0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md) | Structural-reference parser tool and adversarial-triage workflow | Accepted |
| [0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) | HANDOFF.md narrowed to session-internal handoffs; GitHub Issues absorb cross-session deferrals | Accepted |
| [0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) | Scope-lock at boot, descope/reorder audit at shutdown, session-end context telemetry | Accepted |
| [0050](0050-project-venv-and-hook-path-wiring.md) | Project venv (uv-managed) at main repo root with hook PATH wiring | Accepted |
| [0051](0051-routine-mode-and-engine-loop.md) | Routine-mode session pattern and engine-loop foundation | Accepted |
| [0052](0052-routine-boot-freshness-and-concurrency-defense.md) | Routine-mode boot freshness and concurrency defense | Accepted |
| [0053](0053-mechanism-first-exercise-gate.md) | Mechanism-first-exercise gate for novel cross-cutting mechanisms | Accepted |
| [0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) | Lifecycle-push wrapping against the Default Branch Push gate | Accepted |
| [0055](0055-apply-migration-wrapping-against-production-reads-gate.md) | Apply-migration wrapping against the Production Reads gate | Accepted |
| [0056](0056-mempalace-mechanical-adoption-checks.md) | MemPalace mechanical adoption checks | Accepted |
| [0057](0057-adversarial-stance-for-health-check-audits.md) | Adversarial stance for project health-check audits | Accepted |
| [0058](0058-canonical-timestamp-format-and-helper.md) | Canonical timestamp format and shared timestamps.py helper | Accepted |
| [0059](0059-audit-time-structural-reference-fetching.md) | Audit-time fetching of public structural references for verdict fortification | Accepted |
| [0060](0060-routine-wedge-detect-and-pause.md) | Routine wedge detect-and-pause | Accepted |
| [0062](0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) | Retire ADR inline-amendment pattern + governed-doc validator soft-warns | Accepted |
| [0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) | Validator tiered runtime targets + per-phase regression soft-warn | Accepted |
| [0064](0064-uv-lockfile-and-reproducible-builds.md) | `uv` lockfile + reproducible dependency builds | Accepted |
| [0065](0065-validate-py-mirror-to-ci.md) | Mirror `validate.py` gate to GitHub Actions CI | Accepted |
| [0066](0066-pr-template-and-branch-protection.md) | PR template + branch protection on `main` | Accepted |
| [0067](0067-gitleaks-pre-commit-secret-scanning.md) | `gitleaks` pre-commit secret scanning + GitHub-native scanning | Accepted |
| [0068](0068-bandit-sast-pre-commit-and-ci.md) | `bandit` SAST in pre-commit + CI | Accepted |
| [0069](0069-dependabot-pip-and-actions-ecosystems.md) | Dependabot for `pip` and `github-actions` ecosystems | Accepted |
| [0070](0070-project-wired-review-skill.md) | Project-wired `/review` skill (five-axis + Paideia overlays) | Accepted |
| [0071](0071-project-wired-security-review-skill.md) | Project-wired `/security-review` skill (OWASP Top 10 + Paideia overlays) | Accepted |
| [0072](0072-frontend-discipline-skill.md) | Project-wired `/frontend-discipline` skill (invariant core) | Accepted |
| [0073](0073-paideia-frontend-overlays-skill.md) | Project-wired `/paideia-frontend-overlays` skill (project tailoring) | Accepted |
| [0074](0074-pytest-cov-coverage-floor.md) | `pytest-cov` coverage reporting with measured floor | Accepted |
| [0075](0075-github-issue-templates.md) | GitHub issue templates for the eight type labels | Accepted |
| [0076](0076-build-mode-lifecycle-push-wrapping.md) | Build-mode lifecycle-push wrapping (sibling to ADR 0054) | Accepted |
| [0077](0077-adr-template-alternatives-considered-section.md) | ADR template gains "Alternatives Considered" section; Deprecated ADRs join the back-reference orphan check | Accepted |
| [0078](0078-revert-and-rollback-discipline.md) | Revert and rollback discipline | Accepted |
| [0079](0079-hnsw-sync-threshold-tuning.md) | HNSW sync_threshold tuning for cross-session metadata persistence | Accepted |

## Adding a new engine ADR

1. Pick the next unused 4-digit number from the **shared** ADR numbering pool (engine + product use a single sequence per ADR 0037 — numbers do not duplicate across the partition).
2. Filename: `NNNN-kebab-case-title.md`.
3. Use the Nygard template from [`../operations/adr-authoring.md`](../operations/adr-authoring.md).
4. Add a row to the index above in the same commit.
5. Add an entry to [`../ENGINE_LOG.md`](../ENGINE_LOG.md) under `[Unreleased]` → `Added`.
6. (If the ADR resolves an open tension) update [`../../product/docs/tensions.md`](../../product/docs/tensions.md).
7. Capture the conversational reasoning that produced the ADR in a MemPalace `decision`-tagged drawer (verbatim form, recall-by-similarity).

## Engine vs product — partition criterion

An ADR files under `engine/adr/` if its load-bearing reader is the build apparatus itself: validators, hooks, session-lifecycle docs, operations conventions, the AI-and-user collaboration model, expression contracts for inward documentation. An ADR files under `product/adr/` if its load-bearing reader is Paideia-as-a-product: pedagogy, learner model, schema, runtime architecture, business, deployment, rendering policy (because the consumer-of-record for rendering policy is learner-facing prose, per [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) edge-case (a)).

Edge cases settle at the time of authoring or via supersession; the partition is reversible per file. See [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) for the full criterion and the migration history.

## When an ADR supersedes another

- The new ADR carries `Status: Accepted` and a `Supersedes: ADR NNNN` line in the header.
- The old ADR's `Status:` flips to `Superseded by ADR NNNN` (one-directional pointer).
- The old ADR file is **not deleted** — the historical reasoning remains queryable.
- ENGINE_LOG records both: `Added` for the new ADR, `Changed` for the supersession.
- Supersession can cross the engine/product partition; the new ADR files in whichever subtree fits its load-bearing reader.
