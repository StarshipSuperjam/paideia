# P_1 — SQL schema implementation (Phase 3)

> Postgres schema deployed to the Supabase dev project via versioned migrations. Translates [`product/docs/architecture.md`](../product/docs/architecture.md) and [`product/docs/learner-model.md`](../product/docs/learner-model.md) into live tables.

## Phase scope

Phase 3 is the first substantive build phase: the schema that every downstream phase reads or writes to. The schema is the substrate the engine validates against (Phase 4), the seed graph populates (Phase 5), the retrieval layer queries (Phase DEC.1 + Phase 7), and the UI renders (Phase 9). Per [ROADMAP Phase 3](../ROADMAP.md), the schema lands as `0001_*.sql` Supabase migrations and forward; the deployment target is the `paideia-dev` Supabase project (PostgreSQL 17.6 per [`engine/STATE.md`](../engine/STATE.md) Infrastructure).

The schema's design is settled in the contract layer — [ADR 0017](../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md) (Postgres + recursive CTEs over OWL/RDF), [ADR 0019](../product/adr/0019-two-column-rigor-score-override.md) (two-column rigor score), [ADR 0020](../product/adr/0020-teaching-notes-separate-from-summary.md) (teaching notes separate), [ADR 0021](../product/adr/0021-node-deprecation-status-superseded-by.md) (node deprecation), [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) (structural-not-substantive learner storage), [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) (`confidence_level`), [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) (erasure mechanism). This chunk implements; it does not re-decide.

## Output

Migration files under `product/seed-graph/migrations/` (post-`M_partition_migration` path; pre-migration the path is `supabase/migrations/`). The session settles whether the migrations directory lives under `product/seed-graph/` or as a sibling — the [ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md) shape names `product/seed-graph/` as the Phase 5 content target; the schema migrations may sit beside it or inside it, settled in-session.

Tables to land:

- **`nodes`** — `id`, `label`, `domain[]`, `summary`, `teaching_notes`, `aliases[]`, `rigor_score_computed`, `rigor_score_adjustment`, `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC` per [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md)), `confidence` (numeric), `provenance`, `status`, `superseded_by` (per [ADR 0021](../product/adr/0021-node-deprecation-status-superseded-by.md)), `graph_version_added`, timestamps.
- **`edges`** — `source_id`, `target_id`, `type`, `weight`, `confidence`, `provenance`, `evidence`, `graph_version_added`.
- **`learner_events`** — event-sourced log per [ADR 0015](../product/adr/0015-event-sourced-learner-model.md) and [`product/docs/learner-model.md`](../product/docs/learner-model.md). Structured `context` columns per [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — no free-text grab-bags.
- **`mastery_snapshots`** — cached mastery state per [ADR 0023](../product/adr/0023-engagement-depth-aggregation.md), [ADR 0024](../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](../product/adr/0025-historical-maximum-tracking.md). Engagement-depth aggregation as weighted geometric mean; sub-signals stored raw; historical maximum tracking on the snapshot row.
- **`tension_log`** — per [`product/docs/self-correction.md`](../product/docs/self-correction.md) and [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md). `exchange_summary` as JSONB-with-named-fields.
- **`settings`** — `graph_version` counter and other singleton state.

`ON DELETE CASCADE` discipline per [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md): account deletion cascades to every learner-state row.

## Success criteria

- `supabase db push` applies the migrations cleanly to the dev DB. Rollback works.
- `\d+ nodes` shows the expected columns including `confidence_level`.
- `learner_events` and `tension_log` schemas conform to [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md): `exchange_summary` JSONB-with-named-fields; `context` structured columns; no free-text grab-bags.
- `OQ-PRIVACY-A` (erasure mechanism) and `OQ-PRIVACY-B` (institutional-regime column reservation) are settled before migration authoring begins. Both closed by [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) at S-0011 — verify the column shapes match the ADR.
- `engine/tools/validate.py` clean (0 hard-fails).
- ENGINE_LOG entry under `[Unreleased]` for `Added` with the migration filenames and a one-line description per table.

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md) — for the current state and Supabase project ref.
- [`ROADMAP.md`](../ROADMAP.md) — Phase 3 success criteria.
- [`product/docs/architecture.md`](../product/docs/architecture.md) — node/edge schema, rigor-score model, two-column override, ideas-as-nodes.
- [`product/docs/learner-model.md`](../product/docs/learner-model.md) — event-sourced model, engagement depth, scaffolding proximity.
- [`product/docs/self-correction.md`](../product/docs/self-correction.md) — `tension_log` schema and emission categories.
- [`product/adr/0026-persistent-learner-storage-structural-not-substantive.md`](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — structured-columns discipline.
- [`product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md`](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) — `confidence_level` enum.
- [`product/adr/0031-erasure-mechanism-and-individual-only-regime.md`](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) — cascade discipline.
- [`engine/tools/validate.py`](../engine/tools/validate.py) — for the schema-validation extension point that `P_2_graph_validation.md` will fill out next.

## Load-bearing ADRs

[ADR 0015](../product/adr/0015-event-sourced-learner-model.md), [ADR 0017](../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md), [ADR 0019](../product/adr/0019-two-column-rigor-score-override.md), [ADR 0020](../product/adr/0020-teaching-notes-separate-from-summary.md), [ADR 0021](../product/adr/0021-node-deprecation-status-superseded-by.md), [ADR 0023](../product/adr/0023-engagement-depth-aggregation.md), [ADR 0024](../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), [ADR 0025](../product/adr/0025-historical-maximum-tracking.md), [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md), [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md).

## Estimated context budget

Substantive extraction tier: target 60%, cap 70%. The schema design is settled; the work is rendering it as SQL + verifying against the ADR contracts. Context-amplification risk is moderate — the chunk reads three substantial design docs (`architecture.md`, `learner-model.md`, `self-correction.md`) plus 11 ADRs by reference. If the chunk needs to read every ADR's full text, budget pressure surfaces; the mitigation is to read ADRs only when their schema implication is unclear from the design doc alone.

## Session sequencing

Single session preferred. Multi-session fallback: split by table family — Session 1 lands `nodes` / `edges` / `settings` (graph schema); Session 2 lands `learner_events` / `mastery_snapshots` / `tension_log` (learner schema). The split mirrors the structural / substantive boundary in [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md).

## Open tensions consumed

None active at S-0023 close. `OQ-PRIVACY-A` and `OQ-PRIVACY-B` were closed by [ADR 0031](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) at S-0011 — the schema implements the closed decisions.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 3 — full phase scope.
- [`product/docs/architecture.md`](../product/docs/architecture.md) — schema design source.
- [`product/docs/learner-model.md`](../product/docs/learner-model.md) — learner schema source.
- [`P_2_graph_validation.md`](P_2_graph_validation.md) — the next chunk; consumes this schema.
