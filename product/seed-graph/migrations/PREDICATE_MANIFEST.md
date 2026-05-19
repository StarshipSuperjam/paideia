# product/seed-graph/migrations/PREDICATE_MANIFEST.md — Canonical edge-type registry

> Canonical registry of edge predicates used in `public.edges`. The v1 registry was authored at S-0037 per the [Phase 4 build-readiness gate](../../../engine/build_readiness/phase_4_graph_validation.md) (T2-G); subsequent additions land in the same session that introduces a new predicate, paired with an ENGINE_LOG entry under `Added`.

## Why this file exists

Every edge in the Paideia graph carries an `edge_layer` field (one of three values per ADR 0098 — `pedagogical_dependence` / `conceptual_relatedness` / `historical_influence`) and an `edge_type` field naming the per-layer sub-type. As of S-0208 per [ADR 0098](../../adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md), the schema layer constrains both via a compound CHECK on `(edge_layer, edge_type)` coupling to the 16-pair vocabulary below. Prior to S-0208, `edge_type` was intentionally unconstrained per [`product/docs/architecture.md`](../../docs/architecture.md) "Edge Schema"; that line is amended in-body by ADR 0098. Validation continues to live here and at [`engine/tools/validate.py`](../../../engine/tools/validate.py)'s graph audit per [ADR 0016](../../../engine/adr/0016-graph-construction-needs-live-validation.md). The audit reads the registry and soft-warns on any edge whose `edge_type` is absent — `undeclared_predicate` per [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md).

A free-form `edge_type` accumulated schema drift silently across sessions (different sessions inventing equivalent-but-not-identical names — `is_prerequisite_for` vs `prerequisite` vs `pedagogical_prerequisite` — until an audit discovered a long tail). The Cluster 2 vocabulary + the compound CHECK constraint structurally prevent drift now; this manifest remains the human/AI-facing registry where predicate semantics and domain/range are documented.

## Adding a new predicate

1. Add a row to the appropriate per-layer table in the **Predicate registry** below in the same session that uses the new predicate.
2. Extend the `edges_edge_layer_type_coupling` CHECK constraint in a new migration to include the new `(edge_layer, edge_type)` pair — per ADR 0098 premise 4 the extension is `ALTER TABLE ... DROP CONSTRAINT ... ADD CONSTRAINT` (no `ALTER TYPE` complexity).
3. Record the addition in the session's per-session changelog entry at `engine/changelog/<YYYY>/S-NNNN-*.md` per [ADR 0092](../../../engine/adr/0092-per-session-changelog-directory.md).
4. Name the predicate's domain (the column type or table the source side draws from), range (the same for the target side), cardinality, and a short description.

The CHECK constraint catches insert-time drift; this manifest closes the documentation loop.

## Predicate registry

Per [ADR 0098](../../adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md), edges live in three layers; each layer has its own controlled vocabulary. The `edges_edge_layer_type_coupling` CHECK constraint enforces these 16 pairs as the valid universe.

### Layer 1 — `pedagogical_dependence`

Edges encoding teaching-time dependency. Consumed by graph traversal, syllabus generation, mastery computation, and the Phase 4 audit's three hard-fail checks (duplicate IDs, dangling references, cycle detection via Kosaraju SCC). Post-Cluster-2 migration 0130, the 516 existing pedagogical-layer edges all carry `edge_type='soft_prerequisite'` (the epistemically conservative default per ADR 0098 premise 2 + synthesis line 101 — experts overstate necessity). Cluster 7 SQA predictive-validity pipeline will retype specific edges to other sub-types when learner-trace evidence supports.

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `hard_prerequisite` | `nodes` | `nodes` | many-to-many | Source must be mastered before target is teachable (SQA-validated). The strong version of pedagogical dependence; not the migration-default per ADR 0098 premise 2 (experts overstate necessity). |
| `soft_prerequisite` | `nodes` | `nodes` | many-to-many | Source is helpful before target but not strictly required. Post-Cluster-2 default for all 516 retyped pedagogical edges. |
| `helpful_bridge` | `nodes` | `nodes` | many-to-many | Source smooths the conceptual transition into target without being a prerequisite (synthesis paper_1:L116). |
| `co_requisite` | `nodes` | `nodes` | many-to-many | Source and target should be learned together; neither precedes the other (synthesis paper_2:L19). |
| `contrastive_link` | `nodes` | `nodes` | many-to-many | Source is taught against target (e.g., Husserl's phenomenology vs Cartesian dualism); contrast surfaces the concept. |
| `misconception_remediation` | `nodes` | `nodes` | many-to-many | Source is the corrective concept that target needs to displace (Cluster 5 misconception sub-graph alignment). |
| `example_of` | `nodes` | `nodes` | many-to-many | Source is a concrete example illustrating target concept (synthesis paper_2:L15). Cluster 4 node-type taxonomy informs the typing semantics. |
| `supports` | `nodes` | `nodes` | many-to-many | Source provides evidence/argument for target without being a logical prerequisite (synthesis paper_2:L15). |
| `assessed_before` | `nodes` | `nodes` | many-to-many | Source is assessed/tested before target in the curriculum sequence (synthesis paper_2:L15). |
| `unlearning_required_before` | `nodes` | `nodes` | many-to-many | Student must unlearn source's commonsense meaning before learning target (Cluster 5 misconception sub-graph alignment per synthesis line 184). |

### Layer 2 — `conceptual_relatedness`

Edges encoding theoretical affinity without dependency. Reserved-but-unused at the migration 0130 landing — no existing edge populates this layer post-Cluster-2. Cluster 5 (misconception sub-graph encoding) is the natural first author per synthesis cross-cutting observation 4 + ADR 0098 premise 5. Listed here so future sessions don't reinvent these names under different forms.

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `affinity_with` | `nodes` | `nodes` | many-to-many | Source and target share theoretical commitments without one depending on the other (synthesis paper_2:L19). |
| `contrasts_with` | `nodes` | `nodes` | many-to-many | Source and target occupy opposing positions in a theoretical landscape (e.g., Saussure vs Derrida per synthesis paper_2:L64). |
| `same_problem_family` | `nodes` | `nodes` | many-to-many | Source and target address variants of the same problem from different angles. |

### Layer 3 — `historical_influence`

Edges encoding diachronic influence. Display-only (Discovery surface annotation) per [`product/docs/architecture.md`](../../docs/architecture.md) "Edge Schema"; not consumed by traversal, syllabus generation, or mastery computation. May legitimately form cycles (mutual influence between two thinkers' concepts is not a structural error), so the audit's cycle detection ignores this layer. Post-Cluster-2 migration 0130, the 17 existing historical-layer edges all carry `edge_type='influenced_by'` (the most general sub-type per ADR 0098 premise 3 + synthesis line 98); ADR 0098 T2-A names a future historical-influence audit as the natural pass to retype specific edges to `received_via` / `reacted_against` where the framing fits.

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `influenced_by` | `nodes` | `nodes` | many-to-many | Source historically influenced target without claiming pedagogical necessity. Post-Cluster-2 default for all 17 retyped historical edges per ADR 0061 framing. |
| `received_via` | `nodes` | `nodes` | many-to-many | Source reached the modern reception via intermediary target (e.g., "Aristotle received_via Avicenna in medieval Europe"). |
| `reacted_against` | `nodes` | `nodes` | many-to-many | Source was articulated in deliberate opposition to target (e.g., "Quine reacted_against Carnap on analytic-synthetic"). |

## Reserved-but-unused / superseded predicates

Predicates considered during prior design or named in build-plan illustrative lists but not committed to in the current registry, AND predicates that were superseded by ADR 0098's three-layer taxonomy. Listed here so future sessions don't reinvent them under different names; **using one of the reserved entries in an INSERT requires moving the row to the registry above first** (in the same session, paired with a per-session changelog entry per ADR 0092 and a new migration extending the `edges_edge_layer_type_coupling` CHECK constraint per ADR 0098 premise 4).

The `cross_domain_dependency` reserved row was removed at S-0075 closing the [phase_5.md T1-E / T3-B](../../../engine/build_readiness/phase_5.md) deferral. The S-0075 cross-bridges authoring (P5-11; [`0060_seed_crossbridges_part1.sql`](0060_seed_crossbridges_part1.sql)) explicitly adjudicated whether to formally introduce `cross_domain_dependency` or continue the existing disjoint-domain convention (cross-domain edges as `pedagogical_prerequisite` with source and target carrying disjoint `domain[]` arrays). Decision: continue the convention. The reserved status was held since the phase 4 graph-validation gate per [phase_4_graph_validation.md](../../../engine/build_readiness/phase_4_graph_validation.md) T2-G (which settled the v1 registry at two predicates).

### Superseded by ADR 0098 (S-0208)

These predicates were the v1 registry's two entries; ADR 0098's three-layer taxonomy supersedes them. Migration 0130 retyped existing edges from these to the post-Cluster-2 defaults (`pedagogical_prerequisite` → `soft_prerequisite` under `pedagogical_dependence`; `historical_influence` → `influenced_by` under `historical_influence`). The compound CHECK constraint forbids new INSERTs with these values.

| Predicate | Superseded by | Status |
|---|---|---|
| `pedagogical_prerequisite` | `(pedagogical_dependence, soft_prerequisite)` and the other 9 pedagogical sub-types | Superseded at S-0208 per [ADR 0098](../../adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md); use the per-layer vocabulary. |
| `historical_influence` (as edge_type value) | `(historical_influence, influenced_by)` and the other 2 historical sub-types — note the layer name retains "historical_influence" but the edge_type value moves to per-sub-type vocabulary | Superseded at S-0208 per [ADR 0098](../../adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md); ADR 0061's predicate-class commitment is preserved in the layer name. |

### Reserved (no design commitment)

| Predicate | Source | Status |
|---|---|---|
| `enables` | [`build_plan/P_2_graph_validation.md`](../../../build_plan/P_2_graph_validation.md) illustrative list | Reserved; no current design document commits to it. |
| `informed_by` | [`build_plan/P_2_graph_validation.md`](../../../build_plan/P_2_graph_validation.md) illustrative list | Reserved; no current design document commits to it. |

If a reserved entry never gets used by the time the next periodic project health check fires, it should be removed from this list (per [ADR 0022](../../../engine/adr/0022-periodic-project-health-checks.md) audit categories). Reserved is a forward-pointer, not permanent.

## Node-side predicates: `node_type` vocabulary

S-0213 (ADR 0102 + migration 0140) introduces the `node_type TEXT[]` column on `public.nodes` with a 10-value per-element CHECK constraint enforced by `nodes_node_type_valid`. The vocabulary is registered here for parallel structure with the edge-side predicates above. The `undeclared_predicate` validator soft-warn at [`engine/tools/validate.py`](../../../engine/tools/validate.py) stays scoped to `edge_type` at landing — extending to `node_type` is a future-session decision if drift surfaces (the CHECK constraint structurally prevents drift at the database layer).

Per [ADR 0102](../../adr/0102-tier-a-cluster-4-node-schema-redesign.md) Adjudication 2, `node_type` is multi-valued (TEXT[] not TEXT) — kant_walkthrough.md §3.2.1.A surfaced the empirical multi-typing reality (`phenomenology` fits 3 enum values cleanly). A node may carry multiple values, e.g., `node_type = ['threshold_concept', 'bridge_concept', 'disciplinary_practice']`.

| Predicate | Domain | Range | Description |
|---|---|---|---|
| `threshold_concept` | `nodes.node_type` element | n/a | A concept whose acquisition transforms how a learner sees the domain. Meyer & Land 2003 framework — confirmed by [`foundations.md`](../../../engine/build_readiness/pdg_papers_extraction/foundations.md) §2 (F1). |
| `bridge_concept` | `nodes.node_type` element | n/a | A concept bridging two domains the learner already knows. **Synthesis-paper coinage; not literature-stabilized** — per [`foundations.md`](../../../engine/build_readiness/pdg_papers_extraction/foundations.md) §3 (F2 Q1-F2 finding). Star & Griesemer 1989 / Akkerman & Bakker 2011 `boundary_concept` is the closest lit-grounded analogue; rename deferred to a future Cluster 4 sequel session per D8 open-for-revision posture. |
| `disciplinary_practice` | `nodes.node_type` element | n/a | A method or skill rather than a concept (e.g., the phenomenological reduction, running a controlled experiment). |
| `text_excerpt` | `nodes.node_type` element | n/a | A passage from a primary text the curriculum anchors against. |
| `historical_context` | `nodes.node_type` element | n/a | A concept-level entity supplying historical context for adjacent concept-acquisition. **Strict ADR 0008 read** per ADR 0102 Adjudication 3 — admits ONLY concept-level entities. Movement-shaped entities (e.g., `phenomenology`-the-20th-century-movement) route via `tradition_label TEXT[]`, NOT via `node_type=['historical_context']`. |
| `misconception` | `nodes.node_type` element | n/a | A node that explicitly encodes a misconception. Distinct from the JSONB `misconceptions` field on concept nodes (Cluster 5 wires the full sub-graph). |
| `comparative_lens` | `nodes.node_type` element | n/a | A framework used to compare two traditions or approaches (e.g., `analytic_vs_continental_philosophy_of_mind`). Distinct from being one of the compared traditions. |
| `assessment_task` | `nodes.node_type` element | n/a | A node representing an assessment task rather than a concept. Distinct from the JSONB `assessment_items` field on concept nodes. |
| `subfield` | `nodes.node_type` element | n/a | Field-label nodes (`philosophy_of_mind`, `ethics`, `metaphysics`, etc.). Added at S-0213 per [`foundations.md`](../../../engine/build_readiness/pdg_papers_extraction/foundations.md) §D3 + kant_walkthrough §3.4.1 path (a) — accommodates the existing 380-node corpus's field-label nodes that the original 8-value synthesis enum had no value for. |
| `unclassified` | `nodes.node_type` element | n/a | **Transitional default** per ADR 0102 Adjudication 1 (schema-only landing). All 380 existing nodes carry `node_type=['unclassified']` post-migration 0140. Per-domain backfill sequel sessions retype to substantive values. Removed from the enum (and the `node_type_unclassified` validator escalated from soft-warn to hard-fail) at the LAST per-domain backfill sequel session via a small follow-up migration. |

## See also

- [ADR 0098](../../adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md) — Tier-A Cluster 2 edge-type taxonomy + three-relation layering; introduces the per-layer controlled vocabulary + compound CHECK constraint that the current registry reflects.
- [ADR 0097](../../adr/0097-tier-a-cluster-1-contestability-substrate.md) — Tier-A Cluster 1 contestability substrate; layer-orthogonal to the per-layer vocabulary; both clusters together establish the Phase 6 edge contract.
- [ADR 0061](../../adr/0061-historical-influence-retyping-for-history-terminator-bridges.md) — `historical_influence` predicate class; the 17 historical-layer edges this ADR introduced retype to `(historical_influence, influenced_by)` per ADR 0098.
- [ADR 0016](../../../engine/adr/0016-graph-construction-needs-live-validation.md) — graph construction needs live validation; the registry's audit consumer.
- [`engine/build_readiness/phase_4_graph_validation.md`](../../../engine/build_readiness/phase_4_graph_validation.md) — Phase 4 build-readiness gate; v1 registry contents authored per T2-G (now superseded by the Cluster 2 vocabulary).
- [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md) — `undeclared_predicate` soft-warn meaning and response posture.
- [`product/docs/architecture.md`](../../docs/architecture.md) — graph schema; the source-of-truth for predicate domain/range expectations.
- [`0003_edges.sql`](0003_edges.sql) — original `public.edges.edge_type` column declaration with no constraint (the "intentionally unconstrained" framing now superseded by ADR 0098's compound CHECK).
- [`0130_edges_three_relation_layering.sql`](0130_edges_three_relation_layering.sql) — Cluster 2 migration introducing `edge_layer` + the compound CHECK that enforces the 16-pair vocabulary above.
