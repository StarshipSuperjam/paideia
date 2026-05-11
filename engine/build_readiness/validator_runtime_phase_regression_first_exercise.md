# Validator runtime phase regression — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the `validator_runtime_phase_regression` soft-warn landed at S-0126 per [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) (Issues [#88](https://github.com/StarshipSuperjam/paideia/issues/88), [#90](https://github.com/StarshipSuperjam/paideia/issues/90)).

## Mechanism

`engine/tools/validate.py` `validate_runtime_phase_regression()` reads the last entries of `engine/tools/validate-history.jsonl`, filters to entries carrying every per-phase field declared in `VALIDATOR_PHASE_TARGETS_MS`, and fires a `validator_runtime_phase_regression` soft-warn for any phase whose duration exceeds `1.5 × VALIDATOR_PHASE_TARGETS_MS[phase]` across the last 3 consecutive runs.

Tiered targets (per ADR 0063 four-phase model from S-0127):

- `duration_structural_ms` — 500ms (1.5× threshold: 750ms)
- `duration_health_probe_ms` — 5000ms (1.5× threshold: 7500ms)
- `duration_graph_audit_ms` — 5000ms (1.5× threshold: 7500ms)
- `duration_total_ms` — 11000ms (1.5× threshold: 16500ms)

The current run's tentative timings participate in the rolling window: the soft-warn fires on the *third* sustained-breach run, not the run after it.

## Readiness criteria

- **T1-A** — validator naturally surfaces the soft-warn (sustained 1.5× breach across 3 consecutive runs against a real codebase, not a synthetic test fixture).
- **T1-B** — the surfaced phase is investigated and either (a) the regression is real and addressed at the hot path, or (b) the phase boundary is judged wrong and corrected with evidence (e.g., a slow concern is misclassified into the wrong phase), or (c) the threshold is judged too aggressive and adjusted with evidence (e.g., new infrastructure raised steady-state; live-DB load increased after a graph expansion).
- **T1-C** — if the threshold is adjusted, the adjustment is committed with the evidence in the commit message and reflected in `VALIDATOR_PHASE_TARGETS_MS` and `_REGRESSION_BREACH_MULTIPLIER` / `_REGRESSION_RUN_WINDOW` as appropriate; the ADR 0063 Consequences section is folded (per ADR 0036) to record the threshold change rather than amended inline.

## Status

- **T1-A — closed at S-0126.** First natural fire on S-0126's own validator runs: `duration_structural_ms` median ~3705ms exceeded the 750ms threshold across 3 consecutive runs.
- **T1-B — closed at S-0127 via Path B (phase boundary correction).** Investigation showed `validate_shared_state_health()` — invoked inside the structural phase but spawning subprocess probes including a chromadb `PersistentClient` open — was the dominant contributor (~3500ms of the ~3700ms structural total). After moving that, the structural phase still showed ~1200ms because `validate_issue_collisions()` shells out to `gh issue list` (~700ms; network-bound and variable). Both subprocess probes were moved into the new `health_probe` phase in the same fold — the abstraction is "subprocess to live external system," which is categorically different from "in-memory file/regex check." The right resolution was not to bump the structural target (would mask future regressions in the genuinely fast in-memory checks) and not to chase chromadb or gh individually (their costs are intrinsic). Post-fix verification on the live repo: structural ~415ms; health_probe ~3550ms; graph_audit ~1300ms; total ~5260ms — all clean. Closes [Issue #90](https://github.com/StarshipSuperjam/paideia/issues/90).
- **T1-C — N/A for this fire.** No threshold adjustment was needed; the fix was structural (phase boundary correction). T1-C remains the documented procedure for any *future* fire whose resolution genuinely requires a threshold bump.

## Cross-references

- [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — the contract (four-phase model from S-0127 fold).
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category entry under `### \`validator_runtime_phase_regression\``.
- [`engine/operations/health-check.md`](../operations/health-check.md) — Validator-telemetry section names the tiered targets.
- [Issue #88](https://github.com/StarshipSuperjam/paideia/issues/88) — original source.
- [Issue #90](https://github.com/StarshipSuperjam/paideia/issues/90) — T1-B closure source.
