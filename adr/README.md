# Architecture Decision Records

> Settled architectural decisions. Each ADR is durable, structured, and citable — the **contract layer** of two-layer decision recording (per `CLAUDE.md`). The **story layer** (verbatim conversational reasoning) lives in MemPalace `decision`-tagged drawers.

ADRs answer **"what's settled?"**. MemPalace answers **"have we considered X before?"**. Neither replaces the other.

## Authoring guidance

Full procedure — Nygard template, status conventions, when an ADR is warranted, and the ADR-vs-CHANGELOG-vs-MemPalace boundary — lives in [`docs/operations/adr-authoring.md`](../docs/operations/adr-authoring.md). This README only indexes the collection.

## Status conventions (quick reference)

| Status | Meaning |
|---|---|
| `Proposed` | Drafted but not yet committed-to. Rare — most ADRs start at `Accepted`. |
| `Accepted` | In force. Downstream files and code may rely on it. Default for newly authored ADRs. |
| `Deprecated` | No longer in force; no replacement exists. ADR remains in place — it carries the historical reasoning. |
| `Superseded by ADR NNNN` | Replaced by a newer ADR. Pointer is one-directional (older → newer). |

The `Status:` field is required; `tools/validate.py` soft-warns on ADR files missing it.

## Index

The Phase 0 collection (ADRs 0001–0022) landed in S-0003. ADRs 0001–0012 absorb the 12 strong working commitments from `docs/MISSION.md` / `ROADMAP.md`. ADRs 0013–0022 absorb the 10 architectural decisions previously held in `design-reasoning.md` (now retired) plus two decisions that emerged in the S-0001 plan conversation (0016, 0022). Phase 1 ADRs (0023 onward) accumulate as Contract Lock work proceeds; ADRs 0023–0024 landed in S-0004 (engagement-depth aggregation, prompt-pack Session 9), ADR 0025 landed in S-0006 (historical maximum tracking, prompt-pack Session 11), and ADR 0026 landed in S-0007 (privacy posture, inserted ahead of Phase 1.2 rendering policy). Phase 1.1 closed at S-0006 with all three pending prompt-pack sessions (9, 10, 11) settled; Phase 1.2 (rendering policy) moves to S-0008.

### Strong working commitments (ADRs 0001–0012)

| ADR | Title | Status |
|---|---|---|
| [0001](0001-pedagogical-edges-not-historical.md) | Pedagogical edges, not historical | Accepted |
| [0002](0002-commercial-sustainability-without-pedagogical-compromise.md) | Commercial sustainability without pedagogical compromise | Accepted |
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

### Architectural decisions (ADRs 0013–0022)

| ADR | Title | Status |
|---|---|---|
| [0013](0013-mastery-verification-organic-escalation.md) | Mastery verification as organic escalation | Accepted |
| [0014](0014-sonnet-teaches-opus-reviews.md) | Sonnet teaches, Opus reviews | Accepted |
| [0015](0015-event-sourced-learner-model.md) | Event-sourced learner model | Accepted |
| [0016](0016-graph-construction-needs-live-validation.md) | Graph construction needs live validation | Accepted |
| [0017](0017-postgres-recursive-ctes-over-owl-rdf.md) | Postgres + recursive CTEs over OWL/RDF | Accepted |
| [0018](0018-flat-domain-tags-community-detection.md) | Flat domain tags + community detection | Accepted |
| [0019](0019-two-column-rigor-score-override.md) | Two-column rigor score override model | Accepted |
| [0020](0020-teaching-notes-separate-from-summary.md) | Teaching notes separate from summary | Accepted |
| [0021](0021-node-deprecation-status-superseded-by.md) | Node deprecation via status + superseded_by | Accepted |
| [0022](0022-periodic-project-health-checks.md) | Periodic project health checks | Accepted |

### Phase 1 — Contract Lock (ADRs 0023–)

| ADR | Title | Status |
|---|---|---|
| [0023](0023-engagement-depth-aggregation.md) | Engagement-depth aggregation: weighted geometric mean | Accepted |
| [0024](0024-engagement-depth-sub-signals-stored-raw.md) | Engagement-depth sub-signals stored raw, composite derived | Accepted |
| [0025](0025-historical-maximum-tracking.md) | Historical maximum tracking on `mastery_snapshots` | Accepted |
| [0026](0026-persistent-learner-storage-structural-not-substantive.md) | Persistent learner storage is structural, not substantive | Accepted |

## Adding a new ADR

1. Pick the next unused 4-digit number.
2. Filename: `NNNN-kebab-case-title.md`.
3. Use the Nygard template from [`docs/operations/adr-authoring.md`](../docs/operations/adr-authoring.md).
4. Add a row to the index above in the same commit.
5. Add a CHANGELOG entry under `[Unreleased]` → `Added`.
6. (If the ADR resolves an open tension) update `docs/tensions.md`.
7. Capture the conversational reasoning that produced the ADR in a MemPalace `decision`-tagged drawer (verbatim form, recall-by-similarity).

## When an ADR supersedes another

- The new ADR carries `Status: Accepted` and a `Supersedes: ADR NNNN` line in the header.
- The old ADR's `Status:` flips to `Superseded by ADR NNNN` (one-directional pointer).
- The old ADR file is **not deleted** — the historical reasoning remains queryable.
- CHANGELOG records both: `Added` for the new ADR, `Changed` for the supersession.
