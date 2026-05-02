# P_5 — Retrieval / mastery-inference architecture decisions (Phase DEC.1)

> Sits between Phase 5 (seed graph mature) and Phase 6 (self-correction pipeline). After the seed graph is mature, retrieval-shape decisions become testable; before the teaching layer is built, they are load-bearing.

## Phase scope

Phase DEC.1 closes four open tensions tracked in [`product/docs/tensions.md`](../product/docs/tensions.md) since S-0001. Each settles as an ADR with `Status: Accepted` and a Phase-6 implementation tag. The decisions inform the schema's effective use, the teaching layer's input shape, and the self-correction pipeline's operating context.

The chunk is decision-dense; minimal new code. The work is judgment against the now-mature seed graph plus the existing schema and the existing engine.

## Output (four ADRs)

- **OQ-DEC1-A — Server-side mastery computation: confirm or revisit?** ADR settles whether mastery state lives server-side (computed from `mastery_snapshots` per [ADR 0023](../product/adr/0023-engagement-depth-aggregation.md), [ADR 0024](../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](../product/adr/0025-historical-maximum-tracking.md)) or distributed differently. Default direction is confirm; the open question is whether the mature seed graph surfaces a constraint that warrants revisitation.
- **OQ-DEC1-B — Two-hop neighborhood retrieval shape for teaching session context.** ADR settles the retrieval shape: how the teaching endpoint gets its context window. Likely: current concept node + one-hop prerequisite nodes + two-hop neighborhood for entity resolution. The decision constrains the teaching layer's prompt template at [`P_7_teaching_layer.md`](P_7_teaching_layer.md).
- **OQ-DEC1-C — Embedding strategy for entity resolution: pgvector + which embedding model.** ADR settles the embedding choice. pgvector is the default for the Postgres-anchored architecture per [ADR 0017](../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md); the model choice (OpenAI text-embedding-3-large, Voyage, Cohere, etc.) is the open variable.
- **OQ-DEC1-D — Chunk-resolver index for SEP onward-reading vs direct SEP URL pointers.** ADR settles whether SEP onward-reading recommendations resolve via a chunk-resolver index or via direct URL pointers. Direct URL pointers are simpler but coarser; chunk-resolver is finer-grained but requires index maintenance.

## Success criteria

- Four ADRs land at `Status: Accepted` (or `Proposed` if a decision genuinely cannot settle in-session — the `Proposed` fallback is rare per [`engine/operations/adr-authoring.md`](../engine/operations/adr-authoring.md)).
- Each ADR carries a Phase-6 implementation tag (specific guidance for [`P_6_self_correction.md`](P_6_self_correction.md) and [`P_7_teaching_layer.md`](P_7_teaching_layer.md)).
- Each `OQ-DEC1-*` entry in [`product/docs/tensions.md`](../product/docs/tensions.md) flips to `Resolved: YYYY-MM-DD` with the ADR cross-reference; the entry remains in place per the project's tension-resolution discipline.
- `engine/adr/README.md` index updated with the four new ADR rows under a new "Phase DEC.1 — Retrieval / Mastery Architecture" section (or per the engine ADR index structure post-`M_partition_migration`).
- ENGINE_LOG entry under `[Unreleased]` for `Added` (four ADRs).
- MemPalace `decision`-tagged drawer for each ADR per the [two-layer decision recording discipline](../engine/operations/adr-authoring.md).

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase DEC.1.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-DEC1-A` through `OQ-DEC1-D` entries.
- [`product/docs/architecture.md`](../product/docs/architecture.md) — schema; entity resolution service architecture.
- [`product/docs/learner-model.md`](../product/docs/learner-model.md) — mastery model.
- [`product/docs/reading-system.md`](../product/docs/reading-system.md) — SEP onward-reading context for OQ-DEC1-D.
- [`product/adr/0014-sonnet-teaches-opus-reviews.md`](../product/adr/0014-sonnet-teaches-opus-reviews.md) — Sonnet teaching context (informs OQ-DEC1-B retrieval shape).
- [`product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md`](../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md) — recursive CTE shape (informs OQ-DEC1-B).
- `product/seed-graph/migrations/` — the now-mature seed (informs all four decisions by giving them a concrete graph to test against). (Forward-pointing until `P_4` populates the seed.)

## Load-bearing ADRs

[ADR 0014](../product/adr/0014-sonnet-teaches-opus-reviews.md), [ADR 0017](../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md), [ADR 0023](../product/adr/0023-engagement-depth-aggregation.md), [ADR 0024](../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](../product/adr/0025-historical-maximum-tracking.md), [ADR 0029](../product/adr/0029-personal-financial-cost-ceiling.md) (cost-ceiling informs the embedding-model choice in OQ-DEC1-C).

## Estimated context budget

Substantive tier: target 60%, cap 70%. The work is decision-dense — read the open-question entries, read the relevant design docs and ADRs, weigh alternatives against the mature seed graph, settle each ADR. Four ADRs in one session is at the edge of substantive-extraction tolerance per [`engine/operations/adr-authoring.md`](../engine/operations/adr-authoring.md); if budget pressure surfaces, the session settles two ADRs, partial-closes, and a follow-up settles the remaining two.

## Session sequencing

Single session for two ADRs (OQ-DEC1-A and OQ-DEC1-B, the most coupled — server-side mastery shape constrains retrieval shape). Multi-session fallback: Session 1 settles OQ-DEC1-A and OQ-DEC1-B; Session 2 settles OQ-DEC1-C (embedding) and OQ-DEC1-D (chunk-resolver), which are more independent.

## Open tensions consumed

- `OQ-DEC1-A` — closed by ADR.
- `OQ-DEC1-B` — closed by ADR.
- `OQ-DEC1-C` — closed by ADR.
- `OQ-DEC1-D` — closed by ADR.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase DEC.1 — full phase scope.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-DEC1-*` entries.
- [`engine/operations/adr-authoring.md`](../engine/operations/adr-authoring.md) — Nygard template, status conventions, when an ADR is warranted.
- [`P_6_self_correction.md`](P_6_self_correction.md) and [`P_7_teaching_layer.md`](P_7_teaching_layer.md) — successors that consume these ADRs.
