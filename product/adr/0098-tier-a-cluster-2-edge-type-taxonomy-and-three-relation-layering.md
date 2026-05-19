# ADR 0098 — Tier-A Cluster 2: Edge-type taxonomy expansion + three-relation layered separation

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** S-0208 (second Tier-A cluster-implementation ADR per [ADR 0094](0094-phase-6-scope.md) dependency order C1 → **C2** → C4 → C3 → C5; Cluster 1 landed at S-0207 via [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md))

## Context

[ADR 0094](0094-phase-6-scope.md) commits Phase 6 to Tier-A substrate redesign before the SEP/embedding self-correction work; dependency order pins Cluster 2 (edge-type taxonomy + three-relation layered separation) as the natural next after Cluster 1's contestability substrate. [`engine/build_readiness/pdg_papers_extraction/synthesis.md`](../../engine/build_readiness/pdg_papers_extraction/synthesis.md) §Cluster 2 (lines 80-110) names the substrate change: a structural separation of `pedagogical_dependence` / `conceptual_relatedness` / `historical_influence` layers, each with its own controlled-vocabulary `edge_type` (paper_2:L80-81 — *"edge type as enum, not free text"*). The substrate lens-sweep identified seven distinct edge semantics in Paper 1 alone plus three more in Paper 2 (`supports`, `example_of`, `assessed_before`); the existing free-text `edge_type` cannot distinguish "A is a hard prerequisite for B" from "A is a helpful bridge to B" from "A historically influenced B" without semantically meaningful sub-typing.

The current `public.edges` table at [`product/seed-graph/migrations/0003_edges.sql`](../seed-graph/migrations/0003_edges.sql) carries `edge_type TEXT` with two production values across 533 rows: 516 `pedagogical_prerequisite` (the prior schema default; created during Phase 5 seed authoring) and 17 `historical_influence` (added at S-0123 production-audit follow-up per [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md)). [`docs/architecture.md`](../../docs/architecture.md):182 declares `edge_type` *"intentionally unconstrained"* — Cluster 2's commitment is exactly to constrain it, replacing free-text with a per-layer controlled vocabulary. This ADR amends architecture.md:182 in-body via the Consequences section.

Cluster 2 lands the second Tier-A cluster-implementation ADR per [ADR 0094](0094-phase-6-scope.md). Its landing tests two ADR-level T1-A premises (both verified at Cluster 1 landing per [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md)):

- **ADR 0094 T1-A** (premise 2 — "Tier-A implementability without re-decomposition") — re-verified at this ADR's clean landing.
- **ADR 0095 T1-A** (premise 1 — "Tier-A schema implementability in Postgres+JSONB") — re-verified at this ADR's clean landing (compound CHECK constraint is plain Postgres; no AGE escalation required).

In-session plan-mode AskUserQuestion adjudications settled three design choices: (1) enum mechanism = compound CHECK constraint on `(edge_layer, edge_type)` (not Postgres ENUM types and not a lookup table); (2) `edge_cross_layer_default_routing` soft-warn = forward pointer only (Phase 7 routing layer is the natural consumer; implementing now produces dead code); (3) L1.10 node-type partial coverage = defer entirely to Cluster 4 (do not partial-touch the nodes table this session).

[ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) applies — this is a **contract-shape change** under the ADR 0084 trigger classes (the per-layer `edge_type` vocabulary commits a schema contract that all downstream Phase 6+ ADRs + Phase 7+ teaching-layer routing code + the eventual Cluster 7 SQA predictive-validity pipeline will build against). The Load-bearing premises subsection below dogfoods the extraction step.

[ADR 0053](../../engine/adr/0053-mechanism-first-exercise-gate.md) does NOT apply — this ADR authors schema, not a cross-cutting mechanism. Same pattern as ADR 0097 / ADR 0094 / ADR 0095: trigger criteria #1-#4 do not fire; the readiness-note T1/T2 criteria below are premise-disposition closures specific to this ADR.

### Load-bearing premises

*(Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers under the "contract-shape change" class — the per-layer `edge_type` vocabulary commits a schema contract that all five Tier-A cluster ADRs + Phase 7+ teaching-layer routing + the deferred Cluster 7 SQA pipeline will build against.)*

1. **Three-layer separation is exhaustive over edge semantics in this corpus** — `pedagogical_dependence` / `conceptual_relatedness` / `historical_influence` cover the semantic axes the seed graph encodes. *Falsifier:* a future cluster ADR (especially Cluster 5 misconception sub-graph) discovers a 4th orthogonal relation that doesn't fit any of the three (e.g., a meta-pedagogical relation about authoring provenance that's neither a pedagogical claim nor a conceptual affinity nor historical influence). *Test status:* in-context verified — the synthesis ran 5 lens-sweeps (substrate / pedagogy / adversarial / evaluation / Decoding-the-Disciplines) and none surfaced an unaccounted edge relation. **Premise verified.** Future clusters that consume only one or two of the three layers do not falsify the premise (they consume a subset of the layered substrate; the substrate's exhaustiveness is about authoring-time coverage, not query-time consumption).

2. **`soft_prerequisite` is the epistemically conservative default for the 516 retyped pedagogical edges** — per paper_1:L162 ("experts systematically overstate necessity") and synthesis line 101, defaulting to soft inverts the overstatement-prone prior. *Falsifier:* a downstream SQA pass shows the soft default produces under-routing — learners systematically need access to "soft" prereqs that turn out to be hard. *Test status:* in-context partial. The soft-default rationale is paper-level and corpus-level (the 516 edges were authored during Phase 5 LLM-assisted seeding, which inherits the LLM's expert-overstatement bias). **Named in Consequences as Tier-1 readiness criterion (ADR 0098 T1-A)**: closes at Cluster 7 SQA predictive-validity pipeline first-exercise.

3. **`influenced_by` is the epistemically neutral default for the 17 retyped historical edges** — synthesis line 98 names three historical sub-types (`influenced_by` / `received_via` / `reacted_against`); `influenced_by` is the most general and matches the framing of all 17 existing edges per [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md)'s deliberation. *Falsifier:* an historical-influence audit finds some of the 17 are better-typed as `received_via` (transmission-via-intermediary, e.g., "Aristotle reached medieval Europe via Avicenna") or `reacted_against` (deliberate opposition, e.g., "Quine reacted against Carnap's analytic-synthetic distinction"). *Test status:* in-context partial. **Named in Consequences as Tier-2 readiness criterion (ADR 0098 T2-A)**: closes when a future audit examines the 17 edges; until then `influenced_by` holds as a documented default rather than a verified claim.

4. **Compound CHECK on `(edge_layer, edge_type)` is forward-compatible with Cluster 5/7 vocabulary extensions** — extending the vocabulary is an `ALTER TABLE ... DROP CONSTRAINT ... ADD CONSTRAINT`, no `ALTER TYPE` migration complexity. *Falsifier:* a future cluster proposes a vocabulary extension that doesn't fit the `(layer, type)` coupling shape — e.g., an edge that legitimately spans two layers, or an edge type whose semantics changes by context such that `(layer, type)` no longer functionally determines the relation. *Test status:* in-context verified across the 16-entry vocabulary; the Cluster 5 (misconception sub-graph) edge types `common_misconception_about` + `unlearning_required_before` already fit (synthesis line 184: they're pedagogical-dependence sub-types). **Premise verified pending Cluster 5 landing.**

5. **`conceptual_relatedness` is declared but empty at landing** — the three sub-types (`affinity_with` / `contrasts_with` / `same_problem_family`) are reserved-but-unused after migration; no existing edge populates this layer. Cluster 5 (misconception sub-graph) is the natural first author of conceptual_relatedness edges per synthesis cross-cutting observation 4. *Falsifier:* Cluster 5 lands without using the conceptual layer for its misconception edges, indicating the layer was over-declared. *Test status:* in-context partial. **Named in Consequences as Tier-2 readiness criterion (ADR 0098 T2-B)**: closes at Cluster 5 landing — verified if Cluster 5 authors ≥1 conceptual_relatedness edge; falsified if Cluster 5's misconception encoding routes entirely through pedagogical_dependence sub-types.

6. **`edge_provisional_hard_prerequisite` soft-warn is implementable now** — fires when `edge_type='hard_prerequisite'` AND `expert_confidence < 0.4` (low band per ADR 0097 enum convention low=0-0.4, medium=0.4-0.7, high=0.7-1.0). Post-migration the warn fires on zero edges (all 516 retyped to soft_prerequisite; the 17 historical edges are not in the pedagogical layer); future edges manually typed as hard_prerequisite without SQA-validated expert confidence will surface. *Falsifier:* the warn's threshold (`< 0.4`) is wrong — it should fire on `< 0.7` or some other band. *Test status:* in-context verified — the low-band threshold matches paper_1:L162's framing that experts overstate necessity, so low-confidence + hard-typed is the structurally suspect combination. **Premise verified.**

## Decision

**Land the three-relation layered separation as the second Tier-A cluster migration**, structured as one new column + two CHECK constraints + two UPDATE retypings on `public.edges`. The migration file at [`product/seed-graph/migrations/0130_edges_three_relation_layering.sql`](../seed-graph/migrations/0130_edges_three_relation_layering.sql) (per ROUTING.md S-0207 forward-flag, Cluster 2 claims the 0130-0139 sub-range) executes the changes atomically in a BEGIN/COMMIT transaction with full contract header + Postcondition-Assertions block per [ADR 0055](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5 grammar. Paired rollback at [`product/seed-graph/migrations/0130_edges_three_relation_layering_rollback.sql`](../seed-graph/migrations/0130_edges_three_relation_layering_rollback.sql) per [`engine/operations/migration-discipline.md`](../../engine/operations/migration-discipline.md) "Rollback authorship".

### Schema commitments

**New column — ADD COLUMN:**

- `edge_layer TEXT NOT NULL CHECK (edge_layer IN ('pedagogical_dependence', 'conceptual_relatedness', 'historical_influence'))`. The relation-layer enum. Backfilled at migration time: 516 rows whose prior `edge_type = 'pedagogical_prerequisite'` get `edge_layer = 'pedagogical_dependence'`; 17 rows whose prior `edge_type = 'historical_influence'` get `edge_layer = 'historical_influence'`. No row gets `edge_layer = 'conceptual_relatedness'` at landing (Cluster 5 is the natural first author).

**Existing column — ALTER via UPDATE + ADD CONSTRAINT:**

- `edge_type TEXT` (existing, previously unconstrained per architecture.md:182). Existing values retyped: `pedagogical_prerequisite` → `soft_prerequisite` (516 rows); `historical_influence` → `influenced_by` (17 rows). New compound CHECK constraint `edges_edge_layer_type_coupling` couples `(edge_layer, edge_type)` to the 16-pair vocabulary below.

### Per-layer `edge_type` vocabulary

The compound CHECK `(edge_layer, edge_type)` valid pairs (16 total):

**Within `pedagogical_dependence` (10 sub-types):**
- `hard_prerequisite` — A must be mastered before B is teachable (SQA-validated; not the default per premise 2).
- `soft_prerequisite` — A is helpful before B but not strictly required (the post-migration default for all 516 retyped edges).
- `helpful_bridge` — A is not a prerequisite for B but smooths the conceptual transition (synthesis paper_1:L116).
- `co_requisite` — A and B should be learned together; neither precedes the other (synthesis paper_2:L19).
- `contrastive_link` — A is taught against B (e.g., Husserl's phenomenology vs Cartesian dualism); contrast surfaces the concept.
- `misconception_remediation` — A is the corrective concept B needs to displace (Cluster 5 alignment).
- `example_of` — A is a concrete example illustrating concept B (synthesis paper_2:L15).
- `supports` — A provides evidence/argument for B without being a logical prerequisite (synthesis paper_2:L15).
- `assessed_before` — A is assessed/tested before B in the curriculum sequence (synthesis paper_2:L15).
- `unlearning_required_before` — Student must unlearn A's commonsense meaning before learning B (Cluster 5 alignment per synthesis line 184).

**Within `conceptual_relatedness` (3 sub-types, all reserved-but-unused at landing):**
- `affinity_with` — A and B share theoretical commitments without one depending on the other (synthesis paper_2:L19 "conceptual_relatedness" framing).
- `contrasts_with` — A and B occupy opposing positions in a theoretical landscape (e.g., Saussure vs Derrida, per synthesis paper_2:L64).
- `same_problem_family` — A and B address variants of the same problem from different angles.

**Within `historical_influence` (3 sub-types):**
- `influenced_by` — A historically influenced B without claiming pedagogical necessity (the post-migration default for all 17 retyped edges; per ADR 0061 framing).
- `received_via` — A reached the modern reception via intermediary B (e.g., "Aristotle received_via Avicenna in medieval Europe").
- `reacted_against` — A was articulated in deliberate opposition to B (e.g., "Quine reacted_against Carnap on analytic-synthetic").

### Retyping commitments (the 533 existing rows)

| Pre-migration `edge_type` | Count | Post-migration `edge_layer` | Post-migration `edge_type` |
|---|---|---|---|
| `pedagogical_prerequisite` | 516 | `pedagogical_dependence` | `soft_prerequisite` |
| `historical_influence` | 17 | `historical_influence` | `influenced_by` |

The 516 retyped soft_prerequisites stay at [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md)'s `review_status = 'provisional'` default — coordinated handoff: ADR 0097 set the default; Cluster 2's retyping preserves it; Cluster 7 SQA predictive-validity pipeline will upgrade specific edges to `hard_prerequisite` + `review_status = 'approved'` when learner trace evidence supports the upgrade (E.11.1 in [`adversarial_review.md`](../../engine/build_readiness/pdg_papers_extraction/adversarial_review.md)).

### Validator soft-warns

**Implemented this session** (per `feedback_no_pilot_wait_and_see.md` discipline — adoption ships with its own mechanical check):

- `edge_provisional_hard_prerequisite` — fires when `edge_type = 'hard_prerequisite'` AND `expert_confidence < 0.4` (low band per ADR 0097 enum convention). Threshold rationale per premise 6 above. Post-migration the warn fires on zero edges (the entire 516-row pedagogical layer is retyped to `soft_prerequisite`); future manual hard-typing without SQA-validated expert confidence will surface here. Implementation lands in [`engine/tools/validate.py`](../../engine/tools/validate.py) alongside the [Issue #152](https://github.com/StarshipSuperjam/paideia/issues/152) `edge_contestability_unguarded_high_confidence` soft-warn (both consume the contestability schema [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md) committed).

**Forward pointer only** (Phase 7+ routing layer is the natural consumer; implementing now produces dead code):

- `edge_cross_layer_default_routing` — fires when a teaching-layer query asking for "prerequisites of X" traverses edges across layer boundaries without explicit filter. The warn is structurally meaningful only when there IS a teaching layer to surface against; deferred to the Phase 7 routing-layer ADR. Per the in-session plan-mode adjudication.

## Alternatives Considered

### Compound CHECK constraint coupling `(edge_layer, edge_type)` *(chosen)*

- **What:** Single named CHECK constraint on `public.edges` whose body is a disjunction of three per-layer clauses, each pairing the layer literal with an `edge_type IN (...)` listing of the layer's valid sub-types.
- **Pros:** Schema-visible (`\d edges` shows the constraint body); extension is `ALTER TABLE ... DROP CONSTRAINT ... ADD CONSTRAINT` (no `ALTER TYPE` migration complexity); matches ADR 0097's pattern (CHECK on `review_status`); per-layer vocabulary structure visible in constraint body matches synthesis.md text structure. Per premise 4, forward-compatible with Cluster 5/7 vocabulary extensions.
- **Cons:** ~20-line constraint body; verbose to read. Mitigated by per-layer sub-clause grouping that mirrors synthesis.md.
- **Rejected because:** not rejected — chosen per in-session plan-mode adjudication.

### Postgres ENUM types per layer

- **What:** Three `CREATE TYPE` statements (`pedagogical_edge_type` / `conceptual_edge_type` / `historical_edge_type`) + a compound CHECK couples `edge_layer` to the right enum-typed column. Or a single 16-value ENUM with no layer coupling (compound CHECK still required to pair layer to enum subset).
- **Pros:** Type-checked at insert time (Postgres rejects invalid edge_type values without needing CHECK evaluation); canonical Postgres idiom for closed enumerations; named type is reusable across multiple tables.
- **Cons:** `ALTER TYPE ... ADD VALUE` is the extension idiom but it doesn't compose with the compound CHECK constraint that couples layer to enum; type definitions live in a separate schema namespace from the table making schema reading less local; rolling back an ALTER TYPE that's been used in production data requires either `DROP TYPE CASCADE` (destroys data) or copying values out + dropping + recreating (high friction). The 16-value flat enum loses per-layer semantics at the type system level — the compound CHECK has to enforce layer↔enum coupling anyway, so the per-layer information lives in the CHECK, not the type.
- **Rejected because:** extension friction outweighs the type-system gain. Cluster 5 + Cluster 7 are expected to extend the vocabulary; the compound CHECK option pays one ALTER TABLE per extension while the ENUM option pays an ALTER TYPE + a compound-CHECK rewrite per extension. The "type-checked at insert" benefit is largely redundant with the CHECK (both run at insert time; CHECK runs slightly later in the row-validation pipeline but functionally equivalent for the data-integrity claim).

### Controlled-vocabulary lookup table

- **What:** New `public.edge_type_vocabulary` table with rows `(edge_layer TEXT, edge_type TEXT, description TEXT)` + foreign-key constraint from `public.edges` to `public.edge_type_vocabulary` on `(edge_layer, edge_type)`.
- **Pros:** Extending the vocabulary is an INSERT into the vocabulary table (no migration); per-value descriptions live with the data and can be queried for tooltips / documentation; the description column is a natural place to record vocabulary-deliberation provenance (which ADR introduced each value).
- **Cons:** Adds a new public table that needs its own RLS policy, indexes, schema_migrations entry; every edge SELECT that wants type-checked semantics has to JOIN to the vocabulary table (vs reading the CHECK constraint's value-list); over-engineered for 16 fixed values that change rarely (Cluster 5 + Cluster 7 expected; further extensions unlikely). The compound-CHECK option satisfies the schema-contract concern at one-fifth the surface area.
- **Rejected because:** scope creep. The vocabulary is small, expected to evolve slowly, and doesn't need its own RLS surface. The "per-value description" pro is achievable via prose in ADR 0098 (this document) without adding a runtime table.

### Drop + replace existing `edge_type` (no retype-in-place)

- **What:** Drop the existing `edge_type TEXT` column; add a fresh `edge_type TEXT` column with the compound CHECK constraint and NULL defaults; force every existing edge to be re-authored manually with explicit `(edge_layer, edge_type)` pairs.
- **Pros:** Forces explicit per-edge type review at migration time; surfaces edges that don't cleanly fit any new sub-type (lossy retyping would otherwise paper over).
- **Cons:** Destroys the 533-row data signal; manual re-authoring of 533 edges across 380 nodes is a multi-session effort; defeats Cluster 2's lightweight-substrate-redesign framing (the cluster is meant to land in one session per ADR 0094 dependency order).
- **Rejected because:** the in-place retype option (chosen) lossy-maps 516 → soft_prerequisite + 17 → influenced_by which honors the synthesis-prescribed defaults; future SQA-driven upgrades retype specific edges to their semantically-correct sub-type. The "force explicit review" pro is achievable via Cluster 7's SQA pipeline without blocking Cluster 2.

### Defer to Cluster 4 (entangle edge-type vocab with node-type taxonomy)

- **What:** Don't land Cluster 2 separately; bundle the edge-type vocabulary with Cluster 4 (node schema redesign) since several edge types (`example_of`, `supports`, `assessed_before`) need target-node-type anchors that Cluster 4 introduces.
- **Pros:** Edge-type and node-type vocabularies co-evolve; one ADR + one migration instead of two; some edge types (e.g., `example_of` requires the target to be an example-type node) make more semantic sense when node-types exist.
- **Rejected because:** [ADR 0094](0094-phase-6-scope.md) Decision §1 explicitly commits dependency order C1 → **C2** → C4; reversing or merging violates the rationale. Synthesis line 109 explicitly notes the Cluster 2 migration *"is cleaner if Cluster 1's per-edge confidence + provenance columns exist first"* — confirming C2 lands between C1 and C4. The edge-type↔node-type coupling concern is real but addressable: Cluster 4's ADR will add node-type values that Cluster 2's edge types implicitly anchor to; until then, edges with `example_of` / `supports` semantics carry the type assertion without enforcement (same forward-compatibility posture as `conceptual_relatedness` reserved-but-unused at landing).

## Consequences

- **Phase 6 substrate ADR pipeline advances.** Cluster 4 (node schema redesign per synthesis §Cluster 4 lines 141-176) is the natural next at the dependency order C2 → **C4**; Cluster 4's ADR + migration will add the 8+ node-type columns (`node_type`, `disciplinary_domain`, `granularity`, etc.) that several Cluster 2 edge types (`example_of`, `supports`, `assessed_before`) implicitly anchor to. Cluster 3 (goal-relative parameterization) follows; Cluster 5 (misconception sub-graph) extends Cluster 2 + Cluster 4 per synthesis line 180.

- **ADR 0094 T1-A closure: RE-VERIFIED** at this ADR's landing. Cluster 2 lands without scope re-shape — the schema fits in one migration; the 16-entry per-layer vocabulary + the (edge_layer, edge_type) coupling CHECK fit Postgres natively; no cross-cluster dependency forced re-decomposition. ADR 0094 Consequences carries the re-verification marker from this session.

- **ADR 0095 T1-A closure: RE-VERIFIED** at this ADR's landing. The Tier-A schema continues to be implementable in Postgres+JSONB without escalation — Cluster 2 uses plain typed columns + CHECK constraints; no JSONB needed for this cluster; no Apache AGE escalation. ADR 0095 Consequences carries the re-verification marker.

- **The 533 existing edges retain semantic continuity post-migration.** Every existing edge: `edge_layer` is populated deterministically from the prior `edge_type` (pedagogical_prerequisite → pedagogical_dependence; historical_influence → historical_influence); `edge_type` retyped to the synthesis-prescribed default (soft_prerequisite for the 516; influenced_by for the 17); `expert_confidence` / `provenance` / `counterexamples` / `version` / `review_status` / `last_reviewed` / `disagreement_flag` unchanged from [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md)'s shape (Cluster 1's substrate is layer-orthogonal). UNIQUE(source_id, target_id, edge_type) preserved — the retyping changes the third column's value but no two edges share a (source, target, retyped_edge_type) triple (verified post-apply via Postcondition-Assertions). RLS policy `edges_authenticated_read` preserved. Row count invariant: 533.

- **First-exercise readiness criteria** (per [ADR 0094](0094-phase-6-scope.md)'s convention for premise-disposition closures; same pattern as ADR 0097):
  - **T1-A** (premise 2 — `soft_prerequisite` epistemic-conservatism). Closes at Cluster 7 SQA predictive-validity pipeline first-exercise: if learner trace evidence supports upgrading specific edges to `hard_prerequisite`, the soft default is verified (it correctly prevented over-routing); if learners systematically need access to edges the soft default down-routes, the premise is partially falsified and Cluster 7 amends.
  - **T2-A** (premise 3 — `influenced_by` neutral default for the 17 historical edges). Closes at first historical-influence audit (likely Phase 6.5+ or a dedicated SQA-historical-validity pass). The audit either verifies all 17 are correctly typed as `influenced_by` or identifies specific edges that should retype to `received_via` / `reacted_against` via ADR 0098 amendment.
  - **T2-B** (premise 5 — `conceptual_relatedness` reserved-but-unused at landing). Closes at Cluster 5 (misconception sub-graph) landing: verified if Cluster 5 authors ≥1 conceptual_relatedness edge; falsified if Cluster 5 routes entirely through pedagogical_dependence sub-types.

- **No mechanism-first-exercise readiness note authored** per [ADR 0053](../../engine/adr/0053-mechanism-first-exercise-gate.md). Same rationale as ADR 0094 / ADR 0095 / ADR 0097 — this is schema authoring, not a cross-cutting mechanism.

- **Two validator soft-warns land this session** (engine-side companion deliverable, per `feedback_no_pilot_wait_and_see.md`):

  - `edge_provisional_hard_prerequisite` — implementation in [`engine/tools/validate.py`](../../engine/tools/validate.py); fires on `edge_type = 'hard_prerequisite'` AND `expert_confidence < 0.4`. Post-migration expected fires: 0 (all 516 retyped to soft_prerequisite). Future fires surface manual hard-typing without SQA-validated expert confidence; disposition: SQA review per Cluster 7 pipeline.

  - `edge_contestability_unguarded_high_confidence` ([Issue #152](https://github.com/StarshipSuperjam/paideia/issues/152) closure) — implementation in the same `validate.py` edit; fires on `expert_confidence ≥ 0.7` (high band per ADR 0097 enum convention) AND `counterexamples = '[]'::jsonb` AND `provenance->>'rationale' IS NULL`. Post-Cluster-2 expected fires: ~17 (the historical_influence edges retain `expert_confidence = 1.0` from prior production-audit follow-ups; the 516 retyped soft_prerequisites carry `expert_confidence` distribution from Cluster 1 — most are in high band but Cluster 7 will downgrade to low/medium as part of SQA validation). Closes [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md) Cluster-1-deliverable; Cluster 2 is the natural session to land it per the trigger-gate in Issue #152.

  - **Forward-pointer only** (per in-session adjudication): `edge_cross_layer_default_routing` — Phase 7 routing-layer ADR commits the implementation when the routing layer ships.

- **`docs/architecture.md`:182 amended in-body.** The line currently reading *"`edge_type` is intentionally unconstrained"* gains a forward pointer to ADR 0098: *"As of S-0208 per ADR 0098, `edge_type` is constrained to the per-layer controlled vocabulary in the compound CHECK on `(edge_layer, edge_type)`."* The amendment is small (one sentence) and preserves the prior framing for historical context.

- **`docs/PREDICATE_MANIFEST.md` updated this session.** The 16 new (edge_layer, edge_type) pairs register as declared predicates (consumed by validate.py's `undeclared_predicate` soft-warn at [validate.py:2294](../../engine/tools/validate.py:2294)). The two prior entries (`pedagogical_prerequisite`, `historical_influence`) flip to the "Reserved-but-unused / Superseded" section with cross-reference to ADR 0098.

- **[ADR 0061 product](0061-historical-influence-retyping-for-history-terminator-bridges.md) cross-referenced in-body.** ADR 0061's Consequences section gains a forward pointer: "Per [ADR 0098](0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md) S-0208, the 17 `historical_influence` edges this ADR introduced now carry `edge_layer = 'historical_influence'` + `edge_type = 'influenced_by'`. The retyping is lossless — ADR 0061's commitment (historical_influence as a distinct predicate class from pedagogical_prerequisite) is preserved within Cluster 2's three-layer structure." ADR 0061's `Status: Accepted` unchanged — this is an additive context update, not a supersession.

- **Routing manifest updates this session.** [`product/seed-graph/migrations/ROUTING.md`](../seed-graph/migrations/ROUTING.md)'s "Per-session narrative" section adds an S-0208 entry documenting migration 0130 as the first use of the C2=0130-0139 sub-range (per the S-0207 forward-flag in ROUTING.md S-0207 narrative entry). The per-Tier-A-cluster sub-range claim (C2 used; C4 expected at 0140; C3 at 0150; C5 at 0160) further reinforces the prefix-scheme convention; the ROUTING.md prefix-scheme table is updated to reflect the Cluster 2 slot claim.

- **STATE.md updates this session.** "Current phase" row amends to note ADR 0098 landed (ADR count 97 → 98; 91 Accepted + 7 Superseded; 51 engine + 47 product); "Next session work item" row points at Cluster 4 (node schema redesign per synthesis §Cluster 4) as the natural next at the dependency order C2 → C4; Phase 5 closeout numbers (380 nodes, 533 edges) unchanged (this ADR is pure schema; no rows added/removed).

- **No back-pointer cascade to prior ADRs** per [ADR 0041](../../engine/adr/0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md). This ADR is not a supersession; ADR 0094 + ADR 0095 + ADR 0097 + ADR 0061 remain `Status: Accepted` and their commitments hold. This ADR adds-to the substrate rather than supersedes; the cascade discipline's supersession back-reference surface does not fire. The in-body amendments to ADR 0094 + ADR 0095 (re-verifying T1-A) and to ADR 0061 (forward-pointer to the retyping) are status updates within the existing ADRs, not supersessions.

- **Two-layer decision recording** satisfied by this ADR + the matching engine_memory `decisions`-room drawer authored in S-0208. The drawer captures the conversational deliberation including the three plan-mode AskUserQuestion adjudications (enum mechanism, edge_cross_layer_default_routing disposition, L1.10 disposition).

## See also

- [ADR 0094](0094-phase-6-scope.md) — Phase 6 scope: dependency order C1→C2→C4→C3→C5; T1-A re-verified here.
- [ADR 0095](0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) — Postgres+JSONB confirmed; T1-A re-verified here (compound CHECK is plain Postgres).
- [ADR 0093](0093-phase-6-product-trajectory-formalization.md) — Phase 6 product-trajectory formalization; 4 commitments binding for this cluster (no LMS bundling; individual-only scope; BYOK execution surface; retention-mechanic exclusion).
- [ADR 0096](0096-phase-6-learning-outcome-taxonomy.md) — Learning-outcome taxonomy; does not directly constrain Cluster 2 (Cluster 3 consumes it via `learning_outcomes` table); cross-referenced here as the substrate Cluster 3 will rest on.
- [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md) — Cluster 1 contestability substrate; `review_status='provisional'` default coordinates with Cluster 2's retyped soft_prerequisites; this cluster's two new validator soft-warns consume Cluster 1's contestability schema.
- [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md) — `historical_influence` predicate split; the 17 edges this ADR introduced retype to `edge_layer='historical_influence'` + `edge_type='influenced_by'`.
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — pushback-rule extraction step; this ADR triggers under the "contract-shape change" class; Load-bearing premises subsection authored above.
- [ADR 0055](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — apply_migration wrapper + Postcondition-Assertions Layer 2.5; migration 0130 honors the contract.
- [ADR 0039](../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — universal expression contract for AI authoring; the migration body honors per-migration contract block per [`engine/operations/migration-discipline.md`](../../engine/operations/migration-discipline.md).
- [ADR 0077](../../engine/adr/0077-adr-template-alternatives-considered-section.md) — Alternatives Considered template; this ADR uses the per-alternative Pros / Cons / Rejected-because structure for five considered alternatives.
- [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; T1-A / T2-A / T2-B readiness criteria above are premise-disposition closures distinct from cross-cutting-mechanism first-exercise gates.
- [`engine/build_readiness/pdg_papers_extraction/synthesis.md`](../../engine/build_readiness/pdg_papers_extraction/synthesis.md) §Cluster 2 (lines 80-110) — three-relation layering + per-layer vocabulary; the corpus's strongest statement of the substrate's commitments.
- [`engine/build_readiness/pdg_papers_extraction/adversarial_review.md`](../../engine/build_readiness/pdg_papers_extraction/adversarial_review.md) E.11.1 — Cluster 1 ↔ Cluster 2 coordination tension; ADR 0097's `review_status='provisional'` default coordinates with Cluster 2's soft_prerequisite retyping per this section.
- [`product/seed-graph/migrations/0003_edges.sql`](../seed-graph/migrations/0003_edges.sql) — current edges table; the migration targets this schema for ADD COLUMN + ALTER + ADD CONSTRAINT.
- [`product/seed-graph/migrations/0120_edges_contestability_substrate.sql`](../seed-graph/migrations/0120_edges_contestability_substrate.sql) — Cluster 1 migration; Cluster 2's migration 0130 is layer-orthogonal to Cluster 1's contestability columns.
- [`product/seed-graph/migrations/0130_edges_three_relation_layering.sql`](../seed-graph/migrations/0130_edges_three_relation_layering.sql) — the paired migration this ADR commits.
- [`product/seed-graph/migrations/0130_edges_three_relation_layering_rollback.sql`](../seed-graph/migrations/0130_edges_three_relation_layering_rollback.sql) — paired rollback per migration-discipline.
- engine_memory `decisions`-room drawer for ADR 0098 (authored in S-0208) — the conversational deliberation that produced this ADR; recall-by-similarity content for future sessions facing analogous "per-edge controlled-vocabulary authoring under existing-free-text-column adjudication" choices.
