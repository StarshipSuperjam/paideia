# SEP chunk-resolver index — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. [ADR 0088](../../product/adr/0088-sep-chunk-resolver-index.md) (S-0152) commits the `sep_chunks` junction-table schema for node-to-SEP-section pointers. First natural exercise is the first Phase 6 migration that authors the table, plus the backfill batch that populates rows for the 380 existing seed-graph nodes.
>
> Criterion-4 evaluation (consequences span ≥3 ops docs OR ≥5 tooling files): satisfied via 1 ADR (0088) + 1 migration authoring the table + 1 backfill session populating ~380 rows + 1 product-docs forward-pointer (content-strategy.md) + 1 readiness note + Phase 6 teaching-layer prompt-scaffolding integration = ≥6 surfaces. Readiness note required.

## What this mechanism does

ADR 0088 commits a junction-table schema for node-to-SEP-section pointers:

```sql
sep_chunks(
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    sep_url TEXT NOT NULL,
    section_anchor TEXT,   -- nullable: graceful degradation to article-level
    section_title TEXT,    -- nullable: human-readable label
    position INT,          -- nullable: ordering when multiple sections per node
    created_at TIMESTAMPTZ,
    UNIQUE (node_id, sep_url, section_anchor)
)
```

The teaching layer queries `sep_chunks` by `node_id` to surface SEP onward-reading pointers in real-time teaching prose. One-to-many cardinality permits a node to map to multiple SEP sections (e.g., `synthetic_a_priori` → SEP "Kant" section 2 + SEP "Analytic-Synthetic Distinction" section 1). Graceful degradation: NULL `section_anchor` means article-level pointer (teaching prose says "see SEP on Kant" rather than "see SEP section 3.2 of Kant's epistemology").

## Tier 1 — close at first natural exercise (Phase 6 entry)

- **T1-A — schema creation migration applies cleanly.** The first Phase 6 migration authoring `sep_chunks` invokes via [`engine/tools/apply_migration.py`](../tools/apply_migration.py) per [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md). Layer 2.5 postcondition assertions (per ADR 0055 + [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) Consequences amendment) verify: (i) `sep_chunks` table exists; (ii) `CASCADE` behavior on node delete works (synthetic test: insert a node, insert a `sep_chunks` row referencing it, delete the node, verify the chunk row is gone); (iii) `UNIQUE (node_id, sep_url, section_anchor)` constraint rejects duplicate (node_id, URL, anchor) inserts. Migration applies with exit code 0; `supabase_migrations.schema_migrations` recorded.
- **T1-B — backfill batch populates rows for ≥80% of existing nodes.** A dedicated backfill session (or Phase 6 batch) reads existing nodes and authors `sep_chunks` rows. Per ADR 0088 premise 3, estimated effort: ~3 min average per node × 380 nodes ≈ 19 hours of dedicated work. The 20% gap accommodates: service nodes (lower SEP coverage); very obscure concept variants; nodes whose SEP coverage is genuinely thin. Each backfilled row carries `sep_url` (required); `section_anchor` populated where the auditor identifies the right section; `section_title` populated alongside `section_anchor` (human-readable label).
- **T1-C — teaching-layer query in Sonnet's prompt-layer scaffolding.** Sonnet's per-turn prompt assembly queries `sep_chunks` by current concept's `node_id`; the top-ordered (lowest `position`) row's `(sep_url, section_anchor, section_title)` surfaces in the prompt context as onward-reading material. Verified via a synthetic teaching-loop test: given a current concept with ≥1 `sep_chunks` row, Sonnet's prompt context includes the SEP reference; given a current concept with zero `sep_chunks` rows, Sonnet's prompt context omits the SEP-reference slot (no hallucinated URLs).

## Tier 2 — close at subsequent natural occasions

- **First multi-section node observed in teaching.** A node with ≥2 `sep_chunks` rows is the current concept in a teaching session; Sonnet's prompt-layer correctly surfaces the top-ordered section first and (if teaching prose calls for it) the second-ordered section as follow-up reading. Validates the one-to-many cardinality decision.
- **First section-anchor-null graceful-degradation observation.** A node with `section_anchor IS NULL` is the current concept; Sonnet's prompt prose reads as "see SEP on <article title>" rather than "see SEP section X.Y of <article title>." Verifies graceful degradation works without scaffolding bugs.
- **First Phase 6 node-mutation propagating to `sep_chunks`.** Phase 6 self-correction splits, merges, or deprecates a node with non-empty `sep_chunks` rows. The chunk-index reconciliation works cleanly via CASCADE (deprecate → delete cascades); for split/merge, the mutation migration manually re-points or re-creates `sep_chunks` rows on the new node(s). Validates premise 4 (Phase 6 node-mutation pipeline maintains the chunk_id index).
- **First SEP URL rewrite, if/when SEP reorganizes.** Premise 1 named the residual risk: SEP could reorganize URLs, breaking indexed anchors. If/when this fires, a one-time data migration rewrites affected `sep_chunks` rows; record the migration SHA + scope here.

## Tier 3 — defer indefinitely (recorded for future audit)

- **Auto-validation of `sep_url` reachability.** A periodic job that checks each `sep_chunks.sep_url` for 200-OK reachability and flags broken links. Defer until at least 30+ `sep_chunks` rows are populated AND ≥1 broken-URL observation surfaces in the wild. Premature mechanization before there's an observed broken-link problem.
- **`sep_chunks` for the close-reading outline.** Close-reading outlines could optionally cross-reference SEP at section-mapping time (e.g., "this section of the Phenomenology of Spirit maps to graph node X and SEP article Y section Z"). Defer until close-reading pipeline lands AND a use case surfaces. Currently the outline maps user-supplied primary texts to graph nodes; SEP is the onward-reference layer the teaching layer hits, not the close-reading layer.
- **Internationalization.** SEP is English-only at present; if non-English curriculum surfaces (Phase 8+?), parallel reference works (IEP, Routledge, language-specific encyclopedias) may need their own `*_chunks` tables. Defer; premature without a non-English curriculum commitment.

## Empirical record (pending)

*Closes when the first Phase 6 migration lands `sep_chunks` AND the backfill session populates ≥80% of existing nodes AND the teaching-layer query surfaces a real SEP reference in a teaching session.*

This readiness note will be updated with:
- The schema-creation migration SHA + Layer 2.5 postcondition assertion results.
- The backfill session SHA + node-coverage percentage achieved + any nodes deliberately skipped (with reason).
- The first natural teaching-session observation of the SEP reference surfacing in Sonnet's prompt context.
- Any falsifier signal that surfaces (URL stability, section-anchor pedagogical lift, backfill cost, Phase 6 maintenance cost) and how the session responded.
