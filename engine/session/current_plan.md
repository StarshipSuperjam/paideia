paths_to_modify:
  - product/seed-graph/migrations/0040_seed_mind_part1.sql
  - product/seed-graph/migrations/ROUTING.md
criteria_addressed: [0, 1]

# Session plan — S-0066 routine, task P5-07a Philosophy of Mind core seed

The session executes task **P5-07a Philosophy of mind core seed** of target T-PHASE-5 per
[engine/build_readiness/phase_5.md](../build_readiness/phase_5.md) (gate report) and
[product/adr/0052-phase-5-philosophy-subdomain-decomposition.md](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md).
P5-07a's `depends_on: ["P5-01a"]` is satisfied (P5-01a complete since S-0050+S-0051). The
routine eligibility walk picked P5-07a as the first pending task in walk order after P5-05
closed at S-0061 (P5-06 Aesthetics is currently `blocked` per Issue #18; that flip routes
through an interactive session, not this routine).

## Deliverables

1. **`product/seed-graph/migrations/0040_seed_mind_part1.sql`** — first Phase 5 mind file,
   single-file authoring within sub-range `0040-0045` per phase_5.md T2-A. Per phase_5.md
   T1-B P5-07a covers core mind concepts: **mental causation, intentionality, perception,
   personal identity, AI/computational mind**. Specialized concepts — consciousness, qualia,
   hard problem, phenomenology adjacencies — are P5-07b's range (`0046-0049`) and are
   deliberately excluded from this file.

   **Node inventory (28-30 nodes, INTERPRETED 100% per ADR 0030):**
   - **Foundation (3)** — philosophy_of_mind (umbrella), mind (the explanandum), mental_state,
     propositional_attitude (Russell's term; Davidson, Fodor — beliefs/desires/intentions as
     relations to propositions).
   - **Dualism / physicalism (8)** — dualism (umbrella), substance_dualism (Descartes),
     property_dualism (Chalmers, Jackson — physical with non-physical mental properties; the
     position itself, not the hard problem which is P5-07b), physicalism (the umbrella thesis),
     type_identity_theory (Smart, Place — mental types ARE physical types), functionalism
     (Putnam, Lewis, Block — mental states are functional states), behaviorism_logical (Ryle,
     Hempel, Carnap — mental states reduce to behavioral dispositions), eliminative_materialism
     (Churchland — folk psychology is false; no beliefs/desires).
   - **Mental causation (4)** — mental_causation (the puzzle), causal_exclusion_argument (Kim
     — physical causal closure forces overdetermination or epiphenomenalism),
     supervenience_mental (mental supervenes on physical without identity reduction),
     multiple_realizability (Putnam — mental states are realizable in different physical
     substrates; the canonical anti-type-identity argument that motivates functionalism).
   - **Intentionality (4)** — intentionality (Brentano's mark of the mental — aboutness),
     representational_theory_of_mind (Fodor — mental states are representations),
     functional_role_semantics (Block, Harman — content from inferential role),
     causal_theory_of_mental_content (Dretske, Stampe — content from reliable causal
     covariation).
   - **Perception (4)** — perception (the philosophical question), direct_realism_perceptual
     (perception as immediate awareness of objects), representationalism_perception (perception
     as mediated by representations), sense_data_theory (Russell, Ayer — perception of mental
     intermediaries).
   - **Personal identity (3)** — personal_identity (the diachronic question for persons),
     psychological_continuity_theory (Locke, Parfit — continuity of memory/character),
     animalism (Olson — we are human animals).
   - **AI / computational mind (3)** — computational_theory_of_mind (the brain is a computer;
     Putnam), chinese_room_argument (Searle — syntax does not suffice for semantics),
     turing_test (Turing 1950).

   **Edge inventory (~32-36 edges, all `pedagogical_prerequisite`, all within-domain):**
   - Foundation spine: philosophy_of_mind → mind → mental_state → propositional_attitude.
   - Dualism / physicalism branch: mental_state → dualism, dualism → {substance_dualism,
     property_dualism}; mental_state → physicalism, physicalism → {type_identity_theory,
     functionalism, behaviorism_logical, eliminative_materialism}; multiple_realizability
     bridge: type_identity_theory → multiple_realizability → functionalism.
   - Mental causation branch: mental_state → mental_causation, mental_causation →
     causal_exclusion_argument; physicalism → supervenience_mental → mental_causation.
   - Intentionality branch: mental_state → intentionality, intentionality →
     {representational_theory_of_mind, functional_role_semantics,
     causal_theory_of_mental_content}.
   - Perception branch: mental_state → perception, perception → {direct_realism_perceptual,
     representationalism_perception, sense_data_theory}.
   - Personal identity branch: mind → personal_identity, personal_identity →
     {psychological_continuity_theory, animalism}.
   - Computational branch: functionalism → computational_theory_of_mind,
     computational_theory_of_mind → {chinese_room_argument, turing_test}.

   **Cross-domain edges deferred to P5-11.** Mind has natural bridges to epistemology
   (perception → epistemic_justification; introspection → knowledge), to philosophy of
   language (intentionality → reference, propositional_attitude → propositional_content),
   to metaphysics (mental_causation → causation, personal_identity → numerical_identity /
   persistence; bundle theory of self), to ethics (free_will / moral_responsibility from
   P5-02b; agency), to philosophy of science (computational_theory_of_mind → algorithmic
   complexity / cognitive science). Per phase_5.md T2-G #1 the bridges land at P5-11.

   **graph_version increment.** Read 9 at session boot (post-S-0061 per ROUTING.md
   narrative); UPDATE writes 10 in the same transaction as the INSERTs; every node and edge
   carries `graph_version_added = 10` per the per-session monotonicity contract at
   ROUTING.md "graph_version increment contract".

2. **`product/seed-graph/migrations/ROUTING.md`** — per-session narrative entry (~300-400
   words) documenting the seed file, edge structure, graph_version increment, cross-domain
   deferrals, and forward pointer to the next eligible task (P5-07b consciousness/specialized
   becomes eligible after this lands).

## Why these paths address the criteria

P5-07a's criteria are:
- `migration_applied` for `0040_seed_mind_part1` — addressed by authoring the file at the
  exact filename the predicate queries (per check_target.py's name-based lookup post the
  S-0051 fix per Issue #5) and applying it via `engine/tools/apply_migration.py
  --migration-file product/seed-graph/migrations/0040_seed_mind_part1.sql`. The wrapper
  performs shape verification (filename pattern, contract header, BEGIN/COMMIT, scope_lock),
  applies the body via psycopg autocommit, then INSERTs the row into
  `supabase_migrations.schema_migrations` with the migration name.
- `validate_passes` — addressed by the migration's adherence to the v1 predicate registry
  (only `pedagogical_prerequisite` used; PREDICATE_MANIFEST.md not edited), the within-domain
  constraint (no cross-domain edges; P5-11 is the cross-bridge surface), the no-cycle DAG
  structure (every edge points from a lower pedagogical tier to a higher one; Kosaraju SCC
  passes post-apply), and the `confidence_level` distribution at 100% INTERPRETED (well
  within phase_5.md T2-B's INTERPRETED ≥ 70% floor and SYNTHETIC ≤ 20% ceiling).

## Two-commit pattern (S-0053+ procedural finding)

Per the S-0053/S-0054/S-0056/S-0057/S-0058/S-0059/S-0061 pattern, the deliverable commit
(migration file + ROUTING.md narrative) lands separately from the auto_target.json
status-flip commit so the staged scope-check engages on the deliverables under the
in_progress task rather than dropping into "no in_progress task; skipping" mode. Sub-range
slots `0041-0045` left reserved (granularity principle achieved within `0040`; reserved for
future Phase 6+ extension if telemetry warrants additional core-mind concepts).

## Apply mechanics (potential chunked-apply path)

The apply_migration.py wrapper is the canonical path. If the migration body's executable
SQL exceeds psycopg's single-call comfortable size (S-0058/S-0059/S-0061 finding for
~70KB+ payloads), the chunked execute_sql + final apply_migration marker pattern is
documented in ROUTING.md for those sessions. For a 28-30 node + ~32-36 edge migration
the body is expected to fit a single apply_migration call comfortably (S-0050's 28+34 fit
in one; this is the same scale).

## Scope_lock honored

`scope_lock.allowed_paths` for P5-07a includes `0040_*.sql` through `0045_*.sql`,
PREDICATE_MANIFEST.md, ROUTING.md. Operational allowlist (current.json, current_plan.md,
auto_target.json status fields, archive/, register_state.json, ENGINE_LOG.md, HANDOFF.md,
STATE.md) is unioned automatically per ADR 0051 / CLAUDE.md "Routine-mode posture".
PREDICATE_MANIFEST.md is in scope but is not expected to need editing — only
pedagogical_prerequisite edges are authored, already in the v1 registry.
