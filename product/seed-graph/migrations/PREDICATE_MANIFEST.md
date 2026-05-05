# product/seed-graph/migrations/PREDICATE_MANIFEST.md — Canonical edge-type registry

> Canonical registry of edge predicates used in `public.edges`. The v1 registry was authored at S-0037 per the [Phase 4 build-readiness gate](../../../engine/build_readiness/phase_4_graph_validation.md) (T2-G); subsequent additions land in the same session that introduces a new predicate, paired with an ENGINE_LOG entry under `Added`.

## Why this file exists

Every edge in the Paideia graph carries an `edge_type` field naming its predicate. The schema layer leaves `edge_type` unconstrained (per [`product/docs/architecture.md`](../../docs/architecture.md) "Edge Schema"); validation lives here and at [`engine/tools/validate.py`](../../../engine/tools/validate.py)'s graph audit per [ADR 0016](../../../engine/adr/0016-graph-construction-needs-live-validation.md). The audit reads the registry and soft-warns on any edge whose `edge_type` is absent — `undeclared_predicate` per [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md).

A free-form `edge_type` accumulates schema drift silently across sessions: different sessions inventing equivalent-but-not-identical names (`is_prerequisite_for` vs `prerequisite` vs `pedagogical_prerequisite`) until an audit discovers a long tail of variants. The registry closes that loop — adding a predicate is an explicit act, recorded in the same commit that uses it.

## Adding a new predicate

1. Add a row to the **Predicate registry** table below in the same session that uses the new predicate.
2. Record the addition under `Added` in [`engine/ENGINE_LOG.md`](../../../engine/ENGINE_LOG.md) `[Unreleased]`.
3. Name the predicate's domain (the column type or table the source side draws from), range (the same for the target side), cardinality, and a short description.

The audit catches drift; this manifest closes the loop by making the catch's resolution unambiguous.

## Predicate registry

The v1 registry contains the two predicates current design documents commit to:

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `pedagogical_prerequisite` | `nodes` | `nodes` | many-to-many | Source node is a prerequisite for understanding target node. The structural edge type used in graph traversal, syllabus generation, and mastery computation per [`product/docs/architecture.md`](../../docs/architecture.md) "Edge Schema". Default value for `public.edges.edge_type` per [`0003_edges.sql`](0003_edges.sql) and the only edge type the Phase 4 audit's three hard-fail checks (duplicate IDs, dangling references, cycle detection via Kosaraju SCC) restrict to. |
| `historical_influence` | `nodes` | `nodes` | many-to-many | Source concept historically influenced target concept's development. Display-only (Discovery surface annotation) per [`product/docs/architecture.md`](../../docs/architecture.md) "Edge Schema"; not consumed by traversal, syllabus generation, or mastery computation. May legitimately form cycles (mutual influence between two thinkers' concepts is not a structural error), so the audit's cycle detection ignores this type. |

## Reserved-but-unused predicates

Predicates considered during prior design or named in build-plan illustrative lists but not yet committed to in v1. Listed here so future sessions don't reinvent them under different names; **using one of these in an INSERT requires moving the row to the registry above first** (in the same session, paired with an ENGINE_LOG entry).

The `cross_domain_dependency` reserved row was removed at S-0075 closing the [phase_5.md T1-E / T3-B](../../../engine/build_readiness/phase_5.md) deferral. The S-0075 cross-bridges authoring (P5-11; [`0060_seed_crossbridges_part1.sql`](0060_seed_crossbridges_part1.sql)) explicitly adjudicated whether to formally introduce `cross_domain_dependency` or continue the existing disjoint-domain convention (cross-domain edges as `pedagogical_prerequisite` with source and target carrying disjoint `domain[]` arrays). Decision: continue the convention. Reasoning: every cross-domain edge authored in 0060 is shape-identical to within-domain `pedagogical_prerequisite` — same predicate semantics, same domain/range typing, same downstream consumer behavior; the only distinguishing feature is the disjoint-domain shape that the validator's `suspicious_cross_domain_ratio` soft-warn already detects. Cross-bridges authoring did not surface a structural distinction warranting a separate predicate. Per the discipline below ("If a reserved entry never gets used by the time the next periodic project health check fires, it should be removed from this list"), the row is removed in the same commit. The reserved status was held since the phase 4 graph-validation gate per [phase_4_graph_validation.md](../../../engine/build_readiness/phase_4_graph_validation.md) T2-G (which settled the v1 registry at two predicates).

| Predicate | Source | Status |
|---|---|---|
| `enables` | [`build_plan/P_2_graph_validation.md`](../../../build_plan/P_2_graph_validation.md) illustrative list | Reserved; no current design document commits to it. |
| `informed_by` | [`build_plan/P_2_graph_validation.md`](../../../build_plan/P_2_graph_validation.md) illustrative list | Reserved; no current design document commits to it. |

If a reserved entry never gets used by the time the next periodic project health check fires, it should be removed from this list (per [ADR 0022](../../../engine/adr/0022-periodic-project-health-checks.md) audit categories). Reserved is a forward-pointer, not permanent.

## See also

- [ADR 0016](../../../engine/adr/0016-graph-construction-needs-live-validation.md) — graph construction needs live validation; the registry's audit consumer.
- [`engine/build_readiness/phase_4_graph_validation.md`](../../../engine/build_readiness/phase_4_graph_validation.md) — Phase 4 build-readiness gate; v1 registry contents authored per T2-G.
- [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md) — `undeclared_predicate` soft-warn meaning and response posture.
- [`product/docs/architecture.md`](../../docs/architecture.md) — graph schema; the source-of-truth for predicate domain/range expectations.
- [`0003_edges.sql`](0003_edges.sql) — `public.edges.edge_type` column declaration; default `pedagogical_prerequisite`.
