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

The engine collection has **17 ADRs total — all Accepted**. Engine ADRs are about how the build apparatus works (graph validation infrastructure, periodic project audits, expression contracts for engine-internal documents and engine-side code, the engine/product partition itself, the universal expression contract spanning all AI authoring patterns, the build-readiness gate before substantive build sessions, cascade-analysis discipline, soft-warn lifecycle, the harness hook architecture, the recipe-vs-reference skill-conversion partition, shared-state integrity discipline, the structural-reference parser tool, HANDOFF/Issues split for cross-session deferrals, scope-lock at boot + descope/reorder audit, project venv with hook PATH wiring, routine-mode session pattern). The full ADR collection across the project is **51** (17 engine + 34 product).

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
