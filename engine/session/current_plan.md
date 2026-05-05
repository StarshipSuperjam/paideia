# S-0068 plan — routine task P5-06 Aesthetics seed

paths_to_modify: [
  "product/seed-graph/migrations/0110_seed_aesthetics_part1.sql",
  "product/seed-graph/migrations/ROUTING.md"
]
criteria_addressed: [0, 1]

## Rationale

S-0068 is the tenth routine-mode session against [`engine/session/auto_target.json`](auto_target.json) (target T-PHASE-5) and the first Phase 5 session against the aesthetics subdomain. The session executes task **P5-06 Aesthetics seed** — a single (not pre-split) task per [phase_5.md](../build_readiness/phase_5.md) T1-B. P5-06's `depends_on: ["P5-01a"]` was satisfied at S-0050; the task was previously `blocked: decision-required` per Issue #18 (DB-apply path regression), unblocked at S-0067 after the `apply_migration.py` wrapper landed at S-0064 and was first-exercised at S-0066. Routine eligibility walk picked P5-06 as the first pending task in walk order at S-0068 boot.

**Migration deliverable.** `product/seed-graph/migrations/0110_seed_aesthetics_part1.sql` with the aesthetics core inventory across six clusters, all within-domain, all `pedagogical_prerequisite` edges:

- **Foundation (4)** — aesthetics (the field), aesthetic_experience (the phenomenon), aesthetic_property (qualities like beauty, sublimity, gracefulness), aesthetic_judgment (judgments of taste).
- **Definition of art (6)** — art (the philosophical question), imitation_theory_art (Plato/Aristotle mimesis), expression_theory_art (Tolstoy/Collingwood), formalism_artistic (Bell, Fry — significant form), institutional_theory_of_art (Dickie 1974), historical_theory_of_art (Levinson 1979).
- **Aesthetic value & taste (4)** — aesthetic_value, taste_aesthetic (Hume's "Of the Standard of Taste" 1757), aesthetic_disinterest (Kant 1790; Schopenhauer; Stolnitz), sublime (Burke 1757; Kant 1790).
- **Kantian aesthetics (2)** — kantian_aesthetic_judgment (Kant's third Critique), free_play_imagination_understanding (Kant's transcendental account).
- **Representation & meaning (4)** — pictorial_representation (Goodman 1968 *Languages of Art*), depiction (resemblance vs. convention; Wollheim's seeing-in), expression_in_art (Goodman, Davies, Robinson), metaphor (Black, Davidson, Goodman).
- **Ontology of artworks (4)** — ontology_of_artworks (the field), type_token_artworks_distinction (musical works as types), fictional_truth (Walton 1990 *Mimesis as Make-Believe*; Lewis 1978), ontology_musical_works (Goodman, Levinson, Wolterstorff).
- **Criticism & interpretation (3)** — art_criticism, intentionalism_artistic (Hirsch, Levinson actual-intentionalism, Stecker hypothetical-intentionalism), anti_intentionalism (Wimsatt-Beardsley intentional fallacy 1946).

**Total: 27 nodes, ~32 edges.** All edges are within-domain `pedagogical_prerequisite`; cross-domain bridges (aesthetics ↔ ethics on moral content of art, aesthetics ↔ philosophy of language on metaphor and meaning, aesthetics ↔ metaphysics on type-token ontology) are P5-11's exclusive surface per [phase_5.md](../build_readiness/phase_5.md) T2-G #1.

**Confidence_level distribution.** 27/27 INTERPRETED (100%) per [phase_5.md](../build_readiness/phase_5.md) T2-B (INTERPRETED ≥ 70% floor; SYNTHETIC ≤ 20% ceiling). EXTRACTED 0% (no SEP/IEP prose lifted per [ADR 0011](../../product/adr/0011-no-hosted-copyrighted-material.md)). SYNTHETIC 0% (every concept is well-named in the SEP/IEP entry inventory and analytic-aesthetics literature).

**graph_version increment.** Read 10 at session boot (post-S-0066 per ROUTING.md narrative); UPDATE writes 11 in the migration's BEGIN/COMMIT. Every node/edge carries `graph_version_added = 11`.

**Apply mechanics.** Single `engine/tools/apply_migration.py --migration-file product/seed-graph/migrations/0110_seed_aesthetics_part1.sql` invocation per [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md). Sub-range slots 0111-0119 left reserved.

**Verification.** `python3 engine/tools/check_target.py --task-id P5-06` PASS both criteria (`migration_applied` for 0110_seed_aesthetics_part1, `validate_passes`); `python3 engine/tools/validate.py` exit 0 or 1 (no hard-fails).

**Two-commit pattern.** Eager-claim (register + current.json + auto_target P5-06 in_progress) → deliverable (migration + ROUTING.md) → close (auto_target P5-06 complete + STATE.md + ENGINE_LOG + archive S-0068.json + register bump).

**PREDICATE_MANIFEST.md not edited.** Only `pedagogical_prerequisite` used; already in v1 registry per the manifest.

**Cross-domain edges deferred to P5-11.** Aesthetic concepts authored here with cross-domain reach: aesthetic_judgment / kantian_aesthetic_judgment ↔ ethics (moral judgment, judgment of taste analogy); expression_theory_art / expression_in_art ↔ philosophy of mind (intentionality, mental content); metaphor / pictorial_representation ↔ philosophy of language (P5-08 reference and meaning); fictional_truth ↔ metaphysics (modal realism, fictional entities) and philosophy of language (P5-08 fictionalism); type_token_artworks_distinction ↔ metaphysics (P5-02b on universals, types). Bridges land at P5-11.

**No HANDOFF or Issue authoring expected.** Standard seed shape; no infrastructure blockers anticipated (apply_migration.py wrapper is now load-bearing-confirmed per S-0066). If a blocker emerges, route per CLAUDE.md routine-mode posture: HANDOFF for session-internal handoff or `gh issue create` for cross-session deferral per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

**Forward state target.** P5-06 complete in `auto_target.json`; P5-07b, P5-08, P5-09, P5-10 remain eligible for the next routine fire's eligibility walk (P5-07b depends on P5-07a complete, P5-08/09/10 on P5-01a only). Phase 5 progress: 10/16 tasks complete after this session.
