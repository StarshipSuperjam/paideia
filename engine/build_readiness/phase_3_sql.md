# Phase 3 — SQL schema build-readiness report

> Authored by S-0027 (gate session) for S-0028 (build session) per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md). The build session reads this at boot. If Tier 1 contains unresolved items at boot, the build session halts and escalates.
>
> Chunk: [`build_plan/P_1_sql_schema.md`](../../build_plan/P_1_sql_schema.md). Source documents: [`product/docs/architecture.md`](../../product/docs/architecture.md), [`product/docs/learner-model.md`](../../product/docs/learner-model.md), [`product/docs/self-correction.md`](../../product/docs/self-correction.md). Load-bearing ADRs: [0015](../../product/adr/0015-event-sourced-learner-model.md), [0017](../../product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md), [0019](../../product/adr/0019-two-column-rigor-score-override.md), [0020](../../product/adr/0020-teaching-notes-separate-from-summary.md), [0021](../../product/adr/0021-node-deprecation-status-superseded-by.md), [0023](../../product/adr/0023-engagement-depth-aggregation.md), [0024](../../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), [0025](../../product/adr/0025-historical-maximum-tracking.md), [0026](../../product/adr/0026-persistent-learner-storage-structural-not-substantive.md), [0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md), [0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md).

## Pre-session decisions (Tier 1 resolutions)

The five Tier 1 findings from the adversarial analysis preceding S-0027 (preserved in [`~/.claude/plans/the-next-session-begins-lazy-bentley.md`](file://~/.claude/plans/the-next-session-begins-lazy-bentley.md) Findings appendix). Each is settled before S-0028 opens:

### T1-A — Auth model: local `users` table mirror

**Decision.** Phase 3 creates a local `public.users` table that mirrors `auth.users` (Supabase-managed). Triggers on `auth.users` INSERT and DELETE keep the mirror synchronized. App-schema foreign keys target `public.users(id)` with `ON DELETE CASCADE`. Account deletion deletes the `auth.users` row, which propagates via the DELETE trigger to the `public.users` row, which (via declarative `ON DELETE CASCADE`) cascades through every learner-state row in one transaction.

**S-0028 correction.** Originally specified an INSERT trigger only. Without a paired DELETE trigger, account deletion via Supabase Auth removes the `auth.users` row but never deletes the `public.users` mirror, and the `ON DELETE CASCADE` on learner-state FKs never fires — silently violating ADR 0031. S-0028's `0001_users_mirror.sql` includes both `on_auth_user_created` and `on_auth_user_deleted` triggers. Recorded in ENGINE_LOG `### Changed`.

**Rationale.** The decision keeps cascade discipline declarative wherever possible (one trigger plus standard ON DELETE CASCADE clauses, vs. a stored-procedure-only cleanup endpoint). It also avoids app-schema FKs targeting the Supabase-managed `auth.users` table directly, which Postgres permits but Supabase tooling makes awkward.

**Artifact.** [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) Consequences amended in S-0027 to pin the local-mirror shape. The build session implements per the ADR's amended Consequences entry.

### T1-B — RLS posture: on with v1 policies

**Decision.** Row-level security is enabled on every learner-state table in `public.*`. Phase 3 ships v1 policies that gate by `user_id = auth.uid()`. The `public.users` mirror table also carries RLS — its policy permits `id = auth.uid()` reads and rejects writes (the table is trigger-populated, not app-written).

**Rationale.** Confirmed via Supabase MCP at S-0027 build-readiness gate exercise: Postgres 17.6 on `paideia-dev`, `auth.users` provisioned with RLS enabled, `public` schema empty. Supabase convention is RLS-on for `public.*` tables exposed via PostgREST; landing tables without policies leaves them either inaccessible (RLS on, no policy) or fully open (RLS off). The user directed Option 2 from the original analysis.

**Artifact.** RLS policies are authored in Phase 3 migrations alongside their respective `CREATE TABLE` statements. The migration-discipline.md gate (Layer 2) enforces `ENABLE ROW LEVEL SECURITY` on every `CREATE TABLE` in `public.*` — the gate is in force from S-0028 forward.

### T1-C — `tension_log` JSONB enum vocabularies

**Decision.** v1 vocabularies for `teaching_moves_tried`, `friction_type`, and `suggested_review_focus` are authored in [`product/seed-graph/migrations/TENSION_VOCABULARY.md`](../../product/seed-graph/migrations/TENSION_VOCABULARY.md). The Phase 3 migration consumes these as JSONB shape constraints (CHECK clauses or paired ALTER TABLE statements). Phase 6 batch review may refine the vocabularies under [ADR 0026](../../product/adr/0026-persistent-learner-storage-structural-not-substantive.md)'s amendment discipline.

**Rationale.** [ADR 0026](../../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) sub-decision (1) explicitly defers the vocabularies to "authored alongside the Phase 3 schema migration." S-0027's build-readiness exercise authored them as a planning artifact (not a build artifact) so S-0028 inherits a settled vocabulary rather than improvising one under build pressure.

**Artifact.** [`product/seed-graph/migrations/TENSION_VOCABULARY.md`](../../product/seed-graph/migrations/TENSION_VOCABULARY.md). The build session reads this and bakes the IN-list constraints into the `tension_log` migration.

### T1-D — Universal expression contract widening

**Decision.** [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md)'s three-layer posture is generalized to all AI authoring patterns via [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). The SQL/migrations row in [`expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md) is fully instantiated: Layer 1 source-of-truth = [`migration-discipline.md`](../operations/migration-discipline.md); Layer 2 gate = `validate.py`'s `validate_sql_gates()` invoked by the pre-commit hook; Layer 3 cold-review = extended cold-context review pass at session shutdown.

**Rationale.** S-0026's [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) scoped to Python under engine/, leaving SQL migrations outside any contract. Phase 3 SQL is the first substantive build that would have authored under no discipline; the user directed widening before Phase 3 opens.

**Artifact.** [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md), [`expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md), [`migration-discipline.md`](../operations/migration-discipline.md), `validate_sql_gates()` in [`engine/tools/validate.py`](../tools/validate.py), pre-commit SQL-gates branch in [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit), session-shutdown-sequence cold-review SQL extension. All authored in S-0027 Phase A.

### T1-E — Stop-and-think discipline

**Decision.** Every substantive build session is preceded by a gate session whose deliverable is a build-readiness report (this file is the first such report). The protocol is committed in [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md); the operational surface is [`build-readiness-gate.md`](../operations/build-readiness-gate.md). The session-build-lifecycle boot procedure reads the report at boot and halts on absence-or-unresolved-Tier-1.

**Rationale.** The user named the failure mode directly: "the AI is desperate to move forward at every step. I need to bake in a stop-and-think check before each step." The gate is structural — the build session has no path to substantive authoring that bypasses the readiness check.

**Artifact.** [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md), [`build-readiness-gate.md`](../operations/build-readiness-gate.md), [`session-build-lifecycle.md`](../operations/session-build-lifecycle.md) step 5 amendment, this report itself as the protocol's first execution.

## Tier 2 decisions

Concrete answers the build session implements without re-deciding. SQL fragments below are authoritative — the migration copies them verbatim where applicable.

### T2-A — Enum-modeled TEXT columns carry CHECK constraints

Every closed-set TEXT column listed below carries a `CHECK (... IN (...))` constraint. Edge `type` is intentionally exempt per architecture.md:182 (additivity over enum-strictness; predicate validation lives at PREDICATE_MANIFEST/Phase 4 audit).

```sql
-- nodes
confidence_level TEXT NOT NULL DEFAULT 'INTERPRETED'
  CHECK (confidence_level IN ('EXTRACTED', 'INTERPRETED', 'SYNTHETIC')),

status TEXT NOT NULL DEFAULT 'active'
  CHECK (status IN ('active', 'deprecated', 'superseded')),

-- learner_events
interaction_type TEXT NOT NULL
  CHECK (interaction_type IN (
    'direct_teaching', 'assessment', 'callback_reference',
    'incidental_mention', 'cross_domain_connection', 'backward_inference'
  )),

-- tension_log (top-level columns; JSONB exchange_summary fields handled separately)
tension_type TEXT NOT NULL
  CHECK (tension_type IN (
    'struggle_unresolved', 'unexpected_ease', 'spontaneous_connection',
    'source_ineffective', 'mastery_contradiction'
  ))
```

The `interaction_type` enum is fixed at v1 per learner-model.md's six interaction types. Adding a value is a one-line migration that updates the IN list; removing a value requires a backfill plan and an ADR.

### T2-B — Sub-signal range and NULL discipline on `learner_events`

Per [ADR 0024](../../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), sub-signals are NULL when interaction_type is `backward_inference` or `incidental_mention`; otherwise they carry values in [0, 1].

```sql
-- learner_events (column declarations)
generative_ratio NUMERIC NULL,
scaffolding_distance NUMERIC NULL,
novelty NUMERIC NULL,

-- Table-level CHECK
CONSTRAINT sub_signals_range_or_null CHECK (
  (interaction_type IN ('backward_inference', 'incidental_mention'))
  OR (
    generative_ratio BETWEEN 0 AND 1
    AND scaffolding_distance BETWEEN 0 AND 1
    AND novelty BETWEEN 0 AND 1
  )
)
```

### T2-C — `mastery_snapshots` full schema

```sql
CREATE TABLE public.mastery_snapshots (
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  concept_id TEXT NOT NULL REFERENCES public.nodes(id),
  mastery_score NUMERIC NOT NULL,
  max_historical_score NUMERIC NOT NULL DEFAULT 0,
  engagement_depth NUMERIC NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, concept_id)
);

CREATE INDEX mastery_snapshots_user_id_idx ON public.mastery_snapshots (user_id);
CREATE INDEX mastery_snapshots_concept_id_idx ON public.mastery_snapshots (concept_id);

ALTER TABLE public.mastery_snapshots ENABLE ROW LEVEL SECURITY;
CREATE POLICY mastery_snapshots_user_isolation ON public.mastery_snapshots
  USING (user_id = auth.uid());
```

The cache is mutable (one row per user-concept pair). `computed_at` records last refresh; staleness checks at Phase 6/7 use the column. `max_historical_score` defaults to 0; recomputation discipline lives at Phase 6 per ADR 0025.

**S-0028 correction.** Originally declared `concept_id UUID`. `nodes.id` is `TEXT` per [`product/docs/architecture.md:103`](../../product/docs/architecture.md) (slugified human-readable concept name with explicit cross-domain readability rationale at architecture.md:124) and [`product/docs/self-correction.md:34`](../../product/docs/self-correction.md). The fragment is updated to `concept_id TEXT REFERENCES public.nodes(id)`. The drift was gate-session typo, not a settled design change. Recorded in ENGINE_LOG `### Changed`.

### T2-D — `settings.graph_version` initialization and increment contract

```sql
CREATE TABLE public.settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL
);

INSERT INTO public.settings (key, value)
VALUES ('graph_version', '1'::JSONB);

ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;
-- settings is server-managed; no learner-facing policy. Service-role access only.
CREATE POLICY settings_service_role_only ON public.settings
  USING (auth.jwt()->>'role' = 'service_role');
```

The increment contract for Phase 5 seed sessions lives in [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) (amended in S-0027): each Phase 5 session reads the current value, increments by one, and writes that value to every `graph_version_added` field on its inserted nodes/edges.

### T2-E — `edges` PK and unique constraint

```sql
CREATE TABLE public.edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id TEXT NOT NULL REFERENCES public.nodes(id),
  target_id TEXT NOT NULL REFERENCES public.nodes(id),
  edge_type TEXT NOT NULL DEFAULT 'pedagogical_prerequisite',
  weight REAL NOT NULL DEFAULT 1.0
    CHECK (weight BETWEEN 0 AND 1),
  confidence REAL NOT NULL DEFAULT 1.0
    CHECK (confidence BETWEEN 0 AND 1),
  provenance TEXT NOT NULL DEFAULT 'human',
  evidence TEXT,
  graph_version_added INTEGER NOT NULL DEFAULT 1,
  UNIQUE (source_id, target_id, edge_type)
);
```

The `UNIQUE (source_id, target_id, edge_type)` permits multiple edges of different types between the same node pair (a prerequisite edge AND a cross-domain edge between A and B can coexist). Upsert semantics (insert vs ON CONFLICT DO UPDATE) are per-session decisions for Phase 5+; the schema permits both.

The `edge_type` column is intentionally unconstrained at the schema layer per architecture.md:182. Predicate validation lives at PREDICATE_MANIFEST.md/Phase 4 audit.

Edges do NOT directly reference users; they have no learner-state and no cascade requirement. RLS on `edges` mirrors `nodes` (read-allowed for authenticated users; service-role for writes).

**S-0028 corrections.** The pre-S-0028 fragment named (a) `source_id`/`target_id` as `UUID`, (b) the column as `type`, (c) `provenance` and `evidence` as `JSONB`. All three diverge from [`product/docs/architecture.md`](../../product/docs/architecture.md) "Edge Schema" which authors `source_id`/`target_id` as `TEXT REFERENCES nodes(id)` (matching `nodes.id TEXT`), the column as `edge_type`, and `provenance` as `TEXT NOT NULL DEFAULT 'human'` plus `evidence` as `TEXT` (free-text with "may be structured (JSON) later" optionality). The architecture-doc shape is the design source per STATE.md ("translating product/docs/architecture.md ... into live tables"); the gate fragment was updated to match. Recorded in ENGINE_LOG `### Changed`.

### T2-F — `learner_events.session_id` is opaque

`session_id UUID NOT NULL` with no foreign key. No `sessions` table is created at Phase 3. The schema comment names the deferral:

```sql
-- session_id is application-layer opaque; sessions table deferred to Phase 7
-- if session metadata is needed (per phase_3_sql.md T2-F).
```

Phase 7 may introduce a `sessions` table for metadata (started_at, ended_at, device, etc.) at which point a follow-up migration adds the FK. For Phase 3, session identity is recoverable by grouping events on `session_id`.

### T2-G — Migration directory location

`product/seed-graph/migrations/`. Settled in S-0027 Phase C — `git mv` of the existing `supabase/migrations/PREDICATE_MANIFEST.md` and `ROUTING.md` to the new path lands in the same commit; the empty `supabase/` placeholder is removed. ROUTING.md's title is updated to reflect the new path; the graph_version increment contract (T2-D) is added.

The Supabase CLI is configured to read from the new path. The `paideia-dev` project's `supabase/config.toml` (if it exists at repo root) is the configuration surface; the Supabase CLI's `migration_path` option in the project config file points at `product/seed-graph/migrations/`. If `supabase/config.toml` is absent, S-0028 authors a minimal config alongside the first migration.

### T2-H — Rollback test

The build session verifies rollback end-to-end with the following command sequence (run against `paideia-dev` or a test branch):

```bash
# 1. Apply migrations
supabase migration up

# 2. Capture schema state
supabase db dump --schema public > /tmp/post_apply.sql

# 3. Roll back (down migrations or supabase db reset)
supabase db reset

# 4. Re-apply
supabase migration up

# 5. Capture again
supabase db dump --schema public > /tmp/post_reapply.sql

# 6. Diff for stability
diff /tmp/post_apply.sql /tmp/post_reapply.sql
```

A clean rollback produces zero diff. The build session records the verification in `outcome_summary` and includes the diff command output as proof.

## Tier 3 forward pointers

Decisions explicitly deferred. Each entry names the deferral and where it's marked:

- **T3-A — `superseded_by` weight remapping logic.** Per [ADR 0021](../../product/adr/0021-node-deprecation-status-superseded-by.md), node splits transfer mastery weight to replacements. The remapping formula is deferred to Phase 6 mastery recomputation. Phase 3 stores `superseded_by UUID[]` on `nodes`; the Phase 3 migration adds a comment naming the deferral.

- **T3-B — Mastery formula version tracking.** Per [ADR 0024](../../product/adr/0024-engagement-depth-sub-signals-stored-raw.md), engagement-depth weights are application-layer. Phase 3 schema does not version the formula; sub-signals stored raw permit recomputation under any formula. Acceptable; named explicitly so a future session does not add a `mastery_formula_version` column reactively.

- **T3-C — ENGINE_LOG vs Supabase migration version coordination.** Resolved by S-0027 Phase A — [`session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) step 5 gains a one-paragraph note: ENGINE_LOG records session-level filenames; Supabase migration version tracking is separate and automatic.

- **T3-D — Cold-review SQL extension.** Resolved by S-0027 Phase A — [`session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) step 3 cold-review pass widened to cover `product/seed-graph/migrations/**/*.sql`. The S-0028 shutdown will exercise this on the SQL diff.

- **T3-E — Backup tag.** Cut at S-0027 Phase C: `pre-phase-3-v0.0.1` at commit `36b0907` (S-0026 close). Mirrors the `pre-foundation-v0.0.0` pattern. File-level retrieval via `git show pre-phase-3-v0.0.1:<path>` is the legitimate use.

- **T3-F — Health-check cadence proximity.** First cadence audit fires at S-0030 (counter mod 30 == 0). Phase 3 (S-0028), Phase 4 (S-0029), and the start of Phase 5 (S-0030) accumulate before the first audit. S-0027's `outcome_summary` flags this as a forward note. S-0029's shutdown should consider proposing a manual health check at the boundary regardless of cadence trigger.

- **T3-G — `validate_graph()` stub at S-0027 close.** The function returns clean against schema-only DBs. Phase 4 (S-0029 next) fleshes it out per [`build_plan/P_2_graph_validation.md`](../../build_plan/P_2_graph_validation.md). S-0028's shutdown verifies that validate.py runs cleanly post-migration; Phase 4 verifies that validate_graph queries the deployed schema.

## Success criteria for S-0028

Inherited from [`build_plan/P_1_sql_schema.md`](../../build_plan/P_1_sql_schema.md):

- `supabase db push` applies the migrations cleanly to the `paideia-dev` dev DB.
- Rollback works end-to-end per T2-H verification sequence.
- `\d+ public.nodes` shows the expected columns including `confidence_level` with CHECK constraint.
- `\d+ public.learner_events` shows the structured-context columns (`path_id`, `source_text_id`, `session_id`) and the sub-signal CHECK constraint.
- `\d+ public.tension_log` shows the JSONB `exchange_summary` column with shape constraint per TENSION_VOCABULARY.md.
- `engine/tools/validate.py` clean: 0 hard-fails, 0 soft-warns.
- `engine/tools/validate.py --sql-gates --files <migrations>` clean: 0 hard-fails on every authored migration.

Plus session-specific from S-0027:

- Every Tier 2 decision in this report is implemented exactly as documented. The build session does not re-decide.
- The cold-review pass at S-0028 shutdown reports per-file matches against contract blocks; no premise drift surfaced.
- ENGINE_LOG `[Unreleased]` `Added` entries name every migration filename and the table each creates.
- STATE.md `Last build session` row updated for S-0028 close.

## Authored resolution artifacts (in S-0027)

Phase A (universal expression contract):
- [`engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md`](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md)
- [`engine/operations/expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md)
- [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md)
- [`engine/tools/validate.py`](../tools/validate.py) — `validate_sql_gates()` + helpers
- [`engine/tools/test_validate.py`](../tools/test_validate.py) — 18 new tests
- [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) — SQL-gates branch
- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) — cold-review widened to SQL

Phase B (build-readiness gate):
- [`engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md`](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)
- [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md)
- [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) — boot step 5 added
- [`engine/build_readiness/README.md`](README.md)
- [`CLAUDE.md`](../../CLAUDE.md) — Topical pointers

Phase C (this exercise):
- [`product/seed-graph/migrations/TENSION_VOCABULARY.md`](../../product/seed-graph/migrations/TENSION_VOCABULARY.md)
- [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) — graph_version contract amendment
- [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) — moved from `supabase/migrations/`
- [`product/adr/0031-erasure-mechanism-and-individual-only-regime.md`](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) — Consequences pinned to local users mirror
- This file ([`engine/build_readiness/phase_3_sql.md`](phase_3_sql.md))
- Backup tag `pre-phase-3-v0.0.1` at commit `36b0907`

## See also

- [build_plan/P_1_sql_schema.md](../../build_plan/P_1_sql_schema.md) — the chunk being prepared.
- [build_plan/P_2_graph_validation.md](../../build_plan/P_2_graph_validation.md) — the next chunk; Phase 4 fleshes out `validate_graph()`.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the gate protocol this report executes.
- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — the universal expression contract under which Phase 3 SQL discipline operates.
- [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) — cascade discipline; T1-A pinned the cascade FK target shape.
- [ADR 0026](../../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — structural-not-substantive learner storage; T1-C pinned the JSONB vocabulary surface.
- [`migration-discipline.md`](../operations/migration-discipline.md) — Layer 1 contract for SQL migrations the build session honors.
- [`build-readiness-gate.md`](../operations/build-readiness-gate.md) — gate protocol operational doc.
