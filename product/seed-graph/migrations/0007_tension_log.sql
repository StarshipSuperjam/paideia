-- Migration: 0007_tension_log
-- Purpose: Create public.tension_log table per product/docs/self-correction.md
--   "Tension Log Schema" + ADR 0026 (structured-context discipline,
--   exchange_summary JSONB-with-named-fields). Sonnet teaching sessions
--   write tension records; Opus batch reviews consume them.
-- Loads tables: public.tension_log
-- Loads functions: public.tension_log_exchange_summary_valid_v1(jsonb)
-- Preconditions:
--   * public.users exists (depends on 0001_users_mirror.sql).
--   * public.nodes exists (depends on 0002_nodes.sql).
-- Postconditions:
--   * public.tension_log_exchange_summary_valid_v1 IMMUTABLE function
--     exists, validating exchange_summary JSONB against v1 vocabularies
--     in product/seed-graph/migrations/TENSION_VOCABULARY.md.
--   * public.tension_log exists with columns per self-correction.md
--     plus user_id (added per ADR 0031 cascade discipline; not in
--     self-correction.md schema but mandated by the cascade graph).
--   * tension_type CHECK enforces 5-value enum per phase_3_sql.md T2-A.
--   * exchange_summary CHECK invokes the v1 validation function.
--   * FK user_id REFERENCES public.users(id) ON DELETE CASCADE per
--     ADR 0031.
--   * FKs concept_id and learner_reference_node_id REFERENCE
--     public.nodes(id) — no cascade per ADR 0021.
--   * RLS enabled with user-isolation policy (user_id = auth.uid()).
-- Invariants:
--   * exchange_summary JSONB shape conforms to v1 vocabularies in
--     TENSION_VOCABULARY.md: teaching_moves_tried (array of v1 enum),
--     friction_type (v1 enum), pattern_observed (string ≤ 600 chars),
--     suggested_review_focus (null or v1 enum).
--   * Append-only log; tension records are evidence inputs to the
--     Phase 6 Opus batch review.
-- Non-responsibilities:
--   * Does not enforce the cross-column "spontaneous_connection
--     requires unresolved_reference XOR learner_reference_node_id"
--     condition; application-layer per self-correction.md "Teaching
--     Session Context".
--   * Does not enforce pattern_observed substantive-content policy
--     (third-person, no first-person learner claims, etc.); ADR 0026
--     Consequences names a future validate.py soft-warn category for
--     this. Authoring discipline is the primary enforcement.
--   * Does not author secondary indexes; query-pattern indexes at
--     Phase 4.
-- Cross-cutting decisions:
--   * Cascade discipline: see ADR 0031.
--   * Structured shape vs free-text: see ADR 0026.
--   * v1 vocabularies: see TENSION_VOCABULARY.md (authored at S-0027
--     gate exercise).
--   * concept_id / learner_reference_node_id type: TEXT, matching
--     nodes.id (architecture.md authoritative).
--   * user_id presence: ADR 0031 Consequences (line 35) names
--     tension_log among the cascade-target tables; self-correction.md
--     does not include it. The migration adds user_id per ADR 0031.
--     Recorded as drift in outcome_summary.
-- Rollback: DROP TABLE public.tension_log CASCADE; DROP FUNCTION
--   public.tension_log_exchange_summary_valid_v1(jsonb). Verified
--   end-to-end via the Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md,
--   product/docs/self-correction.md, ADR 0026, ADR 0031,
--   product/seed-graph/migrations/TENSION_VOCABULARY.md,
--   build_readiness/phase_3_sql.md T1-C, T2-A.

BEGIN;

CREATE OR REPLACE FUNCTION public.tension_log_exchange_summary_valid_v1(s jsonb)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $func$
BEGIN
  IF s IS NULL OR jsonb_typeof(s) <> 'object' THEN
    RETURN FALSE;
  END IF;

  IF jsonb_typeof(s->'teaching_moves_tried') <> 'array' THEN
    RETURN FALSE;
  END IF;
  IF EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(s->'teaching_moves_tried') v
    WHERE v NOT IN (
      'direct_explanation', 'concrete_example', 'analogy', 'decomposition',
      'prerequisite_check', 'restatement', 'socratic_question',
      'contrast_pair', 'redirect_to_source', 'pause_and_reframe'
    )
  ) THEN
    RETURN FALSE;
  END IF;

  IF (s->>'friction_type') NOT IN (
    'prerequisite_gap', 'formula_vs_grounding', 'source_register_mismatch',
    'terminology_drift', 'aliasing_confusion', 'cross_domain_transfer_block',
    'cognitive_overload', 'motivation_gap', 'false_mastery', 'unexpected_ease'
  ) THEN
    RETURN FALSE;
  END IF;

  IF jsonb_typeof(s->'pattern_observed') <> 'string' THEN
    RETURN FALSE;
  END IF;
  IF length(s->>'pattern_observed') > 600 THEN
    RETURN FALSE;
  END IF;

  IF (s ? 'suggested_review_focus')
     AND (s->>'suggested_review_focus') IS NOT NULL
     AND (s->>'suggested_review_focus') NOT IN (
       'prerequisite_node', 'current_node', 'parent_concept',
       'cross_domain_link', 'source_alternative', 'synthetic_node_review',
       'skip_for_now'
     ) THEN
    RETURN FALSE;
  END IF;

  RETURN TRUE;
END;
$func$;

CREATE TABLE public.tension_log (
  id                         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                    UUID         NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  concept_id                 TEXT         NOT NULL REFERENCES public.nodes(id),
  session_id                 UUID         NOT NULL,
  tension_type               TEXT         NOT NULL
    CHECK (tension_type IN (
      'struggle_unresolved', 'unexpected_ease', 'spontaneous_connection',
      'source_ineffective', 'mastery_contradiction'
    )),
  exchange_summary           JSONB        NOT NULL
    CHECK (public.tension_log_exchange_summary_valid_v1(exchange_summary)),
  learner_reference_node_id  TEXT         NULL REFERENCES public.nodes(id),
  created_at                 TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

ALTER TABLE public.tension_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY tension_log_user_isolation ON public.tension_log
  USING (user_id = auth.uid());

COMMIT;
