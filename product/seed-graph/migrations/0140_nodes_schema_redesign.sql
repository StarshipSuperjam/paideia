-- Migration: 0140_nodes_schema_redesign
-- Purpose: Tier-A Cluster 4 — Node schema redesign per
--   product/adr/0102-tier-a-cluster-4-node-schema-redesign.md.
--   Third Tier-A cluster-implementation migration per
--   product/adr/0094-phase-6-scope.md dependency order
--   C1 → C2 → C4 → C3 → C5. Adds 14 new columns to public.nodes
--   per synthesis.md §Cluster 4 (lines 141-176): node_type TEXT[]
--   with 10-value element CHECK; disciplinary_domain TEXT;
--   granularity TEXT with 3-value CHECK; audience_tags TEXT[];
--   5 JSONB columns (canonical_sources, approved_examples,
--   misconceptions, assessment_items, mastery_evidence);
--   accessibility_notes TEXT; assumed_background TEXT[];
--   jargon_load TEXT with 3-value CHECK; cultural_specificity TEXT;
--   tradition_label TEXT[] open vocabulary. Schema-only landing per
--   ADR 0102 Adjudication 1: all 380 rows carry column defaults
--   post-migration; per-domain node_type backfill defers to Cluster 4
--   sequel sessions (likely 4-6 sessions, one per subdomain,
--   claiming migration slots 0141-0149). The 380-row count is
--   invariant — pure schema additions; no INSERT/DELETE/UPDATE of
--   node rows. Re-verifies ADR 0094 T1-A + ADR 0095 T1-A at landing
--   (third re-verification — Tier-A continues to be implementable
--   in Postgres+JSONB without re-decomposition).
-- Loads tables: public.nodes (14 ADD COLUMN statements; 4 ADD
--   CONSTRAINT statements; no INSERT/UPDATE/DELETE; no DROP).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes exists with the 17
--     columns from 0002_nodes.sql (id, label, domain, summary,
--     teaching_notes, aliases, rigor_score_computed,
--     rigor_score_adjustment, provenance, confidence,
--     confidence_level, status, superseded_by, graph_version_added,
--     created_at, updated_at).
--   * public.nodes carries exactly 380 rows (verified via
--     mcp__supabase__execute_sql at S-0213 boot — see
--     product/adr/0102-tier-a-cluster-4-node-schema-redesign.md
--     Context).
--   * No prior migrations in the 0140-0149 prefix range — this is
--     the first claim within the Cluster 4 sub-range (per
--     ROUTING.md S-0207 / S-0208 narrative entries' forward-flagged
--     sub-range scheme).
--   * Cluster 1 (migration 0120) and Cluster 2 (migration 0130)
--     have been applied — but this migration is layer-orthogonal to
--     both (Cluster 1 + 2 act on public.edges; this migration acts
--     on public.nodes). The preconditions hold regardless of
--     0120/0130 application order.
--   * settings.graph_version unchanged at session boot (post-S-0123;
--     unchanged by this migration because no node/edge rows are
--     inserted/deleted per the ROUTING.md graph_version increment
--     contract — schema additions do not advance the counter).
-- Postconditions:
--   * public.nodes gains 14 new columns:
--     1. node_type TEXT[] NOT NULL DEFAULT '{unclassified}'
--     2. disciplinary_domain TEXT (nullable)
--     3. granularity TEXT (nullable)
--     4. audience_tags TEXT[] NOT NULL DEFAULT '{}'
--     5. canonical_sources JSONB NOT NULL DEFAULT '[]'::jsonb
--     6. approved_examples JSONB NOT NULL DEFAULT '[]'::jsonb
--     7. misconceptions JSONB NOT NULL DEFAULT '[]'::jsonb
--     8. assessment_items JSONB NOT NULL DEFAULT '[]'::jsonb
--     9. mastery_evidence JSONB NOT NULL DEFAULT '[]'::jsonb
--     10. accessibility_notes TEXT (nullable)
--     11. assumed_background TEXT[] NOT NULL DEFAULT '{}'
--     12. jargon_load TEXT (nullable)
--     13. cultural_specificity TEXT (nullable)
--     14. tradition_label TEXT[] NOT NULL DEFAULT '{}'
--   * public.nodes gains 4 CHECK constraints:
--     - nodes_node_type_valid: every element of node_type is in the
--       10-value enum (threshold_concept, bridge_concept,
--       disciplinary_practice, text_excerpt, historical_context,
--       misconception, comparative_lens, assessment_task, subfield,
--       unclassified) — enforced via `node_type <@ ARRAY[...]`.
--     - nodes_node_type_nonempty: array_length(node_type, 1) >= 1
--       (no empty-array node_type values).
--     - nodes_granularity_valid: granularity IN ('coarse', 'medium',
--       'fine') OR granularity IS NULL.
--     - nodes_jargon_load_valid: jargon_load IN ('low', 'medium',
--       'high') OR jargon_load IS NULL.
--   * All 380 existing rows carry the column defaults:
--     - node_type = '{unclassified}' (the transitional default;
--       per-domain backfill sequel sessions retype to substantive
--       values).
--     - disciplinary_domain = NULL
--     - granularity = NULL
--     - audience_tags = '{}'
--     - canonical_sources = '[]'::jsonb
--     - approved_examples = '[]'::jsonb
--     - misconceptions = '[]'::jsonb
--     - assessment_items = '[]'::jsonb
--     - mastery_evidence = '[]'::jsonb
--     - accessibility_notes = NULL
--     - assumed_background = '{}'
--     - jargon_load = NULL
--     - cultural_specificity = NULL
--     - tradition_label = '{}'
--   * public.nodes row count = 380 (invariant — pure schema).
--   * PRIMARY KEY (id) preserved.
--   * RLS policy nodes_authenticated_read preserved.
--   * All 17 pre-existing columns (id, label, domain, summary,
--     teaching_notes, aliases, rigor_score_computed,
--     rigor_score_adjustment, provenance, confidence,
--     confidence_level, status, superseded_by, graph_version_added,
--     created_at, updated_at) unchanged in shape and value.
--   * Cluster 1 + 2 columns on public.edges (expert_confidence,
--     trace_confidence, llm_confidence, disagreement_flag,
--     counterexamples, version, review_status, last_reviewed,
--     provenance JSONB, edge_layer, edge_type CHECK constraints)
--     unchanged — this migration is layer-orthogonal to edges.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. Verifies (a) 14 new columns exist
--   with expected presence; (b) 4 new CHECK constraints exist;
--   (c) row count invariance (380); (d) defaults applied uniformly
--   to all 380 rows.)
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'node_type' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'disciplinary_domain' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'granularity' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'audience_tags' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'canonical_sources' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'approved_examples' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'misconceptions' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'assessment_items' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'mastery_evidence' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'accessibility_notes' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'assumed_background' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'jargon_load' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'cultural_specificity' :: 1
--   SELECT count(*)::int FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nodes' AND column_name = 'tradition_label' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_node_type_valid' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_node_type_nonempty' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_granularity_valid' :: 1
--   SELECT count(*)::int FROM information_schema.table_constraints WHERE table_schema = 'public' AND table_name = 'nodes' AND constraint_name = 'nodes_jargon_load_valid' :: 1
--   SELECT count(*)::int FROM public.nodes :: 380
--   SELECT count(*)::int FROM public.nodes WHERE node_type = ARRAY['unclassified']::text[] :: 380
--   SELECT count(*)::int FROM public.nodes WHERE audience_tags = '{}'::text[] :: 380
--   SELECT count(*)::int FROM public.nodes WHERE assumed_background = '{}'::text[] :: 380
--   SELECT count(*)::int FROM public.nodes WHERE tradition_label = '{}'::text[] :: 380
--   SELECT count(*)::int FROM public.nodes WHERE canonical_sources = '[]'::jsonb :: 380
--   SELECT count(*)::int FROM public.nodes WHERE approved_examples = '[]'::jsonb :: 380
--   SELECT count(*)::int FROM public.nodes WHERE misconceptions = '[]'::jsonb :: 380
--   SELECT count(*)::int FROM public.nodes WHERE assessment_items = '[]'::jsonb :: 380
--   SELECT count(*)::int FROM public.nodes WHERE mastery_evidence = '[]'::jsonb :: 380
--   SELECT count(*)::int FROM public.nodes WHERE disciplinary_domain IS NULL :: 380
--   SELECT count(*)::int FROM public.nodes WHERE granularity IS NULL :: 380
--   SELECT count(*)::int FROM public.nodes WHERE jargon_load IS NULL :: 380
--   SELECT count(*)::int FROM public.nodes WHERE cultural_specificity IS NULL :: 380
--   SELECT count(*)::int FROM public.nodes WHERE accessibility_notes IS NULL :: 380
-- Invariants:
--   * Row count on public.nodes is preserved (380 before; 380 after).
--     Pure schema additions — no INSERT/DELETE/UPDATE of nodes.
--   * PRIMARY KEY (id) preserved.
--   * RLS policy nodes_authenticated_read preserved.
--   * All 17 pre-existing columns unchanged in shape and value.
--   * settings.graph_version unchanged (no row counter advance per
--     ROUTING.md graph_version increment contract).
--   * Cluster 1 + 2 columns and constraints on public.edges unchanged
--     (this migration is layer-orthogonal to edges).
-- Non-responsibilities:
--   * Does NOT backfill per-node node_type values. Per ADR 0102
--     Adjudication 1, schema-only landing this session; per-domain
--     classification defers to Cluster 4 sequel sessions claiming
--     migration slots 0141-0149.
--   * Does NOT backfill any of the other 13 new columns. All carry
--     column defaults; sequel sessions populate per-domain.
--   * Does NOT amend ADR 0008 (concept-nodes-not-thinkers). Per
--     ADR 0102 Adjudication 3, the strict read on historical_context
--     is preserved — movement-shaped entities route via
--     tradition_label, not via node_type=['historical_context'].
--   * Does NOT rename bridge_concept to boundary_concept. Per ADR 0102
--     Adjudication 4, bridge_concept retained as synthesis-paper
--     coinage with provenance note; rename deferred via D8
--     open-for-revision posture.
--   * Does NOT implement the validator soft-warns
--     (node_type_unclassified, node_threshold_concept_lacks_assessment_items,
--     node_lacks_cultural_specificity). Implementation lands in a
--     follow-up commit to engine/tools/validate.py within the same
--     session per `feedback_no_pilot_wait_and_see.md` discipline.
--   * Does NOT touch public.edges (Cluster 2's domain) or any other
--     existing table. Strict additive scope.
--   * Does NOT create new tables (e.g., public.assessments for
--     assessment_items FK). Per ADR 0102 Adjudication 8, JSONB array
--     is forward-compatible; FK extraction defers to a future Phase
--     7+ cluster when assessment authoring becomes load-bearing.
-- Cross-cutting decisions:
--   * Schema-only landing per ADR 0102 Adjudication 1 — `'unclassified'`
--     transitional default on node_type; the structural validator
--     `node_type_unclassified` (severity mode-switched at module-level
--     constant in validate.py) tracks the transition window. The
--     LAST per-domain backfill sequel session escalates the warn to
--     hard-fail AND drops 'unclassified' from the enum via a small
--     follow-up migration.
--   * node_type as TEXT[] per ADR 0102 Adjudication 2 — array form
--     accommodates kant_walkthrough §3.2.1.A multi-typing reality
--     (phenomenology fits 3 enum values cleanly). Per-element CHECK
--     via `<@` operator (the array containment operator: every
--     element of node_type must be in the 10-value vocabulary array).
--   * tradition_label as TEXT[] open vocabulary per ADR 0102
--     Adjudication 6 — no element CHECK because the proposed Cluster 8
--     enum was found under-specified per kant_walkthrough §3.5.D
--     (cross-traditional, sub-traditional, and discipline-as-tradition
--     cases all need accommodation).
--   * disciplinary_domain coexists with existing domain TEXT[] per
--     ADR 0102 Adjudication 7 — `domain` at sub-discipline level
--     (existing usage); `disciplinary_domain` at discipline level
--     (new). No CHECK constraint at landing (open vocabulary; closes
--     when a future ADR commits the discipline taxonomy).
--   * 5 JSONB columns (canonical_sources, approved_examples,
--     misconceptions, assessment_items, mastery_evidence) carry
--     element-shape commitments in ADR 0102 Decision section that
--     are NOT CHECK-enforced. Element-shape soft-warn deferrable to
--     a follow-up if drift surfaces.
--   * 4 CHECK constraints land at column definition time (via
--     CHECK clauses on the ADD COLUMN statements) rather than
--     post-creation ADD CONSTRAINT — cleaner because all 380 existing
--     rows trivially satisfy the CHECKs (defaults are in-vocabulary
--     for node_type; non-NULL for the *_NOT_NULL columns; nullable
--     columns can be NULL per the CHECK's `OR IS NULL` shape for
--     granularity + jargon_load).
--   * No CASCADE discipline change. Nodes carry no learner-state FK
--     to users per ADR 0031; all 14 new columns are simple TEXT /
--     TEXT[] / JSONB types.
--   * RLS posture unchanged. Nodes read by authenticated users; writes
--     service-role-only. The new columns do not need their own RLS rule.
-- Rollback: 0140_nodes_schema_redesign_rollback.sql in the same
--   prefix slot. Reverses all changes: DROP all 4 CHECK constraints
--   (the granularity + jargon_load constraints attach to their
--   columns so DROP COLUMN cascades; the node_type_valid +
--   node_type_nonempty constraints attach to the table so explicit
--   DROP CONSTRAINT lands first); DROP all 14 columns. End-to-end
--   round-trip verified at S-0213 close per migration-discipline.md
--   "Rollback authorship" — apply 0140; capture \d+ public.nodes;
--   apply rollback; re-apply 0140; diff post-re-apply \d+ output
--   against first capture for stability.
-- See also: product/adr/0102-tier-a-cluster-4-node-schema-redesign.md,
--   product/adr/0094-phase-6-scope.md (T1-A re-verified here; T1-B partial closure here),
--   product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md (T1-A re-verified here),
--   product/adr/0097-tier-a-cluster-1-contestability-substrate.md (review_status='provisional' precedent for 'unclassified' transitional default),
--   product/adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md (compound CHECK precedent for node_type element vocabulary),
--   product/adr/0008-concept-nodes-not-thinkers.md (preserved by Adjudication 3 strict read),
--   product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md (pre-existing 3-value enum on nodes orthogonal to this cluster),
--   engine/build_readiness/pdg_papers_extraction/synthesis.md §Cluster 4 (lines 141-176),
--   engine/build_readiness/pdg_papers_extraction/kant_walkthrough.md §3 (per-node walkthrough; §3.2.1.A multi-typing; §3.4.1 subfield 9th enum value motivation),
--   engine/build_readiness/pdg_papers_extraction/foundations.md §2 (F1 threshold concepts) + §3 (F2 bridge_concept coinage finding),
--   engine/operations/migration-discipline.md,
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md (Layer 2.5 grammar),
--   product/seed-graph/migrations/0002_nodes.sql (pre-state schema; 17 columns),
--   product/seed-graph/migrations/0120_edges_contestability_substrate.sql (Cluster 1; layer-orthogonal),
--   product/seed-graph/migrations/0130_edges_three_relation_layering.sql (Cluster 2; layer-orthogonal),
--   product/seed-graph/migrations/ROUTING.md S-0213 narrative entry.

BEGIN;

-- 1. node_type TEXT[] — multi-valued enum per ADR 0102 Adjudication 2.
--    Default '{unclassified}' per Adjudication 1 (schema-only landing).
--    Per-element CHECK via `<@` operator enforces every array element
--    is in the 10-value vocabulary. The nonempty CHECK enforces no
--    row carries an empty-array node_type.
ALTER TABLE public.nodes
  ADD COLUMN node_type TEXT[] NOT NULL DEFAULT ARRAY['unclassified']::text[];

ALTER TABLE public.nodes
  ADD CONSTRAINT nodes_node_type_valid
  CHECK (node_type <@ ARRAY[
    'threshold_concept',
    'bridge_concept',
    'disciplinary_practice',
    'text_excerpt',
    'historical_context',
    'misconception',
    'comparative_lens',
    'assessment_task',
    'subfield',
    'unclassified'
  ]::text[]);

ALTER TABLE public.nodes
  ADD CONSTRAINT nodes_node_type_nonempty
  CHECK (array_length(node_type, 1) >= 1);

-- 2. disciplinary_domain TEXT — discipline level (philosophy /
--    literary_theory / history / etc.). Nullable; no CHECK at landing
--    (open vocabulary; closes when a future ADR commits the discipline
--    taxonomy). Coexists with existing domain TEXT[] at sub-discipline
--    level per ADR 0102 Adjudication 7.
ALTER TABLE public.nodes
  ADD COLUMN disciplinary_domain TEXT;

-- 3. granularity TEXT — three-value enum per synthesis line 154.
--    Nullable + CHECK allows NULL OR IN ('coarse', 'medium', 'fine').
ALTER TABLE public.nodes
  ADD COLUMN granularity TEXT
  CONSTRAINT nodes_granularity_valid
  CHECK (granularity IS NULL OR granularity IN ('coarse', 'medium', 'fine'));

-- 4. audience_tags TEXT[] — open vocabulary; intended values per
--    synthesis: intro, intermediate, advanced, majors, non-majors,
--    multilingual_cohort + future additions. Default '{}'.
ALTER TABLE public.nodes
  ADD COLUMN audience_tags TEXT[] NOT NULL DEFAULT '{}'::text[];

-- 5. canonical_sources JSONB array of citation objects per
--    synthesis line 155. Element shape {author, year, title,
--    identifier?} documented in ADR 0102; not CHECK-enforced.
ALTER TABLE public.nodes
  ADD COLUMN canonical_sources JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 6. approved_examples JSONB array per synthesis line 156. Element
--    shape {description, source_ref?}. "Examples the LLM may use" —
--    distinct from any free-form examples in teaching_notes because
--    curated and structurally retrievable.
ALTER TABLE public.nodes
  ADD COLUMN approved_examples JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 7. misconceptions JSONB array per synthesis line 157. Element
--    shape {description, remediation_ref?, remediation_note?}.
--    Lightweight encoding; the full misconception sub-graph lands
--    in Cluster 5 per synthesis §Cluster 5 + ADR 0094 dependency
--    order C2 + C4 → C5.
ALTER TABLE public.nodes
  ADD COLUMN misconceptions JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 8. assessment_items JSONB array per synthesis line 158 + ADR 0102
--    Adjudication 8 (JSONB rather than FK to a public.assessments
--    table that doesn't exist).
ALTER TABLE public.nodes
  ADD COLUMN assessment_items JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 9. mastery_evidence JSONB array per synthesis line 159. Element
--    shape {evidence_kind, observation_target}.
ALTER TABLE public.nodes
  ADD COLUMN mastery_evidence JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 10. accessibility_notes TEXT per synthesis line 160. Free-text
--     notes for accessibility considerations.
ALTER TABLE public.nodes
  ADD COLUMN accessibility_notes TEXT;

-- 11. assumed_background TEXT[] per synthesis line 161. Text-array
--     list of prerequisite-shaped background assumptions not already
--     captured by inbound hard_prerequisite / soft_prerequisite edges.
ALTER TABLE public.nodes
  ADD COLUMN assumed_background TEXT[] NOT NULL DEFAULT '{}'::text[];

-- 12. jargon_load TEXT — three-value enum per synthesis line 162.
--     Nullable + CHECK allows NULL OR IN ('low', 'medium', 'high').
ALTER TABLE public.nodes
  ADD COLUMN jargon_load TEXT
  CONSTRAINT nodes_jargon_load_valid
  CHECK (jargon_load IS NULL OR jargon_load IN ('low', 'medium', 'high'));

-- 13. cultural_specificity TEXT per synthesis line 163. Records the
--     cultural background the node assumes (e.g., Western_continental_
--     philosophy); enables the equity-metadata validator soft-warn.
ALTER TABLE public.nodes
  ADD COLUMN cultural_specificity TEXT;

-- 14. tradition_label TEXT[] open vocabulary per ADR 0102 Adjudication 6.
--     No element CHECK because the proposed Cluster 8 enum was found
--     under-specified per kant_walkthrough §3.5.D. Cluster 8 (Phase 7+
--     deployment governance) wires the strip-at-LLM-boundary mechanism;
--     this migration owns the column.
ALTER TABLE public.nodes
  ADD COLUMN tradition_label TEXT[] NOT NULL DEFAULT '{}'::text[];

COMMIT;
