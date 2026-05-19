# ADR 0102 — Tier-A Cluster 4: Node schema redesign

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** S-0213 (third Tier-A cluster-implementation ADR per [ADR 0094](0094-phase-6-scope.md) dependency order C1 → C2 → **C4** → C3 → C5; Cluster 1 landed at S-0207 via [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md); Cluster 2 landed at S-0208 via [ADR 0098](0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md))

## Context

[ADR 0094](0094-phase-6-scope.md) commits Phase 6 to Tier-A substrate redesign before the SEP/embedding self-correction work; dependency order pins Cluster 4 (node schema redesign) as the natural next after Cluster 2's edge-type taxonomy. [`engine/build_readiness/pdg_papers_extraction/synthesis.md`](../../engine/build_readiness/pdg_papers_extraction/synthesis.md) §Cluster 4 (lines 141-176) names the substrate change: one node-schema redesign pass that adds 14+ structurally-rich columns to `public.nodes` (currently 17 columns per [`0002_nodes.sql`](../seed-graph/migrations/0002_nodes.sql)). The cluster integrates seven sub-concerns from the papers (L1.6, L1.9-1.13, L1.16, L2.1, L4.13-partial); splitting would force seven sequential migrations on the same table.

Per [ADR 0094](0094-phase-6-scope.md) premise 6 + [`adversarial_review.md`](../../engine/build_readiness/pdg_papers_extraction/adversarial_review.md) E.12.2, five Tier-A fields (`node_type` / `disciplinary_domain` / `granularity` / `canonical_sources` / `misconceptions`) most affect embedding semantic quality at SEP backfill time. Landing Cluster 4 before the SEP/embedding self-correction work (per ADRs 0085-0088) avoids a re-backfill of all 380 nodes after the schema-enriched fields land.

Session β ([`kant_walkthrough.md`](../../engine/build_readiness/pdg_papers_extraction/kant_walkthrough.md), S-0200) produced a node-by-node Cluster 4 walkthrough against three worked examples (`phenomenology`, `consciousness`, `philosophy_of_mind`) and surfaced 8 §6.7 D1-D8 schema-item adjudications. Session γ ([`foundations.md`](../../engine/build_readiness/pdg_papers_extraction/foundations.md), S-0201) produced F1-F4 foundational-reading findings: F1 confirmed Meyer & Land's threshold-concept framework distinguishes method from movement; F2 found `bridge_concept` is a synthesis-author coinage with no stable cross-tradition meaning (Star & Griesemer 1989 + Akkerman & Bakker 2011 `boundary_concept` named as the closest lit-grounded candidate); F3 confirmed bottleneck-vs-threshold is a real distinction; F4 confirmed the phenomenology-vs-introspection misconception framing (Cluster 5 input, not Cluster 4).

In-session plan-mode AskUserQuestion adjudications settled four load-bearing choices:

1. **Backfill strategy: schema-only this session.** `node_type` defaults to `'unclassified'` across all 380 rows; per-domain classification deferred to Cluster 4 sequel sessions. Mirrors [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md)'s `review_status='provisional'` default; matches single-session-per-cluster framing per [ADR 0094](0094-phase-6-scope.md).
2. **`node_type` cardinality: TEXT[] array.** `phenomenology` fits 3 enum values cleanly per Session β §3.2.1; the array form accommodates without disambiguation-flag proliferation. `is_threshold_concept` folds into `node_type` (no separate boolean).
3. **`historical_context` read: strict (preserve [ADR 0008](0008-concept-nodes-not-thinkers.md)).** Movement-shaped entities route via `tradition_label TEXT[]`, not via `historical_context`. No ADR 0008 amendment this session.
4. **`bridge_concept` disposition: keep + provenance note.** Retain in the enum; explicitly named as synthesis-paper coinage; `boundary_concept` flagged as future-revision candidate per D8 (open-for-revision posture).

[ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) applies — this is a **contract-shape change** under the ADR 0084 trigger classes (Cluster 4 commits a node-table schema contract that all downstream Phase 6+ ADRs + Phase 7+ teaching-layer code + the eventual SEP backfill + embedding work will build against). The Load-bearing premises subsection below dogfoods the extraction step.

[ADR 0053](../../engine/adr/0053-mechanism-first-exercise-gate.md) does NOT apply — this ADR authors schema, not a cross-cutting mechanism. Same pattern as ADR 0097 / ADR 0098 / ADR 0094 / ADR 0095: trigger criteria #1-#4 do not fire; the readiness-note T1/T2 criteria below are premise-disposition closures specific to this ADR.

### Load-bearing premises

*(Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers under the "contract-shape change" class — the node-table schema contract propagates to all downstream cluster ADRs + Phase 7+ teaching layer + SEP backfill embedding work.)*

1. **The 14-column addition set is exhaustive over the synthesis §Cluster 4 enumeration without forcing re-decomposition.** *Falsifier:* a future Tier-A cluster (Cluster 3 goal-relative parameterization or Cluster 5 misconception sub-graph) discovers a 15th node column the synthesis omits that's structurally required for downstream cluster work AND that should have landed in Cluster 4's migration to avoid a follow-up schema change. *Test status:* in-context verified against synthesis §Cluster 4 lines 149-165 (14 columns enumerated) + kant_walkthrough.md §3.1 (re-enumerated) + kant_walkthrough.md §3.2.2 / §3.3.2 / §3.4.2 per-field mapping commentary (no additional fields surfaced). **Premise verified.** Future clusters may add columns of their own; that is forward extension, not falsification.

2. **TEXT[] array form for `node_type` correctly models the multi-typing reality kant_walkthrough §3.2.1.A surfaced.** *Falsifier:* downstream consumers (Phase 7+ routing, SEP embedding) need a single primary `node_type` and cannot meaningfully consume an array; the array form forces every consumer to write disambiguation logic (e.g., "if `'threshold_concept'` is in node_type AND `'historical_context'` is in node_type, which one wins for routing?"). *Test status:* in-context partial. The downstream consumers don't exist yet (Phase 7+ teaching-layer code unwritten; SEP embedding work scheduled after this cluster). **Named in Consequences as Tier-1 readiness criterion (ADR 0102 T1-A)**: closes at the first downstream consumer's first exercise. If consumers force a primary-typing judgment, ADR 0102 amends to add a `node_type_primary TEXT` derived field; the underlying TEXT[] remains as the authoritative multi-aspect record.

3. **The 10-value `node_type` enum (9 synthesis values + `subfield` 9th value + `unclassified` transitional default) is exhaustive over the existing 380-node corpus AND admits the multi-typing cases.** *Falsifier:* per-domain backfill in a Cluster 4 sequel session discovers a node whose semantics fit none of the 10 values cleanly (e.g., a meta-pedagogical authorship-provenance node that's neither concept nor practice nor field-label nor example/excerpt). *Test status:* in-context partial against the 3 Session β worked examples + the existing 380-node corpus's label-set scan (no surfaced gaps beyond the `subfield` addition kant_walkthrough §3.4.1 motivated). **Named in Consequences as Tier-1 readiness criterion (ADR 0102 T1-B)**: closes at the LAST per-domain backfill sequel session — verified if no 11th enum value was needed, falsified if specific domains forced an extension. Per D8 (open-for-revision posture) extensions land via ADR 0102 amendment, not supersession.

4. **Schema-only landing this session correctly defers per-domain classification cost to sequel sessions without producing irreversible structure.** *Falsifier:* the `'unclassified'` transitional default semantically corrupts the corpus (downstream consumers read `unclassified` and produce wrong behavior; the `node_type_unclassified` validator soft-warn fails to escalate as backfill drags). *Test status:* in-context verified. The corpus is read by no downstream consumer in the schema-only window (Cluster 5, Cluster 3, Phase 6 SEP backfill, Phase 7+ teaching all sequence after Cluster 4 sequels close per [ADR 0094](0094-phase-6-scope.md) dependency order); the `node_type_unclassified` validator soft-warn surfaces with high cardinality (~380 at landing) every commit so the deferral does not drift silently. **Premise verified.** The validator emits as soft-warn during the transition window; per Consequences below the eventual escalation to hard-fail is a code-edit at the last sequel session.

5. **The strict ADR 0008 read on `historical_context` (movements route via `tradition_label`, not via `node_type=historical_context`) is internally consistent with the existing 380-node corpus's empirical use of `aliases` and `domain`.** *Falsifier:* a per-domain backfill session discovers a node whose semantics REQUIRE the generous read — `historical_context` admitting movement-shaped entities — to avoid losing essential semantic content that no other Cluster 4 column captures. *Test status:* in-context verified against the `phenomenology` worked example. The Session β §3.2.2.A finding that `aliases` is doing double-duty for tradition-context tags reinforces this: the schema already needed `tradition_label`; the strict read makes that need explicit without forcing ADR 0008 amendment. **Named in Consequences as Tier-2 readiness criterion (ADR 0102 T2-A)**: closes at the LAST per-domain backfill sequel session — verified if no node forced the generous read.

6. **The `node_threshold_concept_lacks_assessment_items` soft-warn matches paper_1:L136's pedagogical claim** that threshold-concept nodes must have direct assessment-items to support the teaching-app diagnostic loop. *Falsifier:* the paper's claim is misread — the requirement applies to a different node class (e.g., only `disciplinary_practice` nodes need assessment_items per the paper) and the threshold-concept-anchored soft-warn fires on the wrong population. *Test status:* in-context verified against `paper_1:L136` direct quotation (synthesis line 170 reproduces the binding). **Premise verified.**

7. **The `node_lacks_cultural_specificity` soft-warn (synthesis line 171, "equity metadata gate") is implementable without ambiguity** — `cultural_specificity` is nullable TEXT and the check fires on `IS NULL` (not on empty string or whitespace-only values). *Falsifier:* per-domain backfill discovers genuinely culture-agnostic nodes (e.g., pure formal logic constructs) for which `cultural_specificity` SHOULD be NULL and the soft-warn produces noise rather than signal. *Test status:* in-context partial. **Named in Consequences as Tier-2 readiness criterion (ADR 0102 T2-B)**: closes at first per-domain backfill sequel session; if signal-vs-noise demands a `cultural_specificity_not_applicable BOOLEAN` flag, ADR 0102 amends.

## Decision

**Land the 14-column node schema redesign as the third Tier-A cluster migration**, structured as 14 ADD COLUMN statements + 4 CHECK constraints on `public.nodes` (no existing-column changes; no row-level UPDATEs — schema-only per Adjudication 1). The migration file at [`product/seed-graph/migrations/0140_nodes_schema_redesign.sql`](../seed-graph/migrations/0140_nodes_schema_redesign.sql) (per [ROUTING.md](../seed-graph/migrations/ROUTING.md) S-0207/S-0208 forward-flagged sub-range, Cluster 4 claims 0140-0149) executes the changes atomically in a BEGIN/COMMIT transaction with full contract header + Postcondition-Assertions block per [ADR 0055](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5 grammar. Paired rollback at [`product/seed-graph/migrations/0140_nodes_schema_redesign_rollback.sql`](../seed-graph/migrations/0140_nodes_schema_redesign_rollback.sql) per [`engine/operations/migration-discipline.md`](../../engine/operations/migration-discipline.md) "Rollback authorship".

### Schema commitments

**14 new columns on `public.nodes`** (ordered by synthesis §Cluster 4 enumeration; all are ADD COLUMN — no rename, no ALTER TYPE, no DROP):

1. **`node_type TEXT[] NOT NULL DEFAULT '{unclassified}'`** — multi-valued enum per Adjudication 2. CHECK constraint `nodes_node_type_valid` enforces every array element is one of the 10 values below; CHECK constraint `nodes_node_type_nonempty` enforces `array_length(node_type, 1) >= 1`.

2. **`disciplinary_domain TEXT`** — nullable. Discipline level (`philosophy`, `literary_theory`, `history`, etc.). Coexists with existing `domain TEXT[]` at sub-discipline / topic-area level per Adjudication 7; the two fields have different semantic levels and both persist. No CHECK constraint at landing (open vocabulary; closes when a future ADR commits the discipline taxonomy).

3. **`granularity TEXT`** — nullable CHECK `nodes_granularity_valid` enforcing `IN ('coarse', 'medium', 'fine')`.

4. **`audience_tags TEXT[] NOT NULL DEFAULT '{}'`** — open vocabulary (no element CHECK); intended values per synthesis: `intro`, `intermediate`, `advanced`, `majors`, `non-majors`, `multilingual_cohort`, plus future additions.

5. **`canonical_sources JSONB NOT NULL DEFAULT '[]'::jsonb`** — element shape `{author, year, title, identifier?}` documented here (not CHECK-enforced for migration cost reasons; element-shape soft-warn deferrable to a follow-up if drift surfaces). Per `adversarial_review.md` E.12.2 this is one of the five embedding-quality-affecting fields.

6. **`approved_examples JSONB NOT NULL DEFAULT '[]'::jsonb`** — element shape `{description, source_ref?}`. The "examples the LLM may use" — distinct from any free-form examples in `teaching_notes` because curated and structurally retrievable.

7. **`misconceptions JSONB NOT NULL DEFAULT '[]'::jsonb`** — element shape `{description, remediation_ref?, remediation_note?}`. Lightweight encoding; the full misconception sub-graph (separate `misconception` nodes + `common_misconception_about` / `unlearning_required_before` edges) lands in Cluster 5 per synthesis §Cluster 5 and [ADR 0094](0094-phase-6-scope.md) dependency order C2 + C4 → C5.

8. **`assessment_items JSONB NOT NULL DEFAULT '[]'::jsonb`** — element shape `{type, prompt, expected_response_form, rationale}` per Adjudication 8. JSONB array rather than FK to a `public.assessments` table because: (a) the assessments table doesn't exist and creating it is out-of-scope for Cluster 4; (b) JSONB is forward-compatible — a future cluster (Phase 7+) can extract to an FK relation when assessment authoring becomes load-bearing AND the JSONB array contains enough rows to justify it.

9. **`mastery_evidence JSONB NOT NULL DEFAULT '[]'::jsonb`** — element shape `{evidence_kind, observation_target}`. What counts as evidence of mastery for this node; consumed by the Phase 7+ mastery-computation pipeline (per [ADR 0085](0085-server-side-mastery-computation-confirmed.md)).

10. **`accessibility_notes TEXT`** — nullable. Free-text notes for accessibility considerations a non-Western or multilingual learner might benefit from per kant_walkthrough §3.2.2 (this column's first listed populated case).

11. **`assumed_background TEXT[] NOT NULL DEFAULT '{}'`** — text-array list of prerequisite-shaped background assumptions the node makes that aren't already captured by inbound `hard_prerequisite` / `soft_prerequisite` edges (e.g., `'analytic_philosophy_of_mind_basic'` for the `phenomenology` node per kant_walkthrough §3.2.2). Useful for syllabus pre-flight checks.

12. **`jargon_load TEXT`** — nullable CHECK `nodes_jargon_load_valid` enforcing `IN ('low', 'medium', 'high')`.

13. **`cultural_specificity TEXT`** — nullable. Records the cultural background the node assumes (e.g., `'Western_continental_philosophy'` for `phenomenology`); enables the equity-metadata validator soft-warn below.

14. **`tradition_label TEXT[] NOT NULL DEFAULT '{}'`** — multi-valued open vocabulary per Adjudication 6. NO CHECK on element values (the proposed Cluster 8 enum `{Western_analytic, Continental, Postcolonial}` was found under-specified by kant_walkthrough §3.5.D — cross-traditional (`consciousness`), sub-traditional (`Husserlian` within `Continental`), and discipline-as-tradition cases all need accommodation). Cluster 8 (Phase 7+ deployment governance per [ADR 0094](0094-phase-6-scope.md)) wires the strip-at-LLM-boundary mechanism; Cluster 4 owns the column. The migration adds the field as schema; per-node `tradition_label` population is per-domain-sequel work like `node_type`.

**No existing-column changes.** All 14 are additive. The pre-existing 17 columns (`id`, `label`, `domain`, `summary`, `teaching_notes`, `aliases`, `rigor_score_computed`, `rigor_score_adjustment`, `provenance`, `confidence`, `confidence_level`, `status`, `superseded_by`, `graph_version_added`, `created_at`, `updated_at`) are unchanged in this migration; the post-migration nodes table carries 31 columns total. The 380-row count is invariant.

### `node_type` enum vocabulary (10 values)

The CHECK constraint `nodes_node_type_valid` enforces array elements ∈ this set:

- **`threshold_concept`** — A concept whose acquisition transforms how a learner sees the domain (Meyer & Land 2003 framework per [foundations.md](../../engine/build_readiness/pdg_papers_extraction/foundations.md) §2). Per F1 verified against the threshold-concept literature.
- **`bridge_concept`** — A concept bridging two domains the learner already knows (e.g., `phenomenology` bridging analytic ↔ continental philosophy of mind per Session β §3.2.1). **Synthesis-paper coinage, not literature-stabilized** (per [foundations.md](../../engine/build_readiness/pdg_papers_extraction/foundations.md) §3 Q1-F2 finding — Star & Griesemer 1989's `boundary_concept` from sociology-of-science is the closest lit-grounded analogue; rename deferred to a future Cluster 4 sequel session per D8 open-for-revision posture).
- **`disciplinary_practice`** — A method or skill rather than a concept (e.g., "running a controlled experiment", "the phenomenological reduction").
- **`text_excerpt`** — A passage from a primary text the curriculum anchors against.
- **`historical_context`** — A historical concept supplying context for adjacent concept-acquisition. **Strict ADR 0008 read** per Adjudication 3: admits ONLY concept-level entities. Movement-shaped entities (e.g., `phenomenology`-the-20th-century-movement, `vienna_circle_logical_positivism`-the-school) route via the new `tradition_label TEXT[]` field, NOT via `node_type=['historical_context']`. The strict read preserves [ADR 0008](0008-concept-nodes-not-thinkers.md)'s "nodes are concepts, not thinkers (and not works, schools, or traditions)" rule without amendment this session.
- **`misconception`** — Used for nodes that explicitly encode a misconception. Distinct from the JSONB `misconceptions` field on concept nodes (Cluster 5 wires the full sub-graph per synthesis §Cluster 5).
- **`comparative_lens`** — A framework used to compare two traditions or approaches (distinct from being one of the traditions; e.g., `analytic_vs_continental_philosophy_of_mind` as a comparative framework that operates between `analytic_philosophy_of_mind` and `phenomenology`).
- **`assessment_task`** — A node that represents an assessment task rather than a concept (e.g., the diagnostic that detects whether a student has acquired `intentionality`). Distinct from the JSONB `assessment_items` field on concept nodes.
- **`subfield`** — Added per [foundations.md](../../engine/build_readiness/pdg_papers_extraction/foundations.md) §D3 + kant_walkthrough §3.4.1 path (a). Admits field-label nodes like `philosophy_of_mind`, `ethics`, `metaphysics`, `epistemology` that the existing 380-node corpus uses but that the original 8-value synthesis enum had no value for. The lowest-cost accommodation; preserves [ADR 0008](0008-concept-nodes-not-thinkers.md) on the (defensible) reading that field-labels are concept-like at the discipline-area granularity.
- **`unclassified`** — Transitional default per Adjudication 1. Every existing node carries `node_type=['unclassified']` at migration landing. Per-domain backfill sequel sessions retype to one or more substantive values; the `node_type_unclassified` validator soft-warn surfaces the count every commit during the transition window. Removed from the enum (and the validator escalated to hard-fail) at the LAST per-domain backfill sequel session.

### Backfill commitments

**No row-level UPDATEs this session.** All 380 nodes carry the column defaults post-migration:
- `node_type = '{unclassified}'`
- `disciplinary_domain = NULL`
- `granularity = NULL`
- `audience_tags = '{}'`
- `canonical_sources = '[]'::jsonb`
- `approved_examples = '[]'::jsonb`
- `misconceptions = '[]'::jsonb`
- `assessment_items = '[]'::jsonb`
- `mastery_evidence = '[]'::jsonb`
- `accessibility_notes = NULL`
- `assumed_background = '{}'`
- `jargon_load = NULL`
- `cultural_specificity = NULL`
- `tradition_label = '{}'`

**Cluster 4 sequel sessions** own per-domain classification work. Likely sequence (mapping to existing seed-migration subdomain prefixes per [ROUTING.md](../seed-graph/migrations/ROUTING.md)):

| Sequel session | Subdomain | Approx node count | Migration slot |
|---|---|---|---|
| S-0214 (or later) | epistemology, metaphysics | ~80 | 0141 |
| S-0215 (or later) | ethics, metaethics | ~70 | 0142 |
| S-0216 (or later) | mind, language | ~70 | 0143 |
| S-0217 (or later) | science, logic | ~70 | 0144 |
| S-0218 (or later) | political_philosophy, aesthetics | ~50 | 0145 |
| S-0219 (or later) | service_nodes + cross-domain | ~40 | 0146 |

Numbers are estimates; actual sequencing depends on session availability and may consolidate. **Each sequel session classifies its domain's nodes via per-node review** (not deterministic CASE on label patterns — kant_walkthrough §3 demonstrated the per-node empirical work needed for accurate multi-typing) AND populates the other 13 columns to the extent the source material supports. **The LAST sequel session edits `validate.py` to remove `'unclassified'` from the enum AND escalate the `node_type_unclassified` soft-warn to hard-fail** — the schema CHECK constraint also amends to drop `'unclassified'` from the valid set (separate small migration). Until then the transitional default holds.

### Validator soft-warns

**Implemented this session in [`engine/tools/validate.py`](../../engine/tools/validate.py)** (per `feedback_no_pilot_wait_and_see.md` discipline — adoption ships with its own mechanical adoption-check):

- **`node_type_unclassified`** — fires on any node whose `node_type = ['unclassified']`. Severity is mode-switched at the module-level constant `NODE_TYPE_UNCLASSIFIED_FIRE_MODE` (initial value: `"soft_warn"` this session; the LAST sequel session edits to `"hard_fail"`). Synthesis line 168 binding: "Any node lacking `node_type` after migration: hard-fail until backfilled." This session adopts the schema-only landing per Adjudication 1, which means hard-fail today would block every commit on all 380 nodes; the soft-warn transition window provides the deliberate adoption ramp. Expected fire count at landing: 380 (the entire current corpus).

- **`node_threshold_concept_lacks_assessment_items`** — fires on any node where `'threshold_concept' = ANY(node_type)` AND `assessment_items = '[]'::jsonb`. Per `paper_1:L136` / synthesis line 169. Expected fire count at landing: 0 (no node carries `node_type='{threshold_concept}'` at landing; all are `'unclassified'`). Future fires surface threshold-concept-classified nodes lacking direct diagnostics; disposition: backfill the assessment items, or downgrade the node from `threshold_concept` if no diagnostic exists.

- **`node_lacks_cultural_specificity`** — fires on any node where `cultural_specificity IS NULL`. Equity-metadata gate per synthesis line 171. Expected fire count at landing: 380 (the entire current corpus; the column is added nullable, all existing rows are NULL). Future fires drive backfill effort; per premise 7 above, if a `cultural_specificity_not_applicable BOOLEAN` flag becomes necessary to suppress noise on pure formal-logic nodes, ADR 0102 amends.

All three categories register in `GRAPH_SOFT_WARN_CATEGORIES` so cross-session telemetry sees "category ran clean" distinct from "category did not run."

## Alternatives Considered

### TEXT[] array `node_type` with 10-value CHECK *(chosen)*

- **What:** `node_type TEXT[] NOT NULL DEFAULT '{unclassified}'` with a per-element CHECK constraint enforcing the 10-value vocabulary above. Multi-typed nodes (e.g., `phenomenology = ['threshold_concept', 'bridge_concept', 'disciplinary_practice']`) carry the full semantic content of their multi-aspect reality.
- **Pros:** Accommodates kant_walkthrough §3.2.1.A's empirical multi-typing finding without forcing a primary-typing judgment the data doesn't naturally support. Forward-compatible per D8 open-for-revision posture — extensions land via ADR amendment + `ALTER TABLE ... DROP CONSTRAINT ... ADD CONSTRAINT`. Mirrors ADR 0098's compound CHECK pattern. `is_threshold_concept BOOLEAN` folds in (`'threshold_concept' = ANY(node_type)` is the predicate).
- **Cons:** Downstream consumers needing a single primary type must implement disambiguation logic. Per premise 2 above, this consumer doesn't exist yet; if surfaced post-landing, ADR 0102 amends to add a `node_type_primary TEXT` derived field with explicit precedence rules. Array-form predicates in SQL are slightly more verbose than scalar-form (`'X' = ANY(node_type)` vs `node_type = 'X'`).
- **Rejected because:** not rejected — chosen per Adjudication 2 (in-session AskUserQuestion).

### Single-valued TEXT `node_type` with disambiguation boolean flags

- **What:** `node_type TEXT NOT NULL DEFAULT 'unclassified'` (single primary type) + auxiliary booleans (`is_threshold_concept BOOL DEFAULT FALSE`, `is_method_aspect BOOL DEFAULT FALSE`, `is_subfield BOOL DEFAULT FALSE`, `is_bridge_concept BOOL DEFAULT FALSE`). Each node picks one primary type; the flags carry the multi-aspect signal.
- **Pros:** Single primary type is simpler for downstream consumers; SQL predicates are scalar-form (`node_type = 'X'`). Booleans can be added one-at-a-time as multi-aspect cases surface without ALTER TYPE-style schema friction.
- **Cons:** Adds 4+ columns to manage what one TEXT[] handles. Multi-typed nodes lose information unless ALL relevant flags are set — kant_walkthrough §3.2.1.A shows `phenomenology` needs three flags AND a primary type; the primary-type choice is itself the judgment the data does not naturally support. Each new multi-aspect case adds a column (vs adding an enum value in the array form). The flag set grows as the corpus is classified.
- **Rejected because:** disambiguation flag proliferation. Per Adjudication 2, the multi-typing reality is empirical (kant_walkthrough's three worked examples surfaced one node needing 3 types); flag-form forces the schema author to predict which multi-aspect combinations are needed AND adds flags reactively. Array-form is closed at landing.

### Primary TEXT `node_type` + secondary TEXT[] `node_type_aspects`

- **What:** `node_type TEXT NOT NULL` (one primary) + `node_type_aspects TEXT[] NOT NULL DEFAULT '{}'` (secondary aspects). Splits primary identity from secondary aspect tags. Phenomenology gets `node_type='disciplinary_practice'` + `aspects=['threshold_concept', 'bridge_concept']`.
- **Pros:** Reads middle-ground between scalar and full array. Downstream consumers can default to `node_type` for routing decisions and consult `aspects` only when needed.
- **Cons:** Forces a primary-typing judgment per node — for `phenomenology` the choice between primary `disciplinary_practice` vs primary `threshold_concept` is itself unresolvable from the data. Adds two columns where the array form needs one. Cross-aspect equality (`'X' IN aspects` vs `node_type = 'X'`) requires consumers to write two-path predicates.
- **Rejected because:** the primary-aspect partition is itself a judgment Cluster 4 cannot make on behalf of all 380 nodes. The array form treats all type values as equal-weight; per Adjudication 2, this matches the empirical multi-typing reality.

### Schema-only landing this session, with per-domain backfill in sequel sessions *(chosen, Adjudication 1)*

- **What:** Add the 14 columns with sensible defaults; `node_type` defaults to `'unclassified'` across all 380 rows; per-domain classification work (likely 4-8 sequel sessions, one per subdomain) follows. Validator soft-warns track the transition; the `node_type_unclassified` warn escalates to hard-fail at the LAST sequel session.
- **Pros:** Matches single-session-per-cluster framing per [ADR 0094](0094-phase-6-scope.md). Mirrors ADR 0097's `review_status='provisional'` default — Cluster 1 set a safe default; sequel work upgrades specific cases. Per-domain classification gets proper per-node review (kant_walkthrough §3 demonstrated the empirical work needed for multi-typing accuracy). No CASE-heuristic mis-classifications to audit later. Sequel sessions are independent units; can run interleaved with other Phase 6 work.
- **Cons:** The `'unclassified'` transitional default means downstream consumers reading `node_type` during the transition window observe a sentinel rather than a substantive type. Per premise 4 above, no downstream consumer reads `node_type` in the transition window (Cluster 5 / Cluster 3 / SEP backfill / Phase 7+ teaching all sequence after Cluster 4 sequels close per [ADR 0094](0094-phase-6-scope.md) dependency order); the validator soft-warn ensures the deferral does not drift silently. Transition-window length depends on sequel session cadence — if sequels lag, the soft-warn fires every commit indefinitely.
- **Rejected because:** not rejected — chosen per Adjudication 1.

### Schema + per-node `node_type` backfill via deterministic CASE in same migration

- **What:** Single migration body adds the 14 columns AND backfills `node_type` per node via deterministic CASE on `label` / `domain` patterns (e.g., `WHEN id IN ('philosophy_of_mind', 'ethics', 'metaphysics', 'epistemology', 'logic', 'aesthetics') THEN ARRAY['subfield']`; `WHEN summary LIKE '%misconception%' THEN ARRAY['misconception']`; default ARRAY['unclassified']).
- **Pros:** Saves sequel sessions. Schema lands fully populated; downstream consumers can read `node_type` from day one.
- **Cons:** CASE heuristics produce silent mis-classifications. Per kant_walkthrough §3.2.1.A's multi-typing finding (`phenomenology` needs 3 types; the CASE would pick one), single-pass heuristics cannot accurately classify multi-aspect nodes. Mis-classifications would propagate to downstream consumers as ground truth, requiring future audit work to correct. The sequel-session-per-domain pattern with per-node review trades single-session scope expansion for per-node accuracy.
- **Rejected because:** per-node review is the right unit for multi-typing accuracy; CASE-based backfill would force a future audit-and-correction cycle that the deferral avoids. The "Pros" gain (sequels saved) is dwarfed by the silent-mis-classification cost.

### Strict ADR 0008 read on `historical_context` *(chosen, Adjudication 3)*

- **What:** `historical_context` admits ONLY concept-level entities. Movement-shaped entities like `phenomenology`-the-20th-century-movement route via `tradition_label TEXT[]`. [ADR 0008](0008-concept-nodes-not-thinkers.md)'s "nodes are concepts, not thinkers (and not works, schools, or traditions)" rule is preserved without amendment this session.
- **Pros:** No ADR 0008 amendment; no cascade to other ADR 0008-citing decisions. The `tradition_label` field is added in this same migration so the alternative encoding is immediately available. kant_walkthrough §3.2.2.A's empirical finding that the `aliases` field is doing double-duty for tradition-context tags is resolved by `tradition_label` taking over the tradition-tag role.
- **Cons:** Movement-shaped entities lose the `historical_context` semantic anchor as a node_type. A future consumer that wants to query "all historical-context nodes" must consult `tradition_label` rather than `node_type` for movement-shaped entities. Adds an asymmetry: concept-level historical context goes in `node_type`; movement-level goes in `tradition_label`.
- **Rejected because:** not rejected — chosen per Adjudication 3.

### Generous ADR 0008 read on `historical_context` — amend ADR 0008

- **What:** `historical_context` admits movement-shaped entities. ADR 0008 amends in-body (or via a sibling supersession ADR) to permit movement / tradition entries under the `historical_context` node-type. Phenomenology gets `node_type=['historical_context', 'disciplinary_practice', ...]`.
- **Pros:** More expressive — multi-aspect nodes carry their historical-context-as-movement signal in `node_type` directly. The asymmetry the strict read introduces (movements via `tradition_label`; concepts via `node_type`) is removed.
- **Cons:** Requires ADR 0008 amendment, expanding Cluster 4 scope. Cascade to ADR 0008-citing decisions (which include the Phase 5 seed-authoring discipline). The schema cost of adding `tradition_label` separately is not avoided — `tradition_label` still has a function for `consciousness` (cross-traditional cases) and other nodes where the movement framing is secondary; the generous read does not eliminate the `tradition_label` column, it adds the `historical_context` node-type as a parallel encoding option that may or may not get consistently used.
- **Rejected because:** Cluster 4 scope discipline. Per Adjudication 3, the strict read keeps this session bounded; if a per-domain backfill sequel session finds the strict read genuinely loses essential semantic content (per premise 5 falsifier), ADR 0102 amends OR a successor ADR amends ADR 0008. The deferred-amendment path preserves optionality.

### Keep `bridge_concept` with provenance note *(chosen, Adjudication 4)*

- **What:** Retain `bridge_concept` in the `node_type` enum; ADR 0102 (this Decision section above) explicitly names it as a synthesis-paper coinage (not literature-stabilized), with `boundary_concept` per Star & Griesemer 1989 / Akkerman & Bakker 2011 flagged as a future-revision candidate per D8 (open-for-revision posture). The data already fits the term (Session β §3.2.1 confirmed `phenomenology` exhibits bridge-concept characteristics).
- **Pros:** Smallest possible scope this session. Per D8 the enum is open-for-revision; future Cluster 4 sequel sessions OR a dedicated rename session can convert `bridge_concept` → `boundary_concept` after WebFetch verification of the BO literature. No commitment lost; revision channel preserved.
- **Cons:** The enum carries a coinage. Future readers who don't read this Decision section may assume `bridge_concept` is a literature-stabilized term. Mitigated by the provenance note in this section + ADR-citing comment in the migration body.
- **Rejected because:** not rejected — chosen per Adjudication 4.

### Rename `bridge_concept` to `boundary_concept` after WebFetch on BO literature

- **What:** WebFetch summaries of Star & Griesemer 1989 (boundary objects) + Akkerman & Bakker 2011 (boundary crossing) in this session; if the BO literature supports cross-disciplinary mediation semantics matching the synthesis intent, rename `bridge_concept` → `boundary_concept` in the enum, with the synthesis intent preserved via the ADR's Decision section.
- **Pros:** Lit-grounded enum value; future readers can cite Star & Griesemer for the term. Resolves the coinage concern at landing rather than deferring.
- **Cons:** Adds a WebFetch step to this session's scope. Per [`foundations.md`](../../engine/build_readiness/pdg_papers_extraction/foundations.md) §3.5 the BO literature's STS connotations may not match the synthesis intent (cross-disciplinary mediation in BO ≠ cross-tradition pedagogical bridging in the synthesis); the WebFetch could return ambiguous results requiring further deliberation, which expands scope rather than tightens it.
- **Rejected because:** Cluster 4 scope discipline. Per Adjudication 4, the rename channel is preserved via D8 open-for-revision; a future dedicated session can WebFetch + rename with proper deliberation. Bundling it here risks scope creep on a session that already commits 14 schema additions.

### Drop `bridge_concept` entirely

- **What:** Remove `bridge_concept` from the enum (9 values total). Bridge-function expressed via `audience_tags` (e.g., `bridges_analytic_continental`) or via the existing `comparative_lens` enum value.
- **Pros:** Avoids the grounding question entirely. Smaller enum.
- **Cons:** Per kant_walkthrough §3.2.1 `phenomenology` fits `bridge_concept` cleanly on the bridging-between-traditions function; the data IS bridge-shaped. Dropping forces secondary-tag workarounds (`audience_tags`) for a real semantic category. `comparative_lens` operates BETWEEN compared things; `bridge_concept` IS one of the bridged things — the distinction is fine but real per Session γ §3.5 finding.
- **Rejected because:** the data fits the term; dropping forces less-accurate workarounds. Per Adjudication 4, keep + provenance note + D8 revision path is the right middle ground.

### Defer Cluster 4 entirely to after Cluster 3 + Cluster 5

- **What:** Reverse the [ADR 0094](0094-phase-6-scope.md) dependency order C1 → C2 → C4 → C3 → C5 to C1 → C2 → C3 → C5 → C4. Cluster 3 (goal-relative parameterization) and Cluster 5 (misconception sub-graph) land first; Cluster 4 lands after.
- **Pros:** None specific — would be motivated by a discovery that Cluster 4's schema commitments depend on Cluster 3 or Cluster 5 deliverables in a way the original dependency order missed.
- **Cons:** [ADR 0094](0094-phase-6-scope.md) Decision §1 explicitly commits the C1 → C2 → C4 → C3 → C5 order. Cluster 5 explicitly extends Cluster 4 per synthesis §Cluster 5 ("Dependency: Cluster 2 (edge types) AND Cluster 4 (node-type enum) must land first — this cluster requires both."). Reversing would block Cluster 5 until both Cluster 3 AND Cluster 4 land.
- **Rejected because:** [ADR 0094](0094-phase-6-scope.md) dependency order; Cluster 5's explicit Cluster 4 dependency.

## Consequences

- **Phase 6 substrate ADR pipeline advances.** Cluster 3 (goal-relative parameterization per synthesis §Cluster 3) is the natural next at the dependency order C4 → **C3**; Cluster 3's ADR + migration adds the `learning_outcomes` table + edge-outcome-necessity field per [ADR 0096](0096-phase-6-learning-outcome-taxonomy.md). Cluster 5 (misconception sub-graph) follows after C3 per [ADR 0094](0094-phase-6-scope.md) ordering, consuming this cluster's `misconceptions` JSONB field + the `misconception` `node_type` enum value + Cluster 2's `common_misconception_about` + `unlearning_required_before` edge types. SEP backfill + embedding work per [ADR 0086](0086-model-agnostic-embedding-storage-architecture.md) sequences after Tier-A migrations close (per ADR 0094 Consequences).

- **ADR 0094 T1-A closure: RE-VERIFIED** at this ADR's landing. Cluster 4 lands without scope re-shape — the 14-column schema fits in one migration; the 10-value `node_type` enum fits Postgres natively (TEXT[] with element CHECK); the JSONB columns + array columns + nullable TEXT columns all use plain Postgres types; no cross-cluster dependency forced re-decomposition. ADR 0094 Consequences amended in-body with the re-verification marker from this session — this is the third Tier-A cluster landing without scope re-shape (S-0207 C1, S-0208 C2, S-0213 C4).

- **ADR 0095 T1-A closure: RE-VERIFIED** at this ADR's landing. Postgres + JSONB models the node-schema redesign without shape friction; the JSONB columns store the citation-object / example-object / misconception-object element shapes natively; no Apache AGE escalation required. ADR 0095 Consequences amended in-body with the re-verification marker.

- **ADR 0094 T1-B partial closure.** Premise 3 of ADR 0094 names D-item adjudication closure as Tier-1 readiness. The Session δ₂ + Session β + Session γ D-item adjudications fed forward into this session's Adjudications 1-4 plus the resolve-by-recommendation outcomes (D3 `subfield` enum addition; D4 `tradition_label TEXT[]` open form). D1 (`historical_context` read) + D2 (`node_type` cardinality) + D3 (`subfield` enum gap) + D4 (`tradition_label` cardinality) + D8 (open-for-revision posture) all settle within Tier-A scope at this landing — no Tier-D inclusion forced. D5 (Layer-2 Cluster 2 sub-types `subject_matter_of` / `tradition_as_context`) defers to a Cluster 2 amendment session; D6 + D7 defer to Cluster 5. **Partial closure** — full T1-B closure waits for D6 + D7 settlement at Cluster 5 ADR landing.

- **The 380 existing nodes retain full semantic continuity post-migration.** Every existing node: 14 new columns get column defaults (`node_type='{unclassified}'`; JSONB columns get `'[]'::jsonb`; array columns get `'{}'`; nullable TEXT columns get NULL; `granularity` and `jargon_load` get NULL pending backfill). UNIQUE PRIMARY KEY on `id` preserved; RLS policy `nodes_authenticated_read` preserved; row count invariant: 380. The 17 pre-existing columns are unchanged.

- **First-exercise readiness criteria** (per [ADR 0094](0094-phase-6-scope.md)'s convention for premise-disposition closures; same pattern as ADR 0097 / ADR 0098):
  - **T1-A** (premise 2 — TEXT[] array form correctly models multi-typing for downstream consumers). Closes at first downstream consumer's first exercise (likely Cluster 5 misconception sub-graph at Session δ₅+, OR SEP embedding work per ADR 0086 if that lands first). Verified if consumers handle the array form without forcing a primary-typing judgment; falsified if consumers need a derived `node_type_primary TEXT` (ADR 0102 amends to add it).
  - **T1-B** (premise 3 — 10-value enum exhaustive over corpus). Closes at the LAST per-domain backfill sequel session (the one that escalates `node_type_unclassified` to hard-fail). Verified if no 11th enum value was needed across all backfill sessions; falsified if specific domains forced an extension (D8 open-for-revision posture admits extensions via ADR 0102 amendment).
  - **T2-A** (premise 5 — strict ADR 0008 read on `historical_context` doesn't lose essential semantic content). Closes at the LAST per-domain backfill sequel session. Verified if no node forced the generous read; falsified if specific nodes required ADR 0008 amendment to be properly typed.
  - **T2-B** (premise 7 — `node_lacks_cultural_specificity` soft-warn is implementable without ambiguity). Closes at first per-domain backfill sequel session. Verified if NULL-vs-not-applicable distinction is clean; falsified if a `cultural_specificity_not_applicable BOOLEAN` flag becomes necessary (ADR 0102 amends).

- **No mechanism-first-exercise readiness note authored** per [ADR 0053](../../engine/adr/0053-mechanism-first-exercise-gate.md). Same rationale as ADR 0097 / ADR 0098 / ADR 0094 / ADR 0095 — this is schema authoring, not a cross-cutting mechanism.

- **Three validator checks land this session** (engine-side companion deliverables, per `feedback_no_pilot_wait_and_see.md`):
  - `node_type_unclassified` — implementation in [`engine/tools/validate.py`](../../engine/tools/validate.py); fires on any node with `node_type=['unclassified']`. Severity mode-switched at module-level constant `NODE_TYPE_UNCLASSIFIED_FIRE_MODE` (initial: `"soft_warn"`; LAST sequel session escalates to `"hard_fail"`). Expected fire count at landing: 380 (entire corpus).
  - `node_threshold_concept_lacks_assessment_items` — implementation in same `validate.py` edit; fires on nodes where `'threshold_concept' = ANY(node_type)` AND `assessment_items = '[]'::jsonb`. Expected fire count at landing: 0 (no node carries `threshold_concept` at landing).
  - `node_lacks_cultural_specificity` — implementation in same `validate.py` edit; fires on nodes where `cultural_specificity IS NULL`. Expected fire count at landing: 380 (column added nullable; all existing rows NULL).

- **[`docs/architecture.md`](../docs/architecture.md) "Node Schema" section amended in-body.** The line currently listing the 17 columns gains a forward pointer to ADR 0102 + a summary block naming the 14 new columns added at S-0213. The amendment preserves the existing column justifications and adds per-new-column justifications referencing this ADR for the load-bearing rationale.

- **[`docs/PREDICATE_MANIFEST.md`](../seed-graph/migrations/PREDICATE_MANIFEST.md) — node-side predicates section.** PREDICATE_MANIFEST.md presently tracks edge_type predicates per [ADR 0098](0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md); the 10 `node_type` enum values introduced this session are a parallel registry the validator does not yet consume. The MANIFEST is amended in this session to add a "Node-side predicates: node_type vocabulary" section listing the 10 values; the `undeclared_predicate` check stays scoped to edge_type for now. A future session may extend the check to node_type if drift surfaces.

- **Issue #115 (`historical_node_as_prereq_source` validator soft-warn — pending node-class schema extension) is partially unblocked.** The Issue tracks the Phase 5 production-audit's Proposal 4 (per [`engine/build_readiness/phase_5_audit_system_input.md`](../../engine/build_readiness/phase_5_audit_system_input.md):79-96) which awaits a `node_class` schema extension. The `node_type` field added by this migration serves the same structural role under the post-synthesis renaming. The Issue's enumeration of categories (`history-terminator`, `school-movement`, `thinker-framework`) maps approximately to: `history-terminator` → likely `historical_context` (concept-level) or `subfield`; `school-movement` → `tradition_label` rather than `node_type` per Adjudication 3 (strict ADR 0008 read); `thinker-framework` → existing nodes are concept-level with thinker provenance, typed as `threshold_concept` + `tradition_label` populated. The validator soft-warn promotion remains a follow-up that consumes the per-domain-backfilled `node_type` + `tradition_label` columns; Issue #115 stays open until the first sequel session demonstrates the soft-warn fires correctly.

- **Routing manifest updates this session.** [`product/seed-graph/migrations/ROUTING.md`](../seed-graph/migrations/ROUTING.md)'s prefix-scheme table reflects Cluster 4 sub-range claim (0140-0149) per S-0207/S-0208 forward-flag; per-session narrative entry for S-0213 documents migration 0140 as the first use of the C4 sub-range. Subsequent Cluster 4 sequel sessions claim 0141-0149 (one per subdomain).

- **STATE.md updates this session.** "Current phase" row amends to note ADR 0102 landed (ADR count 101 → 102; 95 Accepted + 7 Superseded; 54 engine + 48 product); "Next session work item" row points at Cluster 3 (goal-relative parameterization per synthesis §Cluster 3) as the natural next at the dependency order C4 → C3 OR at the first Cluster 4 per-domain backfill sequel session (whichever the user prioritizes); Phase 5 closeout numbers (380 nodes, 533 edges) unchanged (this ADR is pure schema; no rows added/removed/retyped).

- **No back-pointer cascade to prior ADRs** per [ADR 0041](../../engine/adr/0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md). This ADR is not a supersession; ADR 0094 + ADR 0095 + ADR 0097 + ADR 0098 + ADR 0008 + ADR 0030 + ADR 0061 remain `Status: Accepted` and their commitments hold. This ADR adds-to the substrate rather than supersedes; the cascade discipline's supersession back-reference surface does not fire. The in-body amendments to ADR 0094 + ADR 0095 (re-verifying T1-A) are status updates within the existing ADRs, not supersessions. ADR 0008 is explicitly read strictly per Adjudication 3 with no amendment.

- **Two-layer decision recording** satisfied by this ADR + the matching engine_memory `decisions`-room drawer authored in S-0213. The drawer captures the conversational deliberation including the four plan-mode AskUserQuestion adjudications (backfill strategy; node_type cardinality; historical_context read; bridge_concept disposition) plus the four resolve-by-recommendation outcomes (D3 subfield enum; D4 tradition_label cardinality; domain/disciplinary_domain reconciliation; assessment_items JSONB vs FK).

## See also

- [ADR 0094](0094-phase-6-scope.md) — Phase 6 scope: dependency order C1→C2→C4→C3→C5; T1-A re-verified here; T1-B partial closure here (D1, D2, D3, D4, D8 settled).
- [ADR 0095](0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) — Postgres+JSONB confirmed; T1-A re-verified here.
- [ADR 0093](0093-phase-6-product-trajectory-formalization.md) — Phase 6 product-trajectory formalization; 4 commitments binding for this cluster.
- [ADR 0096](0096-phase-6-learning-outcome-taxonomy.md) — Learning-outcome taxonomy; cited as foundation for the future Cluster 3 substrate; does not directly constrain Cluster 4.
- [ADR 0097](0097-tier-a-cluster-1-contestability-substrate.md) — Cluster 1 contestability substrate; `review_status='provisional'` default is the precedent for Cluster 4's `'unclassified'` transitional default.
- [ADR 0098](0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md) — Cluster 2 edge-type taxonomy; per-layer CHECK constraint pattern is the precedent for this cluster's `node_type` 10-value CHECK; several Cluster 2 edge types (`example_of`, `supports`, `assessed_before`) implicitly anchor to node-types this cluster introduces.
- [ADR 0008](0008-concept-nodes-not-thinkers.md) — Concept-nodes-not-thinkers; Adjudication 3 (strict read on `historical_context`) preserves this ADR without amendment; the `tradition_label` field added by this migration provides the movement-shaped-entity routing channel.
- [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md) — `confidence_level` enum on nodes; pre-existing 3-value enum (`EXTRACTED`, `INTERPRETED`, `SYNTHETIC`) is orthogonal to this cluster's additions; no interaction.
- [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md) — `historical_influence` predicate split; cited in Adjudication 3 deliberation context (the 17 retyped historical edges anchor to nodes that may carry `tradition_label` post-backfill).
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — pushback-rule extraction step; this ADR triggers under the "contract-shape change" class; Load-bearing premises subsection authored above.
- [ADR 0055](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — apply_migration wrapper + Postcondition-Assertions Layer 2.5; migration 0140 honors the contract.
- [ADR 0039](../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — universal expression contract for AI authoring; the migration body honors per-migration contract block per [`engine/operations/migration-discipline.md`](../../engine/operations/migration-discipline.md).
- [ADR 0077](../../engine/adr/0077-adr-template-alternatives-considered-section.md) — Alternatives Considered template; this ADR uses the per-alternative Pros / Cons / Rejected-because structure for nine considered alternatives.
- [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; T1-A / T1-B / T2-A / T2-B readiness criteria above are premise-disposition closures distinct from cross-cutting-mechanism first-exercise gates.
- [`engine/build_readiness/pdg_papers_extraction/synthesis.md`](../../engine/build_readiness/pdg_papers_extraction/synthesis.md) §Cluster 4 (lines 141-176) — 14-column node redesign + 8-value node_type enum + 3 validator soft-warns; the corpus's strongest statement of this cluster's commitments.
- [`engine/build_readiness/pdg_papers_extraction/kant_walkthrough.md`](../../engine/build_readiness/pdg_papers_extraction/kant_walkthrough.md) §3 — node-by-node Cluster 4 walkthrough against three worked examples (`phenomenology`, `consciousness`, `philosophy_of_mind`); §3.2.1.A multi-typing finding motivated Adjudication 2; §3.4.1 motivated the `subfield` 9th enum value; §6.7 D1-D8 items are the per-item adjudication inputs.
- [`engine/build_readiness/pdg_papers_extraction/foundations.md`](../../engine/build_readiness/pdg_papers_extraction/foundations.md) §2 (F1) + §3 (F2) + §4 (F3) + §5 (F4) — Session γ foundational-reading findings; §2 confirmed Meyer & Land's threshold-concept framework; §3 found `bridge_concept` is synthesis-author coinage (Adjudication 4 deliberation context); §4 confirmed bottleneck-vs-threshold distinction; §5 confirmed phenomenology-vs-introspection misconception framing (Cluster 5 input, not Cluster 4).
- [`engine/build_readiness/pdg_papers_extraction/adversarial_review.md`](../../engine/build_readiness/pdg_papers_extraction/adversarial_review.md) E.12.2 — five Tier-A fields most affecting embedding semantic quality; this cluster lands all five (`node_type`, `disciplinary_domain`, `granularity`, `canonical_sources`, `misconceptions`); ADR 0094 premise 6 cited basis for landing Tier-A before SEP backfill.
- [`product/seed-graph/migrations/0002_nodes.sql`](../seed-graph/migrations/0002_nodes.sql) — current nodes table (17 columns); the migration adds 14 columns; post-migration nodes table carries 31 columns.
- [`product/seed-graph/migrations/0140_nodes_schema_redesign.sql`](../seed-graph/migrations/0140_nodes_schema_redesign.sql) — the paired migration this ADR commits.
- [`product/seed-graph/migrations/0140_nodes_schema_redesign_rollback.sql`](../seed-graph/migrations/0140_nodes_schema_redesign_rollback.sql) — paired rollback per migration-discipline.
- [Issue #115](https://github.com/StarshipSuperjam/paideia/issues/115) — `historical_node_as_prereq_source` validator soft-warn pending node-class schema extension; partially unblocked by this cluster's `node_type` + `tradition_label` additions; full closure depends on per-domain backfill sequels.
- engine_memory `decisions`-room drawer for ADR 0102 (authored in S-0213) — the conversational deliberation that produced this ADR; recall-by-similarity content for future sessions facing analogous "single-table multi-column schema redesign under deferred-classification posture" choices.
