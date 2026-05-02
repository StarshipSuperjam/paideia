-- Migration: 0002_nodes
-- Purpose: Create public.nodes table per product/docs/architecture.md "Node
--   Schema" (concept-level graph nodes). nodes carry no learner state and
--   no FK to users; they are graph metadata authored by Phase 5 seed
--   sessions and read by every downstream phase.
-- Loads tables: public.nodes
-- Preconditions:
--   * No prior public.nodes table (greenfield Phase 3).
--   * 0001_users_mirror.sql is not a precondition — nodes have no FK to
--     users.
-- Postconditions:
--   * public.nodes exists with all columns from architecture.md "Node
--     Schema": id TEXT PK (slugified human-readable concept name per
--     architecture.md:124, e.g. transcendental_idealism), label,
--     domain[], summary, teaching_notes, aliases[],
--     rigor_score_computed, rigor_score_adjustment, provenance,
--     confidence, confidence_level (per ADR 0030), status (per ADR
--     0021), superseded_by[], graph_version_added, timestamps.
--   * confidence_level CHECK enforces ADR 0030 enum (EXTRACTED,
--     INTERPRETED, SYNTHETIC) per build_readiness/phase_3_sql.md T2-A.
--   * status CHECK enforces 3-value enum (active, deprecated,
--     superseded) per phase_3_sql.md T2-A. The architecture.md
--     two-value declaration ('active' | 'deprecated') is a
--     pre-supersession-explicit framing; the gate-report expansion
--     splits deprecated-with-replacement into 'superseded' for finer
--     traversal discrimination. Recorded in outcome_summary.
--   * RLS enabled with read-allowed-to-authenticated policy. Writes
--     are service-role-only (Phase 5 seed sessions, Phase 6 batch
--     reviews); no learner-facing write policy.
-- Invariants:
--   * id is human-readable slugified TEXT, immutable post-creation.
--   * Adjustments to rigor_score_adjustment do not propagate; the
--     formula always reads rigor_score_computed (per architecture.md
--     "Two-Column Override Model").
--   * Deprecated/superseded nodes remain in the table because learner
--     events reference them by ID.
-- Non-responsibilities:
--   * Does not seed any node rows; Phase 5 subdomain sessions populate.
--   * Does not author secondary indexes (label search, domain
--     filtering); query-pattern indexes at Phase 4.
--   * Does not enforce a CHECK on edge_type (column lives on edges,
--     not nodes; intentionally unconstrained at the schema layer per
--     architecture.md:182 + phase_3_sql.md T2-A exemption).
-- Cross-cutting decisions:
--   * id type: TEXT, not UUID. architecture.md:103 + 124 commit to
--     slugified human-readable IDs; corrects the gate report's
--     T2-C/T2-E implicit UUID assumption (resolved at S-0028 boot,
--     recorded in ENGINE_LOG ### Changed).
--   * confidence_level enum: see ADR 0030.
--   * status enum: 3 values per phase_3_sql.md T2-A.
--   * RLS posture: see phase_3_sql.md T1-B.
-- Rollback: DROP TABLE public.nodes CASCADE. The CASCADE removes any
--   downstream FK references; verified end-to-end via the Supabase
--   branch rollback test in S-0028.
-- See also: build_plan/P_1_sql_schema.md, product/docs/architecture.md,
--   ADR 0019, ADR 0020, ADR 0021, ADR 0030, build_readiness/phase_3_sql.md.

BEGIN;

CREATE TABLE public.nodes (
  id                      TEXT         PRIMARY KEY,
  label                   TEXT         NOT NULL,
  domain                  TEXT[]       NOT NULL,
  summary                 TEXT         NOT NULL,
  teaching_notes          TEXT,
  aliases                 TEXT[]       NOT NULL DEFAULT '{}',
  rigor_score_computed    REAL         NOT NULL DEFAULT 0.5,
  rigor_score_adjustment  REAL         NOT NULL DEFAULT 0.0,
  provenance              TEXT         NOT NULL DEFAULT 'human',
  confidence              REAL         NOT NULL DEFAULT 1.0,
  confidence_level        TEXT         NOT NULL DEFAULT 'INTERPRETED'
    CHECK (confidence_level IN ('EXTRACTED', 'INTERPRETED', 'SYNTHETIC')),
  status                  TEXT         NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'deprecated', 'superseded')),
  superseded_by           TEXT[]       NOT NULL DEFAULT '{}',
  graph_version_added     INTEGER      NOT NULL DEFAULT 1,
  created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

ALTER TABLE public.nodes ENABLE ROW LEVEL SECURITY;

CREATE POLICY nodes_authenticated_read ON public.nodes
  FOR SELECT
  TO authenticated
  USING (true);

COMMIT;
