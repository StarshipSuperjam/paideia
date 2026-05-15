# Recall-substrate fix campaign — mechanism-first-exercise gate report

> Authored by S-0185 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first exercise of the A1-PROPER fix campaign that [ADR 0090](../adr/0090-phase-6-recall-substrate-decision.md) commits to. Required because the ADR's Decision section qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files — this ADR's Consequences touch ADR 0090 + ADR 0056 + ADR 0057 + ADR 0079 + `engine/operations/mempalace-operations.md` + the first-exercise note itself = 6 surfaces).

## Mechanism summary

[ADR 0090](../adr/0090-phase-6-recall-substrate-decision.md) preserves MemPalace as the durable semantic-memory substrate via six commitments:

1. **Empirical re-verification first** — probe current mempalace 3.3.5 behavior against the project's actual palace against the three S-0184 modes (HNSW UNKNOWN; wing-filter throws; BM25 mining pollution).
2. **Maintenance for confirmed-broken gaps** — scheduled `mempalace_rebuild_hnsw.py` (Mode 1); one-time-or-recurring `prune_mempalace.py --audit-orphan-wings --apply` (Mode 3); conditional ADR 0057 element 4 contract refinement (Mode 2, only if verification warrants).
3. **Upstream coordination** — monitor MemPalace/mempalace Issues #1082 / #1398 / #1489 and PRs #1463 / #1511 / #1452 / #1428; retire workarounds as upstream fixes land.
4. **Empirical investigation of ADR 0079's falsified recurrence interval** — find out why HNSW UNKNOWN recurred at 39 sessions vs ≥150 expected.
5. **Substrate preserved** — capture surface (Stop/PreCompact hooks, `mempalace_add_drawer`, `mempalace_diary_*`) continues unchanged.
6. **Open future option** — A3 (Postgres + pgvector substrate replacement) stays open under named conditions.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No (refines existing session lifecycle around an existing substrate) |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | No new category authored. Existing categories (`mempalace_hnsw_status_suspect`, `mempalace_wing_count_growth`, `mempalace_zero_citations_after_search`) remain as configured. |
| #3 — introduces a new state file the boot procedure reads | No (consumes existing register_state.json + current.json) |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | **Yes** (6 surfaces: ADR 0090 + ADR 0056 + ADR 0057 + ADR 0079 + `mempalace-operations.md` + the first-exercise note). The S-0187+ wiring also touches `session-shutdown-sequence.md` and potentially `health_check.py` — those are deferred deliverables under the ADR's Consequences but they will count when the wiring lands. |

**Qualifies; first-exercise readiness criteria below.**

## Tier 1 readiness criteria (must close before unattended use)

| ID | Criterion | Status |
|---|---|---|
| **T1-A** | Empirical re-verification completes (ADR 0090 commitment 1). Each of the three S-0184 modes has a documented probe + observed result against current mempalace 3.3.5 + the project's actual palace. Verification report lands at `engine/docs/audits/mempalace_state_S-0186.md` (or equivalent). | **OPEN.** Targeted for S-0186 (next interactive session). |
| **T1-B** | ADR 0079 recurrence-interval investigation completes (ADR 0090 commitment 4). Persist-condition probe, threshold-channel verification, write-path distribution between drawers/closets collections — all documented. Findings inform the rebuild-cadence decision under commitment 2a. May produce an ADR 0079 amendment or follow-up ADR. | **OPEN.** Targeted for S-0186 (concurrent with T1-A; same probing session). |
| **T1-C** | First confirmed-broken-mode mitigation wired successfully (ADR 0090 commitment 2). Specifically: if T1-A surfaces Mode 1 as broken at our scale, the scheduled rebuild wiring lands in session-shutdown-sequence (or whichever cadence the investigation recommends). If Mode 3 broken, one-time prune executes. If Mode 2 broken, ADR 0057 element 4 in-body amendment lands. At least one mitigation must successfully execute end-to-end. | **OPEN.** Targeted for S-0187+ post-verification. |
| **T1-D** | Upstream coordination process documented (ADR 0090 commitment 3). `engine/operations/mempalace-operations.md` gains a "Upstream coordination" subsection naming the watch-list (Issues #1082 / #1398 / #1489; PRs #1463 / #1511 / #1452 / #1428) and the retire-workaround pattern. | **OPEN.** Lands alongside the operational wiring in S-0187+. |

## Tier 2 readiness criteria (settle in advance, document)

- **T2-A — Scheduled-rebuild cadence selection.** The default is per-shutdown (~30s overhead per session). Per-N-sessions is the alternative if per-shutdown shows material session-friction at first exercise. The decision is informed by T1-B (the recurrence-interval investigation). If the investigation shows a deeper bug at the persist condition (e.g., the threshold IS being met but `_persist()` is silently failing), the scheduled-rebuild approach may itself be insufficient and a different mitigation shape is warranted.
- **T2-B — Prune cadence selection.** If T1-A Mode 3 verification shows PR #1424's `_wing_from_transcript_path` improvement is active and recent sessions land in `paideia` properly, the prune is one-shot historical cleanup, not recurring. If new per-worktree wings accumulate post-#1424, a recurring schedule is warranted until PR #1511's `MEMPALACE_WING` env var override merges and is wired into the hook.
- **T2-C — Mode 2 conditional contract refinement.** If T1-A Mode 2 verification shows wing-filter works at our 22K-drawer scale post-mempalace 3.3.5, ADR 0057 element 4 needs no refinement; the bug is upstream-tracked at Issue #1082 and out-of-scope at our scale. If broken, the element 4 amendment per ADR 0090 commitment 2c lands.
- **T2-D — Upstream-coordination drift risk.** The upstream-coordination posture is posture-not-machinery. Drift risk: a session may forget to check upstream status, and the project's workarounds compound. Sunset criterion per ADR 0090 Consequences: three consecutive health-check audits report no MemPalace-substrate findings AND ≥1 workaround retired. If sunset criterion not met by S-0245 (cadence-20 audit), reconsider the posture.

## Tier 3 readiness criteria (refinements over time)

- **T3-A — A3 reconsideration triggers.** Per ADR 0090 commitment 6: Phase 6 partition machinery lands at scale AND decision_embeddings marginal cost is small → reconsider. OR 60 sessions pass without upstream convergence AND workaround cost is unaffordable → reconsider. Either trigger fires → new ADR supersedes or amends ADR 0090.
- **T3-B — Operational-doc cross-references.** `engine/operations/mempalace-operations.md` "Maintenance probes" subsection gains entries for the new scheduled rebuild and (if applicable) the scheduled prune. `engine/operations/cross-references.md` gains ADR 0090's outgoing edges to ADRs 0056 / 0057 / 0079 + ops-doc consumers.

## Pre-S-0185 audit (per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md))

Per ADR 0053's "readiness note before unattended use" framing: this fix campaign is NOT routine-fired; the S-0186 verification + investigation work happens in interactive build sessions. The first-exercise gate's "before unattended use" caveat applies to the *scheduled-rebuild* and *scheduled-prune* wirings (commitment 2a and 2b), which will run under the session-close hook regardless of interactive vs routine. Tier 1 readiness specifically protects those wirings from landing before verification proves them needed and the investigation proves them appropriately-shaped.

## Cross-references

- [ADR 0090](../adr/0090-phase-6-recall-substrate-decision.md) — the substrate decision this note covers.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the first-exercise rubric this note evaluates against.
- [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) — the mechanical-adoption-check layer the substrate decision preserves.
- [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) — element 4's cluster-reading workflow whose conditional refinement T2-C tracks.
- [ADR 0079](../adr/0079-hnsw-sync-threshold-tuning.md) — the prior fix campaign T1-B investigates.
- [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — Mode 1 mitigation tool.
- [`engine/tools/prune_mempalace.py`](../tools/prune_mempalace.py) — Mode 3 mitigation tool.
- [`engine/tools/mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) — Mode 1 bridge tool (retires when upstream Issue #1489 lands).
- [`docs/health-checks/S-0184.md`](../../docs/health-checks/S-0184.md) — the audit that surfaced finding A.
- [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) — closes (the ADR's filing).
