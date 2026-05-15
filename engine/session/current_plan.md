paths_to_modify: ["engine/build_readiness/seed_qa_findings.md"]
criteria_addressed: [0, 1]

# SQA-20 closeout — T-SEED-QA census aggregation

Aggregate the 19 shard evidence files (`engine/build_readiness/seed_qa_evidence/shard_01.md` through `shard_19.md`) into a single closeout findings document at `engine/build_readiness/seed_qa_findings.md`. Scope-locked to that single file per the task's `scope_lock.allowed_paths`.

## Aggregation mandate (per seed_qa_audit.md "Closeout" section)

The closeout must produce, and only produce:

1. **Overall C1 / C2 / C3 error rates** across the full 19-shard census (515 edges, 380 nodes — 1 edge omitted from partitioning per the shards.json sharding tool).
2. **Per-subdomain breakdown** — every edge and node carries domain tags; rates can be cut by subdomain.
3. **C1 drift comparison** vs the production audit's 13% baseline (the audit findings live at `engine/build_readiness/phase_5_production_audit_findings.md`).
4. **Pattern clusters** — the dominant verdict shapes (Defensible sub-taxonomy across shards 04–19; Reversed cluster in shards 01–08; in-shard semantic clusters worth flagging).
5. **A "for Phase 6 self-correction" section** — what the rates and patterns imply for the self-correction pipeline's calibration (per [ADR 0014](../../product/adr/0014-sonnet-teaches-opus-reviews.md), Phase 6's tension log + Opus batch review).

The closeout is **aggregation only**. Disposition — filing Issues, authoring ADR memos, proposing migration corrections — is a follow-up interactive session, matching the production audit's anti-scope.

## Data the closeout reads

- The 19 per-shard evidence files at `engine/build_readiness/seed_qa_evidence/shard_NN.md` (each contains its tally table + cross-cutting observations).
- The two re-audit methodology checks at `shard_01_reaudit.md` (S-0165) and `shard_04_reaudit.md` (S-0165). Both re-audits AGREE with their originals' C1 / C2 / C3 verdicts; the original tallies stand. The closeout notes that the re-audits validated the routine batch's scoring against full SEP-anchored adversarial methodology.
- The pinned rubric at `engine/build_readiness/seed_qa_audit.md` (especially the 13% production-audit baseline framing and the per-criterion definitions).
- The production audit findings at `engine/build_readiness/phase_5_production_audit_findings.md` for the 13% baseline number and the subdomain breakdown the closeout's drift comparison runs against.

## Headline numbers (pre-computed from diary entries S-0163 → S-0181)

- **C1 cumulative across shards 01–19:** 23 defectives / 515 edges = **4.47%** — materially below 13% production-audit baseline.
- **C1 by shard (01–19):** 10.7% / 3.6% / 3.6% / 0.0% / 3.7% / 0.0% / 0.0% / 3.7% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0% / 0.0%.
- **C2 cumulative:** 0 / 380 = **0%** (every node carries substantive teaching_notes; the census's most stable criterion).
- **C3 cumulative:** 0 / 380 = **0%** (no jargon-gated / circular / assumes-the-concept failures; ~7 borderline-PASS calls held per established calibration anchors across the 19-shard batch).
- **Defectives concentrated in shards 01–09:** 3+1+1+0+1+0+0+1+0 = 6 defectives / 217 edges (2.8% in the early shards); shards 10–19 have ZERO defectives across 298 edges (10 consecutive 0-defect shards — the census's longest run).
- **Total edge partition:** 515 scored / 516 `pedagogical_prerequisite` edges in the graph (>99.8% coverage). The 17 `historical_influence` edges are out of scope per the rubric.

## Rationale for the single deliverable

Writing the single file `seed_qa_findings.md` is exactly what criterion `file_exists` checks (criterion 0); `validate_passes` (criterion 1) requires the validator to report no hard-fails — which the scope-locked single-file write naturally satisfies as long as the file is added under the operational allowlist. The two criteria together are the task's completion gate; no other paths are required.

The aggregation is mechanical synthesis from the 19 evidence files plus the diary entries' cross-shard observations. Per-subdomain breakdown will be computed by counting edges and nodes in each domain tag across the shard tables. The drift comparison reads the production audit's findings document for the baseline. Pattern clusters draw on the Defensible sub-shape taxonomy diary entries S-0163 through S-0181 have been building toward this closeout.

## Out of scope

- No edits to `product/seed-graph/migrations/` (per the rubric's anti-scope on migration changes).
- No Issue filing for the C1 defectives (per the rubric's anti-scope on disposition — that's a follow-up interactive session's job).
- No ADR drafts (same).
- No proposals to change the validator (same).
- The closeout does not adjudicate the Defensible-shape taxonomy beyond enumeration — adjudication is a disposition decision.
