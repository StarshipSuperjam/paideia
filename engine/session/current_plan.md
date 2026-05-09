paths_to_modify: ["engine/build_readiness/phase_5_production_audit_evidence/epistemology.md"]
criteria_addressed: [0, 1]

# Plan — S-0105 (routine) — T-PHASE-5-AUDIT / AUDIT-EPI

This routine session executes T-PHASE-5-AUDIT task `AUDIT-EPI`: epistemology
subdomain audit — SEP-anchored review of a 35%-density edge sample (k=25 of N=72)
plus an edge-anchored node sample (~12 unique nodes), per the master-plan prompt
templates at `engine/build_readiness/phase_5_production_audit.md`.

The single deliverable is
`engine/build_readiness/phase_5_production_audit_evidence/epistemology.md`,
populated with verdict + SEP-anchored reasoning + confidence per edge and per
node per the fixed schema in the master plan §"Evidence file schema".

## Why these paths address the criteria

- **`file_exists` criterion** (path:
  `engine/build_readiness/phase_5_production_audit_evidence/epistemology.md`) —
  the deliverable IS the file at the criterion's path; populating it satisfies
  the criterion directly.
- **`validate_passes` criterion** — committing the file routes through the
  pre-commit hook including `validate.py`; absence of hard-fails satisfies the
  criterion.

## Execution shape

1. Pull the live epistemology-domain edge population from production Supabase
   via `engine/tools/apply_migration.py`-equivalent psycopg connection (read-only
   query; no writes). Filter is "edges where source.domain = 'epistemology' OR
   target.domain = 'epistemology' AND NOT both endpoints in service" — the
   master-plan figure of N=72 corresponds to within-epistemology edges only;
   re-derive at query time and record the actual N in the evidence file's sample
   metadata. Cross-bridges are excluded (covered by AUDIT-CB).
2. Sample selection: deterministic md5(seed='AUDIT-EPI' || source_id || '|' ||
   target_id) ordering across the population, then take the first 25.
3. Node sample: union of the sampled edges' source/target node_ids filtered to
   `domain=epistemology` (or specialized epistemology, per the live schema),
   ordered by md5(seed='AUDIT-EPI' || node_id), first 12.
4. For each sampled edge: apply the verbatim master-plan §"Per-edge prompt
   template" with verdict ∈ {sound, defensible, reversed, weak, historical,
   thematic, other} and confidence ∈ {high, medium, low}.
5. For each sampled node: apply the verbatim master-plan §"Per-node prompt
   template" with verdict ∈ {sound, granularity-mismatch, authenticity, other}.
6. Record findings in the schema's named sections.
7. Within-session sample expansion rule (master-plan §"Sample-size policy"):
   if the defect rate at half-sample (after 13 of 25 edges reviewed) exceeds
   60%, expand to 50% density (≈36 edges) before commit. Halt expansion at 50%.
8. Cross-cutting observations: brief, only load-bearing aggregate patterns
   (per master-plan §T2-D — closeout synthesizes; routine session records
   sparingly).
9. Pre-listed audit-system-input proposals (master-plan §"Audit-system-input
   proposals") are skipped per master-plan instruction; record any *new*
   gate-feasible class as an "other" verdict-NOTES finding.

## Verification at close

- File exists at the criterion path with the schema's required sections
  populated.
- `validate.py` exits without hard-fails on the eager-claim commit, the
  deliverable commit, and the close commit.
- `check_target.py --task-id AUDIT-EPI` returns PASS for both criteria.

## Scope-lock affirmation

The active task's `scope_lock.allowed_paths` is
`engine/build_readiness/phase_5_production_audit_evidence/epistemology.md`
(single entry). The plan's `paths_to_modify` is the same single entry. The
operational allowlist (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md)
and CLAUDE.md "Routine-mode posture") covers session-apparatus files at
commit-time. No other tracked files are modified by this session.
