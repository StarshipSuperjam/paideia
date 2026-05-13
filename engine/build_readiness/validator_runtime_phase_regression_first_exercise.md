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
- **T1-C — N/A for the S-0126/S-0127 fire.** No threshold adjustment was needed; the fix was structural (phase boundary correction).

### S-0146 second fire — closed at S-0151 via Path A (hot-check optimization)

The regression soft-warn fired again at S-0146 close: `duration_structural_ms` median 871ms vs 500ms target — pre-existing in the local validate-history (599–895ms range) and confirmed across multiple sessions per [Issue #116](https://github.com/StarshipSuperjam/paideia/issues/116). Investigation at S-0151 Phase A1 profiled the 7 top-level structural-phase functions individually (n=5 runs each, ad-hoc harness at `/tmp/profile_structural_S0151.py`) and attributed the regression to a single hot check:

| Function | Pre-S-0151 median | % of structural |
|---|---|---|
| `validate_adr_back_reference_orphan` | **376ms** | **63%** |
| `validate_timestamp_helper_bypass` | 136ms | 23% |
| `validate_repo_structure` (other) | 18ms | 3% |
| `validate_adr_consequences_amendment_headers` | 11ms | 2% |
| Everything else | <1ms each | <1% |
| **Total (sum of medians)** | **593ms** | 100% |

The root cause was algorithmic, not corpus-growth. `validate_adr_back_reference_orphan` ran two regex searches per (ADR × non-ADR md-file) pair — at S-0146 corpus size (85 ADRs × ~300 non-ADR md files) that produced ~50,000 regex searches per call. The Phase A1 deliberation proposed Path A (tune the hot check) over Path C (target bump) because the cost concentrated in a single function, not corpus-wide; Path B (phase boundary correction) was unlikely because all 7 structural-phase functions are in-memory file/regex with no subprocess components.

Phase B (S-0151 doubt-driven evaluation per [ADR 0084](../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md)) ran the CLAIM → EXTRACT → DOUBT → RECONCILE workflow on the Phase A1 proposal as the in-session "upcoming decision" test case (see [`engine/docs/audits/doubt_driven_evaluation.md`](../docs/audits/doubt_driven_evaluation.md) workflow application 4). The doubt pass surfaced one refinement (cache-key Path normalization) but did not invalidate the path leaning.

**Path A landing (S-0151):** `validate_adr_back_reference_orphan` rewritten to use an inverted-index pre-scan — one `re.finditer(r"ADR\s+(\d{4})\b|\b(\d{4})-[\w-]+\.md")` pass per non-ADR md file extracts the union of cited ADR IDs into a set; the per-ADR check then becomes O(1) set membership. The semantically-equivalent transformation was verified via `/tmp/probe_inverted_index_S0151.py` (zero diff in soft-warn output between the pre-S-0151 pairwise-regex and the post-S-0151 inverted-index implementations on the live repo).

Post-fix verification:

| Function | Post-S-0151 median | Speedup |
|---|---|---|
| `validate_adr_back_reference_orphan` | **195ms** | **1.93×** |
| Structural phase total (sum of medians) | **491ms** | **1.21×** |

Three back-to-back default-mode `validate.py` runs at S-0151 close-time: structural 554ms / 409ms / 423ms — all under the 750ms 1.5× threshold. `validator_runtime_phase_regression` does NOT fire on the rolling-3 window post-fix. 6/6 `TestAdrBackReferenceOrphan` tests green.

- **T1-A second fire — closed at S-0146.** First sustained observation of the soft-warn at the 871ms median.
- **T1-B second close — closed at S-0151 via Path A (hot-check optimization).** Inverted-index optimization in `validate_adr_back_reference_orphan` at [`engine/tools/validate.py:1326-1390`](../tools/validate.py:1326). The first fire (S-0126 → S-0127) was Path B; this fire is Path A. Both paths are documented procedure per the original ADR 0063 Decision section.
- **T1-C — N/A for this fire too.** No threshold adjustment was needed; the corpus growth (38→85 ADRs since S-0126) did not require bumping the target because the algorithmic fix accommodates corpus growth at the same target.

## Cross-references

- [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — the contract (four-phase model from S-0127 fold).
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category entry under `### \`validator_runtime_phase_regression\``.
- [`engine/operations/health-check.md`](../operations/health-check.md) — Validator-telemetry section names the tiered targets.
- [Issue #88](https://github.com/StarshipSuperjam/paideia/issues/88) — original source.
- [Issue #90](https://github.com/StarshipSuperjam/paideia/issues/90) — T1-B closure source (first fire).
- [Issue #116](https://github.com/StarshipSuperjam/paideia/issues/116) — T1-B closure source (second fire).
- [ADR 0084](../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — S-0151's Phase B doubt-driven pass on Phase A1's path proposal.
- [`engine/docs/audits/doubt_driven_evaluation.md`](../docs/audits/doubt_driven_evaluation.md) — workflow application 4 records the doubt pass on this fix.
