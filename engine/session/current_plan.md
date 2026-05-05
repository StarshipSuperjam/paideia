paths_to_modify: ["product/seed-graph/migrations/0050_seed_services_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

S-0074 routine-mode session against task P5-10 Service nodes seed. P5-10 is the
single-task service-node tier per phase_5.md T1-B — "the cross-subject foundational
concepts that several philosophy subdomains require but that no single subject owns
canonically: formal-logic primitives, math prerequisites, history terminators." Range
`0050-0059`; first migration `0050_seed_services_part1`. depends_on [P5-01a] satisfied
since S-0050. Eligibility walk picked P5-10 as the only remaining parallel-eligible
task after S-0073 closed P5-09 (P5-11 cross-bridges depends on all subjects + service
nodes; P5-12 closeout depends on P5-11).

Authoring `0050_seed_services_part1.sql` with 25 nodes + 28 edges across three
sub-clusters, all `confidence_level: INTERPRETED`, all `domain[]={'service'}`,
within-service edges only (cross-domain bridges to philosophy subdomains deferred
to P5-11):

(A) Formal-logic primitives (10 nodes): truth_value, bivalence_principle,
argument_logical, validity_logical, soundness_logical, inference_rule, modus_ponens,
modus_tollens, formal_proof, counterexample. These are sub-philosophical primitives
distinct from the philosophical-logic concepts P5-03 owns (propositional_logic,
predicate_logic, modal_logic, etc.); the names are deliberately suffixed (_logical,
_value) where collision was a risk to avoid drift with substantive concepts already
seeded (truth in language, validity in metaphysics-adjacent epistemology terms).

(B) Math prerequisites (8 nodes): set_mathematical, function_mathematical,
axiom_mathematical, quantifier, probability_mathematical, conditional_probability,
bayes_theorem, expected_value. Same suffix discipline (_mathematical) for set/function
to avoid drift with seeded `relation` (metaphysical, in P5-02a) and conceptually
broader `function` framings.

(C) History terminators (7 nodes): presocratic_naturalism, greek_atomism,
aristotelian_four_causes, scholasticism, renaissance_mechanism,
vienna_circle_logical_positivism, hegelian_dialectic. Doctrine/movement nodes per
ADR 0008 (concepts not thinkers) — each names a position or methodological tradition
that several philosophy subdomains historically descend from but that no single
subdomain canonically owns.

Within-service edges (28 total): formal-logic intra-cluster (10), math intra-cluster
(8), history intra-cluster (5), service-to-service bridges (5 — axiom_mathematical →
formal_proof, set_mathematical → quantifier already counted in math cluster, plus
renaissance_mechanism / hegelian_dialectic / aristotelian_four_causes →
vienna_circle_logical_positivism). All `pedagogical_prerequisite`. No cross-domain
edges (P5-11's exclusive responsibility); no historical_influence edges; no new
edge predicate registrations.

Pre-apply node-existence sweep against the live DB confirmed via grep across
existing seed migrations: none of the 25 proposed ids collide with any of the
~355 already-seeded ids. The closest near-collisions (relation, proposition,
function, evidence, truth) are canonical-homed in metaphysics / language /
epistemology and use different ids than the suffixed service-node names selected
here.

ROUTING.md gets the standard per-session narrative entry under "Phase 5
per-session narrative" naming the migration, the apply mechanic via
`apply_migration.py` per ADR 0055 (sixth load-bearing routine-mode exercise of the
wrapper), the graph_version increment 14 → 15 honored, and the forward-pointer to
P5-11 cross-bridges as the next eligible task.

Operational allowlist files (engine/session/current.json, current_plan.md,
auto_target.json status fields, register_state.json, archive/S-0074.json,
ENGINE_LOG.md, STATE.md) commit per ADR 0051 routine-mode posture; not listed
in scope_lock.

Both task criteria addressed: criterion 0 (migration_applied id
0050_seed_services_part1) lands when apply_migration.py exits 0 and the
schema_migrations row is recorded; criterion 1 (validate_passes) lands when
validate.py exits with no hard-fails (exit 1 with soft-warns only is the expected
shape per the prior 13 routine-mode close-outs).
