paths_to_modify:
  - product/seed-graph/migrations/0020_seed_ethics_part1.sql
  - product/seed-graph/migrations/ROUTING.md

criteria_addressed: [0, 1]

P5-04a Ethics metaethics+normative seed authors `0020_seed_ethics_part1.sql` covering the metaethics layer (moral realism, anti-realism, expressivism, error theory, naturalism vs non-naturalism, moral epistemology, motivational internalism/externalism, the is-ought distinction, the open-question argument) and the normative layer (consequentialism with utilitarianism canonical, deontology with Kantian categorical-imperative anchor, virtue ethics with Aristotelian eudaimonia anchor, contractualism Rawls/Scanlon, ethical egoism, divine command, particularism). Mirrors the cluster-+-foundation pattern from P5-01a / P5-02a / P5-03 at the granularity-principle node count (~25-30). Every node `confidence_level=INTERPRETED`, `domain[]={'ethics'}`, `provenance='ai-seed'`. Edges all `pedagogical_prerequisite`, all within-domain (cross-domain bridges to deontic_logic, free_will, moral_responsibility, knowledge, belief, etc. defer to P5-11 per phase_5.md T2-G #1).

ROUTING.md gets a per-session narrative entry under "Per-session narrative" (operational discipline shared across all P5 seeds; not in scope_lock for tracked-paths but explicitly in the allowed_paths set of P5-04a).

Migration `0020_seed_ethics_part1` addresses criterion 0 (`migration_applied`); the post-apply `validate.py` clean run addresses criterion 1 (`validate_passes`). graph_version increments 6 → 7 in the same transaction as the INSERTs per ROUTING.md "graph_version increment contract".
