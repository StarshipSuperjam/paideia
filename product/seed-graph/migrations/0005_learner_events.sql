-- Migration: 0005_learner_events
-- Purpose: Create public.learner_events table per ADR 0015 (event-sourced
--   learner model), ADR 0024 (sub-signals stored raw), and ADR 0026
--   (structured-context columns, no free-text grab-bags). Events are
--   the source of truth for the learner model; mastery snapshots are
--   derived per ADR 0023.
-- Loads tables: public.learner_events
-- Preconditions:
--   * public.users exists (depends on 0001_users_mirror.sql).
--   * public.nodes exists (depends on 0002_nodes.sql).
-- Postconditions:
--   * public.learner_events exists with columns per learner-model.md
--     "Event-Sourced Architecture" + ADR 0024 sub-signals + ADR 0026
--     structured context (path_id, source_text_id, session_id —
--     cohort_id removed per ADR 0031 amendment).
--   * FK learner_events.user_id REFERENCES public.users(id) ON DELETE
--     CASCADE per ADR 0031.
--   * FK learner_events.concept_id REFERENCES public.nodes(id) — no
--     cascade per ADR 0021 (deprecated/superseded nodes are retained
--     because events reference them).
--   * interaction_type CHECK enforces ADR 0024's six-value enum per
--     build_readiness/phase_3_sql.md T2-A.
--   * Table-level CHECK sub_signals_range_or_null enforces sub-signal
--     [0, 1] range when interaction_type is composite-applicable, or
--     allows any value (including NULL) when type is
--     backward_inference / incidental_mention per gate T2-B.
--   * RLS enabled with v1 user-isolation policy (user_id = auth.uid()).
-- Invariants:
--   * Append-only event log; no UPDATE or DELETE in normal operation
--     (only cascade deletion via account erasure).
--   * Sub-signals (generative_ratio, scaffolding_distance, novelty)
--     stored raw per ADR 0024; engagement_depth composite is computed
--     application-side, not stored on events.
--   * cohort_id is intentionally absent per ADR 0031 (institutional
--     regime foreclosed; reopening requires superseding ADR).
--   * session_id is opaque per gate T2-F — no FK; sessions table
--     deferred to Phase 7 if needed.
-- Non-responsibilities:
--   * Does not author secondary indexes (user_id, concept_id, etc.);
--     query-pattern indexes at Phase 4.
--   * Does not enforce non-NULL sub-signals for composite-applicable
--     types — the gate-report T2-B CHECK as written is permissive on
--     NULL for non-bypass types (PostgreSQL CHECK treats NULL as
--     TRUE). The strict intent ("NULL on composite-type events is a
--     data error" per learner-model.md:60) is enforced at the
--     application layer. Recorded as drift in outcome_summary.
-- Cross-cutting decisions:
--   * Cascade discipline: see ADR 0031 (FK to users(id) ends in ON
--     DELETE CASCADE).
--   * Structured-context discipline: see ADR 0026 (no JSONB grab-bag).
--   * Sub-signals stored raw: see ADR 0024.
--   * Auth model (local users mirror): see ADR 0031 amendment +
--     0001_users_mirror.sql.
-- Rollback: DROP TABLE public.learner_events. Verified end-to-end via
--   the Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md, product/docs/learner-model.md,
--   ADR 0015, ADR 0023, ADR 0024, ADR 0026, ADR 0031,
--   build_readiness/phase_3_sql.md T2-A, T2-B, T2-F.

BEGIN;

CREATE TABLE public.learner_events (
  id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID         NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  concept_id            TEXT         NOT NULL REFERENCES public.nodes(id),
  interaction_type      TEXT         NOT NULL
    CHECK (interaction_type IN (
      'direct_teaching', 'assessment', 'callback_reference',
      'incidental_mention', 'cross_domain_connection', 'backward_inference'
    )),
  generative_ratio      NUMERIC      NULL,
  scaffolding_distance  NUMERIC      NULL,
  novelty               NUMERIC      NULL,
  path_id               UUID         NULL,
  source_text_id        UUID         NULL,
  session_id            UUID         NOT NULL,
  graph_version_added   INTEGER      NOT NULL,
  created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  CONSTRAINT sub_signals_range_or_null CHECK (
    (interaction_type IN ('backward_inference', 'incidental_mention'))
    OR (
      generative_ratio BETWEEN 0 AND 1
      AND scaffolding_distance BETWEEN 0 AND 1
      AND novelty BETWEEN 0 AND 1
    )
  )
);

ALTER TABLE public.learner_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY learner_events_user_isolation ON public.learner_events
  USING (user_id = auth.uid());

COMMIT;
