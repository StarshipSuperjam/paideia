# ADR 0017 — Postgres + recursive CTEs over OWL/RDF

- **Status:** Accepted (Amended by [ADR 0095](0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) — same substrate conclusion; OSS Apache 2.0 + cost-priced posture per ADRs 0065 + 0093 raises the revisit bar with four explicit criteria; Apache AGE named as the only credible Postgres-internal revisit target)
- **Date:** 2026-04-09
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Knowledge graphs have established stacks. **OWL/RDF** is the standard semantic-web format, providing transitive closure inference, SPARQL for traversal, and interoperability with Wikidata/DBpedia. **Dedicated graph databases** (Neo4j, JanusGraph, Memgraph) provide native graph traversal via Cypher or Gremlin, with optimizations for multi-hop queries on dense topologies. **Relational databases with recursive CTEs** (Postgres, SQL Server) handle directed graph traversal as a join-style query — slower in theory than dedicated graph stores, but native to the relational substrate and integrated with the rest of the data model.

Both alternatives were evaluated. They were rejected because they solve problems Paideia doesn't have, and they don't solve the one it does.

**Paideia's graph traversal is narrow.** Given a target concept, return the topologically sorted prerequisite chain, filtered by the learner's mastery state. That's a directed traversal with a join against relational event data. The heavy computation is the **mastery function** running against temporal events — not open-ended semantic reasoning across rich ontological relationships.

**OWL class hierarchies would reintroduce thinker-level aggregation** ("Kantian Epistemology" as a superclass containing Transcendental Idealism, Synthetic A Priori, etc.), which the node granularity principle (ADR 0008) explicitly rejected. Entity resolution — the one place semantic structure would help — is an LLM task (fuzzy matching against labels and aliases per ADR 0020), not a logical entailment task.

**Dedicated graph stores** introduce a second data system, a second query language, and cross-system joins for mastery-filtered traversal. At projected scale (hundreds to low thousands of nodes per subdomain), Postgres handles graph traversal natively with recursive CTEs. The performance case for a graph database doesn't materialize until tens of thousands of nodes with complex multi-hop queries.

Migration risk is low in both directions. Nodes and edges in Postgres export trivially to RDF triples if the need ever arises.

## Decision

The graph is stored in **Postgres** alongside the rest of the data model. Traversal uses **recursive CTEs** for directed prerequisite walks, joined with `learner_events` and `mastery_snapshots` for mastery-filtered queries. No OWL/RDF, no dedicated graph database. Entity resolution remains an LLM task with `summary` fingerprints and `aliases[]` (per ADR 0020), not a logical-entailment task.

## Consequences

- Schema fits the existing Supabase Postgres deployment. Mastery-filtered traversal is one query, not a cross-system join.
- Recursive CTE performance is the bound on traversal depth. At projected scale (low thousands of nodes; chains rarely deeper than 8–10 hops), this is comfortable. If scale grows past the threshold where recursive CTEs degrade, options remain (materialized closure tables, partial precomputation), all without changing the substrate.
- Mastery computation runs in Postgres (per ADR-DEC1-A's anticipated decision in Phase DEC.1; the open tension `OQ-DEC1-A` in `docs/tensions.md` confirms or revisits this at Phase 6). Server-side mastery computation is the working assumption.
- Interoperability with semantic-web tools is sacrificed. If a future use case demands SPARQL queries against Paideia's graph, the export-to-RDF path remains available.
- Operational simplicity: one DB, one backup, one access-control model, one migration tool (`supabase db push`).
- The `validate_graph()` utility (per ADR 0016) connects via `psycopg` directly — no intermediary query layer.
- This ADR is **revisitable at scale**. The thresholds where Postgres no longer suffices are reasonably well-known; if Paideia approaches them, a Status: Superseded ADR can document the substrate change with the migration plan.

## Amendment (S-0203 per ADR 0095)

[ADR 0095](0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) (Phase 6 tool-stack settlement; S-0203, 2026-05-18) amends this ADR in-body — Status stays Accepted; the substrate conclusion (Postgres + JSONB + recursive CTEs) holds; two structural additions land:

1. **Decisive settlement of `adversarial_review.md` E.10.3's "forcing function never fires" critique.** The original Consequences-section framing ("revisitable at scale; thresholds well-known; supersession ADR documents migration plan") was empirically critiqued during the PDG papers extraction pre-phase as offering no actual forcing function — the threshold for revisiting (analytics-or-trace-informed-revision workflows per Cluster 9's L3.15 finding) is the same trigger as the Phase 7+ work that would benefit from a graph-store, meaning the evaluation would never have a forcing function. ADR 0095 settles the evaluation decisively for Phase 6+ (the answer is Postgres) rather than deferring under a softer trigger.
2. **OSS-license-compatibility and cost-priced-shipping constraints from [ADR 0065](0065-oss-pivot-and-byok-disposition.md) + [ADR 0093](0093-phase-6-product-trajectory-formalization.md) are now load-bearing.** This ADR predated the OSS-flip (authored 2026-04-09; OSS flip at S-0128 / 2026-05-08); the original Consequences did not carry constraints against commercial-DB licensing (Neo4j Enterprise, AWS Neptune) or copyleft-friction (Neo4j Community GPLv3) because the project's release surface was different. ADR 0095 surfaces these constraints as foreclosing factors for any alternative substrate evaluation and structures them as four-criterion bar (demonstrated unfixable Postgres failure + Apache 2.0-compatible alternative + maintainer-cost-neutral + amortizable migration cost).

ADR 0095 names **Apache AGE** (Apache 2.0 PostgreSQL extension exposing Cypher syntax over an in-Postgres graph store) as the only credible revisit target if recursive-CTE performance becomes the actual bottleneck on Tier-A-redesigned schema (per [ADR 0094](0094-phase-6-scope.md) Phase 6 expansion). Adopting AGE would amend this ADR + ADR 0095, not supersede them — AGE keeps the substrate Postgres-internal.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Graph Structure.
- [`docs/infrastructure.md`](../docs/infrastructure.md) — Cloud Hosting Stack.
- [`STATE.md`](../../engine/STATE.md) — Supabase project ref.
- ADR 0008 — Concept nodes (no class hierarchy needed).
- ADR 0015 — Event-sourced learner model (the join target for mastery-filtered traversal).
- ADR 0020 — Teaching notes separate from summary (entity resolution uses summary, not OWL).
- `docs/tensions.md` `OQ-DEC1-A` — server-side mastery computation (Phase DEC.1 confirmation).
- [ADR 0095](0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) — Phase 6 tool-stack settlement; amends this ADR in-body (see "Amendment" section above).
- [ADR 0065](0065-oss-pivot-and-byok-disposition.md) — OSS pivot and BYOK disposition; commitment 5 (cost-priced shipping) load-bearing for ADR 0095's revisit-bar criterion 3.
- [ADR 0093](0093-phase-6-product-trajectory-formalization.md) — Phase 6 product-trajectory formalization; commitment 2 (OSS forks not foreclosed) load-bearing for ADR 0095's revisit-bar criterion 2.
