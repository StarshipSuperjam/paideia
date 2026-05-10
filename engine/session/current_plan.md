paths_to_modify: ["engine/build_readiness/phase_5_production_audit_evidence/ethics.md"]
criteria_addressed: [0, 1]

# Plan — S-0108 (routine) — T-PHASE-5-AUDIT / AUDIT-ETH

This routine session executes T-PHASE-5-AUDIT task `AUDIT-ETH`: ethics subdomain
audit — SEP-anchored review of a 35%-density edge sample (k=24 of N=68) plus an
edge-anchored node sample (~12 unique nodes), per the master-plan prompt templates
at `engine/build_readiness/phase_5_production_audit.md`.

The single deliverable is
`engine/build_readiness/phase_5_production_audit_evidence/ethics.md`, populated
with verdict + SEP-anchored reasoning + confidence per edge and per node per the
fixed schema in the master plan §"Evidence file schema".

## Why these paths address the criteria

- **`file_exists` criterion** (path:
  `engine/build_readiness/phase_5_production_audit_evidence/ethics.md`) — the
  deliverable IS the file at the criterion's path; populating it satisfies the
  criterion directly.
- **`validate_passes` criterion** — committing the file routes through the
  pre-commit hook including `validate.py`; absence of hard-fails satisfies the
  criterion.

## Execution shape

1. Read the ethics within-domain edge population from the two seed migrations:
   `0020_seed_ethics_part1.sql` (34 edges, metaethics + normative theory) and
   `0026_seed_ethics_part1.sql` (34 edges, applied ethics). Total N=68 — matches
   the master-plan figure. Live-DB read denied in routine mode per ADR 0055; the
   migrations are the canonical authoring record applied verbatim to production.
2. Sample selection: deterministic md5(seed='AUDIT-ETH' || source_id || '|' ||
   target_id) ordering across the 68-edge population, take first 24 (35.3% density).
3. Node sample: union of the 24 sampled edges' source/target node_ids, ordered
   by md5(seed='AUDIT-ETH' || node_id), take first 12.
4. For each sampled edge: apply the verbatim master-plan §"Per-edge prompt
   template" with verdict ∈ {sound, defensible, reversed, weak, historical,
   thematic, other} and confidence ∈ {high, medium, low}.
5. For each sampled node: apply the verbatim master-plan §"Per-node prompt
   template" with verdict ∈ {sound, granularity-mismatch, authenticity, other}.
6. Record findings in the schema's named sections.
7. Within-session sample expansion rule (master-plan §"Sample-size policy"):
   if the defect rate at half-sample (after 12 of 24 edges reviewed) exceeds
   60%, expand to 50% density (≈34 edges) before commit. Halt at 50%. S-0105
   epistemology returned 5.4% — within-subdomain expansion not expected to fire.
8. Cross-cutting observations: brief, only load-bearing aggregate patterns
   (per master-plan §T2-D — closeout synthesizes; routine session records
   sparingly).
9. Pre-listed audit-system-input proposals (master-plan §"Audit-system-input
   proposals") are skipped per master-plan instruction; record any *new*
   gate-feasible class as an "other" verdict-NOTES finding.
10. Empirical-fortification branch is **not** invoked — the master-plan
    routine-mode prohibition is load-bearing until the closeout closes T1-A
    through T1-D in `fetch_structural_reference_first_exercise.md`. This session
    is parametric-only; medium-confidence + mutation-implying verdicts get
    fortified at the closeout interactive session.

## Verification at close

- File exists at the criterion path with the schema's required sections
  populated.
- `validate.py` exits without hard-fails on the eager-claim commit, the
  deliverable commit, and the close commit.
- `check_target.py --task-id AUDIT-ETH` returns PASS for both criteria.

## Scope-lock affirmation

The active task's `scope_lock.allowed_paths` is
`engine/build_readiness/phase_5_production_audit_evidence/ethics.md` (single
entry). The plan's `paths_to_modify` is the same single entry. The operational
allowlist (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) and
CLAUDE.md "Routine-mode posture") covers session-apparatus files at commit-time.
No other tracked files are modified by this session.
