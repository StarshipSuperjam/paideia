-- Migration: 0003_edges
-- Purpose: Create public.edges table per product/docs/architecture.md
--   "Edge Schema". Edges carry pedagogical-prerequisite relationships
--   (and other types as needed) between concept nodes. Like nodes, edges
--   carry no learner state and no FK to users.
-- Loads tables: public.edges
-- Preconditions:
--   * public.nodes exists (depends on 0002_nodes.sql).
-- Postconditions:
--   * public.edges exists with all columns from architecture.md "Edge
--     Schema": id UUID PK (gen_random_uuid default), source_id and
--     target_id TEXT REFERENCES public.nodes(id), edge_type, weight,
--     provenance, confidence, evidence, graph_version_added,
--     timestamps. UNIQUE (source_id, target_id, edge_type) enforced.
--   * weight CHECK (weight BETWEEN 0 AND 1) per architecture.md
--     interval; confidence likewise.
--   * RLS enabled with read-allowed-to-authenticated policy. Writes
--     are service-role-only (Phase 5 seed sessions).
-- Invariants:
--   * Multiple edge types between the same node pair coexist (a
--     pedagogical_prerequisite edge AND a historical_influence edge
--     between A and B), enforced via UNIQUE (source_id, target_id,
--     edge_type).
--   * edge_type is intentionally unconstrained at the schema layer per
--     architecture.md:182 — additivity over enum-strictness; predicate
--     validation lives at PREDICATE_MANIFEST.md and the Phase 4 audit.
-- Non-responsibilities:
--   * Does not enforce CHECK on edge_type (intentional per
--     architecture.md:182 + phase_3_sql.md T2-A exemption).
--   * Does not seed any edge rows; Phase 5 subdomain sessions populate.
--   * Does not author secondary indexes beyond the UNIQUE (which
--     creates an index on the triple); query-pattern indexes at Phase 4.
-- Cross-cutting decisions:
--   * source_id and target_id type: TEXT, matching nodes.id (per the
--     architecture.md-authoritative resolution at S-0028 boot).
--   * provenance and evidence types: TEXT, per architecture.md:163,165.
--     The gate report T2-E declares JSONB; architecture.md authority
--     applies here as it does for the id-type drift. Recorded in
--     outcome_summary.
--   * weight and confidence type: REAL, per architecture.md:162,164.
--   * RLS posture: see phase_3_sql.md T1-B.
-- Rollback: DROP TABLE public.edges. Verified end-to-end via the
--   Supabase branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md, product/docs/architecture.md,
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md,
--   build_readiness/phase_3_sql.md T2-E.

BEGIN;

CREATE TABLE public.edges (
  id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id            TEXT         NOT NULL REFERENCES public.nodes(id),
  target_id            TEXT         NOT NULL REFERENCES public.nodes(id),
  edge_type            TEXT         NOT NULL DEFAULT 'pedagogical_prerequisite',
  weight               REAL         NOT NULL DEFAULT 1.0
    CHECK (weight BETWEEN 0 AND 1),
  provenance           TEXT         NOT NULL DEFAULT 'human',
  confidence           REAL         NOT NULL DEFAULT 1.0
    CHECK (confidence BETWEEN 0 AND 1),
  evidence             TEXT,
  graph_version_added  INTEGER      NOT NULL DEFAULT 1,
  created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  UNIQUE (source_id, target_id, edge_type)
);

ALTER TABLE public.edges ENABLE ROW LEVEL SECURITY;

CREATE POLICY edges_authenticated_read ON public.edges
  FOR SELECT
  TO authenticated
  USING (true);

COMMIT;
