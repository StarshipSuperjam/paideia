# S-0054 plan — P5-02a Metaphysics core seed

```text
paths_to_modify: ["product/seed-graph/migrations/0030_seed_metaphysics_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]
```

## Rationale

The active routine task is **P5-02a Metaphysics core seed** (target T-PHASE-5; auto_target.json). Selected by routine eligibility walk: P5-01a complete, P5-01b complete, P5-02a is the next pending task with all `depends_on` satisfied (`["P5-01a"]` complete since S-0050).

**Migration file:** `0030_seed_metaphysics_part1.sql` — the first migration in the metaphysics range (`0030-0035` per [ROUTING.md](../../product/seed-graph/migrations/ROUTING.md) numeric prefix scheme as extended at S-0045). Matches `migration_applied` criterion id (`0030_seed_metaphysics_part1`) per auto_target.json P5-02a.criteria[0].

**Content scope.** Per [phase_5.md](../build_readiness/phase_5.md) T1-B, metaphysics core (P5-02a) covers the four foundational pillars: **being, identity, causation, time**. Specialized metaphysics — modality, free will, properties/universals, mereology — is P5-02b's exclusive surface. Concept inventory at the granularity principle (~27 nodes):

- **Being / ontology cluster** (9 nodes): metaphysics (umbrella), ontology, existence, substance, property (basic category — deeper to P5-02b), relation, event, abstract_object, concrete_object
- **Identity cluster** (7 nodes): numerical_identity, leibniz_law, persistence, endurantism, perdurantism, temporal_parts, ship_of_theseus
- **Causation cluster** (4 nodes): causation, humean_regularity_theory, counterfactual_theory_of_causation, causal_powers
- **Time cluster** (7 nodes): time, a_theory_of_time, b_theory_of_time, presentism, eternalism, growing_block_theory, mctaggarts_paradox

**Edges (~32, all within-domain `pedagogical_prerequisite`):** spine from metaphysics → ontology → existence → categories; identity branch rooted at existence → numerical_identity → persistence → 3D/4D split; causation branch rooted at existence + event → causation → three theories; time branch rooted at time → A/B-theory split → presentism/eternalism/growing-block → McTaggart's paradox; cross-branch connections (time → persistence; causation → time; event → causation).

**Confidence_level distribution.** Target 27/27 INTERPRETED (100%) per phase_5.md T2-B floor (≥70%). Mirrors P5-01a/P5-01b. EXTRACTED is 0% (no SEP/IEP prose lifted per ADR 0011); SYNTHETIC is 0% (every concept well-named in the analytic-tradition entry inventory).

**Cross-domain edges deferred to P5-11** per phase_5.md T2-G #1. Metaphysics has natural bridges to philosophy of mind (mental_causation, personal_identity), philosophy of science (causation in scientific explanation, time in physics), philosophy of language (existence and ontological commitment via Quine), epistemology (knowledge of abstract objects). All deferred.

**ROUTING.md addition.** Per-session narrative entry for S-0054 describing what was authored and why, ~250-300 words mirroring S-0050 / S-0053 entries.

**No new predicates.** Only `pedagogical_prerequisite` used (already in v1 registry per [PREDICATE_MANIFEST.md](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)). PREDICATE_MANIFEST.md edit not required → not in scope_lock-required paths.

## Criteria addressed

- **0** — `migration_applied` for `0030_seed_metaphysics_part1`. The authored SQL file is applied via Supabase MCP `apply_migration`; verified post-apply via `check_target.py --task-id P5-02a`.
- **1** — `validate_passes`. The validator is run with venv Python so the live graph audit engages; expected shape mirrors P5-01a/P5-01b: 30 checks, 0 hard-fails, soft-warns include `missing_rigor_score` (partial-seed expected per phase_5.md T2-C) and `issue_collision` (carryover from upstream MemPalace #1/#2 plus open project Issues #12/#13).

## Operational allowlist files (touched but not in scope_lock requirement)

- `engine/session/current.json` — eager-claim + completion bookkeeping
- `engine/session/current_plan.md` — this file
- `engine/session/auto_target.json` — P5-02a status flips (pending → in_progress → complete); no other keys mutated (master-plan-integrity gate enforces)
- `engine/session/register_state.json` — counter bump (next_id 0054 → 0055; last_claimed S-0053 → S-0054)
- `engine/session/archive/S-0054.json` — archive at shutdown
- `engine/ENGINE_LOG.md` — Added entry recording the metaphysics core seed
- `engine/STATE.md` — last/prior session pointers + next-session work item update at shutdown

Per S-0053's procedural finding, the deliverable commit (migration + ROUTING.md) is separated from the status-flip commit (auto_target.json) so the staged scope-check engages on the deliverables under in_progress task rather than dropping into "no in_progress task; skipping" mode.
