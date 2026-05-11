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

[`engine/operations/health-check.md`](../operations/health-check.md) Validator-telemetry section and [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) Response-posture section name three targets:

- **Structural phase** (in-process file/regex checks; no DB consultation) — **< 500ms**.
- **Graph audit phase** (live-DB consultation per [ADR 0016](0016-graph-construction-needs-live-validation.md)) — **< 5s**.
- **Total runtime** — **< 6s**.

The original `< 500ms` target survives in the structural-phase budget — that scope retains its honest meaning. The graph audit phase gets its own budget reflecting Phase 4's load-bearing live-DB cost. The total budget caps the whole pipeline including any optional `--final-check` shutdown audits.

### 2. Per-phase timing instrumentation

[`engine/tools/validate.py`](../tools/validate.py) `main()` is refactored to capture three durations at phase boundaries:

- `duration_structural_ms` — from start through `validate_timestamp_helper_bypass()` (the last structural call).
- `duration_graph_audit_ms` — `validate_graph()` only.
- `duration_total_ms` — start through end, inclusive of `--final-check` shutdown audits when set.

Each `validate-history.jsonl` record gains all three fields. The prior single `duration_ms` field is renamed cleanly to `duration_total_ms` (no back-compat shim in writers — per the feedback memory against backwards-compat hacks). [`engine/tools/health_check.py`](../tools/health_check.py)'s reader accepts both shapes so cross-S-0126 history is summarized without manual cleanup.

Per-phase fields are emitted only by the default-mode pipeline; `--code-gates`, `--sql-gates`, `--health-probe-only`, and `--export-snapshot` skip the structural/graph split (those modes don't run the full pipeline; their durations against the tiered targets would mislead) and emit only `duration_total_ms`.

### 3. Per-phase regression soft-warn

A new [`engine/tools/validate.py`](../tools/validate.py) function `validate_runtime_phase_regression()` reads the last entries of `validate-history.jsonl`, filters to entries carrying the per-phase fields, and emits a `validator_runtime_phase_regression` soft-warn for any phase whose duration exceeds `1.5 × tiered target` across **3 consecutive runs**. The current run's tentative timings participate in the rolling window — the soft-warn fires on the third sustained-breach run, not the run after it.

Conservative thresholding: 1.5× is wide enough to filter single-run noise; 3 consecutive runs requires sustained breach, not a one-off spike. If false-positives surface in the first 5–10 sessions of natural exercise, adjust `_REGRESSION_BREACH_MULTIPLIER` or `_REGRESSION_RUN_WINDOW` with evidence; the steady-state shift hypothesis (e.g., new infrastructure raises structural-phase baseline) is also legitimate grounds for adjusting `VALIDATOR_PHASE_TARGETS_MS` itself.

The category participates in the standard archive surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md); no schema change (the `soft_warns` dict accepts arbitrary category names). Documented in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md).

### 4. First-exercise readiness note

Per [ADR 0053](0053-mechanism-first-exercise-gate.md). Authored at [`engine/build_readiness/validator_runtime_phase_regression_first_exercise.md`](../build_readiness/validator_runtime_phase_regression_first_exercise.md). T1-A closes when the validator naturally surfaces the soft-warn (sustained 1.5× breach across 3 runs).

## Consequences

- The audit's diagnosis is correct on the live repo: structural phase clears < 500ms; graph audit consumes the bulk of runtime; total stays under 6s. The tiered shape now reads as descriptive, not aspirational.
- Per-phase fields enable cross-session regression analysis. Health-check audits per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) consume the structured field; the validator-freshness probe at the Fit posture can now distinguish *which* phase is degrading rather than reporting an aggregate.
- The 1.5× / 3-run threshold is a conservative starting point. If exercise produces false-positives, the readiness-note T1-B criterion (post-first-fire investigation) feeds the threshold adjustment.
- `validate-history.jsonl` is gitignored per-clone. Pre-S-0126 entries in any clone carry `duration_ms` only; the regression check skips them gracefully (insufficient per-phase fields), and the health-check reader accepts both for total-runtime summarization. New entries from S-0126 forward carry the new shape.
- `--code-gates` / `--sql-gates` / `--health-probe-only` / `--export-snapshot` modes are not subjected to the per-phase targets (their pipelines are different). Their records carry `duration_total_ms` only.
- The S-0121 audit's Retire-D recommendation is closed: the unitary `< 500ms` target is retired; the tiered shape replaces it; per-phase timing lands; the regression soft-warn is the gate-side mechanization of the audit-side "runtime drift" telemetry recommendation.

## See also

- [ADR 0016](0016-graph-construction-needs-live-validation.md) — the live-DB consultation contract that drove the runtime increase post-Phase-4 and motivates the graph-audit-phase budget.
- [ADR 0022](0022-periodic-project-health-checks.md) — health-check cadence consumer of `validate-history.jsonl`.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; `validator_runtime_phase_regression` participates in the standard surface.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; the regression soft-warn carries a readiness note.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — the adversarial-stance audit posture that surfaced this work at S-0121.
- [Issue #88](https://github.com/StarshipSuperjam/paideia/issues/88) — closes.
- `docs/health-checks/S-0121.md` — audit source.
- [`engine/operations/health-check.md`](../operations/health-check.md) Validator-telemetry section — tiered-target prose.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category entry + Response-posture budget.
- [`engine/build_readiness/validator_runtime_phase_regression_first_exercise.md`](../build_readiness/validator_runtime_phase_regression_first_exercise.md) — first-exercise readiness note.
