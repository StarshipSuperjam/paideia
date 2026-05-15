paths_to_modify: ["engine/build_readiness/seed_qa_evidence/shard_15.md"]
criteria_addressed: [0, 1]

# Plan — S-0177 routine SQA-15 (T-SEED-QA shard 15 QA census)

Fifteenth routine fire of T-SEED-QA. Score shard 15 — 27 `pedagogical_prerequisite` edges against C1 and 20 nodes against C2/C3 per the pinned rubric at [engine/build_readiness/seed_qa_audit.md](../build_readiness/seed_qa_audit.md). Write the single scope-locked evidence file `engine/build_readiness/seed_qa_evidence/shard_15.md`.

## Procedure

1. Load `shards["shard_15"]` from `engine/build_readiness/seed_qa_evidence/shards.json` (27 edges + 20 nodes, full content embedded).
2. For each edge: assign C1 verdict (Sound / Defensible / Reversed / Weak-redundant) from parametric reasoning; cross-reference audit follow-up migrations 0061–0065 with exact-and-reverse tuple comparison; flag AUDIT-TOUCHED hits with migration number; record one or two-sentence rationale. SEP fetch reserved for genuinely uncertain verdicts (default is parametric).
3. For each node: assign C2 (yes/no/ABSENT — does `teaching_notes` give a learner a foothold beyond restating summary?) and C3 (yes/no — does `summary` parse cold without prior context, watching for circular / jargon-gated / assumes-the-concept failures?).
4. Tally: total, Reversed count, Weak-redundant count, C2 fail count, C3 fail count, teaching_notes ABSENT count.
5. Write the shard_15.md evidence file matching the pinned schema in seed_qa_audit.md exactly. Anti-scope: no Issue filing, no ADR memos, no migration edits, no aggregation across shards (the closeout SQA-20 does that). Cross-cutting observations sparingly — patterns are the closeout's surface.

## Rubric calibration anchors from the prior batch

- Prior 14 shards: cumulative C1 23/380 = 6.05% (under the 13% production-audit baseline). 0-defect run of 5 consecutive shards (10-14). C2 0 fails total. C3 has 1 fail across all 14 shards.
- Defensible sub-shapes already established and held consistent: discipline → object-of-study; umbrella → specific instance (`reductionism_in_science→multiple_realizability`, `deontology→kantian_ethics`); framework-introduces-its-central-concept (shard 13 E-15, shard 14 E-17); structural-vs-pedagogical priority (`formal_proof→classical_logic`); parallel-theories-with-historical-succession (shard 12 E-13 DN→IBE); framing-question-before-argument-FOR-the-framing's-diagnosis (shard 14 E-13 hard_problem→knowledge_argument).
- C3 borderline-PASS calibration: load-bearing term unglossed in opening but rescued by inline gloss or by structural-shape parsability with subsequent grounding (shard 11 N-3 IIT, shard 12 N-3 formal_proof, shard 13 N-10 ersatz_modal_realism, shard 14 N-2 predicate_logic, N-18 gunk).
- Audit-touched workflow: programmatic proximity check followed by per-hit exact-tuple comparison against the 0061–0065 assertion-block tuple lists. Raw grep produces false positives (shared endpoint, adjacent edges); the canonical check is exact-and-reverse tuple match.

## Criteria mapping

- Criterion 0 (`file_exists` `engine/build_readiness/seed_qa_evidence/shard_15.md`) — file written at step 5.
- Criterion 1 (`validate_passes`) — pre-commit hook runs `check_routine_scope.py --staged` against the staged path; the scope-lock allowed_paths is exactly the one file authored.

## Rationale (path/criterion alignment)

The shard_15.md path is the sole task-deliverable; it is also the sole criterion-0 target. The operational allowlist covers the lifecycle files that ride with eager-claim and close commits. No other tracked path is touched.
