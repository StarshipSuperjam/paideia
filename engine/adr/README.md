# Engine Architecture Decision Records

> Settled architectural decisions about **the AI build apparatus** — how the user and Claude run together to construct Paideia. Validators, hooks, session lifecycle, MemPalace integration, operations conventions, expression contracts for inward documentation. Companion index: [`product/adr/README.md`](../../product/adr/README.md) carries decisions about Paideia-the-product (pedagogy, learner model, schema, business, runtime architecture).
>
> The engine/product partition was committed in [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) and executed at S-0024.

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

The engine collection has **5 ADRs total — all Accepted**. Engine ADRs are about how the build apparatus works (graph validation infrastructure, periodic project audits, expression contracts for engine-internal documents and engine-side code, the engine/product partition itself). The full ADR collection across the project is **38** (5 engine + 33 product).

| ADR | Title | Status |
|---|---|---|
| [0016](0016-graph-construction-needs-live-validation.md) | Graph construction needs live validation | Accepted |
| [0022](0022-periodic-project-health-checks.md) | Periodic project health checks | Accepted |
| [0036](0036-expression-contract-for-inward-documents.md) | Expression contract for inward-facing documentation | Accepted |
| [0037](0037-engine-product-wall-and-changelog-rename.md) | Engine / product wall; CHANGELOG.md renames to ENGINE_LOG.md | Accepted |
| [0038](0038-expression-contract-for-ai-authored-code.md) | Expression contract for AI-authored code | Accepted |

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
