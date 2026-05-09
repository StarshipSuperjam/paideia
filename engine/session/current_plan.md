paths_to_modify: ["engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md"]
criteria_addressed: [0, 1]

# Plan — S-0104 (routine) — T-PHASE-5-AUDIT / AUDIT-CB

This routine session executes T-PHASE-5-AUDIT task `AUDIT-CB`: cross-bridge full census (all 71 cross-domain edges) — SEP-anchored review per the master-plan prompt template at `engine/build_readiness/phase_5_production_audit.md`.

The single deliverable is `engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md`, populated with verdict + SEP-anchored reasoning + confidence per edge per the fixed schema in the master plan §"Evidence file schema".

## Why these paths address the criteria

- **`file_exists` criterion** (path: `engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md`) — the deliverable IS the file at the criterion's path; populating it satisfies the criterion directly.
- **`validate_passes` criterion** — committing the file routes through the pre-commit hook including `validate.py`; absence of hard-fails satisfies the criterion.

## Execution shape

1. Confirm the 71-edge inventory by reading `product/seed-graph/migrations/0060_seed_crossbridges_part1.sql` (already done at boot; inventory matches the master-plan figure).
2. Apply the per-edge SEP-anchored prompt template (master-plan §"Per-edge prompt template") to each of the 71 edges in document order matching the migration's groupings (A1 service formal-logic primitives → philosophy 15 edges; A2 service math prerequisites → philosophy 12 edges; A3 service history terminators → philosophy 18 edges; B within-philosophy cross-subdomain 26 edges).
3. Record each finding in the schema's "Sampled-edge candidate findings" section as `Finding E-N` with EDGE / SEP-ANCHORED REASONING / VERDICT / CONFIDENCE / NOTES.
4. Cross-bridges are exempt from per-edge node sampling per the master-plan §"Sample-size policy" (cross-bridges have no nodes; node coverage is via the subdomain tasks). The "Sampled-node candidate findings" section is included as schema-required and marked "N/A — cross-bridges have no node sample".
5. Author a brief "Cross-cutting observations" section noting only the load-bearing aggregate patterns the closeout will need (defect rate, historical-not-pedagogical density, any reversal patterns). Treat sparingly per master-plan §T2-D.
6. Within-session sample expansion rule (master-plan §T2-A) is **not applicable**: AUDIT-CB is full-census (100% density), so the >60% mid-sample expansion trigger has no analog. The aggregate defect rate calibrates whether downstream subdomain tasks expand from 35% → 50% per the within-session expansion rule; that decision is recorded in the closeout, not here.
7. Pre-listed audit-system-input proposals (master-plan §"Audit-system-input proposals") are skipped per master-plan instruction; record any *new* gate-feasible class as an "other" verdict-NOTES finding.

## Calibration role

This task is the calibration set for the larger 11-task batch. The S-0081 gate's 15-edge sample produced 8 substantive findings (53%); the full census reveals whether the gate's defect rate generalizes across the 71-edge population. Downstream subdomain tasks read this file's defect rate at their own boot (via the closeout's interim guidance, not at routine-fire time — closeout is interactive and runs after AUDIT-HT).

## Verification at close

- File exists at the criterion path with the schema's required sections populated.
- `validate.py` exits without hard-fails on the eager-claim commit + the deliverable commit + the close commit.
- `check_target.py --task-id AUDIT-CB` returns PASS for both criteria.

## Scope-lock affirmation

The active task's `scope_lock.allowed_paths` is `engine/build_readiness/phase_5_production_audit_evidence/crossbridges.md` (single entry). The plan's `paths_to_modify` is the same single entry. The operational allowlist (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) and CLAUDE.md "Routine-mode posture") covers session-apparatus files commit-time. No other tracked files are modified by this session.
