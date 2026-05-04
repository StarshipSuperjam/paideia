paths_to_modify: ["product/seed-graph/migrations/0016_seed_epistemology_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

This routine session executes task P5-01b "Epistemology specialized seed" of target T-PHASE-5. The task is the b-half of the epistemology pre-split per phase_5.md T1-B; it depends on P5-01a (`complete` per S-0050 + S-0051's `migration_applied` fix) and feeds the cross-bridges task P5-11.

Scope per the auto_target.json scope_lock for P5-01b:
- product/seed-graph/migrations/0016_*.sql (the migration file)
- 0017–0019_*.sql (additional sub-range, not used this session)
- PREDICATE_MANIFEST.md (no edits needed; only pedagogical_prerequisite used)
- ROUTING.md (per-session narrative entry per ROUTING.md "Per-session narrative" discipline)

Concept inventory (~26 nodes covering the specialized half — social, virtue, formal, reliabilism, knowledge-first, skepticism varieties beyond cartesian, normative epistemology):

- Social epistemology cluster: social_epistemology, epistemic_injustice, peer_disagreement, epistemic_dependence, expertise.
- Virtue epistemology cluster: virtue_epistemology, intellectual_virtue, virtue_reliabilism, virtue_responsibilism.
- Formal epistemology / Bayesian cluster: formal_epistemology, credence, bayesian_epistemology, conditionalization, dutch_book_argument.
- Reliabilism cluster: reliabilism, generality_problem.
- Knowledge-first / specialized: knowledge_first_epistemology, understanding, evidentialism.
- Skepticism varieties: pyrrhonian_skepticism, agrippan_trilemma, problem_of_induction, contextualism_epistemic, relevant_alternatives_theory.
- Norms / closure responses: norm_of_assertion, closure_denial.

Edges (all pedagogical_prerequisite, all within-domain epistemology):
- Cross-references from P5-01a anchors into P5-01b specialized (within-domain since both are tagged only `epistemology`): testimonial_knowledge → social_epistemology, knowledge → social_epistemology, knowledge → virtue_epistemology, epistemic_justification → virtue_epistemology, epistemic_justification → reliabilism, externalism_epistemic → reliabilism, epistemic_justification → evidentialism, internalism_epistemic → evidentialism, belief → credence, evidence → bayesian_epistemology, knowledge → knowledge_first_epistemology, justified_true_belief → knowledge_first_epistemology, propositional_knowledge → understanding, skepticism_epistemic → pyrrhonian_skepticism, skepticism_epistemic → agrippan_trilemma, evidence → problem_of_induction, skepticism_epistemic → contextualism_epistemic, skepticism_epistemic → relevant_alternatives_theory, epistemic_closure → closure_denial, epistemic_closure → contextualism_epistemic, propositional_knowledge → norm_of_assertion.
- Within-cluster within P5-01b: social_epistemology → epistemic_injustice, social_epistemology → peer_disagreement, social_epistemology → epistemic_dependence, social_epistemology → expertise, expertise → epistemic_dependence; virtue_epistemology → intellectual_virtue, virtue_epistemology → virtue_reliabilism, virtue_epistemology → virtue_responsibilism, intellectual_virtue → virtue_responsibilism; formal_epistemology → credence, credence → bayesian_epistemology, bayesian_epistemology → conditionalization, bayesian_epistemology → dutch_book_argument; reliabilism → generality_problem, reliabilism → virtue_reliabilism; pyrrhonian_skepticism → agrippan_trilemma; problem_of_induction → pyrrhonian_skepticism.

graph_version contract: read current value at boot (post-S-0050: 2); UPDATE to 3 in the same transaction; every node + edge writes `graph_version_added = 3`.

confidence_level composition target per phase_5.md T2-B: INTERPRETED ≥ 70% floor; SYNTHETIC ≤ 20% ceiling. This seed targets 26/26 INTERPRETED (100%) like P5-01a; every concept is well-named in the SEP/IEP entry inventory and corresponds to an analytic-tradition concept the literature explicitly names (no inferred-structure-SEP-doesn't-itself-name authoring needed for these specialized concepts).

domain[]: every node tagged `{epistemology}` only. Cross-domain tags deferred to P5-11 per phase_5.md T2-G #4 (domain-tag cardinality explosions vector).

Cross-domain edges deferred to P5-11 per T2-G #1 (cross-domain edge collisions vector). Even though concepts like `bayesian_epistemology`, `problem_of_induction`, and `formal_epistemology` reach into philosophy of science and logic, the bridges land in P5-11.

Criteria addressed:
- index 0 — `migration_applied` for `0016_seed_epistemology_part1`: addressed by writing the SQL and applying via Supabase MCP `apply_migration`.
- index 1 — `validate_passes`: addressed by running `validate.py` post-apply with venv Python; expect zero hard-fails plus the standard partial-seed soft-warns (`missing_rigor_score` for the 26 new nodes, `orphan_leaf` for any newly-orphan terminal nodes resolved at P5-11, `issue_collision` carryover from #1/#2/#11). Cross-domain ratio is 0% (no cross-domain edges authored), so `suspicious_cross_domain_ratio` will not fire.
