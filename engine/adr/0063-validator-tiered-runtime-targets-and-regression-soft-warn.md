# ADR 0063 — Validator tiered runtime targets + per-phase regression soft-warn

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0126

## Context

[`engine/operations/health-check.md`](../operations/health-check.md) and [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) historically documented a single `< 500ms` validator runtime target. That target was authored before [ADR 0016](0016-graph-construction-needs-live-validation.md) added the live-DB graph audit at Phase 4. Post-Phase-4, validator runtime is dominated by the graph-audit phase's DB round-trip; total runtime is ~4–5s on a healthy run. Reading the unitary `< 500ms` target after the Phase 4 addition makes a healthy state look like a regression.

The [S-0121 cadence-fired audit](../../docs/health-checks/S-0121.md) surfaced this as Retire-D: the unitary target was retire-recommend, replaced with a tiered shape that names the structural-only phase and the live-DB phase separately so each can be evaluated on its own scale. The user adjudicated ACCEPT at S-0125.

A correlated gap: the prior `validate-history.jsonl` schema carried a single `duration_ms` field per record; no per-phase timing was captured, so cross-session regression analysis could not distinguish a 5-second total dominated by structural-phase regression from one dominated by graph-audit-phase regression. The audit also recommended per-phase instrumentation as the input to any future regression-detection signal.

## Decision

Three coupled changes mechanize the audit's recommendations at S-0126.

### 1. Tiered runtime targets

[`engine/operations/health-check.md`](../operations/health-check.md) Validator-telemetry section and [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) Response-posture section name four targets:

- **Structural phase** (in-process file/regex checks; no DB consultation, no subprocess probes) — **< 500ms**.
- **Health-probe phase** (external-subprocess probes: chromadb open via `probe_palace.py`, repo state via `probe_repo.py`, GitHub Issues via `gh issue list`) — **< 5s**.
- **Graph audit phase** (live-DB consultation per [ADR 0016](0016-graph-construction-needs-live-validation.md)) — **< 5s**.
- **Total runtime** — **< 11s** (sum of phases plus a ~500ms buffer for `--final-check` shutdown audits + bookkeeping).

The original `< 500ms` target survives in the structural-phase budget — that scope retains its honest meaning. The health-probe phase budget reflects the chromadb `PersistentClient` open cost (subprocess + index load); the graph audit phase budget reflects Phase 4's load-bearing live-DB cost. The total budget caps the whole pipeline.

### 2. Per-phase timing instrumentation

[`engine/tools/validate.py`](../tools/validate.py) `main()` is structured to capture four durations at phase boundaries:

- `duration_structural_ms` — from start through `validate_handoff_long_resolved_sections()` (the last in-process structural check).
- `duration_health_probe_ms` — `validate_shared_state_health()` (subprocess probes against `probe_palace.py` + `probe_repo.py`) + `validate_issue_collisions()` (subprocess `gh issue list` to GitHub).
- `duration_graph_audit_ms` — `validate_graph()` only.
- `duration_total_ms` — start through end, inclusive of `--final-check` shutdown audits when set.

Each `validate-history.jsonl` record gains all four fields. The prior single `duration_ms` field was renamed cleanly to `duration_total_ms` at the original landing (no back-compat shim in writers — per the feedback memory against backwards-compat hacks). [`engine/tools/health_check.py`](../tools/health_check.py)'s reader accepts both legacy single-field and current four-field shapes so cross-history summarization works without manual cleanup.

Per-phase fields are emitted only by the default-mode pipeline; `--code-gates`, `--sql-gates`, `--health-probe-only`, and `--export-snapshot` skip the four-phase split (those modes don't run the full pipeline; their durations against the tiered targets would mislead) and emit only `duration_total_ms`.

### 3. Per-phase regression soft-warn

[`engine/tools/validate.py`](../tools/validate.py) function `validate_runtime_phase_regression()` reads the last entries of `validate-history.jsonl`, filters to entries carrying every per-phase field declared in `VALIDATOR_PHASE_TARGETS_MS` (skipping legacy entries that pre-date the current schema), and emits a `validator_runtime_phase_regression` soft-warn for any phase whose duration exceeds `1.5 × tiered target` across **3 consecutive runs**. The current run's tentative timings participate in the rolling window — the soft-warn fires on the third sustained-breach run, not the run after it.

Adding a phase to `VALIDATOR_PHASE_TARGETS_MS` automatically extends the regression check to that phase. The qualifying-entry filter is keyed off the dict keys (not a hard-coded triple), so the function picks up new phases without code change. New entries from after a phase addition include the new field; older entries are skipped (insufficient per-phase fields).

Conservative thresholding: 1.5× is wide enough to filter single-run noise; 3 consecutive runs requires sustained breach, not a one-off spike. If false-positives surface in the first 5–10 sessions of natural exercise, adjust `_REGRESSION_BREACH_MULTIPLIER` or `_REGRESSION_RUN_WINDOW` with evidence; the steady-state shift hypothesis (e.g., new infrastructure raises a phase's baseline) is also legitimate grounds for adjusting `VALIDATOR_PHASE_TARGETS_MS` itself.

The category participates in the standard archive surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md); no schema change (the `soft_warns` dict accepts arbitrary category names). Documented in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md).

### 4. First-exercise readiness note

Per [ADR 0053](0053-mechanism-first-exercise-gate.md). Authored at [`engine/build_readiness/validator_runtime_phase_regression_first_exercise.md`](../build_readiness/validator_runtime_phase_regression_first_exercise.md). T1-A closes when the validator naturally surfaces the soft-warn (sustained 1.5× breach across 3 runs).

## Consequences

- The audit's diagnosis is correct on the live repo: structural phase clears < 500ms; health-probe phase reflects bounded chromadb-open cost; graph audit consumes the bulk of database time; total stays under 11s. The tiered shape reads as descriptive, not aspirational.
- Per-phase fields enable cross-session regression analysis. Health-check audits per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) consume the structured fields; the validator-freshness probe at the Fit posture can distinguish *which* phase is degrading rather than reporting an aggregate.
- The 1.5× / 3-run threshold is a conservative starting point. If exercise produces false-positives, the readiness-note T1-B criterion (post-first-fire investigation) feeds the threshold adjustment.
- `validate-history.jsonl` is gitignored per-clone. Pre-S-0126 entries in any clone carry `duration_ms` only; pre-S-0127 entries carry the three-phase schema (no `duration_health_probe_ms`); the regression check skips both gracefully (insufficient per-phase fields), and the health-check reader accepts the legacy single-field shape for total-runtime summarization. New entries from S-0127 forward carry the four-phase shape.
- `--code-gates` / `--sql-gates` / `--health-probe-only` / `--export-snapshot` modes are not subjected to the per-phase targets (their pipelines are different). Their records carry `duration_total_ms` only.
- The S-0121 audit's Retire-D recommendation is closed: the unitary `< 500ms` target is retired; the tiered shape replaces it; per-phase timing lands; the regression soft-warn is the gate-side mechanization of the audit-side "runtime drift" telemetry recommendation.
- **S-0127 (Issue #90) — health-probe phase split.** The regression soft-warn first-fire at S-0126 surfaced sustained `duration_structural_ms` breach (~3700ms median, well above the 750ms 1.5× threshold). Investigation showed `validate_shared_state_health()` — invoked inside the structural phase but spawning subprocess probes including a chromadb `PersistentClient` open — was the dominant contributor (~3500ms of the structural total). After moving it out, the structural phase still showed ~1200ms because `validate_issue_collisions()` was also running in the structural phase and shells out to `gh issue list` (~700ms; network-bound and variable). Both subprocess probes moved into the new `health_probe` phase in the same fold. The right resolution was not to bump the structural target (would mask future regressions in the genuinely fast in-memory checks) but to recognize that "subprocess to live external system" is a categorically different kind of work than "in-memory file/regex check." The four-phase model with the ~5s health_probe budget reflects that. Path B per the readiness note T1-B (phase boundary correction with evidence), not Path A (chromadb / gh themselves can't be meaningfully optimized) and not the threshold-adjustment fallback. Verification: post-fix structural phase ~415ms; health_probe ~3550ms; total ~5260ms — all clean against the four-phase tiered targets. Closes [Issue #90](https://github.com/StarshipSuperjam/paideia/issues/90); closes T1-B in the readiness note.

## See also

- [ADR 0016](0016-graph-construction-needs-live-validation.md) — the live-DB consultation contract that drove the runtime increase post-Phase-4 and motivates the graph-audit-phase budget.
- [ADR 0022](0022-periodic-project-health-checks.md) — health-check cadence consumer of `validate-history.jsonl`.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; `validator_runtime_phase_regression` participates in the standard surface.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; the regression soft-warn carries a readiness note.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — the adversarial-stance audit posture that surfaced this work at S-0121.
- [Issue #88](https://github.com/StarshipSuperjam/paideia/issues/88) — closes (original tiered-target work at S-0126).
- [Issue #90](https://github.com/StarshipSuperjam/paideia/issues/90) — closes (S-0127 health-probe phase split).
- `docs/health-checks/S-0121.md` — audit source.
- [`engine/operations/health-check.md`](../operations/health-check.md) Validator-telemetry section — tiered-target prose.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category entry + Response-posture budget.
- [`engine/build_readiness/validator_runtime_phase_regression_first_exercise.md`](../build_readiness/validator_runtime_phase_regression_first_exercise.md) — first-exercise readiness note.
