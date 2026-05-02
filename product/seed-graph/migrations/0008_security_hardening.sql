-- Migration: 0008_security_hardening
-- Purpose: Address Supabase security-advisor findings surfaced post-apply
--   in S-0028 against the functions authored by 0001_users_mirror.sql
--   and 0007_tension_log.sql:
--     (a) tension_log_exchange_summary_valid_v1 has mutable search_path
--         (advisor 0011_function_search_path_mutable).
--     (b) handle_new_auth_user is callable via PostgREST RPC by anon
--         and authenticated roles (advisors 0028 + 0029).
--     (c) handle_deleted_auth_user same shape as (b).
-- Loads tables: (none — alters existing functions and revokes grants)
-- Preconditions:
--   * 0001_users_mirror.sql + 0007_tension_log.sql applied; the three
--     functions exist.
-- Postconditions:
--   * tension_log_exchange_summary_valid_v1 has SET search_path =
--     pg_catalog, public — pinned, advisor 0011 cleared.
--   * EXECUTE on public.handle_new_auth_user() revoked from PUBLIC,
--     anon, authenticated — advisors 0028 + 0029 cleared. The function
--     remains callable via the trigger system (triggers fire as the
--     function owner regardless of EXECUTE grants).
--   * EXECUTE on public.handle_deleted_auth_user() revoked likewise.
-- Invariants:
--   * The two trigger functions continue to fire on auth.users
--     INSERT/DELETE. EXECUTE revocation only blocks PostgREST
--     /rest/v1/rpc/* exposure, not trigger invocation.
-- Non-responsibilities:
--   * Does not address advisor findings on rls_auto_enable — that
--     function is Supabase-internal, not authored by this project.
--   * Does not move the trigger functions to a private schema; the
--     REVOKE-EXECUTE approach is the lighter intervention. If
--     SECURITY DEFINER hardening proves insufficient, schema relocation
--     is the follow-up posture (likely Phase 7+ when application code
--     against the schema surfaces).
-- Cross-cutting decisions:
--   * Public-schema SECURITY DEFINER functions are PostgREST-exposed
--     by default; REVOKE EXECUTE from anon/authenticated is the
--     standard Supabase hardening pattern.
-- Rollback: GRANT EXECUTE on the two trigger functions back to PUBLIC
--   (or the prior grantees); ALTER FUNCTION ... RESET search_path on
--   the validation function. Verified end-to-end via the Supabase
--   branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md,
--   https://supabase.com/docs/guides/database/database-linter
--   advisors 0011, 0028, 0029.

BEGIN;

ALTER FUNCTION public.tension_log_exchange_summary_valid_v1(jsonb)
  SET search_path = pg_catalog, public;

REVOKE EXECUTE ON FUNCTION public.handle_new_auth_user() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.handle_new_auth_user() FROM anon;
REVOKE EXECUTE ON FUNCTION public.handle_new_auth_user() FROM authenticated;

REVOKE EXECUTE ON FUNCTION public.handle_deleted_auth_user() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.handle_deleted_auth_user() FROM anon;
REVOKE EXECUTE ON FUNCTION public.handle_deleted_auth_user() FROM authenticated;

COMMIT;
