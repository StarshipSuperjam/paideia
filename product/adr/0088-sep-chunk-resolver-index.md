# ADR 0088 — SEP chunk-resolver index for node-level onward-reading pointers

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0152

## Context

[`product/docs/tensions.md`](../docs/tensions.md) carries OQ-DEC1-D ("Chunk-resolver index vs direct SEP URL pointers") as decide-before-Phase-6, open since 2026-04-29 (S-0001). The use case: when the teaching layer says *"for more on Synthetic A Priori, see SEP"*, what does the schema carry to support that pointer?

The legal posture is settled: SEP URLs and section anchors are *facts* about SEP's structure (uncopyrightable per Feist), not SEP content. [`product/docs/content-strategy.md:4-16`](../docs/content-strategy.md:4) commits to SEP as structural-reference-only: no SEP prose is reproduced to the learner, but SEP's concept inventory and cross-reference adjacency network are used to inform the graph. URL pointers and section anchors fall on the structural-reference side of this commitment.

The close-reading outline (per [`product/docs/reading-system.md:21-43`](../docs/reading-system.md:21)) carries section-to-concept mapping, but only for **user-supplied primary texts** — Opus generates an outline at ingestion-time for each user-uploaded book, mapping its sections to graph nodes. The close-reading outline does not cover SEP. SEP is not a primary text in the close-reading pipeline; it is an external onward-reading reference that the teaching layer recommends. So the SEP pointer shape is a seed-graph-level schema concern, separate from the close-reading outline mechanism.

The current seed graph contains 380 nodes (per [`engine/STATE.md`](../../engine/STATE.md)). Phase 5 authoring sessions consulted SEP for concept-inventory alignment (per `content-strategy.md:287-288`); the [`product/seed-graph/migrations/ROUTING.md`](../seed-graph/migrations/ROUTING.md) narrative entries record SEP alignment per subdomain, but the alignment is implicit in human-readable prose and is not formalized in the schema. No `sep_url` column exists on the nodes table; no `sep_chunks` junction table exists.

### Load-bearing premises

*Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers under the "contract-shape change" class — it commits a new schema-level structure (`sep_chunks` junction table) to the seed-graph contract.*

1. **SEP's URL scheme and section-anchor scheme are stable enough that indexed references survive across the project's lifetime.** *Falsifier:* SEP undergoes a URL reorganization that breaks indexed anchors, requiring large-scale rewrites of the `sep_chunks` rows. *Test status:* SEP's URL scheme has been `plato.stanford.edu/entries/<entry-id>/` since the encyclopedia's launch in 1995; section-anchor IDs (the `#section-N` fragments) are author-assigned and have been stable across the seen revisions in academic citations. **Premise accepted with low-residual risk.** If SEP reorganizes URLs, the rewrite is a one-time migration; the chunk_id index is recoverable.

2. **Section-anchor precision provides measurable pedagogical lift over article-level pointers.** *Falsifier:* Phase 9 cold-test reveals that learners click SEP links rarely enough that the precision difference doesn't measurably affect engagement. *Test status:* unverifiable in-context — requires Phase 9 cold-test empirical signal. Named in Consequences as a known assumption with Phase-9-review fallback (Tier-2 readiness criterion).

3. **Backfill work for 380 existing nodes is bounded and feasible.** *Falsifier:* a representative-sample backfill effort estimate exceeds reasonable session budget (e.g., >2 sessions of dedicated work, or >5min per node × 380 = 32 hours). *Test status:* attempted in-context. SEP article URLs are derivable from node labels for the well-mapped subset (e.g., `transcendental_idealism` → `plato.stanford.edu/entries/kant-transcendental-idealism/`); section anchors require reading the SEP article to identify the relevant section. Estimate: ~2-5 min per node for URL discovery + section-anchor identification (assuming the auditor has SEP open in a browser); 380 nodes × ~3 min average ≈ 19 hours of dedicated work. This is 1-2 dedicated backfill sessions, not 32 hours. **Premise verified** as feasible; budget is bounded.

4. **Phase 6 self-correction's node-mutation pipeline can maintain the chunk_id index across node splits, merges, and deprecations.** *Falsifier:* a Phase 6 node-mutation (split or merge) requires manual chunk-index reconciliation that exceeds the cost of the mutation itself. *Test status:* unverifiable in-context. Named in Consequences as a known assumption with first-exercise readiness criterion when Phase 6 self-correction first mutates a node with non-empty `sep_chunks` rows.

5. **One node may map to multiple SEP sections (one-to-many cardinality).** *Falsifier:* a single SEP section is always sufficient for any given node's onward-reading recommendation. *Test status:* design-level analysis. Example: the `synthetic_a_priori` node may legitimately point at section 2 of the SEP "Kant" article AND section 1 of the SEP "Analytic-Synthetic Distinction" article — both discuss the concept in pedagogically valuable ways. **Premise accepted with the one-to-many cardinality as the schema-level commitment.**

## Decision

A new `sep_chunks` junction table is committed to the seed-graph schema. Schema shape (to be authored in the first Phase 6 migration that touches this surface):

```sql
CREATE TABLE IF NOT EXISTS sep_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    sep_url TEXT NOT NULL,
    section_anchor TEXT,  -- nullable: NULL means article-level pointer (graceful degradation)
    section_title TEXT,   -- nullable: human-readable label for the section, useful in teaching prose
    position INT,         -- nullable: ordering when multiple sections per node
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (node_id, sep_url, section_anchor)
);

CREATE INDEX idx_sep_chunks_node ON sep_chunks (node_id);
```

- **One-to-many cardinality**: a node may map to multiple SEP sections (premise 5). Multiple rows per node are permitted; the `position` column carries ordering when teaching prose wants to surface "first see X, then see Y."
- **Graceful degradation**: `section_anchor` and `section_title` are nullable. A node that maps to a SEP article without section-anchor precision (because the section is unclear, or precision isn't yet worth the effort) carries `(sep_url, NULL, NULL)`; the teaching layer falls back to "see SEP on Kant" rather than "see SEP section 3.2 of Kant's epistemology."
- **CASCADE on node delete**: matches the existing edges-table CASCADE pattern per [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md)'s data-erasure-with-cascade discipline.

Backfill of the 380 existing nodes happens in a dedicated session (or as a batch within Phase 6 self-correction's first sweep). The backfill is one-time work; ongoing maintenance happens as Phase 6 node-mutations add or remove nodes.

## Alternatives Considered

### Chunk-resolver index (chosen)

- **What:** `sep_chunks(node_id, sep_url, section_anchor, section_title, position)` junction table with one-to-many cardinality. Section-anchor and section-title are nullable for graceful degradation to article-level pointers.
- **Pros:** Highest pedagogical precision — learners clicking a SEP recommendation land directly at the section discussing the concept. Schema accommodates both section-anchor and article-level pointers (via nullable columns). One-to-many cardinality matches real-world cases where a concept is discussed in multiple SEP articles or multiple sections. Phase 6 self-correction can incrementally improve precision (start article-level for a new node; refine to section-anchor when teaching surfaces value).
- **Cons:** 380-node backfill cost (estimated ~19 hours per premise 3). Maintenance discipline as Phase 6 mutates nodes. New schema surface adds query complexity to the teaching layer.
- **Rejected because:** not rejected — chosen.

### Article-level `sep_url` TEXT column on nodes

- **What:** Add a single nullable `sep_url TEXT` column to the existing `nodes` table. One URL per node, pointing to the SEP article landing.
- **Pros:** Simplest schema. No junction table. Minimal backfill cost (one URL per node, derivable from node label for most cases; ~1 min per node × 380 ≈ 6 hours).
- **Cons:** No section-anchor precision. Cannot handle the one-to-many case (a node discussed in multiple SEP articles). Schema-extensible to add `sep_section_anchor TEXT` later, but that path is messier than a junction table — adding a column to nodes for a concern that's actually one-to-many is structural sloppiness.
- **Rejected because:** section-anchor precision is the pedagogically valuable affordance; building a minimum-viable shape that doesn't support it forces a structural rework later. The cost of doing it right at first Phase 6 migration is modest (~13 extra hours of backfill); the cost of restructuring later is higher.

### No schema-level pointer; rely on Sonnet parametric recall

- **What:** No `sep_url` column. The teaching layer asks the user's BYOK model to generate the SEP URL from parametric training-data knowledge.
- **Pros:** Zero schema cost. Zero backfill. Zero ongoing maintenance.
- **Cons:** Hallucination risk — the model may generate a URL that doesn't exist (SEP article that was renamed or doesn't exist). Under [ADR 0065](0065-oss-pivot-and-byok-disposition.md)'s BYOK regime, users may bring smaller open-weights models with weaker SEP knowledge; URL recall reliability varies per user's model choice. The schema-level commitment to *facts about SEP* (URLs are facts per Feist) should not depend on model capability.
- **Rejected because:** anti-pattern under BYOK. The same logic that drove [ADR 0086](0086-model-agnostic-embedding-storage-architecture.md)'s model-agnostic embedding storage applies here: schema commits should be model-agnostic, not bound to assumptions about model parametric knowledge.

### Defer the schema-level choice; bootstrap with first Phase 6 session

- **What:** ADR 0088 commits no schema. The Phase 6 session that first needs SEP pointers picks the shape and authors the migration.
- **Pros:** Lowest schema-now risk.
- **Cons:** OQ-DEC1-D is explicitly *decide-before-Phase-6*; pure deferral violates the decide-before constraint. The Phase 6 session that lands the first SEP-pointer migration faces the same chunk-resolver-vs-direct-URL question with no prior contract; effectively deferring is re-running this deliberation at a less convenient moment.
- **Rejected because:** the tension's own decide-before-Phase-6 framing forecloses pure deferral. The ADR commits to a shape (chunk-resolver junction table); concrete dim values (section-anchor population per node) accrue during Phase 6 backfill.

## Consequences

- **Phase 6 entry can proceed against an explicit SEP-pointer contract.** The schema shape is fixed; the first Phase 6 migration to author SEP pointer infrastructure follows the chunk-resolver pattern. Backfill of 380 existing nodes is a one-time Phase 6 task (or, optionally, a dedicated pre-Phase-6 session if user prefers).

- **New schema (authored at first Phase 6 migration touching this surface):**
  - `sep_chunks(node_id, sep_url, section_anchor, section_title, position, created_at)` junction table with `UNIQUE (node_id, sep_url, section_anchor)` and `CASCADE` on node delete per ADR 0031.
  - `CREATE INDEX idx_sep_chunks_node ON sep_chunks (node_id);` for the common case (teaching layer queries by node).
  - Per ADR 0055 + the migration-discipline contract, the migration includes RLS-enable + GRANT statements at activation time (currently deferred per [Issue #117](https://github.com/StarshipSuperjam/paideia/issues/117) — no Data API consumer yet).

- **First-exercise readiness criteria:**
  - **T1-A (schema creation):** the first Phase 6 migration creating the `sep_chunks` table applies cleanly via [`engine/tools/apply_migration.py`](../../engine/tools/apply_migration.py); CASCADE behavior verified via Layer 2.5 postcondition assertion (per ADR 0055 + ADR 0039 amendment).
  - **T1-B (backfill batch):** a dedicated backfill session (or Phase 6 batch) populates `sep_chunks` rows for ≥80% of the 380 existing nodes. The 20% gap accommodates nodes where SEP coverage is genuinely thin (e.g., service nodes, very obscure concept variants).
  - **T1-C (teaching-layer query):** Sonnet's prompt-layer scaffolding queries `sep_chunks` by node_id and surfaces the top-ordered section_title in onward-reading recommendations.
  - Captured in `engine/build_readiness/sep_chunk_resolver_first_exercise.md` (authored in this commit per ADR 0053).

- **`product/docs/content-strategy.md` "SEP as Structural Reference, Not Content Source" subsection** gains a forward-pointer to ADR 0088 for the schema-level commitment. Done in this commit.

- **`product/docs/tensions.md` OQ-DEC1-D section flips from "Open" to "Resolved by ADR 0088"** in the same commit as this ADR.

- **No supersession.** [ADR 0011](0011-no-hosted-copyrighted-material.md) (no hosted copyrighted material), [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md) (confidence_level on nodes), and [ADR 0046](0046-structural-reference-posture-extends-to-philosophy-reference-works.md) (structural-reference posture for philosophy reference works) all remain Accepted; this ADR adds schema commitment without disturbing prior ones. The chunk-resolver pattern is the operationalization of ADR 0046's structural-reference posture for SEP specifically.

- **The Phase-6-blocker set is now empty.** OQ-DEC1-A (ADR 0085), OQ-DEC1-C (ADR 0086), OQ-DEC1-B (ADR 0087), and OQ-DEC1-D (ADR 0088 — this ADR) all close in S-0152. Phase 6 self-correction master plan can be authored when ready.

- **Cost of pivoting if Phase 9 cold-test surfaces premise 2 falsifier (section-anchor precision provides no measurable lift):** modest. The schema accommodates article-level pointers via NULL section_anchor; if section-anchor backfill turns out to be wasted effort, the project simply stops backfilling section anchors. Existing rows remain valid (NULL section_anchor degrades gracefully). No schema rewrite needed.

## See also

- [ADR 0011](0011-no-hosted-copyrighted-material.md) — No hosted or distributed copyrighted material; SEP URLs and section anchors are facts (Feist), not content, so this ADR is consistent.
- [ADR 0030](0030-confidence-level-evidentiary-mode-on-nodes.md) — `confidence_level` and `evidentiary_mode` on nodes; relevant because SEP-aligned nodes carry `confidence_level: INTERPRETED` per Phase 5 ROUTING.md narratives.
- [ADR 0031](0031-erasure-mechanism-and-individual-only-regime.md) — Erasure with cascade; the `sep_chunks` CASCADE-on-node-delete pattern matches this discipline.
- [ADR 0046](0046-structural-reference-posture-extends-to-philosophy-reference-works.md) — Structural-reference posture for philosophy reference works as a class; this ADR operationalizes the posture for SEP specifically.
- [ADR 0055](../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — `apply_migration.py` wrapping; the first Phase 6 migration creating `sep_chunks` applies through this wrapper with Layer 2.5 postcondition assertions.
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — Extraction step (fourth and final natural exercise in this session).
- [`product/docs/content-strategy.md`](../docs/content-strategy.md) "SEP as Structural Reference" — original commitment now ADR-specified.
- [`product/docs/reading-system.md`](../docs/reading-system.md) "Outline Generation" — separate mechanism (covers user-supplied primary texts, not SEP).
- [`engine/build_readiness/sep_chunk_resolver_first_exercise.md`](../../engine/build_readiness/sep_chunk_resolver_first_exercise.md) — first-exercise readiness note per ADR 0053.
- [`product/docs/tensions.md`](../docs/tensions.md) OQ-DEC1-D — resolved by this ADR.
- [Issue #117](https://github.com/StarshipSuperjam/paideia/issues/117) — Supabase Data API GRANTs; the first migration creating `sep_chunks` will need GRANT statements if a Data API consumer is introduced before Oct 30, 2026.
