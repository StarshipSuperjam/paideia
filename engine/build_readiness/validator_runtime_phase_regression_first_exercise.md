# Validator runtime phase regression — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the `validator_runtime_phase_regression` soft-warn landed at S-0126 per [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) (Issue [#88](https://github.com/StarshipSuperjam/paideia/issues/88)).

## Mechanism

`engine/tools/validate.py` `validate_runtime_phase_regression()` reads the last entries of `engine/tools/validate-history.jsonl`, filters to entries carrying the three per-phase fields (`duration_structural_ms`, `duration_graph_audit_ms`, `duration_total_ms`), and fires a `validator_runtime_phase_regression` soft-warn for any phase whose duration exceeds `1.5 × VALIDATOR_PHASE_TARGETS_MS[phase]` across the last 3 consecutive runs.

Tiered targets (per ADR 0063):

- `duration_structural_ms` — 500ms (1.5× threshold: 750ms)
- `duration_graph_audit_ms` — 5000ms (1.5× threshold: 7500ms)
- `duration_total_ms` — 6000ms (1.5× threshold: 9000ms)

The current run's tentative timings participate in the rolling window: the soft-warn fires on the *third* sustained-breach run, not the run after it.

## Readiness criteria

- **T1-A** — validator naturally surfaces the soft-warn (sustained 1.5× breach across 3 consecutive runs against a real codebase, not a synthetic test fixture).
- **T1-B** — the surfaced phase is investigated and either (a) the regression is real and addressed at the hot path, or (b) the threshold is judged too aggressive and adjusted with evidence (e.g., new infrastructure raised structural-phase steady-state; live-DB load increased after a graph expansion).
- **T1-C** — if the threshold is adjusted, the adjustment is committed with the evidence in the commit message and reflected in `VALIDATOR_PHASE_TARGETS_MS` and `_REGRESSION_BREACH_MULTIPLIER` / `_REGRESSION_RUN_WINDOW` as appropriate; the ADR 0063 Consequences section is not amended (the contract holds; the operational threshold shifts).

## Status

- **Open.** Awaits first natural exercise. Synthetic tests at [`engine/tools/test_validate.py`](../tools/test_validate.py) `TestValidateRuntimePhaseRegression` confirm the mechanism fires correctly on synthetic-fixture inputs (9 tests, all green).

## Cross-references

- [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — the contract.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category entry under `### \`validator_runtime_phase_regression\``.
- [`engine/operations/health-check.md`](../operations/health-check.md) — Validator-telemetry section names the tiered targets.
- [Issue #88](https://github.com/StarshipSuperjam/paideia/issues/88) — source.
