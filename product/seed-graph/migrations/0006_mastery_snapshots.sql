-- Migration: 0006_mastery_snapshots
-- Purpose: Create public.mastery_snapshots table per ADR 0023
--   (engagement-depth aggregation), ADR 0024 (sub-signals stored raw),
--   ADR 0025 (historical maximum tracking) and
--   build_readiness/phase_3_sql.md T2-C. Snapshots cache the latest
--   per-user-per-concept mastery state derived from the event log.
-- Loads tables: public.mastery_snapshots
-- Loads indexes: mastery_snapshots_user_id_idx, mastery_snapshots_concept_id_idx
-- Preconditions:
--   * public.users exists (depends on 0001_users_mirror.sql).
--   * public.nodes exists (depends on 0002_nodes.sql).
-- Postconditions:
--   * public.mastery_snapshots exists with composite PK (user_id,
--     concept_id), columns mastery_score, max_historical_score
--     (DEFAULT 0; per ADR 0025), engagement_depth NULL, computed_at
--     TIMESTAMPTZ DEFAULT NOW().
--   * FK user_id REFERENCES public.users(id) ON DELETE CASCADE per
--     ADR 0031.
--   * FK concept_id REFERENCES public.nodes(id) — no cascade per
--     ADR 0021.
--   * Two secondary indexes on user_id and concept_id for query
--     patterns (per gate T2-C).
--   * RLS enabled with user-isolation policy.
-- Invariants:
--   * One row per (user_id, concept_id) pair (composite PK).
--   * max_historical_score is monotonically non-decreasing under
--     event ingest (per ADR 0025 closed-form incremental update).
--   * Snapshots are mutable cache; computed_at records last refresh.
-- Non-responsibilities:
--   * Does not implement the recomputation logic (Phase 6).
--   * Does not version the mastery formula; sub-signals stored raw
--     permit recomputation under any formula (per ADR 0024).
--   * Does not author additional indexes beyond the two named in
--     gate T2-C.
-- Cross-cutting decisions:
--   * Cascade discipline: see ADR 0031.
--   * concept_id type: TEXT, matching nodes.id (architecture.md
--     authoritative).
--   * Historical maximum tracking: see ADR 0025; max_historical_score
--     DEFAULT 0 to allow first-event population without a separate
--     INSERT path.
-- Rollback: DROP TABLE public.mastery_snapshots. Verified end-to-end
--   via the Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md, product/docs/learner-model.md,
--   ADR 0023, ADR 0024, ADR 0025, ADR 0031,
--   build_readiness/phase_3_sql.md T2-C.

BEGIN;

CREATE TABLE public.mastery_snapshots (
  user_id               UUID         NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  concept_id            TEXT         NOT NULL REFERENCES public.nodes(id),
  mastery_score         NUMERIC      NOT NULL,
  max_historical_score  NUMERIC      NOT NULL DEFAULT 0,
  engagement_depth      NUMERIC      NULL,
  computed_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, concept_id)
);

CREATE INDEX mastery_snapshots_user_id_idx ON public.mastery_snapshots (user_id);
CREATE INDEX mastery_snapshots_concept_id_idx ON public.mastery_snapshots (concept_id);

ALTER TABLE public.mastery_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY mastery_snapshots_user_isolation ON public.mastery_snapshots
  USING (user_id = auth.uid());

COMMIT;
