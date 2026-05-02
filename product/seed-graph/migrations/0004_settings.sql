-- Migration: 0004_settings
-- Purpose: Create public.settings singleton key/value store and seed
--   graph_version=1 per build_readiness/phase_3_sql.md T2-D. The
--   graph_version counter is the central piece of state Phase 5 seed
--   sessions read-modify-write per the increment contract in
--   product/seed-graph/migrations/ROUTING.md.
-- Loads tables: public.settings
-- Loads seed rows: ('graph_version', '1'::JSONB)
-- Preconditions:
--   * No prior public.settings table.
-- Postconditions:
--   * public.settings exists with (key TEXT PK, value JSONB NOT NULL).
--   * Row ('graph_version', 1::JSONB) inserted.
--   * RLS enabled with service-role-only policy. No learner-facing
--     read or write — settings is server-managed.
-- Invariants:
--   * graph_version is a monotonically non-decreasing INTEGER stored as
--     JSONB number. Phase 5 seed sessions increment it per the
--     ROUTING.md contract.
-- Non-responsibilities:
--   * Does not seed other settings keys; future settings land in
--     follow-up migrations.
--   * Does not author the increment trigger or function; the contract
--     in ROUTING.md is application-layer.
-- Cross-cutting decisions:
--   * Service-role-only RLS policy: settings is operational state, not
--     learner-visible. No PostgREST surface for authenticated users.
-- Rollback: DROP TABLE public.settings. Verified end-to-end via the
--   Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md,
--   product/seed-graph/migrations/ROUTING.md "graph_version increment
--   contract", build_readiness/phase_3_sql.md T2-D.

BEGIN;

CREATE TABLE public.settings (
  key    TEXT   PRIMARY KEY,
  value  JSONB  NOT NULL
);

INSERT INTO public.settings (key, value)
VALUES ('graph_version', '1'::JSONB);

ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY settings_service_role_only ON public.settings
  USING (auth.jwt()->>'role' = 'service_role');

COMMIT;
