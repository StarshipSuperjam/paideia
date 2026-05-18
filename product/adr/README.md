# Product Architecture Decision Records

> Settled architectural decisions about **Paideia as a product** — pedagogy, learner model, curriculum, schema, runtime architecture, business, deployment. Companion index: [`engine/adr/README.md`](../../engine/adr/README.md) carries decisions about the AI build apparatus.
>
> The engine/product partition is committed in [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md).

ADRs are durable, structured, and citable — the **contract layer** of two-layer decision recording (per `CLAUDE.md`). The **story layer** (verbatim conversational reasoning) lives in MemPalace `decision`-tagged drawers.

ADRs answer **"what's settled?"**. MemPalace answers **"have we considered X before?"**. Neither replaces the other.

## Authoring guidance

Full procedure — Nygard template, status conventions, when an ADR is warranted, and the ADR-vs-ENGINE_LOG-vs-MemPalace boundary — lives in [`../../engine/operations/adr-authoring.md`](../../engine/operations/adr-authoring.md). This README only indexes the product collection.

## Status conventions (quick reference)

| Status | Meaning |
|---|---|
| `Proposed` | Drafted but not yet committed-to. Rare — most ADRs start at `Accepted`. |
| `Accepted` | In force. Downstream files and code may rely on it. Default for newly authored ADRs. |
| `Deprecated` | No longer in force; no replacement exists. ADR remains in place — it carries the historical reasoning. |
| `Superseded by ADR NNNN` | Replaced by a newer ADR. Pointer is one-directional (older → newer). |

The `Status:` field is required; `engine/tools/validate.py` soft-warns on ADR files missing it.

## Index

The product collection has **43 ADRs total — 39 Accepted plus 4 Superseded** ([ADR 0002](0002-commercial-sustainability-without-pedagogical-compromise.md) by [ADR 0032](0032-personal-project-disposition.md); [ADR 0029](0029-personal-financial-cost-ceiling.md) by [ADR 0065](0065-oss-pivot-and-byok-disposition.md); [ADR 0032](0032-personal-project-disposition.md) by [ADR 0035](0035-multi-platform-apple-expansion.md); [ADR 0035](0035-multi-platform-apple-expansion.md) by [ADR 0065](0065-oss-pivot-and-byok-disposition.md)). The canonical project-wide ADR count lives in [`engine/STATE.md`](../../engine/STATE.md); the engine subtree carries the engine-side ADRs in [`engine/adr/`](../../engine/adr/). ADR numbers are drawn from a single shared sequence and do not duplicate across the partition. ADRs are grouped below by the structural role they play in the project.

### Strong working commitments (ADRs 0001–0012)

| ADR | Title | Status |
|---|---|---|
| [0001](0001-pedagogical-edges-not-historical.md) | Pedagogical edges, not historical | Accepted |
| [0002](0002-commercial-sustainability-without-pedagogical-compromise.md) | Commercial sustainability without pedagogical compromise | Superseded by [ADR 0032](0032-personal-project-disposition.md) |
| [0003](0003-supplementary-media-as-metadata-not-structure.md) | Supplementary media as metadata, not structure | Accepted |
| [0004](0004-relational-learner-model.md) | The learner model is relational | Accepted |
| [0005](0005-per-text-interpretive-outline.md) | Each text gets its own interpretive outline | Accepted |
| [0006](0006-domain-agnostic-architecture.md) | Domain-agnostic architecture | Accepted |
| [0007](0007-cross-domain-porosity.md) | All domains are mutually porous | Accepted |
| [0008](0008-concept-nodes-not-thinkers.md) | Nodes are concepts, not thinkers | Accepted |
| [0009](0009-portable-mastery.md) | Mastery is portable | Accepted |
| [0010](0010-continuous-contextual-assessment.md) | Assessment is continuous and contextual | Accepted |
| [0011](0011-no-hosted-copyrighted-material.md) | No hosted or distributed copyrighted material | Accepted |
| [0012](0012-freshman-defaults-autodidact-ceiling.md) | Freshman defaults, autodidact ceiling | Accepted |

### Architectural decisions (ADRs 0013–0021, product-side)

| ADR | Title | Status |
|---|---|---|
| [0013](0013-mastery-verification-organic-escalation.md) | Mastery verification as organic escalation | Accepted |
| [0014](0014-sonnet-teaches-opus-reviews.md) | Sonnet teaches, Opus reviews | Accepted |
| [0015](0015-event-sourced-learner-model.md) | Event-sourced learner model | Accepted |
| [0017](0017-postgres-recursive-ctes-over-owl-rdf.md) | Postgres + recursive CTEs over OWL/RDF | Accepted |
| [0018](0018-flat-domain-tags-community-detection.md) | Flat domain tags + community detection | Accepted |
| [0019](0019-two-column-rigor-score-override.md) | Two-column rigor score override model | Accepted |
| [0020](0020-teaching-notes-separate-from-summary.md) | Teaching notes separate from summary | Accepted |
| [0021](0021-node-deprecation-status-superseded-by.md) | Node deprecation via status + superseded_by | Accepted |

> [ADR 0016](../../engine/adr/0016-graph-construction-needs-live-validation.md) (graph validation infrastructure) and [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md) (periodic health checks) sit in this numerical range but file under `engine/adr/` because their load-bearing reader is the build apparatus.

### Phase 1 — Contract Lock (ADRs 0023–0032)

| ADR | Title | Status |
|---|---|---|
| [0023](0023-engagement-depth-aggregation.md) | Engagement-depth aggregation: weighted geometric mean | Accepted |
| [0024](0024-engagement-depth-sub-signals-stored-raw.md) | Engagement-depth sub-signals stored raw, composite derived | Accepted |
| [0025](0025-historical-maximum-tracking.md) | Historical maximum tracking on `mastery_snapshots` | Accepted |
| [0026](0026-persistent-learner-storage-structural-not-substantive.md) | Persistent learner storage is structural, not substantive | Accepted |
| [0027](0027-rendering-policy-prompt-layer-contract.md) | Rendering policy is the prompt-layer contract | Accepted |
| [0028](0028-input-side-scope-structural-not-prompt.md) | Input-side scope is structural, not prompt-policed | Accepted |
| [0029](0029-personal-financial-cost-ceiling.md) | Personal financial cost ceiling is an operating constraint | Superseded by [ADR 0065](0065-oss-pivot-and-byok-disposition.md) |
| [0030](0030-confidence-level-evidentiary-mode-on-nodes.md) | `confidence_level` is the evidentiary-mode axis on nodes | Accepted |
| [0031](0031-erasure-mechanism-and-individual-only-regime.md) | Erasure mechanism (hard-delete with cascade); individual-only data regime | Accepted |
| [0032](0032-personal-project-disposition.md) | Personal project disposition; refusal-not-deferral commercial closure (supersedes ADR 0002) | Superseded by [ADR 0035](0035-multi-platform-apple-expansion.md) |

### Phase 1.5 — Mission Realignment (ADRs 0033–0035, product-side)

| ADR | Title | Status |
|---|---|---|
| [0033](0033-mission-realignment-structured-guidance-for-self-learners.md) | Mission realignment: structured guidance for self-learners; globe / reward visual-system obsolescence | Accepted |
| [0034](0034-discovery-planning-engagement-triad.md) | Discovery / Planning / Engagement triad as primary product structure | Accepted |
| [0035](0035-multi-platform-apple-expansion.md) | Multi-platform Apple expansion; iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad (supersedes ADR 0032) | Superseded by [ADR 0065](0065-oss-pivot-and-byok-disposition.md) |

> [ADR 0036](../../engine/adr/0036-expression-contract-for-inward-documents.md) (expression contract for inward-facing documentation) and [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md) (engine/product wall) sit in this numerical range but file under `engine/adr/` because they govern engine-internal practice.

### Phase 4.5 — Input Dataset Survey (ADR 0046, product-side)

| ADR | Title | Status |
|---|---|---|
| [0046](0046-structural-reference-posture-extends-to-philosophy-reference-works.md) | Structural-reference posture extends to philosophy reference works as a class | Accepted |

> ADRs 0038–0045 sit in the numerical range between Phase 1.5 and Phase 4.5 but file under `engine/adr/` (engine-internal expression contracts, build-readiness gate, cascade discipline, soft-warn lifecycle, hook architecture, skill conversion, shared-state integrity); see [`engine/adr/README.md`](../../engine/adr/README.md) for the engine collection.

### Phase 5 — Seed Graph Build (ADR 0052, product-side)

| ADR | Title | Status |
|---|---|---|
| [0052](0052-phase-5-philosophy-subdomain-decomposition.md) | Phase 5 philosophy-subdomain decomposition: 9 subjects + services + cross-bridges + closeout | Accepted |

> ADRs 0047–0051 sit in the numerical range between Phase 4.5 and Phase 5 but file under `engine/adr/` (structural-reference parser tool, HANDOFF/Issues split, scope-lock + descope-reorder audit, project venv + hook PATH wiring, routine-mode and engine loop); see [`engine/adr/README.md`](../../engine/adr/README.md) for the engine collection.

### Phase 5 — Production-audit closeout (ADR 0061, product-side)

| ADR | Title | Status |
|---|---|---|
| [0061](0061-historical-influence-retyping-for-history-terminator-bridges.md) | Retype history-terminator cross-bridges from pedagogical_prerequisite to historical_influence | Accepted |

> ADRs 0053–0060 sit in the numerical range between Phase 5 and the production-audit closeout but file under `engine/adr/` (mechanism-first-exercise gate, lifecycle-push wrapping, apply-migration wrapping, MemPalace mechanical adoption checks, adversarial-stance audit posture, canonical-timestamp helper, audit-time fetcher, routine-wedge detect-and-pause); see [`engine/adr/README.md`](../../engine/adr/README.md) for the engine collection.

### OSS pivot (ADR 0065, product-side; supersedes ADRs 0029 + 0035)

| ADR | Title | Status |
|---|---|---|
| [0065](0065-oss-pivot-and-byok-disposition.md) | OSS pivot and BYOK disposition; open-source under Apache 2.0, users bring their own Anthropic key (supersedes ADRs 0029 + 0035) | Accepted |

> ADRs 0062–0064 sit in the numerical range between the production-audit closeout and the OSS pivot but file under `engine/adr/` (retire-ADR-inline-amendments + governed-doc soft-warns; validator tiered runtime targets; uv lockfile + reproducible builds); see [`engine/adr/README.md`](../../engine/adr/README.md) for the engine collection.

### Phase 6 entry — OQ-DEC1 tension-set settlement (ADRs 0085–0088, product-side)

| ADR | Title | Status |
|---|---|---|
| [0085](0085-server-side-mastery-computation-confirmed.md) | Server-side mastery computation confirmed (settles OQ-DEC1-A) | Accepted |
| [0086](0086-model-agnostic-embedding-storage-architecture.md) | Model-agnostic embedding storage architecture (per-dim partition tables; settles OQ-DEC1-C) | Accepted |
| [0087](0087-two-hop-neighborhood-retrieval-shape.md) | Two-hop neighborhood retrieval shape (prereq+historical_influence edge filter; presumed-match alias resolution; settles OQ-DEC1-B) | Accepted |
| [0088](0088-sep-chunk-resolver-index.md) | SEP chunk-resolver index for node-level onward-reading pointers (`sep_chunks` junction table with graceful article-level degradation; settles OQ-DEC1-D) | Accepted |

> The next available shared ADR number entering S-0152 was 0085 (engine ADRs 0066–0084 already occupied 0066–0084 in the shared sequence per ADR 0037). The four OQ-DEC1 settlements draw from the 0085–0088 range accordingly.

### PDG papers extraction pre-phase — Session δ₁ foundational ADRs (ADRs 0093–0094, product-side)

| ADR | Title | Status |
|---|---|---|
| [0093](0093-phase-6-product-trajectory-formalization.md) | Phase 6 product-trajectory formalization: learner-facing OSS+BYOK, no LMS bundling, web visualizer BYOK deferred | Accepted |
| [0094](0094-phase-6-scope.md) | Phase 6 scope: expand to include Tier-A substrate redesign (Clusters 1-5) before SEP/embedding self-correction work | Accepted |

> Session δ₁ (S-0202) landed the first two of Session δ's four foundational ADRs. The remaining two (tool-stack + learning-outcome taxonomy) plus the three Session-α coordination questions and the eight `kant_walkthrough.md` §6.7 D1-D8 schema items defer to Session δ₂+ per the S-0202 user-approved plan split. The PDG papers extraction pre-phase corpus lives at [`engine/build_readiness/pdg_papers_extraction/`](../../engine/build_readiness/pdg_papers_extraction/). Engine ADRs 0089–0092 occupied the 0089–0092 range between the OQ-DEC1 settlements and these ADRs in the shared sequence per ADR 0037.

## Adding a new product ADR

1. Pick the next unused 4-digit number from the **shared** ADR numbering pool (engine + product use a single sequence per ADR 0037 — numbers do not duplicate across the partition).
2. Filename: `NNNN-kebab-case-title.md`.
3. Use the Nygard template from [`../../engine/operations/adr-authoring.md`](../../engine/operations/adr-authoring.md).
4. Add a row to the index above in the same commit.
5. Add an entry to [`../../engine/ENGINE_LOG.md`](../../engine/ENGINE_LOG.md) under `[Unreleased]` → `Added`.
6. (If the ADR resolves an open tension) update [`../docs/tensions.md`](../docs/tensions.md).
7. Capture the conversational reasoning that produced the ADR in a MemPalace `decision`-tagged drawer (verbatim form, recall-by-similarity).

## Engine vs product — partition criterion

An ADR files under `product/adr/` if its load-bearing reader is Paideia-as-a-product: pedagogy, learner model, schema, runtime architecture, business, deployment, rendering policy (because the consumer-of-record for rendering policy is learner-facing prose, per [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md) edge-case (a)). An ADR files under `engine/adr/` if its load-bearing reader is the build apparatus itself.

Edge cases settle at the time of authoring or via supersession; the partition is reversible per file. See [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md) for the full criterion and the migration history.

## When an ADR supersedes another

- The new ADR carries `Status: Accepted` and a `Supersedes: ADR NNNN` line in the header.
- The old ADR's `Status:` flips to `Superseded by ADR NNNN` (one-directional pointer).
- The old ADR file is **not deleted** — the historical reasoning remains queryable.
- ENGINE_LOG records both: `Added` for the new ADR, `Changed` for the supersession.
- Supersession can cross the engine/product partition; the new ADR files in whichever subtree fits its load-bearing reader.
