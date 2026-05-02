-- Migration: 0001_users_mirror
-- Purpose: Create public.users mirror of auth.users plus the trigger
--   functions that keep the mirror synchronized. The mirror is the FK
--   target for every learner-state cascade per ADR 0031 (amended at
--   S-0027). App-schema FKs target public.users(id) with ON DELETE
--   CASCADE; account deletion via auth.users propagates through the
--   DELETE trigger to the mirror, then through declarative cascades to
--   every learner-state row.
-- Loads tables: public.users
-- Loads functions: public.handle_new_auth_user, public.handle_deleted_auth_user
-- Loads triggers: on_auth_user_created, on_auth_user_deleted (both on auth.users)
-- Preconditions:
--   * paideia-dev project at PostgreSQL 17.6.
--   * auth.users provisioned by Supabase Auth.
--   * No prior public.users table (greenfield Phase 3).
-- Postconditions:
--   * public.users exists with (id UUID PK, email TEXT UNIQUE,
--     created_at TIMESTAMPTZ DEFAULT NOW()).
--   * INSERT trigger on auth.users mirrors row creation into public.users
--     (per build_readiness/phase_3_sql.md T1-A).
--   * DELETE trigger on auth.users mirrors row deletion into public.users
--     (closes gate-report T1-A under-specification surfaced at S-0028;
--     without it, ON DELETE CASCADE on learner-state FKs never fires).
--   * RLS enabled with read-only self-select policy. No write policy —
--     all writes denied; trigger functions run SECURITY DEFINER.
-- Invariants:
--   * public.users mirrors auth.users 1:1 by id, kept in sync by triggers.
--   * No application code writes public.users directly; the only writers
--     are the trigger functions.
-- Non-responsibilities:
--   * Does not create downstream learner-state tables; subsequent
--     migrations under product/seed-graph/migrations/ do.
--   * Does not author secondary indexes; query-pattern indexes at Phase 4.
--   * Does not handle auth.users UPDATE — email changes propagate via a
--     follow-up migration if the need surfaces (Phase 7+).
-- Cross-cutting decisions:
--   * Cascade graph: see ADR 0031 (every learner-state FK to users(id)
--     ends in ON DELETE CASCADE; account deletion cascades through to
--     events, snapshots, tension log).
--   * RLS posture: per build_readiness/phase_3_sql.md T1-B (RLS on with
--     v1 policies for every learner-state table; self-select-only for
--     the mirror table).
-- Rollback: DROP TRIGGER + DROP FUNCTION + DROP TABLE in reverse order;
--   verified end-to-end via the Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md, ADR 0031, build_readiness/phase_3_sql.md.

BEGIN;

CREATE TABLE public.users (
  id          UUID         PRIMARY KEY,
  email       TEXT         NOT NULL UNIQUE,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_self_select ON public.users
  FOR SELECT
  USING (id = auth.uid());

CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $func$
BEGIN
  INSERT INTO public.users (id, email, created_at)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.created_at, NOW()))
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$func$;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_auth_user();

CREATE OR REPLACE FUNCTION public.handle_deleted_auth_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $func$
BEGIN
  DELETE FROM public.users WHERE id = OLD.id;
  RETURN OLD;
END;
$func$;

CREATE TRIGGER on_auth_user_deleted
AFTER DELETE ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_deleted_auth_user();

COMMIT;
